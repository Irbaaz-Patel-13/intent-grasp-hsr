"""
new_slide13_perception.py -- Slide 13: Perception / Part Grounding.

Purpose: unify NEW-C (mask-coverage collapse) and NEW-D (method disagreement)
under one argument -- both independently expose the SAME perception-layer
weakness: object identification works, part grounding does not.

Scientific claim: unchanged from NEW-C/NEW-D -- this figure re-presents their
already-verified real numbers under a shared framing, it does not derive new
values. LangSAM part masks collapse to 86-97% of the whole-object box (6
real live runs, 2 objects); 3 independent part-naming methods disagree on
9/9 real object/instruction pairs (0 fully agree on the example row shown).
Required real data: RUNS list (new_c_langsam_coverage.py, real, unchanged);
  PART_NAMING_ABLATION.csv row via new_d_method_disagreement.load_grid()
  (real, unchanged). Real images: report_assets/figures_live/
  langsam_overlay_knife_pick.png (real live LangSAM run, this session);
  report_assets/figures/fig_stage3b_som_knife_pick.png,
  fig_stage3c_point_knife_pick.png (real, pre-existing).

Run: python new_slide13_perception.py
Output: report_assets/figures/slide13_perception.png
"""
import argparse
import collections
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

import figlayout as fl
import figstyle as fs
import new_c_langsam_coverage as fig_c
import new_d_method_disagreement as fig_d

C_IMAGE = os.path.join("report_assets", "figures_live", "langsam_overlay_knife_pick.png")
C_PCT = fig_c.RUNS[0][2]  # knife/pick, 97 -- same real headline new_c_langsam_coverage.py cites


def render(out_path=None):
    out_path = out_path or os.path.join("report_assets", "figures", "slide13_perception.png")
    pairs, grid = fig_d.load_grid()
    vals = grid[(fig_d.SLIDE_OBJECT, fig_d.SLIDE_INSTRUCTION)]
    # "agree" = size of the largest group of methods that returned the
    # IDENTICAL answer (1 if all 3 differ, up to 3 if all 3 match) -- not
    # the count of distinct answers, which reads backwards ("3/3" looked
    # like unanimous agreement when the real result is zero agreement).
    counts = collections.Counter(vals.values())
    max_agree = counts.most_common(1)[0][1]
    # "1/3" (no two methods share an answer) reads ambiguously as a
    # headline -- state it the same way NEW-D itself does: "0 agree".
    agree_display = max_agree if max_agree > 1 else 0

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("The Object Is Found -- the Part Is Not", **fs.TITLE, x=fs.MARGIN, ha="left")

    # -- two-stage banner: OBJECT ID (check) -> PART GROUNDING (cross)
    ax_banner = fig.add_axes([0.03, 0.83, 0.94, 0.09])
    ax_banner.axis("off")
    ax_banner.set_xlim(0, 1)
    ax_banner.set_ylim(0, 1)
    ax_banner.text(0.20, 0.5, "OBJECT IDENTIFICATION", ha="center", va="center", color=fs.INK, fontsize=18,
                   weight="bold", family=fs.FONT)
    ax_banner.text(0.20, 0.05, "reliable (see Slide 12: 61/65)", ha="center", va="bottom", color=fs.MUTED,
                   fontsize=16, family=fs.FONT, style="italic")
    ax_banner.text(0.35, 0.5, "\u2713", ha="center", va="center", color=fs.ACCEPTED, fontsize=32, weight="bold",
                   family=fs.FONT)
    ax_banner.add_patch(FancyArrowPatch((0.40, 0.5), (0.58, 0.5), transform=ax_banner.transAxes, color=fs.MUTED,
                                         linewidth=2.0, arrowstyle="-|>", mutation_scale=20))
    ax_banner.text(0.80, 0.5, "PART GROUNDING", ha="center", va="center", color=fs.INK, fontsize=18,
                   weight="bold", family=fs.FONT)
    ax_banner.text(0.80, 0.05, "does not converge on a physical region", ha="center", va="bottom", color=fs.MUTED,
                   fontsize=16, family=fs.FONT, style="italic")
    ax_banner.text(0.95, 0.5, "\u2717", ha="center", va="center", color=fs.REJECTED, fontsize=32, weight="bold",
                   family=fs.FONT)

    # -- left half: NEW-C condensed (real image + hero %)
    ax_img_c = fig.add_axes([0.03, 0.17, 0.40, 0.57])
    ax_img_c.imshow(mpimg.imread(C_IMAGE))
    ax_img_c.set_xticks([])
    ax_img_c.set_yticks([])
    for spine in ax_img_c.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)
    ax_img_c.set_title("LangSAM \"part\" mask vs. whole-object box", color=fs.INK, fontsize=16, weight="bold",
                       family=fs.FONT, pad=8)
    # Hero number and its caption on separate axes, stacked with a real gap
    # between them -- cramming both into adjacent fig.text calls at the
    # same y-band made the caption run straight through the "%" glyph.
    ax_hero_c = fig.add_axes([0.03, 0.06, 0.40, 0.10])
    ax_hero_c.axis("off")
    ax_hero_c.text(0.0, 0.5, f"{C_PCT}%", color=fs.CANDIDATE, fontsize=48, weight="bold", family=fs.FONT,
                   ha="left", va="center")
    ax_hero_c.text(0.32, 0.5, "of the whole-object box returned\nas the \"part\" (6 real runs: 86-97%)",
                   color=fs.MUTED, fontsize=16, family=fs.FONT, linespacing=1.3, ha="left", va="center")

    # -- right half: NEW-D condensed (real image + hero disagreement stat)
    ax_img_d = fig.add_axes([0.47, 0.17, 0.40, 0.57])
    ax_img_d.imshow(mpimg.imread(fig_d.SLIDE_SOM_IMG), aspect="auto")
    ax_img_d.set_xticks([])
    ax_img_d.set_yticks([])
    for spine in ax_img_d.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)
    ax_img_d.set_title("3 independent methods, same object", color=fs.INK, fontsize=16, weight="bold",
                       family=fs.FONT, pad=8)
    ax_hero_d = fig.add_axes([0.47, 0.06, 0.40, 0.10])
    ax_hero_d.axis("off")
    ax_hero_d.text(0.0, 0.5, f"{agree_display}/3", color=fs.REJECTED, fontsize=48, weight="bold", family=fs.FONT,
                   ha="left", va="center")
    ax_hero_d.text(0.32, 0.5, 'methods agree on "pick up the knife"\n(A/B/C each name a different region)',
                   color=fs.MUTED, fontsize=16, family=fs.FONT, linespacing=1.3, ha="left", va="center")

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "new_c_langsam_coverage.py + new_d_method_disagreement.py",
                               **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("Slide 13 perception", [
        "This slide re-presents NEW-C and NEW-D's already-verified numbers under a shared framing --",
        "no new measurement is made here.",
        "NEW-C: 6 real live part-grounding runs, 2 objects (knife 97/97/97%, remote 88/86/86%) -- the",
        "only 6 real live part-grounding runs logged in this repo. See new_c_langsam_coverage.py for",
        "the full per-run breakdown (report variant).",
        "NEW-D: 9 real object/instruction pairs; 8/9 are full 3-way disagreement. This slide shows the",
        "knife/'pick up the knife' row specifically. See new_d_method_disagreement.py for all 9 rows.",
        "'Object identification reliable' references Slide 12 (NEW-B, 61/65) -- not re-derived here.",
    ])
    return out_path, report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(out_path=args.out)
    print(f"slide13 written to {path}")
    print(report.summary())
