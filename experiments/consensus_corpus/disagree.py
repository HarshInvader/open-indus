"""Step 1c (descriptive): M77 vs ICIT disagreement on the 469 register-matched texts under three mappings:
harness original, corrected primary, corrected primary + provisional. Same alignment as audit_followups B
(optimal string alignment with adjacent transposition), same link-error cut (0.8), text-level bootstrap.

Also writes the error structure used by the noise model (out/error_model.json) and the per-text alignments
(out/alignments.json) used to build the consensus and ICIT-reading corpora.

    .venv/bin/python -I experiments/consensus_corpus/disagree.py
"""
import sys, json, random
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "audit_followups"))
import b_editor_agreement as B  # noqa
from cooc import matched_pairs  # noqa
from corpus.load import m77_texts  # noqa

BOOT = 2000


def load_maps():
    c = json.load(open(HERE / "out" / "concordance.json"))
    return dict(original=c["harness_original"], primary=c["primary"],
                provisional={**c["primary"], **c["provisional"]})


def osa_trace(a, b, eq):
    """OSA alignment -> list of ops (kind, m, w): match/sub/sub_unmapped/m77_extra/icit_extra/transpose."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = 0 if eq(a[i - 1], b[j - 1]) else 1
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + c)
            if i > 1 and j > 1 and eq(a[i - 1], b[j - 2]) and eq(a[i - 2], b[j - 1]) and c:
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
    ops = []; i, j = n, m
    while i or j:
        if i and j:
            c = 0 if eq(a[i - 1], b[j - 1]) else 1
            if D[i][j] == D[i - 1][j - 1] + c:
                k = "match" if not c else ("sub_unmapped" if a[i - 1][1] is None else "sub")
                ops.append((k, a[i - 1][0], b[j - 1][0], i - 1)); i -= 1; j -= 1; continue
            if i > 1 and j > 1 and eq(a[i - 1], b[j - 2]) and eq(a[i - 2], b[j - 1]) and D[i][j] == D[i - 2][j - 2] + 1:
                ops.append(("transpose", (a[i - 2][0], a[i - 1][0]), (b[j - 2][0], b[j - 1][0]), i - 2)); i -= 2; j -= 2; continue
        if i and D[i][j] == D[i - 1][j] + 1:
            ops.append(("m77_extra", a[i - 1][0], None, i - 1)); i -= 1; continue
        ops.append(("icit_extra", None, b[j - 1][0], i)); j -= 1
    return D[n][m], ops[::-1]


def merge_doubles(flat_m, flat_i, doubles):
    """R6: M77 writes 'X X' where Wells has one doubled sign Wd. Merge X X into one token 'X+X' -> {Wd}
    only when the ICIT reading contains Wd (so a real two-sign reading is never merged)."""
    out, i = [], 0
    while i < len(flat_m):
        x = flat_m[i]
        if i + 1 < len(flat_m) and flat_m[i + 1] == x and set(doubles.get(x, [])) & set(flat_i):
            out.append(x + "+" + x); i += 2
        else:
            out.append(x); i += 1
    return out


def align_text(mseq, iseq, mp, doubles=None):
    fm = B.flat(mseq)
    if doubles:
        fm = merge_doubles(fm, B.flat(iseq), doubles)
    mp = dict(mp)
    for x, ws in (doubles or {}).items():
        mp[x + "+" + x] = ws
    a = [(s, frozenset(mp[s]) if mp.get(s) else None) for s in fm]
    b = [(s, frozenset([s])) for s in B.flat(iseq)]
    d, ops = osa_trace(a, b, B.eq)
    drev, _ = osa_trace(a[::-1], b, B.eq)
    return d, ops, drev, len(a), len(b)


def rates(rows):
    c = Counter(); tok = 0; rev = 0
    for r in rows:
        tok += r["n_m"]; rev += r["rev_better"]
        for o in r["ops"]: c[o[0]] += 1
    den = tok - c["sub_unmapped"]
    dis = c["sub"] + c["m77_extra"] + c["icit_extra"] + c["transpose"]
    return dict(texts=len(rows), m77_tokens=tok, unmapped=c["sub_unmapped"], compared=den,
                total=dis / den, identity=c["sub"] / den, missing_extra=(c["m77_extra"] + c["icit_extra"]) / den,
                m77_only=c["m77_extra"] / den, icit_only=c["icit_extra"] / den, order=c["transpose"] / den,
                direction_texts=rev / len(rows),
                texts_any=sum(any(o[0] in ("sub", "m77_extra", "icit_extra", "transpose") for o in r["ops"]) for r in rows) / len(rows),
                counts=dict(c))


def boot(rows, keys):
    rng = random.Random(1); vals = defaultdict(list)
    for _ in range(BOOT):
        s = rates([rng.choice(rows) for _ in rows])
        for k in keys: vals[k].append(s[k])
    return {k: [sorted(v)[int(.025 * BOOT)], sorted(v)[int(.975 * BOOT) - 1]] for k, v in vals.items()}


def main():
    maps = load_maps()
    pairs = matched_pairs()
    # R6 detection on a first pass with the primary map: 'X' extra next to 'X'->W substitution
    dbl = Counter()
    for p, mt, it in pairs:
        _, o, _, _, _ = align_text(mt["seq"], it["seq"], maps["primary"])
        for x, y in zip(o, o[1:]):
            for e, s_ in ((x, y), (y, x)):
                if e[0] == "m77_extra" and s_[0] == "sub" and s_[1] == e[1]:
                    dbl[(e[1], s_[2])] += 1
    dprim, dprov = defaultdict(list), defaultdict(list)
    for (m, w), c in dbl.items():
        (dprim if c >= 2 else dprov)[m].append(w)
    for m in list(dprim):
        dprov[m] = sorted(set(dprov[m]) | set(dprim[m]))
    conc = json.load(open(HERE / "out" / "concordance.json"))
    conc["doubles_primary"] = dict(dprim)
    conc["doubles_provisional"] = dict(dprov)
    conc["doubles_evidence"] = {f"{m}+{m}->{w}": c for (m, w), c in dbl.items()}
    json.dump(conc, open(HERE / "out" / "concordance.json", "w"), indent=1)
    DBL = dict(original=None, primary=dict(dprim), provisional=dict(dprov))
    res = {}; per_map_rows = {}
    for name, mp in maps.items():
        rows = []
        for p, mt, it in pairs:
            d, ops, drev, na, nb = align_text(mt["seq"], it["seq"], mp, DBL[name])
            rows.append(dict(text_no=mt["text_no"], side=mt["side"], icit=it["id"], n_m=na, n_i=nb, ops=ops,
                             rev_better=drev < d, dist=d))
        per_map_rows[name] = rows
        r = rates(rows)
        r["ci95"] = boot(rows, ["total", "identity", "missing_extra", "order", "direction_texts", "texts_any"])
        res[name] = r
        print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ("counts",)})
    # top-20 sign pairs (primary map)
    rows = per_map_rows["primary"]
    P = Counter()
    for r in rows:
        for k, m, w, _ in r["ops"]:
            if k == "sub": P[("identity", m, w)] += 1
            elif k == "m77_extra": P[("missing_extra", m, "-")] += 1
            elif k == "icit_extra": P[("missing_extra", "-", w)] += 1
            elif k == "transpose": P[("order", "+".join(m), "+".join(w))] += 1
    den = res["primary"]["compared"]; ndis = sum(P.values())
    top = []; cum = 0
    for (k, m, w), c in P.most_common(20):
        cum += c
        top.append(dict(kind=k, m77=m, icit=w, count=c, share_of_disagreement=round(c / ndis, 4), cum_share=round(cum / ndis, 4)))
    res["top20"] = top
    res["n_disagreements_primary"] = ndis
    # error structure for the noise model (primary map)
    sub_by_m = defaultdict(Counter); n_by_m = Counter(); ins = Counter(); dele = Counter()
    pos_del = Counter(); pos_ins = Counter(); trans = 0
    for r in rows:
        L = r["n_m"]
        for k, m, w, i in r["ops"]:
            if k in ("match", "sub", "m77_extra"): n_by_m[m] += 1
            if k == "transpose": n_by_m[m[0]] += 1; n_by_m[m[1]] += 1; trans += 1
            if k == "sub": sub_by_m[m][w] += 1
            if k == "m77_extra":
                dele[m] += 1; pos_del["initial" if i == 0 else "final" if i == L - 1 else "medial"] += 1
            if k == "icit_extra":
                ins[w] += 1; pos_ins["initial" if i == 0 else "final" if i == L else "medial"] += 1
    em = dict(rates={k: res["primary"][k] for k in ("identity", "m77_only", "icit_only", "order", "direction_texts")},
              ci95=res["primary"]["ci95"],
              sub_by_m={m: dict(c) for m, c in sub_by_m.items()}, n_by_m=dict(n_by_m),
              deleted_by_m=dict(dele), inserted_w=dict(ins), pos_del=dict(pos_del), pos_ins=dict(pos_ins),
              n_texts=len(rows), mean_len=sum(r["n_m"] for r in rows) / len(rows))
    json.dump(em, open(HERE / "out" / "error_model.json", "w"), indent=1)
    json.dump({k: [dict(r, ops=[list(o) for o in r["ops"]]) for r in v] for k, v in per_map_rows.items()},
              open(HERE / "out" / "alignments.json", "w"))
    json.dump(res, open(HERE / "out" / "disagreement.json", "w"), indent=1)
    for t in top: print(t)
    print("pos_del", dict(pos_del), "pos_ins", dict(pos_ins))


if __name__ == "__main__":
    main()
