"""Download archive.org OCR text (djvu.txt) for old excavation reports into raw/<id>/.
Untrusted data; only plain text is fetched. Usage: python -I fetch.py ID [ID ...]"""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}), timeout=120) as r:
        return r.read()
for ident in sys.argv[1:]:
    d = os.path.join(HERE, "raw", ident)
    if os.path.exists(d) and os.listdir(d):
        print("skip", ident); continue
    os.makedirs(d, exist_ok=True)
    meta = json.loads(get(f"https://archive.org/metadata/{ident}"))
    files = [f["name"] for f in meta.get("files", []) if f["name"].endswith("_djvu.txt")]
    title = meta.get("metadata", {}).get("title")
    pages = [f.get("name") for f in meta.get("files", []) if f["name"].endswith(".pdf")]
    with open(os.path.join(d, "SOURCE.json"), "w") as fh:
        json.dump({"identifier": ident, "title": title, "djvu": files, "pdf": pages,
                   "url": f"https://archive.org/details/{ident}"}, fh, indent=1)
    for f in files:
        b = get(f"https://archive.org/download/{ident}/{urllib.request.quote(f)}")
        open(os.path.join(d, "ocr.txt"), "wb").write(b)
        print(ident, title, len(b)); break
    else:
        print(ident, title, "NO djvu.txt")
