"""Run the language_vs_code battery (imported unchanged) on every short-label system at Indus size.

usage: .venv/bin/python experiments/short_labels/sl_calibrate.py [R]   -> out/calib.jsonl
Sizes: A = 565 texts with the held-out Indus length list (lengths only; no held-out sign is read);
       B = 150 texts with a fixed random subset of that length list (admits small real systems).
A system enters a size only if its pool of whole units (length 1..17) has >= N units.
"""
import sys, json, random, zlib
from multiprocessing import Pool
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "experiments/language_vs_code"))
from sl_corpora import REG, pool, indus  # noqa
from lvc_metrics import battery, matched_sample  # noqa

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
P = None; LENS = None


def lens():
    ho = [len(t) for t in indus("heldout")]
    rng = random.Random(150)
    return {"A": ho, "B": rng.sample(ho, 150)}


def init():
    global P, LENS
    P = {k: pool(k) for k in REG}
    LENS = lens()


def job(args):
    name, size, r = args
    rng = random.Random(zlib.crc32(f"{name}|{size}|{r}".encode()))
    S = matched_sample(P[name], LENS[size], rng)
    res = battery(S, seed=r)
    lab, fam, st, _ = REG[name]
    res.update(corpus=name, label=lab, family=fam, set=st, size=size, rep=r, n=len(S),
               mean_len=sum(map(len, S)) / len(S), types=len({s for t in S for s in t}), pool=len(P[name]))
    return res


if __name__ == "__main__":
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    init()
    jobs = [(k, s, r) for k in REG for s in ("A", "B") if len(P[k]) >= len(LENS[s]) for r in range(R)]
    skipped = [(k, s) for k in REG for s in ("A", "B") if len(P[k]) < len(LENS[s])]
    print("skipped (pool too small):", skipped, flush=True)
    with Pool(2, initializer=init) as p, open(OUT / "calib.jsonl", "w") as f:
        for i, res in enumerate(p.imap_unordered(job, jobs, chunksize=2)):
            f.write(json.dumps(res, default=float) + "\n"); f.flush()
            if i % 200 == 0: print(i, len(jobs), res["corpus"], res["size"], flush=True)
