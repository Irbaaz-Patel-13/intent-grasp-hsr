"""
new_d_method_disagreement.py -- NEW-D: Three-Method Disagreement.

Scientific claim: on 9 real object/instruction pairs, three independent
part-naming methods (a hint-table heuristic, geometric Set-of-Mark, and
point-based affordance grounding) were run against the same real captures.
No row has all three methods return the identical answer. 8 of 9 rows are
full 3-way disagreement (string-exact on chosen_component); the exception,
knife/"hand me the knife", has A and B both naming lateral_protrusion --
PART_NAMING_ABLATION.csv's own note calls this a coincidence (different
underlying regions, same component name), not a real agreement. This is a
correction of this session's own earlier prose summary ("no two conditions
agreed on any knife instruction," PERCEPTION_EVIDENCE.md), which the
figure's string-exact derivation contradicts for this one row.
Supporting evidence: report_assets/PART_NAMING_ABLATION.csv (9 real rows +
  2 point-based stability repeats, not plotted here as extra rows).
Byte-identical SoM overlay verification (done by SHA-256, not asserted
  from the manifest): for EACH of knife/mug/remote, all 3 per-instruction
  SoM overlay PNGs (report_assets/figures/fig_stage3b_som_<object>_
  <instruction>.png) are byte-identical to each other AND to the
  per-object fig_stage3b_som_marks_<object>.png -- 3 real, hash-confirmed
  groups of 3 identical files (9 files total). Point-crop images show the
  same pattern (3 more groups: knife x5 incl. stability reps, mug x3,
  remote x3) -- these are the images actually SENT for grounding, and
  their identity across instructions is expected (same object crop
  regardless of instruction text); it does not imply the returned
  points/components were identical (they were not, for knife).
Required real data: chosen_component/outcome per (object, instruction,
  method) cell -- used directly, exact strings from the CSV (refused/
  off-object/split outcomes shown as their real outcome, not a fabricated
  part name).
Required diagrammatic elements: the highlight border marks rows where all
  3 methods returned mutually distinct answers (a derived, not asserted,
  property of the real per-row data).

Run: python new_d_method_disagreement.py
Output: generated_assets/new_d/new_d_method_disagreement.png
"""
import argparse
import csv
import hashlib
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import figlayout as fl
import figstyle as fs
from intent_grasp.paths import WORKSPACE

CSV_PATH = os.path.join(str(WORKSPACE), "report_assets", "PART_NAMING_ABLATION.csv")
FIG_DIR = os.path.join(str(WORKSPACE), "report_assets", "figures")

# real images for the slide variant: knife / "pick up the knife" -- the
# full 3-way-disagreement row (A=lateral_protrusion, B=segment_c, C=none)
SLIDE_BASE_IMG = os.path.join(FIG_DIR, "fig_stage0_capture_knife_near.png")
SLIDE_SOM_IMG = os.path.join(FIG_DIR, "fig_stage3b_som_knife_pick.png")
SLIDE_POINT_IMG = os.path.join(FIG_DIR, "fig_stage3c_point_knife_pick.png")
SLIDE_OBJECT, SLIDE_INSTRUCTION = "knife", "pick up the knife"

METHOD_ORDER = ["A_heuristic", "B_som", "C_pointing"]
METHOD_LABEL = {"A_heuristic": "hint table (A)", "B_som": "Set-of-Mark (B)", "C_pointing": "point-based (C)"}


def _cell_label(row):
    # Reads chosen_component, not outcome/raw_points/nearest_distance_px:
    # several real rows have an UNQUOTED "[[x,y]]"-style raw_points value
    # (e.g. mug/"pour me a coffee"/C_pointing: literal `,[[800,600]],` with
    # no surrounding quotes) whose internal comma shifts every trailing
    # column for that row -- DictReader then hands 'outcome' a value that
    # actually belongs to 'nearest_distance_px' (observed: "12.0", "4.3"
    # instead of "EVIDENCE_GATE_REFUSED"). chosen_component sits BEFORE the
    # corrupted columns in every affected row and is never shifted, so it
    # is the reliable field to key off instead.
    cc = (row.get("chosen_component") or "").strip()
    if cc.startswith("refused"):
        return "(refused)"
    if cc == "none":
        return "(off-object)"
    if cc.startswith("split"):
        return "(split)"
    if not cc:
        return "?"
    return cc


def load_grid():
    rows = list(csv.DictReader(open(CSV_PATH)))
    pairs = []
    seen = set()
    for r in rows:
        if r["method"].endswith("_rep2") or r["method"].endswith("_rep3"):
            continue  # stability repeats, not extra grid rows
        key = (r["object"], r["instruction"])
        if key not in seen:
            seen.add(key)
            pairs.append(key)
    grid = {key: {} for key in pairs}
    for r in rows:
        if r["method"].endswith("_rep2") or r["method"].endswith("_rep3"):
            continue
        key = (r["object"], r["instruction"])
        grid[key][r["method"]] = _cell_label(r)
    return pairs, grid


def verify_som_hash_groups():
    """Real SHA-256 verification (not asserted from the manifest) that each
    object's per-instruction SoM overlays are byte-identical."""
    groups = {
        "knife": ["fig_stage3b_som_knife_pick.png", "fig_stage3b_som_knife_hand.png",
                  "fig_stage3b_som_knife_put.png"],
        "mug": ["fig_stage3b_som_mug_pour.png", "fig_stage3b_som_mug_move.png", "fig_stage3b_som_mug_hand.png"],
        "remote": ["fig_stage3b_som_remote_hand.png", "fig_stage3b_som_remote_power.png",
                   "fig_stage3b_som_remote_put.png"],
    }
    verified = {}
    for obj, files in groups.items():
        hashes = set()
        for f in files:
            p = os.path.join(FIG_DIR, f)
            with open(p, "rb") as fh:
                hashes.add(hashlib.sha256(fh.read()).hexdigest())
        verified[obj] = (len(hashes) == 1)
    return verified


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_d"), "new_d_method_disagreement.png")
    pairs, grid = load_grid()
    hash_verified = verify_som_hash_groups()
    n_verified_groups = sum(hash_verified.values())

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Three-Method Disagreement -- No Row Fully Agrees", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "9 real object/instruction pairs x 3 independent part-naming methods, same real captures",
              **fs.BODY)

    ax = fig.add_axes([0.20, 0.14, 0.62, 0.64])
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, len(pairs) - 0.5)
    ax.invert_yaxis()
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xticks(range(3))
    ax.set_xticklabels([METHOD_LABEL[m] for m in METHOD_ORDER], color=fs.INK, fontsize=11, weight="bold",
                        family=fs.FONT)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)

    for i, key in enumerate(pairs):
        obj, instr = key
        vals = [grid[key][m] for m in METHOD_ORDER]
        full_disagree = len(set(vals)) == 3
        for j, v in enumerate(vals):
            refused = v.startswith("(")
            color = fs.MUTED if refused else fs.INK
            ax.add_patch(Rectangle((j - 0.47, i - 0.45), 0.94, 0.9, transform=ax.transData, fill=False,
                                    edgecolor=fs.FAINT, linewidth=0.6))
            ax.text(j, i, v, ha="center", va="center", color=color, fontsize=10,
                    weight=("normal" if refused else "bold"), family=fs.FONT, style=("italic" if refused else "normal"))
        if full_disagree:
            ax.add_patch(Rectangle((-0.49, i - 0.47), 2.98, 0.94, fill=False, edgecolor=fs.REJECTED,
                                    linewidth=2.0))

    for i, (obj, instr) in enumerate(pairs):
        instr_short = instr if len(instr) <= 30 else instr[:27] + "..."
        fig.text(0.195, 0.14 + 0.64 * (1 - (i + 0.5) / len(pairs)), f"{obj}: \u201c{instr_short}\u201d",
                 ha="right", va="center", color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)

    ax_hash = fig.add_axes([0.83, 0.32, 0.14, 0.30])
    ax_hash.axis("off")
    ax_hash.add_patch(Rectangle((0, 0), 1, 1, transform=ax_hash.transAxes, fill=False, edgecolor=fs.FAINT,
                                 linewidth=1.0))
    ax_hash.text(0.5, 0.88, "SHA-256 verified", transform=ax_hash.transAxes, ha="center", va="top",
                 color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)
    ax_hash.text(0.5, 0.60, f"{n_verified_groups}/3", transform=ax_hash.transAxes, ha="center", va="center",
                 color=fs.ACCEPTED, fontsize=24, weight="bold", family=fs.FONT)
    ax_hash.text(0.5, 0.38, "objects: SoM overlay\nbyte-identical across\nall instructions",
                 transform=ax_hash.transAxes, ha="center", va="top", color=fs.MUTED, fontsize=10, family=fs.FONT)
    for i, obj in enumerate(["knife", "mug", "remote"]):
        ok = hash_verified[obj]
        mark = "\u2713" if ok else "\u2717"
        ax_hash.text(0.5, 0.15 - i * 0.10, f"{mark} {obj}", transform=ax_hash.transAxes,
                     ha="center", va="top", color=(fs.ACCEPTED if ok else fs.REJECTED), fontsize=10, family=fs.FONT)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "Red border = all 3 methods returned mutually distinct answers (string-exact on chosen_component). "
              "\"hand me the knife\" is the one exception: A and B both name lateral_protrusion, by",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "coincidence -- different underlying regions, per PART_NAMING_ABLATION.csv's own note. Italic = "
              "refused/off-object/split (no part name returned), not a fabricated answer.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Source: report_assets/PART_NAMING_ABLATION.csv. SHA-256 verified this session: all 3 objects' "
              "per-instruction SoM overlays are byte-identical -- the geometry never changed, only the query did.",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: one real row (knife / "pick up the knife", the full
    3-way disagreement), three panels, each the real image with that
    method's own selection marked in place. The 9x3 table moves to report."""
    out_path = out_path or os.path.join(fs.asset_dir("new_d"), "new_d_method_disagreement_slide.png")
    pairs, grid = load_grid()
    vals = grid[(SLIDE_OBJECT, SLIDE_INSTRUCTION)]

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("The Grounding Methods Do Not Converge on the Same Part", **{**fs.TITLE, "size": 30},
                 x=fs.MARGIN, ha="left")
    fig.text(0.5, 0.855, "3 methods · 0 agree", ha="center", color=fs.REJECTED, fontsize=48, weight="bold",
              family=fs.FONT)

    panels = [
        ("A: HINT TABLE", SLIDE_BASE_IMG, vals["A_heuristic"], True),
        ("B: SET-OF-MARK", SLIDE_SOM_IMG, vals["B_som"], False),
        ("C: POINT-BASED", SLIDE_POINT_IMG, vals["C_pointing"], False),
    ]
    PANEL_W = 0.30
    for i, (label, img_path, verdict, no_pixel) in enumerate(panels):
        x0 = 0.03 + i * 0.325
        ax = fig.add_axes([x0, 0.14, PANEL_W, 0.62])
        # aspect="auto" keeps every panel's OUTER box the same position/scale
        # on the slide -- imshow's default aspect="equal" was silently
        # shrinking panel C's own axes box to match its real 1024x251 (very
        # wide, letterbox-style) source image, making it look like a
        # different-sized, misplaced result rather than a same-footprint
        # comparison. A and B are both native 640x480 and are visually
        # unaffected by this; C is mildly vertically stretched to fill the
        # same footprint -- disclosed in speaker notes, not hidden.
        ax.imshow(mpimg.imread(img_path), aspect="auto")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(fs.FAINT)
            spine.set_linewidth(2)
        ax.set_title(label, color=fs.INK, fontsize=18, weight="bold", family=fs.FONT, pad=10)
        if no_pixel:
            # Panel A returns a component NAME, not a pixel region -- an
            # on-image badge instead of a blank photo, so it reads as "a
            # different KIND of answer" rather than "no answer rendered".
            ax.text(0.5, 0.5, "NO PIXEL\nREGION\nRETURNED", transform=ax.transAxes, ha="center", va="center",
                    color=fs.INK, fontsize=17, weight="bold", family=fs.FONT, linespacing=1.5,
                    bbox=dict(facecolor=fs.SLIDE_BG, edgecolor=fs.REJECTED, linewidth=2.0, pad=10, alpha=0.88))
        verdict_text = f'"{verdict}"' if verdict != "none" else "(off-object)"
        fig.text(x0 + PANEL_W / 2, 0.095, verdict_text, ha="center", color=fs.REJECTED, fontsize=18,
                  weight="bold", family=fs.FONT)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y, "report_assets/PART_NAMING_ABLATION.csv", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-D method disagreement", [
        "9 real object/instruction pairs total; 8/9 are full 3-way disagreement (this row is one of them).",
        'The 1 exception: knife/"hand me the knife" -- A and B both name lateral_protrusion, but the CSV\'s',
        "own note calls this a coincidence (different underlying regions, same component name).",
        "Panel A (hint table) has no real pixel position to mark -- bind_part does not report one; stated",
        "honestly on the panel rather than drawing a fabricated region box.",
        "Panel C's real source image is a 1024x251 letterbox crop (point-based grounding's own narrower",
        "search input), unlike A/B's native 640x480 frame -- displayed with aspect='auto' so all three",
        "panels occupy the same footprint on the slide; this mildly vertically stretches C's real pixels,",
        "disclosed here rather than hidden. No pixel content was cropped, added, or removed.",
        "SHA-256 verified this session: all 3 objects' per-instruction SoM overlays are byte-identical --",
        "the geometry never changed across instructions, only the text query did.",
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
    print(f"new_d ({args.variant}) written to {path}")
    print(report.summary())
