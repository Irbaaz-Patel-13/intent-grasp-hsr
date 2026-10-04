"""Build the four figures used in the top-level README.

Every number is read from the recorded files in workspace/ at run time;
nothing is typed in by hand. Run from the repository root:

    python figures/readme/make_readme_figures.py

Writes docs/images/{pipeline,identification,part_grounding,hardware_trials}.png
"""
import csv
import json
import re
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

from intent_grasp.paths import REPO_ROOT, WORKSPACE

OUT = REPO_ROOT / "docs" / "images"

# Palette: validated reference slots 1-2 (light mode) plus neutral inks.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8984"
HAIRLINE = "#e4e3df"
BLUE = "#2a78d6"
BLUE_TINT = "#e8f1fc"
ORANGE = "#eb6834"
PANEL = "#f3f2ef"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "text.color": INK,
    "axes.edgecolor": HAIRLINE,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote", OUT / f"{name}.png")


def title(fig, text, sub=None, y=0.98):
    fig.text(0.02, y, text, fontsize=15, fontweight="bold", ha="left", va="top")
    if sub:
        fig.text(0.02, y - 0.06, sub, fontsize=11, color=INK_2, ha="left", va="top")


# --------------------------------------------------------------------------
# 1. Pipeline diagram
# --------------------------------------------------------------------------
def box(ax, x, y, w, h, head, body, novel=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=BLUE_TINT if novel else "white",
                                ec=BLUE if novel else INK_3, lw=1.6 if novel else 1.0))
    ax.text(x + w / 2, y + h - 0.35, head, ha="center", va="top", fontsize=10.5, fontweight="bold")
    ax.text(x + w / 2, y + h - 0.95, body, ha="center", va="top", fontsize=9, color=INK_2,
            linespacing=1.35)


def arrow(ax, p, q, color=INK_3):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, color=color,
                                 lw=1.2, shrinkA=0, shrinkB=0))


def fig_pipeline():
    fig = plt.figure(figsize=(14, 6.4))
    ax = fig.add_axes([0, 0, 1, 0.84])
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 11.6)
    ax.axis("off")
    title(fig, "From an instruction to a verified lift",
          "Perception and reasoning run on a GPU PC; everything that moves the robot runs on the HSR workstation.")

    for y0, label in [(6.3, "GPU PC  (Python, CUDA)"), (0.2, "HSR workstation  (ROS Noetic)")]:
        ax.add_patch(FancyBboxPatch((0.2, y0), 27.6, 4.7, boxstyle="round,pad=0,rounding_size=0.2",
                                    fc=PANEL, ec="none"))
        ax.text(27.4, y0 + 4.4, label, fontsize=10, fontweight="bold", color=INK_2, va="top",
                ha="right")

    W, H, Y1, Y2 = 4.0, 2.4, 7.3, 1.2
    xs = [0.8, 5.5, 10.2, 14.9, 19.6, 24.3]
    W_last = 3.3
    top = [
        ("Instruction + RGB-D", "\"I'd like a hot drink\"\n+ head-camera capture", False),
        ("Reason", "GPT-4o: task, object,\npart + task constraints", False),
        ("Find the object", "LangSAM (GroundingDINO\n+ SAM): object mask", False),
        ("Find the part", "split the point cloud,\nmatch the named part", True),
        ("Grasp the part", "Contact-GraspNet,\nonly on that part", False),
        ("Constraints to grip", "force, clearance, lift\n(rule table, no LLM)", True),
    ]
    for i, (h, b, nov) in enumerate(top):
        box(ax, xs[i], Y1, W_last if i == 5 else W, H, h, b, nov)
    for i in range(5):
        arrow(ax, (xs[i] + W, Y1 + H / 2), (xs[i + 1], Y1 + H / 2))
    ax.text(xs[3] + W / 2, Y1 - 0.2, "too few points: refuse, don't guess",
            ha="center", va="top", fontsize=8.8, color=ORANGE, fontweight="bold")

    bxs = [0.8, 6.3, 11.8, 17.3, 22.8]
    bw = 4.5
    bottom = [
        ("Capture", "head RGB-D +\ncamera pose"),
        ("Place the base", "stand where the arm\ncan reach the grasp"),
        ("Pre-flight checks", "8 GO / NO-GO checks\nagainst the URDF"),
        ("Execute", "visual servo, then\nclose until contact"),
        ("Verify", "lift measured with depth,\nlogged to trials.csv"),
    ]
    for i, (h, b) in enumerate(bottom):
        box(ax, bxs[i], Y2, bw, H, h, b)
    for i in range(4):
        arrow(ax, (bxs[i] + bw, Y2 + H / 2), (bxs[i + 1], Y2 + H / 2))

    # hand-offs between machines: straight runs through the gap between lanes
    xa = xs[0] + W / 2
    arrow(ax, (xa, Y2 + H), (xa, Y1), color=BLUE)
    ax.text(xa + 0.25, 5.65, "capture .npz", fontsize=8.8, color=BLUE, va="center")
    xg, xb, ymid = xs[5] + W_last / 2, bxs[1] + bw / 2, 5.65
    ax.plot([xg, xg], [Y1, ymid], color=BLUE, lw=1.2)
    ax.plot([xg, xb], [ymid, ymid], color=BLUE, lw=1.2)
    arrow(ax, (xb, ymid), (xb, Y2 + H), color=BLUE)
    ax.text((xg + xb) / 2, ymid + 0.15, "grasps + point cloud + grip parameters", fontsize=8.8,
            color=BLUE, ha="center", va="bottom")

    for x0, fc, ec, lw, lbl in [(19.9, BLUE_TINT, BLUE, 1.4, "added in this project"),
                                (23.9, "white", INK_3, 1.0, "existing method / tool")]:
        ax.add_patch(FancyBboxPatch((x0, 11.15), 0.5, 0.35, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=fc, ec=ec, lw=lw))
        ax.text(x0 + 0.7, 11.32, lbl, fontsize=9.5, va="center", color=INK_2)
    save(fig, "pipeline")


# --------------------------------------------------------------------------
# 2. Object identification from intent (vlm_stability.csv)
# --------------------------------------------------------------------------
SCENE_LABEL = {
    "TV_remote": "remote",
    "coke_can": "coke can",
    "dishwash_bottle": "dish-soap bottle",
    "metal_spoon": "spoon",
    "pot_with_handle_and_lid": "pot",
    "cluster_mug_cokecan": "mug, can",
    "cluster_mug_cokecan_pot": "mug, can, pot",
    "cluster_mug_remote_pot": "mug, remote, pot",
}


def short(instr, n=44):
    return instr if len(instr) <= n else instr[: n - 1].rstrip() + "…"


def fig_identification():
    rows = list(csv.DictReader(open(WORKSPACE / "vlm_stability.csv", encoding="utf-8")))
    cells = defaultdict(dict)
    order = []
    for r in rows:
        key = (r["scene"], r["instruction"])
        if key not in cells:
            order.append(key)
        cells[key][int(r["pass_no"])] = r
    n_ok = sum(r["correct"] == "1" for r in rows)

    fig = plt.figure(figsize=(12, 7.6))
    ax = fig.add_axes([0.42, 0.09, 0.36, 0.76])
    title(fig, f"GPT-4o picked the intended object in {n_ok} of {len(rows)} runs",
          "13 scene + instruction pairs, each run 5 times. The instruction never names the object.")
    n = len(order)
    for i, key in enumerate(order):
        y = n - 1 - i
        wrong = []
        for p in range(1, 6):
            r = cells[key][p]
            if r["correct"] == "1":
                ax.scatter(p, y, s=150, color=BLUE, zorder=3, edgecolors=SURFACE, linewidths=2)
            else:
                ax.scatter(p, y, s=150, marker="X", color=ORANGE, zorder=3)
                wrong.append(r["picked"])
        scene, instr = key
        ax.text(0.35, y + 0.13, f"“{short(instr)}”", ha="right", va="center", fontsize=10)
        ax.text(0.35, y - 0.25, f"scene: {SCENE_LABEL.get(scene, scene)}", ha="right", va="center",
                fontsize=8.5, color=INK_3)
        if wrong:
            picks = ", ".join(f"{w} ×{wrong.count(w)}" for w in dict.fromkeys(wrong))
            ax.text(5.6, y, f"picked {picks}", va="center", fontsize=9.5, color=INK_2)
    ax.set_xlim(0.4, 5.5)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xticks(range(1, 6), [f"run {p}" for p in range(1, 6)])
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", length=0)
    lx, ly = 0.80, 0.93
    fig.text(lx, ly, "●", color=BLUE, fontsize=14, va="center")
    fig.text(lx + 0.018, ly, "intended object", fontsize=10, va="center", color=INK_2)
    fig.text(lx, ly - 0.035, "✖", color=ORANGE, fontsize=11, va="center")
    fig.text(lx + 0.018, ly - 0.035, "another object", fontsize=10, va="center", color=INK_2)
    save(fig, "identification")


# --------------------------------------------------------------------------
# 3. Part grounding collapse (run logs + live overlay)
# --------------------------------------------------------------------------
RUNS = ["knife_pick2", "knife_hand", "knife_put", "remote_hand", "remote_power", "remote_put"]
WARN = re.compile(r"collapsed to whole object \((\d+)% of object mask covered\)")


def fig_part_grounding():
    data = []
    for run in RUNS:
        log = open(WORKSPACE / f"run_{run}.log", encoding="utf-8", errors="replace").read()
        pct = int(WARN.search(log).group(1))
        cons = json.load(open(WORKSPACE / f"constraints_{run.replace('pick2', 'pick')}.json",
                              encoding="utf-8"))
        data.append((cons["instruction"], cons["target_part"], pct))

    fig = plt.figure(figsize=(13, 5.6))
    title(fig, "Asking LangSAM for a part returns most of the object",
          "Live runs on the HSR head camera. 100% would mean the “part” mask is the whole object.")

    axl = fig.add_axes([0.02, 0.08, 0.42, 0.70])
    im = Image.open(WORKSPACE / "report_assets" / "figures_live" / "langsam_overlay_knife_pick.png")
    axl.imshow(im.crop((150, 300, 450, 440)))
    axl.axis("off")
    axl.set_title("“pick up the knife”: requested part = handle", fontsize=10.5,
                  loc="left", color=INK)
    axl.text(0.0, -0.08, "Pink shading is the mask LangSAM returned for “handle”. "
             "It lies on the blade;\nthe dark handle on the right is left out.",
             transform=axl.transAxes, fontsize=9.5, color=INK_2, va="top")

    ax = fig.add_axes([0.66, 0.12, 0.31, 0.62])
    ys = list(range(len(data)))[::-1]
    for y, (instr, part, pct) in zip(ys, data):
        ax.barh(y, pct, height=0.55, color=BLUE)
        ax.text(pct - 2, y, f"{pct}%", va="center", ha="right", fontsize=10, color="white",
                fontweight="bold")
        ax.text(-3, y + 0.12, f"“{instr}”", ha="right", va="center", fontsize=9.5)
        ax.text(-3, y - 0.22, f"asked for: {part}", ha="right", va="center", fontsize=8.5, color=INK_3)
    ax.axvline(100, color=INK_3, lw=1)
    ax.text(100, len(data) - 0.35, "whole object", ha="center", va="bottom", fontsize=9, color=INK_2)
    ax.set_xlim(0, 112)
    ax.set_ylim(-0.6, len(data) - 0.4)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of the object mask covered by the “part” mask (%)")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    save(fig, "part_grounding")


# --------------------------------------------------------------------------
# 4. Hardware trials (trials.csv)
# --------------------------------------------------------------------------
def fig_hardware():
    rows = list(csv.DictReader(open(WORKSPACE / "trials.csv", encoding="utf-8")))
    pts = []
    for r in rows:
        m = re.match(r"trial (\d+)", r["note"])
        x = int(m.group(1)) if m else 13          # trial 8 has no row; its slot stays empty
        pts.append((x, r["verdict"], float(r["z_rise_m"] or 0) * 100))
    trials = [p for p in pts if p[0] != 13]
    ok = [p for p in trials if p[1] == "GRASP_OK"]

    fig = plt.figure(figsize=(13, 5.8))
    ax = fig.add_axes([0.06, 0.14, 0.92, 0.6])
    title(fig, f"{len(ok)} of {len(trials)} logged trials grasped and lifted the mug",
          "Toyota HSR, real table. Height the mug rose after the grasp, measured with depth.")

    groups = [(0.5, 4.5, "25 Jul"), (4.5, 7.5, "28 Jul  (visual servo off)"),
              (8.5, 12.5, "1 Aug  (fully autonomous)"), (12.5, 13.5, "3 Aug demo")]
    for i, (a, b, lbl) in enumerate(groups):
        if i % 2 == 0:
            ax.axvspan(a, b, color=PANEL, lw=0, zorder=0)
        ax.text((a + b) / 2, 17.2, lbl, ha="center", va="bottom", fontsize=9.5, color=INK_2)

    for x, verdict, z in pts:
        if verdict == "GRASP_OK":
            ax.plot([x, x], [0, z], color=BLUE, lw=2, zorder=2, solid_capstyle="round")
            ax.scatter(x, z, s=90, color=BLUE, zorder=3, edgecolors=SURFACE, linewidths=2)
            ax.text(x, z + 0.8, f"{z:.1f}", ha="center", va="bottom", fontsize=9, color=INK)
        elif verdict.startswith("ABORT"):
            ax.scatter(x, 0.6, s=90, marker="X", color=ORANGE, zorder=3)
            ax.text(x, 1.6, "aborted\nbefore grasp", ha="center", va="bottom", fontsize=8.5, color=INK_2)
        else:
            ax.scatter(x, 0.6, s=90, facecolors=SURFACE, edgecolors=ORANGE, linewidths=2, zorder=3)
            ax.text(x, 1.6, "held, but\nlift failed", ha="center", va="bottom", fontsize=8.5, color=INK_2)
    ax.text(8, 1.6, "no record", ha="center", va="bottom", fontsize=8.5, color=INK_3)

    ax.set_xlim(0.5, 13.5)
    ax.set_ylim(0, 17)
    ax.set_xticks(list(range(1, 14)), [str(i) for i in range(1, 13)] + ["live\ndemo"])
    ax.set_xlabel("trial")
    ax.set_ylabel("lift height (cm)")
    ax.grid(axis="y", color=HAIRLINE, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="both", length=0)
    save(fig, "hardware_trials")


if __name__ == "__main__":
    fig_pipeline()
    fig_identification()
    fig_part_grounding()
    fig_hardware()
