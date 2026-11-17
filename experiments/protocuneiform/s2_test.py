"""Confirmatory test (run once after the freeze): do Indus look-alikes of proto-cuneiform / Proto-Elamite
signs share the function of the sign they resemble?  Pre-registered in docs/prereg/protocuneiform.md.

Run: .venv/bin/python -I experiments/protocuneiform/s2_test.py
Writes: test_results.json (+ prints a log)
"""
import json, sys, collections
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr, rankdata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout  # noqa: E402

NPERM = 10000
MIN_OCC = 3
rng = np.random.default_rng(7)

frozen = json.load(open(HERE / "frozen_pairs.json"))
pcpool = json.load(open(HERE / "pc_pool.json"))
pepool = json.load(open(HERE / "pe_pool.json"))
PCK = sorted(pcpool); PEK = sorted(pepool)
COMMODITY = {"GRAIN_FOOD", "LIQUID_DAIRY", "VESSEL", "TEXTILE", "LIVESTOCK", "OTHER_GOODS"}

# Indus numerals: functional_reading lexicon roles NUMERAL(short) / NUMERAL(tall)
import csv
NUMERALS = set()
for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
    if r["kind"] == "sign" and "NUMERAL" in r["roles"]:
        NUMERALS.add(r["item"])

bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in bridge.items() if v["M"]}


def icit_set():
    out, seen = [], set()
    for t in icit_texts():
        seq = [s if s in ("|", "#") else W2M.get(s, "OOV") for s in t["seq"]]
        k = " ".join(seq)
        if k in seen:
            continue
        seen.add(k); out.append({"seq": seq})
    return out


def signatures(texts):
    """Per sign: AN = share of occurrences directly preceded (same run) by a numeral;
    INIT = share of occurrences that are the first sign of the text; END2 = share in the last two
    positions of the text (texts ending in a break excluded from END2/INIT denominators accordingly)."""
    occ = collections.Counter(); an = collections.Counter(); ini = collections.Counter(); end2 = collections.Counter()
    for t in texts:
        seq = t["seq"]
        flat = [s for s in seq if s != "|"]
        prev = None
        for idx, s in enumerate(flat):
            if s == "#":
                prev = None; continue
            occ[s] += 1
            if prev in NUMERALS:
                an[s] += 1
            if idx == 0:
                ini[s] += 1
            if flat[-1] != "#" and idx >= len(flat) - 2:
                end2[s] += 1
            prev = s
    return {s: {"n": n, "AN": an[s] / n, "INIT": ini[s] / n, "END2": end2[s] / n} for s, n in occ.items()}


def targets(lookset, sig):
    return [s for s in lookset if s not in NUMERALS and s in sig and sig[s]["n"] >= MIN_OCC]


def class_test(signs, sig, feat, positive, pair_key="pc_top3"):
    """mean feat(paired with class in `positive`) - mean feat(others); null = permute PC classes across PC pool."""
    y = np.array([sig[s][feat] for s in signs])
    partner = [frozen["pairs"][s][pair_key][0][0] for s in signs] if pair_key == "pc_top3" else \
              [frozen["pairs"][s]["pc_top1_raw"][0] for s in signs]
    pidx = np.array([PCK.index(p) for p in partner])
    lab = np.array([pcpool[k]["class"] in positive for k in PCK])

    def stat(l):
        g = l[pidx]
        if g.all() or (~g).all():
            return np.nan
        return y[g].mean() - y[~g].mean()
    obs = stat(lab)
    null = np.array([stat(rng.permutation(lab)) for _ in range(NPERM)])
    null = null[~np.isnan(null)]
    # secondary: random pairing (uniform random PC partner per Indus sign)
    null2 = []
    for _ in range(NPERM):
        g = lab[rng.integers(0, len(PCK), len(signs))]
        if g.all() or (~g).all():
            continue
        null2.append(y[g].mean() - y[~g].mean())
    null2 = np.array(null2)
    g = lab[pidx]
    return {"n": len(signs), "n_pos": int(g.sum()), "mean_pos": float(y[g].mean()) if g.any() else None,
            "mean_neg": float(y[~g].mean()) if (~g).any() else None, "stat": float(obs),
            "p_labelperm": float((1 + (null >= obs).sum()) / (1 + len(null))),
            "p_randompair": float((1 + (null2 >= obs).sum()) / (1 + len(null2)))}


def rho_test(signs, sig, feat, pool, keys, srcfeat, pair_key):
    y = np.array([sig[s][feat] for s in signs])
    partner = [frozen["pairs"][s][pair_key][0][0] for s in signs]
    pidx = np.array([keys.index(p) for p in partner])
    vals = np.array([pool[k][srcfeat] for k in keys])
    def stat(v):
        x = v[pidx]
        if np.ptp(x) == 0 or np.ptp(y) == 0:
            return np.nan
        return spearmanr(x, y).statistic
    obs = stat(vals)
    null = np.array([stat(rng.permutation(vals)) for _ in range(NPERM)]); null = null[~np.isnan(null)]
    null2 = []
    for _ in range(NPERM):
        x = vals[rng.integers(0, len(keys), len(signs))]
        if np.ptp(x) > 0:
            null2.append(spearmanr(x, y).statistic)
    null2 = np.array(null2)
    return {"n": len(signs), "rho": float(obs), "p_labelperm": float((1 + (null >= obs).sum()) / (1 + len(null))),
            "p_randompair": float((1 + (null2 >= obs).sum()) / (1 + len(null2)))}


def run_all(sig, pcset, peset, pc_key="pc_top3"):
    t_pc = targets(pcset, sig); t_pe = targets(peset, sig)
    out = {
        "H1_commodity_after_numeral": class_test(t_pc, sig, "AN", COMMODITY, pc_key),
        "H2_office_end_slot": class_test(t_pc, sig, "END2", {"OFFICE_PERSON"}, pc_key),
        "H3_pc_counted_rate_vs_AN": rho_test(t_pc, sig, "AN", pcpool, PCK, "counted_rate",
                                             "pc_top3") if pc_key == "pc_top3" else None,
        "H4_pe_counted_rate_vs_AN": rho_test(t_pe, sig, "AN", pepool, PEK, "counted_rate", "pe_top3"),
        "H5_pe_header_vs_INIT": rho_test(t_pe, sig, "INIT", pepool, PEK, "header_rate", "pe_top3"),
    }
    return out


def holm(ps):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(order):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


def power_sim(sig, pcset, peset, nsim=200, nperm=500):
    """Planted-effect power on dev. H1: a fraction f of commodity-paired targets get an AN value drawn from
    the top quartile of target AN values (others keep a random draw from all target values).
    Spearman tests: planted Indus values = source values (ranked) mixed with noise to give rho ~ r."""
    global NPERM
    keep = NPERM; NPERM = nperm
    res = {}
    t_pc = targets(pcset, sig)
    y = np.array([sig[s]["AN"] for s in t_pc]); top = y[y >= np.quantile(y, 0.75)]
    lab = {k: pcpool[k]["class"] in COMMODITY for k in PCK}
    for f in (0.3, 0.6, 1.0):
        hits = 0
        for _ in range(nsim):
            fake = {}
            for s in t_pc:
                v = rng.choice(y)
                if lab[frozen["pairs"][s]["pc_top3"][0][0]] and rng.random() < f:
                    v = rng.choice(top)
                fake[s] = {"n": 99, "AN": v}
            hits += class_test(t_pc, fake, "AN", COMMODITY)["p_labelperm"] < 0.05 / 5
        res[f"H1_f{f}"] = hits / nsim
    t_pe = targets(peset, sig)
    vals = {k: pepool[k]["counted_rate"] for k in PEK}
    for r in (0.3, 0.5):
        hits = 0
        for _ in range(nsim):
            x = rankdata([vals[frozen["pairs"][s]["pe_top3"][0][0]] for s in t_pe]); x = (x - x.mean()) / x.std()
            z = r * x + np.sqrt(1 - r * r) * rng.standard_normal(len(x))
            fake = {s: {"n": 99, "AN": float(z[i])} for i, s in enumerate(t_pe)}
            hits += rho_test(t_pe, fake, "AN", pepool, PEK, "counted_rate", "pe_top3")["p_labelperm"] < 0.05 / 5
        res[f"rho_r{r}"] = hits / nsim
    NPERM = keep
    return res


def main():
    dev, ho = dev_heldout(version=2)
    sets = {"dev": signatures(dev), "heldout": signatures(ho), "icit": signatures(icit_set())}
    pcset, peset = frozen["pc_lookalike_set"], frozen["pe_lookalike_set"]
    allset = frozen["indus_pool"]
    R = {"numerals_excluded": sorted(NUMERALS, key=lambda s: int(s[1:])), "confirmatory": {}, "exploratory": {}}
    for name, sig in sets.items():
        R["confirmatory"][name] = run_all(sig, pcset, peset)
    hs = list(R["confirmatory"]["dev"])
    pdev = np.array([R["confirmatory"]["dev"][h]["p_labelperm"] for h in hs])
    adj = holm(pdev)
    verdict = {}
    for i, h in enumerate(hs):
        ok = adj[i] < 0.05 and R["confirmatory"]["heldout"][h]["p_labelperm"] < 0.05 and \
             R["confirmatory"]["icit"][h]["p_labelperm"] < 0.05
        verdict[h] = {"dev_p": float(pdev[i]), "dev_holm": float(adj[i]),
                      "heldout_p": R["confirmatory"]["heldout"][h]["p_labelperm"],
                      "icit_p": R["confirmatory"]["icit"][h]["p_labelperm"], "supported": bool(ok)}
    R["verdict"] = verdict
    # exploratory: full pool, raw-chamfer pairing
    for name, sig in sets.items():
        R["exploratory"][f"fullpool_{name}"] = run_all(sig, allset, allset)
        R["exploratory"][f"rawchamfer_lookalike_{name}"] = {
            "H1": class_test(targets(pcset, sig), sig, "AN", COMMODITY, "raw"),
            "H2": class_test(targets(pcset, sig), sig, "END2", {"OFFICE_PERSON"}, "raw")}
    # exploratory: per-class mean AN / END2 / INIT on dev full pool
    pcl = collections.defaultdict(list)
    sig = sets["dev"]
    for s in targets(allset, sig):
        pcl[frozen["pairs"][s]["pc_top3"][0][2]].append(s)
    R["exploratory"]["per_class_dev_fullpool"] = {
        c: {"n": len(v), "AN": float(np.mean([sig[s]["AN"] for s in v])),
            "END2": float(np.mean([sig[s]["END2"] for s in v])), "INIT": float(np.mean([sig[s]["INIT"] for s in v])),
            "signs": v} for c, v in pcl.items()}
    R["exploratory"]["baseline_dev_fullpool"] = {
        k: float(np.mean([sig[s][k] for s in targets(allset, sig)])) for k in ("AN", "END2", "INIT")}
    R["power_dev"] = power_sim(sets["dev"], pcset, peset)
    # per-pair table for the report
    R["pairs_table"] = [{"indus": s, "pc": frozen["pairs"][s]["pc_top3"][0][0], "pc_class": frozen["pairs"][s]["pc_top3"][0][2],
                         "pe": frozen["pairs"][s]["pe_top3"][0][0],
                         "dev": {k: round(sets["dev"][s][k], 3) for k in ("n", "AN", "INIT", "END2")} if s in sets["dev"] else None}
                        for s in pcset]
    json.dump(R, open(HERE / "test_results.json", "w"), indent=1)
    print(json.dumps({"verdict": verdict, "power": R["power_dev"]}, indent=1))
    for name in sets:
        for h, v in R["confirmatory"][name].items():
            print(name, h, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()})


if __name__ == "__main__":
    main()
