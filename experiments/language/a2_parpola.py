"""A2. Parpola's / Mahadevan's Dravidian readings vs the corpus. Predictions frozen in a2_predictions.json.
Run: .venv/bin/python experiments/language/a2_parpola.py
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from corpus.load import dev_heldout, runs  # noqa

P = json.load(open(HERE / "a2_predictions.json"))
SS = P["sign_sets"]
FISH0 = set(SS["fish_plain"]); FISHM = set(SS["fish_family_marked"]); FISH = FISH0 | FISHM
NUM = {s: int(v) for v, ss in SS["short_numerals"].items() for s in ss}
rng = random.Random(11)


def get_runs(texts):
    return [r for t in texts for r in runs(t["seq"])]


def p1(rr, fishset):
    k, N = Counter(), Counter()
    for r in rr:
        for a, b in zip(r, r[1:]):
            if a in NUM:
                N[NUM[a]] += 1; k[NUM[a]] += b in fishset
    tot_k, tot_N = sum(k.values()), sum(N.values())
    p = tot_k / tot_N
    rows = {}
    for n in sorted(N):
        bt = stats.binomtest(k[n], N[n], p, alternative="greater")
        rows[n] = dict(N=N[n], fish=k[n], rate=round(k[n] / N[n], 3), p_greater=round(bt.pvalue, 4))
    # permutation: asterism values {6,7} excess vs others
    labels = [n for n in N for _ in range(N[n])]
    fol = [1] * tot_k + [0] * (tot_N - tot_k)

    def stat(lbl, f):
        a = [x for l, x in zip(lbl, f) if l in (6, 7)]
        b = [x for l, x in zip(lbl, f) if l not in (3, 6, 7)]
        return (np.mean(a) if a else 0) - (np.mean(b) if b else 0)
    # observed: need aligned labels/followers
    obs_l, obs_f = [], []
    for r in rr:
        for a, b in zip(r, r[1:]):
            if a in NUM:
                obs_l.append(NUM[a]); obs_f.append(int(b in fishset))
    obs = stat(obs_l, obs_f)
    null = []
    f2 = list(obs_f)
    for _ in range(5000):
        rng.shuffle(f2); null.append(stat(obs_l, f2))
    null = np.array(null)
    return dict(pooled_rate=round(p, 3), by_value=rows, stat_67_minus_nonasterism=round(obs, 3),
                perm_p=round((1 + (null >= obs).sum()) / 5001, 4))


def ctx_vectors(rr):
    L, R, pos = defaultdict(Counter), defaultdict(Counter), defaultdict(list)
    for r in rr:
        n = len(r)
        for i, s in enumerate(r):
            L[s]["<S>" if i == 0 else r[i - 1]] += 1
            R[s]["<E>" if i == n - 1 else r[i + 1]] += 1
            if n > 1:
                pos[s].append(i / (n - 1))
    return L, R, pos


def cos(c1, c2):
    keys = set(c1) | set(c2)
    a = np.array([c1.get(k, 0) for k in keys], float); b = np.array([c2.get(k, 0) for k in keys], float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def p2(rr):
    L, R, pos = ctx_vectors(rr)
    freq = Counter(s for r in rr for s in r)
    out = {}
    for m in sorted(FISHM, key=lambda s: int(s[1:])):
        if freq[m] < 5:
            continue
        sim = 0.5 * (cos(L[m], L["M59"]) + cos(R[m], R["M59"]))
        pool = [s for s in freq if s not in FISH and freq[m] / 2 <= freq[s] <= freq[m] * 2]
        ns = [0.5 * (cos(L[s], L["M59"]) + cos(R[s], R["M59"])) for s in pool]
        out[m] = dict(freq=freq[m], sim_to_M59=round(sim, 3), null_mean=round(float(np.mean(ns)), 3),
                      null_p95=round(float(np.percentile(ns, 95)), 3), n_null=len(pool),
                      percentile=round(float(np.mean(np.array(ns) < sim)), 3),
                      mean_pos=round(float(np.mean(pos[m])), 2) if pos[m] else None)
    out["M59_mean_pos"] = round(float(np.mean(pos["M59"])), 2)
    return out


def p3(rr):
    def counts(runs_):
        both = adj = 0
        for r in runs_:
            s = set(r)
            if s & FISH0 and s & FISHM:
                both += 1
            for a, b in zip(r, r[1:]):
                if (a in FISH0 and b in FISHM) or (a in FISHM and b in FISH0):
                    adj += 1
        return both, adj
    ob, oa = counts(rr)
    toks = [s for r in rr for s in r]
    nb, na = [], []
    for _ in range(2000):
        rng.shuffle(toks)
        it = iter(toks)
        sh = [[next(it) for _ in r] for r in rr]
        b, a = counts(sh); nb.append(b); na.append(a)
    nb, na = np.array(nb), np.array(na)
    return dict(texts_with_both=ob, null_mean=round(nb.mean(), 1), p_low=round(float((nb <= ob).mean()), 4),
                p_high=round(float((nb >= ob).mean()), 4), adjacent=oa, adj_null_mean=round(na.mean(), 1),
                adj_p_high=round(float((na >= oa).mean()), 4), adj_p_low=round(float((na <= oa).mean()), 4))


def p4(rr):
    def rate(S):
        k = n = 0
        for r in rr:
            for i, s in enumerate(r):
                if s in S:
                    n += 1; k += i > 0 and r[i - 1] in NUM
        return k, n
    k0, n0 = rate(FISH0); k1, n1 = rate(FISHM)
    odds, p = stats.fisher_exact([[k0, n0 - k0], [k1, n1 - k1]], alternative="greater")
    return dict(plain=[k0, n0, round(k0 / n0, 3)], marked=[k1, n1, round(k1 / max(1, n1), 3)], fisher_p_plain_greater=round(p, 4))


def p5(rr):
    freq = Counter(s for r in rr for s in r)
    fin = Counter(r[-1] for r in rr if len(r) > 1)
    tot = Counter(s for r in rr if len(r) > 1 for s in r)
    jar = "M342"
    final_share = fin[jar] / tot[jar]
    exp_final = sum(1 for r in rr if len(r) > 1) / sum(tot.values())

    def left_div(s, n=60, reps=200):
        lefts = [r[i - 1] for r in rr for i in range(1, len(r)) if r[i] == s]
        if len(lefts) < n:
            return None
        return float(np.mean([len(set(rng.sample(lefts, n))) for _ in range(reps)]))
    jd = left_div(jar)
    pool = [s for s in freq if freq[s] >= 120 and s != jar]
    nd = [d for d in (left_div(s) for s in pool) if d is not None]
    # alternation: texts identical except final sign; alternants of the jar
    stem_final = defaultdict(set)
    for r in rr:
        if len(r) > 1:
            stem_final[tuple(r[:-1])].add(r[-1])
    alts = Counter()
    for st, f in stem_final.items():
        if jar in f:
            for x in f - {jar}:
                alts[x] += 1
    return dict(final_share=round(final_share, 3), final_expected_if_uniform=round(exp_final, 3),
                left_diversity_at_60=round(jd, 1), null_signs=len(nd), null_mean=round(float(np.mean(nd)), 1),
                null_max=round(float(np.max(nd)), 1), percentile=round(float(np.mean(np.array(nd) < jd)), 3),
                stems_with_jar=sum(1 for f in stem_final.values() if jar in f),
                stems_where_jar_alternates=sum(1 for f in stem_final.values() if jar in f and len(f) > 1),
                top_alternants=alts.most_common(8))


def main():
    dev, ho = dev_heldout()
    res = {"tests_run": "P1 (2 fish sets x 3 splits), P2 (per marked sign), P3, P4, P5 (3 parts); see each block"}
    for name, texts in [("dev", dev), ("heldout", ho), ("all", dev + ho)]:
        rr = get_runs(texts)
        res[name] = dict(n_texts=len(texts),
                         P1_fishfamily=p1(rr, FISH), P1_plainfish=p1(rr, FISH0),
                         P2=p2(rr), P3=p3(rr), P4=p4(rr), P5=p5(rr))
        print(name, json.dumps(res[name]["P1_fishfamily"]), "\n")
    json.dump(res, open(HERE / "out" / "a2_parpola.json", "w"), indent=1, default=float)
    print(json.dumps(res["all"], indent=1, default=float))


if __name__ == "__main__":
    main()
