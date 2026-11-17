"""T4: what drops when space is tight (square steatite seals, ICIT). Pre-registered in
docs/prereg/space_and_sealing.md. Run: .venv/bin/python experiments/space_and_sealing/t4_space.py
Writes t4.json and t4.log (stdout)."""
import json, sys, math
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sas_lib import (t4_table, CLASSES, PRIMARY_T4, FRAME, NUMERAL, icit_texts, nsigns, signs, norm,
                     classes_of, HERE, ROOT)
sys.path.insert(0, str(ROOT))
from corpus.build import _close  # noqa: E402

NPERM = 10000
RNG = np.random.default_rng(20261115)
OUT = {}


def strata_perms(strata, nperm, rng):
    """Return index array (nperm x n) permuting positions within strata."""
    n = len(strata)
    groups = defaultdict(list)
    for i, s in enumerate(strata):
        groups[s].append(i)
    P = np.tile(np.arange(n), (nperm, 1))
    for idx in groups.values():
        idx = np.array(idx)
        if len(idx) < 2:
            continue
        sub = np.argsort(rng.random((nperm, len(idx))), axis=1)
        P[:, idx] = idx[sub]
    return P


def center_within(x, strata):
    x = np.asarray(x, float).copy()
    g = defaultdict(list)
    for i, s in enumerate(strata):
        g[s].append(i)
    for idx in g.values():
        x[idx] -= x[idx].mean()
    return x


def keep_multi(rows, key="stratum"):
    c = Counter(r[key] for r in rows)
    return [r for r in rows if c[r[key]] >= 2]


def slope_test(rows, Y, nperm=NPERM, strata_key="stratum", rng=RNG):
    """Within-stratum slope of each column of Y on log area; permutation null (area
    permuted within strata). Returns slopes, null SD, two-sided p, one-sided p (pos/neg)."""
    strata = [r[strata_key] for r in rows]
    x = center_within([r["log_area"] for r in rows], strata)
    Y = np.asarray(Y, float)
    Yc = Y - Y.mean(0)
    sxx = (x ** 2).sum()
    obs = x @ Yc / sxx
    P = strata_perms(strata, nperm, rng)
    null = (x[P] @ Yc) / sxx           # nperm x k
    sd = null.std(0)
    p2 = ((np.abs(null) >= np.abs(obs) - 1e-12).sum(0) + 1) / (nperm + 1)
    ppos = ((null >= obs - 1e-12).sum(0) + 1) / (nperm + 1)
    pneg = ((null <= obs + 1e-12).sum(0) + 1) / (nperm + 1)
    return obs, sd, p2, ppos, pneg, null


def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


def class_matrix(rows, kind="share"):
    Y = []
    for r in rows:
        c = r["cls"]
        if kind == "share":
            Y.append([c[k] / r["length"] for k in PRIMARY_T4])
        else:
            Y.append([1.0 if c[k] > 0 else 0.0 for k in PRIMARY_T4])
    return np.array(Y)


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------
R0 = t4_table(require_complete=True)
R = keep_multi(R0)
log(f"T4 table: {len(R0)} distinct complete texts; {len(R)} in strata with >=2 texts "
    f"({len({r['stratum'] for r in R})} site|period strata)")
OUT["n_texts"] = len(R); OUT["n_strata"] = len({r["stratum"] for r in R})
LN2 = math.log(2)

# descriptive: class presence by area tercile (within-stratum centred)
xc = center_within([r["log_area"] for r in R], [r["stratum"] for r in R])
q = np.quantile(xc, [1 / 3, 2 / 3])
terc = np.digitize(xc, q)
desc = {}
for k in PRIMARY_T4 + ["core"]:
    desc[k] = [round(float(np.mean([r["cls"][k] > 0 for r, t in zip(R, terc) if t == j])), 3) for j in range(3)]
desc["mean_length"] = [round(float(np.mean([r["length"] for r, t in zip(R, terc) if t == j])), 2) for j in range(3)]
OUT["presence_by_area_tercile"] = desc
log("presence by within-stratum area tercile (small, mid, large):")
for k, v in desc.items():
    log(f"  {k:13s} {v}")

# P1 positive control: length vs area
obs, sd, p2, ppos, pneg, _ = slope_test(R, np.array([[r["length"]] for r in R]))
OUT["P1_length_vs_area"] = dict(slope_signs_per_log_area=float(obs[0]), signs_per_doubling=float(obs[0] * LN2),
                                null_sd=float(sd[0]), p_one_sided=float(ppos[0]))
log(f"\nP1 length ~ log area: {obs[0]*LN2:+.2f} signs per doubling of area, one-sided p={ppos[0]:.4g}")

# P2 primary: class token share vs area (departure from uniform thinning)
Ys = class_matrix(R, "share")
obs, sd, p2, ppos, pneg, nullS = slope_test(R, Ys)
ph = holm(p2)
P2 = {}
log("\nP2 class token share ~ log area (slope per doubling; + = share grows with space = dropped first on small seals)")
for i, k in enumerate(PRIMARY_T4):
    P2[k] = dict(slope_per_doubling=float(obs[i] * LN2), null_sd_per_doubling=float(sd[i] * LN2),
                 mde80_per_doubling=float(2.8 * sd[i] * LN2), mean_share=float(Ys[:, i].mean()),
                 p_two_sided=float(p2[i]), p_holm=float(ph[i]),
                 verdict=("dropped first" if obs[i] > 0 else "kept (core-like)") if ph[i] < 0.05 else "no departure")
    log(f"  {k:13s} share {Ys[:, i].mean():.3f}  slope {obs[i]*LN2:+.4f}/doubling  MDE {2.8*sd[i]*LN2:.4f}  "
        f"p={p2[i]:.4g} Holm={ph[i]:.4g}  -> {P2[k]['verdict']}")
OUT["P2_share_slopes"] = P2
order = sorted(PRIMARY_T4, key=lambda k: -P2[k]["slope_per_doubling"])
OUT["P2_omission_order_dropped_first_to_kept"] = order
log("  omission order (dropped first -> kept):", " > ".join(order))

# secondary: presence (total effect) vs area
Yp = class_matrix(R, "presence")
obsP, sdP, p2P, _, _, _ = slope_test(R, Yp)
OUT["S_presence_slopes"] = {k: dict(slope_per_doubling=float(obsP[i] * LN2), p_two_sided=float(p2P[i]),
                                    mde80=float(2.8 * sdP[i] * LN2)) for i, k in enumerate(PRIMARY_T4)}
log("\nsecondary: presence ~ log area (change in P(present) per doubling)")
for i, k in enumerate(PRIMARY_T4):
    log(f"  {k:13s} {obsP[i]*LN2:+.3f}  p={p2P[i]:.4g}  MDE {2.8*sdP[i]*LN2:.3f}")


# P3 replication of the order: catalogue vs metric sites; family halves A vs B
def rho(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).correlation)


def split_rep(predA, predB, label, nperm=2000):
    RA = keep_multi([r for r in R if predA(r)]); RB = keep_multi([r for r in R if predB(r)])
    YA, YB = class_matrix(RA), class_matrix(RB)
    oA, _, _, _, _, nA = slope_test(RA, YA, nperm=nperm)
    oB, _, _, _, _, nB = slope_test(RB, YB, nperm=nperm)
    r_obs = rho(oA, oB)
    r_null = np.array([rho(nA[i], nB[i]) for i in range(nperm)])
    p = float(((r_null >= r_obs).sum() + 1) / (nperm + 1))
    log(f"  {label}: nA={len(RA)} nB={len(RB)} rho={r_obs:+.2f} p={p:.4g}")
    log("    A slopes/doubling:", {k: round(float(v * LN2), 4) for k, v in zip(PRIMARY_T4, oA)})
    log("    B slopes/doubling:", {k: round(float(v * LN2), 4) for k, v in zip(PRIMARY_T4, oB)})
    return dict(nA=len(RA), nB=len(RB), rho=r_obs, p=p,
                slopesA={k: float(v * LN2) for k, v in zip(PRIMARY_T4, oA)},
                slopesB={k: float(v * LN2) for k, v in zip(PRIMARY_T4, oB)})


log("\nP3 order replication (Spearman of 8 class slopes between halves; null: area permuted in both)")
P3 = dict(catalogue_vs_metric=split_rep(lambda r: r["catalogue"], lambda r: not r["catalogue"], "catalogue vs metric"),
          family_halves=split_rep(lambda r: r["half"] == "A", lambda r: r["half"] == "B", "family half A vs B"))
P3["pass"] = bool(all(P3[k]["rho"] >= 0.5 and P3[k]["p"] < 0.05 for k in ["catalogue_vs_metric", "family_halves"]))
OUT["P3_order_replication"] = P3
log("  P3 pass:", P3["pass"])

# ---------------- P4/P5: containment ----------------
# reference pool: distinct complete texts on any seal type (SEAL*), normalised, any site
pool = {}
for t in icit_texts():
    if not t["type"].startswith("SEAL") or "#" in t["seq"] or not t["complete"]:
        continue
    sg = tuple(nsigns(t["seq"]))
    if sg:
        pool[sg] = 1
pool = list(pool)
by_len = defaultdict(list)
for sg in pool:
    by_len[len(sg)].append(sg)


def is_subseq(a, b):
    it = iter(b)
    return all(x in it for x in a)


INV = defaultdict(set)
for i, sg in enumerate(pool):
    for x in set(sg):
        INV[x].add(i)
_CACHE = {}


def containers(sg):
    n = len(sg)
    cand = set.intersection(*(INV.get(x, set()) for x in set(sg)))
    return [pool[i] for i in cand if len(pool[i]) > n and is_subseq(sg, pool[i])]


def contained(sg):
    if sg not in _CACHE:
        _CACHE[sg] = bool(containers(sg))
    return _CACHE[sg]


short = [r for r in R if r["length"] <= 3]
obs_c = np.array([contained(tuple(r["signs"])) for r in short])
rate = float(obs_c.mean())
# null: core signs replaced by frequency-matched random core signs (10 frequency bins)
core_tok = Counter(s for sg in pool for s in sg if s not in FRAME and s not in NUMERAL)
types = sorted(core_tok, key=lambda s: core_tok[s])
bins = np.array_split(np.array(types), 10)
bin_of = {s: i for i, b in enumerate(bins) for s in b}
NNULL = 1000
rng2 = np.random.default_rng(7)
null_rates = []
for _ in range(NNULL):
    hits = 0
    for r in short:
        sg = tuple(rng2.choice(bins[bin_of[s]]) if s in bin_of else s for s in r["signs"])
        hits += contained(sg)
    null_rates.append(hits / len(short))
null_rates = np.array(null_rates)
p4 = float(((null_rates >= rate).sum() + 1) / (NNULL + 1))
OUT["P4_containment"] = dict(n_short=len(short), rate=rate, null_mean=float(null_rates.mean()),
                             null_p95=float(np.quantile(null_rates, 0.95)), p_one_sided=p4,
                             by_length={L: dict(n=int(sum(1 for r in short if r["length"] == L)),
                                                rate=float(np.mean([c for r, c in zip(short, obs_c) if r["length"] == L])))
                                        for L in (1, 2, 3)})
log(f"\nP4 containment: {obs_c.sum()}/{len(short)} short texts (1-3 signs) are ordered subsets of a longer seal text "
    f"= {rate:.3f}; frequency-matched core-swap null {null_rates.mean():.3f} (95th pct {np.quantile(null_rates,0.95):.3f}); p={p4:.4g}")

# what the longer versions add (shortest containers), vs container composition
CL = PRIMARY_T4 + ["core"]
add_ct, exp_ct = Counter(), Counter()
per_text = []
for r, c in zip(short, obs_c):
    if not c:
        continue
    cs = containers(tuple(r["signs"]))
    m = min(len(b) for b in cs)
    cs = [b for b in cs if len(b) == m]
    a_t, e_t = Counter(), Counter()
    for b in cs:
        rem = list(b)
        for s in r["signs"]:
            rem.remove(s)
        ca, cb = classes_of(rem), classes_of(list(b))
        for k in CL:
            a_t[k] += ca[k] / len(rem) / len(cs)
            e_t[k] += cb[k] / len(b) / len(cs)
    per_text.append((a_t, e_t))
    add_ct.update(a_t); exp_ct.update(e_t)
ratios = {}
bs = []
rng3 = np.random.default_rng(11)
for _ in range(2000):
    idx = rng3.integers(0, len(per_text), len(per_text))
    A, E = Counter(), Counter()
    for i in idx:
        A.update(per_text[i][0]); E.update(per_text[i][1])
    bs.append({k: (A[k] / E[k]) if E[k] else np.nan for k in CL})
for k in CL:
    v = np.array([b[k] for b in bs], float)
    ratios[k] = dict(added_share=add_ct[k] / len(per_text), container_share=exp_ct[k] / len(per_text),
                     ratio=(add_ct[k] / exp_ct[k]) if exp_ct[k] else None,
                     ci95=[float(np.nanquantile(v, 0.025)), float(np.nanquantile(v, 0.975))])
OUT["P4b_added_by_longer_versions"] = ratios
log("  signs that the shortest longer version adds, by class (ratio >1 = added more than its share = optional):")
for k in CL:
    rr = ratios[k]
    log(f"    {k:13s} added {rr['added_share']:.3f} vs container {rr['container_share']:.3f}  ratio "
        f"{rr['ratio'] if rr['ratio'] is None else round(rr['ratio'], 2)}  CI {rr['ci95'][0]:.2f}-{rr['ci95'][1]:.2f}")

# P5: area beyond length: are short texts on small seals contained more often?
for r, c in zip(short, obs_c):
    r["contained"] = float(c); r["sl"] = f"{r['site']}#{r['length']}"
S5 = keep_multi(short, "sl")
o5, sd5, _, ppos5, pneg5, _ = slope_test(S5, np.array([[r["contained"]] for r in S5]), strata_key="sl")
OUT["P5_containment_vs_area"] = dict(n=len(S5), slope_per_doubling=float(o5[0] * LN2), p_one_sided_negative=float(pneg5[0]),
                                     mde80=float(2.8 * sd5[0] * LN2))
log(f"\nP5 contained ~ log area within site x length (n={len(S5)}): {o5[0]*LN2:+.3f} per doubling, "
    f"one-sided p (smaller seals more contained) = {pneg5[0]:.4g}; MDE {2.8*sd5[0]*LN2:.3f}")

# ---------------- sensitivities for P2 (reported, not decisive) ----------------
log("\nSensitivities for P2 (slope per doubling; two-sided p, 4000 perms)")
SENS = {}


def p2_on(rows, label, recompute=None):
    rows = keep_multi(rows)
    if recompute:
        for r in rows:
            r = recompute(r)
    Y = class_matrix(rows)
    o, sd, p, _, _, _ = slope_test(rows, Y, nperm=4000)
    SENS[label] = dict(n=len(rows), slopes={k: float(v * LN2) for k, v in zip(PRIMARY_T4, o)},
                       p={k: float(v) for k, v in zip(PRIMARY_T4, p)})
    log(f"  {label} (n={len(rows)}): " + ", ".join(f"{k} {v*LN2:+.4f} (p={pp:.3g})" for k, v, pp in zip(PRIMARY_T4, o, p)))


# s1 drop texts with the size-tracking carving variants (raw W706, W742, W745)
p2_on([r for r in R if not any(s in r["seq"] for s in ("W706", "W742", "W745"))], "s1_no_W706_W742_W745")
# s2 one text per family (families: <=1 edit or contained copy)
keys = [tuple(r["signs"]) for r in R]
parent = list(range(len(R)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i


for i in range(len(R)):
    for j in range(i + 1, len(R)):
        if _close(list(keys[i]), list(keys[j])):
            parent[find(i)] = find(j)
seen, fam_rows = set(), []
for i, r in enumerate(R):
    f = find(i)
    if f not in seen:
        seen.add(f); fam_rows.append(r)
p2_on(fam_rows, "s2_one_text_per_family")
# s3 metric sites only, catalogue only
p2_on([r for r in R if not r["catalogue"]], "s3_metric_sites")
p2_on([r for r in R if r["catalogue"]], "s3_catalogue_sites")
# s4 site-only strata (period ignored)
Rs = [dict(r, stratum=r["site"]) for r in R0]
p2_on(Rs, "s4_site_only_strata")
# s5 single-line texts only (line breaks alter layout)
p2_on([r for r in R if r["n_lines"] == 1], "s5_single_line")
# s6 leave-one-sign-out within each class: max |change| of the slope
loo = {}
base = {k: P2[k]["slope_per_doubling"] for k in PRIMARY_T4}
for k in PRIMARY_T4:
    worst = (None, 0.0, base[k])
    for s in sorted(CLASSES[k]):
        if not any(s in r["signs"] for r in R):
            continue
        Y = np.array([[sum(1 for x in r["signs"] if x in CLASSES[k] and x != s) / r["length"]] for r in R])
        o, _, _, _, _, _ = slope_test(R, Y, nperm=10)
        d = o[0] * LN2 - base[k]
        if abs(d) > abs(worst[1]):
            worst = (s, float(d), float(o[0] * LN2))
    loo[k] = dict(sign=worst[0], change=worst[1], slope_without=worst[2])
SENS["s6_leave_one_sign_out"] = loo
log("  s6 leave-one-sign-out (largest change):", {k: (v["sign"], round(v["change"], 4)) for k, v in loo.items()})
OUT["sensitivity"] = SENS

json.dump(OUT, open(HERE / "t4.json", "w"), indent=1, default=float)
