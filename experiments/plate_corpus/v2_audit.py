"""v2 step 1: audit every archive.org upload of the four plate volumes for REAL detail.

For each candidate upload (listed in CANDIDATES, from the v1 title search; probe JSONs in work/), the N
largest JP2 members are taken as likely photo-plate pages (photos compress worse than text). Each page
is fetched once into raw/v2/<item>/pages/ (new dir; untrusted image data, only decoded, never executed)
and measured with v2_effres on the 1024x1024 tile with the most detail:
  mode, mid-tone fraction (bitonal check), block-grid period and ratio, effective enlargement factor.
Real paper resolution = page px width / eff_factor / page width in inches (page width in inches from the
item's stated ppi; this is the nominal geometry and is only used to put uploads on one scale).
Also runs the controls that calibrate eff_factor.
Outputs: work/v2_scan_audit.csv, work/v2_audit_pages/<item>_<idx>.png (small previews to confirm a plate)
Run: .venv/bin/python -I experiments/plate_corpus/v2_audit.py [N]
"""
import csv, json, os, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import pcfetch
from v2_effres import measure

Image.MAX_IMAGE_PIXELS = 400_000_000
RAW2 = os.path.join(D, "raw", "v2")
CANDIDATES = {
    "Mackay1938_FEM": ["in.gov.ignca.9954", "furtherexcavationsatmohenjodaro192731vol2ejhmackay_191_N",
                       "in.ernet.dli.2015.57013", "dli.jZY9lup2kZl6TuXGlZQdjZM9k0Iy.TVA_BOK_0009130",
                       "dli.ernet.426189", "in.ernet.dli.2015.440862"],
    "Vats1940_EH": ["dli.ministry.25730", "excavationsatharappamadhosarupvatsvol2alt_435_p",
                    "excavationsatharappamadhosarupvatsvol2alt1_617_R", "in.ernet.dli.2015.106332",
                    "in.ernet.dli.2015.210462", "in.ernet.dli.2015.358921", "in.ernet.dli.2015.358923",
                    "in.ernet.dli.2015.426170", "in.ernet.dli.2015.537391"],
    "Mackay1943_CE": ["dli.ministry.25495", "chanhudaroexcavations193536emackay_184_y", "in.ernet.dli.2015.105167",
                      "in.gov.ignca.27263", "BK001064ChanhuDaroExcavations193536AmericanOrientalSeriesVol201943AmericanOrientalSociety",
                      "nufj-chanhu-daro-excavations-1935-36-by-ernest-j-h-mack"],
    "Marshall1931_MIC": ["in.gov.ignca.48270", "in.ernet.dli.2015.96024", "in.ernet.dli.2015.441817",
                         "mohenjodaroandtheinduscivilizationvol3jmarshalled1931_292_u",
                         "xSFp_mohenjodaro-and-the-indus-civilization-by-john-marshall-edited-by-sir-john-marsh",
                         "dli.ministry.25759"],
}


def probe(item):
    return json.load(open(os.path.join(D, "work", f"probe_{item}.json")))


def fetch_page(item, idx):
    d = os.path.join(RAW2, item, "pages"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{idx:04d}.jp2")
    if not os.path.exists(f):
        j = probe(item)
        name = j["members"][idx][0]
        url = f"https://archive.org/download/{item}/{urllib.parse.quote(j['zip'])}/{urllib.parse.quote(name)}"
        b = pcfetch.get(url, t=300)
        open(f + ".part", "wb").write(b); os.replace(f + ".part", f)
    return f


def best_tile(g, t=1024):
    H, W = g.shape
    best, bx = -1, (0, 0)
    for y in range(0, max(1, H - t), t // 2):
        for x in range(0, max(1, W - t), t // 2):
            s = g[y:y + t, x:x + t]
            v = float(np.abs(np.diff(s.astype(np.int16), axis=1)).mean())
            mid = float(((s > 40) & (s < 215)).mean())
            sc = v * (0.2 + mid)  # prefer photo areas over pure text
            if sc > best:
                best, bx = sc, (x, y)
    return bx


def audit_page(vol, item, idx, ppi):
    f = fetch_page(item, idx)
    im = Image.open(f); mode = im.mode
    g = np.asarray(im.convert("L"))
    H, W = g.shape
    x, y = best_tile(g)
    m = measure(Image.fromarray(g[y:y + 1024, x:x + 1024]))
    os.makedirs(os.path.join(D, "work", "v2_audit_pages"), exist_ok=True)
    pv = Image.fromarray(g); pv.thumbnail((500, 500))
    pv.save(os.path.join(D, "work", "v2_audit_pages", f"{item[:40]}_{idx:04d}.png"))
    page_in = W / float(ppi) if ppi else None
    real_ppi = (W / m["eff_factor"]) / page_in if page_in else None
    return dict(volume=vol, item=item, page=idx, stated_ppi=ppi, mode=mode, W=W, H=H,
                page_midtone=round(float(((g > 40) & (g < 215)).mean()), 3), tile=f"{x} {y}",
                tile_midtone=m["midtone_frac"], grid_ratio=m["grid_ratio"], grid_period=m["grid_period"],
                eff_factor=m["eff_factor"], loss=json.dumps(m["loss"]),
                real_ppi=round(real_ppi) if real_ppi else "")


def controls():
    """Calibration: a sharp CISI crop and its enlargements."""
    out = []
    im = Image.open(os.path.join(D, "crops", "cisi_FEM_273.png")).convert("L"); w, h = im.size
    out.append(("cisi_FEM_273 as is", measure(im)["eff_factor"]))
    for k in (3, 6):
        for meth, n in ((Image.NEAREST, "nearest"), (Image.BICUBIC, "bicubic")):
            out.append((f"x{k} {n}", measure(im.resize((w * k, h * k), meth))["eff_factor"]))
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    jobs = []
    for vol, items in CANDIDATES.items():
        for item in items:
            j = probe(item)
            sizes = [m[1] for m in j["members"]]
            top = sorted(range(len(sizes)), key=lambda i: -sizes[i])[:n]
            jobs += [(vol, item, i, j.get("ppi")) for i in sorted(top)]
    with ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(fetch_page, it, i) for _, it, i, _ in jobs]
        for f in futs:
            try:
                f.result()
            except Exception as e:
                print("fetch fail", e)
    rows = []
    for vol, item, i, ppi in jobs:
        try:
            r = audit_page(vol, item, i, ppi)
        except Exception as e:
            print("audit fail", item, i, e); continue
        rows.append(r)
        print(vol, item[:34].ljust(34), i, r["mode"], r["W"], "mid", r["page_midtone"], "grid", r["grid_ratio"],
              r["grid_period"], "eff", r["eff_factor"], "real_ppi", r["real_ppi"])
    with open(os.path.join(D, "work", "v2_scan_audit.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for c in controls():
        print("control", c)


if __name__ == "__main__":
    main()
