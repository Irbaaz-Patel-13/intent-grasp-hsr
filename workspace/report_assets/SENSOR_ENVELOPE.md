# Sensor-grounded resolution envelope

**Sensor:** Asus Xtion PRO Live — structured light, depth range 0.8–3.5 m, 640×480 depth,
FOV 58° H × 45° V.

Arithmetic only. No scripts run, no capture data re-read beyond the numbers supplied in
the task. Formula: at depth `d`, horizontal field width = `2·d·tan(29°)`, vertical field
height = `2·d·tan(22.5°)`; mm/px = field size ÷ pixel count (640 horizontal, 480 vertical).

## V1 — mm per pixel at each depth

`tan(29°) = 0.55431`, `tan(22.5°) = 0.41421`

| depth (m) | mm/px horizontal | mm/px vertical |
|---|---|---|
| 0.92 | 1.5936 | 1.5878 |
| 0.99 | 1.7149 | 1.7086 |
| 1.03 | 1.7842 | 1.7777 |
| 1.18 | 2.0440 | 2.0366 |
| 1.21 | 2.0960 | 2.0883 |
| 1.37 | 2.3731 | 2.3645 |
| 1.54 | 2.6676 | 2.6579 |

Horizontal and vertical mm/px are nearly identical at every depth (58°/640 ≈ 0.0906°/px vs.
45°/480 ≈ 0.0938°/px) — angular pixel density is close to isotropic for this sensor/mode.

## V2 — measured component width, mm and px, at its own capture depth

| component | width (mm) | depth (m) | mm/px at that depth | width (px) |
|---|---|---|---|---|
| knife handle | 24 | 0.913 | 1.582 | **15.18** |
| remote lateral protrusion | 18 | 0.920 | 1.594 | **11.29** |
| spoon | 20 | 0.918 | 1.590 | **12.58** |
| pot lid knob | 16 | 0.989 | 1.713 | **9.34** |
| mug handle | 4 | 0.925 | 1.602 | **2.50** |

## V3 — where NOISE sets in

`part_adaptive.describe_components()`'s own evidence rule (read directly from source,
not re-derived here) flags a component `NOISE` if its point count is under 60 **or its
measured 3D closing width is under 6 mm** — at these depths (~1.6 mm/px), 6 mm corresponds
to roughly **3.5–3.8 px**.

Of the five components above, only the **mug handle (4 mm ≈ 2.5 px)** sits below both that
6 mm/~3.7 px code threshold and the next-smallest *successfully resolved* component in this
set (pot lid knob, 16 mm ≈ 9.3 px, evidence `ok`). The other four (9.3–15.2 px) all cleared
evidence `ok` in the sessions that measured them.

This is **consistent with** the mug handle's `NOISE` classification being a genuine
pixel-resolution floor — its 2.5 px width sits below where every other measured component in
this dataset succeeded, and below the code's own 6 mm cutoff. It is **not proof**: five data
points don't establish a precise cutoff, and other factors (specular reflection on the mug's
glazed handle, occlusion angle) could also contribute. Reporting as consistent, not
confirmed.

## V4 — range-limit check

The four *healthy* near captures (knife, remote, spoon, mug — not the pot, which failed for
reasons already diagnosed as fragmentation/dropout, not range) sit at depths 0.913–0.925 m,
i.e. **0.113–0.125 m above** the sensor's 0.8 m minimum. All far captures in this dataset
(1.37–1.54 m, per the depths above) sit **1.96–2.13 m inside** the 3.5 m maximum.

**Implication:** none of these captures are anywhere near either end of the sensor's rated
range. The far-capture failures documented earlier in this audit (the pot's far-view plane
fit locking onto ~0.015 m instead of ~0.45 m; the general degradation at far range in
`range_analysis.csv`) are **not range limits** — the sensor is rated to 3.5 m and every far
capture here is under 1.6 m. Whatever is causing far-view degradation is a different failure
mode (point density, viewing angle, or the plane-fit defect already documented), not the
device running out of range.
