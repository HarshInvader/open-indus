"""Run the discriminator battery on every comparator at Indus size and length mix.

usage: lvc_calibrate.py [R]      -> out/calib.jsonl (one row per corpus x size x replicate)
Sizes: N_dev (1680 texts, Indus dev length mix) and N_ho (565, held-out length mix). Held-out Indus
texts are used ONLY for their length list (no signs), so calibration at held-out size is blind.
"""
import sys, json, random, zlib
from multiprocessing import Pool
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lvc_corpora import load_all, indus  # noqa
from lvc_metrics import battery, matched_sample  # noqa

R = int(sys.argv[1]) if len(sys.argv) > 1 else 25
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
C = None
LENS = None


def init():
    global C, LENS
    C = load_all()
    LENS = {"dev": [len(t) for t in indus("dev")], "heldout": [len(t) for t in indus("heldout")]}


def job(args):
    name, size, r = args
    rng = random.Random(zlib.crc32(f"{name}|{size}|{r}".encode()))
    lab, X = C[name]
    S = matched_sample(X, LENS[size], rng)
    res = battery(S, seed=r)
    res.update(corpus=name, label=lab, size=size, rep=r, n=len(S),
               mean_len=sum(map(len, S)) / len(S), types=len({s for t in S for s in t}))
    return res


if __name__ == "__main__":
    init()
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None   # e.g. W_ (prefix) to append
    keys = [k for k in C if not only or any(k.startswith(o) for o in only)]
    jobs = [(k, s, r) for k in keys for s in ("dev", "heldout") for r in range(R)]
    with Pool(2, initializer=init) as p, open(OUT / "calib.jsonl", "a" if only else "w") as f:
        for i, res in enumerate(p.imap_unordered(job, jobs, chunksize=2)):
            f.write(json.dumps(res) + "\n"); f.flush()
            if i % 50 == 0: print(i, len(jobs), res["corpus"], res["size"], flush=True)
