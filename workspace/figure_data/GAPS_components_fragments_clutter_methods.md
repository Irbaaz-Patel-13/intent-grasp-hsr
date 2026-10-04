# Gaps, conflicts, and provenance notes — components / fragments / clutter / part_selection_methods

Covers the four CSVs written this pass: `figure_data/components.csv`, `figure_data/fragments.csv`,
`figure_data/clutter.csv`, `figure_data/part_selection_methods.csv`. No existing repo file was
modified or deleted.

## 1. Source file chosen for each output, and why

### components.csv (Task A)
Primary source: **`report_assets/SENSOR_ENVELOPE.md`, section V2** ("measured component width,
mm and px, at its own capture depth"). This is the only place in the repo that already assembles
exactly the "5 measured components / 4 recoverable / mug handle refused" set the task described,
with both `width_mm` and `pixels` computed from the sensor's own FOV/resolution spec at each
component's logged capture depth. It does not carry `points`, so each row's `points` value was
cross-matched against a second, independent source with the *same width_mm* to confirm it's the
same measurement:
- knife handle (24 mm) -> `report_assets/PART_NAMING_ABLATION.csv:2` (A_heuristic, lateral_protrusion, 216 pts) — same width, high-confidence match.
- remote lateral_protrusion (18 mm) -> `report_assets/PART_NAMING_ABLATION.csv:29` (B_som, 284 pts) — same width, high-confidence match.
- spoon (20 mm) -> `ax4_spoon.log:7` / `bc_spoon.log:7` (164 pts) — same width, high-confidence match, and this is the log SENSOR_ENVELOPE.md's own number was almost certainly drawn from.
- pot lid knob (16 mm) -> **only** found in `codex/05_figures.md:69`, a figure-*viewing* note (469 pts), not a raw pipeline log. Weaker provenance — see gap #2 below.
- mug handle (4 mm) -> `q6_intent_mug.log:5` (53 pts, NOISE).

The root-level `components.csv` (168 bytes) was read but **not used as the source** — it is an
explicit stub ("# fill in the remaining measured components, then re-run") with only 2 of 5 rows,
no `object`, `pixels` (for mug), or `citable` columns, and its one width_mm value present (knife,
blank) doesn't even fill the column the task needs. Its two present numbers (mug 4mm/2.5px,
knife 15.2px) are consistent with SENSOR_ENVELOPE.md's 4mm/2.50px and 15.18px (rounding only,
not a conflict), so nothing in the stub contradicts what was written — it was simply too
incomplete to serve as the primary source.

### fragments.csv (Task B)
Primary source: **`figures/scripts/fig_5_5_mug_fragmentation.py`** (its `EXPECTED` dict and
docstring), corroborated by **`q6_intent_mug.log:5`** for the `lateral_protrusion` fragment and
by `part_adaptive.py:538-542` for the gate thresholds (`NOISE` if `n<60` OR `width<6mm`). The
script's own docstring states its numbers were cross-verified this project against
`bc_mug.log`/`ax4_mug.log`/`q6_intent_mug.log` — but only `q6_intent_mug.log` (present at root)
actually names `lateral_protrusion`; none of the three root logs individually name
`lateral_protrusion_1` by its 36pt/3mm figure, so that fragment's number is sourced to the figure
script, not an independently located raw log line (see gap #1 below).

### clutter.csv (Task C)
Primary source: **`batch_scene_analysis.csv`**, which is exactly the file
`figures/scripts/fig_5_4_isolated_vs_cluttered.py` reads and asserts against (its `_verify()`
function literally asserts `minor_mm==147`/`over_aperture=='1'` for the isolated pot row and
`minor_mm==46`/`over_aperture=='0'` for the cluttered row) — the strongest corroboration found
for any of the four tasks, since the figure script would raise `AssertionError` at build time if
the CSV values drifted. `capture_id` values were taken from `CAPTURES_DIR = captures_0723` in the
same script, and confirmed to exist on disk (`captures_0723/cap_pot_with_handle_and_lid.npz`,
`captures_0723/cap_cluster_mug_cokecan_pot.npz`, `captures_0723/cap_TV_remote.npz`,
`captures_0723/cap_cluster_mug_remote_pot.npz`). The TV-remote isolated/cluttered pair (13mm ->
73mm) was added beyond the pot because `fig_5_4_isolated_vs_cluttered.py`'s own caption cites it
by name as the counter-example to the pot's direction of change — it's part of the same 5-scene
batch and the same comparison mechanism, not a separately cherry-picked object.
`batch_pot_with_handle_and_lid.json` and `batch_cluster_mug_remote_pot.json` were read and are
consistent with (not contradicting) `batch_scene_analysis.csv` — see conflict-check note in
section 5.

### part_selection_methods.csv (Task D)
Primary source: **`report_assets/PART_NAMING_ABLATION.csv`** in full (all 29 data rows), which is
already structured almost exactly as an A/B/C method comparison — confirmed against
`som_part_selection.py:822-824` (`--mode {som,point}`, whose own help text calls `som` the
"numbered-region selector" and `point` the "point-based affordance selector") and
`part_adaptive.py:568-575` (`bind_part` docstring: "Bind an open-vocabulary VLM part name to a
structural component"). Method mapping used: `A_heuristic` = method A = `part_adaptive.bind_part`;
`B_som` = method B = `som_part_selection.py --mode som`; `C_pointing`/`C_pointing_rep2`/
`C_pointing_rep3` = method C = `som_part_selection.py --mode point`. `vlm_identify.py`/`.csv` was
read and **rejected** as a candidate method C — it identifies which *object* to act on from
unnamed intent across a scene (a different experiment entirely, see its own docstring), not which
*part* of an already-identified object to grasp, and it has no A/B/C structure.

## 2. Empty required fields

- **`part_selection_methods.csv`, `centroid_xyz` — empty on all 29 rows.** No 3D centroid
  coordinate for any component chosen under any of the three methods was found anywhere in
  `report_assets/PART_NAMING_ABLATION.csv`, `condA_results.json`, `mug_condA_parts.json`, or the
  grepped run logs (`run_knife_pick2.log`, `run_remote_hand.log`, etc. print `bound 'X' -> Y (...)`
  lines with width/points/evidence/score but never a centroid). `part_adaptive.describe_components()`
  does compute and return a `centroid` field internally (`part_adaptive.py:544`), but none of the
  logs or CSVs inspected print it. Left blank rather than approximated from any other figure's
  centroid, since no confirmed link between those figures' captures and this ablation run's own
  component instances was found.
- **`part_selection_methods.csv`, `points` — empty on 7 rows** (knife pick/hand(+2 reps)/put under
  method C, mug "hand me the mug" under method C, remote "turn the television on" under method C).
  All 7 are `POINT_OFF_OBJECT` or `SPLIT` outcomes where no single component was resolved, so no
  point count applies — not a missing measurement, a structural non-applicability, explained in
  each row's `notes`.
- **`fragments.csv`, row 3 (`combined`), `width_mm` — empty.** Width is a per-fragment geometric
  property (each fragment's own minimum closing extent); there is no single measured width for
  "53+36 points combined" anywhere in the source, and 4mm+3mm is not a valid sum. Left blank
  rather than guessed; the row exists only to show the point-count gate passing combined while
  the width gate does not, per `figures/scripts/fig_5_5_mug_fragmentation.py:9-11`.
- **`clutter.csv` — no empty fields**; all 4 rows fully populated from `batch_scene_analysis.csv`.
- **`components.csv` — no empty fields**; all 5 rows fully populated (mug handle's `recovered`
  correctly reads `false`).

## 3. Malformed source CSVs found (file + line numbers)

Checked every CSV cited as a source, with Python `csv.reader`, comparing per-row field count
against the header:

- **`report_assets/PART_NAMING_ABLATION.csv`** (header: 13 columns) — **4 malformed rows**:
  - **Line 2** (knife/pick/A_heuristic): 14 fields. The `correct` field contains an unquoted
    comma ("...this object/isolation, so no prior verified side-mapping exists...") that was
    never wrapped in quotes, splitting one field into two.
  - **Line 15** (mug/pour/C_pointing): 14 fields. The `raw_points` field `[[800,600]]` contains an
    unquoted comma inside the brackets, same failure mode as line 2.
  - **Line 18** (mug/move/C_pointing): 14 fields. Same failure mode, `raw_points` = `[[750,600]]`.
  - **Line 27** (remote/put/C_pointing): 12 fields (one *short*, not long). The
    `nearest_distance_px` field is missing entirely (no empty placeholder, no comma for it) —
    this is a dropped column, not a merge. Reconstructed from the surrounding row's own text
    ("identical to C's own hand-me row") for both `pixel_pos` and `correct`.
  All four rows' values used in `part_selection_methods.csv` were reconstructed by hand from the
  raw row text (which was fully legible) rather than by a naive `split(",")`/`csv.reader` pass,
  which would have silently misaligned the remaining columns on these 4 rows. Each affected output
  row's `notes` field carries a "MALFORMED SOURCE ROW" flag.
- **`components.csv`** (root, 168-byte stub; header: 5 columns) — **line 4** is a comment
  (`# fill in the remaining measured components, then re-run`), 2 fields against a 5-column
  header. Not a data-alignment bug (it's clearly a comment, not misparsed data), but flagged per
  the task's parsing instructions; excluded from use as noted in section 1.
- **`batch_scene_analysis.csv`** (header: 27 columns) — no malformed rows; all 5 data rows parse
  cleanly.
- **`vlm_identify.csv`** (header: 16 columns) — no malformed rows; all 11 data rows parse cleanly
  (checked as part of ruling this file out for Task D).

## 4. Knife rows marked `citable=false`, and why

Per the task's ground rule (unanchored PCA eigenvector sign bug in `part_adaptive.py`, documented
at length in `report_assets/PERCEPTION_EVIDENCE.md`'s "`segment_near`/`segment_far` handle/blade
labels are reversed" and "`lateral_protrusion`/`lateral_protrusion_N` ordering is also unanchored"
rows), **every row describing a knife part-level measurement was marked not citable**:

- `components.csv` row 1 (`handle`, knife, 24mm/15.18px/216pts) — has an explicit `citable=false`
  cell, with the reason spelled out in its `note` column.
- `part_selection_methods.csv` — **all 12 knife rows** (3 instructions x method A, x method B, x
  method C/C_rep2/C_rep3 = 3+3+6) carry a `citable=false` warning appended to their `notes` field
  (the schema for this CSV has no dedicated `citable` column, so it is embedded in `notes` per row
  instead of omitted). This includes rows where the *method itself failed*
  (`POINT_OFF_OBJECT`) — the failure outcome is still reported as measured fact (a real, repeatable
  geometric miss), only the semantic "handle"/"blade" labeling on the *successful* rows
  (A_heuristic, B_som) is what's flagged unreliable.
- `fragments.csv` and `clutter.csv` have no knife rows (mug and pot/remote respectively), so no
  citable flag was needed there.

The underlying geometric measurements (component name, point count, width, evidence class) on
knife rows are **not** claimed to be false — only which end is semantically "handle" vs "blade".
This mirrors PERCEPTION_EVIDENCE.md's own distinction ("Invalidates... the 'handle'/'blade'
semantic label... Does NOT invalidate: the component point counts, widths, evidence classes...").

## 5. Quantities with conflicting values across files (both reported, no winner picked)

- **Knife "handle" component width/point-count has THREE different measured values across three
  different sessions/isolation paths in this repo**, all nominally describing the same semantic
  target (knife handle, `captures_pairs_2/cap_knife_head_near.npz`, "pick up the knife"):
  1. **36 mm / 945 pts**, `run_knife_pick2.log:68` (`bound 'handle' -> segment_near ... 36 mm wide, 945 pts, evidence ok`) — the live pipeline run, cited by `PERCEPTION_EVIDENCE.md` as "the pipeline path's number."
  2. **31 mm / 337 pts**, `report_assets/FIGURE_MANIFEST.csv` row for `fig_stage4_knife_same_part_three_tasks.png` — the same figure's own isolation path (`scene_objects`), explicitly distinguished from (1) in that manifest row's own notes.
  3. **24 mm / 216 pts**, `report_assets/PART_NAMING_ABLATION.csv:2` (method A_heuristic, component `lateral_protrusion`) — used as the source for `components.csv`'s "knife handle" row in this task, because it's the row whose method (`bind_part`) most directly matches what "Task A: measured components" was asking about, and it's independently corroborated by `report_assets/SENSOR_ENVELOPE.md`'s own 24mm figure for "knife handle."
  All three numbers are real, logged, and internally consistent within their own session — they
  differ because they come from three different pipeline runs/isolation paths on nominally the
  same object, not because any one of them is wrong. `components.csv` cites only (3); this note
  exists so a reader doesn't cite (3) as *the* number for "knife handle width" without knowing (1)
  and (2) exist and diverge by up to 12mm/729 points.
- **The "90/94/98%" LangSAM-collapse figure** referenced in a task prompt quoted inside
  `report_assets/PERCEPTION_EVIDENCE.md` itself does not match any logged collapse percentage
  found in this session (actual: knife 97% x3, remote 88%/86%/86%). This is not a number used in
  any of the four output CSVs, but is flagged here since it's a live, unresolved discrepancy
  already on record in one of this task's own primary sources, and a reader cross-referencing
  `PERCEPTION_EVIDENCE.md` should not assume the four CSVs silently inherited the wrong figure.
- **NOT a conflict (checked and ruled out):** `batch_cluster_mug_remote_pot.json`'s `width_med`
  field (0.0918 m = 91.8mm) looks superficially like it could clash with `clutter.csv`'s
  `cluster_mug_remote_pot` remote extent of 73mm, but `width_med` is CGN's median *grasp* width
  (a different measured quantity — median over `n_ok` candidate grasps) while `minor_mm`/73mm is
  the part's own measured graspable extent; both numbers appear side-by-side, non-conflicting, in
  the same `batch_scene_analysis.csv` row. Recorded here only to document that the check was made.
- **NOT a conflict (checked and ruled out):** `archive/backups/results_home_0713/part_decomposition_table.md`
  and `experiments/part_grasp/part_decomposition_table.md` are byte-identical (same 3 mug rows,
  same numbers, same "handle has only 65 pts (<80) -- falling back to body" note) — a duplicated
  file, not a divergent one. Not used as a source for any of the four CSVs (its numbers don't
  match the task's expected component/fragment/clutter/method figures), but checked since it was
  one of the two `part_decomposition_table.md` locations the task pointed at.

## 6. `report_bundle_20260801_1611` vintage check

Per the task's ground rule, this folder was checked for same-named files that should take
precedence over root-level copies. It contains `trials.csv`, `close_params.csv`,
`gripper_gap_map.csv`, `place_run.csv`, `CONSTANTS.txt`, and capture `.npz` files under
`captures_pairs/` and `captures_obj/` — **none of these are components/fragments/clutter/
part-selection-method data**, and none share a name with any file used as a primary source above
(`SENSOR_ENVELOPE.md`, `PERCEPTION_EVIDENCE.md`, `PART_NAMING_ABLATION.csv`,
`fig_5_5_mug_fragmentation.py`, `fig_5_4_isolated_vs_cluttered.py`, `batch_scene_analysis.csv` all
exist only at their single repo-root/report_assets/figures/scripts locations, not duplicated
inside this bundle). No vintage conflict applied to this task's four outputs.
