# Figure Audit

Audited every image under `report_assets/`, `figures/`, `generated_assets/`, `portfolio_figures/`, `previews/`, the top level of `report_bundle_20260801_1611/`, and standalone `fig_*` / `*_align` / `*.svg` files at the repo root. Dimensions were read with Pillow (`.venv\Scripts\python.exe`) via a batch script; duplicate detection used MD5 hashing across all PNG/JPG files in scope. A number of images were opened directly to verify content where filenames alone were ambiguous or a known bug was suspected.

Legend: **KEEP** = fine as-is. **REGENERATE** = content is fine/salvageable but resolution, framing, or labelling should be redone. **DO NOT USE** = wrong, misleading, blank, or superseded — should not appear in the report.

---

## 1. `report_assets/figures/` (69 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| figdeck_binding_test.png | 1400×900 | Bar chart: `RELATION_HINTS` score vs. hints-removed score, showing the LLM binder can't discriminate a real part name from gibberish once hints are removed | KEEP | Opened — clean, legible, correct content |
| figdeck_naming_ablation.png | 2200×1100 | Intended: naming-ablation comparison (per `figdeck_naming_ablation.py`) | **DO NOT USE** | Opened — the file is **completely blank** (uniform off-white canvas, no plotted content). Confirms the reported "renders blank" issue. Script ran (file exists, non-trivial byte count) but produced no visible content — likely all-NaN/empty data path. Needs a source-data fix, not just a re-run |
| figdeck_resolution_floor.png | 1400×1000 | Dot plot: component width (px) per part vs. sensor evidence floor, showing mug handle falls into "NOISE" | KEEP | Opened — clean, legible |
| figdeck_trials.png | 2400×1200 | Timeline of 12 hardware trials with servo/hand-placed/no-record annotations | KEEP | Opened — clean, legible |
| fig_intent_mug_head_near.png | 3127×680 | 4-panel: mug geometric decomposition + 3 intent-conditioned part selections ("hot drink"→REFUSED, "pour it out"→rim, "move it aside"→body) | KEEP | Opened — correct, matches known evidence-gate behaviour for mug handle (see CGN diagnostic memory) |
| fig_intent_pot_head_near.png | 3127×680 | Same layout, pot object | KEEP | Same family/size as verified `fig_intent_mug_head_near.png`; not opened individually but naming/structure consistent |
| fig_limitation_pot_capture.png | 640×480 | Raw capture illustrating a pot capture limitation | REGENERATE | Long edge 640px, well under the 1200px floor |
| fig_range_bowl.png | 2160×896 | Two-panel far/near capture of a bowl, both flagged "object not isolated" | KEEP | Opened — correct, clearly labelled failure case |
| fig_range_cluster_*.png (8 files: mug_bowl_knife, mug_can_pot, mug_can_remote, pot_mug, remote_knife, spoon_bowl, spoon_can_remote, spoon_mug_knife, spoon_mug_pot) | 2160×896 | Same far/near cluster-capture layout as `fig_range_bowl.png`, per object cluster | KEEP | Same family/size as verified file; not individually opened |
| fig_range_knife.png, fig_range_mug.png, fig_range_mug_hv.png, fig_range_pot.png, fig_range_remote.png, fig_range_spoon.png | 2160×896 | Same far/near layout, single object | KEEP | Same family/size as verified file; not individually opened |
| fig_results.png | 2295×1360 | 4-panel hardware trial telemetry (outcome, closure vs. grip levels, verified lift, success counts) | KEEP | Opened — clean, all four subplots legible |
| fig_results_11trials.png | 2295×1360 | Same layout, presumably an 11-trial superset/update of `fig_results.png` | KEEP | Same family/size; note two "results" figures exist — confirm before the report which is canonical to avoid using a stale one |
| fig_slide2_intent_regions.png | 2560×1440 | Intent-region slide graphic | KEEP | Reasonable resolution, not opened |
| fig_stage0_capture_knife_near.png | 640×480 | Raw knife capture | REGENERATE | Below 1200px floor |
| fig_stage3b_som_knife_hand.png, _knife_pick.png, _knife_put.png, _marks_knife.png | 640×480 (each) | Set-of-marks numbered overlay (0–4) on knife capture | KEEP (redundant) | All 4 files are **byte-identical** (same MD5) — one underlying SOM image reused across per-task filenames. Not a mislabel (SOM marks precede intent-specific part binding), but 3 of the 4 filenames are redundant copies |
| fig_stage3b_som_marks_mug.png, _mug_hand.png, _mug_move.png, _mug_pour.png | 640×480 (each) | SOM overlay on mug capture | KEEP (redundant) | 4 files byte-identical, same pattern as knife group |
| fig_stage3b_som_marks_remote.png, _remote_hand.png, _remote_power.png, _remote_put.png | 640×480 (each) | SOM overlay on remote capture | KEEP (redundant) | 4 files byte-identical |
| fig_stage3b_som_marks_spoon.png | 640×480 | SOM overlay on spoon capture | KEEP | Only one spoon variant present (no duplicate group) |
| fig_stage3c_point_crop_knife_head_near.png, _knife_hand.png, _knife_hand_rep2.png, _knife_hand_rep3.png, _knife_pick.png, _knife_put.png | 1024×251 (each) | Cropped pointing-overlay strip on knife | KEEP (redundant) | All 6 byte-identical — same crop reused across task/repeat filenames |
| fig_stage3c_point_crop_mug_head_near.png, _mug_hand.png, _mug_move.png, _mug_pour.png | 1024×614 (each) | Cropped pointing-overlay strip on mug | KEEP (redundant) | 4 files byte-identical |
| fig_stage3c_point_crop_remote_head_near.png, _remote_hand.png, _remote_power.png, _remote_put.png | 1024×310 (each) | Cropped pointing-overlay strip on remote | KEEP (redundant) | 4 files byte-identical |
| fig_stage4_knife_same_part_three_tasks.png | 3127×680 | 4-panel knife decomposition; captions read "handle → segment_near" for "pick up / hand me / put away the knife" | **DO NOT USE** | Opened — confirms the known reversed part-label bug (PCA sign issue in `part_adaptive.py`). The highlighted segment in each intent panel sits mid-blade, not on the handle end |
| fig_stage4_mug_evidence_gate.png | 2346×680 | Mug decomposition / evidence-gate panel (structurally identical to `fig_intent_mug_head_near.png`) | KEEP | Mug is not affected by the knife PCA-sign bug; content consistent with verified mug evidence-gate figure |
| fig_stage5_partmask_knife_blade_counterfactual.png | 2400×780 | "pick up the knife / part: 'blade'" → highlights `segment_far` | **DO NOT USE** | Opened — the highlighted region for "blade" sits near the handle end of the knife, not the blade tip. Confirms the reversed part-label bug |
| fig_stage5_partmask_knife_handle_pick.png | 2400×780 | "pick up the knife / part: 'handle'" → highlights `segment_near` | **DO NOT USE** | Opened — the highlighted region for "handle" sits over the blade (near the camera), not the actual green handle. Confirms the reversed part-label bug (companion to the file above) |
| fig_stage7_alignment_knife.png | 2240×1080 | Wrist-roll alignment of gripper closing axis to knife geometry (1° misalignment, elongated 270 mm/25 mm) | KEEP | Opened — legitimate, correctly titled wrist-roll figure, distinct content from the root-level duplicate group (§7) |
| methodology_slide11.png | 3200×1800 | Methodology slide | KEEP | Standard slide-deck resolution |
| NEW-HW_trial_history.png | 3200×1800 | Hardware trial history slide | KEEP | Standard slide-deck resolution |
| Slide10_NEW-A_part_decomposition.png | 3200×1800 | Part decomposition slide | KEEP | Byte-identical to `generated_assets/new_a/new_a_part_decomposition_slide.png` — intentional mirrored copy, not a bug |
| Slide12_NEW-B_identification_grid.png | 3200×1800 | Identification grid slide | KEEP | Byte-identical mirror of `generated_assets/new_b/new_b_identification_grid_slide.png` |
| slide13_perception.png, slide14_hardware.png, slide15_clutter.png | 3200×1800 | Perception / hardware / clutter slides | KEEP | Standard slide-deck resolution, not opened |
| Slide16_NEW-F_failure_register.png | 3200×1800 | Failure register slide | KEEP | Byte-identical mirror of `generated_assets/new_f/new_f_failure_register_slide.png` |
| Slide17a_NEW-H_three_layer_limit.png | 3200×1800 | Three-layer-limit slide | KEEP | Byte-identical mirror of `generated_assets/new_h/new_h_three_layer_limit_slide.png` |
| Slide17b_NEW-I_binding_fragility.png | 3200×1800 | Binding-fragility slide | KEEP | Byte-identical mirror of `generated_assets/new_i/new_i_binding_fragility_slide.png` |

## 2. `report_assets/figures_generated/` (2 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| fig_3_5_constraint_routing.png | 2520×1872 | Constraint routing diagram | KEEP | Good resolution, not opened |
| fig_7_1_base_placement.png | 2520×1300 | Base placement diagram | KEEP | Good resolution, not opened |

## 3. `report_assets/figures_live/` (2 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| langsam_overlay_knife_pick.png | 640×480 | LangSAM segmentation overlay, knife pick task | REGENERATE | Below 1200px floor — raw capture resolution |
| langsam_overlay_remote_power.png | 640×480 | LangSAM segmentation overlay, remote power task | REGENERATE | Below 1200px floor |

## 4. `report_assets/figure_audit/archive/` (4 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| new_a_slide_v1.png | 3200×1800 | Old draft of the part-decomposition slide | **DO NOT USE** | Byte size differs from current `generated_assets/new_a/new_a_part_decomposition_slide.png` — this is a superseded v1 draft sitting in an `archive/` folder. Use the current version instead |
| new_b_slide_v1.png | 3200×1800 | Old draft of the identification-grid slide | **DO NOT USE** | Superseded by current `new_b_identification_grid_slide.png` |
| new_d_slide_v1.png | 3200×1800 | Old draft of a method-disagreement slide | **DO NOT USE** | Superseded by current `new_d_method_disagreement_slide.png` |
| new_e_slide_v1.png | 3200×1800 | Old draft of an isolated-vs-cluttered slide | **DO NOT USE** | Superseded by current `new_e_isolated_vs_cluttered_slide.png` |

---

## 5. `figures/` (59 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| archive/fig_1_1_knife_version/fig_1_1_motivating_handover.png + .svg | 2490×712 | Old knife-based version of the motivating-handover figure | **DO NOT USE** | Explicitly in an `archive/` folder; superseded by the current `figures/out/fig_1_1_motivating_handover.png` |
| assets/knife_joseph_van_unsplash.jpg | 5472×3648 | Stock knife photo | KEEP | High-res; byte-identical duplicate of `figures/joseph-van-Fafvjw1n-ZA-unsplash.jpg` below — redundant copy, not an error |
| joseph-van-Fafvjw1n-ZA-unsplash.jpg | 5472×3648 | Same stock knife photo | KEEP | Duplicate of the file above; keep one, the other is redundant |
| knife.png | 1000×298 | Cropped/banner knife asset | REGENERATE-candidate | Long edge 1000px < 1200; likely fine as a small inline asset, but flag if used as a standalone figure |
| out/fig_1_1_motivating_handover.png/.svg | 2524×1116 | Motivating handover figure | KEEP | Current, non-archived version |
| out/fig_1_2_granularity_gap.png/.svg | 2457×1222 | Granularity-gap figure | KEEP | Good resolution |
| out/fig_2_1_evolution_grasp_synthesis.png/.svg | 2490×1182 | Grasp-synthesis evolution figure | KEEP | Good resolution |
| out/fig_2_1_grounding_chain.png/.svg | 2880×1436 | Grounding-chain figure | KEEP | Good resolution |
| out/fig_3_1_system_architecture.png/.svg | 2655×2535 | System architecture diagram | KEEP | Good resolution |
| out/fig_3_2_scope.png/.svg | 2642×1934 | Scope diagram | KEEP | Good resolution |
| out/fig_3_3_deployment.png/.svg | 2936×3434 | Deployment diagram | KEEP | Good resolution |
| out/fig_3_6_part_decomposition.png/.svg | 2497×285 | Part-decomposition strip figure | KEEP | Short height is by design (thin strip layout); also present as a differently-cropped `generated_assets/fig3_6/fig3_6_part_decomposition.png` (1880×1455) — not byte-identical, likely an earlier draft; treat this `figures/out/` copy as canonical |
| out/fig_3_7_base_placement.png/.svg | 2371×2803 | Base placement figure | KEEP | Good resolution |
| out/fig_3_8_pose_validation.png/.svg | 2423×1617 | Pose validation figure | KEEP | Good resolution |
| out/fig_5_1_mask_coverage.png/.svg | 2490×1262 | Mask coverage figure | KEEP | Good resolution |
| out/fig_5_2_requested_part_vs_mask.png/.svg | 2490×600 | Requested-part-vs-mask figure | KEEP | Short height by design (strip layout) |
| out/fig_5_3_evidence_floor.png/.svg | 2490×1342 | Evidence-floor figure | KEEP | Good resolution |
| out/fig_5_4_isolated_vs_cluttered.png/.svg | 2490×990 | Isolated-vs-cluttered figure | KEEP | Good resolution |
| out/fig_5_5_mug_fragmentation.png/.svg | 2490×1302 | Mug fragmentation figure | KEEP | Good resolution |
| out/fig_6_1_18cell_grid.png/.svg | 1682×1342 | 18-cell results grid | KEEP | Adequate resolution |
| out/fig_6_2_handover_ablation.png/.svg | 2490×1502 | Handover ablation figure | KEEP | Good resolution |
| out/fig_6_3_method_agreement.png/.svg | 2490×1422 | Method agreement figure | KEEP | Good resolution |
| out/fig_6_4_decomposition_recovery.png/.svg | 1437×1422 | Decomposition recovery figure | KEEP | Adequate resolution |
| out/fig_7_2_lift_verification.png/.svg | 2485×1046 | Lift verification figure | KEEP | Good resolution |
| out/_style_smoketest.png/.svg | 1202×782 | Style/theme smoke-test render | **DO NOT USE** | Internal styling test artifact, not a report figure |
| out/proofs/*.png (12 files: fig_1_1, fig_2_1, fig_3_1, fig_5_1..fig_5_5, fig_6_1..fig_6_4 "_proof") | 679×1126 each | Portrait-page proof renders (layout QA thumbnails, not the figures themselves) | **DO NOT USE** | Below 1200px floor and these are internal print-proof thumbnails (PDF-page aspect ratio), not intended as final report images — real figures are the corresponding `figures/out/*.png` files |

---

## 6. `generated_assets/` (36 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| fig01/fig01_acquisition.png ... fig13/fig13_pipeline_summary.png (13 files) | 3200×1800 each | Pipeline stage figures (acquisition, grounding, segmentation, point cloud, affordance reasoning, grasp candidates, filtering, motion planning, execution sequence, visual servo, successful experiment, failure analysis, pipeline summary) | KEEP | Consistent high resolution across the set; not individually opened, filenames correspond to `fig01_acquisition.py`...`fig13_pipeline_summary.py` generators |
| fig3_6/fig3_6_part_decomposition.png | 1880×1455 | Part decomposition figure (mug) | REGENERATE-candidate | Not byte-identical to the current `figures/out/fig_3_6_part_decomposition.png`; appears to be an earlier/alternate-crop draft — confirm which is canonical before using |
| new_a/new_a_part_decomposition.png + _slide.png | 3200×1800 each | Part decomposition (current, non-archived version) | KEEP | Slide variant is byte-identical to `report_assets/figures/Slide10_NEW-A_part_decomposition.png` (intentional mirror) |
| new_b/new_b_identification_grid.png + _slide.png | 3200×1800 each | Identification grid | KEEP | Slide variant mirrors `Slide12_NEW-B_identification_grid.png` |
| new_c/new_c_langsam_coverage.png + _slide.png | 3200×1800 each | LangSAM coverage figure | KEEP | Good resolution |
| new_d/new_d_method_disagreement.png + _slide.png | 3200×1800 each | Method disagreement figure | KEEP | Good resolution; supersedes archived `new_d_slide_v1.png` |
| new_e/new_e_isolated_vs_cluttered.png + _slide.png | 3200×1800 each | Isolated-vs-cluttered figure | KEEP | Good resolution; supersedes archived `new_e_slide_v1.png` |
| new_f/new_f_failure_register.png + _slide.png | 3200×1800 each | Failure register figure | KEEP | Slide variant mirrors `Slide16_NEW-F_failure_register.png` |
| new_g/new_g_clutter_scene_3d.png + _slide.png | 3200×1800 each | 3D clutter scene figure | KEEP | Good resolution |
| new_h/new_h_three_layer_limit.png + _slide.png | 3200×1800 each | Three-layer-limit figure | KEEP | Slide variant mirrors `Slide17a_NEW-H_three_layer_limit.png` |
| new_i/new_i_binding_fragility.png + _slide.png | 3200×1800 each | Binding fragility figure | KEEP | Slide variant mirrors `Slide17b_NEW-I_binding_fragility.png` |
| scene3d_test/cam_iso.png, cam_side.png, cam_top.png | 1000×720 each | 3D scene test renders from 3 camera angles | REGENERATE / low priority | Directory name ("test") and resolution both indicate a dev/test artifact rather than a finished figure; below 1200px floor |
| storyboard/storyboard.png | 960×540 | 13-cell pipeline storyboard/wireframe grid with per-cell claim/source/technique text | **DO NOT USE** | Opened — resolution is far too low for the amount of text packed into each of the 13 cells; the body text is already illegible at native size, let alone at print scale. This is a planning wireframe, not a finished figure |

---

## 7. `portfolio_figures/` (5 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| figure2_composite.png | 2236×1447 | Composite scene figure | KEEP | Good resolution |
| figure2_scene_overview.png | 1920×1080 | Scene overview | KEEP | Good resolution |
| figure2_view_front.png, figure2_view_side.png, figure2_view_top.png | 640×480 each | Individual camera-view captures (front/side/top) feeding the composite above | REGENERATE-candidate | Below 1200px floor; likely fine as source crops for the composite but too small to stand alone in the report |

## 8. `previews/` (3 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| cap_remote_head_far.png, cap_remote_head_near.png | 640×480 each | Raw remote-control captures | REGENERATE-candidate | Below 1200px floor; named/located as internal preview thumbnails, not report figures |
| _contact_sheet.png | 1120×448 | Thumbnail contact sheet of multiple captures | REGENERATE-candidate | Below 1200px floor; intended as an index/overview, illegible if used as a standalone figure |

## 9. `report_bundle_20260801_1611/` (top level, 4 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| final_center_debug.png | 880×660 | Overhead debug capture with grasp-target (green) vs detected-mug (red) markers on a mug | KEEP (below size floor) | Opened — clean and legible at native size despite being below the 1200px guideline; this is a native camera-resolution debug capture, not something that can be trivially re-rendered larger |
| grasp_px_probe.png | 880×660 | Debug capture, grasp pixel probe (same family as above) | KEEP (below size floor) | Same native resolution/purpose as `final_center_debug.png`; not individually opened |
| peek_view.png | 640×480 | Raw peek-view capture | REGENERATE-candidate | Below 1200px floor |
| place_run_map.png | 770×770 | Place-run map | REGENERATE-candidate | Below 1200px floor |

---

## 10. Root-level standalone files (14 files)

| File | Dimensions | Depicts | Verdict | Reason |
|---|---|---|---|---|
| battery_hand_me_the_mug_align.png, battery_lift_the_mug_using_its_handle_align.png, battery_move_the_mug_to_the_other_shelf_align.png, battery_pour_the_water_into_the_bowl_align.png, battery_stack_the_empty_mugs_align.png, battery_the_mug_just_came_out_of_the_microwave_-_align.png, fig_align_handle.png | 2240×1080 each | Filenames claim per-task wrist-roll alignment diagnostics for 6 distinct battery-test tasks, plus a generic `fig_align_handle.png` | **DO NOT USE** | All 7 files are **byte-for-byte identical** (same MD5), showing one single example (55° misalignment, mug handle, elongated 154 mm/28 mm). The battery-test generation script did not actually produce distinct alignment diagnostics per task — using these as-is would misrepresent 6 different task runs with one recycled image |
| fig_align_mug_handle.png | 2240×1080 | Wrist-roll alignment example, 73° misalignment, elongated 51 mm/12 mm part | KEEP | Opened — legitimate, correctly-described content |
| fig_compact.png | 2240×1080 | Same content as `fig_align_mug_handle.png` (byte-identical) | **DO NOT USE** | The image's own caption reads `shape class 'elongated'` — the filename "compact" directly contradicts the depicted content. Also a redundant duplicate of `fig_align_mug_handle.png` |
| fig_alignment_demo.png | 2240×1080 | Generic wrist-roll alignment demo, 2° misalignment, compact 124 mm/60 mm part | KEEP | Opened — legitimate content, correctly generic name |
| fig_wrist_roll_alignment.png | 2240×1080 | Same content as `fig_alignment_demo.png` (byte-identical) | REGENERATE (consolidate) | Exact duplicate under a second name; keep one canonical file to avoid ambiguity, not an accuracy problem |
| fig_part_mask.png | 2400×780 | 3-panel: capture / whole-object mug mask / part mask "handle"→lateral_protrusion (245 px, 8% of object) | KEEP | Opened — **this file is correctly labelled and correctly shows a genuine part-mask figure**, contrary to the reported concern. It is NOT the same image as `fig_wrist_roll_alignment.png` (different dimensions, different hash, different content) |
| fig_part_mask_isolated.png | 2400×780 | Same 3-panel layout, "isolated" scenario where no usable part mask is found ("no usable part mask") | KEEP | Opened — also correctly shows a legitimate part-mask figure (a documented failure case), not mislabelled |
| motivation_slide.svg | 1152×648pt | Motivation slide, vector | KEEP | Not opened; SVG is resolution-independent |

---

## Summary

**Total images audited: 198**

| Verdict | Count |
|---|---|
| KEEP | 158 |
| REGENERATE / REGENERATE-candidate | 22 |
| DO NOT USE | 18 |

*(Counts include every individual file, e.g. each member of a duplicate/byte-identical group is counted separately even where only one copy is needed.)*

### Highest-priority DO NOT USE
1. **`fig_stage4_knife_same_part_three_tasks.png`, `fig_stage5_partmask_knife_blade_counterfactual.png`, `fig_stage5_partmask_knife_handle_pick.png`** — confirmed reversed knife part labels (PCA sign bug in `part_adaptive.py`): "blade" highlights near the handle end, "handle" highlights the blade. Do not use any knife part-label figure without re-verifying against the fixed pipeline.
2. **`battery_*_align.png` (6 files) + `fig_align_handle.png`** — confirmed byte-identical; the battery-test alignment diagnostics were never actually regenerated per task. Presenting these as 6 distinct results would be misleading.
3. **`report_assets/figures/figdeck_naming_ablation.png`** — confirmed blank canvas, no content rendered.
4. **`generated_assets/storyboard/storyboard.png`** — confirmed illegible at native resolution (960×540 with dense per-cell text).
5. **`fig_compact.png`** — filename says "compact," content is explicitly labelled "shape class 'elongated'"; also a duplicate of `fig_align_mug_handle.png`.
6. **`report_assets/figure_audit/archive/*_slide_v1.png` (4 files)**, **`figures/archive/fig_1_1_knife_version/*`**, **`figures/out/_style_smoketest.*`**, **`figures/out/proofs/*` (12 files)** — archived drafts, style smoketests, and internal proof thumbnails; all superseded by or auxiliary to the real report figures.

### Highest-priority REGENERATE
- Most `640×480` raw captures across `previews/`, `report_bundle_20260801_1611/`, `report_assets/figures_live/`, and `portfolio_figures/` (individual views) sit well under the 1200px long-edge floor.
- `fig_wrist_roll_alignment.png` should be consolidated with its byte-identical twin `fig_alignment_demo.png`.
- `generated_assets/fig3_6/fig3_6_part_decomposition.png` is a non-canonical draft that differs from the current `figures/out/fig_3_6_part_decomposition.png` — confirm which is intended before use.
