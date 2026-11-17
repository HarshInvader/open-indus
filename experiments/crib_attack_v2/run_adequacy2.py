"""Substitute adequacy check (sumerian was dropped by amendment 1): elamite30, n=41, a=0, shuffle reps 0-9, 4x iters."""
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
    with Pool(2) as p, open(jl, "a") as fh:
        for res in p.imap_unordered(run_grid.job, [("elamite30", 41, 0, "shuffle", r) for r in range(10)]):
            fh.write(json.dumps(res) + "\n"); fh.flush()
