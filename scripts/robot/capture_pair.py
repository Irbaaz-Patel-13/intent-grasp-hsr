#!/usr/bin/env python3
r"""capture_pair.py -- multi-viewpoint capture of one object, for testing whether
a closer view resolves parts the head camera cannot.

    python3 capture_pair.py --label mug
    python3 capture_pair.py --label pot --dx 0.30 --near_tilt -0.75
    python3 capture_pair.py --label mug --grasp 5        # also capture hand camera

Motivation (measured 26-28 Jul): from the head camera at ~1 m the mug handle
returned 48 pts / 5 mm and the pot handle 75 pts / 5 mm -- both below the depth
sensor's evidence floor, so part-scoped grasping correctly refused. The open
question is whether that is a RANGE limit or a fundamental one. This captures the
same object from:
    head_far   standard pose (~1.0 m, tilt -0.50)   = today's baseline
    head_near  driven --dx closer, steeper tilt     = the actual test (RGB-D)
    hand       hand camera at the grasp hover pose  = qualitative only; the hand
               camera is RGB-only with K = all zeros, so it cannot produce a
               point cloud -- it shows what is VISIBLE, not what is measurable
and returns the base to where it started, so the scene stays reproducible.

Requires: go_stow.py, head_pose.py, capture_real.py, hsr_base_drive.py.
--grasp N additionally uses the joint configuration of grasp N from
place_run.csv for the hand-camera pose (a configuration already validated on
this table height), then restows.
"""
import argparse, csv, os, subprocess, sys, time

ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint",
       "wrist_flex_joint", "wrist_roll_joint"]
COLS = ["q_lift", "q_flex", "q_roll", "q_wflex", "q_wroll"]
CAM_TOPICS = ["/hsrb/hand_camera/image_raw",
              "/hsrb/hand_camera/image_rect_color"]


def run(cmd):
    print("   $ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        if any(k in line for k in ("depth(m)", "saved ->", "settled", "arm stowed",
                                   "head tilt", "ABORT", "Error", "error")):
            print("     " + line.strip())
    if r.returncode != 0:
        print("     (exit %d)" % r.returncode)
    return r.returncode == 0, out



def scene_geometry(npz_path, radius=0.25):
    """Support-plane height and object top from a head capture, in base_link.

    Replicates adapt_real_capture's transform: pinhole backprojection into the
    camera frame, then T_base_cam from the stored TF. Used to place the hand
    camera a fixed distance ABOVE the object rather than at a guessed height.
    """
    import numpy as np
    from scipy.spatial.transform import Rotation
    d = np.load(npz_path, allow_pickle=True)
    keys = {k.lower(): k for k in d.files}
    depth = np.asarray(d[keys.get("depth", "depth")]).astype(float)
    if depth.max() > 100:            # stored in mm
        depth = depth / 1000.0
    K = np.asarray(d[keys.get("k", "K")]).astype(float)
    trans = np.asarray(d[keys.get("tf_trans", "tf_trans")]).ravel()
    quat = np.asarray(d[keys.get("tf_quat", "tf_quat")]).ravel()
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (depth > 0.05) & (depth < 4.0)
    z = depth[ok]
    x = (u[ok] - K[0, 2]) * z / K[0, 0]
    y = (v[ok] - K[1, 2]) * z / K[1, 1]
    pc = np.stack([x, y, z], axis=-1)
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat(quat).as_matrix()
    T[:3, 3] = trans
    pb = (T[:3, :3] @ pc.T).T + T[:3, 3]
    # Restrict hard to the tabletop workspace. Without this the chair back, sofa
    # and equipment rack are counted as "above the plane": the 28 Jul run saw
    # 38323 such points and reported obj_top = 0.768 m for a mug, which drove the
    # arm to its lift limit and into the head.
    fwd = pb[(pb[:, 0] > 0.45) & (pb[:, 0] < 1.05) & (np.abs(pb[:, 1]) < 0.35)]
    if len(fwd) < 500:
        return None
    hh, ee = np.histogram(fwd[:, 2], bins=90)
    plane_z = float(0.5 * (ee[int(np.argmax(hh))] + ee[int(np.argmax(hh)) + 1]))
    # only points in a plausible tabletop-object band count
    above = fwd[(fwd[:, 2] > plane_z + 0.012) & (fwd[:, 2] < plane_z + 0.30)]
    if len(above) < 100:
        return dict(plane_z=plane_z, obj_top=plane_z, n_above=len(above),
                    note="no object band found")
    c = np.median(above[:, :2], axis=0)
    near = above[np.linalg.norm(above[:, :2] - c, axis=1) < radius]
    obj_top = float(np.percentile(near[:, 2], 98)) if len(near) > 50 else plane_z
    obj_top = min(obj_top, plane_z + 0.30)          # hard sanity cap
    return dict(plane_z=plane_z, obj_top=obj_top, n_above=len(above),
                object_height=round(obj_top - plane_z, 3),
                centroid_xy=[round(float(x), 3) for x in c])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="object name, e.g. mug")
    ap.add_argument("--dx", type=float, default=0.25, help="how much closer (m)")
    ap.add_argument("--far_tilt", type=float, default=-0.50)
    ap.add_argument("--near_tilt", type=float, default=-0.70)
    ap.add_argument("--grasp", type=int, default=None,
                    help="also capture the hand camera using grasp N's joint pose")
    ap.add_argument("--csv", default="place_run.csv")
    ap.add_argument("--outdir", default="captures_pairs")
    ap.add_argument("--no-duck", dest="duck", action="store_false",
                    help="do not tuck the arm before the near capture")
    ap.set_defaults(duck=True)
    ap.add_argument("--hand", action="store_true",
                    help="also capture the hand camera, hovering at a height derived "
                         "from the near capture (needs --grasp as the pose template)")
    ap.add_argument("--clearance", type=float, default=0.22,
                    help="(unused for motion; kept for logging)")
    ap.add_argument("--hand_z_max", type=float, default=0.85,
                    help="ceiling on hand height")
    ap.add_argument("--max_raise", type=float, default=0.06,
                    help="most the hover may exceed the validated grasp lift (m)")
    ap.add_argument("--lift_cap", type=float, default=0.62,
                    help="absolute arm_lift ceiling for the hand pose; 0.685 put "
                         "the hand into the head on 28 Jul")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    py = sys.executable

    def head_capture(tag, tilt):
        print("\n== %s capture (tilt %.2f) ==" % (tag, tilt))
#         run([py, "go_stow.py"])
        # At close range with a steep tilt the head sees its own stowed arm: on
        # 28 Jul the gripper sat beside the mug in every near capture. Tuck it
        # further before the near view.
        if a.duck and tag.endswith("near") and os.path.exists("hsr_duck.py"):
            run([py, "hsr_duck.py"])
        run([py, "head_pose.py", str(tilt)])
        ok, out = run([py, "capture_real.py"])
        if not ok:
            sys.exit("capture_real.py failed for %s" % tag)
        dst = os.path.join(a.outdir, "cap_%s_%s.npz" % (a.label, tag))
        subprocess.run(["cp", "head_capture_real.npz", dst])
        for line in out.splitlines():
            if "depth(m)" in line:
                print("     -> %s   [%s]" % (dst, line.strip()))
                break
        else:
            print("     -> %s" % dst)

    # 1. baseline
    head_capture("head_far", a.far_tilt)

    # 2. drive closer and repeat
    print("\n== driving %.2f m closer ==" % a.dx)
    ok, _ = run([py, "hsr_base_drive.py", "--dx", str(a.dx)])
    if not ok:
        sys.exit("base drive failed -- not capturing near view")
    head_capture("head_near", a.near_tilt)

    # 3. optional hand-camera view at a validated arm configuration
    if a.hand or a.grasp is not None:
        print("\n== hand camera, hover derived from the scene ==")
        geo = scene_geometry(os.path.join(a.outdir, "cap_%s_head_near.npz" % a.label))
        if geo:
            print("   scene: plane_z %.3f  obj_top %.3f  (%d pts above plane)"
                  % (geo["plane_z"], geo["obj_top"], geo["n_above"]))
        else:
            print("   scene geometry unavailable -- using the grasp pose unchanged")
        if not os.path.exists(a.csv):
            print("   %s not found -- skipping hand capture" % a.csv)
        else:
            row = next((r for r in csv.DictReader(open(a.csv))
                        if r["grasp"] == str(a.grasp)), None)
            if row is None:
                print("   grasp %d not in %s -- skipping" % (a.grasp, a.csv))
            else:
                q = {k: float(row[c]) for k, c in zip(ARM, COLS)}
                # raise arm_lift so the hand sits --clearance above the object.
                # arm_lift is prismatic and vertical, so a Δ in the joint is a Δ
                # in palm height; every other joint keeps the validated pose.
                # HEIGHT COMES FROM THE VALIDATED GRASP POSE, NOT THE SCENE.
                # Deriving it from depth was tried on 28 Jul and failed twice:
                # the "object top" landed on the chair back behind the table
                # (obj_top 0.75 m for a mug), which drove arm_lift to its limit
                # and put the hand into the head. Segmenting the object well
                # enough to trust with arm motion is the same hard problem the
                # pipeline is still solving, so this uses a bounded offset from
                # a configuration already executed successfully on this table.
                base_lift = q["arm_lift_joint"]
                newlift = min(base_lift + a.max_raise, a.lift_cap)
                print("   hover: arm_lift %.3f -> %.3f  (grasp pose + %.3f, cap %.3f)"
                      % (base_lift, newlift, a.max_raise, a.lift_cap))
                if geo:
                    print("   [scene geometry, DIAGNOSTIC ONLY -- not used for motion]"
                          "  plane_z %.3f  obj_top %.3f  n_above %d"
                          % (geo["plane_z"], geo["obj_top"], geo["n_above"]))
                    if geo.get("object_height", 0) >= 0.29:
                        print("   NOTE: object_height hit the 0.30 m cap -- the depth"
                              " segmentation is picking up background, as expected")
                q["arm_lift_joint"] = newlift
                try:
                    import rospy
                    from sensor_msgs.msg import JointState, Image
                    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
                    rospy.init_node("cap_pair", anonymous=True)
                    st = {}
                    rospy.Subscriber("/hsrb/joint_states", JointState,
                                     lambda m: st.update(dict(zip(m.name, m.position))))
                    pa = rospy.Publisher("/hsrb/arm_trajectory_controller/command",
                                         JointTrajectory, queue_size=1)
                    t0 = time.time()
                    while ("arm_lift_joint" not in st or pa.get_num_connections() == 0) \
                            and time.time() - t0 < 6:
                        time.sleep(0.1)
                    # HEAD TO NEUTRAL before any arm motion. With the head
                    # tilted down its housing sits forward and low, in the arm's
                    # path -- this is why the hand struck it on 28 Jul.
                    ph = rospy.Publisher("/hsrb/head_trajectory_controller/command",
                                         JointTrajectory, queue_size=1)
                    time.sleep(0.6)
                    hj = JointTrajectory(); hj.joint_names = ["head_pan_joint", "head_tilt_joint"]
                    hp = JointTrajectoryPoint(); hp.positions = [0.0, 0.0]
                    hp.time_from_start = rospy.Duration(2.0)
                    hj.points = [hp]; hj.header.stamp = rospy.Time(0)
                    ph.publish(hj); time.sleep(2.5)
                    print("   head -> neutral before arm motion")
                    # lift-first transit, then extend (incident #8)
                    cur = {k: float(st.get(k, 0.0)) for k in ARM}
                    up = dict(cur); up["arm_lift_joint"] = q["arm_lift_joint"]
                    jt = JointTrajectory(); jt.joint_names = ARM
                    for pos, t in ((up, 4.0), (q, 8.0)):
                        p = JointTrajectoryPoint()
                        p.positions = [pos[k] for k in ARM]; p.velocities = [0.0]*5
                        p.time_from_start = rospy.Duration(t); jt.points.append(p)
                    jt.header.stamp = rospy.Time(0); pa.publish(jt); time.sleep(9.0)
                    print("   at hover: arm_lift %.3f" % st.get("arm_lift_joint", 0))
                    got = None
                    for topic in CAM_TOPICS:
                        try:
                            got = (topic, rospy.wait_for_message(topic, Image, timeout=3.0)); break
                        except Exception:
                            continue
                    if got is None:
                        print("   no hand-camera image on %s" % CAM_TOPICS)
                    else:
                        import cv2, numpy as np
                        from cv_bridge import CvBridge
                        img = CvBridge().imgmsg_to_cv2(got[1], desired_encoding="bgr8")
                        dst = os.path.join(a.outdir, "cap_%s_hand.png" % a.label)
                        cv2.imwrite(dst, img)
                        np.savez(os.path.join(a.outdir, "cap_%s_hand.npz" % a.label),
                                 rgb=img[:, :, ::-1], source=got[0],
                                 arm_config=[q[k] for k in ARM])
                        print("   -> %s  (%dx%d, from %s)"
                              % (dst, img.shape[1], img.shape[0], got[0]))
                except Exception as e:
                    print("   hand capture failed: %s: %s" % (type(e).__name__, e))
                finally:
                    pass

    # 4. drive back
    print("\n== returning %.2f m ==" % a.dx)
    run([py, "hsr_base_drive.py", "--dx", str(-a.dx)])
#     run([py, "go_stow.py"])
    print("\nDONE: %s" % a.label)
    print("files in %s/: cap_%s_head_far.npz, cap_%s_head_near.npz%s"
          % (a.outdir, a.label, a.label,
             ", cap_%s_hand.png" % a.label if (a.hand or a.grasp is not None) else ""))
    print("Place the next object and rerun with a new --label.")


if __name__ == "__main__":
    main()
