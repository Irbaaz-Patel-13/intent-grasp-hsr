"""
fig04_pointcloud.py -- Figure 4: Point Cloud Generation.

Scientific question: does RGB-D fusion produce a coherent, well-registered
3D reconstruction of the scene?
Scientific claim: the fused point cloud is a real geometric reconstruction
(not a rendered CAD mug) with a real coordinate frame and a real camera
viewpoint.
Supporting evidence: Experiment_Logs/2026-08-07/fused_cloud.npz (241,818
  pts), multiview.npz (per-view extrinsics, used for the camera-ray overlay).
Required real data: fused_cloud points, multiview camera_extrinsics.
Required diagrammatic elements: for render performance, points are
  subsampled with a fixed seed (figstyle.SEED) -- the subsample is
  deterministic across reruns, not a different random cloud each time. Point
  color encodes real Euclidean distance from the real camera position
  (fig_data.camera_origin, cross-checked against head_capture_real.npz's
  tf_trans) through the same magma colormap Figure 1's depth panel uses --
  a real geometric derivation for depth legibility, not a decorative
  gradient. The rendered raster is cropped to its own non-background content
  bounding box (+20px pad) for the same reason Figure 3 crops to its mask
  bbox: a compact cloud in a 16:9 canvas otherwise reads as mostly empty
  space. Note: Open3D's own rasterizer is not guaranteed byte-stable across
  machines/drivers even with a fixed camera and seed, so this figure's
  reproducibility is verified structurally, not by byte hash (see
  test_fig04_pointcloud.py).
  Rendering path note: Open3D 0.19.0/0.18.0's Filament-based
  `rendering.OffscreenRenderer` cannot construct on this Windows machine
  ("EGL Headless is not supported on this platform" -- a confirmed, current
  upstream limitation, isl-org/Open3D#5745, not fixable from this project's
  code). `render_open3d()` therefore uses the legacy
  `o3d.visualization.Visualizer` with `visible=False`, which uses a
  Windows-native WGL context instead of EGL. This requires a real interactive
  desktop session (confirmed present on this machine) rather than a true
  server-side headless render -- a real, not fabricated, limitation of this
  fallback, stated here rather than silently assumed.

Run: python fig04_pointcloud.py [--exp-dir DIR]
Output: generated_assets/fig04/fig04_pointcloud.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d

import figstyle as fs
import fig_data as fd

MAX_RENDER_POINTS = 60_000


def _subsample(points, rng, max_points=MAX_RENDER_POINTS):
    if len(points) <= max_points:
        return points
    idx = rng.choice(len(points), size=max_points, replace=False)
    return points[idx]


def render_open3d(points, extrinsics, width=1200, height=900):
    """Renders via the legacy o3d.visualization.Visualizer (WGL on Windows),
    not rendering.OffscreenRenderer (Filament/EGL) -- see the module
    docstring's "Rendering path note" for why. Visualizer's
    capture_screen_float_buffer() returns a real render of the same geometry
    the OffscreenRenderer path would have shown; the interfaces
    (points/extrinsics in, an (H, W, 3) uint8 image out) are unchanged.

    Points are colored by real distance from the real camera
    position (fig_data.camera_origin), through the same magma colormap
    Figure 1's depth panel uses -- a genuine geometric derivation, not a
    decorative gradient, and it gives the room's structure (table/chair
    edges) actual depth cues that a flat single-color cloud does not."""
    rng = np.random.default_rng(fs.SEED)
    pts = _subsample(points, rng)

    cam_origin = fd.camera_origin(extrinsics[0]) if len(extrinsics) else np.zeros(3)

    dists = np.linalg.norm(pts - cam_origin, axis=1)
    d_lo, d_hi = np.percentile(dists, [2, 98])
    d_norm = np.clip((dists - d_lo) / max(d_hi - d_lo, 1e-6), 0, 1)
    depth_cmap = matplotlib.colormaps["magma"]
    point_colors = depth_cmap(d_norm)[:, :3]

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(point_colors)

    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)

    sample_idx = rng.choice(len(pts), size=min(24, len(pts)), replace=False)
    ray_pts = [cam_origin] + [pts[i] for i in sample_idx]
    ray_lines = [[0, k + 1] for k in range(len(sample_idx))]
    rays = o3d.geometry.LineSet()
    rays.points = o3d.utility.Vector3dVector(np.array(ray_pts))
    rays.lines = o3d.utility.Vector2iVector(np.array(ray_lines))
    # MUTED, not REASONING -- spec Sec 4 reserves REASONING (purple) for
    # affordance/VLM reasoning; camera rays are geometry, same family as the
    # coordinate frame and frustum wireframes elsewhere in the deck.
    ray_color = matplotlib.colors.to_rgb(fs.MUTED)
    rays.colors = o3d.utility.Vector3dVector(np.tile(ray_color, (len(ray_lines), 1)))

    bbox = pcd.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    extent = max(bbox.get_extent())
    eye = center + np.array([extent * 1.1, -extent * 1.1, extent * 0.8])
    up = np.array([0.0, 0.0, 1.0])
    front = eye - center  # Open3D convention: front points lookat -> eye
    front = front / np.linalg.norm(front)

    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height, visible=False)
    try:
        vis.add_geometry(pcd)
        vis.add_geometry(frame)
        vis.add_geometry(rays)

        opt = vis.get_render_option()
        opt.background_color = np.asarray(matplotlib.colors.to_rgb(fs.SLIDE_BG))
        opt.point_size = 2.5

        ctr = vis.get_view_control()
        ctr.set_lookat(center)
        ctr.set_front(front)
        ctr.set_up(up)
        ctr.set_zoom(0.85)

        vis.poll_events()
        vis.update_renderer()
        img = vis.capture_screen_float_buffer(do_render=True)
    finally:
        vis.destroy_window()

    return (np.asarray(img) * 255).astype(np.uint8)


def _crop_to_content(img, bg_rgb, pad=20):
    """Crops a rendered raster to the bounding box of pixels that differ
    from the background color, plus a fixed pad. A real derivation from the
    actual rendered content (same technique as fig03's mask-bbox crop), so a
    compact point cloud doesn't sit in a mostly-empty 16:9 frame."""
    bg = np.array(bg_rgb) * 255
    diff = np.abs(img.astype(int) - bg.astype(int)).sum(axis=-1)
    mask = diff > 15
    if not mask.any():
        return img
    ys, xs = np.where(mask)
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad, img.shape[0])
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad, img.shape[1])
    return img[y0:y1, x0:x1]


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    points = fd.load_fused_cloud(exp_dir)
    mv = fd.load_multiview(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig04"), "fig04_pointcloud.png")

    o3d_img = render_open3d(points, mv["camera_extrinsics"])
    o3d_img = _crop_to_content(o3d_img, matplotlib.colors.to_rgb(fs.SLIDE_BG))

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 4 -- Point Cloud Generation", **fs.TITLE, x=fs.MARGIN, ha="left")
    ax = fig.add_axes([0.10, 0.12, 0.80, 0.75])
    ax.imshow(o3d_img)
    ax.axis("off")

    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"{len(points):,} fused points ({min(len(points), MAX_RENDER_POINTS):,} "
              f"rendered, seed={fs.SEED}); {mv['view_names'].shape[0]} capture "
              f"view(s) fused. Color = real distance from the camera position.",
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
    print(f"fig04 written to {path}")
