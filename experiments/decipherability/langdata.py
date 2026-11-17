"""Real-language material for planted-answer decipherment experiments.

Every language is reduced to ONE shared phoneme alphabet, then written as akshara-like units:
  CV, bare C (consonant with no following vowel: virama-style), bare V.
Shared alphabet: consonants p b t d k g c j m n s h r l y v (16), vowels a e i o u (5) -> 101 possible
syllable values. Length, aspiration, retroflexion and gemination are not written (as in Linear B /
many early scripts). This keeps every language on the same key space, so scores are comparable.

Languages (planted) and the decipherer's knowledge sources:
  san  Sanskrit  names: Rigveda names+epithets phrases (real)     K1: MW headwords + sa.wikipedia   K2: Pali+Prakrit lexicons
  tam  Tamil     names: synthetic template over Tamil lemmas      K1: ta.wikipedia + Tamil lemmas   K2: Malayalam lexicon (+ml.wikipedia)
  sux  Sumerian  names: Ur III seal legends (real, CDLI)          K1: Sumerian word-form lexicon    K2: none (isolate)
  lat  Latin     names: EDH Italian inscriptions, 1-3 word chunks K1: Caesar, Bellum Gallicum       K2: it.wikipedia
  fin  Finnish   names: synthetic template over Kalevala names    K1: fi.wikipedia                  K2: et.wikipedia
Prose genre: lat Caesar, fin Kalevala, san sa.wikipedia, tam ta.wikipedia (chopped into lines).
"""
import json, re, random, unicodedata, pickle
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw"
SRC = ROOT / "sources/paragorth_Indus-/data"
EXT = ROOT / "experiments/language/ext"

CONS = "pbtdkgcjmnshrlyv"
VOWS = "aeiou"
VALUES = [c + v for c in CONS for v in VOWS] + list(CONS) + list(VOWS)   # 80 + 16 + 5 = 101
VIDX = {v: i for i, v in enumerate(VALUES)}
ALLOWED = set(CONS + VOWS)


def dedouble(w):
    return re.sub(r"(.)\1+", r"\1", w)


def clean(w):
    w = "".join(ch for ch in w if ch in ALLOWED)
    return dedouble(w)


def syllabify(w):
    """normalized word -> list of value strings"""
    out, i = [], 0
    while i < len(w):
        ch = w[i]
        if ch in CONS:
            if i + 1 < len(w) and w[i + 1] in VOWS:
                out.append(ch + w[i + 1]); i += 2
            else:
                out.append(ch); i += 1
        else:
            out.append(ch); i += 1
    return out


# ---------------- normalizers ----------------
# Indic scripts share the ISCII layout: offset within the Unicode block
_IV = {0x05: "a", 0x06: "a", 0x07: "i", 0x08: "i", 0x09: "u", 0x0A: "u", 0x0B: "ri", 0x0C: "li", 0x0D: "e",
       0x0E: "e", 0x0F: "e", 0x10: "e", 0x11: "o", 0x12: "o", 0x13: "o", 0x14: "o"}
_IC = {0x15: "k", 0x16: "k", 0x17: "g", 0x18: "g", 0x19: "n", 0x1A: "c", 0x1B: "c", 0x1C: "j", 0x1D: "j", 0x1E: "n",
       0x1F: "t", 0x20: "t", 0x21: "d", 0x22: "d", 0x23: "n", 0x24: "t", 0x25: "t", 0x26: "d", 0x27: "d", 0x28: "n",
       0x29: "n", 0x2A: "p", 0x2B: "p", 0x2C: "b", 0x2D: "b", 0x2E: "m", 0x2F: "y", 0x30: "r", 0x31: "r", 0x32: "l",
       0x33: "l", 0x34: "l", 0x35: "v", 0x36: "s", 0x37: "s", 0x38: "s", 0x39: "h"}
_IS = {0x3E: "a", 0x3F: "i", 0x40: "i", 0x41: "u", 0x42: "u", 0x43: "ri", 0x44: "ri", 0x46: "e", 0x47: "e", 0x48: "e",
       0x4A: "o", 0x4B: "o", 0x4C: "o"}
_BLOCKS = {0x0900: "deva", 0x0B80: "taml", 0x0D00: "mlym"}


def indic_words(text):
    """transliterate Devanagari / Tamil / Malayalam text -> list of normalized words"""
    words, cur, pend = [], [], False   # pend: last char is a consonant with inherent vowel pending
    def flush():
        nonlocal cur, pend
        if pend: cur.append("a")
        if cur: words.append("".join(cur))
        cur, pend = [], False
    for ch in text:
        o = ord(ch); base = o & ~0x7F; off = o - base
        if base not in _BLOCKS:
            flush(); continue
        tamil = base == 0x0B80
        if off in _IC:
            if pend: cur.append("a")
            cur.append(_IC[off]); pend = True
        elif off in _IS:
            cur.append(_IS[off]); pend = False
        elif off == 0x4D:       # virama / pulli
            pend = False
        elif off in _IV:
            if pend: cur.append("a")
            cur.append(_IV[off]); pend = False
        elif off in (0x01, 0x02):
            if pend: cur.append("a")
            cur.append("m"); pend = False
        elif off == 0x03:
            if pend: cur.append("a")
            cur.append("h" if not tamil else ""); pend = False
        elif off in (0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F) and base == 0x0D00:  # Malayalam chillu letters
            if pend: cur.append("a")
            cur.append({0x7A: "n", 0x7B: "n", 0x7C: "r", 0x7D: "l", 0x7E: "l", 0x7F: "k"}[off]); pend = False
        elif off in (0x57, 0x3C, 0x00):
            continue
        else:
            flush()
    flush()
    return [w for w in (clean(x) for x in words) if w]


def _strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm_iast(w):
    w = w.lower()
    w = w.replace("ṛ", "ri").replace("ṝ", "ri").replace("ḷ", "li").replace("ai", "e").replace("au", "o")
    w = re.sub(r"(?<=[kgcjtdpbṭḍ])h", "", w)
    w = _strip_acc(w)            # ā->a ś->s ṣ->s ṭ->t ṃ->m ṇ->n ...
    return clean(w)


SLP = {"A": "a", "I": "i", "U": "u", "f": "ri", "F": "ri", "x": "li", "X": "li", "E": "e", "O": "o", "M": "m", "H": "h",
       "K": "k", "G": "g", "N": "n", "C": "c", "J": "j", "Y": "n", "w": "t", "W": "t", "q": "d", "Q": "d", "R": "n",
       "T": "t", "D": "d", "P": "p", "B": "b", "S": "s", "z": "s", "~": "m"}


def norm_slp1(w):
    return clean("".join(SLP.get(ch, ch) for ch in w))


def norm_latin(w):
    w = _strip_acc(w.lower())
    for a, b in [("qu", "ku"), ("ph", "p"), ("th", "t"), ("ch", "k"), ("x", "ks"), ("c", "k"), ("q", "k"),
                 ("z", "s"), ("y", "i"), ("f", "v"), ("w", "v"), ("j", "i")]:
        w = w.replace(a, b)
    return clean(w)


def norm_italian(w):
    w = _strip_acc(w.lower())
    for a, b in [("gli", "li"), ("gn", "n"), ("ch", "k"), ("gh", "g"), ("qu", "ku"), ("h", "")]:
        w = w.replace(a, b)
    w = re.sub(r"sc(?=[ei])", "s", w)
    w = re.sub(r"ci(?=[aou])", "c", w); w = re.sub(r"gi(?=[aou])", "j", w)
    w = re.sub(r"g(?=[ei])", "j", w)
    w = re.sub(r"c(?![ei])", "k", w)
    for a, b in [("z", "s"), ("f", "v"), ("x", "ks"), ("y", "i"), ("w", "v"), ("j", "j")]:
        w = w.replace(a, b)
    return clean(w)


def norm_finnic(w):
    w = w.lower()
    for a, b in [("ä", "a"), ("ö", "o"), ("ü", "u"), ("õ", "o"), ("å", "o"), ("y", "u"), ("š", "s"), ("ž", "s"),
                 ("z", "s"), ("f", "v"), ("w", "v"), ("x", "ks"), ("q", "k"), ("c", "k")]:
        w = w.replace(a, b)
    return clean(_strip_acc(w))


def norm_ascii_indic(w):
    """paragorth ASCII-folded Malayalam / Pali / Prakrit / Kannada / Telugu / Santali lexicons"""
    w = w.lower()
    for a, b in [("zh", "l"), ("sh", "s"), ("ch", "c"), ("kh", "k"), ("gh", "g"), ("jh", "j"), ("th", "t"),
                 ("dh", "d"), ("ph", "p"), ("bh", "b"), ("ai", "e"), ("au", "o"), ("f", "v"), ("z", "s"),
                 ("x", "ks"), ("q", "k"), ("w", "v")]:
        w = w.replace(a, b)
    return clean(w)


def norm_sux(w):
    w = w.lower()
    if "x" in w or "..." in w: return ""
    w = re.sub(r"\{[^}]*\}", "", w)
    w = w.replace("sz", "s").replace("s,", "s").replace("t,", "t").replace("ĝ", "g").replace("g~", "g")
    w = w.replace("j", "g").replace("ŋ", "g").replace("š", "s").replace("ḫ", "h")
    w = re.sub(r"[0-9_\-\.\[\]#!?<>()]", "", w)
    return clean(_strip_acc(w))


def latin_script_words(text, norm):
    return [w for w in (norm(t) for t in re.findall(r"[^\W\d_]+", text)) if w]


# ---------------- loaders ----------------
def _gutenberg_body(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    a = t.find("*** START"); b = t.find("*** END")
    if a >= 0: t = t[t.find("\n", a):]
    if b >= 0: t = t[:t.find("*** END")]
    return t


def _lines(p):
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]


def _chunk_texts(seqs, rng, lo=1, hi=3):
    out = []
    for s in seqs:
        i = 0
        while i < len(s):
            k = rng.randint(lo, hi); out.append(s[i:i + k]); i += k
    return out


def _sentences_to_texts(words, rng, lo=4, hi=12):
    """running text -> word lists of 4-12 words (knowledge corpora)"""
    out, i = [], 0
    while i < len(words):
        k = rng.randint(lo, hi); out.append(words[i:i + k]); i += k
    return out


def build_all():
    rng = random.Random(7)
    L = {}
    # ---- Sanskrit
    rv = [[norm_iast(w) for w in l.split()] for l in _lines(EXT / "eqstats/rv_names_epithets.txt")]
    rv = [[w for w in s if w] for s in rv]
    mw = [norm_slp1(w) for w in _lines(EXT / "skt/mw_headwords.txt")]
    sa_wiki = indic_words(open(RAW / "wiki_sa.txt", encoding="utf-8").read())
    pali = [norm_ascii_indic(w) for w in _lines(SRC / "derived/lex_pali.txt")] + \
           [norm_ascii_indic(w) for w in _lines(SRC / "derived/lex_prakrit.txt")]
    L["san"] = dict(name_src=_chunk_texts(rv, rng), real_names=True,
                    prose=sa_wiki,
                    K1=[[w] for w in mw if w] + _sentences_to_texts(sa_wiki, rng),
                    K2=[[w] for w in pali if w])
    # ---- Tamil
    ta_wiki = indic_words(open(RAW / "wiki_ta.txt", encoding="utf-8").read())
    ta_lem = [w for l in _lines(EXT / "wikt/Tamil_lemmas.txt") for w in indic_words(l)]
    mal = [norm_ascii_indic(w) for w in _lines(SRC / "derived/lex_malayalam.txt")]
    ml_wiki = indic_words(open(RAW / "wiki_ml.txt", encoding="utf-8").read()) if (RAW / "wiki_ml.txt").exists() else []
    L["tam"] = dict(name_src=None, real_names=False, name_pool=ta_lem, suffixes=["an", "in", "uku", "ar", "il"],
                    prose=ta_wiki,
                    K1=_sentences_to_texts(ta_wiki, rng),   # lemmas excluded: they are the synthetic name pool
                    K2=[[w] for w in mal if w] + _sentences_to_texts(ml_wiki, rng))
    # ---- Sumerian
    ur3 = [json.loads(l)["seq"] for l in open(SRC / "codelib/ur3_legends.jsonl")]
    ur3 = [s for s in ([norm_sux(w) for w in t] for t in ur3) if all(s) and s]
    sux = [norm_sux(w) for w in _lines(SRC / "derived/lex_sumerian.txt")]
    L["sux"] = dict(name_src=ur3, real_names=True, prose=None,
                    K1=[[w] for w in sux if w], K2=None)
    # ---- Latin
    edh = [json.loads(l)["seq"] for l in open(SRC / "codelib/latin_edh.jsonl")]
    edh = [[norm_latin(w) for w in s if not re.fullmatch(r"[ivxlcdm]+", w) or len(w) > 4] for s in edh]
    edh = [[w for w in s if w] for s in edh]
    caes = latin_script_words(_gutenberg_body(RAW / "caesar.txt"), norm_latin)
    it_wiki = latin_script_words(open(RAW / "wiki_it.txt", encoding="utf-8").read(), norm_italian) \
        if (RAW / "wiki_it.txt").exists() else []
    L["lat"] = dict(name_src=_chunk_texts(edh, rng), real_names=True, prose=caes,
                    K1=_sentences_to_texts(caes, rng), K2=_sentences_to_texts(it_wiki, rng) or None)
    # ---- Finnish
    kal_raw = _gutenberg_body(RAW / "kalevala.txt")
    names = []
    for line in kal_raw.splitlines():
        toks = re.findall(r"[^\W\d_]+", line)
        names += [t for t in toks[1:] if t[:1].isupper()]
    kal = latin_script_words(kal_raw, norm_finnic)
    fi_wiki = latin_script_words(open(RAW / "wiki_fi.txt", encoding="utf-8").read(), norm_finnic)
    et_wiki = latin_script_words(open(RAW / "wiki_et.txt", encoding="utf-8").read(), norm_finnic)
    L["fin"] = dict(name_src=None, real_names=False, name_pool=[norm_finnic(n) for n in names if norm_finnic(n)],
                    title_src=kal, suffixes=["n", "le", "sta", "na", "lta"],
                    prose=kal, K1=_sentences_to_texts(fi_wiki, rng), K2=_sentences_to_texts(et_wiki, rng))
    # Proto-Dravidian reconstructions (for the Indus run only)
    pd = []
    for l in _lines(EXT / "wikt/Proto-Dravidian_lemmas.txt"):
        w = l.split("/")[-1]
        w = w.replace("V", "a").replace("H", "").replace("ṯ", "t").replace("ḻ", "l").replace("ṉ", "n")
        w = norm_iast(re.sub(r"[()\-*]", "", w))
        if w: pd.append(w)
    L["_pdr"] = dict(K1=[[w] for w in pd])
    return L


_CACHE = HERE / "out" / "langdata.pkl"


def load():
    if _CACHE.exists():
        return pickle.load(open(_CACHE, "rb"))
    _CACHE.parent.mkdir(exist_ok=True)
    L = build_all()
    pickle.dump(L, open(_CACHE, "wb"))
    return L


# ---------------- planted name/title texts ----------------
def name_texts(lang, L, n_texts, rng, formula_min=10):
    """Return distinct name/title-like word texts.
    Real corpora (san, sux, lat): real texts first, then template recombination (keep formula words,
    replace rare 'name' words by draws from the empirical name pool).
    Synthetic (tam, fin): [title] name[+suffix] [title] templates over real words."""
    d = L[lang]
    out, seen = [], set()
    def add(t):
        k = " ".join(t)
        if t and k not in seen:
            seen.add(k); out.append(t)
    if d["real_names"]:
        src = list(d["name_src"]); rng.shuffle(src)
        cnt = Counter(w for t in src for w in t)
        pool = [w for w in cnt if cnt[w] < formula_min]
        pw = list(__import__("itertools").accumulate(cnt[w] for w in pool))
        for t in src:
            if len(out) >= n_texts: break
            add(t)
        tries = 0
        while len(out) < n_texts and tries < 50 * n_texts:
            tries += 1
            t = rng.choice(src)
            t = [w if cnt[w] >= formula_min else rng.choices(pool, cum_weights=pw)[0] for w in t]
            add(t)
    else:
        pool = list(dict.fromkeys(w for w in d["name_pool"] if 2 <= len(syllabify(w)) <= 5))
        rng2 = random.Random(11); rng2.shuffle(pool)
        pw = list(__import__("itertools").accumulate(1.0 / (i + 1) ** 0.9 for i in range(len(pool))))
        tsrc = d.get("title_src") or d["prose"]
        tc = Counter(w for w in tsrc if 2 <= len(syllabify(w)) <= 4)
        titles = [w for w, _ in tc.most_common(400)][::10][:40]
        tw = list(__import__("itertools").accumulate(1.0 / (i + 1) for i in range(len(titles))))
        suf = d["suffixes"]
        tries = 0
        while len(out) < n_texts and tries < 50 * n_texts:
            tries += 1
            t = []
            if rng.random() < 0.35: t.append(rng.choices(titles, cum_weights=tw)[0])
            nm = rng.choices(pool, cum_weights=pw)[0]
            if rng.random() < 0.3: nm = nm + rng.choice(suf)
            t.append(clean(nm))
            if rng.random() < 0.3: t.append(rng.choices(pool, cum_weights=pw)[0])
            if rng.random() < 0.4: t.append(rng.choices(titles, cum_weights=tw)[0])
            add(t)
    return out


if __name__ == "__main__":
    L = load()
    for k, d in L.items():
        info = {kk: (len(v) if isinstance(v, list) else v) for kk, v in d.items() if kk not in ("suffixes",)}
        print(k, info)
    rng = random.Random(0)
    for lang in ["san", "tam", "sux", "lat", "fin"]:
        T = name_texts(lang, L, 6, rng)
        print(lang, [" ".join("-".join(syllabify(w)) for w in t) for t in T])
        if L[lang]["prose"]: print("   prose:", " ".join(L[lang]["prose"][1000:1012]))
        print("   K1:", L[lang]["K1"][500:503], " K2:", (L[lang]["K2"] or [[]])[300:302])
