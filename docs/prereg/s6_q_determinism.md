# Pre-registration: S6, pin down the round-seal q-value

Contributor: m0x1n. Written 2026-11-28, before any of the runs below.

## Question

README finding #4 (Gulf round seals break Indus sign order) reports q = 0.02 to 0.09 across all tests, and says the spread comes from Python's unfixed hash seed (docs/REPRO_REPORT.md, "Two causes of drift"). The number behind it is ledger row `lr_gulf`, computed in section F of `experiments/ledger/v2_reruns.py` and corrected in `experiments/ledger/build_ledger.py`.

Two things can move that q from run to run, and this task separates them:

1. **Hash-seed drift.** Code that loops over a Python `set` of strings visits it in an order that depends on `PYTHONHASHSEED`. If such a loop draws random numbers, every later draw from the same random stream changes.
2. **Monte Carlo error.** Section F estimates p from 20,000 matched draws. At p around 5e-4 that is about 10 exceedances, so p itself is noisy, and q_all (a Benjamini-Hochberg q over roughly 2,000 padded tests) moves with it.

## Hypothesis

H1. The statistic in section F (foreign mean permutation percentile, 0.592, and the native pools) does not depend on the hash seed. Only the random draws do, because sections C and D consume the same NumPy stream first, and D loops over `set(site)`.

H2. Once every set loop that feeds a random draw is sorted, and each section gets its own random stream, `v2_reruns.json` is byte-identical under any `PYTHONHASHSEED`.

H3. With enough matched draws (2,000,000 instead of 20,000), the spread of `lr_gulf` q_all over 20 random seeds is much narrower than the 0.02 to 0.09 spread now reported.

## Exact procedure

All runs are in scratch copies; no committed output is overwritten. Code: `experiments/s6_q_determinism/`.

- **Run A (before).** Unmodified `v2_reruns.py` then `build_ledger.py`, under `PYTHONHASHSEED` = 0, 1, ..., 19. Record for `lr_gulf`: p, q_global, q_hier, q_all; and p for every other `lr_*` row.
- **Run B (determinism check).** Modified `v2_reruns.py` (sorted set loops, one named random stream per section, 2,000,000 draws in F), same master seed, under `PYTHONHASHSEED` = 0, 1, 2. Pass: the three `v2_reruns.json` files are byte-identical.
- **Run C (the range).** Modified script under 20 master random seeds (`INDUS_SEED` = 1 ... 20), each also under its own `PYTHONHASHSEED`. Report min, median and max of `lr_gulf` p and each q, and the Monte Carlo 95% interval of each p.

Data split: the frozen v2 split (`data/splits_v2.json`, sha256 `7a2bd876…`) restored by `datasets/fetch.py corpus`. Nothing is tuned; no test, statistic, sign set or threshold is changed. Only the order of loops, the random streams and the number of draws in F change.

## Null and pass marks

The null is unchanged from section F: means of length-matched draws from peripheral-site seals (site held out).

- H1 passes if the F statistic (`foreign_mean_pct`, `native_matched_mean` to 3 decimals, pool sizes) is identical in all 20 runs of Run A.
- H2 passes if Run B gives byte-identical output.
- H3 passes if the max/min ratio of `lr_gulf` q_all over Run C is below 1.5 (now 0.086/0.020 = 4.3).

## Planted control

Not applicable in the usual sense: this task makes no claim about sounds, a language or a grammar. The check that the harness can see drift is Run A itself: it must reproduce the spread reported in docs/REPRO_REPORT.md (seeds 0, 1, 2 giving lr_gulf p of about 2.5e-4, 5e-4 and 1e-4). If it does not, the harness is not measuring what it claims and I will say so.

Disclosure: before writing this file I ran the unmodified script once, under `PYTHONHASHSEED=0` on Python 3.13 with the pinned packages, to time it (5.7 minutes). It gave `lr_gulf` p = 2.0e-4, against 2.5e-4 in docs/REPRO_REPORT.md for the same seed on Python 3.15. That run is not counted in Run A; Run A re-runs seed 0. No other output was seen.

## What I will report if it fails

- If H1 fails, the drift is in the statistic itself, not only in the draws, and I will find and report the line.
- If H2 fails, I will list which outputs still differ.
- If H3 fails, I will report the Run C range as it is and say how many draws would be needed.

Every outcome is reported, including a q range that is wider or higher than now.
