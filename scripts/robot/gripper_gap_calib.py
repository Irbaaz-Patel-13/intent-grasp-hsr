#!/usr/bin/env python3
"""hand_motor angle <-> fingertip gap, measured from live TF (no-load curve).
Gripper-only motion; arm must be stowed. Writes gripper_gap_map.csv."""
import rospy, time, csv
import numpy as np, tf2_ros
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState

ANGLES = [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0, -0.2, -0.4]
TIP_L, TIP_R = "hand_l_finger_tip_frame", "hand_r_finger_tip_frame"

rospy.init_node("gripper_gap_calib")
buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf)
pub = rospy.Publisher("/hsrb/gripper_controller/command", JointTrajectory, queue_size=1)
st = {"m": None}
def cb(msg):
    if "hand_motor_joint" in msg.name:
        st["m"] = msg.position[msg.name.index("hand_motor_joint")]
rospy.Subscriber("/hsrb/joint_states", JointState, cb)
t0 = time.time()
while pub.get_num_connections() == 0 and time.time()-t0 < 5: time.sleep(0.1)
assert pub.get_num_connections() > 0, "no subscriber on gripper /command"
time.sleep(1.0)

rows = []
for a in ANGLES:
    tr = JointTrajectory(); tr.joint_names = ["hand_motor_joint"]
    p = JointTrajectoryPoint(); p.positions = [a]; p.time_from_start = rospy.Duration(1.5)
    tr.points = [p]; pub.publish(tr); time.sleep(2.3)
    try:
        t = buf.lookup_transform(TIP_L, TIP_R, rospy.Time(0), rospy.Duration(2.0))
        v = t.transform.translation
        gap = float(np.linalg.norm([v.x, v.y, v.z]))
    except Exception as e:
        print("TF fail at %.2f: %s" % (a, e)); continue
    print("cmd %+.2f  motor %+.3f  tip gap %6.1f mm" % (a, st["m"] if st["m"] is not None else float("nan"), gap*1000))
    rows.append((a, st["m"], gap))

tr = JointTrajectory(); tr.joint_names = ["hand_motor_joint"]
p = JointTrajectoryPoint(); p.positions = [1.0]; p.time_from_start = rospy.Duration(1.5)
tr.points = [p]; pub.publish(tr); time.sleep(2.0)
with open("gripper_gap_map.csv", "w") as f:
    w = csv.writer(f); w.writerow(["cmd_angle", "motor_angle", "gap_m"]); w.writerows(rows)
print("gripper reopened; wrote gripper_gap_map.csv")
