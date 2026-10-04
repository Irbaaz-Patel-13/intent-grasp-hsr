"""
test_fig05_affordance_reasoning.py -- smoke + reproducibility test for
fig05_affordance_reasoning.py.

Run: python -m pytest tests/test_fig05_affordance_reasoning.py
"""
import hashlib
import os
import tempfile

import numpy as np

import fig05_affordance_reasoning as f5
import fig_data as fd


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_project_point_matches_object_mask_centroid():
    cap = fd.load_capture()
    g = fd.load_grounding()
    u, v = fd.project_point(g.aff_center_3d, cap.K, cap.tf_trans, cap.tf_quat)
    ys, xs = np.where(g.object_mask)
    cu, cv = xs.mean(), ys.mean()
    assert abs(u - cu) < 15 and abs(v - cv) < 15, (
        f"projected anchor ({u:.1f},{v:.1f}) too far from object centroid ({cu:.1f},{cv:.1f})")


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig05.png")
        path = f5.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f5.render(out_path=out1)
        f5.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig05 output is not reproducible"


if __name__ == "__main__":
    test_project_point_matches_object_mask_centroid()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
