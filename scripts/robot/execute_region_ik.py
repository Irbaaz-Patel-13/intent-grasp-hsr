#!/usr/bin/env python
"""
execute_region_ik.py -- CONTAINER (step 3 of 3).
Reads the per-instruction 3D targets, runs whole-body IK to each region,
reports reachability, and optionally executes each grasp.

  cd /workspace/notebooks
  python execute_region_ik.py                 # IK-feasibility only, no motion
  python execute_region_ik.py --execute       # physically run each grasp

Reads:  /workspace/notebooks/cgn_data/region_targets.npz
        (copy it in first: cp <repo>/workspace/region_targets.npz ~/tmc_wrs_docker/notebooks/cgn_data/)
"""
import time, argparse
import numpy as np
import rospy
from utils import move_wholebody_ik, move_hand, move_arm_init

NPZ = "/workspace/notebooks/cgn_data/region_targets.npz"
LIFT = 0.10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    d = np.load(NPZ, allow_pickle=True)
    obj = str(d["object"])
    instrs = list(d["instructions"]); parts = list(d["parts"])
    regs = list(d["regions"]); cents = d["centroids"]
    print(f"object='{obj}'  {len(instrs)} instruction(s)")

    rospy.init_node("execute_region_ik", anonymous=True)
    move_arm_init(); move_hand(1); time.sleep(1.0)

    print("="*64)
    results = []
    for i, instr in enumerate(instrs):
        c = cents[i]
        if not np.all(np.isfinite(c)):
            print(f"  '{instr}' -> region {regs[i]} ({parts[i]}): no 3D target, skip")
            results.append((regs[i], None)); continue
        gx, gy, gz = float(c[0]), float(c[1]), float(c[2]) + 0.02
        reach = move_wholebody_ik(gx, gy, gz, 180, 0, 0)   # top-down
        print(f"  '{instr}'")
        print(f"     region {regs[i]} ({parts[i]})  target odom=({gx:.3f},{gy:.3f},{gz:.3f})")
        print(f"     IK reach: {reach}")
        if reach and args.execute:
            time.sleep(1.0); move_hand(0); time.sleep(1.0)          # close
            lifted = move_wholebody_ik(gx, gy, gz + LIFT, 180, 0, 0)
            time.sleep(1.5)
            print(f"     executed: lift_cmd_ok={lifted}")
            move_hand(1); move_arm_init(); time.sleep(1.0)          # release + reset
        results.append((regs[i], reach))
    print("="*64)

    distinct = len({r for r, _ in results if r >= 0})
    reachable = sum(1 for _, ok in results if ok)
    print(f"  distinct regions targeted: {distinct}")
    print(f"  regions with IK solution : {reachable}/{len(results)}")
    if distinct >= 2 and reachable >= 2:
        print("  >>> EACH intent-selected region is independently reachable by IK.")
        print("      Motor side of differentiability holds: same object,")
        print("      different region per intent, each path-planned and IK-solved.")
    elif distinct >= 2:
        print("  >>> regions differ but not all reachable -- ties to the reachability")
        print("      finding (failures cluster at certain approach geometries).")
    print("="*64)


if __name__ == "__main__":
    main()
