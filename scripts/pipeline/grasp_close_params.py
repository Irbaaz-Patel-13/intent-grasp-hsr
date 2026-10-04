#!/usr/bin/env python
r"""grasp_close_params.py (v2, 21 Jul) -- PC (workspace/). Post-export step.

Per-grasp CLOSING parameters. Two sources, kept strictly separate:
  PERCEPTION (object-specific magnitudes): part_width along the grasp closing
      axis, support plane, object top -- all from the cloud, no object constants.
  INFERRED CONSTRAINTS (task-specific modulation): stability_priority,
      post_grasp_motion, thermal_or_hygiene -> force level, hold margin,
      close depth fraction, cage clearance, post-grasp plan (grasp_policy.py).

New in v2:
  * width-artifact guard: rows whose part_width deviates hard from the scene
    median are flagged ok=0 (14/16 Jul produced 15-64 mm artifact rows from
    slabs that clipped the object edge; one would have cage-closed onto the rim).
  * constraint consumption + closure policy columns.

Run after export_grasps_plain.py, with grasps_plain.npz, fused_cloud.npz,
gripper_gap_map.csv and grasp_policy.py in the same folder:
    python grasp_close_params.py
Then scp close_params.csv to the workstation next to place_run.csv.
"""
import csv, json, os, sys
import numpy as np
from intent_grasp.grasp_policy import closure_policy, explain

SLAB, ORTHO = 0.015, 0.045       # measurement slab half-extents (m)
MAXAP, MINAP = 0.125, 0.030
MED_TOL = 0.30                   # reject widths >30% from the scene median

# ---------------------------------------------------------------- constraints
def load_constraints():
    """Find the VLM constraints for THIS scene. Sources tried in order; the
    first that yields a constraints dict wins. Falls back to neutral defaults
    with a loud warning (closure then reproduces pre-policy behaviour)."""
    # 1) explicit sidecar (written by run_grounding_grasp.py if patched)
    for p in ("constraints.json", "vlm_constraints.json"):
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                c = d.get("constraints", d)
                if isinstance(c, dict) and "post_grasp_motion" in c:
                    print("[constraints] from %s" % p); return c, p
            except Exception as e:
                print("[constraints] %s unreadable: %s" % (p, e))
    # 2) inside grasps_out.npz (what run_grounding_grasp.py saves)
    if os.path.exists("grasps_out.npz"):
        try:
            z = np.load("grasps_out.npz", allow_pickle=True)
            for key in ("constraints", "vlm_constraints"):
                if key in z.files:
                    c = z[key]
                    c = c.item() if c.shape == () else c
                    if isinstance(c, dict):
                        print("[constraints] from grasps_out.npz['%s']" % key)
                        return c, "grasps_out.npz"
            print("[constraints] grasps_out.npz keys: %s" % (list(z.files),))
        except Exception as e:
            print("[constraints] grasps_out.npz unreadable: %s" % e)
    print("[constraints] !! NONE FOUND -- using neutral defaults "
          "(stability=med, motion=translate). Closure will NOT be "
          "task-differentiated this run. Patch run_grounding_grasp.py to dump "
          "constraints.json to enable it.")
    return {"keep_clear": [], "keep_clear_reasons": [],
            "post_grasp_motion": "translate", "stability_priority": "med",
            "thermal_or_hygiene": None}, "DEFAULTS"

# ---------------------------------------------------------------- inputs
g = np.load("grasps_plain.npz", allow_pickle=True)
poses = np.asarray(g["poses"])
aff = np.asarray(g["aff_center_3d"]).ravel() if "aff_center_3d" in g.files else None
print("grasps: %d   keys: %s" % (len(poses), list(g.files)))

c = np.load("fused_cloud.npz", allow_pickle=True)
pts = None
for k in c.files:
    a = np.asarray(c[k])
    if a.ndim == 2 and a.shape[1] == 3 and a.shape[0] > 1000:
        pts = a.astype(np.float64); print("cloud key '%s': %d pts" % (k, len(a))); break
assert pts is not None, "no (N,3) cloud in fused_cloud.npz; keys=%s" % (list(c.files),)

gap_map = None
if os.path.exists("gripper_gap_map.csv"):
    rows = list(csv.reader(open("gripper_gap_map.csv")))[1:]
    gap_map = [(float(r[1]), float(r[2])) for r in rows if len(r) >= 3]
    print("gap map: %d points" % len(gap_map))
else:
    print("!! gripper_gap_map.csv missing -- using the linear 64 mm/rad fit")

constraints, csrc = load_constraints()

# ---------------------------------------------------------------- scene stats
ctr = aff if aff is not None else poses[:, :3, 3].mean(0)
near = pts[np.linalg.norm(pts[:, :2] - ctr[:2], axis=1) < 0.15]
zh, ze = np.histogram(near[:, 2], bins=60)
plane_z = float(0.5 * (ze[np.argmax(zh)] + ze[np.argmax(zh) + 1]))
obj = near[(near[:, 2] > plane_z + 0.008) &
           (np.linalg.norm(near[:, :2] - ctr[:2], axis=1) < 0.08)]
obj_top = float(np.percentile(obj[:, 2], 98)) if len(obj) > 50 else float("nan")
print("plane_z=%.3f  obj_top=%.3f  obj_pts=%d" % (plane_z, obj_top, len(obj)))

# ---------------------------------------------------------------- pass 1: widths
widths = []
for T in poses:
    cpos, R = T[:3, 3], T[:3, :3]
    closing, approach = R[:, 0], R[:, 2]
    third = np.cross(approach, closing)
    t_off = float(np.dot(ctr - cpos, approach))      # CGN origin = gripper base
    d = pts - (cpos + t_off * approach)
    m = (np.abs(d @ approach) < SLAB) & (np.abs(d @ third) < ORTHO) \
        & (np.abs(d @ closing) < 0.10) & (pts[:, 2] > plane_z + 0.008)
    sel = d[m] @ closing
    widths.append((float(np.percentile(sel, 98) - np.percentile(sel, 2))
                   if len(sel) >= 60 else float("nan"), t_off, len(sel)))
finite = [w for w, _, _ in widths if np.isfinite(w)]
w_med = float(np.median(finite)) if finite else float("nan")
print("scene median part_width = %.4f m  (artifact guard: reject >%.0f%% deviation)"
      % (w_med, MED_TOL * 100))

# ---------------------------------------------------------------- pass 2: policy
pol_ref = closure_policy(constraints, part_width_m=w_med if finite else None,
                         plane_z=plane_z, obj_top_z=obj_top, gap_map=gap_map)
print("[policy] %s" % explain(constraints, pol_ref))

out = []
for i, (w, t_off, n) in enumerate(widths):
    ok, note = 1, ""
    if not np.isfinite(w):
        ok, note = 0, "too few pts (%d)" % n
        p = {}
    else:
        if np.isfinite(w_med) and w_med > 0 and abs(w - w_med) / w_med > MED_TOL:
            ok, note = 0, "WIDTH ARTIFACT: %.0fmm vs scene median %.0fmm" % (w*1e3, w_med*1e3)
        p = closure_policy(constraints, part_width_m=w, plane_z=plane_z,
                           obj_top_z=obj_top, gap_map=gap_map)
        if not p.get("width_gate_ok", 1):
            ok, note = 0, (note + " WIDTH GATE: exceeds aperture").strip()
        if "close_z" not in p:
            ok, note = 0, (note + " object too short/absent for close_z").strip()
    f = lambda v, d=4: (round(v, d) if isinstance(v, float) and np.isfinite(v) else "")
    out.append([i, f(w), f(p.get("cage_gap_m", float("nan"))),
                f(p.get("cage_motor_rad", float("nan")), 3),
                f(p.get("close_z", float("nan"))), round(plane_z, 4), f(obj_top),
                p.get("force_level", ""), p.get("effort", ""),
                p.get("hold_margin_rad", ""), p.get("lift_m", ""),
                int(bool(p.get("requires_controlled_tilt", 0))),
                p.get("retreat", ""), ok, note])
    print("g%-3d w=%-7s cage=%-7s motor=%-6s close_z=%-7s force=%-8s ok=%d %s"
          % (i, out[-1][1], out[-1][2], out[-1][3], out[-1][4], out[-1][7], ok, note))

with open("close_params.csv", "w", newline="") as fh:
    w_ = csv.writer(fh)
    w_.writerow(["grasp_id", "part_width_m", "cage_gap_m", "cage_motor_rad",
                 "close_z", "plane_z", "obj_top_z", "force_level", "effort",
                 "hold_margin_rad", "lift_m", "requires_controlled_tilt",
                 "retreat", "ok", "note"])
    w_.writerows(out)
n_ok = sum(1 for r in out if r[-2] == 1)
print("\nwrote close_params.csv  (%d/%d ok)   constraints source: %s"
      % (n_ok, len(out), csrc))
print("scp close_params.csv to the workstation alongside place_run.csv")
