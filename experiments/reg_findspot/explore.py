"""EXPLORATORY follow-ups (not pre-registered) after test.py.

Run: .venv/bin/python experiments/reg_findspot/explore.py   (log: explore.log, output: explore.json)
E1 ticked-fish block concentration without house 12/V (the visible cluster), and per-variant counts.
E2 scan of every sign on >= 10 seals: block and house concentration (same G/permutation as F3), BH over the scan.
E3 F2 restricted to identical texts only and to texts of >= 4 signs.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test import TICKED, bh, gstat_counts, load, perm_labels, f2  # noqa: E402
import test as T  # noqa: E402

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(7)
NP = 5000


def units(d):
    unitA = np.where(d.block.notna(), d.block, np.where(d.kind == "street", "street", None))
    cnt = pd.Series(unitA).value_counts()
    big = set(cnt[cnt >= 8].index) - {"street"}
    uA = np.array([None if u is None else (u if u in big or u == "street" else "other") for u in unitA], object)
    return uA


def gtest_block(d, f):
    uA = units(d)
    m = np.array([u is not None for u in uA])
    lab = pd.factorize(uA[m])[0]
    band = d.band5.fillna(-1).to_numpy()[m]
    P = perm_labels(lab, band, NP, rng)
    nu = lab.max() + 1
    obs = gstat_counts(f[m], lab, nu)
    null = np.array([gstat_counts(f[m], P[r], nu) for r in range(NP)])
    return float(obs), float((1 + (null >= obs - 1e-9).sum()) / (1 + NP))


def gtest_house(d, f):
    hk = d.house_key.to_numpy(object)
    hc = pd.Series(hk[pd.notna(hk)]).value_counts()
    ok = set(hc[hc >= 3].index)
    m = np.array([h in ok for h in hk]) & d.band5.notna().to_numpy()
    lab = pd.factorize(hk[m])[0]
    st = pd.factorize(d.block.to_numpy(object)[m] + "|" + d.band5.to_numpy()[m].astype(str))[0]
    P = perm_labels(lab, st, NP, rng)
    nu = lab.max() + 1
    obs = gstat_counts(f[m], lab, nu)
    null = np.array([gstat_counts(f[m], P[r], nu) for r in range(NP)])
    return float(obs), float((1 + (null >= obs - 1e-9).sum()) / (1 + NP))


def main():
    d = load()
    out = {}
    tf = d.sset.apply(lambda s: bool(s & TICKED)).to_numpy(float)
    # E1
    keep = (d.house_key != "12/V").to_numpy()
    d2 = d[keep].reset_index(drop=True)
    out["E1_ticked_block_without_12V"] = gtest_block(d2, tf[keep])
    out["E1_ticked_house_without_12V"] = gtest_house(d2, tf[keep])
    out["E1_variants"] = {s: int(d.sset.apply(lambda x, s=s: s in x).sum()) for s in sorted(TICKED)}
    out["E1_12V"] = d[d.house_key == "12/V"][["serial", "room_key", "depth", "seq_side0"]].astype(str).to_dict("records")
    # untick fish base signs in the same blocks, for contrast
    base = {"M59", "M65", "M67", "M70", "M72"}
    bf = d.sset.apply(lambda s: bool(s & base)).to_numpy(float)
    out["E1_plain_fish_block"] = gtest_block(d, bf)
    out["E1_plain_fish_house"] = gtest_house(d, bf)
    print("E1", {k: v for k, v in out.items() if k != "E1_12V"}, flush=True)
    # E2 scan
    from collections import Counter
    c = Counter(s for ss in d.sset for s in ss)
    signs = [s for s, n in c.items() if n >= 10]
    rows = []
    for s in sorted(signs, key=lambda s: -c[s]):
        f = d.sset.apply(lambda x, s=s: s in x).to_numpy(float)
        gb, pb = gtest_block(d, f)
        gh, ph = gtest_house(d, f)
        rows.append(dict(sign=s, n=c[s], p_block=pb, p_house=ph))
    qb = bh([r["p_block"] for r in rows])
    qh = bh([r["p_house"] for r in rows])
    for r, a, b in zip(rows, qb, qh):
        r["q_block"], r["q_house"] = float(a), float(b)
    out["E2_scan"] = rows
    out["E2_n_signs"] = len(rows)
    out["E2_block_p05"] = sum(r["p_block"] <= 0.05 for r in rows)
    out["E2_house_p05"] = sum(r["p_house"] <= 0.05 for r in rows)
    out["E2_q05"] = [r for r in rows if r["q_block"] < 0.05 or r["q_house"] < 0.05]
    print("E2 signs", len(rows), "p<=.05 block", out["E2_block_p05"], "house", out["E2_house_p05"],
          "q<.05", out["E2_q05"], flush=True)
    for r in sorted(rows, key=lambda r: min(r["p_block"], r["p_house"]))[:8]:
        print("  ", r)
    # E3
    T.NPERM = 5000
    seqs = [[s for s in q if s != "|"] for q in d.seq]
    r = f2(d, rng)
    ident = [p for p in r["pairs"] if p["kind"] == "identical"]
    long4 = [p for p in r["pairs"] if min(len(p["seqs"][0].split()), len(p["seqs"][1].split())) >= 4]
    def summ(ps):
        sb = sum(1 for p in ps if p["blocks"][0] is not None and p["blocks"][0] == p["blocks"][1]
                 and str(p["blocks"][0]) != "nan")
        sh = sum(1 for p in ps if p["houses"][0] is not None and p["houses"][0] == p["houses"][1]
                 and str(p["houses"][0]) != "nan")
        dd = [abs(p["depths"][0] - p["depths"][1]) for p in ps if None not in p["depths"]]
        return dict(n=len(ps), same_block=sb, same_house=sh, mean_abs_ddepth=float(np.mean(dd)) if dd else None)
    out["E3_identical"] = summ(ident)
    out["E3_len4plus"] = summ(long4)
    # random-pair reference for same block / house share
    blk = d.block.to_numpy(object)
    hk = d.house_key.to_numpy(object)
    nb = sum(1 for i in range(len(d)) for j in range(i + 1, len(d)) if pd.notna(blk[i]) and blk[i] == blk[j])
    nh = sum(1 for i in range(len(d)) for j in range(i + 1, len(d)) if pd.notna(hk[i]) and hk[i] == hk[j])
    npairs = len(d) * (len(d) - 1) / 2
    out["E3_random_pair_same_block"] = nb / npairs
    out["E3_random_pair_same_house"] = nh / npairs
    print("E3", out["E3_identical"], out["E3_len4plus"], out["E3_random_pair_same_block"], out["E3_random_pair_same_house"])
    json.dump(out, open(OUT / "explore.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
