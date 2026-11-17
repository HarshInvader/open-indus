"""Shared helpers: restart search, lexicon builders, nulls."""
import numpy as np, random, sys
from pathlib import Path
import wm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/decipherability"))
import langdata as LD  # noqa: E402

_L = None


def L():
    global _L
    if _L is None: _L = LD.load()
    return _L


def types_of(texts):
    out, seen = [], set()
    for t in texts:
        for w in t:
            if w and w not in seen: seen.add(w); out.append(w)
    return out


def sample_lex(words, n, rng, minsyl=1, maxsyl=8, exclude=()):
    vals = [v for v in wm_lex(words, minsyl, maxsyl) if tuple(v) not in exclude]
    if len(vals) > n:
        idx = rng.choice(len(vals), n, replace=False); vals = [vals[i] for i in sorted(idx)]
    return vals


def wm_lex(words, minsyl=1, maxsyl=8):
    out, seen = [], set()
    for w in words:
        if not w or w in seen: continue
        v = [LD.VIDX[x] for x in LD.syllabify(w)]
        if minsyl <= len(v) <= maxsyl:
            seen.add(w); out.append(v)
    return out


def shuffle_lex(lex, rng):
    """values permuted across all entries, entry lengths kept (destroys real word forms)"""
    flat = np.array([x for l in lex for x in l]); rng.shuffle(flat)
    out, i = [], 0
    for l in lex:
        out.append(list(flat[i:i + len(l)])); i += len(l)
    return out


def shuffle_words(words, rng):
    """signs permuted across all words (frequency-matched shuffled corpus), lengths kept; distinct kept"""
    flat = np.array([x for w in words for x in w]); rng.shuffle(flat)
    out, i = [], 0
    for w in words:
        out.append(tuple(flat[i:i + len(w)])); i += len(w)
    return out


def search(words, wcount, lex, S, true=None, restarts=24, seed=0, oracle=True, soft_every=2, iters=12,
           gold=None, **kw):
    """restart search (alternating hard EM and annealed soft EM). gold: per word set of correct lexicon idx."""
    M = wm.Model(words, wcount, lex, S, **kw)
    rng = np.random.default_rng(seed)
    runs = []
    for r in range(restarts):
        init = M.random_init(rng, "freq" if r % 2 == 0 else "uniform")
        if soft_every and r % soft_every == 1:
            o = M.run_soft(init, rng=rng, noise=0.5, iters=iters)
        else:
            o = M.run(init, iters=iters)
        runs.append(o)
    best = max(runs, key=lambda x: x["score"])
    ntok = float(M.cnt.sum())
    res = dict(score=best["score"], score_tok=best["score"] / ntok, n_matched=int((best["match"] >= 0).sum()),
               nwords=len(words), ntok=ntok, nlex=len(lex), S=S,
               restart_scores=[round(r["score"], 1) for r in runs])
    if true is not None:
        key = M.decode(best["sub"])
        res["acc_tok"], res["acc_typ"] = wm.accuracy(key, true, M.cnt)
        res["acc_cons_tok"] = wm.accuracy(key, true, M.cnt, wm.cons_ok)[0]
        res["restart_acc"] = [round(wm.accuracy(M.decode(r["sub"]), true, M.cnt)[0], 3) for r in runs]
        if oracle:
            tk = np.where(true < wm.NV, true, -1)
            orc = M.run(M.key_counts(tk), iters=iters)
            res["oracle_score"] = orc["score"]
            res["oracle_acc_tok"] = wm.accuracy(M.decode(orc["sub"]), true, M.cnt)[0]
            res["wrong_beats_oracle"] = bool(best["score"] > orc["score"] + 1e-6 and res["acc_tok"] < 0.5)
            res["search_found_oracle_basin"] = bool(best["score"] >= orc["score"] - 1e-6 or res["acc_tok"] >= 0.5)
            if gold is not None:
                res["oracle_cognate_acc"] = cognate_acc(orc["match"], gold)
    if gold is not None:
        res["cognate_acc"] = cognate_acc(best["match"], gold)
    res["_word_scores"] = best["msc"]
    res["_best"] = best; res["_M"] = M
    return res


def cognate_acc(match, gold):
    n = sum(1 for g in gold if g)
    ok = sum(1 for m, g in zip(match, gold) if g and m in g)
    return ok / max(n, 1)


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}
