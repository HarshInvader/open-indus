"""Exp 3. Morphology INSIDE signs: do compound-looking signs behave like
'base sign + modifier'? (NLP morphology induction / Morfessor idea and the
word-embedding analogy test, applied to graphemes; cf. Chinese radicals,
Egyptian determinatives, Sumerian gunu/sheshig sign derivation.)

Families are my reading of Mahadevan's drawings (data/sign_images):
  ENCLOSURE  X -> X between ticks/bars/parentheses (M59->M60, M1->M2 ...)
  ROOF       X -> X under a chevron (M59->M65, M89->M92 ...)
  JAR/CUP+STROKES  M342->M343/344/345, M328->M329/330
  FISH MARKS M59 -> M67 (fins), M70 (inner stroke), M72 (diagonal), M74
  EARS       M328 (cup) -> M342 (jar = cup with side flaps)

Tests (dev; replicated on held-out + external sites where counts allow)
 T1 distributional similarity base~derived (PPMI context cosine) vs
    frequency-matched random partners;
 T2 minimal-pair substitution base<->derived in identical frames;
 T3 modifier consistency: are offset vectors v(derived)-v(base) aligned
    within a modifier class (analogy test)?
 T4 positional shift consistency (sign test across pairs);
 T5 ligature = sequence?  context of jar/cup+strokes vs the bigram
    'strokes + jar/cup' and 'jar/cup + strokes'.
"""
from itertools import combinations

from common import *

FAM = {
    "enclosure": [("M1", "M2"), ("M8", "M9"), ("M25", "M26"), ("M59", "M60"), ("M65", "M66"),
                  ("M67", "M68"), ("M70", "M71"), ("M72", "M73"), ("M110", "M111"), ("M141", "M143"),
                  ("M141", "M144"), ("M155", "M156"), ("M162", "M164"), ("M178", "M179"),
                  ("M206", "M207"), ("M219", "M220"), ("M249", "M250"), ("M280", "M281"),
                  ("M287", "M289"), ("M307", "M308"), ("M387", "M388"), ("M389", "M390"),
                  ("M391", "M392"), ("M403", "M404")],
    "roof": [("M59", "M65"), ("M60", "M66"), ("M89", "M92"), ("M137", "M138"), ("M162", "M163")],
    "inner_strokes": [("M342", "M343"), ("M342", "M344"), ("M342", "M345"), ("M328", "M329"), ("M328", "M330")],
    "fish_marks": [("M59", "M67"), ("M59", "M70"), ("M59", "M72"), ("M59", "M74")],
    "ears": [("M328", "M342")],
}
MINF = 3


def context_matrix(texts):
    feats = defaultdict(Counter)
    for t in texts:
        tt = ("<s>",) + t + ("</s>",)
        for i in range(1, len(tt) - 1):
            feats[tt[i]]["L:" + tt[i - 1]] += 1
            feats[tt[i]]["R:" + tt[i + 1]] += 1
    return feats


def ppmi(feats, signs):
    cols = sorted({c for s in signs for c in feats[s]})
    ci = {c: k for k, c in enumerate(cols)}
    M = np.zeros((len(signs), len(cols)))
    for r, s in enumerate(signs):
        for c, v in feats[s].items():
            M[r, ci[c]] = v
    tot = M.sum()
    pr = M.sum(1, keepdims=True) / tot
    pc = (M.sum(0, keepdims=True) / tot) ** 0.75
    pc /= pc.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.log((M / tot) / (pr * pc))
    P[~np.isfinite(P)] = 0
    P = np.maximum(P, 0)
    return P


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else 0.0


def posprof(texts):
    c = defaultdict(Counter)
    for t in texts:
        for i, s in enumerate(t):
            c[s]["first" if i == 0 else ("last" if i == len(t) - 1 else "mid")] += 1
    return c


def subs_pairs(texts):
    frames = defaultdict(list)
    for t in texts:
        if len(t) < 2:
            continue
        for p in range(len(t)):
            frames[(t[:p], t[p + 1:])].append(t[p])
    c = Counter()
    for v in frames.values():
        for a, b in combinations(set(v), 2):
            c[tuple(sorted((a, b)))] += 1
    return c


def analyse(texts, rng, tag, nnull=2000):
    freq = Counter(s for t in texts for s in t)
    signs = sorted(s for s in freq if freq[s] >= MINF)
    si = {s: k for k, s in enumerate(signs)}
    P = ppmi(context_matrix(texts), signs)
    # SVD embedding for offsets
    U, S, Vt = np.linalg.svd(P, full_matrices=False)
    E = U[:, :40] * S[:40]
    fr = np.array([freq[s] for s in signs], float)
    sp = subs_pairs(texts)
    pp = posprof(texts)
    out = {"pairs": [], "family": {}}
    allcos = []

    def matched(f):
        cand = np.where((fr >= f / 2) & (fr <= f * 2))[0]
        return cand

    for fam, pairs in FAM.items():
        rows = []
        for b, d in pairs:
            row = dict(base=b, derived=d, f_base=freq[b], f_der=freq[d],
                       substitutions=sp.get(tuple(sorted((b, d))), 0))
            for s, key in ((b, "base"), (d, "der")):
                n = sum(pp[s].values()) or 1
                row["pos_" + key] = {k: round(pp[s][k] / n, 2) for k in ("first", "mid", "last")}
            if b in si and d in si:
                obs = cos(P[si[b]], P[si[d]])
                cand = [k for k in matched(freq[d]) if signs[k] not in (b, d)]
                nulls = np.array([cos(P[si[b]], P[k]) for k in cand])
                row["cos"] = round(obs, 3)
                row["cos_null_mean"] = round(float(nulls.mean()), 3)
                row["p_cos"] = round(float((1 + (nulls >= obs).sum()) / (1 + len(nulls))), 4)
                # substitution null: mean substitution count of base with matched partners
                row["subs_null_mean"] = round(float(np.mean([sp.get(tuple(sorted((b, signs[k]))), 0) for k in cand])), 2)
            rows.append(row)
        out["pairs"] += [dict(family=fam, **r) for r in rows]
        tested = [r for r in rows if "cos" in r]
        # T3 offset consistency
        offs = [(si[r["base"]], si[r["derived"]]) for r in tested]
        def mean_pair_cos(vecs):
            vecs = [v / np.linalg.norm(v) for v in vecs if np.linalg.norm(v) > 0]
            return float(np.mean([a @ b for a, b in combinations(vecs, 2)])) if len(vecs) > 1 else np.nan
        obs_off = mean_pair_cos([E[d] - E[b] for b, d in offs])
        null_off = []
        for _ in range(nnull // 4):
            vv = []
            for b, d in offs:
                cand = matched(fr[d]); k = rng.choice(cand)
                vv.append(E[k] - E[b])
            null_off.append(mean_pair_cos(vv))
        null_off = np.array(null_off)
        # T4 positional shift sign test (derived minus base share initial / final)
        dfirst = [r["pos_der"]["first"] - r["pos_base"]["first"] for r in rows if r["f_der"] >= MINF and r["f_base"] >= MINF]
        dlast = [r["pos_der"]["last"] - r["pos_base"]["last"] for r in rows if r["f_der"] >= MINF and r["f_base"] >= MINF]
        from scipy.stats import binomtest, combine_pvalues
        def st(x):
            pos = sum(v > 0 for v in x); neg = sum(v < 0 for v in x)
            return dict(up=pos, down=neg, p=round(binomtest(pos, pos + neg).pvalue, 4) if pos + neg else None)
        out["family"][fam] = dict(
            n_tested=len(tested),
            median_cos=float(np.median([r["cos"] for r in tested])) if tested else None,
            fisher_p_cos=float(combine_pvalues([r["p_cos"] for r in tested])[1]) if tested else None,
            n_p05=sum(r["p_cos"] < 0.05 for r in tested),
            subs_obs=int(sum(r["substitutions"] for r in tested)),
            subs_null=float(sum(r["subs_null_mean"] for r in tested)),
            offset_consistency=obs_off,
            offset_null=(float(np.nanmean(null_off)), float(np.nanstd(null_off))),
            p_offset=float((1 + (null_off >= obs_off).sum()) / (1 + len(null_off))) if len(offs) > 1 else None,
            shift_first=st(dfirst), shift_last=st(dlast))
    # T5 ligature vs sequence (jar/cup + strokes)
    lig = [("M343", "M342", "M97"), ("M343", "M342", "M98"), ("M344", "M342", "M99"), ("M345", "M342", "M102"),
           ("M329", "M328", "M102"), ("M330", "M328", "M104")]
    bif = context_matrix([])
    big = defaultdict(Counter)
    for t in texts:
        tt = ("<s>",) + t + ("</s>",)
        for i in range(1, len(tt) - 2):
            key = tt[i] + "+" + tt[i + 1]
            big[key]["L:" + tt[i - 1]] += 1
            big[key]["R:" + tt[i + 2]] += 1
    out["ligature"] = []
    feats = context_matrix(texts)
    allkeys = signs + [k for k, v in big.items() if sum(v.values()) >= 2 * MINF]
    comb = {**{s: feats[s] for s in signs}, **{k: big[k] for k in allkeys if "+" in k}}
    P2 = ppmi(comb, allkeys)
    ki = {k: n for n, k in enumerate(allkeys)}
    bigkeys = [k for k in allkeys if "+" in k]
    for L, J, S in lig:
        for order in (S + "+" + J, J + "+" + S):
            if L in ki and order in ki:
                obs = cos(P2[ki[L]], P2[ki[order]])
                nl = np.array([cos(P2[ki[L]], P2[ki[k]]) for k in bigkeys if k != order])
                out["ligature"].append(dict(ligature=L, sequence=order, n_seq=sum(big[order].values()) // 2,
                                            cos=round(obs, 3), null_mean=round(float(nl.mean()), 3),
                                            p=round(float((1 + (nl >= obs).sum()) / (1 + len(nl))), 4)))
            else:
                out["ligature"].append(dict(ligature=L, sequence=order, n_seq=sum(big[order].values()) // 2 if order in big else 0, cos=None))
    # T6 enclosure -> text-final? pooled final share of enclosed signs vs their
    # bases and vs frequency-matched random sign sets (texts of length >= 2)
    lastc, totc = Counter(), Counter()
    for t in texts:
        if len(t) < 2:
            continue
        for i, s in enumerate(t):
            totc[s] += 1; lastc[s] += i == len(t) - 1
    allsg = [s for s in totc]
    fra = np.array([totc[s] for s in allsg], float)
    def t6(pairs, label):
        ders = sorted({d for b, d in pairs if totc[d] > 0})
        bases = sorted({b for b, d in pairs})
        n = sum(totc[d] for d in ders); k = sum(lastc[d] for d in ders)
        kb = sum(lastc[b] for b in bases); nb = sum(totc[b] for b in bases)
        null = []
        for _ in range(nnull):
            kk = nn = 0
            for d in ders:
                f = totc[d]
                cand = np.where((fra >= max(1, f / 2)) & (fra <= max(2, f * 2)))[0]
                r = allsg[rng.choice(cand)]
                kk += lastc[r]; nn += totc[r]
            null.append(kk / nn)
        null = np.array(null)
        return dict(label=label, n_signs=len(ders), tokens=n, final_share=round(k / n, 3) if n else None,
                    base_final_share=round(kb / nb, 3) if nb else None,
                    null_final_share=(round(float(null.mean()), 3), round(float(null.std()), 3)),
                    p=float((1 + (null >= (k / n if n else 1)).sum()) / (1 + nnull)))
    fish_enc = [("M59", "M60"), ("M65", "M66"), ("M67", "M68"), ("M70", "M71"), ("M72", "M73")]
    other_enc = [p for p in FAM["enclosure"] if p not in fish_enc]
    out["enclosure_final"] = [t6(fish_enc, "enclosed fish"), t6(other_enc, "other enclosed signs"),
                              t6(FAM["enclosure"], "all enclosed signs")]
    for r in out["enclosure_final"]:
        print("T6", r)
    print("\n==", tag)
    for fam, v in out["family"].items():
        print(fam, v)
    for r in out["pairs"]:
        print({k: r[k] for k in r if k in ("family", "base", "derived", "f_base", "f_der", "cos", "cos_null_mean", "p_cos", "substitutions", "subs_null_mean", "pos_base", "pos_der")})
    for r in out["ligature"]:
        print(r)
    return out


def main():
    rng = np.random.default_rng(3)
    D, H = load_split()
    E, _ = icit_external()
    res = {"dev": analyse(D, rng, "DEV")}
    # replication: held-out + external texts (small; only frequent pairs testable)
    T = sorted(set(H) | (set(E) - set(D)))
    res["test"] = analyse(T, rng, "HELD-OUT + EXTERNAL", nnull=800)
    # full corpus for descriptive power (reported separately; NOT used for claims)
    save_json("exp3_sign_morphology", res)


if __name__ == "__main__":
    main()
