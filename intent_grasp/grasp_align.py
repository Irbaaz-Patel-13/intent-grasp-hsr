#!/usr/bin/env python
r"""grasp_align.py -- wrist-roll alignment of the gripper closing axis to an
object part's geometry.

Why
---
A parallel-jaw gripper must close ACROSS a part's narrow dimension. For a
compact part (mug body) any closing direction works, so this is moot. For an
ELONGATED part (hammer handle, knife handle, screwdriver shaft) the closing
axis must be perpendicular to the part's long axis, or the fingers straddle the
length and either miss or slide off.

part_decomposition.py already computes the PCA of each part -- eigenvalues,
linearity/planarity/sphericity, principal axis and minor-axis width -- and
reports shape_class='elongated'. That information is currently used only to
*label* the grasp (ideal_type='side_grasp'); it never reaches the commanded
pose. This module closes that gap: PCA principal axis -> required wrist_roll.

Convention
----------
Grasp pose T (4x4, base frame), following the CGN convention used throughout
this project (validated in grasp_close_params.py):
    T[:3,0] = closing axis  (direction between the fingers)
    T[:3,2] = approach axis (points toward the object)
wrist_roll_joint rotates the gripper about its tool axis, which for a top-down
grasp is the approach axis. Limits (hsrb): -1.92 .. 3.67 rad.

The closing axis is SIGN-SYMMETRIC (c and -c are the same grasp), so the
required roll is wrapped into [-pi/2, +pi/2]; this both removes the ambiguity
and keeps the correction small enough to stay inside joint limits.

IMPORTANT: the sign of the roll correction depends on the URDF's wrist_roll
axis direction. `--sign -1` flips it. Validate once on the robot with a
deliberately elongated object before trusting it (see verify_sign()).
"""
from __future__ import annotations
import numpy as np

WRIST_ROLL_MIN, WRIST_ROLL_MAX = -1.92, 3.67
APERTURE_MAX = 0.125


def pca_axes(points):
    """Principal axes + shape descriptors for an (N,3) part cloud."""
    P = np.asarray(points, float)
    if len(P) < 10:
        return None
    c = P.mean(0)
    X = P - c
    cov = np.cov(X.T)
    w, V = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    tot = float(w.sum()) or 1e-12
    linearity = float((w[0] - w[1]) / tot)
    planarity = float((w[1] - w[2]) / tot)
    sphericity = float(w[2] / tot)
    if linearity > 0.55:
        cls = "elongated"
    elif planarity > 0.45:
        cls = "planar"
    else:
        cls = "compact"
    # extents along each principal axis
    ext = [float(np.percentile(X @ V[:, i], 98) - np.percentile(X @ V[:, i], 2))
           for i in range(3)]
    return dict(centroid=c, axes=V, eigvals=w, linearity=linearity,
                planarity=planarity, sphericity=sphericity, shape_class=cls,
                long_axis=V[:, 0], extent=ext,
                minor_width=float(min(ext[1], ext[2])))


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def signed_angle_about(a, b, axis):
    """Signed angle from vector a to vector b, measured about `axis`."""
    a, b, axis = _unit(a), _unit(b), _unit(axis)
    a_p = _unit(a - np.dot(a, axis) * axis)
    b_p = _unit(b - np.dot(b, axis) * axis)
    s = float(np.dot(np.cross(a_p, b_p), axis))
    c = float(np.dot(a_p, b_p))
    return float(np.arctan2(s, c))


def wrap_half(a):
    """Wrap into [-pi/2, pi/2] -- the closing axis is sign-symmetric."""
    while a > np.pi / 2:
        a -= np.pi
    while a < -np.pi / 2:
        a += np.pi
    return a


def align_wrist_roll(T, part_points, wrist_roll_now=0.0, sign=+1.0,
                     force_align=False):
    """Roll correction so the fingers close ACROSS the part.

    Returns a dict; `apply` is False when no correction is warranted (compact
    part) or possible (joint limit / width gate), with `reason` explaining why.
    """
    pca = pca_axes(part_points)
    if pca is None:
        return dict(apply=False, reason="too few part points", pca=None)

    approach = _unit(np.asarray(T)[:3, 2])
    closing = _unit(np.asarray(T)[:3, 0])
    long_axis = pca["long_axis"]

    # desired closing direction: perpendicular to the long axis, in the plane
    # normal to the approach axis
    long_perp = long_axis - np.dot(long_axis, approach) * approach
    if np.linalg.norm(long_perp) < 1e-6:
        return dict(apply=False, pca=pca,
                    reason="long axis is parallel to the approach axis; "
                           "closing direction already unconstrained")
    desired = _unit(np.cross(approach, _unit(long_perp)))

    delta = wrap_half(signed_angle_about(closing, desired, approach))
    misalign_deg = abs(np.degrees(delta))
    target = wrist_roll_now + sign * delta

    out = dict(pca=pca, shape_class=pca["shape_class"],
               linearity=round(pca["linearity"], 3),
               minor_width=round(pca["minor_width"], 4),
               long_extent=round(pca["extent"][0], 4),
               closing_now=closing, closing_desired=desired,
               approach=approach, long_axis=long_axis,
               delta_rad=round(float(delta), 4),
               misalign_deg=round(float(misalign_deg), 1),
               wrist_roll_now=round(float(wrist_roll_now), 4),
               wrist_roll_target=round(float(target), 4))

    if pca["shape_class"] != "elongated" and not force_align:
        out.update(apply=False,
                   reason="part is %s (linearity %.2f) -- closing direction is "
                          "not geometrically constrained" % (pca["shape_class"],
                                                             pca["linearity"]))
        return out
    if pca["minor_width"] + 0.02 > APERTURE_MAX:
        out.update(apply=False,
                   reason="WIDTH GATE: minor width %.3f m + clearance exceeds "
                          "aperture %.3f m" % (pca["minor_width"], APERTURE_MAX))
        return out
    if not (WRIST_ROLL_MIN <= target <= WRIST_ROLL_MAX):
        alt = target - np.pi if target > WRIST_ROLL_MAX else target + np.pi
        if WRIST_ROLL_MIN <= alt <= WRIST_ROLL_MAX:
            out.update(apply=True, wrist_roll_target=round(float(alt), 4),
                       reason="using the equivalent +/-pi solution to stay in limits")
            return out
        out.update(apply=False,
                   reason="wrist_roll target %.3f outside limits [%.2f, %.2f]"
                          % (target, WRIST_ROLL_MIN, WRIST_ROLL_MAX))
        return out
    if misalign_deg < 5.0:
        out.update(apply=False, reason="already aligned within 5 deg")
        return out

    out.update(apply=True, reason="elongated part: rotating closing axis %.1f deg "
                                  "to close across the %.3f m minor width"
                                  % (misalign_deg, pca["minor_width"]))
    return out


def verify_sign_procedure():
    return (
        "SIGN VALIDATION (do once, on the robot, with an elongated object):\n"
        "  1. Place a hammer/screwdriver on the table, long axis clearly oblique.\n"
        "  2. Run the pipeline to --stage arm (hover), note wrist_roll from\n"
        "     /hsrb/joint_states and the reported misalign_deg.\n"
        "  3. Command wrist_roll to wrist_roll_target and LOOK: the fingers must\n"
        "     now straddle the handle ACROSS its width, not along its length.\n"
        "  4. If they rotated the wrong way, rerun with sign=-1 and record the\n"
        "     correct sign in RUNBOOK.md as a robot constant.")
