#!/usr/bin/env python3
"""Phase B hand-camera capture — v2 after head-strike incident 2026-07-08.
Order: head to neutral -> deploy arm AT grasp lift -> rise to view lift.
Every trajectory is FK-simulated against a head keep-out sphere before publish."""
import argparse, csv
import numpy as np
import rospy, tf2_ros
from sensor_msgs.msg import Image, CameraInfo, JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from execute_place_grasp_raw import load_chain, fk   # reuse the project's FK
from hsr_base_drive import BaseDriver
import os

ARM = ["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
FRAMES = ["hand_camera_frame", "hand_camera_rgb_frame", "hand_camera_optical_frame"]
HEAD_KEEPOUT_C = np.array([0.05, 0.0, 1.20])   # head sphere, base_link — sized for NEUTRAL head,
HEAD_KEEPOUT_R = 0.22                            # which this script enforces before any arm motion

def traj_safe(J, seq, wp_from, wp_to, samples=15):
    """FK-simulate linear joint interpolation; False if palm enters head keep-out."""
    worst = 1e9
    for s in np.linspace(0.0, 1.0, samples):
        q = {n: (1-s)*a + s*b for n, a, b in zip(ARM, wp_from, wp_to)}
        p = fk(J, seq, q)[:3, 3]
        worst = min(worst, float(np.linalg.norm(p - HEAD_KEEPOUT_C)))
    print("[handview] FK check: min palm-to-head distance %.3f m (limit %.2f)" % (worst, HEAD_KEEPOUT_R))
    return worst > HEAD_KEEPOUT_R

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="place_run.csv"); ap.add_argument("--grasp", type=int, required=True)
    ap.add_argument("--hover", type=float, default=0.12)
    a = ap.parse_args()

    row = None
    for r in csv.DictReader(open(a.csv)):
        if int(r["grasp"]) == a.grasp: row = r; break
    if row is None: raise SystemExit("grasp %d not in %s" % (a.grasp, a.csv))
    q = [float(row["q_lift"]), float(row["q_flex"]), float(row["q_roll"]),
         float(row["q_wflex"]), float(row["q_wroll"])]

    rospy.init_node("hand_view", anonymous=True)
    tfbuf = tf2_ros.Buffer(); tf2_ros.TransformListener(tfbuf)
    st = {"js": {}}
    rospy.Subscriber("/hsrb/joint_states", JointState, lambda m: st.update(js=dict(zip(m.name, m.position))))
    pub_arm = rospy.Publisher("/hsrb/arm_trajectory_controller/command", JointTrajectory, queue_size=1)
    pub_head = rospy.Publisher("/hsrb/head_trajectory_controller/command", JointTrajectory, queue_size=1)
    rospy.sleep(1.5)
    if "arm_lift_joint" not in st["js"]: raise SystemExit("no joint_states")

    # 1. head to NEUTRAL first — out of the arm's swing plane (the crash cause)
    jh = JointTrajectory(); jh.joint_names = ["head_pan_joint", "head_tilt_joint"]
    ph = JointTrajectoryPoint(); ph.positions = [0.0, 0.0]; ph.velocities = [0.0, 0.0]
    ph.time_from_start = rospy.Duration(2.0); jh.points = [ph]; jh.header.stamp = rospy.Time(0)
    pub_head.publish(jh); rospy.sleep(3.0)
    print("[handview] head neutral")

    J, seq = load_chain("hsrb.urdf", "base_link", "hand_palm_link")
    cur = [st["js"].get(n, 0.0) for n in ARM]
    deploy = list(q)                                   # arm config AT grasp lift (palm ~0.63, above mug)
    view = list(q); view[0] = min(0.69, q[0] + a.hover)

    for tag, wf, wt in (("rise-tucked", cur, [q[0]] + cur[1:]),
                        ("deploy", [q[0]] + cur[1:], deploy),
                        ("rise-to-view", deploy, view)):
        if not traj_safe(J, seq, wf, wt):
            raise SystemExit("ABORT: '%s' segment enters head keep-out — not publishing." % tag)

    jt = JointTrajectory(); jt.joint_names = ARM
    for pos, t in (([q[0]] + cur[1:], 3.0), (deploy, 6.5), (view, 8.5)):
        p = JointTrajectoryPoint(); p.positions = pos; p.velocities = [0.0]*5
        p.time_from_start = rospy.Duration(t); jt.points.append(p)
    jt.header.stamp = rospy.Time(0)
    pub_arm.publish(jt); rospy.sleep(9.5)
    print("[handview] at view pose (head-safe sequence, lift %.3f)" % view[0])

    rmsg = rospy.wait_for_message("/hsrb/hand_camera/image_raw", Image, timeout=6.0)
    rgb = np.frombuffer(rmsg.data, dtype=np.uint8).reshape(rmsg.height, rmsg.width, -1)[:, :, :3].copy()
    if "bgr" in rmsg.encoding.lower(): rgb = rgb[:, :, ::-1].copy()
    K = np.array(rospy.wait_for_message("/hsrb/hand_camera/camera_info", CameraInfo, timeout=5.0).K).reshape(3,3)

    tfm = None; frame = None
    for f in FRAMES:
        try:
            tfm = tfbuf.lookup_transform("base_link", f, rospy.Time(0), rospy.Duration(2.0)); frame = f; break
        except Exception: continue
    if tfm is None: raise SystemExit("no hand-camera TF frame found")
    t = tfm.transform.translation; qo = tfm.transform.rotation
    print("[handview] TF base_link->%s  trans=[%.3f %.3f %.3f]" % (frame, t.x, t.y, t.z))
    if t.z > 1.30:  # raised 17 Jul: tall-table envelope (camera z=1.025 was a valid view pose)
        raise SystemExit("ABORT: hand camera at z=%.2f — not a top-down view pose, something is off." % t.z)

    bd = BaseDriver(); bx, by, bt = bd.pose()
    ref_src = a.csv.replace(".csv", ".ref")
    cap_pose = np.array([np.nan]*3)
    for cand in (ref_src + ".orig", ref_src):
        if os.path.exists(cand):
            cap_pose = np.array([float(x) for x in open(cand).read().split(",")]); break
    if not np.any(K): print("[handview] WARNING: hand camera K is ALL ZEROS (uncalibrated camera)")
    np.savez("hand_view_real.npz", rgb=rgb, K=K, frame=frame,
             tf_trans=np.array([t.x,t.y,t.z]), tf_quat=np.array([qo.x,qo.y,qo.z,qo.w]),
             grasp_id=a.grasp, view_q=np.array(view),
             base_pose_view=np.array([bx, by, bt]),      # odom pose when TF was recorded
             base_pose_capture=cap_pose)                  # odom pose of the cloud's frame
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,6)); plt.imshow(rgb); plt.axis("off")
    plt.title("hand camera @ hover")
    plt.tight_layout(); plt.savefig("hand_view_preview.png", dpi=110)
    print("saved -> hand_view_real.npz + hand_view_preview.png")

if __name__ == "__main__":
    main()
