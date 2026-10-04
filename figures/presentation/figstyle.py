"""
figstyle.py -- shared design system for the AffordGrasp dissertation figure
set. Single source of truth for canvas size, typography, color/icon
semantics, and shared rendering utilities. Every figure script imports from
here rather than re-deriving layout constants.

See docs/superpowers/specs/2026-08-07-dissertation-figures-design.md for the
full design rationale (Sec 3-4).
"""
import os

import matplotlib
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from intent_grasp.paths import WORKSPACE

# ---- reproducibility --------------------------------------------------
SEED = 20260807  # fixed across every figure script (spec Sec 13)

# ---- canvas -------------------------------------------------------------
FIG_W_IN, FIG_H_IN = 16.0, 9.0
DPI = 200
THUMB_DPI = 60  # storyboard-pass resolution

# ---- palette (design spec Sec 4) ----------------------------------------
SLIDE_BG = "#15161A"
INK = "#F0EFEC"
MUTED = "#96948B"
FAINT = "#4A4C53"

ACCEPTED = "#54D26A"   # green: accepted / valid / grasp region
CANDIDATE = "#FFC857"  # amber: candidate / warning / keep-clear
REJECTED = "#E5484D"   # red: rejected / collision / failure -- never the mug's own red
REASONING = "#8B7BEE"  # purple: reasoning / affordance / VLM
GEOMETRY = INK         # white/ink: geometry / robot / coordinate frames

CALLOUT_BG = "#1E212B"
FONT = "DejaVu Sans"

# ---- typography hierarchy ------------------------------------------------
TITLE = dict(family=FONT, size=22, weight="bold", color=INK)
SECTION = dict(family=FONT, size=15, weight="bold", color=INK)
BODY = dict(family=FONT, size=11, weight="normal", color=INK)
CAPTION = dict(family=FONT, size=10, weight="normal", color=MUTED)
METRIC = dict(family=FONT, size=13, weight="bold", color=ACCEPTED)

# ---- caption / margin convention (identical across every figure) --------
CAPTION_Y = 0.035
MARGIN = 0.045
GUTTER = 0.026
ROW_GAP_H = 0.052
ROW_GAP_V = 0.075

# ---- asset directory ------------------------------------------------------
ASSET_ROOT = os.path.join(str(WORKSPACE), "generated_assets")


def asset_dir(*parts):
    """Ensures and returns generated_assets/<parts...> (design spec Sec 6)."""
    path = os.path.join(ASSET_ROOT, *parts)
    os.makedirs(path, exist_ok=True)
    return path


# ---- mask overlay compositor ---------------------------------------------
def mask_overlay(mask, color_hex, alpha=0.35):
    """Returns an RGBA image (H, W, 4) transparent everywhere `mask` is False
    and `color_hex` at `alpha` where True. Composited as a separate layer on
    top of an unmodified photo -- real pixels are never recolored in place
    (design spec Sec 4)."""
    rgb = np.array(matplotlib.colors.to_rgb(color_hex))
    h, w = mask.shape
    out = np.zeros((h, w, 4), dtype=float)
    out[mask, :3] = rgb
    out[mask, 3] = alpha
    return out


# ---- raster post-processing ------------------------------------------------
def crop_to_content(img, bg_rgb, pad=20):
    """Crops a rendered raster (H, W, 3) uint8 array to the bounding box of
    pixels that differ from the background color, plus a fixed pad -- a real
    derivation from the actual rendered content, so a compact render doesn't
    sit in a mostly-empty 16:9 frame. Shared by any figure that composites an
    Open3D (or similar) raster into the matplotlib canvas."""
    bg = np.array(bg_rgb) * 255
    diff = np.abs(img.astype(int) - bg.astype(int)).sum(axis=-1)
    mask = diff > 15
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad, img.shape[0])
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad, img.shape[1])
    return img[y0:y1, x0:x1]


# ---- coordinate frame -----------------------------------------------------
def draw_coordinate_frame(ax3d, origin, R, scale=0.05, labels=("X", "Y", "Z")):
    """Draws an ink-colored axis triad (solid/dashed/dotted, not RGB-colored
    -- color is reserved for status semantics elsewhere) at `origin`,
    oriented by rotation matrix R, on a mplot3d Axes3D. Reused identically in
    Figures 1, 4, 8, 9."""
    styles = ["-", "--", ":"]
    for i, (label, ls) in enumerate(zip(labels, styles)):
        vec = R[:, i] * scale
        end = origin + vec
        xs, ys, zs = zip(origin, end)
        ax3d.plot(xs, ys, zs, color=GEOMETRY, linestyle=ls, linewidth=1.4)
        ax3d.text(end[0], end[1], end[2], label, color=GEOMETRY, fontsize=8)


# ---- pipeline-stage iconography (10 fixed glyph keys) ---------------------
ICON_KEYS = [
    "rgb_camera", "depth_camera", "point_cloud", "vlm", "grounding",
    "segmentation", "affordance", "grasp_generation", "motion_planning",
    "execution",
]


def draw_icon(ax, key, cx, cy, r=0.02, color=INK):
    """Draws one fixed line-icon glyph for a pipeline stage, centered at
    (cx, cy) in the axes' data coordinates with characteristic size r. The
    same glyph is reused everywhere that stage appears (Fig 13 pipeline
    diagram, per-figure stage badges)."""
    if key not in ICON_KEYS:
        raise ValueError(f"unknown icon key {key!r}, must be one of {ICON_KEYS}")

    if key == "rgb_camera":
        ax.add_patch(Rectangle((cx - r, cy - 0.6 * r), 2 * r, 1.2 * r,
                                fill=False, edgecolor=color, linewidth=1.2))
        ax.add_patch(Circle((cx, cy), 0.35 * r, fill=False, edgecolor=color, linewidth=1.2))
    elif key == "depth_camera":
        ax.add_patch(Rectangle((cx - r, cy - 0.6 * r), 2 * r, 1.2 * r,
                                fill=False, edgecolor=color, linewidth=1.2))
        for rr in (0.15 * r, 0.35 * r):
            ax.add_patch(Circle((cx, cy), rr, fill=False, edgecolor=color, linewidth=1.0))
    elif key == "point_cloud":
        rng = np.random.default_rng(SEED)
        pts = rng.uniform(-r, r, size=(12, 2))
        ax.scatter(cx + pts[:, 0], cy + pts[:, 1], s=2.5, color=color)
    elif key == "vlm":
        ax.add_patch(Rectangle((cx - r, cy - 0.6 * r), 2 * r, 1.2 * r,
                                fill=False, edgecolor=color, linewidth=1.2))
        for dx in (-0.4, 0.0, 0.4):
            ax.add_patch(Circle((cx + dx * r, cy), 0.06 * r, color=color))
    elif key == "grounding":
        ax.add_patch(Rectangle((cx - r, cy - r), 2 * r, 2 * r, fill=False,
                                edgecolor=color, linewidth=1.2, linestyle="--"))
        ax.add_line(Line2D([cx - 1.3 * r, cx + 1.3 * r], [cy, cy], color=color, linewidth=0.8))
        ax.add_line(Line2D([cx, cx], [cy - 1.3 * r, cy + 1.3 * r], color=color, linewidth=0.8))
    elif key == "segmentation":
        theta = np.linspace(0, 2 * np.pi, 9)
        blob_x = cx + r * (1 + 0.15 * np.cos(3 * theta)) * np.cos(theta)
        blob_y = cy + r * (1 + 0.15 * np.cos(3 * theta)) * np.sin(theta)
        ax.plot(blob_x, blob_y, color=color, linewidth=1.2, linestyle="--")
    elif key == "affordance":
        ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor=color, linewidth=1.2))
        for ang in range(0, 360, 45):
            dx = r * 1.6 * np.cos(np.radians(ang))
            dy = r * 1.6 * np.sin(np.radians(ang))
            ax.add_patch(FancyArrowPatch((cx, cy), (cx + dx, cy + dy), color=color,
                                          linewidth=0.8, arrowstyle="-|>", mutation_scale=6))
    elif key == "grasp_generation":
        ax.add_line(Line2D([cx - r, cx - 0.3 * r], [cy + r, cy + 0.3 * r], color=color, linewidth=1.4))
        ax.add_line(Line2D([cx + r, cx + 0.3 * r], [cy + r, cy + 0.3 * r], color=color, linewidth=1.4))
        ax.add_line(Line2D([cx - 0.3 * r, cx + 0.3 * r], [cy + 0.3 * r, cy + 0.3 * r], color=color, linewidth=1.4))
    elif key == "motion_planning":
        xs = np.linspace(cx - r, cx + r, 20)
        ys = cy + 0.4 * r * np.sin(np.linspace(0, np.pi, 20))
        ax.plot(xs, ys, color=color, linewidth=1.0, linestyle=":")
        ax.add_patch(Circle((xs[-1], ys[-1]), 0.08 * r, color=color))
    elif key == "execution":
        ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor=color, linewidth=1.2))
        ax.add_line(Line2D([cx - 0.4 * r, cx - 0.05 * r], [cy, cy - 0.35 * r], color=color, linewidth=1.4))
        ax.add_line(Line2D([cx - 0.05 * r, cx + 0.5 * r], [cy - 0.35 * r, cy + 0.4 * r], color=color, linewidth=1.4))
