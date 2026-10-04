#!/usr/bin/env python3
"""Tuck the arm to a neutral pose so the head camera has a clear view (refine rule)."""
import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
rospy.init_node("go_stow", anonymous=True)
pub = rospy.Publisher("/hsrb/arm_trajectory_controller/command", JointTrajectory, queue_size=1)
rospy.sleep(1.5)
names = ["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
jt = JointTrajectory(); jt.joint_names = names
p = JointTrajectoryPoint(); p.positions = [0.0, 0.0, 0.0, -1.57, 0.0]
p.velocities = [0.0]*5; p.time_from_start = rospy.Duration(5.0)
jt.points = [p]; jt.header.stamp = rospy.Time(0)
pub.publish(jt); rospy.sleep(6.0); print("arm stowed")
