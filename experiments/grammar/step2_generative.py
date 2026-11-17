"""Step 2 (dev only): the generative model around the classes from step 1.

  - pooled class grammar refitted on dev with the step-1 assignment (fixed)
  - coarse functional transition table (classes collapsed to their functional label)
  - register offsets (seal, sealing, tablet, copper, pottery, other): shrinkage strengths beta/gamma by
    5-fold family CV on dev; per-register CV gain in bits
  - length model: P(length | face area) for square ICIT seals with dimensions (dev-like ICIT set),
    shifted negative binomial with log mean linear in log2(area); CV gain over the area-free model;
    and per-register length distributions on M77 dev complete texts
Writes grammar.json (the deliverable) and step2.json.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glib import *  # noqa
from scipy import optimize, stats

LOG = open(HERE / "step2.log", "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


C = json.load(open(HERE / "classes_m77.json"))
K, ALPHA = C["K"], C["alpha"]
ASSIGN = {w: c for w, c in zip(C["words"], C["cls"])}
LAB = C["class_labels"]
dev = m77_units("dev")
G = ClassBigram(K, alpha=ALPHA).fit_fixed(dev, ASSIGN, default=ASSIGN[UNK])
R = {}

# ---------------------------------------------------------------- coarse functional table
labs_used = [l for l in LABELS if l in LAB]
idx = {l: i for i, l in enumerate(labs_used)}
nL = len(labs_used)
F = np.zeros((nL + 1, nL + 1))
for c1 in range(K + 1):
    for c2 in range(K + 1):
        a = nL if c1 == K else idx[LAB[c1]]
        b = nL if c2 == K else idx[LAB[c2]]
        F[a, b] += G.M[c1, c2]
Fp = F / F.sum(1, keepdims=True)
R["functional_states"] = labs_used
R["functional_counts"] = F.tolist()
R["functional_T"] = Fp.tolist()
log("functional transition table P(next | current) on dev (rows: current; last row BOS, last col EOS)")
log("            " + " ".join(f"{l[:7]:>8s}" for l in labs_used) + "      EOS")
for i, l in enumerate(labs_used + ["BOS"]):
    log(f"{l[:11]:11s} " + " ".join(f"{Fp[i, j]:8.2f}" for j in range(nL + 1)))

# coarse grammar (states = functional labels) as a model, for reference perplexity
coarse_assign = {w: idx[LAB[c]] for w, c in ASSIGN.items()}

# ---------------------------------------------------------------- register offsets
folds = family_folds(dev, 5, 0)
grid = [(5, 5), (20, 20), (50, 50), (20, 100), (100, 20), (200, 200)]
res = {}
for beta, gamma in [(None, None)] + grid:
    lp = n = 0; per = defaultdict(lambda: [0.0, 0])
    for f in range(5):
        tr = [u for u, g in zip(dev, folds) if g != f]
        te = [u for u, g in zip(dev, folds) if g == f and u["full"]]
        base = ClassBigram(K, alpha=ALPHA).fit_fixed(tr, ASSIGN, default=ASSIGN[UNK])
        m = base if beta is None else RegisterGrammar(base, beta, gamma).fit(tr)
        for u in te:
            a, k = m.unit_logp(u); lp += a; n += k
            per[u["register"]][0] += a; per[u["register"]][1] += k
    res[str((beta, gamma))] = dict(bits=-lp / n, per={r: -v[0] / v[1] for r, v in per.items()},
                                   n={r: v[1] for r, v in per.items()})
    log(f"register beta={beta} gamma={gamma}: CV {-lp/n:.4f} bits/event  " +
        " ".join(f"{r}:{-v[0]/v[1]:.3f}" for r, v in sorted(per.items())))
best = min((k for k in res if k != "(None, None)"), key=lambda k: res[k]["bits"])
beta, gamma = eval(best)
log(f"chosen register shrinkage beta={beta} gamma={gamma}; pooled {res['(None, None)']['bits']:.4f} -> {res[best]['bits']:.4f}")
R["register_cv"] = res
R["register_beta_gamma"] = [beta, gamma]
RG = RegisterGrammar(G, beta, gamma).fit(dev)
gain = {r: res["(None, None)"]["per"][r] - res[best]["per"][r] for r in res[best]["per"]}
R["register_gain_bits"] = gain

# describe offsets: KL of each register's transition rows from pooled, and top emission shifts
offsets = {}
for r, D in RG.reg.items():
    w = D["M"].sum(1); w = w / max(w.sum(), 1)
    kl = float(sum(w[i] * np.sum(D["T"][i] * np.log2(D["T"][i] / G.T[i])) for i in range(K + 1)))
    lift = D["E"] / np.maximum(G.emit, 1e-12)
    rawn = Counter(x for u in dev if u["register"] == r for run, _, _ in u["runs"] for x in mapv(run, G.vocab))
    top = sorted([(G.words[i], float(lift[i]), rawn[G.words[i]]) for i in range(len(G.words)) if rawn[G.words[i]] >= 3],
                 key=lambda x: -x[1])[:8]
    # functional-level start / end shifts
    startF = Counter(); endF = Counter()
    for u in dev:
        if u["register"] != r or not u["full"]:
            continue
        t = mapv(u["runs"][0][0], G.vocab)
        startF[LAB[G.cls_of[t[0]]]] += 1; endF[LAB[G.cls_of[t[-1]]]] += 1
    nS = sum(startF.values()) or 1
    offsets[r] = dict(n_texts=D["n_texts"], transition_KL_bits=kl, cv_gain_bits=gain.get(r),
                      enriched_signs=[dict(sign=a, lift=round(b, 2), dev_tokens=c) for a, b, c in top],
                      start_label_share={k: v / nS for k, v in startF.items()},
                      end_label_share={k: v / nS for k, v in endF.items()})
    log(f"  {r:8s} n={D['n_texts']:4d} KL={kl:.3f} gain={gain.get(r, float('nan')):+.3f}  enriched: " +
        ", ".join(f"{a}x{b:.1f}" for a, b, c in top[:6]))
R["register_offsets"] = offsets

# ---------------------------------------------------------------- length
lens = defaultdict(Counter)
for u in dev:
    if u["full"]:
        lens[u["register"]][len(u["runs"][0][0])] += 1
R["length_by_register_m77_dev"] = {r: dict(sorted(c.items())) for r, c in lens.items()}
for r, c in sorted(lens.items()):
    n = sum(c.values()); m = sum(k * v for k, v in c.items()) / n
    log(f"length {r:8s} n={n:4d} mean {m:.2f}  dist " + " ".join(f"{k}:{v}" for k, v in sorted(c.items())))

ho = m77_units("heldout")
wl = icit_devlike(ho)
S = [u for u in wl if u["register"] == "seal" and u["full"] and u["width"] > 0 and u["height"] > 0]
L = np.array([len(u["signs"]) for u in S]); A = np.log2(np.array([u["width"] * u["height"] for u in S]))
A0 = A.mean()
log(f"seals with dimensions (dev-like ICIT, complete): {len(S)}; mean length {L.mean():.2f}; area median {np.median(2**A):.0f} mm2")


def nb_nll(p, y, x):
    a, b, lr = p
    mu = np.exp(a + b * (x - A0)); r = np.exp(lr)
    return -stats.nbinom.logpmf(y - 1, r, r / (r + mu)).sum()


def fit_nb(y, x, use_area=True):
    f = (lambda p: nb_nll(p, y, x)) if use_area else (lambda p: nb_nll([p[0], 0.0, p[1]], y, x))
    p0 = [np.log(max(y.mean() - 1, 0.1)), 0.3, 1.0] if use_area else [np.log(max(y.mean() - 1, 0.1)), 1.0]
    o = optimize.minimize(f, p0, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-6, fatol=1e-8))
    p = o.x if use_area else np.array([o.x[0], 0.0, o.x[1]])
    return p, o.fun


p1, nll1 = fit_nb(L, A, True)
p0, nll0 = fit_nb(L, A, False)
fam = families(S); fids = sorted(set(fam)); rng = random.Random(0); rng.shuffle(fids)
fold = {f: i % 5 for i, f in enumerate(fids)}
cvg = 0.0
for k in range(5):
    tr = np.array([fold[f] != k for f in fam]); te = ~tr
    q1, _ = fit_nb(L[tr], A[tr], True); q0, _ = fit_nb(L[tr], A[tr], False)
    cvg += nb_nll(q0, L[te], A[te]) - nb_nll(q1, L[te], A[te])
bs = []
rs = np.random.default_rng(0)
byf = defaultdict(list)
for i, f in enumerate(fam):
    byf[f].append(i)
fl = list(byf)
for _ in range(300):
    ii = [i for f in rs.choice(len(fl), len(fl)) for i in byf[fl[f]]]
    q, _ = fit_nb(L[ii], A[ii], True); bs.append(q[1])
mu_med = np.exp(p1[0]) + 1
slope_signs = (np.exp(p1[0] + p1[1] * 1) - np.exp(p1[0])) / 1
log(f"length ~ 1 + NegBin(mu = exp(a + b*(log2 area - {A0:.2f})), r): a={p1[0]:.3f} b={p1[1]:.3f} "
    f"(95% CI {np.quantile(bs,.025):.3f}..{np.quantile(bs,.975):.3f}) r={np.exp(p1[2]):.2f}; "
    f"mean length at median area {mu_med:.2f}; +{slope_signs:.2f} signs per area doubling at the median")
log(f"  CV log-lik gain of area over no-area: {cvg:.1f} nats over {len(S)} seals; in-sample LR {2*(nll0-nll1):.1f} (1 df)")
R["length_model"] = dict(form="length = 1 + NegBin(mean=exp(a + b*(log2(width*height mm2) - c)), size=r)",
                         a=float(p1[0]), b=float(p1[1]), b_ci95=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
                         c=float(A0), r=float(np.exp(p1[2])), n=len(S), cv_gain_nats=float(cvg),
                         lr_chi2=float(2 * (nll0 - nll1)), signs_per_doubling_at_median=float(slope_signs),
                         mean_len_at_median_area=float(mu_med))

# ---------------------------------------------------------------- grammar.json (deliverable)
SC = list(csv.DictReader(open(HERE / "sign_classes.csv")))
S1 = json.load(open(HERE / "step1.json"))
classes = []
for c in range(K):
    mem = sorted([(G.words[i], float(G.emit[i])) for i in range(len(G.words)) if G.cls[i] == c], key=lambda x: -x[1])
    classes.append(dict(id=c, label=LAB[c], emissions={w: round(p, 5) for w, p in mem},
                        start_prob=float(G.T[K, c]), end_prob=float(G.T[c, K]),
                        positional_profile=dict(zip(["initial", "medial", "final", "alone"], C["class_info"]["profile"][c]))))
grammar = dict(
    description="Positional class grammar of Indus texts (M77 sign list), fitted on dev (dev_heldout v2). "
                "P(text) = P(c1|BOS) P(s1|c1) prod P(c_i|c_{i-1}) P(s_i|c_i) P(EOS|c_L). Signs seen once in dev "
                "are emitted as <UNK>. No phonetic values.",
    sign_list="M77", K=K, alpha=ALPHA, unk_class=int(ASSIGN[UNK]),
    classes=classes,
    transitions=dict(rows=[f"c{c}" for c in range(K)] + ["BOS"], cols=[f"c{c}" for c in range(K)] + ["EOS"],
                     P=np.round(G.T, 5).tolist()),
    functional=dict(states=labs_used, rows=labs_used + ["BOS"], cols=labs_used + ["EOS"],
                    P=np.round(Fp, 4).tolist(), counts=F.tolist()),
    sign_classes={r["sign"]: dict(final_class=r["final_class"], raw_label=r["label_raw"], fine_class=r["fine_class"],
                                  confidence=float(r["confidence"]), confidence_kind=r["confidence_kind"],
                                  wells_check=r["wells_check"], dev_tokens=int(r["dev_tokens"])) for r in SC},
    kept_functional_classes=S1["kept_labels"],
    registers=dict(beta=beta, gamma=gamma, offsets=offsets,
                   T={r: np.round(D["T"], 5).tolist() for r, D in RG.reg.items()}),
    length=R["length_model"], length_by_register_m77_dev=R["length_by_register_m77_dev"],
    wells=dict(K=S1["K_wells"], alpha=S1["alpha_wells"], file="classes_wells.json"),
)
json.dump(grammar, open(HERE / "grammar.json", "w"), indent=1)
json.dump(R, open(HERE / "step2.json", "w"), indent=1, default=float)
log("wrote grammar.json, step2.json")
