#!/usr/bin/env python
r"""
eval_battery.py -- runs a fixed battery of instructions through the real
constraint-based pipeline (hand_part_grounding.run_pipeline, live GPT-4o)
AND through a deliberately naive keyword baseline, to make the improvement
from constraint-based reasoning visible as an ablation.

The keyword baseline below is NOT part_decomposition.py's routing (that
keyword logic was deleted -- see
docs/superpowers/plans/2026-07-13-constraint-based-part-reasoning.md Task 2).
It is preserved here, standalone, ONLY as a naive comparison point.

Run: python eval_battery.py
"""
import numpy as np

import hand_part_grounding as hpg
from intent_grasp.paths import WORKSPACE

BATTERY = [
    ("Move the mug to the other shelf", False),
    ("Pour the water into the bowl", False),
    ("Hand me the mug", False),
    ("The mug just came out of the microwave — move it to the counter", False),
    ("Stack the empty mugs", False),
    ("Lift the mug using its handle", True),  # explicit-grounding control
]

RESULTS_MD = f"{WORKSPACE}/battery_results.md"


def keyword_baseline_part(instruction: str) -> str:
    """
    Deliberately naive verb/noun -> part lookup, preserved ONLY as an
    ablation baseline -- this mirrors the OLD routing logic that used to
    live in part_decomposition.py's select_part_for_instruction before the
    constraint-based rewrite replaced instruction-keyword routing.
    "handle" is checked first (highest precedence) since it is the most
    explicit, unambiguous signal a naive lookup can key on -- matches this
    project's prior keyword-routing precedence.
    """
    instr = instruction.lower()
    if "handle" in instr:
        return "handle"
    if "pour" in instr:
        return "rim"
    if "lift" in instr or "pick" in instr or "move" in instr:
        return "body"
    return "body"


def main():
    rows = []
    for instruction, is_control in BATTERY:
        slug = instruction.lower().replace(" ", "_").replace("—", "-")[:40]
        out_npz = f"{WORKSPACE}/battery_{slug}.npz"
        out_png = f"{WORKSPACE}/battery_{slug}.png"
        print(f"\n{'='*70}\n[battery] running: \"{instruction}\"\n{'='*70}")
        baseline_part = keyword_baseline_part(instruction)
        # run_pipeline() calls sys.exit(...) (SystemExit, not a normal
        # exception) on a genuine geometric-pipeline abort (e.g. too few
        # points survive for the selected part -- see hand_part_grounding.py
        # / part_decomposition.py's MIN_INTERSECT / "< 3 points" guards).
        # That is real signal about THIS instruction, not a bug in this
        # script, but letting it propagate would kill the whole battery and
        # silently drop the remaining instructions -- catch it here so one
        # aborted row doesn't block reporting the rest.
        try:
            result = hpg.run_pipeline(instruction, target_hint="mug",
                                       out_npz=out_npz, out_png=out_png)
        except SystemExit as e:
            print(f"[battery] ABORTED: \"{instruction}\" -> {e}")
            rows.append({
                "instruction": instruction,
                "is_control": is_control,
                "vlm_part": "ABORTED",
                "keep_clear": "-",
                "post_grasp_motion": "-",
                "selected_part": "-",
                "centroid": None,
                "n_pts": 0,
                "grasp_type": "-",
                "ideal_type": "-",
                "baseline_part": baseline_part,
                "diverged": "n/a",
                "notes": str(e),
            })
            continue
        rows.append({
            "instruction": instruction,
            "is_control": is_control,
            "vlm_part": result["vlm_target_part"],
            "keep_clear": result["constraints"].get("keep_clear", []),
            "post_grasp_motion": result["constraints"].get("post_grasp_motion", "?"),
            "selected_part": result["selected_part"],
            "centroid": result["part_centroid"],
            "n_pts": len(result["part_points_capture"]),
            "grasp_type": result["grasp_type"],
            "ideal_type": result["ideal_type"],
            "baseline_part": baseline_part,
            "diverged": result["selected_part"] != baseline_part,
            "notes": "; ".join(result["notes"]) if result["notes"] else "-",
        })

    lines = [
        "| instruction | VLM part | keep_clear | post_grasp_motion | "
        "selected part | centroid | pts | grasp_type (ideal/executed) | "
        "keyword baseline | diverged | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        c = row["centroid"]
        c_str = f"({c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f})" if c is not None else "-"
        tag = " (control)" if row["is_control"] else ""
        if row["diverged"] == "n/a":
            diverged_str = "n/a"
        else:
            diverged_str = "YES" if row["diverged"] else "no"
        lines.append(
            f"| {row['instruction']}{tag} | {row['vlm_part']} | "
            f"{row['keep_clear']} | {row['post_grasp_motion']} | "
            f"{row['selected_part']} | {c_str} | {row['n_pts']} | "
            f"{row['ideal_type']} / {row['grasp_type']} | "
            f"{row['baseline_part']} | {diverged_str} | {row['notes']} |"
        )
    table_md = "\n".join(lines)
    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(table_md + "\n")
    print(f"\n{table_md}\n")
    print(f"[battery] saved -> {RESULTS_MD}")


if __name__ == "__main__":
    main()
