"""Fig 5.4 -- Isolated against cluttered measurement (QUANTITATIVE, Class D).

Adapted from new_e_isolated_vs_cluttered.py (slide-style, dark background,
large type) to report house style -- same real data, same claim, converted
per the Part 0.3 rule ("slide-to-report conversion is a known, bounded
transformation") rather than rebuilt. Real 5-scene batch
(batch_scene_analysis.csv); this figure isolates the pot pair, which is the
one §5.4 cites.

Scientific claim (unchanged from new_e): the pot's graspable (minor) width
measures 147 mm isolated and 46 mm in a cluttered scene (mug + cokecan + pot) -- same
real object, same real pipeline, opposite evidence-gate outcome (REFUSE ->
PASS against the 125 mm aperture). This demonstrates that clutter changes
what is geometrically MEASURABLE, not what the reasoning layer infers --
the reasoning-layer target (pot/handle) is identical in both rows of
batch_scene_analysis.csv; only `minor_mm` (perception's own measurement)
differs.

Source: workspace/batch_scene_analysis.csv (rows: pot_with_handle_and_lid,
cluster_mug_cokecan_pot -- real, verified below)
Thumbnails: workspace/captures_0723\\cap_pot_with_handle_and_lid.npz,
            workspace/captures_0723\\cap_cluster_mug_cokecan_pot.npz

Run: python figures/dissertation/fig_5_4_isolated_vs_cluttered.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import _qa as qa
import _style as fs

FIGURE_ID = "fig_5_4_isolated_vs_cluttered"
CSV_PATH = os.path.join(DATA_ROOT, "batch_scene_analysis.csv")
CAPTURES_DIR = os.path.join(DATA_ROOT, "captures_0723")
ISO_SCENE, CLUT_SCENE = "pot_with_handle_and_lid", "cluster_mug_cokecan_pot"
APERTURE_MM = 125
THUMB_CROP = (110, 190, 560, 500)  # same tabletop crop convention as the source slide deck

INTENT = "Clutter changes what is measurable without changing what is reasoned."

CAPTION = (
    "Fig 5.4. Isolated against cluttered measurement, same real pot, same real pipeline "
    "(batch_scene_analysis.csv). (a) Isolated capture: measured graspable width 147 mm, over "
    "the 125 mm aperture -- evidence gate REFUSE. (b) The same pot inside a cluttered scene "
    "(sharing the table with a mug and a coke can): measured graspable width 46 mm, under the "
    "aperture -- PASS. The "
    "reasoning layer's target (pot / handle) is identical in both rows; only the geometric "
    "measurement changes. Not generalised beyond this one object -- the TV remote in the same "
    "5-scene batch moves the opposite direction (13 mm -> 73 mm, both PASS), so this is not a "
    "general clutter-degrades-measurement claim."
)


def _load_row(scene):
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = {r["scene"]: r for r in csv.DictReader(f)}
    return rows[scene]


def _verify():
    iso, clut = _load_row(ISO_SCENE), _load_row(CLUT_SCENE)
    assert float(iso["minor_mm"]) == 147 and iso["over_aperture"] == "1"
    assert float(clut["minor_mm"]) == 46 and clut["over_aperture"] == "0"
    assert iso["target_object"] == clut["target_object"] == "pot"
    assert iso["target_part"] == clut["target_part"] == "handle"
    return iso, clut


def build():
    iso, clut = _verify()
    w_iso, w_clut = float(iso["minor_mm"]), float(clut["minor_mm"])

    fig, axes = plt.subplots(1, 2, figsize=(fs.TEXT_WIDTH_IN, 3.4))

    for ax, npz_name, label, w, gate, gate_colour in [
        (axes[0], "cap_pot_with_handle_and_lid.npz", "isolated", w_iso, "REFUSE", fs.OKABE_ITO["vermillion"]),
        (axes[1], "cap_cluster_mug_cokecan_pot.npz", "cluttered (mug + cokecan + pot)", w_clut, "PASS", fs.semantic_colour("keep")),
    ]:
        d = np.load(os.path.join(CAPTURES_DIR, npz_name))
        x0, y0, x1, y1 = THUMB_CROP
        ax.imshow(d["rgb"][y0:y1, x0:x1])
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(label, fontsize=9)
        ax.text(0.5, -0.06, f"{w:.0f} mm ({gate}, 125 mm aperture)", transform=ax.transAxes,
                 ha="center", va="top", fontsize=8.5, fontweight="bold", color=gate_colour)

    fs.panel_label(axes[0], "a")
    fs.panel_label(axes[1], "b")

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {CSV_PATH}")
    fig = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    qa.check_post_save_layout(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="Two real photos of the same pot, one alone on the table, one among several "
                   "other objects; each carries a measured width and a REFUSE/PASS tag -- reads "
                   "as 'the same object measures differently depending on the scene around it' "
                   "without reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="both panels show the measured width, the gate verdict, and the aperture threshold directly.",
        referent_audit="measurement/verdict text sits directly under its own photo.",
    )
    report_path = qa.write_report("V-corrections")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
