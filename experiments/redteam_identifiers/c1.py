"""Red team C1: are cross-site seal-text repeats just chance collisions of short texts?
C1a duplicate audit, C1b generative collision nulls (N1 positional unigram, N2 global bigram, N3 per-site
bigram), C1c length-matched leave-one-out locality ratio, Indus vs Ur III.

usage: .venv/bin/python experiments/redteam_identifiers/c1.py [nsim]
"""
import sys, os, json, re
from collections import Counter, defaultdict
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "experiments/identifiers"))
from id_lib import *  # noqa  (read-only import)

HERE = os.path.dirname(os.path.abspath(__file__))
NSIM = int(sys.argv[1]) if len(sys.argv) > 1 else 500
rng = np.random.default_rng(11)
BANDS = [(1, 1), (2, 2), (3, 3), (4, 5), (6, 99)]


def band(k):
    for a, b in BANDS:
        if a <= k <= b: return f"{a}-{b}" if a != b else str(a)


# ------------------------------------------------------------------ data
ALL = [o for o in icit_objects() if o["complete"]]
I = [o for o in ALL if o["cls"] == "seal"]
RAW = {}
for t in icit_texts(): RAW.setdefault(t["id"].split(".")[0], t)
texts = [flat(o["sp"]) for o in I]
sites = [o["site"] for o in I]


def repeat_stats(T, S):
    c = Counter(T); ss = defaultdict(set)
    for t, s in zip(T, S): ss[t].add(s)
    rep = [t for t, n in c.items() if n > 1]
    out = {"n_rep_texts": len(rep), "obj_on_rep": sum(c[t] for t in rep),
           "obj_on_rep_1to3": sum(c[t] for t in rep if len(t) <= 3),
           "multisite_share": float(np.mean([len(ss[t]) > 1 for t in rep])) if rep else float("nan"),
           "n_multisite": sum(len(ss[t]) > 1 for t in rep)}
    for a, b in BANDS:
        out[f"rep_obj_len_{band(a)}"] = sum(c[t] for t in rep if a <= len(t) <= b)
    return out


# ------------------------------------------------------------------ C1a duplicate audit
def c1a():
    c = Counter(texts)
    grp = defaultdict(list)
    for o, t in zip(I, texts):
        if c[t] > 1: grp[t].append(o)
    flagged = set(); reasons = Counter(); examples = []
    for t, os_ in grp.items():
        for i in range(len(os_)):
            for j in range(i + 1, len(os_)):
                a, b = os_[i], os_[j]; ra, rb = RAW[a["obj"]], RAW[b["obj"]]
                why = None
                if a["cisi"] not in ("-", "") and a["cisi"] == b["cisi"]: why = "same CISI"
                elif a["site"] == b["site"] and ra["symbol"] == rb["symbol"] and ra["width_mm"] == rb["width_mm"] \
                        and ra["height_mm"] == rb["height_mm"] and float(ra["width_mm"] or 0) > 0 and float(ra["height_mm"] or 0) > 0:
                    why = "same site+emblem+size"
                elif a["site"] == b["site"] and ("-" in (a["cisi"], b["cisi"])):
                    why = "same site, one lacks CISI no."
                if why:
                    reasons[why] += 1; flagged.add(b["obj"])
                    examples.append((" ".join(t), a["obj"], a["cisi"], b["obj"], b["cisi"], a["site"], why))
    # all-seal CISI duplicates (not just repeats)
    cc = Counter(o["cisi"] for o in I if o["cisi"] not in ("-", ""))
    keep = [k for k, o in enumerate(I) if o["obj"] not in flagged]
    base = repeat_stats(texts, sites)
    clean_ = repeat_stats([texts[k] for k in keep], [sites[k] for k in keep])
    res = dict(n_repeated_objects=base["obj_on_rep"], n_flagged=len(flagged), share_flagged=len(flagged) / base["obj_on_rep"],
               reasons=dict(reasons), examples=examples, cisi_dupes_all_seals=sum(v - 1 for v in cc.values() if v > 1),
               before=base, after=clean_, verdict="inflated" if len(flagged) / base["obj_on_rep"] >= 0.25 else "not inflated")
    print("C1a", {k: v for k, v in res.items() if k not in ("examples", "before", "after")})
    print("   before", base); print("   after ", clean_)
    for e in examples: print("   ", e)
    return res


# ------------------------------------------------------------------ models
def distinct_corpus(objs):
    return sorted({flat(o["sp"]) for o in objs})


class Bigram:
    def __init__(self, D, V, alpha=0.01):
        self.V = V; self.ix = {s: i for i, s in enumerate(V)}; n = len(V)
        st = np.full(n, alpha); tr = np.full((n, n + 1), alpha)  # last column = END
        for t in D:
            ids = [self.ix[s] for s in t]
            st[ids[0]] += 1
            for a, b in zip(ids, ids[1:]): tr[a, b] += 1
            tr[ids[-1], n] += 1
        self.st = st / st.sum(); self.tr = tr / tr.sum(1, keepdims=True)

    def mix(self, other, w=0.5):
        m = Bigram.__new__(Bigram); m.V = self.V; m.ix = self.ix
        m.st = w * self.st + (1 - w) * other.st; m.tr = w * self.tr + (1 - w) * other.tr
        return m

    def prepare(self, Lmax):
        n = len(self.V); T = self.tr[:, :n]; end = self.tr[:, n]
        beta = [end]  # beta[r](s) = P(exactly r more signs after s, then END)
        for r in range(1, Lmax):
            b = T @ beta[-1]; beta.append(b)
        self.beta = beta
        self.cdf_tr = []
        for r in range(Lmax):  # next sign when after it r more signs remain
            M = T * beta[r][None, :]; M = M / M.sum(1, keepdims=True)
            self.cdf_tr.append(np.cumsum(M, 1))
        self.cdf_st = []
        for L in range(1, Lmax + 1):
            p = self.st * beta[L - 1]; self.cdf_st.append(np.cumsum(p / p.sum()))

    def sample(self, lengths, r_):
        lengths = np.asarray(lengths); out = [None] * len(lengths)
        for L in np.unique(lengths):
            idx = np.where(lengths == L)[0]; k = len(idx)
            cur = np.searchsorted(self.cdf_st[L - 1], r_.random(k) * self.cdf_st[L - 1][-1])
            cur = np.minimum(cur, len(self.V) - 1)
            seqs = [cur]
            for pos in range(1, L):
                C = self.cdf_tr[L - 1 - pos][cur]
                u = r_.random(k)[:, None] * C[:, -1:]
                cur = np.minimum((C < u).sum(1), len(self.V) - 1); seqs.append(cur)
            arr = np.stack(seqs, 1)
            for j, i in enumerate(idx): out[i] = tuple(self.V[x] for x in arr[j])
        return out


class Positional:
    def __init__(self, D, V):
        self.V = V; ix = {s: i for i, s in enumerate(V)}; n = len(V)
        f, m, l, a = (np.full(n, 0.01) for _ in range(4))
        for t in D:
            for s in t: a[ix[s]] += 1
            if len(t) == 1: continue
            f[ix[t[0]]] += 1; l[ix[t[-1]]] += 1
            for s in t[1:-1]: m[ix[s]] += 1
        self.p = {k: v / v.sum() for k, v in dict(f=f, m=m, l=l, a=a).items()}

    def sample(self, lengths, r_):
        out = []
        n = len(self.V)
        for L in lengths:
            if L == 1: out.append((self.V[r_.choice(n, p=self.p["a"])],)); continue
            mid = r_.choice(n, L - 2, p=self.p["m"]) if L > 2 else []
            out.append(tuple([self.V[r_.choice(n, p=self.p["f"])]] + [self.V[x] for x in mid] + [self.V[r_.choice(n, p=self.p["l"])]]))
        return out


def c1b():
    D = distinct_corpus(ALL)
    V = sorted({s for t in D for s in t})
    Lmax = max(len(t) for t in texts)
    lengths = [len(t) for t in texts]
    g = Bigram(D, V); g.prepare(Lmax)
    pos = Positional(D, V)
    # per-site bigram (sites with >= 20 seals), interpolated 50/50 with global
    site_models = {}
    sc = Counter(sites)
    for s, n in sc.items():
        if n >= 20:
            Ds = distinct_corpus([o for o in ALL if o["site"] == s])
            m = Bigram(Ds, V).mix(g, 0.5); m.prepare(Lmax); site_models[s] = m
    # N2x (exploratory robustness): bigram fit WITHOUT any seal text of length 1-3 (no self-training on short seals)
    Dx = sorted({flat(o["sp"]) for o in ALL if not (o["cls"] == "seal" and len(flat(o["sp"])) <= 3)})
    gx = Bigram(Dx, V); gx.prepare(Lmax)
    obs = repeat_stats(texts, sites)
    sims = {"N1": [], "N2": [], "N3": [], "N2x": []}
    for it in range(NSIM):
        sims["N2"].append(repeat_stats(g.sample(lengths, rng), sites))
        sims["N2x"].append(repeat_stats(gx.sample(lengths, rng), sites))
        # N3
        T3 = [None] * len(texts)
        by = defaultdict(list)
        for i, s in enumerate(sites): by[s if s in site_models else "_g"].append(i)
        for s, idx in by.items():
            m = site_models.get(s, g)
            for i, t in zip(idx, m.sample([lengths[i] for i in idx], rng)): T3[i] = t
        sims["N3"].append(repeat_stats(T3, sites))
        if it < min(NSIM, 200):  # positional sampler is slow (per-object python)
            sims["N1"].append(repeat_stats(pos.sample(lengths, rng), sites))
    res = {"observed": obs, "nsim": {k: len(v) for k, v in sims.items()}}
    keys = list(obs)
    for k, L in sims.items():
        arr = {kk: np.array([d[kk] for d in L], float) for kk in keys}
        res[k] = {kk: dict(mean=float(np.nanmean(a)), lo=float(np.nanpercentile(a, 2.5)), hi=float(np.nanpercentile(a, 97.5)),
                           p_ge=float((1 + np.sum(a >= obs[kk])) / (len(a) + 1)), p_le=float((1 + np.sum(a <= obs[kk])) / (len(a) + 1)))
                  for kk, a in arr.items()}
    o13 = obs["obj_on_rep_1to3"]
    hi2, hi1 = res["N2"]["obj_on_rep_1to3"]["hi"], res["N1"]["obj_on_rep_1to3"]["hi"]
    res["verdict"] = "artefact (within/below N2)" if o13 <= hi2 else ("real excess" if o13 > hi1 else "excess over N2 only")
    print("C1b observed", obs)
    for k in ("N1", "N2", "N3", "N2x"):
        print(" ", k, {kk: "%.2f [%.2f,%.2f] p>=%.3f" % (v["mean"], v["lo"], v["hi"], v["p_ge"]) for kk, v in res[k].items()})
    print("  verdict", res["verdict"])
    return res


# ------------------------------------------------------------------ C1c length-matched LOO locality
def loo_R(S, L, pairs, strat=True, B=500, seed=5):
    """S[site] = list of keys, L[site] = list of lengths. R = sum hits / sum expected, expected for a target
    object of length band b = reference site's leave-one-out match rate in band b (or overall)."""
    r_ = np.random.default_rng(seed)
    loo = {}
    for r in {r for _, r in pairs}:
        c = Counter(S[r]); m = defaultdict(list)
        for k, l in zip(S[r], L[r]):
            hit = c[k] > 1; m[band(l) if strat else "all"].append(hit); m["all"].append(hit)
        loo[r] = {b: np.mean(v) for b, v in m.items()}
    H, E = [], []
    for t, r in pairs:
        ref = set(S[r]); h = np.array([k in ref for k in S[t]], float)
        e = np.array([loo[r].get(band(l) if strat else "all", np.nan) for l in L[t]], float)
        ok = ~np.isnan(e); H.append(h[ok]); E.append(e[ok])
    obs = sum(h.sum() for h in H) / sum(e.sum() for e in E)
    vals = []
    for _ in range(B):
        hs = es = 0.0
        for h, e in zip(H, E):
            if len(h) == 0: continue
            j = r_.integers(0, len(h), len(h)); hs += h[j].sum(); es += e[j].sum()
        vals.append(hs / es if es else np.nan)
    return float(obs), [float(x) for x in np.nanpercentile(vals, [2.5, 97.5])], float(sum(h.sum() for h in H)), float(sum(e.sum() for e in E))


def cun_signs(word):
    dets = re.findall(r"\{[^}]*\}", word)
    rest = re.sub(r"\{[^}]*\}", "-", word)
    return dets + [p for p in re.split(r"[-.+]", rest) if p]


def ur3_seals():
    U = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/identifiers/data/ur3_occ.jsonl"))]
    provs = [p for p, c in Counter(u["prov"] for u in U).most_common() if c >= 100 and p != "uncertain"]
    seals = {p: {} for p in provs}
    for u in U:
        if u["prov"] in seals and u["seal_id"]:
            seals[u["prov"]][u["seal_id"].split()[0].split(".")[0]] = u["legend"]
    return seals


def c1c():
    res = {}
    by = defaultdict(list)
    for o, t in zip(I, texts): by[o["site"]].append(t)
    isites = [s for s, v in by.items() if len(v) >= 40]
    pairs = [(a, b) for a in isites for b in isites if a != b]
    S = {s: by[s] for s in isites}; L = {s: [len(t) for t in by[s]] for s in isites}
    res["indus_sites"] = {s: len(by[s]) for s in isites}
    res["indus_unstrat"] = loo_R(S, L, pairs, strat=False)
    res["indus_strat"] = loo_R(S, L, pairs, strat=True)
    seals = ur3_seals()
    up = [p for p in seals if len(seals[p]) >= 100]
    upairs = [(a, b) for a in up for b in up if a != b]
    flatleg = lambda lg: [w for l in lg for w in l]
    for unit in ("signs", "words"):
        Su = {p: [json.dumps(v) for v in seals[p].values()] for p in up}
        if unit == "signs": Lu = {p: [sum(len(cun_signs(w)) for w in flatleg(v)) for v in seals[p].values()] for p in up}
        else: Lu = {p: [len(flatleg(v)) for v in seals[p].values()] for p in up}
        res[f"ur3_unstrat"] = loo_R(Su, Lu, upairs, strat=False)
        res[f"ur3_strat_{unit}"] = loo_R(Su, Lu, upairs, strat=True)
        # length distribution
        allL = [l for p in up for l in Lu[p]]
        res[f"ur3_len_{unit}"] = {"median": float(np.median(allL)), "share_le7": float(np.mean(np.array(allL) <= 7)),
                                  "n_le7": int(np.sum(np.array(allL) <= 7)), "n": len(allL)}
        if unit == "signs":
            # restricted to legends no longer than 7 signs (longest Indus repeat)
            Sr = {p: [k for k, l in zip(Su[p], Lu[p]) if l <= 7] for p in up}
            Lr = {p: [l for l in Lu[p] if l <= 7] for p in up}
            ok = [p for p in up if len(Sr[p]) >= 20]
            res["ur3_le7_sites"] = {p: len(Sr[p]) for p in ok}
            if len(ok) >= 2:
                res["ur3_le7"] = loo_R(Sr, Lr, [(a, b) for a in ok for b in ok if a != b], strat=True)
    # name lines (one line, short) as a length-matched Ur III unit: stratified by signs
    KINGS = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}szul-gi", "{d}i-bi2-{d}suen", "ur-{d}namma", "{d}szul-gi-ra"}
    royal = lambda lg: any(w in KINGS or w == "lugal" for l in lg for w in l)
    Sn = {p: [json.dumps(v[0]) for v in seals[p].values() if not royal(v)] for p in up}
    Ln = {p: [sum(len(cun_signs(w)) for w in v[0]) for v in seals[p].values() if not royal(v)] for p in up}
    res["ur3_nameline_unstrat"] = loo_R(Sn, Ln, upairs, strat=False)
    res["ur3_nameline_strat"] = loo_R(Sn, Ln, upairs, strat=True)
    res["ur3_nameline_len_median"] = float(np.median([l for p in up for l in Ln[p]]))
    # Indus restricted to 1-3 sign texts
    S3 = {s: [t for t in by[s] if len(t) <= 3] for s in isites}; L3 = {s: [len(t) for t in S3[s]] for s in isites}
    res["indus_le3"] = loo_R(S3, L3, pairs, strat=True)
    S7 = {s: [t for t in by[s] if len(t) <= 7] for s in isites}; L7 = {s: [len(t) for t in S7[s]] for s in isites}
    res["indus_le7"] = loo_R(S7, L7, pairs, strat=True)
    tg = ["Harappa", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira"]
    idpairs = [(t, "Mohenjo-daro") for t in tg] + [(t, "Harappa") for t in ["Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira"]]
    res["indus_unstrat_identifiers_pairs"] = loo_R(S, L, idpairs, strat=False)
    res["indus_strat_identifiers_pairs"] = loo_R(S, L, idpairs, strat=True)
    S4 = {s: [t for t in by[s] if len(t) >= 4] for s in isites}; L4 = {s: [len(t) for t in S4[s]] for s in isites}
    res["indus_ge4"] = loo_R(S4, L4, pairs, strat=True)
    for k, v in res.items(): print("C1c", k, v)
    return res


if __name__ == "__main__":
    out = {"C1a": c1a(), "C1c": c1c(), "C1b": c1b()}
    json.dump(out, open(os.path.join(HERE, "c1.json"), "w"), indent=1, default=float)
