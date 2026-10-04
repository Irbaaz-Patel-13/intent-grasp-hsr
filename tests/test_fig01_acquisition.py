"""
test_fig01_acquisition.py -- smoke + reproducibility test for
fig01_acquisition.py.

Run: python -m pytest tests/test_fig01_acquisition.py
"""
import hashlib
import os
import tempfile

import fig01_acquisition as f1


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_frustum_corners_shape():
    import numpy as np
    K = np.array([[500.0, 0, 320.0], [0, 500.0, 240.0], [0, 0, 1.0]])
    corners = f1.frustum_corners(K, 640, 480)
    assert corners.shape == (4, 3)


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig01.png")
        path = f1.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f1.render(out_path=out1)
        f1.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig01 output is not reproducible"


if __name__ == "__main__":
    test_frustum_corners_shape()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
