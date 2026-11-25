"""Lift certify on Linear B (prereg docs/prereg/lift_certify.md, SEALED v3).
Run (from the repo root, under the Indus compute lock; A4 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/lift_certify/run.py kill   # A1, A2/F4, F3, K0, F1, K1/F2, K2, K3 -> kill.json
  board/run.sh .venv/bin/python -I experiments/lift_certify/run.py full   # K4 (refuses unless K1, K2, K3 all passed) -> full.json
Workers: env NWORK (default 4, capped at 4).

Order inside `kill` (the prereg's order, strongest first): A4 guard; A1 (study path reproduces sealed lb_shape_ladder
R1 true IC and N1 mean, draws 1-3, to 1e-9); A2 + F4 (label-free gate counts, draws 1-20; no trigram, no key score);
F3 (trigram-only Hit@1 on the K0 plant, before any K0 lift); K0 (draws 1-5); F1 (grid edge, decided at K0, K0 not
regraded); K1 (bisection on IC only, then lift; F2); K2; K3. A K0 fail stops. A K1 fail makes K2 and K3 run once,
record-only. With K1 passed, a K2 fail stops before K3 is run. `full` runs K4 (9 sealed N2 keys, 3 N3 keys per draw).
Each mode refuses to overwrite its own output. Output JSON holds per-draw summaries only (no per-position arrays).

Reuse (imported by path, not copied): sealed lb_shape_ladder (build, lb_lines, IC, ic_seg, markov, unigram, classes,
permute_in_class_bins, shuffle_in_class, fit, seeds), sealed lb_certify (chunk, m77_lengths, Homer lexicon,
true_value), corpus.build._close (near-copy rule). The bench_restoration trigram is a top-level script (it loads the
Zenodo deposit at import), so its p_uni / p_bi / p_tri / ours_scores logic is reproduced line for line in Trigram.

No Indus step: M77 enters only as text lengths through the sealed `build` (lb_certify.m77_lengths). splits_v2 and
claim-bench key files are never loaded; no M77 sign is masked, restored or read.
"""
import importlib.util, json, os, random, re, statistics, subprocess, sys, time, zlib
from collections import Counter, defaultdict
from fractions import Fraction
from math import log
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
# As lb_formula_dial / ur3_legend_refute: lb_certify on the path (the ladder does `import run as base`) and the
# sealed ladder loaded under its own name so the sealed run.py files do not clash.
sys.path.insert(0, str(ROOT / "experiments/lb_certify"))
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("ladder", ROOT / "experiments/lb_shape_ladder/run.py")
L = importlib.util.module_from_spec(_spec); sys.modules["ladder"] = L; _spec.loader.exec_module(L)
B = L.base                                            # sealed lb_certify module
from corpus.build import _close                       # noqa: E402  (near-copy rule; nothing else used)
assert L.LMIN == 4 and L.MAXW == 7, "sealed ladder constants changed"
LMIN = L.LMIN

NWORK = max(1, min(4, int(os.environ.get("NWORK", "4"))))
BASE = 20261201                                       # study base
NDRAW, NK0 = 20, 5
R1_INDEX = list(L.RUNGS).index("R1")                  # sealed R1 N1 seed: SEED + 1000 k + 7 * 1
GRID0 = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
GRID_F1 = (8.0, 16.0)
NFOLD = 5
N1_KEYS = 20
SUBLEX, SUBLEX_F3 = 500, 2000
PLANT_LMIN, PLANT_LMAX = 4, 7
IC_TOL, BISECT_STEPS = 0.01, 20
N3_RESTARTS, N3_SWAPS, N3_SAMPLE, N3_LAMBDA = 3, 500, 300, 1.0
A1_TOL = 1e-9
GATE_CLEAN, GATE_REACH_SHARE, GATE_TOL = 1376, 0.49, 0.05
F4_MIN = 900
F3_MAX = 60
SEALED_R1 = ROOT / "experiments/lb_shape_ladder/full.json"
LOCK = ROOT / "board/compute.lock"
MEM_GUARD = 0.20

# ------------------------------------------------------------------ frozen readings (verbatim)
R_K0_FAIL = "The pipeline cannot restore signs from a lexicon even on text made of lexicon words."
R_K1_FAIL = ("Unpowered. At the true key's own dictionary coverage (IC 0.20 against 0.15 by chance), a planted language "
             "does not lift restoration by 3 points at Indus shape. With this score (trigram plus λ × covered "
             "consonants, Hit@1, 3-point bar), restoration lift is unpowered at this shape and lexicon density. The "
             "route is closed at the brief's bar, not for every possible statistic.")
R_K1_K3_NOTE = "plant harsher than real text; K1 invalid as a power test"
R_K2_FAIL = "The lift is not specific to the key or to the text."
R_K3_FAIL = ("The true Linear B key with a Homeric lexicon does not lift restoration by 3 points, though a planted "
             "language at the same coverage does. The cause is not isolated: the plant differs from real text in "
             "lexicon match, dose layout and sign order.")
R_K4_FAIL = "Lift exists but keys fitted to noise show it too. No certify by prediction."
R_ALL_PASS = ("On Linear B at Indus shape, held-out restoration lift separates the true key from keys fitted to noise "
              "by these two fitters (3,000-swap IC; 500-swap lift). This is a certify statistic on this bench (one "
              "script, one lexicon, LMIN 4).")
R_INDUS = "It says nothing about any Indus key."


# ------------------------------------------------------------------ guard (as ur3_legend_refute)
def _ancestors():
    out, p = set(), os.getpid()
    for _ in range(64):
        out.add(p)
        try:
            q = int(subprocess.run(["ps", "-o", "ppid=", "-p", str(p)], capture_output=True, text=True).stdout.strip())
        except ValueError:
            break
        if q <= 1 or q == p:
            break
        p = q
    return out


def free_mem_frac():
    # PREREG-AMBIGUITY: "free memory" read as available memory, as ur3_legend_refute: macOS vm_stat free + inactive +
    # speculative pages over hw.memsize; elsewhere MemAvailable / MemTotal.
    if sys.platform == "darwin":
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        page = int(re.search(r"page size of (\d+)", out).group(1))
        g = lambda name: int(re.search(rf"{name}:\s+(\d+)", out).group(1))
        avail = (g("Pages free") + g("Pages inactive") + g("Pages speculative")) * page
        total = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
        return avail / total
    mi = dict(l.split(":", 1) for l in open("/proc/meminfo"))
    return int(mi["MemAvailable"].split()[0]) / int(mi["MemTotal"].split()[0])


def a4():
    """A4: the Indus compute lock (board/run.sh) is held by this process's ancestry, and free memory >= 20%."""
    why = []
    pidf = LOCK / "pid"
    if not pidf.exists():
        why.append("compute lock not held (run under board/run.sh)")
    else:
        try:
            lp = int(pidf.read_text().strip())
        except ValueError:
            lp = -1
        if lp not in _ancestors():
            why.append(f"compute lock held by pid {lp}, not by this run")
    fm = free_mem_frac()
    if fm < MEM_GUARD:
        why.append(f"free memory {fm:.1%} below the {MEM_GUARD:.0%} guard")
    return why, fm


def _conv(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, Fraction):
        return float(o)
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=_conv)


def stop(out, path, msg, code=1):
    out.update(stop=msg, k4_may_run=False)
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(code)


# ------------------------------------------------------------------ draws (sealed build, with source line ids)
def wrap(seqs):
    return [[list(s)] for s in seqs]                  # ladder text form: a chunk is one word


def unwrap(texts):
    return [tuple(s for w in t for s in w) for t in texts]


def draw(k):
    """Draw k = sealed build(k, "chunk"), replayed to keep each chunk's source line id (needed for the CRC32 folds).
    Returns the chunks in build order as (line id, signs, is_dev); checked equal to the sealed build."""
    rng_np = np.random.default_rng(L.SEED + 1000 * k); rng = random.Random(L.SEED + 1000 * k)
    lines = L.lb_lines(); lens = B.m77_lengths()
    flat = [(tid, [s for w in ws for s in w]) for tid, ws in lines]
    ch = B.chunk(flat, lens, rng_np)
    pick = rng_np.choice(len(ch), size=min(2300, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    ids = sorted({tid for tid, _ in ch}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    order = [(tid, tuple(t), tid in dev_ids) for tid, t in ch]
    dev, ho, _ = L.build(k, "chunk")
    assert unwrap(dev) == [t for _, t, d in order if d] and unwrap(ho) == [t for _, t, d in order if not d], \
        "replayed build differs from the sealed build"
    return order


def halves(order):
    """(dev seqs, dev ids, ho seqs, ho ids), each in build order. 'dev followed by ho' is dev + ho."""
    dv = [(i, t) for i, t, d in order if d]; ho = [(i, t) for i, t, d in order if not d]
    return [t for _, t in dv], [i for i, _ in dv], [t for _, t in ho], [i for i, _ in ho]


def sealed_stream(k, n2=False, lex=None):
    """Replay the sealed lb_shape_ladder one((k, "R1")) rng stream: true key, the 1000 N1 keys, and (n2=True) the 9
    sealed N2 keys (real, unigram, markov x 3 restarts). Draws a scored nothing that is not used."""
    dev, ho, _ = L.build(k, "chunk")
    rng = random.Random(L.SEED + 1000 * k + 7 * R1_INDEX)
    freq = Counter(s for t in dev + ho for w in t for s in w)
    order = sorted(freq); rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= 1.0:
            break
        kept.append(s); c += freq[s]
    true = {s: B.true_value(s) for s in kept}
    cl = L.classes(kept, true); cl_of = {s: len(true[s]) for s in kept}
    n1 = [L.permute_in_class_bins(true, cl, freq, rng) for _ in range(L.NPERM)]
    out = dict(dev=dev, ho=ho, freq=freq, kept=kept, true=true, cl=cl, cl_of=cl_of, n1=n1)
    if not n2:
        return out
    L.unigram(ho, rng)                                # control iii scramble (consumed, unused)
    for _ in range(L.NPERM):
        L.permute_in_class_bins(true, cl, freq, rng)  # control iii N1 (consumed, unused)
    for f in (0.0, 0.25, 0.5, 0.75):                  # control ii partial keys (consumed, unused)
        for _ in range(L.NPART):
            keep = set(rng.sample(kept, int(f * len(kept))))
            L.shuffle_in_class(true, [s for s in kept if s not in keep], cl_of, rng)
    corpora = (("real", dev), ("unigram", L.unigram(dev, rng)), ("markov", L.markov(dev, rng)))
    keys = []
    for name, corp in corpora:
        S = L.IC(corp, lex)
        for r in range(L.RESTARTS):
            fk = L.fit(S, L.shuffle_in_class(true, kept, cl_of, rng), kept, cl_of, L.ITERS, rng)
            keys.append((name, r, fk))
    out["n2"] = keys
    return out


def sealed_r1():
    return {r["k"]: r for r in json.load(open(SEALED_R1))["runs"] if r["rung"] == "R1"}


# ------------------------------------------------------------------ clean positions
def is_clean(t, others):
    """No text in `others` is identical to t, one edit from it, or contains / is contained in it (_close)."""
    return not any(t == u or _close(list(t), list(u)) for u in others)


def fold_of(tid):
    # PREREG-AMBIGUITY: "CRC32 of the source line id": zlib.crc32 of the decimal string of the integer line id.
    return zlib.crc32(str(tid).encode()) % NFOLD


# ------------------------------------------------------------------ trigram (bench_restoration ours_scores, line for line)
class Trigram:
    D = 0.75

    def __init__(self, train, cands):
        self.uni = Counter(s for t in train for s in t)
        self.Vn = len(set(self.uni) | set(cands))
        self.tri, self.bi_ctx, self.bi, self.uni_ctx = Counter(), Counter(), Counter(), Counter()
        self.foll2, self.foll1 = defaultdict(set), defaultdict(set)
        for s in train:
            x = ["<s>", "<s>"] + list(s) + ["</s>"]
            for i in range(2, len(x)):
                a, b, c = x[i - 2], x[i - 1], x[i]
                self.tri[(a, b, c)] += 1; self.bi_ctx[(a, b)] += 1; self.foll2[(a, b)].add(c)
                self.bi[(b, c)] += 1; self.uni_ctx[b] += 1; self.foll1[b].add(c)
        self.NU = sum(self.uni.values()) + 1
        self.memo = {}

    def p_uni(self, c):
        return (self.uni.get(c, 0) + 1) / (self.NU + self.Vn)

    def p_bi(self, b, c):
        n = self.uni_ctx.get(b, 0)
        if not n:
            return self.p_uni(c)
        return max(self.bi.get((b, c), 0) - self.D, 0) / n + self.D * len(self.foll1[b]) / n * self.p_uni(c)

    def p_tri(self, a, b, c):
        key = (a, b, c); v = self.memo.get(key)
        if v is None:
            n = self.bi_ctx.get((a, b), 0)
            if not n:
                v = self.p_bi(b, c)
            else:
                v = max(self.tri.get((a, b, c), 0) - self.D, 0) / n + self.D * len(self.foll2[(a, b)]) / n * self.p_bi(b, c)
            self.memo[key] = v
        return v

    def scores(self, s, i, cands):
        x = ["<s>", "<s>"] + list(s) + ["</s>"]
        j = i + 2
        sc = np.zeros(len(cands))
        for k, c in enumerate(cands):
            x[j] = c
            lp = 0.0
            for m in range(j, min(j + 3, len(x))):
                lp += log(self.p_tri(x[m - 2], x[m - 1], x[m]))
            sc[k] = lp
        return sc

    def tiebreak(self, cands):
        """Rank of each candidate under the tie rule: development frequency (desc), then sign name."""
        # PREREG-AMBIGUITY: "development frequency" = frequency in the text this trigram was trained on (the
        # development half for held-out scoring; the four training folds inside the λ cross-fit).
        order = sorted(range(len(cands)), key=lambda q: (-self.uni.get(cands[q], 0), cands[q]))
        tb = np.empty(len(cands), np.int32)
        for r, q in enumerate(order):
            tb[q] = r
        return tb


class Positions:
    """Masked positions of a set of clean texts, with trigram scores B (P x C) and tie ranks TB (P x C)."""

    def __init__(self, texts, tg, cands, cidx):
        self.items = [(t, i) for t in texts for i in range(len(t))]
        self.t = np.array([cidx[t[i]] for t, i in self.items], np.int64)
        self.B = np.array([tg.scores(t, i, cands) for t, i in self.items]).reshape(len(self.items), len(cands))
        tb = tg.tiebreak(cands)
        self.TB = np.tile(tb, (len(self.items), 1))

    @staticmethod
    def concat(parts, ncand):
        p = Positions.__new__(Positions)
        p.items = [x for q in parts for x in q.items]
        p.t = np.concatenate([q.t for q in parts]) if parts else np.zeros(0, np.int64)
        p.B = np.concatenate([q.B for q in parts]) if parts else np.zeros((0, ncand))
        p.TB = np.concatenate([q.TB for q in parts]) if parts else np.zeros((0, ncand), np.int32)
        return p

    def __len__(self):
        return len(self.items)


class Cell:
    """One text (dev half with line ids, held-out half) prepared for scoring: held-out clean positions under a trigram
    on the dev half, and pooled cross-fit positions over the five CRC32 folds of the dev half."""

    def __init__(self, dev, dev_ids, ho, cands, folds=True):
        self.cands = sorted(cands); self.cidx = {c: i for i, c in enumerate(self.cands)}
        tg = Trigram(dev, self.cands)
        ho4 = [t for t in ho if len(t) >= 4]
        clean = [t for t in ho4 if is_clean(t, dev)]
        self.counts = dict(ho_texts_ge4=len(ho4), ho_positions_ge4=sum(len(t) for t in ho4),
                           clean_texts=len(clean), clean_positions=sum(len(t) for t in clean))
        self.ho = Positions(clean, tg, self.cands, self.cidx)
        if not folds:
            return
        fo = [fold_of(i) for i in dev_ids]; parts = []
        for f in range(NFOLD):
            train = [t for t, g in zip(dev, fo) if g != f]
            test = [t for t, g in zip(dev, fo) if g == f and len(t) >= 4]
            test = [t for t in test if is_clean(t, train)]
            parts.append(Positions(test, Trigram(train, self.cands), self.cands, self.cidx))
        self.dv = Positions.concat(parts, len(self.cands))
        self.counts["dev_crossfit_positions"] = len(self.dv)


# ------------------------------------------------------------------ key plus lexicon
LEX = None


def init():
    global LEX
    LEX = B.build_lexicon()[0]


def cov_matrix(pos, cands, key, memo):
    """cov[p, c] = ic_seg of the chunk read with the key, candidate c in the masked place (sealed ic_seg, LMIN 4)."""
    vals = [tuple(key[c]) for c in cands]
    uniq = sorted(set(vals)); ui = np.array([uniq.index(v) for v in vals]); maxv = max(len(v) for v in uniq)
    out = np.zeros((len(pos), len(cands)), np.int64)
    for p, (t, i) in enumerate(pos.items):
        pre = tuple(x for s in t[:i] for x in key[s]); suf = tuple(x for s in t[i + 1:] for x in key[s])
        if len(pre) + len(suf) + maxv < LMIN:
            continue                                  # the chunk cannot reach 4 consonants: the key changes nothing
        row = []
        for v in uniq:
            m = (pre, v, suf); c = memo.get(m)
            if c is None:
                c = memo[m] = L.ic_seg(pre + v + suf, LEX)
            row.append(c)
        out[p] = np.array(row)[ui]
    return out


def ranks(pos, cov, lam):
    """1-based rank of the true sign under S = B + λ cov; ties broken by TB (dev frequency, then name)."""
    if not len(pos):
        return np.zeros(0, np.int64)
    S = pos.B if lam == 0 else pos.B + lam * cov
    r = np.arange(len(pos))
    St = S[r, pos.t][:, None]; TBt = pos.TB[r, pos.t][:, None]
    better = (S > St) | ((S == St) & (pos.TB < TBt))
    return better.sum(1) + 1


def lam_star(cell, key, grid, memo):
    """Frozen rule: highest pooled cross-fit dev Hit@1, ties to the smaller λ; λ* > 0 only with a gain >= 0.5 points
    over λ = 0, else λ* = 0. Held-out text never enters."""
    cov = cov_matrix(cell.dv, cell.cands, key, memo)
    hits = {lam: int((ranks(cell.dv, cov, lam) == 1).sum()) for lam in grid}
    best = max(grid, key=lambda lam: (hits[lam], -lam))
    n = len(cell.dv)
    if best != 0 and not (n and 200 * (hits[best] - hits[0.0]) >= n):   # gain >= 0.5 points, exact
        best = 0.0
    return best, hits, n


def evaluate(cell, key, grid, detail=True):
    memo = {}
    for s in cell.cands:
        assert s in key, "key does not cover every candidate sign"
    lam, dev_hits, n_dev = lam_star(cell, key, grid, memo)
    pos = cell.ho; n = len(pos)
    cov = cov_matrix(pos, cell.cands, key, memo)
    r0 = ranks(pos, cov, 0.0); rS = r0 if lam == 0 else ranks(pos, cov, lam)
    h0, hS = int((r0 == 1).sum()), int((rS == 1).sum())
    out = dict(lam_star=lam, n=n, hits_B=h0, hits_S=hS, lift=Fraction(100 * (hS - h0), n) if n else Fraction(0))
    if not detail:
        return out
    # PREREG-AMBIGUITY: "lift on reachable positions only" — reachable = the chunk read with this key, true sign in
    # place, has >= LMIN consonants (the count table's definition, per key). Reported only; grades nothing.
    reach = np.array([sum(len(key[s]) for s in t) >= LMIN for t, _ in pos.items], bool)
    nr = int(reach.sum())
    out.update(dev_hits={str(k): v for k, v in dev_hits.items()}, n_dev=n_dev,
               hit5_B=float(np.mean(r0 <= 5)) if n else 0.0, hit5_S=float(np.mean(rS <= 5)) if n else 0.0,
               mrr_B=float(np.mean(1 / r0)) if n else 0.0, mrr_S=float(np.mean(1 / rS)) if n else 0.0,
               gained=int(((rS == 1) & (r0 != 1)).sum()), lost=int(((r0 == 1) & (rS != 1)).sum()),
               n_reach=nr, lift_reach=float(100 * (((rS == 1) & reach).sum() - ((r0 == 1) & reach).sum()) / nr) if nr else 0.0)
    return out


def jl(e):
    """JSON form of an evaluate() result (lift as float; exact hits kept for regrading)."""
    return {q: (float(v) if isinstance(v, Fraction) else v) for q, v in e.items()}


def real_cell(order, cands, folds=True):
    dev, dev_ids, ho, _ = halves(order)
    return Cell(dev, dev_ids, ho, cands, folds)


def scramble_cell(order, cands, k):
    """Unigram scramble (sealed ladder `unigram`, seed base + 20,000 + k) of dev followed by ho; trigram and key both
    on the scramble; line ids kept by index."""
    # PREREG-AMBIGUITY: the prereg does not say whether dev and ho are scrambled from one token pool or separately.
    # Read as one call on the whole text (dev followed by ho), as the K1 filler is built.
    dev, dev_ids, ho, _ = halves(order)
    sc = unwrap(L.unigram(wrap(dev + ho), random.Random(BASE + 20000 + k)))
    return Cell(sc[:len(dev)], dev_ids, sc[len(dev):], cands)


# ------------------------------------------------------------------ planted generator (K0, K1)
def plant(order, k, nsub):
    """Text made only of lexicon words (generator frozen in the prereg), cut to draw k's chunk lengths in build order and
    split in half as draw k is. Returns an order list (line id, signs, is_dev) like draw()."""
    freq = Counter(s for _, t, _ in order for s in t)
    signs = sorted(freq)
    single = defaultdict(list); zero = []
    for s in signs:
        v = B.true_value(s)
        if len(v) == 1:
            single[v[0]].append(s)
        elif not v:
            zero.append(s)
    # PREREG-AMBIGUITY: skeletons are drawn uniformly from the lexicon's 4-7 consonant skeletons that can be spelled
    # (every consonant has a sign of exactly that value in draw k); the count excluded is recorded.
    all47 = sorted(t for t in LEX if PLANT_LMIN <= len(t) <= PLANT_LMAX)
    pool = [t for t in all47 if all(single.get(c) for c in t)]
    sub = random.Random(BASE + k).sample(pool, nsub)
    # PREREG-AMBIGUITY: "weights 1 / rank": rank = order of drawing (first drawn = rank 1).
    w_cum = list(np.cumsum([1 / (r + 1) for r in range(nsub)]))
    z = sum(freq[s] for s in zero) / sum(freq.values())
    p0 = z / (1 - z)                                  # share p/(1+p) of zero-consonant signs equals draw k's
    assert p0 <= 1, "zero-consonant share above 1/2: plant cannot match it"
    cum1 = {c: list(np.cumsum([freq[s] for s in ss])) for c, ss in single.items()}
    # PREREG-AMBIGUITY: the zero-consonant sign that follows is drawn by its frequency in draw k; word draws use the
    # spelling rng (base + 50,000 + k).
    cum0 = list(np.cumsum([freq[s] for s in zero]))
    rs = random.Random(BASE + 50000 + k)
    need = sum(len(t) for _, t, _ in order); stream = []
    while len(stream) < need:
        word = rs.choices(sub, cum_weights=w_cum)[0]
        for c in word:
            stream.append(rs.choices(single[c], cum_weights=cum1[c])[0])
            if rs.random() < p0:
                stream.append(rs.choices(zero, cum_weights=cum0)[0])
    out, i = [], 0
    for tid, t, d in order:
        out.append((tid, tuple(stream[i:i + len(t)]), d)); i += len(t)
    info = dict(sublex=nsub, skeletons_4_7=len(all47), unspellable_excluded=len(all47) - len(pool),
                zero_share=z, p_zero_follow=p0)
    return out, info


def as_dev_ho(order):
    """Order list -> list in 'dev followed by ho' order (each half in build order) and back."""
    return [x for x in order if x[2]] + [x for x in order if not x[2]]


def dilute(plant_dh, filler, us, w):
    return [(tid, fill if u >= w else t, d) for (tid, t, d), fill, u in zip(plant_dh, filler, us)]


def ic_ho(order_dh, true):
    ho = [t for _, t, d in order_dh if not d]
    return L.IC(wrap(ho), LEX).full(true)


# ------------------------------------------------------------------ jobs (run in workers)
def job_a1(k):
    st = sealed_stream(k)
    H = L.IC(st["ho"], LEX)
    t = H.full(st["true"]); n1 = float(np.mean([H.full(key) for key in st["n1"]]))
    return dict(k=k, true_ic=t, n1_mean=n1)


def job_gate(k):
    """Label-free counts (A2, F4): no trigram, no lexicon, no key score."""
    order = draw(k); dev, _, ho, _ = halves(order)
    ho4 = [t for t in ho if len(t) >= 4]; clean = [t for t in ho4 if is_clean(t, dev)]
    tv = {s: B.true_value(s) for _, t, _ in order for s in t}
    reach = sum(len(t) for t in clean if sum(len(tv[s]) for s in t) >= LMIN)
    reach_c = sum(1 for t in clean if sum(len(tv[s]) for s in t) >= LMIN for s in t if tv[s])
    cp = sum(len(t) for t in clean)
    return dict(k=k, ho_tokens=sum(len(t) for t in ho), ho_texts_ge4=len(ho4), positions_ge4=sum(len(t) for t in ho4),
                clean_positions=cp, clean_texts=len(clean), reachable=reach, reachable_share=reach / cp if cp else 0.0,
                reachable_with_consonant=reach_c, thin=cp < F4_MIN)


def _plant_cell(k, nsub):
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    po, info = plant(order, k, nsub)
    return order, cands, po, info


def job_k0_trigram(args):
    """F3: trigram-only Hit@1 on the K0 plant's held-out clean positions. No key, no lexicon."""
    k, nsub = args
    _, cands, po, info = _plant_cell(k, nsub)
    c = real_cell(po, cands, folds=False)
    r = ranks(c.ho, None, 0.0)
    return dict(k=k, trigram_hit1=float(100 * np.mean(r == 1)) if len(r) else 0.0, n=len(r), plant=info)


def job_k0(args):
    k, nsub, grid = args
    order, cands, po, info = _plant_cell(k, nsub)
    st = sealed_stream(k); true = st["true"]
    pc = real_cell(po, cands)
    et = evaluate(pc, true, grid)
    es = evaluate(scramble_cell(po, cands, k), true, grid)
    n1 = [evaluate(pc, key, grid, detail=False) for key in st["n1"][:N1_KEYS]]
    return dict(k=k, plant=info, counts=pc.counts, true=et, scramble_true=es, n1=n1)


def job_k1(args):
    """phase 'build': plant, filler, uniforms and the IC bisection only (sees no lift). phase 'lift': rebuild the same
    diluted plant (deterministic) and score the true key; run only after the F2 count is known."""
    phase, k, nsub, grid, target = args
    order, cands, po, info = _plant_cell(k, nsub)
    true = {s: B.true_value(s) for s in cands}
    dh = as_dev_ho(po)
    dev, _, ho, _ = halves(order)
    filler = unwrap(L.markov(wrap(dev + ho), random.Random(BASE + 10000 + k)))   # sealed markov, whole draw
    ur = random.Random(BASE + 60000 + k); us = [ur.random() for _ in dh]
    # PREREG-AMBIGUITY: bisection evaluates midpoints of [lo, hi] only (no endpoint evaluations), at most 20 steps,
    # and assumes the IC rises with w (more plant): IC below target -> lo = w, else hi = w.
    lo, hi, steps, built, w = 0.0, 1.0, [], False, None
    for _ in range(BISECT_STEPS):
        w = (lo + hi) / 2
        ic = ic_ho(dilute(dh, filler, us, w), true); steps.append(dict(w=w, ic=ic))
        if abs(ic - target) <= IC_TOL:
            built = True; break
        if ic < target:
            lo = w
        else:
            hi = w
    out = dict(k=k, plant=info, target_ic=target, bisection=steps, built=built)
    if not built or phase == "build":
        return out                                    # F2: an unbuilt draw is not scored; the filler is not changed
    d = dilute(dh, filler, us, w)
    out.update(w=w, replaced=sum(u >= w for u in us), n_chunks=len(us))
    c = real_cell(d, cands)
    out.update(counts=c.counts, true=jl(evaluate(c, true, grid)))
    return out


def job_k2(args):
    k, grid = args
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k)
    c = real_cell(order, cands)
    es = evaluate(scramble_cell(order, cands, k), st["true"], grid)
    n1 = [evaluate(c, key, grid, detail=False) for key in st["n1"][:N1_KEYS]]
    return dict(k=k, counts=c.counts, scramble_true=es, n1=n1)


def job_k3(args):
    k, grid = args
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k)
    c = real_cell(order, cands)
    return dict(k=k, counts=c.counts, true=evaluate(c, st["true"], grid))


def fit_n3(cell, true, kept, cl_of, sample, rng):
    """N3: hill-climb on the real dev half to maximise cross-fitted dev Hit@1 at λ = 1 on a fixed 300-position sample.
    500 swaps inside consonant-count classes from a shuffled key; swap and accept rule as the sealed ladder fit."""
    # PREREG-AMBIGUITY: start key, class pools, swap draw, the skipped equal-value swap (counted as a step) and the
    # >= acceptance all follow sealed lb_shape_ladder.fit; only the objective differs.
    sub = Positions.__new__(Positions)
    sub.items = [cell.dv.items[i] for i in sample]; sub.t = cell.dv.t[sample]
    sub.B = cell.dv.B[sample]; sub.TB = cell.dv.TB[sample]
    memo = {}

    def obj(key):
        if len(memo) > 2_000_000:
            memo.clear()
        return int((ranks(sub, cov_matrix(sub, cell.cands, key, memo), N3_LAMBDA) == 1).sum())

    key = L.shuffle_in_class(true, kept, cl_of, rng); cur = obj(key); start = cur
    by = defaultdict(list)
    for s in kept:
        by[cl_of[s]].append(s)
    pools = [v for v in by.values() if len(v) >= 2]; w = [len(v) for v in pools]
    for _ in range(N3_SWAPS):
        a, b = rng.sample(rng.choices(pools, weights=w)[0], 2)
        if key[a] == key[b]:
            continue
        key[a], key[b] = key[b], key[a]
        nc = obj(key)
        if nc >= cur:
            cur = nc
        else:
            key[a], key[b] = key[b], key[a]
    return key, dict(start_hits=start, end_hits=cur, n_sample=len(sample))


def job_k4(args):
    k, grid, sealed_n2 = args
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k, n2=True, lex=LEX)
    H = L.IC(st["ho"], LEX); chk = []
    for name, r, fk in st["n2"]:
        chk.append(abs(H.full(fk) - sealed_n2[name][r]))
    c = real_cell(order, cands)
    n2 = [dict(src=name, restart=r, **jl(evaluate(c, fk, grid, detail=False))) for name, r, fk in st["n2"]]
    sample = sorted(random.Random(BASE + 40000 + k).sample(range(len(c.dv)), min(N3_SAMPLE, len(c.dv))))
    n3 = []
    for r in range(N3_RESTARTS):
        rng = random.Random(BASE + 30000 + 10 * k + r)
        fk, fi = fit_n3(c, st["true"], st["kept"], st["cl_of"], sample, rng)
        n3.append(dict(restart=r, fit=fi, **jl(evaluate(c, fk, grid, detail=False))))
    return dict(k=k, n2_ic_maxdiff=max(chk), n2=n2, n3=n3, counts=c.counts)


def run_jobs(fn, jobs):
    with Pool(NWORK, initializer=init) as P:
        return P.map(fn, jobs, chunksize=1)


# ------------------------------------------------------------------ grading helpers (exact)
def lift_of(e):
    return Fraction(100 * (e["hits_S"] - e["hits_B"]), e["n"]) if e["n"] else Fraction(0)


def median_lift(es):
    return statistics.median(sorted(lift_of(e) for e in es))


# ------------------------------------------------------------------ modes
def kill():
    path = HERE / "kill.json"
    assert not path.exists(), "kill.json exists: no rerun after any lift is seen (prereg Aborts)"
    out = dict(prereg="docs/prereg/lift_certify.md", nwork=NWORK, fallbacks={})
    why, fm = a4(); out["A4"] = dict(free_mem_frac=fm, failures=why)
    if why:
        print("A4: do not start:", "; ".join(why)); sys.exit(2)          # nothing computed, nothing written
    t0 = time.time(); sealed = sealed_r1()

    # ---- A1: sealed R1 true IC and N1 mean, draws 1-3, to 1e-9
    a1 = run_jobs(job_a1, [1, 2, 3])
    for r in a1:
        r["d_true"] = abs(r["true_ic"] - sealed[r["k"]]["true_ic"]); r["d_n1"] = abs(r["n1_mean"] - sealed[r["k"]]["n1_mean"])
    out["A1"] = dict(draws=a1, passed=all(r["d_true"] <= A1_TOL and r["d_n1"] <= A1_TOL for r in a1))
    if not out["A1"]["passed"]:
        stop(out, path, "A1: study code does not reproduce sealed R1 true IC / N1 mean (draws 1-3) to 1e-9")

    # ---- A2 + F4: label-free gate counts, draws 1-20
    g = run_jobs(job_gate, list(range(1, NDRAW + 1)))
    mc = statistics.median(r["clean_positions"] for r in g); ms = statistics.median(r["reachable_share"] for r in g)
    # PREREG-AMBIGUITY: "differs from the table by more than 5%" read as relative: |median / table - 1| > 0.05, for
    # the median clean positions (1,376) and the median per-draw reachable share (49%); other counts are reported.
    a2_ok = abs(mc / GATE_CLEAN - 1) <= GATE_TOL and abs(ms / GATE_REACH_SHARE - 1) <= GATE_TOL
    thin = [r["k"] for r in g if r["thin"]]
    out["A2"] = dict(draws=g, median_clean=mc, median_reach_share=ms,
                     median_reachable=statistics.median(r["reachable"] for r in g),
                     median_reachable_with_consonant=statistics.median(r["reachable_with_consonant"] for r in g),
                     passed=a2_ok)
    out["fallbacks"]["F4"] = dict(thin_draws_flagged=thin, median_clean=mc, abort=mc < F4_MIN)
    if not a2_ok:
        stop(out, path, "A2: recomputed gate count differs from the table by more than 5%: stop and redraft")
    if mc < F4_MIN:
        stop(out, path, "A3 (F4): median clean positions below 900: abort")

    # ---- F3: trigram-only Hit@1 on the K0 plant, before any K0 lift
    nsub = SUBLEX
    f3 = run_jobs(job_k0_trigram, [(k, nsub) for k in range(1, NK0 + 1)])
    f3_hit = any(r["trigram_hit1"] > F3_MAX for r in f3)
    out["fallbacks"]["F3"] = dict(check=f3, applied=f3_hit)
    if f3_hit:
        nsub = SUBLEX_F3                              # applied once; also applies to K1
        out["fallbacks"]["F3"]["after"] = run_jobs(job_k0_trigram, [(k, nsub) for k in range(1, NK0 + 1)])
    out["sublex"] = nsub

    # ---- K0: planted, full dose, draws 1-5, original grid
    grid = GRID0
    k0 = run_jobs(job_k0, [(k, nsub, grid) for k in range(1, NK0 + 1)])
    rows = []
    for r in k0:
        lt, ls, mn = lift_of(r["true"]), lift_of(r["scramble_true"]), median_lift(r["n1"])
        rows.append(dict(k=r["k"], plant=r["plant"], counts=r["counts"], true=jl(r["true"]),
                         scramble_true=jl(r["scramble_true"]), n1_lifts=[float(lift_of(e)) for e in r["n1"]],
                         n1_lam_star=[e["lam_star"] for e in r["n1"]], n1_median=mn,
                         ok_true=lt >= 10, ok_scramble=ls <= 1, ok_n1=mn <= 1))
    k0_pass = all(x["ok_true"] and x["ok_scramble"] and x["ok_n1"] for x in rows)
    out["K0"] = dict(grid=grid, draws=rows, passed=k0_pass)
    if not k0_pass:
        out["reading"] = R_K0_FAIL
        stop(out, path, "K0 fail: the pipeline is broken. " + R_K0_FAIL)

    # ---- F1: grid edge, decided at K0 on planted text; K0 is not regraded
    n4 = sum(x["true"]["lam_star"] == 4.0 for x in rows)
    f1 = n4 >= 3
    out["fallbacks"]["F1"] = dict(true_lam4_draws=n4, applied=f1)
    if f1:
        grid = GRID0 + GRID_F1
    out["grid"] = grid

    # ---- K1: planted, real dose, draws 1-20
    kb = run_jobs(job_k1, [("build", k, nsub, grid, sealed[k]["true_ic"]) for k in range(1, NDRAW + 1)])
    nb = sum(r["built"] for r in kb)
    out["fallbacks"]["F2"] = dict(unbuilt=[r["k"] for r in kb if not r["built"]], built=nb, abort=nb < 18)
    if nb < 18:
        out["K1"] = dict(draws=kb, built=nb)
        stop(out, path, "A3 (F2): fewer than 18 of 20 K1 draws built: abort")
    k1 = run_jobs(job_k1, [("lift", r["k"], nsub, grid, sealed[r["k"]]["true_ic"]) for r in kb if r["built"]])
    for r, b in zip(k1, [r for r in kb if r["built"]]):
        assert r["bisection"] == b["bisection"], "K1 rebuild differs from the bisection run"
        r["ok"] = lift_of(r["true"]) >= 3
    k1 = k1 + [r for r in kb if not r["built"]]; k1.sort(key=lambda r: r["k"])
    need = (4 * nb + 4) // 5                          # >= 80% of built draws, rounded up (16 of 20 when all built)
    passes = sum(r.get("ok", False) for r in k1)
    k1_pass = passes >= need
    out["K1"] = dict(draws=k1, built=nb, passes=passes, needed=need, passed=k1_pass)
    graded = k1_pass
    if not k1_pass:
        out["reading"] = R_K1_FAIL

    # ---- K2: real text, negative controls (graded only when K1 passed)
    k2 = run_jobs(job_k2, [(k, grid) for k in range(1, NDRAW + 1)])
    rows = []
    for r in k2:
        ls, mn = lift_of(r["scramble_true"]), median_lift(r["n1"])
        rows.append(dict(k=r["k"], counts=r["counts"], scramble_true=jl(r["scramble_true"]),
                         n1_lifts=[float(lift_of(e)) for e in r["n1"]], n1_lam_star=[e["lam_star"] for e in r["n1"]],
                         n1_median=mn, ok_scramble=ls <= 1, ok_n1=mn <= 1))
    ns, nn = sum(x["ok_scramble"] for x in rows), sum(x["ok_n1"] for x in rows)
    k2_pass = ns >= 19 and nn >= 19
    out["K2"] = dict(draws=rows, scramble_ok=ns, n1_ok=nn, graded=graded, passed=k2_pass if graded else None,
                     record_only=not graded)
    if graded and not k2_pass:
        out["reading"] = R_K2_FAIL
        stop(out, path, "K2 fail (K1 passed): " + R_K2_FAIL)

    # ---- K3: the kill named in the brief
    k3 = run_jobs(job_k3, [(k, grid) for k in range(1, NDRAW + 1)])
    rows = [dict(k=r["k"], counts=r["counts"], true=jl(r["true"]), ok=lift_of(r["true"]) >= 3) for r in k3]
    n3 = sum(x["ok"] for x in rows); k3_pass = n3 >= 16
    out["K3"] = dict(draws=rows, passes=n3, graded=graded, passed=k3_pass if graded else None, record_only=not graded)
    out["seconds"] = round(time.time() - t0, 1)
    if not graded:
        if k3_pass:
            out["K3"]["note"] = R_K1_K3_NOTE + " (needs a new prereg)"
        out["k4_may_run"] = False
        dump(out, path); print("K1 failed: unpowered; K2 and K3 recorded only. K4 does not run.", flush=True); sys.exit(1)
    if not k3_pass:
        out["reading"] = R_K3_FAIL
        stop(out, path, "K3 fail: no certify by prediction. " + R_K3_FAIL)
    out["k4_may_run"] = True
    dump(out, path); print("K0-K3 passed; K4 (full) may run", flush=True)


def full():
    kp, path = HERE / "kill.json", HERE / "full.json"
    assert kp.exists(), "kill.json missing: run `kill` first"
    kr = json.load(open(kp))
    assert kr.get("k4_may_run") is True and kr["K1"]["passed"] is True and kr["K2"]["passed"] is True \
        and kr["K3"]["passed"] is True, "kill.json does not show K1, K2 and K3 all passed: K4 refused"
    assert not path.exists(), "full.json exists: no rerun after any lift is seen (prereg Aborts)"
    why, fm = a4()
    if why:
        print("A4: do not start:", "; ".join(why)); sys.exit(2)
    t0 = time.time(); sealed = sealed_r1(); grid = tuple(kr["grid"])
    res = run_jobs(job_k4, [(k, grid, sealed[k]["n2"]) for k in range(1, NDRAW + 1)])
    out = dict(prereg="docs/prereg/lift_certify.md", grid=grid)
    # PREREG-AMBIGUITY: N2 is "as sealed"; the replayed keys are checked to give the sealed held-out IC to 1e-9 (same
    # tolerance as A1). A mismatch stops before grading.
    bad = [r["k"] for r in res if r["n2_ic_maxdiff"] > A1_TOL]
    if bad:
        out.update(draws=res)
        stop(out, path, f"N2 replay does not reproduce the sealed N2 IC (draws {bad})")
    # True-key lift per draw is the K3 value (same draw, key, grid and code; deterministic).
    true_lift = {x["k"]: Fraction(100 * (x["true"]["hits_S"] - x["true"]["hits_B"]), x["true"]["n"]) for x in kr["K3"]["draws"]}
    rows = []
    for r in res:
        n2l = [lift_of(e) for e in r["n2"]]; n3l = [lift_of(e) for e in r["n3"]]
        mean_n2 = sum(n2l, Fraction(0)) / len(n2l); mx = max(n2l + n3l)
        rows.append(dict(k=r["k"], counts=r["counts"], n2=r["n2"], n3=r["n3"], n2_mean=mean_n2, noise_max=mx,
                         true_lift=true_lift[r["k"]], ok_A=mean_n2 <= 1, ok_B=true_lift[r["k"]] > mx))
    na, nb = sum(x["ok_A"] for x in rows), sum(x["ok_B"] for x in rows)
    bar_a, bar_b = na >= 16, nb >= 16
    certify = bool(kr["K3"]["passed"]) and bar_a and bar_b
    out.update(draws=rows, bar_A=dict(passes=na, passed=bar_a), bar_B=dict(passes=nb, passed=bar_b), certify=certify,
               reading=(R_ALL_PASS + " " + R_INDUS) if certify else R_K4_FAIL, seconds=round(time.time() - t0, 1))
    dump(out, path)
    print(json.dumps(dict(bar_A=out["bar_A"], bar_B=out["bar_B"], certify=certify), default=_conv), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "kill":
        kill()
    elif mode == "full":
        full()
    else:
        sys.exit("usage: run.py kill|full")
