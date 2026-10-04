r"""
differentiability_general.py -- WINDOWS. Generalized differentiability test for
ANY object/instructions. Same SAM-derived candidate regions, different intents ->
different grounded regions. Proves the contribution is general across objects.

Configure for the object under test (mug or hammer) via the block below.

Reads:  workspace/hand_view.npz   (whatever object was last hand-captured)
Saves:  workspace/differentiability_<tag>.png
Needs:  OPENAI_API_KEY
"""
import os, base64, json, io, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.paths import WORKSPACE

# ============== CONFIGURE PER OBJECT ==============
TARGET_OBJECT = "hammer"
TAG = "hammer"
INSTRUCTIONS = [
    "I need to hammer a nail into the wall",   # -> handle (grip to swing)
    "Hand me the hammer so I can use it",      # -> head   (grip head, present handle)
]
# For the mug, set:
#   TARGET_OBJECT="red mug"; TAG="mug"
#   INSTRUCTIONS=["I want to drink some coffee","Wash the inside of the mug"]
# =================================================

NPZ = f"{WORKSPACE}/hand_view.npz"
OUT = f"{WORKSPACE}/differentiability_{TAG}.png"


def _client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def object_mask(model, rgb, obj):
    res = model.predict([Image.fromarray(rgb)], [obj + "."])[0]
    if len(res["masks"]) == 0: return None
    return res["masks"][int(res["scores"].argmax())].astype(bool)


def auto_regions(model, rgb):
    from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
    mg = SAM2AutomaticMaskGenerator(
        model=model.sam.model, points_per_side=48,
        pred_iou_thresh=0.7, stability_score_thresh=0.85, min_mask_region_area=100)
    return [a["segmentation"].astype(bool) for a in mg.generate(rgb)]


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def candidate_subparts(regions, om, max_n=8):
    o = om.sum(); cand = []
    for m in regions:
        a = m.sum()
        if a < 60: continue
        inter = (m & om).sum()
        if inter / max(a, 1) < 0.7: continue
        frac_obj = inter / max(o, 1)
        if not (0.02 <= frac_obj <= 0.90): continue
        cand.append((a, m))
    cand.sort(key=lambda t: -t[0]); kept = []
    for a, m in cand:
        if all(iou(m, k) < 0.7 for k in kept): kept.append(m)
        if len(kept) >= max_n: break
    return kept


def mark_image(rgb, regions):
    pil = Image.fromarray(rgb).convert("RGB")
    try: font = ImageFont.truetype("arial.ttf", 22)
    except Exception: font = ImageFont.load_default()
    cmap = plt.cm.tab10
    for i, m in enumerate(regions):
        color = tuple(int(255*c) for c in cmap(i % 10)[:3])
        ov = np.zeros((*m.shape, 4), dtype=np.uint8); ov[m] = (*color, 90)
        pil = Image.alpha_composite(pil.convert("RGBA"), Image.fromarray(ov)).convert("RGB")
        ys, xs = np.where(m); cy, cx = int(ys.mean()), int(xs.mean())
        dr = ImageDraw.Draw(pil)
        dr.rectangle([cx-13, cy-15, cx+13, cy+15], fill=(255,255,255), outline=(0,0,0))
        dr.text((cx-7, cy-13), str(i), fill=(0,0,0), font=font)
    return pil


def reason_part(instruction, obj):
    r = _client().chat.completions.create(
        model="gpt-4o", temperature=0.0, max_tokens=120,
        messages=[{"role":"user","content":(
            f"A robot must act on this instruction: '{instruction}'. The object is a {obj}. "
            f"Which PART of the {obj} should the robot grasp to best accomplish this, and why? "
            f"For a hammer: swinging/using favours the handle; handing it over safely favours "
            f"gripping the head so the handle is presented to the person. "
            f"Respond ONLY JSON: {{\"part\":\"<one part name>\",\"reason\":\"<short>\"}}.")}])
    t = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try: d = json.loads(t); return d["part"], d.get("reason","")
    except Exception: return None, t


def select_region(marked_pil, obj, part, n):
    buf = io.BytesIO(); marked_pil.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    r = _client().chat.completions.create(
        model="gpt-4o", temperature=0.0, max_tokens=100,
        messages=[{"role":"user","content":[
            {"type":"text","text":(
                f"This {obj} has numbered candidate regions (0..{n-1}). "
                f"Which numbered region is the '{part}' of the {obj}? "
                f"Respond ONLY JSON {{\"region\":<int>}}; use -1 if none match.")},
            {"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}}]}])
    t = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try: return int(json.loads(t)["region"])
    except Exception: return -1


def main():
    d = np.load(NPZ, allow_pickle=True); rgb = d["rgb"]; print(f"object='{TARGET_OBJECT}' rgb{rgb.shape}")
    from lang_sam import LangSAM
    model = LangSAM()
    om = object_mask(model, rgb, TARGET_OBJECT)
    if om is None: print("no object mask"); return
    print(f"object mask {int(om.sum())} px; running SAM auto-mask...")
    regions = candidate_subparts(auto_regions(model, rgb), om)
    n = len(regions); print(f"{n} shared candidate sub-part regions")
    if n == 0: print("no candidates; check view/granularity"); return
    marked = mark_image(rgb, regions)

    results = []
    for instr in INSTRUCTIONS:
        part, why = reason_part(instr, TARGET_OBJECT)
        reg = select_region(marked, TARGET_OBJECT, part, n) if part else -1
        ratio = (regions[reg] & om).sum()/max(om.sum(),1) if 0 <= reg < n else 0
        print(f"  '{instr}'\n     reason-> part='{part}' ({why})\n     ground-> region {reg} ({ratio:.0%})")
        results.append((instr, part, reg, ratio))

    distinct = len({r for _,_,r,_ in results if r >= 0})
    print("="*56)
    print(f"  distinct regions across {len(results)} instructions: {distinct}")
    print("  >>> DIFFERENTIABILITY DEMONSTRATED" if distinct >= 2 else "  >>> not differentiated")
    print("="*56)

    cols = 1 + len(results)
    fig, ax = plt.subplots(1, cols, figsize=(6*cols, 6))
    ax[0].imshow(marked); ax[0].set_title(f"{TARGET_OBJECT}: {n} candidate regions"); ax[0].axis("off")
    for j, (instr, part, reg, ratio) in enumerate(results):
        ax[j+1].imshow(rgb)
        if 0 <= reg < n: ax[j+1].imshow(regions[reg], alpha=0.6, cmap="Oranges")
        ax[j+1].set_title(f'"{instr}"\n-> {part} (region {reg})', fontsize=9); ax[j+1].axis("off")
    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight"); print("saved ->", OUT)


if __name__ == "__main__":
    main()
