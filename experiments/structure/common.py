"""Shared helpers for experiments/structure. Run scripts from repo root."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa: E402

OUT = Path(__file__).resolve().parent
RNG_SEED = 20261114


def signs(seq):
    """All signs of a text in reading order, dropping line breaks and break marks."""
    return [s for s in seq if s not in ("|", "#")]


def is_clean(t):
    """Text whose first and last positions are trustworthy: no break mark, flagged complete."""
    return "#" not in t["seq"] and t.get("complete", True)


def m77_split():
    dev, ho = dev_heldout()
    return dev, ho


def icit_distinct():
    return distinct(icit_texts())


def site_norm(s):
    s = s.replace("-", "").replace(" ", "").lower()
    return {"mohenjodaro": "Mohenjodaro", "harappa": "Harappa", "chanhudaro": "Chanhudaro"}.get(s, s.capitalize())


def load_bridge():
    """W code -> M code (first listed M); only one-to-one or many-to-one bridges are kept."""
    b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    out = {}
    for w, v in b.items():
        ms = v["M"]
        out["W%03d" % int(w)] = "M%d" % ms[0]
    return out


def save_json(name, obj):
    """Merge obj under key `name` into results.json."""
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[name] = obj
    json.dump(d, open(p, "w"), indent=1, default=float)


def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c)


def bh(pvals):
    """Benjamini-Hochberg q-values."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    q = [0] * n
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        prev = min(prev, pvals[i] * n / rank)
        q[i] = prev
    return q


class Bigram:
    """Interpolated Kneser-Ney-ish (absolute discounting) bigram over runs with <s>,</s>."""

    def __init__(self, seqs, d=0.75):
        self.d = d
        self.big = defaultdict(Counter)
        self.uni = Counter()
        for s in seqs:
            toks = ["<s>"] + s + ["</s>"]
            for a, b in zip(toks, toks[1:]):
                self.big[a][b] += 1
            self.uni.update(s + ["</s>"])
        self.vocab = set(self.uni) | {"<unk>"}
        self.N = sum(self.uni.values())
        # continuation counts
        cont = Counter()
        for a, c in self.big.items():
            for b in c:
                cont[b] += 1
        self.cont = cont
        self.ncont = sum(cont.values())

    def p_uni(self, b):
        V = len(self.vocab) + 1
        return (self.cont.get(b, 0) + 0.5) / (self.ncont + 0.5 * V)

    def p(self, a, b):
        c = self.big.get(a)
        pu = self.p_uni(b)
        if not c:
            return pu
        tot = sum(c.values())
        return max(c.get(b, 0) - self.d, 0) / tot + self.d * len(c) / tot * pu

    def logprob(self, s):
        toks = ["<s>"] + s + ["</s>"]
        return sum(math.log2(self.p(a, b)) for a, b in zip(toks, toks[1:]))


class Unigram:
    def __init__(self, seqs, alpha=0.5):
        self.c = Counter()
        for s in seqs:
            self.c.update(s + ["</s>"])
        self.N = sum(self.c.values())
        self.V = len(self.c) + 1
        self.alpha = alpha

    def p(self, b):
        return (self.c.get(b, 0) + self.alpha) / (self.N + self.alpha * self.V)

    def logprob(self, s):
        return sum(math.log2(self.p(b)) for b in s + ["</s>"])
