"""Leakage of random object splits on M77 alone. Prereg: docs/prereg/split_leakage.md.

Run: board/run.sh .venv/bin/python -I experiments/split_leakage/leak.py
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts  # noqa: E402

RULES = [("exact", 0, False), ("1 edit", 1, False), ("exact or contained", 0, True),
         ("1 edit or contained", 1, True), ("2 edits", 2, False), ("2 edits or contained", 2, True)]
N_SPLITS = 200


def lev_capped(a, b, cap):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        best = cur[0]
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            best = min(best, cur[j])
        if best > cap:
            return cap + 1
        prev = cur
    return prev[-1] if prev[-1] <= cap else cap + 1


def is_copy(d, c, mn, k, contain):
    if d == 0:
        return True
    if d <= k and mn >= 4:
        return True
    return contain and c


def units(dedupe):
    out, seen = [], set()
    for t in sorted(m77_texts(), key=lambda t: (t["text_no"], t["side"])):
        seq = tuple(s for s in t["seq"] if s != "|")
        if not seq:
            continue
        if dedupe:
            if seq in seen:
                continue
            seen.add(seq)
        out.append((t["text_no"], seq))
    return out


def relations(u):
    n = len(u)
    J = [" " + " ".join(s) + " " for _, s in u]
    rel = []  # (i, j, d, contained, minlen), i<j
    for i in range(n):
        si = u[i][1]
        for j in range(i + 1, n):
            sj = u[j][1]
            if len(si) <= len(sj):
                c = len(si) >= 3 and J[i] in J[j]
            else:
                c = len(sj) >= 3 and J[j] in J[i]
            d = lev_capped(si, sj, 2) if abs(len(si) - len(sj)) <= 2 else 3
            if c or d <= 2:
                rel.append((i, j, d, c, min(len(si), len(sj))))
    return rel


def fold(s, obj):
    return int(hashlib.sha256(f"leak:{s}:{obj}".encode()).hexdigest()[:8], 16) % 5


def run(dedupe):
    u = units(dedupe)
    rel = relations(u)
    res = {"n_units": len(u), "n_objects": len({o for o, _ in u})}
    for name, k, contain in RULES:
        nb = defaultdict(set)
        for i, j, d, c, mn in rel:
            if is_copy(d, c, mn, k, contain):
                nb[i].add(j)
                nb[j].add(i)
        shares = []
        for s in range(N_SPLITS):
            f = [fold(s, o) for o, _ in u]
            test = [i for i in range(len(u)) if f[i] == 0 and len(u[i][1]) >= 2]
            shares.append(100 * sum(1 for i in test if any(f[j] != 0 for j in nb[i])) / len(test))
        res[name] = {"median": float(np.median(shares)), "p2.5": float(np.percentile(shares, 2.5)),
                     "p97.5": float(np.percentile(shares, 97.5))}
    return res


def main():
    out = {"A_all_texts": run(False), "B_exact_repeats_removed": run(True)}
    (HERE / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
