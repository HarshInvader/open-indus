"""Shared helpers for detached_signs. Layout-only: no covariates here."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout  # noqa

bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": {f"M{m}" for m in v["M"]} for k, v in bridge.items()}
M2W = defaultdict(set)
for w, ms in W2M.items():
    for m in ms:
        M2W[m].add(w)


def lines(seq):
    """Split seq at '|' into lines (lists, '#' kept)."""
    out, cur = [], []
    for s in seq:
        if s == "|":
            out.append(cur); cur = []
        else:
            cur.append(s)
    out.append(cur)
    return [l for l in out if l]


def solo_flags(seq):
    """Return list of (sign, is_detached, n_lines) for every sign token.
    Detached = the token is the only sign on a line that has no '#', in a text with >=2 non-empty lines."""
    ls = lines(seq)
    nl = len(ls)
    out = []
    for l in ls:
        signs = [s for s in l if s != "#"]
        solo = nl >= 2 and len(signs) == 1 and "#" not in l
        for s in signs:
            out.append((s, solo, nl))
    return out


def matches(iseq, mseq):
    """ICIT seq matches an M77 seq via the W->M bridge (from line_breaks/count.py)."""
    a = [s for s in iseq if s != "#"]; b = [s for s in mseq if s != "#"]
    if len(a) != len(b):
        return False
    hits = 0
    for x, y in zip(a, b):
        if x == "|" or y == "|":
            if x != y:
                return False
            continue
        if x in W2M:
            if y not in W2M[x]:
                return False
            hits += 1
    return hits >= max(1, (len(a) - a.count("|")) // 2)


def _flat(seq):
    return [s for s in seq if s not in ("|", "#")]


def icit_only(I=None):
    """Distinct ICIT texts (by seq+site) that match no M77 distinct text (with or without line marks)."""
    I = I or icit_texts()
    T = distinct(m77_texts())
    by_len = defaultdict(list)
    for t in T:
        f = _flat(t["seq"])
        by_len[len(f)].append(f)
    seen, out = set(), []
    for r in I:
        k = (r["site"], " ".join(r["seq"]))
        if k in seen:
            continue
        seen.add(k)
        f = _flat(r["seq"])
        if not f:
            continue
        hit = False
        for g in by_len[len(f)]:
            n = 0; ok = True
            for x, y in zip(f, g):
                if x in W2M:
                    if y not in W2M[x]:
                        ok = False; break
                    n += 1
            if ok and n >= max(1, len(f) // 2):
                hit = True; break
        if not hit:
            out.append(r)
    return out
