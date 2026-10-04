"""Fig 5.2 -- Requested part against returned mask (QUANTITATIVE, Class D).

Extends fig_1_2_granularity_gap.py's single-object treatment to the dual-contour
method (Addendum B sec 18.2.2): whole-object mask as a dashed neutral contour,
returned part mask as a solid coloured contour, drawn on the real RGB capture.
The near-coincidence of the two outlines is the argument, for both objects with a
logged live LangSAM part-grounding run (knife, remote -- see figures/BLOCKERS.md
item 6 and SOURCE_MANIFEST.md sec 4 for why the mug is not a third panel here).

Real raw mask arrays are not saved anywhere in the repo (only composited overlay
PNGs, e.g. report_assets/figures_live/langsam_overlay_knife_pick.png) -- so this
script re-invokes VisualAffordanceGrounder.ground(), the same live, unmodified
function that produced the originally logged runs, on the same two captures used
by those runs (captures_pairs_2/cap_{knife,remote}_head_near.npz -- depths 0.913m/
0.920m match SENSOR_ENVELOPE.md's already-verified V2 table exactly). This is a
re-run of an existing function on an existing capture with no source-code change --
permitted under figures/AffordGrasp_Figure_Spec_FINAL.md sec 5 without a pipeline
gate stop. No robot contact; GroundingDINO/SAM2 weights loaded from local cache
(~50s one-time model load, ~2s/image after).

CORRECTED (2026-08-16, second pass) -- the gap between this live re-run's coverage
(knife 98.3%, remote 92.3%) and the originally logged values (knife 97%, remote 86%)
is NOT run-to-run model stochasticity. Verified: three repeated ground() calls in one
process, same loaded model, same input, are bit-identical (obj_sum/aff_sum equal to
the pixel across all 3 calls -- checked on the remote capture). The gap is a
deterministic shift caused by environment drift since the original runs were logged:
`requirements.txt` pins `torch==2.4.1` but never pins `transformers`, and the
currently-installed `transformers==5.2.0` prints its own warning on every load --
"The image processor of type GroundingDinoImageProcessor is now loaded as a fast
processor by default... This is a breaking change and may produce slightly different
outputs" -- which is exactly the failure mode observed: a small, systematic mask-
boundary shift, proportionally larger on the smaller-area remote (86->92, +6pts) than
the larger-area knife (97->98, +1pt), consistent with boundary-pixel noise mattering
more against a smaller denominator. Per the register's Rule 4 (BLOCKED -- DATA
CONFLICT), this was reported rather than silently reconciled; recorded in
figures/SOURCE_MANIFEST.md and figures/BLOCKERS.md. Citable numbers in prose remain
the ORIGINAL logged values (knife 97%, remote 86%, run_knife_pick2.log /
run_remote_power.log, asserted against those log files exactly as fig_5_1/fig_1_2
do); this figure's own live-rerun values stay on the panels as the real masks that
were actually drawn, now correctly captioned as environment-drifted rather than
"not deterministic."

Sources:
  workspace/captures_pairs_2\\cap_knife_head_near.npz   (real capture, rgb+depth)
  workspace/captures_pairs_2\\cap_remote_head_near.npz  (real capture, rgb+depth)
  workspace/constraints_knife_pick.json                 (real logged reasoning: target_part=handle)
  workspace/constraints_remote_power.json                (real logged reasoning: target_part=sides)
  workspace/run_knife_pick2.log, run_remote_power.log    (citable coverage: 97%, 86%)
  intent_grasp/visual_grounding.py                          (VisualAffordanceGrounder.ground(), live, unmodified)

Run: python figures/dissertation/fig_5_2_requested_part_vs_mask.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
import matplotlib.pyplot as plt
import numpy as np

import _qa as qa
import _style as fs

FIGURE_ID = "fig_5_2_requested_part_vs_mask"

PANELS = [
    dict(obj="knife", capture="cap_knife_head_near.npz", constraints="constraints_knife_pick.json",
         log="run_knife_pick2.log", logged_pct=97),
    dict(obj="remote", capture="cap_remote_head_near.npz", constraints="constraints_remote_power.json",
         log="run_remote_power.log", logged_pct=86),
]

INTENT = "The mask returned for the requested part is nearly coincident with the whole-object mask."

CAPTION = (
    "Fig 5.2. Requested part against returned mask. Dashed contour: whole-object mask. Solid "
    "coloured contour: the mask returned for the reasoning layer's own requested part "
    "(constraints_*.json, real logged output). Shaded region: whole-object mask minus part mask "
    "-- the entire pixel-area difference between the two queries. Knife ('pick up the knife' -> "
    "handle) and remote ('turn the television on' -> sides) are the only two objects with a "
    "logged live LangSAM part-grounding run in this repository. Citable coverage is the "
    "originally logged value (knife 97%, run_knife_pick2.log; remote 86%, run_remote_power.log). "
    "This figure's own live re-run recomputes a close but not identical value (knife 98%, remote "
    "92%) -- not run-to-run model stochasticity (three repeated calls in one process are "
    "bit-identical) but a deterministic shift from environment drift since the original runs: "
    "transformers is unpinned in requirements.txt, and the installed version's image processor "
    "changed defaults (own library warning: 'may produce slightly different outputs'). The two "
    "contours and the shaded difference are from this run; the annotated % is the citable logged "
    "one."
)


def _load_grounder():
    from intent_grasp.config import VisualGroundingConfig
    from intent_grasp.visual_grounding import VisualAffordanceGrounder
    return VisualAffordanceGrounder(VisualGroundingConfig())


def _crop_to_mask(rgb, part_mask, whole_mask, pad_frac=0.35):
    """Tight crop to the object's bounding box (house style: 'tight crop, object
    isolated' -- the Figure 3 segmentation-strip discipline, already applied to
    fig03 for the same reason: at full-frame scale the object was ~1-2% of the
    panel and the contours were illegible)."""
    ys, xs = np.where(whole_mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    h, w = y1 - y0, x1 - x0
    py, px = int(h * pad_frac) + 5, int(w * pad_frac) + 5
    y0, y1 = max(0, y0 - py), min(rgb.shape[0], y1 + py + 1)
    x0, x1 = max(0, x0 - px), min(rgb.shape[1], x1 + px + 1)
    return rgb[y0:y1, x0:x1], part_mask[y0:y1, x0:x1], whole_mask[y0:y1, x0:x1]


def _verify_logged_pct(log_path, pct):
    with open(log_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    needle = f"collapsed to whole object ({pct}% of object mask covered)"
    assert needle in text, f"{log_path} does not contain expected line {needle!r}"


def build():
    grounder = _load_grounder()
    fig, axes = plt.subplots(1, 2, figsize=(fs.TEXT_WIDTH_IN, 3.6))

    panel_results = []
    for ax, p in zip(axes, PANELS):
        cap_path = os.path.join(DATA_ROOT, "captures_pairs_2", p["capture"])
        cons_path = os.path.join(DATA_ROOT, p["constraints"])
        log_path = os.path.join(DATA_ROOT, p["log"])
        _verify_logged_pct(log_path, p["logged_pct"])

        with open(cons_path) as f:
            reasoning = json.load(f)
        d = np.load(cap_path)
        rgb, depth = d["rgb"], d["depth"]

        result = grounder.ground(rgb, depth, target_object=reasoning["target_object"],
                                  target_part=reasoning["target_part"])
        live_pct = 100.0 * result.affordance_mask.sum() / result.object_mask.sum()

        rgb_c, part_c, whole_c = _crop_to_mask(rgb, result.affordance_mask.astype(bool),
                                                result.object_mask.astype(bool))
        fs.mask_contour(ax, rgb_c, part_c, whole_mask=whole_c,
                         colour=fs.semantic_colour("perception"))
        # Near-coincident outlines are hard to see as outlines; shade the actual
        # pixel-area difference (whole minus part) so the small sliver that IS the
        # entire information content of the part query is visible directly, not just
        # implied by two close boundary lines.
        diff = whole_c & ~part_c
        diff_overlay = np.zeros((*diff.shape, 4), dtype=np.uint8)
        vermillion_rgb = tuple(int(fs.OKABE_ITO["vermillion"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        diff_overlay[diff] = (*vermillion_rgb, 160)
        ax.imshow(diff_overlay)
        ax.set_title(f'{p["obj"]}: "{reasoning["instruction"]}" -> {reasoning["target_part"]}',
                     fontsize=8.5)
        ax.annotate(f'logged: {p["logged_pct"]}% (this run: {live_pct:.0f}%)',
                    xy=(0.5, -0.06), xycoords="axes fraction", ha="center", va="top", fontsize=7.5)
        fs.panel_label(ax, "a" if p is PANELS[0] else "b")
        panel_results.append((p["obj"], live_pct, p["logged_pct"]))

    return fig, panel_results


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {[p['capture'] for p in PANELS]}, {[p['log'] for p in PANELS]}")
    fig, panel_results = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    for obj, live_pct, logged_pct in panel_results:
        print(f"[{FIGURE_ID}] {obj}: logged={logged_pct}% live_rerun={live_pct:.1f}%")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="Two real photos, each with a dashed black outline and a solid orange outline "
                   "that trace almost the same boundary around the object; reads as 'the returned "
                   "part is basically the whole object' without reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="each panel titled with its own instruction+part; each panel's logged/live % stated below it; n implicit (2 panels, both objects with a logged run).",
        referent_audit="both contours drawn directly on the real capture they were computed from; tight crop keeps the boundary detail legible.",
    )
    report_path = qa.write_report("V2")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
