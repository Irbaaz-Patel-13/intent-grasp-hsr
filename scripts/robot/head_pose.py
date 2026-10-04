#!/usr/bin/env python3
import sys, rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
tilt = float(sys.argv[1]) if len(sys.argv) > 1 else -0.60
rospy.init_node("head_pose", anonymous=True)
pub = rospy.Publisher("/hsrb/head_trajectory_controller/command", JointTrajectory, queue_size=1)
rospy.sleep(1.0)
jt = JointTrajectory(); jt.joint_names = ["head_pan_joint", "head_tilt_joint"]
p = JointTrajectoryPoint(); p.positions = [0.0, tilt]; p.velocities = [0.0, 0.0]
p.time_from_start = rospy.Duration(2.5); jt.points = [p]; jt.header.stamp = rospy.Time(0)
pub.publish(jt); rospy.sleep(3.5); print("head tilt -> %.2f" % tilt)
