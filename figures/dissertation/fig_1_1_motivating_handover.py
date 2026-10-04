"""Fig 1.1 -- Motivating handover case (Class P -- Pictorial, photo + drawn
overlay, Addendum A sec 17.6).

Object is the **mug** (decision 2026-08-17, superseding an earlier
knife-based build now archived at
figures/archive/fig_1_1_knife_version/README.md): the mug is the object
named in the portfolio's own Chapter 1 motivating text ("A person grabbing
a mug adjusts their hold - handle when pouring, sides when passing it on")
and in the pre-existing, approved presentation figure this rebuilds
(build_motivation_slide.py -> motivation_slide.svg/.png).

Real assets only, reused unmodified from the presentation figure's own
pipeline -- nothing here is redrawn or hand-tuned:
    red-mug.png                              -- real LangSAM+SAM2 RGBA cutout
    outputs/motivation/object_mask.npy       -- whole-mug mask (LangSAM)
    outputs/motivation/handle_mask.npy       -- handle region (SAM2 Set-of-Mark)
    outputs/motivation/rim_mask.npy          -- rim region (SAM2 Set-of-Mark)
    outputs/motivation/segmentation_report.json -- picked-region provenance
`body` = object_mask minus handle_mask minus rim_mask (set difference, same
derivation the presentation figure used -- not a separate mask asset).

Task -> grasp/keep-clear mapping and callout geometry (gutter slots, row
gaps, mug placement fractions) are ported unchanged from the approved
presentation figure (build_motivation_slide.py) -- same real mask
centroids, same non-overlapping layout, just restyled for print:
    (a) Drink     -- grasp: handle   | keep clear: rim     (mouth contact)
    (b) Hand over -- grasp: body     | keep clear: handle  (left free for
                                                              the recipient)
    (c) Store/move-- grasp: any stable region (whole object) | no keep-clear

Report-style differences from the presentation source (DESIGN_STANDARD.md
sec 4/9.4): light print background (not the dark slide bg), Okabe-Ito
palette, no title banner, no decorative "SAME OBJECT" hero-and-fan-arrows
(redundant here -- the three panels already show the identical crop at
identical size/position, which is the same proof the hero panel was
making), house panel_label (a)/(b)/(c) convention, constrained_layout
disabled in favour of the source script's own fixed-rect geometry (mixing
the two caused text to render oversized relative to auto-shrunk axes).

Run: python figures/dissertation/fig_1_1_motivating_handover.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
sys.path.insert(0, HERE)
from intent_grasp.paths import REPO_ROOT  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import binary_erosion

import _qa as qa
import _style as fs
from build_motivation_slide import load_real_cutout  # real-asset loader, reused unmodified

FIGURE_ID = "fig_1_1_motivating_handover"

INTENT = "The same mug requires a different grasp region depending on the task the robot is performing."

GRASP = fs.OKABE_ITO["green"]
KEEPCLEAR = fs.OKABE_ITO["orange"]
MUTED = "#595959"
FAINT = "#C9C9C9"

FIG_W_IN, FIG_H_IN = fs.TEXT_WIDTH_IN, 2.75

# Panel geometry (figure-fraction) -- panel row only, no title banner/hero.
# Narrower absolute panel width than the source 16in slide (this is a
# 6.27in-wide print figure) means the mug must be sized as a SMALLER
# fraction of its own panel than in the source, to leave horizontal room
# for the side callout labels -- tuned below, not copied verbatim.
PANEL_W, GAP = 0.300, 0.030
LEFT0, TOP, BOT = 0.020, 0.950, 0.200

# Within-panel geometry (each panel's own axes-fraction 0..1).
TITLE_Y, INSTR_Y = 0.97, 0.885
MUG_CY, MUG_H = 0.440, 0.360
CAPTION_Y = 0.020
GUTTER = 0.025
ROW_GAP_H = 0.060
ROW_GAP_V = 0.070

PANELS = [
    dict(letter="a", title="Drink", instruction="\u201cI\u2019d like a hot drink\u201d",
         grasp="handle", grasp_label="Handle", grasp_slot="right", grasp_t=0.50,
         clear="rim", clear_label="Rim", clear_slot="top", clear_t=0.46,
         caption="Needs access to the rim."),
    dict(letter="b", title="Hand over", instruction="\u201cPass it to me\u201d",
         grasp="body", grasp_label="Body", grasp_slot="bottom", grasp_t=0.50,
         clear="handle", clear_label="Handle", clear_slot="right", clear_t=0.50,
         caption="Handle stays accessible."),
    dict(letter="c", title="Store / move", instruction="\u201cPut it away\u201d",
         grasp="object", grasp_label="Any stable region", grasp_slot="bottom", grasp_t=0.50,
         clear=None, clear_label=None, clear_slot=None, clear_t=None,
         caption="Only grasp stability matters."),
]

CAPTION = (
    "Fig 1.1. The same mug (real LangSAM+SAM2 segmentation, red-mug.png) requires a different "
    "grasp region depending on the task: (a) drinking leaves the rim clear for the mouth and "
    "grasps the handle; (b) handing the mug to a person grasps the body instead, leaving the "
    "handle free for the recipient to take; (c) storing or moving the mug has no task-specific "
    "keep-clear constraint -- any stable grasp region suffices. Same object, same segmentation "
    "pipeline, three different task-conditioned grasp/keep-clear assignments -- the motivating "
    "case for task-aware (rather than stability-only) grasp selection."
)


def edge_mask(mask, width=2):
    return mask & ~binary_erosion(mask, iterations=width)


def overlay_layer(alpha, masks, grasp_key, clear_key):
    """Transparent RGBA overlay: real mask fill + crisp white contour. The
    mug photo itself is never touched -- composited as a separate imshow
    layer on top of it (same approach, same FILL_ALPHA reasoning, as the
    approved presentation figure)."""
    h, w = alpha.shape
    ov = np.zeros((h, w, 4))
    grasp_m = masks[grasp_key] if grasp_key else np.zeros((h, w), bool)
    clear_m = masks[clear_key] if clear_key else np.zeros((h, w), bool)
    FILL_ALPHA = 0.56
    for m, col in ((grasp_m, GRASP), (clear_m, KEEPCLEAR)):
        if not m.any():
            continue
        c = mcolors.to_rgb(col)
        ov[m] = (*c, FILL_ALPHA)
        ov[edge_mask(m, 2)] = (1.0, 1.0, 1.0, 0.95)
    return ov


def draw_mug(ax, base, overlay, ar, cx, cy, h_frac, ax_w_in, ax_h_in):
    w_frac = (h_frac * ax_h_in * ar) / ax_w_in
    l, b = cx - w_frac / 2.0, cy - h_frac / 2.0
    extent = (l, l + w_frac, b, b + h_frac)
    ax.imshow(base, extent=extent, transform=ax.transAxes, zorder=3, aspect="auto")
    ax.imshow(overlay, extent=extent, transform=ax.transAxes, zorder=4, aspect="auto")
    return l, b, w_frac, h_frac


def add_callout(ax, slot, t, role, label, color, mug_bbox):
    l, b, mw, mh = mug_bbox
    ROLE_FS, NAME_FS = 8.0, 7.5
    if slot == "right":
        edge_x, edge_y = l + mw, b + t * mh
        line_x1 = edge_x + GUTTER
        ax.plot([edge_x, line_x1], [edge_y, edge_y], color=color, lw=1.1,
                 alpha=0.95, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=2.6, color=color, transform=ax.transAxes, zorder=6)
        tx = line_x1 + 0.012
        ax.text(tx, edge_y + ROW_GAP_H / 2, role, color=color, fontsize=ROLE_FS,
                 va="center", ha="left", weight="bold", transform=ax.transAxes)
        ax.text(tx, edge_y - ROW_GAP_H / 2, label, color=MUTED, fontsize=NAME_FS,
                 va="center", ha="left", transform=ax.transAxes)
    elif slot == "left":
        edge_x, edge_y = l, b + t * mh
        line_x0 = edge_x - GUTTER
        ax.plot([line_x0, edge_x], [edge_y, edge_y], color=color, lw=1.1,
                 alpha=0.95, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=2.6, color=color, transform=ax.transAxes, zorder=6)
        tx = line_x0 - 0.012
        ax.text(tx, edge_y + ROW_GAP_H / 2, role, color=color, fontsize=ROLE_FS,
                 va="center", ha="right", weight="bold", transform=ax.transAxes)
        ax.text(tx, edge_y - ROW_GAP_H / 2, label, color=MUTED, fontsize=NAME_FS,
                 va="center", ha="right", transform=ax.transAxes)
    elif slot == "top":
        edge_x, edge_y = l + t * mw, b + mh
        line_y1 = edge_y + GUTTER
        ax.plot([edge_x, edge_x], [edge_y, line_y1], color=color, lw=1.1,
                 alpha=0.95, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=2.6, color=color, transform=ax.transAxes, zorder=6)
        ty = line_y1 + 0.010
        ax.text(edge_x, ty, label, color=MUTED, fontsize=NAME_FS, va="bottom", ha="center",
                 transform=ax.transAxes)
        ax.text(edge_x, ty + ROW_GAP_V, role, color=color, fontsize=ROLE_FS, va="bottom",
                 ha="center", weight="bold", transform=ax.transAxes)
    elif slot == "bottom":
        edge_x, edge_y = l + t * mw, b
        line_y0 = edge_y - GUTTER
        ax.plot([edge_x, edge_x], [line_y0, edge_y], color=color, lw=1.1,
                 alpha=0.95, transform=ax.transAxes, zorder=5, solid_capstyle="round")
        ax.plot([edge_x], [edge_y], marker="o", ms=2.6, color=color, transform=ax.transAxes, zorder=6)
        ty = line_y0 - 0.010
        ax.text(edge_x, ty, label, color=MUTED, fontsize=NAME_FS, va="top", ha="center",
                 transform=ax.transAxes)
        ax.text(edge_x, ty - ROW_GAP_V, role, color=color, fontsize=ROLE_FS, va="top",
                 ha="center", weight="bold", transform=ax.transAxes)


def build():
    rgb, alpha, masks, report = load_real_cutout()
    h, w = alpha.shape
    ar = w / float(h)
    base = np.dstack([rgb, alpha])

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor="white", constrained_layout=False)
    root = fig.add_axes([0, 0, 1, 1]); root.set_axis_off()
    root.set_xlim(0, 1); root.set_ylim(0, 1)

    for k, spec in enumerate(PANELS):
        x0 = LEFT0 + k * (PANEL_W + GAP)
        ax = fig.add_axes([x0, BOT, PANEL_W, TOP - BOT])
        ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        if k > 0:
            fig.add_artist(plt.Line2D([x0 - GAP / 2, x0 - GAP / 2], [BOT + 0.01, TOP - 0.01],
                                        color=FAINT, lw=0.8, transform=fig.transFigure))

        ax.text(0.5, TITLE_Y, spec["title"], color="black", fontsize=10.5, ha="center",
                 va="top", weight="medium")
        ax.text(0.5, INSTR_Y, spec["instruction"], color=MUTED, fontsize=8, style="italic",
                 ha="center", va="top")

        overlay = overlay_layer(alpha, masks, spec["grasp"], spec["clear"])
        ax_w_in = PANEL_W * FIG_W_IN
        ax_h_in = (TOP - BOT) * FIG_H_IN
        mug_bbox = draw_mug(ax, base, overlay, ar, 0.5, MUG_CY, MUG_H, ax_w_in, ax_h_in)

        if spec["clear"]:
            add_callout(ax, spec["clear_slot"], spec["clear_t"], "KEEP CLEAR",
                        spec["clear_label"], KEEPCLEAR, mug_bbox)
        else:
            l, b, mw, mh = mug_bbox
            ax.text(0.5, b + mh + GUTTER + 0.008, "no keep-clear constraint", color=MUTED,
                     fontsize=7.5, style="italic", ha="center", va="bottom")

        add_callout(ax, spec["grasp_slot"], spec["grasp_t"], "GRASP HERE",
                    spec["grasp_label"], GRASP, mug_bbox)

        ax.text(0.5, CAPTION_Y, spec["caption"], color="black", fontsize=8.5, ha="center", va="bottom")
        fs.panel_label(ax, spec["letter"], x=0.0, y=1.0)

    # ---- legend + shared closing statement ----
    ly = 0.110
    root.plot([0.300, 0.328], [ly, ly], color=GRASP, lw=2.4, solid_capstyle="round")
    root.text(0.336, ly, "grasp region", color="black", fontsize=9, va="center")
    root.plot([0.560, 0.588], [ly, ly], color=KEEPCLEAR, lw=2.4, solid_capstyle="round")
    root.text(0.596, ly, "keep-clear region", color="black", fontsize=9, va="center")

    root.text(0.5, 0.040, "Same mug, same segmentation \u2014 grasp region set by task.",
              color="black", fontsize=9.5, ha="center", va="center", weight="medium")

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] source: red-mug.png + outputs/motivation/*.npy (real LangSAM+SAM2 masks)")
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("A")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
    print(f"[{FIGURE_ID}] -- communication check still required: view the PNG, blind-read it, "
          f"compare against INTENT, then call qa.record_communication_check(...).")
