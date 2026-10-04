"""intent_grasp: intent-driven, part-aware grasping for the Toyota HSR."""
import sys as _sys

# grasps_out.npz files recorded before the code became a package pickle
# GraspPose objects under the old top-level module name. Registering the alias
# lets np.load(..., allow_pickle=True) read them unchanged.
from intent_grasp import grasp_generation as _grasp_generation

_sys.modules.setdefault("grasp_generation", _grasp_generation)
