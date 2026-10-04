"""
new_h_three_layer_limit.py -- NEW-H: The Three-Layer Limit.

Scientific claim: one object (mug), two real instructions -- one whose
reasoning-layer target_part resolves to a passing, executable component,
one whose target_part resolves to a component the evidence gate refuses.
The reasoning layer commits to a confident target_part string in both
cases; only the perception layer's real geometric measurement determines
whether execution is even attempted.

Instruction substitution (disclosed, not hidden): the brief's illustrative
left-column instruction ("Pour this out" -> body) has no real source --
every real pour-toned instruction found in this repo (constraints.json,
mug_condA_parts.json, constraints_pour.json) resolves target_part="handle",
not "body" (thematically expected: pouring needs the handle for tilt
control). The real instruction substituted here, "move this out of the
way" -> body -> main_body (ok), is q6_intent_mug.log's own real bind_part
result. The right column, "I'd like a hot drink" -> handle -> keep_clear=
[rim], post_grasp_motion=tilt_pour, is Experiment_Logs/2026-08-07's own
real constraints.json -- the anchor trial used throughout Figures 1-13.
Both columns' Reasoning/Perception cells come from real, independently
logged runs; they are NOT claimed to be the same session as each other,
nor is the Kinematics (trial 9) row claimed to be the literal execution of
either instruction string -- trial 9 is a real GRASP_OK execution on this
same anchor capture/session, cited as "a real successful execution exists
for a main_body-class grasp here," not as this exact instruction's own
logged trial (no instruction string is recorded in trials.csv).
Supporting evidence: q6_intent_mug.log (reasoning+perception, left column);
  Experiment_Logs/2026-08-07/constraints.json (reasoning, right column);
  part_adaptive.py:521-524 (NOISE gate, right column perception);
  trials.csv trial 9 (kinematics, left column, real z_rise_m=0.1420).
Required diagrammatic elements: the two-column/three-band layout and its
  connecting arrows are diagrammatic scaffolding; the right column's
  Kinematics band is explicitly labeled "not attempted" rather than
  asserting a failure that was never run -- the horizontal side-grasp
  limitation is a manipulability-data argument (Figure 7), not a logged
  execution attempt for this specific instruction.

Run: python new_h_three_layer_limit.py
Output: generated_assets/new_h/new_h_three_layer_limit.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp import part_adaptive as pa
from intent_grasp import som_part_selection as sps
from intent_grasp.paths import WORKSPACE
COL_LEFT_X, COL_RIGHT_X, COL_W = 0.03, 0.545, 0.425
BAND_Y = {"reasoning": 0.66, "perception": 0.40, "kinematics": 0.14}
BAND_H = 0.20

# real mug capture reused from NEW-A -- same real 3D components, same real
# camera intrinsics/extrinsics, projected onto the same real pixels
SLIDE_CAP_PATH = os.path.join(str(WORKSPACE), "captures_pairs_2",
                               "cap_mug_head_near.npz")
SLIDE_LEFT_COMPONENTS = ["main_body"]
SLIDE_RIGHT_COMPONENTS = ["lateral_protrusion", "lateral_protrusion_1"]
SLIDE_COMPONENT_COLOR = {"main_body": fs.ACCEPTED, "lateral_protrusion": fs.REJECTED,
                          "lateral_protrusion_1": "#B4433B"}


def _band_box(ax, x, y, w, h, title, lines, border_color, title_color=None):
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes, fill=False,
                            edgecolor=border_color, linewidth=2.0))
    ax.text(x + w / 2, y + h - 0.025, title, transform=ax.transAxes, ha="center", va="top",
            color=title_color or border_color, fontsize=13, weight="bold", family=fs.FONT)
    ax.text(x + w / 2, y + h - 0.075, "\n".join(lines), transform=ax.transAxes, ha="center", va="top",
            color=fs.MUTED, fontsize=10, family=fs.FONT, linespacing=1.5)


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_h"), "new_h_three_layer_limit.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("The Three-Layer Limit -- One Object, Two Instructions", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Reasoning commits to a confident answer either way; only perception's real measurement "
              "decides whether execution is even attempted", **fs.BODY)

    ax = fig.add_axes([0.0, 0.10, 1.0, 0.74])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(COL_LEFT_X + COL_W / 2, 0.955, '"move this out of the way"', transform=ax.transAxes,
            ha="center", color=fs.INK, fontsize=13, weight="bold", family=fs.FONT)
    ax.text(COL_RIGHT_X + COL_W / 2, 0.955, '"I\'d like a hot drink"', transform=ax.transAxes,
            ha="center", color=fs.INK, fontsize=13, weight="bold", family=fs.FONT)

    # -- Reasoning band (both columns commit to an answer -- REASONING accent)
    _band_box(ax, COL_LEFT_X, BAND_Y["reasoning"], COL_W, BAND_H, "REASONING",
              ["target_part: \"body\"", "(q6_intent_mug.log)"], fs.REASONING, fs.REASONING)
    _band_box(ax, COL_RIGHT_X, BAND_Y["reasoning"], COL_W, BAND_H, "REASONING",
              ["target_part: \"handle\"", "keep_clear: [rim]", "post_grasp_motion: tilt_pour",
               "(constraints.json, anchor trial)"], fs.REASONING, fs.REASONING)

    # -- Perception band (real measurement decides pass/refuse)
    _band_box(ax, COL_LEFT_X, BAND_Y["perception"], COL_W, BAND_H, "PERCEPTION -- PASSES",
              ["main_body: 1390 pts / 18 mm", "evidence: ok", "(q6_intent_mug.log)"], fs.ACCEPTED)
    _band_box(ax, COL_RIGHT_X, BAND_Y["perception"], COL_W, BAND_H, "PERCEPTION -- REFUSED",
              ["lateral_protrusion: 53 pts / 4 mm", "+ lateral_protrusion_1: 36 pts / 3 mm",
               "evidence: NOISE (part_adaptive.py:521-524)"], fs.REJECTED)

    # -- Kinematics band: left executes for real; right explicitly not attempted
    _band_box(ax, COL_LEFT_X, BAND_Y["kinematics"], COL_W, BAND_H, "KINEMATICS -- EXECUTED",
              ["real GRASP_OK exists for a main_body-class", "grasp on this capture: z_rise = 0.1420 m",
               "(trials.csv, trial 9 -- same session,", "not this exact instruction's own logged trial)"],
              fs.ACCEPTED)
    _band_box(ax, COL_RIGHT_X, BAND_Y["kinematics"], COL_W, BAND_H, "KINEMATICS -- NOT ATTEMPTED",
              ["Refused before execution -- no attempt", "was logged for this instruction.",
               "(Side-grasp infeasibility here is a Fig. 7", "manipulability argument, not a logged failure.)"],
              fs.MUTED, fs.MUTED)

    # connecting arrows
    for x0 in (COL_LEFT_X, COL_RIGHT_X):
        ax.add_patch(FancyArrowPatch((x0 + COL_W / 2, BAND_Y["reasoning"] - 0.005),
                                      (x0 + COL_W / 2, BAND_Y["perception"] + BAND_H + 0.005),
                                      transform=ax.transAxes, color=fs.MUTED, linewidth=1.6,
                                      arrowstyle="-|>", mutation_scale=15))
    ax.add_patch(FancyArrowPatch((COL_LEFT_X + COL_W / 2, BAND_Y["perception"] - 0.005),
                                  (COL_LEFT_X + COL_W / 2, BAND_Y["kinematics"] + BAND_H + 0.005),
                                  transform=ax.transAxes, color=fs.ACCEPTED, linewidth=1.8,
                                  arrowstyle="-|>", mutation_scale=15))
    # right column: dashed/broken connector -- chain stops here, nothing executed
    ax.plot([COL_RIGHT_X + COL_W / 2, COL_RIGHT_X + COL_W / 2],
            [BAND_Y["perception"] - 0.005, BAND_Y["kinematics"] + BAND_H + 0.005],
            transform=ax.transAxes, color=fs.REJECTED, linewidth=1.6, linestyle=(0, (3, 3)))

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "Left/right columns are two independent real runs, not a matched pair on the same session -- "
              "each cell is sourced individually (see module docstring). Trial 9's z_rise is this same",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "anchor capture's own real successful execution, not logged as this exact instruction's trial "
              "(trials.csv records no instruction string). Right column's kinematics band is a real refusal,",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "not an invented failed attempt -- nothing was executed for it.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def _project_and_bbox(comp_names, comp, K, extr, rgb_shape, pad=45):
    all_u, all_v = [], []
    per_comp = {}
    for name in comp_names:
        u, v, z, valid = pa.project_points_to_pixels(comp[name], K, extr)
        per_comp[name] = (u[valid], v[valid])
        all_u.append(u[valid])
        all_v.append(v[valid])
    all_u, all_v = np.concatenate(all_u), np.concatenate(all_v)
    x0, x1 = max(int(all_u.min()) - pad, 0), min(int(all_u.max()) + pad, rgb_shape[1])
    y0, y1 = max(int(all_v.min()) - pad, 0), min(int(all_v.max()) + pad, rgb_shape[0])
    return per_comp, (x0, x1, y0, y1)


def render_slide(out_path=None):
    """Slide variant: same 3-row/2-column structure, but the perception row
    shows the real mug image with the relevant region highlighted (body
    left, handle fragments right) instead of text-only boxes. All box text
    cut to <=2 lines; full sourcing moves to speaker notes."""
    out_path = out_path or os.path.join(fs.asset_dir("new_h"), "new_h_three_layer_limit_slide.png")
    rgb, comp, desc, K, extr = sps._load_and_isolate(SLIDE_CAP_PATH)
    left_proj, left_bbox = _project_and_bbox(SLIDE_LEFT_COMPONENTS, comp, K, extr, rgb.shape)
    right_proj, right_bbox = _project_and_bbox(SLIDE_RIGHT_COMPONENTS, comp, K, extr, rgb.shape)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Reasoning Always Answers -- Perception Decides", **{**fs.TITLE, "size": 32},
                 x=fs.MARGIN, ha="left")

    col_x = {"left": 0.03, "right": 0.52}
    col_title = {"left": '"move this out of the way"', "right": '"I\'d like a hot drink"'}
    for side in ("left", "right"):
        fig.text(col_x[side] + 0.225, 0.865, col_title[side], ha="center", color=fs.INK, fontsize=18,
                  weight="bold", family=fs.FONT)

    band_y = {"reasoning": 0.665, "perception": 0.36, "kinematics": 0.10}
    band_h = 0.155
    col_w = 0.45

    def band_box(x, y, h, title, lines, color):
        ax = fig.add_axes([x, y, col_w, h])
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, edgecolor=color, linewidth=2.0))
        ax.text(0.5, 0.90, title, transform=ax.transAxes, ha="center", va="top", color=color, fontsize=16,
                weight="bold", family=fs.FONT)
        ax.text(0.5, 0.55, "\n".join(lines), transform=ax.transAxes, ha="center", va="center", color=fs.MUTED,
                fontsize=16, family=fs.FONT, linespacing=1.4)

    band_box(col_x["left"], band_y["reasoning"], band_h, "REASONING", ['target_part: "body"'], fs.REASONING)
    band_box(col_x["right"], band_y["reasoning"], band_h, "REASONING", ['target_part: "handle"'], fs.REASONING)

    for side, comp_names, proj, bbox, title, color in [
        ("left", SLIDE_LEFT_COMPONENTS, left_proj, left_bbox, "PASSES", fs.ACCEPTED),
        ("right", SLIDE_RIGHT_COMPONENTS, right_proj, right_bbox, "REFUSED", fs.REJECTED),
    ]:
        ax = fig.add_axes([col_x[side], band_y["perception"], col_w, band_h + 0.03])
        ax.imshow(rgb)
        for name in comp_names:
            u, v = proj[name]
            ax.scatter(u, v, s=10, color=SLIDE_COMPONENT_COLOR[name], alpha=0.9, linewidths=0)
        x0, x1, y0, y1 = bbox
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(color)
            spine.set_linewidth(2.5)
        ax.text(0.5, 1.10, "PERCEPTION", transform=ax.transAxes, ha="center", va="bottom", color=color,
                fontsize=16, weight="bold", family=fs.FONT)
        ax.text(0.5, 1.24, title, transform=ax.transAxes, ha="center", va="bottom", color=color,
                fontsize=48, weight="bold", family=fs.FONT)

    band_box(col_x["left"], band_y["kinematics"], band_h, "KINEMATICS", ["executed: GRASP_OK",
              "z_rise = 0.1420 m"], fs.ACCEPTED)
    band_box(col_x["right"], band_y["kinematics"], band_h, "KINEMATICS", ["not attempted",
              "(refused before execution)"], fs.MUTED)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "captures_pairs_2/cap_mug_head_near.npz", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-H three-layer limit", [
        "Left column instruction is a disclosed substitution: no real pour-toned instruction in this repo "
        "resolves target_part=\"body\" (all real ones resolve \"handle\"). \"move this out of the way\" -> "
        "body -> main_body is q6_intent_mug.log's own real bind_part result, used honestly in its place.",
        "Right column: Experiment_Logs/2026-08-07/constraints.json -- the anchor trial used throughout "
        "Figures 1-13. keep_clear=[rim], post_grasp_motion=tilt_pour (not shown on slide).",
        "Left/right columns are two independent real runs, not a matched pair on the same session.",
        "Kinematics left: trial 9 (trials.csv) is this same anchor capture's own real successful execution, "
        "not logged as this exact instruction's trial (trials.csv records no instruction string).",
        "Kinematics right: a real refusal before execution, not an invented failed attempt -- nothing was "
        "run for it. The side-grasp infeasibility is a Figure 7 manipulability argument, not a logged failure.",
        "Perception gate: part_adaptive.py:521-524 (NOISE: n<60 or w<6mm). Right column: lateral_protrusion "
        "53pts/4mm + lateral_protrusion_1 36pts/3mm, both independently fail it.",
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
    print(f"new_h ({args.variant}) written to {path}")
    print(report.summary())
