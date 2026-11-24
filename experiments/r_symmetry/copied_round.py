"""Verbatim copies of the round_own_order statistic functions (prereg r_symmetry "Code plan": round_own_order/run.py
runs its analysis at import). Source: experiments/round_own_order/run.py at commit 592193f. Bodies unchanged; the
module globals they read (rng, NV, hbylen, keys) are set by setup() instead of run.py's import-time lines 11, 15-22.
"""
import re
from collections import Counter
import numpy as np

rng = np.random.default_rng(20261124)          # run.py line 11
NV = None
hbylen = keys = None


def setup(**kw):
    globals().update(kw)


# ---- round_own_order/run.py line 12
K, NSH, ND, NSETS = 0.1, 200, 1000, 200

# ---- round_own_order/run.py line 14
def leg(seq): return [s for s in seq if re.fullmatch(r"W\d+", s)]

# ---- round_own_order/run.py lines 24-51
class BG:
    def __init__(self, texts):
        self.b = Counter(); self.u = Counter()
        for t in texts:
            s = ["<s>"] + t + ["</s>"]
            for a, c in zip(s, s[1:]): self.b[(a, c)] += 1; self.u[a] += 1
    def bits(self, t):
        s = ["<s>"] + t + ["</s>"]
        return -sum(np.log2((self.b[(a, c)] + K) / (self.u[a] + K * NV)) for a, c in zip(s, s[1:]))

def shuffles(t):
    return [list(rng.permutation(t)) for _ in range(NSH)]

def score(texts, model_for):
    real = np.empty(len(texts)); sh = np.empty((len(texts), NSH)); L = np.array([len(t) for t in texts])
    for i, t in enumerate(texts):
        M = model_for(i); real[i] = M.bits(t); sh[i] = [M.bits(x) for x in shuffles(t)]
    exc = float(((sh.mean(1) - real)).sum() / L.sum())
    idx = rng.integers(NSH, size=(ND, len(texts)))
    tot = sh[np.arange(len(texts)), idx].sum(1)
    p = float((1 + (tot <= real.sum()).sum()) / (ND + 1))
    return dict(excess=exc, p=p, found=bool(exc >= 0.3 and p < 0.01))

def loo(texts):
    return score(texts, lambda i: BG(texts[:i] + texts[i + 1:]))

def homeset():
    return [list(hbylen[k][rng.integers(len(hbylen[k]))]) for k in keys]
