#!/bin/sh
cd "$(dirname "$0")/../../.." || exit 1
nice -n 20 .venv/bin/python -I experiments/stamp_detector/harvest.py imglist experiments/stamp_detector/raw/list_neg.txt > experiments/stamp_detector/raw/h_negimg.log 2>&1
grep -E "budget|not CC0" experiments/stamp_detector/raw/h_negimg.log | head
ls experiments/stamp_detector/raw/img | wc -l
