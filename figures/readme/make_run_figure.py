"""One real run, end to end: the 7 Aug 2026 experiment log, drawn from its own files.

(a) the head-camera frame with the grounded object and the 3D target projected back
(b) the fused point cloud of the mug with all 25 Contact-GraspNet candidates
(c) collision-aware base placement seen from above
(d) the HSR, posed from the URDF at the chosen base and joint solution, over the cloud

Run from the repository root:

    python figures/readme/make_run_figure.py

Writes docs/images/real_run.png
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from intent_grasp.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "figures" / "presentation"))
sys.path.insert(0, str(REPO_ROOT / "figures" / "readme"))
import fig_data as fd  # noqa: E402
import rgbd  # noqa: E402
import scene3d as s3  # noqa: E402
from make_readme_figures import (BLUE, HAIRLINE, INK, INK_2, INK_3, ORANGE, SURFACE,  # noqa: E402
                                 save, title)

EXP = fd.DEFAULT_EXP_DIR
CHOSEN = s3.EXECUTED_CANDIDATE
FINGERTIP = 0.1034          # Contact-GraspNet: fingertips this far along the approach axis
CAM_HIGH = dict(kind="perspective", elevation_deg=48.0, azimuth_deg=220.0, fov_deg=30.0)


def target_marker(ax, x, y):
    ax.scatter(x, y, s=170, marker="+", color="white", linewidths=4.5, zorder=6)
    ax.scatter(x, y, s=120, marker="+", color=ORANGE, linewidths=2.2, zorder=7)


def gripper_lines(T, width=0.08, palm=0.066):
    """Two-finger gripper glyph from a 4x4 grasp pose (origin at the gripper
    base, z = approach, x = closing direction)."""
    t, x, z = T[:3, 3], T[:3, 0], T[:3, 2]
    c = t + z * palm
    a, b = c + x * width / 2, c - x * width / 2
    return [(t, c), (a, b), (a, a + z * (FINGERTIP - palm)), (b, b + z * (FINGERTIP - palm))]


def project(points, view, proj, w, h):
    px, py, _, ok = s3.project_points(np.atleast_2d(points), view, proj, w, h)
    return px, py, ok


def panel_camera(ax, cap, g):
    ys, xs = np.where(g.object_mask)
    pad = 70
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, 640)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, 480)
    ax.imshow(cap.rgb[y0:y1, x0:x1])
    ax.contour(g.object_mask[y0:y1, x0:x1].astype(float), levels=[0.5], colors=[BLUE], linewidths=1.8)
    u, v = fd.project_point(g.aff_center_3d, cap.K, cap.tf_trans, cap.tf_quat)
    target_marker(ax, u - x0, v - y0)
    ax.axis("off")
    return ("(a) head camera: object found",
            f"“{g.instruction}” → {g.target_object}.\nBlue outline: LangSAM object mask.")


def panel_grasps(ax, cloud, cand):
    c = cand.aff_center_3d
    # the run's own RGB-D frame, back-projected so every point keeps its real colour
    pts, cols, _ = rgbd.backproject(rgbd.load(EXP + "/head_capture_real.npz"))
    sel = np.linalg.norm(pts[:, :2] - c[:2], axis=1) < 0.15
    table_z = np.percentile(pts[sel, 2], 20)
    sel &= pts[:, 2] > table_z - 0.02
    pts, cols = pts[sel], cols[sel]
    W = H = 1000
    view, proj, _ = s3.view_and_projection(CAM_HIGH, c, 0.75, aspect=1.0)
    px, py, depth, ok = s3.project_points(pts, view, proj, W, H)
    order = np.argsort(-depth[ok])                       # far points first, near points on top
    ax.scatter(px[ok][order], py[ok][order], s=3.0, c=cols[ok][order], linewidths=0, rasterized=True)
    on_mug = ok & (pts[:, 2] > table_z + 0.006)

    tips = np.array([T[:3, 3] + T[:3, 2] * FINGERTIP for T in cand.poses])
    tx, ty, _ = project(tips, view, proj, W, H)
    others = np.arange(len(tips)) != CHOSEN
    ax.scatter(tx[others], ty[others], s=38, color="white", edgecolors=INK, linewidths=1.0, zorder=4)
    xs, ys = [px[on_mug], tx], [py[on_mug], ty]
    for p0, p1 in gripper_lines(cand.poses[CHOSEN]):
        qx, qy, _ = project(np.array([p0, p1]), view, proj, W, H)
        xs.append(qx); ys.append(qy)
        ax.plot(qx, qy, color=BLUE, lw=2.8, zorder=5, solid_capstyle="round")
    xs, ys = np.concatenate(xs), np.concatenate(ys)
    pad = 0.12 * max(np.ptp(xs), np.ptp(ys))
    ax.set_xlim(xs.min() - pad, xs.max() + pad)
    ax.set_ylim(ys.max() + pad, ys.min() - pad)
    ax.set_aspect("equal")
    ax.axis("off")
    return ("(b) point cloud: 25 grasp candidates",
            f"White dots: where each candidate's fingers close.\nBlue: candidate {CHOSEN}, the one executed.\n"
            "One head-camera view, so only the near side exists.")


def panel_base(ax, scene, cand):
    k = scene.keepout_xy
    ax.scatter(k[:, 0], k[:, 1], s=26, marker="s", color="#e7e5e0", linewidths=0, zorder=1)
    t = cand.aff_center_3d
    ax.add_patch(plt.Circle(t[:2], s3.REACH_M, fill=False, color="#cfcdc7", lw=1))
    ax.text(t[0] - s3.REACH_M * np.cos(0.5) - 0.02, t[1] - s3.REACH_M * np.sin(0.5),
            "arm reach\n0.63 m", ha="right", va="center", fontsize=8, color=INK_3)
    order = [i for i in range(len(cand.poses)) if i != CHOSEN] + [CHOSEN]
    for i in order:
        if np.isnan(cand.base_x[i]):
            continue
        bx, by, yaw = cand.base_x[i], cand.base_y[i], cand.base_yaw_rad[i]
        chosen = i == CHOSEN
        if chosen:   # HSR base footprint (~0.43 m across) at the executed pose
            ax.add_patch(plt.Circle((bx, by), 0.215, fill=False, color=BLUE, lw=1.4, zorder=2))
        ax.annotate("", xy=(bx + 0.12 * np.cos(yaw), by + 0.12 * np.sin(yaw)), xytext=(bx, by),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE if chosen else INK_3,
                                    lw=2.2 if chosen else 0.9, mutation_scale=12),
                    zorder=4 if chosen else 3)
    ax.scatter([0], [0], s=60, marker="o", facecolors=SURFACE, edgecolors=INK_2, linewidths=1.5, zorder=4)
    ax.text(0.0, -0.05, "start", ha="center", va="top", fontsize=8.5, color=INK_2)
    target_marker(ax, t[0], t[1])
    ax.text(t[0], t[1] + 0.05, "mug", ha="center", va="bottom", fontsize=8.5, color=INK_2)
    ax.set_xlim(-0.35, 0.95)
    ax.set_ylim(-0.42, 0.42)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(HAIRLINE)
    ax.plot([0.55, 0.85], [-0.38, -0.38], color=INK_2, lw=1.5)
    ax.text(0.70, -0.37, "0.3 m", ha="center", va="bottom", fontsize=8, color=INK_2)
    n_ok = int(np.nansum(cand.arm_only_ok))
    return ("(c) where to stand, seen from above",
            f"Arrows: a base pose for each grasp ({n_ok}/25 reachable).\n"
            "Blue circle: robot footprint. Squares: table, kept 0.32 m clear.")


def panel_robot(ax, scene):
    client, rid, jidx = s3.connect_and_load()
    s3.pose_robot(client, rid, jidx, scene.base_selected, scene.joints_selected)
    center = np.array([scene.base_selected[0] + 0.25, scene.base_selected[1], 0.6])
    W, H = 900, 900
    view, proj, _ = s3.view_and_projection(s3.CAM_ISO, center, 2.3, aspect=1.0)
    rgba = s3.mask_transparent_background(s3.render_robot(client, W, H, view, proj))
    near, cols = rgbd.scene_near(EXP + "/head_capture_real.npz", scene.target, 0.6)
    px, py, depth, ok = s3.project_points(near, view, proj, W, H)
    o = np.argsort(-depth[ok])
    ax.scatter(px[ok][o], py[ok][o], s=1.6, c=cols[ok][o], linewidths=0, rasterized=True, zorder=1)
    ax.imshow(rgba, zorder=2)
    tx, ty, _ = project(scene.target, view, proj, W, H)
    target_marker(ax, tx, ty)
    ax.set_xlim(60, W - 60)
    ax.set_ylim(H - 40, 80)
    ax.axis("off")
    return ("(d) the HSR at that pose, from its URDF",
            f"The planner's base pose and joint angles for\ncandidate {CHOSEN}, over the real-colour point cloud.")


def main():
    cap = fd.load_capture(EXP)
    g = fd.load_grounding(EXP)
    cand = fd.load_grasp_candidates(EXP)
    scene = s3.build_scene(EXP)
    cloud = fd.load_fused_cloud(EXP)

    fig = plt.figure(figsize=(16, 5.6))
    title(fig, "One real run, from camera frame to robot pose",
          "Experiment log of 7 Aug 2026. Every panel is drawn from that run's own files; "
          "the orange + is the same 3D grasp target in each.")
    panels = [panel_camera, panel_grasps, panel_base, panel_robot]
    args = [(cap, g), (cloud, cand), (scene, cand), (scene,)]
    for i, (fn, a) in enumerate(zip(panels, args)):
        x = 0.01 + i * 0.25
        ax = fig.add_axes([x, 0.17, 0.225, 0.58])
        head, cap_text = fn(ax, *a)
        fig.text(x, 0.79, head, fontsize=11, color=INK, ha="left", va="bottom")
        fig.text(x, 0.13, cap_text, fontsize=9, color=INK_2, ha="left", va="top", linespacing=1.4)
    save(fig, "real_run")


if __name__ == "__main__":
    main()
