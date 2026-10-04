"""
fig13_pipeline_summary.py -- Figure 13: Pipeline Summary (hero overview).

Scientific question: how do Figures 1-12 compose one coherent, end-to-end
pipeline?
Scientific claim: the preceding figures compose one coherent, end-to-end
real pipeline, from real sensor acquisition through to a real verified
outcome and its real documented failure modes.
Supporting evidence: this figure introduces no new experimental data --
  every tile is a real, automatically cropped thumbnail of that figure's
  own already-rendered PNG (generated_assets/fig0N/...), not a generic
  icon, so each stage visibly shows the actual content it stands for.
Required real data: none new (purely compositional/derived). The thumbnail
  crop (a fixed content band that excludes each figure's title/caption
  text, derived the same way for every figure from figstyle's shared
  layout convention) is a mechanical derivation of already-real pixels,
  not a fabrication.
Required diagrammatic elements: this entire figure is a diagram by
  construction (a pipeline flow chart) -- it does not itself carry any
  additional evidentiary weight beyond what Figures 1-12 already
  established, and is captioned as such. Arrows and the final "REAL
  HARDWARE -> VERIFIED RESULT" badge are schematic composition, not data.

Run: python fig13_pipeline_summary.py [--exp-dir DIR]
Output: generated_assets/fig13/fig13_pipeline_summary.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

import figstyle as fs
import fig_data as fd

# (figure number, relative PNG path, short stage title)
STAGES = [
    (1, "fig01/fig01_acquisition.png", "Scene Acquisition"),
    (2, "fig02/fig02_grounding.png", "Grounding"),
    (3, "fig03/fig03_segmentation.png", "Segmentation"),
    (4, "fig04/fig04_pointcloud.png", "Point Cloud"),
    (5, "fig05/fig05_affordance_reasoning.png", "Affordance"),
    (6, "fig06/fig06_grasp_candidates.png", "Grasp Candidates"),
    (7, "fig07/fig07_filtering.png", "Feasibility Filter"),
    (8, "fig08/fig08_motion_planning.png", "Motion Planning"),
    (9, "fig09/fig09_execution_sequence.png", "Execution Gates"),
    (10, "fig10/fig10_visual_servo.png", "Visual Servo"),
    (11, "fig11/fig11_successful_experiment.png", "Successful Grasp"),
    (12, "fig12/fig12_failure_analysis.png", "Failure Analysis"),
]

# Content band shared by every figure in this set (figstyle's title sits
# above ~0.86 and the caption block sits below ~0.10) -- cropping to this
# band keeps each thumbnail's actual visual content and drops the (at
# thumbnail scale, illegible) title/caption text.
CONTENT_Y0, CONTENT_Y1 = 0.09, 0.87


def _thumbnail(png_path):
    img = mpimg.imread(png_path)
    h = img.shape[0]
    return img[int(CONTENT_Y0 * h):int(CONTENT_Y1 * h), :, :]


def _row(fig, stages, y, h, row_gap=0.010):
    n = len(stages)
    w = (0.94 - (n - 1) * row_gap) / n
    xs = [0.03 + i * (w + row_gap) for i in range(n)]
    for x, (num, rel_path, title) in zip(xs, stages):
        png_path = os.path.join(fs.ASSET_ROOT, rel_path)
        ax = fig.add_axes([x, y, w, h])
        ax.imshow(_thumbnail(png_path))
        ax.axis("off")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False,
                                edgecolor=fs.FAINT, linewidth=1.0))
        fig.text(x + w / 2, y - 0.018, f"Fig {num}", ha="center", va="top",
                  color=fs.MUTED, fontsize=8.5, weight="bold", family=fs.FONT)
        fig.text(x + w / 2, y - 0.036, title, ha="center", va="top",
                  color=fs.MUTED, fontsize=7.6, family=fs.FONT)
    return xs, w


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("fig13"), "fig13_pipeline_summary.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 13 -- Pipeline Summary", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "One coherent, end-to-end real pipeline -- every tile is that figure's own real render, "
              "no new data introduced", **fs.BODY)

    row1 = STAGES[:6]
    row2 = STAGES[6:]
    y1, y2, h = 0.62, 0.34, 0.21
    xs1, w1 = _row(fig, row1, y1, h)
    xs2, w2 = _row(fig, row2, y2, h)

    # Row-wrap arrow: end of row 1 (Fig 6) down to start of row 2 (Fig 7).
    fig.add_artist(FancyArrowPatch((xs1[-1] + w1 / 2, y1 - 0.045), (xs2[0] + w2 / 2, y2 + h + 0.005),
                                    transform=fig.transFigure, color=fs.MUTED, linewidth=1.6,
                                    arrowstyle="-|>", mutation_scale=16,
                                    connectionstyle="arc3,rad=0.25"))

    badge_y, badge_h = 0.15, 0.10
    fig.add_artist(FancyArrowPatch((xs2[-1] + w2 / 2, y2 - 0.045), (xs2[-1] + w2 / 2, badge_y + badge_h + 0.01),
                                    transform=fig.transFigure, color=fs.ACCEPTED, linewidth=1.8,
                                    arrowstyle="-|>", mutation_scale=18))

    ax_badge = fig.add_axes([0.03, badge_y, 0.94, badge_h])
    ax_badge.axis("off")
    ax_badge.add_patch(Rectangle((0, 0), 1, 1, transform=ax_badge.transAxes, fill=False,
                                  edgecolor=fs.ACCEPTED, linewidth=2.0))
    ax_badge.text(0.5, 0.5, "REAL HARDWARE -> VERIFIED RESULT", transform=ax_badge.transAxes,
                  ha="center", va="center", color=fs.ACCEPTED, fontsize=17, weight="bold", family=fs.FONT)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Each tile is a real, automatically cropped thumbnail of that figure's own rendered PNG (same "
              "content band for every figure) -- not a generic icon. Fig 1-6: perception + affordance +",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "grasp generation. Fig 7-12: feasibility, planning, and real hardware execution. This figure "
              "carries no evidence beyond what Figures 1-12 already established.",
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
    print(f"fig13 written to {path}")
