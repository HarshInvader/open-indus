"""sigil_heldout: goodness-of-fit test of a fitted SIGIL emblem grammar (prereg docs/prereg/sigil_heldout.md).
A SIGIL-family grammar is fitted to a corpus's train part; 200 synthetic corpora of test size are generated; four
vocabulary-free statistics of the real test part are compared to the synthetic distribution (two-sided percentile p, Holm).
Run: .venv/bin/python -I experiments/sigil_heldout/run.py time            # one planted fit, timing only
     .venv/bin/python -I experiments/sigil_heldout/run.py kill [workers]  # gates; no Indus
     .venv/bin/python -I experiments/sigil_heldout/run.py indus           # only if kill.json says passed
"""
import json, math, random, sys, time
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/language_vs_code"))
import lvc_corpora as C   # noqa: E402
import lvc_metrics as M   # noqa: E402

ROLES = ["OP", "H1", "M1", "H2", "M2", "M3", "H3", "IS", "TE"]
BLOCKS = ["B1", "B2", "B3"]
NREG = 4; NSYN = 200; SWEEPS = 5; RESTARTS = 3; EM_IT = 8; ALPHA = 5.0
N_TRAIN, N_TEST = 1680, 565          # Indus dev / held-out text counts (shape only)
SEED = 20261124
ORDERS = list(permutations(BLOCKS))


# ---------------- parsing a text under a role assignment ----------------
def parse(signs, role):
    """Deterministic SIGIL parse. Returns (op, is_, te, blocks) or None. blocks: list of (btype, head, dup, mod)."""
    R = [role[s] for s in signs]; S = list(signs)
    is_ = None
    if len(R) >= 2 and R[-2] == "IS":
        is_ = S[-2]; del R[-2]; del S[-2]
    if "IS" in R:
        return None
    op = None
    if R and R[0] == "OP":
        op = S[0]; R = R[1:]; S = S[1:]
    te = None
    if R and R[-1] == "TE":
        te = S[-1]; R = R[:-1]; S = S[:-1]
    if "OP" in R or "TE" in R:
        return None
    blocks, i, n, seen = [], 0, len(R), set()
    while i < n:
        r = R[i]
        if r in ("H1", "H2"):
            b = "B1" if r == "H1" else "B2"; h = S[i]; i += 1
            dup = False
            if i < n and R[i] == r and S[i] == h:
                dup = True; i += 1
            mr = "M1" if r == "H1" else "M2"; mod = None
            if i < n and R[i] == mr:
                mod = S[i]; i += 1
        elif r in ("M3", "H3"):
            b = "B3"; mod = None
            if r == "M3":
                mod = S[i]; i += 1
                if not (i < n and R[i] == "H3"):
                    return None
            h = S[i]; i += 1; dup = False
            if i < n and R[i] == "H3" and S[i] == h:
                dup = True; i += 1
        else:
            return None
        if b in seen:
            return None
        seen.add(b); blocks.append((b, h, dup, mod))
    if op is None and te is None and not blocks:
        return None
    return (op, is_, te, tuple(blocks))


def order_term(present, order, s):
    ref = [b for b in order if b in present]
    k = len(present)
    if k <= 1:
        return 1.0
    if list(present) == ref:
        return (1 - s) ** (k - 1)
    for j in range(k - 1):
        q = list(present); q[j], q[j + 1] = q[j + 1], q[j]
        if q == ref:
            return s * (1 - s) ** max(k - 2, 0)
    return 0.0


# ---------------- the fitted model ----------------
class Fit:
    def __init__(self, texts, role, rng):
        self.texts, self.role, self.rng = texts, dict(role), rng
        self.uni = Counter(s for t in texts for s in t); self.N = sum(self.uni.values())

    def estimate(self, parses, resp):
        """M-step given parses (None = unparsable) and region responsibilities (n x NREG)."""
        P = [(p, r) for p, r in zip(parses, resp) if p is not None]
        self.eps = min(max(1 - len(P) / len(parses), 1e-4), 0.999)
        self.unp_len = [len(t) for t, p in zip(self.texts, parses) if p is None] or [1]
        w = np.array([r for _, r in P]) if P else np.ones((1, NREG)) / NREG
        self.pi = (w.sum(0) + 1) / (w.sum() + NREG)
        em = {k: Counter() for k in ROLES}; emr = {k: [Counter() for _ in range(NREG)] for k in ("OP", "TE")}
        cnt = Counter(); lic = defaultdict(Counter)
        op_r = np.ones(NREG); n_r = np.ones(NREG) * 2
        self.order = []
        for (op, is_, te, bl), r in P:
            n_r += r
            if op is not None:
                op_r += r; em["OP"][op] += 1
                for g in range(NREG): emr["OP"][g][op] += r[g]
            if te is not None:
                cnt["te"] += 1; em["TE"][te] += 1
                for g in range(NREG): emr["TE"][g][te] += r[g]
            cnt["n"] += 1; cnt["is"] += is_ is not None; cnt["len2"] += 1
            if is_ is not None: em["IS"][is_] += 1
            for b, h, dup, mod in bl:
                cnt[b] += 1; cnt[b + "dup"] += dup; cnt[b + "mod"] += mod is not None
                em[{"B1": "H1", "B2": "H2", "B3": "H3"}[b]][h] += 1
                if mod is not None:
                    em[{"B1": "M1", "B2": "M2", "B3": "M3"}[b]][mod] += 1
                    if b == "B1": lic[h][mod] += 1
        self.p_op = op_r / n_r
        n = max(cnt["n"], 1)
        self.q = {b: (cnt[b] + 1) / (n + 2) for b in BLOCKS}
        self.dup = {b: (cnt[b + "dup"] + 1) / (cnt[b] + 2) for b in BLOCKS}
        self.mod = {b: (cnt[b + "mod"] + 1) / (cnt[b] + 2) for b in BLOCKS}
        self.p_te = (cnt["te"] + 1) / (n + 2); self.p_is = (cnt["is"] + 1) / (n + 2)
        self.em = {k: (v, sum(v.values())) for k, v in em.items()}
        self.emr = {k: [(c, sum(c.values())) for c in v] for k, v in emr.items()}
        self.lic = {h: (c, sum(c.values())) for h, c in lic.items()}
        # region orders and swap rate: best permutation per region by expected log-lik of order terms
        self.s = 0.06
        for g in range(NREG):
            best = max(ORDERS, key=lambda o: sum(r[g] * math.log(order_term([b for b, *_ in bl], o, self.s) + 1e-9)
                                                 for (_, _, _, bl), r in P))
            self.order.append(best)
        ex = sw = 0.0
        for (_, _, _, bl), r in P:
            pres = [b for b, *_ in bl]
            if len(pres) < 2: continue
            for g in range(NREG):
                ref = [b for b in self.order[g] if b in pres]
                if pres == ref: ex += r[g] * (len(pres) - 1)
                elif order_term(pres, self.order[g], 0.5) > 0: sw += r[g]; ex += r[g] * max(len(pres) - 2, 0)
        self.s = min(max((sw + 0.5) / (sw + ex + 1), 0.005), 0.45)

    def e(self, k, s):
        c, n = self.em[k]
        return (c[s] + 0.1) / (n + 0.1 * (len(c) + 1))

    def er(self, k, g, s):
        c, n = self.emr[k][g]
        return (c[s] + ALPHA * self.e(k, s)) / (n + ALPHA)

    def lp_region(self, p):
        """log P(text, region g) for each g (parsable text)."""
        op, is_, te, bl = p
        base = 0.0; pres = [b for b, *_ in bl]
        for b in BLOCKS:
            base += math.log(self.q[b] if b in pres else 1 - self.q[b])
        for b, h, dup, mod in bl:
            hk = {"B1": "H1", "B2": "H2", "B3": "H3"}[b]
            base += math.log(self.e(hk, h)) + math.log(self.dup[b] if dup else 1 - self.dup[b])
            base += math.log(self.mod[b] if mod is not None else 1 - self.mod[b])
            if mod is not None:
                if b == "B1" and h in self.lic:
                    c, n = self.lic[h]; base += math.log((c[mod] + 0.1 * self.e("M1", mod)) / (n + 0.1))
                else:
                    base += math.log(self.e({"B1": "M1", "B2": "M2", "B3": "M3"}[b], mod))
        base += math.log(self.p_is if is_ is not None else 1 - self.p_is) + (math.log(self.e("IS", is_)) if is_ is not None else 0)
        base += math.log(self.p_te if te is not None else 1 - self.p_te)
        out = []
        for g in range(NREG):
            ot = order_term(pres, self.order[g], self.s)
            if ot == 0:
                out.append(-math.inf); continue
            v = base + math.log(self.pi[g]) + math.log(ot)
            v += math.log(self.p_op[g]) + math.log(self.er("OP", g, op)) if op is not None else math.log(1 - self.p_op[g])
            if te is not None: v += math.log(self.er("TE", g, te))
            out.append(v)
        return out

    def ll_text(self, t, p):
        if p is not None:
            v = self.lp_region(p); m = max(v)
            if m > -math.inf:
                return math.log(1 - self.eps) + m + math.log(sum(math.exp(x - m) for x in v))
        return math.log(self.eps) + sum(math.log(self.uni[s] / self.N) for s in t)

    def em_regions(self, parses):
        resp = [self.rng.dirichlet(np.ones(NREG)) if p is not None else None for p in parses]
        self.estimate(parses, resp)
        for _ in range(EM_IT):
            new = []
            for p in parses:
                if p is None: new.append(None); continue
                v = np.array(self.lp_region(p)); m = v.max()
                new.append(np.exp(v - m) / np.exp(v - m).sum() if m > -np.inf else np.ones(NREG) / NREG)
            resp = new; self.estimate(parses, resp)
        return resp

    def total_ll(self, parses):
        return sum(self.ll_text(t, p) for t, p in zip(self.texts, parses))

    # ---------------- generation ----------------
    def draw(self, k, g=None):
        c, _ = self.emr[k][g] if g is not None else self.em[k]
        if g is not None and self.rng.random() < ALPHA / (self.emr[k][g][1] + ALPHA) or not c:
            c, _ = self.em[k]
        if not c:
            return None
        keys = list(c); w = np.array([c[x] for x in keys], float)
        return keys[self.rng.choice(len(keys), p=w / w.sum())]

    def generate(self, n):
        rng = self.rng; out = []
        ukeys = list(self.uni); uw = np.array([self.uni[x] for x in ukeys], float); uw /= uw.sum()
        while len(out) < n:
            if rng.random() < self.eps:
                L = self.unp_len[rng.integers(len(self.unp_len))]
                out.append([ukeys[i] for i in rng.choice(len(ukeys), size=L, p=uw)]); continue
            g = rng.choice(NREG, p=self.pi)
            t = []
            if rng.random() < self.p_op[g]:
                x = self.draw("OP", g); t += [x] if x else []
            pres = [b for b in self.order[g] if rng.random() < self.q[b]]
            for j in range(len(pres) - 1):
                if rng.random() < self.s: pres[j], pres[j + 1] = pres[j + 1], pres[j]
            for b in pres:
                hk, mk = {"B1": ("H1", "M1"), "B2": ("H2", "M2"), "B3": ("H3", "M3")}[b]
                h = self.draw(hk)
                if h is None: continue
                dup = rng.random() < self.dup[b]
                mod = None
                if rng.random() < self.mod[b]:
                    if b == "B1" and h in self.lic:
                        c, _ = self.lic[h]; ks = list(c); w = np.array([c[x] for x in ks], float); mod = ks[rng.choice(len(ks), p=w / w.sum())]
                    else:
                        mod = self.draw(mk)
                blk = [h] + ([h] if dup else [])
                if mod is not None:
                    blk = [mod] + blk if b == "B3" else blk + [mod]
                t += blk
            if (not t or rng.random() < self.p_te):
                x = self.draw("TE", g); t += [x] if x else []
            if len(t) >= 2 and rng.random() < self.p_is:
                x = self.draw("IS")
                if x: t.insert(len(t) - 1, x)
            if t:
                out.append(t)
        return out


# ---------------- fitting: role induction + hard EM ----------------
def profile(texts):
    f = defaultdict(lambda: np.zeros(4)); c = Counter()
    for t in texts:
        L = len(t)
        for i, s in enumerate(t):
            c[s] += 1
            f[s] += [L == 1, i == 0 and L > 1, i == L - 1 and L > 1, i / (L - 1) if L > 1 else 0.5]
    return {s: f[s] / c[s] for s in c}, c


def init_roles(texts, rng, heuristic):
    prof, c = profile(texts)
    if not heuristic:
        return {s: ROLES[rng.integers(len(ROLES))] for s in prof}
    # heuristic: first-heavy -> OP, last/sole-heavy -> TE, rest by mean relative position into the six middle roles
    role = {}
    mids = []
    for s, (sole, first, last, pos) in prof.items():
        if first > 0.6: role[s] = "OP"
        elif last + sole > 0.6: role[s] = "TE"
        else: mids.append((pos, s))
    mids.sort()
    order = ["H1", "M1", "H2", "M2", "M3", "H3"]
    for j, (_, s) in enumerate(mids):
        role[s] = order[min(j * 6 // max(len(mids), 1), 5)]
    return role


# ---------------- stage 1: role induction by a class bigram restricted to SIGIL transitions ----------------
_BS = ["H1", "H2", "M3", "H3"]; _BE = ["H1", "M1", "H2", "M2", "H3"]
ALLOWED = {"<s>": set(["OP", "TE", "IS"] + _BS), "OP": set(_BS + ["TE", "IS", "</s>"]), "M3": {"H3"}, "IS": set(_BE + ["TE"]), "TE": {"</s>"}}
for _r in _BE:
    ALLOWED[_r] = set(_BS + ["TE", "IS", "</s>"]) | ({_r} if _r in ("H1", "H2", "H3") else set()) | ({"M1"} if _r == "H1" else {"M2"} if _r == "H2" else set())
OFF = math.log(1e-4)


def stage1(texts, role, rng, sweeps=15):
    by_sign = defaultdict(list)
    for i, t in enumerate(texts):
        for s in set(t): by_sign[s].append(i)
    ns = Counter(s for t in texts for s in t)
    for _ in range(sweeps):
        tr = Counter(); fr = Counter(); nr = Counter()
        for t in texts:
            seq = ["<s>"] + [role[s] for s in t] + ["</s>"]
            tr.update(zip(seq, seq[1:])); fr.update(seq[:-1])
        for s, c in ns.items(): nr[role[s]] += c
        def lt(a, b):
            return math.log((tr[(a, b)] + 0.5) / (fr[a] + 0.5 * 11)) if b in ALLOWED.get(a, ()) else OFF
        moved = 0
        for s in rng.permutation(list(by_sign)):
            cur = role[s]; best, bv = cur, None
            for r in ROLES:
                role[s] = r
                v = ns[s] * math.log(ns[s] / (nr[r] + (0 if r == cur else ns[s])))
                for i in by_sign[s]:
                    seq = ["<s>"] + [role[x] for x in texts[i]] + ["</s>"]
                    v += sum(lt(a, b) for a, b in zip(seq, seq[1:]))
                if bv is None or v > bv + 1e-9: best, bv = r, v
            role[s] = best
            if best != cur:
                moved += 1; nr[cur] -= ns[s]; nr[best] += ns[s]
        if moved == 0: break
    return role


def fit(texts, seed):
    rng = np.random.default_rng(seed)
    best = None
    by_sign = defaultdict(list)
    for i, t in enumerate(texts):
        for s in set(t): by_sign[s].append(i)
    for rs in range(RESTARTS):
        F = Fit(texts, stage1(texts, init_roles(texts, rng, heuristic=(rs == 0)), rng), rng)
        parses = [parse(t, F.role) for t in texts]
        F.em_regions(parses)
        for sw in range(SWEEPS):
            moved = 0
            for s in rng.permutation(list(by_sign)):
                idx = by_sign[s]; cur = F.role[s]
                scores = {}
                for r in ROLES:
                    F.role[s] = r
                    k = "OP" if r == "OP" else r
                    ll = 0.0
                    for i in idx:
                        ll += F.ll_text(texts[i], parse(texts[i], F.role))
                    scores[r] = ll
                r_best = max(scores, key=scores.get)
                F.role[s] = r_best if scores[r_best] > scores[cur] + 1e-9 else cur
                moved += F.role[s] != cur
                if F.role[s] != cur:
                    for i in idx: parses[i] = parse(texts[i], F.role)
            F.em_regions(parses)
            if moved == 0: break
        ll = F.total_ll(parses)
        if best is None or ll > best[0]:
            best = (ll, F)
    return best[1]


# ---------------- statistics (vocabulary-free, inside one corpus) ----------------
def bigram_gain(texts, seed=0):
    rng = random.Random(seed); idx = list(range(len(texts))); rng.shuffle(idx)
    folds = [idx[k::5] for k in range(5)]; tot_u = tot_b = n = 0.0
    for k in range(5):
        test = [texts[i] for i in folds[k]]; train = [texts[i] for j in range(5) if j != k for i in folds[j]]
        uni = Counter(); big = Counter(); ctx = Counter()
        for t in train:
            seq = ["<s>"] + list(t) + ["</s>"]
            uni.update(seq[1:]); big.update(zip(seq, seq[1:])); ctx.update(seq[:-1])
        V = len(uni) + 1; Nu = sum(uni.values())
        types_after = Counter(a for a, _ in big)
        for t in test:
            seq = ["<s>"] + list(t) + ["</s>"]
            for a, b in zip(seq, seq[1:]):
                pu = (uni[b] + 0.5) / (Nu + 0.5 * V)
                c, T = ctx[a], types_after[a]
                pb = (big[(a, b)] + T * pu) / (c + T) if c else pu       # Witten-Bell
                tot_u -= math.log2(pu); tot_b -= math.log2(pb); n += 1
    return (tot_u - tot_b) / n


def polyvalence(texts, min_tok=10):
    c = defaultdict(Counter)
    for t in texts:
        L = len(t)
        for i, s in enumerate(t):
            c[s]["sole" if L == 1 else "first" if i == 0 else "last" if i == L - 1 else "mid"] += 1
    H = []
    for s, d in c.items():
        n = sum(d.values())
        if n >= min_tok:
            H.append(-sum(v / n * math.log2(v / n) for v in d.values()))
    return float(np.mean(H)) if H else 0.0


def stats(texts):
    segs = M.segment(texts)
    return dict(S1_skip_cmi=M.skip_cmi(texts), S2_bigram_gain=bigram_gain(texts),
                S3_seg_share_multi=float(np.mean([len(x) > 1 for s in segs for x in s])), S4_polyvalence=polyvalence(texts))


def holm(ps, alpha=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for j, i in enumerate(order):
        if ps[i] <= alpha / (len(ps) - j): rej[i] = True
        else: break
    return rej


def gof(train, test, seed):
    F = fit(train, seed)
    obs = stats(test)
    syn = [stats(F.generate(len(test))) for _ in range(NSYN)]
    ps = {}
    for k, v in obs.items():
        a = np.array([s[k] for s in syn])
        ps[k] = float(min(1.0, 2 * min((1 + (a <= v).sum()) / (NSYN + 1), (1 + (a >= v).sum()) / (NSYN + 1))))
    rej = holm(list(ps.values()))
    reject = bool(any(rej))   # eps is reported, not a reject rule: the fitter leaves ~41-46% of SIGIL's own texts unparsed (prereg)
    return dict(reject=reject, eps=F.eps, p=ps, obs=obs, syn_mean={k: float(np.mean([s[k] for s in syn])) for k in obs},
                holm_reject=dict(zip(ps, rej)), roles=Counter(F.role.values()))


# ---------------- corpora for the gates ----------------
def sigil_param(seed, jitter=False):
    """lvc_corpora.sigil with optional jittered parameters (stock = same generator, same code path)."""
    if not jitter:
        return C.sigil(n=3000, seed=seed)
    r = random.Random(seed * 7 + 1)
    j = lambda p: min(max(p + r.uniform(-0.15, 0.15), 0.02), 0.98)
    pool = lambda k: max(5, int(k * r.uniform(0.5, 2.0)))
    nreg = r.randint(2, 6)
    rng = random.Random(seed)
    regions = [r.random() + 0.2 for _ in range(nreg)]
    deity = C._PYUrn(rng, "DE", pool(70)); guild = C._PYUrn(rng, "GU", pool(80)); comm = C._PYUrn(rng, "CO", pool(90)); epi = C._PYUrn(rng, "EP", pool(90))
    P = dict(ded=j(0.75), patron=j(0.3), dbl=j(0.05), epi=j(0.65), off=j(0.65), rank=j(0.4), led=j(0.6), tally=j(0.45), cdbl=j(0.05),
             swap=j(0.06), term=j(0.65), issue=j(0.05))
    openers = [f"OP{i}" for i in range(12)]; ranks = [f"RK{i}" for i in range(8)]; tallies = [f"TA{i}" for i in range(1, 10)]
    terms = [f"TE{i}" for i in range(5)]; issue = [f"IS{i}" for i in range(20)]
    lic = {}; conf = []
    for g in range(nreg):
        o = ["ded", "off", "led"]; rng.shuffle(o)
        conf.append(dict(order=o, patron=f"DE{g}", op=rng.sample(openers, 4), term=rng.sample(terms, 2), p_open=rng.uniform(0.35, 0.6)))
    texts = []
    for _ in range(3000):
        c = conf[rng.choices(range(nreg), regions)[0]]; bl = {}
        if rng.random() < c["p_open"]: bl["op"] = [rng.choice(c["op"]) if rng.random() < 0.7 else rng.choice(openers)]
        if rng.random() < P["ded"]:
            d = c["patron"] if rng.random() < P["patron"] else deity.draw()
            if d not in lic: lic[d] = [epi.draw() for _ in range(rng.choices([1, 2, 3, 4, 5], [105, 65, 26, 18, 27])[0])]
            b = [d] + ([d] if rng.random() < P["dbl"] else []) + ([rng.choice(lic[d])] if rng.random() < P["epi"] else []); bl["ded"] = b
        if rng.random() < P["off"]: bl["off"] = [guild.draw()] + ([C._zipf_choice(rng, ranks)] if rng.random() < P["rank"] else [])
        if rng.random() < P["led"]:
            co = comm.draw(); bl["led"] = ([C._zipf_choice(rng, tallies, 1.2)] if rng.random() < P["tally"] else []) + [co] + ([co] if rng.random() < P["cdbl"] else [])
        mid = [x for x in c["order"] if x in bl]
        for i in range(len(mid) - 1):
            if rng.random() < P["swap"]: mid[i], mid[i + 1] = mid[i + 1], mid[i]
        t = bl.get("op", []) + [s for x in mid for s in bl[x]]
        if not t or rng.random() < P["term"]: t.append(rng.choice(c["term"]) if rng.random() < 0.8 else rng.choice(terms))
        if rng.random() < P["issue"] and len(t) >= 2: t.insert(len(t) - 1, rng.choice(issue))
        texts.append(t)
    return texts


def shaped(corpus, rng, lengths):
    """Indus-shaped draw: N_TRAIN + N_TEST texts matched to lengths resampled from Indus dev; shuffled; split."""
    target = [lengths[rng.randrange(len(lengths))] for _ in range(N_TRAIN + N_TEST)]
    X = M.matched_sample(corpus, target, rng); rng.shuffle(X)
    return X[:N_TRAIN], X[N_TRAIN:]


def job(args):
    name, k, seed = args
    rng = random.Random(seed)
    lengths = [len(t) for t in C.indus("dev")]
    src = {"ur3": C.ur3, "linb": C.linb, "slot": C.slot, "heraldry": C.heraldry, "khipu": C.khipu}
    if name == "sigil_stock": corpus = sigil_param(1000 + k)
    elif name == "sigil_jitter": corpus = sigil_param(2000 + k, jitter=True)
    else: corpus = JOB_CACHE.setdefault(name, src[name]())
    tr, te = shaped(corpus, rng, lengths)
    t0 = time.time(); r = gof(tr, te, seed); r["sec"] = round(time.time() - t0, 1)
    return dict(name=name, k=k, seed=seed, **{x: r[x] for x in ("reject", "eps", "p", "obs", "syn_mean", "sec")}, roles=dict(r["roles"]))


JOB_CACHE = {}
PLAN = [("ur3", 50), ("linb", 50), ("sigil_stock", 50), ("sigil_jitter", 50), ("slot", 20), ("heraldry", 10), ("khipu", 10)]


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "time"
    if mode == "time":
        assert sigil_param(3) == C.sigil(n=3000, seed=3)
        print(job(("sigil_stock", 0, SEED)))
    elif mode == "kill":
        from multiprocessing import Pool
        W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        jobs = [(n, k, SEED + 1000 * i + k) for i, (n, K) in enumerate(PLAN) for k in range(K)]
        out = []
        with Pool(W) as pool:
            for r in pool.imap_unordered(job, jobs):
                out.append(r); print(r["name"], r["k"], r["reject"], round(r["eps"], 3), r["sec"], flush=True)
                json.dump(out, open(HERE / "kill_draws.json", "w"), indent=0)
        rate = {n: sum(r["reject"] for r in out if r["name"] == n) for n, _ in PLAN}
        planted = rate["sigil_stock"] + rate["sigil_jitter"]
        passed = rate["ur3"] >= 40 and rate["linb"] >= 40 and planted <= 5 and rate["slot"] <= 2
        res = dict(rejects=rate, n=dict(PLAN), planted_rejects=planted, passed=bool(passed),
                   gate="ur3 >= 40/50 and linb >= 40/50 rejected; planted SIGIL <= 5/100 and slot <= 2/20 rejected")
        json.dump(res, open(HERE / "kill.json", "w"), indent=1); print(res)
    elif mode == "indus":
        k = json.load(open(HERE / "kill.json"))
        assert k["passed"], "kill test failed: the Indus test is not run"
        dev, ho = C.indus("dev"), C.indus("heldout")
        res = {}
        for j, s in enumerate([SEED, SEED + 1, SEED + 2, SEED + 3, SEED + 4]):
            r = gof(dev, ho, s); r["roles"] = dict(r["roles"]); res["primary" if j == 0 else f"seed{j}"] = r
            print(j, r["reject"], r["eps"], r["p"], flush=True)
        json.dump(res, open(HERE / "indus.json", "w"), indent=1)
