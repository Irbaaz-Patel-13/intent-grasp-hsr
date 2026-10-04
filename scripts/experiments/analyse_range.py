#!/usr/bin/env python
r"""analyse_range.py -- does a closer viewpoint resolve object parts that the
standard head-camera distance cannot?

    python .\analyse_range.py --dir captures_pairs_2
    python .\analyse_range.py --dir captures_pairs_2 --only mug,pot,remote
    python .\analyse_range.py --dir captures_pairs_2 --no-figs      # table only

Background. From the standard capture pose (~1.0 m, head tilt -0.50) the part
required for a task was repeatedly measured below the depth sensor's usable
floor: the mug handle returned 48 points / 6 mm and the pot handle 75 points /
5 mm, so part-scoped grasp generation correctly refused to act on them. The open
question was whether that is a RANGE limit or a fundamental one. These paired
captures -- same object, same table, camera driven ~0.25 m closer -- answer it.

Geometry only: no GPU, no API. Each capture is back-projected into base_link
using its own stored K and TF, the support plane is found, the object is
isolated as a connected cluster, and part_adaptive's structural components are
measured. Outputs a per-object table and a far/near figure with the detected
components overlaid on the RGB.
"""
import argparse, csv, glob, json, os, sys
import numpy as np

try:
    from intent_grasp import part_adaptive as pa
except ImportError:
    sys.exit("part_adaptive.py must be in the same folder (run from workspace/)")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])
INK, MUTED = "#1f2933", "#7b8794"
PALETTE = ["#b45309", "#047857", "#1d4ed8", "#b91c1c", "#7c3aed", "#0891b2"]


def load_capture(path):
    d = np.load(path, allow_pickle=True)
    keys = {k.lower(): k for k in d.files}
    def get(*names):
        for n in names:
            if n in keys: return np.asarray(d[keys[n]])
        return None
    rgb = get("rgb", "color", "image")
    depth = get("depth", "depth_image")
    K = get("k", "intrinsics", "camera_matrix")
    trans = get("tf_trans", "trans", "translation")
    quat = get("tf_quat", "quat", "rotation")
    if any(x is None for x in (rgb, depth, K, trans, quat)):
        return None
    depth = depth.astype(float)
    if np.nanmax(depth) > 100: depth /= 1000.0
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat(np.asarray(quat).ravel()).as_matrix()
    T[:3, 3] = np.asarray(trans).ravel()
    return dict(rgb=rgb.astype(np.uint8), depth=depth, K=np.asarray(K, float),
                T_base_cam=T, extr=FLIP @ np.linalg.inv(T),
                depth_med=float(np.median(depth[depth > 0.05])))


def cloud_base(cap):
    d, K, T = cap["depth"], cap["K"], cap["T_base_cam"]
    h, w = d.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (d > 0.05) & (d < 4.0)
    z = d[ok]
    x = (u[ok] - K[0, 2]) * z / K[0, 0]
    y = (v[ok] - K[1, 2]) * z / K[1, 1]
    pc = np.stack([x, y, z], -1)
    return (T[:3, :3] @ pc.T).T + T[:3, 3]


from intent_grasp import scene_objects as so
def find_object(pts, **kw):
    """Objects ON the table, via the table's own footprint (scene_objects)."""
    table, objs = so.find_objects(pts)
    if table is None:
        return None, None, dict(note="no table surface")
    if not objs:
        return table["plane_z"], None, dict(note="no object on the table",
                                            table=table["x"] + table["y"])
    o = objs[0]
    return table["plane_z"], o["points"], dict(n_objects=len(objs), span=o["span"],
                                               height=o["height"],
                                               centroid=o["centroid"])


def analyse(cap, label):
    pts = cloud_base(cap)
    plane, obj, iso = find_object(pts)
    if obj is None:
        return dict(label=label, error="object not isolated", plane_z=plane, iso=iso)
    shape = pa.classify_shape(obj, plane)
    comp, info = pa.find_components(obj, z_table=plane)
    desc = pa.describe_components(comp, info)
    return dict(label=label, plane_z=round(plane, 3), n_obj=len(obj),
                shape=shape["shape_class"], linearity=round(shape["linearity"], 2),
                extent=[round(e * 1e3) for e in shape["extent"]],
                comp=comp, desc=desc, iso=iso, obj=obj,
                depth_med=round(cap["depth_med"], 3))


def overlay(ax, cap, res, title):
    ax.imshow(cap["rgb"]); ax.axis("off")
    ax.set_title(title, fontsize=10, color=INK)
    if res.get("error"):
        ax.text(0.5, 0.06, res["error"], transform=ax.transAxes, ha="center",
                fontsize=9, color="#b91c1c",
                bbox=dict(fc="white", ec="none", alpha=.85)); return
    H, W = cap["rgb"].shape[:2]
    for i, (name, pts3) in enumerate(sorted(res["comp"].items(),
                                            key=lambda kv: -len(kv[1]))):
        u, v, z, ok = pa.project_points_to_pixels(pts3, cap["K"], cap["extr"])
        uu, vv = u[ok], v[ok]
        keep = (uu >= 0) & (uu < W) & (vv >= 0) & (vv < H)
        d = res["desc"].get(name, {})
        lab = "%s  %d pts, %d mm, %s" % (name, d.get("n", 0),
                                         d.get("closing_width_mm", 0),
                                         d.get("evidence", "?"))
        ax.scatter(uu[keep], vv[keep], s=1.6, alpha=.55,
                   c=PALETTE[i % len(PALETTE)], label=lab, linewidths=0)
    ax.legend(loc="lower center", fontsize=6.2, markerscale=5, ncol=1,
              framealpha=.85, bbox_to_anchor=(0.5, -0.02))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="captures_pairs_2")
    ap.add_argument("--only", default="")
    ap.add_argument("--outdir", default="report_assets/figures")
    ap.add_argument("--no-figs", dest="figs", action="store_false")
    ap.set_defaults(figs=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    labels = sorted({os.path.basename(f)[4:-len("_head_far.npz")]
                     for f in glob.glob(os.path.join(a.dir, "cap_*_head_far.npz"))})
    if a.only:
        want = [s.strip().lower() for s in a.only.split(",")]
        labels = [l for l in labels if any(w in l.lower() for w in want)]
    if not labels:
        sys.exit("no cap_*_head_far.npz found in %s" % a.dir)
    print("objects with a far/near pair: %d\n" % len(labels))

    rows = []
    for lab in labels:
        f_far = os.path.join(a.dir, "cap_%s_head_far.npz" % lab)
        f_near = os.path.join(a.dir, "cap_%s_head_near.npz" % lab)
        if not os.path.exists(f_near):
            print("%-28s no near capture -- skipped" % lab); continue
        cf, cn = load_capture(f_far), load_capture(f_near)
        if cf is None or cn is None:
            print("%-28s unreadable npz -- skipped" % lab); continue
        rf, rn = analyse(cf, lab + " far"), analyse(cn, lab + " near")
        print("== %s ==" % lab)
        for tag, r, c in (("far", rf, cf), ("near", rn, cn)):
            if r.get("error"):
                print("   %-5s depth %.2f m  -- %s" % (tag, c["depth_med"], r["error"])); continue
            best = sorted(r["desc"].items(), key=lambda kv: -kv[1]["n"])
            print("   %-5s depth %.2f m  plane %.3f  obj %5d pts  %s lin=%.2f  %s mm"
                  % (tag, c["depth_med"], r["plane_z"], r["n_obj"], r["shape"],
                     r["linearity"], "x".join(str(e) for e in r["extent"])))
            for nm, d in best:
                print("        %-22s %5d pts  %3d mm  %-5s %s"
                      % (nm, d["n"], d["closing_width_mm"], d["evidence"],
                         "graspable" if d["graspable"] else "TOO WIDE"))
        # smallest graspable component = the fine part the range test is about
        def finest(r):
            if r.get("error"): return None
            cands = [(d["closing_width_mm"], n, d) for n, d in r["desc"].items()
                     if d["graspable"] and n != "main_body"]
            return min(cands)[2] if cands else None
        ff, fn = finest(rf), finest(rn)
        rows.append(dict(object=lab,
                         far_depth=cf["depth_med"], near_depth=cn["depth_med"],
                         far_obj_pts=rf.get("n_obj", 0), near_obj_pts=rn.get("n_obj", 0),
                         far_shape=rf.get("shape", "-"), near_shape=rn.get("shape", "-"),
                         far_fine_pts=ff["n"] if ff else 0,
                         near_fine_pts=fn["n"] if fn else 0,
                         far_fine_mm=ff["closing_width_mm"] if ff else 0,
                         near_fine_mm=fn["closing_width_mm"] if fn else 0,
                         far_evidence=ff["evidence"] if ff else "none",
                         near_evidence=fn["evidence"] if fn else "none"))
        if a.figs:
            fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6), dpi=160)
            fig.patch.set_facecolor("white")
            overlay(axes[0], cf, rf, "far  (median depth %.2f m)" % cf["depth_med"])
            overlay(axes[1], cn, rn, "near (median depth %.2f m)" % cn["depth_med"])
            fig.suptitle("%s — structural components at two viewing distances" % lab,
                         fontsize=12.5, color=INK)
            fig.tight_layout(rect=[0, 0, 1, 0.94])
            out = os.path.join(a.outdir, "fig_range_%s.png" % lab)
            fig.savefig(out, facecolor="white"); plt.close(fig)
            print("   -> %s" % out)
        print()

    if not rows: sys.exit("nothing analysed")
    with open("range_analysis.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    L = ["# Does a closer viewpoint resolve graspable parts?", "",
         "Same object, same table, camera driven ~0.25 m closer. 'Finest part' is the",
         "narrowest graspable structural component other than the main body -- i.e. the",
         "handle-like feature that part-scoped grasping needs and that was previously",
         "measured below the sensor's evidence floor (mug 48 pts / 6 mm, pot 75 / 5).", "",
         "| object | depth far → near | object pts far → near | finest part pts | finest part width | evidence far → near |",
         "|---|---|---|---|---|---|"]
    imp = 0
    for r in rows:
        better = r["near_fine_pts"] > r["far_fine_pts"] * 1.4 and r["near_fine_pts"] > 100
        imp += int(better)
        L.append("| %s | %.2f → %.2f m | %d → %d | %d → %d%s | %d → %d mm | %s → %s |"
                 % (r["object"], r["far_depth"], r["near_depth"],
                    r["far_obj_pts"], r["near_obj_pts"],
                    r["far_fine_pts"], r["near_fine_pts"], " **↑**" if better else "",
                    r["far_fine_mm"], r["near_fine_mm"],
                    r["far_evidence"], r["near_evidence"]))
    L += ["", "**%d of %d objects showed a materially better-resolved fine part at the "
          "closer viewpoint.**" % (imp, len(rows)), "",
          "Evidence classes: `ok` (>=120 pts and >=10 mm), `LOW`, `NOISE` (<60 pts or "
          "<6 mm -- rejected by the part binder).", "",
          "Figures: `%s/fig_range_<object>.png`" % a.outdir]
    open("range_analysis.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[-4:]))
    print("\nwrote range_analysis.md and range_analysis.csv")


if __name__ == "__main__":
    main()
