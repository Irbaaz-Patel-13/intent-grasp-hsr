#!/usr/bin/env python
r"""
debug_hand_projection.py -- verify the hand-camera TF convention (hypothesis A)
and the odom-frame head-capture bias correction.

History (see hand_part_grounding.py module docstring for the fuller account):
an original 5-hypothesis sweep (A-E) picked hypothesis E (a DIRECT transform)
because it alone produced a tight, mug-shaped cluster. That was an artifact of
comparing the fused cloud (captured at head-capture time) against tf_trans/
tf_quat (relative to base_link AT HAND-VIEW TIME) without correcting for the
~0.4 m + ~13 degree base motion between the two -- E's particular error just
happened to cancel the frame mismatch. Re-running the sweep after adding
transform_capture_to_view() (base_pose_capture/base_pose_view frame
composition) confirmed hypothesis A instead: tf_trans/tf_quat is the camera's
pose in base_link-at-view-time, quat stored [x, y, z, w],
    p_cam = R.T @ (p_base - t)
with NO ROS link->optical correction (hand_camera_frame is already optical --
applying the correction on top, as hypothesis C did, double-corrects and was
the reason C/E scores don't agree here). Hypothesis E now scores 0 in the mug
region on a frame-matched cloud, proving its earlier win was error
cancellation, not the real convention -- so the B-E sweep is retired and this
script now only exercises A.

Remaining residual: even with A + frame-matching, projected points sat
~(-62, -31) px off the mug centre. That offset matches a head-capture
placement bias measured live on the robot for this run: fused_cloud.npz /
aff_center_3d are ~7.9 cm off in odom x and ~1.2 cm off in odom y from the
mug's true position. load_refine_delta_odom() applies that correction in the
odom frame (after composing capture -> odom, before odom -> view) via
transform_capture_to_view()'s delta_odom argument.

Run this after any new capture (with base_pose_capture/base_pose_view
populated) to confirm the projected cloud -- and the ring marking the
projected aff_center_3d -- lands on the mug (visible ~centre of the hand-cam
RGB, roughly u in [150,350] v in [150,340]).
"""
import sys

import numpy as np
from scipy.spatial.transform import Rotation
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from intent_grasp.paths import WORKSPACE

HAND_NPZ     = f"{WORKSPACE}/hand_view_real.npz"
HAND_SIM_NPZ = f"{WORKSPACE}/hand_view.npz"
FUSED_NPZ    = f"{WORKSPACE}/fused_cloud.npz"
GRASPS_NPZ   = f"{WORKSPACE}/grasps_plain.npz"
OUT_PNG      = f"{WORKSPACE}/projection_debug.png"
REFINE_DELTA_TXT = f"{WORKSPACE}/refine_delta.txt"

PROXIMITY_M = 0.25
# Central mug region in the hand-cam RGB (eyeballed from the image: the mug
# is the white/blue circle roughly centred slightly below image-centre).
MUG_U = (150, 350)
MUG_V = (150, 340)


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
    """Same frame composition as hand_part_grounding.py -- kept local here so
    this diagnostic script stays a standalone, dependency-light script (it
    doesn't import hand_part_grounding.py's VLM/LangSAM-heavy modules).
    delta_odom: optional (3,) odom-frame bias correction, added after the
    capture -> odom step, before the odom -> view step."""
    xc, yc, tc = base_pose_capture
    xv, yv, tv = base_pose_view
    p_odom = points @ _yaw_rotation_matrix(tc).T + np.array([xc, yc, 0.])
    if delta_odom is not None:
        p_odom = p_odom + delta_odom
    p_view = (p_odom - np.array([xv, yv, 0.])) @ _yaw_rotation_matrix(-tv).T
    return p_view


def load_base_poses(hv):
    """See hand_part_grounding.load_base_poses() -- same abort-on-missing/NaN
    contract, duplicated here to keep this script standalone."""
    if "base_pose_capture" not in hv.files or "base_pose_view" not in hv.files:
        sys.exit(
            "ABORT: hand_view_real.npz has no base_pose_capture/base_pose_view "
            "-- this is an old capture from before base-motion correction was "
            "added. Recapture with the updated capture script before rerunning "
            "this diagnostic."
        )
    base_pose_capture = hv["base_pose_capture"].astype(np.float64)
    base_pose_view = hv["base_pose_view"].astype(np.float64)
    if np.any(np.isnan(base_pose_capture)) or np.any(np.isnan(base_pose_view)):
        sys.exit(
            "ABORT: base_pose_capture/base_pose_view is NaN -- this is an old "
            "capture from before base-motion correction was populated. "
            "Recapture with the updated capture script before rerunning this "
            "diagnostic."
        )
    return base_pose_capture, base_pose_view


def load_refine_delta_odom(hv):
    """See hand_part_grounding.load_refine_delta_odom() -- same
    npz-key-then-file-then-zeros-with-warning contract, duplicated here to
    keep this script standalone."""
    if "refine_delta_odom" in hv.files:
        d = np.asarray(hv["refine_delta_odom"], dtype=np.float64)
        return np.array([d[0], d[1], 0.0])
    try:
        with open(REFINE_DELTA_TXT) as f:
            dx, dy = (float(x) for x in f.read().strip().split(","))
        return np.array([dx, dy, 0.0])
    except FileNotFoundError:
        print("WARNING: no refine_delta_odom in npz and no "
              f"{REFINE_DELTA_TXT} found -- proceeding WITHOUT the odom-frame "
              "bias correction. Projections will be off by the known head-"
              "capture placement bias.")
        return np.zeros(3)


def project_to_camera(points, R, t, K):
    """Hypothesis A: p_cam = R.T @ (p_base - t), no ROS link->optical
    correction (hand_camera_frame is already optical)."""
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
    p_cam = (points - t) @ R          # row-vector form of R.T @ (p - t)
    z = p_cam[:, 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        u = fx * p_cam[:, 0] / z + cx
        v = fy * p_cam[:, 1] / z + cy
    return u, v, z


def main():
    hv = np.load(HAND_NPZ, allow_pickle=True)
    rgb = hv["rgb"]
    K_hand = hv["K"].astype(np.float64)
    tf_trans = hv["tf_trans"].astype(np.float64)
    tf_quat = hv["tf_quat"].astype(np.float64)
    frame = str(hv["frame"])
    H, W = rgb.shape[:2]
    print(f"hand_view_real.npz: rgb{rgb.shape}  frame='{frame}'")
    print(f"tf_trans = {tf_trans}")
    print(f"tf_quat  = {tf_quat}  (quat [x,y,z,w], hypothesis A)")

    if not np.any(K_hand):
        print("WARNING: hand_view_real.npz K is all zeros (capture bug) -- "
              "substituting hand_view.npz's (simulated) K -- matches the "
              "visible wide-FOV/fisheye lens, NOT a real calibration.")
        K = np.load(HAND_SIM_NPZ, allow_pickle=True)["camera_intrinsics"].astype(np.float64)
    else:
        K = K_hand
    print(f"K used for projection:\n{K}")

    base_pose_capture, base_pose_view = load_base_poses(hv)
    print(f"base_pose_capture (odom) = {base_pose_capture}")
    print(f"base_pose_view    (odom) = {base_pose_view}")

    delta_odom = load_refine_delta_odom(hv)
    print(f"refine_delta_odom = {delta_odom}")

    fused = np.load(FUSED_NPZ)
    cloud = fused["points"].astype(np.float64)

    grasps = np.load(GRASPS_NPZ)
    aff_center_3d = grasps["aff_center_3d"].astype(np.float64)
    print(f"aff_center_3d = {aff_center_3d}")

    dist = np.linalg.norm(cloud - aff_center_3d, axis=1)
    near = cloud[dist <= PROXIMITY_M]
    print(f"cloud points within {PROXIMITY_M} m of aff_center_3d: {len(near)}")

    # near is in base_link-at-head-capture-time frame; re-express in
    # base_link-at-hand-view-time frame before projecting with tf_trans/
    # tf_quat, which are relative to the view-time base_link. delta_odom
    # corrects the head-capture placement bias in the odom leg of that trip.
    near_view = transform_capture_to_view(near, base_pose_capture, base_pose_view,
                                           delta_odom=delta_odom)
    aff_center_3d_view = transform_capture_to_view(
        aff_center_3d[np.newaxis, :], base_pose_capture, base_pose_view,
        delta_odom=delta_odom)[0]
    print(f"cloud re-expressed in base_link-at-hand-view-time frame "
          f"({len(near_view)} points, bias-corrected)")
    print(f"aff_center_3d (view frame, bias-corrected) = {aff_center_3d_view}")

    R_A = Rotation.from_quat(tf_quat).as_matrix()   # xyzw as-is, hypothesis A

    u, v, z = project_to_camera(near_view, R_A, tf_trans, K)
    in_front = z > 0
    u_i, v_i = u[in_front], v[in_front]
    in_bounds = (u_i >= 0) & (u_i < W) & (v_i >= 0) & (v_i < H)
    u_ib, v_ib = u_i[in_bounds], v_i[in_bounds]

    in_mug = ((u_ib >= MUG_U[0]) & (u_ib <= MUG_U[1]) &
              (v_ib >= MUG_V[0]) & (v_ib <= MUG_V[1]))
    mug_count = int(in_mug.sum())

    mean_u = float(u_ib.mean()) if len(u_ib) else float("nan")
    mean_v = float(v_ib.mean()) if len(v_ib) else float("nan")
    img_cx, img_cy = W / 2.0, H / 2.0
    print("[A: quat=[x,y,z,w], inverse-xform, no optical corr., bias-corrected]")
    print(f"  in-front: {int(in_front.sum())}/{len(near_view)}  "
          f"in-bounds: {len(u_ib)}  in mug region: {mug_count}")
    print(f"  mean projected pixel = ({mean_u:.1f}, {mean_v:.1f})  "
          f"image centre = ({img_cx:.1f}, {img_cy:.1f})")

    u_c, v_c, z_c = project_to_camera(aff_center_3d_view[np.newaxis, :], R_A, tf_trans, K)
    u_c, v_c = float(u_c[0]), float(v_c[0])
    ring_in_mug = (MUG_U[0] <= u_c <= MUG_U[1]) and (MUG_V[0] <= v_c <= MUG_V[1])
    print(f"  aff_center_3d projected pixel = ({u_c:.1f}, {v_c:.1f})  "
          f"in mug region: {ring_in_mug}")

    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.imshow(rgb)
    ax.scatter(u_ib, v_ib, s=3, c="lime", alpha=0.6, label="projected cloud")
    ax.scatter([u_c], [v_c], s=300, facecolors="none", edgecolors="red",
               linewidths=2, label="aff_center_3d (bias-corrected)")
    ax.set_title(
        f"Hypothesis A, bias-corrected\n"
        f"in mug region: {mug_count} / {len(u_ib)} in-bounds  |  "
        f"ring in mug region: {ring_in_mug}", fontsize=10)
    ax.legend(loc="lower right", fontsize=8)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=110, bbox_inches="tight")
    print(f"saved -> {OUT_PNG}")


if __name__ == "__main__":
    main()
