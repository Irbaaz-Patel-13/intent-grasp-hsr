"""
test_fig09_execution_sequence.py -- smoke + data-integrity + reproducibility
test for fig09_execution_sequence.py (3D v2).

Run: python -m pytest tests/test_fig09_execution_sequence.py
"""
import os
import tempfile

import numpy as np
from PIL import Image

import fig09_execution_sequence as f9
import fig_data as fd
import scene3d as s3


def test_trial_12_is_real_grasp_ok_with_expected_values():
    rows = fd.load_trials()
    trial = f9._find_trial(rows, "trial 12")
    assert trial["verdict"] == "GRASP_OK"
    assert abs(float(trial["hand_motor"]) - (-0.3521)) < 1e-3
    assert abs(float(trial["z_rise_m"]) - 0.1418) < 1e-3


def test_gate_thresholds_are_real_calibrated_constants():
    assert f9.G3_EPS == -0.885


def test_lift_frame_z_delta_equals_real_z_rise_exactly():
    scene = s3.build_scene()
    z_rise_m = 0.1418
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    T_world_base = s3.world_base_transform(*scene.base_selected)
    z1 = (T_world_base @ s3.fk(J, seq, scene.joints_selected))[2, 3]
    joints_lift = dict(scene.joints_selected)
    joints_lift["arm_lift_joint"] += z_rise_m
    z2 = (T_world_base @ s3.fk(J, seq, joints_lift))[2, 3]
    assert abs((z2 - z1) - z_rise_m) < 1e-9


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig09.png")
        path = f9.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    import hashlib

    def _sha256(path):
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f9.render(out_path=out1)
        f9.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig09 output is not reproducible"


def test_render_is_not_degenerate():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig09.png")
        f9.render(out_path=out)
        with Image.open(out) as im:
            img = np.asarray(im.convert("RGB"))
        unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
        assert unique_colors > 50, f"render looks blank/degenerate: only {unique_colors} unique colors"


if __name__ == "__main__":
    test_trial_12_is_real_grasp_ok_with_expected_values()
    test_gate_thresholds_are_real_calibrated_constants()
    test_lift_frame_z_delta_equals_real_z_rise_exactly()
    test_render_produces_file()
    test_render_is_reproducible()
    test_render_is_not_degenerate()
    print("ALL PASS")
