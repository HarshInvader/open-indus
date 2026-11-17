"""Red-team reimplementation helpers for pair_numeral_long (written without reading that folder's code).
Run scripts from repo root: .venv/bin/python experiments/redteam_pnl/<x>.py
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa

OUT = ROOT / "experiments" / "redteam_pnl"
SRC = ROOT / "sources" / "shaunmortal_indus" / "data"
_ST = json.load(open(SRC / "stroke_signs.json"))
SHORT_ALL = {f"M{k}": v for k, v in _ST["short"].items()}
TALL_ALL = {f"M{k}": v for k, v in _ST["tall"].items()}
BRIDGE = json.load(open(SRC / "bridge_WM.json"))


def numeral_tables(variant="base"):
    """Return (short, tall) dicts sign->value under a segmentation variant.
    base       : as claimed (short excl. M99/M101 connective-like 2s), all tall incl. M88/M92-94.
    with_2s    : base + M99, M101 as short 2.
    strict_tall: base, but tall-3 variants M88 (dotted), M92 (roofed), M93/M94 (slanted) are NOT numerals.
    pure       : strict_tall + drop bracketed short M111/M122 and two-tier M103/M107/M109/M112... kept? no:
                 drops only bracketed forms M111, M122 (enclosed strokes = possibly separate signs).
    """
    short = {k: v for k, v in SHORT_ALL.items() if k not in ("M99", "M101")}
    tall = dict(TALL_ALL)
    if variant == "with_2s":
        short["M99"] = 2; short["M101"] = 2
    if variant in ("strict_tall", "pure"):
        for k in ("M88", "M92", "M93", "M94"):
            tall.pop(k, None)
    if variant == "pure":
        for k in ("M111", "M122"):
            short.pop(k, None)
    return short, tall


def icit_numeral_tables():
    """Wells signs whose bridge partner is an M numeral. W2 (=M99/M100, mixes the connective) excluded."""
    s0, t0 = numeral_tables("base")
    short, tall = {}, {}
    for w, v in BRIDGE.items():
        ms = [f"M{m}" for m in v["M"]]
        if w == "2":
            continue
        W = f"W{int(w):03d}"
        if all(m in s0 for m in ms):
            vals = {s0[m] for m in ms}
            if len(vals) == 1: short[W] = vals.pop()
        elif all(m in t0 for m in ms):
            vals = {t0[m] for m in ms}
            if len(vals) == 1: tall[W] = vals.pop()
    return short, tall


def W2M():
    return {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}


def numeral_tokens(texts, short, tall, direction="before", cluster=False):
    """One record per (numeral, head) adjacency inside break-free runs.
    direction='before': numeral directly precedes head (head = next non-numeral sign).
    direction='after' : numeral directly follows head (head = previous non-numeral sign).
    cluster=True: value = sum of the contiguous same-system numeral run adjacent to the head.
    Returns list of dict(text_idx, sys, value, head, numsign)."""
    out = []
    isnum = lambda s: s in short or s in tall
    for ti, t in enumerate(texts):
        for r in runs(t["seq"]):
            n = len(r)
            for i, s in enumerate(r):
                if not isnum(s):
                    continue
                j = i + 1 if direction == "before" else i - 1
                if not (0 <= j < n) or isnum(r[j]):
                    continue
                sys_ = "short" if s in short else "tall"
                tab = short if sys_ == "short" else tall
                val = tab[s]
                if cluster:
                    k = i - 1 if direction == "before" else i + 1
                    while 0 <= k < n and r[k] in tab:
                        val += tab[r[k]]; k += -1 if direction == "before" else 1
                out.append(dict(text_idx=ti, sys=sys_, value=val, head=r[j], numsign=s))
    return out


def families(texts, k=3):
    """Union-find families: texts sharing any k-gram of signs (inside a run) are joined."""
    par = list(range(len(texts)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    first = {}
    for i, t in enumerate(texts):
        for r in runs(t["seq"]):
            for a in range(len(r) - k + 1):
                g = tuple(r[a:a + k])
                if g in first:
                    par[f(i)] = f(first[g])
                else:
                    first[g] = i
    return [f(i) for i in range(len(texts))]


def dump(obj, name):
    json.dump(obj, open(OUT / name, "w"), indent=1, default=str)
