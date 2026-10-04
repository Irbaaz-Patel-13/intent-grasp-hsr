#!/usr/bin/env python3
r"""hsr_place_down.py -- set a held object down and release, without tripping
the gripper over-current fault.

    python3 hsr_place_down.py              # ease grip, lower 0.15 m over 6 s, open
    python3 hsr_place_down.py --dz 0.12 --time 8

Why this exists: the same fault that stopped the LIFT (fixed 27 Jul by ramping
over 6 s and easing 0.005 rad after contact) also occurs on the way DOWN. A
0.15 m descent in 4 s with the object held means the arm decelerates, the
object's inertia back-drives the compliant fingers, position-hold fights the
error and current climbs. On this robot the resulting fault can only be cleared
by an e-stop and restart -- which also resets odom -- so it is worth avoiding.

Three mitigations, mirroring the lift fix:
  1. ease the grip ~0.008 rad BEFORE moving (still holding; less spring load)
  2. descend through 4 waypoints over --time seconds instead of one command
  3. open fully only once the object is down and the arm has settled
"""
import argparse, sys, time

ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint",
       "wrist_flex_joint", "wrist_roll_joint"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dz", type=float, default=0.15, help="descent (m)")
    ap.add_argument("--time", type=float, default=6.0, help="descent duration (s)")
    ap.add_argument("--ease", type=float, default=0.008,
                    help="rad to open BEFORE descending (0 disables)")
    ap.add_argument("--open_to", type=float, default=1.0)
    a = ap.parse_args()

    import rospy
    from sensor_msgs.msg import JointState
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

    rospy.init_node("place_down", anonymous=True)
    st = {}
    rospy.Subscriber("/hsrb/joint_states", JointState,
                     lambda m: st.update(dict(zip(m.name, m.position))))
    pa = rospy.Publisher("/hsrb/arm_trajectory_controller/command",
                         JointTrajectory, queue_size=1)
    pg = rospy.Publisher("/hsrb/gripper_controller/command",
                         JointTrajectory, queue_size=1)
    t0 = time.time()
    while ("arm_lift_joint" not in st or pa.get_num_connections() == 0
           or pg.get_num_connections() == 0) and time.time() - t0 < 6:
        time.sleep(0.1)
    if "arm_lift_joint" not in st:
        sys.exit("ABORT: no /hsrb/joint_states")

    q = {k: float(st[k]) for k in ARM}
    grip0 = float(st.get("hand_motor_joint", 0.0))
    print("start: arm_lift %.3f  hand_motor %.3f" % (q["arm_lift_joint"], grip0))

    def send_grip(pos, dur):
        jt = JointTrajectory(); jt.joint_names = ["hand_motor_joint"]
        p = JointTrajectoryPoint(); p.positions = [float(pos)]
        p.time_from_start = rospy.Duration(dur)
        jt.points = [p]; jt.header.stamp = rospy.Time(0)
        pg.publish(jt); time.sleep(dur + 0.4)

    # 1. ease the grip while still holding -- reduces spring load before motion
    if a.ease > 0:
        send_grip(grip0 + a.ease, 1.0)
        print("eased grip %.3f -> %.3f (still holding)"
              % (grip0, float(st.get("hand_motor_joint", grip0))))

    # 2. staged descent
    target = max(0.0, q["arm_lift_joint"] - a.dz)
    n = 4
    jt = JointTrajectory(); jt.joint_names = ARM
    for i in range(1, n + 1):
        p = JointTrajectoryPoint()
        pos = dict(q)
        pos["arm_lift_joint"] = q["arm_lift_joint"] + (target - q["arm_lift_joint"]) * i / float(n)
        p.positions = [pos[k] for k in ARM]; p.velocities = [0.0] * len(ARM)
        p.time_from_start = rospy.Duration(a.time * i / float(n))
        jt.points.append(p)
    jt.header.stamp = rospy.Time(0)
    pa.publish(jt); time.sleep(a.time + 1.0)
    reached = float(st.get("arm_lift_joint", 0.0))
    print("lowered %.3f -> %.3f (commanded %.3f) over %.1f s"
          % (q["arm_lift_joint"], reached, target, a.time))
    if abs(reached - target) > 0.02:
        print("  WARNING: descent incomplete -- check for a joint fault before opening")

    # 3. release once settled
    time.sleep(0.8)
    send_grip(a.open_to, 2.0)
    print("gripper open (%.3f)" % float(st.get("hand_motor_joint", 0.0)))
    print("\nobject released. If the red over-current appeared anyway, try:")
    print("   python3 hsr_place_down.py --time 10 --ease 0.015")


if __name__ == "__main__":
    main()
