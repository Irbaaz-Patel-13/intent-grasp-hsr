#!/usr/bin/env python
r"""
vlm_grid_handover_v2.py -- receiver-aware handover ablation (contract v2).

vlm_grid.py (contract v1) showed the step-3 prompt reasons correctly about
TASK mechanics but has no receiver model: for "hand me the knife" it chose
part=handle, keep_clear=[] -- the robot would present the blade to the
human. v2 adds ONE paragraph of receiver-perspective reasoning to the
step-3 template and re-runs ONLY the six handover cells, so the v1->v2
flip is reportable as a controlled prompt-contract ablation.

The live pipeline contract (config.py) is NOT modified -- v2 exists only
inside this script.

Run: python vlm_grid_handover_v2.py
Outputs: vlm_grid_handover_v2.md, vlm_grid_handover_v2_raw.json
Cost: 12 GPT-4o calls (6 cells x steps 1+3).
"""
import os, json, sys

from intent_grasp.config import VLMConfig
from intent_grasp.affordance_reasoning import (AffordanceReasoner,
                                  ObjectIdentificationResult)
from intent_grasp.paths import WORKSPACE

HANDOVER_CELLS = [
    ("mug",    "Hand me the mug"),
    ("bottle", "Hand me the bottle"),
    ("hammer", "Hand me the hammer"),
    ("knife",  "Hand me the knife"),
    ("bowl",   "Hand me the bowl"),
    ("pan",    "Hand me the pan"),
]

# v1 results from vlm_grid.py (15 Jul run), for the side-by-side table.
V1 = {
    "mug":    ("handle", "[]"),
    "bottle": ("neck",   "[]"),
    "hammer": ("handle", "[]"),
    "knife":  ("handle", "[]"),
    "bowl":   ("rim",    "[]"),
    "pan":    ("handle", "[]"),
}

RECEIVER_PARAGRAPH = """HANDOVER TASKS have one additional constraint source: the RECEIVER. If the task is giving the object to a person, reason from the receiver's perspective as well as the robot's. The part the person will naturally take hold of must remain unobstructed by the robot's gripper and be presented toward them -- that part belongs in keep_clear, with a reason naming the receiver's grasp. If the object has a hazardous region (a blade, a point, a hot surface), the robot must grasp the object such that the hazardous region is controlled by the robot's gripper and NOT presented toward the person; the safe graspable part (for example a handle) is what the person receives. For hazardous objects this can mean the robot grasps a region it would never choose for its own use of the tool. For objects with no hazardous region and no single natural receiving part, keep_clear may still be empty.

"""

RESULTS_MD = f"{WORKSPACE}/vlm_grid_handover_v2.md"
RAW_JSON = f"{WORKSPACE}/vlm_grid_handover_v2_raw.json"

ANCHOR = 'Instruction: "{instruction}"'


def make_reasoner() -> AffordanceReasoner:
    cfg = VLMConfig()
    if not cfg.api_key:
        cfg.api_key = os.environ.get("OPENAI_API_KEY", "")
    # Build the v2 template by inserting the receiver paragraph just above
    # the instruction block of the UNMODIFIED v1 template.
    t = cfg.step3_affordance_reasoning_template
    if t.count(ANCHOR) != 1:
        sys.exit("ABORT: template anchor not found exactly once -- "
                 "config.py step-3 template changed; update ANCHOR.")
    cfg.step3_affordance_reasoning_template = t.replace(
        ANCHOR, RECEIVER_PARAGRAPH + ANCHOR)
    r = AffordanceReasoner(cfg)
    if r.mock_mode:
        sys.exit("ABORT: mock mode (no OPENAI_API_KEY) -- results would "
                 "be fabrications.")
    return r


def main():
    reasoner = make_reasoner()
    rows, raw = [], []
    for obj, instruction in HANDOVER_CELLS:
        print("\n" + "=" * 70)
        print(f"[v2] {obj}: \"{instruction}\"")
        print("=" * 70)
        task = reasoner._step1_task_analysis(instruction)
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
        print(f"  v2 part={aff.target_part}  keep_clear={c['keep_clear']}")
        print(f"  rationale: {aff.rationale}")
        rows.append({
            "object": obj,
            "v1_part": V1[obj][0], "v1_keep_clear": V1[obj][1],
            "v2_part": aff.target_part,
            "v2_keep_clear": "; ".join(c["keep_clear"]) or "[]",
            "v2_kc_reasons": "; ".join(c["keep_clear_reasons"]) or "-",
            "thermal": c["thermal_or_hygiene"] or "-",
            "changed": "YES" if (aff.target_part != V1[obj][0]
                                 or (c["keep_clear"] and V1[obj][1] == "[]"))
                       else "no",
            "rationale": aff.rationale,
        })
        raw.append({"object": obj, "instruction": instruction,
                    "step1": task.raw_response, "step3": aff.raw_response})

    lines = [
        "# Handover ablation: contract v1 (task-mechanics only) vs "
        "v2 (receiver-aware)",
        "",
        "| object | v1 part | v1 keep_clear | v2 part | v2 keep_clear | "
        "v2 reasons | thermal | changed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['object']} | {r['v1_part']} | {r['v1_keep_clear']} | "
            f"{r['v2_part']} | {r['v2_keep_clear']} | {r['v2_kc_reasons']} | "
            f"{r['thermal']} | {r['changed']} |")
    lines.append("\n## v2 rationales\n")
    lines += [f"- **{r['object']}**: {r['rationale']}" for r in rows]
    md = "\n".join(lines)

    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write(md + "\n")
    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    print("\n" + md)
    print(f"\n[v2] saved -> {RESULTS_MD}\n[v2] saved -> {RAW_JSON}")


if __name__ == "__main__":
    main()
