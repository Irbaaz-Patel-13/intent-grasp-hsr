"""
test_fig13_pipeline_summary.py -- smoke + reproducibility + data-integrity
test for fig13_pipeline_summary.py (hero-thumbnail v2).

Run: python -m pytest tests/test_fig13_pipeline_summary.py
"""
import hashlib
import os
import tempfile

import fig13_pipeline_summary as f13
import figstyle as fs


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_all_12_stage_thumbnails_reference_real_rendered_pngs():
    assert len(f13.STAGES) == 12
    for num, rel_path, title in f13.STAGES:
        png_path = os.path.join(fs.ASSET_ROOT, rel_path)
        assert os.path.exists(png_path), f"Fig {num} source PNG missing: {png_path}"


def test_stage_numbers_are_1_through_12_in_order():
    assert [num for num, _, _ in f13.STAGES] == list(range(1, 13))


def test_content_band_excludes_title_and_caption_rows():
    # The crop band must sit strictly inside the figure (not the whole
    # image), so title/caption text is dropped, not merely rescaled.
    assert 0.0 < f13.CONTENT_Y0 < f13.CONTENT_Y1 < 1.0
    assert f13.CONTENT_Y0 > 0.05
    assert f13.CONTENT_Y1 < 0.95


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig13.png")
        path = f13.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f13.render(out_path=out1)
        f13.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig13 output is not reproducible"


if __name__ == "__main__":
    test_all_12_stage_thumbnails_reference_real_rendered_pngs()
    test_stage_numbers_are_1_through_12_in_order()
    test_content_band_excludes_title_and_caption_rows()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
