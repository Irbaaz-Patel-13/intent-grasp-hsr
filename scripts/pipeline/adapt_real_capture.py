r"""
adapt_real_capture.py -- LAPTOP. Convert a single real HSR capture
(head_capture_real.npz: rgb, depth[m], K, base_link->camera TF) into the
multiview.npz + fused_cloud.npz format run_grounding_grasp.py consumes.
World frame = base_link (the pipeline is frame-agnostic; cloud + extrinsics agree).
"""
import numpy as np
from scipy.spatial.transform import Rotation
from intent_grasp.paths import WORKSPACE

IN    = f"{WORKSPACE}/head_capture_real.npz"
OUT_MV = f"{WORKSPACE}/multiview.npz"
OUT_FU = f"{WORKSPACE}/fused_cloud.npz"
DEPTH_MAX = 3.0   # drop far background (room) beyond 3 m; cup is ~0.7 m

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])


def main():
    d = np.load(IN)
    rgb   = d["rgb"]                       # (H,W,3) uint8
    depth = d["depth"].astype(np.float32)  # (H,W) metres
    K     = d["K"].astype(float)           # (3,3)
    trans = d["tf_trans"]; quat = d["tf_quat"]
    H, W = depth.shape
    print(f"rgb{rgb.shape} depth{depth.shape} depth median={np.median(depth[depth>0.05]):.3f} m")

    # camera->base homogeneous transform from the TF
    T_base_cam = np.eye(4)
    T_base_cam[:3, :3] = Rotation.from_quat(quat).as_matrix()  # quat = [x,y,z,w]
    T_base_cam[:3, 3]  = trans
    print(f"camera height above base = {trans[2]:.3f} m")

    # OpenGL world->cam extrinsics the pipeline expects (world = base_link)
    camera_extrinsics = FLIP @ np.linalg.inv(T_base_cam)

    # build the scene cloud in base frame (OpenCV back-projection -> base)
    fx, fy = K[0, 0], K[1, 1]; cx, cy = K[0, 2], K[1, 2]
    u, v = np.meshgrid(np.arange(W), np.arange(H))
    valid = (depth > 0.05) & (depth < DEPTH_MAX)
    z = depth[valid]
    x = (u[valid] - cx) * z / fx
    y = (v[valid] - cy) * z / fy
    pts_cam = np.stack([x, y, z, np.ones_like(z)], axis=-1)     # OpenCV optical
    pts_base = (T_base_cam @ pts_cam.T).T[:, :3]                # -> base frame
    print(f"cloud: {len(pts_base)} pts  "
          f"x[{pts_base[:,0].min():.2f},{pts_base[:,0].max():.2f}] "
          f"y[{pts_base[:,1].min():.2f},{pts_base[:,1].max():.2f}] "
          f"z[{pts_base[:,2].min():.2f},{pts_base[:,2].max():.2f}]")

    # save in the format run_grounding_grasp.py reads (single 'center' view)
    np.savez(OUT_MV,
             view_names=np.array(["center"]),
             rgb=rgb[None, ...],
             depth=depth[None, ...],
             camera_intrinsics=K,
             camera_extrinsics=camera_extrinsics[None, ...])
    print(f"saved -> {OUT_MV}")
    np.savez(OUT_FU, points=pts_base.astype(np.float64))
    print(f"saved -> {OUT_FU}")
    print("\nNOTE: world frame is base_link (not odom). Grasps will be in base frame.")
    print("Watch run_grounding_grasp.py's 'affordance center within fused-cloud extent' line —")
    print("it must say OK. If it WARNs, the frame convention is off and we fix before trusting grasps.")


if __name__ == "__main__":
    main()