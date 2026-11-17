"""Apply the frozen Kober/Ventris method (params chosen on controls only) to the Indus script.

Development on the DEV split of distinct M77 texts; held-out, Harappa vs Mohenjo-daro and ICIT used
only for replication of what was found on dev.

Run: .venv/bin/python experiments/phonetic_grid/indus.py
"""
import sys, json, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.metrics import adjusted_rand_score
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
import grid_lib as G
import corpora as C
from corpus.load import dev_heldout, icit_texts, distinct

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
CTRL = json.load(open(OUT / "controls.json"))
best = CTRL["best"]
G.set_params(min_stem=best["min_stem"], max_tail=best["max_tail"], weight=best.get("weight", "count"))
NNULL = 200
TESTS = []  # (name, p) for multiple-comparison bookkeeping


def clean(recs, complete_only=True):
    out = []
    for r in recs:
        if "#" in r["seq"]:
            continue
        if complete_only and not r.get("complete", True):
            continue
        t = tuple(s for s in r["seq"] if s != "|")
        if t:
            out.append(t)
    return list(dict.fromkeys(out))


def zp(obs, null_list):
    a = np.array(null_list, float)
    z = (obs - a.mean()) / (a.std() + 1e-9)
    p = (1 + (a >= obs).sum()) / (1 + len(a))
    return float(z), float(p)


def null_dist(texts, kind, n, direction, seed=11):
    rng = random.Random(seed); res = []
    for _ in range(n):
        if kind == "block":
            nt = G.shuffle_end_block(texts, rng) if direction == "end" else [tuple(reversed(x)) for x in G.shuffle_end_block([tuple(reversed(t)) for t in texts], rng)]
        elif kind == "final":
            nt = G.shuffle_final(texts, rng) if direction == "end" else [tuple(reversed(x)) for x in G.shuffle_final([tuple(reversed(t)) for t in texts], rng)]
        else:
            nt = G.bigram_null(texts, rng)
        res.append(G.stats(list(dict.fromkeys(nt)), direction))
    return res


# ------------------------------------------------------------------ 1. alternation vs nulls
def alternation_tests(texts, label):
    out = {}
    for direction in ["end", "start"]:
        obs = G.stats(texts, direction)
        row = {"obs": obs}
        for kind in ["block", "final", "bigram"]:
            nd = null_dist(texts, kind, NNULL if kind != "bigram" else 100, direction)
            row[kind] = {}
            for k in ["alt_stems", "triplets", "modularity", "top10_share"]:
                vals = [r[k] for r in nd]
                z, p = zp(obs[k], vals)
                row[kind][k] = dict(null_mean=round(float(np.mean(vals)), 3), null_sd=round(float(np.std(vals)), 3),
                                    ratio=round(obs[k] / max(np.mean(vals), 1e-9), 3), z=round(z, 2), p_upper=round(p, 4))
                if k in ("alt_stems", "modularity"):
                    from scipy.stats import norm
                    TESTS.append((f"{label}:{direction}:{kind}:{k}", float(norm.sf(z))))
        out[direction] = row
    return out


# ------------------------------------------------------------------ 2. grid + stability
def partition(texts, seed=0):
    e, slots, fams = G.kober(texts, "end", **G.PARAMS)
    return G.louvain_rows(e, 1, seed), e, fams


def ari_common(p1, p2):
    k = [s for s in p1 if s in p2]
    if len(k) < 5:
        return float("nan"), len(k)
    return float(adjusted_rand_score([p1[s] for s in k], [p2[s] for s in k])), len(k)


def bootstrap_stability(texts, n=100, seed=0):
    rng = random.Random(seed)
    full, _, _ = partition(texts)
    vals = []
    for i in range(n):
        bs = list(dict.fromkeys(rng.choice(texts) for _ in texts))
        p, _, _ = partition(bs, seed=i)
        vals.append(ari_common(full, p)[0])
    vals = [v for v in vals if v == v]
    return float(np.mean(vals)), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def split_agreement(A, B):
    pa, ea, _ = partition(A); pb, eb, _ = partition(B)
    a, n = ari_common(pa, pb)
    # edge replication: edges with weight>=2 in A that also occur in B
    strong = [e for e, c in ea.items() if c >= 2]
    rep = np.mean([e in eb for e in strong]) if strong else float("nan")
    rng = random.Random(5); reps = []; aris = []
    for i in range(100):
        nb = list(dict.fromkeys(G.shuffle_end_block(B, rng)))
        enb, _, _ = G.kober(nb, "end", **G.PARAMS)
        reps.append(np.mean([e in enb for e in strong]) if strong else float("nan"))
        if i < 30:
            aris.append(ari_common(pa, G.louvain_rows(enb, 1, i))[0])
    z, p = zp(rep, reps)
    aris = [x for x in aris if x == x]
    za, pa_ = zp(a, aris) if aris else (float("nan"), float("nan"))
    return dict(ari=round(a, 3), ari_null=round(float(np.mean(aris)), 3) if aris else None, ari_z=round(za, 2), ari_p=round(pa_, 4),
                shared_nodes=n, strong_edges_A=len(strong), edge_replication=round(float(rep), 3),
                edge_replication_null=round(float(np.mean(reps)), 3), z=round(z, 2), p_upper=round(p, 4))


def control_reference(n_texts):
    """Same stability / split statistics on controls subsampled to the Indus dev size."""
    ref = {}
    for name in ["lb_words", "lb_lines", "synth", "synth_nologo", "dravidian", "synth_prefix", "synth_nomorph"]:
        if name == "lb_words":
            t = C.linear_b_words(n_texts, seed=3)[0]
        elif name == "lb_lines":
            t = C.linear_b_lines(None, seed=3)[0]
        elif name == "synth":
            t = C.synthetic(n_texts, seed=3, logo_share=0.3)[0]
        elif name == "synth_nologo":
            t = C.synthetic(n_texts, seed=3)[0]
        elif name == "dravidian":
            t = C.dravidian(n_texts, seed=3)[0]
        elif name == "synth_prefix":
            t = C.synthetic(n_texts, seed=3, prefixing=True, logo_share=0.3)[0]
        else:
            t = C.synthetic(n_texts, seed=3, morph=False)[0]
        rng = random.Random(1); tt = list(t); rng.shuffle(tt)
        A, B = tt[: len(tt) // 2], tt[len(tt) // 2:]
        st = bootstrap_stability(t, n=50)
        sp = split_agreement(A, B)
        alt = alternation_tests_quick(t)
        ref[name] = dict(bootstrap_ari=st, halves=sp, alternation=alt)
        print("  control ref", name, ref[name], flush=True)
    return ref


def alternation_tests_quick(t):
    out = {}
    for d in ["end", "start"]:
        obs = G.stats(t, d)
        out[d] = {}
        for kind in ["block", "bigram"]:
            nd = null_dist(t, kind, 50, d)
            out[d][kind] = {k: dict(obs=obs[k], null=round(float(np.mean([r[k] for r in nd])), 3),
                                    z=round(zp(obs[k], [r[k] for r in nd])[0], 2)) for k in ["alt_stems", "triplets", "modularity"]}
    return out


# ------------------------------------------------------------------ 3. sign-level features
def sign_features(texts, signs=None, min_n=15):
    D = set(texts)
    freq = Counter(s for t in texts for s in t)
    pos = defaultdict(Counter); left = defaultdict(Counter); right = defaultdict(Counter)
    for t in texts:
        for i, s in enumerate(t):
            pos[s]["init" if i == 0 else "final" if i == len(t) - 1 else "mid"] += 1
            left[s][t[i - 1] if i > 0 else "<S>"] += 1
            right[s][t[i + 1] if i < len(t) - 1 else "<E>"] += 1
    e_end, _, _ = G.kober(texts, "end", **G.PARAMS)
    deg = Counter()
    for (a, b), c in e_end.items():
        deg[a] += 1; deg[b] += 1
    signs = signs or [s for s, c in freq.items() if c >= min_n]
    # substitution frames: same left & right context, one sign different
    ctx = defaultdict(set)
    for t in texts:
        for i, x in enumerate(t):
            ctx[(t[:i], t[i + 1:])].add(x)
    ctx = {k: v for k, v in ctx.items() if len(v) > 1 and len(k[0]) + len(k[1]) >= 2}  # frame needs >= 2 context signs
    feats = {}
    for s in signs:
        n = sum(pos[s].values())
        if n == 0:
            continue
        dele = 0; occ = 0; subs = set(); frames = 0; mob = 0
        for t in texts:
            for i, x in enumerate(t):
                if x != s:
                    continue
                occ += 1
                if len(t) > 1 and (t[:i] + t[i + 1:]) in D:
                    dele += 1
        for (l, r), xs in ctx.items():
            if s in xs and len(xs) > 1:
                frames += 1; subs |= xs - {s}
        for x in set(left[s]) | set(right[s]):
            if x in right[s] and x in left[s]:
                mob += 1
        H = lambda c: float(-sum(v / sum(c.values()) * np.log2(v / sum(c.values())) for v in c.values()))
        feats[s] = dict(n=n, init=pos[s]["init"] / n, mid=pos[s]["mid"] / n, final=pos[s]["final"] / n,
                        left_types=len(left[s]), right_types=len(right[s]), H_left=H(left[s]), H_right=H(right[s]),
                        top_left=left[s].most_common(3), top_right=right[s].most_common(3),
                        deletable=dele / max(occ, 1), subst_partners=len(subs), subst_frames=frames,
                        both_orders=mob, end_alt_degree=deg[s])
    return feats


def matched_null_features(feats, keys=("deletable", "subst_partners", "H_left", "H_right")):
    """For each sign, compare with signs of similar frequency (within factor 1.6) and same dominant slot."""
    out = {}
    allf = list(feats.items())
    for s, f in feats.items():
        dom = max(("init", "mid", "final"), key=lambda k: f[k])
        peers = [g for x, g in allf if x != s and f["n"] / 1.6 <= g["n"] <= f["n"] * 1.6 and max(("init", "mid", "final"), key=lambda k: g[k]) == dom]
        if len(peers) < 3:
            peers = sorted((g for x, g in allf if x != s), key=lambda g: abs(np.log(g["n"] / f["n"])))[:8]
        out[s] = {k: round(float(np.mean([g[k] for g in peers])), 3) for k in keys}
        for k in keys:
            sd = float(np.std([g[k] for g in peers])) + 1e-9
            out[s][k + "_z"] = round((f[k] - out[s][k]) / sd, 2)
        out[s]["n_peers"] = len(peers)
    return out


def calibrate_roles():
    """Feature profile of known suffix signs vs separate-word signs in an agglutinative control."""
    texts, role = C.synthetic_agglut(1700)
    f = sign_features(texts, min_n=15)
    prof = defaultdict(list)
    for s, v in f.items():
        prof[role[s]].append(v)
    keys = ["final", "mid", "deletable", "subst_partners", "H_left", "H_right", "left_types", "both_orders", "end_alt_degree"]
    return {r: {k: round(float(np.mean([v[k] for v in vs])), 3) for k in keys} | {"n_signs": len(vs)} for r, vs in prof.items()}


def deletable_cross(targets, lookup, signs):
    """Share of occurrences in `targets` whose deletion gives a text attested in `lookup`."""
    L = set(lookup); out = {}
    for s in signs:
        occ = dele = 0
        for t in targets:
            for i, x in enumerate(t):
                if x == s:
                    occ += 1
                    dele += (len(t) > 1 and (t[:i] + t[i + 1:]) in L)
        out[s] = (dele, occ, round(dele / max(occ, 1), 3))
    return out


# ------------------------------------------------------------------ main
def main():
    res = {"params": G.PARAMS}
    dev_r, ho_r = dev_heldout()
    dev = clean(dev_r); ho = clean(ho_r)
    dev_all = clean(dev_r, complete_only=False)
    print("dev complete", len(dev), "heldout", len(ho), "dev incl. incomplete", len(dev_all), flush=True)
    res["n"] = dict(dev=len(dev), heldout=len(ho), dev_incl_incomplete=len(dev_all),
                    mean_len_dev=round(float(np.mean([len(t) for t in dev])), 2))

    # 1 alternation
    res["alternation_dev"] = alternation_tests(dev, "dev")
    print(json.dumps(res["alternation_dev"], indent=0)[:3000], flush=True)
    res["alternation_dev_incl_incomplete"] = alternation_tests(dev_all, "dev_all")
    res["alternation_heldout"] = alternation_tests(ho, "heldout")

    # 2 grid
    p, e, fams = partition(dev)
    comms = defaultdict(list)
    for s, c in p.items():
        comms[c].append(s)
    deg = Counter()
    for (a, b), c in e.items():
        deg[a] += c; deg[b] += c
    res["dev_graph"] = dict(nodes=len(p), edges=len(e), communities=sorted([sorted(v, key=lambda s: -deg[s]) for v in comms.values()], key=len, reverse=True),
                            top_edges=[(a, b, c) for (a, b), c in e.most_common(30)],
                            top_families=[(list(st), sorted({b for b, _ in en})) for st, en in sorted(fams.items(), key=lambda x: -len({b for b, _ in x[1]}))[:15]])
    res["bootstrap_stability_dev"] = bootstrap_stability(dev, n=100)
    rng = random.Random(9)
    nulls = []
    for i in range(10):
        nd = list(dict.fromkeys(G.shuffle_end_block(dev, rng)))
        nulls.append(bootstrap_stability(nd, n=30, seed=i)[0])
    res["bootstrap_stability_null"] = (float(np.mean(nulls)), float(np.std(nulls)))
    print("stability", res["bootstrap_stability_dev"], res["bootstrap_stability_null"], flush=True)

    site = {}
    for r in dev_r + ho_r:
        site.setdefault(tuple(s for s in r["seq"] if s != "|"), r["site"])
    allm = list(dict.fromkeys(dev + ho))
    H = [t for t in allm if site.get(t) == "Harappa"]
    M = [t for t in allm if site.get(t) == "Mohenjodaro"]
    res["split_harappa_vs_md"] = split_agreement(M, H) | {"n_md": len(M), "n_harappa": len(H)}
    res["split_dev_vs_heldout"] = split_agreement(dev, ho)
    halves = []
    for i in range(5):
        rr = random.Random(100 + i); tt = list(dev); rr.shuffle(tt)
        halves.append(split_agreement(tt[: len(tt) // 2], tt[len(tt) // 2:]))
    res["split_dev_random_halves"] = {k: round(float(np.nanmean([h[k] for h in halves])), 3) for k in ["ari", "ari_null", "edge_replication", "edge_replication_null", "z", "strong_edges_A", "shared_nodes"]}
    # ICIT, independent transcription, mapped to Mahadevan numbers through the bridge
    bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    wm = {"W%03d" % int(k): "M%d" % v["M"][0] for k, v in bridge.items() if v.get("M")}
    ic = []
    for r in icit_texts():
        if not r.get("complete") or "#" in r["seq"]:
            continue
        t = tuple(wm.get(s, s) for s in r["seq"] if s != "|")
        ic.append(t)
    ic = list(dict.fromkeys(ic))
    res["split_dev_vs_icit"] = split_agreement(dev, ic) | {"n_icit": len(ic)}
    res["alternation_icit"] = alternation_tests(ic, "icit")
    print("splits", res["split_harappa_vs_md"], res["split_dev_vs_heldout"], res["split_dev_vs_icit"], flush=True)

    res["control_reference"] = control_reference(len(dev))

    # 3 sign roles
    f = sign_features(dev, min_n=15)
    mn = matched_null_features(f)
    res["calibration_roles"] = calibrate_roles()
    focus = ["M99", "M267", "M176", "M59", "M342", "M391", "M211", "M12", "M1", "M123", "M343", "M347"]
    res["sign_features"] = {s: f[s] | {"matched_null": mn[s]} for s in focus if s in f}
    # replication of the connective profile on held-out and on ICIT (independent transcription)
    fh = sign_features(ho, signs=[s for s in focus], min_n=1)
    fi = sign_features(ic, signs=[s for s in focus], min_n=1)
    keys = ["n", "init", "mid", "final", "deletable", "subst_partners", "H_left", "H_right", "top_left", "top_right"]
    res["sign_features_heldout"] = {s: {k: fh[s][k] for k in keys} for s in focus if s in fh}
    res["sign_features_icit"] = {s: {k: fi[s][k] for k in keys} for s in focus if s in fi}
    # held-out occurrences, deletion looked up in ALL distinct M77 texts; peers = all signs with n>=15 on dev
    allm77 = list(dict.fromkeys(dev + ho))
    peers = [x for x, v in f.items() if v["n"] >= 15]
    dc = deletable_cross(ho, allm77, peers)
    base = [v[2] for x, v in dc.items() if v[1] >= 5]
    res["deletable_heldout_vs_all"] = {s: dc[s] for s in focus if s in dc}
    res["deletable_heldout_peer_mean"] = (round(float(np.mean(base)), 3), round(float(np.percentile(base, 95)), 3), len(base))
    # suffix-like ranking: final share x END alternation degree
    rank = sorted(f.items(), key=lambda kv: -(kv[1]["final"] * np.log1p(kv[1]["end_alt_degree"])))
    res["suffix_like_ranking"] = [(s, round(v["final"], 2), v["end_alt_degree"], round(v["deletable"], 3), v["subst_partners"], v["n"]) for s, v in rank[:20]]

    # multiplicity
    m = len(TESTS)
    res["tests"] = dict(n=m, bonferroni_alpha=0.05 / m, note="p = one-sided normal approximation from z vs null; permutation p floors at 1/201",
                        list=[(n, p, p * m < 0.05) for n, p in TESTS])
    json.dump(res, open(OUT / "indus.json", "w"), indent=1, default=str)
    print("done; tests run:", m)


if __name__ == "__main__":
    main()
