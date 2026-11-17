"""BLIND shape step: match every Indus sign drawing against proto-cuneiform (PC) and Proto-Elamite (PE)
sign images, freeze the look-alike pairs with their PC function class and PC/PE distributional signature.

Uses NO Indus distributional data: the Indus pool is defined by frequency only (>= 5 distinct M77 texts).
PC/PE signatures come from CDLI ATF (administrative texts) only.

Run: .venv/bin/python -I experiments/protocuneiform/s1_freeze.py
Outputs: pc_pool.json, pe_pool.json, frozen_pairs.json, shape_control.json, contact_sheet.png
"""
import json, re, sys, collections
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from corpus.load import m77_texts, distinct  # noqa: E402
from pc_classes import pc_class, base, COMMODITY  # noqa: E402

NUM = re.compile(r"^(\d+|n|N)\((N\d+[^)]*)\)$")
NORM = 128
MIN_TOK = 20
rng = np.random.default_rng(20261115)

# ---------------------------------------------------------------- image handling

def thin(mask):
    """Zhang-Suen thinning."""
    img = np.pad(mask.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = img
            p2, p3, p4 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:]
            p5, p6, p7 = P[2:, 2:], P[2:, 1:-1], P[2:, :-2]
            p8, p9 = P[1:-1, :-2], P[:-2, :-2]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(x.astype(int) for x in nb)
            seq = nb + [p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(int) for i in range(8))
            c = ((p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)) if step == 0 else ((p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
            m = (P[1:-1, 1:-1] == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if m.any():
                img[1:-1, 1:-1][m] = 0
                changed = True
    return img[1:-1, 1:-1].astype(bool)


def normalise(mask):
    ys, xs = np.nonzero(mask)
    crop = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    h, w = crop.shape
    s = 100.0 / max(h, w)
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    r = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_AREA) > 60
    out = np.zeros((NORM, NORM), bool)
    y0, x0 = (NORM - nh) // 2, (NORM - nw) // 2
    out[y0:y0 + nh, x0:x0 + nw] = r
    return out


def ink_of(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        a = np.array(im.convert("RGBA")).astype(float)
        return (a[..., 3] > 127) & (a[..., :3].mean(-1) < 128)
    return np.array(im.convert("L")) < 128


def first_exemplar(ink):
    """Englund's JPGs often stack 2-4 exemplars of a sign vertically. Keep the first if the image splits
    into >=2 horizontal bands of similar width and height (rule fixed before matching)."""
    rows = ink.any(1)
    bands, cur = [], None
    for y, r in enumerate(rows):
        if r and cur is None:
            cur = y
        if not r and cur is not None:
            bands.append((cur, y)); cur = None
    if cur is not None:
        bands.append((cur, len(rows)))
    # merge bands separated by gaps < 4 px
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < 4:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    big = [b for b in merged if b[1] - b[0] >= 8]
    if len(big) >= 2:
        def width(b):
            xs = np.nonzero(ink[b[0]:b[1]].any(0))[0]
            return xs.max() - xs.min() + 1
        hs = [b[1] - b[0] for b in big]; ws = [width(b) for b in big]
        if min(hs) / max(hs) > 0.5 and min(ws) / max(ws) > 0.6:
            out = np.zeros_like(ink); out[big[0][0]:big[0][1]] = ink[big[0][0]:big[0][1]]
            return out
    return ink


def dihedral(mask):
    outs = []
    for k in range(4):
        r = np.rot90(mask, k)
        outs.append(r); outs.append(r[:, ::-1])
    return outs  # index 0 = identity


def prep(ink, all8=True):
    variants = dihedral(ink) if all8 else [ink]
    out = []
    for v in variants:
        sk = thin(normalise(v))
        dt = cv2.distanceTransform((~sk).astype(np.uint8), cv2.DIST_L2, 5)
        out.append((sk, dt))
    return out


def chamfer(a, b):
    (sa, da), (sb, db) = a, b
    return 0.5 * (db[sa].mean() + da[sb].mean())

# ---------------------------------------------------------------- pools


def pc_image(name):
    d = HERE / "raw/pc_cdli/archsigns"
    p = d / f"{name}.jpg"
    if p.exists():
        return p
    b = base(name)
    if (d / f"{b}.jpg").exists():
        return d / f"{b}.jpg"
    cands = sorted(x for x in d.glob(f"{b}~*.jpg") if "@" not in x.name)
    return cands[0] if cands else None


def pe_image(name, meta):
    if name in meta:
        return HERE / "pe_signs" / meta[name]["file"]
    b = base(name)
    if b in meta:
        return HERE / "pe_signs" / meta[b]["file"]
    cands = sorted(k for k in meta if k.startswith(b + "~") and "+" not in k)
    return HERE / "pe_signs" / meta[cands[0]]["file"] if cands else None


def script_pool(lines):
    tok, withnum, header = collections.Counter(), collections.Counter(), collections.Counter()
    for r in lines:
        signs = [t for t in r["tokens"] if t != "," and not NUM.match(t)]
        for t in set(signs):
            if t.startswith("|") or "(" in t or ")" in t or t.startswith("..."):
                continue
            tok[t] += 1
            withnum[t] += r["has_num"]
            header[t] += (r["k"] == 1 and not r["has_num"])
    return {t: {"n_lines": n, "counted_rate": withnum[t] / n, "header_rate": header[t] / n}
            for t, n in tok.items() if n >= MIN_TOK}


def main():
    # Indus pool: frequency only
    cnt = collections.Counter()
    for t in distinct(m77_texts()):
        for s in set(t["seq"]):
            if s.startswith("M"):
                cnt[s] += 1
    indus = sorted([s for s, n in cnt.items() if n >= 5], key=lambda s: int(s[1:]))
    print("Indus pool", len(indus))

    pc = script_pool(json.load(open(HERE / "pc_lines.json")))
    pe = script_pool(json.load(open(HERE / "pe_lines.json")))
    pemeta = json.load(open(HERE / "pe_signs.json"))
    for k, v in pc.items():
        v["class"] = pc_class(k); v["commodity"] = v["class"] in COMMODITY
        p = pc_image(k); v["image"] = str(p.relative_to(HERE)) if p else None
    for k, v in pe.items():
        p = pe_image(k, pemeta); v["image"] = str(p.relative_to(HERE)) if p else None
    pc = {k: v for k, v in pc.items() if v["image"]}
    pe = {k: v for k, v in pe.items() if v["image"]}
    print("PC pool", len(pc), collections.Counter(v["class"] for v in pc.values()))
    print("PE pool", len(pe))
    json.dump(pc, open(HERE / "pc_pool.json", "w"), indent=1)
    json.dump(pe, open(HERE / "pe_pool.json", "w"), indent=1)

    # shapes
    ind_sh = {s: prep(ink_of(ROOT / f"data/sign_images/{s}.png"), all8=False)[0] for s in indus}
    pc_sh = {k: prep(first_exemplar(ink_of(HERE / v["image"]))) for k, v in pc.items()}
    pe_sh = {k: prep(ink_of(HERE / v["image"])) for k, v in pe.items()}

    def dists(src):
        D8 = np.zeros((len(indus), len(src))); D1 = np.zeros_like(D8)
        keys = list(src)
        for i, s in enumerate(indus):
            for j, k in enumerate(keys):
                ds = [chamfer(ind_sh[s], v) for v in src[k]]
                D8[i, j] = min(ds); D1[i, j] = ds[0]
        return keys, D8, D1

    pck, PC8, PC1 = dists(pc_sh)
    pek, PE8, PE1 = dists(pe_sh)

    # Indus -> Indus nearest other sign (orientation preserved), for scale
    ii = np.array([[chamfer(ind_sh[a], ind_sh[b]) if a != b else np.inf for b in indus] for a in indus])

    # v2 (hubness fix, decided after viewing the v1 contact sheet, before any Indus distribution):
    # CSLS score = 2 d(i,j) - r_S(i) - r_I(j), r = mean distance to the 10 nearest of the other side.
    def csls(D):
        rS = np.sort(D, 1)[:, :10].mean(1); rI = np.sort(D, 0)[:10, :].mean(0)
        return 2 * D - rS[:, None] - rI[None, :]
    PCC, PEC = csls(PC8), csls(PE8)
    frozen = {"indus_pool": indus, "pairs": {}, "matcher": "CSLS over dihedral-min chamfer (primary); raw dihedral chamfer (secondary)"}
    for i, s in enumerate(indus):
        o8 = np.argsort(PCC[i]); e8 = np.argsort(PEC[i]); o1 = np.argsort(PC1[i]); e1 = np.argsort(PE1[i])
        frozen["pairs"][s] = {
            "pc_top3": [[pck[j], round(float(PCC[i, j]), 3), pc[pck[j]]["class"]] for j in o8[:3]],
            "pe_top3": [[pek[j], round(float(PEC[i, j]), 3)] for j in e8[:3]],
            "pc_top1_raw": [pck[int(np.argmin(PC8[i]))], round(float(PC8[i].min()), 3), pc[pck[int(np.argmin(PC8[i]))]]["class"]],
            "pe_top1_raw": [pek[int(np.argmin(PE8[i]))], round(float(PE8[i].min()), 3)],
            "pc_top1_upright": [pck[o1[0]], round(float(PC1[i, o1[0]]), 3), pc[pck[o1[0]]]["class"]],
            "pe_top1_upright": [pek[e1[0]], round(float(PE1[i, e1[0]]), 3)],
            "indus_nearest_other": [indus[int(np.argmin(ii[i]))], round(float(ii[i].min()), 3)],
        }
    # look-alike sets: best tertile of nearest distance (pre-registered)
    for tag, D in (("pc", PCC), ("pe", PEC)):
        best = D.min(1)
        thr = float(np.quantile(best, 1 / 3))
        frozen[f"{tag}_lookalike_threshold"] = thr
        frozen[f"{tag}_lookalike_set"] = [s for i, s in enumerate(indus) if best[i] <= thr]
    np.save(HERE / "dist_pc8.npy", PC8); np.save(HERE / "dist_pe8.npy", PE8)
    np.save(HERE / "csls_pc.npy", PCC); np.save(HERE / "csls_pe.npy", PEC)
    json.dump({"pc_keys": pck, "pe_keys": pek}, open(HERE / "dist_keys.json", "w"))
    json.dump(frozen, open(HERE / "frozen_pairs.json", "w"), indent=1)

    # ---- shape-matcher positive control: PC variants of one base sign should be each other's neighbours
    ctrl = {}
    for tag, sh in (("pc", pc_sh),):
        keys = list(sh); bases = [base(k) for k in keys]
        multi = [i for i, b in enumerate(bases) if bases.count(b) > 1]
        hits, exp = 0, 0.0
        for i in multi:
            d = [min(chamfer(sh[keys[i]][0], v) for v in sh[keys[j]]) if j != i else np.inf for j in range(len(keys))]
            j = int(np.argmin(d)); hits += bases[j] == bases[i]
            exp += (bases.count(bases[i]) - 1) / (len(keys) - 1)
        ctrl[tag] = {"n_signs_with_variants": len(multi), "nearest_is_same_base": hits, "chance_expected": round(exp, 2)}
    # how close are the Indus->PC look-alikes, compared with Indus->Indus nearest neighbours
    ctrl["median_nearest_indus_to_pc"] = float(np.median(PC8.min(1)))
    ctrl["median_nearest_indus_to_pe"] = float(np.median(PE8.min(1)))
    ctrl["median_nearest_indus_to_indus_upright"] = float(np.median(ii.min(1)))
    # random-shape baseline: nearest PC distance for Indus drawings after a random dihedral + shear distortion is
    # not meaningful; instead report the gap between best and 10th-best match (how 'special' the best match is)
    ctrl["median_gap_best_vs_10th_pc"] = float(np.median(np.sort(PC8, 1)[:, 9] - PC8.min(1)))
    json.dump(ctrl, open(HERE / "shape_control.json", "w"), indent=1)
    print(json.dumps(ctrl, indent=1))

    # contact sheet: 48 closest Indus-PC pairs + their PE match
    order = np.argsort(PCC.min(1))[:48]
    cell = 110; W = Image.new("RGB", (6 * 3 * cell, 8 * (cell + 18)), "white"); dr = ImageDraw.Draw(W)
    def thumb(p, crop=False):
        ink = ink_of(p)
        if crop: ink = first_exemplar(ink)
        ys, xs = np.nonzero(ink); ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        im = Image.fromarray((~ink * 255).astype(np.uint8)); im.thumbnail((cell - 14, cell - 14)); return im
    for n, i in enumerate(order):
        s = indus[i]; r, c = divmod(n, 6); x0, y0 = c * 3 * cell, r * (cell + 18)
        pj = int(np.argmin(PCC[i])); ej = int(np.argmin(PEC[i]))
        for k, (p, lab, crop) in enumerate([(ROOT / f"data/sign_images/{s}.png", s, False),
                                             (HERE / pc[pck[pj]]["image"], f"{pck[pj]} {pc[pck[pj]]['class'][:6]}", True),
                                             (HERE / pe[pek[ej]]["image"], pek[ej], False)]):
            W.paste(thumb(p, crop), (x0 + k * cell + 5, y0 + 5))
            dr.text((x0 + k * cell + 3, y0 + cell), lab[:18], fill="black")
        dr.line([(x0 + 3 * cell - 2, y0), (x0 + 3 * cell - 2, y0 + cell + 16)], fill=(180, 180, 180))
    W.save(HERE / "contact_sheet.png")


if __name__ == "__main__":
    main()
