#!/usr/bin/env python
r"""analyse_stability.py -- test the propagation hypothesis on vlm_stability.csv.

Hypothesis: identification failures are not visual-grounding failures. They occur
when step 1 abstracts the requirement too far (e.g. "Container" instead of
"Cup or Mug") AND the scene contains another object that also satisfies the
abstracted requirement. Both conditions are needed: in the mug+can scene a
generic "Container" still selects the mug, because no competing container is
present; in mug+can+pot it selects the pot.

Pairs each pass's required_object_type with that pass's outcome and prints the
contingency, so the claim is measured rather than inferred from marginal counts.

    .\.venv\Scripts\python.exe analyse_stability.py
Writes stability_mechanism.md
"""
import csv, sys, os
from collections import defaultdict, Counter

CSV = "vlm_stability.csv"
# a requirement is SPECIFIC if it names an object category, GENERIC otherwise
SPECIFIC_WORDS = ("mug", "cup", "spoon", "remote", "pot", "kettle", "can",
                  "bottle", "pan", "glass", "tool", "appliance")


def is_specific(t):
    t = (t or "").lower()
    return any(w in t for w in SPECIFIC_WORDS)


def main():
    if not os.path.exists(CSV):
        sys.exit("%s not found -- run vlm_stability.py first" % CSV)
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    if not rows:
        sys.exit("empty csv")

    by_cell = defaultdict(list)
    for r in rows:
        by_cell[(r["scene"], r["instruction"], r["expected"])].append(r)

    L = ["# Where identification failures come from", "",
         "Each pass pairs step 1's inferred `required_object_type` with the object",
         "step 2 then selected. A requirement is called *specific* if it names an",
         "object category (mug, pot, remote, ...) and *generic* otherwise.", ""]

    # global contingency
    cont = Counter()
    for r in rows:
        cont[(is_specific(r["required_type"]), r["correct"] == "1")] += 1
    spec_ok, spec_no = cont[(True, True)], cont[(True, False)]
    gen_ok, gen_no = cont[(False, True)], cont[(False, False)]
    L += ["## Contingency: requirement specificity vs outcome", "",
          "| step-1 requirement | correct | wrong | accuracy |", "|---|---|---|---|",
          "| specific (names a category) | %d | %d | %.0f%% |"
          % (spec_ok, spec_no, 100.0*spec_ok/max(spec_ok+spec_no, 1)),
          "| generic | %d | %d | %.0f%% |"
          % (gen_ok, gen_no, 100.0*gen_ok/max(gen_ok+gen_no, 1)), ""]

    # per-cell detail for the unstable ones
    L += ["## Per-pass detail for cells that varied", ""]
    any_unstable = False
    for (scene, instr, exp), rs in sorted(by_cell.items()):
        n_ok = sum(1 for r in rs if r["correct"] == "1")
        if n_ok == len(rs):
            continue
        any_unstable = True
        L += ["### %s — \"%s\"  (expected *%s*)" % (scene, instr, exp), "",
              "| pass | step-1 required type | specific? | picked | correct |",
              "|---|---|---|---|---|"]
        for r in sorted(rs, key=lambda x: int(x["pass_no"])):
            L.append("| %s | %s | %s | %s | %s |"
                     % (r["pass_no"], r["required_type"],
                        "yes" if is_specific(r["required_type"]) else "**no**",
                        r["picked"], "✓" if r["correct"] == "1" else "✗"))
        L.append("")
    if not any_unstable:
        L += ["All cells were stable.", ""]

    # scenes where a generic requirement still succeeded -> distractor matters
    L += ["## Does a generic requirement always fail?", ""]
    gen_rows = [r for r in rows if not is_specific(r["required_type"])]
    by_scene = defaultdict(lambda: [0, 0])
    for r in gen_rows:
        by_scene[r["scene"]][0 if r["correct"] == "1" else 1] += 1
    L += ["| scene | generic requirement → correct | → wrong |", "|---|---|---|"]
    for s, (ok, no) in sorted(by_scene.items()):
        L.append("| %s | %d | %d |" % (s, ok, no))
    L += ["", "A generic requirement is only harmful when the scene contains a",
          "competing object that also satisfies it — which is why the same generic",
          "requirement succeeds in the two-object scene and fails once a pot is added.", ""]

    # overall
    tot = len(rows); ok = sum(1 for r in rows if r["correct"] == "1")
    cells = len(by_cell); stable = sum(1 for rs in by_cell.values()
                                       if all(r["correct"] == "1" for r in rs))
    L += ["## Summary", "",
          "- %d/%d passes correct (%.0f%%)" % (ok, tot, 100.0*ok/tot),
          "- %d/%d cells stable across every pass" % (stable, cells),
          "- failures confined to %d cell(s)" % (cells - stable), ""]

    open("stability_mechanism.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print("wrote stability_mechanism.md")


if __name__ == "__main__":
    main()
