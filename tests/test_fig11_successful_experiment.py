"""
test_fig11_successful_experiment.py -- smoke + data-integrity +
non-degenerate test for fig11_successful_experiment.py (3D v2).

Run: python -m pytest tests/test_fig11_successful_experiment.py
"""
import os
import tempfile

import numpy as np
from PIL import Image

import fig11_successful_experiment as f11
import fig_data as fd
import scene3d as s3


def test_trial9_is_real_grasp_ok_autonomous():
    rows = fd.load_trials()
    trial = [r for r in rows if "trial 9," in r["note"]][0]
    assert trial["verdict"] == "GRASP_OK"
    assert "autonomous" in trial["note"]
    assert "no hand-placing" in trial["note"]


def test_z_rise_value_matches_trials_csv():
    rows = fd.load_trials()
    trial = [r for r in rows if "trial 9," in r["note"]][0]
    z_rise_m = float(trial["z_rise_m"])
    assert abs(z_rise_m - 0.1420) < 1e-3


def test_lift_pose_z_delta_equals_real_z_rise_exactly():
    # The rendered "lift" pose differs from the "grasp" pose only by adding
    # the real z_rise_m to arm_lift_joint -- verify the resulting palm-frame
    # world Z delta equals that real magnitude exactly (no other joint may
    # move, matching the real single-axis lift ramp).
    scene = s3.build_scene()
    z_rise_m = 0.1420
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    T_world_base = s3.world_base_transform(*scene.base_selected)
    z1 = (T_world_base @ s3.fk(J, seq, scene.joints_selected))[2, 3]
    joints_lift = dict(scene.joints_selected)
    joints_lift["arm_lift_joint"] += z_rise_m
    z2 = (T_world_base @ s3.fk(J, seq, joints_lift))[2, 3]
    assert abs((z2 - z1) - z_rise_m) < 1e-9


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig11.png")
        path = f11.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_not_degenerate():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig11.png")
        f11.render(out_path=out)
        with Image.open(out) as im:
            img = np.asarray(im.convert("RGB"))
        unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
        assert unique_colors > 50, f"render looks blank/degenerate: only {unique_colors} unique colors"


if __name__ == "__main__":
    test_trial9_is_real_grasp_ok_autonomous()
    test_z_rise_value_matches_trials_csv()
    test_lift_pose_z_delta_equals_real_z_rise_exactly()
    test_render_produces_file()
    test_render_is_not_degenerate()
    print("ALL PASS")
