"""Certify size curve on Old Assyrian (prereg docs/prereg/certify_size_curve.md, SEALED v4, tag `certify_size_curve`).
Run (from the repo root, detached, under the Indus compute lock; A4 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/certify_size_curve/run.py kill     # stage 1: aborts, K0 -> kill.json
  board/run.sh .venv/bin/python -I experiments/certify_size_curve/run.py k1       # stage 2: K1 -> k1_targets.json, k1.json
  board/run.sh .venv/bin/python -I experiments/certify_size_curve/run.py real     # stage 3: K2, bar C, K3, fixed sets, 32 u
  board/run.sh .venv/bin/python -I experiments/certify_size_curve/run.py extras   # record-only: ceiling, set Q, pool L
  board/run.sh .venv/bin/python -I experiments/certify_size_curve/run.py k4       # only under reading B, at s*
Workers: env NWORK (default 4, capped at 4).

Order (the prereg's; K0 first, and no real-text gain or dose exists before K0 is graded):
  kill:   A4 + seal check; A7 (hashes); label-free corpus build, A9, A2 (pool, set Q, key purity, density, blocks, clean
          counts) + F4; A1 (sealed lift_score K0 draw-1 gain on Linear B, to 1e-9); F3 (trigram-only Hit@1); A6;
          K0a full dose -> reading 1 stops; F1; K0a low dose (F5) -> reading 2 stops; K0b with its 16 u plant 1 first
          (F6); K0c; step-1 reading (F7). Reading 3: real K3 at 1 u and 16 u once, record-only. Readings 1-4: nothing
          else ever runs.
  k1:     refuses unless kill.json licenses step 2. All dose targets on disk first, then F2 + bisection, then gains.
  real:   refuses unless k1.json is done. Sizes smallest first; labels, curve reading, bound; 32 u last, record-only.
  extras: refuses unless real.json is done. Ceiling lexicon, uncertain-period check (set Q), pool L. Grades nothing.
  k4:     refuses unless real.json holds reading B. 9 N2 + 3 N3 keys per draw at s*, bars A and B.
Each mode refuses to start if its own output exists. Outputs hold per-draw and per-key aggregates only; clustered SEs
and paired differences are computed in memory and no per-position array is saved. Hit@1 and Hit@1 lift are reported
on every cell beside G; G grades the bars.

Reuse. Nothing is loaded at import. The scoring machinery is copied from the sealed experiments/lift_score/run.py and
is unchanged except where the prereg says so (11 letters, tablet folds, 5 N1 keys, plant spelling and vocabulary,
clustered SE, bar C as a paired difference). Sealed lb_shape_ladder / lb_certify functions are imported by path.
The Old Assyrian extraction follows the drafter's scratch scripts; the prereg wins where they differ. Every judgement
call is marked PREREG-AMBIGUITY.

No Indus step: M77 enters only as text lengths (lb_certify.m77_lengths). splits_v2, claim-bench key files and
saao.zip are never opened (A5 / A7 are enforced by an audit hook on file opens). No key values are printed or written.
"""
import csv, hashlib, importlib.util, json, math, os, random, re, statistics, subprocess, sys, time, unicodedata
import zipfile, zlib
from collections import Counter, defaultdict
from itertools import product
from math import log
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PREREG = "docs/prereg/certify_size_curve.md"; TAG = "certify_size_curve"
NWORK = max(1, min(4, int(os.environ.get("NWORK", "4"))))
BASE = 20270201                                       # study base (prereg Seeds)
BASE_LS = 20270101                                    # lift_score base, used by A1 only
UNIT = 2300                                           # 1 u = 2,300 chunks
SIZES = (1, 2, 4, 8, 16); REC32 = 32
NDRAWS = {1: 20, 2: 20, 4: 13, 8: 6, 16: 3, 32: 1}
NBLOCKS = {1: 53, 2: 26, 4: 13, 8: 6, 16: 3, 32: 1}
PASSBAR = {1: 16, 2: 16, 4: 11, 8: 5, 16: 3}
K1_PLANTS = {1: 20, 2: 20, 4: 10, 8: 10, 16: 10}
CLEAN_TABLE = {1: 1614, 2: 2725, 4: 4221, 8: 5668, 16: 7536, 32: 8675}
A2_POOL = dict(texts=4435, lines=73135, tokens=445733, sign_types=207)
A2_Q = dict(texts_kept=36, tokens=1143)
A2_PURITY, A2_PURITY_TOL, A2_DENS4, A2_DENS_TOL, A2_CLEAN_TOL = 0.981, 0.005, 0.110, 0.01, 0.25
W_BY_LEN = {4: 1612, 5: 896, 6: 259, 7: 48}
GRID0 = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
GRID_F1 = (8.0, 16.0)
LAM_MARGIN = 0.01
NFOLD = 5
N1_KEYS, NPERMLEX = 5, 5
VOC, VOC_F3 = 500, 2000                               # plant vocabulary: min(VOC x s, |W|)
LMIN, MAXW = 4, 7
EM_ITERS, EM_ALPHA, RHO0, RHO_MIN, RHO_MAX = 15, 0.01, 0.5, 0.001, 0.999
D_TOL, BISECT_STEPS = 0.005, 12
N3_RESTARTS, N3_SWAPS, N3_RHO = 3, 3000, 0.05
N2_RESTARTS, N2_ITERS = 3, 3000
K0_GAIN, GAIN_BAR, CTRL_BAR = 0.10, 0.02, 0.005
Z1 = 1.645
LOW_DOSE, LOW_DOSE_F5, F5_OFF = 0.25, 0.125, 50000
A1_TOL, A6_TOL = 1e-9, 1e-9
F4_MIN, F3_MAX = 900, 60
F6_DROP, F6_STOP = 60.0, 90.0
EST = {1: 20, 2: 35, 4: 60, 8: 110, 16: 220, 32: 330}  # prereg Cost, seconds per key cell (2 u interpolated)
K1_EQ = 3.8                                           # one K1 plant in key-cell equivalents (see project_hours)
MEM_GUARD = 0.20
LOCK = ROOT / "board/compute.lock"
RAW = ROOT / "experiments/short_labels/raw/cdli"
OGSL = HERE / "raw/ogsl/ogsl.zip"
OGSL_SHA = "46d8a29c11c351baa922c912c4472d6fb7ec7f79e76d4d473f29d58d4caf860f"
SKEL = HERE / "raw/saao/neoass_skeletons.tsv"
SKEL_SHA = "3ab28cf9dae963f5930298e13e75ddde3790ea41ad5119f4c7faa76f14aa8823"
LS_KILL = ROOT / "experiments/lift_score/kill.json"
P_T = "Old Assyrian (ca. 1950-1850 BC)"; P_Q = P_T + " ?"
GENRES = ("Letter", "Legal", "Administrative", "")
OBJ = ("tablet", "tablet & envelope")
SH = "Š"                                         # the letter Š, one code point
OA_ALPHA = sorted("PTKSMNLRHW" + SH)
LB_ALPHA = list("dkmnpqrstz")

# ------------------------------------------------------------------ frozen readings (verbatim from the prereg)
R1 = "The word-and-fragment score does not pass its planted test on Old Assyrian. Nothing is learned about size."
R2 = "No failing cell to rescue at 1 u: this script's shape is easier than Linear B's. Redraft."
R3 = ("Even a planted language at the K0b low dose ({dose}) stays hidden at 128,000 tokens. More text does not rescue "
      "this score. The restoration route stays closed up to that size for this score; a real-text null would add nothing.")
R3_CTRL = "A control with no language also passed its bar at {size}."
R4 = "The gain is not specific beyond one draw. The size question cannot be asked with this score."
R5 = ("At 128,000 tokens the score gains for keys, lexicons or texts with no language. The usable range of this score "
      "ends below that size.")
RA = ("Unpowered at every size. At the lexicon fit the true Old Assyrian key actually reaches with a Neo-Assyrian "
      "lexicon, a planted language does not raise restoration by 0.02 nats per sign with up to {N} tokens. The route "
      "needs more than {N} tokens or a closer lexicon; this study cannot say which.")
RB = ("On Old Assyrian with a Neo-Assyrian lexicon, the true key's fit to the lexicon shows from about {T} sign tokens "
      "in M77-length chunks.")
RC = "Not stable: the gain appears at {T} and is gone, or not specific, at {T2}. No threshold is stated."
RD = ("From {T} a gain exists but it is not specific to the key or the lexicon. No size up to {N} shows the true key's "
      "fit.")
RE = ("No size up to {N} tokens shows the true key's fit, though a planted language at the same dose is visible from "
      "{T}.")
R_ALWAYS = ("This is one script, one lexicon and an oracle key. It is an order of magnitude for other scripts, not a "
            "threshold. M77 holds 13,398 tokens.")
R_2027 = ("G is this study's gate. Hit@1 is the 2027-clause measure and is reported on every cell. A G pass alone does "
          "not meet the 2027 clause.")
R_INDUS = "No Indus key is scored. No outcome supports or counts against any Indus key, and none licenses a run of one."

# ------------------------------------------------------------------ per-process state (set by init / setup)
L = None                                              # sealed lb_shape_ladder module
B = None                                              # sealed lb_certify module
_close = None                                         # corpus.build._close (near-copy rule)
ALPHA = OA_ALPHA                                      # the key letters in use (A1 switches to Linear B and back)
W47 = None                                            # primary word list W: sorted skeletons of 4 to 7 consonants
KEY = None                                            # true key: sign name -> tuple of letters (pool T modal value)
SEQ = None                                            # pool T chunks in the one tablet order: [(tablet id, signs)]
SEQ_L = None                                          # the same, letters only (pool L)
QSEQ = None                                           # set Q chunks
CEIL = None                                           # tablet id -> Counter of word skeletons (extras mode only)
LEXS = {}
INIT_ERR = None
_HELD = {}


def load_sealed():
    """As lift_score: lb_certify on the path (the ladder does `import run as base`) and the sealed ladder loaded
    under its own name. Loads code only, no data."""
    global L, B, _close
    if L is not None:
        return
    for p in (str(ROOT / "experiments/lb_certify"), str(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("ladder", ROOT / "experiments/lb_shape_ladder/run.py")
    mod = importlib.util.module_from_spec(spec); sys.modules["ladder"] = mod; spec.loader.exec_module(mod)
    from corpus.build import _close as cl             # near-copy rule; nothing else used
    assert mod.LMIN == LMIN and mod.MAXW == MAXW, "sealed ladder constants changed"
    assert sorted(mod.base.KEYLET) == LB_ALPHA, "Linear B key alphabet changed"
    L, B, _close = mod, mod.base, cl


# ------------------------------------------------------------------ A5 / A7: only the files the prereg names
_A5_ALLOW = ("experiments/lb_certify/", "experiments/lb_shape_ladder/", "experiments/cognate_decipher/ext/greek/",
             "experiments/short_labels/raw/cdli/", "corpus/", "board/compute.lock/", ".venv/",
             "sources/paragorth_Indus-/data/codelib/linear_b.jsonl", "data/m77_texts.jsonl",
             "experiments/lift_score/kill.json", PREREG, "docs/prereg/HASHES.txt",
             "experiments/certify_size_curve/raw/ogsl/ogsl.zip",
             "experiments/certify_size_curve/raw/saao/neoass_skeletons.tsv",
             "experiments/certify_size_curve/run.py")
_A5_OUT = re.compile(r"^experiments/certify_size_curve/(?:kill|k1_targets|k1|real|extras|k4)\.json(?:\.tmp)?$")
_A5_ON = False


def a5_hook():
    """A5 / A7 / Indus rule: inside the repo only the files this study needs may be opened; any other repo file
    (splits_v2, any key file, any other lexicon file) raises before it is read. saao.zip is refused wherever it is."""
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
        if os.path.basename(full).lower() == "saao.zip":
            raise RuntimeError("A7: the study never opens saao.zip")
        if not full.startswith(root):
            return
        rel = full[len(root):].replace(os.sep, "/")
        if "splits" in rel or not (_A5_OUT.match(rel) or any(rel == a or (a.endswith("/") and rel.startswith(a))
                                                               for a in _A5_ALLOW)):
            raise RuntimeError("A5: the study tried to open a repo file outside its data list: " + rel)

    sys.addaudithook(hook)


# ------------------------------------------------------------------ guard (copied from lift_score)
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
    # PREREG-AMBIGUITY: "free memory" (A4) read as available memory, as lift_score: macOS vm_stat free + inactive +
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
            why.append(f"compute lock held by pid {lp}, not by this run (run under board/run.sh)")
    fm = free_mem_frac()
    if fm < MEM_GUARD:
        why.append(f"free memory {fm:.1%} below the {MEM_GUARD:.0%} guard")
    return why, fm


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal_check():
    # PREREG-AMBIGUITY: not a prereg abort (as lift_score). Before anything is computed the run checks that the
    # prereg file on disk is the sealed one (its sha256 is on a HASHES.txt line with tag certify_size_curve).
    h = sha256_of(ROOT / PREREG); ok = False
    for line in open(ROOT / "docs/prereg/HASHES.txt"):
        f = line.split()
        if len(f) >= 4 and f[0] == h and f[1] == PREREG and f[-1] == TAG:
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
    out.update(stop=msg, status="stopped")
    out.setdefault("license", {})["step2"] = False
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(code)


def say(name, **kw):
    print(name + ": " + json.dumps(kw, default=_conv), flush=True)


def med(xs, nd=4):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), nd) if xs else None


def r4(xs):
    return [None if x is None else round(x, 4) for x in xs]


# ------------------------------------------------------------------ Old Assyrian extraction (label-free)
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
NUM = re.compile(r"^(?:\d+(?:/\d+)?|n)\(")
VOW = set("aeiu")
MERGE = {"b": "P", "p": "P", "d": "T", "t": "T", "ṭ": "T", "g": "K", "k": "K", "q": "K", "s": "S", "ṣ": "S", "z": "S",
         "š": SH, "m": "M", "n": "N", "l": "L", "r": "R", "h": "H", "ḫ": "H", "w": "W"}
DROP = set("yj'ʾʿ")
LINE = re.compile(r"^(\d+[a-z']*(?:\.[a-z0-9']+)*)\.\s+(.*)$")


def norm_reading(y):
    """CDLI ASCII reading -> sign-list value spelling (sz -> š, s, -> ṣ, t, -> ṭ, index digits -> subscripts)."""
    r = y.replace("sz", "š").replace("s,", "ṣ").replace("t,", "ṭ").replace("'", "ʾ")
    m = re.fullmatch(r"([^\d]+?)(\d+|x)?", r)
    if not m:
        return None
    base, idx = m.group(1), m.group(2)
    if idx == "x":
        return base + "ₓ"
    if idx and idx != "1":
        return base + idx.translate(SUB)
    return base


def cons_full(r):
    """Consonant letters of a reading (index stripped), unmerged; None if it holds a letter outside the alphabet."""
    b = re.sub(r"[₀-₉ₓ]+$", "", r)
    out = []
    for ch in b:
        if ch in VOW or ch in DROP:
            continue
        if ch not in MERGE:
            return None
        out.append(ch)
    return out


def tok(content):
    """One ATF line -> [(kind, reading)] or None when the frozen drop rule fires (#, [ ], x, ...). Kinds: R syllabic
    reading, D determinative, L logogram (inside _ _), N numeral, U upper case or compound, W word-divider wedge.
    As the drafter's gate3.tok, which made the Measured tables."""
    s = re.sub(r"\(\$.*?\$\)", " ", content)
    if "#" in s or "[" in s or "]" in s or "..." in s or "…" in s:
        return None
    s = re.sub(r"[<>!?*]", "", s)
    # PREREG-AMBIGUITY: "compounds without a stated value": value(|A.B|) is kept as that reading; a bare |A.B| is one
    # unread sign (a break). Phonetic complements {+x} are determinatives (empty value). As the scratch.
    s = re.sub(r"([a-z0-9,']+)\(\|[^)]*\)", r"\1", s)
    s = re.sub(r"\|[^|]*\|", "CMPD", s)
    out, inlog = [], False
    for part in re.split(r"(_)", s):
        if part == "_":
            inlog = not inlog; continue
        for w in part.split():
            if w in (",", ":", ";", "/", ":.", "::") or w.startswith("$"):
                if w == "/":
                    out.append(("W", "/"))
                continue
            w = re.sub(r"\{\+?([^}]*)\}", lambda m: "-\x01" + m.group(1) + "-", w)
            for x in re.split(r"-", w):
                x = x.strip()
                if not x:
                    continue
                det = x.startswith("\x01"); x = x.lstrip("\x01")
                if re.fullmatch(r"[xX]+", x):
                    return None
                if NUM.match(x) or re.fullmatch(r"[\d/]+", x):
                    out.append(("N", x)); continue
                for y in re.split(r"[.+]", x):
                    if not y:
                        continue
                    if inlog:
                        out.append(("L", y)); continue
                    if y != y.lower():
                        out.append(("U", y)); continue
                    out.append(("D" if det else "R", y))
    return out


def a7():
    """A7: the two repo data files match the SHA-256 values in the prereg's Data section."""
    got = dict(ogsl=sha256_of(OGSL), skeletons=sha256_of(SKEL))
    return dict(got, passed=got["ogsl"] == OGSL_SHA and got["skeletons"] == SKEL_SHA)


def load_lexicon():
    """Primary lexicon: first column of the derived file. Returns (all skeletons as tuples, density check)."""
    sk = []
    with open(SKEL, encoding="utf-8") as f:
        next(f)
        for line in f:
            w = unicodedata.normalize("NFC", line.split("\t")[0])
            assert w and set(w) <= set(OA_ALPHA), "lexicon skeleton outside the 11 letters"
            sk.append(tuple(w))
    assert len(set(sk)) == len(sk)
    by = Counter(len(w) for w in sk)
    dens = {n: by[n] / len(OA_ALPHA) ** n for n in range(1, 8)}
    lmin = min(n for n in dens if dens[n] <= 0.25)
    return sk, dict(skeletons=len(sk), density={n: round(v, 4) for n, v in dens.items()}, rule_LMIN=lmin,
                    W=sum(by[n] for n in range(LMIN, MAXW + 1)), W_by_length=[by[n] for n in range(LMIN, MAXW + 1)])


def ceiling_words(content, v2s, key):
    """Word skeletons of one kept line for the ceiling lexicon: a word is one space-separated group of hyphen-joined
    readings; used only if every part is a syllabic reading with a sign-list entry and a key value."""
    # PREREG-AMBIGUITY (ceiling arm, record-only): the scratch split on `_` before spaces, which kept the syllabic
    # part of a group glued to a logogram. The prereg excludes "any word that holds a logogram", so a group that
    # touches a `_` span is dropped whole here. A group with `{`, `|`, `(`, an upper-case letter, a numeral, a `.`
    # or `+` joint, or an empty part is dropped.
    s = re.sub(r"\(\$.*?\$\)", " ", content); s = re.sub(r"[<>!?*]", "", s)
    out, inlog = [], False
    for w in s.split():
        n_us = w.count("_"); held = inlog or n_us > 0
        if n_us % 2:
            inlog = not inlog
        if held or "{" in w or "|" in w or "(" in w or w != w.lower() or w.startswith("$"):
            continue
        sk, good = [], True
        for y in w.split("-"):
            if not y or re.fullmatch(r"[xX\d/]+", y) or re.search(r"[.+,:;/]$|[.+]", y):
                good = False; break
            v = norm_reading(y); sg = v2s.get(v) if v else None
            if sg is None or cons_full(v) is None or sg not in key:
                good = False; break
            sk += key[sg]
        if good and LMIN <= len(sk) <= MAXW:
            out.append(tuple(sk))
    return out


def build_corpus(need_ceiling=False):
    """Label-free build of everything the study reads from text: pools T, L and set Q, the sign mapping, the true
    key, the chunks in the one tablet order. No lexicon is matched against text and nothing is scored.
    Returns (payload for the workers, stats for A2, list of A9 problems)."""
    load_sealed()
    sl = json.loads(zipfile.ZipFile(OGSL).read("ogsl/ogsl-sl.json"))
    v2s = {}
    # PREREG-AMBIGUITY: 1,108 sign-list values are listed under more than one sign name. The first sign in the file's
    # order is taken (as the scratch, which made the Measured tables). Bears on every cell through the sign tokens.
    for name, d in sl["signs"].items():
        for v in d.get("values", []):
            v2s.setdefault(v, name)
    csv.field_size_limit(10 ** 9)
    cat, both, other_obj = {}, set(), 0
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if not pid.isdigit():
                continue
            # PREREG-AMBIGUITY (bears on A2, so on whether K0 starts): period, genre and object type are compared
            # after stripping outer spaces; object type is lower-cased. The prereg names two object types, "tablet"
            # and "tablet & envelope"; the scratch took any type starting with "tablet". The prereg wins; rows the
            # scratch would have added are counted (other_obj) so an A2 stop can be traced to this.
            per = (r.get("period") or "").strip(); g = (r.get("genre") or "").strip()
            ot = (r.get("object_type") or "").strip().lower()
            if per not in (P_T, P_Q) or g not in GENRES or not ot.startswith("tablet"):
                continue
            if ot not in OBJ:
                other_obj += 1; continue
            pid = "P" + pid.zfill(6); tag = ("T" if per == P_T else "Q", g == "Letter")
            if pid in cat and cat[pid][0] != tag[0]:
                both.add(pid)
            cat[pid] = tag
    lines = {"T": [], "Q": []}; st = {"T": Counter(), "Q": Counter()}; kept_texts = {"T": set(), "Q": set()}
    pid = None; lang_ok = True
    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                pid = line[1:8]; lang_ok = True
                if pid in cat:
                    st[cat[pid][0]]["texts"] += 1     # texts with a transliteration (one per &P header, as scratch)
                continue
            if pid not in cat:
                continue
            if line.startswith("#atf: lang"):
                lang_ok = "akk" in line               # a text with no lang line at all is kept
                continue
            m = LINE.match(line)
            if not m or not lang_ok:
                continue
            t = tok(m.group(2)); p = cat[pid][0]
            if t is None:
                st[p]["lines_dropped"] += 1
            elif t:
                st[p]["lines"] += 1; kept_texts[p].add(pid)
                lines[p].append((pid, t, m.group(2) if (need_ceiling and p == "T") else None))

    def runs_of(pool, key=None):
        """Runs of >= 2 signs inside a line; with key=None also the per-sign reading counts (pool T, for the key)."""
        runs, sign_tok, sign_read, unk = [], Counter(), defaultdict(Counter), 0
        for pid, t, _ in lines[pool]:
            cur = []
            for k, y in t:
                if k == "W":
                    continue                          # word-divider wedge: removed, not a break
                sg = c = None
                if k in ("R", "D"):
                    v = norm_reading(y); sg = v2s.get(v) if v else None; c = cons_full(v) if v else None
                if sg is None or c is None or (key is not None and sg not in key):
                    if k in ("R", "D") and (sg is None or c is None):
                        unk += 1
                    if len(cur) >= 2:
                        runs.append((pid, cur))
                    cur = []; continue
                cur.append(sg); sign_tok[sg] += 1
                sign_read[sg][() if k == "D" else tuple(MERGE[x] for x in c)] += 1
            if len(cur) >= 2:
                runs.append((pid, cur))
        return runs, sign_tok, sign_read, unk

    runs, sign_tok, sign_read, unk = runs_of("T")
    # True key: the merged consonants of the reading each sign most often has in pool T; ties go to the shorter
    # value, then alphabetical order.
    # PREREG-AMBIGUITY: "alphabetical" = Python order of the letter tuples (Š sorts after the ten ASCII letters).
    key, modal = {}, 0
    for sg, cnt in sign_read.items():
        best = sorted(cnt.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0]
        key[sg] = best[0]; modal += best[1]
    ntok = sum(sign_tok.values())
    assert all(set(v) <= set(OA_ALPHA) for v in key.values())
    lens = B.m77_lengths()                            # M77: text lengths only
    ch = B.chunk(runs, lens, np.random.default_rng(BASE + 1))
    by = defaultdict(list)
    for tid, c in ch:
        by[tid].append(tuple(c))
    tids = sorted(by); random.Random(BASE).shuffle(tids)   # one tablet order; chunks follow their tablet
    seq = [(tid, c) for tid in tids for c in by[tid]]
    qruns, q_tok, _, q_unk = runs_of("Q")              # label-free count, as the scratch (Q's own mapped tokens)
    qruns_k, _, _, _ = runs_of("Q", key)               # study text: a Q sign with no value in the T key is a break
    qseq = [(tid, tuple(c)) for tid, c in B.chunk(qruns_k, lens, np.random.default_rng(BASE + 2))]
    t_ids = {p for p, tg in cat.items() if tg[0] == "T"}; q_ids = {p for p, tg in cat.items() if tg[0] == "Q"}
    letters = {p for p, tg in cat.items() if tg[0] == "T" and tg[1]}
    a9 = []
    if both:
        a9.append(f"{len(both)} catalogue ids carry both the exact and the uncertain period")
    if q_ids & ({tid for tid, _ in seq} | kept_texts["T"] | letters):
        a9.append("a set Q tablet is in pool T, pool L or the true key's source")
    if {tid for tid, _ in qseq} - q_ids:
        a9.append("a set Q chunk comes from a tablet outside set Q")
    ceil = None
    if need_ceiling:
        ceil = defaultdict(Counter)
        for pid, _, content in lines["T"]:
            for sk in ceiling_words(content, v2s, key):
                ceil[pid][sk] += 1
        ceil = dict(ceil)
        if set(ceil) & q_ids:
            a9.append("a set Q tablet is in the ceiling lexicon's source")
    sk_all, lexstat = load_lexicon()
    stats = dict(pool_T=dict(texts=st["T"]["texts"], lines=st["T"]["lines"], lines_dropped=st["T"]["lines_dropped"],
                             tokens=ntok, sign_types=len(sign_tok), unmapped_tokens=unk, key_purity=modal / ntok,
                             runs_ge2=len(runs), tablets=len(tids), chunks=len(seq),
                             other_object_type_rows=other_obj),
                 set_Q=dict(texts=st["Q"]["texts"], texts_kept=len(kept_texts["Q"]), lines=st["Q"]["lines"],
                            tokens=sum(q_tok.values()), unmapped_tokens=q_unk, chunks=len(qseq),
                            tablets_with_chunks=len({t for t, _ in qseq})),
                 pool_L=dict(tablets=len(letters & set(tids)), chunks=sum(tid in letters for tid, _ in seq)),
                 lexicon=lexstat, blocks={s: len(seq) // (UNIT * s) for s in SIZES + (REC32,)})
    W = sorted(w for w in sk_all if LMIN <= len(w) <= MAXW)
    return dict(seq=seq, key=key, W=W, qseq=qseq, letters=letters, ceil=ceil), stats, a9


def held(tid):
    """Hashed split (no seed): a tablet is held out if CRC32 of the ASCII string 'ho:' + its id is odd."""
    v = _HELD.get(tid)
    if v is None:
        v = _HELD[tid] = bool(zlib.crc32(("ho:" + tid).encode("ascii")) & 1)
    return v


def block(s, b, pool="T"):
    """Block b (0-based) of size s: the next s x 2,300 chunks of the one tablet order. Returns the order list
    [(tablet id, signs, is_dev)]. Pool L uses the same chunks and order, letters only."""
    seq = SEQ if pool == "T" else SEQ_L
    n = s * UNIT
    assert 0 <= b and (b + 1) * n <= len(seq), "block outside the pool"
    return [(tid, t, not held(tid)) for tid, t in seq[b * n:(b + 1) * n]]


def wrap(seqs):
    return [[list(s)] for s in seqs]                  # ladder text form: a chunk is one word


def unwrap(texts):
    return [tuple(s for w in t for s in w) for t in texts]


def halves(order):
    """(dev seqs, dev ids, ho seqs, ho ids), each in block order. 'dev followed by ho' is dev + ho."""
    dv = [(i, t) for i, t, d in order if d]; ho = [(i, t) for i, t, d in order if not d]
    return [t for _, t in dv], [i for i, _ in dv], [t for _, t in ho], [i for i, _ in ho]


# ------------------------------------------------------------------ clean positions, folds
def is_clean(t, others):
    """The sealed rule, as lift_score: no text in `others` is identical to t, one edit from it, or contains / is
    contained in it (_close). Used here only to check CleanIndex."""
    return not any(t == u or _close(list(t), list(u)) for u in others)


class CleanIndex:
    """The same clean rule answered from hash sets, for chunks of >= 4 signs."""
    # PREREG-AMBIGUITY (bears on K0b / K0c at 16 u): the clean rule is unchanged, but the sealed pairwise loop costs
    # about 1e8 _close calls per 16 u text. This index gives the same answer: t is not clean if a dev chunk u (i) is
    # t; (ii) has t's length (>= 4) and differs in one place; (iii) is longer and contains t; (iv) is one longer and
    # is t with one sign added; (v) is shorter (>= 3) and sits inside t; (vi) is one shorter (>= 4) and is t with one
    # sign removed. It is checked against is_clean on every 1 u real draw (A2) and on Linear B (A1) before any gain.
    def __init__(self, others):
        self.full, self.wild, self.sub, self.dele = set(), set(), set(), set()
        for u in {tuple(x) for x in others}:
            m = len(u); self.full.add(u)
            if m >= 4:
                for i in range(m):
                    self.wild.add(u[:i] + (None,) + u[i + 1:])
            if m >= 5:
                for i in range(m):
                    self.dele.add(u[:i] + u[i + 1:])
                for a in range(m):
                    for b in range(a + 4, m + 1):
                        if b - a < m:
                            self.sub.add(u[a:b])

    def clean(self, t):
        t = tuple(t); n = len(t)
        assert n >= 4
        if t in self.full or t in self.sub or t in self.dele:
            return False
        for i in range(n):
            if t[:i] + (None,) + t[i + 1:] in self.wild:
                return False
            if n >= 5 and t[:i] + t[i + 1:] in self.full:
                return False
        for a in range(n):
            for b in range(a + 3, n + 1):
                if b - a < n and t[a:b] in self.full:
                    return False
        return True


def fold_of(tid):
    """Development folds: CRC32 of the tablet id, mod 5 (lift_score: of the line id; the same function)."""
    return zlib.crc32(str(tid).encode()) % NFOLD


def fold_parts(dev, dev_ids):
    """[(training chunks = the other four folds, every chunk of fold f)] for f = 0..4, each in block order."""
    fo = [fold_of(i) for i in dev_ids]
    return [([t for t, g in zip(dev, fo) if g != f], [t for t, g in zip(dev, fo) if g == f]) for f in range(NFOLD)]


# ------------------------------------------------------------------ trigram (copied from lift_score, unchanged)
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
        # PREREG-AMBIGUITY: no tie rule is given for Hit@1 / Hit@5 / MRR (reported, not graded). As lift_score:
        # frequency in the trigram's training text (desc), then sign name. G has no ties.
        order = sorted(range(len(cands)), key=lambda q: (-self.uni.get(cands[q], 0), cands[q]))
        tb = np.empty(len(cands), np.int32)
        for r, q in enumerate(order):
            tb[q] = r
        return tb


class Positions:
    """Masked positions of a set of texts, with trigram scores B (P x C) and tie ranks TB (P x C)."""

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
    """One text (dev half and held-out half, each with tablet ids) prepared for scoring: held-out clean positions
    under a trigram on the dev half, and cross-fit positions over the five CRC32 folds of the dev half (clean against
    the four training folds). Key-free: one Cell serves every key scored on that text. As lift_score, plus the tablet
    id of every held-out clean position (for the clustered SE) and the clean rule through CleanIndex."""

    def __init__(self, dev, dev_ids, ho, ho_ids, cands, folds=True):
        self.cands = sorted(cands); self.cidx = {c: i for i, c in enumerate(self.cands)}
        self.dev = dev
        self.tg = Trigram(dev, self.cands)
        self.ci = CleanIndex(dev)
        ho4 = [(t, i) for t, i in zip(ho, ho_ids) if len(t) >= 4]
        self.clean = [(t, i) for t, i in ho4 if self.ci.clean(t)]
        self.counts = dict(tokens=sum(len(t) for t in dev) + sum(len(t) for t in ho),
                           ho_texts_ge4=len(ho4), ho_positions_ge4=sum(len(t) for t, _ in ho4),
                           clean_texts=len(self.clean), clean_positions=sum(len(t) for t, _ in self.clean),
                           thin=sum(len(t) for t, _ in self.clean) < F4_MIN)
        self.ho = Positions([t for t, _ in self.clean], self.tg, self.cands, self.cidx)
        self.ho_tab = np.array([str(i) for t, i in self.clean for _ in t])
        if not folds:
            return
        self.fold_train, self.fold_all, self.fold_pos = [], [], []
        for train, allf in fold_parts(dev, dev_ids):
            ci = CleanIndex(train)
            test = [t for t in allf if len(t) >= 4]
            test = [t for t in test if ci.clean(t)]
            self.fold_train.append(train); self.fold_all.append(allf)
            self.fold_pos.append(Positions(test, Trigram(train, self.cands), self.cands, self.cidx))
        self.dv = Positions.concat(self.fold_pos, len(self.cands))
        self.counts["dev_crossfit_positions"] = len(self.dv)


def make_cell(order, cands, folds=True):
    dev, dev_ids, ho, ho_ids = halves(order)
    return Cell(dev, dev_ids, ho, ho_ids, cands, folds)


# ------------------------------------------------------------------ word model (copied from lift_score, unchanged)
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
        """f[i] = P(x[1..i], a unit ends at i); returns (f, P(x)). The sealed forward pass, term for term."""
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
    # PREREG-AMBIGUITY: "15 EM rounds" = fifteen E-step + M-step rounds; the scoring model carries the parameters of
    # the fifteenth M-step (as lift_score). Chunks with no consonant add nothing to the fit.
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
    """q: consonant frequencies of the training text read with the key, add-one over the key letters."""
    c = Counter(x for t in texts for x in cons(t, key))
    tot = sum(c.values()) + len(ALPHA)
    return {a: (c[a] + 1) / tot for a in ALPHA}


def fit_model(lex, texts, key):
    return em(lex, Counter(cons(t, key) for t in texts), qdist(texts, key))


def dose_from(models, fold_all, key):
    """D: sum of LLR(x) over every chunk of each fold under the model fitted on the other four folds, divided by the
    number of consonants. Nats per consonant. Returns (D, consonants)."""
    # PREREG-AMBIGUITY: "every chunk of each fold" = all development chunks, of any length and clean or not (as
    # lift_score); chunks with no consonant add 0 to both sums. Bears on K1 only.
    num, den = 0.0, 0
    for m, chunks in zip(models, fold_all):
        for t in chunks:
            x = cons(t, key); num += m.llr(x); den += len(x)
    return (num / den if den else 0.0), den


def dose(dev, dev_ids, key, lex):
    parts = fold_parts(dev, dev_ids)
    return dose_from([fit_model(lex, tr, key) for tr, _ in parts], [a for _, a in parts], key)


def perm_letters(j):
    # PREREG-AMBIGUITY (bears on bar C in K0b): "a permutation of the 11 letters with no letter fixed", seed base +
    # 800,000 + j: the sorted letters (Š last) are shuffled with random.Random(seed).shuffle, repeated on the same
    # stream until no letter maps to itself; letter i of the sorted alphabet becomes letter i of the shuffled list.
    rng = random.Random(BASE + 800000 + j)
    while True:
        p = list(OA_ALPHA); rng.shuffle(p)
        if all(a != b for a, b in zip(OA_ALPHA, p)):
            return dict(zip(OA_ALPHA, p))


def permuted(words, j):
    m = perm_letters(j); out = {tuple(m[c] for c in w) for w in words}
    assert len(out) == len(set(words))
    return out


def get_lex(j):
    """0: the primary word list W. j = 1..5: W with letter permutation j applied to every word."""
    if j not in LEXS:
        LEXS[j] = Lex(W47 if j == 0 else permuted(W47, j))
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


def se_clustered(x, tab):
    """Prereg: SE_cl = sqrt( C / (C - 1) x sum over tablets of (sum over i in c of (x_i - mean))^2 ) / n.
    Returns (SE or None when fewer than two tablets, C)."""
    n = len(x)
    if not n:
        return None, 0
    _, inv = np.unique(tab, return_inverse=True); C = int(inv.max()) + 1
    if C < 2:
        return None, C
    s = np.bincount(inv, weights=x - x.mean(), minlength=C)
    return float(math.sqrt(C / (C - 1) * float((s ** 2).sum())) / n), C


def bounds(mean, se):
    """One-sided 95% bounds (mean - 1.645 SE_cl, mean + 1.645 SE_cl); None when the SE does not exist."""
    return (None, None) if se is None else (mean - Z1 * se, mean + Z1 * se)


def evaluate(cell, key, lex, grid, extra=None):
    """One key on one text, by the frozen rules: λ* on the cross-fitted development half only, then G and the
    reported figures on the held-out clean positions. Returns (aggregates, per-position log p_S of the true sign);
    the array stays in memory (bar C) and is never written. `extra` = (Positions, {name: mask}) for the fixed sets."""
    for s in cell.cands:
        assert s in key, "key does not cover every candidate sign"
    C = len(cell.cands)
    fms = [fit_model(lex, tr, key) for tr in cell.fold_train]
    D, ncons = dose_from(fms, cell.fold_all, key)
    parts = [llr_matrix(p, cell.cands, key, m) for p, m in zip(cell.fold_pos, fms)]
    cov_dv = np.concatenate(parts) if parts else np.zeros((0, C))
    nd = len(cell.dv)
    # PREREG-AMBIGUITY (bears on K0): "pooled mean" = the mean over all cross-fit positions of the five folds together;
    # the 0.01 margin is inclusive; grid ties go to the smaller λ. As lift_score.
    dl = {lam: (float(logp(cell.dv, cov_dv, lam).mean()) if nd else 0.0) for lam in grid}
    lam = max(grid, key=lambda g: (dl[g], -g))
    if lam != 0 and not (dl[lam] - dl[0.0] >= LAM_MARGIN):
        lam = 0.0
    mf = fit_model(lex, cell.dev, key)                # held-out scoring: fitted on the whole development half
    pos = cell.ho; n = len(pos)
    r0 = ranks(pos, None, 0.0); lp0 = logp(pos, None, 0.0)
    if lam == 0:
        g = np.zeros(n); rS = r0; lpS = lp0           # λ* = 0: G is exactly 0
    else:
        cov = llr_matrix(pos, cell.cands, key, mf)
        lpS = logp(pos, cov, lam); g = lpS - lp0; rS = ranks(pos, cov, lam)
    c4 = np.array([sum(len(key[s]) for s in t) >= LMIN for t, _ in pos.items], bool)
    n4 = int(c4.sum()); h0, hS = int((r0 == 1).sum()), int((rS == 1).sum())
    G = float(g.mean()) if n else 0.0
    se, ntab = se_clustered(g, cell.ho_tab)
    lo, hi = bounds(G, se)
    # PREREG-AMBIGUITY: Hit@1, Hit@5 and MRR are read under the one combined score S at the λ* that G uses; the
    # per-position SE is the population form (std / sqrt(n)). As lift_score. Reported only.
    e = dict(lam=lam, n=n, G=G, se=float(g.std() / math.sqrt(n)) if n else 0.0, se_cl=se, n_tablets=ntab,
             G_lo=lo, G_hi=hi, n_c4=n4, G_c4=float(g[c4].mean()) if n4 else 0.0,
             hits_B=h0, hits_S=hS, hit1_B=100 * h0 / n if n else 0.0, hit1_S=100 * hS / n if n else 0.0,
             hit1_lift=100 * (hS - h0) / n if n else 0.0,
             hit5_B=float(100 * np.mean(r0 <= 5)) if n else 0.0, hit5_S=float(100 * np.mean(rS <= 5)) if n else 0.0,
             mrr_B=float(np.mean(1 / r0)) if n else 0.0, mrr_S=float(np.mean(1 / rS)) if n else 0.0,
             rho=float(mf.rho), D=D, n_cons_dev=ncons, n_dev=nd, dev_gain_by_lam=[round(dl[x] - dl[0.0], 5) for x in grid])
    if extra is not None:
        xp, masks = extra
        if lam == 0 or not len(xp):
            gx = np.zeros(len(xp))
        else:
            gx = logp(xp, llr_matrix(xp, cell.cands, key, mf), lam) - logp(xp, None, 0.0)
        e["fixed"] = {nm: dict(n=int(m.sum()), G=float(gx[m].mean()) if m.any() else None) for nm, m in masks.items()}
    return e, lpS


# ------------------------------------------------------------------ texts: plants, filler, scramble
def vocab_size(s, vm):
    return min(vm * s, len(W47))


def plant_parts(real, s, k, vm, off=0):
    """Plant k at size s on a real block: text made only of lexicon words (generator as lift_score), cut to the
    block's chunk lengths in block order and split as the block is (a planted chunk takes the tablet id of the real
    chunk whose place it fills); the Markov filler of the real block; the fixed dilution uniforms.
    Returns (plant in dev-followed-by-ho order, filler, uniforms, info)."""
    freq = Counter(x for _, t, _ in real for x in t)
    signs = sorted(freq)
    single = defaultdict(list); zero = []
    for x in signs:
        v = KEY[x]
        if len(v) == 1:
            single[v[0]].append(x)
        elif not v:
            zero.append(x)
    # PREREG-AMBIGUITY (bears on K0): "W is put in one seeded random order" = the sorted W shuffled once with
    # random.Random(base + 100,000 + k); rank = place in that order. The plant uses the first min(500 s, |W|) words.
    # A word with a consonant that no one-consonant sign of the block writes is left out and the others keep their
    # ranks (so the vocabularies stay nested); the count left out is recorded.
    words = list(W47); random.Random(BASE + 100000 + k).shuffle(words)
    nvoc = vocab_size(s, vm)
    sub = [(w, r + 1) for r, w in enumerate(words[:nvoc]) if all(single.get(c) for c in w)]
    assert sub, "no plant word can be spelled in this block"
    w_cum = list(np.cumsum([1 / r for _, r in sub])); sub_w = [w for w, _ in sub]
    z = sum(freq[x] for x in zero) / sum(freq.values())
    p0 = z / (1 - z)                                  # share p/(1+p) of zero-consonant signs equals the block's
    assert p0 <= 1, "zero-consonant share above 1/2: plant cannot match it"
    cum1 = {c: list(np.cumsum([freq[x] for x in ss])) for c, ss in single.items()}
    # PREREG-AMBIGUITY (bears on K0): the zero-consonant sign that follows is drawn by its frequency in the block;
    # word draws, sign draws and follow-on draws all use the spelling rng, in this order. As lift_score.
    cum0 = list(np.cumsum([freq[x] for x in zero]))
    rs = random.Random(BASE + 200000 + 1000 * s + k + off)
    need = sum(len(t) for _, t, _ in real); stream = []
    while len(stream) < need:
        word = rs.choices(sub_w, cum_weights=w_cum)[0]
        for c in word:
            stream.append(rs.choices(single[c], cum_weights=cum1[c])[0])
            if zero and rs.random() < p0:
                stream.append(rs.choices(zero, cum_weights=cum0)[0])
    po, i = [], 0
    for tid, t, d in real:
        po.append((tid, tuple(stream[i:i + len(t)]), d)); i += len(t)
    dh = [x for x in po if x[2]] + [x for x in po if not x[2]]
    dev, _, ho, _ = halves(real)
    filler = unwrap(L.markov(wrap(dev + ho), random.Random(BASE + 300000 + 1000 * s + k + off)))
    ur = random.Random(BASE + 400000 + 1000 * s + k + off); us = [ur.random() for _ in dh]
    info = dict(vocabulary=nvoc, unspellable_left_out=nvoc - len(sub), zero_share=z, p_zero_follow=p0)
    return dh, filler, us, info


def dilute(plant_dh, filler, us, w):
    """Each chunk is replaced, when its fixed uniform u >= w, by the filler chunk at the same index."""
    return [(tid, fill if u >= w else t, d) for (tid, t, d), fill, u in zip(plant_dh, filler, us)]


def scramble(order, s, d):
    """Unigram scramble (sealed ladder `unigram`, seed base + 500,000 + 1,000 s + draw) of dev followed by ho; the
    trigram, the word model and the key are all on the scramble; tablet ids are kept by index."""
    # PREREG-AMBIGUITY (bears on K0): one call on the whole text, one token pool; the same seed serves plant k and
    # real draw k of a size. As lift_score.
    dev, dev_ids, ho, ho_ids = halves(order)
    sc = unwrap(L.unigram(wrap(dev + ho), random.Random(BASE + 500000 + 1000 * s + d)))
    return ([(i, t, True) for i, t in zip(dev_ids, sc[:len(dev)])]
            + [(i, t, False) for i, t in zip(ho_ids, sc[len(dev):])])


def make_text(tx):
    """Text spec -> (order, candidates, real block, info). kind: real | plant. Keys of tx: s, b, d (draw number used
    in seeds: block + 1 for real text, k for plants), pool, q (add all of set Q), w / vm / f5 (plants), scr."""
    s, b = tx["s"], tx["b"]
    real = block(s, b, tx.get("pool", "T")); info = {}
    # PREREG-AMBIGUITY (bears on K0): on plants the candidates are every sign type of the real block the plant is
    # built on (the plant uses a subset of them), as lift_score.
    cands = {x for _, t, _ in real for x in t}
    if tx["kind"] == "real":
        order = real
        if tx.get("q"):
            order = real + [(tid, t, not held(tid)) for tid, t in QSEQ]
            cands |= {x for _, t in QSEQ for x in t}
    else:
        dh, filler, us, info = plant_parts(real, s, tx["d"], tx["vm"], F5_OFF if tx.get("f5") else 0)
        w = tx["w"]
        order = dh if w >= 1 else dilute(dh, filler, us, w)
        info.update(w=w, replaced=sum(u >= w for u in us), n_chunks=len(us))
    if tx.get("scr"):
        order = scramble(order, s, tx["d"])
    return order, sorted(cands), real, info


def n1_key(real, s, d, j):
    """Shuffled key j (1..5) of draw d: the sealed lb_shape_ladder shuffle (values permuted within frequency bins of
    10 inside each consonant-count class), seed base + 600,000 + 1,000 s + 10 d + j."""
    # PREREG-AMBIGUITY (bears on K0): the bins use the sign frequencies of the real block (for a plant: the block it
    # is built on), and one rng per key. lift_score took its N1 keys from the real draw in the same way.
    freq = Counter(x for _, t, _ in real for x in t); kept = sorted(freq)
    true = {x: KEY[x] for x in kept}
    k = L.permute_in_class_bins(true, L.classes(kept, true), freq, random.Random(BASE + 600000 + 1000 * s + 10 * d + j))
    out = dict(KEY); out.update(k)
    return out


def ceiling_lex(s, b):
    """Ceiling word list for block (s, b): Old Assyrian word skeletons from pool T tablets outside the block, ranked
    by distinct source tablets, then tokens, then alphabetically, size-matched to the primary list at each length."""
    inside = {tid for tid, _ in SEQ[b * s * UNIT:(b + 1) * s * UNIT]}
    tabs, toks, src = Counter(), Counter(), set()
    for pid, c in CEIL.items():
        if pid in inside:
            continue
        src.add(pid)
        for sk, n in c.items():
            tabs[sk] += 1; toks[sk] += n
    if src & inside:
        raise RuntimeError("A8: a ceiling lexicon would include a word from a tablet of its own block")
    words, short = [], {}
    for n in range(LMIN, MAXW + 1):
        r = sorted((sk for sk in tabs if len(sk) == n), key=lambda sk: (-tabs[sk], -toks[sk], sk))
        words += r[:W_BY_LEN[n]]; short[n] = max(0, W_BY_LEN[n] - len(r))
    return words, dict(words=len(words), shortfall_by_length=short, source_tablets=len(src))


# ------------------------------------------------------------------ Linear B (abort A1 only; copied from lift_score)
def ls_draw(k):
    """lift_score draw k = sealed build(k, "chunk"), replayed to keep each chunk's source line id."""
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


def ls_plant(order, k, nsub, words):
    """lift_score's planted generator with its own seeds, unchanged."""
    freq = Counter(s for _, t, _ in order for s in t)
    signs = sorted(freq)
    single = defaultdict(list); zero = []
    for s in signs:
        v = B.true_value(s)
        if len(v) == 1:
            single[v[0]].append(s)
        elif not v:
            zero.append(s)
    pool = [t for t in words if all(single.get(c) for c in t)]
    sub = random.Random(BASE_LS + k).sample(pool, nsub)
    w_cum = list(np.cumsum([1 / (r + 1) for r in range(nsub)]))
    z = sum(freq[s] for s in zero) / sum(freq.values())
    p0 = z / (1 - z)
    cum1 = {c: list(np.cumsum([freq[s] for s in ss])) for c, ss in single.items()}
    cum0 = list(np.cumsum([freq[s] for s in zero]))
    rs = random.Random(BASE_LS + 50000 + k)
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
    return out


# ------------------------------------------------------------------ workers
def setup(payload):
    global W47, KEY, SEQ, SEQ_L, QSEQ, CEIL
    W47, KEY, SEQ, QSEQ, CEIL = payload["W"], payload["key"], payload["seq"], payload["qseq"], payload["ceil"]
    SEQ_L = [(tid, t) for tid, t in SEQ if tid in payload["letters"]]


def init(payload):
    global INIT_ERR
    try:
        a5_hook(); load_sealed(); setup(payload)
    except BaseException as e:                        # a raising initializer would respawn workers for ever
        INIT_ERR = repr(e)


def _ready():
    if INIT_ERR is not None:
        raise RuntimeError("worker init failed: " + INIT_ERR)


def job_a1(_):
    """A1: this file's scoring code, pointed at Linear B and Homer, on the sealed lift_score K0 draw-1 plant."""
    # PREREG-AMBIGUITY (A1 precedes K0): "the sealed lift_score K0 draw-1 gain" = G of the true key on the K0 draw-1
    # plant in experiments/lift_score/kill.json, rebuilt with lift_score's seeds, vocabulary count and K0 grid.
    global ALPHA
    _ready()
    ref = json.load(open(LS_KILL)); row = [r for r in ref["K0"]["draws"] if r["k"] == 1][0]["true"]
    ALPHA = LB_ALPHA
    try:
        words = sorted(t for t in B.build_lexicon()[0] if LMIN <= len(t) <= MAXW)
        order = ls_draw(1); cands = sorted({s for _, t, _ in order for s in t})
        true = {s: B.true_value(s) for s in cands}
        po = ls_plant(order, 1, int(ref["sublex"]), words)
        cell = make_cell(po, cands)
        dev, _, ho, _ = halves(po)
        slow = sum(len(t) for t in ho if len(t) >= 4 and is_clean(t, dev))
        e, _ = evaluate(cell, true, Lex(words), tuple(float(x) for x in ref["K0"]["grid"]))
    finally:
        ALPHA = OA_ALPHA
    return dict(G=e["G"], sealed_G=row["G"], diff=abs(e["G"] - row["G"]), n=e["n"], sealed_n=row["n"],
                lam=e["lam"], sealed_lam=row["lam"], clean_index_agrees=slow == e["n"])


def job_gate(a):
    """Label-free shape counts of one real draw (A2, F4): no trigram, no lexicon, no key score. On 1 u draws the
    CleanIndex answer is checked against the sealed pairwise rule, on the held-out half and on fold 0."""
    _ready()
    s, b, pool = a
    order = block(s, b, pool); dev, dev_ids, ho, _ = halves(order)
    ci = CleanIndex(dev); ho4 = [t for t in ho if len(t) >= 4]; clean = [t for t in ho4 if ci.clean(t)]
    out = dict(s=s, b=b, tokens=sum(len(t) for _, t, _ in order), tablets=len({i for i, _, _ in order}),
               positions_ge4=sum(len(t) for t in ho4), clean_positions=sum(len(t) for t in clean),
               sign_types=len({x for _, t, _ in order for x in t}))
    out["thin"] = out["clean_positions"] < F4_MIN
    if s == 1:
        ok = [t for t in ho4 if is_clean(t, dev)] == clean
        train, allf = fold_parts(dev, dev_ids)[0]; cf = CleanIndex(train)
        t4 = [t for t in allf if len(t) >= 4]
        ok = ok and [t for t in t4 if is_clean(t, train)] == [t for t in t4 if cf.clean(t)]
        out["clean_index_agrees"] = ok
    return out


def job_trigram(a):
    """F3: trigram-only Hit@1 on a full-dose K0a plant's held-out clean positions. No key, no lexicon, no gain."""
    _ready()
    order, cands, _, info = make_text(a)
    c = make_cell(order, cands, folds=False)
    r = ranks(c.ho, None, 0.0)
    return dict(k=a["d"], trigram_hit1=float(100 * np.mean(r == 1)) if len(r) else 0.0, n=len(r), plant=info)


def job_a6(a):
    """A6: the fitted K0a draw-1 model sums to 1 over all strings of each length 1 to 4 on 11 letters. No gain."""
    # PREREG-AMBIGUITY (A6 precedes K0): "the fitted K0a draw-1 model" = the word model (primary W) fitted on the
    # whole development half of the full-dose K0a plant 1 under the true key; "sums to 1" = for each length n = 1..4
    # the 11^n window probabilities sum to 1 within 1e-9 (a window model is normalised per length). As lift_score.
    _ready()
    order, _, _, _ = make_text(a)
    dev, _, _, _ = halves(order)
    m = fit_model(get_lex(0), dev, KEY)
    sums = [math.fsum(m.fwd(x)[1] for x in product(ALPHA, repeat=n)) for n in (1, 2, 3, 4)]
    return dict(sums=sums, max_dev=max(abs(v - 1) for v in sums), p_sum=float(m.p.sum()), q_sum=math.fsum(m.q.values()))


def fixed_sets(cell, c, top):
    """Record-only fixed position sets of chain c under this cell's trigram: F1 (clean held-out positions of the
    chain's 1 u block) and Ftop (those also clean against the development half of the chain's top block)."""
    dev1, _, ho1, _ = halves(block(1, 16 * c)); ci1 = CleanIndex(dev1)
    f1 = [t for t in ho1 if len(t) >= 4 and ci1.clean(t)]
    citop = CleanIndex(halves(block(top, c * 16 // top))[0])
    pos = Positions(f1, cell.tg, cell.cands, cell.cidx)
    mtop = np.array([citop.clean(t) for t in f1 for _ in t], bool)
    still = np.array([cell.ci.clean(t) for t in f1 for _ in t], bool)
    return pos, dict(F1=np.ones(len(pos), bool), Ftop=mtop, F1_still_clean_here=still)


def job_cells(a):
    """Score a list of keys on one text. key kinds: true (true key, lexicon 0) | perm (true key, letter-permuted
    lexicon j = 1..5; with a true cell in the same job also the paired difference Δ_j and its clustered bound) |
    n1 (shuffled key j = 1..5). lex: primary | ceiling. Returns aggregates and the job's wall time."""
    _ready()
    t0 = time.time(); tx = a["text"]; grid = tuple(a["grid"])
    order, cands, real, info = make_text(tx)
    cell = make_cell(order, cands)
    out = dict(gid=a["gid"], part=a["part"], counts=cell.counts, cells=[], barC=[])
    if info:
        out["plant"] = info
    if a.get("lex") == "ceiling":
        words, cinfo = ceiling_lex(tx["s"], tx["b"]); out["ceiling"] = cinfo
        memo = {}

        def lexf(j):
            if j not in memo:
                memo[j] = Lex(words if j == 0 else permuted(words, j))
            return memo[j]
    else:
        lexf = get_lex
    extra = fixed_sets(cell, a["fixed"][0], a["fixed"][1]) if a.get("fixed") is not None else None
    lp_true = None
    for kind, j in a["keys"]:
        if kind == "true":
            e, lp_true = evaluate(cell, KEY, lexf(0), grid, extra)
        elif kind == "perm":
            e, lp = evaluate(cell, KEY, lexf(j), grid)
            if lp_true is not None:
                d = lp_true - lp; dm = float(d.mean()) if len(d) else 0.0
                se, _ = se_clustered(d, cell.ho_tab)
                out["barC"].append(dict(j=j, delta=dm, se_cl=se, L=bounds(dm, se)[0]))
        else:
            e, _ = evaluate(cell, n1_key(real, tx["s"], tx["d"], j), lexf(0), grid)
        e.update(kind=kind, j=j); out["cells"].append(e)
    out["sec"] = time.time() - t0
    return out


def job_target(a):
    """K1 dose target: D of the true key on the real development half of a block. No held-out text, no masking.
    It sets a dose and grades nothing."""
    _ready()
    s, b = a
    dev, dev_ids, _, _ = halves(block(s, b))
    d, nc = dose(dev, dev_ids, KEY, get_lex(0))
    return dict(s=s, b=b, D=d, n_cons_dev=nc, n_chunks_dev=len(dev))


def job_k1(a):
    """phase 'build': plant, filler, uniforms, D at w = 1 and w = 0 (F2), then the D-only bisection. Sees no gain.
    phase 'gain': rebuild the same diluted plant at the w found (D is re-checked) and score the true key."""
    _ready()
    phase, s, k, b, target = a["phase"], a["s"], a["k"], a["b"], a["target"]
    real = block(s, b); cands = sorted({x for _, t, _ in real for x in t}); lex = get_lex(0)
    dh, filler, us, info = plant_parts(real, s, k, a["vm"])

    def d_at(w):
        dd, di, _, _ = halves(dilute(dh, filler, us, w))
        return dose(dd, di, KEY, lex)[0]

    if phase == "gain":
        w = a["w"]; c = make_cell(dilute(dh, filler, us, w), cands)
        e, _ = evaluate(c, KEY, lex, tuple(a["grid"]))
        assert abs(e["D"] - a["D"]) <= 1e-12, "K1 rebuild differs from the bisection run"
        return dict(s=s, k=k, w=w, replaced=sum(u >= w for u in us), n_chunks=len(us), counts=c.counts, true=e)

    d1 = d_at(1.0); d0 = d_at(0.0)                    # evaluated first, for F2
    out = dict(s=s, k=k, b=b, plant=info, target=target, D_w1=d1, D_w0=d0, steps=[], n_chunks=len(us))
    # PREREG-AMBIGUITY (K1 only, as lift_score): (i) F2 is tested in the order written: zero dose first, then "above
    # the plant's D at w = 1". (ii) An end point already within 0.005 of the target counts as landed (w = 1 before
    # w = 0) and is not one of the 12 steps. (iii) The 12 steps are midpoints of [lo, hi] from [0, 1]; D is taken to
    # rise with w. (iv) "within 0.005" is inclusive.
    if target < d0 - D_TOL:
        out.update(status="no dose above filler", built=True, scored=False, w=None, D=None)
    elif target > d1 + D_TOL:
        out.update(status="target above the full plant; w = 1 used", built=True, scored=True, w=1.0, D=d1)
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
    """N3 objective: summed LLR of the development chunks under a fixed word model, with the interface of the sealed
    ladder IC (full / after / cache), so the sealed `fit` loop runs on it unchanged. Copied from lift_score."""

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


def job_k4(a):
    """K4 keys of one real draw. which = n2: 9 keys hill-climbed for IC (sealed ladder `fit`, 3,000 swaps, 3 restarts)
    on the real development half, its unigram scramble and its Markov chain. which = n3: 3 keys hill-climbed for the
    fixed-weight fragment likelihood. Each key then gets its own word model and λ* by the frozen rules."""
    _ready()
    s, b, d, grid = a["s"], a["b"], a["b"] + 1, tuple(a["grid"])
    real = block(s, b); cands = sorted({x for _, t, _ in real for x in t})
    freq = Counter(x for _, t, _ in real for x in t); kept = sorted(freq)
    true = {x: KEY[x] for x in kept}; cl_of = {x: len(true[x]) for x in kept}
    dev, _, _, _ = halves(real); cell = make_cell(real, cands); lex = get_lex(0); res = []

    def full_key(fk):
        k = dict(KEY); k.update(fk)
        return k

    if a["which"] == "n2":
        # PREREG-AMBIGUITY (K4 only): lift_score replayed the sealed Linear B N2 keys; none exist for Old Assyrian
        # and the prereg lists no N2 seed. They are fitted here as the sealed ladder fitted them (real, unigram and
        # Markov development text; 3 restarts; 3,000 swaps inside consonant-count classes; IC against W), with one
        # rng per draw at base + 900,000 + 1,000 s + draw, a range no other seed uses.
        rng = random.Random(BASE + 900000 + 1000 * s + d); lexset = set(W47); wd = wrap(dev)
        for name, corp in (("real", wd), ("unigram", L.unigram(wd, rng)), ("markov", L.markov(wd, rng))):
            S = L.IC(corp, lexset)
            for r in range(N2_RESTARTS):
                fk = L.fit(S, L.shuffle_in_class(true, kept, cl_of, rng), kept, cl_of, N2_ITERS, rng)
                res.append(dict(src=name, restart=r, **evaluate(cell, full_key(fk), lex, grid)[0]))
    else:
        # PREREG-AMBIGUITY (K4 only, as lift_score): the objective sums over every development chunk; uniform q =
        # 1/11 per letter; restarts 0, 1, 2 (seed base + 700,000 + 1,000 s + 10 draw + restart), one rng per restart
        # for the start key and then the swaps.
        nW = len(lex.words)
        proxy = Model(lex, np.full(nW, 1.0 / nW), N3_RHO, {x: 1.0 / len(ALPHA) for x in ALPHA})
        for r in range(N3_RESTARTS):
            rng = random.Random(BASE + 700000 + 1000 * s + 10 * d + r)
            S = LLRSum(dev, proxy)
            k0 = L.shuffle_in_class(true, kept, cl_of, rng)
            start = S.full(k0)
            fk = L.fit(S, k0, kept, cl_of, N3_SWAPS, rng)
            res.append(dict(src="n3", restart=r, fit_start=start, fit_end=S.full(fk),
                            **evaluate(cell, full_key(fk), lex, grid)[0]))
    return dict(b=b, which=a["which"], counts=cell.counts, keys=res)


POOL = None
PAYLOAD = None


def run_jobs(fn, jobs):
    """Jobs go to at most NWORK (<= 4) worker processes; the pool is opened only after the A4 guard has passed."""
    global POOL
    if POOL is None:
        POOL = Pool(NWORK, initializer=init, initargs=(PAYLOAD,))
    return POOL.map(fn, jobs, chunksize=1)


# ------------------------------------------------------------------ jobs, rows, grading
def trio(gid, tx, grid, parts="ABC", lex="primary", fixed=None):
    """Jobs for one text. A: true key + the 5 letter-permuted lexicons (bar C, permuted-lexicon D). T: true key only.
    B: the 5 shuffled keys. C: the true key on the text's unigram scramble."""
    jobs = []
    for p in parts:
        if p == "A":
            keys = [("true", 0)] + [("perm", j) for j in range(1, NPERMLEX + 1)]
        elif p == "T":
            keys = [("true", 0)]
        elif p == "B":
            keys = [("n1", j) for j in range(1, N1_KEYS + 1)]
        else:
            keys = [("true", 0)]
        jobs.append(dict(gid=gid, part=p, text=dict(tx, scr=True) if p == "C" else tx, keys=keys, grid=grid, lex=lex,
                         fixed=fixed if p in "AT" else None))
    return jobs


def real_tx(s, b, pool="T", q=False):
    return dict(kind="real", s=s, b=b, d=b + 1, pool=pool, q=q)


def plant_tx(s, k, w, vm, nblocks, f5=False):
    # PREREG-AMBIGUITY (bears on K0): "Every K0 plant k is built on block (k - 1) mod the number of blocks of its
    # size" (K0a) against "block k mod the number of blocks" (K0b). Blocks are numbered from 0 here and the first
    # wording is used for every plant, so plant 1 sits on the first block. "draw" in the seeds is k.
    return dict(kind="plant", s=s, b=(k - 1) % nblocks, d=k, w=w, vm=vm, f5=f5)


def gather(res):
    """Job results -> {gid: row}. A row holds the aggregates of every key scored on that text."""
    by = {}
    for r in res:
        row = by.setdefault(r["gid"], dict(counts={}, sec=0.0))
        row["sec"] += r["sec"]
        for k in ("plant", "ceiling"):
            if k in r:
                row[k] = r[k]
        if r["part"] == "C":
            row["counts"]["scramble"] = r["counts"]; row["scramble_true"] = r["cells"][0]
        else:
            row["counts"]["text"] = r["counts"]
            if r["part"] == "B":
                row["n1"] = r["cells"]
            else:
                row["true"] = r["cells"][0]
                if r["part"] == "A":
                    row["perm"] = r["cells"][1:]; row["barC"] = r["barC"]
    return by


def le(x, bar):
    return x is not None and x <= bar


def ge(x, bar):
    return x is not None and x >= bar


def grade(row, bound=False):
    """Bars on one row. bound=True (real text at 16 u only): one-sided clustered bounds; else the sealed point rules.
    The shuffled-key bar is the median of exactly the 5 keys of this draw (the third largest G)."""
    if "true" in row:
        t = row["true"]; row["ok_gain"] = ge(t["G_lo"], GAIN_BAR) if bound else t["G"] >= GAIN_BAR
    if "scramble_true" in row:
        c = row["scramble_true"]; row["ok_scramble"] = le(c["G_hi"], CTRL_BAR) if bound else c["G"] <= CTRL_BAR
    if "n1" in row:
        assert len(row["n1"]) == N1_KEYS
        m = sorted(row["n1"], key=lambda e: (e["G"], e["j"]))[N1_KEYS // 2]
        row.update(n1_median_G=m["G"], n1_median_G_hi=m["G_hi"], n1_max_G=max(e["G"] for e in row["n1"]),
                   n1_median_hit1_lift=statistics.median(e["hit1_lift"] for e in row["n1"]))
        row["ok_n1"] = le(m["G_hi"], CTRL_BAR) if bound else m["G"] <= CTRL_BAR
    if "barC" in row:
        assert len(row["barC"]) == NPERMLEX
        row["perm_max_G"] = max(e["G"] for e in row["perm"])
        row["ok_C"] = all(ge(c["L"], 0.0) for c in row["barC"]) if bound else all(c["delta"] > 0 for c in row["barC"])
    return row


def count(rows, k):
    return sum(bool(r.get(k)) for r in rows)


def brief(rows, key="true"):
    """Short stdout line: G and Hit@1 lift of one key over the rows."""
    return dict(G=r4(r[key]["G"] for r in rows if key in r), hit1_lift=[round(r[key]["hit1_lift"], 2) for r in rows if key in r],
                lam=[r[key]["lam"] for r in rows if key in r])


def project_hours(t16, f5):
    """F6: processor-hours of the whole study from the measured seconds per key cell at 16 u."""
    # PREREG-AMBIGUITY (F6 sits inside K0): the prereg gives no formula. The prereg's own per-cell estimates (20 / 60
    # / 110 / 220 / 330 s at 1 / 4 / 8 / 16 / 32 u; 35 s interpolated for 2 u) are scaled by measured / 220 and
    # multiplied by the key-cell counts of the "Cells" table. A K1 plant counts as 3.8 cells (one gain cell and up
    # to 14 dose fits at a fifth of a cell), which reproduces the prereg's 5 processor-hours for K1; K4 is counted at
    # 1 u. With measured = 220 s this gives 33 hours, the prereg's total. "Seconds per key cell" = the summed wall
    # time of the three jobs of 16 u plant 1 (cell builds included) over its 12 key cells.
    f = t16 / EST[16]
    core = {1: 1 + 60 + 20 + (20 if f5 else 0) + 20 * K1_EQ + 240 + 120 + 20 + 1 + 240, 2: 20 * K1_EQ + 240,
            4: 120 + 10 * K1_EQ + 156 + 78, 8: 10 * K1_EQ + 72, 16: 120 + 5 + 10 * K1_EQ + 36 + 18 + 3}
    opt = {1: 14 * 7, 2: 7 * 7, 4: 3 * 7, 32: 12}     # pool L and the 32 u record-only cell
    hc = f * sum(n * EST[s] for s, n in core.items()) / 3600; ho = f * sum(n * EST[s] for s, n in opt.items()) / 3600
    return hc + ho, hc


def start(mode, path, kill_run=None):
    seal = seal_check(); why, fm = a4()
    if kill_run is not None and (seal["code_sha256"] != kill_run.get("code_sha256")
                                 or seal["prereg_sha256"] != kill_run.get("prereg_sha256")):
        why.append("run.py or the prereg changed since `kill`")
    if not seal["sealed"]:
        why.append("the prereg on disk is not the sealed certify_size_curve prereg (sha256 not in HASHES.txt)")
    if why:
        print("A4: do not start:", "; ".join(why)); sys.exit(2)      # nothing computed, nothing written
    out = dict(prereg=PREREG, mode=mode, status="running", nwork=NWORK, base=BASE, **seal,
               note_2027=R_2027, indus=R_INDUS, A4=dict(free_mem_frac=fm, failures=why))
    dump(out, path)
    return out


def prepare(out, path, need_ceiling=False):
    """A7, then the label-free corpus build and A9. Sets the main process state and the worker payload."""
    global PAYLOAD
    out["A7"] = a7()
    if not out["A7"]["passed"]:
        stop(out, path, "A7: ogsl.zip or neoass_skeletons.tsv does not match its SHA-256 in the prereg")
    PAYLOAD, stats, a9 = build_corpus(need_ceiling)
    setup(PAYLOAD)
    out["A9"] = dict(problems=a9, passed=not a9); out["corpus"] = stats
    if a9:
        stop(out, path, "A9: " + "; ".join(a9))
    return stats


def load_json(name, why):
    p = HERE / name
    if not p.exists():
        sys.exit(f"{name} missing: {why}")
    return json.load(open(p))


def refuse_if_exists(*names):
    for n in names:
        if (HERE / n).exists():
            sys.exit(f"{n} exists: no rerun after any gain is seen (prereg Aborts). If its status shows a stop "
                     "before K0, nothing was scored; that is for the coordinator to judge, not this script.")


# ------------------------------------------------------------------ mode: kill (aborts and K0)
def kill():
    # PREREG-AMBIGUITY: "Results are written to the repo's results folder, not to a temporary directory": every
    # sibling study writes beside its run.py, and so does this one (experiments/certify_size_curve/, in the repo).
    path = HERE / "kill.json"
    refuse_if_exists("kill.json")
    out = start("kill", path); out["fallbacks"] = {}; fb = out["fallbacks"]
    t0 = time.time()
    stats = prepare(out, path)

    # ---- A2, part 1: the Measured tables that need no draw
    pT, pQ, lx = stats["pool_T"], stats["set_Q"], stats["lexicon"]
    bad = [f"pool T {k} {pT[k]} != {v}" for k, v in A2_POOL.items() if pT[k] != v]
    bad += [f"set Q {k} {pQ[k]} != {v}" for k, v in A2_Q.items() if pQ[k] != v]
    if abs(pT["key_purity"] - A2_PURITY) > A2_PURITY_TOL:
        bad.append(f"key purity {pT['key_purity']:.4f}")
    if abs(lx["density"][4] - A2_DENS4) > A2_DENS_TOL or lx["rule_LMIN"] != LMIN or lx["W_by_length"] != list(W_BY_LEN.values()):
        bad.append("primary lexicon density, LMIN or word-list counts")
    bad += [f"blocks at {s} u: {stats['blocks'][s]} != {n}" for s, n in NBLOCKS.items() if stats["blocks"][s] != n]
    out["A2"] = dict(part1_problems=bad)
    if bad:
        stop(out, path, "A2: recomputed Measured tables differ: " + "; ".join(bad) + ". Stop and redraft.")

    # ---- A2, part 2 + F4: label-free clean counts of every real draw (sealed order, hashed split)
    g = run_jobs(job_gate, [(s, b, "T") for s in SIZES + (REC32,) for b in range(NDRAWS[s])])
    shape = {}
    for s in SIZES + (REC32,):
        rs = [r for r in g if r["s"] == s]
        shape[s] = dict(draws=len(rs), tokens_median=statistics.median(r["tokens"] for r in rs),
                        clean_median=statistics.median(r["clean_positions"] for r in rs),
                        clean=[r["clean_positions"] for r in rs], tablets_median=statistics.median(r["tablets"] for r in rs),
                        thin_draws=[r["b"] + 1 for r in rs if r["thin"]])
    # PREREG-AMBIGUITY (A2 precedes K0): "a median clean count differs from its table value by more than 25%" is read
    # as relative, |median / table - 1| > 0.25, over the real draws this study uses at each size (first 20, 20, 13,
    # 6, 3 blocks and the one 32 u block; "real draws used" = the first blocks in the tablet order).
    off = [s for s in shape if abs(shape[s]["clean_median"] / CLEAN_TABLE[s] - 1) > A2_CLEAN_TOL]
    agree = all(r.get("clean_index_agrees", True) for r in g)
    out["A2"].update(shape=shape, clean_off=off, clean_index_agrees=agree, passed=not off and agree)
    fb["F4"] = dict(thin_draws_flagged={s: shape[s]["thin_draws"] for s in shape},
                    sizes_below_900=[s for s in SIZES if shape[s]["clean_median"] < F4_MIN])
    if not agree:
        stop(out, path, "the hashed clean-rule index disagrees with the sealed pairwise rule on a 1 u draw: stop")
    if off:
        stop(out, path, f"A2: median clean positions differ from the table by more than 25% at sizes {off}: stop and redraft")
    if fb["F4"]["sizes_below_900"]:                   # cannot be reached once A2 holds (0.75 x 1,614 > 900)
        stop(out, path, "A3 (F4): a graded size has a median below 900 clean positions")
    T = {s: shape[s]["tokens_median"] for s in shape}
    say("A7 A9 A2", pool_T=A2_POOL, clean_median={s: shape[s]["clean_median"] for s in shape}, tokens_median=T)

    # ---- A1: lift_score K0 draw-1 gain on Linear B, to 1e-9
    a1 = run_jobs(job_a1, [0])[0]
    out["A1"] = dict(a1, passed=a1["diff"] <= A1_TOL and a1["clean_index_agrees"] and a1["n"] == a1["sealed_n"])
    dump(out, path)
    if not out["A1"]["passed"]:
        stop(out, path, "A1: the study code does not reproduce the sealed lift_score K0 draw-1 gain to 1e-9")

    # ---- F3: trigram-only Hit@1 on the full-dose K0a plants, before any K0 gain
    nb = stats["blocks"]; vm = VOC
    full_tx = lambda k: plant_tx(1, k, 1.0, vm, nb[1])
    f3 = run_jobs(job_trigram, [full_tx(k) for k in range(1, 6)])
    f3_hit = any(r["trigram_hit1"] > F3_MAX for r in f3)
    fb["F3"] = dict(check=f3, applied=f3_hit)
    if f3_hit:
        vm = VOC_F3                                   # once; the rule becomes min(2,000 s, |W|) and stays so
        fb["F3"]["after"] = run_jobs(job_trigram, [full_tx(k) for k in range(1, 6)])

    # ---- A6: window model sums to 1 (fitted K0a draw-1 model); sees no gain
    a6 = run_jobs(job_a6, [full_tx(1)])[0]
    out["A6"] = dict(a6, passed=a6["max_dev"] <= A6_TOL)
    dump(out, path)
    if not out["A6"]["passed"]:
        stop(out, path, "A6: the window model does not sum to 1 (to 1e-9) over strings of 1 to 4 consonants")
    say("A1 F3 A6", a1_diff=a1["diff"], trigram_hit1=[round(r["trigram_hit1"], 1) for r in f3], f3_applied=f3_hit,
        a6_max_dev=a6["max_dev"])
    out["K0"] = {}; K0 = out["K0"]

    # ---- K0a, full dose: 5 plants at 1 u; true key, its unigram scramble, 5 shuffled keys (permuted lexicons
    #      record-only). Original grid.
    grid = GRID0
    by = gather(run_jobs(job_cells, [j for k in range(1, 6) for j in trio(f"k0a_full:{k}", full_tx(k), grid)]))
    rows = [dict(k=k, **grade(by[f"k0a_full:{k}"])) for k in range(1, 6)]
    for r in rows:
        r["ok_true"] = r["true"]["G"] >= K0_GAIN
    bars = dict(true_ok=count(rows, "ok_true"), scramble_ok=count(rows, "ok_scramble"), n1_ok=count(rows, "ok_n1"), needed=5)
    full_pass = bars["true_ok"] == 5 and bars["scramble_ok"] == 5 and bars["n1_ok"] == 5
    K0["a_full"] = dict(grid=grid, plants=rows, bars=bars, passed=full_pass)
    say("K0a full", passed=full_pass, **brief(rows), scramble_G=r4(r["scramble_true"]["G"] for r in rows),
        n1_median_G=r4(r["n1_median_G"] for r in rows), n1_max_G=r4(r["n1_max_G"] for r in rows))
    if not full_pass:
        out.update(reading_step1=1, reading=R1)
        stop(out, path, "K0 reading 1. " + R1 + " Nothing else runs.")
    dump(out, path)

    # ---- F1: grid edge, decided on the full-dose K0a plants; K0a is not regraded
    n4 = sum(r["true"]["lam"] == 4.0 for r in rows)
    fb["F1"] = dict(true_lam4_plants=n4, applied=n4 >= 3)
    # PREREG-AMBIGUITY (bears on K0): after F1 the values 8 and 16 are used "for every key in every cell", read as
    # every cell computed after the full-dose K0a plants, the low-dose K0a plants included.
    if n4 >= 3:
        grid = GRID0 + GRID_F1

    # ---- K0a, low dose: 20 plants at 1 u, true key only. Known answer: a miss (fewer than 16 of 20).
    def low_run(w, f5):
        by = gather(run_jobs(job_cells, [j for k in range(1, 21)
                                         for j in trio(f"k0a_low:{k}", plant_tx(1, k, w, vm, nb[1], f5), grid, "T")]))
        rows = [dict(k=k, **grade(by[f"k0a_low:{k}"])) for k in range(1, 21)]
        n = count(rows, "ok_gain")
        say("K0a low", dose=w, passes=n, known_answer_is_a_miss=n < 16, **brief(rows))
        return dict(dose=w, fresh_seeds=f5, plants=rows, passes=n, misses_as_planned=n < 16,
                    median_G=statistics.median(r["true"]["G"] for r in rows))

    low = LOW_DOSE; K0["a_low"] = low_run(low, False)
    fb["F5"] = dict(applied=not K0["a_low"]["misses_as_planned"])
    dump(out, path)
    if fb["F5"]["applied"]:
        # PREREG-AMBIGUITY (bears on K0): "The F5 rebuild adds 50,000 to each" is read as the spelling, filler and
        # dilution seeds of the twenty rebuilt 1 u plants only. The vocabulary order keeps its seed, and the K0b
        # plants, which were never built before, use their own unshifted seeds.
        low = LOW_DOSE_F5; K0["a_low_f5"] = low_run(low, True)
        dump(out, path)
        if not K0["a_low_f5"]["misses_as_planned"]:
            out.update(reading_step1=2, reading=R2)
            stop(out, path, "K0 reading 2 (A3, F5). " + R2 + " Nothing else runs.")
    low_1u = K0["a_low_f5" if fb["F5"]["applied"] else "a_low"]["median_G"]

    # ---- K0b: 16 u plant 1 first, timed (F6); its gains are not read for the projection
    kb = lambda s, k: trio(f"k0b:{s}:{k}", plant_tx(s, k, low, vm, nb[s]), grid)
    first = run_jobs(job_cells, kb(16, 1))
    t16 = sum(r["sec"] for r in first) / 12
    total, core = project_hours(t16, fb["F5"]["applied"])
    fb["F6"] = dict(seconds_per_key_cell_16u=t16, projected_hours=total, projected_hours_without_32u_and_pool_L=core,
                    drop_32u_and_pool_L=total > F6_DROP, stop=total > F6_DROP and core > F6_STOP)
    say("F6", **{k: (round(v, 1) if isinstance(v, float) else v) for k, v in fb["F6"].items()})
    dump(out, path)
    if fb["F6"]["stop"]:
        stop(out, path, "A3 (F6): projected cost above 90 processor-hours without the 32 u cell and pool L: stop and redraft")

    # ---- K0b (the other 19 plants) and K0c (five pure-filler texts at 16 u)
    # PREREG-AMBIGUITY (bears on K0): K0c is run with K0b in every case that reaches K0b, before the step-1 reading
    # is taken, because reading 3's added sentence needs every control. Its result changes the reading only between
    # 5 and 6.
    jobs = [j for k in range(2, 11) for j in kb(16, k)] + [j for k in range(1, 11) for j in kb(4, k)]
    jobs += [j for k in range(1, 6) for j in trio(f"k0c:{k}", plant_tx(16, k, 0.0, vm, nb[16]), grid, "T")]
    by = gather(first + run_jobs(job_cells, jobs))
    K0["b"] = {}; miss = {}
    for s in (4, 16):
        rows = [dict(k=k, **grade(by[f"k0b:{s}:{k}"])) for k in range(1, 11)]
        bars = {q: count(rows, q) for q in ("ok_gain", "ok_scramble", "ok_n1", "ok_C")}
        miss[s] = [q for q in ("ok_scramble", "ok_n1", "ok_C") if bars[q] < 8]
        K0["b"][s] = dict(plants=rows, bars=bars, needed=8, controls_missed=miss[s],
                          median_G=statistics.median(r["true"]["G"] for r in rows))
        say(f"K0b {s} u", **bars, **brief(rows), scramble_G=r4(r["scramble_true"]["G"] for r in rows),
            n1_median_G=r4(r["n1_median_G"] for r in rows), barC_min_delta=r4(min(c["delta"] for c in r["barC"]) for r in rows))
    rows = [dict(k=k, **by[f"k0c:{k}"]) for k in range(1, 6)]
    for r in rows:
        r["ok"] = r["true"]["G"] <= CTRL_BAR
    c_ok = count(rows, "ok")
    K0["c"] = dict(plants=rows, ok=c_ok, needed=5, passed=c_ok == 5)
    say("K0c", ok=c_ok, **brief(rows))
    gain_pass = K0["b"][16]["bars"]["ok_gain"] >= 8
    ctrl4, ctrl16 = not miss[4], not miss[16] and K0["c"]["passed"]
    K0.update(gain_bar_passed=gain_pass, controls_4u_passed=ctrl4, controls_16u_and_K0c_passed=ctrl16,
              low_dose=low, low_dose_median_G={1: low_1u, 4: K0["b"][4]["median_G"], 16: K0["b"][16]["median_G"]})
    lic = dict(step2=False, grid=grid, vm=vm, low_dose=low, tokens_median=T,
               run_32u=not fb["F6"]["drop_32u_and_pool_L"], run_pool_L=not fb["F6"]["drop_32u_and_pool_L"])
    out["license"] = lic; fb["F7"] = dict(applied=False)
    dump(out, path)

    # ---- step 1: the first reading whose condition holds
    if not gain_pass:
        txt = R3.format(dose=low)
        where = [f"{s} u" for s in (4, 16) if miss[s]] + ([] if K0["c"]["passed"] else ["16 u (K0c)"])
        if where:
            txt += " " + R3_CTRL.format(size=" and ".join(where))
        out.update(reading_step1=3, reading=txt)
        dump(out, path); print("K0 reading 3. " + txt, flush=True)
        # Real K3 cells at 1 u and 16 u run once, record-only. Nothing else runs.
        rec = {}
        for s in (1, 16):
            by = gather(run_jobs(job_cells, [j for b in range(NDRAWS[s]) for j in trio(f"k3:{s}:{b}", real_tx(s, b), grid, "T")]))
            rows = [dict(draw=b + 1, **by[f"k3:{s}:{b}"]) for b in range(NDRAWS[s])]
            rec[s] = dict(draws=rows, median_G=statistics.median(r["true"]["G"] for r in rows), graded=False)
            say(f"K3 {s} u record-only", **brief(rows))
        out["K3_record_only"] = rec
        out.update(status="done", seconds=round(time.time() - t0, 1))
        dump(out, path); sys.exit(1)
    if not ctrl4:
        out.update(reading_step1=4, reading=R4)
        stop(out, path, "K0 reading 4. " + R4 + " Nothing else runs.")
    if not ctrl16:
        fb["F7"] = dict(applied=True, missed=miss[16] + ([] if K0["c"]["passed"] else ["K0c"]))
        lic.update(step2=True, ladder=[1, 2, 4, 8], top=8, run_32u=False)
        out.update(reading_step1=5, reading=R5 + " F7 applies: the ladder is 1, 2, 4 and 8 u.")
    else:
        lic.update(step2=True, ladder=list(SIZES), top=16)
        out.update(reading_step1=6, reading="Every K0 bar passes. Step 2 runs on the ladder 1, 2, 4, 8, 16 u.")
    out.update(status="done", seconds=round(time.time() - t0, 1))
    dump(out, path); print(out["reading"] + " `k1` may run.", flush=True)


def licensed():
    kr = load_json("kill.json", "run `kill` first")
    if not (kr.get("status") == "done" and kr.get("license", {}).get("step2") is True and kr.get("reading_step1") in (5, 6)):
        sys.exit("kill.json does not license step 2 (K0 readings 1 to 4 end the study): refused")
    return kr, kr["license"]


# ------------------------------------------------------------------ mode: k1 (power at the true key's own dose)
def k1():
    kr, lic = licensed()
    refuse_if_exists("k1.json", "k1_targets.json")
    path, tpath = HERE / "k1.json", HERE / "k1_targets.json"
    out = start("k1", path, kill_run=kr); t0 = time.time()
    stats = prepare(out, path)
    grid, vm, ladder = tuple(float(x) for x in lic["grid"]), lic["vm"], lic["ladder"]
    # Plant k of size s sits on block (k - 1) mod the number of real draws of that size (10 plants on 6 and on 3
    # blocks at 8 u and 16 u); its target is D of the true key on that block's real development half.
    plants = [(s, k, (k - 1) % NDRAWS[s]) for s in ladder for k in range(1, K1_PLANTS[s] + 1)]
    tg = run_jobs(job_target, sorted({(s, b) for s, _, b in plants}))
    dump(dict(prereg=PREREG, what="K1 dose targets: D of the true key on the real development half of each block; "
              "written before any K1 plant gain is computed", written_unix=time.time(), targets=tg), tpath)
    target = {(r["s"], r["b"]): r["D"] for r in json.load(open(tpath))["targets"]}
    assert len(target) == len(tg)
    out["targets_file"] = "k1_targets.json"; dump(out, path)
    say("K1 targets written", D_median={s: med(d for (q, _), d in target.items() if q == s) for s in ladder})

    kb = run_jobs(job_k1, [dict(phase="build", s=s, k=k, b=b, vm=vm, target=target[(s, b)]) for s, k, b in plants])
    out["build"] = kb; dump(out, path)
    gains = run_jobs(job_k1, [dict(phase="gain", s=r["s"], k=r["k"], b=r["b"], vm=vm, target=r["target"], grid=grid,
                                   w=r["w"], D=r["D"]) for r in kb if r["scored"]])
    gain = {(r["s"], r["k"]): r for r in gains}; out["sizes"] = {}
    for s in ladder:
        rows = []
        for r in (x for x in kb if x["s"] == s):
            row = dict(k=r["k"], block=r["b"], status=r["status"], built=r["built"], target=r["target"], w=r["w"], D=r["D"])
            if (s, r["k"]) in gain:
                row.update(gain[(s, r["k"])]); row["ok"] = row["true"]["G"] >= GAIN_BAR
            else:
                row["ok"] = False
            rows.append(row)
        # PREREG-AMBIGUITY (K1 only, as lift_score): a "no dose above filler" plant is built and counts as a miss; a
        # plant whose target is above the full plant is scored at w = 1 and flagged; only "not landed in 12 steps"
        # plants are unbuilt and leave the denominator. The bar is 80% of the built plants, rounded up.
        nbuilt = sum(r["built"] for r in rows); need = (4 * nbuilt + 4) // 5
        enough = 10 * nbuilt >= 9 * len(rows)
        passes = sum(r["ok"] for r in rows if r["built"])
        out["sizes"][s] = dict(plants=rows, built=nbuilt, enough_built=enough, passes=passes, needed=need,
                               powered=bool(enough and passes >= need),
                               no_dose_above_filler=[r["k"] for r in rows if r["status"] == "no dose above filler"],
                               flagged_w1=[r["k"] for r in rows if r["status"].startswith("target above")],
                               unbuilt=[r["k"] for r in rows if not r["built"]])
        say(f"K1 {s} u", powered=out["sizes"][s]["powered"], passes=passes, needed=need, built=nbuilt,
            no_dose_above_filler=len(out["sizes"][s]["no_dose_above_filler"]),
            G=r4(r["true"]["G"] if "true" in r else None for r in rows),
            hit1_lift=[round(r["true"]["hit1_lift"], 2) if "true" in r else None for r in rows])
    out.update(status="done", seconds=round(time.time() - t0, 1))
    dump(out, path); print("K1 done; `real` may run", flush=True)


# ------------------------------------------------------------------ mode: real (K2, bar C, K3, fixed sets, 32 u)
def fmt(x):
    return f"{int(round(x)):,}"


def label_of(k1p, k3p, ctl):
    if k1p and k3p:
        return "shows" if ctl else "not specific"
    if k1p:
        return "does not show"
    return "seen without planted power" if k3p else "unpowered"


def bound_statement(m, T, ladder, N, kr):
    """Reading E only: the flat / rising rule, and the check of the rule on the low-dose plant medians."""
    pos = [s for s in ladder if m[s] > 0]; txt = f"The need is above {fmt(N)} tokens by an unknown factor."; fit = None
    if len(pos) >= 3:
        x = np.array([math.log2(T[s]) for s in pos]); y = np.array([m[s] for s in pos])
        slope, icpt = np.polyfit(x, y, 1)
        fit = dict(sizes=pos, slope=float(slope), intercept=float(icpt))
        if slope > 0:
            cross = 2 ** ((GAIN_BAR - icpt) / slope); fit["crossing_tokens"] = float(cross)
            txt = (f"Extrapolated, not shown: about {fmt(cross)} tokens." if cross <= 4 * N
                   else "Above 4 x N; not extrapolated further.")
    pm = {int(k): v for k, v in kr["K0"]["low_dose_median_G"].items()}
    line = pm[1] + (pm[4] - pm[1]) / (math.log2(T[4]) - math.log2(T[1])) * (math.log2(T[16]) - math.log2(T[1]))
    return txt, dict(fit=fit, rule_check=dict(plant_medians=pm, line_at_16u=line, measured_16u=pm[16], miss=line - pm[16]))


def real():
    kr, lic = licensed()
    k1r = load_json("k1.json", "run `k1` first")
    if k1r.get("status") != "done":
        sys.exit("k1.json is not done: refused")
    refuse_if_exists("real.json")
    path = HERE / "real.json"
    out = start("real", path, kill_run=kr); t0 = time.time()
    prepare(out, path)
    grid, ladder, top = tuple(float(x) for x in lic["grid"]), lic["ladder"], lic["top"]
    T = {int(k): v for k, v in lic["tokens_median"].items()}; N = T[top]
    # PREREG-AMBIGUITY (fixed sets, record-only): after F7 the three chains keep their start tablets (1 u blocks 0,
    # 16 and 32) and their top block is the 8 u block that holds them.
    chain_of = lambda s, b: (b * s) // 16 if (b * s) % 16 == 0 and b * s < 48 else None
    out["sizes"] = {}; fixed = defaultdict(dict)
    for s in ladder:
        bound = s == 16
        jobs = []
        for b in range(NDRAWS[s]):
            c = chain_of(s, b)
            jobs += trio(f"{s}:{b}", real_tx(s, b), grid, fixed=None if c is None else (c, top))
        for c in range(3):                            # chain blocks outside the graded draws (1 u block 32)
            b = 16 * c // s
            if b >= NDRAWS[s]:
                jobs += trio(f"fx:{s}:{b}", real_tx(s, b), grid, "T", fixed=(c, top))
        by = gather(run_jobs(job_cells, jobs))
        rows = [dict(draw=b + 1, **grade(by[f"{s}:{b}"], bound)) for b in range(NDRAWS[s])]
        for gid, r in by.items():
            if "fixed" in r.get("true", {}):
                b = int(gid.split(":")[-1]); fixed[chain_of(s, b)][s] = dict(r["true"]["fixed"], lam=r["true"]["lam"])
        bar = PASSBAR[s]
        n = {q: count(rows, q) for q in ("ok_gain", "ok_scramble", "ok_n1", "ok_C")}
        k1p = bool(k1r["sizes"][str(s)]["powered"]); k3p = n["ok_gain"] >= bar
        k2p = n["ok_scramble"] >= bar and n["ok_n1"] >= bar; cp = n["ok_C"] >= bar
        lab = label_of(k1p, k3p, k2p and cp)
        out["sizes"][s] = dict(draws=rows, pass_bar=bar, one_sided_bound=bound, counts=n, K1_powered=k1p, K3_passed=k3p,
                               K2_passed=k2p, barC_passed=cp, label=lab, tokens_median=T[s],
                               median_G=statistics.median(r["true"]["G"] for r in rows),
                               thin_draws=[r["draw"] for r in rows if r["counts"]["text"]["thin"]],
                               perm_lexicon_D=[[e["D"] for e in r["perm"]] for r in rows],
                               true_lexicon_D=[r["true"]["D"] for r in rows])
        if lab == "seen without planted power":
            out["sizes"][s]["note"] = "plant harsher than real text at this size"
        dump(out, path)
        say(f"real {s} u", label=lab, pass_bar=bar, **n, **brief(rows), scramble_G=r4(r["scramble_true"]["G"] for r in rows),
            n1_median_G=r4(r["n1_median_G"] for r in rows), n1_max_G=r4(r["n1_max_G"] for r in rows),
            barC_min_L=r4(min((c["L"] for c in r["barC"] if c["L"] is not None), default=None) for r in rows))
    out["fixed_sets"] = {c: fixed[c] for c in sorted(fixed)}

    # ---- labels -> the curve reading (exactly one; the first whose condition holds)
    lab = {s: out["sizes"][s]["label"] for s in ladder}; m = {s: out["sizes"][s]["median_G"] for s in ladder}
    powered = [s for s in ladder if out["sizes"][s]["K1_powered"]]; shows = [s for s in ladder if lab[s] == "shows"]
    extra = {}
    if not powered:
        code, txt = "A", RA.format(N=fmt(N))
        extra["D_by_size"] = {s: med(out["sizes"][s]["true_lexicon_D"]) for s in ladder}
        extra["seen_without_planted_power"] = [s for s in ladder if lab[s] == "seen without planted power"]
    elif shows:
        ss = shows[0]; above = [s for s in powered if s > ss and lab[s] in ("does not show", "not specific")]
        if not above:
            code, txt = "B", RB.format(T=fmt(T[ss]))
            if ss == ladder[0]:
                txt += " It shows at the smallest size run."
            elif ladder[ladder.index(ss) - 1] in powered:
                txt += " The size below did not show."
            else:
                txt += " The size below was unpowered."
            up = [s for s in ladder if s > ss and s not in powered]
            if up:
                txt += f" Sizes {', '.join(f'{s} u' for s in up)} above it were unpowered and neither confirm nor break this."
            extra["s_star"] = ss; extra["K4"] = "pending: run `k4`"
        else:
            code, txt = "C", RC.format(T=fmt(T[ss]), T2=fmt(T[above[0]])) + " K4 does not run."
    elif any(lab[s] == "not specific" for s in powered):
        code, txt = "D", RD.format(T=fmt(T[min(s for s in powered if lab[s] == "not specific")]), N=fmt(N))
    else:
        code, txt = "E", RE.format(N=fmt(N), T=fmt(T[powered[0]]))
        if top == 16:
            b_txt, extra["bound"] = bound_statement(m, T, ladder, N, kr)
        else:
            # PREREG-AMBIGUITY (reading E after F7): the rule check needs a measured 16 u plant median and is made
            # only when 16 u is on the ladder; the flat / rising rule itself is applied to the cut ladder.
            b_txt, extra["bound"] = bound_statement(m, T, ladder, N, dict(K0=dict(low_dose_median_G={1: 0, 4: 0, 16: 0})))
            extra["bound"].pop("rule_check")
        txt += " " + b_txt
    fx = {nm: {s: med(fixed[c][s][nm]["G"] for c in fixed if s in fixed[c]) for s in ladder} for nm in ("F1", "Ftop")}
    txt += " " + R_ALWAYS + f" On fixed positions the gain was {fx['F1']} on F1 and {fx['Ftop']} on Ftop (median of the chains, by size in u)."
    out.update(labels=lab, median_G=m, reading_code=code, reading=txt, reading_detail=extra, k4_may_run=code == "B")
    dump(out, path)

    # ---- the one 32 u draw: last, record-only, one line
    if lic.get("run_32u") and top == 16:
        by = gather(run_jobs(job_cells, trio("32:0", real_tx(REC32, 0), grid)))
        r32 = grade(by["32:0"]); out["record_32u"] = dict(r32, graded=False)
        out["reading"] += f" The one 32 u draw gave G {r32['true']['G']:.4f}."
        say("32 u record-only", **brief([r32]), scramble_G=round(r32["scramble_true"]["G"], 4), n1_median_G=round(r32["n1_median_G"], 4))
    else:
        out["record_32u"] = "not run (F6 or F7)"
    out.update(status="done", seconds=round(time.time() - t0, 1))
    dump(out, path); print(f"Reading {code}. " + out["reading"], flush=True)


# ------------------------------------------------------------------ mode: extras (record-only arms)
def extras():
    kr, lic = licensed()
    rr = load_json("real.json", "run `real` first")
    if rr.get("status") != "done":
        sys.exit("real.json is not done: refused")
    refuse_if_exists("extras.json")
    path = HERE / "extras.json"
    out = start("extras", path, kill_run=kr); t0 = time.time()
    stats = prepare(out, path, need_ceiling=True)
    grid, ladder, top = tuple(float(x) for x in lic["grid"]), lic["ladder"], lic["top"]
    k3 = lambda s, b: rr["sizes"][str(s)]["draws"][b]["true"]["G"]
    out["grades"] = "nothing: every number here is record-only and changes no label, reading or bound"

    # ---- ceiling lexicon: the true key's G and bar C at 1, 4 and 16 u, on the K3 draws
    out["ceiling"] = {}; parts = []
    for s in [x for x in (1, 4, 16) if x in ladder]:
        by = gather(run_jobs(job_cells, [j for b in range(NDRAWS[s])
                                         for j in trio(f"c:{s}:{b}", real_tx(s, b), grid, "A", lex="ceiling")]))
        rows = [dict(draw=b + 1, primary_G=k3(s, b), **grade(by[f"c:{s}:{b}"], s == 16)) for b in range(NDRAWS[s])]
        out["ceiling"][s] = dict(draws=rows, median_G=statistics.median(r["true"]["G"] for r in rows), barC_held=count(rows, "ok_C"))
        parts.append(f"{out['ceiling'][s]['median_G']:.4f} at {s} u (bar C held in {count(rows, 'ok_C')} of {len(rows)})")
        dump(out, path); say(f"ceiling {s} u", barC_held=count(rows, "ok_C"), **brief(rows))
    out["ceiling_sentence"] = ("With a lexicon of Old Assyrian words from other tablets, which no claimant could hold, "
                               "the true key's median G was " + "; ".join(parts) + ".")

    # ---- uncertain-period sensitivity: all of set Q added, at 1 u and the top graded size
    out["sensitivity"] = {}; parts = []
    for s in (1, top):
        by = gather(run_jobs(job_cells, [j for b in range(NDRAWS[s])
                                         for j in trio(f"q:{s}:{b}", real_tx(s, b, q=True), grid, "T")]))
        rows = [dict(draw=b + 1, G_without=k3(s, b), **grade(by[f"q:{s}:{b}"], s == 16)) for b in range(NDRAWS[s])]
        mw, mo = statistics.median(r["true"]["G"] for r in rows), statistics.median(r["G_without"] for r in rows)
        n = count(rows, "ok_gain"); differ = (n >= PASSBAR[s]) != bool(rr["sizes"][str(s)]["K3_passed"])
        out["sensitivity"][s] = dict(draws=rows, median_G_with=mw, median_G_without=mo, difference=mw - mo,
                                     at_or_above_bar_with_Q=n, K3_verdict_would_differ=differ)
        parts.append(f"{mw:.4f} against {mo:.4f} at {s} u ({'would' if differ else 'would not'} have differed)")
        dump(out, path); say(f"set Q {s} u", median_with=round(mw, 4), median_without=round(mo, 4), verdict_would_differ=differ)
    out["sensitivity_sentence"] = (f"With the {stats['set_Q']['tablets_with_chunks']} tablets of uncertain period added, the "
                                   "true key's median G was " + ", and ".join(parts) + ". The graded verdict stands.")

    # ---- pool L (letters only): true key and the K2 controls at 1, 2 and 4 u
    if lic.get("run_pool_L"):
        # PREREG-AMBIGUITY (pool L, record-only): pool L uses pool T's chunks, key and tablet order, restricted to
        # letters, with blocks cut the same way and the same seed formulas; the draws are every whole block (up to
        # 14, 7 and 3).
        out["pool_L"] = {}
        for s in (1, 2, 4):
            nd = stats["pool_L"]["chunks"] // (UNIT * s)
            by = gather(run_jobs(job_cells, [j for b in range(nd) for j in trio(f"l:{s}:{b}", real_tx(s, b, "L"), grid, "TBC")]))
            rows = [dict(draw=b + 1, **grade(by[f"l:{s}:{b}"])) for b in range(nd)]
            out["pool_L"][s] = dict(draws=rows, median_G=med(r["true"]["G"] for r in rows),
                                    counts={q: count(rows, q) for q in ("ok_gain", "ok_scramble", "ok_n1")})
            dump(out, path); say(f"pool L {s} u", **out["pool_L"][s]["counts"], **brief(rows))
    else:
        out["pool_L"] = "not run (F6)"
    out.update(status="done", seconds=round(time.time() - t0, 1))
    dump(out, path); print(out["ceiling_sentence"] + " " + out["sensitivity_sentence"], flush=True)


# ------------------------------------------------------------------ mode: k4 (keys fitted to noise, at s* only)
def k4():
    kr, lic = licensed()
    rr = load_json("real.json", "run `real` first")
    if not (rr.get("status") == "done" and rr.get("reading_code") == "B" and rr.get("k4_may_run") is True):
        sys.exit("real.json does not hold reading B: K4 does not run")
    refuse_if_exists("k4.json")
    path = HERE / "k4.json"
    out = start("k4", path, kill_run=kr); t0 = time.time()
    prepare(out, path)
    grid = tuple(float(x) for x in lic["grid"]); s = int(rr["reading_detail"]["s_star"]); bar = PASSBAR[s]
    res = run_jobs(job_k4, [dict(s=s, b=b, grid=grid, which=w) for b in range(NDRAWS[s]) for w in ("n2", "n3")])
    rows = []
    for b in range(NDRAWS[s]):
        n2 = [r for r in res if r["b"] == b and r["which"] == "n2"][0]["keys"]
        n3 = [r for r in res if r["b"] == b and r["which"] == "n3"][0]["keys"]
        tg = rr["sizes"][str(s)]["draws"][b]["true"]["G"]
        mean_n2 = sum(e["G"] for e in n2) / len(n2); mx = max(e["G"] for e in n2 + n3)
        # PREREG-AMBIGUITY (K4 only): bars A (mean G of the 9 N2 keys <= 0.005) and B (true key G above every N2 and
        # N3 key) are point rules at every size, 16 u included: the prereg defines no clustered bound for them.
        rows.append(dict(draw=b + 1, n2=n2, n3=n3, n2_mean_G=mean_n2, noise_max_G=mx, true_G=tg,
                         ok_A=mean_n2 <= CTRL_BAR, ok_B=tg > mx))
    na, nbb = count(rows, "ok_A"), count(rows, "ok_B"); ok = na >= bar and nbb >= bar
    out.update(s_star=s, pass_bar=bar, draws=rows, bar_A=dict(passes=na, passed=na >= bar), bar_B=dict(passes=nbb, passed=nbb >= bar),
               sentence="Keys fitted to noise by these two fitters " + ("do not" if ok else "do") + " show it too.",
               shows_is_certifies=False, status="done", seconds=round(time.time() - t0, 1))
    dump(out, path)
    say("K4", s_star=s, bar_A=out["bar_A"], bar_B=out["bar_B"],
        noise_median_hit1_lift=med((e["hit1_lift"] for r in rows for e in r["n2"] + r["n3"]), 2))
    print(rr["reading"] + " " + out["sentence"], flush=True)


MODES = dict(kill=kill, k1=k1, real=real, extras=extras, k4=k4)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in MODES:
        sys.exit("usage: run.py kill|k1|real|extras|k4   (in this order, each under board/run.sh)")
    a5_hook(); load_sealed()
    MODES[mode]()
