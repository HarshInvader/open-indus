"""F2. Counts or number-names?  Numeral-value distribution of each sign that follows (head) or precedes a stroke
numeral, short and tall strokes separately.

Usage: .venv/bin/python experiments/pair_numeral_long/f2_numerals.py dev|heldout

Unit: one numeral-sign occurrence inside a break-free run of a distinct text (dev_heldout v2).
Value = stroke count of the numeral sign directly adjacent to the head (fr.SHORT / fr.TALL; short-2 M99/M101 is the
connective and is excluded upstream, so short value 2 comes only from M100).
Models for a sign's value counts over the attested support of its stroke class:
  decay   p(v) ~ v^-a, a >= 0 fitted                      (count-like: small amounts commoner)   k = 1
  capcal  uniform on support values <= cap (cap = max seen) (calendar-like: cycle with a hard cap)  k = 1
  spike   share w on one value v*, rest uniform              (lexeme-like: frozen 'six-fish' type)  k = 2
Classification by BIC; a spike is only accepted if its max-share permutation p (values drawn from the pooled class
distribution without this sign, 20,000 draws) survives BH at q < 0.05 over all classified signs.
"""
import sys, json
import numpy as np
from collections import Counter, defaultdict
from scipy.optimize import minimize_scalar
from scipy.stats import binomtest
from common import *

mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = np.random.default_rng(23)
NMIN = 8
dev, ho = dev_heldout()
SUPPORT = {"S": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12], "T": [1, 2, 3, 4, 5]}


def counts_by(ctx, side="head"):
    by = defaultdict(lambda: defaultdict(Counter))
    for c in ctx:
        h = c[side]
        if h and h not in ("$", "^"):
            by[c["cls"]][h][c["value"]] += 1
    return by


def ll_decay(cn, sup):
    v = np.array(sup, float); x = np.array([cn.get(s, 0) for s in sup], float)
    f = lambda a: -np.sum(x * (-a * np.log(v) - np.log(np.sum(v ** -a))))
    r = minimize_scalar(f, bounds=(0, 8), method="bounded")
    return -r.fun, r.x


def ll_capcal(cn, sup):
    cap = max(cn); S = [s for s in sup if s <= cap]
    n = sum(cn.values())
    return -n * np.log(len(S)), cap


def ll_spike(cn, sup):
    n = sum(cn.values()); best = (-np.inf, None, None)
    for vs in sup:
        k = cn.get(vs, 0)
        w = min(max(k / n, 1e-9), 1 - 1e-9)
        ll = (k * np.log(w) if k else 0) + ((n - k) * np.log((1 - w) / (len(sup) - 1)) if n - k else 0)
        if ll > best[0]:
            best = (ll, vs, k / n)
    return best


def classify(cn, sup):
    n = sum(cn.values())
    ld, a = ll_decay(cn, sup); lc, cap = ll_capcal(cn, sup); ls, vs, w = ll_spike(cn, sup)
    bic = {"decay": -2 * ld + 1 * np.log(n), "capcal": -2 * lc + 1 * np.log(n), "spike": -2 * ls + 2 * np.log(n)}
    best = min(bic, key=bic.get)
    return dict(n=n, best=best, bic={k: round(v, 2) for k, v in bic.items()}, decay_a=round(float(a), 3), cap=int(cap),
                spike_value=int(vs), spike_share=round(w, 3), n_values=len(cn))


def spike_perm(cn, pool, nd=20000):
    n = sum(cn.values()); obs = max(cn.values()) / n
    vals = np.array(sorted(pool)); p = np.array([pool[v] for v in vals], float); p /= p.sum()
    draws = rng.multinomial(n, p, size=nd).max(1) / n
    return float((np.sum(draws >= obs) + 1) / (nd + 1))


def bh(ps):
    ps = np.array(ps); m = len(ps); o = np.argsort(ps); q = np.empty(m)
    q[o] = np.minimum.accumulate((ps[o] * m / np.arange(1, m + 1))[::-1])[::-1]
    return np.minimum(q, 1)


def analyse(texts, side="head", nmin=NMIN):
    ctx = numeral_contexts(texts)
    by = counts_by(ctx, side)
    rows = []
    for cls in "ST":
        allc = Counter()
        for h, cn in by[cls].items(): allc.update(cn)
        for h, cn in by[cls].items():
            if sum(cn.values()) < nmin: continue
            pool = allc.copy(); pool.subtract(cn); pool = +pool
            r = classify(cn, SUPPORT[cls]); r.update(sign=h, cls=cls, dist=dict(sorted(cn.items())),
                                                     p_spike=spike_perm(cn, pool))
            # numeral sign identity behind the modal value (layout-bound compounds, F7)
            ns = Counter(c["numsign"] for c in ctx if c[side] == h and c["cls"] == cls and c["value"] == r["spike_value"])
            r["modal_numsigns"] = dict(ns)
            rows.append(r)
    q = bh([r["p_spike"] for r in rows]) if rows else []
    for r, qq in zip(rows, q):
        r["q_spike"] = float(qq)
        cn = Counter({int(k): v for k, v in r["dist"].items()})
        r["p_uniform_to_cap"] = unif_gof(cn, SUPPORT[r["cls"]])
        if qq < 0.05 and r["spike_share"] >= 0.6:
            r["verdict"] = "lexeme-like"            # one value dominates, more than the pooled numerals allow
        elif qq < 0.05:
            r["verdict"] = "formula-preferring"     # significant preference, but no single dominant value
        elif (r["n_values"] >= 4 and cn.get(1, 0) > 0 and r["cap"] >= 6 and r["bic"]["capcal"] < r["bic"]["decay"]
              and r["p_uniform_to_cap"] > 0.05):
            r["verdict"] = "calendar-like"          # flat from 1 up to a hard cap (cap >= 6 so a cycle is visible)
        elif r["n_values"] >= 3 and r["spike_share"] < 0.6:
            r["verdict"] = "count-like"             # spread over several values, no dominant value
        else:
            r["verdict"] = "unclear"
    return rows, ctx, by


def unif_gof(cn, sup, nd=20000):
    """Permutation (multinomial) chi-square GOF to uniform on support values 1..max observed."""
    cap = max(cn); S = [s for s in sup if s <= cap]; n = sum(cn.values())
    x = np.array([cn.get(s, 0) for s in S], float); e = n / len(S)
    obs = np.sum((x - e) ** 2 / e)
    d = rng.multinomial(n, np.ones(len(S)) / len(S), size=nd)
    sim = np.sum((d - e) ** 2 / e, axis=1)
    return float((np.sum(sim >= obs) + 1) / (nd + 1))


if mode == "dev":
    R = {}
    for side in ("head", "prev"):
        rows, ctx, by = analyse(dev, side)
        R[side] = rows
        print(f"\n=== dev, numeral {'followed by' if side == 'head' else 'preceded by'} sign (n >= {NMIN}) ===")
        for r in sorted(rows, key=lambda r: (r["cls"], -r["n"])):
            print(f"{r['cls']} {r['sign']:6s} n={r['n']:3d} {r['verdict']:13s} best={r['best']:6s} spike {r['spike_value']}@{r['spike_share']:.2f}"
                  f" q={r['q_spike']:.3g} cap={r['cap']} a={r['decay_a']} {r['dist']} numsigns={r['modal_numsigns']}")
    # pooled distributions (all heads) per class
    ctx = numeral_contexts(dev)
    for cls in "ST":
        pc = Counter(c["value"] for c in ctx if c["cls"] == cls)
        R[f"pooled_{cls}"] = dict(sorted(pc.items()))
        print(cls, "pooled all numeral occurrences:", dict(sorted(pc.items())))
    # cap recurrence: caps of count-like / calendar-like heads
    caps = Counter(r["cap"] for r in R["head"] if r["verdict"] in ("count-like", "calendar-like"))
    R["caps_countlike_head"] = dict(caps)
    print("caps among count/calendar-like heads:", dict(caps))
    # context variability for count-like heads with n >= 20: site/object type chi-square permutation
    R["context_var"] = {}
    for r in R["head"]:
        if r["verdict"] != "count-like" or r["n"] < 20: continue
        cc = [c for c in ctx if c["head"] == r["sign"] and c["cls"] == r["cls"]]
        for key in ("site", "object_type"):
            g = [c[key] for c in cc]; v = [c["value"] for c in cc]
            if len(set(g)) < 2: continue
            def stat(vv):
                tab = defaultdict(Counter)
                for a, b in zip(g, vv): tab[a][b] += 1
                tot = Counter(vv); n = len(vv); s = 0
                for a in tab:
                    na = sum(tab[a].values())
                    for b in tot:
                        e = na * tot[b] / n; s += (tab[a][b] - e) ** 2 / e
                return s
            o = stat(v); nul = [stat(list(rng.permutation(v))) for _ in range(5000)]
            p = (np.sum(np.array(nul) >= o) + 1) / 5001
            R["context_var"][f"{r['sign']}_{key}"] = dict(groups=dict(Counter(g)), p=float(p))
            print(f"context variability {r['sign']} by {key}: groups {dict(Counter(g))} p={p:.3f}")
    json.dump(R, open(HERE / "f2_dev.json", "w"), indent=1, default=int)

else:
    R = {}
    devrows, _, _ = analyse(dev, "head")
    ctx_ho = numeral_contexts(ho)
    by_ho = counts_by(ctx_ho, "head")
    poolS = Counter(c["value"] for c in numeral_contexts(dev) if c["cls"] == "S" and c["head"])
    poolT = Counter(c["value"] for c in numeral_contexts(dev) if c["cls"] == "T" and c["head"])
    pool = {"S": poolS, "T": poolT}
    # N1: dev lexeme-like heads keep their spike value on held-out
    lex = [r for r in devrows if r["verdict"] == "lexeme-like"]
    k = n = 0; exp = 0.0; det = []
    for r in lex:
        cn = by_ho[r["cls"]].get(r["sign"], Counter())
        m = sum(cn.values()); hit = cn.get(r["spike_value"], 0)
        base = pool[r["cls"]][r["spike_value"]] / sum(pool[r["cls"]].values())
        k += hit; n += m; exp += m * base
        det.append(dict(sign=r["sign"], cls=r["cls"], value=r["spike_value"], ho_n=m, ho_hits=hit, base=round(base, 3),
                        ho_dist=dict(sorted(cn.items()))))
    # permutation p: hits under values drawn from the pooled dev class distribution
    sims = np.zeros(20000)
    for d in det:
        if d["ho_n"]:
            sims += rng.binomial(d["ho_n"], d["base"], 20000)
    p1 = float((np.sum(sims >= k) + 1) / 20001)
    ci = binomtest(k, n).proportion_ci(0.95, method="wilson") if n else None
    R["N1_lexeme_transfer"] = dict(hits=k, n=n, share=k / n if n else None, expected_share=exp / n if n else None,
                                   ci=[ci.low, ci.high] if ci else None, p=p1, details=det)
    print(f"N1 lexeme-like heads keep spike value on held-out: {k}/{n} = {k / n:.3f} (CI {ci.low:.2f}-{ci.high:.2f}); "
          f"expected from pooled {exp / n:.3f}; p={p1:.2g}")
    for d in det: print("   ", d)
    # N2: dev count-like heads stay spread on held-out (modal share < 0.6 over pooled held-out occurrences, >= 3 values)
    cnt = [r for r in devrows if r["verdict"] == "count-like"]
    agg = []
    for r in cnt:
        cn = by_ho[r["cls"]].get(r["sign"], Counter())
        agg.append(dict(sign=r["sign"], cls=r["cls"], ho_n=sum(cn.values()), ho_dist=dict(sorted(cn.items())),
                        modal_share=(max(cn.values()) / sum(cn.values())) if cn else None, n_values=len(cn)))
    tot = sum(a["ho_n"] for a in agg)
    modal = sum(max(by_ho[a["cls"]][a["sign"]].values()) for a in agg if a["ho_n"])
    R["N2_count_spread"] = dict(details=agg, pooled_modal_share=modal / tot if tot else None, n=tot)
    print(f"N2 count-like heads on held-out: pooled modal share {modal}/{tot} = {modal / max(tot, 1):.3f}")
    for a in agg: print("   ", a)
    # N4: jar M342 after short numerals takes 7 or 12
    cn = by_ho["S"].get("M342", Counter()); m = sum(cn.values()); hit = cn.get(7, 0) + cn.get(12, 0)
    base = (poolS[7] + poolS[12]) / sum(poolS.values())
    bt4 = binomtest(hit, m, base, alternative="greater") if m else None
    R["N4_jar_7_12"] = dict(hits=hit, n=m, share=hit / m if m else None, base=base, p=bt4.pvalue if bt4 else None,
                            ho_dist=dict(sorted(cn.items())))
    print(f"N4 M342 after short numerals in {{7,12}}: {hit}/{m} base {base:.3f} p={bt4.pvalue if bt4 else float('nan'):.3g}")
    # N2 Fisher: count-like modal share (at dev modal value) lower than lexeme hit share
    from scipy.stats import fisher_exact
    dm = {(r["cls"], r["sign"]): r["spike_value"] for r in cnt}
    kk = sum(by_ho[c][s].get(v, 0) for (c, s), v in dm.items()); nn = sum(sum(by_ho[c][s].values()) for (c, s) in dm)
    R["N2_count_spread"]["dev_modal_hits"] = kk; R["N2_count_spread"]["dev_modal_share"] = kk / nn if nn else None
    if nn and n:
        R["N2_count_spread"]["fisher_p_lower_than_N1"] = float(fisher_exact([[kk, nn - kk], [k, n - k]], alternative="less")[1])
    print(f"N2 count-like at dev modal value {kk}/{nn}; Fisher vs N1 p={R['N2_count_spread'].get('fisher_p_lower_than_N1')}")
    # N3: held-out + dev pooled classification (descriptive), and cap recurrence
    allrows, _, _ = analyse(dev + ho, "head")
    R["pooled_classification"] = allrows
    caps = Counter(r["cap"] for r in allrows if r["verdict"] in ("count-like", "calendar-like"))
    R["caps_pooled"] = dict(caps)
    R["calendar_like_pooled"] = [r["sign"] for r in allrows if r["verdict"] == "calendar-like"]
    print("pooled verdicts:", Counter(r["verdict"] for r in allrows), "caps", dict(caps),
          "calendar-like", R["calendar_like_pooled"])
    for r in sorted(allrows, key=lambda r: (r["cls"], -r["n"])):
        print(f"  {r['cls']} {r['sign']:6s} n={r['n']:3d} {r['verdict']:13s} spike {r['spike_value']}@{r['spike_share']:.2f} q={r['q_spike']:.3g} {r['dist']}")
    json.dump(R, open(HERE / "f2_heldout.json", "w"), indent=1, default=int)
