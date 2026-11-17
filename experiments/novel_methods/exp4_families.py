"""Exp 4. Near-duplicate families and 'stemmatics' (manuscript stemmatology /
phylogenetics of variants).

Q1 Are near-duplicate families 'columns' (all members differ at ONE position:
   a paradigm slot, like a form with one blank) or 'trees' (variants differ at
   different positions, chains of copying/abbreviation)? Compare with nulls
   (bigram, trigram) and comparison corpora (seal legends, slot code).
Q2 Inventory of the best minimal-pair sets (frames with >=3 fillers) for
   decipherment, with sites/objects. Descriptive: uses ALL distinct M77 texts
   (dev + held-out), flagged as such; claims rest on Q1 (dev only).
"""
from itertools import combinations

from common import *
from exp1_minimal_pairs import neighbours, MINLEN


def family_shapes(texts):
    pr = neighbours(texts)
    n = len(texts)
    parent = list(range(n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, j, *_ in pr:
        parent[f(i)] = f(j)
    edges = defaultdict(list)
    for i, j, kind, (p, L), a, b in pr:
        # describe the variable position from the right edge too (closer-anchored)
        edges[f(i)].append((kind, p, L))
    comp = Counter(f(i) for i in range(n))
    col = tree = 0; sizes = []
    for c, sz in comp.items():
        if not (3 <= sz <= 12):
            continue
        es = edges[c]
        # single column: all edges are substitutions at the same absolute position
        # in texts of the same length
        keyset = {(k, p, L) for k, p, L in es}
        if all(k == "sub" for k, _, _ in es) and len({(p, L) for _, p, L in es}) == 1:
            col += 1
        else:
            tree += 1
        sizes.append(sz)
    tot = col + tree
    # cyclomatic number of the ED-1 graph restricted to small families
    return dict(n_families=tot, column_share=col / tot if tot else np.nan, mean_size=float(np.mean(sizes)) if sizes else 0)


def main():
    rng = np.random.default_rng(11)
    D, H = load_split()
    res = {"indus_dev": family_shapes(D)}
    m1, m2 = Markov(D, 1), Markov(D, 2)
    for name, gen in [("bigram", lambda: null_corpus(D, rng, model=m1)),
                      ("trigram", lambda: null_corpus(D, rng, model=m2)),
                      ("names", lambda: names_corpus(len(D), rng)),
                      ("slotcode", lambda: slotcode_corpus(len(D), rng))]:
        vals = [family_shapes(gen()) for _ in range(10)]
        res[name] = {k: (float(np.nanmean([v[k] for v in vals])), float(np.nanstd([v[k] for v in vals]))) for k in vals[0]}
    res["indus_heldout"] = family_shapes(H)
    for k, v in res.items():
        print(k, v)

    # ---- Q2 inventory over ALL distinct M77 texts with metadata
    recs_d, recs_h = load_split_records()
    meta = defaultdict(set)
    for r in recs_d + recs_h:
        meta[clean(r["seq"])].add((r["site"], r["object_type"]))
    ALL = sorted(meta)
    frames = defaultdict(set)
    for t in ALL:
        if len(t) < MINLEN:
            continue
        for p in range(len(t)):
            frames[(t[:p], len(t) - p - 1, t[p + 1:])].add(t[p])
    inv = []
    for (pre, kfromend, suf), fill in frames.items():
        if len(fill) >= 3:
            texts = [pre + (x,) + suf for x in fill]
            sites = sorted({s for tx in texts for s, _ in meta[tx]})
            pos = "first" if not pre else ("last" if not suf else "mid")
            inv.append(dict(frame=" ".join(pre) + " [_] " + " ".join(suf), pos=pos, n_fillers=len(fill),
                            fillers=sorted(fill), sites=sites))
    inv.sort(key=lambda r: (-r["n_fillers"], r["frame"]))
    res["minimal_pair_sets"] = inv[:80]
    res["n_frames_ge3"] = len(inv)
    res["frames_by_pos"] = dict(Counter(r["pos"] for r in inv))
    print("\nframes with >=3 fillers:", len(inv), res["frames_by_pos"])
    for r in inv[:45]:
        print(r["n_fillers"], r["pos"], "|", r["frame"], "|", " ".join(r["fillers"]), "|", ",".join(r["sites"]))
    # longest frames (most context = most informative minimal pairs)
    longf = sorted([r for r in inv], key=lambda r: -len(r["frame"].split()))[:25]
    res["longest_frames"] = longf
    print("\nlongest-context frames:")
    for r in longf:
        print(r["n_fillers"], r["pos"], "|", r["frame"], "|", " ".join(r["fillers"]), "|", ",".join(r["sites"]))
    save_json("exp4_families", res)


if __name__ == "__main__":
    main()
