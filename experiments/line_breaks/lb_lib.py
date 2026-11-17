"""Line-break boundary test: shared library (frozen with the prereg).

Boundary model is fitted on SINGLE-LINE dev texts only (dev_heldout(version=2), n_lines == 1).
Primary score per adjacent pair (a, b): end-start ratio
    ESR(a,b) = log2 P(</s>|a) + log2 P(b|<s>) - log2 P(b|a)
(how much more probable 'text ends after a, new text starts with b' is than 'b follows a'),
from an interpolated Kneser-Ney bigram over break-free runs.
Secondary: slot-rule boundary (closer-class a, or opener-class b; never after a stroke numeral,
never next to the connective M99/M123).
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, dev_heldout, distinct, runs  # noqa

BOS, EOS = "<s>", "</s>"
CONNECTIVE = {"M99", "M123"}
JAR = {"M342"}
D = 0.75


def stroke_signs():
    import csv
    out = set()
    for r in csv.DictReader(open(ROOT / "experiments/structure/sign_table.csv")):
        if r["stroke_type"].strip():
            out.add(r["sign"])
    return out


NUMERALS = stroke_signs()


class Model:
    def __init__(self, texts):
        self.big = Counter(); self.ctx = Counter(); self.foll = defaultdict(set); self.prec = defaultdict(set)
        pos = defaultdict(Counter)
        for t in texts:
            for r in runs(t["seq"]):
                s = [BOS] + r + [EOS]
                for a, b in zip(s, s[1:]):
                    self.big[(a, b)] += 1; self.ctx[a] += 1
                    self.foll[a].add(b); self.prec[b].add(a)
                if len(r) == 1:
                    pos[r[0]]["S"] += 1
                else:
                    pos[r[0]]["I"] += 1; pos[r[-1]]["F"] += 1
                    for x in r[1:-1]:
                        pos[x]["M"] += 1
        self.ntypes_big = len(self.big)
        self.vocab = set(self.prec) | set(self.foll)
        self.cls = {}
        for x, c in pos.items():
            n = c["I"] + c["M"] + c["F"]
            if n < 5:
                continue
            sh = {"O": c["I"] / n, "K": c["M"] / n, "C": c["F"] / n}
            self.cls[x] = max(sh, key=sh.get)

    def pcont(self, b):
        return (len(self.prec.get(b, ())) + 0.5) / (self.ntypes_big + 0.5 * (len(self.vocab) + 1))

    def p(self, b, a):
        ca = self.ctx.get(a, 0)
        if ca == 0:
            return self.pcont(b)
        lam = D * len(self.foll[a]) / ca
        return max(self.big.get((a, b), 0) - D, 0) / ca + lam * self.pcont(b)

    def esr(self, a, b):
        return np.log2(self.p(EOS, a)) + np.log2(self.p(b, BOS)) - np.log2(self.p(b, a))

    def slot(self, a, b):
        if a in NUMERALS or a in CONNECTIVE or b in CONNECTIVE:
            return 0
        ca, cb = self.cls.get(a, "K"), self.cls.get(b, "K")
        return int(ca == "C" or cb == "O" or a in JAR)


def fit_model():
    dev, _ = dev_heldout(version=2)
    single = [t for t in dev if t["n_lines"] == 1]
    return Model(single), len(single)


def usable_m77():
    """Distinct M77 texts with exactly 2 non-empty lines, complete, no '#', >=3 signs, unmixed direction.
    Returns list of dicts: seq (signs, no '|'), k (break after k signs), heldout flag, object_type."""
    lines_by = defaultdict(list)
    for l in m77_lines():
        lines_by[(l["text_no"], l["side"])].append(l)
    _, ho = dev_heldout(version=2)
    hos = {" ".join(t["seq"]) for t in ho}
    out = []
    for t in distinct([t for t in m77_texts() if t["n_lines"] > 1]):
        ls = [l for l in sorted(lines_by[(t["text_no"], t["side"])], key=lambda x: x["line"]) if l["signs"]]
        if len(ls) != 2 or "#" in t["seq"] or not t["complete"]:
            continue
        if len({l["direction"] for l in ls} - {"single sign"}) > 1:
            continue
        sg = [s for s in t["seq"] if s != "|"]
        if len(sg) < 3:
            continue
        out.append(dict(seq=sg, k=t["seq"].index("|"), heldout=" ".join(t["seq"]) in hos,
                        object_type=t["object_type"], text_no=t["text_no"], site=t["site"]))
    return out


def ranks(scores):
    """Percentile rank (0..1, midrank ties) of each position's score within the text."""
    s = np.asarray(scores, float); n = len(s)
    if n == 1:
        return np.array([0.5])
    r = np.array([(np.sum(s < x) + 0.5 * (np.sum(s == x) - 1)) / (n - 1) for x in s])
    return r


def text_tables(model, texts):
    """For each text: per-position percentile rank of ESR and slot flag (positions k=1..n-1)."""
    tabs = []
    for t in texts:
        sg = t["seq"]
        e = [model.esr(a, b) for a, b in zip(sg, sg[1:])]
        sl = [model.slot(a, b) for a, b in zip(sg, sg[1:])]
        tabs.append(dict(rank=ranks(e), slot=np.array(sl), n=len(sg)))
    return tabs


def stat(tabs, ks):
    """Mean percentile rank of the break position (k = break after k signs -> index k-1)."""
    return float(np.mean([tb["rank"][k - 1] for tb, k in zip(tabs, ks)]))


def null_draw(tabs, rng, qs=None):
    """Draw break positions from the null (uniform over 1..n-1 unless per-text probs qs given)."""
    out = []
    for i, tb in enumerate(tabs):
        m = tb["n"] - 1
        if qs is None:
            out.append(int(rng.integers(1, m + 1)))
        else:
            out.append(int(rng.choice(np.arange(1, m + 1), p=qs[i])))
    return out


def null_expect(tabs, qs=None):
    vals = []
    for i, tb in enumerate(tabs):
        m = tb["n"] - 1
        q = np.full(m, 1 / m) if qs is None else qs[i]
        vals.append(float(np.dot(q, tb["rank"])))
    return float(np.mean(vals))


def test(tabs, ks, rng, qs=None, nsim=4000):
    obs = stat(tabs, ks)
    sims = np.array([stat(tabs, null_draw(tabs, rng, qs)) for _ in range(nsim)])
    return obs, float(sims.mean()), float((1 + np.sum(sims >= obs)) / (nsim + 1))
