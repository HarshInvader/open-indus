"""Red-team reimplementation (independent of experiments/rank_ladder code).

Builds a distinct-text table of ICIT seals with physical measurements, glyph widths,
emblem class, measurement provenance, and an own family split.
"""
import json, re, random, collections as C
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))

FEATS = {"W590": {"W590"}, "W70x": {"W704", "W705", "W706"}, "W400": {"W400"},
         "W405": {"W405"}, "W390": {"W390"}, "W741": {"W741"}}
DEV_SIGN = {"W590": -1, "W70x": +1, "W400": -1, "W405": +1, "W390": -1}  # claimed dev directions


def emblem(sym):
    if sym.startswith("Bull1"):
        return "unicorn"
    s = sym.split(":")[0]
    return {"None": "none", "-": "unknown", "Zebu": "zebu", "Gaur": "gaur", "Elep": "elephant",
            "Rhin": "rhino", "Tigr": "tiger", "Buff": "buffalo"}.get(s, "other")


# ---- glyph widths from Mahadevan drawings (drawn at a common height, widths vary) ----
_mw = {}
def m_width(n):
    if n not in _mw:
        p = ROOT / f"data/sign_images/M{n}.png"
        if not p.exists():
            _mw[n] = None
        else:
            a = np.array(Image.open(p).convert("RGBA"))
            ink = (a[..., 3] > 50) & (a[..., :3].mean(-1) < 128)
            xs = np.where(ink.any(0))[0]
            _mw[n] = float(xs.max() - xs.min() + 1) if len(xs) else None
    return _mw[n]


def w_width(w):
    b = BRIDGE.get(str(int(w[1:])))
    if not b:
        return None
    ws = [m_width(m) for m in b["M"] if m_width(m)]
    return float(np.mean(ws)) if ws else None


def load_objects():
    R = [json.loads(l) for l in open(ROOT / "data/icit_texts.jsonl")]
    return R


def is_inch(x):
    """measurement is an exact multiple of 0.05 inch (1.27 mm) but not of 0.5 mm-ish metric grid"""
    v = x / 1.27
    return abs(v - round(v)) < 0.02 and abs(x * 2 - round(x * 2)) > 0.05


def build(types=("SEAL:S",), need_both=True):
    R = load_objects()
    wid = {}
    rows = []
    for r in R:
        if r["type"] not in types:
            continue
        w, h = float(r["width_mm"]), float(r["height_mm"])
        if need_both and (w <= 0 or h <= 0):
            continue
        signs = [s for s in r["seq"] if s not in ("|", "#")]
        if not signs:
            continue
        lines = r["seq"].count("|") + 1
        gw = []
        for s in signs:
            if s not in wid:
                wid[s] = w_width(s)
            gw.append(wid[s])
        rows.append(dict(key=" ".join(r["seq"]), signs=signs, site=r["site"], w=w, h=h,
                         emb=emblem(r["symbol"]), sym=r["symbol"], complete=r["complete"],
                         lines=lines, period=r["period"], phase=r["phase"], cisi=r["cisi"],
                         material=r["material"], type=r["type"], gw=gw, inch=(is_inch(w) or is_inch(h)),
                         seq=r["seq"]))
    known = [x for x in wid.values() if x]
    med = float(np.median(known))
    for x in rows:
        x["gw"] = [g if g else med for g in x["gw"]]
        x["gw_known"] = float(np.mean([wid[s] is not None for s in x["signs"]]))
        # per-line widths
        lw, cur = [], 0.0
        i = 0
        for s in x["seq"]:
            if s == "|":
                lw.append(cur); cur = 0.0
            elif s == "#":
                continue
            else:
                cur += x["gw"][i] + 10.0; i += 1
        lw.append(cur)
        x["linew_max"] = max(lw)
        x["glyph_total"] = sum(x["gw"]) + 10.0 * len(x["gw"])
    # pool to distinct texts
    by = C.defaultdict(list)
    for x in rows:
        by[x["key"]].append(x)
    T = []
    for k, xs in by.items():
        mode = lambda f: C.Counter(x[f] for x in xs).most_common(1)[0][0]
        T.append(dict(key=k, signs=xs[0]["signs"], seq=xs[0]["seq"], n_obj=len(xs),
                      la=float(np.mean([np.log(x["w"] * x["h"]) for x in xs])),
                      lw=float(np.mean([np.log(x["w"]) for x in xs])),
                      lh=float(np.mean([np.log(x["h"]) for x in xs])),
                      aspect=float(np.mean([x["w"] / x["h"] for x in xs])),
                      site=mode("site"), emb=mode("emb"), lines=xs[0]["lines"],
                      complete=all(x["complete"] for x in xs), inch=mode("inch"),
                      period=mode("period"), phase=mode("phase"), cisi=xs[0]["cisi"],
                      material=mode("material"), glyph_total=xs[0]["glyph_total"],
                      linew_max=xs[0]["linew_max"], gw_known=xs[0]["gw_known"],
                      nsign=len(xs[0]["signs"])))
    for t in T:
        for f, ss in FEATS.items():
            t[f] = int(any(s in ss for s in t["signs"]))
    return T


# ---- own family split (edit distance <=1 or containment over sign lists) ----
def _close(a, b):
    """project near-copy rule (corpus/build.py): containment if shorter >= 3 signs;
    one edit only if both >= 4 signs."""
    if len(a) > len(b):
        a, b = b, a
    la, lb = len(a), len(b)
    if la >= 3 and lb - la >= 1:
        for i in range(lb - la + 1):
            if b[i:i + la] == a:
                return True
    if lb - la > 1 or la < 4:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def families(T):
    par = list(range(len(T)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            a, b = T[i]["signs"], T[j]["signs"]
            if _close(a, b):
                par[f(i)] = f(j)
    return [f(i) for i in range(len(T))]


def split(T, fam, seed, frac=0.3):
    rng = random.Random(seed)
    fams = C.defaultdict(list)
    for i, g in enumerate(fam):
        fams[g].append(i)
    bysite = C.defaultdict(list)
    for g, idx in fams.items():
        site = C.Counter(T[i]["site"] for i in idx).most_common(1)[0][0]
        bysite[site].append(g)
    ho = set()
    for site, gs in sorted(bysite.items()):
        gs = sorted(gs); rng.shuffle(gs)
        tot = sum(len(fams[g]) for g in gs); acc = 0
        for g in gs:
            if acc >= frac * tot:
                break
            ho.update(fams[g]); acc += len(fams[g])
    return np.array([i in ho for i in range(len(T))])
