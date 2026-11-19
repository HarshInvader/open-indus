"""Planted-power simulation for the HARP pack (docs/prereg/harp_pack.md, section "Power").

Synthetic spreadsheets at the likely size are built from real ICIT Harappa statistics (sign
frequencies and lengths of pottery graffiti; Harappa seal texts; the 386 docket tablets of
experiments/tablet_archives/tablets.csv), an effect of the registered size is planted, and the
FROZEN functions in score.py are run on them. Power = share of planted datasets that reach the
pass rule at alpha = 0.05 / 13 (Bonferroni over all 13 candidate family tests, conservative).

Run:  board/run.sh .venv/bin/python -I experiments/harp_pack/power.py [--quick]
Writes power.json (kept / dropped / min_n, read by score.py) and power.log.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, binomtest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, distinct  # noqa: E402
import experiments.harp_pack.score as S  # noqa: E402
S.MIN_N, S.DROPPED = {}, {}  # power is computed without the min-n gates it is used to set

QUICK = "--quick" in sys.argv
N_CAND = 13
ALPHA = 0.05 / N_CAND
REPS_EXACT = 60 if QUICK else 200
REPS_PERM = 30 if QUICK else 100
N_PERM = 299 if QUICK else 999
REPS_NULL = 30 if QUICK else 60
rng = np.random.default_rng(7)
OUT = Path(__file__).with_name("power.json")
LOG = open(Path(__file__).with_name("power.log"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


# ------------------------------------------------------------------ real inputs (no outcomes)
H = [r for r in icit_texts() if r["site"] == "Harappa"]
graf = distinct([r for r in H if r["type"] in ("POT:T:g", "POsT:T:g")])
tok = {}
lens = []
nbroken = 0
for r in graf:
    sg = [s for s in r["seq"] if s not in ("|", "#")]
    if not sg:
        continue
    lens.append(len(sg))
    nbroken += "#" in r["seq"]
    for s in sg:
        tok[s] = tok.get(s, 0) + 1
SIGNS = np.array(sorted(tok))
P = np.array([tok[s] for s in SIGNS], float)
P /= P.sum()
LENS = np.array(lens)
BROKEN = nbroken / len(lens)
NONJAR = SIGNS != "W740"
P_NJ = P * NONJAR
P_NJ /= P_NJ.sum()
TRIO_W = [s for s in SIGNS if s in S.TRIO] or ["W820"]
TOP_NONJAR = [s for s in SIGNS[np.argsort(-P)] if s not in S.JAR and s not in S.TRIO][:10]
SEALS = S.harappa_seals()
SEAL_RATE = {}
for sg in SEALS:
    k = S.len_stratum(sg)
    c = SEAL_RATE.setdefault(k, [0, 0])
    c[0] += 1
    c[1] += S._has(sg, S.JAR)
SEAL_RATE = {k: b / a for k, (a, b) in SEAL_RATE.items()}
TABS = S.load_tablets()
PERIODS = ["1", "2", "3A", "3B", "3C", "4", "5"]
PSHARE = np.array([0.05, 0.10, 0.15, 0.25, 0.30, 0.10, 0.05])
FORMS = ["storage_jar", "jar_other", "bowl_dish", "goblet_beaker", "other"]
FSHARE = np.array([0.40, 0.15, 0.25, 0.10, 0.10])

SCEN = {
    # readable sherd rows, pre-firing handwritten share, form known share, rim share, lots per period,
    # new (not in ICIT) readable rows, tablet lot coverage, CRP theta for tablet lots
    "central": dict(n_sherd=975, pre=0.20, form=1.0, rim=0.30, lots_pp=60, n_new=740, tab_cov=0.8, theta=60),
    "pessimistic": dict(n_sherd=600, pre=0.10, form=0.7, rim=0.20, lots_pp=40, n_new=400, tab_cov=0.5, theta=120),
}


def text(L=None):
    L = L or int(rng.choice(LENS))
    return list(rng.choice(SIGNS, size=L, p=P))


def sherds(n, pre, form=1.0, rim=0.0, lots_pp=60):
    per = rng.choice(PERIODS, size=n, p=PSHARE)
    rows = []
    for i in range(n):
        sg = text()
        if rng.random() < BROKEN:
            sg.insert(int(rng.integers(0, len(sg) + 1)), "#")
        rows.append(dict(
            object_type="POT", signs=sg, readable_n=sum(1 for x in sg if x != "#"),
            firing_class="pre_hand" if rng.random() < pre else "post",
            lot_key=f"{per[i]}-{int(rng.integers(lots_pp))}", period=per[i],
            vessel_form=rng.choice(FORMS, p=FSHARE) if rng.random() < form else "NA",
            rim_diam_mm=np.nan, icit_cisi=None, mass_g=np.nan))
    df = pd.DataFrame(rows)
    if rim:
        m = rng.random(n) < rim
        df.loc[m, "rim_diam_mm"] = rng.normal(250, 80, m.sum())
    return df


def _replace(sg, new, avoid=()):
    pos = [i for i, x in enumerate(sg) if x != "#" and x not in avoid]
    if not pos:
        return sg + [new]
    sg = list(sg)
    sg[int(rng.choice(pos))] = new
    return sg


def base_rate(S_, n=20000):
    return np.mean([S._has(text(), S_) for _ in range(n)])


JAR_BASE = base_rate(S.JAR)
TRIO_BASE = base_rate(S.TRIO)


# ------------------------------------------------------------------ plants
def plant_C1(df):  # pre-firing jar rate 0.04 vs base ~0.17 (FS1: 1/25 painted vs 70/384 graffiti)
    q = 1 - 0.04 / JAR_BASE
    out = []
    for sg, c in zip(df["signs"], df["firing_class"]):
        if c == "pre_hand" and S._has(sg, S.JAR) and rng.random() < q:
            sg = [str(rng.choice(SIGNS, p=P_NJ)) if x == "W740" else x for x in sg]
        out.append(sg)
    df["signs"] = out
    return df


def plant_C2(df):  # pre-firing trio share 0.15 vs base ~0.05 (FS1: >= 15% on painted)
    q = (0.15 - TRIO_BASE) / (1 - TRIO_BASE)
    df["signs"] = [(_replace(sg, str(rng.choice(TRIO_W)), S.JAR) if c == "pre_hand" and not S._has(sg, S.TRIO)
                    and rng.random() < q else sg) for sg, c in zip(df["signs"], df["firing_class"])]
    return df


def plant_C3(df):  # one pre-firing sign: 6% of pre units, 0.5% of post units
    df["signs"] = [(_replace(sg, "W999") if rng.random() < (0.06 if c == "pre_hand" else 0.005) else sg)
                   for sg, c in zip(df["signs"], df["firing_class"])]
    return df


def plant_C4(df):  # 3 frequent signs, each +10 points in one random form class
    picks = rng.choice(TOP_NONJAR, size=3, replace=False)
    tgt = {s: rng.choice(FORMS[:4]) for s in picks}
    out = []
    for sg, f in zip(df["signs"], df["vessel_form"]):
        for s, ff in tgt.items():
            if f == ff and s not in sg and rng.random() < 0.10:
                sg = sg + [s]
        out.append(sg)
    df["signs"] = out
    return df


def plant_C5(df, rr=2.0):  # jar sign rate on storage jars = rr x other forms
    q = (rr * JAR_BASE - JAR_BASE) / (1 - JAR_BASE)
    df["signs"] = [(_replace(sg, "W740") if f == "storage_jar" and not S._has(sg, S.JAR) and rng.random() < q else sg)
                   for sg, f in zip(df["signs"], df["vessel_form"])]
    return df


def new_pottery(n, eff, lots_pp=60):
    """pottery rows whose jar presence follows the Harappa seal rate of their length stratum x eff."""
    per = rng.choice(PERIODS, size=n, p=PSHARE)
    rows = []
    for i in range(n):
        L = int(rng.choice(LENS))
        brk = rng.random() < BROKEN
        k = ("1-5" if L <= 5 else "6+") + ("|broken" if brk else "|complete")
        r = SEAL_RATE.get(k, np.mean(list(SEAL_RATE.values())))
        sg = list(rng.choice(SIGNS, size=L, p=P_NJ))
        if rng.random() < min(1.0, eff * r):
            sg[int(rng.integers(L))] = "W740"
        if brk:
            sg.insert(int(rng.integers(0, L + 1)), "#")
        rows.append(dict(object_type="POT", signs=sg, readable_n=L, firing_class="post",
                         lot_key=f"{per[i]}-{int(rng.integers(lots_pp))}", period=per[i],
                         vessel_form="NA", rim_diam_mm=np.nan, icit_cisi=None, mass_g=np.nan))
    return pd.DataFrame(rows)


def plant_C9(df, rho=0.5):
    m = df["rim_diam_mm"].notna().to_numpy()
    from experiments.harp_pack.loader import numeral_value
    v = df["signs"].map(numeral_value).to_numpy().astype(float)
    z = pd.Series(v + rng.random(len(v)) * 1e-6).rank().to_numpy()
    z = (z - z.mean()) / z.std()
    rim = 250 + 80 * (rho * z + np.sqrt(1 - rho ** 2) * rng.normal(size=len(v)))
    df.loc[m, "rim_diam_mm"] = rim[m]
    return df


def tablets_df(cov, theta, plant):
    t = TABS.copy().reset_index(drop=True)
    t["unit"] = np.where(t["copy_group"].notna(), t["copy_group"].astype(str), "oid" + t["oid"].astype(str))
    lots = np.array([None] * len(t), dtype=object)
    for g, idx in t.groupby(t["period_key"].fillna("NA")).groups.items():
        idx = np.asarray(idx)
        th = max(1.0, theta * len(idx) / len(t))
        counts = []
        for i in idx:  # Chinese restaurant process within period
            w = np.array(counts + [th], float)
            j = int(rng.choice(len(w), p=w / w.sum()))
            if j == len(counts):
                counts.append(1)
            else:
                counts[j] += 1
            lots[i] = f"{g}#{j}"
    known = rng.random(len(t)) < cov
    lots[~known] = None
    t["lot_tmp"] = lots
    if plant:
        glob = t["tier"].value_counts(normalize=True).reindex([2.0, 3.0, 4.0]).to_numpy()
        mix = {l: rng.dirichlet(3 * glob) for l in set(lots) if l is not None}
        tiers = {}
        for i, (u, l) in enumerate(zip(t["unit"], lots)):
            if l is None:
                continue
            key = (u, l)
            if key not in tiers:
                tiers[key] = 2 + int(rng.choice(3, p=mix[l]))
            t.loc[i, "tier"] = float(tiers[key])
    m = t["cisi"].notna() & (t["cisi"] != "-") & t["lot_tmp"].notna()
    df = pd.DataFrame(dict(icit_cisi=t.loc[m, "cisi"], lot_key=t.loc[m, "lot_tmp"], period="NA",
                           mass_g=np.nan, object_type="TAB"))
    return df, t.drop(columns=["lot_tmp"])


# ------------------------------------------------------------------ runners
def passed(k, r):
    return bool(r.get("eligible", True) and r["p"] < ALPHA and r.get("pass_effect", True))


def run_test(k, scen, scale=1.0, plant=True):
    sc = SCEN[scen]
    kw = dict(n_perm=N_PERM, rng=rng)
    if k in ("C1", "C2", "C3", "C4", "C5", "C9"):
        df = sherds(int(sc["n_sherd"] * scale), sc["pre"], sc["form"], sc["rim"], sc["lots_pp"])
        if plant:
            df = {"C1": plant_C1, "C2": plant_C2, "C3": plant_C3, "C4": plant_C4,
                  "C5": plant_C5, "C9": plant_C9}[k](df)
        if k == "C5":
            return S.test_C5(df)
        return S.TESTS[k](df, **kw)
    if k == "C6":
        df = new_pottery(int(sc["n_new"] * scale), 1.5 if plant else 1.0, sc["lots_pp"])
        return S.test_C6(df, seals=SEALS, icit_pot=(set(), {}), require_ids=False)
    if k == "C7":
        df, t = tablets_df(sc["tab_cov"] * scale, sc["theta"], plant)
        return S.test_C7(df, tabs=t, **kw)
    raise KeyError(k)


def size_key(k, r):
    return {"C1": "n_pre", "C2": "n_pre", "C3": "n_pre", "C4": "n", "C5": "n", "C6": "n_pot",
            "C7": "n_units", "C9": "n"}[k]


def power(k, scen, scale=1.0, plant=True):
    reps = REPS_PERM if k in ("C4", "C7", "C9") else REPS_EXACT
    if not plant:
        reps = REPS_NULL
    hits, ns, extra = 0, [], []
    for _ in range(reps):
        r = run_test(k, scen, scale, plant)
        ns.append(r.get(size_key(k, r), 0))
        if k == "C5":
            hits += r["verdict"].startswith("FAIL") if plant else r["verdict"].startswith("PASS")
        else:
            hits += passed(k, r)
        extra.append(r.get("RR", r.get("R", r.get("rho", r.get("G", np.nan)))))
    return dict(power=hits / reps, reps=reps, mean_n=float(np.mean(ns)),
                mean_effect=float(np.nanmean([e for e in extra if e is not None])))


# ------------------------------------------------------------------ dropped-candidate simulations
def sim_bangles(n=10, reps=REPS_EXACT):
    B = [r for r in H if r["type"] == "BNGL"]
    from experiments.harp_pack.loader import numeral_value
    vs = np.array([numeral_value(r["seq"]) for r in B] or [0])
    ovals = np.mean(["W790" in r["seq"] for r in B])
    h_a = h_b = 0
    for _ in range(reps):
        v = rng.choice(vs, n).astype(float)
        z = pd.Series(v + rng.random(n) * 1e-6).rank().to_numpy()
        z = (z - z.mean()) / (z.std() or 1)
        d = 58 + 3 * (0.5 * z + np.sqrt(0.75) * rng.normal(size=n))
        _, p = S.strat_spearman(v, d, np.zeros(n), N_PERM, rng)
        h_a += p < ALPHA
        o = rng.random(n) < ovals
        if 0 < o.sum() < n:
            d2 = rng.normal(58, 3, n) + 3 * o  # oval bangles 1 SD larger
            h_b += mannwhitneyu(d2[o], d2[~o], alternative="two-sided").pvalue < ALPHA
    return dict(C10a=dict(power=h_a / reps, n=n, effect="rho 0.5", V_pos_share=float((vs > 0).mean())),
                C10b=dict(power=h_b / reps, n=n, effect="1 SD", oval_share=float(ovals)))


def sim_small_class(n, reps=REPS_EXACT, rule=True):
    if rule and n < 8:
        return dict(power=0.0, n=n, note="below magnitude.md minimum n=8: UNTESTABLE by rule")
    hits = 0
    for _ in range(reps):
        v = rng.integers(0, 8, n).astype(float)
        m = 0.5 * (v - v.mean()) / (v.std() or 1) + np.sqrt(0.75) * rng.normal(size=n)
        hits += S.strat_spearman(v, m, np.zeros(n), N_PERM, rng)[1] < ALPHA
    return dict(power=hits / reps, n=n)


def sim_ticked_fish(n_seal, reps=REPS_PERM, rate=6 / 417, n_area=15):
    hits, nf = 0, []
    for _ in range(reps):
        sz = rng.dirichlet(np.ones(n_area) * 2)
        area = rng.choice(n_area, n_seal, p=sz)
        per = rng.choice(len(PERIODS), n_seal, p=PSHARE)
        f = rng.random(n_seal) < rate
        big = [a for a in range(n_area) if (area == a).sum() >= 20]
        if big:
            a = int(rng.choice(big))
            idx = np.where((area == a) & ~f)[0]
            extra = rng.binomial(len(idx), min(1.0, 2 * rate))
            f[rng.choice(idx, extra, replace=False)] = True
        nf.append(int(f.sum()))
        if f.sum() < 2:
            continue
        strata = S._strata_groups(per)
        obs = S.g_table(area, f.astype(int), n_area, 2)
        null = np.array([S.g_table(area, f.astype(int)[S._perm_index(strata, rng)], n_area, 2)
                         for _ in range(N_PERM)])
        hits += (1 + np.sum(null >= obs - 1e-9)) / (1 + N_PERM) < ALPHA
    return dict(power=hits / reps, n_seal=n_seal, mean_fish=float(np.mean(nf)), effect="3x in one area")


def sim_bangle_oval_new(n_new, reps=2000):
    hits = 0
    for _ in range(reps):
        x = rng.binomial(n_new, 0.15)
        if n_new >= 10 and x / n_new >= 0.08 and binomtest(x, n_new, 0.0106, "greater").pvalue < ALPHA:
            hits += 1
    return dict(power=hits / reps, n_new=n_new, note="BO-H1 needs >= 10 new bangle texts")


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    t0 = time.time()
    log(f"alpha={ALPHA:.5f} reps exact/perm/null={REPS_EXACT}/{REPS_PERM}/{REPS_NULL} n_perm={N_PERM} quick={QUICK}")
    log(f"generator: {len(LENS)} Harappa graffiti texts, mean len {LENS.mean():.2f}, broken {BROKEN:.2f}, "
        f"jar base {JAR_BASE:.3f}, trio base {TRIO_BASE:.3f}; seal strata rates {SEAL_RATE}")
    res = {"alpha": ALPHA, "quick": QUICK, "central": {}, "pessimistic": {}, "null_size": {}, "curve": {}}
    cand = ["C1", "C2", "C3", "C4", "C6", "C7", "C9", "C5"]
    for k in cand:
        res["central"][k] = power(k, "central")
        log("central", k, res["central"][k], f"{time.time() - t0:.0f}s")
    for k in cand:
        res["null_size"][k] = power(k, "central", plant=False)
        log("null", k, res["null_size"][k], f"{time.time() - t0:.0f}s")
    for k in cand:
        res["pessimistic"][k] = power(k, "pessimistic")
        log("pessimistic", k, res["pessimistic"][k], f"{time.time() - t0:.0f}s")
    # power curve for min-n (kept candidates only)
    for k in cand:
        if k == "C5" or res["central"][k]["power"] < 0.8:
            continue
        res["curve"][k] = {}
        for sc in (0.25, 0.5, 0.75):
            res["curve"][k][str(sc)] = power(k, "central", sc)
            log("curve", k, sc, res["curve"][k][str(sc)], f"{time.time() - t0:.0f}s")
        res["curve"][k]["1.0"] = res["central"][k]
    # dropped candidates
    b = sim_bangles(10)
    res["central"].update(b)
    res["central"]["C11"] = sim_small_class(4)
    res["central"]["C12"] = sim_small_class(7)
    res["central"]["C12_if_rule_ignored"] = sim_small_class(7, rule=False)
    res["central"]["C13"] = sim_ticked_fish(200)
    res["pessimistic"]["C13"] = sim_ticked_fish(120)
    res["central"]["C14"] = sim_bangle_oval_new(3)
    log("dropped-candidate sims", {k: res["central"][k] for k in ("C10a", "C10b", "C11", "C12", "C13", "C14")})
    # decisions
    kept, dropped, min_n = [], {}, {}
    for k in ["C1", "C2", "C3", "C4", "C6", "C7", "C9", "C10a", "C10b", "C11", "C12", "C13", "C14", "C5"]:
        pw = res["central"][k]["power"]
        if pw >= 0.8:
            if k != "C5":
                kept.append(k)
            cur = res["curve"].get(k, {})
            ok = [float(s) for s, v in cur.items() if v["power"] >= 0.8]
            sc = min(ok) if ok else 1.0
            min_n[k] = int(np.floor(cur.get(str(sc), res["central"][k])["mean_n"])) if cur else 0
        else:
            dropped[k] = round(pw, 3)
    if res["central"]["C5"]["power"] >= 0.8:
        min_n["C5"] = 0
    res.update(kept=kept, dropped=dropped, min_n=min_n, seconds=round(time.time() - t0))
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    log("KEPT", kept, "DROPPED", dropped, "MIN_N", min_n, f"{time.time() - t0:.0f}s")
