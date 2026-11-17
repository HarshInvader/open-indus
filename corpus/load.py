"""Shared loaders. Every experiment imports from here so all agents use identical data.

    from corpus.load import m77_lines, m77_texts, icit_texts, dev_heldout, distinct

Rules (inherited from shaunmortal/indus lessons, adopted here):
  * Count DISTINCT sequences, not objects: moulded tablets repeat one text up to 32 times.
  * Never use held-out sequences when developing a hypothesis; only for the final test.
  * A break is not a sign: use `segments` (break-free runs) for n-gram statistics.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def _jl(name):
    return [json.loads(l) for l in open(DATA / name)]


def m77_lines():
    return _jl("m77_lines.jsonl")


def m77_texts():
    return _jl("m77_texts.jsonl")


def icit_texts():
    return _jl("icit_texts.jsonl")


def distinct(records, key="seq"):
    """Keep the first record of each distinct sign sequence."""
    seen, out = set(), []
    for r in records:
        k = " ".join(r[key]) if isinstance(r[key], list) else r[key]
        if k not in seen:
            seen.add(k); out.append(r)
    return out


def dev_heldout(texts=None, version=2):
    """Return (dev, heldout) lists of DISTINCT M77 object-side texts.
    version=2 (default since 2026-11-14) splits by text family so near-copies never
    straddle the split; version=1 is the original split used by wave-1/2 experiments."""
    texts = distinct(texts or m77_texts())
    held = set(json.load(open(DATA / ("splits_v2.json" if version == 2 else "splits.json")))["heldout"])
    dev = [t for t in texts if " ".join(t["seq"]) not in held]
    ho = [t for t in texts if " ".join(t["seq"]) in held]
    return dev, ho


def runs(seq):
    """Split a seq at line breaks '|' and breaks '#' into contiguous sign runs."""
    out, cur = [], []
    for s in seq:
        if s in ("|", "#"):
            if cur: out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur: out.append(cur)
    return out
