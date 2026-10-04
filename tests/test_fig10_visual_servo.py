"""
test_fig10_visual_servo.py -- smoke + data-integrity + reproducibility
test for fig10_visual_servo.py.

Run: python -m pytest tests/test_fig10_visual_servo.py
"""
import hashlib
import os
import tempfile

import fig10_visual_servo as f10
import fig_data as fd


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_real_photos_exist():
    assert os.path.exists(f10.PHOTO_SUCCESS), f"missing real photo: {f10.PHOTO_SUCCESS}"
    assert os.path.exists(f10.PHOTO_FAILURE), f"missing real photo: {f10.PHOTO_FAILURE}"


def test_trial9_values_match_trials_csv():
    rows = fd.load_trials()
    trial9 = [r for r in rows if "trial 9," in r["note"]][0]
    assert "46.9" in trial9["note"] and "12.7" in trial9["note"]


def test_no_fabricated_convergence_curve():
    # Guard against a future edit accidentally introducing a fabricated
    # per-iteration convergence curve. The figure shows the real trial-9
    # before/after values as a number-arrow-number statement (not a bar
    # chart, not a line plot) -- either way, no interpolated/sampled trace
    # of intermediate iteration values may appear.
    import inspect
    src = inspect.getsource(f10.render)
    assert ".plot(" not in src, "fig10 must not draw a line/curve for servo error"
    assert "linspace" not in src and "np.arange" not in src, \
        "fig10 must not interpolate intermediate iteration values"
    assert "TRIAL9_BEFORE_PX" in src and "TRIAL9_AFTER_PX" in src, \
        "fig10 should display the two real discrete trial-9 values directly"


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig10.png")
        path = f10.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f10.render(out_path=out1)
        f10.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig10 output is not reproducible"


if __name__ == "__main__":
    test_real_photos_exist()
    test_trial9_values_match_trials_csv()
    test_no_fabricated_convergence_curve()
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
