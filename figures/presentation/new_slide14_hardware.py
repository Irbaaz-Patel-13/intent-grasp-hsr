"""
new_slide14_hardware.py -- Slide 14: Real Robot / Hardware Execution.

Purpose: show execution failures were observable, diagnosed, and in some
cases recovered through a real engineering fix -- not a chronological trial
list. Two real, documented, confirmed-with-recovery-trial chains, read
directly from FAILURE_REGISTER.csv and cross-checked against trials.csv's
own recovery-trial verdict.

Scientific claim: unchanged from FAILURE_REGISTER.csv/trials.csv -- this
figure restructures already-verified real rows into a chain diagram, no new
measurement. Does NOT imply every failure was fixed: only the 2 rows whose
real fix_status is "confirmed_with_recovery_trial" are shown as chains;
trial_1_abort/trial_3_abort ("unexplained", fix_status=open) are explicitly
excluded, not silently folded in.
Required real data: report_assets/FAILURE_REGISTER.csv (incident_10_odom_reset,
  trial_4_lift_fault rows, real, unchanged); trials.csv (recovery-trial
  verdict, read live via new_hw_trial_history.load_trials()).

Run: python new_slide14_hardware.py
Output: report_assets/figures/slide14_hardware.png
"""
import argparse
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import figlayout as fl
import figstyle as fs
import new_hw_trial_history as fig_hw
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "report_assets", "FAILURE_REGISTER.csv")
CHAIN_IDS = ["incident_10_odom_reset", "trial_4_lift_fault"]


def load_chain_rows():
    with open(CSV_PATH) as f:
        lines = [l for l in f if not l.startswith("#")]
    rows = {r["id"]: r for r in csv.DictReader(lines)}
    return {cid: rows[cid] for cid in CHAIN_IDS}


# Hand-tightened, faithful short renderings of each real CSV row (full
# original description/source_ref/fix_artefact strings preserved verbatim
# in the speaker notes and in report_assets/FAILURE_REGISTER.csv itself --
# nothing here changes their meaning, only their length for box space).
SHORT_TEXT = {
    "incident_10_odom_reset": {
        "failure": "Silent odometry reset drove\nthe base toward the table",
        "diagnosis": "Stale place_run.ref file\n(lab_patches_0717.py)",
        "patch": "P3: odom-reset guard on\nstale/near-zero reference",
    },
    "trial_4_lift_fault": {
        "failure": "HELD_LIFT_FAULT: loop kept\nstepping past resistance",
        "diagnosis": "trials.csv trial 4;\nlab_patch_0727_lift.py:11-13",
        "patch": "Single-step-break threshold +\nhold_margin=0 option",
    },
}


def _step_box(ax, x, y, w, h, title, body, color, fontsize_body=16):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.01",
                                 transform=ax.transAxes, facecolor=fs.CALLOUT_BG, edgecolor=color, linewidth=2.0))
    ax.text(x + w / 2, y + h - 0.05, title, transform=ax.transAxes, ha="center", va="top", color=color,
            fontsize=16, weight="bold", family=fs.FONT, linespacing=1.2)
    ax.text(x + w / 2, y + h / 2 - 0.08, body, transform=ax.transAxes, ha="center", va="center", color=fs.INK,
            fontsize=fontsize_body, family=fs.FONT, linespacing=1.35)


def render(out_path=None):
    out_path = out_path or os.path.join("report_assets", "figures", "slide14_hardware.png")
    chains = load_chain_rows()
    trials = fig_hw.load_trials()
    by_id = {t["trial_id"]: t for t in trials if t["trial_id"] is not None}

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Real Failures, Diagnosed, and Recovered", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.905,
              "the other 6 real execution defects are patched-only, diagnosed-only, or open (see NEW-F)",
              **{**fs.BODY, "size": 16})
    fig.text(fs.MARGIN, 0.855, "2", color=fs.ACCEPTED, fontsize=48, weight="bold", family=fs.FONT)
    fig.text(0.075, 0.865, "confirmed recovery chains\n(out of 8 real execution defects)", color=fs.MUTED,
              fontsize=16, family=fs.FONT, linespacing=1.3, va="center")

    chain_specs = [
        ("incident_10_odom_reset", "ODOM-RESET GUARD", 0.46),
        ("trial_4_lift_fault", "LIFT-FAULT THRESHOLD FIX", 0.08),
    ]
    step_w, gap = 0.175, 0.018
    start_x = 0.03
    step_h = 0.30

    for cid, chain_title, y in chain_specs:
        row = chains[cid]
        short = SHORT_TEXT[cid]
        recovery_trial = int(row["recovery_trial"])
        outcome = by_id[recovery_trial]["verdict"]
        fig.text(start_x, y + step_h + 0.03, chain_title, color=fs.INK, fontsize=18, weight="bold",
                  family=fs.FONT)

        steps = [
            ("FAILURE", short["failure"], fs.REJECTED),
            ("DIAGNOSIS", short["diagnosis"], fs.CANDIDATE),
            ("PATCH", short["patch"], fs.REASONING),
            (f"RECOVERY\nTRIAL {recovery_trial}", "real logged\nre-attempt", fs.MUTED),
            ("CONFIRMED\nOUTCOME", outcome, fs.ACCEPTED),
        ]
        for i, (title, body, color) in enumerate(steps):
            x = start_x + i * (step_w + gap)
            ax = fig.add_axes([x, y, step_w, step_h])
            ax.axis("off")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            _step_box(ax, 0, 0, 1, 1, title, body, color, fontsize_body=16)
            if i < len(steps) - 1:
                fig.add_artist(FancyArrowPatch((x + step_w, y + step_h / 2), (x + step_w + gap, y + step_h / 2),
                                                transform=fig.transFigure, color=fs.MUTED, linewidth=1.8,
                                                arrowstyle="-|>", mutation_scale=14))

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "report_assets/FAILURE_REGISTER.csv + trials.csv",
                               **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("Slide 14 hardware", [
        "Only 2/17 real failure-register rows have fix_status=confirmed_with_recovery_trial -- these are",
        "the only 2 shown as chains. Not implying every documented failure was fixed (see NEW-F: 8",
        "execution + 7 perception + 2 reasoning failures/limitations total, most patched-only or open).",
        "trial_1_abort and trial_3_abort are 'unexplained' (fix_status=open) -- no diagnosed cause, not",
        "shown here, not silently presented as recovered.",
        "Recovery trial outcome (GRASP_OK) read live from trials.csv, not asserted from the register.",
        "This is real hardware evidence (Toyota HSR), not simulation -- see NEW-HW for the full trial",
        "1-12 history including the real trial-8 gap and the 0.4mm autonomous-cluster spread.",
    ])
    return out_path, report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(out_path=args.out)
    print(f"slide14 written to {path}")
    print(report.summary())
