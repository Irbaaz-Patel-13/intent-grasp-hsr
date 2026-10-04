"""
new_f_failure_register.py -- NEW-F: Failure Mode Distribution.

Scientific claim: the project's 17 documented failure modes/limitations
concentrate in perception (7) and execution (8), not reasoning (2); most
open (unresolved) rows are measured LIMITATIONS of the platform/sensing,
not unfixed DEFECTS; planning (collision-aware base placement) produced
zero documented failure modes across the whole trial series -- a real
positive result, not missing data.
Supporting evidence: report_assets/FAILURE_REGISTER.csv (17 real rows;
  see that file's own header for the selection_criterion this figure
  inherits: real, logged/sourced failures and measured limitations that
  halted a run, endangered hardware, produced a wrong/refused outcome, or
  were flagged as a citability risk in this project's own audit
  documents -- not every code change, and not successes).
Required real data: layer/kind/fix_status per row -- used directly.
Required diagrammatic elements: the unit-marker layout (one square per
  row) is a diagrammatic tally, not new data.

Run: python new_f_failure_register.py
Output: generated_assets/new_f/new_f_failure_register.png
"""
import argparse
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "report_assets", "FAILURE_REGISTER.csv")

LAYER_ORDER = ["reasoning", "perception", "execution", "planning"]
KIND_COLOR = {"defect": fs.REJECTED, "limitation": fs.CANDIDATE, "unexplained": fs.MUTED}
FIX_MARK = {"confirmed_with_recovery_trial": "\u2713", "patched_no_recovery_trial": "P",
            "diagnosed_not_implemented": "?", "open": ""}


def load_rows():
    with open(CSV_PATH) as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_f"), "new_f_failure_register.png")
    rows = load_rows()
    by_layer = {layer: [r for r in rows if r["layer"] == layer] for layer in LAYER_ORDER}

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Failure Mode Distribution -- Perception and Execution, Not Reasoning",
                 **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              f"{len(rows)} real documented failure modes/limitations, grouped by pipeline layer "
              f"(report_assets/FAILURE_REGISTER.csv)", **fs.BODY)

    GRID_Y0, GRID_H = 0.24, 0.54
    ax = fig.add_axes([0.20, GRID_Y0, 0.62, GRID_H])
    ax.set_xlim(0, 9.5)
    ax.set_ylim(-0.6, len(LAYER_ORDER) - 0.4)
    ax.invert_yaxis()
    ax.axis("off")

    sq = 0.72
    for i, layer in enumerate(LAYER_ORDER):
        entries = by_layer[layer]
        fig.text(0.19, GRID_Y0 + GRID_H * (1 - (i + 0.5) / len(LAYER_ORDER)), f"{layer.upper()}\n({len(entries)})",
                 ha="right", va="center", color=fs.INK, fontsize=12, weight="bold", family=fs.FONT,
                 linespacing=1.3)
        if not entries:
            ax.text(0.3, i, "0", ha="left", va="center", color=fs.MUTED, fontsize=16, weight="bold",
                    family=fs.FONT)
            ax.text(1.3, i, "no documented failure mode across the trial series -- a real result, "
                    "not missing data", ha="left", va="center", color=fs.MUTED, fontsize=10, family=fs.FONT,
                    style="italic")
            continue
        for j, r in enumerate(entries):
            x = j * 1.0
            color = KIND_COLOR[r["kind"]]
            ax.add_patch(Rectangle((x, i - sq / 2), sq, sq, facecolor=color, edgecolor=fs.SLIDE_BG,
                                    linewidth=1.5, alpha=0.9, zorder=3))
            mark = FIX_MARK[r["fix_status"]]
            if mark:
                mark_color = fs.SLIDE_BG if r["kind"] != "unexplained" else fs.INK
                ax.text(x + sq / 2, i, mark, ha="center", va="center", color=mark_color, fontsize=13,
                        weight="bold", family=fs.FONT, zorder=4)

    # legend: kind (color) on one row, fix_status (marker) on another --
    # two rows, generously spaced, in the gap between the grid and the
    # caption (not sharing vertical space with either).
    ax_leg = fig.add_axes([0.20, 0.115, 0.62, 0.09])
    ax_leg.axis("off")
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(0, 1)
    kx = 0.0
    for kind, color in KIND_COLOR.items():
        ax_leg.add_patch(Rectangle((kx, 0.68), 0.018, 0.28, facecolor=color, transform=ax_leg.transAxes))
        ax_leg.text(kx + 0.03, 0.82, kind, transform=ax_leg.transAxes, ha="left", va="center",
                    color=fs.INK, fontsize=10, family=fs.FONT)
        kx += 0.16
    mx = 0.0
    for status, mark in FIX_MARK.items():
        label = {"confirmed_with_recovery_trial": "confirmed+recovery", "patched_no_recovery_trial": "patched",
                  "diagnosed_not_implemented": "diagnosed only", "open": "open"}[status]
        ax_leg.text(mx, 0.22, f"[{mark or ' '}]", transform=ax_leg.transAxes, ha="left", va="center",
                    color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)
        ax_leg.text(mx + 0.045, 0.22, label, transform=ax_leg.transAxes, ha="left", va="center",
                    color=fs.MUTED, fontsize=10, family=fs.FONT)
        mx += 0.235

    # side panel: kind totals
    ax2 = fig.add_axes([0.84, 0.30, 0.13, 0.34])
    ax2.axis("off")
    ax2.add_patch(Rectangle((0, 0), 1, 1, transform=ax2.transAxes, fill=False, edgecolor=fs.FAINT, linewidth=1.0))
    ax2.text(0.5, 0.94, "By kind", transform=ax2.transAxes, ha="center", va="top", color=fs.INK, fontsize=11,
             weight="bold", family=fs.FONT)
    kinds = ["defect", "limitation", "unexplained"]
    counts = {k: sum(1 for r in rows if r["kind"] == k) for k in kinds}
    y = 0.76
    for k in kinds:
        ax2.text(0.10, y, k, transform=ax2.transAxes, ha="left", va="center", color=KIND_COLOR[k], fontsize=10,
                 weight="bold", family=fs.FONT)
        ax2.text(0.90, y, str(counts[k]), transform=ax2.transAxes, ha="right", va="center", color=KIND_COLOR[k],
                 fontsize=13, weight="bold", family=fs.FONT)
        y -= 0.16

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "One square per real row: red=defect, amber=limitation, grey=unexplained. Marker = fix_status "
              "(color stays reserved for kind). Source: report_assets/FAILURE_REGISTER.csv.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Selection criterion (from the CSV's own header): real, logged/sourced failures and measured "
              "limitations that halted a run, endangered hardware, produced a wrong/refused outcome, or were",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "flagged as a citability risk in this project's own audit documents -- not every code change, and not successes.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: counts by layer as 4 bars, planning:0 annotated, then
    the 2 real confirmed-with-recovery-trial chains named in one line each.
    The 17-square unit tally moves to report/appendix."""
    out_path = out_path or os.path.join(fs.asset_dir("new_f"), "new_f_failure_register_slide.png")
    rows = load_rows()
    by_layer = {layer: [r for r in rows if r["layer"] == layer] for layer in LAYER_ORDER}

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Perception and Execution Fail -- Planning Never Has", **{**fs.TITLE, "size": 32},
                 x=fs.MARGIN, ha="left")

    # Primary hero: the total, above everything else -- the per-layer bars
    # are the breakdown of THIS number, not a competing headline.
    fig.text(0.06, 0.855, f"{len(rows)}", color=fs.INK, fontsize=64, weight="bold", family=fs.FONT)
    fig.text(0.20, 0.865, "documented failure\nmodes / limitations", color=fs.MUTED, fontsize=16,
              family=fs.FONT, linespacing=1.4)

    ax = fig.add_axes([0.06, 0.24, 0.55, 0.36])
    ax.set_facecolor(fs.SLIDE_BG)
    counts = [len(by_layer[layer]) for layer in LAYER_ORDER]
    colors = [fs.REJECTED if layer != "planning" else fs.MUTED for layer in LAYER_ORDER]
    bars = ax.bar(LAYER_ORDER, counts, color=colors, width=0.6)
    for layer, c, bar in zip(LAYER_ORDER, counts, bars):
        if layer == "planning":
            ax.text(bar.get_x() + bar.get_width() / 2, 0.15, "0", ha="center", va="bottom", color=fs.INK,
                    fontsize=56, weight="bold", family=fs.FONT)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, c + 0.15, f"{c}", ha="center", va="bottom",
                    color=fs.INK, fontsize=56, weight="bold", family=fs.FONT)
    ax.set_xticks(range(len(LAYER_ORDER)))
    ax.set_xticklabels([l.upper() for l in LAYER_ORDER], color=fs.INK, fontsize=16, weight="bold", family=fs.FONT)
    ax.set_yticks([])
    ax.set_ylim(0, max(counts) * 1.7)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(0.06, 0.155, "No documented planning-layer failure across the trial series.",
              color=fs.MUTED, fontsize=16, style="italic", family=fs.FONT)

    fig.text(0.68, 0.72, "2 confirmed fix chains\n(recovery trial logged):", color=fs.INK, fontsize=18,
              weight="bold", family=fs.FONT, linespacing=1.5)
    fig.text(0.68, 0.60, "odom-reset guard\n(P3) -- recovery trial 6", color=fs.ACCEPTED, fontsize=16,
              family=fs.FONT, linespacing=1.4)
    fig.text(0.68, 0.46, "lift-fault threshold fix\n-- recovery trial 5", color=fs.ACCEPTED, fontsize=16,
              family=fs.FONT, linespacing=1.4)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "report_assets/FAILURE_REGISTER.csv", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-F failure register", [
        f"{len(rows)} real documented failure modes/limitations total, by layer: "
        + ", ".join(f"{layer}={len(by_layer[layer])}" for layer in LAYER_ORDER) + ".",
        "By kind: " + ", ".join(f"{k}={sum(1 for r in rows if r['kind'] == k)}"
                                  for k in ["defect", "limitation", "unexplained"]) + ".",
        "Selection criterion (from the CSV's own header): real, logged/sourced failures and measured "
        "limitations that halted a run, endangered hardware, produced a wrong/refused outcome, or were",
        "flagged as a citability risk in this project's own audit documents -- not every code change, "
        "and not successes.",
        "Full 17-row unit tally (one square per row, marker=fix_status) is the report/appendix figure.",
    ])
    return out_path, report


def render(variant="report", out_path=None):
    if variant == "report":
        return render_report(out_path=out_path)
    if variant == "slide":
        return render_slide(out_path=out_path)
    raise ValueError(f"unknown variant {variant!r}, expected 'report' or 'slide'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", choices=["report", "slide"], default="report")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(variant=args.variant, out_path=args.out)
    print(f"new_f ({args.variant}) written to {path}")
    print(report.summary())
