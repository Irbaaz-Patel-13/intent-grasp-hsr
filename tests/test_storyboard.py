"""
test_storyboard.py -- validates the storyboard contact sheet's structure.

Run: python -m pytest tests/test_storyboard.py
"""
import os
import tempfile

import storyboard as sb


def test_all_13_entries_present_with_required_fields():
    assert len(sb.STORYBOARD_ENTRIES) == 13
    required = {"n", "title", "claim", "source", "technique", "composition"}
    for entry in sb.STORYBOARD_ENTRIES:
        assert required.issubset(entry.keys())
        assert entry["claim"].strip() != ""
        assert entry["source"].strip() != ""


def test_entry_numbers_are_1_through_13_unique():
    ns = sorted(e["n"] for e in sb.STORYBOARD_ENTRIES)
    assert ns == list(range(1, 14))


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "storyboard.png")
        path = sb.render_storyboard(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


if __name__ == "__main__":
    test_all_13_entries_present_with_required_fields()
    test_entry_numbers_are_1_through_13_unique()
    test_render_produces_file()
    print("ALL PASS")
