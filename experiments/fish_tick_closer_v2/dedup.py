"""fish_tick_closer_v2: non-chaining de-duplication. Prereg: docs/prereg/fish_tick_closer_v2.md.

Unit (frozen):
  1. exact distinct texts (corpus/load.py::distinct on the full sequence);
  2. texts with the same sign string after removing '|' and '#' are one text (first kept);
  3. greedy pass, longest first (ties: lexicographic sequence string). A candidate text is DROPPED only if
     it has >= 4 signs AND it is within one edit (substitution, insertion or deletion) of, or a contiguous
     part of, a text ALREADY KEPT. No chaining: a dropped text never causes any other text to be dropped.
     Texts with fewer than 4 signs are never dropped by step 3.
"""
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fish_tick_closer"))
import ftc  # noqa: E402

L = ftc.L
MIN_DROP = 4


def signs(t):
    return [s for s in t["seq"] if s not in ("|", "#")]


def near(cand, kept):
    """cand (shorter or equal, >= MIN_DROP signs) is contained in, or within one edit of, kept."""
    lc, lk = len(cand), len(kept)
    if lc < MIN_DROP or lc > lk + 1:
        return False
    if lc <= lk:
        for i in range(lk - lc + 1):
            if kept[i:i + lc] == cand:
                return True
    if lc == lk:
        return sum(x != y for x, y in zip(cand, kept)) <= 1
    a, b = (cand, kept) if lc < lk else (kept, cand)  # one insertion/deletion
    if len(b) - len(a) != 1:
        return False
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def greedy(texts, return_info=False):
    T = L.distinct(texts)
    T = [t for t in T if signs(t)]
    T.sort(key=lambda t: (-len(signs(t)), " ".join(t["seq"])))
    kept, ks, seen = [], [], {}
    drop_onto = Counter()
    n_exact = 0
    for t in T:
        sg = signs(t)
        key = " ".join(sg)
        if key in seen:
            n_exact += 1; drop_onto[seen[key]] += 1
            continue
        hit = None
        if len(sg) >= MIN_DROP:
            for j, k in enumerate(ks):
                if near(sg, k):
                    hit = j; break
        if hit is not None:
            drop_onto[hit] += 1
            seen[key] = hit
            continue
        seen[key] = len(kept)
        kept.append(t); ks.append(sg)
    kept_sorted = sorted(kept, key=lambda t: " ".join(t["seq"]))
    if not return_info:
        return kept_sorted
    info = dict(n_input_distinct=len(T), n_kept=len(kept), n_dropped_same_signs=n_exact,
                n_dropped_near=len(T) - len(kept) - n_exact,
                largest_cluster=(1 + max(drop_onto.values())) if drop_onto else 1)
    return kept_sorted, info


def v1_family_stats(texts):
    """Same union-find as ftc.collapse, returning family sizes."""
    T = L.distinct(texts)
    sg = [[s for s in t["seq"] if s not in ("|", "#")] for t in T]
    n = len(T); par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if sg[i] and sg[j] and ftc._close(sg[i], sg[j]):
                par[find(i)] = find(j)
    sizes = Counter(find(i) for i in range(n))
    return dict(n_input_distinct=n, n_families_kept=len(sizes), largest_family=max(sizes.values()))


def load_sets():
    dev, ho = L.dev_heldout(version=2)
    new = [t for t in L.icit_texts() if t["site"] in ftc.POST1977]
    return {"DEV": (ftc.prep(greedy(dev)), ftc.Scheme(False)), "HELD": (ftc.prep(greedy(ho)), ftc.Scheme(False)),
            "NEW": (ftc.prep(greedy(new)), ftc.Scheme(True))}


def raw_sets():
    dev, ho = L.dev_heldout(version=2)
    new = [t for t in L.icit_texts() if t["site"] in ftc.POST1977]
    return {"DEV": dev, "HELD": ho, "NEW": new}
