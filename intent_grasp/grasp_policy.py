#!/usr/bin/env python
r"""
grasp_policy.py -- maps INFERRED TASK CONSTRAINTS to CLOSURE parameters.

Why this exists
---------------
The VLM contract already emits, per instruction:
    {target_part, keep_clear[+reasons], post_grasp_motion, stability_priority,
     thermal_or_hygiene}
Only the first two ever reached the robot: target_part chose a region and
keep_clear excluded surfaces. post_grasp_motion / stability_priority /
thermal_or_hygiene were computed, logged, and then DISCARDED before execution.
Consequence: two instructions with different inferred constraints could produce
an identical physical action -- the differentiation lived only in *where*, never
in *how*.

This module closes that gap: constraints -> (cage clearance, close depth, grip
force level, hold margin, post-grasp behaviour). All object-specific magnitudes
still come from perception (part_width from the cloud) and from the measured
gripper gap map; this module only supplies the CONSTRAINT-DEPENDENT modulation.

Related work
------------
DeliGrasp (Xie, Lavering & Correll, CoRL 2024) parameterises low-level
contact-rich manipulation from LLM-inferred *object* properties (mass,
friction, spring constant). This module is the task-conditioned counterpart:
the SAME object yields different closure parameters under different
instructions. The HSR gripper exposes effort + position rather than continuous
current control, so the force axis here is DISCRETISED into three levels --
a documented platform limitation, not a design preference.

Pure functions, no ROS / numpy-heavy deps -> unit-testable offline.
"""
from __future__ import annotations

# ---------------------------------------------------------------- constants
# Gripper properties (measured 14 Jul, TF fingertip sweep): ~64 mm per rad,
# usable aperture ceiling 0.127 m. Captures observed at hand_motor -0.29..-0.34.
MM_PER_RAD = 0.064
APERTURE_MAX_M = 0.125
APERTURE_MIN_M = 0.030

# Discrete force levels -> (apply_force effort, hold margin past contact in rad)
# hold_margin is how far BEYOND the detected contact position the fingers are
# commanded to hold. At 64 mm/rad: 0.010 rad ~= 0.6 mm of extra squeeze.
FORCE_LEVELS = {
    "gentle":   dict(effort=0.15, hold_margin=0.000),
    "standard": dict(effort=0.30, hold_margin=0.008),
    "firm":     dict(effort=0.50, hold_margin=0.016),
}

# Cage clearance: gap = part_width + clearance, BEFORE descent.
# Tighter cage = less free travel = less chance of shoving the object, but
# demands better lateral alignment. Loosened when alignment confidence is low.
CLEARANCE_M = {"tight": 0.015, "standard": 0.020, "loose": 0.030}


def _norm(x):
    return (x or "").strip().lower()


def force_level_for(stability_priority, post_grasp_motion):
    """Grip force is driven by how much the grasp must resist slip/torque.

    stability_priority is the VLM's own estimate of slip/tip risk.
    post_grasp_motion escalates it: a tilt_pour applies torque about the grasp
    axis, so it needs more than a straight translate; a handover ends with a
    human pulling the object, which also wants a secure (but releasable) hold.
    """
    s = _norm(stability_priority)
    m = _norm(post_grasp_motion)
    base = {"high": 2.0, "med": 1.0, "medium": 1.0, "low": 0.0}.get(s, 1.0)
    bump = {"tilt_pour": 1.0, "handover": 0.5, "translate": 0.0,
            "none": -1.0}.get(m, 0.0)
    score = base + bump
    if score < 1.0:
        return "gentle"
    if score < 2.0:
        return "standard"
    return "firm"


def close_depth_frac_for(stability_priority, post_grasp_motion):
    """Fraction of the object's height (above the support plane) at which the
    FINGERTIPS should close. Lower = deeper = nearer the centre of mass = a
    shorter lever arm and more resistance to tipping, at the cost of table
    clearance. Default 0.45 reproduces the pre-policy behaviour.
    """
    s = _norm(stability_priority)
    m = _norm(post_grasp_motion)
    if m == "tilt_pour" or s == "high":
        return 0.35          # deeper: resist torque / tipping
    if m == "handover" or s == "low":
        return 0.50          # shallower: leave room for the receiver
    return 0.45


def clearance_for(stability_priority, align_confident=True):
    if not align_confident:
        return CLEARANCE_M["loose"]
    return CLEARANCE_M["tight" if _norm(stability_priority) == "high"
                       else "standard"]


def post_grasp_plan_for(post_grasp_motion):
    """Behaviour AFTER a successful close. lift_m is conservative and is still
    clamped against arm_lift headroom by the executor (incident #9)."""
    m = _norm(post_grasp_motion)
    if m == "tilt_pour":
        return dict(lift_m=0.12, requires_controlled_tilt=True,
                    retreat="none",
                    note="clear the support before any wrist rotation")
    if m == "handover":
        return dict(lift_m=0.10, requires_controlled_tilt=False,
                    retreat="toward_receiver",
                    note="present the receiver-facing part; hold until release")
    if m == "none":
        return dict(lift_m=0.05, requires_controlled_tilt=False,
                    retreat="none", note="in-place manipulation")
    return dict(lift_m=0.10, requires_controlled_tilt=False,
                retreat="none", note="straight translate")


def gap_to_motor(gap_m, gap_map):
    """Invert the MEASURED gap map (list of (motor_rad, gap_m)). Falls back to
    the linear 64 mm/rad fit if no map is supplied."""
    if not gap_map:
        return round((gap_m - 0.0559) / MM_PER_RAD, 3)   # 0-rad intercept, 14 Jul
    pts = sorted(gap_map, key=lambda t: t[1])
    gaps = [g for _, g in pts]
    mots = [m for m, _ in pts]
    if gap_m <= gaps[0]:
        return mots[0]
    if gap_m >= gaps[-1]:
        return mots[-1]
    for i in range(1, len(gaps)):
        if gap_m <= gaps[i]:
            t = (gap_m - gaps[i-1]) / (gaps[i] - gaps[i-1])
            return round(mots[i-1] + t * (mots[i] - mots[i-1]), 3)
    return mots[-1]


def closure_policy(constraints, part_width_m=None, plane_z=None, obj_top_z=None,
                   gap_map=None, align_confident=True):
    """Constraints (+ perception) -> executable closure parameters.

    constraints: the VLM constraints dict.
    part_width_m / plane_z / obj_top_z: from grasp_close_params (perception).
    Returns a dict; keys with None mean 'perception not supplied'.
    """
    c = constraints or {}
    stab = c.get("stability_priority", "med")
    motion = c.get("post_grasp_motion", "translate")
    thermal = c.get("thermal_or_hygiene")
    if str(thermal).strip().lower() in ("", "null", "none", "nan", "n/a", "-"): thermal = None
    keep_clear = c.get("keep_clear", []) or []

    lvl = force_level_for(stab, motion)
    depth_frac = close_depth_frac_for(stab, motion)
    clear = clearance_for(stab, align_confident)
    post = post_grasp_plan_for(motion)

    out = dict(
        force_level=lvl,
        effort=FORCE_LEVELS[lvl]["effort"],
        hold_margin_rad=FORCE_LEVELS[lvl]["hold_margin"],
        close_depth_frac=depth_frac,
        cage_clearance_m=clear,
        keep_clear=list(keep_clear),
        thermal_or_hygiene=thermal,
        minimal_contact=bool(thermal),
        **post,
    )

    if part_width_m is not None:
        gap = min(max(part_width_m + clear, APERTURE_MIN_M), APERTURE_MAX_M)
        out["cage_gap_m"] = round(gap, 4)
        out["cage_motor_rad"] = gap_to_motor(gap, gap_map)
        out["width_gate_ok"] = int(part_width_m + clear <= APERTURE_MAX_M)
    if plane_z is not None and obj_top_z is not None:
        h = obj_top_z - plane_z
        z = plane_z + depth_frac * h
        z = min(max(z, plane_z + 0.025), obj_top_z - 0.025)
        out["close_z"] = round(z, 4)
        out["object_height_m"] = round(h, 4)
    return out


def explain(constraints, params):
    """One-line human-readable justification -- goes in the logs and the report."""
    c = constraints or {}
    bits = [f"stability={c.get('stability_priority')}",
            f"motion={c.get('post_grasp_motion')}"]
    if c.get("thermal_or_hygiene"):
        bits.append(f"thermal/hygiene={c['thermal_or_hygiene']}")
    if c.get("keep_clear"):
        bits.append(f"keep_clear={c['keep_clear']}")
    return ("%s -> force=%s(effort %.2f, hold %+.3f rad), depth_frac=%.2f, "
            "clearance=%.3f m, lift=%.2f m%s"
            % (", ".join(bits), params["force_level"], params["effort"],
               params["hold_margin_rad"], params["close_depth_frac"],
               params["cage_clearance_m"], params["lift_m"],
               ", controlled tilt" if params["requires_controlled_tilt"] else ""))

