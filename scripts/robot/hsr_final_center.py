#!/usr/bin/env python3
"""Final centering v2 — UNCALIBRATED visual servoing (empirical image Jacobian).
v1's analytic model failed: pixel response rotated ~80deg from prediction
(hand camera mounting != TF frame; camera has no calibration). v2 probes
+2cm base-x and +2cm base-y, measures the pixel response, builds J, solves."""
import argparse, csv, os
import numpy as np
import rospy, tf2_ros
from sensor_msgs.msg import Image
from hsr_base_drive import BaseDriver

K_SIM = np.array([[205.4696371, 0, 320.5],[0, 205.4696371, 240.5],[0, 0, 1.0]])
CAM_FRAME = "hand_camera_frame"
RIM_Z = 0.56

def quat_to_R(x, y, z, w):
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
                     [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

def detect_mug_px(rgb):
    g = rgb.astype(float).mean(axis=2)
    H, W = g.shape
    cw = g[H//5:4*H//5, W//5:4*W//5]
    thr = np.percentile(cw, 97)
    # rim-ring detector (17 Jul): HoughCircles + CLAHE, scored by
    # bright-interior-minus-dark-perimeter. Scene-independent (white table OK);
    # validated offline on both 16 Jul failure images. Replaces brightest-blob.
    import cv2
    gg = np.clip(g, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gc = cv2.medianBlur(clahe.apply(gg), 5)
    circ = cv2.HoughCircles(gc, cv2.HOUGH_GRADIENT, dp=1.2, minDist=60,
                            param1=110, param2=42,
                            minRadius=int(0.05*W), maxRadius=int(0.16*W))
    best = None
    if circ is not None:
        for u, v, r in circ[0]:
            if not (W*0.08 < u < W*0.92 and H*0.08 < v < H*0.92): continue
            th = np.linspace(0, 2*np.pi, 90)
            pu = np.clip((u+r*np.cos(th)).astype(int), 0, W-1)
            pv = np.clip((v+r*np.sin(th)).astype(int), 0, H-1)
            iu = np.clip((u+0.5*r*np.cos(th)).astype(int), 0, W-1)
            iv = np.clip((v+0.5*r*np.sin(th)).astype(int), 0, H-1)
            score = float(gg[iv, iu].mean()) - float(gg[pv, pu].mean())
            if best is None or score > best[3]: best = (u, v, r, score)
    if best is None or best[3] < 8: return None, 0
    u, v, r = best[0], best[1], best[2]
    yy, xx = np.mgrid[0:H, 0:W]
    ys, xs = np.where((xx-u)**2 + (yy-v)**2 <= (0.6*r)**2)
    if len(xs) < 200: return None, len(xs)
    return np.array([float(xs.mean()), float(ys.mean())]), len(xs)

def grab_detect():
    msg = rospy.wait_for_message("/hsrb/hand_camera/image_raw", Image, timeout=6.0)
    rgb = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)[:, :, :3].copy()
    if "bgr" in msg.encoding.lower(): rgb = rgb[:, :, ::-1].copy()
    det, npx = detect_mug_px(rgb)
    return rgb, det, npx

def move_base_rel(bd, dx, dy):
    """Relative move in CURRENT base frame; returns the ACTUAL base-frame
    displacement measured from odometry (settle error would otherwise corrupt J)."""
    bx, by, bt = bd.pose()
    co, so = np.cos(bt), np.sin(bt)
    d_odom = np.array([co*dx - so*dy, so*dx + co*dy])
    ok, info = bd.move_to(bx + d_odom[0], by + d_odom[1], bt)
    if not ok: raise SystemExit("ABORT: probe/correction move did not settle: %s" % info)
    rospy.sleep(0.6)
    bx2, by2, bt2 = bd.pose()
    da = np.array([bx2 - bx, by2 - by])              # actual odom displacement
    actual = np.array([ co*da[0] + so*da[1],          # back into base frame
                       -so*da[0] + co*da[1]])
    print("[center] move: commanded (%.4f,%.4f) actual (%.4f,%.4f)" % (dx, dy, actual[0], actual[1]))
    return actual

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="place_run.csv"); ap.add_argument("--grasp", type=int, required=True)
    ap.add_argument("--tol_px", type=float, default=8.0)
    ap.add_argument("--probe", type=float, default=0.04)   # must exceed base settle tol (0.02)
    ap.add_argument("--max_step", type=float, default=0.12)
    ap.add_argument("--ref_file", default="place_run.ref")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    row = None
    for r in csv.DictReader(open(a.csv)):
        if int(r["grasp"]) == a.grasp: row = r; break
    if row is None: raise SystemExit("grasp %d not in %s" % (a.grasp, a.csv))

    rospy.init_node("final_center", anonymous=True)
    tfbuf = tf2_ros.Buffer(); tf2_ros.TransformListener(tfbuf)
    bd = BaseDriver()
    start_pose = np.array(bd.pose())

    from execute_place_grasp_raw import load_chain, fk
    J_, seq = load_chain("hsrb.urdf", "base_link", "hand_palm_link")
    q = dict(zip(["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"],
                 [float(row["q_lift"]), float(row["q_flex"]), float(row["q_roll"]),
                  float(row["q_wflex"]), float(row["q_wroll"])]))
    palm = fk(J_, seq, q)[:3, 3]

    tr = tfbuf.lookup_transform("base_link", CAM_FRAME, rospy.Time(0), rospy.Duration(3.0))
    t = tr.transform.translation; qo = tr.transform.rotation
    R = quat_to_R(qo.x, qo.y, qo.z, qo.w); T = np.array([t.x, t.y, t.z])
    pc = R.T @ (np.array([palm[0], palm[1], RIM_Z]) - T)
    if pc[2] <= 0.03: print("[center] NOTE: palm projection degenerate (pc_z=%.3f) -- irrelevant, GRASP_PX constant is used" % pc[2])
    fx, fy, cx, cy = K_SIM[0,0], K_SIM[1,1], K_SIM[0,2], K_SIM[1,2]
    # GRASP_PX (21 Jul): empirical target pixel = where the mug appears in the
    # hand camera when it is actually BETWEEN THE FINGERS. Folds together the
    # uncalibrated K (all zeros), the ~80 deg mount error, AND the
    # camera-to-finger offset (~45 px). Measured from two capturing closes:
    # (294.6,276.6) held -0.336 and (286.2,273.0) held -0.293; a miss sat at
    # (330.6,292.2). Palm-projection target REMOVED -- it was wrong on all three
    # counts. Override: GRASP_PX="u,v" in the environment.
    tgt = np.array([float(v) for v in os.environ.get("GRASP_PX", "290.4,274.8").split(",")])
    print("[center] GRASP_PX target px = (%.1f, %.1f)  [empirical, finger-frame]" % (tgt[0], tgt[1]))

    def save_debug(rgb, det, tag):
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8,6)); plt.imshow(rgb)
        plt.scatter([tgt[0]],[tgt[1]], c="lime", s=120, marker="+", label="grasp target")
        if det is not None: plt.scatter([det[0]],[det[1]], c="red", s=120, marker="x", label="detected mug")
        plt.legend(); plt.axis("off"); plt.tight_layout()
        plt.savefig("final_center_debug.png", dpi=110)

    rgb, p0, npx = grab_detect()
    save_debug(rgb, p0, "start")
    if p0 is None: raise SystemExit("ABORT: mug not detected (%d px)" % npx)
    err = float(np.linalg.norm(p0 - tgt))
    print("[center] start: detected=(%.1f,%.1f) err=%.1f px (%d px blob)" % (p0[0], p0[1], err, npx))
    if err < a.tol_px:
        print("[center] ALIGNED within %.1f px. Proceed to grasp." % err); return
    if a.dry:
        print("[dry] would probe +%.2fm x, +%.2fm y, then solve. Not moving." % (a.probe, a.probe)); return

    # --- empirical Jacobian from ACTUAL displacements, probes > settle noise ---
    a1 = move_base_rel(bd, a.probe, 0.0)
    _, p1, _ = grab_detect()
    if p1 is None: raise SystemExit("ABORT: lost mug after x-probe")
    a2 = move_base_rel(bd, 0.0, a.probe)
    _, p2, _ = grab_detect()
    if p2 is None: raise SystemExit("ABORT: lost mug after y-probe")
    A = np.column_stack([a1, a2])                       # actual moves (base frame)
    P = np.column_stack([p1 - p0, p2 - p1])             # pixel responses
    Jm = P @ np.linalg.inv(A)                            # J such that dpx = J @ dbase
    print("[center] empirical J (px/m):\n%s" % np.round(Jm, 1))
    if abs(np.linalg.det(Jm)) < 1e4:
        raise SystemExit("ABORT: Jacobian near-singular — probes too small or detector noisy")

    cur = p2
    GAIN = 0.7
    for it in range(5):
        d = GAIN * np.linalg.solve(Jm, tgt - cur)
        step = float(np.linalg.norm(d))
        if step > a.max_step:
            d = d * (a.max_step / step)                  # clamp, don't abort: J refines below
            print("[center] iter %d: clamped step to %.2f m" % (it, a.max_step))
        print("[center] iter %d: solving -> base move (%.4f, %.4f) m" % (it, d[0], d[1]))
        act = move_base_rel(bd, d[0], d[1])
        prev = cur
        rgb, cur, npx = grab_detect()
        save_debug(rgb, cur, "iter%d" % it)
        if cur is None: raise SystemExit("ABORT: lost mug during correction")
        # Broyden rank-1 update: correct J from the observed response to the actual move
        na = float(act @ act)
        if na > 1e-6:
            Jm = Jm + np.outer((cur - prev) - Jm @ act, act) / na
        err = float(np.linalg.norm(cur - tgt))
        print("[center] iter %d: detected=(%.1f,%.1f) err=%.1f px" % (it, cur[0], cur[1], err))
        if err < a.tol_px:
            end_pose = np.array(bd.pose())
            d_total = end_pose[:2] - start_pose[:2]
            if os.path.exists(a.ref_file):
                rx, ry, rt = (float(x) for x in open(a.ref_file).read().split(","))
                open(a.ref_file, "w").write("%f,%f,%f" % (rx + d_total[0], ry + d_total[1], rt))
                print("[center] ref_file shifted by TOTAL (%.4f, %.4f)" % (d_total[0], d_total[1]))
            print("[center] ALIGNED within %.1f px (~%.1f mm). Proceed to grasp." % (err, err*0.7))
            return
    raise SystemExit("ABORT: not converged after 5 solves — inspect final_center_debug.png")

if __name__ == "__main__":
    main()
