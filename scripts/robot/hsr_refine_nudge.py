#!/usr/bin/env python3
"""Close-range target refinement at the standoff (coarse-to-fine active perception).

Measures the mug's actual centroid from a fresh head-depth capture, compares it
to where the plan expects it in the CURRENT base frame, and nudges the base by
the delta. Persists the correction by shifting the ref_file, so the executor's
ref (+) B* lands the base where the relative grasp geometry is true again.

Run AFTER stage base (robot at standoff), BEFORE the arm descends.
"""
import sys, math, argparse
import numpy as np
import rospy, tf2_ros
from sensor_msgs.msg import Image, CameraInfo
from control_msgs.msg import JointTrajectoryControllerState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from hsr_base_drive import BaseDriver

DEPTH_TOPICS = ["/hsrb/head_rgbd_sensor/depth_registered/image_rect_raw",
                "/hsrb/head_rgbd_sensor/depth_registered/image_raw"]
INFO_TOPIC   = "/hsrb/head_rgbd_sensor/rgb/camera_info"
CAM_FRAME    = "head_rgbd_sensor_rgb_frame"

def wrap(a): return math.atan2(math.sin(a), math.cos(a))
def R2(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]])

def quat_to_R(x, y, z, w):
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

def grab_depth(timeout=6.0):
    for topic in DEPTH_TOPICS:
        try:
            msg = rospy.wait_for_message(topic, Image, timeout=timeout)
            d = np.frombuffer(msg.data, dtype=np.uint16).reshape(msg.height, msg.width).astype(np.float64)
            if "16" in msg.encoding.upper(): d = d / 1000.0     # mm -> m
            print("[refine] depth from %s  enc=%s  med=%.3f" % (topic, msg.encoding, np.median(d[d>0])))
            return d
        except rospy.ROSException:
            continue
    raise RuntimeError("no depth image on any known topic")

def tilt_head(tilt):
    pub = rospy.Publisher("/hsrb/head_trajectory_controller/command", JointTrajectory, queue_size=1)
    rospy.sleep(1.0)
    jt = JointTrajectory(); jt.joint_names = ["head_pan_joint", "head_tilt_joint"]
    p = JointTrajectoryPoint(); p.positions = [0.0, tilt]; p.velocities = [0.0, 0.0]
    p.time_from_start = rospy.Duration(2.0)
    jt.points = [p]; jt.header.stamp = rospy.Time(0)
    pub.publish(jt); rospy.sleep(3.0)
    print("[refine] head tilted to %.2f" % tilt)

def measure_centroid(exp_base, K, tfbuf, r=0.12, zlo=-0.10, zhi=0.14):
    d = grab_depth()
    tr = tfbuf.lookup_transform("base_link", CAM_FRAME, rospy.Time(0), rospy.Duration(3.0))
    t = tr.transform.translation; q = tr.transform.rotation
    R = quat_to_R(q.x, q.y, q.z, q.w); T = np.array([t.x, t.y, t.z])
    fx, fy, cx, cy = K[0,0], K[1,1], K[0,2], K[1,2]
    v, u = np.where((d > 0.2) & (d < 1.5))          # near field only
    z = d[v, u]
    pc = np.stack([(u-cx)*z/fx, (v-cy)*z/fy, z], axis=1)
    pb = pc @ R.T + T                                # -> base_link
    m0 = (np.linalg.norm(pb[:, :2] - exp_base[:2], axis=1) < r) \
        & (pb[:, 2] > exp_base[2]+zlo) & (pb[:, 2] < exp_base[2]+zhi)
    n0 = int(m0.sum())
    if n0 < 300: return None, n0
    # support-plane aware: table = low percentile of cylinder; mug = points above it
    z_table = float(np.percentile(pb[m0, 2], 15))
    m = m0 & (pb[:, 2] > z_table + 0.02) & (pb[:, 2] < z_table + 0.18)
    n = int(m.sum())
    print("[refine] support plane z=%.3f  pts above plane=%d (of %d in cylinder)" % (z_table, n, n0))
    if n < 200: return None, n
    return pb[m].mean(axis=0), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grasps", default="grasps_plain.npz")
    ap.add_argument("--ref_file", default="place_run.ref")
    ap.add_argument("--max_nudge", type=float, default=0.08)
    ap.add_argument("--min_nudge", type=float, default=0.008)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    rospy.init_node("hsr_refine_nudge", anonymous=True)
    tfbuf = tf2_ros.Buffer(); tf2_ros.TransformListener(tfbuf)

    aff = np.load(a.grasps, allow_pickle=True)["aff_center_3d"].astype(float)   # ref base frame
    rx, ry, rt = (float(x) for x in open(a.ref_file).read().split(","))
    print("[refine] aff(ref frame)=%s  ref=(%.3f,%.3f,%.1fdeg)" % (np.round(aff,3), rx, ry, math.degrees(rt)))

    bd = BaseDriver()
    cx_, cy_, ct_ = bd.pose()
    # aff -> odom -> current base frame
    aff_odom = np.array([rx, ry]) + R2(rt) @ aff[:2]
    exp = np.zeros(3)
    exp[:2] = R2(-ct_) @ (aff_odom - np.array([cx_, cy_])); exp[2] = aff[2]
    print("[refine] expected mug (current base frame): %s" % np.round(exp, 3))

    Kmsg = rospy.wait_for_message(INFO_TOPIC, CameraInfo, timeout=5.0)
    K = np.array(Kmsg.K).reshape(3, 3)

    cen, n = measure_centroid(exp, K, tfbuf)
    if cen is None:
        print("[refine] only %d pts near expected mug — tilting head down and retrying" % n)
        tilt_head(-0.9)
        cen, n = measure_centroid(exp, K, tfbuf)
        if cen is None:
            sys.exit("ABORT: mug not found near expected position (%d pts). If it rolled away, "
                     "reset it and rerun; if still failing, full recapture needed." % n)
    print("[refine] measured mug centroid: %s  (%d pts)" % (np.round(cen, 3), n))

    delta = cen[:2] - exp[:2]
    mag = float(np.linalg.norm(delta))
    print("[refine] delta (base frame): dx=%.4f dy=%.4f  |d|=%.4f m" % (delta[0], delta[1], mag))
    if mag < a.min_nudge:
        print("[refine] within tolerance — no nudge needed. Proceed to grasp."); return
    if mag > a.max_nudge:
        sys.exit("ABORT: delta %.3f m exceeds max %.3f — scene changed too much, recapture instead." % (mag, a.max_nudge))

    d_odom = R2(ct_) @ delta
    tgt = (cx_ + d_odom[0], cy_ + d_odom[1], ct_)
    print("[refine] nudging base by odom delta (%.4f, %.4f)" % (d_odom[0], d_odom[1]))
    if a.dry: print("[dry] not moving, not rewriting ref."); return

    ok, info = bd.move_to(*tgt)
    print("[refine] nudge settled: %s %s" % (ok, info))
    if not ok: sys.exit("ABORT: nudge did not settle")

    import shutil, os
    if not os.path.exists(a.ref_file + ".orig"):
        shutil.copy(a.ref_file, a.ref_file + ".orig")   # capture-time base pose = cloud frame
    open(a.ref_file, "w").write("%f,%f,%f" % (rx + d_odom[0], ry + d_odom[1], rt))
    open("refine_delta.txt", "w").write("%f,%f" % (d_odom[0], d_odom[1]))   # cloud-bias correction for grounding
    print("[refine] ref_file shifted -> executor target now matches reality. Run --stage grasp.")

if __name__ == "__main__":
    main()
