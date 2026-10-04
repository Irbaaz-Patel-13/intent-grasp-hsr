#!/usr/bin/env python
r"""
vlm_grid.py -- VLM-only object x instruction grid (no grounding, no GPU).

Evaluates the constraint-reasoning claim in isolation: for each (object,
instruction) cell it runs the REAL AffordanceReasoner Step 1 (task analysis)
and Step 3 (part + constraint reasoning), injecting the object identity
directly in place of Step 2 (visual object identification is evaluated
separately by eval_battery.py on real scenes; it is not under test here).

Same prompts, same schemas, same temperature-0 config as the live pipeline --
anything else would invalidate the comparison.

Run: python vlm_grid.py
Outputs: vlm_grid_results.md (table), vlm_grid_raw.json (full responses)
Cost: 36 GPT-4o calls (18 cells x steps 1+3), no images attached.
"""
import os, json, sys

from intent_grasp.config import VLMConfig
from intent_grasp.affordance_reasoning import (AffordanceReasoner,
                                  ObjectIdentificationResult)
from intent_grasp.paths import WORKSPACE

# (object, {instruction_type: instruction})
GRID = [
    ("mug", {
        "relocate": "Move the mug to the other side of the table",
        "use":      "Pour the coffee out of the mug",
        "handover": "Hand me the mug",
    }),
    ("bottle", {
        "relocate": "Move the bottle to the other side of the table",
        "use":      "Pour some water from the bottle",
        "handover": "Hand me the bottle",
    }),
    ("hammer", {
        "relocate": "Move the hammer to the other side of the table",
        "use":      "Hammer the nail into the board",
        "handover": "Hand me the hammer",
    }),
    ("knife", {
        "relocate": "Move the knife to the other side of the table",
        "use":      "Cut the apple with the knife",
        "handover": "Hand me the knife",
    }),
    ("bowl", {
        "relocate": "Move the bowl to the other side of the table",
        "use":      "Pour the cereal out of the bowl",
        "handover": "Hand me the bowl",
    }),
    ("pan", {
        "relocate": "Move the pan to the other side of the table",
        "use":      "Fry an egg in the pan",
        "handover": "Hand me the pan",
    }),
]

RESULTS_MD = f"{WORKSPACE}/vlm_grid_results.md"
RAW_JSON = f"{WORKSPACE}/vlm_grid_raw.json"


def keyword_baseline_part(instruction: str) -> str:
    """Copied verbatim from eval_battery.py (kept standalone there as the
    ablation baseline mirroring the deleted keyword routing)."""
    instr = instruction.lower()
    if "handle" in instr:
        return "handle"
    if "pour" in instr:
        return "rim"
    if "lift" in instr or "pick" in instr or "move" in instr:
        return "body"
    return "body"


def make_reasoner() -> AffordanceReasoner:
    cfg = VLMConfig()
    cfg.api_key = os.environ.get("OPENAI_API_KEY", "")

    print("ENV KEY FOUND:", bool(cfg.api_key))
    print("KEY PREFIX:", cfg.api_key[:8] if cfg.api_key else None)

    r = AffordanceReasoner(cfg)

    if r.mock_mode:
        sys.exit(
            "ABORT: reasoner is in MOCK mode (no OPENAI_API_KEY) -- "
            "grid results would be heuristic fabrications, not data."
        )

    return r


def main():
    reasoner = make_reasoner()
    rows, raw = [], []
    for obj, instrs in GRID:
        for itype, instruction in instrs.items():
            print("\n" + "=" * 70)
            print(f"[grid] {obj} / {itype}: \"{instruction}\"")
            print("=" * 70)
            task = reasoner._step1_task_analysis(instruction)
            print(f"  task_goal: {task.task_goal}")
            # Step 2 bypass: inject object identity (not under test here)
            obj_result = ObjectIdentificationResult(
                target_object=obj,
                object_description=f"a {obj} on the table",
                confidence=1.0,
                approximate_location="center of scene",
                raw_response={"injected": True},
            )
            aff = reasoner._step3_affordance_reasoning(instruction, task,
                                                       obj_result)
            c = aff.constraints
            print(f"  part={aff.target_part}  keep_clear={c['keep_clear']}"
                  f"  motion={c['post_grasp_motion']}"
                  f"  thermal={c['thermal_or_hygiene']}")
            base = keyword_baseline_part(instruction)
            rows.append({
                "object": obj, "type": itype, "instruction": instruction,
                "part": aff.target_part,
                "keep_clear": c["keep_clear"],
                "kc_reasons": c["keep_clear_reasons"],
                "motion": c["post_grasp_motion"],
                "stability": c["stability_priority"],
                "thermal": c["thermal_or_hygiene"],
                "baseline": base,
                "diverged": "YES" if aff.target_part != base else "no",
                "rationale": aff.rationale,
                "confidence": aff.confidence,
            })
            raw.append({
                "object": obj, "type": itype, "instruction": instruction,
                "step1": task.raw_response, "step3": aff.raw_response,
            })

    lines = [
        "| object | type | instruction | VLM part | keep_clear | "
        "keep_clear_reasons | motion | stability | thermal | "
        "keyword baseline | diverged |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        kc = "; ".join(r["keep_clear"]) if r["keep_clear"] else "[]"
        kr = "; ".join(r["kc_reasons"]) if r["kc_reasons"] else "-"
        th = r["thermal"] if r["thermal"] else "-"
        lines.append(
            f"| {r['object']} | {r['type']} | {r['instruction']} | "
            f"{r['part']} | {kc} | {kr} | {r['motion']} | {r['stability']} | "
            f"{th} | {r['baseline']} | {r['diverged']} |")
    table = "\n".join(lines)

    n_div = sum(1 for r in rows if r["diverged"] == "YES")
    summary = (f"\n\n**{len(rows)} cells; system diverged from keyword "
               f"baseline in {n_div}/{len(rows)}.**\n\nRationales:\n\n")
    summary += "\n".join(f"- **{r['object']}/{r['type']}** "
                         f"(part={r['part']}): {r['rationale']}"
                         for r in rows)

    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(table + summary + "\n")
    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    print("\n" + table)
    print(f"\n[grid] saved -> {RESULTS_MD}\n[grid] saved -> {RAW_JSON}")


if __name__ == "__main__":
    main()
