"""
fig12_failure_analysis.py -- Figure 12: Failure Analysis / Engineering
Self-Correction.

Scientific question: what caused the real logged hardware failures, and did
they drive genuine engineering correction?
Scientific claim: specific, real hardware incidents drove specific,
verifiable code fixes -- genuine engineering self-correction, independently
spot-verified, not narrative dressing -- shown as two real, confirmed
FAILURE -> DIAGNOSIS -> CODE CHANGE -> RECOVERY chains. Trials 1 and 3's
root causes are NOT independently confirmed to map to any specific numbered
incident and are presented as visually separate, unconnected failures.
Supporting evidence: trials.csv (trials 1, 3, 4, 5, 6 -- all real logged
  rows); scripts/robot/lab_patch_0727_lift.py (real code
  comments, spot-verified: "22 Jul trial 4  contact -0.355  lift
  0.526->0.526  OVER-CURRENT, no lift"; "resistance appeared at -0.302
  ... never below -0.355"; patches the single-step-break threshold and
  hold_margin); scripts/robot/execute_place_grasp_raw.py
  (incident #10 guard comment, spot-verified). Trial 5's own real note
  ("trial 5, lift patch, ...") and real hold_margin=0.000 independently
  corroborate the 27-Jul lift-fault fix chain -- dated 2026-07-28, one day
  after the 27-Jul patch file -- making trial 5 a confirmed RECOVERY for
  trial 4's FAILURE, not merely an assumed one.
Required real data: all real verdict/contact_pos/z_rise_m/lift_reached/
  hold_margin/note values for trials 1, 3, 4, 5, 6 -- used directly.
Required diagrammatic elements: the card/chain layout is a reconstructed
  diagram (no execution photographs exist for any trial). Chain B's
  FAILURE node ("odometry reset event") is a documented incident type
  from the code's own guard comment, NOT tied to any specific numbered
  trial in trials.csv -- labeled as such rather than inventing a trial
  number. Neutral engineering framing: failure=red, diagnosis/code
  change=amber, recovery=green: color marks real verdict/role, not a
  dramatized aesthetic.

Run: python fig12_failure_analysis.py [--exp-dir DIR]
Output: generated_assets/fig12/fig12_failure_analysis.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

import figstyle as fs
import fig_data as fd


def _find(rows, note_substr):
    for r in rows:
        if note_substr in r["note"]:
            return r
    raise ValueError(f"no trial found with note containing {note_substr!r}")


def _chain_node(ax, x, w, y, h, role, title, lines, color):
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes, fill=False,
                            edgecolor=color, linewidth=1.8))
    ax.text(x + w / 2, y + h - 0.035, role, transform=ax.transAxes, ha="center", va="top",
            color=color, fontsize=9, weight="bold", family=fs.FONT)
    ax.text(x + w / 2, y + h - 0.085, title, transform=ax.transAxes, ha="center", va="top",
            color=fs.INK, fontsize=10.5, weight="bold", family=fs.FONT)
    ax.text(x + w / 2, y + h - 0.135, "\n".join(lines), transform=ax.transAxes, ha="center", va="top",
            color=fs.MUTED, fontsize=8.3, family=fs.FONT, linespacing=1.6)


def _chain_row(ax, y, h, header, nodes):
    """nodes: list of (role, title, lines, color) drawn left-to-right with
    connecting arrows -- one real, confirmed causal chain."""
    ax.text(0.0, y + h + 0.025, header, transform=ax.transAxes, ha="left", va="bottom",
            color=fs.INK, fontsize=11.5, weight="bold", family=fs.FONT)
    n = len(nodes)
    w, gap = 0.205, 0.045
    xs = [i * (w + gap) for i in range(n)]
    for x, (role, title, lines, color) in zip(xs, nodes):
        _chain_node(ax, x, w, y, h, role, title, lines, color)
    for i in range(n - 1):
        x0 = xs[i] + w
        x1 = xs[i + 1]
        ax.add_patch(FancyArrowPatch((x0 + 0.006, y + h / 2), (x1 - 0.006, y + h / 2),
                                      transform=ax.transAxes, color=fs.MUTED, linewidth=1.5,
                                      arrowstyle="-|>", mutation_scale=13))


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    rows = fd.load_trials()
    t1 = _find(rows, "trial 1,")
    t3 = _find(rows, "trial 3,")
    t4 = _find(rows, "trial 4,")
    t5 = _find(rows, "trial 5,")
    t6 = _find(rows, "trial 6,")
    out_path = out_path or os.path.join(fs.asset_dir("fig12"), "fig12_failure_analysis.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 12 -- Failure Analysis: Real Incidents, Real Fixes",
                 **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Two confirmed failure -> diagnosis -> code change -> recovery chains, real logged data",
              **fs.BODY)

    ax = fig.add_axes([0.05, 0.15, 0.91, 0.68])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _chain_row(ax, 0.70, 0.22, "CONFIRMED CHAIN A -- lift-fault (27-Jul patch, spot-verified)", [
        ("FAILURE", f"Trial 4 -- {t4['verdict']}", [
            f"contact={t4['contact_pos']}, lift {t4['lift_commanded']}->{t4['lift_reached']}",
            "(2026-07-25)"], fs.REJECTED),
        ("DIAGNOSIS", "Break threshold too late", [
            "code: resistance -0.302,",
            "steps to -0.355 before stop"], fs.CANDIDATE),
        ("CODE CHANGE", "lab_patch_0727_lift.py", [
            "earlier break + hold_margin=0",
            "option (2026-07-27)"], fs.CANDIDATE),
        ("RECOVERY", f"Trial 5 -- {t5['verdict']}", [
            f"hold_margin={t5['hold_margin']}, note:",
            "\"lift patch\" (2026-07-28)"], fs.ACCEPTED),
    ])

    _chain_row(ax, 0.40, 0.22, "CONFIRMED CHAIN B -- incident #10 (odometry guard, spot-verified)", [
        ("FAILURE", "Odometry reset event", [
            "documented incident type --",
            "not a specific numbered trial"], fs.REJECTED),
        ("DIAGNOSIS", "Stale reference frame", [
            "odom ~ (0,0,0) + stale ref",
            "between trials = incident #10"], fs.CANDIDATE),
        ("CODE CHANGE", "Incident #10 guard", [
            "execute_place_grasp_raw.py:",
            "abort on this precondition"], fs.CANDIDATE),
        ("RECOVERY", f"Trial 6 -- {t6['verdict']}", [
            "note: \"repeat, odom reset",
            "between trials (incident #10)\""], fs.ACCEPTED),
    ])

    # Unconfirmed failures -- visually separate, unconnected (no arrows),
    # muted color throughout (not red) so they never read as part of a
    # resolved chain.
    ax.plot([0.0, 1.0], [0.335, 0.335], transform=ax.transAxes, color=fs.FAINT, linewidth=0.8)
    ax.text(0.0, 0.30, "UNCONFIRMED -- real logged failures, root cause not independently linked to a "
            "specific fix in this audit", transform=ax.transAxes, ha="left", va="top",
            color=fs.MUTED, fontsize=10.5, weight="bold", family=fs.FONT)

    for x, trial, label in [(0.0, t1, "Trial 1"), (0.255, t3, "Trial 3")]:
        ax.add_patch(Rectangle((x, 0.04), 0.205, 0.21, transform=ax.transAxes, fill=False,
                                edgecolor=fs.FAINT, linewidth=1.4, linestyle="--"))
        ax.text(x + 0.1025, 0.225, f"{label} -- {trial['verdict']}", transform=ax.transAxes,
                ha="center", va="top", color=fs.MUTED, fontsize=10, weight="bold", family=fs.FONT)
        ax.text(x + 0.1025, 0.16, trial["note"], transform=ax.transAxes, ha="center", va="top",
                color=fs.MUTED, fontsize=8, family=fs.FONT, wrap=True)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Chain A: trial 5's own real note + hold_margin=0.000 corroborate the 27-Jul fix, dated one "
              "day after the patch. Chain B's FAILURE node is a documented incident type, not a specific",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "trial. Card/chain layout is a reconstructed diagram -- no execution photographs exist for any trial.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig12 written to {path}")
