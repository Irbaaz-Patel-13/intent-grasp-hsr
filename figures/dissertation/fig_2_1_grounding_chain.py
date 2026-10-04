"""Fig 2.1 -- Open-vocabulary grounding: detection and segmentation chained
(Class S/D hybrid -- real capture + real detection + real mask, Chapter 2
mechanism figure, not a Chapter 5 results figure).

Core message: a free-form language query becomes an image region through
two chained real model calls -- open-set detection produces a bounding box,
and that box is what promptable segmentation receives. This figure explains
the MECHANISM; Chapter 5 (fig_5_1/5_2/5_5 etc.) measures what the mechanism
actually returns for real part-level queries. No coverage %, confidence
score, point count, or object comparison belongs here -- those are Ch5.

Real evidence, one real detection call, reused identically across all three
panels (same capture, same crop, same box, same mask):
  Experiment_Logs/2026-08-07/grasps_out.npz  -- `grounding_rgb`, the real
    robot head-camera capture already used throughout this dissertation for
    the mug scenario (same image behind grasps_out.npz's own object_mask,
    which is 3830px -- this script's live re-run of the same detector
    returns 3834px, consistent to within re-run noise).
  visual_grounding.py -- VisualAffordanceGrounder._langsam_predict(), the
    real, unmodified LangSAM (GroundingDINO+SAM2) wrapper the live pipeline
    itself calls. Invoked here directly (not through the two-pass
    ground() convenience method) with a single bare object-level query, so
    the box+mask pair returned are genuinely from ONE real detection call --
    ground()'s own Pass 1 combines object+part into one query string
    ("mug with handle.") to disambiguate near-identical objects, which is
    not an object-level-only query and would show a query this figure is
    not allowed to (Ch5 territory); calling the same real method directly
    with a bare query avoids that without touching any pipeline code.
  No source code was modified. No box or mask coordinate was hand-edited;
  denormalisation of the returned box replicates visual_grounding.py's own
  logic verbatim (lines ~396-403) for consistency with how the live
  pipeline itself interprets LangSAM's output.

QUERY WORDING (spec sec 7 disclosure): the authoritative spec's suggested
display text was "the mug" (with an article). No real query anywhere in
this codebase (fig02_grounding.py, probe_langsam_mug.py, segment_parts.py,
visual_grounding.py's own object_query/combined_query construction) ever
includes an article -- every real GroundingDINO-style prompt in this
project is a bare noun phrase ending in a period ("coffee mug.", "mug
handle.", target_object.lower()+"."). This figure follows that established,
real convention and queries "mug." verbatim -- displayed in the figure
exactly as sent to the model, not silently rewritten to "the mug", and
disclosed here rather than silently substituted (spec sec 7). The two are
semantically equivalent (same object-level referent); only the article
differs, and the article was never part of any real query in this project.

Run: python figures/dissertation/fig_2_1_grounding_chain.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
sys.path.insert(0, HERE)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

import _qa as qa
import _style as fs

FIGURE_ID = "fig_2_1_grounding_chain"

QUERY = "mug."
CAPTURE_PATH = os.path.join(DATA_ROOT, "Experiment_Logs", "2026-08-07", "grasps_out.npz")

BOX_COLOR = fs.OKABE_ITO["blue"]
MASK_COLOR = fs.semantic_colour("perception")  # Okabe-Ito orange -- house perception-layer colour
INK = "black"
MUTED = "#595959"

INTENT = ("A language query becomes an image region through two chained real stages: "
          "open-set detection produces a bounding box, and that box is what promptable "
          "segmentation receives as its prompt.")

CAPTION = (
    "Fig 2.1. Open-vocabulary grounding, real capture and real model output (query "
    "\"mug.\", GroundingDINO+SAM2, box_threshold=text_threshold=0.20). (a) Visual scene: "
    "the real RGB capture. (b) Open-set detection: the language query and the scene are "
    "given to the detector, which returns a bounding box -- everything the next stage can "
    "possibly return lies inside it. (c) Promptable segmentation: the same box is passed "
    "as the prompt to the segmentation stage, which returns the grounded region (shown "
    "faded: the box that produced it). The same pipeline receives object-level and "
    "part-level queries; Chapter 5 measures what it returns for each."
)


def _load_grounder():
    from intent_grasp.config import VisualGroundingConfig
    from intent_grasp.visual_grounding import VisualAffordanceGrounder
    return VisualAffordanceGrounder(VisualGroundingConfig())


def _run_detection():
    """One real detection call: query='mug.' on the real captured RGB. Returns
    the full-frame rgb, boolean mask, and pixel-space box [x1,y1,x2,y2], all
    from the same real GroundingDINO+SAM2 call."""
    from PIL import Image
    d = np.load(CAPTURE_PATH, allow_pickle=True)
    rgb = d["grounding_rgb"]
    h, w = rgb.shape[:2]

    grounder = _load_grounder()
    pil_image = Image.fromarray(rgb)
    result = grounder._langsam_predict(pil_image, QUERY)
    if result is None or len(result["masks"]) == 0:
        raise RuntimeError(f"no real detection for query {QUERY!r} on {CAPTURE_PATH} -- "
                            f"cannot fabricate a box/mask, stopping per spec sec 25")
    best = int(result["scores"].argmax())
    box_raw = result["boxes"][best]
    # Same denormalisation _ground_with_langsam itself uses (visual_grounding.py ~396-403).
    if box_raw.max() <= 1.0:
        box = np.array([box_raw[0] * w, box_raw[1] * h, box_raw[2] * w, box_raw[3] * h])
    else:
        box = np.asarray(box_raw, dtype=float)
    mask = np.asarray(result["masks"][best]).astype(bool)
    score = float(result["scores"][best])
    return rgb, mask, box, score


def _crop(rgb, mask, box, pad_frac=0.65):
    """One crop, computed once from the real mask's own bbox, reused
    identically for all three panels (spec sec 14 -- same image, same crop)."""
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    h, w = y1 - y0, x1 - x0
    py, px = int(h * pad_frac) + 8, int(w * pad_frac) + 8
    cy0, cy1 = max(0, y0 - py), min(rgb.shape[0], y1 + py + 1)
    cx0, cx1 = max(0, x0 - px), min(rgb.shape[1], x1 + px + 1)
    rgb_c = rgb[cy0:cy1, cx0:cx1]
    mask_c = mask[cy0:cy1, cx0:cx1]
    box_c = box - np.array([cx0, cy0, cx0, cy0])
    return rgb_c, mask_c, box_c


def _panel_image(ax, rgb_c):
    h, w = rgb_c.shape[:2]
    ax.imshow(rgb_c, extent=[0, 1, 0, h / w], zorder=1)
    ax.set_xlim(0, 1); ax.set_ylim(-0.02, h / w + 0.02)
    ax.set_aspect("equal")
    ax.axis("off")
    return h / w


def _box_rect(box_c, w_px, h_px, ar):
    x0, y0, x1, y1 = box_c
    # image pixel coords (y down) -> axes data coords (extent 0..1 x, 0..ar y, y up)
    fx0, fx1 = x0 / w_px, x1 / w_px
    fy0, fy1 = ar * (1 - y1 / h_px), ar * (1 - y0 / h_px)
    return fx0, fy0, fx1 - fx0, fy1 - fy0


def build():
    rgb, mask, box, score = _run_detection()
    rgb_c, mask_c, box_c = _crop(rgb, mask, box)
    h_px, w_px = rgb_c.shape[:2]

    FIG_W_IN, FIG_H_IN = fs.TEXT_WIDTH_IN, 3.55
    PANEL_W, GAP, LEFT0 = 0.230, 0.140, 0.020
    TOP, BOT = 0.850, 0.280

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor="white", constrained_layout=False)

    panel_x0 = [LEFT0 + k * (PANEL_W + GAP) for k in range(3)]
    axes = []
    for x0 in panel_x0:
        ax = fig.add_axes([x0, BOT, PANEL_W, TOP - BOT])
        axes.append(ax)

    # ---- panel (a): visual scene ----
    ax = axes[0]
    ar = _panel_image(ax, rgb_c)
    ax.text(0.5, ar + 0.20, f'"{QUERY}"', fontsize=11, fontweight="bold",
             ha="center", va="bottom", color=INK)
    ax.text(0.5, ar + 0.09, "language query", fontsize=7.5, style="italic",
             ha="center", va="bottom", color=MUTED)
    ax.text(0.5, -0.10, "Visual scene", fontsize=9.5, ha="center", va="top", color=INK)
    fs.panel_label(ax, "a", x=0.0, y=ar + 0.30)

    # ---- panel (b): open-set detection ----
    ax = axes[1]
    ar = _panel_image(ax, rgb_c)
    bx, by, bw, bh = _box_rect(box_c, w_px, h_px, ar)
    ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, edgecolor=BOX_COLOR,
                            linewidth=1.8, zorder=5))
    ax.text(0.5, ar + 0.20, "Open-set detection", fontsize=10.5, fontweight="medium",
             ha="center", va="bottom", color=INK)
    ax.text(0.5, ar + 0.09, "detector output: bounding box", fontsize=7.5, style="italic",
             ha="center", va="bottom", color=MUTED)
    # annotation below the image, leader-lined up to the box's bottom edge --
    # never over the mug or the box itself (spec sec 8).
    ax.annotate("The box bounds everything\nthe next stage can return.",
                xy=(bx + bw / 2, by), xytext=(0.5, -0.12), textcoords=("axes fraction", "data"),
                fontsize=7.8, ha="center", va="top", color=BOX_COLOR,
                arrowprops=dict(arrowstyle="-", shrinkA=0, shrinkB=3, lw=0.9, color=BOX_COLOR))
    fs.panel_label(ax, "b", x=0.0, y=ar + 0.30)

    # ---- panel (c): promptable segmentation ----
    ax = axes[2]
    ar = _panel_image(ax, rgb_c)
    # same box, faded/secondary -- it is now the prompt, not the result.
    ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, edgecolor=BOX_COLOR,
                            linewidth=1.2, linestyle=(0, (3, 2)), alpha=0.55, zorder=4))
    from matplotlib.colors import to_rgb
    overlay = np.zeros((*mask_c.shape, 4))
    rgb_col = to_rgb(MASK_COLOR)
    overlay[mask_c] = (*rgb_col, 0.50)
    ax.imshow(overlay, extent=[0, 1, 0, ar], zorder=5)
    ax.contour(np.flipud(mask_c).astype(float), levels=[0.5], colors=[MASK_COLOR],
               linewidths=1.4, extent=[0, 1, 0, ar], zorder=6)
    ax.text(0.5, ar + 0.20, "Promptable segmentation", fontsize=10.5, fontweight="medium",
             ha="center", va="bottom", color=INK)
    ax.text(0.5, ar + 0.09, "receives: bounding box (prompt)", fontsize=7.5, style="italic",
             ha="center", va="bottom", color=MUTED)
    mys, mxs = np.where(mask_c)
    label_x, label_y = mxs.mean() / w_px, ar * (1 - mys.min() / h_px)
    ax.annotate("Grounded region", xy=(label_x, label_y), xytext=(0.5, -0.12),
                textcoords="axes fraction", fontsize=8.2, fontweight="bold", ha="center",
                va="top", color=MASK_COLOR,
                arrowprops=dict(arrowstyle="-", shrinkA=0, shrinkB=3, lw=0.9, color=MASK_COLOR))
    fs.panel_label(ax, "c", x=0.0, y=ar + 0.30)

    # ---- causal arrows between panels + bottom statement ----
    # Drawn on a dedicated overlay axes added AFTER the panel axes, so these
    # never render underneath a panel's (opaque) image even if a label's
    # rendered width edges slightly past its gap's nominal boundary.
    root = fig.add_axes([0, 0, 1, 1]); root.set_axis_off()
    root.set_xlim(0, 1); root.set_ylim(0, 1)
    root.patch.set_alpha(0.0)

    arrow_y = 0.62
    arrow_specs = [
        (panel_x0[0] + PANEL_W + 0.014, panel_x0[1] - 0.014, "open-set\ndetection", INK, None),
        (panel_x0[1] + PANEL_W + 0.014, panel_x0[2] - 0.014, "promptable\nsegmentation", INK, "box = prompt"),
    ]
    for x_start, x_end, label, colour, sublabel in arrow_specs:
        root.add_patch(FancyArrowPatch((x_start, arrow_y), (x_end, arrow_y),
                                         arrowstyle="-|>", mutation_scale=10,
                                         color=colour, linewidth=1.2, zorder=5))
        cx = (x_start + x_end) / 2
        root.text(cx, arrow_y + 0.042, label, fontsize=7.2, ha="center", va="bottom",
                   color=colour, linespacing=1.25)
        if sublabel:
            root.text(cx, arrow_y - 0.042, sublabel, fontsize=7.2, ha="center", va="top",
                       color=BOX_COLOR, style="italic")

    root.text(0.5, 0.095,
              "The same pipeline receives object-level and part-level queries. "
              "Chapter 5 measures what it returns for each.",
              fontsize=9.5, ha="center", va="center", color=INK)

    return fig, score


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] source capture: {CAPTURE_PATH} (real robot head-camera RGB, grounding_rgb)")
    print(f"[{FIGURE_ID}] real detector call: visual_grounding.VisualAffordanceGrounder._langsam_predict, "
          f"query={QUERY!r}")
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig, score = build()
    print(f"[{FIGURE_ID}] real detection score: {score:.4f}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("A")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
    print(f"[{FIGURE_ID}] -- communication check still required: view the PNG, blind-read it, "
          f"compare against INTENT, then call qa.record_communication_check(...).")
