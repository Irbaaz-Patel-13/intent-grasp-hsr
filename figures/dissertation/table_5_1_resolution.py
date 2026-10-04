"""Table 5.1 -- Component width against recovered resolution.

Not a matplotlib figure (register: Tables carry no Class letter). This
script verifies the five rows against SENSOR_ENVELOPE.md V2/V3 and writes
the dissertation-ready markdown table to figures/out/table_5_1_resolution.md,
so the table text and the figure (Fig 5.3, same data) cannot silently drift
apart.

Source: workspace/report_assets\\SENSOR_ENVELOPE.md (V2, V3)

Run: python figures/dissertation/table_5_1_resolution.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TABLE_ID = "table_5_1_resolution"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
ENVELOPE_PATH = os.path.join(DATA_ROOT, "report_assets", "SENSOR_ENVELOPE.md")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

ROWS = [
    ("knife handle",              24, 15.18, "ok"),
    ("remote lateral protrusion", 18, 11.29, "ok"),
    ("spoon",                     20, 12.58, "ok"),
    ("pot lid knob",              16,  9.34, "ok"),
    ("mug handle",                 4,  2.50, "NOISE"),
]


def _verify():
    with open(ENVELOPE_PATH, encoding="utf-8") as f:
        env = f.read()
    for name, width_mm, px, outcome in ROWS:
        pat = rf"\|\s*{re.escape(name)}\s*\|\s*{width_mm}\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*\*\*{px:.2f}\*\*\s*\|"
        assert re.search(pat, env), f"row for {name!r} not found verbatim in {ENVELOPE_PATH}"


def build_markdown():
    _verify()
    lines = [
        "Table 5.1. Component width against recovered resolution.",
        "",
        "| Component | Width (mm) | Pixels at working distance | Outcome |",
        "|---|---|---|---|",
    ]
    for name, width_mm, px, outcome in ROWS:
        lines.append(f"| {name} | {width_mm} | {px:.2f} | {outcome} |")
    lines.append("")
    lines.append("Source: report_assets/SENSOR_ENVELOPE.md V2/V3; gate = <60 pts or <6 mm "
                  "(part_adaptive.py:541-542), ~3.5-3.8 px at these depths.")
    return "\n".join(lines)


if __name__ == "__main__":
    md = build_markdown()
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{TABLE_ID}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(f"[{TABLE_ID}] verified against {ENVELOPE_PATH}")
    print(md)
    print(f"[{TABLE_ID}] wrote: {out_path}")
