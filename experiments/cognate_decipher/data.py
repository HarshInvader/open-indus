"""Data for word-level decipherment controls and the Indus run.

Linear B: DAMOS sign groups (sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl) and the
NeuroDecipher Linear B - Greek cognate list (ext/neurodecipher/linear_b-greek.cog, Luo et al. 2019).
Greek lexicons: the cognate list's Greek forms; Homeric word types (Perseus canonical-greekLit Iliad+Odyssey).
Everything is reduced to the shared 16C+5V alphabet of experiments/decipherability/langdata.py.
"""
import json, re, random, unicodedata, pickle
from collections import Counter
from pathlib import Path
import numpy as np
import wm
from langdata import VIDX, syllabify, clean

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXT = HERE / "ext"
DAMOS = ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
NV = wm.NV

# ---------------------------------------------------------------- Greek
GR = {"α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "d", "η": "e", "θ": "t", "ι": "i", "κ": "k",
      "λ": "l", "μ": "m", "ν": "n", "ξ": "ks", "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t",
      "υ": "u", "φ": "p", "χ": "k", "ψ": "ps", "ω": "o", "f": "v", "ϝ": "v"}


def norm_greek(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    w = re.sub(r"γ(?=[γκχξ])", "n", w)
    return clean("".join(GR.get(c, "") for c in w))


def homer_types(maxn=None):
    cnt = Counter()
    for f in ("homer_001.xml", "homer_002.xml"):
        t = open(EXT / "greek" / f, encoding="utf-8").read()
        t = re.sub(r"<teiHeader.*?</teiHeader>", " ", t, flags=re.S)
        t = re.sub(r"<note.*?</note>", " ", t, flags=re.S)
        t = re.sub(r"<[^>]+>", " ", t)
        for tok in re.findall(r"[Ͱ-Ͽἀ-῿]+", t):
            w = norm_greek(tok)
            if w: cnt[w] += 1
    items = [w for w, _ in cnt.most_common()]
    return items[:maxn] if maxn else items, cnt


# ---------------------------------------------------------------- Linear B
LB_STD = re.compile(r"^([djkmnpqrstwz]?)([aeiou])$")
LBMAP = {"j": "y", "w": "v", "q": "k", "z": "d"}


def lb_value(sy):
    """Linear B transliteration -> shared value id, or -1 (special/undeciphered signs)"""
    m = LB_STD.match(sy)
    if not m: return -1
    c = LBMAP.get(m.group(1), m.group(1))
    return VIDX.get(c + m.group(2), -1)


def _lb_unicode_translit(ch):
    n = unicodedata.name(ch, "")
    if n.startswith("LINEAR B SYLLABLE"):
        return n.split()[-1].lower()
    return None


def lb_cognates():
    """[(lb syllable tuple, set of normalized Greek forms)] from the NeuroDecipher list"""
    out = []
    for i, line in enumerate(open(EXT / "neurodecipher/linear_b-greek.cog", encoding="utf-8")):
        if i == 0: continue
        a, b = line.rstrip("\n").split("\t")
        sy = [_lb_unicode_translit(c) for c in a]
        if not sy or any(s is None for s in sy): continue
        gr = {norm_greek(x) for x in b.split("|") if x != "_"} - {""}
        if gr: out.append((tuple(sy), gr))
    return out


def _clean_acc(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def damos_words():
    words = Counter()
    for l in open(DAMOS):
        r = json.loads(l)
        if not r.get("content"): continue
        for tok in re.split(r"[\s,/]+", _clean_acc(r["content"])):
            if "-" in tok and re.fullmatch(r"[a-z0-9\-]+", tok):
                sy = tuple(x for x in tok.split("-") if x)
                if len(sy) >= 2: words[sy] += 1
    return words


class SignTable:
    def __init__(self): self.id = {}

    def __call__(self, s):
        if s not in self.id: self.id[s] = len(self.id)
        return self.id[s]


def lb_problem(words_sy):
    """syllable-tuples -> (words as sign ids, true value per sign id)"""
    T = SignTable()
    W = [tuple(T(s) for s in w) for w in words_sy]
    true = np.full(len(T.id), -1)
    for s, i in T.id.items(): true[i] = lb_value(s)
    return W, true, T


def lex_values(words, minsyl=1, maxsyl=10):
    out, seen = [], set()
    for w in words:
        if not w or w in seen: continue
        v = [VIDX[x] for x in syllabify(w)]
        if minsyl <= len(v) <= maxsyl:
            seen.add(w); out.append(v)
    return out
