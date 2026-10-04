#!/usr/bin/env python3
"""HSR base drive via /hsrb/omni_base_controller/command (JointTrajectory).

Validated live 2026-07-04 at the Robotarium:
  +0.05m x     -> settle err 0.0021 m
  +0.10rad yaw -> settle err 0.0025 rad, xy drift 0.0009 m
  combo x/y/t  -> errs 0.0007/0.0007 m, 0.0035 rad
Frame: controller state (odom_x/odom_y/odom_t) == /hsrb/odom (verified numerically).
"""
import math, time, argparse
import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.msg import JointTrajectoryControllerState
from std_msgs.msg import Bool

TOPIC_CMD   = "/hsrb/omni_base_controller/command"
TOPIC_STATE = "/hsrb/omni_base_controller/state"
V_MAX   = 0.05                 # m/s   speed cap
W_MAX   = 0.30                 # rad/s yaw cap
TOL_XY  = 0.02                 # m     settle tolerance (matches G1)
TOL_YAW = math.radians(2.0)    # rad

def _wrap(a):
    return math.atan2(math.sin(a), math.cos(a))

class BaseDriver(object):
    def __init__(self, wait=5.0):
        self._pos = None
        self._sub = rospy.Subscriber(TOPIC_STATE, JointTrajectoryControllerState, self._cb)
        self._pub = rospy.Publisher(TOPIC_CMD, JointTrajectory, queue_size=1)
        self._bumped = False
        rospy.Subscriber("/hsrb/base_f_bumper_sensor", Bool, self._bump)
        rospy.Subscriber("/hsrb/base_b_bumper_sensor", Bool, self._bump)
        t0 = time.time()
        while self._pos is None and time.time() - t0 < wait and not rospy.is_shutdown():
            rospy.sleep(0.05)
        if self._pos is None:
            raise RuntimeError("no msg on %s -> base drive unavailable" % TOPIC_STATE)
        # wait for the publisher to actually connect to /hsrb/robot_hardware,
        # otherwise the first (only) trajectory publish is silently dropped
        t0 = time.time()
        while (self._pub.get_num_connections() == 0 and
               time.time() - t0 < wait and not rospy.is_shutdown()):
            rospy.sleep(0.05)
        if self._pub.get_num_connections() == 0:
            raise RuntimeError("no subscriber on %s -> command would be dropped" % TOPIC_CMD)
        print("[base] cmd topic connected (%d subscriber(s))" % self._pub.get_num_connections())

    def _cb(self, m):
        self._pos = list(m.actual.positions)   # [odom_x, odom_y, odom_t]

    def _bump(self, m):
        if getattr(m, "data", False):
            self._bumped = True

    def pose(self):
        return tuple(self._pos)

    def _send(self, x, y, t, duration):
        jt = JointTrajectory()
        jt.joint_names = ["odom_x", "odom_y", "odom_t"]
        p = JointTrajectoryPoint()
        p.positions = [x, y, t]
        p.velocities = [0.0, 0.0, 0.0]
        p.time_from_start = rospy.Duration(duration)
        jt.points = [p]
        jt.header.stamp = rospy.Time(0)
        self._pub.publish(jt)

    def hold(self):
        """Command current pose = immediate stop-and-hold (abort action)."""
        x, y, t = self.pose()
        self._send(x, y, t, 0.5)

    def move_to(self, tx, ty, tyaw, settle_extra=2.5):
        """Blocking move to absolute odom target. Returns (ok, info) like G1."""
        ox, oy, ot = self.pose()
        dist = math.hypot(tx - ox, ty - oy)
        dyaw = abs(_wrap(tyaw - ot))
        dur  = max(dist / V_MAX, dyaw / W_MAX, 3.0)
        print("[base] (%.3f,%.3f,%.1fdeg) -> (%.3f,%.3f,%.1fdeg)  d=%.3fm %.1fdeg  dur=%.1fs"
              % (ox, oy, math.degrees(ot), tx, ty, math.degrees(tyaw),
                 dist, math.degrees(dyaw), dur))
        self._send(tx, ty, tyaw, dur)
        deadline = time.time() + dur + settle_extra
        exy, eyaw = dist, dyaw
        while time.time() < deadline and not rospy.is_shutdown():
            rospy.sleep(0.1)
            if getattr(self, '_bumped', False):
                self.hold()
                return False, {'abort': 'BUMPER CONTACT — stopped'}
            x, y, t = self.pose()
            exy  = math.hypot(tx - x, ty - y)
            eyaw = abs(_wrap(tyaw - t))
            if exy < TOL_XY and eyaw < TOL_YAW:
                rospy.sleep(0.5)                      # confirm it stays settled
                x, y, t = self.pose()
                exy  = math.hypot(tx - x, ty - y)
                eyaw = abs(_wrap(tyaw - t))
                if exy < TOL_XY and eyaw < TOL_YAW:
                    return True, {"arrived_xy": round(exy, 4),
                                  "arrived_yaw": round(math.degrees(eyaw), 2)}
        self.hold()
        return False, {"arrived_xy": round(exy, 4),
                       "arrived_yaw": round(math.degrees(eyaw), 2),
                       "timeout_s": round(dur + settle_extra, 1)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="standalone relative base move test")
    ap.add_argument("--dx", type=float, default=0.0)
    ap.add_argument("--dy", type=float, default=0.0)
    ap.add_argument("--dyaw_deg", type=float, default=0.0)
    a = ap.parse_args()
    rospy.init_node("hsr_base_drive_test", anonymous=True)
    bd = BaseDriver()
    ox, oy, ot = bd.pose()
    dyaw = math.radians(a.dyaw_deg)
    # relative move expressed in CURRENT BASE frame, rotated into odom
    tx = ox + a.dx * math.cos(ot) - a.dy * math.sin(ot)
    ty = oy + a.dx * math.sin(ot) + a.dy * math.cos(ot)
    ok, info = bd.move_to(tx, ty, _wrap(ot + dyaw))
    print("settled:", ok, info)
