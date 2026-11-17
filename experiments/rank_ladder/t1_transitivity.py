"""T1: is pairwise precedence among frame signs transitive (a ladder)?

For every distinct text, every ordered pair of frame features (a before b, same line) is
counted once per text. A pair is 'defined' when it co-occurs in >= MIN texts; its direction
is the majority (ties dropped). Statistics:
  cyc   = share of cyclic (intransitive) triads among triads whose 3 edges are all defined
  viol  = share of pair observations that disagree with the best linear order
          (minimum weighted feedback arc set, local search)
Null: signs shuffled within each text (keeps composition and length), same pipeline.
A random tournament has cyc = 0.25.
Usage: t1_transitivity.py dev|heldout
  dev:     ladder built on M77 dev (v2) and on ICIT dev; nulls on both.
  heldout: frozen dev ladders predict pair directions on M77 held-out v2 and ICIT held-out.
"""
import json, random, sys, itertools
from collections import Counter, defaultdict
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import (icit_texts, dev_heldout, heldout_keys, lines, W2F, M2F, HERE)

MIN = 3
NULL = 500


def m77_sets():
    dev, ho = dev_heldout(version=2)
    return dev, ho


def icit_sets():
    held = heldout_keys()
    seen, dev, ho = set(), [], []
    for t in icit_texts():
        k = " ".join(t["seq"])
        if k in seen:
            continue
        seen.add(k)
        (ho if k in held else dev).append(t)
    return dev, ho


def feat_lines(texts, mp):
    out = []
    for t in texts:
        ls = []
        for l in lines(t["seq"]):
            ls.append([mp.get(s) for s in l if s != "#"])  # keep non-frame as None for shuffles
        out.append(ls)
    return out


def pair_counts(FL):
    C = Counter()
    for ls in FL:
        seen = set()
        for l in ls:
            f = [x for x in l if x]
            for i in range(len(f)):
                for j in range(i + 1, len(f)):
                    if f[i] != f[j]:
                        seen.add((f[i], f[j]))
        for p in seen:
            C[p] += 1
    return C


def tournament(C):
    nodes = sorted({a for a, b in C} | {b for a, b in C})
    E = {}
    for a, b in itertools.combinations(nodes, 2):
        ab, ba = C.get((a, b), 0), C.get((b, a), 0)
        if ab + ba >= MIN and ab != ba:
            E[(a, b)] = 1 if ab > ba else -1
    return nodes, E


def cyc_share(nodes, E):
    def d(a, b):
        if (a, b) in E:
            return E[(a, b)]
        if (b, a) in E:
            return -E[(b, a)]
        return None
    tri = cyc = 0
    for a, b, c in itertools.combinations(nodes, 3):
        x, y, z = d(a, b), d(b, c), d(a, c)
        if None in (x, y, z):
            continue
        tri += 1
        # cycle iff a>b>c>a or reverse: x==y and z==-x
        if x == y and z == -x:
            cyc += 1
    return cyc, tri


def best_order(C, nodes, seed=0):
    rng = random.Random(seed)
    # start from Copeland-like score
    score = {n: 0 for n in nodes}
    for (a, b), k in C.items():
        if a in score and b in score:
            score[a] += k; score[b] -= k
    order = sorted(nodes, key=lambda n: -score[n])

    def cost(o):
        pos = {n: i for i, n in enumerate(o)}
        return sum(k for (a, b), k in C.items() if a in pos and b in pos and pos[a] > pos[b])
    best = cost(order)
    improved = True
    while improved:
        improved = False
        for i in range(len(order)):
            for j in range(len(order)):
                if i == j:
                    continue
                o = order[:]; n = o.pop(i); o.insert(j, n)
                c = cost(o)
                if c < best:
                    best, order, improved = c, o, True
    tot = sum(k for (a, b), k in C.items() if a in nodes and b in nodes)
    return order, best, tot


def stats(FL):
    C = pair_counts(FL)
    nodes, E = tournament(C)
    cyc, tri = cyc_share(nodes, E)
    # restrict order cost to defined pairs' observations
    Cd = Counter({p: k for p, k in C.items() if (p in E or p[::-1] in E)})
    order, viol, tot = best_order(Cd, nodes)
    return dict(n_texts=len(FL), n_nodes=len(nodes), n_edges=len(E), triads=tri, cyclic=cyc,
                cyc_share=cyc / tri if tri else None, viol=viol, obs=tot,
                viol_share=viol / tot if tot else None, order=order)


def shuffle_FL(FL, rng):
    out = []
    for ls in FL:
        nl = []
        for l in ls:
            l2 = l[:]; rng.shuffle(l2); nl.append(l2)
        out.append(nl)
    return out


def run_dev():
    res = {}
    for name, (dev, _), mp in (("M77", m77_sets(), M2F), ("ICIT", icit_sets(), W2F)):
        FL = feat_lines(dev, mp)
        s = stats(FL)
        rng = random.Random(7)
        nc, nv = [], []
        for _ in range(NULL):
            FLs = shuffle_FL(FL, rng)
            C = pair_counts(FLs); nodes, E = tournament(C)
            c, t = cyc_share(nodes, E)
            nc.append(c / t if t else 0.25)
            Cd = Counter({p: k for p, k in C.items() if (p in E or p[::-1] in E)})
            _, v, tot = best_order(Cd, nodes)
            nv.append(v / tot if tot else 0.5)
            if len(nc) >= 200:
                break
        s["null_cyc_mean"] = sum(nc) / len(nc)
        s["null_cyc_min"] = min(nc)
        s["p_cyc"] = (1 + sum(x <= s["cyc_share"] for x in nc)) / (1 + len(nc))
        s["null_viol_mean"] = sum(nv) / len(nv)
        s["null_viol_min"] = min(nv)
        s["p_viol"] = (1 + sum(x <= s["viol_share"] for x in nv)) / (1 + len(nv))
        s["n_null"] = len(nc)
        # list cyclic triads and weakest edges for the report
        C = pair_counts(FL); nodes, E = tournament(C)
        s["edges"] = {f"{a}>{b}" if v == 1 else f"{b}>{a}": [C.get((a, b), 0), C.get((b, a), 0)]
                      for (a, b), v in E.items()}
        res[name] = s
        print(name, {k: v for k, v in s.items() if k not in ("edges",)})
    json.dump(res, open(HERE / "t1_dev.json", "w"), indent=1)


def run_heldout():
    dv = json.load(open(HERE / "t1_dev.json"))
    res = {}
    for name, (_, ho), mp in (("M77", m77_sets(), M2F), ("ICIT", icit_sets(), W2F)):
        order = dv[name]["order"]
        pos = {n: i for i, n in enumerate(order)}
        FL = feat_lines(ho, mp)
        C = pair_counts(FL)
        agree = dis = 0
        pair_agree = pair_dis = 0
        for (a, b), k in C.items():
            if a in pos and b in pos:
                if pos[a] < pos[b]:
                    agree += k
                else:
                    dis += k
        # pair level: held-out majority direction vs dev order, pairs with >=MIN held-out texts
        done = set()
        for (a, b) in C:
            if a not in pos or b not in pos or frozenset((a, b)) in done:
                continue
            done.add(frozenset((a, b)))
            ab, ba = C.get((a, b), 0), C.get((b, a), 0)
            if ab + ba < MIN or ab == ba:
                continue
            fwd = ab if pos[a] < pos[b] else ba
            bwd = ba if pos[a] < pos[b] else ab
            if fwd > bwd:
                pair_agree += 1
            else:
                pair_dis += 1
        from scipy.stats import binomtest
        n = agree + dis
        s = stats(FL)
        res[name] = dict(obs_agree=agree, obs_total=n, obs_share=agree / n if n else None,
                         p_obs=binomtest(agree, n, 0.5, alternative="greater").pvalue if n else None,
                         pairs_agree=pair_agree, pairs_total=pair_agree + pair_dis,
                         pairs_share=pair_agree / (pair_agree + pair_dis) if pair_agree + pair_dis else None,
                         p_pairs=binomtest(pair_agree, pair_agree + pair_dis, 0.5, alternative="greater").pvalue,
                         heldout_cyc=s["cyclic"], heldout_triads=s["triads"], heldout_viol_share=s["viol_share"])
        print(name, res[name])
    json.dump(res, open(HERE / "t1_heldout.json", "w"), indent=1)


if __name__ == "__main__":
    {"dev": run_dev, "heldout": run_heldout}[sys.argv[1]]()
