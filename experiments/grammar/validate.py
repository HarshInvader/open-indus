"""Pre-registered validations of the positional grammar (docs/prereg/grammar.md).

    .venv/bin/python -I experiments/grammar/validate.py dry     # pipeline check on dev only (no held-out,
                                                                # no Gulf, no ICIT-only, no Ur III test split)
    .venv/bin/python -I experiments/grammar/validate.py final   # the registered run

(a) per-sign perplexity on held-out families vs KN bigram, position-only, unigram, shuffled baselines; AIC/BIC
(b) masked restoration: top-5 sign identity, fine-class top-1/top-5, functional label top-1
(c) transfer: MD -> Harappa and small sites; M77 -> ICIT-only sites
(d) negative control: Gulf round seals vs length-matched native Indus seals (Wells grammar)
(e) positive control: the same pipeline on Ur III seal legends recovers slot structure
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glib import *  # noqa

MODE = sys.argv[1] if len(sys.argv) > 1 else "dry"
assert MODE in ("dry", "final")
OUT = HERE / ("validate_dry.json" if MODE == "dry" else "validate_final.json")
LOG = open(HERE / f"validate_{MODE}.log", "w")
t0 = time.time()
RNG = np.random.default_rng(2026)
R = dict(mode=MODE)


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


C = json.load(open(HERE / "classes_m77.json"))
CW = json.load(open(HERE / "classes_wells.json"))
K, ALPHA = C["K"], C["alpha"]
KW, ALPHAW = CW["K"], CW["alpha"]
ASSIGN = {w: c for w, c in zip(C["words"], C["cls"])}
LAB = C["class_labels"]
SC = {r["sign"]: r for r in csv.DictReader(open(HERE / "sign_classes.csv"))}
sys.path.insert(0, str(HERE))
from step1_classes_seeds import SEED_M, SEED_W  # noqa: E402

dev_all = m77_units("dev")
if MODE == "dry":
    f0 = family_folds(dev_all, 4, 7)
    TRAIN = [u for u, g in zip(dev_all, f0) if g != 0]
    TEST = [u for u, g in zip(dev_all, f0) if g == 0]
else:
    TRAIN = dev_all
    TEST = m77_units("heldout")
TEST_FULL = [u for u in TEST if u["full"]]
log(f"mode={MODE}: train {len(TRAIN)} texts, test {len(TEST)} ({len(TEST_FULL)} complete)")


def fam_boot_diff(per_a, per_b, units, B=2000):
    """bootstrap over families of the test set: CI of bits/event(a) - bits/event(b)"""
    fam = families(units)
    byf = defaultdict(list)
    for i, f in enumerate(fam):
        byf[f].append(i)
    fl = list(byf)
    a = np.array([x[0] for x in per_a]); b = np.array([x[0] for x in per_b]); n = np.array([x[1] for x in per_a])
    obs = a.sum() / n.sum() - b.sum() / n.sum()
    ds = []
    for _ in range(B):
        ii = np.concatenate([byf[fl[j]] for j in RNG.integers(0, len(fl), len(fl))])
        ds.append(a[ii].sum() / n[ii].sum() - b[ii].sum() / n[ii].sum())
    return float(obs), [float(np.quantile(ds, .025)), float(np.quantile(ds, .975))], float(np.mean(np.array(ds) >= 0))


def grammar_on(units, seeds=SEED_M, K_=K, a_=ALPHA):
    return ClassBigram(K_, alpha=a_).fit(units, init=seeds, restarts=5)


# ======================================================================= (a) perplexity
log("\n== (a) per-sign perplexity (bits per event = signs + end-of-text), complete test texts")
G = ClassBigram(K, alpha=ALPHA).fit_fixed(TRAIN, ASSIGN, default=ASSIGN[UNK]) if MODE == "final" else grammar_on(TRAIN)
KN = KNBigram().fit(TRAIN)
POS = PositionModel().fit(TRAIN)
UNI = Unigram().fit(TRAIN)
GS = grammar_on(shuffle_units(TRAIN, 1))
labs_t, _ = name_classes(G, TRAIN)
coarse = {w: LABELS.index(labs_t[c]) for w, c in G.cls_of.items()}
GC = ClassBigram(len(LABELS), alpha=ALPHA).fit_fixed(TRAIN, coarse, default=LABELS.index("unclassified"))
GR = RegisterGrammar(G, *json.load(open(HERE / "step2.json"))["register_beta_gamma"]).fit(TRAIN)
models = dict(grammar=G, kn_bigram=KN, position=POS, unigram=UNI, grammar_shuffled_train=GS,
              grammar_functional7=GC, grammar_registers=GR)
A = {}
per = {}
for name, m in models.items():
    b, n, p = bits(m, TEST_FULL)
    per[name] = p
    ab = aic_bic(m, TRAIN) if hasattr(m, "n_params") else {}
    A[name] = dict(bits=b, perplexity=2 ** b, n_events=n, **{k: v for k, v in ab.items() if k in ("k", "AIC", "BIC")})
    log(f"  {name:24s} {b:.3f} bits/event (ppl {2**b:6.1f})  k={ab.get('k', '-')}  AIC={ab.get('AIC', float('nan')):.0f} BIC={ab.get('BIC', float('nan')):.0f}")
shuf = []
for s in range(20):
    b, _, _ = bits(G, shuffle_units(TEST_FULL, 100 + s)); shuf.append(b)
A["grammar_on_shuffled_test"] = dict(bits=float(np.mean(shuf)), sd=float(np.std(shuf)))
log(f"  grammar on shuffled test texts: {np.mean(shuf):.3f} +- {np.std(shuf):.3f}")
for base in ("kn_bigram", "position", "unigram", "grammar_shuffled_train"):
    d, ci, pge = fam_boot_diff(per["grammar"], per[base], TEST_FULL)
    A[f"diff_vs_{base}"] = dict(diff=d, ci95=ci, p_boot_ge0=pge)
    log(f"  grammar - {base:22s} {d:+.3f} bits [95% CI {ci[0]:+.3f}, {ci[1]:+.3f}]")
d, ci, _ = fam_boot_diff(per["grammar_registers"], per["grammar"], TEST_FULL)
A["diff_registers_vs_pooled"] = dict(diff=d, ci95=ci)
log(f"  register-aware - pooled grammar: {d:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]")
A["pass_a"] = bool(A["diff_vs_kn_bigram"]["ci95"][1] < 0 and A["grammar"]["k"] < A["kn_bigram"]["k"])
A["pass_a_vs_position_shuffled"] = bool(A["diff_vs_position"]["ci95"][1] < 0 and A["diff_vs_grammar_shuffled_train"]["ci95"][1] < 0)
log(f"  PASS (a) beats bigram with fewer parameters: {A['pass_a']}; beats position-only and shuffled: {A['pass_a_vs_position_shuffled']}")
R["a_perplexity"] = A

# ======================================================================= (b) masked restoration
log("\n== (b) masked restoration (one hidden sign, complete test texts of 2+ signs, every position)")
vocab_words = [w for w in G.words if w != UNK]
vi = [G.widx[w] for w in vocab_words]
cls_arr = np.array([G.cls[i] for i in vi])
lab_arr = np.array([labs_t[c] for c in cls_arr])
final_lab = {w: SC[w]["final_class"] if w in SC else "unclassified" for w in vocab_words}
recs = defaultdict(list)
for ti, u in enumerate(TEST_FULL):
    toks = list(u["runs"][0][0])
    if len(toks) < 2:
        continue
    for j in range(len(toks)):
        true = toks[j]
        sc = {"grammar": G.fill_scores(toks, j)[vi],
              "kn_bigram": KN.fill_scores(toks, j, cands=vocab_words),
              "position": POS.fill_scores(toks, j, cands=vocab_words),
              "unigram": UNI.fill_scores(toks, j, cands=vocab_words)}
        tc = G.cls_of.get(true if true in G.vocab else UNK)
        tlab = labs_t[tc]
        tfinal = SC[true]["final_class"] if true in SC else "unclassified"
        for name, s in sc.items():
            order = np.argsort(-s)
            top5 = [vocab_words[k] for k in order[:5]]
            rank = (np.where(np.array(vocab_words)[order] == true)[0][0] + 1) if true in G.vocab and true != UNK else None
            p = np.exp2(s - s.max()); p /= p.sum()
            cp = np.bincount(cls_arr, weights=p, minlength=K)
            corder = np.argsort(-cp)
            lp = Counter()
            for L_, pp in zip(lab_arr, p):
                lp[L_] += pp
            recs[name].append(dict(t=ti, top5=true in top5, rr=1 / rank if rank else 0.0,
                                   c1=int(corder[0] == tc), c5=int(tc in corder[:5]),
                                   lab1=int(max(lp, key=lp.get) == tlab),
                                   fin1=(int(final_lab.get(vocab_words[order[0]], "") == tfinal) if tfinal != "unclassified" else None)))
B_ = {}
for name, rs in recs.items():
    fin = [r["fin1"] for r in rs if r["fin1"] is not None]
    B_[name] = dict(n=len(rs), top5=float(np.mean([r["top5"] for r in rs])), mrr=float(np.mean([r["rr"] for r in rs])),
                    class_top1=float(np.mean([r["c1"] for r in rs])), class_top5=float(np.mean([r["c5"] for r in rs])),
                    label_top1=float(np.mean([r["lab1"] for r in rs])),
                    final_class_top1=float(np.mean(fin)) if fin else None, n_final=len(fin))
    log(f"  {name:10s} n={len(rs)} top5 {B_[name]['top5']:.3f}  MRR {B_[name]['mrr']:.3f}  fine-class top1 {B_[name]['class_top1']:.3f} "
        f"top5 {B_[name]['class_top5']:.3f}  label top1 {B_[name]['label_top1']:.3f}  validated-class top1 {B_[name]['final_class_top1']}")


def text_boot(name_a, name_b, key, B=2000):
    ta = defaultdict(list); tb = defaultdict(list)
    for r in recs[name_a]:
        ta[r["t"]].append(r[key])
    for r in recs[name_b]:
        tb[r["t"]].append(r[key])
    ids = sorted(ta)
    xa = [np.array(ta[i], float) for i in ids]; xb = [np.array(tb[i], float) for i in ids]
    obs = np.concatenate(xa).mean() - np.concatenate(xb).mean()
    ds = []
    for _ in range(B):
        jj = RNG.integers(0, len(ids), len(ids))
        ds.append(np.concatenate([xa[j] for j in jj]).mean() - np.concatenate([xb[j] for j in jj]).mean())
    return float(obs), [float(np.quantile(ds, .025)), float(np.quantile(ds, .975))]


for base in ("kn_bigram", "position", "unigram"):
    for key in ("top5", "lab1"):
        d, ci = text_boot("grammar", base, key)
        B_[f"diff_{key}_vs_{base}"] = dict(diff=d, ci95=ci)
        log(f"  grammar - {base:10s} {key}: {d:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]")
B_["pass_b1"] = bool(B_["diff_top5_vs_position"]["ci95"][0] > 0)
B_["pass_b2"] = bool(B_["diff_top5_vs_kn_bigram"]["ci95"][0] > -0.03)
B_["pass_b3"] = bool(B_["grammar"]["label_top1"] >= 0.6 and B_["diff_lab1_vs_position"]["ci95"][0] > 0)
log(f"  PASS b1 (top5 > position) {B_['pass_b1']}; b2 (top5 non-inferior to bigram, margin 0.03) {B_['pass_b2']}; "
    f"b3 (label top1 >= 0.6 and > position) {B_['pass_b3']}")
R["b_restoration"] = B_


# ======================================================================= (c) transfer
log("\n== (c) transfer")


def transfer(train, targets, label, train_seeds=SEED_M, K_=K, a_=ALPHA, indomain=True):
    g = grammar_on(train, train_seeds, K_, a_); kn = KNBigram().fit(train); pos = PositionModel().fit(train); uni = Unigram().fit(train)
    out = {}
    if indomain:
        fo = family_folds(train, 5, 0); pg = []; pk = []; tu = []
        for f in range(5):
            tr = [u for u, q in zip(train, fo) if q != f]; te = [u for u, q in zip(train, fo) if q == f and u["full"]]
            gg = grammar_on(tr, train_seeds, K_, a_); kk = KNBigram().fit(tr)
            pg += bits(gg, te)[2]; pk += bits(kk, te)[2]; tu += te
        dgi, cii, _ = fam_boot_diff(pg, pk, tu)
        out["in_domain"] = dict(grammar=sum(x[0] for x in pg) / sum(x[1] for x in pg),
                                kn_bigram=sum(x[0] for x in pk) / sum(x[1] for x in pk), diff=dgi, ci95=cii)
        log(f"  [{label}] in-domain CV: grammar {out['in_domain']['grammar']:.3f} bigram {out['in_domain']['kn_bigram']:.3f} diff {dgi:+.3f} [{cii[0]:+.3f},{cii[1]:+.3f}]")
    for tname, tu in targets.items():
        tu = [u for u in tu if u["full"]]
        if len(tu) < 10:
            log(f"  [{label}] {tname}: only {len(tu)} complete texts, skipped"); continue
        r = {}
        pp = {}
        for nm, m in (("grammar", g), ("kn_bigram", kn), ("position", pos), ("unigram", uni)):
            b, n, p = bits(m, tu); r[nm] = b; pp[nm] = p
        d, ci, _ = fam_boot_diff(pp["grammar"], pp["kn_bigram"], tu)
        dp, cip, _ = fam_boot_diff(pp["grammar"], pp["position"], tu)
        r.update(n_texts=len(tu), n_events=n, diff_vs_kn=d, ci95_vs_kn=ci, diff_vs_position=dp, ci95_vs_position=cip,
                 pass_beats_bigram=bool(ci[1] < 0), pass_beats_position=bool(cip[1] < 0))
        if indomain:
            r["gap_change_vs_in_domain"] = d - out["in_domain"]["diff"]
        out[tname] = r
        log(f"  [{label}] {tname:22s} n={len(tu):4d} grammar {r['grammar']:.3f} bigram {r['kn_bigram']:.3f} position {r['position']:.3f} "
            f"unigram {r['unigram']:.3f} | g-bigram {d:+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}] g-position {dp:+.3f}")
    return out


src_pool = TRAIN if MODE == "dry" else m77_units("all")
md = [u for u in src_pool if u["site"] == "Mohenjodaro"]
mdkeys = {u["signs"] for u in md}
tg = {"Harappa": [u for u in src_pool if u["site"] == "Harappa" and u["signs"] not in mdkeys],
      "small_sites": [u for u in src_pool if u["site"] in ("Lothal", "Kalibangan", "Chanhudaro", "Other sites") and u["signs"] not in mdkeys]}
R["c1_md_transfer"] = transfer(md, tg, "MD->")
if MODE == "final":
    allm = m77_units("all")
    icit_new = [bridge_unit(u) for u in icit_units(exclude_sites=M77_OLD_SITES_ICIT | FOREIGN | {"Unknown"})]
    mk = {u["signs"] for u in allm}
    icit_new = [u for u in icit_new if u["signs"] not in mk]
    tg2 = {"ICIT_only_all": icit_new, "ICIT_only_fully_bridged": [u for u in icit_new if u["n_unbridged"] == 0],
           "ICIT_only_seals": [u for u in icit_new if u["register"] == "seal"]}
    R["c2_m77_to_icit"] = transfer(allm, tg2, "M77->ICIT", indomain=True)
c1 = R["c1_md_transfer"]
R["pass_c"] = dict(beats_bigram_all=all(v.get("pass_beats_bigram") for k, v in c1.items() if k != "in_domain") and
                   all(v.get("pass_beats_bigram") for k, v in R.get("c2_m77_to_icit", {}).items() if k != "in_domain"),
                   beats_position_all=all(v.get("pass_beats_position") for k, v in c1.items() if k != "in_domain") and
                   all(v.get("pass_beats_position") for k, v in R.get("c2_m77_to_icit", {}).items() if k != "in_domain"))
log(f"  PASS (c) beats bigram on every target: {R['pass_c']['beats_bigram_all']}; beats position-only on every target: {R['pass_c']['beats_position_all']}")


# ======================================================================= (d) Gulf negative control
log("\n== (d) Gulf round seals vs native Indus seals of equal length (Wells grammar)")
wl = icit_devlike(m77_units("heldout"))
native_seals = [u for u in wl if u["register"] == "seal"]
fo = family_folds(wl, 5, 0)
cvb = {}
cvk = {}
for f in range(5):
    tr = [u for u, q in zip(wl, fo) if q != f]
    gw = grammar_on(tr, SEED_W, KW, ALPHAW); kw = KNBigram().fit(tr)
    for u, q in zip(wl, fo):
        if q == f and u["register"] in ("seal", "round_seal"):
            a, n = gw.unit_logp(u); cvb[u["key"]] = (-a / n, n)
            a, n = kw.unit_logp(u); cvk[u["key"]] = (-a / n, n)
GW = grammar_on(wl, SEED_W, KW, ALPHAW); KWB = KNBigram().fit(wl)


def matched(test_units, scorer, ref_units, ref_scores, label, ndraw=10000):
    key = lambda u: (min(len(u["signs"]), 6), u["full"])
    byk = defaultdict(list)
    for u in ref_units:
        if u["key"] in ref_scores:
            byk[key(u)].append(ref_scores[u["key"]][0])
    byk = {k: np.array(v) for k, v in byk.items()}
    tb, keys = [], []
    for u in test_units:
        k = key(u)
        if k not in byk:
            k = (k[0], not k[1])
        a, n = scorer.unit_logp(u); tb.append(-a / n); keys.append(k)
    obs = float(np.mean(tb))
    draws = np.array([np.mean([RNG.choice(byk[k]) for k in keys]) for _ in range(ndraw)])
    p = (1 + (draws >= obs).sum()) / (ndraw + 1)
    allref = np.concatenate([byk[k] for k in set(keys)])
    auc = float(np.mean([(t > r) + 0.5 * (t == r) for t in tb for r in allref]))
    out = dict(n=len(tb), bits=obs, matched_native=float(draws.mean()), diff=obs - float(draws.mean()), p=float(p), auc=auc)
    log(f"  {label:44s} n={len(tb):3d} {obs:.3f} vs matched native {draws.mean():.3f}: diff {out['diff']:+.3f} p={p:.4f} AUC {auc:.2f}")
    return out


D = {}
home_round = [u for u in wl if u["register"] == "round_seal"]
D["home_round_vs_native_grammar"] = matched([u for u in home_round if u["key"] in cvb], type("S", (), {"unit_logp": staticmethod(lambda u: (-cvb[u["key"]][0] * cvb[u["key"]][1], cvb[u["key"]][1]))})(),
                                            native_seals, cvb, "home round seals (CV) vs native square, grammar")
if MODE == "final":
    gulf = [u for u in icit_units(sites=FOREIGN) if u["register"] == "round_seal"]
    gulf_sq = [u for u in icit_units(sites=FOREIGN) if u["register"] == "seal"]
    D["gulf_round_grammar"] = matched(gulf, GW, native_seals, cvb, "Gulf round seals, grammar")
    D["gulf_round_bigram"] = matched(gulf, KWB, native_seals, cvk, "Gulf round seals, KN bigram (reference)")
    D["gulf_square_grammar"] = matched(gulf_sq, GW, native_seals, cvb, "foreign square seals, grammar (secondary)")
    D["pass_d"] = bool(D["gulf_round_grammar"]["diff"] > 0 and D["gulf_round_grammar"]["p"] < 0.01)
    log(f"  PASS (d) Gulf round seals score worse (p<0.01): {D['pass_d']}")
R["d_gulf"] = D


# ======================================================================= (e) Ur III positive control
log("\n== (e) Ur III seal legends: does the same pipeline recover slot structure?")
sys.path.insert(0, str(ROOT / "experiments/genre_alignment"))
import ga_slots  # noqa: E402  (read-only import; tags slots by rule)
T3 = ga_slots.cun_corpus("ur3")
seen = set(); legends = []
for t in T3:
    k = tuple(t["toks"])
    if not k or k in seen:
        continue
    seen.add(k)
    # family = owner name (first word): one owner's several seals/impressions never straddle the split
    legends.append(dict(runs=[(k, True, True)], full=True, signs=k, slots=tuple(t["slots"]), register="seal",
                        key=" ".join(k), fam=k[0]))
fam3 = families(legends)
fids = sorted(set(fam3)); rr = random.Random(3); rr.shuffle(fids)
held_f = set(fids[: len(fids) // 4])
U_tr = [u for u, f in zip(legends, fam3) if f not in held_f]
U_te = [u for u, f in zip(legends, fam3) if f in held_f]
if MODE == "dry":     # dry run never touches the Ur III test families
    fam_tr = families(U_tr); ff = sorted(set(fam_tr)); rr.shuffle(ff); hf = set(ff[: len(ff) // 4])
    U_te = [u for u, f in zip(U_tr, fam_tr) if f in hf]; U_tr = [u for u, f in zip(U_tr, fam_tr) if f not in hf]
rr2 = random.Random(5)
U_tr_small = rr2.sample(U_tr, min(len(dev_all), len(U_tr)))
log(f"  Ur III distinct legends {len(legends)}; train {len(U_tr)} (Indus-size sample {len(U_tr_small)}), test {len(U_te)}; "
    f"mean length {np.mean([len(u['signs']) for u in legends]):.2f} words")


def nmi(a, b):
    from sklearn.metrics import normalized_mutual_info_score
    return float(normalized_mutual_info_score(a, b))


def ur3_pipeline(train, tag, shuffled=False):
    tr = shuffle_units(train, 11) if shuffled else train
    bic = {}
    for Kc in (8, 12, 16, 20, 24, 30):
        m = ClassBigram(Kc, alpha=1.0).fit(tr, restarts=3); bic[Kc] = aic_bic(m, tr)["BIC"]
    Kb = min(bic, key=bic.get)
    fo = family_folds(tr, 5, 0); cv = {}
    for a in (0.3, 1.0, 3.0, 10.0):
        lp = n = 0
        for f in range(5):
            m = ClassBigram(Kb, alpha=a).fit([u for u, q in zip(tr, fo) if q != f], restarts=3)
            b, k, _ = bits(m, [u for u, q in zip(tr, fo) if q == f]); lp += b * k; n += k
        cv[a] = lp / n
    ab = min(cv, key=cv.get)
    m = ClassBigram(Kb, alpha=ab).fit(tr, restarts=5)
    labs, _ = name_classes(m, tr, "UR3")
    return m, labs, Kb, ab


def ur3_eval(m, labs, test):
    pc, gs, lb = [], [], []
    for u in test:
        for w, s in zip(mapv(u["signs"], m.vocab), u["slots"]):
            pc.append(m.cls_of[w]); gs.append(s); lb.append(labs[m.cls_of[w]])
    pc = np.array(pc); gs = np.array(gs)
    maj = {}
    for c in set(pc):
        maj[c] = Counter(gs[pc == c]).most_common(1)[0][0]
    purity = float(np.mean([maj[c] == s for c, s in zip(pc, gs)]))
    iso = {}
    for slot in ("KIN", "SERV", "TITLE", "OWNER", "FATHER", "LORD"):
        idx = gs == slot
        if idx.sum() >= 20:
            iso[slot] = float(np.mean([maj[c] == slot for c in pc[idx]]))
    tab = defaultdict(Counter)
    for s, l in zip(gs, lb):
        tab[s][l] += 1
    return dict(nmi=nmi(pc, gs), purity=purity, isolation=iso,
                slot_x_label={s: dict(c) for s, c in tab.items()}, n_tokens=len(gs))


E = {}
for tag, tr in (("indus_size", U_tr_small), ("full_train", U_tr)):
    m, labs, Kb, ab = ur3_pipeline(tr, tag)
    ev = ur3_eval(m, labs, U_te)
    kn = KNBigram().fit(tr)
    gb, _, pg = bits(m, U_te); kb, _, pk = bits(kn, U_te)
    pos = PositionModel().fit(tr); pb, _, _ = bits(pos, U_te)
    d, ci, _ = fam_boot_diff(pg, pk, U_te)
    ev.update(K=Kb, alpha=ab, class_labels=labs, grammar_bits=gb, kn_bits=kb, position_bits=pb, diff_vs_kn=d, ci95_vs_kn=ci)
    if tag == "indus_size":
        nulls = []
        for s in range(20):
            mn, ln, _, _ = ur3_pipeline(shuffle_units(tr, 200 + s), tag)
            nulls.append(ur3_eval(mn, ln, U_te)["nmi"])
        ev["nmi_null"] = dict(mean=float(np.mean(nulls)), max=float(np.max(nulls)), values=nulls)
        ev["pass_e1"] = bool(ev["nmi"] > max(nulls))
        ev["pass_e2"] = bool(ev["isolation"].get("KIN", 0) >= 0.7 and ev["isolation"].get("SERV", 0) >= 0.7)
        ev["pass_e2_kin"] = bool(ev["isolation"].get("KIN", 0) >= 0.7)
    E[tag] = ev
    log(f"  [{tag}] K={Kb} alpha={ab}: NMI(class, gold slot) {ev['nmi']:.3f}" +
        (f" (shuffled-train null max {ev['nmi_null']['max']:.3f}, mean {ev['nmi_null']['mean']:.3f})" if "nmi_null" in ev else "") +
        f"; purity {ev['purity']:.3f}; isolation " + ", ".join(f"{k} {v:.2f}" for k, v in ev["isolation"].items()))
    log(f"  [{tag}] perplexity: grammar {gb:.3f} vs KN bigram {kb:.3f} (diff {d:+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]) position {pb:.3f}")
    for s in ("OWNER", "TITLE", "KIN", "FATHER", "SERV", "LORD", "EPITHET"):
        if s in ev["slot_x_label"]:
            c = ev["slot_x_label"][s]; n = sum(c.values())
            log(f"     {s:8s} n={n:5d} -> " + ", ".join(f"{k} {v/n:.2f}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])[:4]))
E["pass_e"] = bool(E["indus_size"].get("pass_e1") and E["indus_size"].get("pass_e2"))
log(f"  PASS (e) (e1 NMI above all 20 shuffled-train nulls AND e2 relators isolated >= 0.7): {E['pass_e']}")
R["e_ur3"] = E

R["elapsed_s"] = time.time() - t0
json.dump(R, open(OUT, "w"), indent=1, default=float)
log(f"\nwrote {OUT.name} ({time.time()-t0:.0f}s)")
