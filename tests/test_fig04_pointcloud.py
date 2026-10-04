"""
test_fig04_pointcloud.py -- smoke + reproducibility test for
fig04_pointcloud.py.

Reproducibility here is checked structurally (mean pixel difference under a
threshold), not by byte hash, because Open3D's offscreen rasterizer is not
guaranteed byte-stable across reruns/drivers even though point selection is
seeded (design spec Sec 13; see fig04_pointcloud.py's docstring).

Run: python -m pytest tests/test_fig04_pointcloud.py
"""
import os
import tempfile

import matplotlib.colors
import numpy as np
from PIL import Image

import figstyle as fs
import fig04_pointcloud as f4


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig04.png")
        path = f4.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_structurally_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f4.render(out_path=out1)
        f4.render(out_path=out2)
        img1 = np.asarray(Image.open(out1).convert("RGB"), dtype=np.float32)
        img2 = np.asarray(Image.open(out2).convert("RGB"), dtype=np.float32)
        assert img1.shape == img2.shape
        mean_abs_diff = np.mean(np.abs(img1 - img2))
        assert mean_abs_diff < 1.0, f"fig04 renders differ too much: {mean_abs_diff}"


def test_render_is_not_degenerate():
    # A camera/lighting misconfiguration (e.g. the inverted-front-vector bug
    # or the wrong-camera-origin bug this test was added alongside) can
    # produce a blank/near-blank render that still passes the two tests
    # above (file exists, two blank renders are "reproducible" with each
    # other). Guard against that directly.
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig04.png")
        f4.render(out_path=out)
        img = np.asarray(Image.open(out).convert("RGB"))
        unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
        assert unique_colors > 100, (
            f"render looks blank/degenerate: only {unique_colors} unique colors")
        bg = np.asarray(matplotlib.colors.to_rgb(fs.SLIDE_BG)) * 255
        nonbg_frac = np.mean(np.any(np.abs(img.astype(int) - bg.astype(int)) > 10, axis=-1))
        assert 0.01 < nonbg_frac < 0.60, (
            f"non-background pixel fraction {nonbg_frac:.3f} looks degenerate")


if __name__ == "__main__":
    test_render_produces_file()
    test_render_is_structurally_reproducible()
    test_render_is_not_degenerate()
    print("ALL PASS")
