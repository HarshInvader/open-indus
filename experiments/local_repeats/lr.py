"""local_repeats: what are the repeated 4+ sign seal texts? (prereg docs/prereg/local_repeats.md)

Builds the per-object table, pair categories, tests T1-T5 and scores explanations (a)-(d).
usage: .venv/bin/python experiments/local_repeats/lr.py [nperm]
"""
import sys, os, json, itertools
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import fisher_exact

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "experiments/identifiers"))
from id_lib import icit_objects, icit_texts, m77_texts, flat, W2M  # noqa  (read-only import)

HERE = os.path.dirname(os.path.abspath(__file__))
NPERM = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
rng = np.random.default_rng(20261115)

# ------------------------------------------------------------------ data
OBJ = icit_objects()
RAW = {}
for t in icit_texts(): RAW.setdefault(t["id"].split(".")[0], t)
MERGED = {}
for r in json.load(open(os.path.join(ROOT, "sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json"))):
    if r["cisi"] not in ("-", "") and r["type"].startswith("SEAL"): MERGED.setdefault(r["cisi"], r)
SEALS = [o for o in OBJ if o["complete"] and o["cls"] == "seal"]
for o in SEALS: o["text"] = flat(o["sp"])
ALLC = [o for o in OBJ if o["complete"]]
for o in ALLC: o["text"] = flat(o["sp"])

M77SITE = {"Mohenjodaro": "Mohenjo-daro", "Chanhudaro": "Chanhu-daro"}


def m77_index():
    by = defaultdict(list)
    for t in m77_texts(): by[t["text_no"]].append(t)
    from corpus.load import m77_lines
    meta = {}
    for l in m77_lines(): meta.setdefault(l["text_no"], (l.get("level"), l.get("locus"), l.get("fs_description")))
    idx = defaultdict(list)
    for no, ts in by.items():
        if not all(t["complete"] for t in ts): continue
        seq = tuple(s for t in sorted(ts, key=lambda t: t["side"]) for s in t["seq"] if s != "|")
        if "#" in seq: continue
        site = M77SITE.get(ts[0]["site"], ts[0]["site"])
        lv, lc, fs = meta.get(no, (None, None, None))
        idx[(site, seq)].append(dict(text_no=no, type=ts[0]["object_type"], level=lv, locus=lc, fs=fs))
    return idx


M77 = m77_index()


def num(x):
    try: return float(x)
    except Exception: return 0.0


def info(o):
    r = RAW[o["obj"]]; m = MERGED.get(o["cisi"], {})
    return dict(obj=o["obj"], cisi=o["cisi"], site=o["site"], type=o["type"], symbol=r["symbol"],
                w=num(r["width_mm"]), h=num(r["height_mm"]), material=r["material"],
                period=o["period"], phase=o["phase"], time=m.get("time", ""), shape=m.get("shape", ""),
                cult=m.get("cult", ""), area=m.get("area-section", ""), block=m.get("block-house", ""),
                room=m.get("room-grid", ""))


def known(v): return v not in (None, "", "-", "--")


def dims_cmp(a, b):
    if not (a["w"] > 0 and a["h"] > 0 and b["w"] > 0 and b["h"] > 0): return "unknown", None
    best = None
    for bw, bh in ((b["w"], b["h"]), (b["h"], b["w"])):
        d = max(abs(a["w"] - bw), abs(a["h"] - bh))
        rel = max(abs(a["w"] - bw) / ((a["w"] + bw) / 2), abs(a["h"] - bh) / ((a["h"] + bh) / 2))
        if best is None or rel < best[1]: best = (d, rel)
    d, rel = best
    return ("same" if d <= 0.5 else "different" if rel > 0.10 else "near"), rel


def sym_known(s): return known(s)


def pair_cat(a, b):
    if a["site"] != b["site"]: return "X", {}
    dc, rel = dims_cmp(a, b)
    sk = sym_known(a["symbol"]) and sym_known(b["symbol"])
    sym = ("same" if a["symbol"] == b["symbol"] else "different") if sk else "unknown"
    pk = known(a["period"]) and known(b["period"])
    per = ("same" if (a["period"], a["phase"]) == (b["period"], b["phase"]) else "different") if pk else "unknown"
    ak = known(a["area"]) and known(b["area"])
    area = ("same" if a["area"] == b["area"] else "different") if ak else "unknown"
    f = dict(dims=dc, rel=rel, symbol=sym, period=per, area=area, type_same=a["type"] == b["type"])
    if sym == "same" and dc == "same" and f["type_same"] and per != "different" and area != "different": c = "A/D"
    elif per == "different": c = "C"
    elif dc == "different" or sym == "different": c = "B"
    elif sym == "same" and dc == "near": c = "D"
    else: c = "U"
    return c, f


# ------------------------------------------------------------------ repeated set
cnt = Counter(o["text"] for o in SEALS)
R = sorted([t for t, n in cnt.items() if n >= 2 and len(t) >= 4], key=lambda t: (len(t), t))
fam_objs = {t: [o for o in SEALS if o["text"] == t] for t in R}
all_by_text = defaultdict(list)
for o in ALLC: all_by_text[o["text"]].append(o)
ALLTEXTS_BY_LEN = defaultdict(list)
for t, os_ in all_by_text.items(): ALLTEXTS_BY_LEN[len(t)].append(t)


def longer_variants(t, site=None):
    out = []
    for u in ALLTEXTS_BY_LEN[len(t) + 1]:
        for i in range(len(u)):
            if u[:i] + u[i + 1:] == t:
                for o in all_by_text[u]:
                    if site is None or o["site"] == site:
                        out.append(dict(text=" ".join(u), obj=o["obj"], site=o["site"], cls=o["cls"], ins=u[i], pos=i))
                break
    return out


def shorter_exists(t, site):
    for i in range(len(t)):
        s = t[:i] + t[i + 1:]
        if any(o["site"] == site for o in all_by_text.get(s, [])): return True
    return False


def m77_for(t, site):
    mt = tuple(W2M.get(x) for x in t)
    if None in mt: return []
    return M77.get((site, mt), [])


families = []
pairs = []
for t in R:
    objs = [info(o) for o in fam_objs[t]]
    sites = sorted({o["site"] for o in objs})
    other = [dict(obj=o["obj"], site=o["site"], cls=o["cls"], type=o["type"]) for o in all_by_text[t] if o["cls"] != "seal"]
    m77 = {s: m77_for(t, s) for s in sites}
    lv = longer_variants(t)
    fp = []
    for a, b in itertools.combinations(objs, 2):
        c, f = pair_cat(a, b)
        fp.append(dict(a=a["obj"], b=b["obj"], cat=c, **f)); pairs.append(dict(text=" ".join(t), band="4-5" if len(t) <= 5 else "6+", a=a, b=b, cat=c, f=f))
    families.append(dict(text=" ".join(t), length=len(t), band="4-5" if len(t) <= 5 else "6+", n=len(objs), sites=sites,
                         objects=objs, other_carriers=other, m77=m77, longer=lv, pairs=fp))

# ------------------------------------------------------------------ visual check list (A/D candidates)
boxes = defaultdict(list)
import csv
for r in csv.DictReader(open(os.path.join(ROOT, "experiments/carver_hands/work/boxes.csv"))):
    boxes[r["cisi"]].append(r)


# ------------------------------------------------------------------ tests
def site_pool(field_ok):
    """same-site seals with text length >= 4 and field known, grouped by site; labels = text."""
    P = defaultdict(list)
    for o in SEALS:
        if len(o["text"]) >= 4:
            i = info(o); i["text"] = o["text"]
            if field_ok(i): P[o["site"]].append(i)
    return P


def pair_stat(P, labels, fn):
    vals = []
    for s, L in P.items():
        lab = labels[s]; g = defaultdict(list)
        for k, x in enumerate(lab): g[x].append(k)
        for ks in g.values():
            for i, j in itertools.combinations(ks, 2):
                v = fn(L[i], L[j])
                if v is not None: vals.append(v)
    return vals


def perm_test(field_ok, fn, agg):
    P = site_pool(field_ok)
    lab0 = {s: [x["text"] for x in L] for s, L in P.items()}
    obs_vals = pair_stat(P, lab0, fn)
    if len(obs_vals) < 8: return dict(n_pairs=len(obs_vals), untestable=True, obs=agg(obs_vals) if obs_vals else None)
    obs = agg(obs_vals); null = []
    for _ in range(NPERM):
        lab = {s: [v[k] for k in rng.permutation(len(v))] for s, v in lab0.items()}
        vv = pair_stat(P, lab, fn)
        null.append(agg(vv) if vv else np.nan)
    null = np.array(null, float); null = null[~np.isnan(null)]
    return dict(n_pairs=len(obs_vals), obs=float(obs), null_mean=float(null.mean()),
                null_ci=[float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))],
                p_low=float((1 + (null <= obs).sum()) / (len(null) + 1)), p_high=float((1 + (null >= obs).sum()) / (len(null) + 1)),
                untestable=False)


dims_ok = lambda i: i["w"] > 0 and i["h"] > 0
T = {}
T["T1_size"] = perm_test(dims_ok, lambda a, b: dims_cmp(a, b)[1], lambda v: float(np.median(v)))
T["T2_emblem"] = perm_test(lambda i: sym_known(i["symbol"]), lambda a, b: float(a["symbol"] == b["symbol"]), lambda v: float(np.mean(v)))
T["T3_period"] = perm_test(lambda i: known(i["period"]), lambda a, b: float((a["period"], a["phase"]) != (b["period"], b["phase"])), lambda v: float(np.mean(v)))
T["T4_findspot"] = perm_test(lambda i: known(i["area"]), lambda a, b: float(a["area"] == b["area"]), lambda v: float(np.mean(v)))


def t5():
    out = {}
    for bname, (lo, hi) in (("4-5", (4, 5)), ("6+", (6, 99)), ("all", (4, 99))):
        rows = {"rep": [0, 0], "single": [0, 0], "rep_short": [0, 0], "single_short": [0, 0]}
        for t, n in cnt.items():
            if not lo <= len(t) <= hi: continue
            key = "rep" if n >= 2 else "single"
            sites = {o["site"] for o in SEALS if o["text"] == t}
            lg = any(longer_variants(t, s) for s in sites)
            sh = any(shorter_exists(t, s) for s in sites)
            rows[key][0] += lg; rows[key][1] += 1
            rows[key + "_short"][0] += sh; rows[key + "_short"][1] += 1
        def fx(a, b):
            tab = [[a[0], a[1] - a[0]], [b[0], b[1] - b[0]]]
            return float(fisher_exact(tab, alternative="greater")[1])
        out[bname] = dict(rep_longer=rows["rep"], single_longer=rows["single"], p_longer=fx(rows["rep"], rows["single"]),
                          rep_shorter=rows["rep_short"], single_shorter=rows["single_short"], p_shorter=fx(rows["rep_short"], rows["single_short"]))
    return out


T["T5_extension"] = t5()
fam_p = {"T1_size": T["T1_size"].get("p_low"), "T2_emblem": T["T2_emblem"].get("p_high"),
         "T3_period": T["T3_period"].get("p_low"), "T4_findspot": T["T4_findspot"].get("p_high"),
         "T5_extension": T["T5_extension"]["all"]["p_longer"]}


def holm(d):
    items = sorted([(k, v) for k, v in d.items() if v is not None], key=lambda x: x[1]); m = len(items); out = {}; prev = 0
    for r, (k, v) in enumerate(items):
        q = min(1.0, max(prev, v * (m - r))); out[k] = q; prev = q
    return out


T["holm"] = holm(fam_p)

if __name__ == "__main__":
    json.dump(dict(families=families, tests=T, candidates_AD=[
        dict(text=p["text"], a=p["a"]["obj"], a_cisi=p["a"]["cisi"], b=p["b"]["obj"], b_cisi=p["b"]["cisi"],
             boxes_a=boxes.get(p["a"]["cisi"], []), boxes_b=boxes.get(p["b"]["cisi"], [])) for p in pairs if p["cat"] == "A/D"]),
        open(os.path.join(HERE, "lr_raw.json"), "w"), indent=1, default=float)
    print("families", len(families), "objects", sum(f["n"] for f in families), Counter(f["band"] for f in families))
    print("pairs", Counter((p["band"], p["cat"]) for p in pairs))
    for k, v in T.items(): print(k, v)
