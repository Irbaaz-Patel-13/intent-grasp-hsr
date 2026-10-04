"""Fig 1.2 -- The granularity gap (QUANTITATIVE, real capture + real mask).

Panel (a): the real instruction and the reasoner's own output for this capture
(target_object, target_part) -- constraints_knife_pick.json, a real logged
reasoning result, not hand-typed.
Panel (b): the real LangSAM part-grounding overlay for the same instruction --
report_assets/figures_live/langsam_overlay_knife_pick.png, a live, unmodified
run of VisualAffordanceGrounder.ground()/.visualize_grounding() (see
new_c_langsam_coverage.py, same repo, prior verified source). The annotated
coverage number is the one actually logged for this exact instruction, not
measured from this illustrative re-run image (see caption note below --
same distinction new_c_langsam_coverage.py itself draws for the same image).

Object choice: knife, not mug. Spec prefers an object that also appears in
hardware trials (mug) if it shows the effect as clearly -- it does not: the
mug's only documented perception failure at this location in the pipeline is
an evidence-gate NOISE refusal (part_adaptive.py, insufficient points), a
different failure mode from "returns a mask that is nearly the whole
object". The knife's LangSAM-collapse case is the one actually measured and
logged for this phenomenon. Object identity is stated in the caption per
spec sec "Fig 1.2" instruction for this exact situation.

Sources:
  workspace/constraints_knife_pick.json               (real, root)
  workspace/run_knife_pick2.log                        (real, root; line 62)
  workspace/report_assets\\figures_live\\langsam_overlay_knife_pick.png (real, live run)
  intent_grasp/visual_grounding.py:429-437                (coverage formula: part_px/obj_px)

Run: python figures/dissertation/fig_1_2_granularity_gap.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

import _qa as qa
import _style as fs

FIGURE_ID = "fig_1_2_granularity_gap"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
CONSTRAINTS_PATH = os.path.join(DATA_ROOT, "constraints_knife_pick.json")
LOG_PATH = os.path.join(DATA_ROOT, "run_knife_pick2.log")
OVERLAY_PATH = os.path.join(DATA_ROOT, "report_assets", "figures_live", "langsam_overlay_knife_pick.png")

MEASURED_COVERAGE_PCT = 97  # verbatim from run_knife_pick2.log line 62, re-checked below at runtime

INTENT = ("Asked for the handle specifically, the perception system returns a mask that is "
          "97% of the whole object -- it did not find a part.")

CAPTION = (
    "Fig 1.2. The granularity gap, knife, \"pick up the knife\". (a) The reasoning layer's own "
    "logged output for this capture: a specific semantic part request. (b) LangSAM's real, "
    "unmodified returned box for that request -- there is only one visible box because the "
    "returned \"part\" box and the whole-object detection box coincide almost exactly: {pct}% "
    "of the whole-object mask, logged verbatim by visual_grounding.py's own collapse warning "
    "(coverage = returned-part-mask pixels / whole-object-mask pixels, "
    "visual_grounding.py:432-436). The single box IS the finding -- a part query and an object "
    "query returned nearly the same region. The reasoning layer can be more specific than the "
    "measurable visual grounding actually available to the robot. Image is a live re-run of the "
    "same instruction/capture (illustrative, ~98% by its own re-measurement); the cited {pct}% "
    "is run_knife_pick2.log's own original logged value for this instruction."
).format(pct=MEASURED_COVERAGE_PCT)


def _load_reasoning():
    with open(CONSTRAINTS_PATH) as f:
        return json.load(f)


def _verify_logged_coverage():
    with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
        for line in f:
            if "collapsed to whole object" in line:
                pct = int(line.split("(")[1].split("%")[0])
                return pct, line.strip()
    raise RuntimeError(f"collapse warning line not found in {LOG_PATH}")


def _panel_a(ax, reasoning):
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    steps = [
        ("instruction", f'"{reasoning["instruction"]}"'),
        ("target_object", reasoning["target_object"]),
        ("target_part", reasoning["target_part"]),
    ]
    y = 0.90
    box_h = 0.20
    for i, (k, v) in enumerate(steps):
        colour = fs.semantic_colour("reasoning")
        ax.add_patch(plt.Rectangle((0.08, y - box_h), 0.84, box_h * 0.82,
                                    facecolor=colour, alpha=0.12, edgecolor=colour, linewidth=1.0))
        ax.text(0.12, y - box_h * 0.20, k, fontsize=8, color=colour, fontweight="bold", va="top")
        ax.text(0.12, y - box_h * 0.56, v, fontsize=9.5, color=fs.OKABE_ITO["black"], va="top")
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((0.5, y - box_h), (0.5, y - box_h - 0.06),
                                          arrowstyle="-|>", mutation_scale=9,
                                          color=fs.OKABE_ITO["black"], linewidth=1.0))
        y -= box_h + 0.06
    ax.text(0.5, 0.02, "source: constraints_knife_pick.json (real, logged)",
             fontsize=7, ha="center", color=fs.OKABE_ITO["black"], alpha=0.7)
    fs.panel_label(ax, "a")


def _panel_b(ax, pct):
    img = mpimg.imread(OVERLAY_PATH)
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Only one box is visible because the returned "part" box and the
    # whole-object box coincide -- that coincidence is the finding, so it is
    # annotated directly on the image, not left for the caption to explain.
    h, w = img.shape[0], img.shape[1]
    ax.annotate(f"one box only: \"part\" box = whole-object box ({pct}% overlap)",
                xy=(0.72 * w, 0.70 * h), xytext=(0.5, -0.09), textcoords="axes fraction",
                fontsize=8, ha="center", va="top", color=fs.OKABE_ITO["black"],
                arrowprops=dict(arrowstyle="-", shrinkA=0, shrinkB=3, lw=0.9,
                                 color=fs.OKABE_ITO["black"]))
    ax.text(0.5, -0.16, f"logged value: {pct}% (run_knife_pick2.log)", transform=ax.transAxes,
             ha="center", va="top", fontsize=7.5, color=fs.OKABE_ITO["black"], alpha=0.75)
    fs.panel_label(ax, "b")


def build():
    reasoning = _load_reasoning()
    pct, log_line = _verify_logged_coverage()
    assert pct == MEASURED_COVERAGE_PCT, f"logged coverage {pct}% does not match module constant {MEASURED_COVERAGE_PCT}%"

    fig, axes = plt.subplots(1, 2, figsize=(fs.TEXT_WIDTH_IN, 3.1), gridspec_kw=dict(width_ratios=[1, 1.3]))
    _panel_a(axes[0], reasoning)
    _panel_b(axes[1], pct)
    return fig, reasoning, pct, log_line


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources:")
    print(f"  reasoning: {CONSTRAINTS_PATH}")
    print(f"  coverage log: {LOG_PATH}")
    print(f"  overlay image: {OVERLAY_PATH}")
    fig, reasoning, pct, log_line = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    print(f"[{FIGURE_ID}] reasoning: {reasoning}")
    print(f"[{FIGURE_ID}] logged coverage line: {log_line}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("A")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
