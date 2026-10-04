# Batch scene analysis — pipeline generality across captured objects

Each row is one head-camera capture driven through the unmodified pipeline
(`adapt_real_capture` → `run_grounding_grasp` → `export_grasps_plain` →
`grasp_close_params`), plus an offline PCA pass on the object cloud.

| scene | object | part | keep_clear | motion | shape | lin | long | minor | >aperture | roll | width med | force | close_z | lift |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TV_remote | TV remote control | middle section | - | handover | elongated | 0.92 | 190mm | 13mm | - | YES (31.6°) | 36mm | gentle | 0.4685 | 0.1 |
| cluster_mug_cokecan_pot | pot | handle | - | translate | compact | 0.39 | 171mm | 46mm | - | - (41.2°) | 14mm | firm | 0.5203 | 0.1 |
| cluster_mug_remote_pot | TV remote control | middle section | - | handover | compact | 0.26 | 180mm | 73mm | - | - (61.6°) | 92mm | gentle | 0.5104 | 0.1 |
| metal_spoon | spoon | handle | - | translate | compact | 0.5 | 26mm | 9mm | - | - (71.5°) | 26mm | standard | 0.4598 | 0.1 |
| pot_with_handle_and_lid | pot | handle | - | translate | compact | 0.43 | 196mm | 147mm | YES | - (49.5°) | 17mm | firm | 0.5189 | 0.1 |

## Per-scene wrist-roll decision

- **TV_remote**: elongated part: rotating closing axis 31.6 deg to close acro
- **cluster_mug_cokecan_pot**: part is compact (linearity 0.39) -- closing direction is not
- **cluster_mug_remote_pot**: part is compact (linearity 0.26) -- closing direction is not
- **metal_spoon**: part is compact (linearity 0.50) -- closing direction is not
- **pot_with_handle_and_lid**: part is compact (linearity 0.43) -- closing direction is not
