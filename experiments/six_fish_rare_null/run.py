"""Starter task S4: rare-sign- and length-matched null for 'six then fish' (README #5).

Pre-registration: docs/prereg/2026-11-27_s4_six_fish_rare_null.md
Run from repository root:
    PYTHONHASHSEED=0 .venv/bin/python -I experiments/six_fish_rare_null/run.py
Development/dry-run check (M77 dev + planted controls only; never touches held-out or ICIT):
    PYTHONHASHSEED=0 .venv/bin/python -I experiments/six_fish_rare_null/run.py --dev-check
"""
import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binom, binomtest

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from corpus.load import dev_heldout, icit_texts, runs  # noqa: E402

NUM_M = frozenset({
    "M97", "M98", "M102", "M104", "M105", "M106", "M107", "M108", "M109",
    "M110", "M111", "M112", "M114", "M115", "M116", "M117", "M121",
})
NUM_W = frozenset(
    {f"W{i:03d}" for i in list(range(1, 21)) + [25, 26, 27, 28]} - {"W002", "W012"}
)
M77_SITES = frozenset({"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"})


# ---------------------------------------------------------------------------
# Helpers: deterministic deduplication, edit-1 families, exact Poisson-binomial
# ---------------------------------------------------------------------------
def distinct_by_seq(records):
    seen, out = set(), []
    for r in records:
        k = tuple(r["seq"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def edit1(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def dedup_edit1_families(records):
    """Single-linkage Levenshtein <= 1 over sign-only token tuples; keeps first record per cluster."""
    seqs = [tuple(s for ru in runs(r["seq"]) for s in ru) for r in records]
    n = len(seqs)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    bylen = defaultdict(list)
    for i, s in enumerate(seqs):
        bylen[len(s)].append(i)
    for i, s in enumerate(seqs):
        for L in (len(s), len(s) + 1):
            for j in bylen.get(L, ()):
                if j <= i and L == len(s):
                    continue
                if edit1(s, seqs[j]):
                    ri, rj = find(i), find(j)
                    if ri != rj:
                        if ri < rj:
                            par[rj] = ri
                        else:
                            par[ri] = rj

    kept = []
    seen_roots = set()
    for i, r in enumerate(records):
        root = find(i)
        if root not in seen_roots:
            seen_roots.add(root)
            kept.append(r)
    return kept


def poisson_binomial_sf(probs, k_obs):
    """Exact P(sum_i Bernoulli(p_i) >= k_obs) via dynamic programming."""
    n = len(probs)
    if k_obs <= 0:
        return 1.0
    if k_obs > n:
        return 0.0
    dp = [0.0] * (n + 1)
    dp[0] = 1.0
    for idx, p in enumerate(probs):
        q = 1.0 - p
        for j in range(idx + 1, 0, -1):
            dp[j] = dp[j] * q + dp[j - 1] * p
        dp[0] *= q
    s = sum(dp[k_obs:])
    return float(min(1.0, max(0.0, s)))


def clopper_pearson_ci(k, n, alpha=0.05):
    if n == 0:
        return [None, None]
    ci = binomtest(k, n).proportion_ci(confidence_level=1.0 - alpha, method="exact")
    return [round(float(ci.low), 4), round(float(ci.high), 4)]


def holm_adjust(pvals_dict):
    """Deterministic Holm-Bonferroni over a dict {name: pval}."""
    keys = sorted(pvals_dict.keys(), key=lambda k: (pvals_dict[k], k))
    m = len(keys)
    adj = {}
    running = 0.0
    for idx, k in enumerate(keys):
        val = min(1.0, pvals_dict[k] * (m - idx))
        running = max(running, val)
        adj[k] = running
    return adj


# ---------------------------------------------------------------------------
# Feature extraction: non-final token records with (L, r) strata
# ---------------------------------------------------------------------------
def build_sign_counts(texts):
    c = Counter()
    for t in texts:
        for ru in runs(t["seq"]):
            c.update(ru)
    return c


def extract_nonfinal_records(
    texts,
    ref_counts,
    rare_thresh=10,
    leave_one_text_out=False,
    rare_scope="text",
    type_key="object_type",
):
    """Extract every non-final token inside break-free runs of length >= 2.

    rare_scope:
      - 'text': rare tokens across all sign tokens in the text
      - 'run': rare tokens inside the contiguous run
      - 'excl_trigger': rare tokens in the text excluding the current trigger token
    """
    records = []
    for tid, t in enumerate(texts):
        rlist = runs(t["seq"])
        toks = [s for ru in rlist for s in ru]
        L_text = len(toks)
        if L_text < 2:
            continue
        if leave_one_text_out:
            c_in_t = Counter(toks)
            is_rare = lambda s: (ref_counts[s] - c_in_t[s]) < rare_thresh
        else:
            is_rare = lambda s: ref_counts[s] < rare_thresh
        r_text = sum(1 for s in toks if is_rare(s))
        for ru in rlist:
            L_run = len(ru)
            if L_run < 2:
                continue
            r_run = sum(1 for s in ru if is_rare(s))
            for i in range(L_run - 1):
                a, b = ru[i], ru[i + 1]
                if rare_scope == "text":
                    r_val = r_text
                elif rare_scope == "run":
                    r_val = r_run
                elif rare_scope == "excl_trigger":
                    r_val = r_text - (1 if is_rare(a) else 0)
                else:
                    raise ValueError(f"Unknown rare_scope: {rare_scope}")
                records.append({
                    "tid": tid,
                    "trigger": a,
                    "follower": b,
                    "L_text": L_text,
                    "L_run": L_run,
                    "r_val": r_val,
                    "r_text": r_text,
                    "is_init": i == 0,
                    "site": t.get("site", ""),
                    "otype": t.get(type_key, ""),
                    "id": str(t.get("id", f"{t.get('text_no', tid)}.{t.get('side', 1)}")),
                })
    return records


# ---------------------------------------------------------------------------
# Stratified matched null engine (exact Poisson-binomial + Monte Carlo)
# ---------------------------------------------------------------------------
def make_key_tuple(rec, mode):
    L = min(rec["L_text"], 9)
    r = min(rec["r_val"], 3)
    if mode == "N0":
        return (L,)
    if mode in ("N1", "N2"):
        return (L, r)
    if mode == "N3":
        return (L, r, bool(rec["is_init"]))
    raise ValueError(f"Unknown mode: {mode}")


def make_pools(ref_records, target_fish, mode):
    pools = defaultdict(list)
    for rec in ref_records:
        k = make_key_tuple(rec, mode)
        pools[k].append(1 if rec["follower"] == target_fish else 0)
    return {k: np.array(v, dtype=np.int8) for k, v in pools.items()}


def resolve_stratum(rec, mode, pools, min_pool=5):
    L = min(rec["L_text"], 9)
    r = min(rec["r_val"], 3)
    exact_key = make_key_tuple(rec, mode)

    if mode == "N0":
        for LL in range(L, 0, -1):
            k = (LL,)
            if len(pools.get(k, ())) >= min_pool:
                return k, k != exact_key
        best = max(sorted(pools.keys()), key=lambda x: len(pools[x]))
        return best, True

    if mode in ("N1", "N2"):
        for LL in range(L, 0, -1):
            for rr in range(r, -1, -1):
                k = (LL, rr)
                if len(pools.get(k, ())) >= min_pool:
                    return k, k != exact_key
        for LL in range(L, 0, -1):
            for rr in range(r + 1, 4):
                k = (LL, rr)
                if len(pools.get(k, ())) >= min_pool:
                    return k, True
        best = max(sorted(pools.keys()), key=lambda x: len(pools[x]))
        return best, True

    if mode == "N3":
        init_flag = bool(rec["is_init"])
        for flg in (init_flag, not init_flag):
            for LL in range(L, 0, -1):
                for rr in range(r, -1, -1):
                    k = (LL, rr, flg)
                    if len(pools.get(k, ())) >= min_pool:
                        return k, k != exact_key
        best = max(sorted(pools.keys()), key=lambda x: len(pools[x]))
        return best, True

    raise ValueError(f"Unknown mode: {mode}")


def run_matched_test(target_records, ref_records, target_fish, mode, ndraw=100000, rng=None, min_pool=5):
    """Run exact Poisson-binomial + Monte Carlo matched null test."""
    n = len(target_records)
    if n == 0:
        return dict(n=0, k=0, rate=None, p_exact=None, p_mc=None)
    k_obs = sum(1 for rec in target_records if rec["follower"] == target_fish)
    rate_obs = k_obs / n

    pools = make_pools(ref_records, target_fish, mode)
    resolved_keys = []
    collapsed = 0
    for rec in target_records:
        k, was_col = resolve_stratum(rec, mode, pools, min_pool=min_pool)
        resolved_keys.append(k)
        collapsed += int(was_col)

    probs = [float(pools[k].mean()) for k in resolved_keys]
    p_exact = poisson_binomial_sf(probs, k_obs)
    null_mean_exact = float(np.mean(probs))
    diff_exact = rate_obs - null_mean_exact

    p_mc = None
    null_mean_mc = None
    if ndraw > 0 and rng is not None:
        key_counts = Counter(resolved_keys)
        totals = np.zeros(ndraw, dtype=np.int32)
        for k in sorted(key_counts.keys()):
            m = key_counts[k]
            arr = pools[k]
            pool_n = len(arr)
            n_ones = int(arr.sum())
            if m == 1:
                idx = rng.integers(pool_n, size=ndraw)
                totals += arr[idx]
            elif pool_n >= m:
                totals += rng.hypergeometric(n_ones, pool_n - n_ones, m, size=ndraw)
            else:
                totals += rng.binomial(m, n_ones / pool_n, size=ndraw)
        p_mc = float((1 + int((totals >= k_obs).sum())) / (ndraw + 1))
        null_mean_mc = float(totals.mean() / n)

    return dict(
        n=n,
        k=k_obs,
        rate=round(rate_obs, 4),
        ci95=clopper_pearson_ci(k_obs, n),
        null_mean=round(null_mean_exact, 4),
        null_mean_mc=round(null_mean_mc, 4) if null_mean_mc is not None else None,
        diff=round(diff_exact, 4),
        p_exact=p_exact,
        p_mc=p_mc,
        ndraw=ndraw,
        collapsed=collapsed,
        mean_L=round(float(np.mean([rec["L_text"] for rec in target_records])), 3),
        mean_r=round(float(np.mean([rec["r_val"] for rec in target_records])), 3),
        mean_r_over_L=round(float(np.mean([rec["r_val"] / rec["L_text"] for rec in target_records])), 4),
    )


def run_within_stratum_permutation(
    texts,
    ref_counts,
    trigger_sign,
    fish_sign,
    rare_thresh=10,
    leave_one_text_out=False,
    ndraw=10000,
    rng=None,
):
    """N4: Permute all sign tokens within each (min(L,9), min(r,3)) stratum across texts."""
    stratum_runs = defaultdict(list)
    obs_k = 0
    obs_n = 0
    for t in texts:
        rlist = runs(t["seq"])
        toks = [s for ru in rlist for s in ru]
        if len(toks) < 2:
            continue
        if leave_one_text_out:
            c_in_t = Counter(toks)
            r_val = sum(1 for s in toks if (ref_counts[s] - c_in_t[s]) < rare_thresh)
        else:
            r_val = sum(1 for s in toks if ref_counts[s] < rare_thresh)
        key = (min(len(toks), 9), min(r_val, 3))
        for ru in rlist:
            if len(ru) >= 2:
                stratum_runs[key].append(ru)
                for a, b in zip(ru, ru[1:]):
                    if a == trigger_sign:
                        obs_n += 1
                        if b == fish_sign:
                            obs_k += 1

    if obs_n == 0:
        return dict(n=0, k=0, rate=None, p_perm_rate=None, p_perm_count=None)

    strata_data = []
    for k in sorted(stratum_runs.keys()):
        rlist = stratum_runs[k]
        codes = []
        run_lens = []
        for ru in rlist:
            run_lens.append(len(ru))
            for s in ru:
                if s == trigger_sign:
                    codes.append(1)
                elif s == fish_sign:
                    codes.append(2)
                else:
                    codes.append(0)
        arr = np.array(codes, dtype=np.int8)
        if not np.any(arr == 1):
            continue
        nonfinal_mask = np.ones(len(arr), dtype=bool)
        pos = 0
        for L in run_lens:
            nonfinal_mask[pos + L - 1] = False
            pos += L
        nonfinal_idx = np.nonzero(nonfinal_mask)[0]
        strata_data.append((arr, nonfinal_idx))

    obs_rate = obs_k / obs_n
    perm_k = np.zeros(ndraw, dtype=np.int32)
    perm_n = np.zeros(ndraw, dtype=np.int32)
    for b in range(ndraw):
        tk = 0
        tn = 0
        for arr, nf_idx in strata_data:
            sh = rng.permutation(arr)
            trig_nf = (sh[nf_idx] == 1)
            tn += int(trig_nf.sum())
            if trig_nf.any():
                tk += int((trig_nf & (sh[nf_idx + 1] == 2)).sum())
        perm_k[b] = tk
        perm_n[b] = tn

    perm_rates = np.where(perm_n > 0, perm_k / np.maximum(perm_n, 1), 0.0)
    p_rate = float((1 + int((perm_rates >= obs_rate - 1e-12).sum())) / (ndraw + 1))
    p_count = float((1 + int((perm_k >= obs_k).sum())) / (ndraw + 1))
    return dict(
        n=obs_n,
        k=obs_k,
        rate=round(obs_rate, 4),
        null_mean_rate=round(float(perm_rates.mean()), 4),
        null_mean_k=round(float(perm_k.mean()), 3),
        diff=round(obs_rate - float(perm_rates.mean()), 4),
        p_perm_rate=p_rate,
        p_perm_count=p_count,
        ndraw=ndraw,
    )


# ---------------------------------------------------------------------------
# Planted controls (C1a, C1b, C2, C3) — strictly zero held-out data used
# ---------------------------------------------------------------------------
def run_planted_controls(dev_texts, dev_counts, seed=20261127, reps=1000):
    rng = np.random.default_rng(seed)
    dev_recs = extract_nonfinal_records(dev_texts, dev_counts, rare_thresh=10, rare_scope="text")
    m109_dev = [r for r in dev_recs if r["trigger"] == "M109"]
    all_non_m109 = [r for r in dev_recs if r["trigger"] != "M109"]
    num_non_m109 = [r for r in dev_recs if r["trigger"] in NUM_M and r["trigger"] != "M109"]

    # Empirical M109 (L, r) stratum profile from dev ONLY
    dev_strata = [(min(r["L_text"], 9), min(r["r_val"], 3)) for r in m109_dev]

    pools_n1 = make_pools(all_non_m109, "M59", "N1")
    pools_n0 = make_pools(all_non_m109, "M59", "N0")
    pools_n2 = make_pools(num_non_m109, "M59", "N2")
    pools_n2_n0 = make_pools(num_non_m109, "M59", "N0")

    # Pre-cache (prob, arr) lookup for every (L, r)
    def build_cache(mode, pools):
        cache = {}
        for L in range(1, 10):
            for r in range(0, 4):
                k, _ = resolve_stratum({"L_text": L, "r_val": r, "is_init": False}, mode, pools, min_pool=5)
                arr = pools[k]
                cache[(L, r)] = (float(arr.mean()), arr)
        return cache

    cache_n1 = build_cache("N1", pools_n1)
    cache_n0 = build_cache("N0", pools_n0)
    cache_n2 = build_cache("N2", pools_n2)
    cache_n2_n0 = build_cache("N0", pools_n2_n0)

    # Pre-index all_non_m109 by text id for fast 571-text subsampling
    recs_by_tid = defaultdict(list)
    for r in all_non_m109:
        recs_by_tid[r["tid"]].append((min(r["L_text"], 9), min(r["r_val"], 3), 1 if r["follower"] == "M59" else 0))

    # --- C1a (real-corpus-embedded planted fixed pair) & C2 (calibration) ---
    c1a = {}
    c2 = {}
    for N in (10, 25):
        c1a[f"N={N}"] = {}
        for p_true in (0.25, 0.35, 0.48, 0.70):
            pw_n1_05 = pw_n1_01 = pw_n2_05 = pw_n2_01 = 0
            for _ in range(reps):
                idxs = rng.integers(len(dev_strata), size=N)
                p1_vec = []
                p2_vec = []
                k_planted = 0
                for idx in idxs:
                    Lr = dev_strata[idx]
                    p1, arr1 = cache_n1[Lr]
                    p2, _ = cache_n2[Lr]
                    p1_vec.append(p1)
                    p2_vec.append(p2)
                    if rng.random() < p_true:
                        k_planted += 1
                    else:
                        k_planted += int(arr1[rng.integers(len(arr1))])
                pv1 = poisson_binomial_sf(p1_vec, k_planted)
                pv2 = poisson_binomial_sf(p2_vec, k_planted)
                pw_n1_05 += int(pv1 < 0.05)
                pw_n1_01 += int(pv1 < 0.01)
                pw_n2_05 += int(pv2 < 0.05)
                pw_n2_01 += int(pv2 < 0.01)
            c1a[f"N={N}"][f"p_true={p_true:.2f}"] = dict(
                power_N1_05=round(pw_n1_05 / reps, 4),
                power_N1_01=round(pw_n1_01 / reps, 4),
                power_N2_05=round(pw_n2_05 / reps, 4),
                power_N2_01=round(pw_n2_01 / reps, 4),
            )

        # C1a at held-out corpus size (571 texts subsampled from dev, N=10, p_true=0.48)
        if N == 10:
            pw_sub_n1_05 = pw_sub_n1_01 = 0
            n_dev_texts = len(dev_texts)
            for _ in range(reps):
                sub_tids = rng.choice(n_dev_texts, size=571, replace=False)
                sub_pools_raw = defaultdict(list)
                for tid in sub_tids:
                    for L, r, f in recs_by_tid.get(int(tid), ()):
                        sub_pools_raw[(L, r)].append(f)
                sub_pools = {k: np.array(v, dtype=np.int8) for k, v in sub_pools_raw.items()}
                idxs = rng.integers(len(dev_strata), size=N)
                p_vec = []
                k_pl = 0
                for idx in idxs:
                    L, r = dev_strata[idx]
                    k_res, _ = resolve_stratum({"L_text": L, "r_val": r, "is_init": False}, "N1", sub_pools, min_pool=5)
                    arr1 = sub_pools[k_res]
                    p_vec.append(float(arr1.mean()))
                    if rng.random() < 0.48:
                        k_pl += 1
                    else:
                        k_pl += int(arr1[rng.integers(len(arr1))])
                pv = poisson_binomial_sf(p_vec, k_pl)
                pw_sub_n1_05 += int(pv < 0.05)
                pw_sub_n1_01 += int(pv < 0.01)
            c1a["N=10_sub571_p0.48"] = dict(
                power_N1_05=round(pw_sub_n1_05 / reps, 4),
                power_N1_01=round(pw_sub_n1_01 / reps, 4),
            )

        # C2 calibration: uncoupled trigger in matched (L, r) strata
        fp_n0 = fp_n1 = fp_n2_from_num = fp_n2_n0_from_num = 0
        for _ in range(reps):
            idxs = rng.integers(len(dev_strata), size=N)
            p0_v, p1_v = [], []
            k_all = 0
            p2_v, p2n0_v = [], []
            k_num = 0
            for idx in idxs:
                Lr = dev_strata[idx]
                p0, _ = cache_n0[Lr]
                p1, arr1 = cache_n1[Lr]
                p0_v.append(p0)
                p1_v.append(p1)
                k_all += int(arr1[rng.integers(len(arr1))])

                p2n0, _ = cache_n2_n0[Lr]
                p2, arr2 = cache_n2[Lr]
                p2n0_v.append(p2n0)
                p2_v.append(p2)
                k_num += int(arr2[rng.integers(len(arr2))])
            fp_n0 += int(poisson_binomial_sf(p0_v, k_all) < 0.05)
            fp_n1 += int(poisson_binomial_sf(p1_v, k_all) < 0.05)
            fp_n2_from_num += int(poisson_binomial_sf(p2_v, k_num) < 0.05)
            fp_n2_n0_from_num += int(poisson_binomial_sf(p2n0_v, k_num) < 0.05)
        c2[f"N={N}"] = dict(
            fp_N0_all=round(fp_n0 / reps, 4),
            fp_N1_all=round(fp_n1 / reps, 4),
            fp_N0_num=round(fp_n2_n0_from_num / reps, 4),
            fp_N2_num=round(fp_n2_from_num / reps, 4),
        )

    # --- C3 (Rare-load confounding control on M77 dev: uncoupled trigger exclusively in r=0 texts) ---
    global_all_p = float(np.mean([1 if r["follower"] == "M59" else 0 for r in all_non_m109]))
    global_num_p = float(np.mean([1 if r["follower"] == "M59" else 0 for r in num_non_m109]))
    r0_all_L = np.array([min(r["L_text"], 9) for r in all_non_m109 if r["r_val"] == 0], dtype=np.int32)
    r0_all_f = np.array([1 if r["follower"] == "M59" else 0 for r in all_non_m109 if r["r_val"] == 0], dtype=np.int8)
    r0_num_L = np.array([min(r["L_text"], 9) for r in num_non_m109 if r["r_val"] == 0], dtype=np.int32)
    r0_num_f = np.array([1 if r["follower"] == "M59" else 0 for r in num_non_m109 if r["r_val"] == 0], dtype=np.int8)

    c3_dev = {}
    for N in (10, 25, 50):
        fp_all_glob = fp_all_n0 = fp_all_n1 = 0
        fp_num_glob = fp_num_n0 = fp_num_n2 = 0
        for _ in range(reps):
            idx_a = rng.integers(len(r0_all_L), size=N)
            k = int(r0_all_f[idx_a].sum())
            p_g = float(binom.sf(k - 1, N, global_all_p)) if k > 0 else 1.0
            Ls = r0_all_L[idx_a]
            p_0 = poisson_binomial_sf([cache_n0[(int(L), 0)][0] for L in Ls], k)
            p_1 = poisson_binomial_sf([cache_n1[(int(L), 0)][0] for L in Ls], k)
            fp_all_glob += int(p_g < 0.05)
            fp_all_n0 += int(p_0 < 0.05)
            fp_all_n1 += int(p_1 < 0.05)

            idx_n = rng.integers(len(r0_num_L), size=N)
            kn = int(r0_num_f[idx_n].sum())
            pn_g = float(binom.sf(kn - 1, N, global_num_p)) if kn > 0 else 1.0
            Lsn = r0_num_L[idx_n]
            pn_0 = poisson_binomial_sf([cache_n2_n0[(int(L), 0)][0] for L in Lsn], kn)
            pn_2 = poisson_binomial_sf([cache_n2[(int(L), 0)][0] for L in Lsn], kn)
            fp_num_glob += int(pn_g < 0.05)
            fp_num_n0 += int(pn_0 < 0.05)
            fp_num_n2 += int(pn_2 < 0.05)
        c3_dev[f"N={N}"] = dict(
            all_r0_fp_global_binom=round(fp_all_glob / reps, 4),
            all_r0_fp_N0_length_only=round(fp_all_n0 / reps, 4),
            all_r0_fp_N1_rare_matched=round(fp_all_n1 / reps, 4),
            num_r0_fp_global_binom=round(fp_num_glob / reps, 4),
            num_r0_fp_N0_length_only=round(fp_num_n0 / reps, 4),
            num_r0_fp_N2_rare_matched=round(fp_num_n2 / reps, 4),
        )

    # --- C1b & C3_synth (Pure synthetic corpus of 2,300 distinct texts, mean ~4.5 signs) ---
    dev_lens = np.array([sum(len(ru) for ru in runs(t["seq"])) for t in dev_texts])
    dev_lens = dev_lens[dev_lens >= 1]
    n_synth = 2300
    ranks_c = np.arange(1, 151, dtype=np.float64)
    w_common = 1.0 / (ranks_c ** 1.05)
    w_common[0] = 0.0
    w_common = w_common / w_common.sum()
    w_common_r0 = np.copy(w_common) * (1.0 - 0.08)
    w_common_r0[0] = 0.08
    w_common_rhi = np.copy(w_common) * (1.0 - 0.015)
    w_common_rhi[0] = 0.015
    ranks_r = np.arange(1, 268, dtype=np.float64)
    w_rare = 1.0 / (ranks_r ** 0.7)
    w_rare /= w_rare.sum()

    cdf_r0 = np.cumsum(w_common_r0)
    cdf_rhi = np.cumsum(w_common_rhi)
    cdf_rare = np.cumsum(w_rare)

    synth_texts = []
    lens_syn = dev_lens[rng.integers(len(dev_lens), size=n_synth)]
    regimes = rng.random(n_synth) < 0.55
    for tid in range(n_synth):
        L = int(lens_syn[tid])
        u = rng.random(L)
        if regimes[tid]:
            s_idxs = np.searchsorted(cdf_r0, u)
            seq = [f"S{int(x)}" for x in s_idxs]
        else:
            is_r = rng.random(L) < 0.30
            s_r = 150 + np.searchsorted(cdf_rare, u)
            s_c = np.searchsorted(cdf_rhi, u)
            seq = [f"S{int(sr if fl else sc)}" for fl, sr, sc in zip(is_r, s_r, s_c)]
        synth_texts.append({"id": f"syn_{tid}", "seq": seq, "site": "SYN", "object_type": "seal"})

    synth_counts = build_sign_counts(synth_texts)
    synth_recs = extract_nonfinal_records(synth_texts, synth_counts, rare_thresh=10, rare_scope="text")
    syn_pools_n1 = make_pools(synth_recs, "S0", "N1")
    syn_pools_n0 = make_pools(synth_recs, "S0", "N0")
    syn_cache_n1 = build_cache("N1", syn_pools_n1)
    syn_cache_n0 = build_cache("N0", syn_pools_n0)
    syn_global_p = float(np.mean([1 if r["follower"] == "S0" else 0 for r in synth_recs]))
    syn_r0_L = np.array([min(r["L_text"], 9) for r in synth_recs if r["r_val"] == 0], dtype=np.int32)
    syn_r0_f = np.array([1 if r["follower"] == "S0" else 0 for r in synth_recs if r["r_val"] == 0], dtype=np.int8)
    syn_mean_len = round(float(np.mean([len(t["seq"]) for t in synth_texts])), 3)

    c1b = {"n_texts": n_synth, "mean_len": syn_mean_len, "global_B_rate": round(syn_global_p, 4)}
    for N in (10, 25):
        c1b[f"N={N}"] = {}
        for p_true in (0.0, 0.25, 0.35, 0.48, 0.70):
            pw05 = pw01 = 0
            for _ in range(reps):
                idxs = rng.integers(len(dev_strata), size=N)
                p_vec = []
                k_pl = 0
                for idx in idxs:
                    Lr = dev_strata[idx]
                    p1, arr1 = syn_cache_n1[Lr]
                    p_vec.append(p1)
                    if p_true > 0 and rng.random() < p_true:
                        k_pl += 1
                    else:
                        k_pl += int(arr1[rng.integers(len(arr1))])
                pv = poisson_binomial_sf(p_vec, k_pl)
                pw05 += int(pv < 0.05)
                pw01 += int(pv < 0.01)
            label = "fp_p_true=0.00" if p_true == 0.0 else f"p_true={p_true:.2f}"
            c1b[f"N={N}"][label] = dict(rate_05=round(pw05 / reps, 4), rate_01=round(pw01 / reps, 4))

    c3_synth = {}
    for N in (10, 25, 50):
        fg = f0 = f1 = 0
        for _ in range(reps):
            idx_s = rng.integers(len(syn_r0_L), size=N)
            k = int(syn_r0_f[idx_s].sum())
            pg = float(binom.sf(k - 1, N, syn_global_p)) if k > 0 else 1.0
            Ls = syn_r0_L[idx_s]
            p0 = poisson_binomial_sf([syn_cache_n0[(int(L), 0)][0] for L in Ls], k)
            p1 = poisson_binomial_sf([syn_cache_n1[(int(L), 0)][0] for L in Ls], k)
            fg += int(pg < 0.05)
            f0 += int(p0 < 0.05)
            f1 += int(p1 < 0.05)
        c3_synth[f"N={N}"] = dict(
            r0_fp_global_binom=round(fg / reps, 4),
            r0_fp_N0_length_only=round(f0 / reps, 4),
            r0_fp_N1_rare_matched=round(f1 / reps, 4),
        )

    return dict(
        reps=reps,
        C1a_real_embedded=c1a,
        C1b_synthetic_2300=c1b,
        C2_calibration_dev=c2,
        C3_rare_confound_dev=c3_dev,
        C3_rare_confound_synth2300=c3_synth,
    )


# ---------------------------------------------------------------------------
# Main analysis pipeline
# ---------------------------------------------------------------------------
def describe_rare_gradient(recs, num_set, trigger, fish):
    out = {}
    all_other = [r for r in recs if r["trigger"] != trigger]
    num_other = [r for r in recs if r["trigger"] in num_set and r["trigger"] != trigger]
    for rv in range(4):
        sa = [r for r in all_other if min(r["r_val"], 3) == rv]
        sn = [r for r in num_other if min(r["r_val"], 3) == rv]
        out[f"r={rv}"] = dict(
            all_n=len(sa),
            all_p_fish=round(sum(r["follower"] == fish for r in sa) / max(1, len(sa)), 4),
            num_n=len(sn),
            num_p_fish=round(sum(r["follower"] == fish for r in sn) / max(1, len(sn)), 4),
        )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-check", action="store_true",
                        help="Run only on M77 dev + planted controls (no held-out or ICIT).")
    args = parser.parse_args()

    t0 = time.time()
    dev, ho = dev_heldout(version=2)
    dev_counts = build_sign_counts(dev)

    print(f"[{time.time() - t0:5.1f}s] Running planted controls (1,000 reps each)...", flush=True)
    planted = run_planted_controls(dev, dev_counts, seed=20261127, reps=1000)

    dev_recs = extract_nonfinal_records(dev, dev_counts, rare_thresh=10, rare_scope="text")
    dev_m109 = [r for r in dev_recs if r["trigger"] == "M109"]
    dev_all_other = [r for r in dev_recs if r["trigger"] != "M109"]
    dev_num_other = [r for r in dev_recs if r["trigger"] in NUM_M and r["trigger"] != "M109"]

    rng_dev = np.random.default_rng(100)
    dev_summary = dict(
        n_texts=len(dev),
        rare_gradient=describe_rare_gradient(dev_recs, NUM_M, "M109", "M59"),
        N0_all=run_matched_test(dev_m109, dev_all_other, "M59", "N0", ndraw=100000, rng=rng_dev),
        N1_all=run_matched_test(dev_m109, dev_all_other, "M59", "N1", ndraw=100000, rng=rng_dev),
        N2_num=run_matched_test(dev_m109, dev_num_other, "M59", "N2", ndraw=100000, rng=rng_dev),
    )

    if args.dev_check:
        out = dict(mode="dev_check", dev_summary=dev_summary, planted=planted)
        print(json.dumps(out, indent=2))
        print(f"[{time.time() - t0:5.1f}s] dev-check completed cleanly (held-out and ICIT untouched).", flush=True)
        return

    # ------------------------------------------------------------------
    # Full confirmatory run (M77 held-out v2 + native ICIT)
    # ------------------------------------------------------------------
    print(f"[{time.time() - t0:5.1f}s] Extracting held-out M77 and native ICIT records...", flush=True)
    ho_recs = extract_nonfinal_records(ho, dev_counts, rare_thresh=10, rare_scope="text")
    ho_m109 = [r for r in ho_recs if r["trigger"] == "M109"]
    ho_all_other = [r for r in ho_recs if r["trigger"] != "M109"]
    ho_num_other = [r for r in ho_recs if r["trigger"] in NUM_M and r["trigger"] != "M109"]

    all_m77 = dev + ho
    all_m77_recs = dev_recs + ho_recs
    all_m109 = [r for r in all_m77_recs if r["trigger"] == "M109"]
    all_m77_other = [r for r in all_m77_recs if r["trigger"] != "M109"]
    all_m77_num = [r for r in all_m77_recs if r["trigger"] in NUM_M and r["trigger"] != "M109"]

    icit_dist = distinct_by_seq(icit_texts())
    icit_counts = build_sign_counts(icit_dist)
    icit_recs = extract_nonfinal_records(
        icit_dist, icit_counts, rare_thresh=10, leave_one_text_out=True, rare_scope="text", type_key="type"
    )
    icit_w016 = [r for r in icit_recs if r["trigger"] == "W016"]
    icit_all_other = [r for r in icit_recs if r["trigger"] != "W016"]
    icit_num_other = [r for r in icit_recs if r["trigger"] in NUM_W and r["trigger"] != "W016"]

    print(f"[{time.time() - t0:5.1f}s] Running primary tests T1-T4...", flush=True)
    rng_p = np.random.default_rng(2026)
    primary = {
        "T1_m77_ho_N1_all": run_matched_test(ho_m109, ho_all_other, "M59", "N1", ndraw=100000, rng=rng_p),
        "T2_m77_ho_N2_num_devref": run_matched_test(ho_m109, dev_num_other, "M59", "N2", ndraw=100000, rng=rng_p),
        "T3_icit_N1_all": run_matched_test(icit_w016, icit_all_other, "W220", "N1", ndraw=100000, rng=rng_p),
        "T4_icit_N2_num": run_matched_test(icit_w016, icit_num_other, "W220", "N2", ndraw=100000, rng=rng_p),
    }
    holm_p = holm_adjust({k: v["p_exact"] for k, v in primary.items()})
    for k in sorted(primary.keys()):
        primary[k]["p_holm"] = holm_p[k]

    print(f"[{time.time() - t0:5.1f}s] Running secondary nulls (N0, N1_devref, N2_horef, N3, N4)...", flush=True)
    rng_s = np.random.default_rng(3030)
    secondary = {
        "N0_m77_ho_all": run_matched_test(ho_m109, ho_all_other, "M59", "N0", ndraw=100000, rng=rng_s),
        "N0_m77_ho_num_devref": run_matched_test(ho_m109, dev_num_other, "M59", "N0", ndraw=100000, rng=rng_s),
        "N0_icit_all": run_matched_test(icit_w016, icit_all_other, "W220", "N0", ndraw=100000, rng=rng_s),
        "N0_icit_num": run_matched_test(icit_w016, icit_num_other, "W220", "N0", ndraw=100000, rng=rng_s),
        "N1_m77_ho_devref": run_matched_test(ho_m109, dev_all_other, "M59", "N1", ndraw=100000, rng=rng_s),
        "N2_m77_ho_horef": run_matched_test(ho_m109, ho_num_other, "M59", "N2", ndraw=100000, rng=rng_s),
        "N3_m77_ho_all": run_matched_test(ho_m109, ho_all_other, "M59", "N3", ndraw=100000, rng=rng_s),
        "N3_m77_ho_num_devref": run_matched_test(ho_m109, dev_num_other, "M59", "N3", ndraw=100000, rng=rng_s),
        "N3_icit_all": run_matched_test(icit_w016, icit_all_other, "W220", "N3", ndraw=100000, rng=rng_s),
        "N3_icit_num": run_matched_test(icit_w016, icit_num_other, "W220", "N3", ndraw=100000, rng=rng_s),
        "m77_all_N0_all": run_matched_test(all_m109, all_m77_other, "M59", "N0", ndraw=100000, rng=rng_s),
        "m77_all_N1_all": run_matched_test(all_m109, all_m77_other, "M59", "N1", ndraw=100000, rng=rng_s),
        "m77_all_N2_num": run_matched_test(all_m109, all_m77_num, "M59", "N2", ndraw=100000, rng=rng_s),
        "N4_perm_m77_ho": run_within_stratum_permutation(ho, dev_counts, "M109", "M59", ndraw=10000, rng=rng_s),
        "N4_perm_m77_all": run_within_stratum_permutation(all_m77, dev_counts, "M109", "M59", ndraw=10000, rng=rng_s),
        "N4_perm_icit": run_within_stratum_permutation(
            icit_dist, icit_counts, "W016", "W220", leave_one_text_out=True, ndraw=10000, rng=rng_s
        ),
    }

    diff_retention = {
        "T1_over_N0": round(primary["T1_m77_ho_N1_all"]["diff"] / secondary["N0_m77_ho_all"]["diff"], 4),
        "T2_over_N0": round(primary["T2_m77_ho_N2_num_devref"]["diff"] / secondary["N0_m77_ho_num_devref"]["diff"], 4),
        "T3_over_N0": round(primary["T3_icit_N1_all"]["diff"] / secondary["N0_icit_all"]["diff"], 4),
        "T4_over_N0": round(primary["T4_icit_N2_num"]["diff"] / secondary["N0_icit_num"]["diff"], 4),
    }

    print(f"[{time.time() - t0:5.1f}s] Running sensitivity checks...", flush=True)
    rng_sens = np.random.default_rng(4040)
    rare_sens = {}
    for label, thresh, scope in (
        ("thresh_lt5", 5, "text"),
        ("thresh_lt20", 20, "text"),
        ("scope_run", 10, "run"),
        ("scope_excl_trigger", 10, "excl_trigger"),
    ):
        d_r = extract_nonfinal_records(dev, dev_counts, rare_thresh=thresh, rare_scope=scope)
        h_r = extract_nonfinal_records(ho, dev_counts, rare_thresh=thresh, rare_scope=scope)
        i_r = extract_nonfinal_records(
            icit_dist, icit_counts, rare_thresh=thresh, leave_one_text_out=True, rare_scope=scope, type_key="type"
        )
        rare_sens[label] = {
            "T1_m77_ho_N1": run_matched_test(
                [r for r in h_r if r["trigger"] == "M109"],
                [r for r in h_r if r["trigger"] != "M109"],
                "M59", "N1", ndraw=20000, rng=rng_sens,
            ),
            "T2_m77_ho_N2": run_matched_test(
                [r for r in h_r if r["trigger"] == "M109"],
                [r for r in d_r if r["trigger"] in NUM_M and r["trigger"] != "M109"],
                "M59", "N2", ndraw=20000, rng=rng_sens,
            ),
            "T3_icit_N1": run_matched_test(
                [r for r in i_r if r["trigger"] == "W016"],
                [r for r in i_r if r["trigger"] != "W016"],
                "W220", "N1", ndraw=20000, rng=rng_sens,
            ),
            "T4_icit_N2": run_matched_test(
                [r for r in i_r if r["trigger"] == "W016"],
                [r for r in i_r if r["trigger"] in NUM_W and r["trigger"] != "W016"],
                "W220", "N2", ndraw=20000, rng=rng_sens,
            ),
        }

    seals_only = {
        "m77_ho_seals_N1": run_matched_test(
            [r for r in ho_m109 if r["otype"] == "seal"],
            [r for r in ho_all_other if r["otype"] == "seal"],
            "M59", "N1", ndraw=50000, rng=rng_sens,
        ),
        "m77_ho_seals_N2_devref": run_matched_test(
            [r for r in ho_m109 if r["otype"] == "seal"],
            [r for r in dev_num_other if r["otype"] == "seal"],
            "M59", "N2", ndraw=50000, rng=rng_sens,
        ),
        "m77_all_seals_N1": run_matched_test(
            [r for r in all_m109 if r["otype"] == "seal"],
            [r for r in all_m77_other if r["otype"] == "seal"],
            "M59", "N1", ndraw=50000, rng=rng_sens,
        ),
        "m77_all_seals_N2": run_matched_test(
            [r for r in all_m109 if r["otype"] == "seal"],
            [r for r in all_m77_num if r["otype"] == "seal"],
            "M59", "N2", ndraw=50000, rng=rng_sens,
        ),
        "icit_seals_N1": run_matched_test(
            [r for r in icit_w016 if r["otype"].startswith("SEAL")],
            [r for r in icit_all_other if r["otype"].startswith("SEAL")],
            "W220", "N1", ndraw=50000, rng=rng_sens,
        ),
        "icit_seals_N2": run_matched_test(
            [r for r in icit_w016 if r["otype"].startswith("SEAL")],
            [r for r in icit_num_other if r["otype"].startswith("SEAL")],
            "W220", "N2", ndraw=50000, rng=rng_sens,
        ),
    }

    m77_fam = dedup_edit1_families(all_m77)
    m77_fam_counts = build_sign_counts(m77_fam)
    m77_fam_recs = extract_nonfinal_records(
        m77_fam, m77_fam_counts, rare_thresh=10, leave_one_text_out=True, rare_scope="text"
    )
    icit_fam = dedup_edit1_families(icit_dist)
    icit_fam_counts = build_sign_counts(icit_fam)
    icit_fam_recs = extract_nonfinal_records(
        icit_fam, icit_fam_counts, rare_thresh=10, leave_one_text_out=True, rare_scope="text", type_key="type"
    )
    family_dedup = {
        "m77_n_families": len(m77_fam),
        "m77_fam_N1": run_matched_test(
            [r for r in m77_fam_recs if r["trigger"] == "M109"],
            [r for r in m77_fam_recs if r["trigger"] != "M109"],
            "M59", "N1", ndraw=50000, rng=rng_sens,
        ),
        "m77_fam_N2": run_matched_test(
            [r for r in m77_fam_recs if r["trigger"] == "M109"],
            [r for r in m77_fam_recs if r["trigger"] in NUM_M and r["trigger"] != "M109"],
            "M59", "N2", ndraw=50000, rng=rng_sens,
        ),
        "icit_n_families": len(icit_fam),
        "icit_fam_N1": run_matched_test(
            [r for r in icit_fam_recs if r["trigger"] == "W016"],
            [r for r in icit_fam_recs if r["trigger"] != "W016"],
            "W220", "N1", ndraw=50000, rng=rng_sens,
        ),
        "icit_fam_N2": run_matched_test(
            [r for r in icit_fam_recs if r["trigger"] == "W016"],
            [r for r in icit_fam_recs if r["trigger"] in NUM_W and r["trigger"] != "W016"],
            "W220", "N2", ndraw=50000, rng=rng_sens,
        ),
    }

    loso_m77 = {}
    for site in sorted({r["site"] for r in all_m109}):
        loso_m77[f"drop_{site}"] = run_matched_test(
            [r for r in all_m109 if r["site"] != site],
            [r for r in all_m77_other if r["site"] != site],
            "M59", "N1", ndraw=20000, rng=rng_sens,
        )
    loso_icit = {}
    for site in sorted({r["site"] for r in icit_w016}):
        loso_icit[f"drop_{site}"] = run_matched_test(
            [r for r in icit_w016 if r["site"] != site],
            [r for r in icit_all_other if r["site"] != site],
            "W220", "N1", ndraw=20000, rng=rng_sens,
        )
    post1977_icit = run_matched_test(
        [r for r in icit_w016 if r["site"] not in M77_SITES],
        [r for r in icit_all_other if r["site"] not in M77_SITES],
        "W220", "N1", ndraw=20000, rng=rng_sens,
    )

    def group_profile(recs):
        if not recs:
            return dict(n=0)
        return dict(
            n=len(recs),
            mean_L=round(float(np.mean([r["L_text"] for r in recs])), 3),
            mean_r=round(float(np.mean([r["r_val"] for r in recs])), 3),
            mean_r_over_L=round(float(np.mean([r["r_val"] / r["L_text"] for r in recs])), 4),
            r_hist={str(k): int(v) for k, v in sorted(Counter(min(r["r_val"], 3) for r in recs).items())},
        )

    rare_profiles = {
        "m77_ho_M109": group_profile(ho_m109),
        "m77_ho_all_other": group_profile(ho_all_other),
        "m77_dev_other_NUM": group_profile(dev_num_other),
        "icit_W016": group_profile(icit_w016),
        "icit_all_other": group_profile(icit_all_other),
        "icit_other_NUM": group_profile(icit_num_other),
        "icit_rare_gradient": describe_rare_gradient(icit_recs, NUM_W, "W016", "W220"),
    }

    c1a_10_48 = planted["C1a_real_embedded"]["N=10"]["p_true=0.48"]
    c2_10 = planted["C2_calibration_dev"]["N=10"]
    power_ok = c1a_10_48["power_N1_05"] >= 0.80 and c1a_10_48["power_N2_05"] >= 0.80
    power_low = c1a_10_48["power_N1_05"] < 0.50 or c1a_10_48["power_N2_05"] < 0.50
    cal_ok = c2_10["fp_N1_all"] <= 0.10 and c2_10["fp_N2_num"] <= 0.10

    all_prim_01 = all(primary[k]["p_holm"] < 0.01 for k in primary)
    any_prim_fail = any(primary[k]["p_exact"] >= 0.05 for k in primary)
    ret_ok = all(v >= 0.5 for v in diff_retention.values())
    seals_ok = (
        seals_only["m77_all_seals_N1"]["p_exact"] < 0.01
        and seals_only["m77_all_seals_N2"]["p_exact"] < 0.01
        and seals_only["icit_seals_N1"]["p_exact"] < 0.01
        and seals_only["icit_seals_N2"]["p_exact"] < 0.01
    )
    rare_sens_ok = all(
        rare_sens[lab][t]["p_exact"] < 0.01
        for lab in rare_sens
        for t in rare_sens[lab]
    )

    if power_low or not cal_ok:
        verdict = "INCONCLUSIVE"
    elif any_prim_fail and power_ok:
        verdict = "FALLS"
    elif all_prim_01 and power_ok and cal_ok and ret_ok and seals_ok and rare_sens_ok:
        verdict = "SURVIVES"
    else:
        verdict = "WEAKENS"

    result = {
        "task": "S4",
        "prereg": "docs/prereg/2026-11-27_s4_six_fish_rare_null.md",
        "verdict_by_prereg_rule": verdict,
        "decision_checks": {
            "all_primary_holm_lt_0.01": all_prim_01,
            "any_primary_unadj_ge_0.05": any_prim_fail,
            "C1a_N10_p048_power_ge_0.80": power_ok,
            "C2_N10_fp_le_0.10": cal_ok,
            "excess_retains_half_of_N0": ret_ok,
            "seals_only_lt_0.01": seals_ok,
            "all_rare_sens_lt_0.01": rare_sens_ok,
        },
        "corpus_counts": {
            "m77_dev_distinct": len(dev),
            "m77_ho_distinct": len(ho),
            "icit_distinct": len(icit_dist),
        },
        "primary_holm4": primary,
        "diff_retention_vs_N0": diff_retention,
        "secondary": secondary,
        "dev_summary": dev_summary,
        "rare_profiles": rare_profiles,
        "sensitivity": {
            "rare_definitions": rare_sens,
            "seals_only": seals_only,
            "family_dedup_ed1": family_dedup,
            "leave_one_site_out_m77": loso_m77,
            "leave_one_site_out_icit": loso_icit,
            "post1977_icit_sites": post1977_icit,
        },
        "planted_controls": planted,
    }

    out_path = OUT / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"[{time.time() - t0:5.1f}s] Done. Verdict: {verdict}", flush=True)
    print(json.dumps({
        "verdict": verdict,
        "decision_checks": result["decision_checks"],
        "primary_holm4": primary,
        "diff_retention_vs_N0": diff_retention,
    }, indent=2))


if __name__ == "__main__":
    main()
