"""Anchor cross-read rehearsal on Ur III sealed tablets (prereg docs/prereg/anchor_crossread.md, SEALED v4, tag
`anchor_crossread`).
Run (from the repo root, under the Indus compute lock; A4 checks the lock and the 20% free-memory guard):
  board/run.sh .venv/bin/python -I experiments/anchor_crossread/run.py recount  # optional: A2 + A1 only, no T
  board/run.sh .venv/bin/python -I experiments/anchor_crossread/run.py kill     # A2, A1, F2, Kp, Kc, K0 (+Kk, F1)
  board/run.sh .venv/bin/python -I experiments/anchor_crossread/run.py ladder   # cell P, all arms, rungs 12, 10 .. 3
  board/run.sh .venv/bin/python -I experiments/anchor_crossread/run.py cells    # R1, C1, R2, R3, C2, X20; readings
Workers: env NWORK (default 4, capped at 4).

Order (the prereg's "Checks, in this order"):
  kill:   A4 + seal check; A2 (OGSL hash); A1 (label-free recount of the pools and the gate tables, no T); F2 (cost,
          on synthetic sets, before any real pair); Kp (planted, >= 19 of 20) -> reading 1 stops; Kc (<= 1 of 20) ->
          reading 1 stops; K0 = rung 15 of cell P in arm B2 (K0a NEG <= 1 of 20, K0b POS >= 16 of 20); Kk only if K0a
          fails (reading 2, F4); F1: if B2 fails K0 the same K0 runs for B1, then for A.
  ladder: refuses unless kill.json is done. Rung 15 for the arms K0 did not reach, then 12, 10 and down to 3, every
          arm, POS and NEG (and NEG0 for an arm under F4). Claimed m per arm, the claiming arm, the value bar.
  cells:  refuses unless ladder.json is done. With a claiming arm: R1, C1 (binding), R2, R3, C2 at every rung, then
          X20 (record only). With no claiming arm: X20 in B2 only, and reading 7b.
Each mode refuses to start if its own output exists. Outputs are per-set aggregates only (T, b, pass, counts of
confirmed values); no alignment, no placement and no value is written.

No Indus step: arm C reads the sign sequence and the object type of data/m77_texts.jsonl and nothing else. The code
that gives a sound an M77 sign type is random, seeded and never written out. No key file is opened (A5 is enforced by
an audit hook on file opens), no Indus text is read, no key is scored.

Reference code: the lock, memory guard and seal check are copied from experiments/certify_size_curve/run.py; the pool
build follows the drafter's scratch count scripts (the prereg's tables came from them). The prereg wins where they
differ. Every judgement call is marked PREREG-AMBIGUITY. Nothing is loaded or computed at import.
"""
import csv, hashlib, json, os, random, re, statistics, subprocess, sys, time, zipfile
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PREREG = "docs/prereg/anchor_crossread.md"; TAG = "anchor_crossread"
NWORK = max(1, min(4, int(os.environ.get("NWORK", "4"))))
MEM_GUARD = 0.20
LOCK = ROOT / "board/compute.lock"
RAW = ROOT / "experiments/short_labels/raw/cdli"
OGSL = HERE / "raw/ogsl/ogsl.zip"
OGSL_SHA = "46d8a29c11c351baa922c912c4472d6fb7ec7f79e76d4d473f29d58d4caf860f"
M77 = ROOT / "data/m77_texts.jsonl"
SEED_PREFIX = "anchor_crossread/v3"                   # the prereg's seed string says v3; kept as written
LAM = 0.25                                            # penalty weight (sealed)
RESTARTS = 6; SWEEPS = 20
NPERM = 999; PASSB = 9                                # (1 + b) / 1000 <= 0.01  <=>  b <= 9; stop once b reaches 10
F2_NPERM = 199; F2_PASSB = 1; F2_HOURS = 6.0
TRIES = 10000                                         # rejection cap per restricted re-pairing
ARMS = ("B2", "B1", "A")
RUNGS = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3)             # 15 first, then 12, 10 and down to 3
CITIES = ("Umma", "Girsu")
MISM = ("NEG", "NEG0", "MIS", "OUT")                  # pools read against the mismatch bar
MISMATCH_BAR = 1; POWER_BAR = 16; EDGE = (13, 15); KP_BAR = 19; VALUE_BAR = 0.90
R1_P = 0.20; R2_P = 0.25
W = None                                              # worker state (pools), set by setup()
POOL = None; PAYLOAD = None; INIT_ERR = None
_PART = {}

R_INDUS = ("Rehearsal on Ur III sealed tablets. No Indus key is scored, no Indus text is read, and no outcome "
           "supports or counts against any Indus reading. The Ur III result is an upper bound on power.")
R1_TXT = "Reading 1: {what} failed. A bug. Stop. Nothing else is computed. Fix, state the fix, reseal the code."
R2A = ("Reading 2a ({arm}): mismatched Ur III tablets are not unrelated pairs. The sealer's name shares signs with "
       "the legend of the seal he used (Umma 51% against 32%), and the test picks that up. Under F4 the arm goes on "
       "with NEG0; any claim is worded 'the names are tied to these legends', and only the value bar can add 'and "
       "spelled in them'.")
R2B = ("Reading 2b ({arm}): with no shared sign at all, real mismatches still pass under this arm's freedom. The arm "
       "cannot claim.")
R3_TXT = ("Reading 3: a span-free cross-read test separates true from false pairs. The rule's m is the largest of the "
          "three: {m}.")
R4_TXT = ("Reading 4: the test works on clean Ur III legends only. At the reading gate's floor, or at Indus sign "
          "statistics, 15 pairs are not enough. Section 4 stays. The minimum event is restated as more than 15 pairs.")
R4A = "Reading 4a: unread signs raise the false-pass rate. R1 has no claimed m."
R4B = ("Reading 4b: C1 missed the mismatch bar, which passes by construction. A bug in arm C; arm C is void until "
       "the code is fixed and resealed. P and R1 stand.")
R5_TXT = "Reading 5: B2 has no claim and B1 claims. The legend's reading direction must be known from outside the set."
R6_TXT = ("Reading 6: cross-reading needs an independent reason to locate the name span. The name opens 91.0% of Ur "
          "III legends, so position is nearly free there and may not be on an Indus object.")
R7B = ("Reading 7b: the route is closed at 15 pairs or fewer on this statistic. Section 4 of anchor_objects.md stays "
       "as it is. Reopen with a set of more than 15 pairs or a new statistic under a new prereg.")
R8_TXT = ("Reading 8: a passing set shows the pairing is real. It does not certify single values. The rule may count "
          "the set, never a value.")


# ------------------------------------------------------------------ A5: only the files the prereg names
_A5_ALLOW = ("experiments/short_labels/raw/cdli/", "board/compute.lock/", ".venv/", "data/m77_texts.jsonl", PREREG,
             "docs/prereg/HASHES.txt", "experiments/anchor_crossread/raw/ogsl/ogsl.zip",
             "experiments/anchor_crossread/run.py")
_A5_OUT = re.compile(r"^experiments/anchor_crossread/(?:recount|kill|ladder|cells)\.json(?:\.tmp)?$")
_A5_ON = False


def a5_hook():
    """A5: inside the repo only the files this study needs may be opened. Any other repo file (any Indus key file,
    anything under experiments/certify_size_curve/) raises before it is read."""
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
        if not (_A5_OUT.match(rel) or any(rel == a or (a.endswith("/") and rel.startswith(a)) for a in _A5_ALLOW)):
            raise RuntimeError("A5: the study tried to open a repo file outside its data list: " + rel)

    sys.addaudithook(hook)


# ------------------------------------------------------------------ guard (copied from certify_size_curve)
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
    # PREREG-AMBIGUITY: this prereg names no memory figure; the 20% guard and its reading of "free" are copied from
    # certify_size_curve: macOS vm_stat free + inactive + speculative pages over hw.memsize.
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
    # PREREG-AMBIGUITY: not a prereg abort (as certify_size_curve). Before anything is computed the run checks that
    # the prereg file on disk is the sealed one (its sha256 is on a HASHES.txt line with tag anchor_crossread).
    h = sha256_of(ROOT / PREREG); ok = False
    for line in open(ROOT / "docs/prereg/HASHES.txt"):
        f = line.split()
        if len(f) >= 4 and f[0] == h and f[1] == PREREG and f[-1] == TAG:
            ok = True
    return dict(prereg_sha256=h, sealed=ok, code_sha256=sha256_of(Path(__file__).resolve()))


def dump(obj, path):
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, separators=(",", ":")); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def stop(out, path, msg, code=1):
    out.update(stop=msg, status="stopped"); out["license"] = dict(next=False)
    dump(out, path); print("STOP:", msg, flush=True); sys.exit(code)


def say(name, **kw):
    print(name + ": " + json.dumps(kw), flush=True)


# ------------------------------------------------------------------ seeds (prereg Seeds; no global random state)
def rng_for(ctx, purpose):
    """ctx = (cell, arm, pool, m, city, set). The stream is seeded from the first 8 bytes of SHA-256 of the string."""
    # PREREG-AMBIGUITY: the 8 bytes are read as a big-endian integer.
    s = SEED_PREFIX + "/" + "/".join(str(x) for x in ctx) + "/" + purpose
    return random.Random(int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big"))


# ------------------------------------------------------------------ pools (label-free; as the scratch count scripts)
SUBD = str.maketrans("₀₁₂₃₄₅₆₇₈₉ₓ", "0123456789x")
NUMLINE = re.compile(r"^\d+[\'a-z]*\.\s+(.*)$")
STOPSET = {"asz-a", "dub-sar", "sanga", "szabra", "ugula", "sukkal-mah", "nig2-dab5", "didli-a", "bala-a", "im-sar-a",
           "ugu2-a", "esz-am3", "dab-ba"}
STOPPRE = ("ensi2", "nam-sza3-", "sza13-dub-ba")
STOPSUF = ("-e-ne", "-ta", "-sze3")


def asc(v):
    v = v.translate(SUBD).lower()
    for a, b in (("š", "sz"), ("ṣ", "s,"), ("ṭ", "t,"), ("ḫ", "h"), ("ŋ", "g"), ("ʾ", "'")):
        v = v.replace(a, b)
    return v


def clean1(tok):
    return re.sub(r"[#?!*<>\[\]]", "", tok)


def clean(tok):
    return re.sub(r"[#?!*<>\[\]_]", "", tok)


def load_cdli():
    """-> (provenience by P-number, texts: P-number -> (body lines, [legend line lists])), Ur III only."""
    # PREREG-AMBIGUITY: the task names ur3_legend_refute's loader as the reference, but the prereg's tables (and
    # abort A1's exact counts) were made with the drafter's count1.py, whose line pattern and section rule differ
    # slightly. This is count1.py's loader: an @seal section ends at the next @-line other than @column, and a
    # P-number that occurs twice in the dump keeps its later text at its first place in dump order.
    csv.field_size_limit(10 ** 9)
    per = {}
    with open(RAW / "cdli_cat.csv", encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            if (r.get("period") or "").startswith("Ur III"):
                try:
                    per["P%06d" % int(r["id_text"])] = (r.get("provenience") or "").split("(")[0].strip() or "?"
                except Exception:
                    pass
    texts = {}
    S = dict(cur=None, body=[], seals=[], buf=None, sec=None)

    def flush():
        if S["cur"] is None or S["cur"] not in per:
            return
        if S["buf"]:
            S["seals"].append(S["buf"])
        ss = [s for s in S["seals"] if s]
        if ss:
            texts[S["cur"]] = (S["body"], ss)

    with open(RAW / "cdliatf_unblocked.atf", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("&P"):
                flush(); S.update(cur=line[1:8], sec="body", body=[], seals=[], buf=None); continue
            if line.startswith("@"):
                if line.startswith("@seal"):
                    if S["buf"]:
                        S["seals"].append(S["buf"])
                    S["buf"] = []; S["sec"] = "seal"
                elif not line.startswith("@column"):
                    if S["buf"]:
                        S["seals"].append(S["buf"])
                    S["buf"] = None; S["sec"] = "body"
                continue
            m = NUMLINE.match(line)
            if not m:
                continue
            if S["sec"] == "seal" and S["buf"] is not None:
                S["buf"].append(m.group(1))
            else:
                S["body"].append(m.group(1))
    flush()
    return per, texts


def load_ogsl():
    sl = json.loads(zipfile.ZipFile(OGSL).read("ogsl/ogsl-sl.json"))["signs"]
    r2s = defaultdict(set)
    for name, e in sl.items():
        for v in e.get("values", []):
            r2s[asc(v)].add(name)
    return r2s, {asc(n): n for n in sl}


def rtoks(word):
    out = []
    for t in re.findall(r"\{[^}]*\}|[^-{}\s]+", clean(word)):
        det = t.startswith("{")
        if det:
            t = t[1:-1].lstrip("+")
        for u in ([t] if t.startswith("|") or "(" in t else t.split(".")):
            if u:
                out.append((u, det))
    return out


def sign_of(r, r2s, name_asc):
    """Reading -> OGSL sign name, or None. Several signs: fewest components, then shortest name, then alphabetical."""
    if "(" in r and re.match(r"^[\d/n]+\(", r):
        return "NUM:" + r
    m = re.match(r"^([^()]+)\((.+)\)$", r)             # value(SIGN): the sign is kept
    if m:
        r = m.group(2)
    if r.lower() in r2s and (r == r.lower() or asc(r) not in name_asc):
        return sorted(r2s[r.lower()], key=lambda x: (x.count(".") + x.count("×") + x.count("|"), len(x), x))[0]
    if asc(r) in name_asc:
        return name_asc[asc(r)]
    if asc(r.strip("|")) in name_asc:
        return name_asc[asc(r.strip("|"))]
    return None


def seq(words, r2s, name_asc):
    """-> (signs, readings, determinative flags), or None if a reading maps to no OGSL sign."""
    sg, rd, dt = [], [], []
    for w in words:
        for r, det in rtoks(w):
            s = sign_of(r, r2s, name_asc)
            if s is None:
                return None
            sg.append(s); rd.append(r); dt.append(det)
    return sg, rd, dt


def damaged(l):
    return (any(ch in l for ch in "[]#<>?") or "..." in l or "…" in l
            or bool(re.search(r"(^|[\s\-.{])[xX]+($|[\s\-.}])", l)))


def find(sub, s):
    k = len(sub)
    return [i for i in range(len(s) - k + 1) if s[i:i + k] == sub]


def near(sub, s):
    """2 or more name signs in order inside some legend window of k + 1 signs (variant spelling)."""
    k = len(sub)
    for i in range(len(s)):
        w = s[i:i + k + 1]
        a = [[0] * (len(w) + 1) for _ in range(k + 1)]
        for x in range(k):
            for y in range(len(w)):
                a[x + 1][y + 1] = a[x][y] + 1 if sub[x] == w[y] else max(a[x][y + 1], a[x + 1][y])
        if a[k][len(w)] >= 2:
            return True
    return False


def snd(r):
    """Name sound: lower case, index digits dropped, the x of valuex(SIGN) dropped."""
    r = re.sub(r"/\d+$", "", r); px = "(" in r; v = r.split("(")[0].lower()
    if px and v.endswith("x"):
        v = v[:-1]
    return re.sub(r"\d+$", "", v)


def flat(rs, ds):
    return "".join(snd(r) for r, d in zip(rs, ds) if not d)


def isneg(a, b, nosign=False):
    """Does name a paired with legend b meet the NEG rule (and, for NEG0, share no sign)?"""
    n, L = list(a["nsig"]), list(b["leg"])
    if find(n, L) or near(n, L) or a["fn"] in b["fl"]:
        return False
    return not (nosign and set(n) & set(L))


def onep(P):
    o = {}
    for k, v in P.items():
        o.setdefault(k[0], v)                          # one pair per distinct name, the first in dump order
    return list(o.values())


def build_pools():
    """Rebuilds POS, NEG, VAR and the brief-10 counts. Label-free: no T, no alignment search."""
    per, texts = load_cdli(); r2s, name_asc = load_ogsl()
    st = Counter(); st["ur3_texts_with_legend"] = len(texts)
    # ---- brief 10's matcher (count1.py / chk.py), for the first Count-gate table
    pairs = []
    for pid, (body, S) in texts.items():
        ks = []
        for l in body:
            t = l.split()
            for i, w in enumerate(t):
                if clean1(w) in ("kiszib3", "kiszib") and i + 1 < len(t):
                    ks.append(clean1(t[i + 1]))
        if not ks:
            continue
        st["brief_with_kiszib"] += 1
        owners = [clean1(s[0].split()[0]) if s[0].split() else "" for s in S]
        hit = [k for k in ks if k in owners and k]
        if hit:
            st["brief_match"] += 1
            pairs.append((hit[0], [x for x in S if x[0].split() and clean1(x[0].split()[0]) == hit[0]][0]))
    nm = Counter(n for n, _ in pairs)
    D = {}
    for n, s in pairs:
        if any(("[" in l or "..." in l or " x" in " " + l or "#" in l) for l in s):
            continue
        D.setdefault((n, tuple(s)), 1)
    tl = [sum(len([x for x in re.split(r"[-\s]+", re.sub(r"[{}]", "-", l).strip().strip("-")) if x]) for l in s)
          for (n, s) in D]
    ns = [len([x for x in re.split(r"-+", n.replace("{", "-").replace("}", "-").strip("-")) if x]) for (n, s) in D]
    own = {}
    for (n, s) in D:
        own.setdefault(n, s)
    U = [tuple(n.replace("{", "-").replace("}", "-").strip("-").replace("--", "-").split("-")) for n in own]
    U = [p for p in U if 2 <= len(p) <= 6]
    c = Counter(x for p in U for x in p); N = sum(c.values())
    brief = dict(texts=len(texts), with_kiszib=st["brief_with_kiszib"], match=st["brief_match"],
                 mismatch=st["brief_with_kiszib"] - st["brief_match"], names=len(nm),
                 names_2plus=sum(1 for v in nm.values() if v >= 2), intact_pairs=len(D), usable_names=len(U),
                 sign_types=len(c), collision=sum((v / N) ** 2 for v in c.values()),
                 name_len_median=statistics.median(ns), legend_len_median=statistics.median(tl),
                 legend_len_quartiles=statistics.quantiles(tl, n=4),
                 name_share=statistics.median(a / b for a, b in zip(ns, tl)))
    # ---- frozen pools (count3b.py), then the sound rule (count4b.py)
    cat = Counter(); cand = []
    for pid, (body, S) in texts.items():
        ks = []
        for l in body:
            t = l.split()
            for i, w in enumerate(t):
                if clean(w) in ("kiszib3", "kiszib") and i + 1 < len(t):
                    ks.append(t[i + 1])
        if not ks:
            continue
        if len(ks) != 1 or len(S) != 1:
            cat["not_1name_1seal"] += 1; continue
        k, s = ks[0], S[0]
        if any(damaged(l) for l in s):
            cat["legend_damaged"] += 1; continue
        if damaged(k):
            cat["name_damaged"] += 1; continue
        ck = clean(k)
        if ck in STOPSET or ck.startswith(STOPPRE) or ck.endswith(STOPSUF):
            cat["title_not_name"] += 1; continue
        n = seq([k], r2s, name_asc); L = seq([w for l in s for w in l.split()], r2s, name_asc)
        if n is None or L is None:
            cat["unmapped_reading"] += 1; continue
        if not (2 <= len(n[0]) <= 6):
            cat["name_len"] += 1; continue
        if any(x.startswith("NUM:") for x in n[0]):
            cat["name_numeral"] += 1; continue
        if sum(n[2]) > 1:
            cat["name_2_determinatives"] += 1; continue
        if len(n[0]) - sum(n[2]) < 2:
            cat["name_under_2_sound_units"] += 1; continue
        cand.append((pid, s, n, L))
    attested = {tuple(c[2][1]) for c in cand}
    POS, NEG, VAR = {}, {}, {}
    for pid, s, n, L in cand:
        if n[1][-1] in ("ra", "bi", "ka") and tuple(n[1][:-1]) in attested:
            cat["case_form"] += 1; continue
        rec = dict(prov=per[pid], nsig=tuple(n[0]), ndet=tuple(n[2]), leg=tuple(L[0]), lread=tuple(L[1]),
                   snd=tuple(snd(r) for r, d in zip(n[1], n[2]) if not d), fn=flat(n[1], n[2]), fl=flat(L[1], L[2]),
                   nlines=len(s), start=None, tr=None)
        key = (rec["nsig"], rec["leg"])
        h = find(n[0], L[0])
        if h:
            cat["tablet_POS"] += 1; rec["start"] = h[0]
            rec["tr"] = tuple(h[0] + i for i, d in enumerate(n[2]) if not d)      # truth, used for scoring only
            POS.setdefault(key, rec)
        elif near(n[0], L[0]):
            cat["tablet_VAR"] += 1; VAR.setdefault(key, rec)
        else:
            cat["tablet_NEG"] += 1; NEG.setdefault(key, rec)
    for k in [k for k, v in NEG.items() if v["fn"] in v["fl"]]:
        VAR[k] = NEG.pop(k)
    return POS, NEG, VAR, cat, brief


def load_m77():
    """Arm C: distinct seal texts of 2 or more signs. Only `object_type` and `seq` are read from each record (A5)."""
    T = set()
    with open(M77, encoding="utf-8") as f:
        for l in f:
            r = json.loads(l)
            ot, sq = r.get("object_type"), r.get("seq")
            del r
            if ot != "seal":
                continue
            s = tuple(x for x in sq if x != "|")
            if len(s) >= 2:
                T.add(s)
    return sorted(T)


# ------------------------------------------------------------------ A1: recount against the prereg's tables
VALTAB = {3: (8, .21, 0, .01, .00), 4: (11, .79, 1, .04, .00), 5: (13, .98, 1, .14, .00), 6: (15, 1.0, 2, .29, .00),
          8: (20, 1.0, 3, .69, .00), 10: (23, 1.0, 4, .91, .00), 15: (32, 1.0, 8, 1.0, .21), 20: (39, 1.0, 11, 1.0, .81),
          25: (46, 1.0, 15, 1.0, .99)}


def recount(POS, NEG, VAR, cat, brief, texts77):
    """A1. Every figure below is a count, a length or a sign overlap. No T is computed. -> (stats, problems)."""
    bad = []; st = {}

    def eq(name, got, want):
        st[name] = got
        if got != want:
            bad.append(f"{name}: {got} != {want}")

    def close(name, got, want, tol):
        # PREREG-AMBIGUITY: "shares within 0.01" is taken on the figure as the prereg prints it, so the tolerance is
        # 0.01 plus half a unit of its last printed digit.
        st[name] = round(got, 4)
        if abs(got - want) > tol + 1e-9:
            bad.append(f"{name}: {got:.4f} not within {tol} of {want}")

    P1, N1 = onep(POS), onep(NEG)
    eq("POS_pairs", len(POS), 1316); eq("NEG_pairs", len(NEG), 224); eq("VAR_pairs", len(VAR), 128)
    eq("POS_names", len(P1), 483); eq("NEG_names", len(N1), 154)
    eq("POS_tablets", cat["tablet_POS"], 6303); eq("NEG_tablets_before_sound_rule", cat["tablet_NEG"], 617)
    eq("VAR_tablets_before_sound_rule", cat["tablet_VAR"], 213)
    for k, w in (("legend_damaged", 5113), ("title_not_name", 1289), ("name_damaged", 570), ("not_1name_1seal", 471),
                 ("case_form", 70), ("unmapped_reading", 57), ("name_2_determinatives", 25), ("name_numeral", 7)):
        eq("dropped_" + k, cat[k], w)
    # PREREG-AMBIGUITY: "161 by name length" may or may not include names with under 2 sound units; either passes.
    st["dropped_name_len"] = [cat["name_len"], cat["name_under_2_sound_units"]]
    if 161 not in (cat["name_len"], cat["name_len"] + cat["name_under_2_sound_units"]):
        bad.append(f"dropped by name length: {st['dropped_name_len']} does not give 161")
    by = lambda P, c: [v for v in P if v["prov"] == c]
    for c, pn, nn, nl, z, zl in (("Umma", 227, 63, 56, 31, 30), ("Girsu", 212, 57, 53, 35, 32)):
        C = by(N1, c); Z = [v for v in C if not set(v["nsig"]) & set(v["leg"])]
        eq(f"POS_names_{c}", len(by(P1, c)), pn); eq(f"NEG_names_{c}", len(C), nn)
        eq(f"NEG_legends_{c}", len({v["leg"] for v in C}), nl)
        eq(f"NEG0_names_{c}", len(Z), z); eq(f"NEG0_legends_{c}", len({v["leg"] for v in Z}), zl)
    # brief 10's numbers under its own rule (recount column)
    for k, w in (("texts", 23362), ("with_kiszib", 14891), ("match", 10041), ("mismatch", 4850), ("names", 712),
                 ("names_2plus", 401), ("intact_pairs", 1623), ("usable_names", 505), ("sign_types", 283),
                 ("name_len_median", 3), ("legend_len_median", 9)):
        eq("brief_" + k, brief[k], w)
    close("brief_match_share", brief["match"] / max(1, brief["with_kiszib"]), 0.674, 0.0105)
    close("brief_collision", brief["collision"], 0.020, 0.0005)
    close("brief_name_share", brief["name_share"], 0.33, 0.015)
    for q, w in zip(brief["legend_len_quartiles"], (8, 9, 11)):
        close("brief_legend_quartile_%d" % w, q, w, 0.5)
    # PREREG-AMBIGUITY: the split of the 4,850 brief-rule mismatches into four classes is not recounted. It
    # describes a pool this study does not use, and the prereg notes its own tokeniser gives 4,852.
    st["not_recounted"] = ["brief-rule mismatch classes (1,288 / 1,455 / 174 / 1,935)", "AN, DUB, SAR shares"]
    # shape of the pools (every distinct pair)
    for nm, P, ln, qs, det in (("POS", POS, 9, (8, 9, 11), 0.39), ("NEG", NEG, 10, (9, 10, 12), 0.17)):
        V = list(P.values()); ll = [len(v["leg"]) for v in V]
        eq(nm + "_name_signs_median", statistics.median(len(v["nsig"]) for v in V), 3)
        eq(nm + "_legend_signs_median", statistics.median(ll), ln)
        for q, w in zip(statistics.quantiles(ll, n=4), qs):
            close(f"{nm}_legend_quartile_{w}", q, w, 0.5)
        eq(nm + "_legend_lines_median", statistics.median(v["nlines"] for v in V), 3)
        close(nm + "_one_determinative", sum(1 for v in V if sum(v["ndet"]) == 1) / len(V), det, 0.015)
    eq("POS_name_opens_legend", sum(1 for v in POS.values() if v["start"] == 0), 1198)
    # sign sharing over one pair per name. PREREG-AMBIGUITY: the prereg's figures were sampled (100,000 draws); the
    # recount is exact over all pairs, which lies within the tolerance of a sampled share.
    LS = [set(v["leg"]) for v in P1]; NS = [set(v["nsig"]) for v in P1]
    OF = [set(v["leg"][:v["start"]] + v["leg"][v["start"] + len(v["nsig"]):]) for v in P1]
    n = len(P1); s1 = s2 = so = sn = 0
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            sn += bool(NS[a] & LS[b])
            if a < b:
                x = len(LS[a] & LS[b]); s1 += x >= 1; s2 += x >= 2; so += bool(OF[a] & OF[b])
    up = n * (n - 1) / 2
    close("POS_legends_share_1", s1 / up, 0.934, 0.0105); close("POS_legends_share_2", s2 / up, 0.693, 0.0105)
    close("POS_legends_share_outside_span", so / up, 0.881, 0.0105)
    close("POS_name_shares_other_legend", sn / (2 * up), 0.422, 0.0105)
    close("POS_legends_with_TUR", sum(1 for x in LS if "TUR" in x) / n, 0.89, 0.015)
    sg = Counter(s for v in P1 for s in v["nsig"]); s2g = defaultdict(set); g2s = defaultdict(set)
    for v in P1:
        it = iter(v["snd"])
        for s, d in zip(v["nsig"], v["ndet"]):
            if not d:
                u = next(it); s2g[u].add(s); g2s[s].add(u)
    eq("POS_name_sign_types", len(sg), 205); eq("POS_name_sounds", len(s2g), 201)
    eq("sounds_with_2_signs", sum(1 for x in s2g.values() if len(x) > 1), 47)
    eq("signs_with_2_sounds", sum(1 for x in g2s.values() if len(x) > 1), 45)
    npl = [2 * (max(0, len(v["leg"]) - len(v["nsig"]) + 1) + (len(v["nsig"]) - 1) * max(0, len(v["leg"]) - len(v["nsig"])))
           for v in P1]
    eq("placements_median", statistics.median(npl), 38); eq("placements_max", max(npl), 282)
    # mismatched tablets are not unrelated pairs; re-pairing inside NEG
    for c, own_w, oth_w, cross_w, all_w in (("Umma", .51, .32, .92, .47), ("Girsu", .39, .30, .94, .54)):
        C = by(N1, c); ok = tot = 0; oth = []
        for a in C:
            for b in C:
                if a is b:
                    continue
                tot += 1
                if isneg(a, b):
                    ok += 1; oth.append(bool(set(a["nsig"]) & set(b["leg"])))
        close(f"NEG_own_share_{c}", sum(1 for v in C if set(v["nsig"]) & set(v["leg"])) / len(C), own_w, 0.015)
        close(f"NEG_other_share_{c}", sum(oth) / max(1, len(oth)), oth_w, 0.015)
        close(f"NEG_cross_pairs_meet_rule_{c}", ok / max(1, tot), cross_w, 0.015)
        # PREREG-AMBIGUITY: this figure and the values table below are Monte-Carlo counts. A fresh stream would
        # differ from them by more than 0.01 by chance alone, so the recount replays the scratch scripts' own
        # streams (a private Random(1) here, Random(20261125) below). They are counts, not study draws.
        rng = random.Random(1); acc = 0
        if len(C) >= 10:
            for _ in range(2000):
                S = rng.sample(C, 10); p = list(range(10)); rng.shuffle(p)
                acc += all(isneg(S[i], S[p[i]]) for i in range(10) if p[i] != i)
        close(f"NEG_repairing_of_10_all_NEG_{c}", acc / 2000, all_w, 0.015)
    # how many values, and how many with their own check
    U = [set(v["snd"]) for v in P1]; rng = random.Random(20261125)
    for m in (3, 4, 5, 6, 8, 10, 12, 15, 20, 25):
        vals = []; chk = []
        for _ in range(4000):
            c = Counter(s for i in rng.sample(range(len(U)), m) for s in U[i])
            vals.append(len(c)); chk.append(sum(1 for x in c.values() if x >= 2))
        if m in VALTAB:
            w = VALTAB[m]; f = lambda L, x: sum(1 for v in L if v >= x) / len(L)
            eq(f"values_fixed_median_m{m}", statistics.median(vals), w[0])
            close(f"P_10_fixed_m{m}", f(vals, 10), w[1], 0.015)
            eq(f"repeated_sounds_median_m{m}", statistics.median(chk), w[2])
            close(f"P_3_repeated_m{m}", f(chk, 3), w[3], 0.015); close(f"P_10_repeated_m{m}", f(chk, 10), w[4], 0.015)
    # Indus side: M77 sign identifiers only
    c = Counter(x for t in texts77 for x in t); TS = [frozenset(t) for t in texts77]; n = len(TS)
    eq("M77_texts", n, 1575); eq("M77_tokens", sum(c.values()), 7685); eq("M77_types", len(c), 370)
    eq("M77_median_length", statistics.median(len(t) for t in texts77), 5)
    eq("M77_texts_5plus", sum(1 for t in texts77 if len(t) >= 5), 852)
    eq("M77_types_5plus_tokens", sum(1 for v in c.values() if v >= 5), 175)
    s1 = s2 = 0
    for a in range(n):
        A = TS[a]
        for b in range(a + 1, n):
            x = len(A & TS[b]); s1 += x >= 1; s2 += x >= 2
    up = n * (n - 1) / 2
    close("M77_share_1", s1 / up, 0.395, 0.0105); close("M77_share_2", s2 / up, 0.097, 0.0105)
    close("M77_commonest_sign_in_texts", max(Counter(x for t in TS for x in t).values()) / n, 0.47, 0.015)
    return st, bad


# ------------------------------------------------------------------ the test: alignment family, T, null
def enum_place(k, L, both):
    """Placements of k units on a legend of L signs, as tuples of legend positions: contiguous, or contiguous with
    one legend sign skipped between two units; forward, and (both) reversed."""
    fw = [tuple(range(st, st + k)) for st in range(L - k + 1)]
    fw += [tuple(st + j + (j >= sk) for j in range(k)) for st in range(L - k) for sk in range(1, k)]
    return fw + [tuple(L - 1 - p for p in t) for t in fw] if both else fw


class Prob:
    """One set: m names (sound tuples) and m legends (symbol tuples, opaque). Pair i under a pairing `perm` is
    (name i, legend perm[i])."""

    def __init__(self, names, legs, arm, spans):
        self.m = len(names); self.arm = arm; self.spans = spans
        si, yi = {}, {}
        self.N = [tuple(si.setdefault(s, len(si)) for s in n) for n in names]
        self.L = [tuple(yi.setdefault(y, len(yi)) for y in l) for l in legs]
        self.rs = list(si); self.ry = list(yi); self.ny = len(yi) + 1
        self.has = [frozenset(l) for l in self.L]
        self.so = defaultdict(set)
        for i, n in enumerate(self.N):
            for s in n:
                self.so[s].add(i)
        self.ds = [tuple(dict.fromkeys(n)) for n in self.N]
        self.pc = {}

    def place(self, i, j):
        """[(positions, ((sound, (symbols...)), ...))] for name i in legend j under the arm's family."""
        r = self.pc.get((i, j))
        if r is None:
            n, leg = self.N[i], self.L[j]; k = len(n)
            if self.arm == "A":                        # window of k + 1 signs from the legend's span start, forward
                a = self.spans[j]
                idx = [tuple(a + p for p in t) for t in enum_place(k, len(leg[a:a + k + 1]), False)]
            else:
                idx = enum_place(k, len(leg), self.arm == "B2")
            r = []
            for pos in idx:
                d = {}
                for s, p in zip(n, pos):
                    d.setdefault(s, set()).add(leg[p])
                r.append((pos, tuple((s, tuple(ys)) for s, ys in d.items())))
            self.pc[(i, j)] = r
        return r

    def xfun(self, perm):
        """x(s, y): objects whose name lacks s and whose legend holds y anywhere."""
        hold = defaultdict(list); so = self.so; ny = self.ny; X = {}
        for j in range(self.m):
            for y in self.has[perm[j]]:
                hold[y].append(j)

        def x(s, y):
            v = X.get(s * ny + y)
            if v is None:
                o = so[s]; v = sum(1 for j in hold[y] if j not in o); X[s * ny + y] = v
            return v
        return x

    def T(self, perm, rseed, want=False):
        """Largest G the search finds: six restarts from random placements; sweep the pairs in order; a pair moves
        to its best placement only on a strict gain; stop when a sweep changes nothing or after 20 sweeps."""
        # PREREG-AMBIGUITY (bears on K0): the scratch scripts moved a pair to the first of its best placements even
        # when that only tied its current one. The prereg says "moves only on a strict gain", so a pair stays where
        # it is unless another placement scores strictly higher; among equal best placements the first in the
        # family's order is taken. All credits are multiples of 0.25, so comparisons are exact.
        m = self.m; x = self.xfun(perm); ny = self.ny
        PL = [self.place(i, perm[i]) for i in range(m)]
        best = 0.0; bcur = None
        for r in range(RESTARTS):
            rng = rseed(r)
            cur = [rng.randrange(len(p)) if p else -1 for p in PL]     # no placement: no credit, no a(s, y)
            A = defaultdict(dict)
            for i in range(m):
                if cur[i] >= 0:
                    for s, ys in PL[i][cur[i]][1]:
                        d = A[s]
                        for y in ys:
                            d[y] = d.get(y, 0) + 1
            for _ in range(SWEEPS):
                changed = False
                for i in range(m):
                    P = PL[i]
                    if len(P) < 2:
                        continue
                    ci = cur[i]
                    for s, ys in P[ci][1]:
                        d = A[s]
                        for y in ys:
                            d[y] -= 1
                    c0 = {}
                    for s in self.ds[i]:
                        b = 0.0
                        for y, a in A[s].items():
                            if a >= 2:
                                c = a - 1 - LAM * x(s, y)
                                if c > b:
                                    b = c
                        c0[s] = b
                    memo = {}; bv = -1.0; bp = ci; vc = 0.0
                    for pi, (_, grp) in enumerate(P):
                        v = 0.0
                        for s, ys in grp:
                            c = c0[s]; d = A[s]
                            for y in ys:
                                w = memo.get(s * ny + y)
                                if w is None:
                                    a = d.get(y, 0)    # with this pair added: a + 1 objects, credit a - LAM * x
                                    w = a - LAM * x(s, y) if a >= 1 else 0.0
                                    memo[s * ny + y] = w
                                if w > c:
                                    c = w
                            v += c
                        if v > bv:
                            bv, bp = v, pi
                        if pi == ci:
                            vc = v
                    if bv > vc:
                        cur[i] = bp; changed = True
                    for s, ys in P[cur[i]][1]:
                        d = A[s]
                        for y in ys:
                            d[y] = d.get(y, 0) + 1
                if not changed:
                    break
            g = 0.0
            for s, d in A.items():
                b = 0.0
                for y, a in d.items():
                    if a >= 2:
                        c = a - 1 - LAM * x(s, y)
                        if c > b:
                            b = c
                g += b
            if bcur is None or g > best:
                best, bcur = g, cur
        return (best, bcur) if want else best

    def values(self, perm, cur):
        """Each sound with credit above 0 and its best symbol: sound -> (symbol, [(object, [(unit, position)])])."""
        # PREREG-AMBIGUITY: two symbols with equal credit for one sound: the one met first in the set is taken.
        x = self.xfun(perm); A = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for i in range(self.m):
            if cur[i] < 0:
                continue
            pos = self.place(i, perm[i])[cur[i]][0]; leg = self.L[perm[i]]
            for u, (s, p) in enumerate(zip(self.N[i], pos)):
                A[s][leg[p]][i].append((u, p))
        out = {}
        for s, d in A.items():
            b = 0.0; by = None
            for y in sorted(d):
                a = len(d[y])
                if a >= 2 and a - 1 - LAM * x(s, y) > b:
                    b, by = a - 1 - LAM * x(s, y), y
            if by is not None:
                out[self.rs[s]] = (self.ry[by], list(d[by].items()))
        return out


def loo(prob, names, legs, spans, truth, arm, ctx):
    """Leave-one-out readout. -> (confirmed values, confirmed and right values) for the set."""
    # PREREG-AMBIGUITY: a value is a (sound, symbol) pair within one set. It is "right" only if, for every held-out
    # name that confirms it, the units behind it in the m - 1 search all sit on their true legend positions and some
    # confirming placement of the held-out name puts its units of that sound on their true positions. A set with no
    # truth (NEG, MIS) has no right values. The held-out searches use the seed purpose init/loo<i>/<restart>.
    m = len(names); conf = {}
    for i in range(m):
        idx = [j for j in range(m) if j != i]
        sub = Prob([names[j] for j in idx], [legs[j] for j in idx], arm, [spans[j] for j in idx])
        ident = list(range(m - 1))
        g, cur = sub.T(ident, lambda r: rng_for(ctx, f"init/loo{i}/{r}"), want=True)
        if g <= 0:
            continue
        val = sub.values(ident, cur); n = names[i]; leg = legs[i]
        U = [j for j, s in enumerate(n) if s in val]
        if not U:
            continue
        oks = [pos for pos, _ in prob.place(i, i) if all(leg[pos[j]] == val[n[j]][0] for j in U)]
        if not oks:
            continue
        for s in {n[j] for j in U}:
            y, sup = val[s]; right = False
            if truth is not None and truth[i] is not None:
                right = (any(all(pos[j] == truth[i][j] for j in U if n[j] == s) for pos in oks)
                         and all(truth[idx[o]] is not None and all(truth[idx[o]][u] == p for u, p in ups)
                                 for o, ups in sup))
            conf[(s, y)] = conf.get((s, y), True) and right
    return len(conf), sum(1 for v in conf.values() if v)


# ------------------------------------------------------------------ sets (prereg "Sets", "Cells", "Arm C")
def kept_list(cell, arm, pool, m, city, idx, recs):
    """Shuffle the city's pairs with the seed purpose partition/<idx>; keep a pair only if its legend is new."""
    key = (cell, arm, pool, m, city, idx)
    if key not in _PART:
        L = list(recs); rng_for((cell, arm, pool, m, city, ""), f"partition/{idx}").shuffle(L)
        seen = set(); out = []
        for r in L:
            if r["leg"] not in seen:
                seen.add(r["leg"]); out.append(r)
        if len(_PART) > 64:
            _PART.clear()
        _PART[key] = out
    return _PART[key]


def pick(cell, arm, pool, m, city, s):
    """-> (the m pair records of set s, partition index), or None if the set cannot be drawn (F3)."""
    # PREREG-AMBIGUITY: arm C's mismatch half (pool label MIS in the seeds) takes its m names from the POS names by
    # the same partition procedure as the power half, under its own seed label.
    recs = W["POS" if pool in ("POS", "MIS") else pool][city]
    part, blk = 0, s                                   # POS: one partition per city, its first 10 blocks
    if pool in ("NEG", "NEG0"):
        q = len({r["leg"] for r in recs}) // m
        if q == 0:
            return None
        if q < 10:                                     # successive partitions of q disjoint sets
            part, blk = divmod(s, q)
    block = kept_list(cell, arm, pool, m, city, part, recs)[blk * m:(blk + 1) * m]
    return (block, part) if len(block) == m else None


def build_set(spec):
    """-> dict(names, legs, spans, truth, adm, part) or None. spans: arm A's span start per legend. truth: per pair
    the true legend position of each unit, or None. adm: admissible (name, legend) pairs for restricted re-pairings."""
    cell, arm, pool, m, city, s = spec[:6]; ctx = spec[:6]
    if cell == "Kp":
        # PREREG-AMBIGUITY: Kp's sets are drawn from one stream per set, purpose `host`.
        rng = rng_for(ctx, "host")
        names = [tuple(rng.choices(range(12), k=3)) for _ in range(m)]; rev = rng.random() < 0.5
        legs = []; truth = []; spans = []
        for i, n in enumerate(names):
            L = [("f", i, j) for j in range(6)]; p = rng.randrange(7); sg = [("g", x) for x in n]
            L[p:p] = sg[::-1] if rev else sg
            legs.append(tuple(L)); spans.append(p); truth.append(tuple(p + (2 - j if rev else j) for j in range(3)))
        return dict(names=names, legs=legs, spans=spans, truth=truth, adm=None, part=0)
    if cell == "Kc":
        # PREREG-AMBIGUITY: the two cities hold 227 and 212 POS names, too few for 10 disjoint sets of 15 names plus
        # 15 outside legends each. Set s uses its own partition s: the first block of 15 gives the names and the
        # second block gives the 15 outside legends. Sets overlap across partitions; within a set no pair is true
        # and every pairing is exchangeable, which is all Kc needs.
        kept = kept_list(cell, arm, pool, m, city, s, W["POS"][city])
        if len(kept) < 2 * m:
            return None
        return dict(names=[r["snd"] for r in kept[:m]], legs=[r["leg"] for r in kept[m:2 * m]], spans=[0] * m,
                    truth=None, adm=None, part=s)
    got = pick(cell, arm, pool, m, city, s)
    if got is None:
        return None
    block, part = got
    names = [r["snd"] for r in block]
    if cell in ("C1", "C2"):
        T77 = W["M77"]; hr = rng_for(ctx, "host")
        order = list(range(len(T77))); hr.shuffle(order); used = set(); hosts = []
        for n in names:                                # m distinct texts; a name of k units gets k + 2 signs or more
            for t in order:
                if t not in used and len(T77[t]) >= len(n) + 2:
                    used.add(t); hosts.append(list(T77[t])); break
            else:
                return None
        if pool == "MIS":                              # untouched texts: every pairing is exchangeable
            return dict(names=names, legs=[tuple(h) for h in hosts], spans=[0] * m, truth=None, adm=None, part=part)
        # PREREG-AMBIGUITY: "All names in a set run the same way": one direction per set, drawn at random under B2
        # (as Kp) and forward under B1 and A, whose families cannot hold a reversed name.
        rev = hr.random() < 0.5 if arm == "B2" else False
        cr = rng_for(ctx, "code"); sounds = sorted({x for n in names for x in n})
        if cell == "C1":                               # types drawn in proportion to their M77 token counts
            ty = list(W["M77_TYPES"]); wt = list(W["M77_COUNTS"]); code = {}
            for x in sounds:
                j = cr.choices(range(len(ty)), weights=wt)[0]; code[x] = ty.pop(j); wt.pop(j)
        else:                                          # evenly from the types with 5 or more tokens
            code = dict(zip(sounds, cr.sample(W["M77_T5"], len(sounds))))
        truth = []; spans = []
        for n, h in zip(names, hosts):
            k = len(n); st = hr.randrange(len(h) - k + 1); cd = [code[x] for x in n]
            h[st:st + k] = cd[::-1] if rev else cd
            spans.append(st); truth.append(tuple(st + (k - 1 - j if rev else j) for j in range(k)))
        return dict(names=names, legs=[tuple(h) for h in hosts], spans=spans, truth=truth, adm=None, part=part)
    # PREREG-AMBIGUITY: in R3 a legend symbol is the reading as the editor wrote it, index kept (determinatives too).
    legs = [r["lread"] if cell == "R3" else r["leg"] for r in block]
    if cell == "R1":                                   # each legend sign unread with probability 0.20
        nr = rng_for(ctx, "noise")
        legs = [tuple(("?", i, p) if nr.random() < R1_P else y for p, y in enumerate(l)) for i, l in enumerate(legs)]
    if cell == "R2":                                   # each name unit a word sign with probability 0.25
        nr = rng_for(ctx, "noise")
        names = [tuple(("?", i, j) if nr.random() < R2_P else x for j, x in enumerate(n)) for i, n in enumerate(names)]
    adm = None
    if pool in ("NEG", "NEG0"):                        # the rule is read on the clean records, whatever the cell
        adm = [[i == j or isneg(a, b, pool == "NEG0") for j, b in enumerate(block)] for i, a in enumerate(block)]
    pos = pool == "POS"
    return dict(names=names, legs=legs, spans=[r["start"] if pos else 0 for r in block],
                truth=[r["tr"] for r in block] if pos else None, adm=adm, part=part)


def job_set(spec):
    """One set: observed T, re-pairings with early stopping, leave-one-out readout. Returns aggregates only."""
    if INIT_ERR is not None:
        raise RuntimeError("worker init failed: " + INIT_ERR)
    cell, arm, pool, m, city, s, nperm, passb = spec; ctx = spec[:6]; t0 = time.time()
    row = dict(cell=cell, arm=arm, pool=pool, m=m, city=city, set=s, part=None, built=True, capped=False, T=None,
               b=None, n=0, passed=False, conf=0, right=0)
    S = build_set(spec)
    if S is None:                                      # F3: a set that cannot be drawn
        row["built"] = False; return row
    row["part"] = S["part"]
    prob = Prob(S["names"], S["legs"], arm, S["spans"]); ident = list(range(m)); adm = S["adm"]
    T0 = prob.T(ident, lambda r: rng_for(ctx, f"init/0/{r}")); b = n = 0
    if T0 > 0:                                         # an observed T of 0 never passes
        for p in range(1, nperm + 1):
            pr = rng_for(ctx, f"perm/{p}"); perm = None
            for _ in range(TRIES if adm is not None else 1):
                c = ident[:]; pr.shuffle(c)
                if adm is None or all(adm[i][c[i]] for i in range(m)):
                    perm = c; break
            if perm is None:                           # F3: a NEG re-pairing hit the 10,000 cap
                row["capped"] = True; break
            n += 1
            if prob.T(perm, lambda r, p=p: rng_for(ctx, f"init/{p}/{r}")) >= T0:
                b += 1                                 # ties count against the set
                if b > passb:                          # the run may stop once b reaches 10 (2 under F2)
                    break
        row["passed"] = b <= passb and not row["capped"]
        row["b"] = b
    row["T"] = T0; row["n"] = n
    row["conf"], row["right"] = loo(prob, S["names"], S["legs"], S["spans"], S["truth"], arm, ctx)
    row["sec"] = round(time.time() - t0, 1)
    return row


# ------------------------------------------------------------------ workers
def setup(payload):
    global W
    W = payload


def init(payload):
    global INIT_ERR
    try:
        a5_hook(); setup(payload)
    except BaseException as e:                         # a raising initializer would respawn workers for ever
        INIT_ERR = repr(e)


def run_jobs(jobs):
    """Jobs go to at most NWORK (<= 4) worker processes; the pool is opened only after the A4 guard has passed."""
    global POOL
    if POOL is None:
        POOL = Pool(NWORK, initializer=init, initargs=(PAYLOAD,))
    return POOL.map(job_set, jobs, chunksize=1)


def jobs_for(cell, arm, pool, m, nperm, passb):
    if cell == "Kp":
        return [(cell, arm, pool, m, "-", s, nperm, passb) for s in range(20)]
    return [(cell, arm, pool, m, c, s, nperm, passb) for c in CITIES for s in range(10)]


def summ(rows):
    """20 sets of one cell, arm, pool and rung. F3: an unbuilt set or a capped NEG re-pairing counts as a non-pass
    for POS and as a pass for a mismatch pool."""
    mism = rows[0]["pool"] in MISM
    f3 = [(not r["built"]) or r["capped"] for r in rows]
    cnt = [(r["passed"] and not f) or (mism and f) for r, f in zip(rows, f3)]
    p0 = [c for c, r in zip(cnt, rows) if r["part"] == 0]
    out = dict(passes=sum(cnt), sets=len(rows), f3=sum(f3), first_partition=[sum(p0), len(p0)],
               T=[r["T"] for r in rows], b=[r["b"] for r in rows], n=[r["n"] for r in rows],
               confirmed=[r["conf"] for r in rows], right=[r["right"] for r in rows],
               cpu_s=round(sum(r.get("sec", 0) for r in rows)))
    if not mism:
        out["median_right"] = statistics.median(out["right"])
    return out


def run_groups(groups, nperm, passb):
    """groups: [(cell, arm, pool, m)] -> {group: summary}, all sets of the batch in one map."""
    jobs = [j for g in groups for j in jobs_for(*g, nperm, passb)]
    res = run_jobs(jobs); out = {}
    for g in groups:
        out[g] = summ([r for r in res if (r["cell"], r["arm"], r["pool"], r["m"]) == g])
    return out


# ------------------------------------------------------------------ F2: cost on synthetic sets, before any real pair
def f2_time():
    """Mean CPU seconds per T on 50 synthetic sets of the calibration generator at each m and arm."""
    # PREREG-AMBIGUITY: per set the timing takes T once on the planted pairing and on three re-pairings (the null
    # is 999 of every 1,000 values). CPU time is process time, measured in the parent before the pool opens.
    t = {}
    for m in sorted(RUNGS + (20,)):
        rng = rng_for(("F2", "-", "SYN", m, "-", ""), "host")
        nsnd = 203; w = [1 / (r + 3) ** 0.9 for r in range(nsnd)]
        alt = {s: 1000 + s for s in rng.sample(range(nsnd), 46)}
        poly = dict(zip(rng.sample(range(nsnd), 46), rng.sample(range(nsnd), 46)))
        pool = {}
        while len(pool) < 400:
            sn = tuple(rng.choices(range(nsnd), w, k=rng.choice((2, 3, 3, 3, 3, 4, 4, 5)))); sg = []
            for s in sn:
                if s in alt and rng.random() < 0.4:
                    sg.append(alt[s])
                elif s in poly and rng.random() < 0.5:
                    sg.append(poly[s])
                else:
                    sg.append(s)
            pool.setdefault(sn, (sn, tuple(sg)))
        pool = list(pool.values())

        def legend(owner):
            L = list(owner)
            if rng.random() < 0.56:
                L += ["DUB", "SAR"]
            if rng.random() < 0.89:
                L += ["TUR"] + list(rng.choice(pool)[1])
            return tuple(L + rng.choices(range(nsnd), w, k=rng.choice((0, 0, 1, 2, 3))))
        sets = []
        for _ in range(50):
            S = rng.sample(pool, m); sets.append(([s[0] for s in S], [legend(s[1]) for s in S]))
        for arm in ARMS:
            t0 = time.process_time(); n = 0
            for si, (names, legs) in enumerate(sets):
                pr = Prob(names, legs, arm, [0] * m); ctx = ("F2", arm, "SYN", m, "-", si)
                for p in range(4):
                    perm = list(range(m))
                    if p:
                        rng_for(ctx, f"perm/{p}").shuffle(perm)
                    pr.T(perm, lambda r, p=p: rng_for(ctx, f"init/{p}/{r}")); n += 1
            t[(m, arm)] = (time.process_time() - t0) / n
    # PREREG-AMBIGUITY: the projection sums every cell, arm, pool and rung once: P in three arms, POS and NEG, 10
    # rungs (row X is rungs 12 and 15 of P and is not counted twice); R1, R2, R3, C1, C2 in one arm, taken as B2
    # (the costliest; the claiming arm is not known yet); X20 as P and C1 at m = 20, POS only, B2.
    per = 20 * 1000
    tot = sum(2 * per * t[(m, a)] for a in ARMS for m in RUNGS) + sum(5 * 2 * per * t[(m, "B2")] for m in RUNGS)
    tot += 2 * per * t[(20, "B2")]
    hours = tot / 3600; fb = hours > F2_HOURS
    return dict(ms_per_T={f"{m}/{a}": round(1000 * v, 2) for (m, a), v in t.items()}, projected_cpu_hours=round(hours, 2),
                limit_hours=F2_HOURS, applied=fb, nperm=F2_NPERM if fb else NPERM, pass_b=F2_PASSB if fb else PASSB)


# ------------------------------------------------------------------ modes
def start(mode, path, prev=None):
    seal = seal_check(); why, fm = a4()
    if prev is not None and (seal["code_sha256"] != prev.get("code_sha256")
                             or seal["prereg_sha256"] != prev.get("prereg_sha256")):
        why.append("run.py or the prereg changed since `kill`")
    if not seal["sealed"]:
        why.append("the prereg on disk is not the sealed anchor_crossread prereg (sha256 not in HASHES.txt)")
    if why:
        print("A4: do not start:", "; ".join(why)); sys.exit(2)       # nothing computed, nothing written
    out = dict(prereg=PREREG, mode=mode, status="running", nwork=NWORK, penalty_weight=LAM, **seal, indus=R_INDUS,
               A4=dict(free_mem_frac=round(fm, 3)), fallbacks={})
    dump(out, path)
    return out


def prepare(out, path):
    """A2, then the label-free pool build and A1. Sets the parent state and the worker payload. No T."""
    global PAYLOAD
    ok = OGSL.exists() and sha256_of(OGSL) == OGSL_SHA
    out["A2"] = dict(passed=ok)
    if not ok:
        stop(out, path, "A2: raw/ogsl/ogsl.zip is missing or does not match its SHA-256 in the prereg (the study "
                        "keeps its own copy of the public OGSL zip there)")
    POS, NEG, VAR, cat, brief = build_pools(); texts77 = load_m77()
    st, bad = recount(POS, NEG, VAR, cat, brief, texts77)
    out["A1"] = dict(passed=not bad, problems=bad, recount=st)
    if bad:
        stop(out, path, "A1: a recount differs from the prereg's tables: " + "; ".join(bad[:6]))
    P1, N1 = onep(POS), onep(NEG); c = Counter(x for t in texts77 for x in t); ty = sorted(c)
    keep = ("snd", "nsig", "leg", "lread", "fn", "fl", "start", "tr")
    slim = lambda V, city: [{k: v[k] for k in keep} for v in V if v["prov"] == city]
    PAYLOAD = dict(POS={c_: slim(P1, c_) for c_ in CITIES}, NEG={c_: slim(N1, c_) for c_ in CITIES},
                   NEG0={c_: slim([v for v in N1 if not set(v["nsig"]) & set(v["leg"])], c_) for c_ in CITIES},
                   M77=texts77, M77_TYPES=ty, M77_COUNTS=[c[x] for x in ty], M77_T5=[x for x in ty if c[x] >= 5])
    setup(PAYLOAD)
    say("A1", passed=True, POS=len(POS), NEG=len(NEG), VAR=len(VAR))


def load_json(name, why):
    p = HERE / name
    if not p.exists():
        sys.exit(f"{name} missing: {why}")
    return json.load(open(p))


def refuse_if_exists(*names):
    for n in names:
        if (HERE / n).exists():
            sys.exit(f"{n} exists: no rerun after any T on a real pair is seen (prereg Aborts). If its status shows "
                     "a stop before Kc, nothing real was scored; that is for the coordinator to judge, not this script.")


def run_k0(arm, nperm, passb, out, path, P):
    """K0 for one arm = rung 15 of cell P: K0a (NEG, at most 1 of 20), K0b (POS, at least 16 of 20). Kk (K0a again
    on NEG0) only if K0a fails. -> the arm's K0 record; the rung goes into P[arm]['15']."""
    res = run_groups([("P", arm, "NEG", 15), ("P", arm, "POS", 15)], nperm, passb)
    neg, pos = res[("P", arm, "NEG", 15)], res[("P", arm, "POS", 15)]
    P.setdefault(arm, {})["15"] = dict(NEG=neg, POS=pos)
    k = dict(K0a=neg["passes"], K0a_ok=neg["passes"] <= MISMATCH_BAR, K0b=pos["passes"],
             K0b_ok=pos["passes"] >= POWER_BAR, edge=EDGE[0] <= pos["passes"] <= EDGE[1],
             K0a_first_partition=neg["first_partition"], Kk=None, mismatch_pool="NEG", reading=None)
    if not k["K0a_ok"]:
        kk = run_groups([("P", arm, "NEG0", 15)], nperm, passb)[("P", arm, "NEG0", 15)]
        P[arm]["15"]["NEG0"] = kk; k["Kk"] = kk["passes"]
        if kk["passes"] <= MISMATCH_BAR:               # reading 2a, fallback F4
            k["mismatch_pool"] = "NEG0"; k["reading"] = R2A.format(arm=arm)
            out["fallbacks"]["F4_" + arm] = "K0a failed and Kk passed: NEG0 replaces NEG in the mismatch bar"
        else:                                          # reading 2b
            k["mismatch_pool"] = None; k["reading"] = R2B.format(arm=arm)
    k["K0_ok"] = k["mismatch_pool"] is not None and k["K0b_ok"]
    say("K0 " + arm, K0a=k["K0a"], K0b=k["K0b"], Kk=k["Kk"], passed=k["K0_ok"])
    dump(out, path)
    return k


def recount_mode():
    path = HERE / "recount.json"; refuse_if_exists("recount.json")
    out = start("recount", path); prepare(out, path)
    out["status"] = "done"; dump(out, path)


def kill():
    path = HERE / "kill.json"; refuse_if_exists("kill.json")
    out = start("kill", path); t0 = time.time()
    prepare(out, path)
    # ---- F2, on synthetic sets, before any real pair
    f2 = out["F2"] = f2_time(); nperm, passb = f2["nperm"], f2["pass_b"]
    if f2["applied"]:
        # PREREG-AMBIGUITY: F2 says "every cell". Kp states its own 999 re-pairings and keeps them; Kc, Kk and every
        # cell take 199 re-pairings and pass at b <= 1.
        out["fallbacks"]["F2"] = f"projection {f2['projected_cpu_hours']} CPU-hours > 6: 199 re-pairings, pass at b <= 1"
    say("F2", projected_cpu_hours=f2["projected_cpu_hours"], applied=f2["applied"]); dump(out, path)
    # ---- Kp: planted known answer
    kp = out["Kp"] = run_groups([("Kp", "B2", "PLANT", 15)], NPERM, PASSB)[("Kp", "B2", "PLANT", 15)]
    say("Kp", passes=kp["passes"], bar=">= 19 of 20")
    if kp["passes"] < KP_BAR:
        out["reading"] = R1_TXT.format(what="Kp"); stop(out, path, "A3: Kp below 19 of 20. " + out["reading"])
    dump(out, path)
    # ---- Kc: code check on real names with outside legends
    kc = out["Kc"] = run_groups([("Kc", "B2", "OUT", 15)], nperm, passb)[("Kc", "B2", "OUT", 15)]
    say("Kc", passes=kc["passes"], bar="<= 1 of 20")
    if kc["passes"] > MISMATCH_BAR:
        out["reading"] = R1_TXT.format(what="Kc"); stop(out, path, "A3: Kc above 1 of 20. " + out["reading"])
    dump(out, path)
    # ---- K0 at m = 15 in arm B2; Kk only if K0a fails; F1: B1, then A, only if the arm before fails K0
    out["P"] = {}; out["K0"] = {}
    for arm in ARMS:
        k = out["K0"][arm] = run_k0(arm, nperm, passb, out, path, out["P"])
        if k["K0_ok"]:
            break
        nxt = ARMS[ARMS.index(arm) + 1] if arm != "A" else None
        out["fallbacks"]["F1_" + arm] = f"arm {arm} fails K0" + (f": the same K0 runs for arm {nxt}" if nxt else "")
    ok = [a for a in out["K0"] if out["K0"][a]["K0_ok"]]
    out["license"] = dict(next=True, k0_arm=ok[0] if ok else None)
    out.update(status="done", seconds=round(time.time() - t0, 1)); dump(out, path)
    print("K0 passes in arm " + ok[0] + "." if ok else "K0 fails in every arm (reading 7b once the ladder is on record).",
          "Next: ladder.", flush=True)


def claimed_m(cell, mism):
    """The smallest m such that every rung from m to 15 meets both bars; None if rung 15 misses."""
    got = None
    for m in RUNGS:
        r = cell.get(str(m))
        if (r is None or mism is None or mism not in r or r[mism]["passes"] > MISMATCH_BAR
                or r["POS"]["passes"] < POWER_BAR):
            break
        got = m
    return got


def ladder():
    kr = load_json("kill.json", "run `kill` first")
    if kr.get("status") != "done" or not kr.get("license", {}).get("next"):
        sys.exit("kill.json is not done (reading 1 or an abort): nothing else is computed")
    path = HERE / "ladder.json"; refuse_if_exists("ladder.json")
    out = start("ladder", path, kr); t0 = time.time()
    prepare(out, path)
    nperm, passb = kr["F2"]["nperm"], kr["F2"]["pass_b"]
    out["fallbacks"] = dict(kr["fallbacks"]); P = out["P"] = kr["P"]; K0 = out["K0"] = kr["K0"]
    for arm in ARMS:                                   # rung 15 for the arms K0 did not reach (reading 2 is per arm)
        if arm not in K0:
            K0[arm] = run_k0(arm, nperm, passb, out, path, P)
    for m in RUNGS[1:]:                                # all three arms run the full ladder, for the record
        groups = [("P", a, p, m) for a in ARMS for p in ("POS", "NEG")]
        groups += [("P", a, "NEG0", m) for a in ARMS if K0[a]["mismatch_pool"] == "NEG0"]      # F4
        for (c, a, p, _), v in run_groups(groups, nperm, passb).items():
            P[a].setdefault(str(m), {})[p] = v
        say("rung", m=m, **{a + "/" + p: P[a][str(m)][p]["passes"] for a in ARMS for p in P[a][str(m)]})
        dump(out, path)
    cl = out["claimed_m"] = {a: claimed_m(P[a], K0[a]["mismatch_pool"]) for a in ARMS}
    ca = out["claiming_arm"] = next((a for a in ARMS if cl[a] is not None), None)
    notes = [K0[a]["reading"] for a in ARMS if K0[a]["reading"]]
    for a in ARMS:
        if K0[a]["edge"]:
            notes.append(f"Reading 9 ({a}): {K0[a]['K0b']} of 20 at the top rung is at the edge and is read as a fail.")
    notes.append("Reading 10 (cell P, rungs 10 and 12 by name): " + "; ".join(
        f"{a} m={m}: POS {P[a][str(m)]['POS']['passes']}/20, NEG {P[a][str(m)]['NEG']['passes']}/20, median right "
        f"values {P[a][str(m)]['POS']['median_right']}" for a in ARMS for m in (10, 12, 15)))
    if ca is None:
        notes.append(R7B + " Per arm: " + "; ".join(
            f"{a} fell on " + ("the mismatch bar (2b)" if K0[a]["mismatch_pool"] is None else "power") for a in ARMS))
    else:
        pos = P[ca][str(cl[ca])]["POS"]; cf, rt = sum(pos["confirmed"]), sum(pos["right"])
        # PREREG-AMBIGUITY: with no confirmed value at the claimed m the value bar is read as missed.
        out["value_bar"] = dict(arm=ca, m=cl[ca], confirmed=cf, right=rt, passed=cf > 0 and rt / cf >= VALUE_BAR)
        if not out["value_bar"]["passed"]:
            notes.append(R8_TXT)
        if cl[ca] == 15 and any(P[ca][str(m)]["POS"]["passes"] < POWER_BAR for m in (10, 12)):
            notes.append("Reading 7a: 10 pairs is at the edge. The arm claims m = 15, which rests on one rung.")
    out["notes"] = notes; out["license"] = dict(next=True)
    out.update(status="done", seconds=round(time.time() - t0, 1)); dump(out, path)
    say("ladder", claimed_m=cl, claiming_arm=ca, value_bar=out.get("value_bar", {}).get("passed"))
    print("Next: cells.", flush=True)


def cells():
    lr = load_json("ladder.json", "run `ladder` first")
    if lr.get("status") != "done":
        sys.exit("ladder.json is not done")
    path = HERE / "cells.json"; refuse_if_exists("cells.json")
    out = start("cells", path, lr); t0 = time.time()
    prepare(out, path)
    kr = load_json("kill.json", "run `kill` first"); nperm, passb = kr["F2"]["nperm"], kr["F2"]["pass_b"]
    out["fallbacks"] = dict(lr["fallbacks"]); ca = out["claiming_arm"] = lr["claiming_arm"]
    C = out["cells"] = {}; cl = out["claimed_m"] = {}; notes = list(lr["notes"])
    if ca is not None:
        # PREREG-AMBIGUITY: under F4 the R cells run NEG0 "in place of NEG" and NEG is not also run there.
        mp = lr["K0"][ca]["mismatch_pool"]; cl["P"] = lr["claimed_m"][ca]
        for cell in ("R1", "C1", "R2", "R3", "C2"):    # the two binding cells first
            mis = "MIS" if cell in ("C1", "C2") else mp
            C[cell] = {}
            for m in RUNGS:
                res = run_groups([(cell, ca, "POS", m), (cell, ca, mis, m)], nperm, passb)
                C[cell][str(m)] = {"POS": res[(cell, ca, "POS", m)], mis: res[(cell, ca, mis, m)]}
            cl[cell] = claimed_m(C[cell], mis)
            say(cell, claimed_m=cl[cell], POS=[C[cell][str(m)]["POS"]["passes"] for m in RUNGS],
                mismatch=[C[cell][str(m)][mis]["passes"] for m in RUNGS])
            dump(out, path)
    # ---- X20: record only, POS only, B2 and the claiming arm
    # PREREG-AMBIGUITY: the Cells table lists B2 for X20 without condition, so B2 runs even when no arm claims.
    x20 = out["X20"] = {}
    for arm in dict.fromkeys(("B2", ca) if ca else ("B2",)):
        res = run_groups([("P", arm, "POS", 20), ("C1", arm, "POS", 20)], nperm, passb)
        x20[arm] = dict(P=res[("P", arm, "POS", 20)], C1=res[("C1", arm, "POS", 20)])
    notes.append("Reading 10 (rung 20, record only): " + "; ".join(
        f"{a} {c}: POS {v['passes']}/20, median right values {v['median_right']}" for a in x20 for c, v in x20[a].items()))
    # ---- readings 3 to 7 (the first whose condition holds governs; reading 2, 8, 9, 10 notes are already listed)
    if ca is None:
        reading = R7B
    else:
        if cl["R1"] is not None and cl["C1"] is not None:
            reading = R3_TXT.format(m=max(cl["P"], cl["R1"], cl["C1"]))
        else:
            reading = R4_TXT
            if cl["R1"] is None and C["R1"]["15"][mp]["passes"] > MISMATCH_BAR:
                reading += " " + R4A
        # PREREG-AMBIGUITY: reading 4b is applied when C1 has no claimed m because its rung-15 mismatch half missed
        # the bar. A miss at a lower rung is listed as a note; ten rungs give chance misses room.
        if cl["C1"] is None and C["C1"]["15"]["MIS"]["passes"] > MISMATCH_BAR:
            reading += " " + R4B; out["arm_C_void"] = True
        low = [m for m in RUNGS if C["C1"][str(m)]["MIS"]["passes"] > MISMATCH_BAR]
        if low:
            notes.append(f"C1 mismatch half above 1 of 20 at rungs {low} (it passes by construction; check arm C).")
        if ca == "B1":
            reading = R5_TXT + " " + reading
        elif ca == "A":
            reading = R6_TXT + " " + reading
        if lr["K0"][ca]["mismatch_pool"] == "NEG0":
            reading += " Under F4 the claim is worded: the names are tied to these legends."
    out["reading"] = reading; out["notes"] = notes
    out.update(status="done", seconds=round(time.time() - t0, 1)); dump(out, path)
    say("cells", claiming_arm=ca, claimed_m=cl)
    print(reading, flush=True); print(R_INDUS, flush=True)


MODES = dict(recount=recount_mode, kill=kill, ladder=ladder, cells=cells)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in MODES:
        sys.exit("usage: run.py recount|kill|ladder|cells   (kill, ladder, cells in this order, each under board/run.sh)")
    a5_hook()
    MODES[mode]()
