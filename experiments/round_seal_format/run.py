"""Round-seal format test (board #39). Prereg: docs/prereg/round_seal_format.md
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/round_seal_format/run.py
"""
import sys, json, csv, itertools, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT / "experiments/grammar"), str(ROOT)]
import q4_gulf as Q  # noqa
import glib  # noqa
from corpus.load import icit_texts  # noqa

T0 = time.time()
log = lambda *a: print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)
rng = np.random.default_rng(39)
ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
NUM = set(glib.NUM["ICIT"])
SC = list(csv.DictReader(open(ROOT / "experiments/grammar/sign_classes.csv")))
def wset(lab):
    return {w for r in SC if r["final_class"] == lab for w in r["wells_signs"].split() if w.startswith("W")}
OPEN, CLOSE = wset("opener"), wset("closer")
NDRAW = 10000
R = dict(opener_W=sorted(OPEN), closer_W=sorted(CLOSE), n_numeral_signs=len(NUM))


def legible(seq):
    return [s for s in seq if s not in ("|", "#") and s.startswith("W")]


def mk(seq_raw, **kw):
    raw = [s for s in seq_raw if s != "|"]
    sg = legible(raw)
    first_ok = bool(raw) and raw[0] != "#"
    last_ok = bool(raw) and raw[-1] != "#"
    return dict(seq=sg, L=len(sg), first_ok=first_ok, last_ok=last_ok,
                num1=first_ok and bool(sg) and sg[0] in NUM, op1=first_ok and bool(sg) and sg[0] in OPEN,
                clL=last_ok and bool(sg) and sg[-1] in CLOSE, **kw)


# ---------------- build groups ----------------
seen, units = set(), []
for t in icit_texts():
    site = t["site"]
    grp = "abroad" if site in glib.FOREIGN else "unprov" if site == "Unknown" else "home"
    tp = t["type"]
    if not tp.startswith("SEAL") or t["id"] in NOT_SEALS: continue
    u = mk(t["seq"], site=site, grp=grp, round=tp in ROUND, id=t["id"], type=tp,
           complete=bool(t["complete"]) and "#" not in t["seq"])
    if u["L"] == 0: continue
    k = (grp, " ".join(u["seq"]))
    if k in seen: continue
    seen.add(k); units.append(u)
round_keys = {" ".join(u["seq"]) for u in units if u["round"]}
rnd = [u for u in units if u["round"]]
sq = [u for u in units if not u["round"] and u["grp"] == "home" and " ".join(u["seq"]) not in round_keys]
fsq = [u for u in units if not u["round"] and u["grp"] == "abroad"]
for u in rnd: u["ab"] = u["grp"] != "home"
R["n"] = dict(round=len(rnd), round_home=sum(u["grp"] == "home" for u in rnd), round_abroad=sum(u["grp"] == "abroad" for u in rnd),
              round_unprov=sum(u["grp"] == "unprov" for u in rnd), square_home=len(sq), square_abroad=len(fsq))
log(R["n"])


# ---------------- F tests ----------------
def strata(pool, keyf):
    d = defaultdict(list)
    for i, u in enumerate(pool): d[keyf(u)].append(i)
    return d


def matched_share(sel, pool, feat, use_site, cond):
    """mean of feat over sel vs matched draws from pool; returns obs, null mean, draws"""
    sel = [u for u in sel if cond(u)]; pool = [u for u in pool if cond(u)]
    vals = np.array([float(u[feat]) for u in pool])
    by_sl = strata(pool, lambda u: (u["site"], min(u["L"], 7)))
    by_l = strata(pool, lambda u: min(u["L"], 7))
    idxs, fb = [], 0
    for u in sel:
        c = by_sl.get((u["site"], min(u["L"], 7)), []) if (use_site and u["grp"] == "home") else []
        if len(c) < 5:
            if use_site and u["grp"] == "home": fb += 1
            L = min(u["L"], 7)
            while len(by_l.get(L, [])) < 5 and L > 1: L -= 1
            c = by_l[L]
        idxs.append(np.array(c))
    draws = np.stack([vals[c[rng.integers(len(c), size=NDRAW)]] for c in idxs]).mean(0)
    obs = float(np.mean([u[feat] for u in sel]))
    return dict(n=len(sel), obs=obs, null=float(draws.mean()), fallback=fb), draws


def ptest(obs, draws, direction):
    return float((1 + ((draws >= obs) if direction > 0 else (draws <= obs)).sum()) / (len(draws) + 1))


def ftests(sel, tag):
    out = {}
    for name, feat, dirn, cond in (("F1_numeral_first", "num1", 1, lambda u: u["first_ok"]),
                                    ("F2_opener_first", "op1", -1, lambda u: u["first_ok"]),
                                    ("F4_closer_last", "clL", -1, lambda u: u["last_ok"])):
        r, dr = matched_share(sel, sq, feat, True, cond)
        r["p"] = ptest(r["obs"], dr, dirn); out[name] = r
    # F3 length: site-matched (home), all-home (abroad), no length matching
    s_c = [u for u in sel if u["complete"]]; p_c = [u for u in sq if u["complete"]]
    Ls = np.array([u["L"] for u in p_c]); bys = strata(p_c, lambda u: u["site"])
    idx = [np.array(bys[u["site"]]) if (u["grp"] == "home" and len(bys.get(u["site"], [])) >= 5) else np.arange(len(p_c)) for u in s_c]
    if s_c:
        dr = np.stack([Ls[c[rng.integers(len(c), size=NDRAW)]] for c in idx]).mean(0)
        obs = float(np.mean([u["L"] for u in s_c]))
        out["F3_length"] = dict(n=len(s_c), obs=obs, null=float(dr.mean()), p=ptest(obs, dr, -1))
    return out


F = ftests(rnd, "all")
order = sorted(F, key=lambda k: F[k]["p"]); run = 0
for j, k in enumerate(order):
    run = max(run, min(1, F[k]["p"] * (len(order) - j))); F[k]["p_holm"] = run
R["F_primary"] = F
R["F_home"] = ftests([u for u in rnd if u["grp"] == "home"], "home")
R["F_abroad_all"] = ftests([u for u in rnd if u["grp"] != "home"], "abroad")
R["F_abroad_no_unprov"] = ftests([u for u in rnd if u["grp"] == "abroad"], "abroad")
R["descr"] = {g: dict(n=len(us), numeral_first=float(np.mean([u["num1"] for u in us if u["first_ok"]] or [np.nan])),
                      opener_first=float(np.mean([u["op1"] for u in us if u["first_ok"]] or [np.nan])),
                      closer_last=float(np.mean([u["clL"] for u in us if u["last_ok"]] or [np.nan])),
                      mean_len_complete=float(np.mean([u["L"] for u in us if u["complete"]] or [np.nan])))
              for g, us in (("round_home", [u for u in rnd if u["grp"] == "home"]),
                            ("round_abroad", [u for u in rnd if u["grp"] == "abroad"]),
                            ("round_unprov", [u for u in rnd if u["grp"] == "unprov"]),
                            ("square_home", sq), ("square_abroad", fsq))}
log("F", json.dumps(F, indent=0))

# ---------------- near-copy clusters among round texts ----------------
def bg(s): return {(a, b) for a, b in zip(s, s[1:])}
par = list(range(len(rnd)))
def find(i):
    while par[i] != i: i = par[i]
    return i
for i, j in itertools.combinations(range(len(rnd)), 2):
    A, B = bg(rnd[i]["seq"]), bg(rnd[j]["seq"])
    if A and B and len(A & B) / len(A | B) >= 0.5: par[find(i)] = find(j)
cl = Counter(find(i) for i in range(len(rnd)))
keep1, seenc = [], set()
for i in range(len(rnd)):
    if find(i) not in seenc: seenc.add(find(i)); keep1.append(rnd[i])
R["near_copy"] = dict(clusters_gt1=[c for c in cl.values() if c > 1], n_after=len(keep1))
R["F_nearcopy_dedup"] = {k: v for k, v in ftests(keep1, "dedup").items() if k in ("F1_numeral_first", "F2_opener_first")}

# ---------------- held-out ----------------
fc = pd.read_csv(ROOT / "experiments/foreign_corpus/foreign_corpus.csv")
ho = []
for _, r in fc.iterrows():
    sh = str(r["shape"]).lower()
    if not ("round" in sh or "cylinder" in sh): continue
    if pd.notna(r["icit_id"]) or not isinstance(r["seq_wells"], str): continue
    if r["n_legible"] < 2: continue
    raw = ["#" if s.strip() in ("?", "") else s.strip() for s in r["seq_wells"].split("-")]
    ho.append(mk(raw, id=r["id"], site=r["findspot"], grp="abroad", round=True, complete=False))
# square matched rates for held-out texts (length-matched, all home squares)
def rate(u, feat):
    L = min(u["L"], 7); c = [v for v in sq if min(v["L"], 7) == L and v["first_ok"]]
    return float(np.mean([v[feat] for v in c]))
hoF = [u for u in ho if u["first_ok"]]
p_num = [rate(u, "num1") for u in hoF]; p_op = [rate(u, "op1") for u in hoF]
k_num = sum(u["num1"] for u in hoF); k_op = sum(u["op1"] for u in hoF)
def pb_tail(ps, k, upper):
    sims = (rng.random((100000, len(ps))) < np.array(ps)).sum(1)
    return float(((sims >= k) if upper else (sims <= k)).mean())
# power: discovery numeral-first share as truth
p_true = F["F1_numeral_first"]["obs"]
sims = (rng.random((10000, len(hoF))) < p_true).sum(1)
crit = [k for k in range(len(hoF) + 1) if pb_tail(p_num, k, True) < 0.05] if hoF else []
power = float((sims >= min(crit)).mean()) if crit else 0.0
R["heldout"] = dict(ids=[u["id"] for u in ho], n=len(ho), n_first_legible=len(hoF), L=[u["L"] for u in ho],
                    numeral_first=int(k_num), opener_first=int(k_op), square_rates_num=p_num, square_rates_op=p_op,
                    p_F1=pb_tail(p_num, k_num, True) if hoF else None, p_F2=pb_tail(p_op, k_op, False) if hoF else None,
                    power_F1=power, power_note="p(numeral-first)=discovery share; smallest k reaching p<0.05" if crit else "no outcome can reach p<0.05")
# n needed for 0.8 power with matched square share ~ mean null
p0 = F["F1_numeral_first"]["null"]
for n in range(2, 400):
    kc = binom.ppf(0.95, n, p0) + 1
    if binom.sf(kc - 1, n, p_true) >= 0.8: R["heldout"]["n_for_power_0.8"] = n; break
log("heldout", R["heldout"])

# ---------------- order scores (KN) ----------------
home_all = []  # all home seal texts (round + squares) for KN training, as #25 (home seals and others)
seen2 = set()
for t in icit_texts():
    s = Q.clean(t["seq"]); s = [x for x in s if x.startswith("W")]
    if not s or t["site"] in glib.FOREIGN or t["site"] == "Unknown": continue
    k = " ".join(s)
    if k in seen2: continue
    seen2.add(k); home_all.append(s)
home_index = {" ".join(s): i for i, s in enumerate(home_all)}
N = len(home_all)
idx = rng.permutation(N); f10 = np.zeros(N, int)
for f in range(10): f10[idx[f::10]] = f
models = [Q.KN([home_all[i] for i in range(N) if f10[i] != f]) for f in range(10)]
FULL = Q.KN(home_all)
log("KN fitted", N)


def perms(seq, k=200):
    if len(seq) <= 5:
        ps = set(itertools.permutations(seq)); ps.discard(tuple(seq)); ps = [list(p) for p in ps]
        return ps if len(ps) <= k else [ps[i] for i in rng.choice(len(ps), k, replace=False)]
    out = []
    for _ in range(k):
        p = list(rng.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def model_for(u):
    k = " ".join(u["seq"])
    return models[f10[home_index[k]]] if (u["grp"] == "home" and k in home_index) else FULL


def dscore(seq, M):
    ps = perms(seq)
    if len(seq) < 2 or not ps: return np.nan
    return M.bits(seq) - float(np.mean([M.bits(p) for p in ps]))


for grp in (rnd, sq, fsq, ho):
    for u in grp: u["d"] = dscore(u["seq"], model_for(u))
log("order scored")
sqd = [u for u in sq if not np.isnan(u["d"])]
sqvals = np.array([u["d"] for u in sqd])


def fkey(u, lvl):
    L = min(u["L"], 9)
    return [(L, u["num1"], u["op1"], u["clL"]), (L, u["num1"], u["op1"]), (L, u["num1"]), (L,)][lvl]


POOLS = [strata(sqd, lambda u, l=l: fkey(u, l)) for l in range(4)]


def keys_for(sel, fmt):
    out = []
    for u in sel:
        if fmt:
            got = None
            for l in range(3):
                c = POOLS[l].get(fkey(u, l), [])
                if len(c) >= 5: got = c; break
            if got is None:
                L = min(u["L"], 9)
                while len(POOLS[3].get((L,), [])) < 5 and L > 2: L -= 1
                got = POOLS[3][(L,)]
        else:
            L = min(u["L"], 9)
            while len(POOLS[3].get((L,), [])) < 5 and L > 2: L -= 1
            got = POOLS[3][(L,)]
        out.append(np.array(got))
    return out


def order_test(sel, fmt, ndraw=NDRAW, vals=None, alt=1):
    sel = [u for u in sel if not np.isnan(u["d"])]
    ks = keys_for(sel, fmt)
    draws = np.stack([sqvals[c[rng.integers(len(c), size=ndraw)]] for c in ks]).mean(0)
    v = np.array([u["d"] for u in sel]) if vals is None else vals
    obs = float(v.mean())
    p = ptest(obs, draws, 1) if alt > 0 else float(min(1, 2 * min(ptest(obs, draws, 1), ptest(obs, draws, -1))))
    return dict(n=len(sel), mean_d=obs, null=float(draws.mean()), excess=obs - float(draws.mean()), p=p), ks


rd = [u for u in rnd if not np.isnan(u["d"])]
O1f, ks_f = order_test(rd, True); O1l, ks_l = order_test(rd, False)
# bootstrap fraction explained
nm_f = np.array([sqvals[c].mean() for c in ks_f]); nm_l = np.array([sqvals[c].mean() for c in ks_l])
dv = np.array([u["d"] for u in rd]); fr = []
for _ in range(2000):
    b = rng.integers(len(rd), size=len(rd))
    el = (dv[b] - nm_l[b]).mean()
    if el > 0: fr.append(1 - (dv[b] - nm_f[b]).mean() / el)
O1 = dict(format_matched=O1f, length_only=O1l, frac_explained=1 - O1f["excess"] / O1l["excess"] if O1l["excess"] > 0 else None,
          frac_ci=[float(np.percentile(fr, 2.5)), float(np.percentile(fr, 97.5))])
O1["by_group"] = {g: dict(fmt=order_test([u for u in rd if u["grp"] == g], True)[0], len=order_test([u for u in rd if u["grp"] == g], False)[0])
                  for g in ("home", "abroad", "unprov")}
# O1b: home squares sharing the round format
fmt_sq = [u for u in sqd if u["num1"] and not u["op1"]]
r1b, _ = order_test(fmt_sq, False)
bs = [np.mean(rng.choice([u["d"] for u in fmt_sq], len(fmt_sq))) for _ in range(2000)]
r1b["ci_mean_d"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
O1b = r1b
O2, _ = order_test(fsq, False)
O2fmt, _ = order_test(fsq, True)
# O3: abroad(+unprov) round minus home round
hd = np.array([u["d"] for u in rd if u["grp"] == "home"]); ad = np.array([u["d"] for u in rd if u["grp"] != "home"])
obs3 = ad.mean() - hd.mean(); allv = np.concatenate([hd, ad]); null3 = []
for _ in range(NDRAW):
    p = rng.permutation(allv); null3.append(p[len(hd):].mean() - p[:len(hd)].mean())
null3 = np.array(null3)
O3 = dict(n_home=len(hd), n_abroad=len(ad), diff=float(obs3), p=float((1 + (np.abs(null3) >= abs(obs3)).sum()) / (NDRAW + 1)))
ps = {"O1": O1f["p"], "O2": O2["p"], "O3": O3["p"]}; srt = sorted(ps, key=ps.get); run = 0; holm = {}
for j, k in enumerate(srt):
    run = max(run, min(1, ps[k] * (3 - j))); holm[k] = run
R["order"] = dict(O1=O1, O1b_format_squares=O1b, O2_abroad_nonround=O2, O2_format_matched=O2fmt, O3=O3, holm=holm,
                  O1_nearcopy_dedup=order_test([u for u in keep1 if not np.isnan(u["d"])], True)[0])
log("order", json.dumps(R["order"], indent=0, default=float))

# ---------------- planted checks ----------------
REPS = 500
def shuffled_d(u):
    s = list(u["seq"])
    for _ in range(20):
        p = list(rng.permutation(s))
        if p != s: break
    return dscore(p, model_for(u))
# P1/P2: sets format-matched to round set (draw one square per round text from its format stratum)
p1 = p2 = 0
for rep in range(REPS):
    pick = [sqd[c[rng.integers(len(c))]] for c in ks_f]
    v_un = np.array([u["d"] for u in pick]); v_sh = np.array([shuffled_d(u) for u in pick])
    v_sh = np.where(np.isnan(v_sh), v_un, v_sh)
    p2 += order_test(pick, True, 2000, v_un)[0]["p"] < 0.05
    p1 += order_test(pick, True, 2000, v_sh)[0]["p"] < 0.05
# P3: O2 power
fs = [u for u in fsq if not np.isnan(u["d"])]; ks_o2 = keys_for(fs, False); p3 = 0
for rep in range(REPS):
    pick = [sqd[c[rng.integers(len(c))]] for c in ks_o2]
    v = np.array([shuffled_d(u) for u in pick]); v = np.where(np.isnan(v), np.array([u["d"] for u in pick]), v)
    p3 += order_test(pick, False, 2000, v)[0]["p"] < 0.05
# P4: format-composition pseudo-round sets, length-only null
p4 = []
for rep in range(REPS):
    pick = [sqd[c[rng.integers(len(c))]] for c in ks_f]
    p4.append(order_test(pick, False, 2000)[0]["excess"])
R["planted"] = dict(P1_power_shuffled_fmt_matched=p1 / REPS, P2_fp_unshuffled_fmt_matched=p2 / REPS,
                    P3_O2_power=p3 / REPS, P4_format_only_excess_mean=float(np.mean(p4)),
                    P4_ci=[float(np.percentile(p4, 2.5)), float(np.percentile(p4, 97.5))])
log("planted", R["planted"])
R["heldout"]["d"] = [None if np.isnan(u["d"]) else round(float(u["d"]), 3) for u in ho]

# ---------------- verdicts (prereg rules) ----------------
fexists = F["F1_numeral_first"]["p_holm"] < 0.05 and F["F2_opener_first"]["p_holm"] < 0.05
ex = O1f["excess"]; el = O1l["excess"]
if O1f["p"] >= 0.05 and (O1["frac_explained"] or 0) >= 0.5 and R["planted"]["P1_power_shuffled_fmt_matched"] >= 0.8:
    ov = "format explains the off-order"
elif O1f["p"] < 0.05 and el > 0 and ex >= 0.5 * el:
    ov = "format does not explain the off-order"
else:
    ov = "inconclusive"
R["verdict"] = dict(format_exists_discovery=fexists, heldout_can_confirm=R["heldout"]["power_F1"] >= 0.8, order=ov,
                    findspot_effect=("present" if O2["p"] < 0.05 else "not detected" + (", underpowered" if R["planted"]["P3_O2_power"] < 0.8 else "")))
log("verdict", R["verdict"])
R["round_texts"] = [dict(id=u["id"], grp=u["grp"], site=u["site"], L=u["L"], num1=u["num1"], op1=u["op1"], clL=u["clL"],
                         d=None if np.isnan(u["d"]) else round(float(u["d"]), 3), seq=" ".join(u["seq"])) for u in rnd]
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("done")
