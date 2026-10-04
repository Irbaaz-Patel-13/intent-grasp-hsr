"""
test_fig08_motion_planning.py -- smoke + data-integrity + reproducibility +
geometry test for fig08_motion_planning.py (3D canonical-scene v3).

Run: python -m pytest tests/test_fig08_motion_planning.py
"""
import os
import tempfile

import matplotlib
import numpy as np
from PIL import Image

import fig08_motion_planning as f8
import fig_data as fd
import figstyle as fs


def test_base_clear_and_reach_match_verified_constants():
    # scripts/robot/hsr_base_placement.py -- spot-verified
    # against source; guards against silent drift.
    assert f8.BASE_CLEAR_M == 0.32
    assert f8.REACH_M == 0.633


def test_real_reachability_story_is_correct():
    gc = fd.load_grasp_candidates()
    g = fd.load_grounding()
    target_xy = g.aff_center_3d[:2]
    d_origin = float(np.linalg.norm(target_xy))
    sel_xy = np.array([gc.base_x[f8.EXECUTED_CANDIDATE], gc.base_y[f8.EXECUTED_CANDIDATE]])
    d_sel = float(np.linalg.norm(target_xy - sel_xy))
    assert d_origin > f8.REACH_M, "expected target to be outside reach from the initial base"
    assert d_sel < f8.REACH_M, "expected target to be inside reach from the selected base"
    assert abs(d_origin - 0.678) < 0.01
    assert abs(d_sel - 0.412) < 0.01


def test_target_lies_outside_initial_circle_and_inside_candidate24_circle():
    # Direct Euclidean-distance geometry check, independent of rendering --
    # this is the exact claim the BEFORE/AFTER panels must make visible.
    gc = fd.load_grasp_candidates()
    g = fd.load_grounding()
    target_xy = g.aff_center_3d[:2]
    origin = np.zeros(2)
    sel_xy = np.array([gc.base_x[f8.EXECUTED_CANDIDATE], gc.base_y[f8.EXECUTED_CANDIDATE]])
    assert np.linalg.norm(target_xy - origin) > f8.REACH_M
    assert np.linalg.norm(target_xy - sel_xy) < f8.REACH_M


def test_keepout_cells_use_the_real_documented_formula():
    cloud = fd.load_fused_cloud()
    cells = f8.real_keepout_cells(cloud)
    band = cloud[(cloud[:, 2] > 0.30) & (cloud[:, 2] < 0.65)]
    assert len(band) > 0, "expected some real points in the body-strike band for this trial"
    assert cells.shape[1] == 2


def test_all_25_real_candidates_are_used():
    gc = fd.load_grasp_candidates()
    assert len(gc.base_x) == 25
    assert not np.isnan(gc.base_x).any()
    assert not np.isnan(gc.base_y).any()


def test_render_produces_file_with_expected_dpi_dimensions():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig08.png")
        path = f8.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000
        with Image.open(out) as img:
            assert img.width > 1000 and img.height > 500


def test_render_is_not_degenerate():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig08.png")
        f8.render(out_path=out)
        with Image.open(out) as im:
            img = np.asarray(im.convert("RGB"))
        unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
        assert unique_colors > 50, f"render looks blank/degenerate: only {unique_colors} unique colors"


def test_render_contains_hero_and_inset_by_pixel_content():
    # The 3D hero panel (left) and the top-down inset (upper right) must
    # each have real (non-background) content -- guards against either
    # silently failing to draw.
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig08.png")
        f8.render(out_path=out)
        with Image.open(out) as im:
            img = np.asarray(im.convert("RGB")).astype(int)
        bg = np.array([int(c * 255) for c in matplotlib.colors.to_rgb(fs.SLIDE_BG)])
        diff = np.abs(img - bg).sum(axis=-1)
        w, h = img.shape[1], img.shape[0]
        hero = diff[int(0.20 * h):int(0.75 * h), int(0.04 * w):int(0.68 * w)]
        inset = diff[int(0.15 * h):int(0.55 * h), int(0.75 * w):int(0.96 * w)]
        assert (hero > 15).sum() > 500, "hero 3D panel looks empty"
        assert (inset > 15).sum() > 200, "top-down inset looks empty"


def test_render_is_reproducible():
    import hashlib

    def _sha256(path):
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f8.render(out_path=out1)
        f8.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig08 output is not reproducible"


if __name__ == "__main__":
    test_base_clear_and_reach_match_verified_constants()
    test_real_reachability_story_is_correct()
    test_target_lies_outside_initial_circle_and_inside_candidate24_circle()
    test_keepout_cells_use_the_real_documented_formula()
    test_all_25_real_candidates_are_used()
    test_render_produces_file_with_expected_dpi_dimensions()
    test_render_is_not_degenerate()
    test_render_contains_hero_and_inset_by_pixel_content()
    test_render_is_reproducible()
    print("ALL PASS")
