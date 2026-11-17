"""Search-strength check: does annealing reach the TRUE key's score? (dev only on planted corpora)"""
import sys, time, numpy as np
import cells
from decipher import Corpus, anneal, accuracy

cfgs = [dict(T0=1.0, T1=0.01, sweeps=80, restarts=2), dict(T0=3.0, T1=0.01, sweeps=150, restarts=2),
        dict(T0=0.5, T1=0.005, sweeps=150, restarts=4), dict(T0=8.0, T1=0.02, sweeps=150, restarts=2, per_token=False)]
for lang, genre, ntok, logo in [("lat", "names", 10000, 0.0), ("san", "names", 10000, 0.3), ("sux", "names", 10000, 0.3)]:
    seqs, true, oracle, share = cells.planted(lang, genre, ntok, logo, 0)
    lms = cells.build_lms(lang, genre, share, oracle, ["K1", "K3"])
    corp = Corpus(seqs)
    for k, lm in lms.items():
        tsc = corp.score(true, lm)
        for c in cfgs:
            t = time.time(); rng = np.random.default_rng(0)
            key, sc = anneal(corp, lm, rng, **c)
            print(lang, k, c, "best-true=%.0f" % (sc - tsc), "acc=%.3f" % accuracy(key, true, corp.c)[0],
                  "%.1fs" % (time.time() - t), flush=True)
        # polish from the true key: is the true key a local optimum?
        key, sc = anneal(corp, lm, np.random.default_rng(0), sweeps=0, restarts=1, init_key=true)
        print(lang, k, "from-true polish best-true=%.0f acc=%.3f" % (sc - tsc, accuracy(key, true, corp.c)[0]))
