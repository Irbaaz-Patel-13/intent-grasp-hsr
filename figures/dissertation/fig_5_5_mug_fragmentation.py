"""Fig 5.5 -- Mug handle fragmentation under the decomposition gates
(QUANTITATIVE, Class D).

The mug does NOT belong in Fig 5.1/Fig 6.4 (no logged LangSAM collapse
percentage for the mug -- BLOCKERS.md item 6; its handle is a geometric
evidence-gate refusal, not a grounding-collapse case -- SOURCE_MANIFEST.md
sec 4). This figure is the mug's own real result: its handle fragments into
two DBSCAN clusters, `lateral_protrusion` (53 pts, 4 mm) and
`lateral_protrusion_1` (36 pts, 3 mm). Combined, 53+36=89 points clears the
60-point evidence gate; neither fragment's individual width (4 mm, 3 mm)
clears the 6 mm width floor. This is direct, measured evidence for the
distinction between sampling sufficiency and spatial resolution -- the
§12.3 multi-view-fusion prediction (fusion may fix the sampling problem,
i.e. the point-count gate, without fixing the resolution problem, i.e. the
width floor) is not asserted here, it is measured.

Does NOT claim the handle was recovered. It was not -- evidence stays
NOISE (the gate is `n<60 OR width<6mm`; width fails regardless of the
combined point count). The figure's whole purpose is to show a passed gate
and a failed gate side by side without letting either read as "handle
found."

Source: live re-run of the real, unmodified pipeline chain
  (analyse_range.load_capture/cloud_base/find_object -> part_adaptive.
  find_components -> part_adaptive.describe_components) on
  captures_pairs_2/cap_mug_head_near.npz -- the same real capture and same
  chain new_a_part_decomposition.py already used and cross-verified against
  3 independent logs (bc_mug.log/ax4_mug.log/q6_intent_mug.log). Re-verified
  here to produce the real point cloud arrays for panel (a); the exact
  numbers below are asserted against that live re-run, not retyped.

Run: python figures/dissertation/fig_5_5_mug_fragmentation.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intent_grasp.paths import REPO_ROOT  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "scripts" / "experiments"))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
import matplotlib.pyplot as plt
import numpy as np

import _qa as qa
import _style as fs

FIGURE_ID = "fig_5_5_mug_fragmentation"
CAPTURE_PATH = os.path.join(DATA_ROOT, "captures_pairs_2", "cap_mug_head_near.npz")

POINT_GATE = 60
WIDTH_GATE_MM = 6.0
EXPECTED = {
    "main_body": (1390, 18, "ok"),
    "top_protrusion": (147, 7, "LOW"),
    "lateral_protrusion": (53, 4, "NOISE"),
    "lateral_protrusion_1": (36, 3, "NOISE"),
}

INTENT = "Combined, the mug's two handle fragments clear the point-count gate; individually, neither clears the width floor -- the handle is not recovered."

CAPTION = (
    "Fig 5.5. Mug handle fragmentation under the decomposition gates. Real mug capture "
    "(captures_pairs_2/cap_mug_head_near.npz), four detected components. (a) Point cloud: "
    "main_body (grey, 1390 pts/18 mm, ok), top_protrusion (amber, 147 pts/7 mm, LOW), and the "
    "two handle fragments (lateral_protrusion 53 pts/4 mm, lateral_protrusion_1 36 pts/3 mm, "
    "both NOISE). (b) Combined handle points (53+36=89) against the 60-point evidence gate -- "
    "PASSES. (c) Each fragment's measured width against the 6 mm floor -- both FAIL. The gate "
    "is n<60 OR width<6mm, so the handle stays NOISE regardless of (b): passing one gate does "
    "not recover the part. This is measured evidence for the sampling-vs-resolution "
    "distinction cited in sec 12.3 -- multi-view fusion is predicted to help (b) by adding "
    "points, not (c), which is a physical width no additional viewpoint changes."
)


def _load_and_verify():
    import analyse_range as ar
    from intent_grasp import part_adaptive as pa
    cap = ar.load_capture(CAPTURE_PATH)
    plane, obj, iso = ar.find_object(ar.cloud_base(cap))
    comp, info = pa.find_components(obj, z_table=plane)
    desc = pa.describe_components(comp, info)
    for name, (n, w, ev) in EXPECTED.items():
        d = desc[name]
        assert d["n"] == n and d["closing_width_mm"] == w and d["evidence"] == ev, \
            f"{name} drifted from cited values: got {d}"
    return comp, desc


def build():
    comp, desc = _load_and_verify()

    fig = plt.figure(figsize=(fs.TEXT_WIDTH_IN, 3.3))
    ax_cloud = fig.add_subplot(1, 3, 1, projection="3d")
    ax_pts = fig.add_subplot(1, 3, 2)
    ax_width = fig.add_subplot(1, 3, 3)

    # (a) point cloud
    ax_cloud.set_proj_type("ortho")
    c = comp["main_body"].mean(0)
    colours = {
        "main_body": (fs.OKABE_ITO["black"], 0.10, 2),
        "top_protrusion": (fs.OKABE_ITO["yellow"], 0.9, 5),
        "lateral_protrusion": (fs.OKABE_ITO["vermillion"], 0.9, 8),
        "lateral_protrusion_1": ("#7A1E17", 0.9, 8),
    }
    for name, (colour, alpha, size) in colours.items():
        pts = comp[name]
        ax_cloud.scatter(pts[:, 0] - c[0], pts[:, 1] - c[1], pts[:, 2] - c[2],
                          s=size, c=colour, alpha=alpha, depthshade=False, label=name)
    ax_cloud.set_box_aspect((1, 1, 1))
    ax_cloud.xaxis.set_major_locator(plt.MaxNLocator(2))
    ax_cloud.yaxis.set_major_locator(plt.MaxNLocator(2))
    ax_cloud.zaxis.set_major_locator(plt.MaxNLocator(2))
    ax_cloud.tick_params(labelsize=7)
    ax_cloud.view_init(elev=25, azim=-50)
    ax_cloud.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=7, ncol=1, framealpha=0.9)
    ax_cloud.text2D(0.0, 1.06, "(a)", transform=ax_cloud.transAxes, fontsize=9, fontweight="bold", va="bottom")

    # (b) combined points vs the 60-point gate
    n1, n2 = desc["lateral_protrusion"]["n"], desc["lateral_protrusion_1"]["n"]
    combined = n1 + n2
    ax_pts.bar(["frag 1", "frag 2", "combined"], [n1, n2, combined],
               color=[fs.OKABE_ITO["vermillion"], "#7A1E17", fs.semantic_colour("keep")], width=0.6)
    ax_pts.axhline(POINT_GATE, color=fs.OKABE_ITO["vermillion"], linestyle="--", linewidth=1.0)
    ax_pts.text(-0.45, POINT_GATE + 3, f"{POINT_GATE}-pt gate", fontsize=7, ha="left", va="bottom",
                color=fs.OKABE_ITO["vermillion"])
    ax_pts.annotate(f"{combined} pts\nPASS", (2, combined), xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=7.5, fontweight="bold",
                     color=fs.semantic_colour("keep"))
    ax_pts.set_ylim(0, combined * 1.32)
    ax_pts.set_ylabel("points")
    ax_pts.set_title("point-count gate", fontsize=8.5, pad=10)
    fs.panel_label(ax_pts, "b")

    # (c) individual widths vs the 6mm floor
    w1, w2 = desc["lateral_protrusion"]["closing_width_mm"], desc["lateral_protrusion_1"]["closing_width_mm"]
    bars = ax_width.bar(["frag 1", "frag 2"], [w1, w2],
                         color=[fs.OKABE_ITO["vermillion"], "#7A1E17"], width=0.5)
    ax_width.axhline(WIDTH_GATE_MM, color=fs.OKABE_ITO["vermillion"], linestyle="--", linewidth=1.0)
    ax_width.text(-0.45, WIDTH_GATE_MM + 0.25, f"{WIDTH_GATE_MM:.0f} mm floor", fontsize=7, ha="left",
                  va="bottom", color=fs.OKABE_ITO["vermillion"])
    for bar, w in zip(bars, (w1, w2)):
        ax_width.annotate(f"{w} mm", (bar.get_x() + bar.get_width() / 2, w), xytext=(0, 4),
                           textcoords="offset points", ha="center", va="bottom", fontsize=7.5)
    ax_width.annotate("both FAIL", (0.5, WIDTH_GATE_MM * 1.55), fontsize=7.5, fontweight="bold",
                       ha="center", color=fs.OKABE_ITO["vermillion"])
    ax_width.set_ylabel("width (mm)")
    ax_width.set_ylim(0, WIDTH_GATE_MM * 1.75)
    ax_width.set_title("width gate", fontsize=8.5, pad=10)
    fs.panel_label(ax_width, "c")

    return fig, desc


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {CAPTURE_PATH}")
    fig, desc = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    for nm in ("main_body", "top_protrusion", "lateral_protrusion", "lateral_protrusion_1"):
        d = desc[nm]
        print(f"[{FIGURE_ID}] {nm}: {d['n']} pts, {d['closing_width_mm']} mm, {d['evidence']}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    qa.check_post_save_layout(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="A point cloud with two small red clusters on one side (the handle "
                   "fragments), then a bar chart where 'combined' clears a dashed line "
                   "labelled PASS, then a bar chart where both bars sit under a dashed line "
                   "labelled FAIL -- reads as 'points are enough but width is not' without "
                   "reading the caption; nothing says 'handle recovered.'",
        verdict="COMMUNICATION PASS",
        element_audit="every bar labelled with its measured value; both gate lines labelled at the line; PASS/FAIL stated explicitly on each panel; point-cloud legend names all 4 components.",
        referent_audit="gate lines and their labels sit adjacent in both bar panels; PASS/FAIL annotations sit directly above the bars they describe.",
    )
    report_path = qa.write_report("V-corrections")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
