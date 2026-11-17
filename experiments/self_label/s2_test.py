"""Step 2: are frozen shape-nearest signs enriched on the object class they resemble?
Run once, after frozen_candidates.json and docs/prereg/self_label.md were hashed:
    .venv/bin/python -I experiments/self_label/s2_test.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts  # noqa: E402

OUT = ROOT / "experiments/self_label"
NPERM = 10000
MIN_CLASS = 5      # class needs >= 5 texts in a set to be tested
rng = np.random.default_rng(20261115)

fr = json.load(open(OUT / "frozen_candidates.json"))
POOL = fr["pool"]
ROUTES = ["chamfer", "catalogue", "hu"]  # primary, secondary, tertiary
pairs = defaultdict(list)  # (class, sign) -> routes
for cls, e in fr["classes"].items():
    for r in ROUTES:
        for x in e[r]:
            pairs[(cls, x["sign"])].append(r)

# ---------- data sets ----------
held = set(json.load(open(ROOT / "data/splits_v2.json"))["heldout"])


def m77_set():
    seen, out = set(), []
    for t in m77_texts():
        signs = [s for s in t["seq"] if s.startswith("M")]
        if not signs:
            continue
        key = (" ".join(t["seq"]), t["object_type"], t["site"])
        if key in seen:
            continue
        seen.add(key)
        out.append({"site": t["site"], "cls": t["object_type"], "signs": set(signs),
                    "ho": " ".join(t["seq"]) in held})
    return out


bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": [f"M{m}" for m in v["M"]] for k, v in bridge.items()}


def icit_cls(ty):
    if ty.startswith("SEAL"):
        return "seal"
    if ty.startswith("TAG"):
        return "sealing"
    if ty in ("TAB:B", "TAB:I"):
        return "miniature tablet"
    if ty == "TAB:C":
        return "copper tablet"
    if ty in ("POT:T:g", "POsT:T:g", "POT:T:S"):
        return "pottery graffito"
    if ty == "POT:T:s":
        return "stamped pottery"
    if ty == "ROD":
        return "ivory/bone rod"
    if ty == "IMPL":
        return "bronze implement"
    if ty == "BNGL":
        return "bangle"
    return "other"


def icit_set():
    seen, out = set(), []
    for t in icit_texts():
        ws = [s for s in t["seq"] if s.startswith("W")]
        if not ws:
            continue
        cls = icit_cls(t["type"])
        key = (" ".join(t["seq"]), cls, t["site"])
        if key in seen:
            continue
        seen.add(key)
        ms = set()
        for w in ws:
            ms.update(W2M.get(w, [w]))
        out.append({"site": t["site"], "cls": cls, "signs": ms})
    return out


# ---------- permutation machinery ----------
def perm_test(texts, signs, classes):
    """Return obs[c][s], null mean/sd, p (one-sided enrichment) for every class c and sign s.
    Null: object-class labels permuted among texts within site."""
    n = len(texts)
    X = np.array([[s in t["signs"] for s in signs] for t in texts], dtype=np.int32)  # n x S
    labels = np.array([t["cls"] for t in texts])
    sites = np.array([t["site"] for t in texts])
    idx_by_site = [np.nonzero(sites == st)[0] for st in np.unique(sites)]
    res = {}
    Y = {c: (labels == c).astype(np.int32) for c in classes}
    obs = {c: Y[c] @ X for c in classes}
    ge = {c: np.zeros(len(signs)) for c in classes}
    s1 = {c: np.zeros(len(signs)) for c in classes}
    s2 = {c: np.zeros(len(signs)) for c in classes}
    perm = np.arange(n)
    for _ in range(NPERM):
        for ix in idx_by_site:
            perm[ix] = rng.permutation(ix)
        lab = labels[perm]
        for c in classes:
            v = (lab == c).astype(np.int32) @ X
            ge[c] += v >= obs[c]
            s1[c] += v
            s2[c] += v.astype(float) ** 2
    for c in classes:
        mu = s1[c] / NPERM
        sd = np.sqrt(np.maximum(s2[c] / NPERM - mu ** 2, 1e-12))
        res[c] = {"obs": obs[c], "mu": mu, "sd": sd, "p": (1 + ge[c]) / (NPERM + 1),
                  "n_cls": int(Y[c].sum()), "present": X.sum(0)}
    return res


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    if m == 0:
        return ps
    o = np.argsort(ps)
    q = ps[o] * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(q, 1)
    return out


def analyse(texts, name):
    classes = sorted({c for c, _ in pairs} & {t["cls"] for t in texts})
    classes = [c for c in classes if sum(t["cls"] == c for t in texts) >= MIN_CLASS]
    res = perm_test(texts, POOL, classes)
    rows = []
    for (c, s), routes in sorted(pairs.items()):
        if c not in res:
            continue
        r = res[c]
        j = POOL.index(s)
        z = (r["obs"] - r["mu"]) / r["sd"]
        ok = r["present"] >= 3
        pct = float((z[ok] < z[j]).mean()) if ok[j] else None
        rows.append({"set": name, "cls": c, "sign": s, "routes": routes, "n_cls": r["n_cls"],
                     "present": int(r["present"][j]), "obs": int(r["obs"][j]),
                     "exp": round(float(r["mu"][j]), 2), "z": round(float(z[j]), 2),
                     "p": float(r["p"][j]), "register_pct": pct})
    q = bh([x["p"] for x in rows])
    for x, qq in zip(rows, q):
        x["q"] = float(qq)
    return rows, res, classes


def global_test(res, classes, route):
    """Mean register percentile of the frozen signs vs random k-sign sets from the pool."""
    k = fr["k"]
    zs, frozen_pct = {}, []
    for c in classes:
        r = res[c]
        ok = r["present"] >= 3
        z = (r["obs"] - r["mu"]) / r["sd"]
        pct = np.array([(z[ok] < z[j]).mean() for j in range(len(POOL))])
        zs[c] = (pct, np.nonzero(ok)[0])
        for x in fr["classes"][c][route]:
            j = POOL.index(x["sign"])
            if ok[j]:
                frozen_pct.append(pct[j])
    if not frozen_pct:
        return None
    stat = float(np.mean(frozen_pct))
    null = []
    for _ in range(NPERM):
        v = []
        for c in classes:
            pct, okix = zs[c]
            nk = sum(ok_ for ok_ in [res[c]["present"][POOL.index(x["sign"])] >= 3 for x in fr["classes"][c][route]])
            if nk:
                v.extend(pct[rng.choice(okix, nk, replace=False)])
        null.append(np.mean(v))
    null = np.array(null)
    return {"route": route, "n": len(frozen_pct), "mean_pct": round(stat, 3),
            "null_mean": round(float(null.mean()), 3), "p": float((1 + (null >= stat).sum()) / (NPERM + 1))}


def site_replication(texts, c, s):
    """Enrichment at each site other than the class's main site (site-restricted permutation)."""
    cnt = Counter(t["site"] for t in texts if t["cls"] == c)
    if not cnt:
        return []
    main = cnt.most_common(1)[0][0]
    out = []
    for site, n in cnt.most_common():
        if site == main or n < 3:
            continue
        sub = [t for t in texts if t["site"] == site]
        X = np.array([s in t["signs"] for t in sub])
        Y = np.array([t["cls"] == c for t in sub])
        obs = int((X & Y).sum())
        null = np.array([(X & rng.permutation(Y)).sum() for _ in range(NPERM)])
        out.append({"site": site, "n_cls": int(n), "obs": obs, "exp": round(float(null.mean()), 2),
                    "p": float((1 + (null >= obs).sum()) / (NPERM + 1))})
    return out


if __name__ == "__main__":
    m77 = m77_set()
    dev = [t for t in m77 if not t["ho"]]
    ho = [t for t in m77 if t["ho"]]
    ic = icit_set()
    print("texts: dev", len(dev), "heldout", len(ho), "icit", len(ic))
    print("ICIT class sizes", Counter(t["cls"] for t in ic))
    out = {"n_pairs": len(pairs), "sets": {}, "global": [], "verdict": {}}
    allrows = {}
    for name, texts in (("m77_dev", dev), ("m77_heldout_v2", ho), ("icit", ic)):
        rows, res, classes = analyse(texts, name)
        allrows[name] = rows
        out["sets"][name] = {"n_texts": len(texts), "classes": {c: res[c]["n_cls"] for c in classes},
                             "rows": rows}
        for route in ROUTES:
            g = global_test(res, classes, route)
            if g:
                g["set"] = name
                out["global"].append(g)
        print(f"\n== {name}: {len(texts)} texts; classes {[(c, res[c]['n_cls']) for c in classes]}")
        for x in sorted(rows, key=lambda x: x["p"]):
            print(f"  {x['cls']:18s} {x['sign']:5s} {','.join(x['routes']):18s} obs {x['obs']:3d} exp {x['exp']:6.2f} "
                  f"z {x['z']:6.2f} p {x['p']:.4f} q {x['q']:.3f} reg_pct {x['register_pct']}")
    print("\nGLOBAL (shape route predicts enrichment beyond register)")
    for g in out["global"]:
        print(" ", g)

    # confirmation rule
    ho_rows = {(x["cls"], x["sign"]): x for x in allrows["m77_heldout_v2"]}
    confirmed = []
    for x in allrows["icit"]:
        reps = site_replication(ic, x["cls"], x["sign"])
        x["site_rep"] = reps
        c1 = x["q"] < 0.05
        c2 = any(r["p"] < 0.05 for r in reps)
        c3 = x["register_pct"] is not None and x["register_pct"] >= 0.90
        h = ho_rows.get((x["cls"], x["sign"]))
        c4 = True if h is None else h["obs"] > h["exp"]
        x["pass"] = {"C1_icit_q": c1, "C2_second_site": c2, "C3_register_top10": c3, "C4_heldout_dir": c4}
        if c1 and c2 and c3 and c4:
            confirmed.append((x["cls"], x["sign"]))
        if c1 or x["p"] < 0.05:
            print("ICIT candidate", x["cls"], x["sign"], x["pass"], reps)
    signs_conf = sorted({s for _, s in confirmed})
    out["confirmed_pairs"] = confirmed
    out["verdict"] = {"n_confirmed_signs": len(signs_conf), "signs": signs_conf,
                      "decisive_positive": len(signs_conf) >= 2}
    print("\nCONFIRMED", confirmed, "-> decisive positive:", len(signs_conf) >= 2)

    json.dump(out, open(OUT / "results_raw.json", "w"), indent=1, default=float)
