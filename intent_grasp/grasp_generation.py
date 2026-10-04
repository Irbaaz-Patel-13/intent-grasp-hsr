"""
Task-Oriented Grasp Generation Module
======================================
Generates 6-DoF grasp poses within the affordance region identified by the
visual grounding module.

Primary method: Contact-GraspNet (PyTorch port by elchun) — open-source 6-DoF
grasp detection from depth/point cloud input, no license required.
Fallback: Antipodal grasp sampling on the point cloud.

The key AffordGrasp insight is the ranking formula:
    ranking(g) = score(g) / ||t(g) - c||₂
where t(g) is the grasp translation, c is the 3D affordance centre, and
score(g) is the grasp confidence. This naturally biases selection toward
high-quality grasps near the task-relevant part.

Reference: AffordGrasp, Section III-C: Task-Oriented Grasp Generation
"""

import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from scipy.spatial.transform import Rotation

from intent_grasp.config import GraspConfig
from intent_grasp import diag_log as _diag
@dataclass
class GraspPose:
    """A 6-DoF grasp pose with quality metrics."""
    position: np.ndarray        # (3,) grasp centre position in world frame
    orientation: np.ndarray     # (4,) quaternion (x, y, z, w)
    rotation_matrix: np.ndarray # (3, 3) rotation matrix
    width: float                # gripper opening width in metres
    quality_score: float        # grasp quality (antipodal score, etc.)
    affordance_score: float     # proximity to affordance centre
    combined_score: float       # weighted combination
    approach_direction: np.ndarray  # (3,) approach vector
    reachability_tier: int = 3  # 1=strict pose, 2=relaxed orn, 3=position-only
    
    def as_4x4(self) -> np.ndarray:
        """Return the grasp pose as a 4x4 homogeneous transformation matrix."""
        T = np.eye(4)
        T[:3, :3] = self.rotation_matrix
        T[:3, 3] = self.position
        return T


class AffordanceGraspGenerator:
    """
    Generates task-oriented grasp poses guided by affordance information.
    
    Primary: Contact-GraspNet (PyTorch port) for 6-DoF grasp detection.
    Fallback: Antipodal grasp sampling on the point cloud.
    
    Both methods are followed by the AffordGrasp ranking formula:
        ranking(g) = score(g) / max(||t(g) - c||₂, ε)
    
    Usage:
        config = GraspConfig()
        generator = AffordanceGraspGenerator(config)
        grasps = generator.generate(
            point_cloud=points,
            affordance_center_3d=center
        )
    """
    
    def __init__(self, config: GraspConfig):
        self.config = config
        self.rng = np.random.RandomState(42)
        self.cgn_model = None
        self._last_filter_stats: dict = {}

        # Try to load Contact-GraspNet if configured
        if config.method == "contact_graspnet":
            self._try_load_contact_graspnet()
    
    def _try_load_contact_graspnet(self) -> None:
        """
        Attempt to load Contact-GraspNet PyTorch model (elchun/contact_graspnet_pytorch).

        Package layout issue: the repo installs as a namespace package at
        workspace/contact_graspnet_pytorch\\, so the inner package
        (contact_graspnet_pytorch/contact_graspnet_pytorch/) is accessed as
        contact_graspnet_pytorch.contact_graspnet_pytorch — not what the internal
        imports expect.

        Fix: insert the repo root onto sys.path so 'contact_graspnet_pytorch' resolves
        directly to the inner package directory (which has __init__.py).
        Also mock 'pyrender' which is imported by data.py but not needed for inference.
        """
        import os
        import sys
        import types

        # --- Step 1: locate the repo root ---
        from intent_grasp.paths import THIRD_PARTY
        cgn_repo = str(THIRD_PARTY / "contact_graspnet_pytorch")
        if not os.path.isdir(cgn_repo):
            print("[GraspGen] contact_graspnet_pytorch repo not found at:", cgn_repo)
            print("  Clone it: git clone https://github.com/elchun/contact_graspnet_pytorch.git")
            print("")
            print("WARNING: Using antipodal sampling fallback.")
            self.cgn_model = None
            return

        # --- Step 2: fix sys.path so internal imports resolve correctly ---
        # The inner package (with __init__.py) lives at cgn_repo/contact_graspnet_pytorch/.
        # Inserting cgn_repo at the FRONT of sys.path makes 'import contact_graspnet_pytorch'
        # find that inner package instead of the namespace package at workspace/.
        if cgn_repo not in sys.path:
            sys.path.insert(0, cgn_repo)

        # Evict any already-cached namespace package entries so Python re-resolves
        for key in list(sys.modules.keys()):
            if key == "contact_graspnet_pytorch" or key.startswith("contact_graspnet_pytorch."):
                del sys.modules[key]

        # --- Step 3: mock pyrender — imported by data.py but not used for inference ---
        if "pyrender" not in sys.modules:
            pyrender_mock = types.ModuleType("pyrender")
            for attr in [
                "OffscreenRenderer", "Scene", "Mesh", "Node", "Camera",
                "PerspectiveCamera", "DirectionalLight", "SpotLight",
                "RenderFlags", "Viewer",
            ]:
                setattr(pyrender_mock, attr, None)
            sys.modules["pyrender"] = pyrender_mock
            sys.modules["pyrender.constants"] = types.ModuleType("pyrender.constants")

        # --- Step 4: import classes from the now-correctly-resolved package ---
        try:
            from contact_graspnet_pytorch.contact_grasp_estimator import GraspEstimator  # type: ignore[import]
            from contact_graspnet_pytorch import config_utils  # type: ignore[import]
            from contact_graspnet_pytorch.checkpoints import CheckpointIO  # type: ignore[import]
        except ImportError as e:
            print(f"[GraspGen] contact_graspnet_pytorch import failed: {e}")
            import traceback
            traceback.print_exc()
            print("")
            print("WARNING: Using antipodal sampling fallback.")
            self.cgn_model = None
            return

        # --- Step 5: load config + model + checkpoint ---
        # Expected layout for cgn_checkpoint_dir:
        #   <ckpt_dir>/config.yaml           ← shipped with the repo clone
        #   <ckpt_dir>/checkpoints/model.pt  ← download from repo README
        try:
            ckpt_dir = self.config.cgn_checkpoint_dir
            global_config = config_utils.load_config(ckpt_dir, batch_size=1, arg_configs=[])
            grasp_estimator = GraspEstimator(global_config)

            model_ckpt_dir = os.path.join(ckpt_dir, "checkpoints")
            model_pt = os.path.join(model_ckpt_dir, "model.pt")
            if not os.path.isfile(model_pt):
                print(f"[GraspGen] No checkpoint at {model_pt}")
                print("  Download pretrained weights from the elchun/"
                      "contact_graspnet_pytorch README (Google Drive link)")
                print("  and place model.pt in: " + model_ckpt_dir)
                print("")
                print("WARNING: Using antipodal sampling fallback.")
                self.cgn_model = None
                return

            checkpoint_io = CheckpointIO(
                checkpoint_dir=model_ckpt_dir, model=grasp_estimator.model
            )
            # Patch load_file to use explicit map_location (checkpoint was saved on CUDA)
            import torch as _torch
            _device = _torch.device('cuda' if _torch.cuda.is_available() else 'cpu')
            def _device_load_file(filename):
                import os as _os
                if not _os.path.isabs(filename):
                    filename = _os.path.join(checkpoint_io.checkpoint_dir, filename)
                print(filename)
                print(f'=> Loading checkpoint from local file (map_location={_device})...')
                state_dict = _torch.load(filename, map_location=_device)
                return checkpoint_io.parse_state_dict(state_dict)
            checkpoint_io.load_file = _device_load_file
            checkpoint_io.load("model.pt")
            grasp_estimator.model.to(_device)
            grasp_estimator.model.eval()
            grasp_estimator.device = _device

            self.cgn_model = grasp_estimator
            print(f"[GraspGen] Contact-GraspNet loaded from {model_pt}")

        except Exception as e:
            print(f"[GraspGen] Contact-GraspNet load failed: {e}")
            import traceback
            traceback.print_exc()
            print("")
            print("WARNING: Using antipodal sampling fallback.")
            self.cgn_model = None
    
    def generate(
        self,
        point_cloud: np.ndarray,
        affordance_center_3d: np.ndarray,
        affordance_points: Optional[np.ndarray] = None,
        surface_normals: Optional[np.ndarray] = None,
        table_height: float = 0.0,
        depth_image: Optional[np.ndarray] = None,
        camera_intrinsics: Optional[np.ndarray] = None,
        camera_extrinsics: Optional[np.ndarray] = None,
        segmentation_mask: Optional[np.ndarray] = None,
        sim_env=None,
    ) -> List[GraspPose]:
        """
        Generate task-oriented grasp poses.
        
        Args:
            point_cloud: (N, 3) full scene point cloud
            affordance_center_3d: (3,) 3D affordance centre from visual grounding
            affordance_points: (M, 3) point cloud of the affordance region only
            surface_normals: (N, 3) surface normals (estimated if None)
            table_height: Height of the table surface for collision filtering
            depth_image: (H, W) depth in metres (for Contact-GraspNet)
            camera_intrinsics: (3, 3) camera matrix K (for Contact-GraspNet)
            segmentation_mask: (H, W) affordance mask (for Contact-GraspNet)
        
        Returns:
            List of GraspPose objects sorted by affordance-aware ranking (best first)
        """
        # Use affordance points if available, else use full cloud
        grasp_cloud = affordance_points if affordance_points is not None else point_cloud
        
        if len(grasp_cloud) < 10:
            print("[GraspGen] Warning: Too few points for grasp generation.")
            return []
        
        # ---- Generate candidate grasps ----
        if self.cgn_model is not None and depth_image is not None:
            candidates = self._generate_contact_graspnet(
                depth_image, camera_intrinsics, segmentation_mask, camera_extrinsics
            )
        else:
            # Fallback: antipodal sampling
            if surface_normals is None:
                surface_normals = self._estimate_normals(grasp_cloud)
            elif affordance_points is not None:
                surface_normals = self._estimate_normals(affordance_points)
            
            candidates = self._sample_antipodal_grasps(grasp_cloud, surface_normals)
            
            # Evaluate quality for antipodal grasps
            for grasp in candidates:
                grasp.quality_score = self._evaluate_quality(grasp, grasp_cloud)
        
        if len(candidates) == 0:
            print("[GraspGen] Warning: No valid grasp candidates generated.")
            return []

        # ---- Dump raw CGN candidates to disk before any filtering (for MoveIt replay) ----
        import os as _os
        import time as _time
        import pybullet as _pb
        _obj_name = "unknown"
        _obj_pose_world = np.eye(4)
        if sim_env is not None and getattr(sim_env, "objects", None):
            _closest = min(
                sim_env.objects,
                key=lambda o: np.linalg.norm(
                    np.array(_pb.getBasePositionAndOrientation(o.body_id)[0])
                    - affordance_center_3d
                ),
            )
            _pos, _orn = _pb.getBasePositionAndOrientation(_closest.body_id)
            _obj_name = _closest.category
            _obj_pose_world[:3, :3] = Rotation.from_quat(np.array(_orn)).as_matrix()
            _obj_pose_world[:3, 3] = np.array(_pos)
        _dump_dir = _os.path.join("results", "cgn_candidates")
        _os.makedirs(_dump_dir, exist_ok=True)
        _dump_path = _os.path.join(_dump_dir, f"candidates_{_obj_name}_{_time.strftime('%Y%m%d_%H%M%S')}.npz")
        np.savez(
            _dump_path,
            grasp_pose_world=np.array([c.as_4x4() for c in candidates], dtype=np.float64),
            grasp_xyzxyzw=np.array(
                [np.concatenate([c.position, c.orientation]) for c in candidates],
                dtype=np.float64,
            ),
            object_pose_world=_obj_pose_world,
            object_name=np.array(_obj_name),
            width=np.array([c.width for c in candidates], dtype=np.float64),
            quality_score=np.array([c.quality_score for c in candidates], dtype=np.float64),
        )
        print(f"[GraspGen] Dumped {len(candidates)} raw candidates → {_dump_path}")
        # ---- End dump ----

        # ---- Reachability filter (pre-ranking) ----
        candidates_before_filter = len(candidates)
        if sim_env is not None:
            candidates = self._filter_by_reachability(candidates, sim_env)
        else:
            print("[GraspGen] Warning: sim_env not provided -- skipping reachability filter.")
            self._last_filter_stats = {"tier": "unfiltered", "before": candidates_before_filter,
                                       "after": candidates_before_filter}

        if len(candidates) == 0:
            print("[GraspGen] No reachable grasps after filtering.")
            return []

        # ---- AffordGrasp ranking: score / distance ----
        # This is the paper's core contribution to grasp selection.
        eps = self.config.min_distance_epsilon
        max_dist = self.config.max_distance_from_affordance_center
        
        for grasp in candidates:
            distance = np.linalg.norm(grasp.position - affordance_center_3d)
            grasp.affordance_score = distance  # store raw distance for logging

            if distance > max_dist:
                grasp.combined_score = 0.0  # hard cutoff
            else:
                # Paper formula: ranking = score / distance
                grasp.combined_score = grasp.quality_score / max(distance, eps)

        # ---- Filter and sort ----
        # Remove grasps below table
        candidates = [
            g for g in candidates if g.position[2] > table_height + 0.01
        ]
        # Remove zero-scored grasps (beyond max distance)
        candidates = [g for g in candidates if g.combined_score > 0.0]
        
        # Sort by AffordGrasp ranking (highest first)
        candidates.sort(key=lambda g: g.combined_score, reverse=True)
        
        # Return top-K
        top_grasps = candidates[:self.config.top_k_grasps]
        
        if top_grasps:
            print(f"[GraspGen] Generated {len(candidates)} candidates, "
                  f"returning top {len(top_grasps)}")
            best = top_grasps[0]
            print(f"  Best grasp: pos={best.position}, "
                  f"score={best.quality_score:.3f}, "
                  f"dist_to_aff={best.affordance_score:.4f}, "
                  f"ranking={best.combined_score:.3f}")

        if _diag.enabled():
            _diag.cp("CP9_ranked_grasps",
                     candidates_before_filter=candidates_before_filter,
                     candidates_after_filter=self._last_filter_stats.get("after",
                                                                          candidates_before_filter),
                     reachability_tier=self._last_filter_stats.get("tier", "unfiltered"),
                     n_top_grasps=len(top_grasps),
                     affordance_center=affordance_center_3d,
                     max_dist_cutoff=self.config.max_distance_from_affordance_center,
                     top_grasps=[{"pos": g.position.tolist(),
                                  "quality": g.quality_score,
                                  "dist_to_aff": g.affordance_score,
                                  "combined": g.combined_score}
                                 for g in top_grasps])

        return top_grasps
    
    # =========================================================================
    #  CONTACT-GRASPNET INFERENCE
    # =========================================================================
    
    def _generate_contact_graspnet(
        self,
        depth: np.ndarray,
        intrinsics: np.ndarray,
        segmask: Optional[np.ndarray] = None,
        camera_extrinsics: Optional[np.ndarray] = None,
    ) -> List[GraspPose]:
        """
        Generate grasps using Contact-GraspNet (elchun/contact_graspnet_pytorch).

        The GraspEstimator API:
          1. extract_point_clouds(depth, K, segmap, z_range)
               → pc_full (N,3), pc_segments {seg_id: (M,3)}, pc_colors
          2. predict_scene_grasps(pc_full, pc_segments, local_regions, ...)
               → pred_grasps_cam {seg_id: (N,4,4)}, scores {seg_id: (N,)},
                  contact_pts, gripper_openings {seg_id: (N,)}

        segmask is passed as an integer segmap so the affordance region
        (pixel value = 1) becomes its own pc_segment for local-region inference.
        """
        try:
            import torch as _torch
            # Clear any residual GPU allocations (e.g. from LangSAM) before inference
            if _torch.cuda.is_available():
                _torch.cuda.empty_cache()

            z_range = list(self.config.cgn_z_range)

            # Downsample depth (and segmap) by 2x to reduce point cloud size ~4x.
            # Full 640×480 = 307K points; 320×240 = 77K — fits within 6 GB VRAM.
            factor = 2
            depth_ds = depth[::factor, ::factor].copy()
            K_ds = intrinsics.copy()
            K_ds[0, 0] /= factor  # fx
            K_ds[1, 1] /= factor  # fy
            K_ds[0, 2] /= factor  # cx
            K_ds[1, 2] /= factor  # cy
            segmap_ds = (segmask[::factor, ::factor].astype(np.int32)
                         if segmask is not None else None)

            # Disable autocast: lang_sam/models/utils.py leaks a bfloat16 autocast
            # context at import time. Running CGN inside that context produces bfloat16
            # tensors, which crash at .numpy() with "Got unsupported ScalarType BFloat16".
            # torch.autocast(enabled=False) creates a nested scope that reverts to float32.
            autocast_ctx = (_torch.autocast(device_type="cuda", enabled=False)
                            if _torch.cuda.is_available()
                            else _torch.autocast(device_type="cpu", enabled=False))

            with autocast_ctx:
                # Step 1: depth → point clouds
                pc_full, pc_segments, _ = self.cgn_model.extract_point_clouds(
                    depth_ds, K_ds, segmap=segmap_ds, z_range=z_range
                )

                # Step 2: grasp prediction
                pred_grasps_cam, scores, _, gripper_openings = \
                    self.cgn_model.predict_scene_grasps(
                        pc_full,
                        pc_segments=pc_segments,
                        local_regions=self.config.cgn_local_regions,
                        filter_grasps=self.config.cgn_filter_grasps,
                        forward_passes=self.config.cgn_forward_passes
                    )

            # Step 3: convert to GraspPose objects (transform cam→world)
            # CGN produces poses in image/OpenCV camera frame (x-right, y-down, z-forward).
            # PyBullet's view matrix uses OpenGL frame (x-right, y-up, z-backward).
            # sim_env.depth_to_pointcloud applies the same flip before inv(view):
            #   img frame → OpenGL frame: negate Y and Z  → flip = diag([1,-1,-1,1])
            #   OpenGL frame → world:  inv(view_matrix)
            # So: cam_to_world = inv(view) @ flip
            if camera_extrinsics is not None:
                flip = np.diag([1.0, -1.0, -1.0, 1.0])
                cam_to_world = np.linalg.inv(camera_extrinsics) @ flip
            else:
                cam_to_world = np.eye(4)

            if _diag.enabled():
                seg_counts = {str(k): len(v) for k, v in pc_segments.items()}
                _diag.cp("CP7_cgn_input",
                         pc_full_shape=list(pc_full.shape),
                         pc_full_z_min=float(pc_full[:, 2].min()) if len(pc_full) > 0 else None,
                         pc_full_z_max=float(pc_full[:, 2].max()) if len(pc_full) > 0 else None,
                         pc_segments_keys=list(pc_segments.keys()),
                         pc_segments_counts=seg_counts,
                         segmap_ds_nonzero=int(np.sum(segmap_ds > 0)) if segmap_ds is not None else 0,
                         cam_to_world=cam_to_world)

            candidates = []
            for seg_id, poses_raw in pred_grasps_cam.items():
                if poses_raw is None or len(poses_raw) == 0:
                    continue

                poses_4x4 = np.array(poses_raw)           # (N, 4, 4)
                seg_scores = np.atleast_1d(
                    np.array(scores.get(seg_id, []))
                )
                seg_widths = np.atleast_1d(
                    np.array(gripper_openings.get(seg_id, []))
                )

                for i in range(len(poses_4x4)):
                    T_cam = poses_4x4[i]
                    T_world = cam_to_world @ T_cam
                    rot = T_world[:3, :3]
                    pos = T_world[:3, 3].copy()
                    try:
                        quat = Rotation.from_matrix(rot).as_quat()
                    except Exception:
                        continue  # degenerate rotation matrix

                    width = float(seg_widths[i]) if i < len(seg_widths) else 0.08
                    score = float(seg_scores[i]) if i < len(seg_scores) else 0.0

                    candidates.append(GraspPose(
                        position=pos,
                        orientation=quat,
                        rotation_matrix=rot,
                        width=width,
                        quality_score=score,
                        affordance_score=0.0,
                        combined_score=0.0,
                        approach_direction=rot[:, 2]
                    ))

            print(f"[GraspGen] Contact-GraspNet produced {len(candidates)} grasps")
            if _diag.enabled() and candidates:
                _diag.cp("CP8_cgn_raw_grasps",
                         n_candidates=len(candidates),
                         pos_x_range=[float(min(g.position[0] for g in candidates)),
                                      float(max(g.position[0] for g in candidates))],
                         pos_y_range=[float(min(g.position[1] for g in candidates)),
                                      float(max(g.position[1] for g in candidates))],
                         pos_z_range=[float(min(g.position[2] for g in candidates)),
                                      float(max(g.position[2] for g in candidates))],
                         score_range=[float(min(g.quality_score for g in candidates)),
                                      float(max(g.quality_score for g in candidates))],
                         sample_positions=[g.position.tolist() for g in candidates[:5]],
                         sample_scores=[g.quality_score for g in candidates[:5]])
            return candidates

        except Exception as e:
            import traceback
            print(f"[GraspGen] Contact-GraspNet inference failed: {e}")
            traceback.print_exc()
            print("  Falling back to antipodal sampling on available point cloud.")
            return []
    
    # =========================================================================
    #  ANTIPODAL GRASP SAMPLING
    # =========================================================================
    
    def _sample_antipodal_grasps(
        self,
        points: np.ndarray,
        normals: np.ndarray
    ) -> List[GraspPose]:
        """
        Sample antipodal grasp candidates on the point cloud.
        
        For each sampled contact point, we:
        1. Sample a contact point on the surface
        2. Use the surface normal as the grasp approach direction
        3. Sample a second contact point on the opposite side
        4. Compute the grasp frame (position, orientation, width)
        """
        n_samples = self.config.num_grasp_samples
        n_points = len(points)
        candidates = []
        
        for _ in range(n_samples):
            # Sample a contact point
            idx = self.rng.randint(n_points)
            contact1 = points[idx]
            normal1 = normals[idx]
            
            # Ensure normal points "upward-ish" (away from table)
            if normal1[2] < 0:
                normal1 = -normal1
            
            # Generate multiple approach angles
            for angle_deg in np.linspace(
                self.config.approach_angle_range[0],
                self.config.approach_angle_range[1],
                self.config.num_approach_angles
            ):
                angle_rad = np.deg2rad(angle_deg)
                
                # Compute approach direction (rotate normal around random axis)
                approach = self._rotate_approach(normal1, angle_rad)
                
                # Grasp centre is slightly above contact along approach
                grasp_center = contact1 + approach * self.config.grasp_depth
                
                # Compute grasp frame
                # z-axis: approach direction (into the surface)
                # x-axis: closing direction (perpendicular to approach)
                z_axis = -approach / (np.linalg.norm(approach) + 1e-8)
                
                # Choose x-axis perpendicular to z
                if abs(z_axis[0]) < 0.9:
                    x_axis = np.cross(z_axis, np.array([1, 0, 0]))
                else:
                    x_axis = np.cross(z_axis, np.array([0, 1, 0]))
                x_axis = x_axis / (np.linalg.norm(x_axis) + 1e-8)
                y_axis = np.cross(z_axis, x_axis)
                
                rotation = np.column_stack([x_axis, y_axis, z_axis])
                
                # Estimate grasp width from local point cloud
                width = self._estimate_grasp_width(
                    grasp_center, x_axis, points
                )
                
                if (self.config.grasp_width_range[0] <= width 
                    <= self.config.grasp_width_range[1]):
                    
                    quat = Rotation.from_matrix(rotation).as_quat()  # (x,y,z,w)
                    
                    candidates.append(GraspPose(
                        position=grasp_center,
                        orientation=quat,
                        rotation_matrix=rotation,
                        width=width,
                        quality_score=0.0,
                        affordance_score=0.0,
                        combined_score=0.0,
                        approach_direction=approach
                    ))
        
        return candidates
    
    def _rotate_approach(self, normal: np.ndarray, angle: float) -> np.ndarray:
        """Rotate approach direction around a random perpendicular axis."""
        # Create a random axis perpendicular to normal
        random_vec = self.rng.randn(3)
        perp_axis = np.cross(normal, random_vec)
        perp_norm = np.linalg.norm(perp_axis)
        if perp_norm < 1e-6:
            return normal
        perp_axis = perp_axis / perp_norm
        
        # Rodrigues rotation
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        rotated = (normal * cos_a + 
                   np.cross(perp_axis, normal) * sin_a +
                   perp_axis * np.dot(perp_axis, normal) * (1 - cos_a))
        
        norm = np.linalg.norm(rotated)
        return rotated / norm if norm > 1e-6 else normal
    
    def _estimate_grasp_width(
        self,
        center: np.ndarray,
        closing_dir: np.ndarray,
        points: np.ndarray,
        search_radius: float = 0.05
    ) -> float:
        """Estimate grasp width based on object extent along closing direction."""
        # Find nearby points
        dists = np.linalg.norm(points - center, axis=1)
        nearby_mask = dists < search_radius
        nearby_points = points[nearby_mask]
        
        if len(nearby_points) < 2:
            return 0.04  # default width
        
        # Project onto closing direction
        projections = np.dot(nearby_points - center, closing_dir)
        width = projections.max() - projections.min() + 0.005  # small margin
        
        return float(np.clip(width, 0.01, 0.10))
    
    # =========================================================================
    #  GRASP QUALITY EVALUATION
    # =========================================================================
    
    def _evaluate_quality(
        self, grasp: GraspPose, points: np.ndarray
    ) -> float:
        """
        Evaluate grasp quality using a simplified force-closure metric.
        
        Considers:
        - Antipodal alignment of contact normals
        - Point density near grasp contacts
        - Grasp width (prefer tighter grasps for stability)
        """
        center = grasp.position
        closing_dir = grasp.rotation_matrix[:, 0]  # x-axis = closing direction
        half_width = grasp.width / 2.0
        
        # Find points near each finger
        contact1 = center + closing_dir * half_width
        contact2 = center - closing_dir * half_width
        
        contact_radius = 0.01  # 1cm contact patch
        
        points_near_c1 = np.linalg.norm(points - contact1, axis=1) < contact_radius
        points_near_c2 = np.linalg.norm(points - contact2, axis=1) < contact_radius
        
        density1 = points_near_c1.sum()
        density2 = points_near_c2.sum()
        
        # Quality components
        contact_score = min(density1, density2) / max(density1 + density2, 1)
        width_score = 1.0 - (grasp.width / self.config.grasp_width_range[1])
        
        # Combined quality
        quality = 0.6 * contact_score + 0.4 * width_score
        return float(np.clip(quality, 0.0, 1.0))
    
    # =========================================================================
    #  AFFORDANCE-GUIDED SCORING
    # =========================================================================
    
    def _compute_affordance_score(
        self,
        grasp: GraspPose,
        affordance_center: np.ndarray
    ) -> float:
        """
        Score a grasp by its proximity to the affordance centre.
        
        This is the key insight from AffordGrasp: grasps closer to the
        affordance centre (e.g., the handle of a mug) are preferred
        because they enable task-oriented manipulation.
        """
        distance = np.linalg.norm(grasp.position - affordance_center)
        max_dist = self.config.max_distance_from_affordance_center
        
        # Gaussian-like scoring: closer = higher score
        score = np.exp(-0.5 * (distance / max_dist) ** 2)
        
        return float(score)
    
    # =========================================================================
    #  SURFACE NORMAL ESTIMATION
    # =========================================================================
    
    def _estimate_normals(
        self, points: np.ndarray, k_neighbours: int = 20
    ) -> np.ndarray:
        """
        Estimate surface normals using PCA on local neighbourhoods.
        Falls back to vertical normals if too few points.
        """
        n = len(points)
        normals = np.zeros_like(points)
        
        if n < k_neighbours:
            # Default: all normals point up
            normals[:, 2] = 1.0
            return normals
        
        # Simple KNN-based normal estimation
        from scipy.spatial import KDTree
        tree = KDTree(points)
        
        for i in range(n):
            _, indices = tree.query(points[i], k=min(k_neighbours, n))
            neighbors = points[indices]
            
            # PCA: smallest eigenvector = surface normal
            centroid = neighbors.mean(axis=0)
            centered = neighbors - centroid
            cov = centered.T @ centered / len(centered)
            
            try:
                _, eigenvectors = np.linalg.eigh(cov)
                normal = eigenvectors[:, 0]  # smallest eigenvalue
                
                # Orient normals to point upward
                if normal[2] < 0:
                    normal = -normal
                
                normals[i] = normal
            except np.linalg.LinAlgError:
                normals[i] = np.array([0, 0, 1])
        
        return normals
    
    # =========================================================================
    #  REACHABILITY FILTER
    # =========================================================================

    def _filter_by_reachability(self, grasps, sim_env):
        """
        Filter grasps to those the HSR arm can reach. Three-tier check:
          1. Full pose (position + orientation) IK with strict tolerance
          2. Position + relaxed orientation (within tolerance_rad)
          3. Position-only IK

        Returns the largest tier that has >= min_reachable_candidates.
        Returns the original list if filter disabled.

        Side-effect: updates self._last_filter_stats with tier/count data.
        """
        import pybullet as p
        import numpy as np

        if not self.config.enable_reachability_filter:
            self._last_filter_stats = {"tier": "unfiltered",
                                       "before": len(grasps), "after": len(grasps)}
            return grasps

        cfg = self.config
        robot_id = sim_env.robot_id
        ee_link = sim_env.ee_link_index
        arm_indices = sim_env.arm_joint_indices
        dof_map = sim_env._dof_index_of

        # Snapshot joint states so every IK test starts from a clean slate
        saved_states = [
            p.getJointState(robot_id, j)[0]
            for j in range(p.getNumJoints(robot_id))
        ]

        def _restore():
            for j, q in enumerate(saved_states):
                p.resetJointState(robot_id, j, q)

        def _test_ik(grasp, use_orientation, tolerance_rad=0.0):
            """Returns (reachable, position_residual, orientation_residual_rad)."""
            target_pos = grasp.position
            target_orn = grasp.orientation if use_orientation else None

            if target_orn is not None:
                ik = p.calculateInverseKinematics(
                    robot_id, ee_link,
                    target_pos.tolist(), target_orn.tolist(),
                    lowerLimits=sim_env._ik_lower,
                    upperLimits=sim_env._ik_upper,
                    jointRanges=sim_env._ik_ranges,
                    restPoses=sim_env._ik_rest,
                    maxNumIterations=200,
                    residualThreshold=1e-5,
                )
            else:
                ik = p.calculateInverseKinematics(
                    robot_id, ee_link,
                    target_pos.tolist(),
                    lowerLimits=sim_env._ik_lower,
                    upperLimits=sim_env._ik_upper,
                    jointRanges=sim_env._ik_ranges,
                    restPoses=sim_env._ik_rest,
                    maxNumIterations=200,
                    residualThreshold=1e-5,
                )

            # Apply solution to arm joints (reset only — no physics)
            for j_idx in arm_indices:
                dof = dof_map.get(j_idx)
                if dof is not None and dof < len(ik):
                    p.resetJointState(robot_id, j_idx, ik[dof])

            # FK readback
            ee_state = p.getLinkState(robot_id, ee_link)
            fk_pos = np.array(ee_state[4])
            pos_residual = float(np.linalg.norm(fk_pos - np.array(target_pos)))

            # Orientation residual (geodesic angle between quaternions)
            orn_residual = 0.0
            if use_orientation and target_orn is not None:
                fk_orn = np.array(ee_state[5])
                dot = abs(float(np.dot(fk_orn, np.array(target_orn))))
                orn_residual = float(2.0 * np.arccos(min(1.0, dot)))

            _restore()

            reachable = pos_residual < cfg.reachability_residual_threshold
            if use_orientation and tolerance_rad > 0:
                reachable = reachable and (orn_residual < tolerance_rad)

            return reachable, pos_residual, orn_residual

        n_total = len(grasps)

        # Tier 1: position + orientation, tight tolerance (0.1 rad ~ 6 deg)
        tier1 = [(g, p_r, o_r)
                 for g in grasps
                 for ok, p_r, o_r in [_test_ik(g, use_orientation=True, tolerance_rad=0.1)]
                 if ok]
        print(f"[Reachability] Tier 1 (strict pose): {len(tier1)}/{n_total} reachable")

        if len(tier1) >= cfg.min_reachable_candidates:
            self._last_filter_stats = {"tier": 1, "before": n_total,
                                       "after": len(tier1)}
            for g, _, _ in tier1:
                g.reachability_tier = 1
            return [g for g, _, _ in tier1]

        # Tier 2: position + relaxed orientation
        tol2 = cfg.reachability_orientation_tolerance_rad
        tier2 = [(g, p_r, o_r)
                 for g in grasps
                 for ok, p_r, o_r in [_test_ik(g, use_orientation=True,
                                               tolerance_rad=tol2)]
                 if ok]
        print(f"[Reachability] Tier 2 (+/-{np.degrees(tol2):.0f}deg orientation): "
              f"{len(tier2)}/{n_total} reachable")

        if len(tier2) >= cfg.min_reachable_candidates:
            self._last_filter_stats = {"tier": 2, "before": n_total,
                                       "after": len(tier2)}
            for g, _, _ in tier2:
                g.reachability_tier = 2
            return [g for g, _, _ in tier2]

        # Tier 3: position-only IK
        tier3 = [(g, p_r, 0.0)
                 for g in grasps
                 for ok, p_r, _ in [_test_ik(g, use_orientation=False)]
                 if ok]
        print(f"[Reachability] Tier 3 (position only): {len(tier3)}/{n_total} reachable")

        if len(tier3) > 0:
            self._last_filter_stats = {"tier": 3, "before": n_total,
                                       "after": len(tier3)}
            for g, _, _ in tier3:
                g.reachability_tier = 3
            return [g for g, _, _ in tier3]

        # Zero reachable at any tier — return original list so downstream
        # error reporting (Fix D distance gate) handles the failure honestly.
        print(f"[Reachability] WARNING: 0 grasps reachable at any tier. "
              f"Returning unfiltered to let downstream error reporting handle.")
        self._last_filter_stats = {"tier": "unfiltered_fallback",
                                   "before": n_total, "after": n_total}
        return grasps

    # =========================================================================
    #  VISUALISATION
    # =========================================================================
    
    def visualize_grasps(
        self,
        point_cloud: np.ndarray,
        grasps: List[GraspPose],
        affordance_center: np.ndarray,
        save_path: Optional[str] = None
    ) -> None:
        """
        Visualise grasp poses on the point cloud using matplotlib.
        Shows the point cloud, affordance centre, and grasp frames.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot point cloud (subsample for speed)
        if len(point_cloud) > 5000:
            indices = self.rng.choice(len(point_cloud), 5000, replace=False)
            pts = point_cloud[indices]
        else:
            pts = point_cloud
        
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                   c='lightblue', s=1, alpha=0.3, label='Scene')
        
        # Plot affordance centre
        ax.scatter(*affordance_center, c='red', s=200, marker='*',
                   label='Affordance Centre', zorder=5)
        
        # Plot grasp poses
        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(grasps)))
        for i, grasp in enumerate(grasps):
            pos = grasp.position
            approach = grasp.approach_direction
            closing = grasp.rotation_matrix[:, 0]
            
            # Draw approach vector
            ax.quiver(pos[0], pos[1], pos[2],
                      approach[0], approach[1], approach[2],
                      length=0.03, color=colors[i], arrow_length_ratio=0.3)
            
            # Draw gripper fingers
            hw = grasp.width / 2
            f1 = pos + closing * hw
            f2 = pos - closing * hw
            ax.plot([f1[0], f2[0]], [f1[1], f2[1]], [f1[2], f2[2]],
                    c=colors[i], linewidth=2)
            
            ax.scatter(*pos, c=[colors[i]], s=50, marker='o')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'AffordGrasp: Top {len(grasps)} Task-Oriented Grasps')
        ax.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[GraspGen] Visualisation saved to {save_path}")
        
        plt.close()