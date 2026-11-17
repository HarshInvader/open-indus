"""Exploratory follow-ups to the pre-registered run (NOT confirmatory).

E1 leave-one-feature-out: does each dev pair survive dropping any single feature?
E2 position-free distances (drop pos, first, last): is the Indus closer a mirrored 'seal of'
   (possessive head at the other end) or like any reference slot once position is ignored?
E3 short-text behaviour: share of 1-2-slot legends that contain each slot (closer vs relators).

usage: .venv/bin/python -I experiments/genre_alignment/ga_explore.py   -> explore.json
"""
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ga_slots as GS
import ga_core as GC
from ga_indus import mean_ref, Z

F = GC.FEATURES


def align_sub(A, B, keep):
    idx = [F.index(f) for f in keep]
    a = sorted(A); b = sorted(B)
    D = np.array([[np.linalg.norm(A[x][idx] - B[y][idx]) / np.sqrt(len(idx)) for y in b] for x in a])
    r, c = linear_sum_assignment(D)
    return {a[i]: (b[j], float(D[i, j])) for i, j in zip(r, c)}, a, b, D


def short_share(texts):
    R = [GC.runs(t) for t in texts]
    sh = [set(s for s, _ in rr) for rr in R if len(rr) <= 2]
    al = [set(s for s, _ in rr) for rr in R]
    labs = {s for x in al for s in x}
    return {s: {"in_short": round(sum(s in x for x in sh) / len(sh), 3),
                "overall": round(sum(s in x for x in al) / len(al), 3)} for s in labs}, len(sh) / len(R)


def main():
    titles, lords = GS.build_lexicons()
    refs = {g: GS.cun_corpus(g, titles, lords) for g in ("ur3", "ob")}
    out = {}
    for split in ("dev", "heldout"):
        I = GS.indus_corpus(split, coarse=True); n = len(I)
        A = Z(GC.fingerprints(I, seed=0))
        for g, T in refs.items():
            B = mean_ref(T, n)
            base, _, _, _ = align_sub(A, B, F)
            lofo = defaultdict(dict)
            for f in F:
                m, _, _, _ = align_sub(A, B, [x for x in F if x != f])
                for x in base: lofo[x][f] = m[x][0]
            surv = {x: sum(lofo[x][f] == base[x][0] for f in F) / len(F) for x in base}
            breakers = {x: [f for f in F if lofo[x][f] != base[x][0]] for x in base}
            nopos = [f for f in F if f not in ("pos", "first", "last")]
            _, a, b, D = align_sub(A, B, nopos)
            near = {x: sorted(zip(b, np.round(D[i], 3).tolist()), key=lambda t: t[1])[:3] for i, x in enumerate(a)}
            out[f"{split}:{g}"] = {"base": base, "lofo_survival": surv, "lofo_breakers": breakers,
                                   "positionfree_nearest": near}
            print(split, g, "LOFO survival", {x: round(v, 2) for x, v in surv.items()})
            print("   position-free nearest CLOSER", near.get("CLOSER"), "OPEN", near.get("OPEN"))
    ss = {}
    for nm, T in (("indus_all", GS.indus_corpus(None, coarse=True)), ("ur3", refs["ur3"]), ("ob", refs["ob"])):
        s, frac = short_share(T); ss[nm] = {"share_of_texts_short": round(frac, 3), "slots": s}
        print(nm, "short-texts share", round(frac, 3), {k: v for k, v in s.items()})
    out["short_texts"] = ss
    json.dump(out, open(HERE / "explore.json", "w"), indent=1)


if __name__ == "__main__":
    main()
