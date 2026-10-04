"""Make the presentation figure modules importable from the tests."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "figures", "presentation"))
sys.path.insert(0, ROOT)
