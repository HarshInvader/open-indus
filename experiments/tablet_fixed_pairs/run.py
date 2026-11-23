"""Out-of-sample check: do later-published tablets carry the same fixed numeral pairs? (prereg docs/prereg/tablet_fixed_pairs.md)
Run: .venv/bin/python -I experiments/tablet_fixed_pairs/run.py shape   # counts of ICIT-only legends; no numeral read
     .venv/bin/python -I experiments/tablet_fixed_pairs/run.py test
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corpus")); sys.path.insert(0, str(ROOT / "experiments/grammar"))
sys.path.insert(0, str(ROOT / "experiments/count_index_rehearsal"))
import load as L                # noqa: E402
import glib                     # noqa: E402
from corpus.build import _close  # noqa: E402
import cir                      # noqa: E402

SEED = 20261130; NPERM = 10000; MIN_TAB = 10
SITES_M = {"Harappa": "Harappa", "Mohenjo-daro": "Mohenjodaro"}
# frozen from numerals_by_object (M77 tablets; exploratory there)
TAB_PAIRS = {"M403": 3, "M197": 7, "M190": 3, "M194": 7, "M25": 1}
SHORT, TALL = cir.indus_tables()


def numeral_tokens(signs):
    """numeral directly before a non-numeral head inside a break-free run (same rule as numerals_by_object)"""
    isnum = lambda s: s in SHORT or s in TALL
    out = []
    for r in signs:
        for i, s in enumerate(r):
            if isnum(s) and i + 1 < len(r) and not isnum(r[i + 1]):
                out.append((r[i + 1], (SHORT if s in SHORT else TALL)[s]))
    return out


def m77_seal_pairs():
    """Seal analogue, frozen from M77 before ICIT is read: for the 5 seal heads with most numeral tokens on M77 seals
    (Harappa + Mohenjo-daro, distinct texts), the modal numeral value."""
    vals = defaultdict(list)
    for x in L.distinct(L.m77_texts()):
        if x["site"] in SITES_M.values() and x["object_type"] == "seal":
            for h, v in numeral_tokens(L.runs(x["seq"])):
                vals[h].append(v)
    top = sorted(vals, key=lambda h: -len(vals[h]))[:5]
    return {h: Counter(vals[h]).most_common(1)[0][0] for h in top}, {h: len(vals[h]) for h in top}


def icit_only():
    """Distinct ICIT legends at Harappa / Mohenjo-daro (seal, tablet, copper registers), bridged to M77 signs, with no exact or
    near copy among any M77 text (corpus.build._close). Returns [(register, site, runs)]."""
    m77 = [tuple(s for s in x["seq"] if s not in ("|", "#")) for x in L.distinct(L.m77_texts())]
    m77_set = set(m77); by_len = defaultdict(list)
    for s in m77:
        by_len[len(s)].append(list(s))
    out = []
    for u in glib.icit_units(sites=set(SITES_M), types={"seal", "tablet", "copper"}):
        b = glib.bridge_unit(u); m = list(b["signs"])
        if tuple(m) in m77_set or any(_close(m, s) for L_ in range(len(m) - 1, len(m) + 2) for s in by_len.get(L_, [])):
            continue
        out.append((u["register"], u["site"], [list(r) for r, _, _ in b["runs"]]))
    return out


def rate(tokens, pairs):
    hits = [int(v == pairs[h]) for h, v in tokens if h in pairs]
    return (sum(hits), len(hits))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "shape"
    seal_pairs, seal_n = m77_seal_pairs()
    units = icit_only()
    if mode == "shape":
        print(dict(seal_pairs=seal_pairs, seal_tokens_m77=seal_n,
                   icit_only=dict(Counter((r, s) for r, s, _ in units))))
    elif mode == "test":
        tab = [(s, numeral_tokens(runs)) for r, s, runs in units if r == "tablet"]          # copper: secondary only (see prereg)
        cop = [(s, numeral_tokens(runs)) for r, s, runs in units if r == "copper"]
        sea = [(s, numeral_tokens(runs)) for r, s, runs in units if r == "seal"]
        kt, nt = rate([t for _, ts in tab for t in ts], TAB_PAIRS)
        ks, ns = rate([t for _, ts in sea for t in ts], seal_pairs)
        res = dict(tablet=dict(hits=kt, n=nt, rate=kt / nt if nt else None), seal=dict(hits=ks, n=ns, rate=ks / ns if ns else None),
                   seal_pairs=seal_pairs, tab_pairs=TAB_PAIRS)
        if nt < MIN_TAB:
            res["verdict"] = f"untestable: {nt} ICIT-only tablet tokens on the five heads (< {MIN_TAB})"
        else:
            # null: tablet and seal LEGENDS (each with its matched tokens as 0/1 hits) pooled and relabelled, sizes kept
            leg = [([int(v == TAB_PAIRS[h]) for h, v in ts if h in TAB_PAIRS], 1) for _, ts in tab] + \
                  [([int(v == seal_pairs[h]) for h, v in ts if h in seal_pairs], 0) for _, ts in sea]
            leg = [(h, l) for h, l in leg if h]
            rng = np.random.default_rng(SEED); labs = np.array([l for _, l in leg]); obs = kt / nt - ks / max(ns, 1)
            null = []
            for _ in range(NPERM):
                p = rng.permutation(labs); a = [x for (h, _), l in zip(leg, p) if l == 1 for x in h]; b = [x for (h, _), l in zip(leg, p) if l == 0 for x in h]
                null.append(np.mean(a) - np.mean(b) if a and b else 0.0)
            null = np.array(null); pv = float((1 + (null >= obs).sum()) / (NPERM + 1))
            per_pair = {h: rate([t for _, ts in tab for t in ts], {h: v}) for h, v in TAB_PAIRS.items()}
            res.update(diff=obs, p=pv, per_pair=per_pair, n_tab_legends=sum(1 for h, l in leg if l == 1), n_seal_legends=sum(1 for h, l in leg if l == 0),
                       passed=bool(pv <= 0.01 and obs > 0),
                       verdict="replicates: later tablets keep the fixed pairs more than seals keep theirs" if pv <= 0.01 and obs > 0
                       else "does not replicate above the seal rate")
        kc, nc = rate([t for _, ts in cop for t in ts], TAB_PAIRS); res["copper_secondary"] = dict(hits=kc, n=nc)
        print(json.dumps(res, indent=1)); json.dump(res, open(HERE / "result.json", "w"), indent=1)
