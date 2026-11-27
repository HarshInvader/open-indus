"""Ledger auditor: independent re-runs, on dev_heldout(version=2), of claims whose evidence used split v1 only
(or that had no exact p-value). Own code; only specifications (role sets, template, sign sets, fs80 classes)
are taken from the original teams, because those specifications ARE the claims under test.

Run from the repo root:  .venv/bin/python -I experiments/ledger/v2_reruns.py
Writes experiments/ledger/v2_reruns.json.
Options (for experiments/ledger/seed_sweep.py):  --out PATH   --seed N   --skip D  (D = 300 model fits, about 8 min)

Determinism (starter task S6): the output does not depend on PYTHONHASHSEED. Every loop that feeds a random
generator runs in sorted order, and block F has its own generator, so no other block can move its draws.

Re-runs
  A  functional_reading: held-out parse coverage vs within-text shuffles; lexicon-permutation null; Dholavira
  B  language P4: numerals precede marked fish less often than plain fish
  C  structure: K=3 positional classes learned on dev hold on held-out (nearest-centroid agreement)
  D  context Q1: whole text predicts the seal animal on held-out (balanced accuracy)
  E  structure / README #7: jar M342 closes L-R lines, copy-free lines only
  F  context/redteam Gulf: exact matched-n permutation p for foreign round seals (perm-percentile statistic)
  G  revalidation registers: exact Mann-Whitney p for the reported held-out AUCs
"""
import sys, json, math, random, itertools, argparse
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from scipy import stats
from corpus.load import dev_heldout, runs, m77_lines, icit_texts, distinct

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(Path(__file__).parent / "v2_reruns.json"))
ap.add_argument("--seed", type=int, default=20261114)
ap.add_argument("--skip", default="", help="blocks to skip; only D is supported")
ARGS = ap.parse_args()

OUT = {}
rng = random.Random(ARGS.seed)
nprng = np.random.default_rng(ARGS.seed)
frng = np.random.default_rng([ARGS.seed, 6])  # block F only
dev, ho = dev_heldout(version=2)
dev1, ho1 = dev_heldout(version=1)
OUT["split_sizes"] = dict(v2_dev=len(dev), v2_heldout=len(ho), v1_dev=len(dev1), v1_heldout=len(ho1))
print(OUT["split_sizes"], flush=True)

SRC = ROOT / "sources" / "shaunmortal_indus" / "data"
STROKES = json.load(open(SRC / "stroke_signs.json"))
SHORT = {f"M{k}" for k in STROKES["short"] if k not in ("99", "101")}
TALL = {f"M{k}" for k in STROKES["tall"]}
BR = json.load(open(SRC / "bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BR.items()}


# =====================================================================  A. functional reading
# Role letters: O opener, C connective, S short num, T tall num, U unit, F fish, B ticked fish, N noun,
# I title element, J closer, P post-closer clitic.  Spec copied from functional_reading/fr.py (the claim).
FISH_PLAIN = ["M59", "M61", "M62", "M63", "M64", "M65", "M67", "M69", "M70", "M72", "M74", "M75"]
FISH_BRACK = ["M60", "M66", "M68", "M71", "M73"]
HAND = {"M267": "O", "M391": "O", "M293": "ON", "M150": "O", "M99": "C", "M123": "CN", "M328": "UN", "M190": "U",
        "M342": "J", "M176": "P", "M1": "PJ", "M211": "J", "M169": "JN", "M162": "JN", "M15": "J", "M254": "J",
        "M12": "JP", "M347": "I", "M8": "I", "M343": "N", "M344": "N", "M345": "N", "M403": "N", "M407": "N",
        "M18": "NO", "M387": "NO", "M362": "N", "M363": "N", "M346": "N", "M184": "N"}
for s in FISH_PLAIN: HAND[s] = "F"
for s in FISH_BRACK: HAND[s] = "BF"
for s in sorted(SHORT): HAND.setdefault(s, "S")  # sorted: HAND key order feeds the lexicon-permutation null
HAND["M100"] = "SC"; HAND["M103"] = "S"
for s in sorted(TALL): HAND[s] = "T"
HAND = {k: set(v) for k, v in HAND.items()}

TRANS = {"^": set("OSTUFNIJB"), "O": set("OCSTFNIJU$"), "C": set("CSTFNIJBO"), "S": set("SFTNIUJBC"),
         "T": set("STFNIUJB"), "U": set("USTFNIJP$"), "F": set("SFTNIUJB$"), "N": set("SFTNIUJB$") | {"C", "P"},
         "I": set("ISTFNJ$"), "J": set("JP$"), "B": set("PJ$"), "P": set("P$")}


def lines_of(seq):
    out, cur = [], []
    for s in list(seq) + ["|"]:
        if s in ("|", "#"):
            if cur: out.append(cur)
            cur = []
        else:
            cur.append(s)
    return out


def induce_lexicon(texts, hand):
    pos = defaultdict(Counter); prev = defaultdict(Counter); nxt = defaultdict(Counter); ntext = Counter()
    for t in texts:
        for r in runs(t["seq"]):
            for i, s in enumerate(r):
                k = "A" if len(r) == 1 else "I" if i == 0 else "F" if i == len(r) - 1 else "M"
                pos[s][k] += 1
                if i: prev[s][r[i - 1]] += 1
                if i < len(r) - 1: nxt[s][r[i + 1]] += 1
        ntext.update(set(x for x in t["seq"] if x not in ("|", "#")))
    closers = {s for s, v in hand.items() if "J" in v}
    lex = {}
    for s, c in pos.items():
        if s in hand: lex[s] = hand[s]; continue
        if ntext[s] < 5: lex[s] = {"N"}; continue
        tot = sum(c.values()); pi = c["I"] / tot; pf = c["F"] / tot
        pp = sum(v for k, v in prev[s].items() if k in closers) / max(1, sum(prev[s].values()))
        nn = sum(nxt[s].values()); pj = nxt[s]["M342"] / max(1, nn)
        if pp >= 0.5 and pf >= 0.5: r = {"P", "J"}
        elif pf >= 0.7: r = {"J"}
        elif pf >= 0.45: r = {"J", "N"}
        elif pj >= 0.5 and nn >= 5: r = {"I", "N"}
        elif pi >= 0.6: r = {"O"}
        elif pi >= 0.4: r = {"O", "N"}
        else: r = {"N"}
        lex[s] = r
    for s, v in hand.items(): lex.setdefault(s, v)
    return lex


def accepts_line(line, lex):
    states = {"^"}
    for s in line:
        roles = lex.get(s, {"N"})
        states = {r for st in states for r in TRANS[st] if r in roles}
        if not states: return False
    return any("$" in TRANS[st] for st in states)


def accepts(seq, lex):
    return all(accepts_line(l, lex) for l in lines_of(seq))


def shuffled(seq):
    seq = list(seq); idx = [i for i, s in enumerate(seq) if s not in ("|", "#")]
    vals = [seq[i] for i in idx]; rng.shuffle(vals)
    for i, v in zip(idx, vals): seq[i] = v
    return seq


def coverage_test(texts, lex, nshuf=100):
    real = np.mean([accepts(t["seq"], lex) for t in texts])
    sh = np.array([np.mean([accepts(shuffled(t["seq"]), lex) for t in texts]) for _ in range(nshuf)])
    z = (real - sh.mean()) / sh.std()
    return dict(n=len(texts), coverage=round(float(real), 4), shuffled_mean=round(float(sh.mean()), 4),
                shuffled_sd=round(float(sh.std()), 4), z=round(float(z), 1),
                p_perm=(1 + int((sh >= real).sum())) / (nshuf + 1), p_normal=float(stats.norm.sf(z)))


def fr_block(dv, hv, label):
    dv = [t for t in dv if t["site"] != "West Asian finds"]
    hv = [t for t in hv if t["site"] != "West Asian finds" and "#" not in t["seq"]]
    lex = induce_lexicon(dv, HAND)
    res = coverage_test(hv, lex)
    # lexicon-permutation null: permute role sets among hand-assigned signs, re-induce, re-score
    keys = list(HAND); vals = [HAND[k] for k in keys]; null = []
    for _ in range(300):
        perm = vals[:]; rng.shuffle(perm)
        h2 = dict(zip(keys, perm))
        l2 = induce_lexicon(dv, h2)
        null.append(np.mean([accepts(t["seq"], l2) for t in hv]))
    null = np.array(null)
    res["lexicon_null_mean"] = round(float(null.mean()), 4); res["lexicon_null_sd"] = round(float(null.std()), 4)
    res["lexicon_null_p"] = (1 + int((null >= res["coverage"]).sum())) / (len(null) + 1)
    print(f"A {label}: {res}", flush=True)
    return res, lex


OUT["A_functional_reading"] = {}
OUT["A_functional_reading"]["v1_reproduction"], _ = fr_block(dev1, ho1, "v1 (reproduce 0.760 vs 0.334)")
OUT["A_functional_reading"]["v2"], lex2 = fr_block(dev, ho, "v2")
# Dholavira (ICIT), OOV = noun, lexicon induced on v2 dev
dhol = distinct([t for t in icit_texts() if t["site"] == "Dholavira" and "#" not in t["seq"]])
dseq = [dict(seq=[W2M.get(s, "OOV") if s not in ("|", "#") else s for s in t["seq"]]) for t in dhol]
dseq = [t for t in dseq if any(s not in ("|", "#") for s in t["seq"])]
OUT["A_functional_reading"]["dholavira_v2lex"] = coverage_test(dseq, lex2)
print("A Dholavira:", OUT["A_functional_reading"]["dholavira_v2lex"], flush=True)

# =====================================================================  B. language P4
A2 = json.load(open(ROOT / "experiments" / "language" / "a2_predictions.json"))["sign_sets"]
F0 = set(A2["fish_plain"]); FM = set(A2["fish_family_marked"])
NUM = {s for v, ss in A2["short_numerals"].items() for s in ss}


def p4(texts):
    def rate(S):
        k = n = 0
        for t in texts:
            for r in runs(t["seq"]):
                for i, s in enumerate(r):
                    if s in S: n += 1; k += int(i > 0 and r[i - 1] in NUM)
        return k, n
    k0, n0 = rate(F0); k1, n1 = rate(FM)
    _, p = stats.fisher_exact([[k0, n0 - k0], [k1, n1 - k1]], alternative="greater")
    return dict(plain=[k0, n0], marked=[k1, n1], plain_rate=round(k0 / n0, 3), marked_rate=round(k1 / n1, 3), p=float(p))


OUT["B_language_P4"] = dict(v2_dev=p4(dev), v2_heldout=p4(ho), v1_heldout=p4(ho1))
print("B", OUT["B_language_P4"], flush=True)


# =====================================================================  C. positional classes
def profiles(texts, min_texts=None, signs=None):
    pos = defaultdict(lambda: np.zeros(4)); nt = Counter()
    for t in texts:
        if "#" in t["seq"] or not t["complete"]: continue
        for r in runs(t["seq"]):
            for i, s in enumerate(r):
                k = 3 if len(r) == 1 else 0 if i == 0 else 2 if i == len(r) - 1 else 1
                pos[s][k] += 1
        nt.update(set(s for s in t["seq"] if s not in ("|", "#")))
    keep = [s for s in pos if (signs is None or s in signs) and (min_texts is None or nt[s] >= min_texts)]
    return {s: pos[s] / pos[s].sum() for s in keep}, {s: pos[s].sum() for s in keep}


from sklearn.cluster import KMeans
pd_, _ = profiles(dev, min_texts=10)
sg = sorted(pd_); X = np.array([pd_[s][:3] for s in sg])  # initial/medial/final shares
km = KMeans(3, n_init=50, random_state=0).fit(X)
lab = dict(zip(sg, km.labels_))
ph, nh = profiles(ho, signs=set(sg))
test = [s for s in ph if nh[s] >= 5]
pred = {s: int(np.argmin(((km.cluster_centers_ - ph[s][:3]) ** 2).sum(1))) for s in test}
agree = np.mean([pred[s] == lab[s] for s in test])
labs = np.array([lab[s] for s in test]); prd = np.array([pred[s] for s in test])
null = np.array([np.mean(nprng.permutation(labs) == prd) for _ in range(10000)])
OUT["C_positional_classes"] = dict(n_dev_signs=len(sg), n_test_signs=len(test), agreement=round(float(agree), 3),
                                   chance_mean=round(float(null.mean()), 3),
                                   p=(1 + int((null >= agree).sum())) / (len(null) + 1),
                                   centroids=[[round(x, 2) for x in c] for c in km.cluster_centers_])
print("C", OUT["C_positional_classes"], flush=True)


# =====================================================================  D. animal from text (held-out)
def animal(fs):
    if fs is None: return None
    for lo, hi, a in [(11, 17, "unicorn"), (21, 25, "longhorn_bull"), (31, 35, "zebu"), (61, 65, "buffalo"),
                      (71, 75, "elephant"), (91, 95, "tiger"), (111, 113, "rhino"), (131, 139, "goat_antelope"),
                      (141, 149, "ox_antelope"), (251, 253, "composite"), (361, 362, "gharial")]:
        if lo <= fs <= hi: return a
    if fs in (41, 45, 50): return "shorthorn_bull"
    return None


def seal_items(texts):
    by = defaultdict(set); rec = {}
    for t in texts:
        if t["object_type"] != "seal": continue
        a = animal(t.get("fs80"))
        if a is None: continue
        k = " ".join(t["seq"]); by[k].add(a); rec[k] = t
    return [(rec[k], next(iter(v))) for k, v in by.items() if len(v) == 1]


if "D" not in ARGS.skip:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score
    tr = seal_items(dev); te = seal_items(ho)
    cls_n = Counter(a for _, a in tr + te); classes = sorted(c for c, n in cls_n.items() if n >= 10)
    tr = [(t, a) for t, a in tr if a in classes]; te = [(t, a) for t, a in te if a in classes]
    voc = sorted({s for t, _ in tr for s in t["seq"] if s not in ("|", "#")}); vi = {s: i for i, s in enumerate(voc)}


    def feat(items):
        Xf = np.zeros((len(items), 2 * len(voc) + 2))
        for j, (t, _) in enumerate(items):
            sg_ = [s for s in t["seq"] if s not in ("|", "#")]
            for s in sg_:
                if s in vi: Xf[j, vi[s]] = 1
            if sg_ and sg_[0] in vi: Xf[j, len(voc) + vi[sg_[0]]] = 1
            Xf[j, -2] = len(sg_) / 5; Xf[j, -1] = t["seq"].count("|")
        return Xf


    Xtr, Xte = feat(tr), feat(te)
    ytr = np.array([a for _, a in tr]); yte = np.array([a for _, a in te]); site = np.array([t["site"] for t, _ in tr])
    mk = lambda: LogisticRegression(max_iter=3000, C=0.5, class_weight="balanced")
    ba = balanced_accuracy_score(yte, mk().fit(Xtr, ytr).predict(Xte))
    nb = []
    for _ in range(300):
        yp = ytr.copy()
        for s in sorted(set(site)):  # sorted: the order feeds nprng
            ix = np.where(site == s)[0]; yp[ix] = nprng.permutation(yp[ix])
        nb.append(balanced_accuracy_score(yte, mk().fit(Xtr, yp).predict(Xte)))
    nb = np.array(nb)
    OUT["D_animal_heldout"] = dict(n_train=len(tr), n_test=len(te), classes=classes, test_counts=dict(Counter(yte)),
                                   bal_acc=round(float(ba), 3), null_mean=round(float(nb.mean()), 3),
                                   p=(1 + int((nb >= ba).sum())) / (len(nb) + 1))
    print("D", OUT["D_animal_heldout"], flush=True)


# =====================================================================  E. jar closes L-R lines, copy-free
def ed_le1(a, b):
    if a == b: return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1: return False
    if la == lb: return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb: a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]: i += 1
    return a[i:] == b[i + 1:]


L = m77_lines()
rl = {tuple(l["signs"]) for l in L if l["direction"] == "right-to-left" and len(l["signs"]) >= 2 and "#" not in l["signs"]}
lr = {tuple(l["signs"]) for l in L if l["direction"] == "left-to-right" and len(l["signs"]) >= 2 and "#" not in l["signs"]}
rl_by_len = defaultdict(list)
for x in rl: rl_by_len[len(x)].append(x)
clean_lr = [x for x in lr if not any(ed_le1(x, y) for d in (-1, 0, 1) for y in rl_by_len[len(x) + d])]
last = sum(x[-1] == "M342" for x in clean_lr); first = sum(x[0] == "M342" for x in clean_lr)
last_all = sum(x[-1] == "M342" for x in lr); first_all = sum(x[0] == "M342" for x in lr)
OUT["E_jar_LR_copyfree"] = dict(lr_distinct=len(lr), lr_copyfree=len(clean_lr), jar_last=last, jar_first=first,
                                all_lr_last=last_all, all_lr_first=first_all,
                                p_binom_last_vs_first=float(stats.binomtest(last, last + first, 0.5, alternative="greater").pvalue) if last + first else None)
print("E", OUT["E_jar_LR_copyfree"], flush=True)

# =====================================================================  F. Gulf round seals, exact matched-n p
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar", "Salut",
           "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Dilmun", "Kalba",
           "Gonur", "Gonur Depe", "Altyn Depe", "Shortughai"}
I = icit_texts()
nat = distinct([t for t in I if t["site"] not in FOREIGN and t["site"] != "Unknown" and "#" not in t["seq"]])
fr_round = distinct([t for t in I if t["site"] in FOREIGN and t["type"] in ("SEAL:R", "SEAL:C", "SEAL:CY")
                     and "#" not in t["seq"]])


class KN:
    def __init__(self, seqs, d=0.75):
        self.d = d; self.big = Counter(); self.ctx = Counter(); self.cont = defaultdict(set); self.fol = defaultdict(set)
        for r in seqs:
            r = ["<s>"] + list(r) + ["</s>"]
            for a, b in zip(r, r[1:]):
                self.big[(a, b)] += 1; self.ctx[a] += 1; self.cont[b].add(a); self.fol[a].add(b)
        self.nbt = len(self.big); self.V = len(self.cont) + 1

    def lp(self, r):
        r = ["<s>"] + list(r) + ["</s>"]; tot = 0.0
        for a, b in zip(r, r[1:]):
            pc = (len(self.cont.get(b, ())) + 0.5) / (self.nbt + 0.5 * self.V)
            ca = self.ctx.get(a, 0)
            p = pc if ca == 0 else max(self.big.get((a, b), 0) - self.d, 0) / ca + self.d * len(self.fol[a]) / ca * pc
            tot += math.log(p)
        return tot


def perm_pct(r, m):
    s0 = m.lp(r); ps = set(itertools.permutations(r)); ps.discard(tuple(r))
    if not ps: return None
    sc = [m.lp(p) for p in ps]
    return (sum(x < s0 for x in sc) + 0.5 * sum(x == s0 for x in sc)) / len(sc)


def single_run(t):
    rr = runs(t["seq"])
    return rr[0] if len(rr) == 1 and 2 <= len(rr[0]) <= 7 else None


allnat_runs = [r for t in nat for r in runs(t["seq"])]
m_all = KN(allnat_runs)
fvals = [(len(r), perm_pct(r, m_all)) for r in (single_run(t) for t in fr_round) if r]
fvals = [(n, v) for n, v in fvals if v is not None]
PERIPH = ["Dholavira", "Kalibangan", "Chanhu-daro", "Lothal", "Nausharo", "Banawali"]
pool = defaultdict(list)
for sname in PERIPH:
    m_s = KN([r for t in nat if t["site"] != sname for r in runs(t["seq"])])
    for t in nat:
        if t["site"] == sname and t["type"].startswith("SEAL"):
            r = single_run(t)
            if r:
                v = perm_pct(r, m_s)
                if v is not None: pool[min(len(r), 5)].append(v)
fmean = float(np.mean([v for _, v in fvals]))
draws = []
for _ in range(20000):
    draws.append(np.mean([pool[min(n, 5)][frng.integers(len(pool[min(n, 5)]))] for n, _ in fvals]))
draws = np.array(draws)
OUT["F_gulf_round"] = dict(n_foreign=len(fvals), foreign_mean_pct=round(fmean, 3),
                           native_matched_mean=round(float(draws.mean()), 3),
                           native_matched_p05=round(float(np.quantile(draws, 0.05)), 3),
                           p=(1 + int((draws <= fmean).sum())) / (len(draws) + 1),
                           z=round(float((draws.mean() - fmean) / draws.std()), 2),
                           p_normal=float(stats.norm.sf((draws.mean() - fmean) / draws.std())),
                           pool_sizes={k: len(v) for k, v in pool.items()})
print("F", OUT["F_gulf_round"], flush=True)

# =====================================================================  G. registers: exact MWU p from AUC
rv = json.load(open(ROOT / "experiments" / "revalidation" / "results.json"))["registers"]
ntot = sum(v["n"] for v in rv.values())
G = {}
for k, v in rv.items():
    n1, n0 = v["n"], ntot - v["n"]
    se = math.sqrt((n1 + n0 + 1) / (12 * n1 * n0))
    G[k] = dict(n=n1, auc=v["auc"], z=round((v["auc"] - 0.5) / se, 2), p=float(stats.norm.sf((v["auc"] - 0.5) / se)))
OUT["G_registers_exact"] = G
print("G", G, flush=True)

json.dump(OUT, open(ARGS.out, "w"), indent=1, default=float)
print("done")
