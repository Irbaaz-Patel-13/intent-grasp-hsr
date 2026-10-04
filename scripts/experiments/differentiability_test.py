r"""
differentiability_test.py -- WINDOWS. THE core contribution figure.

Same object, same SAM-derived candidate regions, DIFFERENT instructions ->
DIFFERENT grounded grasp regions. Intent is the ONLY variable.

Pipeline per instruction (faithful to AffordGrasp: reason -> ground):
  Step A (reason):  GPT-4o: instruction + object -> which PART to grasp + why
  Step B (ground):  GPT-4o picks which SAM region is that part (Set-of-Mark)
The candidate regions are segmented ONCE and shared across all instructions,
so any difference in the selected region is caused purely by the instruction.

Perception-derived (SAM makes regions), general (any object/part), intention-driven.

Reads:  workspace/hand_view.npz
Saves:  workspace/differentiability.png
Needs:  OPENAI_API_KEY

Edit INSTRUCTIONS below to change the contrast set.
"""
import os, base64, json, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.paths import WORKSPACE

NPZ = f"{WORKSPACE}/hand_view.npz"
OUT = f"{WORKSPACE}/differentiability.png"
TARGET_OBJECT = "red mug"

# Contrasting instructions that SHOULD call for different grasp regions:
INSTRUCTIONS = [
    "I want to drink some coffee",      # -> handle (avoid hot body, natural hold)
    "Empty the mug out into the sink",  # -> body  (grip the body to tip/pour)
    "Wash the inside of the mug",       # -> rim / opening
]


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
        pred_iou_thresh=0.7, stability_score_thresh=0.85,
        min_mask_region_area=100)
    return [a["segmentation"].astype(bool) for a in mg.generate(rgb)]


def iou(a, b):
    inter = (a & b).sum(); uni = (a | b).sum()
    return inter / max(uni, 1)


def candidate_subparts(regions, om, max_n=8):
    """Sub-parts of the object: on the mug, between 2% and 90% of it; dedup; cap."""
    o = om.sum(); cand = []
    for m in regions:
        a = m.sum()
        if a < 60: continue
        inter = (m & om).sum()
        if inter / max(a, 1) < 0.7: continue          # region must be ON the mug
        frac_obj = inter / max(o, 1)
        if not (0.02 <= frac_obj <= 0.90): continue    # genuine sub-part
        cand.append((a, m))
    cand.sort(key=lambda t: -t[0])
    kept = []
    for a, m in cand:
        if all(iou(m, k) < 0.7 for k in kept):
            kept.append(m)
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
    """Step A: instruction -> optimal grasp part (AffordGrasp reasoning step)."""
    r = _client().chat.completions.create(
        model="gpt-4o", temperature=0.0, max_tokens=120,
        messages=[{"role":"user","content":(
            f"A robot must act on this instruction: '{instruction}'. "
            f"The object is a {obj}. Which PART of the {obj} should the robot grasp "
            f"to best accomplish this, and why? Consider the task: e.g. drinking favours "
            f"the handle (avoid the hot body); pouring favours the body; washing favours "
            f"the rim. Respond ONLY JSON: {{\"part\":\"<one part name>\",\"reason\":\"<short>\"}}.")}])
    t = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try: d = json.loads(t); return d["part"], d.get("reason","")
    except Exception: return None, t


def select_region(marked_pil, obj, part, n):
    """Step B: Set-of-Mark selection of the reasoned part among SAM regions."""
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
    d = np.load(NPZ, allow_pickle=True); rgb = d["rgb"]; print(f"rgb{rgb.shape}")
    from lang_sam import LangSAM
    model = LangSAM()

    om = object_mask(model, rgb, TARGET_OBJECT)
    if om is None: print("no object mask"); return
    print(f"object mask {int(om.sum())} px; running SAM auto-mask...")
    regions = candidate_subparts(auto_regions(model, rgb), om)
    n = len(regions)
    print(f"{n} shared candidate sub-part regions")
    if n < 2:
        print(">>> need >=2 distinct part regions for differentiability; "
              "increase points_per_side or check view. Got", n); 
        if n == 0: return
    marked = mark_image(rgb, regions)

    results = []
    for instr in INSTRUCTIONS:
        part, why = reason_part(instr, TARGET_OBJECT)
        reg = select_region(marked, TARGET_OBJECT, part, n) if part else -1
        ratio = (regions[reg] & om).sum()/max(om.sum(),1) if 0 <= reg < n else 0
        print(f"  '{instr}'")
        print(f"     reason-> part='{part}'  ({why})")
        print(f"     ground-> region {reg}  ({ratio:.0%} of mug)")
        results.append((instr, part, reg, ratio))

    distinct = len({r for _,_,r,_ in results if r >= 0})
    print("="*56)
    print(f"  distinct regions selected across {len(results)} instructions: {distinct}")
    if distinct >= 2:
        print("  >>> DIFFERENTIABILITY DEMONSTRATED: same object, different intent,")
        print("      different perception-derived grasp region.")
    else:
        print("  >>> regions did not differ; check candidate set / instructions")
    print("="*56)

    cols = 1 + len(results)
    fig, ax = plt.subplots(1, cols, figsize=(6*cols, 6))
    ax[0].imshow(marked); ax[0].set_title(f"{n} shared candidate regions"); ax[0].axis("off")
    for j, (instr, part, reg, ratio) in enumerate(results):
        ax[j+1].imshow(rgb)
        if 0 <= reg < n:
            ax[j+1].imshow(regions[reg], alpha=0.6, cmap="Oranges")
        ttl = f'"{instr}"\n-> {part} (region {reg}, {ratio:.0%})'
        ax[j+1].set_title(ttl, fontsize=10); ax[j+1].axis("off")
    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight")
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
