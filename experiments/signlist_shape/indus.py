"""Indus tests I1-I3 (prereg docs/prereg/signlist_shape_context.md).
    board/run.sh .venv/bin/python -I experiments/signlist_shape/indus.py i1    # merges on M77 + merge path
    board/run.sh .venv/bin/python -I experiments/signlist_shape/indus.py i2    # ICIT splits (W vs bridge-lumped)
Writes out/i1.json, out/i2.json, out/partition_both.json."""
import sys, json, random, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/redteam"))
import sl, run_lib  # noqa
from corpus.load import dev_heldout, runs, icit_texts  # noqa

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def log(*a):
    print(*a, flush=True)


def i1():
    t0 = time.time()
    dev, ho = dev_heldout()
    train = [r for t in dev for r in runs(t["seq"])]
    test = [r for t in ho for r in runs(t["seq"])]
    tr_signs = sorted({s for q in train for s in q})
    masks = {}
    for s in tr_signs:
        p = ROOT / "data/sign_images" / f"{s}.png"
        if p.exists():
            masks[s] = sl.norm_mask(sl.ink_of(p))
    pool = [s for s in tr_signs if s in masks]
    log("train", len(train), "test", len(test), "pool", len(pool))
    res, S_shape, S_ctx = run_lib.run_modes(train, pool, masks, log=log)
    allm = [f"M{i}" for i in range(1, 418)]
    fine = {s: s for s in allm}
    parts = {"M77": fine}
    for mode in res:
        parts[f"greedy_{mode}"] = {s: res[mode]["mapping"].get(s, s) for s in allm}
    VJ = json.load(open(ROOT / "experiments/signlist_robustness/variants.json"))
    for k in ("img_hi", "img_mid", "img_lo", "lump_all", "parpola", "lump_fish", "lump_numerals", "lump_jar_man"):
        parts[k] = {s: VJ["partitions"][k].get(s, s) for s in allm}
    per = {k: run_lib.heldout_ll(v, train, test) for k, v in parts.items()}
    ntok = sum(x[1] for x in per["M77"])
    out = {"n_train": len(train), "n_test": len(test), "n_test_tokens": ntok, "pool": len(pool), "lists": {}}
    used = set(tr_signs) | {s for q in test for s in q}
    for k, v in parts.items():
        nl = len({v[s] for s in used})
        out["lists"][k] = {"n_labels_used": nl, "n_labels_all417": len(set(v.values())),
                           "ll_per_tok": sum(x[0] for x in per[k]) / ntok,
                           "vs_M77": run_lib.boot_diff(per[k], per["M77"])}
        log(k, nl, out["lists"][k]["ll_per_tok"], out["lists"][k]["vs_M77"])
    out["both_vs_ctx"] = run_lib.boot_diff(per["greedy_both"], per["greedy_ctx"])
    out["both_vs_shape"] = run_lib.boot_diff(per["greedy_both"], per["greedy_shape"])
    log("both vs ctx", out["both_vs_ctx"])
    for mode in res:
        out[f"accepted_{mode}"] = [(a, b, d, sc) for a, b, d, sc in res[mode]["accepted"]]
        # similarity of each accepted pair for the record
    idx = {s: i for i, s in enumerate(pool)}
    out["accepted_both_sims"] = [(a, b, float(S_shape[idx[a], idx[b]]), float(S_ctx[idx[a], idx[b]]))
                                 for a, b, *_ in res["both"]["accepted"]]
    path = run_lib.merge_path(train, test, res["both"]["cands"], step=10)
    out["path_both"] = path
    log("path argmax", path["argmax_labels"], path["boot95"], "start", path["n_labels_start"])
    pathc = run_lib.merge_path(train, test, res["ctx"]["cands"], step=10)
    out["path_ctx"] = pathc
    log("ctx path argmax", pathc["argmax_labels"], pathc["boot95"])
    json.dump(parts["greedy_both"], open(OUT / "partition_both.json", "w"), indent=0)
    json.dump({k: parts[k] for k in ("greedy_ctx", "greedy_shape")}, open(OUT / "partition_controls.json", "w"))
    out["sec"] = time.time() - t0
    json.dump(out, open(OUT / "i1.json", "w"), indent=1, default=float)


def i2():
    from rt_common import near_dup_clusters
    t0 = time.time()
    flat = sorted({tuple(s for s in t["seq"] if s not in "|#") for t in icit_texts()} - {()})
    cl = near_dup_clusters(flat)
    r = random.Random(0); r.shuffle(cl)
    cut = int(0.75 * len(cl))
    ho = {s for c in cl[cut:] for s in c}
    seen, train, test = set(), [], []
    for t in icit_texts():
        f = tuple(s for s in t["seq"] if s not in "|#")
        if not f or f in seen:
            continue
        seen.add(f)
        (test if f in ho else train).extend(runs(t["seq"]))
    W = sorted({s for q in train + test for s in q})
    B = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    uf = sl.UF()
    bym = defaultdict(list)
    for k, v in B.items():
        w = f"W{int(k):03d}"
        for m in v["M"]:
            bym[m].append(w)
    for m, ws in bym.items():
        for w in ws[1:]:
            uf.union(ws[0], w)
    lumped = {w: uf.find(w) for w in W}
    comps = defaultdict(list)
    for w in W:
        comps[lumped[w]].append(w)
    multi = {k: v for k, v in comps.items() if len(v) >= 2}
    fine = {w: w for w in W}
    pf = run_lib.heldout_ll(fine, train, test)
    pl = run_lib.heldout_ll(lumped, train, test)
    ntok = sum(x[1] for x in pf)
    trc = Counter(s for q in train for s in q)
    out = {"n_train": len(train), "n_test": len(test), "n_test_tokens": ntok,
           "n_W_labels": len(W), "n_W_in_train": len(trc), "n_lumped": len(set(lumped.values())),
           "n_lumped_in_train": len({lumped[w] for w in trc}),
           "fine_minus_lumped": run_lib.boot_diff(pf, pl), "components": []}
    log("ICIT fine-lumped", out["fine_minus_lumped"], len(W), out["n_lumped"])
    helpful = 0; extra = 0; hurt = 0
    for k, mem in sorted(multi.items(), key=lambda kv: -sum(trc[w] for w in kv[1])):
        mp = dict(lumped)
        for w in mem:
            mp[w] = w
        d = run_lib.boot_diff(run_lib.heldout_ll(mp, train, test), pl)
        ms = sorted({m for w in mem for m in (B.get(str(int(w[1:])), {}).get("M", []))})
        row = {"W": mem, "M": ms, "train_tokens": [trc[w] for w in mem], **d}
        out["components"].append(row)
        if d["lo"] > 0:
            helpful += 1; extra += len(mem) - 1
        if d["hi"] < 0:
            hurt += 1
        log(mem, ms, row["train_tokens"], round(d["total_d"], 2), round(d["lo"], 5), round(d["hi"], 5))
    out["n_components"] = len(multi); out["split_helps"] = helpful; out["split_hurts"] = hurt
    out["preferred_W_size"] = out["n_lumped"] + extra
    # rare-sign side: how many W labels have <3 train tokens (the bulk of the 400-vs-700 gap)
    out["W_train_tokens_hist"] = {"0": len(W) - len(trc), "1-2": sum(1 for v in trc.values() if v <= 2),
                                  "3-9": sum(1 for v in trc.values() if 3 <= v <= 9),
                                  "10+": sum(1 for v in trc.values() if v >= 10)}
    # merge path on ICIT, context only (no W drawings): from fine W downward
    pool = sorted(w for w, n in trc.items() if n >= 1)
    C = sl.context_sim(train, pool)
    S_ctx = sl.pct_sim(1 - C)
    cands = sl.candidate_pairs(pool, S_ctx, S_ctx, "ctx")
    path = run_lib.merge_path(train, test, cands, step=10)
    out["path_ctx"] = path
    log("ICIT ctx path argmax", path["argmax_labels"], path["boot95"], "start", path["n_labels_start"])
    out["sec"] = time.time() - t0
    json.dump(out, open(OUT / "i2.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    {"i1": i1, "i2": i2}[sys.argv[1]]()
