"""E3: which positional slot (opener / medial / closer) carries the time signal on seals.
Run: .venv/bin/python experiments/direction_time_animal/e3_time.py [--smoke] [--raw]
--smoke: periods shuffled, few iterations (code check only, no outcome)."""
import json, sys
from collections import Counter, defaultdict
import numpy as np
from dta_lib import OUT, icit_texts, signs, to_m, binary_period, lexicon_roles

SMOKE = "--smoke" in sys.argv
RAW = "--raw" in sys.argv
SLOTS = ["opener", "medial", "closer"]
BINS = [(5, 9), (10, 19), (20, 49), (50, 10**9)]
rng = np.random.default_rng(20261115)


def load():
    seen, units, n_all = set(), [], 0
    for t in icit_texts():
        if t["type"] not in ("SEAL:S", "SEAL:R", "SEAL"):
            continue
        bp = binary_period(t)
        if bp is None:
            continue
        ds, per = bp
        key = (ds, per, tuple(t["seq"]))
        if key in seen:
            continue
        seen.add(key); n_all += 1
        if "#" in t["seq"]:
            continue
        sg = signs(t["seq"])
        if not RAW:
            sg = [to_m(x) for x in sg]
        if len(sg) < 3:
            continue
        units.append(dict(stratum=f"{ds}|{t['type']}", ds=ds, per=per, sg=sg))
    return units, n_all


class Data:
    """Token arrays per slot; texts indexed 0..T-1."""
    def __init__(self, units):
        self.units = units
        self.T = len(units)
        strata = sorted({u["stratum"] for u in units})
        self.sidx = np.array([strata.index(u["stratum"]) for u in units])
        self.K = len(strata); self.strata = strata
        self.per = np.array([u["per"] for u in units])
        vocab = sorted({x for u in units for x in u["sg"]})
        self.vocab = vocab; vi = {x: i for i, x in enumerate(vocab)}; self.V = len(vocab)
        self.tok = {}
        for s in SLOTS:
            tt, ss = [], []
            for i, u in enumerate(units):
                g = u["sg"]
                xs = [g[0]] if s == "opener" else [g[-1]] if s == "closer" else g[1:-1]
                for x in xs:
                    tt.append(i); ss.append(vi[x])
            self.tok[s] = (np.array(tt), np.array(ss))
        # permutation helper: indices of texts per stratum
        self.by_stratum = [np.where(self.sidx == k)[0] for k in range(self.K)]
        self.by_cell = defaultdict(list)
        for i in range(self.T):
            self.by_cell[(self.sidx[i], self.per[i])].append(i)


def G_per_sign(D, s, per, text_w=None, texts=None):
    """G per sign for slot s given text period vector per (length T). texts: optional resample (array of text ids)."""
    tt, ss = D.tok[s]
    if texts is not None:
        # expand tokens for resampled texts (with multiplicity)
        cnt = np.bincount(texts, minlength=D.T)
        w = cnt[tt]
    else:
        w = np.ones(len(tt))
    cell = D.sidx[tt] * 2 + per[tt]
    C = 2 * D.K
    O = np.bincount(ss * C + cell, weights=w, minlength=D.V * C).reshape(D.V, C)
    n = O.sum(1)
    slot_cell = O.sum(0).reshape(D.K, 2)
    share = slot_cell / np.maximum(slot_cell.sum(1, keepdims=True), 1e-12)  # P(p|k)
    nk = O.reshape(D.V, D.K, 2).sum(2)                                    # sign count per stratum
    E = (nk[:, :, None] * share[None]).reshape(D.V, C)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(O > 0, O * np.log(O / E), 0.0)
    return 2 * term.sum(1), n


def permute_periods(D, per):
    p = per.copy()
    for idx in D.by_stratum:
        p[idx] = rng.permutation(per[idx])
    return p


def drift(D, per, texts=None, nperm=50):
    """Return dict slot -> (D array, n array) for signs with n>=5; plus total excess G."""
    out, tot = {}, 0.0
    Gs = {s: G_per_sign(D, s, per, texts=texts) for s in SLOTS}
    nullG = {s: np.zeros(D.V) for s in SLOTS}
    for _ in range(nperm):
        pp = permute_periods(D, per)
        for s in SLOTS:
            nullG[s] += G_per_sign(D, s, pp, texts=texts)[0]
    for s in SLOTS:
        G, n = Gs[s]; E0 = nullG[s] / nperm
        m = n >= 5
        out[s] = ((G[m] - E0[m]) / n[m], n[m], np.where(m)[0])
        tot += (G[m] - E0[m]).sum()
    return out, tot


def S_ab(dr, a, b):
    num = den = 0.0
    for lo, hi in BINS:
        Da, na, _ = dr[a]; Db, nb, _ = dr[b]
        ma = (na >= lo) & (na <= hi); mb = (nb >= lo) & (nb <= hi)
        w = min(ma.sum(), mb.sum())
        if w == 0:
            continue
        num += w * (Da[ma].mean() - Db[mb].mean()); den += w
    return num / den if den else np.nan


def stats(dr):
    return dict(S_oc=S_ab(dr, "opener", "closer"), S_om=S_ab(dr, "opener", "medial"), S_mc=S_ab(dr, "medial", "closer"),
                meanD={s: float(dr[s][0].mean()) if len(dr[s][0]) else None for s in SLOTS},
                n_units={s: int(len(dr[s][0])) for s in SLOTS})


def boot_resample(D):
    out = []
    for idx in D.by_cell.values():
        out.append(rng.choice(idx, size=len(idx), replace=True))
    return np.concatenate(out)


def bootstrap(D, per, nboot, nperm):
    res = []
    for _ in range(nboot):
        texts = boot_resample(D)
        dr, _ = drift(D, per, texts=texts, nperm=nperm)
        st = stats(dr); res.append([st["S_oc"], st["S_om"], st["S_mc"]])
    return np.array(res)


def plant(units, q, f):
    """Swap opener tokens to concentrate a fraction q of opener sign types in a home period (within stratum)."""
    U = [dict(u, sg=list(u["sg"])) for u in units]
    cnt = Counter(u["sg"][0] for u in U)
    types = [x for x, c in cnt.items() if c >= 5]
    sel = set(rng.choice(types, size=max(1, int(round(q * len(types)))), replace=False))
    home = {x: int(rng.integers(2)) for x in sel}
    by_str = defaultdict(list)
    for i, u in enumerate(U):
        by_str[u["stratum"]].append(i)
    for x in sel:
        h = home[x]
        for st, idx in by_str.items():
            away = [i for i in idx if U[i]["sg"][0] == x and U[i]["per"] != h]
            donors = [i for i in idx if U[i]["per"] == h and U[i]["sg"][0] not in sel]
            rng.shuffle(away); rng.shuffle(donors)
            k = min(int(round(f * len(away))), len(donors))
            for a, d in zip(away[:k], donors[:k]):
                U[a]["sg"][0], U[d]["sg"][0] = U[d]["sg"][0], U[a]["sg"][0]
    return U


def main():
    units, n_all = load()
    if SMOKE:
        per = [u["per"] for u in units]; rng.shuffle(per)
        for u, p in zip(units, per): u["per"] = int(p)
    NB, NP, NPLANT, NBP, NPP = (20, 10, 3, 20, 10) if SMOKE else (1000, 50, 100, 200, 30)
    D = Data(units); per = D.per
    res = dict(gate=dict(period_labelled_seal_units=n_all, threshold=800, gate_pass=n_all >= 800),
               analysed_texts=D.T, by_stratum=dict(Counter(u["stratum"] + f"|p{u['per']}" for u in units)))
    dr, tot = drift(D, per, nperm=200)
    res["observed"] = stats(dr)
    # global time signal
    nulltot = []
    for _ in range(100 if not SMOKE else 5):
        nulltot.append(drift(D, permute_periods(D, per), nperm=NP)[1])
    res["global_excessG"] = dict(obs=float(tot), null_mean=float(np.mean(nulltot)),
                                 p=float((1 + np.sum(np.array(nulltot) >= tot)) / (1 + len(nulltot))))
    B = bootstrap(D, per, NB, NP)
    for j, k in enumerate(["S_oc", "S_om", "S_mc"]):
        res[k] = dict(obs=float(res["observed"][k]), ci=[float(np.nanpercentile(B[:, j], 2.5)), float(np.nanpercentile(B[:, j], 97.5))],
                      p_one_sided=float(np.mean(B[:, j] <= 0)))
    # per-dataset observed (descriptive)
    res["per_dataset"] = {}
    for ds in sorted({u["ds"] for u in units}):
        sub = [u for u in units if u["ds"] == ds]
        if len(sub) < 60:
            continue
        Ds = Data(sub); d2, _ = drift(Ds, Ds.per, nperm=100)
        res["per_dataset"][ds] = dict(n=len(sub), **{k: (float(v) if not isinstance(v, dict) else v) for k, v in stats(d2).items()})
    # exploratory: by lexicon role (any position)
    roles = lexicon_roles()
    rows = []
    for s in SLOTS:
        Dv, n, ix = dr[s]
        for d, nn, i in zip(Dv, n, ix):
            rows.append((s, D.vocab[i], roles.get(D.vocab[i], "UNK"), float(d), int(nn)))
    res["by_role_exploratory"] = {r: dict(n=sum(1 for x in rows if x[2] == r), meanD=float(np.mean([x[3] for x in rows if x[2] == r])))
                                  for r in sorted({x[2] for x in rows})}
    res["top_drift_signs"] = sorted(rows, key=lambda x: -x[3])[:15]
    # planted power
    res["power"] = {}
    for q, f in [(0.3, 0.5), (0.5, 0.5), (0.5, 0.3), (1.0, 0.3)]:
        hits, Svals = 0, []
        for _ in range(NPLANT):
            Dp = Data(plant(units, q, f))
            drp, _ = drift(Dp, Dp.per, nperm=NPP)
            Bp = bootstrap(Dp, Dp.per, NBP, NPP)
            hits += np.mean(Bp[:, 0] <= 0) < 0.05
            Svals.append(stats(drp)["S_oc"])
        res["power"][f"q{q}_f{f}"] = dict(power=hits / NPLANT, mean_S_oc=float(np.mean(Svals)))
        print(q, f, res["power"][f"q{q}_f{f}"], flush=True)
    # decision
    so, mean = res["S_oc"], res["observed"]["meanD"]
    top = max(mean, key=lambda s: mean[s])
    if so["p_one_sided"] < 0.05 and top == "opener":
        dec = "SUPPORTED"
    elif top == "medial" and res["S_mc"]["p_one_sided"] < 0.05 and res["S_om"]["obs"] <= 0:
        dec = "REFUTED-MEDIAL"
    elif so["p_one_sided"] >= 0.05 and res["power"]["q0.5_f0.5"]["power"] >= 0.8:
        dec = "REFUTED-EQUAL"
    else:
        dec = "INCONCLUSIVE"
    res["decision"] = dec
    print(json.dumps(res, indent=1, default=str))
    if not SMOKE:
        json.dump(res, open(OUT / ("e3_raw.json" if RAW else "e3.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
