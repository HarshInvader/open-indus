"""Task A: red team of 'Indus connective M99/M123 aligns with the dumu (son of) slot' (genre_alignment P4).
Independent reimplementation. Three Indus slot definitions:
  R0 grammar slots (functional_reading parse roles, GA coarse mapping)  -> replication
  R1 sign-list slots (OPEN/CONN/CLOSER/POST lists, rest CORE)           -> still lexicon-based
  R2 distributional clustering of signs (dev only; no grammar labels)   -> grammar-free
plus a pseudo-connective null (any frequent sign made its own slot) and grammar-free token profiles.
Run: cd experiments/closer_ownership && ../../.venv/bin/python -I co_taskA.py
"""
import csv, json, sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
sys.path.insert(0, ".")
from co_lib import *

rng = np.random.default_rng(7)
refs = load_refs()
REF = {"ur3": ref_corpus(("ur3",), refs), "ob": ref_corpus(("ob",), refs), "fresh": ref_corpus(FRESH, refs)}
GOLD = ("OWNER", "TITLE", "KIN", "FATHER", "SERV", "LORD", "SEAL_OF")
FP = ["occ", "mpos", "first", "last", "rlen", "types20", "short", "recur", "alone", "longdiff", "edge_s", "top"]
FP_NODEF = ["occ", "mpos", "first", "last", "short", "recur", "alone", "longdiff", "edge_s"]   # drops filler-count features
R = {}


def ref_slot_fp(C, n=None):
    C = C if n is None or len(C) <= n else [C[i] for i in rng.choice(len(C), n, replace=False)]
    LR = [runs_of(c["slot"], c["tok"]) for c in C]
    out = {}
    for s in GOLD:
        f = slot_features(LR, s, rng, name_slot="OWNER")
        if f is not None and f["n"] >= 15: out[s] = f
    return out


def scale(fps, keys):
    X = np.array([[f[k] for k in keys] for F in fps for f in F.values()])
    return X.mean(0), np.maximum(X.std(0), 0.05)


def dmat(A, B, keys, sd):
    a = list(A); b = list(B)
    M = np.array([[np.linalg.norm((np.array([A[x][k] for k in keys]) - np.array([B[y][k] for k in keys])) / sd) / np.sqrt(len(keys))
                   for y in b] for x in a])
    return a, b, M


def hungarian(A, B, keys, sd):
    a, b, M = dmat(A, B, keys, sd)
    r, c = linear_sum_assignment(M)
    return {a[i]: (b[j], float(M[i, j])) for i, j in zip(r, c)}


def nearest_slot(f, B, keys, sd):
    d = {y: float(np.linalg.norm((np.array([f[k] for k in keys]) - np.array([B[y][k] for k in keys])) / sd) / np.sqrt(len(keys))) for y in B}
    return min(d, key=d.get), d


# ------------------------------------------------------------- Indus texts
dev = indus_seals("dev"); ho = indus_seals("heldout"); ic = icit_newsite_seals()
print("dev", len(dev), "ho", len(ho), "icit", len(ic))

# ------------------------------------------------------------- A1 raw grammar-free facts
def raw(texts, S, openers):
    occ = [(i, len(t), t[i - 1] if i else None, t) for t in texts for i in range(len(t)) if t[i] in S]
    n = len(occ)
    return dict(n_occ=n, n_texts=len({id(o[3]) for o in occ}), initial=np.mean([o[0] == 0 for o in occ]),
                final=np.mean([o[0] == o[1] - 1 for o in occ]), in_len_le2=np.mean([o[1] <= 2 for o in occ]),
                in_len_le3=np.mean([o[1] <= 3 for o in occ]), after_opener=np.mean([o[2] in openers for o in occ]),
                distinct_left=len({o[2] for o in occ}), distinct_right=len({o[3][o[0] + 1] if o[0] < o[1] - 1 else None for o in occ}),
                texts_le2_share_corpus=np.mean([len(t) <= 2 for t in texts]))
WOPEN = set(w_sets().get("OPEN", set())); WCONN99 = {w for w, ms in bridge().items() if ms[0] == "M99"}
R["A1_raw"] = {"dev_M99": raw(dev, {"M99"}, OPEN_M), "heldout_M99": raw(ho, {"M99"}, OPEN_M),
               "icit_M99(W%s)" % ",".join(sorted(WCONN99)): raw(ic, WCONN99, WOPEN),
               "dev_M123": raw(dev, {"M123"}, OPEN_M)}
for k, v in R["A1_raw"].items(): print("A1", k, {a: round(float(b), 3) for a, b in v.items()})

# ------------------------------------------------------------- slot definitions
def r0_runs(split):
    out = []
    MAP = {"O": "OPEN", "C": "CONN", "S": "CORE", "T": "CORE", "U": "CORE", "F": "CORE", "N": "CORE", "I": "TITLE",
           "J": "CLOSER", "B": "CLOSER", "P": "POST"}
    seen = set()
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/readings.csv")):
        if r["object_type"] != "seal" or r["split"] != split or "#" in r["signs"]: continue
        toks = [t for t in r["parse_roles"].replace("||", " ").split() if "/" in t]
        sig = [t.split("/")[0].replace("!cut@", "") for t in toks]; rol = [t.split("/")[-1] for t in toks]
        k = " ".join(sig)
        if not sig or k in seen: continue
        seen.add(k); out.append(runs_of([MAP.get(x, "CORE") for x in rol], sig))
    return out


def r1_runs(texts, conn=CONN_M):
    out = []
    for s in texts:
        lab = []
        for x in s:
            k = indus_class(x)
            if x in conn: k = "CONN"
            elif k == "CONN": k = "CORE"
            lab.append(k)
        out.append(runs_of(lab, s))
    return out


# distributional clustering (dev only)
def sign_profiles(texts, min_n=10, top=40):
    cnt = Counter(x for t in texts for x in t)
    ctx = [w for w, _ in cnt.most_common(top)]
    ci = {w: i for i, w in enumerate(ctx)}
    signs = [w for w, n in cnt.items() if n >= min_n]
    P = {}
    for w in signs:
        L = np.zeros(top + 2); Rr = np.zeros(top + 2); pos = []; ini = fin = sh = 0; n = 0
        for t in texts:
            for i, x in enumerate(t):
                if x != w: continue
                n += 1; m = len(t)
                pos.append(i / (m - 1) if m > 1 else 0.5); ini += i == 0; fin += i == m - 1; sh += m <= 3
                l = t[i - 1] if i else "<s>"; r = t[i + 1] if i < m - 1 else "</s>"
                L[ci.get(l, top) if l != "<s>" else top + 1] += 1
                Rr[ci.get(r, top) if r != "</s>" else top + 1] += 1
        P[w] = np.concatenate([[ini / n, fin / n, np.mean(pos), sh / n], L / n, Rr / n])
    return P


def cluster_labels(texts, k, seed):
    P = sign_profiles(texts)
    W = sorted(P); X = np.array([P[w] for w in W])
    pos = X[:, :4] * 3.0                              # position block up-weighted
    svd = TruncatedSVD(n_components=10, random_state=seed).fit_transform(X[:, 4:])
    Z = np.hstack([pos, svd / (svd.std() + 1e-9)])
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(Z)
    return {w: "K%d" % l for w, l in zip(W, km.labels_)}


def r2_runs(texts, lab):
    return [runs_of([lab.get(x, "RARE") for x in s], s) for s in texts]


def indus_slot_fp(LR, min_runs=30):
    labs = Counter(l for r in LR for l, _ in r)
    out = {}
    for s, n in labs.items():
        if n < min_runs: continue
        f = slot_features(LR, s, rng, name_slot=None)
        if f is not None: out[s] = f
    return out


# ------------------------------------------------------------- reference fingerprints at Indus size
REFFP = {g: ref_slot_fp(REF[g], n=len(dev)) for g in ("ur3", "ob")}
SD_FULL = scale(list(REFFP.values()), FP)[1]; SD_NODEF = scale(list(REFFP.values()), FP_NODEF)[1]
for g, F in REFFP.items():
    print(g, {s: {k: round(F[s][k], 2) for k in ("occ", "mpos", "short", "types20", "edge_s")} for s in F})


def evaluate(LR, slot, tag, nboot=100):
    out = {}
    F = indus_slot_fp(LR)
    if slot not in F: return {"error": "slot too rare"}
    out["fp"] = {k: round(F[slot][k], 3) for k in FP}
    for g in ("ur3", "ob"):
        for keys, sd, kn in ((FP, SD_FULL, "full"), (FP_NODEF, SD_NODEF, "nodef")):
            H = hungarian(F, REFFP[g], keys, sd)
            nn, d = nearest_slot(F[slot], REFFP[g], keys, sd)
            out[f"{g}_{kn}"] = {"hungarian": H.get(slot), "nearest": nn, "d_KIN": round(d["KIN"], 3),
                                "d_nearest": round(d[nn], 3)}
    # bootstrap (texts resampled, fresh ref subsample), full features, Hungarian
    for g in ("ur3", "ob"):
        win = Counter()
        for _ in range(nboot):
            idx = rng.integers(0, len(LR), len(LR)); Fb = indus_slot_fp([LR[i] for i in idx])
            if slot not in Fb: win["(absent)"] += 1; continue
            Rf = ref_slot_fp(REF[g], n=len(LR))
            H = hungarian(Fb, Rf, FP, SD_FULL); win[H.get(slot, ("none",))[0]] += 1
        out[f"{g}_boot_hungarian"] = {k: v / nboot for k, v in win.items()}
    print(tag, json.dumps(out))
    return out


R["A2_R0_grammar"] = {"dev": evaluate(r0_runs("dev"), "CONN", "R0 dev"), "heldout": evaluate(r0_runs("heldout"), "CONN", "R0 ho")}
R["A2_R1_signlist"] = {"dev": evaluate(r1_runs(dev), "CONN", "R1 dev"), "heldout": evaluate(r1_runs(ho), "CONN", "R1 ho")}
R["A2_R1_M99only"] = {"dev": evaluate(r1_runs(dev, {"M99"}), "CONN", "R1 M99 dev"), "heldout": evaluate(r1_runs(ho, {"M99"}), "CONN", "R1 M99 ho")}

# ------------------------------------------------------------- pseudo-connective null (R1 frame)
cnt = Counter(x for t in dev for x in t)
cands = [w for w, n in cnt.items() if n >= 25 and indus_class(w) == "CORE"]
pseudo = {}
for w in cands:
    LR = r1_runs(dev, {w})
    F = indus_slot_fp(LR)
    if "CONN" not in F: continue
    res = {}
    for g in ("ur3", "ob"):
        H = hungarian(F, REFFP[g], FP, SD_FULL)
        nn, d = nearest_slot(F["CONN"], REFFP[g], FP, SD_FULL)
        res[g] = (H["CONN"][0], nn, round(d["KIN"], 3))
    pseudo[w] = res
real = {}
for name, conn in (("CONN{M99,M123}", CONN_M), ("M99", {"M99"})):
    F = indus_slot_fp(r1_runs(dev, conn))
    real[name] = {g: (hungarian(F, REFFP[g], FP, SD_FULL)["CONN"][0], *(lambda nn, d: (nn, round(d["KIN"], 3)))(*nearest_slot(F["CONN"], REFFP[g], FP, SD_FULL))) for g in ("ur3", "ob")}
summary = {}
for g in ("ur3", "ob"):
    hk = np.mean([v[g][0] == "KIN" for v in pseudo.values()]); nk = np.mean([v[g][1] == "KIN" for v in pseudo.values()])
    dk = np.array([v[g][2] for v in pseudo.values()]); rd = real["M99"][g][2]
    summary[g] = {"n_pseudo": len(pseudo), "share_pseudo_hungarian_KIN": round(float(hk), 3), "share_pseudo_nearest_KIN": round(float(nk), 3),
                  "M99_dKIN": rd, "p_pseudo_dKIN_le_M99": round(float((np.sum(dk <= rd) + 1) / (len(dk) + 1)), 3),
                  "median_pseudo_dKIN": round(float(np.median(dk)), 3)}
R["A3_pseudo_null"] = {"real": real, "summary": summary, "pseudo": pseudo}
print("A3 real", real); print("A3 summary", summary)
print("A3 pseudo mapped to KIN (ur3 hungarian):", [w for w, v in pseudo.items() if v["ur3"][0] == "KIN"])

# ------------------------------------------------------------- A4 distributional clustering (grammar-free)
A4 = {}
for k in (5, 6, 8, 10):
    for seed in (0, 1, 2):
        lab = cluster_labels(dev, k, seed)
        c99 = lab.get("M99"); members = sorted([w for w, l in lab.items() if l == c99], key=lambda w: -cnt[w])
        LRd = r2_runs(dev, lab); LRh = r2_runs(ho, lab)
        Fd = indus_slot_fp(LRd); Fh = indus_slot_fp(LRh)
        row = {"cluster": c99, "members": members[:15], "n_members": len(members), "M123_same": lab.get("M123") == c99}
        for g in ("ur3", "ob"):
            for nm, F in (("dev", Fd), ("ho", Fh)):
                if c99 not in F: row[f"{g}_{nm}"] = None; continue
                H = hungarian(F, REFFP[g], FP, SD_FULL); nn, d = nearest_slot(F[c99], REFFP[g], FP, SD_FULL)
                Hn = hungarian(F, REFFP[g], FP_NODEF, SD_NODEF)
                row[f"{g}_{nm}"] = {"hung": H.get(c99, ("unmatched", 0))[0], "hung_nodef": Hn.get(c99, ("unmatched", 0))[0],
                                    "nearest": nn, "dKIN": round(d["KIN"], 3), "types20": round(F[c99]["types20"], 1)}
        A4[f"k{k}_s{seed}"] = row
        print("A4", k, seed, json.dumps(row))
tally = Counter(); tally_n = Counter()
for row in A4.values():
    for g in ("ur3", "ob"):
        for nm in ("dev", "ho"):
            v = row.get(f"{g}_{nm}")
            if v: tally[(g, nm, v["hung"])] += 1; tally_n[(g, nm)] += 1
R["A4_clusters"] = A4
R["A4_tally"] = {f"{g}|{nm}|{s}": c / tally_n[(g, nm)] for (g, nm, s), c in tally.items()}
print("A4 tally", R["A4_tally"])

# ------------------------------------------------------------- A5 token-level (segmentation-free) M99 vs reference word classes
A5 = {}
for g in ("ur3", "ob", "fresh"):
    CF = ref_class_features(REF[g], classes=("SEAL_OF", "TITLE", "SERV", "KIN", "LORD", "NAME"), rng=rng)
    WF = word_type_features([c["tok"] for c in REF[g]], min_n=15, rng=rng)
    mu, sd = zscaler(list(WF.values()))
    row = {}
    for nm, T in (("dev", dev), ("ho", ho)):
        f = token_features(T, lambda l, i: l[i] == "M99", rng=rng)
        d = {k: dist(f, v, mu, sd) for k, v in CF.items()}
        row[nm] = {"nearest": min(d, key=d.get), "d": {k: round(v, 3) for k, v in d.items()}}
        # nearest single word types
        dw = sorted(((dist(f, v, mu, sd), w) for w, v in WF.items()))[:5]
        row[nm]["nearest_words"] = [(w, round(x, 2)) for x, w in dw]
    # specificity: every frequent Indus sign (dev, >=25 occ) classified
    sp = Counter()
    for w in cnt:
        if cnt[w] < 25: continue
        f = token_features(dev, lambda l, i, w=w: l[i] == w, rng=rng)
        d = {k: dist(f, v, mu, sd) for k, v in CF.items()}; sp[min(d, key=d.get)] += 1
    row["frequent_signs_nearest_class"] = dict(sp)
    A5[g] = row
    print("A5", g, json.dumps(row))
R["A5_token"] = A5
json.dump(R, open("taskA.json", "w"), indent=1, default=str)
