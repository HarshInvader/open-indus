"""Uniformity benchmark (prereg docs/prereg/uniformity_benchmark.md).

The frozen site_signal pipeline (experiments/site_signal/lib.py: design(slot="all", A0={}, min_df=2),
oof_scores(model="nb", k=5, reps=3), auc) is imported and called unchanged, the way s1_confirm.binary_test
calls it. Only the input texts differ.

  board/run.sh .venv/bin/python -I experiments/uniformity_benchmark/run.py sizes   # counts only
  board/run.sh .venv/bin/python -I experiments/uniformity_benchmark/run.py calib   # planted-stock curve (Indus, labels permuted)
  board/run.sh .venv/bin/python -I experiments/uniformity_benchmark/run.py run     # reference AUCs (resumable)
  .venv/bin/python -I experiments/uniformity_benchmark/run.py report
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/site_signal"))
sys.path.insert(0, str(ROOT / "experiments/fish_tick_closer_v2"))
import lib  # noqa: E402  frozen site_signal pipeline
import dedup  # noqa: E402  non-chaining greedy de-duplication

DATA = HERE / "data"
N_DRAWS = 200
N_TOTAL = 621
FRAME_SHARE = 0.383
SEED = 20261121
MD, HA = "Mohenjo-daro", "Harappa"
BINS = list(range(1, 10))  # length bins 1..8 and 9+ (9)

# --------------------------------------------------------------------------- pairs (frozen in prereg)
PAIRS = {
    # name: (pool, site A (y=1), site B, filter, name_bearing, primary)
    "ur3_umma_girsu": ("ur3", "Umma", "Girsu", None, True, True),
    "ur3_pd_nippur": ("ur3", "Puzriš-Dagan", "Nippur", None, True, True),
    "lat_britannia_germania": ("lat", "Britannia", "Germania", "label", True, True),
    "pc_uruk4_uruk3": ("pc", "Uruk IV", "Uruk III", "uruk", False, True),
}
DOBRUJA = {"Constanța", "Constanţa", "Constanța?", "Constanţa?", "Tulcea", "Tulcea?"}


def bin_of(n):
    return min(n, 9)


def indus_mix():
    """Length mix of the site_signal P1 sample (strict ICIT seals, MD + Harappa)."""
    E = lib.eligible_icit("strict")
    MH = [t for t in E if t["site"] in (MD, HA)]
    c = Counter(bin_of(len(t["signs"])) for t in MH)
    tot = sum(c.values())
    return {b: c[b] / tot for b in BINS}, MH


def load_pool(pair):
    pool, a, b, filt, _, _ = PAIRS[pair]
    R = [json.loads(l) for l in open(DATA / f"{pool}.jsonl")]
    out = []
    for r in R:
        s = r["site"]
        if pool == "lat":
            if r["genre"] != filt:
                continue
            if s == "United Kingdom":
                s = "Britannia"
            elif s == "Romania":
                if r.get("region") in DOBRUJA:
                    continue
                s = "Dacia"
            elif s == "Germany":
                s = "Germania"
            else:
                continue
        if pool == "pc" and not r.get("prov", "").startswith("Uruk"):
            continue
        if s not in (a, b):
            continue
        out.append(dict(id=r["id"], site=s, lines=r["lines"], group=r["group"]))
    return out


def to_seq(lines):
    seq = []
    for i, l in enumerate(lines):
        if i:
            seq.append("|")
        seq += l
    return seq


def clean(texts):
    """Drop strings found at both sites (label ambiguous), then non-chaining greedy dedup on the pooled
    pair. For pc (one text = one line of a tablet) dedup keeps the first exact copy; the line-per-tablet
    rule is applied at sampling time."""
    sites_of = {}
    for t in texts:
        sites_of.setdefault(" ".join(w for l in t["lines"] for w in l), set()).add(t["site"])
    T = [dict(t, seq=to_seq(t["lines"])) for t in texts
         if len(sites_of[" ".join(w for l in t["lines"] for w in l)]) == 1]
    T.sort(key=lambda t: t["id"])
    kept = dedup.greedy(T)
    return kept


def strip_frame(texts):
    wc = Counter(w for t in texts for l in t["lines"] for w in l)
    tot = sum(wc.values()); cum = 0; frame = set()
    for w, c in wc.most_common():
        if cum / tot >= FRAME_SHARE:
            break
        frame.add(w); cum += c
    out = []
    for t in texts:
        L = [[w for w in l if w not in frame] for l in t["lines"]]
        L = [l for l in L if l]
        if L:
            out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["group"]))
    return out, dict(n_words=len(frame), share=cum / tot, top=[w for w, _ in wc.most_common(len(frame))][:20])


def pools(pair):
    T = load_pool(pair)
    whole = clean(T)
    stripped, finfo = strip_frame(whole)
    stripped = clean(stripped)
    return {"whole": whole, "frame_removed": stripped}, finfo


def targets(mix, n):
    raw = {b: mix[b] * n for b in BINS}
    t = {b: int(np.floor(v)) for b, v in raw.items()}
    rem = n - sum(t.values())
    for b in sorted(BINS, key=lambda b: -(raw[b] - t[b]))[:rem]:
        t[b] += 1
    return t


def draw_site(texts, tgt, rng, one_per_group):
    """Length-matched sample without replacement; a short bin is filled from the nearest bins
    (ties go to the longer bin). With one_per_group, no two texts share a group (tablet)."""
    byb = {b: [] for b in BINS}
    for i in rng.permutation(len(texts)):
        t = texts[i]
        byb[bin_of(sum(len(l) for l in t["lines"]))].append(t)
    used_g, chosen = set(), []
    ptr = {b: 0 for b in BINS}

    def take(b):
        L = byb[b]
        while ptr[b] < len(L):
            t = L[ptr[b]]; ptr[b] += 1
            if one_per_group and t["group"] in used_g:
                continue
            used_g.add(t["group"]); return t
        return None
    short = 0
    for b in BINS:
        for _ in range(tgt[b]):
            t = take(b)
            if t is None:
                for d in range(1, 9):
                    for bb in (b + d, b - d):
                        if bb in byb:
                            t = take(bb)
                            if t is not None:
                                break
                    if t is not None:
                        break
                short += 1
            if t is None:
                return None, short
            chosen.append(t)
    return chosen, short


def score(sample, a, seed):
    """Exactly s1_confirm.binary_test without the permutation loop, plus one permuted-label AUC."""
    T = [dict(signs=[w for l in t["lines"] for w in l], runs=t["lines"], fam=t["group"], site=t["site"]) for t in sample]
    X, vocab = lib.design(T, {}, "all")
    y = np.array([1 if t["site"] == a else 0 for t in T])
    g = np.array([t["fam"] for t in T])
    keep = np.asarray(X.sum(1)).ravel() > 0
    X, y, g = X[keep], y[keep], g[keep]
    P = lib.oof_scores(X, y, g, model="nb", classes=[0, 1], seed=seed)
    obs = lib.auc(y, P[:, 1])
    rng = np.random.default_rng(seed + 7)
    yp = lib.permute_within(y, np.zeros(len(y), int), rng)
    Pp = lib.oof_scores(X, yp, g, model="nb", classes=[0, 1], seed=seed + 1, reps=1)
    return float(obs), float(lib.auc(yp, Pp[:, 1])), int(X.shape[1]), int(len(y))


# --------------------------------------------------------------------------- modes
def sizes():
    mix, MH = indus_mix()
    print("Indus P1 sample", len(MH), "length mix", {b: round(v, 3) for b, v in mix.items()})
    for pair in PAIRS:
        P, finfo = pools(pair)
        a, b = PAIRS[pair][1], PAIRS[pair][2]
        for v, T in P.items():
            c = Counter(t["site"] for t in T)
            lm = {s: sorted(Counter(bin_of(sum(len(l) for l in t["lines"])) for t in T if t["site"] == s).items()) for s in (a, b)}
            ng = {s: len(set(t["group"] for t in T if t["site"] == s)) for s in (a, b)}
            print(pair, v, dict(c), "groups", ng, "len mix", lm)
        print("   frame", finfo["n_words"], round(finfo["share"], 3), finfo["top"][:10])


def calib(reps=50):
    """Planted local stock on the Indus P1 sample with permuted site labels (s2_explore recipe):
    mean AUC as a function of the share q of Harappa tokens replaced by a 20-sign stock."""
    _, MH = indus_mix()
    freq = Counter(s for t in MH for s in t["signs"])
    common = sorted(s for s, c in freq.items() if c >= 5)
    out = {}
    for q in (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8):
        rng = np.random.default_rng(SEED + int(q * 1000)); aucs = []
        for rep in range(reps):
            sites = np.array([t["site"] for t in MH])[rng.permutation(len(MH))]
            stock = list(rng.choice(common, 20, replace=False))
            T = []
            for t, s in zip(MH, sites):
                t2 = dict(t); t2["site"] = s
                if s == HA:
                    sg = [stock[rng.integers(20)] if rng.random() < q else x for x in t["signs"]]
                    runs, k = [], 0
                    for r in t["runs"]:
                        runs.append(sg[k:k + len(r)]); k += len(r)
                    t2["signs"], t2["runs"] = sg, runs
                T.append(t2)
            X, _ = lib.design(T, {}, "all")
            y = np.array([1 if t["site"] == MD else 0 for t in T])
            P = lib.oof_scores(X, y, np.arange(len(y)), classes=[0, 1], reps=1, seed=rep)
            aucs.append(lib.auc(y, P[:, 1]))
        out[str(q)] = dict(mean_auc=float(np.mean(aucs)), sd=float(np.std(aucs)))
        print("calib q", q, out[str(q)], flush=True)
    lib.jdump(out, HERE / "calib.json")


def run():
    mix, _ = indus_mix()
    path = HERE / "draws.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            r = json.loads(l); done.add((r["pair"], r["variant"], r["design"], r["draw"]))
    jobs = []
    for pair, (pool, a, b, _, _, primary) in PAIRS.items():
        variants = ["whole", "frame_removed"]
        designs = ["balanced"] + (["indus_ratio"] if primary else [])
        jobs.append((pair, variants, designs))
    with open(path, "a") as f:
        for pair, variants, designs in jobs:
            pool, a, b = PAIRS[pair][:3]
            P, finfo = pools(pair)
            for v in variants:
                for d in designs:
                    if d == "indus_ratio" and v != "whole":
                        continue
                    n_a = None if d == "balanced" else 483  # Indus P1: 483 MD : 128 Harappa (n = 611)
                    ntot = N_TOTAL if d == "balanced" else 611
                    for k in range(N_DRAWS):
                        if (pair, v, d, k) in done:
                            continue
                        rng = np.random.default_rng([SEED, k, sum(map(ord, pair)), len(v), len(d)])
                        smp, short = draw_n(P[v], a, b, rng, mix, pool == "pc", n_a, ntot)
                        if smp is None:
                            rec = dict(pair=pair, variant=v, design=d, draw=k, auc=None, null_auc=None, short=short)
                        else:
                            obs, nul, nf, n = score(smp, a, SEED + k)
                            rec = dict(pair=pair, variant=v, design=d, draw=k, auc=obs, null_auc=nul, n_feat=nf, n=n, short=short)
                        f.write(json.dumps(rec) + "\n"); f.flush()
                        if k % 50 == 0:
                            print(pair, v, d, k, rec.get("auc"), flush=True)


def draw_n(texts, a, b, rng, mix, one_per_group, n_a, ntot):
    n_a = n_a if n_a is not None else ntot // 2 + 1
    n_b = ntot - n_a
    A = [t for t in texts if t["site"] == a]
    B = [t for t in texts if t["site"] == b]
    ca, sa = draw_site(A, targets(mix, n_a), rng, one_per_group)
    cb, sb = draw_site(B, targets(mix, n_b), rng, one_per_group)
    if ca is None or cb is None:
        return None, sa + sb
    return ca + cb, sa + sb


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    {"sizes": sizes, "calib": calib, "run": run}[mode]()
