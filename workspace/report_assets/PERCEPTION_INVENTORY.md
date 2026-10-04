# AffordGrasp Perception Inventory

Audit only. No files were created, edited, moved, deleted, or executed except this document.
Generated 2026-08-02 from disk state, git history, and script docstrings on this machine (PC).

**Scoping note (read first):** "Machine" is inferred from each script's own docstring
(WINDOWS/LAPTOP/PC vs CONTAINER/workstation) — not verified by execution, since running
scripts was forbidden. **mtimes on git-tracked files may reflect the last `git checkout`
on this machine, not original authorship** — git-tracked files were not necessarily last
touched when their content suggests. Untracked files (`git status` `??`) have authentic
mtimes. Where mtime ordering was ambiguous, commit dates/messages or cross-references in
other scripts were used instead and are cited explicitly.

---

## Section 1 — Script classification (repo root)

87 `.py` files exist directly in the repo root (`YCB_Dataset/scripts/`,
`contact_graspnet_pytorch/`, and `hsr_description/`/`hsr_meshes/` are third-party
submodules per `.gitmodules` and are excluded — they are not part of the ~40
project-authored scripts this audit concerns. `archive/`, `report_bundle_20260801_1611/`,
`run_0716_funnel/`, `run_0722_GRASP_OK/`, and `ws_backup_0712_extract/` are backup/snapshot
directories, not live perception subdirectories; their contents are cited as **evidence**
below but are not separately classified).

Legend: **V** = VALIDATED, **S** = SUPERSEDED, **U** = UNKNOWN, **UO** = UNVERIFIED-OUTPUT
(the script ran and wrote files, but correctness of those outputs against ground truth was
never established — this is distinct from V, which requires evidence the *content* is
right, not just that a run completed).

| filename | last modified | ~lines | machine | purpose | class | evidence |
|---|---|---|---|---|---|---|
| `_tmp_extract.py` | 2026-05-16 21:10 | 7 | PC | ad-hoc dump of one JSON diagnostic's CP9 grasps | U | scratch snippet, not referenced elsewhere |
| `adapt_real_capture.py` | 2026-06-26 15:22 | 56 | PC | `head_capture_real.npz` → `multiview.npz`+`fused_cloud.npz` | V | `multiview.npz`/`fused_cloud.npz` refreshed 2026-08-02 00:21; named in `RUNBOOK.md` step 2 |
| `affordance_reasoning.py` | 2026-07-15 13:57 | 622 | PC | 3-step VLM affordance-reasoning module | V | imported live: `run_grounding_grasp.py:23` |
| `analyse_cgn_candidates.py` | 2026-07-23 13:22 | 141 | PC | why selected grasps sit ~10cm from affordance centre | V | `cgn_candidate_analysis.md` exists (23 Jul 13:26) |
| `analyse_range.py` | 2026-08-01 23:54 | 208 | PC | does a closer viewpoint resolve parts? | UO | ran and wrote `range_analysis.md`/`.csv` + 14× `fig_range_*.png` (2026-08-02 05:58), but the support-plane fit (`table["plane_z"]` from `scene_objects.find_table()`, called at `analyse_range.py:78-89`) is wrong in ≥3 of 16 far-view rows — see explicit adjudication below |
| `analyse_stability.py` | 2026-07-26 13:56 | 91 | PC | tests identification-failure propagation hypothesis | V | `stability_mechanism.md` exists (26 Jul 13:56) |
| `batch_scene_analysis.py` | 2026-07-26 14:06 | 218 | PC | drives full pipeline over every captured scene | V | `batch_scene_analysis.csv`/`.md` + 5 scene sets in `batch_out/` (26 Jul 14:08-14:11) |
| `build_region_marks.py` | 2026-06-19 21:46 | 194 | PC | two-region (neck/body) SoM overlay for one bottle | U | writes `region_marks.png`, but that file was last (over)written by `build_scene_marks.py` 4 days later (23 Jun 19:28) — its own output is not separable on disk; see §8 |
| `build_scene_marks.py` | 2026-06-23 19:27 | 202 | PC | clusters fused cloud into tabletop objects, numbered SoM overlay | V | `captures\region_marks.png`, `scene_topdown.png`, `scene_side.png` (23 Jun 19:28) |
| `capture_figure2.py` | 2026-05-14 10:40 | 195 | PC (sim) | PyBullet capture → portfolio Figure 2 composite | V | `portfolio_figures/figure2_*.png` (5 files) present, names match exactly |
| `capture_frame.py` | 2026-06-10 12:17 | 93 | workstation (container) | grabs one RGB-D frame inside ROS container | S | superseded by `capture_object.py`/`capture_pair.py`'s multi-view sequence (1 Aug); `RUNBOOK.md`'s validated procedure instead names `capture_real.py`, which is also not this file (only in `archive/backups/ws_backup_0711/`) |
| `capture_head_for_ik.py` | 2026-06-15 13:12 | 59 | workstation (container) | step 1/3 of the old IK-execution capture flow | S | superseded by `capture_object.py` (1 Aug); its downstream partners (`ground_regions_3d.py`, `execute_region_ik.py`) are also superseded — see below |
| `capture_object.py` | 2026-08-01 15:48 | 164 | workstation | full multi-view capture (head_far/near/hand_high) + JSON log | V | `cap_remote_head_far.npz`/`near.npz` (16:59), `previews/` (17:01), `batch_bowl_head_far.json` (2 Aug 00:21) all postdate this script |
| `capture_pair.py` | 2026-08-01 15:12 | 254 | workstation | multi-viewpoint capture testing range-vs-part-resolution | V | `captures_pairs/` (39 files, 28 Jul) matches its default `--outdir`; likely also produced `captures_pairs_2/` (99 files, 1 Aug) — see §8 for the provenance ambiguity vs `capture_object.py` |
| `cgn_metric_correction.py` | 2026-07-23 13:28 | 91 | PC | convention-independent grasp-to-affordance proximity metric | V | `cgn_metric_correction.md` exists (23 Jul 13:29) |
| `closure_differentiation.py` | 2026-07-22 05:02 | 99 | PC | `grasp_policy` differentiation over VLM grid results | V | `closure_differentiation.md` exists (22 Jul 05:13) |
| `config.py` | 2026-07-14 13:11 | 313 | PC | central pipeline configuration | V | imported by nearly every other script (`PipelineConfig`, `VLMConfig`) |
| `debug_hand_projection.py` | 2026-07-10 14:36 | 200 | PC | verifies hand-camera TF convention (hypothesis A) | V | finding is load-bearing in `capture_object.py`/`capture_pair.py`'s current hand-camera handling |
| `diag_log.py` | 2026-05-14 22:08 | 64 | PC | `AFFORD_DEBUG`-gated logging helper | V | imported by `grasp_generation.py`, `make_demo_video.py`, `sim_env.py`, `visual_grounding.py` |
| `diagnostic_reach.py` | 2026-05-16 20:51 | 297 | PC (sim) | HSR kinematic reach sweep | V | `results/REACH_DIAGNOSIS_V3.md` exists |
| `differentiability_bottle.py` | 2026-06-11 11:48 | 128 | PC | intent-differentiation test, mustard bottle | V (historical) | `captures\differentiability_bottle.png` (11 Jun 11:54); superseded for current reporting by `fig_intent_dissection.py` |
| `differentiability_general.py` | 2026-06-11 11:30 | 128 | PC | intent-differentiation test, configurable object (set to hammer) | V (historical) | `captures\differentiability_hammer.png` (11 Jun 11:37); superseded by `fig_intent_dissection.py` |
| `differentiability_test.py` | 2026-06-11 11:22 | 150 | PC | "THE core contribution figure" — early SAM-region version | V (historical) | `captures\differentiability.png` (11 Jun 11:23); superseded by `fig_intent_dissection.py` (1 Aug), the current headline figure built on the geometric pipeline |
| `eval_battery.py` | 2026-07-15 13:18 | 121 | PC | 6-instruction battery: constraint-based vs keyword-baseline ablation | V (partial) | `experiments/battery/battery_*.png` (6 files, 15 Jul 13:15-16); its documented `battery_results.md` was not found on disk |
| `execute_place_grasp_raw_funnel.py` | 2026-07-16 10:50 | 228 | workstation | navigate-then-grasp executor, 16 Jul funnel revision | S | superseded by `report_bundle_20260801_1611/execute_place_grasp_raw.py` (373 lines, pulled 1 Aug), which contains all five `lab_patch_07*` fixes layered on top (markers confirmed, see those rows) — this root copy predates all of them |
| `execute_region_ik.py` | 2026-06-15 13:13 | 62 | workstation (container) | step 3/3 whole-body IK execution (old flow) | S | superseded by the gate-based `execute_place_grasp_raw*.py` executor (16-28 Jul), which replaced SoM-region+IK with CGN-based 6-DoF grasps |
| `export_grasps_plain.bak.py` | 2026-06-10 17:29 | 71 | PC | GraspPose objects → plain numpy (pre-fix) | S | literal `.bak` name; `export_grasps_plain.py`'s own docstring documents the exact fix (geometry-computed `dist_to_aff`) applied over this version |
| `export_grasps_plain.py` | 2026-06-16 14:13 | 77 | PC | GraspPose objects → plain numpy arrays | V | `grasps_plain.npz` refreshed 2026-08-02 00:21; named in `RUNBOOK.md` |
| `fig_intent_dissection.py` | 2026-08-01 23:54 | 161 | PC | headline figure: one object, several intents → different parts | V | `fig_intent_mug_head_near.png`, `fig_intent_pot_head_near.png` (`report_assets/figures/`, 00:02/00:09, 2 Aug) |
| `fig_results_panel.py` | 2026-08-01 23:49 | 103 | PC | turns `trials.csv` into a 4-panel results figure | V | `fig_results.png` (`report_assets/figures/`, 23:50 1 Aug — 1 min after the script) |
| `fix_hsr_urdf.py` | 2026-03-05 00:20 | 185 | PC | converts `hsrb4s.urdf` → PyBullet-compatible urdf | V | `hsr_description/robots/hsrb4s_pybullet.urdf` exists |
| `fix_os_import.py` | 2026-07-26 14:40 | 21 | PC | one-shot patch: add missing `import os` to `run_grounding_grasp.py` | V | `run_grounding_grasp.py` currently imports `os` (line 18) |
| `grasp_align.py` | 2026-07-23 13:39 | 151 | PC | wrist-roll alignment of gripper closing axis to part geometry | V | imported directly: `batch_scene_analysis.py:94` (`pca_axes`, `align_wrist_roll`); `battery_*_align.png`/`fig_align*.png` outputs (23 Jul) produced via `visualise_alignment.py --out` |
| `grasp_close_params.py` | 2026-07-22 05:00 | 146 | PC | per-grasp closing parameters (v2) | V | `close_params.csv`/`constraints.json` refreshed 2026-08-02 00:21 |
| `grasp_diagnostic.py` | 2026-06-10 21:39 | 88 | PC | visualise why a grasp landed on the rim, not the handle | V (historical) | `captures\grasp_diagnostic.png` (10 Jun 21:40) |
| `grasp_generation.py` | 2026-06-08 18:24 | 892 | PC | Contact-GraspNet + antipodal grasp generation | V | imported live: `run_grounding_grasp.py:25` |
| `grasp_policy.py` | 2026-07-22 05:13 | 175 | PC | maps inferred task constraints → closure parameters | V | `close_params.csv`/`trials.csv` carry its `force_level`/`hold_margin`/`cage_motor` columns; `hold_margin`/`requires_controlled_tilt` markers present in `report_bundle_20260801_1611/execute_place_grasp_raw.py` |
| `ground_regions_3d.py` | 2026-06-15 13:12 | 140 | PC | SoM region selection → 3D targets for the old IK flow | S | superseded by `run_grounding_grasp.py`'s CGN-based grasp generation (26 Jul); its `region_targets.npz` output is consumed only by the now-superseded `execute_region_ik.py` |
| `hand_part_grounding.py` | 2026-07-14 13:02 | 555 | PC | grounds the graspable PART on the hand-camera view, PCA shape-classifies it | V | still imported: `eval_battery.py:11` (15 Jul); its `part_decomposition.py` dependency is documented as too narrow for non-vessel objects by `part_adaptive.py`'s own docstring |
| `hand_view_grounding.py` | 2026-06-11 10:45 | 57 | PC | linchpin test: does 'handle' ground on the hand-camera view | V (historical) | `captures\hand_view_grounding.png` (11 Jun 10:46) |
| `hsr_duck.py` | 2026-08-01 15:12 | 61 | workstation | tucks arm out of head-camera FOV before near captures | V | part of the same 1 Aug capture session as `capture_object.py`/`capture_pair.py`, whose docstrings cite the rationale for ducking |
| `hsr_peek.py` | 2026-08-01 15:12 | 144 | workstation | raises arm for a wider hand-camera view, returns to start pose | V | referenced by name in `NOTES_NEXT_SESSION.md`'s GRASP_PX discussion; part of the 1 Aug session |
| `hsr_place_down.py` | 2026-07-28 17:27 | 84 | workstation | lower + release a held object without gripper over-current fault | V | `report_bundle_20260801_1611/hsr_place_down.py` present verbatim (1 Aug pull) |
| `hsr_pose_check.py` | 2026-08-01 15:56 | 175 | workstation | verify an arm pose against the URDF before commanding it | V | written directly in response to the 1 Aug e-stop incident its own docstring describes; `report_bundle_20260801_1611/hsr_pose_check.py` present (1 Aug pull, 180 lines) |
| `illustrate_cgn.py` | 2026-06-26 15:34 | 109 | PC | clean 3D illustration of CGN grasps | V (historical) | `captures\cgn_illustration.png` (26 Jun 15:34, same minute) |
| `lab_patch_0723_close.py` | 2026-07-25 16:40 | 90 | workstation | incident #12 fix: false-contact-on-first-close-step guard | V | `TRAVEL_ARM` contact-arming logic present in `report_bundle_20260801_1611/execute_place_grasp_raw.py:307,324` |
| `lab_patch_0727_lift.py` | 2026-07-28 16:58 | 77 | workstation | over-current-during-lift fix, 3 mitigations | V | comment `"lab_patch_0727_lift L1"` literally present in `report_bundle_20260801_1611/execute_place_grasp_raw.py:339` |
| `lab_patches_0717.py` | 2026-07-21 15:07 | 104 | workstation | P1 rim-ring detector, P2 z-guard, P3 odom-reset guard | V | `"incident #10 guard"` comment (P3) present in `report_bundle_20260801_1611/execute_place_grasp_raw.py:237` |
| `lab_patches_0721.py` | 2026-07-22 16:11 | 119 | workstation | P4 contact-stop close, P5 GRASP_PX into servo | V | CONTACT-STOP/`TRAVEL_ARM` markers present in `report_bundle_20260801_1611/execute_place_grasp_raw.py:290-324` |
| `lab_patches_0722.py` | 2026-07-22 16:10 | 87 | workstation | P6 constraint-conditioned execution (force/hold/lift from policy) | V | `hold_margin`/`requires_controlled_tilt`/`effort` fields present in `report_bundle_20260801_1611/execute_place_grasp_raw.py:84-133` |
| `log_trial.py` | 2026-07-25 15:51 | 103 | workstation | turns an executor run into one `trials.csv` row | V | `trials.csv` exists with exactly its documented schema (28 Jul, 7 rows) |
| `make_demo_video.py` | 2026-07-14 13:02 | 336 | PC (sim) | 4-shot HSR demo video generator | U | no `results/hsr_demo.mp4` found under its documented default name; `results/` has `hsr_demo_hammer.mp4`, `hsr_demo_mug.mp4`, `hsr_demo_mug_smooth.mp4` which may or may not be its output — not conclusively attributable |
| `multiview_grounding_test.py` | 2026-06-11 09:41 | 51 | PC | tests handle-grounding across all 3 captured views | V (historical) | `captures\multiview_grounding.png` (11 Jun 09:43) |
| `overlay.py` | 2026-06-11 09:31 | 11 | PC | quick object/affordance-mask overlay scratch script | V (historical) | `captures\mask_overlay.png` (11 Jun 09:31, same minute) |
| `part_adaptive.py` | 2026-07-26 14:48 | 570 | PC | shape-adaptive part decomposition + part→2D-mask projection | V | imported live: `analyse_range.py`, `fig_intent_dissection.py`, `visualise_part_mask.py`, `test_components.py` |
| `part_decomposition.py` | 2026-07-14 13:02 | 253 | PC | pure-geometry rim/interior/body/handle classifier | V (scoped) | still imported live: `hand_part_grounding.py:97`; `part_adaptive.py`'s own docstring documents its generalisation failure on non-vessel objects (remote, hammer) — superseded for that scope only |
| `part_decomposition_report.py` | 2026-07-13 17:31 | 77 | PC | report figure for `part_decomposition.py` on the grasp-3 capture | V (historical) | `archive/backups/results_home_0713/part_decomposition_report.png` + `part_decomposition_table.md` |
| `patch_feasibility_note.py` | 2026-07-23 13:33 | 56 | PC | one-shot patch: correct feasibility-scan verdict text | U | target text in `run_grounding_grasp.py` not independently re-verified |
| `patch_finders.py` | 2026-08-01 23:53 | 75 | PC | one-shot patch: swap in `scene_objects.find_objects` | V | its `A_NEW`/`B_NEW` block is present verbatim in `analyse_range.py:75` and `fig_intent_dissection.py:67` |
| `patch_grounding_constraints.py` | 2026-07-22 05:08 | 51 | PC | one-shot patch: persist VLM constraints to `constraints.json` | V | `constraints.json` exists at root with the documented schema (fresh 2 Aug; `_move`/`_pour` variants 22 Jul) |
| `patch_part_scoped.py` | 2026-07-26 14:48 | 85 | PC | one-shot patch: scope CGN grasps to the selected part | V | `run_grounding_grasp.py:176` imports `part_adaptive as _pa` (the patch's own signature); part-scoped grasps visible in `fig_intent_dissection.py`/`visualise_part_mask.py` figures |
| `pick_grasp.py` | 2026-07-25 16:40 | 99 | workstation | select executable grasp: scene-relative width + lift-headroom filters | V | `report_bundle_20260801_1611/pick_grasp.py` present verbatim (1 Aug pull); `trials.csv` trial 4 note references the lift-headroom issue this fixes |
| `pipeline.py` | 2026-07-14 13:02 | 587 | PC (sim) | original end-to-end PyBullet pipeline entry point | V (historical, sim only) | `results/trial_202603*`/`trial_202604*`/`trial_202606*` (89+ dirs, Mar-Jun) match its benchmark-trial output pattern; not part of the current real-hardware chain |
| `point_prompt_grounding.py` | 2026-06-11 10:56 | 97 | PC | GPT-4o points to handle pixel, SAM segments from point (v1) | S | superseded by `point_prompt_v2.py` — no `point_prompt_grounding.png` found anywhere on disk (only v2/v3 outputs exist) |
| `point_prompt_v2.py` | 2026-06-11 11:00 | 80 | PC | fixes SAM2 point-predict path + grid overlay (v2) | V (historical) | `captures\point_prompt_v2.png` (11 Jun 11:01); superseded by `point_prompt_v3.py` per that file's own docstring |
| `point_prompt_v3.py` | 2026-06-11 11:03 | 101 | PC | box-prompt + object-mask intersection (v3) | V (historical) | `captures\point_prompt_v3.png` (11 Jun 11:04); superseded by `som_grounding.py` ("Fixes the v1-v3 failure mode", per its docstring) |
| `probe_region_select.py` | 2026-06-19 21:51 | 159 | PC | tests instruction-driven region choice on a single bottle | U | prints only, no persisted output found; its `region_marks.png`/`regions.npz` inputs were later overwritten by `build_scene_marks.py`, so its own two-region run is not separable |
| `probe_scene_select.py` | 2026-06-19 21:42 | 146 | PC | multi-object task-to-object selection via SoM | U | prints only, no persisted output found |
| `repatch_part_scoped.py` | 2026-07-26 14:46 | 17 | PC | reverts + re-applies `patch_part_scoped.py` | V | maintenance wrapper around the confirmed-applied `patch_part_scoped.py` (see that row) |
| `run_grounding_grasp.py` | 2026-07-26 14:55 | 231 | PC | runs perception stack on a real capture: reason → ground → CGN | V | `grasps_out.npz` refreshed 2026-08-02 00:21; named in `RUNBOOK.md`; imports `part_adaptive` (patch confirmed applied) |
| `scene_objects.py` | 2026-08-01 23:57 | 116 | PC | locates objects on the table vs furniture (table-footprint method) | V | imported live: `analyse_range.py`, `fig_intent_dissection.py`; `range_analysis.md` shows plausible per-object point counts (no chair-back artifact) |
| `sim_env.py` | 2026-05-17 15:21 | 1443 | PC (sim) | PyBullet simulation environment + RGB-D capture | V (sim only) | imported by `diagnostic_reach.py`, `test_hsr_loading.py`, `test_ycb_loading.py`, `capture_figure2.py`, `pipeline.py`; not part of the real-hardware chain |
| `som_grounding.py` | 2026-06-11 11:16 | 141 | PC | Set-of-Mark grounding for the task-relevant part | V (historical) | `captures\som_grounding.png`, `som_marks.png` (11 Jun 11:17); superseded for the current pipeline by geometric decomposition (commit `3de382e`) |
| `som_part_selection.py` | 2026-07-10 14:58 | 135 | PC | SoM part selection for the hand-camera grounding pipeline | V (scoped) | has its own dedicated smoke test (`test_som_part_selection.py`); its role in the CURRENT real-hardware pipeline is superseded by `part_adaptive.py`'s geometric decomposition (commit `3de382e`: "replace VLM/mask part selection with geometric decomposition") |
| `test_components.py` | 2026-07-26 14:48 | 78 | PC | CLI diagnostic: runs `part_adaptive`'s full decomposition chain on one `batch_out` scene and prints a component table + part-binding scores | U | prints only, no persisted output — but the code is complete and correctly wired (confirmed by reading it), so stdout-only is not evidence it doesn't work — **see explicit adjudication below** |
| `test_hsr_loading.py` | 2026-03-05 00:25 | 274 | PC (sim) | standalone HSR PyBullet loading/IK/gripper test | V | depends on `hsrb4s_pybullet.urdf`, which exists (confirmed `fix_hsr_urdf.py` output) |
| `test_part_decomposition.py` | 2026-07-14 13:02 | 198 | PC | synthetic-mug smoke test for `part_decomposition.py` | U | "ALL PASS"/exit-0 contract, but no persisted pass log found; `part_decomposition.py` itself is confirmed in live use via `hand_part_grounding.py` |
| `test_som_part_selection.py` | 2026-07-10 14:58 | 87 | PC | monkeypatched smoke test for `som_part_selection.py` | U | same as above, no persisted pass log |
| `test_ycb_loading.py` | 2026-03-04 05:35 | 129 | PC (sim) | smoke test for the local YCB_Dataset integration | V | `captures\test_ycb_scene.png` (4 Mar 05:36, 1 min after the script) |
| `view_captures.py` | 2026-07-25 17:22 | 68 | PC | dumps capture npz RGB/depth to PNG + contact sheets | V | `previews/`, `captures_pairs_2/previews/`, `captures_pairs/previews/`, `captures_0723/previews/` all present with exactly its documented naming |
| `visual_grounding.py` | 2026-06-11 09:26 | 847 | PC | LangSAM (GroundingDINO+SAM) affordance grounding module | V | imported live: `run_grounding_grasp.py:24` |
| `visualise_alignment.py` | 2026-07-23 13:46 | 163 | PC | report-quality 3D figure of wrist-roll alignment, before/after | V | `fig_align_handle.png`, `fig_align_mug_handle.png`, `fig_alignment_demo.png`, `fig_wrist_roll_alignment.png`, `fig_compact.png`, 6× `battery_*_align.png` (all 23 Jul 13:40-53) |
| `visualise_part_mask.py` | 2026-07-26 15:01 | 94 | PC | renders what CGN was actually scoped to (part-mask overlay) | V | `fig_part_mask_isolated.png` written 15:06 — 5 min after the script's final edit at 15:01 — **see explicit adjudication below** |
| `vlm_grid.py` | 2026-07-15 13:31 | 147 | PC | VLM-only object×instruction grid, no grounding/GPU | V (partial) | `vlm_grid_raw.json` exists (15 Jul 13:33); documented `vlm_grid_results.md` not found on disk |
| `vlm_grid_handover_v2.py` | 2026-07-15 13:40 | 116 | PC | receiver-aware handover ablation (contract v2) | V (partial) | `vlm_grid_handover_v2_raw.json` exists (15 Jul 13:42); `.md` not found |
| `vlm_identify.py` | 2026-07-26 13:35 | 185 | PC | intent-only object identification across captured scenes | V | `vlm_identify.md`/`.csv`/`_raw.json` all exist (26 Jul 13:40) |
| `vlm_stability.py` | 2026-07-26 13:45 | 118 | PC | repeats identification matrix N times, per-cell stability | V | `vlm_stability.md`/`.csv` exist (26 Jul 13:54) |

### Explicit adjudication of the 7 named scripts

| script | classification | why |
|---|---|---|
| **`part_adaptive.py`** | **VALIDATED** | Grep-confirmed live import in all four of `analyse_range.py`, `fig_intent_dissection.py`, `visualise_part_mask.py`, `test_components.py` — including the two newest scripts in the repo (1 Aug). Not superseded; it is the current shape-adaptive decomposition engine. |
| **`test_components.py`** | **UNKNOWN (re-adjudicated)** | Read in full. It is a complete, correctly-wired CLI: loads `<dir>/<scene>_fused_cloud.npz` + `_grasps_plain.npz` (default `--dir batch_out`), fits its own local support plane (`estimate_plane()`, a modal-z histogram — not `scene_objects`), then calls `part_adaptive`'s real decomposition chain in the same order `visualise_part_mask.py` does: `pa.adaptive_crop()` → `pa.isolate_object()` → `pa.classify_shape()` → `pa.find_components()` → `pa.describe_components()` → `pa.bind_part()` (once per `--parts` entry, printing a `WEAK binding` flag when the bind score is <3.0). It prints the scene name, affordance centre, plane z, crop radius/point count, isolation method, shape class, a components table, and per-part binding verdicts — no `open()`/`savefig`/`np.savez`/`.to_csv` call exists anywhere in the file, so none of this is ever persisted. **Stdout-only is not evidence of failure**: the code is functionally a non-rendering, multi-part-scoring sibling of `visualise_part_mask.py` (VALIDATED) using the identical function chain, and its inputs (e.g. `batch_out/pot_with_handle_and_lid_fused_cloud.npz`) exist. But per the rule "do not guess," absence of any persisted transcript or NOTES-doc mention still means there is no direct disk evidence a run ever completed — classification stays UNKNOWN, not VALIDATED, with the evidence description corrected to reflect a working, non-broken script rather than an unproven one. |
| **`visualise_part_mask.py`** | **VALIDATED** | `fig_part_mask.png` (14:44) predates the script's final edit (15:01); `fig_part_mask_isolated.png` (15:06) postdates it by 5 minutes and matches the `pa.isolate_object` call added in that edit — i.e. the file was run again right after being edited, and both runs left output on disk. |
| **`analyse_range.py`** | **UNVERIFIED-OUTPUT (corrected from VALIDATED)** | The script ran and wrote `range_analysis.md`/`.csv` (2026-08-02 05:58) plus 14 `fig_range_*.png` — that part of the earlier VALIDATED call was right. But VALIDATED requires the *content* to be right, and it isn't in every row. **Defect:** the support-plane fit — `table["plane_z"]`, returned by `scene_objects.find_table()` and consumed at `analyse_range.py:78-89`'s `find_object()` — comes back at ~0.015–0.026 m for the **far** captures of `pot`, `mug_hv`, and `cluster_mug_can_remote`, where every valid row sits at 0.446–0.459 m. `plane_z` is printed to stdout (`analyse_range.py:164-166`) but is **not written to `range_analysis.csv`/`.md`**, so these exact figures cannot be independently re-derived from the saved outputs without re-running the script (forbidden here) — they are taken as given from the auditor's own run. What the saved CSV *does* corroborate: those same three far-view rows have anomalously low `far_obj_pts` (pot 134, mug_hv 400, cluster_mug_can_remote 412) and `far_shape=slab`, versus far-view counts of 2356–5142 for comparable scenes (`cluster_mug_bowl_knife`, `cluster_pot_mug`) — consistent with a mis-fit plane truncating most of the true object into a thin, misclassified sliver. Every downstream number in those three far rows (`far_fine_pts`, `far_fine_mm`, `far_evidence`, and the corresponding `fig_range_{pot,mug_hv,cluster_mug_can_remote}.png` overlays) is therefore an **artefact of this defect, not a genuine measurement**, and should not be cited in the dissertation without a fix and a re-run. The other 13 objects' far rows and all 16 near rows are not implicated by this specific defect (though, per the UNVERIFIED-OUTPUT class itself, they were likewise never checked against ground truth beyond internal plausibility). <br><br>**Duplication check (read both functions):** `analyse_range.py`'s `find_object()` (line 78) calls **only** `scene_objects.find_objects()` — it does not call `part_adaptive.isolate_object` at all. Reading both: `scene_objects.find_table()`+`find_objects()` is a *seedless, whole-scene* method — it derives its own plane from a forward-region z-histogram, finds the largest coherent surface patch and treats that as "the table," then keeps above-plane clusters inside the table's own xy footprint, rejecting anything too large (>0.28 m span) or too tall (>0.22 m) to be a tabletop object; it needs no prior knowledge of where the object is. `part_adaptive.adaptive_crop()`+`isolate_object()` (used instead by `test_components.py` and `visualise_part_mask.py`) is a *seeded, single-object refiner* — it requires the caller to already supply both a `z_table` and an approximate `centroid_xy`/`seed_xy` (typically an upstream VLM affordance centre), grows a radius crop around that seed until point growth plateaus, then DBSCAN-clusters the crop and keeps only the cluster nearest the seed. **Verdict: not a straight duplicate** — different algorithms with different preconditions (global discovery vs. local refinement around a known point) — but they do overlap in responsibility (both exist to strip clutter/table/furniture down to "the object's points"), and the repo currently runs both live, in different scripts, for what is at bottom the same sub-problem. This is the same architectural fork already noted in Section 8 for `part_decomposition.py` vs. `part_adaptive.py`; it was not previously identified for the object-isolation step specifically. |
| **`fig_intent_dissection.py`** | **VALIDATED** | `fig_intent_mug_head_near.png` and `fig_intent_pot_head_near.png` exist in `report_assets/figures/`, timestamped minutes after the script's own last edit (2026-08-01 23:54 → 00:02/00:09). |
| **`fig_results_panel.py`** | **VALIDATED** | `fig_results.png` in `report_assets/figures/`, timestamped 1 minute after the script's last edit. Reads `trials.csv`, which exists with the exact schema the script expects. |
| **`scene_objects.py`** | **VALIDATED** | Grep-confirmed live import in `analyse_range.py:75` and `fig_intent_dissection.py:67`. Its own docstring states it was written because the *previous* finder locked onto the chair back in "1 Aug figures" — `range_analysis.md`'s per-object point counts (2 Aug 05:58, i.e. produced after this fix) no longer show that failure signature, corroborating the fix took effect. |

---

## Section 2 — Runbook for VALIDATED perception scripts (PC-executable only)

Workstation-side VALIDATED scripts (`capture_object.py`, `capture_pair.py`, `hsr_duck.py`,
`hsr_peek.py`, `hsr_place_down.py`, `hsr_pose_check.py`, `log_trial.py`, `pick_grasp.py`,
`execute_place_grasp_raw_funnel.py`) run via `python3 <script>` over SSH on the ROS
workstation, not `.\.venv\Scripts\python.exe` on this PC — they are listed in Section 1
with their own evidence but are excluded from this PowerShell runbook by nature of the
two-machine split described in this audit's brief.

All commands below run from `D:\Afford-Grasp` unless noted.

| script | command | inputs (exist?) | outputs (exist?) | run after |
|---|---|---|---|---|
| `adapt_real_capture.py` | `.\.venv\Scripts\python.exe adapt_real_capture.py` | `head_capture_real.npz` — **yes** (2026-08-02 00:21) | `multiview.npz`, `fused_cloud.npz` — **yes** (00:21) | (copied from workstation via `scp`) |
| `run_grounding_grasp.py` | `.\.venv\Scripts\python.exe run_grounding_grasp.py "pick up the mug"` (positional instruction string per `RUNBOOK.md`; needs `OPENAI_API_KEY` set) | `multiview.npz`, `fused_cloud.npz` — **yes** | `grasps_out.npz` — **yes** (00:21) | `adapt_real_capture.py` |
| `export_grasps_plain.py` | `.\.venv\Scripts\python.exe export_grasps_plain.py` | `grasps_out.npz` — **yes** | `grasps_plain.npz` — **yes** (00:21) | `run_grounding_grasp.py` |
| `grasp_close_params.py` | `.\.venv\Scripts\python.exe grasp_close_params.py` | `grasps_plain.npz`, `fused_cloud.npz`, `gripper_gap_map.csv` — **yes**; `grasp_policy.py` in same folder — **yes** | `close_params.csv`, `constraints.json` — **yes** (00:21) | `export_grasps_plain.py` |
| `batch_scene_analysis.py` | `.\.venv\Scripts\python.exe batch_scene_analysis.py` | `captures_*/cap_<name>.npz` sets — **yes** (multiple dirs) | `batch_scene_analysis.csv`/`.md`, `batch_out/*` — **yes** | `adapt_real_capture.py` → `run_grounding_grasp.py` → `export_grasps_plain.py` → `grasp_close_params.py` (driven internally per-scene) |
| `analyse_range.py` | `.\.venv\Scripts\python.exe analyse_range.py --dir captures_pairs_2` | `captures_pairs_2/cap_*.npz` — **yes** (99 files); `part_adaptive.py`, `scene_objects.py` alongside — **yes** | `range_analysis.md`/`.csv`, `report_assets/figures/fig_range_*.png` — **yes** | `patch_finders.py` (patches the object-finder this script uses) |
| `fig_intent_dissection.py` | `.\.venv\Scripts\python.exe fig_intent_dissection.py --cap captures_pairs_2\cap_pot_head_near.npz --intents "pick up the pot=handle" "take the lid off=lid knob" "pour from it=rim"` | `captures_pairs_2\cap_pot_head_near.npz` — **yes**; `part_adaptive.py`, `scene_objects.py` — **yes** | `report_assets/figures/fig_intent_*.png` — **yes** | `patch_finders.py`; needs a capture file as `--cap` |
| `fig_results_panel.py` | `.\.venv\Scripts\python.exe fig_results_panel.py` | `trials.csv` — **yes** | `report_assets/figures/fig_results.png` — **yes** | after hardware trials are logged via workstation `log_trial.py` |
| `visualise_part_mask.py` | `.\.venv\Scripts\python.exe visualise_part_mask.py --part handle` | `grasps_out.npz`, `multiview.npz`, `fused_cloud.npz` — **yes** (00:21); `part_adaptive.py` — **yes** | `fig_part_mask.png` (default) — **yes** (stale, 26 Jul; will be overwritten) | `run_grounding_grasp.py` |
| `visualise_alignment.py` | `.\.venv\Scripts\python.exe visualise_alignment.py --demo` | none required (`--demo` synthesizes) or `--npz experiments\part_grasp\part_grasp_handle.npz` (**yes**) | `fig_align.png` or `--out` target | none |
| `analyse_cgn_candidates.py` | `.\.venv\Scripts\python.exe analyse_cgn_candidates.py` | `results/cgn_candidates/candidates_*.npz` — **yes** (`candidates_unknown_20260722_165452.npz`) | `cgn_candidate_analysis.md` — **yes** | a CGN run that dumped raw candidates |
| `cgn_metric_correction.py` | `.\.venv\Scripts\python.exe cgn_metric_correction.py` | `results/cgn_candidates/candidates_unknown_20260722_165452.npz` — **yes** | `cgn_metric_correction.md` — **yes** | `analyse_cgn_candidates.py` (same dump) |
| `closure_differentiation.py` | `D:/Afford-Grasp/.venv/Scripts/python.exe closure_differentiation.py` | `vlm_grid_raw.json` — **yes**; `vlm_grid_handover_v2_raw.json` — **yes** (optional) | `closure_differentiation.md` — **yes** | `vlm_grid.py` (and optionally `vlm_grid_handover_v2.py`) |
| `vlm_grid.py` | `D:/Afford-Grasp/.venv/Scripts/python.exe vlm_grid.py` (needs `OPENAI_API_KEY`) | none (calls GPT-4o live) | `vlm_grid_raw.json` — **yes**; `vlm_grid_results.md` — **no, missing** | none |
| `vlm_grid_handover_v2.py` | `D:/Afford-Grasp/.venv/Scripts/python.exe vlm_grid_handover_v2.py` | none (calls GPT-4o live) | `vlm_grid_handover_v2_raw.json` — **yes**; `.md` — **no, missing** | none |
| `vlm_identify.py` | `.\.venv\Scripts\python.exe vlm_identify.py` (or `--mode both`, `--only cluster`) | captures directories — **yes** | `vlm_identify.md`/`.csv`/`_raw.json` — **yes** | none |
| `vlm_stability.py` | `.\.venv\Scripts\python.exe vlm_stability.py --repeat 5` | same as `vlm_identify.py` | `vlm_stability.md`/`.csv` — **yes** | none |
| `analyse_stability.py` | `.\.venv\Scripts\python.exe analyse_stability.py` | `vlm_stability.csv` — **yes** | `stability_mechanism.md` — **yes** | `vlm_stability.py` |
| `eval_battery.py` | `D:/Afford-Grasp/.venv/Scripts/python.exe eval_battery.py` (needs `OPENAI_API_KEY`) | none (calls GPT-4o live) | `experiments/battery/battery_*.png` — **yes** (6); `battery_results.md` — **no, missing** | none |
| `fix_hsr_urdf.py` | `python fix_hsr_urdf.py` then `python fix_hsr_urdf.py --validate` | source `hsrb4s.urdf` (in `hsr_description`/`hsr_meshes` submodules) — **yes** | `hsr_description/robots/hsrb4s_pybullet.urdf` — **yes** | clone of URDF submodules |
| `test_hsr_loading.py` | `.\.venv\Scripts\python.exe test_hsr_loading.py` (`--gui` optional) | `hsrb4s_pybullet.urdf` — **yes** | prints only + `test_hsr_scene.png`-style capture (not independently confirmed) | `fix_hsr_urdf.py` |
| `test_ycb_loading.py` | `.\.venv\Scripts\python.exe test_ycb_loading.py` (`--gui` optional) | YCB_Dataset submodule assets — **yes** | `captures\test_ycb_scene.png` — **yes** | none |
| `diagnostic_reach.py` | `.\.venv\Scripts\python.exe diagnostic_reach.py` | none (builds sim internally) | `results/REACH_DIAGNOSIS_V3.md` — **yes** | none |
| `capture_figure2.py` | `.\.venv\Scripts\python.exe capture_figure2.py` | none (spawns PyBullet scene) | `portfolio_figures/figure2_*.png` — **yes** | none |
| `view_captures.py` | `.\.venv\Scripts\python.exe view_captures.py --dir captures_pairs_2 --glob "cap_*.npz"` | capture `.npz` files — **yes** | `<dir>\previews\*.png` — **yes** | a capture run |
| `patch_finders.py` | `.\.venv\Scripts\python.exe patch_finders.py` | `analyse_range.py`, `fig_intent_dissection.py` — **yes** (already patched — rerunning is a no-op/idempotent per its own design) | in-place edits to the two target files — **already applied** | none |
| `patch_part_scoped.py` | `.\.venv\Scripts\python.exe patch_part_scoped.py` | `run_grounding_grasp.py` — **yes** | in-place edit — **already applied** (confirmed) | none |
| `repatch_part_scoped.py` | `.\.venv\Scripts\python.exe repatch_part_scoped.py` | `run_grounding_grasp.py.before_partscope` backup — **not directly verified present** | reverts + reapplies `patch_part_scoped.py` | `patch_part_scoped.py` (once, to create the backup it reverts to) |
| `fix_os_import.py` | `.\.venv\Scripts\python.exe fix_os_import.py` | `run_grounding_grasp.py` — **yes** | in-place edit — **already applied** (confirmed, line 18) | none |
| `patch_grounding_constraints.py` | `.\.venv\Scripts\python.exe patch_grounding_constraints.py` | `run_grounding_grasp.py` — **yes** | in-place edit — **already applied** | none |

Historical (V, but the scripts' own npz/png inputs from June no longer exist at the paths
their docstrings hardcode — e.g. `hand_view.npz`, `multiview.npz` from that era):
`differentiability_bottle.py`, `differentiability_general.py`, `differentiability_test.py`,
`grasp_diagnostic.py`, `hand_view_grounding.py`, `illustrate_cgn.py`,
`multiview_grounding_test.py`, `overlay.py`, `point_prompt_v2.py`, `point_prompt_v3.py`,
`som_grounding.py`, `build_scene_marks.py`, `part_decomposition_report.py` — these are not
given runbook rows because their required input files are gone; re-running them today
would need a fresh capture first, at which point they largely duplicate what
`capture_object.py`/`run_grounding_grasp.py`/`fig_intent_dissection.py` already do.

---

## Section 3 — Existing figures

**Scoping note:** "outside `.venv`" technically includes 1,380 `.png`/`.pdf` files. Of
these, `YCB_Dataset/` (78) and `hsr_meshes/` (29) and `contact_graspnet_pytorch/` (12) are
third-party asset/texture files, not figures this project produced — excluded below.
`archive/` (559 files) and `results/` (513 files) are historical backup/trial dumps; they
are summarized by count and representative content rather than enumerated file-by-file, to
keep this report usable. Full per-file detail for these two is available on request but
was judged out of proportion to the audit's purpose. All other directories (189 files) are
listed in full with pixel dimensions below.

### Structural decomposition / part masks
| file | modified | dimensions | producer | status |
|---|---|---|---|---|
| `report_assets/figures/fig_range_bowl.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_mug_bowl_knife.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_mug_can_pot.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_mug_can_remote.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_pot_mug.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_remote_knife.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_spoon_bowl.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_spoon_can_remote.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_spoon_mug_knife.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_cluster_spoon_mug_pot.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_knife.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_mug.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_mug_hv.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_pot.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_remote.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `report_assets/figures/fig_range_spoon.png` | 2026-08-02 05:58 | 2160×896 | `analyse_range.py` | FINISHED |
| `experiments/part_grasp/part_decomposition_report.png` | 2026-07-13 16:36 | 747×757 | `part_decomposition_report.py` | DEBUG (superseded subject matter) |
| `experiments/part_grasp/part_grasp_debug*.png` (4 files) | 12-13 Jul | ~1800×608 | `hand_part_grounding.py` (debug path) | DEBUG |
| `experiments/part_grasp/part_grasp_report_*.png` (3 files) | 13 Jul 16:35-36 | ~1800×608 | `hand_part_grounding.py` | DEBUG |
| `captures\region_marks.png` | 2026-06-23 19:28 | 826×626 | `build_scene_marks.py` (overwrote `build_region_marks.py`'s version) | DEBUG |
| `captures\scene_topdown.png` | 2026-06-23 19:28 | 910×780 | `build_scene_marks.py` | DEBUG |
| `captures\scene_side.png` | 2026-06-23 19:28 | 910×650 | `build_scene_marks.py` | DEBUG |
| `fig_part_mask.png` (root) | 2026-07-26 14:44 | — | `visualise_part_mask.py` (earlier run) | DEBUG |
| `fig_part_mask_isolated.png` (root) | 2026-07-26 15:06 | — | `visualise_part_mask.py` (current run) | DEBUG |

### Grounding (VLM/SAM part & object selection)
| file | modified | dimensions | producer | status |
|---|---|---|---|---|
| `report_assets/figures/fig_intent_mug_head_near.png` | 2026-08-02 00:02 | 3127×680 | `fig_intent_dissection.py` | FINISHED |
| `report_assets/figures/fig_intent_pot_head_near.png` | 2026-08-02 00:09 | 3127×680 | `fig_intent_dissection.py` | FINISHED |
| `captures\hand_view_grounding.png` | 2026-06-11 10:46 | 1790×477 | `hand_view_grounding.py` | DEBUG (historical) |
| `captures\multiview_grounding.png` | 2026-06-11 09:43 | 1757×893 | `multiview_grounding_test.py` | DEBUG (historical) |
| `captures\mask_overlay.png` | 2026-06-11 09:31 | 1790×477 | `overlay.py` | DEBUG (historical) |
| `captures\point_prompt_v2.png` | 2026-06-11 11:01 | 1289×512 | `point_prompt_v2.py` | DEBUG (historical) |
| `captures\point_prompt_v3.png` | 2026-06-11 11:04 | 1790×477 | `point_prompt_v3.py` | DEBUG (historical) |
| `captures\som_grounding.png` | 2026-06-11 11:17 | 1790×477 | `som_grounding.py` | DEBUG (historical) |
| `captures\som_marks.png` | 2026-06-11 11:17 | 640×480 | `som_grounding.py` | DEBUG (historical) |
| `captures\differentiability.png` | 2026-06-11 11:23 | 2389×491 | `differentiability_test.py` | DEBUG (historical; superseded subject) |
| `captures\differentiability_bottle.png` | 2026-06-11 11:54 | 1790×488 | `differentiability_bottle.py` | DEBUG (historical) |
| `captures\differentiability_hammer.png` | 2026-06-11 11:37 | 1790×488 | `differentiability_general.py` | DEBUG (historical) |
| `experiments/battery/battery_*.png` (6 files) | 2026-07-15 13:15-16 | 1800×608 | `eval_battery.py` | DEBUG |
| `battery_*_align.png` (root, 6 files) | 2026-07-23 13:52 | — | `visualise_alignment.py` (`--out` per instruction) | DEBUG |

### Alignment
| file | modified | dimensions | producer | status |
|---|---|---|---|---|
| `fig_align_handle.png` (root) | 2026-07-23 13:52 | — | `visualise_alignment.py` | DEBUG |
| `fig_align_mug_handle.png` (root) | 2026-07-23 13:40 | — | `visualise_alignment.py` | DEBUG |
| `fig_alignment_demo.png` (root) | 2026-07-23 13:52 | — | `visualise_alignment.py --demo` | DEBUG |
| `fig_wrist_roll_alignment.png` (root) | 2026-07-23 13:40 | — | `visualise_alignment.py` | DEBUG |
| `fig_compact.png` (root) | 2026-07-23 13:53 | — | `visualise_alignment.py` | DEBUG |

### Captures (previews / contact sheets)
| directory | files | dimensions | producer |
|---|---|---|---|
| `previews\` (root) | 3 | 640×480 (previews), 1120×448 (contact sheet) | `view_captures.py` |
| `captures_pairs\previews\` | 17 | 640×480 (previews), 1120×4032 (contact sheet) | `view_captures.py` |
| `captures_pairs_2\previews\` | 76 | 640×480 (previews), 2240×4032 (contact sheet) | `view_captures.py` |
| `captures_0723\previews\` | 9 | 640×480 (previews), 2240×896 (contact sheet) | `view_captures.py` |
| `captures\` (legacy, 33 files incl. `capture_preview.png` 1540×550, `fused_views.png` 1362×621) | Mar-Jul 2026 | mixed | various (see rows above) |

### Diagnostics (hardware / servo / reach)
| file | modified | dimensions | producer |
|---|---|---|---|
| `grasp_px_probe.png` (root) | 2026-08-01 15:34 | — | workstation capture/servo tooling |
| `final_center_debug.png` (root) | 2026-07-28 17:07 | — | `hsr_final_center.py` (workstation; not a root PC script — see §8) |
| `peek_view.png` (root) | 2026-07-28 17:12 | — | `hsr_peek.py` |
| `report_bundle_20260801_1611/*.png` (5 files) | 2026-08-01 16:11 | mixed (880×660, 640×480, 770×770) | workstation executor snapshot |
| `run_0716_funnel/*.png` (2 files) | 2026-07-16 12:29 | 880×660, 770×770 | workstation executor snapshot |
| `results/hsr_head_camera_test.png` | (in `results/`, not individually dated above) | — | workstation |

### Trial telemetry
| file | modified | dimensions | producer | status |
|---|---|---|---|---|
| `report_assets/figures/fig_results.png` | 2026-08-01 23:50 | 2295×1360 | `fig_results_panel.py` | FINISHED |

### Portfolio (early PyBullet reproduction, not HSR)
| file | modified | dimensions | producer | status |
|---|---|---|---|---|
| `portfolio_figures/figure2_composite.png` | (checkout time; git-tracked) | 2236×1447 | `capture_figure2.py` | FINISHED (for the PyBullet reproduction, not the HSR dissertation) |
| `portfolio_figures/figure2_scene_overview.png` | " | 1920×1080 | `capture_figure2.py` | FINISHED |
| `portfolio_figures/figure2_view_{front,side,top}.png` (3) | " | 640×480 | `capture_figure2.py` | FINISHED |

### Archived / historical (summarized, not enumerated)
- `archive/backups/` — 559 png/pdf files across `HSR_logs_20260714_183749/` (14 Jul
  snapshot: diagnostic visuals, `differentiability*.png`, `grasp_diagnostic.png`,
  `point_prompt_v2/v3.png`, `region_marks.png`, `som_*.png`, `test_ycb_scene.png` — all
  duplicates of the `captures\` copies above, confirming those historical scripts' outputs
  survive in at least two places), `results_home_0713/` (part-decomposition report), and
  `ws_backup_0711/`. All DEBUG/historical.
- `results/` — 513 png/pdf files, mostly inside ~90 `trial_2026030x_*`…`trial_20260608_*`
  directories (PyBullet-benchmark trial captures, March-June 2026) plus a handful of
  diagnostic pngs at top level. DEBUG/historical.

---

## Section 4 — Capture datasets

| directory | files | size | naming pattern | date range | contents |
|---|---|---|---|---|---|
| `captures/` | 33 | 19 MB | mixed legacy names (`differentiability*.png`, `region_marks.png`, `test_ycb_scene.png`, etc.) | 2026-03-04 → 2026-07-14 | **not a capture set** — a manually-collected dump of output pngs from the June/early-July exploratory grounding scripts (see Section 3) |
| `captures_pairs/` | 39 | 53 MB | `cap_<label>_head_{far,near}.npz`, `cap_mug_hv_hand.npz`, `previews/` | 2026-07-28 | single-object: `mug`, `pot`, `remote`, `spoon`; multi-object clusters: `cluster_mug_can_pot`, `cluster_mug_can_remote`, `cluster_spoon_can_remote`, `cluster_spoon_mug_pot` — produced by `capture_pair.py` |
| `captures_pairs_2/` | 99 | 94 MB | same pattern as above, plus `_depth.png` previews | 2026-08-01 | single-object: `bowl`, `knife`, `mug`, `mug_hv`, `pot`, `remote`, `spoon`; multi-object clusters: `cluster_mug_bowl_knife`, `cluster_mug_can_pot`, `cluster_mug_can_remote`, `cluster_pot_mug`, `cluster_remote_knife`, `cluster_spoon_bowl`, `cluster_spoon_can_remote`, `cluster_spoon_mug_knife`, `cluster_spoon_mug_pot` — the range-analysis dataset consumed by `analyse_range.py` (16 object conditions total); provenance vs. `capture_object.py`/`capture_pair.py` is ambiguous (see §8) |
| `captures_0723/` | 17 | 23 MB | `cap_<label>.npz` (single view only, no far/near pair), `previews/` | 2026-07-25 | single-object: `coke_can`, `dishwash_bottle`, `metal_spoon`, `pot_with_handle_and_lid`, `TV_remote`; multi-object clusters: `cluster_mug_cokecan`, `cluster_mug_cokecan_pot`, `cluster_mug_remote_pot` — the dataset `batch_scene_analysis.py` was run against |
| `batch_out/` | 24 | 34 MB | `<scene>_{close_params.csv, constraints.json, fused_cloud.npz, grasps_plain.npz}` | 2026-07-26 → 2026-08-02 | per-scene pipeline outputs for 6 scenes: 5 from `captures_0723` (26 Jul, via `batch_scene_analysis.py`) + `bowl_head_far` (2 Aug, via the current single-object pipeline) |
| `results/` | 933 | 59 MB | `trial_YYYYMMDD_HHMMSS_<object>[.zip]` (~90 dirs), plus `REACH_DIAGNOSIS*.md`, `MOTION_TRACE*_REPORT.md`, `POST_*_REPORT.md`, `*_diag.json`, `*.mp4` | 2026-03-01 → 2026-05-17 | almost entirely the **PyBullet simulation** benchmark/diagnostic era (`pipeline.py`, `diagnostic_reach.py`); single-object trials only (`mug`, `hammer`, `scissors`, `spoon`, `pan`, `cup`, `wine_glass`, `bottle`) — no clutter/multi-object scenes |
| `report_assets/` | 19 (in `figures/`) | 32 MB | `fig_*.png` | 2026-08-01 → 2026-08-02 | current dissertation-figure output directory (see Section 3) |

---

## Section 5 — Results and data

| file | modified | contents (one line) |
|---|---|---|
| `batch_scene_analysis.csv` / `.md` | 2026-07-26 14:11 | Per-scene pipeline generality table across 5 `captures_0723` objects (object ID confidence, target part, width/roll gates) |
| `vlm_identify.md` / `.csv` / `_raw.json` | 2026-07-26 13:40 | Intent-only object identification results — does the reasoner infer the right object from intent alone, across captured scenes |
| `vlm_stability.md` / `.csv` | 2026-07-26 13:54 | 5-pass repeat of the identification matrix; per-cell stability given non-deterministic GPT-4o at temperature=0 |
| `stability_mechanism.md` | 2026-07-26 13:56 | Contingency table pairing step-1 abstracted object type against outcome, testing the over-abstraction failure hypothesis |
| `cgn_candidate_analysis.md` | 2026-07-23 13:26 | Analysis of the raw 200-candidate CGN dump vs. the 25 that survive selection (H1/H2/H3 hypotheses on why grasps land ~10cm from the affordance centre) |
| `cgn_metric_correction.md` | 2026-07-23 13:29 | Convention-independent (perpendicular-offset) grasp-to-affordance proximity, replacing the origin-to-centre Euclidean metric |
| `closure_differentiation.md` | 2026-07-22 05:13 | Constraint-conditioned closure parameters generated from the saved VLM grid runs, per-object differentiation counts |
| `range_analysis.md` / `.csv` | 2026-08-02 05:58 | Far-vs-near viewpoint comparison across 16 object conditions — does a closer view resolve graspable parts (printed in full below) |
| `constraints.json` / `_move.json` / `_pour.json` | 2026-07-22 → 2026-08-02 | Per-run inferred VLM task constraints (target_part, keep_clear, stability_priority, post_grasp_motion, thermal_or_hygiene) |
| `close_params.csv` / `_move.csv` / `_pour.csv` | 2026-07-22 → 2026-08-02 | Per-grasp closing parameters (width, force level, cage clearance, hold margin) from `grasp_close_params.py` |
| `gripper_gap_map.csv` | 2026-07-14 18:37 | Measured gripper-motor-position-to-physical-gap calibration table |
| `trials.csv` | 2026-07-28 18:09 | Hardware trial log, one row per executor run (printed in full below) |
| `vlm_grid_raw.json` / `vlm_grid_handover_v2_raw.json` | 2026-07-15 13:33/13:42 | Raw GPT-4o responses for the object×instruction reasoning grid (contract v1) and the 6-cell handover ablation (contract v2) |
| `batch_bowl_head_far.json` / `batch_cluster_*.json` / `batch_TV_remote.json` / `batch_metal_spoon.json` / `batch_pot_with_handle_and_lid.json` | 2026-07-26 → 2026-08-02 | Per-scene capture/run metadata logs (one per `batch_scene_analysis.py` or `capture_object.py` run) |
| `_organize_manifest.md` / `_organize_plan.md` | 2026-07-19 | A prior file-organization pass's manifest and plan (housekeeping, not perception analysis) |

### `trials.csv` (printed in full)

```csv
timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note
2026-07-25 15:56:45,16,ABORT_,,,,-0.145,contact,,,,close_params.csv,firm,0.739,0.614,0.000,0.0001,0.0001,0.02,yes,"trial 1, skip_base validation"
2026-07-25 16:13:34,5,GRASP_OK,True,0.0961,-0.3115,-0.312,contact,0.685,0.685,yes,close_params.csv,standard,0.823,0.493,0.000,0.0004,0.0001,0.01,yes,"trial 2, lower surface, tol 6px"
2026-07-25 16:34:26,10,ABORT_,,,,+0.741,contact,,,,close_params.csv,firm,0.742,0.486,0.000,0.0017,0.0,0.0,yes,"trial 3, recorded, autonomous"
2026-07-25 16:53:59,16,HELD_LIFT_FAULT,True,0.0001,-0.3546,-0.355,contact,0.685,0.526,NO,close_params.csv,firm,0.748,0.492,0.000,0.0026,0.0001,0.01,yes,"trial 4, grasp 16, i12 fix, tol 20px"
2026-07-28 17:17:07,5,GRASP_OK,True,0.1534,-0.2936,-0.294,contact,0.685,0.685,yes,close_params.csv,firm,0.736,0.485,0.000,0.001,0.0001,0.02,no,"trial 5, lift patch, hand-placed (servo out of basin: mug at FOV edge)"
2026-07-28 17:23:04,5,GRASP_OK,True,0.1532,-0.2606,-0.261,contact,0.685,0.685,yes,close_params.csv,firm,0.736,0.485,0.000,0.0008,0.0001,0.02,no,"trial 6, repeat, odom reset between trials (incident #10), skip_base"
2026-07-28 17:24:40,5,GRASP_OK,True,0.1532,-0.2937,-0.294,contact,0.685,0.685,yes,close_params.csv,firm,0.736,0.485,0.000,0.0004,0.0002,0.03,no,"trial 7, repeat, hand-placed"
```

### `range_analysis.csv` (printed verbatim, read directly from disk — supersedes the earlier reconstruction, which used guessed column names and rounded values)

```csv
object,far_depth,near_depth,far_obj_pts,near_obj_pts,far_shape,near_shape,far_fine_pts,near_fine_pts,far_fine_mm,near_fine_mm,far_evidence,near_evidence
bowl,1.3760000467300415,0.9430000185966492,0,0,-,-,0,0,0,0,none,none
cluster_mug_bowl_knife,1.3539999723434448,0.9459999799728394,2356,2208,vessel,slab,52,428,14,18,NOISE,ok
cluster_mug_can_pot,1.5360000133514404,1.2100000381469727,0,2269,-,blob,0,43,0,3,none,NOISE
cluster_mug_can_remote,1.5360000133514404,1.180999994277954,412,2048,slab,blob,45,58,11,6,NOISE,NOISE
cluster_pot_mug,1.3539999723434448,0.9589999914169312,5142,2509,wide_blob,slab,173,338,7,15,LOW,ok
cluster_remote_knife,1.3539999723434448,0.9229999780654907,1515,2742,slab,slab,120,30,31,5,ok,NOISE
cluster_spoon_bowl,1.3589999675750732,0.9459999799728394,161,1359,slab,slab,0,83,0,12,none,LOW
cluster_spoon_can_remote,1.5360000133514404,1.1770000457763672,0,1125,-,slab,0,51,0,8,none,NOISE
cluster_spoon_mug_knife,1.3650000095367432,0.9229999780654907,2268,1810,vessel,blob,77,30,9,4,LOW,NOISE
cluster_spoon_mug_pot,1.3760000467300415,1.034000039100647,0,3510,-,vessel,0,171,0,12,none,ok
knife,1.3650000095367432,0.9129999876022339,979,1638,elongated,slab,89,769,11,19,LOW,ok
mug,1.3700000047683716,0.925000011920929,1508,1942,blob,blob,44,36,3,3,NOISE,NOISE
mug_hv,1.5160000324249268,1.180999994277954,400,656,slab,slab,153,42,88,6,ok,NOISE
pot,1.3760000467300415,0.9890000224113464,134,3148,slab,slab,35,131,40,9,NOISE,LOW
remote,1.3700000047683716,0.9200000166893005,2177,4677,slab,slab,67,284,9,18,LOW,ok
spoon,1.3700000047683716,0.9179999828338623,0,2087,-,slab,0,47,0,5,none,NOISE
```

Note the real header has no `depth_far_m`/`pts_far`/etc. column names as previously (wrongly)
reconstructed — the actual fields are `far_depth`, `near_depth`, `far_obj_pts`, `near_obj_pts`,
`far_shape`, `near_shape`, `far_fine_pts`, `near_fine_pts`, `far_fine_mm`, `near_fine_mm`,
`far_evidence`, `near_evidence`. It also carries a `far_shape`/`near_shape` column (`vessel`,
`slab`, `blob`, `wide_blob`, `elongated`, or `-` when no object was isolated) that the
rendered `.md` table and the earlier reconstruction both omitted entirely. `far_depth`/
`near_depth` are the capture's **median camera depth** (`cap["depth_med"]`), not the
support-plane height — see the `analyse_range.py` UNVERIFIED-OUTPUT entry above for why
that distinction matters: the plane-fit defect described there is not visible in this file
at all, because `plane_z` itself was never written to a column here.

---

## Section 6 — Handoff documents (printed in full)

Files found matching `HANDOFF`, `NOTES`, `ADDENDUM`, `RUNBOOK`, `README`, or `skeleton`
(case-insensitive), excluding `.venv`: **7 files**. No `HANDOFF`, `ADDENDUM`, or `skeleton`
files exist anywhere in the repo.

### `D:\Afford-Grasp\NOTES_NEXT_SESSION.md` (root — the live, current one)

```markdown
# Session 2026-07-11 wrap — state + next actions
FINDING: final-centering diverged because the TARGET PIXEL is computed via the broken
hand-camera model (K=0, fisheye, TF/mount mismatch ~80deg, sensitivity 3-6x off).
Empirical-J servo mechanics are proven (actual-displacement fix works, Broyden in place).
FIX (first job next lab): calibrate the grasp-axis pixel ONCE empirically:
  robot at standoff -> hand_view pose over mug -> manually verify/execute one descend+close
  that captures the mug -> record mug's detected pixel in the frame just before close
  -> hardcode as GRASP_PX in hsr_final_center.py, delete the palm-projection target entirely.
BUMPER: guard fired correctly when servo diverged into table. No damage observed (verify on arrival).
STATE: place_run.ref polluted by servo moves — next session is a FULL fresh run (rm ref, stow, capture).
GATE DISCIPLINE: abort = stop. No stage runs after an abort, ever.
SERVO DATA (dissertation figure): settle noise 0.02m measured; J columns ~330-540 px/m vs
analytic 1450; iter-0 prediction (-35,+20) vs observed (-5.7,+90.9) px.

## 16 Jul session (funnel first hardware run)
- palm_tip_dz = 0.069 (measured at cage+grasp wrist pose) -- ROBOT CONSTANT, use --palm_tip_dz 0.069
- Funnel executed end-to-end; slow close CAUGHT toppled mug (held=True, -0.32) vs Tuesday's ejection
- LIVE PATCHES on execute_place_grasp_raw.py: lift-first transit, lift headroom clamp+abort, wrist clamp -1.90, descend+lift execution-verify. hsr_preflight.py: C7 palm-z bound now aff-relative. All differ from backups.
- OPEN BUGS (patches coming from home session): probe detector blind on WHITE table (brightest-blob locks on tabletop); hsr_hand_view z>1.0 guard stale for tall table; NO ref-freshness guard (odom reset + stale place_run.ref = drove into table, incident #10)
- UNRESOLVED: lift trajectory didn't execute on loaded gripper during grasp attempt (headroom was fine; wrist clamp may fix; instrumented now) -- check /hsrb/arm_trajectory_controller/state if it recurs
- New-table envelope: plane_z 0.745 (vs 0.457), manip degraded (best 0.14 vs 0.185), wrist_flex saturates, min-depth gate needed base +0.10 step-in

## 16 Jul session (funnel first hardware run)
- palm_tip_dz = 0.069 (measured at cage+grasp wrist pose) -- ROBOT CONSTANT, use --palm_tip_dz 0.069
- Funnel executed end-to-end; slow close CAUGHT toppled mug (held=True, -0.32) vs Tuesday's ejection
- LIVE PATCHES on execute_place_grasp_raw.py: lift-first transit, lift headroom clamp+abort, wrist clamp -1.90, descend+lift execution-verify. hsr_preflight.py: C7 palm-z bound now aff-relative. All differ from backups.
- OPEN BUGS (patches coming from home session): probe detector blind on WHITE table (brightest-blob locks on tabletop); hsr_hand_view z>1.0 guard stale for tall table; NO ref-freshness guard (odom reset + stale place_run.ref = drove into table, incident #10)
- UNRESOLVED: lift trajectory didn't execute on loaded gripper during grasp attempt (headroom was fine; wrist clamp may fix; instrumented now) -- check /hsrb/arm_trajectory_controller/state if it recurs
- New-table envelope: plane_z 0.745 (vs 0.457), manip degraded (best 0.14 vs 0.185), wrist_flex saturates, min-depth gate needed base +0.10 step-in

## 16 Jul session (funnel first hardware run)

- palm_tip_dz = 0.069 (measured at cage+grasp wrist pose) -- ROBOT CONSTANT, use --palm_tip_dz 0.069
- Funnel executed end-to-end; slow close CAUGHT toppled mug (held=True, -0.32) vs Tuesday's ejection
- LIVE PATCHES on execute_place_grasp_raw.py: lift-first transit, lift headroom clamp+abort, wrist clamp -1.90, descend+lift execution-verify. hsr_preflight.py: C7 palm-z bound now aff-relative. All differ from backups.
- OPEN BUGS (patches coming from home session): probe detector blind on WHITE table (brightest-blob locks on tabletop); hsr_hand_view z>1.0 guard stale for tall table; NO ref-freshness guard (odom reset + stale place_run.ref = drove into table, incident #10)

- UNRESOLVED: lift trajectory didn't execute on loaded gripper during grasp attempt (headroom was fine; wrist clamp may fix; instrumented now) -- check /hsrb/arm_trajectory_controller/state if it recurs
- New-table envelope: plane_z 0.745 (vs 0.457), manip degraded (best 0.14 vs 0.185), wrist_flex saturates, min-depth gate needed base +0.10 step-in
```

**Note on this file's own duplication:** the "16 Jul session" block is pasted in three times
verbatim (lines 15-21, 23-29, 31-39 in the source) — an artifact of the notes file itself
having been appended to carelessly, not something this audit introduced. **Also note the
file has not been updated since 16 Jul**, despite six more sessions of hardware work
(22, 23, 25, 27, 28 Jul, 1-2 Aug per `trials.csv`, `lab_patch_*.py`, and commit `6fce4c9`)
having happened since. It is stale relative to the current state of the executor.

### `D:\Afford-Grasp\README.md` (root)

Describes the **original PyBullet/UR5 reproduction** of the AffordGrasp paper (installation,
`pipeline.py` usage, module docs for `sim_env.py`/`affordance_reasoning.py`/
`visual_grounding.py`/`grasp_generation.py`, paper benchmark numbers). It explicitly says,
under "Extending This Work — For the Toyota HSR (dissertation)": *"Replace UR5 URDF with
HSR URDF in `sim_env.py`... Integrate with ROS for real-world deployment"* — i.e. **this
README describes the starting point, not the current HSR/real-hardware system** that the
other 80+ root scripts and this audit's evidence describe. It has not been updated to
reflect the real-hardware pipeline, workstation/PC split, or any of the July/August work.

### `D:\Afford-Grasp\archive\backups\ws_backup_0711\NOTES_NEXT_SESSION.md`

Identical to the first 14 lines of the current root `NOTES_NEXT_SESSION.md` above (the
11 Jul session wrap) — this is the source snapshot the root file was later appended to.

### `D:\Afford-Grasp\archive\backups\ws_backup_0711\results\run_0712_servo_session\NOTES_NEXT_SESSION.md`

Byte-identical to the above (same 11 Jul content, archived a second time inside the servo
session's own results folder).

### `D:\Afford-Grasp\archive\backups\ws_backup_0711\RUNBOOK.md`

```markdown
# AffordGrasp hardware run — standard procedure (validated 2026-07-06)
# ssh workstation2@192.168.2.98

## Setup
- Robot ~0.9-1.0 m from table edge, square on. Mug within ~15 cm of edge.
- rm -f place_run.ref
- python3 go_stow.py                       # arm tucked (refine needs clear camera)
- head down:   python3 head_pose.py -0.60
- python3 capture_real.py                  # GATE: depth min ~0.6-1.0
- Base + head FROZEN after capture.

## PC (PowerShell, .venv)
- key check: python -c "import os; print(os.environ.get('OPENAI_API_KEY','NOT SET')[-6:])"
- scp workstation2@192.168.2.98:~/Afford-Grasp/Afford-Grasp/head_capture_real.npz .
- python adapt_real_capture.py             # GATE: within-cloud OK
- python run_grounding_grasp.py "pick up the mug"     # GATE: no 401
- python export_grasps_plain.py            # GATE: aff FRESH (differs from last run)
- scp grasps_plain.npz fused_cloud.npz workstation2@192.168.2.98:~/Afford-Grasp/Afford-Grasp/

## Workstation
- ./run_pipeline.sh grasps_plain.npz fused_cloud.npz place_run
    GATES: keep-out cells printed; keep-out clearance min >= 0.32; 25/25; GO grasp N
- execute dry:   python3 execute_place_grasp_raw.py --urdf hsrb.urdf --csv place_run.csv --grasp N --ref_file place_run.ref --dry
- stage base:    ... --stage base          # GATE: G1 True; hands off base
- refine:        python3 hsr_refine_nudge.py
    RULES: arm must be STOWED; ABORT = STOP, never proceed past a refine abort
- grasp:         ... --stage grasp         # GATE: G2 -> G3 held:True -> GRASP OK
- archive: mkdir -p results/run_$(date +%m%d_%H%M) && cp place_run.csv place_run.ref place_run_map.png grasps_plain.npz results/run_$(date +%m%d_%H%M)/

## Gate telemetry reference
- hand_motor: -0.8899 empty | -0.877 rim pinch | -0.276 body grip | threshold -0.885
- G3 success reads: z_rise ~0.10+, held True
```

**This is the only file in the repo that names itself a validated standard procedure** —
dated 6 Jul, before most of the `lab_patch_*.py` fixes existed. It references
`capture_real.py`, `go_stow.py`, `head_pose.py`, `hsr_refine_nudge.py`, `run_pipeline.sh`
— **none of which exist at the current repo root** (only `go_stow.py`/`head_pose.py` exist
inside this same archive backup; `capture_real.py` similarly only archived; `hsr_refine_nudge.py`
and `run_pipeline.sh` were not found anywhere outside `archive/`). This procedure is
superseded in spirit by the `capture_object.py`/`capture_pair.py` + `hsr_pose_check.py` +
`execute_place_grasp_raw*.py` + `lab_patch_*.py` chain, but **no equivalent up-to-date
RUNBOOK exists at the live repo root** — see Section 8.

### `D:\Afford-Grasp\hsr_description\README.rst` (submodule)

```rst
hsr_description
===============================================================================

Toyota HSR - URDF robot models
```

### `D:\Afford-Grasp\hsr_meshes\README.md` (submodule)

```markdown
hsr_meshes
===============================================================================

Toyota HSR - 3D mesh files

[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License badge/link]
```

---

## Section 7 — Version control

- **Git repository:** yes.
- **Branch:** `fix-affordance-prompt-degeneracy`
- **Working tree:** dirty — 10 modified tracked files, 21 untracked files/directories
  (see raw status below). None of this audit's actions changed that state except adding
  `report_assets/PERCEPTION_INVENTORY.md`.

### Last 20 commits

```
6fce4c9  2026-07-31 21:34  Hardware trials 0716-0728, CGN metric correction, intent-only eval, part_adaptive
935fd2a  2026-07-14 13:16  fix: remove biasing worked example and add strict keep_clear justification
fc1daca  2026-07-14 12:55  fix: reject empty-bucket direct-match selection; surface fallback notes in battery table
d6bebc6  2026-07-13 23:02  feat: add six-instruction eval battery with naive-keyword-baseline ablation
2341117  2026-07-13 23:02  feat: replace instruction-keyword part routing with constraint-enforced VLM pass-through
79b6f1c  2026-07-13 22:39  feat: replace instruction-keyword part routing with constraint-enforced VLM pass-through
96fddba  2026-07-13 22:30  feat: replace grasp-approach VLM contract with constraint-based reasoning
2b581a0  2026-07-13 16:34  fix: use view-frame parts for report figure, dedupe part constants
ec2263b  2026-07-13 16:21  feat: add three-instruction geometric part decomposition report
3de382e  2026-07-13 16:08  refactor: replace VLM/mask part selection with geometric decomposition
b0b75d6  2026-07-13 15:41  feat: add geometric rim/interior/body/handle part classifier
93f1d66  2026-06-11 09:52  Remove local settings with secrets from tracking
f88df47  2026-05-19 11:58  Add SAM ViT model weights file (sam_vit_h_4b8939.pth)
716ce87  2026-05-14 10:50  fix: add path entries to .gitmodules and reset YCB_Dataset pointer
5b9c321  2026-05-14 10:48  chore: register YCB_Dataset in .gitmodules
364e391  2026-05-14 10:44  chore: point hsr_description submodule at fork with PyBullet URDF
80ecc66  2026-05-14 10:44  chore: point CGN submodule at fork with NumPy 2.0 fix
9cfbf26  2026-05-14 10:40  chore: update submodule pointers (YCB_Dataset, contact_graspnet_pytorch, hsr_description)
6cf5e1b  2026-05-14 10:40  feat: add figure capture and demo video scripts; refine pipeline and sim_env
0e35cb7  2026-05-14 10:40  chore: add .gitignore for pycache, venv, results, and portfolio artefacts
```

### `git status --porcelain`

```
 M capture_pair.py
 M close_params.csv
 M constraints.json
 M fused_cloud.npz
 M grasp_px_probe.png
 M grasps_out.npz
 M grasps_plain.npz
 M head_capture_real.npz
 M hsr_peek.py
 M multiview.npz
?? analyse_range.py
?? batch_bowl_head_far.json
?? batch_out/bowl_head_far_close_params.csv
?? batch_out/bowl_head_far_constraints.json
?? batch_out/bowl_head_far_fused_cloud.npz
?? batch_out/bowl_head_far_grasps_plain.npz
?? cap_remote_head_far.npz
?? cap_remote_head_near.npz
?? capture_object.py
?? captures_pairs_2/
?? fig_intent_dissection.py
?? fig_results_panel.py
?? hsr_duck.py
?? hsr_pose_check.py
?? patch_finders.py
?? previews/
?? range_analysis.csv
?? range_analysis.md
?? report_assets/
?? report_bundle_20260801_1611/
?? scene_objects.py
```

Note: `report_assets/` itself is untracked — this inventory file is being added inside a
directory git does not yet know about (it will show as part of that same `??` entry, not
as a new distinct line).

---

## Section 8 — Gaps and duplication

### Referenced but missing from disk
- `RUNBOOK.md` (the only file that calls itself validated) names `capture_real.py`,
  `go_stow.py`, `head_pose.py`, `hsr_refine_nudge.py`, and `run_pipeline.sh` as the
  workstation-side steps. **None exist at the current repo root** — `go_stow.py` and
  `head_pose.py` exist only inside `archive/backups/ws_backup_0711/`; `capture_real.py`
  likewise only archived; `hsr_refine_nudge.py` and `run_pipeline.sh` were not found
  anywhere in the repo (including archive). If the workstation still has local copies not
  mirrored here, that is outside this audit's visibility (PC only).
- `execute_place_grasp_raw.py` (the plain name, used by `RUNBOOK.md`, all five
  `lab_patch_*.py` files' anchor-text, and `pick_grasp.py`'s companion) does not exist at
  repo root — only `execute_place_grasp_raw_funnel.py` (16 Jul, 228 lines, pre-dates all
  the patches) does. The current, fully-patched version (373 lines) exists only inside
  `report_bundle_20260801_1611/`, a one-off snapshot pulled from the workstation on 1 Aug.
  **If that snapshot folder were deleted, the current executor's source would not exist
  anywhere in this repo.**
- `eval_battery.py`'s documented `battery_results.md`, `vlm_grid.py`'s documented
  `vlm_grid_results.md`, and `vlm_grid_handover_v2.py`'s documented
  `vlm_grid_handover_v2.md` are all missing — only their `_raw.json`/`.png` companions
  survive. The formatted tables could be regenerated from the raw JSON without new API
  calls, if needed.
- `patch_grounding_constraints.py` and `lab_patches_0721.py`'s P5 both describe writing
  `run_grounding_grasp.py.before_constraints`/similar backup files as safety nets; these
  backup files were not confirmed present at repo root (not searched for specifically
  beyond the two named-adjudication checks in Section 1).

### Duplicate/overlapping scripts (same job, different evidence quality)
- **`capture_object.py` vs `capture_pair.py`** (both 1 Aug, 36 min apart): near-identical
  purpose (multi-view single-object capture with head_far/near + optional hand view).
  `capture_object.py` is the later revision and has the freshest, most specific evidence
  (`cap_remote_head_far/near.npz`, `batch_bowl_head_far.json`); `capture_pair.py` has the
  older `captures_pairs/` set and possibly `captures_pairs_2/` (ambiguous — both scripts
  accept `--outdir`, and neither's default matches `captures_pairs_2`, so provenance can't
  be resolved from disk alone). **Recommendation for a future session: check which script
  the workstation currently invokes, and delete or clearly mark the other as historical.**
- **`build_region_marks.py` vs `build_scene_marks.py`**: both write to `region_marks.png`
  (and both use `regions.npz`). `build_scene_marks.py` ran later (23 Jun vs 19 Jun) and its
  output is what currently sits on disk — `build_region_marks.py`'s distinct two-region
  (neck/body) output has been silently overwritten. This is a **filename collision**, not
  just chronological supersession.
- **`execute_place_grasp_raw_funnel.py`** (root) vs **`report_bundle_20260801_1611/execute_place_grasp_raw.py`**
  vs **`run_0716_funnel/execute_place_grasp_raw.py`** vs **archived copies** in
  `archive/backups/ws_backup_0711/` (7 different `.before_*`/`.BACKUP_SAFE` variants) and
  `ws_backup_0712_extract/`: at least 10 copies of this one file exist across the repo at
  different patch states. The `report_bundle_20260801_1611/` copy (373 lines) is the best
  evidenced as current (see Section 1), but it lives in a dated snapshot folder, not at a
  stable path.
- **`differentiability_test.py` / `_bottle.py` / `_general.py`** vs **`fig_intent_dissection.py`**:
  both pairs test "same object/region set, different instruction → different selected
  region," which is the dissertation's central claim. The June trio used LangSAM
  SAM-region prototyping on synthetic/early captures; `fig_intent_dissection.py` (1 Aug)
  does the same experiment on the current geometric-decomposition pipeline with real
  captures and is the better-evidenced, currently-relevant version.
- **`part_decomposition.py`** (rim/interior/body/handle, vessel-only) vs **`part_adaptive.py`**
  (shape-adaptive, general): both are live (imported by different current scripts —
  `hand_part_grounding.py` vs. `analyse_range.py`/`fig_intent_dissection.py`/
  `visualise_part_mask.py`/`test_components.py`), but `part_adaptive.py`'s own docstring
  documents `part_decomposition.py`'s failures on non-vessel objects. **The repo currently
  runs two different part-classification algorithms depending on which entry script is
  used** (`hand_part_grounding.py` vs. the newer geometry scripts) — this is a live
  architectural fork, not settled supersession.
- **`point_prompt_grounding.py` → `point_prompt_v2.py` → `point_prompt_v3.py` → `som_grounding.py` → `som_part_selection.py`**:
  a clean, well-documented iteration chain (each file's docstring names the specific
  failure of its predecessor). Only the last two (`som_part_selection.py`,
  `hand_part_grounding.py`) are current; the first three are historical only.

### Purpose could not be determined
- None outright — every root `.py` file had either a docstring or clear leading-comment
  purpose statement. The genuine uncertainty in this audit is **evidence of execution**
  (UNKNOWN classifications above), not purpose.
