"""Wrong lexicon and matcher dial on Linear B (prereg docs/prereg/lb_wrong_lexicon.md, SEALED v5).
Run (from the repo root, under the Indus compute lock and memory guard):
  nice -n 20 .venv/bin/python -I experiments/lb_wrong_lexicon/run.py kill   # tables, K3, rung aborts, K1 (+rerun), K2
  nice -n 20 .venv/bin/python -I experiments/lb_wrong_lexicon/run.py full   # KG, B0 x LMIN 5 controls, B1-B3, rest
Workers: env NWORK (default 4, capped at 4).

Order inside `kill` (prereg "Cost"): label-free tables and aborts (sealed F0/F1 builder reproduced, Arm A table and
K3, Arm B step table and rung aborts, label-free F0 counts), then K1 (F0 x B0 x LMIN 4 on the unpatched scorer path),
K1 rerun (patched path: LMIN set to 5, set back to 4, scored), then K2 (fully wrong key, 13 F0 cells). Any sealed
STOP writes kill.json with kill_passed=false and exits non-zero. `full` refuses unless kill.json says kill_passed,
rebuilds the label-free part (checked equal to kill.json), then runs KG, the two B0 x LMIN 5 controls, the B1/B2/B3
cells, and the remaining cells, in that order, and applies the frozen readings. Output JSON holds aggregates only.

Scoring goes through the sealed lb_formula_dial cell_job (true key, one value per sign, lrung "1.0" path, i.e. the
sealed lb_shape_ladder IC with R1's N1 seed and kept-sign order). Per job the worker sets lb_formula_dial's LEX to the
cell's lexicon and, for LMIN 5, patches the ladder module global LMIN (read by ic_seg and IC.shape) and restores it.
The K2 wrong key is applied by patching the sealed lb_certify true_value for that job only, and restoring it.
"""
import importlib.util, json, math, os, random, re, sys, time, unicodedata
from collections import Counter, defaultdict
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/lb_certify"))
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("formula_dial", ROOT / "experiments/lb_formula_dial/run.py")
F = importlib.util.module_from_spec(_spec); sys.modules["formula_dial"] = F; _spec.loader.exec_module(F)
L = F.L                                               # sealed lb_shape_ladder module (scorer, LMIN global)
B = F.B                                               # sealed lb_certify module (Homer, skeleton, true_value)
assert L.LMIN == 4, "sealed ladder LMIN is not 4"
LMIN_SEALED = L.LMIN
TRUE_VALUE_SEALED = B.true_value

NWORK = min(4, int(os.environ.get("NWORK", "4")))
NSUB = L.NSUB; MAXW = L.MAXW
LETTERS9 = "dkmnprstz"                                 # q-free key letters (density over 9^L)
S_THIN, S_WRONG = 20261202, 20261203
WRONG_TRIES = 100_000
THIN_STEP, THIN_TARGET = 500, 0.177
K3_D4, K3_TOL4, K3_D5, K3_TOL5 = 0.177, 0.005, 0.0143, 0.01
TABLE_TOL_A, TABLE_TOL_B = 0.0005, 0.002
GEN_D4, GEN_D5 = 0.339, 0.092                         # generous matcher target (distance column)
PASS, CLEAR_FAIL, VOID_AT, POOLED_MAX = 16, 12, 3, 0.03

# ------------------------------------------------------------------ sounds, M0, expansion tables (frozen)
VOW_GR = B.VOW                                        # sealed Greek vowel set
GSND = {"π": "π", "β": "β", "φ": "φ", "κ": "κ", "γ": "γ", "χ": "χ", "τ": "τ", "θ": "θ", "δ": "δ", "λ": "λ",
        "ρ": "ρ", "ζ": "ζ", "μ": "μ", "ν": "ν", "σ": "σ", "ς": "σ", "ξ": "κσ", "ψ": "πσ"}
M0 = {"π": "p", "β": "p", "φ": "p", "κ": "k", "γ": "k", "χ": "k", "τ": "t", "θ": "t", "δ": "d", "λ": "r",
      "ρ": "r", "ζ": "z", "μ": "m", "ν": "n", "σ": "s"}
Q_SOUNDS = set("πβφτθκγχ")                            # q rule: frozen at every rung, never widened
LAT = {"p": "π", "b": "β", "f": "φ", "v": "β", "k": "κ", "g": "γ", "c": "κ", "q": "κ", "x": "κσ", "t": "τ",
       "d": "δ", "l": "λ", "r": "ρ", "z": "ζ", "m": "μ", "n": "ν", "s": "σ"}
VOW_LAT, SKIP_LAT = set("aeiou"), set("hjwy")
assert set(LAT) | VOW_LAT | SKIP_LAT == set("abcdefghijklmnopqrstuvwxyz")
STEPS = [None, ("d", "τ"), ("d", "θ"), ("t", "δ"), ("d", "ζ"), ("t", "ζ"), ("d", "σ"), ("t", "σ"), ("d", "ν"),
         ("t", "ν"), ("d", "λ"), ("t", "λ"), ("d", "ρ")]
RUNG_STEP = {"B0": 0, "B1": 3, "B2": 9, "B3": 11}
# Prereg Arm B table: step -> (density 4, 5, 6, rule LMIN). Rung abort uses densities 4 and 5 (tol 0.002).
TABLE_B = {0: (0.177, 0.014, 0.0005, 4), 1: (0.252, 0.026, 0.0010, 5), 2: (0.269, 0.029, 0.0012, 5),
           3: (0.286, 0.034, 0.0014, 5), 4: (0.289, 0.034, 0.0014, 5), 5: (0.292, 0.035, 0.0015, 5),
           6: (0.310, 0.045, 0.0021, 5), 7: (0.328, 0.055, 0.0029, 5), 8: (0.349, 0.066, 0.0039, 5),
           9: (0.366, 0.077, 0.0051, 5), 10: (0.374, 0.084, 0.0064, 5), 11: (0.382, 0.091, 0.0078, 5),
           12: (0.393, 0.100, 0.0105, 5)}
# Prereg Arm A table: label -> (types, density 4 full, density 5 full, kept or None=all, d4 thinned, d5 thinned)
TABLE_A = {"H": (28144, 0.1770, 0.0143, None, 0.1770, 0.0143), "G": (20420, 0.2076, 0.0222, 13920, 0.1768, 0.0180),
           "Fi": (20653, 0.1881, 0.0157, 17653, 0.1756, 0.0142), "Id": (14025, 0.1911, 0.0131, 12025, 0.1770, 0.0113),
           "Hu": (17967, 0.2672, 0.0327, 8967, 0.1760, 0.0185), "Es": (11571, 0.1585, 0.0137, None, 0.1585, 0.0137),
           "Od": (16145, 0.1254, 0.0082, None, 0.1254, 0.0082)}
H_RAW_FORMS = 30747
SOURCES_A = {"G": ("greek", "experiments/decipherability/raw/wiki_el.txt"),
             "Fi": ("latin", "experiments/decipherability/raw/kalevala.txt"),
             "Id": ("latin", "experiments/decipherability/raw/wiki_id.txt"),
             "Hu": ("latin", "experiments/decipherability/raw/wiki_hu.txt"),
             "Es": ("latin", "experiments/decipherability/raw/wiki_es.txt")}
READING_A = ("G", "Fi", "Id", "Hu"); REPORT_A = ("Es", "Od"); WRONG_A = ("Fi", "Id", "Hu")
HOMER = ("homer_001.xml", "homer_002.xml")            # 001 Iliad, 002 Odyssey (TEI titles)
GREEK_RUN = re.compile(r"[Ͱ-Ͽἀ-῿]+")                   # sealed lb_certify pattern
# PREREG-AMBIGUITY: "runs of letters" for Latin-script lists is read as runs of Unicode letters ([^\W\d_]+), so that
# accented and foreign-script words exist to be dropped as unmappable (the prereg reports nonzero drops).
LATIN_RUN = re.compile(r"[^\W\d_]+")


def table_of(step):
    t = {s: {M0[s]} | ({"q"} if s in Q_SOUNDS else set()) for s in M0}
    for i in range(1, step + 1):
        letter, sound = STEPS[i]; t[sound].add(letter)
    return t


def type_of(tok):
    """One type rule for every list: lower-case, NFD, strip combining marks."""
    return "".join(ch for ch in unicodedata.normalize("NFD", tok.lower()) if not unicodedata.combining(ch))


def seq_greek(t):
    out = []
    for ch in t:
        if ch in VOW_GR:
            out.append("V")
        elif ch in GSND:
            out += list(GSND[ch])
    return out


def seq_latin(t):
    out = []
    for ch in t:
        if ch in VOW_LAT:
            out.append("V")
        elif ch in SKIP_LAT:
            continue                                  # skipped as if absent: neighbours are adjacent
        else:
            out += list(LAT[ch])
    return out


def skel_sounds(seq):
    """Sealed skeleton rules on M0 letters (as lb_certify.skeleton); the surviving sounds are stored."""
    m = ["V" if x == "V" else M0[x] for x in seq]
    cons = []
    for i, c in enumerate(m):
        if c == "V":
            continue
        nxt = m[i + 1] if i + 1 < len(m) else None
        if nxt is None and c in "snr":
            continue
        if nxt is not None and nxt != "V" and c in "snrm":
            continue
        if cons and cons[-1][1] == c and i > 0 and m[i - 1] == c:
            continue
        cons.append((seq[i], c))
    return tuple(s for s, _ in cons)


def expand(skels, table):
    lex = set()
    for sk in skels:
        if 1 <= len(sk) <= MAXW:
            lex.update(product(*[sorted(table[s]) for s in sk]))
    return lex


def densities(lex):
    cnt = Counter(len(t) for t in lex if "q" not in t)
    return {Lh: cnt[Lh] / 9 ** Lh for Lh in range(1, MAXW + 1)}


def rule_lmin(d):
    return next((Lh for Lh in range(1, MAXW + 1) if d[Lh] <= 0.25), MAXW + 1)


def m0_qfree(sk):
    return tuple(M0[s] for s in sk)                   # at M0 the only q-free expansion of a skeleton


# ------------------------------------------------------------------ word lists (label-free)
def homer_tokens(files):
    toks = []
    for f in files:
        txt = re.sub(r"<[^>]+>", " ", open(ROOT / "experiments/cognate_decipher/ext/greek" / f, encoding="utf8").read())
        toks += GREEK_RUN.findall(txt)
    return toks


def word_types(kind, toks):
    """Returns (sorted types, distinct dropped strings). Unmappable = any char outside a-z (Latin lists only)."""
    ts = {type_of(t) for t in toks}
    if kind == "latin":
        bad = {t for t in ts if any(not ("a" <= ch <= "z") for ch in t)}
        return sorted(ts - bad), len(bad)
    return sorted(ts), 0


def lexicon_list(kind, types):
    seqf = seq_greek if kind == "greek" else seq_latin
    return {t: skel_sounds(seqf(t)) for t in types}


def thin(types, skmap, d4_ref):
    """Sort by code point, shuffle once with Random(20261202), drop from the end in steps of 500; keep the step whose
    density at 4 is nearest 0.177 (tie: larger size). Only a lexicon denser than H at 4 is thinned."""
    order = sorted(types); random.Random(S_THIN).shuffle(order)
    full4 = len({m0_qfree(skmap[t]) for t in order if len(skmap[t]) == 4}) / 9 ** 4
    if not full4 > d4_ref:
        return order, None
    best, n = None, len(order)
    while n > 0:                                      # from the largest size down, strict improvement only
        d4 = len({m0_qfree(skmap[t]) for t in order[:n] if len(skmap[t]) == 4}) / 9 ** 4
        if best is None or abs(d4 - THIN_TARGET) < best[1]:
            best = (n, abs(d4 - THIN_TARGET))
        n -= THIN_STEP
    return order[:best[0]], best[0]


def arm_a_tables():
    T0 = table_of(0)
    rec, lexs, mism = {}, {}, []
    sealed_lex, sealed_raw = B.build_lexicon()
    h_toks = homer_tokens(HOMER)
    h_types, _ = word_types("greek", h_toks)
    h_sk = lexicon_list("greek", h_types)
    sk_diff = sum(list(m0_qfree(h_sk[t])) != B.skeleton(t) for t in h_types)   # per type, vs sealed skeleton
    if sk_diff:
        mism.append(f"H: sound builder M0 letters differ from the sealed skeleton on {sk_diff} types")
    H = expand(h_sk.values(), T0)
    lex_equal = H == sealed_lex
    dH = densities(H)
    h4 = {t for t in H if len(t) == 4 and "q" not in t}
    lists = {"H": ("greek", h_types, h_sk, 0, len(set(h_toks)))}
    od_toks = homer_tokens(HOMER[1:]); od_types, _ = word_types("greek", od_toks)
    lists["Od"] = ("greek", od_types, lexicon_list("greek", od_types), 0, None)
    for lab, (kind, path) in SOURCES_A.items():
        txt = open(ROOT / path, encoding="utf8").read()
        toks = GREEK_RUN.findall(txt) if kind == "greek" else LATIN_RUN.findall(txt)
        types, dropped = word_types(kind, toks)
        lists[lab] = (kind, types, lexicon_list(kind, types), dropped, None)
    for lab in ("H", "G", "Fi", "Id", "Hu", "Es", "Od"):
        kind, types, skmap, dropped, raw = lists[lab]
        full = H if lab == "H" else expand({skmap[t] for t in types}, T0)
        dfull = densities(full)
        kept_types, kept = (types, None) if lab == "H" else thin(types, skmap, dH[4])
        lex = full if kept is None else expand({skmap[t] for t in kept_types}, T0)
        dth = densities(lex)
        own4 = {t for t in full if len(t) == 4 and "q" not in t}
        r = dict(kind=kind, types=len(types), dropped_unmappable_types=dropped, raw_forms=raw,
                 density_full={Lh: float(v) for Lh, v in dfull.items()}, kept=len(kept_types) if kept else "all",
                 kept_size=len(kept_types), density_thinned={Lh: float(v) for Lh, v in dth.items()},
                 rule_lmin_thinned=rule_lmin(dth), lexicon_size=len(lex),
                 share_4cons_homeric_full=(len(own4 & h4) / len(own4)) if own4 else None)
        # K3, matched density (after thinning)
        r["K3_bounds_met"] = bool(abs(dth[4] - K3_D4) <= K3_TOL4 and abs(dth[5] - K3_D5) <= K3_TOL5)
        n_tab, f4, f5, k_tab, t4, t5 = TABLE_A[lab]
        chk = []
        if len(types) != n_tab:
            chk.append(f"types {len(types)} != {n_tab}")
        if (k_tab is None) != (kept is None) or (k_tab is not None and kept != k_tab):
            chk.append(f"kept {kept} != {k_tab}")
        for nm, a, b in (("d4 full", dfull[4], f4), ("d5 full", dfull[5], f5), ("d4 thinned", dth[4], t4),
                         ("d5 thinned", dth[5], t5)):
            if abs(a - b) > TABLE_TOL_A:
                chk.append(f"{nm} {a:.5f} vs {b}")
        if lab == "H" and raw != H_RAW_FORMS:
            chk.append(f"raw forms {raw} != {H_RAW_FORMS}")
        r["table_mismatch"] = chk
        mism += [f"{lab}: {c}" for c in chk]
        rec[lab] = r; lexs[lab] = lex
    rec["H"]["sound_builder_types_differing_from_sealed_skeleton"] = sk_diff
    rec["H"]["sealed_lexicon_set_equal"] = bool(lex_equal); rec["H"]["sealed_lexicon_size"] = len(sealed_lex)
    if not lex_equal:
        mism.append("H: M0 builder lexicon is not set-equal to the sealed lexicon")
    return rec, lexs, mism, h_sk


def ho_letter_counts(draws):
    cnt = Counter()
    for d in draws.values():
        for t in d["ho"]:
            for w in t:
                for s in w:
                    cnt.update(B.true_value(s))
    return cnt


def arm_b_tables(h_sk, draws):
    cnt = ho_letter_counts(draws); tot = sum(cnt.values())
    skels = set(h_sk.values())
    rec, lexs, run_rungs = {}, {}, {}
    for step in range(len(STEPS)):
        tab = table_of(step); lex = expand(skels, tab); d = densities(lex)
        inv = defaultdict(set)
        for snd, lets in tab.items():
            for l in lets:
                inv[l].add(snd)
        nsnd = {l: len(inv[l]) for l in inv}
        # PREREG-AMBIGUITY: g is not defined in the prereg beyond "sounds per letter"; reported (never used) as the
        # token-weighted mean number of sounds per key letter over pooled held-out F0 key consonants (q counts 8).
        g = sum(cnt[l] * nsnd.get(l, 0) for l in cnt) / tot
        multi = sum(cnt[l] for l in cnt if nsnd.get(l, 0) > 1) / tot
        over = sum(1 for snd, lets in tab.items() if len(lets - {"q"}) >= 2)
        dist = abs(math.log(d[4] / GEN_D4)) + abs(math.log(d[5] / GEN_D5))
        e4, e5, e6, elmin = TABLE_B[step]
        r = dict(step=step, pair=list(STEPS[step]) if STEPS[step] else None,
                 density={Lh: float(v) for Lh, v in d.items()}, rule_lmin=rule_lmin(d),
                 sounds_on_d=nsnd["d"], sounds_on_t=nsnd["t"], max_sounds_non_q=max(v for l, v in nsnd.items()
                                                                                   if l != "q"),
                 g_token_weighted=g, token_share_multi_sound=multi, sounds_matching_2plus_letters=over,
                 distance=dist, table=dict(d4=e4, d5=e5, d6=e6, rule_lmin=elmin),
                 diff_d4=float(d[4] - e4), diff_d5=float(d[5] - e5), lexicon_size=len(lex))
        rung = next((n for n, s in RUNG_STEP.items() if s == step), None)
        if rung:
            ok = rule_lmin(d) <= 5 and abs(d[4] - e4) <= TABLE_TOL_B and abs(d[5] - e5) <= TABLE_TOL_B
            r.update(rung=rung, run=bool(ok))
            run_rungs[rung] = bool(ok)
            if ok:
                lexs[rung] = lex
        # PREREG-AMBIGUITY: steps that are not rungs are recomputed and reported; a mismatch there has no stated
        # consequence (the abort rule names rungs only), so it is flagged and does not abort.
        r["flag_table_mismatch"] = bool(abs(d[4] - e4) > TABLE_TOL_B or abs(d[5] - e5) > TABLE_TOL_B
                                        or rule_lmin(d) != elmin)
        rec[step] = r
    return rec, lexs, run_rungs, dict(key_consonants_ho_pooled=tot)


def f0_counts(draws):
    """Label-free: segment shares at 4+ and 5+ consonants, and value classes of the true key, on held-out F0."""
    seg = Counter(); classes = []
    for k, d in draws.items():
        freq = Counter(s for t in d["dev"] + d["ho"] for w in t for s in w)
        true = {s: B.true_value(s) for s in freq}
        S = L.IC(d["ho"], set())
        for t in d["ho"]:
            for c in S.segs(t, true):
                seg["all"] += len(c); seg["ge4"] += len(c) * (len(c) >= 4); seg["ge5"] += len(c) * (len(c) >= 5)
        cc = Counter(len(v) for v in true.values())
        classes.append(dict(k=k, **{f"cons_{c}": n for c, n in sorted(cc.items())},
                            distinct_values_cons_1=len({tuple(v) for v in true.values() if len(v) == 1})))
    return dict(key_consonants=seg["all"], share_in_segs_ge4=seg["ge4"] / seg["all"],
                share_in_segs_ge5=seg["ge5"] / seg["all"], value_classes=classes)


# ------------------------------------------------------------------ K2 wrong key (label-free construction)
def wrong_key(k, signs):
    """Within each consonant-count class, shuffle values across signs until no sign keeps a value equal to its own
    (up to 100,000 tries); a class with a single distinct value keeps it. Random(20261203 + 1000 k)."""
    rng = random.Random(S_WRONG + 1000 * k)
    true = {s: tuple(B.true_value(s)) for s in signs}
    cl = defaultdict(list)
    for s in sorted(signs):
        cl[len(true[s])].append(s)
    key, info = dict(true), dict(k=k, classes={})
    for c in sorted(cl):
        ss = cl[c]; vals = [true[s] for s in ss]
        if len(set(vals)) == 1:
            info["classes"][c] = dict(n=len(ss), kept=True)
            continue
        # Implementer choice: the same list is reshuffled in place on each try (each try is a uniform shuffle).
        tries = 0; ok = False
        while tries < WRONG_TRIES:
            tries += 1; rng.shuffle(vals)
            if all(v != true[s] for s, v in zip(ss, vals)):
                ok = True; break
        info["classes"][c] = dict(n=len(ss), kept=False, tries=tries, found=ok)
        if not ok:
            info["void"] = True
            return None, info
        key.update(zip(ss, vals))
    info["void"] = False
    return key, info


# ------------------------------------------------------------------ workers
LEXS = None


def winit(lexs):
    global LEXS
    LEXS = lexs


def job(a):
    """One cell-draw through the sealed lb_formula_dial cell_job. lmin None = unpatched sealed path."""
    cell, lex, lmin, prime, wrong, args = a
    F.LEX = LEXS[lex]
    try:
        if lmin is not None:
            if prime is not None:
                L.LMIN = prime                         # patch in place first (K1 rerun) ...
            L.LMIN = lmin                              # ... then the cell's LMIN
        else:
            assert L.LMIN == LMIN_SEALED
        if wrong is not None:
            B.true_value = lambda s, _w=wrong: list(_w[s])
        r = F.cell_job(args)
    finally:
        L.LMIN = LMIN_SEALED; B.true_value = TRUE_VALUE_SEALED
    assert L.LMIN == LMIN_SEALED and B.true_value is TRUE_VALUE_SEALED
    lex_name, fr, lm = cell
    r.update(cell=cell_name(cell), lex=lex_name, lmin=lm, wrong_key=wrong is not None)
    return r


def cell_name(cell):
    lex, fr, lm = cell
    return f"{lex} x {fr} x L{lm}"


def jobs_for(cell, draws, corp, wrong=None, lmin_patch=True, prime=None):
    lex, fr, lm = cell; out = []
    for k in range(1, NSUB + 1):
        if (fr, k) not in corp:
            continue                                   # unbuilt F1 draw: non-pass
        w = None
        if wrong is not None:
            w = wrong.get(k)
            if w is None:
                continue                               # no wrong key found: void draw in every K2 cell
        out.append((cell, lex, lm if lmin_patch else None, prime, w, F.cell_args(fr, "1.0", k, draws, corp, {})))
    return out


def summarise(rows, void=False):
    s = F.summarise(rows)
    if s is None:
        return None
    s["band"] = "pass" if s["P"] >= PASS else ("clear_fail" if s["P"] <= CLEAR_FAIL else "edge")
    s["K2_void"] = bool(void)
    s["interpretable"] = bool(s["interpretable"] and not void)
    s["cell_pass"] = bool(s["cell_pass"] and not void)
    return s


def conv(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, set):
        return sorted(o)
    raise TypeError(type(o))


def dumps(obj, path):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=conv)


def jround(x):
    return json.loads(json.dumps(x, default=conv))


# ------------------------------------------------------------------ label-free part (shared by kill and full)
def labelfree():
    t0 = time.time()
    fsum, draws, corp, _ = F.labelfree()
    fk = json.load(open(ROOT / "experiments/lb_formula_dial/kill.json"))
    builder_same = json.loads(json.dumps(F.strip(fsum))) == F.strip(fk["labelfree"])
    f1_built = sum(("F1", k) in corp for k in range(1, NSUB + 1))
    arec, alex, amism, h_sk = arm_a_tables()
    brec, blex, run_rungs, binfo = arm_b_tables(h_sk, draws)
    lexs = dict(alex); lexs.update({r: v for r, v in blex.items() if r != "B0"})
    assert blex.get("B0") is None or blex["B0"] == alex["H"], "Arm B step 0 differs from the M0 Homeric lexicon"
    counts = f0_counts(draws)
    wrong, winfo = {}, []
    for k, d in draws.items():
        signs = set(Counter(s for t in d["dev"] + d["ho"] for w in t for s in w))
        key, info = wrong_key(k, signs); winfo.append(info)
        if key is not None:
            wrong[k] = key
    stops = []
    if not builder_same:
        stops.append("sealed lb_formula_dial label-free build not reproduced (differs from its kill.json)")
    if f1_built != NSUB - 2:
        stops.append(f"F1 built draws {f1_built}, sealed study had {NSUB - 2}")
    if amism:
        stops.append("K3 abort: Arm A table not reproduced: " + "; ".join(amism))
    summ = dict(formula_dial_builder_reproduced=bool(builder_same), F1_built=f1_built, F1_unbuilt_nonpass=NSUB - f1_built,
                arm_a=arec, K3=dict(mismatches=amism, passed=not amism,
                                    bounds_met={l: arec[l]["K3_bounds_met"] for l in arec},
                                    usable_for_readings=[l for l in READING_A if arec[l]["K3_bounds_met"]]),
                arm_b=brec, arm_b_info=binfo, rungs_run=run_rungs, f0_counts=counts,
                wrong_keys=dict(void_draws=[i["k"] for i in winfo if i["void"]], per_draw=winfo),
                stops=stops)
    return jround(summ), dict(draws=draws, corp=corp, lexs=lexs, wrong=wrong), round(time.time() - t0, 1)


def k1_check(rows):
    sealed = {r["k"]: r for r in json.load(open(ROOT / "experiments/lb_shape_ladder/full.json"))["runs"]
              if r["rung"] == "R1"}
    per = []
    for r in rows:
        s = sealed[r["k"]]
        per.append(dict(k=r["k"], max_abs_diff=max(abs(r[q] - s[q]) for q in ("true_ic", "n1_mean", "n1_p99")),
                        tokens_equal=r["tokens_ho"] == s["tokens_ho"]))
    P = sum(r["refute"] for r in rows); C = sum(r["shuffled_refute"] for r in rows)
    eq = len(per) == NSUB and all(m["max_abs_diff"] <= 1e-9 and m["tokens_equal"] for m in per)
    return dict(P=P, scrambled_passes=C, match_1e9=bool(eq), passed=bool(P == NSUB and C <= 1 and eq),
                per_draw=per, cell=summarise(rows), runs=sorted(rows, key=lambda r: r["k"]))


def k2_cells(rungs_run):
    cells = [("H", "F0", 5), ("H", "F0", 4)]
    for r in ("B1", "B2"):
        if rungs_run.get(r):
            cells += [(r, "F0", 5), (r, "F0", 4)]
    if rungs_run.get("B3"):
        cells.append(("B3", "F0", 5))
    cells += [(l, "F0", 4) for l in ("G", "Fi", "Id", "Hu", "Es", "Od")]
    return cells


# ------------------------------------------------------------------ modes
def kill():
    t0 = time.time()
    summ, S, secs = labelfree()
    out = dict(labelfree=summ, labelfree_seconds=secs, kill_passed=False)
    print(json.dumps(dict(builder=summ["formula_dial_builder_reproduced"], F1_built=summ["F1_built"],
                          K3=summ["K3"], rungs_run=summ["rungs_run"],
                          wrong_key_void_draws=summ["wrong_keys"]["void_draws"],
                          seg_share_ge5=summ["f0_counts"]["share_in_segs_ge5"]), indent=1), flush=True)

    def stop(msg):
        out["stop"] = msg; dumps(out, HERE / "kill.json"); print("STOP:", msg, flush=True); sys.exit(1)

    if summ["stops"]:
        stop(" | ".join(summ["stops"]))
    out["K3"] = dict(passed=True)
    with Pool(NWORK, initializer=winit, initargs=(S["lexs"],)) as P:
        k1 = P.map(job, jobs_for(("H", "F0", 4), S["draws"], S["corp"], lmin_patch=False), chunksize=1)
        K1 = k1_check(k1); out["K1"] = K1
        print("K1", json.dumps({q: K1[q] for q in ("P", "scrambled_passes", "match_1e9", "passed")}), flush=True)
        if not K1["passed"]:
            stop("K1 failed: STOP")
        k1b = P.map(job, jobs_for(("H", "F0", 4), S["draws"], S["corp"], prime=5), chunksize=1)
        K1b = k1_check(k1b)
        h1 = {r["k"]: r["n1_keys_sha256"] for r in k1}
        K1b["n1_keys_identical_to_K1"] = all(r["n1_keys_sha256"] == h1[r["k"]] for r in k1b)
        K1b["passed"] = bool(K1b["passed"] and K1b["n1_keys_identical_to_K1"])
        K1b.pop("runs")
        out["K1_rerun_patched"] = K1b
        print("K1 rerun (patched LMIN 5 -> 4)", json.dumps({q: K1b[q] for q in ("P", "scrambled_passes", "match_1e9",
                                                                               "passed")}), flush=True)
        if not K1b["passed"]:
            stop("K1 rerun on the patched LMIN path failed: STOP")
        cells = k2_cells(summ["rungs_run"]); jobs = []
        for c in cells:
            jobs += jobs_for(c, S["draws"], S["corp"], wrong=S["wrong"])
        res = P.map(job, jobs, chunksize=1)
    by = defaultdict(list)
    for r in res:
        by[r["cell"]].append(r)
    k2 = {}
    for c in cells:
        rows = by[cell_name(c)]; Pn = sum(r["refute"] for r in rows)
        k2[cell_name(c)] = dict(scored=len(rows), P=Pn, void=bool(Pn >= VOID_AT),
                                median_margin=float(np.median([r["margin"] for r in rows])) if rows else None)
    n_all = sum(v["scored"] for v in k2.values()); p_all = sum(v["P"] for v in k2.values())
    pooled = p_all / n_all if n_all else None
    void = [c for c, v in k2.items() if v["void"]]
    K2 = dict(cells=k2, void_cells=void, pooled_passes=p_all, pooled_draws=n_all, pooled_rate=pooled,
              void_draws=summ["wrong_keys"]["void_draws"])
    stop_k2 = ("H x F0 x L4" in void) or pooled is None or pooled > POOLED_MAX
    K2["passed"] = not stop_k2
    out["K2"] = K2
    print("K2", json.dumps(dict(void_cells=void, pooled_rate=pooled, passed=K2["passed"])), flush=True)
    if stop_k2:
        stop("K2: F0 x B0 x LMIN 4 void or pooled wrong-key pass rate above 3%: STOP")
    out["kill_passed"] = True
    out["seconds"] = round(time.time() - t0, 1)
    dumps(out, HERE / "kill.json")
    print("kill passed; kill.json written", flush=True)


def full():
    kp = HERE / "kill.json"
    if not kp.exists():
        sys.exit("kill.json missing: run `kill` first")
    kr = json.load(open(kp))
    if kr.get("kill_passed") is not True or not (kr.get("K1", {}).get("passed") and
                                                 kr.get("K1_rerun_patched", {}).get("passed") and
                                                 kr.get("K2", {}).get("passed") and kr.get("K3", {}).get("passed")):
        sys.exit("kill test did not pass every gate: full run refused")
    t0 = time.time()
    summ, S, _ = labelfree()
    if summ != kr["labelfree"]:
        sys.exit("label-free rebuild differs from kill.json: full run refused")
    rr = summ["rungs_run"]; void = set(kr["K2"]["void_cells"])
    dr, co = S["draws"], S["corp"]
    KG = [("G", "F0", 4)]
    controls = [("H", "F0", 5), ("H", "F1", 5)]
    loose = []
    for r in ("B1", "B2"):
        if rr.get(r):
            loose += [(r, "F0", 5), (r, "F1", 5), (r, "F0", 4), (r, "F1", 4)]
    if rr.get("B3"):
        loose += [("B3", "F0", 5), ("B3", "F1", 5)]
    rest = [("H", "F1", 4)] + [(l, "F0", 4) for l in ("Fi", "Id", "Hu", "Es", "Od")]
    by = defaultdict(list)
    for r in kr["K1"]["runs"]:                                       # F0 x B0 x LMIN 4 = K1 (sealed R1)
        by["H x F0 x L4"].append(r)
    with Pool(NWORK, initializer=winit, initargs=(S["lexs"],)) as P:
        for name, batch in (("KG", KG), ("B0 x LMIN 5 controls", controls), ("B1-B3", loose), ("rest", rest)):
            jobs = [j for c in batch for j in jobs_for(c, dr, co)]
            res = P.map(job, jobs, chunksize=1)
            for r in res:
                by[r["cell"]].append(r)
            print(name, json.dumps({cell_name(c): sum(r["refute"] for r in by[cell_name(c)]) for c in batch}),
                  flush=True)
    cells = {c: summarise(rows, void=c in void) for c, rows in by.items()}
    R = readings(cells, summ, by)
    out = dict(labelfree=summ, K2_void_cells=sorted(void), rungs_run=rr, cells=cells, readings=R,
               runs=[r for c in sorted(by) for r in sorted(by[c], key=lambda r: r["k"])],
               seconds=round(time.time() - t0, 1))
    print(json.dumps(dict(cells={c: {q: v[q] for q in ("P", "scrambled_passes", "band", "interpretable")}
                                 for c, v in sorted(cells.items()) if v}, readings=R), indent=1))
    dumps(out, HERE / "full.json")


def readings(cells, summ, by):
    usable_a = set(summ["K3"]["usable_for_readings"])

    def ok(c):
        v = cells.get(c)
        return bool(v and v["interpretable"])

    def P(c):
        v = cells.get(c)
        return v["P"] if v else None

    def okA(l):
        return ok(f"{l} x F0 x L4") and l in usable_a

    A = {}
    pa = {l: P(f"{l} x F0 x L4") for l in ("H",) + READING_A + REPORT_A}
    A["P"] = pa
    A["median_margin"] = {l: cells[f"{l} x F0 x L4"]["median_margin"] if cells.get(f"{l} x F0 x L4") else None
                          for l in pa}
    A["usable"] = {l: okA(l) for l in READING_A}
    kg = okA("G") and pa["G"] >= PASS
    A["KG_holds"] = bool(kg)
    struct = (okA("Fi") and pa["Fi"] >= PASS) or sum(okA(l) and pa[l] >= PASS for l in WRONG_A) >= 2
    lang = kg and all(okA(l) for l in WRONG_A) and all(pa[l] <= CLEAR_FAIL for l in WRONG_A)
    A["structure_not_language"] = bool(struct)
    A["language_specific_at_this_shape"] = bool(lang)
    A["partly_language_specific"] = bool(kg and not struct and not lang)
    A["uninterpretable_no_carry_to_second_right_lexicon"] = bool(not kg and not struct)
    A["report_only"] = {l: dict(P=pa[l], density_thinned_4=summ["arm_a"][l]["density_thinned"]["4"],
                                density_thinned_5=summ["arm_a"][l]["density_thinned"]["5"]) for l in REPORT_A}

    Bd = {}
    c0, c1, p0, p1, b30, b31 = ("H x F0 x L5", "H x F1 x L5", "B2 x F0 x L5", "B2 x F1 x L5",
                                "B3 x F0 x L5", "B3 x F1 x L5")
    Bd["P"] = {c: P(c) for c in (c0, c1, p0, p1, b30, b31)}
    Bd["interpretable"] = {c: ok(c) for c in (c0, c1, p0, p1, b30, b31)}

    def passes(c):
        return ok(c) and P(c) >= PASS

    lmin_alone = ok(c0) and P(c0) < PASS
    Bd["lmin5_alone_removes_power"] = bool(lmin_alone) if ok(c0) else None
    # PREREG-AMBIGUITY: a non-interpretable F1 control is treated like a control below the bar: F1 x B2 and F1 x B3
    # cannot be read, so Arm B is read on F0 alone (a reading naming a non-interpretable cell cannot be drawn).
    f1_mode = passes(c1)
    Bd["F1_control_below_bar_or_uninterpretable"] = bool(not f1_mode)
    Bd["read_on"] = "F0 and F1" if f1_mode else "F0 only"
    Bd["looseness_removes_power"] = bool(passes(c0) and ok(p0) and P(p0) <= CLEAR_FAIL) \
        if ok(c0) and ok(p0) else None
    Bd["removes_power_at_indus_formula_excess"] = bool(passes(p0) and f1_mode and ok(p1) and P(p1) <= CLEAR_FAIL) \
        if ok(p0) and f1_mode and ok(p1) else None
    edge = []
    for p, c in ((p0, c0), (p1, c1)):
        if p == p1 and not f1_mode:
            continue
        if ok(p) and 13 <= P(p) <= 15 and passes(c):
            edge.append(p)
    Bd["at_the_edge"] = edge
    prims = [p0] + ([p1] if f1_mode else []); b3s = [b30] + ([b31] if f1_mode else [])
    drawable = all(ok(c) for c in prims + b3s)
    Bd["no_loss_found"] = bool(all(P(c) >= PASS for c in prims + b3s)) if drawable else None
    Bd["no_loss_at_B2_not_held_at_denser_step"] = bool(all(P(c) >= PASS for c in prims) and
                                                        any(P(c) < PASS for c in b3s)) if drawable else None
    if lmin_alone:
        Bd["qualifier"] = "not separable from the LMIN change (F0 x B0 x LMIN 5 below 16)"
    paired = {}
    for p, c in ((p0, c0), (p1, c1)):
        a = {r["k"]: r["refute"] for r in by.get(c, [])}; b = {r["k"]: r["refute"] for r in by.get(p, [])}
        ks = sorted(set(a) & set(b))
        paired[f"{p} vs {c}"] = dict(pass_control_fail_primary=sum(a[k] and not b[k] for k in ks),
                                     fail_control_pass_primary=sum(b[k] and not a[k] for k in ks), draws=len(ks))
    Bd["paired_discordant"] = paired
    Bd["report_only"] = {c: P(c) for c in cells if c.startswith("B1") or c.endswith("L4") and not
                         any(c.startswith(l + " ") for l in READING_A + REPORT_A)}
    return dict(not_interpretable=sorted(c for c, v in cells.items() if v and not v["interpretable"]),
                arm_a=A, arm_b=Bd)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "kill":
        kill()
    elif mode == "full":
        full()
    else:
        sys.exit("usage: run.py kill|full")
