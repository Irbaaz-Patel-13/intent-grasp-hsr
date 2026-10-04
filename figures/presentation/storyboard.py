"""
storyboard.py -- low-resolution 13-panel contact sheet, the blueprint every
full-resolution figure is checked against (design spec Sec 11). Each
thumbnail states its Scientific claim / Real data source / Illustration
technique / Expected visual composition, per spec.

Run: python storyboard.py
Output: generated_assets/storyboard/storyboard.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as fs

STORYBOARD_ENTRIES = [
    dict(n=1, title="Acquisition",
         claim="The system captures a real, calibrated RGB-D observation of the scene.",
         source="head_capture_real.npz (rgb, depth, K, tf_trans/quat)",
         technique="Annotated RGB + depth colormap + camera frustum diagram",
         composition="3-panel row: RGB | depth | frustum/coordinate-frame diagram"),
    dict(n=2, title="Grounding",
         claim="Language grounding correctly localizes the target object and part from a natural instruction.",
         source="grasps_out.npz (instruction, target_object, target_part, object_mask)",
         technique="Annotated RGB with bbox + mask overlay",
         composition="single annotated RGB panel, bbox derived from object_mask, instruction as caption"),
    dict(n=3, title="Segmentation",
         claim="The target object is cleanly separated from the background.",
         source="grasps_out.npz (object_mask)",
         technique="Mask / extracted-object / background-removed triptych",
         composition="3-panel row: pixel mask | cutout | silhouette"),
    dict(n=4, title="Point Cloud",
         claim="RGB-D fusion produces a coherent 3D reconstruction of the object and scene.",
         source="fused_cloud.npz (241,818 pts), multiview.npz",
         technique="Open3D offscreen render with camera rays + coordinate frame",
         composition="single 3D render panel, one fixed camera angle"),
    dict(n=5, title="Affordance Reasoning",
         claim="Reasoning yields a 3D affordance anchor point even where 2D part-level segmentation collapses toward the whole object -- a documented, real limitation of language-based part grounding on this object, not a clean candidate/rejected region split.",
         source="grasps_out.npz (object_mask, affordance_mask, aff_center_3d); corroborated by report_assets/PART_NAMING_ABLATION.csv and PERCEPTION_EVIDENCE.md",
         technique="Honest-limitation diagram: object_mask vs affordance_mask overlay (96.97% IoU, measured) plus the 3D anchor point that downstream grasp ranking actually uses",
         composition="RGB + near-identical mask overlay + aff_center_3d marker + caption stating the measured overlap explicitly, not a fabricated region split"),
    dict(n=6, title="Grasp Candidates",
         claim="A real grasp-generation run produced 25 scored candidate poses -- but the candidate actually executed on hardware (#24) is NOT the top-ranked one by this ranking (rank 25/25); a different, downstream feasibility criterion (Figure 7) determined selection.",
         source="grasps_plain.npz (25 real poses, combined_score range [2.36, 3.14], via fig_data.load_grasp_candidates)",
         technique="Open3D render, object-scale framing, candidates as spheres colored by combined_score, approach vectors derived from real pose rotations, executed candidate highlighted",
         composition="single 3D render (candidates + local point-cloud context) + caption stating candidate 24's real rank explicitly, not implying top-score=selected"),
    dict(n=7, title="Grasp Feasibility",
         claim="Candidate 24's real manipulability (0.175) is the maximum among all 25 real candidates and clears the real hsr_preflight.py C4 gate threshold (manip_min=0.10) -- NOT a progressive collision/reachability/IK filtering funnel, which this trial's own data does not support (collision_free and arm_only_ok are constant across all 25 candidates).",
         source="place_run.csv (25 real manip values, via fig_data.load_grasp_candidates); scripts/robot/hsr_preflight.py (real manip_min=0.10 C4 gate)",
         technique="Real quantitative bar chart: manipulability per candidate index vs. the real threshold line, executed candidate highlighted",
         composition="25-bar chart, real manip values, threshold line + callout, explicit caption that collision_free/arm_only_ok/clearance_m are not shown as filters (constant/sentinel for this trial)"),
    dict(n=8, title="Motion Planning",
         claim="Collision-aware base placement, gated by a real keep-out clearance computed from captured scene geometry, converts an unreachable target into a reachable one.",
         source="place_run.csv (25 real base-placement candidates), place_run_map.png; scripts/robot/hsr_base_placement.py (BASE_CLEAR=0.32m, real algorithm); DEMO_RUNBOOK.md/CODEBASE_GUIDE.md (documented 0/25->25/25 capability, general claim -- not this trial's own before/after, which only has the after state)",
         technique="2D top-down map: real base candidates + real keep-out cells from the real point cloud",
         composition="place_run_map.png-style render + keep-out cell overlay + documented-capability callout (correctly attributed, not overclaimed as this trial's raw log)"),
    dict(n=9, title="Execution Sequence",
         claim="The real GRASP_OK/FAILED verdict is determined by three explicit, hardware-calibrated safety gates (G1 base-settled, G2 palm-vs-FK, G3 lift-verify), not simply whether the arm moved.",
         source="trials.csv (real per-trial g1_xy, g2_pos_err, g2_ori_deg, z_rise_m, hand_motor); scripts/robot/execute_place_grasp_raw.py (exact G1/G2/G3 predicates, G3 eps=-0.885 calibrated 2026-07-06)",
         technique="Gate-flow diagram (G1->G2->G3) annotated with one real trial's actual values -- diagrammatic staging, real gate numbers",
         composition="three-gate flow diagram, real pass/fail values from trial 12, explicitly labeled as reconstructed sequencing (no execution photographs exist)"),
    dict(n=10, title="Visual Servo Correction",
         claim="A real empirical Jacobian, bootstrapped from measured odometry displacement and refined by an explicit Broyden update each iteration, reduces real image-space pixel error across multiple real trials.",
         source="trials.csv (trial 9: 46.9->12.7px; trial 12: 17.4px residual); DEMO_RUNBOOK.md (47->13px in four iterations); scripts/robot/hsr_final_center.py (Broyden update, spot-verified); real hand-camera debug photos: scripts/robot/results/run_0712_servo_session/final_center_debug.png, run_0710_1521_center_fail/final_center_debug.png (two independent real sessions, one a documented failure)",
         technique="Real hand-camera photos (honestly captioned by session) + real cross-trial before/after quantitative panel -- NOT a fabricated per-iteration curve (no continuous convergence trace exists anywhere in the evidence)",
         composition="two real debug-frame photos + bar/dumbbell chart of real trial 9/12 pixel residuals"),
    dict(n=11, title="Successful Experiment",
         claim="A specific, real, fully autonomous trial (no hand-placement) achieved a verified grasp and lift, passing all three real safety gates.",
         source="trials.csv (trials 9-12, 2026-08-01, GRASP_OK, servo_used=yes, explicit autonomous/no-hand-placing notes)",
         technique="Real Open3D point-cloud/grasp-pose render (same style as Figures 4/6) + quantitative metrics panel",
         composition="scene render (real geometry, not a photo) + metrics callout box (real z_rise_m, hand_motor, gate values) + G1/G2/G3 pass indicators"),
    dict(n=12, title="Failure Analysis",
         claim="Specific, real hardware incidents each drove a specific, verifiable code fix -- genuine engineering self-correction, independently spot-verified, not narrative dressing.",
         source="trials.csv (trials 1 ABORT_, 3 ABORT_, 4 HELD_LIFT_FAULT, 6 -- explicitly references 'incident #10'); scripts/robot/execute_place_grasp_raw.py (incidents #8-#12 + 27-Jul lift-fault chain, all spot-verified against source); NOTES_NEXT_SESSION.md (real bumper-contact event, 2026-07-11)",
         technique="Incident-card timeline (what/why/fix), labeled as code-comment/documentation evidence, not photographed -- does not claim a confirmed root-cause mapping for trials 1/3/4 individually (only trial 6 -> incident #10 is independently confirmed)",
         composition="2-3 incident cards (#10, hardware-confirmed; 27-Jul lift-fault chain, explains the real G3 threshold in Figs 9/11) with explicit what/why/fix structure"),
    dict(n=13, title="Pipeline Summary",
         claim="The 12 preceding figures compose one coherent, end-to-end real pipeline.",
         source="derived from Figures 1-12 (no new data)",
         technique="Icon-based flow diagram using shared figstyle iconography",
         composition="vertical flow: 10 stage icons connected top-to-bottom"),
]


def render_storyboard(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("storyboard"), "storyboard.png")
    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.THUMB_DPI, facecolor=fs.SLIDE_BG)
    n_cols, n_rows = 4, 4
    for entry in STORYBOARD_ENTRIES:
        ax = fig.add_subplot(n_rows, n_cols, entry["n"])
        ax.set_facecolor(fs.CALLOUT_BG)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(fs.FAINT)
        ax.set_title(f"{entry['n']:02d}  {entry['title']}", **fs.SECTION, loc="left")
        caption = (f"Claim: {entry['claim']}\n"
                   f"Source: {entry['source']}\n"
                   f"Technique: {entry['technique']}\n"
                   f"Composition: {entry['composition']}")
        ax.text(0.02, 0.92, caption, transform=ax.transAxes, va="top", ha="left",
                 fontsize=5.2, color=fs.INK, wrap=True, family=fs.FONT)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.02, wspace=0.12, hspace=0.35)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    path = render_storyboard()
    print(f"storyboard written to {path}")
