#!/bin/bash
# usage: wb.sh <original-url> <outfile> [timestamp]  -- fetch nearest Wayback capture (raw, id_)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
url="$1"; out="$2"; ts="${3:-2024}"
curl -sL -m 120 -A "$UA" -o "$out" -w "%{http_code} %{size_download} " "https://web.archive.org/web/${ts}id_/$url"
file -b "$out" | cut -c1-60
