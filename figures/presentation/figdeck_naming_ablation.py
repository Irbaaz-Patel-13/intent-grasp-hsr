#!/usr/bin/env python
r"""figdeck_naming_ablation.py -- FIG 4 for the MSc defence deck.

3x9 matrix: three part-naming conditions (A hint table, B Set-of-Mark,
C point-based) against nine object/instruction pairs, coloured by outcome.
Reads report_assets/PART_NAMING_ABLATION.csv directly -- nothing recomputed.

    python figdeck_naming_ablation.py
"""
import argparse, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties

BG, INK, PRIMARY, CAVEAT, GREY = (
    "#FAF9F6", "#16181D", "#12415C", "#C2703D", "#6B6560")

CSV = "report_assets/PART_NAMING_ABLATION.csv"

METHOD_COLS = [("A_heuristic", "A . hint table"),
               ("B_som", "B . Set-of-Mark"),
               ("C_pointing", "C . point-based")]

ABBREV = {"lateral_protrusion": "lat_protr", "segment_a": "seg_a",
          "segment_b": "seg_b", "segment_c": "seg_c",
          "main_body": "main_body"}


def classify(outcome, chosen):
    if outcome == "SELECTED":
        return "resolved", ABBREV.get(chosen, chosen)
    if str(outcome).startswith("EVIDENCE_GATE_REFUSED"):
        return "refused", "NOISE"
    if outcome == "POINT_OFF_OBJECT":
        return "failed", "POINT_OFF_OBJECT"
    if outcome == "SPLIT":
        return "failed", "SPLIT"
    return "failed", str(outcome)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--out", default="report_assets/figures/figdeck_naming_ablation.png")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    # A handful of rows in this CSV have malformed trailing free-text fields
    # (an unescaped comma inside prose, an unquoted bracket list) that throw
    # off pandas' header alignment for the whole file. The columns this
    # figure needs -- object, instruction, method, chosen_component,
    # outcome -- sit at fixed positions (0, 1, 2, 4, last) before or after
    # that damage in every row, so we read by position instead of trusting
    # a header-aligned frame.
    keep_methods = {m for m, _ in METHOD_COLS}
    records = []
    with open(a.csv, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    for row in rows[1:]:
        obj, instr, method, chosen, outcome = row[0], row[1], row[2], row[4], row[-1]
        if method in keep_methods:
            records.append((obj, instr, method, chosen, outcome))

    pairs = list(dict.fromkeys((r[0], r[1]) for r in records))

    mono = FontProperties(family=["monospace"])
    sans = FontProperties(family=["sans-serif"])

    n_rows, n_cols = len(pairs), len(METHOD_COLS)
    fig, ax = plt.subplots(figsize=(11.0, 5.5), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.22, right=0.98, top=0.90, bottom=0.16)

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    COLORS = {"resolved": PRIMARY, "refused": GREY, "failed": CAVEAT}
    GAP = 0.06

    for ri, (obj, instr) in enumerate(pairs):
        ax.text(-0.08, ri + 0.5, "%s . %s" % (obj, instr), ha="right",
                va="center", fontproperties=sans, fontsize=9.6, color=INK,
                transform=ax.transData)
        for ci, (method, _) in enumerate(METHOD_COLS):
            match = [r for r in records if r[0] == obj and r[1] == instr
                     and r[2] == method]
            if not match:
                continue
            _, _, _, chosen, outcome = match[0]
            cat, label = classify(outcome, chosen)
            c = COLORS[cat]
            x0, y0 = ci + GAP / 2, ri + GAP / 2
            w = 1 - GAP
            h = 1 - GAP
            ax.add_patch(Rectangle((x0, y0), w, h, facecolor=c, alpha=0.85,
                                    edgecolor=BG, linewidth=2))
            fs = 8.6 if len(label) <= 12 else 7.0
            ax.text(x0 + w / 2, y0 + h / 2, label, ha="center", va="center",
                     fontproperties=mono, fontsize=fs, color=BG)

    for ci, (_, title) in enumerate(METHOD_COLS):
        ax.text(ci + 0.5, -0.20, title, ha="center", va="bottom",
                 fontproperties=sans, fontsize=10.5, color=INK)

    ax.text(0, n_rows + 0.55,
             "No knife instruction gets three-way agreement; the one "
             "A/B match ('hand me', both lateral_protrusion) is flagged "
             "in the log itself as coincidental, not independently verified.",
             ha="left", va="top", fontproperties=sans, fontsize=9.2,
             color=INK, transform=ax.transData)

    fig.savefig(a.out, facecolor=BG)
    cap_path = os.path.splitext(a.out)[0] + ".txt"
    with open(cap_path, "w", encoding="utf-8") as fh:
        fh.write("Selected component per condition and object/instruction "
                 "pair, coloured by outcome (source: %s).\n" % a.csv)
    print("wrote %s and %s (%d rows x %d cols)" % (a.out, cap_path, n_rows, n_cols))


if __name__ == "__main__":
    main()
