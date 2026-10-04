"""Shared style module for AffordGrasp dissertation figures (spec v3, sec 4/9.4/9.7).

Every figure script imports from here instead of restyling. Run standalone to
smoke-test the palette and layout constants:
    python figures/dissertation/_style.py
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

mpl.use("Agg")

mpl.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "figure.dpi": 150,
    "savefig.dpi": 400,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.4,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.constrained_layout.use": True,
})

TEXT_WIDTH_IN = 6.27      # A4, 1in margins
HALF_WIDTH_IN = 3.05
MAX_HEIGHT_IN = 8.0

OKABE_ITO = {
    "black":      "#000000",
    "orange":     "#E69F00",
    "sky_blue":   "#56B4E9",
    "green":      "#009E73",
    "yellow":     "#F0E442",
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "purple":     "#CC79A7",
}

# DESIGN_STANDARD.md Rule 1 -- no internal identifier (component key, file name,
# function name, code label) reaches a figure. Every label a figure script wants
# to draw routes through display(); a missing entry raises rather than leaking
# the raw key, so an unlabelled component is a build failure, not a silent typo.
DISPLAY_NAME = {
    # part_adaptive.py component keys
    "main_body":            "body",
    "top_protrusion":       "rim / lid region",
    "rim_ring":              "rim",
    "lateral_protrusion":    "handle (fragment 1)",
    "lateral_protrusion_1":  "handle (fragment 2)",
    "segment_a":             "thin end",
    "segment_b":             "mid-section",
    "segment_c":              "thick end",
    # part-selection ablation method codes (report_assets/PART_NAMING_ABLATION.csv)
    "A_heuristic":            "heuristic",
    "B_som":                  "Set-of-Mark",
    "C_pointing":             "pointing",
    # evidence-gate outcome strings (part_adaptive.py's own vocabulary)
    "ok":                     "accepted",
    "LOW":                    "marginal",
    "NOISE":                  "refused",
}


def display(key):
    """Reader-facing label for an internal identifier. Raises on a missing
    entry (DESIGN_STANDARD.md Rule 1) -- add the translation before plotting,
    never let a raw code identifier reach a figure."""
    if key not in DISPLAY_NAME:
        raise KeyError(f"No reader-facing name for {key!r} -- add one to "
                        f"_style.DISPLAY_NAME before plotting it")
    return DISPLAY_NAME[key]

# Fixed semantic colour mapping (sec 4.3): same colour = same layer/category
# everywhere. Set by Fig 3.1 (Batch C1), reused by every later architecture
# and evidence figure.
SEMANTIC_COLOUR = {
    "reasoning":          OKABE_ITO["blue"],
    "perception":         OKABE_ITO["orange"],
    "geometric_planning": OKABE_ITO["green"],
    "robot_control":      OKABE_ITO["vermillion"],
    "verification":       OKABE_ITO["purple"],
    "measured":           OKABE_ITO["blue"],
    "estimated":          OKABE_ITO["sky_blue"],
    "reject":             OKABE_ITO["black"],
    "keep":               OKABE_ITO["green"],
}

# Second channel per semantic colour (sec 4.3: colour + hatching/marker/line
# style so categories survive greyscale printing).
SEMANTIC_HATCH = {
    "reasoning": "",
    "perception": "///",
    "geometric_planning": "...",
    "robot_control": "xxx",
    "verification": "\\\\\\",
    "measured": "",
    "estimated": "///",
}


def semantic_colour(layer):
    return SEMANTIC_COLOUR[layer]


def semantic_hatch(layer):
    return SEMANTIC_HATCH.get(layer, "")


# Structural conventions adopted from the existing fig01-13 storyboard
# (figstyle.py/figlayout.py), per Addendum A sec 17.1 -- the storyboard wins
# on purely visual/structural matters. Typography, background and in-figure
# titles stay governed by this spec's sec 4 (light print background, no
# in-figure title, Okabe-Ito on white) -- only the STRUCTURE below is
# adopted: rounded status cards with a coloured left/border accent, leader
# lines anchoring every label to its referent, orthogonal (not free-floating
# diagonal) connectors between stages.
def status_card(ax, xy, w, h, colour, title=None, rows=None, fontsize=8, row_gap=0.028):
    """Rounded card with a coloured border, optional bold title + labelled
    rows (each row: (label, value), label bold on its own line, value below
    it) -- the incident/gate-card idiom used throughout fig09/fig12. Every
    line gets its own explicit y-slot so rows cannot overlap regardless of
    how many lines a value wraps to (the earlier bug: multi-line strings
    packed into one text() call at a fixed y-step)."""
    from matplotlib.patches import FancyBboxPatch
    import textwrap
    x, y = xy
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                          facecolor=colour, alpha=0.10, edgecolor=colour, linewidth=1.3)
    ax.add_patch(box)

    line_h = row_gap
    ty = y + h - row_gap
    title_lines = (title or "").split("\n")
    for tl in title_lines:
        ax.text(x + w / 2, ty, tl, ha="center", va="top", fontsize=fontsize,
                 fontweight="bold", color=colour)
        ty -= line_h * 1.15
    ty -= line_h * 0.4

    for label, value in (rows or []):
        ax.text(x + w / 2, ty, label + ":", ha="center", va="top", fontsize=fontsize - 1,
                 fontweight="bold", color=OKABE_ITO["black"])
        ty -= line_h
        # value: a string (single line -- caller is responsible for keeping it
        # short enough to fit the card width) or a pre-split list of lines.
        value_lines = value if isinstance(value, (list, tuple)) else [str(value)]
        for vl in value_lines:
            ax.text(x + w / 2, ty, vl, ha="center", va="top", fontsize=fontsize - 1,
                     color=OKABE_ITO["black"])
            ty -= line_h
        ty -= line_h * 0.5
    return box


def orthogonal_arrow(ax, start, end, colour=None, rad=0.0):
    """Single-bend/orthogonal connector between two stages -- no free-floating
    diagonal arrows (Addendum A sec 17.2 Class S rule, applied wherever an
    arrow indicates flow/sequence)."""
    from matplotlib.patches import FancyArrowPatch
    colour = colour or OKABE_ITO["black"]
    style = f"angle,angleA=0,angleB=90,rad={rad}" if start[1] != end[1] and start[0] != end[0] else "arc3,rad=0"
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10,
                                  color=colour, linewidth=1.1, connectionstyle=style))


def leader_label(ax, point, text_xy, text, colour=None, fontsize=8, ha="left"):
    """A label joined to its referent by a thin leader line -- every label
    must be anchored to the element it describes (Addendum A sec 17.4
    referent audit), never left floating."""
    colour = colour or OKABE_ITO["black"]
    ax.annotate(text, xy=point, xytext=text_xy, fontsize=fontsize, color=colour, ha=ha,
                 arrowprops=dict(arrowstyle="-", shrinkA=0, shrinkB=2, lw=0.9, color=colour))


def panel_label(ax, letter, x=0.0, y=1.06):
    """Consistent (a)/(b)/(c) panel label placement: above the top spine,
    left-aligned to the axes' left edge, clear of y-tick labels (which sit
    below y=1 in axes fraction) and of the axis title if present."""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=9,
             fontweight="bold", va="bottom", ha="left")


def annotate_value(ax, x, y, value, unit="", prefix="", fontsize=8, **kwargs):
    """Consistent numeric annotation: 'prefix value unit', fixed font size."""
    text = f"{prefix}{value}{(' ' + unit) if unit else ''}"
    return ax.annotate(text, (x, y), fontsize=fontsize, **kwargs)


def truncation_marker(ax, axis="y", at=0.0):
    """Draw a small break/zig-zag marking a truncated (non-zero-baseline) axis."""
    if axis == "y":
        y0 = ax.get_ylim()[0]
        ax.plot([-0.012, 0.012], [y0, y0], transform=ax.get_yaxis_transform(),
                 clip_on=False, color="black", lw=0.8)
        # y=-0.045 (not 0.0): the bottom y-tick's own label sits centered on
        # y=0 in axes-fraction space -- placing the break glyph there collided
        # with it (found on fig_7_2_lift_verification.py); dropping it just
        # below the tick label clears that collision for any axis this helper
        # is used on, not only that figure's own tick spacing.
        ax.text(-0.02, -0.045, "//", transform=ax.transAxes, fontsize=7,
                 rotation=90, va="top", ha="right")
    else:
        x0 = ax.get_xlim()[0]
        ax.text(0.0, -0.06, "//", transform=ax.transAxes, fontsize=7, va="top")


def save_figure(fig, name, out_dir=None):
    """Write PDF + SVG + 400dpi PNG to figures/out/ under deterministic names."""
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for ext in ("pdf", "svg", "png"):
        p = os.path.join(out_dir, f"{name}.{ext}")
        fig.savefig(p)
        paths[ext] = p
    return paths


def mask_contour(ax, rgb, part_mask, whole_mask=None, colour=None, ref_colour=None):
    """Outline, not flood fill (Addendum B sec 18.2.1): light fill + a hard
    boundary contour for the part mask; the whole-object mask, if given, as a
    dashed neutral reference contour. Two nearly-identical outlines make the
    coverage argument at a glance where a single filled blob would not."""
    import matplotlib.colors as mcolors
    colour = colour or OKABE_ITO["blue"]
    ref_colour = ref_colour or OKABE_ITO["black"]
    ax.imshow(rgb)
    cmap = mcolors.ListedColormap([colour])
    ax.imshow(np.ma.masked_where(part_mask == 0, part_mask), cmap=cmap, alpha=0.22,
              interpolation="nearest")
    ax.contour(part_mask.astype(float), levels=[0.5], colors=[colour], linewidths=1.4)
    if whole_mask is not None:
        ax.contour(whole_mask.astype(float), levels=[0.5], colors=[ref_colour],
                    linewidths=1.2, linestyles="dashed")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def mask_overlay(ax, rgb, mask, colour=None, alpha=0.45):
    """Alpha-composite a boolean mask over an RGB image using PIL (not OpenCV
    colour maps — those are not colourblind-safe, sec 9.6). Native resolution,
    no upscaling."""
    if colour is None:
        colour = OKABE_ITO["sky_blue"]
    rgb_arr = np.asarray(rgb)
    h, w = mask.shape[:2]
    base = Image.fromarray(rgb_arr[:h, :w].astype(np.uint8)).convert("RGBA")
    rgb_int = tuple(int(colour.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    overlay[mask.astype(bool)] = (*rgb_int, int(alpha * 255))
    over_img = Image.fromarray(overlay, mode="RGBA")
    composed = Image.alpha_composite(base, over_img)
    ax.imshow(np.asarray(composed))
    ax.set_xticks([]); ax.set_yticks([])
    return ax


# Fixed camera pose for every point-cloud figure (Fig 3.5, 4.6, 4.7), so
# panels are visually comparable (sec 9.2). Recorded here, not per-script.
CLOUD_CAMERA = dict(
    front=[0.55, -0.55, 0.35],
    lookat=[0.0, 0.0, 0.0],
    up=[0.0, 0.0, 1.0],
    zoom=0.7,
)


def render_cloud(points, colours=None, out_png=None, width=900, height=700,
                  camera=None, point_size=3.0):
    """Fixed-camera offscreen point-cloud render via open3d. Returns an
    (H,W,3) uint8 array; writes out_png if given. Falls back to a matplotlib
    3D scatter (sec 9.2 fallback) if open3d offscreen rendering is unavailable
    on this machine."""
    camera = camera or CLOUD_CAMERA
    try:
        import open3d as o3d
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.asarray(points, dtype=np.float64))
        if colours is not None:
            pcd.colors = o3d.utility.Vector3dVector(np.asarray(colours, dtype=np.float64))
        vis = o3d.visualization.Visualizer()
        vis.create_window(width=width, height=height, visible=False)
        vis.add_geometry(pcd)
        opt = vis.get_render_option()
        opt.point_size = point_size
        opt.background_color = np.array([1.0, 1.0, 1.0])
        ctr = vis.get_view_control()
        ctr.set_front(camera["front"])
        ctr.set_lookat(camera["lookat"])
        ctr.set_up(camera["up"])
        ctr.set_zoom(camera["zoom"])
        vis.poll_events()
        vis.update_renderer()
        img = np.asarray(vis.capture_screen_float_buffer(do_render=True))
        vis.destroy_window()
        img = (img * 255).astype(np.uint8)
        if out_png:
            Image.fromarray(img).save(out_png)
        return img
    except Exception as exc:  # pragma: no cover - fallback path
        print(f"[render_cloud] open3d offscreen render failed ({exc}); "
              f"falling back to matplotlib 3D scatter")
        fig = plt.figure(figsize=(width / 150, height / 150))
        ax = fig.add_subplot(111, projection="3d")
        P = np.asarray(points)
        c = colours if colours is not None else "k"
        ax.scatter(P[:, 0], P[:, 1], P[:, 2], c=c, s=point_size)
        ax.set_box_aspect((1, 1, 1))
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        if out_png:
            Image.fromarray(buf).save(out_png)
        plt.close(fig)
        return buf


if __name__ == "__main__":
    print("TEXT_WIDTH_IN =", TEXT_WIDTH_IN, "HALF_WIDTH_IN =", HALF_WIDTH_IN)
    print("OKABE_ITO palette:", OKABE_ITO)
    print("SEMANTIC_COLOUR:", SEMANTIC_COLOUR)
    fig, ax = plt.subplots(figsize=(HALF_WIDTH_IN, 2.0))
    ax.plot([0, 1], [0, 1], color=OKABE_ITO["blue"])
    panel_label(ax, "a")
    paths = save_figure(fig, "_style_smoketest")
    plt.close(fig)
    print("wrote:", paths)
