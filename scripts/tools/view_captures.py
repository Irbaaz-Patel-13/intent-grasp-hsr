#!/usr/bin/env python
r"""view_captures.py -- dump the RGB (and optionally depth) from capture npz
files as PNGs, plus a single contact sheet for quick review.

    .\.venv\Scripts\python.exe view_captures.py                     # all cap_*.npz in captures_0723\
    .\.venv\Scripts\python.exe view_captures.py --dir . --glob "head_capture*.npz"
    .\.venv\Scripts\python.exe view_captures.py --depth             # also write depth previews

Writes into <dir>\previews\ and a contact sheet <dir>\previews\_contact_sheet.png
"""
import argparse, glob, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_rgb_depth(z):
    rgb = depth = None
    for k in z.files:
        a = np.asarray(z[k])
        if rgb is None and a.ndim == 3 and a.shape[2] == 3 and a.shape[0] > 50:
            rgb = a
        if depth is None and a.ndim == 2 and a.shape[0] > 50 and a.shape[1] > 50 \
           and a.dtype.kind in "fiu":
            depth = a
    return rgb, depth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="captures_0723")
    ap.add_argument("--glob", default="cap_*.npz")
    ap.add_argument("--depth", action="store_true")
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.dir, a.glob)))
    if not files:
        sys.exit("no files matching %s in %s" % (a.glob, a.dir))
    out = os.path.join(a.dir, "previews")
    os.makedirs(out, exist_ok=True)

    panels = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        z = np.load(f, allow_pickle=True)
        rgb, depth = find_rgb_depth(z)
        if rgb is None:
            print("  %-38s no RGB found (keys: %s)" % (name, list(z.files))); continue
        img = rgb.astype(np.uint8) if rgb.dtype != np.uint8 else rgb
        plt.imsave(os.path.join(out, name + ".png"), img)
        d_med = float(np.median(depth[depth > 0])) if depth is not None and (depth > 0).any() else float("nan")
        if d_med > 100: d_med /= 1000.0           # mm -> m
        print("  %-38s rgb%s  depth median %.3f m" % (name, (img.shape,), d_med))
        panels.append((name.replace("cap_", ""), img))
        if a.depth and depth is not None:
            dd = depth.astype(float)
            dd[dd == 0] = np.nan
            plt.imsave(os.path.join(out, name + "_depth.png"), dd, cmap="viridis")

    if panels:
        cols = min(a.cols, len(panels))
        rows = int(np.ceil(len(panels) / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(4.0*cols, 3.2*rows), dpi=140)
        axes = np.atleast_1d(axes).ravel()
        for ax in axes: ax.axis("off")
        for ax, (name, img) in zip(axes, panels):
            ax.imshow(img); ax.set_title(name, fontsize=9); ax.axis("off")
        fig.suptitle("Head-camera captures", fontsize=13)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        sheet = os.path.join(out, "_contact_sheet.png")
        fig.savefig(sheet, facecolor="white")
        print("\ncontact sheet -> %s" % sheet)
    print("individual PNGs -> %s" % out)


if __name__ == "__main__":
    main()
