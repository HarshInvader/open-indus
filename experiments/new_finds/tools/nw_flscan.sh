#!/bin/bash
# usage: nw_flscan.sh outdir start end [size]  -- fetch Frontline migration_catalog images by sequential id
out="$1"; a="$2"; b="$3"; size="${4:-FREE_320}"
mkdir -p "$out"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
for ((i=a; i<=b; i++)); do
  curl -s -A "$UA" -o "$out/$i.webp" "https://fl-i.thgim.com/public/migration_catalog/article$i.ece/alternates/$size/x" &
  if (( (i - a) % 8 == 7 )); then wait; fi
done
wait
for f in "$out"/*.webp; do
  if ! file -b "$f" | grep -q "Web/P"; then rm -f "$f"; fi
done
ls "$out" | wc -l
