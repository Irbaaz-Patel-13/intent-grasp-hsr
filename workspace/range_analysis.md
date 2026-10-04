# Does a closer viewpoint resolve graspable parts?

Same object, same table, camera driven ~0.25 m closer. 'Finest part' is the
narrowest graspable structural component other than the main body -- i.e. the
handle-like feature that part-scoped grasping needs and that was previously
measured below the sensor's evidence floor (mug 48 pts / 6 mm, pot 75 / 5).

| object | depth far → near | object pts far → near | finest part pts | finest part width | evidence far → near |
|---|---|---|---|---|---|
| bowl | 1.38 → 0.94 m | 0 → 0 | 0 → 0 | 0 → 0 mm | none → none |
| cluster_mug_bowl_knife | 1.35 → 0.95 m | 2356 → 2208 | 52 → 428 **↑** | 14 → 18 mm | NOISE → ok |
| cluster_mug_can_pot | 1.54 → 1.21 m | 0 → 2269 | 0 → 43 | 0 → 3 mm | none → NOISE |
| cluster_mug_can_remote | 1.54 → 1.18 m | 412 → 2048 | 45 → 58 | 11 → 6 mm | NOISE → NOISE |
| cluster_pot_mug | 1.35 → 0.96 m | 5142 → 2509 | 173 → 338 **↑** | 7 → 15 mm | LOW → ok |
| cluster_remote_knife | 1.35 → 0.92 m | 1515 → 2742 | 120 → 30 | 31 → 5 mm | ok → NOISE |
| cluster_spoon_bowl | 1.36 → 0.95 m | 161 → 1359 | 0 → 83 | 0 → 12 mm | none → LOW |
| cluster_spoon_can_remote | 1.54 → 1.18 m | 0 → 1125 | 0 → 51 | 0 → 8 mm | none → NOISE |
| cluster_spoon_mug_knife | 1.37 → 0.92 m | 2268 → 1810 | 77 → 30 | 9 → 4 mm | LOW → NOISE |
| cluster_spoon_mug_pot | 1.38 → 1.03 m | 0 → 3510 | 0 → 171 **↑** | 0 → 12 mm | none → ok |
| knife | 1.37 → 0.91 m | 979 → 1638 | 89 → 769 **↑** | 11 → 19 mm | LOW → ok |
| mug | 1.37 → 0.93 m | 1508 → 1942 | 44 → 36 | 3 → 3 mm | NOISE → NOISE |
| mug_hv | 1.52 → 1.18 m | 400 → 656 | 153 → 42 | 88 → 6 mm | ok → NOISE |
| pot | 1.38 → 0.99 m | 134 → 3148 | 35 → 131 **↑** | 40 → 9 mm | NOISE → LOW |
| remote | 1.37 → 0.92 m | 2177 → 4677 | 67 → 284 **↑** | 9 → 18 mm | LOW → ok |
| spoon | 1.37 → 0.92 m | 0 → 2087 | 0 → 47 | 0 → 5 mm | none → NOISE |

**6 of 16 objects showed a materially better-resolved fine part at the closer viewpoint.**

Evidence classes: `ok` (>=120 pts and >=10 mm), `LOW`, `NOISE` (<60 pts or <6 mm -- rejected by the part binder).

Figures: `report_assets/figures/fig_range_<object>.png`
