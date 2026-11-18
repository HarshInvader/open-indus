"""name_anchors: how many name-text anchors does success test (b) need? Pre-registration: docs/prereg/name_anchors.md.

    board/run.sh .venv/bin/python -I experiments/name_anchors/run.py           # full grid, 2 workers
    board/run.sh .venv/bin/python -I experiments/name_anchors/run.py smoke     # 1 cell
"""
import sys, json, random, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "decipherability"))
import cells as C  # noqa
from decipher import Corpus, anneal, NV, LOGO  # noqa

LANGS = ["san", "tam", "sux", "lat", "fin"]
WRONG = {"san": "tam", "tam": "san", "sux": "lat", "lat": "fin", "fin": "sux"}
MS = [1, 2, 3, 5, 10]
NWRONG = 19
SW, RS = 60, 2


def syl(v):
    return 0 <= v < NV


def cell(args):
    lang, rep = args
    t0 = time.time()
    seqs, true, oracle, share = C.planted(lang, "names", 10000, 0.2, rep)
    S = int(true.shape[0])
    r = random.Random(rep)
    idx = list(range(len(seqs))); r.shuffle(idx)
    cut = int(0.75 * len(idx))
    dev = [seqs[i] for i in idx[:cut]]; ho = [seqs[i] for i in idx[cut:]]
    cdev, cho = Corpus(dev, S=S), Corpus(ho, S=S)
    d = C.L()
    lms = {"K1": C.LM(d[lang]["K1"], share, True, name="K1"),
           "K3": C.phonotactic_lm(d[lang]["K1"], share, True),
           "W": C.LM(d[WRONG[lang]]["K1"], share, True, name="W")}
    rng = np.random.default_rng(rep * 101 + 7)
    cand = [q for q in dev if 2 <= len(q) <= 6 and sum(syl(int(true[s])) for s in q) >= 2]
    by_len = {}
    for q in dev:
        by_len.setdefault(len(q), []).append(q)
    out = dict(lang=lang, rep=rep, S=S, n_dev=len(dev), n_ho=len(ho), ntok=int(cdev.ntok + cho.ntok), m={})
    syl_mask = np.array([syl(int(v)) for v in true])
    # m = 0 baseline accuracy per LM
    base = {}
    for k, lm in lms.items():
        key, _ = anneal(cdev, lm, rng, sweeps=SW, restarts=RS)
        base[k] = float((cdev.c[syl_mask] * (key[syl_mask] == true[syl_mask])).sum() / cdev.c[syl_mask].sum())
    out["base_acc"] = base
    for m in MS:
        ar = random.Random(7 * rep + m)
        names = ar.sample(cand, m)
        values = [[int(true[s]) for s in q] for q in names]

        def fix_from(texts):
            f = {}
            for q, vals in zip(texts, values):
                for s, v in zip(q, vals):
                    if syl(v) and int(s) not in f:
                        f[int(s)] = v
            return f

        correct = fix_from(names)
        wrongs = []
        for _ in range(NWRONG):
            alt = [ar.choice([q for q in by_len[len(n)] if q is not n] or [n]) for n in names]
            wrongs.append(fix_from(alt))
        cov = float(cdev.c[list(correct)].sum() / cdev.ntok) if correct else 0.0
        res = dict(n_fixed=len(correct), token_cover=cov, lm={})
        for k, lm in lms.items():
            kc, _ = anneal(cdev, lm, rng, sweeps=SW, restarts=RS, fixed=correct)
            sc_c = cho.score(kc, lm)
            free = syl_mask.copy(); free[list(correct)] = False
            acc_free = float((cdev.c[free] * (kc[free] == true[free])).sum() / max(cdev.c[free].sum(), 1))
            sc_w = []
            for f in wrongs:
                kw, _ = anneal(cdev, lm, rng, sweeps=SW, restarts=RS, fixed=f)
                sc_w.append(cho.score(kw, lm))
            rank = 1 + sum(w >= sc_c for w in sc_w)
            res["lm"][k] = dict(ho_correct=sc_c, ho_wrong=sc_w, rank=rank, passed=rank == 1, acc_free=acc_free)
        out["m"][m] = res
    out["secs"] = time.time() - t0
    with open(HERE / "cells.jsonl", "a") as fh:
        fh.write(json.dumps(out) + "\n")
    return lang, rep, out["secs"]


def summarise():
    rows = [json.loads(l) for l in open(HERE / "cells.jsonl")]
    summ = {}
    for m in MS:
        s = {}
        for k in ("K1", "K3", "W"):
            cs = [r["m"][str(m)]["lm"][k] for r in rows]
            s[k] = dict(power=float(np.mean([c["passed"] for c in cs])), n=len(cs),
                        median_rank=float(np.median([c["rank"] for c in cs])),
                        acc_free=float(np.mean([c["acc_free"] for c in cs])),
                        base_acc=float(np.mean([r["base_acc"][k] for r in rows])))
        s["n_fixed"] = float(np.mean([r["m"][str(m)]["n_fixed"] for r in rows]))
        s["token_cover"] = float(np.mean([r["m"][str(m)]["token_cover"] for r in rows]))
        summ[m] = s
    mstar = {k: next((m for m in MS if summ[m][k]["power"] >= 0.8), None) for k in ("K1", "K3", "W")}
    json.dump(dict(summary=summ, m_star=mstar, n_cells=len(rows)), open(HERE / "results.json", "w"), indent=1)
    return summ, mstar


if __name__ == "__main__":
    if sys.argv[1:] == ["summary"]:
        print(json.dumps(summarise(), indent=1)); sys.exit()
    jobs = [(l, r) for r in range(3) for l in LANGS]
    if sys.argv[1:] == ["smoke"]:
        global_ms = MS
        print(cell(("lat", 0))); sys.exit()
    (HERE / "cells.jsonl").unlink(missing_ok=True)
    with Pool(2) as p:
        for lang, rep, secs in p.imap_unordered(cell, jobs):
            print(lang, rep, round(secs), flush=True)
    s, ms = summarise()
    print(json.dumps(ms))
