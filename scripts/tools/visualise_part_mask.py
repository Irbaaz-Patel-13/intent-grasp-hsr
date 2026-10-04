#!/usr/bin/env python
r"""visualise_part_mask.py -- render what CGN was actually scoped to.

Overlays the whole-object mask and the part mask on the capture RGB, and marks
the selected grasps, so "CGN SCOPED to 'lateral_protrusion': 245 px" can be
checked by eye instead of taken on trust -- essential in cluttered scenes where
the crop may have swallowed a neighbouring object.

    .\.venv\Scripts\python.exe visualise_part_mask.py --part handle
    .\.venv\Scripts\python.exe visualise_part_mask.py --part "lid knob" --out fig.png
Reads grasps_out.npz + fused_cloud.npz + multiview.npz from the last run.
"""
import argparse, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from intent_grasp import part_adaptive as pa
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default=None, help="override the VLM's part name")
    ap.add_argument("--out", default="fig_part_mask.png")
    ap.add_argument("--view", type=int, default=None)
    a = ap.parse_args()

    g = np.load("grasps_out.npz", allow_pickle=True)
    rgb = np.asarray(g["grounding_rgb"])
    obj_mask = np.asarray(g["object_mask"]) if "object_mask" in g.files else None
    aff_mask = np.asarray(g["affordance_mask"])
    aff = np.asarray(g["aff_center_3d"]).ravel()
    vlm_part = a.part or (str(g["target_part"]) if "target_part" in g.files else "handle")
    obj_name = str(g["target_object"]) if "target_object" in g.files else "?"
    instr = str(g["instruction"]) if "instruction" in g.files else ""

    mv = np.load("multiview.npz", allow_pickle=True)
    vi = a.view if a.view is not None else 0
    K = np.asarray(mv["camera_intrinsics"])
    K = K[vi] if K.ndim == 3 else K
    extr = np.asarray(mv["camera_extrinsics"])[vi]

    z = np.load("fused_cloud.npz", allow_pickle=True)
    cloud = None
    for k in z.files:
        arr = np.asarray(z[k])
        if arr.ndim == 2 and arr.shape[1] == 3 and arr.shape[0] > 1000:
            cloud = arr.astype(float); break

    near = cloud[np.linalg.norm(cloud[:, :2] - aff[:2], axis=1) < 0.25]
    hh, ee = np.histogram((near if len(near) > 200 else cloud)[:, 2], bins=80)
    z_table = float(0.5 * (ee[int(np.argmax(hh))] + ee[int(np.argmax(hh)) + 1]))
    obj, r = pa.adaptive_crop(cloud, aff[:2], z_table=z_table, start=0.06,
                              step=0.02, max_radius=0.16)
    obj, iso = pa.isolate_object(obj, aff[:2])
    print("isolation: %s" % iso)
    shape = pa.classify_shape(obj, z_table)
    comp, info = pa.find_components(obj, z_table=z_table)
    desc = pa.describe_components(comp, info)
    nm, pp, sc, note = pa.bind_part(vlm_part, comp, desc, keep_clear=[],
                                    linearity=shape["linearity"])
    print("crop %.2f m, %d pts, %s" % (r, len(obj), shape["shape_class"]))
    print(note)

    H, W = rgb.shape[:2]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), dpi=150)
    for ax in axes: ax.axis("off")
    axes[0].imshow(rgb); axes[0].set_title("capture", fontsize=10)

    ov = rgb.copy().astype(float)
    m = aff_mask > 0
    ov[m] = 0.55 * ov[m] + 0.45 * np.array([60, 130, 240])
    axes[1].imshow(ov.astype(np.uint8))
    axes[1].set_title("whole-object mask (%d px)\nwhat CGN used before" % int(m.sum()),
                      fontsize=10)

    ov2 = rgb.copy().astype(float)
    ov2[m] = 0.75 * ov2[m] + 0.25 * np.array([60, 130, 240])
    if pp is not None:
        pm, npx = pa.project_part_to_mask(pp, K, extr, (H, W))
        pmb = pm > 0
        ov2[pmb] = 0.35 * ov2[pmb] + 0.65 * np.array([240, 90, 40])
        ttl = "part mask '%s' -> %s\n%d px (%.0f%% of object)" % (
            vlm_part, nm, npx, 100.0 * npx / max(int(m.sum()), 1))
    else:
        ttl = "no usable part mask\n%s" % note[:60]
    # every other component, outlined, so contamination is visible
    for cname, cpts in comp.items():
        if pp is not None and cname == nm:
            continue
        u, v, zz, ok = pa.project_points_to_pixels(cpts, K, extr)
        ui, vi_ = u[ok], v[ok]
        keep = (ui >= 0) & (ui < W) & (vi_ >= 0) & (vi_ < H)
        axes[2].scatter(ui[keep], vi_[keep], s=0.6, alpha=.35, label=cname)
    axes[2].imshow(ov2.astype(np.uint8))
    axes[2].set_title(ttl, fontsize=10)
    if len(comp) > 1:
        axes[2].legend(loc="lower right", fontsize=6, markerscale=6, framealpha=.75)

    fig.suptitle("%s  |  object: %s   part: '%s'" % (instr, obj_name, vlm_part),
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(a.out, facecolor="white")
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
