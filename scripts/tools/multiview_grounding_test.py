r"""
multiview_grounding_test.py -- WINDOWS side. Test whether the handle grounds
CLEANLY from any of the three captured views. Runs the grounder on each view
with the same object/part, reports part_grounding_ok + overlap ratio per view,
and saves a comparison overlay.

This tests the hypothesis: single-view part grounding fails because the handle
is poorly presented; a better viewpoint (from multiview) may isolate it.

Reads:  workspace/multiview.npz
Saves:  workspace/multiview_grounding.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from intent_grasp.config import PipelineConfig
from intent_grasp.visual_grounding import VisualAffordanceGrounder
from intent_grasp.paths import WORKSPACE

MV = f"{WORKSPACE}/multiview.npz"
OUT = f"{WORKSPACE}/multiview_grounding.png"
TARGET_OBJECT = "red mug"
TARGET_PART   = "handle"


def main():
    config = PipelineConfig()
    config.visual_grounding.workspace_image_crop = None
    grounder = VisualAffordanceGrounder(config.visual_grounding)

    mv = np.load(MV, allow_pickle=True)
    names = [str(n) for n in mv["view_names"]]
    K = mv["camera_intrinsics"]
    V = len(names)

    fig, ax = plt.subplots(2, V, figsize=(6*V, 9))
    print("="*60)
    for i, name in enumerate(names):
        rgb = mv["rgb"][i]; depth = mv["depth"][i]; extr = mv["camera_extrinsics"][i]
        gr = grounder.ground(rgb_image=rgb, depth_image=depth,
                             target_object=TARGET_OBJECT, target_part=TARGET_PART,
                             camera_intrinsics=K, camera_extrinsics=extr,
                             simulation_segmask=None, target_body_id=None)
        om = (gr.object_mask > 0); am = (gr.affordance_mask > 0)
        ratio = am.sum() / max(om.sum(), 1)
        ok = getattr(gr, "part_grounding_ok", None)
        print(f" view '{name}': part_grounding_ok={ok}  "
              f"affordance/object={ratio:.0%}  aff_px={int(am.sum())}")

        ax[0, i].imshow(rgb); ax[0, i].set_title(f"{name} RGB"); ax[0, i].axis("off")
        ax[1, i].imshow(rgb); ax[1, i].imshow(am, alpha=0.5, cmap="Oranges")
        tag = "OK" if ok else "COLLAPSED"
        ax[1, i].set_title(f"{name} handle mask [{tag}] {ratio:.0%}"); ax[1, i].axis("off")
    print("="*60)
    print("Looking for a view where part_grounding_ok=True and ratio is LOW")
    print("(handle isolated, not whole mug).")

    plt.tight_layout(); plt.savefig(OUT, dpi=100, bbox_inches="tight")
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
