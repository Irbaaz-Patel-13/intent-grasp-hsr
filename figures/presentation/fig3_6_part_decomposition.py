"""
fig3_6_part_decomposition.py -- Figure 3.6, "Geometric Part Decomposition
and Evidence Gating" (dissertation print variant: white background, near-
black ink, restrained accents, no decoration).

Real-data pipeline (identical calls to the live, unmodified project code):
  raw depth backproject -> scene_objects.find_objects() isolates the mug
  (1942 real points, `obj`) -> part_adaptive.find_components(obj,
  z_table=plane_z) splits it into up to 5 named structural candidates ->
  part_adaptive.describe_components() measures each one.

This script performs that isolation step itself (same functions, same
capture file) to recover the FULL 1942-point isolated object cloud for the
"complete capture" panel; the 4-component decomposition itself is loaded
via new_a_part_decomposition.load_real_components(), which calls the exact
same som_part_selection._load_and_isolate() -> part_adaptive chain already
cross-verified byte-identical against bc_mug.log / ax4_mug.log /
q6_intent_mug.log. Both paths run find_components() on the same `obj`
array with the same z_table, so the two are guaranteed consistent.

Four real components (this trial):
  main_body            1390 pts, 18 mm, evidence=SUPPORTED
  top_protrusion         147 pts,  7 mm, evidence=LOW
  lateral_protrusion      53 pts,  4 mm, evidence=NOISE
  lateral_protrusion_1    36 pts,  3 mm, evidence=NOISE
  (sum 1626 of 1942 isolated points)

The remaining 316 points are real, isolated-object points that did not pass
ANY component's geometric membership test inside find_components() (not a
z_table/floor exclusion -- verified numerically: 0 of the 316 are below the
z_table+5mm floor; all 316 simply failed every body/rim/top/lateral test).
They are drawn as faint uncoloured context points in the decomposition
panel so the mug's silhouette stays continuous, and are never counted,
coloured, or labelled as a component.

rim_ring is a fifth possible component in find_components() whose geometric
formation test (radial coefficient-of-variation + angular arc-coverage)
did not pass on this capture, so it never entered the candidate set at all.
This is NOT an evidence-gate rejection (NOISE/LOW) and is captioned as such.

lateral_protrusion / lateral_protrusion_1 are labelled ONLY by their literal
computational names. Their real projected position in this capture sits
near the mug's rim/opening, not on the visible loop handle -- whether this
is the occluded lower loop or something else is NOT verified here.

evaluation_outputs/part_adaptive_mug_evaluation.json is NOT used anywhere
in this script (confirmed-degenerate run, different source capture).

Run: python fig3_6_part_decomposition.py
Output: generated_assets/fig3_6/fig3_6_part_decomposition.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from scipy.spatial.transform import Rotation

import figstyle as fs
import new_a_part_decomposition as na
import scene3d as s3
from intent_grasp import scene_objects as so
# ---------------------------------------------------------------- palette
BG = "#FFFFFF"
INK = "#141414"
INK_FAR = "#8A8D93"     # far-depth end of the neutral point-cloud shading
MUTED = "#5A5E66"
FAINT = "#C7CAD0"
CONTEXT = "#D8DADD"     # the 316 real, unassigned context points
ACCEPTED = "#1E7B34"
CANDIDATE = "#B7791F"
REJECTED = "#C0392B"
REJECTED_2 = "#7B241C"
MONO = "DejaVu Sans Mono"
SANS = fs.FONT

FIG_W_IN, FIG_H_IN = 6.27, 4.85
DPI = 300

COMPONENT_COLOR = {
    "main_body": INK,
    "top_protrusion": CANDIDATE,
    "lateral_protrusion": REJECTED,
    "lateral_protrusion_1": REJECTED_2,
}
EVIDENCE_LABEL = {"ok": "SUPPORTED", "LOW": "LOW", "NOISE": "NOISE"}

# Chosen close to CAM_ISO (elevation 25, azimuth 135 -- the project's
# standard isometric view) but nudged (elevation 22, azimuth 145) after a
# numeric check: at exact CAM_ISO, lateral_protrusion_1's real points
# project INSIDE main_body's on-screen x-span (embedded in its silhouette
# from that particular angle -- a real occlusion artifact of that
# viewpoint). At this nearby angle both lateral fragments fall fully
# outside main_body's projected bounding box while the view still reads as
# the same familiar oblique mug shot -- verified by re-projecting the real
# 1942-point object and comparing per-component pixel bounding boxes.
CAM_MAIN = dict(kind="perspective", elevation_deg=22.0, azimuth_deg=145.0, fov_deg=40.0)
CANVAS = 1400


def load_full_isolated_cloud(cap_path=na.CAP_PATH):
    """Reproduces the object-isolation half of
    som_part_selection._load_and_isolate() (same functions, same capture)
    to recover the full 1942-point isolated object cloud -- the decomposed
    4-component set is a strict subset of exactly this array."""
    d = np.load(cap_path, allow_pickle=True)
    R = Rotation.from_quat(np.asarray(d["tf_quat"], float).ravel()).as_matrix()
    t = np.asarray(d["tf_trans"], float).ravel()
    depth = d["depth"].astype(float)
    K = np.asarray(d["K"], float)
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (depth > 0.05) & (depth < 4.0)
    z = depth[ok]
    x = (u[ok] - K[0, 2]) * z / K[0, 0]
    y = (v[ok] - K[1, 2]) * z / K[1, 1]
    pts = (R @ np.stack([x, y, z], -1).T).T + t
    table, objs = so.find_objects(pts)
    if table is None or not objs:
        raise SystemExit("no table/object found in %s" % cap_path)
    return objs[0]["points"], table["plane_z"]


def _context_points(obj, comp, plane_z):
    """The real isolated-object points that find_components() did not
    assign to any of the 4 components -- computed by exact-value set
    difference against the same array (every component array is a literal
    boolean-indexed slice of `obj`, so exact float match is safe here)."""
    used = np.vstack(list(comp.values()))
    used_set = set(map(tuple, np.round(used, 8)))
    pool = obj[obj[:, 2] > plane_z + 0.005]
    mask = np.array([tuple(np.round(p, 8)) not in used_set for p in pool])
    return pool[mask]


def _shared_view(obj):
    center = obj.mean(axis=0)
    extent = float(np.linalg.norm(obj.max(axis=0) - obj.min(axis=0))) * 1.3
    return s3.view_and_projection(CAM_MAIN, center, extent, aspect=1.0)


def _proj(pts, view, proj, canvas=CANVAS):
    px, py, depth, valid = s3.project_points(pts, view, proj, canvas, canvas)
    if not valid.all():
        raise RuntimeError("real points fell behind CAM_MAIN -- check framing")
    return px, py, depth


def render_capture_panel(ax, obj, view, proj):
    """(a) The complete real captured geometry, neutral, depth-shaded so the
    surface reads as a coherent 3D shape rather than flat scattered dots.
    Depth shading is a real derived quantity (each point's own distance
    along the camera view axis, from the same real projection matrices used
    everywhere else in this figure) -- not a synthetic/aesthetic gradient."""
    px, py, depth = _proj(obj, view, proj)
    dn = (depth - depth.min()) / max(depth.max() - depth.min(), 1e-9)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("depth_ink", [INK, INK_FAR])
    colors = cmap(1.0 - dn)  # nearest points darkest
    ax.scatter(px, py, s=3.6, c=colors, linewidths=0, zorder=2)
    ax.set_title("(a) complete captured geometry", fontsize=6.6, family=SANS,
                 color=INK, loc="left", pad=3)
    _finish_3d_axes(ax, px, py)
    return px, py


def render_decomposition_panel(ax, obj, comp, desc, context_pts, view, proj):
    """(b) SAME real geometry, SAME camera -- the 4 real components
    highlighted, the ~316 unassigned real points kept as faint context so
    the silhouette stays continuous (not 4 clouds floating in empty
    space)."""
    if len(context_pts):
        cx, cy, _ = _proj(context_pts, view, proj)
        ax.scatter(cx, cy, s=3.0, color=CONTEXT, linewidths=0, zorder=1)

    proj_xy = {}
    for name in ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"]:
        px, py, _ = _proj(comp[name], view, proj)
        proj_xy[name] = (px, py)
        color = COMPONENT_COLOR[name]
        if name in ("lateral_protrusion", "lateral_protrusion_1"):
            # Small components get an outline + slightly larger marker to
            # raise contrast against the dense body cloud -- real point
            # positions are untouched, only the marker's own size/edge.
            ax.scatter(px, py, s=15, facecolors=color, edgecolors=INK,
                       linewidths=0.5, zorder=4)
        else:
            ax.scatter(px, py, s=3.2, color=color, linewidths=0, zorder=2)

    ax.set_title("(b) decomposition (same geometry, same view)", fontsize=6.6,
                 family=SANS, color=INK, loc="left", pad=3)
    all_px = np.concatenate([v[0] for v in proj_xy.values()])
    all_py = np.concatenate([v[1] for v in proj_xy.values()])
    _finish_3d_axes(ax, all_px, all_py)
    return proj_xy


def _finish_3d_axes(ax, px, py, pad_frac=0.10):
    xr, yr = px.max() - px.min(), py.max() - py.min()
    padx, pady = xr * pad_frac, yr * pad_frac
    ax.set_xlim(px.min() - padx, px.max() + padx)
    ax.set_ylim(py.max() + pady, py.min() - pady)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(FAINT)
        spine.set_linewidth(0.6)


def render_fragment_inset(ax, name, comp, context_pts, view, proj, box_color):
    """A true zoom crop of the SAME real projected points: only this
    component's real points, plus nearby real context points already
    computed for panel (b), restricted to a tight bounding box around the
    component. No points are moved, invented, or redrawn as a solid
    shape."""
    fx, fy, _ = _proj(comp[name], view, proj)
    cx, cy, _ = _proj(context_pts, view, proj) if len(context_pts) else (np.array([]), np.array([]), None)
    mx, my, _ = _proj(comp["main_body"], view, proj)

    pad_x = (fx.max() - fx.min()) * 0.45 + 22
    pad_y = (fy.max() - fy.min()) * 0.45 + 22
    x0, x1 = fx.min() - pad_x, fx.max() + pad_x
    y0, y1 = fy.min() - pad_y, fy.max() + pad_y

    if len(cx):
        m = (cx >= x0) & (cx <= x1) & (cy >= y0) & (cy <= y1)
        ax.scatter(cx[m], cy[m], s=4.0, color=CONTEXT, linewidths=0, zorder=1)
    mbody = (mx >= x0) & (mx <= x1) & (my >= y0) & (my <= y1)
    ax.scatter(mx[mbody], my[mbody], s=3.5, color=INK, alpha=0.55, linewidths=0, zorder=2)
    ax.scatter(fx, fy, s=26, facecolors=box_color, edgecolors=BG, linewidths=0.9, zorder=4)

    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(box_color)
        spine.set_linewidth(1.1)
    d = na.load_real_components()[1][name]
    ax.set_title(f"{name}\n{d['n']} pts, {d['closing_width_mm']} mm, NOISE",
                 fontsize=5.4, family=SANS, color=box_color, loc="center", pad=2)
    return x0, x1, y0, y1


def mark_source_region(ax_parent, x0, x1, y0, y1, color):
    ax_parent.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                   edgecolor=color, linewidth=0.9, zorder=6))


def render_evidence_plot(ax, desc):
    ax.set_facecolor(BG)
    ax.set_yscale("log")
    NOISE_N, NOISE_W_MM = na.NOISE_N, na.NOISE_W_MM
    LOW_N, LOW_W_MM = na.LOW_N, na.LOW_W_MM
    xmax = max(d["closing_width_mm"] for d in desc.values()) * 1.35

    ax.axvspan(0, LOW_W_MM, facecolor=CANDIDATE, alpha=0.07, zorder=0)
    ax.axhspan(1, LOW_N, facecolor=CANDIDATE, alpha=0.07, zorder=0)
    ax.axvspan(0, NOISE_W_MM, facecolor=REJECTED, alpha=0.10, zorder=1)
    ax.axhspan(1, NOISE_N, facecolor=REJECTED, alpha=0.10, zorder=1)

    ax.axvline(NOISE_W_MM, color=REJECTED, linewidth=1.0, linestyle=(0, (3, 2)), zorder=2)
    ax.axhline(NOISE_N, color=REJECTED, linewidth=1.0, linestyle=(0, (3, 2)), zorder=2)
    ax.axvline(LOW_W_MM, color=CANDIDATE, linewidth=0.9, linestyle=(0, (1, 2)), zorder=2)
    ax.axhline(LOW_N, color=CANDIDATE, linewidth=0.9, linestyle=(0, (1, 2)), zorder=2)

    label_bbox = dict(facecolor=BG, edgecolor="none", alpha=0.85, pad=0.8)
    ax.text(NOISE_W_MM + 0.12, 1.05, f"NOISE: n<{NOISE_N} or w<{NOISE_W_MM:.0f} mm",
            color=REJECTED, fontsize=5.0, family=SANS, rotation=90, va="bottom", bbox=label_bbox, zorder=3)
    ax.text(LOW_W_MM + 0.12, 1.05, f"LOW: n<{LOW_N} or w<{LOW_W_MM:.0f} mm",
            color=CANDIDATE, fontsize=5.0, family=SANS, rotation=90, va="bottom", bbox=label_bbox, zorder=3)

    label_layout = {
        "main_body": ((-8, 8), "right", "bottom"),
        "top_protrusion": ((0, 34), "center", "bottom"),
        "lateral_protrusion": ((48, -4), "left", "center"),
        "lateral_protrusion_1": ((-6, -30), "center", "top"),
    }
    for name, d in desc.items():
        color = COMPONENT_COLOR[name]
        (ox, oy), ha, va = label_layout[name]
        ax.scatter([d["closing_width_mm"]], [d["n"]], s=20, color=color, zorder=5,
                   edgecolors=BG, linewidths=0.6)
        ax.annotate(f"{name}\n{d['closing_width_mm']} mm, {d['n']} pt",
                    (d["closing_width_mm"], d["n"]), color=color, fontsize=5.0,
                    family=SANS, ha=ha, va=va, linespacing=1.2,
                    xytext=(ox, oy), textcoords="offset points",
                    bbox=label_bbox, zorder=6)

    ax.set_xlim(0, xmax)
    ax.set_ylim(1, 3000)
    ax.set_xlabel("closing width, mm", color=MUTED, fontsize=6.2, family=SANS)
    ax.set_ylabel("point count, n (log)", color=MUTED, fontsize=6.2, family=SANS)
    ax.tick_params(colors=MUTED, labelsize=5.6, length=2.5)
    for spine in ax.spines.values():
        spine.set_color(FAINT)
        spine.set_linewidth(0.7)


def render_action_gate(ax, desc):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    d1, d2 = desc["lateral_protrusion"], desc["lateral_protrusion_1"]

    def node(y, label, fam=SANS, color=INK, size=6.6, weight="bold"):
        ax.text(0.5, y, label, ha="center", va="center", family=fam, color=color,
                fontsize=size, weight=weight, transform=ax.transAxes)

    def arrow(y0, y1):
        ax.annotate("", xy=(0.5, y1), xytext=(0.5, y0), xycoords="axes fraction",
                    textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=0.8, mutation_scale=5))

    node(0.96, 'target_part = "handle"', fam=MONO, size=6.4)
    arrow(0.90, 0.83)
    node(0.79, "candidate geometric components", size=5.4, weight="normal", color=MUTED)
    arrow(0.75, 0.685)
    ax.text(0.5, 0.605,
            f"lateral_protrusion\n{d1['n']} pts \u00b7 {d1['closing_width_mm']} mm \u00b7 NOISE\n\n"
            f"lateral_protrusion_1\n{d2['n']} pts \u00b7 {d2['closing_width_mm']} mm \u00b7 NOISE",
            ha="center", va="center", family=MONO, color=REJECTED, fontsize=5.4,
            weight="bold", linespacing=1.5, transform=ax.transAxes)
    arrow(0.435, 0.365)
    node(0.30, "REFUSED", color=REJECTED, size=11)
    arrow(0.24, 0.175)
    node(0.11, "no valid handle component", size=5.4, weight="normal", color=MUTED)

    ax.text(0.5, -0.03, "semantic request \u2260 geometric evidence", ha="center", va="top",
            family=SANS, color=MUTED, fontsize=5.2, style="italic", transform=ax.transAxes)


def render_process_strip(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    stages = ["real RGB-D capture", "object isolation", "geometric decomposition",
              "component measurement", "evidence gate", "part binding / action gate"]
    n = len(stages)
    xs = np.linspace(0.5 / n, 1 - 0.5 / n, n)
    for i, (x, label) in enumerate(zip(xs, stages)):
        ax.text(x, 0.5, label, ha="center", va="center", family=SANS, color=INK,
                fontsize=5.0, transform=ax.transAxes)
        if i < n - 1:
            ax.annotate("", xy=(xs[i + 1] - 0.5 / n, 0.5), xytext=(x + 0.5 / n, 0.5),
                        xycoords="axes fraction", textcoords="axes fraction",
                        arrowprops=dict(arrowstyle="-|>", color=FAINT, linewidth=0.7, mutation_scale=4.5))


def render(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("fig3_6"), "fig3_6_part_decomposition.png")
    comp, desc = na.load_real_components()
    obj, plane_z = load_full_isolated_cloud()
    context_pts = _context_points(obj, comp, plane_z)
    view, proj_m, eye = _shared_view(obj)

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI, facecolor=BG)

    ax_strip = fig.add_axes([0.02, 0.965, 0.96, 0.03])
    render_process_strip(ax_strip)

    ax_a = fig.add_axes([0.020, 0.525, 0.335, 0.415])
    render_capture_panel(ax_a, obj, view, proj_m)

    ax_b = fig.add_axes([0.375, 0.525, 0.335, 0.415])
    proj_xy = render_decomposition_panel(ax_b, obj, comp, desc, context_pts, view, proj_m)

    ax_inset1 = fig.add_axes([0.735, 0.760, 0.245, 0.180])
    box1 = render_fragment_inset(ax_inset1, "lateral_protrusion", comp, context_pts, view, proj_m, REJECTED)
    mark_source_region(ax_b, *box1, color=REJECTED)

    ax_inset2 = fig.add_axes([0.735, 0.525, 0.245, 0.180])
    box2 = render_fragment_inset(ax_inset2, "lateral_protrusion_1", comp, context_pts, view, proj_m, REJECTED_2)
    mark_source_region(ax_b, *box2, color=REJECTED_2)

    ax_evid = fig.add_axes([0.075, 0.145, 0.415, 0.335])
    render_evidence_plot(ax_evid, desc)

    ax_gate = fig.add_axes([0.575, 0.100, 0.400, 0.400])
    render_action_gate(ax_gate, desc)

    fig.text(0.02, 0.075,
            "rim_ring \u2014 not geometrically formed in this capture (its formation test failed; "
            "this is distinct from evidence-gate NOISE/LOW rejection).",
            ha="left", va="top", family=SANS, color=MUTED, fontsize=4.8)
    fig.text(0.02, 0.050,
            "Capture: captures_pairs_2/cap_mug_head_near.npz \u00b7 1942 real isolated points \u00b7 "
            "measurements cross-verified against bc_mug.log, ax4_mug.log, q6_intent_mug.log.",
            ha="left", va="top", family=SANS, color=MUTED, fontsize=4.8)
    fig.text(0.02, 0.025,
            "Grey context points (316) are real, isolated points that matched no component's geometric "
            "test; never counted or coloured as evidence.",
            ha="left", va="top", family=SANS, color=MUTED, fontsize=4.8)

    fig.savefig(out_path, facecolor=BG)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(out_path=args.out)
    print(f"fig3_6 written to {path}")
