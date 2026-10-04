#!/usr/bin/env python
r"""vlm_identify.py -- intent-only object identification across captured scenes.

Tests the part of the claim that naming the object in the instruction hides:
given ONLY a stated intent ("I'd like a hot drink"), does the reasoner infer the
required object type, then pick the right object out of a real cluttered scene --
and does the SAME image yield DIFFERENT objects under different intents?

Runs the real AffordanceReasoner (steps 1-3) on each capture's RGB. No
GroundingDINO, no CGN, no GPU: ~3 API calls and a few seconds per cell, versus
~2 min for the full pipeline. Use batch_scene_analysis.py afterwards for the
geometry/width/roll columns on whichever pairs matter.

    .\.venv\Scripts\python.exe vlm_identify.py                 # intent-only matrix
    .\.venv\Scripts\python.exe vlm_identify.py --mode both     # + named-object control
    .\.venv\Scripts\python.exe vlm_identify.py --only cluster
Outputs: vlm_identify.md, vlm_identify.csv, vlm_identify_raw.json
"""
import argparse, csv, glob, json, os, sys
import numpy as np

# scene -> (objects actually present, [(intent_instruction, expected_object), ...])
# The intent NEVER names the target object; step 1 must infer the object type and
# step 2 must find it in the image. Cluster scenes reuse the SAME image under
# several intents -- that is the discrimination test.
SCENES = {
    "TV_remote": (["remote"], [
        ("I want to change the TV channel", "remote"),
    ]),
    "coke_can": (["can"], [
        ("I'm thirsty and I'd like something fizzy to drink", "can"),
    ]),
    "dishwash_bottle": (["bottle"], [
        ("I need to wash up these dirty dishes", "bottle"),
    ]),
    "metal_spoon": (["spoon"], [
        ("I want to stir sugar into my tea", "spoon"),
    ]),
    "pot_with_handle_and_lid": (["pot"], [
        ("I want to boil some water for pasta", "pot"),
    ]),
    "cluster_mug_cokecan": (["mug", "can"], [
        ("I'd like a hot drink",                              "mug"),
        ("I'm thirsty and I'd like something fizzy to drink", "can"),
    ]),
    "cluster_mug_cokecan_pot": (["mug", "can", "pot"], [
        ("I'd like a hot drink",                              "mug"),
        ("I'm thirsty and I'd like something fizzy to drink", "can"),
        ("I want to boil some water for pasta",               "pot"),
    ]),
    "cluster_mug_remote_pot": (["mug", "remote", "pot"], [
        ("I'd like a hot drink",                "mug"),
        ("I want to change the TV channel",     "remote"),
        ("I want to boil some water for pasta", "pot"),
    ]),
}
# explicit-naming control, for the ablation column
NAMED = {"remote": "pick up the TV remote", "can": "pick up the can of coke",
         "bottle": "pick up the dish soap bottle", "spoon": "pick up the spoon",
         "pot": "pick up the pot", "mug": "pick up the mug"}


def load_rgb(path):
    z = np.load(path, allow_pickle=True)
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 3 and a.shape[2] == 3 and a.shape[0] > 50:
            return (a.astype(np.uint8) if a.dtype != np.uint8 else a)
    return None


def match(pred, expected):
    """Loose containment match, both directions, so 'red mug'/'coffee mug' count."""
    p, e = (pred or "").lower().strip(), expected.lower().strip()
    if not p:
        return False
    if e in p or p in e:
        return True
    syn = {"can": ["coke", "soda", "cola", "drink can", "soft drink"],
           "remote": ["remote control", "tv remote", "controller"],
           "bottle": ["soap", "detergent", "washing-up", "dish"],
           "pot": ["pan", "saucepan", "cooking pot", "cookware"],
           "mug": ["cup", "coffee"], "spoon": ["teaspoon", "spoon"]}
    return any(s in p for s in syn.get(e, []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="captures_0723")
    ap.add_argument("--only", default="")
    ap.add_argument("--mode", choices=["intent", "named", "both"], default="intent")
    a = ap.parse_args()

    sys.path.insert(0, os.getcwd())
    from intent_grasp.config import VLMConfig
    from intent_grasp.affordance_reasoning import AffordanceReasoner
    cfg = VLMConfig()
    if not cfg.api_key:
        cfg.api_key = os.environ.get("OPENAI_API_KEY", "")
    reasoner = AffordanceReasoner(cfg)
    if reasoner.mock_mode:
        sys.exit("ABORT: reasoner is in MOCK mode (no OPENAI_API_KEY) -- results "
                 "would be heuristic fabrications, not measurements.")

    rows, raw = [], []
    for scene, (present, intents) in SCENES.items():
        if a.only and a.only.lower() not in scene.lower():
            continue
        cap = os.path.join(a.dir, "cap_%s.npz" % scene)
        if not os.path.exists(cap):
            print("skip %s (no capture)" % scene); continue
        rgb = load_rgb(cap)
        if rgb is None:
            print("skip %s (no RGB in npz)" % scene); continue

        cases = []
        if a.mode in ("intent", "both"):
            cases += [(i, e, "intent") for i, e in intents]
        if a.mode in ("named", "both"):
            cases += [(NAMED[e], e, "named") for _, e in intents if e in NAMED]

        for instr, expected, kind in cases:
            print("\n%-26s [%s] \"%s\"" % (scene, kind, instr))
            try:
                res = reasoner.reason(instruction=instr, scene_image=rgb,
                                      verbose=False, target_hint=None)
            except Exception as e:
                print("   ERROR:", e)
                rows.append(dict(scene=scene, kind=kind, instruction=instr,
                                 expected=expected, error=str(e)[:80])); continue
            ta, oi, af = res.task_analysis, res.object_identification, res.affordance_reasoning
            c = af.constraints or {}
            ok = match(oi.target_object, expected)
            print("   needs '%s' -> picked '%s' (conf %.2f) %s | part=%s keep_clear=%s"
                  % (ta.required_object_type, oi.target_object, oi.confidence,
                     "OK" if ok else "MISMATCH (expected %s)" % expected,
                     af.target_part, c.get("keep_clear", [])))
            rows.append(dict(scene=scene, kind=kind, instruction=instr,
                             present=";".join(present), expected=expected,
                             required_type=ta.required_object_type,
                             picked=oi.target_object, conf=round(oi.confidence, 2),
                             correct=int(ok), part=af.target_part,
                             keep_clear=";".join(c.get("keep_clear", []) or []) or "-",
                             motion=c.get("post_grasp_motion", ""),
                             stability=c.get("stability_priority", ""),
                             thermal=(c.get("thermal_or_hygiene") or "-"),
                             rationale=af.rationale))
            raw.append(dict(scene=scene, kind=kind, instruction=instr,
                            step1=ta.raw_response, step2=oi.raw_response,
                            step3=af.raw_response))

    if not rows:
        sys.exit("nothing ran")
    with open("vlm_identify.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["scene", "kind", "instruction", "present", "expected", "required_type",
                "picked", "conf", "correct", "part", "keep_clear", "motion",
                "stability", "thermal", "rationale", "error"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); [w.writerow(r) for r in rows]
    json.dump(raw, open("vlm_identify_raw.json", "w", encoding="utf-8"), indent=1)

    done = [r for r in rows if "error" not in r]
    n_i = [r for r in done if r["kind"] == "intent"]
    n_n = [r for r in done if r["kind"] == "named"]
    L = ["# Object identification from intent alone", "",
         "The instruction never names the target object: step 1 infers the required",
         "object type, step 2 must find it in the scene. Cluster rows reuse the SAME",
         "image under different intents — that is the discrimination test.", "",
         "| scene | objects present | instruction | inferred type needed | picked | conf | correct | part | keep_clear |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in done:
        if r["kind"] != "intent":
            continue
        L.append("| %s | %s | %s | %s | **%s** | %.2f | %s | %s | %s |"
                 % (r["scene"], r["present"], r["instruction"], r["required_type"],
                    r["picked"], r["conf"], "✓" if r["correct"] else "✗ (want %s)" % r["expected"],
                    r["part"], r["keep_clear"]))
    if n_i:
        L += ["", "**Intent-only identification: %d/%d correct.**"
              % (sum(r["correct"] for r in n_i), len(n_i))]
    if n_n:
        L += ["", "**Explicit-naming control: %d/%d correct.**"
              % (sum(r["correct"] for r in n_n), len(n_n))]
    # discrimination summary: same image, different intents -> different objects?
    L += ["", "## Discrimination within a single image", ""]
    for scene in sorted(set(r["scene"] for r in n_i)):
        rs = [r for r in n_i if r["scene"] == scene]
        if len(rs) < 2:
            continue
        picks = [r["picked"] for r in rs]
        L.append("- **%s** (%d intents): picked %s — %s"
                 % (scene, len(rs), ", ".join("'%s'" % p for p in picks),
                    "all distinct" if len(set(p.lower() for p in picks)) == len(picks)
                    else "NOT all distinct"))
    L += ["", "## Rationales", ""]
    L += ["- **%s / %s**: %s" % (r["scene"], r["expected"], r["rationale"]) for r in n_i]
    open("vlm_identify.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n" + "\n".join(L[:8 + len(n_i)]))
    print("\nwrote vlm_identify.md / .csv / _raw.json")


if __name__ == "__main__":
    main()
