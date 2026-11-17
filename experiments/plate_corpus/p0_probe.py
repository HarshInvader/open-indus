"""P0: probe archive.org scans of the plate volumes without downloading whole volumes.
For each item: list the JP2 zip members (archive.org serves a listing of the zip) and their sizes.
Downloaded text is parsed in memory only. Usage: python -I p0_probe.py ITEM [ITEM ...]
Writes work/probe_<item>.json (member names + sizes)."""
import json, os, re, sys, html, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "research-script"}
def get(url, t=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
        return r.read()
def members(item):
    meta = json.loads(get(f"https://archive.org/metadata/{item}"))
    z = [f for f in meta["files"] if f["name"].endswith("_jp2.zip")]
    if not z: return meta, None, []
    zn = z[0]["name"]
    page = get(f"https://archive.org/download/{item}/{urllib.parse.quote(zn)}/").decode("utf8", "replace")
    out = []
    for m in re.finditer(r'<tr><td><a href="([^"]+?\.jp2)">[^<]*</a>.*?<td id="size">(\d+)', page, re.S):
        out.append((html.unescape(urllib.parse.unquote(m.group(1).split('.zip/', 1)[1])), int(m.group(2))))
    return meta, zn, out, None
if __name__ == "__main__":
    os.makedirs(os.path.join(D, "work"), exist_ok=True)
    for item in sys.argv[1:]:
        r = members(item)
        meta, zn, out = r[0], r[1], r[2]
        sub = r[3] if len(r) > 3 else None
        sizes = [s for _, s in out if s]
        print(item, "| ppi", meta.get("metadata", {}).get("ppi"), "| pages", len(out),
              "| median KB/page", (sorted(sizes)[len(sizes)//2] // 1024) if sizes else None, "| subdir", sub)
        json.dump(dict(item=item, zip=zn, subdir=sub, ppi=meta.get("metadata", {}).get("ppi"), members=out),
                  open(os.path.join(D, "work", f"probe_{item}.json"), "w"), indent=0)
