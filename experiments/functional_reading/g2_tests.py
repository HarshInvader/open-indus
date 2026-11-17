"""Predictive tests of the frozen functional grammar. Grammar + lexicon fit on DEV only; every number
below is on held-out M77 or on ICIT texts (bridged W->M), never used in design.
(a) parse coverage vs within-text shuffle null
(b) object type from parse vs sign-bag baseline
(c) masked-sign prediction vs KN bigram
(d) foreign (Gulf / West Asian) detection
"""
import json, random, math
from collections import Counter, defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import roc_auc_score, balanced_accuracy_score
from fr import *

rng = random.Random(7); nrng = np.random.default_rng(7)
dev, ho, dev_g, lex, comps, G = load_model()
R = {}
M77_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}
dev_keys = {" ".join(t["seq"]) for t in dev}


def nsig(t): return sum(1 for s in t["seq"] if s not in ("|", "#"))


def shuffled(t, r):
    seq = list(t["seq"]); pos = [i for i, s in enumerate(seq) if s not in ("|", "#")]
    vals = [seq[i] for i in pos]; r.shuffle(vals)
    for i, v in zip(pos, vals): seq[i] = v
    return dict(t, seq=seq)


def coverage(texts, label, nshuf=20):
    texts = [t for t in texts if nsig(t) >= 2]
    real = np.array([G.accepts(t) for t in texts], float)
    sh = np.array([[G.accepts(shuffled(t, rng)) for t in texts] for _ in range(nshuf)], float).mean(1)
    p = (np.sum(sh >= real.mean()) + 1) / (nshuf + 1)
    out = dict(n=len(texts), coverage=float(real.mean()), shuffle_mean=float(sh.mean()), shuffle_sd=float(sh.std()),
               z=float((real.mean() - sh.mean()) / (sh.std() + 1e-9)), p=float(p))
    print(f"(a) {label:45s} n={out['n']:4d} coverage {out['coverage']:.3f}  shuffled {out['shuffle_mean']:.3f}±{out['shuffle_sd']:.3f}  z={out['z']:.1f}")
    return out


# ---------------------------------------------------------------- ICIT test sets
icit = icit_texts()
icit_new, icit_foreign = [], []
seen = set()
for t in icit:
    k = " ".join(t["seq"])
    if k in seen: continue
    seen.add(k)
    m = dict(t, seq=bridge_seq(t["seq"]), wseq=t["seq"])
    if t["site"] in FOREIGN_SITES:
        icit_foreign.append(m)
    elif t["site"] not in M77_SITES_ICIT and t["site"] != "Unknown" and " ".join(m["seq"]) not in dev_keys:
        icit_new.append(m)
full_bridged = lambda ts: [t for t in ts if not any(s.startswith("OOV") for s in t["seq"])]
print("ICIT new-site texts", len(icit_new), "fully bridged", len(full_bridged(icit_new)), "foreign", len(icit_foreign))

# ---------------------------------------------------------------- (a) coverage
ho_n = [t for t in ho if t["site"] != "West Asian finds"]
clean = lambda ts: [t for t in ts if not has_break(t)]
R["a_coverage"] = {
    "dev_clean (in-sample, for reference)": coverage(clean(dev_g), "dev clean (in-sample)", 5),
    "heldout_clean": coverage(clean(ho_n), "held-out, no break"),
    "heldout_all_breaks_open": coverage(ho_n, "held-out, all (break edges open)"),
    "heldout_seal": coverage([t for t in clean(ho_n) if t["object_type"] == "seal"], "held-out seals"),
    "heldout_tablet": coverage([t for t in clean(ho_n) if m77_class(t["object_type"]) == "tablet"], "held-out tablets/sealings"),
    "heldout_copper": coverage([t for t in clean(ho_n) if t["object_type"] == "copper tablet"], "held-out copper"),
    "heldout_pottery": coverage([t for t in clean(ho_n) if t["object_type"] == "pottery graffito"], "held-out pottery"),
    "icit_newsites_fullbridged": coverage(clean(full_bridged(icit_new)), "ICIT new sites, fully bridged"),
    "icit_newsites_all_oov_as_noun": coverage(clean(icit_new), "ICIT new sites, OOV=unknown noun"),
    "icit_dholavira_fullbridged": coverage([t for t in clean(full_bridged(icit_new)) if t["site"] == "Dholavira"], "Dholavira, fully bridged"),
    "icit_dholavira_all": coverage([t for t in clean(icit_new) if t["site"] == "Dholavira"], "Dholavira, OOV=unknown noun"),
}
# failures: which sign/role conflicts block parses (held-out)
fail_first = Counter()
for t in clean(ho_n):
    if nsig(t) < 2 or G.accepts(t): continue
    for (r, so, eo) in clean_runs(t):
        for j in range(1, len(r) + 1):
            if not np.isfinite(G.logprob(r[:j], False, True)):
                fail_first[(r[j - 1], j - 1 == 0, j == len(r))] += 1; break
R["a_fail_signs_heldout"] = [(f"{s} first={a} last={b}", n) for (s, a, b), n in fail_first.most_common(15)]
print("    top blocking signs (held-out):", R["a_fail_signs_heldout"][:10])


# ---------------------------------------------------------------- (b) object type
def parse_feats(t, with_cat=True):
    f = Counter()
    lines, ok = G.parse_text(t)
    f["accepted"] = float(ok); f["nlines"] = len(lines)
    for (r, roles, so, eo) in lines:
        if roles is None: continue
        f["len"] += len(r)
        prev = "^"
        for s, ro in zip(r, roles):
            f["R_" + ro] += 1; f["RB_" + prev + ro] += 1; prev = ro
        f["RB_" + prev + "$"] += 1
        if with_cat:
            for c in read_line(r, roles, lex, comps):
                f["L_" + c["label"]] += 1
                if c["label"] in ("CLOSER", "CLOSER(jar)", "DOC-TYPE CLITIC", "POST-CLOSER", "UNIT/MEASURE", "TITLE",
                                  "REGISTER", "TITLE-BLOCK", "NUMBER-NAME", "COUNT+MEASURE", "OPENER", "BRACKETED-FISH CLOSER"):
                    f["LS_" + c["label"] + "_" + "+".join(c["signs"])] += 1   # filler of a functional slot
    return f


def bag_feats(t):
    f = Counter(s for s in t["seq"] if s not in ("|", "#"))
    f["len"] = nsig(t); f["nlines"] = t["seq"].count("|") + 1
    return f


def evaluate_type(train, test, featf, lab_tr, lab_te, classes):
    dv = DictVectorizer()
    Xtr = dv.fit_transform([featf(t) for t in train]); Xte = dv.transform([featf(t) for t in test])
    clf = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(Xtr, lab_tr)
    P = clf.predict_proba(Xte)
    aucs = {}
    for c in classes:
        y = np.array([l == c for l in lab_te])
        if 0 < y.sum() < len(y):
            aucs[c] = float(roc_auc_score(y, P[:, list(clf.classes_).index(c)]))
    pred = clf.classes_[P.argmax(1)]
    return dict(macro_auc=float(np.mean(list(aucs.values()))), auc=aucs, bal_acc=float(balanced_accuracy_score(lab_te, pred))), P, clf


classes = ["seal", "tablet", "copper", "pottery"]
trn = [t for t in dev_g if m77_class(t["object_type"])]
tst = [t for t in ho_n if m77_class(t["object_type"])]
ytr = [m77_class(t["object_type"]) for t in trn]; yte = [m77_class(t["object_type"]) for t in tst]
icit_te = [t for t in icit_new if icit_class(t["type"])]
yic = [icit_class(t["type"]) for t in icit_te]
R["b_objtype"] = {"n_train": len(trn), "n_heldout": len(tst), "n_icit": len(icit_te),
                  "heldout_counts": Counter(yte), "icit_counts": Counter(yic)}
models = {"sign_bag": bag_feats, "parse_roles_only": lambda t: parse_feats(t, False), "parse_roles+slot_fillers": parse_feats,
          "sign_bag+parse": lambda t: bag_feats(t) + parse_feats(t)}
Pstore = {}
for name, ff in models.items():
    rh, Ph, _ = evaluate_type(trn, tst, ff, ytr, yte, classes)
    ri, Pi, _ = evaluate_type(trn, icit_te, ff, ytr, yic, classes)
    Pstore[name] = (Ph, Pi)
    R["b_objtype"][name] = {"heldout": rh, "icit_newsites": ri}
    print(f"(b) {name:26s} held-out macroAUC {rh['macro_auc']:.3f} balacc {rh['bal_acc']:.3f} {({k: round(v, 3) for k, v in rh['auc'].items()})} | ICIT macroAUC {ri['macro_auc']:.3f} balacc {ri['bal_acc']:.3f}")
# paired bootstrap: parse(slot fillers) vs sign bag on held-out macro AUC
def boot_diff(a, b, y, B=1000):
    y = np.array(y); out = []
    ci = {c: i for i, c in enumerate(sorted(set(ytr)))}
    for _ in range(B):
        idx = nrng.integers(0, len(y), len(y)); yy = y[idx]; d = []
        for c in classes:
            t = yy == c
            if 0 < t.sum() < len(t):
                d.append(roc_auc_score(t, a[idx, ci[c]]) - roc_auc_score(t, b[idx, ci[c]]))
        out.append(np.mean(d))
    out = np.array(out); return float(out.mean()), [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]
for comp_name in ("parse_roles+slot_fillers", "parse_roles_only", "sign_bag+parse"):
    R["b_objtype"][f"delta_{comp_name}_vs_bag_heldout"] = boot_diff(Pstore[comp_name][0], Pstore["sign_bag"][0], yte)
    R["b_objtype"][f"delta_{comp_name}_vs_bag_icit"] = boot_diff(Pstore[comp_name][1], Pstore["sign_bag"][1], yic)
    print(f"    delta macroAUC {comp_name} - bag: held-out {R['b_objtype'][f'delta_{comp_name}_vs_bag_heldout']}, ICIT {R['b_objtype'][f'delta_{comp_name}_vs_bag_icit']}")
# null for roles-only: permute labels on train
null = []
for _ in range(30):
    yp = list(ytr); rng.shuffle(yp)
    null.append(evaluate_type(trn, tst, lambda t: parse_feats(t, False), yp, yte, classes)[0]["macro_auc"])
R["b_objtype"]["roles_only_label_perm_null"] = [float(np.mean(null)), float(np.percentile(null, 95))]
print("    roles-only null macroAUC", R["b_objtype"]["roles_only_label_perm_null"])

# ---------------------------------------------------------------- (c) masked-sign prediction
bg = KNBigram().fit([r for t in dev_g for r in runs(t["seq"])])
vocab = sorted({s for t in dev_g for s in t["seq"] if s not in ("|", "#")})
uni = Counter(s for t in dev_g for s in t["seq"] if s not in ("|", "#"))
Emat = np.array([G.emis_vec(s) for s in vocab])     # V x K
role_of = {s: max(lex[s]["roles"], key=lambda r: G.role_tot[RI[r]]) if s in lex else "N" for s in vocab}


def grammar_mask_scores(r, i):
    K = len(ROLES)
    a = G.start.copy() if i == 0 else None
    if i > 0:
        a = G.start * G.emis_vec(r[0]); a /= a.sum()
        for s in r[1:i]:
            a = (a @ G.trans) * G.emis_vec(s); a /= max(a.sum(), 1e-300)
        a = a @ G.trans
    b = G.end.copy()
    for s in reversed(r[i + 1:]):
        b = G.trans @ (G.emis_vec(s) * b); b /= max(b.sum(), 1e-300)
    return np.log((Emat * (a * b)[None, :]).sum(1) + 1e-300)


def bigram_mask_scores(r, i):
    prev = r[i - 1] if i > 0 else "<s>"; nxt = r[i + 1] if i + 1 < len(r) else "</s>"
    return np.array([math.log(bg.p(c, prev)) + math.log(bg.p(nxt, c)) for c in vocab])


uni_sc = np.log(np.array([uni[s] for s in vocab], float))
ranks = defaultdict(list); role_hits = defaultdict(list)
tests = [r for t in clean(ho_n) for r in runs(t["seq"]) if len(r) >= 3]
for r in tests:
    for i in range(len(r)):
        true = r[i]
        if true not in vocab: continue
        sc = {"unigram": uni_sc, "grammar": grammar_mask_scores(r, i), "bigram": bigram_mask_scores(r, i)}
        sc["grammar+bigram (fixed 1:1 log-linear)"] = sc["grammar"] + sc["bigram"]
        ti = vocab.index(true)
        for k, v in sc.items():
            rank = 1 + int(np.sum(v > v[ti])); ranks[k].append(rank)
            role_hits[k].append(role_of[vocab[int(np.argmax(v))]] == role_of[true])
R["c_masked"] = {"n_positions": len(ranks["bigram"]), "n_runs": len(tests)}
for k in ranks:
    rk = np.array(ranks[k])
    R["c_masked"][k] = dict(MRR=float(np.mean(1 / rk)), top1=float(np.mean(rk == 1)), top10=float(np.mean(rk <= 10)),
                            median_rank=float(np.median(rk)), role_of_top1_correct=float(np.mean(role_hits[k])))
    print(f"(c) {k:38s} MRR {R['c_masked'][k]['MRR']:.3f} top1 {R['c_masked'][k]['top1']:.3f} top10 {R['c_masked'][k]['top10']:.3f} median rank {R['c_masked'][k]['median_rank']:.0f}  role(top1) {R['c_masked'][k]['role_of_top1_correct']:.3f}")
# paired comparison grammar+bigram vs bigram
d = 1 / np.array(ranks["grammar+bigram (fixed 1:1 log-linear)"]) - 1 / np.array(ranks["bigram"])
bs = [np.mean(d[nrng.integers(0, len(d), len(d))]) for _ in range(2000)]
R["c_masked"]["delta_MRR_combo_vs_bigram"] = [float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
print("    delta MRR (grammar+bigram) - bigram:", R["c_masked"]["delta_MRR_combo_vs_bigram"])
# role prediction: grammar posterior role at the masked slot vs majority role
# slot-role prediction: role posterior at the masked slot (grammar) vs role of bigram's top candidate,
# scored against the role the full-text Viterbi parse gives the true sign. Only parsable runs.
racc = defaultdict(list)
maj = Counter(r for t in dev_g if not has_break(t) for (rr, a_, b_) in clean_runs(t) for r in (G.viterbi(rr) or [])).most_common(1)[0][0]
for r in tests:
    vit = G.viterbi(r)
    if vit is None: continue
    for i in range(len(r)):
        K = len(ROLES)
        if i == 0: a = G.start.copy()
        else:
            a = G.start * G.emis_vec(r[0]); a /= max(a.sum(), 1e-300)
            for s_ in r[1:i]:
                a = (a @ G.trans) * G.emis_vec(s_); a /= max(a.sum(), 1e-300)
            a = a @ G.trans
        b = G.end.copy()
        for s_ in reversed(r[i + 1:]):
            b = G.trans @ (G.emis_vec(s_) * b); b /= max(b.sum(), 1e-300)
        racc["grammar_role_posterior"].append(ROLES[int(np.argmax(a * b))] == vit[i])
        bsc = bigram_mask_scores(r, i)
        racc["bigram_top_candidate_role"].append(role_of[vocab[int(np.argmax(bsc))]] == vit[i])
        racc["majority_role"].append(vit[i] == maj)
R["c_masked"]["slot_role_accuracy"] = {k: float(np.mean(v)) for k, v in racc.items()}
R["c_masked"]["slot_role_n"] = len(racc["majority_role"])
print("    slot-role accuracy:", R["c_masked"]["slot_role_accuracy"], "n", R["c_masked"]["slot_role_n"])

# ---------------------------------------------------------------- (d) foreign detection
def per_sign_bits(t, model):
    tot, n = 0.0, 0
    for (r, so, eo) in clean_runs(t):
        if model == "grammar":
            lp = G.logprob(r, so, eo)
            if not np.isfinite(lp): lp = G.logprob(r, True, True) - 10  # penalty for parse failure
            if not np.isfinite(lp): lp = -15.0 * (len(r) + 1)            # unparsable even with open edges
        else:
            lp = bg.logprob(r)
        tot += -lp; n += len(r) + 1
    return tot / max(n, 1)


def auc_perm(scores, y, B=2000):
    scores = np.array(scores); y = np.array(y)
    obs = roc_auc_score(y, scores)
    null = [roc_auc_score(nrng.permutation(y), scores) for _ in range(B)]
    return float(obs), float((np.sum(np.array(null) >= obs) + 1) / (B + 1))


def foreign_block(native, foreign, label):
    ts = native + foreign; y = [0] * len(native) + [1] * len(foreign)
    out = {"n_native": len(native), "n_foreign": len(foreign)}
    out["parse_failure"] = auc_perm([0.0 if G.accepts(t) else 1.0 for t in ts], y)
    out["fail_rate_foreign"] = float(np.mean([not G.accepts(t) for t in foreign]))
    out["fail_rate_native"] = float(np.mean([not G.accepts(t) for t in native]))
    gb = [per_sign_bits(t, "grammar") for t in ts]; bb = [per_sign_bits(t, "bigram") for t in ts]
    out["grammar_bits"] = auc_perm(gb, y); out["bigram_bits"] = auc_perm(bb, y)
    out["grammar_minus_bigram"] = auc_perm(list(np.array(gb) - np.array(bb)), y)
    # structural flags from the parse: no closer at end, closer not final, no opener, numeral without head
    def flags(t):
        lines, ok = G.parse_text(t); f = 0
        for (r, roles, so, eo) in lines:
            if roles and roles[-1] not in "JPBU": f += 1
        return f + (0 if ok else 2)
    out["structural_flags"] = auc_perm([flags(t) for t in ts], y)
    print(f"(d) {label}: n {len(native)}/{len(foreign)}  parse-fail {out['fail_rate_native']:.2f} vs {out['fail_rate_foreign']:.2f} AUC {out['parse_failure'][0]:.2f} p={out['parse_failure'][1]:.3f} | grammar bits AUC {out['grammar_bits'][0]:.2f} p={out['grammar_bits'][1]:.3f} | bigram bits AUC {out['bigram_bits'][0]:.2f} p={out['bigram_bits'][1]:.3f} | flags AUC {out['structural_flags'][0]:.2f}")
    return out


R["d_foreign"] = {}
ho_wa = [t for t in ho if t["site"] == "West Asian finds" and nsig(t) >= 2]
ho_nat = [t for t in ho_n if nsig(t) >= 2]
R["d_foreign"]["m77_heldout"] = foreign_block(ho_nat, ho_wa, "M77 held-out West Asian vs native")
fround = [t for t in icit_foreign if (t["type"].startswith("SEAL:R") or t["type"].startswith("SEAL:C")) and nsig(t) >= 2]
fall = [t for t in icit_foreign if nsig(t) >= 2]
nat_icit = [t for t in icit_new if nsig(t) >= 2]
R["d_foreign"]["icit_all_foreign_vs_newsite_native"] = foreign_block(nat_icit, fall, "ICIT foreign (all) vs new-site native")
R["d_foreign"]["icit_round_foreign_vs_newsite_native"] = foreign_block(nat_icit, [t for t in fround if nsig(t) >= 2], "ICIT foreign round/cyl vs new-site native")
R["d_foreign"]["foreign_texts"] = [(t["site"], t["type"], " ".join(t["seq"]), bool(G.accepts(t))) for t in fall]

json.dump(R, open(OUT / "g2_tests.json", "w"), indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o))
