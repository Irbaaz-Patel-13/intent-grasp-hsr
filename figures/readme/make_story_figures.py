"""Picture-first figures for the README, each drawn from recorded data.

    scenes.png          the head-camera RGB-D scenes the reasoning was tested on
    handle_gate.png     the real mug point cloud split into parts, and why the handle is refused
    motion.png          the HSR's URDF at each commanded stage of one run, onion-skinned
    grips.png           one object, different tasks: the grip parameters drawn to scale

Run from the repository root:

    python figures/readme/make_story_figures.py
"""
import csv
import json
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from intent_grasp import som_part_selection as sps
from intent_grasp.paths import REPO_ROOT, WORKSPACE

sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
sys.path.insert(0, str(REPO_ROOT / "figures" / "readme"))
import fig_data as fd  # noqa: E402
import scene3d as s3  # noqa: E402
from make_readme_figures import (BLUE, BLUE_TINT, HAIRLINE, INK, INK_2, INK_3, ORANGE,  # noqa: E402
                                 PANEL, SURFACE, save, title)

EXP = fd.DEFAULT_EXP_DIR


# --------------------------------------------------------------------------
# 1. Through the robot's eyes
# --------------------------------------------------------------------------
SCENES = [
    ("TV_remote", "remote"), ("coke_can", "coke can"), ("dishwash_bottle", "dish-soap bottle"),
    ("metal_spoon", "spoon"), ("pot_with_handle_and_lid", "pot"), ("cluster_mug_cokecan", "mug + can"),
    ("cluster_mug_cokecan_pot", "mug + can + pot"), ("cluster_mug_remote_pot", "mug + remote + pot"),
]


def fig_scenes():
    rows = list(csv.DictReader(open(WORKSPACE / "vlm_stability.csv", encoding="utf-8")))
    by_scene = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_scene[r["scene"]][r["instruction"]].append(r)

    fig = plt.figure(figsize=(16, 9.4))
    title(fig, "What the robot saw, and what it decided to pick",
          "Real HSR head-camera captures (RGB with the depth image inset). "
          "Below each: the instruction it was given, and its pick across 5 runs.")
    for i, (scene, label) in enumerate(SCENES):
        d = np.load(WORKSPACE / "captures_0723" / f"cap_{scene}.npz", allow_pickle=True)
        col, row = i % 4, i // 4
        ax = fig.add_axes([0.01 + col * 0.248, 0.47 - row * 0.43, 0.235, 0.30])
        ax.imshow(d["rgb"])
        ax.axis("off")
        dep = d["depth"].astype(float)
        dep[dep <= 0] = np.nan
        ins = ax.inset_axes([0.70, 0.66, 0.29, 0.33])
        ins.imshow(dep, cmap="Greys_r", vmin=np.nanpercentile(dep, 2), vmax=np.nanpercentile(dep, 98))
        ins.set_xticks([]); ins.set_yticks([])
        for s in ins.spines.values():
            s.set_color("white"); s.set_linewidth(1.5)
        ax.text(0.01, 1.03, f"scene: {label}", transform=ax.transAxes, fontsize=11,
                fontweight="bold", va="bottom")
        y = -0.03
        for instr, rs in by_scene[scene].items():
            ok = sum(r["correct"] == "1" for r in rs)
            picks = [r["picked"] for r in rs]
            top = max(set(picks), key=picks.count)
            mark, color = ("●", BLUE) if ok == len(rs) else ("✖", ORANGE)
            short = instr if len(instr) <= 40 else instr[:39].rstrip() + "…"
            ax.text(0.0, y, mark, transform=ax.transAxes, fontsize=10, color=color, va="top")
            ax.text(0.05, y, f"“{short}”", transform=ax.transAxes, fontsize=9, va="top")
            wrong = [p for p in picks if p != top] if ok == len(rs) else [r["picked"] for r in rs if r["correct"] != "1"]
            res = f"→ {top}, {ok}/{len(rs)} right" if ok == len(rs) else \
                f"→ {ok}/{len(rs)} right; also picked {max(set(wrong), key=wrong.count)}"
            ax.text(0.05, y - 0.075, res, transform=ax.transAxes, fontsize=8.5, color=INK_2, va="top")
            y -= 0.17
    save(fig, "scenes")


# --------------------------------------------------------------------------
# 2. Why the mug handle is refused
# --------------------------------------------------------------------------
GATE_N, GATE_MM = 60, 6
PART_STYLE = {
    "main_body": ("body", "#9a9893"),
    "top_protrusion": ("rim", BLUE),
    "lateral_protrusion": ("handle piece 1", ORANGE),
    "lateral_protrusion_1": ("handle piece 2", "#b8471f"),
}


def fig_handle_gate():
    cap = WORKSPACE / "captures_pairs_2" / "cap_mug_head_near.npz"
    rgb, comp, desc, K, extr = sps._load_and_isolate(str(cap))

    fig = plt.figure(figsize=(15, 6.4))
    title(fig, "Why the robot refuses to grab this mug by its handle",
          "Real head-camera capture. The point cloud is split into parts; a part needs "
          f"{GATE_N} points and {GATE_MM} mm of width before the robot will trust it.")

    # left: the camera view, cropped around the mug
    allp = np.vstack(list(comp.values()))
    from intent_grasp.part_adaptive import project_points_to_pixels
    u, v, _, valid = project_points_to_pixels(allp, K, extr)
    cx, cy = np.median(u[valid]), np.median(v[valid])
    r = 95
    x0, y0 = int(max(cx - r, 0)), int(max(cy - r * 0.8, 0))
    axl = fig.add_axes([0.01, 0.08, 0.30, 0.68])
    axl.imshow(rgb[y0:int(cy + r * 0.8), x0:int(cx + r)])
    axl.axis("off")
    fig.text(0.01, 0.79, "(a) what the camera sees", fontsize=11)

    # middle: the same mug as parts
    axm = fig.add_axes([0.33, 0.08, 0.34, 0.68])
    center = allp.mean(axis=0)
    extent = float(np.linalg.norm(np.ptp(allp, axis=0))) * 1.6
    cam = dict(kind="perspective", elevation_deg=30.0, azimuth_deg=200.0, fov_deg=35.0)
    view, proj, _ = s3.view_and_projection(cam, center, extent, aspect=1.0)
    W = H = 1000
    xs, ys = [], []
    for name in ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"]:
        if name not in comp:
            continue
        lab, col = PART_STYLE[name]
        px, py, _, ok = s3.project_points(comp[name], view, proj, W, H)
        big = name.startswith("lateral")
        axm.scatter(px[ok], py[ok], s=16 if big else 7, color=col, linewidths=0, zorder=3 if big else 2)
        xs.append(px[ok]); ys.append(py[ok])
        d = desc[name]
        mx, my = np.median(px[ok]), np.median(py[ok])
        txt = f"{lab}\n{d['n']} points, {d['closing_width_mm']} mm wide"
        if d["evidence"] == "NOISE":
            txt += "\nrefused"
        dx = {"main_body": -330, "top_protrusion": 40, "lateral_protrusion": 200,
              "lateral_protrusion_1": -240}[name]
        dy = {"main_body": 230, "top_protrusion": -150, "lateral_protrusion": -170,
              "lateral_protrusion_1": -110}[name]
        axm.annotate(txt, xy=(mx, my), xytext=(mx + dx, my + dy), fontsize=9.5,
                     color=ORANGE if d["evidence"] == "NOISE" else INK, ha="center", va="center",
                     arrowprops=dict(arrowstyle="-", color=INK_3, lw=0.8))
    xs, ys = np.concatenate(xs), np.concatenate(ys)
    axm.set_xlim(xs.min() - 300, xs.max() + 300)
    axm.set_ylim(ys.max() + 220, ys.min() - 220)
    axm.set_aspect("equal")
    axm.axis("off")
    fig.text(0.33, 0.79, "(b) the same mug as a point cloud, split into parts", fontsize=11)

    # right: the gate, as two fill bars per part
    axr = fig.add_axes([0.72, 0.18, 0.26, 0.5])
    names = [n for n in ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"] if n in desc]
    for i, name in enumerate(names):
        d = desc[name]
        y = len(names) - 1 - i
        lab, col = PART_STYLE[name]
        frac = min(d["n"] / GATE_N, 1.0)
        axr.add_patch(Rectangle((0, y - 0.18), 1.0, 0.36, color=PANEL, lw=0))
        axr.add_patch(Rectangle((0, y - 0.18), frac, 0.36, color=col, lw=0))
        axr.text(-0.04, y, lab, ha="right", va="center", fontsize=10)
        verdict = {"ok": "trusted", "LOW": "usable, weak evidence"}.get(
            d["evidence"], f"{d['n']}/{GATE_N} points: refused")
        axr.text(1.04, y, verdict, ha="left", va="center", fontsize=9,
                 color=ORANGE if d["evidence"] == "NOISE" else INK_2)
    axr.axvline(1.0, color=INK, lw=1)
    axr.set_xlim(0, 1.0)
    axr.set_ylim(-0.6, len(names) - 0.4)
    axr.axis("off")
    fig.text(0.72, 0.79, f"(c) points against the {GATE_N}-point gate", fontsize=11)
    fig.text(0.72, 0.12, "Seen from the side, the handle comes back as two thin\n"
             "slivers. Rather than guess, the robot declines to use it.",
             fontsize=9, color=INK_2, va="top")
    save(fig, "handle_gate")


# --------------------------------------------------------------------------
# 3. Motion, onion-skinned
# --------------------------------------------------------------------------
STOW = {"arm_lift_joint": 0.0, "arm_flex_joint": 0.0, "arm_roll_joint": 0.0,
        "wrist_flex_joint": -1.57, "wrist_roll_joint": 0.0}   # scripts/robot/go_stow.py


def fig_motion():
    scene = s3.build_scene(EXP)
    cand = s3.EXECUTED_CANDIDATE
    row = next(r for r in csv.DictReader(open(EXP + "/close_params.csv")) if r["grasp_id"] == str(cand))
    lift = float(row["lift_m"])
    grasp = dict(scene.joints_selected)
    lifted = dict(grasp, arm_lift_joint=grasp["arm_lift_joint"] + lift)
    b = scene.base_selected
    stages = [
        ("1  start", "arm stowed for a clear camera view", (0.0, 0.0, 0.0), STOW),
        ("2  drive", f"base to x={b[0]:.2f} m, y={b[1]:.2f} m", b, STOW),
        ("3  reach", "arm to the planner's joint solution", b, grasp),
        ("4  lift", f"arm lift +{lift * 100:.0f} cm, checked with depth", b, lifted),
    ]

    W, H = 1400, 900
    center = np.array([0.35, 0.0, 0.55])
    cam = dict(kind="perspective", elevation_deg=12.0, azimuth_deg=-80.0, fov_deg=38.0)
    view, proj, _ = s3.view_and_projection(cam, center, 2.4, aspect=W / H)
    client, rid, jidx = s3.connect_and_load()
    layers = []
    for _, _, base, joints in stages:
        s3.pose_robot(client, rid, jidx, base, joints)
        layers.append(s3.mask_transparent_background(s3.render_robot(client, W, H, view, proj)))

    fig = plt.figure(figsize=(15, 7.6))
    title(fig, "How the robot moved in the 7 Aug run",
          "The HSR's URDF posed at each commanded stage and drawn on top of each other: "
          "fainter = earlier. Grey dots are the real point cloud.")
    ax = fig.add_axes([0.0, 0.0, 0.72, 0.84])
    near = scene.cloud[np.linalg.norm(scene.cloud[:, :2] - scene.target[:2], axis=1) < 0.55]
    px, py, _, ok = s3.project_points(near, view, proj, W, H)
    ax.scatter(px[ok], py[ok], s=0.5, color=INK_3, alpha=0.5, linewidths=0, rasterized=True)
    alphas = [0.22, 0.38, 0.6, 1.0]
    for layer, a in zip(layers, alphas):
        img = layer.astype(float) / 255
        img[..., 3] *= a
        ax.imshow(img)
    tx, ty, _, _ = s3.project_points(scene.target[None], view, proj, W, H)
    ax.scatter(tx, ty, s=120, marker="+", color=ORANGE, linewidths=2.2, zorder=5)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    for i, (head, body, _, _) in enumerate(stages):
        y = 0.70 - i * 0.15
        fig.text(0.74, y, head, fontsize=12, fontweight="bold", color=INK, alpha=0.45 + 0.55 * alphas[i])
        fig.text(0.74, y - 0.04, body, fontsize=10, color=INK_2)
    fig.text(0.74, 0.08, "Joint values come from the run's own planner output\n"
             "(place_run.csv) and the stow pose in go_stow.py.",
             fontsize=9, color=INK_3)
    save(fig, "motion")


# --------------------------------------------------------------------------
# 4. Same object, different tasks, different grips
# --------------------------------------------------------------------------
TASKS = [("knife", ["knife_pick", "knife_hand", "knife_put"]),
         ("remote", ["remote_hand", "remote_power", "remote_put"])]


def draw_grip(ax, rows, cons):
    """Front view of the gripper, to scale in millimetres. Force, lift and
    retreat are per-task (identical on every candidate row); the jaw opening
    and part width are medians over the candidates that passed the width checks."""
    good = [r for r in rows if r["ok"] == "1"]
    p = good[0]
    gap = float(np.median([float(r["cage_gap_m"]) for r in good])) * 1000
    part = float(np.median([float(r["part_width_m"]) for r in good])) * 1000
    lift = float(p["lift_m"]) * 1000
    finger_w, finger_h = 10, 55
    # the part being held, as a bar at the grip height
    ax.add_patch(Rectangle((-part / 2, 0), part, 22, color="#d6d3cc", lw=0, zorder=1))
    # fingers at the planned opening
    for sx in (-1, 1):
        x = sx * gap / 2 - (finger_w if sx < 0 else 0)
        ax.add_patch(Rectangle((x, -12), finger_w, finger_h, color=BLUE, lw=0, zorder=2))
    ax.add_patch(Rectangle((-gap / 2 - finger_w, finger_h - 12), gap + 2 * finger_w, 10, color=BLUE, lw=0, zorder=2))
    # lift arrow, to scale
    ax.add_patch(FancyArrowPatch((95, 0), (95, lift), arrowstyle="-|>", mutation_scale=12, color=INK_2, lw=1.4))
    ax.text(102, lift / 2, f"lift\n{lift:.0f} mm", fontsize=8.5, color=INK_2, va="center")
    if p["retreat"] == "toward_receiver":
        ax.add_patch(FancyArrowPatch((-95, lift * 0.6), (-140, lift * 0.6), arrowstyle="-|>",
                                     mutation_scale=12, color=INK_2, lw=1.4))
        ax.text(-118, lift * 0.6 + 8, "offer to\nperson", fontsize=8.5, color=INK_2, ha="center", va="bottom")
    ax.set_xlim(-160, 160)
    ax.set_ylim(-30, 130)
    ax.set_aspect("equal")
    ax.axis("off")
    force = {"standard": "normal", "gentle": "gentle", "firm": "firm"}[p["force_level"]]
    ax.text(0, finger_h + 8, f"{force} grip (effort {float(p['effort']):.2f})", ha="center",
            va="bottom", fontsize=9.5, color=BLUE if force != "gentle" else "#5a9be6", fontweight="bold")
    body = (f"grasp: {cons['target_part']}; jaws open {gap:.0f} mm on a {part:.0f} mm part\n"
            f"{len(good)} of {len(rows)} candidate grasps passed the width checks")
    return f"“{cons['instruction']}”", body


def fig_grips():
    fig = plt.figure(figsize=(15, 8.4))
    title(fig, "Same object, different task, different grip",
          "Grip settings the system derived from each instruction's constraints, drawn to scale "
          "(front view of the jaws, millimetres). No extra model call; a fixed rule table.")
    for r, (obj, runs) in enumerate(TASKS):
        fig.text(0.01, 0.72 - r * 0.40, obj, fontsize=13, fontweight="bold", rotation=90, va="center")
        for c, run in enumerate(runs):
            rows = list(csv.DictReader(open(WORKSPACE / f"close_params_{run}.csv", encoding="utf-8")))
            cons = json.load(open(WORKSPACE / f"constraints_{run}.json", encoding="utf-8"))
            ax = fig.add_axes([0.05 + c * 0.32, 0.53 - r * 0.40, 0.28, 0.26])
            head, body = draw_grip(ax, rows, cons)
            ax.text(0.0, 1.12, head, transform=ax.transAxes, fontsize=11, va="bottom")
            ax.text(0.0, -0.06, body, transform=ax.transAxes, fontsize=9, color=INK_2, va="top",
                    linespacing=1.4)
    save(fig, "grips")


if __name__ == "__main__":
    fig_scenes()
    fig_handle_gate()
    fig_motion()
    fig_grips()
