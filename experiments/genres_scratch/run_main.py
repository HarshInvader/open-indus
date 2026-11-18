"""Main pipeline: K by family CV, final fit, held-out S1, association tests, stability.
Usage: board/run.sh .venv/bin/python -I experiments/genres_scratch/run_main.py <corpus> [models...]
corpus in m77, icit, cun, lat.  Resumable: one json per (corpus, model) in out/.
"""
import json
import math
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gs  # noqa: E402
import data  # noqa: E402

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
KS = list(range(1, 11))


def load(corpus):
    if corpus == "m77":
        return data.m77()
    if corpus == "icit":
        return data.icit()
    tr, te, avail = data.known(corpus)
    return tr, te


def lenbin(u):
    return f"{min(len(u['signs']), 6)}{'f' if u['full'] else 'b'}"


def fam_boot_diff(units, d, n=1000, seed=0):
    fam = gs.glib.families(units)
    ids = sorted(set(fam))
    by = {}
    for i, f in enumerate(fam):
        by.setdefault(f, []).append(i)
    rng = np.random.default_rng(seed)
    S = np.array([d[by[f]].sum() for f in ids]); C = np.array([len(by[f]) for f in ids])
    bs = []
    for _ in range(n):
        p = rng.integers(0, len(ids), len(ids))
        bs.append(S[p].sum() / C[p].sum())
    return float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def labels_for(corpus):
    if corpus == "m77":
        return ["obj", "site"]
    if corpus == "icit":
        return ["shape", "reg", "sitegrp"]
    return ["genre"]


def job(args):
    corpus, name = args
    f = OUT / f"main_{corpus}_{name}.json"
    if f.exists():
        return str(f)
    t0 = time.time()
    tr, te = load(corpus)
    rec = dict(corpus=corpus, model=name, n_train=len(tr), n_test=len(te))
    restarts_cv = 2 if name == "HMM" else 3
    res = gs.cv_curve(name, tr, KS, folds=5, seed=0, restarts=restarts_cv)
    K, means, best = gs.pick_K(res)
    rec.update(K=K, K_best=best, cv_means={str(k): v for k, v in means.items()})
    m = gs.MODELS[name]().fit(tr, K, seed=0, restarts=3)
    m1 = gs.MODELS[name]().fit(tr, 1, seed=0, restarts=1)
    if name == "LDA":
        rec["ho_ll_K"] = m.heldout_score(te); rec["ho_ll_1"] = m1.heldout_score(te)
        # family bootstrap of the difference via resampled perplexity
        fam = gs.glib.families(te); ids = sorted(set(fam)); by = {}
        for i, fa in enumerate(fam):
            by.setdefault(fa, []).append(i)
        rng = np.random.default_rng(0); bs = []
        for _ in range(200):
            p = rng.integers(0, len(ids), len(ids))
            sub = [te[i] for q in p for i in by[ids[q]]]
            bs.append(m.heldout_score(sub) - m1.heldout_score(sub))
        rec["ho_diff_ci"] = [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]
    else:
        lk, l1 = m.loglik(te), m1.loglik(te)
        rec["ho_ll_K"] = float(lk.mean()); rec["ho_ll_1"] = float(l1.mean())
        rec["ho_diff_ci"] = fam_boot_diff(te, lk - l1)
    rec["S1"] = bool(K >= 2 and rec["ho_diff_ci"][0] > 0)
    gd, gh = m.assign(tr), m.assign(te)
    rec["sizes_train"] = {str(k): int(v) for k, v in Counter(gd.tolist()).items()}
    rec["tests"] = {}
    for lab in labels_for(corpus):
        idd = [i for i, u in enumerate(tr) if u.get(lab) is not None]
        idh = [i for i, u in enumerate(te) if u.get(lab) is not None]
        yd = [tr[i][lab] for i in idd]; yh = [te[i][lab] for i in idh]
        r = gs.assoc_test(gd[idd], yd, gh[idh], yh, K, nperm=2000, seed=1)
        r["nmi"] = gs.nmi(gh[idh], yh); r["ari"] = gs.ari(gh[idh], yh); r["n"] = len(idh)
        rec["tests"][lab] = r
    if corpus == "m77":  # secondary (a): object type beyond site and length
        strata = [f"{u['site']}|{lenbin(u)}" for u in te]
        r = gs.assoc_test(gd, [u["obj"] for u in tr], gh, [u["obj"] for u in te], K, nperm=2000, seed=2,
                          strata=strata)
        rec["tests"]["obj_within_site_len"] = r
        strata = [lenbin(u) for u in te]
        rec["tests"]["obj_within_len"] = gs.assoc_test(gd, [u["obj"] for u in tr], gh, [u["obj"] for u in te],
                                                       K, nperm=2000, seed=3, strata=strata)
        rec["tests"]["site_within_obj_len"] = gs.assoc_test(
            gd, [u["site"] for u in tr], gh, [u["site"] for u in te], K, nperm=2000, seed=4,
            strata=[f"{u['obj']}|{lenbin(u)}" for u in te])
    if K >= 2:
        rec["stability"] = gs.stability(name, tr, K, n=20 if name != "LDA" else 10, seed=0,
                                        restarts=1 if name in ("HMM", "LDA") else 2)
    # exploratory (not a verdict gate): association at a forced K = 4
    me = m if K == 4 else gs.MODELS[name]().fit(tr, 4, seed=0, restarts=3 if name != "LDA" else 1)
    ed, eh = me.assign(tr), me.assign(te)
    rec["explore_K4"] = {"sizes_train": {str(k): int(v) for k, v in Counter(ed.tolist()).items()}}
    for lab in labels_for(corpus):
        idd = [i for i, u in enumerate(tr) if u.get(lab) is not None]
        idh = [i for i, u in enumerate(te) if u.get(lab) is not None]
        r = gs.assoc_test(ed[idd], [tr[i][lab] for i in idd], eh[idh], [te[i][lab] for i in idh], 4,
                          nperm=2000, seed=5)
        r["ari"] = gs.ari(eh[idh], [te[i][lab] for i in idh])
        rec["explore_K4"][lab] = r
    if corpus == "m77":
        rec["explore_K4"]["obj_within_site_len"] = gs.assoc_test(
            ed, [u["obj"] for u in tr], eh, [u["obj"] for u in te], 4, nperm=2000, seed=6,
            strata=[f"{u['site']}|{lenbin(u)}" for u in te])
    rec["explore_assign_train"] = ed.tolist(); rec["explore_assign_test"] = eh.tolist()
    rec["assign_train"] = gd.tolist(); rec["assign_test"] = gh.tolist()
    rec["secs"] = round(time.time() - t0)
    json.dump(rec, open(f, "w"))
    return str(f)


if __name__ == "__main__":
    corpus = sys.argv[1]
    models = sys.argv[2:] or ["BG", "LCA", "HMM", "LDA"]
    with Pool(2) as p:
        for r in p.imap_unordered(job, [(corpus, m) for m in models]):
            print("done", r, flush=True)
