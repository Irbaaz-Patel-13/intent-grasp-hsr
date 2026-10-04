#!/usr/bin/env python3
r"""capture_object.py -- full multi-view capture of one object, with a JSON log.

    python3 capture_object.py --label mug
    python3 capture_object.py --label pot --dx 0.30
    python3 capture_object.py --label spoon --no-hand      # head views only

Sequence per object:
  1. head_far   arm ducked, tilt -0.50, standard distance   (RGB-D)
  2. drive --dx closer
  3. head_near  arm ducked, tilt -0.70                      (RGB-D)
  4. hand_high  head neutral, arm raised to --hand_lift     (RGB, overhead)
  5. drive back, restow

Why the hand pose is separate from the grasp pose: hsr_peek caps arm_lift at
0.64 because it runs BETWEEN servoing and grasping, where the arm must return
to a hover it will descend from. A capture has no descent to protect, so the
arm can use its full travel (limit 0.69). The real constraint is the head, and
that is handled by moving it to neutral first -- the 28 Jul collision happened
with the head tilted -0.70 and the arm at 0.685.

Everything is recorded to <outdir>/capture_log.json: joint states, odom before
and after, depth statistics, and the files written. That log is the provenance
for the figures in the report.
"""
import argparse, json, os, subprocess, sys, time
from datetime import datetime

ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint",
       "wrist_flex_joint", "wrist_roll_joint"]
# arm extended forward and level, wrist rolled so the camera looks down
HAND_POSE = {"arm_flex_joint": -0.75, "arm_roll_joint": 0.0,
             "wrist_flex_joint": -1.30, "wrist_roll_joint": 0.0}
CAM_TOPICS = ["/hsrb/hand_camera/image_raw", "/hsrb/hand_camera/image_rect_color"]


def sh(cmd, tag=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        if any(k in line for k in ("depth(m)", "saved ->", "settled", "arm stowed",
                                   "head tilt", "ABORT", "ducked", "Error")):
            print("     " + line.strip())
    return r.returncode == 0, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--dx", type=float, default=0.25)
    ap.add_argument("--far_tilt", type=float, default=-0.50)
    ap.add_argument("--near_tilt", type=float, default=-0.70)
    ap.add_argument("--hand_lift", type=float, default=0.685,
                    help="arm_lift for the overhead hand view (limit 0.69)")
    ap.add_argument("--outdir", default="captures_obj")
    ap.add_argument("--no-hand", dest="hand", action="store_false")
    ap.set_defaults(hand=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    py = sys.executable
    log = dict(label=a.label, started=datetime.now().isoformat(timespec="seconds"),
               dx=a.dx, hand_lift=a.hand_lift, steps=[])

    import rospy, numpy as np
    from sensor_msgs.msg import JointState, Image
    from nav_msgs.msg import Odometry
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
    rospy.init_node("capture_object", anonymous=True)
    st = {"js": {}, "odom": None}
    rospy.Subscriber("/hsrb/joint_states", JointState,
                     lambda m: st.update(js=dict(zip(m.name, m.position))))
    rospy.Subscriber("/hsrb/odom", Odometry, lambda m: st.update(odom=m))
    pa = rospy.Publisher("/hsrb/arm_trajectory_controller/command",
                         JointTrajectory, queue_size=1)
    ph = rospy.Publisher("/hsrb/head_trajectory_controller/command",
                         JointTrajectory, queue_size=1)
    t0 = time.time()
    while (not st["js"] or st["odom"] is None or pa.get_num_connections() == 0) \
            and time.time() - t0 < 8:
        time.sleep(0.1)
    if not st["js"]:
        sys.exit("ABORT: no /hsrb/joint_states")

    def odom_now():
        o = st["odom"]
        if o is None: return None
        p, q = o.pose.pose.position, o.pose.pose.orientation
        yaw = np.arctan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
        return [round(p.x, 4), round(p.y, 4), round(float(np.degrees(yaw)), 2)]

    def joints():
        return {k: round(float(st["js"].get(k, 0.0)), 4)
                for k in ARM + ["head_pan_joint", "head_tilt_joint", "hand_motor_joint"]}

    log["odom_start"] = odom_now()
    log["joints_start"] = joints()
    print("odom start: %s" % log["odom_start"])

    def head_view(tag, tilt):
        print("\n== %s (tilt %.2f) ==" % (tag, tilt))
        sh([py, "go_stow.py"])
        if False:  # duck disabled 1 Aug (floor strike)
            sh([py, "hsr_duck.py"])
        sh([py, "head_pose.py", str(tilt)])
        ok, out = sh([py, "capture_real.py"])
        if not ok: sys.exit("capture_real failed at %s" % tag)
        dst = os.path.join(a.outdir, "cap_%s_%s.npz" % (a.label, tag))
        subprocess.run(["cp", "head_capture_real.npz", dst])
        depth = next((l.strip() for l in out.splitlines() if "depth(m)" in l), "")
        print("     -> %s" % dst)
        log["steps"].append(dict(step=tag, tilt=tilt, file=dst, depth=depth,
                                 odom=odom_now(), joints=joints()))

    head_view("head_far", a.far_tilt)
    print("\n== driving %.2f m closer ==" % a.dx)
    ok, _ = sh([py, "hsr_base_drive.py", "--dx", str(a.dx)])
    if not ok: sys.exit("base drive failed")
    log["steps"].append(dict(step="drive_in", dx=a.dx, odom=odom_now()))
    head_view("head_near", a.near_tilt)

    if a.hand:
        print("\n== hand camera, overhead ==")
        # head to neutral FIRST -- with the head tilted its housing sits forward
        # and low, which is how the hand struck it on 28 Jul.
        hj = JointTrajectory(); hj.joint_names = ["head_pan_joint", "head_tilt_joint"]
        hp = JointTrajectoryPoint(); hp.positions = [0.0, 0.0]
        hp.time_from_start = rospy.Duration(2.0)
        hj.points = [hp]; hj.header.stamp = rospy.Time(0)
        ph.publish(hj); time.sleep(2.5); print("     head -> neutral")

        lift = min(a.hand_lift, 0.685)
        cur = {k: float(st["js"].get(k, 0.0)) for k in ARM}
        # raise while still folded, THEN unfold (incident #8: simultaneous
        # interpolation swept the hand through tabletop space)
        stage1 = dict(cur); stage1["arm_lift_joint"] = lift
        stage2 = dict(HAND_POSE); stage2["arm_lift_joint"] = lift
        jt = JointTrajectory(); jt.joint_names = ARM
        for pos, t in ((stage1, 4.0), (stage2, 9.0)):
            p = JointTrajectoryPoint()
            p.positions = [pos[k] for k in ARM]; p.velocities = [0.0]*len(ARM)
            p.time_from_start = rospy.Duration(t); jt.points.append(p)
        jt.header.stamp = rospy.Time(0); pa.publish(jt); time.sleep(10.0)
        print("     arm_lift %.3f, flex %.2f (commanded %.3f)"
              % (st["js"].get("arm_lift_joint", 0), st["js"].get("arm_flex_joint", 0), lift))

        got = None
        for topic in CAM_TOPICS:
            try:
                got = (topic, rospy.wait_for_message(topic, Image, timeout=3.0)); break
            except Exception:
                continue
        if got is None:
            print("     no hand-camera image on %s" % CAM_TOPICS)
            log["steps"].append(dict(step="hand_high", error="no image"))
        else:
            import cv2
            from cv_bridge import CvBridge
            img = CvBridge().imgmsg_to_cv2(got[1], desired_encoding="bgr8")
            png = os.path.join(a.outdir, "cap_%s_hand.png" % a.label)
            cv2.imwrite(png, img)
            np.savez(os.path.join(a.outdir, "cap_%s_hand.npz" % a.label),
                     rgb=img[:, :, ::-1], source=got[0],
                     arm_config=[float(st["js"].get(k, 0.0)) for k in ARM])
            print("     -> %s (%dx%d)" % (png, img.shape[1], img.shape[0]))
            log["steps"].append(dict(step="hand_high", file=png, source=got[0],
                                     odom=odom_now(), joints=joints()))
        sh([py, "go_stow.py"])

    print("\n== returning %.2f m ==" % a.dx)
    sh([py, "hsr_base_drive.py", "--dx", str(-a.dx)])
    sh([py, "go_stow.py"])
    log["odom_end"] = odom_now()
    log["joints_end"] = joints()
    dxy = max(abs(log["odom_end"][i] - log["odom_start"][i]) for i in (0, 1))
    log["odom_drift_m"] = round(dxy, 4)
    print("odom end: %s   drift %.4f m" % (log["odom_end"], dxy))

    lf = os.path.join(a.outdir, "capture_log.json")
    allrec = json.load(open(lf)) if os.path.exists(lf) else []
    allrec.append(log)
    json.dump(allrec, open(lf, "w"), indent=1)
    print("\nDONE %s -- logged to %s (%d objects so far)" % (a.label, lf, len(allrec)))


if __name__ == "__main__":
    main()
