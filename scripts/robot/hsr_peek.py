#!/usr/bin/env python3
r"""hsr_peek.py -- raise the arm for a wider hand-camera view, then return to the
EXACT pose it started from.

    python3 hsr_peek.py                 # +0.08 m, capture, return
    python3 hsr_peek.py --dz 0.12       # higher
    python3 hsr_peek.py --stay          # stay raised (does NOT restore)

Why the return matters: GRASP_PX (290.4, 274.8) in hsr_final_center.py is an
EMPIRICAL constant measured at the hover arm configuration -- it encodes the
camera-to-finger offset as seen from that exact pose. Raise the camera and the
same physical offset projects to a different pixel, so servoing from a raised
view would drive the base to the wrong place. Use the raised view to SEE the
scene; servo only after returning.

Odom is untouched by design: only arm joints are commanded, and the base is
never moved. The script records odom before and after and reports any drift, so
place_run.ref and the servo's reference stay valid.
"""
import argparse, sys, time

ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint",
       "wrist_flex_joint", "wrist_roll_joint"]
LIFT_MAX = 0.69
CAM_TOPICS = ["/hsrb/hand_camera/image_raw",
              "/hsrb/hand_camera/image_rect_color",
              "/hsrb/hand_camera/image_raw/compressed"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dz", type=float, default=0.08, help="extra lift (m)")
    ap.add_argument("--lift_cap", type=float, default=0.64,
                    help="absolute arm_lift ceiling; 0.685 with a tilted head put "
                         "the hand into the head camera on 28 Jul")
    ap.add_argument("--out", default="peek_view.png")
    ap.add_argument("--dwell", type=float, default=1.5)
    ap.add_argument("--stay", action="store_true",
                    help="do NOT return to the starting pose")
    a = ap.parse_args()

    import rospy, numpy as np
    from sensor_msgs.msg import JointState, Image
    from nav_msgs.msg import Odometry
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

    rospy.init_node("hsr_peek", anonymous=True)
    st = {"js": {}, "odom": None, "img": None}
    rospy.Subscriber("/hsrb/joint_states", JointState,
                     lambda m: st.update(js=dict(zip(m.name, m.position))))
    rospy.Subscriber("/hsrb/odom", Odometry, lambda m: st.update(odom=m))
    pub = rospy.Publisher("/hsrb/arm_trajectory_controller/command",
                          JointTrajectory, queue_size=1)
    t0 = time.time()
    while (not st["js"] or st["odom"] is None or pub.get_num_connections() == 0) \
            and time.time() - t0 < 6:
        time.sleep(0.1)
    if not st["js"]:
        sys.exit("ABORT: no /hsrb/joint_states")

    def odom_xy():
        o = st["odom"]
        if o is None:
            return None
        p = o.pose.pose.position
        q = o.pose.pose.orientation
        yaw = np.arctan2(2.0*(q.w*q.z + q.x*q.y), 1.0 - 2.0*(q.y*q.y + q.z*q.z))
        return (p.x, p.y, float(np.degrees(yaw)))

    start = {k: float(st["js"].get(k, 0.0)) for k in ARM}
    odom0 = odom_xy()
    print("start arm : %s" % {k: round(v, 3) for k, v in start.items()})
    print("start odom: (%.3f, %.3f, %.1f deg)" % odom0)

    # HEAD TO NEUTRAL before raising. On 28 Jul the hand struck the head camera:
    # the head was tilted -0.70 (housing forward and low) while the arm was driven
    # to arm_lift 0.685. Neutralise first, restore at the end.
    from trajectory_msgs.msg import JointTrajectory as _JT, JointTrajectoryPoint as _JP
    ph = rospy.Publisher("/hsrb/head_trajectory_controller/command", _JT, queue_size=1)
    time.sleep(0.6)
    head0 = (float(st["js"].get("head_pan_joint", 0.0)),
             float(st["js"].get("head_tilt_joint", 0.0)))
    moved_head = abs(head0[0]) > 0.05 or abs(head0[1]) > 0.05
    if moved_head:
        hj = _JT(); hj.joint_names = ["head_pan_joint", "head_tilt_joint"]
        hp = _JP(); hp.positions = [0.0, 0.0]; hp.time_from_start = rospy.Duration(2.0)
        hj.points = [hp]; hj.header.stamp = rospy.Time(0)
        ph.publish(hj); time.sleep(2.5)
        print("head (%.2f, %.2f) -> neutral" % head0)

    target = min(start["arm_lift_joint"] + a.dz, LIFT_MAX - 0.005, a.lift_cap)
    dz = target - start["arm_lift_joint"]
    if dz < 0.005:
        print("no headroom to raise (arm_lift %.3f, limit %.3f) -- capturing here"
              % (start["arm_lift_joint"], LIFT_MAX))
    else:
        print("raising arm_lift %.3f -> %.3f  (+%.3f m)"
              % (start["arm_lift_joint"], target, dz))
        up = dict(start); up["arm_lift_joint"] = target
        jt = JointTrajectory(); jt.joint_names = ARM
        p = JointTrajectoryPoint(); p.positions = [up[k] for k in ARM]
        p.velocities = [0.0]*len(ARM); p.time_from_start = rospy.Duration(3.0)
        jt.points = [p]; jt.header.stamp = rospy.Time(0)
        pub.publish(jt); time.sleep(3.5)
        reached = float(st["js"].get("arm_lift_joint", 0.0))
        print("reached arm_lift %.3f %s" % (reached,
              "" if abs(reached - target) < 0.01 else "  <-- did NOT reach target"))
    time.sleep(a.dwell)

    # ---- capture whatever the hand camera sees ----
    got = None
    for topic in CAM_TOPICS:
        try:
            msg = rospy.wait_for_message(topic, Image, timeout=3.0)
            got = (topic, msg); break
        except Exception:
            continue
    if got is None:
        print("no hand-camera image on %s -- view not saved" % CAM_TOPICS)
    else:
        topic, msg = got
        try:
            import cv2
            from cv_bridge import CvBridge
            img = CvBridge().imgmsg_to_cv2(msg, desired_encoding="bgr8")
            cv2.imwrite(a.out, img)
            print("saved %s from %s  (%dx%d)" % (a.out, topic, img.shape[1], img.shape[0]))
        except Exception as e:
            print("could not decode image from %s: %s" % (topic, e))

    if a.stay:
        print("\n--stay given: arm left raised. GRASP_PX is NOT valid at this "
              "height -- do not run hsr_final_center.py until you return.")
    else:
        jt = JointTrajectory(); jt.joint_names = ARM
        p = JointTrajectoryPoint(); p.positions = [start[k] for k in ARM]
        p.velocities = [0.0]*len(ARM); p.time_from_start = rospy.Duration(3.0)
        jt.points = [p]; jt.header.stamp = rospy.Time(0)
        pub.publish(jt); time.sleep(3.5)
        back = {k: float(st["js"].get(k, 0.0)) for k in ARM}
        err = max(abs(back[k] - start[k]) for k in ARM)
        print("\nreturned arm: %s" % {k: round(v, 3) for k, v in back.items()})
        print("max joint error vs start: %.4f rad %s"
              % (err, "OK" if err < 0.01 else "<-- NOT restored, re-run --stage arm"))

    if moved_head:
        hj = _JT(); hj.joint_names = ["head_pan_joint", "head_tilt_joint"]
        hp = _JP(); hp.positions = [head0[0], head0[1]]
        hp.time_from_start = rospy.Duration(2.0)
        hj.points = [hp]; hj.header.stamp = rospy.Time(0)
        ph.publish(hj); time.sleep(2.5)
        print("head restored to (%.2f, %.2f)" % head0)

    odom1 = odom_xy()
    d = max(abs(odom1[0]-odom0[0]), abs(odom1[1]-odom0[1]))
    print("end odom  : (%.3f, %.3f, %.1f deg)   drift %.4f m, %.2f deg  %s"
          % (odom1[0], odom1[1], odom1[2], d, abs(odom1[2]-odom0[2]),
             "-- reference intact" if d < 0.005 else "-- BASE MOVED, reference suspect"))


if __name__ == "__main__":
    main()
