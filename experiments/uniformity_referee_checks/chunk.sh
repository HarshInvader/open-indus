#!/bin/bash
# One resumable chunk of rc.py: memory guard (>= 20% free) -> compute.lock.indus -> board/run.sh -> timeout 85m.
# Usage (repo root): experiments/uniformity_referee_checks/chunk.sh <job>
set -u
JOB="$1"
cd "$(dirname "$0")/../.."
LOCK="$(cd .. && pwd)/open-citizen-science/.local/compute.lock.indus"   # sibling project directory
LOG=experiments/uniformity_referee_checks/run.log
for i in $(seq 1 90); do
  free=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}')
  [ "${free:-0}" -ge 20 ] && break
  echo "$(date -u +%FT%TZ) memory free ${free}% < 20%, waiting" >> "$LOG"; /bin/sleep 20
done
until mkdir "$LOCK" 2>/dev/null; do
  echo "$(date -u +%FT%TZ) indus lock held: $(cat $LOCK/owner 2>/dev/null)" >> "$LOG"; /bin/sleep 30
done
echo "indus uniformity_referee_checks $JOB $(date -u +%FT%TZ)" > "$LOCK/owner"
trap 'rm -rf "$LOCK"' EXIT
echo "$(date -u +%FT%TZ) start $JOB" >> "$LOG"
timeout -s INT 85m board/run.sh .venv/bin/python -I experiments/uniformity_referee_checks/rc.py run "$JOB" >> "$LOG" 2>&1
rc=$?
echo "$(date -u +%FT%TZ) end $JOB exit $rc" >> "$LOG"
exit $rc
