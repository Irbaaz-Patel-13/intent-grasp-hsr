"""
new_c_langsam_coverage.py -- NEW-C: Part-Mask Coverage Collapse.

Scientific claim: on the only 6 live runs where LangSAM part-level text
grounding was actually exercised on a real capture, its returned "part"
mask covers 86-97% of the whole-object detection box -- i.e. it does not
find a part at all, it re-finds the object. The near-coincidence with the
100% reference line IS the finding; the axis is not rescaled to exaggerate
the (already small) gap.
Supporting evidence: run_knife_pick2.log, run_knife_hand.log,
  run_knife_put.log, run_remote_hand.log, run_remote_power.log,
  run_remote_put.log -- each file's own "[VisualGrounder] WARNING: part
  grounding collapsed to whole object (N% of object mask covered)" line.
Required real data: all 6 real percentages, used directly.
Required diagrammatic elements: none.
Scope: two objects, six live runs. Not claimed as a broader sample -- no
  other object has a live part-grounding run logged in this repo.

Run: python new_c_langsam_coverage.py
Output: generated_assets/new_c/new_c_langsam_coverage.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

# object, run identifier, real coverage %, source file
RUNS = [
    ("knife", "pick", 97, "run_knife_pick2.log"),
    ("knife", "hand", 97, "run_knife_hand.log"),
    ("knife", "put", 97, "run_knife_put.log"),
    ("remote", "hand", 88, "run_remote_hand.log"),
    ("remote", "power", 86, "run_remote_power.log"),
    ("remote", "put", 86, "run_remote_put.log"),
]

# Live GroundingDINO+SAM2 overlay, generated this session (visual_grounding
# .VisualAffordanceGrounder.ground()+.visualize_grounding(), real, unmodified
# functions -- no cached overlay pre-existed anywhere in the repo). Object
# mask blue, part/affordance mask red, amber box=whole object, blue
# box=returned "part". See report_assets/figures_live/ for both this and
# the remote-control counterpart.
SLIDE_IMAGE = os.path.join(str(WORKSPACE), "report_assets", "figures_live",
                            "langsam_overlay_knife_pick.png")
SLIDE_PCT = 97  # matches RUNS[0] (knife/pick) -- the headline number this image illustrates


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_c"), "new_c_langsam_coverage.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Part-Mask Coverage Collapse -- Two Objects, Six Live Runs", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "LangSAM's \"part\" mask nearly equals the whole-object box -- it re-finds the object, not a part",
              **fs.BODY)

    ax = fig.add_axes([0.05, 0.16, 0.92, 0.62])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(RUNS) - 0.4)
    ax.invert_yaxis()

    ax.axvline(100, color=fs.INK, linewidth=1.6)
    # Right-aligned and pulled 1.5pt inside the 100% line so the label never
    # overflows the axes into the canvas margin (was clipped at the right
    # edge when centered directly on x=100).
    ax.text(98.5, -0.58, "whole object", ha="right", va="bottom", color=fs.INK, fontsize=10, family=fs.FONT)

    group_color = {"knife": fs.CANDIDATE, "remote": fs.REJECTED}
    for i, (obj, run, pct, src) in enumerate(RUNS):
        color = group_color[obj]
        ax.add_patch(Rectangle((0, i - 0.32), pct, 0.64, facecolor=color, edgecolor="none", alpha=0.85))
        ax.text(2, i, f"{run}: {pct}%", ha="left", va="center", color=fs.SLIDE_BG, fontsize=10.5,
                weight="bold", family=fs.FONT)

    ax.set_yticks(range(len(RUNS)))
    ax.set_yticklabels([obj if i == 0 or RUNS[i - 1][0] != obj else "" for i, (obj, *_ ) in enumerate(RUNS)],
                        color=fs.INK, fontsize=11, weight="bold", family=fs.FONT)
    ax.set_xlabel("part-mask coverage of the whole-object detection box (%)", color=fs.MUTED, fontsize=10,
                  family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)

    # group separator between knife and remote
    ax.axhline(2.5, color=fs.FAINT, linewidth=0.8, linestyle=(0, (2, 2)))

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Source: [VisualGrounder] WARNING lines in run_knife_{pick2,hand,put}.log and "
              "run_remote_{hand,power,put}.log -- the only 6 real live part-grounding runs logged.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Axis is 0-100, unscaled -- bars sitting near the 100% reference line is the finding, "
              "not an artefact of framing.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: lead with the real image -- whole-object box and the
    returned 'part' mask visibly coinciding -- beside the real headline
    number at hero size. Bar chart moves to the report variant only."""
    out_path = out_path or os.path.join(fs.asset_dir("new_c"), "new_c_langsam_coverage_slide.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle('LangSAM "Finds a Part" -- It Re-Finds the Object', **{**fs.TITLE, "size": 32},
                 x=fs.MARGIN, ha="left")

    img = mpimg.imread(SLIDE_IMAGE)
    ax_img = fig.add_axes([0.03, 0.10, 0.60, 0.74])
    ax_img.imshow(img)
    ax_img.set_xticks([])
    ax_img.set_yticks([])
    for spine in ax_img.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)

    ax_num = fig.add_axes([0.66, 0.10, 0.31, 0.74])
    ax_num.axis("off")
    ax_num.text(0.5, 0.56, f"{SLIDE_PCT}%", transform=ax_num.transAxes, ha="center", va="center",
                color=fs.CANDIDATE, fontsize=96, weight="bold", family=fs.FONT)
    ax_num.text(0.5, 0.30, "of the whole-object box\nis what came back as\nthe \"part\" mask",
                transform=ax_num.transAxes, ha="center", va="top", color=fs.INK, fontsize=18,
                weight="bold", family=fs.FONT, linespacing=1.4)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "langsam_overlay_knife_pick.png (live run, this session)",
                               **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-C LangSAM coverage", [
        "6 real live part-grounding runs total (2 objects): knife 97/97/97%, remote 88/86/86%.",
        "Source: [VisualGrounder] WARNING lines in run_knife_{pick2,hand,put}.log and",
        "run_remote_{hand,power,put}.log -- the only 6 real live part-grounding runs logged in this repo.",
        "Scope: two objects, six runs -- not claimed as a broader sample; no other object has a live",
        "part-grounding run logged here.",
        "This image is a fresh live re-run (this session), not one of the original 6 logged runs -- it",
        "reproduces the same collapse behavior (98% here vs. 97% logged) but is illustrative, not the",
        "cited data point. The cited 97% is run_knife_pick2.log's own number.",
        "Axis in the report bar chart is 0-100, unscaled -- bars sitting near the 100% line is the",
        "finding, not a framing artefact.",
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
    print(f"new_c ({args.variant}) written to {path}")
    print(report.summary())
