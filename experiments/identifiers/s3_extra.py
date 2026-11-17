"""S3 follow-ups (after the prereg run): bootstrap CI of the pooled cross-site ratio R (P3) for Indus seals
and the Ur III reference; exploratory: which seal texts repeat (length, cross-site), and a two-part
mixture reading (shared short labels + unique combinations).

usage: .venv/bin/python experiments/identifiers/s3_extra.py
"""
import sys, json
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from id_lib import *  # noqa

rng = np.random.default_rng(3)


def cov_samples(ab, B, seed=0):
    """Chao et al. 2014 augmented-multinomial bootstrap samples of coverage (as in id_lib.boot_ci)."""
    import math
    r = np.random.default_rng(seed)
    x, f = freq_counts(ab); n = int(x.sum()); S = len(x)
    f0 = int(math.ceil(chao1(ab) - S)); Cn = coverage(ab)
    w = np.sum(x / n * (1 - x / n) ** n); lam = (1 - Cn) / w if w > 0 else 0
    pr = x / n * (1 - lam * (1 - x / n) ** n)
    if f0 > 0: pr = np.concatenate([pr, np.full(f0, (1 - Cn) / f0)])
    pr = np.clip(pr, 0, None); pr /= pr.sum()
    return np.array([coverage(y[y > 0]) for y in (r.multinomial(n, pr) for _ in range(B))])


def pooled_R(S, pairs, B=1000):
    """Pooled R = sum hits / sum (C_ref * n_tgt). CI: targets resampled with replacement (hits), reference
    coverage drawn from its Chao bootstrap (resampling reference objects would create fake repeats)."""
    refs = {r for _, r in pairs}
    C = {r: coverage(list(Counter(S[r]).values())) for r in refs}
    Cs = {r: cov_samples(list(Counter(S[r]).values()), B, seed=i) for i, r in enumerate(sorted(refs))}
    hit = {(t, r): np.array([x in set(S[r]) for x in S[t]], float) for t, r in pairs}
    obs = sum(hit[k].sum() for k in pairs) / sum(C[r] * len(S[t]) for t, r in pairs)
    vals = []
    for b in range(B):
        o = p = 0.0
        for t, r in pairs:
            h = hit[(t, r)]; o += h[rng.integers(0, len(h), len(h))].sum(); p += Cs[r][b] * len(h)
        vals.append(o / p)
    return obs, np.percentile(vals, [2.5, 97.5]).tolist()


def main():
    out = {}
    I = [o for o in icit_objects() if o["complete"] and o["cls"] == "seal"]
    by = defaultdict(list)
    for o in I: by[o["site"]].append(o)
    tg = ["Harappa", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira"]
    for kind, f in (("text", lambda o: o["sp"]), ("core", lambda o: core_key(flat(o["sp"]))),
                    ("frame", lambda o: frame_key(flat(o["sp"])))):
        S = {s: [f(o) for o in by[s]] for s in tg + ["Mohenjo-daro"]}
        pairs_md = [(t, "Mohenjo-daro") for t in tg]
        pairs_all = pairs_md + [(t, "Harappa") for t in ["Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira"]]
        r1 = pooled_R(S, pairs_md, B=500); r2 = pooled_R(S, pairs_all, B=500)
        out[f"indus_{kind}"] = {"R_vs_MD": r1, "R_all": r2}
        print("Indus", kind, "R vs MD %.2f CI %.2f-%.2f" % (r1[0], *r1[1]), "| R all %.2f CI %.2f-%.2f" % (r2[0], *r2[1]))
    # Ur III reference
    U = [json.loads(l) for l in open(OUT / "data/ur3_occ.jsonl")]
    provs = [p for p, c in Counter(u["prov"] for u in U).most_common() if c >= 100 and p != "uncertain"]
    KINGS = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}szul-gi", "{d}i-bi2-{d}suen", "ur-{d}namma", "{d}szul-gi-ra"}
    royal = lambda lg: any(w in KINGS or w == "lugal" for l in lg for w in l)
    seals = {p: {} for p in provs}
    for u in U:
        if u["prov"] in seals and u["seal_id"]:
            seals[u["prov"]][u["seal_id"].split()[0].split(".")[0]] = u["legend"]
    pairs = [(a, b) for a in provs for b in provs if a != b]
    for lvl, f in (("seal", lambda v: json.dumps(v)), ("name", lambda v: json.dumps(v[0]))):
        S = {p: [f(v) for v in seals[p].values() if lvl == "seal" or not royal(v)] for p in provs}
        r = pooled_R(S, pairs, B=200)
        out[f"ur3_{lvl}"] = {"R_all": r}
        print("UrIII", lvl, "R %.2f CI %.2f-%.2f" % (r[0], *r[1]))
    # ---- exploratory: what repeats among seals (ICIT, all sites)
    texts = [flat(o["sp"]) for o in I]
    c = Counter(texts); sites_of = defaultdict(set)
    for o in I: sites_of[flat(o["sp"])].add(o["site"])
    L = Counter(len(t) for t in texts)
    rep = {t: n for t, n in c.items() if n > 1}
    print("ICIT seals: objects", len(texts), "distinct", len(c), "repeated texts", len(rep), "objects on repeated texts", sum(rep.values()))
    rows = []
    for k in range(1, 9):
        objs = [t for t in texts if len(t) == k]
        if not objs: continue
        ab = list(Counter(objs).values())
        nrep = sum(n for t, n in Counter(objs).items() if n > 1)
        multi = sum(1 for t in set(objs) if c[t] > 1 and len(sites_of[t]) > 1)
        rows.append(dict(length=k, objects=len(objs), share_on_repeated=nrep / len(objs), new_rate=1 - coverage(ab),
                         repeated_multisite=multi, repeated=sum(1 for t in set(objs) if c[t] > 1)))
        print(rows[-1])
    out["by_length"] = rows
    top = sorted(rep.items(), key=lambda x: -x[1])[:15]
    out["top_repeated"] = [(" ".join(t), n, sorted(sites_of[t])) for t, n in top]
    for t, n, s in out["top_repeated"]: print(n, t, s)
    # share of repeated seal texts found at >1 site vs a null where duplicates are assigned sites at random
    multi_obs = np.mean([len(sites_of[t]) > 1 for t in rep])
    site_list = [o["site"] for o in I]; sims = []
    for _ in range(2000):
        perm = rng.permutation(site_list); ss = defaultdict(set)
        for t, s in zip(texts, perm): ss[t].add(s)
        sims.append(np.mean([len(ss[t]) > 1 for t in rep]))
    out["repeated_multisite"] = dict(obs=float(multi_obs), null_mean=float(np.mean(sims)),
                                     p_local=float((1 + np.sum(np.array(sims) <= multi_obs)) / 2001))
    print("repeated seal texts found at >1 site:", out["repeated_multisite"])
    # ---- exploratory: matched-sample coverage (m = 100 objects) of Indus seal text/core/frame vs Ur III
    m = 100; mc = []
    for site in ["Mohenjo-daro", "Harappa", "Dholavira", "Lothal", "Kalibangan", "Chanhu-daro"]:
        X = by[site]
        if len(X) < m: continue
        for kind, f in (("text", lambda o: o["sp"]), ("core", lambda o: core_key(flat(o["sp"]))),
                        ("frame", lambda o: frame_key(flat(o["sp"])))):
            mc.append(dict(ref="Indus", site=site, kind=kind, n=len(X), new_rate_m=1 - coverage(list(Counter(f(o) for o in X).values()), m)))
    for p in provs:
        V = list(seals[p].values())
        if len(V) < m: continue
        mc.append(dict(ref="UrIII", site=p, kind="legend", n=len(V), new_rate_m=1 - coverage(list(Counter(json.dumps(v) for v in V).values()), m)))
        W = [v for v in V if not royal(v)]
        mc.append(dict(ref="UrIII", site=p, kind="name line", n=len(W), new_rate_m=1 - coverage(list(Counter(json.dumps(v[0]) for v in W).values()), m)))
    for r in mc: print("matched m=100", r)
    out["matched_m100"] = mc
    json.dump(out, open(OUT / "s3_extra.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
