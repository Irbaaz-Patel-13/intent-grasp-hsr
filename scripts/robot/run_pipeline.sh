#!/usr/bin/env bash
# run_pipeline.sh -- turnkey: grasps+cloud -> collision-aware placement -> preflight GO/NO-GO.
# Usage: ./run_pipeline.sh grasps_plain.npz fused_cloud.npz [out_prefix]
set -euo pipefail
GR="${1:-grasps_plain.npz}"; CL="${2:-fused_cloud.npz}"; OUT="${3:-place_run}"; URDF="hsrb.urdf"

for f in "$URDF" "$GR" "$CL" hsr_base_placement.py hsr_preflight.py execute_place_grasp_raw.py; do
  [ -f "$f" ] || { echo "MISSING: $f"; exit 1; }
done

echo ">> [1/3] reading affordance center from $GR"
AFF=$(python3 -c "import numpy as np; d=np.load('$GR',allow_pickle=True); a=d['aff_center_3d'] if 'aff_center_3d' in d.files else np.asarray(d['poses'])[:,:3,3].mean(0); print('%.4f,%.4f,%.4f'%(a[0],a[1],a[2]))")
echo "   aff = $AFF"

echo ">> [2/3] collision-aware base placement -> ${OUT}.csv"
python3 hsr_base_placement.py --urdf "$URDF" --grasps "$GR" --frame base_link \
    --cloud "$CL" --aff "$AFF" --out_prefix "$OUT"

echo ">> [3/3] pre-flight GO/NO-GO (auto-picks safest grasp)"
set +e
python3 hsr_preflight.py --urdf "$URDF" --grasps "$GR" --cloud "$CL" --csv "${OUT}.csv"
RC=$?
set -e
echo ""
if [ $RC -eq 0 ]; then
  echo "PIPELINE OK -> rehearse in sim next:  see the 'run:' line above, then drop --sim for the real grasp."
else
  echo "PIPELINE NO-GO -> fix the FAIL line above before touching the robot."
fi
exit $RC
