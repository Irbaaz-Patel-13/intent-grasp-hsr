"""Fig 3.7 -- Base placement (QUANTITATIVE + real 3D context, Class D).

Scientific claim: a grasp target that lies outside the robot's documented planar
reach from the initial base pose is brought inside that reach by translating the
base to candidate #24's real, IK-verified placement. Both base poses, the shared
target, and the reach constant are the same real values `fig08_motion_planning.py`
(slide-deck figure) already established and this session's evidence audit verified
against `test_scene3d.py`/`test_fig08_motion_planning.py` (both `ALL PASS`,
recomputed independently: d_origin=0.678 m, d_selected=0.412 m, FK error=2.7 mm).

REACH_M=0.633 m is a DOCUMENTED reach constant (`hsr_base_placement.py`'s own
descriptive literal, reused here via `scene3d.REACH_M`) -- not a measured maximum,
not IK-derived, not enforced inside the real placement search (which instead does a
free-base IK solve per candidate). Always labelled "documented reach, r = 0.633 m",
never "maximum"/"kinematic"/"measured" reach, never "annulus" (it is a single outer
radial bound, no inner radius exists anywhere in this codebase).

The "0/25 -> 25/25" before/after capability is a general DEMO_RUNBOOK.md claim, NOT
this trial's own measured before-state (figures/BLOCKERS.md item 3, independently
confirmed this session) -- this figure only shows this trial's real after-state
(25/25) plus the geometric unreachable-at-origin argument; it does not draw or imply
0/25 anywhere.

Sources: Experiment_Logs/2026-08-07/place_run.csv (25 real base-placement
candidates), grasps_out.npz/grasps_plain.npz (real target), fused_cloud.npz (real
scene + real keep-out cells), scene3d.py (validated FK chain + PyBullet render,
2.7 mm), scripts/robot/hsr_base_placement.py (BASE_CLEAR=0.32,
REACH_M=0.633 literal, real algorithm), workstation_history.txt (candidate 24
actually driven/armed/servoed/grasped on hardware).

Run: python figures/dissertation/fig_3_7_base_placement.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from intent_grasp.paths import REPO_ROOT  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon

import _qa as qa
import _style as fs
import fig_data as fd
import scene3d as s3

FIGURE_ID = "fig_3_7_base_placement"
EXP_DIR = fd.DEFAULT_EXP_DIR

INTENT = ("The affordance target lies outside the robot's documented planar reach "
          "from the initial base pose; translating the base to candidate 24's real, "
          "IK-verified placement brings the same target inside that reach.")

CAPTION = (
    "Fig 3.7. Base placement. (a) Real captured scene (point cloud, robot geometry, "
    "keep-out cells) at the initial base pose (dimmed) and candidate 24's real "
    "placement (accent colour). (b)-(c) Top-down planar-reach proof, drawn from the "
    "same target and base coordinates as (a): the target sits outside the documented "
    "reach circle (r = 0.633 m) from the initial base (d = 0.678 m) and inside it "
    "after the base translates to candidate 24 (d = 0.412 m). Candidate 24 was "
    "selected by the real collision-aware placement search (max manipulability of "
    "all 25 real candidates, base keep-out clearance 0.358 m against a 0.32 m limit) "
    "and was the candidate actually driven, armed, visual-servoed and grasped on the "
    "physical HSR (Experiment_Logs/2026-08-07). REACH_M=0.633 m is a documented "
    "planar reach constant (hsr_base_placement.py), not a measured kinematic "
    "maximum and not itself enforced inside the placement search."
)


def _load_verified_geometry(exp_dir=EXP_DIR):
    scene = s3.build_scene(exp_dir)
    gc = fd.load_grasp_candidates(exp_dir)
    cand = s3.EXECUTED_CANDIDATE

    target_xy = scene.target[:2].copy()
    base_initial_xy = np.array(scene.base_initial[:2], dtype=float)
    base_selected_xy = np.array(scene.base_selected[:2], dtype=float)

    d_origin = float(np.linalg.norm(target_xy - base_initial_xy))
    d_selected = float(np.linalg.norm(target_xy - base_selected_xy))
    assert d_origin > s3.REACH_M, f"expected target outside reach at origin, got {d_origin:.4f}"
    assert d_selected < s3.REACH_M, f"expected target inside reach at candidate 24, got {d_selected:.4f}"
    assert abs(d_origin - 0.678) < 0.01, f"d_origin drifted from cited 0.678 m: {d_origin:.4f}"
    assert abs(d_selected - 0.412) < 0.01, f"d_selected drifted from cited 0.412 m: {d_selected:.4f}"

    delta_xy = base_selected_xy - base_initial_xy
    delta_yaw_deg = float(np.degrees(scene.base_selected[2] - scene.base_initial[2]))

    # FK validation error, recomputed live (mirrors test_scene3d.py exactly).
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    q, base, _ = s3.load_candidate_joints(exp_dir, candidate=cand)
    T_world_palm = s3.world_base_transform(*base) @ s3.fk(J, seq, q)
    fk_err_m = float(np.linalg.norm(T_world_palm[:3, 3] - gc.poses[cand, :3, 3]))
    assert fk_err_m < 0.01, f"FK error exceeds 0.01 m tolerance: {fk_err_m:.4f}"

    # Real keep-out clearance, recomputed live against the real formula (never the
    # 0.322/0.334 numbers -- those belong to an unrelated CGN diagnostic, see the
    # evidence report; do not reintroduce them here even as a sanity check).
    cloud_full = fd.load_fused_cloud(exp_dir)
    ko_full = s3.real_keepout_cells(cloud_full)
    base_xy_all = np.column_stack([gc.base_x, gc.base_y])
    table_clear_all = np.array([
        float(np.min(np.linalg.norm(ko_full - b, axis=1))) if len(ko_full) else np.nan
        for b in base_xy_all
    ])
    table_clear_min = float(np.nanmin(table_clear_all))
    table_clear_median = float(np.nanmedian(table_clear_all))
    table_clear_candidate24 = float(table_clear_all[cand])
    assert table_clear_min >= s3.BASE_CLEAR_M - 1e-6, "a candidate violates BASE_CLEAR_M"

    manip24 = float(gc.manip[cand])
    assert manip24 == float(np.nanmax(gc.manip)), "candidate 24 is not max-manipulability"
    arm_only_ok24 = bool(gc.arm_only_ok[cand])
    assert arm_only_ok24

    return dict(
        scene=scene, target_xy=target_xy, base_initial_xy=base_initial_xy,
        base_selected_xy=base_selected_xy, d_origin=d_origin, d_selected=d_selected,
        delta_xy=delta_xy, delta_yaw_deg=delta_yaw_deg, fk_err_m=fk_err_m,
        table_clear_min=table_clear_min, table_clear_median=table_clear_median,
        table_clear_candidate24=table_clear_candidate24, manip24=manip24,
        arm_only_ok24=arm_only_ok24, keepout_xy_full=ko_full,
    )


# ---------------------------------------------------------------------------
# 3D hero panel -- ported from fig08_motion_planning.py's projection helpers,
# recoloured for report style (white background, Okabe-Ito palette).
# ---------------------------------------------------------------------------

STOWED_JOINTS = {name: 0.0 for name in s3.ARM}

INITIAL_RGBA = (0.62, 0.62, 0.64, 1.0)   # quiet neutral grey -- Level 3 emphasis


def _hex_to_rgba(hexcolour, alpha=1.0):
    r, g, b = (int(hexcolour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (r, g, b, alpha)


SELECTED_RGBA = _hex_to_rgba(fs.OKABE_ITO["green"])


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


def _draw_keepout_voxels(ax, keepout_xy, z_top, view, proj, w, h, color, cell=s3.KEEPOUT_VOX):
    for x, y in keepout_xy:
        corners = np.array([
            [x - cell / 2, y - cell / 2, z_top], [x + cell / 2, y - cell / 2, z_top],
            [x + cell / 2, y + cell / 2, z_top], [x - cell / 2, y + cell / 2, z_top],
        ])
        px, py, depth, valid = s3.project_points(corners, view, proj, w, h)
        if valid.all():
            ax.add_patch(Polygon(np.column_stack([px, py]), closed=True, facecolor=color,
                                  edgecolor="none", alpha=0.25, zorder=1))


def _render_hero_3d(geo, width=1400, height=1050):
    scene = geo["scene"]
    client = s3.connect()
    robot_initial, ji = s3.load_robot(client, rgba=INITIAL_RGBA)
    robot_selected, _ = s3.load_robot(client, rgba=SELECTED_RGBA)
    s3.pose_robot(client, robot_initial, ji, scene.base_initial, STOWED_JOINTS)
    s3.pose_robot(client, robot_selected, ji, scene.base_selected, scene.joints_selected)

    bx, by = scene.base_initial[0], scene.base_initial[1]
    sx, sy = scene.base_selected[0], scene.base_selected[1]
    center = np.array([(bx + sx) / 2, (by + sy) / 2, 0.55])
    span = float(np.hypot(sx - bx, sy - by))
    extent = max(2.0 * s3.REACH_M + span, 2.6)

    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    import pybullet as pb
    pb.disconnect(client)

    fig = plt.figure(figsize=(width / 300, height / 300), dpi=300, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    z_levels = [0.0, 0.4, 0.8, 1.2]
    muted = "#9a9a9a"
    for cxy, color, alpha in [((bx, by), muted, 0.30), ((sx, sy), fs.OKABE_ITO["green"], 0.45)]:
        for ring in _cylinder_rings(cxy, s3.REACH_M, z_levels):
            _draw_projected_ring(ax, ring, view, proj, width, height, color, alpha)

    _draw_keepout_voxels(ax, scene.keepout_xy, 0.65, view, proj, width, height, color="#c9c9c9")

    cpx, cpy, cdepth, cvalid = s3.project_points(scene.cloud, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=1.1, color="#b5b5b5", alpha=0.5, zorder=1.4, linewidths=0)

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    tx, ty, tdepth, tvalid = s3.project_points(scene.target[None, :], view, proj, width, height)
    if tvalid[0]:
        ax.scatter([tx[0]], [ty[0]], s=100, color=fs.OKABE_ITO["vermillion"], marker="+",
                   linewidths=2.2, zorder=5)

    floor_pts = np.array([[bx, by, 0.02], [sx, sy, 0.02]])
    fpx, fpy, fdepth, fvalid = s3.project_points(floor_pts, view, proj, width, height)
    if fvalid.all():
        ax.plot(fpx, fpy, color=fs.OKABE_ITO["green"], linewidth=1.8,
                linestyle=(0, (1, 1.5)), zorder=1.6)

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba()).copy()
    plt.close(fig)
    return buf


# ---------------------------------------------------------------------------
# 2D panels
# ---------------------------------------------------------------------------

def _draw_2d_panel(ax, letter, base_xy, target_xy, reach_m, is_selected, dist_label_val, base_label):
    accent = fs.OKABE_ITO["green"] if is_selected else "#9a9a9a"
    target_c = fs.OKABE_ITO["vermillion"]

    ax.add_patch(Circle(base_xy, reach_m, fill=False, edgecolor=accent, linewidth=1.4,
                         linestyle=(0, (4, 3)), zorder=2))
    ax.scatter(*base_xy, s=42, color=accent, marker="s", zorder=4, label=base_label)
    ax.scatter(*target_xy, s=70, color=target_c, marker="+", linewidths=2.2, zorder=5,
               label="target")
    ax.annotate("", xy=tuple(target_xy), xytext=tuple(base_xy),
                arrowprops=dict(arrowstyle="-", color="#444444", linewidth=1.0, shrinkA=0, shrinkB=0),
                zorder=3)
    mid = (np.asarray(base_xy) + np.asarray(target_xy)) / 2
    ax.annotate(f"{dist_label_val:.3f} m", xy=tuple(mid), xytext=(mid[0], mid[1] + reach_m * 0.10),
                ha="center", va="bottom", fontsize=8, fontweight="bold", color="#222222",
                bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.85))
    # Anchored straight up from the circle's own top (not out to the side): a
    # sideways placement pushed the text past this axes' own right edge into
    # the neighbouring panel's tick labels (clip_on=False on annotate text).
    # Centred above the circle keeps the label's bbox inside its own panel.
    fs.leader_label(ax, (base_xy[0], base_xy[1] + reach_m),
                     (base_xy[0], base_xy[1] + reach_m * 1.18),
                     "documented reach, r = 0.633 m", colour=accent, fontsize=7, ha="center")

    ax.set_aspect("equal")
    half = reach_m * 1.35
    cx = (base_xy[0] + target_xy[0]) / 2
    cy = (base_xy[1] + target_xy[1]) / 2
    half = max(half, abs(base_xy[0] - target_xy[0]), abs(base_xy[1] - target_xy[1])) + reach_m * 0.15
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_xlabel("x (m)", fontsize=8)
    ax.set_ylabel("y (m)", fontsize=8)
    ax.tick_params(labelsize=7)
    # prune='both': the default locator was emitting one tick just past each
    # axis limit (still a real Text artist, just off the visible plot area) --
    # for these bottom-row panels that off-range y-tick landed underneath the
    # axes, overlapping the x-tick-label row below it.
    ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=6, prune="both"))
    ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=6, prune="both"))
    fs.panel_label(ax, letter)


def _draw_transition(fig, rect, delta_xy, delta_yaw_deg):
    # A thin full-width band in the gap between the hero panel and the two 2D
    # panels, so its glyphs never contend for space inside either panel's own
    # axes box (a narrow vertical strip squeezed between panels (b)/(c) forced
    # text to bleed into their tick labels and leader lines -- moved here).
    ax = fig.add_axes(rect)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fs.orthogonal_arrow(ax, (0.40, 0.55), (0.60, 0.55), colour="#222222")
    ax.text(0.5, 0.95, "base translation", ha="center", va="top", fontsize=7.5,
            fontweight="bold", color="#222222")
    ax.text(0.5, 0.15, f"\u0394x = {delta_xy[0]:+.3f} m   \u0394y = {delta_xy[1]:+.3f} m   "
                        f"\u0394yaw = {delta_yaw_deg:+.1f}\u00b0",
            ha="center", va="bottom", fontsize=7.2, color="#444444")


def build():
    geo = _load_verified_geometry()

    fig = plt.figure(figsize=(fs.TEXT_WIDTH_IN, 7.4), facecolor="white")

    ax_hero = fig.add_axes([0.03, 0.52, 0.94, 0.44])
    hero_img = _render_hero_3d(geo)
    ax_hero.imshow(hero_img)
    ax_hero.axis("off")
    fs.panel_label(ax_hero, "a")

    ax_b = fig.add_axes([0.09, 0.09, 0.38, 0.36])
    _draw_2d_panel(ax_b, "b", geo["base_initial_xy"], geo["target_xy"], s3.REACH_M,
                   is_selected=False, dist_label_val=geo["d_origin"], base_label="initial base")

    _draw_transition(fig, [0.09, 0.465, 0.86, 0.045], geo["delta_xy"], geo["delta_yaw_deg"])

    ax_c = fig.add_axes([0.57, 0.09, 0.38, 0.36])
    _draw_2d_panel(ax_c, "c", geo["base_selected_xy"], geo["target_xy"], s3.REACH_M,
                   is_selected=True, dist_label_val=geo["d_selected"], base_label="candidate 24")

    # Level 3 validation callout -- compact, quiet, in the hero panel's empty corner.
    ax_hero.text(0.015, 0.03,
                 f"candidate 24: manip {geo['manip24']:.3f} (max of 25), arm_only_ok=1, "
                 f"FK error {geo['fk_err_m']*1000:.1f} mm, executed on hardware",
                 transform=ax_hero.transAxes, fontsize=7.0, color="#666666", va="bottom", ha="left")

    return fig, geo


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig, geo = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("fig37")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
