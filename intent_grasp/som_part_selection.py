r"""
som_part_selection.py -- Set-of-Marks (SoM) part selection for the hand-camera
part-grounding pipeline (hand_part_grounding.py).

LangSAM's part-level text prompt (e.g. "mug handle.") collapses to the whole
object mask in most runs (see visual_grounding.py's part_grounding_ok
warning) -- GroundingDINO/SAM don't reliably localise sub-object parts from
text alone. This module replaces that step, when it collapses, with the
Set-of-Mark technique already prototyped in som_grounding.py:
  1. SAM2's automatic mask generator segments the object-bbox crop into
     candidate regions (perception-derived, not text-driven).
  2. Candidates that are sub-parts of the object (mostly on it, not ~all of
     it) are kept and numbered.
  3. GPT-4o is shown the numbered image and asked ONLY to pick a number
     (selection, not open-ended coordinates) for the part named by
     AffordanceReasoner's Step 3, given the task instruction for context.
  4. The chosen region's mask (mapped back to full-image coordinates) is the
     part mask.

Reuses auto_regions()/filter_subparts()/mark_image() from som_grounding.py
as-is; only the VLM call is new here, built on AffordanceReasoner's client
pattern (config.vlm.api_key/model_name, mock-mode aware) rather than
som_grounding.py's ad hoc OpenAI(api_key=os.environ[...]) client, so it
degrades the same way the rest of the pipeline does when no API key is set.
"""
import argparse
import json
import base64
import io
import os
from typing import Optional, Tuple

import numpy as np

from intent_grasp.som_grounding import auto_regions, filter_subparts, mark_image

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from intent_grasp import part_adaptive as pa
except ImportError:
    pa = None


def _crop_bbox_with_padding(bbox, pad, w, h):
    x1, y1, x2, y2 = bbox
    return (max(0, x1 - pad), max(0, y1 - pad), min(w, x2 + pad), min(h, y2 + pad))


def ask_vlm_region(vlm_config, marked_pil, target_object, target_part,
                    instruction, n) -> Tuple[int, str]:
    """
    Ask GPT-4o which numbered SoM region is target_part, given instruction
    for task context. Mirrors AffordanceReasoner._call_vlm's client
    construction (config.vlm.api_key/model_name) and
    _parse_json_response's markdown-fence stripping, so this degrades the
    same way (a printed warning, region=-1) when no API key is configured --
    unlike som_grounding.py's ask_vlm_pick(), which hard-requires
    OPENAI_API_KEY via os.environ and raises KeyError if it's unset.

    Returns (region_idx, reason). region_idx is -1 if the VLM found no
    matching region, the response was unparseable, or no client is available.
    """
    if OpenAI is None or not vlm_config.api_key:
        print("[som_part_selection] WARNING: no OPENAI_API_KEY / openai package "
              "-- cannot run SoM region selection, treating as 'no match'.")
        return -1, "no_vlm_client"

    client = OpenAI(api_key=vlm_config.api_key)
    buf = io.BytesIO()
    marked_pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    prompt = (
        f"This close-up image of a {target_object} has {n} numbered candidate "
        f"regions (0..{n - 1}), each a differently-coloured patch with its number. "
        f"The task is: \"{instruction}\". For this task, which numbered region "
        f"corresponds to the '{target_part}' of the {target_object} -- the part "
        f"of the object that should be grasped? "
        f"Respond ONLY JSON: {{\"region\": <int>, \"reason\": \"<short>\"}}. "
        f"If none of the regions is the {target_part}, set region to -1."
    )
    response = client.chat.completions.create(
        model=vlm_config.model_name,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]}],
        max_tokens=120, temperature=0.0,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        data = json.loads(text.strip())
        return int(data["region"]), data.get("reason", "")
    except Exception as e:
        print(f"[som_part_selection] unparseable VLM response: {text!r} ({e})")
        return -1, "unparseable"


def select_part_via_som(lang_sam_model, vlm_config, rgb, object_mask, object_bbox,
                         target_object, target_part, instruction, crop_padding=20):
    """
    Run the SoM part-selection pipeline described in the module docstring.

    Args:
        lang_sam_model: the LangSAM instance already loaded by
            VisualAffordanceGrounder (grounder.lang_sam) -- reused so SAM2's
            weights aren't loaded twice.
        vlm_config: config.vlm (VLMConfig) -- supplies api_key/model_name for
            ask_vlm_region().
        rgb: (H,W,3) uint8 hand-camera image.
        object_mask: (H,W) bool -- the whole-object mask from the same
            grounder.ground() call (Pass 1, which reliably works).
        object_bbox: (x1,y1,x2,y2) int -- ditto, full-image coordinates.
        target_object / target_part: strings from AffordanceReasoner.
        instruction: the raw task instruction string (task context for the
            VLM's region choice).
        crop_padding: pixels of padding around object_bbox before running
            the automatic mask generator (matches VisualGroundingConfig.
            crop_padding's role in visual_grounding.py's part-detection pass).

    Returns:
        (part_mask_full, marked_pil, n_candidates, chosen_region, reason)
        part_mask_full is None if SoM found no usable region (no candidates,
        or the VLM picked none/none parseable) -- caller should fall back to
        the whole-object mask in that case.
    """
    h, w = rgb.shape[:2]
    x1, y1, x2, y2 = _crop_bbox_with_padding(object_bbox, crop_padding, w, h)
    rgb_crop = rgb[y1:y2, x1:x2]
    om_crop = object_mask[y1:y2, x1:x2]

    print(f"[som_part_selection] running SAM automatic mask generator on "
          f"object crop ({rgb_crop.shape[1]}x{rgb_crop.shape[0]} px)...")
    regions_crop = auto_regions(lang_sam_model, rgb_crop)
    print(f"[som_part_selection] {len(regions_crop)} raw regions")
    candidates = filter_subparts(regions_crop, om_crop)
    print(f"[som_part_selection] {len(candidates)} candidate sub-part regions")

    if len(candidates) == 0:
        return None, None, 0, -1, "no_candidates"

    marked = mark_image(rgb_crop, candidates)
    region, reason = ask_vlm_region(vlm_config, marked, target_object,
                                     target_part, instruction, len(candidates))
    print(f"[som_part_selection] VLM picked region {region}  reason='{reason}'")

    if region is None or region < 0 or region >= len(candidates):
        return None, marked, len(candidates), region, reason

    chosen_crop = candidates[region]
    part_mask_full = np.zeros((h, w), dtype=bool)
    part_mask_full[y1:y2, x1:x2] = chosen_crop
    return part_mask_full, marked, len(candidates), region, reason


# =====================================================================
#  GEOMETRIC variant (added this session) -- candidates come from
#  part_adaptive.find_components()/describe_components(), not SAM2's
#  appearance-based automatic mask generator. mark_image() above is reused
#  unchanged; only the candidate front end and the VLM prompt are new.
#
#  Why: bind_part()'s RELATION_HINTS name-to-vocabulary table was shown
#  (Parts AA/AM/AO/ANr this session) to mislabel components for roughly
#  half of objects -- a component's internal NAME does not reliably predict
#  which physical region it is, and even an unrelated internal rename can
#  silently change which region a query resolves to (ANr3). This path
#  sidesteps RELATION_HINTS entirely: the VLM is shown the instruction and
#  each candidate's MEASURED geometry, never a part name, and picks a
#  region number directly.
#
#  Candidate rule (ANr1, revised from an earlier percentage-exclusion
#  proposal): every component is offered, including ones that cover most
#  of the object -- share of the total object's points is DISCLOSED, not
#  used to exclude, since a vessel's "body" is often >70% of the object
#  and is still the correct answer for many instructions.
#
#  Evidence rule (ANr2, revised from an earlier withholding proposal):
#  NOISE/LOW components are NOT withheld either -- withholding would make
#  a correct-but-weak answer (e.g. a 4 mm mug handle) unavailable and turn
#  a legitimate evidence-gate refusal into an invisible gap. Every
#  component is offered; evidence class is disclosed when below the floor.
#  If the VLM picks one anyway, the existing evidence gate refuses it at
#  execution, and that refusal is logged as its own outcome (AP4).
# =====================================================================

OUTCOME_SELECTED = "SELECTED"
OUTCOME_EVIDENCE_GATE_REFUSED = "EVIDENCE_GATE_REFUSED"
OUTCOME_VLM_NONE = "VLM_NONE"
OUTCOME_UNPARSEABLE = "UNPARSEABLE"


def build_candidates(comp, desc):
    """comp/desc from part_adaptive.find_components()/describe_components() ->
    an ordered list of candidate dicts (one per component). No exclusion by
    size or evidence (ANr1/ANr2) -- every component found is offered.

    Ordering (AX2): for objects elongated enough that find_components() itself
    would create axis segments (same test it uses internally: major extent >
    2.2x the next), candidates are ordered by their mean position along the
    object's own PCA major axis, so numbering runs coherently end-to-end
    rather than jumping around by size. For non-elongated objects (e.g. a
    mug, which has no meaningful single major axis), there is no coherent
    "along the object" ordering to fall back on -- candidates are ordered
    largest-first instead. This is a stated fallback, not a hidden default.
    """
    total = sum(len(pts) for pts in comp.values())
    order = sorted(comp.keys(), key=lambda k: -len(comp[k]))  # default / fallback
    axis_ordered = False
    if pa is not None and comp:
        all_pts = np.vstack(list(comp.values()))
        if len(all_pts) >= 10:
            p = pa.pca(all_pts)
            if p["extent"][0] > 2.2 * max(p["extent"][1], 1e-6):
                axis = p["axes"][:, 0]
                centroid = p["centroid"]
                order = sorted(comp.keys(),
                               key=lambda k: float((comp[k].mean(0) - centroid) @ axis))
                axis_ordered = True
    print("[som_part_selection] candidate order: %s"
          % ("PCA major-axis position" if axis_ordered else "largest-first (fallback -- object not elongated)"))
    out = []
    for name in order:
        pts = comp[name]
        d = desc.get(name, {})
        out.append(dict(
            name=name, points=pts, n=len(pts),
            width_mm=d.get("closing_width_mm", -1),
            evidence=d.get("evidence", "ok"),
            share_pct=100.0 * len(pts) / total if total else 0.0,
        ))
    return out


def masks_for_candidates(candidates, K, extrinsics, shape_hw):
    """Project each candidate's 3D points to a 2D mask via
    part_adaptive.project_part_to_mask -- the same round-trip verified
    against the RGB in Part AA. Drops any candidate that projects to 0 px
    (nothing to mark or select)."""
    kept = []
    for c in candidates:
        mask, npx = pa.project_part_to_mask(c["points"], K, extrinsics, shape_hw)
        if npx == 0:
            print("[som_part_selection] WARNING: '%s' projects to 0 px -- "
                  "dropped from candidates" % c["name"])
            continue
        c = dict(c); c["mask"] = mask.astype(bool); c["mask_px"] = npx
        kept.append(c)
    return kept


def format_region_list(candidates):
    """One line per numbered region: width, points, share of object, and an
    explicit evidence-floor note when below floor. No part names (AP3)."""
    lines = []
    for i, c in enumerate(candidates):
        floor_note = " (below evidence floor)" if c["evidence"] in ("LOW", "NOISE") else ""
        lines.append("  %d: closing width %d mm, %d points, %.1f%% of object%s"
                     % (i, c["width_mm"], c["n"], c["share_pct"], floor_note))
    return "\n".join(lines)


def build_prompt(instruction, candidates):
    """The prompt itself -- instruction + measured geometry only, no part
    vocabulary anywhere (AN3/AP3)."""
    return (
        "A robot is about to act on the object shown, following this "
        "instruction: \"%s\"\n\n"
        "The image has %d numbered candidate regions marked on the object, "
        "each a distinct colour-tinted patch with a number label. Measured "
        "properties of each region:\n%s\n\n"
        "Considering the instruction and each region's measured size, "
        "position and share of the object, which numbered region should "
        "the robot grasp? Respond ONLY with JSON: "
        "{\"region\": <int>, \"reason\": \"<short>\"}\n"
        "If none of the regions is an appropriate place to grasp for this "
        "instruction, set region to -1."
        % (instruction, len(candidates), format_region_list(candidates))
    )


def ask_vlm_task_region(vlm_config, marked_pil, instruction, candidates) -> Tuple[int, str]:
    """Ask GPT-4o which numbered region to grasp, given ONLY the instruction
    and each region's measured geometry. Mirrors AffordanceReasoner._call_vlm's
    client construction (config.api_key/model_name) -- degrades the same way
    (a printed warning, region=-1) when no API key is configured.
    """
    if OpenAI is None or not vlm_config.api_key:
        print("[som_part_selection] WARNING: no OPENAI_API_KEY / openai package "
              "-- cannot run geometric SoM selection, treating as 'no match'.")
        return -1, "no_vlm_client"

    prompt = build_prompt(instruction, candidates)
    client = OpenAI(api_key=vlm_config.api_key)
    buf = io.BytesIO()
    marked_pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    response = client.chat.completions.create(
        model=vlm_config.model_name,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,%s" % b64}},
        ]}],
        max_tokens=120, temperature=0.0,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        data = json.loads(text.strip())
        return int(data["region"]), data.get("reason", "")
    except Exception as e:
        print("[som_part_selection] unparseable VLM response: %r (%s)" % (text, e))
        return -2, "unparseable"


def _resolve_label_collisions(pil_image, positions, collision_px=35, nudge_px=30):
    """Deterministic, SYMMETRIC label-collision fix, applied AFTER
    mark_image() has already drawn (unchanged, per the hard rule) at each
    mask's true centroid. mark_image cannot be edited and always draws every
    label at its true centroid regardless of what runs afterward -- this
    function cannot erase that, only add to it.

    positions: list of (region_index, cx, cy) in the same numbering used to
    call mark_image.

    Rule (BA2, revised twice by viewing the actual rendered output, not
    assumed correct):
    v1 (AX1): only the LATER of a colliding pair was moved, by the full
       nudge_px, to a position far from its own original spot. Bug: since
       mark_image's original label at the old spot was never erased (a
       previous erasure attempt was found to damage a *different*,
       still-valid nearby label and was removed), the moved region ended up
       with TWO separately-legible copies of the same digit in two
       different places -- visible on the remote overlay ("1" appeared
       twice).
    v2 (this version, BA2): BOTH members of a colliding pair move apart from
       their shared MIDPOINT, by nudge_px/2 each, in the direction away from
       the other. Each is redrawn exactly once, at its new position, with a
       leader line back to its true centroid. Because each member's new
       position is only nudge_px/2 from its OWN original mark_image-drawn
       spot, the leftover original rendering sits close enough to blend
       into the new one rather than reading as a second, clearly-separate
       legible copy -- while the two DIFFERENT members end up separated
       from EACH OTHER by roughly nudge_px (the sum of their two opposite
       half-moves), which is the actual goal.

    Threshold raised from 25px to 35px (BA3) so borderline near-misses (e.g.
    27.6px) are also caught.

    Known limitation, disclosed rather than solved: this is one deterministic
    pairwise pass, not a layout solver. A region that collides with two
    different neighbours (a "chain") only ends up separated from whichever
    pairing was processed last in iteration order -- it is not guaranteed
    clear of every neighbour simultaneously. Re-run output is checked by eye
    below, not assumed correct from this description.
    """
    from PIL import ImageDraw, ImageFont
    positions = list(positions)
    moved_to = {}
    for i in range(len(positions)):
        idx_i, cx_i, cy_i = positions[i]
        for j in range(i):
            idx_j, cx_j, cy_j = positions[j]
            dx, dy = cx_i - cx_j, cy_i - cy_j
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < collision_px:
                if dist < 1e-6:
                    dx, dy, dist = 1.0, 1.0, 2 ** 0.5
                ux, uy = dx / dist, dy / dist
                mx, my = 0.5 * (cx_i + cx_j), 0.5 * (cy_i + cy_j)
                half = nudge_px / 2.0
                moved_to[idx_i] = (mx + ux * half, my + uy * half)
                moved_to[idx_j] = (mx - ux * half, my - uy * half)

    if not moved_to:
        return pil_image, set()

    pil_image = pil_image.convert("RGB")
    dr = ImageDraw.Draw(pil_image)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    pos_by_idx = {idx: (cx, cy) for idx, cx, cy in positions}
    for idx, (nx, ny) in moved_to.items():
        ox, oy = pos_by_idx[idx]
        dr.line([ox, oy, nx, ny], fill=(0, 0, 0), width=1)
        dr.rectangle([nx - 13, ny - 15, nx + 13, ny + 15], fill=(255, 255, 255), outline=(0, 0, 0))
        dr.text((nx - 7, ny - 13), str(idx), fill=(0, 0, 0), font=font)
    return pil_image, set(moved_to.keys())


def _draw_region_outlines(pil_image, candidates, width_px=2):
    """mark_image's own fill is a translucent tint at alpha=90/255 (~35%) --
    confirmed present in the pixel data but subtle on a small, real,
    naturally-lit region (measured: ~30-50/255 per channel shift, this
    session). mark_image is left unchanged (hard rule); this draws a bold,
    solid-colour boundary around each candidate's mask ON TOP of
    mark_image's output instead, using the same per-index tab10 colour
    mark_image itself uses, so the added outline still corresponds visually
    to mark_image's own (faint) tint and label colour. Uses a simple
    erosion-difference boundary (mask minus its own erosion), widened by
    width_px, drawn solid -- not a mask fill, so it does not fight with the
    label boxes drawn afterward.
    """
    from scipy import ndimage
    from PIL import Image
    import matplotlib.pyplot as plt
    pil_image = pil_image.convert("RGB")
    arr = np.asarray(pil_image).copy()
    cmap = plt.cm.tab10
    for i, c in enumerate(candidates):
        color = np.array([int(255 * v) for v in cmap(i % 10)[:3]], dtype=np.uint8)
        m = c["mask"]
        boundary = m & ~ndimage.binary_erosion(m, iterations=1)
        if width_px > 1:
            boundary = ndimage.binary_dilation(boundary, iterations=width_px - 1)
        arr[boundary] = color
    return Image.fromarray(arr)


def select_region_via_geometric_som(rgb, comp, desc, K, extrinsics, instruction,
                                    vlm_config=None, dry=False):
    """Geometric-candidate Set-of-Mark region selection.

    rgb: (H,W,3) uint8 image to mark and show the VLM.
    comp/desc: from part_adaptive.find_components()/describe_components().
    K, extrinsics: this capture's intrinsics/extrinsics (project_part_to_mask
        convention -- the same one verified against the RGB in Part AA).
    instruction: raw task instruction text.
    vlm_config: config.vlm (VLMConfig); required unless dry=True.
    dry: if True, build the overlay and prompt but make NO API call.

    Returns dict(outcome, region_index, chosen, candidates, marked_pil, prompt, note).
    outcome is one of SELECTED / EVIDENCE_GATE_REFUSED / VLM_NONE / UNPARSEABLE
    (None when dry=True, since no outcome exists yet).
    """
    if pa is None:
        raise RuntimeError("part_adaptive.py must be importable")
    h, w = rgb.shape[:2]
    candidates = build_candidates(comp, desc)
    candidates = masks_for_candidates(candidates, K, extrinsics, (h, w))
    if not candidates:
        return dict(outcome=OUTCOME_VLM_NONE, region_index=-1, chosen=None,
                    candidates=[], marked_pil=None, prompt=None,
                    note="no components produced a non-empty projected mask")

    marked = mark_image(rgb, [c["mask"] for c in candidates])
    marked = _draw_region_outlines(marked, candidates)
    positions = []
    for i, c in enumerate(candidates):
        ys, xs = np.where(c["mask"])
        positions.append((i, float(xs.mean()), float(ys.mean())))
    marked, nudged = _resolve_label_collisions(marked, positions)
    if nudged:
        print("[som_part_selection] label collision(s) resolved for region(s): %s"
              % sorted(nudged))
    prompt = build_prompt(instruction, candidates)

    if dry:
        return dict(outcome=None, region_index=None, chosen=None,
                    candidates=candidates, marked_pil=marked, prompt=prompt,
                    note="dry run -- no API call made")

    region, reason = ask_vlm_task_region(vlm_config, marked, instruction, candidates)
    if region == -2:
        return dict(outcome=OUTCOME_UNPARSEABLE, region_index=-2, chosen=None,
                    candidates=candidates, marked_pil=marked, prompt=prompt, note=reason)
    if region is None or region < 0 or region >= len(candidates):
        return dict(outcome=OUTCOME_VLM_NONE, region_index=region, chosen=None,
                    candidates=candidates, marked_pil=marked, prompt=prompt, note=reason)

    chosen = candidates[region]
    if chosen["evidence"] == "NOISE":
        # ANr2/AP4: the VLM picked a region below the evidence floor. This is
        # a legitimate outcome, logged distinctly from VLM_NONE -- the model
        # made an instruction-driven choice; geometry says it isn't resolvable.
        return dict(outcome=OUTCOME_EVIDENCE_GATE_REFUSED, region_index=region,
                    chosen=chosen, candidates=candidates, marked_pil=marked,
                    prompt=prompt, note=reason)
    return dict(outcome=OUTCOME_SELECTED, region_index=region, chosen=chosen,
                candidates=candidates, marked_pil=marked, prompt=prompt, note=reason)


# =====================================================================
#  Point-based affordance selection (added this session, Part BI/BH)
#
#  Design basis, kept here rather than only in the task transcript:
#  - Set-of-Mark (Yang et al. 2023) degrades when many marks must fit a
#    small object and depends on the model's OCR of the marks themselves --
#    demonstrated directly this session (Parts AX/BA/BB: label collisions,
#    duplicate digits, occlusion by draw order all traced to needing the
#    model to read small numbered tags packed onto a small object).
#  - MOKA (Liu et al.) converts affordance reasoning to VQA over a compact
#    POINT representation rather than a numbered menu of regions.
#  - RoboPoint (Yuan et al., CoRL 2024) instruction-tunes a VLM to emit
#    keypoint affordances and beats GPT-4o by 21.8% on affordance accuracy
#    -- i.e. GPT-4o pointing is the BASELINE condition in that paper's own
#    comparison table, not the proposed method. Reflected in Part BK: GPT-4o
#    pointing (this code path) is labelled condition C (baseline), not
#    presented as state of the art.
#  - Molmo/PixMo (Deitke et al. 2024, arXiv:2409.17146) emits points
#    natively in a NORMALISED image frame -- the 0-1000 scale used in the
#    prompt below mirrors that convention so the same point-mapping code
#    (normalized_points_to_full_image / assign_points_to_candidates) can be
#    reused unchanged for a Molmo condition (Part BJ) without writing a
#    second geometry path.
#  - UNLIKE pure-2D pointing methods, the returned point is never
#    back-projected into 3D via a depth heuristic of its own. It only
#    SELECTS among the 3D structural components find_components() already
#    computed, via the same project_points_to_pixels/project_part_to_mask
#    round-trip verified against the RGB in Part AA -- the point is a 2D
#    selector over existing 3D geometry, not an independent 2D->3D estimate.
# =====================================================================

OUTCOME_POINT_SELECTED = "SELECTED"
OUTCOME_POINT_SPLIT = "SPLIT"
OUTCOME_POINT_SELECTED_NEAREST = "SELECTED_NEAREST"
OUTCOME_POINT_OFF_OBJECT = "POINT_OFF_OBJECT"
OUTCOME_POINT_VLM_NONE = "VLM_NONE"
OUTCOME_POINT_EVIDENCE_GATE_REFUSED = "EVIDENCE_GATE_REFUSED"
OUTCOME_POINT_UNPARSEABLE = "UNPARSEABLE"

OFF_OBJECT_PX = 20.0


def crop_union_bbox(rgb, candidates, expand_frac=0.6):
    """Crop to the union of all candidate masks, expanded by expand_frac on
    each side (Part BH2's arithmetic). Returns
    (crop_rgb, col_origin, row_origin, crop_w, crop_h).
    """
    H, W = rgb.shape[:2]
    union = np.zeros((H, W), dtype=bool)
    for c in candidates:
        union |= c["mask"]
    rows, cols = np.where(union)
    col_min, col_max = int(cols.min()), int(cols.max())
    row_min, row_max = int(rows.min()), int(rows.max())
    pad_w = int(round(expand_frac * (col_max - col_min)))
    pad_h = int(round(expand_frac * (row_max - row_min)))
    c0 = max(0, col_min - pad_w); r0 = max(0, row_min - pad_h)
    c1 = min(W - 1, col_max + pad_w); r1 = min(H - 1, row_max + pad_h)
    crop = rgb[r0:r1 + 1, c0:c1 + 1]
    return crop, c0, r0, crop.shape[1], crop.shape[0]


def upscale_long_side(crop_pil, target_long_side=1024):
    """BM3: upscale so the LONG side is target_long_side px, LANCZOS,
    aspect ratio preserved. Returns the upscaled PIL image. Does NOT change
    the coordinate math anywhere -- normalized_points_to_full_image must
    keep using the ORIGINAL (pre-upscale) crop_w/crop_h, since normalised
    0-1000 coordinates are scale-invariant by construction (they are
    fractions of the image shown, not pixel counts) -- upscaling changes
    what the model SEES, not what "x=1000" MEANS."""
    from PIL import Image
    w, h = crop_pil.size
    long_side = max(w, h)
    if long_side <= 0:
        return crop_pil
    scale = target_long_side / float(long_side)
    new_w, new_h = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    return crop_pil.resize((new_w, new_h), Image.LANCZOS)


def build_point_prompt(instruction):
    """Literature-following point-affordance prompt (BI3): normalised
    0-1000 coordinates, up to 3 points, no part vocabulary anywhere."""
    return (
        "The image shows an object a robot is about to grasp.\n"
        "Instruction: \"%s\"\n"
        "Identify up to 3 points on the object where the robot should place "
        "its gripper.\n"
        "Give each point in normalised coordinates on a 0-1000 scale, where "
        "x=0 is the left edge, x=1000 the right edge, y=0 the top edge, "
        "y=1000 the bottom edge of THIS image.\n"
        "Respond ONLY with JSON:\n"
        "{\"points\": [[x, y], ...], \"reason\": \"<short>\"}\n"
        "If no point on this object is appropriate for the instruction, "
        "return {\"points\": [], \"reason\": \"<short>\"}."
        % instruction
    )


def normalized_points_to_full_image(points_1000, crop_w, crop_h, col_origin, row_origin):
    """BI4: normalised [x,y] (0-1000, crop-relative) -> full-image (col,row).
    x is horizontal (col), y is vertical (row) -- the u/col, v/row
    convention confirmed against the actual project_part_to_mask code in
    Part BH1 (mask[vi, ui] = 1 -> v is the row index, u is the column
    index)."""
    out = []
    for x, y in points_1000:
        col = col_origin + (x / 1000.0) * crop_w
        row = row_origin + (y / 1000.0) * crop_h
        out.append((col, row))
    return out


def ask_vlm_points(vlm_config, crop_pil, instruction):
    """GPT-4o point-affordance call on the UNANNOTATED crop -- no marks, no
    numbers, no tint (BI2). Mirrors AffordanceReasoner._call_vlm's client
    construction; degrades the same way (empty client warning) with no API
    key configured. Returns (points_1000, reason); points_1000 is None if
    unparseable or no client was available (reason distinguishes the two)."""
    if OpenAI is None or not vlm_config.api_key:
        print("[som_part_selection] WARNING: no OPENAI_API_KEY / openai package "
              "-- cannot run point-affordance selection.")
        return None, "no_vlm_client"
    prompt = build_point_prompt(instruction)
    client = OpenAI(api_key=vlm_config.api_key)
    buf = io.BytesIO()
    crop_pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    response = client.chat.completions.create(
        model=vlm_config.model_name,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,%s" % b64,
                                                 "detail": "high"}},
        ]}],
        max_tokens=200, temperature=0.0,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        data = json.loads(text.strip())
        return data.get("points", []), data.get("reason", "")
    except Exception as e:
        print("[som_part_selection] unparseable VLM response: %r (%s)" % (text, e))
        return None, "unparseable"


def _nearest_mask_distance(mask, col, row):
    """Distance in px from (col,row) to the nearest True pixel of mask."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return float("inf")
    d = np.sqrt((xs - col) ** 2 + (ys - row) ** 2)
    return float(d.min())


def assign_points_to_candidates(full_image_points, candidates, off_object_px=OFF_OBJECT_PX):
    """BI5: assign each (col,row) point independently to the candidate whose
    mask contains it; if none contains it, to the NEAREST mask, recording
    the distance in px. A point farther than off_object_px from every mask
    is flagged off_object rather than force-assigned."""
    assignments = []
    for (col, row) in full_image_points:
        ci = int(round(col)); ri = int(round(row))
        contained = None
        for idx, c in enumerate(candidates):
            h, w = c["mask"].shape
            if 0 <= ri < h and 0 <= ci < w and c["mask"][ri, ci]:
                contained = idx
                break
        if contained is not None:
            assignments.append(dict(col=col, row=row, candidate_index=contained,
                                    candidate_name=candidates[contained]["name"],
                                    method="contains", distance_px=0.0, off_object=False))
            continue
        best_idx, best_dist = None, float("inf")
        for idx, c in enumerate(candidates):
            d = _nearest_mask_distance(c["mask"], col, row)
            if d < best_dist:
                best_idx, best_dist = idx, d
        off = best_idx is None or best_dist > off_object_px
        assignments.append(dict(col=col, row=row,
                                candidate_index=(None if off else best_idx),
                                candidate_name=(None if off else candidates[best_idx]["name"]),
                                method=("off_object" if off else "nearest"),
                                distance_px=best_dist, off_object=off))
    return assignments


def classify_point_outcome(assignments, candidates):
    """BI6/BI7: aggregate per-point assignments into ONE outcome. Does not
    silently majority-vote when points disagree -- that case is reported as
    SPLIT with every component's point count."""
    if not assignments:
        return dict(outcome=OUTCOME_POINT_VLM_NONE, chosen=None, split=None,
                    note="empty points list")
    on_object = [a for a in assignments if not a["off_object"]]
    if not on_object:
        return dict(outcome=OUTCOME_POINT_OFF_OBJECT, chosen=None, split=None,
                    note="all %d point(s) >%.0fpx from every candidate mask"
                    % (len(assignments), OFF_OBJECT_PX))
    distinct = sorted(set(a["candidate_name"] for a in on_object))
    if len(distinct) > 1:
        counts = {name: sum(1 for a in on_object if a["candidate_name"] == name)
                 for name in distinct}
        return dict(outcome=OUTCOME_POINT_SPLIT, chosen=None, split=counts,
                    note="points disagree across components: %s" % counts)
    name = distinct[0]
    chosen = next(c for c in candidates if c["name"] == name)
    used_nearest = any(a["method"] == "nearest" for a in on_object)
    if chosen["evidence"] == "NOISE":
        return dict(outcome=OUTCOME_POINT_EVIDENCE_GATE_REFUSED, chosen=chosen, split=None,
                    note="assigned component '%s' is NOISE evidence" % name)
    if used_nearest:
        max_d = max(a["distance_px"] for a in on_object if a["method"] == "nearest")
        return dict(outcome=OUTCOME_POINT_SELECTED_NEAREST, chosen=chosen, split=None,
                    note="nearest-mask assignment, max distance %.1fpx" % max_d)
    return dict(outcome=OUTCOME_POINT_SELECTED, chosen=chosen, split=None, note="")


def select_point_via_geometric_affordance(rgb, comp, desc, K, extrinsics, instruction,
                                          vlm_config=None, dry=False, expand_frac=0.6):
    """Point-based affordance selection (Part BI, resolution fixed in BM).
    Crops to the union of all candidate masks -- UNANNOTATED, no
    marks/tint/numbers -- upscales the crop so its long side is 1024px
    (LANCZOS) before sending, asks the VLM for up to 3 normalised points,
    converts them to full-image pixels USING THE ORIGINAL (pre-upscale)
    crop dimensions (BM3 -- normalised 0-1000 coordinates are fractions of
    the shown image, scale-invariant by construction, so the conversion
    must not use the upscaled size), and assigns each point independently
    to a 3D structural component via its projected mask.
    """
    if pa is None:
        raise RuntimeError("part_adaptive.py must be importable")
    candidates = build_candidates(comp, desc)
    candidates = masks_for_candidates(candidates, K, extrinsics, rgb.shape[:2])
    if not candidates:
        return dict(outcome=OUTCOME_POINT_VLM_NONE, chosen=None, split=None,
                    candidates=[], crop=None, crop_sent=None, crop_origin=None,
                    crop_size=None, crop_sent_size=None, prompt=None,
                    raw_points_1000=None, full_image_points=None,
                    assignments=None, reason="",
                    note="no components produced a non-empty projected mask")

    crop_arr, c0, r0, cw, ch = crop_union_bbox(rgb, candidates, expand_frac)
    from PIL import Image
    crop_pil = Image.fromarray(crop_arr)          # ORIGINAL -- coordinate math uses this size
    crop_sent = upscale_long_side(crop_pil)         # UPSCALED -- what is actually POSTed
    prompt = build_point_prompt(instruction)

    if dry:
        return dict(outcome=None, chosen=None, split=None, candidates=candidates,
                    crop=crop_pil, crop_sent=crop_sent, crop_origin=(c0, r0),
                    crop_size=(cw, ch), crop_sent_size=crop_sent.size,
                    prompt=prompt, raw_points_1000=None, full_image_points=None,
                    assignments=None, reason="", note="dry run -- no API call made")

    points_1000, reason = ask_vlm_points(vlm_config, crop_sent, instruction)
    if points_1000 is None:
        outcome = OUTCOME_POINT_UNPARSEABLE if reason == "unparseable" else OUTCOME_POINT_VLM_NONE
        return dict(outcome=outcome, chosen=None, split=None, candidates=candidates,
                    crop=crop_pil, crop_sent=crop_sent, crop_origin=(c0, r0),
                    crop_size=(cw, ch), crop_sent_size=crop_sent.size,
                    prompt=prompt, raw_points_1000=None, full_image_points=None,
                    assignments=None, reason=reason, note=reason)

    # BM3 verification, explicit: normalized_points_to_full_image is called
    # with (cw, ch) -- the ORIGINAL crop's width/height -- never crop_sent's.
    full_points = normalized_points_to_full_image(points_1000, cw, ch, c0, r0)
    assignments = assign_points_to_candidates(full_points, candidates)
    result = classify_point_outcome(assignments, candidates)
    result.update(candidates=candidates, crop=crop_pil, crop_sent=crop_sent,
                  crop_origin=(c0, r0), crop_size=(cw, ch),
                  crop_sent_size=crop_sent.size, prompt=prompt,
                  raw_points_1000=points_1000, full_image_points=full_points,
                  assignments=assignments, reason=reason)
    return result


def _load_and_isolate(cap_path):
    """Load a cap_*.npz capture and isolate the largest object via
    scene_objects -- the same seedless method fig_intent_dissection.py /
    analyse_range.py use, appropriate here because selecting the part is the
    whole point: no prior VLM-grounded affordance centre exists yet to seed
    part_adaptive's adaptive_crop path."""
    from scipy.spatial.transform import Rotation
    from intent_grasp import scene_objects as so
    FLIP = np.diag([1.0, -1.0, -1.0, 1.0])
    d = np.load(cap_path, allow_pickle=True)
    rgb = np.asarray(d["rgb"])
    R = Rotation.from_quat(np.asarray(d["tf_quat"], float).ravel()).as_matrix()
    t = np.asarray(d["tf_trans"], float).ravel()
    depth = d["depth"].astype(float)
    K = np.asarray(d["K"], float)
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = t
    extr = FLIP @ np.linalg.inv(T)
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (depth > 0.05) & (depth < 4.0)
    z = depth[ok]
    x = (u[ok] - K[0, 2]) * z / K[0, 0]
    y = (v[ok] - K[1, 2]) * z / K[1, 1]
    pts = (R @ np.stack([x, y, z], -1).T).T + t

    table, objs = so.find_objects(pts)
    if table is None or not objs:
        raise SystemExit("no table/object found in %s" % cap_path)
    obj = objs[0]["points"]
    plane_z = table["plane_z"]
    comp, info = pa.find_components(obj, z_table=plane_z)
    desc = pa.describe_components(comp, info)
    return rgb, comp, desc, K, extr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", required=True, help="cap_*.npz capture file")
    ap.add_argument("--instruction", required=True)
    ap.add_argument("--out", default=None, help="overlay/crop output path")
    ap.add_argument("--mode", choices=["som", "point"], default="som",
                    help="'som' = numbered-region selector (AN/AX/BA/BB); "
                         "'point' = point-based affordance selector (BI)")
    ap.add_argument("--dry", action="store_true",
                    help="build overlay/crop + prompt, make NO API call")
    a = ap.parse_args()

    rgb, comp, desc, K, extr = _load_and_isolate(a.cap)
    print("components found: %s" % sorted(comp.keys()))

    vlm_config = None
    if not a.dry:
        from intent_grasp.config import VLMConfig
        vlm_config = VLMConfig()
        vlm_config.api_key = vlm_config.api_key or os.environ.get("OPENAI_API_KEY", "")

    tag = os.path.basename(a.cap).replace("cap_", "").replace(".npz", "")

    if a.mode == "point":
        result = select_point_via_geometric_affordance(
            rgb, comp, desc, K, extr, a.instruction, vlm_config=vlm_config, dry=a.dry)
        out = a.out or os.path.join(
            "report_assets", "figures", "fig_stage3c_point_crop_%s.png" % tag)
        if result["crop_sent"] is not None:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            result["crop_sent"].save(out)
            print("wrote crop (as SENT, upscaled) -> %s  origin=%s  "
                  "original_size=%s  sent_size=%s"
                  % (out, result["crop_origin"], result["crop_size"], result["crop_sent_size"]))
        print()
        if a.dry:
            print("--- prompt (DRY -- no API call made) ---")
            print(result["prompt"])
        else:
            print("outcome: %s  note=%s" % (result["outcome"], result["note"]))
            print("raw normalised points (0-1000): %s" % result["raw_points_1000"])
            print("full-image points (col,row): %s" % result["full_image_points"])
            if result["assignments"]:
                for a_ in result["assignments"]:
                    print("  point (%.1f,%.1f) -> %s  method=%s  dist_px=%.1f  off_object=%s"
                          % (a_["col"], a_["row"], a_["candidate_name"], a_["method"],
                             a_["distance_px"], a_["off_object"]))
            if result["chosen"] is not None:
                c = result["chosen"]
                print("chosen component: %s  n=%d  width_mm=%d  evidence=%s"
                      % (c["name"], c["n"], c["width_mm"], c["evidence"]))
        return

    result = select_region_via_geometric_som(
        rgb, comp, desc, K, extr, a.instruction, vlm_config=vlm_config, dry=a.dry)

    out = a.out or os.path.join(
        "report_assets", "figures", "fig_stage3b_som_marks_%s.png" % tag)
    if result["marked_pil"] is not None:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        result["marked_pil"].save(out)
        print("wrote %s" % out)

    print()
    print("--- region list ---")
    print(format_region_list(result["candidates"]))
    print()
    if a.dry:
        print("--- prompt (DRY -- no API call made) ---")
        print(result["prompt"])
    else:
        print("outcome: %s  region=%s  note=%s" %
              (result["outcome"], result["region_index"], result["note"]))
        if result["chosen"] is not None:
            c = result["chosen"]
            print("chosen component: %s  n=%d  width_mm=%d  evidence=%s" %
                  (c["name"], c["n"], c["width_mm"], c["evidence"]))


if __name__ == "__main__":
    main()
