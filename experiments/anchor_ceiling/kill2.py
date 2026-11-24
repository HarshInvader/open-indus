"""anchor_ceiling v2 kill test (prereg docs/prereg/anchor_ceiling_v2.md). Writes kill2.json.
Usage: kill2.py select  -> select.json (10 plants, seed 20261201, strength 1.0, A3, both methods; ARI only)
       kill2.py kill    -> kill2.json (needs select.json): supervised gate, then blind, then null corpus.

Code-level definitions, fixed with this file's seal:
- plant j: fields get the real pool counts from the 44 pool words and the remainder from the other 48 union words;
  redrawn until every field has >= 3 held-out planted words in >= 4 draws. The same plant is used at every strength.
- picture plant: v1 rule (kill.planted_pics), with its own rng per (plant, strength, draw).
- recovered in a plant: passed in >= 4 of 5 draws. Plant adjusted Rand = median over draws.
- power(strength) = mean over plants of the share of fields recovered.
- the null corpus runs only if the blind bar passed (whole anchor tuple permuted across all documents, 200 shuffles).
"""
import json, os, sys
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import core as K, core2 as C2, kill as K1  # noqa: E402

NPERM = 1000; NPLANT = 20; NSEL = 10; NSHUF = 200; STRENGTHS = [1.0, 0.6, 0.3]
SEL_SEED, KILL_SEED, NULL_SEED = 20261201, 20261202, 20261203
WORDS = sorted(open(HERE / "truth/words.txt").read().split())


def setup():
    T, _ = K1.truth()
    T = {w: f for w, f in T.items() if f in C2.FIELDS}
    D = K1.draws()
    sc = [set(K.eligible(dev, held)[1]) for dev, held in D]
    ok = Counter(w for s in sc for w in s)
    pool = [w for w in WORDS if ok[w] >= 4]; rest = [w for w in WORDS if ok[w] < 4]
    return T, D, sc, pool, rest


def make_plant(seed, j, T, sc, pool, rest):
    rng = np.random.default_rng([seed, j])
    for _ in range(100000):
        pp = list(rng.permutation(pool)); rr = list(rng.permutation(rest)); plant = {}
        for f in C2.FIELDS:
            npool = sum(1 for w in T if T[w] == f and w in pool)
            nall = sum(1 for w in T if T[w] == f)
            for w in pp[:npool] + rr[:nall - npool]: plant[str(w)] = f
            pp = pp[npool:]; rr = rr[nall - npool:]
        if all(sum(sum(1 for w in s if plant.get(w) == f) >= 3 for s in sc) >= 4 for f in C2.FIELDS):
            return plant
    raise RuntimeError(f"no scoreable plant for seed {seed}, plant {j}")


def eval_plant(seed, j, s, method, nperm, supervised):
    T, D, sc, pool, rest = setup()
    plant = make_plant(seed, j, T, sc, pool, rest)
    res = []
    for k, (dev, held) in enumerate(D):
        rng = np.random.default_rng([seed, j, int(s * 10), k])
        el, _, _ = K.eligible(dev, held)
        A = K.anchors_of(dev + held)
        A["pic"] = K1.planted_pics(dev + held, set(el), plant, s, rng)
        res.append(C2.run_rung(dev, held, "A3", A, plant, method, nperm, rng, supervised=supervised))
    def rec(key=None):
        rr = [r[key] if key else r for r in res]
        return {f: sum(x.get("passed", {}).get(f, False) for x in rr) >= 4 for f in C2.FIELDS}
    out = dict(plant=j, strength=s, ari=float(np.nanmedian([r["ari"] for r in res])), recovered=rec(),
               pair_auc=float(np.nanmedian([r["pair_auc"] for r in res])))
    if supervised:
        out["sup_dev_recovered"] = rec("sup_dev"); out["sup_held_recovered"] = rec("sup_held")
        out["sup_held_ari"] = float(np.nanmedian([r["sup_held"]["ari"] for r in res]))
    return out


def _ep(a): return eval_plant(*a)


def summarise(ps, key="recovered", ari="ari"):
    frac = {f: float(np.mean([p[key][f] for p in ps])) for f in C2.FIELDS}
    return dict(median_ari=float(np.median([p[ari] for p in ps])), field_recovery=frac,
                power=float(np.mean([np.mean(list(p[key].values())) for p in ps])),
                bar=bool(np.median([p[ari] for p in ps]) >= 0.8 and min(frac.values()) >= 0.8))


def one_null(args):
    j, method = args
    T, D, _, _, _ = setup()
    rng = np.random.default_rng([NULL_SEED, j])
    docs = K.all_docs(); sh = rng.permutation(len(docs))
    tup = {d["id"]: docs[sh[i]] for i, d in enumerate(docs)}
    res = []
    for dev, held in D:
        A = {v: {d["id"]: tup[d["id"]][v] for d in dev + held} for v in ["site", "cls", "pic", "hand"]}
        res.append(C2.run_rung(dev, held, "A3", A, T, method, NPERM, rng))
    return [f for f in C2.FIELDS if sum(r["passed"].get(f, False) for r in res) >= 4]


def main(mode):
    nw = int(os.environ.get("NWORK", "4"))
    with Pool(nw, initializer=setup) as P:
        if mode == "select":
            out = {}
            for m in ["kmeans", "ward"]:
                ps = P.map(_ep, [(SEL_SEED, j, 1.0, m, 1, False) for j in range(NSEL)], chunksize=1)
                out[m] = dict(stat=float(np.median([p["ari"] for p in ps])), plants=ps)
                print(m, out[m]["stat"], flush=True)
            out["chosen"] = "kmeans" if out["kmeans"]["stat"] >= out["ward"]["stat"] else "ward"
            print("chosen", out["chosen"]); json.dump(out, open(HERE / "select.json", "w"), indent=1); return
        m = json.load(open(HERE / "select.json"))["chosen"]
        out = {"method": m}
        sup = P.map(_ep, [(KILL_SEED, j, 1.0, m, NPERM, True) for j in range(NPLANT)], chunksize=1)
        a = {f: float(np.mean([p["sup_dev_recovered"][f] for p in sup])) for f in C2.FIELDS}
        b = summarise(sup, "sup_held_recovered", "sup_held_ari")
        gate = min(a.values()) >= 0.8 and b["bar"]
        out["supervised"] = dict(dev_field_recovery=a, held=b, passed=bool(gate))
        print("supervised", out["supervised"], flush=True)
        out["plants"] = sup
        if not gate:
            out["passed"] = False; out["stop"] = "profiles too thin at this size"
        else:
            ps = sup + P.map(_ep, [(KILL_SEED, j, s, m, NPERM, False) for s in STRENGTHS[1:] for j in range(NPLANT)], chunksize=1)
            out["plants"] = ps
            out["blind"] = {str(s): summarise([p for p in ps if p["strength"] == s]) for s in STRENGTHS}
            for s in STRENGTHS:
                out["blind"][str(s)]["pair_auc"] = float(np.median([p["pair_auc"] for p in ps if p["strength"] == s]))
            print("blind", out["blind"], flush=True)
            pw = [s for s in STRENGTHS if out["blind"][str(s)]["power"] >= 0.8]
            out["smallest_powered_strength"] = min(pw) if pw else None
            if not out["blind"]["1.0"]["bar"]:
                out["passed"] = False; out["stop"] = "blind clustering fails"
            else:
                nl = P.map(one_null, [(j, m) for j in range(NSHUF)], chunksize=2)
                rate = float(np.mean([bool(x) for x in nl]))
                out["null"] = dict(any_recovered_rate=rate, field_counts=dict(Counter(f for x in nl for f in x)))
                out["passed"] = rate <= 0.05
                if not out["passed"]: out["stop"] = "the method finds fields in noise"
        print("PASSED", out["passed"], out.get("stop", ""), flush=True)
        json.dump(out, open(HERE / "kill2.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
