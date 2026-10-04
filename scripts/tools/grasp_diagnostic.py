r"""
grasp_diagnostic.py -- WINDOWS side. Analyse WHY the grasp landed on the rim,
not the handle. Visualises the fused mug, the affordance (handle) region, and
every CGN grasp candidate relative to it. Pure file analysis -- no live sim.

Reads:  workspace/fused_cloud.npz   (scene points+colors)
        workspace/grasps_out.npz    (affordance_points, aff_center, labels)
        workspace/grasps_plain.npz  (poses Nx4x4, scores, dist_to_aff)
Saves:  workspace/grasp_diagnostic.png
"""
import numpy as np
import matplotlib
from intent_grasp.paths import WORKSPACE
matplotlib.use("Agg"); import matplotlib.pyplot as plt

FUSED = f"{WORKSPACE}/fused_cloud.npz"
GOUT  = f"{WORKSPACE}/grasps_out.npz"
GPLN  = f"{WORKSPACE}/grasps_plain.npz"
OUT   = f"{WORKSPACE}/grasp_diagnostic.png"
AFF_RADIUS = 0.06     # the executor's selection radius

SCENE = "#B8B8B8"; AFFCOL = "#C0653A"; GRASP = "#4C6E8A"; CHOSEN = "#3A7D44"


def main():
    fused = np.load(FUSED)
    pts, cols = fused["points"], fused["colors"]
    g = np.load(GOUT, allow_pickle=True)
    aff_pts = np.asarray(g["affordance_points"], float)
    aff_c   = np.asarray(g["aff_center_3d"], float)
    obj = str(g["target_object"]); part = str(g["target_part"])
    p = np.load(GPLN)
    poses, scores, dist = p["poses"], p["scores"], p["dist_to_aff"]
    gpos = poses[:, :3, 3]

    # min distance from each grasp to the affordance POINT CLOUD (handle), not just centre
    def min_to_aff(pt):
        return float(np.min(np.linalg.norm(aff_pts - pt[None, :], axis=1))) if len(aff_pts) else np.nan
    d_center = np.linalg.norm(gpos - aff_c[None, :], axis=1)
    d_handle = np.array([min_to_aff(pt) for pt in gpos])

    # replicate executor selection
    near = d_center < AFF_RADIUS
    chosen = int(np.argmax(scores * near)) if near.any() else int(np.argmin(d_center))

    # ---- printed quantitative report ----
    print("="*64)
    print(f" instruction target: object='{obj}' part='{part}'")
    print(f" affordance centre : {np.round(aff_c,3)}")
    print(f" affordance points : {len(aff_pts)}  extent "
          f"x[{aff_pts[:,0].min():.2f},{aff_pts[:,0].max():.2f}] "
          f"y[{aff_pts[:,1].min():.2f},{aff_pts[:,1].max():.2f}] "
          f"z[{aff_pts[:,2].min():.2f},{aff_pts[:,2].max():.2f}]")
    print("-"*64)
    print(f" {'grasp':>5} {'score':>6} {'d_center':>9} {'d_handle':>9}  {'on handle?':>10}")
    for i in range(len(poses)):
        onh = "YES" if d_handle[i] < 0.03 else "near" if d_handle[i] < 0.06 else "no"
        mark = " <- CHOSEN" if i == chosen else ""
        print(f" {i:>5} {scores[i]:>6.3f} {d_center[i]:>9.3f} {d_handle[i]:>9.3f}  {onh:>10}{mark}")
    print("-"*64)
    print(f" grasps with d_handle<0.03 (truly on handle): {(d_handle<0.03).sum()}")
    print(f" grasps with d_center <{AFF_RADIUS} (selectable): {near.sum()}")
    if (d_handle < 0.03).sum() == 0:
        print(" >>> DIAGNOSIS: CGN proposed NO grasp on the handle. The fix is")
        print("     upstream (mask coverage / handle visibility / cloud density),")
        print("     not selection tightening.")
    elif not near.any():
        print(" >>> DIAGNOSIS: handle grasps exist but fell outside selection radius.")
        print("     Tighten max_distance_from_affordance_center / AFF_RADIUS.")
    print("="*64)

    # ---- visual: crop scene around the mug ----
    lo = aff_c - 0.25; hi = aff_c + 0.25
    m = np.all((pts >= lo) & (pts <= hi), axis=1)
    sp, sc = pts[m], cols[m]

    fig, ax = plt.subplots(1, 2, figsize=(16, 7))
    for a, (i0, i1, lab) in zip(ax, [(0, 1, "TOP-DOWN (x-y)"), (0, 2, "SIDE (x-z)")]):
        a.scatter(sp[:, i0], sp[:, i1], s=2, c=SCENE, alpha=0.25, label="scene")
        a.scatter(aff_pts[:, i0], aff_pts[:, i1], s=6, c=AFFCOL, label=f"affordance ({part})")
        a.scatter(aff_c[i0], aff_c[i1], marker="*", s=320, c="k", zorder=5, label="aff centre")
        for j in range(len(gpos)):
            col = CHOSEN if j == chosen else GRASP
            a.scatter(gpos[j, i0], gpos[j, i1], s=90, c=col, edgecolors="k",
                      zorder=4, label=("chosen grasp" if j == chosen else ("grasp" if j == 0 else None)))
            a.annotate(f"{j}", (gpos[j, i0], gpos[j, i1]), fontsize=9, zorder=6)
            # approach direction (3rd column of rotation), short segment
            ap = poses[j, :3, 2] * 0.05
            a.plot([gpos[j, i0], gpos[j, i0] + ap[i0]],
                   [gpos[j, i1], gpos[j, i1] + ap[i1]], c=col, lw=1.2)
        a.set_title(lab); a.set_aspect("equal"); a.grid(alpha=0.3)
        a.set_xlabel("xyz"[i0]); a.set_ylabel("xyz"[i1])
    handles, labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels, loc="best", fontsize=8)
    plt.suptitle(f"Grasp selection vs affordance — '{part}' of {obj}", fontsize=13)
    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight")
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
