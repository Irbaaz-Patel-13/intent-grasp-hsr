"""Fig 3.1 -- System architecture and data flow (Class S, schematic, no photo/3D).

Verified against the live repository (run_grounding_grasp.py, visual_grounding.py,
grasp_generation.py, grasp_policy.py, grasp_close_params.py, part_adaptive.py,
affordance_reasoning.py, config.py, DEMO_RUNBOOK.md) -- see the accompanying
evidence report (printed by this script and given in the session's final
report) for exact citations. Corrections made relative to the design brief
this script implements are documented inline below at each corrected point.

Run: python figures/dissertation/fig_3_1_system_architecture.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import _qa as qa
import _style as fs

FIGURE_ID = "fig_3_1_system_architecture"

FIG_W_IN, FIG_H_IN = fs.TEXT_WIDTH_IN, 6.30

REASON = fs.OKABE_ITO["blue"]
GROUND = fs.OKABE_ITO["orange"]
GRASP = fs.OKABE_ITO["green"]
EXECUTE = fs.OKABE_ITO["vermillion"]   # corrected from the brief's "purple": _style.py's
                                        # own pre-existing SEMANTIC_COLOUR (its docstring
                                        # states it was "Set by Fig 3.1" and is reused by
                                        # every later figure) maps robot_control->vermillion,
                                        # verification->purple. Base placement/servo/closure
                                        # are robot_control; only the final artefact is
                                        # verification -- so the band is vermillion and only
                                        # the terminal "verified z-rise" arrow/label is purple.
VERIFY = fs.OKABE_ITO["purple"]
INK = "black"
MUTED = "#595959"

INTENT = ("An instruction that never names its target becomes a verified physical grasp "
          "through four bands; the reasoning layer nominates a part, perception must locate "
          "it, and a second constraint path reaches the gripper without passing through "
          "perception at all.")

CAPTION = (
    "Fig 3.1. System architecture and data flow, as implemented. Read left to right, top row "
    "then bottom row. An instruction that names no object (\"I'd like a hot drink\") and a "
    "single RGB-D capture enter Reasoning, which emits structured JSON constraints "
    "(target_object, target_part, keep_clear, post_grasp_motion, stability_priority, "
    "thermal_or_hygiene). Reason and Ground are adjacent by design: the part is nominated in "
    "Reason and must be located in Ground, the boundary this dissertation's evaluation is "
    "built around. Grounding chains open-set detection and promptable segmentation (Fig 2.1) "
    "to return an affordance mask and its 3D centre. Grasp decomposes the isolated object "
    "into components and binds the requested part to one of them -- using both the grounded "
    "region and, independently, the target_part/keep_clear strings matched against component "
    "geometry -- then generates and ranks Contact-GraspNet candidates by quality over distance "
    "to the affordance centre. Execute places the base, validates the candidate, closes an "
    "image-space error with an online visual servo, and closes the gripper; success is a "
    "verified depth-measured z-rise, not a reachability flag. A second path leaves the JSON "
    "constraints directly for the closure stage -- stability_priority, post_grasp_motion and "
    "thermal_or_hygiene set force level, close depth and post-grasp behaviour with no further "
    "model call, entirely bypassing perception. This is the implemented architecture; the "
    "portfolio architecture and physical deployment topology are Figs 3.2 and 3.3."
)


def box(ax, cx, cy, w, h, title, subtitle=None, edge=INK, fill="white", fs_title=8.3, fs_sub=7.0):
    b = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                        boxstyle="round,pad=0.012,rounding_size=0.045",
                        facecolor=fill, edgecolor=edge, linewidth=1.1, zorder=5)
    ax.add_patch(b)
    if subtitle:
        ax.text(cx, cy + h * 0.14, title, ha="center", va="center", fontsize=fs_title,
                 fontweight="medium", color=INK, zorder=6)
        ax.text(cx, cy - h * 0.28, subtitle, ha="center", va="center", fontsize=fs_sub,
                 style="italic", color=MUTED, zorder=6)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=fs_title,
                 fontweight="medium", color=INK, zorder=6)
    return cx - w / 2, cy - h / 2, w, h


def band(ax, x0, y0, w, h, colour, name):
    bg = FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.01,rounding_size=0.05",
                         facecolor=colour, alpha=0.07, edgecolor=colour, linewidth=1.3, zorder=1)
    ax.add_patch(bg)
    ax.text(x0 + 0.08, y0 + h - 0.10, name, ha="left", va="top", fontsize=10.5,
             fontweight="bold", color=colour, zorder=2)
    return x0, y0, w, h


def arrow(ax, p0, p1, colour=INK, lw=1.2, style="-|>", dashed=False, mscale=9):
    ls = (0, (3, 2)) if dashed else "solid"
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=mscale,
                                  color=colour, linewidth=lw, linestyle=ls, zorder=4))


def label(ax, x, y, text, colour=INK, fontsize=7.0, style_="normal", ha="center", va="center", weight="normal"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fontsize, color=colour,
             style=style_, fontweight=weight, zorder=6)


def build():
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor="white", constrained_layout=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W_IN); ax.set_ylim(0, FIG_H_IN)
    ax.set_aspect("equal")
    ax.axis("off")

    # ---------------------------------------------------------------- input
    label(ax, 1.55, 5.98, '"I\'d like a hot drink"', fontsize=10, weight="bold")
    label(ax, 1.55, 5.76, "instruction (names no object) + RGB-D capture (head camera)",
          fontsize=7, style_="italic", colour=MUTED)
    arrow(ax, (1.55, 5.66), (1.55, 5.10))

    # ---------------------------------------------------------------- row 1 bands
    R_X, R_Y, R_W, R_H = 0.15, 4.10, 2.80, 1.00
    G_X, G_Y, G_W, G_H = 3.35, 4.10, 2.77, 1.00
    band(ax, R_X, R_Y, R_W, R_H, REASON, "REASON")
    band(ax, G_X, G_Y, G_W, G_H, GROUND, "GROUND")

    reason_box = box(ax, R_X + R_W / 2, R_Y + R_H / 2 - 0.06, 2.52, 0.55,
                      "Reasoning", "GPT-4o, temperature 0")
    ground_box = box(ax, G_X + G_W / 2, G_Y + G_H / 2 - 0.06, 2.52, 0.55,
                      "Grounding", "object + part (GroundingDINO+SAM2, Fig 2.1)")

    rb_x, rb_y, rb_w, rb_h = reason_box
    gb_x, gb_y, gb_w, gb_h = ground_box
    arrow(ax, (rb_x + rb_w, rb_y + rb_h / 2), (gb_x, gb_y + gb_h / 2))
    label(ax, (rb_x + rb_w + gb_x) / 2, rb_y + rb_h / 2 + 0.15,
          "structured JSON\nconstraints", fontsize=7.0)

    # ---------------------------------------------------------------- row 2 bands
    P_X, P_Y, P_W, P_H = 0.15, 1.65, 2.80, 2.00
    E_X, E_Y, E_W, E_H = 3.35, 1.65, 2.77, 2.00
    band(ax, P_X, P_Y, P_W, P_H, GRASP, "GRASP")
    band(ax, E_X, E_Y, E_W, E_H, EXECUTE, "EXECUTE")

    # ---- Ground (row1) -> Grasp (row2): routed entirely through the empty
    # gap column between the two band columns (x in [2.95, 3.35]) so it never
    # crosses any band's fill. Kept HIGH in the row1/row2 corridor (close to
    # row1's own bottom edge) so the boundary annotation below has clear air.
    GAP_X = (R_X + R_W + G_X) / 2  # = 3.15, centre of the inter-column gap
    corridor_y = R_Y - 0.06  # just below row 1
    ax.add_patch(FancyArrowPatch((gb_x, gb_y + gb_h * 0.15), (GAP_X, gb_y + gb_h * 0.15),
                                  arrowstyle="-", color=INK, linewidth=1.2, zorder=3))
    ax.add_patch(FancyArrowPatch((GAP_X, gb_y + gb_h * 0.15), (GAP_X, corridor_y),
                                  arrowstyle="-", color=INK, linewidth=1.2, zorder=3))
    ax.add_patch(FancyArrowPatch((GAP_X, corridor_y), (0.70, corridor_y),
                                  arrowstyle="-", color=INK, linewidth=1.2, zorder=3))
    ax.add_patch(FancyArrowPatch((0.70, corridor_y), (0.70, P_Y + P_H),
                                  arrowstyle="-|>", mutation_scale=9, color=INK,
                                  linewidth=1.2, zorder=3))
    label(ax, GAP_X + 0.06, corridor_y + 0.14, "affordance mask \u2192\n3D affordance centre",
          fontsize=7.0, ha="left")

    # boundary annotation -- the dissertation's thesis, expressed structurally
    # (spec sec 3.7/3.9; only annotation of its kind). Placed low in the
    # corridor (just above row 2), centred on the true Reason/Ground seam
    # (GAP_X), well clear of the connector above it.
    label(ax, GAP_X, P_Y + P_H + 0.10, "part nominated here \u00b7 part must be located here",
          fontsize=7.4, weight="bold", colour=INK)

    # ---- Grasp band: 3 stages ----
    # Vertical budget from the band title down: title at P_Y+P_H-0.10; a fixed
    # 0.22 gap to the arrow-label row; a further 0.15 gap to the box tops --
    # keeps every label clear of the band-title text above it (was the cause
    # of a title/label collision in the previous pass).
    title_y = P_Y + P_H - 0.10
    above_y = title_y - 0.30
    box_half_h = 0.30
    stage_y = above_y - 0.15 - box_half_h
    sw, sgap = 0.72, 0.17
    sx = [P_X + 0.16 + sw / 2 + i * (sw + sgap) for i in range(3)]
    b_decomp = box(ax, sx[0], stage_y, sw, 0.60, "Decomposition\n+ part binding", None, fs_title=7.0)
    b_gen = box(ax, sx[1], stage_y, sw, 0.60, "Grasp\ngeneration (CGN)", None, fs_title=7.0)
    b_filt = box(ax, sx[2], stage_y, sw, 0.60, "Ranking +\nfiltering", None, fs_title=7.0)
    for a, b_ in [(b_decomp, b_gen), (b_gen, b_filt)]:
        ax.add_patch(FancyArrowPatch((a[0] + a[2], stage_y), (b_[0], stage_y),
                                      arrowstyle="-|>", mutation_scale=7, color=INK,
                                      linewidth=1.0, zorder=4))
    label(ax, (b_decomp[0] + b_decomp[2] + b_gen[0]) / 2, above_y,
          "component set\n+ bound part", fontsize=7.0)
    label(ax, (b_gen[0] + b_gen[2] + b_filt[0]) / 2, above_y,
          "25\ncandidates", fontsize=7.0)

    # target_part / keep_clear string bypass -- direct from Reasoning into part
    # binding, independent of the grounded mask (CORRECTION vs the design brief:
    # see script docstring / evidence report -- bind_part() consumes the raw
    # target_part string + keep_clear list matched against geometric component
    # names, a real second channel the brief's binary Architecture A/B framing
    # did not anticipate; it can override the mask-derived scoping when its own
    # match is confident, and falls back to the mask otherwise). Routed
    # straight down at x=0.55 -- clear of the boundary-annotation text (x=1.55)
    # and short, since Reason and Grasp share the same column and this arrow
    # only needs to cross the row1/row2 corridor, not the full band height.
    bypass_x = R_X + 0.40
    ax.add_patch(FancyArrowPatch((bypass_x, R_Y), (bypass_x, P_Y + P_H),
                                  arrowstyle="-|>", mutation_scale=8, color=REASON,
                                  linewidth=1.1, linestyle=(0, (3, 2)), zorder=3))
    label(ax, bypass_x - 0.06, (R_Y + P_Y + P_H) / 2, "target_part,\nkeep_clear\n(strings)",
          fontsize=7.0, colour=REASON, style_="italic", ha="right")

    # Grasp -> Execute (plain line here -- the arrowhead lives on the single
    # diagonal segment below that actually enters Base placement, avoiding a
    # double-arrowhead where the two segments meet).
    arrow(ax, (b_filt[0] + b_filt[2], stage_y), (E_X + 0.06, stage_y), style="-")
    label(ax, (b_filt[0] + b_filt[2] + E_X + 0.06) / 2, above_y,
          "surviving\ncandidates", fontsize=7.0)

    # ---- Execute band: 4 stages, 2x2 S-curve (base -> validation -> servo -> closure) ----
    # Same fixed-gap budget as the Grasp band above: title -> 0.22 gap -> label
    # row -> 0.15 gap -> row-1 box tops.
    ex_title_y = E_Y + E_H - 0.10
    ex_above_y = ex_title_y - 0.30
    ex_box_half_h = 0.275
    ex_row1_y = ex_above_y - 0.15 - ex_box_half_h
    ex_row2_y = E_Y + 0.55
    ew, egap = 1.16, 0.16
    ex1 = E_X + 0.15 + ew / 2
    ex2 = ex1 + ew + egap
    b_base = box(ax, ex1, ex_row1_y, ew, 0.55, "Base placement", None, fs_title=7.4)
    b_val = box(ax, ex2, ex_row1_y, ew, 0.55, "Validation", None, fs_title=7.4)
    b_servo = box(ax, ex1, ex_row2_y, ew, 0.55, "Visual servo", None, fs_title=7.4)
    b_close = box(ax, ex2, ex_row2_y, ew, 0.55, "Closure + lift", None, fs_title=7.4)

    arrow(ax, (b_base[0] + b_base[2], ex_row1_y), (b_val[0], ex_row1_y))
    label(ax, (b_base[0] + b_base[2] + b_val[0]) / 2, ex_above_y,
          "base pose\n(x, y, yaw)", fontsize=7.0)

    # Validation -> Visual servo: S-curve elbow (row1 right -> row2 left),
    # routed through the small mid-band gap so it does not cross Base placement.
    mid_y = (ex_row1_y - b_val[3] / 2 + ex_row2_y + b_servo[3] / 2) / 2
    ax.add_patch(FancyArrowPatch((ex2, ex_row1_y - b_val[3] / 2), (ex2, mid_y),
                                  arrowstyle="-", color=INK, linewidth=1.1, zorder=3))
    ax.add_patch(FancyArrowPatch((ex2, mid_y), (ex1, mid_y),
                                  arrowstyle="-", color=INK, linewidth=1.1, zorder=3))
    ax.add_patch(FancyArrowPatch((ex1, mid_y), (ex1, ex_row2_y + b_servo[3] / 2),
                                  arrowstyle="-|>", mutation_scale=7, color=INK,
                                  linewidth=1.1, zorder=3))
    label(ax, (ex1 + ex2) / 2, mid_y + 0.09, "validated config.", fontsize=7.0)

    arrow(ax, (b_servo[0] + b_servo[2], ex_row2_y), (b_close[0], ex_row2_y))
    label(ax, (b_servo[0] + b_servo[2] + b_close[0]) / 2, ex_row2_y - ex_box_half_h - 0.16,
          "joint\nvelocity", fontsize=7.0)

    # entry from Grasp band into Base placement (top of first stage)
    ax.add_patch(FancyArrowPatch((E_X + 0.06, stage_y), (b_base[0], ex_row1_y),
                                  arrowstyle="-|>", mutation_scale=7, color=INK,
                                  linewidth=1.0, zorder=4))

    # ---- verified output ----
    out_x = ex2 + 0.10
    arrow(ax, (out_x, ex_row2_y - b_close[3] / 2), (out_x, E_Y - 0.55), colour=VERIFY)
    label(ax, out_x + 0.02, E_Y - 0.70, "verified z-rise\n(depth-measured)", fontsize=7.0,
          weight="bold", colour=VERIFY, ha="left")

    # ---------------------------------------------------------------- constraint fork
    # stability_priority / post_grasp_motion / thermal_or_hygiene -> closure
    # parameters, no model call (grasp_policy.closure_policy, called from
    # grasp_close_params.py -- pure functions, no API/model import in that path).
    # CORRECTION vs the design brief: keep_clear is NOT part of this fork -- it
    # never reaches closure_policy's numeric branches or close_params.csv's
    # columns; it travels with target_part into part binding instead (the
    # dashed arrow above). Dropped from this label accordingly.
    # Routed along the LEFT MARGIN (x=0.05, strictly left of the Grasp band)
    # for its full vertical run, then along the bottom margin, entering
    # Closure + lift from the left of its bottom edge -- offset from the
    # verified-z-rise exit (right of the bottom edge) so the two never meet.
    fork_x0 = 0.05
    fork_y = 0.90
    close_in_x = ex2 - 0.20
    ax.add_patch(FancyArrowPatch((rb_x, R_Y), (fork_x0, R_Y),
                                  arrowstyle="-", color=REASON, linewidth=1.3, zorder=3))
    ax.add_patch(FancyArrowPatch((fork_x0, R_Y), (fork_x0, fork_y),
                                  arrowstyle="-", color=REASON, linewidth=1.3, zorder=3))
    ax.add_patch(FancyArrowPatch((fork_x0, fork_y), (close_in_x, fork_y),
                                  arrowstyle="-", color=REASON, linewidth=1.3, zorder=3))
    ax.add_patch(FancyArrowPatch((close_in_x, fork_y), (close_in_x, ex_row2_y - b_close[3] / 2),
                                  arrowstyle="-|>", mutation_scale=9, color=REASON,
                                  linewidth=1.3, zorder=3))
    label(ax, 3.10, fork_y - 0.22,
          "stability_priority, post_grasp_motion, thermal_or_hygiene\n"
          "\u2192 closure parameters \u00b7 no model call", fontsize=7.0,
          weight="bold", colour=REASON)

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("A")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
    print(f"[{FIGURE_ID}] -- communication check still required: view the PNG, blind-read it, "
          f"compare against INTENT, then call qa.record_communication_check(...).")
