"""Formula dial on Linear B (prereg docs/prereg/lb_formula_dial.md, sealed v4).
Run (from the repo root, under the Indus compute lock and memory guard):
  nice -n 20 .venv/bin/python -I experiments/lb_formula_dial/run.py kill   # targets, G0, feasibility, K1, K2 -> kill.json
  nice -n 20 .venv/bin/python -I experiments/lb_formula_dial/run.py full   # all cells (refuses unless kill.json passed) -> full.json
Workers: env NWORK (default 4).

Order inside `kill`: label-free part first (e_M, F0 excess, G0, tilt and D1 builds, 1.18 and 2.0 keys, feasibility
gate), then K1 (F0 x 1.0, must reproduce sealed lb_shape_ladder R1 to 1e-9), then K2 (D1 guard). `full` rebuilds the
label-free part (deterministic, checked against kill.json), runs every reachable cell and applies the frozen readings.
Output JSON holds aggregates only.
"""
import hashlib, importlib.util, json, math, os, random, sys, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
# As in experiments/lb_shape_ladder/coverage.py: the ladder's run.py does `import run as base` (lb_certify); put
# lb_certify on the path and load the ladder under its own name so the two sealed run.py files do not clash.
sys.path.insert(0, str(ROOT / "experiments/lb_certify"))
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("ladder", ROOT / "experiments/lb_shape_ladder/run.py")
L = importlib.util.module_from_spec(_spec); sys.modules["ladder"] = L; _spec.loader.exec_module(L)
B = L.base                                            # sealed lb_certify module
from corpus.load import m77_texts, distinct, runs    # noqa: E402

NWORK = int(os.environ.get("NWORK", "4"))
NSUB, NPERM, LMIN, MAXW = L.NSUB, L.NPERM, L.LMIN, L.MAXW
R1_INDEX = list(L.RUNGS).index("R1")                  # N1 seed of sealed R1: SEED + 1000 k + 7 * 1
TOPN, NBASE, TOL = 50, 20, 0.005
F2_MULT, D1_SHARE = 1.5, 0.05
TAU_LO, TAU_HI, TAU_CAP = 0.0, 8.0, 30
LOOSE_LO, LOOSE_HI = 0.16, 0.18
MAX_FAIL = 2                                          # feasibility: more than 2 of 20 failed draws drops a rung
S_RECHUNK, S_TILT, S_LOOSE, S_BASE = 20261126, 20261127, 20261128, 20261129
FRUNG_IDX = {"F1": 1, "F2": 2, "D1": 3}
LRUNGS = ("1.0", "1.18", "2.0"); LRUNG_IDX = {"1.18": 1, "2.0": 2}
FRUNGS = ("F0", "F1", "F2", "D1")
PRIMARY = (("F1", "1.0"), ("F0", "1.18"), ("F1", "1.18"))


# ------------------------------------------------------------------ formula measure (label-free)
def _flat(units, idx):
    toks, valid = [], []
    for u in units:
        toks += [idx[s] for s in u]
        valid += [True] * (len(u) - 1) + [False] if u else []
    return np.array(toks, dtype=np.int64), np.array(valid[:-1] if valid else [], dtype=bool)


def top_share(toks, valid, V):
    if len(toks) < 2 or not valid.any():
        return 0.0
    codes = toks[:-1][valid] * V + toks[1:][valid]
    cnt = np.bincount(codes)
    return float(np.sort(cnt)[-TOPN:].sum() / codes.size)


def excess(units, seed):
    """Top-50 pair share minus its mean over NBASE unigram shuffles (tokens permuted across positions, unit lengths
    kept). Pairs never cross a unit (chunk, or M77 run between breaks). Fresh rng per call, so the value is a
    deterministic function of the units."""
    idx = {}
    for u in units:
        for s in u:
            idx.setdefault(s, len(idx))
    V = max(len(idx), 1); toks, valid = _flat(units, idx)
    share = top_share(toks, valid, V)
    rng = np.random.default_rng(seed)
    base = float(np.mean([top_share(rng.permutation(toks), valid, V) for _ in range(NBASE)]))
    return share - base, share


def m77_target(n_bar):
    """e_M: median excess over 20 random draws of distinct M77 seal/sealing texts, each cut to n_bar tokens."""
    recs = distinct([r for r in m77_texts() if r["object_type"] in ("seal", "sealing")])
    texts = [rs for rs in (runs(r["seq"]) for r in recs) if rs]
    rng = np.random.default_rng(S_BASE); ex, sh = [], []
    for _ in range(20):
        order = rng.permutation(len(texts)); units, n = [], 0
        for i in order:
            for run_ in texts[i]:
                take = run_[:n_bar - n]
                if take:
                    units.append(take); n += len(take)
            if n >= n_bar:
                break
        e, s = excess(units, int(rng.integers(2 ** 62)))
        ex.append(e); sh.append(s)
    return dict(e_M=float(np.median(ex)), draws_excess=[float(x) for x in ex], draws_share=[float(x) for x in sh],
                n_bar=n_bar, n_texts_pool=len(texts), types=len({s for t in texts for r in t for s in r}))


# ------------------------------------------------------------------ Linear B draws (label-free)
def f0_draw(k):
    """Sealed lb_shape_ladder build(k, 'chunk'), re-traced to also return the dev line ids (checked equal)."""
    rng_np = np.random.default_rng(L.SEED + 1000 * k); rng = random.Random(L.SEED + 1000 * k)
    lines = L.lb_lines(); lens = B.m77_lengths()
    flat = [(tid, [s for w in ws for s in w]) for tid, ws in lines]
    ch = B.chunk(flat, lens, rng_np)
    pick = rng_np.choice(len(ch), size=min(2300, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    items = [(tid, [t]) for tid, t in ch]
    ids = sorted({tid for tid, _ in items}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    dev = [t for tid, t in items if tid in dev_ids]; ho = [t for tid, t in items if tid not in dev_ids]
    sd, sh, _ = L.build(k, "chunk")
    assert sd == dev and sh == ho, "re-traced build differs from sealed lb_shape_ladder build"
    return dev, ho, dev_ids, lines, lens


def tilt_pool(k, dev_ids, lines, lens):
    flat = [(tid, [s for w in ws for s in w]) for tid, ws in lines if tid not in dev_ids]
    ch = B.chunk(flat, lens, np.random.default_rng(S_RECHUNK + 1000 * k))
    units = [t for _, t in ch]
    pc = Counter((a, b) for u in units for a, b in zip(u, u[1:]))
    top = {p for p, _ in pc.most_common(TOPN)}
    f = np.array([sum((a, b) in top for a, b in zip(u, u[1:])) / (len(u) - 1) for u in units])
    return units, f


def tilt_draw(k, rung, target, ho_units, pool, f):
    """Length-stratified weighted draw without replacement; frozen tau bisection that sees only the excess."""
    need = Counter(len(u) for u in ho_units)
    plen = np.array([len(u) for u in pool])
    strata = {Lh: np.flatnonzero(plen == Lh) for Lh in need}
    short = {int(Lh): (int(m), int(len(strata[Lh]))) for Lh, m in need.items() if len(strata[Lh]) < m}
    rec = dict(k=k, rung=rung, target=target, pool_tokens=int(plen.sum()), pool_chunks=len(pool))
    if short:
        return None, dict(rec, ok=False, why="stratum too small", short=short)
    u = np.random.default_rng(S_TILT + 1000 * k + FRUNG_IDX[rung]).random(len(pool))
    elog = -np.log(u)
    seed = S_BASE + k

    def draw(tau):
        r = elog / np.exp(tau * f); pick = []
        for Lh, m in need.items():
            ii = strata[Lh]; pick += list(ii[np.argsort(r[ii], kind="stable")[:m]])
        pick.sort()
        units = [pool[i] for i in pick]
        return units, excess(units, seed)

    _, (e_hi, _) = draw(TAU_HI)
    lo, hi, it, hit = TAU_LO, TAU_HI, 0, None
    while it < TAU_CAP:
        it += 1; tau = (lo + hi) / 2
        units, (e, sh) = draw(tau)
        if abs(e - target) <= TOL:
            hit = (tau, units, e, sh); break
        if e < target:
            lo = tau
        else:
            hi = tau
    rec.update(excess_at_tau_max=e_hi, iterations=it)
    if hit is None or e_hi < target - TOL:
        why = "excess at tau=8 below target" if e_hi < target - TOL else "no stop within cap"
        return None, dict(rec, ok=False, why=why, last_tau=tau, last_excess=e)
    tau, units, e, sh = hit
    return units, dict(rec, ok=True, tau=tau, excess=e, share=sh, **describe(units))


def d1_draw(k, target, ho_units, n_k):
    rng = random.Random(S_TILT + 1000 * k + FRUNG_IDX["D1"])
    dist = sorted({tuple(u) for u in ho_units})
    nf = int(round(D1_SHARE * len(dist)))
    formula = [list(t) for t in rng.sample(dist, nf)]
    units = [list(u) for u in ho_units]; seed = S_BASE + k
    e, sh = excess(units, seed); copies = 0
    rec = dict(k=k, rung="D1", target=target, n_distinct_f0=len(dist), n_formula=nf)
    while e < target - TOL:
        if sum(map(len, units)) > 2 * n_k:
            break
        units.append(list(formula[copies % nf])); copies += 1
        e, sh = excess(units, seed)
    tok = sum(map(len, units))
    ok = abs(e - target) <= TOL and tok <= 2 * n_k
    why = None if ok else ("needs more than 2 n_k tokens" if tok > 2 * n_k else "overshot tolerance")
    return (units if ok else None), dict(rec, ok=ok, why=why, copies=copies, excess=e, share=sh,
                                        token_growth=tok / n_k, **describe(units))


def describe(units):
    return dict(tokens=int(sum(map(len, units))), chunks=len(units), distinct_chunks=len({tuple(u) for u in units}),
                length_dist={int(a): int(b) for a, b in sorted(Counter(map(len, units)).items())})


# ------------------------------------------------------------------ loose keys (label-free; no IC)
def loose_key(k, rung, dev, ho):
    """Built once on F0 of draw k over F0's key universe (dev + held-out signs). sign -> tuple of alternatives."""
    freq = Counter(s for t in dev + ho for w in t for s in w)
    hof = Counter(s for t in ho for w in t for s in w); hot = sum(hof.values())
    U = sorted(freq); true = {s: tuple(B.true_value(s)) for s in U}
    by = defaultdict(list)
    for s in U:
        by[len(true[s])].append(s)
    donors = {s: [d for d in by[len(true[s])] if d != s and true[d] != true[s]] for s in U}
    elig = [s for s in U if donors[s]]
    rng = random.Random(S_LOOSE + 1000 * k + LRUNG_IDX[rung])
    key = {s: (true[s],) for s in U}; loose, share = [], 0.0
    if rung == "2.0":
        for s in elig:
            loose.append(s)
    else:
        order = elig[:]; rng.shuffle(order); n = 0
        for s in order:
            if (n + hof[s]) / hot > LOOSE_HI:
                continue
            loose.append(s); n += hof[s]
            if n / hot >= LOOSE_LO:
                break
    for s in loose:
        key[s] = (true[s], true[rng.choice(donors[s])])
    share = sum(hof[s] for s in loose) / hot
    hs = [s for s in U if hof[s]]
    info = dict(k=k, rung=rung, n_universe=len(U), n_eligible=len(elig), n_no_donor=len(U) - len(elig),
                n_loose=len(loose), loose_token_share_ho=share,
                values_per_sign=float(np.mean([len(key[s]) for s in U])),
                values_per_sign_ho_types=float(np.mean([len(key[s]) for s in hs])),
                ok=bool(rung == "2.0" or share >= LOOSE_LO))
    return key, info


# ------------------------------------------------------------------ lattice scorer for keys with alternatives
class LatticeIC:
    """Token IC with alternatives: max covered consonants jointly over segmentation and each token's alternative,
    by a dynamic programme over (consonant position, alternative of the token cut at that position). All
    alternatives of a sign have one length here, so the consonant total is fixed and the tie rule (fewer
    consonants) never binds. Segments are as in the sealed IC at full coverage: one per word; vowel signs are
    transparent. Cached per segment on the tuple of alternative-set ids."""

    def __init__(self, texts, lex, pre):
        self.lex, self.pre = lex, pre
        self.segs = [tuple(w) for t in texts for w in t if w]
        self.cache, self.aid, self.sets = {}, {}, []

    def _id(self, alts):
        i = self.aid.get(alts)
        if i is None:
            i = self.aid[alts] = len(self.sets); self.sets.append(alts)
        return i

    def full(self, key):
        kid = {}
        for s, v in key.items():
            alts = tuple(tuple(a) for a in v)
            assert len({len(a) for a in alts}) == 1
            kid[s] = self._id(alts) if alts[0] else None
        cov = tot = 0
        for sg in self.segs:
            ids = tuple(kid[s] for s in sg if kid[s] is not None)
            if not ids:
                continue
            r = self.cache.get(ids)
            if r is None:
                r = self.cache[ids] = lattice([self.sets[i] for i in ids], self.lex, self.pre)
            cov += r[0]; tot += r[1]
        return cov / tot if tot else 0.0


def lattice(tokens, lex, pre):
    tp, op = [], []
    for t, alts in enumerate(tokens):
        for o in range(len(alts[0])):
            tp.append(t); op.append(o)
    n = len(tp)
    f = [dict() for _ in range(n + 1)]; f[0][-1] = 0

    def put(j, st, v):
        if v > f[j].get(st, -1):
            f[j][st] = v

    def state(j, a):
        return a if j < n and op[j] > 0 else -1

    for i in range(n):
        for st, v in f[i].items():
            choices = (st,) if op[i] > 0 else range(len(tokens[tp[i]]))
            for a in choices:
                put(i + 1, state(i + 1, a), v)                       # consonant i left uncovered
            stack = [(i, a, ()) for a in choices]
            while stack:                                             # lexicon words starting at i
                p, a, pref = stack.pop()
                pref = pref + (tokens[tp[p]][a][op[p]],)
                if pref not in pre:
                    continue
                q = p + 1; Lw = len(pref)
                if Lw >= LMIN and pref in lex:
                    put(q, state(q, a), v + Lw)
                if Lw < MAXW and q < n:
                    for b in ((a,) if op[q] > 0 else range(len(tokens[tp[q]]))):
                        stack.append((q, b, pref))
    return (max(f[n].values()), n)


# ------------------------------------------------------------------ one scored cell-draw
LEX = PRE = None


def init():
    global LEX, PRE
    L.init(); LEX = L.LEX
    PRE = {t[:i] for t in LEX for i in range(1, len(t) + 1)}


def keys_hash(h, key, kept):
    h.update(repr([key[s] for s in kept]).encode())


def cell_job(args):
    """N1 seed and kept-sign order as sealed R1 (shared by every cell of draw k). freq = bin frequencies."""
    k, frung, lrung, ho, freq, lkey = args
    t0 = time.time()
    rng = random.Random(L.SEED + 1000 * k + 7 * R1_INDEX)
    order = sorted(freq); rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= 1.0:
            break
        kept.append(s); c += freq[s]
    true = {s: B.true_value(s) for s in kept}
    cl = L.classes(kept, true)
    if lrung == "1.0":
        key = true; mk = lambda texts: L.IC(texts, LEX)
    else:
        key = {s: lkey.get(s, (tuple(true[s]),)) for s in kept}; mk = lambda texts: LatticeIC(texts, LEX, PRE)
    shape = L.IC(ho, LEX).shape(true)
    H = mk(ho); t_ho = H.full(key)
    h = hashlib.sha256(); n1 = []
    for _ in range(NPERM):
        pk = L.permute_in_class_bins(key, cl, freq, rng); keys_hash(h, pk, kept); n1.append(H.full(pk))
    n1 = np.array(n1)
    Hs = mk(L.unigram(ho, rng)); t_sh = Hs.full(key)
    n1s = np.array([Hs.full(L.permute_in_class_bins(key, cl, freq, rng)) for _ in range(NPERM)])
    p99, p99s = float(np.quantile(n1, .99)), float(np.quantile(n1s, .99))
    ho_tok = sum(len(w) for t in ho for w in t)
    loose_tok = sum(1 for t in ho for w in t for s in w if len(key[s]) > 1) / ho_tok
    return dict(k=k, frung=frung, lrung=lrung, tokens_ho=ho_tok, n_keyed=len(kept), shape=shape,
                loose_token_share=loose_tok, true_ic=t_ho, n1_mean=float(n1.mean()), n1_p99=p99,
                W=p99 - float(n1.mean()), signal=t_ho - float(n1.mean()), margin=t_ho - p99, refute=bool(t_ho > p99),
                shuffled_true=t_sh, shuffled_n1_mean=float(n1s.mean()), shuffled_n1_p99=p99s,
                shuffled_refute=bool(t_sh > p99s), n1_keys_sha256=h.hexdigest(), seconds=round(time.time() - t0, 1))


# ------------------------------------------------------------------ label-free part
def labelfree():
    t0 = time.time()
    draws = {}
    for k in range(1, NSUB + 1):
        dev, ho, dev_ids, lines, lens = f0_draw(k)
        draws[k] = dict(dev=dev, ho=ho, dev_ids=dev_ids, n_k=sum(len(w) for t in ho for w in t))
    n_bar = int(round(float(np.median([d["n_k"] for d in draws.values()]))))
    tgt = m77_target(n_bar); e_M = tgt["e_M"]
    targets = dict(F1=e_M, F2=F2_MULT * e_M)
    f0_ex = {}
    for k, d in draws.items():
        e, sh = excess([t[0] for t in d["ho"]], S_BASE + k)
        f0_ex[k] = dict(k=k, excess=e, share=sh, **describe([t[0] for t in d["ho"]]))
    f0_med = float(np.median([x["excess"] for x in f0_ex.values()]))
    g0 = bool(f0_med >= e_M - TOL)
    rec = {"F0": list(f0_ex.values()), "F1": [], "F2": [], "D1": []}
    corp = {("F0", k): d["ho"] for k, d in draws.items()}
    for k, d in draws.items():
        units0 = [t[0] for t in d["ho"]]
        pool, f = tilt_pool(k, d["dev_ids"], lines, lens)
        for rung in ("F1", "F2"):
            if rung == "F1" and g0:
                continue
            units, r = tilt_draw(k, rung, targets[rung], units0, pool, f)
            rec[rung].append(r)
            if units is not None:
                corp[(rung, k)] = [[u] for u in units]
        units, r = d1_draw(k, targets["F2"], units0, d["n_k"])
        rec["D1"].append(r)
        if units is not None:
            corp[("D1", k)] = [[u] for u in units]
    if g0:
        for k in draws:
            corp[("F1", k)] = corp[("F0", k)]
    gate = {}
    for rung in ("F1", "F2", "D1"):
        if rung == "F1" and g0:
            gate[rung] = dict(reachable=True, failed=0, note="G0 applied: F1 = F0")
            continue
        nf = sum(not r["ok"] for r in rec[rung])
        gate[rung] = dict(reachable=nf <= MAX_FAIL, failed=nf)
    lkeys, linfo = {}, {"1.18": [], "2.0": []}
    for k, d in draws.items():
        for lr in ("1.18", "2.0"):
            key, info = loose_key(k, lr, d["dev"], d["ho"]); lkeys[(lr, k)] = key; linfo[lr].append(info)
    for lr in ("1.18", "2.0"):
        nf = sum(not i["ok"] for i in linfo[lr]); gate[lr] = dict(reachable=nf <= MAX_FAIL, failed=nf)
    stop = (not g0) and not gate["F1"]["reachable"]
    summary = dict(n_k=[d["n_k"] for d in draws.values()], m77=tgt, targets=targets, tol=TOL,
                   f0_median_excess=f0_med, G0_applied=g0, gate=gate, study_stopped_F1_unreachable=stop,
                   rungs=rec, loose=linfo, seconds=round(time.time() - t0, 1))
    return summary, draws, corp, lkeys


def cell_args(frung, lrung, k, draws, corp, lkeys):
    d = draws[k]
    ho = corp[(frung, k)]
    base_ho = corp[("F0", k)] if frung == "D1" else ho          # D1: bins frozen at F0's
    freq = Counter(s for t in d["dev"] + base_ho for w in t for s in w)
    return (k, frung, lrung, ho, freq, lkeys.get((lrung, k)))


def run_jobs(jobs):
    with Pool(NWORK, initializer=init) as P:
        return P.map(cell_job, jobs, chunksize=1)


def summarise(rows, n_total=NSUB):
    """P counts passes out of 20; draws not scored (failed build or key) count as non-passes."""
    if not rows:
        return None
    P = sum(r["refute"] for r in rows); C = sum(r["shuffled_refute"] for r in rows)
    return dict(scored=len(rows), P=P, scrambled_passes=C, interpretable=C <= 1, cell_pass=bool(P >= 16 and C <= 1),
                median_W=float(np.median([r["W"] for r in rows])),
                median_signal=float(np.median([r["signal"] for r in rows])),
                median_margin=float(np.median([r["margin"] for r in rows])),
                mean_true_ic=float(np.mean([r["true_ic"] for r in rows])),
                mean_cons_per_seg=float(np.mean([r["shape"]["cons_per_seg"] for r in rows])),
                mean_loose_token_share=float(np.mean([r["loose_token_share"] for r in rows])))


def strip(s):
    return {k: v for k, v in s.items() if k != "seconds"}


# ------------------------------------------------------------------ modes
def kill():
    summ, draws, corp, lkeys = labelfree()
    print(json.dumps({k: v for k, v in summ.items() if k not in ("rungs", "loose", "m77")}, indent=1), flush=True)
    out = dict(labelfree=summ)
    if summ["study_stopped_F1_unreachable"]:
        out.update(kill_passed=False, stop="F1 unreachable and G0 did not apply: study stops before the kill tests")
        json.dump(out, open(HERE / "kill.json", "w"), indent=1); print(out["stop"]); return
    sealed = {r["k"]: r for r in json.load(open(ROOT / "experiments/lb_shape_ladder/full.json"))["runs"]
              if r["rung"] == "R1"}
    k1 = run_jobs([cell_args("F0", "1.0", k, draws, corp, lkeys) for k in range(1, NSUB + 1)])
    match = []
    for r in k1:
        s = sealed[r["k"]]
        d = {q: abs(r[q] - s[q]) for q in ("true_ic", "n1_mean", "n1_p99", "shuffled_true", "shuffled_n1_p99")}
        match.append(dict(k=r["k"], max_abs_diff_required=max(d["true_ic"], d["n1_mean"], d["n1_p99"]),
                          max_abs_diff_shuffled=max(d["shuffled_true"], d["shuffled_n1_p99"]),
                          tokens_equal=r["tokens_ho"] == s["tokens_ho"]))
    P = sum(r["refute"] for r in k1); C = sum(r["shuffled_refute"] for r in k1)
    eq = all(m["max_abs_diff_required"] <= 1e-9 for m in match)
    K1 = dict(P=P, scrambled_passes=C, match_1e9=eq, passed=bool(P >= 16 and C <= 1 and eq), per_draw=match,
              cell=summarise(k1), runs=k1)
    out.update(K1=K1, kill_passed=K1["passed"])
    print(json.dumps({q: K1[q] for q in ("P", "scrambled_passes", "match_1e9", "passed")}), flush=True)
    if not K1["passed"]:
        out["stop"] = "K1 failed: STOP, no other cell is run"
        json.dump(out, open(HERE / "kill.json", "w"), indent=1); print(out["stop"]); return
    if summ["gate"]["D1"]["reachable"]:
        ks = [k for k in range(1, NSUB + 1) if ("D1", k) in corp]
        d1 = run_jobs([cell_args("D1", "1.0", k, draws, corp, lkeys) for k in ks])
        h0 = {r["k"]: r["n1_keys_sha256"] for r in k1}
        same = all(r["n1_keys_sha256"] == h0[r["k"]] for r in d1)
        assert same, "D1 N1 keys differ from F0's (bins must be frozen at F0)"
        wF0 = K1["cell"]["median_W"]; wD1 = float(np.median([r["W"] for r in d1]))
        K2 = dict(median_W_F0=wF0, median_W_D1=wD1, ratio=wD1 / wF0, keys_identical=same,
                  passed=bool(wD1 >= 1.25 * wF0), cell=summarise(d1), runs=d1)
    else:
        K2 = dict(passed=False, note="D1 unreachable at the feasibility gate; D1 removed from every reading")
    out["K2"] = K2
    print(json.dumps({q: K2.get(q) for q in ("median_W_F0", "median_W_D1", "ratio", "passed")}), flush=True)
    json.dump(out, open(HERE / "kill.json", "w"), indent=1)


def full():
    kp = HERE / "kill.json"
    assert kp.exists(), "kill.json missing: run `kill` first"
    kr = json.load(open(kp))
    assert kr.get("kill_passed") is True, "kill test did not pass: full run refused"
    summ, draws, corp, lkeys = labelfree()
    a, b = json.loads(json.dumps(strip(summ))), strip(kr["labelfree"])
    assert a == b, "label-free rebuild differs from kill.json"
    gate, g0 = summ["gate"], summ["G0_applied"]
    d1_ok = gate["D1"]["reachable"] and kr["K2"]["passed"]
    fr_live = [f for f in FRUNGS if f == "F0" or gate[f]["reachable"]]
    lr_live = [lr for lr in LRUNGS if lr == "1.0" or gate[lr]["reachable"]]
    jobs = []
    for fr in fr_live:
        if fr == "F1" and g0:
            continue                                                   # F1 = F0, cells copied below
        for lr in lr_live:
            for k in range(1, NSUB + 1):
                if (fr, k) not in corp:
                    continue                                           # failed draw: non-pass
                if lr != "1.0" and not next(i for i in summ["loose"][lr] if i["k"] == k)["ok"]:
                    continue                                           # 1.18 draw below 16%: non-pass
                jobs.append(cell_args(fr, lr, k, draws, corp, lkeys))
    res = run_jobs(jobs)
    by = defaultdict(list)
    for r in res:
        by[(r["frung"], r["lrung"])].append(r)
    if g0:
        for lr in lr_live:
            by[("F1", lr)] = [dict(r, frung="F1") for r in by[("F0", lr)]]
    for fr, kname in (("F0", "K1"), ("D1", "K2")):                     # determinism check against kill.json
        if kname in kr and "runs" in kr[kname]:
            old = {r["k"]: r for r in kr[kname]["runs"]}
            for r in by[(fr, "1.0")]:
                assert abs(r["true_ic"] - old[r["k"]]["true_ic"]) <= 1e-12 and \
                    r["n1_keys_sha256"] == old[r["k"]]["n1_keys_sha256"], f"{fr} x 1.0 differs from kill.json"
    for lr in lr_live:                                                 # D1 keys identical to F0's, every rung
        h0 = {r["k"]: r["n1_keys_sha256"] for r in by[("F0", lr)]}
        assert all(r["n1_keys_sha256"] == h0[r["k"]] for r in by[("D1", lr)])
    cells = {f"{fr} x {lr}": summarise(by[(fr, lr)]) for fr in FRUNGS for lr in LRUNGS if by.get((fr, lr))}
    out = dict(labelfree=summ, cells=cells, D1_in_readings=d1_ok, readings=readings(cells, summ, d1_ok),
               runs=res)
    print(json.dumps(dict(cells={c: {q: v[q] for q in ("P", "scrambled_passes", "cell_pass", "median_W")}
                                 for c, v in cells.items()}, readings=out["readings"]), indent=1))
    json.dump(out, open(HERE / "full.json", "w"), indent=1)


def readings(cells, summ, d1_ok):
    def cp(name):
        c = cells.get(name)
        return None if c is None else c["cell_pass"]
    g0 = summ["G0_applied"]
    f1, f0l, f1l = cp("F1 x 1.0"), cp("F0 x 1.18"), cp("F1 x 1.18")
    w0 = cells["F0 x 1.0"]["median_W"]
    r = 1.0 if g0 else (cells["F1 x 1.0"]["median_W"] / w0 if cells.get("F1 x 1.0") else None)
    R = dict(r=r, primary={n: cp(n) for n in ("F1 x 1.0", "F0 x 1.18", "F1 x 1.18")})
    R["already_at_indus_excess"] = g0
    if f1 is not None and r is not None:
        R["formula_reuse_explains"] = bool(not f1 and r >= 1.5)
        R["formula_reuse_supporting_D1"] = bool(d1_ok and cells.get("D1 x 1.0") and not cp("D1 x 1.0"))
        R["tilt_lowers_power_not_width"] = bool(not f1 and r < 1.5)
        R["formula_widens_null_power_holds"] = bool(r >= 1.5 and f1)
        if not f1 and r < 1.5:
            R["signal_F0_F1"] = (cells["F0 x 1.0"]["median_signal"], cells["F1 x 1.0"]["median_signal"])
    R["looseness_explains_scott_shape"] = None if f0l is None else bool(not f0l)
    R["both_needed"] = None if None in (f1, f0l, f1l) else bool(f1 and f0l and not f1l)
    R["neither"] = None if None in (f1, f0l, f1l) else bool(f1 and f0l and f1l)
    R["F2_dropped"] = not summ["gate"]["F2"]["reachable"]
    R["stress_limits"] = {n: cells[n]["P"] for n in cells if n.startswith("F2") or n.endswith("2.0")}
    R["not_interpretable"] = [n for n, c in cells.items() if not c["interpretable"]]
    return R


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "kill":
        kill()
    elif mode == "full":
        full()
    else:
        sys.exit("usage: run.py kill|full")
