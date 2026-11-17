"""Exploratory follow-ups after the frozen run (not pre-registered).
1. Power for P1 (whole text, all lengths, A0): plant a 20-sign local stock into Harappa tokens (any slot).
2. Closer-slot detail: which closers differ MD vs Harappa at A0, and does A1 merging absorb them?
3. Beta diversity: observed vs pooled-null dissimilarity per pair.
"""
import json
from collections import Counter

import numpy as np
from scipy.stats import fisher_exact

import lib

MD, HA = "Mohenjo-daro", "Harappa"
out = {}
E = lib.eligible_icit("strict")
MH = [t for t in E if t["site"] in (MD, HA)]
fin = json.load(open(lib.HERE / "s1_final.json"))
thr = fin["confirmatory"]["P1"]["null_q95"]
freq = Counter(s for t in MH for s in t["signs"])
common = sorted(s for s, c in freq.items() if c >= 5)
A0 = {}
pw = {}
for q in (0.1, 0.2, 0.3):
    rng = np.random.default_rng(99 + int(q * 100)); hits = 0; aucs = []
    for rep in range(100):
        sites = np.array([t["site"] for t in MH])[rng.permutation(len(MH))]
        stock = list(rng.choice(common, 20, replace=False))
        T = []
        for t, s in zip(MH, sites):
            t2 = dict(t); t2["site"] = s
            if s == HA:
                sg = [stock[rng.integers(20)] if rng.random() < q else x for x in t["signs"]]
                runs, k = [], 0
                for r in t["runs"]:
                    runs.append(sg[k:k + len(r)]); k += len(r)
                t2["signs"], t2["runs"] = sg, runs
            T.append(t2)
        X, _ = lib.design(T, A0, "all")
        y = np.array([1 if t["site"] == MD else 0 for t in T])
        P = lib.oof_scores(X, y, np.arange(len(y)), classes=[0, 1], reps=1, seed=rep)
        a = lib.auc(y, P[:, 1]); aucs.append(a); hits += a >= thr
    pw[str(q)] = dict(power=hits / 100, mean_auc=float(np.mean(aucs)))
    print("P1 power", q, pw[str(q)], flush=True)
out["power_P1"] = pw

MH3 = [t for t in MH if len(t["signs"]) >= 3]
A1 = lib.allograph_map("A1")
rows = []
for lv, am in (("A0", {}), ("A1", A1)):
    c = {s: Counter(am.get(t["signs"][-1], t["signs"][-1]) for t in MH3 if t["site"] == s) for s in (MD, HA)}
    n = {s: sum(c[s].values()) for s in c}
    for sg in set(c[MD]) | set(c[HA]):
        a, b = c[MD][sg], c[HA][sg]
        if a + b < 8:
            continue
        _, p = fisher_exact([[a, n[MD] - a], [b, n[HA] - b]])
        rows.append(dict(level=lv, closer=sg, md=a, h=b, rate_md=a / n[MD], rate_h=b / n[HA], p=p))
rows.sort(key=lambda r: r["p"])
out["closers"] = rows[:12]
for r in rows[:12]:
    print(r)

P5 = fin["P5"]
out["P5_pairs"] = [dict(pair=f"{i}", bc=b, bc_null=bn, ja=j, ja_null=jn, km=d)
                   for i, (b, bn, j, jn, d) in enumerate(zip(P5["bray_curtis"], P5["bray_curtis_pool_null"],
                                                                P5["jaccard"], P5["jaccard_pool_null"], P5["dist_km"]))]
print(P5["sites"]); print(out["P5_pairs"])
lib.jdump(out, lib.HERE / "s2_explore.json")
