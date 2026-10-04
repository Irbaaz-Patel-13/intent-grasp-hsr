"""Fig 2.1 -- Evolution of grasp synthesis (Class S -- Schematic).

Three-stage progression -- source of grasp information, representation, task
conditioning -- not a citation list. Background/architecture context, no
repository data source.

Run: python figures/dissertation/fig_2_1_evolution_grasp_synthesis.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt

import _qa as qa
import _style as fs

FIGURE_ID = "fig_2_1_evolution_grasp_synthesis"

INTENT = ("Grasp synthesis has moved from geometry alone, through learned priors over shape, "
          "to synthesis conditioned on what the task actually requires.")

STAGES = [
    dict(title="Geometric / analytic", colour=fs.OKABE_ITO["blue"],
         rows=[("source", ["object geometry", "(CAD / mesh)"]),
               ("representation", ["analytic contact", "points, force closure"]),
               ("task conditioning", ["none -- object-agnostic", "to intended use"])]),
    dict(title="Data-driven", colour=fs.OKABE_ITO["orange"],
         rows=[("source", ["learned prior over", "grasp datasets"]),
               ("representation", ["learned pose/quality", "predictor (e.g. CGN)"]),
               ("task conditioning", ["none -- best graspable", "region only"])]),
    dict(title="Language-conditioned\n(this project)", colour=fs.OKABE_ITO["green"],
         rows=[("source", ["instruction + reasoning", "+ geometry"]),
               ("representation", ["part-scoped candidate", "poses"]),
               ("task conditioning", ["explicit -- instruction sets", "part + constraints"])]),
]

CAPTION = (
    "Fig 2.1. Three stages in the source of grasp information used by prior work, characterised "
    "by what determines the grasp (geometry, learned shape prior, or task instruction), not an "
    "exhaustive citation list."
)


def build():
    fig, ax = plt.subplots(figsize=(fs.TEXT_WIDTH_IN, 3.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")

    n = len(STAGES)
    w = 0.27
    gap = (1 - n * w) / (n + 1)
    y0, h = 0.10, 0.74

    for i, stage in enumerate(STAGES):
        x = gap + i * (w + gap)
        fs.status_card(ax, (x, y0), w, h, stage["colour"], title=stage["title"],
                        rows=stage["rows"], fontsize=7.6, row_gap=0.052)
        if i < n - 1:
            fs.orthogonal_arrow(ax, (x + w + 0.006, y0 + h / 2), (x + w + gap - 0.006, y0 + h / 2))

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] source: none (Class S, conceptual)")
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("B")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
