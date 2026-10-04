#!/usr/bin/env python
r"""scene_objects.py -- locate the objects ON the table, not the furniture behind it.

The earlier finder took the largest connected cluster above the support plane
inside a guessed x/y window. In this lab that is the CHAIR BACK: every scene
reported the same 446 x 283 x 51 mm "object", and the overlays landed on the
chair rather than the mug (1 Aug figures).

This version derives the workspace from the data:
  1. support plane = modal z of the forward region
  2. TABLE = the largest connected patch of points lying within +/-2 cm of that
     plane -- its xy footprint defines where objects can be
  3. candidates = points above the plane whose xy falls INSIDE that footprint
  4. clusters that are too large to be a tabletop object (horizontal extent above
     --max_obj) are rejected: a graspable object is smaller than the furniture

Returns every object found, largest first, so cluttered scenes give several.
"""
import numpy as np


def _cluster(P, eps=0.02, min_samples=12):
    if len(P) < 20:
        return np.zeros(len(P), int)
    try:
        from sklearn.cluster import DBSCAN
        return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(P)
    except Exception:
        from scipy import ndimage
        v = max(eps * 0.7, 0.008)
        idx = np.floor((P - P.min(0)) / v).astype(int)
        vol = np.zeros(idx.max(0) + 3, bool)
        vol[tuple(idx.T)] = True
        cc, _ = ndimage.label(vol)
        return cc[tuple(idx.T)] - 1


def find_table(pts, x_lo=0.30, x_hi=1.60, y_half=0.70, tol=0.02):
    """Support height and the xy footprint of the surface itself."""
    fwd = pts[(pts[:, 0] > x_lo) & (pts[:, 0] < x_hi) & (np.abs(pts[:, 1]) < y_half)]
    if len(fwd) < 800:
        return None
    hh, ee = np.histogram(fwd[:, 2], bins=100)
    plane = float(0.5 * (ee[int(np.argmax(hh))] + ee[int(np.argmax(hh)) + 1]))
    surf = fwd[np.abs(fwd[:, 2] - plane) < tol]
    if len(surf) < 300:
        return None
    lab = _cluster(surf[:, :2], eps=0.03, min_samples=20)
    best, n = None, 0
    for u in set(lab.tolist()):
        if u < 0:
            continue
        g = surf[lab == u]
        if len(g) > n:
            best, n = g, len(g)
    if best is None:
        return None
    return dict(plane_z=plane, n_surface=len(best),
                x=(float(best[:, 0].min()), float(best[:, 0].max())),
                y=(float(best[:, 1].min()), float(best[:, 1].max())),
                area=float(np.ptp(best[:, 0]) * np.ptp(best[:, 1])))


def find_objects(pts, table=None, band=(0.012, 0.30), margin=0.02,
                 max_obj=0.28, min_pts=120, max_height=0.22, merge_xy=0.06):
    """Objects resting on the table surface, largest first."""
    if table is None:
        table = find_table(pts)
    if table is None:
        return None, []
    xl, xh = table["x"]; yl, yh = table["y"]; pz = table["plane_z"]
    inside = ((pts[:, 0] > xl + margin) & (pts[:, 0] < xh - margin) &
              (pts[:, 1] > yl + margin) & (pts[:, 1] < yh - margin))
    above = pts[inside & (pts[:, 2] > pz + band[0]) & (pts[:, 2] < pz + band[1])]
    if len(above) < min_pts:
        return table, []
    lab = _cluster(above, eps=0.02, min_samples=12)
    objs = []
    for u in set(lab.tolist()):
        if u < 0:
            continue
        g = above[lab == u]
        if len(g) < min_pts:
            continue
        span = max(float(np.ptp(g[:, 0])), float(np.ptp(g[:, 1])))
        if span > max_obj:                      # furniture, not a tabletop object
            continue
        h = float(g[:, 2].max() - pz)
        if h > max_height:            # struts and clipped furniture edges
            continue
        objs.append(dict(points=g, n=len(g), span=round(float(span), 3),
                         centroid=[round(float(x), 3) for x in g.mean(0)],
                         height=round(h, 3)))
    # merge fragments of the same object (depth gaps split a mug in two)
    merged = []
    for o in sorted(objs, key=lambda d: -d["n"]):
        hit = None
        for m in merged:
            d = ((o["centroid"][0]-m["centroid"][0])**2 +
                 (o["centroid"][1]-m["centroid"][1])**2) ** 0.5
            if d < merge_xy:
                hit = m
                break
        if hit is None:
            merged.append(dict(o))
            continue
        P = np.vstack([hit["points"], o["points"]])
        hit.update(points=P, n=len(P),
                   span=round(max(float(np.ptp(P[:,0])), float(np.ptp(P[:,1]))), 3),
                   centroid=[round(float(x),3) for x in P.mean(0)],
                   height=round(float(P[:,2].max()-pz), 3))
    merged.sort(key=lambda d: -d["n"])
    return table, merged


def describe(table, objs):
    if table is None:
        return "no table surface found"
    s = ("table: plane z=%.3f, x[%.2f,%.2f] y[%.2f,%.2f], %d surface pts"
         % (table["plane_z"], table["x"][0], table["x"][1],
            table["y"][0], table["y"][1], table["n_surface"]))
    if not objs:
        return s + "  -- no objects on it"
    return s + "\n" + "\n".join(
        "   object %d: %5d pts, span %.3f m, height %.3f m, centroid %s"
        % (i, o["n"], o["span"], o["height"], o["centroid"])
        for i, o in enumerate(objs))
