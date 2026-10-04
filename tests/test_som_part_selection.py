r"""
test_som_part_selection.py -- standalone smoke test for som_part_selection.py.
No GPU/SAM2/OpenAI calls: auto_regions() and ask_vlm_region() are monkeypatched
so this only exercises select_part_via_som()'s own logic (bbox-crop math,
sub-part filtering call, region-index validation, full-image mask mapping,
and the None-fallback paths a caller must handle).

Run: python -m pytest tests/test_som_part_selection.py
Expected on success: prints "ALL PASS" and exits 0; any assertion failure
raises AssertionError and exits non-zero.
"""
import numpy as np

from intent_grasp import som_part_selection as sps
class _FakeVLMConfig:
    api_key = ""       # forces ask_vlm_region's own no-client path when hit directly
    model_name = "gpt-4o-2024-08-06"


def _make_object_scene(h=40, w=40):
    """40x40 image; object mask is a 20x20 square at (10,10)-(30,30); bbox
    matches it exactly (no padding needed for the test)."""
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    object_mask = np.zeros((h, w), dtype=bool)
    object_mask[10:30, 10:30] = True
    object_bbox = (10, 10, 30, 30)
    return rgb, object_mask, object_bbox


def test_no_candidates_returns_none():
    rgb, object_mask, object_bbox = _make_object_scene()
    sps.auto_regions = lambda model, rgb_crop: []  # monkeypatch: SAM finds nothing
    part_mask, marked, n_cand, region, reason = sps.select_part_via_som(
        lang_sam_model=None, vlm_config=_FakeVLMConfig(), rgb=rgb,
        object_mask=object_mask, object_bbox=object_bbox,
        target_object="mug", target_part="handle", instruction="pick up the mug",
        crop_padding=0)
    assert part_mask is None, "expected None when no SAM regions are found"
    assert marked is None
    assert n_cand == 0
    assert region == -1


def test_happy_path_maps_region_to_full_image():
    rgb, object_mask, object_bbox = _make_object_scene()
    # crop_padding=0 -> crop is exactly object_bbox (10,10)-(30,30) = 20x20.
    # Two candidate regions inside that 20x20 crop (crop-local coordinates):
    # region 0 = a 4x4 patch, region 1 = a different 4x4 patch.
    crop_h, crop_w = 20, 20
    region0 = np.zeros((crop_h, crop_w), dtype=bool); region0[0:4, 0:4] = True
    region1 = np.zeros((crop_h, crop_w), dtype=bool); region1[16:20, 16:20] = True
    sps.auto_regions = lambda model, rgb_crop: [region0, region1]
    sps.filter_subparts = lambda regions, om: regions  # accept both as candidates
    sps.ask_vlm_region = lambda *a, **k: (1, "picked region 1")

    part_mask, marked, n_cand, region, reason = sps.select_part_via_som(
        lang_sam_model=None, vlm_config=_FakeVLMConfig(), rgb=rgb,
        object_mask=object_mask, object_bbox=object_bbox,
        target_object="mug", target_part="handle", instruction="pick up the mug",
        crop_padding=0)

    assert n_cand == 2
    assert region == 1
    assert part_mask is not None
    assert part_mask.shape == (40, 40)
    # region1 was crop-local [16:20,16:20]; bbox origin is (10,10) -> full-image [26:30,26:30]
    assert part_mask[26:30, 26:30].all()
    assert part_mask.sum() == 16, "only the chosen region's pixels should be set"


def test_out_of_range_region_returns_none():
    rgb, object_mask, object_bbox = _make_object_scene()
    region0 = np.zeros((20, 20), dtype=bool); region0[0:4, 0:4] = True
    sps.auto_regions = lambda model, rgb_crop: [region0]
    sps.filter_subparts = lambda regions, om: regions
    sps.ask_vlm_region = lambda *a, **k: (-1, "no_match")

    part_mask, marked, n_cand, region, reason = sps.select_part_via_som(
        lang_sam_model=None, vlm_config=_FakeVLMConfig(), rgb=rgb,
        object_mask=object_mask, object_bbox=object_bbox,
        target_object="mug", target_part="handle", instruction="pick up the mug",
        crop_padding=0)
    assert part_mask is None
    assert n_cand == 1
    assert region == -1


def test_ask_vlm_region_no_client_returns_minus_one():
    marked = None  # not touched before the api_key check
    region, reason = sps.ask_vlm_region(_FakeVLMConfig(), marked, "mug", "handle",
                                         "pick up the mug", n=3)
    assert region == -1
    assert reason == "no_vlm_client"


if __name__ == "__main__":
    # test_ask_vlm_region_no_client_returns_minus_one runs before the tests
    # that monkeypatch sps.ask_vlm_region -- those patches persist on the
    # module object for the rest of the process, so this must go first.
    test_ask_vlm_region_no_client_returns_minus_one()
    test_no_candidates_returns_none()
    test_happy_path_maps_region_to_full_image()
    test_out_of_range_region_returns_none()
    print("ALL PASS")
