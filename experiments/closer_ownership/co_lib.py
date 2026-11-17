"""Shared code for closer_ownership (task A red team of CONN->dumu, task B closer = ownership/title).

Written independently of experiments/genre_alignment code (not read before this file was written).
Units: distinct legends (references, word tokens) / distinct Indus seal texts (sign tokens).
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, dev_heldout, distinct  # noqa: E402

# ----------------------------------------------------------------- references
KNOWN = ("ur3", "ob")                       # used by genre_alignment
FRESH = ("oakk", "oa", "mb", "ed3b", "lag2", "na", "ma", "nb")   # never aligned to Indus before
STRICT_FRESH = ("mb", "ed3b", "lag2", "na", "ma", "nb")          # not even in genre_alignment's C1 control

SEAL_OF_RE = re.compile(r"^(\{na4\})?(na4-)?kiszib3?(-ne)?$")
SERV_FORMS = {"arad", "arad2", "ir3", "ir11", "geme2", "arad-zu", "arad2-zu", "arad2-da-ni", "arad2-da-ni-ir",
              "arad-da-ni", "arad2-su", "arad2-su2", "arad-su", "arad2-sa", "geme2-zu", "geme2-ni", "ir3-ne-ne"}
KIN_FORMS = {"dumu", "dumu-munus", "dam", "dumu-mi2", "dumu-ni", "dumu-a-ni", "dumu-ni-ir", "dumu-munus-a-ni"}
TITLE_SEED = {"dub-sar", "ensi2", "sanga", "ugula", "szabra", "nu-banda3", "dam-gar3", "sukkal", "sukkal-mah", "gudu4",
              "kurusda", "kuruszda", "muhaldim", "nar", "szu-i", "aga3-us2", "ra2-gaba", "gala", "um-mi-a", "nu-esz3",
              "engar", "sipa", "ka-guru7", "szar2-ra-ab-du", "lu2-kin-gi4-a", "szakkan6", "ha-za-an-nu-u2", "lu2-sag",
              "{lu2}sag", "sza13-dub-ba", "ugula-e2", "dub-sar-mah", "ad-kup4", "simug", "zadim", "nagar", "sag-du5",
              "gal-ukken-na", "gu-za-la2", "i3-du8", "sa12-du5", "lu2-mar-sa", "abgal", "en", "lukur", "nin-dingir"}
CONJ = {"u3"}


def load_refs():
    return [json.loads(l) for l in open(HERE / "data/legends_all.jsonl")]


def derive_titles(refs):
    """Data-driven title list from KNOWN cultures only (never from fresh data): frequent words that are never
    legend-initial and stand right after the first word in >=50% of their occurrences."""
    cnt, init, pos2 = Counter(), Counter(), Counter()
    for r in refs:
        if r["group"] not in KNOWN: continue
        w = r["words"]
        for i, x in enumerate(w):
            cnt[x] += 1
            if i == 0: init[x] += 1
            if i == 1: pos2[x] += 1
    out = set()
    for x, n in cnt.items():
        if n < 5 or init[x] > 0 or x.startswith("{d}") or x in ("lugal", "dingir") or x in SERV_FORMS or x in KIN_FORMS: continue
        if SEAL_OF_RE.match(x) or x in CONJ: continue
        if pos2[x] / n >= 0.5: out.add(x)
    return out


_TITLES = None


def titles():
    global _TITLES
    if _TITLES is None:
        _TITLES = TITLE_SEED | derive_titles(load_refs())
    return _TITLES


def word_class(w, group, prev=None):
    if SEAL_OF_RE.match(w): return "SEAL_OF"
    if group in ("mb", "na", "ma", "nb") and w == "na4": return "SEAL_OF"
    if w in SERV_FORMS: return "SERV"
    if w in KIN_FORMS: return "KIN"
    if group in ("mb", "na", "ma", "nb") and w == "a": return "KIN"   # A = maru 'son' in MB/NA legends
    if w in CONJ: return "CONJ"
    if w in titles(): return "TITLE"
    if w == "lugal" or w == "dingir" or w.startswith("{d}"): return "LORD"
    return "NAME"


def tag_legend(words, group):
    """gold slot labels per word (rule-based). NAME after KIN = FATHER; NAME/LORD after SERV = LORD;
    first NAME = OWNER; other NAME = NAME."""
    cl = [word_class(w, group) for w in words]
    out = []; seen_owner = False; mode = None
    for c in cl:
        if c in ("SEAL_OF", "SERV", "KIN", "CONJ", "TITLE"):
            out.append(c); mode = c if c in ("SERV", "KIN") else None; continue
        if mode == "KIN": out.append("FATHER"); continue
        if mode == "SERV": out.append("LORD"); continue
        if c == "LORD": out.append("LORD"); continue
        if not seen_owner: out.append("OWNER"); seen_owner = True
        else: out.append("NAME")
    return out


def ref_corpus(groups, refs=None):
    """list of (tokens, classes, slots) for distinct legends of the groups. tokens are words; classes = word_class."""
    refs = refs or load_refs()
    C = []
    for r in refs:
        if r["group"] in groups:
            w = r["words"]
            C.append(dict(tok=w, cls=[word_class(x, r["group"]) for x in w], slot=tag_legend(w, r["group"]), group=r["group"]))
    return C


# ----------------------------------------------------------------- Indus
OPEN_M = {"M267", "M391", "M293", "M150"}
CONN_M = {"M99", "M123"}
CLOSER_M = {"M342", "M211", "M12", "M14", "M15", "M254", "M169", "M60", "M66", "M68", "M71", "M73"}  # lexicon role CLOSER >=0.5 (grade A/B or hand) + bracketed fish
POST_M = {"M176", "M1"}


def _clean(seq):
    if "#" in seq: return None
    s = [x for x in seq if x != "|"]
    return s or None


def indus_seals(split):
    """distinct complete-ish M77 seal texts (object_type seal), break-free, line breaks dropped."""
    dev, ho = dev_heldout(version=2)
    T = dev if split == "dev" else ho
    out, seen = [], set()
    for t in T:
        if t["object_type"] != "seal": continue
        s = _clean(t["seq"])
        if not s: continue
        k = " ".join(s)
        if k in seen: continue
        seen.add(k); out.append(s)
    return out


M77_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}


def bridge():
    b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    return {"W" + w.zfill(3): ["M%d" % m for m in v["M"]] for w, v in b.items()}


def icit_newsite_seals():
    """distinct break-free ICIT seal texts (SEAL*) from sites absent from M77 (and not 'Unknown'), in W signs."""
    out, seen = [], set()
    for t in icit_texts():
        if not t["type"].startswith("SEAL"): continue
        if t["site"] in M77_SITES_ICIT or t["site"] in ("Unknown", ""): continue
        s = _clean(t["seq"])
        if not s: continue
        k = " ".join(s)
        if k in seen: continue
        seen.add(k); out.append(s)
    return out


W_SETS = None


def w_sets():
    """W-sign versions of the Indus sign classes via the bridge (W sign belongs to a class if ANY of its M readings does,
    except where it would merge classes)."""
    global W_SETS
    if W_SETS is None:
        b = bridge(); d = defaultdict(set)
        for w, ms in b.items():
            for name, S in (("OPEN", OPEN_M), ("CONN", CONN_M), ("CLOSER", CLOSER_M), ("POST", POST_M)):
                if ms[0] in S: d[name].add(w)     # first listed M reading, as functional_reading did
        W_SETS = dict(d)
    return W_SETS


def indus_class(sign):
    if sign.startswith("W"):
        for k, S in w_sets().items():
            if sign in S: return k
        return "CORE"
    if sign in OPEN_M: return "OPEN"
    if sign in CONN_M: return "CONN"
    if sign in CLOSER_M: return "CLOSER"
    if sign in POST_M: return "POST"
    return "CORE"


# ----------------------------------------------------------------- token-level features (label-free)
FEATS = ["edge", "dedge", "s2", "s3", "r_short", "r_long", "ndiv"]   # mirror-invariant (no reading direction)
POSF = ["ini", "fin"]                                                 # direction-dependent, reported only


def token_features(legends, is_target, rng=None, ndiv_n=30, ndiv_reps=20):
    """legends: list of token lists. is_target(legend, i) -> bool. Returns dict of features or None."""
    rng = rng or np.random.default_rng(0)
    N = len(legends)
    lens = np.array([len(l) for l in legends])
    q75 = np.quantile(lens, 0.75)
    occ, has = [], np.zeros(N, bool)
    for j, l in enumerate(legends):
        n = len(l)
        for i in range(n):
            if is_target(l, i):
                has[j] = True
                left = l[i - 1] if i > 0 else None
                right = l[i + 1] if i < n - 1 else None
                occ.append((i, n, left, right))
    if len(occ) < 5: return None
    occ_i = np.array([o[0] for o in occ]); occ_n = np.array([o[1] for o in occ])
    edge = np.mean((occ_i == 0) | (occ_i == occ_n - 1))
    half = np.maximum((occ_n - 1) / 2, 1e-9)
    dd = np.where(occ_n > 1, np.minimum(occ_i, occ_n - 1 - occ_i) / half, 0.0)
    L = lens[has]
    p = has.mean()
    sh = lens <= 2; lo = lens >= max(q75, 3)
    r_short = (has[sh].mean() if sh.any() else 0) / p
    r_long = (has[lo].mean() if lo.any() else 0) / p
    nb = [x for o in occ for x in (o[2], o[3]) if x is not None]
    if len(nb) >= ndiv_n:
        nd = np.mean([len({nb[k] for k in rng.choice(len(nb), ndiv_n, replace=False)}) / ndiv_n for _ in range(ndiv_reps)])
    else:
        nd = len(set(nb)) / max(len(nb), 1)
    return dict(edge=edge, dedge=float(dd.mean()), s2=float(np.mean(L <= 2)), s3=float(np.mean(L <= 3)),
                r_short=float(r_short), r_long=float(r_long), ndiv=float(nd),
                ini=float(np.mean(occ_i == 0)), fin=float(np.mean(occ_i == occ_n - 1)),
                n_occ=len(occ), n_leg=int(has.sum()), occupancy=float(p))


def class_target(cls_lists, name):
    """is_target over a reference corpus by gold word class; returns closure using parallel class lists."""
    def f(l, i, _c={id(x): y for x, y in cls_lists}):
        return _c[id(l)][i] == name
    return f


def ref_class_features(C, classes=("SEAL_OF", "TITLE", "SERV", "KIN", "LORD", "NAME"), rng=None):
    legs = [c["tok"] for c in C]
    out = {}
    for name in classes:
        m = {id(c["tok"]): c["cls"] for c in C}
        f = token_features(legs, lambda l, i, m=m, name=name: m[id(l)][i] == name, rng=rng)
        if f is not None: out[name] = f
    return out


def word_type_features(legends, min_n=8, rng=None):
    cnt = Counter(x for l in legends for x in l)
    out = {}
    for w, n in cnt.items():
        if n >= min_n:
            f = token_features(legends, lambda l, i, w=w: l[i] == w, rng=rng)
            if f: out[w] = f
    return out


def zscaler(feature_dicts, feats=FEATS):
    X = np.array([[d[k] for k in feats] for d in feature_dicts])
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-9] = 1.0
    return mu, sd


def vec(d, feats=FEATS):
    return np.array([d[k] for k in feats])


def dist(a, b, mu, sd, feats=FEATS):
    return float(np.linalg.norm((vec(a, feats) - vec(b, feats)) / sd) / np.sqrt(len(feats)))


# ----------------------------------------------------------------- slot-level (runs)
def runs_of(labels, fillers):
    out = []
    for lab, f in zip(labels, fillers):
        if out and out[-1][0] == lab: out[-1][1].append(f)
        else: out.append([lab, [f]])
    return out


SLOTF = ["occ", "mpos", "first", "last", "rlen", "types20", "short", "recur", "alone", "longdiff", "nameonly"]
SLOTF_NOPOS = ["occ", "rlen", "types20", "short", "recur", "alone", "longdiff", "nameonly", "edge_s"]


def slot_features(legs_runs, name, rng=None, name_slot=None):
    """legs_runs: list of run lists [(label, fillers)]. Features of slot `name`."""
    rng = rng or np.random.default_rng(0)
    N = len(legs_runs); nr = np.array([len(r) for r in legs_runs])
    pres = np.array([any(l == name for l, _ in r) for r in legs_runs])
    if pres.sum() < 10: return None
    pos, first, last, rl, fill, recur, alone, edge = [], [], [], [], [], [], [], []
    nameonly = []
    for r, p in zip(legs_runs, pres):
        if not p: continue
        k = [j for j, (l, _) in enumerate(r) if l == name]
        recur.append(len(k) > 1); alone.append(len(r) == 1)
        if name_slot is not None:
            nameonly.append(len(r) == 2 and {l for l, _ in r} == {name, name_slot})
        for j in k:
            n = len(r)
            pos.append(j / (n - 1) if n > 1 else 0.5); first.append(j == 0); last.append(j == n - 1)
            edge.append(j == 0 or j == n - 1)
            rl.append(len(r[j][1])); fill.append(" ".join(r[j][1]))
    fill = np.array(fill)
    t20 = np.mean([len(set(rng.choice(fill, 20, replace=len(fill) < 20))) for _ in range(30)])
    cnt = Counter(fill)
    sh = nr <= 2; lg = nr >= 4
    return dict(occ=float(pres.mean()), mpos=float(np.mean(pos)), first=float(np.mean(first)), last=float(np.mean(last)),
                rlen=float(np.mean(rl)), types20=float(t20), top=cnt.most_common(1)[0][1] / len(fill),
                short=float(pres[sh].mean()) if sh.any() else 0.0, recur=float(np.mean(recur)), alone=float(np.mean(alone)),
                longdiff=float((pres[lg].mean() if lg.any() else 0) - (pres[sh].mean() if sh.any() else 0)),
                nameonly=float(np.mean(nameonly)) if nameonly else 0.0, edge_s=float(np.mean(edge)), n=int(pres.sum()))
