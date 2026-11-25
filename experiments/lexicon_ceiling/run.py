"""Lexicon ceiling on Old Assyrian (prereg docs/prereg/lexicon_ceiling.md, SEALED v2, tag `lexicon_ceiling`).
Run once (from the repo root, detached, under the Indus compute lock; A4 checks the lock and the 20% memory guard):
  board/run.sh .venv/bin/python -I experiments/lexicon_ceiling/run.py kill > experiments/lexicon_ceiling/kill.out 2>&1
Workers: env NWORK (default 4, capped at 4). One mode, `kill`. Exit 2: a seal mismatch or bad usage (nothing computed).
Exit 1: any planned stop (A4, an existing output, an abort, a verification miss, reading 0b or 0c). Exit 0: readings 1-4.

Order (the prereg's; no gain of this study exists before the ledger is on disk, and no real-text gain before FC):
  seal:   this prereg against its HASHES.txt line; the sealed certify_size_curve run.py against its code line. Exit 2.
  start:  refuse if kill.json / ledger.json exist; A4; A7; the sealed label-free corpus build; A9.
  gate:   A2 (pool, types, tablets with a word, shortfall, list size, near-copy counts), F4 clean counts.
  lists:  per draw: exclusion 1 (block ids), exclusion 2 (near-copies), the size-matched list; V1 provenance, V2 second
          build by deletion, V3 canaries on draw 1, A8 (builder with no near-copies == sealed ceiling_lex), A9;
          V4 ledger.json. Any miss stops.
  A1:     sealed K0a plant 1 and sealed real draw 4 (primary list) through the copied functions, to 1e-9.
  K0b:    F3 (trigram Hit@1), A6, 5 full-dose plants from the ceiling list; bars; F1; FC (P1 / P2 / stop).
  K0a:    20 sealed 1 u draws: true key, 5 permuted copies, 5 shuffled keys, all with the draw's ceiling list. T, P, S, C.
  record: scramble, leak dial, filler, counts, in this order, each started only inside the FT clock (4.5 h).
  reading: exactly one of 1, 2, 3, 4, with the frozen added sentences.

Reuse. The sealed experiments/certify_size_curve/run.py is read once, its bytes are hashed, and those same bytes are
executed as a module (`S`); no bytecode is written and no name of that module is assigned from here. Its scoring
machinery is called unchanged. The plant generator, scramble, shuffled-key, text-builder, ceiling-builder and job
functions are parameterised copies (base and word list as arguments). Sealed modes kill / k1 / real / extras / k4 are
never called. No Indus step: M77 enters as text lengths only, inside the sealed corpus build. splits_v2, claim-bench
key files and saao.zip are never opened (audit hook on file opens). No key value or per-position array is written.
Every judgement call is marked PREREG-AMBIGUITY.
"""
import csv, hashlib, json, math, os, random, re, statistics, sys, time, types, zipfile
from collections import Counter, defaultdict
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.dont_write_bytecode = True                        # the sealed folders get no new __pycache__ entry from this run
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PREREG = "docs/prereg/lexicon_ceiling.md"; TAG = "lexicon_ceiling"
SEALED_REL = "experiments/certify_size_curve/run.py"; SEALED_TAG = "certify_size_curve_code"
SEALED_KILL = ROOT / "experiments/certify_size_curve/kill.json"
HASHES = ROOT / "docs/prereg/HASHES.txt"
NWORK = max(1, min(4, int(os.environ.get("NWORK", "4"))))
BASE_NEW = 20270301                                   # study base: K0b plants and filler texts only (prereg Seeds)
NDRAW, NPLANT, NFILL = 20, 5, 5
NEAR_LINES, NEAR_SIGNS = 3, 5                         # exclusion 2: >= 3 identical kept lines of >= 5 signs
CANARY_N = 1000
NEW_ID = "X999999"                                    # id of the synthetic near-copy (V3); not a CDLI P number
FT_SEC = 4.5 * 3600
A1_PLANT_G = 0.3731052945333844                       # sealed K0a plant-1 gain (prereg A1)
A1_DRAW = 4
PASS_T, FAIL_T, CTRL_MAX, C_MIN = 16, 4, 1, 16
FC_MAX = 1                                            # FC: a rule is usable if it flags 0 or 1 of the 5 plants
A2_TABLETS = 3951
A2_TYPES = {4: 1967, 5: 1793, 6: 720, 7: 191}
A2_WORD_TABLETS = 3821
A2_LIST = 2815
A2_NEAR = [9, 8, 4, 14, 3, 19, 15, 5, 9, 3, 5, 8, 10, 9, 9, 10, 6, 7, 2, 7]
MEASURED = dict(word_tokens=40322, lines_on_two_or_more_tablets=2436, tablets_in_draw=[58, 86, 75.5],
                source_tablets=[3730, 3761], source_word_tokens=[39305, 39540],
                types_outside_min={4: 1946, 5: 1765, 6: 704, 7: 185}, words_changed_by_exclusion_2=[0, 12],
                clean_median=1594.5, clean_draw_16=895)

# ------------------------------------------------------------------ frozen readings (verbatim from the prereg)
R0B = "The pipeline did not find a language planted from the ceiling list ({bars}). Nothing is learned about real text."
R0C = ("Letter-permuted copies gain on planted text under both rules. The real-text question cannot be asked with this "
       "control.")
R1 = ("The score works on real text with a matched lexicon, so the limit for Indus is that no matched lexicon can "
      "exist.")
R2 = ("A same-archive word list raises restoration on real text in {T} of 20 draws, but the controls do not hold: "
      "letter-permuted copies gained in {P} of 20, shuffled keys in {S} of 20, and the true list beat all five copies "
      "in {C} of 20. The gain is not shown to be the lexicon's or the key's. The score is not shown to work on real "
      "text.")
R3 = "This score has no power on real text even with the best lexicon, so restoration is untested, not closed."
R4 = ("With the best lexicon the score gains on real text in {T} of 20 draws, under the 16 needed. It has some power on "
      "real text and too little to certify. Lexicon distance explains part of the real-text null and the score explains "
      "the rest; this study cannot size the two.")
R4_CTRL = ("Permuted copies gained in {P} of 20 and shuffled keys in {S} of 20, so even this part is not shown to be "
           "the lexicon's.")
X_GATE = "G is the gate. Hit@1 lift was {lo:.2f} to {hi:.2f} points, median {med:.2f}. A G pass alone does not meet the 2027 clause."
X_RULE = "The rule in force was {rule}. Under the other rule P was {other}. Bar C held in {C} of 20. S was {S}."
X_SCR = "The true key on the scramble reached 0.02 in {n} of 20 draws."
X_SCR_FT = "The scramble cell did not run (FT)."
X_LEAK = ("With the draw's own tablets left in the source (a deliberate leak), median G was {leak:.4f} against "
          "{clean:.4f}.")
X_DOSE = ("The dose D with the ceiling list was {lo:.3f} to {hi:.3f}; with the Neo-Assyrian list it was −0.067 "
          "to +0.012; on the sealed quarter-dose plants −0.078 to −0.021; on the full-dose plants 0.20 to "
          "0.26.")
X_FILL = "On the order-1 filler the ceiling list gave G {vals}."
X_COV = ("The ceiling list held {c:.1%} of the held-out word tokens of 4 to 7 consonants; the Neo-Assyrian list held "
         "{n:.1%}.")
X_ONE = ("This is one script, one archive and an oracle key. The list was built with the editors' word division and "
         "holds names. It is an upper bound that no claimant could hold.")
X_CSC = "The result and reading of `certify_size_curve` are unchanged."
X_INDUS = "No Indus key is scored. No outcome supports or counts against any Indus key, and none licenses a run of one."
NOTE_2027 = ("G is this study's gate. Hit@1 is the 2027-clause measure and is reported on every cell. A G pass alone "
             "does not meet the 2027 clause.")

# ------------------------------------------------------------------ per-process state
S = None                                              # the sealed certify_size_curve run.py, executed from hashed bytes
POOL = None
PAYLOAD = None
SEALED_SHA = None
INIT_ERR = None


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes_line(rel, tag):
    # PREREG-AMBIGUITY: if HASHES.txt holds several lines for one path and tag, the last one is the seal in force.
    got = None
    with open(HASHES, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 4 and p[1] == rel and p[-1] == tag:
                got = p[0]
    return got


def seal_check():
    """Before anything else: this prereg and the sealed certify_size_curve run.py against their HASHES.txt lines."""
    info, bad = {}, []
    for name, rel, tag in (("prereg", PREREG, TAG), ("sealed_code", SEALED_REL, SEALED_TAG)):
        want = hashes_line(rel, tag); have = sha256_of(ROOT / rel)
        info[name + "_sha256"] = have
        if want is None:
            bad.append(f"no HASHES.txt line for {rel} with tag {tag}")
        elif want != have:
            bad.append(f"{rel}: sha256 {have} is not the sealed {want}")
    return info, bad


def load_sealed_run(expect):
    """Load the sealed run.py by path: read its bytes, check them against the sealed hash, execute those bytes."""
    global S, SEALED_SHA
    if S is not None:
        return
    src = (ROOT / SEALED_REL).read_bytes()
    if hashlib.sha256(src).hexdigest() != expect:
        raise RuntimeError("A7: the sealed certify_size_curve run.py does not match its SHA-256")
    mod = types.ModuleType("certify_size_curve_run")
    mod.__file__ = str(ROOT / SEALED_REL)             # the loader's own attribute (its HERE / ROOT); no study name is set
    sys.modules[mod.__name__] = mod
    exec(compile(src, str(ROOT / SEALED_REL), "exec"), mod.__dict__)
    mod.load_sealed()                                 # sealed lb_shape_ladder / lb_certify: code only, no data
    assert set(mod._A5_ALLOW) <= set(_ALLOW), "the sealed file-open list is not inside this study's list"
    S, SEALED_SHA = mod, expect


# ------------------------------------------------------------------ A5 / A7 / Indus rule (copy of the sealed hook)
_ALLOW = ("experiments/lb_certify/", "experiments/lb_shape_ladder/", "experiments/cognate_decipher/ext/greek/",
          "experiments/short_labels/raw/cdli/", "corpus/", "board/compute.lock/", ".venv/",
          "sources/paragorth_Indus-/data/codelib/linear_b.jsonl", "data/m77_texts.jsonl",
          "experiments/lift_score/kill.json", "docs/prereg/certify_size_curve.md", "docs/prereg/HASHES.txt",
          "experiments/certify_size_curve/raw/ogsl/ogsl.zip",
          "experiments/certify_size_curve/raw/saao/neoass_skeletons.tsv",
          "experiments/certify_size_curve/run.py",
          # added by this study (prereg change 8, and what A1 and the seal check must read)
          "experiments/certify_size_curve/kill.json", PREREG, "experiments/lexicon_ceiling/run.py")
_OUT = re.compile(r"^experiments/lexicon_ceiling/(?:(?:kill|ledger)\.json(?:\.tmp)?|kill\.out)$")
_HOOK_ON = False


def a5_hook():
    """Inside the repo only the files this study needs may be opened; splits_v2, any key file and any other lexicon
    file raise before they are read. saao.zip is refused wherever it is."""
    global _HOOK_ON
    if _HOOK_ON:
        return
    _HOOK_ON = True
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
        if "splits" in rel or not (_OUT.match(rel) or any(rel == a or (a.endswith("/") and rel.startswith(a))
                                                            for a in _ALLOW)):
            raise RuntimeError("A5: the study tried to open a repo file outside its data list: " + rel)

    sys.addaudithook(hook)


def stop(out, path, msg, code="0a", reading=None):
    # PREREG-AMBIGUITY: a planned stop writes status "stopped" (as the sealed study); "done" is kept for readings 1-4.
    out.update(stop=msg, status="stopped", reading_code=code, reading=reading)
    S.dump(out, path); print("STOP:", msg, flush=True)
    if POOL is not None:
        POOL.close(); POOL.join()
    sys.exit(1)


# ------------------------------------------------------------------ label-free: rows, near-copies, the ceiling list
def read_rows():
    """Pool T kept lines as raw text rows, read again from the catalogue and the text file by a copy of the sealed
    build_corpus loops. Returns ([(tablet id, line text, sign count)], set Q ids, value -> sign map). Label-free."""
    sl = json.loads(zipfile.ZipFile(S.OGSL).read("ogsl/ogsl-sl.json"))
    v2s = {}
    for name, d in sl["signs"].items():
        for v in d.get("values", []):
            v2s.setdefault(v, name)
    csv.field_size_limit(10 ** 9)
    cat = {}
    with open(S.RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if not pid.isdigit():
                continue
            per = (r.get("period") or "").strip(); g = (r.get("genre") or "").strip()
            ot = (r.get("object_type") or "").strip().lower()
            if per not in (S.P_T, S.P_Q) or g not in S.GENRES or not ot.startswith("tablet"):
                continue
            if ot not in S.OBJ:
                continue
            cat["P" + pid.zfill(6)] = "T" if per == S.P_T else "Q"
    rows = []; pid = None; lang_ok = True
    with open(S.RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                pid = line[1:8]; lang_ok = True
                continue
            if pid not in cat:
                continue
            if line.startswith("#atf: lang"):
                lang_ok = "akk" in line
                continue
            m = S.LINE.match(line)
            if not m or not lang_ok or cat[pid] != "T":
                continue
            t = S.tok(m.group(2))
            if t:
                # PREREG-AMBIGUITY (A2, so whether K0 starts): a line's sign count = its sealed-tokeniser R and D items, mapped or not.
                rows.append((pid, m.group(2), sum(k in ("R", "D") for k, _ in t)))
    return rows, {p for p, tg in cat.items() if tg == "Q"}, v2s


def line_key(content):
    # PREREG-AMBIGUITY (A2): a line is compared after removing < > ! ? * and collapsing spaces, and nothing else.
    return " ".join(re.sub(r"[<>!?*]", "", content).split())


def tab_counters(rows, v2s):
    """Tablet id -> Counter of word skeletons, by the sealed ceiling word rule (S.ceiling_words), from raw rows."""
    out = defaultdict(Counter)
    for pid, content, _ in rows:
        for sk in S.ceiling_words(content, v2s, S.KEY):
            out[pid][sk] += 1
    return dict(out)


def near_copies(inside, long_by_tab, idx, extra=None):
    """Exclusion 2: tablets outside the block that share >= 3 identical long lines with any one tablet of the block.
    `extra` = {id: set of long lines} adds synthetic tablets (V3 only)."""
    # PREREG-AMBIGUITY (A2): shared lines are counted as distinct line texts, not as line instances.
    # PREREG-AMBIGUITY (A2): every pool T tablet with a kept line is a candidate, not only tablets with a usable word.
    near = set()
    for t in inside:
        mine = long_by_tab.get(t)
        if not mine:
            continue
        cnt = Counter()
        for ln in mine:
            for u in idx[ln]:
                if u not in inside:
                    cnt[u] += 1
        near |= {u for u, n in cnt.items() if n >= NEAR_LINES}
        for u, lines in (extra or {}).items():
            if u not in inside and len(lines & mine) >= NEAR_LINES:
                near.add(u)
    return near


def ceil_build(ceil, drop):
    """Parameterised copy of the sealed ceiling_lex: skeletons from the tablets of `ceil` not in `drop`, ranked by
    distinct source tablets, then tokens, then alphabetically, size-matched to the primary list at each length.
    Returns (words, info, source ids, {kept skeleton: its source ids})."""
    tabs, toks, src, prov = Counter(), Counter(), set(), defaultdict(set)
    for pid, c in ceil.items():
        if pid in drop:
            continue
        src.add(pid)
        for sk, n in c.items():
            tabs[sk] += 1; toks[sk] += n; prov[sk].add(pid)
    words, short, single, avail = [], {}, {}, {}
    for n in range(S.LMIN, S.MAXW + 1):
        r = sorted((sk for sk in tabs if len(sk) == n), key=lambda sk: (-tabs[sk], -toks[sk], sk))
        keep = r[:S.W_BY_LEN[n]]
        words += keep; short[n] = max(0, S.W_BY_LEN[n] - len(r)); avail[n] = len(r)
        single[n] = sum(tabs[sk] == 1 for sk in keep)
    info = dict(words=len(words), shortfall_by_length=short, source_tablets=len(src), types_available=avail,
                source_word_tokens=sum(toks.values()), one_tablet_words_by_length=single,
                last_ranked_tablets={n: min((tabs[sk] for sk in words if len(sk) == n), default=0)
                                     for n in range(S.LMIN, S.MAXW + 1)})
    return words, info, src, {sk: prov[sk] for sk in words}


def list_sha(words):
    """SHA-256 of the sorted list, one skeleton per line (each letter is one code point)."""
    return hashlib.sha256("\n".join(sorted("".join(w) for w in words)).encode("utf-8")).hexdigest()


def block_ids(b):
    # PREREG-AMBIGUITY: a block's tablets = every id with a chunk in the block's slice, as sealed ceiling_lex (a tablet cut by the edge counts).
    return {tid for tid, _ in S.SEQ[b * S.UNIT:(b + 1) * S.UNIT]}


def canaries(ceil, long_by_tab, idx, pool_types):
    """V3, on draw 1. A 4-consonant skeleton that occurs nowhere in the pool is added with a high count, in turn, to
    five tablets; the full build (both exclusions) is rerun each time. The lists are thrown away; nothing is scored."""
    # PREREG-AMBIGUITY (A8): the canary is the first 4-letter string in alphabet order absent from the pool; "high count" = 1,000 tokens added to the tablet's word counter.
    # PREREG-AMBIGUITY (A8): tablets = first held-out block tablet with >= 3 long lines, first development block tablet, first source id in sorted order.
    inside = block_ids(0)
    canary = next(w for w in product(S.OA_ALPHA, repeat=4) if w not in pool_types)
    order = S.block(1, 0)
    ho_t = next((tid for tid, _, d in order if not d and len(long_by_tab.get(tid, ())) >= NEAR_LINES), None)
    dev_t = next((tid for tid, _, d in order if d), None)
    near0 = near_copies(inside, long_by_tab, idx)
    src_t = min((p for p in ceil if p not in inside and p not in near0), default=None)
    if ho_t is None or dev_t is None or src_t is None or NEW_ID in ceil or NEW_ID in long_by_tab:
        return dict(passed=False, problem="no tablet for a canary case, or the synthetic id exists")

    def present(pid, extra=None):
        c2 = dict(ceil); c2[pid] = Counter(ceil.get(pid, {})); c2[pid][canary] += CANARY_N
        words, _, _, _ = ceil_build(c2, inside | near_copies(inside, long_by_tab, idx, extra))
        return canary in set(words)

    three = sorted(long_by_tab[ho_t])[:NEAR_LINES]
    got = dict(a_heldout_tablet=present(ho_t), b_development_tablet=present(dev_t),
               c_copy_sharing_3_lines=present(NEW_ID, {NEW_ID: set(three)}),
               d_copy_sharing_2_lines=present(NEW_ID, {NEW_ID: set(three[:NEAR_LINES - 1])}),
               e_ordinary_source_tablet=present(src_t))
    want = dict(a_heldout_tablet=False, b_development_tablet=False, c_copy_sharing_3_lines=False,
                d_copy_sharing_2_lines=True, e_ordinary_source_tablet=True)
    return dict(canary="".join(canary), count=CANARY_N, present=got, expected=want, passed=got == want)


# ------------------------------------------------------------------ texts and keys (parameterised copies)
def plant_parts(real, s, k, vm, base, voc, off=0):
    """Copy of the sealed plant_parts with the seed base and the vocabulary list as parameters; otherwise unchanged."""
    freq = Counter(x for _, t, _ in real for x in t)
    signs = sorted(freq)
    single = defaultdict(list); zero = []
    for x in signs:
        v = S.KEY[x]
        if len(v) == 1:
            single[v[0]].append(x)
        elif not v:
            zero.append(x)
    # PREREG-AMBIGUITY (bears on K0b): "a seeded order of that block's ceiling list" = the list sorted, then shuffled once with base + 100,000 + k, as sealed for W.
    words = sorted(voc); random.Random(base + 100000 + k).shuffle(words)
    nvoc = min(vm * s, len(words))
    sub = [(w, r + 1) for r, w in enumerate(words[:nvoc]) if all(single.get(c) for c in w)]
    assert sub, "no plant word can be spelled in this block"
    w_cum = list(np.cumsum([1 / r for _, r in sub])); sub_w = [w for w, _ in sub]
    z = sum(freq[x] for x in zero) / sum(freq.values())
    p0 = z / (1 - z)
    assert p0 <= 1, "zero-consonant share above 1/2: plant cannot match it"
    cum1 = {c: list(np.cumsum([freq[x] for x in ss])) for c, ss in single.items()}
    cum0 = list(np.cumsum([freq[x] for x in zero]))
    rs = random.Random(base + 200000 + 1000 * s + k + off)
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
    dev, _, ho, _ = S.halves(real)
    filler = S.unwrap(S.L.markov(S.wrap(dev + ho), random.Random(base + 300000 + 1000 * s + k + off)))
    ur = random.Random(base + 400000 + 1000 * s + k + off); us = [ur.random() for _ in dh]
    info = dict(vocabulary=nvoc, unspellable_left_out=nvoc - len(sub), zero_share=z, p_zero_follow=p0)
    return dh, filler, us, info


def scramble(order, s, d, base):
    """Copy of the sealed scramble (ladder `unigram`, seed base + 500,000 + 1,000 s + draw) with the base as parameter."""
    dev, dev_ids, ho, ho_ids = S.halves(order)
    sc = S.unwrap(S.L.unigram(S.wrap(dev + ho), random.Random(base + 500000 + 1000 * s + d)))
    return ([(i, t, True) for i, t in zip(dev_ids, sc[:len(dev)])]
            + [(i, t, False) for i, t in zip(ho_ids, sc[len(dev):])])


def n1_key(real, s, d, j, base):
    """Copy of the sealed shuffled key j of draw d (seed base + 600,000 + 1,000 s + 10 d + j), base as parameter."""
    freq = Counter(x for _, t, _ in real for x in t); kept = sorted(freq)
    true = {x: S.KEY[x] for x in kept}
    k = S.L.permute_in_class_bins(true, S.L.classes(kept, true), freq,
                                  random.Random(base + 600000 + 1000 * s + 10 * d + j))
    out = dict(S.KEY); out.update(k)
    return out


def make_text(tx, voc):
    """Copy of the sealed make_text. tx: kind real | plant, s, b, d (seed draw number: block + 1 for real text, k for
    plants), base, and for plants w (1.0 full dose, 0.0 pure order-1 filler) and vm; scr = unigram scramble."""
    s, b = tx["s"], tx["b"]
    real = S.block(s, b); info = {}
    cands = {x for _, t, _ in real for x in t}
    if tx["kind"] == "real":
        order = real
    else:
        dh, filler, us, info = plant_parts(real, s, tx["d"], tx["vm"], tx["base"], voc)
        w = tx["w"]
        order = dh if w >= 1 else S.dilute(dh, filler, us, w)
        info.update(w=w, replaced=sum(u >= w for u in us), n_chunks=len(us))
    if tx.get("scr"):
        order = scramble(order, s, tx["d"], tx["base"])
    return order, sorted(cands), real, info


# ------------------------------------------------------------------ workers
def init(payload, sealed_sha):
    global INIT_ERR
    try:
        a5_hook(); load_sealed_run(sealed_sha); S.setup(payload)
    except BaseException as e:                        # a raising initializer would respawn workers for ever
        INIT_ERR = repr(e)


def _ready():
    if INIT_ERR is not None:
        raise RuntimeError("worker init failed: " + INIT_ERR)


def run_jobs(fn, jobs):
    """Jobs go to at most NWORK (<= 4) worker processes; the pool is opened only after the A4 guard has passed."""
    global POOL
    if POOL is None:
        POOL = Pool(NWORK, initializer=init, initargs=(PAYLOAD, SEALED_SHA))
    return POOL.map(fn, jobs, chunksize=1)


def _words(a):
    """The job's word list (None = the primary Neo-Assyrian list), checked against the ledger's SHA-256."""
    if a.get("words") is None:
        return None
    words = [tuple(w) for w in a["words"]]
    assert list_sha(words) == a["sha"], "the job's word list is not the one in the ledger"
    return words


def job_gate(a):
    """Label-free clean counts of one sealed real draw (count gate, F4): the sealed job, called unchanged."""
    _ready()
    return S.job_gate(a)


def job_trigram(a):
    """F3: trigram-only Hit@1 on a K0b plant's held-out clean positions. No key, no lexicon, no gain."""
    _ready()
    order, cands, _, info = make_text(a["text"], _words(a))
    c = S.make_cell(order, cands, folds=False)
    r = S.ranks(c.ho, None, 0.0)
    return dict(k=a["text"]["d"], trigram_hit1=float(100 * np.mean(r == 1)) if len(r) else 0.0, n=len(r), plant=info)


def job_a6(a):
    """A6: the fitted K0b plant-1 model sums to 1 over all strings of each length 1 to 4 on 11 letters. No gain."""
    # PREREG-AMBIGUITY (A6 precedes K0b): the model = the block's ceiling list fitted on plant 1's whole development half under the true key, as sealed.
    _ready()
    words = _words(a)
    order, _, _, _ = make_text(a["text"], words)
    dev, _, _, _ = S.halves(order)
    m = S.fit_model(S.Lex(words), dev, S.KEY)
    sums = [math.fsum(m.fwd(x)[1] for x in product(S.ALPHA, repeat=n)) for n in (1, 2, 3, 4)]
    return dict(sums=sums, max_dev=max(abs(v - 1) for v in sums), p_sum=float(m.p.sum()), q_sum=math.fsum(m.q.values()))


def job_cells(a):
    """Copy of the sealed job_cells with the word list as a parameter. key kinds: true (true key, the list) | perm
    (true key, the list under sealed letter permutation j; after a true cell also the paired difference of bar C) |
    n1 (shuffled key j, the list). Returns aggregates only, Hit@1 included, and the job's wall time."""
    _ready()
    t0 = time.time(); tx = a["text"]; grid = tuple(a["grid"])
    words = _words(a)
    order, cands, real, info = make_text(tx, S.W47 if words is None else words)
    cell = S.make_cell(order, cands)
    out = dict(gid=a["gid"], part=a["part"], counts=cell.counts, cells=[], barC=[])
    if info:
        out["plant"] = info
    if words is None:
        lexf = S.get_lex
    else:
        memo = {}

        def lexf(j):
            if j not in memo:
                memo[j] = S.Lex(words if j == 0 else S.permuted(words, j))
            return memo[j]
    lp_true = None
    for kind, j in a["keys"]:
        if kind == "true":
            e, lp_true = S.evaluate(cell, S.KEY, lexf(0), grid)
        elif kind == "perm":
            e, lp = S.evaluate(cell, S.KEY, lexf(j), grid)
            if lp_true is not None:
                d = lp_true - lp; dm = float(d.mean()) if len(d) else 0.0
                se, _ = S.se_clustered(d, cell.ho_tab)
                out["barC"].append(dict(j=j, delta=dm, se_cl=se, L=S.bounds(dm, se)[0]))
        else:
            e, _ = S.evaluate(cell, n1_key(real, tx["s"], tx["d"], j, tx["base"]), lexf(0), grid)
        e.update(kind=kind, j=j); out["cells"].append(e)
    out["sec"] = time.time() - t0
    return out


# ------------------------------------------------------------------ jobs, rows, grading
def trio(gid, tx, grid, parts, words, sha):
    """Jobs for one text. A: true key + the 5 permuted copies. T: true key only. B: the 5 shuffled keys. C: the true
    key on the text's unigram scramble."""
    jobs = []
    for p in parts:
        if p == "A":
            keys = [("true", 0)] + [("perm", j) for j in range(1, S.NPERMLEX + 1)]
        elif p == "B":
            keys = [("n1", j) for j in range(1, S.N1_KEYS + 1)]
        else:
            keys = [("true", 0)]
        jobs.append(dict(gid=gid, part=p, text=dict(tx, scr=True) if p == "C" else tx, keys=keys, grid=grid,
                         words=words, sha=sha))
    return jobs


def real_tx(b):
    return dict(kind="real", s=1, b=b, d=b + 1, base=S.BASE)       # real text keeps the sealed base 20270201


def plant_tx(k, w, vm, base):
    # PREREG-AMBIGUITY (bears on K0b): plant and filler k sit on block k - 1 (blocks 0 to 4); "draw" in every seed is k.
    return dict(kind="plant", s=1, b=k - 1, d=k, w=w, vm=vm, base=base)


def gather(res):
    """Job results -> {gid: row}. A row holds the aggregates of every key scored on that text."""
    by = {}
    for r in res:
        row = by.setdefault(r["gid"], dict(counts={}, sec=0.0))
        row["sec"] += r["sec"]
        if "plant" in r:
            row["plant"] = r["plant"]
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


def third(cells):
    # PREREG-AMBIGUITY (bears on K0): "the median ... (the third largest of five)" = the third of the five G values in sorted order.
    assert len(cells) == 5
    return sorted(e["G"] for e in cells)[2]


def controls(row):
    """Control figures of one row: the permuted copies (max, median, bar C) and the shuffled keys (median, max)."""
    assert len(row["perm"]) == S.NPERMLEX and len(row["barC"]) == S.NPERMLEX and len(row["n1"]) == S.N1_KEYS
    row.update(perm_max_G=max(e["G"] for e in row["perm"]), perm_median_G=third(row["perm"]),
               n1_median_G=third(row["n1"]), n1_max_G=max(e["G"] for e in row["n1"]),
               n1_median_hit1_lift=statistics.median(e["hit1_lift"] for e in row["n1"]),
               barC_min_delta=min(c["delta"] for c in row["barC"]),
               ok_C=all(c["delta"] > 0 for c in row["barC"]))         # sealed bar C, point rule (1 u)
    row["perm_hit_P1"] = row["perm_max_G"] >= S.GAIN_BAR
    row["perm_hit_P2"] = row["perm_median_G"] >= S.GAIN_BAR
    return row


def rng(xs):
    xs = list(xs)
    return (min(xs), max(xs)) if xs else (None, None)


# ------------------------------------------------------------------ mode: kill (the whole study)
def kill(seal):
    path, lpath = HERE / "kill.json", HERE / "ledger.json"
    for p in (path, lpath):
        if p.exists():
            print(f"{p.name} exists: no rerun after any gain is seen (prereg Aborts). If its status shows a stop "
                  "before K0b, nothing was scored; that is for the coordinator to judge, not this script.", flush=True)
            sys.exit(1)
    # PREREG-AMBIGUITY: the sealed seal check (the certify_size_curve prereg, whose text governs data and scoring) must also hold; a miss exits 2.
    sc = S.seal_check()
    if not sc["sealed"] or sc["code_sha256"] != seal["sealed_code_sha256"]:
        print("SEAL: the certify_size_curve prereg or code on disk is not the sealed one", flush=True); sys.exit(2)
    # PREREG-AMBIGUITY: A4 ("do not start") exits 1 as a planned stop and writes nothing, so a later start is not refused.
    why, fm = S.a4()
    if why:
        print("A4: do not start:", "; ".join(why), "(nothing computed, nothing written)", flush=True); sys.exit(1)
    t0 = time.time()                                  # PREREG-AMBIGUITY (FT): the clock starts here, when the run starts.
    mine = sha256_of(Path(__file__).resolve())
    listed = any(len(p) >= 2 and p[0] == mine and p[1] == "experiments/lexicon_ceiling/run.py"
                 for p in (ln.split() for ln in open(HASHES, encoding="utf-8")))
    out = dict(prereg=PREREG, mode="kill", status="running", nwork=NWORK, base_new=BASE_NEW, base_sealed=S.BASE,
               sealed=True, code_sha256=mine, code_hash_in_HASHES=listed, certify_prereg_sha256=sc["prereg_sha256"],
               note_2027=NOTE_2027, indus=X_INDUS, A4=dict(free_mem_frac=fm, failures=why), **seal)
    out["fallbacks"] = {}; fb = out["fallbacks"]
    S.dump(out, path)

    # ---- A7 (sign list, primary skeleton file; the sealed code file was checked before it was executed)
    out["A7"] = dict(S.a7(), sealed_code=True)
    if not out["A7"]["passed"]:
        stop(out, path, "A7: ogsl.zip or neoass_skeletons.tsv does not match its SHA-256")

    # ---- the sealed label-free corpus build (with the ceiling word counts) and A9
    global PAYLOAD
    payload, stats, a9 = S.build_corpus(True)
    S.setup(payload)
    PAYLOAD = dict(payload, ceil=None)                # workers get word lists inside their jobs, never the source
    ceil = S.CEIL
    out["A9"] = dict(problems=a9, passed=not a9); out["corpus"] = stats
    if a9:
        stop(out, path, "A9: " + "; ".join(a9))

    # ---- A2, part 1: the Measured numbers that need no draw
    # PREREG-AMBIGUITY (A2, so whether K0 starts): the stop list is A2's own (the 3,951 tablets counted as a pool T figure); other Measured numbers are recorded with a match flag.
    pT = stats["pool_T"]
    pool_types = {sk for c in ceil.values() for sk in c}
    types = {n: sum(len(sk) == n for sk in pool_types) for n in range(S.LMIN, S.MAXW + 1)}
    bad = [f"pool T {k} {pT[k]} != {v}" for k, v in S.A2_POOL.items() if pT[k] != v]
    if pT["tablets"] != A2_TABLETS:
        bad.append(f"pool T tablets with a chunk {pT['tablets']} != {A2_TABLETS}")
    if types != A2_TYPES:
        bad.append(f"whole-pool skeleton types {types} != {A2_TYPES}")
    if len(ceil) != A2_WORD_TABLETS:
        bad.append(f"tablets with a usable word {len(ceil)} != {A2_WORD_TABLETS}")
    if stats["blocks"][1] < NDRAW:
        bad.append(f"only {stats['blocks'][1]} blocks at 1 u")
    out["A2"] = dict(part1_problems=bad, types_whole_pool=types, tablets_with_a_word=len(ceil),
                     word_tokens=sum(sum(c.values()) for c in ceil.values()))
    if bad:
        stop(out, path, "A2: recomputed counts differ: " + "; ".join(bad) + ". Stop and redraft.")

    # ---- raw rows, long lines, the per-draw lists and their verification (all label-free)
    rows, q_ids, v2s = read_rows()
    rows_ok = len(rows) == pT["lines"] and tab_counters(rows, v2s) == ceil
    long_by_tab, idx = defaultdict(set), defaultdict(set)
    for pid, content, nsig in rows:
        if nsig >= NEAR_SIGNS:
            k = line_key(content); long_by_tab[pid].add(k); idx[k].add(pid)
    lists, shas, ledger, v1_bad, v2_bad, a8_bad, a9_bad = [], [], [], [], [], [], []
    for b in range(NDRAW):
        inside = block_ids(b); near = near_copies(inside, long_by_tab, idx); drop = inside | near
        words, info, src, prov = ceil_build(ceil, drop)
        sha = list_sha(words)
        # A8: with an empty near-copy set the copied builder must equal the sealed one
        w1 = ceil_build(ceil, inside)[0]
        if w1 != S.ceiling_lex(1, b)[0]:
            a8_bad.append(b + 1)
        # V1: provenance
        if set().union(*prov.values()) & drop or src & drop:
            v1_bad.append(b + 1)
        # V2: a second build by deletion (rows of the block and of the near-copies removed before any word is read)
        # PREREG-AMBIGUITY (A8): the rows are the kept pool T lines held in memory; they are filtered by id first and only then tokenised into words.
        w2 = ceil_build(tab_counters([r for r in rows if r[0] not in drop], v2s), set())[0]
        sha2 = list_sha(w2)
        if sha2 != sha or len(w2) != len(words):
            v2_bad.append(b + 1)
        if src & q_ids:
            a9_bad.append(b + 1)
        lists.append(words); shas.append(sha)
        ledger.append(dict(draw=b + 1, block_tablets=len(inside), heldout_tablets=sum(S.held(t) for t in inside),
                           near_copy_tablets=len(near), near_copy_tablets_with_a_word=len(near & set(ceil)),
                           source_tablets=info["source_tablets"], source_word_tokens=info["source_word_tokens"],
                           list_sha256=sha, list_sha256_second_build=sha2, list_words=info["words"],
                           shortfall_by_length=info["shortfall_by_length"], types_available=info["types_available"],
                           one_tablet_words_by_length=info["one_tablet_words_by_length"],
                           last_ranked_tablets=info["last_ranked_tablets"],
                           words_changed_by_exclusion_2=len(set(words) - set(w1))))
    v3 = canaries(ceil, long_by_tab, idx, pool_types)
    # PREREG-AMBIGUITY (leak dial, record-only): "no exclusion at all" gives one whole-pool list, size-matched as the others and shared by the 20 draws.
    leak_words, leak_info, _, _ = ceil_build(ceil, set())
    leak_sha = list_sha(leak_words)

    # ---- A2, part 2 + F4: clean counts of the 20 sealed draws, near-copy counts, shortfall (FS), list size
    g = run_jobs(job_gate, [(1, b, "T") for b in range(NDRAW)])
    clean = [r["clean_positions"] for r in g]; thin = [r["b"] + 1 for r in g if r["thin"]]
    agree = all(r.get("clean_index_agrees", True) for r in g)
    near_counts = [d["near_copy_tablets"] for d in ledger]
    short = [d["draw"] for d in ledger if any(d["shortfall_by_length"].values())]
    wrong_size = [d["draw"] for d in ledger if d["list_words"] != A2_LIST]
    got = dict(word_tokens=out["A2"]["word_tokens"],
               lines_on_two_or_more_tablets=sum(len(v) >= 2 for v in idx.values()),
               tablets_in_draw=[min(r["tablets"] for r in g), max(r["tablets"] for r in g),
                                statistics.median(r["tablets"] for r in g)],
               source_tablets=list(rng(d["source_tablets"] for d in ledger)),
               source_word_tokens=list(rng(d["source_word_tokens"] for d in ledger)),
               types_outside_min={n: min(d["types_available"][n] for d in ledger) for n in A2_TYPES},
               words_changed_by_exclusion_2=list(rng(d["words_changed_by_exclusion_2"] for d in ledger)),
               clean_median=statistics.median(clean), clean_draw_16=clean[15])
    out["A2"].update(near_copy_counts=near_counts, near_copy_counts_expected=A2_NEAR, shortfall_draws=short,
                     list_size_wrong_draws=wrong_size, clean=clean, thin_draws=thin, clean_index_agrees=agree,
                     measured=got, measured_prereg=MEASURED, measured_matches={k: got[k] == MEASURED[k] for k in got})
    fb["F4"] = dict(thin_draws_flagged=thin, rule="kept and flagged")
    fb["FS"] = dict(shortfall_draws=short, applied=bool(short))

    # ---- V4: the ledger, on disk before any gain
    ver = dict(V1=dict(draws_failed=v1_bad, passed=not v1_bad), V2=dict(draws_failed=v2_bad, passed=not v2_bad and rows_ok,
                                                                        rows_reproduce_sealed_counts=rows_ok),
               V3=v3, A8_builder_equals_sealed=dict(draws_failed=a8_bad, passed=not a8_bad),
               A9_set_Q_in_source=dict(draws_failed=a9_bad, passed=not a9_bad))
    S.dump(dict(prereg=PREREG, what="V4 ledger: written before any gain of this study is computed",
                written_unix=time.time(), near_copy_rule=dict(lines=NEAR_LINES, signs=NEAR_SIGNS),
                size_target=S.W_BY_LEN, verification=ver, draws=ledger,
                leak_dial_list=dict(list_sha256=leak_sha, **leak_info), **seal), lpath)
    out["verification"] = ver; out["ledger_file"] = "ledger.json"
    S.dump(out, path)
    S.say("A7 A9 A2 ledger", near_copies=near_counts, thin_draws=thin, clean_median=got["clean_median"],
          V1=ver["V1"]["passed"], V2=ver["V2"]["passed"], V3=v3["passed"], A8=not a8_bad)
    bad = []
    if near_counts != A2_NEAR:
        bad.append("near-copy counts differ from the prereg's")
    if short:
        bad.append(f"shortfall in draws {short} (FS)")
    if wrong_size:
        bad.append(f"list is not 2,815 words in draws {wrong_size}")
    if not agree:
        bad.append("the hashed clean-rule index disagrees with the sealed pairwise rule")
    out["A2"]["passed"] = not bad
    if bad:
        stop(out, path, "A2: " + "; ".join(bad) + ". Stop and redraft.")
    bad = [k for k in ("V1", "V2", "V3", "A8_builder_equals_sealed") if not ver[k]["passed"]]
    if bad:
        stop(out, path, "A8: verification failed: " + ", ".join(bad))
    if a9_bad:
        stop(out, path, f"A9: a set Q tablet is in the ceiling source of draws {a9_bad}")

    # ---- A1: two sealed Old Assyrian gains through the copied functions, to 1e-9
    # PREREG-AMBIGUITY (A1 precedes K0b): draw 4's sealed gain = K3_record_only, 1 u, draw 4, true key in the sealed kill.json; both cells use the sealed grid, base and 500-word rule.
    ref = json.load(open(SEALED_KILL))
    ref4 = [r for r in ref["K3_record_only"]["1"]["draws"] if r["draw"] == A1_DRAW][0]["true"]
    grid = tuple(float(x) for x in ref["license"]["grid"]); assert grid == S.GRID0
    a1 = gather(run_jobs(job_cells, trio("a1:plant", plant_tx(1, 1.0, S.VOC, S.BASE), grid, "T", None, None)
                         + trio("a1:real", real_tx(A1_DRAW - 1), grid, "T", None, None)))
    gp, gr = a1["a1:plant"]["true"], a1["a1:real"]["true"]
    out["A1"] = dict(plant1=dict(G=gp["G"], sealed_G=A1_PLANT_G, diff=abs(gp["G"] - A1_PLANT_G), n=gp["n"], lam=gp["lam"],
                                 hit1_B=gp["hit1_B"], hit1_S=gp["hit1_S"], hit1_lift=gp["hit1_lift"]),
                     real_draw4=dict(G=gr["G"], sealed_G=ref4["G"], diff=abs(gr["G"] - ref4["G"]), n=gr["n"],
                                     sealed_n=ref4["n"], lam=gr["lam"], sealed_lam=ref4["lam"],
                                     hit1_B=gr["hit1_B"], hit1_S=gr["hit1_S"], hit1_lift=gr["hit1_lift"]))
    out["A1"]["passed"] = out["A1"]["plant1"]["diff"] <= S.A1_TOL and out["A1"]["real_draw4"]["diff"] <= S.A1_TOL
    S.dump(out, path)
    if not out["A1"]["passed"]:
        stop(out, path, "A1: the copied functions do not reproduce the sealed plant-1 or draw-4 gain to 1e-9")

    # ---- F3: trigram-only Hit@1 on the five K0b plants, before any K0b gain
    vm = S.VOC
    ptx = lambda k: plant_tx(k, 1.0, vm, BASE_NEW)
    tri = lambda: run_jobs(job_trigram, [dict(text=ptx(k), words=lists[k - 1], sha=shas[k - 1])
                                         for k in range(1, NPLANT + 1)])
    f3 = tri(); f3_hit = any(r["trigram_hit1"] > S.F3_MAX for r in f3)
    fb["F3"] = dict(check=f3, applied=f3_hit)
    if f3_hit:
        vm = S.VOC_F3                                 # once: the plant vocabulary becomes 2,000 words
        fb["F3"]["after"] = tri()

    # ---- A6: the fitted K0b plant-1 window model sums to 1; sees no gain
    a6 = run_jobs(job_a6, [dict(text=ptx(1), words=lists[0], sha=shas[0])])[0]
    out["A6"] = dict(a6, passed=a6["max_dev"] <= S.A6_TOL)
    S.dump(out, path)
    if not out["A6"]["passed"]:
        stop(out, path, "A6: the window model does not sum to 1 (to 1e-9) over strings of 1 to 4 consonants")
    S.say("A1 F3 A6", a1_diff=[out["A1"]["plant1"]["diff"], out["A1"]["real_draw4"]["diff"]],
          trigram_hit1=[round(r["trigram_hit1"], 1) for r in f3], f3_applied=f3_hit, a6_max_dev=a6["max_dev"])

    # ---- K0b: five full-dose plants from the ceiling list; true key, 5 permuted copies, 5 shuffled keys, scramble
    grid = S.GRID0
    by = gather(run_jobs(job_cells, [j for k in range(1, NPLANT + 1)
                                     for j in trio(f"k0b:{k}", ptx(k), grid, "ABC", lists[k - 1], shas[k - 1])]))
    prow = []
    for k in range(1, NPLANT + 1):
        r = controls(by[f"k0b:{k}"])
        r.update(k=k, block=k - 1, ok_true=r["true"]["G"] >= S.K0_GAIN,
                 ok_scramble=r["scramble_true"]["G"] <= S.CTRL_BAR, ok_n1=r["n1_median_G"] <= S.CTRL_BAR)
        prow.append(r)
    bars = dict(true_ok=S.count(prow, "ok_true"), scramble_ok=S.count(prow, "ok_scramble"),
                n1_ok=S.count(prow, "ok_n1"), needed=NPLANT)
    missed = [nm for q, nm in (("true_ok", "true key G below 0.10"), ("scramble_ok", "scramble G above 0.005"),
                               ("n1_ok", "shuffled keys' median G above 0.005")) if bars[q] < NPLANT]
    # FC: the control rule, set on the plants before any real-text gain
    p1, p2 = S.count(prow, "perm_hit_P1"), S.count(prow, "perm_hit_P2")
    rule = "P1" if p1 <= FC_MAX else ("P2" if p2 <= FC_MAX else None)
    fb["FC"] = dict(plants_flagged_P1=p1, plants_flagged_P2=p2, rule_in_force=rule, usable=rule is not None,
                    perm_G=[S.r4(e["G"] for e in r["perm"]) for r in prow])
    out["K0b"] = dict(grid=grid, vocabulary_multiplier=vm, plants=prow, bars=bars, bars_missed=missed, passed=not missed)
    S.say("K0b", passed=not missed, **S.brief(prow), scramble_G=S.r4(r["scramble_true"]["G"] for r in prow),
          n1_median_G=S.r4(r["n1_median_G"] for r in prow), perm_max_G=S.r4(r["perm_max_G"] for r in prow),
          perm_median_G=S.r4(r["perm_median_G"] for r in prow), FC_rule=rule, P1_plants=p1, P2_plants=p2)
    # PREREG-AMBIGUITY (bears on K0): the K0b bars are read before FC, so a plant miss gives reading 0b even where FC would also stop.
    if missed:
        txt = R0B.format(bars="; ".join(missed))
        stop(out, path, "K0b reading 0b. " + txt + " No real-text cell runs.", "0b", txt)
    if rule is None:
        stop(out, path, "A3 (FC), reading 0c. " + R0C + " No real-text cell runs.", "0c", R0C)
    # F1: grid edge, decided on the K0b plants; K0b is not regraded
    n4 = sum(r["true"]["lam"] == 4.0 for r in prow)
    fb["F1"] = dict(true_lam4_plants=n4, applied=n4 >= 3)
    # PREREG-AMBIGUITY (bears on K0a): after F1 the values 8 and 16 serve every key in every cell computed after K0b.
    if n4 >= 3:
        grid = S.GRID0 + S.GRID_F1
    S.dump(out, path)

    # ---- K0a: the 20 sealed 1 u draws; true key and 5 permuted copies, then the 5 shuffled keys (graded, always run)
    by = gather(run_jobs(job_cells, [j for b in range(NDRAW)
                                     for j in trio(f"k0a:{b}", real_tx(b), grid, "AB", lists[b], shas[b])]))
    rows_a = []
    for b in range(NDRAW):
        r = controls(by[f"k0a:{b}"])
        r.update(draw=b + 1, thin=r["counts"]["text"]["thin"], hit_T=r["true"]["G"] >= S.GAIN_BAR,
                 hit_S=r["n1_median_G"] >= S.GAIN_BAR)
        rows_a.append(r)
    T = S.count(rows_a, "hit_T"); P1 = S.count(rows_a, "perm_hit_P1"); P2 = S.count(rows_a, "perm_hit_P2")
    Sn = S.count(rows_a, "hit_S"); C = S.count(rows_a, "ok_C")
    P = P1 if rule == "P1" else P2; other = P2 if rule == "P1" else P1
    lift = [r["true"]["hit1_lift"] for r in rows_a]; dose = [r["true"]["D"] for r in rows_a]
    med_G = statistics.median(r["true"]["G"] for r in rows_a)
    out["K0a"] = dict(grid=grid, draws=rows_a, T=T, P=P, P1=P1, P2=P2, S=Sn, C=C, rule_in_force=rule,
                      median_G=med_G, G=[r["true"]["G"] for r in rows_a], hit1_lift=lift,
                      hit1_B=[r["true"]["hit1_B"] for r in rows_a], hit1_S=[r["true"]["hit1_S"] for r in rows_a],
                      D=dose, thin_draws=[r["draw"] for r in rows_a if r["thin"]])
    S.dump(out, path)
    S.say("K0a", T=T, P1=P1, P2=P2, S=Sn, C=C, rule=rule, **S.brief(rows_a),
          perm_max_G=S.r4(r["perm_max_G"] for r in rows_a), n1_median_G=S.r4(r["n1_median_G"] for r in rows_a))

    # ---- record-only cells, in the listed order, each started only inside the FT clock
    # PREREG-AMBIGUITY (FT): a "cell" is one row of the record-only list; the clock is read once before each, the counts row included.
    rec = {}; fb["FT"] = dict(limit_hours=FT_SEC / 3600, elapsed_hours_at_start={}, not_started=[])

    def may(name):
        el = time.time() - t0
        fb["FT"]["elapsed_hours_at_start"][name] = round(el / 3600, 3)
        if el > FT_SEC:
            fb["FT"]["not_started"].append(name)
        return el <= FT_SEC

    if may("scramble"):
        by = gather(run_jobs(job_cells, [j for b in range(NDRAW)
                                         for j in trio(f"scr:{b}", real_tx(b), grid, "C", lists[b], shas[b])]))
        cells = [dict(draw=b + 1, counts=by[f"scr:{b}"]["counts"]["scramble"], **by[f"scr:{b}"]["scramble_true"])
                 for b in range(NDRAW)]
        rec["scramble"] = dict(draws=cells, reached_bar=sum(e["G"] >= S.GAIN_BAR for e in cells), graded=False)
        S.dump(out | dict(record_only=rec), path)
        S.say("scramble record-only", G=S.r4(e["G"] for e in cells), hit1_lift=[round(e["hit1_lift"], 2) for e in cells])
    if may("leak_dial"):
        by = gather(run_jobs(job_cells, [j for b in range(NDRAW)
                                         for j in trio(f"leak:{b}", real_tx(b), grid, "T", leak_words, leak_sha)]))
        cells = [dict(draw=b + 1, **by[f"leak:{b}"]["true"]) for b in range(NDRAW)]
        rec["leak_dial"] = dict(draws=cells, median_G=statistics.median(e["G"] for e in cells),
                                median_G_with_exclusions=med_G, list_sha256=leak_sha, graded=False,
                                note="a deliberate leak; never a result")
        S.dump(out | dict(record_only=rec), path)
        S.say("leak dial record-only", G=S.r4(e["G"] for e in cells), hit1_lift=[round(e["hit1_lift"], 2) for e in cells])
    if may("filler"):
        by = gather(run_jobs(job_cells, [j for k in range(1, NFILL + 1)
                                         for j in trio(f"fill:{k}", plant_tx(k, 0.0, vm, BASE_NEW), grid, "T",
                                                       lists[k - 1], shas[k - 1])]))
        cells = [dict(k=k, block=k - 1, plant=by[f"fill:{k}"]["plant"], **by[f"fill:{k}"]["true"])
                 for k in range(1, NFILL + 1)]
        rec["filler"] = dict(texts=cells, graded=False)
        S.dump(out | dict(record_only=rec), path)
        S.say("filler record-only", G=S.r4(e["G"] for e in cells), hit1_lift=[round(e["hit1_lift"], 2) for e in cells])
    if may("counts"):
        # PREREG-AMBIGUITY (record-only): held-out word tokens = all sealed-rule words of the draw's held-out tablets; the sentence's share pools the 20 draws.
        prim = set(S.W47); per, tot = [], Counter()
        for b in range(NDRAW):
            cs = set(lists[b]); tk = Counter()
            for tid in block_ids(b):
                if S.held(tid):
                    tk.update(ceil.get(tid, {}))
            n = sum(tk.values()); nc = sum(v for sk, v in tk.items() if sk in cs)
            nn = sum(v for sk, v in tk.items() if sk in prim)
            tot.update(tokens=n, in_ceiling=nc, in_neo_assyrian=nn)
            per.append(dict(draw=b + 1, heldout_word_tokens=n, share_in_ceiling=nc / n if n else None,
                            share_in_neo_assyrian=nn / n if n else None,
                            list_share_also_neo_assyrian={m: sum(len(w) == m and w in prim for w in cs)
                                                          / max(1, sum(len(w) == m for w in cs))
                                                          for m in range(S.LMIN, S.MAXW + 1)}))
        rec["counts"] = dict(draws=per, pooled_share_in_ceiling=tot["in_ceiling"] / tot["tokens"] if tot["tokens"] else None,
                             pooled_share_in_neo_assyrian=tot["in_neo_assyrian"] / tot["tokens"] if tot["tokens"] else None,
                             heldout_word_tokens=tot["tokens"], label_free=True)
    out["record_only"] = rec

    # ---- the reading: the first of 1, 2, 3, 4 whose condition holds (0a, 0b, 0c stopped above)
    # PREREG-AMBIGUITY (reading text): "P" in readings 2 and 4 is P under the rule in force; both counts are in the added sentence.
    if T >= PASS_T:
        if P <= CTRL_MAX and Sn <= CTRL_MAX and (rule == "P1" or C >= C_MIN):
            code, txt = "1", R1
        else:
            code, txt = "2", R2.format(T=T, P=P, S=Sn, C=C)
    elif T <= FAIL_T:
        code, txt = "3", R3
    else:
        code, txt = "4", R4.format(T=T)
        if P > CTRL_MAX or Sn > CTRL_MAX:
            txt += " " + R4_CTRL.format(P=P, S=Sn)
    # PREREG-AMBIGUITY (reading text): the prereg words an FT cut for the scramble only; a cut leak, filler or counts row gets the same "did not run (FT)" form.
    add = [X_GATE.format(lo=min(lift), hi=max(lift), med=statistics.median(lift)),
           X_RULE.format(rule=rule, other=other, C=C, S=Sn),
           X_SCR.format(n=rec["scramble"]["reached_bar"]) if "scramble" in rec else X_SCR_FT,
           X_LEAK.format(leak=rec["leak_dial"]["median_G"], clean=med_G) if "leak_dial" in rec
           else "The leak dial did not run (FT).",
           X_DOSE.format(lo=min(dose), hi=max(dose)),
           X_FILL.format(vals=", ".join(f"{e['G']:.4f}" for e in rec["filler"]["texts"])) if "filler" in rec
           else "The filler cell did not run (FT).",
           X_COV.format(c=rec["counts"]["pooled_share_in_ceiling"], n=rec["counts"]["pooled_share_in_neo_assyrian"])
           if "counts" in rec and rec["counts"]["heldout_word_tokens"] else "The coverage count did not run (FT).",
           X_ONE, X_CSC, X_INDUS]
    out.update(reading_code=code, reading=txt, reading_added=add, reading_full=txt + " " + " ".join(add),
               status="done", seconds=round(time.time() - t0, 1))
    S.dump(out, path)
    print(f"Reading {code}. " + out["reading_full"], flush=True)
    POOL.close(); POOL.join()


if __name__ == "__main__":
    seal, bad = seal_check()                          # before anything else
    if bad:
        print("SEAL: do not start: " + "; ".join(bad), flush=True); sys.exit(2)
    if sys.argv[1:] != ["kill"]:
        print("usage: run.py kill   (once, under board/run.sh; stdout is the study's kill.out)", flush=True); sys.exit(2)
    # PREREG-AMBIGUITY: kill.out is this run's redirected stdout, as in the sealed study; the script itself writes kill.json and ledger.json.
    a5_hook(); load_sealed_run(seal["sealed_code_sha256"])
    kill(seal)
