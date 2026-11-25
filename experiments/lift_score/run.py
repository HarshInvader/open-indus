"""Lift score on Linear B (prereg docs/prereg/lift_score.md, SEALED v3, tag `lift_score`).
Run (from the repo root, under the Indus compute lock; A4 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/lift_score/run.py kill   # A-checks, F3, A6, K0, F1, K1/F2 -> kill.json
  board/run.sh .venv/bin/python -I experiments/lift_score/run.py full   # K2, K3, K4 (only after K0 and K1 passed) -> full.json
Workers: env NWORK (default 4, capped at 4).

Order (the prereg's order, strongest first; K0 is first of the kill tests and nothing real-text is scored before it):
  kill: A4 guard (lock, memory) and the seal check; A1 (sealed R1 true IC and N1 mean, draws 1-3, to 1e-9); A2 + F4
        (label-free clean counts, draws 1-20); F3 (trigram-only Hit@1 on the K0 plant, before any K0 gain); A6 (window
        model sums to 1; sees no gain); **K0** (draws 1-5, original grid). A K0 fail STOPS: nothing else runs.
        Then F1 (grid edge, decided at K0; K0 not regraded); K1: the 20 dose targets (D of the true key on the real
        development half; the first real-text number) are written to k1_targets.json BEFORE any K1 plant is built or
        scored; then the D-only bisection (F2), then the K1 gains. A K1 fail: K2 and K3 run once, record-only, in this
        same mode; K4 never runs; the route rule applies.
  full: refuses unless kill.json shows K0 and K1 passed. K2 (a fail stops before K3), K3 (a fail stops), K4 (9 sealed
        N2 keys, 3 N3 keys per draw; bars A, B, C).
Each mode refuses to start if its own output exists (no rerun after any gain is seen). Outputs hold per-draw and per-key
aggregates only (no per-position arrays). Hit@1 and Hit@1 lift (the 2027-clause measure) are reported for every cell
and key; G grades the bars.

Reuse. Nothing is loaded at import: the sealed modules are loaded by load_sealed() (called in main and in each worker).
  Imported by path (they load no data at import): sealed lb_shape_ladder (build, lb_lines, IC, markov, unigram, classes,
  permute_in_class_bins, shuffle_in_class, fit, seeds), sealed lb_certify (chunk, m77_lengths, Homer lexicon,
  true_value), corpus.build._close (near-copy rule).
  Copied from the sealed sibling experiments/lift_certify/run.py (not imported: it loads the ladder at import and its
  study base is a module constant): the guard, draw / halves / sealed_stream, the clean rule, the CRC32 folds, the
  bench_restoration trigram (itself a line-for-line copy), Positions, ranks, the planted generator and dilute.
  The word model (Lex, Model, em) follows the label-free pilot the prereg was drafted from; the prereg wins where they
  differ (each place is marked PREREG-AMBIGUITY).

No Indus step: M77 enters only as text lengths through the sealed `build` (lb_certify.m77_lengths). splits_v2 and
claim-bench key files are never loaded (A5 is enforced by an audit hook on file opens); no M77 sign is masked,
restored or read. No key values are printed or written.
"""
import hashlib, importlib.util, json, math, os, random, re, statistics, subprocess, sys, time, zlib
from collections import Counter, defaultdict
from itertools import product
from math import log
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PREREG = "docs/prereg/lift_score.md"
NWORK = max(1, min(4, int(os.environ.get("NWORK", "4"))))
BASE = 20270101                                       # study base (prereg Seeds)
NDRAW, NK0 = 20, 5
GRID0 = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
GRID_F1 = (8.0, 16.0)
LAM_MARGIN = 0.01                                     # nats; λ* > 0 only with this pooled dev gain over λ = 0
NFOLD = 5
N1_KEYS, NPERMLEX = 20, 5
SUBLEX, SUBLEX_F3 = 500, 2000
LMIN, MAXW = 4, 7                                     # word list W: skeletons of 4 to 7 consonants
EM_ITERS, EM_ALPHA, RHO0, RHO_MIN, RHO_MAX = 15, 0.01, 0.5, 0.001, 0.999
D_TOL, BISECT_STEPS = 0.005, 12
N3_RESTARTS, N3_SWAPS, N3_RHO = 3, 3000, 0.05
K0_GAIN, GAIN_BAR, CTRL_BAR = 0.10, 0.02, 0.005
A1_TOL, A6_TOL = 1e-9, 1e-9
GATE_CLEAN, GATE_TOL, F4_MIN, F3_MAX = 1376, 0.05, 900, 60
MEM_GUARD = 0.20
SEALED_R1 = ROOT / "experiments/lb_shape_ladder/full.json"
LOCK = ROOT / "board/compute.lock"

# ------------------------------------------------------------------ frozen readings (verbatim from the prereg)
R_K0_FAIL = ("The word-and-fragment score did not pass its planted test ({bar}). By the one-attempt rule, certify by "
             "held-out restoration on existing texts is closed for this corpus size (about 13,100 sign tokens in chunks "
             "of M77 length). This is a rule, not a proof that no score could work: the oracle gain was 0.50 nats.")
R_K1_FAIL = ("Unpowered. A planted language diluted to the true key's own dose (cross-fitted lexicon likelihood per "
             "consonant) does not raise restoration by 0.02 nats per sign at Indus shape. By the one-attempt rule, "
             "certify by held-out restoration on existing texts is closed for this corpus size. No further score is "
             "drafted; reopening needs more text.")
R_K1_K3_NOTE = "plant harsher than real text; K1 invalid as a power test"
R_K2_FAIL = "The gain is not specific to the key or to the text."
R_K3_FAIL = ("The true Linear B key with a Homeric lexicon does not raise restoration by 0.02 nats per sign, though a "
             "planted language at the same dose does. The cause is not isolated: the plant differs from real text in "
             "lexicon match, dose layout and sign order.")
R_AB_FAIL = "A gain exists but keys fitted to noise show it too. No certify by prediction."
R_C_FAIL = ("The gain comes from the sign grouping and the fragment model, not from the lexicon. It cannot certify "
            "sign values.")
R_ALL_PASS = ("On Linear B at Indus shape, a held-out restoration gain separates the true key from keys fitted to noise "
              "by these two fitters (3,000-swap IC; 3,000-swap fragment likelihood). This is a candidate certify "
              "statistic on this bench (one script, one lexicon). N3 was fitted to a fixed-weight proxy, not to G; no "
              "key fitted to G or to the learned-weight model was tried, and a new prereg with such a fitter is needed "
              "before 'certify' is used. A G pass alone does not meet the 2027 held-out-prediction clause; the Hit@1 "
              "figures are reported beside it.")
R_INDUS = "It says nothing about any Indus key."
R_2027 = "G is this study's gate, not the 2027 measure; Hit@1 is reported on every cell. A G pass alone does not meet the 2027 clause."

# ------------------------------------------------------------------ sealed modules, loaded on demand (never at import)
L = None                                              # sealed lb_shape_ladder module
B = None                                              # sealed lb_certify module
_close = None                                         # corpus.build._close (near-copy rule)
LEX = None                                            # Homeric skeleton lexicon (set of tuples), per worker
W47 = None                                            # word list W: sorted skeletons of 4 to 7 consonants
ALPHA = None                                          # the ten key letters, sorted
LEXS = {}                                             # 0 = Homeric W; j = 1..5 letter-permuted W (Lex objects)
INIT_ERR = None


def load_sealed():
    """As lb_formula_dial / lift_certify: lb_certify on the path (the ladder does `import run as base`) and the sealed
    ladder loaded under its own name. Loads code only, no data."""
    global L, B, _close, ALPHA
    if L is not None:
        return
    for p in (str(ROOT / "experiments/lb_certify"), str(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("ladder", ROOT / "experiments/lb_shape_ladder/run.py")
    mod = importlib.util.module_from_spec(spec); sys.modules["ladder"] = mod; spec.loader.exec_module(mod)
    from corpus.build import _close as cl             # near-copy rule; nothing else used
    assert mod.LMIN == LMIN and mod.MAXW == MAXW, "sealed ladder constants changed"
    assert list(mod.RUNGS).index("R1") == 1, "sealed ladder rung order changed"
    L, B, _close = mod, mod.base, cl
    ALPHA = sorted(B.KEYLET)
    assert ALPHA == list("dkmnpqrstz"), "key alphabet is not the ten prereg letters"


# ------------------------------------------------------------------ A5: no Indus key file, no split file
_A5_ALLOW = ("experiments/lift_score/", "experiments/lb_certify/", "experiments/lb_shape_ladder/",
             "experiments/cognate_decipher/ext/greek/", "corpus/", "board/compute.lock/", ".venv/",
             "sources/paragorth_Indus-/data/codelib/linear_b.jsonl", "data/m77_texts.jsonl",
             "docs/prereg/lift_score.md", "docs/prereg/HASHES.txt")
_A5_ON = False


def a5_hook():
    """A5 / Indus rule: inside the repo, only the files this study needs may be opened (Linear B lines, the Homer
    texts, M77 as text lengths, the sealed ladder outputs and code). Any other repo file (splits_v2, any key file)
    raises before it is read. Files outside the repo (the interpreter, system files) are not restricted."""
    global _A5_ON
    if _A5_ON:
        return
    _A5_ON = True
    root = os.path.realpath(str(ROOT)) + os.sep

    def hook(event, args):
        if event != "open" or not args:
            return
        p = args[0]
        if isinstance(p, bytes):
            p = os.fsdecode(p)
        elif isinstance(p, os.PathLike):
            p = os.fspath(p)
        if not isinstance(p, str):
            return
        full = os.path.realpath(p)
        if not full.startswith(root):
            return
        rel = full[len(root):].replace(os.sep, "/")
        if "splits" in rel or not any(rel == a or rel.startswith(a) for a in _A5_ALLOW):
            raise RuntimeError("A5: the study tried to open a repo file outside its data list: " + rel)

    sys.addaudithook(hook)


# ------------------------------------------------------------------ guard (copied from lift_certify)
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
    # PREREG-AMBIGUITY: "free memory" (A4) read as available memory, as lift_certify / ur3_legend_refute: macOS vm_stat
    # free + inactive + speculative pages over hw.memsize; elsewhere MemAvailable / MemTotal.
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
            why.append(f"compute lock held by pid {lp}, not by this run (run under board/run.sh)")
    fm = free_mem_frac()
    if fm < MEM_GUARD:
        why.append(f"free memory {fm:.1%} below the {MEM_GUARD:.0%} guard")
    return why, fm


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal_check():
    # PREREG-AMBIGUITY: not a prereg abort. Before anything is computed the run checks that the prereg file on disk
    # is the sealed one (its sha256 is on a HASHES.txt line with tag lift_score) and refuses to start otherwise.
    h = sha256_of(ROOT / PREREG); ok = False
    for line in open(ROOT / "docs/prereg/HASHES.txt"):
        f = line.split()
        if len(f) >= 4 and f[0] == h and f[1] == PREREG and f[-1] == "lift_score":
            ok = True
    return dict(prereg_sha256=h, sealed=ok, code_sha256=sha256_of(Path(__file__).resolve()))


def _conv(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def dump(obj, path):
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=_conv); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def stop(out, path, msg, code=1):
    out.update(stop=msg, status="stopped", full_may_run=False)
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(code)


# ------------------------------------------------------------------ draws (sealed build, with source line ids)
def wrap(seqs):
    return [[list(s)] for s in seqs]                  # ladder text form: a chunk is one word


def unwrap(texts):
    return [tuple(s for w in t for s in w) for t in texts]


_DRAWS = {}


def draw(k):
    """Draw k = sealed build(k, "chunk"), replayed to keep each chunk's source line id (needed for the CRC32 folds).
    Returns the chunks in build order as (line id, signs, is_dev); checked equal to the sealed build."""
    if k in _DRAWS:
        return _DRAWS[k]
    rng_np = np.random.default_rng(L.SEED + 1000 * k); rng = random.Random(L.SEED + 1000 * k)
    lines = L.lb_lines(); lens = B.m77_lengths()      # M77: text lengths only
    flat = [(tid, [s for w in ws for s in w]) for tid, ws in lines]
    ch = B.chunk(flat, lens, rng_np)
    pick = rng_np.choice(len(ch), size=min(2300, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    ids = sorted({tid for tid, _ in ch}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    order = [(tid, tuple(t), tid in dev_ids) for tid, t in ch]
    dev, ho, _ = L.build(k, "chunk")
    assert unwrap(dev) == [t for _, t, d in order if d] and unwrap(ho) == [t for _, t, d in order if not d], \
        "replayed build differs from the sealed build"
    _DRAWS.clear(); _DRAWS[k] = order                 # one draw kept per worker
    return order


def halves(order):
    """(dev seqs, dev ids, ho seqs, ho ids), each in build order. 'dev followed by ho' is dev + ho."""
    dv = [(i, t) for i, t, d in order if d]; ho = [(i, t) for i, t, d in order if not d]
    return [t for _, t in dv], [i for i, _ in dv], [t for _, t in ho], [i for i, _ in ho]


def sealed_stream(k, n2=False, lex=None):
    """Replay the sealed lb_shape_ladder one((k, "R1")) rng stream: true key, the 1000 N1 keys, and (n2=True) the 9
    sealed N2 keys (real, unigram, markov x 3 restarts). Copied from lift_certify. Scores nothing."""
    dev, ho, _ = L.build(k, "chunk")
    rng = random.Random(L.SEED + 1000 * k + 7 * 1)    # sealed R1 stream: SEED + 1000 k + 7 * index("R1")
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


# ------------------------------------------------------------------ clean positions, folds (copied from lift_certify)
def is_clean(t, others):
    """No text in `others` is identical to t, one edit from it, or contains / is contained in it (_close)."""
    return not any(t == u or _close(list(t), list(u)) for u in others)


def fold_of(tid):
    # PREREG-AMBIGUITY: "CRC32 of the source line id": zlib.crc32 of the decimal string of the integer line id, as
    # lift_certify and the pilot. Bears on λ* and on D (K0, K1).
    return zlib.crc32(str(tid).encode()) % NFOLD


def fold_parts(dev, dev_ids):
    """[(training chunks = the other four folds, every chunk of fold f)] for f = 0..4, each in build order."""
    fo = [fold_of(i) for i in dev_ids]
    return [([t for t, g in zip(dev, fo) if g != f], [t for t, g in zip(dev, fo) if g == f]) for f in range(NFOLD)]


# ------------------------------------------------------------------ trigram (bench_restoration ours_scores, as lift_certify)
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
        """B(c): the sum of the log probabilities of the up to three trigrams that contain position i."""
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
        # PREREG-AMBIGUITY: this prereg gives no tie rule for Hit@1 / Hit@5 / MRR (reported, not graded). Ties are
        # broken as in lift_certify: frequency in the trigram's training text (desc), then sign name. G has no ties.
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
    on the dev half, and cross-fit positions over the five CRC32 folds of the dev half (clean against the four
    training folds). Key-free: one Cell serves every key scored on that text."""

    def __init__(self, dev, dev_ids, ho, cands, folds=True):
        self.cands = sorted(cands); self.cidx = {c: i for i, c in enumerate(self.cands)}
        self.dev = dev
        tg = Trigram(dev, self.cands)
        ho4 = [t for t in ho if len(t) >= 4]
        clean = [t for t in ho4 if is_clean(t, dev)]
        self.counts = dict(ho_texts_ge4=len(ho4), ho_positions_ge4=sum(len(t) for t in ho4),
                           clean_texts=len(clean), clean_positions=sum(len(t) for t in clean))
        self.ho = Positions(clean, tg, self.cands, self.cidx)
        if not folds:
            return
        self.fold_train, self.fold_all, self.fold_pos = [], [], []
        for train, allf in fold_parts(dev, dev_ids):
            test = [t for t in allf if len(t) >= 4]
            test = [t for t in test if is_clean(t, train)]
            self.fold_train.append(train); self.fold_all.append(allf)
            self.fold_pos.append(Positions(test, Trigram(train, self.cands), self.cands, self.cidx))
        self.dv = Positions.concat(self.fold_pos, len(self.cands))
        self.counts["dev_crossfit_positions"] = len(self.dv)


# ------------------------------------------------------------------ word model (prereg "Word model"; code after the pilot)
class Lex:
    """Word list with fragment indexes: proper prefixes, proper suffixes, strict infixes (once per place)."""

    def __init__(self, words):
        self.words = sorted(words); self.id = {w: i for i, w in enumerate(self.words)}
        self.len = np.array([len(w) for w in self.words], float)
        pre, suf, inf = defaultdict(list), defaultdict(list), defaultdict(Counter)
        for i, w in enumerate(self.words):
            n = len(w)
            for j in range(1, n):
                pre[w[:j]].append(i); suf[w[j:]].append(i)
            for o in range(1, n):
                for e in range(o + 1, n):
                    inf[w[o:e]][i] += 1
        self.pre = {k: np.array(v) for k, v in pre.items()}; self.suf = {k: np.array(v) for k, v in suf.items()}
        self.inf = {k: (np.array(list(v)), np.array(list(v.values()), float)) for k, v in inf.items()}


class Model:
    """Window model: a stream of units; a unit is a word of W (prob (1 - rho) p[w]) or one consonant (rho q[c])."""

    def __init__(self, lex, p, rho, q):
        self.lex, self.p, self.rho, self.q = lex, p, rho, q
        self.E = rho + (1 - rho) * float((p * lex.len).sum())      # mean unit length
        self.memo = {}; self.fr = {}

    def frag(self, kind, t):
        """kind 0: Pre(t); 1: Suf(t); 2: Inf(t). Total p of the words behind the fragment."""
        k = (kind, t); v = self.fr.get(k)
        if v is None:
            if kind == 2:
                e = self.lex.inf.get(t); v = float((self.p[e[0]] * e[1]).sum()) if e is not None else 0.0
            else:
                e = (self.lex.pre if kind == 0 else self.lex.suf).get(t); v = float(self.p[e].sum()) if e is not None else 0.0
            self.fr[k] = v
        return v

    def fwd(self, x):
        """f[i] = P(x[1..i], a unit ends at i); returns (f, P(x)). The prereg's forward pass, term for term. Fragments
        longer than 6 (Pre, Suf) or 5 (Inf) consonants cannot sit in a word of at most 7, so those terms are skipped."""
        n = len(x); r = self.rho; f = [0.0] * (n + 1); f[0] = 1 / self.E
        for i in range(1, n + 1):
            v = f[i - 1] * r * self.q[x[i - 1]]
            for ln in range(LMIN, min(MAXW, i) + 1):
                j = self.lex.id.get(x[i - ln:i])
                if j is not None:
                    v += f[i - ln] * (1 - r) * self.p[j]
            if i < MAXW:
                v += (1 - r) / self.E * self.frag(1, x[:i])
            f[i] = v
        P = f[n]
        for i in range(max(0, n - MAXW + 1), n):
            P += f[i] * (1 - r) * self.frag(0, x[i:])
        if n <= MAXW - 2:
            P += (1 - r) / self.E * self.frag(2, x)
        return f, P

    def llr(self, x):
        """LLR(x) = log P(x) - sum log q(x[i]); an empty string scores 0."""
        if not x:
            return 0.0
        v = self.memo.get(x)
        if v is None:
            v = self.memo[x] = log(self.fwd(x)[1]) - sum(log(self.q[c]) for c in x)
        return v


def em(lex, strings, q):
    """EM for the word weights p and rho (per key, per training text). strings: Counter of consonant tuples.
    Start p uniform over W, rho = 0.5; fifteen iterations; p(w) = (n(w) + α) / (N + α |W|), α = 0.01; rho = single
    consonants / all units, held in [0.001, 0.999]."""
    # PREREG-AMBIGUITY: "fifteen iterations" = fifteen E-step + M-step rounds; the model used for scoring carries the
    # parameters of the fifteenth M-step (as the pilot). Chunks with no consonant add nothing to the fit.
    nW = len(lex.words); p = np.full(nW, 1.0 / nW); rho = RHO0
    for _ in range(EM_ITERS):
        m = Model(lex, p, rho, q); cnt = np.zeros(nW); oov = 0.0; r = rho
        for x, mult in strings.items():
            n = len(x)
            if not n:
                continue
            f, P = m.fwd(x)
            b = [0.0] * (n + 1); b[n] = 1.0           # b[i] = P(x[i+1..n] | a unit ends at i)
            for i in range(n - 1, -1, -1):
                v = r * q[x[i]] * b[i + 1]
                for ln in range(LMIN, min(MAXW, n - i) + 1):
                    j = lex.id.get(x[i:i + ln])
                    if j is not None:
                        v += (1 - r) * p[j] * b[i + ln]
                if n - i < MAXW:
                    v += (1 - r) * m.frag(0, x[i:])
                b[i] = v
            w = mult / P
            for i in range(1, n + 1):
                oov += w * f[i - 1] * r * q[x[i - 1]] * b[i]                      # single consonants
                for ln in range(LMIN, min(MAXW, i) + 1):
                    j = lex.id.get(x[i - ln:i])
                    if j is not None:
                        cnt[j] += w * f[i - ln] * (1 - r) * p[j] * b[i]           # whole words
            for i in range(1, min(n, MAXW - 1) + 1):                              # words behind a suffix fragment
                e = lex.suf.get(x[:i])
                if e is not None:
                    cnt[e] += w * (1 - r) / m.E * b[i] * p[e]
            for i in range(max(0, n - MAXW + 1), n):                              # words behind a prefix fragment
                e = lex.pre.get(x[i:])
                if e is not None:
                    cnt[e] += w * f[i] * (1 - r) * p[e]
            e = lex.inf.get(x) if n <= MAXW - 2 else None                         # words behind an infix fragment
            if e is not None:
                cnt[e[0]] += w * (1 - r) / m.E * p[e[0]] * e[1]
        tot = float(cnt.sum())
        if oov + tot > 0:
            rho = min(RHO_MAX, max(RHO_MIN, oov / (oov + tot)))
        p = (cnt + EM_ALPHA) / (tot + EM_ALPHA * nW)
    return Model(lex, p, rho, q)


def cons(t, key):
    return tuple(c for s in t for c in key[s])


def qdist(texts, key):
    """q: consonant frequencies of the training text read with the key, add-one over the ten letters."""
    c = Counter(x for t in texts for x in cons(t, key))
    tot = sum(c.values()) + len(ALPHA)
    return {a: (c[a] + 1) / tot for a in ALPHA}


def fit_model(lex, texts, key):
    return em(lex, Counter(cons(t, key) for t in texts), qdist(texts, key))


def dose_from(models, fold_all, key):
    """D: sum of LLR(x) over every chunk of each fold under the model fitted on the other four folds, divided by the
    number of consonants. Nats per consonant. Returns (D, consonants)."""
    # PREREG-AMBIGUITY: "every chunk of each fold" = all development chunks, of any length and clean or not (as the
    # pilot); chunks with no consonant add 0 to both sums. Bears on K1 (the dose target and the bisection).
    num, den = 0.0, 0
    for m, chunks in zip(models, fold_all):
        for t in chunks:
            x = cons(t, key); num += m.llr(x); den += len(x)
    return (num / den if den else 0.0), den


def dose(dev, dev_ids, key, lex):
    parts = fold_parts(dev, dev_ids)
    return dose_from([fit_model(lex, tr, key) for tr, _ in parts], [a for _, a in parts], key)


def perm_letters(j):
    # PREREG-AMBIGUITY: "a permutation of the ten consonant letters with no letter fixed", seed base + 70,000 + j:
    # the sorted letters are shuffled with random.Random(seed).shuffle, repeated on the same stream until no letter
    # maps to itself; letter i of the sorted alphabet is rewritten as letter i of the shuffled list.
    rng = random.Random(BASE + 70000 + j)
    while True:
        p = list(ALPHA); rng.shuffle(p)
        if all(a != b for a, b in zip(ALPHA, p)):
            return dict(zip(ALPHA, p))


def get_lex(j):
    """0: the Homeric word list W. j = 1..5: W with letter permutation j applied to every word."""
    if j not in LEXS:
        if j == 0:
            LEXS[j] = Lex(W47)
        else:
            m = perm_letters(j); words = {tuple(m[c] for c in w) for w in W47}
            assert len(words) == len(W47)
            LEXS[j] = Lex(words)
    return LEXS[j]


def llr_matrix(pos, cands, key, model):
    """cov[p, c] = LLR of the whole chunk read with the key, candidate c in the masked place."""
    vals = [tuple(key[c]) for c in cands]; uniq = sorted(set(vals)); ui = np.array([uniq.index(v) for v in vals])
    out = np.zeros((len(pos), len(cands)))
    for p_, (t, i) in enumerate(pos.items):
        pre = cons(t[:i], key); suf = cons(t[i + 1:], key)
        out[p_] = np.array([model.llr(pre + v + suf) for v in uniq])[ui]
    return out


def logp(pos, cov, lam):
    """log softmax share of the true sign over all candidates under S = B + λ cov."""
    if not len(pos):
        return np.zeros(0)
    S = pos.B if (lam == 0 or cov is None) else pos.B + lam * cov
    m = S.max(1, keepdims=True)
    return S[np.arange(len(pos)), pos.t] - (m[:, 0] + np.log(np.exp(S - m).sum(1)))


def ranks(pos, cov, lam):
    """1-based rank of the true sign under S = B + λ cov; ties broken by TB."""
    if not len(pos):
        return np.zeros(0, np.int64)
    S = pos.B if (lam == 0 or cov is None) else pos.B + lam * cov
    r = np.arange(len(pos))
    St = S[r, pos.t][:, None]; TBt = pos.TB[r, pos.t][:, None]
    better = (S > St) | ((S == St) & (pos.TB < TBt))
    return better.sum(1) + 1


def evaluate(cell, key, lexid, grid):
    """One key on one text, by the frozen rules: λ* on the cross-fitted development half only, then G and the
    reported figures on the held-out clean positions. Returns aggregates only."""
    for s in cell.cands:
        assert s in key, "key does not cover every candidate sign"
    lex = get_lex(lexid); C = len(cell.cands)
    fms = [fit_model(lex, tr, key) for tr in cell.fold_train]
    D, ncons = dose_from(fms, cell.fold_all, key)
    parts = [llr_matrix(p, cell.cands, key, m) for p, m in zip(cell.fold_pos, fms)]
    cov_dv = np.concatenate(parts) if parts else np.zeros((0, C))
    nd = len(cell.dv)
    # PREREG-AMBIGUITY: "pooled mean" = the mean over all cross-fit positions of the five folds together (not a mean
    # of fold means); the 0.01 margin is inclusive (a gain of exactly 0.01 nats keeps λ* > 0). Bears on K0 and K1.
    dl = {lam: (float(logp(cell.dv, cov_dv, lam).mean()) if nd else 0.0) for lam in grid}
    lam = max(grid, key=lambda g: (dl[g], -g))        # highest pooled mean; ties go to the smaller λ
    if lam != 0 and not (dl[lam] - dl[0.0] >= LAM_MARGIN):
        lam = 0.0
    mf = fit_model(lex, cell.dev, key)                # held-out scoring: fitted on the whole development half
    pos = cell.ho; n = len(pos)
    r0 = ranks(pos, None, 0.0)
    if lam == 0:
        g = np.zeros(n); rS = r0                      # λ* = 0: G is exactly 0
    else:
        cov = llr_matrix(pos, cell.cands, key, mf)
        g = logp(pos, cov, lam) - logp(pos, None, 0.0); rS = ranks(pos, cov, lam)
    # "G on positions in chunks of >= 4 consonants": the chunk read with this key, true sign in place.
    c4 = np.array([sum(len(key[s]) for s in t) >= LMIN for t, _ in pos.items], bool)
    n4 = int(c4.sum()); h0, hS = int((r0 == 1).sum()), int((rS == 1).sum())
    # PREREG-AMBIGUITY: Hit@1, Hit@5 and MRR are read under the one combined score S at the same λ* that G uses (the
    # pilot tuned a second, hit-based λ for Hit@1; the prereg defines one λ rule, so the prereg wins). The standard
    # error of G is the population form (std / sqrt(n)), as the pilot. Reported only; they grade no bar.
    return dict(lam=lam, n=n, G=float(g.mean()) if n else 0.0, se=float(g.std() / math.sqrt(n)) if n else 0.0,
                n_c4=n4, G_c4=float(g[c4].mean()) if n4 else 0.0,
                hits_B=h0, hits_S=hS, hit1_B=100 * h0 / n if n else 0.0, hit1_S=100 * hS / n if n else 0.0,
                hit1_lift=100 * (hS - h0) / n if n else 0.0,
                hit5_B=float(100 * np.mean(r0 <= 5)) if n else 0.0, hit5_S=float(100 * np.mean(rS <= 5)) if n else 0.0,
                mrr_B=float(np.mean(1 / r0)) if n else 0.0, mrr_S=float(np.mean(1 / rS)) if n else 0.0,
                rho=float(mf.rho), D=D, n_cons_dev=ncons, n_dev=nd, dev_gain_by_lam=[dl[x] - dl[0.0] for x in grid])


# ------------------------------------------------------------------ texts
def make_cell(order, cands, folds=True):
    dev, dev_ids, ho, _ = halves(order)
    return Cell(dev, dev_ids, ho, cands, folds)


def scramble_cell(order, cands, k):
    """Unigram scramble (sealed ladder `unigram`, seed base + 20,000 + k) of dev followed by ho; the trigram, the word
    model and the key are all on the scramble; line ids are kept by index."""
    # PREREG-AMBIGUITY: the prereg says "the scramble as in lift_certify/run.py": one call on the whole text (dev
    # followed by ho), one token pool. The same seed serves the K0 plant and the K2 real text of draw k. Bears on K0.
    dev, dev_ids, ho, _ = halves(order)
    sc = unwrap(L.unigram(wrap(dev + ho), random.Random(BASE + 20000 + k)))
    return Cell(sc[:len(dev)], dev_ids, sc[len(dev):], cands)


def plant(order, k, nsub):
    """Text made only of lexicon words (generator as lift_certify, new seeds), cut to draw k's chunk lengths in build
    order and split in half as draw k is. Returns an order list (line id, signs, is_dev) like draw()."""
    freq = Counter(s for _, t, _ in order for s in t)
    signs = sorted(freq)
    single = defaultdict(list); zero = []
    for s in signs:
        v = B.true_value(s)
        if len(v) == 1:
            single[v[0]].append(s)
        elif not v:
            zero.append(s)
    # PREREG-AMBIGUITY: skeletons are drawn uniformly (random.Random(base + k).sample) from the sorted 4-7 consonant
    # skeletons that can be spelled (every consonant has a sign of exactly that value in draw k); the count excluded
    # is recorded. As lift_certify. Bears on K0 and K1.
    pool = [t for t in W47 if all(single.get(c) for c in t)]
    sub = random.Random(BASE + k).sample(pool, nsub)
    # PREREG-AMBIGUITY: "weights 1 / rank": rank = order of drawing (first drawn = rank 1). As lift_certify.
    w_cum = list(np.cumsum([1 / (r + 1) for r in range(nsub)]))
    z = sum(freq[s] for s in zero) / sum(freq.values())
    p0 = z / (1 - z)                                  # share p/(1+p) of zero-consonant signs equals draw k's
    assert p0 <= 1, "zero-consonant share above 1/2: plant cannot match it"
    cum1 = {c: list(np.cumsum([freq[s] for s in ss])) for c, ss in single.items()}
    # PREREG-AMBIGUITY: the zero-consonant sign that follows is drawn by its frequency in draw k; word draws, sign
    # draws and the follow-on draws all use the spelling rng (base + 50,000 + k), in this order. As lift_certify.
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
    info = dict(sublex=nsub, skeletons_4_7=len(W47), unspellable_excluded=len(W47) - len(pool),
                zero_share=z, p_zero_follow=p0)
    return out, info


def as_dev_ho(order):
    """Order list in 'dev followed by ho' order (each half in build order)."""
    return [x for x in order if x[2]] + [x for x in order if not x[2]]


def dilute(plant_dh, filler, us, w):
    """Each chunk is replaced, when its fixed uniform u >= w, by the filler chunk at the same index."""
    return [(tid, fill if u >= w else t, d) for (tid, t, d), fill, u in zip(plant_dh, filler, us)]


# ------------------------------------------------------------------ workers
def init():
    global LEX, W47, INIT_ERR
    try:
        a5_hook(); load_sealed()
        LEX = B.build_lexicon()[0]
        W47 = sorted(t for t in LEX if LMIN <= len(t) <= MAXW)
    except BaseException as e:                        # a raising initializer would respawn workers for ever
        INIT_ERR = repr(e)


def _ready():
    if INIT_ERR is not None:
        raise RuntimeError("worker init failed: " + INIT_ERR)


def job_a1(k):
    _ready()
    st = sealed_stream(k)
    H = L.IC(st["ho"], LEX)
    t = H.full(st["true"]); n1 = float(np.mean([H.full(key) for key in st["n1"]]))
    return dict(k=k, true_ic=t, n1_mean=n1, lexicon=len(LEX), word_list=len(W47),
                word_list_by_length=[sum(len(w) == n for w in W47) for n in range(LMIN, MAXW + 1)])


def job_gate(k):
    """Label-free counts (A2, F4): no trigram, no lexicon, no key score."""
    _ready()
    order = draw(k); dev, _, ho, _ = halves(order)
    ho4 = [t for t in ho if len(t) >= 4]; clean = [t for t in ho4 if is_clean(t, dev)]
    cp = sum(len(t) for t in clean)
    return dict(k=k, sign_tokens=sum(len(t) for _, t, _ in order), ho_texts_ge4=len(ho4),
                positions_ge4=sum(len(t) for t in ho4), clean_positions=cp, clean_texts=len(clean), thin=cp < F4_MIN)


def _plant_cell(k, nsub):
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    # PREREG-AMBIGUITY: on plants the candidates are every sign type of the real draw k (the plant uses a subset of
    # them), as lift_certify. Bears on K0 and K1.
    po, info = plant(order, k, nsub)
    return order, cands, po, info


def job_k0_trigram(a):
    """F3: trigram-only Hit@1 on the K0 plant's held-out clean positions. No key, no lexicon score, no gain."""
    _ready()
    k, nsub = a
    _, cands, po, info = _plant_cell(k, nsub)
    c = make_cell(po, cands, folds=False)
    r = ranks(c.ho, None, 0.0)
    return dict(k=k, trigram_hit1=float(100 * np.mean(r == 1)) if len(r) else 0.0, n=len(r), plant=info)


def job_a6(nsub):
    """A6: the fitted K0 draw-1 model sums to 1 over all strings of each length 1 to 4. Sees no gain."""
    # PREREG-AMBIGUITY: "the fitted K0 draw-1 model" = the word model (Homeric W) fitted on the whole development
    # half of the K0 draw-1 plant under the true key; "sums to 1 over all strings of 1 to 4 consonants" = for each
    # length n = 1..4 the 10^n window probabilities sum to 1 within 1e-9 (a window model is normalised per length).
    _ready()
    _, cands, po, _ = _plant_cell(1, nsub)
    dev, _, _, _ = halves(po)
    m = fit_model(get_lex(0), dev, sealed_stream(1)["true"])
    sums = [math.fsum(m.fwd(x)[1] for x in product(ALPHA, repeat=n)) for n in (1, 2, 3, 4)]
    return dict(sums=sums, max_dev=max(abs(s - 1) for s in sums), p_sum=float(m.p.sum()), q_sum=math.fsum(m.q.values()))


def job_cells(a):
    """Score a list of (kind, j) keys on one text of draw k. text: plant | plant_scr | real | real_scr.
    kind: true (Homeric W) | n1 (sealed N1 key j, 0-based, Homeric W) | perm (true key, letter-permuted W j = 1..5)."""
    _ready()
    k, text, nsub, grid = a["k"], a["text"], a["nsub"], tuple(a["grid"])
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k); out = dict(k=k, text=text)
    if text.startswith("plant"):
        src, out["plant"] = plant(order, k, nsub)
    else:
        src = order
    cell = scramble_cell(src, cands, k) if text.endswith("_scr") else make_cell(src, cands)
    res = []
    for kind, j in a["keys"]:
        if kind == "true":
            e = evaluate(cell, st["true"], 0, grid)
        elif kind == "n1":
            e = evaluate(cell, st["n1"][j], 0, grid)
        else:
            e = evaluate(cell, st["true"], j, grid)
        e.update(kind=kind, j=j, text=text); res.append(e)
    out.update(counts=cell.counts, cells=res)
    return out


def job_target(k):
    """K1 dose target: D of the true key on the real development half of draw k. No held-out text, no masking.
    It sets a dose and grades nothing."""
    _ready()
    dev, dev_ids, _, _ = halves(draw(k))
    d, nc = dose(dev, dev_ids, sealed_stream(k)["true"], get_lex(0))
    return dict(k=k, D=d, n_cons_dev=nc, n_chunks_dev=len(dev))


def job_k1(a):
    """phase 'build': plant, filler, uniforms, D at w = 1 and w = 0 (F2), then the D-only bisection. Sees no gain.
    phase 'gain': rebuild the same diluted plant at the w found (deterministic; D is re-checked) and score the true
    key; run only after every target is on disk and the F2 count is known."""
    _ready()
    phase, k, nsub, target = a["phase"], a["k"], a["nsub"], a["target"]
    order, cands, po, info = _plant_cell(k, nsub)
    true = sealed_stream(k)["true"]; lex = get_lex(0)
    dh = as_dev_ho(po)
    dev, _, ho, _ = halves(order)
    filler = unwrap(L.markov(wrap(dev + ho), random.Random(BASE + 10000 + k)))   # sealed markov, once, dev followed by ho
    ur = random.Random(BASE + 60000 + k); us = [ur.random() for _ in dh]

    def d_at(w):
        dd, di, _, _ = halves(dilute(dh, filler, us, w))
        return dose(dd, di, true, lex)[0]

    if phase == "gain":
        w = a["w"]; dil = dilute(dh, filler, us, w)
        c = make_cell(dil, cands)
        e = evaluate(c, true, 0, tuple(a["grid"]))
        assert abs(e["D"] - a["D"]) <= 1e-12, "K1 rebuild differs from the bisection run"
        return dict(k=k, w=w, replaced=sum(u >= w for u in us), n_chunks=len(us), counts=c.counts, true=e)

    d1 = d_at(1.0); d0 = d_at(0.0)                    # evaluated first, for F2
    out = dict(k=k, plant=info, target=target, D_w1=d1, D_w0=d0, steps=[], n_chunks=len(us))
    # PREREG-AMBIGUITY (all bear on K1): (i) the F2 rules are tested in the order written: zero dose first, then
    # "richer than the full plant". (ii) An end point already within 0.005 of the target counts as landed (w = 1 is
    # tried before w = 0), since the plant "is diluted ... until its D is within 0.005 of the target"; it is not one
    # of the 12 steps. (iii) The 12 steps are midpoints of [lo, hi] starting from [0, 1], and D is taken to rise with
    # w (more plant): D below target -> lo = w, else hi = w. (iv) "within 0.005" is inclusive.
    if target < d0 - D_TOL:
        out.update(status="no dose above filler", built=True, scored=False, w=None, D=None)
    elif target > d1 + D_TOL:
        out.update(status="real text richer than the full plant", built=True, scored=True, w=1.0, D=d1)
    elif abs(d1 - target) <= D_TOL:
        out.update(status="landed", built=True, scored=True, w=1.0, D=d1)
    elif abs(d0 - target) <= D_TOL:
        out.update(status="landed", built=True, scored=True, w=0.0, D=d0)
    else:
        lo, hi = 0.0, 1.0
        out.update(status="unbuilt", built=False, scored=False, w=None, D=None)
        for _ in range(BISECT_STEPS):
            w = (lo + hi) / 2; d = d_at(w); out["steps"].append(dict(w=w, D=d))
            if abs(d - target) <= D_TOL:
                out.update(status="landed", built=True, scored=True, w=w, D=d); break
            if d < target:
                lo = w
            else:
                hi = w
    return out


class LLRSum:
    """N3 objective: summed LLR of the development chunks under a fixed word model. It has the interface of the sealed
    ladder IC (full / after / cache), so the sealed `fit` loop runs on it unchanged."""

    def __init__(self, texts, model):
        self.texts, self.model = texts, model
        self.by_sign = defaultdict(list)
        for i, t in enumerate(texts):
            for s in set(t):
                self.by_sign[s].append(i)

    def one(self, t, key):
        return self.model.llr(cons(t, key))

    def full(self, key):
        self.cache = [self.one(t, key) for t in self.texts]
        return self.total(self.cache)

    @staticmethod
    def total(vals):
        s = 0.0
        for v in vals:
            s += v
        return s

    def after(self, key, signs):
        idx = set()
        for s in signs:
            idx.update(self.by_sign[s])
        new = {i: self.one(self.texts[i], key) for i in idx}
        return self.total(new.get(i, c) for i, c in enumerate(self.cache)), new


def job_k4_n2(a):
    """The 9 sealed N2 keys of draw k (replayed), each with its own word model and λ*."""
    _ready()
    k, grid, sealed_n2 = a["k"], tuple(a["grid"]), a["sealed_n2"]
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k, n2=True, lex=LEX)
    # PREREG-AMBIGUITY: N2 is "as sealed"; the replayed keys are checked to give the sealed held-out IC to 1e-9 (the
    # A1 tolerance) before any of them is scored. A mismatch scores nothing and stops the mode.
    H = L.IC(st["ho"], LEX)
    diff = max(abs(H.full(fk) - sealed_n2[name][r]) for name, r, fk in st["n2"])
    if diff > A1_TOL:
        return dict(k=k, n2_ic_maxdiff=diff, n2=None)
    c = make_cell(order, cands)
    return dict(k=k, n2_ic_maxdiff=diff, counts=c.counts,
                n2=[dict(src=name, restart=r, **evaluate(c, fk, 0, grid)) for name, r, fk in st["n2"]])


def job_k4_n3(a):
    """N3: 3 keys per draw, hill-climbed on the real development half with the sealed `fit` loop (3,000 swaps inside
    consonant-count classes from a shuffled key) to maximise the summed LLR of the development chunks under the word
    model with uniform p, rho = 0.05 and uniform q. Each then gets its own word model and λ* by the frozen rules."""
    _ready()
    k, grid = a["k"], tuple(a["grid"])
    order = draw(k); cands = sorted({s for _, t, _ in order for s in t})
    st = sealed_stream(k); lex = get_lex(0)
    dev, _, _, _ = halves(order)
    # PREREG-AMBIGUITY: the objective sums over every development chunk (any length, no folds); "uniform q" = 1/10
    # per letter, in both the single-consonant unit and the null; restarts are numbered 0, 1, 2 (seed base + 30,000 +
    # 10 k + restart, as lift_certify) and one rng per restart draws the start key and then the swaps.
    nW = len(lex.words)
    proxy = Model(lex, np.full(nW, 1.0 / nW), N3_RHO, {x: 1.0 / len(ALPHA) for x in ALPHA})
    c = make_cell(order, cands); res = []
    for r in range(N3_RESTARTS):
        rng = random.Random(BASE + 30000 + 10 * k + r)
        S = LLRSum(dev, proxy)
        k0 = L.shuffle_in_class(st["true"], st["kept"], st["cl_of"], rng)
        start = S.full(k0)
        fk = L.fit(S, k0, st["kept"], st["cl_of"], N3_SWAPS, rng)
        res.append(dict(restart=r, fit_start=start, fit_end=S.full(fk), **evaluate(c, fk, 0, grid)))
    return dict(k=k, counts=c.counts, n3=res)


POOL = None


def run_jobs(fn, jobs):
    """Jobs go to at most NWORK (<= 4) worker processes; the pool is opened only after the A4 guard has passed."""
    global POOL
    if POOL is None:
        POOL = Pool(NWORK, initializer=init)
    return POOL.map(fn, jobs, chunksize=1)


# ------------------------------------------------------------------ assembling and grading
def cell_jobs(k, text, nsub, grid, parts):
    """Jobs for one text of one draw; N1 is split in two so that four workers stay busy."""
    jobs = []
    for part in parts:
        if part == "true":
            jobs.append([("true", 0)])
        elif part == "perm":
            jobs.append([("perm", j) for j in range(1, NPERMLEX + 1)])
        elif part == "n1":
            jobs += [[("n1", j) for j in range(0, N1_KEYS // 2)], [("n1", j) for j in range(N1_KEYS // 2, N1_KEYS)]]
    return [dict(k=k, text=text, nsub=nsub, grid=grid, keys=ks) for ks in jobs]


def gather(res):
    """Job results -> {k: dict(counts={text: ...}, cells=[...], plant=...)}."""
    by = {}
    for r in res:
        d = by.setdefault(r["k"], dict(counts={}, cells=[]))
        d["counts"][r["text"]] = r["counts"]; d["cells"] += r["cells"]
        if "plant" in r:
            d["plant"] = r["plant"]
    return by


def pick(d, text, kind):
    return sorted((c for c in d["cells"] if c["text"] == text and c["kind"] == kind), key=lambda c: c["j"])


def control_row(k, d, text):
    """Per-draw row of the control cells on `text` (plant or real): scramble, N1, permuted lexicons."""
    scr = pick(d, text + "_scr", "true")[0]; n1 = pick(d, text, "n1"); pm = pick(d, text, "perm")
    assert len(n1) == N1_KEYS and len(pm) == NPERMLEX
    row = dict(k=k, counts=d["counts"], scramble_true=scr, n1=n1, perm=pm,
               n1_median_G=statistics.median(e["G"] for e in n1),
               n1_median_hit1_lift=statistics.median(e["hit1_lift"] for e in n1),
               perm_max_G=max(e["G"] for e in pm))
    row.update(ok_scramble=scr["G"] <= CTRL_BAR, ok_n1=row["n1_median_G"] <= CTRL_BAR)
    return row


def med(xs):
    xs = list(xs)
    return round(statistics.median(xs), 4) if xs else None


def say(name, **kw):
    print(name + ": " + json.dumps(kw, default=_conv), flush=True)


def real_controls(nsub, grid):
    """K2 cells on real text: true key on the unigram scramble, 20 N1 keys, 5 letter-permuted lexicons."""
    jobs = [j for k in range(1, NDRAW + 1)
            for j in cell_jobs(k, "real_scr", nsub, grid, ["true"]) + cell_jobs(k, "real", nsub, grid, ["n1", "perm"])]
    by = gather(run_jobs(job_cells, jobs))
    rows = [control_row(k, by[k], "real") for k in sorted(by)]
    ns, nn = sum(r["ok_scramble"] for r in rows), sum(r["ok_n1"] for r in rows)
    return rows, ns, nn, (ns >= 19 and nn >= 19)


def real_true(nsub, grid):
    """K3 cell: the true key on real text."""
    by = gather(run_jobs(job_cells, [j for k in range(1, NDRAW + 1) for j in cell_jobs(k, "real", nsub, grid, ["true"])]))
    rows = [dict(k=k, counts=by[k]["counts"], true=pick(by[k], "real", "true")[0]) for k in sorted(by)]
    for r in rows:
        r["ok"] = r["true"]["G"] >= GAIN_BAR
    n = sum(r["ok"] for r in rows)
    return rows, n, n >= 16


def start(mode, path, kill_run=None):
    seal = seal_check(); why, fm = a4()
    if kill_run is not None and (seal["code_sha256"] != kill_run.get("code_sha256")
                                 or seal["prereg_sha256"] != kill_run.get("prereg_sha256")):
        why.append("run.py or the prereg changed since `kill`")
    if not seal["sealed"]:
        why.append("the prereg on disk is not the sealed lift_score prereg (sha256 not in HASHES.txt)")
    if why:
        print("A4: do not start:", "; ".join(why)); sys.exit(2)      # nothing computed, nothing written
    out = dict(prereg=PREREG, mode=mode, status="running", nwork=NWORK, base=BASE, **seal,
               note_2027=R_2027, indus=R_INDUS, A4=dict(free_mem_frac=fm, failures=why), fallbacks={})
    dump(out, path)
    return out


# ------------------------------------------------------------------ modes
def kill():
    path, tpath = HERE / "kill.json", HERE / "k1_targets.json"
    if path.exists() or tpath.exists():
        sys.exit("kill.json or k1_targets.json exists: no rerun after any gain is seen (prereg Aborts). If its status "
                 "shows a stop before K0, nothing was scored; that is for the coordinator to judge, not this script.")
    out = start("kill", path)
    t0 = time.time(); sealed = sealed_r1()

    # ---- A1: sealed R1 true IC and N1 mean, draws 1-3, to 1e-9
    a1 = run_jobs(job_a1, [1, 2, 3])
    for r in a1:
        r["d_true"] = abs(r["true_ic"] - sealed[r["k"]]["true_ic"]); r["d_n1"] = abs(r["n1_mean"] - sealed[r["k"]]["n1_mean"])
    out["A1"] = dict(draws=a1, passed=all(r["d_true"] <= A1_TOL and r["d_n1"] <= A1_TOL for r in a1))
    if not out["A1"]["passed"]:
        stop(out, path, "A1: study code does not reproduce sealed R1 true IC / N1 mean (draws 1-3) to 1e-9")

    # ---- A2 + F4: label-free clean counts, draws 1-20
    g = run_jobs(job_gate, list(range(1, NDRAW + 1)))
    mc = statistics.median(r["clean_positions"] for r in g)
    # PREREG-AMBIGUITY: "differ from 1,376 by more than 5%" read as relative: |median / 1376 - 1| > 0.05.
    a2_ok = abs(mc / GATE_CLEAN - 1) <= GATE_TOL
    out["A2"] = dict(draws=g, median_clean=mc, passed=a2_ok)
    out["fallbacks"]["F4"] = dict(thin_draws_flagged=[r["k"] for r in g if r["thin"]], median_clean=mc, abort=mc < F4_MIN)
    if mc < F4_MIN:
        stop(out, path, "A3 (F4): median clean positions below 900: abort")
    if not a2_ok:
        stop(out, path, "A2: recomputed median clean positions differ from 1,376 by more than 5%: stop and redraft")
    say("A1 A2", a1=out["A1"]["passed"], median_clean=mc, thin=out["fallbacks"]["F4"]["thin_draws_flagged"])

    # ---- F3: trigram-only Hit@1 on the K0 plant, before any K0 gain
    nsub = SUBLEX
    f3 = run_jobs(job_k0_trigram, [(k, nsub) for k in range(1, NK0 + 1)])
    f3_hit = any(r["trigram_hit1"] > F3_MAX for r in f3)
    out["fallbacks"]["F3"] = dict(check=f3, applied=f3_hit)
    if f3_hit:
        nsub = SUBLEX_F3                              # applied once; K0 is rebuilt; also applies to K1
        out["fallbacks"]["F3"]["after"] = run_jobs(job_k0_trigram, [(k, nsub) for k in range(1, NK0 + 1)])
    out["sublex"] = nsub

    # ---- A6: window model sums to 1 (fitted K0 draw-1 model); sees no gain
    a6 = run_jobs(job_a6, [nsub])[0]
    out["A6"] = dict(a6, passed=a6["max_dev"] <= A6_TOL)
    dump(out, path)
    if not out["A6"]["passed"]:
        stop(out, path, "A6: the window model does not sum to 1 (to 1e-9) over strings of 1 to 4 consonants")
    say("F3 A6", trigram_hit1=[round(r["trigram_hit1"], 1) for r in f3], f3_applied=f3_hit, a6_max_dev=a6["max_dev"])

    # ---- K0 (first kill test): planted, full dose, draws 1-5, original grid
    # PREREG-AMBIGUITY: the N1 keys are scored on the plant itself (not on its scramble), each with its own word model
    # and λ*, as in lift_certify K0. The five letter-permuted-lexicon cells of the K0 row of the cell table are
    # computed in this same stage, before K0 is graded; they are record-only and enter no K0 bar.
    grid = GRID0
    jobs = [j for k in range(1, NK0 + 1)
            for j in cell_jobs(k, "plant", nsub, grid, ["true", "perm", "n1"]) + cell_jobs(k, "plant_scr", nsub, grid, ["true"])]
    by = gather(run_jobs(job_cells, jobs)); rows = []
    for k in sorted(by):
        row = control_row(k, by[k], "plant")
        row.update(plant=by[k]["plant"], true=pick(by[k], "plant", "true")[0])
        row["ok_true"] = row["true"]["G"] >= K0_GAIN
        rows.append(row)
    miss_gain = not all(r["ok_true"] for r in rows)
    miss_ctrl = not all(r["ok_scramble"] and r["ok_n1"] for r in rows)
    k0_pass = not (miss_gain or miss_ctrl)
    out["K0"] = dict(grid=grid, draws=rows, passed=k0_pass,
                     bars=dict(true_ok=sum(r["ok_true"] for r in rows), scramble_ok=sum(r["ok_scramble"] for r in rows),
                               n1_ok=sum(r["ok_n1"] for r in rows), needed=NK0))
    say("K0", passed=k0_pass, true_G=[round(r["true"]["G"], 4) for r in rows],
        true_hit1_lift=[round(r["true"]["hit1_lift"], 2) for r in rows], true_lam=[r["true"]["lam"] for r in rows],
        scramble_G=[round(r["scramble_true"]["G"], 4) for r in rows], n1_median_G=[round(r["n1_median_G"], 4) for r in rows],
        perm_max_G=[round(r["perm_max_G"], 4) for r in rows])
    if not k0_pass:
        bar = " and ".join(b for b, m in (("gain", miss_gain), ("control", miss_ctrl)) if m)
        out["reading"] = R_K0_FAIL.format(bar="bar missed: " + bar)
        out["route"] = "closed for this corpus size (one-attempt rule); the line moves to certify_size_curve"
        stop(out, path, "K0 fail. " + out["reading"] + " Nothing else runs.")
    dump(out, path)

    # ---- F1: grid edge, decided at K0 on planted text; K0 is not regraded
    n4 = sum(r["true"]["lam"] == 4.0 for r in rows)
    f1 = n4 >= 3
    out["fallbacks"]["F1"] = dict(true_lam4_draws=n4, applied=f1)
    if f1:
        grid = GRID0 + GRID_F1                        # for every key in every later cell
    out["grid"] = grid

    # ---- K1: dose targets first (the first real-text number), all 20 on disk before any K1 plant is built or scored
    tg = sorted(run_jobs(job_target, list(range(1, NDRAW + 1))), key=lambda r: r["k"])
    dump(dict(prereg=PREREG, what="K1 dose targets: D of the true key on the real development half; written before "
              "any K1 plant gain is computed", written_unix=time.time(), targets=tg), tpath)
    assert len(json.load(open(tpath))["targets"]) == NDRAW
    target = {r["k"]: r["D"] for r in tg}
    out["K1"] = dict(targets=tg, targets_file="k1_targets.json"); dump(out, path)
    say("K1 targets written", D=[round(r["D"], 4) for r in tg])

    # ---- K1 build: F2 end points and the D-only bisection (no gain is computed here)
    kb = sorted(run_jobs(job_k1, [dict(phase="build", k=k, nsub=nsub, target=target[k]) for k in range(1, NDRAW + 1)]),
                key=lambda r: r["k"])
    nb = sum(r["built"] for r in kb)
    # PREREG-AMBIGUITY (bears on K1): a "no dose above filler" draw is a built draw that counts as a miss (it is in
    # the denominator and no gain is computed for it); a "real text richer than the full plant" draw is scored at
    # w = 1 and graded like any other; only "not landed in 12 steps" draws are unbuilt and leave the denominator.
    out["fallbacks"]["F2"] = dict(unbuilt=[r["k"] for r in kb if not r["built"]],
                                  no_dose_above_filler=[r["k"] for r in kb if r["status"] == "no dose above filler"],
                                  richer_than_full_plant=[r["k"] for r in kb if r["status"].startswith("real text richer")],
                                  built=nb, abort=nb < 18)
    out["K1"].update(build=kb, built=nb); dump(out, path)
    say("K1 build", built=nb, status=[r["status"] for r in kb], w=[r["w"] for r in kb])
    if nb < 18:
        stop(out, path, "A3 (F2): fewer than 18 of 20 K1 draws built: abort")

    # ---- K1 gains
    k1 = run_jobs(job_k1, [dict(phase="gain", k=r["k"], nsub=nsub, target=target[r["k"]], grid=grid, w=r["w"], D=r["D"])
                           for r in kb if r["scored"]])
    gain = {r["k"]: r for r in k1}; rows = []
    for r in kb:
        row = dict(k=r["k"], status=r["status"], built=r["built"], target=r["target"], w=r["w"], D=r["D"])
        if r["k"] in gain:
            row.update(gain[r["k"]]); row["ok"] = row["true"]["G"] >= GAIN_BAR
        else:
            row["ok"] = False
        rows.append(row)
    need = (4 * nb + 4) // 5                          # >= 80% of built draws, rounded up (16 of 20 when all built)
    passes = sum(r["ok"] for r in rows if r["built"])
    k1_pass = passes >= need
    out["K1"].update(draws=rows, passes=passes, needed=need, passed=k1_pass)
    say("K1", passed=k1_pass, passes=passes, needed=need, G=[round(r["true"]["G"], 4) if "true" in r else None for r in rows],
        hit1_lift=[round(r["true"]["hit1_lift"], 2) if "true" in r else None for r in rows])
    if k1_pass:
        out.update(status="done", full_may_run=True, seconds=round(time.time() - t0, 1))
        dump(out, path); print("K0 and K1 passed; `full` (K2, K3, K4) may run", flush=True)
        return

    # ---- K1 failed: unpowered; the route rule applies. K2 and K3 run once, record-only. K4 does not run.
    out["reading"] = R_K1_FAIL + " K2 and K3 run once, record-only. The line moves to certify_size_curve."
    out["route"] = "closed for this corpus size (one-attempt rule); the line moves to certify_size_curve"
    out["full_may_run"] = False
    dump(out, path)
    rows, ns, nn, k2_ok = real_controls(nsub, grid)
    out["K2"] = dict(draws=rows, scramble_ok=ns, n1_ok=nn, graded=False, passed=None, record_only=True,
                     would_meet_bars=k2_ok)
    dump(out, path)
    rows3, n3, k3_ok = real_true(nsub, grid)
    out["K3"] = dict(draws=rows3, passes=n3, graded=False, passed=None, record_only=True, would_meet_bar=k3_ok)
    if k3_ok:
        out["K3"]["note"] = R_K1_K3_NOTE + "; the route stays closed and the K1-fails reading stands"
    say("K2 K3 record-only", scramble_ok=ns, n1_ok=nn, k3_G=[round(r["true"]["G"], 4) for r in rows3],
        k3_hit1_lift=[round(r["true"]["hit1_lift"], 2) for r in rows3])
    out.update(status="done", seconds=round(time.time() - t0, 1))
    dump(out, path); print("K1 failed: unpowered; K2 and K3 recorded only. K4 does not run.", flush=True); sys.exit(1)


def full():
    kp, path = HERE / "kill.json", HERE / "full.json"
    if not kp.exists():
        sys.exit("kill.json missing: run `kill` first")
    kr = json.load(open(kp))
    if not (kr.get("full_may_run") is True and kr.get("status") == "done" and kr["K0"]["passed"] is True
            and kr["K1"]["passed"] is True):
        sys.exit("kill.json does not show K0 and K1 passed: K2-K4 refused (after a K1 fail they were run record-only)")
    if path.exists():
        sys.exit("full.json exists: no rerun after any gain is seen (prereg Aborts)")
    out = start("full", path, kill_run=kr)
    t0 = time.time(); sealed = sealed_r1(); grid = tuple(float(x) for x in kr["grid"]); nsub = kr["sublex"]
    out.update(grid=grid, fallbacks=kr["fallbacks"])

    # ---- K2: real text, negative controls (K1 passed, so graded)
    rows2, ns, nn, k2_pass = real_controls(nsub, grid)
    out["K2"] = dict(draws=rows2, scramble_ok=ns, n1_ok=nn, graded=True, passed=k2_pass)
    say("K2", passed=k2_pass, scramble_ok=ns, n1_ok=nn, n1_median_G=[round(r["n1_median_G"], 4) for r in rows2],
        n1_median_hit1_lift=[round(r["n1_median_hit1_lift"], 2) for r in rows2])
    if not k2_pass:
        out["reading"] = R_K2_FAIL
        stop(out, path, "K2 fail (K1 passed): " + R_K2_FAIL + " Nothing else runs.")
    dump(out, path)

    # ---- K3: the true key on real text
    rows3, n3, k3_pass = real_true(nsub, grid)
    out["K3"] = dict(draws=rows3, passes=n3, graded=True, passed=k3_pass)
    say("K3", passed=k3_pass, passes=n3, G=[round(r["true"]["G"], 4) for r in rows3],
        hit1_lift=[round(r["true"]["hit1_lift"], 2) for r in rows3])
    if not k3_pass:
        out["reading"] = R_K3_FAIL
        stop(out, path, "K3 fail: no certify by prediction with this score. " + R_K3_FAIL)
    dump(out, path)

    # ---- K4: keys fitted to noise (K1, K2, K3 all passed)
    r2 = sorted(run_jobs(job_k4_n2, [dict(k=k, grid=grid, sealed_n2=sealed[k]["n2"]) for k in range(1, NDRAW + 1)]),
                key=lambda r: r["k"])
    bad = [r["k"] for r in r2 if r["n2"] is None]
    if bad:
        out["K4"] = dict(n2_ic_maxdiff=[r["n2_ic_maxdiff"] for r in r2])
        stop(out, path, f"N2 replay does not reproduce the sealed N2 IC (draws {bad}); no noise key was scored")
    r3 = sorted(run_jobs(job_k4_n3, [dict(k=k, grid=grid) for k in range(1, NDRAW + 1)]), key=lambda r: r["k"])
    true_g = {r["k"]: r["true"]["G"] for r in rows3}; perm_max = {r["k"]: r["perm_max_G"] for r in rows2}
    rows = []
    for a, b in zip(r2, r3):
        k = a["k"]; assert b["k"] == k
        n2g = [e["G"] for e in a["n2"]]; n3g = [e["G"] for e in b["n3"]]
        mean_n2 = sum(n2g) / len(n2g); mx = max(n2g + n3g)
        rows.append(dict(k=k, counts=a["counts"], n2=a["n2"], n3=b["n3"], n2_mean_G=mean_n2, noise_max_G=mx,
                         true_G=true_g[k], perm_max_G=perm_max[k],
                         ok_A=mean_n2 <= CTRL_BAR, ok_B=true_g[k] > mx, ok_C=true_g[k] > perm_max[k]))
    na, nb, nc = (sum(r[q] for r in rows) for q in ("ok_A", "ok_B", "ok_C"))
    bar_a, bar_b, bar_c = na >= 16, nb >= 16, nc >= 16
    certify = bool(k3_pass and bar_a and bar_b and bar_c)
    if certify:
        reading = R_ALL_PASS + " " + R_INDUS
    elif not (bar_a and bar_b):
        reading = R_AB_FAIL
    else:
        reading = R_C_FAIL
    out["K4"] = dict(draws=rows, bar_A=dict(passes=na, passed=bar_a), bar_B=dict(passes=nb, passed=bar_b),
                     bar_C=dict(passes=nc, passed=bar_c))
    out.update(certify_by_gain=certify, reading=reading, status="done", seconds=round(time.time() - t0, 1))
    dump(out, path)
    say("K4", bar_A=out["K4"]["bar_A"], bar_B=out["K4"]["bar_B"], bar_C=out["K4"]["bar_C"], certify_by_gain=certify,
        noise_median_hit1_lift=med(e["hit1_lift"] for r in rows for e in r["n2"] + r["n3"]))
    print(reading, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("kill", "full"):
        sys.exit("usage: run.py kill|full   (under board/run.sh)")
    a5_hook(); load_sealed()
    kill() if mode == "kill" else full()
