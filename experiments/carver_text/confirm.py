"""Carver hands x text: the single confirmatory test (prereg docs/prereg/carver_text.md).

Statistic: rarity-weighted shared signs, sum over shared sign types of log(N / df), with df counted over all
450 linked seals (label-free). Mean over within-hand pairs, near-copy pairs excluded.
Null: hand labels reshuffled within site x size-tercile strata (same hand sizes), 10,000 times. One-sided, alpha 0.01.
Planted check in the same run, on reshuffled hands: 0% planted (size), 40% and 50% planted (power), 200 replicates each.
Pass: size <= 0.025 and power >= 0.8 at 40% or 50%; the null claim names the smallest share reaching 0.8.
Run from repo root: .venv/bin/python -I experiments/carver_text/confirm.py
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ct  # noqa: E402  (load, strata, pair_mats, within_mean, permute, hand_labels)

SEED, NPERM, NREP, NPERM_PLANT, NBOOT, ALPHA = 20261121, 10000, 200, 1000, 2000, 0.01


def idf_mat(seqs):
    sets = [set(s) for s in seqs]
    df = Counter(x for s in sets for x in s)
    N = len(seqs)
    w = {x: math.log(N / df[x]) for x in df}
    M = np.zeros((N, N))
    for i in range(N):
        for j in range(i + 1, N):
            M[i, j] = M[j, i] = sum(w[x] for x in sets[i] & sets[j])
    return M


def ptest(M, labels, strat, mask, nperm, rng):
    obs, pairs = ct.within_mean(M, labels, mask)
    null = np.array([ct.within_mean(M, ct.permute(labels, strat, rng), mask)[0] for _ in range(nperm)])
    return obs, float(null.mean()), float((1 + np.sum(null >= obs)) / (1 + nperm)), pairs


def planted(pool, labels0, strat, share, rng):
    freq = Counter(t for s in pool for t in s["seq"])
    cands = sorted(t for t, n in freq.items() if 5 <= n <= 50)
    hits = 0
    for _ in range(NREP):
        lab = ct.permute(labels0, strat, rng)
        hands = sorted({l for l in lab if l is not None})
        sig = {h: rng.choice(cands) for h in hands}
        seqs = [list(s["seq"]) for s in pool]
        for i, l in enumerate(lab):
            if l is not None and rng.random() < share:
                seqs[i][rng.randrange(len(seqs[i]))] = sig[l]
        _, _, NC = ct.pair_mats(seqs)
        hits += ptest(idf_mat(seqs), lab, strat, ~NC, NPERM_PLANT, rng)[2] <= ALPHA
    return hits / NREP


def main():
    seals, pool = ct.load()
    labels = ct.hand_labels(pool)
    strat = ct.strata(pool)
    rng = random.Random(SEED)
    seqs = [s["seq"] for s in pool]
    _, _, NC = ct.pair_mats(seqs)
    M = idf_mat(seqs)
    size = planted(pool, labels, strat, 0.0, rng)
    power40 = planted(pool, labels, strat, 0.4, rng)
    power50 = planted(pool, labels, strat, 0.5, rng)
    mde = 40 if power40 >= 0.8 else (50 if power50 >= 0.8 else None)
    obs, mu, p, pairs = ptest(M, labels, strat, ~NC, NPERM, rng)
    hands = sorted({l for l in labels if l is not None})
    lab = np.array([-1 if l is None else l for l in labels])
    rs = []
    for _ in range(NBOOT):
        num = den = 0.0
        for h in rng.choices(hands, k=len(hands)):
            idx = np.where(lab == h)[0]
            m = (~NC)[np.ix_(idx, idx)].copy(); np.fill_diagonal(m, False)
            num += M[np.ix_(idx, idx)][m].sum(); den += m.sum()
        rs.append(num / den / mu)
    ci = [float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))]
    planted_ok = size <= 0.025 and mde is not None
    if not planted_ok:
        verdict = "VOID: planted check failed in this run"
    elif p <= ALPHA:
        verdict = "POSITIVE: expert hands share rare signs above chance (hint-informed, single dataset, no independent replication)"
    else:
        verdict = f"NULL: no effect of >={mde}% detectable (hint-informed, single dataset, no independent replication)"
    out = dict(obs=obs, null_mean=mu, ratio=obs / mu, ratio_ci95_boot_hands=ci, p=p, alpha=ALPHA, nperm=NPERM,
               within_hand_pairs=pairs, hands=len(hands), grouped_linked=int((lab >= 0).sum()), pool=len(pool),
               planted=dict(size_0pct=size, power_40pct=power40, power_50pct=power50, mde_pct=mde, reps=NREP, ok=planted_ok), verdict=verdict)
    (ct.OUT / "confirm.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
