"""M99 relator test (board #42). Shared, frozen logic.

Split-attestation statistic (D2). For a host text t = L s R with s at a mid position
(len(L) >= 1, len(R) >= 1), the occurrence scores 1 when
  * L (the whole left part) is the END of some other text, and
  * R (the whole right part) is the START of some other text,
where "other text" means a distinct text outside the host's near-copy cluster.
A relator joining two independent units should split its texts into two text-like
pieces more often than position-, frequency- and span-length-matched signs.

Secondary statistic A (Fable plan 7 wording): mean of [L is a whole text elsewhere]
and [R is a whole text elsewhere].
"""
import math
import random
from collections import defaultdict


def lev1(a, b):
    """True if Levenshtein(a, b) <= 1."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def clusters(texts):
    """Greedy leader clustering (no chaining): texts sorted by (-len, seq); each text
    joins the first leader within one edit, else becomes a leader.
    Returns (cluster id per text, list of leader indices)."""
    order = sorted(range(len(texts)), key=lambda i: (-len(texts[i]), texts[i]))
    leaders, cid = [], [None] * len(texts)
    by_len = defaultdict(list)
    for i in order:
        t = texts[i]
        hit = None
        for L in (len(t) - 1, len(t), len(t) + 1):
            for j in by_len[L]:
                if lev1(t, texts[j]):
                    hit = j
                    break
            if hit is not None:
                break
        if hit is None:
            cid[i] = len(leaders)
            leaders.append(i)
            by_len[len(t)].append(i)
        else:
            cid[i] = cid[hit]
    return cid, leaders


class Pool:
    """Index of prefixes, suffixes and whole texts -> set of cluster ids."""

    def __init__(self, texts, cid):
        self.pre, self.suf, self.whole = defaultdict(set), defaultdict(set), defaultdict(set)
        for t, c in zip(texts, cid):
            self.whole[t].add(c)
            for k in range(1, len(t) + 1):
                self.pre[t[:k]].add(c)
                self.suf[t[-k:]].add(c)

    @staticmethod
    def _other(d, key, c):
        s = d.get(key)
        return bool(s) and (len(s) > 1 or c not in s)

    def d2(self, L, R, c):
        return int(self._other(self.suf, L, c) and self._other(self.pre, R, c))

    def a(self, L, R, c):
        return (self._other(self.whole, L, c) + self._other(self.whole, R, c)) / 2


def occurrences(hosts, host_cid, pool):
    """Per sign: list of (d2, a, lenL, lenR) over mid occurrences in the host texts."""
    occ = defaultdict(list)
    for t, c in zip(hosts, host_cid):
        n = len(t)
        for i in range(1, n - 1):
            L, R = t[:i], t[i + 1:]
            occ[t[i]].append((pool.d2(L, R, c), pool.a(L, R, c), i, n - 1 - i))
    return occ


def summarise(occ, min_occ):
    out = {}
    for s, v in occ.items():
        if len(v) < min_occ:
            continue
        n = len(v)
        out[s] = dict(n=n, d2=sum(x[0] for x in v) / n, a=sum(x[1] for x in v) / n,
                      mL=sum(x[2] for x in v) / n, mR=sum(x[3] for x in v) / n)
    return out


def matched_pct(summ, target, stat="d2", k=20):
    """Share of the k nearest candidate signs (log count, mean len L, mean len R)
    whose score is strictly below the target's. Returns (pct, n_matched, neighbours)."""
    if target not in summ:
        return None, 0, []
    T = summ[target]
    cand = [s for s in summ if s != target]

    def dist(s):
        S = summ[s]
        return ((math.log(S["n"]) - math.log(T["n"])) ** 2 + (S["mL"] - T["mL"]) ** 2
                + (S["mR"] - T["mR"]) ** 2)

    nb = sorted(cand, key=lambda s: (dist(s), s))[:k]
    if not nb:
        return None, 0, []
    pct = sum(summ[s][stat] < T[stat] for s in nb) / len(nb)
    return pct, len(nb), nb


def run_test(pool_texts, host_idx, targets, min_occ=8, k=20, n_shuffle=200, seed=0,
             stats=("d2", "a")):
    """pool_texts: list of distinct tuples. host_idx: indices (into pool_texts) of the
    host texts; only cluster leaders among them are used as hosts.
    Returns dict per target: observed score, matched percentile, shuffle p."""
    cid, leaders = clusters(pool_texts)
    lead = set(leaders)
    hidx = [i for i in host_idx if i in lead]
    pool = Pool(pool_texts, cid)
    occ = occurrences([pool_texts[i] for i in hidx], [cid[i] for i in hidx], pool)
    summ = summarise(occ, min_occ)
    res = {"n_pool": len(pool_texts), "n_hosts": len(hidx), "n_candidates": len(summ)}
    rng = random.Random(seed)
    null = {t: [] for t in targets}
    for _ in range(n_shuffle):
        sh = []
        for t in pool_texts:
            x = list(t)
            rng.shuffle(x)
            sh.append(tuple(x))
        p2 = Pool(sh, cid)
        o2 = occurrences([sh[i] for i in hidx], [cid[i] for i in hidx], p2)
        for t in targets:
            v = o2.get(t, [])
            null[t].append(sum(x[0] for x in v) / len(v) if v else 0.0)
    for t in targets:
        r = {"n_occ": len(occ.get(t, []))}
        if t in summ:
            r.update({k_: summ[t][k_] for k_ in ("d2", "a", "mL", "mR")})
            for st in stats:
                pct, nm, nb = matched_pct(summ, t, st, k)
                r[f"pct_{st}"], r["n_matched"] = pct, nm
                if st == "d2":
                    r["neighbours"] = nb
            obs = summ[t]["d2"]
            r["shuffle_mean"] = sum(null[t]) / max(1, len(null[t]))
            r["p_shuffle"] = (1 + sum(x >= obs for x in null[t])) / (1 + len(null[t])) if n_shuffle else None
            r["flag"] = bool(r["pct_d2"] is not None and r["pct_d2"] >= 0.95
                             and r["n_matched"] >= 10
                             and (r["p_shuffle"] is None or r["p_shuffle"] < 0.05))
        else:
            r["flag"] = False
        res[t] = r
    res["summ"] = summ
    return res
