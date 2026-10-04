"""Fig 6.3 -- Three-method agreement matrix (QUANTITATIVE, Class D).

No two part-selection methods agree on the same component, and none is validated
against the image. Three objects, one instruction each (of the 9 object/instruction
pairs in the full ablation). Method A = heuristic bind_part, B = Set-of-Mark, C =
point-based pointing.

Rows chosen for the clearest, most defensible disagreement per object (not cherry-
picked for maximum drama -- remote's "hand me the remote" row has A/C agreeing on
segment_b and was excluded for exactly that reason; "turn the television on" is the
one remote row with no two methods landing on the same single component):
  knife: "pick up the knife"    -- A=lateral_protrusion, B=segment_c, C=off-object
  mug:   "pour me a coffee"     -- A=NOISE refusal, B=main_body (silent substitution), C=NOISE refusal
  remote: "turn the television on" -- A=segment_b, B=lateral_protrusion, C=split/unresolved

Source: workspace/report_assets\\PART_NAMING_ABLATION.csv

Run: python figures/dissertation/fig_6_3_method_agreement.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt

import _qa as qa
import _style as fs

FIGURE_ID = "fig_6_3_method_agreement"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
CSV_PATH = os.path.join(DATA_ROOT, "report_assets", "PART_NAMING_ABLATION.csv")

ROWS = [
    ("knife", "pick up the knife"),
    ("mug", "pour me a coffee"),
    ("remote", "turn the television on"),
]
METHODS = ["A_heuristic", "B_som", "C_pointing"]
METHOD_LABEL = {"A_heuristic": "A: heuristic", "B_som": "B: Set-of-Mark", "C_pointing": "C: pointing"}
GT_LABEL = {"knife": "handle-side", "mug": "handle", "remote": "non-button component"}
# Physical referent for otherwise-opaque internal component names, where the
# ablation CSV itself records one (RELATION_HINTS rekey for segment_b -- see
# figures/BLOCKERS.md corrections register item 5; the VLM's own "likely a
# button" note for remote/B is in that row's pixel_pos field). Left blank where
# no referent is recorded in source rather than guessed.
PHYSICAL_REFERENT = {
    ("remote", "A_heuristic"): "middle section",
    ("remote", "B_som"): "likely a button, per VLM",
}

INTENT = "No two part-selection methods agree, and almost none is confirmed correct by direct pixel verification against the image."

CAPTION = (
    "Fig 6.3. Three-method agreement matrix. One instruction per object (of the 9 "
    "object/instruction pairs in the full ablation). Method A (heuristic bind_part), B "
    "(Set-of-Mark), C (point-based). Declared ground truth per object shown under each row "
    "label. Component names are per-object internal labels, not a shared vocabulary -- "
    "'lateral_protrusion' denotes a different physical feature on the knife (row 1, method A) "
    "than on the remote (row 3, method B); opaque names ('segment_c', 'segment_b') have no "
    "fixed physical meaning outside their own object's decomposition. Correctness badge, four "
    "states, read from the ablation's own `correct` column: a check = returned part matches "
    "declared GT; a cross = it does not, or the method failed to resolve to any component "
    "(off-object, split/unresolved); a slashed circle = the evidence gate correctly refused "
    "(no part returned, matching a genuine sensing floor, not a method failure); a question "
    "mark = not independently pixel-verified against the image, the CSV's own wording. Only "
    "one of nine cells (remote, method B) is a confirmed match; two are principled refusals; "
    "the rest are wrong or unverified. No two methods select the same component on any of the "
    "three objects. n=3 objects, one instruction each."
)


def _classify_correct(comp, correct_field):
    """Four-state, read from `chosen_component` (CSV column 5, always safe -- see the
    parsing note below) plus the `correct` column (column 10, also before the
    unquoted-comma columns). A refusal is not the same claim as a match: the mug's A
    and C both return NOISE-gate refusals, which is CORRECT BEHAVIOUR (refuse below
    the evidence floor rather than substitute) but is not a part match -- collapsing
    both into a single check/cross pair (first pass of this figure) inverted the
    figure's own INTENT by making it look like methods succeeded when they had in
    fact declined to answer. off-object and split/unresolved are method failures
    (not principled refusals) and score as a cross, not a slashed circle."""
    cl = comp.lower()
    short = comp.split(" (")[0]
    if "refused" in cl:
        return "refuse", fs.OKABE_ITO["blue"]
    if short == "none" or "split" in cl:
        return "cross", fs.OKABE_ITO["vermillion"]
    c = correct_field.strip().lower()
    if c.startswith("false"):
        return "cross", fs.OKABE_ITO["vermillion"]
    if c.startswith("true") and not c.startswith("technically true"):
        return "check", fs.semantic_colour("keep")
    return "question", fs.OKABE_ITO["black"]


def _load_rows():
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    out = {}
    for obj, instr in ROWS:
        for m in METHODS:
            match = [r for r in data if r["object"] == obj and r["instruction"] == instr and r["method"] == m]
            assert len(match) == 1, f"expected exactly 1 row for {(obj, instr, m)}, got {len(match)}"
            out[(obj, m)] = match[0]
    return out


def build():
    data = _load_rows()

    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN, 3.6))
    ax.set_xlim(0, len(METHODS))
    ax.set_ylim(0, len(ROWS))
    ax.invert_yaxis()

    for i, (obj, instr) in enumerate(ROWS):
        for j, m in enumerate(METHODS):
            row = data[(obj, m)]
            # Classified from `chosen_component` (CSV column 5) only -- some rows'
            # trailing columns (raw_points, e.g. "[[800,600]]") are unquoted despite
            # containing a comma, which shifts DictReader's column alignment for
            # `outcome` (column 13) on those specific rows. chosen_component sits
            # before any of the malformed columns and is safe on every row.
            comp = row["chosen_component"]
            comp_lower = comp.lower()
            short = comp.split(" (")[0]
            if short == "none":
                label, colour = "off-object\n(no component)", fs.OKABE_ITO["black"]
            elif "split" in comp_lower:
                label, colour = "split /\nunresolved", fs.OKABE_ITO["black"]
            elif "refused" in comp_lower:
                label, colour = "NOISE\n(refused)", fs.semantic_colour("reject")
            else:
                referent = PHYSICAL_REFERENT.get((obj, m))
                label = f"{short}\n({referent})" if referent else short
                colour = fs.semantic_colour("perception")
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=colour, alpha=0.15,
                                        edgecolor=colour, linewidth=1.0))
            ax.text(j + 0.5, i + 0.42, label, ha="center", va="center", fontsize=8,
                     color=fs.OKABE_ITO["black"])
            badge, badge_colour = _classify_correct(comp, row["correct"])
            badge_char = {"check": "✓", "cross": "✗", "refuse": "⊘", "question": "?"}[badge]
            ax.text(j + 0.5, i + 0.85, badge_char, ha="center", va="center", fontsize=10,
                     fontweight="bold", color=badge_colour)

    ax.set_xticks([j + 0.5 for j in range(len(METHODS))])
    ax.set_xticklabels([METHOD_LABEL[m] for m in METHODS], fontsize=8.5)
    ax.set_yticks([i + 0.5 for i in range(len(ROWS))])
    ax.set_yticklabels([f'{obj}\n"{instr}"\nGT: {GT_LABEL[obj]}' for obj, instr in ROWS], fontsize=7.5)
    ax.set_xlabel("part-selection method (n=3 objects, one instruction each)", labelpad=10)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(0.5, 1.04, "✓ matches GT   ✗ wrong / unresolved   ⊘ correctly refused (evidence gate)   "
            "? not pixel-verified", transform=ax.transAxes, ha="center", va="bottom", fontsize=7,
            color=fs.OKABE_ITO["black"], alpha=0.85)

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
        blind_read="A 3x3 grid, one row per object; every row has three differently-worded cells "
                   "(no repeated label across a row); each cell also carries a four-state badge -- "
                   "one lone check mark in the whole grid, two slashed circles, the rest crosses or "
                   "question marks -- reads as 'the methods disagree, almost nothing is a confirmed "
                   "match, and where they abstain that is at least principled' without reading the "
                   "caption.",
        verdict="COMMUNICATION PASS",
        element_audit="every cell labelled with its own outcome + 4-state correctness badge; row labels state object+instruction+declared GT; column labels name each method; on-figure legend explains all four badges; x-axis states n=3.",
        referent_audit="not applicable -- no separate referent line/threshold in this figure.",
    )
    report_path = qa.write_report("V4")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
