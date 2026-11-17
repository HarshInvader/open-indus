"""Planted validation grid for the crib attack (no Indus data).  Pre-registered in
docs/prereg/crib_attack_planted.md.  Run: .venv/bin/python -I experiments/crib_attack/run_planted.py [cond ...]
Writes experiments/crib_attack/out/<cond>.json (one record per search)."""
import sys, json, time
from pathlib import Path
import numpy as np
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from names import ur3_units, linb_units, spellings  # noqa
from sim import make_corpus, shuffle_texts  # noqa
from attack import NameIndex, Attack  # noqa

NS = [20, 30, 60, 120]
REPS = {"planted": 10, "wronglang": 10, "shuffle": 20}
CONDS = {  # script, attacker coverage, misread
    "A_main": ("A", 1.0, 0.2),
    "A_cov50": ("A", 0.5, 0.2),
    "B_main": ("B", 1.0, 0.2),
}


def iters_for(n):
    return int(min(15000, max(4000, 120 * n)))


_CACHE = {}


def setup(cond):
    if cond in _CACHE:
        return _CACHE[cond]
    script, cov, mis = CONDS[cond]
    u = ur3_units(); l = linb_units()
    units = sorted(u); w = [u[x] for x in units]
    lunits = sorted(l); lw = [l[x] for x in lunits]
    sp_all = spellings(u, script) | spellings(l, script)
    values = sorted({x for v in sp_all for x in v})
    if cov < 1.0:
        r = np.random.default_rng(777)
        keep = [units[i] for i in r.permutation(len(units))[: int(len(units) * cov)]]
        att = spellings({k: 1 for k in keep}, script)
    else:
        att = spellings(u, script)
    ni = NameIndex(att, values)
    ni.values = values; ni.vid = {v: i for i, v in enumerate(values)}; ni.nv = len(values)
    # rebuild index on the global value ids
    by = {}
    for sp in att:
        by.setdefault(len(sp), []).append([ni.vid[x] for x in sp])
    ni.by_k = {k: np.array(v, dtype=np.int16) for k, v in sorted(by.items())}
    _CACHE[cond] = (script, mis, units, w, lunits, lw, values, ni)
    return _CACHE[cond]


def job(args):
    cond, kind, n, rep = args
    script, mis, units, w, lunits, lw, values, ni = setup(cond)
    rng = np.random.default_rng([2026, 1117, NS.index(n), rep, ["planted", "wronglang", "shuffle"].index(kind),
                                 list(CONDS).index(cond)])
    if kind == "wronglang":
        c = make_corpus(n, lunits, lw, values, script, rng, misread=mis)
    else:
        c = make_corpus(n, units, w, values, script, rng, misread=mis)
    texts = c["texts"]
    if kind == "shuffle":
        texts = shuffle_texts(texts, rng)
    a = Attack(texts, ni, c["nsigns"], rng)
    t0 = time.time()
    S, key = a.run(iters_for(n), restarts=3)
    tk = c["true_key"]
    S_true = a.score(tk) if kind != "shuffle" else None
    # secondary: exact full-name matches (k >= 3) under the best key, and under the true key
    def exact(kk):
        n_ = 0
        for i in range(len(a.texts)):
            for k_, win in a.windows[i]:
                if k_ >= 3 and ((ni.by_k[k_][:, None, :] == kk[win][None]).all(-1)).any():
                    n_ += 1; break
        return n_
    E = exact(key); E_true = exact(tk) if kind != "shuffle" else None
    toks = np.concatenate([np.asarray(t) for t in texts])
    present = np.unique(toks)
    cnt = np.bincount(toks, minlength=c["nsigns"])
    assigned = np.flatnonzero(key >= 0) if key is not None else np.array([], int)
    correct = assigned[key[assigned] == tk[assigned]] if assigned.size else assigned
    syl_present = present[tk[present] >= 0]
    syl2 = syl_present[cnt[syl_present] >= 2]
    return dict(cond=cond, kind=kind, n=n, rep=rep, S=int(S), S_true=S_true, E=int(E), E_true=E_true,
                n_assigned=int(assigned.size), n_correct=int(correct.size),
                n_syl_present=int(syl_present.size), n_correct_rep2=int(np.isin(correct, syl2).sum()),
                n_syl_rep2=int(syl2.size), n_name_texts=int(sum(c["name_text"])), secs=round(time.time() - t0, 1))


if __name__ == "__main__":
    # checkpointed: each finished search is appended to out/<cond>.jsonl; finished jobs are skipped on restart
    conds = sys.argv[1:] or list(CONDS)
    (HERE / "out").mkdir(exist_ok=True)
    for cond in conds:
        jl = HERE / "out" / f"{cond}.jsonl"
        done = set()
        if jl.exists():
            for line in open(jl):
                r = json.loads(line); done.add((r["cond"], r["kind"], r["n"], r["rep"]))
        jobs = [(cond, k, n, r) for n in NS for k, R in REPS.items() for r in range(R if cond == "A_main" else R * 2 // 3)]
        jobs = [j for j in jobs if j not in done]
        jobs.sort(key=lambda j: -j[2])
        with Pool(2) as p, open(jl, "a") as fh:  # laptop limit: never more than 2 workers
            for res in p.imap_unordered(job, jobs, chunksize=1):
                fh.write(json.dumps(res) + "\n"); fh.flush()
        res = [json.loads(l) for l in open(jl)]
        json.dump(res, open(HERE / "out" / f"{cond}.json", "w"), indent=0)
        print(cond, "done", len(res), flush=True)
