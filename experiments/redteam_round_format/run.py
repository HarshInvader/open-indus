"""Red team of #22 (board #23, H9). Prereg: docs/prereg/redteam_round_format.md
    PYTHONHASHSEED=0 .venv/bin/python -I experiments/redteam_round_format/run.py
Attack 3 (corrected set), Attack 4 (order vs inventory decomposition), Attack 5 (KN on grammar's set),
plus Gaur over-representation (Attack 1, descriptive).
"""
import sys, json, itertools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT)]
import q4_gulf as Q  # noqa
from corpus.load import icit_texts  # noqa

ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}  # CISI H-368/H-369: classified as incised tablets (CISI 1, intro fn 75)
rng = np.random.default_rng(23)

# ---- build groups exactly as fmt_control.py (first-seen dedup) ----
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
    (native if grp == "n" else foreign).append(dict(seq=s, site=site, fmt=fmt, type=t["type"], id=t["id"], sym=t["symbol"]))
fk = {" ".join(r["seq"]) for r in foreign}
native = [r for r in native if " ".join(r["seq"]) not in fk]
nt = [r["seq"] for r in native]
N = len(nt)

# ---- CV models: record fold model per native text ----
idx = rng.permutation(N); fold_of = np.zeros(N, int)
models = []
for f in range(10):
    te = idx[f::10]; fold_of[te] = f
    models.append(Q.KN([nt[i] for i in np.setdiff1d(idx, te)]))
FULL = Q.KN(nt)


def perms(seq, k=200):
    L = len(seq)
    if L <= 5:
        ps = {p for p in itertools.permutations(seq)}
        ps.discard(tuple(seq))
        ps = list(ps)
        if not ps: return []
        return ps if len(ps) <= k else [ps[i] for i in rng.choice(len(ps), k, replace=False)]
    out = []
    for _ in range(k):
        p = list(rng.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def decomp(seq, M):
    real = M.bits(seq)
    ps = perms(seq)
    if not ps: return real, np.nan, np.nan, np.nan
    pb = np.array([M.bits(list(p)) for p in ps])
    return real, real - pb.mean(), pb.mean(), float((pb <= real).mean())


rows = []
for i, r in enumerate(native):
    real, d, u, q = decomp(r["seq"], models[fold_of[i]])
    rows.append(dict(r, grp="home", real=real, d=d, u=u, q=q, L=len(r["seq"])))
for r in foreign:
    real, d, u, q = decomp(r["seq"], FULL)
    rows.append(dict(r, grp="foreign", real=real, d=d, u=u, q=q, L=len(r["seq"])))

ok = lambda x: x["L"] >= 2 and not np.isnan(x["d"])  # order defined only if a distinct permutation exists
home_seal = [x for x in rows if x["grp"] == "home" and x["fmt"] == "seal" and ok(x)]
h8_circ = [x for x in rows if x["grp"] == "home" and x["fmt"] == "round"]
circ = [x for x in h8_circ if x["id"] not in NOT_SEALS]
circ2 = [x for x in circ if ok(x)]
fr = [x for x in rows if x["grp"] == "foreign" and x["fmt"] == "round" and ok(x)]

bylen = defaultdict(list)
for x in home_seal: bylen[min(x["L"], 9)].append(x)


def vs_home(group, key, ndraw=10000, shift=0.0, ref=None):
    bl = bylen if ref is None else ref
    keys = [min(x["L"], 9) for x in group]
    pools = {k: np.array([y[key] for y in bl[k]]) for k in set(keys)}
    obs = float(np.mean([x[key] for x in group])) + shift
    draws = np.array([np.mean([pools[k][rng.integers(len(pools[k]))] for k in keys]) for _ in range(ndraw)])
    p = (1 + (draws >= obs).sum()) / (ndraw + 1)
    return dict(n=len(group), mean=obs, matched_home=float(draws.mean()), diff=obs - float(draws.mean()), p=float(p))


def perm_diff(a, b, n=20000):
    a, b = np.asarray(a), np.asarray(b); obs = a.mean() - b.mean(); allv = np.concatenate([a, b]); na = len(a)
    ds = np.empty(n)
    for i in range(n):
        p = rng.permutation(len(allv)); ds[i] = allv[p[:na]].mean() - allv[p[na:]].mean()
    return dict(n_a=len(a), n_b=len(b), diff=float(obs), p_two_sided=float((1 + (np.abs(ds) >= abs(obs)).sum()) / (n + 1)))


R = {"n_native": N, "h8_home_circular_ids": [x["id"] for x in h8_circ], "corrected_ids": [x["id"] for x in circ2]}
# Attack 3: KN total bits, corrected set
R["A3_total_h8set"] = vs_home([x for x in h8_circ if ok(x)], "real")
R["A3_total_corrected"] = vs_home(circ2, "real")
R["A3_total_foreign"] = vs_home(fr, "real")
# Attack 4: decomposition
P = {}
P["home_circ_order_d"] = vs_home(circ2, "d")
P["home_circ_inventory_u"] = vs_home(circ2, "u")
P["foreign_minus_circ_order_d"] = perm_diff([x["d"] for x in fr], [x["d"] for x in circ2])
P["foreign_minus_circ_inventory_u"] = perm_diff([x["u"] for x in fr], [x["u"] for x in circ2])
ps = {"home_circ_order_d": P["home_circ_order_d"]["p"], "home_circ_inventory_u": P["home_circ_inventory_u"]["p"],
      "foreign_minus_circ_order_d": P["foreign_minus_circ_order_d"]["p_two_sided"],
      "foreign_minus_circ_inventory_u": P["foreign_minus_circ_inventory_u"]["p_two_sided"]}
order = sorted(ps, key=ps.get); holm = {}; run = 0
for j, k in enumerate(order):
    run = max(run, min(1, ps[k] * (len(order) - j))); holm[k] = run
for k in P: P[k]["p_holm"] = holm[k]
R["A4_primary"] = P
R["A4_secondary"] = dict(foreign_order_d=vs_home(fr, "d"), foreign_inventory_u=vs_home(fr, "u"),
                         home_seal_mean_d=float(np.mean([x["d"] for x in home_seal])),
                         home_seal_mean_u=float(np.mean([x["u"] for x in home_seal])),
                         home_circ_mean_q=float(np.mean([x["q"] for x in circ2])),
                         foreign_mean_q=float(np.mean([x["q"] for x in fr])),
                         home_seal_mean_q=float(np.mean([x["q"] for x in home_seal])))
# power for foreign-minus-circ on d: true diff = foreign d excess over home seals
eff = R["A4_secondary"]["foreign_order_d"]["diff"]
hits = 0; sims = 400
fd = np.array([x["d"] for x in fr])
for _ in range(sims):
    keys = [min(x["L"], 9) for x in circ2]
    samp = np.array([bylen[k][rng.integers(len(bylen[k]))]["d"] for k in keys])
    # null world: home-circular = ordinary home seals; alt world: foreign shifted down by eff relative to them
    a = samp + 0.0; b = fd
    # power: chance to detect foreign > circ when circ behaves like ordinary home seals
    obs = b.mean() - a.mean(); allv = np.concatenate([b, a]); nb = len(b)
    ds = np.array([(lambda p: allv[p[:nb]].mean() - allv[p[nb:]].mean())(rng.permutation(len(allv))) for _ in range(500)])
    hits += ((1 + (np.abs(ds) >= abs(obs)).sum()) / 501) < 0.05
R["A4_power_foreign_vs_ordinary_circ_n"] = dict(order_effect=eff, power=hits / sims, n_home=len(circ2), n_foreign=len(fr))
# POST HOC robustness (not in prereg): uniqueness confound. Home seals often have near-copies in the CV
# training folds (moulded/repeated texts), which makes their real order look memorised; circular and foreign texts
# are unique. Reference = home seals with no other native text sharing >=50% of their bigram set (Jaccard).
def bg(seq): return {(a, b) for a, b in zip(seq, seq[1:])}
allbg = [bg(t) for t in nt]
inv = defaultdict(set)
for i, B in enumerate(allbg):
    for b in B: inv[b].add(i)
pos = {id(r): i for i, r in enumerate(native)}
uniq_ref = defaultdict(list); nuniq = 0
id2i = {r["id"]: i for i, r in enumerate(native)}
for x in home_seal:
    i = id2i[x["id"]]; B = allbg[i]; cand = set().union(*(inv[b] for b in B)) - {i}
    if all(len(B & allbg[j]) / len(B | allbg[j]) < 0.5 for j in cand):
        uniq_ref[min(x["L"], 9)].append(x); nuniq += 1
R["POSTHOC_unique_ref"] = dict(n_unique_home_seals=nuniq,
    circ_d=vs_home(circ2, "d", ref=uniq_ref), circ_u=vs_home(circ2, "u", ref=uniq_ref),
    circ_total=vs_home(circ2, "real", ref=uniq_ref),
    foreign_d=vs_home(fr, "d", ref=uniq_ref), foreign_u=vs_home(fr, "u", ref=uniq_ref),
    foreign_total=vs_home(fr, "real", ref=uniq_ref),
    unique_seal_mean_d=float(np.mean([x["d"] for v in uniq_ref.values() for x in v])),
    unique_seal_mean_q=float(np.mean([x["q"] for v in uniq_ref.values() for x in v])))
# Attack 1 descriptive: Gaur symbol
hs_all = [x for x in rows if x["grp"] == "home" and x["fmt"] == "seal"]
g_c = sum("Gaur" in (x["sym"] or "") for x in circ); g_s = sum("Gaur" in (x["sym"] or "") for x in hs_all)
R["A1_gaur"] = dict(circ_gaur=g_c, circ_n=len(circ), seal_gaur=g_s, seal_n=len(hs_all),
                    fisher_p=float(fisher_exact([[g_c, len(circ) - g_c], [g_s, len(hs_all) - g_s]])[1]))
fg = [x for x in rows if x["grp"] == "foreign" and x["fmt"] == "round"]
R["A1_gaur"]["foreign_round_gaur"] = sum("Gaur" in (x["sym"] or "") for x in fg); R["A1_gaur"]["foreign_round_n"] = len(fg)
# Attack 5: KN on grammar's 12-unit home-round set (ICIT SEAL:C/CY at home, distinct by sequence, incl. 1-sign)
allhome = [t for t in icit_texts() if t["type"] in ROUND and t["site"] not in Q.FOREIGN_WEST | Q.FOREIGN_CA | {"Unknown"}]
gseen, gset = set(), []
for t in allhome:
    s = Q.clean(t["seq"]); k = " ".join(s)
    if s and k not in gseen: gseen.add(k); gset.append((t["id"], s))
byseq = {" ".join(x["seq"]): x for x in rows if x["grp"] == "home"}
g_rows = []
for i, s in gset:
    x = byseq.get(" ".join(s))
    g_rows.append(dict(id=i, seq=" ".join(s), L=len(s), kn_cv=round(float(x["real"]), 2) if x else None,
                       labelled_as=x["fmt"] if x else None, in_h8_set=bool(x and x["fmt"] == "round")))
R["A5_grammar_set_kn"] = g_rows
gr = [r for r in g_rows if r["kn_cv"] is not None]
R["A5_summary"] = dict(n=len(gr), kn_mean_all=float(np.mean([r["kn_cv"] for r in gr])),
                       kn_mean_h8=float(np.mean([r["kn_cv"] for r in gr if r["in_h8_set"]])),
                       kn_mean_extra=float(np.mean([r["kn_cv"] for r in gr if not r["in_h8_set"]])) if any(not r["in_h8_set"] for r in gr) else None)
R["per_text_home_circular"] = [dict(id=x["id"], site=x["site"], type=x["type"], sym=x["sym"], seq=" ".join(x["seq"]),
                                    real=round(x["real"], 2), d=round(x["d"], 2), u=round(x["u"], 2), q=round(x["q"], 2))
                               for x in h8_circ]
R["per_text_foreign_round"] = [dict(id=x["id"], site=x["site"], seq=" ".join(x["seq"]), real=round(x["real"], 2),
                                    d=round(x["d"], 2), u=round(x["u"], 2), q=round(x["q"], 2)) for x in fr]
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in R.items() if not k.startswith("per_text")}, indent=1, default=float))
for x in R["per_text_home_circular"]: print(x)
