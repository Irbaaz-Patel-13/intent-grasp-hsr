#!/usr/bin/env python
"""capture_real.py -- REAL HSR, capture-only (NO motion commands).
One synced RGB + registered-depth frame, 16UC1 mm -> metres, records the
base_link->camera TF at capture time. Saves head_capture_real.npz. Pure subscriber."""
import numpy as np, rospy, tf2_ros
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import message_filters

OUT   = "head_capture_real.npz"   # writes to current directory
RGB   = "/hsrb/head_rgbd_sensor/rgb/image_raw"
DEPTH = "/hsrb/head_rgbd_sensor/depth_registered/image_raw"
INFO  = "/hsrb/head_rgbd_sensor/rgb/camera_info"
BASE, CAM = "base_link", "head_rgbd_sensor_rgb_frame"

def main():
    rospy.init_node("capture_real", anonymous=True)
    bridge = CvBridge()
    tf_buf = tf2_ros.Buffer(); tf2_ros.TransformListener(tf_buf)

    info = rospy.wait_for_message(INFO, CameraInfo, timeout=10)
    K = np.array(info.K, float).reshape(3, 3)
    print(f"K:\n{np.round(K,2)}")

    box = {}
    def cb(rgb_msg, depth_msg):
        if "done" in box: return
        box["rgb"] = bridge.imgmsg_to_cv2(rgb_msg, "rgb8")
        box["depth_raw"] = bridge.imgmsg_to_cv2(depth_msg, "passthrough")
        box["enc"] = depth_msg.encoding
        box["done"] = True

    rs = message_filters.Subscriber(RGB, Image)
    ds = message_filters.Subscriber(DEPTH, Image)
    message_filters.ApproximateTimeSynchronizer([rs, ds], 5, 0.2).registerCallback(cb)

    print("waiting for synced RGB+depth...")
    t0 = rospy.Time.now()
    while "done" not in box and (rospy.Time.now()-t0).to_sec() < 15:
        rospy.sleep(0.05)
    if "done" not in box:
        raise SystemExit("ABORT: no synced frame in 15s")

    draw = box["depth_raw"]
    print(f"depth enc={box['enc']} dtype={draw.dtype} min={draw.min()} max={draw.max()}")
    depth_m = draw.astype(np.float32) / 1000.0          # 16UC1 mm -> metres
    v = depth_m[(depth_m > 0.05) & (depth_m < 5.0)]
    print(f"depth(m): median={np.median(v):.3f} range=[{v.min():.3f},{v.max():.3f}]")

    tf = tf_buf.lookup_transform(BASE, CAM, rospy.Time(0), rospy.Duration(5.0))
    t, q = tf.transform.translation, tf.transform.rotation
    trans = np.array([t.x, t.y, t.z]); quat = np.array([q.x, q.y, q.z, q.w])
    print(f"TF {BASE}->{CAM}: trans={np.round(trans,3)} quat={np.round(quat,3)}")

    np.savez(OUT, rgb=box["rgb"], depth=depth_m, K=K,
             tf_trans=trans, tf_quat=quat, base_frame=BASE, cam_frame=CAM,
             depth_encoding=box["enc"])
    print(f"saved -> {OUT}  (capture-only; no motion commanded)")

if __name__ == "__main__":
    main()
