"""Part (d) of experiments/grammar/validate.py (Gulf negative control), copied verbatim in logic so it can be
re-run alone. Run through runner.py so OLD/NEW labels apply:
    .venv/bin/python -I experiments/round_label_audit/runner.py new experiments/round_label_audit/d_gulf.py
"""
import json, sys
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "experiments/grammar"
sys.path.insert(0, str(G))
import glib  # noqa
from glib import ClassBigram, KNBigram, m77_units, icit_devlike, family_folds, icit_units, FOREIGN  # noqa
from step1_classes_seeds import SEED_W  # noqa

CW = json.load(open(G / "classes_wells.json"))
KW, ALPHAW = CW["K"], CW["alpha"]
RNG = np.random.default_rng(2026)
tag = "new" if glib.icit_register("SEAL:R") == "seal" else "old"


def grammar_on(units, seeds, K_, a_):
    return ClassBigram(K_, alpha=a_).fit(units, init=seeds, restarts=5)


wl = icit_devlike(m77_units("heldout"))
native_seals = [u for u in wl if u["register"] == "seal"]
fo = family_folds(wl, 5, 0)
cvb, cvk = {}, {}
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
    if not tb:
        print(f"  {label}: n=0"); return dict(n=0)
    obs = float(np.mean(tb))
    draws = np.array([np.mean([RNG.choice(byk[k]) for k in keys]) for _ in range(ndraw)])
    p = (1 + (draws >= obs).sum()) / (ndraw + 1)
    allref = np.concatenate([byk[k] for k in set(keys)])
    auc = float(np.mean([(t > r) + 0.5 * (t == r) for t in tb for r in allref]))
    out = dict(n=len(tb), bits=obs, matched_native=float(draws.mean()), diff=obs - float(draws.mean()), p=float(p), auc=auc)
    print(f"  {label:44s} n={len(tb):3d} {obs:.3f} vs matched native {draws.mean():.3f}: diff {out['diff']:+.3f} p={p:.4f} AUC {auc:.2f}", flush=True)
    return out


class CV:
    @staticmethod
    def unit_logp(u):
        return (-cvb[u["key"]][0] * cvb[u["key"]][1], cvb[u["key"]][1])


print(f"[{tag}] native reference seals: {len(native_seals)}")
D = {"n_native_ref": len(native_seals)}
home_round = [u for u in wl if u["register"] == "round_seal"]
D["home_round_vs_native_grammar"] = matched([u for u in home_round if u["key"] in cvb], CV, native_seals, cvb,
                                            "home round seals (CV) vs native, grammar")
gulf = [u for u in icit_units(sites=FOREIGN) if u["register"] == "round_seal"]
gulf_sq = [u for u in icit_units(sites=FOREIGN) if u["register"] == "seal"]
D["gulf_round_grammar"] = matched(gulf, GW, native_seals, cvb, "Gulf round seals, grammar")
D["gulf_round_bigram"] = matched(gulf, KWB, native_seals, cvk, "Gulf round seals, KN bigram (reference)")
D["gulf_square_grammar"] = matched(gulf_sq, GW, native_seals, cvb, "foreign square seals, grammar (secondary)")
D["pass_d"] = bool(D["gulf_round_grammar"]["diff"] > 0 and D["gulf_round_grammar"]["p"] < 0.01)
print("  PASS (d):", D["pass_d"])
json.dump(D, open(Path(__file__).resolve().parent / f"out_{tag}/d_gulf.json", "w"), indent=1)
