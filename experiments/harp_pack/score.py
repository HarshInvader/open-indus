"""Frozen scorer for the HARP prediction pack. Pre-registration: docs/prereg/harp_pack.md.

Run (January 2027, once, after the spreadsheet is in raw/harp/ and the loader report is checked):
    board/run.sh .venv/bin/python -I experiments/harp_pack/score.py raw/harp/<file> > experiments/harp_pack/score.log

Kept tests (Holm family): see KEPT. Dropped tests are listed in DROPPED and never computed here.
Every test function returns a dict with n, effect, raw p and an eligibility flag; run_all applies
Holm over the eligible kept tests and the frozen verdict rules.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import hypergeom, fisher_exact

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

JAR = {"W740"}                                  # M342
TRIO = {"W820", "W741", "W861", "W817"}         # M391, M343, M267 (both Wells numbers of M267)
FAMILY_ALPHA = 0.05
SEED = 20270105

# kept tests and their frozen minimum sizes (filled from power.py, central scenario; see prereg)
KEPT = ["C1", "C2", "C3", "C4", "C6", "C7", "C9"]
SEPARATE = ["C5"]   # F3b (forward_predictions.md), own rule, not in the Holm family
MIN_N = {}          # set below from power.json
DROPPED = {}        # set below from power.json

_PJ = Path(__file__).with_name("power.json")
if _PJ.exists():
    _pw = json.load(open(_PJ))
    MIN_N = _pw.get("min_n", {})
    DROPPED = _pw.get("dropped", {})
    KEPT = _pw.get("kept", KEPT)


# ---------------------------------------------------------------- statistics
def strat_hyper(strata):
    """strata: iterable of (N, K, n, a): stratum size, units with feature, units in target class,
    target-class units with feature. Null = class labels permuted within stratum.
    -> (A, E, p_upper, p_lower)."""
    pmf = np.array([1.0])
    A, E = 0, 0.0
    for N, K, n, a in strata:
        N, K, n, a = int(N), int(K), int(n), int(a)
        if N == 0 or n == 0:
            continue
        x = np.arange(0, min(n, K) + 1)
        pmf = np.convolve(pmf, hypergeom.pmf(x, N, K, n))
        A += a
        E += n * K / N
    pmf = pmf / pmf.sum()
    return A, E, float(min(1.0, pmf[A:].sum())), float(min(1.0, pmf[: A + 1].sum()))


def _perm_index(strata, rng):
    """one within-stratum permutation of positions; strata = list of index arrays."""
    out = np.arange(sum(len(s) for s in strata))
    for s in strata:
        out[s] = s[rng.permutation(len(s))]
    return out


def _strata_groups(labels):
    labels = np.asarray(labels)
    return [np.where(labels == u)[0] for u in np.unique(labels)]


def g_presence(X, lab, k):
    """sum over columns of X (0/1 units x signs) of the LR G of presence x label (k classes)."""
    oh = np.zeros((len(lab), k))
    oh[np.arange(len(lab)), lab] = 1
    O1 = X.T @ oh
    col = oh.sum(0)
    O0 = col[None, :] - O1
    N = len(lab)
    r1 = X.sum(0)[:, None]
    E1 = r1 * col[None, :] / N
    E0 = (N - r1) * col[None, :] / N
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(O1 > 0, O1 * np.log(O1 / E1), 0).sum() + np.where(O0 > 0, O0 * np.log(O0 / E0), 0).sum()
    return 2 * g


def g_table(rows, cols, nr, nc):
    O = np.zeros((nr, nc))
    np.add.at(O, (rows, cols), 1)
    E = O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / O.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2 * np.where(O > 0, O * np.log(O / E), 0).sum()


def within_ranks(x, strata):
    """ranks within stratum scaled to (-0.5, 0.5); ties = average rank."""
    out = np.zeros(len(x))
    for s in strata:
        r = pd.Series(x[s]).rank(method="average").to_numpy()
        out[s] = (r - 0.5) / len(s) - 0.5
    return out


def strat_spearman(v, m, strata_labels, n_perm, rng):
    strata = _strata_groups(strata_labels)
    rm = within_ranks(np.asarray(m, float), strata)
    rv = within_ranks(np.asarray(v, float), strata)

    def corr(a):
        if a.std() == 0 or rm.std() == 0:
            return 0.0
        return float(np.corrcoef(a, rm)[0, 1])
    obs = corr(rv)
    null = np.array([corr(rv[_perm_index(strata, rng)]) for _ in range(n_perm)])
    p = (1 + np.sum(np.abs(null) >= abs(obs) - 1e-12)) / (1 + n_perm)
    return obs, float(p)


def holm(ps):
    ks = sorted(ps, key=lambda k: ps[k])
    m, out, run = len(ks), {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (m - i) * ps[k]))
        out[k] = run
    return out


def _has(signs, S):
    return any(s in S for s in signs)


def _rr(a, n1, b, n2):
    return ((a + 0.5) / (n1 + 1)) / ((b + 0.5) / (n2 + 1))


# ---------------------------------------------------------------- units
def sherd_units(df, cls_col, classes=None):
    """distinct (class, lot, sequence) among sherd rows with a readable text.
    Missing lot -> 'NA|<period>' so identical texts without a lot collapse within period."""
    d = df[(df["object_type"] == "POT") & df["signs"].notna()].copy()
    d = d[d["readable_n"] > 0]
    if classes is not None:
        d = d[d[cls_col].isin(classes)]
    d["seqs"] = d["signs"].map(" ".join)
    lot = d["lot_key"].astype(object)
    d["lotu"] = np.where(lot.isna(), "NA|" + d["period"].astype(str), lot.astype(str))
    return d.drop_duplicates([cls_col, "lotu", "seqs"]).reset_index(drop=True)


def _two_class(u, S, tail):
    pre = (u["firing_class"] == "pre_hand").to_numpy()
    f = u["signs"].map(lambda s: _has(s, S)).to_numpy()
    strata = []
    for _, g in u.groupby("period").groups.items():
        g = np.asarray(g)
        strata.append((len(g), f[g].sum(), pre[g].sum(), (f[g] & pre[g]).sum()))
    A, E, pu, pl = strat_hyper(strata)
    npre, npost = int(pre.sum()), int((~pre).sum())
    a, b = int((f & pre).sum()), int((f & ~pre).sum())
    return dict(n_pre=npre, n_post=npost, a_pre=a, b_post=b,
                share_pre=a / max(npre, 1), share_post=b / max(npost, 1),
                RR=_rr(a, npre, b, npost), A=A, E=E, p=pu if tail == "upper" else pl)


# ---------------------------------------------------------------- tests
def test_C1(df, **_):
    """jar sign M342 depleted on pre-firing handwritten marks vs post-firing graffiti (FS1)."""
    u = sherd_units(df, "firing_class", ["pre_hand", "post"])
    r = _two_class(u, JAR, "lower")
    r["eligible"] = r["n_pre"] >= MIN_N.get("C1", 0) and r["n_post"] >= 50
    r["pass_effect"] = r["RR"] <= 0.5
    r["kill"] = r["RR"] >= 0.8
    return r


def test_C2(df, **_):
    """opener trio M391/M343/M267 enriched on pre-firing handwritten marks (FS1)."""
    u = sherd_units(df, "firing_class", ["pre_hand", "post"])
    r = _two_class(u, TRIO, "upper")
    r["eligible"] = r["n_pre"] >= MIN_N.get("C2", 0) and r["n_post"] >= 50
    r["pass_effect"] = r["RR"] >= 2   # FS1's ">= 15%" wording is reported, not gated (see prereg)
    r["kill"] = r["RR"] <= 1.2
    return r


def lot_half(lot):
    return int(hashlib.sha256(str(lot).encode()).hexdigest(), 16) % 2


def test_C3(df, **_):
    """a pre-firing vocabulary found in one half of the lots replicates in the other
    (firing_stage primary, with a lot split instead of a site split)."""
    u = sherd_units(df, "firing_class", ["pre_hand", "post"])
    half = u["lotu"].map(lot_half).to_numpy()
    pre = (u["firing_class"] == "pre_hand").to_numpy()
    dev, ho = half == 0, half == 1
    n1, n2 = int((dev & pre).sum()), int((dev & ~pre).sum())
    cnt = {}
    for sg, p_, d_ in zip(u["signs"], pre, dev):
        if not d_:
            continue
        for s in set(sg) - {"#"}:
            c = cnt.setdefault(s, [0, 0])
            c[0 if p_ else 1] += 1
    S = sorted(s for s, (a, b) in cnt.items() if a >= 3 and _rr(a, n1, b, n2) >= 5)
    uh = u[ho].reset_index(drop=True)
    r = dict(S=S, n_dev_pre=n1, n_dev_post=n2)
    if not S or len(uh) == 0:
        r.update(n_pre=int((ho & pre).sum()), p=1.0, R_ho=float("nan"), eligible=False,
                 pass_effect=False, kill=False, note="S empty")
        return r
    t = _two_class(uh, set(S), "upper")
    r.update(n_pre=t["n_pre"], n_post=t["n_post"], a_pre=t["a_pre"], b_post=t["b_post"],
             R_ho=t["RR"], p=t["p"])
    r["eligible"] = t["n_pre"] >= MIN_N.get("C3", 0)
    r["pass_effect"] = t["RR"] >= 2
    r["kill"] = t["RR"] < 1.25
    return r


def _form_universe(df):
    u = sherd_units(df, "vessel_form")
    u = u[u["vessel_form"] != "NA"]
    vc = u["vessel_form"].value_counts()
    keep = vc[vc >= 30].index
    return u[u["vessel_form"].isin(keep)].reset_index(drop=True)


def test_C4(df, n_perm=2000, rng=None, **_):
    """omnibus: sign presence x vessel form (sum of G over signs in >= 10 units)."""
    rng = rng or np.random.default_rng(SEED)
    u = _form_universe(df)
    if len(u) == 0:
        return dict(n=0, p=1.0, eligible=False, pass_effect=False, kill=False)
    forms = sorted(u["vessel_form"].unique())
    lab = u["vessel_form"].map({f: i for i, f in enumerate(forms)}).to_numpy()
    sc = {}
    for sg in u["signs"]:
        for s in set(sg) - {"#"}:
            sc[s] = sc.get(s, 0) + 1
    signs = sorted(s for s, c in sc.items() if c >= 10)
    if not signs or len(forms) < 2:
        return dict(n=len(u), p=1.0, eligible=False, pass_effect=False, kill=False)
    idx = {s: i for i, s in enumerate(signs)}
    X = np.zeros((len(u), len(signs)))
    for i, sg in enumerate(u["signs"]):
        for s in set(sg):
            if s in idx:
                X[i, idx[s]] = 1
    strata = _strata_groups((u["period"] + "|" + u["firing_class"]).to_numpy())
    obs = g_presence(X, lab, len(forms))
    null = np.array([g_presence(X, lab[_perm_index(strata, rng)], len(forms)) for _ in range(n_perm)])
    p = (1 + np.sum(null >= obs - 1e-9)) / (1 + n_perm)
    return dict(n=len(u), forms=forms, n_signs=len(signs), G=float(obs), G_null=float(null.mean()),
                p=float(p), eligible=len(u) >= MIN_N.get("C4", 0), pass_effect=True, kill=False)


def test_C5(df, **_):
    """F3b (forward_predictions.md): jar sign on storage jars vs other forms. Prediction: RR < 1.5."""
    u = _form_universe(df) if len(df) else df
    if len(u) == 0:
        return dict(n=0, eligible=False, verdict="UNTESTABLE")
    if (u["vessel_form"] == "storage_jar").any():
        tgt = u["vessel_form"] == "storage_jar"
        contrast = "storage_jar vs other"
    else:
        tgt = u["vessel_form"].isin(["storage_jar", "jar_other"])
        contrast = "jar (any) vs non-jar"
    f = u["signs"].map(lambda s: _has(s, JAR))
    a, n1 = int((f & tgt).sum()), int(tgt.sum())
    b, n2 = int((f & ~tgt).sum()), int((~tgt).sum())
    rr = (a / max(n1, 1)) / max(b / max(n2, 1), 1e-9)
    p = fisher_exact([[a, n1 - a], [b, n2 - b]], alternative="greater")[1] if n1 and n2 else 1.0
    elig = (a + b) >= max(5, MIN_N.get("C5_jar", 5)) and len(u) >= MIN_N.get("C5", 0)
    if not elig:
        v = "UNTESTABLE"
    elif rr < 1.5:
        v = "PASS (not a self-label)"
    elif rr >= 2 and p < 0.05:
        v = "FAIL (jar sign concentrated on jars)"
    else:
        v = "INCONCLUSIVE"
    return dict(contrast=contrast, n=len(u), a=a, n_target=n1, b=b, n_other=n2, RR=rr, p=float(p),
                eligible=elig, verdict=v)


def harappa_seals():
    from corpus.load import icit_texts
    seen, out = set(), []
    for r in icit_texts():
        if r["site"] == "Harappa" and r["type"].startswith("SEAL"):
            k = " ".join(r["seq"])
            if k not in seen:
                seen.add(k)
                out.append([s for s in r["seq"] if s != "|"])
    return out


def icit_harappa_pottery():
    from corpus.load import icit_texts
    rows = [r for r in icit_texts() if r["site"] == "Harappa" and r["type"].startswith(("POT", "POsT"))]
    cisi = {r["cisi"] for r in rows if r["cisi"] != "-"}
    nocisi = {}
    for r in rows:
        if r["cisi"] == "-":
            k = " ".join(s for s in r["seq"] if s != "|")
            nocisi[k] = nocisi.get(k, 0) + 1
    return cisi, nocisi


def len_stratum(signs):
    n = sum(1 for s in signs if s != "#")
    return ("1-5" if n <= 5 else "6+") + ("|broken" if "#" in signs else "|complete")


def new_sherds(df, icit_pot=None):
    """sherd rows not already in ICIT: drop rows whose CISI id is an ICIT Harappa pottery id, and,
    among rows without such an id, drop up to c rows per text where c = number of ICIT Harappa
    pottery records without a CISI number carrying that exact text (first rows in sheet order)."""
    cisi, nocisi = icit_pot or icit_harappa_pottery()
    d = df[(df["object_type"] == "POT") & df["signs"].notna()].copy()
    d = d[d["readable_n"] > 0]
    linked = d["icit_cisi"].isin(cisi)
    d = d[~linked]
    left = dict(nocisi)
    keep = []
    for sg in d["signs"]:
        k = " ".join(sg)
        if left.get(k, 0) > 0:
            left[k] -= 1
            keep.append(False)
        else:
            keep.append(True)
    return d[np.array(keep, bool)], int(linked.sum())


def test_C6(df, seals=None, icit_pot=None, require_ids=True, **_):
    """jar sign M342 enriched on new Harappa pottery vs Harappa seals, length-stratified
    (m342_offsite, on sherds not in ICIT)."""
    seals = seals if seals is not None else harappa_seals()
    cisi_ids = (icit_pot or icit_harappa_pottery())[0]
    d, n_linked = new_sherds(df, icit_pot)
    d = d.copy()
    d["seqs"] = d["signs"].map(" ".join)
    lot = d["lot_key"].astype(object)
    d["lotu"] = np.where(lot.isna(), "NA|" + d["period"].astype(str), lot.astype(str))
    d = d.drop_duplicates(["lotu", "seqs"])
    pot = list(d["signs"])
    st = {}
    for sg in seals:
        k = len_stratum(sg)
        c = st.setdefault(k, [0, 0, 0, 0])
        c[0] += 1
        c[1] += _has(sg, JAR)
    for sg in pot:
        k = len_stratum(sg)
        c = st.setdefault(k, [0, 0, 0, 0])
        c[2] += 1
        c[3] += _has(sg, JAR)
    strata = [(s0 + p0, s1 + p1, p0, p1) for s0, s1, p0, p1 in st.values()]
    A, E_perm, pu, _ = strat_hyper(strata)
    # effect: observed / expected from the seal rate of each length stratum (as m342_offsite)
    E = sum(p0 * s1 / s0 for s0, s1, p0, p1 in st.values() if s0 > 0)
    R = A / E if E > 0 else float("nan")
    has_ids = bool(n_linked > 0) or bool(df["icit_cisi"].isin(cisi_ids).any())
    return dict(n_pot=len(pot), n_seal=len(seals), n_linked_dropped=n_linked, O=A, E=E, E_perm=E_perm, R=R, p=pu,
                id_linking=has_ids, eligible=len(pot) >= MIN_N.get("C6", 0) and (has_ids or not require_ids),
                pass_effect=R >= 1.25, kill=R < 1.25)   # m342_offsite detection bar


def load_tablets():
    t = pd.read_csv(ROOT / "experiments/tablet_archives/tablets.csv", dtype={"cisi": str})
    return t[t["tier"].notna()].copy()


def _tab_join(df, tabs):
    s = df[df["icit_cisi"].notna()].drop_duplicates("icit_cisi").set_index("icit_cisi")
    t = tabs.copy()
    t["lot_key"] = t["cisi"].map(s["lot_key"]) if len(s) else None
    t["mass_g"] = t["cisi"].map(s["mass_g"]) if len(s) else np.nan
    per = t["cisi"].map(s["period"]) if len(s) else pd.Series("NA", index=t.index)
    per = per.fillna("NA")
    t["stratum"] = t["type"].astype(str) + "|" + np.where(per != "NA", per, t["period_key"].fillna("NA").astype(str))
    t["unit"] = np.where(t["copy_group"].notna(), t["copy_group"].astype(str), "oid" + t["oid"].astype(str))
    return t


def test_C7(df, tabs=None, n_perm=2000, rng=None, **_):
    """docket tier (2/3/4 tall strokes + M328) x HARP lot (tablet_archives T1 at true lot level)."""
    rng = rng or np.random.default_rng(SEED)
    t = _tab_join(df, tabs if tabs is not None else load_tablets())
    t = t[t["lot_key"].notna()].drop_duplicates(["unit", "lot_key"])
    sz = t["lot_key"].value_counts()
    t = t[t["lot_key"].isin(sz[sz >= 3].index)].reset_index(drop=True)
    if t["lot_key"].nunique() < 2:
        return dict(n_units=len(t), n_lots=0, p=1.0, eligible=False, pass_effect=False, kill=False)
    lots = {l: i for i, l in enumerate(sorted(t["lot_key"].unique()))}
    rows = t["lot_key"].map(lots).to_numpy()
    tier = (t["tier"].astype(int) - 2).to_numpy()
    strata = _strata_groups(t["stratum"].to_numpy())
    obs = g_table(rows, tier, len(lots), 3)
    null = np.array([g_table(rows, tier[_perm_index(strata, rng)], len(lots), 3) for _ in range(n_perm)])
    p = (1 + np.sum(null >= obs - 1e-9)) / (1 + n_perm)
    return dict(n_units=len(t), n_lots=len(lots), G=float(obs), G_null=float(null.mean()), p=float(p),
                eligible=len(t) >= MIN_N.get("C7", 0), pass_effect=True, kill=False)


def test_C9(df, n_perm=2000, rng=None, **_):
    """numeral value V on a sherd vs vessel rim diameter, within form x period (magnitude T2)."""
    rng = rng or np.random.default_rng(SEED)
    d = df[(df["object_type"] == "POT") & df["signs"].notna() & df["rim_diam_mm"].notna()].copy()
    d = d[d["readable_n"] > 0]
    if len(d) < 3:
        return dict(n=len(d), p=1.0, eligible=False, pass_effect=False, kill=False)
    from experiments.harp_pack.loader import numeral_value
    d["seqs"] = d["signs"].map(" ".join)
    lot = d["lot_key"].astype(object)
    d["lotu"] = np.where(lot.isna(), "NA|" + d["period"].astype(str), lot.astype(str))
    d = d.groupby(["lotu", "seqs"], as_index=False).agg(
        signs=("signs", "first"), rim=("rim_diam_mm", "median"),
        form=("vessel_form", "first"), period=("period", "first"))
    v = d["signs"].map(numeral_value).to_numpy()
    rho, p = strat_spearman(v, d["rim"].to_numpy(), (d["form"] + "|" + d["period"]).to_numpy(), n_perm, rng)
    return dict(n=len(d), n_V_pos=int((v > 0).sum()), rho=rho, p=p,
                eligible=len(d) >= MIN_N.get("C9", 0) and (v > 0).sum() >= 8,
                pass_effect=True, kill=False)


TESTS = {"C1": test_C1, "C2": test_C2, "C3": test_C3, "C4": test_C4, "C6": test_C6,
         "C7": test_C7, "C9": test_C9}


def verdicts(res):
    """Holm over eligible kept tests; frozen verdict rules (prereg table)."""
    ps = {k: r["p"] for k, r in res.items() if r.get("eligible")}
    adj = holm(ps) if ps else {}
    for k, r in res.items():
        if not r.get("eligible"):
            r["verdict"] = "UNTESTABLE (below frozen minimum n or missing column)"
            continue
        r["p_holm"] = adj[k]
        if adj[k] < FAMILY_ALPHA and r["pass_effect"]:
            r["verdict"] = "PASS"
        elif r.get("kill") or adj[k] >= FAMILY_ALPHA:
            r["verdict"] = "FAIL"
        else:
            r["verdict"] = "INCONCLUSIVE"
    return res


def run_all(df, n_perm=2000, seals=None, tabs=None, icit_pot=None):
    rng = np.random.default_rng(SEED)
    res = {k: TESTS[k](df, n_perm=n_perm, rng=rng, seals=seals, tabs=tabs, icit_pot=icit_pot)
           for k in KEPT if k in TESTS}
    res = verdicts(res)
    res["C5"] = test_C5(df)
    res["DROPPED"] = DROPPED
    return res


if __name__ == "__main__":
    from experiments.harp_pack.loader import load
    df, rep = load(sys.argv[1])
    print(json.dumps({"loader_report": rep}, indent=1, default=str))
    print(json.dumps(run_all(df), indent=1, default=str))
