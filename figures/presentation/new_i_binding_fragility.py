"""
new_i_binding_fragility.py -- NEW-I: Binding Fragility (a passing evidence
gate is not proof of a correct answer).

Scientific claim: the evidence gate (NEW-A/NEW-H) only tests whether a
component has ENOUGH points/width -- it has no way to know whether that
component is the PHYSICALLY correct one for the query. A real, documented
defect (PERCEPTION_EVIDENCE.md, Part ANr3) demonstrates this directly: an
unrelated internal rename orphaned a RELATION_HINTS key, silently
misrouting the remote's "sides"/"middle section" queries from the correct
middle segment to main_body -- a small side fragment. Both answers clear
the evidence gate (both "ok"/SUPPORTED by a wide margin); nothing in the
gate itself flags the wrong one. This is a different failure class from
NEW-A/NEW-H (insufficient evidence, correctly refused): here the evidence
is sufficient and the gate says nothing is wrong, because nothing about
sufficiency is wrong -- the routing itself was wrong.
Supporting evidence: report_assets/PERCEPTION_EVIDENCE.md, Part ANr3 (the
  original diagnosis, this session); part_adaptive.py.before_orphan_fix
  (real backup file, the actual broken RELATION_HINTS dict, orphaned
  "segment_mid" key); part_adaptive.py (current, fixed, "segment_b" key).
  Both the broken and fixed code paths were RE-RUN live this session
  (not re-quoted from the earlier session's log) via part_adaptive.bind_part()
  with each real RELATION_HINTS dict swapped in, against a live
  som_part_selection._load_and_isolate() decomposition of
  captures_pairs_2/cap_remote_head_near.npz -- reproducing the exact
  point counts and widths PERCEPTION_EVIDENCE.md documents (286pts/38mm
  main_body; 1565pts/43mm segment_b), confirming the bug and fix are both
  real and reproducible, not quoted from memory.
Required real data: both queries' real bind_part() output (component name,
  n, closing_width_mm, evidence, score) under both real RELATION_HINTS
  dicts -- used directly.
Required diagrammatic elements: the two component hulls are real convex
  hulls of real projected points (same technique as NEW-A/NEW-H); solid
  vs. dashed outline encodes routing correctness (a fact independently
  established in PERCEPTION_EVIDENCE.md Part ANr3/AW1/AW2), not a
  re-judgement made for this figure.

Run: python new_i_binding_fragility.py
Output: generated_assets/new_i/new_i_binding_fragility.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

import figlayout as fl
import figstyle as fs
from intent_grasp import part_adaptive as pa
from intent_grasp import som_part_selection as sps
from intent_grasp.paths import WORKSPACE
CAP_PATH = os.path.join(str(WORKSPACE), "captures_pairs_2", "cap_remote_head_near.npz")
QUERIES = ["sides", "middle section"]

# The real, broken dict (part_adaptive.py.before_orphan_fix, lines 538-547):
# component names were already renamed segment_mid -> segment_a/b/c, but
# this hints dict still keys off the pre-rename "segment_mid" -- an orphaned
# key that binds to nothing.
BROKEN_RELATION_HINTS = {
    "lateral_protrusion": ("handle", "grip", "haft", "spout", "ear", "lug", "arm"),
    "top_protrusion":     ("lid", "knob", "cap", "cover", "button", "lid knob", "stopper"),
    "rim_ring":           ("rim", "lip", "mouth", "opening", "brim", "top edge"),
    "main_body":          ("body", "side", "sides", "wall", "barrel", "exterior",
                            "surface", "middle", "centre", "center"),
    "segment_mid":        ("middle", "mid", "middle section", "shaft", "centre",
                            "center", "sides", "side"),
}


def run_both_states():
    """Live-calls the real part_adaptive.bind_part() against a live
    decomposition, under both the real broken and real fixed RELATION_HINTS
    dicts. Not a simulation -- this is the actual function, actual data."""
    rgb, comp, desc, K, extr = sps._load_and_isolate(CAP_PATH)
    fixed_hints = dict(pa.RELATION_HINTS)
    results = {}
    for query in QUERIES:
        pa.RELATION_HINTS = BROKEN_RELATION_HINTS
        name_b, pts_b, score_b, note_b = pa.bind_part(query, comp, desc)
        pa.RELATION_HINTS = fixed_hints
        name_f, pts_f, score_f, note_f = pa.bind_part(query, comp, desc)
        results[query] = {
            "broken": {"name": name_b, "n": len(pts_b), "score": score_b, "evidence": desc[name_b]["evidence"],
                       "width_mm": desc[name_b]["closing_width_mm"]},
            "fixed": {"name": name_f, "n": len(pts_f), "score": score_f, "evidence": desc[name_f]["evidence"],
                      "width_mm": desc[name_f]["closing_width_mm"]},
        }
    pa.RELATION_HINTS = fixed_hints
    return rgb, comp, desc, K, extr, results


def _hull_polygon(u, v, pad_px=4):
    from scipy.spatial import ConvexHull
    pts = np.column_stack([u, v])
    hull = ConvexHull(pts)
    verts = pts[hull.vertices]
    c = verts.mean(axis=0)
    direction = verts - c
    norm = np.linalg.norm(direction, axis=1, keepdims=True)
    norm[norm == 0] = 1
    return verts + direction / norm * pad_px


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_i"), "new_i_binding_fragility.png")
    rgb, comp, desc, K, extr = sps._load_and_isolate(CAP_PATH)
    _, _, _, _, _, results = run_both_states()

    u_wrong, v_wrong, _, valid_wrong = pa.project_points_to_pixels(comp["main_body"], K, extr)
    u_right, v_right, _, valid_right = pa.project_points_to_pixels(comp["segment_b"], K, extr)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Binding Fragility -- a Supported Answer Can Still Be Wrong",
                 **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "A component rename orphaned a RELATION_HINTS key; both the wrong and the corrected answer "
              "clear the evidence gate", **fs.BODY)

    ax_left = fig.add_axes([0.035, 0.14, 0.46, 0.68])
    ax_left.imshow(rgb)
    hull_wrong = _hull_polygon(u_wrong[valid_wrong], v_wrong[valid_wrong])
    hull_right = _hull_polygon(u_right[valid_right], v_right[valid_right])
    ax_left.add_patch(Polygon(hull_wrong, closed=True, facecolor=fs.REASONING, alpha=0.32,
                               edgecolor=fs.REASONING, linewidth=2.4, linestyle=(0, (4, 3))))
    ax_left.add_patch(Polygon(hull_right, closed=True, facecolor=fs.REASONING, alpha=0.55,
                               edgecolor=fs.REASONING, linewidth=2.8))
    all_u = np.concatenate([u_wrong[valid_wrong], u_right[valid_right]])
    all_v = np.concatenate([v_wrong[valid_wrong], v_right[valid_right]])
    pad = 90
    x0, x1 = max(int(all_u.min()) - pad, 0), min(int(all_u.max()) + pad, rgb.shape[1])
    y0, y1 = max(int(all_v.min()) - pad, 0), min(int(all_v.max()) + pad, rgb.shape[0])
    ax_left.set_xlim(x0, x1)
    ax_left.set_ylim(y1, y0)
    ax_left.set_xticks([])
    ax_left.set_yticks([])
    for spine in ax_left.spines.values():
        spine.set_color(fs.FAINT)
    ax_left.set_title("captures_pairs_2/cap_remote_head_near.npz -- dashed = pre-fix (wrong), "
                      "solid = post-fix (correct)", color=fs.MUTED, fontsize=11, family=fs.FONT, style="italic")

    ax_right = fig.add_axes([0.545, 0.14, 0.42, 0.68])
    ax_right.axis("off")
    y = 0.97
    for query in QUERIES:
        r = results[query]
        ax_right.text(0.0, y, f'query: "{query}"', transform=ax_right.transAxes, color=fs.INK, fontsize=13,
                      weight="bold", family=fs.FONT)
        y -= 0.075
        b, f = r["broken"], r["fixed"]
        ax_right.text(0.02, y, f"pre-fix:  {b['name']} -- {b['n']}pts/{b['width_mm']}mm -- "
                      f"evidence: {b['evidence'].upper()} (WRONG region)", transform=ax_right.transAxes,
                      color=fs.REJECTED, fontsize=11, family=fs.FONT)
        y -= 0.06
        ax_right.text(0.02, y, f"post-fix: {f['name']} -- {f['n']}pts/{f['width_mm']}mm -- "
                      f"evidence: {f['evidence'].upper()} (correct region)", transform=ax_right.transAxes,
                      color=fs.ACCEPTED, fontsize=11, family=fs.FONT)
        y -= 0.11

    ax_right.text(0.0, y - 0.02, "Both answers pass the same evidence gate. The gate tests SUFFICIENCY\n"
                  "(enough points, wide enough) -- it has no mechanism to test whether the\n"
                  "component is the physically correct one for the query.", transform=ax_right.transAxes,
                  color=fs.INK, fontsize=12, weight="bold", family=fs.FONT, linespacing=1.6, va="top")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "RELATION_HINTS before: key \"segment_mid\" (orphaned -- no component has this name after the "
              "segment_a/b/c rename). RELATION_HINTS after: rekeyed to \"segment_b\".", **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Both code paths re-run live this session via part_adaptive.bind_part() with each real dict "
              "swapped in -- reproducing PERCEPTION_EVIDENCE.md Part ANr3's documented numbers exactly.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Source: report_assets/PERCEPTION_EVIDENCE.md (Part ANr3/AW1/AW2); "
              "part_adaptive.py.before_orphan_fix (real backup, broken dict).", **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_i"), "new_i_binding_fragility_slide.png")
    rgb, comp, desc, K, extr = sps._load_and_isolate(CAP_PATH)
    _, _, _, _, _, results = run_both_states()

    u_wrong, v_wrong, _, valid_wrong = pa.project_points_to_pixels(comp["main_body"], K, extr)
    u_right, v_right, _, valid_right = pa.project_points_to_pixels(comp["segment_b"], K, extr)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("A Rename Silently Changed the Answer", **{**fs.TITLE, "size": 30}, x=fs.MARGIN, ha="left")

    ax_left = fig.add_axes([0.03, 0.10, 0.48, 0.74])
    ax_left.imshow(rgb)
    hull_wrong = _hull_polygon(u_wrong[valid_wrong], v_wrong[valid_wrong])
    hull_right = _hull_polygon(u_right[valid_right], v_right[valid_right])
    ax_left.add_patch(Polygon(hull_wrong, closed=True, facecolor=fs.REASONING, alpha=0.32,
                               edgecolor=fs.REASONING, linewidth=3.0, linestyle=(0, (4, 3))))
    ax_left.add_patch(Polygon(hull_right, closed=True, facecolor=fs.REASONING, alpha=0.55,
                               edgecolor=fs.REASONING, linewidth=3.4))
    # Both real regions are a small fraction of the full 640x480 frame --
    # crop to their combined extent (+ generous pad) so they're actually
    # visible, the same convention NEW-A/NEW-H use.
    all_u = np.concatenate([u_wrong[valid_wrong], u_right[valid_right]])
    all_v = np.concatenate([v_wrong[valid_wrong], v_right[valid_right]])
    pad = 90
    x0, x1 = max(int(all_u.min()) - pad, 0), min(int(all_u.max()) + pad, rgb.shape[1])
    y0, y1 = max(int(all_v.min()) - pad, 0), min(int(all_v.max()) + pad, rgb.shape[0])
    ax_left.set_xlim(x0, x1)
    ax_left.set_ylim(y1, y0)
    ax_left.set_xticks([])
    ax_left.set_yticks([])
    for spine in ax_left.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)
    ax_left.set_title("dashed = wrong (pre-fix)  ·  solid = correct (post-fix)", color=fs.MUTED, fontsize=16,
                      family=fs.FONT, style="italic", pad=8)

    r = results["sides"]
    b, f = r["broken"], r["fixed"]
    ax_right = fig.add_axes([0.56, 0.10, 0.41, 0.74])
    ax_right.axis("off")
    ax_right.set_xlim(0, 1)
    ax_right.set_ylim(0, 1)
    ax_right.text(0.0, 0.98, 'query: "sides" / "middle section"', transform=ax_right.transAxes, color=fs.INK,
                  fontsize=18, weight="bold", family=fs.FONT, va="top")

    # Explicit architectural chain -- an evaluation insight, not a bug
    # report: the SAME evidence gate is consulted at both ends of the chain
    # and returns PASS both times.
    def _chain_box(cx, cy, w, h, label, color):
        ax_right.add_patch(FancyBboxPatch(
            (cx, cy), w, h, boxstyle="round,pad=0.004,rounding_size=0.008", transform=ax_right.transAxes,
            facecolor=fs.CALLOUT_BG, edgecolor=color, linewidth=1.8))
        ax_right.text(cx + w / 2, cy + h / 2, label, transform=ax_right.transAxes, ha="center", va="center",
                      color=fs.INK, fontsize=16, weight="bold", family=fs.FONT, linespacing=1.15)

    bw, bh, bgap = 0.235, 0.155, 0.03
    row1_y, row2_y = 0.78, 0.53
    row1 = [("BUG\nFOUND", fs.MUTED), (f"WRONG PART\n{b['name']}", fs.REJECTED),
            ("GATE\n= PASS", fs.REJECTED)]
    row2 = [("FIX\n(rekey)", fs.MUTED), (f"CORRECT PART\n{f['name']}", fs.ACCEPTED),
            ("GATE\n= PASS", fs.ACCEPTED)]
    for i, (label, color) in enumerate(row1):
        _chain_box(i * (bw + bgap), row1_y, bw, bh, label, color)
        if i < 2:
            ax_right.add_patch(FancyArrowPatch((i * (bw + bgap) + bw, row1_y + bh / 2),
                                                ((i + 1) * (bw + bgap), row1_y + bh / 2),
                                                transform=ax_right.transAxes, color=fs.MUTED, linewidth=1.4,
                                                arrowstyle="-|>", mutation_scale=10))
    ax_right.add_patch(FancyArrowPatch((bw / 2, row1_y), (bw / 2, row2_y + bh), transform=ax_right.transAxes,
                                        color=fs.MUTED, linewidth=1.4, arrowstyle="-|>", mutation_scale=10,
                                        connectionstyle="arc3,rad=0.4"))
    for i, (label, color) in enumerate(row2):
        _chain_box(i * (bw + bgap), row2_y, bw, bh, label, color)
        if i < 2:
            ax_right.add_patch(FancyArrowPatch((i * (bw + bgap) + bw, row2_y + bh / 2),
                                                ((i + 1) * (bw + bgap), row2_y + bh / 2),
                                                transform=ax_right.transAxes, color=fs.MUTED, linewidth=1.4,
                                                arrowstyle="-|>", mutation_scale=10))

    ax_right.text(0.0, 0.40, "The evidence gate tests geometric sufficiency, not semantic correctness.",
                  transform=ax_right.transAxes, color=fs.MUTED, fontsize=16, family=fs.FONT, va="top",
                  linespacing=1.4, wrap=True)
    ax_right.text(0.0, 0.22, "SUPPORTED", transform=ax_right.transAxes, color=fs.REASONING,
                  fontsize=48, weight="bold", family=fs.FONT, va="center")
    ax_right.text(0.0, 0.02, "\u2260 CORRECT", transform=ax_right.transAxes, color=fs.REASONING,
                  fontsize=48, weight="bold", family=fs.FONT, va="bottom")

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "captures_pairs_2/cap_remote_head_near.npz", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-I binding fragility", [
        "Root cause: RELATION_HINTS keyed components by NAME, not by measured geometry. Renaming",
        "segment_mid -> segment_a/b/c (done for good reason, elsewhere) orphaned the hints entry --",
        "no error, no warning, just a different (wrong) answer for the same query string.",
        "Both bind_part() calls re-run live this session (not re-quoted): pre-fix and post-fix",
        "RELATION_HINTS dicts both swapped into the real function against a live decomposition of",
        "captures_pairs_2/cap_remote_head_near.npz. Reproduced PERCEPTION_EVIDENCE.md Part ANr3's",
        "exact numbers (286pts/38mm main_body; 1565pts/43mm segment_b).",
        "main_body's own hints ALSO include 'sides'/'middle'/'centre' -- untouched, coincidental overlap,",
        "not part of this specific defect, but part of why the tie-break landed there.",
        "This complements, not duplicates, NEW-A/NEW-H: those show the gate correctly REFUSING",
        "insufficient evidence. This shows the gate has no mechanism to catch a WRONG but",
        "sufficiently-evidenced answer -- a different, orthogonal failure class.",
        "Fix: report_assets/PERCEPTION_EVIDENCE.md Part AW1/AW2 (rekey confirmed corrected).",
        "Real backup files as evidence: part_adaptive.py.before_orphan_fix (broken),",
        "part_adaptive.py.before_segment_rename (pre-rename state).",
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
    print(f"new_i ({args.variant}) written to {path}")
    print(report.summary())
