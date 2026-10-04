r"""
export_grasps_plain.py -- WINDOWS. GraspPose objects -> plain numpy arrays.

FIX (2026-06-16): dist_to_aff is COMPUTED from geometry (pose translation vs
aff_center_3d), not read from a field GraspPose lacks (which returned NaN and
would silently break per-region selection that filters by affordance distance).
Geometry is the source of truth. Also exports affordance_score/combined_score
and HARD-ABORTS rather than saving corrupt (non-finite) distances.
"""
import numpy as np
from intent_grasp.paths import WORKSPACE

IN  = f"{WORKSPACE}/grasps_out.npz"
OUT = f"{WORKSPACE}/grasps_plain.npz"


def get_pose(g):
    for a in ["pose", "grasp_pose", "transform", "matrix", "pose_matrix", "T", "grasp_T"]:
        if hasattr(g, a):
            M = np.asarray(getattr(g, a), dtype=float)
            if M.shape == (4, 4):
                return M
    pos = None
    for a in ["position", "pos", "translation", "center", "grasp_center"]:
        if hasattr(g, a):
            pos = np.asarray(getattr(g, a), dtype=float); break
    R = None
    for a in ["rotation_matrix", "rotation", "R", "orientation_matrix"]:
        if hasattr(g, a):
            r = np.asarray(getattr(g, a), dtype=float)
            if r.shape == (3, 3): R = r; break
    if R is None:
        for a in ["quaternion", "quat", "orientation"]:
            if hasattr(g, a):
                q = np.asarray(getattr(g, a), dtype=float)
                if q.shape == (4,):
                    from scipy.spatial.transform import Rotation
                    R = Rotation.from_quat(q).as_matrix(); break
    M = np.eye(4)
    if R is not None: M[:3, :3] = R
    if pos is not None: M[:3, 3] = pos
    return M


def get_num(g, names, default=np.nan):
    for a in names:
        if hasattr(g, a):
            try: return float(getattr(g, a))
            except Exception: pass
    return default


def main():
    d = np.load(IN, allow_pickle=True)
    grasps = d["grasps"]
    aff = np.asarray(d["aff_center_3d"], dtype=float)
    print("num grasps:", len(grasps), " aff_center_3d:", np.round(aff, 3))

    poses, q_score, a_score, c_score = [], [], [], []
    for g in grasps:
        poses.append(get_pose(g))
        q_score.append(get_num(g, ["quality_score", "score", "quality", "cgn_score"]))
        a_score.append(get_num(g, ["affordance_score"]))
        c_score.append(get_num(g, ["combined_score"]))
    poses = np.array(poses)
    q_score = np.array(q_score); a_score = np.array(a_score); c_score = np.array(c_score)

    # --- dist_to_aff COMPUTED from geometry (the fix) ---
    gp = poses[:, :3, 3]
    dist = np.linalg.norm(gp - aff[None, :], axis=1)

    R = poses[:, :3, :3]
    bad_pose = (np.abs(R).sum(axis=(1, 2)) < 1e-6) | \
               np.all(np.isclose(R, np.eye(3)), axis=(1, 2))

    print("\nposes shape:", poses.shape)
    print("quality_score :", np.round(q_score, 3))
    print("dist_to_aff   :", np.round(dist, 3), "  <- COMPUTED, must be finite")
    if not np.all(np.isfinite(dist)):
        raise SystemExit("ABORT: dist_to_aff non-finite -- aff_center_3d or poses corrupt")
    if bad_pose.any():
        print("WARNING: identity/zero rotation at idx", np.where(bad_pose)[0],
              "-- rotation auto-detect may have missed a field")

    np.savez(OUT, poses=poses, scores=q_score, dist_to_aff=dist,
             aff_center_3d=aff, quality_score=q_score,
             affordance_score=a_score, combined_score=c_score)
    print("\nsaved ->", OUT)
    print(f"  nearest grasp to affordance: #{int(np.argmin(dist))} at {dist.min():.3f} m")


if __name__ == "__main__":
    main()
