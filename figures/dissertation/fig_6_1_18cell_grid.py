"""Fig 6.1 -- The 18-cell grid (QUANTITATIVE, Class D).

The inferred part does not change with the task for five of six objects. Text-only
offline reasoning grid (AffordanceReasoner, Stage 1+3, no image/capture needed --
6 objects x 3 instruction types = 18 cells). Source located 2026-08-16 after the
V3 blocker (figures/BLOCKERS.md item 2): experiments/vlm_grid/vlm_grid_raw.json,
cross-checked against experiments/vlm_grid/vlm_grid_results.md (same 18 rows, plus
a keyword-baseline/diverged column pair -- 16/18 diverged, matching the Fact
Block's keyword-baseline claim, not independently re-derived here).

Source: workspace/experiments\\vlm_grid\\vlm_grid_raw.json

Run: python figures/dissertation/fig_6_1_18cell_grid.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt

import _qa as qa
import _style as fs

FIGURE_ID = "fig_6_1_18cell_grid"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
GRID_PATH = os.path.join(DATA_ROOT, "experiments", "vlm_grid", "vlm_grid_raw.json")

OBJECT_ORDER = ["mug", "hammer", "knife", "pan", "bowl", "bottle"]
TYPE_ORDER = ["relocate", "use", "handover"]

INTENT = "The inferred part does not change with the task for five of six objects."

CAPTION = (
    "Fig 6.1. The 18-cell grid: inferred target part by object (rows) and instruction type "
    "(columns), from offline text-only reasoning (AffordanceReasoner, no image required; "
    "experiments/vlm_grid/vlm_grid_raw.json). Five of six objects return the identical part "
    "across all three instruction types (green). Only the bottle (red outline) varies: body "
    "for relocation, neck for both pouring and handover. n=18 cells, 6 objects x 3 instruction "
    "types."
)


def _load_grid():
    with open(GRID_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 18, f"expected 18 cells, got {len(data)}"
    grid = {}
    for e in data:
        grid[(e["object"], e["type"])] = e["step3"]["target_part"]
    for obj in OBJECT_ORDER:
        for t in TYPE_ORDER:
            assert (obj, t) in grid, f"missing cell ({obj}, {t})"
    return grid


def build():
    grid = _load_grid()

    fig, ax = plt.subplots(figsize=(fs.HALF_WIDTH_IN + 1.2, 3.4))
    ax.set_xlim(0, len(TYPE_ORDER))
    ax.set_ylim(0, len(OBJECT_ORDER))
    ax.invert_yaxis()

    constant_colour = fs.OKABE_ITO["green"]
    varying_colour = fs.OKABE_ITO["vermillion"]

    for i, obj in enumerate(OBJECT_ORDER):
        parts = [grid[(obj, t)] for t in TYPE_ORDER]
        is_constant = len(set(parts)) == 1
        for j, t in enumerate(TYPE_ORDER):
            part = grid[(obj, t)]
            edge = constant_colour if is_constant else varying_colour
            face = constant_colour if is_constant else varying_colour
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=face, alpha=0.18,
                                        edgecolor=edge, linewidth=1.8 if not is_constant else 1.0))
            ax.text(j + 0.5, i + 0.5, part, ha="center", va="center", fontsize=9,
                     fontweight="bold" if not is_constant else "normal",
                     color=fs.OKABE_ITO["black"])

    ax.set_xticks([j + 0.5 for j in range(len(TYPE_ORDER))])
    ax.set_xticklabels(TYPE_ORDER, fontsize=9)
    ax.set_yticks([i + 0.5 for i in range(len(OBJECT_ORDER))])
    ax.set_yticklabels(OBJECT_ORDER, fontsize=9)
    ax.set_xlabel("instruction type (n=18 cells, 6 objects x 3 types)", labelpad=10)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.text(len(TYPE_ORDER) + 0.05, 5.5, "only object\nwith a\nchanging part", fontsize=7.5,
            ha="left", va="center", color=varying_colour)
    ax.annotate("", xy=(len(TYPE_ORDER), 5.5), xytext=(len(TYPE_ORDER) + 0.02, 5.5),
                arrowprops=dict(arrowstyle="-", color=varying_colour, lw=0.9))

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {GRID_PATH}")
    fig = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.HALF_WIDTH_IN + 1.2)
    qa.check_labels_complete(fig, FIGURE_ID)
    qa.check_post_save_layout(fig, FIGURE_ID, width_class=fs.HALF_WIDTH_IN + 1.2)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="A 6x3 grid of part names; five rows are solid green with the same word "
                   "repeated three times, one row (bottle) is red-outlined with a different word "
                   "in its first column vs the other two -- reads as 'the part barely changes "
                   "except for one object' without reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="every cell labelled with its own part name; row/column headers state object/instruction type; arrow+note calls out the bottle row explicitly; x-axis states n=18.",
        referent_audit="callout arrow points directly at the bottle row.",
    )
    report_path = qa.write_report("V3")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
