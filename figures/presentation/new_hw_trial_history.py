"""
new_hw_trial_history.py -- Hardware Trial History (real trials.csv, trial 1-12,
gap at trial 8 preserved).

Scientific claim: the real logged hardware trial series ran trials 1-7 and
9-12 (trial 8 has no record in trials.csv -- a real gap, not renumbered or
interpolated). The 4 fully-autonomous trials (9-12) are tightly repeatable:
real z_rise_m values 0.1420/0.1418/0.1416/0.1418, spread 0.4mm, computed
directly from the file, not typed from memory.
Supporting evidence: trials.csv (12 real rows + 1 unlabeled "live demo" row,
  13 lines total incl. header).
Required real data: trial_id (parsed from each row's own note field), verdict,
  z_rise_m -- used directly. Rows without a z_rise (ABORT_ rows) are shown as
  such, not defaulted to 0 and hidden.
Required diagrammatic elements: the trial-8 gap marker and the trials-9-12
  bracket are diagrammatic scaffolding over real, unmodified per-row data.

Run: python new_hw_trial_history.py
Output: report_assets/figures/NEW-HW_trial_history.png
"""
import csv
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "trials.csv")
VERDICT_COLOR = {"GRASP_OK": fs.ACCEPTED, "HELD_LIFT_FAULT": fs.CANDIDATE, "ABORT_": fs.REJECTED}
AUTONOMOUS_TRIALS = [9, 10, 11, 12]  # note field: "trial N, ...autonomous..."


def load_trials():
    rows = list(csv.DictReader(open(CSV_PATH)))
    out = []
    for r in rows:
        m = re.search(r"trial (\d+)", r["note"])
        trial_id = int(m.group(1)) if m else None
        out.append({
            "trial_id": trial_id, "verdict": r["verdict"],
            "z_rise_m": float(r["z_rise_m"]) if r["z_rise_m"] else None,
            "note": r["note"], "timestamp": r["timestamp"],
        })
    return out


def render(out_path=None):
    out_path = out_path or os.path.join("report_assets", "figures", "NEW-HW_trial_history.png")
    trials = load_trials()
    numbered = [t for t in trials if t["trial_id"] is not None]
    by_id = {t["trial_id"]: t for t in numbered}
    max_trial = max(by_id.keys())

    auto = [by_id[i]["z_rise_m"] for i in AUTONOMOUS_TRIALS if i in by_id and by_id[i]["z_rise_m"] is not None]
    auto_min, auto_max = min(auto), max(auto)
    auto_spread_mm = round((auto_max - auto_min) * 1000, 1)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Hardware Trial History -- Real Log, Trial 8 Gap Preserved", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              f"{len(numbered)} real logged trials (trials.csv) -- trial 8 has no record, not renumbered",
              **fs.BODY)

    ax = fig.add_axes([0.07, 0.28, 0.86, 0.50])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0.3, max_trial + 0.7)
    ax.set_ylim(0, 0.19)
    ax.set_xticks(range(1, max_trial + 1))
    ax.set_ylabel("z_rise (m)", color=fs.MUTED, fontsize=16, family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=14)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)

    for i in range(1, max_trial + 1):
        t = by_id.get(i)
        if t is None:
            ax.axvspan(i - 0.35, i + 0.35, color=fs.FAINT, alpha=0.25, zorder=0)
            ax.text(i, 0.10, "NO\nRECORD", ha="center", va="center", color=fs.MUTED, fontsize=13,
                    weight="bold", family=fs.FONT, linespacing=1.3)
            continue
        color = VERDICT_COLOR.get(t["verdict"], fs.MUTED)
        if t["z_rise_m"] is not None:
            ax.bar(i, t["z_rise_m"], width=0.55, color=color, zorder=3)
            ax.text(i, t["z_rise_m"] + 0.004, f"{t['z_rise_m']:.3f}", ha="center", va="bottom", color=color,
                    fontsize=11, weight="bold", family=fs.FONT)
        else:
            ax.scatter([i], [0.006], marker="x", s=140, color=color, linewidths=3, zorder=3)

    ax.annotate("", xy=(9, 0.175), xytext=(12, 0.175),
                arrowprops=dict(arrowstyle="-", color=fs.ACCEPTED, linewidth=2.0))
    ax.plot([9, 9], [0.170, 0.175], color=fs.ACCEPTED, linewidth=2.0)
    ax.plot([12, 12], [0.170, 0.175], color=fs.ACCEPTED, linewidth=2.0)
    ax.text(10.5, 0.180, "fully autonomous, all GRASP_OK", ha="center", va="bottom", color=fs.ACCEPTED,
            fontsize=13, weight="bold", family=fs.FONT)

    ax_hero = fig.add_axes([0.07, 0.10, 0.40, 0.14])
    ax_hero.axis("off")
    ax_hero.text(0.0, 0.5, f"{auto_spread_mm}mm", color=fs.ACCEPTED, fontsize=52, weight="bold", va="center",
                family=fs.FONT)
    ax_hero.text(0.55, 0.65, "z-rise spread across", color=fs.INK, fontsize=16, family=fs.FONT, va="center")
    ax_hero.text(0.55, 0.35, "trials 9-12 (autonomous)", color=fs.INK, fontsize=16, family=fs.FONT, va="center")

    ax_legend = fig.add_axes([0.55, 0.10, 0.38, 0.14])
    ax_legend.axis("off")
    ax_legend.set_xlim(0, 1)
    ax_legend.set_ylim(0, 1)
    for i, (verdict, color) in enumerate(VERDICT_COLOR.items()):
        y = 0.85 - i * 0.38
        ax_legend.add_patch(Rectangle((0.0, y - 0.06), 0.05, 0.12, facecolor=color, transform=ax_legend.transAxes))
        ax_legend.text(0.08, y, verdict.rstrip("_"), transform=ax_legend.transAxes, ha="left", va="center",
                        color=color, fontsize=14, weight="bold", family=fs.FONT)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Bars = real z_rise_m per trial; x marker = ABORT_ (no lift, no z_rise recorded). Trial 8 gap is "
              "real (trials.csv has no such row) -- not interpolated or renumbered.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"Source: trials.csv ({len(numbered)} real numbered rows). Spread computed as "
              f"max({auto_max:.4f})-min({auto_min:.4f}) over trials 9-12, not typed from memory.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    fig.savefig(out_path.replace(".png", ".pdf"), facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


if __name__ == "__main__":
    path, report = render()
    print(f"NEW-HW written to {path}")
    print(report.summary())
