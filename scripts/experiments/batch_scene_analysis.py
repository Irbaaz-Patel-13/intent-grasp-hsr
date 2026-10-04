#!/usr/bin/env python
r"""batch_scene_analysis.py -- run the FULL perception pipeline over every
captured scene and report, in one table, which stages generalise beyond the mug.

For each captures_*/cap_<name>.npz it drives the existing scripts unmodified:
    adapt_real_capture.py -> run_grounding_grasp.py -> export_grasps_plain.py
    -> grasp_close_params.py
then adds an offline geometry pass (grasp_align.pca_axes) on the object cloud to
report shape class, principal-axis extent, minor width, whether the part exceeds
the gripper aperture, and whether wrist-roll alignment would apply.

What each column tests:
    target_object / conf : does object identification work without a hint, and
                           does it discriminate in the CLUSTER scenes?
    target_part          : is part selection object-appropriate, or does the
                           'handle' prior dominate (the documented mug result)?
    keep_clear           : are functional surfaces protected (pot lid, can top)?
    width / gate         : does the width gate reject parts wider than the
                           125 mm aperture (expected: the pot body)?
    shape / roll         : does PCA classify elongated parts (spoon, remote) and
                           demand a wrist-roll correction, while leaving compact
                           parts (mug, can) alone?
    force / close_z/lift : do the constraint-derived closure parameters differ
                           across objects and tasks?

Run from workspace/ (venv python), ~2 min per scene (models reload each run):
    .\.venv\Scripts\python.exe batch_scene_analysis.py
    .\.venv\Scripts\python.exe batch_scene_analysis.py --only spoon,remote,pot
    .\.venv\Scripts\python.exe batch_scene_analysis.py --dry     # show the plan only
Outputs: batch_scene_analysis.md, batch_scene_analysis.csv, per-scene JSON.
"""
import argparse, csv, glob, json, os, shutil, subprocess, sys, time
import numpy as np

# instruction per scene: chosen so the CONSTRAINTS should differ, and so the
# cluster scenes test discrimination (naming one object among several)
DEFAULT_INSTRUCTIONS = {
    "mug":                        "pick up the mug",
    "coke_can":                   "pick up the can of coke",
    "dishwash_bottle":            "pick up the dish soap bottle",
    "metal_spoon":                "pick up the spoon",
    "TV_remote":                  "hand me the TV remote",
    "pot_with_handle_and_lid":    "pick up the pot",
    "cluster_mug_cokecan":        "pick up the mug",
    "cluster_mug_cokecan_pot":    "pick up the pot",
    "cluster_mug_remote_pot":     "hand me the TV remote",
}
APERTURE_MAX = 0.125


def run(cmd, py, timeout=600):
    """Run a pipeline script; return (ok, stdout+stderr)."""
    try:
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        p = subprocess.run([py] + cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace", env=env)
        return p.returncode == 0, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT after %ds" % timeout


def object_cloud(cloud_npz, aff, radius_xy=0.10, plane_band=0.008):
    """Points belonging to the object near the affordance centre."""
    z = np.load(cloud_npz, allow_pickle=True)
    pts = None
    for k in z.files:
        a = np.asarray(z[k])
        if a.ndim == 2 and a.shape[1] == 3 and a.shape[0] > 1000:
            pts = a.astype(float); break
    if pts is None:
        return None, None
    near = pts[np.linalg.norm(pts[:, :2] - aff[:2], axis=1) < 0.18]
    if len(near) < 200:
        return None, None
    h, e = np.histogram(near[:, 2], bins=60)
    plane_z = float(0.5 * (e[np.argmax(h)] + e[np.argmax(h) + 1]))
    obj = near[(near[:, 2] > plane_z + plane_band) &
               (np.linalg.norm(near[:, :2] - aff[:2], axis=1) < radius_xy)]
    return (obj if len(obj) > 30 else None), plane_z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="captures_0723")
    ap.add_argument("--py", default=r".venv\Scripts\python.exe")
    ap.add_argument("--only", default="", help="comma-separated substrings to include")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--keep", action="store_true",
                    help="keep per-scene fused_cloud/grasps files (default: overwritten)")
    a = ap.parse_args()

    sys.path.insert(0, os.getcwd())
    try:
        from intent_grasp.grasp_align import pca_axes, align_wrist_roll
    except ImportError:
        sys.exit("grasp_align.py not found in %s -- copy it there first" % os.getcwd())

    caps = sorted(glob.glob(os.path.join(a.dir, "cap_*.npz")))
    if a.only:
        keys = [s.strip().lower() for s in a.only.split(",")]
        caps = [c for c in caps if any(k in os.path.basename(c).lower() for k in keys)]
    if not caps:
        sys.exit("no captures matched in %s" % a.dir)

    plan = []
    for c in caps:
        name = os.path.splitext(os.path.basename(c))[0].replace("cap_", "")
        instr = DEFAULT_INSTRUCTIONS.get(name, "pick up the %s" % name.replace("_", " "))
        plan.append((c, name, instr))
    print("scenes to run (%d):" % len(plan))
    for _, n, i in plan:
        print("   %-28s <- \"%s\"" % (n, i))
    if a.dry:
        return

    rows, t_start = [], time.time()
    for idx, (cap, name, instr) in enumerate(plan, 1):
        print("\n" + "=" * 72)
        print("[%d/%d] %s   \"%s\"" % (idx, len(plan), name, instr))
        print("=" * 72)
        r = dict(scene=name, instruction=instr)
        shutil.copyfile(cap, "head_capture_real.npz")

        ok, out = run(["adapt_real_capture.py"], a.py)
        if not ok:
            r["error"] = "adapt_real_capture failed"; print(out[-800:]); rows.append(r); continue

        ok, out = run(["run_grounding_grasp.py", instr], a.py, timeout=900)
        if not ok:
            r["error"] = "grounding failed"; print(out[-1500:]); rows.append(r); continue
        for line in out.splitlines():
            if "grounded:" in line or "affordance center within" in line \
               or "Target Object:" in line or "Confidence:" in line:
                print("   " + line.strip())

        if os.path.exists("constraints.json"):
            cj = json.load(open("constraints.json", encoding="utf-8"))
            c = cj.get("constraints", {})
            r.update(target_object=cj.get("target_object", ""),
                     target_part=cj.get("target_part", ""),
                     keep_clear=";".join(c.get("keep_clear", []) or []) or "-",
                     motion=c.get("post_grasp_motion", ""),
                     stability=c.get("stability_priority", ""),
                     thermal=(c.get("thermal_or_hygiene") or "-"))

        ok, _ = run(["export_grasps_plain.py"], a.py)
        if not ok:
            r["error"] = "export failed"; rows.append(r); continue
        ok, out = run(["grasp_close_params.py"], a.py)
        if ok:
            for line in out.splitlines():
                if line.startswith("plane_z") or line.startswith("scene median") \
                   or line.startswith("[policy]"):
                    print("   " + line.strip())
            if os.path.exists("close_params.csv"):
                cp = [x for x in csv.DictReader(open("close_params.csv")) if x.get("ok") == "1"]
                if cp:
                    ws = sorted(float(x["part_width_m"]) for x in cp)
                    r.update(n_ok=len(cp), width_med=round(ws[len(ws)//2], 4),
                             force=cp[0].get("force_level", ""),
                             close_z=cp[0].get("close_z", ""),
                             lift=cp[0].get("lift_m", ""),
                             tilt=cp[0].get("requires_controlled_tilt", ""))
                else:
                    r["n_ok"] = 0
        else:
            r["error"] = "close_params failed"

        # ---- offline geometry: shape class, aperture gate, wrist-roll ----
        try:
            g = np.load("grasps_plain.npz", allow_pickle=True)
            aff = np.asarray(g["aff_center_3d"]).ravel()
            poses = np.asarray(g["poses"])
            obj, plane_z = object_cloud("fused_cloud.npz", aff)
            r["aff_z"] = round(float(aff[2]), 3)
            r["plane_z"] = round(float(plane_z), 3) if plane_z else ""
            if obj is not None:
                p = pca_axes(obj)
                r.update(shape=p["shape_class"], linearity=round(p["linearity"], 2),
                         long_mm=round(p["extent"][0] * 1e3),
                         minor_mm=round(p["minor_width"] * 1e3),
                         obj_pts=len(obj))
                r["over_aperture"] = int(p["minor_width"] + 0.02 > APERTURE_MAX)
                al = align_wrist_roll(poses[0], obj, wrist_roll_now=0.0)
                r["roll_apply"] = int(bool(al.get("apply")))
                r["roll_deg"] = al.get("misalign_deg", "")
                r["roll_reason"] = al.get("reason", "")[:60]
                print("   geometry: %s lin=%.2f long=%dmm minor=%dmm roll=%s (%s)"
                      % (r["shape"], r["linearity"], r["long_mm"], r["minor_mm"],
                         r["roll_apply"], r["roll_reason"][:40]))
        except Exception as e:
            r["geom_error"] = "%s: %s" % (type(e).__name__, e)

        if a.keep:
            os.makedirs("batch_out", exist_ok=True)
            for f in ("fused_cloud.npz", "grasps_plain.npz", "close_params.csv",
                      "constraints.json"):
                if os.path.exists(f):
                    shutil.copyfile(f, os.path.join("batch_out", "%s_%s" % (name, f)))
        rows.append(r)
        json.dump(r, open("batch_%s.json" % name, "w", encoding="utf-8"), indent=1)

    # ---------------- report ----------------
    cols = ["scene", "target_object", "target_part", "keep_clear", "motion",
            "stability", "thermal", "shape", "linearity", "long_mm", "minor_mm",
            "over_aperture", "roll_apply", "roll_deg", "n_ok", "width_med",
            "force", "close_z", "lift", "tilt", "aff_z", "plane_z", "error"]
    with open("batch_scene_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols + ["instruction", "roll_reason",
                                                 "obj_pts", "geom_error"],
                           extrasaction="ignore")
        w.writeheader()
        for r in rows: w.writerow(r)

    L = ["# Batch scene analysis — pipeline generality across captured objects", "",
         "Each row is one head-camera capture driven through the unmodified pipeline",
         "(`adapt_real_capture` → `run_grounding_grasp` → `export_grasps_plain` →",
         "`grasp_close_params`), plus an offline PCA pass on the object cloud.", "",
         "| scene | object | part | keep_clear | motion | shape | lin | long | minor | >aperture | roll | width med | force | close_z | lift |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("error"):
            L.append("| %s | **%s** | | | | | | | | | | | | | |" % (r["scene"], r["error"])); continue
        L.append("| %s | %s | %s | %s | %s | %s | %s | %smm | %smm | %s | %s (%s°) | %smm | %s | %s | %s |"
                 % (r.get("scene",""), r.get("target_object",""), r.get("target_part",""),
                    r.get("keep_clear","-"), r.get("motion",""), r.get("shape",""),
                    r.get("linearity",""), r.get("long_mm",""), r.get("minor_mm",""),
                    "YES" if r.get("over_aperture") else "-",
                    "YES" if r.get("roll_apply") else "-", r.get("roll_deg",""),
                    round(float(r["width_med"])*1e3) if r.get("width_med") else "",
                    r.get("force",""), r.get("close_z",""), r.get("lift","")))
    L += ["", "## Per-scene wrist-roll decision", ""]
    for r in rows:
        if r.get("roll_reason"):
            L.append("- **%s**: %s" % (r["scene"], r["roll_reason"]))
    open("batch_scene_analysis.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n" + "\n".join(L[:6 + len(rows)]))
    print("\nwrote batch_scene_analysis.md / .csv   (%.1f min)" % ((time.time()-t_start)/60))


if __name__ == "__main__":
    main()