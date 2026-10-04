"""
new_methodology.py -- Slide 11: Experimental Methodology.

Purpose: a dedicated methodology/evaluation diagram, not a result figure.
Answers "what exactly did you test, and how did you decide whether the
system worked?" -- the real 9-stage pipeline this dissertation's own code
implements, split into the perception/evaluation half (what NEW-A/B/C/D/G
measure) and the execution/evaluation half (what NEW-HW/F measure), each
stage tagged with the real evidence source file(s) that back it.

Scientific claim: none -- this is process documentation, not a result. Every
stage name and every evidence-source badge is a real file that exists in
this repository; no invented terminology, no fabricated pipeline stage.
Required real data: every cited source file's existence is checked
programmatically at render time (_real_sources_exist()) and reported on the
figure's own caption and stdout, rather than asserted from memory.

Run: python new_methodology.py
Output: report_assets/figures/methodology_slide11.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

HERE = str(WORKSPACE)

# (stage label, [(display_badge, real_checkable_path), ...])
PERCEPTION_STAGES = [
    ("REAL OBJECT /\nSCENE", [("captures_pairs_2/*.npz", "captures_pairs_2")]),
    ("VLM\nREASONING", [("vlm_stability.csv", "vlm_stability.csv")]),
    ("PART\nGROUNDING", [("PART_NAMING_ABLATION.csv", "report_assets/PART_NAMING_ABLATION.csv")]),
    ("GEOMETRIC\nDECOMPOSITION", [("batch_scene_analysis.csv", "batch_scene_analysis.csv")]),
    ("EVIDENCE\nGATE", [("part_adaptive.py", "part_adaptive.py")]),
]
EXECUTION_STAGES = [
    ("GRASP\nGENERATION", [("grasp_policy.py", "grasp_policy.py")]),
    ("KINEMATIC /\nCOLLISION CHECKS", [("execute_place_grasp_raw.py",
                                         "scripts/robot/execute_place_grasp_raw.py")]),
    ("REAL HSR\nEXECUTION", [("trials.csv", "trials.csv")]),
    ("LOGGED\nOUTCOME", [("FAILURE_REGISTER.csv", "report_assets/FAILURE_REGISTER.csv")]),
]


def _real_sources_exist():
    """Every cited evidence-source file is checked to exist -- this diagram
    cites nothing that isn't actually in the repository."""
    missing = []
    for label, sources in PERCEPTION_STAGES + EXECUTION_STAGES:
        for badge, real_path in sources:
            if not os.path.exists(os.path.join(HERE, real_path)):
                missing.append((label, real_path))
    return missing


def _stage_box(ax, x, y, w, h, label, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012",
                                 transform=ax.transAxes, facecolor=fs.CALLOUT_BG, edgecolor=color,
                                 linewidth=2.0))
    ax.text(x + w / 2, y + h / 2, label, transform=ax.transAxes, ha="center", va="center", color=fs.INK,
            fontsize=16, weight="bold", family=fs.FONT, linespacing=1.3)


def render(out_path=None):
    out_path = out_path or os.path.join("report_assets", "figures", "methodology_slide11.png")
    missing = _real_sources_exist()

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Experimental Methodology -- What Was Tested, and How", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Real pipeline stages; each box's own badge is the real file that evaluates it", **fs.BODY)

    ax = fig.add_axes([0.02, 0.10, 0.96, 0.72])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # -- row labels
    ax.text(0.005, 0.79, "PERCEPTION /\nEVALUATION", transform=ax.transAxes, ha="left", va="center",
            color=fs.REASONING, fontsize=13, weight="bold", family=fs.FONT, linespacing=1.4, rotation=0)
    ax.text(0.005, 0.28, "EXECUTION /\nEVALUATION", transform=ax.transAxes, ha="left", va="center",
            color=fs.CANDIDATE, fontsize=13, weight="bold", family=fs.FONT, linespacing=1.4, rotation=0)

    n_p = len(PERCEPTION_STAGES)
    box_w, gap = 0.148, 0.02
    start_x = 0.145
    row_y_top, row_h = 0.62, 0.28
    for i, (label, sources) in enumerate(PERCEPTION_STAGES):
        x = start_x + i * (box_w + gap)
        _stage_box(ax, x, row_y_top, box_w, row_h, label, fs.REASONING)
        ax.text(x + box_w / 2, row_y_top - 0.05, sources[0][0], transform=ax.transAxes, ha="center", va="top",
                color=fs.MUTED, fontsize=12, family="monospace")
        if i < n_p - 1:
            ax.add_patch(FancyArrowPatch((x + box_w, row_y_top + row_h / 2), (x + box_w + gap, row_y_top + row_h / 2),
                                          transform=ax.transAxes, color=fs.MUTED, linewidth=1.6,
                                          arrowstyle="-|>", mutation_scale=13))

    # connector: last perception box (evidence gate) down to first execution box
    last_px = start_x + (n_p - 1) * (box_w + gap) + box_w / 2
    ax.add_patch(FancyArrowPatch((last_px, row_y_top), (last_px, 0.28 + row_h),
                                  transform=ax.transAxes, color=fs.MUTED, linewidth=1.6,
                                  arrowstyle="-|>", mutation_scale=13, connectionstyle="arc3,rad=-0.3"))

    n_e = len(EXECUTION_STAGES)
    row_y_bot = 0.12
    start_x_e = 0.145
    for i, (label, sources) in enumerate(EXECUTION_STAGES):
        x = start_x_e + i * (box_w + gap)
        _stage_box(ax, x, row_y_bot, box_w, row_h, label, fs.CANDIDATE)
        ax.text(x + box_w / 2, row_y_bot - 0.05, sources[0][0], transform=ax.transAxes, ha="center", va="top",
                color=fs.MUTED, fontsize=12, family="monospace")
        if i < n_e - 1:
            ax.add_patch(FancyArrowPatch((x + box_w, row_y_bot + row_h / 2), (x + box_w + gap, row_y_bot + row_h / 2),
                                          transform=ax.transAxes, color=fs.MUTED, linewidth=1.6,
                                          arrowstyle="-|>", mutation_scale=13))

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Perception/evaluation: does the system correctly identify intent and find geometric evidence "
              "for the requested part? Execution/evaluation: does a supported part actually reach the robot.",
              **fs.CAPTION)
    src_status = "all cited evidence-source files verified to exist" if not missing else \
        f"WARNING: {len(missing)} cited source(s) not found: {missing}"
    fig.text(fs.MARGIN, fs.CAPTION_Y, f"Source-file badges are the real evaluation artefacts per stage -- {src_status}.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report, missing


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report, missing = render(out_path=args.out)
    print(f"methodology written to {path}")
    print(report.summary())
    if missing:
        print(f"WARNING: missing cited sources: {missing}")
