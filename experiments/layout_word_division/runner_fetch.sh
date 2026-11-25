#!/bin/sh
# layout_word_division: detached CDLI photo fetch (1 req/s). Launched by the coordinator.
# Usage, from the repo root:
#   nohup perl -e 'use POSIX qw(setsid); setsid() or die; exec @ARGV' sh experiments/layout_word_division/runner_fetch.sh STAGE_DIR >> experiments/layout_word_division/run.log 2>&1 < /dev/null &
STAGE="$1"
[ -n "$STAGE" ] || { echo "usage: runner_fetch.sh STAGE_DIR"; exit 2; }
echo $$ > experiments/layout_word_division/fetch.pid
echo "HEARTBEAT $(date -u +%Y-%m-%dT%H:%M:%SZ) stage=fetch_start"
nice -n 10 .venv/bin/python -I experiments/layout_word_division/make_crops.py fetch --stage "$STAGE"; RC=$?
echo "HEARTBEAT $(date -u +%Y-%m-%dT%H:%M:%SZ) stage=fetch_end rc=$RC"
rm -f experiments/layout_word_division/fetch.pid
