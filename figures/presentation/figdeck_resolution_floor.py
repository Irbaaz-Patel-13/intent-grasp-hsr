#!/usr/bin/env python
r"""figdeck_resolution_floor.py -- FIG 2 for the MSc defence deck.

Sensor resolution floor: measured component widths (px) against the code's
evidence-gate cutoff. Data is hard-coded from report_assets/SENSOR_ENVELOPE.md,
table V2 -- those numbers are already derived there (mm/px x measured mm width
at each component's own capture depth); nothing is recomputed here.

    python figdeck_resolution_floor.py
    python figdeck_resolution_floor.py --out report_assets/figures/figdeck_resolution_floor.png
"""
import argparse, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.font_manager import FontProperties

BG, INK, PRIMARY, CAVEAT, GREY = (
    "#FAF9F6", "#16181D", "#12415C", "#C2703D", "#6B6560")

SOURCE = "report_assets/SENSOR_ENVELOPE.md (table V2)"

# component, width_mm, depth_m, width_px -- table V2, verbatim
DATA = [
    ("knife handle",              24, 0.913, 15.18),
    ("remote lateral protrusion", 18, 0.920, 11.29),
    ("spoon",                     20, 0.918, 12.58),
    ("pot lid knob",              16, 0.989,  9.34),
    ("mug handle",                 4, 0.925,  2.50),
]
FLOOR_LO, FLOOR_HI = 3.5, 3.8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="report_assets/figures/figdeck_resolution_floor.png")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    mono = FontProperties(family=["monospace"])
    sans = FontProperties(family=["sans-serif"])

    # order by width descending, top to bottom
    rows = sorted(DATA, key=lambda r: -r[3])
    n = len(rows)
    ys = list(range(n, 0, -1))

    fig, ax = plt.subplots(figsize=(7.0, 5.0), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.30, right=0.93, top=0.90, bottom=0.14)

    ax.set_xlim(0, 17)
    ax.set_ylim(0.4, n + 0.6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_yticks([])

    ax.axvspan(FLOOR_LO, FLOOR_HI, color=CAVEAT, alpha=0.22, lw=0, zorder=1)
    ax.text((FLOOR_LO + FLOOR_HI) / 2, n + 0.42, "evidence floor",
            ha="center", va="bottom", fontproperties=sans, fontsize=8.6,
            color=CAVEAT)

    for (name, mm, depth, px), y in zip(rows, ys):
        below = px < FLOOR_LO
        c = CAVEAT if below else PRIMARY
        ax.scatter([px], [y], s=90, facecolor=c, edgecolor=c, zorder=3)
        ax.text(-0.4, y, name, ha="right", va="center",
                fontproperties=sans, fontsize=10.5, color=INK)
        tag = "NOISE" if below else "ok"
        ax.text(px + 0.55, y, tag, ha="left", va="center",
                fontproperties=mono, fontsize=9.5, color=c)
        ax.text(px, y - 0.30, "%.2f px" % px, ha="center", va="top",
                fontproperties=mono, fontsize=8.2, color=GREY)

    ax.tick_params(axis="x", colors=INK, labelsize=9)
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(mono)
    ax.set_xlabel("component width (px)", fontproperties=sans, fontsize=10,
                  color=INK)

    # direct callout on the mug handle
    mug_y = ys[[r[0] for r in rows].index("mug handle")]
    ax.text(6.4, mug_y, "4 mm ≈ 2.5 px\nbelow the sensor's evidence floor",
            fontproperties=sans, fontsize=9.2, color=CAVEAT,
            va="center", ha="left")

    fig.savefig(a.out, facecolor=BG)
    cap_path = os.path.splitext(a.out)[0] + ".txt"
    with open(cap_path, "w", encoding="utf-8") as fh:
        fh.write("Measured component widths in pixels against the sensor's "
                 "~6 mm evidence-gate cutoff (source: %s).\n" % SOURCE)
    print("wrote %s and %s" % (a.out, cap_path))


if __name__ == "__main__":
    main()
