"""
fig06_grasp_candidates.py -- Figure 6: Grasp Generation (v2 -- 3D
canonical-scene rebuild).

Scientific question: how does the grounded task/part region become a set of
discrete, scored 6-DoF grasp hypotheses -- and which one gets executed?
Scientific claim: a real grasp-generation run on this exact capture produced
25 candidate poses with real, non-trivial quality/affordance/combined
scores. The candidate actually executed on real hardware (#24) is NOT the
top-ranked candidate by this figure's own combined_score -- a different,
real, execution-feasibility criterion (Figure 7) determined selection. The
executed candidate is now shown as the REAL posed robot/gripper mesh (FK-
validated), on the object, at real scale -- not an abstract marker.
Supporting evidence: Experiment_Logs/2026-08-07/grasps_plain.npz (25 real
  poses, quality_score/affordance_score/combined_score/manip via
  fig_data.load_grasp_candidates); place_run.csv (candidate 24's real FK-
  validated joint values, via scene3d.build_scene). See
  docs/evidence/FIGURES_5_7_EVIDENCE_AUDIT.md for the numeric verification
  (combined_score range [2.3615, 3.1411], candidate 24 = 2.3615, the lowest
  in the set -- rank 25/25).
Required real data: all 25 poses, combined_score, manip -- used directly.
Required diagrammatic elements: rejected-candidate approach vectors are a
  deterministic derivation (each pose's own rotation matrix, local +z axis)
  from the real saved pose -- not an invented direction, same convention as
  v1. The posed robot/gripper is candidate 24's real FK-validated pose
  (scene3d.py); its finger aperture is the URDF default (no real per-
  candidate aperture was logged for this generation step), stated as such.

Run: python fig06_grasp_candidates.py [--exp-dir DIR]
Output: generated_assets/fig06/fig06_grasp_candidates.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs
import fig_data as fd
import scene3d as s3

EXECUTED_CANDIDATE = s3.EXECUTED_CANDIDATE
APPROACH_LEN_M = 0.035
SELECTED_RGBA = (0.55, 0.80, 0.62, 1.0)


def render_hero_3d(scene, gc, width=1700, height=1200):
    client = s3.connect()
    robot_id, ji = s3.load_robot(client, rgba=SELECTED_RGBA)
    s3.pose_robot(client, robot_id, ji, scene.base_selected, scene.joints_selected)

    origins = gc.poses[:, :3, 3]
    bx, by = scene.base_selected[0], scene.base_selected[1]
    center = np.array([bx, by, scene.target[2]])
    extent = 1.5

    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)
    robot_rgba = s3.render_robot(client, width, height, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    import pybullet as pb
    pb.disconnect(client)

    fig = plt.figure(figsize=(fs.FIG_W_IN * 0.86, fs.FIG_H_IN * 0.78), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    cpx, cpy, cdepth, cvalid = s3.project_points(scene.cloud, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=1.8, color=fs.MUTED, alpha=0.5, zorder=1, linewidths=0)

    cmap = matplotlib.colormaps["magma"]
    s_ = gc.combined_score
    s_norm = (s_ - s_.min()) / max(s_.max() - s_.min(), 1e-6)
    pt_colors = cmap(s_norm)[:, :3]

    ax.imshow(robot_rgba, extent=[0, width, height, 0], zorder=2)

    # Rejected-candidate pose axes are drawn AFTER (on top of) the opaque
    # robot raster, not before it -- the candidates cluster tightly around
    # the same small object as the executed grasp, so most fall spatially
    # behind/inside the robot silhouette; drawing them on top (a standard
    # "reference overlay" convention) is what keeps all 25 real poses
    # visible rather than mostly occluded.
    approach = gc.poses[:, :3, 2]
    for i in range(len(origins)):
        if i == EXECUTED_CANDIDATE:
            continue
        a, b = origins[i], origins[i] + approach[i] * APPROACH_LEN_M
        px, py, depth, valid = s3.project_points(np.array([a, b]), view, proj, width, height)
        if valid.all():
            ax.plot(px, py, color=pt_colors[i], linewidth=1.6, alpha=0.95, zorder=3)
            ax.scatter([px[0]], [py[0]], s=16, color=pt_colors[i], zorder=3, linewidths=0)

    ex_a, ex_b = origins[EXECUTED_CANDIDATE], origins[EXECUTED_CANDIDATE] + approach[EXECUTED_CANDIDATE] * APPROACH_LEN_M * 1.6
    epx, epy, edepth, evalid = s3.project_points(np.array([ex_a, ex_b]), view, proj, width, height)
    if evalid.all():
        ax.plot(epx, epy, color=fs.ACCEPTED, linewidth=2.6, zorder=4)

    return fig


def render(exp_dir=fd.DEFAULT_EXP_DIR, out_path=None):
    scene = s3.build_scene(exp_dir)
    gc = fd.load_grasp_candidates(exp_dir)
    out_path = out_path or os.path.join(fs.asset_dir("fig06"), "fig06_grasp_candidates.png")

    hero_fig = render_hero_3d(scene, gc)
    hero_path = os.path.join(fs.asset_dir("fig06"), "_hero_tmp.png")
    hero_fig.savefig(hero_path, facecolor=fs.SLIDE_BG)
    plt.close(hero_fig)
    hero_img = mpimg.imread(hero_path)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Figure 6 -- Grasp Generation", **fs.TITLE, x=fs.MARGIN, ha="left")

    exec_score = gc.combined_score[EXECUTED_CANDIDATE]
    rank = int((gc.combined_score > exec_score).sum()) + 1
    fig.text(fs.MARGIN, 0.885,
              f"25 real candidates (colored by combined_score) -- executed #{EXECUTED_CANDIDATE} "
              f"(green, real posed robot) ranks {rank}/25, not top-ranked", **fs.BODY)

    ax = fig.add_axes([0.06, 0.12, 0.88, 0.72])
    ax.imshow(hero_img)
    ax.axis("off")

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "Rendered from candidate 24's real FK-validated joint values through the HSR URDF -- geometry "
              "is the robot description, pose is measured; not a photograph. Thin lines: the other 24 real",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              f"candidate poses, colored by combined_score [{gc.combined_score.min():.2f}, "
              f"{gc.combined_score.max():.2f}]. Selection uses a downstream feasibility criterion (Fig. 7).",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    if os.path.exists(hero_path):
        os.remove(hero_path)
    return out_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exp-dir", default=fd.DEFAULT_EXP_DIR)
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path = render(exp_dir=args.exp_dir, out_path=args.out)
    print(f"fig06 written to {path}")
