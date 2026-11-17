"""Q3b. Is there a numeral-like class detectable from distribution alone? Cluster signs (>=10 distinct texts, dev) on
left/right neighbour profiles + positional profile; test whether stroke signs (identified by DRAWING, shaunmortal
data/stroke_signs.json) concentrate in one cluster beyond chance (hypergeometric), K chosen by bootstrap stability.
"""
import json
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import hypergeom
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import adjusted_rand_score

from common import ROOT, m77_split, runs, save_json, signs, is_clean

rng = np.random.default_rng(1)
ss = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
SHORT = {"M%s" % k for k in ss["short"]}; TALL = {"M%s" % k for k in ss["tall"]}
STROKES = SHORT | TALL
dev, ho = m77_split()


def embed(texts_runs, texts_clean, keep):
    occ = defaultdict(Counter)
    for r in texts_runs:
        rr = ["<s>"] + r + ["</s>"]
        for i in range(1, len(rr) - 1):
            occ[rr[i]]["L_" + rr[i - 1]] += 1; occ[rr[i]]["R_" + rr[i + 1]] += 1
    feats = sorted({f for x in keep for f in occ[x]})
    fi = {f: i for i, f in enumerate(feats)}
    M = np.zeros((len(keep), len(feats)))
    for a, x in enumerate(keep):
        for f, c in occ[x].items():
            M[a, fi[f]] = c
    # PPMI
    tot = M.sum(); pr = M.sum(1, keepdims=True) / tot; pc = M.sum(0, keepdims=True) / tot
    pmi = np.log((M / tot + 1e-12) / (pr * pc + 1e-12)); ppmi = np.maximum(pmi, 0) * (M > 0)
    Z = TruncatedSVD(20, random_state=0).fit_transform(ppmi)
    Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9
    return Z


runs_dev = [r for t in dev for r in runs(t["seq"])]
clean_dev = [signs(t["seq"]) for t in dev if is_clean(t)]
nt = Counter(x for t in dev for x in set(signs(t["seq"])))
keep = sorted([x for x in nt if nt[x] >= 10], key=lambda x: -nt[x])
Z = embed(runs_dev, clean_dev, keep)
isS = np.array([x in STROKES for x in keep])
res = {"n_signs": len(keep), "n_stroke_signs": int(isS.sum()), "by_K": {}}
for K in range(2, 11):
    km = KMeans(K, n_init=30, random_state=0).fit(Z)
    # stability: bootstrap texts
    aris = []
    for b in range(15):
        idx = rng.integers(0, len(dev), len(dev))
        dv = [dev[i] for i in idx]
        Zb = embed([r for t in dv for r in runs(t["seq"])], None, keep)
        aris.append(adjusted_rand_score(km.labels_, KMeans(K, n_init=10, random_state=b).fit_predict(Zb)))
    best = None
    for c in range(K):
        mem = km.labels_ == c
        k = int((mem & isS).sum()); n = int(mem.sum())
        p = hypergeom.sf(k - 1, len(keep), int(isS.sum()), n)
        if best is None or p < best["p"]:
            best = {"cluster": c, "size": n, "strokes_in": k, "p": float(p), "members": [x for x, m in zip(keep, mem) if m]}
    res["by_K"][K] = {"ARI": float(np.mean(aris)), "best_stroke_cluster": best}
save_json("q3b_context_classes", res)
for K, v in res["by_K"].items():
    b = v["best_stroke_cluster"]
    print(K, round(v["ARI"], 2), b["size"], b["strokes_in"], "%.2g" % b["p"], b["members"][:25])
print("stroke signs considered:", [x for x in keep if x in STROKES])
