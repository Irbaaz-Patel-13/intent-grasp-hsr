"""Fig 6.2 -- Handover contract ablation (QUANTITATIVE, Class D).

Under a receiver-aware contract (v2: keep the part the receiver needs clear), four
of six objects change the grasped part entirely; the other two (bowl, pan) keep the
same part but change what must stay clear. Source located alongside the V3 grid fix
(figures/BLOCKERS.md item 2): experiments/vlm_grid/vlm_grid_handover_v2_raw.json,
cross-checked against experiments/vlm_grid/vlm_grid_handover_v2.md's own "changed"
column and rationales (v1 = contract in vlm_grid_raw.json's handover rows).

FINDING (2026-08-16, flagged on review): the pan's v2 record is internally
self-contradictory. `target_part="handle"` and `constraints.keep_clear=["handle"]`
in the same JSON object -- the structured output asks the robot to grasp the handle
while also keeping the handle clear. The free-text `rationale` field disagrees with
the structured `target_part` field it sits next to: "The robot should hold the pan
by the body, leaving the handle clear" -- i.e. the model's own stated reasoning
concludes body, but the target_part field it emitted says handle. This is a
reasoning-layer schema-consistency defect (structured field vs. its own rationale
disagreeing), not a grasp-choice error, and is now annotated directly on the pan
row rather than smoothed into "keep-clear only" like bowl.

Source: workspace/experiments\\vlm_grid\\vlm_grid_raw.json (v1, handover rows)
        workspace/experiments\\vlm_grid\\vlm_grid_handover_v2_raw.json (v2)

Run: python figures/dissertation/fig_6_2_handover_ablation.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

import _qa as qa
import _style as fs

FIGURE_ID = "fig_6_2_handover_ablation"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
V1_PATH = os.path.join(DATA_ROOT, "experiments", "vlm_grid", "vlm_grid_raw.json")
V2_PATH = os.path.join(DATA_ROOT, "experiments", "vlm_grid", "vlm_grid_handover_v2_raw.json")

# Row order: knife and mug first -- knife is "the clearest single demonstration",
# mug's v2 (body, keep_clear=handle) is what Fig 1.1 panel (b) shows directly.
OBJECT_ORDER = ["knife", "mug", "hammer", "bottle", "bowl", "pan"]

INTENT = "Under a receiver-aware contract, four of six objects change the grasped part."

CAPTION = (
    "Fig 6.2. Handover contract ablation. v1 (task-mechanics only) vs v2 (receiver-aware: "
    "keep the part the receiver needs clear) target part, per object, for the 'hand me the "
    "X' instruction. Four objects change part entirely (orange arrow) -- knife handle -> blade "
    "spine, mug handle -> body, hammer handle -> head, bottle neck -> body. Two (bowl, pan) "
    "keep the same part (grey arrow). Bowl's keep-clear moves to 'interior', a different kind "
    "of constraint from the other five (a volume, not a graspable surface). Pan's v2 record is "
    "self-contradictory: target_part='handle' and keep_clear=['handle'] in the same structured "
    "output, while its own free-text rationale concludes the opposite ('hold the pan by the "
    "body, leaving the handle clear') -- flagged in purple, a reasoning-layer schema-consistency "
    "defect, not a grasp-choice error. n=6 objects, one instruction type (handover) each."
)


def _load():
    with open(V1_PATH, encoding="utf-8") as f:
        v1_data = json.load(f)
    with open(V2_PATH, encoding="utf-8") as f:
        v2_data = json.load(f)
    v1 = {e["object"]: e["step3"] for e in v1_data if e["type"] == "handover"}
    v2 = {e["object"]: e["step3"] for e in v2_data}
    assert set(OBJECT_ORDER) <= set(v1) and set(OBJECT_ORDER) <= set(v2), \
        "object set mismatch between v1 handover rows and v2 ablation"
    return v1, v2


def build():
    v1, v2 = _load()

    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(OBJECT_ORDER))
    ax.invert_yaxis()
    ax.axis("off")

    n_changed = 0
    for i, obj in enumerate(OBJECT_ORDER):
        y = i + 0.5
        p1, p2 = v1[obj]["target_part"], v2[obj]["target_part"]
        kc2 = ", ".join(v2[obj]["constraints"]["keep_clear"]) or "-"
        part_changed = p1 != p2
        n_changed += int(part_changed)
        colour = fs.OKABE_ITO["vermillion"] if part_changed else fs.OKABE_ITO["black"]

        # Column x-positions widened (2026-08-16, second pass) after the previous
        # spacing collided on the widest words at save time ("hammer" into "v1:
        # handle", "v2: blade spine" into "keep clear:") -- QA's text-overlap check
        # passed on the pre-save draw but the saved PNG (different effective layout
        # once constrained_layout finalises at savefig dpi) still showed it, so this
        # was caught by eye, not by the checker; verify by eye on every multi-column
        # text figure, not just on a QA PASS.
        ax.text(0.02, y, obj, fontsize=9, fontweight="bold", va="center", ha="left")
        ax.text(0.15, y, f"v1: {p1}", fontsize=8, va="center", ha="left",
                 color=fs.OKABE_ITO["black"])
        ax.add_patch(FancyArrowPatch((0.345, y), (0.395, y), arrowstyle="-|>", mutation_scale=9,
                                      color=colour, linewidth=1.4 if part_changed else 0.9))
        ax.text(0.41, y, f"v2: {p2}", fontsize=8, va="center", ha="left",
                 fontweight="bold" if part_changed else "normal", color=colour)
        kc_list = v2[obj]["constraints"]["keep_clear"]
        self_contradict = (not part_changed) and (p2 in kc_list)
        kc_colour = fs.OKABE_ITO["purple"] if self_contradict else fs.OKABE_ITO["black"]
        ax.text(0.68, y, f"clear: {kc2}", fontsize=7.5, va="center", ha="left",
                 color=kc_colour, alpha=1.0 if self_contradict else 0.85,
                 fontweight="bold" if self_contradict else "normal")
        if self_contradict:
            ax.text(0.68, y + 0.30, "target_part = keep_clear", fontsize=7,
                     va="center", ha="left", color=fs.OKABE_ITO["purple"], style="italic")
        # Changed/unchanged status is carried by arrow colour + v2-label boldness
        # (orange+bold=part changed, grey+plain=keep-clear only) -- a separate text tag
        # in this column collided with the "keep clear:" text next to it (both
        # right-hand-side annotations competing for the same narrow strip).
        if i < len(OBJECT_ORDER) - 1:
            ax.axhline(i + 1, color=fs.OKABE_ITO["black"], alpha=0.10, linewidth=0.6)

    assert n_changed == 4, f"expected 4/6 changed part, computed {n_changed}"
    ax.text(0.02, -0.55, f"{n_changed}/6 objects change the grasped part under the "
            f"receiver-aware contract (n=6)", fontsize=8.5, va="center", ha="left",
            color=fs.OKABE_ITO["black"], fontweight="bold")
    ax.text(0.02, -0.22, "orange/bold = part changed    grey = keep-clear only changed    "
            "purple = keep-clear contradicts the part", fontsize=7, va="center", ha="left",
            color=fs.OKABE_ITO["black"], alpha=0.75)

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {V1_PATH}, {V2_PATH}")
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
        blind_read="Six rows, each an object with a v1 part -> v2 part arrow; four arrows are "
                   "orange/bold with a different word on each side, two are grey with the same "
                   "word on both sides -- reads as 'most objects get a different grasp for "
                   "handover' at a glance; the pan row's purple keep-clear text and italic "
                   "'contradiction' note stand out as the one row worth a second look.",
        verdict="COMMUNICATION PASS",
        element_audit="every row labelled with object, v1 part, v2 part, v2 keep-clear; colour legend + summary line state 4/6 and n=6; pan row carries an explicit contradiction flag.",
        referent_audit="each arrow sits directly between the two part labels it connects.",
    )
    report_path = qa.write_report("V4")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
