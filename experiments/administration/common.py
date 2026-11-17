"""Shared helpers for experiments/administration. Run scripts from the repo root:
    .venv/bin/python experiments/administration/<script>.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa: E402,F401

OUT = Path(__file__).resolve().parent
SEED = 20261114

OPENERS = {"M267", "M391", "M293", "M150"}
CONNECTIVES = {"M99", "M123"}
CLOSERS = {"M342", "M211", "M1", "M176", "M169", "M15", "M254", "M12"}

TALL = {"M86": 1, "M87": 2, "M88": 3, "M89": 3, "M92": 3, "M93": 3, "M94": 3, "M95": 4, "M96": 5}
SHORT = {"M97": 1, "M98": 1, "M102": 3, "M103": 3, "M104": 4, "M105": 4, "M106": 5, "M107": 5,
         "M108": 6, "M109": 6, "M110": 7, "M111": 7, "M112": 7, "M114": 8, "M115": 9, "M116": 9,
         "M117": 9, "M118": 10, "M121": 12, "M122": 5}  # M99/M100/M101 (2 short) = connective, excluded


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def lines_of(seq):
    out, cur = [], []
    for s in seq:
        if s == "|":
            out.append(cur); cur = []
        else:
            cur.append(s)
    out.append(cur)
    return [l for l in out if l]


def core(seq):
    """Text minus opener formula (opener + connective) and trailing closers."""
    s = list(seq)
    if s and s[0] in OPENERS:
        s = s[1:]
        if s and s[0] in CONNECTIVES:
            s = s[1:]
    while s and s[-1] in CLOSERS:
        s = s[:-1]
    return tuple(s)


def key(seq):
    return " ".join(seq)


def load_bridge():
    b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    return {int(w): "M%d" % v["M"][0] for w, v in b.items()}


def load_merged():
    return json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json"))


def save_json(name, obj):
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[name] = obj
    json.dump(d, open(p, "w"), indent=1, default=float)


def bh(pvals):
    """Benjamini-Hochberg q-values."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    q = [0.0] * n
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        prev = min(prev, pvals[i] * n / rank)
        q[i] = prev
    return q
