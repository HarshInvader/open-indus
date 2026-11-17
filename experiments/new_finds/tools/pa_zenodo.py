"""Search Zenodo: python -I pa_zenodo.py "query" [pages]  -> id year title | pdf files"""
import json
import sys
import urllib.parse
import urllib.request

q = sys.argv[1]
pages = int(sys.argv[2]) if len(sys.argv) > 2 else 2
for p in range(1, pages + 1):
    url = "https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": q, "size": 25, "page": p})
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.4.0"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=60))
    except Exception as e:
        print("ERR", e)
        break
    hits = d.get("hits", {}).get("hits", [])
    if not hits:
        break
    for h in hits:
        m = h["metadata"]
        files = [f["key"] for f in h.get("files", [])]
        print(h["id"], m.get("publication_date", "")[:4], "|", m["title"][:110], "|", ";".join(files)[:120])
