"""
new_e_isolated_vs_cluttered.py -- NEW-E: Isolated vs. Cluttered (measurement
instability under scene composition, not clutter degradation).

Scientific claim: on the 5 real scenes run through the full pipeline
(batch_scene_analysis.py), the two objects that appear in BOTH an isolated
and a cluttered capture do not move in the same direction: the pot's
graspable width drops 147mm -> 46mm (isolated -> cluttered, flipping the
real evidence gate from REFUSE to PASS); the TV remote's rises 13mm ->
73mm (both pass). The finding is that the SAME real measurement pipeline
returns substantially different widths for the same physical part
depending on scene composition -- not that clutter uniformly degrades
measurement. Only 5 real scenes exist in this dataset; this is not
generalised beyond them.
Supporting evidence: batch_scene_analysis.csv/.md (5 real rows: TV_remote,
  cluster_mug_cokecan_pot, cluster_mug_remote_pot, metal_spoon,
  pot_with_handle_and_lid -- target_object, target_part, minor_mm,
  over_aperture, all real, all used directly).
Required real data: all widths, all over_aperture flags, all target_object/
  target_part strings -- used directly, no invented cell.
Required diagrammatic elements: none. metal_spoon has no cluttered-capture
  row in this dataset -- its cluttered cell is rendered "not captured",
  not inferred or interpolated.

Run: python new_e_isolated_vs_cluttered.py
Output: generated_assets/new_e/new_e_isolated_vs_cluttered.png
"""
import argparse
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "batch_scene_analysis.csv")
CAPTURES_DIR = os.path.join(str(WORKSPACE), "captures_0723")
SLIDE_ISO_NPZ = "cap_pot_with_handle_and_lid.npz"
SLIDE_CLUT_NPZ = "cap_cluster_mug_cokecan_pot.npz"

# real (object-key, isolated-scene, cluttered-scene-or-None) pairing, derived
# from which target_object repeats across the 5 real rows
PAIRS = [
    ("pot", "pot_with_handle_and_lid", "cluster_mug_cokecan_pot"),
    ("TV remote control", "TV_remote", "cluster_mug_remote_pot"),
    ("spoon", "metal_spoon", None),
]


def load_rows():
    rows = {r["scene"]: r for r in csv.DictReader(open(CSV_PATH))}
    return rows


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_e"), "new_e_isolated_vs_cluttered.png")
    rows = load_rows()

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Isolated vs. Cluttered -- Measurement Instability, Not Clutter Degradation",
                 **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "5 real scenes (batch_scene_analysis.csv) -- the pot and the remote move in OPPOSITE "
              "directions; this is not a general clutter-degrades-measurement claim", **fs.BODY)

    ax = fig.add_axes([0.09, 0.16, 0.56, 0.64])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(0, 160)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["ISOLATED", "CLUTTERED"], color=fs.INK, fontsize=12, weight="bold", family=fs.FONT)
    ax.set_ylabel("graspable (minor) width, mm", color=fs.MUTED, fontsize=10, family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.axhline(125, color=fs.MUTED, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.text(1.28, 125, "125mm aperture", ha="right", va="bottom", color=fs.MUTED, fontsize=10, family=fs.FONT)

    def gate_color(row):
        return fs.REJECTED if row["over_aperture"] == "1" else fs.ACCEPTED

    # TV remote (13mm) and spoon (9mm) sit close enough in data-space that
    # their labels collide at default placement; nudge in display (point)
    # space, not data space, so the fix holds regardless of axis scale.
    ISO_LABEL_NUDGE_PT = {"pot": (0, 0), "TV remote control": (0, 13), "spoon": (0, -13)}

    for label, iso_scene, clut_scene in PAIRS:
        iso = rows[iso_scene]
        w_iso = float(iso["minor_mm"])
        c_iso = gate_color(iso)
        ax.scatter([0], [w_iso], s=140, color=c_iso, zorder=5, edgecolors=fs.SLIDE_BG, linewidths=1.5)
        ax.annotate(f"{label}\n{w_iso:.0f}mm", (0, w_iso), ha="right", va="center", color=c_iso, fontsize=10,
                    weight="bold", family=fs.FONT, xytext=(-14 + ISO_LABEL_NUDGE_PT[label][0],
                    ISO_LABEL_NUDGE_PT[label][1]), textcoords="offset points")

        if clut_scene is None:
            ax.text(1.0, w_iso, "not captured", ha="left", va="center", color=fs.MUTED, fontsize=10,
                    family=fs.FONT, style="italic")
            continue

        clut = rows[clut_scene]
        w_clut = float(clut["minor_mm"])
        c_clut = gate_color(clut)
        ax.scatter([1], [w_clut], s=140, color=c_clut, zorder=5, edgecolors=fs.SLIDE_BG, linewidths=1.5)
        delta = w_clut - w_iso
        line_color = fs.ACCEPTED if delta > 0 else fs.REJECTED
        ax.add_patch(FancyArrowPatch((0, w_iso), (1, w_clut), color=line_color, linewidth=2.0,
                                      arrowstyle="-|>", mutation_scale=16, zorder=4,
                                      connectionstyle="arc3,rad=0.0"))
        mid_y = (w_iso + w_clut) / 2
        ax.text(0.5, mid_y + 6, f"{delta:+.0f}mm", ha="center", va="bottom", color=line_color, fontsize=11,
                weight="bold", family=fs.FONT)
        ax.text(1.06, w_clut, f"{w_clut:.0f}mm", ha="left", va="center", color=c_clut, fontsize=10,
                weight="bold", family=fs.FONT)

    ax.text(0, 152, "REFUSE" if rows["pot_with_handle_and_lid"]["over_aperture"] == "1" else "PASS",
            ha="center", va="bottom", color=gate_color(rows["pot_with_handle_and_lid"]), fontsize=10,
            weight="bold", family=fs.FONT)
    ax.text(1, 152, "PASS" if rows["cluster_mug_cokecan_pot"]["over_aperture"] == "0" else "REFUSE",
            ha="center", va="bottom", color=gate_color(rows["cluster_mug_cokecan_pot"]), fontsize=10,
            weight="bold", family=fs.FONT)

    fig.text(0.09, 0.115, "Only 5 real scenes exist in this dataset -- not generalised beyond them.",
              color=fs.MUTED, fontsize=10, style="italic", family=fs.FONT)

    # -- second panel: reasoning (stable) vs perception (unstable) for the 2 cluttered scenes
    ax2 = fig.add_axes([0.70, 0.16, 0.26, 0.64])
    ax2.axis("off")
    ax2.add_patch(Rectangle((0, 0), 1, 1, transform=ax2.transAxes, fill=False, edgecolor=fs.FAINT, linewidth=1.0))
    ax2.text(0.5, 0.96, "Cluttered scenes: reasoning vs. perception", transform=ax2.transAxes, ha="center",
              va="top", color=fs.INK, fontsize=11, weight="bold", family=fs.FONT)
    y = 0.82
    for scene in ["cluster_mug_cokecan_pot", "cluster_mug_remote_pot"]:
        r = rows[scene]
        gate = "REFUSE" if r["over_aperture"] == "1" else "PASS"
        gate_c = fs.REJECTED if r["over_aperture"] == "1" else fs.ACCEPTED
        ax2.text(0.06, y, scene, transform=ax2.transAxes, ha="left", va="top", color=fs.MUTED, fontsize=10,
                  family=fs.FONT, style="italic")
        y -= 0.075
        ax2.text(0.06, y, f"reasoning: {r['target_object']} / {r['target_part']}", transform=ax2.transAxes,
                  ha="left", va="top", color=fs.REASONING, fontsize=10, weight="bold", family=fs.FONT)
        y -= 0.075
        ax2.text(0.06, y, f"perception: {r['minor_mm']}mm -- {gate}", transform=ax2.transAxes, ha="left",
                  va="top", color=gate_c, fontsize=10, weight="bold", family=fs.FONT)
        y -= 0.12
    ax2.text(0.06, y - 0.02, "Reasoning names a confident object+part\neither way; perception's real width is\n"
              "what actually varies.", transform=ax2.transAxes, ha="left", va="top", color=fs.MUTED,
              fontsize=10, family=fs.FONT, linespacing=1.4)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Green = evidence gate PASS, red = REFUSE (over_aperture, 125mm). The gate refused the pot's "
              "isolated 147mm measurement and accepted its cluttered 46mm measurement -- same real object.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Source: batch_scene_analysis.csv (5 real rows). metal_spoon has no cluttered-capture row in "
              "this dataset -- rendered \"not captured\", not inferred.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: same isolated-vs-cluttered composition, kept as-is,
    with real RGB thumbnails at the pot's two endpoints and enlarged
    REFUSE/PASS labels. The reasoning side-panel moves to the report."""
    out_path = out_path or os.path.join(fs.asset_dir("new_e"), "new_e_isolated_vs_cluttered_slide.png")
    rows = load_rows()

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Same Pot, Same Pipeline -- Opposite Gate Outcome", **{**fs.TITLE, "size": 32},
                 x=fs.MARGIN, ha="left")

    ax = fig.add_axes([0.06, 0.14, 0.46, 0.64])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(0, 160)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["ISOLATED", "CLUTTERED"], color=fs.INK, fontsize=16, weight="bold", family=fs.FONT)
    ax.set_ylabel("graspable width, mm", color=fs.MUTED, fontsize=14, family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=12)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.axhline(125, color=fs.MUTED, linewidth=1.2, linestyle=(0, (4, 3)))

    def gate_color(row):
        return fs.REJECTED if row["over_aperture"] == "1" else fs.ACCEPTED

    for label, iso_scene, clut_scene in PAIRS:
        if clut_scene is None:
            continue
        iso, clut = rows[iso_scene], rows[clut_scene]
        w_iso, w_clut = float(iso["minor_mm"]), float(clut["minor_mm"])
        c_iso, c_clut = gate_color(iso), gate_color(clut)
        is_pot = label == "pot"
        lw = 3.0 if is_pot else 1.4
        alpha = 1.0 if is_pot else 0.35
        ax.scatter([0], [w_iso], s=(220 if is_pot else 90), color=c_iso, zorder=5, edgecolors=fs.SLIDE_BG,
                   linewidths=1.5, alpha=alpha)
        ax.scatter([1], [w_clut], s=(220 if is_pot else 90), color=c_clut, zorder=5, edgecolors=fs.SLIDE_BG,
                   linewidths=1.5, alpha=alpha)
        line_color = fs.ACCEPTED if w_clut > w_iso else fs.REJECTED
        ax.add_patch(FancyArrowPatch((0, w_iso), (1, w_clut), color=line_color, linewidth=lw,
                                      arrowstyle="-|>", mutation_scale=(20 if is_pot else 12), zorder=4, alpha=alpha))
        if is_pot:
            # Labels sit OFF to the side of their endpoint, not stacked on
            # the line's own path -- REFUSE/PASS/delta previously collided
            # with the arrow they were meant to annotate.
            ax.text(0, w_iso + 8, "REFUSE", ha="center", va="bottom", color=c_iso, fontsize=48, weight="bold",
                     family=fs.FONT)
            ax.text(1, w_clut - 8, "PASS", ha="center", va="top", color=c_clut, fontsize=48, weight="bold",
                     family=fs.FONT)
            ax.text(0.5, 158, f"pot: {w_clut - w_iso:+.0f}mm", ha="center", va="top",
                     color=fs.INK, fontsize=18, weight="bold", family=fs.FONT)

    ax_iso = fig.add_axes([0.56, 0.50, 0.19, 0.30])
    ax_clut = fig.add_axes([0.78, 0.50, 0.19, 0.30])
    THUMB_CROP = (110, 190, 560, 500)  # same tabletop crop convention as NEW-B
    for ax_img, npz_name, label in [(ax_iso, SLIDE_ISO_NPZ, "pot, isolated"),
                                     (ax_clut, SLIDE_CLUT_NPZ, "pot, in clutter")]:
        d = np.load(os.path.join(CAPTURES_DIR, npz_name))
        x0c, y0c, x1c, y1c = THUMB_CROP
        ax_img.imshow(d["rgb"][y0c:y1c, x0c:x1c])
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spine in ax_img.spines.values():
            spine.set_color(fs.FAINT)
            spine.set_linewidth(2)
        ax_img.set_title(label, color=fs.INK, fontsize=16, weight="bold", family=fs.FONT, pad=6)

    fig.text(0.56, 0.44, "Only 5 real scenes exist in\nthis dataset -- not generalised.",
              color=fs.MUTED, fontsize=16, style="italic", family=fs.FONT, linespacing=1.5)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "batch_scene_analysis.csv", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-E isolated vs cluttered", [
        "Faint pair on the chart: TV remote control (13mm->73mm, both PASS) -- moves the OPPOSITE "
        "direction from the pot, so this is not a general clutter-degrades-measurement claim.",
        "metal_spoon has no cluttered-capture row in this dataset -- not shown here, not inferred.",
        "125mm dashed line: the real evidence-gate aperture threshold.",
        "Reasoning-vs-perception panel (both cluttered scenes: reasoning names a confident object+part "
        "either way; perception's real measured width is what actually varies) -- report variant only.",
        "Source: batch_scene_analysis.csv (5 real rows).",
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
    print(f"new_e ({args.variant}) written to {path}")
    print(report.summary())
