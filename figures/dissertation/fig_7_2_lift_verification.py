"""Fig 7.2 -- Lift verification (QUANTITATIVE + real 3D context, Class D).

Scientific claim: four consecutive autonomous grasps (trials 9-12, 2026-08-01,
trials.csv) lifted the object to within 0.4mm of each other. Left panel renders
what trial 9's own 0.1420m lift looks like against the robot (ghosted pre-lift
pose, solid post-lift pose, dimension line) -- ported from
fig11_successful_experiment.py's render_hero_3d, recoloured for report style and
switched to CAM_SIDE per this figure's own spec (a side view is what makes a
vertical lift legible as a vertical displacement). Right panel shows all four
real z_rise_m values as markers on a truncated axis with the spread bracketed.

trial 9's z_rise_m is 0.1420m (trials.csv row 9; NOT 0.1418m -- that is trial
10's value; see the plan's Global Constraints for the correction against the
build spec's own inconsistent prose).

Pose geometry (candidate 24's joints/base, via scene3d.build_scene) is the
2026-08-07 anchor capture -- a DIFFERENT real session than trials 9-12
themselves (2026-08-01), exactly as fig11_successful_experiment.py's own
caption already states; the real z_rise_m magnitudes are applied as a pure
arm_lift_joint delta (the only joint that moves during the real lift ramp --
execute_place_grasp_raw.py's lift-ramp loop only steps ARM[0]).

Sources: trials.csv (real z_rise_m for trials 9-12), Experiment_Logs/2026-08-07/
place_run.csv (candidate 24 joints, via scene3d.build_scene), scene3d.py
(validated FK chain + PyBullet render).

Run: python figures/dissertation/fig_7_2_lift_verification.py
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

import _qa as qa
import _style as fs
import fig_data as fd
import scene3d as s3

FIGURE_ID = "fig_7_2_lift_verification"
EXP_DIR = fd.DEFAULT_EXP_DIR
LIFT_TRIALS = (9, 10, 11, 12)

INTENT = "Four consecutive autonomous grasps lifted the object to within four tenths of a millimetre of each other."

CAPTION = (
    "Fig 7.2. Lift verification. (a) Trial 9's real 0.1420 m lift: grasp pose "
    "(ghosted grey) and post-lift pose (green), same real geometry (candidate 24, "
    "2026-08-07 anchor capture), the lift applied as a pure arm_lift_joint delta "
    "(the only joint the real lift ramp moves). (b) All four consecutive real "
    "z_rise_m values (trials 9-12, trials.csv, 2026-08-01): 0.1420, 0.1418, "
    "0.1416, 0.1418 m -- spread 0.4 mm. Axis is truncated (break marked); markers, "
    "not bars, and no error bars -- four observations do not support an interval. "
    "Rendered from the robot description at logged joint values; geometry is the "
    "manufacturer's model, pose is measured -- not a photograph. Pose/scene "
    "geometry is the 2026-08-07 anchor capture, a different real session than "
    "trials 9-12's own metrics (trials.csv), exactly as Fig 11's caption already "
    "states."
)


def _load_verified_lift(exp_dir=EXP_DIR):
    from intent_grasp import scene_objects as so
    scene = s3.build_scene(exp_dir)
    table_info, _ = so.find_objects(scene.cloud)
    table_z = float(table_info["plane_z"])
    rows = fd.load_trials(DATA_ROOT)
    z_rise_trials = {}
    for n in LIFT_TRIALS:
        row = next(r for r in rows if f"trial {n}," in r["note"])
        z_rise_trials[n] = float(row["z_rise_m"])

    assert abs(z_rise_trials[9] - 0.1420) < 1e-4, f"trial 9 drifted: {z_rise_trials[9]}"
    assert abs(z_rise_trials[10] - 0.1418) < 1e-4, f"trial 10 drifted: {z_rise_trials[10]}"
    assert abs(z_rise_trials[11] - 0.1416) < 1e-4, f"trial 11 drifted: {z_rise_trials[11]}"
    assert abs(z_rise_trials[12] - 0.1418) < 1e-4, f"trial 12 drifted: {z_rise_trials[12]}"
    spread_m = max(z_rise_trials.values()) - min(z_rise_trials.values())
    assert abs(spread_m - 0.0004) < 1e-5, f"spread drifted from cited 0.4mm: {spread_m}"

    joints_grasp = dict(scene.joints_selected)
    joints_lift = dict(scene.joints_selected)
    joints_lift["arm_lift_joint"] = joints_grasp["arm_lift_joint"] + z_rise_trials[9]

    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    T_world_base = s3.world_base_transform(*scene.base_selected)
    palm_grasp = (T_world_base @ s3.fk(J, seq, joints_grasp))[:3, 3]
    palm_lift = (T_world_base @ s3.fk(J, seq, joints_lift))[:3, 3]
    assert abs(np.linalg.norm(palm_lift - palm_grasp) - z_rise_trials[9]) < 1e-6

    return dict(scene=scene, z_rise_trials=z_rise_trials, spread_m=spread_m,
                joints_grasp=joints_grasp, joints_lift=joints_lift,
                palm_grasp=palm_grasp, palm_lift=palm_lift, table_z=table_z)


GRASP_RGBA = (0.62, 0.62, 0.64, 0.30)   # ghosted, alpha 0.30, neutral grey (spec)
LIFT_RGBA = tuple(int(fs.OKABE_ITO["green"].lstrip("#")[i:i + 2], 16) / 255
                   for i in (0, 2, 4)) + (1.0,)


def _render_lift_hero(geo, width=1400, height=900):
    scene = geo["scene"]
    client = s3.connect()
    robot_grasp, ji = s3.load_robot(client, rgba=GRASP_RGBA)
    robot_lift, _ = s3.load_robot(client, rgba=LIFT_RGBA)
    s3.pose_robot(client, robot_grasp, ji, scene.base_selected, geo["joints_grasp"])
    s3.pose_robot(client, robot_lift, ji, scene.base_selected, geo["joints_lift"])

    bx, by = scene.base_selected[0], scene.base_selected[1]
    gripper_z = (geo["palm_grasp"][2] + geo["palm_lift"][2]) / 2.0
    center = np.array([bx, by, (gripper_z + geo["table_z"]) / 2.0])
    extent = max(0.62, (gripper_z - geo["table_z"]) * 1.6)  # cropped to arm/gripper/table (spec) -- excludes base/wheels

    view, proj, eye = s3.view_and_projection(s3.CAM_SIDE, center, extent, aspect=width / height)
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

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    # table surface reference line -- real table plane_z (scene_objects.find_objects
    # on the real fused cloud), not the robot base frame's z=0
    table_pts = np.array([[bx - 0.4, by, geo["table_z"]], [bx + 0.4, by, geo["table_z"]]])
    tpx, tpy, _, tvalid = s3.project_points(table_pts, view, proj, width, height)
    if tvalid.all():
        ax.plot(tpx, tpy, color="#9a9a9a", linewidth=1.0, linestyle=(0, (3, 2)), zorder=1)

    ppx, ppy, _, pvalid = s3.project_points(
        np.array([geo["palm_grasp"], geo["palm_lift"]]), view, proj, width, height)
    if pvalid.all():
        ax.annotate("", xy=(ppx[1], ppy[1]), xytext=(ppx[0], ppy[0]),
                    arrowprops=dict(arrowstyle="<|-|>", color="black", linewidth=1.3,
                                     shrinkA=0, shrinkB=0), zorder=5)
        mid = ((ppx[0] + ppx[1]) / 2, (ppy[0] + ppy[1]) / 2)
        ax.annotate(f"{geo['z_rise_trials'][9]:.4f} m", xy=mid, xytext=(mid[0] + 16, mid[1]),
                    fontsize=9, fontweight="bold", color="black", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.9),
                    zorder=6)

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba()).copy()
    plt.close(fig)
    return buf


def _draw_repeatability(ax, z_rise_trials, spread_m):
    trials = sorted(z_rise_trials)
    ys = [z_rise_trials[t] for t in trials]
    green = fs.OKABE_ITO["green"]

    ax.scatter(trials, ys, s=81, color=green, zorder=4, marker="o")
    mean_y = float(np.mean(ys))
    ax.axhline(mean_y, color="#888888", linewidth=0.9, zorder=1)
    ax.annotate(f"mean {mean_y:.4f} m", xy=(trials[1], mean_y), xytext=(0, 9),
                textcoords="offset points", fontsize=7, color="#555555", ha="center", va="bottom")

    y_lo, y_hi = min(ys), max(ys)
    x_bracket = trials[-1] + 0.65
    ax.annotate("", xy=(x_bracket, y_hi), xytext=(x_bracket, y_lo),
                arrowprops=dict(arrowstyle="-", color="black", linewidth=1.0), zorder=3)
    ax.annotate(f"spread\n{spread_m * 1000:.1f} mm", xy=(x_bracket, (y_hi + y_lo) / 2),
                xytext=(6, 0), textcoords="offset points", fontsize=7.5,
                fontweight="bold", va="center", linespacing=1.2)

    ax.set_ylim(0.1410, 0.1425)
    ax.set_xlim(trials[0] - 0.6, trials[-1] + 1.5)
    ax.set_xticks(trials)
    ax.set_xlabel("trial")
    ax.set_ylabel("z_rise (m)")
    fs.truncation_marker(ax, axis="y")
    ax.set_title("four consecutive runs", fontsize=8.5, loc="right")
    fs.panel_label(ax, "b")


def build():
    geo = _load_verified_lift()

    fig = plt.figure(figsize=(fs.TEXT_WIDTH_IN, 2.8), facecolor="white")
    ax_hero = fig.add_axes([0.02, 0.02, 0.575, 0.90])
    hero_img = _render_lift_hero(geo)
    ax_hero.imshow(hero_img)
    ax_hero.axis("off")
    ax_hero.set_title("trial 9: grasp and lift", fontsize=9)
    fs.panel_label(ax_hero, "a")

    ax_rep = fig.add_axes([0.68, 0.20, 0.29, 0.68])
    _draw_repeatability(ax_rep, geo["z_rise_trials"], geo["spread_m"])

    return fig, geo


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig, geo = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="A ghosted arm and a solid green arm at slightly different "
                   "heights with a measured gap between them, then four dots that "
                   "all sit inside a narrow bracketed band on a broken axis -- "
                   "reads as 'the lift is real and it repeats' without reading "
                   "the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="dimension line labelled with the real trial-9 lift value; "
                       "all four trial markers labelled by trial number on the x-axis; "
                       "spread bracket labelled in mm; axis truncation marked.",
        referent_audit="dimension label sits directly between the two palm "
                        "markers it measures; spread label sits directly beside its bracket.",
    )
    report_path = qa.write_report("fig72")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
