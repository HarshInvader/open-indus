"""local_hands: shared library (frozen with MINIMUM.txt).

Question: is the choice between ICIT (Wells/Fuls) variants of one Mahadevan sign set by the
neighbouring sign (contextual allograph) or by place / period (local hand)?

Sign space and tokeniser: ICIT records as built by corpus/build.py icit() and read by
corpus.load.icit_texts() (W### tokens, reading order, '|' line break, '#' damage).
Sign runs: corpus.load.runs (cut at '|' and '#').

Variant families: experiments/consensus_corpus/out/concordance.json "primary" map (M sign ->
list of W signs; the project's corrected M77 -> ICIT concordance). See families_from_map().

Text families (for the hold-out): experiments/split_witness/sw_lib.families() (union-find over
distinct flattened ICIT sequences, corpus/build.py _close rule).

Statistics (all in G form: G = 2 * N * conditional mutual information, natural log):
  G(form ; X | stratum) = 2 * sum_cells n_sxf * ln(n_sxf * n_s / (n_sx * n_sf))
  computed with integer codes and np.unique / bincount (no smoothing).
Permutation nulls: form labels shuffled among tokens inside each stratum (perm_within).
This module computes nothing on real data by itself.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, runs  # noqa: E402

CONC = ROOT / "experiments" / "consensus_corpus" / "out" / "concordance.json"
BOUND_L, BOUND_R, LB, DMG = "<s>", "</s>", "<lb>", "<dmg>"
MIN_VARIANT_TOKENS = 10      # dev tokens per variant (section 2 of MINIMUM.txt)
HOLDOUT_MOD = 5              # text family -> held out when hash mod 5 == 0 (20%)


# ---------------------------------------------------------------- families
def families_from_map(primary):
    """Variant families from an M -> [W...] map.
    A W sign is exclusive if it appears in the list of exactly one M sign.
    Family of M = its exclusive W signs, kept only if there are >= 2 of them.
    Returns dict family_id ('M###') -> sorted list of W signs."""
    owners = defaultdict(set)
    for m, ws in primary.items():
        for w in ws:
            owners[w].add(m)
    fam = {}
    for m, ws in primary.items():
        ex = sorted({w for w in ws if len(owners[w]) == 1})
        if len(ex) >= 2:
            fam[m] = ex
    return fam


def load_families():
    return families_from_map(json.load(open(CONC))["primary"])


def icit_type(t):
    """Coarse object type (same rule as experiments/redteam_chrono/rc_lib.icit_type)."""
    t = t.upper()
    if t.startswith("TAB:B"):
        return "tab_moulded"
    if t.startswith("TAB:I"):
        return "tab_incised"
    if t.startswith("TAB"):
        return "tablet"
    if t.startswith("SEAL"):
        return "seal"
    if t.startswith("POT") or t.startswith("POST"):
        return "pot"
    if t.startswith("TAG"):
        return "sealing"
    return "other"


def period_key(r):
    """Within-site period label, or None. ICIT period/phase codes are site-specific, so the
    label is site|period|phase and is only compared inside one site."""
    p, ph = r["period"].strip(), r["phase"].strip()
    if p in ("", "-"):
        return None
    return f"{r['site']}|{p}|{ph if ph not in ('', '-') else ''}"


def flat(seq):
    return [s for s in seq if s not in ("|", "#")]


def holdout_of(text_family_id):
    h = int(hashlib.sha256(f"local_hands:holdout:{text_family_id}".encode()).hexdigest()[:8], 16)
    return h % HOLDOUT_MOD == 0


def neighbours(seq, i):
    """Previous and next item around position i of a raw ICIT seq (with '|' and '#').
    Text edge -> <s> / </s>; line break -> <lb>; damage mark -> <dmg>."""
    def tag(x):
        return LB if x == "|" else DMG if x == "#" else x
    prev = BOUND_L if i == 0 else tag(seq[i - 1])
    nxt = BOUND_R if i == len(seq) - 1 else tag(seq[i + 1])
    return prev, nxt


def collapse(sign, w2fam):
    """Neighbour identity at the merged level: a W in a variant family becomes its family id."""
    return w2fam.get(sign, sign)


def occurrences(fams, text_fam):
    """Eligible occurrences (section 2 of MINIMUM.txt), before the per-variant token floor.
    One record per distinct (site, coarse type, flattened sequence); record order = file order.
    Returns a list of dicts: family, form, site, type, period, prev, next, holdout, rec_id."""
    w2fam = {w: f for f, ws in fams.items() for w in ws}
    seen, out = set(), []
    for r in icit_texts():
        site = r["site"].strip()
        if site in ("", "-") or site.lower().startswith("unknown"):
            continue
        fl = flat(r["seq"])
        if not fl:
            continue
        typ = icit_type(r["type"])
        k = (site, typ, " ".join(fl))
        if k in seen:
            continue
        seen.add(k)
        ho = holdout_of(text_fam[" ".join(fl)])
        seq = r["seq"]
        for i, s in enumerate(seq):
            if s in w2fam:
                p, n = neighbours(seq, i)
                out.append(dict(family=w2fam[s], form=s, site=site, type=typ, period=period_key(r),
                                prev=collapse(p, w2fam), next=collapse(n, w2fam),
                                holdout=ho, rec_id=r["id"]))
    return out


def apply_floor(occ, floor=MIN_VARIANT_TOKENS):
    """Drop variants with < floor DEV tokens; drop families left with < 2 variants.
    The floor is applied on dev tokens only; the same variant set is used for held-out."""
    dev = defaultdict(lambda: defaultdict(int))
    for o in occ:
        if not o["holdout"]:
            dev[o["family"]][o["form"]] += 1
    keep = {f: {w for w, c in d.items() if c >= floor} for f, d in dev.items()}
    keep = {f: ws for f, ws in keep.items() if len(ws) >= 2}
    return [o for o in occ if o["family"] in keep and o["form"] in keep[o["family"]]], keep


# ---------------------------------------------------------------- statistics
def codes(*cols):
    """Joint integer code of several columns (lists of hashables)."""
    keys = [repr(k) for k in zip(*cols)]
    lut = {k: i for i, k in enumerate(sorted(set(keys)))}  # deterministic, no hash()
    return np.array([lut[k] for k in keys], dtype=np.int64)


def g_cond(form, x, strat):
    """G = 2 * sum n ln(n n_s / (n_sx n_sf)) over strata s, x levels and form levels f.
    form, x, strat: int arrays."""
    def cnt(*a):
        k = np.zeros(len(a[0]), dtype=np.int64)
        for v in a:
            k = k * (int(v.max()) + 1) + v
        _, inv, c = np.unique(k, return_inverse=True, return_counts=True)
        return c[inv]
    n_sxf = cnt(strat, x, form)
    n_s = cnt(strat)
    n_sx = cnt(strat, x)
    n_sf = cnt(strat, form)
    # sum over tokens of ln(...) equals sum over cells of n * ln(...)
    return float(2.0 * np.sum(np.log(n_sxf * n_s / (n_sx * n_sf))))


def h_cond(form, strat):
    """Conditional entropy H(form | strat) * N, nats (used for the normalised effect)."""
    k = strat * (int(form.max()) + 1) + form
    _, inv, c = np.unique(k, return_inverse=True, return_counts=True)
    _, inv_s, cs = np.unique(strat, return_inverse=True, return_counts=True)
    return float(-np.sum(np.log(c[inv] / cs[inv_s])))


def dense(*cols):
    """Dense joint code of integer arrays."""
    k = np.zeros(len(cols[0]), dtype=np.int64)
    for v in cols:
        k = k * (int(v.max()) + 1) + v
    return np.unique(k, return_inverse=True)[1].astype(np.int64)


def make_g(x, strat, form0):
    """Fast G(form; x | strat) for forms that are within-stratum permutations of form0.
    Under such permutations n_s, n_sx and n_sf are fixed, so only sum n_sxf ln n_sxf moves.
    Returns g(form); equals g_cond(form, x, strat)."""
    sx = dense(strat, x)
    nf = int(form0.max()) + 1

    def xlogx(c):
        c = c[c > 0].astype(float)
        return float(np.sum(c * np.log(c)))
    const = (xlogx(np.bincount(strat)) - xlogx(np.bincount(sx))
             - xlogx(np.bincount(dense(strat, form0))))

    def g(form):
        return 2.0 * (xlogx(np.bincount(sx * nf + form)) + const)
    return g


def perm_within(form, strat, rng):
    """Shuffle form labels among tokens of the same stratum."""
    order = np.lexsort((rng.random(len(form)), strat))
    out = np.empty_like(form)
    # tokens sorted by stratum then random key; refill each stratum block with its own labels
    srt = np.argsort(strat, kind="stable")
    out[order] = form[srt]
    return out


def perm_p(stat_fn, form, strat, rng, nperm):
    obs = stat_fn(form)
    null = np.array([stat_fn(perm_within(form, strat, rng)) for _ in range(nperm)])
    p = float((1 + np.sum(null >= obs - 1e-9)) / (nperm + 1))
    return obs, p, null


def arrays(occ):
    """Integer arrays for the tests from occurrence dicts."""
    form = codes([o["family"] for o in occ], [o["form"] for o in occ])
    fam = codes([o["family"] for o in occ])
    site = codes([o["site"] for o in occ])
    typ = codes([o["type"] for o in occ])
    prev = codes([o["prev"] for o in occ])
    nxt = codes([o["next"] for o in occ])
    return dict(form=form, fam=fam, site=site, type=typ, prev=prev, next=nxt)


MIN_CTX_TOKENS = 5          # neighbour values rarer than this (per family, per side) -> <other>


def collapse_ctx(A, k=MIN_CTX_TOKENS):
    """Per family and per side, neighbour values with < k tokens in the analysed set become one
    reserved code (<other>). Uses no form labels. Returns a new array dict."""
    B = dict(A)
    for side in ("prev", "next"):
        v = A[side].copy()
        other = int(v.max()) + 1
        key = dense(A["fam"], v)
        cnt = np.bincount(key)[key]
        v[cnt < k] = other
        B[side] = v
    return B


def nb_test(A, rng, nperm):
    """Neighbour test, place controlled. Strata = family x site x type.
    T_nb = G(form; prev | stratum) + G(form; next | stratum). Null: forms permuted in strata.
    Rare neighbour values are pooled first (collapse_ctx)."""
    A = collapse_ctx(A)
    s = dense(A["fam"], A["site"], A["type"])
    g1, g2 = make_g(A["prev"], s, A["form"]), make_g(A["next"], s, A["form"])
    f = lambda fm: g1(fm) + g2(fm)  # noqa: E731
    obs, p, null = perm_p(f, A["form"], s, rng, nperm)
    # effect = excess over the null mean, as a share of H(form | stratum), mean of two sides
    eff = ((obs - null.mean()) / 2.0) / max(h_cond(A["form"], s), 1e-12) / 2.0
    return dict(T=obs, p=p, null_mean=float(null.mean()), U_excess=float(eff))


def pl_test(A, rng, nperm):
    """Place test, neighbours controlled. Strata = family x type x prev x next.
    T_pl = G(form; site | stratum). Null: forms permuted in strata (site labels fixed).
    Rare neighbour values are pooled first (collapse_ctx)."""
    A = collapse_ctx(A)
    s = dense(A["fam"], A["type"], A["prev"], A["next"])
    f = make_g(A["site"], s, A["form"])
    obs, p, null = perm_p(f, A["form"], s, rng, nperm)
    eff = ((obs - null.mean()) / 2.0) / max(h_cond(A["form"], s), 1e-12)
    return dict(T=obs, p=p, null_mean=float(null.mean()), U_excess=float(eff))


def informative_tokens(strat, x):
    """Tokens in strata that hold >= 2 tokens and >= 2 levels of x. Only these strata can
    carry a dependence of form on x. Uses no form labels (safe for the count gate)."""
    out = np.zeros(len(strat), dtype=bool)
    order = np.argsort(strat, kind="stable")
    s_sorted = strat[order]
    bounds = np.flatnonzero(np.diff(s_sorted)) + 1
    for blk in np.split(order, bounds):
        if len(blk) >= 2 and len(set(x[blk].tolist())) >= 2:
            out[blk] = True
    return out


def informative_counts(A):
    """Gate quantities: tokens that can inform each test (no form labels used)."""
    A = collapse_ctx(A)
    s_nb = dense(A["fam"], A["site"], A["type"])
    s_pl = dense(A["fam"], A["type"], A["prev"], A["next"])
    nb = informative_tokens(s_nb, A["prev"]) | informative_tokens(s_nb, A["next"])
    pl = informative_tokens(s_pl, A["site"])
    return dict(nb_informative=int(nb.sum()), pl_informative=int(pl.sum()))
