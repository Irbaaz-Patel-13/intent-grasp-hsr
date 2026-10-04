"""
test_scene3d.py -- FK validation + scene/camera contract tests for
scene3d.py (shared 3D rendering module for Figures 8, 9, 11).

Run: python -m pytest tests/test_scene3d.py
"""
import glob
import hashlib
import os

import numpy as np

import fig_data as fd
import scene3d as s3


def test_fk_matches_real_logged_grasp_pose_within_tolerance():
    # The core Stage-0 requirement: PyBullet/real-chain FK at candidate 24's
    # real logged joint values must match candidate 24's own real logged
    # grasp pose (grasps_plain.npz) to within 0.01 m / 1 deg.
    gc = fd.load_grasp_candidates()
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    q, base, _ = s3.load_candidate_joints(candidate=s3.EXECUTED_CANDIDATE)
    T_base_palm = s3.fk(J, seq, q)
    T_world_base = s3.world_base_transform(*base)
    T_world_palm = T_world_base @ T_base_palm

    pos_err = float(np.linalg.norm(T_world_palm[:3, 3] - gc.poses[s3.EXECUTED_CANDIDATE, :3, 3]))
    assert pos_err < 0.01, f"FK position error {pos_err:.4f} m exceeds 0.01 m tolerance"

    R_fk = T_world_palm[:3, :3]
    R_logged = gc.poses[s3.EXECUTED_CANDIDATE, :3, :3]
    R_rel = R_fk.T @ R_logged
    ang_err = float(np.degrees(np.arccos(np.clip((np.trace(R_rel) - 1) / 2, -1, 1))))
    assert ang_err < 1.0, f"FK orientation error {ang_err:.3f} deg exceeds 1 deg tolerance"


def test_fk_chain_includes_the_wrist_ft_sensor_fixed_joints():
    # Regression guard for the diagnosed root cause of the earlier ~0.88m Z
    # discrepancy: the real chain-builder must discover the wrist F/T
    # sensor's fixed joints between wrist_roll and hand_palm, not skip them.
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    assert "wrist_ft_sensor_frame_joint" in seq
    assert any("wrist_ft_sensor_frame" in jn for jn in seq)


def test_fk_prismatic_axis_scales_exactly_with_arm_lift():
    J, seq = s3.load_chain(s3.REAL_FK_URDF, "base_link", "hand_palm_link")
    q, _, _ = s3.load_candidate_joints(candidate=s3.EXECUTED_CANDIDATE)
    z1 = s3.fk(J, seq, q)[2, 3]
    q2 = dict(q)
    q2["arm_lift_joint"] = q["arm_lift_joint"] + 0.10
    z2 = s3.fk(J, seq, q2)[2, 3]
    assert abs((z2 - z1) - 0.10) < 1e-9


def test_real_base_pose_matches_place_run_csv():
    q, base, row = s3.load_candidate_joints(candidate=s3.EXECUTED_CANDIDATE)
    assert base[0] == float(row["base_x"])
    assert base[1] == float(row["base_y"])
    assert base[2] == float(row["base_yaw_rad"])


def test_build_scene_uses_real_data_only():
    scene = s3.build_scene()
    assert scene.base_initial == (0.0, 0.0, 0.0)
    assert scene.base_selected[0] != 0.0 or scene.base_selected[1] != 0.0
    assert len(scene.cloud) > 0
    assert scene.cloud.shape[1] == 3
    assert scene.keepout_xy.shape[1] == 2
    assert set(scene.joints_selected.keys()) == set(s3.ARM)


def test_only_three_named_cameras_are_defined():
    assert s3.CAM_ISO["kind"] == "perspective"
    assert s3.CAM_SIDE["kind"] == "ortho"
    assert s3.CAM_TOP["kind"] == "ortho"


def test_no_figure_module_defines_its_own_camera_constants():
    # CAM_* constants must live only in scene3d.py -- guards against a
    # figure quietly reintroducing a bespoke camera instead of reusing the
    # shared rig.
    fig_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "figures", "presentation")
    for path in glob.glob(os.path.join(fig_dir, "fig*.py")):
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        assert "CAM_ISO =" not in src, f"{path} defines its own CAM_ISO"
        assert "CAM_SIDE =" not in src, f"{path} defines its own CAM_SIDE"
        assert "CAM_TOP =" not in src, f"{path} defines its own CAM_TOP"


def test_view_and_projection_is_reproducible():
    scene = s3.build_scene()
    center = np.array(scene.base_selected[:2] + (0.55,))
    v1, p1, e1 = s3.view_and_projection(s3.CAM_ISO, center, 2.4)
    v2, p2, e2 = s3.view_and_projection(s3.CAM_ISO, center, 2.4)
    assert v1 == v2
    assert p1 == p2
    assert np.array_equal(e1, e2)


if __name__ == "__main__":
    test_fk_matches_real_logged_grasp_pose_within_tolerance()
    test_fk_chain_includes_the_wrist_ft_sensor_fixed_joints()
    test_fk_prismatic_axis_scales_exactly_with_arm_lift()
    test_real_base_pose_matches_place_run_csv()
    test_build_scene_uses_real_data_only()
    test_only_three_named_cameras_are_defined()
    test_no_figure_module_defines_its_own_camera_constants()
    test_view_and_projection_is_reproducible()
    print("ALL PASS")
