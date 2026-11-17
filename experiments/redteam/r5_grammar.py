"""Claim 5 (structure): strict opener/core/closer grammar; held-out real order beats all
permutations in 63% (mean percentile 0.94). Attacks:
  a. remove the fixed positional signs (jar M342, post-closer M176, openers M267/M391, connective M99)
     from train and test and rerun;
  b. restrict to held-out texts containing none of them;
  c. a position-only model (P(sign|first), P(sign|last), P(sign|medial); no adjacency) - how much
     of the 63% does it already give?
  d. leakage: drop held-out texts with an edit-distance<=1 neighbour in dev (variant copies);
  e. the O*KC* template statistic is not reimplemented (classes are learned from the same
     positional profiles it then tests); we note it as circular.
Own implementation, same split file (data/splits.json)."""
import itertools, math
from collections import Counter, defaultdict
import numpy as np
from rt_common import m77, flat, splits, KN, edit1, save

rng = np.random.default_rng(3)
FIXED = {"M342", "M176", "M267", "M391", "M99"}


def load():
    held = splits()
    dev, ho, seen = [], [], set()
    for r in m77():
        k = " ".join(r["seq"])
        if k in seen: continue
        seen.add(k)
        f = flat(r["seq"])
        if not f: continue
        (ho if k in held else dev).append(f)
    dev = sorted(set(dev)); ho = sorted(set(ho) - set(dev))
    return dev, ho


class PosModel:
    def __init__(self, texts):
        self.c = {k: Counter() for k in ("F", "M", "L", "S")}
        for t in texts:
            if len(t) == 1: self.c["S"][t[0]] += 1; continue
            for i, s in enumerate(t):
                self.c["F" if i == 0 else "L" if i == len(t) - 1 else "M"][s] += 1
        self.V = {s for c in self.c.values() for s in c} | {"<unk>"}

    def bits(self, t):
        b = 0
        for i, s in enumerate(t):
            k = "S" if len(t) == 1 else "F" if i == 0 else "L" if i == len(t) - 1 else "M"
            c = self.c[k]; n = sum(c.values())
            b -= math.log2((c.get(s, 0) + 0.1) / (n + 0.1 * len(self.V)))
        return b


def perm_test(model, texts, maxperm=5040):
    best, pct, n = 0, [], 0
    for t in texts:
        if len(t) < 2 or len(set(t)) < 2: continue
        P = set(itertools.permutations(t)) if math.factorial(len(t)) <= maxperm else {tuple(rng.permutation(t)) for _ in range(maxperm)} | {t}
        b0 = model.bits(t)
        others = [model.bits(p) for p in P if p != t]
        n += 1
        best += all(b0 < b for b in others)
        pct.append(np.mean([b0 < b for b in others]) + 0.5 * np.mean([b0 == b for b in others]))
        # chance expectation of 'best': 1/|P|
    exp_best = np.mean([1 / len(set(itertools.permutations(t))) if math.factorial(len(t)) <= maxperm else 1 / maxperm
                        for t in texts if len(t) >= 2 and len(set(t)) >= 2])
    return dict(n=n, best_share=round(best / n, 3), mean_pct=round(float(np.mean(pct)), 3), chance_best=round(float(exp_best), 3))


def strip(texts, S):
    out = [tuple(x for x in t if x not in S) for t in texts]
    return [t for t in out if t]


def main():
    dev, ho = load()
    ho_noleak = [t for t in ho if not any(edit1(t, d) for d in dev if abs(len(d) - len(t)) <= 1)]
    res = {"n_dev": len(dev), "n_heldout": len(ho), "n_heldout_no_ed1_neighbour": len(ho_noleak)}
    kn = KN(dev)
    res["baseline_bigram"] = perm_test(kn, ho)
    res["bigram_no_leak"] = perm_test(kn, ho_noleak)
    res["position_only_model"] = perm_test(PosModel(dev), ho)
    res["position_only_no_leak"] = perm_test(PosModel(dev), ho_noleak)
    d2, h2 = strip(dev, FIXED), strip(ho_noleak, FIXED)
    res["bigram_fixed_signs_removed_no_leak"] = perm_test(KN(d2), h2)
    res["position_only_fixed_removed_no_leak"] = perm_test(PosModel(d2), h2)
    h3 = [t for t in ho_noleak if not (set(t) & FIXED)]
    res["bigram_texts_without_fixed_no_leak"] = perm_test(kn, h3)
    res["position_only_texts_without_fixed_no_leak"] = perm_test(PosModel(dev), h3)
    # top-10 most positional signs removed
    pos = defaultdict(lambda: [0, 0, 0])
    for t in dev:
        if len(t) < 2: continue
        for i, s in enumerate(t):
            pos[s][0] += 1; pos[s][1] += i == 0; pos[s][2] += i == len(t) - 1
    skew = sorted([(max(v[1], v[2]) / v[0], s) for s, v in pos.items() if v[0] >= 30], reverse=True)
    top10 = {s for _, s in skew[:10]} | FIXED
    res["top_positional_removed"] = sorted(top10)
    res["bigram_top15_removed_no_leak"] = perm_test(KN(strip(dev, top10)), strip(ho_noleak, top10))
    # internal order of the core: interior of texts of length>=4 (drop first and last sign)
    core_d = [t[1:-1] for t in dev if len(t) >= 4]
    core_h = [t[1:-1] for t in ho_noleak if len(t) >= 4]
    res["bigram_interior_only_no_leak"] = perm_test(KN(core_d), core_h)
    res["position_only_interior_no_leak"] = perm_test(PosModel(core_d), core_h)
    for k, v in res.items(): print(k, v)
    save("r5_grammar", res)


main()
