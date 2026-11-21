"""Stages (run in this order, each through board/run.sh):
    gate | dev | held | new | redteam
Prereg: docs/prereg/parpola_rules34.md. Results go to results.json (one key per stage).
"""
import sys
import time

from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p34 as P  # noqa: E402

ALPHA_DEV = 0.01
EX_M, EX_W = P.EXCLUDE["M"], P.EXCLUDE["W"]
SQ_M, SQ_W = P.SIGNS["M"]["squirrel"], P.SIGNS["W"]["squirrel"]


def gate():
    dev, _ = P.load("dev")
    rng = np.random.default_rng(34)
    cnt = P.counts(dev)
    out = {}
    # ---- rule 3: planted substituting pair
    pool, _ = P.rule3_pool(cnt, "M87", "M59", EX_M)
    rows = []
    for trial in range(P.N_GATE):
        a, b = rng.choice(pool, 2, replace=False)
        a, b = (a, b) if cnt[a] <= cnt[b] else (b, a)
        planted, k = P.plant_substitution(dev, a, b, P.S_PLANT, rng)
        r = P.rule3(planted, a, b, EX_M, seed=trial)
        r0 = P.rule3(dev, a, b, EX_M, seed=trial)  # false-alarm check, nothing planted
        # held-out-size power: plant into a 34% random subset of dev texts, test at 0.05
        sub = [dev[i] for i in rng.choice(len(dev), int(0.34 * len(dev)), replace=False)]
        try:
            ps, _ = P.plant_substitution(sub, a, b, P.S_PLANT, rng)
            rs = P.rule3(ps, a, b, EX_M, seed=trial)["p"]
        except Exception:  # subset too small for a pool
            rs = None
        rows.append(dict(a=a, b=b, k=k, p=r["p"], p_noplant=r0["p"], p_heldsize=rs))
        print("r3", trial, a, b, k, round(r["p"], 4), round(r0["p"], 4), rs, flush=True)
    det = np.mean([x["p"] < ALPHA_DEV for x in rows])
    fa = np.mean([x["p_noplant"] < ALPHA_DEV for x in rows])
    hs = [x["p_heldsize"] for x in rows if x["p_heldsize"] is not None]
    out["rule3"] = dict(s=P.S_PLANT, trials=rows, detection=float(det), false_alarm=float(fa),
                        heldsize_power_p05=float(np.mean([p < 0.05 for p in hs])) if hs else None,
                        gate_pass=bool(det >= 0.8))
    # ---- rule 3, strong level (reported power curve only; not the gate)
    rows = []
    for trial in range(30):
        a, b = rng.choice(pool, 2, replace=False)
        a, b = (a, b) if cnt[a] <= cnt[b] else (b, a)
        planted, k = P.plant_substitution(dev, a, b, 0.5, rng)
        rows.append(P.rule3(planted, a, b, EX_M, seed=100 + trial)["p"])
        print("r3strong", trial, a, b, k, round(rows[-1], 4), flush=True)
    out["rule3_strong_s050"] = dict(detection=float(np.mean([p < ALPHA_DEV for p in rows])), p=rows)
    # ---- rule 4: planted fixed partner
    p1, ps, heads = P.rule4_pools(cnt, "M403", "M87", SQ_M, EX_M)
    rows = []
    for trial in range(P.N_GATE):
        h = rng.choice(heads)
        x = rng.choice([s for s in p1 if s != h])
        y = rng.choice([s for s in ps if s not in (h, x)])
        planted, k = P.plant_partner(dev, h, x, P.Q_PLANT, rng)
        r = P.rule4(planted, h, x, (y,), EX_M)
        r0 = P.rule4(dev, h, x, (y,), EX_M)
        sub = [dev[i] for i in rng.choice(len(dev), int(0.34 * len(dev)), replace=False)]
        try:
            psb, _ = P.plant_partner(sub, h, x, P.Q_PLANT, rng)
            rs = P.rule4(psb, h, x, (y,), EX_M)["p"]
        except Exception:  # head absent from subset or pool empty
            rs = None
        rows.append(dict(h=h, x=x, y=y, k=k, share=r["obs_share"], p=r["p"], p_noplant=r0["p"], p_heldsize=rs))
        print("r4", trial, h, x, y, k, round(r["obs_share"], 3), round(r["p"], 4), round(r0["p"], 4), rs, flush=True)
    det = np.mean([x["p"] < ALPHA_DEV for x in rows])
    fa = np.mean([x["p_noplant"] < ALPHA_DEV for x in rows])
    hs = [x["p_heldsize"] for x in rows if x["p_heldsize"] is not None]
    out["rule4"] = dict(q=P.Q_PLANT, trials=rows, detection=float(det), false_alarm=float(fa),
                        heldsize_power_p05=float(np.mean([p < 0.05 for p in hs])) if hs else None,
                        gate_pass=bool(det >= 0.8))
    P.save("gate", out)
    print({k: (v["detection"], v.get("false_alarm"), v.get("heldsize_power_p05"), v.get("gate_pass")) for k, v in out.items()})


def test(split):
    texts, sc = P.load(split)
    S = P.SIGNS[sc]
    ex = P.EXCLUDE[sc]
    cnt = P.counts(texts)
    out = dict(n_texts=len(texts))
    if min(cnt[S["vel"]], cnt[S["fish"]]) >= 10:
        out["rule3"] = P.rule3(texts, S["vel"], S["fish"], ex)
    else:
        out["rule3"] = dict(descriptive_only=True, n_a=cnt[S["vel"]], n_b=cnt[S["fish"]])
    if cnt[S["muruku"]] >= 10:
        out["rule4"] = P.rule4(texts, S["muruku"], S["vel"], S["squirrel"], ex)
    else:
        out["rule4"] = dict(descriptive_only=True, n=cnt[S["muruku"]])
    P.save(split, out)
    print(split, out)


def redteam():
    out = {}
    for split in ("dev", "held"):
        texts, _ = P.load(split)
        rng = np.random.default_rng(3434)
        o = {}
        base3 = P.rule3(texts, "M87", "M59", EX_M)
        # alt null A, rule 3: position-matched pairs
        pairs = P.rule3_position_pairs(texts, "M87", "M59", EX_M, k=50)
        o["r3_altA_position"] = {k: v for k, v in P.rule3(texts, "M87", "M59", EX_M, pairs=pairs).items()
                                 if k in ("obs", "n_null", "null_median", "null_q95", "p")}
        o["r3_altA_position"]["pairs"] = pairs[:10]
        # alt null B, rule 3: within-text order shuffle
        n_sub = base3["n_sub"]
        sh = []
        for i in range(P.N_SHUF):
            occ_s = P.occurrences(P.shuffle_within(texts, rng))
            sh.append(P.overlap(occ_s, "M87", "M59", n_sub, seed=i))
        sh = np.array(sh)
        o["r3_altB_shuffle"] = dict(obs=base3["obs"], null_mean=float(sh.mean()), null_q95=float(np.quantile(sh, 0.95)),
                                    p=(1 + int((sh >= base3["obs"]).sum())) / (1 + len(sh)))
        # robustness: no edge tokens; near-copy collapse
        o["r3_noedges"] = {k: v for k, v in P.rule3(texts, "M87", "M59", EX_M, edges=False).items()
                           if k in ("obs", "null_median", "null_q95", "p")}
        # rule 4
        o["r4_altA_heads"] = P.rule4_heads_null(texts, "M403", "M87", SQ_M, EX_M)
        base4 = P.rule4(texts, "M403", "M87", SQ_M, EX_M)
        sh = []
        for _ in range(P.N_SHUF):
            occ_s = P.occurrences(P.shuffle_within(texts, rng))
            sh.append(P.share_next(occ_s, "M403", {"M87", *SQ_M})[0])
        sh = np.array(sh)
        o["r4_altB_shuffle"] = dict(obs=base4["obs_share"], null_mean=float(sh.mean()),
                                    null_q95=float(np.quantile(sh, 0.95)),
                                    p=(1 + int((sh >= base4["obs_share"]).sum())) / (1 + len(sh)))
        out[split] = o
        print(split, o, flush=True)
    # near-copy collapse on dev (primary nulls)
    dev_raw, _ = P.L.dev_heldout(version=2)
    dc = P.collapse_near(dev_raw)
    out["dev_collapsed"] = dict(n_texts=len(dc),
                                rule3={k: v for k, v in P.rule3(dc, "M87", "M59", EX_M).items()
                                       if k in ("n_a", "n_b", "obs", "null_median", "null_q95", "p")},
                                rule4={k: v for k, v in P.rule4(dc, "M403", "M87", SQ_M, EX_M).items()
                                       if k in ("n_with_next", "obs_share", "null_q95", "p")})
    print("dev_collapsed", out["dev_collapsed"])
    P.save("redteam", out)


if __name__ == "__main__":
    t0 = time.time()
    st = sys.argv[1]
    {"gate": gate, "dev": lambda: test("dev"), "held": lambda: test("held"), "new": lambda: test("new"),
     "redteam": redteam}[st]()
    print("seconds", round(time.time() - t0, 1))
