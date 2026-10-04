r"""
hand_view_grounding.py -- WINDOWS side. The linchpin test: does 'handle' ground
on the close-up hand-camera view, where it collapsed (90%) on the head view?

Runs the SAME grounder on the hand_view.npz RGB and reports part_grounding_ok +
overlap ratio + saves an overlay. This single result decides whether the
eye-in-hand approach resolves the part-grounding failure.

Copy hand_view.npz from the container to workspace/ first:
  (WSL2)  cp ~/tmc_wrs_docker/notebooks/cgn_data/hand_view.npz <repo>/workspace/
"""
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.config import PipelineConfig
from intent_grasp.visual_grounding import VisualAffordanceGrounder
from intent_grasp.paths import WORKSPACE

NPZ = f"{WORKSPACE}/hand_view.npz"
OUT = f"{WORKSPACE}/hand_view_grounding.png"
TARGET_OBJECT = "red mug"
TARGET_PART   = "handle"


def main():
    d = np.load(NPZ, allow_pickle=True)
    rgb = d["rgb"]; K = d["camera_intrinsics"]
    view = str(d["view"]) if "view" in d else "?"
    print(f"hand view '{view}'  rgb{rgb.shape}")

    config = PipelineConfig()
    config.visual_grounding.workspace_image_crop = None
    grounder = VisualAffordanceGrounder(config.visual_grounding)

    # depth=None: hand camera is RGB-only; we only test 2D grounding here.
    # Pass a dummy depth so the grounder runs its 2D mask logic; we ignore 3D.
    dummy_depth = np.full(rgb.shape[:2], 0.3, dtype=np.float32)
    dummy_extr = np.eye(4)

    gr = grounder.ground(rgb_image=rgb, depth_image=dummy_depth,
                         target_object=TARGET_OBJECT, target_part=TARGET_PART,
                         camera_intrinsics=K, camera_extrinsics=dummy_extr,
                         simulation_segmask=None, target_body_id=None)

    om = (gr.object_mask > 0); am = (gr.affordance_mask > 0)
    ratio = am.sum() / max(om.sum(), 1)
    ok = getattr(gr, "part_grounding_ok", None)
    print("="*56)
    print(f"  part_grounding_ok = {ok}")
    print(f"  object_mask px    = {int(om.sum())}")
    print(f"  handle_mask px    = {int(am.sum())}")
    print(f"  handle/object     = {ratio:.0%}   (head view was 90% = COLLAPSED)")
    print("="*56)
    if ok and ratio < 0.6:
        print("  >>> HANDLE ISOLATED on hand view -- eye-in-hand resolves it!")
    else:
        print("  >>> still collapsed -- viewpoint alone doesn't fix grounding.")

    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    ax[0].imshow(rgb); ax[0].set_title(f"hand view [{view}] RGB")
    ax[1].imshow(rgb); ax[1].imshow(om, alpha=0.5, cmap="Blues"); ax[1].set_title("object_mask")
    ax[2].imshow(rgb); ax[2].imshow(am, alpha=0.5, cmap="Oranges")
    tag = "OK" if (ok and ratio < 0.6) else "COLLAPSED"
    ax[2].set_title(f"handle_mask [{tag}] {ratio:.0%}")
    for a in ax: a.axis("off")
    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight")
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
