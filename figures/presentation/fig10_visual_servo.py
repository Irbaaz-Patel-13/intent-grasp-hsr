"""
fig10_visual_servo.py -- Figure 10: Visual Servo Error Reduction.

Scientific question: does online visual feedback measurably reduce
image-space grasp misalignment?
Scientific claim: a real empirical Jacobian, bootstrapped from measured
odometry displacement and refined by an explicit Broyden update each
iteration, reduces real image-space pixel error. This is an ERROR-REDUCTION
figure, not a trajectory figure -- no continuous per-iteration convergence
curve exists anywhere in the evidence (docs/evidence/
FIGURES_8_13_EVIDENCE_AUDIT.md, Figure 10 section, confirmed by explicit
search of scripts/robot/: no per-iteration log, no x/y
error history, no time-series, no trial-9 image sequence, no trial-9
before/after photo pair). The figure therefore shows exactly two measured
endpoints for trial 9 (46.9px, 12.7px), never an interpolated or sampled
path between them.

Supporting evidence: trials.csv (trial 9: "servo 46.9->12.7px + lift
  patch"; trial 12: "servo residual 17.4px (~12mm)"); DEMO_RUNBOOK.md
  ("Servo: 47 -> 13 px (~9mm) in four iterations" -- a general aggregate,
  explicitly not this specific trial); one REAL hand-camera debug
  photograph (workspace/robot_runs/run_0712_servo_
  session/final_center_debug.png), displaying the pipeline's own real "+"
  grasp-target / "x" detected-object pixel markers, baked into the photo
  by the pipeline itself (not synthesized by this figure). It is a single
  final frame from a session other than trial 9 and is labeled
  "illustrative measurement frame (not trial 9)" -- it demonstrates what
  the measurement looks like, not the 46.9/12.7 values themselves, which
  it cannot: neither photo's marker separation matches either number, and
  no scale bar exists to make 12.7px legible at photographic scale.

Required real data: trial 9's before/after pixel error, trial 12's
  residual, one real photograph, all used directly and unmodified. The
  reduction percentage is a direct arithmetic derivation of the two real
  trial-9 numbers (category B). The dominant panel's dot-pair schematic
  places the target/detected markers at a horizontal spacing exactly
  proportional to the real 46.9px and 12.7px values on one shared pixel
  axis (not arbitrary spacing) -- a to-scale diagram of a measured
  quantity, not an illustration of motion.

Required diagrammatic elements: NONE presented as a convergence trace, a
  curved path, or a time series. No plot()/linspace/arange-based
  interpolation appears anywhere in this file. The single real photo is
  never positioned to imply it is a before/after pair or that it belongs
  to trial 9.

Run: python fig10_visual_servo.py [--exp-dir DIR]
Output: generated_assets/fig10/fig10_visual_servo.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle

import figstyle as fs
import fig_data as fd

PHOTO_SUCCESS = os.path.join(
    fd.HERE, "robot_runs",
    "run_0712_servo_session", "final_center_debug.png")
PHOTO_FAILURE = os.path.join(
    fd.HERE, "robot_runs",
    "run_0710_1521_center_fail", "final_center_debug.png")

TRIAL9_BEFORE_PX, TRIAL9_AFTER_PX = 46.9, 12.7
TRIAL12_RESIDUAL_PX = 17.4
PX_TICKS = [0, 10, 20, 30, 40, 50]


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("fig10"), "fig10_visual_servo.png")
    reduction_pct = (TRIAL9_BEFORE_PX - TRIAL9_AFTER_PX) / TRIAL9_BEFORE_PX * 100.0

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 10 -- Visual Servo Error Reduction", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Visual servoing reduced image-space pixel error (trial 9, real; two measured endpoints)",
              **fs.BODY)

    # -- PRIMARY: the real 46.9px -> 12.7px reduction, as a
    # number-arrow-number statement. Two disconnected endpoints, no path.
    ax_hero = fig.add_axes([0.0, 0.72, 1.0, 0.13])
    ax_hero.set_xlim(0, 1)
    ax_hero.set_ylim(0, 1)
    ax_hero.axis("off")
    ax_hero.text(0.34, 0.55, f"{TRIAL9_BEFORE_PX:.1f}px", ha="center", va="center",
                 color=fs.CANDIDATE, fontsize=44, weight="bold", family=fs.FONT)
    ax_hero.text(0.34, 0.15, "before servo", ha="center", va="center",
                 color=fs.MUTED, fontsize=11, family=fs.FONT)
    ax_hero.add_patch(FancyArrowPatch((0.44, 0.55), (0.56, 0.55), color=fs.ACCEPTED,
                                       linewidth=3.0, arrowstyle="-|>", mutation_scale=26))
    ax_hero.text(0.50, 0.80, f"-{reduction_pct:.0f}%", ha="center", va="center",
                 color=fs.ACCEPTED, fontsize=15, weight="bold", family=fs.FONT)
    ax_hero.text(0.66, 0.55, f"{TRIAL9_AFTER_PX:.1f}px", ha="center", va="center",
                 color=fs.ACCEPTED, fontsize=44, weight="bold", family=fs.FONT)
    ax_hero.text(0.66, 0.15, "after servo", ha="center", va="center",
                 color=fs.MUTED, fontsize=11, family=fs.FONT)

    # -- PRIMARY (continued): to-scale schematic proving the reduction is
    # real spacing, not an arbitrary illustration. SECONDARY: what is
    # measured (target pixel, detected centroid, error vector). Two
    # discrete rows on one shared pixel axis -- explicitly not a path.
    ax_sch = fig.add_axes([0.12, 0.53, 0.76, 0.16])
    ax_sch.set_facecolor(fs.SLIDE_BG)
    ax_sch.set_xlim(-8, 58)
    ax_sch.set_ylim(-0.15, 1.25)
    for spine in ("top", "right", "left"):
        ax_sch.spines[spine].set_visible(False)
    ax_sch.spines["bottom"].set_color(fs.MUTED)
    ax_sch.set_yticks([])
    ax_sch.set_xticks(PX_TICKS)
    ax_sch.tick_params(axis="x", colors=fs.MUTED, labelsize=8)
    ax_sch.set_xlabel("image-space pixel distance from grasp target (px)", color=fs.MUTED,
                       fontsize=9, family=fs.FONT)
    ax_sch.text(25, 1.15, "+  target pixel        x  detected centroid", ha="center", va="center",
                color=fs.MUTED, fontsize=8.5, family=fs.FONT)

    def dim_row(y, value, color, label):
        ax_sch.add_line(Line2D([0, value], [y, y], color=color, linewidth=1.6))
        ax_sch.add_line(Line2D([0, 0], [y - 0.06, y + 0.06], color=color, linewidth=1.2))
        ax_sch.add_line(Line2D([value, value], [y - 0.06, y + 0.06], color=color, linewidth=1.2))
        ax_sch.scatter([0], [y], marker="+", s=170, color=fs.INK, linewidths=1.8, zorder=3)
        ax_sch.scatter([value], [y], marker="x", s=110, color=color, linewidths=1.8, zorder=3)
        ax_sch.text(value / 2.0, y + 0.14, f"{value:.1f} px", ha="center", va="center",
                    color=color, fontsize=11, weight="bold", family=fs.FONT)
        ax_sch.text(-7, y, label, ha="left", va="center", color=fs.MUTED, fontsize=9, family=fs.FONT)

    dim_row(0.85, TRIAL9_BEFORE_PX, fs.CANDIDATE, "before")
    dim_row(0.25, TRIAL9_AFTER_PX, fs.ACCEPTED, "after")

    # -- TERTIARY: one real camera frame, illustrative of the measurement
    # method only. Not trial 9, not positioned as a before/after pair.
    ax_photo = fig.add_axes([0.045, 0.09, 0.34, 0.30])
    ax_photo.imshow(mpimg.imread(PHOTO_SUCCESS))
    ax_photo.axis("off")
    ax_photo.set_title("Illustrative measurement frame (not trial 9)", color=fs.MUTED,
                        fontsize=10, style="italic", family=fs.FONT)

    # -- FOOTNOTE: mechanism + secondary trials, visually subordinate.
    ax_sup = fig.add_axes([0.43, 0.09, 0.525, 0.30])
    ax_sup.set_xlim(0, 1)
    ax_sup.set_ylim(0, 1)
    ax_sup.axis("off")
    ax_sup.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax_sup.transAxes,
                                facecolor=fs.CALLOUT_BG, edgecolor=fs.FAINT, linewidth=1.0))
    ax_sup.text(0.05, 0.88, "Mechanism", color=fs.INK, fontsize=11, weight="bold", family=fs.FONT)
    ax_sup.text(0.05, 0.76, "Empirical Jacobian visual servoing (Broyden update)\nhsr_final_center.py",
                color=fs.MUTED, fontsize=9.5, family=fs.FONT, va="top")
    ax_sup.text(0.05, 0.56, "Trial 12 (real)", color=fs.INK, fontsize=11, weight="bold", family=fs.FONT)
    ax_sup.text(0.05, 0.44, f"residual {TRIAL12_RESIDUAL_PX}px (~12mm), v-axis limited by base deadband",
                color=fs.MUTED, fontsize=9.5, family=fs.FONT, va="top")
    ax_sup.text(0.05, 0.26, "DEMO_RUNBOOK aggregate example (not trial 9)", color=fs.INK, fontsize=11,
                weight="bold", family=fs.FONT)
    ax_sup.text(0.05, 0.14, "\"47 -> 13px (~9mm) in four iterations\"", color=fs.MUTED, fontsize=9.5,
                family=fs.FONT, style="italic", va="top")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Two measured endpoints, trial 9 (real) -- no per-iteration log, no x/y error history, no "
              "time-series, and no trial-9 photo exist, so none is shown or interpolated. The dot-pair",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "schematic above is to scale on one shared pixel axis. The photo is a real frame from a "
              "different session, shown only to illustrate the target/detected pixel measurement.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig10 written to {path}")
