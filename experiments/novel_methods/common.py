"""Shared helpers for experiments/novel_methods.

Texts are DISTINCT sequences (corpus.load.dev_heldout), line breaks '|' removed
(reading order is continuous across lines), texts containing a break '#' dropped
(a break would fake insertions/deletions in alignment-based methods).
"""
import json, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, icit_texts, m77_texts, distinct  # noqa: E402

OUT = Path(__file__).resolve().parent


def clean(seq):
    if "#" in seq:
        return None
    s = tuple(x for x in seq if x != "|")
    return s if s else None


def load_split():
    dev, ho = dev_heldout()
    D = sorted({c for t in dev if (c := clean(t["seq"]))})
    H = sorted({c for t in ho if (c := clean(t["seq"]))} - set(D))
    return D, H


def load_split_records():
    dev, ho = dev_heldout()
    return ([t for t in dev if clean(t["seq"])], [t for t in ho if clean(t["seq"])])


M77_SITES = {t["site"] for t in m77_texts()}


def icit_external():
    """ICIT texts from sites absent from M77, mapped to Mahadevan numbers via the
    176-sign bridge. Only texts whose every sign is bridged are kept. Returns
    (texts_as_M_tuples, site_counter)."""
    br = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    w2m = {}
    for w, v in br.items():
        if v.get("M"):
            w2m["W%03d" % int(w)] = "M%d" % v["M"][0]
    out, sites = set(), Counter()
    norm = lambda s: s.lower().replace("-", "").replace(" ", "")
    m77n = {norm(s) for s in M77_SITES}
    for t in distinct(icit_texts()):
        if norm(t["site"]) in m77n or "#" in t["seq"]:
            continue
        seq = [s for s in t["seq"] if s != "|"]
        if not seq or not all(s in w2m for s in seq):
            continue
        tup = tuple(w2m[s] for s in seq)
        if tup not in out:
            out.add(tup); sites[t["site"]] += 1
    return sorted(out), sites


# ---------------------------------------------------------------- nulls
class Markov:
    """Order-k Markov generator fitted on a list of texts, sampling texts of an
    exact requested length (backward messages over states). k=1 = bigram null."""

    def __init__(self, texts, k=1, alpha=0.0):
        self.k = k
        self.trans = defaultdict(Counter)
        for t in texts:
            ctx = ("<s>",) * k
            for s in list(t) + ["</s>"]:
                self.trans[ctx][s] += 1
                ctx = (ctx + (s,))[-k:]
        self.cache = {}

    def _p(self, ctx):
        c = self.trans.get(ctx)
        if not c:
            return [], np.array([])
        items = list(c.items())
        syms = [a for a, _ in items]
        w = np.array([b for _, b in items], float)
        return syms, w / w.sum()

    def _beta(self, ctx, n):
        # probability that from ctx we emit exactly n more symbols then </s>
        key = (ctx, n)
        if key in self.cache:
            return self.cache[key]
        syms, p = self._p(ctx)
        tot = 0.0
        for s, q in zip(syms, p):
            if s == "</s>":
                if n == 0:
                    tot += q
            elif n > 0:
                tot += q * self._beta((ctx + (s,))[-self.k:], n - 1)
        self.cache[key] = tot
        return tot

    def sample(self, n, rng):
        ctx = ("<s>",) * self.k
        if self._beta(ctx, n) == 0:
            return None
        out = []
        for i in range(n):
            syms, p = self._p(ctx)
            w = np.array([0.0 if s == "</s>" else q * self._beta((ctx + (s,))[-self.k:], n - i - 1)
                          for s, q in zip(syms, p)])
            w /= w.sum()
            s = syms[rng.choice(len(syms), p=w)]
            out.append(s)
            ctx = (ctx + (s,))[-self.k:]
        return tuple(out)


def null_corpus(texts, rng, k=1, model=None):
    """Distinct-text corpus of the same size and length distribution, from an
    order-k Markov model of `texts`."""
    model = model or Markov(texts, k)
    lens = [len(t) for t in texts]
    out = set()
    tries = 0
    while len(out) < len(texts) and tries < 50 * len(texts):
        tries += 1
        t = model.sample(lens[len(out) % len(lens)] if False else rng.choice(lens), rng)
        if t:
            out.add(t)
    return sorted(out)


def shuffle_corpus(texts, rng):
    """Unigram null: shuffle all tokens across texts, keep lengths, dedupe."""
    toks = [s for t in texts for s in t]
    rng.shuffle(toks)
    out, i = [], 0
    for t in texts:
        out.append(tuple(toks[i:i + len(t)])); i += len(t)
    return sorted(set(out))


# ------------------------------------------------- comparison corpora
def _syllabify(name):
    """Crude orthographic CV(C) syllabification of a lower-case name."""
    v = "aeiouy"
    name = re.sub(r"[^a-z]", "", name.lower())
    sylls, cur, i = [], "", 0
    while i < len(name):
        cur += name[i]
        if name[i] in v:
            # take one following consonant if followed by another consonant or end
            j = i + 1
            while j < len(name) and name[j] in v:
                cur += name[j]; j += 1
            if j < len(name) and (j + 1 >= len(name) or name[j + 1] not in v):
                cur += name[j]; j += 1
            sylls.append(cur); cur = ""; i = j
            continue
        i += 1
    if cur:
        if sylls:
            sylls[-1] += cur
        else:
            sylls.append(cur)
    return sylls


def names_corpus(n_texts, rng):
    """Synthetic logo-syllabic SEAL LEGENDS from a real personal-name list
    (/usr/share/dict/propernames). Template (Old Akkadian / Ur III seal style):
        [TITLE]? NAME [ 'son-of' NAME ]? [OCCUPATION]? [GOD-servant]?
    Names are written syllabically (one token per syllable); titles, occupations
    and 'son-of' are single logograms. Known answer: slots and fillers."""
    names = [l.strip() for l in open("/usr/share/dict/propernames") if l.strip()]
    sy = [tuple("s:" + x for x in _syllabify(nm)) for nm in names]
    sy = [s for s in sy if 1 <= len(s) <= 4]
    zipf = lambda k: (lambda w: w / w.sum())(1.0 / np.arange(1, k + 1) ** 1.1)
    titles = ["L:title%d" % i for i in range(8)]
    occs = ["L:occ%d" % i for i in range(25)]
    gods = ["L:god%d" % i for i in range(6)]
    pn = zipf(len(sy)); rng_perm = rng.permutation(len(sy)); sy = [sy[i] for i in rng_perm]
    pt, po, pg = zipf(8), zipf(25), zipf(6)
    out = set()
    while len(out) < n_texts:
        t = []
        if rng.random() < 0.25: t.append(titles[rng.choice(8, p=pt)])
        t += list(sy[rng.choice(len(sy), p=pn)])
        if rng.random() < 0.35:
            t.append("L:son"); t += list(sy[rng.choice(len(sy), p=pn)])
        if rng.random() < 0.4: t.append(occs[rng.choice(25, p=po)])
        if rng.random() < 0.15: t += ["L:servant", gods[rng.choice(6, p=pg)]]
        if 1 <= len(t) <= 14:
            out.add(tuple(t))
    return sorted(out)


def slotcode_corpus(n_texts, rng):
    """Synthetic NON-LINGUISTIC administrative code (licence plate / ICD-like):
    6 slots with disjoint Zipfian vocabularies, slots 0,2,4 optional; no
    dependencies between slots. Known answer: 6 slots."""
    sizes = [12, 40, 60, 25, 15, 5]
    pres = [0.4, 1.0, 0.6, 0.9, 0.5, 0.7]
    vocab = [["C%d_%d" % (k, i) for i in range(n)] for k, n in enumerate(sizes)]
    probs = [(lambda w: w / w.sum())(1.0 / np.arange(1, n + 1) ** 1.0) for n in sizes]
    out = set()
    while len(out) < n_texts:
        t = tuple(vocab[k][rng.choice(sizes[k], p=probs[k])] for k in range(6) if rng.random() < pres[k])
        if t:
            out.add(t)
    return sorted(out)


def save_json(key, obj):
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[key] = obj
    json.dump(d, open(p, "w"), indent=1, default=float)
