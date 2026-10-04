"""
fig08_motion_planning.py -- Figure 8: Motion Planning / Collision-Aware Base
Placement (v3 -- 3D canonical-scene rebuild).

Scientific claim: the target is unreachable from the robot's initial base
position, so the planner evaluates candidate base placements under a real
keep-out constraint and selects a collision-safe repositioning (candidate
#24) that brings the target within the robot's real 0.633m reach.

Visual architecture (v3): a dominant CAM_ISO 3D render of the ONE canonical
scene (scene3d.build_scene) -- the real point cloud, real keep-out cells as
low-alpha voxel footprints, and TWO real robot instances (initial base,
dimmed; candidate #24, full colour and green-tinted as "selected") each
inside a translucent 0.633m reach cylinder -- plus a small CAM_TOP inset
carrying the strict, unambiguous distance proof (0.678m outside / 0.412m
inside) that a 3D perspective render cannot make fully unambiguous by
itself. This replaces both the v1 oblique-3D scene and the v2 three-panel
top-down-only composition: the 3D hero view gives robot/scene context and
geometric depth: the top-down inset keeps the strict reachability proof.

FK: see scene3d.py's module docstring for the validated real FK chain
(2.7mm position / exact 1:1 lift-scaling against candidate 24's own real
logged grasp pose) used to pose the "selected" robot's arm. The "initial"
robot's arm is posed at the URDF's own zero position (a real, valid,
in-limits configuration for every arm joint) -- NOT a measured pose, since
no initial-base joint configuration was ever logged; it is dimmed and
captioned as a neutral/stowed convention, never claimed as measured.

Supporting evidence: Experiment_Logs/2026-08-07/place_run.csv (25 real
  base-placement candidates + candidate 24's real joint values, via
  scene3d.build_scene/load_candidate_joints); grasps_out.npz aff_center_3d
  (real target); fused_cloud.npz (real scene, real keep-out cells, same
  documented formula as v1/v2); hsr_description/robots/hsrb4s_pybullet.urdf
  (real robot geometry); DEMO_RUNBOOK.md/CODEBASE_GUIDE.md (documented
  0/25->25/25 capability, kept in a small isolated footer).
Required diagrammatic elements: reach cylinders and keep-out voxel tops are
  schematic wireframe/translucent overlays (derived from the real REACH_M/
  BASE_CLEAR_M constants and real cell coordinates -- category B, not
  invented geometry). The initial robot's arm pose is the documented
  zero-position convention described above, not a measurement.

Run: python fig08_motion_planning.py [--exp-dir DIR]
Output: generated_assets/fig08/fig08_motion_planning.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

import figstyle as fs
import fig_data as fd
import scene3d as s3

BASE_CLEAR_M = s3.BASE_CLEAR_M
REACH_M = s3.REACH_M
EXECUTED_CANDIDATE = s3.EXECUTED_CANDIDATE
real_keepout_cells = s3.real_keepout_cells  # canonical home is scene3d.py (v3)
STOWED_JOINTS = {name: 0.0 for name in s3.ARM}  # real URDF zero position; documented, not measured

INITIAL_RGBA = (0.42, 0.43, 0.47, 1.0)   # dimmed neutral
SELECTED_RGBA = (0.55, 0.80, 0.62, 1.0)  # neutral grey tinted toward ACCEPTED green


def _cylinder_rings(center_xy, radius, z_levels, n=64):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rings = [np.column_stack([center_xy[0] + radius * np.cos(t), center_xy[1] + radius * np.sin(t),
                               np.full(n, z)]) for z in z_levels]
    return rings


def _draw_projected_ring(ax, ring_xyz, view, proj, w, h, color, alpha, linewidth=1.1):
    px, py, depth, valid = s3.project_points(ring_xyz, view, proj, w, h)
    if valid.all():
        px = np.append(px, px[0])
        py = np.append(py, py[0])
        ax.plot(px, py, color=color, alpha=alpha, linewidth=linewidth, zorder=1)


def _draw_keepout_voxels(ax, keepout_xy, z_top, view, proj, w, h, cell=s3.KEEPOUT_VOX):
    for x, y in keepout_xy:
        corners = np.array([
            [x - cell / 2, y - cell / 2, z_top], [x + cell / 2, y - cell / 2, z_top],
            [x + cell / 2, y + cell / 2, z_top], [x - cell / 2, y + cell / 2, z_top],
        ])
        px, py, depth, valid = s3.project_points(corners, view, proj, w, h)
        if valid.all():
            ax.add_patch(Polygon(np.column_stack([px, py]), closed=True, facecolor=fs.FAINT,
                                  edgecolor="none", alpha=0.22, zorder=1))


def render_hero_3d(scene, width=1700, height=1150):
    client = s3.connect()
    robot_initial, ji = s3.load_robot(client, rgba=INITIAL_RGBA)
    robot_selected, _ = s3.load_robot(client, rgba=SELECTED_RGBA)
    s3.pose_robot(client, robot_initial, ji, scene.base_initial, STOWED_JOINTS)
    s3.pose_robot(client, robot_selected, ji, scene.base_selected, scene.joints_selected)

    bx, by = scene.base_initial[0], scene.base_initial[1]
    sx, sy = scene.base_selected[0], scene.base_selected[1]
    center = np.array([(bx + sx) / 2, (by + sy) / 2, 0.55])
    span = float(np.hypot(sx - bx, sy - by))
    extent = max(2.0 * REACH_M + span, 2.6)

    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    import pybullet as pb
    pb.disconnect(client)

    fig = plt.figure(figsize=(fs.FIG_W_IN * 0.72, fs.FIG_H_IN * 0.80), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    z_levels = [0.0, 0.4, 0.8, 1.2]
    for cxy, color, alpha in [((bx, by), fs.MUTED, 0.35), ((sx, sy), fs.ACCEPTED, 0.55)]:
        for ring in _cylinder_rings(cxy, REACH_M, z_levels):
            _draw_projected_ring(ax, ring, view, proj, width, height, color, alpha)

    _draw_keepout_voxels(ax, scene.keepout_xy, 0.65, view, proj, width, height)

    cpx, cpy, cdepth, cvalid = s3.project_points(scene.cloud, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=1.6, color=fs.MUTED, alpha=0.55, zorder=1.4, linewidths=0)

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    tx, ty, tdepth, tvalid = s3.project_points(scene.target[None, :], view, proj, width, height)
    if tvalid[0]:
        ax.scatter([tx[0]], [ty[0]], s=140, color=fs.INK, marker="+", linewidths=2.6, zorder=5)

    floor_pts = np.array([[bx, by, 0.02], [sx, sy, 0.02]])
    fpx, fpy, fdepth, fvalid = s3.project_points(floor_pts, view, proj, width, height)
    if fvalid.all():
        ax.plot(fpx, fpy, color=fs.ACCEPTED, linewidth=2.2, linestyle=(0, (1, 1.5)), zorder=1.6)

    return fig


def render_topdown_inset(fig, rect, target_xy, sel_xy, d_origin, d_selected):
    ax = fig.add_axes(rect)
    ax.set_aspect("equal")
    ax.set_facecolor(fs.CALLOUT_BG)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    origin = np.zeros(2)
    ax.add_patch(Circle(origin, REACH_M, fill=False, edgecolor=fs.MUTED, linewidth=1.3, linestyle=(0, (4, 3))))
    ax.add_patch(Circle(sel_xy, REACH_M, fill=False, edgecolor=fs.ACCEPTED, linewidth=1.3, linestyle=(0, (4, 3))))
    ax.scatter(*origin, s=26, color=fs.MUTED, marker="s", zorder=4)
    ax.scatter(*sel_xy, s=26, color=fs.ACCEPTED, marker="s", zorder=4)
    ax.scatter(*target_xy, s=55, color=fs.INK, marker="x", linewidths=2.0, zorder=5)
    ax.annotate("", xy=target_xy, xytext=origin,
                arrowprops=dict(arrowstyle="<->", color=fs.REJECTED, linewidth=1.0, shrinkA=0, shrinkB=0))
    ax.text(target_xy[0] * 0.5, target_xy[1] * 0.5 - 0.05, f"{d_origin:.3f} m", ha="center", va="top",
            color=fs.REJECTED, fontsize=7.5, weight="bold", family=fs.FONT,
            bbox=dict(boxstyle="round,pad=0.1", facecolor=fs.CALLOUT_BG, edgecolor="none"))
    mid2 = (sel_xy + target_xy) / 2
    ax.text(mid2[0], mid2[1] - 0.05, f"{d_selected:.3f} m", ha="center", va="top",
            color=fs.ACCEPTED, fontsize=7.5, weight="bold", family=fs.FONT,
            bbox=dict(boxstyle="round,pad=0.1", facecolor=fs.CALLOUT_BG, edgecolor="none"))
    W = REACH_M * 1.3
    lo = min(origin[0], sel_xy[0], target_xy[0]) - 0.05
    hi = max(origin[0], sel_xy[0], target_xy[0]) + 0.05
    span = max(hi - lo, 2 * W)
    cx = (lo + hi) / 2
    ax.set_xlim(cx - span / 2 - 0.1, cx + span / 2 + 0.1)
    ax.set_ylim(-span / 2 - 0.1, span / 2 + 0.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Top-down distance proof", color=fs.MUTED, fontsize=9, family=fs.FONT, pad=4)


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    scene = s3.build_scene(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig08"), "fig08_motion_planning.png")

    target_xy = scene.target[:2]
    sel_xy = np.array(scene.base_selected[:2])
    d_origin = float(np.linalg.norm(target_xy))
    d_selected = float(np.linalg.norm(target_xy - sel_xy))

    hero_fig = render_hero_3d(scene)
    hero_path = os.path.join(fs.asset_dir("fig08"), "_hero_tmp.png")
    hero_fig.savefig(hero_path, facecolor=fs.SLIDE_BG)
    plt.close(hero_fig)
    import matplotlib.image as mpimg
    hero_img = mpimg.imread(hero_path)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 8 -- Collision-Aware Base Placement", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              f"Unreachable from the initial base ({d_origin:.3f} m > {REACH_M} m reach) -> collision-aware "
              f"repositioning to candidate #24 brings the target within reach ({d_selected:.3f} m)", **fs.BODY)

    ax_hero = fig.add_axes([0.03, 0.13, 0.68, 0.70])
    ax_hero.imshow(hero_img)
    ax_hero.axis("off")

    render_topdown_inset(fig, [0.735, 0.44, 0.235, 0.39], target_xy, sel_xy, d_origin, d_selected)

    ax_legend = fig.add_axes([0.735, 0.13, 0.235, 0.27])
    ax_legend.axis("off")
    ax_legend.add_patch(Rectangle((0, 0), 1, 1, transform=ax_legend.transAxes,
                                   fill=False, edgecolor=fs.FAINT, linewidth=1.0))
    legend_lines = [
        ("Grey robot + cylinder", "initial base (stowed arm, not measured)", fs.MUTED),
        ("Green robot + cylinder", "candidate #24 (real logged joints)", fs.ACCEPTED),
        ("Dotted green line", "real base repositioning", fs.ACCEPTED),
        ("Faint squares", f"real keep-out cells (clear={BASE_CLEAR_M} m)", fs.FAINT),
        ("White +", "real target (aff_center_3d)", fs.INK),
    ]
    for i, (k, v, c) in enumerate(legend_lines):
        y = 0.90 - i * 0.19
        ax_legend.text(0.06, y, k, transform=ax_legend.transAxes, color=c, fontsize=8.6,
                        weight="bold", family=fs.FONT, va="top")
        ax_legend.text(0.06, y - 0.075, v, transform=ax_legend.transAxes, color=fs.MUTED, fontsize=7.8,
                        family=fs.FONT, va="top")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              f"Real values: reach={REACH_M} m, BASE_CLEAR={BASE_CLEAR_M} m, 25/25 real candidates, "
              f"candidate #24 selected. FK-posed from candidate 24's real logged joints (place_run.csv),",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "validated to 2.7mm against the real logged grasp pose (test_scene3d.py). Initial robot's arm "
              "is the URDF zero-position convention, not a measured pose -- dimmed and captioned as such.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Documented system-level capability (not this trial's own before/after): arm-only reachable "
              "after base placement, 0/25 -> 25/25 (DEMO_RUNBOOK.md).",
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
    print(f"fig08 written to {path}")
