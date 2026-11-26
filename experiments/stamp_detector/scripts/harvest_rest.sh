#!/bin/sh
# Finish OB records, then the late-period training negatives. One request per second throughout.
cd "$(dirname "$0")/../../.." || exit 1
P="nice -n 20 .venv/bin/python -I experiments/stamp_detector/harvest.py records"
L=experiments/stamp_detector/raw/h_ob3.log
$P ob "Old Babylonian" 7000 > $L 2>&1
$P nb "Neo-Babylonian" 250 >> $L 2>&1
$P ach "Achaemenid" 250 >> $L 2>&1
$P hel "Hellenistic" 200 >> $L 2>&1
grep -E "ids|budget" $L
wc -l experiments/stamp_detector/raw/records_ob.jsonl experiments/stamp_detector/raw/records_nb.jsonl experiments/stamp_detector/raw/records_ach.jsonl experiments/stamp_detector/raw/records_hel.jsonl
