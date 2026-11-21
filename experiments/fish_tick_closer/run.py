"""fish_tick_closer runner. Prereg: docs/prereg/fish_tick_closer.md.

Stages, in the frozen order (each writes out_<stage>.json):
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer/run.py gate
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer/run.py dev
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer/run.py test      # HELD and NEW
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer/run.py redteam
    board/run.sh .venv/bin/python -I experiments/fish_tick_closer/run.py sensitivity
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ftc  # noqa: E402

R_REAL, R_GATE, N_PLANT, R_SHUF = 9999, 999, 200, 1000
P1_ALPHA = {"DEV": None, "HELD": 0.05, "NEW": 0.05}   # DEV uses the 4-of-5 rule
P2_ALPHA = {"DEV": 0.01, "HELD": 0.05, "NEW": 0.05}


def dump(name, obj):
    json.dump(obj, open(HERE / f"out_{name}.json", "w"), indent=1, default=float)
    print(json.dumps(obj, default=float)[:3000], flush=True)


def p1_detect(res, set_name):
    if set_name == "DEV":
        return res["n_pass_001"] >= 4
    p = res["pooled"]["p"]
    return p is not None and p < P1_ALPHA[set_name]


def p2_detect(res, set_name):
    return res["p"] is not None and res["p"] < P2_ALPHA[set_name]


def gate(sets):
    out = {}
    for si, (name, (texts, sch)) in enumerate(sets.items()):
        rec = {}
        for mode in ("true", "false_alarm"):
            rng = np.random.default_rng(5200 + si)
            d1 = d2 = 0
            nx, nfin = [], []
            for k in range(N_PLANT):
                pt, X = ftc.plant(texts, sch, 0.30, rng, false_alarm=(mode == "false_alarm"))
                r1 = ftc.p1(pt, sch, R_GATE, rng, tick_override=X)
                r2 = ftc.p2(pt, sch, rng, draws=10000, tickset=set(X))
                d1 += p1_detect(r1, name); d2 += p2_detect(r2, name)
                nx.append([b["nA"] for b in r1["bases"]]); nfin.append(r2["n_target"])
                if k == 0:
                    rec[mode + "_example"] = dict(p1=r1, p2=r2)
            rec[mode] = dict(p1_detect=d1 / N_PLANT, p2_detect=d2 / N_PLANT,
                             planted_tokens_per_base_mean=np.mean(nx, 0).tolist(),
                             planted_final_texts_mean=float(np.mean(nfin)))
            print(name, mode, rec[mode], flush=True)
        rec["p1_gate_pass"] = rec["true"]["p1_detect"] >= 0.80
        rec["p2_gate_pass"] = rec["true"]["p2_detect"] >= 0.80
        rec["p1_miscalibrated"] = rec["false_alarm"]["p1_detect"] > 0.10
        rec["p2_miscalibrated"] = rec["false_alarm"]["p2_detect"] > 0.10
        out[name] = rec
    return out


def real(sets, names):
    out = {}
    for si, name in enumerate(names):
        texts, sch = sets[name]
        rng = np.random.default_rng(7700 + si)
        r1 = ftc.p1(texts, sch, R_REAL, rng)
        r2 = ftc.p2(texts, sch, rng)
        out[name] = dict(n_texts=len(texts), p1=r1, p1_pass=p1_detect(r1, name), p2=r2, p2_pass=p2_detect(r2, name))
    return out


def redteam(sets):
    out = {}
    for si, (name, (texts, sch)) in enumerate(sets.items()):
        rng = np.random.default_rng(9100 + si)
        rec = {}
        rec["R1_length_strata"] = ftc.p1(texts, sch, R_REAL, rng, strata=True)["pooled"]
        obs, nt = ftc.p1_obs_sum(texts, sch)
        keep = sch.fish | sch.closers | {"#"}
        sims = []
        for _ in range(R_SHUF):
            sh = []
            for t in texts:
                s = list(t["seq"])
                idx = [i for i, x in enumerate(s) if x not in keep]
                vals = [s[i] for i in idx]
                rng.shuffle(vals)
                for i, v in zip(idx, vals):
                    s[i] = v
                sh.append(dict(t, seq=s))
            sims.append(ftc.p1_obs_sum(sh, sch)[0])
        sims = np.array(sims)
        rec["R2_within_text_shuffle"] = dict(delta_sum=obs, n_testable=nt, null_mean=float(sims.mean()),
                                             p=float((1 + (sims >= obs).sum()) / (1 + R_SHUF)) if nt else None)
        rec["R3_drop_start"] = ftc.p1(texts, sch, R_REAL, rng, drop_start=True)["pooled"]
        rec["R1p_nopost"] = ftc.p2(texts, sch, rng, pool="nopost")
        rec["R3p_plainfish_pool"] = ftc.p2(texts, sch, rng, pool="plainfish")
        base = ftc.p2(texts, sch, rng, draws=10)
        sims2 = []
        for _ in range(R_SHUF):
            sh = []
            for t in texts:
                s = list(t["seq"]); rng.shuffle(s); sh.append(dict(t, seq=s))
            r = ftc.p2(sh, sch, rng, draws=10)
            if r["n_target"]:
                sims2.append(r["share"])
        sims2 = np.array(sims2)
        rec["R2p_within_text_shuffle"] = dict(
            share=base["share"], n_target=base["n_target"], n_valid=len(sims2),
            null_mean=float(sims2.mean()) if len(sims2) else None,
            p=(float((1 + (sims2 >= base["share"]).sum()) / (1 + len(sims2)))
               if len(sims2) and base["share"] is not None else None))
        out[name] = rec
        print(name, json.dumps(rec, default=float), flush=True)
    return out


def main():
    stage = sys.argv[1]
    t0 = time.time()
    if stage == "sensitivity":
        sets = ftc.load_sets(collapse_near=False)
        dump(stage, real(sets, ["DEV", "HELD", "NEW"]))
        return
    sets = ftc.load_sets()
    print({k: len(v[0]) for k, v in sets.items()}, flush=True)
    if stage == "gate":
        dump(stage, gate(sets))
    elif stage == "dev":
        dump(stage, real(sets, ["DEV"]))
    elif stage == "test":
        dump(stage, real(sets, ["HELD", "NEW"]))
    elif stage == "redteam":
        dump(stage, redteam(sets))
    print("seconds", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
