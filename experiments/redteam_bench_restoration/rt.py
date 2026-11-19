"""Red team of experiments/bench_restoration (IIT Hyderabad masked-sign release, Zenodo 24164070).

Independent reimplementation: near-copy detection, KN / Witten-Bell trigrams, Hit@k, bootstrap, split checks.
Does not import or read experiments/bench_restoration code. Prereg: docs/prereg/redteam_bench_restoration.md.

Run (from repo root, through the compute gate):
    board/run.sh .venv/bin/python -I experiments/redteam_bench_restoration/rt.py           # real run
    board/run.sh .venv/bin/python -I experiments/redteam_bench_restoration/rt.py --smoke   # synthetic corpus only
"""
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts  # noqa: E402

DEP = ROOT / "experiments/bench_restoration/raw/dep/zenodo_deposit/data"
SIGNS = [f"M{i}" for i in range(1, 418)]
SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}
REPORTED = {"kn3": 39.56, "transformer": 37.49, "blend": 40.84}
SEED = 20261119
SMOKE = "--smoke" in sys.argv
VARIANTS = ["parpola", "lump_fish", "lump_all", "img_lo"]
BOS, EOS = "<s>", "</s>"


# ---------------------------------------------------------------- data
def load_deposit():
    folds = list(csv.DictReader(open(DEP / "fold_assignments.csv")))
    pos = list(csv.DictReader(open(DEP / "masked_positions_exhaustive.csv")))
    npz = np.load(DEP / "predictions/test_probabilities.npz")
    probs = {k: npz[k] for k in ("kn3", "transformer", "blend")}
    assert list(npz["sign_ids"]) == list(range(1, 418))
    return folds, pos, probs


def m77_by_id():
    out = {}
    for t in m77_texts():
        key = str(t["text_no"]) if t["side"] == 0 else f"{t['text_no']}.{t['side']}"
        assert key not in out
        out[key] = [s for s in t["seq"] if s != "|"]
    return out


def synthetic_corpus(folds, pos):
    """Smoke mode: random texts of the deposit's test lengths, with ~30% of test texts planted as copies
    (exact, one substitution, or contained) of a training text. Truth signs are therefore unrelated to the real ones."""
    rng = np.random.default_rng(1)
    lens = Counter(r["text_id"] for r in pos)
    freq = rng.dirichlet(np.ones(417) * 0.3)
    seqs = {}
    train_ids = [r["text_id"] for r in folds if r["split"] != "test"]
    for r in folds:
        n = lens.get(r["text_id"], int(rng.integers(1, 9)))
        seqs[r["text_id"]] = [SIGNS[j] for j in rng.choice(417, size=n, p=freq)]
    planted = 0
    free = list(rng.permutation(train_ids))
    for tid in lens:
        if rng.random() < 0.30:
            src = list(seqs[tid])                      # plant a copy of the test text INTO a training text
            kind = rng.integers(3)
            if kind == 1 and len(src) >= 4:
                src[int(rng.integers(len(src)))] = SIGNS[int(rng.integers(417))]
            elif kind == 2 and len(src) >= 3:
                src = src + [SIGNS[int(rng.integers(417))]]
            seqs[free.pop()] = src
            planted += 1
    return seqs, planted


# ---------------------------------------------------------------- near copies
def lev_capped(a, b, cap):
    """Sign-level Levenshtein distance, returns cap+1 if it exceeds cap."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        best = cur[0]
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            best = min(best, cur[j])
        if best > cap:
            return cap + 1
        prev = cur
    return prev[-1] if prev[-1] <= cap else cap + 1


def contained(a, b, ja, jb):
    """Shorter text is a contiguous substring of the longer one, shorter >= 3 signs. ja/jb = ' '-padded joins."""
    if len(a) > len(b):
        a, b, ja, jb = b, a, jb, ja
    if len(a) < 3:
        return False
    return ja in jb


def pair_relation(seqs, ids_a, ids_b):
    """For every (a, b) pair that is a near copy under the loosest rule (k<=2 or contained),
    return dict (a,b) -> (dist_capped_at_3, contained, min_len)."""
    rel = {}
    J = {i: " " + " ".join(seqs[i]) + " " for i in set(ids_a) | set(ids_b)}
    for a in ids_a:
        sa = seqs[a]
        for b in ids_b:
            if a == b:
                continue
            sb = seqs[b]
            c = contained(sa, sb, J[a], J[b])
            d = lev_capped(sa, sb, 2) if abs(len(sa) - len(sb)) <= 2 else 3
            if c or d <= 2:
                rel[(a, b)] = (d, c, min(len(sa), len(sb)))
    return rel


def is_copy(info, k, contain):
    d, c, mn = info
    if d == 0:
        return True
    if d <= k and mn >= 4:
        return True
    return contain and c


def leaked_set(rel, test_ids, train_ids, k, contain):
    train = set(train_ids)
    out = set()
    for (a, b), info in rel.items():
        if a in test_ids and b in train and is_copy(info, k, contain):
            out.add(a)
    return out


# ---------------------------------------------------------------- language models
class KN3:
    """Interpolated Kneser-Ney trigram, discount D at every order, uniform base over signs+EOS."""

    def __init__(self, texts, vocab, D=0.75):
        self.D, self.V = D, len(vocab) + 1
        c3, c2h = Counter(), Counter()
        for t in texts:
            p = [BOS, BOS] + t + [EOS]
            for i in range(2, len(p)):
                c3[(p[i - 2], p[i - 1], p[i])] += 1
        self.c3 = c3
        self.c3h, self.t3h = Counter(), Counter()
        cont2 = Counter()  # N1+(. v w)
        for (u, v, w), n in c3.items():
            self.c3h[(u, v)] += n
            self.t3h[(u, v)] += 1
            cont2[(v, w)] += 1
        self.cont2 = cont2
        self.c2h, self.t2h = Counter(), Counter()
        cont1 = Counter()  # N1+(. w) over bigram types
        for (v, w), n in cont2.items():
            self.c2h[v] += n
            self.t2h[v] += 1
            cont1[w] += 1
        self.cont1 = cont1
        self.n1 = sum(cont1.values())
        self.t1 = len(cont1)
        self.cache = {}

    def p1(self, w):
        return max(self.cont1.get(w, 0) - self.D, 0) / self.n1 + self.D * self.t1 / self.n1 / self.V

    def p2(self, v, w):
        h = self.c2h.get(v, 0)
        if h == 0:
            return self.p1(w)
        return max(self.cont2.get((v, w), 0) - self.D, 0) / h + self.D * self.t2h[v] / h * self.p1(w)

    def p3(self, u, v, w):
        key = (u, v, w)
        r = self.cache.get(key)
        if r is not None:
            return r
        h = self.c3h.get((u, v), 0)
        if h == 0:
            r = self.p2(v, w)
        else:
            r = max(self.c3.get(key, 0) - self.D, 0) / h + self.D * self.t3h[(u, v)] / h * self.p2(v, w)
        self.cache[key] = r
        return r


class WB3:
    """Witten-Bell interpolated trigram, uniform base over signs+EOS."""

    def __init__(self, texts, vocab):
        self.V = len(vocab) + 1
        self.c = [Counter(), Counter(), Counter()]   # c[n][(hist..., w)]
        self.h = [Counter(), Counter(), Counter()]   # history totals
        self.t = [Counter(), Counter(), Counter()]   # history types
        for t in texts:
            p = [BOS, BOS] + t + [EOS]
            for i in range(2, len(p)):
                for n in range(3):
                    g = tuple(p[i - n:i + 1])
                    self.c[n][g] += 1
        for n in range(3):
            for g, k in self.c[n].items():
                self.h[n][g[:-1]] += k
                self.t[n][g[:-1]] += 1
        self.cache = {}

    def p(self, hist, w):
        key = hist + (w,)
        r = self.cache.get(key)
        if r is not None:
            return r
        n = len(hist)
        lower = 1.0 / self.V if n == 0 else self.p(hist[1:], w)
        H, T = self.h[n].get(hist, 0), self.t[n].get(hist, 0)
        r = lower if H == 0 else (self.c[n].get(key, 0) + T * lower) / (H + T)
        self.cache[key] = r
        return r

    def p3(self, u, v, w):
        return self.p((u, v), w)


def lm_scores(lm, seq, i):
    """Log-score of every candidate sign at position i (only trigrams touching i)."""
    p = [BOS, BOS] + list(seq) + [EOS]
    j = i + 2
    out = np.empty(417)
    for ci, c in enumerate(SIGNS):
        p[j] = c
        s = 0.0
        for e in (j, j + 1, j + 2):
            if e < len(p):
                s += math.log(lm.p3(p[e - 2], p[e - 1], p[e]))
        out[ci] = s
    return out


def rank_of(scores, truth_idx):
    """1-based rank; ties broken by lower sign id (stable)."""
    t = scores[truth_idx]
    return int(np.sum(scores > t) + np.sum(scores[:truth_idx] == t) + 1)


# ---------------------------------------------------------------- evaluation
def metrics(ranks):
    r = np.asarray(ranks)
    return {"hit1": 100 * float(np.mean(r == 1)), "hit5": 100 * float(np.mean(r <= 5)),
            "mrr": float(np.mean(1.0 / r)), "n": int(len(r))}


def paired_boot(text_of, ranks_a, ranks_b, subset_texts, reps=10000, seed=SEED):
    """Paired bootstrap over texts of Hit@1(a) - Hit@1(b), points."""
    texts = sorted(subset_texts)
    idx = {t: k for k, t in enumerate(texts)}
    ha, hb, nn = np.zeros(len(texts)), np.zeros(len(texts)), np.zeros(len(texts))
    for row, t in enumerate(text_of):
        if t in idx:
            k = idx[t]
            ha[k] += ranks_a[row] == 1
            hb[k] += ranks_b[row] == 1
            nn[k] += 1
    obs = 100 * (ha.sum() - hb.sum()) / nn.sum()
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(texts), size=(reps, len(texts)))
    d = 100 * (ha[draws].sum(1) - hb[draws].sum(1)) / nn[draws].sum(1)
    return {"diff": float(obs), "ci": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_one_sided_a_gt_b": float(np.mean(d <= 0)), "n_texts": len(texts), "n_pos": int(nn.sum())}


def obj_fold(salt, obj):
    return int(hashlib.sha256((salt + obj).encode()).hexdigest()[:8], 16) % 5


def main():
    folds, pos, probs = load_deposit()
    seqs_all = m77_by_id()
    ids = [r["text_id"] for r in folds]
    missing = [i for i in ids if i not in seqs_all]
    assert not missing, missing[:5]
    if SMOKE:
        seqs, planted = synthetic_corpus(folds, pos)
    else:
        seqs, planted = {i: seqs_all[i] for i in ids}, None

    split = {r["text_id"]: r["split"] for r in folds}
    obj = {r["text_id"]: r["object_id"] for r in folds}
    train_ids = [i for i in ids if split[i] in ("train", "val")]
    test_ids = sorted(set(r["text_id"] for r in pos), key=ids.index)
    text_of = [r["text_id"] for r in pos]
    pos0 = [int(r["position_0based"]) for r in pos]
    assert [int(r["row"]) for r in pos] == list(range(len(pos)))
    for t in test_ids:
        assert split[t] == "test"
    truth = np.array([SIGN_IDX[seqs[t][i]] for t, i in zip(text_of, pos0)])
    lens_ok = all(len(seqs[t]) == sum(1 for x in text_of if x == t) for t in test_ids)
    res = {"smoke": SMOKE, "planted_copies": planted, "n_train_pool": len(train_ids), "n_test_texts": len(test_ids),
           "n_positions": len(pos), "test_lengths_match_position_counts": lens_ok}

    # ---- S1 split rule
    s1 = sum(int(r["fold"]) == obj_fold("ebuds:", r["object_id"]) for r in folds)
    val_ok = sum((r["split"] == "val") == (obj_fold("ebuds:", r["object_id"]) != 0 and
                 int(hashlib.sha256(("ebuds-val:" + r["object_id"]).encode()).hexdigest()[:8], 16) % 10 == 0)
                 for r in folds)
    res["S1_fold_rule_matches"] = f"{s1}/{len(folds)}"
    res["S1_val_rule_matches"] = f"{val_ok}/{len(folds)}"

    # ---- ranks for every model
    ranks = {}
    for m, P in probs.items():
        ranks[m] = [rank_of(P[r].astype(np.float64), truth[r]) for r in range(len(pos))]
    kn = KN3([seqs[i] for i in train_ids], SIGNS)
    wb = WB3([seqs[i] for i in train_ids], SIGNS)
    uni = Counter(s for i in train_ids for s in seqs[i])
    uni_scores = np.array([uni.get(s, 0) for s in SIGNS], dtype=float)
    ranks["my_kn3"], ranks["my_wb3"], ranks["unigram"] = [], [], []
    for r in range(len(pos)):
        t, i = text_of[r], pos0[r]
        ranks["my_kn3"].append(rank_of(lm_scores(kn, seqs[t], i), truth[r]))
        ranks["my_wb3"].append(rank_of(lm_scores(wb, seqs[t], i), truth[r]))
        ranks["unigram"].append(rank_of(uni_scores, truth[r]))

    # ---- K1 rebuild
    res["all_positions"] = {m: metrics(rk) for m, rk in ranks.items()}
    res["K1_rebuild_gap"] = {m: res["all_positions"][m]["hit1"] - REPORTED[m] for m in REPORTED}
    res["K1_trips"] = any(abs(g) > 0.5 for g in res["K1_rebuild_gap"].values())

    # ---- near-copy relation (test x train) for M77 and sign-list variants
    def relabel(var):
        part = json.load(open(ROOT / "experiments/signlist_robustness/variants.json"))["partitions"][var]
        return {i: [part.get(s, s) for s in seqs[i]] for i in ids}

    rel_m77 = pair_relation(seqs, test_ids, train_ids)
    grid = {}
    leak_sets = {}
    for k in (0, 1, 2):
        for contain in (True, False):
            L = leaked_set(rel_m77, set(test_ids), train_ids, k, contain)
            leak_sets[(k, contain)] = L
            grid[f"k{k}_contain{contain}"] = {"leaked": len(L), "share": 100 * len(L) / len(test_ids)}
    for var in VARIANTS:
        sv = relabel(var)
        rv = pair_relation(sv, test_ids, train_ids)
        L = leaked_set(rv, set(test_ids), train_ids, 1, True)
        leak_sets[var] = L
        grid[f"{var}_k1_containTrue"] = {"leaked": len(L), "share": 100 * len(L) / len(test_ids)}
    res["leak_grid"] = grid
    primary = leak_sets[(1, True)]
    res["K2_primary_leaked"] = len(primary)
    res["K2_primary_share"] = 100 * len(primary) / len(test_ids)
    res["K2_trips"] = not (30 <= res["K2_primary_share"] <= 42)
    exact = leak_sets[(0, False)]
    res["exact_copies"] = len(exact)

    # ---- clean / leaked scoring per leak definition
    def split_eval(L):
        clean = set(test_ids) - L
        rows_c = [r for r, t in enumerate(text_of) if t in clean]
        rows_l = [r for r, t in enumerate(text_of) if t in L]
        out = {"clean_texts": len(clean), "clean_pos": len(rows_c), "leaked_pos": len(rows_l),
               "clean": {m: metrics([ranks[m][r] for r in rows_c]) for m in ranks},
               "leaked": {m: metrics([ranks[m][r] for r in rows_l]) for m in ranks} if rows_l else {}}
        out["boot_tf_minus_mykn3"] = paired_boot(text_of, ranks["transformer"], ranks["my_kn3"], clean)
        out["boot_blend_minus_mykn3"] = paired_boot(text_of, ranks["blend"], ranks["my_kn3"], clean)
        return out

    res["primary"] = split_eval(primary)
    P_ = res["primary"]
    res["primary"]["boot_tf_minus_mywb3"] = paired_boot(text_of, ranks["transformer"], ranks["my_wb3"],
                                                        set(test_ids) - primary)
    res["primary"]["boot_tf_minus_theirkn3"] = paired_boot(text_of, ranks["transformer"], ranks["kn3"],
                                                           set(test_ids) - primary)
    res["K3_tf_minus_mykn3_clean"] = P_["clean"]["transformer"]["hit1"] - P_["clean"]["my_kn3"]["hit1"]
    res["K3_trips"] = res["K3_tf_minus_mykn3_clean"] > 3.0
    res["K4_blend_leaked_minus_clean"] = P_["leaked"]["blend"]["hit1"] - P_["clean"]["blend"]["hit1"]
    res["K4_trips"] = res["K4_blend_leaked_minus_clean"] <= 5.0

    sens = {}
    for key, L in leak_sets.items():
        name = key if isinstance(key, str) else f"k{key[0]}_contain{key[1]}"
        e = split_eval(L)
        sens[name] = {"leaked_texts": len(L),
                      "clean_hit1": {m: e["clean"][m]["hit1"] for m in ("transformer", "blend", "kn3", "my_kn3")},
                      "tf_minus_mykn3": e["boot_tf_minus_mykn3"],
                      "blend_leaked_minus_clean": (e["leaked"]["blend"]["hit1"] - e["clean"]["blend"]["hit1"])
                      if e["leaked"] else None}
    res["sensitivity"] = sens
    res["tie_depends_on_definition"] = any(
        v["tf_minus_mykn3"]["diff"] > 3 and v["tf_minus_mykn3"]["ci"][0] > 0 for v in sens.values())

    # ---- S2 families across objects; S3 random object splits
    res["S2_leaked_with_copy_in_other_object"] = sum(
        1 for (a, b), info in rel_m77.items() if a in primary and b in set(train_ids) and is_copy(info, 1, True)
        and obj[a] != obj[b]) > 0
    res["S2_leaked_texts_whose_copy_shares_object"] = len({a for (a, b), info in rel_m77.items()
                                                           if a in primary and b in set(train_ids)
                                                           and is_copy(info, 1, True) and obj[a] == obj[b]})
    rel_all = pair_relation(seqs, ids, ids)
    nbrs = defaultdict(set)
    for (a, b), info in rel_all.items():
        if is_copy(info, 1, True):
            nbrs[a].add(b)
    shares = []
    for s in range(200):
        f = {i: obj_fold(f"rt:{s}:", obj[i]) for i in ids}
        te = [i for i in ids if f[i] == 0 and len(seqs[i]) >= 2]
        tr = {i for i in ids if f[i] != 0}
        shares.append(100 * sum(1 for i in te if nbrs[i] & tr) / len(te))
    res["S3_random_object_split_share"] = {"median": float(np.median(shares)),
                                           "p2.5": float(np.percentile(shares, 2.5)),
                                           "p97.5": float(np.percentile(shares, 97.5)),
                                           "their_share_percentile": float(np.mean(np.array(shares)
                                                                                   <= res["K2_primary_share"]) * 100)}

    trips = [k for k in ("K1", "K2", "K3", "K4") if res[f"{k}_trips"]]
    b = P_["boot_tf_minus_mykn3"]
    refuted = res["K2_trips"] and res["K2_primary_share"] < 15 and res["K3_trips"] and b["ci"][0] > 0
    res["trips"] = trips
    res["verdict"] = "REFUTED" if refuted else ("WEAKENED" if trips else "SURVIVES")

    out = HERE / ("results_smoke.json" if SMOKE else "results.json")
    json.dump(res, open(out, "w"), indent=1, default=str)
    short = {k: res[k] for k in ("verdict", "trips", "K1_rebuild_gap", "K2_primary_leaked", "K2_primary_share",
                                 "K3_tf_minus_mykn3_clean", "K4_blend_leaked_minus_clean", "S1_fold_rule_matches",
                                 "S3_random_object_split_share", "planted_copies")}
    print(json.dumps(short, indent=1))


if __name__ == "__main__":
    main()
