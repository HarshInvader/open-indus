"""Stamp detector: split, train, gate, sweep. Prereg docs/prereg/stamp_detector.md (sealed; hash in HASHES.txt).
Run with the vision venv from the repo root:
  .venv-vision/bin/python -I experiments/stamp_detector/gate.py split    -> out/split.json, out/lists/*.txt
  .venv-vision/bin/python -I experiments/stamp_detector/gate.py train    -> out/model.npz (threshold fixed on train only)
  .venv-vision/bin/python -I experiments/stamp_detector/gate.py test     -> out/gate.json (run ONCE)
  .venv-vision/bin/python -I experiments/stamp_detector/gate.py sweep    -> out/review_queue.csv (only if the gate passed)
Embeddings come from embed.py in raw/emb/<stem>.npz (stem = Yale nat id, or control name)."""
import csv, json, re, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
RAW, OUT = HERE / "raw", HERE / "out"
EMB = RAW / "emb"
SEED = 20261120
N_EARLY_TRAIN, N_EARLY_TEST, N_LATE = 400, 300, 400
EARLY = ("ur3", "ob")            # records files for the sweep population
LATE = ("nb", "ach", "hel")      # records files for N-late (train only)
RECALL_BAR, FP_BAR = 0.80, 0.02


def recs(name):
    p = RAW / f"records_{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def period(r):
    m = re.search(r"Period = (.+?)(?:,|$)", " ".join(t for t in r["texts"] if "Period =" in t))
    return m.group(1).strip() if m else ""


def split():
    rng = np.random.default_rng(SEED)
    rows = list(csv.DictReader((HERE / "labels_pos.csv").open()))
    pos = sorted({r["nat"] for r in rows if r["label"] == "yes"})
    rng.shuffle(pos)
    k = round(0.6 * len(pos))
    stamp_ids = {r["id"] for r in recs("stamp")} | {r["id"] for r in recs("pos")}
    early = {r["id"]: r for n in EARLY for r in recs(n) if r["nat"] and r["id"] not in stamp_ids}
    early_ids = sorted(early)
    pick = rng.choice(len(early_ids), N_EARLY_TRAIN + N_EARLY_TEST, replace=False)
    ne = [early[early_ids[i]]["nat"][0] for i in pick]
    late = {r["id"]: r for n in LATE for r in recs(n) if r["nat"] and r["id"] not in stamp_ids}
    late_ids = sorted(late)
    pl = rng.choice(len(late_ids), min(N_LATE, len(late_ids)), replace=False)
    nl = [late[late_ids[i]]["nat"][0] for i in pl]
    ctrl = sorted(p.stem for p in (RAW / "ctrl").glob("*.jpg"))
    s = dict(seed=SEED, P_train=pos[:k], P_test=pos[k:], C=ctrl, N_early_train=ne[:N_EARLY_TRAIN],
             N_early_test=ne[N_EARLY_TRAIN:], N_late=nl)
    gate_nat = set(ne) | set(pos)
    s["sweep"] = sorted(r["nat"][0] for r in early.values() if r["nat"][0] not in gate_nat)
    OUT.mkdir(exist_ok=True); (OUT / "lists").mkdir(exist_ok=True)
    (OUT / "split.json").write_text(json.dumps(s))
    img = lambda n: str(RAW / "img" / f"{n}.jpg")
    for key in ("N_early_train", "N_early_test", "N_late", "P_train", "P_test"):
        (OUT / "lists" / f"{key}.txt").write_text("\n".join(img(n) for n in s[key]) + "\n")
    (OUT / "lists" / "sweep.txt").write_text("\n".join(img(n) for n in s["sweep"]) + "\n")
    print({k: len(v) for k, v in s.items() if isinstance(v, list)})


def load(stem):
    p = EMB / f"{stem}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    return z["feats"].astype(np.float32), z["xy"]


def fit_mil(pos, neg, rounds=3):
    """pos, neg: lists of tile matrices. Round 1: all positive-image tiles positive; rounds 2-3: top 3 per image."""
    Xn = np.concatenate([n for n in neg if len(n)])
    clf = None
    for r in range(rounds):
        if r == 0:
            Xp = np.concatenate([p for p in pos if len(p)])
        else:
            Xp = np.concatenate([p[np.argsort(-clf.decision_function(p))[:3]] for p in pos if len(p)])
        X = np.concatenate([Xp, Xn]); y = np.r_[np.ones(len(Xp)), np.zeros(len(Xn))]
        clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(X, y)
    return clf


def score(clf, F):
    if F is None or not len(F[0]):
        return -np.inf, None
    d = clf.decision_function(F[0]); i = int(np.argmax(d))
    return float(d[i]), F[1][i].tolist()


def get(stems):
    out = {}
    for s in stems:
        f = load(s)
        if f is not None and len(f[0]):
            out[s] = f
    return out


def train():
    s = json.loads((OUT / "split.json").read_text())
    P, NE, NL = get(s["P_train"]), get(s["N_early_train"]), get(s["N_late"])
    print("train images", len(P), len(NE), len(NL), flush=True)
    # out-of-fold threshold on N-early train (5 folds over all train images)
    rng = np.random.default_rng(SEED)
    items = [("p", k) for k in P] + [("e", k) for k in NE] + [("l", k) for k in NL]
    fold = rng.integers(0, 5, len(items))
    oof_e = []
    for f in range(5):
        tr = [it for it, g in zip(items, fold) if g != f]
        te = [it for it, g in zip(items, fold) if g == f and it[0] == "e"]
        src = dict(p=P, e=NE, l=NL)
        clf = fit_mil([P[k][0] for t, k in tr if t == "p"], [src[t][k][0] for t, k in tr if t != "p"])
        oof_e += [score(clf, NE[k])[0] for _, k in te]
        print("fold", f, flush=True)
    thr = float(np.quantile(oof_e, 0.99))
    clf = fit_mil([v[0] for v in P.values()], [v[0] for v in NE.values()] + [v[0] for v in NL.values()])
    np.savez(OUT / "model.npz", coef=clf.coef_, intercept=clf.intercept_, thr=thr)
    print("threshold", thr, "oof flags", sum(x > thr for x in oof_e), "of", len(oof_e))


def model():
    z = np.load(OUT / "model.npz")
    clf = LogisticRegression(); clf.coef_, clf.intercept_, clf.classes_ = z["coef"], z["intercept"], np.array([0., 1.])
    return clf, float(z["thr"])


def test():
    assert not (OUT / "gate.json").exists(), "gate already run once"
    s = json.loads((OUT / "split.json").read_text()); clf, thr = model()
    per = {r["nat"][0]: period(r) for r in recs("pos") if r["nat"]}
    res = {}
    for key in ("P_test", "C", "N_early_test"):
        res[key] = {k: score(clf, load(k)) for k in s[key]}
    missing = {k: sum(v[0] == -np.inf for v in res[k].values()) for k in res}
    pc = {**res["P_test"], **res["C"]}
    recall = float(np.mean([v[0] > thr for v in pc.values()]))
    flags = sorted([k for k, v in res["N_early_test"].items() if v[0] > thr])
    fp_rate = len(flags) / len(res["N_early_test"])
    byp = {}
    for k, v in res["P_test"].items():
        byp.setdefault(per.get(k, "?").split()[0], []).append(v[0] > thr)
    g = dict(threshold=thr, recall_P_test_C=recall, n_P_test_C=len(pc), recall_C=float(np.mean([v[0] > thr for v in res["C"].values()])),
             YBC5447=bool(res["C"].get("YBC5447_yale", (-np.inf,))[0] > thr), recall_by_period={k: [int(sum(v)), len(v)] for k, v in byp.items()},
             n_early_flags=flags, n_early_flag_rate=fp_rate, missing_embeddings=missing,
             recall_pass=recall >= RECALL_BAR, fp_pass_before_review=fp_rate <= FP_BAR,
             note="Flags are reviewed by eye; a flag showing a real stamp counts as a find, not a false flag.",
             scores={k: {kk: vv[0] for kk, vv in v.items()} for k, v in res.items()})
    (OUT / "gate.json").write_text(json.dumps(g, indent=1))
    print({k: g[k] for k in ("threshold", "recall_P_test_C", "n_P_test_C", "recall_C", "YBC5447", "recall_by_period",
                             "n_early_flags", "n_early_flag_rate", "missing_embeddings", "recall_pass", "fp_pass_before_review")})


def sweep():
    g = json.loads((OUT / "gate.json").read_text())
    assert (OUT / "gate_review.json").exists(), "eye review of gate flags must be recorded first"
    rv = json.loads((OUT / "gate_review.json").read_text())
    assert g["recall_pass"] and rv["fp_after_review"] <= FP_BAR, "gate failed: no sweep"
    s = json.loads((OUT / "split.json").read_text()); clf, thr = model()
    meta = {r["nat"][0]: r for n in EARLY for r in recs(n) if r["nat"]}
    rows, n_scored = [], 0
    for k in s["sweep"]:
        sc, xy = score(clf, load(k))
        if sc == -np.inf:
            continue
        n_scored += 1
        if sc > thr:
            r = meta[k]; t = " ".join(r["texts"])
            date = re.search(r"Date = (.+?),", t)
            rows.append(dict(ypm=r.get("ypm", ""), score=round(sc, 3), tile_xy_size=xy, period=period(r),
                             date=date.group(1) if date else "", title=r.get("name", ""),
                             link="https://collections.peabody.yale.edu/search/Record/" + r.get("ypm", "").replace(" ", "-"),
                             image=f"https://manifests.collections.yale.edu/ypm/nat/{k}"))
    rows.sort(key=lambda x: -x["score"])
    with (OUT / "review_queue.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["ypm"]); w.writeheader(); w.writerows(rows)
    print("scored", n_scored, "of", len(s["sweep"]), "flags", len(rows))


if __name__ == "__main__":
    dict(split=split, train=train, test=test, sweep=sweep)[sys.argv[1]]()
