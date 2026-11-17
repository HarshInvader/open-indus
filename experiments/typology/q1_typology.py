"""Q1. Do signs inside Indus name cores recombine like syllabograms or like fixed logographic name elements?

Usage: .venv/bin/python experiments/typology/q1_typology.py [dev|heldout] [N_sub] [reps]
Compares Indus cores (distinct types, length >= 2) with length-matched, size-matched samples from
calibration corpora.  Each corpus is subsampled `reps` times at N_sub cores without replacement with the
Indus length mix; Indus itself is subsampled the same way (m-out-of-n bootstrap -> 95% interval).
"""
import sys, json
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from corpora import (indus_cores, ur3_names, linear_b_names, linear_b_words, proto_elamite,  # noqa
                     chinese_names, synthetic)
from metrics import metrics, metrics_rel, whole_word_metrics, matched_sample, max_feasible  # noqa

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
N_SUB = int(sys.argv[2]) if len(sys.argv) > 2 else 450
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 200
N_NAT = int(sys.argv[4]) if len(sys.argv) > 4 else 600
MAXL = int(sys.argv[5]) if len(sys.argv) > 5 else 3   # positional analysis on cores of length 2..MAXL
rng = np.random.default_rng(11)

ind = indus_cores(split)
ind_strict = indus_cores(split, strict=True)
I_all = list(ind); I2 = [c for c in I_all if 2 <= len(c) <= MAXL]
lend = Counter(min(len(c), 4) for c in I_all); tot = sum(lend.values())
len_dist = {L: n / tot for L, n in lend.items()}


def shuffled_indus(cores, seed):
    r = np.random.default_rng(seed)
    toks = [s for c in cores for s in c]; r.shuffle(toks)
    out, k = [], 0
    for c in cores:
        out.append(tuple(toks[k:k + len(c)])); k += len(c)
    return list(dict.fromkeys(out))


REFS = {
    "Indus (strict nouns)": list(ind_strict),
    "Indus (loose: numerals/titles kept)": list(indus_cores(split, loose=True)),
    "Ur III seal names (logo-syllabic)": list(ur3_names()),
    "Linear B words (syllabic)": list(linear_b_words()),
    "Linear B person names (syllabic)": list(linear_b_names()),
    "Proto-Elamite entries": list(proto_elamite()),
    "Chinese full names (logographic)": list(chinese_names(False)),
    "Chinese given names (logographic)": list(chinese_names(True)),
    "Synthetic slot code (logographic, fixed slots)": list(synthetic("logo_slot", 8000, len_dist, 1)),
    "Synthetic free-order code (logographic)": list(synthetic("logo_free", 8000, len_dist, 2)),
    "Synthetic syllabary names": list(synthetic("syll", 8000, len_dist, 3)),
}

print(f"split={split}: Indus cores {len(I_all)} types ({len(I2)} of length 2..{MAXL}), signs {len({s for c in I_all for s in c})}")
print(f"length mix (len>=2): {dict(sorted(Counter(min(len(c),5) for c in I2).items()))}; N_sub={N_SUB}, reps={REPS}")

KEYS = ["H_pos", "fixed_share", "float_sign", "float_bigram", "recurring_bigram_share", "anagram",
        "partner_div", "types_per_token", "pair_completeness", "pair_density", "top10_share",
        "H_rel", "fixed_excess", "float_rel", "bigram_rel", "partner_rel", "anagram_rel"]
WW = ["len1_share", "standalone_tok", "fully_decomposable"]


def summarize(rows):
    out = {}
    for k in rows[0]:
        v = np.array([r[k] for r in rows], float)
        v = v[~np.isnan(v)]
        out[k] = [float(v.mean()), float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) else [np.nan] * 3
    return out


res = {}
# Indus itself
rows = []
for _ in range(REPS):
    idx = rng.choice(len(I2), N_SUB, replace=False)
    rows.append(metrics_rel([I2[i] for i in idx], rng))
res["INDUS"] = summarize(rows)
target_lens_all = [len(c) for c in I2]
rows = [metrics_rel(shuffled_indus([I2[i] for i in rng.choice(len(I2), N_SUB, replace=False)], s), rng) for s in range(REPS)]
res["Indus shuffled across cores (null)"] = summarize(rows)
feas = {}
for name, cores in REFS.items():
    c2 = [c for c in cores if 2 <= len(c) <= MAXL]
    feas[name] = max_feasible(c2, target_lens_all)
    n = min(N_SUB, feas[name])
    rows = []
    if n < 50:
        print("  infeasible:", name, n); continue
    for _ in range(REPS):
        tl = [target_lens_all[i] for i in rng.choice(len(target_lens_all), n, replace=False)]
        smp = matched_sample(c2, tl, rng)
        if smp is not None:
            rows.append(metrics_rel(smp, rng))
    if rows:
        res[name] = summarize(rows); res[name]["_N"] = n
    else:
        print("  infeasible:", name)

# whole-word metrics at natural length, N_NAT cores
ww = {}
for name, cores in [("INDUS", I_all)] + list(REFS.items()):
    n = min(N_NAT, len(cores))
    rows = [whole_word_metrics([cores[i] for i in rng.choice(len(cores), n, replace=False)]) for _ in range(REPS)]
    ww[name] = summarize(rows); ww[name]["_N"] = n

print(f"\n{'corpus':48s} " + " ".join(f"{k[:11]:>17s}" for k in KEYS[:7]))
for name, r in res.items():
    tag = "" if r.get("_N", N_SUB) == N_SUB else f" [N={r['_N']}]"
    print(f"{(name + tag)[:48]:48s} " + " ".join(f"{r[k][0]:5.3f}[{r[k][1]:.2f},{r[k][2]:.2f}]" for k in KEYS[:7]))
print(f"\n{'corpus':48s} " + " ".join(f"{k[:11]:>17s}" for k in KEYS[7:]))
for name, r in res.items():
    print(f"{name[:48]:48s} " + " ".join(f"{r[k][0]:5.3f}[{r[k][1]:.2f},{r[k][2]:.2f}]" for k in KEYS[7:11]))
print(f"\nrelative to each sample's own cross-core shuffle (1 = no positional/pairing structure)")
print(f"{'corpus':48s} " + " ".join(f"{k[:11]:>17s}" for k in KEYS[11:]))
for name, r in res.items():
    print(f"{name[:48]:48s} " + " ".join(f"{r[k][0]:5.3f}[{r[k][1]:.2f},{r[k][2]:.2f}]" for k in KEYS[11:]))
print(f"\nwhole-word metrics, natural length mix, N={N_NAT} cores incl. length 1")
for name, r in ww.items():
    print(f"{name[:48]:48s} " + " ".join(f"{k}={r[k][0]:.3f}[{r[k][1]:.2f},{r[k][2]:.2f}]" for k in WW))

# placement: standardized distance on the core metrics, using only matched references at full N
CORE = ["H_rel", "fixed_excess", "float_rel", "bigram_rel", "partner_rel", "types_per_token"]
refs = [n for n in res if n not in ("INDUS",) and not n.startswith("Indus (") and res[n].get("_N", N_SUB) == N_SUB]
M = np.array([[res[n][k][0] for k in CORE] for n in refs])
sd = M.std(0); sd[sd == 0] = 1
x = np.array([res["INDUS"][k][0] for k in CORE])
dist = {n: float(np.sqrt((((M[i] - x) / sd) ** 2).mean())) for i, n in enumerate(refs)}
print("\nstandardized RMS distance of Indus to each reference (core metrics):")
for n, d in sorted(dist.items(), key=lambda t: t[1]):
    print(f"  {d:5.2f}  {n}")
# syllabicity index per metric: 0 = synthetic fixed-slot logographic, 1 = Linear B words
lo, hi = "Synthetic slot code (logographic, fixed slots)", "Linear B words (syllabic)"
print("\nposition on the slot-logographic (0) -> Linear B syllabic (1) axis, per metric [95% of Indus subsamples]:")
six = {}
for k in CORE:
    a, b = res[lo][k][0], res[hi][k][0]
    if not abs(b - a) > 1e-9:
        continue
    v = [(res["INDUS"][k][j] - a) / (b - a) for j in range(3)]
    six[k] = v
    print(f"  {k:16s} {v[0]:+.2f} [{min(v[1:]):+.2f}, {max(v[1:]):+.2f}]   (slot {a:.3f}, LinB {b:.3f}, Chinese full {res['Chinese full names (logographic)'][k][0]:.3f}, Ur III {res['Ur III seal names (logo-syllabic)'][k][0]:.3f})")

out = HERE / f"q1_{split}_L{MAXL}_N{N_SUB}.json"
json.dump(dict(split=split, maxlen=MAXL, n_cores=len(I_all), n_cores_len2=len(I2), N_sub=N_SUB, reps=REPS,
               matched=res, whole_word=ww, distance=dist, syllabicity_axis=six, feasible_N=feas),
          open(out, "w"), indent=1, default=float)
print("wrote", out)
