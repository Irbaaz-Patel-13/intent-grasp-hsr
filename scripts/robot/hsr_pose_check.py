#!/usr/bin/env python3
r"""hsr_pose_check.py -- verify an arm pose against the URDF BEFORE commanding it.

    python3 hsr_pose_check.py --limits                 # print all joint limits
    python3 hsr_pose_check.py --current                # evaluate the current pose
    python3 hsr_pose_check.py --pose lift=0.685,flex=-0.75,roll=0,wflex=-1.30,wroll=0
    python3 hsr_pose_check.py --sweep flex=-2.6:0.0:0.2 --at lift=0.0

WHY THIS EXISTS
On 1 Aug an unverified pose (arm_flex -2.55 with arm_lift driven to 0.0) put the
hand into the floor and required an e-stop. Every other stage of this pipeline
checks itself before moving -- pre-flight C5 joint margins, C6 approach sweep,
C7 FK sanity, G1/G2/G3 gates -- but the capture poses were authored by hand and
commanded directly. This closes that gap: it reads the SAME hsrb.urdf the
executor uses, runs the SAME forward kinematics, and reports the palm and
fingertip heights, the distance to the head keep-out sphere, and whether every
joint is inside its URDF limit.

Nothing here moves the robot. Run it, read the verdict, then command the pose.
"""
import argparse, sys
import xml.etree.ElementTree as ET
import numpy as np

ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint",
       "wrist_flex_joint", "wrist_roll_joint"]
ALIAS = {"lift": "arm_lift_joint", "flex": "arm_flex_joint",
         "roll": "arm_roll_joint", "wflex": "wrist_flex_joint",
         "wroll": "wrist_roll_joint"}
LOCKED = {"wrist_ft_sensor_frame_joint"}
# head keep-out: centre in base_link and radius, as used by hsr_hand_view.py
HEAD_C, HEAD_R = np.array([0.05, 0.0, 1.20]), 0.22
FLOOR_MIN = 0.12          # palm/fingertips must stay this far above base z=0


def aaR(ax, th):
    ax = ax / (np.linalg.norm(ax) or 1); x, y, z = ax
    c, s, C = np.cos(th), np.sin(th), 1 - np.cos(th)
    return np.array([[c+x*x*C, x*y*C-z*s, x*z*C+y*s],
                     [y*x*C+z*s, c+y*y*C, y*z*C-x*s],
                     [z*x*C-y*s, z*y*C+x*s, c+z*z*C]])


def Rx(a): c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=np.cos(a),np.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=np.cos(a),np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def Tf(xyz, rpy):
    T = np.eye(4); T[:3, :3] = Rz(rpy[2]) @ Ry(rpy[1]) @ Rx(rpy[0]); T[:3, 3] = xyz
    return T


def load_urdf(path):
    r = ET.parse(path).getroot(); J = {}
    for j in r.findall("joint"):
        o = j.find("origin"); xyz = [0,0,0]; rpy = [0,0,0]
        if o is not None:
            xyz = [float(v) for v in o.get("xyz", "0 0 0").split()]
            rpy = [float(v) for v in o.get("rpy", "0 0 0").split()]
        ax = [1,0,0]; aa = j.find("axis")
        if aa is not None: ax = [float(v) for v in aa.get("xyz", "1 0 0").split()]
        lim = j.find("limit"); lo = hi = None
        if lim is not None:
            lo = float(lim.get("lower")) if lim.get("lower") is not None else None
            hi = float(lim.get("upper")) if lim.get("upper") is not None else None
        J[j.get("name")] = dict(type=j.get("type"),
                                parent=j.find("parent").get("link"),
                                child=j.find("child").get("link"),
                                xyz=xyz, rpy=rpy, axis=np.array(ax, float),
                                lower=lo, upper=hi)
    return J


def chain(J, root, tip):
    bc = {v["child"]: k for k, v in J.items()}
    seq, link = [], tip
    while link in bc and link != root:
        jn = bc[link]; seq.append(jn); link = J[jn]["parent"]
    return list(reversed(seq))


def fk_points(J, seq, q):
    """Return {link_name: position} for every link along the chain."""
    T = np.eye(4); pts = {}
    for jn in seq:
        j = J[jn]; T = T @ Tf(j["xyz"], j["rpy"])
        if j["type"] in ("revolute", "continuous", "prismatic") and jn not in LOCKED:
            v = q.get(jn, 0.0); ax = j["axis"] / (np.linalg.norm(j["axis"]) or 1)
            M = np.eye(4)
            if j["type"] == "prismatic": M[:3, 3] = ax * v
            else: M[:3, :3] = aaR(ax, v)
            T = T @ M
        pts[j["child"]] = T[:3, 3].copy()
    return pts, T


def parse_pose(s):
    q = {}
    for kv in s.split(","):
        k, v = kv.split("=")
        k = k.strip(); q[ALIAS.get(k, k)] = float(v)
    return q


def evaluate(J, seq, q, verbose=True):
    problems = []
    for jn in ARM:
        j = J.get(jn)
        if j is None or j["lower"] is None: continue
        v = q.get(jn, 0.0)
        if v < j["lower"] - 1e-6 or v > j["upper"] + 1e-6:
            problems.append("%s = %+.3f is OUTSIDE [%.3f, %.3f]"
                            % (jn, v, j["lower"], j["upper"]))
        elif min(v - j["lower"], j["upper"] - v) < 0.05:
            problems.append("%s = %+.3f is within 0.05 rad of a limit [%.3f, %.3f]"
                            % (jn, v, j["lower"], j["upper"]))
    pts, T = fk_points(J, seq, q)
    palm = T[:3, 3]
    lowest_name, lowest = min(((k, v) for k, v in pts.items()), key=lambda kv: kv[1][2])
    head_d = min(np.linalg.norm(p - HEAD_C) for p in pts.values())
    if lowest[2] < FLOOR_MIN:
        problems.append("FLOOR: '%s' at z = %.3f m (minimum %.2f) -- would strike "
                        "the ground" % (lowest_name, lowest[2], FLOOR_MIN))
    if head_d < HEAD_R:
        problems.append("HEAD: closest link is %.3f m from the head keep-out centre "
                        "(radius %.2f)" % (head_d, HEAD_R))
    if verbose:
        print("  palm (base_link)     : [%.3f %.3f %.3f]" % tuple(palm))
        print("  lowest link          : %s at z = %.3f m" % (lowest_name, lowest[2]))
        print("  closest to head c/o  : %.3f m (keep-out radius %.2f)" % (head_d, HEAD_R))
    # FLOOR and HEAD violations must sort before proximity-to-limit nags: on
    # 1 Aug a sweep row 62 mm BELOW the floor displayed only "arm_lift within
    # 0.05 rad of a limit", because the display showed problems[0].
    problems.sort(key=lambda p: 0 if p.startswith(("FLOOR", "HEAD")) else
                                (1 if "OUTSIDE" in p else 2))
    return problems, palm, lowest[2], head_d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urdf", default="hsrb.urdf")
    ap.add_argument("--tip", default="hand_palm_link")
    ap.add_argument("--limits", action="store_true")
    ap.add_argument("--current", action="store_true")
    ap.add_argument("--pose")
    ap.add_argument("--sweep", help="joint=lo:hi:step, e.g. flex=-2.6:0.0:0.2")
    ap.add_argument("--at", default="", help="fixed joints for --sweep")
    a = ap.parse_args()

    J = load_urdf(a.urdf)
    seq = chain(J, "base_link", a.tip)

    if a.limits:
        print("JOINT LIMITS from %s" % a.urdf)
        for jn in ARM + ["hand_motor_joint", "head_pan_joint", "head_tilt_joint"]:
            j = J.get(jn)
            if not j: print("  %-22s NOT FOUND" % jn); continue
            print("  %-22s %-10s [%s, %s]" % (jn, j["type"],
                  "%.4f" % j["lower"] if j["lower"] is not None else "-",
                  "%.4f" % j["upper"] if j["upper"] is not None else "-"))
        print("\nchain base_link -> %s:\n  %s" % (a.tip, " -> ".join(seq)))
        return

    if a.current:
        import rospy
        from sensor_msgs.msg import JointState
        rospy.init_node("pose_check", anonymous=True)
        m = rospy.wait_for_message("/hsrb/joint_states", JointState, timeout=5.0)
        q = {k: m.position[m.name.index(k)] for k in ARM if k in m.name}
        print("CURRENT POSE: %s" % {k: round(v, 3) for k, v in q.items()})
        probs, *_ = evaluate(J, seq, q)
    elif a.pose:
        q = parse_pose(a.pose)
        for k in ARM: q.setdefault(k, 0.0)
        print("CANDIDATE POSE: %s" % {k: round(v, 3) for k, v in q.items()})
        probs, *_ = evaluate(J, seq, q)
    elif a.sweep:
        name, rng = a.sweep.split("=")
        lo, hi, st = [float(x) for x in rng.split(":")]
        base = parse_pose(a.at) if a.at else {}
        for k in ARM: base.setdefault(k, 0.0)
        jn = ALIAS.get(name.strip(), name.strip())
        print("SWEEP %s from %.2f to %.2f (fixed: %s)"
              % (jn, lo, hi, {k: round(v,2) for k, v in base.items() if k != jn}))
        print("  %-8s %-24s %-9s %-9s %s" % ("value", "palm xyz", "lowest z", "head d", "verdict"))
        v = lo
        while v <= hi + 1e-9:
            q = dict(base); q[jn] = v
            probs, palm, low, hd = evaluate(J, seq, q, verbose=False)
            print("  %+7.2f  [%6.3f %6.3f %6.3f]  %7.3f   %7.3f   %s"
                  % (v, palm[0], palm[1], palm[2], low, hd,
                     "OK" if not probs else probs[0][:44]))
            v += st
        return
    else:
        ap.print_help(); return

    print()
    if probs:
        print("REJECTED -- do not command this pose:")
        for p in probs: print("   * %s" % p)
        sys.exit(1)
    print("POSE OK: inside all joint limits, clear of the floor and the head.")


if __name__ == "__main__":
    main()
