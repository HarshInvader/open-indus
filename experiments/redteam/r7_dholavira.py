"""Claim 7 (structure): Dholavira-only texts gain less from an M77 bigram (0.71 vs 1.19 bits on 4+ sign
texts) -> regional pairings. The missing selection-effect control: every site's SITE-UNIQUE texts,
scored by a model trained with that site held out, training size equalised.
Native ICIT (no bridge, so no selection by bridge coverage). Seals and all objects."""
from collections import Counter, defaultdict
import numpy as np
from rt_common import icit, KN, Uni, save

rng = np.random.default_rng(11)
SITES = ["Dholavira", "Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"]
NTRAIN = 1800
REPS = 5


def load():
    rows, seen = [], set()
    for t in icit():
        if "#" in t["seq"]: continue
        s = tuple(x for x in t["seq"] if x != "|")
        if not s: continue
        k = (t["site"], s)
        if k in seen: continue
        seen.add(k)
        rows.append(dict(seq=s, site=t["site"], seal=t["type"].startswith("SEAL")))
    return rows


def gain(tr, texts):
    kn = KN(tr); un = Uni(tr, alpha=0.5, vocab=kn.V)
    out = defaultdict(list)
    for t in texts:
        L = len(t)
        if L < 2: continue
        g = (un.bits(t) - kn.bits(t)) / (L + 1)
        out["2" if L == 2 else "3" if L == 3 else "4+"].append(g)
        out["all"].append(g)
    return out


def main():
    rows = load()
    sites_of = defaultdict(set)
    for r in rows: sites_of[r["seq"]].add(r["site"])
    res = {}
    for seals in (False, True):
        tag = "seals" if seals else "all_objects"
        R = {}
        for S in SITES:
            test_all = [r["seq"] for r in rows if r["site"] == S and (r["seal"] or not seals)]
            test_u = [t for t in test_all if len(sites_of[t]) == 1]
            pool = [r["seq"] for r in rows if r["site"] != S]
            acc = {"unique": defaultdict(list), "all": defaultdict(list)}
            for rep in range(REPS):
                tr = [pool[i] for i in rng.choice(len(pool), min(NTRAIN, len(pool)), replace=False)]
                for nm, T in (("unique", test_u), ("all", test_all)):
                    for k, v in gain(tr, T).items(): acc[nm][k].append(np.mean(v) if v else np.nan)
                    acc[nm]["n_" + "x"].append(0)
            R[S] = {nm: {k: round(float(np.nanmean(v)), 3) for k, v in d.items() if not k.startswith("n_")} for nm, d in acc.items()}
            R[S]["n_unique_len2+"] = sum(len(t) >= 2 for t in test_u)
            R[S]["n_unique_len4+"] = sum(len(t) >= 4 for t in test_u)
            R[S]["share_unique"] = round(len(test_u) / max(1, len(test_all)), 3)
            print(tag, S, R[S])
        res[tag] = R
    save("r7_dholavira", res)


main()
