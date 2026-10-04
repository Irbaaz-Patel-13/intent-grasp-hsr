"""
fig07_filtering.py -- Figure 7: Grasp Feasibility.

Scientific question: does the selected grasp candidate satisfy the robot's
actual manipulability requirement -- i.e. is it kinematically robust enough
to execute, not merely collision-free?
Scientific claim: candidate 24 (the one executed on real hardware) has the
maximum real manipulability (0.17484) among all 25 real candidates, well
above the real hsr_preflight.py C4 gate threshold (manip_min=0.10). This
figure does NOT show a progressive filtering funnel -- the audit
(docs/evidence/FIGURES_5_7_EVIDENCE_AUDIT.md) confirmed collision_free and
arm_only_ok are constant (all 25 candidates pass) for this trial, so no
candidate rejection is visible in the real data, and clearance_m is a
constant sentinel (9.0), not a real measured clearance value.
Supporting evidence: Experiment_Logs/2026-08-07/place_run.csv (via
  fig_data.load_grasp_candidates); scripts/robot/
  hsr_preflight.py (C4 manipulability gate, manip_min=0.10 default,
  re-verified against source: "if m>=a.manip_min: ... OK ... else: ... WARN
  ... near-singular, fragile").
Required real data: manip (all 25 candidates, real, varying
  0.0402-0.17484), collision_free, arm_only_ok -- used directly.
Required diagrammatic elements: none for the plotted content -- every
  point is a real manip value. MANIP_MIN_THRESHOLD below is implementation
  evidence (a real code constant, not itself a per-trial measurement) and
  is labeled as such in the caption.

Run: python fig07_filtering.py [--exp-dir DIR]
Output: generated_assets/fig07/fig07_filtering.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs
import fig_data as fd

EXECUTED_CANDIDATE = 24
# hsr_preflight.py C4 gate default, scripts/robot/hsr_preflight.py:90 --
# real code constant (implementation evidence), not a per-trial measurement.
MANIP_MIN_THRESHOLD = 0.10


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    gc = fd.load_grasp_candidates(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig07"), "fig07_filtering.png")

    n = len(gc.manip)
    idx = np.arange(n)
    above = gc.manip >= MANIP_MIN_THRESHOLD
    n_below = int((~above).sum())

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 7 -- Grasp Feasibility", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Does the selected grasp satisfy the robot's actual manipulability requirement?",
              **fs.BODY)

    ax = fig.add_axes([0.07, 0.16, 0.86, 0.62])
    ax.set_facecolor(fs.SLIDE_BG)
    bar_colors = [fs.ACCEPTED if a else fs.CANDIDATE for a in above]
    ax.bar(idx, gc.manip, color=bar_colors, width=0.65, zorder=2)
    ax.axhline(MANIP_MIN_THRESHOLD, color=fs.INK, linewidth=1.4, linestyle="--", zorder=3)
    ax.text(n - 0.4, MANIP_MIN_THRESHOLD + 0.004,
            f"manip_min = {MANIP_MIN_THRESHOLD:.2f}  (hsr_preflight.py C4 gate)",
            color=fs.INK, fontsize=9, ha="right", va="bottom", family=fs.FONT)

    ex_manip = gc.manip[EXECUTED_CANDIDATE]
    ax.scatter([EXECUTED_CANDIDATE], [ex_manip], s=220, facecolor="none",
               edgecolor=fs.INK, linewidth=2.2, zorder=4)
    ax.annotate(f"Executed: #{EXECUTED_CANDIDATE}\nmanip={ex_manip:.3f}",
                xy=(EXECUTED_CANDIDATE, ex_manip), xytext=(EXECUTED_CANDIDATE - 6, ex_manip + 0.035),
                color=fs.INK, fontsize=10, family=fs.FONT,
                arrowprops=dict(arrowstyle="-", color=fs.MUTED, linewidth=1.0))

    ax.set_xlabel("candidate index", **fs.BODY)
    ax.set_ylabel("manipulability (real, place_run.csv)", **fs.BODY)
    ax.set_xlim(-1, n)
    ax.set_ylim(0, max(gc.manip.max() * 1.25, MANIP_MIN_THRESHOLD * 1.5))
    ax.tick_params(colors=fs.MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)

    legend_x = 0.07
    ax_leg = fig.add_axes([legend_x, 0.80, 0.5, 0.05])
    ax_leg.axis("off")
    ax_leg.add_patch(plt.Rectangle((0, 0.3), 0.02, 0.4, color=fs.ACCEPTED, transform=ax_leg.transAxes))
    ax_leg.text(0.03, 0.3, f"at/above threshold ({n - n_below}/{n})", transform=ax_leg.transAxes,
                **fs.CAPTION, va="bottom")
    ax_leg.add_patch(plt.Rectangle((0.32, 0.3), 0.02, 0.4, color=fs.CANDIDATE, transform=ax_leg.transAxes))
    ax_leg.text(0.35, 0.3, f"below threshold ({n_below}/{n})", transform=ax_leg.transAxes,
                **fs.CAPTION, va="bottom")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              f"collision_free/arm_only_ok are constant (1) for all 25 real candidates -- not shown "
              f"as filters here. clearance_m is a constant sentinel (9.0), not a real measured clearance.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"Selected grasp = candidate {EXECUTED_CANDIDATE} (manip={ex_manip:.3f}, the real maximum).",
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
    print(f"fig07 written to {path}")
