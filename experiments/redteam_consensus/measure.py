"""Red team #38, part A/B/C1-2: independent rebuild of the concordance fixes and of the M77-ICIT disagreement rate.
Own aligner (Needleman-Wunsch with configurable costs), own rule re-derivation, split-half cross-validation.
Pre-registered: docs/prereg/redteam_consensus.md.

    board/run.sh .venv/bin/python -I experiments/redteam_consensus/measure.py
"""
import sys, json, random, itertools, statistics
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness as H  # noqa
from corpus.load import m77_texts, icit_texts  # noqa

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
BRK = ("|", "#")


def flat(s):
    return [x for x in s if x not in BRK]


# ------------------------------------------------------------------ data
def pairs_all():
    d = json.load(open(ROOT / "experiments/audit_followups/out/b_editor_agreement.json"))["pairs"]
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    icit = {t["id"]: t for t in icit_texts()}
    return [(p, m77[(p["text_no"], p["side"])], icit[p["icit"]]) for p in d]


def harness_map():
    V = H.Variant("ICIT")
    return {m: set(ws) for m, ws in V.inv.items() if ws}


def n3_map():
    c = json.load(open(ROOT / "experiments/consensus_corpus/out/concordance.json"))
    return ({m: set(w) for m, w in c["primary"].items() if w}, {m: set(w) for m, w in c["doubles_primary"].items()},
            {m: set(w) for m, w in c["harness_original"].items() if w})


# ------------------------------------------------------------------ aligner
def tokens(mseq, iseq, mp, dbl, mode):
    fm, fi = flat(mseq), flat(iseq)
    out, i = [], 0
    while i < len(fm):
        x = fm[i]
        nxt = i + 1 < len(fm) and fm[i + 1] == x and x in dbl
        if nxt and (mode == "always" or (mode == "cond" and dbl[x] & set(fi))):
            out.append((x + "+" + x, frozenset(dbl[x]), 2)); i += 2
        else:
            out.append((x, frozenset(mp[x]) if x in mp else None, 1)); i += 1
    return out, fi


def nw(a, b, sub=1.0, gap=1.0, swap=1.0, wild_unmapped=False):
    """a: [(label, Wset|None, width)], b: [W]. Returns ops list [(kind, ia, ib)]."""
    n, m = len(a), len(b)
    def same(i, j):
        s = a[i][1]
        return s is not None and b[j] in s
    def cost(i, j):
        if a[i][1] is None:
            return 0.0 if wild_unmapped else sub
        return 0.0 if same(i, j) else sub
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i * gap
    for j in range(m + 1): D[0][j] = j * gap
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            v = min(D[i - 1][j] + gap, D[i][j - 1] + gap, D[i - 1][j - 1] + cost(i - 1, j - 1))
            if swap is not None and i > 1 and j > 1 and same(i - 1, j - 2) and same(i - 2, j - 1) and not same(i - 1, j - 1):
                v = min(v, D[i - 2][j - 2] + swap)
            D[i][j] = v
    ops = []; i, j = n, m; e = 1e-9
    while i or j:
        if i and j and abs(D[i][j] - (D[i - 1][j - 1] + cost(i - 1, j - 1))) < e:
            k = "unmapped" if a[i - 1][1] is None else ("match" if same(i - 1, j - 1) else "sub")
            ops.append((k, i - 1, j - 1)); i -= 1; j -= 1; continue
        if swap is not None and i > 1 and j > 1 and same(i - 1, j - 2) and same(i - 2, j - 1) and not same(i - 1, j - 1) \
                and abs(D[i][j] - (D[i - 2][j - 2] + swap)) < e:
            ops.append(("swap", i - 2, j - 2)); i -= 2; j -= 2; continue
        if i and abs(D[i][j] - (D[i - 1][j] + gap)) < e:
            ops.append(("m_extra" if a[i - 1][1] is not None else "unmapped_extra", i - 1, None)); i -= 1; continue
        ops.append(("i_extra", i, j - 1)); j -= 1
    return ops[::-1]


def count(a, b, ops):
    c = Counter(o[0] for o in ops)
    c["n_m"] = len(a); c["n_i"] = len(b)
    return c


def rate(cs, n3style=False):
    t = Counter()
    for c in cs: t.update(c)
    den = t["n_m"] - t["unmapped"] - (0 if n3style else t["unmapped_extra"])
    dis = t["sub"] + t["m_extra"] + t["i_extra"] + t["swap"] + (t["unmapped_extra"] if n3style else 0)
    return dis / den if den else float("nan"), t


def lcs_rate(a, b):
    """No substitutions: unmatched tokens over both readings. Unmapped M tokens are wildcards (agreement upper bound)."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    W = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            ok = a[i - 1][1] is None or b[j - 1] in a[i - 1][1]
            cands = [(L[i - 1][j], W[i - 1][j]), (L[i][j - 1], W[i][j - 1])]
            if ok: cands.append((L[i - 1][j - 1] + 1, W[i - 1][j - 1] + (a[i - 1][1] is None)))
            L[i][j], W[i][j] = max(cands)
    l, w = L[n][m], W[n][m]
    real = l - w
    return (n + m - 2 * l), (n + m - 2 * w)


def boot(per, fn, B=2000, seed=1):
    r = random.Random(seed); v = []
    for _ in range(B):
        v.append(fn([r.choice(per) for _ in per]))
    v.sort(); return [round(v[int(.025 * B)], 4), round(v[int(.975 * B) - 1], 4)]


def eval_map(pairs, mp, dbl, mode="cond", **kw):
    per = []
    for p, mt, it in pairs:
        a, b = tokens(mt["seq"], it["seq"], mp, dbl, mode)
        per.append(count(a, b, nw(a, b, **kw)))
    return per


# ------------------------------------------------------------------ rules (my reimplementation)
def positional(pairs):
    pos = defaultdict(Counter)
    for p, mt, it in pairs:
        a, b = flat(mt["seq"]), flat(it["seq"])
        if len(a) == len(b):
            for x, y in zip(a, b): pos[x][y] += 1
    return pos


def derive(pairs, base):
    mp = {m: set(w) for m, w in base.items()}
    pos = positional(pairs)
    owner = defaultdict(Counter)
    for m, c in pos.items():
        for w, k in c.items(): owner[w][m] += k
    for m, c in pos.items():
        tot = sum(c.values()); (w1, c1), = c.most_common(1)
        cur = mp.get(m, set())
        if w1 not in cur and c1 >= 3 and c1 / tot >= 2 / 3:
            if not cur or sum(c[w] for w in cur) == 0: mp[m] = {w1}
            else: mp[m] = cur | {w1}
    for m, c in pos.items():
        cur = mp.get(m, set())
        if len(cur) >= 2:
            for w in list(cur):
                if c[w] == 0 and any(k >= 5 for mm, k in owner[w].items() if mm != m) and len(mp[m]) > 1:
                    mp[m].discard(w)
    dbl = defaultdict(Counter)
    for p, mt, it in pairs:
        a, b = tokens(mt["seq"], it["seq"], mp, {}, "never")
        ops = nw(a, b)
        for x, y in zip(ops, ops[1:]):
            for e, s in ((x, y), (y, x)):
                if e[0] == "m_extra" and s[0] == "sub" and a[e[1]][0] == a[s[1]][0]:
                    dbl[a[e[1]][0]][b[s[2]]] += 1
    D = {m: {w for w, k in c.items() if k >= 2} for m, c in dbl.items()}
    return mp, {m: w for m, w in D.items() if w}


def diff(base, mp):
    return {m: (sorted(base.get(m, [])), sorted(mp.get(m, []))) for m in set(base) | set(mp) if base.get(m, set()) != mp.get(m, set())}


# ------------------------------------------------------------------ main
def main():
    res = {}
    P562 = pairs_all()
    P = [x for x in P562 if x[0]["norm"] <= 0.8]
    HM = harness_map(); N3, N3D, N3orig = n3_map()
    res["n_pairs"] = len(P)
    # sanity: N3's harness_original equals harness map on the M signs that occur
    res["harness_map_agrees_with_n3_original"] = sum(1 for m in N3orig if N3orig[m] != HM.get(m, set()))

    # ---------- A1: independent positional evidence for each N3 change
    pos = positional(P)
    A1 = {}
    for m in ["M65", "M67", "M70", "M72", "M59", "M66", "M68", "M71", "M73", "M389", "M387", "M162", "M216", "M175", "M205", "M210"]:
        c = pos.get(m, Counter()); tot = sum(c.values())
        A1[m] = dict(tot=tot, top=c.most_common(4), harness=sorted(HM.get(m, [])), n3=sorted(N3.get(m, [])),
                     n3_count=sum(c[w] for w in N3.get(m, [])), share=round(sum(c[w] for w in N3.get(m, [])) / tot, 3) if tot else None)
    res["A1_positional"] = A1
    # fish block contingency (plain + ticked) on equal-length pairs
    fishM = ["M59", "M65", "M67", "M70", "M72", "M60", "M66", "M68", "M71", "M73"]
    fishW = ["W220", "W226", "W231", "W232", "W233", "W234", "W235", "W236", "W240", "W241"]
    res["A1_fish_table"] = {m: {w: pos.get(m, Counter())[w] for w in fishW if pos.get(m, Counter())[w]} for m in fishM}
    # doubles evidence: M X X with ICIT Wd, and ICIT Wd facing single M X
    dd = Counter()
    for p, mt, it in P:
        fm, fi = flat(mt["seq"]), flat(it["seq"])
        for x, ws in N3D.items():
            nXX = sum(1 for i in range(len(fm) - 1) if fm[i] == x == fm[i + 1])
            nX = fm.count(x)
            hasWd = any(w in ws for w in fi)
            single_W = sum(1 for w in fi if w in N3.get(x, set()))
            if nXX: dd[(x, "XX_with_Wd" if hasWd else "XX_without_Wd")] += 1
            if hasWd and not nXX: dd[(x, "Wd_with_no_XX", "single_X" if nX else "no_X")] += 1
            if nXX and single_W >= 2: dd[(x, "XX_and_ICIT_two_singles")] += 1
    res["A2_doubles_cases"] = {" ".join(k): v for k, v in dd.items()}

    # ---------- headline reproductions (own aligner, OSA-like swap on)
    def R(per): return rate(per)[0]
    cfgs = {
        "harness_map": (HM, {}, "never", {}),
        "n3_map_no_doubles": (N3, {}, "never", {}),
        "n3_primary_v0_swap": (N3, N3D, "cond", {}),
        "v1_levenshtein_noswap": (N3, N3D, "cond", dict(swap=None)),
        "v2_cheap_gaps_0.6": (N3, N3D, "cond", dict(gap=0.6)),
        "v2b_dear_gaps_1.5": (N3, N3D, "cond", dict(gap=1.5)),
        "doubles_always": (N3, N3D, "always", {}),
        "doubles_never": (N3, N3D, "never", {}),
        "harness_map_plus_doubles": (HM, N3D, "cond", {}),
    }
    B = {}
    for k, (mp, dbl, mode, kw) in cfgs.items():
        per = eval_map(P, mp, dbl, mode, **kw)
        r, t = rate(per)
        B[k] = dict(rate=round(r, 4), ci=boot(per, R), rate_n3style=round(rate(per, True)[0], 4), counts={x: t[x] for x in ("n_m", "unmapped", "unmapped_extra", "match", "sub", "m_extra", "i_extra", "swap")},
                    texts_any=round(sum((c["sub"] + c["m_extra"] + c["i_extra"] + c["swap"]) > 0 for c in per) / len(per), 4))
        print(k, B[k]["rate"], B[k]["ci"], flush=True)
    # v3 LCS
    lc = []
    for p, mt, it in P:
        a, b = tokens(mt["seq"], it["seq"], N3, N3D, "cond")
        lc.append(lcs_rate(a, b))
    f = lambda xs: sum(x[0] for x in xs) / sum(x[1] for x in xs)
    B["v3_lcs_both_readings"] = dict(rate=round(f(lc), 4), ci=boot(lc, f))
    # v4 unmapped counted as disagreement
    per = eval_map(P, N3, N3D, "cond")
    t = Counter(); [t.update(c) for c in per]
    v4 = (t["sub"] + t["m_extra"] + t["i_extra"] + t["swap"] + t["unmapped"] + t["unmapped_extra"]) / t["n_m"]
    B["v4_unmapped_as_disagreement"] = dict(rate=round(v4, 4))
    # denominator: both readings
    B["v1b_denominator_mean_length"] = dict(rate=round((t["sub"] + t["m_extra"] + t["i_extra"] + t["swap"]) /
                                                       ((t["n_m"] + t["n_i"]) / 2 - t["unmapped"] - t["unmapped_extra"]), 4))
    # v5 relink under corrected map
    for cut in (0.8, 0.5, 1.0):
        sel = []
        for x in P562:
            p, mt, it = x
            a, b = tokens(mt["seq"], it["seq"], N3, N3D, "cond")
            ops = nw(a, b)
            c = count(a, b, ops)
            d = c["sub"] + c["m_extra"] + c["i_extra"] + c["swap"] + c["unmapped"] + c["unmapped_extra"]
            if d / max(len(a), len(b)) <= cut: sel.append(c)
        r, _ = rate(sel)
        B[f"v5_relink_cut_{cut}"] = dict(n=len(sel), rate=round(r, 4), ci=boot(sel, R))
    # v6 per site / object type
    by = defaultdict(list)
    for (p, mt, it), c in zip(P, per):
        by["site:" + mt["site"]].append(c); by["type:" + mt["object_type"]].append(c)
    B["v6_strata"] = {k: dict(n=len(v), rate=round(rate(v)[0], 4)) for k, v in by.items() if len(v) >= 20}
    res["B_sensitivity"] = B

    # ---------- A2 plain-fish permutation check
    PM = ["M59", "M65", "M67", "M70", "M72"]; PW = ["W220", "W231", "W233", "W235", "W240"]
    perm = []
    for pw in itertools.permutations(PW):
        mp = {m: set(w) for m, w in N3.items()}
        for m, w in zip(PM, pw): mp[m] = {w}
        perm.append((round(R(eval_map(P, mp, N3D, "cond")), 4), dict(zip(PM, pw))))
    perm.sort(key=lambda x: x[0])
    n3p = {m: sorted(N3[m])[0] for m in PM}; hp = {m: sorted(HM[m])[0] if m in HM else None for m in PM}
    res["A2_fish_perm"] = dict(best=perm[:5], worst=perm[-1], n3_rank=[i for i, x in enumerate(perm) if x[1] == n3p],
                               harness_rank=[i for i, x in enumerate(perm) if x[1] == hp], n=len(perm),
                               n3_pairing=n3p, harness_pairing=hp)
    print("fish perm", res["A2_fish_perm"]["best"][:2], res["A2_fish_perm"]["n3_rank"], res["A2_fish_perm"]["harness_rank"], flush=True)

    # ---------- A2 my in-sample rule derivation + split-half cross-validation
    mp_all, d_all = derive(P, HM)
    res["A2_my_rules_all"] = dict(changes={m: v for m, v in diff(HM, mp_all).items()}, doubles={m: sorted(w) for m, w in d_all.items()},
                                  rate=round(R(eval_map(P, mp_all, d_all, "cond")), 4))
    print("my rules in-sample", res["A2_my_rules_all"]["rate"], flush=True)
    rng = random.Random(38); cv = []
    for s in range(200):
        idx = list(range(len(P))); rng.shuffle(idx)
        A = [P[i] for i in idx[:len(P) // 2]]; Bh = [P[i] for i in idx[len(P) // 2:]]
        mA, dA = derive(A, HM); mB, dB = derive(Bh, HM)
        cv.append(dict(oos=R(eval_map(Bh, mA, dA, "cond")), ins=R(eval_map(Bh, mB, dB, "cond")),
                       harness=R(eval_map(Bh, HM, {}, "never")), n3=R(eval_map(Bh, N3, N3D, "cond"))))
        if s % 20 == 0: print("cv", s, {k: round(v, 4) for k, v in cv[-1].items()}, flush=True)
    q = lambda xs: [round(sorted(xs)[int(.025 * len(xs))], 4), round(sorted(xs)[int(.975 * len(xs)) - 1], 4)]
    res["A2_cv"] = {k: dict(mean=round(statistics.mean(x[k] for x in cv), 4), q95=q([x[k] for x in cv])) for k in cv[0]}
    res["A2_cv"]["optimism_mean"] = round(statistics.mean(x["oos"] - x["ins"] for x in cv), 4)
    res["A2_cv"]["n3_minus_oos_mean"] = round(statistics.mean(x["oos"] - x["n3"] for x in cv), 4)

    # ---------- C1 sign-link selection on register pairs
    sel_lo, sel_hi = [], []
    for c in per:
        d = c["sub"] + c["m_extra"] + c["i_extra"] + c["swap"] + c["unmapped"] + c["unmapped_extra"]
        (sel_lo if d / max(c["n_m"], c["n_i"]) <= 0.5 else sel_hi).append(c)
    res["C1_signlink_selection"] = dict(n_le05=len(sel_lo), rate_le05=round(rate(sel_lo)[0], 4),
                                        n_gt05=len(sel_hi), rate_gt05=round(rate(sel_hi)[0], 4))
    # ---------- C2 composition linked vs unlinked (N3's link set)
    seq = json.load(open(ROOT / "experiments/consensus_corpus/out/seq_links.json"))
    linked = {tuple(json.loads(k)) for k in seq} | {(mt["text_no"], mt["side"]) for _, mt, _ in P}
    T = [t for t in m77_texts() if flat(t["seq"])]
    freq = Counter(s for t in T for s in flat(t["seq"]))
    fish = {"M59", "M60", "M65", "M66", "M67", "M68", "M69", "M70", "M71", "M72", "M73"}
    def desc(ts):
        L = [len(flat(t["seq"])) for t in ts]; toks = [s for t in ts for s in flat(t["seq"])]
        return dict(n=len(ts), mean_len=round(statistics.mean(L), 2), rare_share=round(sum(freq[s] < 10 for s in toks) / len(toks), 4),
                    fish_share=round(sum(s in fish for s in toks) / len(toks), 4),
                    sites=dict(Counter(t["site"] for t in ts).most_common(6)), types=dict(Counter(t["object_type"] for t in ts).most_common(5)))
    res["C2_composition"] = dict(linked=desc([t for t in T if (t["text_no"], t["side"]) in linked]),
                                 unlinked=desc([t for t in T if (t["text_no"], t["side"]) not in linked]))
    json.dump(res, open(OUT / "measure.json", "w"), indent=1, default=list)
    print(json.dumps({k: v for k, v in res.items() if k.startswith(("A2_cv", "C", "A2_my"))}, indent=1, default=list))


if __name__ == "__main__":
    main()
