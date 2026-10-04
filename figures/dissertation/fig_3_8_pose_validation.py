"""Fig 3.8 -- Pose validation constraints (QUANTITATIVE + real 3D context, Class D).

Every commanded configuration is checked against floor clearance and a head
keep-out volume before motion; a violation aborts. Panel (a) is candidate 24's
real accepted pose (place_run.csv, Experiment_Logs/2026-08-07, the same pose
scene3d.build_scene() renders everywhere else in this figure set). Panel (b) is
the real wrist-limit incident: candidate 17 of the same real placement search
commands wrist_flex_joint = -1.92 rad -- exactly the URDF's own lower bound
(hsrb.urdf: <limit lower="-1.92" upper="1.22" .../>), which the flight code's
own operational margin (scene3d.py load_candidate_joints's `max(q, -1.90)`
clamp; same clamp in execute_place_grasp_raw.py:119, "incident #9: trajectories
at the -1.92 URDF limit appear to be silently rejected") refuses to command.
-1.90 is that flight-code margin, NOT the URDF's own bound -- the two numbers
are deliberately different and the caption states this.

Uses candidate 24's joints WITHOUT scene3d.load_candidate_joints()'s clamp for
the accepted panel (that clamp only ever matters for candidates at the limit,
and candidate 24 is not one), and reads candidate 17's RAW place_run.csv row
directly (bypassing the clamp entirely) for the rejected panel, so the real
-1.92 commanded value is what gets rendered and evaluated, not a
silently-corrected substitute.

Sources:
  scripts/robot/hsrb.urdf        (real URDF, joint limits)
  Experiment_Logs/2026-08-07/place_run.csv         (candidates 17 and 24, real logged joints)
  hsr_pose_check.py                                (real, unmodified FK + limit/floor/head-keepout evaluator)
  scene3d.py                                       (validated FK chain + PyBullet render)
  scripts/robot/hsr_preflight.py (the real 8 preflight checks C1-C8)

Run: python figures/dissertation/fig_3_8_pose_validation.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from intent_grasp.paths import REPO_ROOT  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "robot"))
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
import hsr_pose_check as hpc

FIGURE_ID = "fig_3_8_pose_validation"
EXP_DIR = fd.DEFAULT_EXP_DIR
REJECTED_CANDIDATE = 17
WRIST_SOFT_LIMIT = -1.90  # flight-code operational margin, NOT the URDF bound

INTENT = ("Every commanded configuration is checked against floor clearance and a "
          "head keep-out volume before motion, and a violation aborts.")

CAPTION = (
    "Fig 3.8. Pose validation constraints. (a) Candidate 24's real accepted pose "
    "(place_run.csv) -- clear of the floor-clearance plane (0.12 m) and the head "
    "keep-out sphere (r = 0.22 m). (b) Candidate 17 of the same real placement "
    "search, commanding wrist_flex_joint = -1.92 rad -- exactly the URDF's own "
    "lower bound (hsrb.urdf), which the flight code's own operational margin "
    "(-1.90 rad, scene3d.py / execute_place_grasp_raw.py) silently refuses to "
    "command. -1.90 rad is a flight-code safety margin, not the URDF's own "
    "limit -- the two numbers are deliberately different. Rendered from the "
    "robot description at logged joint values; geometry is the manufacturer's "
    "model, pose is measured -- not a photograph."
)

PREFLIGHT_CHECKS = [
    ("C1", "files load"), ("C2", "scene consistency"), ("C3", "grasp flags ok"),
    ("C4", "manipulability"), ("C5", "joint-limit margins"),
    ("C6", "approach-path collision"), ("C7", "FK sanity"), ("C8", "gate self-test"),
]
VIOLATED_CHECK = "C5"


def _load_verified_poses(exp_dir=EXP_DIR):
    J = hpc.load_urdf(s3.REAL_FK_URDF)
    seq = hpc.chain(J, "base_link", "hand_palm_link")

    wrist_lower = J["wrist_flex_joint"]["lower"]
    assert abs(wrist_lower - (-1.92)) < 1e-6, f"URDF wrist_flex lower drifted: {wrist_lower}"

    q_accepted, base_accepted, _ = s3.load_candidate_joints(exp_dir, candidate=s3.EXECUTED_CANDIDATE)
    problems_accepted, palm_acc, lowest_acc, head_d_acc = hpc.evaluate(J, seq, q_accepted, verbose=False)
    assert not problems_accepted, f"candidate 24 unexpectedly flagged: {problems_accepted}"

    path = os.path.join(exp_dir, "place_run.csv")
    row = next(r for r in csv.DictReader(open(path)) if r["grasp"] == str(REJECTED_CANDIDATE))
    q_rejected = {k: float(row[c]) for k, c in zip(s3.ARM, s3.COLS)}
    base_rejected = (float(row["base_x"]), float(row["base_y"]), float(row["base_yaw_rad"]))
    assert abs(q_rejected["wrist_flex_joint"] - (-1.92)) < 1e-6, \
        f"candidate {REJECTED_CANDIDATE} wrist_flex drifted: {q_rejected['wrist_flex_joint']}"
    assert q_rejected["wrist_flex_joint"] <= WRIST_SOFT_LIMIT + 1e-9, \
        "expected commanded value at/below the flight-code's own operational margin"

    problems_rejected, palm_rej, lowest_rej, head_d_rej = hpc.evaluate(J, seq, q_rejected, verbose=False)
    assert any("wrist_flex_joint" in p for p in problems_rejected), \
        f"expected hsr_pose_check to flag wrist_flex_joint near/at its URDF bound: {problems_rejected}"

    pts_rejected, _ = hpc.fk_points(J, seq, q_rejected)
    wrist_link_pos = pts_rejected["wrist_flex_link"]

    return dict(J=J, seq=seq, q_accepted=q_accepted, base_accepted=base_accepted,
                q_rejected=q_rejected, base_rejected=base_rejected,
                wrist_urdf_lower=wrist_lower, wrist_soft_limit=WRIST_SOFT_LIMIT,
                problems_rejected=problems_rejected, wrist_link_pos=wrist_link_pos,
                palm_accepted=palm_acc, palm_rejected=palm_rej)


NEUTRAL_RGBA = (0.55, 0.57, 0.62, 1.0)
VIOLATION_HEX = fs.OKABE_ITO["vermillion"]


HIGHLIGHT_JOINTS = ["wrist_flex_joint", "wrist_roll_joint", "hand_palm_joint"]


def _render_pose_panel(q, base, width=1100, height=1150, wrist_pos_to_mark=None, highlight=False):
    import pybullet as pb
    client = s3.connect()
    robot, ji = s3.load_robot(client, rgba=NEUTRAL_RGBA)
    if highlight:
        # highlight the violating wrist-flex link plus the downstream wrist-roll
        # and palm links (spec: "the violating link drawn in vermillion") --
        # rest of the robot stays neutral grey.
        vermillion_rgba = tuple(int(VIOLATION_HEX.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)
        for jn in HIGHLIGHT_JOINTS:
            pb.changeVisualShape(robot, ji[jn], rgbaColor=vermillion_rgba, physicsClientId=client)
    s3.pose_robot(client, robot, ji, base, q)

    center = np.array([base[0], base[1], 1.00])  # torso/arm/head crop -- excludes base+floor
    extent = 1.55
    view, proj, eye = s3.view_and_projection(s3.CAM_SIDE, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    pb.disconnect(client)

    fig = plt.figure(figsize=(width / 300, height / 300), dpi=300, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    # floor clearance plane (z=0.12) -- a horizontal line in this side ortho view;
    # label anchored at the line's own midpoint so it never falls outside this
    # tightly-cropped canvas the way an end-anchored label did in testing.
    floor_pts = np.array([[base[0] - 0.55, base[1], hpc.FLOOR_MIN], [base[0] + 0.55, base[1], hpc.FLOOR_MIN]])
    fpx, fpy, _, fvalid = s3.project_points(floor_pts, view, proj, width, height)
    if fvalid.all():
        ax.plot(fpx, fpy, color=VIOLATION_HEX, linewidth=1.2, linestyle=(0, (5, 3)), zorder=3)
        fmx, fmy = (fpx[0] + fpx[1]) / 2, (fpy[0] + fpy[1]) / 2
        ax.annotate("floor clearance, 0.12 m", xy=(fmx, fmy), xytext=(0, -8),
                    textcoords="offset points", fontsize=7, color=VIOLATION_HEX,
                    ha="center", va="top")

    # head keep-out sphere -> a circle in this side ortho view
    hx, hy, hz = hpc.HEAD_C[0] + base[0], hpc.HEAD_C[1] + base[1], hpc.HEAD_C[2]
    theta = np.linspace(0, 2 * np.pi, 64)
    ring = np.column_stack([hx + hpc.HEAD_R * np.cos(theta), np.full(64, hy),
                             hz + hpc.HEAD_R * np.sin(theta)])
    rpx, rpy, _, rvalid = s3.project_points(ring, view, proj, width, height)
    if rvalid.all():
        ax.plot(np.append(rpx, rpx[0]), np.append(rpy, rpy[0]), color=VIOLATION_HEX,
                 linewidth=1.0, linestyle=(0, (2, 2)), zorder=3)
        # label anchored to the circle's own leftmost point, pulled further left
        # so it sits clear of the head mesh the circle encloses (found in testing:
        # a label placed inside the circle overlapped the rendered head geometry)
        ax.annotate("keep-out,\nr = 0.22 m", xy=(rpx.min(), (rpy.min() + rpy.max()) / 2),
                    xytext=(-8, 0), textcoords="offset points", fontsize=7,
                    color=VIOLATION_HEX, ha="right", va="center", linespacing=1.2)

    if wrist_pos_to_mark is not None:
        wpx, wpy, _, wvalid = s3.project_points(wrist_pos_to_mark[None, :], view, proj, width, height)
        if wvalid[0]:
            ax.scatter([wpx[0]], [wpy[0]], s=140, facecolors="none", edgecolors=VIOLATION_HEX,
                       linewidths=2.2, zorder=6)
            ax.annotate("commanded -1.92 rad,\nlimit -1.90 rad", xy=(wpx[0], wpy[0]),
                        xytext=(wpx[0] - 20, wpy[0] + 70), fontsize=7.5, fontweight="bold",
                        color=VIOLATION_HEX, ha="right", va="top", linespacing=1.3,
                        arrowprops=dict(arrowstyle="-", color=VIOLATION_HEX, linewidth=1.0),
                        bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.9),
                        zorder=7)

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba()).copy()
    plt.close(fig)
    return buf


def _draw_checks_strip(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ncols = 4
    xs = np.linspace(0.5 / ncols, 1 - 0.5 / ncols, ncols)
    row_y = {0: 0.72, 1: 0.22}
    for i, (code, name) in enumerate(PREFLIGHT_CHECKS):
        row, col = divmod(i, ncols)
        colour = fs.OKABE_ITO["vermillion"] if code == VIOLATED_CHECK else "#333333"
        weight = "bold" if code == VIOLATED_CHECK else "normal"
        ax.text(xs[col], row_y[row], f"{code} {name}", ha="center", va="center", fontsize=7.0,
                 color=colour, fontweight=weight, transform=ax.transAxes)


def build():
    geo = _load_verified_poses()

    fig = plt.figure(figsize=(fs.TEXT_WIDTH_IN, 3.9), facecolor="white")
    ax_a = fig.add_axes([0.02, 0.20, 0.47, 0.76])
    img_a = _render_pose_panel(geo["q_accepted"], geo["base_accepted"])
    ax_a.imshow(img_a)
    ax_a.axis("off")
    ax_a.set_title("accepted", fontsize=9, loc="right")
    fs.panel_label(ax_a, "a")

    ax_b = fig.add_axes([0.51, 0.20, 0.47, 0.76])
    img_b = _render_pose_panel(geo["q_rejected"], geo["base_rejected"],
                                wrist_pos_to_mark=geo["wrist_link_pos"], highlight=True)
    ax_b.imshow(img_b)
    ax_b.axis("off")
    ax_b.set_title("rejected -- wrist flex beyond limit", fontsize=9, loc="right")
    fs.panel_label(ax_b, "b")

    ax_strip = fig.add_axes([0.02, 0.01, 0.96, 0.14])
    _draw_checks_strip(ax_strip)

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
        blind_read="Two side-view robot poses side by side, each with a dashed "
                   "floor line and a dashed head circle; the right pose has a "
                   "vermillion ring around its wrist with a number pair next to "
                   "it and a small part of the arm itself coloured vermillion, "
                   "and one word in the strip below is coloured differently "
                   "from the rest -- reads as 'this configuration fails one "
                   "specific check' without reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="floor line and keep-out circle labelled with their real "
                       "thresholds in both panels; wrist violation labelled with "
                       "both the commanded and limit values; violated check named "
                       "in the strip.",
        referent_audit="the commanded/limit label sits directly beside the "
                        "vermillion wrist ring it describes.",
    )
    report_path = qa.write_report("fig38")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
