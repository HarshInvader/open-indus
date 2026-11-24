"""Ur III seal legends under the sealed IC refute bench (prereg docs/prereg/ur3_legend_refute.md, SEALED v3).
Run (from the repo root, under the Indus compute lock; A5 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/ur3_legend_refute/run.py kill   # K0, K1, K2, K3 -> kill.json
  board/run.sh .venv/bin/python -I experiments/ur3_legend_refute/run.py full   # L1-L5 (refuses unless kill passed) -> full.json
Workers: env NWORK (default 4, capped at 4).

Order inside `kill` (strongest first): K0 (study scorer path on Linear B + Homer reproduces sealed lb_shape_ladder R1
per draw to 1e-9, 20 of 20, control 0; A1), K1 (label-free tables and counts recomputed, no IC; A2), K2 (wrong-key
calibration on administrative text; A3), K3 (planted true reading on administrative text with scrambled control and
partial keys; A3, K3 fail). Any abort or K3 fail writes kill.json with kill_passed=false and exits non-zero.
`full` refuses unless kill.json shows every check passed, rebuilds the label-free part (checked equal to kill.json),
runs cells L1-L5 and applies the frozen readings. Output JSON holds per-draw summaries only.

Reuse: the scorer (IC, ic_seg, permute_in_class_bins, shuffle_in_class, unigram, classes) is the sealed
lb_shape_ladder module; chunk and M77 lengths are sealed lb_certify; excess, m77_target and summarise are sealed
lb_formula_dial. LMIN is the ladder module global (read by ic_seg and IC.shape); each job sets it and restores it.
Extraction and lexicon rules follow the label-free scratch scripts the prereg's frozen counts came from (gate2.py,
lex.py); every place the prereg is silent and the scratch logic decides is marked "as scratch".
"""
import csv, hashlib, importlib.util, json, os, random, re, subprocess, sys, time, zipfile, zlib
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
# As lb_wrong_lexicon: put lb_certify on the path (the ladder does `import run as base`) and load the sealed
# lb_formula_dial under its own name; it loads the ladder as "ladder" and exposes lb_certify as F.B.
sys.path.insert(0, str(ROOT / "experiments/lb_certify"))
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("formula_dial", ROOT / "experiments/lb_formula_dial/run.py")
F = importlib.util.module_from_spec(_spec); sys.modules["formula_dial"] = F; _spec.loader.exec_module(F)
L = F.L                                               # sealed lb_shape_ladder (scorer, null, controls, build)
B = F.B                                               # sealed lb_certify (chunk, m77_lengths, Homer, true_value)
assert L.LMIN == 4 and L.MAXW == 7, "sealed ladder constants changed"
LMIN_SEALED = L.LMIN

NWORK = min(4, int(os.environ.get("NWORK", "4")))
BASE = 20261126
NSUB, NPERM, NPART = 20, L.NPERM, L.NPART            # 20 draws, 1000 N1 draws, 40 partial keys per level
NCHUNK = 2300
PASS, CLEAR_FAIL, CTRL_MAX, K2_MAX = 16, 12, 1, 1
LEVELS = (0.0, 0.25, 0.5, 0.75)
RAW = ROOT / "experiments/short_labels/raw/cdli"
LEX_OB = ROOT / "experiments/onomasticon/raw/x_epsd2-admin-oldbab/epsd2/admin/oldbab/gloss-sux.json"
LEX_RIM = ROOT / "experiments/onomasticon/raw/x_rimanum/rimanum/gloss-sux.json"
LEX_OAKK_ZIP = ROOT / "experiments/meaning_classes/raw/oracc/oakk.zip"
SEALED_R1 = ROOT / "experiments/lb_shape_ladder/full.json"
LOCK = ROOT / "board/compute.lock"
MEM_GUARD = 0.20

# Cells: name -> (text form, lexicon, LMIN). LMIN is frozen (3 for L1-L4 whatever K1 recomputes; 4 for L5).
CELLS = {"L1": ("chunk", "ob_spelled", 3), "L2": ("line", "ob_spelled", 3), "L3": ("chunk", "oakk_spelled", 3),
         "L4": ("chunk", "cf_all", 3), "L5": ("chunk", "ob_spelled", 4)}
# PREREG-AMBIGUITY: K2 and K3 name the text (administrative M77 chunks) but not the lexicon or LMIN. Read literally as
# the primary set-up: OB administrative spelled forms, LMIN 3 (the L1 bench on the kill-test text).
KILL_LEX, KILL_LMIN = "ob_spelled", 3

# ------------------------------------------------------------------ frozen tables (A2)
T_COUNTS = dict(legends=4819, legend_tokens=52907, sample_lines=39192, sample_texts=3475)
T_COVER = 0.90
T_EXCESS = {"legends": 0.255, "admin": 0.165}; T_EXCESS_TOL = 0.01
T_DENS_TOL = 0.01
T_DENS = {"homer_qfree": {4: 0.177, 5: 0.014},
          "ob_spelled": {2: 0.735, 3: 0.180, 4: 0.014, 5: 0.001},
          "oakk_spelled": {2: 0.821, 3: 0.243, 4: 0.016, 5: 0.001},
          "cf_all": {2: 0.699, 3: 0.126, 4: 0.008, 5: 0.000},
          "spelled_all": {2: 0.847, 3: 0.300, 4: 0.026, 5: 0.001},
          "oakk_names_spelled": {2: 0.918, 3: 0.339, 4: 0.036, 5: 0.002}}
T_SKEL = dict(homer_qfree=10491, ob_spelled=1838, oakk_spelled=1940, cf_all=928, spelled_all=3044,
              oakk_names_spelled=4327)            # reported beside the recount; skeleton counts gate nothing
T_LMIN = dict(homer_qfree=4, ob_spelled=3, oakk_spelled=3, cf_all=3, spelled_all=4, oakk_names_spelled=4)
T_MAPPING = dict(legend_share=dict(R=0.883, D=0.093, N=0.000, U=0.024), legend_reading_types=670,
                 admin_lines=767047, admin_tokens=4175889, admin_share=dict(R=0.761, D=0.051, N=0.176, U=0.012),
                 sample_tokens=212556, runs_ge2=39690, runs_ge2_tokens=166856, runs_ge2_texts=3472,
                 legend_sections_broken=10198, admin_lines_broken=204699)


# ------------------------------------------------------------------ readings and tokens (frozen; logic as scratch)
NUM = re.compile(r"^(?:\d+(?:/\d+)?|n)\(")
VOW = set("aeiu")
A14 = set("bdghklmnprsStz")                           # S = š (sz); g stands for g and ĝ


def cons(reading):
    """Consonants of one reading in order: sz -> S (š), s, -> X (ṣ), t, -> T (ṭ); index digits and a final x removed.
    None if anything outside a-z (plus S X T) remains. As scratch gate2.cons."""
    r = reading.replace("sz", "S").replace("s,", "X").replace("t,", "T").replace("'", "")
    r = re.sub(r"[\d₀-₉ₓ]+$", "", r)
    if r.endswith("x") and len(r) > 1:
        r = r[:-1]
    if not r or not re.fullmatch(r"[a-zSXT]+", r):
        return None
    return [c for c in r if c not in VOW]


def tok(content):
    """One ATF line -> [(kind, value)] or None if the frozen drop rule fires. Kinds: R reading (keyed), D determinative
    (keyed, empty value), N numeral (break), U unkeyed (upper case, compound, letter outside the alphabet; break).
    As scratch gate2.tok with RULE 'frozen'."""
    s = re.sub(r"\(\$.*?\$\)", " ", content)
    if "#" in s or "[" in s or "]" in s:
        return None
    s = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", s).replace("_", " ")
    if "..." in s or "…" in s:
        return None
    # PREREG-AMBIGUITY: "|compounds| without a stated value" — a value written before a compound, value(|A.B|), is kept
    # as that reading; a bare |A.B| is one unkeyed sign. As scratch.
    s = re.sub(r"([a-z0-9,']+)\(\|[^)]*\)", r"\1", s)
    s = re.sub(r"\|[^|]*\|", "CMPD", s)
    out = []
    for w in s.split():
        if w in (",", ":", ";", "/") or w.startswith("$"):
            continue
        # PREREG-AMBIGUITY: phonetic complements {+x} are treated as determinatives (empty value), as scratch.
        w = re.sub(r"\{\+?([^}]*)\}", lambda m: "-\x01" + m.group(1) + "-", w)
        for x in re.split(r"-", w):
            x = x.strip()
            if not x:
                continue
            det = x.startswith("\x01"); x = x.lstrip("\x01")
            if re.fullmatch(r"[xX]+", x):
                return None                           # drop rule: x
            if NUM.match(x) or re.fullmatch(r"[\d/]+", x):
                out.append(("N", x)); continue
            if det:
                out.append(("D", x)); continue
            for y in re.split(r"[.+]", x):
                if not y:
                    continue
                c = cons(y) if y == y.lower() else None
                out.append(("R", y) if (c is not None and set(c) <= A14) else ("U", y))
    return out


def value(sign):
    """True key: a reading's consonants; a determinative has the empty value. Unkeyed kinds are not in the key."""
    kind, v = sign
    return [] if kind == "D" else cons(v)


def keyed(sign):
    return sign[0] in ("R", "D")


# ------------------------------------------------------------------ CDLI extraction (as scratch gate2)
def load_cdli():
    csv.field_size_limit(10 ** 9)
    cat = {}
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit() and (r.get("period") or "").startswith("Ur III"):
                cat["P" + pid.zfill(6)] = ((r.get("object_type") or "").lower().strip(), (r.get("genre") or "").lower())
    legends, seen, admin, tot, alltexts = [], set(), [], Counter(), set()
    S = dict(pid=None, insec=False, buf=[], ok=True, keep=False, sealobj=False, isadmin=False)

    def flush_seal():
        buf = S["buf"]
        if buf and S["ok"]:
            k = tuple(t for l in buf for t in l)
            if k not in seen:                          # one copy per distinct sign sequence, first in dump order
                seen.add(k); legends.append((S["pid"], [t for l in buf for t in l]))
        elif buf and not S["ok"]:
            tot["legend_sections_broken"] += 1         # one broken line drops its whole legend
        S["buf"] = []; S["ok"] = True

    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                if S["pid"] in cat:
                    flush_seal()
                pid = S["pid"] = line[1:8]; S["insec"] = False; S["buf"] = []; S["ok"] = True
                if pid in cat:
                    ot, genre = cat[pid]; S["sealobj"] = ot.startswith("seal")
                    S["insec"] = S["sealobj"]; S["isadmin"] = genre.startswith("administrative") and not S["sealobj"]
                    S["keep"] = zlib.crc32(pid.encode("ascii")) % 20 == 0     # fixed 5% sample, no seed
                continue
            if S["pid"] not in cat:
                continue
            if line.startswith("@"):
                tag = line[1:].split()[0] if line[1:].strip() else ""
                # PREREG-AMBIGUITY: an @seal section ends at the next @-line other than @column (as scratch); a
                # seal object's whole text is one legend.
                if tag == "seal":
                    flush_seal(); S["insec"] = True
                elif tag != "column" and not S["sealobj"]:
                    flush_seal(); S["insec"] = False
                continue
            m = re.match(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$", line)
            if not m:
                continue
            t = tok(m.group(2))
            if S["insec"]:
                if t is None:
                    S["ok"] = False; S["buf"].append([])
                elif t:
                    S["buf"].append(t)
            elif S["isadmin"]:
                if t is None:
                    tot["admin_lines_broken"] += 1; continue
                if not t:
                    continue
                tot["admin_lines"] += 1; tot["admin_tok"] += len(t); alltexts.add(S["pid"])
                for k, _ in t:
                    tot["admin_" + k] += 1
                if S["keep"]:
                    admin.append((S["pid"], t))
    flush_seal()
    aruns = []                                         # numeral cut: each numeral-free run is a text (tablet id)
    for p, t in admin:
        cur = []
        for kt in t:
            if kt[0] == "N":
                if cur:
                    aruns.append((p, cur))
                cur = []
            else:
                cur.append(kt)
        if cur:
            aruns.append((p, cur))
    c = Counter(k for _, u in legends for k, _ in u); nl = sum(c.values()); at = tot["admin_tok"]
    mapping = dict(
        legends=len(legends), legend_source_texts=len({p for p, _ in legends}), legend_tokens=nl,
        legend_share={k: c[k] / nl for k in "RDNU"}, legend_keyed=(c["R"] + c["D"]) / nl,
        legend_reading_types=len({r for _, u in legends for k, r in u if k == "R"}),
        legend_sections_broken=tot["legend_sections_broken"],
        admin_lines=tot["admin_lines"], admin_texts=len(alltexts), admin_tokens=at,
        admin_lines_broken=tot["admin_lines_broken"], admin_share={k: tot["admin_" + k] / at for k in "RDNU"},
        admin_keyed_of_non_numeral=(tot["admin_R"] + tot["admin_D"]) / (at - tot["admin_N"]),
        sample_lines=len(admin), sample_texts=len({p for p, _ in admin}), sample_tokens=sum(len(t) for _, t in admin),
        runs=len(aruns), runs_ge2=sum(len(u) >= 2 for _, u in aruns),
        runs_ge2_tokens=sum(len(u) for _, u in aruns if len(u) >= 2),
        runs_ge2_texts=len({p for p, u in aruns if len(u) >= 2}))
    return legends, aruns, mapping


# ------------------------------------------------------------------ lexicons (as scratch lex.py)
TRL = str.maketrans({"š": "S", "ŋ": "g", "ĝ": "g", "ḫ": "h", "ṣ": "X", "ṭ": "T", "ʾ": None, "'": None})


def _norm(s):
    return re.sub(r"[\d₀-₉ₓ]", "", s.lower().translate(TRL))


def sk_cf(cf):
    """Citation form: consonants with doubled letters collapsed."""
    w = _norm(cf)
    if not re.fullmatch(r"[a-zSXT]+", w):
        return None
    return tuple(ch for i, ch in enumerate(w) if ch not in VOW and not (i and w[i - 1] == ch))


def sk_form(n):
    """Attested spelling: consonants sign by sign, nothing collapsed; determinatives removed; upper case drops it."""
    n = re.sub(r"\{[^}]*\}", "-", n); o = []
    for x in re.split(r"[-.+ ]", n):
        if not x:
            continue
        if x != x.lower():
            return None
        w = _norm(x)
        if not re.fullmatch(r"[a-zSXT]+", w):
            return None
        o += [ch for ch in w if ch not in VOW]
    return tuple(o)


def lex_of(ents):
    cf, fm = set(), set()
    for e in ents:
        s = sk_cf(e.get("cf", ""))
        if s and 1 <= len(s) <= 7 and set(s) <= A14:
            cf.add(s)
        for fo in e.get("forms", []):
            s = sk_form(fo.get("n", ""))
            if s and 1 <= len(s) <= 7 and set(s) <= A14:
                fm.add(s)
    return cf, fm


def build_lexicons():
    z = zipfile.ZipFile(LEX_OAKK_ZIP)
    src = {"oakk": json.loads(z.read("epsd2/admin/oakk/gloss-sux.json"))["entries"],
           "oldbab": json.load(open(LEX_OB, encoding="utf-8"))["entries"],
           "rimanum": json.load(open(LEX_RIM, encoding="utf-8"))["entries"]}
    sk = {nm: lex_of(e) for nm, e in src.items()}
    qcf, qfm = lex_of(json.loads(z.read("epsd2/admin/oakk/gloss-qpn.json"))["entries"])
    # PREREG-AMBIGUITY: the primary "OB administrative, spelled" is the OB glossary's spelled forms alone; the Rimanum
    # glossary enters only the citation-form lexicon (L4, as the prereg states) and the "all pooled" report row.
    return dict(ob_spelled=sk["oldbab"][1], oakk_spelled=sk["oakk"][1],
                cf_all=sk["oldbab"][0] | sk["oakk"][0] | sk["rimanum"][0],
                spelled_all=sk["oldbab"][1] | sk["oakk"][1] | sk["rimanum"][1],
                oakk_names_spelled=qfm, rimanum_cf=sk["rimanum"][0])


def density(lex, letters):
    d = {Lw: sum(len(s) == Lw for s in lex) / letters ** Lw for Lw in range(1, L.MAXW + 1)}
    return d, min((Lw for Lw in d if d[Lw] <= 0.25), default=None)


# ------------------------------------------------------------------ draws (lb_shape_ladder build, on CDLI units)
def build(units, k, form, lens):
    """units = [(text id, [token, ...])]. Returns dev, ho as ladder texts ([[tokens]]) and whether 2,300 chunks existed.
    Seeds, chunking, pick and split exactly as lb_shape_ladder build(k, form) and scratch gate2 build."""
    rng_np = np.random.default_rng(BASE + 1000 * k); rng = random.Random(BASE + 1000 * k)
    ch = B.chunk(units, lens, rng_np)
    # PREREG-AMBIGUITY (A4): a draw counts as built when 2,300 chunks exist to pick from (ladder takes min(2300, n)).
    built = len(ch) >= NCHUNK
    pick = rng_np.choice(len(ch), size=min(NCHUNK, len(ch)), replace=False)
    ch = [ch[i] for i in pick]
    T = sum(len(t) for _, t in ch)
    if form == "chunk":
        items = ch
    else:
        # "Whole" rows take whole texts (all units, as scratch, including 1-token ones) to the same token budget.
        order = list(range(len(units))); rng.shuffle(order); items, n = [], 0
        for i in order:
            if n >= T:
                break
            items.append(units[i]); n += len(units[i][1])
    ids = sorted({tid for tid, _ in items}); rng.shuffle(ids); dev_ids = set(ids[:len(ids) // 2])
    dev = [[t] for tid, t in items if tid in dev_ids]; ho = [[t] for tid, t in items if tid not in dev_ids]
    return dev, ho, built


def segs(unit):
    """Keyed consonant segments of one unit (as scratch gate2 segs): R adds its consonants, D nothing, else a break."""
    out, cur = [], []
    for k, r in unit:
        if k == "R":
            cur += cons(r)
        elif k == "D":
            pass
        else:
            out.append(cur); cur = []
    out.append(cur)
    return [c for c in out if c]


def shape_stats(units, lens, n=13100, draws=3):
    """Descriptive share and segment columns (13,100 tokens, 3 draws), as scratch gate2 stats. Gates nothing."""
    res = {}
    for mode in ("whole", "m77chunk"):
        rows = []
        for d in range(draws):
            rng = random.Random(1000 + d); order = list(range(len(units))); rng.shuffle(order)
            texts, c = [], 0
            for i in order:
                u = units[i]
                if len(u) < 2:
                    continue
                if mode == "whole":
                    parts = [u]
                else:
                    parts, j = [], 0
                    while len(u) - j >= 2:
                        Lc = min(rng.choice(lens), len(u) - j); parts.append(u[j:j + Lc]); j += Lc
                for p in parts:
                    texts.append(p); c += len(p)
                if c >= n:
                    break
            bg = Counter((a, b) for t in texts for a, b in zip(t, t[1:]))
            share = sum(v for _, v in bg.most_common(50)) / max(1, sum(bg.values()))
            sg = [s for t in texts for s in segs(t)]; tc = sum(len(s) for s in sg)
            rows.append(dict(tokens=c, texts=len(texts), top50_share=share, cons_per_seg=tc / len(sg),
                             **{f"cons_in_segs_ge{Lw}": sum(len(s) for s in sg if len(s) >= Lw) / tc for Lw in (3, 4, 5)}))
        res[mode] = rows
    return res


# ------------------------------------------------------------------ label-free part (K1; no IC)
def labelfree():
    t0 = time.time()
    legends, aruns, mapping = load_cdli()
    lens = B.m77_lengths()
    lexs = build_lexicons()
    homer = {t for t in B.build_lexicon()[0] if "q" not in t}     # sealed Homer lexicon, q-free (density over 9^L)
    dens = {}
    for nm in T_DENS:
        lx = homer if nm == "homer_qfree" else lexs[nm]
        d, lmin = density(lx, 9 if nm == "homer_qfree" else 14)
        dens[nm] = dict(skeletons=len(lx), density={str(Lw): v for Lw, v in d.items()}, rule_lmin=lmin,
                        table=T_DENS[nm], table_skeletons=T_SKEL[nm], table_lmin=T_LMIN[nm])
    dens["rimanum_cf"] = dict(skeletons=len(lexs["rimanum_cf"]))
    units = {"legends": legends, "admin": aruns}
    draws, excess = {}, {}
    for lab in ("legends", "admin"):
        for form in ("chunk", "line"):
            ex, sh, nk, sc, nb = [], [], [], [], 0
            for k in range(1, NSUB + 1):
                dev, ho, built = build(units[lab], k, form, lens)
                nb += built
                draws[(lab, form, k)] = (dev, ho, built)
                hu = [t[0] for t in ho]
                e, s = F.excess(hu, F.S_BASE + k)
                ex.append(e); sh.append(s); nk.append(sum(map(len, hu)))
                sc.append(sum(len(x) for t in hu for x in segs(t)))
            excess[f"{lab} {form}"] = dict(excess=ex, excess_min=min(ex), excess_max=max(ex),
                                           excess_median=float(np.median(ex)), share_median=float(np.median(sh)),
                                           heldout_tokens_median=int(round(float(np.median(nk)))),
                                           heldout_key_consonants_median=int(np.median(sc)), built=nb)
    nbars = sorted({4014, excess["legends chunk"]["heldout_tokens_median"],
                    excess["admin chunk"]["heldout_tokens_median"]})
    m77 = {str(nb): {q: v for q, v in F.m77_target(nb).items() if q in ("e_M", "n_bar")} for nb in nbars}
    shape = {lab: shape_stats([u for _, u in units[lab]], lens) for lab in units}
    tables = dict(mapping=mapping, mapping_table=T_MAPPING, density=dens, excess=excess, m77_excess=m77, shape=shape)
    # ---- A2
    fails = []
    for q, v in T_COUNTS.items():
        if mapping[q] != v:
            fails.append(f"count {q} = {mapping[q]} (table {v})")
    if mapping["legend_keyed"] < T_COVER:
        fails.append(f"legend coverage {mapping['legend_keyed']:.4f} < {T_COVER}")
    for nm, row in dens.items():
        for Lw, v in T_DENS.get(nm, {}).items():
            if abs(row["density"][str(Lw)] - v) > T_DENS_TOL:
                fails.append(f"density {nm} L{Lw} = {row['density'][str(Lw)]:.4f} (table {v})")
    if dens["ob_spelled"]["rule_lmin"] != 3:
        fails.append(f"primary rule LMIN = {dens['ob_spelled']['rule_lmin']} (must be 3)")
    for lab, tv in T_EXCESS.items():
        m = excess[f"{lab} chunk"]["excess_median"]
        if abs(m - tv) > T_EXCESS_TOL:
            fails.append(f"{lab} chunk excess median {m:.4f} (table {tv})")
    K1 = dict(passed=not fails, A2_failures=fails, tables=tables)
    lexs_run = {nm: lexs[nm] for nm in ("ob_spelled", "oakk_spelled", "cf_all")}
    return K1, draws, lexs_run, homer, round(time.time() - t0, 1)


# ------------------------------------------------------------------ scored job (worker)
LEXS = None


def init(lexs):
    global LEXS
    LEXS = lexs


def _kept(freq, rng):
    """Kept-sign order as sealed R1 (sorted, shuffled by the N1 generator, coverage loop at 1.0)."""
    order = sorted(freq); rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= 1.0:
            break
        kept.append(s); c += freq[s]
    return kept


def score_job(a):
    """One (check or cell, draw). a: task, k, name, ho, freq, vals, lex, lmin, seeds, sealed_rng, partial."""
    t0 = time.time()
    lex = LEXS[a["lex"]]
    L.LMIN = a["lmin"]
    try:
        freq, ho = a["freq"], a["ho"]
        rng = random.Random(a["seed_n1"])
        kept = _kept(freq, rng)
        true = {s: list(a["vals"][s]) for s in kept}
        cl = L.classes(kept, true); cl_of = {s: len(true[s]) for s in kept}
        H = L.IC(ho, lex)
        rec = dict(task=a["task"], name=a["name"], k=a["k"], lmin=a["lmin"], lex=a["lex"], n_ho=len(ho),
                   n_keyed=len(kept), tokens_ho=sum(len(w) for t in ho for w in t))
        if a["task"] == "K2":
            # PREREG-AMBIGUITY: "tested against a fresh N1" read as the N1 of the claimed key (within-bin permutations
            # of the claimed key's values, the claimant's own test); kept order from the draw's N1 seed as every cell.
            claimed = L.permute_in_class_bins(true, cl, freq, random.Random(a["seed_claim"]))
            t = H.full(claimed); rf = random.Random(a["seed_fresh"])
            n1 = np.array([H.full(L.permute_in_class_bins(claimed, cl, freq, rf)) for _ in range(NPERM)])
            p99 = float(np.quantile(n1, .99))
            rec.update(claimed_ic=t, n1_mean=float(n1.mean()), n1_p99=p99, wrong_key_pass=bool(t > p99))
            return dict(rec, seconds=round(time.time() - t0, 1))
        t_ho = H.full(true); shape = H.shape(true)
        n1 = np.array([H.full(L.permute_in_class_bins(true, cl, freq, rng)) for _ in range(NPERM)])
        if a["sealed_rng"]:                            # K0: one generator in sealed R1 order
            rs = rsn = rng; prs = [rng] * len(LEVELS)
        else:
            rs, rsn = random.Random(a["seed_scr"]), random.Random(a["seed_scr_n1"])
            prs = [random.Random(s) for s in a["seed_part"]] if a["partial"] else None
        Hs = L.IC(L.unigram(ho, rs), lex); t_sh = Hs.full(true)
        n1s = np.array([Hs.full(L.permute_in_class_bins(true, cl, freq, rsn)) for _ in range(NPERM)])
        p99, p99s = float(np.quantile(n1, .99)), float(np.quantile(n1s, .99))
        m = float(n1.mean())
        rec.update(shape=shape, loose_token_share=0.0, true_ic=t_ho, n1_mean=m, n1_p99=p99, W=p99 - m,
                   signal=t_ho - m, margin=t_ho - p99, refute=bool(t_ho > p99), shuffled_true=t_sh,
                   shuffled_n1_mean=float(n1s.mean()), shuffled_n1_p99=p99s, shuffled_refute=bool(t_sh > p99s))
        if a["partial"]:                               # control ii as sealed ladder, one generator per level
            part = {}
            for f, pr in zip(LEVELS, prs):
                v = []
                for _ in range(NPART):
                    keep = set(pr.sample(kept, int(f * len(kept))))
                    v.append(H.full(L.shuffle_in_class(true, [s for s in kept if s not in keep], cl_of, pr)))
                part[f] = float(np.mean(v))
            part[1.0] = t_ho
            rec.update(partial=part, partial_rise=bool(all(part[x] < part[y]
                                                           for x, y in zip(LEVELS, LEVELS[1:] + (1.0,)))))
        return dict(rec, seconds=round(time.time() - t0, 1))
    finally:
        L.LMIN = LMIN_SEALED


def run_jobs(jobs, lexs):
    with Pool(NWORK, initializer=init, initargs=(lexs,)) as P:
        return P.map(score_job, jobs, chunksize=1)


def ur3_job(task, name, k, dev, ho, lex, lmin, partial=False):
    freq = Counter(s for t in dev + ho for w in t for s in w if keyed(s))
    vals = {s: value(s) for s in freq}
    return dict(task=task, name=name, k=k, ho=ho, freq=freq, vals=vals, lex=lex, lmin=lmin, sealed_rng=False,
                partial=partial, seed_n1=BASE + 1000 * k + 7, seed_scr=BASE + 600_000 + k,
                seed_scr_n1=BASE + 610_000 + k, seed_part=[BASE + 700_000 + 1000 * k + j for j in range(4)],
                seed_claim=BASE + 500_000 + k, seed_fresh=BASE + 510_000 + k)


def summ(rows):
    """Sealed lb_formula_dial summarise (P out of 20; unbuilt draws are absent, so non-passes) plus the grade."""
    s = F.summarise(rows) if rows else dict(scored=0, P=0, scrambled_passes=0, interpretable=True, cell_pass=False)
    s.pop("mean_loose_token_share", None)
    P = s["P"]
    s["grade"] = "pass" if P >= PASS else ("clear_fail" if P <= CLEAR_FAIL else "edge")
    return s


# ------------------------------------------------------------------ guards (A5) and IO
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
    # PREREG-AMBIGUITY: "free memory" read as available memory: macOS vm_stat free + inactive + speculative pages
    # over hw.memsize; elsewhere MemAvailable / MemTotal.
    if sys.platform == "darwin":
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        page = int(re.search(r"page size of (\d+)", out).group(1))
        g = lambda name: int(re.search(rf"{name}:\s+(\d+)", out).group(1))
        avail = (g("Pages free") + g("Pages inactive") + g("Pages speculative")) * page
        total = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
        return avail / total
    mi = dict(l.split(":", 1) for l in open("/proc/meminfo"))
    return int(mi["MemAvailable"].split()[0]) / int(mi["MemTotal"].split()[0])


def a5():
    """A5: the Indus compute lock (board/run.sh) is held by this process's ancestry, and free memory >= 20%."""
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
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=_conv)


def roundtrip(x):
    return json.loads(json.dumps(x, default=_conv))


def stop(out, path, msg):
    out.update(kill_passed=False, stop=msg)
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(1)


# ------------------------------------------------------------------ readings (frozen wording)
R_K3_FAIL = ("the bench has no power on cuneiform at Indus formula excess and this size; cause not separated "
             "(pipeline or formulae).")
R_K3_EDGE = "power not shown at the bar"
R_L1_PASS = ("the refute standard survives real formulae and names, at reading level. This does not show the language "
             "is identified (Spanish passed in lb_wrong_lexicon). This is an upper bound from an editor-resolved "
             "reading, a same-convention lexicon and segments twice Linear B's. It does not show why yj_ic_refute or "
             "scott_ic_refute lost power.")
R_L1_FAIL = ("on a formulaic, name-heavy seal corpus a true reading does not beat its shuffles. Fit-refute has no "
             "stated power on seal legends at 1.6 x Indus excess. It does not decide Indus-level corpora. Cause not "
             "separated (excess, names missing from the lexicon, lexicon period).")
R_L1_EDGE = "not decided."
R_ORACLE = "The oracle key sets the weight of each outcome: a fail is strong, and a pass is an upper bound."


# ------------------------------------------------------------------ modes
def kill():
    path = HERE / "kill.json"
    assert not path.exists(), "kill.json exists: no rerun after any IC is seen (prereg Aborts)"
    out = dict(prereg="docs/prereg/ur3_legend_refute.md", nwork=NWORK)
    why, fm = a5(); out["A5"] = dict(free_mem_frac=fm, failures=why)
    if why:
        print("A5: do not start:", "; ".join(why)); sys.exit(2)      # nothing computed, nothing written
    t0 = time.time()
    # ---- K0: study scorer path on Linear B + Homer, sealed R1 seeds, vs sealed full.json R1 to 1e-9 (A1)
    homer_full = B.build_lexicon()[0]
    sealed = {r["k"]: r for r in json.load(open(SEALED_R1))["runs"] if r["rung"] == "R1"}
    jobs = []
    for k in range(1, NSUB + 1):
        dev, ho, _ = L.build(k, "chunk")
        freq = Counter(s for t in dev + ho for w in t for s in w)
        jobs.append(dict(task="K0", name="K0", k=k, ho=ho, freq=freq, vals={s: B.true_value(s) for s in freq},
                         lex="homer", lmin=LMIN_SEALED, sealed_rng=True, partial=True,
                         seed_n1=L.SEED + 1000 * k + 7 * F.R1_INDEX))
    k0 = run_jobs(jobs, {"homer": homer_full})
    per, ok = [], True
    for r in k0:
        s = sealed[r["k"]]
        d = {q: abs(r[q] - s[q]) for q in ("true_ic", "n1_mean", "n1_p99", "shuffled_true", "shuffled_n1_p99")}
        d.update({f"partial_{f}": abs(r["partial"][f] - s["partial"][str(f)]) for f in LEVELS + (1.0,)})
        mx = max(d.values()); ok = ok and mx <= 1e-9 and r["tokens_ho"] == s["tokens_ho"]
        per.append(dict(k=r["k"], max_abs_diff=mx, tokens_equal=r["tokens_ho"] == s["tokens_ho"],
                        refute=r["refute"], shuffled_refute=r["shuffled_refute"]))
    P0 = sum(r["refute"] for r in k0); C0 = sum(r["shuffled_refute"] for r in k0)
    out["K0"] = dict(P=P0, scrambled_passes=C0, match_1e9=ok, passed=bool(ok and P0 == NSUB and C0 == 0),
                     per_draw=per, seconds=round(time.time() - t0, 1))
    print(json.dumps({q: out["K0"][q] for q in ("P", "scrambled_passes", "match_1e9", "passed")}), flush=True)
    if not out["K0"]["passed"]:
        stop(out, path, "A1: K0 does not reproduce lb_shape_ladder R1")
    # ---- K1: tables and counts, no IC (A2)
    K1, draws, lexs, _, secs = labelfree()
    out["K1"] = dict(K1, seconds=secs)
    print(json.dumps(dict(K1_passed=K1["passed"], A2_failures=K1["A2_failures"],
                          counts={q: K1["tables"]["mapping"][q] for q in T_COUNTS},
                          excess_medians={q: K1["tables"]["excess"][q]["excess_median"] for q in K1["tables"]["excess"]}),
                     indent=1, default=_conv), flush=True)
    if not K1["passed"]:
        stop(out, path, "A2: recomputed tables differ from the sealed v2 tables; stop and redraft")
    adm = {k: draws[("admin", "chunk", k)] for k in range(1, NSUB + 1)}
    # ---- K2: one N1 draw as the claimed key vs a fresh N1, administrative chunks (A3)
    t0 = time.time()
    k2 = run_jobs([ur3_job("K2", "K2", k, d[0], d[1], KILL_LEX, KILL_LMIN) for k, d in adm.items() if d[2]], lexs)
    n2 = sum(r["wrong_key_pass"] for r in k2)
    out["K2"] = dict(wrong_key_passes=n2, scored=len(k2), passed=bool(n2 <= K2_MAX),
                     per_draw=[{q: r[q] for q in ("k", "claimed_ic", "n1_mean", "n1_p99", "wrong_key_pass")} for r in k2],
                     seconds=round(time.time() - t0, 1))
    print(json.dumps({q: out["K2"][q] for q in ("wrong_key_passes", "scored", "passed")}), flush=True)
    if not out["K2"]["passed"]:
        stop(out, path, "A3: K2 wrong-key pass rate above 1 of 20")
    # ---- K3: planted true reading on administrative chunks, scrambled control, partial keys (A3, K3 fail)
    t0 = time.time()
    k3 = run_jobs([ur3_job("K3", "K3", k, d[0], d[1], KILL_LEX, KILL_LMIN, partial=True)
                   for k, d in adm.items() if d[2]], lexs)
    s3 = summ(k3)
    pm = {str(f): float(np.mean([r["partial"][f] for r in k3])) if k3 else None for f in LEVELS + (1.0,)}
    rising = bool(k3) and all(pm[str(x)] < pm[str(y)] for x, y in zip(LEVELS, LEVELS[1:] + (1.0,)))
    k3_pass = bool(s3["P"] >= PASS and rising and s3["scrambled_passes"] <= CTRL_MAX)
    if k3_pass:
        reading = None
    elif CLEAR_FAIL < s3["P"] < PASS:
        # PREREG-AMBIGUITY: at 13-15 the reading is "power not shown at the bar" and it is still a K3 fail (legend
        # cells not run); the frozen K3-fails reading is recorded beside it.
        reading = f"{R_K3_EDGE}; K3 fail: {R_K3_FAIL}"
    else:
        reading = R_K3_FAIL
    out["K3"] = dict(cell=s3, partial_means=pm, partial_rising=rising, passed=k3_pass, reading=reading,
                     runs=[{q: v for q, v in r.items() if q != "seconds"} for r in k3], seconds=round(time.time() - t0, 1))
    print(json.dumps(dict(P=s3["P"], scrambled=s3["scrambled_passes"], partial_means=pm, rising=rising,
                          passed=k3_pass)), flush=True)
    if s3["scrambled_passes"] > CTRL_MAX:
        stop(out, path, "A3: K3 scrambled control above 1 of 20")
    if not k3_pass:
        stop(out, path, "K3 fail: the legend cells are not run. " + out["K3"]["reading"])
    out["kill_passed"] = True
    dump(out, path); print("kill passed; full may run", flush=True)


def full():
    kp, path = HERE / "kill.json", HERE / "full.json"
    assert kp.exists(), "kill.json missing: run `kill` first"
    kr = json.load(open(kp))
    assert kr.get("kill_passed") is True and all(kr.get(q, {}).get("passed") is True for q in ("K0", "K1", "K2", "K3")), \
        "kill.json does not show every check passed: full run refused"
    assert not path.exists(), "full.json exists: no rerun after any IC is seen (prereg Aborts)"
    why, fm = a5()
    if why:
        print("A5: do not start:", "; ".join(why)); sys.exit(2)
    t0 = time.time()
    K1, draws, lexs, _, _ = labelfree()
    assert roundtrip(K1) == {q: v for q, v in kr["K1"].items() if q != "seconds"}, \
        "label-free rebuild differs from kill.json"
    jobs, built = [], {}
    for name, (form, lex, lmin) in CELLS.items():
        built[name] = 0
        for k in range(1, NSUB + 1):
            dev, ho, ok = draws[("legends", form, k)]
            if not ok:
                continue                                # A4: unbuilt draw counts as a non-pass
            built[name] += 1
            jobs.append(ur3_job("cell", name, k, dev, ho, lex, lmin))
    res = run_jobs(jobs, lexs)
    cells = {}
    for name in CELLS:
        rows = [r for r in res if r["name"] == name]
        cells[name] = dict(summ(rows), built=built[name], form=CELLS[name][0], lexicon=CELLS[name][1],
                           lmin=CELLS[name][2], role="primary" if name == "L1" else "report only")
    c1 = cells["L1"]
    if c1["scrambled_passes"] > CTRL_MAX:
        # PREREG-AMBIGUITY: no frozen reading covers an L1 scrambled control above 1 of 20; the cell does not pass
        # (sealed bar) and is recorded as not interpretable.
        l1 = "L1 scrambled control above 1 of 20: L1 not interpretable; " + R_L1_EDGE
    elif c1["grade"] == "pass":
        l1 = R_L1_PASS
    elif c1["grade"] == "clear_fail":
        l1 = R_L1_FAIL
    else:
        l1 = R_L1_EDGE
    readings = dict(oracle=R_ORACLE, L1_grade=c1["grade"], L1_cell_pass=c1["cell_pass"], L1=l1,
                    report_only={n: dict(P=cells[n]["P"], scrambled_passes=cells[n]["scrambled_passes"],
                                         grade=cells[n]["grade"], note="describes; decides nothing")
                                 for n in CELLS if n != "L1"})
    out = dict(prereg="docs/prereg/ur3_legend_refute.md", cells=cells, readings=readings,
               runs=[{q: v for q, v in r.items() if q != "seconds"} for r in res], seconds=round(time.time() - t0, 1))
    print(json.dumps(dict(cells={n: {q: c[q] for q in ("P", "scrambled_passes", "grade", "median_W")}
                                 for n, c in cells.items()}, L1=l1), indent=1, default=_conv), flush=True)
    dump(out, path)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "kill":
        kill()
    elif mode == "full":
        full()
    else:
        sys.exit("usage: run.py kill|full")
