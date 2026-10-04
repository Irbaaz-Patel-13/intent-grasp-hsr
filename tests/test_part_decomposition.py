r"""
test_part_decomposition.py -- standalone smoke test for part_decomposition.py.
Builds a synthetic mug-shaped point cloud (table plane + cylindrical body +
rim ring + a laterally-offset handle cluster) so classification can be
checked against known ground truth without needing a real capture.

Run: python -m pytest tests/test_part_decomposition.py
Expected on success: prints "ALL PASS" and exits 0.
"""
import numpy as np

from intent_grasp import part_decomposition as pd
RNG = np.random.default_rng(0)


def _ring(n, r, z, jitter=0.002):
    theta = RNG.uniform(0, 2 * np.pi, n)
    x = r * np.cos(theta) + RNG.normal(0, jitter, n)
    y = r * np.sin(theta) + RNG.normal(0, jitter, n)
    zz = np.full(n, z) + RNG.normal(0, jitter, n)
    return np.stack([x, y, zz], axis=1)


def _disc(n, r_max, z, jitter=0.002):
    theta = RNG.uniform(0, 2 * np.pi, n)
    r = RNG.uniform(0, r_max, n)
    x = r * np.cos(theta) + RNG.normal(0, jitter, n)
    y = r * np.sin(theta) + RNG.normal(0, jitter, n)
    zz = np.full(n, z) + RNG.normal(0, jitter, n)
    return np.stack([x, y, zz], axis=1)


def make_synthetic_mug():
    """
    Object-centroid axis at xy=(0.5, 0.2). Table at z=0.40 (world frame).
    Mug body radius 0.04, height z in [0.42, 0.50] (top). Handle sticks out
    to xy=(0.5 + 0.055, 0.2) around z=0.44-0.47 (a coherent cluster clearly
    beyond r_outer, tight in xy so DBSCAN eps=0.015 links it).
    """
    ax, ay = 0.5, 0.2
    table = _disc(600, 0.10, 0.40, jitter=0.003) + np.array([ax, ay, 0])
    body_layers = []
    for z in np.linspace(0.425, 0.495, 12):
        body_layers.append(_ring(40, 0.04, z, jitter=0.0015) + np.array([ax, ay, 0]))
    body = np.concatenate(body_layers, axis=0)
    rim = _ring(150, 0.04, 0.50, jitter=0.0015) + np.array([ax, ay, 0])
    interior = _disc(60, 0.018, 0.46, jitter=0.0015) + np.array([ax, ay, 0])
    # handle: small tight cluster laterally offset beyond r_outer
    n_handle = 30
    hx = ax + 0.055 + RNG.normal(0, 0.004, n_handle)
    hy = ay + RNG.normal(0, 0.004, n_handle)
    hz = RNG.uniform(0.44, 0.47, n_handle)
    handle = np.stack([hx, hy, hz], axis=1)
    cloud = np.concatenate([table, body, rim, interior, handle], axis=0)
    return cloud, (ax, ay), n_handle


def test_extract_object_cloud_radius():
    cloud, (ax, ay), _ = make_synthetic_mug()
    far = np.array([[ax + 5.0, ay, 0.4]])
    cloud_with_outlier = np.concatenate([cloud, far], axis=0)
    obj = pd.extract_object_cloud(cloud_with_outlier, np.array([ax, ay]), radius=0.12)
    assert len(obj) == len(cloud), f"expected outlier dropped, got {len(obj)} vs {len(cloud)}"


def test_remove_support_plane_drops_table():
    cloud, _, _ = make_synthetic_mug()
    above, z_table = pd.remove_support_plane(cloud, percentile=15, margin=0.015)
    assert 0.395 < z_table < 0.41, f"z_table={z_table} not near table z=0.40"
    assert above[:, 2].min() > z_table + 0.014, "plane points should be stripped"
    # body/rim/interior/handle all survive (12*40+150+60+30=720 pts)
    assert len(above) > 650, f"too few points survived plane removal: {len(above)}"


def test_classify_parts_buckets_synthetic_mug():
    cloud, (ax, ay), n_handle = make_synthetic_mug()
    above, z_table = pd.remove_support_plane(cloud, percentile=15, margin=0.015)
    parts, stats = pd.classify_parts(above, z_table)

    assert len(parts["rim"]) > 100, f"rim too small: {len(parts['rim'])}"
    assert len(parts["body"]) > 300, f"body too small: {len(parts['body'])}"
    assert len(parts["interior"]) > 20, f"interior too small: {len(parts['interior'])}"
    # near-root handle points (r close to r_outer, where the handle meets the
    # body) legitimately fall inside the r_outer + 0.005 candidate margin and
    # are never DBSCAN candidates -- only the protruding majority is
    # recoverable, so this checks "recovery clearly worked", not "near-total".
    assert len(parts["handle"]) >= 20, (
        f"handle cluster recovery too small: {len(parts['handle'])} vs {n_handle}")

    # geometry sanity: handle points should sit outside r_outer
    handle_r = np.linalg.norm(parts["handle"][:, :2] - stats["axis_xy"], axis=1)
    assert handle_r.min() > stats["r_outer"], "handle points should be beyond r_outer"

    # rim points should be near z_top
    assert parts["rim"][:, 2].min() > stats["z_top"] - 0.021


def test_dbscan_xy_finds_single_dense_cluster_and_ignores_noise():
    cluster = RNG.normal(0, 0.003, (30, 2)) + np.array([0.5, 0.5])
    noise = RNG.uniform(-1, 1, (10, 2))
    xy = np.concatenate([cluster, noise], axis=0)
    labels = pd.dbscan_xy(xy, eps=0.015, min_samples=15)
    cluster_labels = labels[:30]
    assert (cluster_labels == cluster_labels[0]).all(), "cluster should share one label"
    assert cluster_labels[0] != -1, "dense cluster should not be noise"
    # scattered noise points (far apart) should mostly be -1
    assert (labels[30:] == -1).sum() >= 8


def test_handle_grasp_anchor_is_near_body():
    cloud, (ax, ay), _ = make_synthetic_mug()
    above, z_table = pd.remove_support_plane(cloud, percentile=15, margin=0.015)
    parts, stats = pd.classify_parts(above, z_table)
    anchor = pd.handle_grasp_anchor(parts["handle"], stats["axis_xy"])
    anchor_r = np.linalg.norm(anchor[:2] - stats["axis_xy"])
    full_handle_r = np.linalg.norm(parts["handle"][:, :2] - stats["axis_xy"], axis=1)
    assert anchor_r <= np.median(full_handle_r), "root anchor should be closer-in than the handle average"


def test_select_part_from_target_synonym_mapping():
    parts = {
        "rim": np.zeros((150, 3)), "interior": np.zeros((60, 3)),
        "body": np.zeros((400, 3)), "handle": np.zeros((90, 3)),
        "unclassified": np.zeros((10, 3)),
    }
    name, pts, notes = pd.select_part_from_target("opening", [], parts)
    assert name == "rim", f"'opening' should map to rim, got {name}"
    name, pts, notes = pd.select_part_from_target("grip", [], parts)
    assert name == "handle", f"'grip' should map to handle, got {name}"
    name, pts, notes = pd.select_part_from_target("wall", [], parts)
    assert name == "body", f"'wall' should map to body, got {name}"
    name, pts, notes = pd.select_part_from_target("inside", [], parts)
    assert name == "interior", f"'inside' should map to interior, got {name}"
    name, pts, notes = pd.select_part_from_target("some unknown thing", [], parts)
    assert name == "body", f"unrecognized target_part should default to body, got {name}"
    assert notes, "expected a note for the unrecognized-synonym default"


def test_select_part_from_target_keep_clear_inconsistency_falls_back():
    # VLM picked rim but also listed rim in keep_clear -- inconsistency.
    # body is largest of the remaining candidates.
    parts = {
        "rim": np.zeros((150, 3)), "interior": np.zeros((60, 3)),
        "body": np.zeros((400, 3)), "handle": np.zeros((90, 3)),
        "unclassified": np.zeros((10, 3)),
    }
    name, pts, notes = pd.select_part_from_target("rim", ["opening"], parts)
    assert name == "body", f"expected fallback to body (largest, not in keep_clear), got {name}"
    assert any("inconsistency" in n for n in notes), f"expected an inconsistency note, got {notes}"


def test_select_part_from_target_fallbacks_respect_keep_clear():
    # handle too small -> falls back, but body is in keep_clear so it must
    # skip body too and land on rim (the next largest not excluded).
    parts = {
        "rim": np.zeros((150, 3)), "interior": np.zeros((60, 3)),
        "body": np.zeros((400, 3)), "handle": np.zeros((10, 3)),
        "unclassified": np.zeros((0, 3)),
    }
    name, pts, notes = pd.select_part_from_target("handle", ["body"], parts)
    assert name == "rim", f"expected fallback to rim (body excluded via keep_clear), got {name}"
    assert notes, "expected a fallback note"

    # body too small -> falls back to rim (no keep_clear conflict)
    parts2 = dict(parts)
    parts2["body"] = np.zeros((5, 3))
    name2, pts2, notes2 = pd.select_part_from_target("body", [], parts2)
    assert name2 == "rim", f"expected fallback to rim, got {name2}"


def test_select_part_from_target_normalizes_compound_keep_clear_phrases():
    # Real VLM output uses compound phrases like "rim/opening", not bare
    # synonym words -- this must still be recognized and enforced.
    parts = {
        "rim": np.zeros((150, 3)), "interior": np.zeros((60, 3)),
        "body": np.zeros((400, 3)), "handle": np.zeros((90, 3)),
        "unclassified": np.zeros((10, 3)),
    }
    name, pts, notes = pd.select_part_from_target("rim", ["rim/opening"], parts)
    assert name == "body", f"expected fallback to body (rim excluded via compound keep_clear phrase), got {name}"
    assert any("inconsistency" in n for n in notes), f"expected an inconsistency note, got {notes}"

    # a genuinely unrecognized keep_clear phrase should be logged, not silently dropped
    name2, pts2, notes2 = pd.select_part_from_target("body", ["something unrecognizable"], parts)
    assert name2 == "body"
    assert any("no recognized synonym" in n for n in notes2), f"expected an unmapped-keep_clear note, got {notes2}"


def test_select_part_from_target_overrides_keep_clear_rather_than_returning_empty_bucket():
    # Real battery scenario: keep_clear excludes both rim and body; handle
    # is below its point-count minimum; interior is empty (a single oblique
    # hand-camera view can't see inside the mug). The fallback must not
    # settle for the empty interior bucket just because it's "not excluded"
    # -- it must override keep_clear as a last resort and return the
    # largest non-empty part instead of a 0-point selection.
    parts = {
        "rim": np.zeros((997, 3)), "interior": np.zeros((0, 3)),
        "body": np.zeros((1313, 3)), "handle": np.zeros((65, 3)),
        "unclassified": np.zeros((493, 3)),
    }
    name, pts, notes = pd.select_part_from_target("handle", ["rim", "body"], parts)
    assert name == "body", f"expected override fallback to body (largest non-empty), got {name}"
    assert len(pts) > 0, "must never return an empty-bucket selection when a non-empty part exists"
    assert any("OVERRIDING keep_clear" in n for n in notes), f"expected a loud override note, got {notes}"


def test_select_part_from_target_direct_match_never_returns_empty_bucket():
    # target_part maps directly to a bucket with 0 points (no keep_clear
    # conflict, no under-threshold handle/body fallback involved) -- the
    # direct-match fast path must still reject an empty selection and
    # route through the fallback helper, not return it silently.
    parts = {
        "rim": np.zeros((997, 3)), "interior": np.zeros((0, 3)),
        "body": np.zeros((1313, 3)), "handle": np.zeros((65, 3)),
        "unclassified": np.zeros((493, 3)),
    }
    name, pts, notes = pd.select_part_from_target("interior", ["rim"], parts)
    assert name != "interior", f"must not directly select an empty bucket, got {name}"
    assert len(pts) > 0, "must never return an empty-bucket selection when a non-empty part exists"
    assert notes, "expected a fallback note explaining the empty-bucket rejection"


if __name__ == "__main__":
    test_extract_object_cloud_radius()
    test_remove_support_plane_drops_table()
    test_classify_parts_buckets_synthetic_mug()
    test_dbscan_xy_finds_single_dense_cluster_and_ignores_noise()
    test_handle_grasp_anchor_is_near_body()
    test_select_part_from_target_synonym_mapping()
    test_select_part_from_target_keep_clear_inconsistency_falls_back()
    test_select_part_from_target_fallbacks_respect_keep_clear()
    test_select_part_from_target_normalizes_compound_keep_clear_phrases()
    test_select_part_from_target_overrides_keep_clear_rather_than_returning_empty_bucket()
    test_select_part_from_target_direct_match_never_returns_empty_bucket()
    print("ALL PASS")
