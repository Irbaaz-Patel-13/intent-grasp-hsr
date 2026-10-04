"""
fig01_acquisition.py -- Figure 1: Real Scene Acquisition.

Scientific question: what did the robot actually observe, geometrically,
before any perception ran?
Scientific claim: acquisition produces a real, calibrated RGB-D observation
with known camera geometry (intrinsics + robot-frame extrinsics), not a
canned image.
Supporting evidence: Experiment_Logs/2026-08-07/head_capture_real.npz.
Required real data: rgb, depth, K, tf_quat, cam_frame, base_frame
  -- all used directly, no synthetic substitution.
Required diagrammatic elements: the camera-frustum wireframe is a geometric
  construction from K and the image size (a real, deterministic derivation,
  not an invented shape), rotated into the real camera orientation (R_cam,
  from tf_quat) so it agrees with the coordinate-frame triad drawn at the
  same origin -- both represent the same real orientation, not two different
  frames sharing a point. Depth pixels with value <= 0 are a real no-return
  sensor sentinel (21.3% of this capture), masked to NaN before coloring
  rather than shown as if they were valid near-range measurements.

Run: python fig01_acquisition.py [--exp-dir DIR]
Output: generated_assets/fig01/fig01_acquisition.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (registers 3D projection)
import numpy as np
from scipy.spatial.transform import Rotation

import figstyle as fs
import fig_data as fd


def frustum_corners(K, w, h, depth=0.6):
    """Real geometric derivation of the 4 far-plane corner rays of the
    camera's field of view from intrinsics K, at a fixed illustrative depth."""
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    corners_px = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=float)
    rays = []
    for px, py in corners_px:
        x = (px - cx) / fx * depth
        y = (py - cy) / fy * depth
        rays.append([x, y, depth])
    return np.array(rays)


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    cap = fd.load_capture(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig01"), "fig01_acquisition.png")

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 1 -- Real Scene Acquisition", **fs.TITLE, x=fs.MARGIN, ha="left")

    ax_rgb = fig.add_axes([0.04, 0.15, 0.28, 0.72])
    ax_rgb.imshow(cap.rgb)
    ax_rgb.set_title("RGB", **fs.SECTION)
    ax_rgb.axis("off")

    ax_depth = fig.add_axes([0.36, 0.15, 0.28, 0.72])
    # cap.depth uses 0 as a no-return/invalid-pixel sentinel (21.3% of this
    # capture), not "closest surface" -- mask those out to NaN before
    # clipping/coloring, or they render as the darkest (nearest-looking)
    # colour on a colourbar labelled "metres".
    depth_valid = np.where(cap.depth > 0, cap.depth, np.nan)
    depth_vis = np.clip(depth_valid, 0, np.nanpercentile(depth_valid, 98))
    cmap = matplotlib.colormaps["magma"].copy()
    cmap.set_bad(fs.FAINT)
    im = ax_depth.imshow(depth_vis, cmap=cmap)
    ax_depth.set_title("Depth", **fs.SECTION)
    ax_depth.axis("off")
    cbar = fig.colorbar(im, ax=ax_depth, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=fs.MUTED, labelsize=8)
    cbar.set_label("metres", color=fs.MUTED, fontsize=8)
    invalid_pct = 100 * float(np.sum(cap.depth <= 0)) / cap.depth.size

    ax3 = fig.add_axes([0.68, 0.12, 0.29, 0.78], projection="3d")
    ax3.set_facecolor(fs.SLIDE_BG)
    h, w = cap.depth.shape
    R_cam = Rotation.from_quat(cap.tf_quat).as_matrix()
    # frustum_corners() gives rays in the camera's own optical frame
    # (canonical +z-forward). Rotate them by the real R_cam so the frustum
    # and the coordinate triad below agree on which way the camera actually
    # points -- plotting raw optical-frame corners next to a real-orientation
    # triad (as an earlier version did) draws two different frames sharing
    # an origin, so the axis labels point somewhere unrelated to the frustum.
    corners = frustum_corners(cap.K, w, h) @ R_cam.T
    origin = np.zeros(3)
    for c in corners:
        xs, ys, zs = zip(origin, c)
        ax3.plot(xs, ys, zs, color=fs.MUTED, linewidth=1.0)
    loop = np.vstack([corners, corners[:1]])
    ax3.plot(loop[:, 0], loop[:, 1], loop[:, 2], color=fs.GEOMETRY, linewidth=1.2)
    fs.draw_coordinate_frame(ax3, origin, R_cam, scale=0.08)
    rot_obj = Rotation.from_matrix(R_cam)
    tilt_rad = rot_obj.as_euler('xyx', degrees=False)[0]
    # Anchored in axes-fraction (2D) space, not a 3D data point -- this keeps
    # the label clear of the frustum apex/coordinate-frame axes regardless of
    # view angle, unlike a 3D-anchored ax3.text() near the origin.
    ax3.text2D(0.5, 0.04, f"{cap.cam_frame}\n(schematic, head tilt {tilt_rad:.2f} rad)",
               transform=ax3.transAxes, color=fs.MUTED, fontsize=7, ha="center")
    ax3.set_title("Camera Frustum", **fs.SECTION)
    ax3.set_axis_off()
    ax3.view_init(elev=15, azim=-60)

    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"cam_frame={cap.cam_frame}  base_frame={cap.base_frame}  "
              f"K=[[{cap.K[0,0]:.1f},0,{cap.K[0,2]:.1f}],[0,{cap.K[1,1]:.1f},{cap.K[1,2]:.1f}]]  "
              f"depth invalid px: {invalid_pct:.1f}%",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig01 written to {path}")
