"""A1b. Does Yajnadevam's key make Sanskrit words more readily than null keys?

Matcher (generous, uses HIS latitude as measured by a1_free_choices.py):
  * vowels are free (key vowels ignored, any vowels may be inserted);
  * each key consonant may be read as any member of its class:
      s:{s S z h H}  n:{n N R Y m M}  d:{d D q Q}  t:{t T w W}  b:{b B}  k:{k K}  c:{c C}
      j:{j J}  p:{p P}  m:{m M}  others identical;
  * word breaks anywhere (also inside a sign value);
  * lexicon = 194k Monier-Williams headwords (Cologne sanhw1, SLP1) + stems with the
    consonantal case endings -m, -s/-H, -sy(a), -t, -n.
Score of a key on a corpus: CPW = key consonants / words, where for each text we take the
segmentation of its consonant string into lexicon skeletons with the FEWEST words (long
dictionary words = better fit; 1-consonant words exist for every consonant, so every text
is segmentable and the question is how long the words can be). Also LONG = share of texts
segmentable using only words of >= 2 consonants.

Nulls:
  N1 permuted keys: values shuffled across signs inside frequency bins (same value inventory);
  N2 fitted keys: hill-climb (value swaps) maximising CPW, run on (a) the real corpus and
     (b) random corpora with the same sign frequencies and text lengths (unigram) and
     (c) a bigram-Markov corpus; Yajnadevam fitted his key to the corpus, so the fair null is a
     key fitted the same way to text that has no language in it.
  Planted control: a Sanskrit corpus (RV names/epithets) written with a random consonantal key
     of the same shape; does the fitter score higher on it than on random corpora?
Run: .venv/bin/python experiments/language/a1_key_null.py [--quick]
"""
import json
import random
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1]))
from yj_common import load_key  # noqa
from corpus.load import icit_texts, distinct, runs  # noqa

QUICK = "--quick" in sys.argv
STRICT = "--strict" in sys.argv  # no consonant latitude: key letter = that plain consonant only
CLASSES = {} if STRICT else {"s": "sSzhH", "n": "nNRYmM", "d": "dDqQ", "t": "tTwW", "b": "bB", "k": "kK", "c": "cC",
           "j": "jJ", "p": "pP", "m": "mM"}
KEYLET = "kgcjtdnpbmyrlvsh"
INV = defaultdict(set)  # reading consonant -> key letters that may produce it
for kl in KEYLET:
    for ch in CLASSES.get(kl, kl):
        INV[ch].add(kl)
CONS = set(INV)
ENDINGS = [(), ("m",), ("s",), ("s", "y"), ("t",), ("n",)]
MAXW = 7


def build_lexicon():
    words = [w.strip() for w in open(HERE / "ext" / "skt" / "mw_headwords.txt") if w.strip()]
    sk = set()
    for w in words:
        c = [ch for ch in w if ch in CONS]
        if not c or len(c) > MAXW:
            continue
        for e in ENDINGS:
            cc = c + list(e)
            if len(cc) > MAXW:
                continue
            for t in product(*[sorted(INV[ch]) for ch in cc]):
                sk.add(t)
    return sk


def key_cons(val):
    return [c for c in val if c in KEYLET]


def min_words(cons, lex):
    """Fewest lexicon skeletons covering cons; also whether a cover with all words >=2 cons exists."""
    n = len(cons)
    INF = 10 ** 9
    best = [0] + [INF] * n
    best2 = [True] + [False] * n
    for i in range(1, n + 1):
        for L in range(1, min(MAXW, i) + 1):
            if best[i - L] < INF and tuple(cons[i - L:i]) in lex:
                best[i] = min(best[i], best[i - L] + 1)
                if L >= 2 and best2[i - L]:
                    best2[i] = True
    return best[n], best2[n]


class Scorer:
    def __init__(self, texts, lex):
        self.texts, self.lex = texts, lex
        self.by_sign = defaultdict(list)
        for i, t in enumerate(texts):
            for s in set(t):
                self.by_sign[s].append(i)

    def text_score(self, t, key):
        cons = []
        for s in t:
            cons += key_cons(key.get(s, ""))
        if len(cons) < 2:
            return None
        w, l2 = min_words(cons, self.lex)
        return len(cons), w, l2

    def full(self, key):
        self.cache = [self.text_score(t, key) for t in self.texts]
        return self.summary()

    def summary(self):
        v = [c for c in self.cache if c]
        C = sum(x[0] for x in v); W = sum(x[1] for x in v)
        return dict(cpw=C / W, long=sum(x[2] for x in v) / len(v), n=len(v))

    def cpw_after(self, key, signs):
        idx = set()
        for s in signs:
            idx.update(self.by_sign[s])
        new = {i: self.text_score(self.texts[i], key) for i in idx}
        C = W = 0
        for i, c in enumerate(self.cache):
            c = new.get(i, c)
            if c:
                C += c[0]; W += c[1]
        return C / W, new


def fit(scorer, key0, signs, iters, rng):
    key = dict(key0)
    cur = scorer.full(key)["cpw"]
    for _ in range(iters):
        a, b = rng.sample(signs, 2)
        if key[a] == key[b]:
            continue
        key[a], key[b] = key[b], key[a]
        new_cpw, new = scorer.cpw_after(key, [a, b])
        if new_cpw >= cur:
            cur = new_cpw
            for i, c in new.items():
                scorer.cache[i] = c
        else:
            key[a], key[b] = key[b], key[a]
    return key, scorer.full(key)


def freq_bins(signs, freq, size=10):
    ss = sorted(signs, key=lambda s: -freq[s])
    return [ss[i:i + size] for i in range(0, len(ss), size)]


def permute_in_bins(key, bins, rng):
    k = dict(key)
    for b in bins:
        vals = [key[s] for s in b]
        rng.shuffle(vals)
        for s, v in zip(b, vals):
            k[s] = v
    return k


def unigram_corpus(texts, rng):
    toks = [s for t in texts for s in t]
    return [[rng.choice(toks) for _ in t] for t in texts]


def bigram_corpus(texts, rng):
    nxt = defaultdict(list); starts = []
    for t in texts:
        starts.append(t[0])
        for a, b in zip(t, t[1:]):
            nxt[a].append(b)
    out = []
    for t in texts:
        s = [rng.choice(starts)]
        while len(s) < len(t):
            s.append(rng.choice(nxt[s[-1]]) if nxt[s[-1]] else rng.choice(starts))
        out.append(s)
    return out


def planted_sanskrit(texts, key, rng):
    """Seal-like legends from RV names/epithets (SLP1), mapped to key-consonant strings, then
    'written' with signs: each sign of the real key whose value has 1 consonant spells that
    consonant (random choice among signs with that value class). Lengths matched roughly."""
    src = HERE / "ext" / "eqstats" / "rv_names_epithets_lemmas.txt"
    from yj_common import iast_to_slp  # noqa
    lem = [iast_to_slp(l.split()[0]) for l in open(src, encoding="utf8") if l.strip() and not l.startswith("#")]
    from yj_common import SLP_CONS  # noqa
    lem = [w for w in lem if all(ch.isascii() for ch in w)]
    by_cons = defaultdict(list)
    for s, v in key.items():
        kc = key_cons(v)
        if len(kc) == 1:
            by_cons[kc[0]].append(s)
    rev = {}
    for kl in KEYLET:
        for ch in CLASSES.get(kl, kl):
            rev.setdefault(ch, kl)
    out = []
    for t in texts:
        target = len(t)
        seq = []
        while len(seq) < target:
            w = rng.choice(lem)
            for ch in w:
                if ch in rev and by_cons.get(rev[ch]):
                    seq.append(rng.choice(by_cons[rev[ch]]))
        out.append(seq[:target])
    return out


def main():
    rng = random.Random(7)
    key = load_key()
    lex = build_lexicon()
    print("lexicon skeletons:", len(lex))
    texts = []
    for t in distinct(icit_texts()):
        for r in runs(t["seq"]):
            codes = [s[1:] for s in r]
            if all(c in key and key[c] for c in codes) and len(codes) >= 2:
                texts.append(codes)
    texts = [list(x) for x in dict.fromkeys(tuple(t) for t in texts)]
    print("distinct keyed runs:", len(texts))
    freq = Counter(s for t in texts for s in t)
    signs = sorted(freq)
    bins = freq_bins(signs, freq)
    res = {"n_texts": len(texts), "lexicon_skeletons": len(lex)}

    sc = Scorer(texts, lex)
    real = sc.full(key)
    res["yajnadevam_key"] = real
    print("Yajnadevam key:", real)

    nperm = 40 if QUICK else 200
    perm = [sc.full(permute_in_bins(key, bins, rng)) for _ in range(nperm)]
    pc = np.array([p["cpw"] for p in perm]); pl = np.array([p["long"] for p in perm])
    res["N1_permuted"] = dict(n=nperm, cpw_mean=pc.mean(), cpw_sd=pc.std(), long_mean=pl.mean(), long_sd=pl.std(),
                              z_cpw=(real["cpw"] - pc.mean()) / pc.std(), z_long=(real["long"] - pl.mean()) / pl.std(),
                              p_cpw=(1 + (pc >= real["cpw"]).sum()) / (nperm + 1),
                              p_long=(1 + (pl >= real["long"]).sum()) / (nperm + 1))
    print("N1:", res["N1_permuted"])

    # N2 fitted keys
    iters = 1500 if QUICK else 6000
    nfit = 2 if QUICK else 4
    fits = defaultdict(list)
    corpora = {"real": lambda: texts, "unigram": lambda: unigram_corpus(texts, rng),
               "bigram": lambda: bigram_corpus(texts, rng),
               "planted_sanskrit": lambda: planted_sanskrit(texts, key, rng)}
    for name, mk in corpora.items():
        for k in range(nfit):
            corp = mk()
            s2 = Scorer(corp, lex)
            start = permute_in_bins(key, bins, rng)  # random start from the same inventory
            s0 = s2.full(start)
            kf, sf = fit(s2, start, signs, iters, rng)
            yj = s2.full(key) if name != "real" else real
            fits[name].append(dict(start=s0, fitted=sf, yj_key_on_this=yj))
            print(name, k, "start", round(s0["cpw"], 3), "fitted", round(sf["cpw"], 3), sf["long"], flush=True)
    res["N2_fitted"] = {n: dict(fitted_cpw=[f["fitted"]["cpw"] for f in v], fitted_long=[f["fitted"]["long"] for f in v],
                                start_cpw=[f["start"]["cpw"] for f in v],
                                yj_key_cpw=[f["yj_key_on_this"]["cpw"] for f in v]) for n, v in fits.items()}
    res["iters"] = iters
    json.dump(res, open(HERE / "out" / ("a1_key_null_strict.json" if STRICT else "a1_key_null.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
