#!/usr/bin/env python
r"""
part_decomposition_report.py -- runs hand_part_grounding.run_pipeline() for
the three benchmark instructions against the current grasp-3 capture set
(hand_view_real.npz / fused_cloud.npz / grasps_plain.npz already on disk),
and emits:
  - part_decomposition_report.png : one 3D scatter of the scene's classified
    points (rim/interior/body/handle/unclassified), from the first
    run (the object-cloud classification doesn't depend on which
    instruction drove the grounding, since all three target the same mug --
    see the plan's Task 3 note on why one run is representative).
  - part_decomposition_table.md   : instruction -> selected part -> centroid
    -> grasp_type table, printed and saved.

Run: python part_decomposition_report.py
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

import hand_part_grounding as hpg
from intent_grasp import part_decomposition as pd
from intent_grasp.paths import WORKSPACE
INSTRUCTIONS = [
    ("pick up the mug", None),
    ("pour the water out of the mug", None),
    ("pick up the mug by the handle", None),
]

REPORT_PNG = f"{WORKSPACE}/part_decomposition_report.png"
REPORT_MD = f"{WORKSPACE}/part_decomposition_table.md"


def main():
    rows = []
    scene_parts_for_plot = None
    for instruction, target_hint in INSTRUCTIONS:
        slug = instruction.lower().replace(" ", "_")[:40]
        out_npz = f"{WORKSPACE}/part_grasp_report_{slug}.npz"
        out_png = f"{WORKSPACE}/part_grasp_report_{slug}.png"
        print(f"\n{'='*70}\n[report] running: \"{instruction}\"\n{'='*70}")
        result = hpg.run_pipeline(instruction, target_hint=target_hint,
                                   out_npz=out_npz, out_png=out_png)
        if scene_parts_for_plot is None:
            scene_parts_for_plot = result["parts_view"]
        rows.append({
            "instruction": instruction,
            "selected_part": result["selected_part"],
            "centroid": result["grasp_anchor_view"],
            "grasp_type": result["grasp_type"],
            "ideal_type": result["ideal_type"],
            "notes": "; ".join(result["notes"]) if result["notes"] else "-",
        })

    # ---- comparison figure: one scene, all classified points ----
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    for name, pts in scene_parts_for_plot.items():
        if len(pts) == 0:
            continue
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=4,
                   c=pd.PART_COLORS[name], alpha=0.7, label=f"{name} ({len(pts)})")
    ax.set_title("grasp-3 scene: geometric part decomposition")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(REPORT_PNG, dpi=110, bbox_inches="tight")
    print(f"\n[report] saved -> {REPORT_PNG}")

    # ---- table ----
    lines = ["| instruction | selected part | centroid (x, y, z) | grasp_type | ideal_type | notes |",
              "|---|---|---|---|---|---|"]
    for row in rows:
        c = row["centroid"]
        c_str = f"({c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f})"
        lines.append(f"| {row['instruction']} | {row['selected_part']} | {c_str} "
                      f"| {row['grasp_type']} | {row['ideal_type']} | {row['notes']} |")
    table_md = "\n".join(lines)
    with open(REPORT_MD, "w") as f:
        f.write(table_md + "\n")
    print(f"\n{table_md}\n")
    print(f"[report] saved -> {REPORT_MD}")


if __name__ == "__main__":
    main()
