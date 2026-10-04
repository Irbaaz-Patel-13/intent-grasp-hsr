"""
test_fig02_grounding.py -- smoke + reproducibility test for
fig02_grounding.py.

Run: python -m pytest tests/test_fig02_grounding.py
"""
import hashlib
import os
import tempfile

import fig02_grounding as f2


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_render_produces_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "fig02.png")
        path = f2.render(out_path=out)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 10_000


def test_render_is_reproducible():
    with tempfile.TemporaryDirectory() as tmp:
        out1 = os.path.join(tmp, "a.png")
        out2 = os.path.join(tmp, "b.png")
        f2.render(out_path=out1)
        f2.render(out_path=out2)
        assert _sha256(out1) == _sha256(out2), "fig02 output is not reproducible"


if __name__ == "__main__":
    test_render_produces_file()
    test_render_is_reproducible()
    print("ALL PASS")
