"""README figures that show what the depth camera actually measured.

    handle_gate.png   the mug: photo, the raw depth readings, and the parts the
                      decomposition found in them, against the evidence gate
    viewpoint.png     the part decomposition re-run on far and near captures of
                      four objects: getting closer turns a guess into evidence,
                      except for the mug handle

Run from the repository root:

    python figures/readme/make_cloud_figures.py
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from intent_grasp import som_part_selection as sps
from intent_grasp.paths import REPO_ROOT, WORKSPACE

sys.path.insert(0, str(REPO_ROOT / "figures" / "readme"))
import rgbd  # noqa: E402
from make_readme_figures import BLUE, INK, INK_2, INK_3, ORANGE, PANEL, save, title  # noqa: E402

AQUA = "#1baf7a"            # reference palette slot 3; slots 1-3 validate all-pairs
EVIDENCE = {"ok": ("trusted", BLUE), "LOW": ("weak", AQUA), "NOISE": ("refused", ORANGE)}
GATE_N, GATE_MM = 60, 6
CAPS = WORKSPACE / "captures_pairs_2"


def isolate(name):
    path = CAPS / f"cap_{name}.npz"
    _, comp, desc, _, _ = sps._load_and_isolate(str(path))
    return rgbd.load(path), comp, desc


def fine_parts(desc):
    """The handle-like parts: lateral protrusions, as part_adaptive names them."""
    return [k for k in desc if k.startswith("lateral_protrusion")]


# --------------------------------------------------------------------------
# handle_gate.png
# --------------------------------------------------------------------------
def fig_handle_gate():
    cap, comp, desc = isolate("mug_head_near")
    obj = np.vstack(list(comp.values()))
    x0, y0, x1, y1 = rgbd.crop_box(rgbd.to_pixels(cap, obj), 30, cap["rgb"].shape)
    x1, y1 = min(x1 + 40, 640), min(y1 + 45, 480)          # take in the handle and the lower body
    rgb = cap["rgb"][y0:y1, x0:x1]
    depth = cap["depth"][y0:y1, x0:x1]
    no_depth = ~((depth > 0.05) & (depth < 4.0))
    sides = fine_parts(desc)
    style = {"main_body": ("main body", BLUE), "top_protrusion": ("rim", AQUA)}
    for i, k in enumerate(sides):
        style[k] = (f"side piece {i + 1}", ORANGE)

    fig = plt.figure(figsize=(16, 6.8))
    title(fig, "Why the robot can't use this mug's handle",
          "Real HSR head-camera capture. Much of the handle returned no depth, and what the part finder "
          "did pick up near it is too small to trust, so the evidence gate refuses it.")

    def frame(ax):
        ax.set_xlim(0, x1 - x0)
        ax.set_ylim(y1 - y0, 0)
        ax.axis("off")

    ax = fig.add_axes([0.01, 0.12, 0.30, 0.62])
    ax.imshow(rgb)
    frame(ax)
    fig.text(0.01, 0.78, "(a) what the camera sees", fontsize=11.5)

    ax = fig.add_axes([0.34, 0.12, 0.30, 0.62])
    ax.imshow((rgb * 0.55 + 255 * 0.45).astype(np.uint8))
    shade = np.zeros(no_depth.shape + (4,))
    shade[no_depth] = (0.05, 0.05, 0.05, 0.72)
    ax.imshow(shade)
    frame(ax)
    fig.text(0.34, 0.78, "(b) where depth came back empty", fontsize=11.5)
    fig.text(0.34, 0.10, "Dark: pixels with no depth reading. The shiny rim and the\n"
             "top of the handle came back empty.", fontsize=9.5, color=INK_2, va="top")

    ax = fig.add_axes([0.67, 0.12, 0.30, 0.62])
    ax.imshow((rgb * 0.55 + 255 * 0.45).astype(np.uint8))
    for k in ["main_body", "top_protrusion"] + sides:
        if k not in comp:
            continue
        lab, col = style[k]
        q = rgbd.to_pixels(cap, comp[k])
        ax.scatter(q[:, 0] - x0, q[:, 1] - y0, s=7 if k == "main_body" else 14, color=col,
                   linewidths=0, zorder=3)
        if k in sides:
            mx, my = np.nanmedian(q[:, 0]) - x0, np.nanmedian(q[:, 1]) - y0
            right = mx > (x1 - x0) / 2
            where = "where the handle\nmeets the rim" if right else "opposite\nrim edge"
            ax.annotate(f"{lab}\n{where}", xy=(mx, my), xytext=(mx + (28 if right else -24), my - 32),
                        ha="left" if right else "right", fontsize=8.5, color=INK,
                        arrowprops=dict(arrowstyle="-", color=INK_3, lw=0.8))
    frame(ax)
    fig.text(0.67, 0.78, "(c) the parts found in the readings it did get", fontsize=11.5)
    lines = []
    for k in ["main_body", "top_protrusion"] + sides:
        d = desc[k]
        lab, col = style[k]
        word = EVIDENCE[d["evidence"]][0]
        lines.append((f"{lab}: {d['n']} points, {d['closing_width_mm']} mm → {word}", col))
    for i, (txt, col) in enumerate(lines):
        fig.text(0.67, 0.10 - i * 0.033, "●", color=col, fontsize=10, va="top")
        fig.text(0.682, 0.10 - i * 0.033, txt, fontsize=9.5, color=INK_2, va="top")
    save(fig, "handle_gate")


# --------------------------------------------------------------------------
# viewpoint.png
# --------------------------------------------------------------------------
OBJECTS = [("knife", "knife"), ("remote", "remote"), ("pot", "pot"), ("mug", "mug")]


def distance(cap, comp):
    obj = np.vstack(list(comp.values()))
    return float(np.median(np.linalg.norm(obj - cap["t"], axis=1)))


def tile(ax, cap, comp, desc):
    obj = np.vstack(list(comp.values()))
    if len(obj) < 100:   # isolation failed: show the whole frame rather than a crop of stray points
        x0, y0, x1, y1 = 0, 0, cap["rgb"].shape[1], cap["rgb"].shape[0]
    else:
        x0, y0, x1, y1 = rgbd.crop_box(rgbd.to_pixels(cap, obj), 22, cap["rgb"].shape, aspect=1.3)
    ax.imshow(cap["rgb"][y0:y1, x0:x1])
    body = rgbd.to_pixels(cap, obj)
    ax.scatter(body[:, 0] - x0, body[:, 1] - y0, s=2, color="white", alpha=0.35, linewidths=0)
    for k in fine_parts(desc):
        p = rgbd.to_pixels(cap, comp[k])
        col = EVIDENCE[desc[k]["evidence"]][1]
        ax.scatter(p[:, 0] - x0, p[:, 1] - y0, s=9, color=col, alpha=0.9, linewidths=0)
    ax.set_xlim(0, x1 - x0)
    ax.set_ylim(y1 - y0, 0)
    ax.axis("off")


def fig_viewpoint():
    fig = plt.figure(figsize=(16, 9.0))
    title(fig, "Moving the camera closer turns weak parts into trusted ones, but not on the mug",
          "The part decomposition re-run on a far and a near real capture of each object. "
          "White: the object's depth readings. Coloured: the smallest part the decomposition found.")
    for c, (name, label) in enumerate(OBJECTS):
        fig.text(0.075 + c * 0.235 + 0.10, 0.83, label, fontsize=13, fontweight="bold", ha="center")
        for r, view in enumerate(["far", "near"]):
            ax = fig.add_axes([0.075 + c * 0.235, 0.47 - r * 0.40, 0.21, 0.31])
            try:
                cap, comp, desc = isolate(f"{name}_head_{view}")
            except SystemExit:
                ax.axis("off")
                ax.text(0.5, 0.5, "object not found", ha="center", va="center", color=INK_3)
                continue
            tile(ax, cap, comp, desc)
            parts = fine_parts(desc)
            if parts:
                bits = []
                for k in parts:
                    d = desc[k]
                    bits.append(f"{d['n']} pts, {d['closing_width_mm']} mm")
                ev = [desc[k]["evidence"] for k in parts]
                word, col = EVIDENCE[min(ev, key=["ok", "LOW", "NOISE"].index)] if "ok" in ev else \
                    EVIDENCE["LOW"] if "LOW" in ev else EVIDENCE["NOISE"]
                head = f"{distance(cap, comp):.2f} m away: {word}"
                body = "smallest part: " + " + ".join(bits)
            else:
                d = max(desc.values(), key=lambda d: d["n"])
                word, col = EVIDENCE[d["evidence"]]
                head = "far view: pot not found"
                body = f"isolation kept only {d['n']} stray points, so there are no parts"
            ax.text(0.0, -0.04, head, transform=ax.transAxes, fontsize=10.5, color=col,
                    fontweight="bold", va="top")
            ax.text(0.0, -0.13, body, transform=ax.transAxes, fontsize=9, color=INK_2, va="top")
    for r, lab in enumerate(["far", "near"]):
        fig.text(0.045, 0.625 - r * 0.40, lab, fontsize=12, fontweight="bold", rotation=90,
                 ha="center", va="center", color=INK_2)
    for (k, (word, col)), lx in zip(EVIDENCE.items(), [0.52, 0.68, 0.79]):
        fig.text(lx, 0.88, "●", color=col, fontsize=13, va="center")
        rule = {"ok": "≥120 pts and ≥10 mm", "LOW": "in between",
                "NOISE": f"<{GATE_N} pts or <{GATE_MM} mm"}[k]
        fig.text(lx + 0.014, 0.88, f"{word}: {rule}", fontsize=9, color=INK_2, va="center")
    save(fig, "viewpoint")


if __name__ == "__main__":
    fig_handle_gate()
    fig_viewpoint()
