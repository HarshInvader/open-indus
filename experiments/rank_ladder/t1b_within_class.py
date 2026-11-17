"""T1b: is there a ladder INSIDE a slot class (Baer: stacked titles in a fixed rank order),
beyond the trivial opener < title < closer < post-closer template?

Classes: OPEN = OP*, CN*; TITLE = TI*, TB*, MJ*; CLOSE = CL*, PC*.
Statistic: share of within-class pair observations (texts where two different same-class
frame signs co-occur in one line) that agree with the best within-class linear order;
plus cyclic triads among within-class defined edges.
Null: in every text, frame signs of one class are permuted among the positions that class
occupies (between-class template kept, within-class order randomised).
Usage: t1b_within_class.py dev|heldout
"""
import json, random, sys, itertools
from collections import Counter
sys.path.insert(0, __import__("os").path.dirname(__file__))
from t1_transitivity import m77_sets, icit_sets, feat_lines, pair_counts, tournament, cyc_share, best_order, MIN
from common import W2F, M2F, HERE

CLS = {"OP": "OPEN", "CN": "OPEN", "TI": "TITLE", "TB": "TITLE", "MJ": "TITLE", "CL": "CLOSE", "PC": "CLOSE"}
cls = lambda f: CLS[f[:2]]


def within(C):
    return Counter({p: k for p, k in C.items() if cls(p[0]) == cls(p[1])})


def stat(FL):
    C = within(pair_counts(FL))
    out = {}
    for c in ("OPEN", "TITLE", "CLOSE", "ALL"):
        Cc = Counter({p: k for p, k in C.items() if c == "ALL" or cls(p[0]) == c})
        nodes, E = tournament(Cc)
        cy, tri = cyc_share(nodes, E) if c != "ALL" else (None, None)
        Cd = Counter({p: k for p, k in Cc.items() if (p in E or p[::-1] in E)})
        if c == "ALL":
            # sum over classes of best within-class orders
            out[c] = None
            continue
        order, v, tot = best_order(Cd, nodes)
        out[c] = dict(nodes=len(nodes), edges=len(E), triads=tri, cyclic=cy, viol=v, obs=tot,
                      agree_share=1 - v / tot if tot else None, order=order)
    tv = sum(out[c]["viol"] for c in ("OPEN", "TITLE", "CLOSE"))
    to = sum(out[c]["obs"] for c in ("OPEN", "TITLE", "CLOSE"))
    out["ALL"] = dict(viol=tv, obs=to, agree_share=1 - tv / to if to else None)
    return out


def shuffle_within(FL, rng):
    out = []
    for ls in FL:
        nl = []
        for l in ls:
            l2 = l[:]
            for c in ("OPEN", "TITLE", "CLOSE"):
                idx = [i for i, x in enumerate(l2) if x and cls(x) == c]
                vals = [l2[i] for i in idx]; rng.shuffle(vals)
                for i, v in zip(idx, vals):
                    l2[i] = v
            nl.append(l2)
        out.append(nl)
    return out


def dev():
    res = {}
    for name, (d, _), mp in (("M77", m77_sets(), M2F), ("ICIT", icit_sets(), W2F)):
        FL = feat_lines(d, mp)
        s = stat(FL)
        rng = random.Random(11)
        nulls = [stat(shuffle_within(FL, rng)) for _ in range(200)]
        for c in ("OPEN", "TITLE", "CLOSE", "ALL"):
            nv = [n[c]["agree_share"] for n in nulls if n[c]["agree_share"] is not None]
            s[c]["null_agree_mean"] = sum(nv) / len(nv)
            s[c]["null_agree_p95"] = sorted(nv)[int(0.95 * len(nv))]
            s[c]["p"] = (1 + sum(x >= s[c]["agree_share"] for x in nv)) / (1 + len(nv))
            if c != "ALL":
                nc = [n[c]["cyclic"] / n[c]["triads"] for n in nulls if n[c]["triads"]]
                s[c]["null_cyc_share"] = sum(nc) / len(nc) if nc else None
        res[name] = s
        for c in ("OPEN", "TITLE", "CLOSE", "ALL"):
            print(name, c, s[c])
    json.dump(res, open(HERE / "t1b_dev.json", "w"), indent=1)


def heldout():
    from scipy.stats import binomtest
    dv = json.load(open(HERE / "t1b_dev.json"))
    res = {}
    for name, (_, h), mp in (("M77", m77_sets(), M2F), ("ICIT", icit_sets(), W2F)):
        C = within(pair_counts(feat_lines(h, mp)))
        tot_a = tot_n = 0
        r = {}
        for c in ("OPEN", "TITLE", "CLOSE"):
            pos = {n: i for i, n in enumerate(dv[name][c]["order"])}
            a = n = 0
            for (x, y), k in C.items():
                if cls(x) == c and x in pos and y in pos:
                    n += k; a += k if pos[x] < pos[y] else 0
            r[c] = dict(agree=a, n=n, share=a / n if n else None)
            tot_a += a; tot_n += n
        # null for held-out: within-class shuffle of held-out texts, scored against the dev order
        FL = feat_lines(h, mp)
        rng = random.Random(12); nv = []
        for _ in range(500):
            Cn = within(pair_counts(shuffle_within(FL, rng)))
            a = n = 0
            for c in ("OPEN", "TITLE", "CLOSE"):
                pos = {q: i for i, q in enumerate(dv[name][c]["order"])}
                for (x, y), k in Cn.items():
                    if cls(x) == c and x in pos and y in pos:
                        n += k; a += k if pos[x] < pos[y] else 0
            nv.append(a / n if n else 0.5)
        r["ALL"] = dict(agree=tot_a, n=tot_n, share=tot_a / tot_n, null_mean=sum(nv) / len(nv),
                        p=(1 + sum(x >= tot_a / tot_n for x in nv)) / (1 + len(nv)))
        res[name] = r
        print(name, r)
    json.dump(res, open(HERE / "t1b_heldout.json", "w"), indent=1)


if __name__ == "__main__":
    {"dev": dev, "heldout": heldout}[sys.argv[1]]()
