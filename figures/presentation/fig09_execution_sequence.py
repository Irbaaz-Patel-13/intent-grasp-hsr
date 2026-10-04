"""
fig09_execution_sequence.py -- Figure 9: Execution Sequence / Safety Gates
(v2 -- 3D canonical-scene rebuild).

Scientific question: how is a real GRASP_OK/FAILED verdict actually
determined during execution?
Scientific claim: the real verdict is determined by three explicit,
hardware-calibrated safety gates (G1 base-settled, G2 palm-vs-FK, G3
lift-verify). G2 and G3 correspond to two real, distinct arm
configurations (grasp pose, post-lift pose) and are rendered as two real
3D frames from the same scene/camera. G1 (base-settled) is a base/odometry
check, not a distinct arm pose -- no separate joint configuration exists
for it, so it is NOT rendered as a posed frame; it is stated as such
rather than invented.
Supporting evidence: trials.csv (real per-trial g1_xy, g2_pos_err,
  g2_ori_deg, hand_motor, z_rise_m, lift_executed, verdict -- trial 12
  used here); scripts/robot/execute_place_grasp_raw.py
  (exact G1/G2/G3 predicates, spot-verified: g_settled moved<0.03m &
  yaw<3deg & speed<0.02; g_palm pos_err<0.02m & ori_err<15deg; g_lift
  rose>0.5*lift_commanded & hand_motor>eps, eps=-0.885 "calibrated
  2026-07-06"; the lift ramp loop only steps ARM[0]=arm_lift_joint, so the
  "lift" frame differs from the "grasp" frame by a pure arm_lift_joint
  delta, not an invented trajectory).
Required real data: trial 12's g1_xy, g2_pos_err, g2_ori_deg, hand_motor,
  z_rise_m, lift_executed, verdict -- used directly for all printed
  metrics. Pose geometry: candidate 24's real FK-validated joint values
  (place_run.csv) + the real z_rise_m magnitude applied as the documented
  single-axis lift delta -- the SAME cross-session convention as Figure 11
  (trial 12's own joint state was not separately logged; only its scalar
  gate values were).
Required diagrammatic elements: the two-frame staging is a reconstructed
  diagram -- no execution photographs exist for any trial. No interpolated
  motion is shown between frames.

Run: python fig09_execution_sequence.py [--exp-dir DIR]
Output: generated_assets/fig09/fig09_execution_sequence.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs
import fig_data as fd
import scene3d as s3

TRIAL_NOTE_MATCH = "trial 12"
G1_THRESH_M, G1_THRESH_DEG = 0.03, 3.0
G2_THRESH_M, G2_THRESH_DEG = 0.02, 15.0
G3_EPS = -0.885

FRAME_RGBA = (0.62, 0.80, 0.66, 1.0)  # single consistent robot colour across both real frames


def _find_trial(rows, note_substr):
    for r in rows:
        if note_substr in r["note"]:
            return r
    raise ValueError(f"no trial found with note containing {note_substr!r}")


def render_frame(scene, joints, width=900, height=1000):
    client = s3.connect()
    robot_id, ji = s3.load_robot(client, rgba=FRAME_RGBA)
    s3.pose_robot(client, robot_id, ji, scene.base_selected, joints)

    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    T_world_base = s3.world_base_transform(*scene.base_selected)
    palm = (T_world_base @ s3.fk(J, seq, joints))[:3, 3]

    bx, by = scene.base_selected[0], scene.base_selected[1]
    center = np.array([bx, by, palm[2]])
    extent = 1.2
    view, proj, eye = s3.view_and_projection(s3.CAM_SIDE, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    import pybullet as pb
    pb.disconnect(client)

    fig = plt.figure(figsize=(width / 200, height / 200), dpi=200, facecolor=fs.SLIDE_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    cpx, cpy, cdepth, cvalid = s3.project_points(scene.cloud, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=1.8, color=fs.MUTED, alpha=0.5, zorder=1, linewidths=0)
    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)
    return fig


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    rows = fd.load_trials()
    trial = _find_trial(rows, TRIAL_NOTE_MATCH)
    scene = s3.build_scene(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig09"), "fig09_execution_sequence.png")

    g1_xy = float(trial["g1_xy"])
    g2_pos_err = float(trial["g2_pos_err"])
    g2_ori_deg = float(trial["g2_ori_deg"])
    hand_motor = float(trial["hand_motor"])
    z_rise_m = float(trial["z_rise_m"])
    lift_executed = trial["lift_executed"]
    verdict = trial["verdict"]

    g1_pass = g1_xy < G1_THRESH_M
    g2_pass = (g2_pos_err < G2_THRESH_M) and (g2_ori_deg < G2_THRESH_DEG)
    g3_pass = (hand_motor > G3_EPS) and (lift_executed == "yes")

    joints_grasp = dict(scene.joints_selected)
    joints_lift = dict(scene.joints_selected)
    joints_lift["arm_lift_joint"] = joints_grasp["arm_lift_joint"] + z_rise_m

    tmp_paths = []
    frames = []
    for tag, joints in [("grasp", joints_grasp), ("lift", joints_lift)]:
        f = render_frame(scene, joints)
        tmp_path = os.path.join(fs.asset_dir("fig09"), f"_frame_{tag}_tmp.png")
        f.savefig(tmp_path, facecolor=fs.SLIDE_BG)
        plt.close(f)
        frames.append(mpimg.imread(tmp_path))
        tmp_paths.append(tmp_path)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 9 -- Execution Sequence: Real Safety Gates", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885, "Trial 12 (2026-08-01), real logged gate values -- two real 3D frames "
              "(grasp, post-lift), reconstructed staging, no execution photographs exist", **fs.BODY)

    fig.text(0.09, 0.855, "G1: BASE-SETTLED", **fs.SECTION)
    fig.text(0.09, 0.825, f"(no distinct arm pose -- base/odometry check only)  "
              f"g1_xy = {g1_xy:.4f} m  (< {G1_THRESH_M} m)  {'PASS' if g1_pass else 'FAIL'}",
              color=(fs.ACCEPTED if g1_pass else fs.REJECTED), fontsize=10, family=fs.FONT, va="top")

    verdict_color = fs.ACCEPTED if verdict == "GRASP_OK" else fs.REJECTED
    fig.text(0.94, 0.855, f"Real logged verdict: {verdict}", ha="right",
             color=verdict_color, fontsize=13, weight="bold", family=fs.FONT)

    ax1 = fig.add_axes([0.05, 0.13, 0.40, 0.58])
    ax1.imshow(frames[0])
    ax1.axis("off")
    ax1.set_title("G2: PALM vs FK (grasp pose)", color=(fs.ACCEPTED if g2_pass else fs.REJECTED),
                  fontsize=12.5, weight="bold", family=fs.FONT)
    fig.text(0.05, 0.105, f"pos_err = {g2_pos_err:.4f} m (< {G2_THRESH_M})   "
              f"ori_err = {g2_ori_deg:.2f} deg (< {G2_THRESH_DEG})   {'PASS' if g2_pass else 'FAIL'}",
              color=(fs.ACCEPTED if g2_pass else fs.REJECTED), fontsize=10, family=fs.FONT)

    ax2 = fig.add_axes([0.53, 0.13, 0.40, 0.58])
    ax2.imshow(frames[1])
    ax2.axis("off")
    ax2.set_title("G3: LIFT-VERIFY (post-lift pose)", color=(fs.ACCEPTED if g3_pass else fs.REJECTED),
                  fontsize=12.5, weight="bold", family=fs.FONT)
    fig.text(0.53, 0.105, f"hand_motor = {hand_motor:.4f} (> {G3_EPS})   z_rise = {z_rise_m:.4f} m   "
              f"lift_executed = {lift_executed}   {'PASS' if g3_pass else 'FAIL'}",
              color=(fs.ACCEPTED if g3_pass else fs.REJECTED), fontsize=10, family=fs.FONT)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Rendered from logged joint values through the HSR URDF (candidate #24, place_run.csv) -- "
              "geometry is the robot description, pose is measured; not a photograph. Gate thresholds are",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "real code constants. Pose is the anchor capture/candidate 24 (self-consistent); gate values "
              "are trial 12's own real measurements -- a different real session, stated explicitly.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    for tp in tmp_paths:
        if os.path.exists(tp):
            os.remove(tp)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig09 written to {path}")
