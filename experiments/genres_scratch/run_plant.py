"""Planted-genre power on real M77 texts (prereg section 'Planted-genre controls').
Fake labels by family 70/20/10; in the two minority classes each token is replaced with prob f by a
class-specific substitute (cyclic shift inside blocks of 5 neighbouring frequency ranks).
Same pipeline as run_main but 3-fold CV, K in 1..6.  Resumable: out/plant.jsonl.
Usage: board/run.sh .venv/bin/python -I experiments/genres_scratch/run_plant.py
"""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gs  # noqa: E402
import data  # noqa: E402

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
F = OUT / "plant.jsonl"
FS = [0.0, 0.15, 0.30, 0.50, "synth"]
REPS = 5
MODELS = ["BG2", "LCA", "HMM"]  # amendment A1: LDA dropped, BG2 added


def plant(f, rep):
    dev, ho = data.m77()
    rng = random.Random(1000 * rep + int(f * 100))
    allsig = Counter(x for u in dev + ho for x in u["signs"])
    ranked = [s for s, _ in allsig.most_common()]
    subs = {}
    for c in (1, 2):
        m = {}
        for b in range(0, len(ranked), 5):
            blk = ranked[b:b + 5]
            if len(blk) < 2:
                m[blk[0]] = blk[0]; continue
            off = rng.randint(1, len(blk) - 1)
            for i, s in enumerate(blk):
                m[s] = blk[(i + off) % len(blk)]
        subs[c] = m
    out = []
    for us in (dev, ho):
        fam = gs.glib.families(us)
        ids = sorted(set(fam)); rng.shuffle(ids)
        # fix (v2): quota fill so one chained giant family cannot swallow a minority class
        cnt = Counter(fam); lab = {}
        quota = {1: 0.2 * len(us), 2: 0.1 * len(us)}
        for fa in ids:
            lab[fa] = 0
            for c in (1, 2):
                if cnt[fa] <= quota[c]:
                    lab[fa] = c; quota[c] -= cnt[fa]; break
        new = []
        for u, fa in zip(us, fam):
            c = lab[fa]
            runs = []
            for r, b, e in u["runs"]:
                if c:
                    r = tuple(subs[c][x] if rng.random() < f else x for x in r)
                runs.append((r, b, e))
            new.append(dict(runs=runs, full=u["full"], signs=tuple(x for r, _, _ in runs for x in r),
                            fake=str(c), obj=u["obj"]))
        out.append(new)
    return out


def synth(rep):
    """negative control: corpora drawn from ONE bigram model fitted to all M77 texts"""
    dev, ho = data.m77()
    m = gs.BG().fit(dev + ho, 1, seed=rep, restarts=1)
    P = np.exp(m.params["lP"][0]); V = m.enc.V
    names = m.enc.vocab + ["<UNK>"]
    rng = np.random.default_rng(500 + rep)
    def gen():
        s, a = [], V
        while len(s) < 17:
            b = rng.choice(V + 1, p=P[a] / P[a].sum())
            if b == V:
                break
            s.append(names[b]); a = b
        return s or [names[rng.integers(V)]]
    out = []
    for n in (len(dev), len(ho)):
        us = []
        for _ in range(n):
            s = gen()
            us.append(dict(runs=[(tuple(s), True, True)], full=True, signs=tuple(s), fake="0", obj="x"))
        out.append(us)
    return out


def s1(name, m, m1, te):
    import run_main
    d = m.loglik(te) - m1.loglik(te)
    ci = run_main.fam_boot_diff(te, d, n=300)
    return ci


def job(args):
    f, rep = args
    tr, te = synth(rep) if f == "synth" else plant(f, rep)
    rec = dict(f=f, rep=rep)
    rec["nb_gain"] = gs.nb_gain(tr, te, [u["fake"] for u in tr], [u["fake"] for u in te]) if f != "synth" else None
    for name in MODELS:
        res = gs.cv_curve(name, tr, list(range(1, 7)), folds=3, seed=rep, restarts=1 if name == "HMM" else 2)
        K, means, best = gs.pick_K(res)
        m = gs.MODELS[name]().fit(tr, K, seed=rep, restarts=1 if name == "HMM" else 2)
        m1 = gs.MODELS[name]().fit(tr, 1, seed=rep, restarts=1)
        ci = s1(name, m, m1, te)
        gd, gh = m.assign(tr), m.assign(te)
        if f == "synth":
            rec[name] = dict(K=K, ci=ci, S1=bool(K >= 2 and ci[0] > 0), p=1.0); continue
        r = gs.assoc_test(gd, [u["fake"] for u in tr], gh, [u["fake"] for u in te], K, nperm=500, seed=rep)
        r["K"] = K; r["ci"] = ci; r["S1"] = bool(K >= 2 and ci[0] > 0); r["ari"] = gs.ari(gh, [u["fake"] for u in te])
        rec[name] = r
    return rec


if __name__ == "__main__":
    done = set()
    if F.exists():
        for l in open(F):
            d = json.loads(l); done.add((d["f"], d["rep"]))
    todo = [(f, r) for r in range(REPS) for f in FS if (f, r) not in done]
    todo.sort(key=lambda x: (x[0] != "synth", str(x[0])))
    if "--real" in sys.argv:
        dev, ho = data.m77()
        real = {lab: gs.nb_gain(dev, ho, [u[lab] for u in dev], [u[lab] for u in ho]) for lab in ("obj", "site")}
        json.dump(real, open(OUT / "nb_real.json", "w")); print(real)
        sys.exit()
    with Pool(2) as p:
        for rec in p.imap_unordered(job, todo):
            with open(F, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec["f"], rec["rep"], {m: (rec[m]["K"], round(rec[m]["p"], 3)) for m in MODELS}, flush=True)
