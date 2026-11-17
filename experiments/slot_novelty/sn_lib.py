"""slot_novelty shared code (Fable plan 5, tests T2 and T3).

T2  Where the novelty lives: Baayen productivity per positional slot (opener / medial / closer),
    seals only, stratified by text length 3, 4, 5, 6+. Positional slots, no grammar.
T3  Frame dependency: MI between opener class and closer class against nulls that keep the
    adjacent-sign chain (positional suffix swaps = exact positional-bigram-preserving shuffle;
    secondary: fitted bigram chain sampled at the real lengths).

Units: DISTINCT M77 seal texts (dev_heldout(version=2)), complete, no break, line breaks dropped.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, icit_texts  # noqa: E402

M77_OLD_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}


# ------------------------------------------------------------------ data
def clean(seq):
    return tuple(s for s in seq if s != "|")


def indus_seals(split, site=None, min_len=1):
    """distinct complete M77 seal texts of a split ('dev' | 'heldout'); site = M77 site name or None."""
    dev, ho = dev_heldout(version=2)
    S = dev if split == "dev" else ho
    out, seen = [], set()
    for t in S:
        if t["object_type"] != "seal" or not t["complete"] or "#" in t["seq"]:
            continue
        if site and t["site"] != site:
            continue
        s = clean(t["seq"])
        if len(s) < min_len or s in seen:
            continue
        seen.add(s); out.append(s)
    return out


def icit_newsite_seals(min_len=1):
    """distinct complete ICIT seal texts from sites absent from M77 (independent of M77 objects)."""
    out, seen = [], set()
    for t in icit_texts():
        if not t["type"].startswith("SEAL") or t["site"] in M77_OLD_SITES_ICIT:
            continue
        if not t["complete"] or "#" in t["seq"]:
            continue
        s = clean(t["seq"])
        if len(s) < min_len or s in seen:
            continue
        seen.add(s); out.append(s)
    return out


def ur3_legends():
    """Ur III seal legends with rule-tagged slots (genre_alignment tagger, imported read-only).
    Returns list of dicts {words, slots, signs, sign_slots}."""
    sys.path.insert(0, str(ROOT / "experiments/genre_alignment"))
    import ga_slots  # noqa
    T = ga_slots.cun_corpus("ur3")
    out, seen = [], set()
    for t in T:
        key = tuple(t["toks"])
        if key in seen or not key:
            continue
        seen.add(key)
        signs, sslots = [], []
        for w, sl in zip(t["toks"], t["slots"]):
            for g in split_signs(w):
                signs.append(g); sslots.append(sl)
        out.append(dict(words=list(key), slots=list(t["slots"]), signs=signs, sign_slots=sslots))
    return out


def split_signs(word):
    """cuneiform word -> sign readings (determinatives kept as separate signs)."""
    return [p for p in re.findall(r"\{[^}]*\}|[^-{}.\s]+", word) if p]


# ------------------------------------------------------------------ T2
SLOTS = ("opener", "medial", "closer")


def strata(texts, lengths=(3, 4, 5, 6)):
    """length strata; last value means 'and longer'."""
    out = {}
    top = lengths[-1]
    for L in lengths:
        out[f"{L}+" if L == top else str(L)] = [t for t in texts if (len(t) >= L if L == top else len(t) == L)]
    return out


def common_set(texts, cover=0.80):
    """signs that together cover `cover` of all tokens of the corpus (most frequent first)."""
    c = Counter(s for t in texts for s in t)
    tot = sum(c.values()); acc = 0; out = set()
    for s, n in c.most_common():
        if acc >= cover * tot:
            break
        out.add(s); acc += n
    return out


def slot_tokens(texts, rng):
    """one token per text per slot: first, a random interior sign, last."""
    op = [t[0] for t in texts]
    cl = [t[-1] for t in texts]
    me = [t[rng.integers(1, len(t) - 1)] for t in texts]
    return {"opener": op, "medial": me, "closer": cl}


def P_of(tokens):
    c = Counter(tokens)
    n1 = sum(1 for v in c.values() if v == 1)
    return n1 / len(tokens), n1, len(c)


def t2_stratum(texts, common, rng, n_medial_draws=50):
    """productivity per slot for one length stratum. P = n1/N with N = #texts (equal for all slots)."""
    N = len(texts)
    res = {}
    for s in ("opener", "closer"):
        toks = [t[0] if s == "opener" else t[-1] for t in texts]
        P, n1, V = P_of(toks)
        res[s] = dict(P=P, n1=n1, V=V)
    Ps, n1s, Vs = [], [], []
    for _ in range(n_medial_draws):
        P, n1, V = P_of([t[rng.integers(1, len(t) - 1)] for t in texts])
        Ps.append(P); n1s.append(n1); Vs.append(V)
    res["medial"] = dict(P=float(np.mean(Ps)), n1=float(np.mean(n1s)), V=float(np.mean(Vs)))
    tot = sum(res[s]["n1"] for s in SLOTS)
    for s in SLOTS:
        res[s]["share"] = res[s]["n1"] / tot if tot else float("nan")
    # novelty decomposition on slot CONTENT (opener sign / medial string / closer sign)
    content = {"opener": [(t[0],) for t in texts], "medial": [tuple(t[1:-1]) for t in texts],
               "closer": [(t[-1],) for t in texts]}
    for s in SLOTS:
        c = Counter(content[s])
        novel = [k for k, v in c.items() if v == 1]
        rare = sum(1 for k in novel if any(x not in common for x in k))
        res[s]["content_novel_rate"] = len(novel) / N
        res[s]["novel_rare_sign"] = rare / N
        res[s]["novel_common_combo"] = (len(novel) - rare) / N
        res[s]["frac_novel_from_rare"] = rare / len(novel) if novel else float("nan")
    Pv = {s: res[s]["P"] for s in SLOTS}
    order = sorted(SLOTS, key=lambda s: -Pv[s])
    res["top"] = order[0]
    res["ratio_top_second"] = Pv[order[0]] / Pv[order[1]] if Pv[order[1]] > 0 else float("inf")
    res["ratio_max_min"] = Pv[order[0]] / Pv[order[2]] if Pv[order[2]] > 0 else float("inf")
    res["N"] = N
    return res


def growth_curve(tokens, rng, n_perm=20, npts=20):
    """type growth V(n) averaged over random orders."""
    N = len(tokens); pts = np.unique(np.linspace(1, N, npts).astype(int))
    V = np.zeros(len(pts))
    arr = np.array(tokens, dtype=object)
    for _ in range(n_perm):
        perm = arr[rng.permutation(N)]
        seen = set(); vs = []; j = 0
        for i, x in enumerate(perm, 1):
            seen.add(x)
            if j < len(pts) and i == pts[j]:
                vs.append(len(seen)); j += 1
        V += np.array(vs)
    return pts.tolist(), (V / n_perm).tolist()


def t2_bootstrap(texts, common, rng, B=500):
    """bootstrap over texts: returns arrays of P per slot and the top/second ratio for the OBSERVED top slot."""
    obs = t2_stratum(texts, common, rng)
    top = obs["top"]
    others = [s for s in SLOTS if s != top]
    N = len(texts)
    rat, shares, Pb = [], [], {s: [] for s in SLOTS}
    for _ in range(B):
        # bootstrap duplicates would create artificial non-hapaxes: subsample WITHOUT replacement at 80%
        idx = rng.choice(N, int(0.8 * N), replace=False)
        r = t2_stratum([texts[i] for i in idx], common, rng, n_medial_draws=10)
        for s in SLOTS:
            Pb[s].append(r[s]["P"])
        sec = max(r[s]["P"] for s in others)
        rat.append(r[top]["P"] / sec if sec > 0 else np.inf)
        shares.append(r[top]["share"])
    q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    obs["ci_ratio_top_vs_next"] = q(rat)
    obs["ci_share_top"] = q(shares)
    for s in SLOTS:
        obs[s]["ci_P_sub80"] = q(Pb[s])
    return obs


def shuffle_within(texts, rng):
    """negative control: permute signs inside each text (destroys position, keeps composition)."""
    out = []
    for t in texts:
        t = list(t); rng.shuffle(t); out.append(tuple(t))
    return out


def t2_verdict(r, cfg):
    """per-stratum label: 'single' | 'even' | 'mixed'."""
    single = (r[r["top"]]["share"] >= cfg["share_single"] and r["ratio_top_second"] >= cfg["ratio_single"]
              and r["ci_ratio_top_vs_next"][0] > 1.0)
    even = r["ratio_max_min"] < cfg["ratio_even"]
    return "single" if single else ("even" if even else "mixed")


# ------------------------------------------------------------------ T3
def classes(tokens, K):
    top = [s for s, _ in Counter(tokens).most_common(K)]
    m = {s: i for i, s in enumerate(top)}
    return np.array([m.get(s, K) for s in tokens]), top


def mi_bits(a, b):
    a = np.asarray(a); b = np.asarray(b)
    n = len(a)
    ka, kb = a.max() + 1, b.max() + 1
    J = np.zeros((ka, kb))
    np.add.at(J, (a, b), 1)
    J /= n
    pa = J.sum(1, keepdims=True); pb = J.sum(0, keepdims=True)
    nz = J > 0
    return float((J[nz] * np.log2(J[nz] / (pa @ pb)[nz])).sum())


def oc_mi(texts, K, op_map=None, cl_map=None):
    """MI(opener class; closer class). Class maps are fixed from the observed data and reused for nulls."""
    op = [t[0] for t in texts]; cl = [t[-1] for t in texts]
    if op_map is None:
        _, top_o = classes(op, K); op_map = {s: i for i, s in enumerate(top_o)}
        _, top_c = classes(cl, K); cl_map = {s: i for i, s in enumerate(top_c)}
    a = [op_map.get(s, K) for s in op]; b = [cl_map.get(s, K) for s in cl]
    return mi_bits(a, b), op_map, cl_map


def swap_sweep(texts, rng):
    """one sweep of positional suffix swaps: for every (length L, position k in 2..L-1 (1-based),
    sign at k), permute the suffixes after k among the texts that share that sign there.
    Preserves exactly: length distribution, every positional unigram and positional bigram count
    per length (so the whole adjacent chain), and each text's prefix up to k."""
    T = [list(t) for t in texts]
    byL = defaultdict(list)
    for i, t in enumerate(T):
        byL[len(t)].append(i)
    for L, idx in byL.items():
        if L < 3:
            continue
        ks = list(range(1, L - 1))  # 0-based interior positions
        rng.shuffle(ks)
        for k in ks:
            grp = defaultdict(list)
            for i in idx:
                grp[T[i][k]].append(i)
            for g in grp.values():
                if len(g) < 2:
                    continue
                suf = [T[i][k + 1:] for i in g]
                perm = rng.permutation(len(g))
                for i, p in zip(g, perm):
                    T[i] = T[i][:k + 1] + suf[p]
    return [tuple(t) for t in T]


def swap_null(texts, K, rng, n=1000, burn=5, thin=2):
    obs, om, cm = oc_mi(texts, K)
    cur = list(texts)
    for _ in range(burn):
        cur = swap_sweep(cur, rng)
    vals = []
    for _ in range(n):
        for _ in range(thin):
            cur = swap_sweep(cur, rng)
        vals.append(oc_mi(cur, K, om, cm)[0])
    vals = np.array(vals)
    return dict(I_obs=obs, I_null_mean=float(vals.mean()), I_null_sd=float(vals.std()),
                excess=float(obs - vals.mean()), z=float((obs - vals.mean()) / (vals.std() + 1e-12)),
                p=float((1 + (vals >= obs).sum()) / (1 + n)), n_texts=len(texts))


class BigramChain:
    """MLE bigram chain with START/END fitted on texts; exact sampling conditional on length."""

    def __init__(self, texts):
        V = sorted({s for t in texts for s in t})
        self.V = V; self.ix = {s: i for i, s in enumerate(V)}
        n = len(V)
        self.start = np.zeros(n); self.T = np.zeros((n, n)); self.end = np.zeros(n)
        out = np.zeros(n)
        for t in texts:
            self.start[self.ix[t[0]]] += 1
            for a, b in zip(t, t[1:]):
                self.T[self.ix[a], self.ix[b]] += 1
            self.end[self.ix[t[-1]]] += 1
        self.start /= self.start.sum()
        tot = self.T.sum(1) + self.end
        tot[tot == 0] = 1
        self.T = self.T / tot[:, None]; self.end = self.end / tot

    def sample(self, L, rng):
        # beta[j] = P(end exactly after j more symbols | current state) ; beta[0] = end prob
        beta = [self.end]
        for _ in range(L - 1):
            beta.append(self.T @ beta[-1])
        p = self.start * beta[L - 1]
        p = p / p.sum()
        s = rng.choice(len(p), p=p); out = [s]
        for j in range(L - 2, -1, -1):
            p = self.T[s] * beta[j]
            p = p / p.sum()
            s = rng.choice(len(p), p=p); out.append(s)
        return tuple(self.V[i] for i in out)


def bigram_null(texts, K, rng, n=1000):
    obs, om, cm = oc_mi(texts, K)
    ch = BigramChain(texts)
    Ls = [len(t) for t in texts]
    vals = []
    for _ in range(n):
        sim = [ch.sample(L, rng) for L in Ls]
        vals.append(oc_mi(sim, K, om, cm)[0])
    vals = np.array(vals)
    return dict(I_obs=obs, I_null_mean=float(vals.mean()), I_null_sd=float(vals.std()),
                excess=float(obs - vals.mean()), z=float((obs - vals.mean()) / (vals.std() + 1e-12)),
                p=float((1 + (vals >= obs).sum()) / (1 + n)), n_texts=len(texts))


def plant_template(texts, f, rng, n_pairs=2):
    """planted frame dependency: texts opening with the i-th most common opener get, with prob f,
    the i-th most common closer as their last sign (i = 1..n_pairs)."""
    op = Counter(t[0] for t in texts).most_common(n_pairs)
    cl = Counter(t[-1] for t in texts).most_common(n_pairs + 1)
    cl = [c for c, _ in cl]
    out = []
    for t in texts:
        t = list(t)
        for i, (o, _) in enumerate(op):
            if t[0] == o and rng.random() < f:
                t[-1] = cl[i]
        out.append(tuple(t))
    return out


def dump(obj, path):
    def conv(o):
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, np.ndarray): return o.tolist()
        raise TypeError(type(o))
    json.dump(obj, open(path, "w"), indent=1, default=conv)


# ------------------------------------------------------------------ T2 pooled + windows
def t2_pooled(texts, common, rng, n_medial_draws=50):
    """sum n1 per slot over length strata 3,4,5,6+ (each stratum has equal N across slots).
    Returns per-slot pooled P (= sum n1 / sum N), shares, ratios, and the per-stratum results."""
    per = {k: t2_stratum(T, common, rng, n_medial_draws) for k, T in strata(texts).items() if len(T) >= 2}
    N = sum(r["N"] for r in per.values())
    n1 = {s: sum(r[s]["n1"] for r in per.values()) for s in SLOTS}
    tot = sum(n1.values())
    P = {s: n1[s] / N for s in SLOTS}
    order = sorted(SLOTS, key=lambda s: -P[s])
    return dict(N=N, P=P, share={s: n1[s] / tot for s in SLOTS}, top=order[0], second=order[1],
                low=order[2], ratio_top_second=P[order[0]] / P[order[1]],
                ratio_max_min=P[order[0]] / P[order[2]], per_stratum=per)


def t2_pooled_ci(texts, common, rng, B=500, frac=0.8):
    """CIs by subsampling texts without replacement (frac); ratios computed for the OBSERVED slot order."""
    obs = t2_pooled(texts, common, rng)
    top, sec, low = obs["top"], obs["second"], obs["low"]
    r_ts, r_mm, sh, Pb = [], [], [], {s: [] for s in SLOTS}
    r_low = []
    n = len(texts)
    for _ in range(B):
        idx = rng.choice(n, int(frac * n), replace=False)
        r = t2_pooled([texts[i] for i in idx], common, rng, n_medial_draws=5)
        for s in SLOTS:
            Pb[s].append(r["P"][s])
        r_ts.append(r["P"][top] / max(r["P"][sec], 1e-9))
        r_mm.append(r["P"][top] / max(r["P"][low], 1e-9))
        oth = min(r["P"][s] for s in SLOTS if s != "closer")
        r_low.append(oth / max(r["P"]["closer"], 1e-9))
        sh.append(r["share"][top])
    q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    obs["ci_ratio_top_second"] = q(r_ts); obs["ci_ratio_max_min"] = q(r_mm)
    obs["ci_share_top"] = q(sh); obs["ci_P_sub"] = {s: q(Pb[s]) for s in SLOTS}
    obs["ratio_minOM_over_closer"] = min(obs["P"]["opener"], obs["P"]["medial"]) / max(obs["P"]["closer"], 1e-9)
    obs["ci_ratio_minOM_over_closer"] = q(r_low)
    return obs


def pooled_label(r, cfg):
    single = (r["share"][r["top"]] >= cfg["share_single"] and r["ratio_top_second"] >= cfg["ratio_single"]
              and r["ci_ratio_top_second"][0] > 1.0)
    even = r["ratio_max_min"] < cfg["ratio_even"]
    return "single" if single else ("even" if even else "mixed")


def t2_windows(texts, common, rng, n_draws=50):
    """combination novelty at equal unit (2-sign windows), texts of length >= 4:
    start (s1 s2), interior (a random adjacent pair touching neither edge), end (s_{L-1} s_L).
    novelty = window occurs once in that slot within its length stratum; split into
    windows made only of common signs (new combination) vs containing a rare sign."""
    res = {"start": [0, 0, 0], "interior": [0, 0, 0], "end": [0, 0, 0]}  # novel, novel_common, N
    for k, T in strata(texts).items():
        T = [t for t in T if len(t) >= 4]
        if len(T) < 2:
            continue
        for slot, get in (("start", lambda t: t[:2]), ("end", lambda t: t[-2:])):
            c = Counter(get(t) for t in T)
            nov = [w for w, v in c.items() if v == 1]
            res[slot][0] += len(nov); res[slot][1] += sum(all(x in common for x in w) for w in nov)
            res[slot][2] += len(T)
        a = b = 0.0
        for _ in range(n_draws):
            ws = []
            for t in T:
                j = rng.integers(1, len(t) - 2)
                ws.append(t[j:j + 2])
            c = Counter(ws); nov = [w for w, v in c.items() if v == 1]
            a += len(nov); b += sum(all(x in common for x in w) for w in nov)
        res["interior"][0] += a / n_draws; res["interior"][1] += b / n_draws; res["interior"][2] += len(T)
    return {s: dict(novel_rate=v[0] / v[2], novel_common_combo_rate=v[1] / v[2],
                    frac_novel_common=v[1] / v[0] if v[0] else float("nan"), N=v[2]) for s, v in res.items()}
