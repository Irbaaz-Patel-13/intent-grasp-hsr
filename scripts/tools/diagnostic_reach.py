"""
Diagnostic script: HSR kinematic reach investigation.
Loads the HSR via the existing SimulationEnvironment (no objects spawned),
then sweeps individual arm joints, queries IK for several target positions,
and writes results to results/REACH_DIAGNOSIS_V3.md.

DO NOT modify pipeline files — this script is read-only w.r.t. the pipeline.
"""

import os
import sys
import io
import math
import numpy as np
import pybullet as p

# Ensure imports find the project root
from intent_grasp.config import SimulationConfig
from intent_grasp.sim_env import SimulationEnvironment

# ── Output helper ─────────────────────────────────────────────────────────────

_lines: list[str] = []

def _p(*args, **kwargs):
    line = " ".join(str(a) for a in args)
    print(line, **kwargs)
    _lines.append(line)

# ── Setup ─────────────────────────────────────────────────────────────────────

_p("=== REACH DIAGNOSIS V3: HSR kinematic workspace ===")
_p("")

config = SimulationConfig()
sim = SimulationEnvironment(config, gui=False)
sim.setup()

robot_id = sim.robot_id
ee_link  = sim.ee_link_index
arm_idxs = sim.arm_joint_indices        # [23, 24, 25, 26, 27]
dof_of   = sim._dof_index_of            # {abs_joint -> dof_pos}
ik_lower = sim._ik_lower
ik_upper = sim._ik_upper
ik_ranges= sim._ik_ranges
ik_rest  = sim._ik_rest
j2idx    = sim.joint_name_to_idx
n_joints = p.getNumJoints(robot_id)

# ── Step 2: loadURDF parameters ───────────────────────────────────────────────

_p("## 1. Robot Loading")
_p(f"  URDF: {config.hsr_urdf}")
_p(f"  useFixedBase = True  (hardcoded in _load_hsr; robot base is pinned to world)")
_p(f"  robot_base_position = {config.robot_base_position}")
_p(f"  robot_base_orientation = {config.robot_base_orientation}")
_p(f"  Total joints: {n_joints}")
_p(f"  Controllable DoF (non-FIXED joints): {len(dof_of)}")
_p(f"  EE link index: {ee_link}")
_p("")

# ── Step 3: Joint info ────────────────────────────────────────────────────────

JTYPE = {
    p.JOINT_REVOLUTE:  "REVOLUTE",
    p.JOINT_PRISMATIC: "PRISMATIC",
    p.JOINT_FIXED:     "FIXED",
    p.JOINT_SPHERICAL: "SPHERICAL",
    p.JOINT_PLANAR:    "PLANAR",
}

def joint_row(j):
    info = p.getJointInfo(robot_id, j)
    name = info[1].decode()
    jtype = JTYPE.get(info[2], str(info[2]))
    lo, hi = info[8], info[9]
    in_dof = j in dof_of
    dof_pos = dof_of.get(j, "N/A")
    return (j, name, jtype, lo, hi, in_dof, dof_pos)

_p("## 2. Arm Joint Info")
_p(f"  {'idx':>4}  {'name':<30}  {'type':<10}  {'lower':>8}  {'upper':>8}  {'controllable':>12}  {'DoF pos':>7}")
for j in arm_idxs:
    row = joint_row(j)
    _p(f"  {row[0]:>4}  {row[1]:<30}  {row[2]:<10}  {row[3]:>8.4f}  {row[4]:>8.4f}  {str(row[5]):>12}  {str(row[6]):>7}")

_p("")
_p("## 3. Base and Wheel Joint Info")
_p(f"  {'idx':>4}  {'name':<35}  {'type':<10}  {'lower':>8}  {'upper':>8}  {'controllable':>12}  {'DoF pos':>7}")
for j in range(n_joints):
    info = p.getJointInfo(robot_id, j)
    name = info[1].decode()
    if "base" in name.lower() or "wheel" in name.lower():
        row = joint_row(j)
        _p(f"  {row[0]:>4}  {row[1]:<35}  {row[2]:<10}  {row[3]:>8.4f}  {row[4]:>8.4f}  {str(row[5]):>12}  {str(row[6]):>7}")

_p("")

# ── Current EE pose ───────────────────────────────────────────────────────────

ee_state0 = p.getLinkState(robot_id, ee_link)
ee_pos0 = np.array(ee_state0[4])
_p(f"## 4. EE Position at Home Pose: {ee_pos0.round(4).tolist()}")
_p("")

# Helper: save / restore ALL joint states

def save_joint_states():
    return [p.getJointState(robot_id, j)[0] for j in range(n_joints)]

def restore_joint_states(saved):
    for j, q in enumerate(saved):
        p.resetJointState(robot_id, j, q)

# ── Step 4: Single-joint sweeps ───────────────────────────────────────────────

_p("## 5. Single-Joint Sweeps (11 steps, reset-only -- no physics)")
_p("   Reports (joint_angle, EE_x, EE_y, EE_z) per step.")
_p("")

sweep_joints = arm_idxs[:]  # [23, 24, 25, 26, 27]
# Also add torso_lift
torso_lift_idx = sim.torso_lift_joint_idx
if torso_lift_idx is not None:
    sweep_joints = list(sweep_joints) + [torso_lift_idx]

global_max_y = -np.inf
global_min_y = +np.inf
limit_hits = []

for j in sweep_joints:
    info = p.getJointInfo(robot_id, j)
    jname = info[1].decode()
    lo = info[8]
    hi = info[9]
    if lo >= hi:
        lo, hi = -0.01, 0.01    # effectively fixed
    saved = save_joint_states()
    _p(f"  Joint {j} '{jname}'  range=[{lo:.4f}, {hi:.4f}]")
    step_vals = np.linspace(lo, hi, 11)
    ys = []
    for angle in step_vals:
        p.resetJointState(robot_id, j, angle)
        ee = np.array(p.getLinkState(robot_id, ee_link)[4])
        ys.append(ee[1])
        _p(f"    angle={angle:7.4f}  EE=[{ee[0]:.4f}, {ee[1]:.4f}, {ee[2]:.4f}]")
    restore_joint_states(saved)
    jmin_y = min(ys)
    jmax_y = max(ys)
    if jmin_y < global_min_y:
        global_min_y = jmin_y
    if jmax_y > global_max_y:
        global_max_y = jmax_y
    if lo == -0.01:
        limit_hits.append(f"J{j} '{jname}': effectively fixed (lo>=hi)")
    _p(f"  -> EE y range for this joint: [{jmin_y:.4f}, {jmax_y:.4f}]")
    _p("")

_p(f"  GLOBAL max EE y from single-joint sweeps: {global_max_y:.4f} m")
_p(f"  GLOBAL min EE y from single-joint sweeps: {global_min_y:.4f} m")
_p("")

# ── Step 5: IK queries for a grid of target y values ─────────────────────────

_p("## 6. IK Residual Grid -- target positions along y-axis")
_p("   Orientation: gripper pointing down (Euler [pi, 0, 0]).")
_p("   IK seeded from static home rest pose (no chain seeding).")
_p("")

down_quat = p.getQuaternionFromEuler([math.pi, 0.0, 0.0])

targets = [
    [0.5,  +0.3, 0.2],
    [0.5,  +0.0, 0.2],
    [0.5,  -0.1, 0.2],
    [0.5,  -0.2, 0.2],
    [0.5,  -0.3, 0.2],
]

reachable = []
unreachable = []

# Change 1: print IK call signature once (arrays are identical for all targets)
print(f"[IK CALL] lowerLimits.length={len(ik_lower)}")
print(f"[IK CALL] upperLimits.length={len(ik_upper)}")
print(f"[IK CALL] jointRanges.length={len(ik_ranges)}")
print(f"[IK CALL] restPoses.length={len(ik_rest)}")
print(f"[IK CALL] restPoses (first 20)={[round(v,4) for v in ik_rest[:20]]}")
print(f"[IK CALL] ee_link_index={ee_link}")
print(f"[IK CALL] target_orn (down_quat)={[round(v,6) for v in down_quat]}")
print(f"[IK CALL] maxNumIterations=200")
print(f"[IK CALL] residualThreshold=1e-5")
print()

ARM_DOF_POSITIONS = [12, 13, 14, 15, 16]
ARM_DOF_NAMES     = ['arm_lift', 'arm_flex', 'arm_roll', 'wrist_flex', 'wrist_roll']

for tgt in targets:
    saved = save_joint_states()

    print(f"[IK CALL] target_pos={tgt}")

    ik_result = p.calculateInverseKinematics(
        robot_id, ee_link,
        tgt, down_quat,
        lowerLimits=ik_lower,
        upperLimits=ik_upper,
        jointRanges=ik_ranges,
        restPoses=ik_rest,
        maxNumIterations=200,
        residualThreshold=1e-5,
    )

    # Change 2: print raw IK result
    print(f"[IK RESULT] length={len(ik_result)}")
    print(f"[IK RESULT] full={[round(v,4) for v in ik_result]}")
    for name, dof in zip(ARM_DOF_NAMES, ARM_DOF_POSITIONS):
        if dof < len(ik_result):
            print(f"[IK RESULT] {name} (DoF {dof}) = {ik_result[dof]:.4f}")
    print()

    # Apply IK solution using DoF-correct mapping (same logic as pipeline)
    for j_idx in arm_idxs:
        dof_pos = dof_of.get(j_idx)
        if dof_pos is not None and dof_pos < len(ik_result):
            p.resetJointState(robot_id, j_idx, ik_result[dof_pos])

    ee_fk = np.array(p.getLinkState(robot_id, ee_link)[4])
    residual = float(np.linalg.norm(ee_fk - np.array(tgt)))

    restore_joint_states(saved)

    tag = "REACHABLE (<1cm)" if residual < 0.01 else ("CLOSE (1-5cm)" if residual < 0.05 else "UNREACHABLE (>5cm)")
    _p(f"  target={[round(v,2) for v in tgt]}  FK={ee_fk.round(4).tolist()}  residual={residual:.4f} m  {tag}")
    if residual < 0.01:
        reachable.append(tgt)
    else:
        unreachable.append(tgt)

_p("")

# ── Change 3: Position-only IK control test ───────────────────────────────────

_p("## 6b. Position-Only IK Control Test (no orientation constraint)")
_p("   Same targets, no targetOrientation passed to calculateInverseKinematics.")
_p("")

print("\n=== POSITION-ONLY IK CONTROL TEST ===")

for y_test in [+0.30, 0.00, -0.10, -0.20, -0.30]:
    target_pos_only = [0.5, y_test, 0.2]
    saved = save_joint_states()

    ik_result_no_orn = p.calculateInverseKinematics(
        robot_id, ee_link,
        target_pos_only,
        # NO targetOrientation
        lowerLimits=ik_lower,
        upperLimits=ik_upper,
        jointRanges=ik_ranges,
        restPoses=ik_rest,
        maxNumIterations=200,
        residualThreshold=1e-5,
    )

    arm_roll_val = ik_result_no_orn[14] if 14 < len(ik_result_no_orn) else float('nan')

    # Apply only arm joints
    for j_idx in arm_idxs:
        dof = dof_of.get(j_idx)
        if dof is not None and dof < len(ik_result_no_orn):
            p.resetJointState(robot_id, j_idx, ik_result_no_orn[dof])

    ee_state = p.getLinkState(robot_id, ee_link)
    fk_pos = np.array(ee_state[4])
    residual_no_orn = float(np.linalg.norm(fk_pos - np.array(target_pos_only)))

    restore_joint_states(saved)

    msg = (f"  target y={y_test:+.2f}  FK=[{fk_pos[0]:.4f},{fk_pos[1]:.4f},{fk_pos[2]:.4f}]  "
           f"residual={residual_no_orn:.4f}  arm_roll={arm_roll_val:.4f}")
    print(msg)
    _p(msg)

_p("")

# ── Change 4: Direct joint-space control test ─────────────────────────────────

_p("## 6c. Direct Joint-Space Control (no IK -- confirms physical reach)")
_p("   Sets arm_roll_joint manually to known values from the joint sweep.")
_p("")

print("\n=== DIRECT JOINT-SPACE CONTROL ===")

# Save current state
saved_global = save_joint_states()

# arm_roll = -0.311 -> from sweep: EE y ~ +0.035 (close to 0.00)
p.resetJointState(robot_id, 25, -0.311)
ee_state = p.getLinkState(robot_id, ee_link)
msg1 = f"  arm_roll=-0.311 manually  -> EE = {[round(v,4) for v in ee_state[4]]}"
print(msg1)
_p(msg1)

# arm_roll = -1.497 -> from sweep: EE y ~ -0.063 (global minimum)
p.resetJointState(robot_id, 25, -1.497)
ee_state = p.getLinkState(robot_id, ee_link)
msg2 = f"  arm_roll=-1.497 manually  -> EE = {[round(v,4) for v in ee_state[4]]}"
print(msg2)
_p(msg2)

# arm_roll = +1.468 -> from sweep: EE y ~ +0.218 (global maximum)
p.resetJointState(robot_id, 25, 1.468)
ee_state = p.getLinkState(robot_id, ee_link)
msg3 = f"  arm_roll=+1.468 manually  -> EE = {[round(v,4) for v in ee_state[4]]}"
print(msg3)
_p(msg3)

# Reset
restore_joint_states(saved_global)

_p("")

# ── Step 6: Summary ───────────────────────────────────────────────────────────

_p("## 7. Summary")
_p("")
_p(f"  Max EE y (single-joint sweeps): {global_max_y:.4f} m")
_p(f"  Min EE y (single-joint sweeps): {global_min_y:.4f} m")
_p("")
_p(f"  IK residual < 1 cm (reachable):  {[str([round(v,2) for v in t]) for t in reachable]}")
_p(f"  IK residual > 1 cm (unreachable): {[str([round(v,2) for v in t]) for t in unreachable]}")
_p("")
if limit_hits:
    _p(f"  Effectively-fixed joints (lo>=hi): {limit_hits}")
else:
    _p("  No effectively-fixed joints in sweep set.")
_p("")
_p("  Interpretation:")
if global_min_y > -0.05:
    _p("  *** The HSR EE CANNOT reach negative y from any single-joint adjustment.")
    _p(f"  *** Min EE y achieved by any single arm joint sweep: {global_min_y:.4f} m")
    _p("  *** This confirms target y=-0.31 m is kinematically unreachable from the home pose.")
elif global_min_y < -0.25:
    _p(f"  *** The HSR CAN reach y={global_min_y:.3f} m in single-joint sweeps.")
    _p("  *** IK failure is NOT a workspace limit -- it is an IK seeding / solver issue.")
else:
    _p(f"  *** The HSR reaches y as low as {global_min_y:.4f} m in single-joint sweeps.")
    _p("  *** Target y=-0.31 m may be at or beyond the kinematic limit for combined joints.")

_p("")
_p("=== END OF REACH DIAGNOSIS V3 ===")

# ── Write report ──────────────────────────────────────────────────────────────

os.makedirs("results", exist_ok=True)
report_path = "results/REACH_DIAGNOSIS_V3.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# HSR Kinematic Reach Diagnosis V3\n\n")
    f.write("**Date:** 2026-05-16  \n")
    f.write("**Script:** `diagnostic_reach.py` (read-only; no pipeline changes)  \n\n")
    f.write("```\n")
    f.write("\n".join(_lines))
    f.write("\n```\n")

print(f"\n[Reach] Report written to {report_path}")

p.disconnect()
