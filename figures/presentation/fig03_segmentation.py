"""
fig03_segmentation.py -- Figure 3: Segmentation.

Scientific question: once grounded, is the target object cleanly separated
from the background at the pixel level?
Scientific claim: segmentation of the real capture produces a clean,
contiguous object silhouette suitable for downstream 3D reconstruction.
Supporting evidence: Experiment_Logs/2026-08-07/grasps_out.npz (object_mask),
  applied to the same grounding_rgb frame as Figure 2.
Required real data: object_mask, grounding_rgb.
Required diagrammatic elements: none for the pixel content -- every pixel
  shown is either the real photo or a real mask derived from it. The three
  panels ARE cropped to the mask's bounding box (fd.mask_bbox) plus a fixed
  20px pad, rather than showing the full 640x480 frame -- this is a real,
  deterministic derivation from the real mask (same bbox function Figure 2
  uses), done because the object is only ~1.2% of the full frame and is
  illegibly small at presentation scale otherwise. Never invents a boundary
  beyond the real mask's own extent plus the stated pad.

Run: python fig03_segmentation.py [--exp-dir DIR]
Output: generated_assets/fig03/fig03_segmentation.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs
import fig_data as fd

CROP_PAD_PX = 20


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    g = fd.load_grounding(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig03"), "fig03_segmentation.png")

    mask = g.object_mask
    cutout = g.rgb.copy()
    cutout[~mask] = 0
    silhouette = np.zeros((*mask.shape, 3), dtype=np.uint8)
    ink_rgb = tuple(int(c * 255) for c in matplotlib.colors.to_rgb(fs.INK))
    silhouette[mask] = ink_rgb

    x0, y0, x1, y1 = fd.mask_bbox(mask)
    h, w = mask.shape
    cx0, cy0 = max(x0 - CROP_PAD_PX, 0), max(y0 - CROP_PAD_PX, 0)
    cx1, cy1 = min(x1 + CROP_PAD_PX, w), min(y1 + CROP_PAD_PX, h)
    mask_crop = mask[cy0:cy1, cx0:cx1]
    cutout_crop = cutout[cy0:cy1, cx0:cx1]
    silhouette_crop = silhouette[cy0:cy1, cx0:cx1]

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 3 -- Segmentation", **fs.TITLE, x=fs.MARGIN, ha="left")

    panels = [("Pixel Mask", mask_crop.astype(float), "gray"),
              ("Extracted Object", cutout_crop, None),
              ("Silhouette", silhouette_crop, None)]
    width = 0.28
    for i, (title, img, cmap) in enumerate(panels):
        ax = fig.add_axes([0.05 + i * (width + 0.02), 0.15, width, 0.72])
        ax.imshow(img, cmap=cmap)
        ax.set_title(title, **fs.SECTION)
        ax.axis("off")

    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"{int(mask.sum())} object px of {mask.size} total "
              f"({100 * mask.sum() / mask.size:.1f}%); background removed, not recolored. "
              f"Panels cropped to the mask's bounding box +{CROP_PAD_PX}px pad for legibility.",
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
    print(f"fig03 written to {path}")
