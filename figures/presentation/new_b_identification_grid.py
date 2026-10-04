"""
new_b_identification_grid.py -- NEW-B: Identification Grid (13 scenes x 5
passes).

Scientific claim: real intent-only object identification, repeated 5 times
per scene/instruction cell (temperature=0 does not make the backend
bit-deterministic), is 61/65 correct (94%); the 4 failures cluster in two
cells, both asking for the mug across pot-containing cluttered scenes.
Supporting evidence: vlm_stability.csv (65 real rows: pass_no, scene,
  instruction, correct); vlm_stability.md (same data, its own 61/65 summary,
  used only as a cross-check, not as the plotted source -- the CSV's raw
  per-pass rows are what's plotted). Right-hand strip: a REAL but SEPARATE
  and complementary dataset -- experiments/vlm_grid/vlm_grid_results.md's
  18-cell (6 object x 3 instruction) keyword-baseline-divergence battery
  (16/18 diverged). No keyword-baseline comparison exists for these same
  13 scene/instruction cells; the strip is not a per-row breakdown of this
  grid, and is captioned as such.
Required real data: all 65 real per-pass correct/incorrect values, in
  source (not sorted) row order -- used directly, un-reordered, so the
  clustering of the 4 failures is visible as it actually occurred, not as
  a curated pattern.
Required diagrammatic elements: none. The grid is a direct rendering of
  the real CSV.

Run: python new_b_identification_grid.py
Output: generated_assets/new_b/new_b_identification_grid.png
"""
import argparse
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "vlm_stability.csv")
KEYWORD_DIVERGED, KEYWORD_TOTAL = 16, 18  # experiments/vlm_grid/vlm_grid_results.md, real, separate dataset

CAPTURES_DIR = os.path.join(str(WORKSPACE), "captures_0723")
FAIL_SCENES = [
    ("cluster_mug_cokecan_pot", "cap_cluster_mug_cokecan_pot.npz"),
    ("cluster_mug_remote_pot", "cap_cluster_mug_remote_pot.npz"),
]
FAIL_INSTRUCTION = "I'd like a hot drink"


def load_grid():
    rows = list(csv.DictReader(open(CSV_PATH)))
    row_keys = []  # (scene, instruction) in first-seen (source) order
    seen = set()
    for r in rows:
        key = (r["scene"], r["instruction"])
        if key not in seen:
            seen.add(key)
            row_keys.append(key)
    grid = {key: [None] * 5 for key in row_keys}
    for r in rows:
        key = (r["scene"], r["instruction"])
        grid[key][int(r["pass_no"]) - 1] = int(r["correct"])
    return row_keys, grid


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_b"), "new_b_identification_grid.png")
    row_keys, grid = load_grid()
    n_rows = len(row_keys)
    total_correct = sum(sum(v) for v in grid.values())
    total_cells = n_rows * 5
    stable_rows = sum(1 for v in grid.values() if sum(v) == 5)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Identification Stability -- 13 Scenes x 5 Passes", **fs.TITLE, x=fs.MARGIN, ha="left")
    # Subtitle previously repeated the same correct/total figure the bottom
    # summary line already states in full -- kept to one statement each.
    fig.text(fs.MARGIN, 0.885,
              "Real repeated intent-only identification, source (not sorted) row order", **fs.BODY)

    ax = fig.add_axes([0.34, 0.12, 0.46, 0.70])
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(-0.5, n_rows - 0.5)
    ax.invert_yaxis()
    ax.set_xticks(range(5))
    ax.set_xticklabels([f"pass {i+1}" for i in range(5)], color=fs.MUTED, fontsize=10, family=fs.FONT)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.set_facecolor(fs.SLIDE_BG)

    for i, key in enumerate(row_keys):
        vals = grid[key]
        for j, v in enumerate(vals):
            if v == 1:
                ax.add_patch(Circle((j, i), 0.32, facecolor=fs.ACCEPTED, edgecolor="none", zorder=3))
            else:
                ax.add_patch(Circle((j, i), 0.34, facecolor="none", edgecolor=fs.REJECTED, linewidth=2.4, zorder=3))
        if sum(vals) < 5:
            ax.add_patch(Rectangle((-0.46, i - 0.46), 4.92, 0.92, fill=False, edgecolor=fs.REJECTED,
                                    linewidth=1.0, linestyle=(0, (3, 2)), zorder=2))

    # row labels (scene + instruction) on the left, outside the axes -- one
    # combined line per row (not two) so 13 rows fit at a legible 10pt.
    for i, (scene, instr) in enumerate(row_keys):
        instr_short = instr if len(instr) <= 34 else instr[:31] + "..."
        fig.text(0.335, 0.12 + 0.70 * (1 - (i + 0.5) / n_rows),
                 f"{scene}: \u201c{instr_short}\u201d", ha="right", va="center",
                 color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)

    ax.text(2.0, -1.6, f"{total_correct}/{total_cells} correct (94%)  --  {stable_rows}/{n_rows} rows "
             "perfectly stable (5/5)  --  4 failures, both in pot-containing cluttered scenes",
             ha="center", va="top", color=fs.MUTED, fontsize=10, family=fs.FONT)

    # right-hand strip: real but separate dataset
    ax2 = fig.add_axes([0.83, 0.30, 0.14, 0.35])
    ax2.axis("off")
    ax2.add_patch(Rectangle((0, 0), 1, 1, transform=ax2.transAxes, fill=False, edgecolor=fs.FAINT, linewidth=1.0))
    ax2.text(0.5, 0.86, "Keyword-baseline\ndivergence", transform=ax2.transAxes, ha="center", va="top",
              color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)
    ax2.text(0.5, 0.55, f"{KEYWORD_DIVERGED}/{KEYWORD_TOTAL}", transform=ax2.transAxes, ha="center", va="center",
              color=fs.CANDIDATE, fontsize=26, weight="bold", family=fs.FONT)
    ax2.text(0.5, 0.30, "diverged", transform=ax2.transAxes, ha="center", va="top",
              color=fs.MUTED, fontsize=10, family=fs.FONT)
    ax2.text(0.5, 0.08, "separate 18-cell\nbattery, not these\n13 scenes", transform=ax2.transAxes,
              ha="center", va="top", color=fs.MUTED, fontsize=10, family=fs.FONT, style="italic")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "Filled green = correct, outlined red = incorrect; dashed row border marks a row with any "
              "failure. Rows are in source order (first appearance in the raw CSV), not sorted.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Source: vlm_stability.csv (65 real rows). Right strip: experiments/vlm_grid/vlm_grid_results.md "
              "-- a real, separate 6-object x 3-instruction battery, not a per-row breakdown of this grid.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "No keyword-baseline comparison exists for these 13 scene/instruction cells.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: drop the 65-cell grid, lead with 61/65 at hero size,
    then the two real scene photos that produced all 4 failures."""
    out_path = out_path or os.path.join(fs.asset_dir("new_b"), "new_b_identification_grid_slide.png")
    row_keys, grid = load_grid()
    n_rows = len(row_keys)
    total_correct = sum(sum(v) for v in grid.values())
    total_cells = n_rows * 5

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Two Cells Fail -- Same Instruction, Both Scenes Have a Pot", **{**fs.TITLE, "size": 32},
                 x=fs.MARGIN, ha="left")

    stable_rows = sum(1 for v in grid.values() if sum(v) == 5)

    # Primary hero (61/65 correct) and secondary hero (11/13 scenes fully
    # stable) as two tight units, each number+tag kept adjacent -- neither
    # floats disconnected from what it labels.
    ax_num = fig.add_axes([0.03, 0.58, 0.24, 0.20])
    ax_num.axis("off")
    ax_num.text(0.5, 0.62, f"{total_correct}/{total_cells}", transform=ax_num.transAxes, ha="center",
                va="center", color=fs.ACCEPTED, fontsize=72, weight="bold", family=fs.FONT)
    ax_num.text(0.5, 0.18, "correct", transform=ax_num.transAxes, ha="center", va="center",
                color=fs.MUTED, fontsize=18, family=fs.FONT)

    ax_num2 = fig.add_axes([0.03, 0.36, 0.24, 0.16])
    ax_num2.axis("off")
    ax_num2.text(0.5, 0.60, f"{stable_rows}/{n_rows}", transform=ax_num2.transAxes, ha="center",
                va="center", color=fs.INK, fontsize=44, weight="bold", family=fs.FONT)
    ax_num2.text(0.5, 0.10, "scenes stable across\nall five passes", transform=ax_num2.transAxes, ha="center",
                va="center", color=fs.MUTED, fontsize=16, family=fs.FONT, linespacing=1.3)

    # Tight crop on the tabletop (drop couch/rack/floor margins) so the pot
    # is the obvious shared element between the two scenes, not a detail a
    # viewer has to hunt for in a wide establishing shot.
    CROP = (110, 190, 560, 500)  # x0, y0, x1, y1
    for i, (scene, npz_name) in enumerate(FAIL_SCENES):
        d = np.load(os.path.join(CAPTURES_DIR, npz_name))
        rgb = d["rgb"]
        x0, y0, x1, y1 = CROP
        ax = fig.add_axes([0.31 + i * 0.345, 0.12, 0.32, 0.66])
        ax.imshow(rgb[y0:y1, x0:x1])
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(fs.REJECTED)
            spine.set_linewidth(2.5)
        ax.set_title(scene, color=fs.INK, fontsize=16, weight="bold", family=fs.FONT, pad=8)

    fig.text(0.03, 0.28, f'instruction: "{FAIL_INSTRUCTION}"', color=fs.INK, fontsize=18, weight="bold",
              family=fs.FONT)
    fig.text(0.03, 0.20, "both scenes contain\na pot", color=fs.MUTED, fontsize=16, family=fs.FONT,
              linespacing=1.4)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "vlm_stability.csv", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-B identification grid", [
        "Full grid: 13 scenes x 5 passes = 65 real cells, source vlm_stability.csv, source row order.",
        f"{sum(1 for v in grid.values() if sum(v) == 5)}/{n_rows} rows are perfectly stable (5/5 correct).",
        "All 4 failures: 3x cluster_mug_cokecan_pot, 1x cluster_mug_remote_pot, all on the same "
        f'instruction "{FAIL_INSTRUCTION}".',
        "Right-hand strip in the report grid (16/18 keyword-baseline divergence) is a real but SEPARATE "
        "18-cell battery (experiments/vlm_grid/vlm_grid_results.md) -- not a breakdown of these 13 cells.",
        "No keyword-baseline comparison exists for these exact 13 scene/instruction cells.",
    ])
    return out_path, report


def render(variant="report", out_path=None):
    if variant == "report":
        return render_report(out_path=out_path)
    if variant == "slide":
        return render_slide(out_path=out_path)
    raise ValueError(f"unknown variant {variant!r}, expected 'report' or 'slide'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", choices=["report", "slide"], default="report")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(variant=args.variant, out_path=args.out)
    print(f"new_b ({args.variant}) written to {path}")
    print(report.summary())
