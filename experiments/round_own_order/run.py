"""Round texts: shared order of their own? (prereg docs/prereg/round_own_order.md)
Run: .venv/bin/python -I experiments/round_own_order/run.py [power|real]"""
import sys, json, re
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/typology"))
from corpus.load import icit_texts, distinct  # noqa
import q2_gulf as Q  # noqa
rng = np.random.default_rng(20261124)
K, NSH, ND, NSETS = 0.1, 200, 1000, 200

def leg(seq): return [s for s in seq if re.fullmatch(r"W\d+", s)]
RT = json.load(open(ROOT / "experiments/round_seal_format/results.json"))["round_texts"]
rnd = [t for t in (leg(u["seq"].split()) for u in RT) if len(t) >= 2]
home = [t for t in (leg(x["seq"]) for x in distinct(icit_texts())
        if x["type"] == "SEAL:S" and x["site"] not in Q.FOREIGN_ALL and x["site"] != "Unknown") if len(t) >= 2]
V = sorted({s for t in rnd + home for s in t}) + ["<s>", "</s>"]; NV = len(V)
hbylen = defaultdict(list)
for t in home: hbylen[min(len(t), 6)].append(t)
keys = [min(len(t), 6) for t in rnd]

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

mode = sys.argv[1] if len(sys.argv) > 1 else "power"
info = dict(n_round=len(rnd), n_home=len(home), V=NV)
print(info, flush=True)
if mode == "power":
    res = [loo(homeset()) for _ in range(NSETS)]
    pw = float(np.mean([r["found"] for r in res]))
    out = dict(info, power=pw, home_excess_median=float(np.median([r["excess"] for r in res])),
               gate="PASS" if pw >= 0.8 else "STOP: untestable at n")
    print(out); json.dump(out, open(HERE / "power.json", "w"), indent=1)
elif mode == "real":
    assert json.load(open(HERE / "power.json"))["power"] >= 0.8, "power gate not passed"
    assert not (HERE / "real.json").exists(), "already scored"
    r = loo(rnd)
    hx = [score(rnd, (lambda M: (lambda i: M))(BG(homeset())))["excess"] for _ in range(NSETS)]
    out = dict(info, round_loo=r, home_trained_excess_on_round_median=float(np.median(hx)),
               verdict=("A supported (own order)" if r["found"] and r["excess"] > np.median(hx) else
                        "order = weak Indus order" if r["found"] else "no order found"))
    print(out); json.dump(out, open(HERE / "real.json", "w"), indent=1)
