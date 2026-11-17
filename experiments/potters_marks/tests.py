"""Pre-registered tests for experiments/potters_marks (see docs/prereg/potters_marks.md).

Run once: .venv/bin/python experiments/potters_marks/tests.py  -> tests.json, tests.log
"""
import csv, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, distinct  # noqa: E402

RNG = np.random.default_rng(20261115)
NPERM = 10000
FRAME_ROLES = {"OPENER", "CONNECTIVE", "CLOSER", "POST-CLOSER CLITIC", "TITLE ELEMENT", "UNIT/MEASURE",
               "BRACKETED-FISH CLOSER"}
CORE_ROLES = {"NOUN", "FISH-CLASS NOUN"}
NAMED_FRAME = ["M342", "M328", "M211", "M162", "M169", "M267", "M391", "M99"]
out, log = {}, []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); log.append(s)


# ------------------------------------------------------------------ sign universe and classes
lex = {r["item"]: r for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv"))}


def modal_role(s):
    best, bw = None, -1
    for part in s.split(";"):
        m = re.match(r"\s*(.+?)\s+([0-9.]+)\s*$", part)
        if m and float(m.group(2)) > bw:
            best, bw = m.group(1), float(m.group(2))
    return best


def ink(sign):
    """Skeleton-free complexity proxy: number of dark pixels of the drawing scaled to a 64-px box."""
    im = Image.open(ROOT / f"data/sign_images/{sign}.png").convert("L")
    a = np.array(im) < 128
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return 0.0
    crop = Image.fromarray((a[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype(np.uint8))
    crop.thumbnail((64, 64))
    return float((np.array(crop) > 64).sum())


U = {}
for s, r in lex.items():
    if not s.startswith("M") or not r["roles"]:
        continue
    try:
        f = int(r["dev_texts"])
    except ValueError:
        continue
    if f < 5:
        continue
    role = modal_role(r["roles"])
    cls = "frame" if role in FRAME_ROLES else "core" if role in CORE_ROLES else "numeral" if role and role.startswith("NUMERAL") else None
    if cls:
        U[s] = dict(cls=cls, role=role, freq=f, ink=ink(s))
say("universe (dev_texts>=5):", Counter(v["cls"] for v in U.values()))

# ------------------------------------------------------------------ marks
marks = list(csv.DictReader(open(HERE / "marks.csv")))


def credited(defn):
    """Return {sign: n_marks} credited as an early precursor under a definition."""
    got = Counter()
    for m in marks:
        mm = m["m77_match"].strip()
        if mm in ("", "-"):
            continue
        n = int(m["n_marks"]) if str(m["n_marks"]).isdigit() else 1
        if defn == "P1":
            if m["early"] != "yes" or m["match_conf"] not in ("A", "B"):
                continue
            for pos in mm.split("-"):
                if "|" not in pos and pos.startswith("M"):
                    got[pos] += n
        elif defn == "P2":
            if m["early"] != "yes" or m["match_basis"] not in ("author", "icit"):
                continue
            for pos in mm.split("-"):
                for alt in pos.split("|"):
                    if alt.startswith("M"):
                        got[alt] += n
        elif defn == "P3":
            if m["early"] not in ("yes", "doubtful", "transitional"):
                continue
            for pos in mm.split("-"):
                for alt in pos.split("|"):
                    if alt.startswith("M"):
                        got[alt] += n
    return got


def test_a(defn):
    cred = credited(defn)
    sig = [s for s in U if U[s]["cls"] in ("frame", "core")]
    y = np.array([1 if cred.get(s, 0) > 0 else 0 for s in sig])
    fr = np.array([1 if U[s]["cls"] == "frame" else 0 for s in sig])
    inkv = np.array([U[s]["ink"] for s in sig])
    logf = np.log([U[s]["freq"] for s in sig])
    a, b = int(((fr == 1) & (y == 1)).sum()), int(((fr == 1) & (y == 0)).sum())
    c, d = int(((fr == 0) & (y == 1)).sum()), int(((fr == 0) & (y == 0)).sum())
    fisher_or, fisher_p = stats.fisher_exact([[a, b], [c, d]], alternative="greater")
    # complexity-stratified permutation (tertiles of ink), statistic = frame rate - core rate
    tert = np.digitize(inkv, np.quantile(inkv, [1 / 3, 2 / 3]))

    def diff(lbl):
        return y[lbl == 1].mean() - y[lbl == 0].mean()

    obs = diff(fr)
    null = np.empty(NPERM)
    for i in range(NPERM):
        p = fr.copy()
        for t in range(3):
            idx = np.where(tert == t)[0]
            p[idx] = RNG.permutation(p[idx])
        null[i] = diff(p)
    p_perm = float((np.sum(null >= obs - 1e-12) + 1) / (NPERM + 1))
    # logistic regression precursor ~ frame + ink + log freq (Firth-free; report coefficient)
    try:
        import statsmodels.api as sm
        X = sm.add_constant(np.column_stack([fr, (inkv - inkv.mean()) / inkv.std(), logf - logf.mean()]))
        res = sm.Logit(y, X).fit(disp=0)
        logit = dict(beta_frame=float(res.params[1]), p_frame=float(res.pvalues[1]),
                     beta_ink=float(res.params[2]), beta_logfreq=float(res.params[3]))
    except Exception as e:  # noqa
        logit = dict(error=str(e))
    frame_hits = sorted([s for s in sig if U[s]["cls"] == "frame" and cred.get(s, 0) > 0], key=lambda s: int(s[1:]))
    core_hits = sorted([s for s in sig if U[s]["cls"] == "core" and cred.get(s, 0) > 0], key=lambda s: int(s[1:]))
    num_hits = sorted([s for s in U if U[s]["cls"] == "numeral" and cred.get(s, 0) > 0], key=lambda s: int(s[1:]))
    # power: planted frame rate = 2x and 3x core rate, same n
    pw = {}
    base = max(c / (c + d), 0.02)
    for mult in (2, 3):
        hits = 0
        for i in range(500):
            yf = RNG.random(a + b) < min(1, base * mult)
            yc = RNG.random(c + d) < base
            pp = stats.fisher_exact([[yf.sum(), (a + b) - yf.sum()], [yc.sum(), (c + d) - yc.sum()]],
                                    alternative="greater")[1]
            hits += pp < 0.05
        pw[f"{mult}x"] = hits / 500
    r = dict(defn=defn, frame_with=a, frame_n=a + b, core_with=c, core_n=c + d,
             frame_rate=a / (a + b), core_rate=c / (c + d), fisher_or=float(fisher_or), fisher_p=float(fisher_p),
             diff=float(obs), p_strat_perm=p_perm, logit=logit, power_fisher=pw,
             frame_hits=frame_hits, core_hits=core_hits, numeral_hits=num_hits)
    return r


say("\n=== Test (a): frame vs core signs with an early precursor ===")
out["a"] = {}
for defn in ("P1", "P2", "P3"):
    r = test_a(defn)
    out["a"][defn] = r
    say(f"{defn}: frame {r['frame_with']}/{r['frame_n']} ({r['frame_rate']:.3f}) vs core {r['core_with']}/{r['core_n']} "
        f"({r['core_rate']:.3f}); Fisher OR {r['fisher_or']:.2f} p={r['fisher_p']:.3f}; strat-perm p={r['p_strat_perm']:.3f}; "
        f"logit {r['logit']}; power {r['power_fisher']}")
    say("   frame hits:", r["frame_hits"]); say("   core hits:", r["core_hits"]); say("   numeral hits:", r["numeral_hits"])

say("\nNamed frame signs (P1 / P2 / P3 credited marks):")
c1, c2, c3 = credited("P1"), credited("P2"), credited("P3")
out["named"] = {s: dict(P1=c1.get(s, 0), P2=c2.get(s, 0), P3=c3.get(s, 0), role=U.get(s, {}).get("role")) for s in NAMED_FRAME}
for s in NAMED_FRAME:
    say(f"  {s}: {out['named'][s]}")

# ------------------------------------------------------------------ test (b): Sarai Khola vessel clustering
say("\n=== Test (b): do marks cluster on one vessel class? (Sarai Khola, Halim 1972) ===")
FAM = {"strokes": [1, 2, 3, 4, 5, 6, 12, 29, 32, 33, 35, 40], "cross_T": [7, 8, 9, 11],
       "V": [10, 20, 22, 24, 25, 26], "W_N": [18, 19, 23, 27, 28, 30, 31], "chevron_arrow": [13, 14, 17],
       "Y_star": [16, 21], "curvilinear": [15, 36, 37, 38, 39], "tree": [34]}
cat2fam = {c: f for f, cs in FAM.items() for c in cs}
occ = []  # (family, cat, class)
for m in marks:
    if m["source"] != "H72" or m["vessel_class"] not in ("jar", "bowl"):
        continue
    cat = int(m["mark_id"][2:4])
    occ += [(cat2fam[cat], cat, m["vessel_class"])] * int(m["n_marks"])
fams = np.array([o[0] for o in occ]); cats = np.array([o[1] for o in occ]); cls = np.array([1 if o[2] == "jar" else 0 for o in occ])
say(f"typed occurrences: {len(occ)} (jar {cls.sum()}, bowl {len(cls) - cls.sum()})")
keep = [f for f in FAM if (fams == f).sum() >= 3]


def chi(lbl, groups, fam):
    s = 0.0
    p0 = lbl.mean()
    for g in groups:
        idx = fam == g
        n = idx.sum(); o = lbl[idx].sum(); e = n * p0
        if e > 0 and n - e > 0:
            s += (o - e) ** 2 / e + ((n - o) - (n - e)) ** 2 / (n - e)
    return s


mask = np.isin(fams, keep)
lblk, famk = cls[mask], fams[mask]
obs = chi(lblk, keep, famk)
null = np.array([chi(RNG.permutation(lblk), keep, famk) for _ in range(NPERM)])
p_chi = float((np.sum(null >= obs - 1e-12) + 1) / (NPERM + 1))
per = {}
for f in keep:
    idx = famk == f
    n, j = int(idx.sum()), int(lblk[idx].sum())
    p_two = float(stats.binomtest(j, n, lblk.mean()).pvalue)
    per[f] = dict(n=n, jar=j, bowl=n - j, jar_share=j / n, p_binom_two_sided=p_two)
ps = [per[f]["p_binom_two_sided"] for f in keep]
order = np.argsort(ps); q = np.empty(len(ps)); m_ = len(ps)
for rank, i in enumerate(order[::-1]):
    k = m_ - rank
    q[i] = min(1.0, ps[i] * m_ / k) if rank == 0 else min(q[order[::-1][rank - 1]], ps[i] * m_ / k)
for f, qq in zip(keep, q):
    per[f]["q_bh"] = float(qq)
restricted = [f for f in keep if max(per[f]["jar_share"], 1 - per[f]["jar_share"]) >= 0.8 and per[f]["q_bh"] < 0.05]
for f in keep:
    say(f"  {f}: {per[f]}")
say(f"chi2 = {obs:.2f}, permutation p = {p_chi:.3f}; restricted families (>=80% one class, q<0.05): {restricted}")

# power: plant one family of size n fully in jars (or bowls) and others as observed-random
pw = {}
base = lblk.mean()
for n_plant in (4, 6, 10):
    hits = 0
    for i in range(300):
        lab = (RNG.random(len(lblk)) < base).astype(int)  # observed families, no real clustering
        lab2 = np.concatenate([lab, np.ones(n_plant, int)])  # plus one family entirely on jars
        fam2 = np.concatenate([famk, np.array(["PLANT"] * n_plant)])
        o = chi(lab2, keep + ["PLANT"], fam2)
        nl = np.array([chi(RNG.permutation(lab2), keep + ["PLANT"], fam2) for _ in range(200)])
        hits += (np.sum(nl >= o) + 1) / 201 < 0.05
    pw[f"plant_{n_plant}_all_jar"] = hits / 300
say("power (one extra family entirely on jars, chi2 perm p<0.05):", pw)
out["b"] = dict(n_typed=len(occ), jar=int(cls.sum()), bowl=int(len(cls) - cls.sum()), families=per, chi2=obs,
                p_perm=p_chi, restricted=restricted, power=pw,
                note="only Sarai Khola has per-mark vessel type; Mehrgarh (Quivron 1980) states marks are on goblets, cups and jars alike, without counts")

# Precursors of named frame signs on typed vessels
say("\nTyped vessel occurrences per M77 match (Sarai Khola + Kot Diji, any confidence):")
typed = defaultdict(Counter)
for m in marks:
    if m["vessel_class"] in ("jar", "bowl", "lid") and m["m77_match"] not in ("", "-"):
        typed[m["m77_match"]][m["vessel_class"]] += int(m["n_marks"]) if str(m["n_marks"]).isdigit() else 1
for k, v in sorted(typed.items()):
    say(f"  {k}: {dict(v)}")
out["typed_by_match"] = {k: dict(v) for k, v in typed.items()}

# ------------------------------------------------------------------ test (c): Mature pottery
say("\n=== Test (c): Mature pottery keeps the vessel association? ===")
icit = icit_texts()
pot = [r for r in icit if r["type"].upper().startswith("PO")]
say("ICIT pottery rows:", len(pot), "| vessel form recorded: 0 (shape field is the inscription field, not the pot)")
out["c"] = dict(verdict="untestable", reason="neither ICIT nor M77 records the vessel form of inscribed pottery")
# descriptive: share of distinct Mature pottery texts containing each named frame sign, by marking method
bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W_of = defaultdict(set)
for w, v in bridge.items():
    for mnum in v["M"]:
        W_of[f"M{mnum}"].add(f"W{int(w):03d}")
early_ids = {m["mark_id"][5:] for m in marks if m["source"] == "ICIT"}
desc = {}
for typ in ("POT:T:p", "POT:T:g", "POT:T:s"):
    rows = distinct([r for r in pot if r["type"] == typ and r["id"] not in early_ids])
    d = {}
    for s in NAMED_FRAME + ["M347", "M176", "M177", "M294"]:
        n = sum(1 for r in rows if any(w in W_of[s] for w in r["seq"]))
        d[s] = n
    desc[typ] = dict(n=len(rows), counts=d)
    say(f"  {typ} (distinct Mature texts {len(rows)}): {d}")
seals = distinct([r for r in icit if r["type"].startswith("SEAL")])
d = {s: sum(1 for r in seals if any(w in W_of[s] for w in r["seq"])) for s in NAMED_FRAME + ["M347", "M176", "M177", "M294"]}
desc["SEAL"] = dict(n=len(seals), counts=d)
say(f"  SEAL (distinct {len(seals)}): {d}")
out["c"]["descriptive"] = desc

json.dump(out, open(HERE / "tests.json", "w"), indent=1, default=float)
open(HERE / "tests.log", "w").write("\n".join(log) + "\n")
