"""Wiring of the frozen procedure (sl.py) to a corpus: shape + context similarity, greedy merges in 3 modes,
merge path, held-out scoring. Used by ka.py (known-answer) and indus.py."""
import random
import numpy as np
import sl


def build_sims(train, pool, masks):
    """pool: list of sign names with masks[name]. -> (S_shape, S_ctx) percentile similarity matrices."""
    Dh, Dc = sl.shape_matrix([masks[s] for s in pool])
    S_shape = (sl.pct_sim(Dh) + sl.pct_sim(Dc)) / 2
    C = sl.context_sim(train, pool)
    S_ctx = sl.pct_sim(1 - C)
    return S_shape, S_ctx, Dh, Dc, C


def heldout_ll(cls, train, test, order=3):
    m = sl.ClassLM(cls, order).fit(train)
    per = []
    for q in test:
        ll, n = m.score([q])
        per.append((ll, n))
    return per


def boot_diff(per_a, per_b, B=1000, seed=0):
    """per-token LL difference a - b with bootstrap 95% CI over texts."""
    a = np.array(per_a); b = np.array(per_b)
    assert (a[:, 1] == b[:, 1]).all()
    n = a[:, 1].sum()
    d = (a[:, 0].sum() - b[:, 0].sum()) / n
    r = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        i = r.integers(0, len(a), len(a))
        bs.append((a[i, 0].sum() - b[i, 0].sum()) / a[i, 1].sum())
    return {"d_per_tok": d, "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "total_d": float(a[:, 0].sum() - b[:, 0].sum())}


def merge_path(train, test, cands, step=10, B=1000, seed=0, max_merges=None):
    """apply candidates in order; held-out per-text LL every `step` merges -> argmax n_labels with bootstrap."""
    signs = sorted({s for q in train + test for s in q})
    uf = sl.UF()
    pts = []

    def rec(k):
        mp = uf.mapping(signs)
        per = heldout_ll(mp, train, test)
        pts.append({"merges": k, "n_labels": len(set(mp.values())), "per": per})

    rec(0)
    k = 0
    for a, b, _ in cands[: max_merges or len(cands)]:
        if uf.find(a) == uf.find(b):
            continue
        uf.union(a, b); k += 1
        if k % step == 0:
            rec(k)
    if k % step:
        rec(k)
    M = np.array([[x[0] for x in p["per"]] for p in pts])   # points x texts
    tot = M.sum(1)
    best = int(tot.argmax())
    r = np.random.default_rng(seed)
    am = []
    for _ in range(B):
        i = r.integers(0, M.shape[1], M.shape[1])
        am.append(pts[int(M[:, i].sum(1).argmax())]["n_labels"])
    ntok = sum(x[1] for x in pts[0]["per"])
    return {"curve": [(p["merges"], p["n_labels"], float(t / ntok)) for p, t in zip(pts, tot)],
            "argmax_labels": pts[best]["n_labels"], "argmax_merges": pts[best]["merges"],
            "boot95": [float(np.percentile(am, 2.5)), float(np.percentile(am, 97.5))],
            "n_labels_start": pts[0]["n_labels"]}


def run_modes(train, pool, masks, modes=("both", "ctx", "shape"), log=print, max_cands=300):
    S_shape, S_ctx, *_ = build_sims(train, pool, masks)
    out = {}
    for mode in modes:
        cands = sl.candidate_pairs(pool, S_shape, S_ctx, mode)
        acc, mp = sl.greedy(train, cands, max_cands=max_cands)
        log(f"[{mode}] candidates {len(cands)}, accepted {len(acc)}")
        out[mode] = {"cands": cands, "accepted": acc, "mapping": mp}
    return out, S_shape, S_ctx
