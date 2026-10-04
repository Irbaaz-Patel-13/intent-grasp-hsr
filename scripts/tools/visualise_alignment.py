#!/usr/bin/env python
r"""visualise_alignment.py -- report-quality 3D figure of wrist-roll alignment.

Renders the part's point cloud, its PCA principal axis, and the gripper fingers
BEFORE and AFTER the roll correction, so the geometric argument is visible
rather than asserted. Intended as a dissertation figure, not a diagnostic chart.

    .\.venv\Scripts\python.exe visualise_alignment.py --demo
    .\.venv\Scripts\python.exe visualise_alignment.py --npz experiments\part_grasp\part_grasp_handle.npz
    .\.venv\Scripts\python.exe visualise_alignment.py --demo --angle 25 --out fig_align.png

--npz auto-detects the part-point array and (optionally) a 4x4 grasp pose; if no
pose is stored it assumes a top-down grasp with the closing axis along +x, which
is the CGN convention this pipeline receives.
"""
import argparse, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from intent_grasp.grasp_align import align_wrist_roll, _unit

INK = "#1f2933"; MUTED = "#7b8794"; ACC = "#b45309"; GOOD = "#047857"; BAD = "#b91c1c"


def rot_about(axis, ang):
    a = _unit(np.asarray(axis, float)); x, y, z = a
    c, s, C = np.cos(ang), np.sin(ang), 1 - np.cos(ang)
    return np.array([[c+x*x*C, x*y*C-z*s, x*z*C+y*s],
                     [y*x*C+z*s, c+y*y*C, y*z*C-x*s],
                     [z*x*C-y*s, z*y*C+x*s, c+z*z*C]])


def finger_box(centre, closing, approach, gap, side, w=0.012, h=0.055, d=0.022):
    """One finger as a box: offset +-gap/2 along `closing`, extruded along
    `approach` (downward) with thickness w across and depth d."""
    c = _unit(closing); a = _unit(approach); b = _unit(np.cross(a, c))
    o = np.asarray(centre, float) + side * (gap / 2.0) * c - a * (h / 2.0)
    verts = []
    for sc in (-w/2, w/2):
        for sb in (-d/2, d/2):
            for sa in (0.0, h):
                verts.append(o + sc*c + sb*b + sa*a)
    v = np.array(verts)
    idx = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
    return [[v[i] for i in f] for f in idx]


def draw_panel(ax, P, res, closing, title, ok):
    ax.scatter(P[:,0], P[:,1], P[:,2], s=1.4, c=MUTED, alpha=.45,
               depthshade=False, linewidths=0)
    pca = res["pca"]; ctr = pca["centroid"]
    L = pca["extent"][0] * 0.62
    u = pca["long_axis"]
    ax.plot(*np.array([ctr-L*u, ctr+L*u]).T, color=ACC, lw=2.6, zorder=6)
    ax.text(*(ctr+L*u*1.12), "part long axis", color=ACC, fontsize=8, zorder=7)

    gap = max(pca["minor_width"] + 0.022, 0.03)
    col = GOOD if ok else BAD
    for side in (-1, +1):
        ax.add_collection3d(Poly3DCollection(
            finger_box(ctr, closing, res["approach"], gap, side),
            facecolor=col, edgecolor=INK, linewidths=.4, alpha=.85))
    c = _unit(closing) * gap * 0.72
    ax.plot(*np.array([ctr-c, ctr+c]).T, color=col, lw=1.4, ls=(0,(4,3)), zorder=6)
    ax.text(*(ctr+c*1.25), "closing axis", color=col, fontsize=8, zorder=7)

    R = max(pca["extent"][0], 0.10) * 0.75
    ax.set_xlim(ctr[0]-R, ctr[0]+R); ax.set_ylim(ctr[1]-R, ctr[1]+R)
    ax.set_zlim(ctr[2]-R*.7, ctr[2]+R*.7)
    ax.set_box_aspect((1,1,.75)); ax.view_init(elev=26, azim=-58)
    ax.set_xlabel("x (m)", fontsize=8); ax.set_ylabel("y (m)", fontsize=8)
    ax.set_zlabel("z (m)", fontsize=8)
    ax.tick_params(labelsize=7, colors=MUTED)
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.set_facecolor("white"); pane.pane.set_edgecolor("#e4e7eb")
    ax.set_title(title, fontsize=10.5, color=INK, pad=8)


PART_HINTS = ("part_points", "part_pts", "part", "region", "selected")


def load_npz(path, key=None, list_only=False):
    """Load part points. An npz here typically holds BOTH the whole-object cloud
    and the selected part; auto-detection must not silently take the larger one
    (the mug body is 3871 pts, its handle ~139). Prefers a key whose NAME says
    'part', else the SMALLEST plausible (N,3) array, and always reports what it
    chose plus the alternatives."""
    z = np.load(path, allow_pickle=True)
    cands = []
    T = None
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 2 and a.shape[1] == 3 and a.shape[0] > 20:
            cands.append((k, a.astype(float)))
        if a.ndim == 2 and a.shape == (4, 4) and T is None:
            T = a.astype(float)
        if a.ndim == 3 and a.shape[1:] == (4, 4) and T is None:
            T = a[0].astype(float)

    print("point arrays in %s:" % path)
    for k, a in cands:
        print("   %-24s %6d pts   extent %.3f x %.3f x %.3f m"
              % (k, len(a), *(a.max(0) - a.min(0))))
    if list_only:
        sys.exit(0)
    if not cands:
        sys.exit("no (N,3) arrays found; keys=%s" % (list(z.files),))

    if key:
        sel = [c for c in cands if c[0] == key]
        if not sel:
            sys.exit("key '%s' not among the point arrays above" % key)
        k, P = sel[0]
    else:
        named = [c for c in cands
                 if any(h in c[0].lower() for h in PART_HINTS)]
        pool = named or cands
        k, P = min(pool, key=lambda c: len(c[1]))     # part < whole object
        print("   -> auto-selected '%s' (%s). Override with --key" %
              (k, "name suggests a part" if named else "smallest array"))
    print("using '%s': %d points" % (k, len(P)))
    return P, T


def demo_part(angle_deg):
    rng = np.random.default_rng(4)
    t = np.radians(angle_deg)
    u = np.array([np.cos(t), np.sin(t), 0.0])
    v = np.array([-np.sin(t), np.cos(t), 0.0]); w = np.array([0, 0, 1.0])
    n, L, r = 1800, 0.16, 0.014
    s = rng.uniform(-L/2, L/2, n); a = rng.uniform(0, 2*np.pi, n)
    return (np.array([0.75, 0.05, 0.48]) + s[:, None]*u
            + r*np.cos(a)[:, None]*v + r*np.sin(a)[:, None]*w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz"); ap.add_argument("--demo", action="store_true")
    ap.add_argument("--key", help="which array in the npz holds the PART points")
    ap.add_argument("--list", action="store_true", help="list point arrays and exit")
    ap.add_argument("--angle", type=float, default=35.0,
                    help="demo: part long-axis orientation in the xy-plane (deg)")
    ap.add_argument("--out", default="fig_wrist_roll_alignment.png")
    ap.add_argument("--sign", type=float, default=1.0)
    a = ap.parse_args()

    if a.npz:
        P, T = load_npz(a.npz, key=a.key, list_only=a.list)
    elif a.demo:
        P, T = demo_part(a.angle), None
    else:
        sys.exit("pass --demo or --npz <file>")

    if T is None:                      # CGN convention: top-down, closing along +x
        T = np.eye(4); T[:3, 0] = [1, 0, 0]; T[:3, 1] = [0, -1, 0]; T[:3, 2] = [0, 0, -1]
        T[:3, 3] = P.mean(0)

    res = align_wrist_roll(T, P, wrist_roll_now=0.0, sign=a.sign, force_align=True)
    if res.get("pca") is None:
        sys.exit(res["reason"])

    closing_before = res["closing_now"]
    closing_after = rot_about(res["approach"], res["delta_rad"]) @ closing_before

    fig = plt.figure(figsize=(11.2, 5.4), dpi=200)
    fig.patch.set_facecolor("white")
    ax1 = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122, projection="3d")
    draw_panel(ax1, P, res, closing_before,
               "(a) CGN closing axis, uncorrected\nmisalignment %.0f°"
               % res["misalign_deg"], ok=False)
    draw_panel(ax2, P, res, closing_after,
               "(b) after wrist-roll correction (%+.0f°)\nfingers close across the %.0f mm minor width"
               % (np.degrees(res["delta_rad"]), res["minor_width"]*1000), ok=True)

    sub = ("shape class '%s' (linearity %.2f, long extent %.0f mm, minor width %.0f mm) "
           "→ closing axis constrained; wrist_roll %+.3f rad"
           % (res["shape_class"], res["linearity"], res["long_extent"]*1000,
              res["minor_width"]*1000, res["delta_rad"]*a.sign))
    fig.suptitle("Wrist-roll alignment of the gripper closing axis to part geometry",
                 fontsize=12.5, color=INK, y=.985)
    fig.text(.5, .045, sub, ha="center", fontsize=9, color=MUTED)
    fig.tight_layout(rect=[0, .07, 1, .94])
    fig.savefig(a.out, facecolor="white")
    print("wrote %s" % a.out)
    print("  class=%s  misalign=%.1f deg  delta=%+.3f rad  apply=%s"
          % (res["shape_class"], res["misalign_deg"], res["delta_rad"], res["apply"]))


if __name__ == "__main__":
    main()