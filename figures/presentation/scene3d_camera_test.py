"""
scene3d_camera_test.py -- Stage 1 checkpoint render: one test image per
named camera (CAM_ISO, CAM_SIDE, CAM_TOP), robot posed at candidate 24 +
real point cloud composited via project_points(). Not a dissertation
figure -- a rendering-pipeline validation artifact.

Run: python scene3d_camera_test.py
Output: generated_assets/scene3d_test/cam_{iso,side,top}.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs
import scene3d as s3

WIDTH, HEIGHT = 1000, 720


def render_one(camera, name, scene, client, robot_id, joint_index):
    center = np.array(scene.base_selected[:2] + (0.55,))
    extent = 2.4
    view, proj, eye = s3.view_and_projection(camera, center, extent, aspect=WIDTH / HEIGHT)

    s3.pose_robot(client, robot_id, joint_index, scene.base_selected, scene.joints_selected)
    robot_rgba = s3.render_robot(client, WIDTH, HEIGHT, view, proj)
    robot_rgba = s3.mask_transparent_background(robot_rgba)

    px, py, depth, valid = s3.project_points(scene.cloud, view, proj, WIDTH, HEIGHT)
    onscreen = valid & (px > 0) & (px < WIDTH) & (py > 0) & (py < HEIGHT) & (depth > -1) & (depth < 1)

    fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100, facecolor=fs.SLIDE_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.scatter(px[onscreen], py[onscreen], s=1.5, color=fs.MUTED, alpha=0.6, zorder=1)
    ax.imshow(robot_rgba, extent=[0, WIDTH, HEIGHT, 0], zorder=2)
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(HEIGHT, 0)
    ax.axis("off")
    out_dir = fs.asset_dir("scene3d_test")
    out_path = os.path.join(out_dir, f"cam_{name}.png")
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)
    plt.close(fig)
    return out_path


def main():
    scene = s3.build_scene()
    client, robot_id, joint_index = s3.connect_and_load()
    for camera, name in [(s3.CAM_ISO, "iso"), (s3.CAM_SIDE, "side"), (s3.CAM_TOP, "top")]:
        out = render_one(camera, name, scene, client, robot_id, joint_index)
        print(f"{name} -> {out}")


if __name__ == "__main__":
    main()
