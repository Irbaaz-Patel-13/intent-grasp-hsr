"""Fig 5.1 -- Mask coverage by object and run (QUANTITATIVE, Class D).

Every live run where LangSAM part-level text grounding was actually
exercised on a real capture returns a "part" mask covering 86-97% of the
whole-object detection box. Six live runs exist in this repo, two objects
(knife x3, remote x3) -- this is `new_c_langsam_coverage.py`'s own stated
scope ("no other object has a live part-grounding run logged in this
repo"), verified again below by re-reading each log's collapse-warning
line directly rather than trusting the constant table.

Scope note (see figures/BLOCKERS.md): the FINAL register's Fact Block also
cites a third figure, "mug 98%", for this same phenomenon. Searched
q6_intent_mug.log, ax4_mug.log, bc_mug.log, bi9_mug.log, bm5_mug.log,
bo_mug_*.log and every *.json under report_assets/figure_data/ -- no
"[VisualGrounder] ... collapsed to whole object" line, and no other 98%
coverage figure, exists for the mug anywhere in this repo. The mug's own
documented perception failure (q6_intent_mug.log line 5; PERCEPTION_EVIDENCE.md
row "Evidence gate refuses insufficient parts") is a NOISE point-count/width
gate refusal on the handle component -- a different mechanism from LangSAM
collapse, explicitly distinguished as such in PERCEPTION_EVIDENCE.md itself.
"86-98%" appears in codex/CODEX.md and CODEBASE_GUIDE.md as the stated range
of the same 6 knife/remote runs (97 max, not 98) -- the "98" most likely
originates from that rounded/paraphrased range text, not a separate mug
measurement. This figure therefore plots only the 6 sourced runs and does
not include a mug bar; flagged as BLOCKED-DATA-GAP for the mug value in
BLOCKERS.md rather than fabricated.

Sources:
  workspace/run_knife_pick2.log, run_knife_hand.log, run_knife_put.log
  workspace/run_remote_hand.log, run_remote_power.log, run_remote_put.log
  figures/presentation/new_c_langsam_coverage.py (RUNS list, prior-verified source, re-checked below)

Run: python figures/dissertation/fig_5_1_mask_coverage.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt

import _qa as qa
import _style as fs

FIGURE_ID = "fig_5_1_mask_coverage"
from intent_grasp.paths import WORKSPACE  # noqa: E402
DATA_ROOT = str(WORKSPACE)
# object, run, pct, log file -- verbatim from new_c_langsam_coverage.py RUNS
RUNS = [
    ("knife",  "pick",  97, "run_knife_pick2.log"),
    ("knife",  "hand",  97, "run_knife_hand.log"),
    ("knife",  "put",   97, "run_knife_put.log"),
    ("remote", "hand",  88, "run_remote_hand.log"),
    ("remote", "power", 86, "run_remote_power.log"),
    ("remote", "put",   86, "run_remote_put.log"),
]

INTENT = ("Part-level queries return masks covering nearly the whole object on every "
          "live run where part grounding was actually measured.")

CAPTION = (
    "Fig 5.1. Mask coverage by object and run. Coverage = returned-part mask pixels / "
    "whole-object mask pixels (metric defined in Fig 3.6). All 6 live runs where LangSAM "
    "part-level text grounding was exercised on a real capture (knife x3, remote x3 -- the "
    "only two objects with a logged live part-grounding run in this repository) return a "
    "returned-part mask covering 86-97% of the whole-object detection box, against a 100% "
    "reference line. The knife's three instructions ('pick up', 'hand me', 'put away') "
    "independently collapse to the identical 97% -- not a copy error, the same mechanism "
    "firing on every instruction for that object. n=6 runs, 2 objects; not claimed as a "
    "broader sample (new_c_langsam_coverage.py's own documented scope)."
)


def _verify_sources():
    for obj, run, pct, log_name in RUNS:
        path = os.path.join(DATA_ROOT, log_name)
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        needle = f"collapsed to whole object ({pct}% of object mask covered)"
        assert needle in text, f"{path} does not contain expected line {needle!r}"


def build():
    _verify_sources()
    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN, 3.2))

    labels = [f"{obj}\n{run}" for obj, run, _, _ in RUNS]
    pcts = [p for _, _, p, _ in RUNS]
    colours = [fs.semantic_colour("perception") if obj == "knife" else fs.OKABE_ITO["sky_blue"]
               for obj, _, _, _ in RUNS]

    ax.axhline(100, color=fs.OKABE_ITO["black"], linewidth=1.0, linestyle="--", zorder=1)
    ax.text(len(RUNS) - 0.5, 100.6, "whole-object reference (100%)", fontsize=7.5,
            ha="right", va="bottom", color=fs.OKABE_ITO["black"])

    bars = ax.bar(labels, pcts, color=colours, width=0.55, zorder=2)
    for bar, p in zip(bars, pcts):
        ax.annotate(f"{p}%", (bar.get_x() + bar.get_width() / 2, p),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    # Three identical 97% values in a row reads as a copy error unless called out --
    # it is real (three different instructions, same collapse) and part of the finding.
    ax.annotate("three instructions,\nidentical collapse", xy=(1, 97), xytext=(1, 55),
                ha="center", va="center", fontsize=7.5, color=fs.OKABE_ITO["black"],
                arrowprops=dict(arrowstyle="-", shrinkA=2, shrinkB=8, lw=0.8,
                                 color=fs.OKABE_ITO["black"]))

    ax.set_ylabel("part-mask coverage (% of object mask)")
    ax.set_xlabel("object / run (n=6 live runs)")
    ax.set_ylim(0, 112)
    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] sources: {[r[3] for r in RUNS]}")
    fig = build()
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    qa.record_communication_check(
        FIGURE_ID, INTENT,
        blind_read="Six bars, all close to a dashed 100% reference line (86-97%); reads as "
                   "'every measured run returns almost the whole object, not a part' without "
                   "reading the caption.",
        verdict="COMMUNICATION PASS",
        element_audit="every bar labelled with its own %; x-axis states n=6 runs; colour separates the two objects (knife/remote).",
        referent_audit="100% reference line labelled directly; each % label anchored over its own bar.",
    )
    report_path = qa.write_report("V1")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
