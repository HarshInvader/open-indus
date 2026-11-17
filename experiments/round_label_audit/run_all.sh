#!/bin/bash
# run from repo root: bash experiments/round_label_audit/run_all.sh
cd "$(dirname "$0")/../.."
export PYTHONHASHSEED=0
L=experiments/round_label_audit/logs; mkdir -p $L
S="experiments/context/q4_gulf.py experiments/context/q4b_gulf_internal.py experiments/redteam/r4_gulf.py experiments/typology/q2_gulf.py experiments/round_label_audit/d_gulf.py experiments/foreign_corpus/score.py experiments/redteam_foreign/attack.py experiments/name_structure/compare.py experiments/foreign_final_numerals/test.py"
for v in old new; do
  for s in $S; do
    n=$(basename $(dirname $s))_$(basename $s .py)
    ( .venv/bin/python -I experiments/round_label_audit/runner.py $v $s > $L/${n}_$v.log 2>&1; echo "exit $?" >> $L/${n}_$v.log ) &
  done
done
wait
echo ALL DONE
