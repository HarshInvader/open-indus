"""T5: confirmatory statistics that combine dev-frozen choices with held-out data.
Run AFTER t2_status.py heldout and t3_emblem.py heldout. Reads t2_dev.json / t2_heldout.json.
  H3  dev-selected size signs (dev p < 0.01) replicate: S = sum_k sign(dev delta_k) * z_heldout_k / sqrt(K),
      permutation null (residuals permuted within strata), one-sided; plus per-sign one-sided Holm.
  H3f F12 reference: W741 (M343) smaller, one-sided.
  H5  ladder score vs residual area: held-out Spearman in the dev direction (negative), one-sided.
  H6b frame-feature count lower on other-animal than unicorn seals, one-sided.
  H8  emblem as status: 'none' seals smaller and zebu seals larger (one-sided each, Holm over 2).
  S1  sensitivity: H3 with glyph-footprint strata in place of length strata.
  S2  metric-measured sites only (not Mohenjo-daro/Harappa; STATE F36), dev+held-out, exploratory.
Usage: t5_confirm.py heldout
"""
import json, math, sys
import numpy as np
from scipy.stats import rankdata
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import seal_table, strata, resid_by_strata, FRAME, HERE, footprint
from t2_status import perm_within

N = 10000
rng = np.random.default_rng(77)
dev = json.load(open(HERE / "t2_dev.json"))
SEL = sorted(f for f, v in dev["features"].items() if v["p"] < 0.01)
SGN = {f: np.sign(dev["features"][f]["delta_log"]) for f in SEL}


def size_rows(split):
    return [r for r in seal_table(split) if r["log_area"] is not None]


def h3(rows, st, label):
    y = np.array([r["log_area"] for r in rows])
    res = np.array(resid_by_strata(list(y), st))
    X = {f: np.array([f in r["feats"] for r in rows]) for f in SEL}
    perms = [perm_within(st, rng) for _ in range(N)]
    def deltas(rv):
        return {f: rv[x].mean() - rv[~x].mean() if x.sum() else 0.0 for f, x in X.items()}
    obs = deltas(res)
    nulls = [deltas(res[p]) for p in perms]
    se = {f: np.std([n[f] for n in nulls]) for f in SEL}
    S = sum(SGN[f] * obs[f] / se[f] for f in SEL) / math.sqrt(len(SEL))
    Sn = np.array([sum(SGN[f] * n[f] / se[f] for f in SEL) / math.sqrt(len(SEL)) for n in nulls])
    per = {}
    for f in SEL:
        nd = np.array([n[f] for n in nulls])
        p1 = (1 + (SGN[f] * nd >= SGN[f] * obs[f]).sum()) / (1 + N)
        per[f] = dict(n=int(X[f].sum()), dev_pct=dev["features"][f]["pct"], pct=100 * (math.exp(obs[f]) - 1),
                      z=float(obs[f] / se[f]), p_one=float(p1))
    # Holm
    ps = sorted(per.items(), key=lambda kv: kv[1]["p_one"])
    m = len(ps)
    running = 0
    for i, (f, v) in enumerate(ps):
        running = max(running, min(1, (m - i) * v["p_one"]))
        per[f]["p_holm"] = float(running)
    return dict(label=label, selected=SEL, S=float(S), p=float((1 + (Sn >= S).sum()) / (1 + N)), per_sign=per)


def one_sided_feature(rows, st, f, direction):
    y = np.array([r["log_area"] for r in rows]); res = np.array(resid_by_strata(list(y), st))
    x = np.array([f(r) for r in rows])
    d = res[x].mean() - res[~x].mean()
    nd = np.array([res[p][x].mean() - res[p][~x].mean() for p in (perm_within(st, rng) for _ in range(N))])
    return dict(n=int(x.sum()), pct=100 * (math.exp(d) - 1),
                p_one=float((1 + (direction * nd >= direction * d).sum()) / (1 + N)),
                mde_pct=100 * (math.exp(2.5 * nd.std()) - 1))


def main():
    out = {}
    rows = size_rows("heldout")
    st = strata(rows)
    out["H3"] = h3(rows, st, "site x length x lines strata")
    out["H3f_W741"] = one_sided_feature(rows, st, lambda r: "MJ_W741" in r["feats"], -1)
    # H5 ladder (one-sided negative)
    lad = json.load(open(HERE / "t1_dev.json"))["ICIT"]["order"]
    pos = {f: i / (len(lad) - 1) for i, f in enumerate(lad)}
    keep = [i for i, r in enumerate(rows) if r["feats"] & set(pos)]
    R = [rows[i] for i in keep]; stR = [st[i] for i in keep]
    y = np.array([r["log_area"] for r in R]); res = rankdata(resid_by_strata(list(y), stR))
    sc = rankdata([np.mean([pos[f] for f in r["feats"] if f in pos]) for r in R])
    def corr(a, b):
        a = a - a.mean(); b = b - b.mean(); return float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))
    obs = corr(res, sc); nl = np.array([corr(res[perm_within(stR, rng)], sc) for _ in range(N)])
    out["H5_ladder"] = dict(n=len(R), spearman=obs, p_one_negative=float((1 + (nl <= obs).sum()) / (1 + N)),
                            mde_rho=float(2.5 * nl.std()))
    # H6b frame count by emblem
    E = [r for r in seal_table("heldout") if r["emblem"] not in ("unknown", "none", "other")]
    stE = strata(E)
    cnt = np.array(resid_by_strata([float(len(r["feats"])) for r in E], stE))
    u = np.array([r["emblem"] == "unicorn" for r in E])
    d = cnt[~u].mean() - cnt[u].mean()
    nd = []
    for _ in range(N):
        p = perm_within(stE, rng); uu = u[p]; nd.append(cnt[~uu].mean() - cnt[uu].mean())
    nd = np.array(nd)
    out["H6b_framecount"] = dict(n_unicorn=int(u.sum()), n_other=int((~u).sum()), delta=float(d),
                                 p_one_negative=float((1 + (nd <= d).sum()) / (1 + N)), mde=float(2.5 * nd.std()))
    # H8 emblem -> size
    a = one_sided_feature(rows, st, lambda r: r["emblem"] == "none", -1)
    b = one_sided_feature(rows, st, lambda r: r["emblem"] == "zebu", +1)
    ps = sorted([("none_smaller", a), ("zebu_larger", b)], key=lambda kv: kv[1]["p_one"])
    ps[0][1]["p_holm"] = min(1, 2 * ps[0][1]["p_one"]); ps[1][1]["p_holm"] = max(ps[0][1]["p_holm"], ps[1][1]["p_one"])
    out["H8_emblem_size"] = dict(ps)
    # S1 footprint strata
    fp = [footprint(r["signs"]) for r in rows]
    st_fp = [(r["site"], min(int(f / 0.6), 7), min(r["n_lines"], 2)) for r, f in zip(rows, fp)]
    out["S1_footprint"] = h3(rows, st_fp, "site x glyph-footprint bin x lines strata")
    # S2 metric sites (dev + held-out pooled; exploratory)
    allr = size_rows("all")
    met = [r for r in allr if r["site"] not in ("Mohenjo-daro", "Harappa")]
    stm = strata(met)
    s2 = {}
    for f in SEL + ["MJ_W741"]:
        x = sum(f in r["feats"] for r in met)
        if x >= 3:
            s2[f] = one_sided_feature(met, stm, lambda r, f=f: f in r["feats"], SGN.get(f, -1))
    out["S2_metric_sites"] = dict(n=len(met), per_sign=s2)
    json.dump(out, open(HERE / "t5_heldout.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
