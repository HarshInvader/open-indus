"""Confirmatory tests (docs/prereg/numeral_grammar.md).
Usage: .venv/bin/python experiments/numeral_grammar/test.py dev|heldout
'dev' = dry run (fit and score on dev) to check the code; 'heldout' = the registered test."""
import json, math, sys, random
from collections import Counter, defaultdict
sys.path.insert(0, "experiments/numeral_grammar")
from common import *
from models import Fit, MODELS, loglik, scopeB_prob, EPS
from scipy.stats import binomtest, fisher_exact
import numpy as np

mode = sys.argv[1]
dev, ho = dev_heldout(version=2)
OLD_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}


def collect(texts, table, unit_fn):
    out = []
    for t in texts:
        for g in groups_from_runs(t["seq"], table):
            out.append(dict(g=tuple((c, v) for _, c, v in g["group"]), signs=[s for s, _, _ in g["group"]],
                            unit=unit_fn(t), site=t["site"], prev=g["prev"], next=g["next"],
                            text=" ".join(t["seq"])))
    return out


def m77unit(t):
    return {"Mohenjodaro": "M77_MD", "Harappa": "M77_Harappa"}.get(t["site"], "M77_other")


devG = collect(dev, M_NUM, m77unit)
fit = Fit([r["g"] for r in devG])
if mode == "dev":
    testG = devG
    icitG = []
else:
    testG = collect(ho, M_NUM, m77unit)
    icit_new = [t for t in distinct(icit_texts()) if t["site"] not in OLD_ICIT]
    icit_all = distinct(icit_texts())
    icitG = collect(icit_new, W_NUM, lambda t: "ICIT_new")
allG = testG + icitG
UNITS = ["M77_MD", "M77_Harappa", "M77_other", "ICIT_new"]
R = {"mode": mode, "n_groups": len(testG), "n_icit_groups": len(icitG)}
log = []
P = lambda *a: (log.append(" ".join(str(x) for x in a)), print(*a))

# ---------------- inventory of multi-sign groups in the test data
P(f"== mode {mode}: M77 groups {len(testG)} (multi {sum(len(r['g'])>1 for r in testG)}); ICIT-new groups {len(icitG)} (multi {sum(len(r['g'])>1 for r in icitG)})")
for r in allG:
    if len(r["g"]) > 1:
        P("  multi:", key([(s,) + x for s, x in zip(r["signs"], r["g"])]), "|", r["unit"], r["site"], "|", r["text"])

# ---------------- T1
P("\n== T1 held-out log10 likelihood (all groups)")
T1 = {}
for u in ["pooled_M77"] + UNITS:
    gs = [r["g"] for r in (testG if u == "pooled_M77" else [x for x in allG if x["unit"] == u])]
    T1[u] = {m: loglik(fit, m, gs) for m in MODELS}
    T1[u]["n"] = len(gs)
    P(u, "n=", len(gs), {m: round(T1[u][m], 2) for m in MODELS})
lr = lambda u, a, b: T1[u][a] - T1[u][b]
verdict = {}
for m in ["M2a", "M2b", "M3", "M4", "M5"]:
    pooled = lr("pooled_M77", m, "M1")
    units_pos = sum(lr(u, m, "M1") > 0 for u in UNITS if T1[u]["n"] > 0)
    extra = True
    if m in ("M2a", "M2b"):
        extra = lr("pooled_M77", m, "M3") >= 1 and lr("pooled_M77", m, "M4") >= 1
    win = pooled >= 1 and units_pos >= 3 and extra
    verdict[m] = dict(log10LR_vs_M1_pooled=round(pooled, 2), units_LR_gt1=units_pos,
                      per_unit={u: round(lr(u, m, "M1"), 2) for u in UNITS}, win=bool(win),
                      tie=abs(pooled) < 1)
    P(m, "vs M1:", verdict[m])
R["T1"] = dict(loglik=T1, verdict=verdict)
# decomposition: singles vs multi
dec = {}
for m in MODELS:
    dec[m] = dict(single=round(loglik(fit, m, [r["g"] for r in testG if len(r["g"]) == 1]), 2),
                  multi=round(loglik(fit, m, [r["g"] for r in testG if len(r["g"]) > 1]), 2))
P("decomposition (M77 test):", dec); R["T1_decomposition"] = dec

# ---------------- T2 scope B
P("\n== T2 groups containing S12 (k>=2)")
S12 = ("S", 12)
g12 = [r for r in allG if len(r["g"]) >= 2 and S12 in r["g"]]
T2 = {m: sum(math.log10(scopeB_prob(fit, m, r["g"])) for r in g12) for m in ["M1", "M2a", "M2b"]}
T2["n"] = len(g12); T2["groups"] = [key([(s,) + x for s, x in zip(r["signs"], r["g"])]) for r in g12]
P(T2); R["T2"] = T2

# ---------------- P1 order
P("\n== P1 order of 12 + short partner")
p1 = [r["g"] for r in g12 if len(r["g"]) == 2 and r["g"].count(S12) == 1 and all(c == "S" for c, v in r["g"])]
big_first = sum(g[0] == S12 for g in p1)
R["P1"] = dict(n=len(p1), big_first=big_first,
               p_two_sided=binomtest(big_first, len(p1), 0.5).pvalue if p1 else None)
P(R["P1"])

# ---------------- P2 partner set
p2 = [x for r in g12 for x in r["g"] if x != S12]
viol = [x for x in p2 if not (x[0] == "S" and 1 <= x[1] <= 11)]
R["P2"] = dict(partners=[list(x) for x in p2], violations=[list(x) for x in viol], holds=len(viol) == 0)
P("\n== P2", R["P2"])

# ---------------- P3 big single group
if mode == "heldout":
    big = [(r["text"], r["site"]) for r in testG if any(v >= 13 for _, v in r["g"])]
    for t in icit_all:
        for g in groups_from_runs(t["seq"], W_NUM):
            if any(v >= 13 for _, c, v in g["group"]):
                big.append((" ".join(t["seq"]), t["site"] + " " + t.get("type", "")))
    R["P3"] = dict(n_violations=len(big), cases=big, holds=len(big) == 0)
    P("\n== P3", R["P3"])

# ---------------- P4 partner distribution vs standalone
stand = [r["g"][0][1] for r in allG if len(r["g"]) == 1 and r["g"][0][0] == "S"]
part = [x[1] for x in p2 if x[0] == "S" and x[1] != 12]
def chi(a, b):
    vals = sorted(set(a) | set(b)); A = Counter(a); Bc = Counter(b)
    n = len(a) + len(b); s = 0
    for v in vals:
        for grp, cnt in ((A, len(a)), (Bc, len(b))):
            e = (A[v] + Bc[v]) * cnt / n
            s += (grp[v] - e) ** 2 / e if e > 0 else 0
    return s
if part:
    obs = chi(part, stand); pool = part + stand; rng = random.Random(1); k = 0
    for _ in range(10000):
        rng.shuffle(pool)
        if chi(pool[:len(part)], pool[len(part):]) >= obs - 1e-12: k += 1
    R["P4"] = dict(partners=Counter(part), standalone=Counter(stand), p=(k + 1) / 10001)
else:
    R["P4"] = dict(partners={}, p=None, note="no short partners of 12")
P("\n== P4", R["P4"])

# ---------------- P5 additivity: short+short pairs without 12, sum <= 12
p5 = [r for r in allG if len(r["g"]) == 2 and all(c == "S" for c, v in r["g"]) and S12 not in r["g"]
      and sum(v for c, v in r["g"]) <= 12]
R["P5"] = dict(n=len(p5), groups=[key([(s,) + x for s, x in zip(r["signs"], r["g"])]) for r in p5],
               holds=len(p5) <= 1)
P("\n== P5", R["P5"])

# ---------------- P6 short-1 prefix
S1 = ("S", 1)
p6 = [r["g"] for r in allG if len(r["g"]) == 2 and r["g"].count(S1) == 1]
first = sum(g[0] == S1 for g in p6)
pair_tok = [t for r in allG if len(r["g"]) == 2 for t in r["g"]]
single_tok = [r["g"][0] for r in allG if len(r["g"]) == 1]
a = sum(t == S1 for t in pair_tok); b = len(pair_tok) - a
c = sum(t == S1 for t in single_tok); d = len(single_tok) - c
R["P6"] = dict(n=len(p6), s1_first=first,
               p_order=binomtest(first, len(p6), 0.5, alternative="greater").pvalue if p6 else None,
               s1_share_pairs=a / max(1, a + b), s1_share_singles=c / max(1, c + d),
               p_share=fisher_exact([[a, b], [c, d]], alternative="greater")[1])
R["P6"]["holds"] = bool(p6) and first / len(p6) >= 0.75 and R["P6"]["p_order"] < 0.05 and R["P6"]["p_share"] < 0.05
P("\n== P6", R["P6"])

# ---------------- C1 cross-class order
cc = [r["g"] for r in allG if len(r["g"]) == 2 and {r["g"][0][0], r["g"][1][0]} == {"S", "T"}]
tf = sum(g[0][0] == "T" for g in cc)
R["C1"] = dict(n=len(cc), tall_first=tf, p=binomtest(tf, len(cc), 0.5).pvalue if cc else None,
               fixed=bool(cc) and max(tf, len(cc) - tf) / len(cc) >= 0.8 and binomtest(tf, len(cc), 0.5).pvalue < 0.05,
               pairs=Counter(key([("",) + x for x in g]) for g in cc))
P("\n== C1", R["C1"])

# ---------------- C2 numeral-bound signs (list from dev)
def prec_stats(texts, table):
    tot = Counter(); num = Counter()
    for t in texts:
        for rr in runs(t["seq"]):
            for i, s in enumerate(rr):
                if s in table and table[s][0] != "C":
                    continue
                if i == 0:
                    continue
                tot[s] += 1
                p = rr[i - 1]
                if p in table and table[p][0] != "C":
                    num[s] += 1
    return tot, num
dt, dn = prec_stats(dev, M_NUM)
listed = sorted([s for s in dt if dt[s] >= 6 and dn[s] / dt[s] >= 0.5], key=lambda s: -dn[s] / dt[s])
R["C2_dev_list"] = {s: f"{dn[s]}/{dt[s]}" for s in listed}
P("\n== C2 dev list", R["C2_dev_list"])
tt, tn = (prec_stats(ho, M_NUM) if mode == "heldout" else (dt, dn))
base = sum(tn.values()) / sum(tt.values())
chk = {s: (tn[s], tt[s]) for s in listed if tt[s] >= 3}
kk = sum(v[0] for v in chk.values()); nn = sum(v[1] for v in chk.values())
R["C2"] = dict(checked={s: f"{a}/{b}" for s, (a, b) in chk.items()}, pooled=f"{kk}/{nn}", base_rate=base,
               p=binomtest(kk, nn, base, alternative="greater").pvalue if nn else None,
               each_ge_half=sum(a / b >= 0.5 for a, b in chk.values()), n_checked=len(chk))
P("== C2 test", R["C2"])

# ---------------- power by simulation (T1 M2 vs M1 and T2), under fitted M2b and M2a
def sample_from(model, k=2, rng=None):
    cells = fit.allowed_cells(model, k)
    from models import dirichlet
    d = dirichlet(fit.pairs, cells)
    if rng.random() < EPS:
        toks = list(fit.B); w = [fit.B[t] for t in toks]
        return tuple(rng.choices(toks, w, k=k))
    return rng.choices(cells, [d[c] for c in cells])[0]
rng = random.Random(7)
pw = {}
nmulti = {u: sum(len(r["g"]) > 1 for r in allG if r["unit"] == u) for u in UNITS}
n12 = max(1, len(g12))
for m in ["M2a", "M2b"]:
    hits = 0; hitsB = 0
    for _ in range(2000):
        pooled = 0; pos = 0
        for u in UNITS:
            gs = [sample_from(m, 2, rng) for _ in range(nmulti[u])]
            l = sum(math.log10(fit.prob(m, g)) - math.log10(fit.prob("M1", g)) for g in gs)
            if u != "ICIT_new":
                pooled += l
            pos += l > 0
        hits += pooled >= 1 and pos >= 3
        gs = []
        while len(gs) < n12:
            g = sample_from(m, 2, rng)
            if S12 in g:
                gs.append(g)
        lB = sum(math.log10(scopeB_prob(fit, m, g)) - math.log10(scopeB_prob(fit, "M1", g)) for g in gs)
        hitsB += lB >= 1
    pw[m] = dict(T1_power=hits / 2000, T2_power_at_n12=hitsB / 2000, n_multi=nmulti, n12=n12)
# P1 power: if true order share is 0.9, chance to reject 0.5 at observed n
n1 = max(1, R["P1"]["n"])
pw["P1_power_true0.9"] = float(np.mean([binomtest(np.random.default_rng(i).binomial(n1, 0.9), n1, 0.5).pvalue < 0.05 for i in range(2000)]))
R["power"] = pw
P("\n== power", pw)

out = f"experiments/numeral_grammar/test_{mode}.json"
json.dump(R, open(out, "w"), indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o))
open(f"experiments/numeral_grammar/test_{mode}.log", "w").write("\n".join(log))
