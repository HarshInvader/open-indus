#!/bin/sh
# Rebuild the font and screenshot the specimen in light and dark.
# Run from the project root: sh site/font/shoot.sh
set -e
cd "$(dirname "$0")"
../../.venv/bin/python -I build_font.py >/dev/null 2>&1 || ../../.venv/bin/python -I build_font.py
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL="file://$(pwd)/specimen.html"
for mode in light dark; do
  flag=""
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars $flag --virtual-time-budget=3000 \
    --window-size=1200,${H:-6740} --screenshot="$(pwd)/shots/specimen-$mode.png" "$URL#$mode" >/dev/null 2>&1
done
echo shots written
