"""Claim 8 (structure): L-to-R labelled lines follow the R-to-L grammar when read as labelled
(89%; 84% jar-free). Attacks:
  a. how far does the agreement survive when ALL strongly positional signs (the cues a transcriber
     could have used to decide direction) are deleted, not just the jar?
  b. is the signal carried by short lines (2-3 signs, where it can only be positional)?
  c. ICIT vs M77: are the ICIT L/R labels an independent judgement? Overlap of L-R sequences.
Own implementation: KN bigram trained on distinct R-L lines (75%), score each L-R line as labelled
vs reversed."""
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import binomtest
from rt_common import m77_lines, icit, KN, save

rng = np.random.default_rng(8)


def lines_m77():
    rl, lr, seen = [], [], set()
    for l in m77_lines():
        if l["direction"] not in ("right-to-left", "left-to-right"): continue
        for seg in l["segments"]:
            s = tuple(seg)
            if len(s) < 2: continue
            k = (l["direction"], s)
            if k in seen: continue
            seen.add(k)
            (rl if l["direction"] == "right-to-left" else lr).append(s)
    return rl, lr


def lines_icit():
    rl, lr, seen = [], [], set()
    for t in icit():
        d = t["direction"]
        if d not in ("R/L", "L/R"): continue
        for seg in t["segments"]:
            s = tuple(seg)
            if len(s) < 2: continue
            k = (d, s)
            if k in seen: continue
            seen.add(k)
            (rl if d == "R/L" else lr).append(s)
    return rl, lr


def test(rl, lr, drop):
    rl2 = [tuple(x for x in s if x not in drop) for s in rl]
    lr2 = [tuple(x for x in s if x not in drop) for s in lr]
    rl2 = [s for s in rl2 if len(s) >= 2]; lr2 = [s for s in lr2 if len(s) >= 2]
    idx = rng.permutation(len(rl2)); cut = int(.75 * len(rl2))
    tr = [rl2[i] for i in idx[:cut]]; te = [rl2[i] for i in idx[cut:]]
    m = KN(tr)
    def acc(S):
        r = [m.bits(s) < m.bits(s[::-1]) for s in S if s != s[::-1]]
        return sum(r), len(r)
    a, n = acc(te); b, k = acc(lr2)
    bylen = defaultdict(lambda: [0, 0])
    for s in lr2:
        if s == s[::-1]: continue
        g = "2" if len(s) == 2 else "3" if len(s) == 3 else "4+"
        bylen[g][0] += m.bits(s) < m.bits(s[::-1]); bylen[g][1] += 1
    return dict(rl_heldout=f"{a}/{n}={a/n:.2f}", lr_as_labelled=f"{b}/{k}={b/k:.2f}",
                p=binomtest(b, k, .5, alternative="greater").pvalue, lr_by_len={g: f"{x}/{y}" for g, (x, y) in bylen.items()})


def positional(rl, top):
    c = defaultdict(lambda: [0, 0, 0])
    for s in rl:
        for i, x in enumerate(s):
            c[x][0] += 1; c[x][1] += i == 0; c[x][2] += i == len(s) - 1
    sk = sorted([(max(v[1], v[2]) / v[0], x) for x, v in c.items() if v[0] >= 20], reverse=True)
    return {x for _, x in sk[:top]}


def main():
    res = {}
    for name, (rl, lr) in (("M77", lines_m77()), ("ICIT", lines_icit())):
        jar = {"M342"} if name == "M77" else {"W740"}
        R = {"n_rl": len(rl), "n_lr": len(lr), "none": test(rl, lr, set()), "jar": test(rl, lr, jar)}
        for top in (10, 20, 40):
            P = positional(rl, top) | jar
            R[f"top{top}_positional_removed"] = test(rl, lr, P)
        res[name] = R
        for k, v in R.items(): print(name, k, v)
    res["note"] = "ICIT and M77 transcribe largely the same objects; agreement between them is not an independent replication."
    save("r8_direction", res)


main()


def leak_check():
    from rt_common import edit1
    out = {}
    for name, (rl, lr) in (("M77", lines_m77()), ("ICIT", lines_icit())):
        rls = set(rl)
        exact = [s for s in lr if s in rls]
        near = [s for s in lr if s not in rls and any(edit1(s, r) for r in rl if abs(len(r) - len(s)) <= 1)]
        clean = [s for s in lr if s not in rls and s not in set(near)]
        # rerun with leaked lines removed, R-L training excludes nothing else
        R = {"lr_exact_in_rl": len(exact), "lr_ed1_in_rl": len(near), "lr_clean": len(clean),
             "clean_none": test(rl, clean, set()),
             "clean_top20_removed": test(rl, clean, positional(rl, 20) | ({"M342"} if name == "M77" else {"W740"}))}
        out[name] = R
        print(name, R)
    save("r8_direction_leak", out)


leak_check()
