"""
new_a_part_decomposition.py -- NEW-A: Part Decomposition (replaces the
slide-10 object-segmentation figure, which argued Stage-2 grounding, not
this project's actual contribution).

Scientific claim: on a real mug capture, shape-adaptive geometric
decomposition splits the object into 4 real components. The handle is not
one clean, graspable region -- it fragments into two separate clusters
(lateral_protrusion, lateral_protrusion_1), and BOTH independently fail the
evidence gate's NOISE threshold (n<60 points or width<6mm), so the system
refuses to select it rather than substitute a different part silently.
Supporting evidence: live re-run of the real, unmodified pipeline chain
  (`som_part_selection._load_and_isolate` -> `part_adaptive.find_components`
  -> `part_adaptive.describe_components`) on
  `captures_pairs_2/cap_mug_head_near.npz`, producing n/width values that
  match `bc_mug.log`/`ax4_mug.log`/`q6_intent_mug.log` exactly: main_body
  1390pts/18mm, top_protrusion 147pts/7mm(LOW), lateral_protrusion 53pts/4mm
  (NOISE), lateral_protrusion_1 36pts/3mm(NOISE).
NOTE: `evaluation_outputs/part_adaptive_mug_evaluation.json` is a DEGENERATE
  run (all-zero extent/eigvals, empty components) -- do not cite it as a
  source for this or any other figure; the live re-run above is the real
  source, cross-verified against three independent log files.
Required real data: all 4 real component point clouds (this trial's live
  decomposition output), their real n/width values, the real NOISE/LOW
  gate thresholds (part_adaptive.py:521-524) -- all used directly.
Required diagrammatic elements: none. The CAM_ISO projection of the real
  component point cloud is a direct geometric projection (scene3d.py),
  not a schematic.

Run: python new_a_part_decomposition.py
Output: generated_assets/new_a/new_a_part_decomposition.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull

import figlayout as fl
import figstyle as fs
from intent_grasp import part_adaptive as pa
import scene3d as s3
from intent_grasp import som_part_selection as sps
from intent_grasp.paths import WORKSPACE
# Presentation-level label for the real code's evidence states. NOISE is the
# code's own word (part_adaptive.py:524); "REFUSED" is the ACTION GATE
# outcome (part_adaptive.py:626-627, ev=="NOISE" -> REJECTED), kept visually
# distinct from the evidence label itself so neither term silently replaces
# the other on the slide.
EVIDENCE_LABEL = {"ok": "SUPPORTED", "LOW": "LOW", "NOISE": "NOISE"}
EVIDENCE_COLOR_KEY = {"ok": "ACCEPTED", "LOW": "CANDIDATE", "NOISE": "REJECTED"}

CAP_PATH = os.path.join(str(WORKSPACE), "captures_pairs_2", "cap_mug_head_near.npz")
NOISE_N, NOISE_W_MM = 60, 6.0
LOW_N, LOW_W_MM = 120, 10.0

# part_adaptive.py:538-547 -- RELATION_HINTS, the real string-match table the
# reasoning layer's target_part is bound against (NOT geometry). Both handle
# fragments key off the same "lateral_protrusion" hint entry; the trailing
# "_1" is DBSCAN's own label order (find_components(), sorted(set(labels))),
# not a semantic distinction -- hence "#1"/"#2" here rather than treating
# the suffix as meaningful.
REJECTED_2 = "#B4433B"  # a second, darker shade of fs.REJECTED for fragment #2
COMPONENT_COLOR = {
    "main_body": fs.INK,
    "top_protrusion": fs.CANDIDATE,
    "lateral_protrusion": fs.REJECTED,
    "lateral_protrusion_1": REJECTED_2,
}
COMPONENT_LABEL = {
    "main_body": "main_body",
    "top_protrusion": "top_protrusion",
    "lateral_protrusion": "handle #1 (lateral_protrusion)",
    "lateral_protrusion_1": "handle #2 (lateral_protrusion_1)",
}
# Per NEW-A revision 5: label offsets are looked up per real component name,
# not silently defaulted -- a future object (NEW-E/NEW-G) with an unregistered
# component name must fail loudly here rather than render overlapping labels.
LABEL_OFFSET_PT = {
    "main_body": (10, 8), "top_protrusion": (10, 8),
    "lateral_protrusion": (10, 16), "lateral_protrusion_1": (10, -26),
}


def get_label_offset(name):
    if name not in LABEL_OFFSET_PT:
        raise KeyError(
            f"LABEL_OFFSET_PT has no entry for component {name!r} -- add one explicitly "
            f"rather than letting it silently collide with another label")
    return LABEL_OFFSET_PT[name]


def load_real_components():
    rgb, comp, desc, K, extr = sps._load_and_isolate(CAP_PATH)
    return comp, desc


def load_real_components_with_image():
    return sps._load_and_isolate(CAP_PATH)


def render_left_panel(ax, comp, desc, width=1300, height=1300):
    all_pts = np.vstack(list(comp.values()))
    center = all_pts.mean(axis=0)
    extent = float(np.linalg.norm(all_pts.max(axis=0) - all_pts.min(axis=0))) * 1.15
    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=1.0)

    ax.set_facecolor(fs.SLIDE_BG)
    for name, pts in comp.items():
        px, py, depth, valid = s3.project_points(pts, view, proj, width, height)
        on = valid & (px > 0) & (px < width) & (py > 0) & (py < height)
        color = COMPONENT_COLOR.get(name, fs.MUTED)
        ax.scatter(px[on], py[on], s=5, color=color, linewidths=0, zorder=2)

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.set_title("Real mug point cloud, real decomposition (CAM_ISO)", color=fs.INK,
                 fontsize=12, weight="bold", family=fs.FONT)


def render_left_legend(ax, desc):
    """Legend lives in its own axes below the point cloud -- not overlaid on
    it -- so it never crowds the data (flagged: 'legend was moved once and
    still crowds the cloud')."""
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    order = ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"]
    positions = [(0.0, 0.72), (0.52, 0.72), (0.0, 0.22), (0.52, 0.22)]
    for name, (lx, ly) in zip(order, positions):
        d = desc[name]
        color = COMPONENT_COLOR.get(name, fs.MUTED)
        ax.scatter([lx + 0.015], [ly], s=45, color=color, transform=ax.transAxes, zorder=6, clip_on=False)
        ax.text(lx + 0.05, ly, f"{COMPONENT_LABEL[name]}\n{d['n']}pts / {d['closing_width_mm']}mm",
                transform=ax.transAxes, color=color, fontsize=10, weight="bold", family=fs.FONT,
                va="center", zorder=6, linespacing=1.25)


def render_right_panel(ax, desc):
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_yscale("log")

    xmax = max(d["closing_width_mm"] for d in desc.values()) * 1.35
    # One hatched band per threshold, not stacked alpha fills -- overlapping
    # translucent color fills rendered muddy brown where red and amber
    # regions crossed. Hatching with facecolor="none" never blends.
    ax.axvspan(0, LOW_W_MM, facecolor="none", edgecolor=fs.CANDIDATE, hatch="\\", linewidth=0,
               alpha=0.4, zorder=0)
    ax.axhspan(1, LOW_N, facecolor="none", edgecolor=fs.CANDIDATE, hatch="\\", linewidth=0,
               alpha=0.4, zorder=0)
    ax.axvspan(0, NOISE_W_MM, facecolor="none", edgecolor=fs.REJECTED, hatch="/", linewidth=0,
               alpha=0.55, zorder=1)
    ax.axhspan(1, NOISE_N, facecolor="none", edgecolor=fs.REJECTED, hatch="/", linewidth=0,
               alpha=0.55, zorder=1)

    ax.axvline(NOISE_W_MM, color=fs.REJECTED, linewidth=1.4, linestyle=(0, (4, 2)), zorder=2)
    ax.axhline(NOISE_N, color=fs.REJECTED, linewidth=1.4, linestyle=(0, (4, 2)), zorder=2)
    ax.axvline(LOW_W_MM, color=fs.CANDIDATE, linewidth=1.2, linestyle=(0, (2, 2)), zorder=2)
    ax.axhline(LOW_N, color=fs.CANDIDATE, linewidth=1.2, linestyle=(0, (2, 2)), zorder=2)

    label_bbox = dict(facecolor=fs.SLIDE_BG, edgecolor="none", alpha=0.82, pad=1.5)
    ax.text(NOISE_W_MM + 0.15, 1.3, f"NOISE: n<{NOISE_N} or w<{NOISE_W_MM:.0f}mm", color=fs.REJECTED,
            fontsize=10, family=fs.FONT, rotation=90, va="bottom", bbox=label_bbox, zorder=6)
    ax.text(LOW_W_MM + 0.15, 1.3, f"LOW: n<{LOW_N} or w<{LOW_W_MM:.0f}mm", color=fs.CANDIDATE,
            fontsize=10, family=fs.FONT, rotation=90, va="bottom", bbox=label_bbox, zorder=6)

    for name, d in desc.items():
        color = COMPONENT_COLOR.get(name, fs.MUTED)
        ax.scatter([d["closing_width_mm"]], [d["n"]], s=90, color=color, zorder=5,
                   edgecolors=fs.SLIDE_BG, linewidths=1.2)
        ax.annotate(f"{COMPONENT_LABEL[name]}\n({d['closing_width_mm']}mm, {d['n']}pts)",
                    (d["closing_width_mm"], d["n"]), color=color, fontsize=10, weight="bold", family=fs.FONT,
                    xytext=get_label_offset(name), textcoords="offset points", bbox=label_bbox, zorder=6)

    ax.set_xlim(0, xmax)
    ax.set_ylim(1, 3000)
    ax.set_xlabel("closing width (mm)", color=fs.MUTED, fontsize=10, family=fs.FONT)
    ax.set_ylabel("point count (log scale)", color=fs.MUTED, fontsize=10, family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.set_title("Every real component vs. both real evidence-gate thresholds", color=fs.INK,
                 fontsize=12, weight="bold", family=fs.FONT)


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_a"), "new_a_part_decomposition.png")
    comp, desc = load_real_components()

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Part Decomposition -- the Handle Fragments, and the Gate Refuses It",
                 **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Real mug capture, real geometric decomposition -- not Stage-2 object segmentation", **fs.BODY)

    # Semantic-binding bridge: the reasoning layer's target_part string is
    # bound to a structural component by STRING MATCH against RELATION_HINTS
    # (part_adaptive.py:538-547), not by geometry -- this is a documented
    # self-correction, not a caption caveat, so it gets its own visual step.
    bridge_ax = fig.add_axes([0.035, 0.805, 0.93, 0.052])
    bridge_ax.axis("off")
    bridge_ax.add_patch(matplotlib.patches.FancyBboxPatch(
        (0.0, 0.05), 1.0, 0.9, boxstyle="round,pad=0.01,rounding_size=0.01",
        transform=bridge_ax.transAxes, facecolor=fs.CALLOUT_BG, edgecolor=fs.REASONING, linewidth=1.0))
    bridge_text = ("constraints.json  target_part=\"handle\"   -->   RELATION_HINTS "
                   "(string match, not geometry)   -->   part_adaptive.py: lateral_protrusion")
    bridge_ax.text(0.5, 0.5, bridge_text, transform=bridge_ax.transAxes, ha="center", va="center",
                    color=fs.REASONING, fontsize=11, weight="bold", family=fs.FONT)

    ax_left = fig.add_axes([0.035, 0.29, 0.44, 0.495])
    render_left_panel(ax_left, comp, desc)
    ax_leg = fig.add_axes([0.035, 0.14, 0.44, 0.13])
    render_left_legend(ax_leg, desc)

    ax_right = fig.add_axes([0.545, 0.16, 0.42, 0.605])
    render_right_panel(ax_right, desc)

    d1 = desc["lateral_protrusion"]
    d2 = desc["lateral_protrusion_1"]
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              f"The handle fragments into two clusters (#1, #2), {d1['n']} + {d2['n']} points "
              f"({d1['closing_width_mm']}mm + {d2['closing_width_mm']}mm) -- neither clears either threshold.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "\"#1\"/\"#2\" is DBSCAN's own cluster label order, not a semantic distinction. Binding step: "
              "part_adaptive.py:538-547 (RELATION_HINTS). Gate: part_adaptive.py:521-524.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Source: live re-run of part_adaptive.find_components()/describe_components() on "
              "captures_pairs_2/cap_mug_head_near.npz, cross-verified vs. bc_mug.log/ax4_mug.log/q6_intent_mug.log.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def _hull_polygon(u, v, pad_px=3):
    """Real convex hull of the real projected points -- a filled region
    derived directly from the actual component's own pixel footprint, not a
    fabricated boundary. pad_px expands the hull slightly outward so a thin
    fragment (e.g. 36 points) still reads as a region, not a sliver."""
    pts = np.column_stack([u, v])
    if len(pts) < 3:
        # too few points for a hull (shouldn't happen at these ns, but fail
        # safe rather than crash): pad each point into a small square.
        pts = np.vstack([pts + [pad_px, pad_px], pts + [-pad_px, pad_px],
                          pts + [pad_px, -pad_px], pts + [-pad_px, -pad_px]])
        hull = ConvexHull(pts)
        return pts[hull.vertices]
    hull = ConvexHull(pts)
    verts = pts[hull.vertices]
    c = verts.mean(axis=0)
    direction = verts - c
    norm = np.linalg.norm(direction, axis=1, keepdims=True)
    norm[norm == 0] = 1
    return verts + direction / norm * pad_px


def render_slide(out_path=None):
    """Slide variant: real RGB crop of the SAME mug Figure 3 segments, with
    all 4 real components rendered as filled convex-hull regions (real
    projected pixel footprint, mask-language like Figure 3 -- not scatter
    dots) and the real evidence hierarchy (SUPPORTED/LOW/NOISE, code's own
    words) shown for every component, with the action-gate outcome kept
    visually distinct from the evidence label itself."""
    out_path = out_path or os.path.join(fs.asset_dir("new_a"), "new_a_part_decomposition_slide.png")
    rgb, comp, desc, K, extr = load_real_components_with_image()

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    title_kw = {**fs.TITLE, "size": 30}
    fig.suptitle("Same Mug, Next Stage -- Which Parts Have Evidence to Grasp?", **title_kw, x=fs.MARGIN, ha="left")

    # fs.INK (near-white) is invisible as a fill against the mug's own light
    # interior -- slide-local override to fs.ACCEPTED (main_body's real
    # evidence status is "ok"/SUPPORTED anyway, so green is also semantically
    # consistent). Report variant's dark-background point cloud is unaffected
    # since it keeps using the shared COMPONENT_COLOR dict, not this one.
    slide_color = dict(COMPONENT_COLOR)
    slide_color["main_body"] = fs.ACCEPTED

    order = ["main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"]
    proj, all_u, all_v = {}, [], []
    for name in order:
        u, v, z, valid = pa.project_points_to_pixels(comp[name], K, extr)
        proj[name] = (u[valid], v[valid])
        all_u.append(u[valid])
        all_v.append(v[valid])
    all_u, all_v = np.concatenate(all_u), np.concatenate(all_v)
    pad = 40
    x0, x1 = max(int(all_u.min()) - pad, 0), min(int(all_u.max()) + pad, rgb.shape[1])
    y0, y1 = max(int(all_v.min()) - pad, 0), min(int(all_v.max()) + pad, rgb.shape[0])

    ax_left = fig.add_axes([0.03, 0.10, 0.52, 0.74])
    ax_left.imshow(rgb)
    for name in order:
        u, v = proj[name]
        hull = _hull_polygon(u, v)
        color = slide_color.get(name, fs.MUTED)
        ax_left.add_patch(Polygon(hull, closed=True, facecolor=color, alpha=0.40, edgecolor=color,
                                   linewidth=2.2, zorder=3))
    ax_left.set_xlim(x0, x1)
    ax_left.set_ylim(y1, y0)
    ax_left.set_xticks([])
    ax_left.set_yticks([])
    for spine in ax_left.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)
    ax_left.set_title("same physical mug as Figure 3", color=fs.MUTED, fontsize=16, family=fs.FONT,
                      style="italic", pad=8)

    # bridge, one smaller line
    fig.text(0.03, 0.875, 'target_part="handle" -> RELATION_HINTS (string match) -> lateral_protrusion',
              color=fs.REASONING, fontsize=16, weight="bold", family=fs.FONT)

    # Evidence hierarchy: all 4 real components, code's own evidence words.
    rows = [
        ("main_body", "main_body"), ("top_protrusion", "top_protrusion"),
        ("lateral_protrusion", "handle fragment #1"), ("lateral_protrusion_1", "handle fragment #2"),
    ]
    ax_right = fig.add_axes([0.585, 0.22, 0.39, 0.62])
    ax_right.axis("off")
    row_y = [0.93, 0.71, 0.46, 0.24]
    for (name, label), y in zip(rows, row_y):
        d = desc[name]
        color_key = EVIDENCE_COLOR_KEY[d["evidence"]]
        color = getattr(fs, color_key)
        swatch = slide_color.get(name, fs.MUTED)
        ax_right.add_patch(matplotlib.patches.Rectangle((0.0, y - 0.045), 0.03, 0.09, transform=ax_right.transAxes,
                                                          facecolor=swatch, edgecolor="none"))
        ax_right.text(0.05, y + 0.02, f"{label} -- {d['n']} pts / {d['closing_width_mm']} mm",
                      transform=ax_right.transAxes, color=fs.INK, fontsize=17, weight="bold", family=fs.FONT,
                      va="center")
        ax_right.text(0.05, y - 0.07, EVIDENCE_LABEL[d["evidence"]], transform=ax_right.transAxes, color=color,
                      fontsize=22 if d["evidence"] != "ok" else 22, weight="bold", family=fs.FONT, va="center")

    # Action-gate flow for the two NOISE components: evidence label is NOT
    # silently overwritten -- REFUSED is shown as a separate downstream step.
    ax_gate = fig.add_axes([0.585, 0.02, 0.39, 0.185])
    ax_gate.axis("off")
    ax_gate.set_xlim(0, 1)
    ax_gate.set_ylim(0, 1)
    ax_gate.text(0.0, 0.88, "evidence: NOISE (both handle fragments)", transform=ax_gate.transAxes, ha="left",
                va="center", color=fs.REJECTED, fontsize=16, family=fs.FONT)
    ax_gate.annotate("", xy=(0.30, 0.10), xytext=(0.02, 0.60), transform=ax_gate.transAxes,
                     arrowprops=dict(arrowstyle="-|>", color=fs.MUTED, linewidth=1.6))
    ax_gate.text(0.35, 0.60, "ACTION GATE:", transform=ax_gate.transAxes, ha="left", va="center", color=fs.MUTED,
                fontsize=16, family=fs.FONT)
    ax_gate.text(0.35, 0.15, "REFUSED", transform=ax_gate.transAxes, ha="left", va="center", color=fs.REJECTED,
                fontsize=48, weight="bold", family=fs.FONT)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "captures_pairs_2/cap_mug_head_near.npz", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-A part decomposition", [
        "Live re-run of part_adaptive.find_components()/describe_components() on the real capture,",
        "cross-verified against bc_mug.log / ax4_mug.log / q6_intent_mug.log (exact match).",
        "Filled regions are real convex hulls of each component's own real projected pixel footprint",
        "(part_adaptive.project_points_to_pixels) -- not scatter dots, not a fabricated segmentation.",
        "The two handle fragments are NOT merged into one region -- their disjoint hulls are the",
        "fragmentation evidence itself; do not visually imply a continuous handle.",
        "'SUPPORTED'/'LOW'/'NOISE' are the code's own evidence words (part_adaptive.py:520-524).",
        "'REFUSED' is the separate ACTION GATE outcome (part_adaptive.py:626-627, evidence==NOISE ->",
        "REJECTED) -- kept visually distinct from the evidence label; NOISE is not silently renamed.",
        "LOW (top_protrusion, 147pts/7mm) does NOT auto-refuse -- it costs -2.5 in candidate scoring",
        "(part_adaptive.py:592) but remains selectable if nothing better is available.",
        "Object identity verified this session: same physical red mug, same table/chair/room as",
        "Figure 3's anchor-trial capture -- confirmed by direct visual comparison, different capture pass.",
        "'#1'/'#2' is DBSCAN's own cluster label order, not a semantic distinction.",
        "Binding step (RELATION_HINTS) is a string match against part_adaptive.py:538-547, not geometry.",
        "Gate thresholds: part_adaptive.py:520-524. NOISE: n<60 or w<6mm. LOW: n<120 or w<10mm.",
        "evaluation_outputs/part_adaptive_mug_evaluation.json is DEGENERATE -- do not cite it.",
    ])
    return out_path, report


def render(variant="report", out_path=None):
    if variant == "report":
        return render_report(out_path=out_path)
    if variant == "slide":
        return render_slide(out_path=out_path)
    raise ValueError(f"unknown variant {variant!r}, expected 'report' or 'slide'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", choices=["report", "slide"], default="report")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(variant=args.variant, out_path=args.out)
    print(f"new_a ({args.variant}) written to {path}")
    print(report.summary())
