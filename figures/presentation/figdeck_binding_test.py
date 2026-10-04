#!/usr/bin/env python
r"""figdeck_binding_test.py -- FIG 3 for the MSc defence deck.

The binding discrimination test, shown honestly: with RELATION_HINTS present
the bind score looks like it discriminates real part names from controls;
with hints removed, a real part name and pure gibberish score identically.
Numbers are hard-coded from the project's own bind_part evaluation output.

    python figdeck_binding_test.py
"""
import argparse, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

BG, INK, PRIMARY, CAVEAT, GREY = (
    "#FAF9F6", "#16181D", "#12415C", "#C2703D", "#6B6560")

SOURCE = "bind_part RELATION_HINTS ablation (hint-table vs. hints-removed query scores)"

PANEL_A = [  # (label, score, is_real)
    ("blade",    7.38, True),
    ("handle",   7.17, True),
    ("lid knob", 2.38, False),
    ("rim",      2.38, False),
]
PANEL_B = [  # (label, score)
    ("blade",           2.800),
    ("xyzzy (nonsense)", 2.800),
]
XMAX = 8.2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="report_assets/figures/figdeck_binding_test.png")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    mono = FontProperties(family=["monospace"])
    sans = FontProperties(family=["sans-serif"])

    fig, (axA, axB) = plt.subplots(
        2, 1, figsize=(7.0, 4.5), dpi=200, height_ratios=[4, 2.4])
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.20, right=0.95, top=0.90, bottom=0.10,
                         hspace=0.62)

    # Panel A -- with hint table
    axA.set_facecolor(BG)
    ys = list(range(len(PANEL_A), 0, -1))
    for (name, score, real), y in zip(PANEL_A, ys):
        c = PRIMARY if real else GREY
        axA.barh(y, score, height=0.55, color=c, zorder=2)
        axA.text(-0.15, y, name, ha="right", va="center",
                  fontproperties=sans, fontsize=10.5, color=INK)
        axA.text(score + 0.15, y, "%.2f" % score, ha="left", va="center",
                  fontproperties=mono, fontsize=9.5, color=c)
    axA.set_xlim(0, XMAX)
    axA.set_ylim(0.3, len(PANEL_A) + 0.7)
    axA.set_yticks([])
    for sp in axA.spines.values():
        sp.set_visible(False)
    axA.set_xticks([])
    axA.text(0, len(PANEL_A) + 0.55,
              "RELATION_HINTS -- apparent discrimination",
              ha="left", va="bottom", fontproperties=sans, fontsize=10.5,
              color=INK)

    # Panel B -- hints removed
    axB.set_facecolor(BG)
    ysB = list(range(len(PANEL_B), 0, -1))
    for (name, score), y in zip(PANEL_B, ysB):
        axB.barh(y, score, height=0.55, color=CAVEAT, zorder=2)
        axB.text(-0.15, y, name, ha="right", va="center",
                  fontproperties=sans, fontsize=10.5, color=INK)
        axB.text(score + 0.15, y, "%.3f" % score, ha="left", va="center",
                  fontproperties=mono, fontsize=9.5, color=CAVEAT)
    axB.axvline(2.800, color=CAVEAT, lw=1.0, ls=(0, (4, 3)), zorder=1)
    axB.set_xlim(0, XMAX)
    axB.set_ylim(0.3, len(PANEL_B) + 0.9)
    axB.set_yticks([])
    for sp in axB.spines.values():
        sp.set_visible(False)
    axB.set_xticks([])
    axB.text(0, len(PANEL_B) + 0.7, "hints removed -- no discrimination",
              ha="left", va="bottom", fontproperties=sans, fontsize=10.5,
              color=INK)
    axB.text(2.800, 0.32,
              "identical score -- the binding cannot distinguish\n"
              "a part name from gibberish",
              ha="center", va="top", fontproperties=sans, fontsize=8.8,
              color=CAVEAT)

    fig.savefig(a.out, facecolor=BG)
    cap_path = os.path.splitext(a.out)[0] + ".txt"
    with open(cap_path, "w", encoding="utf-8") as fh:
        fh.write("With RELATION_HINTS the bind score separates real part "
                 "names from controls; with hints removed a real name and "
                 "gibberish score identically (source: %s).\n" % SOURCE)
    print("wrote %s and %s" % (a.out, cap_path))


if __name__ == "__main__":
    main()
