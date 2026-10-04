"""
Diagnostic logging helper for AffordGrasp pipeline.
Only active when the AFFORD_DEBUG environment variable is set to a non-empty value.
All functions are no-ops when AFFORD_DEBUG is unset, so normal runs are unaffected.
"""
import os
import json
import time

_ENABLED: bool = bool(os.environ.get("AFFORD_DEBUG"))
_LOG: dict = {"meta": {}, "checkpoints": []}


def enabled() -> bool:
    return _ENABLED


def meta(**kwargs) -> None:
    if _ENABLED:
        _LOG["meta"].update({k: _cvt(v) for k, v in kwargs.items()})


def cp(name: str, **data) -> None:
    if not _ENABLED:
        return
    entry: dict = {"cp": name, "t": round(time.time(), 3)}
    for k, v in data.items():
        entry[k] = _cvt(v)
    _LOG["checkpoints"].append(entry)
    preview = json.dumps(entry, default=str)
    print(f"[DIAG:{name}] {preview[:400]}")


def motion_record(record: dict) -> None:
    """Append one waypoint record to _LOG["motion_trace"]."""
    if not _ENABLED:
        return
    if "motion_trace" not in _LOG:
        _LOG["motion_trace"] = []
    _LOG["motion_trace"].append({k: _cvt(v) for k, v in record.items()})


def save(path: str) -> None:
    if not _ENABLED:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(_LOG, f, indent=2, default=str)
    print(f"[DIAG] Saved diagnostics -> {path}")


def _cvt(v):
    """Recursively convert numpy / torch types to JSON-serialisable Python."""
    try:
        import numpy as np
        if isinstance(v, np.ndarray):
            if v.size <= 16:
                return v.tolist()
            return {
                "shape": list(v.shape),
                "dtype": str(v.dtype),
                "min": float(v.min()),
                "max": float(v.max()),
                "mean": float(v.mean()),
                "std": float(v.std()),
            }
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
    except ImportError:
        pass
    if isinstance(v, (list, tuple)):
        return [_cvt(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _cvt(val) for k, val in v.items()}
    return v
