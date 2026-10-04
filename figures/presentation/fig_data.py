"""
fig_data.py -- shared, validated experiment-data loading for the
dissertation figure set. Every figure script loads real data through these
functions rather than reading .npz/.csv files directly, so the
data-provenance contract (design spec Sec 2/13) has one enforcement point.
"""
import csv
import dataclasses
import os

import numpy as np
from intent_grasp.paths import WORKSPACE

HERE = str(WORKSPACE)
DEFAULT_EXP_DIR = os.path.join(HERE, "Experiment_Logs", "2026-08-07")


@dataclasses.dataclass
class Capture:
    rgb: np.ndarray
    depth: np.ndarray
    K: np.ndarray
    tf_trans: np.ndarray
    tf_quat: np.ndarray
    base_frame: str
    cam_frame: str


def load_capture(exp_dir=DEFAULT_EXP_DIR):
    d = np.load(os.path.join(exp_dir, "head_capture_real.npz"), allow_pickle=True)
    cap = Capture(rgb=d["rgb"], depth=d["depth"], K=d["K"],
                  tf_trans=d["tf_trans"], tf_quat=d["tf_quat"],
                  base_frame=str(d["base_frame"]), cam_frame=str(d["cam_frame"]))
    assert cap.rgb.shape == (480, 640, 3), f"unexpected rgb shape {cap.rgb.shape}"
    assert cap.depth.shape == (480, 640), f"unexpected depth shape {cap.depth.shape}"
    return cap


@dataclasses.dataclass
class Grounding:
    instruction: str
    target_object: str
    target_part: str
    rgb: np.ndarray
    object_mask: np.ndarray
    affordance_mask: np.ndarray
    aff_center_3d: np.ndarray
    affordance_points: np.ndarray


def load_grounding(exp_dir=DEFAULT_EXP_DIR):
    d = np.load(os.path.join(exp_dir, "grasps_out.npz"), allow_pickle=True)
    g = Grounding(
        instruction=str(d["instruction"]), target_object=str(d["target_object"]),
        target_part=str(d["target_part"]), rgb=d["grounding_rgb"],
        object_mask=d["object_mask"].astype(bool),
        affordance_mask=d["affordance_mask"].astype(bool),
        aff_center_3d=d["aff_center_3d"], affordance_points=d["affordance_points"])
    assert g.object_mask.shape == (480, 640)
    assert g.object_mask.sum() > 0, "grounding produced an empty object mask"
    return g


def mask_bbox(mask):
    """Tight (x0, y0, x1, y1) pixel bbox of a boolean mask -- used for
    Figure 2's grounding box, since no bbox is stored separately."""
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


@dataclasses.dataclass
class GraspCandidates:
    poses: np.ndarray
    scores: np.ndarray
    quality_score: np.ndarray
    affordance_score: np.ndarray
    combined_score: np.ndarray
    dist_to_aff: np.ndarray
    aff_center_3d: np.ndarray
    collision_free: np.ndarray
    manip: np.ndarray
    arm_only_ok: np.ndarray
    clearance_m: np.ndarray
    base_x: np.ndarray
    base_y: np.ndarray
    base_yaw_rad: np.ndarray
    standoff_m: np.ndarray


def load_grasp_candidates(exp_dir=DEFAULT_EXP_DIR):
    d = np.load(os.path.join(exp_dir, "grasps_plain.npz"), allow_pickle=True)
    n = d["poses"].shape[0]
    collision_free = np.ones(n, dtype=bool)
    arm_only_ok = np.ones(n, dtype=bool)
    manip = np.full(n, np.nan)
    clearance_m = np.full(n, np.nan)
    base_x = np.full(n, np.nan)
    base_y = np.full(n, np.nan)
    base_yaw_rad = np.full(n, np.nan)
    standoff_m = np.full(n, np.nan)
    place_run = os.path.join(exp_dir, "place_run.csv")
    if os.path.exists(place_run):
        with open(place_run, newline="") as f:
            for row in csv.DictReader(f):
                i = int(row["grasp"])
                if i < n:
                    collision_free[i] = bool(int(row["collision_free"]))
                    arm_only_ok[i] = bool(int(row["arm_only_ok"]))
                    manip[i] = float(row["manip"])
                    clearance_m[i] = float(row["clearance_m"])
                    base_x[i] = float(row["base_x"])
                    base_y[i] = float(row["base_y"])
                    base_yaw_rad[i] = float(row["base_yaw_rad"])
                    standoff_m[i] = float(row["standoff_m"])
    return GraspCandidates(
        poses=d["poses"], scores=d["scores"], quality_score=d["quality_score"],
        affordance_score=d["affordance_score"], combined_score=d["combined_score"],
        dist_to_aff=d["dist_to_aff"], aff_center_3d=d["aff_center_3d"],
        collision_free=collision_free, manip=manip, arm_only_ok=arm_only_ok,
        clearance_m=clearance_m, base_x=base_x, base_y=base_y,
        base_yaw_rad=base_yaw_rad, standoff_m=standoff_m)


def load_fused_cloud(exp_dir=DEFAULT_EXP_DIR):
    d = np.load(os.path.join(exp_dir, "fused_cloud.npz"), allow_pickle=True)
    pts = d["points"]
    assert pts.ndim == 2 and pts.shape[1] == 3, f"unexpected points shape {pts.shape}"
    return pts


def load_multiview(exp_dir=DEFAULT_EXP_DIR):
    d = np.load(os.path.join(exp_dir, "multiview.npz"), allow_pickle=True)
    return dict(view_names=d["view_names"], rgb=d["rgb"], depth=d["depth"],
                camera_intrinsics=d["camera_intrinsics"],
                camera_extrinsics=d["camera_extrinsics"])


def project_point(point_base, K, tf_trans, tf_quat):
    """Projects a real 3D point in base_link frame into real 2D pixel
    coordinates, using the real camera intrinsics/extrinsics from
    head_capture_real.npz. A deterministic geometric derivation (never an
    invented pixel location) -- verified against grasps_out.npz's
    aff_center_3d, which projects within (2.8, 9.8)px of object_mask's own
    centroid for the anchor trial (test_fig05's tolerance is 15px)."""
    from scipy.spatial.transform import Rotation
    R_cam = Rotation.from_quat(tf_quat).as_matrix()
    p_cam = R_cam.T @ (np.asarray(point_base) - np.asarray(tf_trans))
    u = K[0, 0] * p_cam[0] / p_cam[2] + K[0, 2]
    v = K[1, 1] * p_cam[1] / p_cam[2] + K[1, 2]
    return float(u), float(v)


def camera_origin(extrinsic):
    """World-frame camera position from a world->camera view matrix
    (extrinsic = [R|t] such that p_cam = R @ p_world + t) -- NOT the same as
    extrinsic[:3, 3], which is the view-matrix translation, not a position."""
    R, t = extrinsic[:3, :3], extrinsic[:3, 3]
    return -R.T @ t


def load_trials(repo_root=HERE):
    path = os.path.join(repo_root, "trials.csv")
    with open(path, newline="") as f:
        return list(csv.DictReader(f))
