"""
segment_parts.py -- real perception for the Slide 2 motivation figure.

Reuses the repo's actual, validated grounding mechanism from som_grounding.py
(object_mask / auto_regions / filter_subparts / mark_image are imported
unchanged, not reimplemented) applied to red-mug.png:

  1. LangSAM text grounding -> whole-object mask ("coffee mug.")
     (part-level text grounding on this same image collapses to the whole
     object at ~19.2% for every part prompt -- see probe_langsam_mug.py --
     which is the documented 86-98% collapse failure mode part_adaptive.py
     exists to work around for real 3D captures. This image has no depth,
     so the repo's Set-of-Mark fallback is used instead of part_adaptive.)
  2. SAM2 automatic mask generator -> every region SAM finds in the image,
     independent of any text prompt.
  3. filter_subparts() keeps regions that sit mostly on the mug but are not
     the whole mug -- i.e. real candidate sub-parts.
  4. GPT-4o (same call convention as som_grounding.ask_vlm_pick) is shown the
     numbered candidates and asked to SELECT (not draw) the handle, then the
     rim, by number.
  5. "body" is not asked for -- it is object_mask minus whatever the VLM
     selected as handle/rim, i.e. a set-difference of two real masks.

Everything here is either a model output (GroundingDINO+SAM mask, SAM2
region, GPT-4o selection) or a boolean set operation on model outputs.
No region is hand-drawn or coordinate-tuned.

Writes into outputs/motivation/:
    object_mask.npy, handle_mask.npy, rim_mask.npy, body_mask.npy   (H,W) bool
    som_marks.png            numbered SAM candidate regions (diagnostic)
    segmentation_report.json  what was picked and why
"""
import os
import sys
import json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from intent_grasp import som_grounding as som  # object_mask, auto_regions, filter_subparts, mark_image

IMG_PATH = os.path.join(ROOT, "red-mug.png")


def load_rgb_on_white(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(bg, im).convert("RGB")
    return np.asarray(comp)


def ask_vlm_pick_generic(marked_pil, obj, part_desc, n):
    import base64, io
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    buf = io.BytesIO(); marked_pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    prompt = (
        f"This image of a {obj} has numbered candidate regions (0..{n-1}), each a "
        f"differently-coloured patch with its number, produced by an automatic "
        f"image segmentation model (not hand-drawn). "
        f"Which numbered region corresponds to {part_desc}? "
        f'Respond ONLY JSON: {{"region":<int>,"reason":"<short>"}}. '
        f"If none of the regions matches, set region to -1."
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
        max_tokens=120, temperature=0.0)
    txt = resp.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    d = json.loads(txt)
    return int(d["region"]), d.get("reason", "")


def main():
    rgb = load_rgb_on_white(IMG_PATH)
    print("rgb", rgb.shape)

    from lang_sam import LangSAM
    print("loading LangSAM ...")
    model = LangSAM()

    om = som.object_mask(model, rgb, "coffee mug")
    if om is None:
        sys.exit("no object mask -- cannot proceed")
    print(f"object mask: {int(om.sum())} px ({100.0*om.sum()/om.size:.1f}%)")
    np.save(os.path.join(HERE, "object_mask.npy"), om)

    print("running SAM2 automatic mask generator ...")
    regions = som.auto_regions(model, rgb)
    print(f"{len(regions)} raw SAM regions")
    cand = som.filter_subparts(regions, om)
    print(f"{len(cand)} candidate sub-part regions (on the mug, not the whole mug)")
    if len(cand) == 0:
        sys.exit("SAM found no sub-part candidates on this image")

    marked = som.mark_image(rgb, cand)
    marked.save(os.path.join(HERE, "som_marks.png"))
    print("saved som_marks.png with", len(cand), "candidates")

    report = {"object_mask_px": int(om.sum()), "n_candidates": len(cand)}

    # Print every candidate's own geometry so a wrong VLM pick is visible,
    # not just trusted -- centroid_y small = near the top of the mug.
    for i, m in enumerate(cand):
        ys, xs = np.where(m)
        print(f"  candidate {i}: {int(m.sum())} px, centroid=({xs.mean():.0f},{ys.mean():.0f}), "
              f"bbox y=[{ys.min()},{ys.max()}] x=[{xs.min()},{xs.max()}]")

    picks = {}
    part_prompts = {
        "handle": "the handle -- the curved piece sticking out the side, used for holding "
                  "(NOT the body, rim, or interior opening)",
        "rim": "the interior opening of the cup -- the disc-shaped area bounded by the rim, "
               "where you would drink from or where liquid is poured/leaves (NOT the handle, "
               "NOT the exterior body wall)",
    }
    for part, desc in part_prompts.items():
        region, reason = ask_vlm_pick_generic(marked, "coffee mug", desc, len(cand))
        print(f"[{part}] VLM picked region {region}: {reason}")
        if region is None or region < 0 or region >= len(cand):
            print(f"  >>> no {part} region selected among SAM candidates")
            picks[part] = None
            report[part] = {"picked": None, "reason": reason}
            continue
        m = cand[region]
        ratio = (m & om).sum() / max(om.sum(), 1)
        picks[part] = m
        np.save(os.path.join(HERE, f"{part}_mask.npy"), m)
        report[part] = {"picked_region": region, "reason": reason,
                         "area_px": int(m.sum()), "frac_of_mug": float(ratio)}
        print(f"  -> {part}_mask.npy  {int(m.sum())} px = {ratio:.1%} of mug")

    # body = object minus whatever was actually picked for handle/rim
    # (a set-difference of two real masks -- not a drawn region)
    carve = np.zeros_like(om)
    for m in picks.values():
        if m is not None:
            carve |= m
    body = om & ~carve
    np.save(os.path.join(HERE, "body_mask.npy"), body)
    report["body"] = {"area_px": int(body.sum()), "frac_of_mug": float(body.sum() / max(om.sum(), 1)),
                       "derivation": "object_mask minus handle_mask minus rim_mask"}
    print(f"body_mask.npy (derived): {int(body.sum())} px = {body.sum()/max(om.sum(),1):.1%} of mug")

    with open(os.path.join(HERE, "segmentation_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("wrote segmentation_report.json")


if __name__ == "__main__":
    main()
