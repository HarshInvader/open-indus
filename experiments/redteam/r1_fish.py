"""Claim 1 (novel_methods): bracketed ('ticked') fish move to text-final position.
Independent re-run on full ICIT in native Wells numbering (no bridge) plus M77.
Wells codes identified by rendering the lipi font (img/wells_fish.png) and checked
against Mahadevan drawings (img/m_fish.png): the 'brackets' are four corner ticks.
  W226 = M60 (plain fish + ticks)      base W220 = M59
  W232 = M71 (stroke fish + ticks)     base W231 = M70
  W234 = M73 (bar fish + ticks)        base W233 = M72
  W236 = M66 (hat fish + ticks)        base W235 = M65
  W241 = M68 (whisker fish + ticks)    base W240 = M67
  W237 = hatched fish + ticks (no M77 equivalent tested by novel_methods)
"""
import random
from collections import Counter, defaultdict
import numpy as np
from rt_common import icit, m77, flat, distinct_recs, near_dup_clusters, save

rng = random.Random(1)
PAIRS_W = [("W220", "W226"), ("W231", "W232"), ("W233", "W234"), ("W235", "W236"), ("W240", "W241")]
PAIRS_M = [("M59", "M60"), ("M70", "M71"), ("M72", "M73"), ("M65", "M66"), ("M67", "M68")]


def texts_of(recs, filt=lambda r: True):
    out = []
    for r in distinct_recs([r for r in recs if filt(r)]):
        f = flat(r["seq"])
        if f and len(f) >= 2:
            out.append((f, r))
    # distinct flattened sequences
    seen, o2 = set(), []
    for f, r in out:
        if f not in seen:
            seen.add(f); o2.append((f, r))
    return o2


def stats(T, signs):
    n = k = 0; exp = 0.0; prev32 = 0; fin_after_tall2 = 0
    for f, _ in T:
        for i, s in enumerate(f):
            if s in signs:
                n += 1; exp += 1 / len(f)
                last = i == len(f) - 1
                k += last
                if i > 0 and f[i - 1] in ("W032", "M87"):
                    prev32 += 1; fin_after_tall2 += last
    return dict(tokens=n, final=k, share=round(k / n, 3) if n else None,
                shuffle_expect=round(exp / n, 3) if n else None,
                after_tall2=prev32, final_after_tall2=fin_after_tall2)


def freq_null(T, signs, nnull=2000):
    tot, last = Counter(), Counter()
    for f, _ in T:
        for i, s in enumerate(f):
            tot[s] += 1; last[s] += i == len(f) - 1
    allsg = list(tot); fr = np.array([tot[s] for s in allsg])
    ders = [s for s in signs if tot[s]]
    k = sum(last[s] for s in ders); n = sum(tot[s] for s in ders)
    null = []
    for _ in range(nnull):
        kk = nn = 0
        for d in ders:
            c = np.where((fr >= max(1, tot[d] / 2)) & (fr <= max(2, tot[d] * 2)))[0]
            r = allsg[rng.choice(list(c))]
            kk += last[r]; nn += tot[r]
        null.append(kk / nn)
    null = np.array(null)
    return dict(obs=round(k / n, 3) if n else None, null_mean=round(null.mean(), 3),
                null_sd=round(null.std(), 3), p=float((1 + (null >= k / n).sum()) / (1 + nnull)) if n else None)


def cluster_level(T, signs):
    """Collapse edit-distance<=1 families; each family counts once (mean final share
    over its ticked-fish tokens)."""
    rel = [f for f, _ in T if any(s in signs for s in f)]
    cls = near_dup_clusters(rel)
    vals = []
    for c in cls:
        n = k = 0
        for f in c:
            for i, s in enumerate(f):
                if s in signs:
                    n += 1; k += i == len(f) - 1
        vals.append(k / n)
    return dict(texts=len(rel), families=len(cls), mean_final=round(float(np.mean(vals)), 3))


def run(T, pairs, label):
    res = {"n_texts": len(T)}
    ders = [d for _, d in pairs]; bases = [b for b, _ in pairs]
    res["pooled_ticked"] = stats(T, set(ders))
    res["pooled_bases"] = stats(T, set(bases))
    res["freq_null_ticked"] = freq_null(T, ders)
    res["per_pair"] = {f"{b}->{d}": dict(base=stats(T, {b}), ticked=stats(T, {d})) for b, d in pairs}
    first = ders[0]
    res["ticked_without_" + first] = stats(T, set(ders[1:]))
    res["freq_null_without_" + first] = freq_null(T, ders[1:])
    res["cluster_level_ticked"] = cluster_level(T, set(ders))
    res["cluster_level_without_" + first] = cluster_level(T, set(ders[1:]))
    # site split
    bysite = defaultdict(list)
    for f, r in T:
        bysite[r["site"] if r["site"] in ("Harappa", "Mohenjo-daro", "Mohenjodaro") else "other"].append((f, r))
    res["by_site"] = {s: stats(v, set(ders)) for s, v in bysite.items()}
    # what ends texts containing a final ticked fish vs jar
    print("==", label); import json; print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    I = texts_of(icit())
    out = {"icit_native": run(I, PAIRS_W, "ICIT native")}
    # W237 on its own
    out["icit_W237"] = stats(I, {"W237"})
    out["icit_seals_only"] = run(texts_of(icit(), lambda r: r["type"].startswith("SEAL")), PAIRS_W, "ICIT seals")
    M = texts_of(m77())
    out["m77"] = run(M, PAIRS_M, "M77 all")
    # Texts with final ticked fish: do they lack the jar? (claim: fills closer slot)
    fin = [f for f, _ in I if f[-1] in {d for _, d in PAIRS_W} or (len(f) > 1 and f[-1] == "W400" and f[-2] in {d for _, d in PAIRS_W})]
    out["final_ticked_with_jar"] = dict(n=len(fin), with_W740=sum("W740" in f for f in fin))
    # listing of contexts of W226
    ctx = Counter(" ".join(f[max(0, i - 1):i + 2]) for f, _ in I for i, s in enumerate(f) if s == "W226")
    out["W226_top_contexts"] = ctx.most_common(12)
    print(out["final_ticked_with_jar"], out["W226_top_contexts"], out["icit_W237"])
    save("r1_fish", out)
