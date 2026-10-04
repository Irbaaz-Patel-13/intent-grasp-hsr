# Hardware run: standard procedure (validated 2026-07-06)

The robot side runs inside the HSR workstation's ROS Noetic container. Copy this
folder there and run everything from inside it. Replace `<user>@<workstation>`
with your own login.

## Setup (workstation)
- Robot ~0.9-1.0 m from table edge, square on. Mug within ~15 cm of edge.
- `rm -f place_run.ref`
- `python3 go_stow.py` (arm tucked; the refine step needs a clear camera)
- head down: `python3 head_pose.py -0.60`
- `python3 capture_real.py` (GATE: depth min ~0.6-1.0)
- Base and head stay FROZEN after capture.

## PC (from `workspace/`, with the venv active)
- key check: `python -c "import os; print(os.environ.get('OPENAI_API_KEY','NOT SET')[-6:])"`
- `scp <user>@<workstation>:<robot-dir>/head_capture_real.npz .`
- `python ../scripts/pipeline/adapt_real_capture.py` (GATE: within-cloud OK)
- `python ../scripts/pipeline/run_grounding_grasp.py "pick up the mug"` (GATE: no 401)
- `python ../scripts/pipeline/export_grasps_plain.py` (GATE: aff FRESH, differs from last run)
- `python ../scripts/pipeline/grasp_close_params.py`
- `scp grasps_plain.npz fused_cloud.npz close_params.csv <user>@<workstation>:<robot-dir>/`

## Workstation
- `./run_pipeline.sh grasps_plain.npz fused_cloud.npz place_run`
  GATES: keep-out cells printed; keep-out clearance min >= 0.32; 25/25; GO grasp N
- execute dry: `python3 execute_place_grasp_raw.py --urdf hsrb.urdf --csv place_run.csv --grasp N --ref_file place_run.ref --dry`
- stage base: `... --stage base` (GATE: G1 True; hands off base)
- refine: `python3 hsr_refine_nudge.py`
  RULES: arm must be STOWED; ABORT = STOP, never proceed past a refine abort
- grasp: `... --stage grasp` (GATE: G2, then G3 held:True, then GRASP OK)
- log: `python3 log_trial.py <executor-output.txt> --note "..."` appends the run to `trials.csv`
- archive: `mkdir -p results/run_$(date +%m%d_%H%M) && cp place_run.csv place_run.ref place_run_map.png grasps_plain.npz results/run_$(date +%m%d_%H%M)/`

## Gate telemetry reference
- hand_motor: -0.8899 empty | -0.877 rim pinch | -0.276 body grip | threshold -0.885
- G3 success reads: z_rise ~0.10+, held True

## Not included on purpose
`hsr_duck.py` was retired after it drove the arm into the floor on 1 Aug 2026.
`capture_pair.py` and `capture_object.py` only call it if the file exists, so
they skip that step here.

`capture_head_for_ik.py` and `execute_region_ik.py` come from the earlier
simulator workflow and import `utils` from the Toyota WRS docker notebooks, which
isn't part of this repo.
