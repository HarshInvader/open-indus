"""Revision report: reads draws_<job>.jsonl written by rev.py and applies the pre-registered rules in
docs/prereg/uniformity_paper_revision.md. Writes results.json and table.md. No thresholds are set here that are
not in the prereg."""
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MARGIN = 0.05
PS_BAR = 0.80
MD, HA, CD = "Mohenjo-daro", "Harappa", "Chanhu-daro"
S2 = json.load(open(ROOT / "experiments/uniformity_paper/step2/results.json"))
IFAMS = ("m77_seal", "icit_seal", "icit_sealtype")
RATES = (0.0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
FORMS = ("sign", "spelt", "ur3emp")


def load(job):
    p = HERE / f"draws_{job}.jsonl"
    by = {}
    if p.exists():
        for l in open(p):
            r = json.loads(l)
            by.setdefault(r["cond"], []).append(r)
    return by


def med(x):
    return float(np.median(x)) if len(x) else None


def pct(x, qs=(2.5, 5, 50, 95, 97.5)):
    x = np.asarray(x, float)
    return {str(q): float(np.percentile(x, q)) for q in qs}


def s2_part2(fam, a, b):
    for r in S2["part2"]:
        if r["family"] == fam and {r["a"], r["b"]} == {a, b}:
            return r


def s2_within(fam):
    r = s2_part2(fam, MD, HA)
    return r["within"]


# =========================================================================== R1
def r1():
    by = load("boot")
    out = {}
    for cond, rs in by.items():
        df, dn, dc = [], [], []
        for r in rs:
            if not r["b"] or not r["w"]:
                continue
            b, w, nu = med(r["b"]), med(r["w"]), med(r["bnull"])
            df.append(b - w); dn.append(b - nu); dc.append(b - max(w, nu))
        if not df:
            out[cond] = dict(failed=True); continue
        kind = "indus" if cond.startswith(("MDHA", "UNI")) else "ref" if cond.startswith("REF") else "cd"
        row = dict(kind=kind, n_side=rs[0]["n"], reps=len(df), d_floor=pct(df), d_null=pct(dn), d_cons=pct(dc))
        for key, d in (("floor", df), ("null", dn), ("cons", dc)):
            q05, q95 = np.percentile(d, 5), np.percentile(d, 95)
            row[f"tost_{key}"] = bool(q05 > -MARGIN and q95 < MARGIN)
            row[f"m_star_{key}"] = float(max(abs(q05), abs(q95)))
            row[f"above_{key}"] = bool(q05 >= MARGIN)
        out[cond] = row
    return out


# =========================================================================== R2
def r80_of(det):
    """First crossing of 0.80 on the rate grid, linear interpolation; None if never reached."""
    prev_r, prev_p = None, None
    for r, p in zip(RATES, det):
        if p >= 0.80:
            if prev_r is None:
                return r
            return prev_r + (0.80 - prev_p) / (p - prev_p) * (r - prev_r) if p != prev_p else r
        prev_r, prev_p = r, p
    return None


def first_at(seq, bar):
    for r, p in zip(RATES, seq):
        if p >= bar:
            return r
    return None


def r2():
    by = load("names")
    out = {}
    for fam in IFAMS:
        rs = [r for r in by.get(fam, []) if r["w"]]
        if not rs:
            continue
        obs = s2_part2(fam, MD, HA)["delta"]
        D = {}  # form -> reps x rates array of Δ
        for form in FORMS:
            M = []
            for r in rs:
                w = med(r["w"])
                row = []
                for rate in RATES:
                    key = "0.0" if rate == 0.0 else f"{form}|{rate}"
                    v = r["b"].get(key, [])
                    row.append(med(v) - w if v else np.nan)
                M.append(row)
            D[form] = np.array(M)
        fo = {}
        rng = np.random.default_rng(7)
        for form, M in D.items():
            det = np.nanmean(M >= MARGIN, 0).tolist()
            exc = np.nanmean(M > obs, 0).tolist()
            r80, r95 = r80_of(det), first_at(exc, 0.95)
            boots80, boots95 = [], []
            for _ in range(1000):
                Mb = M[rng.integers(len(M), size=len(M))]
                x = r80_of(np.nanmean(Mb >= MARGIN, 0)); boots80.append(np.inf if x is None else x)
                y = first_at(np.nanmean(Mb > obs, 0), 0.95); boots95.append(np.inf if y is None else y)
            ci = lambda b: [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
            fo[form] = dict(detect=dict(zip(map(str, RATES), det)), exceed_obs=dict(zip(map(str, RATES), exc)),
                            median_delta=dict(zip(map(str, RATES), np.nanmedian(M, 0).tolist())),
                            r80=r80, r80_ci=ci(boots80), r95_excluded=r95, r95_ci=ci(boots95))
        out[fam] = dict(reps=len(rs), n_side=rs[0]["n"], observed_delta=obs, forms=fo)
    return out


def diffuse():
    by = load("diffuse")
    out = {}
    for cond, rs in by.items():
        fam, kind, v = cond.split("|")
        w = s2_within(fam)
        a = np.array([r["auc"] for r in rs])
        out[cond] = dict(family=fam, kind=kind, level=float(v), draws=len(a), median_auc=med(a),
                         power=float(np.mean(a - w >= MARGIN)), share=float(np.mean([r["share"] for r in rs])))
    return out


# =========================================================================== generic trios
def summ(by, name):
    rs = [r for r in by.get(name, []) if r.get("auc") is not None]
    if not rs:
        return None
    a = np.array([r["auc"] for r in rs]); nu = np.array([r["null"] for r in rs])
    d = dict(n=rs[0]["n"], draws=len(a), median=med(a), null_med=med(nu), null_q95=float(np.quantile(nu, 0.95)), _a=a)
    if "jsd" in rs[0]:
        d.update(_j=np.array([r["jsd"] for r in rs]), jsd_med=med([r["jsd"] for r in rs]),
                 jsd_p_med=med([r["jsd_p"] for r in rs]))
    return d


def trio(by, key, bpre="B_", wpre="W_", gpre="G_"):
    B, W, G = summ(by, bpre + key), summ(by, wpre + key), summ(by, gpre + key)
    if not B or not W:
        return dict(key=key, failed=True, n=(B or W or {}).get("n"))
    thr = max(0.65, B["null_q95"])
    gate = float(np.mean(G["_a"] >= thr)) if G else None
    return dict(key=key, n=B["n"], b=B["median"], w=W["median"], delta=B["median"] - W["median"],
                d_null=B["median"] - B["null_med"],
                p_floor=float((1 + np.sum(W["_a"] >= B["median"])) / (1 + len(W["_a"]))),
                gate=gate, gate_pass=bool(gate is not None and gate >= 0.8))


def family(rows):
    gated = [r for r in rows if r.get("gate_pass") and r.get("delta") is not None]
    if not gated:
        v = "underpowered"
    else:
        v = "above floor" if min(r["delta"] for r in gated) >= MARGIN else "not above floor"
    ds = [r["delta"] for r in gated]
    return dict(verdict=v, min_delta=min(ds, default=None), max_delta=max(ds, default=None),
                gated=[r["split"] for r in gated], rows=rows)


def roles():
    by = load("roles")
    out = {}
    from rev import ROLE_VARIANTS, BM_VARIANTS  # noqa: E402
    for corp, sps, vs in (("ur3", ("U_reign", "U_coll", "G_reign", "G_coll"), ROLE_VARIANTS),
                          ("cdli", ("U_reign", "G_reign"), ROLE_VARIANTS),
                          ("bm", ("U_reign", "U_coll", "G_reign", "G_coll"), BM_VARIANTS)):
        for v in vs:
            rows = [dict(trio(by, f"{corp}_{v}_{sp}"), split=sp) for sp in sps]
            out[f"{corp}|{v}"] = family(rows)
    return out


def latin():
    by = load("latin")
    out = {}
    for cls in ("MIL", "STAMP", "GRAF", "REST"):
        rows = [dict(trio(by, f"lat_{cls}_{sp}"), split=sp) for sp in ("ge_rlp_vs_bwhe", "br_north_vs_south")]
        out[cls] = family(rows)
    return out


def alt():
    by = load("alt")
    out = {}
    for fam in IFAMS:
        B, W, P = summ(by, f"AB_{fam}"), summ(by, f"AW_{fam}"), summ(by, f"AP_{fam}")
        if not (B and W and P):
            continue
        d = B["median"] - W["median"]
        pf = float((1 + np.sum(W["_a"] >= B["median"])) / (1 + len(W["_a"])))
        pw = float(np.mean(P["_a"] - W["median"] >= MARGIN))
        if pw < 0.8:
            v = "underpowered"
        elif d >= MARGIN and pf <= 0.10:
            v = "differs"
        elif d < MARGIN and pf > 0.10:
            v = "same"
        else:
            v = "inconclusive"
        ps = float(np.mean(B["_j"][:, None] > W["_j"][None, :]))
        jpow = float(np.mean(P["_j"] > np.quantile(W["_j"], 0.95)))
        jv = "underpowered" if jpow < 0.8 else ("between > floor" if ps >= PS_BAR else "not above floor")
        nb = s2_part2(fam, MD, HA)["verdict"]
        out[f"indus|{fam}"] = dict(n=B["n"], lr_b=B["median"], lr_w=W["median"], lr_delta=d, lr_p_floor=pf, lr_power=pw,
                                   lr_verdict=v, jsd_b=B["jsd_med"], jsd_w=W["jsd_med"], jsd_ps=ps, jsd_p_b=B["jsd_p_med"],
                                   jsd_power=jpow, jsd_verdict=jv, nb_verdict=nb,
                                   agree=bool((v == "same") == (nb == "same") and (jv != "between > floor") == (nb == "same")))
    S2F = S2["part1_families"]["whole"]
    for corp, sps in (("ur3", ("U_reign", "U_coll", "G_reign", "G_coll")), ("cdli", ("U_reign", "G_reign")),
                      ("lat", ("ge_rlp_vs_bwhe", "br_north_vs_south"))):
        rows, jrows = [], []
        for sp in sps:
            t = trio(by, f"{corp}_{sp}", "AB_", "AW_", "AG_")
            t["split"] = sp
            rows.append(t)
            B, W = summ(by, f"AB_{corp}_{sp}"), summ(by, f"AW_{corp}_{sp}")
            if B and W:
                jrows.append(dict(split=sp, jsd_b=B["jsd_med"], jsd_w=W["jsd_med"],
                                  ps=float(np.mean(B["_j"][:, None] > W["_j"][None, :])), jsd_p_b=B["jsd_p_med"]))
        fv = family(rows)
        jv = "between > floor" if jrows and min(r["ps"] for r in jrows) >= PS_BAR else "not above floor"
        out[f"ref|{corp}"] = dict(lr=fv, jsd=jrows, jsd_verdict=jv, nb_verdict=S2F[corp]["verdict"],
                                  agree=bool(fv["verdict"] == S2F[corp]["verdict"] and
                                             (jv == "between > floor") == (S2F[corp]["verdict"] == "above floor")))
    return out


def m93():
    by = load("m93")
    from rev import M93_VARIANTS  # noqa: E402
    out = {}
    for big in (HA, MD):
        W = summ(by, f"MW_{big}")
        rows = {}
        for v in M93_VARIANTS:
            B = summ(by, f"MB_{big}_{v}")
            if not (B and W):
                continue
            rows[v] = dict(n=B["n"], b=B["median"], w=W["median"], null=B["null_med"], d_floor=B["median"] - W["median"],
                           d_cons=B["median"] - max(W["median"], B["null_med"]),
                           p_floor=float((1 + np.sum(W["_a"] >= B["median"])) / (1 + len(W["_a"]))))
        out[big] = rows
    verdict = {}
    for v in M93_VARIANTS:
        if v == "base" or not all(v in out[b] and "base" in out[b] for b in (HA, MD)):
            continue
        rm = all(out[b][v]["d_cons"] < MARGIN for b in (HA, MD))
        part = all(out[b]["base"]["d_cons"] - out[b][v]["d_cons"] >= out[b]["base"]["d_cons"] / 2 for b in (HA, MD))
        verdict[v] = "removes" if rm else "partly" if part else "does not remove"
    return dict(pairs=out, verdict=verdict)


def unicorn():
    by = load("unicorn")
    out = {}
    for fam in ("icit_seal", "icit_sealtype"):
        B, W = summ(by, f"UB_{fam}"), summ(by, f"UW_{fam}")
        if not (B and W):
            continue
        pw = {}
        for q in (0.10, 0.15, 0.20):
            P = summ(by, f"UP{q}_{fam}")
            pw[str(q)] = float(np.mean(P["_a"] - W["median"] >= MARGIN)) if P else None
        d = B["median"] - W["median"]
        pf = float((1 + np.sum(W["_a"] >= B["median"])) / (1 + len(W["_a"])))
        gp = pw["0.15"] is not None and pw["0.15"] >= 0.8
        v = ("differs" if d >= MARGIN and pf <= 0.10 and gp else "same" if d < MARGIN and gp
             else "differs (gate fails)" if d >= MARGIN and pf <= 0.10 else "underpowered")
        out[fam] = dict(n=B["n"], b=B["median"], w=W["median"], delta=d, d_null=B["median"] - B["null_med"],
                        p_floor=pf, power=pw, verdict=v)
    return out


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def main():
    R = dict(boot=r1(), names=r2(), diffuse=diffuse(), roles=roles(), latin=latin(), alt=alt(), m93=m93(), unicorn=unicorn())
    R = clean(R)
    json.dump(R, open(HERE / "results.json", "w"), indent=1)
    print(json.dumps(R, indent=1)[:200])


if __name__ == "__main__":
    main()
