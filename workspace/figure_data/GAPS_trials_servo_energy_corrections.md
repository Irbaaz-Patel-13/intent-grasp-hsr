# Gaps, conflicts, and sourcing notes — trials / servo / energy / corrections

Covers only the four files produced this pass: `trials_clean.csv`, `servo_trace.csv`,
`energy_inventory.csv`, `corrections.csv`. Rule followed throughout: every empty cell means "not
found in the repo," never a guess.

---

## Task A — trials_clean.csv

### Candidate trial-log files found and their row counts

Verified with `csv.reader` (field count checked against header on every row — no malformed rows
found in any of these five files):

| File | Data rows | Trial numbers present |
|---|---|---|
| `report_bundle_20260801_1611/trials.csv` | 11 | 1-7, 9-12 (no trial 8) |
| `trials.csv` (root) | 12 | 1-7, 9-12, **plus** one unlabeled row (2026-08-03, grasp=2, `GRASP_OK`, note="live demo") |
| `trials_0728.csv` | 7 | 1-7 (byte-identical to the first 8 lines — header + 7 rows — of `trials.csv`; confirmed by `diff`, no differences) |
| `Backups/2026-08-07/Afford-Grasp/trials.csv` | 12 | same as root `trials.csv` |
| `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/trials.csv` | 4 | earliest partial snapshot |

**Chosen source: `report_bundle_20260801_1611/trials.csv`** (11 rows), per the task's instruction to
prefer the bundle vintage, and because it is the one file whose row set exactly matches the required
`1-7, 9-12` range with no extra rows to explain away. The root `trials.csv`'s 12th row (2026-08-03,
"live demo") is real data but is explicitly out of scope for this task (trial numbers 1-7, 9-12
only) and was **excluded**, not folded into trial 12 or renumbered as trial 13. This exclusion is
independently confirmed correct by the repo's own prior audit: `report_bundle_20260801_1611/README.md`
states the 12th row "post-dates this bundle and was not included in any figure or count derived from
the 11-row set," and `figures/TABLE_DATA.md:203-204` reaches the same conclusion.

`log_trial.py` (root and bundle copies, byte-identical) confirms `trials.csv` is the intended
canonical output of the trial-logging workflow (appends one row per hardware run via
`csv.DictWriter`), and its own `FIELDS` list matches the columns actually found in every candidate
file above — no other output path or filename pattern was found repo-wide for this script.

Trial 8: genuinely absent. The bundle file's line 8 is trial 7, line 9 is trial 9 — no row, no
placeholder, no comment referencing trial 8 anywhere in the CSV. This gap is independently confirmed
by three other repo documents that already audited it: `report_assets/figure_audit/contradictions.md`
item 4, `codex/04_data.md` §4 "Twelfth trial", and `figures/TABLE_DATA.md` §"Twelfth trial".

### verdict -> outcome mapping

Only three distinct `verdict` values appear across the 11 in-scope rows:

| `verdict` (source) | `outcome` (mapped) | Rationale |
|---|---|---|
| `GRASP_OK` | `GRASP_OK` | Direct match, no transform needed. |
| `ABORT_` (literal, trailing underscore) | `ABORT` | `log_trial.py:82`: `r["verdict"] = "ABORT_" + grab(r"ABORT ?(\w+)", text)` — the regex for an abort *reason* suffix found no match on these two runs, so the code appended an empty string, leaving the literal string `ABORT_`. Trimmed to `ABORT` for the enum; no abort-reason text was ever recorded for trials 1 or 3. |
| `HELD_LIFT_FAULT` | `HELD_LIFT_FAULT` | Direct match, no transform needed. |

All three verdict values found map cleanly — no row was left with an empty `outcome` due to an
unmappable verdict. (`log_trial.py` also defines `EMPTY_NO_CONTACT` and `FAILED_OTHER` verdict
strings, but neither ever appears in any of the 11 real rows, so no mapping decision was needed for
them.)

### `mode` column — what was filled in and why, what was left empty

The task's `mode` enum is `hand-placed | semi | fully autonomous`. No trial's note field, and no
other document found repo-wide, ever uses the word "semi" in connection with any trial — that enum
value is simply unused in this dataset, not an omission on my part.

- **Trials 5, 7**: note field contains the literal phrase "hand-placed" → filled directly.
- **Trial 6**: note field does *not* say "hand-placed" (it says "repeat, odom reset between trials
  (incident #10), skip_base"). Filled as `hand-placed` anyway, based on: (a) `servo_used=no` in this
  row (the same field value shared by trials 5 and 7, both explicitly hand-placed), and (b)
  `report_assets/PERCEPTION_EVIDENCE.md:27` explicitly groups trials 5-7 together as the 3
  `servo_used=no` / hand-placed trials. This is an inference from a corroborating repo document, not
  a literal quote from trial 6's own row — flagged here rather than silently treated as equally solid
  as trials 5/7.
- **Trial 9**: note field contains the literal phrase "fully autonomous" → filled directly.
- **Trials 10, 11, 12**: notes contain only the bare word "autonomous" (10, 11) or no mode word at
  all (12) — none say "fully autonomous" literally. Filled as `fully autonomous` based on: same date
  (2026-08-01) and `servo_used=yes` as trial 9; and because six independent repo documents
  (`build_manifests.py:282`, `figures/TABLE_DATA.md:315-318`, `report_assets/PERCEPTION_EVIDENCE.md:27`,
  `fig_results_panel.py:159-166`, `storyboard.py:70`, `new_hw_trial_history.py:98`) all explicitly and
  repeatedly describe trials 9-12 as one "4 consecutive, fully autonomous" group.
- **Trials 1, 2, 3, 4**: left **empty**. `figures/TABLE_DATA.md`'s own Table 7.1 does classify these
  four as "autonomous," but *only* the bare word "autonomous" — the same weaker word it deliberately
  avoids using for trials 1-4 while reserving "fully autonomous" only for the 9-12 group. Since the
  task's enum has no plain "autonomous" value, and no document anywhere upgrades trials 1-4 to "fully
  autonomous" or downgrades them to "hand-placed," mapping them to either enum value would be a guess.
  Left empty rather than invented.

### Every empty cell in trials_clean.csv, and why

- `mode` empty for trials 1, 2, 3, 4 — see above.
- `z_rise_m`, `held` empty for trials 1 and 3 (`ABORT_` verdict rows) — the source CSV itself leaves
  these fields blank for both rows (grasp never reached the point where `z_rise_m`/`held` are
  measured); not a parsing artefact.
- All fields for trial 8 empty except `note` — no record exists at all, per instruction.

---

## Task B — servo_trace.csv

**No true per-iteration servo log exists anywhere in this repository.** This is not merely something
I failed to find — it was already explicitly audited and confirmed absent by two independent
documents already in the repo before this task started:

1. `fig10_visual_servo.py:9-16` (script docstring): "no per-iteration log exists anywhere in the
   evidence (docs/evidence/FIGURES_8_13_EVIDENCE_AUDIT.md, Figure 10 section, confirmed by explicit
   search of `Backups/2026-08-07/Afford-Grasp/`: no per-iteration log, no x/y error history, no
   time-series, no trial-9 image sequence, no trial-9 before/after photo pair)."
2. `docs/evidence/FIGURES_8_13_EVIDENCE_AUDIT.md:162-168`: "I searched explicitly (`grep` for
   `[center] iter`, `empirical J`, `ALIGNED within` across the entire `diagnostics/` log and every
   `results/run_07*` directory) and found no per-iteration numeric log for any single continuous run
   — only discrete before/after values per trial."

I independently re-ran the same class of search this session (`grep` for `[center] iter`,
`detected=.*err=` across every `.txt`/`.log`/`.md` file in the repo, including `Experiment_Logs/` and
`Backups/`) and found the same result: those print-format strings exist only inside the *source code*
of `hsr_final_center.py` (the `print()` call itself, e.g.
`Backups/2026-08-07/Afford-Grasp/hsr_final_center.py:172`), never in any captured terminal/log
output.

What *does* exist, and is what `servo_trace.csv` contains:

- **Trial 9**: two measured endpoints, `46.9px` (before) and `12.7px` (after) —
  `fig10_visual_servo.py:70` (`TRIAL9_BEFORE_PX, TRIAL9_AFTER_PX = 46.9, 12.7`), corroborated by
  `report_bundle_20260801_1611/trials.csv:9`'s note ("servo 46.9->12.7px + lift patch").
- **Trial 12**: one residual value, `17.4px` — `fig10_visual_servo.py:71`
  (`TRIAL12_RESIDUAL_PX = 17.4`), corroborated by `report_bundle_20260801_1611/trials.csv:12`'s note
  ("servo residual 17.4px (~12mm)").
- A third, **non-trial-specific** data point exists: `DEMO_RUNBOOK.md:249` states "Servo: 47 -> 13 px
  (~9 mm) in four iterations" as a general aggregate/typical example, explicitly *not* claimed to be
  trial 9 (its own numbers, 47/13, differ slightly from trial 9's logged 46.9/12.7). Because it
  carries no trial identifier and the task's schema requires one, I did **not** insert a row for it
  under any trial number — doing so would have required assigning it a trial number that isn't
  attested anywhere. It is reported here instead of silently dropped.

Given no real per-iteration index exists, the `iteration` column uses the descriptive labels
`before`/`after`/`final` rather than fabricated integers — using `1, 2, 3...` would imply a
resolution the data doesn't have.

`converged` and `jacobian_update` are **empty on all three rows**. Reasoning considered and rejected:
`hsr_final_center.py` raises `SystemExit("ABORT: not converged after 5 solves...")` on failure to
converge, and neither trial 9 nor trial 12 has an `ABORT` verdict — so one could argue convergence is
implied. I chose not to fill this in, because it would be inferring a state from the *absence* of an
error path rather than from a directly logged value, and the task's "never invent" rule extends to
categorical inferences, not just numbers. Likewise, `hsr_final_center.py`'s Broyden-update mechanism
is described in general terms (mechanism used by the pipeline) but no log confirms it fired on a
specific iteration of trial 9 or trial 12. Both left empty rather than guessed.

---

## Task C — energy_inventory.csv

**No measured or estimated energy/power value exists anywhere in this repository.** Searched
case-insensitively for `Wh`, `watt`, `kWh`, `power_draw`, `energy` across every `.py`, `.log`, `.txt`,
`.md`, `.json`, `.csv` file (excluding `Backups/`, `archive/`, `.venv/`). Every hit was either an
unrelated match (author affiliation "Heriot-Watt University", "energetic" false positives from
directory listing noise) or one of:

- `figures/REFERENCES_RECONCILED.md:121` — a citation to an *external* paper (Jegham et al. 2025,
  arXiv:2505.09598, "How hungry is AI? Benchmarking energy, water, and carbon footprint of LLM
  inference") — a literature reference, not a measurement of this project's own pipeline.
- `figures/SOURCE_MANIFEST.md:198` — the clearest evidence of absence: "6.2 Energy by stage |
  LITERATURE-SOURCED + measured | Jegham et al. 2025 arXiv:2505.09598; Epoch AI; **any measurable
  workstation GPU energy value (not yet located)** | **TODO** | yes | distinguish measured vs
  estimated". This is the repo's own prior audit explicitly stating this figure was never built and
  no measurable value was ever located.

Per the task's own fallback instruction, `energy_inventory.csv` contains **only the header row**:
`stage,energy_Wh,kind,basis,source`. No stage (vision-language inference, workstation compute, grasp
generation, robot motion, capture/transfer) has any real number to report.

---

## Task D — corrections.csv

### Root `corrections.csv` (not modified, read only)

`D:\Afford-Grasp\corrections.csv` (168-280 bytes) contains **five repetitions of the header row
(`claim_as_reported,re_measured_finding,what_changed`) each followed by one entirely blank data
row** — i.e. an empty five-row template, no actual claims/findings/changes present. Nothing could be
carried forward from it because it contains no data to verify. Its structure (exactly 5 header+blank
pairs) does, however, corroborate the task's premise that five corrections are the intended count —
this looks like an unfilled template for the same 5-item list reconstructed below.

### Evidence the "5 corrections" are a real, named set in this repo

`figures/BLOCKERS.md:65` and `figures/PIPELINE_CHANGES.md:53-58` both refer to "**Correction 5** from
the register's corrections table" (the `RELATION_HINTS` rekey, below) — confirming a canonical,
numbered corrections list is a real, referenced artefact in this project, even though no single
standalone file titled "corrections register" was found (searched for `CORRECTIONS_REGISTER`,
"corrections table", "corrections register" repo-wide). The other four entries below were
reconstructed from the strongest claim/re-measured-finding/what-changed narratives found across the
repo's audit documents (`cgn_metric_correction.md`, `report_assets/PERCEPTION_EVIDENCE.md`,
`report_assets/figure_audit/contradictions.md`) — all five are independently verifiable at the cited
line numbers, none invented.

### The five corrections written to `corrections.csv`

1. **CGN grasp-to-affordance metric** (`cgn_metric_correction.py`/`.md`, `cgn_candidate_analysis.md`,
   2026-07-23) — euclidean origin-to-affordance distance decomposed into depth-along-approach vs.
   perpendicular offset; the old 0.06 m euclidean criterion was unpassable by construction.
2. **Correction 5 — RELATION_HINTS rekey** (`figures/PIPELINE_CHANGES.md`, 2026-08-16) — an
   unrelated rename (`segment_mid` → `segment_b`) orphaned a hint-table dict key, silently misrouting
   the remote's "middle section"/"sides" queries to the wrong (much smaller) component; fixed by
   rekeying the hint entry.
3. **Knife segment_near/segment_far "sign flip" claim corrected** (`report_assets/PERCEPTION_EVIDENCE.md:24`)
   — original claim that handle/blade labels "flip" between isolation paths was itself wrong;
   re-measurement showed the PCA sign is stable per point set but arbitrary relative to physical
   semantics.
4. **FAILURE_REGISTER total, 13 vs. 17** (`report_assets/figure_audit/contradictions.md`, 2026-08-09)
   — the register has 17 real rows; no "13" source was found anywhere in this repo's own outputs.
5. **fig_stage7_alignment_knife.png roll-correction inconsistency** (`report_assets/PERCEPTION_EVIDENCE.md:28`)
   — figure panel visually shows a wrist-roll correction as applied, but the run's own log records
   `apply=False`; figure marked not citable.

All five were found (the task allowed for fewer than five if not all were findable — all five were
located with verifiable in-repo sources).

### `section` column

Left **empty on every row**. No source document assigns any of these five corrections to a specific
dissertation section/chapter number. `figures/BLOCKERS.md:48` ties a *related* but distinct item (the
`close_params.csv` root-vs-bundle conflict, see below) to "dissertation §3.12 (Software Engineering
and Reproducibility)," but no equivalent explicit section marker exists for any of the five
corrections actually used here. Rather than guess which chapter a given correction belongs in, this
column was left blank throughout.

### `date` column caveats

Corrections 1 and 2 have dates stated directly in their source documents (file content, not just file
mtime). Corrections 3 and 5 have **no date stated in the document text** — the dates used
(2026-08-03) are the filesystem mtime of `report_assets/PERCEPTION_EVIDENCE.md`, flagged explicitly
as such in the `source` cell rather than presented as an authored date. Correction 4's date
(2026-08-09) comes from `contradictions.md`'s own "Generated 2026-08-09T16:34:01" header line.

---

## Conflicting values found across files (both values and both locations reported, no winner picked)

1. **Root vs. bundle `trials.csv` row count.** Root has 12 data rows (11 in-scope + one 2026-08-03
   "live demo" row); `report_bundle_20260801_1611/trials.csv` has 11. `figures/SOURCE_MANIFEST.md`
   (top matter, "§0.2 data-version conflict" note) additionally states "`trials.csv`: root and bundle
   copies are byte-identical" — which is **inconsistent** with the direct `diff` run this session
   (one extra line in root, confirmed non-identical). Both claims are reported here; not resolved,
   since `SOURCE_MANIFEST.md` may simply predate the root file's 2026-08-03 append and never have
   been true at the same time as the current file states.
2. **`close_params.csv`, root vs. `report_bundle_20260801_1611/`** (adjacent to, but not part of, the
   four target files — reported because it was surfaced while investigating the corrections register
   and is exactly the same class of conflict this task asks about). `codex/04_data.md:114` and
   `figures/SOURCE_MANIFEST.md:146-147` both confirm: root `close_params.csv` (mtime 2026-08-03) has
   `part_width_m=0.0871`, `cage_motor_rad=0.832`, and `ok=1` (success) for **all 25** rows; the bundle
   copy (mtime 2026-08-01) has `part_width_m=0.087`, `cage_motor_rad=0.83`, and `ok=0` (fail) for
   **all 25** rows. Not a formatting difference — two different grasp-generation runs, both files
   internally consistent but mutually contradictory on the `ok` flag for every single row. Neither
   value was used in this task's four CSVs; reported here per the task's instruction to surface any
   two-value conflict found during the work.

## Malformed CSVs found

None of the five `trials.csv` candidates, `place_run.csv` (bundle and `Experiment_Logs/2026-08-07/`
copies), or the four output CSVs themselves had any field-count mismatch when parsed with
`csv.reader` and checked row-by-row against the header. `figures/BLOCKERS.md`'s "Data-quality items"
section separately documents a malformed file **not part of this task's scope**:
`report_assets/PART_NAMING_ABLATION.csv` has at least one row (mug/"pour me a coffee"/C_pointing)
with an unquoted comma inside the `raw_points` field (`[[800,600]]` instead of `"[[800,600]]"`),
which shifts every column after it by one under a naive `csv.DictReader`. Noted here for completeness
since it was found while searching for "malformed CSV" candidates, but it is unrelated to
trials/servo/energy/corrections.
