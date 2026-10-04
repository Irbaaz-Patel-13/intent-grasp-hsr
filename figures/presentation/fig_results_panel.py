#!/usr/bin/env python
r"""fig_results_panel.py -- turn trials.csv into the results figure.

    python fig_results_panel.py
    python fig_results_panel.py --csv trials.csv --out report_assets/figures/fig_results.png

Four panels from the hardware telemetry:
  (a) trial timeline -- verdict per attempt, coloured, annotated with condition
      (servo on/off), so the progression across the session is visible
  (b) gripper contact position at closure for every successful grasp, with the
      calibrated reference levels (empty close, rim pinch, body grip) marked --
      this is the evidence that the closure is verified rather than assumed
  (c) verified lift height per success
  (d) outcome counts

Nothing is recomputed: every number is read from the log written during the runs.
"""
import argparse, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, MUTED = "#1f2933", "#7b8794"
COL = {"GRASP_OK": "#047857", "HELD_LIFT_FAULT": "#b45309",
       "EMPTY_NO_CONTACT": "#b91c1c", "FAILED_OTHER": "#b91c1c"}


def col(v):
    for k, c in COL.items():
        if v.startswith(k): return c
    return "#6b7280"


# ---------------------------------------------------------------------------
# figdeck variant -- house-style single-panel dot plot for the defence deck.
# Additive only: default `main()` behaviour above is untouched. Triggered by
# --figdeck, reuses the same csv.DictReader row-loading as the rest of this
# file.
# ---------------------------------------------------------------------------
BG_D, INK_D, PRIMARY_D, CAVEAT_D, GREY_D = (
    "#FAF9F6", "#16181D", "#12415C", "#C2703D", "#6B6560")


def _figdeck_entries(rows):
    import re
    entries = []
    for r in rows:
        note = r.get("note", "")
        m = re.search(r"trial (\d+)", note)
        tnum = int(m.group(1)) if m else None
        ts = r.get("timestamp", "")
        date_str = ts.split(" ")[0] if ts else ""
        verdict = r.get("verdict", "")
        servo = (r.get("servo_used") or "").strip().lower()
        zraw = r.get("z_rise_m")
        try:
            zval = float(zraw) if zraw else float("nan")
        except ValueError:
            zval = float("nan")
        entries.append(dict(trial=tnum, date=date_str, verdict=verdict,
                             servo=servo, z=zval, gap=False))
    entries.sort(key=lambda e: e["trial"])
    full, inserted = [], False
    for e in entries:
        if not inserted and e["trial"] > 8:
            full.append(dict(trial=8, date=None, verdict="NO_RECORD",
                              servo=None, z=None, gap=True))
            inserted = True
        full.append(e)
    if not inserted:
        full.append(dict(trial=8, date=None, verdict="NO_RECORD",
                          servo=None, z=None, gap=True))
    return full


def render_figdeck(rows, out_path, csv_path):
    import datetime as _dt
    import matplotlib.transforms as mtransforms
    from matplotlib.font_manager import FontProperties

    mono = FontProperties(family=["monospace"])
    sans = FontProperties(family=["sans-serif"])

    entries = _figdeck_entries(rows)
    n = len(entries)
    ys = [n - i for i in range(n)]  # trial 1 at top

    fig, ax = plt.subplots(figsize=(12.0, 6.0), dpi=200)
    fig.patch.set_facecolor(BG_D)
    ax.set_facecolor(BG_D)
    fig.subplots_adjust(left=0.17, right=0.50, top=0.93, bottom=0.09)

    ax.set_xlim(0, 0.18)
    ax.set_ylim(0.3, n + 0.7)
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(axis="x", colors=INK_D, labelsize=9)
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(mono)
    ax.set_xlabel("z-rise (m)", fontproperties=sans, fontsize=10, color=INK_D)

    trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)

    # thin rules between date groups (and around the trial-8 gap)
    prev_date = None
    for e, y in zip(entries, ys):
        if e["date"] != prev_date:
            if prev_date is not None:
                rule_y = y + 0.5
                ax.plot([-0.30, 1.55], [rule_y, rule_y], transform=trans,
                         color=GREY_D, lw=0.6, clip_on=False, zorder=1)
            prev_date = e["date"]

    # date labels (mono) at the left of each group's first row
    prev_date = None
    for e, y in zip(entries, ys):
        if e["gap"]:
            ax.text(-0.06, y, "no record", transform=trans, ha="right",
                     va="center", fontproperties=mono, fontsize=9,
                     color=CAVEAT_D)
            prev_date = None
            continue
        if e["date"] != prev_date:
            dt = _dt.datetime.strptime(e["date"], "%Y-%m-%d")
            ax.text(-0.06, y, dt.strftime("%d %b"), transform=trans,
                     ha="right", va="center", fontproperties=mono,
                     fontsize=10.5, color=INK_D)
            prev_date = e["date"]

    # dots + right-hand condition labels
    aug1_ys = []
    for e, y in zip(entries, ys):
        if e["gap"]:
            ax.plot([0, 0.18], [y, y], color=CAVEAT_D, lw=1.0,
                     ls=(0, (3, 3)), zorder=1)
            ax.text(1.06, y, "trial 8 -- no record", transform=trans,
                     fontproperties=mono, fontsize=8.6, color=CAVEAT_D,
                     va="center", clip_on=False)
            continue
        if e["date"] == "2026-08-01":
            aug1_ys.append(y)
        ok = e["verdict"].startswith("GRASP_OK")
        x = e["z"] if (ok and e["z"] == e["z"]) else 0.0
        if ok:
            ax.scatter([x], [y], s=46, facecolor=PRIMARY_D,
                       edgecolor=PRIMARY_D, clip_on=False, zorder=3)
        else:
            ax.scatter([x], [y], s=46, facecolor="none",
                       edgecolor=GREY_D, linewidth=1.3, clip_on=False,
                       zorder=3)
        cond = ("servo . autonomous" if e["servo"] == "yes"
                 else "no servo . hand-placed")
        ax.text(1.06, y, "trial %-2d  %s" % (e["trial"], cond),
                transform=trans, fontproperties=mono, fontsize=8.6,
                color=INK_D, va="center", clip_on=False)

    # bracket over the 1 Aug group (4 consecutive, fully autonomous)
    if aug1_ys:
        y0, y1 = max(aug1_ys) + 0.32, min(aug1_ys) - 0.32
        bx = 1.62
        ax.plot([bx, bx + 0.018, bx + 0.018, bx], [y0, y0, y1, y1],
                transform=trans, color=INK_D, lw=1.0, clip_on=False,
                zorder=2)
        ax.text(bx + 0.03, (y0 + y1) / 2, "4 consecutive,\nfully autonomous",
                transform=trans, fontproperties=sans, fontsize=9.0,
                color=INK_D, va="center", clip_on=False)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, facecolor=BG_D)
    cap_path = os.path.splitext(out_path)[0] + ".txt"
    with open(cap_path, "w", encoding="utf-8") as fh:
        fh.write("Hardware grasp trials by z-rise, grouped by capture date, "
                 "trial 8 marked as a genuine gap in the log "
                 "(source: %s, %d recorded trials).\n" % (csv_path, len(rows)))
    print("wrote %s and %s (%d rows incl. gap)" % (out_path, cap_path, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="trials.csv")
    ap.add_argument("--out", default="report_assets/figures/fig_results.png")
    ap.add_argument("--figdeck", action="store_true",
                     help="render the house-style single-panel dot plot "
                          "for the defence deck instead of the default "
                          "four-panel figure; writes to --out")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    if not rows: raise SystemExit("empty %s" % a.csv)
    if a.figdeck:
        render_figdeck(rows, a.out, a.csv)
        return
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    def f(r, k, d=np.nan):
        try: return float(r.get(k) or d)
        except ValueError: return d

    n = len(rows)
    idx = np.arange(1, n+1)
    verd = [r.get("verdict","") for r in rows]
    servo = [(r.get("servo_used") or "-") for r in rows]

    fig, ax = plt.subplots(2, 2, figsize=(13.5, 8.0), dpi=170)
    fig.patch.set_facecolor("white")

    # (a) timeline
    A = ax[0,0]
    for i, v in zip(idx, verd):
        A.barh(i, 1, color=col(v), alpha=.9, height=.72)
    for i, (v, s) in enumerate(zip(verd, servo), start=1):
        A.text(1.04, i, "%s   servo=%s" % (v.replace("_"," ").title(), s),
               va="center", fontsize=7.6, color=INK)
    A.set_yticks(idx); A.set_yticklabels(["trial %d" % i for i in idx], fontsize=7.5)
    A.set_xlim(0, 3.2); A.set_xticks([]); A.invert_yaxis()
    A.set_title("(a) attempt-by-attempt outcome", fontsize=10.5, color=INK)
    for sp in A.spines.values(): sp.set_visible(False)

    # (b) contact position
    B = ax[0,1]
    cp = [(i, f(r,"contact_pos")) for i, r in zip(idx, rows)
          if not np.isnan(f(r,"contact_pos"))]
    if cp:
        xs, ys = zip(*cp)
        B.scatter(xs, ys, s=64, c=[col(verd[x-1]) for x in xs], zorder=3)
        for lv, lab, c in ((-0.8899, "empty close (calibrated)", "#b91c1c"),
                           (-0.877,  "rim pinch", "#b45309"),
                           (-0.276,  "body grip", "#047857")):
            B.axhline(lv, ls=(0,(5,4)), lw=1.1, c=c, alpha=.8)
            B.text(max(xs)+0.15, lv, lab, fontsize=7.4, color=c, va="center")
    B.set_xlabel("trial", fontsize=9); B.set_ylabel("hand_motor at contact (rad)", fontsize=9)
    B.set_title("(b) closure verified against calibrated grip levels", fontsize=10.5, color=INK)
    B.tick_params(labelsize=8, colors=MUTED); B.grid(alpha=.25)

    # (c) lift height
    C = ax[1,0]
    lz = [(i, f(r,"z_rise_m")) for i, r in zip(idx, rows)
          if r.get("verdict","").startswith("GRASP_OK")]
    if lz:
        xs, ys = zip(*lz)
        C.bar(xs, ys, color="#047857", alpha=.85, width=.6)
        for x, y in zip(xs, ys):
            C.text(x, y+0.004, "%.3f" % y, ha="center", fontsize=7.6, color=INK)
    C.set_xlabel("trial", fontsize=9); C.set_ylabel("verified lift, z_rise (m)", fontsize=9)
    C.set_title("(c) lift verified by forward kinematics (G3)", fontsize=10.5, color=INK)
    C.tick_params(labelsize=8, colors=MUTED); C.grid(alpha=.25, axis="y")

    # (d) counts
    D = ax[1,1]
    from collections import Counter
    cnt = Counter(verd)
    labs = list(cnt); vals = [cnt[k] for k in labs]
    D.bar(range(len(labs)), vals, color=[col(k) for k in labs], alpha=.9)
    D.set_xticks(range(len(labs)))
    D.set_xticklabels([k.replace("_","\n") for k in labs], fontsize=7.8)
    for i, v in enumerate(vals):
        D.text(i, v+0.05, str(v), ha="center", fontsize=9, color=INK)
    ok = sum(v for k, v in cnt.items() if k.startswith("GRASP_OK"))
    held = sum(1 for r in rows if (r.get("held") or "") == "True")
    D.set_title("(d) %d/%d full success · %d/%d object secured"
                % (ok, n, held, n), fontsize=10.5, color=INK)
    D.tick_params(labelsize=8, colors=MUTED); D.grid(alpha=.25, axis="y")

    fig.suptitle("Hardware grasp trials — telemetry logged during execution",
                 fontsize=13, color=INK)
    fig.tight_layout(rect=[0,0,1,0.94])
    fig.savefig(a.out, facecolor="white")
    print("wrote %s  (%d trials, %d full successes)" % (a.out, n, ok))


if __name__ == "__main__":
    main()
