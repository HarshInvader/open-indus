"""parpola_rules34: Parpola's rule 3 (M87 substitutes for fish M59) and rule 4
(M403 has fixed partners M87 / squirrel). Prereg: docs/prereg/parpola_rules34.md.

Library only; run.py drives the stages. Distinct texts only. Line breaks '|' are
transparent (a text reads on across lines); '#' (break) leaves the context unknown.
"""
import json
import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "corpus"))
import load as L  # noqa: E402

# Post-1977 ICIT sites (same list as experiments/fish_tick_closer).
POST1977 = {"Dholavira", "Nausharo", "Banawali", "Rakhigarhi", "Farmana", "Bhirrana", "Gola Dhoro (Bagasra)",
            "Karanpura", "Khirsara", "Kanmer", "Shikarpur", "Lakhanjo-daro", "Tarkhanewala-dera", "Naru-Waro-dharo"}

# Sign identities fixed from the drawings before any context was looked at (prereg section 2).
SIGNS = {
    "M": dict(fish="M59", vel="M87", muruku="M403", squirrel=("M51", "M52")),
    "W": dict(fish="W220", vel="W032", muruku="W840", squirrel=("W255",)),  # W255 = M51 (bridge); M52 has no W
}
EXCLUDE = {  # never used as null-pool members (they are the tested signs)
    "M": {"M59", "M87", "M403", "M51", "M52"},
    "W": {"W220", "W032", "W840", "W255"},
}

R_SUB = 20          # subsample draws per pair (rule 3)
S_PLANT = 0.25      # rule 3 gate: share of the planted sign's tokens that stand in the partner's slots
Q_PLANT = 0.30      # rule 4 gate: share of the head's tokens given the planted fixed partner
N_GATE = 50         # planted trials per gate
N_SHUF = 1000       # within-text shuffles (red team)


# ------------------------------------------------------------------ data
def prep(texts):
    out = []
    for t in L.distinct(texts):
        seq = [s for s in t["seq"] if s != "|"]
        if any(s != "#" for s in seq):
            out.append(seq)
    return out


def load(split):
    if split in ("dev", "held"):
        dev, ho = L.dev_heldout(version=2)
        return prep(dev if split == "dev" else ho), "M"
    if split == "new":
        return prep([t for t in L.icit_texts() if t["site"] in POST1977]), "W"
    raise ValueError(split)


def collapse_near(texts_raw):
    """Near-copy collapse (fish_tick_closer rule) for the red team."""
    sys.path.insert(0, str(ROOT / "experiments" / "fish_tick_closer"))
    import ftc  # noqa: E402  (reads only; no side effects)
    return prep(ftc.collapse(texts_raw))


def counts(texts):
    return Counter(s for t in texts for s in t if s != "#")


def occurrences(texts):
    """sign -> list of (left, right); '^'/'$' at text edges, None next to a break."""
    occ = {}
    for t in texts:
        n = len(t)
        for i, s in enumerate(t):
            if s == "#":
                continue
            left = "^" if i == 0 else (None if t[i - 1] == "#" else t[i - 1])
            right = "$" if i == n - 1 else (None if t[i + 1] == "#" else t[i + 1])
            occ.setdefault(s, []).append((left, right))
    return occ


def _seed(*parts):
    return zlib.crc32("|".join(map(str, parts)).encode())


# ------------------------------------------------------------------ rule 3
def _cos(c1, c2):
    if not c1 or not c2:
        return 0.0
    dot = sum(v * c2.get(k, 0) for k, v in c1.items())
    return dot / (np.sqrt(sum(v * v for v in c1.values())) * np.sqrt(sum(v * v for v in c2.values())))


def overlap(occ, a, b, n_sub, seed=0, edges=True):
    """Mean over R_SUB draws of 0.5*(cos(left ctx) + cos(right ctx)), each sign
    subsampled to n_sub occurrences so frequency does not drive the score."""
    rng = np.random.default_rng(_seed(seed, *sorted((a, b))))
    oa, ob = occ[a], occ[b]
    vals = []
    for _ in range(R_SUB):
        ia = rng.choice(len(oa), n_sub, replace=False)
        ib = rng.choice(len(ob), n_sub, replace=False)
        res = []
        for side in (0, 1):
            ca = Counter(oa[i][side] for i in ia if oa[i][side] is not None and (edges or oa[i][side] not in "^$"))
            cb = Counter(ob[i][side] for i in ib if ob[i][side] is not None and (edges or ob[i][side] not in "^$"))
            res.append(_cos(ca, cb))
        vals.append(np.mean(res))
    return float(np.mean(vals))


def rule3_pool(cnt, a, b, excl):
    lo, hi = 0.5 * min(cnt[a], cnt[b]), 2 * max(cnt[a], cnt[b])
    pool = sorted(s for s in cnt if lo <= cnt[s] <= hi and s not in excl and s not in (a, b))
    return pool, int(lo)


def rule3(texts, a, b, excl, seed=0, edges=True, pairs=None):
    cnt, occ = counts(texts), occurrences(texts)
    pool, n_sub = rule3_pool(cnt, a, b, excl)
    obs = overlap(occ, a, b, n_sub, seed, edges)
    if pairs is None:
        pairs = [(pool[i], pool[j]) for i in range(len(pool)) for j in range(i + 1, len(pool))]
    null = np.array([overlap(occ, x, y, n_sub, seed, edges) for x, y in pairs])
    p = (1 + int((null >= obs).sum())) / (1 + len(null))
    return dict(a=a, b=b, n_a=cnt[a], n_b=cnt[b], n_sub=n_sub, pool=len(pool), n_null=len(null), obs=obs,
                null_median=float(np.median(null)), null_q95=float(np.quantile(null, 0.95)),
                null_max=float(null.max()), p=p, above_median=bool(obs > np.median(null)))


def position_profile(occ, s):
    c = Counter()
    for l, r in occ[s]:
        c[("I" if l == "^" else "") + ("F" if r == "$" else "") or "M"] += 1
    n = sum(c.values())
    return np.array([c[k] / n for k in ("I", "M", "F", "IF")])


def rule3_position_pairs(texts, a, b, excl, k=50):
    """Alt null A: the k pool pairs whose position profiles are closest to (a, b)."""
    cnt, occ = counts(texts), occurrences(texts)
    pool, _ = rule3_pool(cnt, a, b, excl)
    pa, pb = position_profile(occ, a), position_profile(occ, b)
    tv = lambda u, v: 0.5 * np.abs(u - v).sum()  # noqa: E731
    sc = []
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            x, y = pool[i], pool[j]
            px, py = position_profile(occ, x), position_profile(occ, y)
            sc.append((min(tv(px, pa) + tv(py, pb), tv(py, pa) + tv(px, pb)), x, y))
    sc.sort()
    return [(x, y) for _, x, y in sc[:k]]


# ------------------------------------------------------------------ rule 4
def share_next(occ, h, partners):
    rs = [r for _, r in occ.get(h, []) if r is not None]
    return (sum(r in partners for r in rs) / len(rs)) if rs else float("nan"), len(rs)


def rule4_pools(cnt, head, partners_main, partners_sq, excl):
    f1 = cnt[partners_main]
    fs = sum(cnt[s] for s in partners_sq)
    fh = cnt[head]
    bad = excl | {head, partners_main, *partners_sq}
    p1 = sorted(s for s in cnt if f1 / 2 <= cnt[s] <= 2 * f1 and s not in bad)
    ps = sorted(s for s in cnt if fs / 2 <= cnt[s] <= 2 * fs and s not in bad)
    heads = sorted(s for s in cnt if fh / 2 <= cnt[s] <= 2 * fh and s not in bad)
    return p1, ps, heads


def rule4(texts, head, p_main, p_sq, excl):
    """Primary null (b): pseudo-partner sets {x, y}, x matched to p_main, y to the squirrel set."""
    cnt, occ = counts(texts), occurrences(texts)
    P = {p_main, *p_sq}
    obs, n = share_next(occ, head, P)
    p1, ps, heads = rule4_pools(cnt, head, p_main, p_sq, excl)
    null = np.array([share_next(occ, head, {x, y})[0] for x in p1 for y in ps if x != y])
    p = (1 + int((null >= obs).sum())) / (1 + len(null))
    nxt = Counter(r for _, r in occ.get(head, []) if r is not None)
    return dict(head=head, n_head_tokens=cnt[head], n_with_next=n, obs_share=obs,
                share_main=nxt[p_main] / n if n else None, share_sq=sum(nxt[s] for s in p_sq) / n if n else None,
                n_null=len(null), null_median=float(np.median(null)), null_q05=float(np.quantile(null, 0.05)),
                null_q95=float(np.quantile(null, 0.95)), null_q99=float(np.quantile(null, 0.99)), p=p,
                top_next=nxt.most_common(6))


def rule4_heads_null(texts, head, p_main, p_sq, excl):
    """Alt null A: other heads matched in frequency to the head, same true partner set."""
    cnt, occ = counts(texts), occurrences(texts)
    P = {p_main, *p_sq}
    obs, _ = share_next(occ, head, P)
    _, _, heads = rule4_pools(cnt, head, p_main, p_sq, excl)
    null = np.array([share_next(occ, h, P)[0] for h in heads])
    null = null[~np.isnan(null)]
    return dict(obs=obs, n_null=len(null), null_q95=float(np.quantile(null, 0.95)),
                p=(1 + int((null >= obs).sum())) / (1 + len(null)))


# ------------------------------------------------------------------ shuffles (alt null B)
def shuffle_within(texts, rng):
    out = []
    for t in texts:
        idx = [i for i, s in enumerate(t) if s != "#"]
        vals = [t[i] for i in idx]
        rng.shuffle(vals)
        u = list(t)
        for i, v in zip(idx, vals):
            u[i] = v
        out.append(u)
    return out


# ------------------------------------------------------------------ planting (gates)
def plant_substitution(texts, a, b, s, rng):
    """Relabel k random tokens of b as a, with k/(n_a+k) = s."""
    pos = [(ti, i) for ti, t in enumerate(texts) for i, x in enumerate(t) if x == b]
    na = sum(x == a for t in texts for x in t)
    k = min(int(round(s * na / (1 - s))), len(pos) // 2)
    chosen = rng.choice(len(pos), k, replace=False)
    out = [list(t) for t in texts]
    for c in chosen:
        ti, i = pos[c]
        out[ti][i] = a
    return out, k


def plant_partner(texts, h, x, q, rng):
    """In a share q of h's tokens, make x the next sign (replace it, or insert at text end / before a break)."""
    pos = [(ti, i) for ti, t in enumerate(texts) for i, s in enumerate(t) if s == h]
    k = int(round(q * len(pos)))
    chosen = set(int(c) for c in rng.choice(len(pos), k, replace=False))
    out = [list(t) for t in texts]
    by_text = {}
    for c in chosen:
        ti, i = pos[c]
        by_text.setdefault(ti, []).append(i)
    for ti, idxs in by_text.items():
        t = out[ti]
        for i in sorted(idxs, reverse=True):
            if i + 1 < len(t) and t[i + 1] != "#":
                t[i + 1] = x
            else:
                t.insert(i + 1, x)
    return out, k


def save(key, obj):
    p = Path(__file__).resolve().parent / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[key] = obj
    json.dump(d, open(p, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
