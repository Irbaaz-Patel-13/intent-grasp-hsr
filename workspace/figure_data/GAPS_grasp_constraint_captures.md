# Gaps, conflicts and sourcing notes -- grasp_targets.csv / constraint_map.csv / captures_index.csv

All three CSVs were built by direct inspection of files in this repo (via `.venv\Scripts\python.exe`
for `.npz` reads, and plain `csv.reader` for CSV field-count checks). No value in any output row was
invented; every populated cell traces to a specific file/line/key cited in that row's `source` column.

## Task A -- figure_data/grasp_targets.csv

**What "candidate" means here.** `export_grasps_plain.py` (read first, per the task) only produces
`grasps_plain.npz` (25 *grasp poses* -- position/orientation/scores -- computed from `grasps_out.npz`,
in the camera/world frame the CGN pipeline works in, not base frame). That file has no
`reachable_before/after` or `dist_from_base_m` concept. The columns actually requested
(`candidate, reachable_before, reachable_after, dist_from_base_m`, "base frame") match
**`place_run.csv`** instead: 25 *base-placement candidates* (`grasp` id 0-24, `base_x`, `base_y`,
`arm_only_ok`, `manip`, ...) produced by `hsr_base_placement.py`'s collision-aware search, which is
exactly the data `docs/superpowers/plans/2026-08-17-fig-3-7-base-placement.md` (read for context, per
the task) uses for the "Fig 3.7 base placement" figure. So:

- `x, y` = `base_x, base_y` from `place_run.csv` (planar base position in the base/world frame).
- `z` = `0.0` for every row -- not a logged per-candidate value, but the codebase's fixed planar-base
  convention (`hsr_base_placement.py`'s `base_T(bx,by,byaw)` hard-sets `T[:3,3]=[bx,by,0]`; `scene3d.py`
  encodes the same convention as `base_initial=(0.0,0.0,0.0)`). Flagged here rather than silently
  presented as measured.
- `dist_from_base_m` = Euclidean **2D** distance from that candidate's `(base_x,base_y)` to the
  affordance target's `(x,y)` (`aff_center_3d[:2]` from `grasps_plain.npz`). 2D (not 3D) matches how the
  Fig 3.7 plan itself computes `d_origin`/`d_selected` (`target_xy = scene.target[:2]`).
- `reachable_before` = whether the target was reachable from the **initial** base pose
  `(0,0,0)` (`scene3d.py:226`, `REACH_M=0.633` at `scene3d.py:77`). Computed once
  (`d_origin=0.678 m > REACH_M` -> `False`) and applied to all 25 rows, since the initial base pose is
  the same for every candidate -- this is a derived/computed value, not a stored per-row field.
- `reachable_after` = `arm_only_ok AND (dist_from_base_m < REACH_M)` for that row. All 25 rows are
  `True`: `place_run.csv`'s 25 rows are already the *retained* candidates (all passed the arm-only IK
  feasibility test used by the search), consistent with the task's own phrase "25 retained candidates".

**Source chosen: `Experiment_Logs/2026-08-07/place_run.csv` + `Experiment_Logs/2026-08-07/grasps_plain.npz`**,
not `report_bundle_20260801_1611/place_run.csv`, and not the repo-root `grasps_plain.npz`. Reasoning:
the Fig 3.7 plan document independently cites `d_origin=0.678 m`, `d_selected=0.412 m`, and
`manip24=0.17484` as already-verified numbers for candidate 24. Recomputing from
`Experiment_Logs/2026-08-07/place_run.csv` row 24 (`base_x=0.2674, base_y=0.0155, manip=0.17484`)
against `Experiment_Logs/2026-08-07/grasps_plain.npz`'s `aff_center_3d` reproduces `d_origin=0.6781 m`
and `d_selected=0.4122 m` exactly. This is the only one of the three candidate sources whose numbers
match the plan's independently-verified values, so it was treated as the authoritative vintage instead
of applying the root-vs-bundle rule (which does not directly apply here -- see conflict below).

**Root-vs-bundle conflict found, not resolved by the stated rule.** `place_run.csv` does not exist at
the repo root at all, so the "prefer report_bundle_20260801_1611 over root" rule has no root copy to
prefer against. But `report_bundle_20260801_1611/place_run.csv` (2424 bytes, Aug 1 16:11, 25 data rows)
and `Experiment_Logs/2026-08-07/place_run.csv` (2424 bytes, Aug 7 17:18, 25 data rows) have the
**same header, same row count, same byte size, but completely different numeric content** row-for-row
(e.g. candidate 24: bundle has `base_x=0.2819, base_y=-0.0167, manip=0.08`; Experiment_Logs has
`base_x=0.2674, base_y=0.0155, manip=0.17484`). These are two different real base-placement search runs
for what looks like the same target, not a copy/corruption of one file. **Both are listed here, no
winner picked**, beyond the Fig-3.7-plan-corroboration reasoning above that determined which one feeds
`grasp_targets.csv`.

**Conflicting `aff_center_3d` (target position) across grasps_plain.npz copies -- both values listed,
no winner picked:**
- root `grasps_plain.npz`: `aff_center_3d = [0.6957, 0.0544, 0.5000]`
- `Experiment_Logs/2026-08-07/grasps_plain.npz`: `aff_center_3d = [0.6777, -0.0244, 0.4999]`
These differ by ~2 cm in x and ~8 cm in y -- not noise. `report_bundle_20260801_1611` has no
`grasps_plain.npz`/`grasps_out.npz` at all, so it could not be consulted for a tiebreak.

**`place_run_map.png`**: `report_bundle_20260801_1611/place_run_map.png` exists (companion image to
`place_run.csv`) -- noted per the task, not opened/decoded.

**No empty cells** in `grasp_targets.csv`: all 25 rows have every field populated (x, y from
`place_run.csv`; z=0.0 code convention; both reachability flags and dist_from_base_m computed; source
cited per row).

**Malformed-row check**: `Experiment_Logs/2026-08-07/place_run.csv` and
`report_bundle_20260801_1611/place_run.csv` both parsed with `csv.reader` -- 26 rows (1 header + 25
data), 15 fields/row throughout, **zero malformed rows** in either.

## Task B -- figure_data/constraint_map.csv

Derived purely by reading `grasp_policy.py` (204 lines) and `grasp_close_params.py` (160 lines) end to
end and tracing every `if`/`.get(...)`/dict-lookup branch to the closure parameter(s) it feeds and the
arithmetic/geometric formula that consumes that parameter downstream. No prose/report table (e.g. any
"Table 3.2") was consulted, per the task's explicit instruction. 12 rows, one per (field, closure
parameter) branch actually present in the code, including:
- the three `stability_priority`-driven branches (`force_level`, `close_depth_frac`, `cage_clearance_m`),
- the two `post_grasp_motion`-driven branches (`force_level`'s bump term, and the full post-grasp plan:
  `lift_m`/`requires_controlled_tilt`/`retreat`/`note`),
- `thermal_or_hygiene` -> `minimal_contact` (boolean only; confirmed by reading `grasp_policy.py:171`
  that the thermal string itself is never multiplied into any geometric formula in either file),
- `keep_clear`/`keep_clear_reasons` -> pass-through only (confirmed dead beyond the output dict --
  `keep_clear_reasons` is read by `grasp_close_params.py`'s `load_constraints()` but never referenced
  again in either file),
- `align_confident` -> `cage_clearance_m`'s "loose" branch, flagged as **unreachable in this codebase**
  (`closure_policy()` defaults it to `True`; neither call site in `grasp_close_params.py` ever passes
  `align_confident=False`),
- the two perception (non-VLM-constraint) inputs that the closure parameters are actually computed
  against: `part_width_m` (-> `cage_gap_m`/`cage_motor_rad`/`width_gate_ok`, plus the separate
  width-artifact QC guard `MED_TOL=0.30`) and `plane_z`/`obj_top_z` (-> `close_z`/`object_height_m`),
- the discrete `force_level` tier's own numeric lookup table (`effort`, `hold_margin_rad`).

No empty cells; every row has a `source` citing line ranges in `grasp_policy.py` and/or
`grasp_close_params.py`.

## Task C -- figure_data/captures_index.csv

**The originally-suggested directories contain zero qualifying rows.** All of
`captures_pairs_2/`, `captures_pairs/`, `captures_0723/`, `captures/`,
`report_bundle_20260801_1611/captures_pairs/`, and `report_bundle_20260801_1611/captures_obj/` were
searched exhaustively (recursive listing, all `.npz` keys dumped via numpy). Every `cap_*.npz` in these
directories contains only `rgb, depth, K, tf_trans, tf_quat, base_frame, cam_frame, depth_encoding` (or,
for `cap_mug_hv_hand.npz`, just `rgb, source, arm_config`) -- **no `object_mask` or `part_mask` array,
under any name, in any file in any of these six directories.** `captures/regions.npz` (checked because
its name suggested per-region masks) contains only `names/centers_odom/pixels/counts` summary arrays,
not pixel masks. `report_bundle_20260801_1611/captures_obj/capture_log.json` is a step-by-step capture
log (odom, joint states, depth stats) with no mask references. Masks (object/part) are computed live at
figure-build time by the LangSAM/SoM/PCA pipeline (`part_adaptive.py`, `som_part_selection.py`,
`hand_part_grounding.py`) from these raw captures and are not persisted to disk anywhere under these six
directories.

**Where matching rgb + object_mask + part_mask triples actually exist**: the `grasps_out.npz`-style
bundle format (produced by `run_grounding_grasp.py` / `visual_grounding.py`), which embeds
`grounding_rgb` (480x640x3 uint8), `object_mask` (480x640 uint8) and `affordance_mask` (480x640 uint8,
the part-level mask for `target_part`) as three arrays inside **one** `.npz` file. A repo-wide search
(`find . -iname "*grasps_out*.npz"`, excluding `archive/` and `Backups/`) found exactly four such
bundles, all used as rows here (all four `object_mask`/`affordance_mask`/`grounding_rgb` triples agree
in resolution at 640x480 -- **no resolution mismatches found**):

| capture_id | file | object | target_part | instruction |
|---|---|---|---|---|
| root_mug_hotdrink | `grasps_out.npz` | red mug | handle | "I'd like a hot drink" |
| explog0807_mug_hotdrink | `Experiment_Logs/2026-08-07/grasps_out.npz` | red mug | handle | "I'd like a hot drink" |
| batchout_bowl_head_far | `batch_out/bowl_head_far_grasps_out.npz` | bowl | rim | "pick up the bowl head far" |
| run0722_mug_grasp_ok | `run_0722_GRASP_OK/grasps_out.npz` | mug | handle | "Pick up the mug and move it to the other side of the table" |

Since `rgb_path`/`object_mask_path`/`part_mask_path` are all arrays inside one file rather than
separate files on disk, each path is written as `<file>::<npz key>` (e.g.
`grasps_out.npz::grounding_rgb`) and `mask_format=npz-embedded-array`.

**No knife captures qualify -- and none exist to mark `citable=false`.** The repo has extensive knife
*run* artifacts at the root (`close_params_knife_hand.csv`, `close_params_knife_pick.csv`,
`close_params_knife_put.csv`, `constraints_knife_hand.json`, `constraints_knife_pick.json`,
`constraints_knife_put.json`, `head_capture_real_knife.npz`, and ~15 `*_knife*.log` files), but a
repo-wide search for any `*grasps_out*.npz` with `target_object` containing "knife" (checked every
`grasps_out.npz`-style file found anywhere in the repo, including `archive/` and `Backups/`) returned
**zero matches**. `head_capture_real_knife.npz` itself only has the same raw
`rgb/depth/K/tf_trans/tf_quat/...` keys as the other raw captures -- no masks. `captures_pairs_2/`
does have `cap_knife_head_far.npz` / `cap_knife_head_near.npz` raw captures, but (per above) with no
mask pair, so they don't qualify as a row either way. **Conclusion: the known PCA eigenvector-sign bug
in `part_adaptive.py` that reverses knife part labels cannot currently be cited via a persisted
rgb+object_mask+part_mask bundle in this repo** -- the affected run's grounding bundle was apparently
never saved (or was overwritten by a later non-knife run of the same root `grasps_out.npz` file), so
`captures_index.csv` has zero knife rows and the `citable=false` rule has nothing to apply to. This is
flagged explicitly rather than silently omitted.

**Root vs `Experiment_Logs/2026-08-07` `grasps_out.npz` -- two different real captures, not a
duplicate.** `grasps_out.npz` (root, Aug 7 18:12) and `Experiment_Logs/2026-08-07/grasps_out.npz`
(Aug 7 17:00) share the same instruction/object/part but are byte-different, with different
`object_mask` pixel counts (3493 vs 3830) and different `aff_center_3d` (see Task A section above) --
i.e. two separate capture events on the same day, not one file copied. Both are included as separate
`capture_id` rows rather than collapsed. Worth noting as a side observation (not itself one of the three
required tables): the root run's accompanying `constraints.json` (`keep_clear=[]`,
`post_grasp_motion="translate"`, `stability_priority="med"`) is structurally identical to
`grasp_close_params.py`'s own `DEFAULTS` fallback (`grasp_close_params.py:63-65`), while
`Experiment_Logs/2026-08-07/constraints.json` has the fuller, differentiated content
(`keep_clear=["rim"]`, `post_grasp_motion="tilt_pour"`, `stability_priority="high"`) -- suggesting the
18:12 root run may have hit the "no constraints found, using neutral defaults" fallback path rather than
genuinely re-inferring different constraints. Flagged, not resolved, and not used to pick a
`grasp_targets.csv` source (that decision was made on the independently-verified Fig 3.7 numbers, above).

**`close_params.csv` three-way conflict (background context, not directly consumed by any of the three
required CSVs, but checked per the task's general root-vs-bundle instruction since the filename exists
in three places):**
- root `close_params.csv` (2067 B, Aug 7 18:21): `force_level=standard`, `effort=0.3`,
  `hold_margin_rad=0.008`, part widths ~0.081-0.091 m
- `report_bundle_20260801_1611/close_params.csv` (1989 B, Aug 1 16:11): `force_level=firm`,
  `effort=0.5`, `hold_margin_rad=0.016`, part widths ~0.081-0.090 m
- `Experiment_Logs/2026-08-07/close_params.csv` (1980 B, Aug 7 17:18): `force_level=firm`,
  `effort=0.5`, `hold_margin_rad=0.016`, `lift_m=0.12`, `requires_controlled_tilt=1`, part widths
  ~0.079-0.090 m

All three have 25 data rows and pass the field-count/malformed-row check cleanly. The root file's
`force_level=standard` (not `firm`) is consistent with the same "defaults fallback" pattern noted above
for `constraints.json` (root's `constraints.json` has `stability_priority=med`/`post_grasp_motion=translate`,
which `force_level_for()` maps to `standard`, not `firm`) -- i.e. root's 18:21 `close_params.csv` and
18:12 `constraints.json` are internally consistent with each other, just apparently generated from a
defaulted/neutral constraints run rather than the fuller one in `Experiment_Logs`/`report_bundle`. Listed
here for completeness; not resolved to a single winner, and not used by any of the three required CSVs.

**`constraints.json` conflict (also background context):**
- root (298 B, 11 lines): `keep_clear=[]`, `post_grasp_motion="translate"`, `stability_priority="med"`
- `Experiment_Logs/2026-08-07/constraints.json` (398 B, 15 lines): `keep_clear=["rim"]`,
  `post_grasp_motion="tilt_pour"`, `stability_priority="high"`
`report_bundle_20260801_1611` has no `constraints.json`, so no three-way comparison was possible there.

**`gripper_gap_map.csv`**: root (340 B) and `report_bundle_20260801_1611/gripper_gap_map.csv` (340 B)
are identical in size and row count (10 lines); not byte-diffed further since neither is consumed by any
of the three required CSVs.

## Malformed-row summary (all CSVs checked with `csv.reader`, field count vs header)

`Experiment_Logs/2026-08-07/place_run.csv`, `report_bundle_20260801_1611/place_run.csv`,
`close_params.csv` (root), `report_bundle_20260801_1611/close_params.csv`,
`Experiment_Logs/2026-08-07/close_params.csv`, `gripper_gap_map.csv` (root), and
`report_bundle_20260801_1611/gripper_gap_map.csv` were all checked. **Zero malformed rows found in any
of them** -- every data row has exactly as many fields as its header.

The three output CSVs (`grasp_targets.csv`, `constraint_map.csv`, `captures_index.csv`) were themselves
re-parsed with `csv.reader` after being written and confirmed to have zero field-count mismatches
against their own headers (26/13/5 rows, 8/6/11 fields respectively, no malformed lines).

## Empty-field summary

- `grasp_targets.csv`: no empty cells.
- `constraint_map.csv`: no empty cells.
- `captures_index.csv`: no empty cells (all four rows have every column populated; `citable=1` for all
  four since none is a knife capture -- see above).
