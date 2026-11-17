"""Red team of #23 (board #25, H11). Prereg: docs/prereg/redteam_round_order.md
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/redteam_round_order/run.py
Stage 1 (cached in out/scores.pkl): KN / Wells-grammar / positional scores of every text and its permutations.
Stage 2: rare-load-matched nulls, planted controls, leave-one-out, sensitivity -> results.json
"""
import sys, json, itertools, pickle, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
(OUT / "out").mkdir(exist_ok=True)
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT / "experiments/grammar"), str(ROOT)]
import q4_gulf as Q  # noqa
import glib  # noqa
from glib import ClassBigram, PositionModel, unit_from  # noqa
from step1_classes_seeds import SEED_W  # noqa
from corpus.load import icit_texts  # noqa

T0 = time.time()
log = lambda *a: print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)
ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
CW = json.load(open(ROOT / "experiments/grammar/classes_wells.json"))
NPERM = 200
rng = np.random.default_rng(25)

# ---------------- groups (as #23) ----------------
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
    broken = ("#" in t["seq"]) or (not t["complete"])
    (native if grp == "n" else foreign).append(dict(seq=s, site=site, fmt=fmt, type=t["type"], id=t["id"], broken=broken))
fk = {" ".join(r["seq"]) for r in foreign}
native = [r for r in native if " ".join(r["seq"]) not in fk]
nt = [r["seq"] for r in native]
N = len(nt)
log("native", N, "foreign", len(foreign))


def perms(seq, k=NPERM):
    L = len(seq)
    if L <= 5:
        ps = set(itertools.permutations(seq)); ps.discard(tuple(seq)); ps = [list(p) for p in ps]
        if not ps: return []
        return ps if len(ps) <= k else [ps[i] for i in rng.choice(len(ps), k, replace=False)]
    out = []
    for _ in range(k):
        p = list(rng.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def U(seq):
    return unit_from(list(seq), True)


class GRw:
    def __init__(s, tr):
        s.m = ClassBigram(CW["K"], alpha=CW["alpha"]).fit([U(x) for x in tr], init=SEED_W, restarts=2)
    def bits(s, seq):
        a, n = s.m.unit_logp(U(seq)); return -a / n


class POSw:
    def __init__(s, tr):
        s.m = PositionModel(cap=4).fit([U(x) for x in tr])
    def bits(s, seq):
        a, n = s.m.unit_logp(U(seq)); return -a / n


SC = OUT / "out/scores.pkl"
if SC.exists():
    S = pickle.load(open(SC, "rb")); log("loaded cached scores")
else:
    idx = rng.permutation(N)
    f10 = np.zeros(N, int); f5 = np.zeros(N, int)
    for f in range(10): f10[idx[f::10]] = f
    for f in range(5): f5[idx[f::5]] = f
    P_nat = [perms(s) for s in nt]
    P_for = [perms(r["seq"]) for r in foreign]
    S = dict(f10=f10, f5=f5, P_nat=P_nat, P_for=P_for)
    # training counts per KN fold (for rare load)
    cnt10 = [Counter(x for i in range(N) if f10[i] != f for x in nt[i]) for f in range(10)]
    cfull = Counter(x for t in nt for x in t)
    S["r_nat"] = np.array([sum(cnt10[f10[i]][x] < 10 for x in nt[i]) for i in range(N)])
    S["unk_nat"] = np.array([sum(cnt10[f10[i]][x] < 2 for x in nt[i]) for i in range(N)])
    S["r_for"] = np.array([sum(cfull[x] < 10 for x in r["seq"]) for r in foreign])
    for name, mk, folds, nf in (("KN", Q.KN, f10, 10), ("GR", GRw, f5, 5), ("POS", POSw, f5, 5)):
        real = np.zeros(N); pb = [None] * N; models = []
        for f in range(nf):
            models.append(mk([nt[i] for i in range(N) if folds[i] != f])); log(name, "fold", f, "fitted")
        for i in range(N):
            M = models[folds[i]]; real[i] = M.bits(nt[i])
            pb[i] = np.array([M.bits(p) for p in P_nat[i]])
        full = mk(nt)
        freal = np.array([full.bits(r["seq"]) for r in foreign])
        fpb = [np.array([full.bits(p) for p in P_for[j]]) for j in range(len(foreign))]
        S[name] = dict(real=real, pb=pb, freal=freal, fpb=fpb)
        S[name + "_models"] = models  # kept for planted shuffles (scored by own fold model)
        log(name, "scored")
    pickle.dump(S, open(SC, "wb"))

# ---------------- per-text statistics ----------------
def dq(real, pb):
    if len(pb) == 0: return np.nan, np.nan, np.nan
    return real - pb.mean(), pb.mean(), float((pb <= real).mean())

stat = {}
for name in ("KN", "GR", "POS"):
    D = S[name]
    stat[name] = dict(nat=np.array([dq(D["real"][i], D["pb"][i]) for i in range(N)]),
                      for_=np.array([dq(D["freal"][j], D["fpb"][j]) for j in range(len(foreign))]))
L_nat = np.array([len(s) for s in nt]); L_for = np.array([len(r["seq"]) for r in foreign])
has_perm = np.array([len(p) > 0 for p in S["P_nat"]])
fmt = np.array([r["fmt"] for r in native]); ids = np.array([r["id"] for r in native])
broken = np.array([r["broken"] for r in native])
seal = (fmt == "seal") & has_perm
circ = np.where((fmt == "round") & has_perm & ~np.isin(ids, list(NOT_SEALS)))[0]
fr = np.array([j for j, r in enumerate(foreign) if r["fmt"] == "round" and len(S["P_for"][j]) > 0])
log("home round ids", list(ids[circ]), "foreign round n", len(fr))
r_nat, r_for = S["r_nat"], S["r_for"]

# no-near-copy reference (#23 rule)
def bg(seq): return {(a, b) for a, b in zip(seq, seq[1:])}
allbg = [bg(t) for t in nt]; inv = defaultdict(set)
for i, B in enumerate(allbg):
    for b in B: inv[b].add(i)
uniq = np.zeros(N, bool)
for i in np.where(seal)[0]:
    B = allbg[i]; cand = set().union(*(inv[b] for b in B)) - {i} if B else set()
    uniq[i] = all(len(B & allbg[j]) / len(B | allbg[j]) < 0.5 for j in cand)


# ---------------- strata and matched nulls ----------------
def make_pools(ref_mask, mode):
    """mode: 'N0' length; 'N1' length x rare; 'N3' length x rare x broken"""
    pools = defaultdict(list)
    for i in np.where(ref_mask)[0]:
        L = min(L_nat[i], 9); r = min(r_nat[i], 3)
        k = (L,) if mode == "N0" else (L, r) if mode == "N1" else (L, r, bool(broken[i]))
        pools[k].append(i)
    return {k: np.array(v) for k, v in pools.items()}


def key_for(L, r, b, mode, pools):
    L = min(L, 9); r = min(r, 3)
    if mode == "N0":
        k = (L,)
        while (len(pools.get(k, [])) < 5) and k[0] > 1: k = (k[0] - 1,)
        return k
    for LL in range(L, 0, -1):
        for rr in range(r, -1, -1):
            k = (LL, rr) if mode == "N1" else (LL, rr, b)
            if len(pools.get(k, [])) >= 5: return k
    raise ValueError("no stratum")


def null_test(vals, keys, pools, refvals, ndraw):
    obs = float(np.mean(vals))
    mats = np.stack([refvals[pools[k][rng.integers(len(pools[k]), size=ndraw)]] for k in keys])
    draws = mats.mean(0)
    return dict(n=len(vals), mean=obs, null_mean=float(draws.mean()), diff=obs - float(draws.mean()),
                p=float((1 + (draws >= obs).sum()) / (ndraw + 1)))


def test_group(sel_vals, sel_L, sel_r, sel_b, scorer, mode, ref_mask=None, col=0, ndraw=10000):
    ref_mask = seal if ref_mask is None else ref_mask
    pools = make_pools(ref_mask, mode)
    keys = [key_for(L, r, b, mode, pools) for L, r, b in zip(sel_L, sel_r, sel_b)]
    return null_test(sel_vals, keys, pools, stat[scorer]["nat"][:, col], ndraw)


R = dict(n_native=N, n_home_seals=int(seal.sum()), n_unique_seals=int(uniq.sum()), home_round_ids=list(ids[circ]),
         nperm=NPERM, cuts="GR restarts 5->2; planted controls 1000 reps x 2000 null draws")
R["home_round_texts"] = [dict(id=ids[i], seq=" ".join(nt[i]), L=int(L_nat[i]), rare_lt10=int(r_nat[i]), unk=int(S["unk_nat"][i]),
                              broken=bool(broken[i]), **{f"{s}_d": round(float(stat[s]["nat"][i, 0]), 3) for s in stat},
                              **{f"{s}_q": round(float(stat[s]["nat"][i, 2]), 3) for s in stat}) for i in circ]
# rare-load description
R["rare_load"] = dict(home_round_mean_r_over_L=float(np.mean(r_nat[circ] / L_nat[circ])),
                      home_seal_mean_r_over_L=float(np.mean(r_nat[seal] / L_nat[seal])),
                      foreign_round_mean_r_over_L=float(np.mean(r_for[fr] / L_for[fr])))

# primary
cb = broken[circ]
prim = {}
for s in ("KN", "GR", "POS"):
    prim[s] = test_group(stat[s]["nat"][circ, 0], L_nat[circ], r_nat[circ], cb, s, "N1")
order = sorted(prim, key=lambda k: prim[k]["p"]); run = 0
for j, k in enumerate(order):
    run = max(run, min(1, prim[k]["p"] * (3 - j))); prim[k]["p_holm"] = run
R["primary_N1"] = prim
log("primary", json.dumps(prim))

# secondary
sec = {}
for s in ("KN", "GR", "POS"):
    sec[s] = dict(
        N0=test_group(stat[s]["nat"][circ, 0], L_nat[circ], r_nat[circ], cb, s, "N0"),
        N2_unique=test_group(stat[s]["nat"][circ, 0], L_nat[circ], r_nat[circ], cb, s, "N1", ref_mask=seal & uniq),
        N3_broken=test_group(stat[s]["nat"][circ, 0], L_nat[circ], r_nat[circ], cb, s, "N3"),
        q_N1=test_group(stat[s]["nat"][circ, 2], L_nat[circ], r_nat[circ], cb, s, "N1", col=2),
        q_N0=test_group(stat[s]["nat"][circ, 2], L_nat[circ], r_nat[circ], cb, s, "N0", col=2),
        foreign_N0=test_group(stat[s]["for_"][fr, 0], L_for[fr], r_for[fr], [False] * len(fr), s, "N0"),
        foreign_N1=test_group(stat[s]["for_"][fr, 0], L_for[fr], r_for[fr], [False] * len(fr), s, "N1"),
    )
    # foreign minus home round on N1-standardised d
    pools = make_pools(seal, "N1"); dn = stat[s]["nat"][:, 0]
    def resid(vals, Ls, rs):
        return np.array([v - dn[pools[key_for(L, r, False, "N1", pools)]].mean() for v, L, r in zip(vals, Ls, rs)])
    a = resid(stat[s]["for_"][fr, 0], L_for[fr], r_for[fr]); b = resid(stat[s]["nat"][circ, 0], L_nat[circ], r_nat[circ])
    allv = np.concatenate([a, b]); na = len(a); obs = a.mean() - b.mean()
    ds = np.array([(lambda p: allv[p[:na]].mean() - allv[p[na:]].mean())(rng.permutation(len(allv))) for _ in range(20000)])
    sec[s]["foreign_minus_round_resid"] = dict(foreign=float(a.mean()), home_round=float(b.mean()), diff=float(obs),
                                               p_two_sided=float((1 + (np.abs(ds) >= abs(obs)).sum()) / 20001))
R["secondary"] = sec
log("secondary done")

# leave-one-out
loo = {s: [] for s in stat}
for s in stat:
    for j in range(len(circ)):
        keep = np.delete(circ, j)
        t = test_group(stat[s]["nat"][keep, 0], L_nat[keep], r_nat[keep], broken[keep], s, "N1", ndraw=5000)
        loo[s].append(dict(dropped=ids[circ[j]], diff=t["diff"], p=t["p"]))
R["loo_N1"] = {s: dict(rows=loo[s], max_p=max(x["p"] for x in loo[s]), min_diff=min(x["diff"] for x in loo[s])) for s in loo}

# complete-only
comp = circ[~broken[circ]]
R["complete_only"] = {s: test_group(stat[s]["nat"][comp, 0], L_nat[comp], r_nat[comp], [False] * len(comp), s, "N1",
                                    ref_mask=seal & ~broken) for s in stat}
R["complete_only"]["ids"] = list(ids[comp])

# 2977.1 reversed (KN, its own fold model)
i2977 = [i for i in circ if ids[i] == "2977.1"]
if i2977:
    i = i2977[0]; M = S["KN_models"][S["f10"][i]]
    rv = M.bits(nt[i][::-1]) - S["KN"]["pb"][i].mean()
    vals = stat["KN"]["nat"][circ, 0].copy(); vals[list(circ).index(i)] = rv
    R["rev_2977_KN"] = dict(d_reversed=float(rv), test=test_group(vals, L_nat[circ], r_nat[circ], cb, "KN", "N1"))
log("loo/sensitivity done")

# ---------------- planted controls ----------------
def score_shuffled(s, i):
    M = S[s + "_models"][S["f10" if s == "KN" else "f5"][i]]
    ps = S["P_nat"][i]
    p = ps[rng.integers(len(ps))]
    return M.bits(p) - S[s]["pb"][i].mean()

REPS, ND = 1000, 2000
planted = {}
for s in ("KN", "GR", "POS"):
    dn = stat[s]["nat"][:, 0]
    P1 = make_pools(seal, "N1"); P0 = make_pools(seal, "N0")
    keys1 = [key_for(L, r, False, "N1", P1) for L, r in zip(L_nat[circ], r_nat[circ])]
    keys0 = [key_for(L, r, False, "N0", P0) for L, r in zip(L_nat[circ], r_nat[circ])]
    # pre-draw null distributions once per mode (same keys every replicate)
    def nulldraws(pools, keys):
        return np.stack([dn[pools[k][rng.integers(len(pools[k]), size=ND)]] for k in keys]).mean(0)
    nd1 = nulldraws(P1, keys1); nd0 = nulldraws(P0, keys0)
    pv = lambda obs, nd: (1 + (nd >= obs).sum()) / (len(nd) + 1)
    # rare-heavy pool: top quartile r/L within length, home seals
    rh = defaultdict(list)
    for L in set(min(x, 9) for x in L_nat[circ]):
        m = np.where(seal & (np.minimum(L_nat, 9) == L))[0]
        rl = r_nat[m] / L_nat[m]; thr = np.quantile(rl, 0.75)
        rh[L] = m[rl >= thr]
    c1 = c2_0 = c2_1 = c2b_0 = c2b_1 = 0
    for _ in range(REPS):
        pick = [P1[k][rng.integers(len(P1[k]))] for k in keys1]
        sh = np.mean([score_shuffled(s, i) for i in pick])
        c1 += pv(sh, nd1) < 0.05
        un = np.mean(dn[pick])
        c2_0 += pv(un, nd0) < 0.05; c2_1 += pv(un, nd1) < 0.05
        pick2 = [rh[min(L, 9)][rng.integers(len(rh[min(L, 9)]))] for L in L_nat[circ]]
        un2 = np.mean(dn[pick2])
        c2b_0 += pv(un2, nd0) < 0.05; c2b_1 += pv(un2, nd1) < 0.05
    planted[s] = dict(C1_power_shuffled_rare_matched=c1 / REPS, C2_fp_rare_matched_N0=c2_0 / REPS, C2_fp_rare_matched_N1=c2_1 / REPS,
                      C2b_fp_top_quartile_rare_N0=c2b_0 / REPS, C2b_fp_top_quartile_rare_N1=c2b_1 / REPS)
    log("planted", s, planted[s])
R["planted"] = planted

# ---------------- decision ----------------
p = R["primary_N1"]
surv = (p["KN"]["p_holm"] < 0.05 and (p["GR"]["p_holm"] < 0.05 or p["POS"]["p_holm"] < 0.05)
        and planted["KN"]["C1_power_shuffled_rare_matched"] >= 0.8 and planted["KN"]["C2_fp_rare_matched_N1"] <= 0.10
        and R["loo_N1"]["KN"]["max_p"] < 0.05 and R["complete_only"]["KN"]["diff"] > 0)
if planted["KN"]["C1_power_shuffled_rare_matched"] < 0.5: verdict = "inconclusive"
elif surv: verdict = "survives"
elif p["KN"]["p"] >= 0.05 and planted["KN"]["C1_power_shuffled_rare_matched"] >= 0.8: verdict = "falls"
else: verdict = "weakens"
R["verdict_by_prereg_rule"] = verdict
R["n_over_half_N0"] = {s: p[s]["diff"] / sec[s]["N0"]["diff"] if sec[s]["N0"]["diff"] else None for s in p}
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("VERDICT", verdict)
print(json.dumps({k: v for k, v in R.items() if k != "home_round_texts"}, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
for x in R["home_round_texts"]: print(x)
