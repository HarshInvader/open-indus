"""Pre-registered Indus run (docs/prereg/genre_alignment.md): align Indus seal slots to Ur III and
Old Babylonian seal-legend slots by distributional fingerprint.

usage: .venv/bin/python -I experiments/genre_alignment/ga_indus.py
needs controls.json (frozen standardisation, threshold tau, slot reliabilities) from ga_controls.py
writes indus_alignment.json
"""
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ga_slots as GS
import ga_core as GC
from ga_controls import induce

CTRL = json.load(open(HERE / "controls.json"))
MU = np.array(CTRL["standardisation"]["mu"]); SD = np.array(CTRL["standardisation"]["sd"])
TAU = CTRL["C1"]["tau_precision80"]
REL = CTRL["C1"]["slot_reliability"]
Z = lambda fp: {k: (v - MU) / SD for k, v in fp.items()}
REPS = 100
PRED = {"ur3": {"CLOSER": "SERV", "CORE": "OWNER", "TITLE": "TITLE", "CONN": "KIN"},
        "ob": {"CLOSER": "SERV", "CORE": "OWNER", "TITLE": "TITLE", "CONN": "KIN", "OPEN": "SEAL_OF"}}


def mean_ref(texts, n, reps=20, seed=0):
    acc = defaultdict(list)
    for r in range(reps):
        rng = random.Random(seed + r)
        for k, v in Z(GC.fingerprints(GC.subsample(texts, n, rng), seed=r)).items(): acc[k].append(v)
    return {k: np.mean(v, 0) for k, v in acc.items() if len(v) >= reps // 2}


def run(I, refs, label):
    n = len(I); out = {"n_texts": n}
    A = Z(GC.fingerprints(I, seed=0))
    out["indus_fingerprint"] = {k: dict(zip(GC.FEATURES, np.round(v * SD + MU, 3).tolist())) for k, v in A.items()}
    for g, texts in refs.items():
        B = mean_ref(texts, n)
        pairs, m, (a, b, D) = GC.align(A, B)
        pairs_d, _, _ = GC.align(A, B, dummy=TAU)
        null = GC.column_perm_null(A, B, n=2000, seed=7)
        p = float((np.sum(null <= m) + 1) / (len(null) + 1))
        nearest = {}
        for i, x in enumerate(a):
            o = np.argsort(D[i]); nearest[x] = {"nearest": b[o[0]], "d": round(float(D[i, o[0]]), 3),
                                                "second": b[o[1]], "d2": round(float(D[i, o[1]]), 3)}
        # bootstrap: resample Indus texts and a fresh reference subsample
        freq = defaultdict(Counter); acc = defaultdict(Counter)
        for r in range(REPS):
            rng = random.Random(500 + r)
            Ib = [rng.choice(I) for _ in range(n)]
            Ab = Z(GC.fingerprints(Ib, seed=r))
            Bb = Z(GC.fingerprints(GC.subsample(texts, n, rng), seed=r))
            pb, _, _ = GC.align(Ab, Bb)
            for x, y, d in pb: freq[x][y] += 1
            pdm, _, _ = GC.align(Ab, Bb, dummy=TAU)
            for x, y, d in pdm: acc[x][y if y else "none"] += 1
        out[g] = {"pairs": [(x, y, round(d, 3)) for x, y, d in pairs], "mean_dist": m, "colperm_p": p,
                  "null_mean": float(null.mean()), "null_q05": float(np.quantile(null, 0.05)),
                  "pairs_with_dummy_tau": [(x, y, round(d, 3)) for x, y, d in pairs_d], "nearest": nearest,
                  "dist_matrix": {"rows": a, "cols": b, "D": np.round(D, 3).tolist()},
                  "boot_pair_freq": {x: {y: c / REPS for y, c in v.most_common()} for x, v in freq.items()},
                  "boot_accept_freq": {x: {y: c / REPS for y, c in v.most_common()} for x, v in acc.items()}}
        print(label, g, "p", p, "mean", round(m, 3), "null", round(float(null.mean()), 3))
        for x, y, d in pairs: print("   ", x, "->", y, round(d, 3), "boot", round(freq[x][y] / REPS, 2), nearest[x])
    return out


def main():
    titles, lords = GS.build_lexicons()
    refs = {g: GS.cun_corpus(g, titles, lords) for g in ("ur3", "ob")}
    res = {"tau": TAU, "predictions": PRED}
    for split in ("dev", "heldout"):
        res[split] = run(GS.indus_corpus(split, coarse=True), refs, split)
    # ---- verdicts (pre-registered rule)
    ver = {}
    for g, pr in PRED.items():
        for x, y in pr.items():
            d = res["dev"][g]; h = res["heldout"][g]
            dev_pair = dict((a, b) for a, b, _ in d["pairs"]).get(x)
            dist = dict((a, dd) for a, b, dd in d["pairs"]).get(x)
            crit = {"a_global_p<0.05": d["colperm_p"] < 0.05,
                    "b_boot>=0.7": d["boot_pair_freq"].get(x, {}).get(y, 0) >= 0.7,
                    "c_dist<tau": dev_pair == y and dist is not None and dist < TAU,
                    "d_heldout_boot>=0.5": h["boot_pair_freq"].get(x, {}).get(y, 0) >= 0.5,
                    "e_ref_slot_reliable>=0.75": REL.get(y, 0) >= 0.75}
            if all(crit.values()): v = "supported"
            elif crit["a_global_p<0.05"] and crit["b_boot>=0.7"] and crit["d_heldout_boot>=0.5"]: v = "suggestive"
            else: v = "not supported"
            ver[f"{g}:{x}->{y}"] = {"criteria": crit, "verdict": v, "dev_match": dev_pair, "dev_dist": dist}
            print(g, x, "->", y, v, crit, "dev match:", dev_pair, dist)
    res["verdicts"] = ver
    # ---- exploratory (not pre-registered as confirmatory)
    exp = {}
    exp["fine_dev"] = run(GS.indus_corpus("dev", coarse=False), refs, "fine-dev")
    rng = random.Random(3)
    Id = GS.indus_corpus("dev", coarse=True)
    blind = induce([dict(t, gold=t["slots"]) for t in Id], k=6, seed=0)
    c = defaultdict(Counter)
    for t in blind:
        for s, g0 in zip(t["slots"], t["gold"]): c[s][g0] += 1
    exp["blind_classes_vs_roles"] = {s: dict(v.most_common(4)) for s, v in c.items()}
    exp["blind_dev"] = run([{"toks": t["toks"], "slots": t["slots"]} for t in blind], refs, "blind-dev")
    res["exploratory"] = exp
    json.dump(res, open(HERE / "indus_alignment.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
