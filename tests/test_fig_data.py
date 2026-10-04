"""
test_fig_data.py -- unit tests for fig_data.py's experiment-directory
loaders, run against the real 2026-08-07 anchor trial.

Run: python -m pytest tests/test_fig_data.py
"""
import numpy as np

import fig_data as fd


def test_load_capture_shapes():
    cap = fd.load_capture()
    assert cap.rgb.shape == (480, 640, 3)
    assert cap.depth.shape == (480, 640)
    assert cap.K.shape == (3, 3)
    assert cap.tf_trans.shape == (3,)
    assert cap.tf_quat.shape == (4,)


def test_load_grounding_matches_capture_frame():
    cap = fd.load_capture()
    g = fd.load_grounding()
    assert np.array_equal(g.rgb, cap.rgb), \
        "grounding_rgb should be the same frame as head_capture_real.npz"
    assert g.object_mask.sum() > 0
    assert g.target_object == "red mug"
    assert g.target_part == "handle"


def test_mask_bbox_matches_mask_extent():
    g = fd.load_grounding()
    x0, y0, x1, y1 = fd.mask_bbox(g.object_mask)
    ys, xs = np.where(g.object_mask)
    assert x0 == xs.min() and x1 == xs.max() + 1
    assert y0 == ys.min() and y1 == ys.max() + 1


def test_load_grasp_candidates_joins_place_run_csv():
    gc = fd.load_grasp_candidates()
    assert gc.poses.shape == (25, 4, 4)
    assert gc.collision_free.shape == (25,)
    assert gc.manip.shape == (25,)
    assert not np.isnan(gc.manip).all(), "place_run.csv join produced all-NaN manip"
    assert bool(gc.collision_free[24]) is True  # candidate 24 was the one executed


def test_load_fused_cloud_point_count():
    pts = fd.load_fused_cloud()
    assert pts.shape == (241818, 3)


def test_camera_origin_matches_head_capture_tf_trans():
    # Independent cross-check: multiview.npz's first view and
    # head_capture_real.npz are the same real camera pose, from two
    # separately-saved files. If camera_origin() is computing the view
    # matrix -> position transform correctly, they must agree.
    cap = fd.load_capture()
    mv = fd.load_multiview()
    origin = fd.camera_origin(mv["camera_extrinsics"][0])
    assert origin.shape == (3,)
    assert np.allclose(origin, cap.tf_trans, atol=1e-3), (
        f"camera_origin {origin} does not match head_capture_real.npz "
        f"tf_trans {cap.tf_trans}")


def test_load_trials_has_verdict_column():
    rows = fd.load_trials()
    assert len(rows) == 12
    assert all("verdict" in r for r in rows)
    verdicts = {r["verdict"] for r in rows}
    assert "GRASP_OK" in verdicts


if __name__ == "__main__":
    test_load_capture_shapes()
    test_load_grounding_matches_capture_frame()
    test_mask_bbox_matches_mask_extent()
    test_load_grasp_candidates_joins_place_run_csv()
    test_load_fused_cloud_point_count()
    test_camera_origin_matches_head_capture_tf_trans()
    test_load_trials_has_verdict_column()
    print("ALL PASS")
