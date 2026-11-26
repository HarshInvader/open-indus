#!/bin/sh
cd "$(dirname "$0")/../../.." || exit 1
nice -n 20 .venv/bin/python -I experiments/stamp_detector/harvest.py imglist experiments/stamp_detector/raw/list_eye_pool.txt > experiments/stamp_detector/raw/h_pool.log 2>&1
grep -E "budget" experiments/stamp_detector/raw/h_pool.log
n=0; while read l; do [ -f "$l" ] || n=$((n+1)); done < experiments/stamp_detector/raw/list_eye_pool.txt; echo missing $n
