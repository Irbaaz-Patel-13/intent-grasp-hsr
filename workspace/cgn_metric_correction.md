# Grasp-to-affordance proximity, convention-corrected

dump: `results\cgn_candidates\candidates_unknown_20260722_165452.npz`   aff centre: [0.763, 0.062, 0.5]
```

RAW CANDIDATES (n=200)
  euclidean origin->aff (CURRENT metric) : min 0.085  p25 0.168  median 0.334  p75 0.432  max 0.510
  depth along approach (gripper offset)  : min -0.250  p25 0.109  median 0.155  p75 0.263  max 0.469
  PERPENDICULAR offset (aiming error)    : min 0.010  p25 0.114  median 0.253  p75 0.332  max 0.406
  perp < 0.02 m : 8   perp < 0.03 m : 15   perp < 0.06 m : 41

SELECTED (top 25) (n=25)
  euclidean origin->aff (CURRENT metric) : min 0.092  p25 0.112  median 0.120  p75 0.126  max 0.143
  depth along approach (gripper offset)  : min 0.085  p25 0.109  median 0.115  p75 0.121  max 0.131
  PERPENDICULAR offset (aiming error)    : min 0.010  p25 0.016  median 0.022  p75 0.037  max 0.066
  perp < 0.02 m : 11   perp < 0.03 m : 16   perp < 0.06 m : 23
```

Selected grasps miss the affordance centre by a median of 0.022 m PERPENDICULAR to the approach axis, while sitting a median of 0.115 m back along it. The current euclidean metric (median 0.120 m) is dominated by that gripper-depth offset, not by aiming error.
