#!/usr/bin/env python
r"""fig_intent_dissection.py -- the headline figure: one object, several intents,
different structural parts selected, and (optionally) the grasps generated on the
part that was chosen.

    python fig_intent_dissection.py --cap captures_pairs_2\cap_pot_head_near.npz ^
        --intents "pick up the pot=handle" "take the lid off=lid knob" "pour from it=rim"

    python fig_intent_dissection.py --cap captures_pairs_2\cap_mug_head_near.npz ^
        --intents "I'd like a hot drink=handle" "pour it out=rim" "move it=body" ^
        --grasps grasps_out.npz

Panel 0 shows the full structural decomposition -- every component the geometry
finds, named by its relation to the object (lateral_protrusion, top_protrusion,
rim_ring, main_body, axis segments). Panels 1..N each show ONE intent, with the
component that the VLM's inferred part binds to highlighted and everything else
faded. With --grasps, the CGN grasp positions are projected on top, so the figure
shows intent -> part -> where the gripper would actually land.

Part names come from the VLM (constraints.json / vlm_identify.csv record them);
pass them as "intent=part". Binding to geometry is done by part_adaptive, not by
a lookup table.
"""
import argparse, os, sys
import numpy as np
try:
    from intent_grasp import part_adaptive as pa
except ImportError:
    sys.exit("part_adaptive.py must be alongside this script")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])
INK, MUTED, FADE = "#1f2933", "#7b8794", "#c9d1d9"
HL = ["#b45309", "#047857", "#1d4ed8", "#7c3aed", "#b91c1c", "#0891b2"]


def load(path):
    d = np.load(path, allow_pickle=True)
    k = {x.lower(): x for x in d.files}
    def g(*n):
        for i in n:
            if i in k: return np.asarray(d[k[i]])
    rgb, depth, K = g("rgb", "color"), g("depth"), g("k", "intrinsics")
    tr, qt = g("tf_trans", "trans"), g("tf_quat", "quat")
    if any(v is None for v in (rgb, depth, K, tr, qt)):
        sys.exit("capture missing rgb/depth/K/tf in %s (keys %s)" % (path, d.files))
    depth = depth.astype(float)
    if np.nanmax(depth) > 100: depth /= 1000.0
    T = np.eye(4); T[:3, :3] = Rotation.from_quat(np.asarray(qt).ravel()).as_matrix()
    T[:3, 3] = np.asarray(tr).ravel()
    return dict(rgb=rgb.astype(np.uint8), depth=depth, K=np.asarray(K, float),
                T=T, extr=FLIP @ np.linalg.inv(T))


def cloud(c):
    d, K, T = c["depth"], c["K"], c["T"]
    h, w = d.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    ok = (d > 0.05) & (d < 4.0); z = d[ok]
    x = (u[ok]-K[0,2])*z/K[0,0]; y = (v[ok]-K[1,2])*z/K[1,1]
    return (T[:3,:3] @ np.stack([x,y,z],-1).T).T + T[:3,3]


from intent_grasp import scene_objects as so
def isolate(pts, pick=0):
    """Objects ON the table, via the table's own footprint (scene_objects)."""
    table, objs = so.find_objects(pts)
    print(so.describe(table, objs))
    if table is None or not objs:
        sys.exit("no object found on the table surface")
    if pick >= len(objs):
        sys.exit("only %d object(s) found; --pick %d out of range" % (len(objs), pick))
    return table["plane_z"], objs[pick]["points"]


def px(c, p3, shape):
    u, v, z, ok = pa.project_points_to_pixels(p3, c["K"], c["extr"])
    H, W = shape
    keep = ok & (u>=0)&(u<W)&(v>=0)&(v<H)
    return u[keep], v[keep]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", required=True)
    ap.add_argument("--intents", nargs="+", required=True,
                    help='each as "intent text=vlm part name"')
    ap.add_argument("--grasps", help="grasps_out.npz / grasps_plain.npz to overlay")
    ap.add_argument("--out", default=None)
    ap.add_argument("--title", default=None)
    a = ap.parse_args()

    c = load(a.cap)
    H, W = c["rgb"].shape[:2]
    plane, obj = isolate(cloud(c))
    shape = pa.classify_shape(obj, plane)
    comp, info = pa.find_components(obj, z_table=plane)
    desc = pa.describe_components(comp, info)
    name = os.path.basename(a.cap).replace("cap_", "").replace(".npz", "")
    print("%s: plane %.3f, %d object pts, %s (lin %.2f), components: %s"
          % (name, plane, len(obj), shape["shape_class"], shape["linearity"],
             sorted(desc)))

    pairs = []
    for s in a.intents:
        if "=" not in s: sys.exit('intents must be "text=part": %r' % s)
        t, p = s.rsplit("=", 1); pairs.append((t.strip(), p.strip()))

    gr = None
    if a.grasps and os.path.exists(a.grasps):
        z = np.load(a.grasps, allow_pickle=True)
        for k in z.files:
            arr = np.asarray(z[k])
            if arr.ndim == 3 and arr.shape[1:] == (4, 4):
                gr = arr[:, :3, 3]; break
            if arr.dtype == object and arr.size and hasattr(arr.flat[0], "shape"):
                try:
                    gr = np.array([np.asarray(g)[:3, 3] for g in arr]); break
                except Exception: pass
        print("grasp overlay: %s poses" % (len(gr) if gr is not None else "none found"))

    n = len(pairs) + 1
    cols = min(n, 4); rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4.6*cols, 4.0*rows), dpi=170)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes: ax.axis("off")

    # panel 0 -- full structural decomposition
    ax = axes[0]; ax.imshow(c["rgb"])
    for i, (nm, p3) in enumerate(sorted(comp.items(), key=lambda kv: -len(kv[1]))):
        u, v = px(c, p3, (H, W))
        d = desc.get(nm, {})
        ax.scatter(u, v, s=1.5, alpha=.6, c=HL[i % len(HL)], linewidths=0,
                   label="%s (%d pts, %d mm)" % (nm, d.get("n",0),
                                                 d.get("closing_width_mm",0)))
    ax.legend(loc="lower center", fontsize=5.8, markerscale=5, framealpha=.85)
    ax.set_title("structural decomposition\n(geometry only — no object model)",
                 fontsize=9.5, color=INK)

    # panels 1..N -- one intent each
    for i, (intent, part) in enumerate(pairs, start=1):
        if i >= len(axes): break
        ax = axes[i]; ax.imshow(c["rgb"])
        nm, pp, sc, note = pa.bind_part(part, comp, desc, keep_clear=[],
                                        linearity=shape["linearity"])
        for onm, p3 in comp.items():
            if pp is not None and onm == nm: continue
            u, v = px(c, p3, (H, W))
            ax.scatter(u, v, s=1.0, alpha=.30, c=FADE, linewidths=0)
        if pp is not None:
            u, v = px(c, pp, (H, W))
            ax.scatter(u, v, s=3.0, alpha=.95, c=HL[(i-1) % len(HL)], linewidths=0)
            d = desc.get(nm, {})
            sub = "%s → %s\n%d pts, %d mm, %s" % (part, nm, d.get("n",0),
                                                 d.get("closing_width_mm",0),
                                                 d.get("evidence","?"))
            if gr is not None and len(pp):
                ctr = pp.mean(0)
                near = gr[np.linalg.norm(gr - ctr, axis=1) < 0.16]
                if len(near):
                    gu, gv = px(c, near, (H, W))
                    ax.scatter(gu, gv, s=42, marker="x", c="#111827",
                               linewidths=1.4, alpha=.9)
                    sub += "  ·  %d grasps on this part" % len(near)
        else:
            sub = "%s → REFUSED\n%s" % (part, note[:58])
        ax.set_title('"%s"' % intent, fontsize=9.5, color=INK)
        ax.text(0.5, -0.02, sub, transform=ax.transAxes, ha="center", va="top",
                fontsize=8, color=MUTED)
        print('  "%s" -> %s' % (intent, note[:88]))

    fig.suptitle(a.title or ("%s — the same object dissected differently by intent" % name),
                 fontsize=13, color=INK)
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    out = a.out or os.path.join("report_assets", "figures",
                                "fig_intent_%s.png" % name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor="white", bbox_inches="tight"); print("\nwrote %s" % out)


if __name__ == "__main__":
    main()
