"""Q1 head direction in two-element name cores.

Metrics on a set of distinct two-element types (A, B) in reading order (AA types dropped):
  HFI_prod  share of types whose second element is the more productive one (productivity = number of
            distinct two-element types containing the element, any position), ties dropped. >0.5 head-final.
  logV      log(V1/V2): distinct elements in position 1 over position 2.  Heads form a smaller recurrent set,
            so head-final -> V2 < V1 -> logV > 0.
  hub_pos2  among 'hub' elements (productivity >= 4), type-weighted share of their occurrences in position 2.
            >0.5 head-final.
  HFI_sa    among types where exactly one element also occurs as a one-element name, share where it is B.
Calibration: each reference corpus subsampled to the Indus number of types (n), 1000 subsamples; we report mean,
2.5-97.5% and the share of subsamples on the true side of 0.5 / 0.
Indus: bootstrap over types (CI) and an order null (each type's order flipped at random, which keeps
productivity and makes direction exactly symmetric in expectation).
Usage: .venv/bin/python experiments/core_semantics/h1_head.py [dev|heldout] [reps]
"""
import sys, json
from collections import Counter
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
import cs_data as D

HUB = 4


def metrics(types, single=None):
    types = [t for t in types if t[0] != t[1]]
    prod = Counter()
    for a, b in types:
        prod[a] += 1
        prod[b] += 1
    w = [1 if prod[b] > prod[a] else 0 for a, b in types if prod[a] != prod[b]]
    hfi = float(np.mean(w)) if w else np.nan
    V1 = len({a for a, _ in types}); V2 = len({b for _, b in types})
    hubs = {e for e, c in prod.items() if c >= HUB}
    p2 = sum(1 for _, b in types if b in hubs); p1 = sum(1 for a, _ in types if a in hubs)
    hub = p2 / (p1 + p2) if p1 + p2 else np.nan
    sa = np.nan
    if single is not None:
        z = [1 if (b in single) else 0 for a, b in types if (a in single) != (b in single)]
        sa = float(np.mean(z)) if z else np.nan
    return dict(HFI_prod=hfi, logV=float(np.log(V1 / V2)), hub_pos2=hub, HFI_sa=sa, n=len(types))


def summarise(rows, keys=("HFI_prod", "logV", "hub_pos2", "HFI_sa")):
    out = {}
    for k in keys:
        v = np.array([r[k] for r in rows], float)
        v = v[~np.isnan(v)]
        if len(v) == 0:
            continue
        out[k] = dict(mean=round(float(v.mean()), 3), lo=round(float(np.percentile(v, 2.5)), 3),
                      hi=round(float(np.percentile(v, 97.5)), 3),
                      share_pos=round(float(np.mean(v > (0 if k == "logV" else 0.5))), 3))
    return out


def subsample(types, single, n, reps, rng):
    types = list(types)
    rows = []
    for _ in range(reps):
        idx = rng.choice(len(types), min(n, len(types)), replace=False)
        rows.append(metrics([types[i] for i in idx], single))
    return summarise(rows)


def synthetic(direction, n, rng, n_heads=40, n_mods=300):
    """Planted corpus: heads from a small Zipf set, modifiers from a large one; direction 'final'/'initial'."""
    ph = 1 / np.arange(1, n_heads + 1); ph /= ph.sum()
    pm = 1 / np.arange(1, n_mods + 1) ** 0.8; pm /= pm.sum()
    out = set()
    while len(out) < n:
        h = f"h{rng.choice(n_heads, p=ph)}"; m = f"m{rng.choice(n_mods, p=pm)}"
        out.add((m, h) if direction == "final" else (h, m))
    return list(out)


def indus_sets(split):
    inc, occ = D.indus_types(split)
    two = [c for c in inc if len(c) == 2]
    single = {o["core"][0] for o in occ if len(o["core"]) == 1 and not o["num_adj"]}
    return two, single, inc, occ


def indus_test(two, single, reps, rng):
    obs = metrics(two, single)
    two_ = [t for t in two if t[0] != t[1]]
    boot = [metrics([two_[i] for i in rng.integers(0, len(two_), len(two_))], single) for _ in range(reps)]
    null = []
    for _ in range(reps):
        flip = rng.random(len(two_)) < 0.5
        null.append(metrics([(b, a) if f else (a, b) for (a, b), f in zip(two_, flip)], single))
    res = {"observed": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in obs.items()},
           "bootstrap": summarise(boot), "order_null": summarise(null), "p_two_sided": {}}
    for k in ("HFI_prod", "logV", "hub_pos2", "HFI_sa"):
        nv = np.array([r[k] for r in null], float); nv = nv[~np.isnan(nv)]
        c = np.median(nv)
        res["p_two_sided"][k] = round(float((1 + np.sum(np.abs(nv - c) >= abs(obs[k] - c))) / (1 + len(nv))), 4)
    return res


def anagram(two, n=None, reps=200, rng=None):
    s = [t for t in set(two) if t[0] != t[1]]
    if n is not None and len(s) > n:
        vals = []
        for _ in range(reps):
            sub = set(s[i] for i in rng.choice(len(s), n, replace=False))
            vals.append(sum(1 for a, b in sub if (b, a) in sub) / n)
        return dict(n=n, mean=round(float(np.mean(vals)), 3), lo=round(float(np.percentile(vals, 2.5)), 3),
                    hi=round(float(np.percentile(vals, 97.5)), 3))
    s = set(s)
    both = sum(1 for a, b in s if (b, a) in s)
    return dict(types=len(s), in_both_orders=both, share=round(both / len(s), 3))


def pair_order(inc):
    """Unordered sign pairs (2-sign cores) attested in >=2 distinct texts: observed share attested in both orders
    vs expectation under fully free order (each text's order a fair coin): 1 - 2*0.5^k."""
    from collections import defaultdict
    by = defaultdict(lambda: [0, 0])
    for c, k in inc.items():
        if len(c) == 2 and c[0] != c[1]:
            a, b = sorted(c)
            by[(a, b)][0 if c == (a, b) else 1] += k
    rows = [(v[0], v[1]) for v in by.values() if sum(v) >= 2]
    obs = sum(1 for x, y in rows if x and y) / len(rows)
    exp = float(np.mean([1 - 2 * 0.5 ** (x + y) for x, y in rows]))
    # majority-order share (how fixed are pairs that recur)
    maj = sum(max(x, y) for x, y in rows) / sum(x + y for x, y in rows)
    return dict(n_pairs=len(rows), both_orders_obs=round(obs, 3), both_orders_free_exp=round(exp, 3),
                majority_order_token_share=round(maj, 3))


def sign_skew(two, kmin=6):
    """Per-sign share of occurrences in position 2 among two-core types; binomial test vs 0.5, BH-FDR."""
    from scipy.stats import binomtest
    t = [x for x in two if x[0] != x[1]]
    c1, c2 = Counter(a for a, _ in t), Counter(b for _, b in t)
    rows = []
    for e in set(c1) | set(c2):
        n = c1[e] + c2[e]
        if n >= kmin:
            rows.append(dict(sign=e, n=n, pos2=round(c2[e] / n, 2), p=binomtest(c2[e], n, 0.5).pvalue))
    rows.sort(key=lambda r: r["p"])
    m = len(rows)
    for i, r in enumerate(rows):
        r["q"] = round(min(1, r["p"] * m / (i + 1)), 4); r["p"] = round(r["p"], 4)
    return dict(signs=rows, n_tested=m, n_q05=sum(r["q"] < 0.05 for r in rows))


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    rng = np.random.default_rng(1)
    two, single, inc, occ = indus_sets(split)
    n = len([t for t in two if t[0] != t[1]])
    print(f"Indus {split}: {len(two)} two-sign core types ({n} non-identical), standalone signs {len(single)}")
    res = {"split": split, "n_types": n}
    refs = {}
    s2, s1 = D.sanskrit_names(); refs["sanskrit (head-final)"] = (list(s2), s1, +1)
    u2, u1 = D.ur3_names(); refs["ur3 (head-initial)"] = (list(u2), u1, -1)
    c2, c1 = D.chinese_given(); refs["chinese given (no fixed head)"] = (list(c2), c1, 0)
    refs["synthetic head-final"] = (synthetic("final", 4000, rng), None, +1)
    refs["synthetic head-initial"] = (synthetic("initial", 4000, rng), None, -1)
    res["calibration"] = {}
    for name, (t, s, truth) in refs.items():
        full = metrics(t, s)
        sub = subsample(t, s, n, reps, rng)
        res["calibration"][name] = {"truth": truth, "full": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in full.items()}, f"subsample_n{n}": sub}
        print(f"\n{name}: full {res['calibration'][name]['full']}")
        for k, v in sub.items():
            print(f"   n={n} {k:9s} mean {v['mean']:+.3f} [{v['lo']:+.3f},{v['hi']:+.3f}] share>neutral {v['share_pos']:.3f}")
    res["indus"] = indus_test(two, single, reps, rng)
    res["indus_anagram"] = anagram(two)
    res["ref_anagram"] = {k: anagram(v[0], n, 200, rng) for k, v in refs.items() if "synthetic" not in k}
    res["sign_skew"] = sign_skew(two)
    print("per-sign position skew (signs with >=6 two-core types):")
    for r in res["sign_skew"]["signs"]:
        print("   ", r)
    print("   ", {k: v for k, v in res["sign_skew"].items() if k != "signs"})
    print("\nIndus", json.dumps(res["indus"], indent=1))
    print("anagram", res["indus_anagram"], res["ref_anagram"])
    res["pair_order"] = pair_order(inc)
    print("pair order (unordered pairs with >=2 texts):", res["pair_order"])
    json.dump(res, open(D.HERE / f"h1_head_{split}.json", "w"), indent=1, default=float)
