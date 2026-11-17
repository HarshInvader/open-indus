"""Task B confirmatory run (pre-registered: docs/prereg/closer_ownership.md). Fresh refs + Indus held-out v2 + ICIT."""
import json, numpy as np
from co_core import *
rng = np.random.default_rng(20261115)
SD = np.array([0.227, 0.328, 0.524, 0.249, 0.364])
refs = load_refs()
F_ALL = ref_corpus(FRESH, refs); F_STRICT = ref_corpus(STRICT_FRESH, refs)
OB = ref_corpus(("ob",), refs); UR3 = ref_corpus(("ur3",), refs)
print("fresh pool", len(F_ALL), "strict", len(F_STRICT), Counter(c["group"] for c in F_ALL))
print("fresh class tokens", Counter(k for c in F_ALL for k in c["cls"]))
R = {"n": {"fresh": len(F_ALL), "strict": len(F_STRICT)}}
def r2(d): return {k: round(float(v), 3) for k, v in d.items() if k in DEC + REPORT + ["n"]}
REFF = {}
for name, C in (("fresh", F_ALL), ("strict", F_STRICT), ("oakk", ref_corpus(("oakk",), refs)), ("oa", ref_corpus(("oa",), refs)),
                ("mb", ref_corpus(("mb",), refs)), ("ob", OB), ("ur3", UR3)):
    REFF[name] = ref_class_feats(C, rng)
    for k, v in REFF[name].items(): print("%-7s %-8s" % (name, k), r2(v))
R["ref_features"] = {g: {k: r2(v) for k, v in F.items()} for g, F in REFF.items()}

# ---------------- gate
NHO = 418
def g1(A, B, reps=40):
    res = Counter()
    for _ in range(reps):
        Fa = ref_class_feats(subsample(A, NHO, rng), rng); Fb = ref_class_feats(B if len(B) < 1000 else subsample(B, 1000, rng), rng)
        for t in ("SEAL_OF", "SERV"):
            if t in Fa: res[(t, nearest(Fa[t], Fb, SD)[0])] += 1
    return res
def binacc(res, t):
    ok = {"SEAL_OF": ("SEAL_OF", "TITLE"), "SERV": ("SERV",)}[t]
    n = sum(v for (a, b), v in res.items() if a == t); k = sum(v for (a, b), v in res.items() if a == t and b in ok)
    return k / n if n else float("nan"), n
G1 = {}
for lab, A, B in (("ob->fresh", OB, F_ALL), ("fresh->ob", F_ALL, OB)):
    res = g1(A, B); G1[lab] = {t: binacc(res, t) for t in ("SEAL_OF", "SERV")}; G1[lab]["raw"] = {f"{a}->{b}": v for (a, b), v in res.items()}
    print("G1", lab, G1[lab])
cells = [G1[l][t][0] for l in G1 for t in ("SEAL_OF", "SERV")]
g1_pass = np.nanmean(cells) >= 0.75 and np.nanmin(cells) >= 0.5
print("G1 mean", np.nanmean(cells), "min", np.nanmin(cells), "PASS" if g1_pass else "FAIL")

def g2(A, B, reps=20, K=12):
    res = defaultdict(Counter)
    for _ in range(reps):
        a = subsample(A, NHO, rng); Fb = ref_class_feats(B if len(B) < 1000 else subsample(B, 1000, rng), rng)
        top = {w for w, _ in Counter(w for c in a for w in c["tok"]).most_common(K)}
        LR = blind_word_slots(a, None, top)
        gold = defaultdict(Counter)
        for c in a:
            for w, k in zip(c["tok"], c["cls"]): gold[w][k] += 1
        for w in top:
            g = gold[w].most_common(1)[0][0]
            if g not in ("SEAL_OF", "SERV"): continue
            f = feats(LR, "W:" + w, rng)
            if f is None: continue
            res[(w, g)][nearest(f, Fb, SD)[0]] += 1
    return res
G2 = {}; tot = Counter()
for lab, A, B in (("ob->fresh", OB, F_ALL), ("fresh->ob", F_ALL, OB)):
    res = g2(A, B); G2[lab] = {f"{w}|{g}": dict(v) for (w, g), v in res.items()}
    print("G2", lab, G2[lab])
    for (w, g), v in res.items():
        ok = ("SEAL_OF", "TITLE") if g == "SEAL_OF" else ("SERV",)
        tot[(g, "n")] += sum(v.values()); tot[(g, "ok")] += sum(c for k, c in v.items() if k in ok)
acc_k = tot[("SEAL_OF", "ok")] / max(tot[("SEAL_OF", "n")], 1); acc_a = tot[("SERV", "ok")] / max(tot[("SERV", "n")], 1)
pooled = (tot[("SEAL_OF", "ok")] + tot[("SERV", "ok")]) / max(tot[("SEAL_OF", "n")] + tot[("SERV", "n")], 1)
g2_pass = pooled >= 0.75 and acc_k >= 0.5 and acc_a >= 0.5
print("G2 kisib", acc_k, tot[("SEAL_OF", "n")], "arad", acc_a, tot[("SERV", "n")], "pooled", pooled, "PASS" if g2_pass else "FAIL")
R["gate"] = {"G1": G1, "G1_mean": float(np.nanmean(cells)), "G1_min": float(np.nanmin(cells)), "G1_pass": bool(g1_pass),
             "G2": G2, "G2_kisib": acc_k, "G2_arad": acc_a, "G2_pooled": pooled, "G2_n": [tot[("SEAL_OF", "n")], tot[("SERV", "n")]],
             "G2_pass": bool(g2_pass)}

# ---------------- Indus
HO = indus_seals("heldout"); IC = icit_newsite_seals()
print("held-out", len(HO), "icit", len(IC))
R["indus"] = {}
for sname, X in (("heldout", HO), ("icit", IC)):
    for mode in ("set", "jar"):
        f = feats(indus_runs(X, mode), "CLOSER", rng)
        out = {"features": r2(f)}
        for g in ("fresh", "strict", "ob", "ur3"):
            nn, d = nearest(f, REFF[g], SD); out["nearest_" + g] = nn; out["dist_" + g] = {k: round(v, 3) for k, v in d.items()}
        # bootstrap vs fresh pool
        win = Counter(); ownwin = 0; bs = defaultdict(list)
        B = 200 if mode == "set" else 100
        for _ in range(B):
            fb = feats(indus_runs(boot(X, rng), mode), "CLOSER", rng)
            Fb = ref_class_feats(boot(F_ALL, rng), rng)
            nn, d = nearest(fb, Fb, SD); win[nn] += 1
            own = min(d.get("SEAL_OF", 9), d.get("TITLE", 9)); ownwin += own < d.get("SERV", 9)
            for k in ("short", "nameonly", "longdiff"): bs[k].append(fb[k])
        out["boot_nearest_fresh"] = {k: v / B for k, v in win.items()}
        out["boot_own_or_title_beats_serv"] = ownwin / B
        out["ci90"] = {k: [round(float(np.quantile(v, .05)), 3), round(float(np.quantile(v, .95)), 3)] for k, v in bs.items()}
        R["indus"][f"{sname}_{mode}"] = out
        print(sname, mode, json.dumps(out))

# ---------------- predictions
def I(s): return R["indus"][f"{s}_set"]
fs = REFF["fresh"].get("SERV", {})
P = {}
P["P1"] = {s: (I(s)["features"]["short"], I(s)["features"]["short"] >= 0.40) for s in ("heldout", "icit")}
P["P2"] = {s: (I(s)["features"]["nameonly"], I(s)["features"]["nameonly"] >= 0.20) for s in ("heldout", "icit")}
P["P3"] = {s: (I(s)["features"]["longdiff"], I(s)["features"]["longdiff"] <= 0) for s in ("heldout", "icit")}
P["P4"] = {s: (I(s)["boot_own_or_title_beats_serv"], I(s)["boot_own_or_title_beats_serv"] >= 0.80) for s in ("heldout", "icit")}
P["P5"] = {"fresh_SERV_short": fs.get("short"), "fresh_SERV_nameonly": fs.get("nameonly"),
           "pass": bool(fs and fs["short"] <= 0.10 and fs["nameonly"] <= 0.05)}
gate = g1_pass and g2_pass
allp = all(v[1] for k in ("P1", "P2", "P4") for v in P[k].values()) and P["P5"]["pass"]
refuted = all(I(s)["boot_nearest_fresh"].get("SERV", 0) >= 0.8 for s in ("heldout", "icit")) or all(I(s)["features"]["short"] < 0.2 for s in ("heldout", "icit"))
verdict = "untestable (gate failed)" if not gate else ("supported" if allp else ("refuted" if refuted else "inconclusive"))
P["verdict"] = verdict
print(json.dumps(P, indent=1, default=str))
R["predictions"] = P
json.dump(R, open("taskB.json", "w"), indent=1, default=str)
