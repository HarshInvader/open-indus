"""Fetch helpers for single pages of archive.org scans (no whole-volume downloads).
All downloads go to experiments/plate_corpus/raw/<item>/ and are treated as untrusted image data.
CLI:  python -I pcfetch.py thumbs ITEM START END [WIDTH]   -> raw/<item>/thumbs/NNNN.jpg + contact sheet in work/
      python -I pcfetch.py page ITEM IDX                   -> raw/<item>/pages/NNNN.jp2 (original JP2 from the zip)
      python -I pcfetch.py info ITEM IDX                   -> IIIF info (width/height)"""
import json, os, sys, time, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(D, "raw")
UA = {"User-Agent": "research-script"}

def get(url, t=180, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
                return r.read()
        except Exception as e:
            if getattr(e, "code", None) in (401, 403):
                raise  # never try to get around access control
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))

def members(item):
    p = os.path.join(D, "work", f"probe_{item}.json")
    j = json.load(open(p))
    return j["zip"], [m[0] for m in j["members"]], [m[1] for m in j["members"]]

def iiif_id(item, idx):
    z, names, _ = members(item)
    return urllib.parse.quote(f"{item}/{z}/{names[idx]}", safe="")

def info(item, idx):
    return json.loads(get(f"https://iiif.archive.org/image/iiif/3/{iiif_id(item, idx)}/info.json"))

def thumb(item, idx, width=300):
    d = os.path.join(RAW, item, "thumbs"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{idx:04d}_w{width}.jpg")
    if not os.path.exists(f):
        b = get(f"https://archive.org/download/{item}/page/n{idx}_w{width}.jpg")  # BookReader page API (fast)
        open(f, "wb").write(b)
    return f

def page(item, idx):
    d = os.path.join(RAW, item, "pages"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{idx:04d}.jp2")
    if not os.path.exists(f):
        z, names, _ = members(item)
        url = f"https://archive.org/download/{item}/{urllib.parse.quote(z)}/{urllib.parse.quote(names[idx])}"
        open(f, "wb").write(get(url, t=300))
    return f

def contact(item, files, out, cols=10, w=300):
    from PIL import Image, ImageDraw
    ims = [Image.open(f).convert("L").resize((w, int(w * 1.45))) for f in files]
    h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("L", (cols * w, rows * (h + 20)), 255)
    dr = ImageDraw.Draw(sheet)
    for k, (f, im) in enumerate(zip(files, ims)):
        x, y = (k % cols) * w, (k // cols) * (h + 20)
        sheet.paste(im, (x, y + 20)); dr.text((x + 4, y + 4), os.path.basename(f)[:4], fill=0)
    sheet.save(out)

if __name__ == "__main__":
    cmd, item = sys.argv[1], sys.argv[2]
    if cmd == "thumbs":
        a, b = int(sys.argv[3]), int(sys.argv[4]); w = int(sys.argv[5]) if len(sys.argv) > 5 else 200
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(6) as ex:
            fs = list(ex.map(lambda i: thumb(item, i, w), range(a, b)))
        out = os.path.join(D, "work", f"contact_{item[:20]}_{a}_{b}.png"); contact(item, fs, out, w=w); print(out)
    elif cmd == "page":
        print(page(item, int(sys.argv[3])))
    elif cmd == "info":
        print(info(item, int(sys.argv[3])))
