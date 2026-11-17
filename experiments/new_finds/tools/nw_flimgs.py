"""List images + captions in a saved Frontline/Hindu HTML page. Usage: python -I nw_flimgs.py page.html"""
import re, sys, html

t = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
seen = set()
for m in re.finditer(r"<img[^>]+>|<source[^>]+>", t):
    tag = m.group(0)
    alt = re.search(r'alt="([^"]*)"', tag)
    urls = re.findall(r'(?:srcset|data-original|src|data-src)="([^"]+)"', tag)
    urls = [u for u in urls if "thgim" in u]
    if not urls:
        continue
    base = re.sub(r"/alternates/[^/]+/", "/alternates/FREE_1200/", urls[0].split(" ")[0])
    if base in seen:
        continue
    seen.add(base)
    print(base, "|", html.unescape(alt.group(1))[:200] if alt else "")
