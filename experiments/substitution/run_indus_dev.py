"""Indus dev (M77, dev_heldout v2, distinct clean texts) and ICIT (native Wells numbers):
mine X <-> YZ(W) equations, score against the frame-matched permutation null, and the
within-text shuffle null. Writes results.json keys indus_dev, icit_all, shuffle_null.
Usage: .venv/bin/python experiments/substitution/run_indus_dev.py [nperm]
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import (analyse, clean, distinct, dev_heldout, icit_texts, load_icit, load_m77,  # noqa: E402
                    save_results, system_score)


def text_ids_m77():
    dev, ho = dev_heldout(version=2)
    ids = defaultdict(list)
    for t in dev + ho:
        c = clean(t["seq"])
        if c:
            ids[c].append(str(t["text_no"]))
    return ids


def text_ids_icit():
    ids = defaultdict(list)
    for t in distinct(icit_texts()):
        c = clean(t["seq"])
        if c:
            ids[c].append("%s (%s)" % (t["id"], t["site"]))
    return ids


def describe(texts, items, ev, ids, top=25):
    """Attach example text ids to the top equations."""
    g = defaultdict(list)
    for e in ev:
        g[(e["X"], " ".join(e["Y"]))].append(e)
    bigram = Counter()
    for t in texts:
        for k in (2, 3):
            for i in range(len(t) - k + 1):
                bigram[" ".join(t[i:i + k])] += 1
    tok = Counter(x for t in texts for x in t)
    out = []
    for r in items[:top]:
        evs = g[(r["X"], r["Y"])]
        pairs = []
        seen = set()
        for e in evs:
            a, b = texts[e["a"]], texts[e["b"]]
            key = (a, b)
            if key in seen:
                continue
            seen.add(key)
            pairs.append({"X_text": " ".join(a), "X_ids": ids.get(a, [])[:3],
                          "Y_text": " ".join(b), "Y_ids": ids.get(b, [])[:3]})
        d = {k: r[k] for k in ("X", "Y", "k", "lam", "p", "q")}
        d.update(n_X=tok[r["X"]], n_Y_string=bigram[r["Y"]], examples=pairs[:4])
        out.append(d)
    return out


def shuffle_null(texts, nrep=20, nperm=100, seed=0):
    rng = np.random.default_rng(seed)
    res = []
    for i in range(nrep):
        T = []
        for t in texts:
            t = list(t); rng.shuffle(t); T.append(tuple(t))
        T = sorted(set(T))
        out, items, ev, units, eqs = analyse(T, nperm=nperm, seed=i, tier="L")
        res.append(dict(n_events=out["n_events"], G=out["G"], n_sig=out["n_sig_q05"], S=out["S"]))
    return {k: float(np.mean([r[k] for r in res])) for k in res[0]} | {"n_rep": nrep}


if __name__ == "__main__":
    nperm = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    D, H = load_m77()
    ids = text_ids_m77()
    allres = {}
    for tier in ("W", "L"):
        out, items, ev, units, eqs = analyse(D, nperm=nperm, seed=1, tier=tier)
        out["n_texts"] = len(D)
        out["top"] = describe(D, items, ev, ids)
        out["sig"] = [{k: r[k] for k in ("X", "Y", "k", "lam", "p", "q")} for r in items if r["q"] < 0.05]
        # shared signs among significant equations
        sigeq = {(r["X"], tuple(r["Y"].split())): r["k"] for r in items if r["q"] < 0.05}
        out["sig_S"], out["sig_P"] = system_score(sigeq, 1)
        use = defaultdict(set)
        for x, y in sigeq:
            for s in set(y):
                use[s].add(x)
        out["sig_shared_signs"] = sorted([(s, sorted(xs)) for s, xs in use.items() if len(xs) >= 2],
                                         key=lambda z: -len(z[1]))[:15]
        allres[tier] = out
        print("M77 dev tier", tier, {k: v for k, v in out.items() if not isinstance(v, (list, dict))})
        for r in out["top"][:15]:
            print("   %s = %s  k=%d lam=%.3f q=%.2g nX=%d nY=%d  e.g. %s | %s" % (
                r["X"], r["Y"], r["k"], r["lam"], r["q"], r["n_X"], r["n_Y_string"],
                r["examples"][0]["X_ids"], r["examples"][0]["Y_ids"]))
        print("   shared signs among sig:", out["sig_shared_signs"][:8])
    save_results("indus_dev", allres)

    # ICIT, native Wells numbering, all distinct clean texts (same objects mostly)
    I = load_icit()
    iids = text_ids_icit()
    out, items, ev, units, eqs = analyse(I, nperm=nperm, seed=2, tier="L")
    out["n_texts"] = len(I)
    out["top"] = describe(I, items, ev, iids)
    out["sig"] = [{k: r[k] for k in ("X", "Y", "k", "lam", "p", "q")} for r in items if r["q"] < 0.05]
    print("ICIT all L", {k: v for k, v in out.items() if not isinstance(v, (list, dict))})
    for r in out["top"][:15]:
        print("   %s = %s  k=%d lam=%.3f q=%.2g" % (r["X"], r["Y"], r["k"], r["lam"], r["q"]))
    save_results("icit_all", out)

    sn = shuffle_null(D, nrep=10, nperm=100)
    print("within-text shuffle null (M77 dev):", sn)
    save_results("shuffle_null", sn)
