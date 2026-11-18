"""A1 development on KNOWN-ANSWER corpora only (cun to choose beta; lat to confirm). Never touches Indus.
Usage: board/run.sh .venv/bin/python -I experiments/genres_scratch/tune_bg2.py"""
import json, sys
from multiprocessing import Pool
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import gs, data

def job(a):
    corpus, beta = a
    gs.BG2.beta = beta
    tr, te, _ = data.known(corpus)
    res = gs.cv_curve("BG2", tr, list(range(1, 9)), folds=5, seed=0, restarts=2)
    K, means, best = gs.pick_K(res)
    m = gs.BG2().fit(tr, K, seed=0, restarts=3)
    m4 = gs.BG2().fit(tr, 4, seed=0, restarts=3)
    y = [u["genre"] for u in te]
    return dict(corpus=corpus, beta=beta, K=K, best=best, cv={k: round(v, 3) for k, v in means.items()},
                ari=gs.ari(m.assign(te), y), ari4=gs.ari(m4.assign(te), y))

if __name__ == "__main__":
    out = HERE / "out/tune_bg2.jsonl"
    with Pool(2) as p:
        for r in p.imap_unordered(job, [(c, b) for c in ("cun", "lat") for b in (5.0, 20.0, 80.0)]):
            print(r, flush=True); open(out, "a").write(json.dumps(r) + "\n")
