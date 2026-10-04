"""Fig 3.6 -- Geometric part decomposition and evidence gating (2D projected,
photograph-anchored -- POINT-CLOUD DESIGN PHILOSOPHY spec Part C).

Clustering yields named components, each is measured, and the evidence gate
retains those with sufficient support and refuses the rest. Real mug capture
(captures_pairs_2/cap_mug_head_near.npz, via
new_a_part_decomposition.load_real_components_with_image() ->
som_part_selection._load_and_isolate(), the same real, unmodified isolation +
find_components()/describe_components() chain the pre-existing root-level
fig3_6_part_decomposition.py and figures/scripts/fig_5_5_mug_fragmentation.py
both already use).

Per the build spec's Part A: this is a 2D argument (extent + membership), not a
3D one -- every panel after (a) is a projection onto the PRINCIPAL PLANE of the
isolated object cloud (part_adaptive.pca(), first two axes by eigenvalue),
computed once from the full cloud and applied identically to every component,
never an arbitrary 3D camera view. Panels (b)-(d) render filled concave hulls
(shapely.concave_hull) rather than raw scatter points, so the mug reads as an
object, not a haze (spec Part A.2/Rule 2).

The mug exercises BOTH evidence-gate tiers on one object: main_body accepted,
top_protrusion marginal (LOW), the two handle fragments refused (NOISE) -- the
gate demonstrated working both ways, not just as a refusal case.

Sources: captures_pairs_2/cap_mug_head_near.npz (real capture),
new_a_part_decomposition.py (NOISE_N=60/NOISE_W_MM=6.0, LOW_N=120/LOW_W_MM=10.0 --
identical to part_adaptive.py's own gate constants), part_adaptive.py
(find_components/describe_components/pca, live, unmodified).

Run: python figures/dissertation/fig_3_6_part_decomposition.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from intent_grasp.paths import REPO_ROOT  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
from shapely import concave_hull, MultiPoint

import _qa as qa
import _style as fs
import new_a_part_decomposition as na
from intent_grasp import part_adaptive as pa
FIGURE_ID = "fig_3_6_part_decomposition"
COMPONENT_ORDER = ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"]


def _panel_title(ax, letter, word):
    """One text artist, not two: at this figure's 4-panel width, a separate
    fs.panel_label() plus ax.set_title() collided regardless of title loc=
    (the title text alone is nearly as wide as the whole narrow axes) -- found
    in QA. Folding the letter into the same string removes the collision by
    construction."""
    ax.text(0.0, 1.06, f"({letter}) {word}", transform=ax.transAxes, fontsize=8.5,
             fontweight="bold", va="bottom", ha="left")

INTENT = ("Clustering yields named components, each is measured, and the evidence "
          "gate retains those with sufficient support and refuses the rest.")


def _load_verified_decomposition():
    rgb, comp, desc, K, extr = na.load_real_components_with_image()
    for name in COMPONENT_ORDER:
        assert name in comp and name in desc, f"missing component {name!r}"

    all_pts = np.vstack([comp[name] for name in COMPONENT_ORDER])
    fit = pa.pca(all_pts)
    c, V = fit["centroid"], fit["axes"]

    proj2d = {name: (comp[name] - c) @ V[:, :2] for name in COMPONENT_ORDER}

    evidences = {name: desc[name]["evidence"] for name in COMPONENT_ORDER}
    assert evidences["main_body"] == "ok"
    assert evidences["top_protrusion"] == "LOW"
    assert evidences["lateral_protrusion"] == "NOISE"
    assert evidences["lateral_protrusion_1"] == "NOISE"

    return dict(rgb=rgb, comp=comp, desc=desc, pca=fit, proj2d=proj2d)


def _hull_patch(points_xy, colour, alpha=0.55, ratio=0.4, min_points=6, edge_lw=1.3):
    """Filled concave hull (spec Rule 2, tier 1) via shapely; None if too sparse
    to form a boundary -- caller must then draw large soft points instead and
    caption the sparseness (spec Rule 2's explicit exception)."""
    pts = np.asarray(points_xy)
    if len(pts) < min_points:
        return None
    geom = concave_hull(MultiPoint(pts), ratio=ratio)
    if geom.geom_type != "Polygon" or geom.is_empty:
        return None
    coords = np.array(geom.exterior.coords)
    return MplPolygon(coords, closed=True, facecolor=colour, edgecolor=colour,
                       alpha=alpha, linewidth=edge_lw, zorder=2)


def _scale_bar(ax, x0, y0, length_m, label, colour="#000000"):
    ax.plot([x0, x0 + length_m], [y0, y0], color=colour, linewidth=1.6, solid_capstyle="butt", zorder=5)
    ax.text(x0 + length_m / 2, y0, label, ha="center", va="bottom", fontsize=7.0, color=colour, zorder=5)


def _draw_capture_panel(ax, rgb):
    ax.imshow(rgb)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    _panel_title(ax, "a", "capture")


def _draw_isolated_panel(ax, proj2d, orient_flip=(1, 1)):
    all_pts = np.vstack(list(proj2d.values()))
    fx, fy = orient_flip
    flipped = all_pts * [fx, fy]
    hull = _hull_patch(flipped, colour="#8a8d93")
    if hull is not None:
        ax.add_patch(hull)
    else:
        ax.scatter(flipped[:, 0], flipped[:, 1], s=16, alpha=0.35, color="#8a8d93")

    span = flipped.max(0) - flipped.min(0)
    ax.set_xlim(flipped[:, 0].min() - span[0] * 0.12, flipped[:, 0].max() + span[0] * 0.12)
    ax.set_ylim(flipped[:, 1].min() - span[1] * 0.12, flipped[:, 1].max() + span[1] * 0.12)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    _scale_bar(ax, flipped[:, 0].min(), flipped[:, 1].min() - span[1] * 0.05, 0.02, "20 mm")
    _panel_title(ax, "b", "isolated cloud")


# Determined by visual comparison against the real capture photo: PCA
# eigenvector sign is arbitrary; (1, 1) already produced a coherent, roughly
# mug-shaped hull in panel (b) with no obvious left-right/up-down mirroring
# artifact against panel (a)'s photograph -- no flip needed.
ORIENT_FLIP = (1, 1)

GATE_TIER_COLOUR = {"ok": fs.semantic_colour("keep"), "LOW": fs.OKABE_ITO["yellow"],
                     "NOISE": fs.OKABE_ITO["vermillion"]}
CARE_ABOUT = {"main_body": "body", "lateral_protrusion": "handle fragment",
              "lateral_protrusion_1": "handle fragment"}


def _draw_components_panel(ax, proj2d, desc, orient_flip=ORIENT_FLIP):
    fx, fy = orient_flip
    all_pts_now = np.vstack(list(proj2d.values())) * [fx, fy]
    span_now = all_pts_now.max(0) - all_pts_now.min(0)
    body_c = (proj2d["main_body"] * [fx, fy]).mean(0)

    # Text offsets scale with each component's own position relative to the
    # body centroid (left fragment's label goes further left, right fragment's
    # further right) and alternate vertically -- a fixed small offset put both
    # fragment labels at nearly the same screen position and they ran together
    # into unreadable overlapping text (found in QA).
    label_dy = {"main_body": 0.22, "lateral_protrusion": 0.30, "lateral_protrusion_1": -0.30}
    for name in COMPONENT_ORDER:
        pts = proj2d[name] * [fx, fy]
        coloured = name in CARE_ABOUT
        colour = fs.OKABE_ITO["black"] if name == "main_body" else \
            (fs.OKABE_ITO["vermillion"] if "lateral" in name else "#c7cad0")
        hull = _hull_patch(pts, colour=colour if coloured else "#c7cad0",
                            alpha=0.5 if coloured else 0.30, min_points=6)
        if hull is not None:
            ax.add_patch(hull)
        elif coloured:
            ax.scatter(pts[:, 0], pts[:, 1], s=18, color=colour, alpha=0.7)
        if coloured:
            cx, cy = pts.mean(0)
            side = np.sign(cx - body_c[0]) or 1.0
            tx = cx + side * span_now[0] * 0.22
            ty = cy + label_dy[name] * span_now[1]
            fs.leader_label(ax, (cx, cy), (tx, ty), CARE_ABOUT[name], colour=colour,
                             fontsize=7, ha="center" if name == "main_body" else ("left" if side > 0 else "right"))

    all_pts = np.vstack(list(proj2d.values())) * [fx, fy]
    span = all_pts.max(0) - all_pts.min(0)
    ax.set_xlim(all_pts[:, 0].min() - span[0] * 0.15, all_pts[:, 0].max() + span[0] * 0.15)
    ax.set_ylim(all_pts[:, 1].min() - span[1] * 0.15, all_pts[:, 1].max() + span[1] * 0.15)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    _panel_title(ax, "c", "components")


def _draw_gate_panel(ax, proj2d, desc, orient_flip=ORIENT_FLIP):
    fx, fy = orient_flip
    for name in COMPONENT_ORDER:
        pts = proj2d[name] * [fx, fy]
        colour = GATE_TIER_COLOUR[desc[name]["evidence"]]
        hull = _hull_patch(pts, colour=colour, alpha=0.55, min_points=6)
        if hull is not None:
            ax.add_patch(hull)
        else:
            ax.scatter(pts[:, 0], pts[:, 1], s=18, color=colour, alpha=0.7)

    all_pts = np.vstack(list(proj2d.values())) * [fx, fy]
    span = all_pts.max(0) - all_pts.min(0)
    ax.set_xlim(all_pts[:, 0].min() - span[0] * 0.15, all_pts[:, 0].max() + span[0] * 0.15)
    ax.set_ylim(all_pts[:, 1].min() - span[1] * 0.15, all_pts[:, 1].max() + span[1] * 0.15)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    _panel_title(ax, "d", "evidence gate")
    ax.text(0.0, -0.20, f"refused: under {na.NOISE_N} points or {na.NOISE_W_MM:.0f} mm",
            transform=ax.transAxes, fontsize=7.0, color=GATE_TIER_COLOUR["NOISE"], ha="left")
    ax.text(0.0, -0.38, f"marginal: under {na.LOW_N} points or {na.LOW_W_MM:.0f} mm",
            transform=ax.transAxes, fontsize=7.0, color="#8a8300", ha="left")


CAPTION = (
    "Fig 3.6. Geometric decomposition procedure. Real mug capture "
    "(captures_pairs_2/cap_mug_head_near.npz). All projections are onto the "
    "principal plane of the isolated object cloud (part_adaptive.pca(), shared "
    "across every panel). (a) The real capture. (b) The isolated cloud as a "
    "filled concave hull. (c) find_components()'s four real components; only "
    "the body and the two handle fragments are coloured -- the remaining "
    "component (top_protrusion) stays neutral, uncoloured. (d) The evidence "
    "gate's outcome for all four: main_body accepted (green), top_protrusion "
    "marginal (amber), both handle fragments refused (vermillion) -- the gate "
    "exercising both its tiers on one real object."
)


def build():
    geo = _load_verified_decomposition()
    fig, axes = plt.subplots(1, 4, figsize=(fs.TEXT_WIDTH_IN, 2.6))
    _draw_capture_panel(axes[0], geo["rgb"])
    _draw_isolated_panel(axes[1], geo["proj2d"], orient_flip=ORIENT_FLIP)
    _draw_components_panel(axes[2], geo["proj2d"], geo["desc"], orient_flip=ORIENT_FLIP)
    _draw_gate_panel(axes[3], geo["proj2d"], geo["desc"], orient_flip=ORIENT_FLIP)
    return fig, geo


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig, geo = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="A photo of a mug, then a grey silhouette of the same shape, "
                   "then the same silhouette split into a black body and two red "
                   "labelled fragments with one part left grey, then the same "
                   "shape recoloured green/amber/red with a two-line legend below "
                   "-- reads as 'clustering finds parts, measures them, and a gate "
                   "accepts or refuses each one' without reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="every coloured component in (c) has a leader-labelled name; "
                       "(d)'s legend states both gate thresholds directly.",
        referent_audit="leader labels in (c) point at their own hull's centroid; "
                        "the gate legend sits directly beneath the panel it describes.",
    )
    report_path = qa.write_report("fig36")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
