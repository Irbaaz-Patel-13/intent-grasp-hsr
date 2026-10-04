# Processing Log

Generated 2026-08-09T16:34:01 by build_manifests.py.

| Figure | Processing script | Real source file(s) |
|---|---|---|
| NEW-A | new_a_part_decomposition.py | captures_pairs_2/cap_mug_head_near.npz, bc_mug.log, ax4_mug.log, q6_intent_mug.log, part_adaptive.py:520-534 (evidence gate) |
| NEW-B | new_b_identification_grid.py (load_grid()) | vlm_stability.csv |
| NEW-D | new_d_method_disagreement.py (load_grid(), verify_som_hash_groups()) | report_assets/PART_NAMING_ABLATION.csv, report_assets/figures/fig_stage3b_som_knife_pick.png, report_assets/figures/fig_stage3c_point_knife_pick.png, report_assets/figures/fig_stage0_capture_knife_near.png |
| NEW-E | new_e_isolated_vs_cluttered.py (load_rows()) | batch_scene_analysis.csv |
| NEW-F | new_f_failure_register.py (load_rows()) | report_assets/FAILURE_REGISTER.csv |
| NEW-H | new_h_three_layer_limit.py | captures_pairs_2/cap_mug_head_near.npz (reused from NEW-A, same physical mug), q6_intent_mug.log (left column: reasoning+perception), Experiment_Logs/2026-08-07/constraints.json (right column: reasoning, real anchor trial), part_adaptive.py:520-524 (evidence gate), trials.csv trial 9 (left column kinematics, real z_rise_m=0.1420) |
| NEW-HW | new_hw_trial_history.py (load_trials()) | trials.csv |
| NEW-I | new_i_binding_fragility.py (run_both_states()) | report_assets/PERCEPTION_EVIDENCE.md (Part ANr3/AW1/AW2), part_adaptive.py.before_orphan_fix (real backup file, broken RELATION_HINTS dict), part_adaptive.py (current, fixed RELATION_HINTS dict), captures_pairs_2/cap_remote_head_near.npz |

## Audit steps performed this pass (see contradictions.md for details)

1. Traced Figure 3's source capture and compared against NEW-A/NEW-H's source capture by MD5 and
   direct visual comparison -- confirmed same physical object, different capture pass.
2. Verified NEW-A's PASS/LOW/NOISE labels against the real evidence-gate code
   (part_adaptive.py:520-524), not against memory of expected values.
3. Verified NEW-D's disagreement count is computed from real CSV rows at manifest-build time, not
   assumed to be "0 agree".
4. Verified trials.csv trial numbering (trial 8 gap) and computed (not typed) the trials 9-12
   z-rise spread.
5. Checked FAILURE_REGISTER.csv's real row count (17) against the "13" figure referenced in the
   request -- no such figure exists in this repo's own generated outputs.
