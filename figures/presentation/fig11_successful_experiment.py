"""
fig11_successful_experiment.py -- Figure 11: Successful Experiment (v2 --
3D canonical-scene rebuild).

Scientific question: did the full pipeline achieve a real, verified,
autonomous successful grasp on real hardware?
Scientific claim: a specific real trial (trial 9, 2026-08-01) -- fully
autonomous, no hand-placement -- achieved a verified grasp and lift,
passing the real safety gates. The lift itself is shown as a real vertical
displacement, not just a printed number.
Supporting evidence: trials.csv trial 9 (real z_rise_m=0.1420, hand_motor,
  g1_xy, g2_pos_err, g2_ori_deg, verdict=GRASP_OK, explicit "fully
  autonomous... no hand-placing" note). Scene/pose geometry: the
  2026-08-07 anchor capture's real point cloud and candidate 24's real
  logged joint values (place_run.csv), via scene3d.build_scene -- a
  DIFFERENT real session than trial 9 itself, since no point cloud or
  joint state was separately saved for the 2026-08-01 session. Stated
  explicitly so the two real sources are never conflated.
Required real data: trial 9's real per-gate/lift values (used directly for
  all printed metrics); candidate 24's real FK-validated joint values (used
  for the rendered pose); the real z_rise_m magnitude (0.1420 m) applied as
  a pure arm_lift_joint delta to that pose (only arm_lift_joint moves during
  the real lift ramp -- scripts/robot/
  execute_place_grasp_raw.py's lift-ramp loop only steps ARM[0]) -- category
  B: a real magnitude applied via a real, documented single-axis motion,
  not an invented trajectory.
Required diagrammatic elements: the two rendered robot poses (grasp,
  post-lift) are 3D renders of the anchor-capture geometry, captioned as a
  different real session than trial 9's own metrics. No interpolated frames
  between them.

Run: python fig11_successful_experiment.py [--exp-dir DIR]
Output: generated_assets/fig11/fig11_successful_experiment.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

import figstyle as fs
import fig_data as fd
import scene3d as s3

EXECUTED_CANDIDATE = s3.EXECUTED_CANDIDATE
G1_THRESH_M = 0.03
G2_THRESH_M, G2_THRESH_DEG = 0.02, 15.0
G3_EPS = -0.885

GRASP_RGBA = (0.55, 0.57, 0.62, 1.0)     # dimmed neutral -- pre-lift
LIFT_RGBA = (0.55, 0.80, 0.62, 1.0)      # neutral grey tinted toward ACCEPTED -- post-lift


def render_hero_3d(scene, z_rise_m, width=1500, height=1150):
    client = s3.connect()
    robot_grasp, ji = s3.load_robot(client, rgba=GRASP_RGBA)
    robot_lift, _ = s3.load_robot(client, rgba=LIFT_RGBA)

    joints_grasp = dict(scene.joints_selected)
    joints_lift = dict(scene.joints_selected)
    joints_lift["arm_lift_joint"] = joints_grasp["arm_lift_joint"] + z_rise_m

    s3.pose_robot(client, robot_grasp, ji, scene.base_selected, joints_grasp)
    s3.pose_robot(client, robot_lift, ji, scene.base_selected, joints_lift)

    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    T_world_base = s3.world_base_transform(*scene.base_selected)
    palm_grasp = (T_world_base @ s3.fk(J, seq, joints_grasp))[:3, 3]
    palm_lift = (T_world_base @ s3.fk(J, seq, joints_lift))[:3, 3]

    bx, by = scene.base_selected[0], scene.base_selected[1]
    center = np.array([bx, by, (palm_grasp[2] + palm_lift[2]) / 2.0])
    extent = 1.3

    view, proj, eye = s3.view_and_projection(s3.CAM_SIDE, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    import pybullet as pb
    pb.disconnect(client)

    fig = plt.figure(figsize=(fs.FIG_W_IN * 0.60, fs.FIG_H_IN * 0.82), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    cpx, cpy, cdepth, cvalid = s3.project_points(scene.cloud, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=2.0, color=fs.MUTED, alpha=0.55, zorder=1, linewidths=0)

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    ppx, ppy, pdepth, pvalid = s3.project_points(np.array([palm_grasp, palm_lift]), view, proj, width, height)
    if pvalid.all():
        ax.plot(ppx, ppy, color=fs.ACCEPTED, linewidth=2.0, linestyle=(0, (2, 2)), zorder=5)
        mid = (ppx.mean(), ppy.mean())
        ax.text(mid[0] + 14, mid[1], f"z_rise = {z_rise_m:.4f} m", color=fs.ACCEPTED, fontsize=11,
                weight="bold", family=fs.FONT, va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", facecolor=fs.SLIDE_BG, edgecolor=fs.ACCEPTED, linewidth=0.8))

    return fig


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    scene = s3.build_scene(exp_dir)
    rows = fd.load_trials()
    trial = [r for r in rows if "trial 9," in r["note"]][0]
    out_path = out_path or os.path.join(fs.asset_dir("fig11"), "fig11_successful_experiment.png")

    g1_xy = float(trial["g1_xy"])
    g2_pos_err = float(trial["g2_pos_err"])
    g2_ori_deg = float(trial["g2_ori_deg"])
    hand_motor = float(trial["hand_motor"])
    z_rise_m = float(trial["z_rise_m"])
    g1_pass = g1_xy < G1_THRESH_M
    g2_pass = (g2_pos_err < G2_THRESH_M) and (g2_ori_deg < G2_THRESH_DEG)
    g3_pass = (hand_motor > G3_EPS) and (trial["lift_executed"] == "yes")

    hero_fig = render_hero_3d(scene, z_rise_m)
    hero_path = os.path.join(fs.asset_dir("fig11"), "_hero_tmp.png")
    hero_fig.savefig(hero_path, facecolor=fs.SLIDE_BG)
    plt.close(hero_fig)
    hero_img = mpimg.imread(hero_path)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 11 -- Successful Experiment", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885, f"Trial 9, 2026-08-01: {trial['verdict']}, fully autonomous, "
              f"no hand-placing", **fs.BODY)

    ax = fig.add_axes([0.03, 0.12, 0.60, 0.72])
    ax.imshow(hero_img)
    ax.axis("off")
    ax.set_title("Grasp -> lift, real 3D geometry (anchor capture pose)", **fs.SECTION, fontsize=12)

    ax_info = fig.add_axes([0.66, 0.15, 0.31, 0.68])
    ax_info.add_patch(Rectangle((0, 0), 1, 1, transform=ax_info.transAxes,
                                 facecolor=fs.CALLOUT_BG, edgecolor="none", zorder=0))
    ax_info.axis("off")
    ax_info.set_title("Trial 9 real metrics", **fs.SECTION, loc="left", y=1.0)

    def gate_line(y, label, passed):
        c = fs.ACCEPTED if passed else fs.REJECTED
        ax_info.text(0.06, y, ("\u2713 " if passed else "\u2717 ") + label, transform=ax_info.transAxes,
                     color=c, fontsize=11, weight="bold", family=fs.FONT, va="top")

    gate_line(0.86, f"G1 base-settled (g1_xy={g1_xy:.4f}m)", g1_pass)
    gate_line(0.78, f"G2 palm-vs-FK (pos={g2_pos_err:.4f}m, ori={g2_ori_deg:.2f}deg)", g2_pass)
    gate_line(0.70, f"G3 lift-verify (motor={hand_motor:.4f}, z_rise={z_rise_m:.4f}m)", g3_pass)
    ax_info.text(0.06, 0.58,
                 f"z_rise_m:     {z_rise_m:.4f} m\n"
                 f"hand_motor:   {hand_motor:.4f}\n"
                 f"servo:        46.9 -> 12.7 px\n"
                 f"servo_used:   {trial['servo_used']}\n\n"
                 f"verdict:      {trial['verdict']}",
                 transform=ax_info.transAxes, va="top", ha="left", **fs.BODY)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "Rendered from logged joint values through the HSR URDF (candidate #24, place_run.csv) -- "
              "geometry is the robot description, pose is measured; not a photograph.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Pose/scene geometry is the 2026-08-07 anchor capture (Figures 1-6), not a photograph of "
              "trial 9 itself -- trial 9's own point cloud/joints were not separately saved. Lift = real",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "z_rise_m (0.1420m, trial 9) applied as a pure arm_lift_joint delta (the only joint that "
              "moves during the real lift ramp). All metrics on the right are trial 9's own real values.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    if os.path.exists(hero_path):
        os.remove(hero_path)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig11 written to {path}")
