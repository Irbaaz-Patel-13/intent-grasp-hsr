# Contradictions and Resolutions

Generated 2026-08-09T16:34:01. Each entry: what was checked, what was found, how it was resolved.

## 1. NEW-A object identity vs. Figure 3

**Checked:** whether NEW-A's mug capture (`captures_pairs_2/cap_mug_head_near.npz`) is the same
physical object as Figure 3's source (`Experiment_Logs/2026-08-07/grasps_out.npz` /
`head_capture_real.npz`).

**Found:** different capture (different MD5, different camera distance/framing). Visual
side-by-side comparison confirms same physical red mug, same table/chair/room -- a different
capture pass of the same scene, not a different object.

**Resolution:** no fix needed. NEW-A and NEW-H were already using the correct object.

## 2. NEW-A gate labels (LOW vs. PASS/REFUSED)

**Checked:** whether `top_protrusion` (147pts/7mm) is mislabeled LOW when it clears the stated
"≥60pts and ≥6mm" gate.

**Found:** `part_adaptive.py:520-524` defines TWO thresholds, not one: NOISE (n<60 or w<6mm) and a
separate, stricter LOW (n<120 or w<10mm). 147pts/7mm clears NOISE but fails LOW on width (7mm <
10mm). `q6_intent_mug.log` independently confirms this component is "below evidence floor".

**Resolution:** LOW label is code-derived and correct. No change made.

## 3. FAILURE_REGISTER total: 17 vs. a possible "13"

**Checked:** whether the dissertation text's failure count (13, per the prompt's framing) conflicts
with the figure's count.

**Found:** `report_assets/FAILURE_REGISTER.csv` has 17 real rows. No "13"-total figure exists
anywhere in this codebase's own generated figures or manifests.

**Resolution:** no contradiction found in the repository's own artefacts to resolve. If the
dissertation text itself says 13, that is a document-level discrepancy outside this repo's data
and should be corrected against the real 17-row register.

## 4. trials.csv: trial 8

**Checked:** whether trial 8 is missing due to a data error or is a genuine gap.

**Found:** `trials.csv` goes trial 7 -> trial 9 with no trial 8 row anywhere in the file (13 lines
total incl. header, covering trials 1-7, 9-12, plus one unlabeled "live demo" row).

**Resolution:** gap is real and preserved as-is in the hardware figure. Not renumbered, not
interpolated.

## 5. trials 9-12 z-rise spread

**Checked:** the "~0.4mm" spread figure appearing in prior draft text.

**Found:** computed directly from `trials.csv`: z_rise_m = 0.1420, 0.1418, 0.1416, 0.1418 ->
min=0.1416, max=0.1420, spread=0.0004m = 0.4mm exactly.

**Resolution:** confirmed by calculation, not typed from memory. Used in the hardware figure.
