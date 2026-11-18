"""Board #45: is jar sign M342 enriched on pottery vs seals off Mohenjo-daro (Harappa, Lothal, Kalibangan)?
Pre-registration: docs/prereg/m342_offsite.md.

    board/run.sh .venv/bin/python -I experiments/m342_offsite/m342.py plant   # known-answer + power (no real contrast)
    board/run.sh .venv/bin/python -I experiments/m342_offsite/m342.py real    # primary + secondaries (only after plant)

Statistic R = O/E: O = pottery texts containing the sign; E = sum over strata of n_pottery_s * (seal rate_s),
strata = signs-in-text bin (1,2,3,4,5,6+) x broken (any '#' or complete False). Strata without seals are dropped.
Null: object-type labels permuted within strata. p = one-sided (enrichment) permutation p.
"""
import sys, json, csv
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct  # noqa

SITES_M = ("Harappa", "Lothal", "Kalibangan")
SITES_I = ("Harappa", "Lothal", "Kalibangan")
SEED = 45
NPERM = 4000
NPLANT = 400
JAR, JAR_W = "M342", "W740"


def nsig(seq):
    return sum(1 for s in seq if s not in ("|", "#"))


def stratum(seq, complete):
    n = nsig(seq)
    broken = ("#" in seq) or (complete is False)
    return (min(n, 6), broken)


def pool_m(recs, pot_types=("pottery graffito",), seal_types=("seal",), keep=None):
    """Distinct texts per class; returns list of (seq, is_pot, stratum)."""
    out, seen = [], set()
    for r in recs:
        if r["site"] not in SITES_M:
            continue
        ot = r["object_type"]
        if ot in pot_types:
            pot = True
        elif ot in seal_types:
            pot = False
        else:
            continue
        if keep is not None and not keep(r):
            continue
        k = (pot, " ".join(r["seq"]))
        if k in seen or nsig(r["seq"]) == 0:
            continue
        seen.add(k)
        out.append((list(r["seq"]), pot, stratum(r["seq"], r.get("complete"))))
    return out


def pool_icit():
    out, seen = [], set()
    for r in icit_texts():
        if r["site"] not in SITES_I:
            continue
        t = r["type"] or ""
        if t.startswith("POT"):
            pot = True
        elif t.startswith("SEAL"):
            pot = False
        else:
            continue
        k = (pot, " ".join(r["seq"]))
        if k in seen or nsig(r["seq"]) == 0:
            continue
        seen.add(k)
        out.append((list(r["seq"]), pot, stratum(r["seq"], r.get("complete"))))
    return out


class Test:
    def __init__(self, pool):
        strata = sorted({p[2] for p in pool if not p[1]}, key=str)  # strata with seals
        sid = {s: i for i, s in enumerate(strata)}
        self.pool = [p for p in pool if p[2] in sid]
        self.dropped_pot = sum(1 for p in pool if p[1] and p[2] not in sid)
        self.s = np.array([sid[p[2]] for p in self.pool])
        self.pot = np.array([p[1] for p in self.pool])
        self.groups = [np.where(self.s == i)[0] for i in range(len(strata))]
        self.n = len(self.pool)

    def has(self, sign, seqs=None):
        seqs = seqs if seqs is not None else [p[0] for p in self.pool]
        return np.array([sign in q for q in seqs], dtype=float)

    def R(self, x, pot):
        O = x[pot].sum(); E = 0.0
        for g in self.groups:
            pg = pot[g]; npot = pg.sum(); nseal = (~pg).sum()
            if npot and nseal:
                E += npot * x[g][~pg].mean()
            elif npot:
                E += npot * x[g].mean()
        return O / E if E > 0 else np.nan, O, E

    def perm_labels(self, rng, k):
        """k label permutations within strata -> bool array (k, n)."""
        out = np.empty((k, self.n), dtype=bool)
        for g in self.groups:
            lab = self.pot[g]
            for j in range(k):
                out[j, g] = rng.permutation(lab)
        return out

    def test(self, x, pot, rng, k=NPERM):
        r, O, E = self.R(x, pot)
        perms = self.perm_labels(rng, k)
        null = np.array([self.R(x, perms[j])[0] for j in range(k)])
        p = (1 + np.sum(null >= r - 1e-12)) / (k + 1)
        p_low = (1 + np.sum(null <= r + 1e-12)) / (k + 1)
        return dict(R=float(r), O=int(O), E=float(E), p=float(p), p_low=float(p_low),
                    null_mean=float(np.nanmean(null)), n_pot=int(pot.sum()), n_seal=int((~pot).sum()))


def control_sign(T, jar=JAR):
    """Non-jar sign whose text count in the pool is closest to M342's (jar family M342-M347 excluded)."""
    c = Counter()
    for q, _, _ in T.pool:
        for s in set(q):
            if s not in ("|", "#"):
                c[s] += 1
    target = c[jar]
    excl = {f"M{i}" for i in range(342, 348)} | {jar}
    cands = [(abs(v - target), s) for s, v in c.items() if s not in excl]
    return min(cands)[1], c[jar], c[min(cands)[1]]


def plant_once(T, rng, ratio, ctrl, k_perm, pot_override=None, jar=JAR):
    pot = T.perm_labels(rng, 1)[0] if pot_override is None else pot_override
    seqs = [list(p[0]) for p in T.pool]
    x = T.has(jar, seqs)
    r0, O, E = T.R(x, pot)
    need = int(round((ratio - 1) * E))
    cand = [i for i in np.where(pot)[0] if x[i] == 0]
    pick = rng.choice(cand, size=min(need, len(cand)), replace=False) if need > 0 and cand else []
    for i in pick:
        q = seqs[i]
        idx = [j for j, s in enumerate(q) if s not in ("|", "#") and s != ctrl]
        if idx:
            q[idx[-1]] = jar  # jar is a final sign: overwrite the last readable sign
    xj = T.has(jar, seqs); xc = T.has(ctrl, seqs)
    a = T.test(xj, pot, rng, k_perm); b = T.test(xc, pot, rng, k_perm)
    return a, b


def plant(T, rng, label, ratio=1.5, reps=NPLANT, k_perm=1000, jar=JAR):
    ctrl, nj, nc = control_sign(T, jar)
    hit = 0; fp = 0; Rs = []; Rc = []; null_hit = 0
    for _ in range(reps):
        a, b = plant_once(T, rng, ratio, ctrl, k_perm, jar=jar)
        hit += (a["p"] < 0.05 and a["R"] >= 1.25); Rs.append(a["R"])
        fp += (b["p"] < 0.05 and b["R"] >= 1.25); Rc.append(b["R"])
    # size: no plant
    for _ in range(reps // 2):
        a, _ = plant_once(T, rng, 1.0, ctrl, k_perm, jar=jar)
        null_hit += (a["p"] < 0.05 and a["R"] >= 1.25)
    return dict(pool=label, ratio=ratio, reps=reps, power=hit / reps, median_R_planted=float(np.median(Rs)),
                control=ctrl, control_texts=nc, jar_texts=nj, control_fp=fp / reps, median_R_control=float(np.median(Rc)),
                size=null_hit / (reps // 2), n_pot=int(T.pot.sum()), n_seal=int((~T.pot).sum()), dropped_pot=T.dropped_pot)


def boosted(pool, rng, n_pot):
    pots = [p for p in pool if p[1]]; seals = [p for p in pool if not p[1]]
    idx = rng.choice(len(pots), size=n_pot, replace=True)
    return seals + [pots[i] for i in idx]


def cons_recs():
    return json.load(open(ROOT / "experiments/consensus_corpus/out/corpora/cons_sign_ext.json"))["recs"]


def main(phase):
    rng = np.random.default_rng(SEED)
    out = HERE / f"{phase}.json"
    res = {}
    cons = pool_m(cons_recs())
    T = Test(cons)
    if phase == "plant":
        res["primary"] = plant(T, rng, "consensus H/L/K pottery vs seal")
        json.dump(res, open(out, "w"), indent=1); print(res, flush=True)
        res["primary_ratio_2"] = plant(T, rng, "same, 2.0x", ratio=2.0, reps=200)
        res["icit"] = plant(Test(pool_icit()), rng, "ICIT H/L/K POT vs SEAL", reps=200, jar=JAR_W)
        if res["primary"]["power"] < 0.8:
            res["needed"] = []
            for n in (100, 150, 200, 300, 400):
                Tb = Test(boosted(cons, rng, n))
                r = plant(Tb, rng, f"pottery resampled to {n}", reps=150, k_perm=500)
                res["needed"].append(r)
                print(n, r["power"], flush=True)
                if r["power"] >= 0.8:
                    break
    else:
        x = T.has(JAR); ctrl, _, _ = control_sign(T)
        res["primary"] = T.test(x, T.pot, rng)
        res["primary"]["control"] = ctrl
        res["primary_control"] = T.test(T.has(ctrl), T.pot, rng)
        Tb = Test(pool_m(distinct(m77_texts())))
        res["s1_base_m77"] = Tb.test(Tb.has(JAR), Tb.pot, rng)
        Ti = Test(pool_icit())
        res["s2_icit"] = Ti.test(Ti.has(JAR_W), Ti.pot, rng)
        Ts = Test(pool_m(cons_recs(), pot_types=("sealing",)))
        res["s3_sealing_vs_seal"] = Ts.test(Ts.has(JAR), Ts.pot, rng)
        # s4: Harappa seals restricted to register-confirmed seals (Vats 1940), Lothal/Kalibangan unchanged
        reg = {r["m77_text_no"] for r in csv.DictReader(open(ROOT / "experiments/old_registers/registers.csv"))
               if r["site"] == "Harappa" and r["m77_text_no"]}
        keys = {" ".join(t["seq"]) for t in m77_texts() if str(t["text_no"]) in reg}
        keep = lambda r: not (r["site"] == "Harappa" and r["object_type"] == "seal" and r["key0"] not in keys)
        T4 = Test(pool_m(cons_recs(), keep=keep))
        res["s4_register_seals"] = T4.test(T4.has(JAR), T4.pot, rng)
        res["s4_register_seals"]["harappa_register_texts"] = len(keys)
        for site in SITES_M:
            Tsite = Test(pool_m([r for r in cons_recs() if r["site"] == site]))
            if Tsite.pot.sum():
                res[f"site_{site}"] = Tsite.test(Tsite.has(JAR), Tsite.pot, rng)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
