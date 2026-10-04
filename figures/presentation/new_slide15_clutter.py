"""
new_slide15_clutter.py -- Slide 15: Object + Clutter Generalisation.

Purpose: unify NEW-E (isolated-vs-cluttered slope) and NEW-G (real fused
clutter cloud) into one coherent experiment: the SAME real pipeline can
produce opposite geometric gate outcomes for the SAME object, and the real
3D scene that number came from is a genuine 8-object clutter cloud, not a
toy scene.

Scientific claim: unchanged from NEW-E/NEW-G -- re-presents their already-
verified real numbers/cloud side by side, no new measurement. Preserves both
caveats verbatim: (1) this is measurement instability, not evidence clutter
universally degrades perception (remote moves the OPPOSITE direction); (2)
NEW-G's live re-decomposition is a fresh derivation, NOT asserted to equal
NEW-E's cached 46mm.
Required real data: batch_scene_analysis.csv (via new_e_isolated_vs_cluttered
  .load_rows(), real, unchanged); captures_0723/cap_pot_with_handle_and_lid
  .npz + cap_cluster_mug_cokecan_pot.npz (real RGB); batch_out/
  cluster_mug_cokecan_pot_fused_cloud.npz (real, 237,991 pts, via
  new_g_clutter_scene_3d.py's own real scene_objects.find_objects() call).

Run: python new_slide15_clutter.py
Output: report_assets/figures/slide15_clutter.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

import figlayout as fl
import figstyle as fs
import new_e_isolated_vs_cluttered as fig_e
import new_g_clutter_scene_3d as fig_g
import scene3d as s3


def render(out_path=None):
    out_path = out_path or os.path.join("report_assets", "figures", "slide15_clutter.png")
    rows = fig_e.load_rows()
    iso, clut = rows["pot_with_handle_and_lid"], rows["cluster_mug_cokecan_pot"]
    w_iso, w_clut = float(iso["minor_mm"]), float(clut["minor_mm"])

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Same Pipeline, Opposite Gate Outcome for the Same Object", **fs.TITLE, x=fs.MARGIN, ha="left")

    # -- LEFT: real isolated / cluttered thumbnails
    THUMB_CROP = (110, 190, 560, 500)
    x0c, y0c, x1c, y1c = THUMB_CROP
    ax_iso = fig.add_axes([0.02, 0.50, 0.135, 0.34])
    ax_clut = fig.add_axes([0.02, 0.12, 0.135, 0.34])
    for ax_img, npz_name, label in [(ax_iso, fig_e.SLIDE_ISO_NPZ, "isolated"),
                                     (ax_clut, fig_e.SLIDE_CLUT_NPZ, "cluttered")]:
        d = np.load(os.path.join(fig_e.CAPTURES_DIR, npz_name))
        ax_img.imshow(d["rgb"][y0c:y1c, x0c:x1c])
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spine in ax_img.spines.values():
            spine.set_color(fs.FAINT)
            spine.set_linewidth(2)
        ax_img.set_title(label, color=fs.INK, fontsize=16, weight="bold", family=fs.FONT, pad=6)

    # -- CENTER: slope chart (pot only -- the dominant, dissertation-relevant example)
    ax = fig.add_axes([0.24, 0.14, 0.36, 0.68])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(0, 160)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["ISOLATED", "CLUTTERED"], color=fs.INK, fontsize=16, weight="bold", family=fs.FONT)
    ax.set_ylabel("graspable width, mm", color=fs.MUTED, fontsize=16, family=fs.FONT)
    ax.tick_params(colors=fs.MUTED, labelsize=16)
    for spine in ax.spines.values():
        spine.set_color(fs.FAINT)
    ax.axhline(125, color=fs.MUTED, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.text(1.28, 128, "125mm aperture", ha="right", va="bottom", color=fs.MUTED, fontsize=16, family=fs.FONT)

    ax.scatter([0], [w_iso], s=200, color=fs.REJECTED, zorder=5, edgecolors=fs.SLIDE_BG, linewidths=1.5)
    ax.scatter([1], [w_clut], s=200, color=fs.ACCEPTED, zorder=5, edgecolors=fs.SLIDE_BG, linewidths=1.5)
    ax.add_patch(FancyArrowPatch((0, w_iso), (1, w_clut), color=fs.CANDIDATE, linewidth=3.0,
                                  arrowstyle="-|>", mutation_scale=18, zorder=4))
    ax.text(0, w_iso + 8, "REFUSE", ha="center", va="bottom", color=fs.REJECTED, fontsize=22, weight="bold",
            family=fs.FONT)
    ax.text(1, w_clut - 8, "PASS", ha="center", va="top", color=fs.ACCEPTED, fontsize=22, weight="bold",
            family=fs.FONT)
    fig.text(0.42, 0.855, f"{w_iso:.0f}mm \u2192 {w_clut:.0f}mm", ha="center", color=fs.INK, fontsize=48,
              weight="bold", family=fs.FONT)

    # -- RIGHT: real fused 3D clutter cloud (reuses NEW-G's own live pipeline call)
    d = np.load(fig_g.CLOUD_PATH)
    cloud = d["points"]
    rng = np.random.default_rng(fs.SEED)
    cloud_show = cloud[rng.choice(len(cloud), 40_000, replace=False)] if len(cloud) > 40_000 else cloud
    table = {"plane_z": fig_g.REAL_TABLE_PLANE_Z, "x": (cloud[:, 0].min(), cloud[:, 0].max()),
             "y": (cloud[:, 1].min(), cloud[:, 1].max())}
    from intent_grasp import scene_objects as so
    _, objs = so.find_objects(cloud, table=table)
    all_obj_pts = np.vstack([o["points"] for o in objs])
    bbox_min, bbox_max = all_obj_pts.min(axis=0), all_obj_pts.max(axis=0)
    center = (bbox_min + bbox_max) / 2
    extent = max(float(np.linalg.norm(bbox_max - bbox_min)), 0.4) * 1.15
    near = np.linalg.norm(cloud_show[:, :2] - center[:2], axis=1) < extent * 0.75
    cloud_show = cloud_show[near]
    width, height = 900, 900
    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)

    ax_cloud = fig.add_axes([0.63, 0.14, 0.35, 0.68])
    ax_cloud.set_facecolor(fs.SLIDE_BG)
    ax_cloud.set_xlim(0, width)
    ax_cloud.set_ylim(height, 0)
    ax_cloud.axis("off")
    cpx, cpy, cdepth, cvalid = s3.project_points(cloud_show, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax_cloud.scatter(cpx[on], cpy[on], s=2.0, color=fs.MUTED, alpha=0.65, zorder=1, linewidths=0)
    for i, o in enumerate(objs):
        p = o["points"]
        px, py, depth, valid = s3.project_points(p, view, proj, width, height)
        onm = valid & (px > -20) & (px < width + 20) & (py > -20) & (py < height + 20)
        ax_cloud.scatter(px[onm], py[onm], s=3.5, color=fig_g.OBJECT_COLORS[i % len(fig_g.OBJECT_COLORS)],
                          alpha=0.9, zorder=2, linewidths=0)
    ax_cloud.set_title("real fused cloud, 8 objects, 237,991 pts", color=fs.INK, fontsize=16, weight="bold",
                       family=fs.FONT, pad=8)

    # Caveat ("measurement instability, not a general clutter claim") moves
    # to speaker notes -- no room to place it on-slide without colliding
    # with the x-axis tick labels directly below the chart.
    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y,
                               "batch_scene_analysis.csv + cluster_mug_cokecan_pot_fused_cloud.npz", **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("Slide 15 clutter", [
        "Pot: 147mm isolated (REFUSE, over 125mm aperture) -> 46mm cluttered (PASS). Same real object,",
        "same real pipeline, opposite gate outcome.",
        "Remote (not plotted here, see NEW-E report variant): 13mm isolated -> 73mm cluttered, both PASS",
        "-- moves the OPPOSITE direction from the pot. This is why the claim is 'measurement instability',",
        "not a general 'clutter degrades perception' law.",
        "Spoon has no cluttered-capture row in this dataset -- not shown, not inferred.",
        "Only 5 real scenes exist in this dataset -- not generalised beyond them.",
        "Fused cloud: real, 237,991 pts, batch_out/cluster_mug_cokecan_pot_fused_cloud.npz. 8 real objects",
        "found live via scene_objects.find_objects() -- table plane corrected to this cloud's own real",
        "z=0.463 peak (see new_g_clutter_scene_3d.py docstring).",
        "Object IDENTITY in the cloud (which cluster is 'the pot') was not re-derived to pixel-exact",
        "correspondence with the original batch run -- see NEW-G's own honesty note.",
    ])
    return out_path, report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(out_path=args.out)
    print(f"slide15 written to {path}")
    print(report.summary())
