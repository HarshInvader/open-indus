#!/bin/bash
# usage: pa_get.sh <url> <outfile>
# images: via images.weserv.nl proxy (bypasses Cloudflare block on harappa.com); other files: direct, then r.jina.ai not used for binaries
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
url="$1"; out="$2"
case "$url" in
  *.jpg|*.jpeg|*.png|*.JPG|*.gif)
    curl -sL -m 90 -A "$UA" -o "$out" -w "%{http_code} %{size_download} " "https://images.weserv.nl/?url=${url#https://}" ;;
  *)
    curl -sL -m 120 -A "$UA" -o "$out" -w "%{http_code} %{size_download} " "$url" ;;
esac
file -b "$out" | cut -c1-60
