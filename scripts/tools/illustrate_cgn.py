r"""
illustrate_cgn.py -- WINDOWS. Clean 3D illustration of CGN grasps on the object.
Reads grasps_plain.npz + grasps_out.npz (affordance points) + fused_cloud.npz.
Tight crop to the object, sensibly-scaled gripper glyphs, chosen grasp in green
with its approach arrow. Read-only on all inputs. Saves cgn_illustration.png.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from intent_grasp.paths import WORKSPACE

PLAIN = f"{WORKSPACE}/grasps_plain.npz"
OUTNPZ= f"{WORKSPACE}/grasps_out.npz"
FUSED = f"{WORKSPACE}/fused_cloud.npz"
OUT   = f"{WORKSPACE}/cgn_illustration.png"

AFF_RADIUS = 0.06          # matches execute_grasp_v2.py selection radius
N_SHOW     = 10            # how many candidate grippers to draw (top by score), declutters
HALF       = 0.12          # crop half-width around the object (m)
# gripper glyph drawing size (illustrative; real width not stored in npz)
G_W, G_FIN, G_BASE = 0.05, 0.028, 0.018


def gripper_segments(pose, w=G_W, fin=G_FIN, base=G_BASE):
    hw = w / 2.0
    local = np.array([
        [ hw, 0, fin], [ hw, 0, 0],
        [-hw, 0, 0],   [-hw, 0, fin],
        [ 0,  0, 0],   [ 0,  0, -base],
    ])
    R, t = pose[:3, :3], pose[:3, 3]
    p = (R @ local.T).T + t
    return [(p[0], p[1]), (p[1], p[2]), (p[2], p[3]), (p[4], p[5])]


def choose_idx(dist, score):
    near = dist < AFF_RADIUS
    if near.sum() == 0:
        return int(np.argmin(dist))
    cand = np.where(near)[0]
    return int(cand[np.argmax(score[cand])])


def crop(pts, aff, half, zlo, zhi):
    if pts is None or len(pts) == 0:
        return None
    m = ((np.abs(pts[:, 0] - aff[0]) < half) &
         (np.abs(pts[:, 1] - aff[1]) < half) &
         (pts[:, 2] > zlo) & (pts[:, 2] < zhi))
    return pts[m]


def draw(ax, poses, score, aff, obj_pts, ctx_pts, idx, show_idx):
    if ctx_pts is not None and len(ctx_pts):
        ax.scatter(ctx_pts[:,0], ctx_pts[:,1], ctx_pts[:,2], s=2, c="#E2E5EA", alpha=0.5)
    if obj_pts is not None and len(obj_pts):
        ax.scatter(obj_pts[:,0], obj_pts[:,1], obj_pts[:,2], s=8, c="#2563EB", alpha=0.85)
    # candidate grippers — muted, thin
    for i in show_idx:
        if i == idx:
            continue
        ax.add_collection3d(Line3DCollection(
            gripper_segments(poses[i]), colors=["#9AA8C2"], linewidths=1.2, alpha=0.55))
    # affordance centre
    ax.scatter([aff[0]], [aff[1]], [aff[2]], marker="*", s=240, c="#E11D48",
               edgecolors="white", linewidths=1, depthshade=False, zorder=5)
    # chosen grasp — green + approach arrow
    ax.add_collection3d(Line3DCollection(
        gripper_segments(poses[idx]), colors=["#16A34A"], linewidths=3.2))
    g = poses[idx][:3, 3]; ap = poses[idx][:3, 2]
    ax.quiver(g[0], g[1], g[2], ap[0]*0.05, ap[1]*0.05, ap[2]*0.05,
              color="#16A34A", linewidth=2)


def main():
    d = np.load(PLAIN)
    poses, score, dist, aff = d["poses"], d["scores"], d["dist_to_aff"], d["aff_center_3d"]
    idx = choose_idx(dist, score)
    show_idx = list(np.argsort(score)[::-1][:N_SHOW])
    if idx not in show_idx:
        show_idx.append(idx)
    print(f"{len(poses)} CGN grasps; chosen #{idx} score={score[idx]:.3f} dist={dist[idx]:.3f}")

    zlo, zhi = aff[2] - HALF, aff[2] + HALF + 0.03

    obj_pts = None
    try:
        o = np.load(OUTNPZ, allow_pickle=True)
        obj_pts = crop(np.asarray(o["affordance_points"], float), aff, HALF, zlo, zhi)
    except Exception as e:
        print(f"  (affordance points skipped: {e})")

    ctx_pts = None
    try:
        f = np.load(FUSED)["points"].astype(float)
        ctx_pts = crop(f, aff, HALF + 0.04, zlo - 0.02, zhi + 0.02)
        if ctx_pts is not None and len(ctx_pts) > 1200:
            ctx_pts = ctx_pts[::len(ctx_pts)//1200]
    except Exception as e:
        print(f"  (context cloud skipped: {e})")

    def setlims(ax):
        ax.set_xlim(aff[0]-HALF, aff[0]+HALF)
        ax.set_ylim(aff[1]-HALF, aff[1]+HALF)
        ax.set_zlim(zlo, zhi)
        ax.set_box_aspect((1, 1, 1))

    fig = plt.figure(figsize=(14, 6.5))
    ax1 = fig.add_subplot(121, projection="3d")
    draw(ax1, poses, score, aff, obj_pts, ctx_pts, idx, show_idx)
    setlims(ax1); ax1.view_init(elev=20, azim=-60)
    ax1.set_title("CGN grasps on the real mug (3D)")
    ax1.set_xlabel("x (m)"); ax1.set_ylabel("y (m)"); ax1.set_zlabel("z (m)")

    ax2 = fig.add_subplot(122, projection="3d")
    draw(ax2, poses, score, aff, obj_pts, ctx_pts, idx, show_idx)
    setlims(ax2); ax2.view_init(elev=89, azim=-90)
    ax2.set_title("Top-down — green = grasp that would execute")
    ax2.set_xlabel("x (m)"); ax2.set_ylabel("y (m)"); ax2.set_zlabel("")

    fig.suptitle("Contact-GraspNet on real HSR data: affordance-ranked 6-DoF grasps "
                 f"(showing top {N_SHOW} of {len(poses)})", fontsize=12, y=0.98)
    fig.tight_layout()
    fig.savefig(OUT, dpi=130, bbox_inches="tight"); plt.close(fig)
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()