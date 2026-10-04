"""Fig 3.3 -- Two-machine deployment architecture (Class S, schematic).

Evidence: codex/CODEX.md sec 1 ("Two machines" paragraph) and sec 2 (DEMO_RUNBOOK.md
command sequence, reproduced verbatim there), cross-checked directly against
DEMO_RUNBOOK.md in this session. Both independently agree on every fact drawn below.

  PC = Windows, CUDA .venv, no ROS -- reasoning, grounding, part selection,
    grasp generation, closure-parameter computation (all PC-side scripts below
    confirmed LIVE in codex/CODEX.md sec 3).
  Workstation = ROS Noetic, real HSR attached -- capture, grasp/placement
    selection, preflight validation, base placement, visual servo, gripper
    closure + lift (all workstation-side, run over ssh per DEMO_RUNBOOK.md;
    codex/CODEX.md sec 9 notes several of these scripts exist only in this
    PC-side snapshot's backup folder, not at the workstation root -- drawn
    here as the STAGE the runbook actually executes there, not as a specific
    file guaranteed present workstation-side).
  Transfer mechanism: scp of files, NOT a live ROS/message connection between
    machines (DEMO_RUNBOOK.md's own command sequence, verbatim):
    workstation -> PC:  head_capture_real.npz
    PC -> workstation:  grasps_plain.npz, fused_cloud.npz, close_params.csv
  CORRECTION vs the design brief: the brief listed constraints.json as one of
  the files crossing the boundary. DEMO_RUNBOOK.md's actual scp command lists
  only grasps_plain.npz, fused_cloud.npz and close_params.csv -- constraints.json
  is written on the PC (run_grounding_grasp.py) and consumed on the PC
  (grasp_close_params.py); it does not cross the boundary. Drawn accordingly
  (constraints.json shown as a PC-internal artefact only).
  Closed loop: hsr_final_center.py, called with --tol_px/--probe/--max_step
  (DEMO_RUNBOOK.md line 137/sec2) -- an iterative image-space servo, confirmed
  closed-loop and workstation-side. Every other stage is called once per run
  (staged/one-shot) -- confirmed by the runbook's own single-invocation
  command list; no stage other than the servo is re-invoked in a loop.
  Security: no IP address, hostname or credential from DEMO_RUNBOOK.md is
  reproduced here (both appear in that file; both are deliberately omitted).

Run: python figures/dissertation/fig_3_3_deployment.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

import _qa as qa
import _style as fs

FIGURE_ID = "fig_3_3_deployment"

FIG_W_IN, FIG_H_IN = fs.TEXT_WIDTH_IN, 7.7

PC = fs.OKABE_ITO["blue"]
WS = fs.OKABE_ITO["vermillion"]
LOOP = fs.OKABE_ITO["green"]
INK = "black"
MUTED = "#595959"

INTENT = ("The pipeline runs on two machines connected only by staged file transfer (scp), not a "
          "live connection; one stage -- visual servo -- is a closed loop, and it runs entirely on "
          "the workstation side that talks to the real robot.")

CAPTION = (
    "Fig 3.3. Two-machine deployment architecture, as run (DEMO_RUNBOOK.md). PC (Windows, CUDA, "
    "no ROS): reasoning, grounding, part selection, grasp generation, closure-parameter "
    "computation. Workstation (ROS Noetic, real HSR attached): capture, grasp/placement "
    "selection, preflight validation, base placement, visual servo, gripper closure and lift. "
    "The two machines exchange files by scp, not a live message connection: head_capture_real.npz "
    "workstation-to-PC; grasps_plain.npz, fused_cloud.npz and close_params.csv PC-to-workstation. "
    "constraints.json is written and consumed on the PC only and does not cross the boundary. "
    "Every stage runs once per grasp attempt except visual servo (green loop icon), which iterates "
    "a closed loop -- image-space error, online Broyden-Jacobian update, re-servo -- until its "
    "pixel-error tolerance is met, entirely within the workstation/HSR side."
)


def box(ax, cx, cy, w, h, title, subtitle=None, fs_title=7.6, fs_sub=6.6, edge=INK):
    b = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                        boxstyle="round,pad=0.010,rounding_size=0.035",
                        facecolor="white", edgecolor=edge, linewidth=1.1, zorder=5)
    ax.add_patch(b)
    if subtitle:
        ax.text(cx, cy + h * 0.20, title, ha="center", va="center", fontsize=fs_title,
                 fontweight="medium", color=INK, zorder=6)
        ax.text(cx, cy - h * 0.26, subtitle, ha="center", va="center", fontsize=fs_sub,
                 style="italic", color=MUTED, zorder=6)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=fs_title,
                 fontweight="medium", color=INK, zorder=6)
    return cx - w / 2, cy - h / 2, w, h


def band(ax, x0, y0, w, h, colour, name, sub):
    bg = FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.01,rounding_size=0.05",
                         facecolor=colour, alpha=0.06, edgecolor=colour, linewidth=1.3, zorder=1)
    ax.add_patch(bg)
    ax.text(x0 + 0.10, y0 + h - 0.14, name, ha="left", va="top", fontsize=12,
             fontweight="bold", color=colour, zorder=2)
    ax.text(x0 + 0.10, y0 + h - 0.38, sub, ha="left", va="top", fontsize=7.6,
             style="italic", color=MUTED, zorder=2)
    return x0, y0, w, h


def varrow(ax, x, y0, y1, colour=INK, lw=1.1, mscale=8):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=mscale,
                                  color=colour, linewidth=lw, zorder=4))


def build():
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), facecolor="white", constrained_layout=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W_IN); ax.set_ylim(0, FIG_H_IN)
    ax.set_aspect("equal")
    ax.axis("off")

    PC_X, PC_W = 0.20, 2.85
    WS_X, WS_W = 3.25, 2.82
    TOP, BOT = 7.55, 0.20

    band(ax, PC_X, BOT, PC_W, TOP - BOT, PC, "PC", "Windows, CUDA .venv, no ROS")
    band(ax, WS_X, BOT, WS_W, TOP - BOT, WS, "WORKSTATION", "ROS Noetic, real HSR attached")

    pc_cx = PC_X + PC_W / 2
    ws_cx = WS_X + WS_W / 2

    top_row_y = 6.85

    # ---- workstation: capture (top row, mirrors PC's first stage height) ----
    box(ax, ws_cx, top_row_y, 2.40, 0.46, "Capture", "capture_object.py / capture_pair.py")

    # ---- transfer 1: workstation -> PC ----
    ax.add_patch(FancyArrowPatch((WS_X, top_row_y), (PC_X + PC_W, top_row_y), arrowstyle="-|>",
                                  mutation_scale=10, color=INK, linewidth=1.3, zorder=4))
    ax.text((PC_X + PC_W + WS_X) / 2, top_row_y + 0.20, "scp:\nhead_capture_real.npz",
             fontsize=6.9, ha="center", color=INK, fontweight="bold", linespacing=1.2)

    # ---- PC stages: 6, evenly spaced ----
    pc_y = [top_row_y - 0.60 - i * 0.60 for i in range(6)]
    pc_specs = [
        ("Reasoning", "affordance_reasoning.py (GPT-4o)"),
        ("Grounding", "visual_grounding.py (LangSAM)"),
        ("Part selection", "part_adaptive.py"),
        ("Grasp generation", "grasp_generation.py (Contact-GraspNet)"),
        ("Closure parameters", "grasp_close_params.py + grasp_policy.py"),
        ("Export", "export_grasps_plain.py"),
    ]
    pc_boxes = []
    for y, (title, sub) in zip(pc_y, pc_specs):
        pc_boxes.append(box(ax, pc_cx, y, 2.60, 0.46, title, sub))
    for y_a, y_b in zip(pc_y[:-1], pc_y[1:]):
        varrow(ax, pc_cx, y_a - 0.23, y_b + 0.23)
    # capture -> reasoning
    varrow(ax, pc_cx, top_row_y - 0.23, pc_y[0] + 0.23)

    # constraints.json -- PC-internal only, does not cross the boundary
    # (correction vs the design brief -- see script docstring).
    cj_x = pc_cx - 1.55
    ax.add_patch(FancyArrowPatch((cj_x, pc_y[0] - 0.02), (cj_x, pc_y[4] + 0.02),
                                  arrowstyle="-", color=MUTED, linewidth=1.0,
                                  linestyle=(0, (2, 2)), zorder=3))
    ax.text(cj_x - 0.08, (pc_y[0] + pc_y[4]) / 2, "constraints.json\n(PC-internal,\nnever crosses)",
             fontsize=6.1, color=MUTED, ha="right", va="center", style="italic", linespacing=1.2)

    # ---- transfer 2: PC -> workstation (aligned with PC's last stage) ----
    xfer_y = pc_y[-1] - 0.36
    ax.add_patch(FancyArrowPatch((PC_X + PC_W, xfer_y), (WS_X, xfer_y), arrowstyle="-|>",
                                  mutation_scale=10, color=INK, linewidth=1.3, zorder=4))
    ax.text((PC_X + PC_W + WS_X) / 2, xfer_y + 0.30,
             "scp: grasps_plain.npz\nfused_cloud.npz\nclose_params.csv", fontsize=6.7,
             ha="center", color=INK, fontweight="bold", linespacing=1.2)
    varrow(ax, pc_cx, pc_y[-1] - 0.23, xfer_y + 0.05, colour=INK, lw=1.1)

    # ---- workstation execution stages (below transfer 2) ----
    ws_y = [xfer_y - 0.55 - i * 0.62 for i in range(5)]
    ws_specs = [
        ("Grasp selection", "pick_grasp.py"),
        ("Preflight validation", "8 offline GO/NO-GO checks"),
        ("Base placement", "execute_place_grasp_raw \u2013\u2013stage base"),
        ("Visual servo", "hsr_final_center.py -- empirical Jacobian"),
        ("Closure + lift", "execute_place_grasp_raw \u2013\u2013stage grasp"),
    ]
    ws_boxes = []
    for i, (y, (title, sub)) in enumerate(zip(ws_y, ws_specs)):
        edge = LOOP if title == "Visual servo" else INK
        ws_boxes.append(box(ax, ws_cx, y, 2.60, 0.48, title, sub, edge=edge))
    varrow(ax, ws_cx, xfer_y - 0.05, ws_y[0] + 0.24)
    for y_a, y_b in zip(ws_y[:-1], ws_y[1:]):
        varrow(ax, ws_cx, y_a - 0.24, y_b + 0.24)

    # closed-loop icon on Visual servo -- a small return arrow to its own right edge.
    servo_x, servo_y, servo_w, servo_h = ws_boxes[3]
    loop_cx = servo_x + servo_w + 0.30
    loop_cy = servo_y + servo_h / 2
    ax.add_patch(Circle((loop_cx, loop_cy), 0.001, alpha=0))  # anchor, no-op
    ax.annotate("", xy=(servo_x + servo_w, loop_cy + 0.10), xytext=(loop_cx, loop_cy + 0.16),
                arrowprops=dict(arrowstyle="-|>", color=LOOP, lw=1.4,
                                 connectionstyle="arc3,rad=-1.3"))
    ax.text(loop_cx + 0.05, loop_cy, "closed\nloop", fontsize=6.3, color=LOOP, fontweight="bold",
             ha="left", va="center", linespacing=1.1)

    # ---- HSR ----
    hsr_y = ws_y[-1] - 0.55
    box(ax, ws_cx, hsr_y, 2.20, 0.42, "Toyota HSR", "ROS Noetic, real hardware", edge=WS)
    varrow(ax, ws_cx, ws_y[-1] - 0.24, hsr_y + 0.21, colour=WS)

    return fig


if __name__ == "__main__":
    print(f"[{FIGURE_ID}] INTENT: {INTENT}")
    fig = build()
    qa.check(fig, FIGURE_ID, width_class=fs.TEXT_WIDTH_IN)
    qa.check_labels_complete(fig, FIGURE_ID)
    paths = fs.save_figure(fig, FIGURE_ID)
    plt.close(fig)
    qa.check_output_files(FIGURE_ID)
    report_path = qa.write_report("B")
    print(f"[{FIGURE_ID}] wrote: {paths}")
    print(f"[{FIGURE_ID}] caption:\n{CAPTION}")
    print(f"[{FIGURE_ID}] QA report: {report_path}")
