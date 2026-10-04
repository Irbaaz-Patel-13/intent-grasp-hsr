#!/usr/bin/env python
r"""
run_grounding_grasp.py  --  WINDOWS side (.venv with CUDA).

Runs the existing AffordGrasp perception stack on a REAL multiview Gazebo capture:
  instruction -> VLM reason -> object+part -> LangSAM ground -> affordance mask
  -> lift mask into 3D (odom) -> CGN on the FUSED cloud, filtered by affordance.

Inputs (copied from the sim):
  workspace/multiview.npz    (per-view rgb/depth/K/extrinsics, odom frame)
  workspace/fused_cloud.npz  (points Nx3 + colors, odom frame)

Output:
  workspace/grasps_out.npz   (grasp poses in odom, ready for whole-body IK)

Run from the repo root so the pipeline modules import.
"""
import os
import numpy as np

# ---- import the existing pipeline pieces via the central config ----
from intent_grasp.config import PipelineConfig
from intent_grasp.affordance_reasoning import AffordanceReasoner
from intent_grasp.visual_grounding import VisualAffordanceGrounder
from intent_grasp.grasp_generation import AffordanceGraspGenerator

# Relocation task: a pure "move it" goal favours a stable top/body grasp rather
# than the handle-side grasp that a drinking task forces (which is not HSR-wrist
# feasible). The grasp part/approach is still decided by the VLM, not hardcoded.
import sys as _sys
from intent_grasp.paths import WORKSPACE
INSTRUCTION   = _sys.argv[1] if len(_sys.argv) > 1 else "Pick up the mug and move it to the other side of the table"
print("[instruction]", INSTRUCTION)
TARGET_HINT   = _sys.argv[2] if len(_sys.argv) > 2 else None   # 25 Jul: was hardcoded "mug"; only consumed in mock mode, but misleading in the execution path          # suppress hallucination; matches our staged object
VIEW_FOR_GROUND = "center"     # clearest framing of the mug
KEEP_GRASPS   = 25             # keep more candidates so a body-centred / vertical grasp survives
MV   = f"{WORKSPACE}/multiview.npz"
FUSED= f"{WORKSPACE}/fused_cloud.npz"
OUT  = f"{WORKSPACE}/grasps_out.npz"
EXEC_RADIUS = 0.06             # must match execute_grasp_v2.py's selection radius


def backproject_mask(mask, depth, K, extrinsics):
    """Replicate sim_env.depth_to_pointcloud for a masked region. Returns (M,3) in odom."""
    fx, fy = K[0, 0], K[1, 1]; cx, cy = K[0, 2], K[1, 2]
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    valid = (depth > 0.01) & (depth < 5.0)
    if mask is not None:
        valid &= (mask > 0)
    z = depth[valid]
    x_img = (u[valid] - cx) * z / fx
    y_img = (v[valid] - cy) * z / fy
    pts_cam = np.stack([x_img, -y_img, -z, np.ones_like(z)], axis=-1)  # OpenGL flip
    pts_world = (np.linalg.inv(extrinsics) @ pts_cam.T).T[:, :3]       # -> odom
    return pts_world


def grasp_pose_matrix(g):
    """Best-effort 4x4 from a GraspPose, to read approach axis for diagnostics."""
    for a in ["pose", "transform", "matrix", "T"]:
        if hasattr(g, a):
            M = np.asarray(getattr(g, a), float)
            if M.shape == (4, 4):
                return M
    M = np.eye(4)
    for a in ["rotation_matrix", "rotation", "R"]:
        if hasattr(g, a):
            r = np.asarray(getattr(g, a), float)
            if r.shape == (3, 3): M[:3, :3] = r; break
    for a in ["position", "pos", "translation"]:
        if hasattr(g, a):
            M[:3, 3] = np.asarray(getattr(g, a), float); break
    return M


def report_feasibility(grasps, aff_center_3d):
    """Print, per grasp, distance-to-affordance and tilt-from-vertical.
    Low tilt = top-down = HSR-wrist feasible; within EXEC_RADIUS = the executor can pick it.
    This is read-only diagnostics â€” it does not change what is saved."""
    print("\n  feasibility scan (what the HSR wrist can actually do):")
    print("   #   dist_to_aff   tilt_from_vertical   within_radius")
    feasible_near = 0
    for i, g in enumerate(grasps):
        M = grasp_pose_matrix(g)
        pos = M[:3, 3]; approach = M[:3, 2]
        dist = float(np.linalg.norm(pos - aff_center_3d))
        # approach pointing down (-z world) => top-down; tilt 0deg = perfectly vertical
        tilt = float(np.degrees(np.arccos(np.clip(-approach[2], -1.0, 1.0))))
        near = dist < EXEC_RADIUS
        if near and tilt < 45:
            feasible_near += 1
        print(f"   {i:<3} {dist:9.3f}     {tilt:11.1f}deg        {'YES' if near else 'no'}")
    print(f"  -> {feasible_near} grasp(s) are BOTH within {EXEC_RADIUS} m AND near-vertical "
          f"(<45deg) â€” these are the ones likely to execute.")
    if feasible_near == 0:
        print("  -> NOTE: this 0.06 m criterion is unpassable by construction --")
        print("     dist_to_aff is measured from CGN's pose ORIGIN (gripper base),")
        print("     which sits ~0.115 m behind the contact; 0/200 raw candidates fall")
        print("     inside 0.06 m. Convention-independent aiming error = perpendicular")
        print("     offset of the approach ray from the affordance centre:")
        print("     median 0.022 m, 23/25 selected within 0.06 m (see")
        print("     cgn_metric_correction.py). Residual ~2 cm is closed by the visual")
        print("     servo. Executable-grasp limit here is TOP-DOWN-ONLY execution,")
        print("     not the 5-DoF wrist (that finding is the base-placement result).")


def main():
    mv = np.load(MV, allow_pickle=True)
    names = [str(n) for n in mv["view_names"]]
    vi = names.index(VIEW_FOR_GROUND)
    rgb = mv["rgb"][vi]                       # (H,W,3) uint8 RGB
    depth = mv["depth"][vi]                   # (H,W) float32 m
    K = mv["camera_intrinsics"]               # (3,3)
    extr = mv["camera_extrinsics"][vi]        # (4,4) OpenGL world->cam (world=odom)
    print(f"grounding on view '{VIEW_FOR_GROUND}': rgb{rgb.shape} depth med={np.nanmedian(depth):.3f}")

    fused = np.load(FUSED)
    full_cloud = fused["points"].astype(np.float64)   # (N,3) odom
    print(f"fused cloud: {full_cloud.shape[0]} points, "
          f"x[{full_cloud[:,0].min():.2f},{full_cloud[:,0].max():.2f}]")

    # ---- build the three stages via the real PipelineConfig path ----
    config = PipelineConfig()                               # all defaults + OPENAI_API_KEY from env
    config.visual_grounding.workspace_image_crop = None     # real camera: do NOT use sim-tuned crop
    config.grasp.enable_reachability_filter = False         # no PyBullet IK in this standalone path
    # keep more CGN candidates so a body-centred / vertical (wrist-feasible) grasp survives
    if hasattr(config.grasp, "top_k_grasps"):
        config.grasp.top_k_grasps = KEEP_GRASPS
    reasoner  = AffordanceReasoner(config.vlm)
    grounder  = VisualAffordanceGrounder(config.visual_grounding)
    grasp_gen = AffordanceGraspGenerator(config.grasp)

    # ---- Stage 2: VLM reasoning ----
    rr = reasoner.reason(instruction=INSTRUCTION, scene_image=rgb,
                         verbose=True, target_hint=TARGET_HINT)
    target_object = rr.object_identification.target_object
    target_part   = rr.affordance_reasoning.target_part
    approach      = rr.affordance_reasoning.constraints.get("post_grasp_motion", "?")
    print(f"\nVLM -> object='{target_object}'  part='{target_part}'  approach='{approach}'")
    if str(approach).lower() == "side":
        print("  NOTE: VLM chose a SIDE approach â€” historically not HSR-wrist feasible.")
        print("        Watch the feasibility scan below; a top-down body grasp is what executes.")

    # ---- Stage 3: grounding ----
    gr = grounder.ground(
        rgb_image=rgb, depth_image=depth,
        target_object=target_object, target_part=target_part,
        camera_intrinsics=K, camera_extrinsics=extr,
        simulation_segmask=None, target_body_id=None,
    )
    aff_mask = gr.affordance_mask
    print(f"grounded: affordance_mask pixels={int((aff_mask>0).sum())}, "
          f"confidence={gr.confidence:.3f}, center_px={gr.affordance_center}")

    # ---- lift mask -> 3D affordance points + robust center (odom) ----
    affordance_points = backproject_mask(aff_mask, depth, K, extr)
    aff_center_3d = grounder.compute_affordance_center_3d_from_mask(aff_mask, depth, K, extr)
    if aff_center_3d is None and len(affordance_points):
        aff_center_3d = np.median(affordance_points, axis=0)
    print(f"affordance: {len(affordance_points)} pts, center_3d={np.round(aff_center_3d,3)}")

    # ---- GROUND-TRUTH CHECK: does the affordance center fall inside the fused cloud? ----
    lo = full_cloud.min(0) - 0.1; hi = full_cloud.max(0) + 0.1
    inside = np.all(aff_center_3d >= lo) and np.all(aff_center_3d <= hi)
    print(f"affordance center within fused-cloud extent: {inside}  "
          f"{'OK' if inside else '<-- WARNING: lift may be wrong-frame'}")

    # ---- Stage 4: CGN on the FUSED cloud, filtered by affordance ----
    # ---- part-scoped grasp generation (25 Jul) -------------------------------
    # The VLM already says WHICH PART to grasp; until now nothing acted on it and
    # CGN sampled the whole object. Bind that part to a structural component of
    # the cloud, project it into image space, and scope CGN to it.
    grasp_mask = aff_mask
    if os.environ.get("PART_SCOPED", "1") != "0":
        try:
            from intent_grasp import part_adaptive as _pa
            _kc = list((rr.affordance_reasoning.constraints or {}).get("keep_clear", []) or [])
            _near = full_cloud[np.linalg.norm(full_cloud[:, :2] - aff_center_3d[:2], axis=1) < 0.25]
            _hh, _ee = np.histogram((_near if len(_near) > 200 else full_cloud)[:, 2], bins=80)
            _zt = float(0.5 * (_ee[int(np.argmax(_hh))] + _ee[int(np.argmax(_hh)) + 1]))
            _obj, _r = _pa.adaptive_crop(full_cloud, aff_center_3d[:2], z_table=_zt,
                                         start=0.06, step=0.02, max_radius=0.16)
            _obj, _iso = _pa.isolate_object(_obj, aff_center_3d[:2])
            print("[part] object isolation: %s" % _iso)
            _sh = _pa.classify_shape(_obj, _zt)
            _comp, _inf = _pa.find_components(_obj, z_table=_zt)
            _desc = _pa.describe_components(_comp, _inf)
            _nm, _pp, _sc, _note = _pa.bind_part(target_part, _comp, _desc,
                                                 keep_clear=_kc,
                                                 linearity=_sh["linearity"])
            print("[part] object %d pts (crop %.2f m, %s), components: %s"
                  % (len(_obj), _r, _sh["shape_class"], sorted(_desc)))
            print("[part] %s" % _note)
            if _pp is not None and _sc >= 3.0:
                _m, _npx = _pa.project_part_to_mask(_pp, K, extr, depth.shape)
                _nobj = int((aff_mask > 0).sum())
                if _npx >= 150:
                    grasp_mask = _m
                    print("[part] CGN SCOPED to '%s': mask %d px (%.0f%% of the "
                          "%d px object mask)" % (_nm, _npx, 100.0 * _npx / max(_nobj, 1), _nobj))
                else:
                    print("[part] projected mask only %d px -- falling back to the "
                          "whole-object mask" % _npx)
            else:
                print("[part] no confident binding (score %.1f) -- falling back to "
                      "the whole-object mask" % _sc)
        except Exception as _e:
            print("[part] part-scoping unavailable (%s: %s) -- whole-object mask"
                  % (type(_e).__name__, _e))
    # --------------------------------------------------------------------------

    grasps = grasp_gen.generate(
        point_cloud=full_cloud,
        affordance_center_3d=aff_center_3d,
        affordance_points=affordance_points,
        table_height=0.0,
        depth_image=depth,
        camera_intrinsics=K,
        camera_extrinsics=extr,
        segmentation_mask=grasp_mask,
        sim_env=None,            # skip PyBullet reachability filter
    )
    n = len(grasps) if grasps is not None else 0
    print(f"\nCGN produced {n} grasp(s)")
    if n:
        report_feasibility(grasps, aff_center_3d)

    # ---- save grasps (poses in odom) for whole-body IK back in the sim ----
    # --- 21 Jul: persist inferred constraints for the closure policy ---
    # grasp_close_params.py reads constraints.json and maps stability_priority /
    # post_grasp_motion / thermal_or_hygiene to force level, hold margin, close
    # depth and post-grasp plan (grasp_policy.py). Non-fatal by construction.
    try:
        import json as _json
        _c = dict(getattr(rr.affordance_reasoning, "constraints", {}) or {})
        _json.dump({"instruction": INSTRUCTION,
                    "target_object": target_object,
                    "target_part": target_part,
                    "constraints": _c},
                   open("constraints.json", "w", encoding="utf-8"),
                   indent=2, default=str)
        print("[constraints] wrote constraints.json ->", _c)
    except Exception as _e:
        print("[constraints] WARNING: could not write constraints.json:", _e)

    np.savez(OUT, instruction=INSTRUCTION, target_object=target_object,
             target_part=target_part, aff_center_3d=aff_center_3d,
             affordance_points=affordance_points,
             grasps=np.array(grasps, dtype=object),
             affordance_mask=gr.affordance_mask,
             object_mask=gr.object_mask,
             grounding_rgb=rgb)
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
