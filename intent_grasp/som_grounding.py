r"""
som_grounding.py -- WINDOWS. Set-of-Mark grounding for the task-relevant part.

Fixes the v1-v3 failure mode: instead of asking GPT-4o to EMIT coordinates
(imprecise, ~40px off) or text-prompting GroundingDINO (collapses to whole
object), we:
  1. get a reliable whole-object mask (text 'red mug.' -- this already works)
  2. run SAM2's automatic mask generator to segment the image into REGIONS
  3. keep regions that are SUB-PARTS of the mug (overlap object, not the whole mug)
  4. overlay numbered marks on those candidate regions
  5. ask GPT-4o ONLY to pick the number that is the handle (selection, not coords)
  6. that region's mask = the affordance mask

Perception-derived (SAM makes the regions, VLM selects), general (swap the part
name for any object/part), intention-driven (part name comes from reasoning).

The marked image is itself the key diagnostic: if NO candidate region is the
handle, SoM can't help and we tune granularity / move to VLPart.

Reads:  workspace/hand_view.npz   (the clear close-up)
Saves:  workspace/som_marks.png       (numbered candidate regions)
        workspace/som_grounding.png   (chosen handle mask)
Needs:  OPENAI_API_KEY
"""
import os, base64, json, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.paths import WORKSPACE

NPZ = f"{WORKSPACE}/hand_view.npz"
MARKS = f"{WORKSPACE}/som_marks.png"
OUT   = f"{WORKSPACE}/som_grounding.png"
TARGET_OBJECT = "red mug"; TARGET_PART = "handle"


def object_mask(model, rgb, obj):
    res = model.predict([Image.fromarray(rgb)], [obj + "."])[0]
    if len(res["masks"]) == 0: return None
    return res["masks"][int(res["scores"].argmax())].astype(bool)


def auto_regions(model, rgb):
    """SAM2 automatic mask generator -> list of region masks (bool HxW)."""
    try:
        from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
        mg = SAM2AutomaticMaskGenerator(
            model=model.sam.model, points_per_side=32,
            pred_iou_thresh=0.7, stability_score_thresh=0.85,
            min_mask_region_area=150)
        anns = mg.generate(rgb)
    except Exception as e:
        print("  custom generator failed (%s); trying model.sam.generate" % e)
        anns = model.sam.generate(rgb)
    return [a["segmentation"].astype(bool) for a in anns]


def filter_subparts(regions, om):
    """Keep regions that are sub-parts of the object: mostly inside the object
    mask, but not (near-)equal to the whole object."""
    o_area = om.sum(); keep = []
    for m in regions:
        a = m.sum()
        if a < 80: continue
        inter = (m & om).sum()
        frac_in = inter / max(a, 1)          # how much of region is on the mug
        frac_obj = inter / max(o_area, 1)    # how much of the mug it covers
        if frac_in > 0.6 and frac_obj < 0.85:  # on the mug, but not the whole mug
            keep.append(m)
    return keep


def mark_image(rgb, regions):
    """Overlay numbered marks + colored outlines on each candidate region."""
    pil = Image.fromarray(rgb).convert("RGB"); dr = ImageDraw.Draw(pil, "RGBA")
    try: font = ImageFont.truetype("arial.ttf", 22)
    except Exception: font = ImageFont.load_default()
    cmap = plt.cm.tab10
    for i, m in enumerate(regions):
        color = tuple(int(255*c) for c in cmap(i % 10)[:3])
        ys, xs = np.where(m)
        cy, cx = int(ys.mean()), int(xs.mean())
        # tint
        ov = np.zeros((*m.shape, 4), dtype=np.uint8); ov[m] = (*color, 90)
        pil = Image.alpha_composite(pil.convert("RGBA"), Image.fromarray(ov)).convert("RGB")
        dr = ImageDraw.Draw(pil)
        dr.rectangle([cx-13, cy-15, cx+13, cy+15], fill=(255,255,255), outline=(0,0,0))
        dr.text((cx-7, cy-13), str(i), fill=(0,0,0), font=font)
    return pil


def ask_vlm_pick(marked_pil, obj, part, n):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    buf = io.BytesIO(); marked_pil.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    prompt = (
        f"This image of a {obj} has numbered candidate regions (0..{n-1}), each a "
        f"differently-coloured patch with its number. "
        f"Which numbered region corresponds to the {part} of the {obj} -- the curved "
        f"piece sticking out the side used for holding (NOT the body, rim, or opening)? "
        f"Respond ONLY JSON: {{\"region\":<int>,\"reason\":\"<short>\"}}. "
        f"If none of the regions is the {part}, set region to -1."
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}}]}],
        max_tokens=120, temperature=0.0)
    txt = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try:
        d = json.loads(txt); return int(d["region"]), d.get("reason","")
    except Exception as e:
        print("  unparseable:", txt, "|", e); return None, None


def main():
    d = np.load(NPZ, allow_pickle=True); rgb = d["rgb"]; print(f"rgb{rgb.shape}")
    from lang_sam import LangSAM
    model = LangSAM()

    om = object_mask(model, rgb, TARGET_OBJECT)
    if om is None: print("  no object mask"); return
    print(f"  object mask: {int(om.sum())} px")

    print("  running SAM2 automatic mask generator...")
    regions = auto_regions(model, rgb)
    print(f"  {len(regions)} raw regions")
    cand = filter_subparts(regions, om)
    print(f"  {len(cand)} candidate sub-part regions (on the mug, not the whole mug)")
    if len(cand) == 0:
        print("  >>> NO sub-part candidates -- SAM didn't separate any mug parts.")
        print("      (handle not surfaced as a region; tune granularity or use VLPart)")
        return

    marked = mark_image(rgb, cand)
    marked.save(MARKS); print(f"  saved candidate marks -> {MARKS}")

    region, reason = ask_vlm_pick(marked, TARGET_OBJECT, TARGET_PART, len(cand))
    print(f"  VLM picked region {region}  reason='{reason}'")
    if region is None or region < 0 or region >= len(cand):
        print("  >>> VLM found no handle region among candidates.")
        # still save marks for inspection
        return

    aff = cand[region]
    ratio = (aff & om).sum() / max(om.sum(), 1)
    print("="*56)
    print(f"  chosen handle mask: {int(aff.sum())} px = {ratio:.0%} of mug")
    print(f"  (head/hand text-grounding was 90-99% = COLLAPSED)")
    if ratio < 0.5:
        print("  >>> HANDLE ISOLATED via SoM -- perception-derived, VLM-selected!")
    else:
        print("  >>> chosen region too large; SAM region may merge handle+body")
    print("="*56)

    fig, ax = plt.subplots(1,3,figsize=(18,6))
    ax[0].imshow(marked); ax[0].set_title(f"{len(cand)} candidate regions"); ax[0].axis("off")
    ax[1].imshow(rgb); ax[1].imshow(om, alpha=0.4, cmap="Blues"); ax[1].set_title("object mask"); ax[1].axis("off")
    ax[2].imshow(rgb); ax[2].imshow(aff, alpha=0.6, cmap="Oranges")
    ax[2].set_title(f"chosen handle (region {region}) = {ratio:.0%} of mug"); ax[2].axis("off")
    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight")
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
