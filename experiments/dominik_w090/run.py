"""Task #19: Dominik 2026 W090-after-W520 vs W740. Prereg docs/prereg/dominik_w090.md.
Run: .venv/bin/python -I experiments/dominik_w090/run.py"""
import json, random, sys
from collections import Counter, defaultdict
from math import log
from pathlib import Path
from scipy.stats import fisher_exact
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from corpus.load import icit_texts, distinct, runs, dev_heldout  # noqa

def icit_runs(texts, rev):
    out = []
    for t in texts:
        for seg in t["segments"]:
            r = [s for s in seg if s not in ("|", "#")]
            if len(r) >= 1:
                out.append(r[::-1] if rev else r)
    return out

def contrast(rs, A="W520", B="W740", C="W090", W33="W033"):
    kA = nA = kB = nB = 0
    for r in rs:
        for i, s in enumerate(r[:-1]):
            nxt = r[i + 1]
            if s == A:
                if (i > 0 and r[i - 1] == W33) or nxt == W33:
                    continue
                nA += 1; kA += nxt == C
            elif s == B:
                nB += 1; kB += nxt == C
    p = fisher_exact([[kA, nA - kA], [kB, nB - kB]], alternative="less")[1] if nA and nB else float("nan")
    return {"k_A": kA, "n_A": nA, "k_B": kB, "n_B": nB, "rate_A": kA / nA if nA else None,
            "rate_B": kB / nB if nB else None, "fisher_p_less": p,
            "power_zero_if_same_rate": (1 - kB / nB) ** nA if nB else None}

def zero_cells(rs, rng=None, mode=None):
    pairs = [(r[i], r[i + 1]) for r in rs for i in range(len(r) - 1)]
    if mode == "label":
        nx = [b for _, b in pairs]; rng.shuffle(nx); pairs = [(a, b) for (a, _), b in zip(pairs, nx)]
    nxt = defaultdict(Counter)
    for a, b in pairs:
        nxt[a][b] += 1
    tot = {a: sum(c.values()) for a, c in nxt.items()}
    X = [a for a in tot if tot[a] >= 500]; Y = [a for a in tot if 100 <= tot[a] <= 200]
    z = cand = 0; ps = []
    for x in X:
        for c, k in nxt[x].items():
            if k / tot[x] < 0.05: continue
            for y in Y:
                if y == x: continue
                cand += 1
                ky = nxt[y][c]
                if ky == 0: z += 1
                ps.append(fisher_exact([[ky, tot[y] - ky], [k, tot[x] - k]], alternative="less")[1])
    return z, cand, ps

def within_text_shuffle(rs, rng):
    out = []
    for r in rs:
        r = r[:]; rng.shuffle(r); out.append(r)
    return out

if __name__ == "__main__":
    rng = random.Random(19)
    icit = distinct(icit_texts())
    res = {"n_icit_distinct": len(icit)}
    orders = {}
    for name, rev in [("reading", False), ("listing", True)]:
        rs = icit_runs(icit, rev)
        orders[name] = (rs, contrast(rs))
    dist = {k: abs(log(max(v[1]["n_B"], 1) / 994)) + abs(log(max(v[1]["n_A"], 1) / 136)) for k, v in orders.items()}
    primary = min(dist, key=dist.get)
    res["order_choice"] = {"denominator_distance": dist, "primary": primary}
    for k, (rs, c) in orders.items():
        res["T1_" + k] = c
        no220 = [r for r in rs if "W220" not in r]
        res["T1_" + k + "_no_W220"] = contrast(no220)
    rs = orders[primary][0]
    rev = primary == "listing"
    # T2a M77 heldout via bridge (M-numbers)
    dev, ho = dev_heldout(version=2)
    for nm, tx in [("T2a_m77_heldout", ho), ("T2a_m77_dev", dev)]:
        mr = [r[::-1] if rev else r for t in tx for r in runs(t["seq"])]
        res[nm] = contrast(mr, A="M211", B="M342", C="M1", W33="M89")
    big = {"Mohenjo-daro", "Mohenjodaro", "Harappa", "Lothal", "Kalibangan", "Chanhudaro", "Chanhu-daro"}
    sites = Counter(t["site"] for t in icit)
    other = [t for t in icit if t["site"] not in big]
    res["T2b_icit_other_sites"] = contrast(icit_runs(other, rev))
    res["T2b_sites_excluded_check"] = {s: sites[s] for s in sites if s in big}
    # T3
    z, cand, ps = zero_cells(rs)
    pc = res["T1_" + primary]["fisher_p_less"]
    res["T3"] = {"zero_cells_observed": z, "candidate_triples": cand,
                 "rank_of_claim_p": sum(p <= pc for p in ps), "n_triples": len(ps)}
    nl = [zero_cells(rs, rng, "label")[0] for _ in range(1000)]
    nw = [zero_cells(within_text_shuffle(rs, rng))[0] for _ in range(200)]
    res["T3"].update({"label_perm_null_mean": sum(nl) / len(nl), "label_perm_p_ge": (1 + sum(x >= z for x in nl)) / 1001,
                      "within_text_null_mean": sum(nw) / len(nw), "within_text_p_ge": (1 + sum(x >= z for x in nw)) / 201})
    # T4 position
    def pos(sign):
        fin = tot = 0
        for r in icit_runs(icit, False):
            for i, s in enumerate(r):
                if s == sign: tot += 1; fin += i == len(r) - 1
        return {"tokens": tot, "final_share_reading_order": fin / tot if tot else None}
    res["T4"] = {s: pos(s) for s in ["W520", "W740", "W090"]}
    json.dump(res, open(HERE / "results.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
