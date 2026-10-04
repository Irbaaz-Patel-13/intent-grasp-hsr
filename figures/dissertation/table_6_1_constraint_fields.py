"""Table 6.1 -- Constraint fields across the grid.

Per cell: target part, keep_clear (with reasons), post-grasp motion, stability
priority. Not a matplotlib figure (register: Tables carry no Class letter).
Verifies row count/structure against experiments/vlm_grid/vlm_grid_raw.json and
writes the dissertation-ready markdown table to
figures/out/table_6_1_constraint_fields.md.

Source: workspace/experiments\\vlm_grid\\vlm_grid_raw.json

Run: python figures/dissertation/table_6_1_constraint_fields.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TABLE_ID = "table_6_1_constraint_fields"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
GRID_PATH = os.path.join(DATA_ROOT, "experiments", "vlm_grid", "vlm_grid_raw.json")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

OBJECT_ORDER = ["mug", "hammer", "knife", "pan", "bowl", "bottle"]
TYPE_ORDER = ["relocate", "use", "handover"]


def build_markdown():
    with open(GRID_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 18, f"expected 18 cells, got {len(data)}"
    by_key = {(e["object"], e["type"]): e for e in data}
    for obj in OBJECT_ORDER:
        for t in TYPE_ORDER:
            assert (obj, t) in by_key, f"missing cell ({obj}, {t})"

    lines = [
        "Table 6.1. Constraint fields across the grid.",
        "",
        "| Object | Type | Part | Keep clear | Reason | Motion | Stability |",
        "|---|---|---|---|---|---|---|",
    ]
    for obj in OBJECT_ORDER:
        for t in TYPE_ORDER:
            e = by_key[(obj, t)]["step3"]
            kc = ", ".join(e["constraints"]["keep_clear"]) or "-"
            reasons = "; ".join(e["constraints"]["keep_clear_reasons"]) or "-"
            lines.append(f"| {obj} | {t} | {e['target_part']} | {kc} | {reasons} | "
                         f"{e['constraints']['post_grasp_motion']} | {e['constraints']['stability_priority']} |")
    lines.append("")
    lines.append("Source: experiments/vlm_grid/vlm_grid_raw.json (18 cells, verified count and "
                  "object/type coverage above); see Fig 6.1 for the part-name pattern this table "
                  "underlies.")
    return "\n".join(lines)


if __name__ == "__main__":
    md = build_markdown()
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{TABLE_ID}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(f"[{TABLE_ID}] verified against {GRID_PATH}")
    print(md)
    print(f"[{TABLE_ID}] wrote: {out_path}")
