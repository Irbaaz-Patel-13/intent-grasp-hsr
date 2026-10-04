"""Fig 3.2 -- Portfolio scope against delivered and evaluated scope (Class S).

Evidence audit (repo: portfolio PDF, codex/CODEX.md, live source), see script
docstring notes at each placement below. Zones are VERIFIED, not assumed from
the design brief's proposed layout -- several placements differ from what a
naive reading of the brief would produce; each is cited.

Evidence sources:
  IrbaazAhmedPatel_H00523379_Dr._Mauro_Dragone-3.pdf, sec 1.3 -- objectives
    O1-O6 verbatim (portfolio's own committed scope).
  codex/CODEX.md sec 3, 7 -- live/diagnostic status and commit history for
    every module cited below.
  visual_grounding.py:182-220 (`ground_multiview`) -- real O3 delivery is
    per-view scoring + best-view SELECTION, not pixel-level fusion into
    unified 3D mask clusters (which is what O3's own text commits to).
  report_assets/PART_NAMING_ABLATION.csv -- real 3-method part-selection
    comparison, evaluated offline (not a committed objective).
  codex/CODEX.md sec 7 (2026-07-13/14 commits) -- geometric decomposition
    replaced the committed LangSAM/mask part-selection approach; not itself
    a committed deliverable.
  hand_part_grounding.py [codex: LIVE, "parallel path", not in
    run_grounding_grasp.py's import chain] -- eye-in-hand path delivered,
    used only by eval_battery.py/part_decomposition_report.py (offline).
  trials.csv (bundle, 11 rows) + DEMO_RUNBOOK.md -- hardware trials delivered
    at one object (mug), far below O5's committed >=10 objects x 2-3
    instructions x 5 repeats.
  No "occlusion" hit anywhere in project code/csv/md (grep, this session) --
    O6 not evidenced as delivered or evaluated in any form.
  No single-vs-multi-view success-rate ablation artifact found (grep, this
    session) -- O4's PyBullet embedding is delivered/evaluated (portfolio
    sec 1.8 preliminary results); the specific view-condition ablation is not.

Run: python figures/dissertation/fig_3_2_scope.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

import _qa as qa
import _style as fs

FIGURE_ID = "fig_3_2_scope"

FIG_W_IN, FIG_H_IN = fs.TEXT_WIDTH_IN, 4.6

COMMITTED = fs.OKABE_ITO["blue"]
DELIVERED = fs.OKABE_ITO["orange"]
INK = "black"
MUTED = "#595959"

INTENT = ("The portfolio's committed scope, what was actually delivered, and what was actually "
          "evaluated are three different sets, not one.")

# (label, zone, eval_marker)  zone: 'committed' | 'both' | 'delivered'
# eval_marker: 'HW' evaluated on hardware, 'offline' evaluated offline only, '\u2014' not evaluated
COMPONENTS = [
    ("Multi-view mask fusion (O3)\u2020", "committed", "\u2014"),
    ("Occlusion-failure analysis (O6)", "committed", "\u2014"),
    ("Single/multi-view ablation (O4)", "committed", "\u2014"),
    ("Literature review (O1)", "both", "\u2014"),
    ("Reasoning\u2192grounding\u2192grasp (O2)", "both", "HW"),
    ("PyBullet HSR simulation (O4)", "both", "offline"),
    ("Hardware trials (O5)\u2021", "both", "HW"),
    ("Geometric part decomposition", "delivered", "HW"),
    ("3-method part-selection comparison", "delivered", "offline"),
    ("Eye-in-hand capture path", "delivered", "offline"),
]

CAPTION = (
    "Fig 3.2. Portfolio scope against delivered and evaluated scope. Left region: objectives "
    "committed in the portfolio proposal (O1-O6). Right region: what the repository actually "
    "implements. Overlap: both committed and delivered. Marker beside each item states how it "
    "was evaluated -- HW (hardware), offline, or \u2014 (not evaluated) -- verified from the "
    "repository, not inferred from code existing. \u2020O3 committed pixel-level fusion of "
    "multiple views into unified 3D mask clusters; the delivered mechanism "
    "(visual_grounding.py's ground_multiview) scores each view independently and selects the "
    "best-scoring one -- view selection, not fusion, a materially weaker capability than "
    "committed, so this item stays in the committed-only region. \u2021Hardware trials were "
    "delivered and evaluated, but at reduced scale: 11 trials on one object (mug), against the "
    "committed >=10 objects x 2-3 instructions x 5 repeats. Region area does not encode quantity."
)


def build():
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor="white", constrained_layout=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W_IN); ax.set_ylim(0, FIG_H_IN)
    ax.set_aspect("equal")
    ax.axis("off")

    cx_l, cx_r, cy = 2.15, 4.45, 2.55
    rw, rh = 2.35, 1.85

    ax.add_patch(Ellipse((cx_l, cy), rw * 2, rh * 2, facecolor=COMMITTED, alpha=0.14,
                          edgecolor=COMMITTED, linewidth=1.6, zorder=1))
    ax.add_patch(Ellipse((cx_r, cy), rw * 2, rh * 2, facecolor=DELIVERED, alpha=0.14,
                          edgecolor=DELIVERED, linewidth=1.6, zorder=1))

    ax.text(0.95, cy + rh + 0.28, "Committed in portfolio", fontsize=11, fontweight="bold",
             color=COMMITTED, ha="left")
    ax.text(FIG_W_IN - 0.35, cy + rh + 0.28, "Delivered", fontsize=11, fontweight="bold",
             color=DELIVERED, ha="right")

    # Every zone uses centre-anchored, stacked (label above, marker below)
    # text -- avoids the left-/right-anchored text growing INTO the
    # neighbouring zone that a naive outward-growing layout produces.
    zone_x = {"committed": 1.00, "both": (cx_l + cx_r) / 2, "delivered": 5.60}
    zone_rows = {"committed": [], "both": [], "delivered": []}
    for label, zone, ev in COMPONENTS:
        zone_rows[zone].append((label, ev))

    row_h = 0.40
    max_n = max(len(rows) for rows in zone_rows.values())
    shared_top = cy + (max_n - 1) * row_h / 2
    for zone, rows in zone_rows.items():
        x = zone_x[zone]
        for i, (label, ev) in enumerate(rows):
            y = shared_top - i * row_h
            marker_colour = MUTED if ev == "\u2014" else (fs.OKABE_ITO["green"] if ev == "HW"
                                                            else fs.OKABE_ITO["sky_blue"])
            ax.text(x, y + 0.11, label, fontsize=7.6, color=INK, ha="center", va="center")
            ax.text(x, y - 0.12, f"[{ev}]", fontsize=7.3, color=marker_colour, ha="center",
                     va="center", fontweight="bold")

    # legend for evaluation markers
    ly = 0.55
    for i, (tag, colour, desc) in enumerate([
        ("HW", fs.OKABE_ITO["green"], "evaluated on hardware"),
        ("offline", fs.OKABE_ITO["sky_blue"], "evaluated offline only"),
        ("\u2014", MUTED, "not evaluated"),
    ]):
        x0 = 0.9 + i * 2.0
        ax.text(x0, ly, f"[{tag}]", fontsize=8, color=colour, fontweight="bold", ha="left", va="center")
        ax.text(x0 + 0.62, ly, desc, fontsize=8, color=INK, ha="left", va="center")

    ax.text(FIG_W_IN / 2, 0.16, "Region area does not represent quantity.", fontsize=7.5,
             style="italic", color=MUTED, ha="center", va="center")

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("B")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
