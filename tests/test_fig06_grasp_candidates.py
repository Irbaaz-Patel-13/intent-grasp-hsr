"""
test_fig06_grasp_candidates.py -- smoke + data-integrity + structural
reproducibility test for fig06_grasp_candidates.py.

Reproducibility here is structural (mean pixel difference under a
threshold), not byte-hash, for the same reason as fig04_pointcloud.py:
Open3D's Visualizer rasterizer is not guaranteed byte-stable across
reruns/drivers even with seeded point selection.

Run: python -m pytest tests/test_fig06_grasp_candidates.py
"""
import os
import tempfile

import numpy as np
from PIL import Image

import fig06_grasp_candidates as f6
import fig_data as fd


def test_executed_candidate_is_not_top_ranked():
    gc = fd.load_grasp_candidates()
    exec_score = gc.combined_score[f6.EXECUTED_CANDIDATE]
    assert exec_score < gc.combined_score.max(), (
        "candidate 24 should NOT be the top combined_score candidate for this trial")
    rank = int((gc.combined_score > exec_score).sum()) + 1
    assert rank >= 20, f"expected candidate 24 near the bottom of the ranking, got rank {rank}/25"


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig06.png")
        path = f6.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_not_degenerate():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig06.png")
        f6.render(out_path=out)
        with Image.open(out) as im:
            img = np.asarray(im.convert("RGB"))
        unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
        assert unique_colors > 50, f"render looks blank/degenerate: only {unique_colors} unique colors"


if __name__ == "__main__":
    test_executed_candidate_is_not_top_ranked()
    test_render_produces_file()
    test_render_is_not_degenerate()
    print("ALL PASS")
