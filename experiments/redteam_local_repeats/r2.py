"""R2: 'texts grow, never shrink' (R2a) and 'not local' (R2b).
usage: .venv/bin/python experiments/redteam_local_repeats/r2.py [nsim_generative]
"""
import sys, os, json, itertools
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import fisher_exact, binom

NGEN = int(sys.argv[1]) if len(sys.argv) > 1 else 300
sys.argv = sys.argv[:1] + ["10"]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from rlib import *  # noqa
import c1, lr  # noqa
from id_lib import flat  # noqa

rng = np.random.default_rng(314)
out = {}
SEALS, cnt = lr.SEALS, lr.cnt

# ---------------------------------------------------------------- R2a-0 reproduce
out["R2a0_reproduce"] = lr.T["T5_extension"]; print("R2a0", out["R2a0_reproduce"]["all"])

# per (text, site) unit
site_of = defaultdict(set)
for o in SEALS: site_of[o["text"]].add(o["site"])
units = []
for t, n in cnt.items():
    if len(t) < 4: continue
    for s in sorted(site_of[t]):
        units.append(dict(text=t, site=s, rep=n >= 2, L=len(t), longer=bool(lr.longer_variants(t, s)),
                          shorter=lr.shorter_exists(t, s), n_sites=len(site_of[t])))
ru = [u for u in units if u["rep"]]; su = [u for u in units if not u["rep"]]
tab = [[sum(u["longer"] for u in ru), len(ru) - sum(u["longer"] for u in ru)], [sum(u["longer"] for u in su), len(su) - sum(u["longer"] for u in su)]]
out["R2a1_units"] = dict(rep_units=len(ru), rep_longer=tab[0][0], single_units=len(su), single_longer=tab[1][0],
                         p_fisher=float(fisher_exact(tab, alternative="greater")[1]),
                         rep_shorter=sum(u["shorter"] for u in ru), single_shorter=sum(u["shorter"] for u in su),
                         rep_unit_hits=[(" ".join(u["text"]), u["site"]) for u in ru if u["longer"]])
print("R2a1", out["R2a1_units"])

# ---------------------------------------------------------------- R2a-2 commonness-matched controls
D_all = c1.distinct_corpus(c1.ALL); V = sorted({s for t in D_all for s in t})
g = c1.Bigram(D_all, V); g.prepare(60)
for u in units: u["comm"] = bigram_logp(g, u["text"], cond=True) / u["L"]
fams = sorted({u["text"] for u in ru})
ctrl = {}
for u in ru:
    pool = [v for v in su if v["L"] == u["L"] and v["site"] == u["site"]]
    if len(pool) < 10: pool = [v for v in su if v["L"] == u["L"]]
    pool = sorted(pool, key=lambda v: abs(v["comm"] - u["comm"]))[:10]
    ctrl[(u["text"], u["site"])] = pool
NDRAW = 10000
res_l, res_s = [], []
for _ in range(NDRAW):
    hl = hs = 0
    for t in fams:
        us = [u for u in ru if u["text"] == t]
        picks = [ctrl[(u["text"], u["site"])][rng.integers(10)] for u in us]
        hl += any(p["longer"] for p in picks); hs += any(p["shorter"] for p in picks)
    res_l.append(hl); res_s.append(hs)
res_l, res_s = np.array(res_l), np.array(res_s)
ctrl_short_rate = res_s.mean() / len(fams)
out["R2a2_matched"] = dict(obs_longer=6, null_longer=summ(res_l, 6), obs_shorter=0,
                           null_shorter=dict(mean=float(res_s.mean()), p_le0=float((res_s <= 0).mean())),
                           control_family_shorter_rate=float(ctrl_short_rate),
                           P0_of_15_shorter_binomial=float(binom.pmf(0, len(fams), ctrl_short_rate)),
                           P0_of_15_shorter_singleton_rate=float(binom.pmf(0, 15, 37 / 1017)),
                           rep_comm_mean=float(np.mean([u["comm"] for u in ru])), single_comm_mean=float(np.mean([u["comm"] for u in su])),
                           control_comm_mean=float(np.mean([v["comm"] for p in ctrl.values() for v in p])),
                           control_longer_unit_rate=float(np.mean([v["longer"] for p in ctrl.values() for v in p])))
print("R2a2", out["R2a2_matched"])

# Mantel-Haenszel by length x site group x commonness tertile, permutation within strata
tert = np.percentile([u["comm"] for u in units], [33.3, 66.7])
def stratum(u):
    sg = u["site"] if u["site"] in ("Mohenjo-daro", "Harappa") else "other"
    return (min(u["L"], 6), sg, int(np.searchsorted(tert, u["comm"])))
S = defaultdict(list)
for u in units: S[stratum(u)].append(u)
def mh(lab):
    num = den = 0.0
    for k, us in S.items():
        n = len(us)
        if n < 2: continue
        a = sum(1 for u, r in zip(us, lab[k]) if r and u["longer"]); b = sum(1 for u, r in zip(us, lab[k]) if r and not u["longer"])
        c = sum(1 for u, r in zip(us, lab[k]) if not r and u["longer"]); d = sum(1 for u, r in zip(us, lab[k]) if not r and not u["longer"])
        num += a * d / n; den += b * c / n
    return num / den if den > 0 else np.inf
lab0 = {k: [u["rep"] for u in us] for k, us in S.items()}
obs_mh = mh(lab0); nullmh = []
for _ in range(5000):
    nullmh.append(mh({k: list(rng.permutation(v)) for k, v in lab0.items()}))
nullmh = np.array(nullmh)
exp_hits = sum(sum(u["longer"] for u in us) / len(us) * sum(u["rep"] for u in us) for us in S.values())
out["R2a2_MH"] = dict(OR_MH=float(obs_mh), p_perm=float((1 + (nullmh >= obs_mh).sum()) / (len(nullmh) + 1)),
                      rep_unit_hits_obs=tab[0][0], rep_unit_hits_expected_within_strata=float(exp_hits))
print("R2a2 MH", out["R2a2_MH"])

# ---------------------------------------------------------------- R2a-3 generative null
ALLC = lr.ALLC
lens = [len(o["text"]) for o in ALLC]; sites = [o["site"] for o in ALLC]; isseal = [o["cls"] == "seal" for o in ALLC]


def growth_stats(T):
    have = set(zip(sites, T)); has_longer = set()
    for s, u in zip(sites, T):
        if len(u) >= 5:
            for i in range(len(u)): has_longer.add((s, u[:i] + u[i + 1:]))
    c = Counter(t for t, k in zip(T, isseal) if k and len(t) >= 4); ss = defaultdict(set)
    for t, k, s in zip(T, isseal, sites):
        if k and len(t) >= 4: ss[t].add(s)
    r = dict(rep_n=0, rep_l=0, rep_s=0, sin_n=0, sin_l=0, sin_s=0)
    for t, n in c.items():
        lg = any((s, t) in has_longer for s in ss[t])
        sh = any((s, t[:i] + t[i + 1:]) in have for s in ss[t] for i in range(len(t)))
        k = "rep" if n >= 2 else "sin"
        r[k + "_n"] += 1; r[k + "_l"] += lg; r[k + "_s"] += sh
    return r


obsg = growth_stats([o["text"] for o in ALLC]); out["R2a3_observed"] = obsg; print("R2a3 obs", obsg)
tri = Trigram(D_all, V)
for name, m in (("N2", g), ("TRI-A", tri)):
    R = [growth_stats(m.sample(lens, rng)) for _ in range(NGEN)]
    tot = {k: sum(r[k] for r in R) for k in R[0]}
    rep_share = tot["rep_l"] / max(tot["rep_n"], 1); sin_share = tot["sin_l"] / tot["sin_n"]
    out["R2a3_" + name] = dict(pooled=tot, rep_longer_share=rep_share, single_longer_share=sin_share,
                               rep_shorter_share=tot["rep_s"] / max(tot["rep_n"], 1), single_shorter_share=tot["sin_s"] / tot["sin_n"],
                               ratio_rep_over_single=rep_share / sin_share if sin_share else None,
                               binom_p_obs6of15=float(binom.sf(5, 15, rep_share)),
                               mean_rep_families_per_sim=tot["rep_n"] / NGEN)
    print("R2a3", name, out["R2a3_" + name], flush=True)

# ---------------------------------------------------------------- R2b locality variants
L4 = [o for o in SEALS if len(o["text"]) >= 4]; site_arr = np.array([o["site"] for o in L4])
F = lr.families
FORM = {f["text"] for f in F if is_formula(tuple(f["text"].split()))}
FLAG = {"W176 W740 W400 W033 W700", "W820 W002 W003 W390", "W861 W002 W016 W390", "W817 W002 W004 W390"}


def loc_stats(fs, site_lists):
    pairs_same = pairs = 0; fam_shares = []
    for f, sl in zip(fs, site_lists):
        ps = [a == b for a, b in itertools.combinations(sl, 2)]
        pairs_same += sum(ps); pairs += len(ps); fam_shares.append(np.mean(ps))
    return pairs_same / pairs, float(np.mean(fam_shares))


def loc_test(fs, NP=10000):
    obs = loc_stats(fs, [[o["site"] for o in f["objects"]] for f in fs])
    sizes = [f["n"] for f in fs]; N1, N2_ = [], []
    for _ in range(NP):
        perm = rng.permutation(site_arr)[:sum(sizes)]; k = 0; sl = []
        for n in sizes: sl.append(list(perm[k:k + n])); k += n
        a, b = loc_stats(fs, sl); N1.append(a); N2_.append(b)
    N1, N2_ = np.array(N1), np.array(N2_)
    return dict(n_families=len(fs), n_pairs=sum(n * (n - 1) // 2 for n in sizes),
                pair_share=obs[0], pair_null=float(N1.mean()), pair_p_more_local=float((1 + (N1 >= obs[0]).sum()) / (NP + 1)),
                fam_share=obs[1], fam_null=float(N2_.mean()), fam_p_more_local=float((1 + (N2_ >= obs[1]).sum()) / (NP + 1)))


variants = {"V1V2_all": F, "V3_nonformula": [f for f in F if f["text"] not in FORM], "V3b_formula_only": [f for f in F if f["text"] in FORM],
            "V4_drop_flagged": [f for f in F if f["text"] not in FLAG], "V5_band45": [f for f in F if f["band"] == "4-5"],
            "V5b_band45_nonformula": [f for f in F if f["band"] == "4-5" and f["text"] not in FORM]}
R2b = {k: loc_test(v) for k, v in variants.items()}
for k, v in R2b.items(): print("R2b", k, v)
# V6 between/within per-possible-pair ratio, family bootstrap
ns = Counter(site_arr); n = len(site_arr); poss_w = sum(v * (v - 1) / 2 for v in ns.values()); poss_b = n * (n - 1) / 2 - poss_w
def ratio(fs):
    w = b = 0
    for f in fs:
        for x, y in itertools.combinations([o["site"] for o in f["objects"]], 2):
            if x == y: w += 1
            else: b += 1
    return (b / poss_b) / (w / poss_w) if w else np.inf
for nm, fs in (("all", F), ("nonformula", variants["V3_nonformula"])):
    bs = [ratio([fs[i] for i in rng.integers(0, len(fs), len(fs))]) for _ in range(5000)]
    bs = np.array(bs); fin = bs[np.isfinite(bs)]
    R2b["V6_ratio_" + nm] = dict(ratio=ratio(fs), ci=[float(np.percentile(fin, 2.5)), float(np.percentile(fin, 97.5))], share_inf=float(np.mean(~np.isfinite(bs))))
    print("R2b V6", nm, R2b["V6_ratio_" + nm])
# site composition of non-formula same-text pairs
R2b["nonformula_pairs_by_site_pair"] = Counter(" / ".join(sorted((a["site"], b["site"]))) for f in variants["V3_nonformula"]
                                               for a, b in itertools.combinations(f["objects"], 2))
print(R2b["nonformula_pairs_by_site_pair"])
out["R2b"] = R2b
json.dump(out, open(os.path.join(HERE, "r2.json"), "w"), indent=1, default=lambda x: dict(x) if isinstance(x, Counter) else str(x))
