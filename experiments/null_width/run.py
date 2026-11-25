"""Null width: which label-free text properties set the width of the shuffle null, and what width does M77's shape
imply? (prereg docs/prereg/null_width.md, SEALED v3).

Run (from the repo root, under the Indus compute lock; A5 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/null_width/run.py kill    # K0, K1 (+F0, F1), K2        -> kill.json
  board/run.sh .venv/bin/python -I experiments/null_width/run.py fit     # fit cells, F2, F3, K3       -> predictions.json
      (STOP: the coordinator commits predictions.json and adds its sha256 to docs/prereg/HASHES.txt)
  board/run.sh .venv/bin/python -I experiments/null_width/run.py blind   # LD1, LD2, V1, V2: K4, K5    -> blind.json
  board/run.sh .venv/bin/python -I experiments/null_width/run.py m77     # label-free M77 step         -> m77.json
Workers: env NWORK (default 4, capped at 4 by the sealed ur3_legend_refute module).

Order. The prereg's order is K0, K1 (F0 and F1 applied, form frozen), K2, then the fit (F2, F3), then K3, K4, K5, then
the M77 step. K3 grades the *fitted* predictor, so it cannot run before the fit: it runs in `fit`, after F2 and F3,
on label-free properties only (its targets are sealed widths; no IC is computed for K3). `kill` therefore holds K0, K1
and K2 only. Every mode refuses to overwrite its own output and refuses unless the previous mode passed.

Reuse (by path, not copied): build, lexicons, tokens, chunking, the scored job (N1, scramble, seeds), A5 lock and memory
checks are the sealed experiments/ur3_legend_refute/run.py; the scorer (IC, classes, permute_in_class_bins, unigram) is
the sealed lb_shape_ladder module reached through it; excess is the sealed lb_formula_dial function. The `m77` mode
imports none of these modules: it runs the sealed `excess` and A5 functions by extracting their source from the
sealed files with `ast` (no module-level code of those files runs, so no scorer is imported; A6). Where the prereg is
silent, extraction follows the label-free scratch scripts the frozen tables came from (gate1-gate4.py); those places
are marked "as scratch".
"""
import ast, hashlib, json, math, os, random, re, subprocess, sys, time, zlib
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PREREG = "docs/prereg/null_width.md"
HASHES = ROOT / "docs/prereg/HASHES.txt"
UR3 = ROOT / "experiments/ur3_legend_refute"
FDIAL = ROOT / "experiments/lb_formula_dial/run.py"
P_KILL, P_PRED, P_BLIND, P_M77 = (HERE / n for n in ("kill.json", "predictions.json", "blind.json", "m77.json"))

BASE = 20261130                                       # study base
NFIT, NSUB = 10, 20
LMIN = 3
K0_DRAWS = (1, 2, 3)
K0_TOL = 1e-9
K2_BAR, K2_MIN_BUILT = 0.052, 16
F0_MIN = 8                                            # of 10
VIF_MAX = 5.0
F2_BAR, F3_BAR = 0.18, 0.10
TOL15 = 0.14                                          # "within 15%" = |ln ratio| <= 0.14 (K3's own definition)
BAND = 1.15
K4_MIN, K5_MIN = 12, 16
PHAT_TOL = 3
CTRL_MAX = 1
A2_REL, A2_E = 0.05, 0.01
NBOOT = 2000
Q1_EFFECT = 0.10
RANGE_TOL = 0.10
D_M77 = 0.180
TAU_LO, TAU_HI, TAU_STEPS = 0.0, 12.0, 30
SEALED_SIGNALS = dict(administrative=0.059, legends=0.085, linear_b=0.051)
K3_TARGET = dict(W_scr=0.085, W_real=0.111)           # L1, sealed medians as stated in the prereg
L2_SEALED = dict(W_scr=0.086, W_real=0.113)
LB_SEALED = dict(W_scr=0.025, W_real=0.031)

# ------------------------------------------------------------------ cells (dial table order = tilt seed index)
CELLS = ("M1", "M2", "M3", "M4", "Hs1", "Ex1", "Ex2", "Nq", "Nh", "N2", "S3", "S2", "Dq", "Dh", "Dp", "T432", "T300",
         "LD1", "LD2")
LABEL = {"Nq": "N¼", "Nh": "N½", "Dq": "D¼", "Dh": "D½", "Dp": "D+"}
# PREREG-AMBIGUITY: "base + 100,000 + 1000k + cell index (cells in the order of the dial table, then LD1, LD2)". The
# index is read as the 1-based position in that list (M1 = 1 ... T300 = 17, LD1 = 18, LD2 = 19); A0 is F0, untilted.
CELL_INDEX = {c: i + 1 for i, c in enumerate(CELLS)}
FIT = ("A0",) + CELLS[:17]
DIAL = dict(M1="M", M2="M", M3="M", M4="M", Hs1="Hs", Ex1="Ex", Ex2="Ex", Nq="N", Nh="N", N2="N", S3="S", S2="S",
            Dq="D", Dh="D", Dp="D", T432="T", T300="T")
# PREREG-AMBIGUITY: "if a dial loses all its cells, its term is dropped". Dial -> term read as M->C, S->G (segment
# length is the dial on the readable share), D->D, N->N, T->T, Ex->E (stage 2); Hs has no predictor term.
TERM_OF_DIAL = dict(M="C", S="G", D="D", N="N", T="T", Ex="E", Hs=None)
STAGE1 = ("C", "G", "D", "N", "T")
# tilt: cell -> (chunk statistic, target, tolerance, sign of tau)
TILT = {"M1": ("M", 0.0132, 0.0005, 1), "M2": ("M", 0.0200, 0.0008, 1), "M3": ("M", 0.0319, 0.0008, 1),
        "M4": ("M", 0.0462, 0.0012, 1), "Hs1": ("Hs", 0.0262, 0.0005, 1),
        "Ex1": ("Ex", 0.210, 0.005, 1), "Ex2": ("Ex", 0.255, 0.005, 1),
        "LD1": ("Hs", 0.0188, 0.0005, -1), "LD2": ("Hs", 0.0113, 0.0005, -1)}
LEX_OF = {"Dq": "ob_quarter", "Dh": "ob_half", "Dp": "spelled_all"}
T_KEEP = {"T432": 432, "T300": 300}
# Draws built per cell. Fit cells use draws 1-10. Cells the second table marks 19/20 or 20/20 are built on 20 draws for
# A2; M2 and M3 also feed V1, V2 and K2; LD1, LD2, V1, V2 have 20 draws.
GATE20 = ("A0", "M3", "M2", "Hs1", "Nh", "Nq", "S3", "S2", "T432", "T300")
N_DRAWS = {c: (NSUB if c in GATE20 or c in ("LD1", "LD2", "V1", "V2") else NFIT) for c in ("A0",) + CELLS + ("V1", "V2")}

# ------------------------------------------------------------------ frozen tables
# First "Measured" table (A2 gates G, C, H, T, N at 5% and E at 0.01; other columns reported).
T1 = {"A0": dict(H=0.0113, T=508, C=0.091, G=0.885, N=4450, E=0.164),
      "Awhole": dict(H=0.0109, T=499, C=0.091, G=0.914, N=4519, E=0.161),
      "L1": dict(H=0.0262, T=433, C=0.179, G=0.932, N=6020, E=0.255),
      "L2": dict(H=0.0254, T=436, C=0.176, G=0.988, N=6001, E=0.252),
      "LB": dict(H=0.0243, T=73, C=0.157, G=0.355, N=2797, E=0.127),
      "M77_4014": dict(H=0.0221, T=309, E=0.159),
      "M77_all": dict(H=0.0222, T=395, E=0.162)}
# Second table, reported beside the recount (only the build counts of the 19/20 and 20/20 rows gate, A2).
T2 = {"A0": dict(H=0.0113, C=0.091, G=0.885, T=508, E=0.164, coverage=0.986),
      "M3": dict(H=0.0255, C=0.179, G=0.848, T=461, E=0.226, coverage=0.972),
      "M2": dict(H=0.0187, C=0.142, G=0.867, T=479, E=0.200, coverage=0.978),
      "Hs1": dict(H=0.0263, C=0.126, G=0.837, T=475, E=0.196, coverage=0.989),
      "Ex2": dict(H=0.0139, C=0.101, G=0.882, T=489, E=0.253, coverage=0.988),
      "Ex1": dict(H=0.0127, C=0.095, G=0.883, T=495, E=0.211, coverage=0.988),
      "Nh": dict(H=0.0116, C=0.093, G=0.887, T=469, E=0.152, coverage=0.985),
      "Nq": dict(H=0.0117, C=0.094, G=0.889, T=445, E=0.151, coverage=0.985),
      "S3": dict(H=0.0115, C=0.092, G=0.820, T=504, E=0.175, coverage=0.986),
      "S2": dict(H=0.0119, C=0.094, G=0.632, T=498, E=0.195, coverage=0.986),
      "T432": dict(H=0.0117, C=0.093, G=0.867, T=432, E=0.164, coverage=0.966),
      "T300": dict(H=0.0123, C=0.097, G=0.847, T=300, E=0.164, coverage=0.943),
      "LD1": dict(H=0.0187, C=0.152, G=0.924, T=450, E=0.235, coverage=0.969),
      "LD2": dict(H=0.0112, C=0.109, G=0.909, T=467, E=0.217, coverage=0.953)}

# ------------------------------------------------------------------ frozen readings
R_K2_FAIL = ("Raising consonant-mass concentration on administrative text to the legend level does not widen the "
             "scrambled null half-way. Concentration does not account for the legends' wider null.")
R_NOPRED = "These properties do not predict W across the dials to a log residual of 0.18."
R_K3_FAIL = ("A predictor built on administrative dials does not reach the legends' width. The form, or a property "
             "other than C, G, D, N, T and E, is responsible.")
R_K4_FAIL = "The predictor matches the legends at their own shape but not when they are moved. Not shown to be general."
R_K5_FAIL = "Width is predicted; pass or fail is not."
R_ALL = ("The shuffle null's width on the Ur III benches tracks {props} and can be predicted from label-free shape to "
         "within 15%. On M77's shape the predicted width is {w}; {smin_clause}. Signal rose with width on the read "
         "texts, so the signals listed are not a forecast for M77.")
R_SMIN = ("a true key would need a signal of at least {s} on this bench (token IC, N1, a cuneiform-like lexicon at "
          "density 0.18, LMIN 3, under the flat shape)")
R_NO_SMIN = "no minimum signal is stated"
R_LB = "Linear B is an extrapolation and sets no scope. Its predicted and sealed widths are reported and change no reading."
R_K3_KNOWN = "K3 is a known-answer check, not a blind one: its targets were seen and helped choose the form."
R_INDUS = ("No reading says anything about any Indus key. A predicted W above the signals seen so far would say that "
           "fit-refute lacks stated power at M77's shape on this bench. It would not say any key is wrong.")


# ------------------------------------------------------------------ sealed code by path
def extract(path, names, ns):
    """Run only the named top-level functions and assignments of a sealed file (no other module code runs)."""
    tree = ast.parse(path.read_text(encoding="utf-8")); body, found = [], set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            body.append(node); found.add(node.name)
        elif isinstance(node, ast.Assign):
            tn = {e.id for t in node.targets for e in (t.elts if isinstance(t, ast.Tuple) else [t])
                  if isinstance(e, ast.Name)}
            if tn & names:
                body.append(node); found |= tn & names
    assert set(names) <= found, f"sealed names missing in {path.name}: {set(names) - found}"
    exec(compile(ast.Module(body=body, type_ignores=[]), path.name, "exec"), ns)
    return ns


def sealed_excess():
    """The sealed lb_formula_dial excess (and S_BASE), without importing lb_formula_dial or the ladder."""
    return extract(FDIAL, {"_flat", "top_share", "excess", "TOPN", "NBASE", "S_BASE"}, {"np": np})


def guard():
    """A5 exactly as sealed ur3_legend_refute (functions run from its source): the compute lock (board/run.sh) is held
    by this process's ancestry, and free memory >= 20%. Nothing is computed or written on failure."""
    ns = extract(UR3 / "run.py", {"_ancestors", "free_mem_frac", "a5", "LOCK", "MEM_GUARD"},
                 dict(os=os, re=re, subprocess=subprocess, sys=sys, ROOT=ROOT))
    why, fm = ns["a5"]()
    if why:
        print("A5: do not start:", "; ".join(why)); sys.exit(2)
    return fm


U = F = L = B = None
SEALED_MODULES = ("ur3_legend_refute_sealed", "formula_dial", "ladder", "run")


def load_sealed():
    """Load sealed ur3_legend_refute by path (it loads lb_formula_dial as F, the ladder scorer as L, lb_certify as B)."""
    global U, F, L, B
    if U is not None:
        return
    import importlib.util
    sys.path.insert(0, str(ROOT / "experiments/lb_certify")); sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("ur3_legend_refute_sealed", UR3 / "run.py")
    U = importlib.util.module_from_spec(spec); sys.modules[spec.name] = U; spec.loader.exec_module(U)
    F, L, B = U.F, U.L, U.B
    assert U.BASE == 20261126 and U.NCHUNK == 2300 and F.S_BASE == 20261129 and L.NPERM == 1000


# ------------------------------------------------------------------ workers (sealed scored job)
def _w_init(lexs):
    load_sealed(); U.init(lexs)


def _w_score(a):
    return U.score_job(a)


def run_jobs(jobs, lexs):
    if not jobs:
        return []
    from multiprocessing import Pool
    with Pool(U.NWORK, initializer=_w_init, initargs=(lexs,)) as P:
        return P.map(_w_score, jobs, chunksize=1)


def slim(r):
    """Per-draw summary kept on disk (no permutation arrays)."""
    return dict(name=r["name"], k=r["k"], tokens_ho=r["tokens_ho"], n_keyed=r["n_keyed"], true_ic=r["true_ic"],
                n1_mean=r["n1_mean"], n1_p99=r["n1_p99"], W_real=r["W"], signal=r["signal"], refute=r["refute"],
                shuffled_true=r["shuffled_true"], shuffled_n1_mean=r["shuffled_n1_mean"],
                shuffled_n1_p99=r["shuffled_n1_p99"], W_scr=r["shuffled_n1_p99"] - r["shuffled_n1_mean"],
                shuffled_refute=r["shuffled_refute"])


# ------------------------------------------------------------------ IO
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


def roundtrip(x):
    return json.loads(json.dumps(x, default=_conv))


def dump(obj, path):
    with open(path, "x") as f:                        # "x": never overwrite an existing output
        json.dump(roundtrip(obj), f, indent=1)


def refuse_if_exists(path):
    if path.exists():
        sys.exit(f"{path.name} exists: no rerun after any IC is seen (prereg Aborts); refused")


def stop(out, path, msg, code=1):
    out.update(passed=False, stop=msg)
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(code)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_seconds(x):
    if isinstance(x, dict):
        return {k: strip_seconds(v) for k, v in x.items() if k != "seconds"}
    if isinstance(x, list):
        return [strip_seconds(v) for v in x]
    return x


def med(xs):
    return float(np.median(xs))


# ------------------------------------------------------------------ data
class Data:
    pass


def load_data():
    """CDLI legends and administrative runs, lexicons and F0 draws exactly as sealed ur3_legend_refute."""
    load_sealed()
    D = Data(); t0 = time.time()
    D.legends, D.aruns, D.mapping = U.load_cdli()
    D.lens = B.m77_lengths()
    lx = U.build_lexicons()
    ob = lx["ob_spelled"]
    # Lexicon thinning: CRC32 of the skeleton's letters joined as text; no seed. Kept if mod 4 is 0 (D¼) or below 2 (D½).
    crc = lambda s: zlib.crc32("".join(s).encode("utf-8")) % 4
    D.lexs = dict(ob_spelled=ob, ob_quarter={s for s in ob if crc(s) == 0}, ob_half={s for s in ob if crc(s) < 2},
                  spelled_all=lx["spelled_all"])
    D.dens = {nm: float(U.density(v, 14)[0][LMIN]) for nm, v in D.lexs.items()}
    D.skel = {nm: len(v) for nm, v in D.lexs.items()}
    homer_q = {t for t in B.build_lexicon()[0] if "q" not in t}
    # PREREG-AMBIGUITY: Linear B's D is read as the sealed table's lexicon density at LMIN 4 (Homer, q-free, over 9^4).
    D.dens_lb = float(U.density(homer_q, 9)[0][4])
    D.adm = {k: trace_build(D.aruns, k, D.lens, U.NCHUNK) for k in range(1, NSUB + 1)}
    D.leg = {k: trace_build(D.legends, k, D.lens, U.NCHUNK) for k in range(1, NSUB + 1)}
    for lab, units in (("adm", D.aruns), ("leg", D.legends)):
        for k in range(1, NSUB + 1):
            dev, ho, built = U.build(units, k, "chunk", D.lens)
            t = getattr(D, lab)[k]
            assert [[u] for u in t[0]] == dev and [[u] for u in t[1]] == ho and t[2] == built, \
                "re-traced build differs from sealed ur3_legend_refute build"
    D.seconds = round(time.time() - t0, 1)
    return D


def trace_build(units, k, lens, nchunk):
    """Sealed ur3_legend_refute build(units, k, 'chunk'), re-traced to also return the dev text ids and to allow
    N2's 4,600 chunks (same draw seed). Returns dev units, held-out units, built, dev ids."""
    rng_np = np.random.default_rng(U.BASE + 1000 * k); rng = random.Random(U.BASE + 1000 * k)
    ch = B.chunk(units, lens, rng_np)
    built = len(ch) >= nchunk
    pick = rng_np.choice(len(ch), size=min(nchunk, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    ids = sorted({tid for tid, _ in ch}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    dev = [t for tid, t in ch if tid in dev_ids]; ho = [t for tid, t in ch if tid not in dev_ids]
    return dev, ho, built, dev_ids


_V = {}


def uval(s):
    """Ur III true key: a keyed sign's consonants (determinative: empty); None if the sign is not keyed (a break)."""
    if s not in _V:
        _V[s] = tuple(U.value(s)) if U.keyed(s) else None
    return _V[s]


def restricted(keep):
    return lambda s: uval(s) if s in keep else None


def lbval(s):
    return tuple(B.true_value(s))


def seed_n1(k):
    return U.BASE + 1000 * k + 7                      # sealed ur3_job N1 seed for draw k


# ------------------------------------------------------------------ properties (label-free)
def bins_u(freq, vals, rng):
    """u_s as (bin-mates holding s's value, bin size), with the bins N1 uses: kept order as sealed (sorted, shuffled by
    the draw's N1 generator), consonant-count classes, sorted by dev + held-out frequency, bins of 10."""
    # PREREG-AMBIGUITY: "bins ... as N1 uses them" read literally: ties in frequency fall as in N1 (kept order from the
    # N1 seed), not in dictionary order as the scratch count did.
    kept = U._kept(freq, rng)
    cl = L.classes(kept, vals)
    u = {}
    for ss in cl.values():
        ss = sorted(ss, key=lambda s: -freq[s])
        for i in range(0, len(ss), 10):
            b = ss[i:i + 10]; vc = Counter(vals[s] for s in b)
            for s in b:
                u[s] = (vc[vals[s]], len(b))
    return u


def conc_C(hof, cc, u):
    M = sum(hof[s] * cc[s] for s in hof)
    return math.sqrt(sum((hof[s] * cc[s] / M) ** 2 * (1 - u[s][0] / u[s][1]) for s in hof)), M


def seg_stats(ho, ccfn, lmin):
    """Keyed consonant segments of held-out units: a keyed sign adds its consonants, anything else breaks."""
    segs = []
    for unit in ho:
        cur = 0
        for s in unit:
            c = ccfn(s)
            if c is None:
                segs.append(cur); cur = 0
            else:
                cur += c
        segs.append(cur)
    segs = [x for x in segs if x]; tc = sum(segs)
    return sum(x for x in segs if x >= lmin) / tc, tc / len(segs), tc


def h_stats(hof):
    n = sum(hof.values()); p = np.array(sorted(hof.values(), reverse=True), dtype=float) / n
    H = float((p ** 2).sum())
    return dict(H=H, eff_types=1 / H, entropy_bits=float(-(p * np.log2(p)).sum()), top10=float(p[:10].sum())), n


def props(dev, ho, val, sn1, lmin, Dv, e_seed, exfn):
    """C, G, D, N, T, E, H (and reported companions) on one draw. dev, ho: lists of units (sign lists)."""
    freq = Counter(s for u in dev + ho for s in u if val(s) is not None)
    hof = Counter(s for u in ho for s in u if val(s) is not None)
    vals = {s: val(s) for s in freq}
    u = bins_u(freq, vals, random.Random(sn1))
    cc = {s: len(v) for s, v in vals.items()}
    C, M = conc_C(hof, cc, u)
    G, cps, tc = seg_stats(ho, lambda s: cc.get(s), lmin)
    assert tc == M
    hs, n = h_stats(hof)
    tok = sum(len(x) for x in ho)
    return dict(C=C, G=G, D=Dv, N=M, T=len(freq), E=float(exfn(ho, e_seed)[0]), cons_per_seg=cps, tokens=tok,
                coverage=n / tok, **hs)


def C2_only(dev, ho, val, sn1):
    freq = Counter(s for u in dev + ho for s in u if val(s) is not None)
    hof = Counter(s for u in ho for s in u if val(s) is not None)
    vals = {s: val(s) for s in freq}
    u = bins_u(freq, vals, random.Random(sn1))
    return conc_C(hof, {s: len(v) for s, v in vals.items()}, u)[0] ** 2


def H_only(ho, val):
    c = Counter(s for u in ho for s in u if val(s) is not None)
    p = np.array(list(c.values()), dtype=float) / sum(c.values())
    return float((p ** 2).sum())


def rank_shape(dev, ho, val, sn1):
    """For the M77 transplant shapes: per frequency rank (dev + held-out, ties by sign name) the consonant count and
    u_s (as bin-mates sharing the value, bin size) of the draw's keyed signs. No sign names or values are kept."""
    freq = Counter(s for u in dev + ho for s in u if val(s) is not None)
    vals = {s: val(s) for s in freq}
    u = bins_u(freq, vals, random.Random(sn1))
    # PREREG-AMBIGUITY: "ties by sign name" read as the reading string, then the token kind.
    order = sorted(freq, key=lambda s: (-freq[s], s[1], s[0]))
    return dict(cc=[len(vals[s]) for s in order], u_num=[u[s][0] for s in order], u_den=[u[s][1] for s in order])


# ------------------------------------------------------------------ dials (label-free)
def make_pool(units, k, dev_ids, lens):
    """All chunks of the texts outside draw k's development half, rechunked with M77 lengths (seed base + 1000k)."""
    flat = [(tid, t) for tid, t in units if tid not in dev_ids]
    return [t for _, t in B.chunk(flat, lens, np.random.default_rng(BASE + 1000 * k))]


def f_mass(pool):
    """Share of the chunk's key consonants on the pool's 10 heaviest signs (consonant mass), as scratch gate3."""
    c = Counter()
    for u in pool:
        for s in u:
            if uval(s) is not None:
                c[s] += len(uval(s))
    top = {s for s, _ in c.most_common(10)}
    return np.array([sum(len(uval(s)) for s in u if s in top) /
                     max(1, sum(len(uval(s)) for s in u if uval(s) is not None)) for u in pool])


def f_sign(pool):
    """Share of the chunk's tokens on the pool's 10 most frequent keyed signs, as scratch gate2."""
    c = Counter(s for u in pool for s in u if uval(s) is not None)
    top = {s for s, _ in c.most_common(10)}
    return np.array([sum(s in top for s in u) / len(u) for u in pool])


def f_pairs(pool):
    """Share of the chunk's pairs in the pool's top 50 (sealed lb_formula_dial tilt_pool measure)."""
    pc = Counter((a, b) for u in pool for a, b in zip(u, u[1:]))
    top = {p for p, _ in pc.most_common(F.TOPN)}
    return np.array([sum((a, b) in top for a, b in zip(u, u[1:])) / (len(u) - 1) for u in pool])


def tilt_draw(ho_units, pool, f, stat, target, tol, sign, seed):
    """Length-stratified weighted draw without replacement matching the held-out length counts, weight exp(sign tau f)
    (as sealed lb_formula_dial tilt_draw); tau bisected on [0, 12], at most 30 steps, seeing only the target."""
    need = Counter(len(u) for u in ho_units)
    plen = np.array([len(u) for u in pool])
    strata = {Lh: np.flatnonzero(plen == Lh) for Lh in need}
    rec = dict(target=target, pool_chunks=len(pool), need_chunks=len(ho_units))
    short = {int(Lh): [int(m), int(len(strata[Lh]))] for Lh, m in need.items() if len(strata[Lh]) < m}
    if short:
        return None, dict(rec, ok=False, why="stratum too small", short=short)
    elog = -np.log(np.random.default_rng(seed).random(len(pool)))

    def draw(tau):
        r = elog / np.exp(sign * tau * f); pick = []
        for Lh, m in need.items():
            ii = strata[Lh]; pick += list(ii[np.argsort(r[ii], kind="stable")[:m]])
        pick.sort()
        return [pool[i] for i in pick]

    lo, hi, v = TAU_LO, TAU_HI, None
    for it in range(1, TAU_STEPS + 1):
        tau = (lo + hi) / 2; units = draw(tau); v = stat(units)
        if abs(v - target) <= tol:
            return units, dict(rec, ok=True, tau=tau, value=v, iterations=it)
        if (v < target) == (sign > 0):
            lo = tau
        else:
            hi = tau
    return None, dict(rec, ok=False, why="no stop within 30 steps", last_tau=tau, last_value=v)


def cut(units, m):
    """Every chunk cut into pieces of at most m signs; 1-sign pieces dropped (as scratch gate2)."""
    return [u[i:i + m] for u in units for i in range(0, len(u), m) if len(u[i:i + m]) >= 2]


# ------------------------------------------------------------------ label-free part (K1; no IC)
def m77_rows(exfn):
    """First table's M77 rows: 20 draws of 4,014 tokens (as sealed m77_target / scratch gate1), and all distinct runs."""
    recs = F.distinct([r for r in F.m77_texts() if r["object_type"] in ("seal", "sealing")])
    texts = [rs for rs in (F.runs(r["seq"]) for r in recs) if rs]
    rng = np.random.default_rng(F.S_BASE); rows = []
    for _ in range(20):
        order = rng.permutation(len(texts)); units, n = [], 0
        for i in order:
            for run_ in texts[i]:
                take = run_[:4014 - n]
                if take:
                    units.append(take); n += len(take)
            if n >= 4014:
                break
        e, _ = exfn(units, int(rng.integers(2 ** 62)))
        hs, _ = h_stats(Counter(s for u in units for s in u))
        rows.append(dict(T=len({s for u in units for s in u}), E=float(e), **hs))
    allu = [r for t in texts for r in t]
    hs, ntok = h_stats(Counter(s for u in allu for s in u))
    a = dict(T=len({s for u in allu for s in u}), E=float(exfn(allu, F.S_BASE)[0]), tokens=ntok, **hs)
    return rows, a


def summarise_props(draws):
    """Median (min, max) of each property over the built draws of a cell."""
    ps = [d["props"] for d in draws.values() if d["built"]]
    if not ps:
        return None
    return {q: [med([p[q] for p in ps]), float(min(p[q] for p in ps)), float(max(p[q] for p in ps))] for q in ps[0]}


def labelfree(D):
    """Builds every cell and both tables, applies A2, F0 and F1. Computes no IC. Returns (K1 block, texts store)."""
    t0 = time.time()
    exfn = F.excess
    cells = {c: {} for c in ("A0",) + CELLS + ("V1", "V2", "L1", "L2", "Awhole", "LB")}
    store = {}

    def put(c, k, built, info, dev=None, ho=None, val=None, lex="ob_spelled", corpus="admin"):
        rec = dict(built=bool(built), **info)
        if built:
            rec["props"] = props(dev, ho, val, seed_n1(k), LMIN, D.dens[lex], F.S_BASE + k, exfn)
            store[(c, k)] = dict(dev=dev, ho=ho, val=val, lex=lex, corpus=corpus)
        cells[c][str(k)] = rec

    for k in range(1, NSUB + 1):
        dA, hA, bA, idsA = D.adm[k]
        dL, hL, bL, idsL = D.leg[k]
        ok_ = lambda c: k <= N_DRAWS[c]
        # PREREG-AMBIGUITY: every dial starts from F0 draw k, so a dial draw is unbuilt when F0 draw k is (N2 has its
        # own build).
        put("A0", k, bA, {}, dA, hA, uval)
        put("L1", k, bL, {}, dL, hL, uval, corpus="legends")
        dW, hW, bW = U.build(D.aruns, k, "line", D.lens)
        put("Awhole", k, bW, {}, [t[0] for t in dW], [t[0] for t in hW], uval)
        dW, hW, bW = U.build(D.legends, k, "line", D.lens)
        put("L2", k, bW, {}, [t[0] for t in dW], [t[0] for t in hW], uval, corpus="legends")
        pool = make_pool(D.aruns, k, idsA, D.lens) if bA else None
        fs = {}
        for c in ("M1", "M2", "M3", "M4", "Hs1", "Ex1", "Ex2"):
            if not ok_(c):
                continue
            if not bA:
                put(c, k, False, dict(why="F0 draw unbuilt")); continue
            kind, target, tol, sign = TILT[c]
            if kind not in fs:
                fs[kind] = dict(M=f_mass, Hs=f_sign, Ex=f_pairs)[kind](pool)
            stat = dict(M=lambda un: C2_only(dA, un, uval, seed_n1(k)),
                        Hs=lambda un: H_only(un, uval),
                        Ex=lambda un: float(exfn(un, F.S_BASE + k)[0]))[kind]
            un, info = tilt_draw(hA, pool, fs[kind], stat, target, tol, sign,
                                 BASE + 100_000 + 1000 * k + CELL_INDEX[c])
            put(c, k, un is not None, info, dA, un, uval)
        for c, fr in (("Nq", 0.25), ("Nh", 0.5)):
            if ok_(c):
                put(c, k, bA, {}, dA, hA[:int(len(hA) * fr)], uval)
        if ok_("N2"):
            d2, h2, b2, _ = trace_build(D.aruns, k, D.lens, 4600)
            put("N2", k, b2, dict(chunks=len(d2) + len(h2)), d2, h2, uval)
        for c, m in (("S3", 3), ("S2", 2)):
            if ok_(c):
                put(c, k, bA, {}, dA, cut(hA, m) if bA else None, uval)
        for c in ("Dq", "Dh", "Dp"):
            if ok_(c):
                put(c, k, bA, {}, dA, hA, uval, lex=LEX_OF[c])
        if bA:
            fr_ = Counter(s for u in dA + hA for s in u if uval(s) is not None)
            order = [s for s, _ in fr_.most_common()]   # top types by dev + held-out frequency, as scratch gate2
        for c, K in T_KEEP.items():
            if ok_(c):
                put(c, k, bA, {}, dA, hA, restricted(set(order[:K])) if bA else None)
        # validation cells: V1 = the M2 draw cut as S3; V2 = the first half of the M3 draw's chunks
        m2, m3 = store.get(("M2", k)), store.get(("M3", k))
        put("V1", k, m2 is not None, {}, dA, cut(m2["ho"], 3) if m2 else None, uval)
        # PREREG-AMBIGUITY: "first half of the M3 draw's chunks" read as its first int(n/2) chunks in drawn (pool) order.
        put("V2", k, m3 is not None, {}, dA, m3["ho"][:int(len(m3["ho"]) * 0.5)] if m3 else None, uval)
        # legends tilted down (K4): pool and tilted draw built from legends as for the dials
        if bL:
            poolL = make_pool(D.legends, k, idsL, D.lens); fL = f_sign(poolL)
        for c in ("LD1", "LD2"):
            if not bL:
                put(c, k, False, dict(why="F0 draw unbuilt"), corpus="legends"); continue
            kind, target, tol, sign = TILT[c]
            un, info = tilt_draw(hL, poolL, fL, lambda x: H_only(x, uval), target, tol, sign,
                                 BASE + 100_000 + 1000 * k + CELL_INDEX[c])
            put(c, k, un is not None, info, dL, un, uval, corpus="legends")
        # Linear B F0 (reported, not graded): sealed lb_shape_ladder R1 draw, Homer N1 seed
        dB, hB, _ = L.build(k, "chunk")
        cells["LB"][str(k)] = dict(built=True, props=props(
            [w for t in dB for w in t], [w for t in hB for w in t], lbval, L.SEED + 1000 * k + 7 * F.R1_INDEX, 4,
            D.dens_lb, F.S_BASE + k, exfn))
    # ---- tables and A2
    summ = {c: dict(built=sum(d["built"] for d in v.values()), of=len(v),
                    built_fit=sum(d["built"] for kk, d in v.items() if int(kk) <= NFIT), medians=summarise_props(v))
            for c, v in cells.items()}
    m77_draws, m77_all = m77_rows(exfn)
    first = {c: summ[c]["medians"] for c in ("A0", "Awhole", "L1", "L2", "LB")}
    first["M77_4014"] = {q: [med([r[q] for r in m77_draws])] for q in m77_draws[0]}
    first["M77_all"] = {q: [v] for q, v in m77_all.items()}
    fails = []
    for row, tv in T1.items():
        got = first[row]
        if got is None:
            fails.append(f"{row}: no draw built"); continue
        for q, v in tv.items():
            g = got[q][0]
            bad = abs(g - v) > A2_E if q == "E" else abs(g - v) > A2_REL * abs(v)
            if bad:
                fails.append(f"{row} {q} = {g:.4f} (table {v})")
    for c in GATE20:
        if summ[c]["built"] < 16:
            fails.append(f"cell {c} built {summ[c]['built']} of {summ[c]['of']} (< 16)")
    # sealed excess run from source (used by the M77 step) equals the imported sealed function
    ns = sealed_excess(); probe = store[("A0", 1)]["ho"] if ("A0", 1) in store else D.adm[1][1]
    ex_same = bool(ns["excess"](probe, F.S_BASE + 1) == exfn(probe, F.S_BASE + 1))
    if not ex_same:
        fails.append("excess extracted from source differs from the imported sealed excess")
    # ---- F0: unbuilt fit cells
    dropped = [c for c in FIT if summ[c]["built_fit"] < F0_MIN]
    a4 = [c for c in ("M2", "M3") if c in dropped]
    kept = [c for c in FIT if c not in dropped]
    not_tested = sorted({TERM_OF_DIAL[DIAL[c]] for c in DIAL if TERM_OF_DIAL[DIAL[c]]}
                        - {TERM_OF_DIAL[DIAL[c]] for c in kept if c in DIAL and TERM_OF_DIAL[DIAL[c]]})
    F0 = dict(built_of_10={c: summ[c]["built_fit"] for c in FIT}, dropped=dropped, kept_cells=kept,
              terms_not_tested=not_tested, A4=a4)
    # ---- F1: collinearity on the stage 1 design matrix (cell medians of label-free properties), form frozen here
    terms = [t for t in STAGE1 if t not in not_tested]
    Z = {t: np.array([math.log(med([d["props"][t] for kk, d in cells[c].items()
                                    if int(kk) <= NFIT and d["built"]])) for c in kept]) for t in terms}
    log, cur = [], list(terms)
    while len(cur) > 1:
        v = vif(np.column_stack([Z[t] for t in cur]))
        vd = dict(zip(cur, v))
        if max(v) <= VIF_MAX:
            log.append(dict(vif=vd, action="all at most 5")); break
        order = sorted(cur, key=lambda t: -vd[t])
        drop = order[0] if order[0] != "C" else order[1]
        rest = [t for t in cur if t != drop]
        # PREREG-AMBIGUITY: a dropped term's "closest partner" read as the remaining term with the largest |correlation|
        # with it across the fit cells' design matrix.
        partner = max(rest, key=lambda t: float(np.nan_to_num(abs(np.corrcoef(Z[drop], Z[t])[0, 1]))))
        log.append(dict(vif=vd, dropped=drop, not_separable_from=partner))
        cur = rest
    if len(cur) == 1:
        log.append(dict(vif={cur[0]: 1.0}, action="single term"))
    F1 = dict(candidate_terms=terms, terms=cur, log=log,
              dropped={e["dropped"]: e["not_separable_from"] for e in log if "dropped" in e},
              E_in_stage2="E" not in not_tested)
    K1 = dict(passed=not fails and not a4, A2_failures=fails, first_table=first, first_table_frozen=T1,
              m77_4014_draws=m77_draws, second_table={c: summ[c] for c in summ}, second_table_frozen=T2,
              cells=cells, lexicon_density_L3=D.dens, lexicon_skeletons=D.skel, density_linear_b_L4=D.dens_lb,
              excess_source_equals_sealed=ex_same, F0=F0, F1=F1, seconds=round(time.time() - t0, 1))
    return roundtrip(K1), store


def vif(Z):
    out = []
    for j in range(Z.shape[1]):
        y = Z[:, j]; X = np.column_stack([np.ones(len(y)), np.delete(Z, j, 1)])
        b, *_ = np.linalg.lstsq(X, y, rcond=None); r = y - X @ b; ss = float(((y - y.mean()) ** 2).sum())
        r2 = 1 - float(r @ r) / ss if ss > 0 else 1.0
        out.append(float("inf") if r2 >= 1 - 1e-15 else 1 / (1 - r2))
    return out


def job(cell, k, store):
    s = store[(cell, k)]
    j = U.ur3_job("cell", cell, k, [[u] for u in s["dev"]], [[u] for u in s["ho"]], s["lex"], LMIN)
    if cell in T_KEEP:                                # only the top types are keyed; the rest are breaks
        j["freq"] = Counter({x: n for x, n in j["freq"].items() if s["val"](x) is not None})
        j["vals"] = {x: v for x, v in j["vals"].items() if x in j["freq"]}
    return j


def check_rebuild(K1, kr_K1):
    assert strip_seconds(K1) == strip_seconds(kr_K1), "label-free rebuild differs from kill.json"


# ------------------------------------------------------------------ predictor (pure; shared with the M77 step)
def predict_draw(p, form):
    ls = form["b"][0] + sum(b * math.log(p[t]) for t, b in zip(form["terms"], form["b"][1:]))
    ws = math.exp(ls); s2 = form["stage2"]
    fac = math.exp(s2["g0"] + s2.get("g1", 0.0) * p["E"]) if s2["kind"] == "linear" else s2["c"]
    return ws, ws * fac


def predict_cell(plist, form):
    pr = [predict_draw(p, form) for p in plist]
    return dict(W_scr_hat=med([a for a, _ in pr]), W_real_hat=med([b for _, b in pr]),
                per_draw=[dict(W_scr_hat=a, W_real_hat=b) for a, b in pr])


def lnr(a, b):
    return abs(math.log(a / b))


# ------------------------------------------------------------------ fit pieces
def cell_points(rows):
    """One point per cell: medians over built draws of ln W_scr, ln(W_real / W_scr) and of each property."""
    # PREREG-AMBIGUITY: "the median over its built draws ... of each property" read as the median of the raw
    # property; the log is taken of that median (ln W uses the median of the logs, as written).
    return dict(lnWs=med([math.log(r["W_scr"]) for r in rows]),
                lnR=med([math.log(r["W_real"] / r["W_scr"]) for r in rows]),
                Ws=med([r["W_scr"] for r in rows]), Wr=med([r["W_real"] for r in rows]),
                R=med([r["W_real"] / r["W_scr"] for r in rows]),
                **{q: med([r["props"][q] for r in rows]) for q in ("C", "G", "D", "N", "T", "E", "H")})


def ols(X, y):
    b, *_ = np.linalg.lstsq(np.asarray(X, float), np.asarray(y, float), rcond=None)
    return [float(x) for x in b]


def fit1(pts, cells, terms):
    X = [[1.0] + [math.log(pts[c][t]) for t in terms] for c in cells]
    return ols(X, [pts[c]["lnWs"] for c in cells])


def fit2(pts, cells, use_E):
    X = [[1.0, pts[c]["E"]] if use_E else [1.0] for c in cells]
    b = ols(X, [pts[c]["lnR"] for c in cells])
    return dict(kind="linear", g0=b[0], **({"g1": b[1]} if use_E else {}))


def do_fit(rows, cells, terms, use_E):
    """Stage 1 and stage 2 on cell medians; LOO residuals; F2 and F3. Returns the fit record and the final form."""
    pts = {c: cell_points(rows[c]) for c in cells}
    b = fit1(pts, cells, terms)
    s2 = fit2(pts, cells, use_E)
    loo = {}
    for c in cells:
        rest = [x for x in cells if x != c]
        fb = fit1(pts, rest, terms); f2 = fit2(pts, rest, use_E)
        form = dict(terms=terms, b=fb, stage2=f2)
        pr = [predict_draw(r["props"], form) for r in rows[c]]
        ws_hat = med([a for a, _ in pr])
        r_hat = med([math.exp(f2["g0"] + f2.get("g1", 0.0) * r["props"]["E"]) for r in rows[c]])
        # PREREG-AMBIGUITY: stage 2's leave-one-cell-out residual read by analogy with stage 1's:
        # |ln(predicted median W_real/W_scr / observed median W_real/W_scr)|.
        loo[c] = dict(stage1=lnr(ws_hat, pts[c]["Ws"]), stage2=lnr(r_hat, pts[c]["R"]))
    f2_max = max(v["stage1"] for v in loo.values()); s2_max = max(v["stage2"] for v in loo.values())
    no_pred = f2_max > F2_BAR
    f3 = bool(use_E and s2["g1"] < 0) or s2_max > F3_BAR
    # PREREG-AMBIGUITY: F3's constant "the median of W_real / W_scr over the fit points" read as the median over fit
    # cells of exp(cell point ln(W_real/W_scr)).
    stage2 = dict(kind="constant", c=med([math.exp(pts[c]["lnR"]) for c in cells])) if f3 else s2
    form = dict(terms=terms, b=b, stage2=stage2)
    fitted = {c: dict(point=pts[c], **{q: v for q, v in predict_cell([r["props"] for r in rows[c]], form).items()
                                       if q != "per_draw"}) for c in cells}
    rec = dict(points=pts, stage1_b=dict(zip(["b0"] + terms, b)), stage2_linear=s2, loo=loo,
               F2=dict(max_loo_stage1=f2_max, bar=F2_BAR, no_predictor=no_pred),
               F3=dict(applied=f3, g1_negative=bool(use_E and s2["g1"] < 0), max_loo_stage2=s2_max, bar=F3_BAR),
               fitted=fitted)
    return rec, form


def bootstrap(rows, cells, terms, form):
    """Coefficient intervals: resample draw index k (1-10) with replacement, recompute every cell median, refit both
    stages in the frozen final form. 2,000 resamples, seed base + 900,000."""
    # PREREG-AMBIGUITY: numpy default_rng(base + 900,000); a resampled index unbuilt in a cell is simply absent from
    # that cell; a cell with no draw left is left out of that resample.
    rng = np.random.default_rng(BASE + 900_000)
    by = {c: {r["k"]: r for r in rows[c]} for c in cells}
    B1, B2 = [], []
    lin = form["stage2"]["kind"] == "linear"; useE = "g1" in form["stage2"]
    for _ in range(NBOOT):
        idx = rng.integers(1, NFIT + 1, size=NFIT)
        rr = {c: [by[c][k] for k in idx if k in by[c]] for c in cells}
        cs = [c for c in cells if rr[c]]
        pts = {c: cell_points(rr[c]) for c in cs}
        B1.append(fit1(pts, cs, terms))
        if lin:
            s = fit2(pts, cs, useE); B2.append([s["g0"]] + ([s["g1"]] if useE else []))
        else:
            B2.append([med([math.exp(pts[c]["lnR"]) for c in cs])])
    ci = lambda col: [float(np.quantile(col, 0.025)), float(np.quantile(col, 0.975))]
    A1, A2 = np.array(B1), np.array(B2)
    out = dict(stage1={n: ci(A1[:, i]) for i, n in enumerate(["b0"] + terms)})
    names = (["g0"] + (["g1"] if useE else [])) if lin else ["c"]
    out["stage2"] = {n: ci(A2[:, i]) for i, n in enumerate(names)}
    return out


def q1(fitrec, form, ci, cells, not_tested, f1_dropped):
    """A property tracks W if its interval excludes 0 and |coefficient| x its dialled log range >= 0.10."""
    pts = fitrec["points"]; out = {}
    for t, b in zip(form["terms"], form["b"][1:]):
        lo, hi = ci["stage1"][t]; xs = [math.log(pts[c][t]) for c in cells]; rng_ = max(xs) - min(xs)
        out[t] = dict(coef=b, ci95=[lo, hi], dialled_log_range=rng_, effect=abs(b) * rng_,
                      tracks=bool((lo > 0 or hi < 0) and abs(b) * rng_ >= Q1_EFFECT))
    if "g1" in form["stage2"]:
        # PREREG-AMBIGUITY: E enters stage 2 linearly; its "dialled log range" is read as its range in E itself.
        lo, hi = ci["stage2"]["g1"]; xs = [pts[c]["E"] for c in cells]; rng_ = max(xs) - min(xs); g1 = form["stage2"]["g1"]
        out["E"] = dict(coef=g1, ci95=[lo, hi], dialled_range=rng_, effect=abs(g1) * rng_,
                        tracks=bool((lo > 0 or hi < 0) and abs(g1) * rng_ >= Q1_EFFECT))
    elif "E" not in not_tested:
        out["E"] = dict(tracks=False, note="stage 2 constant (F3) or without E: not shown to matter in this range")
    for t in not_tested:
        out[t] = dict(tracks=False, note="not tested")
    for t, p in f1_dropped.items():
        out[t] = dict(tracks=False, note=f"not separable from {p}")
    for t, v in out.items():
        v.setdefault("note", "tracks W" if v["tracks"] else "not shown to matter in this range")
    return out


# ------------------------------------------------------------------ modes
def mode_kill():
    refuse_if_exists(P_KILL)
    fm = guard()
    load_sealed()
    out = dict(prereg=PREREG, mode="kill", nwork=U.NWORK, A5=dict(free_mem_frac=fm))
    D = load_data()
    out["data_seconds"] = D.seconds
    # ---- K0: study code reproduces sealed ur3_legend_refute per draw to 1e-9 (A1)
    t0 = time.time()
    s_adm = {r["k"]: r for r in json.load(open(UR3 / "kill.json"))["K3"]["runs"]}
    s_leg = {r["k"]: r for r in json.load(open(UR3 / "full.json"))["runs"] if r["name"] == "L1"}
    jobs = []
    for nm, units, sealed in (("K0_admin", D.aruns, s_adm), ("K0_legends", D.legends, s_leg)):
        for k in K0_DRAWS:
            dev, ho, _ = U.build(units, k, "chunk", D.lens)
            jobs.append(U.ur3_job("cell", nm, k, dev, ho, "ob_spelled", LMIN))
    res = run_jobs(jobs, D.lexs)
    per, ok = [], True
    for r in res:
        s = (s_adm if r["name"] == "K0_admin" else s_leg)[r["k"]]
        d = {q: abs(r[q] - s[q]) for q in ("n1_mean", "n1_p99", "shuffled_n1_mean", "shuffled_n1_p99", "true_ic")}
        mx = max(d.values()); good = mx <= K0_TOL and r["tokens_ho"] == s["tokens_ho"]; ok = ok and good
        per.append(dict(name=r["name"], k=r["k"], max_abs_diff=mx, tokens_equal=r["tokens_ho"] == s["tokens_ho"],
                        match=good))
    out["K0"] = dict(passed=bool(ok), per_draw=per, seconds=round(time.time() - t0, 1))
    print(json.dumps(dict(K0_passed=ok, max_diff=max(p["max_abs_diff"] for p in per))), flush=True)
    if not ok:
        stop(out, P_KILL, "A1: K0 does not reproduce sealed ur3_legend_refute")
    # ---- K1: tables, every cell built, F0 and F1 on label-free counts; form frozen (no IC)
    K1, store = labelfree(D)
    out["K1"] = K1
    print(json.dumps(dict(K1_passed=K1["passed"], A2_failures=K1["A2_failures"], F0=K1["F0"],
                          F1_terms=K1["F1"]["terms"], F1_dropped=K1["F1"]["dropped"],
                          built={c: K1["second_table"][c]["built"] for c in K1["second_table"]}), indent=1),
          flush=True)
    if K1["A2_failures"]:
        stop(out, P_KILL, "A2: a recomputed property or build count differs from the sealed tables; stop and redraft")
    if K1["F0"]["A4"]:
        stop(out, P_KILL, f"A4: {', '.join(K1['F0']['A4'])} dropped under F0")
    # ---- K2: the one-cell kill on M3, 20 draws
    t0 = time.time()
    ks = [int(k) for k, d in K1["cells"]["M3"].items() if d["built"]]
    if len(ks) < K2_MIN_BUILT:
        stop(out, P_KILL, f"A4: M3 builds {len(ks)} of 20 draws at K2 (< 16)")
    rows = [slim(r) for r in run_jobs([job("M3", k, store) for k in sorted(ks)], D.lexs)]
    mW = med([r["W_scr"] for r in rows]); ctrl = sum(r["shuffled_refute"] for r in rows)
    out["K2"] = dict(built=len(ks), median_W_scr=mW, bar=K2_BAR, scrambled_passes=ctrl,
                     median_W_real=med([r["W_real"] for r in rows]), P=sum(r["refute"] for r in rows),
                     passed=bool(mW >= K2_BAR), runs=rows, seconds=round(time.time() - t0, 1))
    print(json.dumps({q: out["K2"][q] for q in ("built", "median_W_scr", "scrambled_passes", "passed")}), flush=True)
    if ctrl > CTRL_MAX:
        stop(out, P_KILL, "A3: scrambled-text control passes in more than 1 of 20 draws in K2")
    if not out["K2"]["passed"]:
        out["reading"] = R_K2_FAIL
        stop(out, P_KILL, "K2 fails: " + R_K2_FAIL + " No fit, no M77 step.")
    out.update(passed=True, kill_passed=True)
    dump(out, P_KILL); print("kill passed; fit may run", flush=True)


def mode_fit():
    refuse_if_exists(P_PRED)
    assert P_KILL.exists(), "kill.json missing: run `kill` first"
    kr = json.load(open(P_KILL))
    assert kr.get("kill_passed") is True and all(kr.get(q, {}).get("passed") is True for q in ("K0", "K1", "K2")), \
        "kill.json does not show K0, K1 and K2 passed: fit refused"
    fm = guard()
    load_sealed(); t0 = time.time()
    D = load_data()
    K1, store = labelfree(D)
    check_rebuild(K1, kr["K1"])
    F0, F1 = K1["F0"], K1["F1"]
    cells = F0["kept_cells"]; terms = F1["terms"]; useE = F1["E_in_stage2"]
    # ---- per-draw rows of every fit cell (draws 1-10): A0 = sealed values; M3 = K2's draws 1-10; others scored now
    props_of = lambda c, k: K1["cells"][c][str(k)]["props"]
    rows = {}
    sealed = {r["k"]: r for r in json.load(open(UR3 / "kill.json"))["K3"]["runs"]}
    rows["A0"] = [dict(k=k, W_real=sealed[k]["W"], W_scr=sealed[k]["shuffled_n1_p99"] - sealed[k]["shuffled_n1_mean"],
                       signal=sealed[k]["signal"], refute=sealed[k]["refute"], props=props_of("A0", k), source="sealed")
                  for k in range(1, NFIT + 1) if K1["cells"]["A0"][str(k)]["built"] and k in sealed]
    rows["M3"] = [dict(r, props=props_of("M3", r["k"]), source="K2") for r in kr["K2"]["runs"] if r["k"] <= NFIT]
    jobs = [job(c, k, store) for c in cells if c not in ("A0", "M3")
            for k in range(1, NFIT + 1) if K1["cells"][c][str(k)]["built"]]
    print(f"fit: scoring {len(jobs)} cell-draws", flush=True)
    for r in run_jobs(jobs, D.lexs):
        rows.setdefault(r["name"], []).append(dict(slim(r), props=props_of(r["name"], r["k"]), source="scored"))
    for c in cells:
        rows[c] = sorted(rows[c], key=lambda r: r["k"])
    out = dict(prereg=PREREG, mode="fit", A5=dict(free_mem_frac=fm), kill_json_sha256=sha256(P_KILL),
               fit_cells=cells, F0=F0, F1=F1, rows={c: rows[c] for c in cells})
    # ---- fit, F2, F3
    fitrec, form = do_fit(rows, cells, terms, useE)
    out["fit"] = fitrec
    if fitrec["F2"]["no_predictor"]:
        out.update(predictor=False, reading=R_NOPRED + " No M77 step.", seconds=round(time.time() - t0, 1))
        dump(out, P_PRED); print("F2: no predictor.", R_NOPRED, flush=True); return
    out["predictor"] = True
    out["form"] = form
    ci = bootstrap(rows, cells, terms, form)
    out["bootstrap_ci95"] = ci
    out["Q1"] = q1(fitrec, form, ci, cells, F0["terms_not_tested"], F1["dropped"])
    # report only: ln sqrt(H) in place of ln C
    pts = fitrec["points"]
    for c in cells:
        pts[c]["sqrtH"] = math.sqrt(pts[c]["H"])
    bH = ols([[1.0] + [math.log(pts[c]["sqrtH"] if t == "C" else pts[c][t]) for t in terms] for c in cells],
             [pts[c]["lnWs"] for c in cells])
    out["sqrtH_in_place_of_C"] = dict(terms=["sqrtH" if t == "C" else t for t in terms], b=bH, note="report only")
    # q80: pooled 80th percentile of W_real,k over its cell median, across the fit cells
    ratios = [r["W_real"] / pts[c]["Wr"] for c in cells for r in rows[c]]
    out["q80"] = float(np.quantile(ratios, 0.8))
    # fit cells' range of cell medians (for the M77 range rule)
    out["fit_ranges"] = {q: [min(pts[c][q] for c in cells), max(pts[c][q] for c in cells)]
                         for q in ("C", "G", "D", "N", "T", "E", "H")}
    # ---- K3: planted known answer, L1 label-free properties -> sealed widths
    pl = lambda c: [d["props"] for d in K1["cells"][c].values() if d["built"]]
    l1 = predict_cell(pl("L1"), form); l2 = predict_cell(pl("L2"), form); lb = predict_cell(pl("LB"), form)
    miss = {q: math.log(l1[q + "_hat"] / K3_TARGET[q]) for q in ("W_scr", "W_real")}
    k3 = all(abs(v) <= TOL15 for v in miss.values())
    sealed_l1 = [r for r in json.load(open(UR3 / "full.json"))["runs"] if r["name"] == "L1"]
    out["K3"] = dict(L1=dict(W_scr_hat=l1["W_scr_hat"], W_real_hat=l1["W_real_hat"], target=K3_TARGET,
                             ln_ratio=miss, n_draws=len(pl("L1")),
                             sealed_medians_recounted=dict(W_scr=med([r["shuffled_n1_p99"] - r["shuffled_n1_mean"]
                                                                      for r in sealed_l1]),
                                                           W_real=med([r["W"] for r in sealed_l1]))),
                     passed=bool(k3), note=R_K3_KNOWN,
                     L2_report=dict(W_scr_hat=l2["W_scr_hat"], W_real_hat=l2["W_real_hat"], sealed=L2_SEALED),
                     linear_b_report=dict(W_scr_hat=lb["W_scr_hat"], W_real_hat=lb["W_real_hat"], sealed=LB_SEALED,
                                          ratio=dict(W_scr=lb["W_scr_hat"] / LB_SEALED["W_scr"],
                                                     W_real=lb["W_real_hat"] / LB_SEALED["W_real"]),
                                          note=R_LB))
    if not k3:
        sign = {q: ("over" if v > 0 else "under") for q, v in miss.items()}
        out["K3"]["reading"] = R_K3_FAIL + f" Miss: {json.dumps(miss)} ({json.dumps(sign)}). No M77 step."
    # ---- blind predictions: LD1, LD2, V1, V2 (label-free properties only), committed and hashed before scoring
    blind = {}
    for c in ("LD1", "LD2", "V1", "V2"):
        ds = [(int(k), d["props"]) for k, d in K1["cells"][c].items() if d["built"]]
        pc = predict_cell([p for _, p in ds], form) if ds else None
        blind[c] = dict(built=len(ds), of=NSUB,
                        W_scr_hat=pc["W_scr_hat"] if pc else None, W_real_hat=pc["W_real_hat"] if pc else None,
                        draws=[dict(k=k, props=p, **pd) for (k, p), pd in zip(ds, pc["per_draw"] if pc else [])])
    out["blind_predictions"] = blind
    # ---- M77 transplant shapes (Sa, Sb; sensitivity only): rank -> consonant count and u_s, no sign names or values
    out["shapes"] = {"Sa": {str(k): rank_shape(D.adm[k][0], D.adm[k][1], uval, seed_n1(k))
                            for k in range(1, NSUB + 1) if D.adm[k][2]},
                     "Sb": {str(k): rank_shape(D.leg[k][0], D.leg[k][1], uval, seed_n1(k))
                            for k in range(1, NSUB + 1) if D.leg[k][2]}}
    out["seconds"] = round(time.time() - t0, 1)
    dump(out, P_PRED)
    print(json.dumps(dict(form=form, F2=fitrec["F2"], F3=fitrec["F3"], K3=dict(passed=k3, L1=out["K3"]["L1"]),
                          Q1={t: v["note"] for t, v in out["Q1"].items()},
                          blind={c: (v["built"], v["W_scr_hat"], v["W_real_hat"]) for c, v in blind.items()}),
                     indent=1, default=_conv), flush=True)
    print("STOP: commit predictions.json and add its sha256 to docs/prereg/HASHES.txt before `blind`.", flush=True)


def mode_blind():
    refuse_if_exists(P_BLIND)
    assert P_PRED.exists(), "predictions.json missing: run `fit` first"
    sha = sha256(P_PRED)
    assert any(l.split()[:1] == [sha] for l in HASHES.read_text().splitlines()), \
        "predictions.json sha256 is not in docs/prereg/HASHES.txt: blind refused"
    pred = json.load(open(P_PRED)); kr = json.load(open(P_KILL))
    assert pred.get("predictor") is True, "no predictor (F2): K3 to K5 are not run"
    # PREREG-AMBIGUITY: the prereg bars K3-K5 only under F2; after a K3 fail it bars only the M77 step. Blind is
    # therefore allowed after a K3 fail, and the K3 reading stands whatever K4 and K5 show.
    fm = guard()
    load_sealed(); t0 = time.time()
    D = load_data()
    K1, store = labelfree(D)
    check_rebuild(K1, kr["K1"])
    bp = pred["blind_predictions"]
    for c in bp:
        now = [dict(k=int(k), props=d["props"]) for k, d in K1["cells"][c].items() if d["built"]]
        assert now == [dict(k=d["k"], props=d["props"]) for d in bp[c]["draws"]], f"{c} differs from predictions.json"
    out = dict(prereg=PREREG, mode="blind", A5=dict(free_mem_frac=fm), predictions_sha256=sha)
    run_c = [c for c in ("LD1", "LD2") if bp[c]["built"] >= K4_MIN] + ["V1", "V2"]
    jobs = [job(c, d["k"], store) for c in run_c for d in bp[c]["draws"]]
    print(f"blind: scoring {len(jobs)} cell-draws", flush=True)
    res = {}
    for r in run_jobs(jobs, D.lexs):
        res.setdefault(r["name"], []).append(slim(r))
    for c in res:
        res[c].sort(key=lambda r: r["k"])
    out["runs"] = res
    # A3 on the validation cells
    ctrl = {c: sum(r["shuffled_refute"] for r in res.get(c, [])) for c in ("V1", "V2")}
    out["scrambled_passes"] = ctrl
    if any(v > CTRL_MAX for v in ctrl.values()):
        stop(out, P_BLIND, "A3: scrambled-text control passes in more than 1 of 20 draws in V1 or V2")
    # K4
    k4 = {}
    for c in ("LD1", "LD2"):
        if c not in res:
            k4[c] = dict(status="not run", built=bp[c]["built"]); continue
        obs = dict(W_scr=med([r["W_scr"] for r in res[c]]), W_real=med([r["W_real"] for r in res[c]]))
        lr = {q: math.log(bp[c][q + "_hat"] / obs[q]) for q in obs}
        k4[c] = dict(status="run", built=bp[c]["built"], observed=obs,
                     predicted=dict(W_scr=bp[c]["W_scr_hat"], W_real=bp[c]["W_real_hat"]), ln_ratio=lr,
                     passed=all(abs(v) <= TOL15 for v in lr.values()))
    k4_run = [c for c in k4 if k4[c]["status"] == "run"]
    k4_pass = bool(k4_run) and all(k4[c]["passed"] for c in k4_run)
    # K5
    k5 = {}
    for c in ("V1", "V2"):
        rr = {r["k"]: r for r in res.get(c, [])}
        hat = {d["k"]: d["W_real_hat"] for d in bp[c]["draws"]}
        P = sum(r["refute"] for r in rr.values())
        Phat = sum(rr[k]["signal"] > hat[k] for k in rr)
        obsW = med([r["W_real"] for r in rr.values()]) if rr else None
        lr = math.log(bp[c]["W_real_hat"] / obsW) if rr else None
        k5[c] = dict(built=bp[c]["built"], observed_W_real=obsW, predicted_W_real=bp[c]["W_real_hat"], ln_ratio=lr,
                     P=P, P_hat=Phat, width_ok=bool(rr) and abs(lr) <= TOL15,
                     pass_ok=bool(rr) and abs(Phat - P) <= PHAT_TOL)
        k5[c]["passed"] = bool(k5[c]["width_ok"] and k5[c]["pass_ok"])
    k5_pass = all(k5[c]["passed"] for c in k5)
    k3_pass = pred["K3"]["passed"] is True
    gate_ok = bool(k4_run) and all(bp[c]["built"] >= K5_MIN for c in ("V1", "V2"))
    if not k3_pass:
        reading = pred["K3"]["reading"]
    elif not k4_run:
        # PREREG-AMBIGUITY: no frozen reading covers both K4 cells "not run"; the prereg says only that the M77
        # step is not run.
        reading = "K4 not run (both legend cells built fewer than 12 draws): the M77 step is not run."
    elif not k4_pass:
        reading = R_K4_FAIL + " No M77 step."
    elif not k5_pass:
        reading = R_K5_FAIL + " The M77 step is not run."
    elif not gate_ok:
        reading = "V1 or V2 built fewer than 16 of 20 draws: the M77 step is not run."
    else:
        reading = "K3, K4 and K5 passed: the M77 step may run."
    out.update(K4=dict(cells=k4, passed=k4_pass), K5=dict(cells=k5, passed=k5_pass), K3_passed=k3_pass,
               m77_allowed=bool(k3_pass and k4_pass and k5_pass and gate_ok), reading=reading, passed=True,
               seconds=round(time.time() - t0, 1))
    dump(out, P_BLIND)
    print(json.dumps(dict(K4=k4, K5=k5, m77_allowed=out["m77_allowed"], reading=reading), indent=1), flush=True)


def mode_m77():
    """Label-free M77 step. Imports no scorer and no sealed module; no IC, no N1, no lexicon match on M77 (A6); no value
    string is assigned to any M77 sign and nothing key-shaped is written."""
    refuse_if_exists(P_M77)
    assert P_BLIND.exists() and P_PRED.exists(), "blind.json or predictions.json missing"
    blind = json.load(open(P_BLIND))
    assert blind.get("m77_allowed") is True, "blind.json does not allow the M77 step: refused"
    sha = sha256(P_PRED)
    assert blind["predictions_sha256"] == sha and \
        any(l.split()[:1] == [sha] for l in HASHES.read_text().splitlines()), "predictions.json changed or not hashed"
    fm = guard()
    pred = json.load(open(P_PRED)); form = pred["form"]
    ns = sealed_excess(); exfn, S_BASE = ns["excess"], ns["S_BASE"]
    sys.path.insert(0, str(ROOT))
    from corpus.load import m77_texts, distinct, runs
    recs = distinct([r for r in m77_texts() if r["object_type"] in ("seal", "sealing")])
    texts = [rs for rs in (runs(r["seq"]) for r in recs) if rs]
    rows = {"Sa": [], "Sb": [], "Sc": []}
    for k in range(1, NSUB + 1):
        # split in half at random (seed base + 800,000 + k); as scratch gate4: shuffle text order, first half = dev
        rng = random.Random(BASE + 800_000 + k); order = list(range(len(texts))); rng.shuffle(order)
        half = len(order) // 2
        dev = [r for i in order[:half] for r in texts[i]]; ho = [r for i in order[half:] for r in texts[i]]
        fmz = Counter(s for u in dev + ho for s in u)
        rank = sorted(fmz, key=lambda s: (-fmz[s], s))           # ties by sign name
        E = float(exfn(ho, S_BASE + k)[0])
        shapes = {}
        for nm in ("Sa", "Sb"):
            sh = pred["shapes"][nm].get(str(k))
            if sh is None:
                continue
            n = min(len(rank), len(sh["cc"]))
            shapes[nm] = ({rank[i]: sh["cc"][i] for i in range(n)},
                          {rank[i]: (sh["u_num"][i], sh["u_den"][i]) for i in range(n)})
        # Sc, flat: one consonant per sign, no bin-mate shares its value: u_s = 1 / size of s's frequency bin
        # PREREG-AMBIGUITY: Sc's bins taken over M77 dev + held-out frequency, ties by sign name, bins of 10.
        ucs = {}
        for i in range(0, len(rank), 10):
            b = rank[i:i + 10]
            for s in b:
                ucs[s] = (1, len(b))
        shapes["Sc"] = ({s: 1 for s in rank}, ucs)
        for nm, (cc, u) in shapes.items():
            hof = Counter(s for x in ho for s in x if s in cc)
            C, M = conc_C(hof, cc, u)
            G, cps, tc = seg_stats(ho, lambda s: cc.get(s), LMIN)
            hs, _ = h_stats(hof)
            # PREREG-AMBIGUITY: D is the prereg's literal 0.180 (the primary lexicon at LMIN 3).
            p = dict(C=C, G=G, D=D_M77, N=M, T=len(cc), E=E, cons_per_seg=cps, **hs)
            ws, wr = predict_draw(p, form)
            rows[nm].append(dict(k=k, props=p, W_scr_hat=ws, W_real_hat=wr))
    used = list(form["terms"]) + (["E"] if form["stage2"]["kind"] == "linear" and "g1" in form["stage2"] else [])
    out = dict(prereg=PREREG, mode="m77", A5=dict(free_mem_frac=fm), predictions_sha256=sha, n_texts=len(texts),
               primary="Sc", note="Sc is primary and the only shape that gets S_min; Sa and Sb are sensitivity rows.")
    res = {}
    for nm, rr in rows.items():
        if not rr:
            res[nm] = dict(status="no draws"); continue
        pm = {q: med([r["props"][q] for r in rr]) for q in rr[0]["props"]}
        ws, wr = med([r["W_scr_hat"] for r in rr]), med([r["W_real_hat"] for r in rr])
        # PREREG-AMBIGUITY: "outside the fit cells' range ... by more than 10%" read as below 0.90 x min or above
        # 1.10 x max of the fit cells' medians, for each property the final predictor uses.
        outr = {q: pm[q] for q in used
                if pm[q] < (1 - RANGE_TOL) * pred["fit_ranges"][q][0] or pm[q] > (1 + RANGE_TOL) * pred["fit_ranges"][q][1]}
        res[nm] = dict(role="primary" if nm == "Sc" else "sensitivity", draws=len(rr), property_medians=pm,
                       W_scr_hat=ws, W_scr_band=[ws / BAND, ws * BAND], W_real_hat=wr, W_real_band=[wr / BAND, wr * BAND],
                       out_of_range=outr, extrapolated=bool(outr))
    sc = res["Sc"]
    smin = None if sc.get("extrapolated", True) else sc["W_real_hat"] * BAND * pred["q80"]
    if smin is not None:
        sc["S_min"] = smin
    tracks = [t for t, v in pred["Q1"].items() if v.get("tracks")]
    clause = R_SMIN.format(s=f"{smin:.3f}") if smin is not None else R_NO_SMIN
    out.update(shapes=res, q80=pred["q80"], signals_seen=SEALED_SIGNALS,
               signals_note="Signal rose with width on these texts, so they are not a forecast for M77.",
               reading=R_ALL.format(props=", ".join(tracks) if tracks else "none of the properties",
                                    w=f"{sc['W_real_hat']:.3f}", smin_clause=clause),
               linear_b=R_LB, indus=R_INDUS)
    leaked = [m for m in SEALED_MODULES if m in sys.modules]
    assert not leaked, f"A6: the M77 step imported a sealed scorer module: {leaked}"
    dump(out, P_M77)
    print(json.dumps(dict(shapes={n: {q: v.get(q) for q in ("W_scr_hat", "W_real_hat", "extrapolated", "S_min")}
                                  for n, v in res.items()}, reading=out["reading"]), indent=1), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    modes = dict(kill=mode_kill, fit=mode_fit, blind=mode_blind, m77=mode_m77)
    if mode not in modes:
        sys.exit("usage: run.py kill|fit|blind|m77")
    modes[mode]()
