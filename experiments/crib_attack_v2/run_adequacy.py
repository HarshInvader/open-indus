"""Pre-registered search-adequacy check: shuffle condition, (sumerian|gulf, n=41, a=0), reps 0-9,
same corpora/seeds as the grid but 4x iterations.  Appends to out/adequacy.jsonl (resumable)."""
import sys, json
from pathlib import Path
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_grid  # noqa

_base = run_grid.iters_for
run_grid.iters_for = lambda n: 4 * _base(n)

if __name__ == "__main__":
    jl = HERE / "out" / "adequacy.jsonl"
    done = set()
    if jl.exists():
        done = {(r["list"], r["rep"]) for r in map(json.loads, open(jl))}
    jobs = [(t, 41, 0, "shuffle", r) for t in ("sumerian", "gulf") for r in range(10) if (t, r) not in done]
    with Pool(2) as p, open(jl, "a") as fh:
        for res in p.imap_unordered(run_grid.job, jobs):
            fh.write(json.dumps(res) + "\n"); fh.flush()
    print("done", flush=True)
