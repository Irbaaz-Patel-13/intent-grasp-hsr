#!/usr/bin/env python
r"""test_components.py -- structural component decomposition on a REAL capture.

    .\.venv\Scripts\python.exe test_components.py pot_with_handle_and_lid
    .\.venv\Scripts\python.exe test_components.py TV_remote --parts handle,sides,"middle section"

Estimates the support plane FIRST (without it the crop grows across the whole
tabletop: a pot measured 283 mm wide and three "lateral protrusions" turned out
to be table edges), then crops adaptively, finds structural components, and
binds the requested part names.
"""
import argparse, glob, os, sys
import numpy as np
from intent_grasp import part_adaptive as pa
def load_cloud(path):
    z = np.load(path, allow_pickle=True)
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 2 and a.shape[1] == 3 and a.shape[0] > 1000:
            return a.astype(float)
    sys.exit("no (N,3) cloud in %s (keys %s)" % (path, list(z.files)))


def estimate_plane(pts, centre_xy, radius=0.25):
    """Support height = modal z of points near the object."""
    near = pts[np.linalg.norm(pts[:, :2] - centre_xy, axis=1) < radius]
    if len(near) < 200:
        near = pts
    h, e = np.histogram(near[:, 2], bins=80)
    return float(0.5 * (e[np.argmax(h)] + e[np.argmax(h) + 1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--dir", default="batch_out")
    ap.add_argument("--parts", default="handle,lid knob,rim,body,sides,middle section")
    ap.add_argument("--max_radius", type=float, default=0.16,
                    help="hard cap on the crop; a tabletop object is rarely wider")
    a = ap.parse_args()

    cf = os.path.join(a.dir, "%s_fused_cloud.npz" % a.scene)
    gf = os.path.join(a.dir, "%s_grasps_plain.npz" % a.scene)
    for f in (cf, gf):
        if not os.path.exists(f):
            sys.exit("missing %s\navailable: %s" % (f, sorted(
                os.path.basename(x) for x in glob.glob(os.path.join(a.dir, "*_fused_cloud.npz")))))
    pts = load_cloud(cf)
    aff = np.asarray(np.load(gf, allow_pickle=True)["aff_center_3d"]).ravel()

    z_table = estimate_plane(pts, aff[:2])
    print("scene            : %s" % a.scene)
    print("affordance centre: %s" % np.round(aff, 3).tolist())
    print("support plane z  : %.3f" % z_table)

    obj, r = pa.adaptive_crop(pts, aff[:2], z_table=z_table,
                              start=0.06, step=0.02, max_radius=a.max_radius)
    if len(obj) < 100:
        sys.exit("only %d points above the plane -- object not captured" % len(obj))
    obj, iso = pa.isolate_object(obj, aff[:2])
    print("crop radius      : %.2f m -> %d object points" % (r, len(obj)))
    print("object isolation : %s" % iso)
    print("object extent    : %s mm"
          % [round((obj[:, i].max() - obj[:, i].min()) * 1e3) for i in range(3)])

    shape = pa.classify_shape(obj, z_table)
    print("shape class      : %s (linearity %.2f, max horizontal %.0f mm)"
          % (shape["shape_class"], shape["linearity"], shape["max_horizontal"] * 1e3))

    comp, info = pa.find_components(obj, z_table=z_table)
    desc = pa.describe_components(comp, info)
    if not desc:
        sys.exit("no components found")
    print("\ncomponents:")
    print("  %-24s %6s %-7s %6s %8s %10s %10s" %
          ("name", "pts", "where", "h_frac", "radial", "size mm", "close mm"))
    for n, d in sorted(desc.items(), key=lambda kv: -kv[1]["n"]):
        print("  %-24s %6d %-7s %6.2f %6dmm %10s %7dmm  %s"
              % (n, d["n"], d["where"], d["height_fraction"], d["radial_offset_mm"],
                 "x".join(str(s) for s in d["size_mm"]), d["closing_width_mm"],
                 "graspable" if d["graspable"] else "TOO WIDE"))

    print("\npart binding:")
    for p in [s.strip() for s in a.parts.split(",") if s.strip()]:
        nm, pp, sc, note = pa.bind_part(p, comp, desc, keep_clear=[],
                                        linearity=shape["linearity"])
        flag = "" if sc >= 3.0 else "   <-- WEAK binding, would not execute"
        print("  %-16s -> %s%s" % ("'" + p + "'", note[:96], flag))


if __name__ == "__main__":
    main()
