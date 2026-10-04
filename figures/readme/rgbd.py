"""Turn a recorded HSR capture back into a coloured point cloud.

Every cap_*.npz / head_capture_real.npz stores the RGB frame, the depth
image (metres), the camera intrinsics K and the camera pose in base_link
(tf_trans, tf_quat). Back-projecting each valid depth pixel and keeping its
RGB value gives the real, coloured cloud the robot measured.
"""
import numpy as np
from scipy.spatial.transform import Rotation


def load(path):
    d = np.load(path, allow_pickle=True)
    return dict(rgb=np.asarray(d["rgb"]), depth=d["depth"].astype(float), K=np.asarray(d["K"], float),
                R=Rotation.from_quat(np.asarray(d["tf_quat"], float).ravel()).as_matrix(),
                t=np.asarray(d["tf_trans"], float).ravel())


def backproject(cap, zmin=0.05, zmax=4.0):
    """Returns points (N,3) in base_link, colours (N,3) in 0..1 and pixel (N,2) as (u, v)."""
    depth, K = cap["depth"], cap["K"]
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (depth > zmin) & (depth < zmax)
    z = depth[ok]
    x = (u[ok] - K[0, 2]) * z / K[0, 0]
    y = (v[ok] - K[1, 2]) * z / K[1, 1]
    pts = (cap["R"] @ np.stack([x, y, z], -1).T).T + cap["t"]
    cols = cap["rgb"][ok].astype(float) / 255.0
    return pts, cols, np.stack([u[ok], v[ok]], -1)


def scene_near(path, center_xy, radius, step=2, zmin=0.15):
    """Coloured points of a capture within `radius` (m, horizontal) of a point,
    keeping every `step`-th pixel in each direction."""
    pts, cols, uv = backproject(load(path))
    keep = (uv[:, 0] % step == 0) & (uv[:, 1] % step == 0)
    keep &= np.linalg.norm(pts[:, :2] - np.asarray(center_xy)[:2], axis=1) < radius
    keep &= pts[:, 2] > zmin                  # drop the floor
    return pts[keep], cols[keep]


def to_pixels(cap, points):
    """base_link points -> (u, v) pixels of this capture."""
    K = cap["K"]
    pc = (cap["R"].T @ (np.atleast_2d(points) - cap["t"]).T).T
    z = np.where(pc[:, 2] > 1e-6, pc[:, 2], np.nan)
    return np.stack([K[0, 0] * pc[:, 0] / z + K[0, 2], K[1, 1] * pc[:, 1] / z + K[1, 2]], -1)


def crop_box(uv, pad, shape, aspect=None):
    """Integer crop (x0, y0, x1, y1) around pixel coordinates, optionally forced to an aspect ratio."""
    uv = uv[np.isfinite(uv).all(1)]
    x0, y0 = uv.min(0) - pad
    x1, y1 = uv.max(0) + pad
    if aspect:
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        if w / h < aspect:
            w = h * aspect
        else:
            h = w / aspect
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    H, W = shape[:2]
    return int(max(x0, 0)), int(max(y0, 0)), int(min(x1, W)), int(min(y1, H))
