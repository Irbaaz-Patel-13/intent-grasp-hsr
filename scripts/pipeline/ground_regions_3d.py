r"""
ground_regions_3d.py -- WINDOWS .venv (step 2 of 3).
Reads the head capture, runs Set-of-Mark per instruction (the method that worked),
back-projects each selected region to a 3D centroid in odom, writes the targets.

  cd workspace/
  set OPENAI_API_KEY=your-key   (or $env: in PowerShell)
  python ground_regions_3d.py --object "red mug" ^
      --instr "I want to drink some coffee" --instr "Wash the inside of the mug"

Reads:  workspace/head_capture.npz   (from step 1)
Saves:  workspace/region_targets.npz (per-instruction 3D targets for IK)
        workspace/region_targets.png (marked regions + chosen, for your eye)
Then copy region_targets.npz back to the container (step 3).
"""
import os, io, json, base64, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.paths import WORKSPACE

NPZ = f"{WORKSPACE}/head_capture.npz"
OUT = f"{WORKSPACE}/region_targets.npz"
FIG = f"{WORKSPACE}/region_targets.png"


def _client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def object_mask(model, rgb, obj):
    res = model.predict([Image.fromarray(rgb)], [obj + "."])[0]
    if len(res["masks"]) == 0: return None
    return res["masks"][int(res["scores"].argmax())].astype(bool)

def auto_regions(model, rgb):
    from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
    mg = SAM2AutomaticMaskGenerator(model=model.sam.model, points_per_side=48,
        pred_iou_thresh=0.7, stability_score_thresh=0.85, min_mask_region_area=100)
    return [a["segmentation"].astype(bool) for a in mg.generate(rgb)]

def _iou(a, b): return (a & b).sum() / max((a | b).sum(), 1)

def candidate_subparts(regions, om, max_n=8):
    o = om.sum(); cand = []
    for m in regions:
        a = m.sum()
        if a < 60: continue
        inter = (m & om).sum()
        if inter / max(a, 1) < 0.7: continue
        if not (0.02 <= inter / max(o, 1) <= 0.90): continue
        cand.append((a, m))
    cand.sort(key=lambda t: -t[0]); kept = []
    for a, m in cand:
        if all(_iou(m, k) < 0.7 for k in kept): kept.append(m)
        if len(kept) >= max_n: break
    return kept

def mark_image(rgb, regions):
    pil = Image.fromarray(rgb).convert("RGB")
    try: font = ImageFont.truetype("arial.ttf", 22)
    except Exception: font = ImageFont.load_default()
    cmap = plt.cm.tab10
    for i, m in enumerate(regions):
        color = tuple(int(255*c) for c in cmap(i % 10)[:3])
        ov = np.zeros((*m.shape, 4), np.uint8); ov[m] = (*color, 90)
        pil = Image.alpha_composite(pil.convert("RGBA"), Image.fromarray(ov)).convert("RGB")
        ys, xs = np.where(m); cy, cx = int(ys.mean()), int(xs.mean())
        dr = ImageDraw.Draw(pil)
        dr.rectangle([cx-13, cy-15, cx+13, cy+15], fill=(255,255,255), outline=(0,0,0))
        dr.text((cx-7, cy-13), str(i), fill=(0,0,0), font=font)
    return pil

def reason_part(instr, obj):
    r = _client().chat.completions.create(model="gpt-4o", temperature=0.0, max_tokens=120,
        messages=[{"role":"user","content":(
            f"A robot must act on: '{instr}'. The object is a {obj}. Which PART should it "
            f"grasp to best accomplish this? Respond ONLY JSON {{\"part\":\"<name>\",\"reason\":\"<short>\"}}.")}])
    t = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try: d = json.loads(t); return d["part"], d.get("reason","")
    except Exception: return None, t

def select_region(marked, obj, part, n):
    buf = io.BytesIO(); marked.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    r = _client().chat.completions.create(model="gpt-4o", temperature=0.0, max_tokens=80,
        messages=[{"role":"user","content":[
            {"type":"text","text":(f"This {obj} has numbered regions 0..{n-1}. Which is the '{part}'? "
                f"Respond ONLY JSON {{\"region\":<int>}}; -1 if none.")},
            {"type":"image_url","image_url":{"url":f"data:image/png;base64,{b64}"}}]}])
    t = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try: return int(json.loads(t)["region"])
    except Exception: return -1

def centroid_3d(mask, depth, K, T):
    ys, xs = np.where(mask); z = depth[ys, xs]
    ok = np.isfinite(z) & (z > 0.1) & (z < 3.0)
    if ok.sum() < 20: return None, 0
    xs, ys, z = xs[ok], ys[ok], z[ok]
    fx, fy, cx, cy = K[0,0], K[1,1], K[0,2], K[1,2]
    X = (xs - cx) * z / fx; Y = (ys - cy) * z / fy
    pc = np.stack([X, Y, z, np.ones_like(z)], 0)
    po = (T @ pc)[:3].T
    return np.median(po, axis=0), int(ok.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", required=True)
    ap.add_argument("--instr", action="append", required=True)
    args = ap.parse_args()

    d = np.load(NPZ, allow_pickle=True)
    rgb, depth = d["rgb"], d["depth"]; K = d["camera_intrinsics"]; T = d["T_odom_cam"]
    print(f"loaded head_capture: rgb{rgb.shape} depth{depth.shape}")

    from lang_sam import LangSAM
    model = LangSAM()
    om = object_mask(model, rgb, args.object)
    if om is None: print("no object mask"); return
    regions = candidate_subparts(auto_regions(model, rgb), om)
    n = len(regions); print(f"{n} shared candidate sub-part regions")
    if n == 0:
        print(">>> SoM found no sub-parts on the head view. The head distance may be")
        print("    too far to separate parts; tell Claude and we add the hand-view bridge.")
        return
    marked = mark_image(rgb, regions)

    instrs, parts, regs, cents, npxs = [], [], [], [], []
    print("="*60)
    for instr in args.instr:
        part, why = reason_part(instr, args.object)
        reg = select_region(marked, args.object, part, n) if part else -1
        c, npx = (None, 0)
        if 0 <= reg < n:
            c, npx = centroid_3d(regions[reg], depth, K, T)
        print(f"  '{instr}'")
        print(f"     part='{part}' ({why})  -> region {reg}")
        if c is not None:
            print(f"     3D centroid odom=({c[0]:.3f},{c[1]:.3f},{c[2]:.3f})  {npx} px")
        else:
            print(f"     no valid-depth 3D centroid for this region")
        instrs.append(instr); parts.append(str(part)); regs.append(int(reg))
        cents.append(c if c is not None else np.array([np.nan]*3)); npxs.append(npx)
    print("="*60)

    np.savez(OUT, object=args.object, instructions=np.array(instrs, object),
             parts=np.array(parts, object), regions=np.array(regs),
             centroids=np.array(cents, float), npx=np.array(npxs))
    print("saved ->", OUT)

    cols = 1 + len(instrs)
    fig, ax = plt.subplots(1, cols, figsize=(5*cols, 5))
    ax[0].imshow(marked); ax[0].set_title(f"{n} candidate regions"); ax[0].axis("off")
    for j, instr in enumerate(instrs):
        ax[j+1].imshow(rgb)
        if 0 <= regs[j] < n: ax[j+1].imshow(regions[regs[j]], alpha=0.6, cmap="Oranges")
        ax[j+1].set_title(f"{parts[j]} (region {regs[j]})", fontsize=9); ax[j+1].axis("off")
    plt.tight_layout(); plt.savefig(FIG, dpi=100, bbox_inches="tight"); print("saved ->", FIG)
    print("\nnext: cp region_targets.npz back to the container, run execute_region_ik.py")


if __name__ == "__main__":
    main()
