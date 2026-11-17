"""Board #18: bench of the IIT Hyderabad masked-sign restoration release (Zenodo 24164070).
Prereg: docs/prereg/bench_restoration.md. Reads the deposit as data only; none of its code is run.
Run: .venv/bin/python -I experiments/bench_restoration/bench.py
"""
import csv, json, sys
from collections import Counter, defaultdict
from math import log
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts  # noqa
from corpus.build import _close  # noqa

D = HERE / "raw/dep/zenodo_deposit/data"
rng = np.random.default_rng(18)

seqs = {}
for t in m77_texts():
    k = str(t["text_no"]) if t["side"] == 0 else f"{t['text_no']}.{t['side']}"
    seqs.setdefault(k, [s for s in t["seq"] if s != "|"])

fa = list(csv.DictReader(open(D / "fold_assignments.csv")))
train = [r["text_id"] for r in fa if r["split"] in ("train", "val", "validation")]
test = [r["text_id"] for r in fa if r["split"] == "test"]
print("splits", Counter(r["split"] for r in fa))
ex = list(csv.DictReader(open(D / "masked_positions_exhaustive.csv")))
P = np.load(D / "predictions/test_probabilities.npz")
sign_ids = list(P["sign_ids"])
col = {f"M{int(s)}": i for i, s in enumerate(sign_ids)}
truth = [seqs[r["text_id"]][int(r["position_0based"])] for r in ex]
tcol = np.array([col.get(s, -1) for s in truth])
print("truth signs outside 1..417:", int((tcol < 0).sum()))


def metrics_from_probs(prob):
    out = []
    for r in range(len(ex)):
        if tcol[r] < 0:
            out.append((0, 0, 0.0)); continue
        p = prob[r]
        rank = int((p > p[tcol[r]]).sum()) + 1
        out.append((rank == 1, rank <= 5, 1 / rank))
    return np.array(out, float)


res = {"n_positions": len(ex), "n_test_texts": len(set(r["text_id"] for r in ex))}
M = {m: metrics_from_probs(P[m]) for m in ("kn3", "transformer", "blend")}

# leakage
train_seqs = [seqs[t] for t in train]
train_set = {tuple(s) for s in train_seqs}
leak = {}
for t in set(r["text_id"] for r in ex):
    s = seqs[t]
    exact = tuple(s) in train_set
    fam = exact or any(_close(s, u) or _close(u, s) for u in train_seqs if abs(len(u) - len(s)) <= 20)
    leak[t] = (exact, fam)
is_leak = np.array([leak[r["text_id"]][1] for r in ex])
res["leak"] = {"test_texts_exact_copy_in_train": sum(v[0] for v in leak.values()),
               "test_texts_family_in_train": sum(v[1] for v in leak.values()),
               "n_test_texts": len(leak), "positions_leaked": int(is_leak.sum())}

# our baselines
uni = Counter(s for s in train_seqs for s in s)
V = sorted(set(uni) | set(col))
Vn = len(V)
tri, bi_ctx, bi, uni_ctx = Counter(), Counter(), Counter(), Counter()
foll2, foll1 = defaultdict(set), defaultdict(set)
for s in train_seqs:
    x = ["<s>", "<s>"] + s + ["</s>"]
    for i in range(2, len(x)):
        a, b, c = x[i - 2], x[i - 1], x[i]
        tri[(a, b, c)] += 1; bi_ctx[(a, b)] += 1; foll2[(a, b)].add(c)
        bi[(b, c)] += 1; uni_ctx[b] += 1; foll1[b].add(c)
NU = sum(uni.values()) + 1
Dd = 0.75


def p_uni(c):
    return (uni.get(c, 0) + 1) / (NU + Vn)


def p_bi(b, c):
    n = uni_ctx.get(b, 0)
    if not n:
        return p_uni(c)
    return max(bi.get((b, c), 0) - Dd, 0) / n + Dd * len(foll1[b]) / n * p_uni(c)


def p_tri(a, b, c):
    n = bi_ctx.get((a, b), 0)
    if not n:
        return p_bi(b, c)
    return max(tri.get((a, b, c), 0) - Dd, 0) / n + Dd * len(foll2[(a, b)]) / n * p_bi(b, c)


def ours_scores(s, i):
    x = ["<s>", "<s>"] + s + ["</s>"]
    j = i + 2
    sc = np.zeros(len(sign_ids))
    for k, sid in enumerate(sign_ids):
        x[j] = f"M{int(sid)}"
        lp = 0.0
        for m in range(j, min(j + 3, len(x))):
            lp += log(p_tri(x[m - 2], x[m - 1], x[m]))
        sc[k] = lp
    return sc


ours = np.array([ours_scores(seqs[r["text_id"]], int(r["position_0based"])) for r in ex])
M["ours_trigram"] = metrics_from_probs(ours)
uv = np.array([log(p_uni(f"M{int(s)}")) for s in sign_ids])
M["unigram"] = metrics_from_probs(np.tile(uv, (len(ex), 1)))

def summ(mask):
    return {m: {"hit1": round(100 * v[mask, 0].mean(), 2), "hit5": round(100 * v[mask, 1].mean(), 2),
                "mrr": round(v[mask, 2].mean(), 4), "n": int(mask.sum())} for m, v in M.items()}

allm = np.ones(len(ex), bool)
res["all"] = summ(allm)
res["clean"] = summ(~is_leak)
res["leaked"] = summ(is_leak)

# paired bootstrap over texts on clean positions
tids = np.array([r["text_id"] for r in ex])
clean_t = sorted(set(tids[~is_leak]))
idx = {t: np.where((tids == t) & ~is_leak)[0] for t in clean_t}


def boot(a, b):
    d_obs = M[a][~is_leak, 0].mean() - M[b][~is_leak, 0].mean()
    ds = []
    for _ in range(10000):
        pick = rng.choice(len(clean_t), len(clean_t))
        rows = np.concatenate([idx[clean_t[i]] for i in pick])
        ds.append(M[a][rows, 0].mean() - M[b][rows, 0].mean())
    ds = np.array(ds)
    return {"diff_hit1_pts": round(100 * d_obs, 2), "ci95": [round(100 * np.quantile(ds, .025), 2), round(100 * np.quantile(ds, .975), 2)],
            "p_one_sided": float((ds <= 0).mean())}

best_ng = max(["kn3", "ours_trigram"], key=lambda m: M[m][~is_leak, 0].mean())
res["best_ngram_clean"] = best_ng
res["transformer_minus_best_ngram_clean"] = boot("transformer", best_ng)
res["blend_minus_best_ngram_clean"] = boot("blend", best_ng)
res["kn3_minus_transformer_clean"] = boot("kn3", "transformer")
for k, v in res.items():
    print(k, json.dumps(v))
json.dump(res, open(HERE / "results.json", "w"), indent=1)
