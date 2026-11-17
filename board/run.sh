#!/bin/bash
# Team compute gate: one compute job at a time, background priority.
# Usage (from repo root): board/run.sh <command...>     e.g. board/run.sh .venv/bin/python -I experiments/x/run.py
# Waits for the lock, runs the command on efficiency cores at lowest priority, releases the lock.
LOCK="$(cd "$(dirname "$0")" && pwd)/compute.lock"
while ! mkdir "$LOCK" 2>/dev/null; do
  pid=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then rm -rf "$LOCK"; continue; fi
  echo "compute lock held by pid ${pid:-?}: $(cat "$LOCK/cmd" 2>/dev/null); waiting 20s" >&2
  /bin/sleep 20
done
echo $$ > "$LOCK/pid"; echo "$*" > "$LOCK/cmd"
trap 'rm -rf "$LOCK"' EXIT
trap 'exit 130' INT TERM
taskpolicy -b nice -n 20 "$@"
