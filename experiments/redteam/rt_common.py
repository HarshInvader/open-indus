"""Red-team helpers. Independent of other teams' code: reads the jsonl data directly."""
import json, math, random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent


def jl(name):
    return [json.loads(l) for l in open(DATA / name)]


def icit():
    return jl("icit_texts.jsonl")


def m77():
    return jl("m77_texts.jsonl")


def m77_lines():
    return jl("m77_lines.jsonl")


def splits():
    return set(json.load(open(DATA / "splits.json"))["heldout"])


def flat(seq):
    """Drop line breaks; None if text has a break mark."""
    if "#" in seq:
        return None
    s = tuple(x for x in seq if x != "|")
    return s or None


def distinct_recs(recs, key=lambda r: tuple(r["seq"])):
    seen, out = set(), []
    for r in recs:
        k = key(r)
        if k in seen:
            continue
        seen.add(k); out.append(r)
    return out


def edit1(a, b):
    """True if Levenshtein distance between tuples a,b <= 1."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def near_dup_clusters(seqs):
    """Union-find clusters of sequences at edit distance <= 1 (single linkage)."""
    seqs = list(seqs)
    par = list(range(len(seqs)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    bylen = defaultdict(list)
    for i, s in enumerate(seqs):
        bylen[len(s)].append(i)
    for i, s in enumerate(seqs):
        for L in (len(s), len(s) + 1):
            for j in bylen.get(L, []):
                if j <= i and L == len(s):
                    continue
                if edit1(s, seqs[j]):
                    par[f(i)] = f(j)
    cl = defaultdict(list)
    for i in range(len(seqs)):
        cl[f(i)].append(seqs[i])
    return list(cl.values())


class KN:
    """Interpolated Kneser-Ney bigram (own implementation) with BOS/EOS.
    discount d; unk mass via add-one on the continuation unigram."""

    def __init__(self, texts, d=0.75, vocab=None):
        self.d = d
        self.big = defaultdict(Counter)
        cont = defaultdict(set)
        for t in texts:
            p = "<s>"
            for s in list(t) + ["</s>"]:
                self.big[p][s] += 1; cont[s].add(p); p = s
        self.V = set(vocab or []) | {s for t in texts for s in t} | {"</s>", "<unk>"}
        self.cc = Counter({s: len(v) for s, v in cont.items()})
        self.ntypes = sum(self.cc.values())
        self.ctot = {p: sum(c.values()) for p, c in self.big.items()}
        self.nfoll = {p: len(c) for p, c in self.big.items()}

    def pcont(self, s):
        return (self.cc.get(s, 0) + 1) / (self.ntypes + len(self.V))

    def p(self, prev, s):
        pc = self.pcont(s)
        if prev not in self.big:
            return pc
        c = self.big[prev]; tot = self.ctot[prev]
        return max(c.get(s, 0) - self.d, 0) / tot + self.d * self.nfoll[prev] / tot * pc

    def bits(self, t, eos=True):
        p, b = "<s>", 0.0
        seq = list(t) + (["</s>"] if eos else [])
        for s in seq:
            b -= math.log2(self.p(p, s)); p = s
        return b


class Uni:
    def __init__(self, texts, alpha=1.0, vocab=None):
        self.c = Counter(s for t in texts for s in list(t) + ["</s>"])
        self.V = set(vocab or []) | set(self.c) | {"<unk>"}
        self.n = sum(self.c.values()); self.a = alpha

    def p(self, s):
        return (self.c.get(s, 0) + self.a) / (self.n + self.a * len(self.V))

    def bits(self, t, eos=True):
        seq = list(t) + (["</s>"] if eos else [])
        return -sum(math.log2(self.p(s)) for s in seq)


def save(name, obj):
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[name] = obj
    json.dump(d, open(p, "w"), indent=1, default=str)
