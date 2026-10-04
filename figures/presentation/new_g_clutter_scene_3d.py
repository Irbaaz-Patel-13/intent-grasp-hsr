"""
new_g_clutter_scene_3d.py -- NEW-G: Clutter Scene, 3D (visual companion to
NEW-E).

Scientific claim: the cluttered scene NEW-E's "pot: 46mm, PASS" number
comes from is a real, multi-object fused point cloud, not a single-object
crop -- the pot in this figure's rendering is one of several distinct real
objects, sharing the scene with real clutter.
Supporting evidence: batch_out/cluster_mug_cokecan_pot_fused_cloud.npz
  (real fused cloud, 237,991 points -- confirmed multi-view, not
  single-view, before building this figure). Object segmentation:
  scene_objects.find_objects(), the same real, seedless multi-object
  finder used elsewhere in this project, run live this session (table
  plane_z corrected to the real 0.463 peak in this cloud's own z-histogram
  -- find_table()'s default histogram search locked onto this fused
  cloud's floor points instead, since this multi-view fusion's FOV extends
  to the floor unlike the narrower single-view captures find_table() was
  tuned against; documented here, not silently worked around).
Required real data: the real fused cloud; 8 real object clusters found by
  a real, unmodified pipeline function.
Honesty note (read before citing): exact per-cluster object IDENTITY
  (which of the 8 real clusters is "the pot" vs "the mug" vs "the
  cokecan") was NOT re-derived to pixel-exact correspondence with the
  original batch_scene_analysis.py run for this figure -- that run used a
  seeded crop from its own affordance-reasoning stage, which this
  companion visualization does not replay. The cluster shown decomposed
  here is identified only by real geometric plausibility (span closest to
  a pot-sized object among the 8) and captioned as such. Its own live
  decomposition numbers (32mm main_body, 15mm lateral_protrusion) are a
  FRESH derivation from this session, not asserted to equal NEW-E's cached
  46mm -- NEW-E remains the authoritative number for that claim.

Run: python new_g_clutter_scene_3d.py
Output: generated_assets/new_g/new_g_clutter_scene_3d.png
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figlayout as fl
import figstyle as fs
from intent_grasp import part_adaptive as pa
import scene3d as s3
from intent_grasp import scene_objects as so
from intent_grasp.paths import WORKSPACE
CLOUD_PATH = os.path.join(str(WORKSPACE), "batch_out",
                           "cluster_mug_cokecan_pot_fused_cloud.npz")
# real RGB of the SAME scene this fused cloud comes from -- confirmed to exist
SLIDE_RGB_PATH = os.path.join(str(WORKSPACE), "captures_0723",
                               "cap_cluster_mug_cokecan_pot.npz")
REAL_TABLE_PLANE_Z = 0.463  # real secondary z-histogram peak in this cloud; see module docstring
DECOMPOSED_OBJECT_IDX = 3   # most pot-plausible span among the 8 real clusters; see module docstring

OBJECT_COLORS = [fs.MUTED, "#7C8A99", "#8E97A6", fs.CANDIDATE, "#6E7B87", "#5F6C78", "#96A0AC", "#828E99"]
COMPONENT_COLOR = {"main_body": fs.INK, "lateral_protrusion": fs.REJECTED, "top_protrusion": fs.CANDIDATE,
                    "segment_a": fs.REASONING, "segment_b": fs.REASONING, "segment_c": fs.REASONING}


def render_report(out_path=None):
    out_path = out_path or os.path.join(fs.asset_dir("new_g"), "new_g_clutter_scene_3d.png")
    d = np.load(CLOUD_PATH)
    cloud = d["points"]
    rng = np.random.default_rng(fs.SEED)
    if len(cloud) > 60_000:
        cloud_show = cloud[rng.choice(len(cloud), 60_000, replace=False)]
    else:
        cloud_show = cloud

    table = {"plane_z": REAL_TABLE_PLANE_Z, "x": (cloud[:, 0].min(), cloud[:, 0].max()),
             "y": (cloud[:, 1].min(), cloud[:, 1].max())}
    _, objs = so.find_objects(cloud, table=table)

    target = objs[DECOMPOSED_OBJECT_IDX]["points"]
    comp, info = pa.find_components(target, z_table=REAL_TABLE_PLANE_Z)
    desc = pa.describe_components(comp, info)

    # Frame the real tabletop-object cluster tightly, not the full raw
    # cloud's extent -- this fused cloud has sparse real points scattered
    # far beyond the objects themselves (consistent with the far-view
    # background inclusion already documented elsewhere in this project),
    # which would otherwise dominate the camera framing at near-zero
    # visual density. Cropping to the real objects' own combined bounding
    # box (+ margin) is the same precedent as Figure 8's keep-out crop.
    all_obj_pts = np.vstack([o["points"] for o in objs])
    bbox_min, bbox_max = all_obj_pts.min(axis=0), all_obj_pts.max(axis=0)
    center = (bbox_min + bbox_max) / 2
    extent = max(float(np.linalg.norm(bbox_max - bbox_min)), 0.4) * 1.15
    near = np.linalg.norm(cloud_show[:, :2] - center[:2], axis=1) < extent * 0.75
    cloud_show = cloud_show[near]
    width, height = 1700, 1150
    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("Clutter Scene, 3D -- Companion to Figure NEW-E", **fs.TITLE, x=fs.MARGIN, ha="left")
    fig.text(fs.MARGIN, 0.885,
              "Real fused cluttered-scene cloud (237,991 pts) -- the pot NEW-E measures shares this scene "
              "with 7 other real objects", **fs.BODY)

    ax = fig.add_axes([0.035, 0.14, 0.68, 0.68])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    # Was near-black (fs.FAINT at alpha=0.35 on the near-black SLIDE_BG) --
    # raised to fs.MUTED at higher alpha/size so the real background cloud
    # is actually visible, not just technically present.
    cpx, cpy, cdepth, cvalid = s3.project_points(cloud_show, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=1.8, color=fs.MUTED, alpha=0.65, zorder=1, linewidths=0)

    for i, o in enumerate(objs):
        if i == DECOMPOSED_OBJECT_IDX:
            continue
        p = o["points"]
        px, py, depth, valid = s3.project_points(p, view, proj, width, height)
        on = valid & (px > -20) & (px < width + 20) & (py > -20) & (py < height + 20)
        ax.scatter(px[on], py[on], s=3.0, color=OBJECT_COLORS[i % len(OBJECT_COLORS)], alpha=0.9,
                   zorder=2, linewidths=0)

    for name, pts in comp.items():
        px, py, depth, valid = s3.project_points(pts, view, proj, width, height)
        on = valid & (px > -20) & (px < width + 20) & (py > -20) & (py < height + 20)
        ax.scatter(px[on], py[on], s=6, color=COMPONENT_COLOR.get(name, fs.MUTED), zorder=4, linewidths=0)

    ax_info = fig.add_axes([0.74, 0.16, 0.24, 0.64])
    ax_info.axis("off")
    ax_info.add_patch(matplotlib.patches.Rectangle((0, 0), 1, 1, transform=ax_info.transAxes, fill=False,
                                                     edgecolor=fs.FAINT, linewidth=1.0))
    ax_info.text(0.06, 0.94, "8 real objects found", transform=ax_info.transAxes, ha="left", va="top",
                 color=fs.MUTED, fontsize=10, weight="bold", family=fs.FONT)
    ax_info.text(0.06, 0.87, "(scene_objects.find_objects, live)", transform=ax_info.transAxes, ha="left",
                 va="top", color=fs.MUTED, fontsize=10, family=fs.FONT, style="italic")
    ax_info.text(0.06, 0.74, "Decomposed this session\n(most pot-plausible span):", transform=ax_info.transAxes,
                 ha="left", va="top", color=fs.INK, fontsize=10, weight="bold", family=fs.FONT)
    y = 0.60
    for name, d_ in desc.items():
        c = COMPONENT_COLOR.get(name, fs.MUTED)
        ax_info.text(0.06, y, f"{name}: {d_['n']}pts / {d_['closing_width_mm']}mm ({d_['evidence']})",
                     transform=ax_info.transAxes, ha="left", va="top", color=c, fontsize=10, family=fs.FONT)
        y -= 0.075
    ax_info.text(0.06, y - 0.03, "Fresh live derivation, not\nasserted to equal NEW-E's\ncached 46mm.",
                 transform=ax_info.transAxes, ha="left", va="top", color=fs.MUTED, fontsize=10, family=fs.FONT,
                 style="italic", linespacing=1.4)

    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.036,
              "Faint grey: full real cloud. Muted blue-grey clusters: the other 7 real objects, not "
              "independently decomposed by the original batch run. Colored points: this session's live",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y + 0.018,
              "decomposition of the object identified as most pot-plausible by span, NOT pixel-matched to "
              "the original run's exact seed/crop -- see module docstring for the honesty note in full.",
              **fs.CAPTION)
    fig.text(fs.MARGIN, fs.CAPTION_Y,
              "Source: batch_out/cluster_mug_cokecan_pot_fused_cloud.npz (real, multi-view). "
              "Table plane corrected to this cloud's own real z=0.463 peak (see docstring).",
              **fs.CAPTION)
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_invariants(fig)
    plt.close(fig)
    return out_path, report


def render_slide(out_path=None):
    """Slide variant: the brightened 3D cloud paired with the real RGB photo
    of the same scene (confirmed to exist -- captures_0723/
    cap_cluster_mug_cokecan_pot.npz)."""
    out_path = out_path or os.path.join(fs.asset_dir("new_g"), "new_g_clutter_scene_3d_slide.png")
    d = np.load(CLOUD_PATH)
    cloud = d["points"]
    rng = np.random.default_rng(fs.SEED)
    if len(cloud) > 60_000:
        cloud_show = cloud[rng.choice(len(cloud), 60_000, replace=False)]
    else:
        cloud_show = cloud

    table = {"plane_z": REAL_TABLE_PLANE_Z, "x": (cloud[:, 0].min(), cloud[:, 0].max()),
             "y": (cloud[:, 1].min(), cloud[:, 1].max())}
    _, objs = so.find_objects(cloud, table=table)
    all_obj_pts = np.vstack([o["points"] for o in objs])
    bbox_min, bbox_max = all_obj_pts.min(axis=0), all_obj_pts.max(axis=0)
    center = (bbox_min + bbox_max) / 2
    extent = max(float(np.linalg.norm(bbox_max - bbox_min)), 0.4) * 1.15
    near = np.linalg.norm(cloud_show[:, :2] - center[:2], axis=1) < extent * 0.75
    cloud_show = cloud_show[near]
    width, height = 1300, 1300
    view, proj, eye = s3.view_and_projection(s3.CAM_ISO, center, extent, aspect=width / height)

    fig = plt.figure(figsize=(fs.FIG_W_IN, fs.FIG_H_IN), dpi=fs.DPI, facecolor=fs.SLIDE_BG)
    fig.suptitle("8 Real Objects, One Fused Cloud", **{**fs.TITLE, "size": 32}, x=fs.MARGIN, ha="left")

    rgb = np.load(SLIDE_RGB_PATH)["rgb"]
    ax_rgb = fig.add_axes([0.03, 0.10, 0.44, 0.74])
    ax_rgb.imshow(rgb)
    ax_rgb.set_xticks([])
    ax_rgb.set_yticks([])
    for spine in ax_rgb.spines.values():
        spine.set_color(fs.FAINT)
        spine.set_linewidth(2)
    ax_rgb.set_title("real RGB, same scene", color=fs.INK, fontsize=18, weight="bold", family=fs.FONT, pad=8)

    ax = fig.add_axes([0.51, 0.10, 0.46, 0.68])
    ax.set_facecolor(fs.SLIDE_BG)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.set_title("fused 3D cloud (237,991 pts)", color=fs.INK, fontsize=18, weight="bold", family=fs.FONT, pad=8)

    cpx, cpy, cdepth, cvalid = s3.project_points(cloud_show, view, proj, width, height)
    on = cvalid & (cpx > -20) & (cpx < width + 20) & (cpy > -20) & (cpy < height + 20)
    ax.scatter(cpx[on], cpy[on], s=2.2, color=fs.MUTED, alpha=0.7, zorder=1, linewidths=0)
    for i, o in enumerate(objs):
        p = o["points"]
        px, py, depth, valid = s3.project_points(p, view, proj, width, height)
        on = valid & (px > -20) & (px < width + 20) & (py > -20) & (py < height + 20)
        ax.scatter(px[on], py[on], s=4.0, color=OBJECT_COLORS[i % len(OBJECT_COLORS)], alpha=0.95,
                   zorder=2, linewidths=0)

    fig.text(0.51, 0.855, "8", color=fs.CANDIDATE, fontsize=52, weight="bold", family=fs.FONT)
    fig.text(0.565, 0.865, "real objects found", color=fs.INK, fontsize=18, weight="bold", family=fs.FONT)

    caption_kw = {**fs.CAPTION, "size": 16}
    caption_texts = [fig.text(fs.MARGIN, fs.CAPTION_Y,
                               "batch_out/cluster_mug_cokecan_pot_fused_cloud.npz + cap_cluster_mug_cokecan_pot.npz",
                               **caption_kw)]
    fig.savefig(out_path, facecolor=fs.SLIDE_BG)

    report = fl.run_slide_invariants(fig, caption_texts)
    plt.close(fig)

    fl.print_speaker_notes("NEW-G clutter scene 3D", [
        "Companion to NEW-E's pot measurement -- this is the real multi-object scene that number comes from.",
        f"Table plane corrected to this cloud's own real z={REAL_TABLE_PLANE_Z} peak (find_table()'s default "
        "search locked onto floor points instead -- this fusion's FOV reaches the floor, unlike narrower "
        "single-view captures find_table() was tuned against).",
        "Object IDENTITY (which cluster is 'the pot' vs 'the mug') was NOT re-derived to pixel-exact "
        "correspondence with the original batch run -- not decomposed in this slide image.",
        "Report variant additionally shows a live re-decomposition of the most pot-plausible cluster "
        "(fresh derivation, not asserted to equal NEW-E's cached 46mm).",
    ])
    return out_path, report


def render(variant="report", out_path=None):
    if variant == "report":
        return render_report(out_path=out_path)
    if variant == "slide":
        return render_slide(out_path=out_path)
    raise ValueError(f"unknown variant {variant!r}, expected 'report' or 'slide'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", choices=["report", "slide"], default="report")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    path, report = render(variant=args.variant, out_path=args.out)
    print(f"new_g ({args.variant}) written to {path}")
    print(report.summary())
