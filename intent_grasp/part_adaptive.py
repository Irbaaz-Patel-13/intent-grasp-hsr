#!/usr/bin/env python
r"""part_adaptive.py -- shape-adaptive part decomposition + part->2D-mask
projection, so grasps can be generated ON the part the instruction implies.

Why this module exists
----------------------
The pipeline already infers WHICH PART to grasp (VLM: "handle", "sides",
"middle section") but nothing downstream acts on it:

  * run_grounding_grasp.py grounds the whole OBJECT; its second, part-level
    LangSAM pass has collapsed to the whole object on every real run
    (94-98% coverage), so aff_center_3d is the object centroid.
  * grasp_generation.generate() restricts CGN sampling by `segmentation_mask`
    (a 2D image mask), NOT by `affordance_points` -- confirmed at
    grasp_generation.py:236-238 / 418-425. So handing CGN 3D part points does
    nothing; the part must be expressed as an IMAGE MASK.
  * part_decomposition.classify_parts() works, but its vocabulary
    (rim/interior/body/handle) and its z-band + radial-distance logic assume an
    upright rotationally-symmetric vessel. Measured consequences (23 Jul batch):
      - VLM said "middle section"/"sides" for a remote -> no such part exists,
        select_part_from_target cannot match.
      - pot standalone: minor width 147 mm > 125 mm aperture (body ungraspable,
        handle mandatory) yet nothing steers CGN to the handle.
      - fixed 0.12 m crop: the same remote measured linearity 0.92 / 13 mm alone
        but 0.26 / 73 mm in clutter, because the crop swallowed its neighbours.

This module supplies the three missing pieces:
  1. adaptive_crop      -- object-sized crop instead of a fixed 0.12 m sphere
  2. decompose          -- classify the object's SHAPE first, then decompose
                           with a scheme that fits it (vessel / elongated /
                           slab / wide_vessel), delegating vessels to the
                           existing proven classify_parts when available
  3. match_part / project_part_to_mask -- map the VLM's free-text part name onto
                           whatever geometric parts exist, then project that
                           part's points into image space as the mask CGN needs

Frame convention is taken from run_grounding_grasp.backproject_mask (lines
41-54): OpenCV pinhole, then an OpenGL flip [x, -y, -z, 1], then
p_world = inv(extrinsics) @ p_cam. project_points_to_pixels() is the exact
inverse and is round-trip tested against that code.
"""
from __future__ import annotations
import numpy as np

APERTURE_MAX = 0.125           # measured usable gripper aperture (m)


# ----------------------------------------------------------------- projection
def project_points_to_pixels(points_world, K, extrinsics):
    """World (odom/base) -> pixel coords. Exact inverse of backproject_mask.

    Returns (u, v, z_cam, valid) with z_cam the positive depth along the view
    axis and `valid` marking points in front of the camera.
    """
    P = np.asarray(points_world, float).reshape(-1, 3)
    hom = np.concatenate([P, np.ones((len(P), 1))], axis=1)      # (N,4)
    cam = (np.asarray(extrinsics, float) @ hom.T).T              # world -> OpenGL cam
    x_gl, y_gl, z_gl = cam[:, 0], cam[:, 1], cam[:, 2]
    # backproject built [x_img, -y_img, -z]; invert that flip
    z = -z_gl
    x_img, y_img = x_gl, -y_gl
    valid = z > 1e-6
    z_safe = np.where(valid, z, 1.0)
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    u = x_img * fx / z_safe + cx
    v = y_img * fy / z_safe + cy
    return u, v, z, valid


def project_part_to_mask(part_points, K, extrinsics, shape, dilate_px=6,
                         min_px=60):
    """Part points -> binary image mask suitable for grasp_gen(segmentation_mask=).

    Dilated so the mask is solid rather than a sparse dot pattern; CGN segments
    the cloud through this mask, and holes would fragment the region.
    """
    h, w = shape
    u, v, z, valid = project_points_to_pixels(part_points, K, extrinsics)
    ui = np.round(u[valid]).astype(int)
    vi = np.round(v[valid]).astype(int)
    keep = (ui >= 0) & (ui < w) & (vi >= 0) & (vi < h)
    ui, vi = ui[keep], vi[keep]
    mask = np.zeros((h, w), dtype=np.uint8)
    if len(ui) == 0:
        return mask, 0
    mask[vi, ui] = 1
    if dilate_px > 0:
        try:
            import cv2
            k = np.ones((2 * dilate_px + 1, 2 * dilate_px + 1), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
            mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
        except ImportError:
            from scipy import ndimage
            mask = ndimage.binary_dilation(mask, iterations=dilate_px).astype(np.uint8)
    n = int(mask.sum())
    return mask, n


# ------------------------------------------------------------ crop + PCA
def adaptive_crop(cloud, centroid_xy, z_table=None, start=0.10, step=0.03,
                  max_radius=0.30, grow_tol=0.12):
    """Crop around the object, growing the radius until the point count stops
    growing appreciably -- i.e. until the object is fully enclosed. Replaces the
    fixed 0.12 m sphere, which truncated the pot and merged neighbours in clutter.
    """
    C = np.asarray(cloud, float)
    if z_table is not None:
        C = C[C[:, 2] > z_table + 0.008]
    c = np.asarray(centroid_xy, float)[:2]
    d = np.linalg.norm(C[:, :2] - c, axis=1)
    r, prev = start, 0
    while r < max_radius:
        n = int((d < r).sum())
        if prev and (n - prev) / max(prev, 1) < grow_tol:
            break
        prev, r = n, r + step
    return C[d < r], round(r, 3)


def isolate_object(points, seed_xy, eps=0.018, min_samples=10):
    """Keep only the connected cluster containing the target.

    adaptive_crop() takes a cylinder around the affordance centre, so in clutter
    it merges neighbours: on the mug+can scene (26 Jul) the crop grew to 0.14 m,
    swallowed the can, and the component finder then reported table-edge noise as
    a "lateral protrusion" which the binder selected as the mug's handle. The
    part mask landed on bare table.

    Clustering the cropped points and keeping the cluster nearest the seed makes
    the object a connected body rather than a radius, which is what "the object"
    actually means.
    """
    P = np.asarray(points, float)
    if len(P) < 30:
        return P, dict(method="too_few", n_clusters=0, kept=len(P))
    lab = None
    try:
        from sklearn.cluster import DBSCAN
        lab = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(P)
        method = "dbscan"
    except Exception:
        try:
            from scipy import ndimage
            v = 0.012
            idx = np.floor((P - P.min(0)) / v).astype(int)
            dims = idx.max(0) + 3
            vol = np.zeros(dims, bool)
            vol[idx[:, 0], idx[:, 1], idx[:, 2]] = True
            cc, n = ndimage.label(vol)
            lab = cc[idx[:, 0], idx[:, 1], idx[:, 2]] - 1
            method = "voxel_cc"
        except Exception:
            return P, dict(method="unavailable", n_clusters=0, kept=len(P))
    seed = np.asarray(seed_xy, float)[:2]
    best, best_d, sizes = None, 1e9, {}
    for u in set(lab.tolist()):
        if u < 0:
            continue
        grp = P[lab == u]
        sizes[int(u)] = len(grp)
        if len(grp) < 40:
            continue
        d = float(np.linalg.norm(grp[:, :2].mean(0) - seed))
        if d < best_d:
            best, best_d = u, d
    if best is None:
        return P, dict(method=method, n_clusters=len(sizes), kept=len(P),
                       note="no cluster large enough; kept everything")
    keep = P[lab == best]
    return keep, dict(method=method, n_clusters=len(sizes), kept=len(keep),
                      dropped=len(P) - len(keep), seed_dist=round(best_d, 3),
                      cluster_sizes=sorted(sizes.values(), reverse=True)[:6])


def pca(points):
    P = np.asarray(points, float)
    c = P.mean(0); X = P - c
    w, V = np.linalg.eigh(np.cov(X.T))
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    proj = X @ V
    ext = [float(np.percentile(proj[:, i], 98) - np.percentile(proj[:, i], 2))
           for i in range(3)]
    tot = float(w.sum()) or 1e-12
    return dict(centroid=c, axes=V, eigvals=w, extent=ext, proj=proj,
                linearity=float((w[0]-w[1])/tot), planarity=float((w[1]-w[2])/tot),
                sphericity=float(w[2]/tot))


def classify_shape(points, z_table=None):
    """Coarse object shape class -- decides WHICH decomposition scheme applies."""
    p = pca(points)
    e0, e1, e2 = p["extent"]
    e1 = max(e1, 1e-6); e2 = max(e2, 1e-6)
    height = float(points[:, 2].max() - points[:, 2].min())
    horiz = max(float(points[:, 0].max()-points[:, 0].min()),
                float(points[:, 1].max()-points[:, 1].min()))
    # hollowness: for an upright vessel the topmost band is a ring, so its
    # points sit far from the vertical axis relative to the band's own radius
    top = points[points[:, 2] > points[:, 2].max() - 0.02]
    hollow = False
    if len(top) > 40:
        r = np.linalg.norm(top[:, :2] - top[:, :2].mean(0), axis=1)
        hollow = float(r.mean()) > 0.55 * float(r.max())
    if e0 / e1 > 2.5 and e1 / e2 < 2.5:
        cls = "elongated"
    elif e0 / e2 > 3.0 and e1 / e2 > 2.2 and height < 0.06:
        cls = "slab"
    elif hollow and height > 0.04:
        cls = "wide_vessel" if horiz > APERTURE_MAX else "vessel"
    else:
        cls = "wide_blob" if horiz > APERTURE_MAX else "blob"
    # NOTE: this is an OBJECT-level flag meaning "the whole object cannot be
    # spanned in one bite" -- it is NOT the grasp gate. The gate is applied
    # per-part to part_width(), because a 196 mm pot with a 29 mm handle is
    # perfectly graspable BY THE HANDLE.
    p.update(shape_class=cls, height=height, max_horizontal=horiz, hollow=hollow,
             object_too_wide=bool(horiz > APERTURE_MAX))
    return p


# ------------------------------------------------------------- decomposition
def _decompose_elongated(points, p):
    """Split along the principal axis. The THINNER end is the graspable
    handle/shaft; the thicker end is the functional head (spoon bowl, hammer
    head, knife blade). Derived from the cloud, not from the object's name."""
    s = p["proj"][:, 0]
    lo, hi = np.percentile(s, 2), np.percentile(s, 98)
    span = hi - lo
    a, b = lo + span/3.0, lo + 2*span/3.0
    seg = {"end_a": points[s < a], "mid": points[(s >= a) & (s <= b)],
           "end_b": points[s > b]}
    def thickness(q):
        if len(q) < 10: return 1e9
        d = q - q.mean(0)
        return float(np.percentile(np.linalg.norm(d[:, 1:], axis=1), 90))
    ta, tb = thickness(seg["end_a"]), thickness(seg["end_b"])
    thin, thick = ("end_a", "end_b") if ta <= tb else ("end_b", "end_a")
    return {"handle": seg[thin], "mid": seg["mid"], "head": seg[thick]}, \
           {"handle_thickness": min(ta, tb), "head_thickness": max(ta, tb)}


def _decompose_slab(points, p):
    """Flat object (remote): the graspable feature is the pair of long sides;
    the face carries the function (buttons / IR window) and stays clear."""
    s0, s1 = p["proj"][:, 0], p["proj"][:, 1]
    q = np.percentile(s1, [10, 90])
    sides = points[(s1 < q[0]) | (s1 > q[1])]
    mid = points[(s1 >= q[0]) & (s1 <= q[1])]
    e = np.percentile(s0, [15, 85])
    return {"sides": sides, "middle": mid,
            "end_near": points[s0 < e[0]], "end_far": points[s0 > e[1]],
            "face": points[points[:, 2] > np.percentile(points[:, 2], 80)]}, {}


def _decompose_vessel(points, z_table, p):
    """Delegate to the proven mug logic when available; else a z/radius fallback."""
    try:
        from intent_grasp import part_decomposition as pd
        parts, stats = pd.classify_parts(points, z_table)
        return {k: v for k, v in parts.items() if len(v)}, dict(stats or {})
    except Exception:
        z = points[:, 2]; ztop = float(np.percentile(z, 98))
        axis = points[:, :2].mean(0)
        r = np.linalg.norm(points[:, :2] - axis, axis=1); rout = float(np.percentile(r, 95))
        rim = points[(z > ztop - 0.015) & (r > 0.7*rout)]
        interior = points[(z > ztop - 0.03) & (r <= 0.7*rout)]
        body = points[(z <= ztop - 0.015) & (r > 0.6*rout)]
        handle = points[r > 1.05*rout]
        return {k: v for k, v in dict(rim=rim, interior=interior, body=body,
                                      handle=handle).items() if len(v)}, {}


def decompose(points, z_table=None, shape=None):
    """Shape-adaptive decomposition -> (parts dict, info dict)."""
    p = shape or classify_shape(points, z_table)
    cls = p["shape_class"]
    if cls == "elongated":
        parts, extra = _decompose_elongated(points, p)
    elif cls == "slab":
        parts, extra = _decompose_slab(points, p)
    elif cls in ("vessel", "wide_vessel"):
        if z_table is None:
            z_table = float(np.percentile(points[:, 2], 2))
        parts, extra = _decompose_vessel(points, z_table, p)
    else:
        s = p["proj"][:, 0]
        parts = {"whole": points,
                 "near_half": points[s < np.median(s)],
                 "far_half": points[s >= np.median(s)]}
        extra = {}
    parts = {k: v for k, v in parts.items() if v is not None and len(v) >= 15}
    info = dict(shape_class=cls, extent=p["extent"], linearity=round(p["linearity"], 3),
                object_too_wide=p["object_too_wide"], max_horizontal=round(p["max_horizontal"], 3),
                available=sorted(parts), **extra)
    return parts, info


# ------------------------------------------------------- semantic part match
SYNONYMS = {
    "handle": ("handle", "grip", "shaft", "stem", "haft", "hand", "holder", "arm"),
    "mid":    ("middle", "mid", "centre", "center", "middle section", "midsection",
               "central", "shaft", "side", "sides"),
    "head":   ("head", "bowl", "blade", "tip", "end", "scoop", "business end"),
    "sides":  ("side", "sides", "lateral", "edge", "edges", "flank"),
    "rim":    ("rim", "lip", "opening", "mouth", "top edge", "brim"),
    "body":   ("body", "wall", "surface", "exterior", "outside", "barrel", "side wall"),
    "interior": ("interior", "inside", "inner", "cavity"),
    "face":   ("face", "front", "front panel", "buttons", "keypad", "top face"),
    "middle": ("middle", "mid", "centre", "center", "middle section"),
}


def match_part(vlm_part, parts, keep_clear=None):
    """Map free-text VLM part name onto an available geometric part.

    Returns (part_name, points, note). Falls back to the largest graspable part
    rather than failing, and never returns a part named in keep_clear.
    """
    avail = {k: v for k, v in parts.items() if len(v) >= 15}
    if not avail:
        return None, None, "no geometric parts with enough points"
    kc = {str(s).lower().strip() for s in (keep_clear or [])}

    def blocked(name):
        for k in kc:
            if k and (k in name.lower() or name.lower() in k
                      or any(k in s for s in SYNONYMS.get(name, ()))):
                return True
        return False

    want = (vlm_part or "").lower().strip()
    # 1. exact / substring on the geometric names themselves
    for name in avail:
        if want and (want == name.lower() or want in name.lower() or name.lower() in want):
            if not blocked(name):
                return name, avail[name], "direct name match '%s'" % want
    # 2. synonym families
    for canon, words in SYNONYMS.items():
        if want and any(w in want for w in words):
            for name in avail:
                if name.lower() == canon or canon in name.lower() \
                   or any(w in name.lower() for w in words):
                    if not blocked(name):
                        return name, avail[name], \
                               "matched '%s' -> '%s' via synonym family '%s'" % (want, name, canon)
    # 3. fallback: prefer a part the gripper can actually close on
    free = [(k, v) for k, v in avail.items() if not blocked(k) and k != "whole"]
    if not free:
        return None, None, "every available part is in keep_clear %s" % sorted(kc)
    graspable = [(len(v), k) for k, v in free
                 if part_width(v) + 0.02 <= APERTURE_MAX]
    if graspable:
        graspable.sort(reverse=True)
        name = graspable[0][1]
        return name, avail[name], \
            "NO MATCH for '%s' among %s -- fell back to largest GRASPABLE part '%s'" \
            % (want, sorted(avail), name)
    widest = sorted(((part_width(v), k) for k, v in free))[0]
    return None, None, \
        ("NO GRASPABLE PART for '%s': every candidate exceeds the %.0f mm aperture "
         "(narrowest is '%s' at %.0f mm). A different approach direction or a "
         "finer decomposition is required." % (want, APERTURE_MAX*1e3, widest[1],
                                               widest[0]*1e3))


def part_width(points, approach=(0, 0, -1)):
    """Minimum closing width of a part: smallest extent perpendicular to the
    approach axis. This is what the aperture gate must be applied to."""
    P = np.asarray(points, float)
    a = np.asarray(approach, float); a = a / (np.linalg.norm(a) or 1)
    X = P - P.mean(0)
    X = X - np.outer(X @ a, a)                    # drop the approach component
    w, V = np.linalg.eigh(np.cov(X.T))
    proj = X @ V[:, np.argsort(w)]
    e = [float(np.percentile(proj[:, i], 98) - np.percentile(proj[:, i], 2))
         for i in range(proj.shape[1])]
    e = sorted(x for x in e if x > 1e-6)
    return float(e[0]) if e else 0.0


# =====================================================================
#  Structural components  (open-vocabulary part binding)
# =====================================================================
r"""
The decomposition above emits a FIXED vocabulary (rim/body/handle, or
handle/mid/head). The VLM emits an OPEN one -- measured on real captures:
"handle", "sides", "middle section", "body", "front panel". Add a lid and it
will say "lid", "knob", "lid handle". A synonym table cannot keep up, and the
mismatch is the reason select_part_from_target could not bind the remote's
"middle section" to anything.

find_components() instead reports parts by their GEOMETRIC RELATION to the main
mass -- lateral_protrusion, top_protrusion, rim_ring, main_body, axis segments --
each with measured position, size and closing width. Those relations are
object-independent: a pot's side handle, a mug's handle and a saucepan's stick
handle are all "lateral protrusion"; a pot's lid knob and a kettle's lid knob are
both "top protrusion". Binding then works on WHERE the part is and HOW BIG it is,
which is what the gripper actually cares about, with the word list as a hint
rather than the mechanism.
"""


def find_components(points, z_table=None, min_pts=25):
    """Decompose into structural components named by geometric relation.

    Returns {name: points}. Names are relational, not semantic:
        main_body          the dominant mass
        rim_ring           thin ring at the top outer edge (open vessels)
        top_protrusion_k   sticks up above the main top surface (lid knob, cap)
        lateral_protrusion_k  sticks out sideways beyond the body radius (handle, spout)
        segment_near/mid/far  along the principal axis (elongated objects)
    """
    P = np.asarray(points, float)
    if z_table is None:
        z_table = float(np.percentile(P[:, 2], 2)) - 0.002
    P = P[P[:, 2] > z_table + 0.005]
    if len(P) < min_pts:
        return {}, {}
    comp, info = {}, {}

    axis_xy = np.median(P[:, :2], axis=0)
    r = np.linalg.norm(P[:, :2] - axis_xy, axis=1)
    z = P[:, 2]
    r_body = float(np.percentile(r, 85))
    z_top = float(np.percentile(z, 97))
    z_bot = float(z.min())
    height = z_top - z_bot

    # --- main body: the dominant radial mass
    body_m = (r <= r_body * 1.05) & (z <= z_top - 0.006)
    if body_m.sum() >= min_pts:
        comp["main_body"] = P[body_m]

    # --- rim ring: thin band at the top, at the outer radius
    rim_m = (z > z_top - 0.018) & (r > 0.70 * r_body) & (r <= r_body * 1.15)
    if rim_m.sum() >= min_pts:
        ring = P[rim_m]
        rr = np.linalg.norm(ring[:, :2] - axis_xy, axis=1)
        ang = np.arctan2(ring[:, 1] - axis_xy[1], ring[:, 0] - axis_xy[0])
        # a real rim is (a) hollow, (b) roughly constant radius, and (c) spread
        # over a wide arc. A flat slab satisfies (a) alone -- the TV remote grew
        # a 191 mm "rim_ring" (23 Jul) before these two extra tests were added.
        radial_cv = float(rr.std() / max(rr.mean(), 1e-6))
        arc = float(np.ptp(np.sort(ang)))
        occupied = len(set(np.digitize(ang, np.linspace(-np.pi, np.pi, 13)).tolist()))
        if (float(rr.mean()) > 0.55 * float(rr.max()) and radial_cv < 0.30
                and occupied >= 6):
            comp["rim_ring"] = ring

    # --- top protrusions: above the main top surface, near the axis (lid knob)
    top_m = (z > z_top - 0.004)
    if top_m.sum() > 10:
        z_surface = float(np.percentile(P[P[:, 2] > z_top - 0.05][:, 2], 60))
        knob_m = (z > z_surface + 0.012) & (r < 0.6 * r_body)
        if knob_m.sum() >= min_pts:
            comp["top_protrusion"] = P[knob_m]

    # --- lateral protrusions: beyond the body radius (handle, spout)
    lat_m = r > r_body * 1.18
    if lat_m.sum() >= min_pts:
        lat = P[lat_m]
        try:
            from scipy import ndimage  # noqa
            from sklearn.cluster import DBSCAN
            lab = DBSCAN(eps=0.025, min_samples=12).fit_predict(lat[:, :2])
        except Exception:
            ang = np.arctan2(lat[:, 1] - axis_xy[1], lat[:, 0] - axis_xy[0])
            lab = (np.digitize(ang, np.linspace(-np.pi, np.pi, 9)) - 1)
        k = 0
        for u in sorted(set(lab.tolist())):
            if u < 0:
                continue
            grp = lat[lab == u]
            if len(grp) >= min_pts:
                comp["lateral_protrusion" + ("" if k == 0 else "_%d" % k)] = grp
                k += 1

    # --- axis segments for elongated objects
    p = pca(P)
    if p["extent"][0] > 2.2 * max(p["extent"][1], 1e-6):
        s = p["proj"][:, 0]
        lo, hi = np.percentile(s, [2, 98]); sp = hi - lo

        # np.linalg.eigh's eigenvector sign is arbitrary -- unanchored, it flips
        # segment_a/segment_c between runs on the same object geometry (the
        # documented segment_near/segment_far reversal). Anchor it the same way
        # _decompose_elongated() already does elsewhere in this file: the
        # thinner end is the graspable one (handle/shaft), so segment_a is
        # always that end, regardless of which way eigh's sign happened to fall.
        low_mask, high_mask = s < lo + sp/3, s > hi - sp/3

        def _end_thickness(mask):
            if mask.sum() < 10:
                return 1e9
            return float(np.percentile(np.linalg.norm(p["proj"][mask, 1:], axis=1), 90))

        if _end_thickness(low_mask) > _end_thickness(high_mask):
            s = -s
            lo, hi = -hi, -lo

        for nm, m in (("segment_a", s < lo + sp/3),
                      ("segment_b", (s >= lo + sp/3) & (s <= lo + 2*sp/3)),
                      ("segment_c", s > lo + 2*sp/3)):
            if m.sum() >= min_pts:
                comp[nm] = P[m]

    info = dict(axis_xy=axis_xy, r_body=round(r_body, 4), z_top=round(z_top, 4),
                height=round(height, 4), z_table=round(float(z_table), 4),
                n_points=len(P))
    return comp, info


def describe_components(comp, info, approach=(0, 0, -1)):
    """Measured description of every component -- position relative to the object,
    size, closing width, and whether the gripper can close on it. This is what a
    VLM can bind an open-vocabulary part name against, and what a human reads in
    the log to see why a part was chosen."""
    out = {}
    if not comp:
        return out
    all_pts = np.vstack(list(comp.values()))
    ctr = all_pts.mean(0)
    z_top = float(np.percentile(all_pts[:, 2], 98))
    z_bot = float(all_pts[:, 2].min())
    H = max(z_top - z_bot, 1e-6)
    for name, pts in comp.items():
        c = pts.mean(0)
        w = part_width(pts, approach)
        ext = pca(pts)["extent"]
        rel_h = (c[2] - z_bot) / H
        # evidence: a component measured from very few points, or narrower than
        # the depth sensor can resolve at ~1 m, is not a trustworthy target.
        # (23 Jul: the pot handle was seen as 75 pts / 5 mm from the head view --
        # geometrically "graspable" but physically an occluded sliver.)
        evidence = "ok"
        if len(pts) < 120 or w < 0.010:
            evidence = "LOW"
        if len(pts) < 60 or w < 0.006:
            evidence = "NOISE"
        out[name] = dict(
            n=len(pts), evidence=evidence, centroid=np.round(c, 3).tolist(),
            height_fraction=round(float(rel_h), 2),
            radial_offset_mm=round(float(np.linalg.norm(c[:2] - ctr[:2])) * 1e3),
            size_mm=[round(e * 1e3) for e in ext],
            closing_width_mm=round(w * 1e3),
            graspable=bool(w + 0.02 <= APERTURE_MAX),
            where=("top" if rel_h > 0.75 else "upper" if rel_h > 0.5
                   else "middle" if rel_h > 0.25 else "lower"))
    return out


# hints only -- binding is decided by geometry, these bias the choice
RELATION_HINTS = {
    "lateral_protrusion": ("handle", "grip", "haft", "spout", "ear", "lug", "arm"),
    "top_protrusion":     ("lid", "knob", "cap", "cover", "button",
                           "lid knob", "stopper"),
    "rim_ring":           ("rim", "lip", "mouth", "opening", "brim", "top edge"),
    "main_body":          ("body", "side", "sides", "wall", "barrel", "exterior",
                           "surface", "middle", "centre", "center"),
    "segment_b":          ("middle", "mid", "middle section", "shaft", "centre",
                           "center", "sides", "side"),
}


def bind_part(vlm_part, comp, desc, keep_clear=None, prefer_graspable=True,
              linearity=None, min_linearity_for_segments=0.60):
    """Bind an open-vocabulary VLM part name to a structural component.

    Scores each component by: hint-word overlap, whether it is graspable, and
    (as a tie-break) size. Returns (name, points, score, note). Never returns a
    component the constraints say to keep clear.
    """
    want = (vlm_part or "").lower().strip()
    kc = [str(s).lower().strip() for s in (keep_clear or []) if s]

    def is_blocked(name):
        hints = RELATION_HINTS.get(name.rstrip("_0123456789"), ())
        for k in kc:
            if k and (k in name.lower() or any(k in h or h in k for h in hints)):
                return True
        return False

    scored = []
    for name, pts in comp.items():
        if is_blocked(name):
            continue
        d = desc.get(name, {})
        base = name.rstrip("_0123456789")
        hints = RELATION_HINTS.get(base, ())
        # segment_* names come from splitting along the principal axis, which is
        # only meaningful for a genuinely elongated object. A partial view of a
        # pot can read as "elongated" (linearity 0.45, 23 Jul) and then bind
        # "handle" to segment_near -- which was the lid. Suppress the semantic
        # hints for segments when linearity does not support them.
        if base.startswith("segment") and linearity is not None \
                and linearity < min_linearity_for_segments:
            hints = ()
        s = 0.0
        hint = 0.0
        if want:
            if any(h == want for h in hints):        hint = 5.0
            elif any(h in want or want in h for h in hints): hint = 3.0
        s += hint
        if d.get("graspable"):                        s += 2.0
        elif prefer_graspable:                        s -= 3.0
        ev = d.get("evidence", "ok")
        if ev == "LOW":                               s -= 2.5
        elif ev == "NOISE":                           s -= 6.0
        s += min(len(pts) / 2000.0, 0.8)              # mild size tie-break
        scored.append((s, name, pts, d, hint))
    if not scored:
        return None, None, 0.0, "all components blocked by keep_clear %s" % kc
    # If any component actually MATCHES the requested part name, the answer must
    # come from that set -- substituting an unrelated component changes what the
    # robot does. (23 Jul: with the pot's real handle rejected as NOISE, "handle"
    # fell through to the lid knob, i.e. remove-the-lid instead of carry-the-pot.)
    matched = [t for t in scored if t[4] > 0]
    if matched:
        matched.sort(key=lambda t: -t[0])
        s, name, pts, d, _h = matched[0]
        if not d.get("graspable") or d.get("evidence") == "NOISE":
            return None, None, s, (
                "the component matching '%s' is %s (%s, %d mm, %d pts) -- not "
                "usable, and substituting a different part would change the task"
                % (want, name, d.get("evidence"), d.get("closing_width_mm", -1), len(pts)))
        ev = d.get("evidence", "ok")
        return name, pts, s, ("bound '%s' -> %s (%s of the object, %d mm wide, "
                              "%d pts, evidence %s, score %.1f)"
                              % (want, name, d.get("where"),
                                 d.get("closing_width_mm", -1), len(pts), ev, s))
    scored.sort(key=lambda t: -t[0])
    s, name, pts, d, _h = scored[0]
    if not d.get("graspable"):
        return None, None, s, ("best match '%s' has closing width %s mm > aperture; "
                               "no graspable component for '%s'"
                               % (name, d.get("closing_width_mm"), want))
    ev = d.get("evidence", "ok")
    note = ("bound '%s' -> %s (%s of the object, %d mm wide, %d pts, evidence %s, "
            "score %.1f)" % (want, name, d.get("where"),
                             d.get("closing_width_mm", -1), len(pts), ev, s))
    if ev == "NOISE":
        return None, None, s, note + " -- REJECTED: below the sensor's evidence floor"
    return name, pts, s, note
