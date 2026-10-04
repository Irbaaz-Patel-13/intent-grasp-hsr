#!/usr/bin/env python
r"""vlm_stability.py -- repeat the intent-only identification matrix N times and
report per-cell stability.

Motivation: two consecutive runs of the same cell disagreed --
    cluster_mug_cokecan_pot / "I'd like a hot drink"
        pass 1: step1 required type "Cup or Mug" -> picked red mug      (correct)
        pass 2: step1 required type "Container"  -> picked pot with lid (wrong)
The visual step was not at fault: a pot IS a container, and it is the largest one
in view. The error propagated from step 1 abstracting the requirement too far.
config.py sets temperature=0, but the OpenAI backend is not bit-deterministic, so
single-pass numbers are not a measurement. This quantifies it.

    .\.venv\Scripts\python.exe vlm_stability.py --repeat 5
    .\.venv\Scripts\python.exe vlm_stability.py --repeat 5 --only cluster
Outputs: vlm_stability.md, vlm_stability.csv
Cost: ~3 API calls per cell per pass.
"""
import argparse, csv, json, os, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.getcwd())
import vlm_identify as vi          # reuse SCENES, load_rgb, match


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="captures_0723")
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--only", default="")
    a = ap.parse_args()

    from intent_grasp.config import VLMConfig
    from intent_grasp.affordance_reasoning import AffordanceReasoner
    cfg = VLMConfig()
    if not cfg.api_key:
        cfg.api_key = os.environ.get("OPENAI_API_KEY", "")
    reasoner = AffordanceReasoner(cfg)
    if reasoner.mock_mode:
        sys.exit("ABORT: mock mode -- results would be fabrications.")

    cells = []
    for scene, (present, intents) in vi.SCENES.items():
        if a.only and a.only.lower() not in scene.lower():
            continue
        cap = os.path.join(a.dir, "cap_%s.npz" % scene)
        if not os.path.exists(cap):
            continue
        rgb = vi.load_rgb(cap)
        if rgb is None:
            continue
        for instr, expected in intents:
            cells.append((scene, present, instr, expected, rgb))
    if not cells:
        sys.exit("no cells to run")

    print("%d cells x %d passes = %d reasoning runs\n" % (len(cells), a.repeat,
                                                          len(cells) * a.repeat))
    obs = defaultdict(list)
    rows = []
    for p in range(1, a.repeat + 1):
        print("--- pass %d/%d ---" % (p, a.repeat))
        for scene, present, instr, expected, rgb in cells:
            try:
                res = reasoner.reason(instruction=instr, scene_image=rgb,
                                      verbose=False, target_hint=None)
                rt = res.task_analysis.required_object_type
                pick = res.object_identification.target_object
                part = res.affordance_reasoning.target_part
                kc = ";".join(res.affordance_reasoning.constraints.get("keep_clear", []) or []) or "-"
                ok = vi.match(pick, expected)
            except Exception as e:
                print("   ERROR %s: %s" % (scene, e)); continue
            key = (scene, instr, expected)
            obs[key].append(dict(required_type=rt, picked=pick, part=part,
                                 keep_clear=kc, correct=int(ok)))
            rows.append(dict(pass_no=p, scene=scene, instruction=instr,
                             expected=expected, required_type=rt, picked=pick,
                             part=part, keep_clear=kc, correct=int(ok)))
            print("   %-26s %-46s -> %-18s %s" % (scene, instr[:46], pick,
                                                  "OK" if ok else "MISS"))

    with open("vlm_stability.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["pass_no", "scene", "instruction", "expected",
                                          "required_type", "picked", "part",
                                          "keep_clear", "correct"])
        w.writeheader(); [w.writerow(r) for r in rows]

    L = ["# Identification stability over %d passes" % a.repeat, "",
         "`temperature=0` does not make the backend bit-deterministic. Each cell was",
         "run %d times; the columns below show how often the correct object was" % a.repeat,
         "identified and how much step 1's inferred requirement varied.", "",
         "| scene | instruction | correct | picked (distinct) | required type (distinct) | part (distinct) |",
         "|---|---|---|---|---|---|"]
    tot_c = tot_n = 0
    unstable = []
    for (scene, instr, expected), o in obs.items():
        n = len(o); c = sum(x["correct"] for x in o)
        tot_c += c; tot_n += n
        picks = Counter(x["picked"] for x in o)
        types = Counter(x["required_type"] for x in o)
        parts = Counter(x["part"] for x in o)
        if c < n:
            unstable.append((scene, instr, expected, picks, types))
        L.append("| %s | %s | **%d/%d** | %s | %s | %s |"
                 % (scene, instr[:44], c, n,
                    ", ".join("%s×%d" % (k, v) for k, v in picks.most_common()),
                    ", ".join("%s×%d" % (k, v) for k, v in types.most_common()),
                    ", ".join("%s×%d" % (k, v) for k, v in parts.most_common())))
    L += ["", "**Overall: %d/%d correct (%.0f%%) across %d cells x %d passes.**"
          % (tot_c, tot_n, 100.0*tot_c/max(tot_n, 1), len(obs), a.repeat)]

    if unstable:
        L += ["", "## Cells that were not stable", "",
              "For each, note whether the wrong pick coincides with a *more generic*",
              "`required_object_type` from step 1 -- that is the propagation path:",
              "an under-specified requirement leaves step 2 without enough constraint",
              "to discriminate, and it selects another object that also satisfies it.", ""]
        for scene, instr, expected, picks, types in unstable:
            L.append("- **%s** — \"%s\" (want *%s*)" % (scene, instr, expected))
            L.append("  - picked: %s" % ", ".join("%s×%d" % (k, v) for k, v in picks.most_common()))
            L.append("  - step-1 requirement: %s" % ", ".join("'%s'×%d" % (k, v) for k, v in types.most_common()))
    else:
        L += ["", "All cells were stable across every pass."]

    open("vlm_stability.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n" + "\n".join(L))
    print("\nwrote vlm_stability.md / .csv")


if __name__ == "__main__":
    main()
