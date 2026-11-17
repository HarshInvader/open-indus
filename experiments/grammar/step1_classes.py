"""Step 1 (dev only): induce sign classes, name them, bootstrap them, and cross-check under the Wells list.

  1. K chosen by BIC on dev (alpha=1), alpha then chosen by 5-fold family CV on dev.
  2. Final class grammar on all dev (seeded init + random restarts, best training likelihood).
  3. Bootstrap over dev text families (B runs): per-sign label stability = confidence.
  4. Wells: the same pipeline on ICIT texts at Indus sites with no near-copy in M77 held-out
     (icit_devlike), seeds = Wells numerals/connective. Bridged signs compared.
  5. Final label per sign: kept only if bootstrap stability >= 0.7 AND (Wells label agrees, or the sign
     has no Wells counterpart in the Wells vocabulary -> flagged 'M77 only'). Rare signs (dev count 1,
     modelled as <UNK>) get a context posterior; label kept only if posterior >= 0.9.
  6. A functional class is kept if it occurs under both lists, token-weighted member stability >= 0.7 and
     (token-weighted) bridged agreement for the class >= 0.5 and above the 95th percentile of a label-permutation null.
Outputs: classes_m77.json, classes_wells.json, sign_classes.csv, step1.json
"""
import csv, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glib import *  # noqa

B = int(sys.argv[1]) if len(sys.argv) > 1 else 200
t0 = time.time()
LOG = open(HERE / "step1.log", "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


# seeds from earlier experiments (initialisation only): see step1_classes_seeds.py
from step1_classes_seeds import SEED_M, SEED_W  # noqa: E402


def choose(units, corpus, Kgrid=(8, 12, 16, 20, 24, 30, 40, 50), agrid=(0.3, 1.0, 3.0, 10.0), seed_init=None):
    bic = {}
    for K in Kgrid:
        m = ClassBigram(K, alpha=1.0).fit(units, init=seed_init, restarts=3)
        bic[K] = aic_bic(m, units)
        log(f"  [{corpus}] K={K:3d} k={bic[K]['k']:5d} AIC={bic[K]['AIC']:.0f} BIC={bic[K]['BIC']:.0f}")
    Kb = min(bic, key=lambda k: bic[k]["BIC"])
    folds = family_folds(units, 5, 0)
    cvb = {}
    for a in agrid:
        lp = n = 0
        for f in range(5):
            tr = [u for u, g in zip(units, folds) if g != f]
            te = [u for u, g in zip(units, folds) if g == f]
            m = ClassBigram(Kb, alpha=a).fit(tr, init=seed_init, restarts=3)
            b, k, _ = bits(m, te); lp += b * k; n += k
        cvb[a] = lp / n
        log(f"  [{corpus}] K={Kb} alpha={a}: CV {cvb[a]:.3f} bits/event")
    ab = min(cvb, key=cvb.get)
    return Kb, ab, {str(k): v for k, v in bic.items()}, {str(k): v for k, v in cvb.items()}


def label_signs(model, units, corpus):
    labs, info = name_classes(model, units, corpus)
    return {w: labs[model.cls_of[w]] for w in model.words}, labs, info


def boot(units, K, a, corpus, seed_init, B, seed=1):
    fam = families(units)
    byfam = defaultdict(list)
    for u, f in zip(units, fam):
        byfam[f].append(u)
    fids = sorted(byfam)
    rng = random.Random(seed)
    rec = defaultdict(Counter)
    for b in range(B):
        smp = [u for f in (rng.choice(fids) for _ in fids) for u in byfam[f]]
        m = ClassBigram(K, alpha=a).fit(smp, init=seed_init, restarts=2, seed=b)
        sl, _, _ = label_signs(m, smp, corpus)
        for w, l in sl.items():
            if w != UNK:
                rec[w][l] += 1
        if (b + 1) % 25 == 0:
            log(f"  [{corpus}] bootstrap {b+1}/{B} ({time.time()-t0:.0f}s)")
    return rec


def run(corpus, units, seed_init):
    log(f"== {corpus}: {len(units)} distinct texts, {sum(u['full'] for u in units)} complete")
    K, a, bic, cvb = choose(units, corpus, seed_init=seed_init)
    log(f"  [{corpus}] chosen K={K} (BIC), alpha={a} (CV)")
    m = ClassBigram(K, alpha=a).fit(units, init=seed_init, restarts=5)
    sl, labs, info = label_signs(m, units, corpus)
    rec = boot(units, K, a, corpus, seed_init, B)
    raw = Counter(x for u in units for r, _, _ in u["runs"] for x in r)
    signs = {}
    for w in sorted(raw):
        if w in m.vocab:
            n_b = sum(rec[w].values())
            stab = rec[w][sl[w]] / n_b if n_b else 0.0
            signs[w] = dict(label=sl[w], cls=m.cls_of[w], conf=stab, kind="bootstrap", n=raw[w],
                            boot=dict(rec[w]))
        else:
            agg, n = rare_posterior(m, units, w, labs)
            lab, p = max(agg.items(), key=lambda kv: kv[1])
            signs[w] = dict(label=lab, cls=None, conf=float(p), kind="context-posterior", n=raw[w],
                            post={k: float(v) for k, v in agg.items()})
    return dict(K=K, alpha=a, bic=bic, cv=cvb, class_labels=labs, class_info=info, model=m, signs=signs)


dev = m77_units("dev")
ho = m77_units("heldout")
RM = run("M77", dev, SEED_M)
wl = icit_devlike(ho)
log(f"Wells dev-like set: {len(wl)} ICIT texts (Indus sites, no near-copy of an M77 held-out text)")
RW = run("ICIT", wl, SEED_W)

# ---------------------------------------------------------------- cross-check
def wells_label_for(m):
    """majority Wells label over the W counterparts of an M sign (by Wells token count)"""
    c = Counter()
    for w in M2W.get(m, []):
        if w in RW["signs"] and RW["signs"][w]["kind"] == "bootstrap":
            c[RW["signs"][w]["label"]] += RW["signs"][w]["n"]
    return c.most_common(1)[0][0] if c else None


pairs = []
for m, s in RM["signs"].items():
    if s["kind"] != "bootstrap":
        continue
    wl_ = wells_label_for(m)
    if wl_ is not None:
        pairs.append((m, s["label"], wl_, s["n"]))
log(f"bridged M signs with a Wells label: {len(pairs)}")
agree = np.mean([a == b for _, a, b, _ in pairs])
rng = np.random.default_rng(0)
A = [a for _, a, _, _ in pairs]; Bw = [b for _, _, b, _ in pairs]
null = [np.mean(np.array(A) == rng.permutation(Bw)) for _ in range(2000)]
log(f"overall agreement {agree:.3f} vs permutation mean {np.mean(null):.3f} (95th {np.quantile(null, .95):.3f})")
per_label = {}
for L in LABELS:
    idx = [i for i, (_, a, _, _) in enumerate(pairs) if a == L]
    if not idx:
        per_label[L] = dict(n=0); continue
    obs = np.mean([pairs[i][2] == L for i in idx])
    nl = []
    for _ in range(2000):
        pb = rng.permutation(Bw)
        nl.append(np.mean([pb[i] == L for i in idx]))
    mem = [RM["signs"][pairs[i][0]]["conf"] for i in idx]
    allmem = [s["conf"] for s in RM["signs"].values() if s["kind"] == "bootstrap" and s["label"] == L]
    allw = [s["n"] for s in RM["signs"].values() if s["kind"] == "bootstrap" and s["label"] == L]
    wstab = float(np.average(allmem, weights=allw)) if allw else 0.0
    in_wells = any(s["label"] == L for s in RW["signs"].values() if s["kind"] == "bootstrap")
    keep = bool(in_wells and wstab >= 0.7 and obs >= 0.5 and obs > np.quantile(nl, .95))
    per_label[L] = dict(n_bridged=len(idx), agreement=float(obs), null95=float(np.quantile(nl, .95)),
                        null_mean=float(np.mean(nl)), mean_stability=float(np.mean(allmem)), token_weighted_stability=wstab,
                        n_members=len(allmem), in_wells=in_wells, keep=keep)
    log(f"  {L:12s} bridged {len(idx):3d} agree {obs:.2f} (null95 {np.quantile(nl, .95):.2f}) "
        f"stability {np.mean(allmem):.2f} tokw {wstab:.2f} (n={len(allmem)}) in_wells={in_wells} KEEP={keep}")

kept = {L for L, v in per_label.items() if v.get("keep")}
rows = []
for m, s in sorted(RM["signs"].items(), key=lambda kv: -kv[1]["n"]):
    wl_ = wells_label_for(m) if s["kind"] == "bootstrap" else None
    wsig = ";".join(M2W.get(m, []))
    if s["kind"] == "bootstrap":
        ok = s["conf"] >= 0.7 and (wl_ is None or wl_ == s["label"]) and s["label"] in kept
        wells_check = "n/a" if wl_ is None else ("agree" if wl_ == s["label"] else f"differs:{wl_}")
    else:
        ok = s["conf"] >= 0.9 and s["label"] in kept
        wells_check = "n/a (rare)"
    final = s["label"] if ok else "unclassified"
    rows.append(dict(sign=m, dev_tokens=s["n"], label_raw=s["label"], fine_class=s["cls"], confidence=round(s["conf"], 3),
                     confidence_kind=s["kind"], wells_signs=wsig, wells_label=wl_ or "", wells_check=wells_check,
                     seed=SEED_M.get(m, ""), final_class=final))
with open(HERE / "sign_classes.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

tok = Counter()
for r in rows:
    tok[r["final_class"]] += r["dev_tokens"]
ntok = sum(tok.values())
log("final classes (signs / dev token share):")
for L in LABELS:
    ns = sum(r["final_class"] == L for r in rows)
    log(f"  {L:12s} {ns:4d} signs  {tok[L]/ntok:.3f} of tokens")
seed_agree = np.mean([r["label_raw"] == r["seed"] for r in rows if r["seed"] and r["confidence_kind"] == "bootstrap"])
log(f"agreement of induced label with seed label (frequent signs): {seed_agree:.3f}")


def dump(R, name, corpus):
    m = R["model"]
    out = dict(corpus=corpus, K=R["K"], alpha=R["alpha"], words=m.words, cls=[int(c) for c in m.cls],
               class_labels=R["class_labels"], T=m.T.tolist(), emit=m.emit.tolist(), pc=m.pc.tolist(),
               bic=R["bic"], cv=R["cv"], class_info=R["class_info"],
               signs={k: {kk: vv for kk, vv in v.items()} for k, v in R["signs"].items()})
    json.dump(out, open(HERE / name, "w"), indent=0)


dump(RM, "classes_m77.json", "M77")
dump(RW, "classes_wells.json", "ICIT")
json.dump(dict(B=B, K_m77=RM["K"], alpha_m77=RM["alpha"], K_wells=RW["K"], alpha_wells=RW["alpha"],
               n_wells_devlike=len(wl), bridged_pairs=len(pairs), overall_agreement=float(agree),
               agreement_null_mean=float(np.mean(null)), agreement_null95=float(np.quantile(null, .95)),
               per_label=per_label, kept_labels=sorted(kept),
               final_counts={L: sum(r["final_class"] == L for r in rows) for L in LABELS},
               final_token_share={L: tok[L] / ntok for L in LABELS}, seed_agreement=float(seed_agree)),
          open(HERE / "step1.json", "w"), indent=1)
log(f"done ({time.time()-t0:.0f}s)")
