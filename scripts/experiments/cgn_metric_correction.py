#!/usr/bin/env python
r"""cgn_metric_correction.py -- measure grasp-to-affordance proximity in a
convention-independent way.

Motivation: the pipeline's "dist_to_aff" is the Euclidean distance from CGN's
grasp-pose ORIGIN (the gripper base) to the affordance centre. Because the
origin sits ~one gripper-depth behind the contact, that distance can never be
small for a valid grasp -- 0/200 raw candidates fall inside the 0.06 m
criterion, with a floor of 0.085 m. The criterion is therefore unpassable by
construction, and the warning it triggers ("NONE are body-centred + vertical:
expect CONTROL_FAILED ... HSR 5-DoF wrist limit") is a misattribution.

Convention-independent alternative: decompose (aff - origin) along the grasp's
approach axis into
    depth_along_approach  = how far back the origin sits  (a gripper property)
    perpendicular_offset  = how far the approach RAY misses the affordance
                            (the quantity that actually matters for aiming)
A well-aimed grasp has a small perpendicular offset regardless of where the
pose origin is defined.

Run in workspace/:
    .\.venv\Scripts\python.exe cgn_metric_correction.py --dump <latest candidates npz>
Writes cgn_metric_correction.md
"""
import argparse, glob, os, sys
import numpy as np


def find_poses(z):
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 3 and a.shape[1:] == (4, 4) and a.shape[0] > 5:
            return a, k
    return None, None


def decompose(T, aff):
    o = T[:, :3, 3]
    ap = T[:, :3, 2]
    n = np.linalg.norm(ap, axis=1); n[n == 0] = 1
    ap = ap / n[:, None]
    v = aff - o                                   # origin -> affordance
    depth = np.einsum("ij,ij->i", v, ap)          # along approach
    perp = np.linalg.norm(v - depth[:, None] * ap, axis=1)
    tilt = np.degrees(np.arccos(np.clip(-ap[:, 2], -1, 1)))
    return depth, perp, np.linalg.norm(v, axis=1), tilt


def report(name, depth, perp, euc, tilt, f):
    def q(a):
        return "min %.3f  p25 %.3f  median %.3f  p75 %.3f  max %.3f" % (
            a.min(), np.percentile(a, 25), np.median(a), np.percentile(a, 75), a.max())
    lines = [
        "\n%s (n=%d)" % (name, len(perp)),
        "  euclidean origin->aff (CURRENT metric) : " + q(euc),
        "  depth along approach (gripper offset)  : " + q(depth),
        "  PERPENDICULAR offset (aiming error)    : " + q(perp),
        "  perp < 0.02 m : %d   perp < 0.03 m : %d   perp < 0.06 m : %d"
        % ((perp < 0.02).sum(), (perp < 0.03).sum(), (perp < 0.06).sum()),
    ]
    for l in lines:
        print(l); f.write(l + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=None)
    ap.add_argument("--selected", default="grasps_plain.npz")
    a = ap.parse_args()
    dump = a.dump
    if dump is None:
        c = glob.glob(os.path.join("results", "cgn_candidates", "candidates_*.npz"))
        if not c:
            sys.exit("no dumps found; pass --dump")
        dump = max(c, key=os.path.getmtime)          # newest by TIME, not name
    print("dump:", dump)

    zs = np.load(a.selected, allow_pickle=True)
    aff = np.asarray(zs["aff_center_3d"]).ravel()
    Tsel, _ = find_poses(zs)
    zr = np.load(dump, allow_pickle=True)
    Traw, _ = find_poses(zr)
    if Traw is None or Tsel is None:
        sys.exit("could not locate poses")

    with open("cgn_metric_correction.md", "w", encoding="utf-8") as f:
        f.write("# Grasp-to-affordance proximity, convention-corrected\n\n")
        f.write("dump: `%s`   aff centre: %s\n" % (dump, np.round(aff, 3).tolist()))
        f.write("```\n")
        report("RAW CANDIDATES", *decompose(Traw, aff), f=f)
        report("SELECTED (top 25)", *decompose(Tsel, aff), f=f)
        d, p, e, t = decompose(Tsel, aff)
        f.write("```\n\n")
        verdict = (
            "Selected grasps miss the affordance centre by a median of %.3f m "
            "PERPENDICULAR to the approach axis, while sitting a median of %.3f m "
            "back along it. The current euclidean metric (median %.3f m) is "
            "dominated by that gripper-depth offset, not by aiming error."
            % (np.median(p), np.median(d), np.median(e)))
        print("\n" + verdict)
        f.write(verdict + "\n")
    print("\nwrote cgn_metric_correction.md")


if __name__ == "__main__":
    main()
