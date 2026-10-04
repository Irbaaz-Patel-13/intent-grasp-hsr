#!/usr/bin/env python
"""
capture_frame.py  --  run INSIDE the simulator container (ROS Noetic sourced).

Grabs one registered RGB-D frame + intrinsics from the HSR head camera, looks up
the odom->camera transform from TF, converts it to the OpenGL world->camera
'camera_extrinsics' your AffordGrasp pipeline expects, and saves everything to a
single .npz in the shared cgn_data folder (visible from Windows).

The Windows pipeline then loads this .npz, builds a CapturedImage, and runs
perception+grasp-generation byte-identically to the PyBullet path -- only the
frame source changed.

Usage (inside container, after `source /opt/ros/noetic/setup.bash`):
    python capture_frame.py
    python capture_frame.py --out /workspace/notebooks/cgn_data/frame_live.npz
"""
import argparse
import numpy as np
import rospy
import tf2_ros
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from tf.transformations import quaternion_matrix

RGB_TOPIC   = "/hsrb/head_rgbd_sensor/rgb/image_raw"
DEPTH_TOPIC = "/hsrb/head_rgbd_sensor/depth_registered/image"   # float32 metres, aligned to RGB
INFO_TOPIC  = "/hsrb/head_rgbd_sensor/rgb/camera_info"
WORLD_FRAME = "odom"
CAM_FRAME   = "head_rgbd_sensor_rgb_frame"

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])   # OpenCV optical frame -> OpenGL frame


def grab(topic, msg_type, timeout=10.0):
    return rospy.wait_for_message(topic, msg_type, timeout=timeout)


def lookup_T_odom_cam(timeout=10.0):
    """4x4 homogeneous transform odom -> camera (camera pose in world, OpenCV axes)."""
    buf = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(buf)
    deadline = rospy.Time.now() + rospy.Duration(timeout)
    rate = rospy.Rate(10)
    last_err = None
    while rospy.Time.now() < deadline and not rospy.is_shutdown():
        try:
            tr = buf.lookup_transform(WORLD_FRAME, CAM_FRAME, rospy.Time(0))
            t = tr.transform.translation
            q = tr.transform.rotation
            T = quaternion_matrix([q.x, q.y, q.z, q.w])   # 4x4, rotation only
            T[0, 3], T[1, 3], T[2, 3] = t.x, t.y, t.z
            return T
        except (tf2_ros.LookupException, tf2_ros.ExtrapolationException,
                tf2_ros.ConnectivityException) as e:
            last_err = e
            rate.sleep()
    raise RuntimeError("TF %s->%s unavailable: %s" % (WORLD_FRAME, CAM_FRAME, last_err))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/workspace/notebooks/cgn_data/frame_live.npz")
    args = ap.parse_args()

    rospy.init_node("capture_frame", anonymous=True)
    bridge = CvBridge()

    print("Waiting for camera_info ...")
    info = grab(INFO_TOPIC, CameraInfo)
    K = np.array(info.K, dtype=np.float64).reshape(3, 3)

    print("Waiting for RGB ...")
    rgb_msg = grab(RGB_TOPIC, Image)
    rgb = bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="rgb8")   # force RGB order
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

    print("Waiting for registered depth ...")
    depth_msg = grab(DEPTH_TOPIC, Image)
    depth = bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")
    depth = np.asarray(depth, dtype=np.float32)                   # metres

    # ---- integrity checks: catch the silent corruptions before they reach CGN ----
    assert rgb.ndim == 3 and rgb.shape[2] == 3, "RGB not HxWx3: %s" % (rgb.shape,)
    assert depth.shape == rgb.shape[:2], \
        "depth/RGB shape mismatch: %s vs %s (depth not registered to RGB?)" % (depth.shape, rgb.shape[:2])
    finite = depth[np.isfinite(depth)]
    med = float(np.median(finite)) if finite.size else float("nan")
    assert 0.05 < med < 10.0, \
        "median depth %.3f looks wrong for metres (mm topic by mistake?)" % med

    print("Looking up TF %s -> %s ..." % (WORLD_FRAME, CAM_FRAME))
    T_odom_cam = lookup_T_odom_cam()
    camera_extrinsics = FLIP @ np.linalg.inv(T_odom_cam)          # OpenGL world->camera

    np.savez(
        args.out,
        rgb=rgb,                              # (H,W,3) uint8, RGB
        depth=depth,                          # (H,W)  float32, metres
        camera_intrinsics=K,                  # (3,3)  float64
        camera_extrinsics=camera_extrinsics,  # (4,4)  float64, OpenGL world->cam
        T_odom_cam=T_odom_cam,                # (4,4)  raw TF, kept for debugging
    )
    print("\nSaved:", args.out)
    print("  rgb   :", rgb.shape, rgb.dtype)
    print("  depth :", depth.shape, depth.dtype, "median=%.3f m" % med)
    print("  K     :\n", K)
    print("  cam pose in odom (x,y,z): %.3f %.3f %.3f"
          % (T_odom_cam[0, 3], T_odom_cam[1, 3], T_odom_cam[2, 3]))


if __name__ == "__main__":
    main()
