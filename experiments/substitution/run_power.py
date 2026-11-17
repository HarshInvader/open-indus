"""Power calibration for the X <-> YZ substitution test.

Two kinds of planted corpora:
  A. synthetic Indus-genre corpora (sim.AltSynth), alternation rate p over logogram signs,
     q = 0.5 chance per occurrence of using the syllabic spelling;
  B. Indus dev itself with a planted system: a fraction p of Indus signs (tokens >= 2)
     get a 2-3 sign spelling from 50 NEW pseudo-syllabograms (Q00-Q49); each occurrence
     is respelled with probability q. This keeps the real Indus confounds (formulae,
     paradigms, near-copy families) exactly.

For each corpus: the full pipeline (L-tier mining, frame units, (slot,k)-stratified
permutation null, BH) is run and we record
  n_sig  = equations with q < 0.05 (the detection statistic),
  tp_sig = planted equations among them,
  rec    = planted equations attested in >= 2 independent frames (an oracle ceiling),
  S, p_S = shared-sign system score and its null p,
  sys_tp = planted equations at q<0.05 that share a syllable with another one.
Usage: .venv/bin/python experiments/substitution/run_power.py [nseeds] [nperm]
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import analyse, load_m77, paradigm_partners, save_results, sce_filter, sce_system  # noqa: E402
from sim import AltSynth  # noqa: E402


def score(T, truth, nperm, seed):
    out, items, ev, units, eqs = analyse(T, nperm=nperm, seed=seed, tier="L", ks=(2, 3))
    tset = set(truth.items())
    sig = [(r["X"], tuple(r["Y"].split())) for r in items if r["q"] < 0.05]
    tp = [e for e in sig if e in tset]
    syl_use = {}
    for x, y in tp:
        for s in set(y):
            syl_use.setdefault(s, set()).add(x)
    sys_tp = sum(1 for x, y in tp if any(len(syl_use[s]) >= 2 for s in set(y)))
    rec = sum(1 for e in tset if eqs.get(e, 0) >= 2)
    sces = sce_filter(items, paradigm_partners(T))
    tp_sce = sum(1 for r in sces if (r["X"], tuple(r["Y"].split())) in tset)
    n_shared, n_in_sys, _ = sce_system(sces)
    tp_sys = sum(1 for r in sces if (r["X"], tuple(r["Y"].split())) in tset) if n_shared else 0
    return dict(n_sce=len(sces), tp_sce=tp_sce, sce_shared=n_shared, sce_in_sys=n_in_sys,n_sig=out["n_sig_q05"], tp_sig=len(tp), fp_sig=len(sig) - len(tp), rec=rec, n_truth=len(tset),
                sys_tp=sys_tp, G=out["G"], p_G=out["p_G"], S=out["S"], p_S=out["p_S"], n_units=out["n_units"])


def job_synth(args):
    seed, p, q, n, mult_p, nperm = args
    s = AltSynth(seed=seed, p=p, q=q, n_target=n, mult_p=mult_p)
    T = s.corpus(n)
    r = score(T, s.truth["alt"], nperm, seed)
    r.update(kind="synth", seed=seed, p=p, q=q, n=n, mult_p=mult_p, token_share=s.alt_token_share,
             mean_len=float(np.mean([len(t) for t in T])))
    return r


def plant_indus(D, seed, p, q):
    rng = np.random.default_rng(seed)
    from collections import Counter
    tok = Counter(x for t in D for x in t)
    cand = sorted(x for x, c in tok.items() if c >= 2)
    alt = {}
    for x in cand:
        if rng.random() < p:
            alt[x] = tuple("Q%02d" % int(v) for v in rng.choice(50, int(rng.integers(2, 4))))
    out = set()
    for t in D:
        u = []
        for x in t:
            if x in alt and rng.random() < q:
                u += list(alt[x])
            else:
                u.append(x)
        out.add(tuple(u))
    share = sum(tok[x] for x in alt) / sum(tok.values())
    return sorted(out), alt, share


def job_indus(args):
    seed, p, q, nperm = args
    D, _ = load_m77()
    T, alt, share = plant_indus(D, seed, p, q)
    r = score(T, alt, nperm, seed)
    r.update(kind="indus_plant", seed=seed, p=p, q=q, n=len(T), token_share=share)
    return r


def summarise(rows, keys):
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    out = []
    for k, rs in sorted(g.items()):
        d = dict(zip(keys, k))
        for f in ("n_sig", "tp_sig", "fp_sig", "n_sce", "tp_sce", "sce_shared", "sce_in_sys", "rec", "n_truth",
                  "sys_tp", "token_share"):
            d[f] = float(np.mean([r[f] for r in rs]))
        d["n_runs"] = len(rs)
        out.append(d)
    return out


if __name__ == "__main__":
    nseeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    nperm = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    ps = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
    jobs = [(1000 + s, p, 0.5, 1675, 0.90, nperm) for p in ps for s in range(nseeds)]
    jobs += [(1500 + s, p, 0.5, 2300, 0.90, nperm) for p in (0.0, 0.3, 1.0) for s in range(nseeds)]
    # higher legend multiplicity (what a corpus with many copies per name would give)
    jobs += [(2000 + s, p, 0.5, 2300, 0.60, nperm) for p in (0.0, 0.3, 1.0) for s in range(nseeds)]
    ijobs = [(3000 + s, p, 0.5, nperm) for p in (0.1, 0.3, 0.5, 1.0) for s in range(nseeds)]
    t0 = time.time()
    with Pool(2) as pool:
        rows = pool.map(job_synth, jobs, chunksize=1)
        irows = pool.map(job_indus, ijobs, chunksize=1)
    print("done in %.0fs" % (time.time() - t0))
    json.dump(rows + irows, open(HERE / "power_runs.json", "w"), indent=0)
    for d in summarise(rows, ["n", "mult_p", "p"]):
        print(d)
    for d in summarise(irows, ["p"]):
        print("indus_plant", d)
