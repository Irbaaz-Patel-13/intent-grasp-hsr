#!/usr/bin/env python
"""
capture_head_for_ik.py -- CONTAINER (step 1 of 3).
Capture a synced head RGB-D frame + the camera pose in odom, save to npz.
No perception here; that runs on Windows (step 2).

Run in the Jupyter / container terminal:
  cd /workspace/notebooks
  python capture_head_for_ik.py
Then copy to Windows:
  (WSL2) cp ~/tmc_wrs_docker/notebooks/cgn_data/head_capture.npz <repo>/workspace/
"""
import time
import numpy as np
import rospy, tf2_ros, message_filters
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from tf.transformations import quaternion_matrix
from utils import move_arm_init, move_hand

RGB   = "/hsrb/head_rgbd_sensor/rgb/image_raw"
DEPTH = "/hsrb/head_rgbd_sensor/depth_registered/image"
INFO  = "/hsrb/head_rgbd_sensor/rgb/camera_info"
CAM_FRAME = "head_rgbd_sensor_rgb_frame"
WORLD = "odom"
OUT = "/workspace/notebooks/cgn_data/head_capture.npz"


def main():
    rospy.init_node("capture_head_for_ik", anonymous=True)
    bridge = CvBridge()
    buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf); rospy.sleep(1.0)
    move_arm_init(); move_hand(1); time.sleep(1.0)   # arm clear of the head view

    info = rospy.wait_for_message(INFO, CameraInfo, timeout=10)
    K = np.array(info.K, dtype=np.float64).reshape(3, 3)

    box = {}; got = {"n": 0}
    rs = message_filters.Subscriber(RGB, Image)
    ds = message_filters.Subscriber(DEPTH, Image)
    sync = message_filters.ApproximateTimeSynchronizer([rs, ds], queue_size=10, slop=0.05)
    def cb(r, d):
        got["n"] += 1
        if got["n"] > 10:                              # flush stale pairs
            box["rgb"] = bridge.imgmsg_to_cv2(r, "rgb8")
            box["depth"] = bridge.imgmsg_to_cv2(d, "32FC1")
    sync.registerCallback(cb)
    t = rospy.Time.now()
    while "rgb" not in box and (rospy.Time.now() - t).to_sec() < 10:
        rospy.sleep(0.1)
    rs.sub.unregister(); ds.sub.unregister()
    if "rgb" not in box:
        print("ERROR: no synced RGB-D pair received"); return

    tr = buf.lookup_transform(WORLD, CAM_FRAME, rospy.Time(0), rospy.Duration(5)).transform
    T = quaternion_matrix([tr.rotation.x, tr.rotation.y, tr.rotation.z, tr.rotation.w])
    T[0,3], T[1,3], T[2,3] = tr.translation.x, tr.translation.y, tr.translation.z

    rgb = np.ascontiguousarray(box["rgb"], np.uint8)
    depth = np.asarray(box["depth"], np.float32)
    np.savez(OUT, rgb=rgb, depth=depth, camera_intrinsics=K, T_odom_cam=T)
    cp = T[:3, 3]
    print(f"saved {OUT}")
    print(f"  rgb{rgb.shape} depth{depth.shape}  head_cam@odom=({cp[0]:.3f},{cp[1]:.3f},{cp[2]:.3f})")
    print("  next: cp this to Windows and run ground_regions_3d.py")


if __name__ == "__main__":
    main()
