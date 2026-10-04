"""Repository locations shared by the package, scripts and figure code.

Every script used to live at the repository root and read its inputs from
there. After the reorganisation the inputs live under ``workspace/``, so
anything that used to be "next to the script" now resolves against
``WORKSPACE`` instead.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = REPO_ROOT / "workspace"
THIRD_PARTY = REPO_ROOT / "third_party"
