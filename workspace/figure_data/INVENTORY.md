# AffordGrasp Figure Data Inventory

Auto-generated inventory of data files, dissertation-relevant images, and duplicate-basename conflicts across the repository. Generated 2026-08-18.

- Data files scanned: 1603 (67 are `.csv`, of which 4 flagged malformed)
- Qualifying images (report_assets/figures/captures/run_*//runs/): 196
- Duplicate basenames considered (csv/json/md, after filtering noise): 49

---

## 1. Data files

One entry per file matched by the pre-built list of `.csv/.json/.md/.npz/.npy/.yaml/.yml` files (excludes `.git`, `.venv`, `__pycache__`, `node_modules` anywhere in the tree). Grouped by top-level directory. For `.csv` files the verbatim header row and data-row count (via Python `csv.reader`, header excluded) are given; malformed CSVs are flagged inline.

### (repo root) (63 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| _organize_manifest.md | 6575 | 2026-07-19 |  |  |
| _organize_plan.md | 6534 | 2026-07-19 |  |  |
| batch_bowl_head_far.json | 503 | 2026-08-02 |  |  |
| batch_cluster_mug_cokecan_pot.json | 608 | 2026-07-26 |  |  |
| batch_cluster_mug_remote_pot.json | 632 | 2026-07-26 |  |  |
| batch_metal_spoon.json | 597 | 2026-07-26 |  |  |
| batch_pot_with_handle_and_lid.json | 617 | 2026-07-26 |  |  |
| batch_scene_analysis.csv | 1324 | 2026-07-26 | `scene,target_object,target_part,keep_clear,motion,stability,thermal,shape,linearity,long_mm,minor_mm,over_aperture,roll_apply,roll_deg,n_ok,width_med,force,close_z,lift,tilt,aff_z,plane_z,error,instruction,roll_reason,obj_pts,geom_error` | 5 |
| batch_scene_analysis.md | 1693 | 2026-07-26 |  |  |
| batch_TV_remote.json | 622 | 2026-07-26 |  |  |
| cap_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| cap_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| cgn_candidate_analysis.md | 405 | 2026-07-23 |  |  |
| cgn_metric_correction.md | 1224 | 2026-07-23 |  |  |
| close_params.csv | 2067 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| close_params_knife_hand.csv | 1209 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 11 |
| close_params_knife_pick.csv | 1304 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 13 |
| close_params_knife_put.csv | 970 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 9 |
| close_params_move.csv | 1992 | 2026-07-22 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| close_params_pour.csv | 2017 | 2026-07-22 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| close_params_remote_hand.csv | 2708 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| close_params_remote_power.csv | 2628 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| close_params_remote_put.csv | 2594 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| closure_differentiation.md | 6775 | 2026-07-22 |  |  |
| CODEBASE_GUIDE.md | 94200 | 2026-08-03 |  |  |
| components.csv | 168 | 2026-08-18 | `name,width_mm,pixels,recovered,note` | 3 — MALFORMED — see note (field-count mismatch on 1 line(s)) |
| condA_results.json | 3519 | 2026-08-03 |  |  |
| constraints.json | 298 | 2026-08-07 |  |  |
| constraints_knife_hand.json | 283 | 2026-08-02 |  |  |
| constraints_knife_pick.json | 280 | 2026-08-02 |  |  |
| constraints_knife_put.json | 296 | 2026-08-02 |  |  |
| constraints_move.json | 324 | 2026-07-22 |  |  |
| constraints_pour.json | 421 | 2026-07-22 |  |  |
| constraints_remote_hand.json | 301 | 2026-08-02 |  |  |
| constraints_remote_power.json | 409 | 2026-08-02 |  |  |
| constraints_remote_put.json | 302 | 2026-08-02 |  |  |
| corrections.csv | 280 | 2026-08-18 | `claim_as_reported,re_measured_finding,what_changed` | 9 |
| DEMO_RUNBOOK.md | 11333 | 2026-08-09 |  |  |
| fused_cloud.npz | 5700866 | 2026-08-07 |  |  |
| grasps_out.npz | 1624087 | 2026-08-07 |  |  |
| grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| gripper_gap_map.csv | 340 | 2026-07-14 | `cmd_angle,motor_angle,gap_m` | 9 |
| head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| head_capture_real_bowl.npz | 2152680 | 2026-08-02 |  |  |
| head_capture_real_knife.npz | 2152680 | 2026-08-02 |  |  |
| head_capture_real_pot.npz | 2152680 | 2026-08-02 |  |  |
| mug_condA_parts.json | 987 | 2026-08-03 |  |  |
| multiview.npz | 2151910 | 2026-08-07 |  |  |
| NOTES_NEXT_SESSION.md | 4333 | 2026-07-16 |  |  |
| range_analysis.csv | 1626 | 2026-08-02 | `object,far_depth,near_depth,far_obj_pts,near_obj_pts,far_shape,near_shape,far_fine_pts,near_fine_pts,far_fine_mm,near_fine_mm,far_evidence,near_evidence` | 16 |
| range_analysis.md | 2326 | 2026-08-02 |  |  |
| README.md | 8883 | 2026-05-14 |  |  |
| skills-lock.json | 272 | 2026-08-04 |  |  |
| stability_mechanism.md | 1890 | 2026-07-26 |  |  |
| trials.csv | 2518 | 2026-08-07 | `timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note` | 12 |
| trials_0728.csv | 1491 | 2026-08-02 | `timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note` | 7 |
| vlm_grid_handover_v2_raw.json | 7710 | 2026-07-15 |  |  |
| vlm_grid_raw.json | 23616 | 2026-07-15 |  |  |
| vlm_identify.csv | 6339 | 2026-07-26 | `scene,kind,instruction,present,expected,required_type,picked,conf,correct,part,keep_clear,motion,stability,thermal,rationale,error` | 13 |
| vlm_identify.md | 7335 | 2026-07-26 |  |  |
| vlm_identify_raw.json | 19248 | 2026-07-26 |  |  |
| vlm_stability.csv | 6443 | 2026-07-26 | `pass_no,scene,instruction,expected,required_type,picked,part,keep_clear,correct` | 65 |
| vlm_stability.md | 2942 | 2026-07-26 |  |  |

### .claude/ (2 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| .claude/settings.local.json | 17673 | 2026-08-16 |  |  |
| .claude/skills/find-skills/SKILL.md | 5472 | 2026-08-04 |  |  |

### .superpowers/ (25 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/progress.md | 10872 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-1-brief.md | 12109 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-1-report.md | 4206 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-2-brief.md | 9728 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-2-report.md | 7358 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-3-brief.md | 9805 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-3-report.md | 4966 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-4-brief.md | 8197 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-4-report.md | 10563 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-5-brief.md | 5761 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-5-report.md | 4197 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-6-brief.md | 5538 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-6-report.md | 6470 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-7-brief.md | 12405 | 2026-08-08 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-7-report.md | 20675 | 2026-08-07 |  |  |
| .superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-finalreview-fixwave-report.md | 9479 | 2026-08-08 |  |  |
| .superpowers/sdd/final-review-fix-report-2.md | 6776 | 2026-07-14 |  |  |
| .superpowers/sdd/final-review-fix-report.md | 8150 | 2026-07-13 |  |  |
| .superpowers/sdd/progress.md | 6408 | 2026-07-14 |  |  |
| .superpowers/sdd/task-1-brief.md | 14460 | 2026-07-13 |  |  |
| .superpowers/sdd/task-1-report.md | 8462 | 2026-07-13 |  |  |
| .superpowers/sdd/task-2-brief.md | 12915 | 2026-07-13 |  |  |
| .superpowers/sdd/task-2-report.md | 20348 | 2026-07-13 |  |  |
| .superpowers/sdd/task-3-brief.md | 7447 | 2026-07-13 |  |  |
| .superpowers/sdd/task-3-report.md | 10378 | 2026-07-13 |  |  |

### .vscode/ (1 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| .vscode/settings.json | 47 | 2026-03-05 |  |  |

### archive/ (385 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| archive/backups/HSR_logs_20260714_183749/fused_cloud.npz | 5830394 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/grasps_out.npz | 1664723 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/grasps_plain.npz | 6026 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/gripper_gap_map.csv | 340 | 2026-07-19 | `cmd_angle,motor_angle,gap_m` | 9 |
| archive/backups/HSR_logs_20260714_183749/hand_cam_stow_frame.npz | 922124 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/hand_view.npz | 923106 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/hand_view_real.npz | 924140 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/hand_view_real_grasp1_center_fail.npz | 924140 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/head_capture.npz | 2151620 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/head_capture_real.npz | 2152680 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/multiview.npz | 6453950 | 2026-07-19 |  |  |
| archive/backups/HSR_logs_20260714_183749/place_run.csv | 1932 | 2026-07-19 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| archive/backups/HSR_logs_20260714_183749/regions.npz | 1224 | 2026-07-19 |  |  |
| archive/backups/results_home_0713/fused_cloud.npz | 5851538 | 2026-07-12 |  |  |
| archive/backups/results_home_0713/grasps_plain.npz | 6026 | 2026-07-12 |  |  |
| archive/backups/results_home_0713/hand_view_real.npz | 924140 | 2026-07-12 |  |  |
| archive/backups/results_home_0713/part_decomposition_table.md | 431 | 2026-07-13 |  |  |
| archive/backups/results_home_0713/part_grasp.npz | 36329 | 2026-07-13 |  |  |
| archive/backups/results_home_0713/part_grasp_handle.npz | 96001 | 2026-07-13 |  |  |
| archive/backups/results_home_0713/part_grasp_pickup.npz | 50781 | 2026-07-12 |  |  |
| archive/backups/results_home_0713/part_grasp_pour.npz | 50781 | 2026-07-12 |  |  |
| archive/backups/results_home_0713/part_grasp_report_pick_up_the_mug.npz | 36329 | 2026-07-13 |  |  |
| archive/backups/results_home_0713/part_grasp_report_pick_up_the_mug_by_the_handle.npz | 36329 | 2026-07-13 |  |  |
| archive/backups/results_home_0713/part_grasp_report_pour_the_water_out_of_the_mug.npz | 28713 | 2026-07-13 |  |  |
| archive/backups/ws_backup_0711/NOTES_NEXT_SESSION.md | 1094 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_183028.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_183356.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_183708.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_184028.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_184348.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_bottle_20260608_184704.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_182915.npz | 34916 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_183253.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_183609.npz | 5916 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_183925.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_184242.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_hammer_20260608_184558.npz | 41716 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_mug.npz | 41704 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_mug_20260608_183137.npz | 41704 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_mug_20260608_184132.npz | 41704 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_unknown_20260610_172425.npz | 41720 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_unknown_20260610_175305.npz | 41720 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_unknown_20260611_093009.npz | 41720 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_unknown_20260616_125811.npz | 41720 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_wine_glass_20260608_182802.npz | 41732 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_wine_glass_20260608_183504.npz | 41732 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_wine_glass_20260608_183817.npz | 41732 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/cgn_candidates/candidates_wine_glass_20260608_184456.npz | 20132 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag/diag_bottle_diag.json | 7217 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag/diag_hammer_diag.json | 7209 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag/diag_mug_diag.json | 7249 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag/DIAGNOSTIC_REPORT.md | 15263 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag2_bottle_diag.json | 7341 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag2_hammer_diag.json | 7351 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/diag2_mug_diag.json | 7338 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/motion_trace2_mug_diag.json | 76649 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/MOTION_TRACE2_REPORT.md | 7214 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/motion_trace3_mug_diag.json | 79888 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/MOTION_TRACE3_REPORT.md | 7014 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/motion_trace_mug_diag.json | 73183 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/MOTION_TRACE_REPORT.md | 9194 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/POST_FIX_REPORT.md | 6564 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/post_reach_filter_bottle_diag.json | 79785 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/post_reach_filter_hammer_diag.json | 79694 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/POST_REACH_FILTER_REPORT.md | 9977 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS.md | 9449 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS_V2.md | 6242 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS_V3.md | 8918 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/fused_cloud.npz | 6322178 | 2026-07-06 |  |  |
| archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/grasps_plain.npz | 6026 | 2026-07-06 |  |  |
| archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/head_capture_real.npz | 2152680 | 2026-07-06 |  |  |
| archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/place_run.csv | 2422 | 2026-07-06 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| archive/backups/ws_backup_0711/results/run_0710_1447/grasps_plain.npz | 6026 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1447/hand_view_real.npz | 924140 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1447/place_run.csv | 2008 | 2026-07-10 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/fused_cloud.npz | 5784482 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/grasps_plain.npz | 6026 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/hand_view_real.npz | 924140 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/hand_view_real_grasp1_center_fail.npz | 924140 | 2026-07-10 |  |  |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/place_run.csv | 1484 | 2026-07-10 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/fused_cloud.npz | 5851538 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/grasps_plain.npz | 6026 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/hand_view_real.npz | 924140 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/head_capture_real.npz | 2152680 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/NOTES_NEXT_SESSION.md | 1094 | 2026-07-12 |  |  |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/place_run.csv | 2251 | 2026-07-12 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/pipeline_results.json | 3053 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_150555_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_151412_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_151833_mug/pipeline_results.json | 3069 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_151833_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_151833_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_152831_mug/pipeline_results.json | 3067 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_152831_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_152831_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153131_mug/pipeline_results.json | 3066 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153131_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153131_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153324_mug/pipeline_results.json | 3064 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153324_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153324_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153407_mug/pipeline_results.json | 3059 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153407_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260301_153407_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202801_hammer/pipeline_results.json | 3068 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202801_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202801_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202822_scissors/pipeline_results.json | 3083 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202822_scissors/reasoning_result.json | 136 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202822_scissors/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202908_scissors/pipeline_results.json | 3087 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202908_scissors/reasoning_result.json | 136 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_202908_scissors/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204333_mug/reasoning_result.json | 127 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204333_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204458_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204726_mug/pipeline_results.json | 3054 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204726_mug/reasoning_result.json | 122 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204726_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204850_hammer/pipeline_results.json | 3097 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204850_hammer/reasoning_result.json | 148 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204850_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204942_hammer/pipeline_results.json | 3105 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204942_hammer/reasoning_result.json | 155 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_204942_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205507_mug/pipeline_results.json | 3051 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205507_mug/reasoning_result.json | 117 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205507_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205551_mug/pipeline_results.json | 3063 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205551_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260303_205551_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_053620_hammer/pipeline_results.json | 3092 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_053620_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_053620_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_053713_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_053713_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_061906_hammer/reasoning_result.json | 134 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_061906_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_123300_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_123300_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124212_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124212_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124358_mug/pipeline_results.json | 594 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124358_mug/reasoning_result.json | 118 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124358_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124810_hammer/pipeline_results.json | 606 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124810_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_124810_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125146_hammer/pipeline_results.json | 605 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125146_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125146_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125408_hammer/pipeline_results.json | 606 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125408_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_125408_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130322_hammer/pipeline_results.json | 605 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130322_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130322_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130604_hammer/pipeline_results.json | 607 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130604_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130604_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130821_hammer/pipeline_results.json | 607 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130821_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130821_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130939_hammer/pipeline_results.json | 606 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130939_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_130939_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131200_hammer/pipeline_results.json | 1251 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131200_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131200_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131547_hammer/pipeline_results.json | 3082 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131547_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131547_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131735_hammer/pipeline_results.json | 1250 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131735_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131735_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131938_hammer/pipeline_results.json | 606 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131938_hammer/reasoning_result.json | 132 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_131938_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132204_hammer/pipeline_results.json | 3098 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132204_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132204_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132329_hammer/pipeline_results.json | 3093 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132329_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132329_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132432_hammer/pipeline_results.json | 3098 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132432_hammer/reasoning_result.json | 132 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132432_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132608_mug/pipeline_results.json | 3073 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132608_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_132608_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_133550_mug/pipeline_results.json | 3078 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_133550_mug/reasoning_result.json | 118 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_133550_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_133750_mug/reasoning_result.json | 118 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_133750_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134014_mug/pipeline_results.json | 3072 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134014_mug/reasoning_result.json | 118 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134014_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134100_mug/pipeline_results.json | 3064 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134100_mug/reasoning_result.json | 118 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134100_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134201_mug/pipeline_results.json | 3066 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134201_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134201_mug/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134459_hammer/pipeline_results.json | 3103 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134459_hammer/reasoning_result.json | 134 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134459_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134953_hammer/pipeline_results.json | 3087 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134953_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_134953_hammer/scene_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/pipeline_results.json | 3104 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/reasoning_result.json | 132 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/pipeline_results.json | 3117 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/reasoning_result.json | 148 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/pipeline_results.json | 3122 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/reasoning_result.json | 150 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/pipeline_results.json | 3107 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/pipeline_results.json | 3119 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/pipeline_results.json | 3135 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/pipeline_results.json | 3120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/pipeline_results.json | 2664 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/reasoning_result.json | 146 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/pipeline_results.json | 3109 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/pipeline_results.json | 1283 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/pipeline_results.json | 3092 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/reasoning_result.json | 128 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/pipeline_results.json | 3089 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/pipeline_results.json | 2628 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/pipeline_results.json | 607 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/reasoning_result.json | 132 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/pipeline_results.json | 3087 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/reasoning_result.json | 139 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/pipeline_results.json | 609 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/pipeline_results.json | 602 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/reasoning_result.json | 123 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/pipeline_results.json | 2170 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/pipeline_results.json | 3100 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/reasoning_result.json | 136 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/pipeline_results.json | 3074 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/pipeline_results.json | 3096 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/pipeline_results.json | 3086 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/reasoning_result.json | 139 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/pipeline_results.json | 599 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/reasoning_result.json | 121 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/pipeline_results.json | 605 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/pipeline_results.json | 631 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/reasoning_result.json | 154 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/pipeline_results.json | 3075 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/reasoning_result.json | 121 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/pipeline_results.json | 606 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/pipeline_results.json | 625 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/reasoning_result.json | 147 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/pipeline_results.json | 2622 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/reasoning_result.json | 120 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/pipeline_results.json | 1251 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/reasoning_result.json | 131 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/pipeline_results.json | 630 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/reasoning_result.json | 154 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/pipeline_results.json | 600 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/reasoning_result.json | 123 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/pipeline_results.json | 2178 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/reasoning_result.json | 135 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/pipeline_results.json | 1274 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/reasoning_result.json | 154 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/scene_front_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/scene_side_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/scene_top_intrinsics.npy | 200 | 2026-06-23 |  |  |
| archive/backups/ws_backup_0711/RUNBOOK.md | 1846 | 2026-07-06 |  |  |

### Backups/ (471 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| Backups/2026-08-07/Afford-Grasp/.claude/settings.local.json | 12577 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/.vscode/settings.json | 47 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_cluster_mug_cokecan.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_cluster_mug_cokecan_pot.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_cluster_mug_remote_pot.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_coke_can.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_dishwash_bottle.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_metal_spoon.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_pot_with_handle_and_lid.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/cap_TV_remote.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_obj/cap_mug_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_obj/cap_mug_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_obj/capture_log.json | 1818 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_bowl_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_bowl_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_bowl_knife_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_bowl_knife_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_can_pot_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_can_pot_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_can_remote_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_mug_can_remote_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_pot_mug_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_pot_mug_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_remote_knife_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_remote_knife_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_bowl_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_bowl_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_can_remote_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_can_remote_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_mug_knife_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_mug_knife_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_mug_pot_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_cluster_spoon_mug_pot_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_knife_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_knife_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_mug_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_mug_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_mug_hv_hand.npz | 922504 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_mug_hv_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_mug_hv_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_pot_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_pot_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_remote_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_remote_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_spoon_head_far.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/captures_pairs/cap_spoon_head_near.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/close_params.csv | 2067 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/close_params_move.csv | 1992 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/close_params_pour.csv | 2017 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/checkpoints/contact_graspnet/config.yaml | 3637 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/contact_graspnet_env.yml | 8753 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/contact_graspnet_pytorch/config.yaml | 3635 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/docs/acronym_setup.md | 3039 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/docs/generate_scenes.md | 882 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/gripper_control_points/panda.npy | 448 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/gripper_control_points/panda_gripper_coords.yml | 424 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/gripper_models/panda_pc.npy | 817460 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/Pointnet_Pointnet2_pytorch/README.md | 7982 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/README.md | 5901 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/0.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/1.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/10.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/11.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/12.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/13.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/2.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/3.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/4.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/5.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/6.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/7.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/8.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/test_data/9.npy | 10138333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/fused_cloud.npz | 5700866 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/gripper_gap_map.csv | 340 | 2026-08-07 | `cmd_angle,motor_angle,gap_m` | 9 |
| Backups/2026-08-07/Afford-Grasp/hand_view_real.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/hsr_meshes/README.md | 524 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/NOTES_NEXT_SESSION.md | 4333 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/place_run.csv | 2106 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/README.md | 8883 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_183028.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_183356.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_183708.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_184028.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_184348.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_bottle_20260608_184704.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_182915.npz | 34916 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_183253.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_183609.npz | 5916 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_183925.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_184242.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_hammer_20260608_184558.npz | 41716 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_mug.npz | 41704 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_mug_20260608_183137.npz | 41704 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_mug_20260608_184132.npz | 41704 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_unknown_20260610_172425.npz | 41720 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_unknown_20260610_175305.npz | 41720 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_unknown_20260611_093009.npz | 41720 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_unknown_20260616_125811.npz | 41720 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_wine_glass_20260608_182802.npz | 41732 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_wine_glass_20260608_183504.npz | 41732 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_wine_glass_20260608_183817.npz | 41732 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/cgn_candidates/candidates_wine_glass_20260608_184456.npz | 20132 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag/diag_bottle_diag.json | 7217 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag/diag_hammer_diag.json | 7209 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag/diag_mug_diag.json | 7249 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag/DIAGNOSTIC_REPORT.md | 15263 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag2_bottle_diag.json | 7341 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag2_hammer_diag.json | 7351 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/diag2_mug_diag.json | 7338 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/motion_trace2_mug_diag.json | 76649 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE2_REPORT.md | 7214 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/motion_trace3_mug_diag.json | 79888 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE3_REPORT.md | 7014 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/motion_trace_mug_diag.json | 73183 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE_REPORT.md | 9194 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/POST_FIX_REPORT.md | 6564 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/post_reach_filter_bottle_diag.json | 79785 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/post_reach_filter_hammer_diag.json | 79694 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/POST_REACH_FILTER_REPORT.md | 9977 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS.md | 9449 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS_V2.md | 6242 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS_V3.md | 8918 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/fused_cloud.npz | 6322178 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/place_run.csv | 2422 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/hand_view_real.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/place_run.csv | 2008 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/fused_cloud.npz | 5784482 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/hand_view_real.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/hand_view_real_grasp1_center_fail.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/place_run.csv | 1484 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/fused_cloud.npz | 5851538 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/hand_view_real.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/NOTES_NEXT_SESSION.md | 1094 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/place_run.csv | 2251 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/hand_view_real.npz | 924140 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/place_run.csv | 1932 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/fused_cloud.npz | 6021938 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/gripper_gap_map.csv | 340 | 2026-08-07 | `cmd_angle,motor_angle,gap_m` | 9 |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/place_run.csv | 2394 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/close_params.csv | 1987 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/fused_cloud.npz | 5719994 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/gripper_gap_map.csv | 340 | 2026-08-07 | `cmd_angle,motor_angle,gap_m` | 9 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/place_run.csv | 2420 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/close_params_move.csv | 1992 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/close_params_pour.csv | 2017 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/fused_cloud.npz | 5715482 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/place_run.csv | 2233 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/close_params.csv | 1985 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/fused_cloud.npz | 5813450 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/place_run.csv | 2412 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/trials.csv | 882 | 2026-08-07 | `timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note` | 4 |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150326_mug/pipeline_results.json | 3053 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150326_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150326_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150555_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151412_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151833_mug/pipeline_results.json | 3069 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151833_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151833_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_152831_mug/pipeline_results.json | 3067 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_152831_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_152831_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153131_mug/pipeline_results.json | 3066 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153131_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153131_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153324_mug/pipeline_results.json | 3064 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153324_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153324_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153407_mug/pipeline_results.json | 3059 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153407_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153407_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202801_hammer/pipeline_results.json | 3068 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202801_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202801_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202822_scissors/pipeline_results.json | 3083 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202822_scissors/reasoning_result.json | 136 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202822_scissors/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202908_scissors/pipeline_results.json | 3087 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202908_scissors/reasoning_result.json | 136 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202908_scissors/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204333_mug/reasoning_result.json | 127 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204333_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204458_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204726_mug/pipeline_results.json | 3054 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204726_mug/reasoning_result.json | 122 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204726_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204850_hammer/pipeline_results.json | 3097 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204850_hammer/reasoning_result.json | 148 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204850_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204942_hammer/pipeline_results.json | 3105 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204942_hammer/reasoning_result.json | 155 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204942_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205507_mug/pipeline_results.json | 3051 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205507_mug/reasoning_result.json | 117 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205507_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205551_mug/pipeline_results.json | 3063 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205551_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205551_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053620_hammer/pipeline_results.json | 3092 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053620_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053620_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053713_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053713_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_061906_hammer/reasoning_result.json | 134 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_061906_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_123300_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_123300_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124212_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124212_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124358_mug/pipeline_results.json | 594 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124358_mug/reasoning_result.json | 118 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124358_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124810_hammer/pipeline_results.json | 606 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124810_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124810_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125146_hammer/pipeline_results.json | 605 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125146_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125146_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125408_hammer/pipeline_results.json | 606 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125408_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125408_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130322_hammer/pipeline_results.json | 605 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130322_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130322_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130604_hammer/pipeline_results.json | 607 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130604_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130604_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130821_hammer/pipeline_results.json | 607 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130821_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130821_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130939_hammer/pipeline_results.json | 606 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130939_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130939_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131200_hammer/pipeline_results.json | 1251 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131200_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131200_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131547_hammer/pipeline_results.json | 3082 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131547_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131547_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131735_hammer/pipeline_results.json | 1250 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131735_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131735_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131938_hammer/pipeline_results.json | 606 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131938_hammer/reasoning_result.json | 132 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131938_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132204_hammer/pipeline_results.json | 3098 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132204_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132204_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132329_hammer/pipeline_results.json | 3093 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132329_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132329_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132432_hammer/pipeline_results.json | 3098 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132432_hammer/reasoning_result.json | 132 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132432_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132608_mug/pipeline_results.json | 3073 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132608_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132608_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133550_mug/pipeline_results.json | 3078 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133550_mug/reasoning_result.json | 118 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133550_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133750_mug/reasoning_result.json | 118 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133750_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134014_mug/pipeline_results.json | 3072 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134014_mug/reasoning_result.json | 118 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134014_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134100_mug/pipeline_results.json | 3064 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134100_mug/reasoning_result.json | 118 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134100_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134201_mug/pipeline_results.json | 3066 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134201_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134201_mug/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134459_hammer/pipeline_results.json | 3103 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134459_hammer/reasoning_result.json | 134 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134459_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134953_hammer/pipeline_results.json | 3087 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134953_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134953_hammer/scene_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/pipeline_results.json | 3104 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/reasoning_result.json | 132 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/pipeline_results.json | 3117 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/reasoning_result.json | 148 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/pipeline_results.json | 3122 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/reasoning_result.json | 150 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/pipeline_results.json | 3107 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/pipeline_results.json | 3119 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/pipeline_results.json | 3135 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/pipeline_results.json | 3120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/pipeline_results.json | 2664 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/reasoning_result.json | 146 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/pipeline_results.json | 3109 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/pipeline_results.json | 1283 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/pipeline_results.json | 3092 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/reasoning_result.json | 128 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/pipeline_results.json | 3089 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/pipeline_results.json | 2628 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/pipeline_results.json | 607 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/reasoning_result.json | 132 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/pipeline_results.json | 3087 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/reasoning_result.json | 139 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/pipeline_results.json | 609 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/pipeline_results.json | 602 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/reasoning_result.json | 123 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/pipeline_results.json | 2170 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/pipeline_results.json | 3100 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/reasoning_result.json | 136 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/pipeline_results.json | 3074 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/pipeline_results.json | 3096 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/pipeline_results.json | 3086 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/reasoning_result.json | 139 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/pipeline_results.json | 599 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/reasoning_result.json | 121 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/pipeline_results.json | 605 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/pipeline_results.json | 631 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/reasoning_result.json | 154 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/pipeline_results.json | 3075 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/reasoning_result.json | 121 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/pipeline_results.json | 606 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/pipeline_results.json | 625 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/reasoning_result.json | 147 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/pipeline_results.json | 2622 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/reasoning_result.json | 120 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/pipeline_results.json | 1251 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/reasoning_result.json | 131 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/pipeline_results.json | 630 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/reasoning_result.json | 154 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/pipeline_results.json | 600 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/reasoning_result.json | 123 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/pipeline_results.json | 2178 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/reasoning_result.json | 135 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/pipeline_results.json | 1274 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/reasoning_result.json | 154 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/scene_front_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/scene_side_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/scene_top_intrinsics.npy | 200 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/RUNBOOK.md | 1846 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/trials.csv | 2518 | 2026-08-07 | `timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note` | 12 |
| Backups/2026-08-07/Afford-Grasp/YCB_Dataset/README.md | 1826 | 2026-08-07 |  |  |
| Backups/2026-08-07/Afford-Grasp/YCB_Dataset/scripts/ycb_mass.json | 1886 | 2026-08-07 |  |  |

### batch_out/ (26 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| batch_out/bowl_head_far_close_params.csv | 1610 | 2026-08-02 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/bowl_head_far_constraints.json | 288 | 2026-08-02 |  |  |
| batch_out/bowl_head_far_fused_cloud.npz | 5965394 | 2026-08-02 |  |  |
| batch_out/bowl_head_far_grasps_out.npz | 1640547 | 2026-08-02 |  |  |
| batch_out/bowl_head_far_grasps_plain.npz | 6026 | 2026-08-02 |  |  |
| batch_out/bowl_head_far_multiview.npz | 2151910 | 2026-08-02 |  |  |
| batch_out/cluster_mug_cokecan_pot_close_params.csv | 2289 | 2026-07-26 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/cluster_mug_cokecan_pot_constraints.json | 283 | 2026-07-26 |  |  |
| batch_out/cluster_mug_cokecan_pot_fused_cloud.npz | 5712050 | 2026-07-26 |  |  |
| batch_out/cluster_mug_cokecan_pot_grasps_plain.npz | 6026 | 2026-07-26 |  |  |
| batch_out/cluster_mug_remote_pot_close_params.csv | 2692 | 2026-07-26 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/cluster_mug_remote_pot_constraints.json | 307 | 2026-07-26 |  |  |
| batch_out/cluster_mug_remote_pot_fused_cloud.npz | 5735690 | 2026-07-26 |  |  |
| batch_out/cluster_mug_remote_pot_grasps_plain.npz | 6026 | 2026-07-26 |  |  |
| batch_out/metal_spoon_close_params.csv | 1997 | 2026-07-26 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/metal_spoon_constraints.json | 284 | 2026-07-26 |  |  |
| batch_out/metal_spoon_fused_cloud.npz | 5810930 | 2026-07-26 |  |  |
| batch_out/metal_spoon_grasps_plain.npz | 6026 | 2026-07-26 |  |  |
| batch_out/pot_with_handle_and_lid_close_params.csv | 2192 | 2026-07-26 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/pot_with_handle_and_lid_constraints.json | 290 | 2026-07-26 |  |  |
| batch_out/pot_with_handle_and_lid_fused_cloud.npz | 5715314 | 2026-07-26 |  |  |
| batch_out/pot_with_handle_and_lid_grasps_plain.npz | 6026 | 2026-07-26 |  |  |
| batch_out/TV_remote_close_params.csv | 2616 | 2026-07-26 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| batch_out/TV_remote_constraints.json | 307 | 2026-07-26 |  |  |
| batch_out/TV_remote_fused_cloud.npz | 5820890 | 2026-07-26 |  |  |
| batch_out/TV_remote_grasps_plain.npz | 6026 | 2026-07-26 |  |  |

### captures/ (6 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| captures/hand_cam_stow_frame.npz | 922124 | 2026-07-12 |  |  |
| captures/hand_view.npz | 923106 | 2026-06-11 |  |  |
| captures/hand_view_real.npz | 924140 | 2026-07-12 |  |  |
| captures/hand_view_real_grasp1_center_fail.npz | 924140 | 2026-07-10 |  |  |
| captures/head_capture.npz | 2151620 | 2026-06-15 |  |  |
| captures/regions.npz | 1224 | 2026-06-23 |  |  |

### captures_0723/ (8 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| captures_0723/cap_cluster_mug_cokecan.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_cluster_mug_cokecan_pot.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_cluster_mug_remote_pot.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_coke_can.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_dishwash_bottle.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_metal_spoon.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_pot_with_handle_and_lid.npz | 2152680 | 2026-07-25 |  |  |
| captures_0723/cap_TV_remote.npz | 2152680 | 2026-07-25 |  |  |

### captures_pairs/ (19 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| captures_pairs/cap_cluster_mug_can_pot_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_mug_can_pot_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_mug_can_remote_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_mug_can_remote_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_spoon_can_remote_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_spoon_can_remote_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_spoon_mug_pot_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_cluster_spoon_mug_pot_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_mug_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_mug_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_mug_hv_hand.npz | 922504 | 2026-07-28 |  |  |
| captures_pairs/cap_mug_hv_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_mug_hv_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_pot_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_pot_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_remote_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_remote_head_near.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_spoon_head_far.npz | 2152680 | 2026-07-28 |  |  |
| captures_pairs/cap_spoon_head_near.npz | 2152680 | 2026-07-28 |  |  |

### captures_pairs_2/ (33 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| captures_pairs_2/cap_bowl_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_bowl_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_bowl_knife_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_bowl_knife_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_can_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_can_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_can_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_mug_can_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_pot_mug_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_pot_mug_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_remote_knife_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_remote_knife_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_bowl_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_bowl_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_can_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_can_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_mug_knife_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_mug_knife_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_mug_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_cluster_spoon_mug_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_knife_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_knife_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_mug_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_mug_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_mug_hv_hand.npz | 922504 | 2026-08-01 |  |  |
| captures_pairs_2/cap_mug_hv_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_mug_hv_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_spoon_head_far.npz | 2152680 | 2026-08-01 |  |  |
| captures_pairs_2/cap_spoon_head_near.npz | 2152680 | 2026-08-01 |  |  |

### codex/ (8 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| codex/01_census.md | 22171 | 2026-08-04 |  |  |
| codex/02_history.md | 23574 | 2026-08-04 |  |  |
| codex/03_scripts.md | 155169 | 2026-08-04 |  |  |
| codex/04_data.md | 211412 | 2026-08-05 |  |  |
| codex/05_figures.md | 42193 | 2026-08-05 |  |  |
| codex/06_graph.md | 17427 | 2026-08-05 |  |  |
| codex/CODEX.md | 33659 | 2026-08-05 |  |  |
| codex/index.csv | 412255 | 2026-08-05 | `path,type,machine,purpose,status,produced_by,produces,last_modified,tracked,evidence_tag` | 2674 |

### contact_graspnet_pytorch/ (24 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| contact_graspnet_pytorch/checkpoints/contact_graspnet/config.yaml | 3637 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/contact_graspnet_env.yml | 8753 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/contact_graspnet_pytorch/config.yaml | 3635 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/docs/acronym_setup.md | 3039 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/docs/generate_scenes.md | 882 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/gripper_control_points/panda.npy | 448 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/gripper_control_points/panda_gripper_coords.yml | 424 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/gripper_models/panda_pc.npy | 817460 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/Pointnet_Pointnet2_pytorch/README.md | 7982 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/README.md | 5901 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/0.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/1.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/10.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/11.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/12.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/13.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/2.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/3.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/4.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/5.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/6.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/7.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/8.npy | 10138333 | 2026-03-04 |  |  |
| contact_graspnet_pytorch/test_data/9.npy | 10138333 | 2026-03-04 |  |  |

### docs/ (10 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| docs/evidence/FIGURES_5_7_EVIDENCE_AUDIT.md | 19520 | 2026-08-08 |  |  |
| docs/evidence/FIGURES_8_13_EVIDENCE_AUDIT.md | 18658 | 2026-08-08 |  |  |
| docs/superpowers/plans/2026-07-10-som-part-selection.md | 25286 | 2026-07-10 |  |  |
| docs/superpowers/plans/2026-07-13-constraint-based-part-reasoning.md | 41661 | 2026-07-13 |  |  |
| docs/superpowers/plans/2026-07-13-geometric-part-decomposition.md | 41365 | 2026-07-13 |  |  |
| docs/superpowers/plans/2026-08-07-dissertation-figures-storyboard-batch1.md | 67798 | 2026-08-08 |  |  |
| docs/superpowers/plans/2026-08-17-fig-3-7-base-placement.md | 29259 | 2026-08-17 |  |  |
| docs/superpowers/plans/2026-08-18-pointcloud-figures.md | 72595 | 2026-08-18 |  |  |
| docs/superpowers/specs/2026-08-07-dissertation-figures-design.md | 14788 | 2026-08-07 |  |  |
| docs/superpowers/specs/2026-08-08-figures-8-13-evidence-audit.md | 15197 | 2026-08-08 |  |  |

### evaluation_outputs/ (1 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| evaluation_outputs/part_adaptive_mug_evaluation.json | 1221 | 2026-08-08 |  |  |

### Experiment_Logs/ (8 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| Experiment_Logs/2026-08-07/close_params.csv | 1980 | 2026-08-07 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| Experiment_Logs/2026-08-07/constraints.json | 398 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/fused_cloud.npz | 5803898 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/grasps_out.npz | 1628119 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/grasps_plain.npz | 6026 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/head_capture_real.npz | 2152680 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/multiview.npz | 2151910 | 2026-08-07 |  |  |
| Experiment_Logs/2026-08-07/place_run.csv | 2424 | 2026-08-07 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |

### experiments/ (24 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| experiments/battery/battery_hand_me_the_mug.npz | 8975 | 2026-07-15 |  |  |
| experiments/battery/battery_lift_the_mug_using_its_handle.npz | 8965 | 2026-07-15 |  |  |
| experiments/battery/battery_move_the_mug_to_the_other_shelf.npz | 8965 | 2026-07-15 |  |  |
| experiments/battery/battery_pour_the_water_into_the_bowl.npz | 9024 | 2026-07-15 |  |  |
| experiments/battery/battery_results.md | 1083 | 2026-07-15 |  |  |
| experiments/battery/battery_stack_the_empty_mugs.npz | 8965 | 2026-07-15 |  |  |
| experiments/battery/battery_the_mug_just_came_out_of_the_microwave_-.npz | 8978 | 2026-07-15 |  |  |
| experiments/part_grasp/part_decomposition_table.md | 431 | 2026-07-13 |  |  |
| experiments/part_grasp/part_grasp.npz | 37124 | 2026-07-13 |  |  |
| experiments/part_grasp/part_grasp_handle.npz | 96001 | 2026-07-13 |  |  |
| experiments/part_grasp/part_grasp_pickup.npz | 50781 | 2026-07-12 |  |  |
| experiments/part_grasp/part_grasp_pour.npz | 50781 | 2026-07-12 |  |  |
| experiments/part_grasp/part_grasp_report_pick_up_the_mug.npz | 36329 | 2026-07-13 |  |  |
| experiments/part_grasp/part_grasp_report_pick_up_the_mug_by_the_handle.npz | 36329 | 2026-07-13 |  |  |
| experiments/part_grasp/part_grasp_report_pour_the_water_out_of_the_mug.npz | 28713 | 2026-07-13 |  |  |
| experiments/runs/grasp4_calib1/grasp4_calib1_fused_cloud.npz | 5756690 | 2026-07-14 |  |  |
| experiments/runs/grasp4_calib1/grasp4_calib1_grasps_plain.npz | 6026 | 2026-07-14 |  |  |
| experiments/runs/grasp4_calib1/grasp4_calib1_hand_view_real.npz | 924140 | 2026-07-14 |  |  |
| experiments/runs/grasp4_calib1/grasp4_calib1_head_capture_real.npz | 2152680 | 2026-07-14 |  |  |
| experiments/runs/grasp4_calib1/grasp4_calib1_place_run.csv | 1722 | 2026-07-14 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| experiments/vlm_grid/vlm_grid_handover_v2.md | 2773 | 2026-07-15 |  |  |
| experiments/vlm_grid/vlm_grid_handover_v2_raw.json | 7710 | 2026-07-15 |  |  |
| experiments/vlm_grid/vlm_grid_raw.json | 23616 | 2026-07-15 |  |  |
| experiments/vlm_grid/vlm_grid_results.md | 8931 | 2026-07-15 |  |  |

### figures/ (24 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| figures/archive/fig_1_1_knife_version/README.md | 838 | 2026-08-17 |  |  |
| figures/ASSET_LICENCES.md | 562 | 2026-08-15 |  |  |
| figures/BLOCKERS.md | 11985 | 2026-08-16 |  |  |
| figures/DESIGN_STANDARD.md | 7550 | 2026-08-16 |  |  |
| figures/out/table_5_1_resolution.md | 462 | 2026-08-15 |  |  |
| figures/out/table_6_1_constraint_fields.md | 1566 | 2026-08-16 |  |  |
| figures/PIPELINE_CHANGES.md | 4963 | 2026-08-16 |  |  |
| figures/QA_REPORT_A.md | 11417 | 2026-08-17 |  |  |
| figures/QA_REPORT_B.md | 4345 | 2026-08-17 |  |  |
| figures/QA_REPORT_fig36.md | 7965 | 2026-08-18 |  |  |
| figures/QA_REPORT_fig37.md | 4313 | 2026-08-17 |  |  |
| figures/QA_REPORT_fig38.md | 4051 | 2026-08-18 |  |  |
| figures/QA_REPORT_fig72.md | 9593 | 2026-08-18 |  |  |
| figures/QA_REPORT_selftest.md | 1223 | 2026-08-15 |  |  |
| figures/QA_REPORT_V-corrections.md | 4118 | 2026-08-16 |  |  |
| figures/QA_REPORT_V1.md | 3459 | 2026-08-16 |  |  |
| figures/QA_REPORT_V2.md | 1933 | 2026-08-16 |  |  |
| figures/QA_REPORT_V3.md | 1873 | 2026-08-16 |  |  |
| figures/QA_REPORT_V4.md | 4215 | 2026-08-16 |  |  |
| figures/QA_REPORT_V5.md | 1917 | 2026-08-16 |  |  |
| figures/REFERENCES_RECONCILED.md | 18530 | 2026-08-17 |  |  |
| figures/SOURCE_MANIFEST.md | 33031 | 2026-08-16 |  |  |
| figures/TABLE_DATA.md | 42144 | 2026-08-17 |  |  |
| figures/VISUAL_AUDIT.md | 6295 | 2026-08-16 |  |  |

### hsr_meshes/ (1 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| hsr_meshes/README.md | 524 | 2026-03-05 |  |  |

### outputs/ (5 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| outputs/motivation/body_mask.npy | 4000128 | 2026-08-06 |  |  |
| outputs/motivation/handle_mask.npy | 4000128 | 2026-08-06 |  |  |
| outputs/motivation/object_mask.npy | 4000128 | 2026-08-06 |  |  |
| outputs/motivation/rim_mask.npy | 4000128 | 2026-08-06 |  |  |
| outputs/motivation/segmentation_report.json | 559 | 2026-08-06 |  |  |

### report_assets/ (22 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| report_assets/CONSTRAINT_PROPAGATION.csv | 2611 | 2026-08-02 | `object,instruction,inferred_part,post_grasp_motion,stability_priority,keep_clear,lift_m,retreat,force_level,requires_controlled_tilt,alternative_parts_available,affected_by_segment_reversal` | 8 |
| report_assets/FAILURE_REGISTER.csv | 6883 | 2026-08-09 | `# selection_criterion: this register captures real, logged/sourced failures and` | 24 — MALFORMED — see note (field-count mismatch on 22 line(s)) |
| report_assets/figure_audit/contradictions.md | 2631 | 2026-08-09 |  |  |
| report_assets/figure_audit/evidence_manifest.json | 8407 | 2026-08-09 |  |  |
| report_assets/figure_audit/processing_log.md | 2421 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-A_manifest.json | 2784 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-B_manifest.json | 1544 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-D_manifest.json | 4473 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-E_manifest.json | 1723 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-F_manifest.json | 2299 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-H_manifest.json | 2334 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-HW_manifest.json | 2466 | 2026-08-09 |  |  |
| report_assets/figure_data/NEW-I_manifest.json | 2294 | 2026-08-09 |  |  |
| report_assets/figure_data/Slide11_methodology_manifest.json | 1658 | 2026-08-09 |  |  |
| report_assets/figure_data/Slide13_perception_manifest.json | 2332 | 2026-08-09 |  |  |
| report_assets/figure_data/Slide14_hardware_manifest.json | 2819 | 2026-08-09 |  |  |
| report_assets/figure_data/Slide15_clutter_manifest.json | 2206 | 2026-08-09 |  |  |
| report_assets/FIGURE_MANIFEST.csv | 10084 | 2026-08-02 | `figure_path,stage_number,stage_name,generating_script,exact_command,input_capture,instruction,inferred_part,part_source,evidence_class,date_generated,what_a_non_specialist_sees,proposed_slot,affected_by_segment_reversal` | 9 — MALFORMED — see note (field-count mismatch on 6 line(s)) |
| report_assets/PART_NAMING_ABLATION.csv | 7155 | 2026-08-03 | `object,instruction,method,expected_component,chosen_component,width_mm,points,evidence,pixel_pos,correct,raw_points,nearest_distance_px,outcome` | 29 — MALFORMED — see note (field-count mismatch on 4 line(s)) |
| report_assets/PERCEPTION_EVIDENCE.md | 19769 | 2026-08-03 |  |  |
| report_assets/PERCEPTION_INVENTORY.md | 74882 | 2026-08-02 |  |  |
| report_assets/SENSOR_ENVELOPE.md | 3477 | 2026-08-02 |  |  |

### report_bundle_20260801_1611/ (27 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| report_bundle_20260801_1611/captures_obj/cap_mug_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_obj/cap_mug_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_obj/capture_log.json | 1818 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_mug_can_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_mug_can_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_mug_can_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_mug_can_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_spoon_can_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_spoon_can_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_spoon_mug_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_cluster_spoon_mug_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_mug_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_mug_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_mug_hv_hand.npz | 922504 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_mug_hv_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_mug_hv_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_pot_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_pot_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_remote_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_remote_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_spoon_head_far.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/captures_pairs/cap_spoon_head_near.npz | 2152680 | 2026-08-01 |  |  |
| report_bundle_20260801_1611/close_params.csv | 1989 | 2026-08-01 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| report_bundle_20260801_1611/gripper_gap_map.csv | 340 | 2026-08-01 | `cmd_angle,motor_angle,gap_m` | 9 |
| report_bundle_20260801_1611/place_run.csv | 2424 | 2026-08-01 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |
| report_bundle_20260801_1611/README.md | 552 | 2026-08-09 |  |  |
| report_bundle_20260801_1611/trials.csv | 2362 | 2026-08-01 | `timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note` | 11 |

### results/ (398 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| results/cgn_candidates/candidates_bottle.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_183028.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_183356.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_183708.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_184028.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_184348.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_bottle_20260608_184704.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_182915.npz | 34916 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_183253.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_183609.npz | 5916 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_183925.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_184242.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_hammer_20260608_184558.npz | 41716 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_mug.npz | 41704 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_mug_20260608_183137.npz | 41704 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_mug_20260608_184132.npz | 41704 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_unknown_20260610_172425.npz | 41720 | 2026-06-10 |  |  |
| results/cgn_candidates/candidates_unknown_20260610_175305.npz | 41720 | 2026-06-10 |  |  |
| results/cgn_candidates/candidates_unknown_20260611_093009.npz | 41720 | 2026-06-11 |  |  |
| results/cgn_candidates/candidates_unknown_20260616_125811.npz | 41720 | 2026-06-16 |  |  |
| results/cgn_candidates/candidates_unknown_20260623_195915.npz | 41720 | 2026-06-23 |  |  |
| results/cgn_candidates/candidates_unknown_20260623_201059.npz | 41720 | 2026-06-23 |  |  |
| results/cgn_candidates/candidates_unknown_20260626_152847.npz | 41720 | 2026-06-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260703_151126.npz | 41720 | 2026-07-03 |  |  |
| results/cgn_candidates/candidates_unknown_20260704_144024.npz | 41720 | 2026-07-04 |  |  |
| results/cgn_candidates/candidates_unknown_20260706_152359.npz | 41720 | 2026-07-06 |  |  |
| results/cgn_candidates/candidates_unknown_20260706_154029.npz | 41720 | 2026-07-06 |  |  |
| results/cgn_candidates/candidates_unknown_20260706_163800.npz | 41720 | 2026-07-06 |  |  |
| results/cgn_candidates/candidates_unknown_20260706_164019.npz | 41720 | 2026-07-06 |  |  |
| results/cgn_candidates/candidates_unknown_20260708_135022.npz | 41720 | 2026-07-08 |  |  |
| results/cgn_candidates/candidates_unknown_20260708_140411.npz | 41720 | 2026-07-08 |  |  |
| results/cgn_candidates/candidates_unknown_20260708_142120.npz | 41720 | 2026-07-08 |  |  |
| results/cgn_candidates/candidates_unknown_20260710_142509.npz | 41720 | 2026-07-10 |  |  |
| results/cgn_candidates/candidates_unknown_20260710_151137.npz | 41720 | 2026-07-10 |  |  |
| results/cgn_candidates/candidates_unknown_20260712_145223.npz | 41720 | 2026-07-12 |  |  |
| results/cgn_candidates/candidates_unknown_20260714_144654.npz | 41720 | 2026-07-14 |  |  |
| results/cgn_candidates/candidates_unknown_20260714_175933.npz | 41720 | 2026-07-14 |  |  |
| results/cgn_candidates/candidates_unknown_20260716_111631.npz | 41720 | 2026-07-16 |  |  |
| results/cgn_candidates/candidates_unknown_20260716_113421.npz | 41720 | 2026-07-16 |  |  |
| results/cgn_candidates/candidates_unknown_20260716_114333.npz | 41720 | 2026-07-16 |  |  |
| results/cgn_candidates/candidates_unknown_20260721_151415.npz | 41720 | 2026-07-21 |  |  |
| results/cgn_candidates/candidates_unknown_20260721_153530.npz | 41720 | 2026-07-21 |  |  |
| results/cgn_candidates/candidates_unknown_20260721_155928.npz | 41720 | 2026-07-21 |  |  |
| results/cgn_candidates/candidates_unknown_20260722_161840.npz | 41720 | 2026-07-22 |  |  |
| results/cgn_candidates/candidates_unknown_20260722_164945.npz | 41720 | 2026-07-22 |  |  |
| results/cgn_candidates/candidates_unknown_20260722_165127.npz | 41720 | 2026-07-22 |  |  |
| results/cgn_candidates/candidates_unknown_20260722_165452.npz | 41720 | 2026-07-22 |  |  |
| results/cgn_candidates/candidates_unknown_20260725_155403.npz | 41720 | 2026-07-25 |  |  |
| results/cgn_candidates/candidates_unknown_20260725_160911.npz | 41720 | 2026-07-25 |  |  |
| results/cgn_candidates/candidates_unknown_20260725_163031.npz | 41720 | 2026-07-25 |  |  |
| results/cgn_candidates/candidates_unknown_20260725_164853.npz | 41720 | 2026-07-25 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_140201.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_140244.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_140757.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_140847.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_140932.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_141021.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_141110.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_144137.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_145629.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260726_150631.npz | 41720 | 2026-07-26 |  |  |
| results/cgn_candidates/candidates_unknown_20260728_170238.npz | 41720 | 2026-07-28 |  |  |
| results/cgn_candidates/candidates_unknown_20260801_151711.npz | 41720 | 2026-08-01 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_002100.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_170513.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_170919.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_171023.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_171128.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_171702.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_173716.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_173818.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260802_173921.npz | 41720 | 2026-08-02 |  |  |
| results/cgn_candidates/candidates_unknown_20260803_141032.npz | 41720 | 2026-08-03 |  |  |
| results/cgn_candidates/candidates_unknown_20260807_162836.npz | 41720 | 2026-08-07 |  |  |
| results/cgn_candidates/candidates_unknown_20260807_164344.npz | 41720 | 2026-08-07 |  |  |
| results/cgn_candidates/candidates_unknown_20260807_170023.npz | 41720 | 2026-08-07 |  |  |
| results/cgn_candidates/candidates_unknown_20260807_181248.npz | 41720 | 2026-08-07 |  |  |
| results/cgn_candidates/candidates_wine_glass_20260608_182802.npz | 41732 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_wine_glass_20260608_183504.npz | 41732 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_wine_glass_20260608_183817.npz | 41732 | 2026-06-08 |  |  |
| results/cgn_candidates/candidates_wine_glass_20260608_184456.npz | 20132 | 2026-06-08 |  |  |
| results/diag/diag_bottle_diag.json | 7217 | 2026-05-14 |  |  |
| results/diag/diag_hammer_diag.json | 7209 | 2026-05-14 |  |  |
| results/diag/diag_mug_diag.json | 7249 | 2026-05-14 |  |  |
| results/diag/DIAGNOSTIC_REPORT.md | 15263 | 2026-05-14 |  |  |
| results/diag2_bottle_diag.json | 7341 | 2026-05-14 |  |  |
| results/diag2_hammer_diag.json | 7351 | 2026-05-14 |  |  |
| results/diag2_mug_diag.json | 7338 | 2026-05-14 |  |  |
| results/motion_trace2_mug_diag.json | 76649 | 2026-05-15 |  |  |
| results/MOTION_TRACE2_REPORT.md | 7214 | 2026-05-15 |  |  |
| results/motion_trace3_mug_diag.json | 79888 | 2026-05-15 |  |  |
| results/MOTION_TRACE3_REPORT.md | 7014 | 2026-05-15 |  |  |
| results/motion_trace_mug_diag.json | 73183 | 2026-05-14 |  |  |
| results/MOTION_TRACE_REPORT.md | 9194 | 2026-05-14 |  |  |
| results/POST_FIX_REPORT.md | 6564 | 2026-05-14 |  |  |
| results/post_reach_filter_bottle_diag.json | 79785 | 2026-05-16 |  |  |
| results/post_reach_filter_hammer_diag.json | 79694 | 2026-05-16 |  |  |
| results/POST_REACH_FILTER_REPORT.md | 9977 | 2026-05-16 |  |  |
| results/REACH_DIAGNOSIS.md | 9449 | 2026-05-15 |  |  |
| results/REACH_DIAGNOSIS_V2.md | 6242 | 2026-05-16 |  |  |
| results/REACH_DIAGNOSIS_V3.md | 8918 | 2026-05-16 |  |  |
| results/trial_20260301_150326_mug/pipeline_results.json | 3053 | 2026-03-01 |  |  |
| results/trial_20260301_150326_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_150326_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_150555_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_151412_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_151833_mug/pipeline_results.json | 3069 | 2026-03-01 |  |  |
| results/trial_20260301_151833_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_151833_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_152831_mug/pipeline_results.json | 3067 | 2026-03-01 |  |  |
| results/trial_20260301_152831_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_152831_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_153131_mug/pipeline_results.json | 3066 | 2026-03-01 |  |  |
| results/trial_20260301_153131_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_153131_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_153324_mug/pipeline_results.json | 3064 | 2026-03-01 |  |  |
| results/trial_20260301_153324_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_153324_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260301_153407_mug/pipeline_results.json | 3059 | 2026-03-01 |  |  |
| results/trial_20260301_153407_mug/reasoning_result.json | 127 | 2026-03-01 |  |  |
| results/trial_20260301_153407_mug/scene_intrinsics.npy | 200 | 2026-03-01 |  |  |
| results/trial_20260303_202801_hammer/pipeline_results.json | 3068 | 2026-03-03 |  |  |
| results/trial_20260303_202801_hammer/reasoning_result.json | 131 | 2026-03-03 |  |  |
| results/trial_20260303_202801_hammer/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_202822_scissors/pipeline_results.json | 3083 | 2026-03-03 |  |  |
| results/trial_20260303_202822_scissors/reasoning_result.json | 136 | 2026-03-03 |  |  |
| results/trial_20260303_202822_scissors/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_202908_scissors/pipeline_results.json | 3087 | 2026-03-03 |  |  |
| results/trial_20260303_202908_scissors/reasoning_result.json | 136 | 2026-03-03 |  |  |
| results/trial_20260303_202908_scissors/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_204333_mug/reasoning_result.json | 127 | 2026-03-03 |  |  |
| results/trial_20260303_204333_mug/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_204458_mug/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_204726_mug/pipeline_results.json | 3054 | 2026-03-03 |  |  |
| results/trial_20260303_204726_mug/reasoning_result.json | 122 | 2026-03-03 |  |  |
| results/trial_20260303_204726_mug/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_204850_hammer/pipeline_results.json | 3097 | 2026-03-03 |  |  |
| results/trial_20260303_204850_hammer/reasoning_result.json | 148 | 2026-03-03 |  |  |
| results/trial_20260303_204850_hammer/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_204942_hammer/pipeline_results.json | 3105 | 2026-03-03 |  |  |
| results/trial_20260303_204942_hammer/reasoning_result.json | 155 | 2026-03-03 |  |  |
| results/trial_20260303_204942_hammer/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_205507_mug/pipeline_results.json | 3051 | 2026-03-03 |  |  |
| results/trial_20260303_205507_mug/reasoning_result.json | 117 | 2026-03-03 |  |  |
| results/trial_20260303_205507_mug/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260303_205551_mug/pipeline_results.json | 3063 | 2026-03-03 |  |  |
| results/trial_20260303_205551_mug/reasoning_result.json | 120 | 2026-03-03 |  |  |
| results/trial_20260303_205551_mug/scene_intrinsics.npy | 200 | 2026-03-03 |  |  |
| results/trial_20260304_053620_hammer/pipeline_results.json | 3092 | 2026-03-04 |  |  |
| results/trial_20260304_053620_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_053620_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_053713_mug/reasoning_result.json | 120 | 2026-03-04 |  |  |
| results/trial_20260304_053713_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_061906_hammer/reasoning_result.json | 134 | 2026-03-04 |  |  |
| results/trial_20260304_061906_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_123300_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_123300_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_124212_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_124212_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_124358_mug/pipeline_results.json | 594 | 2026-03-04 |  |  |
| results/trial_20260304_124358_mug/reasoning_result.json | 118 | 2026-03-04 |  |  |
| results/trial_20260304_124358_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_124810_hammer/pipeline_results.json | 606 | 2026-03-04 |  |  |
| results/trial_20260304_124810_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_124810_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_125146_hammer/pipeline_results.json | 605 | 2026-03-04 |  |  |
| results/trial_20260304_125146_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_125146_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_125408_hammer/pipeline_results.json | 606 | 2026-03-04 |  |  |
| results/trial_20260304_125408_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_125408_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_130322_hammer/pipeline_results.json | 605 | 2026-03-04 |  |  |
| results/trial_20260304_130322_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_130322_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_130604_hammer/pipeline_results.json | 607 | 2026-03-04 |  |  |
| results/trial_20260304_130604_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_130604_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_130821_hammer/pipeline_results.json | 607 | 2026-03-04 |  |  |
| results/trial_20260304_130821_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_130821_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_130939_hammer/pipeline_results.json | 606 | 2026-03-04 |  |  |
| results/trial_20260304_130939_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_130939_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_131200_hammer/pipeline_results.json | 1251 | 2026-03-04 |  |  |
| results/trial_20260304_131200_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_131200_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_131547_hammer/pipeline_results.json | 3082 | 2026-03-04 |  |  |
| results/trial_20260304_131547_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_131547_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_131735_hammer/pipeline_results.json | 1250 | 2026-03-04 |  |  |
| results/trial_20260304_131735_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_131735_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_131938_hammer/pipeline_results.json | 606 | 2026-03-04 |  |  |
| results/trial_20260304_131938_hammer/reasoning_result.json | 132 | 2026-03-04 |  |  |
| results/trial_20260304_131938_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_132204_hammer/pipeline_results.json | 3098 | 2026-03-04 |  |  |
| results/trial_20260304_132204_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_132204_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_132329_hammer/pipeline_results.json | 3093 | 2026-03-04 |  |  |
| results/trial_20260304_132329_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_132329_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_132432_hammer/pipeline_results.json | 3098 | 2026-03-04 |  |  |
| results/trial_20260304_132432_hammer/reasoning_result.json | 132 | 2026-03-04 |  |  |
| results/trial_20260304_132432_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_132608_mug/pipeline_results.json | 3073 | 2026-03-04 |  |  |
| results/trial_20260304_132608_mug/reasoning_result.json | 120 | 2026-03-04 |  |  |
| results/trial_20260304_132608_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_133550_mug/pipeline_results.json | 3078 | 2026-03-04 |  |  |
| results/trial_20260304_133550_mug/reasoning_result.json | 118 | 2026-03-04 |  |  |
| results/trial_20260304_133550_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_133750_mug/reasoning_result.json | 118 | 2026-03-04 |  |  |
| results/trial_20260304_133750_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_134014_mug/pipeline_results.json | 3072 | 2026-03-04 |  |  |
| results/trial_20260304_134014_mug/reasoning_result.json | 118 | 2026-03-04 |  |  |
| results/trial_20260304_134014_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_134100_mug/pipeline_results.json | 3064 | 2026-03-04 |  |  |
| results/trial_20260304_134100_mug/reasoning_result.json | 118 | 2026-03-04 |  |  |
| results/trial_20260304_134100_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_134201_mug/pipeline_results.json | 3066 | 2026-03-04 |  |  |
| results/trial_20260304_134201_mug/reasoning_result.json | 120 | 2026-03-04 |  |  |
| results/trial_20260304_134201_mug/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_134459_hammer/pipeline_results.json | 3103 | 2026-03-04 |  |  |
| results/trial_20260304_134459_hammer/reasoning_result.json | 134 | 2026-03-04 |  |  |
| results/trial_20260304_134459_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_134953_hammer/pipeline_results.json | 3087 | 2026-03-04 |  |  |
| results/trial_20260304_134953_hammer/reasoning_result.json | 131 | 2026-03-04 |  |  |
| results/trial_20260304_134953_hammer/scene_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195711_hammer/pipeline_results.json | 3104 | 2026-03-04 |  |  |
| results/trial_20260304_195711_hammer/reasoning_result.json | 132 | 2026-03-04 |  |  |
| results/trial_20260304_195711_hammer/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195711_hammer/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195711_hammer/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195947_mug/pipeline_results.json | 3117 | 2026-03-04 |  |  |
| results/trial_20260304_195947_mug/reasoning_result.json | 148 | 2026-03-04 |  |  |
| results/trial_20260304_195947_mug/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195947_mug/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_195947_mug/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200345_mug/pipeline_results.json | 3122 | 2026-03-04 |  |  |
| results/trial_20260304_200345_mug/reasoning_result.json | 150 | 2026-03-04 |  |  |
| results/trial_20260304_200345_mug/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200345_mug/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200345_mug/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200633_mug/pipeline_results.json | 3107 | 2026-03-04 |  |  |
| results/trial_20260304_200633_mug/reasoning_result.json | 147 | 2026-03-04 |  |  |
| results/trial_20260304_200633_mug/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200633_mug/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200633_mug/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200749_mug/pipeline_results.json | 3119 | 2026-03-04 |  |  |
| results/trial_20260304_200749_mug/reasoning_result.json | 147 | 2026-03-04 |  |  |
| results/trial_20260304_200749_mug/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200749_mug/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_200749_mug/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_201628_spoon/pipeline_results.json | 3135 | 2026-03-04 |  |  |
| results/trial_20260304_201628_spoon/reasoning_result.json | 147 | 2026-03-04 |  |  |
| results/trial_20260304_201628_spoon/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_201628_spoon/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_201628_spoon/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_202957_pan/pipeline_results.json | 3120 | 2026-03-04 |  |  |
| results/trial_20260304_202957_pan/reasoning_result.json | 147 | 2026-03-04 |  |  |
| results/trial_20260304_202957_pan/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_202957_pan/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_202957_pan/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_203246_cup/pipeline_results.json | 2664 | 2026-03-04 |  |  |
| results/trial_20260304_203246_cup/reasoning_result.json | 146 | 2026-03-04 |  |  |
| results/trial_20260304_203246_cup/scene_front_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_203246_cup/scene_side_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260304_203246_cup/scene_top_intrinsics.npy | 200 | 2026-03-04 |  |  |
| results/trial_20260305_002649_hammer/pipeline_results.json | 3109 | 2026-03-05 |  |  |
| results/trial_20260305_002649_hammer/reasoning_result.json | 131 | 2026-03-05 |  |  |
| results/trial_20260305_002649_hammer/scene_front_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_002649_hammer/scene_side_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_002649_hammer/scene_top_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_004102_wine_glass/pipeline_results.json | 1283 | 2026-03-05 |  |  |
| results/trial_20260305_004102_wine_glass/reasoning_result.json | 147 | 2026-03-05 |  |  |
| results/trial_20260305_004102_wine_glass/scene_front_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_004102_wine_glass/scene_side_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_004102_wine_glass/scene_top_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_013436_bottle/pipeline_results.json | 3092 | 2026-03-05 |  |  |
| results/trial_20260305_013436_bottle/reasoning_result.json | 128 | 2026-03-05 |  |  |
| results/trial_20260305_013436_bottle/scene_front_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_013436_bottle/scene_side_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260305_013436_bottle/scene_top_intrinsics.npy | 200 | 2026-03-05 |  |  |
| results/trial_20260411_225854_hammer/pipeline_results.json | 3089 | 2026-04-11 |  |  |
| results/trial_20260411_225854_hammer/reasoning_result.json | 131 | 2026-04-11 |  |  |
| results/trial_20260411_225854_hammer/scene_front_intrinsics.npy | 200 | 2026-04-11 |  |  |
| results/trial_20260411_225854_hammer/scene_side_intrinsics.npy | 200 | 2026-04-11 |  |  |
| results/trial_20260411_225854_hammer/scene_top_intrinsics.npy | 200 | 2026-04-11 |  |  |
| results/trial_20260608_174518_mug/pipeline_results.json | 2628 | 2026-06-08 |  |  |
| results/trial_20260608_174518_mug/reasoning_result.json | 120 | 2026-06-08 |  |  |
| results/trial_20260608_174518_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174518_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174518_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174742_hammer/pipeline_results.json | 607 | 2026-06-08 |  |  |
| results/trial_20260608_174742_hammer/reasoning_result.json | 132 | 2026-06-08 |  |  |
| results/trial_20260608_174742_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174742_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174742_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174852_bottle/pipeline_results.json | 3087 | 2026-06-08 |  |  |
| results/trial_20260608_174852_bottle/reasoning_result.json | 139 | 2026-06-08 |  |  |
| results/trial_20260608_174852_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174852_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_174852_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_175412_bottle/pipeline_results.json | 609 | 2026-06-08 |  |  |
| results/trial_20260608_175412_bottle/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_175412_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_175412_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_175412_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182730_mug/pipeline_results.json | 602 | 2026-06-08 |  |  |
| results/trial_20260608_182730_mug/reasoning_result.json | 123 | 2026-06-08 |  |  |
| results/trial_20260608_182730_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182730_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182730_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182849_hammer/pipeline_results.json | 2170 | 2026-06-08 |  |  |
| results/trial_20260608_182849_hammer/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_182849_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182849_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_182849_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183000_bottle/pipeline_results.json | 3100 | 2026-06-08 |  |  |
| results/trial_20260608_183000_bottle/reasoning_result.json | 136 | 2026-06-08 |  |  |
| results/trial_20260608_183000_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183000_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183000_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183111_mug/pipeline_results.json | 3074 | 2026-06-08 |  |  |
| results/trial_20260608_183111_mug/reasoning_result.json | 120 | 2026-06-08 |  |  |
| results/trial_20260608_183111_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183111_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183111_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183221_hammer/pipeline_results.json | 3096 | 2026-06-08 |  |  |
| results/trial_20260608_183221_hammer/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_183221_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183221_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183221_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183331_bottle/pipeline_results.json | 3086 | 2026-06-08 |  |  |
| results/trial_20260608_183331_bottle/reasoning_result.json | 139 | 2026-06-08 |  |  |
| results/trial_20260608_183331_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183331_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183331_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183435_mug/pipeline_results.json | 599 | 2026-06-08 |  |  |
| results/trial_20260608_183435_mug/reasoning_result.json | 121 | 2026-06-08 |  |  |
| results/trial_20260608_183435_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183435_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183435_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183544_hammer/pipeline_results.json | 605 | 2026-06-08 |  |  |
| results/trial_20260608_183544_hammer/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_183544_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183544_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183544_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183642_bottle/pipeline_results.json | 631 | 2026-06-08 |  |  |
| results/trial_20260608_183642_bottle/reasoning_result.json | 154 | 2026-06-08 |  |  |
| results/trial_20260608_183642_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183642_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183642_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183746_mug/pipeline_results.json | 3075 | 2026-06-08 |  |  |
| results/trial_20260608_183746_mug/reasoning_result.json | 121 | 2026-06-08 |  |  |
| results/trial_20260608_183746_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183746_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183746_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183900_hammer/pipeline_results.json | 606 | 2026-06-08 |  |  |
| results/trial_20260608_183900_hammer/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_183900_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183900_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_183900_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184003_bottle/pipeline_results.json | 625 | 2026-06-08 |  |  |
| results/trial_20260608_184003_bottle/reasoning_result.json | 147 | 2026-06-08 |  |  |
| results/trial_20260608_184003_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184003_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184003_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184107_mug/pipeline_results.json | 2622 | 2026-06-08 |  |  |
| results/trial_20260608_184107_mug/reasoning_result.json | 120 | 2026-06-08 |  |  |
| results/trial_20260608_184107_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184107_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184107_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184215_hammer/pipeline_results.json | 1251 | 2026-06-08 |  |  |
| results/trial_20260608_184215_hammer/reasoning_result.json | 131 | 2026-06-08 |  |  |
| results/trial_20260608_184215_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184215_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184215_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184324_bottle/pipeline_results.json | 630 | 2026-06-08 |  |  |
| results/trial_20260608_184324_bottle/reasoning_result.json | 154 | 2026-06-08 |  |  |
| results/trial_20260608_184324_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184324_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184324_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184426_mug/pipeline_results.json | 600 | 2026-06-08 |  |  |
| results/trial_20260608_184426_mug/reasoning_result.json | 123 | 2026-06-08 |  |  |
| results/trial_20260608_184426_mug/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184426_mug/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184426_mug/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184530_hammer/pipeline_results.json | 2178 | 2026-06-08 |  |  |
| results/trial_20260608_184530_hammer/reasoning_result.json | 135 | 2026-06-08 |  |  |
| results/trial_20260608_184530_hammer/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184530_hammer/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184530_hammer/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184637_bottle/pipeline_results.json | 1274 | 2026-06-08 |  |  |
| results/trial_20260608_184637_bottle/reasoning_result.json | 154 | 2026-06-08 |  |  |
| results/trial_20260608_184637_bottle/scene_front_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184637_bottle/scene_side_intrinsics.npy | 200 | 2026-06-08 |  |  |
| results/trial_20260608_184637_bottle/scene_top_intrinsics.npy | 200 | 2026-06-08 |  |  |

### run_0716_funnel/ (5 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| run_0716_funnel/fused_cloud.npz | 6021938 | 2026-07-16 |  |  |
| run_0716_funnel/grasps_plain.npz | 6026 | 2026-07-16 |  |  |
| run_0716_funnel/gripper_gap_map.csv | 340 | 2026-07-16 | `cmd_angle,motor_angle,gap_m` | 9 |
| run_0716_funnel/head_capture_real.npz | 2152680 | 2026-07-16 |  |  |
| run_0716_funnel/place_run.csv | 2394 | 2026-07-16 | `grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll` | 25 |

### run_0722_GRASP_OK/ (5 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| run_0722_GRASP_OK/close_params.csv | 1987 | 2026-07-22 | `grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note` | 25 |
| run_0722_GRASP_OK/closure_differentiation.md | 6775 | 2026-07-22 |  |  |
| run_0722_GRASP_OK/constraints.json | 324 | 2026-07-22 |  |  |
| run_0722_GRASP_OK/grasps_out.npz | 1621727 | 2026-07-22 |  |  |
| run_0722_GRASP_OK/grasps_plain.npz | 6026 | 2026-07-22 |  |  |

### YCB_Dataset/ (2 files)

| Path | Size (bytes) | Modified | CSV header | Data rows |
|---|---|---|---|---|
| YCB_Dataset/README.md | 1826 | 2026-03-04 |  |  |
| YCB_Dataset/scripts/ycb_mass.json | 1886 | 2026-03-04 |  |  |

### CSV parse issues — detail

- **components.csv** — MALFORMED — see note (field-count mismatch on 1 line(s))
  - Mismatched lines: line 4 (2 fields)
- **report_assets/FAILURE_REGISTER.csv** — MALFORMED — see note (field-count mismatch on 22 line(s))
  - Mismatched lines: line 2 (3 fields), line 5 (4 fields), line 6 (1 fields), line 7 (1 fields), line 8 (9 fields), line 9 (9 fields), line 10 (9 fields), line 11 (9 fields), line 12 (9 fields), line 13 (9 fields), line 14 (9 fields), line 15 (9 fields), line 16 (9 fields), line 17 (9 fields), line 18 (9 fields), line 19 (9 fields), line 20 (9 fields), line 21 (9 fields), line 22 (9 fields), line 23 (9 fields), line 24 (9 fields), line 25 (9 fields)
- **report_assets/FIGURE_MANIFEST.csv** — MALFORMED — see note (field-count mismatch on 6 line(s))
  - Mismatched lines: line 2 (15 fields), line 3 (16 fields), line 4 (16 fields), line 5 (15 fields), line 6 (17 fields), line 8 (15 fields)
- **report_assets/PART_NAMING_ABLATION.csv** — MALFORMED — see note (field-count mismatch on 4 line(s))
  - Mismatched lines: line 2 (14 fields), line 15 (14 fields), line 18 (14 fields), line 27 (12 fields)

---

## 2. Images

Restricted to files under `report_assets/`, `figures/`, `captures/`, and any `run_*`/`runs/` directories, filtered from the pre-built image list (2208 images total in repo). Long edge < 1200px is flagged.

| Path | Dimensions (WxH) | Size (bytes) | Flag |
|---|---|---|---|
| archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/place_run_map.png | 770x770 | 61135 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1447/hand_view_preview.png | 880x660 | 570048 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1447/place_run_map.png | 770x770 | 58300 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/final_center_debug.png | 880x660 | 569127 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/final_center_debug_grasp1_center_fail.png | 880x660 | 569127 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/hand_view_preview.png | 880x660 | 540194 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/hand_view_preview_grasp1_center_fail.png | 880x660 | 540194 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/place_run_map.png | 770x770 | 59168 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/final_center_debug.png | 880x660 | 622797 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/hand_view_preview.png | 880x660 | 573451 | ⚠ <1200px long edge |
| archive/backups/ws_backup_0711/results/run_0712_servo_session/place_run_map.png | 770x770 | 60013 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/place_run_map.png | 770x770 | 61135 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/hand_view_preview.png | 880x660 | 570048 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/place_run_map.png | 770x770 | 58300 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/final_center_debug.png | 880x660 | 569127 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/final_center_debug_grasp1_center_fail.png | 880x660 | 569127 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/hand_view_preview.png | 880x660 | 540194 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/hand_view_preview_grasp1_center_fail.png | 880x660 | 540194 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/place_run_map.png | 770x770 | 59168 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/final_center_debug.png | 880x660 | 622797 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/hand_view_preview.png | 880x660 | 573451 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/place_run_map.png | 770x770 | 60013 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/hand_view_preview.png | 880x660 | 563418 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/place_run_map.png | 770x770 | 59349 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/grasp_px_probe.png | 880x660 | 526064 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/place_run_map.png | 770x770 | 59550 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/place_run_map.png | 770x770 | 59791 | ⚠ <1200px long edge |
| Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/place_run_map.png | 770x770 | 59785 | ⚠ <1200px long edge |
| captures/capture_preview.png | 1540x550 | 636809 |  |
| captures/cgn_illustration.png | 1665x834 | 296622 |  |
| captures/differentiability.png | 2389x491 | 599939 |  |
| captures/differentiability_bottle.png | 1790x488 | 620245 |  |
| captures/differentiability_hammer.png | 1790x488 | 622719 |  |
| captures/final_center_debug.png | 880x660 | 569127 | ⚠ <1200px long edge |
| captures/final_center_debug_grasp1_center_fail.png | 880x660 | 569127 | ⚠ <1200px long edge |
| captures/fused_views.png | 1362x621 | 469202 |  |
| captures/grasp_diagnostic.png | 1488x691 | 117576 |  |
| captures/hand_part_som_marks.png | 146x161 | 36438 | ⚠ <1200px long edge |
| captures/hand_view_grounding.png | 1790x477 | 795100 |  |
| captures/hand_view_preview.png | 880x660 | 563418 | ⚠ <1200px long edge |
| captures/hand_view_preview_grasp1_center_fail.png | 880x660 | 540194 | ⚠ <1200px long edge |
| captures/mask_overlay.png | 1790x477 | 629367 |  |
| captures/multiview_grounding.png | 1757x893 | 1193443 |  |
| captures/point_prompt_v2.png | 1289x512 | 652119 |  |
| captures/point_prompt_v3.png | 1790x477 | 835283 |  |
| captures/projection_debug.png | 845x709 | 756426 | ⚠ <1200px long edge |
| captures/real_view.png | 666x506 | 539913 | ⚠ <1200px long edge |
| captures/refine_preview.png | 1100x770 | 774072 | ⚠ <1200px long edge |
| captures/region_marks.png | 826x626 | 363826 | ⚠ <1200px long edge |
| captures/scene_side.png | 910x650 | 105316 | ⚠ <1200px long edge |
| captures/scene_topdown.png | 910x780 | 69118 | ⚠ <1200px long edge |
| captures/som_grounding.png | 1790x477 | 840189 |  |
| captures/som_marks.png | 640x480 | 299804 | ⚠ <1200px long edge |
| captures/som_marks_handle.png | 146x161 | 36438 | ⚠ <1200px long edge |
| captures/test_ycb_scene.png | 960x720 | 226115 | ⚠ <1200px long edge |
| experiments/runs/grasp4_calib1/grasp4_calib1_grasp_px_probe.png | 880x660 | 599867 | ⚠ <1200px long edge |
| experiments/runs/grasp4_calib1/grasp4_calib1_hand_view_preview.png | 880x660 | 598871 | ⚠ <1200px long edge |
| experiments/runs/grasp4_calib1/grasp4_calib1_place_run_map.png | 770x770 | 58963 | ⚠ <1200px long edge |
| figures/archive/fig_1_1_knife_version/fig_1_1_motivating_handover.png | 2490x712 | 1117627 |  |
| figures/archive/fig_1_1_knife_version/fig_1_1_motivating_handover.svg | N/A (unreadable) | 1553968 | ⚠ could not read dimensions |
| figures/assets/knife_joseph_van_unsplash.jpg | 5472x3648 | 1846575 |  |
| figures/joseph-van-Fafvjw1n-ZA-unsplash.jpg | 5472x3648 | 1846575 |  |
| figures/knife.png | 1000x298 | 171335 | ⚠ <1200px long edge |
| figures/out/_style_smoketest.png | 1202x782 | 43798 |  |
| figures/out/_style_smoketest.svg | N/A (unreadable) | 7644 | ⚠ could not read dimensions |
| figures/out/fig_1_1_motivating_handover.png | 2524x1116 | 335840 |  |
| figures/out/fig_1_1_motivating_handover.svg | N/A (unreadable) | 453287 | ⚠ could not read dimensions |
| figures/out/fig_1_2_granularity_gap.png | 2457x1222 | 1150219 |  |
| figures/out/fig_1_2_granularity_gap.svg | N/A (unreadable) | 1321355 | ⚠ could not read dimensions |
| figures/out/fig_2_1_evolution_grasp_synthesis.png | 2490x1182 | 207963 |  |
| figures/out/fig_2_1_evolution_grasp_synthesis.svg | N/A (unreadable) | 7559 | ⚠ could not read dimensions |
| figures/out/fig_2_1_grounding_chain.png | 2880x1436 | 287498 |  |
| figures/out/fig_2_1_grounding_chain.svg | N/A (unreadable) | 332728 | ⚠ could not read dimensions |
| figures/out/fig_3_1_system_architecture.png | 2655x2535 | 313121 |  |
| figures/out/fig_3_1_system_architecture.svg | N/A (unreadable) | 22560 | ⚠ could not read dimensions |
| figures/out/fig_3_2_scope.png | 2642x1934 | 311529 |  |
| figures/out/fig_3_2_scope.svg | N/A (unreadable) | 9546 | ⚠ could not read dimensions |
| figures/out/fig_3_3_deployment.png | 2936x3434 | 406165 |  |
| figures/out/fig_3_3_deployment.svg | N/A (unreadable) | 24872 | ⚠ could not read dimensions |
| figures/out/fig_3_6_part_decomposition.png | 2497x285 | 161161 |  |
| figures/out/fig_3_6_part_decomposition.svg | N/A (unreadable) | 112276 | ⚠ could not read dimensions |
| figures/out/fig_3_7_base_placement.png | 2371x2803 | 701881 |  |
| figures/out/fig_3_7_base_placement.svg | N/A (unreadable) | 708268 | ⚠ could not read dimensions |
| figures/out/fig_3_8_pose_validation.png | 2423x1617 | 195037 |  |
| figures/out/fig_3_8_pose_validation.svg | N/A (unreadable) | 213107 | ⚠ could not read dimensions |
| figures/out/fig_5_1_mask_coverage.png | 2490x1262 | 116711 |  |
| figures/out/fig_5_1_mask_coverage.svg | N/A (unreadable) | 11610 | ⚠ could not read dimensions |
| figures/out/fig_5_2_requested_part_vs_mask.png | 2490x600 | 273308 |  |
| figures/out/fig_5_2_requested_part_vs_mask.svg | N/A (unreadable) | 310998 | ⚠ could not read dimensions |
| figures/out/fig_5_3_evidence_floor.png | 2490x1342 | 187477 |  |
| figures/out/fig_5_3_evidence_floor.svg | N/A (unreadable) | 85870 | ⚠ could not read dimensions |
| figures/out/fig_5_4_isolated_vs_cluttered.png | 2490x990 | 2168530 |  |
| figures/out/fig_5_4_isolated_vs_cluttered.svg | N/A (unreadable) | 2824596 | ⚠ could not read dimensions |
| figures/out/fig_5_5_mug_fragmentation.png | 2490x1302 | 258714 |  |
| figures/out/fig_5_5_mug_fragmentation.svg | N/A (unreadable) | 242795 | ⚠ could not read dimensions |
| figures/out/fig_6_1_18cell_grid.png | 1682x1342 | 93596 |  |
| figures/out/fig_6_1_18cell_grid.svg | N/A (unreadable) | 13502 | ⚠ could not read dimensions |
| figures/out/fig_6_2_handover_ablation.png | 2490x1502 | 159794 |  |
| figures/out/fig_6_2_handover_ablation.svg | N/A (unreadable) | 11373 | ⚠ could not read dimensions |
| figures/out/fig_6_3_method_agreement.png | 2490x1422 | 193521 |  |
| figures/out/fig_6_3_method_agreement.svg | N/A (unreadable) | 11482 | ⚠ could not read dimensions |
| figures/out/fig_6_4_decomposition_recovery.png | 1437x1422 | 318234 |  |
| figures/out/fig_6_4_decomposition_recovery.svg | N/A (unreadable) | 810145 | ⚠ could not read dimensions |
| figures/out/fig_7_2_lift_verification.png | 2485x1046 | 162227 |  |
| figures/out/fig_7_2_lift_verification.svg | N/A (unreadable) | 125085 | ⚠ could not read dimensions |
| figures/out/proofs/fig_1_1_motivating_handover_proof.png | 679x1126 | 103299 | ⚠ <1200px long edge |
| figures/out/proofs/fig_2_1_grounding_chain_proof.png | 679x1126 | 159837 | ⚠ <1200px long edge |
| figures/out/proofs/fig_3_1_system_architecture_proof.png | 679x1126 | 112035 | ⚠ <1200px long edge |
| figures/out/proofs/fig_5_1_proof.png | 679x1126 | 71365 | ⚠ <1200px long edge |
| figures/out/proofs/fig_5_2_proof.png | 679x1126 | 157653 | ⚠ <1200px long edge |
| figures/out/proofs/fig_5_3_proof.png | 679x1126 | 81944 | ⚠ <1200px long edge |
| figures/out/proofs/fig_5_4_proof.png | 679x1126 | 278397 | ⚠ <1200px long edge |
| figures/out/proofs/fig_5_5_proof.png | 679x1126 | 91464 | ⚠ <1200px long edge |
| figures/out/proofs/fig_6_1_proof.png | 679x1126 | 95960 | ⚠ <1200px long edge |
| figures/out/proofs/fig_6_2_proof.png | 679x1126 | 82656 | ⚠ <1200px long edge |
| figures/out/proofs/fig_6_3_proof.png | 679x1126 | 89646 | ⚠ <1200px long edge |
| figures/out/proofs/fig_6_4_proof.png | 679x1126 | 141902 | ⚠ <1200px long edge |
| report_assets/figure_audit/archive/new_a_slide_v1.png | 3200x1800 | 340468 |  |
| report_assets/figure_audit/archive/new_b_slide_v1.png | 3200x1800 | 2173299 |  |
| report_assets/figure_audit/archive/new_d_slide_v1.png | 3200x1800 | 1427755 |  |
| report_assets/figure_audit/archive/new_e_slide_v1.png | 3200x1800 | 1135072 |  |
| report_assets/figures/fig_intent_mug_head_near.png | 3127x680 | 757443 |  |
| report_assets/figures/fig_intent_pot_head_near.png | 3127x680 | 767527 |  |
| report_assets/figures/fig_limitation_pot_capture.png | 640x480 | 542633 | ⚠ <1200px long edge |
| report_assets/figures/fig_range_bowl.png | 2160x896 | 1877458 |  |
| report_assets/figures/fig_range_cluster_mug_bowl_knife.png | 2160x896 | 1966344 |  |
| report_assets/figures/fig_range_cluster_mug_can_pot.png | 2160x896 | 2029038 |  |
| report_assets/figures/fig_range_cluster_mug_can_remote.png | 2160x896 | 1945935 |  |
| report_assets/figures/fig_range_cluster_pot_mug.png | 2160x896 | 2004486 |  |
| report_assets/figures/fig_range_cluster_remote_knife.png | 2160x896 | 1942354 |  |
| report_assets/figures/fig_range_cluster_spoon_bowl.png | 2160x896 | 1897844 |  |
| report_assets/figures/fig_range_cluster_spoon_can_remote.png | 2160x896 | 1936240 |  |
| report_assets/figures/fig_range_cluster_spoon_mug_knife.png | 2160x896 | 1949508 |  |
| report_assets/figures/fig_range_cluster_spoon_mug_pot.png | 2160x896 | 1909033 |  |
| report_assets/figures/fig_range_knife.png | 2160x896 | 1901889 |  |
| report_assets/figures/fig_range_mug.png | 2160x896 | 1920324 |  |
| report_assets/figures/fig_range_mug_hv.png | 2160x896 | 1876874 |  |
| report_assets/figures/fig_range_pot.png | 2160x896 | 1982934 |  |
| report_assets/figures/fig_range_remote.png | 2160x896 | 1906485 |  |
| report_assets/figures/fig_range_spoon.png | 2160x896 | 1884381 |  |
| report_assets/figures/fig_results.png | 2295x1360 | 151854 |  |
| report_assets/figures/fig_results_11trials.png | 2295x1360 | 174010 |  |
| report_assets/figures/fig_slide2_intent_regions.png | 2560x1440 | 357099 |  |
| report_assets/figures/fig_stage0_capture_knife_near.png | 640x480 | 525998 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_knife_hand.png | 640x480 | 457148 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_knife_pick.png | 640x480 | 457148 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_knife_put.png | 640x480 | 457148 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_marks_knife.png | 640x480 | 457148 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_marks_mug.png | 640x480 | 465863 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_marks_remote.png | 640x480 | 454564 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_marks_spoon.png | 640x480 | 450000 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_mug_hand.png | 640x480 | 465863 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_mug_move.png | 640x480 | 465863 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_mug_pour.png | 640x480 | 465863 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_remote_hand.png | 640x480 | 454564 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_remote_power.png | 640x480 | 454564 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3b_som_remote_put.png | 640x480 | 454564 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_crop_knife_head_near.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_crop_mug_head_near.png | 1024x614 | 384249 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_crop_remote_head_near.png | 1024x310 | 346587 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_knife_hand.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_knife_hand_rep2.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_knife_hand_rep3.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_knife_pick.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_knife_put.png | 1024x251 | 244364 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_mug_hand.png | 1024x614 | 384249 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_mug_move.png | 1024x614 | 384249 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_mug_pour.png | 1024x614 | 384249 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_remote_hand.png | 1024x310 | 346587 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_remote_power.png | 1024x310 | 346587 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage3c_point_remote_put.png | 1024x310 | 346587 | ⚠ <1200px long edge |
| report_assets/figures/fig_stage4_knife_same_part_three_tasks.png | 3127x680 | 760152 |  |
| report_assets/figures/fig_stage4_mug_evidence_gate.png | 2346x680 | 729602 |  |
| report_assets/figures/fig_stage5_partmask_knife_blade_counterfactual.png | 2400x780 | 847940 |  |
| report_assets/figures/fig_stage5_partmask_knife_handle_pick.png | 2400x780 | 848010 |  |
| report_assets/figures/fig_stage7_alignment_knife.png | 2240x1080 | 278952 |  |
| report_assets/figures/figdeck_binding_test.png | 1400x900 | 64127 |  |
| report_assets/figures/figdeck_naming_ablation.png | 2200x1100 | 12027 |  |
| report_assets/figures/figdeck_resolution_floor.png | 1400x1000 | 69432 |  |
| report_assets/figures/figdeck_trials.png | 2400x1200 | 114419 |  |
| report_assets/figures/methodology_slide11.png | 3200x1800 | 265687 |  |
| report_assets/figures/NEW-HW_trial_history.png | 3200x1800 | 220830 |  |
| report_assets/figures/Slide10_NEW-A_part_decomposition.png | 3200x1800 | 339303 |  |
| report_assets/figures/Slide12_NEW-B_identification_grid.png | 3200x1800 | 1867824 |  |
| report_assets/figures/slide13_perception.png | 3200x1800 | 2743682 |  |
| report_assets/figures/slide14_hardware.png | 3200x1800 | 322616 |  |
| report_assets/figures/slide15_clutter.png | 3200x1800 | 1145239 |  |
| report_assets/figures/Slide16_NEW-F_failure_register.png | 3200x1800 | 203634 |  |
| report_assets/figures/Slide17a_NEW-H_three_layer_limit.png | 3200x1800 | 481663 |  |
| report_assets/figures/Slide17b_NEW-I_binding_fragility.png | 3200x1800 | 458551 |  |
| report_assets/figures_generated/fig_3_5_constraint_routing.png | 2520x1872 | 261962 |  |
| report_assets/figures_generated/fig_7_1_base_placement.png | 2520x1300 | 202108 |  |
| report_assets/figures_live/langsam_overlay_knife_pick.png | 640x480 | 370641 | ⚠ <1200px long edge |
| report_assets/figures_live/langsam_overlay_remote_power.png | 640x480 | 372040 | ⚠ <1200px long edge |
| run_0716_funnel/grasp_px_probe.png | 880x660 | 526064 | ⚠ <1200px long edge |
| run_0716_funnel/place_run_map.png | 770x770 | 59550 | ⚠ <1200px long edge |

Summary: 196 qualifying images, 91 flagged <1200px long edge, 22 unreadable.

---

## 3. Conflicts (duplicate basenames)

For every basename appearing at more than one path (from the pre-built dupe-basename list, 156 basenames total), restricted here to `.csv`, `.json`, and `.md` files — numbered-array `.npy` files (e.g. `0.npy`, `1.npy`, ...) and vendor/candidate-run duplicates (e.g. `candidates_bottle_*.npz`) are skipped as noise, not dissertation-relevant data/doc files.

### acronym_setup.md (2 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/docs/acronym_setup.md` — modified 2026-08-07, size=3039 bytes
  - `contact_graspnet_pytorch/docs/acronym_setup.md` — modified 2026-03-04, size=3039 bytes

### capture_log.json (2 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/captures_obj/capture_log.json` — modified 2026-08-07, size=1818 bytes
  - `report_bundle_20260801_1611/captures_obj/capture_log.json` — modified 2026-08-01, size=1818 bytes

### close_params.csv (7 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Experiment_Logs/2026-08-07/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `report_bundle_20260801_1611/close_params.csv` — modified 2026-08-01, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `run_0722_GRASP_OK/close_params.csv` — modified 2026-07-22, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25

### close_params_move.csv (3 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/close_params_move.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/close_params_move.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `close_params_move.csv` — modified 2026-07-22, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25

### close_params_pour.csv (3 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/close_params_pour.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/close_params_pour.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `close_params_pour.csv` — modified 2026-07-22, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25

### closure_differentiation.md (2 occurrences)

  - `closure_differentiation.md` — modified 2026-07-22, size=6775 bytes
  - `run_0722_GRASP_OK/closure_differentiation.md` — modified 2026-07-22, size=6775 bytes

### constraints.json (3 occurrences)

  - `constraints.json` — modified 2026-08-07, size=298 bytes
  - `Experiment_Logs/2026-08-07/constraints.json` — modified 2026-08-07, size=398 bytes
  - `run_0722_GRASP_OK/constraints.json` — modified 2026-07-22, size=324 bytes

### diag2_bottle_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag2_bottle_diag.json` — modified 2026-06-23, size=7341 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag2_bottle_diag.json` — modified 2026-08-07, size=7341 bytes
  - `results/diag2_bottle_diag.json` — modified 2026-05-14, size=7341 bytes

### diag2_hammer_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag2_hammer_diag.json` — modified 2026-06-23, size=7351 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag2_hammer_diag.json` — modified 2026-08-07, size=7351 bytes
  - `results/diag2_hammer_diag.json` — modified 2026-05-14, size=7351 bytes

### diag2_mug_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag2_mug_diag.json` — modified 2026-06-23, size=7338 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag2_mug_diag.json` — modified 2026-08-07, size=7338 bytes
  - `results/diag2_mug_diag.json` — modified 2026-05-14, size=7338 bytes

### diag_bottle_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag/diag_bottle_diag.json` — modified 2026-06-23, size=7217 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag/diag_bottle_diag.json` — modified 2026-08-07, size=7217 bytes
  - `results/diag/diag_bottle_diag.json` — modified 2026-05-14, size=7217 bytes

### diag_hammer_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag/diag_hammer_diag.json` — modified 2026-06-23, size=7209 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag/diag_hammer_diag.json` — modified 2026-08-07, size=7209 bytes
  - `results/diag/diag_hammer_diag.json` — modified 2026-05-14, size=7209 bytes

### diag_mug_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag/diag_mug_diag.json` — modified 2026-06-23, size=7249 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag/diag_mug_diag.json` — modified 2026-08-07, size=7249 bytes
  - `results/diag/diag_mug_diag.json` — modified 2026-05-14, size=7249 bytes

### DIAGNOSTIC_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/diag/DIAGNOSTIC_REPORT.md` — modified 2026-06-23, size=15263 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/diag/DIAGNOSTIC_REPORT.md` — modified 2026-08-07, size=15263 bytes
  - `results/diag/DIAGNOSTIC_REPORT.md` — modified 2026-05-14, size=15263 bytes

### generate_scenes.md (2 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/docs/generate_scenes.md` — modified 2026-08-07, size=882 bytes
  - `contact_graspnet_pytorch/docs/generate_scenes.md` — modified 2026-03-04, size=882 bytes

### gripper_gap_map.csv (7 occurrences)

  - `archive/backups/HSR_logs_20260714_183749/gripper_gap_map.csv` — modified 2026-07-19, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `gripper_gap_map.csv` — modified 2026-07-14, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `report_bundle_20260801_1611/gripper_gap_map.csv` — modified 2026-08-01, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `run_0716_funnel/gripper_gap_map.csv` — modified 2026-07-16, header=`cmd_angle,motor_angle,gap_m`, rows=9

### motion_trace2_mug_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/motion_trace2_mug_diag.json` — modified 2026-06-23, size=76649 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/motion_trace2_mug_diag.json` — modified 2026-08-07, size=76649 bytes
  - `results/motion_trace2_mug_diag.json` — modified 2026-05-15, size=76649 bytes

### MOTION_TRACE2_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/MOTION_TRACE2_REPORT.md` — modified 2026-06-23, size=7214 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE2_REPORT.md` — modified 2026-08-07, size=7214 bytes
  - `results/MOTION_TRACE2_REPORT.md` — modified 2026-05-15, size=7214 bytes

### motion_trace3_mug_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/motion_trace3_mug_diag.json` — modified 2026-06-23, size=79888 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/motion_trace3_mug_diag.json` — modified 2026-08-07, size=79888 bytes
  - `results/motion_trace3_mug_diag.json` — modified 2026-05-15, size=79888 bytes

### MOTION_TRACE3_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/MOTION_TRACE3_REPORT.md` — modified 2026-06-23, size=7014 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE3_REPORT.md` — modified 2026-08-07, size=7014 bytes
  - `results/MOTION_TRACE3_REPORT.md` — modified 2026-05-15, size=7014 bytes

### motion_trace_mug_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/motion_trace_mug_diag.json` — modified 2026-06-23, size=73183 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/motion_trace_mug_diag.json` — modified 2026-08-07, size=73183 bytes
  - `results/motion_trace_mug_diag.json` — modified 2026-05-14, size=73183 bytes

### MOTION_TRACE_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/MOTION_TRACE_REPORT.md` — modified 2026-06-23, size=9194 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/MOTION_TRACE_REPORT.md` — modified 2026-08-07, size=9194 bytes
  - `results/MOTION_TRACE_REPORT.md` — modified 2026-05-14, size=9194 bytes

### NOTES_NEXT_SESSION.md (5 occurrences)

  - `archive/backups/ws_backup_0711/NOTES_NEXT_SESSION.md` — modified 2026-07-12, size=1094 bytes
  - `archive/backups/ws_backup_0711/results/run_0712_servo_session/NOTES_NEXT_SESSION.md` — modified 2026-07-12, size=1094 bytes
  - `Backups/2026-08-07/Afford-Grasp/NOTES_NEXT_SESSION.md` — modified 2026-08-07, size=4333 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/NOTES_NEXT_SESSION.md` — modified 2026-08-07, size=1094 bytes
  - `NOTES_NEXT_SESSION.md` — modified 2026-07-16, size=4333 bytes

### part_decomposition_table.md (2 occurrences)

  - `archive/backups/results_home_0713/part_decomposition_table.md` — modified 2026-07-13, size=431 bytes
  - `experiments/part_grasp/part_decomposition_table.md` — modified 2026-07-13, size=431 bytes

### pipeline_results.json (213 occurrences)

  - `archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/pipeline_results.json` — modified 2026-06-23, size=3053 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_151833_mug/pipeline_results.json` — modified 2026-06-23, size=3069 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_152831_mug/pipeline_results.json` — modified 2026-06-23, size=3067 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153131_mug/pipeline_results.json` — modified 2026-06-23, size=3066 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153324_mug/pipeline_results.json` — modified 2026-06-23, size=3064 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153407_mug/pipeline_results.json` — modified 2026-06-23, size=3059 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202801_hammer/pipeline_results.json` — modified 2026-06-23, size=3068 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202822_scissors/pipeline_results.json` — modified 2026-06-23, size=3083 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202908_scissors/pipeline_results.json` — modified 2026-06-23, size=3087 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204726_mug/pipeline_results.json` — modified 2026-06-23, size=3054 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204850_hammer/pipeline_results.json` — modified 2026-06-23, size=3097 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204942_hammer/pipeline_results.json` — modified 2026-06-23, size=3105 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_205507_mug/pipeline_results.json` — modified 2026-06-23, size=3051 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_205551_mug/pipeline_results.json` — modified 2026-06-23, size=3063 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_053620_hammer/pipeline_results.json` — modified 2026-06-23, size=3092 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_124358_mug/pipeline_results.json` — modified 2026-06-23, size=594 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_124810_hammer/pipeline_results.json` — modified 2026-06-23, size=606 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_125146_hammer/pipeline_results.json` — modified 2026-06-23, size=605 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_125408_hammer/pipeline_results.json` — modified 2026-06-23, size=606 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130322_hammer/pipeline_results.json` — modified 2026-06-23, size=605 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130604_hammer/pipeline_results.json` — modified 2026-06-23, size=607 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130821_hammer/pipeline_results.json` — modified 2026-06-23, size=607 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130939_hammer/pipeline_results.json` — modified 2026-06-23, size=606 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131200_hammer/pipeline_results.json` — modified 2026-06-23, size=1251 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131547_hammer/pipeline_results.json` — modified 2026-06-23, size=3082 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131735_hammer/pipeline_results.json` — modified 2026-06-23, size=1250 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131938_hammer/pipeline_results.json` — modified 2026-06-23, size=606 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132204_hammer/pipeline_results.json` — modified 2026-06-23, size=3098 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132329_hammer/pipeline_results.json` — modified 2026-06-23, size=3093 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132432_hammer/pipeline_results.json` — modified 2026-06-23, size=3098 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132608_mug/pipeline_results.json` — modified 2026-06-23, size=3073 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_133550_mug/pipeline_results.json` — modified 2026-06-23, size=3078 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134014_mug/pipeline_results.json` — modified 2026-06-23, size=3072 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134100_mug/pipeline_results.json` — modified 2026-06-23, size=3064 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134201_mug/pipeline_results.json` — modified 2026-06-23, size=3066 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134459_hammer/pipeline_results.json` — modified 2026-06-23, size=3103 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134953_hammer/pipeline_results.json` — modified 2026-06-23, size=3087 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/pipeline_results.json` — modified 2026-06-23, size=3104 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/pipeline_results.json` — modified 2026-06-23, size=3117 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/pipeline_results.json` — modified 2026-06-23, size=3122 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/pipeline_results.json` — modified 2026-06-23, size=3107 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/pipeline_results.json` — modified 2026-06-23, size=3119 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/pipeline_results.json` — modified 2026-06-23, size=3135 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/pipeline_results.json` — modified 2026-06-23, size=3120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/pipeline_results.json` — modified 2026-06-23, size=2664 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/pipeline_results.json` — modified 2026-06-23, size=3109 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/pipeline_results.json` — modified 2026-06-23, size=1283 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/pipeline_results.json` — modified 2026-06-23, size=3092 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/pipeline_results.json` — modified 2026-06-23, size=3089 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/pipeline_results.json` — modified 2026-06-23, size=2628 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/pipeline_results.json` — modified 2026-06-23, size=607 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/pipeline_results.json` — modified 2026-06-23, size=3087 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/pipeline_results.json` — modified 2026-06-23, size=609 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/pipeline_results.json` — modified 2026-06-23, size=602 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/pipeline_results.json` — modified 2026-06-23, size=2170 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/pipeline_results.json` — modified 2026-06-23, size=3100 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/pipeline_results.json` — modified 2026-06-23, size=3074 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/pipeline_results.json` — modified 2026-06-23, size=3096 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/pipeline_results.json` — modified 2026-06-23, size=3086 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/pipeline_results.json` — modified 2026-06-23, size=599 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/pipeline_results.json` — modified 2026-06-23, size=605 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/pipeline_results.json` — modified 2026-06-23, size=631 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/pipeline_results.json` — modified 2026-06-23, size=3075 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/pipeline_results.json` — modified 2026-06-23, size=606 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/pipeline_results.json` — modified 2026-06-23, size=625 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/pipeline_results.json` — modified 2026-06-23, size=2622 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/pipeline_results.json` — modified 2026-06-23, size=1251 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/pipeline_results.json` — modified 2026-06-23, size=630 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/pipeline_results.json` — modified 2026-06-23, size=600 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/pipeline_results.json` — modified 2026-06-23, size=2178 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/pipeline_results.json` — modified 2026-06-23, size=1274 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150326_mug/pipeline_results.json` — modified 2026-08-07, size=3053 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151833_mug/pipeline_results.json` — modified 2026-08-07, size=3069 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_152831_mug/pipeline_results.json` — modified 2026-08-07, size=3067 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153131_mug/pipeline_results.json` — modified 2026-08-07, size=3066 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153324_mug/pipeline_results.json` — modified 2026-08-07, size=3064 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153407_mug/pipeline_results.json` — modified 2026-08-07, size=3059 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202801_hammer/pipeline_results.json` — modified 2026-08-07, size=3068 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202822_scissors/pipeline_results.json` — modified 2026-08-07, size=3083 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202908_scissors/pipeline_results.json` — modified 2026-08-07, size=3087 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204726_mug/pipeline_results.json` — modified 2026-08-07, size=3054 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204850_hammer/pipeline_results.json` — modified 2026-08-07, size=3097 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204942_hammer/pipeline_results.json` — modified 2026-08-07, size=3105 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205507_mug/pipeline_results.json` — modified 2026-08-07, size=3051 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205551_mug/pipeline_results.json` — modified 2026-08-07, size=3063 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053620_hammer/pipeline_results.json` — modified 2026-08-07, size=3092 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124358_mug/pipeline_results.json` — modified 2026-08-07, size=594 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124810_hammer/pipeline_results.json` — modified 2026-08-07, size=606 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125146_hammer/pipeline_results.json` — modified 2026-08-07, size=605 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125408_hammer/pipeline_results.json` — modified 2026-08-07, size=606 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130322_hammer/pipeline_results.json` — modified 2026-08-07, size=605 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130604_hammer/pipeline_results.json` — modified 2026-08-07, size=607 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130821_hammer/pipeline_results.json` — modified 2026-08-07, size=607 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130939_hammer/pipeline_results.json` — modified 2026-08-07, size=606 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131200_hammer/pipeline_results.json` — modified 2026-08-07, size=1251 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131547_hammer/pipeline_results.json` — modified 2026-08-07, size=3082 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131735_hammer/pipeline_results.json` — modified 2026-08-07, size=1250 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131938_hammer/pipeline_results.json` — modified 2026-08-07, size=606 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132204_hammer/pipeline_results.json` — modified 2026-08-07, size=3098 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132329_hammer/pipeline_results.json` — modified 2026-08-07, size=3093 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132432_hammer/pipeline_results.json` — modified 2026-08-07, size=3098 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132608_mug/pipeline_results.json` — modified 2026-08-07, size=3073 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133550_mug/pipeline_results.json` — modified 2026-08-07, size=3078 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134014_mug/pipeline_results.json` — modified 2026-08-07, size=3072 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134100_mug/pipeline_results.json` — modified 2026-08-07, size=3064 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134201_mug/pipeline_results.json` — modified 2026-08-07, size=3066 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134459_hammer/pipeline_results.json` — modified 2026-08-07, size=3103 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134953_hammer/pipeline_results.json` — modified 2026-08-07, size=3087 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/pipeline_results.json` — modified 2026-08-07, size=3104 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/pipeline_results.json` — modified 2026-08-07, size=3117 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/pipeline_results.json` — modified 2026-08-07, size=3122 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/pipeline_results.json` — modified 2026-08-07, size=3107 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/pipeline_results.json` — modified 2026-08-07, size=3119 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/pipeline_results.json` — modified 2026-08-07, size=3135 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/pipeline_results.json` — modified 2026-08-07, size=3120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/pipeline_results.json` — modified 2026-08-07, size=2664 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/pipeline_results.json` — modified 2026-08-07, size=3109 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/pipeline_results.json` — modified 2026-08-07, size=1283 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/pipeline_results.json` — modified 2026-08-07, size=3092 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/pipeline_results.json` — modified 2026-08-07, size=3089 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/pipeline_results.json` — modified 2026-08-07, size=2628 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/pipeline_results.json` — modified 2026-08-07, size=607 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/pipeline_results.json` — modified 2026-08-07, size=3087 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/pipeline_results.json` — modified 2026-08-07, size=609 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/pipeline_results.json` — modified 2026-08-07, size=602 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/pipeline_results.json` — modified 2026-08-07, size=2170 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/pipeline_results.json` — modified 2026-08-07, size=3100 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/pipeline_results.json` — modified 2026-08-07, size=3074 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/pipeline_results.json` — modified 2026-08-07, size=3096 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/pipeline_results.json` — modified 2026-08-07, size=3086 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/pipeline_results.json` — modified 2026-08-07, size=599 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/pipeline_results.json` — modified 2026-08-07, size=605 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/pipeline_results.json` — modified 2026-08-07, size=631 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/pipeline_results.json` — modified 2026-08-07, size=3075 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/pipeline_results.json` — modified 2026-08-07, size=606 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/pipeline_results.json` — modified 2026-08-07, size=625 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/pipeline_results.json` — modified 2026-08-07, size=2622 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/pipeline_results.json` — modified 2026-08-07, size=1251 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/pipeline_results.json` — modified 2026-08-07, size=630 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/pipeline_results.json` — modified 2026-08-07, size=600 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/pipeline_results.json` — modified 2026-08-07, size=2178 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/pipeline_results.json` — modified 2026-08-07, size=1274 bytes
  - `results/trial_20260301_150326_mug/pipeline_results.json` — modified 2026-03-01, size=3053 bytes
  - `results/trial_20260301_151833_mug/pipeline_results.json` — modified 2026-03-01, size=3069 bytes
  - `results/trial_20260301_152831_mug/pipeline_results.json` — modified 2026-03-01, size=3067 bytes
  - `results/trial_20260301_153131_mug/pipeline_results.json` — modified 2026-03-01, size=3066 bytes
  - `results/trial_20260301_153324_mug/pipeline_results.json` — modified 2026-03-01, size=3064 bytes
  - `results/trial_20260301_153407_mug/pipeline_results.json` — modified 2026-03-01, size=3059 bytes
  - `results/trial_20260303_202801_hammer/pipeline_results.json` — modified 2026-03-03, size=3068 bytes
  - `results/trial_20260303_202822_scissors/pipeline_results.json` — modified 2026-03-03, size=3083 bytes
  - `results/trial_20260303_202908_scissors/pipeline_results.json` — modified 2026-03-03, size=3087 bytes
  - `results/trial_20260303_204726_mug/pipeline_results.json` — modified 2026-03-03, size=3054 bytes
  - `results/trial_20260303_204850_hammer/pipeline_results.json` — modified 2026-03-03, size=3097 bytes
  - `results/trial_20260303_204942_hammer/pipeline_results.json` — modified 2026-03-03, size=3105 bytes
  - `results/trial_20260303_205507_mug/pipeline_results.json` — modified 2026-03-03, size=3051 bytes
  - `results/trial_20260303_205551_mug/pipeline_results.json` — modified 2026-03-03, size=3063 bytes
  - `results/trial_20260304_053620_hammer/pipeline_results.json` — modified 2026-03-04, size=3092 bytes
  - `results/trial_20260304_124358_mug/pipeline_results.json` — modified 2026-03-04, size=594 bytes
  - `results/trial_20260304_124810_hammer/pipeline_results.json` — modified 2026-03-04, size=606 bytes
  - `results/trial_20260304_125146_hammer/pipeline_results.json` — modified 2026-03-04, size=605 bytes
  - `results/trial_20260304_125408_hammer/pipeline_results.json` — modified 2026-03-04, size=606 bytes
  - `results/trial_20260304_130322_hammer/pipeline_results.json` — modified 2026-03-04, size=605 bytes
  - `results/trial_20260304_130604_hammer/pipeline_results.json` — modified 2026-03-04, size=607 bytes
  - `results/trial_20260304_130821_hammer/pipeline_results.json` — modified 2026-03-04, size=607 bytes
  - `results/trial_20260304_130939_hammer/pipeline_results.json` — modified 2026-03-04, size=606 bytes
  - `results/trial_20260304_131200_hammer/pipeline_results.json` — modified 2026-03-04, size=1251 bytes
  - `results/trial_20260304_131547_hammer/pipeline_results.json` — modified 2026-03-04, size=3082 bytes
  - `results/trial_20260304_131735_hammer/pipeline_results.json` — modified 2026-03-04, size=1250 bytes
  - `results/trial_20260304_131938_hammer/pipeline_results.json` — modified 2026-03-04, size=606 bytes
  - `results/trial_20260304_132204_hammer/pipeline_results.json` — modified 2026-03-04, size=3098 bytes
  - `results/trial_20260304_132329_hammer/pipeline_results.json` — modified 2026-03-04, size=3093 bytes
  - `results/trial_20260304_132432_hammer/pipeline_results.json` — modified 2026-03-04, size=3098 bytes
  - `results/trial_20260304_132608_mug/pipeline_results.json` — modified 2026-03-04, size=3073 bytes
  - `results/trial_20260304_133550_mug/pipeline_results.json` — modified 2026-03-04, size=3078 bytes
  - `results/trial_20260304_134014_mug/pipeline_results.json` — modified 2026-03-04, size=3072 bytes
  - `results/trial_20260304_134100_mug/pipeline_results.json` — modified 2026-03-04, size=3064 bytes
  - `results/trial_20260304_134201_mug/pipeline_results.json` — modified 2026-03-04, size=3066 bytes
  - `results/trial_20260304_134459_hammer/pipeline_results.json` — modified 2026-03-04, size=3103 bytes
  - `results/trial_20260304_134953_hammer/pipeline_results.json` — modified 2026-03-04, size=3087 bytes
  - `results/trial_20260304_195711_hammer/pipeline_results.json` — modified 2026-03-04, size=3104 bytes
  - `results/trial_20260304_195947_mug/pipeline_results.json` — modified 2026-03-04, size=3117 bytes
  - `results/trial_20260304_200345_mug/pipeline_results.json` — modified 2026-03-04, size=3122 bytes
  - `results/trial_20260304_200633_mug/pipeline_results.json` — modified 2026-03-04, size=3107 bytes
  - `results/trial_20260304_200749_mug/pipeline_results.json` — modified 2026-03-04, size=3119 bytes
  - `results/trial_20260304_201628_spoon/pipeline_results.json` — modified 2026-03-04, size=3135 bytes
  - `results/trial_20260304_202957_pan/pipeline_results.json` — modified 2026-03-04, size=3120 bytes
  - `results/trial_20260304_203246_cup/pipeline_results.json` — modified 2026-03-04, size=2664 bytes
  - `results/trial_20260305_002649_hammer/pipeline_results.json` — modified 2026-03-05, size=3109 bytes
  - `results/trial_20260305_004102_wine_glass/pipeline_results.json` — modified 2026-03-05, size=1283 bytes
  - `results/trial_20260305_013436_bottle/pipeline_results.json` — modified 2026-03-05, size=3092 bytes
  - `results/trial_20260411_225854_hammer/pipeline_results.json` — modified 2026-04-11, size=3089 bytes
  - `results/trial_20260608_174518_mug/pipeline_results.json` — modified 2026-06-08, size=2628 bytes
  - `results/trial_20260608_174742_hammer/pipeline_results.json` — modified 2026-06-08, size=607 bytes
  - `results/trial_20260608_174852_bottle/pipeline_results.json` — modified 2026-06-08, size=3087 bytes
  - `results/trial_20260608_175412_bottle/pipeline_results.json` — modified 2026-06-08, size=609 bytes
  - `results/trial_20260608_182730_mug/pipeline_results.json` — modified 2026-06-08, size=602 bytes
  - `results/trial_20260608_182849_hammer/pipeline_results.json` — modified 2026-06-08, size=2170 bytes
  - `results/trial_20260608_183000_bottle/pipeline_results.json` — modified 2026-06-08, size=3100 bytes
  - `results/trial_20260608_183111_mug/pipeline_results.json` — modified 2026-06-08, size=3074 bytes
  - `results/trial_20260608_183221_hammer/pipeline_results.json` — modified 2026-06-08, size=3096 bytes
  - `results/trial_20260608_183331_bottle/pipeline_results.json` — modified 2026-06-08, size=3086 bytes
  - `results/trial_20260608_183435_mug/pipeline_results.json` — modified 2026-06-08, size=599 bytes
  - `results/trial_20260608_183544_hammer/pipeline_results.json` — modified 2026-06-08, size=605 bytes
  - `results/trial_20260608_183642_bottle/pipeline_results.json` — modified 2026-06-08, size=631 bytes
  - `results/trial_20260608_183746_mug/pipeline_results.json` — modified 2026-06-08, size=3075 bytes
  - `results/trial_20260608_183900_hammer/pipeline_results.json` — modified 2026-06-08, size=606 bytes
  - `results/trial_20260608_184003_bottle/pipeline_results.json` — modified 2026-06-08, size=625 bytes
  - `results/trial_20260608_184107_mug/pipeline_results.json` — modified 2026-06-08, size=2622 bytes
  - `results/trial_20260608_184215_hammer/pipeline_results.json` — modified 2026-06-08, size=1251 bytes
  - `results/trial_20260608_184324_bottle/pipeline_results.json` — modified 2026-06-08, size=630 bytes
  - `results/trial_20260608_184426_mug/pipeline_results.json` — modified 2026-06-08, size=600 bytes
  - `results/trial_20260608_184530_hammer/pipeline_results.json` — modified 2026-06-08, size=2178 bytes
  - `results/trial_20260608_184637_bottle/pipeline_results.json` — modified 2026-06-08, size=1274 bytes

### place_run.csv (18 occurrences)

  - `archive/backups/HSR_logs_20260714_183749/place_run.csv` — modified 2026-07-19, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/place_run.csv` — modified 2026-07-06, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0710_1447/place_run.csv` — modified 2026-07-10, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/place_run.csv` — modified 2026-07-10, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0712_servo_session/place_run.csv` — modified 2026-07-12, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Experiment_Logs/2026-08-07/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `report_bundle_20260801_1611/place_run.csv` — modified 2026-08-01, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `run_0716_funnel/place_run.csv` — modified 2026-07-16, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25

### POST_FIX_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/POST_FIX_REPORT.md` — modified 2026-06-23, size=6564 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/POST_FIX_REPORT.md` — modified 2026-08-07, size=6564 bytes
  - `results/POST_FIX_REPORT.md` — modified 2026-05-14, size=6564 bytes

### post_reach_filter_bottle_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/post_reach_filter_bottle_diag.json` — modified 2026-06-23, size=79785 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/post_reach_filter_bottle_diag.json` — modified 2026-08-07, size=79785 bytes
  - `results/post_reach_filter_bottle_diag.json` — modified 2026-05-16, size=79785 bytes

### post_reach_filter_hammer_diag.json (3 occurrences)

  - `archive/backups/ws_backup_0711/results/post_reach_filter_hammer_diag.json` — modified 2026-06-23, size=79694 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/post_reach_filter_hammer_diag.json` — modified 2026-08-07, size=79694 bytes
  - `results/post_reach_filter_hammer_diag.json` — modified 2026-05-16, size=79694 bytes

### POST_REACH_FILTER_REPORT.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/POST_REACH_FILTER_REPORT.md` — modified 2026-06-23, size=9977 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/POST_REACH_FILTER_REPORT.md` — modified 2026-08-07, size=9977 bytes
  - `results/POST_REACH_FILTER_REPORT.md` — modified 2026-05-16, size=9977 bytes

### progress.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/progress.md` — modified 2026-08-08, size=10872 bytes
  - `.superpowers/sdd/progress.md` — modified 2026-07-14, size=6408 bytes

### REACH_DIAGNOSIS.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS.md` — modified 2026-06-23, size=9449 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS.md` — modified 2026-08-07, size=9449 bytes
  - `results/REACH_DIAGNOSIS.md` — modified 2026-05-15, size=9449 bytes

### REACH_DIAGNOSIS_V2.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS_V2.md` — modified 2026-06-23, size=6242 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS_V2.md` — modified 2026-08-07, size=6242 bytes
  - `results/REACH_DIAGNOSIS_V2.md` — modified 2026-05-16, size=6242 bytes

### REACH_DIAGNOSIS_V3.md (3 occurrences)

  - `archive/backups/ws_backup_0711/results/REACH_DIAGNOSIS_V3.md` — modified 2026-06-23, size=8918 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/REACH_DIAGNOSIS_V3.md` — modified 2026-08-07, size=8918 bytes
  - `results/REACH_DIAGNOSIS_V3.md` — modified 2026-05-16, size=8918 bytes

### README.md (12 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/Pointnet_Pointnet2_pytorch/README.md` — modified 2026-08-07, size=7982 bytes
  - `Backups/2026-08-07/Afford-Grasp/contact_graspnet_pytorch/README.md` — modified 2026-08-07, size=5901 bytes
  - `Backups/2026-08-07/Afford-Grasp/hsr_meshes/README.md` — modified 2026-08-07, size=524 bytes
  - `Backups/2026-08-07/Afford-Grasp/README.md` — modified 2026-08-07, size=8883 bytes
  - `Backups/2026-08-07/Afford-Grasp/YCB_Dataset/README.md` — modified 2026-08-07, size=1826 bytes
  - `contact_graspnet_pytorch/Pointnet_Pointnet2_pytorch/README.md` — modified 2026-03-04, size=7982 bytes
  - `contact_graspnet_pytorch/README.md` — modified 2026-03-04, size=5901 bytes
  - `figures/archive/fig_1_1_knife_version/README.md` — modified 2026-08-17, size=838 bytes
  - `hsr_meshes/README.md` — modified 2026-03-05, size=524 bytes
  - `README.md` — modified 2026-05-14, size=8883 bytes
  - `report_bundle_20260801_1611/README.md` — modified 2026-08-09, size=552 bytes
  - `YCB_Dataset/README.md` — modified 2026-03-04, size=1826 bytes

### reasoning_result.json (231 occurrences)

  - `archive/backups/ws_backup_0711/results/trial_20260301_150326_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_151833_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_152831_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153131_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153324_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260301_153407_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202801_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202822_scissors/reasoning_result.json` — modified 2026-06-23, size=136 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_202908_scissors/reasoning_result.json` — modified 2026-06-23, size=136 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204333_mug/reasoning_result.json` — modified 2026-06-23, size=127 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204726_mug/reasoning_result.json` — modified 2026-06-23, size=122 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204850_hammer/reasoning_result.json` — modified 2026-06-23, size=148 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_204942_hammer/reasoning_result.json` — modified 2026-06-23, size=155 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_205507_mug/reasoning_result.json` — modified 2026-06-23, size=117 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260303_205551_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_053620_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_053713_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_061906_hammer/reasoning_result.json` — modified 2026-06-23, size=134 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_123300_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_124212_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_124358_mug/reasoning_result.json` — modified 2026-06-23, size=118 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_124810_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_125146_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_125408_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130322_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130604_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130821_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_130939_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131200_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131547_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131735_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_131938_hammer/reasoning_result.json` — modified 2026-06-23, size=132 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132204_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132329_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132432_hammer/reasoning_result.json` — modified 2026-06-23, size=132 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_132608_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_133550_mug/reasoning_result.json` — modified 2026-06-23, size=118 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_133750_mug/reasoning_result.json` — modified 2026-06-23, size=118 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134014_mug/reasoning_result.json` — modified 2026-06-23, size=118 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134100_mug/reasoning_result.json` — modified 2026-06-23, size=118 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134201_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134459_hammer/reasoning_result.json` — modified 2026-06-23, size=134 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_134953_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_195711_hammer/reasoning_result.json` — modified 2026-06-23, size=132 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_195947_mug/reasoning_result.json` — modified 2026-06-23, size=148 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200345_mug/reasoning_result.json` — modified 2026-06-23, size=150 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200633_mug/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_200749_mug/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_201628_spoon/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_202957_pan/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260304_203246_cup/reasoning_result.json` — modified 2026-06-23, size=146 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_002649_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_004102_wine_glass/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260305_013436_bottle/reasoning_result.json` — modified 2026-06-23, size=128 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260411_225854_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174518_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174742_hammer/reasoning_result.json` — modified 2026-06-23, size=132 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_174852_bottle/reasoning_result.json` — modified 2026-06-23, size=139 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_175412_bottle/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_182730_mug/reasoning_result.json` — modified 2026-06-23, size=123 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_182849_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183000_bottle/reasoning_result.json` — modified 2026-06-23, size=136 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183111_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183221_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183331_bottle/reasoning_result.json` — modified 2026-06-23, size=139 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183435_mug/reasoning_result.json` — modified 2026-06-23, size=121 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183544_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183642_bottle/reasoning_result.json` — modified 2026-06-23, size=154 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183746_mug/reasoning_result.json` — modified 2026-06-23, size=121 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_183900_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184003_bottle/reasoning_result.json` — modified 2026-06-23, size=147 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184107_mug/reasoning_result.json` — modified 2026-06-23, size=120 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184215_hammer/reasoning_result.json` — modified 2026-06-23, size=131 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184324_bottle/reasoning_result.json` — modified 2026-06-23, size=154 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184426_mug/reasoning_result.json` — modified 2026-06-23, size=123 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184530_hammer/reasoning_result.json` — modified 2026-06-23, size=135 bytes
  - `archive/backups/ws_backup_0711/results/trial_20260608_184637_bottle/reasoning_result.json` — modified 2026-06-23, size=154 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_150326_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_151833_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_152831_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153131_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153324_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260301_153407_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202801_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202822_scissors/reasoning_result.json` — modified 2026-08-07, size=136 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_202908_scissors/reasoning_result.json` — modified 2026-08-07, size=136 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204333_mug/reasoning_result.json` — modified 2026-08-07, size=127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204726_mug/reasoning_result.json` — modified 2026-08-07, size=122 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204850_hammer/reasoning_result.json` — modified 2026-08-07, size=148 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_204942_hammer/reasoning_result.json` — modified 2026-08-07, size=155 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205507_mug/reasoning_result.json` — modified 2026-08-07, size=117 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260303_205551_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053620_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_053713_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_061906_hammer/reasoning_result.json` — modified 2026-08-07, size=134 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_123300_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124212_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124358_mug/reasoning_result.json` — modified 2026-08-07, size=118 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_124810_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125146_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_125408_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130322_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130604_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130821_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_130939_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131200_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131547_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131735_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_131938_hammer/reasoning_result.json` — modified 2026-08-07, size=132 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132204_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132329_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132432_hammer/reasoning_result.json` — modified 2026-08-07, size=132 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_132608_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133550_mug/reasoning_result.json` — modified 2026-08-07, size=118 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_133750_mug/reasoning_result.json` — modified 2026-08-07, size=118 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134014_mug/reasoning_result.json` — modified 2026-08-07, size=118 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134100_mug/reasoning_result.json` — modified 2026-08-07, size=118 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134201_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134459_hammer/reasoning_result.json` — modified 2026-08-07, size=134 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_134953_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195711_hammer/reasoning_result.json` — modified 2026-08-07, size=132 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_195947_mug/reasoning_result.json` — modified 2026-08-07, size=148 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200345_mug/reasoning_result.json` — modified 2026-08-07, size=150 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200633_mug/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_200749_mug/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_201628_spoon/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_202957_pan/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260304_203246_cup/reasoning_result.json` — modified 2026-08-07, size=146 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_002649_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_004102_wine_glass/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260305_013436_bottle/reasoning_result.json` — modified 2026-08-07, size=128 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260411_225854_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174518_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174742_hammer/reasoning_result.json` — modified 2026-08-07, size=132 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_174852_bottle/reasoning_result.json` — modified 2026-08-07, size=139 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_175412_bottle/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182730_mug/reasoning_result.json` — modified 2026-08-07, size=123 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_182849_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183000_bottle/reasoning_result.json` — modified 2026-08-07, size=136 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183111_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183221_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183331_bottle/reasoning_result.json` — modified 2026-08-07, size=139 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183435_mug/reasoning_result.json` — modified 2026-08-07, size=121 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183544_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183642_bottle/reasoning_result.json` — modified 2026-08-07, size=154 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183746_mug/reasoning_result.json` — modified 2026-08-07, size=121 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_183900_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184003_bottle/reasoning_result.json` — modified 2026-08-07, size=147 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184107_mug/reasoning_result.json` — modified 2026-08-07, size=120 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184215_hammer/reasoning_result.json` — modified 2026-08-07, size=131 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184324_bottle/reasoning_result.json` — modified 2026-08-07, size=154 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184426_mug/reasoning_result.json` — modified 2026-08-07, size=123 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184530_hammer/reasoning_result.json` — modified 2026-08-07, size=135 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/trial_20260608_184637_bottle/reasoning_result.json` — modified 2026-08-07, size=154 bytes
  - `results/trial_20260301_150326_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260301_151833_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260301_152831_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260301_153131_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260301_153324_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260301_153407_mug/reasoning_result.json` — modified 2026-03-01, size=127 bytes
  - `results/trial_20260303_202801_hammer/reasoning_result.json` — modified 2026-03-03, size=131 bytes
  - `results/trial_20260303_202822_scissors/reasoning_result.json` — modified 2026-03-03, size=136 bytes
  - `results/trial_20260303_202908_scissors/reasoning_result.json` — modified 2026-03-03, size=136 bytes
  - `results/trial_20260303_204333_mug/reasoning_result.json` — modified 2026-03-03, size=127 bytes
  - `results/trial_20260303_204726_mug/reasoning_result.json` — modified 2026-03-03, size=122 bytes
  - `results/trial_20260303_204850_hammer/reasoning_result.json` — modified 2026-03-03, size=148 bytes
  - `results/trial_20260303_204942_hammer/reasoning_result.json` — modified 2026-03-03, size=155 bytes
  - `results/trial_20260303_205507_mug/reasoning_result.json` — modified 2026-03-03, size=117 bytes
  - `results/trial_20260303_205551_mug/reasoning_result.json` — modified 2026-03-03, size=120 bytes
  - `results/trial_20260304_053620_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_053713_mug/reasoning_result.json` — modified 2026-03-04, size=120 bytes
  - `results/trial_20260304_061906_hammer/reasoning_result.json` — modified 2026-03-04, size=134 bytes
  - `results/trial_20260304_123300_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_124212_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_124358_mug/reasoning_result.json` — modified 2026-03-04, size=118 bytes
  - `results/trial_20260304_124810_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_125146_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_125408_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_130322_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_130604_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_130821_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_130939_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_131200_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_131547_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_131735_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_131938_hammer/reasoning_result.json` — modified 2026-03-04, size=132 bytes
  - `results/trial_20260304_132204_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_132329_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_132432_hammer/reasoning_result.json` — modified 2026-03-04, size=132 bytes
  - `results/trial_20260304_132608_mug/reasoning_result.json` — modified 2026-03-04, size=120 bytes
  - `results/trial_20260304_133550_mug/reasoning_result.json` — modified 2026-03-04, size=118 bytes
  - `results/trial_20260304_133750_mug/reasoning_result.json` — modified 2026-03-04, size=118 bytes
  - `results/trial_20260304_134014_mug/reasoning_result.json` — modified 2026-03-04, size=118 bytes
  - `results/trial_20260304_134100_mug/reasoning_result.json` — modified 2026-03-04, size=118 bytes
  - `results/trial_20260304_134201_mug/reasoning_result.json` — modified 2026-03-04, size=120 bytes
  - `results/trial_20260304_134459_hammer/reasoning_result.json` — modified 2026-03-04, size=134 bytes
  - `results/trial_20260304_134953_hammer/reasoning_result.json` — modified 2026-03-04, size=131 bytes
  - `results/trial_20260304_195711_hammer/reasoning_result.json` — modified 2026-03-04, size=132 bytes
  - `results/trial_20260304_195947_mug/reasoning_result.json` — modified 2026-03-04, size=148 bytes
  - `results/trial_20260304_200345_mug/reasoning_result.json` — modified 2026-03-04, size=150 bytes
  - `results/trial_20260304_200633_mug/reasoning_result.json` — modified 2026-03-04, size=147 bytes
  - `results/trial_20260304_200749_mug/reasoning_result.json` — modified 2026-03-04, size=147 bytes
  - `results/trial_20260304_201628_spoon/reasoning_result.json` — modified 2026-03-04, size=147 bytes
  - `results/trial_20260304_202957_pan/reasoning_result.json` — modified 2026-03-04, size=147 bytes
  - `results/trial_20260304_203246_cup/reasoning_result.json` — modified 2026-03-04, size=146 bytes
  - `results/trial_20260305_002649_hammer/reasoning_result.json` — modified 2026-03-05, size=131 bytes
  - `results/trial_20260305_004102_wine_glass/reasoning_result.json` — modified 2026-03-05, size=147 bytes
  - `results/trial_20260305_013436_bottle/reasoning_result.json` — modified 2026-03-05, size=128 bytes
  - `results/trial_20260411_225854_hammer/reasoning_result.json` — modified 2026-04-11, size=131 bytes
  - `results/trial_20260608_174518_mug/reasoning_result.json` — modified 2026-06-08, size=120 bytes
  - `results/trial_20260608_174742_hammer/reasoning_result.json` — modified 2026-06-08, size=132 bytes
  - `results/trial_20260608_174852_bottle/reasoning_result.json` — modified 2026-06-08, size=139 bytes
  - `results/trial_20260608_175412_bottle/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_182730_mug/reasoning_result.json` — modified 2026-06-08, size=123 bytes
  - `results/trial_20260608_182849_hammer/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_183000_bottle/reasoning_result.json` — modified 2026-06-08, size=136 bytes
  - `results/trial_20260608_183111_mug/reasoning_result.json` — modified 2026-06-08, size=120 bytes
  - `results/trial_20260608_183221_hammer/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_183331_bottle/reasoning_result.json` — modified 2026-06-08, size=139 bytes
  - `results/trial_20260608_183435_mug/reasoning_result.json` — modified 2026-06-08, size=121 bytes
  - `results/trial_20260608_183544_hammer/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_183642_bottle/reasoning_result.json` — modified 2026-06-08, size=154 bytes
  - `results/trial_20260608_183746_mug/reasoning_result.json` — modified 2026-06-08, size=121 bytes
  - `results/trial_20260608_183900_hammer/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_184003_bottle/reasoning_result.json` — modified 2026-06-08, size=147 bytes
  - `results/trial_20260608_184107_mug/reasoning_result.json` — modified 2026-06-08, size=120 bytes
  - `results/trial_20260608_184215_hammer/reasoning_result.json` — modified 2026-06-08, size=131 bytes
  - `results/trial_20260608_184324_bottle/reasoning_result.json` — modified 2026-06-08, size=154 bytes
  - `results/trial_20260608_184426_mug/reasoning_result.json` — modified 2026-06-08, size=123 bytes
  - `results/trial_20260608_184530_hammer/reasoning_result.json` — modified 2026-06-08, size=135 bytes
  - `results/trial_20260608_184637_bottle/reasoning_result.json` — modified 2026-06-08, size=154 bytes

### RUNBOOK.md (2 occurrences)

  - `archive/backups/ws_backup_0711/RUNBOOK.md` — modified 2026-07-06, size=1846 bytes
  - `Backups/2026-08-07/Afford-Grasp/RUNBOOK.md` — modified 2026-08-07, size=1846 bytes

### settings.json (2 occurrences)

  - `.vscode/settings.json` — modified 2026-03-05, size=47 bytes
  - `Backups/2026-08-07/Afford-Grasp/.vscode/settings.json` — modified 2026-08-07, size=47 bytes

### settings.local.json (2 occurrences)

  - `.claude/settings.local.json` — modified 2026-08-16, size=17673 bytes
  - `Backups/2026-08-07/Afford-Grasp/.claude/settings.local.json` — modified 2026-08-07, size=12577 bytes

### task-1-brief.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-1-brief.md` — modified 2026-08-07, size=12109 bytes
  - `.superpowers/sdd/task-1-brief.md` — modified 2026-07-13, size=14460 bytes

### task-1-report.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-1-report.md` — modified 2026-08-07, size=4206 bytes
  - `.superpowers/sdd/task-1-report.md` — modified 2026-07-13, size=8462 bytes

### task-2-brief.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-2-brief.md` — modified 2026-08-08, size=9728 bytes
  - `.superpowers/sdd/task-2-brief.md` — modified 2026-07-13, size=12915 bytes

### task-2-report.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-2-report.md` — modified 2026-08-07, size=7358 bytes
  - `.superpowers/sdd/task-2-report.md` — modified 2026-07-13, size=20348 bytes

### task-3-brief.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-3-brief.md` — modified 2026-08-07, size=9805 bytes
  - `.superpowers/sdd/task-3-brief.md` — modified 2026-07-13, size=7447 bytes

### task-3-report.md (2 occurrences)

  - `.superpowers/sdd/2026-08-07-dissertation-figures-storyboard-batch1/task-3-report.md` — modified 2026-08-07, size=4966 bytes
  - `.superpowers/sdd/task-3-report.md` — modified 2026-07-13, size=10378 bytes

### trials.csv (4 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=4
  - `Backups/2026-08-07/Afford-Grasp/trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=12
  - `report_bundle_20260801_1611/trials.csv` — modified 2026-08-01, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=11
  - `trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=12

### vlm_grid_handover_v2_raw.json (2 occurrences)

  - `experiments/vlm_grid/vlm_grid_handover_v2_raw.json` — modified 2026-07-15, size=7710 bytes
  - `vlm_grid_handover_v2_raw.json` — modified 2026-07-15, size=7710 bytes

### vlm_grid_raw.json (2 occurrences)

  - `experiments/vlm_grid/vlm_grid_raw.json` — modified 2026-07-15, size=23616 bytes
  - `vlm_grid_raw.json` — modified 2026-07-15, size=23616 bytes

### ycb_mass.json (2 occurrences)

  - `Backups/2026-08-07/Afford-Grasp/YCB_Dataset/scripts/ycb_mass.json` — modified 2026-08-07, size=1886 bytes
  - `YCB_Dataset/scripts/ycb_mass.json` — modified 2026-03-04, size=1886 bytes

### Call-outs requested

- **trials.csv** — 4 copies:
  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=4
  - `Backups/2026-08-07/Afford-Grasp/trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=12
  - `report_bundle_20260801_1611/trials.csv` — modified 2026-08-01, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=11
  - `trials.csv` — modified 2026-08-07, header=`timestamp,grasp,verdict,held,z_rise_m,hand_motor,contact_pos,stop_reason,lift_commanded,lift_reached,lift_executed,close_params,force_level,cage_motor,close_z,hold_margin,g1_xy,g2_pos_err,g2_ori_deg,servo_used,note`, rows=12
  - Verdict: headers match, but row counts DIFFER across copies.

- **place_run.csv** — 18 copies:
  - `archive/backups/HSR_logs_20260714_183749/place_run.csv` — modified 2026-07-19, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0706_1549_GRASP_OK/place_run.csv` — modified 2026-07-06, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0710_1447/place_run.csv` — modified 2026-07-10, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/place_run.csv` — modified 2026-07-10, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `archive/backups/ws_backup_0711/results/run_0712_servo_session/place_run.csv` — modified 2026-07-12, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0706_1549_GRASP_OK/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0710_1447/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0714_eject/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_servo_demo/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `Experiment_Logs/2026-08-07/place_run.csv` — modified 2026-08-07, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `report_bundle_20260801_1611/place_run.csv` — modified 2026-08-01, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - `run_0716_funnel/place_run.csv` — modified 2026-07-16, header=`grasp,score,arm_only_ok,base_x,base_y,base_yaw_rad,standoff_m,manip,collision_free,clearance_m,q_lift,q_flex,q_roll,q_wflex,q_wroll`, rows=25
  - Verdict: headers and row counts MATCH across all copies.

- **close_params.csv** — 7 copies:
  - `Backups/2026-08-07/Afford-Grasp/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Backups/2026-08-07/Afford-Grasp/results/run_0723_trials/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `Experiment_Logs/2026-08-07/close_params.csv` — modified 2026-08-07, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `report_bundle_20260801_1611/close_params.csv` — modified 2026-08-01, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - `run_0722_GRASP_OK/close_params.csv` — modified 2026-07-22, header=`grasp_id,part_width_m,cage_gap_m,cage_motor_rad,close_z,plane_z,obj_top_z,force_level,effort,hold_margin_rad,lift_m,requires_controlled_tilt,retreat,ok,note`, rows=25
  - Verdict: headers and row counts MATCH across all copies.

- **constraints.json** — 3 copies:
  - `constraints.json` — modified 2026-08-07, size=298 bytes
  - `Experiment_Logs/2026-08-07/constraints.json` — modified 2026-08-07, size=398 bytes
  - `run_0722_GRASP_OK/constraints.json` — modified 2026-07-22, size=324 bytes

- **gripper_gap_map.csv** — 7 copies:
  - `archive/backups/HSR_logs_20260714_183749/gripper_gap_map.csv` — modified 2026-07-19, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `Backups/2026-08-07/Afford-Grasp/results/run_0722_GRASP_OK/gripper_gap_map.csv` — modified 2026-08-07, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `gripper_gap_map.csv` — modified 2026-07-14, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `report_bundle_20260801_1611/gripper_gap_map.csv` — modified 2026-08-01, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - `run_0716_funnel/gripper_gap_map.csv` — modified 2026-07-16, header=`cmd_angle,motor_angle,gap_m`, rows=9
  - Verdict: headers and row counts MATCH across all copies.

- **grasp_px_probe.png** — 6 copies:
  - `archive/backups/HSR_logs_20260714_183749/grasp_px_probe.png` — modified 2026-07-19, 880x660, 565288 bytes
  - `Backups/2026-08-07/Afford-Grasp/grasp_px_probe.png` — modified 2026-08-07, 880x660, 599943 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/run_0716_funnel/grasp_px_probe.png` — modified 2026-08-07, 880x660, 526064 bytes
  - `grasp_px_probe.png` — modified 2026-08-01, 880x660, 599943 bytes
  - `report_bundle_20260801_1611/grasp_px_probe.png` — modified 2026-08-01, 880x660, 599943 bytes
  - `run_0716_funnel/grasp_px_probe.png` — modified 2026-07-16, 880x660, 526064 bytes

- **final_center_debug.png** — 9 copies:
  - `archive/backups/HSR_logs_20260714_183749/final_center_debug.png` — modified 2026-07-19, 880x660, 622797 bytes
  - `archive/backups/ws_backup_0711/results/run_0710_1521_center_fail/final_center_debug.png` — modified 2026-07-10, 880x660, 569127 bytes
  - `archive/backups/ws_backup_0711/results/run_0712_servo_session/final_center_debug.png` — modified 2026-07-12, 880x660, 622797 bytes
  - `Backups/2026-08-07/Afford-Grasp/final_center_debug.png` — modified 2026-08-07, 880x660, 617508 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/run_0710_1521_center_fail/final_center_debug.png` — modified 2026-08-07, 880x660, 569127 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/final_center_debug.png` — modified 2026-08-07, 880x660, 622797 bytes
  - `captures/final_center_debug.png` — modified 2026-07-10, 880x660, 569127 bytes
  - `final_center_debug.png` — modified 2026-07-28, 880x660, 581995 bytes
  - `report_bundle_20260801_1611/final_center_debug.png` — modified 2026-08-01, 880x660, 631332 bytes

- **peek_view.png** — 3 copies:
  - `Backups/2026-08-07/Afford-Grasp/peek_view.png` — modified 2026-08-07, 640x480, 387175 bytes
  - `peek_view.png` — modified 2026-07-28, 640x480, 379105 bytes
  - `report_bundle_20260801_1611/peek_view.png` — modified 2026-08-01, 640x480, 387175 bytes

- **NOTES_NEXT_SESSION.md** — 5 copies:
  - `archive/backups/ws_backup_0711/NOTES_NEXT_SESSION.md` — modified 2026-07-12, size=1094 bytes
  - `archive/backups/ws_backup_0711/results/run_0712_servo_session/NOTES_NEXT_SESSION.md` — modified 2026-07-12, size=1094 bytes
  - `Backups/2026-08-07/Afford-Grasp/NOTES_NEXT_SESSION.md` — modified 2026-08-07, size=4333 bytes
  - `Backups/2026-08-07/Afford-Grasp/results/run_0712_servo_session/NOTES_NEXT_SESSION.md` — modified 2026-08-07, size=1094 bytes
  - `NOTES_NEXT_SESSION.md` — modified 2026-07-16, size=4333 bytes
