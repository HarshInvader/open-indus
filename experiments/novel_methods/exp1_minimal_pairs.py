"""Exp 1. Minimal pairs, substitution matrix, optional signs (genomics: BLOSUM /
indel spectra; manuscript stemmatics: near-duplicate families).

Questions
 Q1  Are Indus texts organised in near-duplicate families (edit distance 1)
     more than an adjacency (bigram) process predicts?
 Q2  WHERE in the text does variation sit (first / medial / last), and is
     that different from the null?
 Q3  WHICH signs substitute for each other in identical frames (paradigms)
     and WHICH signs are optional (indels)?
 Q4  Do dev substitution classes predict held-out substitutions?

Comparison: bigram null (k=1), trigram null (k=2), unigram shuffle,
synthetic seal legends written logo-syllabically, synthetic slot code.
"""
from itertools import combinations

from common import *

NREP = 20


MINLEN = 3  # both texts of a substitution pair, the longer text of an indel pair


def neighbours(texts):
    """All edit-distance-1 pairs. Returns list of (i, j, kind, pos_info, a, b)
    kind 'sub': same length, position p differs, a->b
    kind 'ind': texts[j] = texts[i] with sign b inserted at p (a=None)"""
    idx = {t: i for i, t in enumerate(texts)}
    frames = defaultdict(list)
    for i, t in enumerate(texts):
        for p in range(len(t)):
            frames[(t[:p], t[p + 1:])].append((i, p))
    pairs = []
    for (pre, suf), lst in frames.items():
        for (i, p), (j, _) in combinations(lst, 2):
            if len(texts[i]) < MINLEN:
                continue
            pairs.append((i, j, "sub", (p, len(texts[i])), texts[i][p], texts[j][p]))
        # indel: shorter text pre+suf exists?
        short = pre + suf
        if len(short) >= MINLEN - 1 and short in idx:
            for (j, p) in lst:
                pairs.append((idx[short], j, "ind", (p, len(texts[j])), None, texts[j][p]))
    return pairs


def relpos(p, n):
    if n == 1:
        return "only"
    return "first" if p == 0 else ("last" if p == n - 1 else "mid")


def summarise(texts):
    pr = neighbours(texts)
    n = len(texts)
    has = set()
    for i, j, *_ in pr:
        has.add(i); has.add(j)
    subs = [x for x in pr if x[2] == "sub"]
    ind = [x for x in pr if x[2] == "ind"]
    # families: connected components
    parent = list(range(n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, j, *_ in pr:
        parent[f(i)] = f(j)
    comp = Counter(f(i) for i in range(n))
    sizes = sorted(comp.values(), reverse=True)
    # only texts of length >=3 for positional stats (position classes meaningful)
    sp = Counter(relpos(*x[3]) for x in subs if x[3][1] >= 3)
    ip = Counter(relpos(*x[3]) for x in ind if x[3][1] >= 3)
    tot_s = sum(sp.values()) or 1
    tot_i = sum(ip.values()) or 1
    return dict(
        n=n,
        frac_with_neighbour=len(has) / n,
        sub_per_text=len(subs) / n,
        ind_per_text=len(ind) / n,
        largest_family=sizes[0],
        n_families_ge3=sum(s >= 3 for s in sizes),
        sub_first=sp["first"] / tot_s, sub_mid=sp["mid"] / tot_s, sub_last=sp["last"] / tot_s,
        ind_first=ip["first"] / tot_i, ind_mid=ip["mid"] / tot_i, ind_last=ip["last"] / tot_i,
    ), pr


def positional_baseline(texts):
    """Share of positions (len>=3 texts) that are first/mid/last, the
    'uniform' expectation for where variation would sit."""
    c = Counter()
    for t in texts:
        if len(t) >= 3:
            c["first"] += 1; c["last"] += 1; c["mid"] += len(t) - 2
    s = sum(c.values())
    return {k: v / s for k, v in c.items()}


def main():
    rng = np.random.default_rng(20261114)
    D, H = load_split()
    res = {}
    obs, pr = summarise(D)
    res["indus_dev"] = obs
    res["indus_heldout_alone"] = summarise(H)[0]
    res["positional_baseline_dev"] = positional_baseline(D)
    nulls = {"bigram": [], "trigram": [], "shuffle": [], "names": [], "slotcode": []}
    m1, m2 = Markov(D, 1), Markov(D, 2)
    sub_null = [Counter() for _ in range(NREP)]
    ind_null = [Counter() for _ in range(NREP)]
    for r in range(NREP):
        N1 = null_corpus(D, rng, model=m1)
        s1, p1 = summarise(N1)
        nulls["bigram"].append(s1)
        for x in p1:
            if x[2] == "sub":
                sub_null[r][tuple(sorted((x[4], x[5])))] += 1
            else:
                ind_null[r][x[5]] += 1
        nulls["trigram"].append(summarise(null_corpus(D, rng, model=m2))[0])
        nulls["shuffle"].append(summarise(shuffle_corpus(D, rng))[0])
        if r < 5:
            nulls["names"].append(summarise(names_corpus(len(D), rng))[0])
            nulls["slotcode"].append(summarise(slotcode_corpus(len(D), rng))[0])
    table = {}
    for k, lst in nulls.items():
        table[k] = {m: (float(np.mean([x[m] for x in lst])), float(np.std([x[m] for x in lst]))) for m in obs}
    res["nulls"] = table
    print("metric".ljust(22), "indus", *[k.ljust(14) for k in table])
    for m in obs:
        print(m.ljust(22), ("%.3f" % obs[m]).ljust(8),
              *[("%.3f+-%.3f" % table[k][m]).ljust(14) for k in table])
    # z-scores vs bigram / trigram
    res["z_vs_bigram"] = {m: (obs[m] - table["bigram"][m][0]) / (table["bigram"][m][1] or 1e-9) for m in obs}
    res["z_vs_trigram"] = {m: (obs[m] - table["trigram"][m][0]) / (table["trigram"][m][1] or 1e-9) for m in obs}
    print("z vs bigram", {k: round(v, 1) for k, v in res["z_vs_bigram"].items()})
    print("z vs trigram", {k: round(v, 1) for k, v in res["z_vs_trigram"].items()})

    # ---- Q3 substitution matrix (sign pairs) and optional signs
    freq = Counter(s for t in D for s in t)
    sub = Counter(); ind = Counter(); subpos = defaultdict(Counter); indpos = defaultdict(Counter)
    for i, j, kind, (p, n), a, b in pr:
        if kind == "sub":
            k = tuple(sorted((a, b))); sub[k] += 1; subpos[k][relpos(p, n)] += 1
        else:
            ind[b] += 1; indpos[b][relpos(p, n)] += 1
    exp_sub = Counter()
    for c in sub_null:
        for k, v in c.items():
            exp_sub[k] += v / NREP
    rows = []
    for k, v in sub.most_common():
        e = exp_sub.get(k, 0.0)
        nullvals = [c.get(k, 0) for c in sub_null]
        p_emp = (1 + sum(x >= v for x in nullvals)) / (NREP + 1)
        rows.append(dict(pair=k, obs=v, exp_bigram=round(e, 2), log2_odds=round(float(np.log2((v + .5) / (e + .5))), 2),
                         p_emp=p_emp, pos=dict(subpos[k])))
    res["top_substitutions"] = rows[:60]
    print("\nTop substitution pairs (obs, bigram-null exp, positions):")
    for r in rows[:30]:
        print(r)
    exp_ind = Counter()
    for c in ind_null:
        for k, v in c.items():
            exp_ind[k] += v / NREP
    irows = []
    for s, v in ind.most_common(40):
        irows.append(dict(sign=s, indels=v, freq=freq[s], rate=round(v / freq[s], 3),
                          exp_bigram=round(exp_ind.get(s, 0), 2), pos=dict(indpos[s])))
    res["top_optional_signs"] = irows
    print("\nTop optional (inserted/deleted) signs:")
    for r in irows[:25]:
        print(r)

    # ---- substitution graph communities (paradigm classes) on dev
    import networkx as nx
    G = nx.Graph()
    for (a, b), v in sub.items():
        if a != b:
            G.add_edge(a, b, weight=v)
    comms = nx.community.louvain_communities(G, weight="weight", seed=1, resolution=1.0)
    comms = sorted(comms, key=lambda c: -sum(freq[s] for s in c))
    cid = {s: k for k, c in enumerate(comms) for s in c}
    res["paradigm_classes"] = [sorted(c, key=lambda s: -freq[s])[:15] for c in comms[:12]]
    mod = nx.community.modularity(G, comms, weight="weight")
    res["paradigm_modularity"] = mod
    print("\nSubstitution-graph communities (modularity %.3f):" % mod)
    for c in res["paradigm_classes"]:
        print("  ", c)

    # ---- Q4 held-out: pairs involving at least one held-out text
    ALL = sorted(set(D) | set(H))
    hset = set(H)
    _, prA = summarise(ALL)
    ho_sub = [(ALL[i], ALL[j], a, b) for i, j, kind, _, a, b in prA
              if kind == "sub" and (ALL[i] in hset or ALL[j] in hset) and a in G and b in G]
    seen_edge = sum(G.has_edge(a, b) for *_, a, b in ho_sub)
    same_comm = sum(cid.get(a) == cid.get(b) for *_, a, b in ho_sub)
    # null: replace b by a random graph node with same frequency rank band
    nodes = list(G.nodes())
    nf = np.array([freq[s] for s in nodes], float)
    ordr = np.argsort(nf)
    rank = {nodes[k]: r for r, k in enumerate(ordr)}
    sims_e, sims_c = [], []
    for _ in range(500):
        e = c = 0
        for *_, a, b in ho_sub:
            r = rank[b]
            lo, hi = max(0, r - 5), min(len(nodes), r + 6)
            bb = nodes[ordr[rng.integers(lo, hi)]]
            e += G.has_edge(a, bb); c += cid.get(a) == cid.get(bb)
        sims_e.append(e); sims_c.append(c)
    res["heldout_substitutions"] = dict(
        n=len(ho_sub), seen_as_dev_edge=seen_edge, null_edge=(float(np.mean(sims_e)), float(np.std(sims_e))),
        same_dev_class=same_comm, null_same_class=(float(np.mean(sims_c)), float(np.std(sims_c))),
        p_edge=(1 + sum(x >= seen_edge for x in sims_e)) / 501, p_class=(1 + sum(x >= same_comm for x in sims_c)) / 501)
    print("\nHeld-out substitutions:", res["heldout_substitutions"])

    # held-out texts: fraction with an ED-1 neighbour in dev, vs bigram-null texts
    Dset = set(D)

    def has_dev_nb(t):
        for p in range(len(t)):
            for d in (t[:p] + t[p + 1:],):
                if d in Dset:
                    return True
        frames = set()
        return False
    dframes = set()
    for t in D:
        for p in range(len(t)):
            dframes.add((t[:p], t[p + 1:]))
            dframes.add(("DEL",) + t[:p] + t[p + 1:])
    def nb(t):
        if any((t[:p], t[p + 1:]) in dframes for p in range(len(t))):
            return True  # substitution (or identical frame)
        if any(t[:p] + t[p + 1:] in Dset for p in range(len(t))):
            return True  # t = dev text + insertion
        if ("DEL",) + t in dframes:
            return True  # t = dev text with one deletion
        return False
    ho_rate = np.mean([nb(t) for t in H if len(t) >= MINLEN])
    nr = []
    for r in range(10):
        N = null_corpus(H, rng, model=m1)
        N = [t for t in N if t not in Dset]
        nr.append(np.mean([nb(t) for t in N if len(t) >= MINLEN]))
    res["heldout_dev_neighbour_rate"] = dict(heldout=float(ho_rate), bigram_null_novel=(float(np.mean(nr)), float(np.std(nr))))
    print("Held-out texts with ED-1 neighbour in dev: %.3f; bigram-null novel texts: %.3f+-%.3f" % (ho_rate, np.mean(nr), np.std(nr)))
    # external sites
    E, _ = icit_external()
    E = [t for t in E if t not in Dset and len(t) >= MINLEN]
    res["external_dev_neighbour_rate"] = dict(n=len(E), rate=float(np.mean([nb(t) for t in E])))
    print("External (non-M77 sites, bridged) texts with dev neighbour:", res["external_dev_neighbour_rate"])
    save_json("exp1_minimal_pairs", res)


if __name__ == "__main__":
    main()
