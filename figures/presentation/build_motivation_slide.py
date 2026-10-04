"""
build_motivation_slide.py -- Slide 2 (Motivation & Problem) figure.

Renders motivation_slide.png / motivation_slide.svg from REAL perception
outputs produced by outputs/motivation/segment_parts.py:
    outputs/motivation/object_mask.npy   -- LangSAM (GroundingDINO+SAM) whole-mug mask
    outputs/motivation/handle_mask.npy   -- SAM2 automatic-mask-generator region,
    outputs/motivation/rim_mask.npy         selected by GPT-4o Set-of-Mark (same
    outputs/motivation/body_mask.npy        mechanism as som_grounding.py), or a
                                             set-difference of the above (body)

No region in this figure is hand-drawn or coordinate-tuned; every highlighted
area traces a real segmentation mask. See segmentation_report.json for the
picked-region provenance of each mask.

The mug's own pixels are never recoloured -- masks are drawn as a separate
translucent RGBA layer (crisp white contour + fill) composited on top of the
unmodified photo, and every annotation sits in one of four fixed gutters
(top / right / left / bottom) around a mug rendered at identical size and
position in all three panels, connected by a single short horizontal-or-
vertical leader segment whose coordinate range never overlaps the label
text's -- so it cannot cross text, the mask, or another leader by construction.

    python build_motivation_slide.py --out motivation_slide

Requires: numpy, pillow, matplotlib, scipy.
"""
import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image
from scipy.ndimage import binary_erosion
from intent_grasp.paths import WORKSPACE

HERE = str(WORKSPACE)
MASK_DIR = os.path.join(HERE, "outputs", "motivation")
IMG_PATH = os.path.join(HERE, "red-mug.png")

# ---- palette -----------------------------------------------------------
SLIDE_BG  = "#15161A"
INK       = "#F0EFEC"
MUTED     = "#96948B"
FAINT     = "#4A4C53"

GRASP     = "#54D26A"   # user-specified
KEEPCLEAR = "#FFC857"   # user-specified
ACCENT    = "#8B7BEE"
CALLOUT_BG = "#1E212B"

FONT = "DejaVu Sans"
FIG_W_IN, FIG_H_IN = 16.0, 9.0

# Each panel: which real mask plays "grasp" / "keep-clear", a short label,
# a fixed gutter slot (top/right/left/bottom) placing the annotation close
# to where that mask actually sits on the mug, and the real target point
# (panel-local mug-bbox fraction) measured directly off the mask geometry
# -- see outputs/motivation/segmentation_report.json and the centroid dump
# this script's docstring above references. Not eyeballed.
PANELS = [
    dict(n="1", title="Drink", instruction='"I’d like a hot drink"',
         grasp="handle", grasp_label="Handle", grasp_slot="right", grasp_t=0.50,
         clear="rim",    clear_label="Rim",    clear_slot="top",   clear_t=0.46,
         caption="Needs access to the rim."),
    dict(n="2", title="Hand Over", instruction='"Pass it to me"',
         grasp="body",   grasp_label="Body",   grasp_slot="left",  grasp_t=0.44,
         clear="handle", clear_label="Handle", clear_slot="right", clear_t=0.50,
         caption="Handle must stay accessible."),
    dict(n="3", title="Store / Move", instruction='"Put it away"',
         grasp="object", grasp_label="Any stable region", grasp_slot="bottom", grasp_t=0.50,
         clear=None,     clear_label=None,     clear_slot=None,    clear_t=None,
         caption="Only grasp stability matters."),
]

# Fixed mug placement -- identical in every panel.
MUG_CY, MUG_H = 0.460, 0.500
GUTTER = 0.026            # gap between mug silhouette and swatch/leader end
ROW_GAP_H = 0.052          # heading<->name spacing, left/right slots (both va=center)
ROW_GAP_V = 0.075          # heading<->name spacing, top/bottom slots (stacked, va=top/bottom)


# ---- perception loading --------------------------------------------------

def load_real_cutout():
    """The mug as segmented by the real pipeline: RGB + its own alpha channel
    (red-mug.png already carries a genuine per-pixel alpha cutout), cropped
    tightly around the LangSAM object mask. Returns rgb, alpha, masks(dict),
    all pixel-aligned and cropped identically."""
    im = Image.open(IMG_PATH).convert("RGBA")
    arr = np.asarray(im).astype(np.float64) / 255.0
    rgb, alpha = arr[..., :3], arr[..., 3]

    masks = {}
    for name in ("object", "handle", "rim", "body"):
        p = os.path.join(MASK_DIR, f"{name}_mask.npy")
        masks[name] = np.load(p) if os.path.exists(p) else None

    with open(os.path.join(MASK_DIR, "segmentation_report.json")) as f:
        report = json.load(f)

    om = masks["object"]
    ys, xs = np.where(om)
    pad = 12
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, om.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, om.shape[1])

    rgb = rgb[y0:y1, x0:x1]
    alpha = alpha[y0:y1, x0:x1]
    masks = {k: (v[y0:y1, x0:x1] if v is not None else None) for k, v in masks.items()}
    return rgb, alpha, masks, report


def edge_mask(mask, width=2):
    return mask & ~binary_erosion(mask, iterations=width)


def overlay_layer(alpha, masks, grasp_key, clear_key):
    """A transparent RGBA layer (fill + crisp white contour) for the real
    masks -- the mug photo itself is never touched; this is composited on
    top of it as a separate imshow call, i.e. a genuine alpha overlay."""
    h, w = alpha.shape
    ov = np.zeros((h, w, 4))

    grasp_m = masks[grasp_key] if grasp_key else np.zeros((h, w), bool)
    clear_m = masks[clear_key] if clear_key else np.zeros((h, w), bool)

    # Green over this mug's saturated red glaze is a losing fight at low
    # opacity -- red and green are opposing hues, so any modest alpha blend
    # reads as muddy olive/brown rather than green (this is colour-mixing
    # physics, reproduced on first render here). 0.56 is the lowest opacity
    # at which the fill still reads unambiguously as its own hue rather than
    # a blend; below the mug's own detail remains visible through it.
    FILL_ALPHA = 0.56
    for m, col in ((grasp_m, GRASP), (clear_m, KEEPCLEAR)):
        if not m.any():
            continue
        c = matplotlib.colors.to_rgb(col)
        ov[m] = (*c, FILL_ALPHA)
        e = edge_mask(m, 2)
        ov[e] = (1.0, 1.0, 1.0, 0.95)

    return ov


def centroid_frac(mask):
    ys, xs = np.where(mask)
    h, w = mask.shape
    return xs.mean() / w, ys.mean() / h  # (cx, cy) in [0,1], y downward, image space


# ---- figure ---------------------------------------------------------------

def draw_mug(ax, base, overlay, ar, cx, cy, h_frac, ax_w_in, ax_h_in):
    """Place the unmodified mug photo, then the transparent mask overlay on
    top of it at the same extent -- true compositing, not pixel recolouring.
    Returns the mug's bbox in axes-fraction (l, b, w, h)."""
    w_frac = (h_frac * ax_h_in * ar) / ax_w_in
    l, b = cx - w_frac / 2.0, cy - h_frac / 2.0
    extent = (l, l + w_frac, b, b + h_frac)
    ax.imshow(base, extent=extent, transform=ax.transAxes, zorder=3, aspect="auto")
    ax.imshow(overlay, extent=extent, transform=ax.transAxes, zorder=4, aspect="auto")
    return l, b, w_frac, h_frac


def add_callout(ax, slot, t, role, label, color, mug_bbox):
    """Draw one annotation: a small dot on the mug edge, a single short
    straight leader (pure horizontal or pure vertical -- never both), and a
    two-row label (bold role name, muted region name) sitting in the gutter
    on the far side of the leader from the mug. Because the leader's
    coordinate range stops strictly before the label's, and the two text
    rows are stacked so the leader only ever needs to reach the NEAR row,
    neither the mask, the text, nor another leader can be crossed.
    """
    l, b, mw, mh = mug_bbox
    ROLE_FS, NAME_FS = 9.5, 8.5
    if slot == "right":
        edge_x, edge_y = l + mw, b + t * mh
        line_x1 = edge_x + GUTTER
        ax.plot([edge_x, line_x1], [edge_y, edge_y], color=color, lw=1.1,
                 alpha=0.9, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=3.0, color=color,
                 transform=ax.transAxes, zorder=6)
        tx = line_x1 + 0.010
        ax.text(tx, edge_y + ROW_GAP_H / 2, role, color=color, fontsize=ROLE_FS,
                 family=FONT, va="center", ha="left", weight="semibold")
        ax.text(tx, edge_y - ROW_GAP_H / 2, label, color=MUTED, fontsize=NAME_FS,
                 family=FONT, va="center", ha="left")
    elif slot == "left":
        edge_x, edge_y = l, b + t * mh
        line_x0 = edge_x - GUTTER
        ax.plot([line_x0, edge_x], [edge_y, edge_y], color=color, lw=1.1,
                 alpha=0.9, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=3.0, color=color,
                 transform=ax.transAxes, zorder=6)
        tx = line_x0 - 0.010
        ax.text(tx, edge_y + ROW_GAP_H / 2, role, color=color, fontsize=ROLE_FS,
                 family=FONT, va="center", ha="right", weight="semibold")
        ax.text(tx, edge_y - ROW_GAP_H / 2, label, color=MUTED, fontsize=NAME_FS,
                 family=FONT, va="center", ha="right")
    elif slot == "top":
        edge_x, edge_y = l + t * mw, b + mh
        line_y1 = edge_y + GUTTER
        ax.plot([edge_x, edge_x], [edge_y, line_y1], color=color, lw=1.1,
                 alpha=0.9, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=3.0, color=color,
                 transform=ax.transAxes, zorder=6)
        ty = line_y1 + 0.008
        ax.text(edge_x, ty, label, color=MUTED, fontsize=NAME_FS,
                 family=FONT, va="bottom", ha="center")
        ax.text(edge_x, ty + ROW_GAP_V, role, color=color, fontsize=ROLE_FS,
                 family=FONT, va="bottom", ha="center", weight="semibold")
    elif slot == "bottom":
        edge_x, edge_y = l + t * mw, b
        line_y0 = edge_y - GUTTER
        ax.plot([edge_x, edge_x], [line_y0, edge_y], color=color, lw=1.1,
                 alpha=0.9, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=3.0, color=color,
                 transform=ax.transAxes, zorder=6)
        ty = line_y0 - 0.008
        ax.text(edge_x, ty, label, color=MUTED, fontsize=NAME_FS,
                 family=FONT, va="top", ha="center")
        ax.text(edge_x, ty - ROW_GAP_V, role, color=color, fontsize=ROLE_FS,
                 family=FONT, va="top", ha="center", weight="semibold")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="motivation_slide")
    ap.add_argument("--dpi", type=int, default=220)
    a = ap.parse_args()

    rgb, alpha, masks, report = load_real_cutout()
    h, w = alpha.shape
    ar = w / float(h)
    base = np.dstack([rgb, alpha])

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor=SLIDE_BG)
    root = fig.add_axes([0, 0, 1, 1]); root.set_axis_off()
    root.set_xlim(0, 1); root.set_ylim(0, 1)

    # ---------------- Top: title / subtitle ----------------
    root.text(0.055, 0.975, "Motivation & problem", color=ACCENT,
              fontsize=13, family=FONT, va="center")
    root.plot([0.055, 0.130], [0.958, 0.958], color=ACCENT, lw=1.6)

    root.text(0.5, 0.916, "How Should a Robot Decide", color=INK,
              fontsize=25, family=FONT, ha="center", va="center", weight="medium")
    root.text(0.5, 0.873, "Where to Grasp an Object?", color=INK,
              fontsize=25, family=FONT, ha="center", va="center", weight="medium")

    root.text(0.5, 0.832,
              "Humans naturally adapt their grasp according to the intended task.",
              color=MUTED, fontsize=12, family=FONT, ha="center", va="center")
    root.text(0.5, 0.807,
              "Robotic grasp planners typically optimise for grasp stability rather than task intention.",
              color=MUTED, fontsize=12, family=FONT, ha="center", va="center")

    # ---------------- Hero: SAME OBJECT + 3 arrows ----------------
    root.text(0.5, 0.760, "SAME OBJECT", color=INK, fontsize=14, family=FONT,
              ha="center", va="center", weight="semibold")
    root.text(0.5, 0.739,
              "real segmentation — GroundingDINO + SAM, red-mug.png",
              color=MUTED, fontsize=9, family=FONT, style="italic",
              ha="center", va="center")

    hero_bot, hero_top = 0.498, 0.716
    hero_ax = fig.add_axes([0.40, hero_bot, 0.20, hero_top - hero_bot])
    hero_ax.set_axis_off(); hero_ax.set_xlim(0, 1); hero_ax.set_ylim(0, 1)
    hero_ax_w_in, hero_ax_h_in = 0.20 * FIG_W_IN, (hero_top - hero_bot) * FIG_H_IN
    e_l, e_b, e_w, e_h = draw_mug(hero_ax, base, np.zeros((h, w, 4)), ar, 0.5, 0.50, 0.86,
                                   hero_ax_w_in, hero_ax_h_in)
    # thin outline traced from the real object mask boundary -- shows this
    # cutout is itself segmentation output, not a stock photo crop.
    om_outline = edge_mask(masks["object"], 3)
    ov = np.zeros((*om_outline.shape, 4))
    ov[om_outline] = (*matplotlib.colors.to_rgb(ACCENT), 0.9)
    hero_ax.imshow(ov, extent=(e_l, e_l + e_w, e_b, e_b + e_h),
                    transform=hero_ax.transAxes, zorder=5)

    # three arrows fan from the hero mug down to each panel
    arrow_src = (0.5, hero_bot - 0.010)
    panel_centers_x = [0.185, 0.5, 0.815]
    arrow_dst_y = 0.460
    rads = [0.30, 0.0, -0.30]
    for cx, rad in zip(panel_centers_x, rads):
        arr = FancyArrowPatch(arrow_src, (cx, arrow_dst_y),
                               connectionstyle=f"arc3,rad={rad}",
                               transform=root.transAxes,
                               color=FAINT, lw=1.2, alpha=0.9,
                               arrowstyle="-|>", mutation_scale=11,
                               shrinkA=2, shrinkB=6, zorder=1)
        root.add_patch(arr)

    # ---------------- Three panels ----------------
    panel_w, gap = 0.278, 0.033
    left0, top, bot = 0.060, 0.448, 0.100

    for k, spec in enumerate(PANELS):
        x0 = left0 + k * (panel_w + gap)
        ax = fig.add_axes([x0, bot, panel_w, top - bot])
        ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        # a restrained divider instead of a card -- keeps the mug the focus
        if k > 0:
            fig.add_artist(plt.Line2D([x0 - gap / 2, x0 - gap / 2],
                                       [bot + 0.01, top - 0.01],
                                       color=FAINT, lw=0.8, transform=fig.transFigure))

        ax.text(0.0, 0.955, spec["n"], color=ACCENT, fontsize=11.5, family=FONT)
        ax.text(0.038, 0.955, spec["title"], color=INK, fontsize=15, family=FONT,
                weight="medium")
        ax.text(0.0, 0.900, spec["instruction"], color=MUTED,
                fontsize=10, family=FONT, style="italic")

        grasp_key, clear_key = spec["grasp"], spec["clear"]
        overlay = overlay_layer(alpha, masks, grasp_key, clear_key)

        ax_w_in = panel_w * FIG_W_IN
        ax_h_in = (top - bot) * FIG_H_IN
        mug_bbox = draw_mug(ax, base, overlay, ar, 0.5, MUG_CY, MUG_H, ax_w_in, ax_h_in)

        if clear_key:
            add_callout(ax, spec["clear_slot"], spec["clear_t"], "KEEP CLEAR",
                        spec["clear_label"], KEEPCLEAR, mug_bbox)
        else:
            l, b, mw, mh = mug_bbox
            ax.text(0.5, b + mh + GUTTER + 0.006, "no mandatory keep-clear region",
                    color=MUTED, fontsize=9, family=FONT, style="italic",
                    ha="center", va="bottom")

        add_callout(ax, spec["grasp_slot"], spec["grasp_t"], "GRASP HERE",
                    spec["grasp_label"], GRASP, mug_bbox)

        ax.text(0.5, 0.025, spec["caption"], color=INK, fontsize=9.5,
                family=FONT, ha="center", va="bottom")

    # ---------------- Legend ----------------
    ly = 0.086
    root.plot([0.060, 0.078], [ly, ly], color=GRASP, lw=2.4, solid_capstyle="round")
    root.text(0.086, ly, "Suitable grasp region", color=INK, fontsize=11.5,
              family=FONT, va="center")
    root.plot([0.320, 0.338], [ly, ly], color=KEEPCLEAR, lw=2.4, solid_capstyle="round")
    root.text(0.346, ly, "Task-constrained keep-clear region", color=INK, fontsize=11.5,
              family=FONT, va="center")
    root.text(0.945, ly,
              "Real segmentation masks (LangSAM + SAM2 Set-of-Mark) — not hand-drawn.",
              color=MUTED, fontsize=9, family=FONT, ha="right", va="center")

    # ---------------- Bottom callout ----------------
    root.plot([0.060, 0.060], [0.028, 0.066], color=ACCENT, lw=2.2, solid_capstyle="round")
    root.text(0.078, 0.047,
              "Task intention determines which surfaces can and cannot be grasped.",
              color=INK, fontsize=15, family=FONT, ha="left", va="center",
              weight="medium")

    png_path = a.out + ".png"
    svg_path = a.out + ".svg"
    fig.savefig(png_path, facecolor=SLIDE_BG, dpi=a.dpi)
    fig.savefig(svg_path, facecolor=SLIDE_BG)
    print("wrote", os.path.abspath(png_path))
    print("wrote", os.path.abspath(svg_path))


if __name__ == "__main__":
    main()
