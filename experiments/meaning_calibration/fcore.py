"""Form F (fixed partner, the parpola_rules34/p34.rule4 code path) on Indus-shaped Linear B draws.
Prereg docs/prereg/meaning_calibration.md. Shared by kill.py and run.py.
"""
import math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/language_vs_code"))
sys.path.insert(0, str(ROOT / "experiments/parpola_rules34"))
import load as LB          # noqa: E402
import lvc_corpora as C    # noqa: E402
import p34                 # noqa: E402

SEED0 = 20261124
NDRAW = 5
MIN_DEV, MIN_HELD = 10, 3          # eligibility: next-tokens of the head (p34.share_next definition: text end counts)
SHARE = 0.4
BINS = [(10, 19), (20, 49), (50, 10 ** 9)]


def tclass(t):
    if re.fullmatch(r"\d+", t): return "numeral"
    if re.search(r"[a-z]", t): return "word"
    return "ideogram/measure"


def bin_of(n):
    for lo, hi in BINS:
        if lo <= n <= hi: return f"{lo}-{hi if hi < 10 ** 9 else ''}"
    return "below"


def draw(k, docs=None):
    """Draw k: 1,680 dev + 565 held-out documents, disjoint, lengths matched to Indus dev / held-out
    (nearest-length fallback as lvc_metrics.matched_sample)."""
    docs = docs or LB.documents()
    rng = random.Random(SEED0 + k)
    dl = [len(t) for t in C.indus("dev")]; hl = [len(t) for t in C.indus("held")]
    by = defaultdict(list)
    for i, d in enumerate(docs): by[LB.length(d["seq"])].append(i)
    for v in by.values(): rng.shuffle(v)
    def take(L):
        for dd in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 8, -8, 10, 12, 15, 20, 30, 50]:
            if by.get(L + dd): return docs[by[L + dd].pop()]
        return None
    dev = [take(dl[rng.randrange(len(dl))]) for _ in range(1680)]
    held = [take(hl[rng.randrange(len(hl))]) for _ in range(565)]
    return [d["seq"] for d in dev if d], [d["seq"] for d in held if d]


class Side:
    """Counts and next-token tables for one text set."""
    def __init__(self, texts):
        self.texts = texts
        self.cnt = p34.counts(texts)
        occ = p34.occurrences(texts)
        self.nxt = {h: Counter(r for _, r in v if r is not None) for h, v in occ.items()}

    def n(self, h):
        return sum(self.nxt.get(h, Counter()).values())


def f_test(side, head, main, sq):
    """Share of head's next-tokens in P = {main, *sq}; null = pseudo-partner sets as p34.rule4 (x ~ main frequency,
    y ~ summed secondary frequency, all pairs; with no secondaries the set is {x})."""
    nx = side.nxt.get(head, Counter()); n = sum(nx.values())
    if n == 0: return None
    P = {main, *sq}
    obs = sum(nx[s] for s in P) / n
    cnt = side.cnt
    f1 = cnt[main]; fs = sum(cnt[s] for s in sq)
    bad = {head, main, *sq, "#"}
    p1 = [s for s in cnt if f1 / 2 <= cnt[s] <= 2 * f1 and s not in bad]
    if sq:
        ps = [s for s in cnt if fs / 2 <= cnt[s] <= 2 * fs and s not in bad]
        a = np.array([nx[x] for x in p1], float); b = np.array([nx[y] for y in ps], float)
        null = (a[:, None] + b[None, :])
        same = np.array([[x == y for y in ps] for x in p1]) if p1 and ps else np.zeros((len(p1), len(ps)), bool)
        null = null[~same] / n
    else:
        null = np.array([nx[x] for x in p1], float) / n
    if null.size == 0: return None
    p = (1 + int((null >= obs - 1e-12).sum())) / (1 + null.size)
    return dict(obs=obs, n=n, p=p, median=float(np.median(null)), n_null=int(null.size))


def eligible(dev, held):
    return {h for h in dev.nxt if h != "#" and dev.n(h) >= MIN_DEV and held.n(h) >= MIN_HELD}


def verdict(dev, held, head, main, sq, power_by_bin):
    """S / R / U for one claim on one draw."""
    if not (dev.n(head) >= MIN_DEV and held.n(head) >= MIN_HELD): return "U", None
    rd = f_test(dev, head, main, sq); rh = f_test(held, head, main, sq)
    if rd is None: return "U", None
    if rd["obs"] >= SHARE and rd["p"] <= 0.01 and rh is not None and rh["p"] <= 0.05: return "S", (rd, rh)
    if rd["obs"] <= rd["median"] and power_by_bin.get(bin_of(rd["n"]), 0) >= 0.8: return "R", (rd, rh)
    return "U", (rd, rh)


def plant(texts, head, x, rng):
    """Replace the token after `head` by x at ceil(0.4 n) of head's n next-positions (existing x count towards it).
    Only real-token next positions (not text end, not a break) can be replaced. Returns (texts, ok)."""
    pos, n, have = [], 0, 0
    for ti, t in enumerate(texts):
        for i, s in enumerate(t):
            if s != head: continue
            if i == len(t) - 1: n += 1; continue
            r = t[i + 1]
            if r == "#": continue
            n += 1
            if r == x: have += 1
            else: pos.append((ti, i + 1))
    need = math.ceil(SHARE * n) - have
    if need <= 0: return texts, True
    if need > len(pos): return texts, False
    out = [list(t) for t in texts]
    for j in rng.sample(range(len(pos)), need):
        ti, i = pos[j]; out[ti][i] = x
    return out, True
