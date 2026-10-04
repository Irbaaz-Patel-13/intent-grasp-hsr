"""
test_figstyle.py -- unit tests for figstyle.py's shared design-system helpers.

Run: python -m pytest tests/test_figstyle.py
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import figstyle as fs


def test_palette_hex_codes_are_valid():
    for name in ["SLIDE_BG", "INK", "MUTED", "FAINT", "ACCEPTED", "CANDIDATE",
                 "REJECTED", "REASONING"]:
        hexcode = getattr(fs, name)
        matplotlib.colors.to_rgb(hexcode)  # raises ValueError if invalid


def test_rejected_color_distinct_from_common_object_reds():
    # the mug is a saturated photographic red; REJECTED must not collide
    # with it so status overlays are never confusable with the object itself
    mug_red_approx = (0.80, 0.10, 0.08)
    rejected_rgb = matplotlib.colors.to_rgb(fs.REJECTED)
    dist = sum((a - b) ** 2 for a, b in zip(mug_red_approx, rejected_rgb)) ** 0.5
    assert dist > 0.05, "REJECTED accent is too close to the mug's own red"


def test_icon_registry_has_all_ten_stage_keys():
    expected = {"rgb_camera", "depth_camera", "point_cloud", "vlm", "grounding",
                "segmentation", "affordance", "grasp_generation",
                "motion_planning", "execution"}
    assert set(fs.ICON_KEYS) == expected


def test_draw_icon_renders_all_keys_without_error():
    fig, ax = plt.subplots()
    for key in fs.ICON_KEYS:
        fs.draw_icon(ax, key, 0.5, 0.5)
    plt.close(fig)


def test_draw_icon_rejects_unknown_key():
    fig, ax = plt.subplots()
    try:
        fs.draw_icon(ax, "not_a_real_stage", 0.5, 0.5)
        raised = False
    except ValueError:
        raised = True
    plt.close(fig)
    assert raised, "draw_icon should reject unknown icon keys"


def test_mask_overlay_transparent_outside_mask():
    mask = np.zeros((10, 10), dtype=bool)
    mask[3:6, 3:6] = True
    overlay = fs.mask_overlay(mask, fs.ACCEPTED, alpha=0.4)
    assert overlay.shape == (10, 10, 4)
    assert np.all(overlay[~mask, 3] == 0.0)
    assert np.all(overlay[mask, 3] == 0.4)


def test_asset_dir_creates_directory():
    import os
    path = fs.asset_dir("test_probe")
    assert os.path.isdir(path)


def test_seed_is_fixed_integer():
    assert isinstance(fs.SEED, int)


def test_draw_coordinate_frame_does_not_recolor_with_status_palette():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure()
    ax3 = fig.add_subplot(projection="3d")
    fs.draw_coordinate_frame(ax3, np.zeros(3), np.eye(3))
    for line in ax3.get_lines():
        assert line.get_color() != fs.REJECTED, \
            "coordinate frame must not reuse status-semantic colors"
    plt.close(fig)


if __name__ == "__main__":
    test_palette_hex_codes_are_valid()
    test_rejected_color_distinct_from_common_object_reds()
    test_icon_registry_has_all_ten_stage_keys()
    test_draw_icon_renders_all_keys_without_error()
    test_draw_icon_rejects_unknown_key()
    test_mask_overlay_transparent_outside_mask()
    test_asset_dir_creates_directory()
    test_seed_is_fixed_integer()
    test_draw_coordinate_frame_does_not_recolor_with_status_palette()
    print("ALL PASS")
