"""
test_fig12_failure_analysis.py -- smoke + data-integrity + reproducibility
test for fig12_failure_analysis.py.

Run: python -m pytest tests/test_fig12_failure_analysis.py
"""
import hashlib
import os
import tempfile

import fig12_failure_analysis as f12
import fig_data as fd


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_trial_verdicts_match_real_data():
    rows = fd.load_trials()
    assert f12._find(rows, "trial 1,")["verdict"] == "ABORT_"
    assert f12._find(rows, "trial 3,")["verdict"] == "ABORT_"
    assert f12._find(rows, "trial 4,")["verdict"] == "HELD_LIFT_FAULT"
    assert f12._find(rows, "trial 6,")["verdict"] == "GRASP_OK"


def test_trial_6_note_references_incident_10():
    rows = fd.load_trials()
    t6 = f12._find(rows, "trial 6,")
    assert "incident #10" in t6["note"]


def test_trial_5_is_real_confirmed_recovery_for_trial_4():
    # Trial 5's own note + hold_margin=0.000 corroborate the 27-Jul
    # lift-fault fix (lab_patch_0727_lift.py), dated one day after the
    # patch -- this is what justifies showing it as chain A's RECOVERY.
    rows = fd.load_trials()
    t4 = f12._find(rows, "trial 4,")
    t5 = f12._find(rows, "trial 5,")
    assert t4["verdict"] == "HELD_LIFT_FAULT"
    assert t5["verdict"] == "GRASP_OK"
    assert "lift patch" in t5["note"]
    assert float(t5["hold_margin"]) == 0.0
    assert t4["timestamp"][:10] == "2026-07-25"
    assert t5["timestamp"][:10] == "2026-07-28"


def test_unconfirmed_trials_are_not_claimed_as_grasp_ok():
    # Trials 1/3 must stay visually/semantically separate from the two
    # confirmed recovery chains -- they are real failures, not successes.
    rows = fd.load_trials()
    t1 = f12._find(rows, "trial 1,")
    t3 = f12._find(rows, "trial 3,")
    assert t1["verdict"] != "GRASP_OK"
    assert t3["verdict"] != "GRASP_OK"


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig12.png")
        path = f12.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f12.render(out_path=out1)
        f12.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig12 output is not reproducible"


if __name__ == "__main__":
    test_trial_verdicts_match_real_data()
    test_trial_6_note_references_incident_10()
    test_trial_5_is_real_confirmed_recovery_for_trial_4()
    test_unconfirmed_trials_are_not_claimed_as_grasp_ok()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
