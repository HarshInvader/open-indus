"""R1: travelling numeral formula. R1a null choice, R1b novelty grep, R1c independence, R1d M77 held-out.
usage: .venv/bin/python experiments/redteam_local_repeats/r1.py [nsim]
"""
import sys, os, json, re, glob, itertools
from collections import Counter, defaultdict
import numpy as np

NSIM = int(sys.argv[1]) if len(sys.argv) > 1 else 500
sys.argv = sys.argv[:1] + ["10"]  # lr.py reads argv[1] as nperm
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rlib import *  # noqa
import c1  # noqa  read-only
import lr  # noqa  read-only
from id_lib import m77_objects, flat  # noqa
from corpus.load import dev_heldout  # noqa

rng = np.random.default_rng(20261114)
out = {}

# ---------------------------------------------------------------- data
SEALS = lr.SEALS
T45 = [o["text"] for o in SEALS if 4 <= len(o["text"]) <= 5]
D_all = c1.distinct_corpus(c1.ALL)
V = sorted({s for t in D_all for s in t})
seal45 = {o["text"] for o in SEALS if 4 <= len(o["text"]) <= 5}
D_lo = [t for t in D_all if t not in seal45]


def stats(T):
    c = Counter(T)
    rep = [t for t, k in c.items() if k > 1 and 4 <= len(t) <= 5]
    return dict(all=sum(c[t] for t in rep), formula=sum(c[t] for t in rep if is_formula(t)),
                other=sum(c[t] for t in rep if not is_formula(t)), formula_frame=sum(is_formula(t) for t in T),
                formula_texts_rep=sum(1 for t in rep if is_formula(t)))


obs = stats(T45); out["observed"] = obs; print("observed", obs)
L45 = [len(t) for t in T45]

# ---------------------------------------------------------------- R1a nulls
g = c1.Bigram(D_all, V); g.prepare(30)
models = {"N2": g, "TRI-A": Trigram(D_all, V), "TRI-L": Trigram(D_lo, V), "SLOT-A": Slot(D_all, V), "SLOT-L": Slot(D_lo, V),
          "TRI-A_l80": Trigram(D_all, V, (0.8, 0.15, 0.05)), "TRI-A_l40": Trigram(D_all, V, (0.4, 0.4, 0.2)),
          "TRI-L_l80": Trigram(D_lo, V, (0.8, 0.15, 0.05))}
R1a = {}
for name, m in models.items():
    S = [stats(m.sample(L45, rng)) for _ in range(NSIM)]
    R1a[name] = {k: summ([s[k] for s in S], obs[k]) for k in obs}
    print("R1a", name, {k: "%.2f [%.0f-%.0f] p=%.3f" % (v["mean"], v["lo"], v["hi"], v["p_ge"]) for k, v in R1a[name].items()}, flush=True)
out["R1a"] = R1a

# model adequacy: 5-fold CV over distinct texts, log-lik of held-out 4-5 seal texts
folds = np.arange(len(D_all)) % 5; rng.shuffle(folds)
cv = defaultdict(list)
for f in range(5):
    tr = [t for t, k in zip(D_all, folds) if k != f]; te = [t for t, k in zip(D_all, folds) if k == f and t in seal45]
    gb = c1.Bigram(tr, V); gb.prepare(30); tg = Trigram(tr, V); sl = Slot(tr, V)
    tgs = {l3: Trigram(tr, V, (l3, (1 - l3) * 0.75, (1 - l3) * 0.25)) for l3 in (0.3, 0.4, 0.5, 0.7, 0.8)}
    for t in te:
        for l3, m_ in tgs.items(): cv["trigram_joint_l%d" % int(l3 * 100)].append(m_.logp(t))
        cv["bigram_joint"].append(bigram_logp(gb, t, cond=False)); cv["trigram_joint"].append(tg.logp(t))
        cv["bigram_cond"].append(bigram_logp(gb, t, cond=True)); cv["slot_cond"].append(sl.logp(t))
        cv["formula"].append(is_formula(t))
cvr = {k: float(np.mean(v)) for k, v in cv.items() if k != "formula"}
fm = np.array(cv["formula"])
for k in list(cvr):
    cvr[k + "_formula_texts"] = float(np.mean(np.array(cv[k])[fm])) if fm.any() else None
cvr["n_test_texts"] = len(fm); cvr["n_formula_test_texts"] = int(fm.sum())
cvr["trigram_minus_bigram_joint_nats_per_text"] = cvr["trigram_joint"] - cvr["bigram_joint"]
cvr["slot_minus_bigram_cond_nats_per_text"] = cvr["slot_cond"] - cvr["bigram_cond"]
out["R1a_cv_loglik"] = cvr; print("CV", cvr)

# where the formula 4-gram lives in the corpus (distinct texts, any class, any length)
def contains(u, t):
    return any(u[i:i + len(t)] == t for i in range(len(u) - len(t) + 1))
frame_in = Counter()
for t in D_all:
    for i in range(len(t) - 3):
        if is_formula(t[i:i + 4]): frame_in["len4" if len(t) == 4 else "inside_longer"] += 1; break
pref3 = Counter()  # opener W002 numeral as a 3-gram: what follows?
for t in D_all:
    for i in range(len(t) - 2):
        if t[i] in OPEN and t[i + 1] == "W002" and t[i + 2] in NUM:
            pref3["END" if i + 3 == len(t) else t[i + 3]] += 1
out["formula_context"] = dict(distinct_texts_with_frame=dict(frame_in), next_after_opener_W002_num=pref3.most_common(10))
print("context", out["formula_context"])

# ---------------------------------------------------------------- R1b novelty grep
pat = re.compile(r"(M267|M391)[- ]M99[- ]M10[2-9][- ]M16[12]|W8(17|61|20)[- ]W0?02[- ]W0?0(3|4|16)[- ]W390|opener \+ stroke \+ tree")
hits = []
files = glob.glob(os.path.join(lr.ROOT, "sources/*/STATE.md")) + glob.glob(os.path.join(lr.ROOT, "sources/*/*.md")) + \
    glob.glob(os.path.join(lr.ROOT, "experiments/*/RESULTS.md")) + glob.glob(os.path.join(lr.ROOT, "docs/*.md"))
for fpath in sorted(set(files)):
    if "local_repeats" in fpath: continue
    for ln, line in enumerate(open(fpath, errors="ignore"), 1):
        if pat.search(line): hits.append(dict(file=os.path.relpath(fpath, lr.ROOT), line=ln, text=line.strip()[:300]))
out["R1b_prior_records"] = hits
print("R1b", len(hits)); [print("  ", h["file"], h["line"], h["text"][:200]) for h in hits]

# ---------------------------------------------------------------- R1c independence of the 14 objects
fobj = [o for o in SEALS if is_formula(o["text"]) and lr.cnt[o["text"]] >= 2]
rows = []
for o in fobj:
    i = lr.info(o); r = lr.RAW[o["obj"]]
    flags = []
    if not o["type"].startswith("SEAL"): flags.append("not SEAL type")
    if any(w in (r["material"] or "").lower() for w in ("faience", "terracotta", "copper", "clay", "paste")): flags.append("material " + r["material"])
    if not lr.known(o["cisi"]): flags.append("no CISI")
    other = [x for x in lr.all_by_text[o["text"]] if x["cls"] != "seal" and x["site"] == o["site"]]
    if other: flags.append("same text on %d other carriers at site" % len(other))
    rows.append(dict(obj=o["obj"], cisi=o["cisi"], site=o["site"], text=" ".join(o["text"]), type=o["type"], material=r["material"],
                     w=i["w"], h=i["h"], symbol=i["symbol"], period=i["period"], area=i["area"], flags=flags))
for a, b in itertools.combinations(rows, 2):
    if a["site"] == b["site"] and a["symbol"] == b["symbol"] and a["w"] > 0 and b["w"] > 0 and \
            abs(a["w"] - b["w"]) <= 0.5 and abs(a["h"] - b["h"]) <= 0.5:
        a["flags"].append("same site/emblem/dims as " + b["cisi"]); b["flags"].append("same site/emblem/dims as " + a["cisi"])
for r in rows: print("R1c", r)
flagged = {r["obj"] for r in rows if r["flags"]}
# recompute with flagged objects removed
keep = [o["text"] for o in SEALS if 4 <= len(o["text"]) <= 5 and o["obj"] not in flagged]
obs_c = stats(keep)
Lk = [len(t) for t in keep]
Sc = {}
for name in ("N2", "TRI-L", "SLOT-L"):
    S = [stats(models[name].sample(Lk, rng)) for _ in range(NSIM)]
    Sc[name] = {k: summ([s[k] for s in S], obs_c[k]) for k in ("formula", "other", "formula_frame")}
out["R1c"] = dict(objects=rows, n_flagged=len(flagged), observed_after_drop=obs_c, nulls_after_drop=Sc,
                  sites=sorted({r["site"] for r in rows}))
print("R1c after drop", obs_c, {k: {kk: round(vv["p_ge"], 3) for kk, vv in v.items()} for k, v in Sc.items()})

# M77 transcription of the frame (Mahadevan signs)
MOPEN = {"M267", "M391"}; MCON = {"M99", "M100"}; MCL = {"M161", "M162", "M167", "M168", "M169"}
MNUM = {"M97", "M98", "M101"} | {f"M{k}" for k in range(102, 119)} | {"M121", "M122"}
def mformula(t, closers=MCL, cons=MCON):
    return len(t) == 4 and t[0] in MOPEN and t[1] in cons and t[2] in MNUM and t[3] in closers
mall = [o for o in m77_objects() if o["complete"]]
for o in mall: o["text"] = flat(o["sp"])
mseal = [o for o in mall if o["cls"] == "seal"]
mf = [o for o in mseal if mformula(o["text"])]
out["R1c_m77_frame"] = dict(n_seal_objects=len(mf), by_text=Counter(" ".join(o["text"]) for o in mf).most_common(),
                            by_site=Counter(o["site"] for o in mf), closers=Counter(o["text"][3] for o in mf),
                            connective=Counter(o["text"][1] for o in mf),
                            other_classes=Counter(o["cls"] for o in mall if mformula(o["text"]) and o["cls"] != "seal"))
print("M77 frame", out["R1c_m77_frame"])

# ---------------------------------------------------------------- R1d M77 dev / held-out
dev, ho = dev_heldout(version=2)
def dclean(ts):
    return sorted({tuple(s for s in t["seq"] if s != "|") for t in ts if t["complete"] and "#" not in t["seq"]} - {()})
Ddev = dclean(dev)
VM = sorted({s for o in mall for s in o["text"]} | {s for t in Ddev for s in t})
mdev = [o for o in m77_objects("dev") if o["complete"] and o["cls"] == "seal"]
mho = [o for o in m77_objects("heldout") if o["complete"] and o["cls"] == "seal"]
for L_ in (mdev, mho):
    for o in L_: o["text"] = flat(o["sp"])
def mstats(T):
    c = Counter(T)
    return dict(frame=sum(mformula(t) for t in T), frame_strict=sum(mformula(t, {"M161"}, {"M99"}) for t in T),
                frame_rep_texts=sum(1 for t, k in c.items() if k > 1 and mformula(t)),
                frame_rep_objects=sum(k for t, k in c.items() if k > 1 and mformula(t)),
                rep45_objects=sum(k for t, k in c.items() if k > 1 and 4 <= len(t) <= 5))
od, oh = mstats([o["text"] for o in mdev]), mstats([o["text"] for o in mho])
gm = c1.Bigram(Ddev, VM); gm.prepare(40); tm = Trigram(Ddev, VM); sm = Slot(Ddev, VM)
Lh = [len(o["text"]) for o in mho]
R1d = dict(dev_observed=od, heldout_observed=oh, n_dev_seals=len(mdev), n_heldout_seals=len(mho),
           heldout_frame_texts=Counter(" ".join(o["text"]) for o in mho if mformula(o["text"])).most_common(),
           dev_frame_texts=Counter(" ".join(o["text"]) for o in mdev if mformula(o["text"])).most_common())
for name, m in (("bigram_dev", gm), ("trigram_dev", tm), ("slot_dev", sm)):
    S = [mstats(m.sample(Lh, rng)) for _ in range(NSIM)]
    R1d[name] = {k: summ([s[k] for s in S], oh[k]) for k in oh}
    print("R1d", name, {k: "%.2f [%.0f-%.0f] p=%.3f obs %d" % (v["mean"], v["lo"], v["hi"], v["p_ge"], oh[k]) for k, v in R1d[name].items()})
out["R1d"] = R1d
print("R1d obs dev", od, "heldout", oh)
print(R1d["heldout_frame_texts"], R1d["dev_frame_texts"])

# ICIT sites absent from M77 (descriptive)
m77sites = {o["site"] for o in mall}
out["R1d_icit_new_sites"] = dict(formula_frame_seals=Counter(o["site"] for o in SEALS if is_formula(o["text"]) and o["site"] not in m77sites),
                                 all_formula_frame_seals=Counter(o["site"] for o in SEALS if is_formula(o["text"])))
print("new sites", out["R1d_icit_new_sites"])
json.dump(out, open(os.path.join(HERE, "r1.json"), "w"), indent=1, default=lambda x: x if not isinstance(x, set) else sorted(x))
