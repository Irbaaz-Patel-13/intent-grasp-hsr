#!/usr/bin/env python
r"""
hand_part_grounding.py -- LAPTOP side, offline (pure numpy + repo's existing
model wrappers). No robot/ROS code here.

Grounds the graspable PART (not just the object) on the close-up hand-camera
view, lifts it into 3D by projecting the fused scene cloud into the hand
camera and intersecting with the part mask, then PCA-classifies the part's
3D shape to decide a grasp strategy.

Pipeline
--------
  1. VLM reasoning: the existing AffordanceReasoner (affordance_reasoning.py)
     turns the instruction into (target_object, target_part) -- reused as-is,
     not reimplemented.
  2. Object grounding: the existing VisualAffordanceGrounder / LangSAM
     loading pattern (visual_grounding.py) segments the whole OBJECT (Pass 1
     of _ground_with_langsam, gr.object_mask) in the hand-camera RGB. This
     replaces the former reliance on LangSAM's part-level text prompt
     (which reliably collapses to the whole object) and a VLM/Set-of-Marks
     part-selection fallback -- part-level selection is now done by pure
     geometry (part_decomposition.py, step 3 below), not by masking.
  3. 3D lift + geometric part decomposition: fused_cloud.npz points within
     PROXIMITY_M of aff_center_3d (grasps_plain.npz) are re-expressed in the
     base_link frame AT HAND-VIEW TIME (the base moves between the head
     capture and the hand view -- see transform_capture_to_view()), then
     projected into the hand camera using K and the base_link(at-view-time)
     -> camera TF, and intersected with the object mask -> the object's 3D
     points (in both the base_link-at-head-capture-time frame, "capture", and
     the base_link-at-view-time frame, "view"). The capture-frame points seed
     part_decomposition.py's geometric classifier (rim/interior/body/handle/
     unclassified via support-plane removal + radial/height thresholds +
     DBSCAN on the handle's lateral coherence), which selects the part for
     this instruction -- see docs/superpowers/plans/
     2026-07-13-geometric-part-decomposition.md.
  4. Shape policy: PCA on the selected part's points (transformed to view
     frame) classifies it as elongated / flat (disc-like) / bulky, and a
     width gate rejects parts too wide for the gripper.

Inputs (workspace/):
  hand_view_real.npz : rgb (H,W,3) uint8, K (3,3) float, tf_trans (3,) float,
                        tf_quat (4,) float [x,y,z,w], base_pose_capture (3,)
                        float [x,y,theta] (odom, at head-capture time),
                        base_pose_view (3,) float [x,y,theta] (odom, at this
                        hand-view time).
                        NOTE (found by debug_hand_projection.py): this capture's
                        K is all zeros (never populated) -- substituted here
                        with hand_view.npz's simulated K (same camera model,
                        matches the visible wide-FOV/fisheye lens).
                        NOTE 2 (superseded finding): an earlier 5-hypothesis
                        sweep concluded tf_quat/tf_trans was a base_link <-
                        camera (reverse) transform. That conclusion was an
                        artifact of comparing clouds across two DIFFERENT
                        base_link frames (the base moved ~0.4 m + yawed ~13
                        degrees between the head capture that produced
                        fused_cloud.npz and this hand view) -- the "reverse"
                        hypothesis only matched because its error partially
                        cancelled the frame mismatch. Frame composition on a
                        fresh capture confirmed hypothesis A: tf_trans/tf_quat
                        is the camera's pose in base_link-at-view-time,
                        p_cam = R.T @ (p_base - t), quat [x,y,z,w], and
                        hand_camera_frame is ALREADY optical -- no ROS
                        link->optical correction. See project_to_camera() and
                        transform_capture_to_view() below.
                        NOTE 3: this run's head capture also has a measured
                        odom-frame placement bias (~7.9 cm x, ~1.2 cm y) --
                        see load_refine_delta_odom() below.
  fused_cloud.npz     : points (N,3) float64, base_link-at-head-capture-time frame
  grasps_plain.npz    : aff_center_3d (3,) float64, base_link-at-head-capture-time frame

Output:
  part_grasp.npz      : part_points (base_link-at-hand-view-time frame),
                         part_centroid, pca_eigvals, pca_eigvecs,
                         shape_class, grasp_type, ideal_type, minor_axis_width,
                         width_ok, selected_part, part_names, part_counts,
                         part_centroids
  part_grasp_debug.png: 3-panel figure -- RGB+object mask overlay, projected
                        cloud on the image, 3D classified parts (all buckets
                        colored, selected part highlighted) with PCA axes.

Usage:
  python hand_part_grounding.py "I want to drink some coffee"
  python hand_part_grounding.py "Wash the inside of the mug" --target mug
"""
import sys
import argparse

import numpy as np
from scipy.spatial.transform import Rotation
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 -- registers the 3d projection

from intent_grasp.config import PipelineConfig
from intent_grasp.affordance_reasoning import AffordanceReasoner
from intent_grasp.visual_grounding import VisualAffordanceGrounder
from intent_grasp import part_decomposition as pd
from intent_grasp.paths import WORKSPACE
HAND_NPZ     = f"{WORKSPACE}/hand_view_real.npz"
HAND_SIM_NPZ = f"{WORKSPACE}/hand_view.npz"
FUSED_NPZ    = f"{WORKSPACE}/fused_cloud.npz"
GRASPS_NPZ   = f"{WORKSPACE}/grasps_plain.npz"
OUT_NPZ      = f"{WORKSPACE}/part_grasp.npz"
OUT_PNG      = f"{WORKSPACE}/part_grasp_debug.png"

PROXIMITY_M   = 0.20   # keep fused-cloud points within this radius of aff_center_3d
MIN_INTERSECT = 100    # abort if fewer than this many part points survive the mask
WIDTH_GATE_M  = 0.12   # reject the grasp if the minor-axis width exceeds this

REFINE_DELTA_TXT = f"{WORKSPACE}/refine_delta.txt"


def _yaw_rotation_matrix(theta):
    """Rotation matrix for a planar (z-axis) yaw of theta radians."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s, 0.],
        [s,  c, 0.],
        [0., 0., 1.],
    ])


def transform_capture_to_view(points, base_pose_capture, base_pose_view,
                               delta_odom=None):
    """
    Re-express points from the base_link frame AT HEAD-CAPTURE TIME (the
    frame fused_cloud.npz / grasps_plain.npz are stored in) into the
    base_link frame AT HAND-VIEW TIME (the frame hand_view_real.npz's
    tf_trans/tf_quat are relative to). The robot base translates and yaws
    (planar motion, z unchanged) between the two captures, so treating the
    two base_link frames as identical -- as earlier code implicitly did --
    silently mixes frames; this is the actual root cause of the old
    "34 cm from target" / hypothesis-E-only-works finding.

    base_pose_capture / base_pose_view: (x, y, theta) in odom.
    delta_odom: optional (3,) odom-frame correction (see
    load_refine_delta_odom()) added once the points are in odom, before the
    odom -> view-time-base_link step -- it corrects a head-capture placement
    bias, so it belongs in odom, not in either base_link frame.
    """
    xc, yc, tc = base_pose_capture
    xv, yv, tv = base_pose_view
    p_odom = points @ _yaw_rotation_matrix(tc).T + np.array([xc, yc, 0.])
    if delta_odom is not None:
        p_odom = p_odom + delta_odom
    p_view = (p_odom - np.array([xv, yv, 0.])) @ _yaw_rotation_matrix(-tv).T
    return p_view


def load_refine_delta_odom(hv):
    """
    Load the odom-frame (dx, dy) correction for the measured head-capture
    placement bias (this run: the fused cloud/aff_center_3d sit ~7.9 cm off
    in odom x and ~1.2 cm off in odom y from the mug's true position, per
    live measurement on the robot -- see project_cgn_diagnostic_findings
    memory). Order: hv['refine_delta_odom'] npz key, then refine_delta.txt,
    else (0, 0, 0) with a loud warning -- skipping this silently
    reintroduces that bias into every projection.
    """
    if "refine_delta_odom" in hv.files:
        d = np.asarray(hv["refine_delta_odom"], dtype=np.float64)
        return np.array([d[0], d[1], 0.0])
    try:
        with open(REFINE_DELTA_TXT) as f:
            dx, dy = (float(x) for x in f.read().strip().split(","))
        return np.array([dx, dy, 0.0])
    except FileNotFoundError:
        print("[hand_part_grounding] WARNING: no refine_delta_odom in npz and "
              f"no {REFINE_DELTA_TXT} found -- proceeding WITHOUT the odom-frame "
              "bias correction. Projections will be off by the known head-"
              "capture placement bias.")
        return np.zeros(3)


def load_base_poses(hv):
    """
    Load base_pose_capture / base_pose_view (x, y, theta in odom) from the
    hand-view npz. Required by transform_capture_to_view() to correct for
    base motion between the head capture (fused_cloud.npz) and this hand
    view. Older captures predate this field -- abort rather than silently
    assuming the base didn't move (see transform_capture_to_view() docstring).
    """
    if "base_pose_capture" not in hv.files or "base_pose_view" not in hv.files:
        sys.exit(
            "ABORT: hand_view_real.npz has no base_pose_capture/base_pose_view "
            "-- this is an old capture from before base-motion correction was "
            "added. Recapture with the updated capture script before running "
            "this pipeline."
        )
    base_pose_capture = hv["base_pose_capture"].astype(np.float64)
    base_pose_view = hv["base_pose_view"].astype(np.float64)
    if np.any(np.isnan(base_pose_capture)) or np.any(np.isnan(base_pose_view)):
        sys.exit(
            "ABORT: base_pose_capture/base_pose_view is NaN -- this is an old "
            "capture from before base-motion correction was populated. "
            "Recapture with the updated capture script before running this "
            "pipeline."
        )
    return base_pose_capture, base_pose_view


def project_to_camera(points, K, tf_trans, tf_quat):
    """
    Project base_link-at-view-time-frame points into the hand camera's pixel
    plane, using hypothesis A (confirmed convention -- tf_trans/tf_quat is
    the camera's pose in base_link, translation in base coordinates,
    hand_camera_frame is already optical so no ROS link->optical correction
    is applied):
        p_cam = R.T @ (p_base - t)
        pixel_homog = K @ p_cam
    Points passed in MUST already be in the base_link frame at hand-view
    time -- see transform_capture_to_view().
    Returns (pixels (M,2) float [u, v], z_cam (M,) float). Caller must filter
    z_cam > 0 (in front of the camera) before trusting the pixel coordinates.
    """
    R = Rotation.from_quat(tf_quat).as_matrix()   # tf_quat = [x, y, z, w]
    p_cam = (points - tf_trans) @ R               # row-vector form of R.T @ (p_base - t)
    proj = p_cam @ K.T                            # row-vector form of K @ p_cam
    z_cam = p_cam[:, 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        u = proj[:, 0] / z_cam
        v = proj[:, 1] / z_cam
    return np.stack([u, v], axis=1), z_cam


def classify_part_shape(part_points):
    """
    PCA-classify a part's 3D points using the standard linearity / planarity /
    sphericity decomposition of the sorted covariance eigenvalues
    (Weinmann et al., 2015; they sum to 1 so the shape class is whichever
    is largest):
        linearity   = (l1 - l2) / l1   -> one dominant axis  = elongated
        planarity   = (l2 - l3) / l1   -> two dominant axes  = flat / disc
        sphericity  =  l3 / l1         -> three comparable   = bulky

    Returns (centroid, eigvals_desc, eigvecs_desc, shape_class, minor_axis_width).
    eigvecs_desc columns are the principal axes sorted major -> minor.
    minor_axis_width is the point extent along the smallest-variance axis
    (the thinnest cross-section -- what the gripper has to close around).
    """
    centroid = part_points.mean(axis=0)
    centered = part_points - centroid
    cov = np.cov(centered, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(cov)        # ascending order
    order = np.argsort(-eigvals)                  # sort descending: l1 >= l2 >= l3
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    l1, l2, l3 = np.maximum(eigvals, 1e-12)
    linearity = (l1 - l2) / l1
    planarity = (l2 - l3) / l1
    sphericity = l3 / l1

    scores = {"elongated": linearity, "flat": planarity, "bulky": sphericity}
    shape_class = max(scores, key=scores.get)

    minor_axis = eigvecs[:, 2]
    proj = centered @ minor_axis
    minor_axis_width = float(proj.max() - proj.min())

    print(f"  PCA eigvals (desc): {eigvals}")
    print(f"  linearity={linearity:.3f}  planarity={planarity:.3f}  "
          f"sphericity={sphericity:.3f}  -> shape_class='{shape_class}'")
    print(f"  minor-axis width = {minor_axis_width:.3f} m")

    return centroid, eigvals, eigvecs, shape_class, minor_axis_width


def decide_grasp_type(shape_class, minor_axis_width, part_points):
    """
    Apply the requested grasp-type policy:
        rim/flat            -> "top_down"
        upright bulky body  -> "horizontal_base"
        width gate: reject (append _REJECTED_WIDTH) if minor_axis_width
            exceeds WIDTH_GATE_M

    The policy doesn't specify a type for "elongated" (e.g. a handle/rod) or
    for a bulky-but-not-upright part; both are extended here with a printed
    NOTE so the assumption is visible rather than silently applied:
        elongated          -> "top_down" AT THE PART CENTROID. The
                               kinematically natural grasp for an elongated
                               part is a side approach perpendicular to the
                               long axis, but the HSR's 5-DoF wrist has no
                               wrist yaw, so arbitrary-orientation side
                               approaches were proven unreachable in this
                               project -- executing one would just fail on
                               the real robot. ideal_type still reports
                               "side_grasp" so the report shows what an
                               unconstrained arm would have done.
        bulky, not upright  -> "top_down" (safest default)

    "Upright" is judged from the axis-aligned z-extent vs the horizontal
    (x/y) extent in base_link frame (z is up), not from the PCA axes, since
    PCA axes needn't align with world-up for a near-isotropic (bulky) cluster.

    Returns (grasp_type, ideal_type, upright, width_ok). ideal_type is the
    kinematics-unconstrained grasp choice; grasp_type is what's actually
    commanded (identical to ideal_type except for the elongated case above,
    and both get the same width-gate rejection suffix).
    """
    pmin, pmax = part_points.min(axis=0), part_points.max(axis=0)
    z_extent = pmax[2] - pmin[2]
    xy_extent = max(pmax[0] - pmin[0], pmax[1] - pmin[1])
    upright = bool(z_extent > xy_extent)

    if shape_class == "flat":
        ideal_type = grasp_type = "top_down"
    elif shape_class == "bulky":
        ideal_type = grasp_type = "horizontal_base" if upright else "top_down"
        if not upright:
            print("  NOTE: bulky but not upright (not covered by the given policy) "
                  "-> defaulting to top_down")
    else:  # "elongated"
        ideal_type = "side_grasp"
        grasp_type = "top_down"
        print("  NOTE: ideal_type='side_grasp' (perpendicular to the long axis), but "
              "side approach is kinematically infeasible on the HSR (5-DoF wrist, no "
              "wrist yaw) -> commanding 'top_down' at the part centroid instead")

    width_ok = minor_axis_width <= WIDTH_GATE_M
    if not width_ok:
        print(f"  WIDTH GATE: minor-axis width {minor_axis_width:.3f} m > "
              f"{WIDTH_GATE_M} m -> REJECTING grasp_type '{grasp_type}'")
        grasp_type = f"{grasp_type}_REJECTED_WIDTH"
        ideal_type = f"{ideal_type}_REJECTED_WIDTH"

    return grasp_type, ideal_type, upright, width_ok


def run_pipeline(instruction, target_hint=None, out_npz=OUT_NPZ, out_png=OUT_PNG):
    """
    Runs the full grounding -> object-cloud intersection -> geometric part
    decomposition -> shape/grasp-type pipeline for one instruction against
    the fixed HAND_NPZ/FUSED_NPZ/GRASPS_NPZ inputs, saving to out_npz/out_png.
    Returns a dict of the key results (see the plan's Task 2 Interfaces
    section for the full key list) for callers like
    part_decomposition_report.py that need to aggregate multiple runs
    without re-parsing the saved npz/png.
    """
    # ---- load inputs ----
    hv = np.load(HAND_NPZ, allow_pickle=True)
    rgb = hv["rgb"]
    K = hv["K"].astype(np.float64)
    tf_trans = hv["tf_trans"].astype(np.float64)
    tf_quat = hv["tf_quat"].astype(np.float64)
    H, W = rgb.shape[:2]
    print(f"[hand_part_grounding] hand view: rgb{rgb.shape}")

    if not np.any(K):
        print("[hand_part_grounding] WARNING: hand_view_real.npz K is all zeros "
              "(capture bug) -- substituting hand_view.npz's (simulated) K.")
        K = np.load(HAND_SIM_NPZ, allow_pickle=True)["camera_intrinsics"].astype(np.float64)

    base_pose_capture, base_pose_view = load_base_poses(hv)
    print(f"[hand_part_grounding] base_pose_capture (odom) = {base_pose_capture}")
    print(f"[hand_part_grounding] base_pose_view    (odom) = {base_pose_view}")

    fused = np.load(FUSED_NPZ)
    cloud = fused["points"].astype(np.float64)
    print(f"[hand_part_grounding] fused cloud: {len(cloud)} points (base_link frame)")

    grasps = np.load(GRASPS_NPZ)
    aff_center_3d = grasps["aff_center_3d"].astype(np.float64)
    print(f"[hand_part_grounding] aff_center_3d = {aff_center_3d}")

    delta_odom = load_refine_delta_odom(hv)
    print(f"[hand_part_grounding] refine_delta_odom = {delta_odom}")

    # ---- Step 1: VLM reasoning -> (target_object, target_part) ----
    config = PipelineConfig()
    reasoner = AffordanceReasoner(config.vlm)
    rr = reasoner.reason(instruction=instruction, scene_image=rgb,
                          verbose=True, target_hint=target_hint)
    target_object = rr.object_identification.target_object
    vlm_target_part = rr.affordance_reasoning.target_part
    constraints = rr.affordance_reasoning.constraints
    keep_clear = constraints.get("keep_clear", [])
    print(f"[hand_part_grounding] VLM -> object='{target_object}'  part='{vlm_target_part}'  "
          f"constraints={constraints}")

    # ---- Step 1b: LangSAM object grounding on the hand-camera RGB (Pass 1 of
    # _ground_with_langsam, gr.object_mask -- reliably works even when the
    # part-level Pass 2 collapses, so we only use Pass 1's output now) ----
    config.visual_grounding.workspace_image_crop = None  # hand-cam close-up, no sim crop
    grounder = VisualAffordanceGrounder(config.visual_grounding)
    # Hand camera is RGB-only here; ground() requires a depth image for its
    # internal 2D mask logic but we don't use its 3D output (we compute our
    # own 3D points below via cloud projection), so a dummy depth/extrinsics
    # is fine -- same trick as hand_view_grounding.py.
    dummy_depth = np.full((H, W), 0.3, dtype=np.float32)
    dummy_extr = np.eye(4)
    gr = grounder.ground(rgb_image=rgb, depth_image=dummy_depth,
                          target_object=target_object, target_part=vlm_target_part,
                          camera_intrinsics=K, camera_extrinsics=dummy_extr,
                          simulation_segmask=None, target_body_id=None)
    part_mask = gr.object_mask.astype(bool)
    print(f"[hand_part_grounding] object mask px = {int(part_mask.sum())}  "
          f"part_grounding_ok = {gr.part_grounding_ok}")

    # ---- Step 2: project nearby fused-cloud points into the hand camera ----
    dist = np.linalg.norm(cloud - aff_center_3d, axis=1)
    near = cloud[dist <= PROXIMITY_M]
    print(f"[hand_part_grounding] cloud points within {PROXIMITY_M} m of "
          f"aff_center_3d: {len(near)}")

    # near is still in base_link-at-head-capture-time frame (same frame as
    # aff_center_3d, so the proximity filter above is valid); re-express in
    # base_link-at-hand-view-time frame before projecting with the hand
    # camera's TF, which is relative to the view-time base_link. delta_odom
    # corrects the head-capture placement bias in the odom leg of that trip.
    near_view = transform_capture_to_view(near, base_pose_capture, base_pose_view,
                                           delta_odom=delta_odom)
    aff_center_3d_view = transform_capture_to_view(
        aff_center_3d[np.newaxis, :], base_pose_capture, base_pose_view,
        delta_odom=delta_odom)[0]
    print(f"[hand_part_grounding] aff_center_3d (view frame, bias-corrected) = "
          f"{aff_center_3d_view}")

    pixels, z_cam = project_to_camera(near_view, K, tf_trans, tf_quat)
    in_front = z_cam > 0
    u = np.round(pixels[:, 0]).astype(int)
    v = np.round(pixels[:, 1]).astype(int)
    in_bounds = in_front & (u >= 0) & (u < W) & (v >= 0) & (v < H)
    print(f"[hand_part_grounding] projected in-front-and-in-bounds: "
          f"{int(in_bounds.sum())}")

    near_ib = near_view[in_bounds]
    u_ib, v_ib = u[in_bounds], v[in_bounds]
    in_mask = part_mask[v_ib, u_ib]
    object_points = near_ib[in_mask]
    print(f"[hand_part_grounding] mask-cloud intersection (object 3D points): "
          f"{len(object_points)}")

    # near is still in the head-capture frame at this point in the file (only
    # near_view, above, has been re-expressed into view frame) -- slice it
    # with the same boolean indices to get the object's points in capture
    # frame, which is what part_decomposition.py's geometry expects.
    near_ib_capture = near[in_bounds]
    object_points_capture = near_ib_capture[in_mask]

    if len(object_points_capture) < MIN_INTERSECT:
        sys.exit(
            f"ABORT: mask-cloud intersection has only {len(object_points_capture)} "
            f"points (< {MIN_INTERSECT}). Check TF/K/mask alignment (frames, "
            f"quaternion convention, PROXIMITY_M) before trusting a grasp from this."
        )

    # ---- Step 3: geometric part decomposition (replaces VLM/mask part
    # selection -- see docs/superpowers/plans/2026-07-13-geometric-part-decomposition.md) ----
    intersection_centroid_capture = object_points_capture.mean(axis=0)
    object_cloud_capture = pd.extract_object_cloud(
        cloud, intersection_centroid_capture[:2], radius=0.12)
    print(f"[hand_part_grounding] object cloud (0.12m xy of intersection "
          f"centroid): {len(object_cloud_capture)} points")

    above_plane, z_table = pd.remove_support_plane(
        object_cloud_capture, percentile=15, margin=0.015)
    print(f"[hand_part_grounding] z_table={z_table:.3f}  "
          f"{len(above_plane)} points survive plane removal")

    parts, stats = pd.classify_parts(above_plane, z_table)
    part_counts = {name: len(pts) for name, pts in parts.items()}
    part_centroids = {name: (pts.mean(axis=0) if len(pts) else None)
                       for name, pts in parts.items()}
    for name in pd.PART_NAMES:
        c = part_centroids[name]
        c_str = np.array2string(c, precision=3) if c is not None else "n/a"
        print(f"  part='{name}': {part_counts[name]} pts  centroid={c_str}")

    selected_part, selected_points_capture, select_notes = \
        pd.select_part_from_target(vlm_target_part, keep_clear, parts)
    for note in select_notes:
        print(f"[hand_part_grounding] NOTE: {note}")
    print(f"[hand_part_grounding] selected part = '{selected_part}' "
          f"({len(selected_points_capture)} pts)")

    if len(selected_points_capture) < 3:
        sys.exit(
            f"ABORT: selected part '{selected_part}' has only "
            f"{len(selected_points_capture)} points -- cannot run PCA. Check "
            f"the object-cloud radius / plane threshold against this capture."
        )

    # geometry (PCA, grasp type) still runs on the selected part's points,
    # transformed into hand-view frame for the debug figure / output schema
    # (same frame the old part_grasp.npz stored).
    part_points = transform_capture_to_view(
        selected_points_capture, base_pose_capture, base_pose_view,
        delta_odom=delta_odom)

    centroid, eigvals, eigvecs, shape_class, minor_axis_width = \
        classify_part_shape(part_points)
    grasp_type, ideal_type, upright, width_ok = decide_grasp_type(
        shape_class, minor_axis_width, part_points)

    if selected_part == "handle":
        anchor_capture = pd.handle_grasp_anchor(
            selected_points_capture, stats["axis_xy"])
        grasp_anchor_view = transform_capture_to_view(
            anchor_capture[np.newaxis, :], base_pose_capture, base_pose_view,
            delta_odom=delta_odom)[0]
        print(f"[hand_part_grounding] handle root anchor (view frame) = "
              f"{grasp_anchor_view}  (ideal_type='side_grasp', executed as "
              f"top_down at this anchor, not the handle centroid)")
    else:
        grasp_anchor_view = centroid

    print(f"[hand_part_grounding] grasp_type = '{grasp_type}'  "
          f"(ideal_type = '{ideal_type}')")

    # ---- Step 4: save + debug figure ----
    part_names = pd.PART_NAMES
    part_counts_arr = np.array([part_counts[n] for n in part_names], dtype=int)
    part_centroids_arr = np.array(
        [part_centroids[n] if part_centroids[n] is not None else [np.nan] * 3
         for n in part_names], dtype=float)

    requires_controlled_tilt = constraints.get("post_grasp_motion") == "tilt_pour"

    np.savez(out_npz,
             part_points=part_points,
             part_centroid=centroid,
             pca_eigvals=eigvals,
             pca_eigvecs=eigvecs,
             shape_class=shape_class,
             grasp_type=grasp_type,
             ideal_type=ideal_type,
             minor_axis_width=minor_axis_width,
             width_ok=width_ok,
             target_object=target_object,
             target_part=vlm_target_part,
             selected_part=selected_part,
             grasp_anchor=grasp_anchor_view,
             part_names=np.array(part_names),
             part_counts=part_counts_arr,
             part_centroids=part_centroids_arr,
             requires_controlled_tilt=requires_controlled_tilt,
             constraints=constraints)
    print(f"[hand_part_grounding] saved -> {out_npz}")

    fig = plt.figure(figsize=(18, 6))

    ax0 = fig.add_subplot(1, 3, 1)
    ax0.imshow(rgb)
    ax0.imshow(part_mask, alpha=0.5, cmap="Oranges")
    ax0.set_title(f"RGB + object mask (target='{target_object}')")
    ax0.axis("off")

    ax1 = fig.add_subplot(1, 3, 2)
    ax1.imshow(rgb)
    ax1.scatter(u_ib[~in_mask], v_ib[~in_mask], s=3, c="cyan", alpha=0.4,
                label="cloud (outside mask)")
    ax1.scatter(u_ib[in_mask], v_ib[in_mask], s=4, c="red", alpha=0.8,
                label="cloud (in object mask)")
    ax1.set_title(f"Projected cloud ({int(in_bounds.sum())} pts)")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 3, 3, projection="3d")
    parts_view = {}
    for name, pts in parts.items():
        if len(pts) == 0:
            parts_view[name] = pts
            continue
        view_pts = transform_capture_to_view(
            pts, base_pose_capture, base_pose_view, delta_odom=delta_odom)
        parts_view[name] = view_pts
        alpha = 0.9 if name == selected_part else 0.25
        ax2.scatter(view_pts[:, 0], view_pts[:, 1], view_pts[:, 2],
                    s=4, c=pd.PART_COLORS[name], alpha=alpha, label=name)
    for i, color in enumerate(["r", "g", "b"]):
        axis = eigvecs[:, i] * np.sqrt(max(eigvals[i], 0.0)) * 2
        ax2.plot([centroid[0], centroid[0] + axis[0]],
                  [centroid[1], centroid[1] + axis[1]],
                  [centroid[2], centroid[2] + axis[2]], c=color, linewidth=2)
    title = f"parts (selected: {selected_part}, {shape_class}, {grasp_type})"
    if ideal_type != grasp_type:
        title += f"  [ideal: {ideal_type}]"
    ax2.set_title(title, fontsize=9)
    ax2.set_xlabel("x"); ax2.set_ylabel("y"); ax2.set_zlabel("z")
    ax2.legend(loc="upper left", fontsize=7)

    plt.tight_layout()
    plt.savefig(out_png, dpi=100, bbox_inches="tight")
    print(f"[hand_part_grounding] saved -> {out_png}")

    return {
        "target_object": target_object,
        "vlm_target_part": vlm_target_part,
        "constraints": constraints,
        "rationale": rr.affordance_reasoning.rationale,
        "confidence": rr.affordance_reasoning.confidence,
        "requires_controlled_tilt": requires_controlled_tilt,
        "selected_part": selected_part,
        "part_points_view": part_points,
        "part_points_capture": selected_points_capture,
        "part_centroid": centroid,
        "part_counts": part_counts,
        "part_centroids": part_centroids,
        "grasp_anchor_view": grasp_anchor_view,
        "shape_class": shape_class,
        "grasp_type": grasp_type,
        "ideal_type": ideal_type,
        "minor_axis_width": minor_axis_width,
        "width_ok": width_ok,
        "notes": select_notes,
        "parts": parts,
        "parts_view": parts_view,
        "stats": stats,
        "out_npz_path": out_npz,
        "out_png_path": out_png,
    }


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("instruction",
                     help="Natural-language task instruction, e.g. "
                          "'I want to drink some coffee'")
    ap.add_argument("--target", default=None,
                     help="Optional object-name hint to suppress VLM hallucination "
                          "(passed through to AffordanceReasoner as target_hint)")
    args = ap.parse_args()
    run_pipeline(args.instruction, target_hint=args.target)


if __name__ == "__main__":
    main()
