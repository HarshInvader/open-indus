"""Floor experiment (prereg docs/prereg/genre_floor.md). Resumable: out/floor.jsonl.
Usage: board/run.sh .venv/bin/python -I experiments/genre_floor/run.py [KIND ...]"""
import json, sys, warnings
warnings.filterwarnings("ignore")
from multiprocessing import Pool
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import floor  # noqa: E402

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
F = OUT / "floor.jsonl"
GRID = {"NULL": [0.0], "VOC": [0.25, 0.5, 0.75, 1.0], "FORM": [0.25, 0.5, 0.75, 1.0], "LEN": [0.5, 1.0],
        "MIX": [0.15, 0.25, 0.5, 0.75, 1.0], "CUN": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]}
REPS = 10


def job(a):
    kind, s, rep = a
    tr, te = floor.make("MIX" if kind == "NULL" else kind, s, rep)
    rec = dict(kind=kind, s=s, rep=rep, n_tr=len(tr), n_te=len(te),
               gain=floor.lr_gain(tr, te, [u["y"] for u in tr], [u["y"] for u in te]))
    for name in ("HMM", "LCA"):
        rec[name] = floor.detect(name, tr, te, rep)
    return rec


if __name__ == "__main__":
    kinds = sys.argv[1:] or list(GRID)
    done = set()
    if F.exists():
        for l in open(F):
            d = json.loads(l); done.add((d["kind"], d["s"], d["rep"]))
    todo = [(k, s, r) for k in kinds for s in GRID[k] for r in range(REPS) if (k, s, r) not in done]
    with Pool(2) as p:
        for rec in p.imap_unordered(job, todo):
            with open(F, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec["kind"], rec["s"], rec["rep"], round(rec["gain"], 3),
                  {m: (rec[m]["K"], rec[m]["det"]) for m in ("HMM", "LCA")}, flush=True)
