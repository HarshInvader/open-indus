"""S4: 'six then fish' (M109 -> M59) against a null matched on slot position, run length and rare-sign load.
Pre-registration: docs/prereg/s4_sixfish_rare_null.md (sealed before any null was computed).

Run from the repo root:  .venv/bin/python -I experiments/s4_sixfish_rare_null/run.py
Writes experiments/s4_sixfish_rare_null/results.json. Deterministic (named, seeded NumPy streams).
"""
import json, sys, zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, icit_texts, distinct, runs  # noqa: E402

SEED = 20261128
NREP, NREP_PLANT = 100_000, 20_000
NONNATIVE_REGIONS = ("Persian Gulf", "Mesopotamia", "Iranian Plateau", "Central Asia", "Other")


def g(*tag):
    return np.random.default_rng([SEED] + [zlib.crc32(str(t).encode()) for t in tag])


def m77_runs(texts):
    return [r for t in texts if t["site"] != "West Asian finds" for r in runs(t["seq"])]


def rare_load(run, cnt):
    return sum(cnt[x] < 10 for x in run)


def slots(R, A):
    """(run index, position) of every A token that has a next sign."""
    return [(i, j) for i, r in enumerate(R) for j, x in enumerate(r[:-1]) if x == A]


def matched_null(R, A, B, cnt, n, rg):
    """T1. For each A slot draw a run without A from the same (min(L,9), min(r,3)) stratum (fallback r then L,
    only to strata long enough for the slot), read whether position j+1 holds B. Returns obs, null and p."""
    S = slots(R, A)
    obs = sum(R[i][j + 1] == B for i, j in S)
    strata = defaultdict(list)
    for k, r in enumerate(R):
        if A in r: continue
        strata[(min(len(r), 9), min(rare_load(r, cnt), 3))].append(k)
    cols = []
    for i, j in S:
        L = min(len(R[i]), 9); rr = min(rare_load(R[i], cnt), 3); key = None
        for LL in range(L, 0, -1):
            if LL < 9 and LL < j + 2: break
            for r2 in range(rr, -1, -1):
                if len(strata.get((LL, r2), [])) >= 5: key = (LL, r2); break
            if key: break
        if key is None:  # no stratum of >= 5 runs is long enough: pool every run long enough (reported)
            pool = [k for k, r in enumerate(R) if A not in r and len(r) >= j + 2]; key = ("any_long_enough", j + 2)
        else:
            pool = strata[key]
        hit = np.array([R[k][min(j, len(R[k]) - 2) + 1] == B for k in pool], float)
        cols.append((hit, key))
    draws = np.zeros(n)
    for hit, _ in cols:
        draws += hit[rg.integers(len(hit), size=n)]
    return dict(slots=len(S), obs=int(obs), null_mean=round(float(draws.mean()), 3),
                null_rate=round(float(draws.mean()) / max(1, len(S)), 4),
                p=(1 + int((draws >= obs).sum())) / (n + 1),
                strata_used=sorted({str(k) for _, k in cols}))


def within_run_shuffle(R, A, B, n, rg):
    rel = [r for r in R if A in r]
    obs = sum(r[j + 1] == B for r in rel for j, x in enumerate(r[:-1]) if x == A)
    arr = [np.array([1 if x == A else 2 if x == B else 0 for x in r]) for r in rel]
    null = np.zeros(n, int); B_ = 5_000
    for b0 in range(0, n, B_):
        b = min(B_, n - b0)
        for a in arr:
            if (a == 2).sum() == 0 or len(a) < 2: continue
            P = np.argsort(rg.random((b, len(a))), axis=1)
            s = a[P]
            null[b0:b0 + b] += ((s[:, :-1] == 1) & (s[:, 1:] == 2)).sum(1)
    return dict(runs=len(rel), obs=int(obs), null_mean=round(float(null.mean()), 3),
                p=(1 + int((null >= obs).sum())) / (n + 1))


def planted(R, cnt, rg):
    nxt = Counter(x for r in R for x in r[:-1])
    carriers = sorted([s for s, c in nxt.items() if 8 <= c <= 20 and s not in ("M109", "M59")],
                      key=lambda s: (-nxt[s], int(s[1:])))[:20]
    out = []
    for c in carriers:
        S = slots(R, c)
        raw = sum(R[i][j + 1] == "M59" for i, j in S) / len(S)
        p0 = matched_null(R, c, "M59", cnt, NREP_PLANT, g("plant0", c))["p"]
        R2 = [list(r) for r in R]
        pick = g("plantpick", c).random(len(S)) < 0.6
        for (i, j), pk in zip(S, pick):
            if pk: R2[i][j + 1] = "M59"
        p1 = matched_null(R2, c, "M59", cnt, NREP_PLANT, g("plant1", c))["p"]
        out.append(dict(carrier=c, slots=len(S), raw_m59_rate=round(raw, 3), planted_hits=int(pick.sum()), p_unplanted=p0, p_planted=p1))
    fp = [o for o in out]; fp_clean = [o for o in out if o["raw_m59_rate"] <= 0.2]
    return dict(carriers=out, n=len(out),
                false_positive_rate=round(np.mean([o["p_unplanted"] < 0.05 for o in fp]), 3),
                false_positive_rate_raw_le_0_2=round(np.mean([o["p_unplanted"] < 0.05 for o in fp_clean]), 3) if fp_clean else None,
                power=round(np.mean([o["p_planted"] < 0.05 for o in out]), 3))


def holm(ps):
    o = np.argsort(ps); m = len(ps); out = np.empty(m); run = 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (m - r) * ps[i])); out[i] = run
    return [float(x) for x in out]


def main():
    dev, ho = dev_heldout(version=2)
    Rd, Rh = m77_runs(dev), m77_runs(ho)
    cnt = Counter(x for r in Rd for x in r)
    allnext = Counter(r[j + 1] for r in Rh for j in range(len(r) - 1))
    OUT = dict(seed=SEED, base_rate_heldout=round(allnext["M59"] / sum(allnext.values()), 4))
    OUT["T1_heldout_matched"] = matched_null(Rh, "M109", "M59", cnt, NREP, g("T1"))
    OUT["T2_heldout_within_run"] = within_run_shuffle(Rh, "M109", "M59", NREP, g("T2"))
    OUT["T3_dev_matched"] = matched_null(Rd, "M109", "M59", cnt, NREP, g("T3"))
    I = distinct([t for t in icit_texts() if t["region"] not in NONNATIVE_REGIONS])
    Ri = [r for t in I for r in runs(t["seq"])]
    OUT["T4_icit_matched"] = matched_null(Ri, "W016", "W220", Counter(x for r in Ri for x in r), NREP, g("T4"))
    h = holm(np.array([OUT["T1_heldout_matched"]["p"], OUT["T2_heldout_within_run"]["p"]]))
    OUT["holm"] = dict(T1=h[0], T2=h[1])
    OUT["planted_control"] = planted(Rh, cnt, g("plant"))
    t1, t2 = h[0] < 0.05, h[1] < 0.05
    OUT["verdict"] = "survives" if t1 else "weakened" if t2 else "refuted beyond position, length and rare load"
    OUT["underpowered"] = bool(OUT["planted_control"]["power"] < 0.8)
    json.dump(OUT, open(HERE / "results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in OUT.items() if k != "planted_control"}, indent=1))
    pc = OUT["planted_control"]
    print("planted:", {k: pc[k] for k in ("n", "false_positive_rate", "false_positive_rate_raw_le_0_2", "power")})


if __name__ == "__main__":
    main()
