"""S8: the corrected round-seal order test (redteam_round_order, KN, null N1) under 13 sign lists.
Pre-registration: docs/prereg/s8_round_signlists.md (sealed before any variant was scored).

Run from the repo root:  .venv/bin/python -I experiments/s8_round_signlists/run.py [--jobs 4]
Writes experiments/s8_round_signlists/results.json. Deterministic (no hash-order-dependent draws).
Groups, units, the KN scorer, d, rare load and the N1 null follow experiments/redteam_round_order/run.py;
the code here is a lean re-implementation of those steps (KN only), so the cached GR/POS scores are not needed.
"""
import argparse, itertools, json, sys, zlib
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT)]
import q4_gulf as Q  # noqa: E402  (clean, KN, FOREIGN_WEST, FOREIGN_CA)
from corpus.load import icit_texts  # noqa: E402

SEED = 20261128
NPERM, NDRAW, NREP, NDRAW_REP = 200, 10_000, 1_000, 2_000
ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
VJ = json.load(open(ROOT / "experiments/signlist_robustness/variants.json"))
BR = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BR.items()}
# overrides used in signlist_robustness/harness.py (font-verified fish codes, two-tier six, jar)
for m, w in zip(["M60", "M66", "M68", "M71", "M73", "M59", "M65", "M67", "M70", "M72"],
                ["W226", "W232", "W234", "W236", "W241", "W220", "W231", "W233", "W235", "W240"]):
    W2M[w] = m
W2M["W016"] = "M109"; W2M["W740"] = "M342"
VARIANTS = ["ICIT", "M77", "parpola", "lump_fish", "lump_numerals", "lump_jar_man", "lump_all",
            "split_s1", "split_s2", "split_s3", "img_hi", "img_mid", "img_lo"]


def g(*tag):
    return np.random.default_rng([SEED] + [zlib.crc32(str(t).encode()) for t in tag])


# ---------------- groups, fixed on the original Wells sequences (as redteam_round_order/run.py) -------------
def groups():
    seen, native, foreign = set(), [], []
    for t in icit_texts():
        s = Q.clean(t["seq"])
        if not s: continue
        site = t["site"]
        grp = "f" if site in Q.FOREIGN_WEST | Q.FOREIGN_CA else "u" if site == "Unknown" else "n"
        if grp == "u": continue
        fmt = "round" if t["type"] in ROUND else "seal" if t["type"].startswith("SEAL") else "other"
        k = (grp, " ".join(s))
        if k in seen: continue
        seen.add(k)
        (native if grp == "n" else foreign).append(dict(seq=s, fmt=fmt, id=t["id"]))
    fk = {" ".join(r["seq"]) for r in foreign}
    return [r for r in native if " ".join(r["seq"]) not in fk]


NATIVE = groups()
NT0 = [r["seq"] for r in NATIVE]
N = len(NT0)
FMT = np.array([r["fmt"] for r in NATIVE]); IDS = np.array([r["id"] for r in NATIVE])
_idx = g("folds").permutation(N); F10 = np.zeros(N, int)
for f in range(10): F10[_idx[f::10]] = f


# ---------------- sign lists on Wells signs ----------------
def relabel_fn(name):
    if name == "ICIT":
        return lambda i, s: list(s)
    if name.startswith("split_"):
        spec = VJ["splits"][name]
        def f(i, s):
            r = g(name, i); out = []
            for w in s:
                k = spec.get(W2M.get(w, ""), 0)
                out.append(f"{w}.{'abc'[r.integers(k)]}" if k else w)
            return out
        return f
    part = VJ["partitions"][name]
    def f(i, s):
        return [part.get(W2M[w], W2M[w]) if w in W2M else w for w in s]
    return f


def perms(seq, r):
    L = len(seq)
    if L <= 5:
        ps = sorted(set(itertools.permutations(seq))); ps.remove(tuple(seq)) if tuple(seq) in ps else None
        ps = [list(p) for p in ps]
        return ps if len(ps) <= NPERM else [ps[i] for i in r.choice(len(ps), NPERM, replace=False)]
    out = []
    for _ in range(NPERM):
        p = list(r.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def key_for(L, rr, pools):
    L = min(L, 9); rr = min(rr, 3)
    for LL in range(L, 0, -1):
        for r2 in range(rr, -1, -1):
            if len(pools.get((LL, r2), [])) >= 5: return (LL, r2)
    raise ValueError("no stratum")


def null_test(vals, keys, pools, ref, ndraw, r):
    obs = float(np.mean(vals))
    draws = np.stack([ref[pools[k][r.integers(len(pools[k]), size=ndraw)]] for k in keys]).mean(0)
    return dict(mean=obs, null_mean=float(draws.mean()), excess=obs - float(draws.mean()),
                p=float((1 + (draws >= obs).sum()) / (ndraw + 1)))


def run_variant(name):
    rl = relabel_fn(name)
    nt = [rl(i, s) for i, s in enumerate(NT0)]
    n_copies = N - len({" ".join(s) for s in nt})
    P = [perms(s, g("perm", name, i)) for i, s in enumerate(nt)]
    cnt = [Counter(x for i in range(N) if F10[i] != f for x in nt[i]) for f in range(10)]
    rare = np.array([sum(cnt[F10[i]][x] < 10 for x in nt[i]) for i in range(N)])
    L = np.array([len(s) for s in nt])
    d = np.full(N, np.nan); dperm = np.full(N, np.nan)  # dperm: one own permutation scored as "real" (C1)
    for f in range(10):
        M = Q.KN([nt[i] for i in range(N) if F10[i] != f])
        for i in np.where(F10 == f)[0]:
            if not P[i]: continue
            pb = np.array([M.bits(p) for p in P[i]])
            d[i] = M.bits(nt[i]) - pb.mean()
            j = g("c1", name, i).integers(len(pb)); dperm[i] = pb[j] - pb.mean()
    has = ~np.isnan(d)
    seal = (FMT == "seal") & has
    circ = np.where((FMT == "round") & has & ~np.isin(IDS, list(NOT_SEALS)))[0]
    pools = defaultdict(list)
    for i in np.where(seal)[0]: pools[(min(L[i], 9), min(rare[i], 3))].append(i)
    pools = {k: np.array(v) for k, v in pools.items()}
    keys = [key_for(L[i], rare[i], pools) for i in circ]
    prim = null_test(d[circ], keys, pools, d, NDRAW, g("null", name))
    # planted controls: draw 8 N1-matched home seals (one per round-seal stratum)
    r = g("planted", name); c1 = c2 = 0
    for _ in range(NREP):
        pick = np.array([pools[k][r.integers(len(pools[k]))] for k in keys])
        c1 += null_test(dperm[pick], keys, pools, d, NDRAW_REP, r)["p"] < 0.05
        c2 += null_test(d[pick], keys, pools, d, NDRAW_REP, r)["p"] < 0.05
    cov = sum(w in W2M for s in NT0 for w in s) / sum(len(s) for s in NT0)
    return dict(variant=name, n_labels=len({x for s in nt for x in s}), n_texts_now_copies=n_copies,
                home_round_ids=[str(x) for x in IDS[circ]], n_home_seals=int(seal.sum()),
                home_round_d=[round(float(x), 3) for x in d[circ]], **{k: round(v, 4) if k != "p" else v for k, v in prim.items()},
                C1_power=c1 / NREP, C2_false_positive=c2 / NREP, bridge_token_coverage=round(cov, 3))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("variants", nargs="*")
    a = ap.parse_args()
    names = a.variants or VARIANTS
    with ProcessPoolExecutor(a.jobs) as ex:
        res = list(ex.map(run_variant, names))
    for r in res:
        print(f"{r['variant']:14s} labels={r['n_labels']:4d} excess={r['excess']:+.3f} p={r['p']:.4g} "
              f"C1={r['C1_power']:.3f} C2={r['C2_false_positive']:.3f} copies={r['n_texts_now_copies']}", flush=True)
    base = next((r for r in res if r["variant"] == "ICIT"), None)
    out = dict(seed=SEED, n_native=N, variants={r["variant"]: r for r in res})
    if base and len(res) == len(VARIANTS):
        alt = [r for r in res if r["variant"] != "ICIT"]
        fails = [r["variant"] for r in alt if not (r["excess"] > 0 and r["p"] < 0.05)]
        out["C0_harness_check"] = dict(excess=base["excess"], p=base["p"], target=1.64,
                                       passed=abs(base["excess"] - 1.64) <= 0.25 and base["p"] < 0.01)
        out["share_of_baseline"] = {r["variant"]: round(r["excess"] / base["excess"], 3) for r in alt}
        out["lists_where_it_disappears"] = fails
        out["verdict"] = "robust" if not fails else "sensitive" if len(fails) <= 2 else "fragile"
        json.dump(out, open(HERE / "results.json", "w"), indent=1)
        print(json.dumps({k: out[k] for k in ("C0_harness_check", "lists_where_it_disappears", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
