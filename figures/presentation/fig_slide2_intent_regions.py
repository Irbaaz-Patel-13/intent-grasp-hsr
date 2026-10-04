"""
fig_slide2_intent_regions.py -- Slide 2 (Motivation & Problem) figure.  v2

One mug, three intents, three different grasp/keep-clear region pairs.
Schematic overlay on a product photograph -- NOT system output, and labelled
as such on the figure itself.

    python fig_slide2_intent_regions.py --img red-mug.png --tune
    python fig_slide2_intent_regions.py --img red-mug.png --out slide2.png

Requires: numpy, pillow, matplotlib, scipy.

v2 changes: the object is keyed on colour saturation rather than brightness,
so the mug's near-white interior is no longer mistaken for background, and the
grey drop shadow no longer inflates the bounding box.
"""

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image
from scipy.ndimage import (gaussian_filter, binary_erosion, binary_closing,
                           binary_fill_holes, label)


SLIDE_BG   = "#16171B"
PANEL_BG   = "#1D1F24"
INK        = "#F2F1EE"
MUTED      = "#8E8C86"
HAIRLINE   = "#33353B"

GRASP      = "#4E9A63"
KEEPCLEAR  = "#D99A3C"
ACCENT     = "#7C6CE0"

FONT = "DejaVu Sans"


INTENTS = [
    dict(n="1",
         title="Drink from it",
         instruction='"I\'d like a hot drink"',
         grasp="handle",
         grasp_why="Handle keeps the hand\noff a hot surface",
         clear="rim",
         clear_why="Rim meets the lips"),
    dict(n="2",
         title="Pour it out",
         instruction='"Pour this out"',
         grasp="body",
         grasp_why="Body allows a\ncontrolled tilt",
         clear="rim",
         clear_why="Rim is where the\nliquid leaves"),
    dict(n="3",
         title="Hand it over",
         instruction='"Pass it to me"',
         grasp="body",
         grasp_why="Body presents the\nhandle outward",
         clear="handle",
         clear_why="Handle is for the\nperson receiving"),
]

# Normalised bounds within the mug bounding box. y=0 is the top of the mug.
# Retuned for a shadow-free box: the rim ellipse occupies the top ~17%, and
# the handle begins at ~70% across.
REGIONS = {
    "rim":    dict(x0=0.00, x1=0.70, y0=0.00, y1=0.17),
    "body":   dict(x0=0.00, x1=0.70, y0=0.17, y1=1.00),
    "handle": dict(x0=0.68, x1=1.00, y0=0.12, y1=0.66),
}


def cutout(path, sat_thresh=0.12, feather=1.6, mode="sat"):
    """
    Isolate the mug.

    mode="sat"   -- foreground is saturated colour, then enclosed holes are
                    filled. Correct for a coloured object on white with a grey
                    shadow: the shadow is unsaturated and drops out, the white
                    interior is enclosed and is recovered.
    mode="white" -- foreground is anything not near-white. Use only if the
                    object itself is grey or white.
    """
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im).astype(np.float64) / 255.0

    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    sat = mx - mn

    if mode == "sat":
        core = sat > sat_thresh
    else:
        core = mn < 0.90

    core = binary_closing(core, np.ones((5, 5)))
    core = binary_fill_holes(core)

    lab, n = label(core)
    if n == 0:
        raise SystemExit("No object found -- lower --sat-thresh.")
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    core = lab == sizes.argmax()

    alpha = gaussian_filter(core.astype(np.float64), feather)
    alpha = np.clip((alpha - 0.35) / 0.35, 0.0, 1.0)

    ys, xs = np.where(core)
    pad = 3
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, core.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, core.shape[1])

    frac = 100.0 * core.sum() / core.size
    print("object %d x %d px, %.1f%% of frame" % (x1 - x0, y1 - y0, frac))
    return rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def region_mask(shape, spec, alpha):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    nx, ny = xx / max(w - 1, 1), yy / max(h - 1, 1)
    box = ((nx >= spec["x0"]) & (nx < spec["x1"]) &
           (ny >= spec["y0"]) & (ny < spec["y1"]))
    return box & (alpha > 0.5)


def shade_preserving_tint(rgb, mask, hexcol, strength=0.80):
    """Recolour a region while keeping its own highlights and shadow."""
    out = rgb.copy()
    if not mask.any():
        return out

    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    vals = lum[mask]
    lo, hi = np.percentile(vals, 3), np.percentile(vals, 97)
    if hi - lo < 1e-6:
        hi = lo + 1e-6
    t = np.clip((lum[mask] - lo) / (hi - lo), 0.0, 1.0)

    base = np.array(matplotlib.colors.to_rgb(hexcol))
    dark = base * 0.32
    light = base + (1.0 - base) * 0.62
    ramp = dark[None, :] + (light - dark)[None, :] * t[:, None]

    out[mask] = rgb[mask] * (1.0 - strength) + ramp * strength
    return out


def outline(mask, width=2):
    return mask & ~binary_erosion(mask, iterations=width)


def render_panel(rgb, alpha, grasp_name, clear_name):
    out = rgb.copy()
    a = alpha.copy()
    masks = {}

    for name, col in ((grasp_name, GRASP), (clear_name, KEEPCLEAR)):
        m = region_mask(rgb.shape[:2], REGIONS[name], alpha)
        masks[name] = m
        out = shade_preserving_tint(out, m, col)

    coded = np.zeros(rgb.shape[:2], bool)
    for m in masks.values():
        coded |= m
    rest = (alpha > 0.5) & ~coded
    lum = (out @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    out[rest] = (lum * 0.72 + out * 0.28)[rest]

    for name, col in ((grasp_name, GRASP), (clear_name, KEEPCLEAR)):
        e = outline(masks[name], 2)
        out[e] = matplotlib.colors.to_rgb(col)
        a[e] = 1.0

    return np.dstack([out, a]), masks


def centroid(mask, w, h):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return 0.5, 0.5
    return xs.mean() / w, ys.mean() / h


def place_labels(anchors, min_gap):
    order = sorted(range(len(anchors)), key=lambda i: anchors[i])
    out = list(anchors)
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        if out[j] - out[i] < min_gap:
            out[j] = out[i] + min_gap
    top = out[order[-1]]
    if top > 0.96:
        for i in range(len(out)):
            out[i] -= top - 0.96
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--out", default="fig_slide2_intent_regions.png")
    ap.add_argument("--sat-thresh", type=float, default=0.12)
    ap.add_argument("--mode", choices=["sat", "white"], default="sat")
    ap.add_argument("--tune", action="store_true")
    ap.add_argument("--dpi", type=int, default=160)
    a = ap.parse_args()

    rgb, alpha = cutout(a.img, a.sat_thresh, mode=a.mode)
    h, w = alpha.shape

    if a.tune:
        fig, ax = plt.subplots(figsize=(6, 7), facecolor=SLIDE_BG)
        ax.imshow(np.dstack([rgb, alpha]))
        for i, (name, spec) in enumerate(REGIONS.items()):
            rx, ry = spec["x0"] * w, spec["y0"] * h
            rw = (spec["x1"] - spec["x0"]) * w
            rh = (spec["y1"] - spec["y0"]) * h
            ax.add_patch(Rectangle((rx, ry), rw, rh, fill=False,
                                   ec=ACCENT, lw=1.4, ls=(0, (5, 3))))
            ax.annotate(name,
                        xy=(rx + rw, ry), xycoords="data",
                        xytext=(14, -14 - i * 26), textcoords="offset points",
                        color=ACCENT, fontsize=12, family=FONT,
                        ha="left", va="top",
                        bbox=dict(fc=SLIDE_BG, ec=ACCENT, lw=0.6, pad=2.5),
                        arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
        ax.set_xlim(-0.30 * w, 1.34 * w)
        ax.set_ylim(1.05 * h, -0.10 * h)
        ax.set_axis_off()
        fig.savefig("region_tune.png", facecolor=SLIDE_BG,
                    bbox_inches="tight", dpi=130)
        print("wrote region_tune.png")
        return

    fig = plt.figure(figsize=(16, 9), facecolor=SLIDE_BG)
    fig.subplots_adjust(0, 0, 1, 1)
    root = fig.add_axes([0, 0, 1, 1]); root.set_axis_off()
    root.set_xlim(0, 1); root.set_ylim(0, 1)

    root.text(0.055, 0.935, "Motivation & problem", color=ACCENT,
              fontsize=15, family=FONT, va="center")
    root.plot([0.055, 0.135], [0.912, 0.912], color=ACCENT, lw=2.2)

    root.text(0.055, 0.845,
              "Where a robot should grasp is set by the task, not the shape.",
              color=INK, fontsize=27, family=FONT, va="center")
    root.text(0.055, 0.788,
              "One mug, three instructions, three different answers.",
              color=MUTED, fontsize=15.5, family=FONT, va="center")

    panel_w, gap = 0.276, 0.028
    left0, top, bot = 0.055, 0.715, 0.145

    for k, spec in enumerate(INTENTS):
        x0 = left0 + k * (panel_w + gap)
        ax = fig.add_axes([x0, bot, panel_w, top - bot])
        ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        ax.add_patch(FancyBboxPatch(
            (0.005, 0.005), 0.99, 0.99,
            boxstyle="round,pad=0.004,rounding_size=0.02",
            fc=PANEL_BG, ec=HAIRLINE, lw=1.0, transform=ax.transAxes))

        ax.text(0.055, 0.945, spec["n"], color=ACCENT, fontsize=13, family=FONT)
        ax.text(0.105, 0.945, spec["title"], color=INK, fontsize=16, family=FONT)
        ax.text(0.055, 0.888, spec["instruction"], color=MUTED,
                fontsize=12.5, family=FONT, style="italic")

        comp, masks = render_panel(rgb, alpha, spec["grasp"], spec["clear"])

        asp = w / float(h)
        mug_h = 0.52
        mug_w = min(0.44, mug_h * asp * (top - bot) / 1.0)
        mug_l, mug_b = 0.06, 0.30
        ax.imshow(comp, extent=(mug_l, mug_l + mug_w, mug_b, mug_b + mug_h),
                  transform=ax.transAxes, zorder=3, aspect="auto")

        items = [(spec["grasp"], spec["grasp_why"], GRASP, "Grasp here"),
                 (spec["clear"], spec["clear_why"], KEEPCLEAR, "Keep clear")]

        raw = []
        for name, _, _, _ in items:
            _, cy = centroid(masks[name], w, h)
            raw.append(mug_b + (1.0 - cy) * mug_h)
        ys = place_labels(raw, min_gap=0.235)

        lab_x = mug_l + mug_w + 0.07
        for (name, why, col, kind), y_src, y in zip(items, raw, ys):
            cx, cy = centroid(masks[name], w, h)
            px = mug_l + cx * mug_w
            ax.plot([px, lab_x - 0.035], [y_src, y], color=col, lw=0.9,
                    ls=(0, (3, 3)), alpha=0.75, transform=ax.transAxes, zorder=2)
            ax.plot([px], [y_src], marker="o", ms=3.4, color=col,
                    transform=ax.transAxes, zorder=4)
            ax.add_patch(Rectangle((lab_x - 0.028, y - 0.012), 0.016, 0.026,
                                   fc=col, ec="none", transform=ax.transAxes))
            ax.text(lab_x, y, "%s: %s" % (kind, name), color=col,
                    fontsize=12.5, family=FONT, va="center")
            ax.text(lab_x, y - 0.075, why, color=MUTED, fontsize=11,
                    family=FONT, va="top", linespacing=1.45)

    ly = 0.088
    root.add_patch(Rectangle((0.055, ly - 0.011), 0.017, 0.024, fc=GRASP, ec="none"))
    root.text(0.080, ly, "Grasp region -- suitable to hold",
              color=INK, fontsize=12.5, family=FONT, va="center")
    root.add_patch(Rectangle((0.330, ly - 0.011), 0.017, 0.024, fc=KEEPCLEAR, ec="none"))
    root.text(0.355, ly, "Keep-clear region -- must stay free for the task",
              color=INK, fontsize=12.5, family=FONT, va="center")

    root.text(0.945, 0.040,
              "Illustrative schematic -- regions drawn by hand, not system output.",
              color=MUTED, fontsize=10.5, family=FONT, ha="right", va="center")

    fig.savefig(a.out, facecolor=SLIDE_BG, dpi=a.dpi)
    print("wrote %s" % os.path.abspath(a.out))


if __name__ == "__main__":
    main()
