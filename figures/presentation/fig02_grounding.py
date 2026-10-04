"""
fig02_grounding.py -- Figure 2: Grounding.

Scientific question: does language grounding correctly localize the
requested object and part from a natural-language instruction?
Scientific claim: grounding on the real capture produces a real, non-trivial
object mask and part label consistent with the given instruction.
Supporting evidence: Experiment_Logs/2026-08-07/grasps_out.npz.
Required real data: instruction, target_object, target_part, grounding_rgb,
  object_mask -- all used directly.
Required diagrammatic elements: the bounding box is a real geometric
  derivation (tight bbox of object_mask) -- no bbox was stored separately,
  so none is invented. No scalar grounding-confidence value was logged for
  this run; rather than fabricate one, this figure omits a confidence
  readout and states that fact in its caption.

Run: python fig02_grounding.py [--exp-dir DIR]
Output: generated_assets/fig02/fig02_grounding.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figstyle as fs
import fig_data as fd


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    g = fd.load_grounding(exp_dir)
    x0, y0, x1, y1 = fd.mask_bbox(g.object_mask)
    out_path = out_path or os.path.join(fs.asset_dir("fig02"), "fig02_grounding.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 2 -- Grounding", **fs.TITLE, x=fs.MARGIN, ha="left")

    ax = fig.add_axes([0.06, 0.12, 0.60, 0.75])
    ax.imshow(g.rgb)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                            edgecolor=fs.ACCEPTED, linewidth=2.0))
    # Low alpha (was 0.30) -- spec Sec 4 requires the real mug's own colour to
    # stay visible; 0.30 of a saturated green fill was turning a red mug
    # olive-brown, which reads as recoloring even though it's technically a
    # separate RGBA layer.
    ax.imshow(fs.mask_overlay(g.object_mask, fs.ACCEPTED, alpha=0.12))
    ax.axis("off")
    ax.set_title(f'target_object="{g.target_object}"   target_part="{g.target_part}"',
                 **fs.SECTION)

    ax_info = fig.add_axes([0.70, 0.12, 0.26, 0.75])
    # set_facecolor() on an axis() == "off" axes never paints (the axes
    # patch itself is suppressed) -- an explicit Rectangle in axes-fraction
    # coordinates is what actually renders the callout background.
    ax_info.add_patch(Rectangle((0, 0), 1, 1, transform=ax_info.transAxes,
                                 facecolor=fs.CALLOUT_BG, edgecolor="none", zorder=0))
    ax_info.axis("off")
    info = (f'Instruction:\n"{g.instruction}"\n\n'
            f"Grounded object mask: {int(g.object_mask.sum())} px\n"
            f"Bounding box: ({x0},{y0})-({x1},{y1})\n\n"
            f"No scalar grounding-confidence value was logged for this run.")
    ax_info.text(0.05, 0.92, info, transform=ax_info.transAxes, va="top", ha="left",
                  **fs.BODY, wrap=True)

    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Bounding box derived geometrically from the real object mask "
              "(grasps_out.npz); not a separately stored detection box.",
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
    print(f"fig02 written to {path}")
