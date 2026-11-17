"""Test 1: do Indus seal name cores have the shape of attested Meluhhan names better than
Sumerian/Akkadian (Ur III) names?

Run: .venv/bin/python experiments/meluhha/name_shape.py

Data
- Meluhhan / Gulf names written in cuneiform or Linear Elamite (catalogue.csv):
  secure = na-na-sa3 (=Na-na-za), sa6-ma-ar ; extended adds sak-ku-si (BM 120573, Indus-type seal),
  za-si-ri (Linear Elamite Gulf seal), da-la-me (weak).
- Ur III seal-legend personal names (paragorth codelib, via experiments/typology/corpora.py, read only),
  determinatives dropped; one count per distinct name.
- Indus name cores = maximal runs of unknown-noun / fish-noun slots in experiments/functional_reading/readings.csv
  (typology's extractor), one count per distinct text, dev+heldout (descriptive, nothing is fitted).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "typology"))
import corpora  # noqa: E402  (read-only import of another agent's loader)

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(20261114)

MEL_SECURE = [("na", "na", "sa"), ("sa", "ma", "ar")]
MEL_EXT = MEL_SECURE + [("sak", "ku", "si"), ("za", "si", "ri"), ("da", "la", "me")]
VOW = set("aeiu")


def norm(s):
    s = s.lower().replace("sz", "s").replace("s,", "s").replace("t,", "t")
    s = re.sub(r"[0-9x]+$", "", s)
    return s


def syllables(signs):
    """Approximate spoken syllables of a cuneiform spelling: CV-VC sequences (ma-ar) merge."""
    s = "".join(signs)
    # merge V-V across a sign boundary when the second sign starts with the same vowel (ma-ar -> mar)
    out, prev = 0, None
    for i, sg in enumerate(signs):
        v = [c for c in sg if c in VOW]
        n = len(re.findall(r"[aeiu]+", sg))
        if i > 0 and sg[0] in VOW and prev and prev[-1] == sg[0]:
            n -= 1
        out += n
        prev = sg
    return max(out, 1)


def adj_repeat(t):
    return any(a == b for a, b in zip(t, t[1:]))


def init_redup(t):
    return len(t) >= 2 and t[0] == t[1]


# ---------------------------------------------------------------- reference corpora
ur = []
for k in corpora.ur3_names():
    t = tuple(norm(s) for s in k if not s.startswith("{"))
    t = tuple(s for s in t if s)
    if t:
        ur.append(t)
ur = sorted(set(ur))

bytext = corpora.indus_cores_by_text()
cores = [c for v in bytext.values() for c in v]

res = {}


def describe(name, names, syl=True):
    L = Counter(len(t) for t in names)
    d = {
        "n": len(names),
        "mean_signs": float(np.mean([len(t) for t in names])),
        "len_dist": {k: L[k] / len(names) for k in sorted(L)},
        "adj_repeat_rate_len>=2": float(np.mean([adj_repeat(t) for t in names if len(t) >= 2])),
        "init_redup_rate_len>=2": float(np.mean([init_redup(t) for t in names if len(t) >= 2])),
    }
    if syl:
        S = [syllables(t) for t in names]
        d["mean_syllables"] = float(np.mean(S))
        d["syl_dist"] = {k: v / len(S) for k, v in sorted(Counter(S).items())}
    res[name] = d
    return d


dm = describe("meluhhan_extended", MEL_EXT)
ds = describe("meluhhan_secure", MEL_SECURE)
du = describe("ur3_names", ur)
di = describe("indus_cores", cores, syl=False)

# ---------------------------------------------------------------- 1a. are Meluhhan names Ur III-shaped?
p3 = du["len_dist"].get(3, 0)
res["1a_all_three_signs"] = {
    "ur3_share_3signs": p3,
    "p_all5_3signs": p3 ** 5, "p_both_secure_3signs": p3 ** 2,
}
# syllable count: Meluhhan 2-3 syllables, Ur III share with 2-3 syllables
p23 = sum(v for k, v in du["syl_dist"].items() if k in (2, 3))
res["1a_syll_2to3"] = {"ur3_share": p23, "p_all5": p23 ** 5}
# reduplication: 1 of 5 (1 of 2 secure) vs Ur III rate
r_ur = du["init_redup_rate_len>=2"]
from scipy.stats import binom  # noqa: E402
res["1a_redup"] = {
    "ur3_init_redup_rate": r_ur,
    "p_at_least_1_of_5": float(1 - binom.cdf(0, 5, r_ur)),
    "p_at_least_1_of_2": float(1 - binom.cdf(0, 2, r_ur)),
    "ur3_examples": [ "-".join(t) for t in ur if init_redup(t)][:25],
}
# post hoc recurrent element: sibilant-a sign (sa/sa6/sa3/za/sak/sag) in 4 of 5 names
SIB = re.compile(r"^(sa|za|sag|sak)$")
q = float(np.mean([any(SIB.match(s) for s in t) for t in ur if len(t) == 3]))
res["1a_posthoc_sibilant_a"] = {"ur3_rate_3sign_names": q, "observed": "4/5",
                               "p_ge4_of5": float(1 - binom.cdf(3, 5, q)),
                               "note": "post hoc, chosen after looking; not counted"}

# ---------------------------------------------------------------- 1b. Indus cores vs the two name shapes
# Under 'syllabic spelling' a core's sign count should follow the name's syllable distribution;
# under 'cuneiform-like CV spelling' the written-sign distribution. Score Indus core lengths by
# multinomial log-likelihood per core, Dirichlet(0.5) smoothing over lengths 1..7.
K = range(1, 8)


def smooth(counts, alpha=0.5):
    tot = sum(counts.get(k, 0) for k in K) + alpha * len(K)
    return {k: (counts.get(k, 0) + alpha) / tot for k in K}


Lind = Counter(min(len(t), 7) for t in cores)
n_ind = sum(Lind.values())


def ll(p):
    return sum(Lind[k] * np.log(p[k]) for k in K) / n_ind


mel_sig = Counter(len(t) for t in MEL_EXT)
mel_syl = Counter(syllables(t) for t in MEL_EXT)
ur_sig = Counter(min(len(t), 7) for t in ur)
ur_syl = Counter(min(syllables(t), 7) for t in ur)
scores = {
    "mel_signs": ll(smooth(mel_sig)), "mel_syll": ll(smooth(mel_syl)),
    "ur3_signs": ll(smooth(ur_sig, 0.0 + 1e-9)), "ur3_syll": ll(smooth(ur_syl, 1e-9)),
}
# Bayesian bootstrap on the 5 Meluhhan names to show how unstable their shape distribution is
bb = []
for _ in range(2000):
    w = rng.dirichlet(np.ones(len(MEL_EXT)))
    c = Counter()
    for wi, t in zip(w, MEL_EXT):
        c[syllables(t)] += wi * len(MEL_EXT)
    bb.append(ll(smooth(c)))
scores["mel_syll_bootstrap_95"] = [float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))]
# share of Indus cores that are 2-3 signs (= Meluhhan syllable range)
scores["indus_share_2to3"] = (Lind[2] + Lind[3]) / n_ind
scores["indus_share_1"] = Lind[1] / n_ind
res["1b_length_loglik_per_core"] = scores

# repetition inside Indus cores vs a frequency-preserving null (shuffle tokens among all core slots,
# keeping every core's length)
multi = [t for t in cores if len(t) >= 2]
obs_rep = float(np.mean([adj_repeat(t) for t in multi]))
obs_init = float(np.mean([init_redup(t) for t in multi]))
pool = np.array([s for t in multi for s in t])
lens = [len(t) for t in multi]
null_rep, null_init = [], []
for _ in range(2000):
    rng.shuffle(pool)
    i, rr, ii = 0, 0, 0
    for L_ in lens:
        t = pool[i:i + L_]
        i += L_
        rr += any(t[j] == t[j + 1] for j in range(L_ - 1))
        ii += t[0] == t[1]
    null_rep.append(rr / len(lens))
    null_init.append(ii / len(lens))
null_rep, null_init = np.array(null_rep), np.array(null_init)
res["1b_indus_repetition"] = {
    "n_multi_cores": len(multi),
    "obs_adj_repeat": obs_rep, "null_mean": float(null_rep.mean()),
    "p_excess": float((null_rep >= obs_rep).mean()),
    "obs_init_redup": obs_init, "null_init_mean": float(null_init.mean()),
    "p_init_excess": float((null_init >= obs_init).mean()),
    "ur3_init_redup": r_ur, "meluhhan_init_redup": "1/5 (0.20); secure 1/2",
    "examples": Counter("-".join(t) for t in multi if adj_repeat(t)).most_common(12),
}
# which reference does the Indus init-redup rate fit better? binomial log-lik per core
k_obs = int(round(obs_init * len(multi)))
res["1b_redup_fit"] = {
    "loglik_ur3_rate": float(binom.logpmf(k_obs, len(multi), r_ur)),
    "loglik_mel_0.20": float(binom.logpmf(k_obs, len(multi), 0.20)),
    "loglik_mel_beta_posterior_mean": float(binom.logpmf(k_obs, len(multi), (1 + 0.5) / (5 + 1))),
}

print(json.dumps(res, indent=1, default=str))
out = HERE / "results.json"
allr = json.loads(out.read_text()) if out.exists() else {}
allr["name_shape"] = res
out.write_text(json.dumps(allr, indent=1, default=str))

# ---------------------------------------------------------------- addenda (concentration, CI)
from scipy.stats import beta  # noqa: E402
rep_signs = Counter(t[j] for t in multi for j in range(len(t) - 1) if t[j] == t[j + 1])
tot = sum(rep_signs.values())
top4 = rep_signs.most_common(4)
res["1b_repeat_concentration"] = {
    "repeat_tokens": tot, "distinct_doubled_signs": len(rep_signs),
    "top4": top4, "top4_share": sum(c for _, c in top4) / tot,
}
res["1a_meluhhan_redup_jeffreys95"] = [float(beta.ppf(0.025, 1.5, 4.5)), float(beta.ppf(0.975, 1.5, 4.5))]
res["1b_p_one_sign_name"] = {"indus_cores": di["len_dist"][1], "ur3_signs": du["len_dist"].get(1, 0),
                             "ur3_syll": du["syl_dist"].get(1, 0), "meluhhan": 0.0}
print(json.dumps({k: res[k] for k in ("1b_repeat_concentration", "1a_meluhhan_redup_jeffreys95", "1b_p_one_sign_name")}, indent=1, default=str))
allr["name_shape"] = res
out.write_text(json.dumps(allr, indent=1, default=str))
