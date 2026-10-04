#!/usr/bin/env python
r"""
part_decomposition.py -- pure-geometry part classifier for a single rigid
object's point cloud (rim / interior / body / handle), replacing reliance on
VLM/mask part-level selection in hand_part_grounding.py. No VLM/ROS/plotting
dependencies here so this stays independently testable -- see
test_part_decomposition.py for the synthetic-mug fixtures this was built
against.

Classification precedence (undocumented by the originating spec, decided
here): handle is resolved first via DBSCAN lateral-coherence on the
r > r_outer + 0.005 candidate ring, keeping only the single largest cluster
(a real handle is one coherent protrusion, not scattered outlier points);
rim/interior/body are then computed on the remaining points so a point is
never double-counted; anything matching none of the four bins is
"unclassified".
"""
import re
from typing import Optional

import numpy as np
from scipy.spatial import cKDTree

PART_NAMES = ["rim", "interior", "body", "handle", "unclassified"]
PART_COLORS = {"rim": "tab:blue", "interior": "tab:green", "body": "tab:purple",
               "handle": "tab:red", "unclassified": "lightgray"}


def extract_object_cloud(cloud: np.ndarray, centroid_xy: np.ndarray,
                          radius: float = 0.12) -> np.ndarray:
    """All points within `radius` (xy-only, ignores z) of centroid_xy."""
    xy_dist = np.linalg.norm(cloud[:, :2] - np.asarray(centroid_xy), axis=1)
    return cloud[xy_dist <= radius]


def remove_support_plane(points: np.ndarray, percentile: float = 15,
                          margin: float = 0.015):
    """
    z_table = the given percentile of points' z; drop points at or below
    z_table + margin. Returns (points_above, z_table).
    """
    z_table = float(np.percentile(points[:, 2], percentile))
    above = points[points[:, 2] > z_table + margin]
    return above, z_table


def dbscan_xy(xy: np.ndarray, eps: float = 0.015, min_samples: int = 15) -> np.ndarray:
    """
    Minimal DBSCAN on 2D points using scipy.spatial.cKDTree (no sklearn in
    this venv). Standard core/border/noise semantics; label -1 = noise.
    """
    n = len(xy)
    labels = np.full(n, -1, dtype=int)
    if n == 0:
        return labels
    tree = cKDTree(xy)
    neighbors = tree.query_ball_point(xy, r=eps)
    is_core = np.array([len(nb) >= min_samples for nb in neighbors])
    visited = np.zeros(n, dtype=bool)
    cluster_id = 0
    for i in range(n):
        if visited[i] or not is_core[i]:
            continue
        visited[i] = True
        labels[i] = cluster_id
        queue = list(neighbors[i])
        while queue:
            j = queue.pop()
            if not visited[j]:
                visited[j] = True
                labels[j] = cluster_id
                if is_core[j]:
                    queue.extend(neighbors[j])
            elif labels[j] == -1:
                labels[j] = cluster_id
        cluster_id += 1
    return labels


def classify_parts(points: np.ndarray, z_table: float,
                    dbscan_eps: float = 0.015, dbscan_min_samples: int = 15):
    """
    Buckets `points` (already above the support plane, see
    remove_support_plane) into rim/interior/body/handle/unclassified.
    Returns (parts: dict[str, np.ndarray], stats: dict).
    """
    axis_xy = points[:, :2].mean(axis=0)
    r = np.linalg.norm(points[:, :2] - axis_xy, axis=1)
    r_outer = float(np.percentile(r, 95))
    z_top = float(np.percentile(points[:, 2], 95))

    handle_mask = np.zeros(len(points), dtype=bool)
    handle_candidate = r > r_outer + 0.005
    if handle_candidate.sum() >= dbscan_min_samples:
        cand_idx = np.nonzero(handle_candidate)[0]
        labels = dbscan_xy(points[cand_idx][:, :2], eps=dbscan_eps,
                            min_samples=dbscan_min_samples)
        if (labels >= 0).any():
            counts = np.bincount(labels[labels >= 0])
            biggest = int(np.argmax(counts))
            handle_mask[cand_idx[labels == biggest]] = True

    remaining = ~handle_mask
    rim_mask = (remaining & (points[:, 2] > z_top - 0.02)
                & (r >= r_outer - 0.015) & (r <= r_outer + 0.01))
    interior_mask = (remaining & ~rim_mask & (points[:, 2] < z_top - 0.02)
                      & (r < r_outer - 0.02))
    body_mask = (remaining & ~rim_mask & ~interior_mask & (r >= r_outer - 0.015)
                 & (points[:, 2] > z_table + 0.02) & (points[:, 2] < z_top - 0.01))
    unclassified_mask = remaining & ~rim_mask & ~interior_mask & ~body_mask

    parts = {
        "rim": points[rim_mask],
        "interior": points[interior_mask],
        "body": points[body_mask],
        "handle": points[handle_mask],
        "unclassified": points[unclassified_mask],
    }
    stats = {"axis_xy": axis_xy, "r_outer": r_outer, "z_top": z_top, "z_table": z_table}
    return parts, stats


def handle_grasp_anchor(handle_points: np.ndarray, axis_xy: np.ndarray) -> np.ndarray:
    """
    The "handle root" -- the quarter of handle points closest to the object
    axis (where the handle attaches to the body), averaged. Used as the
    top-down grasp target instead of the full handle centroid: the free end
    of a handle loop can dangle away from the body, but the root is where a
    top-down gripper closing around the handle stock won't collide with the
    body.
    """
    r = np.linalg.norm(handle_points[:, :2] - axis_xy, axis=1)
    threshold = np.percentile(r, 25)
    root = handle_points[r <= threshold]
    if len(root) == 0:
        root = handle_points
    return root.mean(axis=0)


PART_SYNONYMS = {
    "rim": "rim", "opening": "rim", "lip": "rim",
    "body": "body", "side": "body", "wall": "body",
    "handle": "handle", "grip": "handle",
    "interior": "interior", "inside": "interior",
}

# rim/interior have no artificial minimum (unlike handle/body's 80/100), but
# every part still needs at least 1 point to be directly selectable -- see
# select_part_from_target's use of max(PART_MIN_POINTS[p], 1), not this dict
# value alone, wherever a literally-empty bucket must be rejected.
PART_MIN_POINTS = {"rim": 0, "interior": 0, "body": 100, "handle": 80}


def _normalize_part_name(name: str) -> Optional[str]:
    """
    Maps a free-text part/surface name to a canonical bucket name via
    PART_SYNONYMS. Tries an exact match first (the fast path for clean
    output like "handle"), then falls back to a word-boundary token search,
    since real VLM output is often a compound phrase ("rim/opening",
    "the rim", "rim or opening") rather than a single bare synonym word --
    exact-match-only silently failed to recognize these, which meant
    keep_clear enforcement could silently never fire against real VLM
    output (confirmed live: keep_clear=['rim/opening'] normalized to
    nothing under the old exact-match version). If a compound phrase
    contains tokens for more than one canonical bucket, the first
    PART_SYNONYMS entry (in the dict's definition order: rim family, then
    body, then handle, then interior) that appears wins -- deterministic,
    documented here since it's not obvious from the code alone.
    Returns None only if no known synonym token appears anywhere in the
    string.
    """
    text = (name or "").strip().lower()
    if not text:
        return None
    if text in PART_SYNONYMS:
        return PART_SYNONYMS[text]
    for synonym, canonical in PART_SYNONYMS.items():
        if re.search(rf"\b{re.escape(synonym)}\b", text):
            return canonical
    return None


def _largest_adequate_part(excluded: set, parts: dict, notes: list, reason: str) -> str:
    """
    Picks the largest of rim/body/handle/interior that is NOT in `excluded`
    and meets its own PART_MIN_POINTS threshold (tier 1). If nothing
    qualifies, relaxes to any NON-EMPTY part not in `excluded` (tier 2 --
    still respects the keep_clear constraint, just not the usual 80/100-pt
    minimums). If every non-excluded bucket is genuinely empty in this
    capture (e.g. a single oblique view where "interior" has 0 points, and
    keep_clear happens to exclude every other populated bucket), the
    keep_clear constraint is overridden as a last resort in favour of
    returning *some* usable geometry rather than a 0-point selection that
    would otherwise abort the whole grasp attempt (tier 3 -- loudly logged,
    since it means the VLM's stated constraint could not be geometrically
    honored). Only if literally every bucket is empty does this fall
    through to the previous unconditional choice, which the caller's own
    <3-point guard will then correctly abort on -- that's a genuine
    "no usable geometry at all" failure, not a fallback-logic gap.

    This tiering was tightened after a real battery run (see
    docs/superpowers/plans/2026-07-13-constraint-based-part-reasoning.md)
    showed the original two-tier version could return an empty bucket:
    PART_MIN_POINTS['rim']/['interior'] are 0 (no enforced minimum), so a
    literally-empty rim/interior bucket trivially satisfied the tier-1
    check, and the old tier-2 relaxation had no point-count floor at all.
    """
    tier1 = [p for p in ("body", "rim", "handle", "interior")
             if p not in excluded and len(parts[p]) >= PART_MIN_POINTS[p]
             and len(parts[p]) > 0]
    if tier1:
        best = max(tier1, key=lambda p: len(parts[p]))
        notes.append(f"{reason} -- falling back to largest adequate part not "
                     f"in keep_clear: '{best}' ({len(parts[best])} pts)")
        return best

    tier2 = [p for p in ("body", "rim", "handle", "interior")
             if p not in excluded and len(parts[p]) > 0]
    if tier2:
        best = max(tier2, key=lambda p: len(parts[p]))
        notes.append(f"{reason} -- no part not-in-keep_clear meets its usual "
                     f"point-count minimum; falling back to the largest "
                     f"NON-EMPTY part not in keep_clear: '{best}' "
                     f"({len(parts[best])} pts)")
        return best

    tier3 = [p for p in ("body", "rim", "handle", "interior") if len(parts[p]) > 0]
    if tier3:
        best = max(tier3, key=lambda p: len(parts[p]))
        notes.append(f"{reason} -- EVERY part not in keep_clear is empty in "
                     f"this capture; OVERRIDING keep_clear as a last resort "
                     f"so a grasp is still possible: '{best}' "
                     f"({len(parts[best])} pts). The VLM's keep_clear "
                     f"constraint could not be geometrically honored -- "
                     f"treat this grasp with reduced confidence.")
        return best

    best = max(("body", "rim", "handle", "interior"), key=lambda p: len(parts[p]))
    notes.append(f"{reason} -- every part is empty in this capture "
                 f"('{best}' picked with 0 pts); caller's point-count guard "
                 f"will abort.")
    return best


def select_part_from_target(target_part: str, keep_clear: list, parts: dict):
    """
    Maps the VLM's chosen target_part to one of rim/body/handle/interior by
    NAME EQUIVALENCE ONLY (see PART_SYNONYMS) -- this replaces instruction-
    keyword routing (the deleted select_part_for_instruction) now that part
    selection is the VLM's job (constraint-based reasoning, see
    affordance_reasoning.py's step-3 prompt), not this module's. This
    function's only remaining responsibility is geometric constraint
    enforcement: a part the VLM itself listed in keep_clear can never be
    selected, even as a fallback target, and the existing point-count
    fallbacks (handle<80, body<100) must also honor keep_clear.

    Returns (part_name, part_points, notes: list[str]).
    """
    notes = []
    canonical = _normalize_part_name(target_part)
    if canonical is None:
        notes.append(f"VLM target_part '{target_part}' has no recognized "
                      "synonym mapping -- defaulting to 'body'")
        canonical = "body"

    keep_clear_canonical = set()
    for kc in keep_clear or []:
        mapped = _normalize_part_name(kc)
        if mapped:
            keep_clear_canonical.add(mapped)
        else:
            notes.append(f"keep_clear entry '{kc}' has no recognized synonym "
                          "-- ignored for exclusion")

    if canonical in keep_clear_canonical:
        notes.append(f"VLM selected '{canonical}' which is also in keep_clear "
                      f"{sorted(keep_clear_canonical)} -- VLM inconsistency")
        canonical = _largest_adequate_part(
            keep_clear_canonical, parts, notes, "inconsistency fallback")
    elif len(parts[canonical]) < max(PART_MIN_POINTS[canonical], 1):
        notes.append(f"{canonical} has only {len(parts[canonical])} pts "
                      f"(<{max(PART_MIN_POINTS[canonical], 1)})")
        canonical = _largest_adequate_part(
            keep_clear_canonical | {canonical}, parts, notes, "point-count fallback")

    return canonical, parts[canonical], notes
