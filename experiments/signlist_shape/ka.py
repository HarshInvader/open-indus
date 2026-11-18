"""Known-answer tests (prereg K1, K2).
    board/run.sh .venv/bin/python -I experiments/signlist_shape/ka.py k1   # PC + PE real variants
    board/run.sh .venv/bin/python -I experiments/signlist_shape/ka.py k2   # planted allographs in Indus dev
Appends one JSON row per condition to out/ka.jsonl (resumable: finished conditions are skipped)."""
import sys, json, re, random, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
import sl, run_lib  # noqa
from corpus.load import dev_heldout, runs  # noqa

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
JL = OUT / "ka.jsonl"
PCD = ROOT / "experiments/protocuneiform"
done = {json.loads(l)["cond"] for l in open(JL)} if JL.exists() else set()


def log(*a):
    print(*a, flush=True)


def emit(row):
    with open(JL, "a") as f:
        f.write(json.dumps(row, default=float) + "\n")


NUM = re.compile(r"^\d+\(")


def base(s):
    return s.split("~")[0]


def load_script(name):
    L = json.load(open(PCD / ("pc_lines.json" if name == "PC" else "pe_lines.json")))
    seqs = []
    for l in L:
        q = [t for t in l["tokens"] if t != "," and not NUM.match(t)]
        if q:
            seqs.append(tuple(q))
    seqs = sorted(set(seqs))
    random.Random(0).shuffle(seqs)
    return [list(q) for q in seqs]


def masks_for(name, signs):
    d = PCD / ("raw/pc_cdli/archsigns" if name == "PC" else "pe_signs")
    ext = ".jpg" if name == "PC" else ".png"
    out = {}
    for s in signs:
        p = d / (s + ext)
        if p.exists():
            ink = sl.ink_of(p)
            if name == "PC":
                ink = sl.first_exemplar(ink)
            if ink.sum() > 0:
                out[s] = sl.norm_mask(ink)
    return out


def k1(name, size):
    cond = f"K1_{name}_{size}"
    if cond in done:
        return
    t0 = time.time()
    seqs = load_script(name)
    if size == "indus":
        train, test = seqs[:2300], seqs[2300:3000]
    else:
        cut = int(0.8 * len(seqs)); train, test = seqs[:cut], seqs[cut:]
    tr_signs = sorted({s for q in train for s in q})
    masks = masks_for(name, tr_signs)
    pool = [s for s in tr_signs if s in masks]
    log(cond, "train", len(train), "test", len(test), "signs", len(tr_signs), "pool", len(pool))
    res, S_shape, S_ctx = run_lib.run_modes(train, pool, masks, log=log)
    row = {"cond": cond, "n_train": len(train), "n_test": len(test), "n_signs_train": len(tr_signs), "pool": len(pool)}
    n_true_pairs = sum(1 for i in range(len(pool)) for j in range(i + 1, len(pool)) if base(pool[i]) == base(pool[j]))
    n_pairs = len(pool) * (len(pool) - 1) // 2
    row["true_pairs_in_pool"] = n_true_pairs; row["pair_base_rate"] = n_true_pairs / n_pairs
    for mode, r in res.items():
        prf = sl.pair_prf(r["mapping"], pool, base)
        cand_true = sum(base(a) == base(b) for a, b, _ in r["cands"])
        acc_true = sum(base(a) == base(b) for a, b, *_ in r["accepted"])
        row[mode] = {"pair_prf": prf, "n_cands": len(r["cands"]), "cand_true_rate": cand_true / max(1, len(r["cands"])),
                     "n_accepted": len(r["accepted"]), "accepted_true": acc_true,
                     "merge_precision": acc_true / max(1, len(r["accepted"])),
                     "accepted": [(a, b, round(d, 2)) for a, b, d, _ in r["accepted"]][:60]}
        log(mode, prf, "merge-level precision", row[mode]["merge_precision"], "cand true rate", row[mode]["cand_true_rate"])
    # calibration: true merge vs fine, greedy vs fine on held-out
    allsigns = sorted({s for q in train + test for s in q})
    fine = {s: s for s in allsigns}
    truth = {s: base(s) for s in allsigns}
    pf = run_lib.heldout_ll(fine, train, test)
    pt = run_lib.heldout_ll(truth, train, test)
    row["truth_minus_fine"] = run_lib.boot_diff(pt, pf)
    row["n_labels_fine"] = len(set(fine.values())); row["n_labels_truth"] = len(set(truth.values()))
    for mode in res:
        mp = {s: res[mode]["mapping"].get(s, s) for s in allsigns}
        row[mode]["heldout_minus_fine"] = run_lib.boot_diff(run_lib.heldout_ll(mp, train, test), pf)
    # does the 'both' greedy beat ctx on held-out?
    path = run_lib.merge_path(train, test, res["both"]["cands"], step=10, max_merges=600)
    row["path"] = {k: v for k, v in path.items()}
    row["sec"] = time.time() - t0
    log(cond, "truth-fine", row["truth_minus_fine"], "path argmax", path["argmax_labels"], path["boot95"],
        "fine", row["n_labels_fine"], "truth", row["n_labels_truth"], f"{row['sec']:.0f}s")
    emit(row)


def indus_masks(signs):
    out = {}
    for s in signs:
        p = ROOT / "data/sign_images" / f"{s}.png"
        if p.exists():
            out[s] = sl.norm_mask(sl.ink_of(p))
    return out


def k2(seed):
    cond = f"K2_seed{seed}"
    if cond in done:
        return
    t0 = time.time()
    dev, _ = dev_heldout()
    train = [r for t in dev for r in runs(t["seq"])]
    from collections import Counter
    c = Counter(s for q in train for s in q)
    elig = sorted(s for s, n in c.items() if n >= 20)
    rng = random.Random(seed); nrng = np.random.default_rng(seed)
    picked = sorted(rng.sample(elig, 30))
    masks = indus_masks(sorted(c))
    new = []
    for q in train:
        new.append([(s + (".a" if rng.random() < 0.5 else ".b")) if s in picked else s for s in q])
    for s in picked:
        masks[s + ".a"] = masks[s]
        masks[s + ".b"] = sl.norm_mask(sl.perturb(masks[s] > 0, nrng))
        del masks[s]
    pool = sorted({s for q in new for s in q if s in masks})
    res, *_ = run_lib.run_modes(new, pool, masks, log=log)
    row = {"cond": cond, "picked": picked, "pool": len(pool)}
    planted = {(s + ".a", s + ".b") for s in picked}
    for mode, r in res.items():
        acc = r["accepted"]
        hit = sum((a, b) in planted or (b, a) in planted for a, b, *_ in acc)
        touch = [x for x in acc if x[0][-2:] in (".a", ".b") or x[1][-2:] in (".a", ".b")]
        # recall counted on the final partition (a planted pair may be joined through a chain)
        mp = r["mapping"]
        rejoined = sum(mp[s + ".a"] == mp[s + ".b"] for s in picked)
        row[mode] = {"accepted": len(acc), "direct_hits": hit, "touch_planted": len(touch),
                     "recall": rejoined / 30, "precision": hit / max(1, len(touch)),
                     "other_merges": len(acc) - len(touch)}
        log(cond, mode, row[mode])
    row["sec"] = time.time() - t0
    emit(row)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "k1":
        for name in ("PC", "PE"):
            for size in ("indus", "full"):
                k1(name, size)
    elif what == "k2":
        for seed in (1, 2, 3):
            k2(seed)
