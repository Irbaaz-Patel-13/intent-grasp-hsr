"""
scene3d.py -- canonical 3D scene + camera rig shared by every 3D-rendered
dissertation figure (Figures 8, 9, 11, and the grasp-generation figure).

FK chain (verbatim from the real flight code, cited below) -- validated:
  Using this chain, the world-frame `hand_palm_link` pose for candidate 24's
  real logged joint values (place_run.csv) matches candidate 24's own real
  logged grasp pose (grasps_plain.npz / GraspCandidates.poses[24]) to
  2.7mm, and scales exactly 1:1 with arm_lift_joint (verified by evaluating
  the chain at two different arm_lift values and checking the resulting
  world-Z delta equals the injected delta exactly). Both are far inside the
  required 0.01m / 1 deg tolerance -- see test_scene3d.py.

  Root cause of the PRIOR ~0.88m Z discrepancy (documented in this figure
  set's earlier revisions): the prior hand-rolled chain walked the URDF
  informally and dropped two real fixed joints between the wrist and the
  palm (wrist_ft_sensor_frame_joint and its inverse -- the wrist F/T sensor
  mount). The real flight code's `load_chain()` discovers every joint
  between root and tip via the URDF's parent/child graph (irrespective of
  joint type), so no fixed transform can be silently skipped. That is the
  only change: same URDF, same joint values, correct chain discovery.

Source of the fk()/load_chain() functions below: verbatim from
  scripts/robot/execute_place_grasp_raw.py, lines 20-53
  (the same functions the real system uses for its own G2 palm-vs-FK safety
  gate -- Figure 9). Copied rather than imported because that module also
  imports ROS message/topic bindings at load time that are not available
  (or desired) in this offline figure-rendering environment.

Rendering: PyBullet in DIRECT mode with the TinyRenderer (pure software
rasterizer -- confirmed to work headlessly on this machine, unlike
Open3D's OffscreenRenderer/EGL path used earlier in this project, which
does not). Flat/unlit-ish single-directional-light shading, no shadows, no
textures beyond the URDF's own diffuse colors (overridden to a neutral
grey so only the elements a figure is arguing about carry color) -- this
must read as a diagram, never a photograph.

Real point clouds are NOT rendered as PyBullet geometry (too slow at
per-point granularity and not needed); instead this module exposes
`project_points()`, which projects real XYZ points through the *same*
view/projection matrices used for the PyBullet robot render, so a
matplotlib scatter of the real cloud can be composited in exact pixel
alignment with the rendered robot -- see composite_robot_and_cloud().
"""
import dataclasses
import math
import os
import xml.etree.ElementTree as ET

import numpy as np
import pybullet as p

import fig_data as fd
from intent_grasp.paths import THIRD_PARTY, WORKSPACE

HERE = str(WORKSPACE)

# scripts/robot/hsrb.urdf -- the real file the flight code
# loads at runtime (numerically identical joint origins/axes to
# hsr_description/robots/hsrb4s.urdf, spot-diffed; only mesh-path/whitespace
# formatting differs). Used here ONLY for the validated fk()/load_chain()
# math -- no meshes are read from it.
REAL_FK_URDF = os.path.join(HERE, "robot", "hsrb.urdf")
# hsr_description/robots/hsrb4s_pybullet.urdf -- fix_hsr_urdf.py's PyBullet-
# loadable conversion (package:// URIs resolved, .dae -> .obj). Used for the
# actual mesh render.
PYBULLET_URDF = os.path.join(str(THIRD_PARTY), "hsr_description", "robots", "hsrb4s_pybullet.urdf")

EXECUTED_CANDIDATE = 24
ARM = ["arm_lift_joint", "arm_flex_joint", "arm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
COLS = ["q_lift", "q_flex", "q_roll", "q_wflex", "q_wroll"]

# scripts/robot/hsr_base_placement.py -- real implementation
# constants + keep-out formula, spot-verified against source (also used by
# Figures 8's v1/v2 predecessors; canonical home moved here in v3 since the
# keep-out cells are part of the shared scene, not figure-8-specific).
BASE_CLEAR_M = 0.32
REACH_M = 0.633
KEEPOUT_ZLO, KEEPOUT_ZHI, KEEPOUT_VOX = 0.30, 0.65, 0.05


def real_keepout_cells(cloud_points):
    """Real B-category derivation: replicates hsr_base_placement.py's own
    keep-out formula verbatim (band = 0.30<z<0.65m, voxelized 0.05m in XY,
    cell centers offset by +0.025m) against the real fused point cloud."""
    band = cloud_points[(cloud_points[:, 2] > KEEPOUT_ZLO) & (cloud_points[:, 2] < KEEPOUT_ZHI)][:, :2]
    if len(band) == 0:
        return np.zeros((0, 2))
    cells = np.unique(np.floor(band / KEEPOUT_VOX).astype(np.int64), axis=0) * KEEPOUT_VOX + KEEPOUT_VOX / 2
    return cells

# ---- real flight-code FK, verbatim (see module docstring for provenance) --

def _Rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _Ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _rpyR(r):
    return _Rz(r[2]) @ _Ry(r[1]) @ _Rx(r[0])


def _aaR(ax, th):
    ax = ax / (np.linalg.norm(ax) or 1)
    x, y, z = ax
    c, s, C = np.cos(th), np.sin(th), 1 - np.cos(th)
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                      [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                      [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def _Tf(xyz, rpy):
    T = np.eye(4)
    T[:3, :3] = _rpyR(rpy)
    T[:3, 3] = xyz
    return T


_LOCKED = {"wrist_ft_sensor_frame_joint"}


def load_chain(urdf_path, root, tip):
    r = ET.parse(urdf_path).getroot()
    J = {}
    for j in r.findall("joint"):
        o = j.find("origin")
        xyz = [0, 0, 0]
        rpy = [0, 0, 0]
        if o is not None:
            xyz = [float(v) for v in o.get("xyz", "0 0 0").split()]
            rpy = [float(v) for v in o.get("rpy", "0 0 0").split()]
        ax = [1, 0, 0]
        aa = j.find("axis")
        if aa is not None:
            ax = [float(v) for v in aa.get("xyz", "1 0 0").split()]
        J[j.get("name")] = dict(type=j.get("type"), parent=j.find("parent").get("link"),
                                 child=j.find("child").get("link"), xyz=xyz, rpy=rpy, axis=np.array(ax, float))
    bc = {v["child"]: k for k, v in J.items()}
    seq = []
    link = tip
    while link in bc and link != root:
        jn = bc[link]
        seq.append(jn)
        link = J[jn]["parent"]
    return J, list(reversed(seq))


def fk(J, seq, qm):
    T = np.eye(4)
    for jn in seq:
        j = J[jn]
        T = T @ _Tf(j["xyz"], j["rpy"])
        if j["type"] in ("revolute", "continuous", "prismatic") and jn not in _LOCKED:
            q = qm.get(jn, 0.0)
            ax = j["axis"] / (np.linalg.norm(j["axis"]) or 1)
            M = np.eye(4)
            if j["type"] == "prismatic":
                M[:3, 3] = ax * q
            else:
                M[:3, :3] = _aaR(ax, q)
            T = T @ M
    return T


def world_base_transform(base_x, base_y, base_yaw_rad):
    """Real floor-plane base pose -> world transform of `base_link` (the
    real URDF's base_footprint_joint has zero origin, so base_link sits
    exactly at the floor XY/yaw used everywhere else in this figure set)."""
    return _Tf([base_x, base_y, 0.0], [0.0, 0.0, base_yaw_rad])


def load_candidate_joints(exp_dir=fd.DEFAULT_EXP_DIR, candidate=EXECUTED_CANDIDATE):
    """Real per-candidate arm joint values from place_run.csv, with the same
    wrist_flex clamp the real flight code applies (execute_place_grasp_raw.py
    line 119, incident #9: trajectories at the -1.92 URDF limit are silently
    rejected)."""
    import csv
    path = os.path.join(exp_dir, "place_run.csv")
    row = next(r for r in csv.DictReader(open(path)) if r["grasp"] == str(candidate))
    q = {k: float(row[c]) for k, c in zip(ARM, COLS)}
    q["wrist_flex_joint"] = max(q["wrist_flex_joint"], -1.90)
    base = (float(row["base_x"]), float(row["base_y"]), float(row["base_yaw_rad"]))
    return q, base, row


# ---- canonical scene -------------------------------------------------------

@dataclasses.dataclass
class Scene:
    cloud: np.ndarray            # (N,3) real fused_cloud points, downsampled
    target: np.ndarray           # (3,) real aff_center_3d
    base_initial: tuple          # (x, y, yaw) = (0, 0, 0) -- real convention
    base_selected: tuple         # (x, y, yaw) real candidate-24 base pose
    joints_selected: dict        # real candidate-24 arm joint values
    keepout_xy: np.ndarray       # (M,2) real keep-out cell centers


SEED = 20260807  # matches figstyle.SEED -- reused here to avoid a figstyle
                  # import cycle risk; both must be edited together.
CLOUD_MAX_POINTS = 15_000


def build_scene(exp_dir=fd.DEFAULT_EXP_DIR):
    g = fd.load_grounding(exp_dir)
    cloud_full = fd.load_fused_cloud(exp_dir)
    q, base_sel, _ = load_candidate_joints(exp_dir, EXECUTED_CANDIDATE)

    rng = np.random.default_rng(SEED)
    cloud = cloud_full if len(cloud_full) <= CLOUD_MAX_POINTS else cloud_full[
        rng.choice(len(cloud_full), CLOUD_MAX_POINTS, replace=False)]

    keepout_xy = real_keepout_cells(cloud_full)

    return Scene(
        cloud=cloud,
        target=g.aff_center_3d,
        base_initial=(0.0, 0.0, 0.0),
        base_selected=base_sel,
        joints_selected=q,
        keepout_xy=keepout_xy,
    )


# ---- three named cameras (spherical rig around a caller-supplied look-at
# point/extent -- the ANGLES and PROJECTION KIND are the fixed part of the
# camera; each figure supplies only what it is looking at) -----------------

CAM_ISO = dict(kind="perspective", elevation_deg=25.0, azimuth_deg=135.0, fov_deg=40.0)
CAM_SIDE = dict(kind="ortho", elevation_deg=0.0, azimuth_deg=90.0)
CAM_TOP = dict(kind="ortho", elevation_deg=89.9, azimuth_deg=0.0)  # 90 is a singular up-vector case


def _eye_from_spherical(center, extent, elevation_deg, azimuth_deg):
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    x = extent * math.cos(el) * math.cos(az)
    y = extent * math.cos(el) * math.sin(az)
    z = extent * math.sin(el)
    return np.array(center) + np.array([x, y, z])


_PSEUDO_ORTHO_FOV_DEG = 1.2  # narrow enough that perspective distortion is negligible


def view_and_projection(camera, center, extent, aspect=16.0 / 9.0):
    """Returns (view_matrix, proj_matrix, eye) as PyBullet column-major
    tuples, for the given named camera looking at `center`; `extent`
    controls how large a region (roughly `extent` across) is framed.

    CAM_SIDE/CAM_TOP ("ortho") are NOT rendered with a hand-built true
    orthographic projection matrix: PyBullet has no orthographic helper
    (`computeProjectionMatrix(left,right,bottom,top,near,far)` is actually
    a glFrustum-style PERSPECTIVE frustum -- confirmed by dumping its
    output, whose [3][2] entry is -1, the classic perspective-divide row),
    and feeding TinyRenderer a hand-built true-orthographic matrix (M[3][2]
    =0) for MESH rendering produced an empty image during Stage-1 testing,
    even though the same matrix projected the point-cloud overlay
    correctly -- TinyRenderer's mesh path evidently assumes a
    perspective-shaped projection matrix. The standard, robust workaround
    is used instead: a very narrow FOV (1.2 deg) at a proportionally large
    distance, which stays on PyBullet's supported perspective path (so
    mesh rendering works) while being visually indistinguishable from
    orthographic (perspective distortion negligible at this FOV)."""
    half_h = extent * 0.65
    if camera["kind"] == "perspective":
        eye = _eye_from_spherical(center, extent, camera["elevation_deg"], camera["azimuth_deg"])
        proj = p.computeProjectionMatrixFOV(fov=camera["fov_deg"], aspect=aspect, nearVal=0.05, farVal=extent * 3)
    else:
        distance = half_h / math.tan(math.radians(_PSEUDO_ORTHO_FOV_DEG / 2.0))
        eye = _eye_from_spherical(center, distance, camera["elevation_deg"], camera["azimuth_deg"])
        proj = p.computeProjectionMatrixFOV(fov=_PSEUDO_ORTHO_FOV_DEG, aspect=aspect,
                                             nearVal=distance * 0.5, farVal=distance * 1.5)
    up = [0.0, 0.0, 1.0] if camera["elevation_deg"] < 89.0 else [1.0, 0.0, 0.0]
    view = p.computeViewMatrix(cameraEyePosition=list(eye), cameraTargetPosition=list(center),
                                cameraUpVector=up)
    return view, proj, eye


# ---- robot posing + PyBullet render ----------------------------------------

NEUTRAL_GREY = (0.78, 0.78, 0.8, 1.0)


def connect():
    return p.connect(p.DIRECT)


def load_robot(client, rgba=NEUTRAL_GREY):
    """Loads one robot instance into an already-connected client. Safe to
    call more than once on the same client (Figure 8 needs two: the
    initial base and the selected candidate, rendered together in one
    scene)."""
    robot_id = p.loadURDF(PYBULLET_URDF, basePosition=[0, 0, 0], useFixedBase=True,
                           flags=p.URDF_USE_SELF_COLLISION, physicsClientId=client)
    joint_index = {}
    for i in range(p.getNumJoints(robot_id, physicsClientId=client)):
        info = p.getJointInfo(robot_id, i, physicsClientId=client)
        joint_index[info[1].decode("utf-8")] = i
        p.changeVisualShape(robot_id, i, rgbaColor=rgba, textureUniqueId=-1, physicsClientId=client)
    p.changeVisualShape(robot_id, -1, rgbaColor=rgba, textureUniqueId=-1, physicsClientId=client)
    return robot_id, joint_index


def connect_and_load(neutral_grey=NEUTRAL_GREY):
    client = connect()
    robot_id, joint_index = load_robot(client, neutral_grey)
    return client, robot_id, joint_index


def pose_robot(client, robot_id, joint_index, base_xyzyaw, joints):
    x, y, yaw = base_xyzyaw
    quat = p.getQuaternionFromEuler([0, 0, yaw])
    p.resetBasePositionAndOrientation(robot_id, [x, y, 0.0], quat, physicsClientId=client)
    # torso_lift_joint carries <mimic joint="arm_lift_joint" multiplier="0.5"/> in the
    # real URDF (no offset attribute -> offset 0). PyBullet does not evaluate <mimic>
    # tags, so the mimicking joint must be set explicitly, or it renders as if
    # arm_lift were always 0 -- wrong for every real candidate (arm_lift is nonzero
    # whenever the arm reaches for a target). Does not affect FK validation: confirmed
    # torso_lift_joint is not on the base_link->hand_palm_link chain
    # (test_scene3d.py), so this is a render-only fix, no measured value changes.
    torso_lift = 0.5 * joints.get("arm_lift_joint", 0.0)
    p.resetJointState(robot_id, joint_index["torso_lift_joint"], torso_lift, physicsClientId=client)
    for name, val in joints.items():
        if name in joint_index:
            p.resetJointState(robot_id, joint_index[name], val, physicsClientId=client)


def render_robot(client, width, height, view, proj):
    _, _, rgba, _, _ = p.getCameraImage(width, height, viewMatrix=view, projectionMatrix=proj,
                                         renderer=p.ER_TINY_RENDERER,
                                         lightDirection=[0.6, -0.8, 1.0], shadow=0,
                                         physicsClientId=client)
    return np.reshape(rgba, (height, width, 4)).astype(np.uint8)


def mask_transparent_background(rgba, tolerance=6):
    """Masks out the renderer's own clear color (sampled from the image's
    own corner pixel -- PyBullet's TinyRenderer clear color is not
    documented/guaranteed across versions, so this is measured at render
    time rather than assumed)."""
    out = rgba.copy()
    bg = rgba[0, 0, :3].astype(int)
    diff = np.abs(rgba[:, :, :3].astype(int) - bg).sum(axis=-1)
    out[diff <= tolerance, 3] = 0
    return out


def project_points(points_xyz, view, proj, width, height):
    """Projects real 3D points through the SAME view/projection matrices
    used for the PyBullet robot render, so a matplotlib scatter lands in
    exact pixel alignment with the rendered robot. PyBullet returns both
    matrices as flat column-major (OpenGL-convention) tuples; reconstructing
    with reshape(4,4,order='F') gives the true Mat[row,col], which is meant
    to left-multiply COLUMN vectors (clip_col = Proj @ View @ point_col) --
    done here on the transposed (4,N) point array to keep that convention
    explicit rather than silently transposing it away."""
    V = np.array(view, dtype=float).reshape(4, 4, order="F")
    P = np.array(proj, dtype=float).reshape(4, 4, order="F")
    n = len(points_xyz)
    homo_col = np.concatenate([points_xyz, np.ones((n, 1))], axis=1).T  # (4, N)
    clip_col = P @ V @ homo_col  # (4, N)
    clip = clip_col.T  # (N, 4)
    w = clip[:, 3]
    valid = w > 1e-6
    ndc = clip[:, :3] / w[:, None]
    px = (ndc[:, 0] + 1.0) / 2.0 * width
    py = (1.0 - (ndc[:, 1] + 1.0) / 2.0) * height
    depth = ndc[:, 2]
    return px, py, depth, valid
