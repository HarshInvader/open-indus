"""anchor_ceiling kill test (prereg docs/prereg/anchor_ceiling.md, 'Kill test, run first'). Writes kill.json.

Code-level definitions, fixed with this file's seal:
- plants: 20 field assignments of the 92 union words at the real scored field sizes (from the frozen truth), each
  evaluated in all 5 draws. Planted picture values are 'PL_<field>'. Run at rung A3.
- a field is recovered in a plant if it passes (matched F1 >= 0.5 and above the null's 95th percentile) in >= 4 of 5
  draws. A plant's adjusted Rand = median over draws.
- bar at strength 1.0: median over plants of the adjusted Rand >= 0.8, and every field recovered in >= 80% of plants.
- power(strength) = mean over plants of the share of fields recovered; the smallest strength with power >= 0.8 is
  reported.
- null corpus: per rung, only that rung's added anchor is permuted across all documents; 200 shuffles; the real
  frozen truth. 'Any field recovered' rate must be <= 0.05 at A3 (the gate). Other rungs' rates are reported; a rung
  whose own null fails is not read.
- the kill test passes if the strength-1.0 bar is met and the A3 null rate is <= 0.05.
"""
import json, sys, os
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import core as K  # noqa: E402

NPERM = 1000; NPLANT = 20; NSHUF = 200; STRENGTHS = [1.0, 0.6, 0.3]; SEED = 20261126


def truth():
    A = json.load(open(HERE / "truth/labels_A.json")); B = json.load(open(HERE / "truth/labels_B.json"))
    kept = {w: A[w] for w in A if A[w] == B[w] and A[w] != "unknown"}
    c = Counter(kept.values())
    fields = sorted(f for f, n in c.items() if n >= 4)
    return {w: f for w, f in kept.items() if f in fields}, fields


DRAWS = None


def draws():
    global DRAWS
    if DRAWS is None:
        DRAWS = [K.draw_docs(k) for k in range(K.NDRAW)]
    return DRAWS


def planted_pics(docs, el, plant, s, rng):
    out = {}
    for d in docs:
        ws = [w for w in d["words"] if w in el and w in plant]
        if ws and rng.random() < s:
            out[d["id"]] = "PL_" + plant[ws[rng.integers(len(ws))]]
        else:
            out[d["id"]] = d["pic"]
    return out


def one_plant(args):
    s, j, words, sizes = args
    rng = np.random.default_rng([SEED, int(s * 10), j])
    perm = rng.permutation(words); plant, i = {}, 0
    for f, n in sizes:
        for w in perm[i:i + n]: plant[str(w)] = f
        i += n
    fields = [f for f, _ in sizes]
    res = []
    for k, (dev, held) in enumerate(draws()):
        el, _, _ = K.eligible(dev, held)
        A = K.anchors_of(dev + held)
        A["pic"] = planted_pics(dev + held, set(el), plant, s, rng)
        res.append(K.run_rung(dev, held, "A3", A, plant, fields, NPERM, rng))
    rec = {f: sum(r["passed"].get(f, False) for r in res) >= 4 for f in fields}
    return dict(strength=s, plant=j, ari=float(np.nanmedian([r["ari"] for r in res])), recovered=rec,
                draws=[dict(k=r["k"], n=r["n"], fields=r["fields"], f1=r["f1"]) for r in res])


def one_shuffle(args):
    rung, j = args
    T, fields = truth()
    rng = np.random.default_rng([SEED, 7, ["A1", "A2", "A3", "A4"].index(rung), j])
    docs = K.all_docs(); v = K.ADDED[rung]
    vals = [d[v] for d in docs]; sh = rng.permutation(len(vals))
    shuf = {d["id"]: vals[sh[i]] for i, d in enumerate(docs)}
    res = []
    for dev, held in draws():
        A = K.anchors_of(dev + held); A[v] = {d["id"]: shuf[d["id"]] for d in dev + held}
        res.append(K.run_rung(dev, held, rung, A, T, fields, NPERM, rng))
    rec = [f for f in fields if sum(r["passed"].get(f, False) for r in res) >= 4]
    return dict(rung=rung, shuffle=j, recovered=rec, ari=float(np.nanmedian([r["ari"] for r in res])))


def main():
    T, fields = truth()
    sizes = [(f, sum(1 for x in T.values() if x == f)) for f in fields]
    words = sorted(open(HERE / "truth/words.txt").read().split())
    print("fields", sizes, flush=True)
    nw = int(os.environ.get("NWORK", "4"))
    with Pool(nw, initializer=draws) as P:
        plants = P.map(one_plant, [(s, j, words, sizes) for s in STRENGTHS for j in range(NPLANT)], chunksize=1)
        out = {"fields": sizes, "plants": plants}
        summ = {}
        for s in STRENGTHS:
            ps = [p for p in plants if p["strength"] == s]
            frac = {f: float(np.mean([p["recovered"][f] for p in ps])) for f in fields}
            summ[str(s)] = dict(median_ari=float(np.median([p["ari"] for p in ps])), field_recovery=frac,
                                power=float(np.mean([np.mean(list(p["recovered"].values())) for p in ps])))
            print(s, summ[str(s)], flush=True)
        out["plant_summary"] = summ
        bar = summ["1.0"]["median_ari"] >= 0.8 and min(summ["1.0"]["field_recovery"].values()) >= 0.8
        powered = [s for s in STRENGTHS if summ[str(s)]["power"] >= 0.8]
        out["bar_strength_1"] = bar; out["smallest_powered_strength"] = min(powered) if powered else None
        json.dump(out, open(HERE / "kill.json", "w"), indent=1)
        sh = P.map(one_shuffle, [(r, j) for r in ["A3", "A1", "A2", "A4"] for j in range(NSHUF)], chunksize=2)
    out["null_corpus"] = {r: dict(any_recovered_rate=float(np.mean([bool(x["recovered"]) for x in sh if x["rung"] == r])),
                                  field_counts=dict(Counter(f for x in sh if x["rung"] == r for f in x["recovered"])))
                          for r in ["A1", "A2", "A3", "A4"]}
    out["null_shuffles"] = sh
    out["passed"] = bool(bar and out["null_corpus"]["A3"]["any_recovered_rate"] <= 0.05)
    print("null", {r: v["any_recovered_rate"] for r, v in out["null_corpus"].items()}, "PASSED", out["passed"], flush=True)
    json.dump(out, open(HERE / "kill.json", "w"), indent=1)


if __name__ == "__main__":
    main()
