"""language_id (board #32): can 1-3 name anchors pick the language? Pre-registration: docs/prereg/language_id.md.

    board/run.sh .venv/bin/python -I experiments/language_id/run.py          # 12 cells, 2 workers
    board/run.sh .venv/bin/python -I experiments/language_id/run.py summary
"""
import sys, json, random, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "decipherability"))
import cells as C  # noqa
from decipher import Corpus, anneal, NV  # noqa

TRUE = ["san", "tam", "lat", "fin"]
ALL = ["san", "tam", "sux", "lat", "fin"]
MS = [1, 2, 3]
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
    others = [o for o in ALL if o != lang]
    lms = {f"K1:{o}": C.LM(d[o]["K1"], share, True, name=o) for o in others}
    lms["TRUE"] = C.LM(d[lang]["K1"], share, True, name=lang)
    lms["REL"] = C.LM(d[lang]["K2"], share, True, name=lang + ":K2")
    rng = np.random.default_rng(rep * 211 + 3)
    cand = [q for q in dev if 2 <= len(q) <= 6 and sum(syl(int(true[s])) for s in q) >= 2]
    by_len = {}
    for q in dev:
        by_len.setdefault(len(q), []).append(q)
    out = dict(lang=lang, rep=rep, m={})
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
        wrongs = [fix_from([ar.choice([q for q in by_len[len(n)] if q is not n] or [n]) for n in names]) for _ in range(NWRONG)]
        z = {}
        for k, lm in lms.items():
            kc, _ = anneal(cdev, lm, rng, sweeps=SW, restarts=RS, fixed=correct)
            sc = cho.score(kc, lm)
            ws = [cho.score(anneal(cdev, lm, rng, sweeps=SW, restarts=RS, fixed=f)[0], lm) for f in wrongs]
            z[k] = dict(z=float((sc - np.mean(ws)) / (np.std(ws, ddof=1) + 1e-9)), rank=1 + sum(w >= sc for w in ws))
        out["m"][m] = z
    out["secs"] = time.time() - t0
    with open(HERE / "cells.jsonl", "a") as fh:
        fh.write(json.dumps(out) + "\n")
    return lang, rep, out["secs"]


def summarise():
    rows = [json.loads(l) for l in open(HERE / "cells.jsonl")]
    summ = {}
    for m in MS:
        s = {}
        for cond, right in (("EXACT", "TRUE"), ("RELATIVE", "REL")):
            picks, ranks, sig = [], [], []
            for r in rows:
                z = r["m"][str(m)]
                cands = [right] + [k for k in z if k.startswith("K1:")]
                order = sorted(cands, key=lambda k: -z[k]["z"])
                picks.append(order[0] == right); ranks.append(order.index(right) + 1); sig.append(z[right]["z"] > 1.645)
            s[cond] = dict(power=float(np.mean(picks)), median_rank=float(np.median(ranks)), z_sig=float(np.mean(sig)), n=len(rows))
        summ[m] = s
    feasible = any(summ[m]["RELATIVE"]["power"] >= 0.8 for m in (1, 2))
    json.dump(dict(summary=summ, feasible_relative=feasible, n_cells=len(rows)), open(HERE / "results.json", "w"), indent=1)
    return summ, feasible


if __name__ == "__main__":
    if sys.argv[1:] == ["summary"]:
        print(json.dumps(summarise(), indent=1)); sys.exit()
    (HERE / "cells.jsonl").unlink(missing_ok=True)
    jobs = [(l, r) for r in range(3) for l in TRUE]
    with Pool(2) as p:
        for lang, rep, secs in p.imap_unordered(cell, jobs):
            print(lang, rep, round(secs), flush=True)
    print(json.dumps(summarise()[1]))
