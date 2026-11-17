"""Q2b. Probable allographs: signs that look alike (Mahadevan drawings) AND whose contexts cannot be told apart.

Developed on DEV only. Validation: held-out bigram log-likelihood after merging, against (a) random frequency-matched
merges and (b) look-alike pairs with different contexts. Builds on shaunmortal M3/M4 (cited in RESULTS.md); this is
an independent re-implementation on our split with a permutation test for context difference.
"""
import itertools
import json
import math
import random
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageFilter

from common import Bigram, ROOT, m77_split, runs, save_json, signs

rng = random.Random(20261114)
dev, ho = m77_split()
dev_runs = [r for t in dev for r in runs(t["seq"])]
ho_runs = [r for t in ho for r in runs(t["seq"])]
tok = Counter(s for r in dev_runs for s in r)
MIN = 8
cand = sorted([s for s, c in tok.items() if c >= MIN], key=lambda s: -tok[s])

# ---- contexts: list of (left, right) per occurrence ----
occ = defaultdict(list)
for r in dev_runs:
    rr = ["<s>"] + r + ["</s>"]
    for i in range(1, len(rr) - 1):
        occ[rr[i]].append((rr[i - 1], rr[i + 1]))


def ctx_vec(occs, keys_l, keys_r):
    l = Counter(a for a, _ in occs); r = Counter(b for _, b in occs)
    vl = np.array([l[k] for k in keys_l], float); vr = np.array([r[k] for k in keys_r], float)
    return vl, vr


def jsd(p, q):
    p = p / p.sum(); q = q / q.sum(); m = (p + q) / 2
    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def divergence(oa, ob):
    keys_l = sorted({x for x, _ in oa + ob}); keys_r = sorted({y for _, y in oa + ob})
    la, ra = ctx_vec(oa, keys_l, keys_r); lb, rb = ctx_vec(ob, keys_l, keys_r)
    return (jsd(la + 1e-9, lb + 1e-9) + jsd(ra + 1e-9, rb + 1e-9)) / 2


def perm_p(a, b, n=300):
    oa, ob = occ[a], occ[b]
    obs = divergence(oa, ob)
    pool = oa + ob; k = len(oa); ge = 0
    for _ in range(n):
        rng.shuffle(pool)
        if divergence(pool[:k], pool[k:]) >= obs:
            ge += 1
    return obs, (ge + 1) / (n + 1)


# ---- distributional similarity (cosine on smoothed L/R neighbour profiles) for all candidate pairs ----
allk = sorted({x for s in cand for o in occ[s] for x in o})
idx = {k: i for i, k in enumerate(allk)}
M = np.zeros((len(cand), 2 * len(allk)))
for i, s in enumerate(cand):
    for a, b in occ[s]:
        M[i, idx[a]] += 1; M[i, len(allk) + idx[b]] += 1
P = M / M.sum(1, keepdims=True)
P = np.sqrt(P)  # Hellinger-style
Pn = P / np.linalg.norm(P, axis=1, keepdims=True)
D = Pn @ Pn.T
np.fill_diagonal(D, -1)
rankD = (-D).argsort(1).argsort(1)  # rank of j among i's neighbours (0 = nearest)


# ---- image similarity ----
def load_img(s):
    im = Image.open(ROOT / f"data/sign_images/{s}.png").convert("RGBA")
    a = np.array(im).astype(float)
    ink = (a[..., 3] / 255) * (1 - a[..., :3].mean(-1) / 255)
    ys, xs = np.where(ink > 0.2)
    ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = ink.shape; S = max(h, w)
    pad = np.zeros((S, S)); pad[(S - h) // 2:(S - h) // 2 + h, (S - w) // 2:(S - w) // 2 + w] = ink
    img = Image.fromarray((pad * 255).astype(np.uint8)).resize((40, 40), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
    v = np.array(img, float).ravel()
    return v / (np.linalg.norm(v) + 1e-9)


IMG = np.array([load_img(s) for s in cand])
IS = IMG @ IMG.T
np.fill_diagonal(IS, -1)
iu = np.triu_indices(len(cand), 1)
img_thr = float(np.quantile(IS[iu], 0.98))
dist_thr = float(np.quantile(D[iu], 0.95))

pairs = []
for i, j in zip(*iu):
    if IS[i, j] >= img_thr:
        a, b = cand[i], cand[j]
        obs, p = perm_p(a, b)
        pairs.append({"a": a, "b": b, "tok_a": tok[a], "tok_b": tok[b], "img_sim": float(IS[i, j]), "ctx_cos": float(D[i, j]),
                      "rank_ab": int(rankD[i, j]) + 1, "rank_ba": int(rankD[j, i]) + 1, "ctx_jsd": obs, "perm_p_diff": p})
# classify (three tiers; permutation power grows with frequency, so "distinguishable" frequent pairs with
# near-identical neighbour profiles are reported as a variant family, not as distinct signs)
for x in pairs:
    mutual = max(x["rank_ab"], x["rank_ba"]) <= 5
    if x["ctx_cos"] >= dist_thr and mutual and x["perm_p_diff"] > 0.05:
        x["verdict"] = "allograph-candidate"
    elif x["ctx_cos"] >= dist_thr and mutual:
        x["verdict"] = "variant-family (contexts similar but distinguishable)"
    elif x["perm_p_diff"] < 0.01:
        x["verdict"] = "lookalike-distinct"
    else:
        x["verdict"] = "undecided (low power)"
# visual check of the drawings (by eye, data/sign_images) for every allograph-candidate / variant-family pair
VISUAL = {
    ("M12", "M14"): "same figure, extra head strokes: accept",
    ("M387", "M386"): "same leaf outline, M386 empty: accept",
    ("M389", "M386"): "same leaf outline, M386 empty: accept",
    ("M216", "M226"): "same crossed-chevron, extra tick: accept",
    ("M343", "M344"): "same handled jar, 1 vs 2 inner strokes: accept as probable (inner strokes may carry meaning, cf. shaunmortal F16)",
    ("M343", "M345"): "same handled jar, 1 vs 3 inner strokes: accept as probable (as above)",
    ("M267", "M286"): "different interior (heart vs dotted circle in diamond): possible only",
    ("M391", "M286"): "oval with spokes vs diamond: reject",
    ("M397", "M177"): "stick with circle vs ladder: reject (blurred-image artefact)",
}
for x in pairs:
    v = VISUAL.get((x["a"], x["b"])) or VISUAL.get((x["b"], x["a"]))
    if v:
        x["visual"] = v
pairs.sort(key=lambda x: (x["verdict"], -x["ctx_cos"]))

# also: context-only near-twins (no image condition) for the record
twins = []
for i, j in zip(*iu):
    if max(rankD[i, j], rankD[j, i]) == 0 and D[i, j] >= dist_thr:
        twins.append((cand[i], cand[j], float(D[i, j]), float(IS[i, j])))


# ---- held-out validation ----
def ho_bits(merge):
    f = lambda r: [merge.get(s, s) for s in r]
    bg = Bigram([f(r) for r in dev_runs])
    tot = sum(bg.logprob(f(r)) for r in ho_runs)
    n = sum(len(r) + 1 for r in ho_runs)
    return -tot / n


DISTINCT = {frozenset((x["a"], x["b"])) for x in pairs if x["perm_p_diff"] < 0.01}


def to_merge(pairlist, guard=True):
    """Greedy union onto the most frequent member; refuse a union that would join two members whose
    contexts differ significantly (prevents chaining M391-M286-M267)."""
    group = {}
    def members(x):
        return group.get(x, {x})
    for a, b in pairlist:
        ga, gb = members(a), members(b)
        if ga is gb or (a in gb):
            continue
        if guard and any(frozenset((p, q)) in DISTINCT for p in ga for q in gb):
            continue
        g = ga | gb
        for m in g:
            group[m] = g
    out = {}
    for g in {id(g): g for g in group.values()}.values():
        head = max(g, key=lambda s: tok[s])
        for m in g:
            if m != head:
                out[m] = head
    return out


base = ho_bits({})
allo = [(x["a"], x["b"]) for x in sorted(pairs, key=lambda x: -x["ctx_cos"]) if x["verdict"] == "allograph-candidate"]
allo_vis = [p for p in allo if "accept" in (VISUAL.get(p) or VISUAL.get(p[::-1]) or "")]
look = [(x["a"], x["b"]) for x in pairs if x["verdict"] == "lookalike-distinct"]
bits_allo = ho_bits(to_merge(allo))
bits_allo_vis = ho_bits(to_merge(allo_vis))
fam = [(x["a"], x["b"]) for x in pairs if x["verdict"].startswith("variant")]
bits_fam = ho_bits(to_merge(fam, guard=False))
bits_look = ho_bits(to_merge(rng.sample(look, min(len(look), len(allo))), guard=False)) if look else None
# null: random frequency-matched merges (same number of pairs, partners within factor 2 of frequency)
null = []
for _ in range(200):
    pl = []
    for a, b in allo:
        pool = [s for s in cand if s not in (a, b) and 0.5 <= tok[s] / tok[b] <= 2]
        c = rng.choice(pool) if pool else rng.choice(cand)
        pl.append((a, c))
    null.append(ho_bits(to_merge(pl)))
null = np.array(null)
# null 2: context-matched pairs that do NOT look alike (image sim below median), same number of pairs
lowimg = float(np.median(IS[iu]))
ctxpool = [(cand[i], cand[j], D[i, j]) for i, j in zip(*iu) if IS[i, j] < lowimg]
null2 = []
for _ in range(200):
    pl = []
    for a, b in allo:
        cc = D[cand.index(a), cand.index(b)]
        near = [p for p in ctxpool if abs(p[2] - cc) < 0.05]
        if near:
            p = rng.choice(near); pl.append((p[0], p[1]))
    null2.append(ho_bits(to_merge(pl, guard=False)))
null2 = np.array(null2)

# same validation on ICIT? (Wells list differs; done via bridge in q6)
out = {
    "dev_signs_considered": len(cand), "min_dev_tokens": MIN, "image_sim_threshold_top2pct": img_thr,
    "ctx_cos_threshold_top5pct": dist_thr, "pairs_tested_perm": len(pairs),
    "n_allograph_candidates": len(allo), "n_lookalike_distinct": len(look),
    "heldout_bits_per_sign": {"published_list": base, "allograph_merges": bits_allo, "lookalike_merges": bits_look,
                              "random_matched_merges_mean": float(null.mean()), "random_sd": float(null.std()),
                              "z_vs_random": float((bits_allo - null.mean()) / null.std()),
                              "p_random_le": float(((null <= bits_allo).sum() + 1) / (len(null) + 1)),
                              "visual_accepted_merges": bits_allo_vis, "variant_family_merges": bits_fam,
                              "ctx_matched_nonlookalike_mean": float(null2.mean()), "ctx_matched_sd": float(null2.std()),
                              "p_ctxmatched_le": float(((null2 <= bits_allo).sum() + 1) / (len(null2) + 1))},
    "pairs": pairs, "context_twins": twins,
    "merge_map": to_merge(allo), "merge_map_visual": to_merge(allo_vis),
}
save_json("q2_allographs", out)
json.dump(out, open(ROOT / "experiments/structure/allographs.json", "w"), indent=1, default=float)
print({k: v for k, v in out.items() if k not in ("pairs", "context_twins")})
for x in pairs:
    if not x["verdict"].startswith("undecided"):
        print(x["verdict"], x["a"], x["b"], x["tok_a"], x["tok_b"], round(x["img_sim"], 3), round(x["ctx_cos"], 3), x["rank_ab"], x["rank_ba"], round(x["perm_p_diff"], 3), x.get("visual", ""))
print("undecided", [(x["a"], x["b"], round(x["ctx_cos"], 2), round(x["perm_p_diff"], 2)) for x in pairs if x["verdict"].startswith("undecided")])
print("twins", twins)
