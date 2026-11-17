"""Shared code for the modifier-paradigm test.

Unit: distinct texts with no '#' break; line breaks '|' removed; length >= 2.
Per (derived, base) pair we measure signed shifts (derived minus base) in
  final  = share of tokens that are text-final
  init   = share of tokens that are text-initial
  relpos = mean relative position i/(L-1)
  seal   = share of tokens on seals/sealings (object-type register)
and partner-class shifts (left/right neighbour role class from the frozen
functional_reading lexicon). Consistency across bases is tested against a
null that replaces each derived sign by a random sign of matched frequency.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R))
from corpus.load import dev_heldout, distinct, icit_texts  # noqa: E402

HERE = Path(__file__).resolve().parent
FEATS = ["final", "init", "relpos", "seal"]
MIN_TOK = 3          # tokens of each sign in a pair, per corpus
MIN_BASES = 3        # distinct bases per modifier
SEALISH_M = {"seal", "sealing"}


# ---------- data ----------
def _clean(seq):
    if "#" in seq:
        return None
    s = [x for x in seq if x != "|"]
    return s if len(s) >= 2 else None


def m77_corpus(split):
    dev, ho = dev_heldout(version=2)
    src = {"dev": dev, "heldout": ho, "all": dev + ho}[split]
    out = []
    for t in src:
        s = _clean(t["seq"])
        if s:
            out.append((tuple(s), t["object_type"] in SEALISH_M, t["site"]))
    return out


def icit_corpus(new_sites_only=False):
    m77_sites = {t["site"].lower() for t in dev_heldout(version=2)[0] + dev_heldout(version=2)[1]}
    out = []
    for t in distinct(icit_texts()):
        s = _clean(t["seq"])
        if not s or any(not x.startswith("W") for x in s):
            continue
        if new_sites_only and t["site"].lower() in m77_sites:
            continue
        out.append((tuple(s), t["type"].upper().startswith("SEAL"), t["site"]))
    return out


def load_pairs(path):
    rows = list(csv.DictReader(open(path)))
    return [(r["sign"], r["base"], r["modifier"], r["confidence"], r["base_family"]) for r in rows]


# ---------- role classes for partners ----------
def _lexicon_roles():
    roles = {}
    for r in csv.DictReader(open(R / "experiments/functional_reading/lexicon.csv")):
        if r["kind"] != "sign" or not r["roles"]:
            continue
        top = r["roles"].split()[0]
        top = {"NUMERAL(short)": "NUM", "NUMERAL(tall)": "NUM", "UNIT/MEASURE": "NUM",
               "FISH-CLASS": "FISH", "BRACKETED-FISH": "FISH", "POST-CLOSER": "CLOSER",
               "CONNECTIVE": "OPENER"}.get(top, top)
        roles[r["item"]] = top
    return roles


ROLE = _lexicon_roles()
CLASSES = ["<s>", "</s>", "OPENER", "NUM", "FISH", "TITLE", "CLOSER", "NOUN", "OOV"]


def _bridge():
    b = json.load(open(R / "sources/shaunmortal_indus/data/bridge_WM.json"))
    return {f"W{int(w):03d}": f"M{v['M'][0]}" for w, v in b.items()}


W2M = _bridge()


def role_of(sign):
    if sign in ("<s>", "</s>"):
        return sign
    if sign.startswith("W"):
        m = W2M.get(sign)
        if m is None:
            return "OOV"
        sign = m
    return ROLE.get(sign, "NOUN")


# ---------- per-sign profiles ----------
def profiles(corpus):
    """sign -> dict of token counts and partner class counters."""
    P = defaultdict(lambda: {"n": 0, "final": 0, "init": 0, "relpos": 0.0, "seal": 0,
                             "L": Counter(), "R": Counter()})
    for seq, sealish, _ in corpus:
        L = len(seq)
        for i, s in enumerate(seq):
            p = P[s]
            p["n"] += 1
            p["final"] += i == L - 1
            p["init"] += i == 0
            p["relpos"] += i / (L - 1)
            p["seal"] += bool(sealish)
            p["L"][role_of(seq[i - 1]) if i else "<s>"] += 1
            p["R"][role_of(seq[i + 1]) if i < L - 1 else "</s>"] += 1
    return P


def feat(p, f):
    return p[f] / p["n"]


def dist(c):
    v = np.array([c.get(k, 0) for k in CLASSES], float)
    return v / v.sum() if v.sum() else v


def jsd(p, q):
    m = (p + q) / 2
    def kl(a, b):
        k = a > 0
        return float(np.sum(a[k] * np.log2(a[k] / b[k])))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# ---------- modifier test ----------
def usable(pairs, P, min_tok=MIN_TOK):
    return [pr for pr in pairs if P[pr[0]]["n"] >= min_tok and P[pr[1]]["n"] >= min_tok]


def stat(pairs_by_base, P, derived_of=None):
    """pairs_by_base: {base: [derived,...]}. Returns per-feature mean-over-bases delta,
    partner-shift consistency (mean pairwise cosine of per-base diff vectors), mean JSD."""
    deltas = {f: [] for f in FEATS}
    diffs, js = [], []
    for b, ds in pairs_by_base.items():
        pb = P[b]
        dd = {f: [] for f in FEATS}
        vecs, jj = [], []
        for d in ds:
            d = derived_of.get((b, d), d) if derived_of else d
            pd = P[d]
            for f in FEATS:
                dd[f].append(feat(pd, f) - feat(pb, f))
            vd = np.concatenate([dist(pd["L"]), dist(pd["R"])])
            vb = np.concatenate([dist(pb["L"]), dist(pb["R"])])
            vecs.append(vd - vb)
            jj.append(0.5 * (jsd(dist(pd["L"]), dist(pb["L"])) + jsd(dist(pd["R"]), dist(pb["R"]))))
        for f in FEATS:
            deltas[f].append(np.mean(dd[f]))
        diffs.append(np.mean(vecs, 0))
        js.append(np.mean(jj))
    out = {f: float(np.mean(v)) for f, v in deltas.items()}
    out.update({f + "_pos": int(np.sum(np.array(v) > 0)) for f, v in deltas.items()})
    out.update({f + "_neg": int(np.sum(np.array(v) < 0)) for f, v in deltas.items()})
    cs = []
    for i in range(len(diffs)):
        for j in range(i + 1, len(diffs)):
            a, b = diffs[i], diffs[j]
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na and nb:
                cs.append(a @ b / (na * nb))
    out["partner_cos"] = float(np.mean(cs)) if cs else 0.0
    out["jsd"] = float(np.mean(js))
    out["per_base"] = {b: {f: float(x) for f, x in zip(FEATS, vals)}
                       for b, vals in zip(pairs_by_base, zip(*[deltas[f] for f in FEATS]))}
    return out


def by_base(pairs):
    g = defaultdict(list)
    for d, b, *_ in pairs:
        g[b].append(d)
    return dict(g)


def freq_pool(P, min_tok):
    return [s for s, p in P.items() if p["n"] >= min_tok]


def signflip_test(pairs_by_base, P, max_exact=16, n_rand=20000, seed=0):
    """H0: per-base shifts (derived - base) are symmetric around 0, i.e. the modifier has no
    consistent direction. Exact sign-flip permutation over bases (each base counts once).
    Features: two-sided on the mean shift. Partner classes: one-sided on the mean pairwise
    cosine of per-base partner-difference vectors (flipping = swapping derived/base)."""
    obs = stat(pairs_by_base, P)
    bases = list(obs["per_base"])
    k = len(bases)
    D = np.array([[obs["per_base"][b][f] for f in FEATS] for b in bases])
    V = []
    for b in bases:
        pb = P[b]
        vs = [np.concatenate([dist(P[d]["L"]), dist(P[d]["R"])]) - np.concatenate([dist(pb["L"]), dist(pb["R"])])
              for d in pairs_by_base[b]]
        V.append(np.mean(vs, 0))
    V = np.array(V)
    nrm = np.linalg.norm(V, axis=1); nrm[nrm == 0] = 1
    C = (V / nrm[:, None]) @ (V / nrm[:, None]).T
    iu = np.triu_indices(k, 1)
    if k <= max_exact:
        S = np.array([[1 if (m >> j) & 1 else -1 for j in range(k)] for m in range(2 ** k)])
    else:
        S = np.random.default_rng(seed).choice([-1, 1], size=(n_rand, k))
    means = S @ D / k                                   # (nperm, nfeat)
    ob = D.mean(0)
    res = {"obs": obs, "k": k, "p": {}, "min_attainable_p": float(2 / 2 ** k) if k <= max_exact else 1 / n_rand}
    for fi, f in enumerate(FEATS):
        res["p"][f] = float(np.mean(np.abs(means[:, fi]) >= abs(ob[fi]) - 1e-12))
    if k >= 2:
        pc = np.array([np.mean((np.outer(s, s) * C)[iu]) for s in S])
        oc = np.mean(C[iu])
        res["p"]["partner_cos"] = float(np.mean(pc >= oc - 1e-12))
        res["obs"]["partner_cos"] = float(oc)
    else:
        res["p"]["partner_cos"] = 1.0
    return res


def sign_test_p(pos, neg):
    from scipy.stats import binomtest
    n = pos + neg
    return float(binomtest(pos, n, 0.5).pvalue) if n else 1.0


def bh(ps):
    ps = np.asarray(ps, float); n = len(ps)
    o = np.argsort(ps); q = np.empty(n)
    prev = 1.0
    for r, i in enumerate(o[::-1]):
        k = n - r
        prev = min(prev, ps[i] * n / k); q[i] = prev
    return q


# ---------- token-level stratified test (strata = bases) ----------
def cmh(pairs_by_base, P, f="final"):
    """Mantel-Haenszel test of derived vs base for a binary token feature, stratified by base
    (all derived forms of one base pooled). Returns pooled OR, signed z (positive = derived higher)
    and two-sided p (continuity-uncorrected)."""
    from scipy.stats import norm
    num = den = 0.0; a_sum = e_sum = v_sum = 0.0
    for b, ds in pairs_by_base.items():
        a = sum(P[d][f] for d in ds); n1 = sum(P[d]["n"] for d in ds)
        c = P[b][f]; n0 = P[b]["n"]
        bb = n1 - a; dd = n0 - c; N = n1 + n0
        m1 = a + c; m0 = N - m1
        if N < 2 or m1 == 0 or m0 == 0:
            continue
        a_sum += a; e_sum += n1 * m1 / N
        v_sum += n1 * n0 * m1 * m0 / (N * N * (N - 1))
        num += a * dd / N; den += bb * c / N
    if v_sum == 0:
        return {"or": float("nan"), "z": 0.0, "p": 1.0}
    z = (a_sum - e_sum) / np.sqrt(v_sum)
    return {"or": float(num / den) if den else float("inf"), "z": float(z), "p": float(2 * norm.sf(abs(z)))}


def power_sim(pairs_by_base, P, shift, f="final", n_sim=2000, alpha=0.05, seed=0):
    """Power of the one-sided CMH (derived higher) when every derived form has base rate + shift,
    keeping the observed token counts."""
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sim):
        Q = {}
        for b, ds in pairs_by_base.items():
            pb = feat(P[b], f)
            Q[b] = {"n": P[b]["n"], f: rng.binomial(P[b]["n"], pb)}
            for d in ds:
                Q[d] = {"n": P[d]["n"], f: rng.binomial(P[d]["n"], min(1.0, pb + shift))}
        r = cmh(pairs_by_base, Q, f)
        hits += r["z"] > norm.isf(alpha)
    return hits / n_sim


def robust(pairs_by_base, P, f="final"):
    """CMH z with every base dropped in turn: returns full z, the leave-one-out z closest to 0
    (same sign required to count as robust), and per-base direction counts."""
    full = cmh(pairs_by_base, P, f)
    loo = []
    for b in pairs_by_base:
        g = {k: v for k, v in pairs_by_base.items() if k != b}
        if g:
            loo.append(cmh(g, P, f)["z"])
    worst = min(loo, key=lambda z: z * np.sign(full["z"])) if loo else 0.0
    up = sum(np.mean([feat(P[d], f) for d in ds]) > feat(P[b], f) for b, ds in pairs_by_base.items())
    dn = sum(np.mean([feat(P[d], f) for d in ds]) < feat(P[b], f) for b, ds in pairs_by_base.items())
    return {"z": full["z"], "p": full["p"], "or": full["or"], "loo_worst_z": float(worst), "up": int(up), "down": int(dn),
            "k": len(pairs_by_base)}


def robust_T(r):
    """Robust signed statistic: the leave-one-base-out CMH z closest to zero, signed by the full z;
    0 if dropping one base flips the sign."""
    s = np.sign(r["z"])
    return float(s * max(0.0, s * r["loo_worst_z"])) if r["k"] > 1 else r["z"]


def calibrated_test(pairs_by_base, P, f="final", n_fake=2000, seed=0, min_tok=1):
    """Empirical null for robust_T: fake modifiers with the same structure (same number of bases and
    derived forms per base), each base replaced by a random sign of 0.5-2x the real base's tokens and
    each derived form by a random sign of 0.5-2x the real derived form's tokens (widened until >= 8
    candidates). Captures between-sign heterogeneity, rarity of derived forms and base frequency.
    Returns T_obs, two-sided p and one-sided p (upper and lower)."""
    rng = np.random.default_rng(seed)
    r = robust(pairs_by_base, P, f)
    T = robust_T(r)
    pool = np.array(freq_pool(P, min_tok)); pn = np.array([P[s]["n"] for s in pool])

    def cands(n):
        lo, hi = 0.5, 2.0
        while True:
            idx = np.where((pn >= n * lo) & (pn <= n * hi))[0]
            if len(idx) >= 8 or lo < 0.01:
                return idx
            lo /= 1.5; hi *= 1.5
    struct = [(cands(P[b]["n"]), [cands(P[d]["n"]) for d in ds]) for b, ds in pairs_by_base.items()]
    Ts = []
    for _ in range(n_fake):
        used = set(); g = {}
        for cb, cds in struct:
            b = pool[rng.choice(cb)]
            while b in used:
                b = pool[rng.choice(cb)]
            used.add(b); ds = []
            for cd in cds:
                d = pool[rng.choice(cd)]
                tries = 0
                while d in used and tries < 50:
                    d = pool[rng.choice(cd)]; tries += 1
                used.add(d); ds.append(d)
            g[b] = ds
        Ts.append(robust_T(robust(g, P, f)))
    Ts = np.array(Ts)
    return {**r, "T": T, "p_two": float((1 + np.sum(np.abs(Ts) >= abs(T) - 1e-12)) / (n_fake + 1)),
            "p_up": float((1 + np.sum(Ts >= T - 1e-12)) / (n_fake + 1)),
            "p_down": float((1 + np.sum(Ts <= T + 1e-12)) / (n_fake + 1)),
            "null_T_sd": float(Ts.std()), "null_T_q95abs": float(np.percentile(np.abs(Ts), 95))}
