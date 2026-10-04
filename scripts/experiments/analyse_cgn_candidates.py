#!/usr/bin/env python
r"""analyse_cgn_candidates.py -- why are the selected grasps always ~10 cm from
the affordance centre, and are near-vertical / horizontal candidates being
generated but discarded?

Every pipeline run prints "0 grasp(s) are BOTH within 0.06 m AND near-vertical"
and "NONE are body-centred + vertical". That is the reason the visual servo is
needed at all, and it has never been traced to a cause. This inspects the RAW
200-candidate dump (results/cgn_candidates/candidates_*.npz) against the 25 that
survive selection, and separates three hypotheses:

  H1 GENERATION  -- CGN never proposes close/vertical grasps for this geometry
                    (mask covers the whole mug, so contacts spread over the body)
  H2 RANKING     -- close/vertical candidates ARE generated but the ranking
                    (score / dist_to_aff) discards them
  H3 DEFINITION  -- the affordance "centre" is the centroid of a hollow
                    cylinder, i.e. mid-air inside the mug, so NO physical grasp
                    can be within 6 cm of it

Run in workspace/:
    .\.venv\Scripts\python.exe analyse_cgn_candidates.py
    .\.venv\Scripts\python.exe analyse_cgn_candidates.py --dump results\cgn_candidates\candidates_unknown_20260722_165127.npz
Writes cgn_candidate_analysis.md
"""
import argparse, glob, os, sys
import numpy as np


def newest_dump():
    c = sorted(glob.glob(os.path.join("results", "cgn_candidates", "candidates_*.npz")))
    if not c:
        sys.exit("no candidate dumps found under results/cgn_candidates/")
    return c[-1]


def find_poses(z):
    """Return (N,4,4) poses from an npz with unknown key naming."""
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 3 and a.shape[1:] == (4, 4) and a.shape[0] > 5:
            return a, k
    for k in z.files:                      # fallback: (N,3) positions only
        a = np.asarray(z[k])
        if a.ndim == 2 and a.shape[1] == 3 and a.shape[0] > 5:
            T = np.tile(np.eye(4), (len(a), 1, 1)); T[:, :3, 3] = a
            return T, k + " (positions only)"
    return None, None


def find_scores(z, n):
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 1 and a.shape[0] == n and a.dtype.kind == "f":
            if 0.0 <= float(np.nanmin(a)) and float(np.nanmax(a)) <= 1.0:
                return a, k
    return None, None


def stats(T, aff, label):
    pos = T[:, :3, 3]
    d = np.linalg.norm(pos - aff, axis=1)
    # approach axis = 3rd column; tilt from world -z (top-down)
    ap = T[:, :3, 2]
    nrm = np.linalg.norm(ap, axis=1); nrm[nrm == 0] = 1
    ap = ap / nrm[:, None]
    tilt = np.degrees(np.arccos(np.clip(-ap[:, 2], -1, 1)))
    print("\n%s  (n=%d)" % (label, len(T)))
    print("  dist_to_aff  min %.3f  p10 %.3f  median %.3f  max %.3f"
          % (d.min(), np.percentile(d, 10), np.median(d), d.max()))
    print("  tilt_from_vert  min %.1f  median %.1f  max %.1f deg"
          % (tilt.min(), np.median(tilt), tilt.max()))
    print("  within 0.06 m            : %d" % (d < 0.06).sum())
    print("  near-vertical (<45 deg)  : %d" % (tilt < 45).sum())
    print("  BOTH                     : %d" % ((d < 0.06) & (tilt < 45)).sum())
    print("  near-horizontal (>60 deg): %d" % (tilt > 60).sum())
    return d, tilt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=None)
    ap.add_argument("--cloud", default="fused_cloud.npz")
    ap.add_argument("--selected", default="grasps_plain.npz")
    a = ap.parse_args()

    dump = a.dump or newest_dump()
    print("raw dump   :", dump)
    zr = np.load(dump, allow_pickle=True)
    print("raw keys   :", list(zr.files))
    Traw, kr = find_poses(zr)
    if Traw is None:
        sys.exit("could not locate poses in the dump; keys above -- paste to Claude")
    print("raw poses  : key '%s' shape %s" % (kr, (Traw.shape,)))

    zs = np.load(a.selected, allow_pickle=True)
    Tsel, ks = find_poses(zs)
    aff = np.asarray(zs["aff_center_3d"]).ravel()
    print("selected   : key '%s' shape %s" % (ks, (Tsel.shape,)))
    print("aff centre :", np.round(aff, 3))

    d_raw, t_raw = stats(Traw, aff, "RAW CANDIDATES")
    d_sel, t_sel = stats(Tsel, aff, "SELECTED (top 25)")

    # H3: is the affordance centre inside the object's hollow interior?
    note3 = ""
    if os.path.exists(a.cloud):
        zc = np.load(a.cloud, allow_pickle=True)
        pts = None
        for k in zc.files:
            arr = np.asarray(zc[k])
            if arr.ndim == 2 and arr.shape[1] == 3 and arr.shape[0] > 1000:
                pts = arr; break
        if pts is not None:
            dd = np.linalg.norm(pts - aff, axis=1)
            near = (dd < 0.06).sum()
            surf = float(dd.min())
            print("\nAFFORDANCE-CENTRE GEOMETRY")
            print("  nearest CLOUD point to aff centre : %.3f m" % surf)
            print("  cloud points within 0.06 m        : %d" % near)
            note3 = ("nearest surface point is %.3f m from the affordance centre, "
                     "so a gripper contacting the object can never have its origin "
                     "within 0.06 m of that centre" % surf) if surf > 0.03 else \
                    ("surface reaches within %.3f m of the centre" % surf)

    # verdict
    both_raw = int(((d_raw < 0.06) & (t_raw < 45)).sum())
    print("\n---------------- VERDICT ----------------")
    if both_raw > 0:
        print("H2 RANKING: %d raw candidates are close AND vertical but did not "
              "survive selection -> the ranking (score/dist) is discarding the "
              "executable ones. Fix = re-rank, not re-generate." % both_raw)
    elif (t_raw < 45).sum() > 0 and (d_raw < 0.06).sum() == 0:
        print("H1/H3: vertical candidates exist, but NONE are within 0.06 m of "
              "the affordance centre at generation time.")
        if note3:
            print("     -> " + note3)
        print("     -> the 0.06 m criterion is measuring against a point no "
              "grasp can reach; the metric, not the grasps, is at fault.")
    else:
        print("H1 GENERATION: CGN does not propose near-vertical candidates for "
              "this geometry at all.")
    print("  near-horizontal raw candidates (>60 deg): %d  %s"
          % (int((t_raw > 60).sum()),
             "-> a horizontal drive-in mode would have candidates to execute"
             if (t_raw > 60).sum() else "-> no horizontal grasps generated"))

    with open("cgn_candidate_analysis.md", "w", encoding="utf-8") as f:
        f.write("# CGN candidate analysis\n\ndump: `%s`\n\n" % dump)
        f.write("| set | n | min dist | median dist | median tilt | <0.06m | <45deg | both | >60deg |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for lbl, d, t in (("raw", d_raw, t_raw), ("selected", d_sel, t_sel)):
            f.write("| %s | %d | %.3f | %.3f | %.1f | %d | %d | %d | %d |\n"
                    % (lbl, len(d), d.min(), np.median(d), np.median(t),
                       (d < 0.06).sum(), (t < 45).sum(),
                       ((d < 0.06) & (t < 45)).sum(), (t > 60).sum()))
        if note3:
            f.write("\n%s\n" % note3)
    print("\nwrote cgn_candidate_analysis.md")


if __name__ == "__main__":
    main()
