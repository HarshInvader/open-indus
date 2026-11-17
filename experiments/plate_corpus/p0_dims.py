"""P0b: per item, median page pixel size from the scandata.xml (no image download). Parsed in memory only.
Usage: python -I p0_dims.py ITEM [...]  -> work/dims.json (appended)"""
import json, os, re, sys, statistics as S, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcfetch import get, D
out = json.load(open(os.path.join(D, "work", "dims.json"))) if os.path.exists(os.path.join(D, "work", "dims.json")) else {}
for item in sys.argv[1:]:
    meta = json.loads(get(f"https://archive.org/metadata/{item}"))
    sd = [f["name"] for f in meta["files"] if f["name"].endswith("_scandata.xml")]
    if not sd: print(item, "no scandata"); continue
    x = get(f"https://archive.org/download/{item}/{urllib.parse.quote(sd[0])}").decode("utf8", "replace")
    ws = [int(v) for v in re.findall(r"<width>(\d+)</width>", x)]
    hs = [int(v) for v in re.findall(r"<height>(\d+)</height>", x)]
    pp = re.findall(r"<dpi>(\d+)</dpi>", x)
    r = dict(n=len(ws), w=S.median(ws) if ws else None, h=S.median(hs) if hs else None, dpi=pp[:1], ppi=meta["metadata"].get("ppi"))
    out[item] = r; print(item, r)
json.dump(out, open(os.path.join(D, "work", "dims.json"), "w"), indent=1)
