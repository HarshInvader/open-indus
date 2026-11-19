"""Mismatch study, stage 1: planted checks and the attacker-invariance kill test.

Prereg: docs/prereg/mismatch_study.md (stage 1 is sections 4-5). Text preparation reuses
experiments/redteam_decipherability/rt.py unchanged (folding, syllabifier, paragraphs, logogram set,
corpus sampling logic). Everything that depends on the value inventory is re-written here with the
inventory as a parameter, so the same code serves alphabet, syllabary and logo-syllabic scripts.

Attacks (all choose their answer by their own objective, never by accuracy):
  A0  bigram LM + channel term, annealed Gibbs, 4 restarts x 300 sweeps   (rt.py's attack)
  A1  trigram LM + channel term, annealed Gibbs, 8 restarts x 300 sweeps
  A2  EM on an HMM (hidden values, fixed bigram LM transitions), 10 restarts x 60 iterations
  A3  A0's search with many restarts: 1,000 restarts x 100 sweeps

Run (repo root):  .venv/bin/python -I experiments/mismatch_study/mm.py pc1|pc2|pc3|kill|gate|analyse
Results append to experiments/mismatch_study/out/<stage>.jsonl and are resumable.
"""
import json, math, random, sys, zlib
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "redteam_decipherability"))
import rt  # noqa: E402  (text prep only)

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

PAIRS = {"lat": {"src": "caesar.txt", "rel": "wiki_it.txt"},
         "fin": {"src": "kalevala.txt", "rel": "wiki_et.txt"}}


# ------------------------------------------------------------------ script types
class Script:
    """Value inventory. The last two values are always LOGO and the boundary #."""
    def __init__(self, kind):
        self.kind = kind
        if kind == "alpha":
            units = rt.CONS + rt.VOWS
        else:
            units = [v for v in rt.VALUES if v not in ("LOGO", "#")]
        self.values = units + ["LOGO", "#"]
        self.vidx = {v: i for i, v in enumerate(self.values)}
        self.nv = len(self.values)
        self.LOGO, self.BND = self.nv - 2, self.nv - 1
        self.q = 0.3 if kind == "logo" else 0.0

    def word_values(self, w, logos):
        if w in logos:
            return [self.LOGO]
        units = list(w) if self.kind == "alpha" else rt.syllabify(w)
        return [self.vidx[u] for u in units]


# ------------------------------------------------------------------ language models
def chunks(paras, seed=7):
    """Running text cut into 1-2 word chunks, as rt.train_lm does."""
    words = [w for p in paras for w in p]
    rng, i, out = random.Random(seed), 0, []
    while i < len(words):
        k = 1 if rng.random() < 0.5 else 2
        out.append(words[i:i + k]); i += k
    return words, out


def value_seqs(paras, sc, shuffle_seed=None):
    words, ch = chunks(paras)
    logos = rt.logo_set(words, sc.q)
    seqs = [[v for w in c for v in sc.word_values(w, logos)] for c in ch]
    if shuffle_seed is not None:  # shuffled-language negative: unigram kept, order destroyed
        flat = [v for s in seqs for v in s]
        random.Random(shuffle_seed).shuffle(flat)
        out, j = [], 0
        for s in seqs:
            out.append(flat[j:j + len(s)]); j += len(s)
        seqs = out
    return seqs


def lm2_probs(seqs, sc, alpha=0.1):
    C = np.full((sc.nv, sc.nv), alpha)
    for s in seqs:
        m = [sc.BND] + s + [sc.BND]
        for a, b in zip(m, m[1:]):
            C[a, b] += 1
    return C / C.sum(1, keepdims=True)


def lm3_probs(seqs, sc, P2, k=2.0):
    """P(c|a,b) = (n(abc) + k P2(c|b)) / (n(ab.) + k)."""
    n3 = np.zeros((sc.nv, sc.nv, sc.nv))
    for s in seqs:
        m = [sc.BND, sc.BND] + s + [sc.BND]
        for a, b, c in zip(m, m[1:], m[2:]):
            n3[a, b, c] += 1
    return (n3 + k * P2[None, :, :]) / (n3.sum(2, keepdims=True) + k)


def unigram(seqs, sc):
    c = np.bincount([v for s in seqs for v in s], minlength=sc.nv).astype(float)
    return c / c.sum()


# ------------------------------------------------------------------ planted corpus
def make_corpus(paras, ntok, rng, p_one, sc):
    """rt.make_corpus with the inventory as a parameter (same sampling rule)."""
    words = [w for p in paras for w in p]
    logos = rt.logo_set(words, sc.q)
    cands = []
    for p in paras:
        i = 0
        while i < len(p):
            k = 1 if rng.random() < p_one else 2
            cands.append(tuple(p[i:i + k])); i += k
    rng.shuffle(cands)
    seen, texts, n = set(), [], 0
    for c in cands:
        if c in seen:
            continue
        seen.add(c)
        vals = []
        for w in c:
            vals += sc.word_values(w, logos) if w not in logos else [("W", w)]
        texts.append(vals); n += len(vals)
        if n >= ntok:
            break
    return assign_signs(texts, rng, sc), n


def assign_signs(texts, rng, sc):
    syl_used = sorted({v for t in texts for v in t if not isinstance(v, tuple)})
    logo_words = sorted({v[1] for t in texts for v in t if isinstance(v, tuple)})
    signs = [("S", v) for v in syl_used] + [("L", w) for w in logo_words]
    order = list(range(len(signs))); rng.shuffle(order)
    sid = {signs[i]: j for j, i in enumerate(order)}
    true_val = {j: (s[1] if s[0] == "S" else sc.LOGO) for s, j in sid.items()}
    seqs = [[sid[("S", v)] if not isinstance(v, tuple) else sid[("L", v[1])] for v in t] for t in texts]
    return seqs, true_val


class Cipher:
    """Collapsed corpus: syllabic signs 0..S-1, LG = S (all logograms), B = S+1 (boundary)."""
    def __init__(self, seqs, true_val, sc):
        syl = sorted(s for s, v in true_val.items() if v != sc.LOGO)
        idx = {s: i for i, s in enumerate(syl)}
        self.S = S = len(syl); self.sc = sc
        LG, B = S, S + 1
        self.texts = [[idx.get(s, LG) for s in t] for t in seqs]
        self.N = np.zeros((S + 2, S + 2)); self.cnt = np.zeros(S + 2)
        t3 = Counter()
        for t in self.texts:
            m = [B] + t + [B]
            for a, b in zip(m, m[1:]):
                self.N[a, b] += 1
            for x in t:
                self.cnt[x] += 1
            m3 = [B, B] + t + [B]
            t3.update(zip(m3, m3[1:], m3[2:]))
        self.T = np.array([(a, b, c, n) for (a, b, c), n in t3.items()], dtype=np.int64)
        self.by_sign = {s: self.T[(self.T[:, 0] == s) | (self.T[:, 1] == s) | (self.T[:, 2] == s)] for s in range(S)}
        self.truth = np.array([true_val[s] for s in syl] + [sc.LOGO, sc.BND])

    def accuracy(self, key):
        c = self.cnt[:self.S]
        return float((c * (key[:self.S] == self.truth[:self.S])).sum() / c.sum())

    def tokens(self):
        return int(self.cnt[:self.S + 1].sum())


# ------------------------------------------------------------------ objective
def xlogx(x):
    return np.where(x > 0, x * np.log(np.maximum(x, 1e-300)), 0.0)


def channel(key, cp):
    c = cp.cnt[:cp.S]
    cv = np.bincount(key[:cp.S], weights=c, minlength=cp.sc.nv)
    return float(xlogx(c).sum() - xlogx(cv).sum())


def score2(key, cp, L2):
    return float((cp.N * L2[np.ix_(key, key)]).sum()) + channel(key, cp)


def score3(key, cp, L3):
    T = cp.T
    return float((T[:, 3] * L3[key[T[:, 0]], key[T[:, 1]], key[T[:, 2]]]).sum()) + channel(key, cp)


def chan_delta(s, key, cp, cv, cand):
    c = cp.cnt[s]
    if c <= 0:
        return 0.0
    base = cv.copy(); base[key[s]] -= c
    return -(xlogx(base[cand] + c) - xlogx(base[cand]))


def cond2(s, key, cp, L2, cv):
    cand = np.arange(cp.sc.nv - 2)
    row, col = cp.N[s].copy(), cp.N[:, s].copy()
    self_ = cp.N[s, s]; row[s] = 0; col[s] = 0
    v = L2[np.ix_(cand, key)] @ row + L2[np.ix_(key, cand)].T @ col + self_ * L2[cand, cand]
    return v + chan_delta(s, key, cp, cv, cand)


def cond3(s, key, cp, L3, cv):
    cand = np.arange(cp.sc.nv - 2)
    E = cp.by_sign[s]
    if len(E) == 0:
        return chan_delta(s, key, cp, cv, cand) + np.zeros(len(cand))
    idx = []
    for j in range(3):
        col = E[:, j]
        idx.append(np.where((col == s)[:, None], cand[None, :], key[col][:, None]))
    v = (E[:, 3][:, None] * L3[idx[0], idx[1], idx[2]]).sum(0)
    return v + chan_delta(s, key, cp, cv, cand)


def gibbs(cp, cond, scorefn, L, rng, init=None, sweeps=300, t0=3.0, greedy_only=False):
    """rt.search generalised to any conditional (same schedule)."""
    S, sc = cp.S, cp.sc
    g = np.random.default_rng(rng.randrange(1 << 30))
    key = np.zeros(S + 2, dtype=int); key[S] = sc.LOGO; key[S + 1] = sc.BND
    key[:S] = g.integers(0, sc.nv - 2, S) if init is None else init[:S]
    temps = [0.0] * 10 if greedy_only else list(np.linspace(t0, 1.0, sweeps - 10)) + [0.0] * 10
    for T in temps:
        cv = np.bincount(key[:S], weights=cp.cnt[:S], minlength=sc.nv).astype(float)
        for s in g.permutation(S):
            if cp.cnt[s] == 0:
                continue
            v = cond(s, key, cp, L, cv)
            if T == 0:
                new = int(np.argmax(v))
            else:
                z = (v - v.max()) / T; p = np.exp(z); p /= p.sum()
                new = int(g.choice(len(p), p=p))
            cv[key[s]] -= cp.cnt[s]; key[s] = new; cv[new] += cp.cnt[s]
    return key, scorefn(key, cp, L)


# ------------------------------------------------------------------ EM attack
def em_attack(cp, P2, rng, restarts=10, iters=60):
    """HMM: hidden value sequence follows the model's bigram P2 (fixed, boundary at both ends);
    each syllabic value emits a sign with free P(sign|value); LOGO emits LG. Pick the restart with the
    highest likelihood; key[s] = value with the largest expected count for sign s."""
    sc, S = cp.sc, cp.S
    nv = sc.nv
    syl_vals = np.arange(nv - 2)
    groups = defaultdict(list)
    for t in cp.texts:
        if t:
            groups[len(t)].append(t)
    groups = {L: np.array(v) for L, v in groups.items()}
    g = np.random.default_rng(rng.randrange(1 << 30))
    best = None
    for r in range(restarts):
        Em = np.zeros((nv, S + 1))  # P(sign | value), columns: syllabic signs then LG
        Em[syl_vals, :S] = g.dirichlet(np.ones(S), size=len(syl_vals))
        Em[sc.LOGO, S] = 1.0
        for it in range(iters + 1):
            counts = np.zeros((nv, S + 1)); ll = 0.0
            for L, obs in groups.items():
                n = len(obs)
                al = np.zeros((L, n, nv)); sca = np.zeros((L, n))
                a = P2[sc.BND][None, :] * Em[:, obs[:, 0]].T
                sca[0] = a.sum(1) + 1e-300; al[0] = a / sca[0][:, None]
                for t in range(1, L):
                    a = (al[t - 1] @ P2) * Em[:, obs[:, t]].T
                    sca[t] = a.sum(1) + 1e-300; al[t] = a / sca[t][:, None]
                end = al[L - 1] @ P2[:, sc.BND]
                ll += float(np.log(sca).sum() + np.log(end + 1e-300).sum())
                be = np.zeros((L, n, nv)); be[L - 1] = P2[:, sc.BND][None, :] / (end[:, None] + 1e-300)
                for t in range(L - 2, -1, -1):
                    be[t] = ((Em[:, obs[:, t + 1]].T * be[t + 1]) @ P2.T) / sca[t + 1][:, None]
                for t in range(L):
                    gam = al[t] * be[t]
                    gam /= gam.sum(1, keepdims=True) + 1e-300
                    np.add.at(counts.T, obs[:, t], gam)
            if it == iters:
                break
            Em = counts.copy(); Em[np.ix_(syl_vals, np.arange(S))] += 1e-4  # no value can die
            Em[sc.LOGO] = 0; Em[sc.LOGO, S] = 1.0; Em[sc.BND] = 0; Em[syl_vals, S] = 0
            Em /= Em.sum(1, keepdims=True) + 1e-300
        key = np.zeros(S + 2, dtype=int); key[S] = sc.LOGO; key[S + 1] = sc.BND
        key[:S] = np.argmax(counts[syl_vals, :S], axis=0)
        if best is None or ll > best[0]:
            best = (ll, key)
    return best[1], best[0]


# ------------------------------------------------------------------ one cell
def build(pair, ntok, kind, rep, model="K2", shuffle=False):
    sc = Script(kind)
    cfg = PAIRS[pair]
    rng = random.Random(zlib.crc32(f"mm|{pair}|{ntok}|{kind}|{rep}".encode()))
    paras = rt.paragraphs(cfg["src"])
    half_a = [p for i, p in enumerate(paras) if i % 2 == 0]
    half_b = [p for i, p in enumerate(paras) if i % 2 == 1]
    wl = np.mean([len(sc.word_values(w, set())) for p_ in half_a for w in p_])
    p_one = float(min(1.0, max(0.0, 2.0 - 4.5 / wl)))
    (seqs, true_val), n = make_corpus(half_a, ntok, rng, p_one, sc)
    cp = Cipher(seqs, true_val, sc)
    if model == "K0":
        ms = value_seqs(half_b, sc, shuffle_seed=11 if shuffle else None)
    else:
        ms = value_seqs(rt.paragraphs(cfg["rel"]), sc)
    P2 = lm2_probs(ms, sc)
    return cp, ms, P2, sc


def freq_rank_baseline(cp, ms):
    """Assign signs to values by matching frequency ranks (model unigram vs sign counts)."""
    u = unigram(ms, cp.sc)[:cp.sc.nv - 2]
    vals = np.argsort(-u)
    order = np.argsort(-cp.cnt[:cp.S])
    key = np.zeros(cp.S + 2, dtype=int); key[cp.S] = cp.sc.LOGO; key[cp.S + 1] = cp.sc.BND
    for r, s in enumerate(order):
        key[s] = vals[r] if r < len(vals) else vals[-1]
    return cp.accuracy(key)


def run_attack(att, cp, ms, P2, seed, R=None):
    rng = random.Random(seed)
    L2 = np.log(P2)
    if att == "A0" or att == "A3":
        R = R or (4 if att == "A0" else 1000)
        sw = 300 if att == "A0" else 100
        runs = [gibbs(cp, cond2, score2, L2, rng, sweeps=sw) for _ in range(R)]
    elif att == "A1":
        L3 = np.log(lm3_probs(ms, cp.sc, P2))
        runs = [gibbs(cp, cond3, score3, L3, rng) for _ in range(R or 8)]
    elif att == "A2":
        runs = [em_attack(cp, P2, rng, restarts=R or 10)]
    accs = [cp.accuracy(k) for k, _ in runs]
    i = int(np.argmax([s for _, s in runs]))
    return dict(acc=accs[i], obj=float(runs[i][1]), max_acc=max(accs), n_restarts=len(runs),
                restart_accs=accs if len(accs) <= 50 else None)


# ------------------------------------------------------------------ synthetic sources (PC2)
def synth_cell(lam, rep, ntok=10000):
    """True source P: sparse random bigram chain over the 95 syllabic values with Zipf unigrams.
    Attacker's model Q = lam*P + (1-lam)*R, R an independent chain. Exact probabilities, no estimation."""
    sc = Script("syll")
    nv, K = sc.nv, sc.nv - 2
    g = np.random.default_rng(1000 + rep)
    zipf = 1.0 / np.arange(1, K + 1); g.shuffle(zipf)

    def chain():
        P = np.zeros((nv, nv))
        for a in list(range(K)) + [sc.BND]:
            row = g.dirichlet(np.full(K, 0.05)) * 0.7 + 0.3 * zipf / zipf.sum()
            P[a, :K] = 0.8 * row; P[a, sc.BND] = 0.2
        P[sc.LOGO, :K] = 1.0 / K
        return P
    P, R = chain(), chain()
    Q = lam * P + (1 - lam) * R
    Q = np.maximum(Q, 1e-9); Q /= Q.sum(1, keepdims=True)  # no log(0) in the objective
    rng = random.Random(77 + rep)
    texts, n = [], 0
    while n < ntok:
        L = rng.randint(3, 7); t, prev = [], sc.BND
        for _ in range(L):
            p = P[prev, :K] / P[prev, :K].sum()
            v = int(g.choice(K, p=p)); t.append(v); prev = v
        texts.append(t); n += L
    seqs, true_val = assign_signs(texts, rng, sc)
    cp = Cipher(seqs, true_val, sc)
    # excess cross-entropy of Q over P (bits per value) on fresh text from P
    held, xs = [], 0.0
    for _ in range(4000):
        L = rng.randint(3, 7); prev = sc.BND
        for _ in range(L):
            p = P[prev, :K] / P[prev, :K].sum(); v = int(g.choice(K, p=p))
            xs += math.log2(P[prev, v] / Q[prev, v]); prev = v
        held.append(L)
    return cp, Q, xs / sum(held)


def fit_boundary(rows):
    """Logistic fit acc ~ sigmoid(a + b*dH + c*log10(n)) by least squares; returns (a,b,c) and the
    dH where acc = 0.5 for each n. Used by PC2's planted-surface check and by the core plane."""
    from scipy.optimize import least_squares
    X = np.array([[r["dH"], math.log10(r["n"])] for r in rows]); y = np.array([r["acc"] for r in rows])

    def res(p):
        return 1 / (1 + np.exp(-(p[0] + p[1] * X[:, 0] + p[2] * X[:, 1]))) - y
    p = least_squares(res, x0=[1.0, -1.0, 0.5]).x
    return p, (lambda n: -(p[0] + p[2] * math.log10(n)) / p[1])


# ------------------------------------------------------------------ stages
def append(name, rec):
    with open(OUT / f"{name}.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(name, json.dumps({k: v for k, v in rec.items() if k != "restart_accs"}), flush=True)


def have(name, keys):
    f = OUT / f"{name}.jsonl"
    if not f.exists():
        return set()
    return {tuple(json.loads(l)[k] for k in keys) for l in f.read_text().splitlines()}


def stage_pc1():
    """True-model control: every script type, both pairs, 2.5k, A0. Pass: acc >= 0.90 in all 6 cells."""
    done = have("pc1", ("pair", "kind"))
    for pair in PAIRS:
        for kind in ("alpha", "syll", "logo"):
            if (pair, kind) in done:
                continue
            cp, ms, P2, sc = build(pair, 2500, kind, 0, model="K0")
            r = run_attack("A0", cp, ms, P2, seed=1)
            append("pc1", dict(pair=pair, kind=kind, ntok=2500, S=cp.S, tokens=cp.tokens(), **r))


def stage_pc2():
    """Dialled-KL synthetic sources, 10k, A0, 2 reps; plus the planted-surface fit check."""
    done = have("pc2", ("lam", "rep"))
    for rep in (0, 1):
        for lam in (1.0, 0.8, 0.6, 0.4, 0.2, 0.0):
            if (lam, rep) in done:
                continue
            cp, Q, dH = synth_cell(lam, rep)
            r = run_attack("A0", cp, None, Q, seed=2 + rep)
            append("pc2", dict(lam=lam, rep=rep, dH=dH, S=cp.S, tokens=cp.tokens(), **r))
    g = np.random.default_rng(5)
    truth = (2.0, -4.0, 0.8)  # planted surface
    rows = [dict(dH=d, n=n, acc=float(np.clip(1 / (1 + np.exp(-(truth[0] + truth[1] * d + truth[2] * math.log10(n))))
                                              + g.normal(0, 0.05), 0, 1)))
            for d in np.linspace(0, 2, 9) for n in (1000, 2500, 10000, 30000, 100000)]
    _, bd = fit_boundary(rows)
    planted = -(truth[0] + truth[2] * 4) / truth[1]
    (OUT / "pc2_fit.json").write_text(json.dumps(dict(planted_dH_at_10k=planted, recovered=bd(10000))))
    print("pc2 fit", planted, bd(10000))


def stage_pc3():
    """Shuffled-language negative: model trained on order-destroyed true-language text, 10k, A0."""
    done = have("pc3", ("pair",))
    for pair in PAIRS:
        if (pair,) in done:
            continue
        cp, ms, P2, sc = build(pair, 10000, "syll", 0, model="K0", shuffle=True)
        r = run_attack("A0", cp, ms, P2, seed=3)
        append("pc3", dict(pair=pair, ntok=10000, freq_baseline=freq_rank_baseline(cp, ms), **r))


def stage_gate():
    """Each attack must recover the true key under the true model (K0, syllabary, 10k, rep 0) at >= 0.90,
    or its kill-test result is uninformative."""
    done = have("gate", ("pair", "att"))
    for pair in PAIRS:
        for att in ("A0", "A1", "A2"):
            if (pair, att) in done:
                continue
            cp, ms, P2, sc = build(pair, 10000, "syll", 0, model="K0")
            r = run_attack(att, cp, ms, P2, seed=4)
            append("gate", dict(pair=pair, att=att, **r))


def stage_kill():
    """Related-language model (K2), syllabary, both pairs. A0/A1/A2 at 2.5k, 10k, 30k x 3 reps;
    A3 at 10k and 30k, rep 0."""
    done = have("kill", ("pair", "ntok", "att", "rep"))
    plan = [(p, n, a, r) for a in ("A0", "A1", "A2") for p in PAIRS for n in (2500, 10000, 30000) for r in range(3)]
    plan += [(p, n, "A3", 0) for p in PAIRS for n in (10000, 30000)]
    for p, n, a, r in plan:
        if (p, n, a, r) in done:
            continue
        cp, ms, P2, sc = build(p, n, "syll", r, model="K2")
        res = run_attack(a, cp, ms, P2, seed=zlib.crc32(f"{p}{n}{a}{r}".encode()))
        res["true_obj_A0"] = score2(cp.truth.copy(), cp, np.log(P2))
        append("kill", dict(pair=p, ntok=n, att=a, rep=r, S=cp.S, tokens=cp.tokens(), **res))


def load(name):
    f = OUT / f"{name}.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []


def analyse():
    from scipy.stats import spearmanr
    v = {}
    pc1 = load("pc1")
    v["PC1"] = dict(cells=len(pc1), min_acc=min((r["acc"] for r in pc1), default=None),
                    pass_=len(pc1) == 6 and all(r["acc"] >= 0.90 for r in pc1))
    pc2 = load("pc2")
    if pc2:
        by = defaultdict(list)
        for r in pc2:
            by[r["lam"]].append(r["acc"])
        lams = sorted(by); accs = [float(np.mean(by[l])) for l in lams]
        rho = float(spearmanr(lams, accs).correlation) if len(lams) > 2 else None
        fit = json.loads((OUT / "pc2_fit.json").read_text()) if (OUT / "pc2_fit.json").exists() else {}
        fit_ok = bool(fit) and abs(fit["recovered"] - fit["planted_dH_at_10k"]) <= 0.10 * abs(fit["planted_dH_at_10k"])
        v["PC2"] = dict(acc_by_lam=dict(zip(lams, accs)), spearman=rho, fit=fit,
                        pass_=(by.get(1.0) and np.mean(by[1.0]) >= 0.90) and rho is not None and rho >= 0.8 and fit_ok)
    pc3 = load("pc3")
    v["PC3"] = dict(rows=[(r["pair"], r["acc"], r["freq_baseline"]) for r in pc3],
                    pass_=len(pc3) == 2 and all(r["acc"] <= r["freq_baseline"] + 0.05 for r in pc3))
    gate = load("gate")
    v["gate"] = {f'{r["pair"]}-{r["att"]}': r["acc"] for r in gate}
    valid = {a for a in ("A0", "A1", "A2") if all(r["acc"] >= 0.90 for r in gate if r["att"] == a)
             and sum(r["att"] == a for r in gate) == 2}
    valid.add("A3") if "A0" in valid else None
    kill = load("kill")
    cells = defaultdict(list)
    for r in kill:
        cells[(r["pair"], r["ntok"], r["att"])].append(r["acc"])
    means = {f"{p}|{n}|{a}": float(np.mean(x)) for (p, n, a), x in cells.items()}
    lifted = {k: m for k, m in means.items() if k.split("|")[2] in valid and m > 0.5}
    spread = {}
    for (p, n) in {(p, n) for (p, n, a) in cells}:
        ms_ = [means.get(f"{p}|{n}|{a}") for a in sorted(valid) if f"{p}|{n}|{a}" in means]
        if ms_:
            spread[f"{p}|{n}"] = float(max(ms_) - min(ms_))
    v["kill_test"] = dict(valid_attacks=sorted(valid), cell_means=means, cells_above_0_5=lifted,
                          spread_across_attacks=spread,
                          verdict=("KILL: an attack lifts related-model recovery above 0.5" if lifted else
                                   "SURVIVES (no attack above 0.5)") + ("" if len(valid) >= 3 else " -- fewer than 3 valid attacks: uninformative"),
                          plateau_within_0_10=all(s <= 0.10 for s in spread.values()) if spread else None)
    print(json.dumps(v, indent=1, default=str))
    (OUT / "verdicts.json").write_text(json.dumps(v, indent=1, default=str))


if __name__ == "__main__":
    {"pc1": stage_pc1, "pc2": stage_pc2, "pc3": stage_pc3, "gate": stage_gate, "kill": stage_kill,
     "analyse": analyse}[sys.argv[1]]()
