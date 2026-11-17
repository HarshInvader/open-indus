"""v2 helper: fetch small page thumbnails (BookReader API) into raw/v2/<item>/thumbs and make a contact sheet.
Untrusted image data, only decoded. Run: .venv/bin/python -I v2_thumbs.py ITEM START END"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import pcfetch

def thumb(item, idx, w=120):
    d = os.path.join(D, "raw", "v2", item, "thumbs"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{idx:04d}_w{w}.jpg")
    if not os.path.exists(f):
        open(f, "wb").write(pcfetch.get(f"https://archive.org/download/{item}/page/n{idx}_w{w}.jpg"))
    return f

if __name__ == "__main__":
    item, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    with ThreadPoolExecutor(4) as ex:
        fs = []
        for f in ex.map(lambda i: (lambda: thumb(item, i))() , range(a, b)):
            fs.append(f)
    out = os.path.join(D, "work", f"v2_contact_{item[:16]}_{a}_{b}.png")
    pcfetch.contact(item, fs, out, cols=10, w=120); print(out)
