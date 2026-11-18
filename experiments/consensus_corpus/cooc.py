"""Step 1a (descriptive, mapping evidence): M77 <-> Wells sign co-occurrence on register-matched texts.

Two kinds of evidence, both computed on the 469 register-matched texts of audit_followups B
(link made through excavation registers, never through signs; norm distance <= 0.8):

  pos   mapping-FREE: on pairs whose M77 and ICIT readings have the same number of signs, count
        (M, W) at the same position. Uses no bridge at all.
  ali   mapping-dependent: (M, W) pairs aligned as match or substitution by the audit's alignment
        under the current harness mapping (bridge + overrides).

Writes out/cooc.json. Pure counting, a few seconds; no test outcomes are looked at.

    .venv/bin/python -I experiments/consensus_corpus/cooc.py
"""
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
sys.path.insert(0, str(ROOT / "experiments" / "audit_followups"))
import harness as H  # noqa
import b_editor_agreement as B  # noqa
import b2_explore as B2  # noqa
from corpus.load import m77_texts, icit_texts  # noqa


def matched_pairs(cut=B.LINK_ERR):
    d = json.load(open(ROOT / "experiments/audit_followups/out/b_editor_agreement.json"))
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    icit = {t["id"]: t for t in icit_texts()}
    out = []
    for p in d["pairs"]:
        if p["norm"] <= cut:
            out.append((p, m77[(p["text_no"], p["side"])], icit[p["icit"]]))
    return out


def main():
    V = H.Variant("ICIT")
    pairs = matched_pairs()
    pos = Counter(); ali = Counter(); mfreq = Counter(); wfreq = Counter()
    for p, mt, it in pairs:
        a = B.flat(mt["seq"]); b = B.flat(it["seq"])
        mfreq.update(a); wfreq.update(b)
        if len(a) == len(b):
            pos.update(zip(a, b))
        A = [(s, B.wset(V, s)) for s in a]; Bb = [(s, frozenset([s])) for s in b]
        # aligned matches + substitutions
        n, m = len(A), len(Bb)
        D = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1): D[i][0] = i
        for j in range(m + 1): D[0][j] = j
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                c = 0 if B.eq(A[i - 1], Bb[j - 1]) else 1
                D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + c)
        i, j = n, m
        while i or j:
            if i and j and D[i][j] == D[i - 1][j - 1] + (0 if B.eq(A[i - 1], Bb[j - 1]) else 1):
                ali[(a[i - 1], b[j - 1])] += 1; i -= 1; j -= 1
            elif i and D[i][j] == D[i - 1][j] + 1:
                i -= 1
            else:
                j -= 1
    cur = {m: sorted(V.inv.get(m, [])) for m in mfreq}
    res = dict(n_pairs=len(pairs), n_equal_len=sum(len(B.flat(mt["seq"])) == len(B.flat(it["seq"])) for _, mt, it in pairs),
               current_map=cur,
               pos=[(m, w, c) for (m, w), c in pos.most_common()],
               ali=[(m, w, c) for (m, w), c in ali.most_common()],
               mfreq=mfreq, wfreq=wfreq)
    json.dump(res, open(HERE / "out" / "cooc.json", "w"), indent=0, default=list)
    # summary: per M sign, pos distribution vs current map
    byM = defaultdict(Counter)
    for (m, w), c in pos.items(): byM[m][w] += c
    print("n_pairs", res["n_pairs"], "equal-length", res["n_equal_len"])
    rows = []
    for m, ctr in byM.items():
        tot = sum(ctr.values()); (w1, c1), = ctr.most_common(1)
        inmap = sum(c for w, c in ctr.items() if w in cur.get(m, []))
        if w1 not in cur.get(m, []) and c1 >= 2:
            rows.append((c1, m, w1, tot, inmap, cur.get(m), ctr.most_common(4)))
    for r in sorted(rows, reverse=True):
        print(r)


if __name__ == "__main__":
    main()
