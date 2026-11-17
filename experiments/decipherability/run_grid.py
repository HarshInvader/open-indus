"""Run the planted-answer grid in parallel. Appends one JSON line per cell to out/<name>.jsonl.
usage: .venv/bin/python experiments/decipherability/run_grid.py names|prose|anchors [nproc]"""
import sys, json, os, itertools, traceback
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells

OUT = Path(__file__).resolve().parent / "out"


def job(args):
    kw = args.pop("kw", {})
    try:
        return cells.run_cell(**args, **kw)
    except Exception as e:
        return dict(error=traceback.format_exc(), **args)


def plan(name):
    J = []
    if name == "names":
        for ntok, logo, rep, lang in itertools.product([2500, 5000, 10000, 25000, 50000, 100000, 230000],
                                                       [0.0, 0.2, 0.4, 0.6], [0, 1], cells.LANGS):
            J.append(dict(lang=lang, genre="names", ntok=ntok, logo=logo, rep=rep, kw=dict(nshuf=2)))
    elif name == "prose":
        for ntok, logo, rep, lang in itertools.product([2500, 5000, 10000, 25000, 45000], [0.0, 0.3, 0.6], [0, 1],
                                                       ["san", "tam", "lat", "fin"]):
            J.append(dict(lang=lang, genre="prose", ntok=ntok, logo=logo, rep=rep, kw=dict(nshuf=2)))
    elif name == "anchors":
        for logo, rep, lang in itertools.product([0.2, 0.4], [0, 1, 2], cells.LANGS):
            J.append(dict(lang=lang, genre="names", ntok=10000, logo=logo, rep=rep + 10,
                          kw=dict(kinds=("K1", "K2", "K3"), nshuf=0, anchors=(0, 5, 10, 20, 40, 80))))
    return J


if __name__ == "__main__":
    name = sys.argv[1]; nproc = min(2, int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    J = plan(name)
    path = OUT / f"{name}.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            r = json.loads(l)
            if "error" not in r: done.add((r["lang"], r["ntok_target"], r["logo"], r["rep"]))
    J = [j for j in J if (j["lang"], j["ntok"], j["logo"], j["rep"]) not in done]
    # big inventories first for load balance
    J.sort(key=lambda j: -j["logo"])
    print(name, len(J), "jobs", flush=True)
    def conv(o):
        import numpy as np
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, np.bool_): return bool(o)
        return str(o)
    with Pool(nproc) as p, open(path, "a") as f:
        for i, r in enumerate(p.imap_unordered(job, J)):
            f.write(json.dumps(r, default=conv) + "\n"); f.flush()
            print(i, r.get("lang"), r.get("ntok_target"), r.get("logo"), r.get("rep"),
                  "ERR" if "error" in r else "%.0fs" % r["secs"], flush=True)
