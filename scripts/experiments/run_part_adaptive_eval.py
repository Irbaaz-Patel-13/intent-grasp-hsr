import sys
import json
from pathlib import Path

import numpy as np
from intent_grasp import part_adaptive as pa
def json_safe(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def find_cloud(data):
    preferred = [
        "points",
        "point_cloud",
        "cloud",
        "xyz",
        "world_points",
        "fused_cloud",
    ]

    for key in preferred:
        if key not in data.files:
            continue

        arr = np.asarray(data[key])

        if arr.ndim == 2 and arr.shape[1] >= 3:
            return arr[:, :3].astype(float), key

    for key in data.files:
        arr = np.asarray(data[key])

        if arr.ndim == 2 and arr.shape[1] >= 3:
            return arr[:, :3].astype(float), key

    return None, None


def main():

    if len(sys.argv) != 2:
        print()
        print("Usage:")
        print(
            r'  .\.venv\Scripts\python.exe .\run_part_adaptive_eval.py "PATH_TO_NPZ"'
        )
        print()
        sys.exit(2)

    input_path = Path(sys.argv[1]).resolve()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file does not exist:\n{input_path}"
        )

    print("=" * 78)
    print("PART-ADAPTIVE READ-ONLY EVALUATION")
    print("=" * 78)
    print(f"Input: {input_path}")
    print()

    # ---------------------------------------------------------
    # LOAD NPZ
    # ---------------------------------------------------------

    data = np.load(input_path, allow_pickle=True)

    print("NPZ CONTENTS")
    print("-" * 78)

    for key in data.files:
        arr = data[key]
        print(
            f"  {key}: "
            f"shape={getattr(arr, 'shape', None)}, "
            f"dtype={getattr(arr, 'dtype', None)}"
        )

    # ---------------------------------------------------------
    # FIND POINT CLOUD
    # ---------------------------------------------------------

    cloud, cloud_key = find_cloud(data)

    if cloud is None:
        raise RuntimeError(
            "\nNo Nx3 point cloud was found in this NPZ.\n"
            f"Available keys: {data.files}"
        )

    cloud = cloud[np.isfinite(cloud).all(axis=1)]

    if len(cloud) < 20:
        raise RuntimeError(
            f"Only {len(cloud)} valid 3D points found."
        )

    print()
    print("POINT CLOUD")
    print("-" * 78)
    print(f"  Source key: {cloud_key}")
    print(f"  Valid points: {len(cloud)}")
    print(
        f"  XYZ min: "
        f"{np.min(cloud, axis=0)}"
    )
    print(
        f"  XYZ max: "
        f"{np.max(cloud, axis=0)}"
    )

    # ---------------------------------------------------------
    # SEED
    # ---------------------------------------------------------

    seed_xy = cloud[:, :2].mean(axis=0)

    print()
    print("TARGET SEED")
    print("-" * 78)
    print(f"  XY centroid: {seed_xy}")

    # ---------------------------------------------------------
    # ADAPTIVE CROP
    # ---------------------------------------------------------

    cropped, crop_radius = pa.adaptive_crop(
        cloud,
        seed_xy
    )

    print()
    print("1. ADAPTIVE CROP")
    print("-" * 78)
    print(f"  Radius: {crop_radius:.3f} m")
    print(f"  Points: {len(cropped)}")
    print(
        f"  Retained: "
        f"{100.0 * len(cropped) / len(cloud):.1f}%"
    )

    # ---------------------------------------------------------
    # OBJECT ISOLATION
    # ---------------------------------------------------------

    object_cloud, isolation = pa.isolate_object(
        cropped,
        seed_xy
    )

    print()
    print("2. OBJECT ISOLATION")
    print("-" * 78)

    for key, value in isolation.items():
        print(f"  {key}: {value}")

    print(f"  Object points: {len(object_cloud)}")

    # ---------------------------------------------------------
    # SHAPE CLASSIFICATION
    # ---------------------------------------------------------

    shape = pa.classify_shape(object_cloud)

    print()
    print("3. SHAPE CLASSIFICATION")
    print("-" * 78)

    important_shape_keys = [
        "shape_class",
        "height",
        "max_horizontal",
        "hollow",
        "object_too_wide",
        "extent",
        "linearity",
        "planarity",
        "sphericity",
    ]

    for key in important_shape_keys:
        if key not in shape:
            continue

        value = shape[key]

        if isinstance(value, (float, np.floating)):
            print(f"  {key}: {float(value):.4f}")
        else:
            print(f"  {key}: {value}")

    # ---------------------------------------------------------
    # SHAPE-ADAPTIVE DECOMPOSITION
    # ---------------------------------------------------------

    parts, decomposition_info = pa.decompose(
        object_cloud,
        shape=shape
    )

    print()
    print("4. SHAPE-ADAPTIVE DECOMPOSITION")
    print("-" * 78)

    for key, value in decomposition_info.items():

        if key in ["extent"]:
            print(f"  {key}: {value}")

        elif isinstance(value, (float, np.floating)):
            print(f"  {key}: {float(value):.4f}")

        else:
            print(f"  {key}: {value}")

    print()
    print("  GENERATED PARTS")

    for name, points in parts.items():
        print(
            f"    {name:30s} "
            f"{len(points):6d} points"
        )

    # ---------------------------------------------------------
    # STRUCTURAL COMPONENTS
    # ---------------------------------------------------------

    components = {}
    component_info = {}
    descriptions = {}

    print()
    print("5. STRUCTURAL COMPONENT ANALYSIS")
    print("-" * 78)

    try:

        components, component_info = pa.find_components(
            object_cloud
        )

        print(
            f"  Components found: "
            f"{len(components)}"
        )

        for name, points in components.items():
            print(
                f"    {name:30s} "
                f"{len(points):6d} points"
            )

        try:
            descriptions = pa.describe_components(
                components,
                component_info
            )

            print()
            print("  COMPONENT EVIDENCE")

            for name, description in descriptions.items():

                print()
                print(f"    [{name}]")

                if isinstance(description, dict):

                    for key, value in description.items():
                        print(
                            f"      {key}: {value}"
                        )

                else:
                    print(
                        f"      {description}"
                    )

        except Exception as exc:

            print()
            print(
                "  describe_components() failed:"
            )
            print(
                f"    {type(exc).__name__}: {exc}"
            )

    except Exception as exc:

        print(
            "  find_components() failed:"
        )
        print(
            f"    {type(exc).__name__}: {exc}"
        )

    # ---------------------------------------------------------
    # SAVE MACHINE-READABLE RESULT
    # ---------------------------------------------------------

    output_dir = Path("evaluation_outputs")
    output_dir.mkdir(exist_ok=True)

    output_path = (
        output_dir /
        "part_adaptive_mug_evaluation.json"
    )

    result = {
        "input": str(input_path),
        "cloud_key": cloud_key,
        "raw_points": int(len(cloud)),
        "cropped_points": int(len(cropped)),
        "object_points": int(len(object_cloud)),
        "crop_radius_m": float(crop_radius),
        "seed_xy": seed_xy,
        "isolation": isolation,
        "shape": {
            key: value
            for key, value in shape.items()
            if key not in ["axes", "proj"]
        },
        "decomposition": decomposition_info,
        "parts": {
            name: int(len(points))
            for name, points in parts.items()
        },
        "components": {
            name: int(len(points))
            for name, points in components.items()
        },
        "component_descriptions": descriptions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            json_safe(result),
            f,
            indent=2
        )

    print()
    print("=" * 78)
    print("EVALUATION COMPLETE")
    print("=" * 78)
    print(f"Result: {output_path.resolve()}")
    print()
    print("IMPORTANT:")
    print("  part_adaptive.py was NOT modified.")
    print("  The input NPZ was NOT modified.")
    print("=" * 78)


if __name__ == "__main__":
    main()
