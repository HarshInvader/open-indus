"""EXPLORATORY (not pre-registered), run after b_editor_agreement.py: which sign pairs make up the M77-ICIT
substitutions, how concentrated they are, and how the rate moves with a stricter link-error cut.

    board/run.sh .venv/bin/python -I experiments/audit_followups/b2_explore.py
"""
import sys, json
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
sys.path.insert(0, str(HERE))
import harness as H  # noqa
import b_editor_agreement as B  # noqa
from corpus.load import m77_texts, icit_texts  # noqa


def subs(a, b):
    """traceback returning substituted (M, W) pairs and the extra signs on each side."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = 0 if B.eq(a[i - 1], b[j - 1]) else 1
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + c)
    out, mx, ix = [], [], []
    i, j = n, m
    while i or j:
        if i and j and D[i][j] == D[i - 1][j - 1] + (0 if B.eq(a[i - 1], b[j - 1]) else 1):
            if not B.eq(a[i - 1], b[j - 1]) and a[i - 1][1] is not None: out.append((a[i - 1][0], b[j - 1][0]))
            i -= 1; j -= 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            mx.append(a[i - 1][0]); i -= 1
        else:
            ix.append(b[j - 1][0]); j -= 1
    return out, mx, ix


def main():
    V = H.Variant("ICIT")
    d = json.load(open(HERE / "out" / "b_editor_agreement.json"))
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    icit = {t["id"]: t for t in icit_texts()}
    pairs = [p for p in d["pairs"] if p["norm"] <= B.LINK_ERR]
    S, MX, IX = Counter(), Counter(), Counter()
    for p in pairs:
        a = [(s, B.wset(V, s)) for s in B.flat(m77[(p["text_no"], p["side"])]["seq"])]
        b = [(s, frozenset([s])) for s in B.flat(icit[p["icit"]]["seq"])]
        s, mx, ix = subs(a, b)
        S.update(s); MX.update(mx); IX.update(ix)
    tot = sum(S.values())
    top = S.most_common(25)
    cum10 = sum(c for _, c in S.most_common(10)) / tot
    repeated = sum(c for _, c in S.items() if c >= 3) / tot
    res = dict(n_sub=tot, distinct_pairs=len(S), share_top10_pairs=cum10, share_pairs_seen_3plus=repeated,
               top_pairs=[(f"{m}->{w}", c, sorted(V.inv.get(m, []))) for (m, w), c in top],
               m77_extra_top=MX.most_common(10), icit_extra_top=IX.most_common(10))
    # stricter link cut sensitivity
    for cut in (0.5, 0.6, 0.7, 0.8):
        ps = [p for p in d["pairs"] if p["norm"] <= cut]
        c = Counter()
        for p in ps: c.update(p["ops"])
        den = sum(p["n_m77"] for p in ps) - c["sub_unmapped"]
        res[f"rate_total_cut{cut}"] = dict(texts=len(ps), rate=(c["sub"] + c["m77_extra"] + c["icit_extra"] + c["transpose"]) / den,
                                          rate_sub=c["sub"] / den)
    print(json.dumps(res, indent=1))
    json.dump(res, open(HERE / "out" / "b2_explore.json", "w"), indent=1)



def corrected():
    """EXPLORATORY: treat every (M, W) substitution pair seen >= 3 times as a mapping equivalence
    (bridge/override error or a consistent sign-list convention), realign, recompute the rate."""
    import random as _r
    V = H.Variant("ICIT")
    d = json.load(open(HERE / "out" / "b_editor_agreement.json"))
    ex = json.load(open(HERE / "out" / "b2_explore.json"))
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    icit = {t["id"]: t for t in icit_texts()}
    pairs = [p for p in d["pairs"] if p["norm"] <= B.LINK_ERR]
    S = Counter()
    for p in pairs:
        a = [(s, B.wset(V, s)) for s in B.flat(m77[(p["text_no"], p["side"])]["seq"])]
        b = [(s, frozenset([s])) for s in B.flat(icit[p["icit"]]["seq"])]
        S.update(subs(a, b)[0])
    extra = {}
    for (m, w), c in S.items():
        if c >= 3: extra.setdefault(m, set()).add(w)
    per = []
    for p in pairs:
        a = [(s, frozenset((B.wset(V, s) or set()) | extra.get(s, set())) or None) for s in B.flat(m77[(p["text_no"], p["side"])]["seq"])]
        b = [(s, frozenset([s])) for s in B.flat(icit[p["icit"]]["seq"])]
        dist, ops = B.align(a, b, B.eq)
        per.append((len(a), ops))

    def rate(ps):
        c = Counter(); n = 0
        for L, o in ps: c.update(o); n += L
        den = n - c["sub_unmapped"]
        return (c["sub"] + c["m77_extra"] + c["icit_extra"] + c["transpose"]) / den, c["sub"] / den, (c["m77_extra"] + c["icit_extra"]) / den
    r0 = rate(per)
    rng = _r.Random(1); bs = sorted(rate([rng.choice(per) for _ in per])[0] for _ in range(2000))
    out = dict(equivalences_added={m: sorted(w) for m, w in extra.items()}, rate_total=r0[0], rate_sub=r0[1], rate_indel=r0[2],
               ci95_total=[bs[50], bs[1949]], texts=len(per))
    print(json.dumps(out, indent=1))
    ex["corrected_mapping"] = out
    json.dump(ex, open(HERE / "out" / "b2_explore.json", "w"), indent=1)


if __name__ == "__main__":
    main()
    corrected()
