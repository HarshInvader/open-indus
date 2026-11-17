"""Download PDF files of Zenodo records: python -I pa_zget.py outdir id1 id2 ..."""
import json
import os
import sys
import urllib.request

out = sys.argv[1]
H = {"User-Agent": "curl/8.4.0"}
for rid in sys.argv[2:]:
    try:
        req = urllib.request.Request(f"https://zenodo.org/api/records/{rid}", headers=H)
        d = json.load(urllib.request.urlopen(req, timeout=60))
        for f in d.get("files", []):
            if not f["key"].lower().endswith(".pdf"):
                continue
            dest = os.path.join(out, f"z{rid}.pdf")
            url = f["links"]["self"]
            urllib.request.urlretrieve(url, dest) if False else None
            r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300)
            with open(dest, "wb") as fh:
                fh.write(r.read())
            print(rid, dest, os.path.getsize(dest), d["metadata"]["title"][:80])
            break
    except Exception as e:
        print(rid, "ERR", e)
