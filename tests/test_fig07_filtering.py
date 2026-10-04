"""
test_fig07_filtering.py -- smoke + data-integrity + reproducibility test
for fig07_filtering.py.

Run: python -m pytest tests/test_fig07_filtering.py
"""
import hashlib
import os
import tempfile

import fig07_filtering as f7
import fig_data as fd


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_collision_free_and_arm_only_ok_are_constant_for_this_trial():
    # This is the exact real-data fact the figure must not contradict:
    # no candidate is rejected by these columns in this trial.
    gc = fd.load_grasp_candidates()
    assert set(gc.collision_free.tolist()) == {True}
    assert set(gc.arm_only_ok.tolist()) == {True}


def test_clearance_m_is_a_constant_sentinel():
    gc = fd.load_grasp_candidates()
    assert len(set(gc.clearance_m.tolist())) == 1, "clearance_m should be a constant sentinel"


def test_executed_candidate_has_max_manip():
    gc = fd.load_grasp_candidates()
    assert gc.manip[f7.EXECUTED_CANDIDATE] == gc.manip.max()
    assert gc.manip[f7.EXECUTED_CANDIDATE] > f7.MANIP_MIN_THRESHOLD


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig07.png")
        path = f7.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f7.render(out_path=out1)
        f7.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig07 output is not reproducible"


if __name__ == "__main__":
    test_collision_free_and_arm_only_ok_are_constant_for_this_trial()
    test_clearance_m_is_a_constant_sentinel()
    test_executed_candidate_has_max_manip()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
