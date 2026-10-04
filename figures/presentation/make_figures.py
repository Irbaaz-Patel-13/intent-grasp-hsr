"""
make_figures.py - build the AffordGrasp dissertation figures from project data.

Usage (from the repository root):

    python figures/presentation/make_figures.py --root workspace --all
    python figures/presentation/make_figures.py --root workspace --figure envelope
    python figures/presentation/make_figures.py --root workspace --figure overlay \\
           --rgb capture_0801.png --object-mask obj.npy --part-mask part.npy

Figures:
    envelope    5.2  sensor resolution envelope, width against recovered pixels
    trials      7.3  trial outcome timeline and lift verification
    corrections 7.7  corrections register, claim against re-measurement
    constraint  3.5  constraint field to closure parameter routing
    baseplace   7.1  base placement before and after, top-down reach geometry
    overlay     5.1  mask coverage on a real capture (needs --rgb and masks)

Every builder writes PDF (place this in Word) and PNG at 400 dpi.
Nothing is invented: if a required measurement is missing the builder says so
and, where useful, writes a template for you to complete.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.path import Path as MPath

import figkit as fk
from figkit import (BLUE, FAINT, GREEN, INK, MUTED, ORANGE, PURPLE, RED, RULE,
                    SKY, DataProblem)

WORKING_DISTANCE_M = 0.92
ARROW = fk.arrow()
OK = fk.OKABE_ITO
GATE_POINTS = 60
GATE_WIDTH_MM = 6.0


# ==========================================================================
# 5.2  SENSOR RESOLUTION ENVELOPE
# ==========================================================================

def fig_envelope(root, out, args):
    """
    Physical width against recovered pixels, with the component crop at each
    point instead of a text label.

    The sensor argument is geometric, but a reader who has not seen the
    captures has no idea what 2.5 px looks like. Placing the actual crop at
    each measurement makes the floor visible: the recovered components are
    still recognisable, the refused one is a smear.
    """
    cam = fk.load_camera(root)
    comps = fk.load_components(root, Path(args.components) if args.components
                               else None)
    mmpp = cam.mm_per_px(WORKING_DISTANCE_M)
    print(f"    {cam.name}: {mmpp:.3f} mm/px at {WORKING_DISTANCE_M:.2f} m")
    bank, by_key = _capture_bank(root, args)

    widths = np.array([c.width_mm for c in comps], float)
    pixels = np.array([c.pixels for c in comps], float)
    wmax = float(np.nanmax(widths)) if np.isfinite(widths).any() else 20.0

    fig = fk.new_figure(fk.COL_W, 4.90)
    ax = fig.add_subplot(111)
    ax.set_xlabel("physical component width (mm)")
    ax.set_ylabel("recovered width (pixels)")
    ax.set_xlim(0, wmax * 1.32)
    ax.set_ylim(0, float(np.nanmax(pixels)) * 2.25)
    fk.declutter(ax)

    floor_lo, floor_hi = 3.5, 3.8
    ax.axhspan(0, floor_lo, color=FAINT, zorder=0)
    ax.axhspan(floor_lo, floor_hi, color=ORANGE, alpha=0.20, zorder=1)
    for yv in (floor_lo, floor_hi):
        ax.axhline(yv, color=ORANGE, lw=0.6, ls=(0, (4, 3)), zorder=2)
    ax.axvline(GATE_WIDTH_MM, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    x = np.linspace(0, wmax * 1.30, 200)
    ax.plot(x, x / mmpp, color=INK, lw=1.2, zorder=3)

    ax.text(wmax * 1.30, floor_hi + 0.30,
            f"evidence floor {floor_lo}\u2013{floor_hi} px",
            fontsize=fk.FS_SMALL, color=ORANGE, ha="right", va="bottom")
    ax.text(GATE_WIDTH_MM + 0.35, 0.35,
            f"evidence gate {GATE_WIDTH_MM:.0f} mm", fontsize=fk.FS_SMALL,
            color=MUTED, ha="left", va="bottom")

    # markers first, so the crops can lead back to them
    for c in comps:
        ok = c.recovered and c.pixels >= floor_lo
        cit = getattr(c, "citable", True)
        ax.scatter([c.width_mm], [c.pixels], s=46, zorder=6,
                   marker="o" if ok else "X",
                   facecolor=(GREEN if ok else RED) if cit else "white",
                   edgecolor=(GREEN if ok else RED) if not cit else "white",
                   linewidth=1.4 if not cit else 0.9)

    # crops, alternating above and below the trend so leaders do not cross
    assets = bundle_for(load_assets(root), "5.2")
    crops = {}
    for cid, rec in assets.items():
        img = _asset_array(root, rec, "overlay")
        if img is None:
            continue
        if img.ndim == 3 and img.shape[2] == 4:
            img = img[..., :3]
        if img.dtype != np.uint8:
            img = (255 * np.clip(img, 0, 1)).astype(np.uint8)
        before = img.shape[0]
        img = fk.trim_caption_band(img)
        if img.shape[0] != before:
            print(f"    trimmed a {before - img.shape[0]} px debug caption "
                  f"band from {Path(rec['overlay']['path']).name}")
        stem = Path(rec["overlay"]["path"]).stem.lower()
        crops[stem] = (img, rec["overlay"]["citable"])
    # crops sit on a shelf across the top with a leader to each measurement,
    # which is the only arrangement that cannot collide when the points
    # cluster along the trend line
    placed = 0
    order = sorted(comps, key=lambda c: c.width_mm)
    ymax = ax.get_ylim()[1]
    xs_shelf = np.linspace(wmax * 0.15, wmax * 1.17, len(order))
    # two shelf heights, alternating, so neighbouring captions cannot collide
    shelf_ys = [ymax * (0.90 if i % 2 == 0 else 0.70)
                for i in range(len(order))]
    for xshelf, shelf_y, c in zip(xs_shelf, shelf_ys, order):
        short = fk.display_soft(fk.split_qualifier(c.name)[0])
        ok = c.recovered and c.pixels >= floor_lo
        crop = None
        want = re.sub(r"[^a-z0-9]+", "_",
                      f"{c.object} {short}".lower()).strip("_")
        for stem, (img, cit) in crops.items():
            if stem in want or want in stem or stem.split("_")[0] in want:
                crop = img
                break
        cap = None if crop is not None else _pick_capture(by_key,
                                                          short.split()[0])
        lab = (f"{short}\n{c.width_mm:.0f} mm, {c.pixels:.1f} px"
               + ("" if getattr(c, "citable", True) else "\nnot citable"))
        colour = GREEN if ok else RED
        if crop is None and cap is not None:
            bb = fk.crop_to(cap["part"] if cap["part"].any() else cap["obj"],
                            pad_frac=0.55, shape=cap["rgb"].shape[:2])
            x0, y0, x1, y1 = bb
            crop = cap["rgb"][y0:y1 + 1, x0:x1 + 1]
        if crop is not None:
            fk.image_inset(ax, (xshelf, shelf_y), crop, w_in=0.82,
                           label=lab, label_colour=colour, anchor="center",
                           leader=True, leader_to=(c.width_mm, c.pixels),
                           frame=INK if getattr(c, "citable", True) else RED)
            placed += 1
        else:
            fk.annotate_point(ax, (c.width_mm, c.pixels), lab, dx=-12, dy=10,
                              ha="right", va="bottom", colour=colour)
    print(f"    {placed} of {len(comps)} components illustrated with a crop")

    ax.legend(handles=[
        Line2D([], [], color=INK, lw=1.2,
               label=f"predicted, {mmpp:.2f} mm/px at {WORKING_DISTANCE_M:.2f} m"),
        Line2D([], [], marker="o", ls="none", mfc=GREEN, mec="white",
               label="recovered"),
        Line2D([], [], marker="X", ls="none", mfc=RED, mec="white",
               label="refused at the gate"),
    ], loc="lower right", ncol=1)
    return fk.save(fig, out, "fig_5_3_evidence_floor")

# ==========================================================================
# 7.3  TRIAL TIMELINE AND LIFT VERIFICATION
# ==========================================================================

def fig_trials(root: Path, out: Path, args):
    """
    Two panels sharing one trial axis:
      (a) outcome per trial, with trial 8 shown as an explicit empty slot
      (b) verified z-rise, autonomous runs distinguished from hand-placed
    """
    rows = fk.load_trials(root, args.bundle,
                          explicit=Path(args.trials_csv) if args.trials_csv
                          else None)

    if args.trial_ids:
        override = [int(x) for x in args.trial_ids.split(",")]
        if len(override) != len(rows):
            raise DataProblem(
                f"--trial-ids gives {len(override)} ids for {len(rows)} rows")
        for r, i in zip(rows, override):
            r["_id"] = i
        print(f"    trial ids overridden: {override}")

    c_out = fk.pick_column(rows, "outcome", "verdict", "result", "status",
                           label="outcome")
    c_z = fk.pick_column(rows, "z_rise_m", "z_rise", "zrise", "rise",
                         required=False)
    c_mode = fk.pick_column(rows, "mode", "autonomy", "placement",
                            "servo_used", "note", required=False)
    c_date = fk.pick_column(rows, "date", "day", required=False)

    ids = [r["_id"] for r in rows]
    span = list(range(min(ids), max(ids) + 1))          # includes the gap

    fig = fk.new_figure(fk.COL_W, 4.3)
    gs = fig.add_gridspec(2, 1, height_ratios=[0.52, 1.0], hspace=0.10)
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)

    by_id = {r["_id"]: r for r in rows}

    # ---- panel (a): outcomes -------------------------------------------
    seen = []
    for t in span:
        if t not in by_id:
            ax0.add_patch(mpatches.Rectangle(
                (t - 0.36, 0.26), 0.72, 0.48,
                facecolor="white", edgecolor=MUTED, linewidth=0.7,
                linestyle=(0, (2, 2)), zorder=3))
            ax0.text(t, 0.5, "no\nrecord", ha="center", va="center",
                     fontsize=fk.FS_SMALL, color=MUTED, zorder=4,
                     linespacing=1.15)
            continue
        oc = str(by_id[t][c_out]).strip().upper().replace(" ", "_")
        col = fk.OUTCOME_COLOURS.get(oc, PURPLE)
        seen.append(oc)
        ax0.add_patch(mpatches.Rectangle(
            (t - 0.36, 0.26), 0.72, 0.48,
            facecolor=col, edgecolor="white", linewidth=0.8, zorder=3))

    ax0.set_ylim(0, 1)
    ax0.set_yticks([])
    ax0.set_ylabel("outcome")
    for s in ("left", "bottom"):
        ax0.spines[s].set_visible(False)
    plt.setp(ax0.get_xticklabels(), visible=False)
    ax0.tick_params(axis="x", length=0)

    order = ["GRASP_OK", "ABORT", "HELD_LIFT_FAULT"]
    counts = {o: seen.count(o) for o in order}
    handles = [mpatches.Patch(facecolor=fk.OUTCOME_COLOURS[o], edgecolor="white",
                              label=f"{o.replace('_',' ').lower()} ({counts[o]})")
               for o in order if counts[o]]
    handles.append(mpatches.Patch(facecolor="white", edgecolor=MUTED,
                                  linestyle=(0, (2, 2)),
                                  label="trial 8, no record"))
    ax0.legend(handles=handles, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, 1.02))

    # ---- panel (b): verified lift --------------------------------------
    if c_z is None:
        ax1.text(0.5, 0.5, "no z-rise column found in trials.csv",
                 transform=ax1.transAxes, ha="center", va="center",
                 fontsize=fk.FS_ANNOT, color=MUTED)
        ax1.set_yticks([])
    else:
        auto_x, auto_y, hand_x, hand_y = [], [], [], []
        for t in span:
            if t not in by_id:
                continue
            z = fk.to_float(by_id[t][c_z])
            if not np.isfinite(z):
                continue
            is_auto = True
            if c_mode:
                is_auto = "auto" in str(by_id[t][c_mode]).lower()
            (auto_x if is_auto else hand_x).append(t)
            (auto_y if is_auto else hand_y).append(z)

        if auto_y:
            ax1.scatter(auto_x, auto_y, s=42, marker="o", facecolor=BLUE,
                        edgecolor="white", linewidth=0.8, zorder=5,
                        label="fully autonomous")
            lo, hi = min(auto_y), max(auto_y)
            ax1.axhspan(lo, hi, color=BLUE, alpha=0.12, zorder=1)
            ax1.annotate(
                f"spread {1000*(hi-lo):.1f} mm",
                xy=(float(np.mean(auto_x)), hi), xytext=(0, 9),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=fk.FS_SMALL, color=BLUE)
        if hand_y:
            ax1.scatter(hand_x, hand_y, s=42, marker="s", facecolor=SKY,
                        edgecolor="white", linewidth=0.8, zorder=5,
                        label="hand-placed")
            lo, hi = min(hand_y), max(hand_y)
            ax1.axhspan(lo, hi, color=SKY, alpha=0.12, zorder=1)

        ax1.set_ylabel("verified z-rise (m)")
        ax1.legend(loc="upper right", ncol=2)
        ymin, ymax = ax1.get_ylim()
        ax1.set_ylim(ymin - (ymax - ymin) * 0.06,
                     ymax + (ymax - ymin) * 0.22)
        fk.declutter(ax1)

    ax1.set_xlabel("trial")
    ax1.set_xticks(span)
    ax1.set_xlim(min(span) - 0.7, max(span) + 0.7)
    if c_date:
        print("    dates present; not drawn, the trial axis is the ordering")
    return fk.save(fig, out, "table_7_1_trial_record")


# ==========================================================================
# 7.7  CORRECTIONS REGISTER
# ==========================================================================

def fig_corrections(root: Path, out: Path, args):
    """
    Claim as reported, what re-measurement found, what changed.

    Rendered as a figure rather than a Word table so the row heights can be
    computed from the wrapped text, which is what stops cells colliding.
    """
    rows = fk.load_table(root, "figure_data/corrections.csv",
                         "corrections.csv",
                         "report_assets/corrections.csv",
                         f"{args.bundle}/corrections.csv",
                         label="corrections register")
    if rows is None:
        tpl = root / "corrections.csv"
        tpl.write_text(
            "claim_as_reported,re_measured_finding,what_changed\n"
            ",,\n" * 5, encoding="utf-8")
        raise DataProblem(
            f"no corrections register found. Template written to {tpl}; "
            f"fill in the five documented corrections and re-run.")

    c1 = fk.pick_column(rows, "claim_as_reported", "claim", "as_reported",
                        label="claim")
    c2 = fk.pick_column(rows, "re_measured_finding", "re_measured", "finding",
                        "corrected", label="finding")
    c3 = fk.pick_column(rows, "what_changed", "effect", "consequence",
                        required=False)

    cols = [("Claim as reported", c1, 30),
            ("What re-measurement found", c2, 30)]
    if c3:
        cols.append(("What it changed", c3, 26))

    # Wrap first, then size the figure to the content. Never the other way.
    cells = []
    for r in rows:
        cells.append([fk.wrap(r[key], w) for _, key, w in cols])
    line_h = 0.155                                    # inches per text line
    heights = [max(c.count("\n") + 1 for c in row) * line_h + 0.14
               for row in cells]
    head_h = 0.30
    fig_h = head_h + sum(heights) + 0.30

    fig = fk.new_figure(fk.COL_W, fig_h)
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    widths = np.array([w for _, _, w in cols], dtype=float)
    widths = widths / widths.sum()
    xs = np.concatenate([[0.0], np.cumsum(widths)])

    y = 1.0
    ax.add_patch(mpatches.Rectangle((0, y - head_h / fig_h), 1, head_h / fig_h,
                                    facecolor=FAINT, edgecolor="none"))
    for i, (title, _, _) in enumerate(cols):
        ax.text(xs[i] + 0.008, y - (head_h / fig_h) / 2, title,
                va="center", ha="left", fontsize=fk.FS_LABEL,
                fontweight="bold", color=INK)
    ax.plot([0, 1], [y - head_h / fig_h] * 2, color=INK, lw=0.8)
    y -= head_h / fig_h

    for row, h in zip(cells, heights):
        hh = h / fig_h
        for i, cell in enumerate(row):
            ax.text(xs[i] + 0.008, y - hh / 2, cell, va="center", ha="left",
                    fontsize=fk.FS_ANNOT, color=INK, linespacing=1.25)
        y -= hh
        ax.plot([0, 1], [y, y], color=RULE, lw=0.5)
    return fk.save(fig, out, "table_7_4_corrections_register")


# ==========================================================================
# 3.5  CONSTRAINT FIELD -> CLOSURE PARAMETER ROUTING
# ==========================================================================

# Falls back to the mapping already stated in Table 3.2 if no file is present.
DEFAULT_ROUTING = [
    ("stability_priority", ["force level", "close depth fraction",
                            "cage clearance"]),
    ("post_grasp_motion",  ["force level", "close depth fraction",
                            "lift height", "controlled-tilt flag",
                            "retreat"]),
    ("thermal_or_hygiene", ["minimal-contact flag"]),
    ("keep_clear",         ["carried in policy result"]),
    ("target_part",        ["consumed upstream"]),
]


def fig_constraint(root, out, args):
    """
    What reaches gripper closure, and from where.

    The routing table mixes three kinds of left-hand item: fields the VLM
    actually emits, quantities perception measures, and values the policy
    derives. Drawing them as one undifferentiated column hid the point, and
    the explanatory asides stored in the same cell overflowed every box. Both
    are fixed here: asides become subtext, and the left column is banded by
    origin.
    """
    rows = fk.load_table(root, "figure_data/constraint_map.csv",
                         "constraint_map.csv", label="constraint routing")
    if rows:
        c_f = fk.pick_column(rows, "field", "constraint", label="field")
        c_p = fk.pick_column(rows, "closure_parameter", "parameter",
                             label="parameter")
        routing = []
        for r in rows:
            routing.append((r[c_f], r[c_p]))
    else:
        print("    using the mapping stated in Table 3.2")
        routing = [(f, p) for f, ps in DEFAULT_ROUTING for p in ps]

    VLM_FIELDS = {"stability_priority", "post_grasp_motion",
                  "thermal_or_hygiene", "keep_clear", "target_part",
                  "align_confident"}

    lefts, rights, edges = [], [], []
    for f, p in routing:
        fn, fq = fk.split_qualifier(f)
        pn, pq = fk.split_qualifier(p)
        if (fn, fq) not in lefts: lefts.append((fn, fq))
        if (pn, pq) not in rights: rights.append((pn, pq))
        edges.append(((fn, fq), (pn, pq)))

    # band the left column: emitted by the model, or supplied to it
    vlm = [l for l in lefts if l[0] in VLM_FIELDS]
    other = [l for l in lefts if l[0] not in VLM_FIELDS]
    lefts = vlm + other
    print(f"    {len(vlm)} VLM constraint fields, {len(other)} perception or "
          f"derived inputs, {len(rights)} closure parameters")

    n = max(len(lefts), len(rights))
    row_h = 0.052
    fig = fk.new_figure(fk.COL_W, max(4.2, 0.60 * n + 1.15))
    ax = fig.add_subplot(111)
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    def lay(items, top=0.90, bot=0.055):
        if len(items) == 1: return [(top + bot) / 2]
        return list(np.linspace(top, bot, len(items)))

    ly, ry = lay(lefts), lay(rights)
    LX, RX, BW = 0.02, 0.575, 0.405
    bh = min(0.072, 0.86 / max(n, 1))

    def box(x, y, name, qual, edge, face, mono=True):
        # identifiers can be multi-value ("a, b, c" or "a / b / c"); wrapping
        # on separators is what keeps them inside the box
        nm = fk.wrap_ident(name, 34)
        nlines = nm.count("\n") + 1
        h = bh * (1.0 + 0.34 * (nlines - 1))
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y - h / 2), BW, h,
            boxstyle="round,pad=0.003,rounding_size=0.010",
            facecolor=face, edgecolor=edge, linewidth=0.8, zorder=3))
        yy = y + (0.013 if qual else 0)
        ax.text(x + BW / 2, yy, nm, ha="center", va="center",
                fontsize=fk.FS_ANNOT, zorder=4, linespacing=1.15,
                family="monospace" if mono else "serif")
        if qual:
            ax.text(x + BW / 2, y - 0.013 - 0.012 * (nlines - 1),
                    fk.wrap(qual, 52), ha="center", va="center",
                    fontsize=fk.FS_SMALL - 0.6, color=MUTED, zorder=4,
                    linespacing=1.1)

    lpos, rpos = {}, {}
    for (nm, q), y in zip(lefts, ly):
        is_vlm = nm in VLM_FIELDS
        box(LX, y, nm, q, BLUE if is_vlm else MUTED,
            FAINT if is_vlm else "#F7F7F7")
        lpos[(nm, q)] = y
    for (nm, q), y in zip(rights, ry):
        passthru = "pass-through" in q.lower() or "not a closure" in q.lower()
        box(RX, y, nm, q, MUTED if passthru else GREEN, "white")
        rpos[(nm, q)] = y

    for a, b in edges:
        y0, y1 = lpos[a], rpos[b]
        weak = a[0] not in VLM_FIELDS
        x0, x1 = LX + BW, RX
        mid = (x0 + x1) / 2
        path = MPath([(x0, y0), (mid, y0), (mid, y1), (x1, y1)],
                     [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4])
        ax.add_patch(mpatches.PathPatch(
            path, facecolor="none", edgecolor=MUTED if weak else BLUE,
            linewidth=0.6, alpha=0.40 if weak else 0.70,
            linestyle=(0, (2, 2)) if weak else "solid", zorder=2))

    ax.text(LX + BW / 2, 0.975, "constraint field", ha="center", va="center",
            fontsize=fk.FS_LABEL, fontweight="bold")
    ax.text(RX + BW / 2, 0.975, "gripper closure parameter", ha="center",
            va="center", fontsize=fk.FS_LABEL, fontweight="bold")
    fig.legend(handles=[
        mpatches.Patch(facecolor=FAINT, edgecolor=BLUE,
                       label="emitted by the reasoning layer"),
        mpatches.Patch(facecolor="#F7F7F7", edgecolor=MUTED,
                       label="perception input or derived value"),
    ], loc="outside lower center", ncol=2)
    return fk.save(fig, out, "table_3_2_constraint_routing")

# ==========================================================================
# 7.1  BASE PLACEMENT, BEFORE AND AFTER
# ==========================================================================

def fig_baseplace(root, out, args):
    """
    Reachability as distance from the base, which is the quantity actually
    recorded.

    An earlier version drew a planar reach circle over the raw x/y columns.
    That was misleading: reachability came from the whole-body IK oracle, not
    from a planar radius, so candidates appeared outside a circle while being
    marked reachable. This plots the recorded per-candidate distance against
    the fixed-base reach limit instead, which is exactly the comparison the
    correction in Section 7.1 rests on.
    """
    rows = fk.load_table(root, "figure_data/grasp_targets.csv",
                         "export_grasps_plain.csv", "place_run.csv",
                         label="grasp targets")
    if not rows:
        raise DataProblem("figure_data/grasp_targets.csv not found")
    c_d = fk.pick_column(rows, "dist_from_base_m", "distance", label="distance")
    c_b = fk.pick_column(rows, "reachable_before", required=False)
    c_a = fk.pick_column(rows, "reachable_after", required=False)

    after = [fk.to_float(r[c_d]) for r in rows]
    after = [d for d in after if np.isfinite(d)]
    shift = args.d_before - args.d_after
    before = [d + shift for d in after]
    n_b = sum(fk.truthy(r[c_b]) for r in rows) if c_b else 0
    n_a = sum(fk.truthy(r[c_a]) for r in rows) if c_a else len(after)
    print(f"    {len(after)} candidates; recorded reachable "
          f"{n_b} before, {n_a} after")
    print(f"    recorded distance after placement "
          f"{min(after):.3f}-{max(after):.3f} m; "
          f"before derived by the {shift:.3f} m base translation "
          f"{min(before):.3f}-{max(before):.3f} m")

    fig = fk.new_figure(fk.COL_W, 3.1)
    ax = fig.add_subplot(111)
    reach = args.reach

    ax.axvspan(reach, max(before) * 1.06, color=RED, alpha=0.07, zorder=0)
    ax.axvline(reach, color=INK, lw=1.2, zorder=5)
    ax.annotate(f"fixed-base reach limit {reach:.3f} m",
                xy=(reach, 1.62), xytext=(-8, 0), textcoords="offset points",
                ha="right", va="center", fontsize=fk.FS_ANNOT, color=INK)

    rng = np.random.default_rng(3)
    for y, vals, col, lab, nk in [
            (1.0, before, RED, "at the capture pose", n_b),
            (0.0, after, GREEN, "after base translation", n_a)]:
        jit = rng.uniform(-0.11, 0.11, len(vals))
        ax.scatter(vals, y + jit, s=26, facecolor=col, edgecolor="white",
                   linewidth=0.5, zorder=4)
        ax.plot([min(vals), max(vals)], [y + 0.30] * 2, color=col, lw=1.0,
                zorder=3)
        for xe in (min(vals), max(vals)):
            ax.plot([xe, xe], [y + 0.27, y + 0.33], color=col, lw=1.0,
                    zorder=3)
        ax.text((min(vals) + max(vals)) / 2, y + 0.37,
                f"{min(vals):.2f}\u2013{max(vals):.2f} m",
                ha="center", va="bottom", fontsize=fk.FS_SMALL, color=col)
        ax.text(-0.012, y, f"{lab}\n{nk} of {len(vals)} reachable",
                transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=fk.FS_ANNOT, color=INK, linespacing=1.25)

    ax.set_yticks([]); ax.set_ylim(-0.55, 2.05)
    ax.set_xlim(min(after) * 0.90, max(before) * 1.06)
    ax.set_xlabel("distance from base to grasp candidate (m)")
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    fk.declutter(ax, xgrid=True, ygrid=False)
    ax.text(0.0, -0.20,
            fk.wrap("Distances after placement are recorded per candidate. "
                    "Distances at the capture pose are those values shifted by "
                    f"the {shift:.3f} m base translation, and match the "
                    "0.65-0.80 m range reported in Section 7.1. Reachability "
                    "flags come from the inverse-kinematics oracle, not from "
                    "this planar distance.", 104),
            transform=ax.transAxes, fontsize=fk.FS_SMALL, color=MUTED,
            ha="left", va="top", linespacing=1.3)
    return fk.save(fig, out, "fig_7_x_base_placement")

# ==========================================================================
# 5.1  MASK COVERAGE OVERLAY ON A REAL CAPTURE
# ==========================================================================

def _load_mask(root: Path, spec) -> np.ndarray:
    """Accept a path, an .npy, or an 'archive.npz::member' reference."""
    m = fk.load_array(root, spec)
    if m.ndim == 3:
        m = m[..., 0]
    if m.ndim != 2:
        raise DataProblem(f"{spec} is not a 2-D mask (shape {m.shape})")
    if m.dtype == bool:
        return m
    return m > (0.5 if float(m.max()) <= 1.0 else 127)


def _resolve_capture(root: Path, args):
    """Return (rgb_spec, obj_spec, part_spec, query) from flags or the index."""
    if args.rgb and args.object_mask and args.part_mask:
        return args.rgb, args.object_mask, args.part_mask, args.query
    rows = fk.load_table(root, "figure_data/captures_index.csv",
                         "captures_index.csv", label="captures index")
    if not rows:
        raise DataProblem(
            "overlay needs --rgb, --object-mask and --part-mask, or a "
            "figure_data/captures_index.csv to pick from with --capture-id")
    c_id = fk.pick_column(rows, "capture_id", "id", label="capture_id")
    c_rgb = fk.pick_column(rows, "rgb_path", "rgb", label="rgb_path")
    c_om = fk.pick_column(rows, "object_mask_path", "object_mask",
                          label="object_mask_path")
    c_pm = fk.pick_column(rows, "part_mask_path", "part_mask",
                          label="part_mask_path")
    c_q = fk.pick_column(rows, "instruction", "query", required=False)
    c_cit = fk.pick_column(rows, "citable", required=False)

    if not args.capture_id:
        print("    available captures:")
        for r in rows:
            cit = "" if not c_cit else (
                "" if fk.truthy(r[c_cit]) else "   [NOT CITABLE]")
            print(f"      {r[c_id]}  -  {r.get(c_q, '')}{cit}")
        raise DataProblem("choose one with --capture-id")

    match = [r for r in rows if r[c_id].strip() == args.capture_id.strip()]
    if not match:
        raise DataProblem(f"no capture_id {args.capture_id!r} in the index")
    r = match[0]
    if c_cit and not fk.truthy(r[c_cit]):
        print("    ! this capture is marked NOT CITABLE in the index")
    return r[c_rgb], r[c_om], r[c_pm], args.query or r.get(c_q, "")


def fig_overlay(root: Path, out: Path, args):
    """
    Draw the object-query mask and the part-query mask on the real capture and
    state the coverage. This is the figure that carries the collapse claim, so
    it shows outlines rather than filled masks: a filled part mask over a
    filled object mask hides exactly the difference the reader is looking for.
    """
    rgb_spec, obj_spec, part_spec, query = _resolve_capture(root, args)
    rgb = fk.load_array(root, rgb_spec)
    if rgb.ndim == 2:
        rgb = np.dstack([rgb] * 3)
    if rgb.dtype != np.uint8:
        rgb = (255 * (rgb - rgb.min()) /
               max(rgb.ptp(), 1e-9)).astype(np.uint8)
    m_obj = _load_mask(root, obj_spec)
    m_part = _load_mask(root, part_spec)
    if m_obj.shape != rgb.shape[:2] or m_part.shape != rgb.shape[:2]:
        raise DataProblem(
            f"shape mismatch: rgb {rgb.shape[:2]}, object {m_obj.shape}, "
            f"part {m_part.shape}")

    coverage = m_part.sum() / max(m_obj.sum(), 1)
    print(f"    coverage = {coverage:.3f}  "
          f"(part {int(m_part.sum())} px / object {int(m_obj.sum())} px)")

    h, w = rgb.shape[:2]
    fig = fk.new_figure(fk.COL_W, fk.COL_W * h / w * 0.52)
    axes = fig.subplots(1, 2)

    for ax in axes:
        ax.imshow(rgb)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(RULE)
            s.set_linewidth(0.7)

    axes[0].set_title("(a) capture and query", fontsize=fk.FS_ANNOT,
                      color=MUTED)
    if query:
        axes[0].text(0.02, 0.02, f'"{query}"', transform=axes[0].transAxes,
                     fontsize=fk.FS_ANNOT, color="white", va="bottom",
                     bbox=dict(boxstyle="round,pad=0.3", fc=INK, ec="none",
                               alpha=0.75))

    # Outlines, not fills: the overlap is the finding.
    axes[1].contour(m_obj, levels=[0.5], colors=[BLUE], linewidths=1.4)
    axes[1].contour(m_part, levels=[0.5], colors=[ORANGE], linewidths=1.4,
                    linestyles="dashed")
    axes[1].set_title("(b) object query against part query",
                      fontsize=fk.FS_ANNOT, color=MUTED)
    axes[1].text(0.98, 0.02, f"coverage {coverage*100:.0f}%",
                 transform=axes[1].transAxes, ha="right", va="bottom",
                 fontsize=fk.FS_LABEL, color="white", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.32", fc=RED, ec="none",
                           alpha=0.88))

    handles = [Line2D([], [], color=BLUE, lw=1.4, label="object query"),
               Line2D([], [], color=ORANGE, lw=1.4, ls="--",
                      label="part query")]
    fig.legend(handles=handles, loc="outside lower center", ncol=2)
    stem = args.stem or "fig_5_2_requested_vs_returned"
    return fk.save(fig, out, stem)


# ==========================================================================
# ADDITIONAL FIGURES
# Each expects a file under figure_data/ produced by the repo-scan step.
# ==========================================================================

def _need(root, name, label):
    rows = fk.load_table(root, f"figure_data/{name}", name,
                         f"report_assets/{name}", label=label)
    if rows is None:
        raise DataProblem(
            f"{label} needs figure_data/{name}. Run the repo-scan prompt "
            f"(CLAUDE_CODE_PROMPT.md) to generate it.")
    return rows


# ---- 5.1  mask coverage by object and run --------------------------------

def _capture_bank(root, args):
    """
    Load every capture named in captures_index.csv, keyed by capture_id and
    also indexed by (object, instruction) so a data row can find its picture.
    """
    rows = fk.load_table(root, "figure_data/captures_index.csv",
                         "captures_index.csv", label="captures index")
    if not rows:
        return {}, {}
    c_id = fk.pick_column(rows, "capture_id", label="capture_id")
    c_rgb = fk.pick_column(rows, "rgb_path", label="rgb_path")
    c_om = fk.pick_column(rows, "object_mask_path", label="object_mask_path")
    c_pm = fk.pick_column(rows, "part_mask_path", label="part_mask_path")
    c_ob = fk.pick_column(rows, "object", required=False)
    c_in = fk.pick_column(rows, "instruction", required=False)

    bank, by_key = {}, {}
    for r in rows:
        try:
            rgb = fk.load_array(root, r[c_rgb])
            if rgb.ndim == 2:
                rgb = np.dstack([rgb] * 3)
            if rgb.dtype != np.uint8:
                rgb = (255 * (rgb - rgb.min()) /
                       max(float(rgb.max() - rgb.min()), 1e-9)).astype(np.uint8)
            rec = dict(rgb=rgb,
                       obj=_load_mask(root, r[c_om]),
                       part=_load_mask(root, r[c_pm]),
                       object=r.get(c_ob, ""), instruction=r.get(c_in, ""))
        except Exception as e:
            print(f"    ! capture {r[c_id]}: {e}")
            continue
        bank[r[c_id]] = rec
        if c_ob:
            by_key.setdefault(r[c_ob].strip().lower(), []).append(rec)
    print(f"    {len(bank)} capture(s) loaded for compositing")
    return bank, by_key


def _pick_capture(by_key, object_name):
    """Best capture for an object name, matching on the leading noun."""
    if not by_key:
        return None
    key = str(object_name).strip().lower()
    if key in by_key:
        return by_key[key][0]
    for k, v in by_key.items():
        if k in key or key in k or k.split()[-1] == key.split()[-1]:
            return v[0]
    return None


def fig_coverage(root, out, args):
    """
    Coverage per run, each row flanked by its own regrounded capture.

    FIGURE_ASSETS.csv pairs every run_id in coverage.csv with the masks
    regenerated for that exact query, so each bar is anchored to the pictures
    that produced it rather than to a representative capture of the object.
    """
    rows = _need(root, "coverage.csv", "mask coverage")
    c_obj = fk.pick_column(rows, "object", label="object")
    c_cov = fk.pick_column(rows, "coverage", "coverage_frac", label="coverage")
    c_ins = fk.pick_column(rows, "instruction", "run", required=False)
    c_run = fk.pick_column(rows, "run_id", required=False)
    assets = load_assets(root).get("5.1", {})

    items = []
    for r in rows:
        v = fk.to_float(r[c_cov])
        if v > 1.5:
            v /= 100.0
        rid = r[c_run].strip() if c_run else ""
        items.append((r[c_obj].strip(),
                      r[c_ins].strip() if c_ins else "", v, rid))

    bundles = {}
    for o, ins, v, rid in items:
        rec = assets.get(rid)
        if rec is None:
            for k, cand in assets.items():
                if rid and rid in k:
                    rec = cand
                    break
        if rec:
            bundles[rid] = _asset_masks(root, rec)
    have = any(b and b[0] is not None for b in bundles.values())
    if not have:
        print("    ! no regrounded capture resolved; bars only")

    nrow = len(items)
    fig = fk.new_figure(fk.COL_W, 0.98 * nrow + 1.15)
    if have:
        gs = fig.add_gridspec(nrow, 3, width_ratios=[1.0, 3.2, 1.0],
                              wspace=0.06, hspace=0.34)
    else:
        gs = fig.add_gridspec(nrow, 1, hspace=0.34)

    for i, (o, ins, v, rid) in enumerate(items):
        ax = fig.add_subplot(gs[i, 1] if have else gs[i, 0])
        ax.barh([0], [v], height=0.55,
                color=fk.semantic_colour("perception"),
                edgecolor="white", linewidth=0.6, zorder=3)
        ax.text(0.012, 0, f"\u201c{ins}\u201d", ha="left", va="center",
                fontsize=fk.FS_SMALL, color="white", zorder=5)
        ax.text(1.05, 0, f"{v*100:.0f}%", ha="left", va="center",
                fontsize=fk.FS_SMALL, color=INK, zorder=5)
        ax.axvline(1.0, color=OK["black"], lw=1.0, ls=(0, (4, 2)), zorder=4)
        ax.set_xlim(0, 1.24); ax.set_ylim(-0.5, 0.5); ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        fk.declutter(ax, xgrid=True, ygrid=False)
        if i == 0:
            ax.text(1.0, 0.55, "whole-object baseline ",
                    color=OK["black"], fontsize=fk.FS_SMALL, ha="right",
                    va="bottom")
        if i < nrow - 1:
            plt.setp(ax.get_xticklabels(), visible=False)
            ax.tick_params(axis="x", length=0)
        else:
            ax.set_xlabel("part-mask area as a fraction of the "
                          "whole-object mask")
        if not have:
            continue

        rgb, mo, mp = bundles.get(rid, (None, None, None))
        axl, axr = fig.add_subplot(gs[i, 0]), fig.add_subplot(gs[i, 2])
        for a in (axl, axr):
            a.set_xticks([]); a.set_yticks([])
        if rgb is None:
            for a in (axl, axr):
                a.set_axis_off()
                a.text(0.5, 0.5, "no capture", transform=a.transAxes,
                       ha="center", va="center", fontsize=fk.FS_SMALL,
                       color=MUTED)
            continue
        bb = fk.crop_to(mo if mo is not None else mp, pad_frac=0.24,
                        shape=rgb.shape[:2], aspect=1.0)
        x0, y0, x1, y1 = bb
        sub = rgb[y0:y1 + 1, x0:x1 + 1]
        for a, part, whole, ttl in (
                (axl, None, mo, "object query"),
                (axr, mp, mo, "part query")):
            a.imshow(sub, interpolation="antialiased")
            fk.mask_contour(a,
                            None if part is None else part[y0:y1+1, x0:x1+1],
                            whole_mask=None if whole is None
                            else whole[y0:y1+1, x0:x1+1],
                            colour=fk.semantic_colour("perception"))
            for sp in a.spines.values():
                sp.set_edgecolor(RULE); sp.set_linewidth(0.7)
            if i == 0:
                a.set_title(ttl, fontsize=fk.FS_SMALL, color=MUTED, pad=2)
        axl.set_ylabel(o, fontsize=fk.FS_SMALL, color=INK, rotation=0,
                       ha="right", va="center", labelpad=4)

    if have:
        fig.legend(handles=[
            Line2D([], [], color=OK["black"], lw=1.0, ls=(0, (4, 2)),
                   label="whole-object mask"),
            mpatches.Patch(facecolor=fk.semantic_colour("perception"),
                           alpha=0.35,
                           edgecolor=fk.semantic_colour("perception"),
                           label="part mask returned"),
        ], loc="outside lower center", ncol=2)
    return fk.save(fig, out, "fig_5_1_mask_coverage_by_run")

def _thumb(ax, root, rec, role="rgb", title=None, citable=True,
           crop_frac=0.55):
    """Draw one bundle asset into an axes, centre-cropped, with a frame."""
    img = _asset_array(root, rec, role)
    if img is None:
        ax.set_axis_off()
        ax.text(0.5, 0.5, "no capture\nin the repository", ha="center",
                va="center", transform=ax.transAxes, fontsize=fk.FS_SMALL,
                color=MUTED, linespacing=1.2)
        if title:
            ax.set_title(title, fontsize=fk.FS_SMALL, color=MUTED, pad=2)
        return False
    if img.ndim == 2:
        img = np.dstack([img] * 3)
    if img.dtype != np.uint8:
        img = (255 * (img - img.min()) /
               max(float(img.max() - img.min()), 1e-9)).astype(np.uint8)
    img = fk.trim_caption_band(img)
    h, w = img.shape[:2]
    if crop_frac < 1.0:
        ch, cw = int(h * crop_frac), int(w * crop_frac)
        y0, x0 = (h - ch) // 2, (w - cw) // 2
        img = img[y0:y0 + ch, x0:x0 + cw]
    ax.imshow(img, interpolation="antialiased")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(RED if not citable else RULE)
        s.set_linewidth(1.1 if not citable else 0.7)
    if title:
        ax.set_title(title, fontsize=fk.FS_SMALL, color=MUTED, pad=2)
    if not citable:
        ax.text(0.5, 0.03, "not citable", transform=ax.transAxes,
                ha="center", va="bottom", fontsize=fk.FS_SMALL - 0.5,
                color="white", bbox=dict(boxstyle="round,pad=0.22", fc=RED,
                                         ec="none", alpha=0.9))
    return True


def _cloud(ax, root, rec, colour_by_label=True):
    """Filled 2-D projection of a labelled cloud, per the point-cloud rule."""
    a = rec.get("cloud")
    if not a or not a["path"]:
        return False
    p, _ = fk.split_ref(a["path"])
    p = p if p.is_absolute() else root / p
    if not p.exists():
        print(f"    ! cloud not found: {p}")
        return False
    z = np.load(p, allow_pickle=False)
    xy = z["points_xy"] if "points_xy" in z else z[list(z.keys())[0]]
    lab = z["part_labels"] if "part_labels" in z else np.full(len(xy), -1)
    names = ([str(s) for s in z["label_names"]]
             if "label_names" in z else [])
    ax.scatter(xy[:, 0], xy[:, 1], s=1.6, c="#BFBFBF", linewidths=0,
               zorder=2)
    pal = [fk.semantic_colour("geometric_planning"),
           fk.semantic_colour("perception"), fk.OKABE_ITO["purple"]]
    shown = 0
    for i, li in enumerate(sorted(set(int(v) for v in lab) - {-1})):
        sel = lab == li
        if sel.sum() < 3:
            continue
        col = pal[i % len(pal)]
        hull = fk.hull_2d(xy[sel])
        ax.fill(hull[:, 0], hull[:, 1], facecolor=col, alpha=0.22,
                edgecolor=col, linewidth=1.2, zorder=3)
        ax.scatter(xy[sel, 0], xy[sel, 1], s=2.4, c=col, linewidths=0,
                   zorder=4)
        nm = names[li] if li < len(names) else f"component {li}"
        cx, cy = xy[sel, 0].mean(), xy[sel, 1].mean()
        dy = 16 if i % 2 == 0 else -18
        ax.annotate(fk.display_soft(nm), xy=(cx, cy), xytext=(0, dy),
                    textcoords="offset points", ha="center",
                    va="bottom" if dy > 0 else "top",
                    fontsize=fk.FS_SMALL, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
        shown += 1
    if shown == 0:
        ax.text(0.5, 0.04, "no component recovered", transform=ax.transAxes,
                ha="center", va="bottom", fontsize=fk.FS_SMALL, color=RED)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(RULE); s.set_linewidth(0.7)
    return True


def fig_fragmentation(root, out, args):
    """
    The mug handle case: source capture, recovered components, and both limbs
    of the evidence gate.

    Panels (a) and (b) are the picture and the geometry from the same capture;
    (c) and (d) are the two gate limbs. The combined point count clears one
    limb, neither fragment clears the other, so the component stays refused.
    """
    rows = _need(root, "fragments.csv", "fragment measurements")
    c_part = fk.pick_column(rows, "fragment", "part", label="fragment")
    c_pts = fk.pick_column(rows, "points", label="points")
    c_w = fk.pick_column(rows, "width_mm", "width", label="width_mm")
    bundle = bundle_for(load_assets(root), "5.4")
    rec = bundle.get("mug_fragmentation", {})

    frags, combined = [], None
    for r in rows:
        nm, pts, w = str(r[c_part]).strip(), fk.to_float(r[c_pts]), fk.to_float(r[c_w])
        if "combin" in nm.lower() or not np.isfinite(w):
            combined = pts
        else:
            frags.append((nm, pts, w))
    if not frags:
        raise DataProblem("fragments.csv has no per-fragment rows with a width")
    names = [fk.wrap(fk.display(f[0], strict=False), 14) for f in frags]

    fig = fk.new_figure(fk.COL_W, 4.05)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], hspace=0.12,
                          wspace=0.24)
    axA, axB = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    axC, axD = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

    _thumb(axA, root, rec, "rgb", crop_frac=0.62)
    fk.panel_label(axA, "a")
    axA.set_xlabel("source capture", fontsize=fk.FS_SMALL, color=MUTED)
    if not _cloud(axB, root, rec):
        axB.set_axis_off()
        axB.text(0.5, 0.5, "cloud not available", ha="center", va="center",
                 transform=axB.transAxes, fontsize=fk.FS_SMALL, color=MUTED)
    fk.panel_label(axB, "b")
    axB.set_xlabel("recovered components", fontsize=fk.FS_SMALL, color=MUTED)

    x = np.arange(len(frags))
    pts = [f[1] for f in frags]
    axC.bar(x, pts, width=0.5, color=fk.semantic_colour("robot_control"),
            edgecolor="white", linewidth=0.6, zorder=3)
    if combined and np.isfinite(combined):
        axC.bar([len(x)], [combined], width=0.5,
                color=fk.semantic_colour("keep"), edgecolor="white",
                linewidth=0.6, hatch="//", zorder=3)
        axC.text(len(x), combined + 3, f"{combined:.0f}", ha="center",
                 va="bottom", fontsize=fk.FS_SMALL,
                 color=fk.semantic_colour("keep"))
    for xx, v in zip(x, pts):
        axC.text(xx, v + 3, f"{v:.0f}", ha="center", va="bottom",
                 fontsize=fk.FS_SMALL)
    axC.axhline(GATE_POINTS, color=fk.OKABE_ITO["orange"], lw=1.0,
                ls=(0, (4, 3)), zorder=4)
    axC.text(len(x) + 0.42, GATE_POINTS + 2, f"gate {GATE_POINTS} points",
             color=fk.OKABE_ITO["orange"], fontsize=fk.FS_SMALL,
             ha="right", va="bottom")
    axC.set_xticks(list(x) + ([len(x)] if combined else []))
    axC.set_xticklabels(names + (["combined"] if combined else []),
                        fontsize=fk.FS_SMALL)
    axC.set_ylabel("points")
    axC.set_ylim(0, max(pts + ([combined] if combined else []) +
                        [GATE_POINTS]) * 1.34)
    fk.declutter(axC); fk.panel_label(axC, "c")

    wid = [f[2] for f in frags]
    axD.bar(x, wid, width=0.5, color=fk.semantic_colour("robot_control"),
            edgecolor="white", linewidth=0.6, zorder=3)
    for xx, v in zip(x, wid):
        axD.text(xx, v + 0.15, f"{v:.0f} mm", ha="center", va="bottom",
                 fontsize=fk.FS_SMALL)
    axD.axhline(GATE_WIDTH_MM, color=fk.OKABE_ITO["orange"], lw=1.0,
                ls=(0, (4, 3)), zorder=4)
    axD.text(len(x) - 0.55, GATE_WIDTH_MM + 0.12, f"gate {GATE_WIDTH_MM:g} mm",
             color=fk.OKABE_ITO["orange"], fontsize=fk.FS_SMALL, ha="right",
             va="bottom")
    axD.set_xticks(x); axD.set_xticklabels(names, fontsize=fk.FS_SMALL)
    axD.set_ylabel("measured width (mm)")
    axD.set_ylim(0, max(wid + [GATE_WIDTH_MM]) * 1.42)
    fk.declutter(axD); fk.panel_label(axD, "d")
    return fk.save(fig, out, "fig_5_4_fragmentation")

def fig_clutter(root, out, args):
    """
    Isolated against cluttered, with the four source scenes above the change.

    The captures carry what changed about the scene; the slope carries what
    changed about the measurement. Direction is not uniform, so the slope form
    is the honest one.
    """
    rows = _need(root, "clutter.csv", "clutter comparison")
    c_obj = fk.pick_column(rows, "object", label="object")
    c_part = fk.pick_column(rows, "part", required=False)
    c_cond = fk.pick_column(rows, "condition", "scene", label="condition")
    c_ext = fk.pick_column(rows, "extent_mm", "width_mm", label="extent_mm")
    bundle = bundle_for(load_assets(root), "5.5")

    items = {}
    for r in rows:
        key = f"{r[c_obj]} {r[c_part]}" if c_part else r[c_obj]
        cond = "isolated" if "isol" in r[c_cond].lower() else "cluttered"
        items.setdefault(key, {})[cond] = fk.to_float(r[c_ext])

    order = ["pot_isolated", "pot_cluttered", "remote_isolated",
             "remote_cluttered"]
    order = [k for k in order if k in bundle] or list(bundle)[:4]
    fig = fk.new_figure(fk.COL_W, 5.30)
    gs = fig.add_gridspec(2, max(len(order), 1),
                          height_ratios=[0.92, 1.30], hspace=0.30,
                          wspace=0.14)
    for i, cid in enumerate(order):
        ax = fig.add_subplot(gs[0, i])
        lab = cid.replace("_", " ")
        _thumb(ax, root, bundle[cid], "rgb", title=lab, crop_frac=0.60)
        fk.panel_label(ax, "abcd"[i] if i < 4 else str(i))

    ax = fig.add_subplot(gs[1, :])
    labels = []
    for name, d in sorted(items.items()):
        a, b = d.get("isolated", np.nan), d.get("cluttered", np.nan)
        if not (np.isfinite(a) and np.isfinite(b)):
            continue
        col = (fk.semantic_colour("robot_control") if b < a
               else fk.semantic_colour("reasoning"))
        ax.plot([0, 1], [a, b], marker="o", ms=6, lw=1.6, color=col, zorder=4)
        labels.append(ax.annotate(f"{name}\n{a:.0f} {ARROW} {b:.0f} mm",
                                  xy=(1, b), xytext=(12, 0),
                                  textcoords="offset points", va="center",
                                  ha="left", fontsize=fk.FS_SMALL, color=col))
    ax.axhline(GATE_WIDTH_MM, color=fk.OKABE_ITO["orange"], lw=0.9,
               ls=(0, (4, 3)), zorder=3)
    ax.text(-0.06, GATE_WIDTH_MM, f"{GATE_WIDTH_MM:g} mm gate ",
            color=fk.OKABE_ITO["orange"], fontsize=fk.FS_SMALL, ha="right",
            va="bottom")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["isolated", "cluttered"])
    ax.set_xlim(-0.5, 1.78); ax.set_ylim(0, None)
    ax.set_ylabel("measured graspable extent (mm)")
    fk.declutter(ax); fk.panel_label(ax, "e")
    ax.text(0.0, -0.20,
            fk.wrap("Clutter changes what is measurable without changing what "
                    "is reasoned. The direction is not uniform: the pot "
                    "component shrinks, the remote component grows. Extents "
                    "come from the multi-view fused chain; the captures above "
                    "are the corresponding scenes.", 104),
            transform=ax.transAxes, fontsize=fk.FS_SMALL, color=MUTED,
            ha="left", va="top", linespacing=1.3)
    fk.resolve_collisions(fig, labels)
    return fk.save(fig, out, "fig_5_5_clutter_dependence")

def fig_grid(root, out, args):
    """
    The eighteen-cell grid with the capture behind each object.

    The nominated part is constant within every object except one, so the
    figure has to make the row the unit of reading. Each row leads with the
    capture that object's cells were reasoned over; two objects have no
    capture anywhere in the repository and are drawn as recorded gaps.
    """
    rows = _need(root, "reasoning_grid.csv", "reasoning grid")
    c_obj = fk.pick_column(rows, "object", label="object")
    c_ins = fk.pick_column(rows, "instruction_type", "instruction",
                           label="instruction")
    c_part = fk.pick_column(rows, "target_part", "part", label="target_part")
    c_flag = fk.pick_column(rows, "thermal_flag", "thermal", required=False)
    bundle = bundle_for(load_assets(root), "6.1")

    objs, inss = [], []
    for r in rows:
        if r[c_obj] not in objs: objs.append(r[c_obj])
        if r[c_ins] not in inss: inss.append(r[c_ins])
    cell = {(r[c_obj], r[c_ins]): r for r in rows}

    def find(o):
        for cid, rec in bundle.items():
            if cid.split("_")[0].lower() == o.strip().lower():
                return rec
        return None

    fig = fk.new_figure(fk.COL_W, 0.80 * len(objs) + 1.30)
    gs = fig.add_gridspec(len(objs), 2, width_ratios=[0.62, 4.0],
                          wspace=0.05, hspace=0.16)
    for j, o in enumerate(objs):
        rec = find(o)
        axi = fig.add_subplot(gs[j, 0])
        _thumb(axi, root, rec or {}, "rgb",
               citable=(rec or {}).get("rgb", {}).get("citable", True),
               crop_frac=0.58)
        axi.set_ylabel(o, fontsize=fk.FS_LABEL, rotation=0, ha="right",
                       va="center", labelpad=6)

        ax = fig.add_subplot(gs[j, 1])
        ax.set_axis_off(); ax.set_xlim(0, len(inss)); ax.set_ylim(0, 1)
        parts = {cell[(o, i)][c_part] for i in inss if (o, i) in cell}
        constant = len(parts) == 1
        for i, ins in enumerate(inss):
            r = cell.get((o, ins))
            ax.add_patch(mpatches.Rectangle(
                (i + 0.03, 0.13), 0.94, 0.74,
                facecolor=FAINT if constant else "#FDF1E3",
                edgecolor="white", linewidth=1.2, zorder=2))
            if r is None:
                continue
            ax.text(i + 0.5, 0.50, r[c_part], ha="center", va="center",
                    fontsize=fk.FS_ANNOT, zorder=3)
            if c_flag and fk.flagged(r[c_flag]):
                ax.plot([i + 0.90], [0.79], marker="o", ms=3.2,
                        color=fk.semantic_colour("robot_control"), zorder=4)
        ax.text(len(inss) + 0.04, 0.5, "constant" if constant else "varies",
                ha="left", va="center", fontsize=fk.FS_SMALL,
                color=MUTED if constant else fk.OKABE_ITO["orange"])
        if j == 0:
            for i, ins in enumerate(inss):
                ax.text(i + 0.5, 1.05, ins, ha="center", va="bottom",
                        fontsize=fk.FS_LABEL, fontweight="bold")

    fig.text(0.02, 0.012,
             fk.wrap("A dot marks a thermal or hygiene flag. The shaded row is "
                     "the one object whose nominated part varies across "
                     "instructions. Two objects have no capture in the "
                     "repository and are shown as gaps rather than "
                     "substituted.", 108),
             fontsize=fk.FS_SMALL, color=MUTED, ha="left", va="bottom",
             linespacing=1.3)
    return fk.save(fig, out, "fig_6_1_reasoning_grid")

def fig_handover(root, out, args):
    """Nominated part under each contract, with the changes called out."""
    rows = _need(root, "handover_ablation.csv", "handover ablation")
    c_obj = fk.pick_column(rows, "object", label="object")
    c_con = fk.pick_column(rows, "contract", "condition", label="contract")
    c_part = fk.pick_column(rows, "target_part", "part", label="target_part")
    c_bad = fk.pick_column(rows, "contradiction", "defect", required=False)

    objs = []
    for r in rows:
        if r[c_obj] not in objs:
            objs.append(r[c_obj])
    base, recv, bad = {}, {}, set()
    for r in rows:
        tgt = recv if any(k in r[c_con].lower()
                          for k in ("receiver", "aware", "revised")) else base
        tgt[r[c_obj]] = r[c_part]
        if c_bad and str(r[c_bad]).strip().lower() in ("1", "true", "yes"):
            bad.add(r[c_obj])

    fig = fk.new_figure(fk.COL_W, 0.38 * len(objs) + 1.3)
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(objs) + 0.4)
    xa, xb = 0.30, 0.68

    ax.text(xa, len(objs) + 0.15, "baseline contract", ha="center",
            fontsize=fk.FS_LABEL, fontweight="bold")
    ax.text(xb, len(objs) + 0.15, "receiver-aware contract", ha="center",
            fontsize=fk.FS_LABEL, fontweight="bold")

    changed = 0
    for j, o in enumerate(objs):
        y = len(objs) - 1 - j + 0.5
        a, b = base.get(o, "-"), recv.get(o, "-")
        diff = a != b
        changed += diff
        ax.text(0.02, y, o, ha="left", va="center", fontsize=fk.FS_ANNOT)
        for x, t in ((xa, a), (xb, b)):
            ax.add_patch(mpatches.FancyBboxPatch(
                (x - 0.125, y - 0.17), 0.25, 0.34,
                boxstyle="round,pad=0.004,rounding_size=0.02",
                facecolor=FAINT if not diff else "#E8F4EF",
                edgecolor=MUTED if not diff else GREEN,
                linewidth=0.8, zorder=2))
            ax.text(x, y, t, ha="center", va="center", fontsize=fk.FS_ANNOT,
                    zorder=3)
        ax.annotate("", xy=(xb - 0.13, y), xytext=(xa + 0.13, y),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8,
                                    color=GREEN if diff else RULE,
                                    shrinkA=0, shrinkB=0))
        if o in bad:
            ax.text(xb, y - 0.30, "internally contradictory",
                    ha="center", va="top", fontsize=fk.FS_SMALL, color=RED)
    ax.text(0.0, -0.02,
            f"The nominated part changes for {changed} of {len(objs)} objects.",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=fk.FS_SMALL, color=MUTED)
    return fk.save(fig, out, "fig_6_2_handover_ablation")


# ---- 6.3  three-method agreement matrix ----------------------------------

def fig_agreement(root, out, args):
    """
    What each method selected, per object, across all logged instructions.

    The source has several instructions per object and no instruction column,
    so pairwise per-cell agreement is not recoverable. What IS recoverable is
    the set of components each method ever selected for an object, and whether
    two methods' sets intersect. Any intersection is printed to the console,
    because Section 6.5 claims no two methods agreed on any object and an
    intersection would qualify that claim.
    """
    rows = _need(root, "part_selection_methods.csv", "part selection methods")
    c_obj = fk.pick_column(rows, "object", label="object")
    c_m = fk.pick_column(rows, "method", label="method")
    c_sel = fk.pick_column(rows, "selected_component", "selection",
                           label="selected_component")
    c_ref = fk.pick_column(rows, "refused", required=False)
    c_val = fk.pick_column(rows, "validated_against_image", "validated",
                           required=False)

    c_mn = fk.pick_column(rows, "method_name", required=False)
    objs, methods, mnames = [], [], {}
    sets, refused, validated = {}, {}, {}
    for r in rows:
        o, meth = r[c_obj].strip(), r[c_m].strip()
        if o not in objs: objs.append(o)
        if meth not in methods: methods.append(meth)
        if c_mn and meth not in mnames:
            mnames[meth] = fk.split_qualifier(r[c_mn])[0]
        sel = r[c_sel].strip()
        sets.setdefault((o, meth), []).append(sel)
        if c_ref and fk.truthy(r[c_ref]):
            refused[(o, meth)] = True
        if c_val and fk.truthy(r[c_val]):
            validated[(o, meth)] = True
    methods.sort()

    def core(s):
        """Strip parenthetical commentary so 'refused (matched x)' compares."""
        return re.split(r"[(\[]", s)[0].strip().lower()

    overlaps = []
    for o in objs:
        for i, a in enumerate(methods):
            for b in methods[i + 1:]:
                sa = {core(s) for s in sets.get((o, a), []) if s}
                sb = {core(s) for s in sets.get((o, b), []) if s}
                shared = {x for x in (sa & sb) if x and "none" not in x}
                if shared:
                    overlaps.append((o, a, b, sorted(shared)))
    if overlaps:
        print("    ! methods share a selected component on:")
        for o, a, b, sh in overlaps:
            print(f"        {o}: {a} and {b} both selected {', '.join(sh)}")
        print("      Section 6.5 says no two methods agreed on any object - "
              "check that wording against this.")
    else:
        print("    no two methods share a selected component on any object")

    bundle = bundle_for(load_assets(root), "6.3")

    def _find(o):
        for cid, rec in bundle.items():
            if cid.split("_")[0].lower() == o.strip().lower():
                return rec
        return None

    fig = fk.new_figure(fk.COL_W, 0.86 * len(objs) + 1.7)
    gs = fig.add_gridspec(1, 2, width_ratios=[0.62, 4.0], wspace=0.05)
    inner = gs[0, 1].subgridspec(1, 1)
    ax = fig.add_subplot(inner[0, 0])
    imgs = gs[0, 0].subgridspec(len(objs), 1, hspace=0.14)
    for j, o in enumerate(objs):
        rec = _find(o)
        axi = fig.add_subplot(imgs[j, 0])
        _thumb(axi, root, rec or {}, "rgb",
               citable=(rec or {}).get("rgb", {}).get("citable", True),
               crop_frac=0.58)
    ax.set_axis_off()
    ax.set_xlim(0, len(methods))
    ax.set_ylim(0, len(objs))

    for j, o in enumerate(objs):
        y = len(objs) - 1 - j
        shared_here = {x for ov in overlaps if ov[0] == o for x in ov[3]}
        for i, meth in enumerate(methods):
            sel = sets.get((o, meth), [])
            uniq = []
            for s in sel:
                if s and s not in uniq:
                    uniq.append(s)
            is_ref = refused.get((o, meth), False)
            hit = any(core(s) in shared_here for s in uniq)
            ax.add_patch(mpatches.Rectangle(
                (i + 0.04, y + 0.08), 0.92, 0.84,
                facecolor="#E8F4EF" if hit else ("#F4F4F4" if is_ref else FAINT),
                edgecolor=GREEN if hit else "white", linewidth=1.2, zorder=2))
            body = "\n".join(fk.wrap(fk.display_soft(s), 24)
                             for s in uniq[:3]) or "-"
            ax.text(i + 0.5, y + 0.52, body, ha="center", va="center",
                    fontsize=fk.FS_SMALL, color=INK, zorder=3,
                    linespacing=1.2)
            if validated.get((o, meth)):
                # a drawn marker, not a glyph: the check mark is missing from
                # the serif fonts this style falls back to
                ax.plot([i + 0.90], [y + 0.82], marker="o", ms=4.0,
                        color=BLUE, zorder=4)
        ax.text(-0.02, y + 0.5, o, ha="right", va="center",
                fontsize=fk.FS_LABEL)
    for i, meth in enumerate(methods):
        # method codes A/B/C carry reader-facing names in DISPLAY_NAME
        nm = fk.display_soft(mnames.get(meth, f"method {meth}"))
        ax.text(i + 0.5, len(objs) + 0.10, nm, ha="center",
                va="bottom", fontsize=fk.FS_LABEL, fontweight="bold")

    ax.text(0.0, -0.02,
            fk.wrap("Each cell lists the distinct components that method "
                    "selected for that object across all logged instructions. "
                    "Green marks a component two methods share. A blue dot "
                    "marks a selection independently checked against the "
                    "image.", 100),
            transform=ax.transAxes, fontsize=fk.FS_SMALL, color=MUTED,
            ha="left", va="top", linespacing=1.3)
    return fk.save(fig, out, "fig_6_3_method_selections")

def fig_servo(root, out, args):
    """
    Servo alignment as measured endpoints, NOT a convergence curve.

    The repository holds no per-iteration servo log; only before/after values
    per trial exist. Drawing a smooth trajectory would imply a time series that
    was never recorded, so this plots the endpoints as a slope chart and says
    so on the figure.
    """
    rows = _need(root, "servo_trace.csv", "servo trace")
    c_tr = fk.pick_column(rows, "trial", label="trial")
    c_it = fk.pick_column(rows, "iteration", "stage", "point", label="iteration")
    c_e = fk.pick_column(rows, "pixel_error", "error_px", label="pixel_error")

    per = {}
    for r in rows:
        v = fk.to_float(r[c_e])
        if np.isfinite(v):
            per.setdefault(str(r[c_tr]).strip(), {})[
                str(r[c_it]).strip().lower()] = v

    fig = fk.new_figure(fk.HALF_W * 1.75, 3.2)
    ax = fig.add_subplot(111)

    xs = {"before": 0.0, "after": 1.0, "final": 1.0}
    labelled = []
    for i, (trial, pts) in enumerate(sorted(per.items())):
        col = [BLUE, PURPLE, GREEN, ORANGE][i % 4]
        if "before" in pts and "after" in pts:
            ax.plot([0, 1], [pts["before"], pts["after"]], marker="o", ms=6,
                    lw=1.6, color=col, zorder=4)
            labelled.append(ax.annotate(
                f"trial {trial}\n{pts['before']:.1f} {ARROW} {pts['after']:.1f} px",
                xy=(1, pts["after"]), xytext=(12, 0),
                textcoords="offset points", va="center", ha="left",
                fontsize=fk.FS_ANNOT, color=col))
        for k, v in pts.items():
            if k not in ("before", "after"):
                ax.scatter([xs.get(k, 1.0)], [v], s=52, marker="D",
                           facecolor="white", edgecolor=col, linewidth=1.4,
                           zorder=5)
                labelled.append(ax.annotate(
                    f"trial {trial}\nresidual {v:.1f} px",
                    xy=(xs.get(k, 1.0), v), xytext=(12, 0),
                    textcoords="offset points", va="center", ha="left",
                    fontsize=fk.FS_ANNOT, color=col))

    if args.servo_tolerance:
        ax.axhline(args.servo_tolerance, color=RED, lw=0.9, ls=(0, (4, 3)),
                   zorder=3)
        ax.text(-0.06, args.servo_tolerance,
                f"{args.servo_tolerance:g} px tolerance ", color=RED,
                fontsize=fk.FS_SMALL, ha="right", va="bottom")
    if args.servo_noise_floor:
        ax.axhspan(0, args.servo_noise_floor, color=ORANGE, alpha=0.16,
                   zorder=1)
        ax.text(-0.06, args.servo_noise_floor / 2,
                f"detector noise\nfloor \u00b1{args.servo_noise_floor:g} px ",
                color=ORANGE, fontsize=fk.FS_SMALL, ha="right", va="center",
                linespacing=1.2)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["before servo", "after servo"])
    ax.set_xlim(-0.55, 1.62)
    ax.set_ylim(0, max(v for p in per.values() for v in p.values()) * 1.22)
    ax.set_ylabel("image-space alignment error (pixels)")
    fk.declutter(ax)
    ax.text(0.0, -0.155,
            fk.wrap("Measured endpoints only. No per-iteration servo log was "
                    "recorded, so no trajectory between these points is "
                    "claimed. The tolerance sits inside the detector noise "
                    "floor; see Section 7.6.", 92),
            transform=ax.transAxes, fontsize=fk.FS_SMALL, color=MUTED,
            ha="left", va="top", linespacing=1.3)
    fk.resolve_collisions(fig, labelled)
    return fk.save(fig, out, "fig_7_1_servo_endpoints")

def fig_energy(root, out, args):
    rows = _need(root, "energy_inventory.csv", "energy inventory")
    if not rows:
        raise DataProblem(
            "energy_inventory.csv is header-only: no measured or estimated "
            "energy value exists anywhere in the repository. Figures 10.2 and "
            "10.3 cannot be built from project data, and Table 10.1 cannot be "
            "populated. Either measure the workstation and robot draw, or "
            "state in Section 10.1.2 that the inventory rests entirely on "
            "published per-query estimates and cite them.")
    c_st = fk.pick_column(rows, "stage", "component", label="stage")
    c_e = fk.pick_column(rows, "energy_wh", "energy", "wh", label="energy_Wh")
    c_k = fk.pick_column(rows, "kind", "measured", "source_kind",
                         required=False)

    pairs = [(r[c_st], fk.to_float(r[c_e]),
              r[c_k] if c_k else "") for r in rows]
    pairs = [p for p in pairs if np.isfinite(p[1])]
    if not pairs:
        raise DataProblem("energy_inventory.csv has rows but no numeric "
                          "energy_Wh values")
    pairs.sort(key=lambda p: -p[1])
    st, en, kinds = zip(*pairs)

    fig = fk.new_figure(fk.COL_W, 0.34 * len(st) + 1.7)
    ax = fig.add_subplot(111)
    cols = [BLUE if "meas" in str(k).lower() else SKY for k in kinds]
    y = np.arange(len(st))
    ax.barh(y, en, height=0.62, color=cols, edgecolor="white", linewidth=0.6,
            zorder=3)
    tot = sum(en)
    for yy, v in zip(y, en):
        ax.text(v * 1.02, yy, f"{v:.3g} Wh  ({v/tot*100:.0f}%)", va="center",
                ha="left", fontsize=fk.FS_SMALL, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(st, fontsize=fk.FS_SMALL)
    ax.invert_yaxis()
    ax.set_xlabel("energy per instruction-conditioned grasp attempt (Wh)")
    ax.set_xlim(0, max(en) * 1.42)
    fk.declutter(ax, xgrid=True, ygrid=False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(handles=[mpatches.Patch(color=BLUE, label="measured"),
                       mpatches.Patch(color=SKY, label="published estimate")],
              loc="lower right")
    return fk.save(fig, out, "fig_10_2_energy_by_stage")

def fig_carbon(root, out, args):
    rows = _need(root, "energy_inventory.csv", "energy inventory")
    if not rows:
        raise DataProblem(
            "energy_inventory.csv is header-only, so carbon per functional "
            "unit cannot be computed from project data. See the note under "
            "--figure energy.")
    c_e = fk.pick_column(rows, "energy_wh", "energy", "wh", label="energy_Wh")
    total_wh = sum(v for v in (fk.to_float(r[c_e]) for r in rows)
                   if np.isfinite(v))
    if total_wh <= 0:
        raise DataProblem("no numeric energy_Wh values to total")
    kwh = total_wh / 1000.0

    gi = np.linspace(10, 720, 300)
    fig = fk.new_figure(fk.COL_W, 2.9)
    ax = fig.add_subplot(111)
    ax.plot(gi, kwh * gi * 1000.0, color=INK, lw=1.3, zorder=3)
    for x, lab, col in [(10, "lowest-carbon grid", GREEN),
                        (708, "highest-carbon grid", RED)]:
        ax.axvline(x, color=col, lw=0.8, ls=(0, (3, 2)), zorder=2)
        ax.annotate(f"{lab}\n{x:g} g/kWh \u2192 {kwh*x*1000:.2f} mg",
                    xy=(x, kwh * x * 1000.0),
                    xytext=(8 if x < 400 else -8, 10),
                    textcoords="offset points",
                    ha="left" if x < 400 else "right", va="bottom",
                    fontsize=fk.FS_SMALL, color=col)
    ax.set_xlabel("grid carbon intensity (g CO\u2082e per kWh)")
    ax.set_ylabel("carbon per attempt (mg CO\u2082e)")
    ax.set_xlim(0, 760)
    ax.set_ylim(0, None)
    fk.declutter(ax)
    ax.text(0.985, 0.04, f"energy per functional unit: {total_wh:.4g} Wh",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=fk.FS_SMALL, color=MUTED)
    return fk.save(fig, out, "fig_10_3_carbon_sensitivity")

# ==========================================================================
# IMAGE-BASED FIGURES  (real captures, annotated)
# ==========================================================================

def _mask_bbox(mask, pad=14, aspect=None):
    """
    Bounding box of a mask, optionally grown to a target width/height ratio.

    Matching the source aspect keeps a magnified crop the same shape as the
    full-frame panels beside it, so the filmstrip stays on one baseline.
    """
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    H, W = mask.shape
    x0, y0 = max(int(xs.min()) - pad, 0), max(int(ys.min()) - pad, 0)
    x1, y1 = min(int(xs.max()) + pad, W - 1), min(int(ys.max()) + pad, H - 1)
    if aspect:
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        if cw / ch < aspect:                      # too tall, widen
            need = int(round(ch * aspect)) - cw
            x0 = max(x0 - need // 2, 0)
            x1 = min(x0 + int(round(ch * aspect)) - 1, W - 1)
            x0 = max(min(x0, x1 - int(round(ch * aspect)) + 1), 0)
        else:                                     # too wide, heighten
            need = int(round(cw / aspect)) - ch
            y0 = max(y0 - need // 2, 0)
            y1 = min(y0 + int(round(cw / aspect)) - 1, H - 1)
            y0 = max(min(y0, y1 - int(round(cw / aspect)) + 1), 0)
    return (x0, y0, x1, y1)


def _panel(ax, rgb, title):
    ax.imshow(rgb)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(RULE); s.set_linewidth(0.7)
    ax.set_title(title, fontsize=fk.FS_ANNOT, color=MUTED, pad=3)


def _tag(ax, text, colour=INK, loc="lower left"):
    va, ha = ("bottom", "left") if "lower" in loc else ("top", "left")
    x, y = (0.025, 0.03) if "lower" in loc else (0.025, 0.97)
    if "right" in loc:
        x, ha = 0.975, "right"
    return ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va,
                   fontsize=fk.FS_SMALL, color="white", zorder=6,
                   bbox=dict(boxstyle="round,pad=0.30", fc=colour, ec="none",
                             alpha=0.86))


def fig_stages(root, out, args):
    """
    One real capture carried through the perception stages.

    Four panels on the same photograph, differing only in what is drawn over
    it: the capture and its instruction; the object-level mask; the part-level
    mask against the object mask, with measured coverage; and a magnified crop
    of the nominated region. Panels share one image so the reader compares
    overlays, not scenes - which is the whole argument of Chapter 5.
    """
    rgb_spec, obj_spec, part_spec, query = _resolve_capture(root, args)
    rgb = fk.load_array(root, rgb_spec)
    if rgb.ndim == 2:
        rgb = np.dstack([rgb] * 3)
    if rgb.dtype != np.uint8:
        rgb = (255 * (rgb - rgb.min()) /
               max(float(rgb.max() - rgb.min()), 1e-9)).astype(np.uint8)
    m_obj = _load_mask(root, obj_spec)
    m_part = _load_mask(root, part_spec)
    if m_obj.shape != rgb.shape[:2] or m_part.shape != rgb.shape[:2]:
        raise DataProblem(f"shape mismatch: rgb {rgb.shape[:2]}, "
                          f"object {m_obj.shape}, part {m_part.shape}")

    cov = m_part.sum() / max(m_obj.sum(), 1)
    print(f"    coverage = {cov:.3f}  (part {int(m_part.sum())} px / "
          f"object {int(m_obj.sum())} px)")

    h, w = rgb.shape[:2]
    fig = fk.new_figure(fk.COL_W, fk.COL_W / 4 * (h / w) * 1.18 + 0.72)
    axes = fig.subplots(1, 4)

    # (a) the capture and the instruction
    _panel(axes[0], rgb, "(a) capture and instruction")
    if query:
        _tag(axes[0], f'"{fk.wrap(query, 26)}"')

    # (b) object-level query: filled, because extent is the point here
    ov = rgb.copy()
    ov[m_obj] = (0.55 * ov[m_obj] +
                 0.45 * np.array([0, 114, 178])).astype(np.uint8)
    _panel(axes[1], ov, "(b) object query")
    fk.mask_contour(axes[1], m_obj, colour=BLUE)
    _tag(axes[1], f"{int(m_obj.sum())} px", BLUE)

    # (c) both outlines, unfilled: the overlap is the finding
    _panel(axes[2], rgb, "(c) part against object query")
    fk.mask_contour(axes[2], m_part, whole_mask=m_obj, colour=ORANGE)
    _tag(axes[2], f"coverage {cov*100:.0f}%",
         RED if cov > 0.75 else GREEN, loc="lower right")

    # (d) magnified crop of the nominated region
    bb = _mask_bbox(m_part, pad=max(6, int(0.04 * w)), aspect=w / h)
    if bb:
        x0, y0, x1, y1 = bb
        _panel(axes[3], rgb[y0:y1 + 1, x0:x1 + 1], "(d) nominated region")
        axes[3].contour(m_part[y0:y1 + 1, x0:x1 + 1], levels=[0.5],
                        colors=[ORANGE], linewidths=1.4, linestyles="dashed")
        # show the crop window back on panel (c)
        axes[2].add_patch(mpatches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0, facecolor="none", edgecolor=INK,
            linewidth=0.9, linestyle=(0, (3, 2)), zorder=7))
        _tag(axes[3], f"{x1-x0+1}x{y1-y0+1} px", INK)
    else:
        _panel(axes[3], rgb, "(d) nominated region")
        axes[3].text(0.5, 0.5, "part mask empty", transform=axes[3].transAxes,
                     ha="center", va="center", fontsize=fk.FS_ANNOT,
                     color=RED)

    fig.legend(handles=[
        Line2D([], [], color=BLUE, lw=1.3, label="object query"),
        Line2D([], [], color=ORANGE, lw=1.3, ls="--", label="part query"),
        Line2D([], [], color=INK, lw=0.9, ls=(0, (3, 2)), label="crop window"),
    ], loc="outside lower center", ncol=3)
    stem = args.stem or f"fig_5_1_stages_{args.capture_id or 'capture'}"
    return fk.save(fig, out, stem)


def fig_gallery(root, out, args):
    """
    Every indexed capture as a contact sheet with its measured coverage.

    Useful as an appendix figure and as a sanity check that the masks pair
    correctly with their images before any of them is used in the body.
    """
    rows = fk.load_table(root, "figure_data/captures_index.csv",
                         "captures_index.csv", label="captures index")
    if not rows:
        raise DataProblem("figure_data/captures_index.csv not found")
    c_id = fk.pick_column(rows, "capture_id", label="capture_id")
    c_rgb = fk.pick_column(rows, "rgb_path", label="rgb_path")
    c_om = fk.pick_column(rows, "object_mask_path", label="object_mask_path")
    c_pm = fk.pick_column(rows, "part_mask_path", label="part_mask_path")
    c_ob = fk.pick_column(rows, "object", required=False)
    c_cit = fk.pick_column(rows, "citable", required=False)

    items = []
    for r in rows:
        try:
            rgb = fk.load_array(root, r[c_rgb])
            mo = _load_mask(root, r[c_om])
            mp = _load_mask(root, r[c_pm])
        except Exception as e:
            print(f"    ! {r[c_id]}: {e}")
            continue
        if rgb.ndim == 2:
            rgb = np.dstack([rgb] * 3)
        items.append((r[c_id], r.get(c_ob, ""), rgb, mo, mp,
                      fk.truthy(r[c_cit]) if c_cit else True))
    if not items:
        raise DataProblem("no capture in the index could be loaded")

    ncol = min(4, len(items))
    nrow = int(np.ceil(len(items) / ncol))
    h, w = items[0][2].shape[:2]
    fig = fk.new_figure(fk.COL_W,
                        (fk.COL_W / ncol) * (h / w) * nrow * 1.16 + 0.55)
    axes = np.atleast_1d(fig.subplots(nrow, ncol)).ravel()
    for ax in axes:
        ax.set_axis_off()
    for ax, (cid, obj, rgb, mo, mp, cit) in zip(axes, items):
        ax.set_axis_on()
        cov = mp.sum() / max(mo.sum(), 1)
        _panel(ax, rgb, f"{obj or cid}")
        ax.contour(mo, levels=[0.5], colors=[BLUE], linewidths=1.0)
        ax.contour(mp, levels=[0.5], colors=[ORANGE], linewidths=1.0,
                   linestyles="dashed")
        _tag(ax, f"{cov*100:.0f}%", RED if cov > 0.75 else GREEN,
             loc="lower right")
        if not cit:
            _tag(ax, "not citable", RED, loc="upper left")
    return fk.save(fig, out, "fig_appendix_capture_gallery")


# ==========================================================================
# ASSET BUNDLES  (figure_assets/FIGURE_ASSETS.csv)
# ==========================================================================

# The dissertation text is authoritative on figure numbering. Claude Code
# keyed FIGURE_ASSETS.csv from the script filenames
# (fig_5_4_isolated_vs_cluttered.py / fig_5_5_mug_fragmentation.py), which are
# the reverse of the text. Remap on read so a builder never pulls a real
# capture under the wrong caption.
BUNDLE_ID = {
    "5.4": "5.5",   # text 5.4 = mug fragmentation  -> CSV row 5.5
    "5.5": "5.4",   # text 5.5 = isolated/cluttered -> CSV row 5.4
}


def bundle_for(assets, figure_id):
    """Assets for a text figure number, honouring the known ID swap."""
    key = BUNDLE_ID.get(figure_id, figure_id)
    if key != figure_id:
        print(f"    figure {figure_id} (text numbering) reads bundle "
              f"{key} (script numbering)")
    return assets.get(key, {})


def load_assets(root):
    """
    figure_id -> {capture_id -> {role -> (path, npz_key, citable, caption)}}

    FIGURE_ASSETS.csv is the authority on which file each figure draws. A row
    with an empty asset_path is a recorded gap, not an oversight, and is kept
    so the builder can render the gap rather than quietly omitting the object.
    """
    rows = fk.load_table(root, "figure_assets/FIGURE_ASSETS.csv",
                         "FIGURE_ASSETS.csv", label="figure assets")
    if not rows:
        return {}
    c_fig = fk.pick_column(rows, "figure_id", label="figure_id")
    c_role = fk.pick_column(rows, "role", label="role")
    c_path = fk.pick_column(rows, "asset_path", label="asset_path")
    c_key = fk.pick_column(rows, "npz_key", required=False)
    c_cap = fk.pick_column(rows, "capture_id", required=False)
    c_cit = fk.pick_column(rows, "citable", required=False)
    c_frag = fk.pick_column(rows, "caption_fragment", required=False)

    out, gaps = {}, 0
    for r in rows:
        fid = r[c_fig].strip()
        cid = (r[c_cap].strip() if c_cap else "") or r[c_path].strip()
        rec = out.setdefault(fid, {}).setdefault(cid, {})
        if not r[c_path].strip():
            gaps += 1
        rec[r[c_role].strip()] = dict(
            path=r[c_path].strip(),
            key=(r[c_key].strip() if c_key else ""),
            citable=fk.truthy(r[c_cit]) if c_cit else True,
            caption=(r[c_frag].strip() if c_frag else ""))
    print(f"    assets for {len(out)} figures; {gaps} recorded gap(s)")
    return out


def _asset_array(root, rec, role):
    """Load one asset by role, honouring the npz member key."""
    a = rec.get(role)
    if not a or not a["path"]:
        return None
    spec = a["path"] + (f"::{a['key']}" if a["key"] else "")
    try:
        return fk.load_array(root, spec)
    except Exception as e:
        print(f"    ! {role} {a['path']}: {e}")
        return None


def _asset_masks(root, rec):
    """(rgb, object_mask, part_mask) for one capture bundle."""
    rgb = _asset_array(root, rec, "rgb")
    if rgb is None:
        return None, None, None
    if rgb.ndim == 2:
        rgb = np.dstack([rgb] * 3)
    if rgb.dtype != np.uint8:
        rgb = (255 * (rgb - rgb.min()) /
               max(float(rgb.max() - rgb.min()), 1e-9)).astype(np.uint8)
    def _m(role):
        a = _asset_array(root, rec, role)
        if a is None:
            return None
        a = np.squeeze(a)
        if a.ndim == 3:
            a = a[..., 0]
        return a if a.dtype == bool else a > (0.5 if float(a.max()) <= 1 else 127)
    return rgb, _m("object_mask"), _m("part_mask")


# ==========================================================================
# CLI
# ==========================================================================

BUILDERS = {
    "envelope":    fig_envelope,
    "trials":      fig_trials,
    "corrections": fig_corrections,
    "constraint":  fig_constraint,
    "baseplace":   fig_baseplace,
    "overlay":     fig_overlay,
    "coverage":      fig_coverage,
    "fragmentation": fig_fragmentation,
    "clutter":       fig_clutter,
    "grid":          fig_grid,
    "handover":      fig_handover,
    "agreement":     fig_agreement,
    "servo":         fig_servo,
    "energy":        fig_energy,
    "carbon":        fig_carbon,
    "stages":        fig_stages,
    "gallery":       fig_gallery,
}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Build AffordGrasp dissertation figures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument("--out", default="report_assets/figures_generated")
    ap.add_argument("--bundle", default="report_bundle_20260801_1611",
                    help="authoritative report bundle folder")
    ap.add_argument("--figure", choices=sorted(BUILDERS), action="append")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--components", help="explicit components CSV")
    ap.add_argument("--trials-csv", help="explicit trials CSV to use")
    ap.add_argument("--trial-ids",
                    help="comma-separated ids, e.g. 1,2,3,4,5,6,7,9,10,11,12")

    ap.add_argument("--servo-tolerance", type=float, default=20.0)
    ap.add_argument("--servo-noise-floor", type=float, default=10.0)

    ap.add_argument("--reach", type=float, default=0.633)
    ap.add_argument("--d-before", type=float, default=0.670)
    ap.add_argument("--d-after", type=float, default=0.412)
    ap.add_argument("--keepout", type=float, default=0.320)

    ap.add_argument("--capture-id", help="id from figure_data/captures_index.csv")
    ap.add_argument("--rgb"); ap.add_argument("--object-mask")
    ap.add_argument("--part-mask"); ap.add_argument("--query")
    ap.add_argument("--stem")
    args = ap.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    if not root.exists():
        sys.exit(f"root does not exist: {root}")

    fk.use_style()
    names = sorted(BUILDERS) if args.all else (args.figure or [])
    if not names:
        ap.error("choose --all or at least one --figure")

    print(f"root: {root}\nout : {out}\n")
    failed = []
    for name in names:
        print(f"[{name}]")
        try:
            BUILDERS[name](root, out, args)
        except DataProblem as e:
            print(f"    SKIPPED: {e}")
            failed.append(name)
        except Exception as e:
            print(f"    ERROR: {type(e).__name__}: {e}")
            failed.append(name)
        print()
    print("done." + (f" incomplete: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
