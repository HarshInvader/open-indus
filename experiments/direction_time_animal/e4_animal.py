"""E4: do text-only seals carry an extra sign class / longer text vs iconic seals, matched on area and period?
Run: .venv/bin/python experiments/direction_time_animal/e4_animal.py [--smoke]
--smoke: group labels shuffled, few iterations (code check only)."""
import json, sys, warnings
from collections import Counter, defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from dta_lib import OUT, icit_texts, signs, to_m, binary_period, lexicon_roles, ROLES, area, site_group

warnings.filterwarnings("ignore")
SMOKE = "--smoke" in sys.argv
rng = np.random.default_rng(20261116)
ROLE = lexicon_roles()


def load():
    seen, U = set(), []
    for t in icit_texts():
        if t["type"] not in ("SEAL:S", "SEAL:R", "SEAL") or area(t) <= 0 or "#" in t["seq"]:
            continue
        sym = t["symbol"].strip()
        if sym == "-":
            continue
        g = 1 if sym == "None" else 0
        sg = [to_m(x) for x in signs(t["seq"])]
        if not sg:
            continue
        key = (g, tuple(sg))
        if key in seen:
            continue
        seen.add(key)
        bp = binary_period(t)
        U.append(dict(g=g, sg=sg, site=site_group(t["site"]), per=("u" if bp is None else str(bp[1])),
                      area=area(t), type=t["type"]))
    return U


def assign_strata(U, edges, with_len):
    for u in U:
        ab = int(np.searchsorted(edges, u["area"], side="right"))
        L = min(len(u["sg"]), 6) if len(u["sg"]) >= 2 else 1
        u["s0"] = f"{u['site']}|{u['per']}|a{ab}"
        u["s1"] = u["s0"] + (f"|L{L}" if with_len else "")
    return U


def usable(U, key):
    c = defaultdict(set)
    for u in U: c[u[key]].add(u["g"])
    return [u for u in U if len(c[u[key]]) == 2]


def perm_labels(U, key):
    by = defaultdict(list)
    for i, u in enumerate(U): by[u[key]].append(i)
    g = np.array([u["g"] for u in U])
    for idx in by.values():
        g[idx] = rng.permutation(g[idx])
    return g


def strat_diff(U, key, val, g):
    """Stratified (harmonic-mean weighted) difference text-only minus iconic in per-text value val (array)."""
    by = defaultdict(list)
    for i, u in enumerate(U): by[u[key]].append(i)
    num = den = 0.0
    for idx in by.values():
        idx = np.array(idx); a = idx[g[idx] == 1]; b = idx[g[idx] == 0]
        if len(a) == 0 or len(b) == 0: continue
        w = len(a) * len(b) / (len(a) + len(b))
        num += w * (val[a].mean() - val[b].mean()); den += w
    return num / den


def role_matrix(U):
    M = np.zeros((len(U), len(ROLES)))
    for i, u in enumerate(U):
        for x in u["sg"]:
            M[i, ROLES.index(ROLE.get(x, "UNK"))] += 1
    return M


def role_share_diffs(U, key, M, g):
    """Token-share difference per role, stratified: per stratum share = sum tokens role / sum tokens."""
    by = defaultdict(list)
    for i, u in enumerate(U): by[u[key]].append(i)
    num = np.zeros(M.shape[1]); den = 0.0
    for idx in by.values():
        idx = np.array(idx); a = idx[g[idx] == 1]; b = idx[g[idx] == 0]
        if len(a) == 0 or len(b) == 0: continue
        w = len(a) * len(b) / (len(a) + len(b))
        sa = M[a].sum(0) / M[a].sum(); sb = M[b].sum(0) / M[b].sum()
        num += w * (sa - sb); den += w
    return num / den


def O2(U, nperm):
    M = role_matrix(U); g0 = np.array([u["g"] for u in U])
    obs = role_share_diffs(U, "s1", M, g0)
    null = np.array([role_share_diffs(U, "s1", M, perm_labels(U, "s1")) for _ in range(nperm)])
    sd = null.std(0); sd[sd == 0] = np.inf
    z = obs / sd; T = float((z ** 2).sum())
    Tn = ((null / sd) ** 2).sum(1)
    return dict(T=T, p=float((1 + (Tn >= T).sum()) / (1 + nperm)), diff={r: float(d) for r, d in zip(ROLES, obs)},
                z={r: float(v) for r, v in zip(ROLES, z)})


def featurize(U, vocab):
    vi = {x: i for i, x in enumerate(vocab)}
    X = np.zeros((len(U), len(vocab)))
    for i, u in enumerate(U):
        for x in u["sg"]:
            if x in vi: X[i, vi[x]] += 1
    return X


def auc_folds(U, X, g):
    md = np.array([u["site"] == "MD" for u in U])
    aucs = []
    for tr in (md, ~md):
        te = ~tr
        if len(set(g[tr])) < 2 or len(set(g[te])) < 2: continue
        clf = LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced").fit(X[tr], g[tr])
        aucs.append(roc_auc_score(g[te], clf.decision_function(X[te])))
    return float(np.mean(aucs))


def O3(U, nperm):
    vocab = sorted({x for u in U for x in u["sg"]})
    X = featurize(U, vocab); g0 = np.array([u["g"] for u in U])
    obs = auc_folds(U, X, g0)
    null = np.array([auc_folds(U, X, perm_labels(U, "s1")) for _ in range(nperm)])
    return dict(auc=obs, null_mean=float(null.mean()), null_95=float(np.percentile(null, 95)),
                p=float((1 + (null >= obs).sum()) / (1 + nperm)))


def O1(U, nperm):
    L = np.array([len(u["sg"]) for u in U], float); g0 = np.array([u["g"] for u in U])
    obs = strat_diff(U, "s0", L, g0)
    null = np.array([strat_diff(U, "s0", L, perm_labels(U, "s0")) for _ in range(nperm)])
    return dict(diff_signs=float(obs), p_two_sided=float((1 + (np.abs(null) >= abs(obs)).sum()) / (1 + nperm)),
                mean_len_textonly=float(L[g0 == 1].mean()), mean_len_iconic=float(L[g0 == 0].mean()))


def plant(U, kind, frac=0.10):
    V = [dict(u, sg=list(u["sg"])) for u in U]
    openers = Counter(x for u in V if u["g"] == 0 for x in u["sg"] if ROLE.get(x) == "OPENER")
    ops, w = zip(*openers.items()); w = np.array(w, float) / sum(w)
    idx = [i for i, u in enumerate(V) if u["g"] == 1]
    for i in rng.choice(idx, size=int(round(frac * len(idx))), replace=False):
        if kind == "a":
            V[i]["sg"] = [str(rng.choice(ops, p=w))] + V[i]["sg"]
        else:
            V[i]["sg"] = V[i]["sg"] + ["PLANT_CLOSER"]
    return V


def prepare(U, edges):
    U = assign_strata([dict(u) for u in U], edges, with_len=True)
    return usable(U, "s1")


def main():
    U = load()
    if SMOKE:
        g = [u["g"] for u in U]; rng.shuffle(g)
        for u, x in zip(U, g): u["g"] = x
    NP1, NP2, NP3, NPL, NP2p, NP3p = (50, 50, 10, 3, 50, 10) if SMOKE else (2000, 2000, 200, 100, 500, 100)
    n_text_only = sum(u["g"] for u in U)
    edges = np.quantile([u["area"] for u in U if u["g"] == 1], [0.2, 0.4, 0.6, 0.8])
    res = dict(gate=dict(text_only_with_area=n_text_only, threshold=100, gate_pass=n_text_only >= 100),
               n_iconic=len(U) - n_text_only, area_edges=edges.tolist(),
               text_only_by_type=dict(Counter(u["type"] for u in U if u["g"] == 1)),
               text_only_by_site=dict(Counter(u["site"] for u in U if u["g"] == 1)))
    U0 = usable(assign_strata([dict(u) for u in U], edges, with_len=False), "s0")
    res["O1_n"] = dict(text_only=sum(u["g"] for u in U0), iconic=sum(1 - u["g"] for u in U0))
    res["O1"] = O1(U0, NP1)
    U1 = prepare(U, edges)
    res["O2_O3_n"] = dict(text_only=sum(u["g"] for u in U1), iconic=sum(1 - u["g"] for u in U1),
                          strata=len({u["s1"] for u in U1}))
    res["O2"] = O2(U1, NP2)
    res["O3"] = O3(U1, NP3)
    ps = sorted([("O2", res["O2"]["p"]), ("O3", res["O3"]["p"])], key=lambda x: x[1])
    holm = {ps[0][0]: min(1, 2 * ps[0][1]), ps[1][0]: min(1, max(2 * ps[0][1], ps[1][1]))}
    res["holm"] = holm
    print(json.dumps(res, indent=1), flush=True)
    # planted power
    res["power"] = {}
    for kind in ("a", "b"):
        h2 = h3 = 0
        for _ in range(NPL):
            Up = prepare(plant(U, kind), edges)
            h2 += O2(Up, NP2p)["p"] < 0.05
            h3 += O3(Up, NP3p)["p"] < 0.05
        res["power"][kind] = dict(O2=h2 / NPL, O3=h3 / NPL)
        print(kind, res["power"][kind], flush=True)
    sup = min(holm.values()) < 0.05
    refute = (not sup) and max(res["power"]["a"]["O2"], res["power"]["b"]["O2"], res["power"]["a"]["O3"], res["power"]["b"]["O3"]) >= 0.8
    res["decision"] = "SUPPORTED" if sup else "REFUTED" if refute else "INCONCLUSIVE"
    print(json.dumps(res, indent=1))
    if not SMOKE:
        json.dump(res, open(OUT / "e4.json", "w"), indent=1)


if __name__ == "__main__":
    main()
