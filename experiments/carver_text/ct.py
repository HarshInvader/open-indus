"""Carver hands x text (prereg docs/prereg/carver_text.md). Needs out/seals.json from parse.py.

Stages (run in this order; each refuses to run before the previous one's file exists):
  power   planted 20% hand-specific sign on the real hand structure; writes out/power.json
  real    the sealed test on real texts (only if power >= 0.8 and the join gate passed); writes out/real.json
Run from repo root: .venv/bin/python -I experiments/carver_text/ct.py power|real
"""
import json, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SEED = 20261120
NPERM_REAL, NPERM_POWER, NREP_POWER, NBOOT = 5000, 500, 200, 2000
ATTR = ["EYE", "EAR", "HEAD", "HORN", "NECK", "HALTER", "TAIL", "LEG", "HOOF", "PIZZLE", "STAND"]


# ------------------------------------------------------------------ data
def load():
    seals = json.loads((OUT / "seals.json").read_text())
    pool = [s for s in seals if s["icit"] and len(s["icit"][0]["seq"]) >= 1]
    for s in pool:
        t = s["icit"][0]
        s["seq"] = list(t["seq"])
        try:
            area = float(t["width_mm"]) * float(t["height_mm"])
        except ValueError:
            area = 0.0
        s["area"] = area
    return seals, pool


def strata(pool):
    """site x size tercile (tercile within site; unknown size = own bin)."""
    out, by = [None] * len(pool), defaultdict(list)
    for i, s in enumerate(pool):
        by[s["icit"][0]["site"]].append(i)
    for site, idx in by.items():
        known = [i for i in idx if pool[i]["area"] > 0]
        cuts = np.quantile([pool[i]["area"] for i in known], [1 / 3, 2 / 3]) if len(known) >= 3 else None
        for i in idx:
            a = pool[i]["area"]
            b = "u" if a <= 0 else (0 if cuts is None else int(np.searchsorted(cuts, a, side="right")))
            out[i] = f"{site}|{b}"
    return out


def lev1(a, b):
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def contained(a, b):
    if len(a) > len(b):
        a, b = b, a
    return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


def pair_mats(seqs):
    n = len(seqs)
    sets = [set(s) for s in seqs]
    J = np.zeros((n, n)); SL = np.zeros((n, n)); NC = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            u = len(sets[i] | sets[j])
            J[i, j] = J[j, i] = len(sets[i] & sets[j]) / u if u else 0.0
            SL[i, j] = SL[j, i] = float(seqs[i][0] == seqs[j][0] or seqs[i][-1] == seqs[j][-1])
            NC[i, j] = NC[j, i] = lev1(seqs[i], seqs[j]) or contained(seqs[i], seqs[j])
    return J, SL, NC


def within_mean(M, labels, mask):
    """Mean of M over unordered pairs with equal non-None labels and mask True."""
    lab = np.array([-1 if l is None else l for l in labels])
    same = (lab[:, None] == lab[None, :]) & (lab[:, None] >= 0)
    np.fill_diagonal(same, False)
    sel = same & mask
    return float(M[sel].mean()) if sel.any() else float("nan"), int(sel.sum() // 2)


def permute(labels, strat, rng):
    lab = list(labels)
    by = defaultdict(list)
    for i, s in enumerate(strat):
        by[s].append(i)
    for idx in by.values():
        vals = [lab[i] for i in idx]
        rng.shuffle(vals)
        for i, v in zip(idx, vals):
            lab[i] = v
    return lab


def test(mats, labels, strat, nperm, rng, boot=False):
    """Returns per statistic: obs, null mean, ratio, one-sided p, and (optionally) bootstrap CI of the ratio."""
    J, SL, NC = mats
    res = {}
    for name, M in (("sign_jaccard", J), ("slot_share", SL)):
        for arm, mask in (("nc_excluded", ~NC), ("all_pairs", np.ones_like(NC))):
            obs, npairs = within_mean(M, labels, mask)
            null = np.array([within_mean(M, permute(labels, strat, rng), mask)[0] for _ in range(nperm)])
            mu = float(np.nanmean(null))
            r = dict(obs=obs, null_mean=mu, ratio=obs / mu if mu > 0 else float("nan"), pairs=npairs,
                     p=float((1 + np.sum(null >= obs)) / (1 + nperm)))
            if boot:
                hands = sorted({l for l in labels if l is not None})
                lab = np.array([-1 if l is None else l for l in labels])
                rs = []
                for _ in range(NBOOT):
                    pick = rng.choices(hands, k=len(hands))
                    num = den = 0.0
                    for h in pick:
                        idx = np.where(lab == h)[0]
                        sub = M[np.ix_(idx, idx)]; m = mask[np.ix_(idx, idx)].copy(); np.fill_diagonal(m, False)
                        num += sub[m].sum(); den += m.sum()
                    rs.append((num / den) / mu if den and mu > 0 else np.nan)
                r["ratio_ci95"] = [float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))]
            res[f"{name}|{arm}"] = r
    return res


def holm2(p1, p2, alpha=0.05):
    """Holm over two tests: at least one rejected iff min p <= alpha / 2."""
    return min(p1, p2) <= alpha / 2


def hand_labels(pool, key="group"):
    names = sorted({s[key] for s in pool if s.get(key)})
    cnt = Counter(s[key] for s in pool if s.get(key))
    idx = {n: i for i, n in enumerate(names) if cnt[n] >= 2}
    return [idx.get(s.get(key)) for s in pool]


def recluster(seals, pool, thr):
    """Hands from the 11 non-text attributes only: connected components of seals sharing >= thr identical
    base attribute types (minor-variant letters stripped; n/a never matches). Pool seals only."""
    base = [{a: re.sub(r"[a-z]$", "", s["attrs"][a]) for a in ATTR if s["attrs"][a] != "n/a"} for s in pool]
    n = len(pool); parent = list(range(n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if sum(1 for a in base[i] if base[j].get(a) == base[i][a]) >= thr:
                parent[f(i)] = f(j)
    comp = [f(i) for i in range(n)]
    c = Counter(comp)
    return [comp[i] if c[comp[i]] >= 2 else None for i in range(n)], sorted(c.values(), reverse=True)[:5]


# ------------------------------------------------------------------ stages
def stage_power():
    seals, pool = load()
    labels = hand_labels(pool)
    strat = strata(pool)
    rng = random.Random(SEED)
    freq = Counter(t for s in pool for t in s["seq"])
    cands = sorted(t for t, n in freq.items() if 5 <= n <= 50)
    hands = sorted({l for l in labels if l is not None})
    hits, rows = 0, []
    for rep in range(NREP_POWER):
        seqs = [list(s["seq"]) for s in pool]
        sig = {h: rng.choice(cands) for h in hands}
        for i, l in enumerate(labels):
            if l is not None and rng.random() < 0.2:
                seqs[i][rng.randrange(len(seqs[i]))] = sig[l]
        mats = pair_mats(seqs)
        r = test(mats, labels, strat, NPERM_POWER, rng)
        ok = holm2(r["sign_jaccard|nc_excluded"]["p"], r["slot_share|nc_excluded"]["p"])
        hits += ok
        rows.append(dict(rep=rep, ok=bool(ok), pJ=r["sign_jaccard|nc_excluded"]["p"], pS=r["slot_share|nc_excluded"]["p"]))
    out = dict(power=hits / NREP_POWER, reps=NREP_POWER, grouped_linked=sum(l is not None for l in labels),
               hands=len(hands), pool=len(pool), rows=rows)
    (OUT / "power.json").write_text(json.dumps(out, indent=1))
    print("POWER", out["power"], "hands", out["hands"], "grouped linked", out["grouped_linked"], "pool", out["pool"])


def stage_real():
    pw = json.loads((OUT / "power.json").read_text())
    assert pw["grouped_linked"] >= 120, "join gate failed"
    assert pw["power"] >= 0.8, "power gate failed: study is dead (prereg)"
    seals, pool = load()
    strat = strata(pool)
    rng = random.Random(SEED + 1)
    mats = pair_mats([s["seq"] for s in pool])
    out = {"jamison": test(mats, hand_labels(pool), strat, NPERM_REAL, rng, boot=True)}
    lab7, top = recluster(seals, pool, 7)
    thr = 7
    if top and top[0] > 40:
        lab7, top = recluster(seals, pool, 8); thr = 8
    out["recluster"] = dict(threshold=thr, largest=top, hands=len({l for l in lab7 if l is not None}),
                            res=test(mats, lab7, strat, NPERM_REAL, rng, boot=True))
    J = out["jamison"]
    pos = holm2(J["sign_jaccard|nc_excluded"]["p"], J["slot_share|nc_excluded"]["p"])
    rc = out["recluster"]["res"]
    same_dir = all(rc[k]["ratio"] > 1 for k in ("sign_jaccard|nc_excluded", "slot_share|nc_excluded"))
    neutral = all(J[k]["ratio_ci95"][1] <= 1.1 for k in ("sign_jaccard|nc_excluded", "slot_share|nc_excluded"))
    out["verdict"] = ("POSITIVE: same-hand seals share text" if pos and same_dir else
                      "POSITIVE (Jamison hands only; re-cluster arm disagrees)" if pos else
                      "TEXT-NEUTRAL: carvers are text-neutral (upper CI <= 1.1)" if neutral else "INCONCLUSIVE")
    (OUT / "real.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"power": stage_power, "real": stage_real}[sys.argv[1]]()
