#!/usr/bin/env python3
"""pick_grasp.py -- choose the grasp to execute, with all feasibility filters.

Replaces the inline snippet, which had two problems:
  * the width band 0.075-0.095 m was a MUG-DIAMETER constant -- a knife handle
    (~22 mm) or a hammer shaft (~30 mm) would be rejected outright, so the
    selection step could not generalise beyond cup-like objects. Now the band is
    scene-relative: within +-30% of the scene's own median part width, which is
    the same criterion grasp_close_params.py uses for its artifact guard.
  * it did not check LIFT HEADROOM. Trial 3 (23 Jul) selected grasp 10 with
    q_lift = 0.667; arm_lift's limit is 0.69, leaving 0.018 m -- below the 0.03 m
    the executor needs to verify a grasp, so it aborted after closing. Grasps
    are now rejected unless q_lift + LIFT_MIN + margin <= LIFT_MAX.

Usage:
    python3 pick_grasp.py                       # prints ranked candidates
    python3 pick_grasp.py --json                # machine-readable
    python3 pick_grasp.py --max_yaw 25 --relax  # widen if nothing passes
"""
import argparse, csv, json, math, sys

LIFT_MAX = 0.69      # arm_lift_joint upper limit
LIFT_MIN = 0.03      # minimum rise the executor needs for G3 verification
LIFT_MARGIN = 0.005


def load(place="place_run.csv", close="close_params.csv"):
    rows = list(csv.DictReader(open(place)))
    cp = {r["grasp_id"]: r for r in csv.DictReader(open(close))}
    return rows, cp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--place", default="place_run.csv")
    ap.add_argument("--close", default="close_params.csv")
    ap.add_argument("--max_yaw", type=float, default=25.0)
    ap.add_argument("--max_base_y", type=float, default=0.4)
    ap.add_argument("--width_tol", type=float, default=0.30,
                    help="accept part widths within this fraction of the scene median")
    ap.add_argument("--relax", action="store_true",
                    help="drop the base-pose preferences if nothing passes")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, cp = load(a.place, a.close)
    widths = [float(c["part_width_m"]) for c in cp.values()
              if c.get("ok") == "1" and c.get("part_width_m")]
    if not widths:
        sys.exit("no ok=1 rows with a width in %s" % a.close)
    w_med = sorted(widths)[len(widths)//2]

    cand, rejected = [], {}
    for r in rows:
        g = r["grasp"]; c = cp.get(g, {})
        why = None
        if r["arm_only_ok"] != "1":
            why = "not arm-reachable"
        elif r.get("collision_free", "1") == "0":
            why = "collision"
        elif c.get("ok") != "1":
            why = "close_params ok=0 (%s)" % (c.get("note") or "")
        else:
            w = float(c["part_width_m"])
            qlift = float(r.get("q_lift", 0.0))
            head = LIFT_MAX - qlift - LIFT_MARGIN
            yaw = math.degrees(float(r["base_yaw_rad"]))
            if abs(w - w_med) / w_med > a.width_tol:
                why = "width %.0fmm off scene median %.0fmm" % (w*1e3, w_med*1e3)
            elif head < LIFT_MIN:
                why = "lift headroom %.3f m < %.3f (q_lift %.3f)" % (head, LIFT_MIN, qlift)
            elif not a.relax and (abs(yaw) > a.max_yaw
                                  or abs(float(r["base_y"])) > a.max_base_y):
                why = "base pose off-front (yaw %.1f, y %.2f)" % (yaw, float(r["base_y"]))
        if why:
            rejected[g] = why
        else:
            cand.append(dict(grasp=g, manip=float(r["manip"]),
                             width=float(c["part_width_m"]),
                             headroom=round(LIFT_MAX - float(r.get("q_lift", 0)) - LIFT_MARGIN, 3),
                             yaw=round(math.degrees(float(r["base_yaw_rad"])), 1),
                             force=c.get("force_level", ""),
                             cage=c.get("cage_motor_rad", "")))
    cand.sort(key=lambda d: -d["manip"])

    if a.json:
        print(json.dumps(dict(median_width=w_med, candidates=cand), indent=1)); return

    print("scene median part width: %.0f mm   (accepting +-%.0f%%)"
          % (w_med*1e3, a.width_tol*100))
    if not cand:
        print("\nNO VALID CANDIDATES. Rejection reasons:")
        from collections import Counter
        for why, n in Counter(rejected.values()).most_common():
            print("   %2d x  %s" % (n, why))
        print("\nTry --relax (ignore base-pose preference), or move the object "
              "lower / closer if lift headroom is the blocker.")
        return
    print("\n  grasp   manip   width   lift_head   yaw    force     cage")
    for d in cand[:8]:
        print("   %-5s  %.3f   %.0fmm    %.3f m   %+5.1f   %-8s  %s"
              % (d["grasp"], d["manip"], d["width"]*1e3, d["headroom"],
                 d["yaw"], d["force"], d["cage"]))
    print("\nUSE N = %s   (%d of %d grasps passed)" % (cand[0]["grasp"], len(cand), len(rows)))
    if rejected:
        from collections import Counter
        print("rejected:", ", ".join("%dx %s" % (n, w.split("(")[0].strip())
                                     for w, n in Counter(rejected.values()).most_common(4)))


if __name__ == "__main__":
    main()
