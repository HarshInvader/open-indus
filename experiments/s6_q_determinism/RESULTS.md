# S6: pin down the round-seal q-value

Contributor: m0x1n (starter task S6). Pre-registration: `docs/prereg/s6_q_determinism.md`, sha256 `9c06b80f…`, sealed in its own commit before any sweep ran.

## Conclusion

**The round-seal q-value is now the same on every run. Across 20 random seeds its q over all tests is 0.013 to 0.015, not 0.02 to 0.09.** Its p is 1.8e-4 (Monte Carlo 95% interval 1.65e-4 to 2.03e-4). The verdict on finding #4 does not change: it passed before and it passes now. What changes is that the number can be quoted.

The drift had two causes:

1. **Hash-seed order fed the random stream.** Section D of `experiments/ledger/v2_reruns.py` looped over `set(site)` while drawing from the NumPy stream that section F draws from next. Section A built its role list from the sets `SHORT` and `TALL`. The hash seed changed the order, so it changed every later draw.
2. **Too few draws.** Section F estimated p from 20,000 matched draws. At p ≈ 2e-4 that is about 4 exceedances, so p itself jumped between 1e-4 and 5.5e-4 from one stream to the next. q over about 2,000 padded tests magnified each jump.

I also found a third problem, in the repository's own fix for this. **`PYTHONHASHSEED` had no effect on any script run with `-I`.** Isolated mode implies `-E`, and `-E` tells Python to ignore every `PYTHON*` variable, `PYTHONHASHSEED` included:

```
$ PYTHONHASHSEED=0 python3 -I -c "print(hash('abc'))"   # differs on every run
$ PYTHONHASHSEED=0 python3    -c "print(hash('abc'))"   # same on every run
```

`scripts/reproduce.sh` exports `PYTHONHASHSEED=0` and then runs every script with `-I`, so every one of its runs got a random hash seed. The "seed 0, 1, 2" columns in `docs/REPRO_REPORT.md` were probably three random seeds; I could not re-run that exact setup to confirm it. The same flaw explains why two "seeded" rebuilds of `splits_v2` gave different held-out sets.

## What changed

| File | Change |
|---|---|
| `experiments/ledger/v2_reruns.py` | Sorted the three set loops that feed random draws (`SHORT`, `TALL`, `set(site)`). Each section now draws from its own named stream (`streams("A")`, `"C"`, `"D"`, `"F"`), so one section's draws can no longer shift another's. Master seed from `INDUS_SEED` (default 20261114). Section F uses 2,000,000 vectorised draws instead of 20,000 and reports `hits`, `n_draws` and the exact 95% Monte Carlo interval `p_mc95`. No statistic, sign set, null or threshold changed. |
| `experiments/ledger/build_ledger.py` | The `lr_gulf` note reads the number of draws and the MC interval from the run instead of hard-coding "20,000". |
| `scripts/reproduce.sh` | Runs scripts with `-s -P` instead of `-I`, so the exported `PYTHONHASHSEED=0` actually applies. `-s -P` keeps the other two parts of isolation: no user site-packages, and the script's directory is not put first on the path. |
| `experiments/s6_q_determinism/` | `sweep.py` (runs everything in scratch copies), `analyze.py`, `results.json`, and `runs/` with each run's summary, log and `v2_reruns.json`. |

I did not regenerate the committed `experiments/ledger/v2_reruns.json`, `results.json` or `docs/test_ledger.csv`. That is the lead's step. After this change, running v2_reruns → build_ledger → merge_rows gives the default-seed numbers in the table below.

## Numbers

Every q below is computed the way README's q is: the run's `lr_*` p-values are written into the **committed** `docs/test_ledger.csv`, then `merge_rows.py` recomputes every q column. That step also merges the 78 experiment rows that were pending in the working tree. Python 3.13.18 with the pinned packages from `requirements.txt` (pinned for 3.15; see caveats). 4 workers, about 30 seconds per run.

| `lr_gulf` | Run A: original code, 20 hash seeds | Run B: fixed, 3 hash seeds | Run C: fixed, 20 random seeds |
|---|---|---|---|
| p | 1.0e-4 to 5.5e-4 (median 3.0e-4) | 1.83e-4, identical | 1.67e-4 to 2.01e-4 (median 1.8e-4) |
| q_global (confirmatory) | 0.0020 to 0.0086 | 0.0035 | 0.0032 to 0.0037 |
| q_hier | 0.00046 to 0.0025 | 0.00084 | 0.00077 to 0.00093 |
| **q_all (all tests)** | **0.0080 to 0.037** | **0.0143** | **0.0130 to 0.0154** |
| max / min of q_all | 4.7 | 1 | 1.19 |

The README range (0.02 to 0.09) was computed against the smaller ledger that `build_ledger.py` rebuilds by itself. On that ledger, Run A gives q_all 0.020 to 0.095, which reproduces the README range. Run C gives 0.032 to 0.037. That ledger is missing 589 committed rows that no script regenerates (see below), so the table above is the one to cite.

The Monte Carlo 95% interval of p in any single Run C run is about ±10% (widest: 1.82e-4 to 2.22e-4). The spread over 20 seeds matches it, so what remains is honest Monte Carlo error. There is no hidden order effect left.

## Pre-registered hypotheses

| Hypothesis | Pass mark | Result | Verdict |
|---|---|---|---|
| H1: section F's statistic does not depend on the hash seed | `foreign_mean_pct`, `native_matched_mean` to 3 d.p., and pool sizes identical over Run A | `foreign_mean_pct` = 0.592 and pool sizes {2: 36, 3: 32, 4: 38, 5: 76} in all 20 runs. `native_matched_mean` was 0.894, 0.895 or 0.896. | **Refuted as written; supported in substance.** My pass mark was wrong: `native_matched_mean` is the mean of the random draws, so it is a Monte Carlo quantity and not part of the statistic. The statistic itself never moved. Run B confirms this: the pool code is unchanged and its output is byte-identical across hash seeds. |
| H2: the fixed script is byte-identical under any hash seed | 3 `v2_reruns.json` files identical | 1 distinct sha256 over `PYTHONHASHSEED` = 0, 1, 2 | **Supported** |
| H3: with 2,000,000 draws, q_all max/min over 20 seeds < 1.5 | ratio < 1.5 | 1.19 (was 4.7) | **Supported** |
| Planted check: the harness reproduces the reported drift | Run A spread similar to REPRO_REPORT | Run A p 1e-4 to 5.5e-4, against 1e-4 to 5e-4 reported | **Supported.** Exact per-seed values differ because REPRO_REPORT's seeds were not applied (the `-I` finding). |

## Caveats and what was not checked

- **Python version.** These runs used Python 3.13.18. The project pins 3.15.0, which was not available here. All packages were at the pinned versions. String hashing and `random.Random` seeding behave the same in both, but the exact Run A values may differ on 3.15.
- **The ledger cannot be rebuilt from scripts.** `build_ledger.py` followed by `merge_rows.py` gives 788 rows. The committed ledger has 1,299, and 78 more are pending in `ledger_rows.csv` files. 589 committed rows (for example `as_g1`, `bo_h1`, `bb_gate`) are missing from the rebuild: no script or `ledger_rows.csv` regenerates them. That is why the sweep patches the committed ledger instead of rebuilding it. Anyone re-running `build_ledger.py` today would silently drop those rows and lower every q. This is worth its own issue.
- **Other rows still carry Monte Carlo noise.** Across Run C random seeds, `lr_fr_lex` (README #9, quoted as p = 0.013) ranges from 0.0033 to 0.027, because it uses 300 permutations. `lr_animal` (300 draws) ranges from 0.050 to 0.100. Both are now deterministic for a fixed seed, but their quoted values should either use more permutations or carry an MC interval. I did not change them, to keep this task to the round-seal number.
- **`corpus/build.py:splits_v2`** still breaks ties with `max(set(...))`. With the `-I` fix, a rebuild under `PYTHONHASHSEED=0` is now repeatable, but it will not match the frozen committed split. I did not touch `corpus/` (CONTRIBUTING). The committed split is still the one every result uses.
- No ledger rows are added. None of these checks is a hypothesis test on Indus texts, and none produces a p-value.

## S6b: the same fix for README #9 (functional reading)

Pre-registration: `docs/prereg/s6b_lexicon_null.md`, sealed in its own commit after S6 and before this run.

Run C showed the second-largest Monte Carlo swing in the ledger. Row `lr_fr_lex`, behind README #9 ("weakly supported, p=0.013, q=0.085"), moved from 0.0033 to 0.027 with the random seed, because it uses 300 lexicon permutations. S6b raises the v2 block to 10,000 permutations, with an exact MC interval. Nothing else changes; the v1 reproduction block keeps 300. Run D repeats Run C's 20 seeds.

| `lr_fr_lex` | Run C: 300 permutations | Run D: 10,000 permutations |
|---|---|---|
| p | 0.0033 to 0.027 (max/min 8.0) | **0.011 to 0.014** (median 0.012; max/min 1.29) |
| q_global | 0.038 to 0.22 | **0.10 to 0.13** |
| q_hier | 0.012 to 0.082 | **0.038 to 0.044** |
| q_all | 0.18 to 1 | 0.49 to 0.62 |

- **H4 supported.** The max/min ratio of p is 1.29, under the 1.5 bar. One run's MC 95% interval is about ±0.002 (seed 1: 109 of 10,000, 0.009 to 0.013).
- **H5 (descriptive).** q_global is **above 0.05 under every seed** (0.10 to 0.13), and q_hier is **below 0.05 under every seed** (0.038 to 0.044). So the honest reading of README #9 is: "p ≈ 0.012; passes the hierarchical correction, fails the global one." Before, it depended on the seed which side of 0.05 the q_global fell. The README's "q=0.085" matches neither the committed ledger (q_global 0.124) nor this range, so it should be updated.
- `lr_gulf` is unchanged between Run C and Run D, to every digit. Each section now has its own random stream, so drawing more permutations in section A no longer moves section F.
- Run D takes about 105 seconds per run, up from 30.

## Reproduce

```bash
python3 datasets/fetch.py corpus
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -I experiments/s6_q_determinism/sweep.py A   # original code (git show 1c1da07), 20 hash seeds
.venv/bin/python -I experiments/s6_q_determinism/sweep.py B   # fixed code, 3 hash seeds
.venv/bin/python -I experiments/s6_q_determinism/sweep.py C   # fixed code, 20 random seeds (run before S6b)
.venv/bin/python -I experiments/s6_q_determinism/sweep.py D   # after S6b (10,000 lexicon permutations), 20 seeds
.venv/bin/python -I experiments/s6_q_determinism/analyze.py
```
