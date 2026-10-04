# GAPS.md — sourcing decisions, empty fields, conflicts, malformed CSVs

Synthesized from six independent investigations of this repository (one for `INVENTORY.md`, four
covering the 15 `figure_data/*.csv` outputs in disjoint groups, one for `FIGURE_AUDIT.md`). Full
per-group detail lives in the four `GAPS_*.md` files in this directory — this file consolidates
the cross-cutting picture, especially the contradictions, which is the part that matters most.
No number in any output CSV was invented; every empty cell below is a genuine "not found."

---

## 1. Source file chosen per output, and why

| Output | Chosen source | Why |
|---|---|---|
| `trials_clean.csv` | `report_bundle_20260801_1611/trials.csv` (11 rows) + explicit trial-8 gap row | Only candidate whose row set is exactly 1-7,9-12 with no extra rows to explain away; bundle preferred per ground rule |
| `components.csv` | `report_assets/SENSOR_ENVELOPE.md` §V2, cross-matched to logs for `points` | Only place assembling the 5-component/4-recoverable/mug-refused set with measured mm+px |
| `fragments.csv` | `figures/scripts/fig_5_5_mug_fragmentation.py` + `q6_intent_mug.log` + `part_adaptive.py:538-542` | Script's own `EXPECTED` dict, corroborated by raw log and gate-threshold source |
| `clutter.csv` | `batch_scene_analysis.csv` | The exact file `fig_5_4_isolated_vs_cluttered.py` asserts against at build time |
| `coverage.csv` | Six root `run_*.log` files (`run_knife_pick2/hand/put.log`, `run_remote_hand/power/put.log`) | Primal source; `new_c_langsam_coverage.py`'s table is itself a transcription of these |
| `reasoning_grid.csv` | `vlm_grid_raw.json` `step3` blocks | Only file covering all 6 objects × 3 instruction types with the required schema |
| `handover_ablation.csv` | `vlm_grid_raw.json` (baseline) + `vlm_grid_handover_v2_raw.json` (receiver_aware) | v2 script's own hard-coded `V1` dict confirms `vlm_grid_raw.json` is its baseline dataset |
| `part_selection_methods.csv` | `report_assets/PART_NAMING_ABLATION.csv` (all 29 rows) | Already structured as A/B/C; mapped to `bind_part`/SoM/point methods via source code |
| `servo_trace.csv` | `fig10_visual_servo.py` constants + `trials.csv` note corroboration | No per-iteration log exists anywhere (independently confirmed absent by 2 prior in-repo audits + this pass) |
| `energy_inventory.csv` | — (header only) | No measured/estimated energy value exists anywhere; `figures/SOURCE_MANIFEST.md:198` itself marks this `TODO` |
| `grasp_targets.csv` | `Experiment_Logs/2026-08-07/place_run.csv` + `.../grasps_plain.npz` | Only candidate whose recomputed `d_origin`/`d_selected`/`manip24` match the independently-verified Fig 3.7 plan values |
| `corrections.csv` | Reconstructed from 5 separate audit docs (root `corrections.csv` is an empty template) | `figures/BLOCKERS.md`/`PIPELINE_CHANGES.md` confirm a real, numbered 5-item corrections set exists |
| `constraint_map.csv` | `grasp_policy.py` + `grasp_close_params.py` (direct code trace) | Per instruction: derived from code, not from any prose table |
| `captures_index.csv` | Four `grasps_out.npz`-style bundles (root, `Experiment_Logs`, `batch_out`, `run_0722_GRASP_OK`) | Only place rgb+object_mask+part_mask actually co-exist; the six suggested capture dirs hold zero masks (computed live, never persisted) |

`INVENTORY.md` and `FIGURE_AUDIT.md` are exhaustive walks, not single-source picks — see those
files directly.

---

## 2. Every field left empty (by output)

- **`trials_clean.csv`**: `mode` empty for trials 1-4 (only "autonomous" is attested, never "fully
  autonomous" or "hand-placed" — the schema's enum has no plain "autonomous" value); `z_rise_m`/`held`
  empty for trials 1 and 3 (`ABORT_` verdict, grasp never reached the measurement point — blank in
  the source itself); trial 8 fully empty except `note=no record`.
- **`coverage.csv`**: `object_mask_px` empty on all 6 rows — never printed in any log, and
  back-solving it from the rounded coverage % was rejected as manufacturing false precision.
- **`part_selection_methods.csv`**: `centroid_xyz` empty on all 29 rows (no 3D centroid printed
  anywhere for any method/run); `points` empty on 7 rows (`POINT_OFF_OBJECT`/`SPLIT` outcomes —
  structurally not applicable, not a missing measurement).
- **`fragments.csv`**: row 3 (`combined`) `width_mm` empty — no single measured width exists for a
  two-fragment union.
- **`servo_trace.csv`**: `converged`/`jacobian_update` empty on all 3 rows — inferring convergence
  from the absence of an `ABORT` verdict was considered and rejected as a categorical guess.
- **`energy_inventory.csv`**: every cell empty except the header — no data exists.
- **`corrections.csv`**: `section` empty on all 5 rows — no source document assigns any correction
  to a dissertation section number.
- **`reasoning_grid.csv`**: knife/relocate's `thermal_flag` holds the literal source-data anomaly
  string `"null"` (quoted text, not empty) — preserved verbatim, not normalized, per the
  pull-JSON-verbatim rule.
- `components.csv`, `clutter.csv`, `grasp_targets.csv`, `constraint_map.csv`, `captures_index.csv`,
  `handover_ablation.csv`: no empty required fields.

---

## 3. Conflicting file vintages (row counts / sizes)

| Filename | Locations found | Row counts / sizes | Resolution |
|---|---|---|---|
| `trials.csv` | root, `report_bundle_20260801_1611/`, `trials_0728.csv`, `Backups/2026-08-07/…`, `Backups/…/run_0723_trials/` | 12 / 11 / 7 / 12 / 4 | Bundle (11) used; root's 12th row ("live demo," 2026-08-03) is real but out of the 1-7,9-12 scope — excluded, not renumbered |
| `place_run.csv` | `report_bundle_20260801_1611/`, `Experiment_Logs/2026-08-07/` | both 25 rows, both 2424 bytes, **same header, different numeric content row-for-row** | Experiment_Logs version used (matches independently-verified Fig 3.7 plan numbers); both listed, no winner declared by the size/header match alone |
| `close_params.csv` | root, `report_bundle_20260801_1611/`, `Experiment_Logs/2026-08-07/` | all 25 rows | See §4 conflict #1 below — not resolved |
| `constraints.json` | root, `Experiment_Logs/2026-08-07/` | 298B/11 lines vs 398B/15 lines | See §4 conflict #2 — not resolved |
| `grasps_plain.npz` / `grasps_out.npz` | root, `Experiment_Logs/2026-08-07/`, `batch_out/`, `run_0722_GRASP_OK/` | 4 distinct bundles, all used as separate `captures_index.csv` rows | Not collapsed — genuinely different capture events |
| `gripper_gap_map.csv` | root, bundle | identical (340B, 10 lines) | No conflict |
| `components.csv` (repo-root stub) | root only | 2 populated data rows + 5 header-repeat template rows across the two conflated files people call "components.csv" and "corrections.csv" at root | Neither used as primary source — too incomplete/empty; superseded by `figure_data/components.csv` and `figure_data/corrections.csv` |
| `part_decomposition_table.md` | `archive/backups/results_home_0713/`, `experiments/part_grasp/` | byte-identical | Confirmed duplicate, not divergent — not used as a source (numbers don't match required components/fragments) |

Full per-directory conflict listing (49 duplicate basenames total, all cross-checked) is in
`INVENTORY.md` §3.

---

## 4. Malformed CSVs (file + line numbers)

All found via `csv.reader` field-count-vs-header checks; naive `split(",")` was never used:

1. **`report_assets/PART_NAMING_ABLATION.csv`** (13-column header) — lines **2, 15, 18** have 14
   fields (unquoted commas inside free-text `correct`/`raw_points` fields, e.g. `[[800,600]]`
   un-quoted); line **27** has 12 fields (a dropped `nearest_distance_px` column, not a merge).
   Values used in `part_selection_methods.csv` were reconstructed by hand from the legible raw row
   text, not by a naive parse that would have shifted later columns.
2. **`components.csv`** (repo-root stub, 5-column header) — line 4 is a comment
   (`# fill in the remaining measured components...`), 2 fields against 5. Not data corruption,
   just an unfilled template line; excluded from use.
3. **`report_assets/FAILURE_REGISTER.csv`** — 22 mismatched lines (2, 5, 6, 7, 9-23) per the
   INVENTORY.md agent's independent parse. Not consumed by any of the 15 required outputs, flagged
   for completeness.
4. **`report_assets/FIGURE_MANIFEST.csv`** — 6 mismatched lines (2, 3, 4, 5, 6, 8), same status as
   above (used only as corroborating context for the knife-handle 31mm/337pts figure, not as a
   primary parsed source).

No malformed rows were found in any of the fifteen `figure_data/*.csv` outputs themselves — each
was re-parsed with `csv.reader` after writing and confirmed field-count-clean.

---

## 5. Quantities found with two different conflicting values (both listed, no winner picked)

1. **`close_params.csv`, root vs. bundle vs. Experiment_Logs — three-way conflict, not fully
   reconciled between the two investigating agents' own characterizations:**
   - Trials/corrections agent: root (mtime 2026-08-03) has `part_width_m=0.0871`,
     `cage_motor_rad=0.832`, **`ok=1` (success) for all 25 rows**; bundle (mtime 2026-08-01) has
     `part_width_m=0.087`, `cage_motor_rad=0.83`, **`ok=0` (fail) for all 25 rows**.
   - Grasp/captures agent: root has `force_level=standard`, `effort=0.3`, `hold_margin_rad=0.008`;
     bundle **and** `Experiment_Logs/2026-08-07` both have `force_level=firm`, `effort=0.5`,
     `hold_margin_rad=0.016` (Experiment_Logs additionally has `lift_m=0.12`,
     `requires_controlled_tilt=1`).
   Both reports are reproduced here verbatim rather than merged into one number, since they were
   produced by independent passes reading different columns of the same three files and neither
   was asked to reconcile with the other. A reader needing this file's `ok`/`force_level` value
   should re-open all three copies directly rather than trust either summary alone.
2. **`trials.csv` row-count / identity claim.** `figures/SOURCE_MANIFEST.md` states root and bundle
   `trials.csv` are "byte-identical." Direct `diff` this session shows they are not (root has one
   extra row). Both claims reported; the manifest claim may simply predate root's 2026-08-03 append.
3. **`place_run.csv`, bundle vs. Experiment_Logs** — identical header/row-count/byte-size, entirely
   different numeric content (e.g. candidate 24: bundle `base_x=0.2819,base_y=-0.0167,manip=0.08`
   vs. Experiment_Logs `base_x=0.2674,base_y=0.0155,manip=0.17484`). Two real, different
   base-placement search runs, not a corrupted copy.
4. **`grasps_plain.npz` `aff_center_3d`, root vs. Experiment_Logs** — `[0.6957, 0.0544, 0.5000]`
   vs. `[0.6777, -0.0244, 0.4999]` — ~2cm x / ~8cm y difference, not noise.
5. **`constraints.json`, root vs. Experiment_Logs/2026-08-07** — root: `keep_clear=[]`,
   `post_grasp_motion="translate"`, `stability_priority="med"`; Experiment_Logs: `keep_clear=["rim"]`,
   `post_grasp_motion="tilt_pour"`, `stability_priority="high"`. Root's values match
   `grasp_close_params.py`'s own neutral-default fallback shape exactly, suggesting that run hit the
   "no constraints found" path rather than a genuine re-inference.
6. **Knife "handle" component width/points — three different values across three sessions, all
   real, none wrong:**
   - `run_knife_pick2.log:68` (live pipeline run): **36mm / 945 pts**
   - `report_assets/FIGURE_MANIFEST.csv` (isolation path for `fig_stage4_knife_same_part_three_tasks.png`): **31mm / 337 pts**
   - `report_assets/PART_NAMING_ABLATION.csv:2` (method A_heuristic, used in `components.csv`): **24mm / 216 pts**
7. **Mug/handover thermal flag** — `vlm_grid_raw.json`: `thermal_or_hygiene=null` (empty);
   `mug_condA_parts.json`: `thermal_or_hygiene="hot liquid"`. Same object, same effective
   instruction, different files disagree.
8. **Mug/pour `stability_priority`** — `vlm_grid_raw.json`: `med`; `mug_condA_parts.json`: `high`
   (instruction phrasing differs slightly between the two, may be two separate reasoning calls
   rather than a strict re-run — not resolved either way).
9. **LangSAM mask-collapse percentage** — a task prompt quoted inside
   `report_assets/PERCEPTION_EVIDENCE.md` cites "90/94/98%"; actual logged values found this session
   are knife 97%×3, remote 88%/86%/86%. Not used in any output CSV; flagged as a live discrepancy
   already on record in one of this task's own primary sources.
10. **FAILURE_REGISTER total** — register itself has 17 real rows; no in-repo source for a "13"
    figure was found (this is corrections.csv item 4).
11. **Old-schema mug part binding** — `archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/reasoning_result.json`:
    `optimal_part="body"`; `vlm_grid_raw.json`'s current-schema mug rows: `target_part="handle"`
    (all three instruction types). Different vintage/pipeline, not reconciled.

---

## 6. Knife-related rows marked `citable=false`

Per the standing PCA-eigenvector-sign bug in `part_adaptive.py` (reverses knife
`segment_near`/`segment_far`/`lateral_protrusion_N` handle/blade semantics — geometry itself is not
in question, only which end is labeled which):

- `components.csv` row 1 (knife handle, 24mm/216pts) — explicit `citable=false` cell.
- `part_selection_methods.csv` — all 12 knife rows, flagged in `notes` (schema has no dedicated
  `citable` column for this file).
- `coverage.csv` — 3 knife rows (`knife_pick2`/`knife_hand`/`knife_put`).
- `reasoning_grid.csv` — 3 knife rows (relocate/use/handover).
- `handover_ablation.csv` — 1 knife receiver_aware row (`target_part="blade spine"`).
- `captures_index.csv` — **zero knife rows exist to flag**: no persisted knife
  rgb+object_mask+part_mask bundle survives anywhere in the repo (the affected run's grounding
  bundle was apparently never saved, or was overwritten). Flagged explicitly rather than silently
  omitted.
- `fragments.csv`, `clutter.csv`, `grasp_targets.csv`, `constraint_map.csv`,
  `trials_clean.csv`, `corrections.csv`, `servo_trace.csv`, `energy_inventory.csv` — no knife rows,
  not applicable.

Caveat noted independently by two agents: for `coverage.csv`/`reasoning_grid.csv`/
`handover_ablation.csv`, the "handle"/"blade" label comes from VLM text reasoning
(`affordance_reasoning.py`), not `part_adaptive.py`'s geometric PCA classifier — so the specific
reversal mechanism doesn't literally apply to those three files. They were flagged anyway per the
blanket instruction rather than making a case-by-case exception.

---

## 7. Figure audit highlights (full detail in `FIGURE_AUDIT.md`)

198 images audited: **158 KEEP / 22 REGENERATE / 18 DO NOT USE**.

- Knife part-label figures confirmed genuinely wrong by opening them (not just filename-matched):
  `fig_stage4_knife_same_part_three_tasks.png`, `fig_stage5_partmask_knife_*` (2 files) — DO NOT USE.
- **New finding, not in the original known-problems list**: the 6 `battery_*_align.png` task files
  plus `fig_align_handle.png` are byte-for-byte identical (MD5-confirmed) — never regenerated per
  task, so presenting them as 6 distinct results is misleading. DO NOT USE.
- `figdeck_naming_ablation.png` confirmed genuinely blank (uniform canvas).
- **Correction to the task brief's assumption**: `fig_part_mask.png`/`fig_part_mask_isolated.png`
  are actually fine — they show real part masks, are not byte/dimension-identical to
  `fig_wrist_roll_alignment.png`, and were incorrectly reported as mislabelled.
- `fig_compact.png` is a duplicate of `fig_align_mug_handle.png` whose own caption says "shape
  class 'elongated'" — filename contradicts content.
- `generated_assets/storyboard/storyboard.png` (960×540, 13 dense text cells) illegible at native
  resolution.

---

## 8. Where to look for more detail

- `figure_data/INVENTORY.md` — full file-by-file walk (1603 data files, 196 in-scope images, 49
  duplicate-basename conflicts).
- `figure_data/FIGURE_AUDIT.md` — full per-image verdict table.
- `figure_data/GAPS_trials_servo_energy_corrections.md`
- `figure_data/GAPS_components_fragments_clutter_methods.md`
- `figure_data/GAPS_coverage_reasoning_handover.md`
- `figure_data/GAPS_grasp_constraint_captures.md`
