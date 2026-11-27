# Rare-sign- and length-matched null for 'six then fish' (Starter task S4)

**Verdict: SURVIVES.** Two-tier six followed by plain fish (`M109 -> M59` in M77; `W016 -> W220` in native ICIT; README #5) passes a pre-registered null matched on both rare-sign load and text length, on M77 v2 held-out and on native ICIT, against both all non-final tokens and other short numerals (all 4 primary tests Holm `p <= 2.9e-7`).

Rare-sign load was a real suspect. Across both M77 and ICIT, baseline `P(next = fish)` drops sharply as a text carries more rare signs (after other short numerals in M77 `dev`, from 11.3% at `r = 0` down to 0% at `r >= 2`), and two-tier six occurs more often in `r = 0` texts than average (`r/L = 0.070` vs `0.156` in M77 held-out; `0.070` vs `0.111` in ICIT). Planted control `C3` confirms that an uncoupled numeral restricted to `r = 0` texts triggers 10–19% false positives under naive global or length-only nulls, while our `(L, r)`-matched null restores strict calibration (2.2–2.7% at `alpha = 0.05`). Even against this steeper matched numeral baseline (9.3% on M77 held-out, 11.5% when also matching run-initial position), the observed rate of 7/10 (70.0%, 95% CI 34.8–93.3%) on held-out and 13/33 (39.4%, 95% CI 22.9–57.9%) on ICIT clears by +35 to +68 percentage points and retains 99.4–100.3% of the length-only excess.

This confirms the pair as a robust sequential fixed expression; it does not test any language or meaning (such as Parpola's *aṟu-mīn* "Pleiades").

- **Pre-registration:** `docs/prereg/2026-11-27_s4_six_fish_rare_null.md` (SHA-256 `6f48d2f5...`, sealed in `docs/prereg/HASHES.txt` and committed before any held-out or ICIT run).
- **Code:** `experiments/six_fish_rare_null/run.py` (SHA-256 `996ea5f9...`, sealed in the same pre-registration commit; verified byte-identical `results.json` under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=42`).
- **Run command:** `PYTHONHASHSEED=0 .venv/bin/python -I experiments/six_fish_rare_null/run.py` (~13s on one CPU).
- **Machine-readable output:** `experiments/six_fish_rare_null/results.json`.
- **Ledger rows added:** `s4_6f_ho_n1`, `s4_6f_ho_n2`, `s4_6f_icit_n1`, `s4_6f_icit_n2` in `docs/test_ledger.csv`.

---

## Setup
- **Counting unit:** Distinct texts (`distinct()` in `corpus/load.py` for M77: 1,699 dev, 571 held-out under frozen split v2; 3,504 distinct native ICIT texts). Break-free runs (`runs()`, splitting at `|` and `#`). Only non-final tokens within runs of length `>= 2` are eligible.
- **Rare-sign load `r` and length `L`:** `L_bin = min(L_text, 9)` and `r_bin = min(r_text, 3)`, where `r_text` counts tokens with reference frequency `< 10` (matching `experiments/redteam_round_order/`). Reference frequency is strictly `count_dev(s)` for M77 `dev` and `heldout` (zero leakage from held-out), and deterministic leave-one-text-out count `count_icit(s) - count_in_text(s)` for ICIT. Strata with `< 5` reference tokens collapse `r -> r - 1`, then `L -> L - 1`.
- **Nulls and p-values:** Exact one-sided Poisson-binomial tail `p_exact` over stratum follower rates `p_i`, cross-checked against 100,000 Monte Carlo draws (`p_mc`, without replacement within strata whenever stratum size permits). Primary family: 4 tests (`T1`–`T4`), Holm-Bonferroni corrected.

## Why rare-sign load was a real confound to check
In both corpora, texts with zero rare signs carry far more `M59` / `W220` followers than rare-heavy texts, especially after short numerals:

| rare-sign load `r` | M77 dev all (`n`, `P(M59)`) | M77 dev other NUM (`n`, `P(M59)`) | ICIT all (`n`, `P(W220)`) | ICIT other NUM (`n`, `P(W220)`) |
|---|---|---|---|---|
| `r = 0` | 3,571 (0.0400) | 194 (**0.1134**) | 5,302 (0.0373) | 302 (**0.0762**) |
| `r = 1` | 1,633 (0.0294) | 80 (0.0250) | 3,100 (0.0184) | 176 (0.0284) |
| `r = 2` | 500 (0.0120) | 29 (0.0000) | 739 (0.0217) | 44 (0.0000) |
| `r >= 3` | 105 (0.0095) | 12 (0.0000) | 231 (0.0216) | 15 (0.0000) |

Two-tier six occurs in lower-rare-load texts than the corpus average in both M77 held-out (`mean r/L = 0.070` vs `0.156` for all other non-final tokens; 7/10 in `r = 0`) and ICIT (`mean r/L = 0.070` vs `0.111` for all other tokens and `0.118` for other numerals; 24/33 in `r = 0`).

---

## Primary results (Holm-Bonferroni across 4 tests)

| Test | Split / corpus | Reference pool (`(L, r)` matched) | Observed `k/N` (95% CI) | Matched null mean | Excess (`diff`) | `p_exact` | `p_holm` | `p_mc` (100k) | Collapsed strata |
|---|---|---|---|---|---|---|---|---|---|
| **T1** | M77 v2 held-out | Held-out all non-`M109` | **7/10 = 0.700** (0.348–0.933) | 0.0175 | **+0.6825** | `1.03e-11` | **`2.06e-11`** | `1.0e-5` | 0 / 10 |
| **T2** | M77 v2 held-out | Dev other short numerals | **7/10 = 0.700** (0.348–0.933) | 0.0933 | **+0.6067** | `2.91e-7` | **`2.91e-7`** | `1.0e-5` | 0 / 10 |
| **T3** | ICIT native | ICIT all non-`W016` | **13/33 = 0.394** (0.229–0.579) | 0.0285 | **+0.3654** | `1.61e-12` | **`4.83e-12`** | `1.0e-5` | 0 / 33 |
| **T4** | ICIT native | ICIT other short numerals | **13/33 = 0.394** (0.229–0.579) | 0.0416 | **+0.3523** | `1.15e-12` | **`4.59e-12`** | `1.0e-5` | 2 / 33 |

- Rare-sign matching raises the M77 held-out numeral baseline from the naive 3.1% unigram rate (or 6.0% pooled numeral rate in `redteam`) to **9.33%** (`T2`), yet the observed rate remains +60.7 percentage points above it (`p_holm = 2.91e-7`).
- Compared to the length-only null `N0`, rare-sign matching retains **100.3%** (`T1`), **99.5%** (`T2`), **99.6%** (`T3`), and **99.4%** (`T4`) of the rate excess.

---

## Planted controls (1,000 replicates each; zero held-out data used)

### C1a (Real-corpus-embedded planted fixed pair) & C1b (2,300-text synthetic corpus, mean length 4.43)
Stratum profiles drawn strictly from M77 `dev`'s `M109` `(L, r)` distribution (`n = 15`).

| Planted rate `p_true` | C1a `N=10` N1 power (`0.05` / `0.01`) | C1a `N=10` N2 power (`0.05` / `0.01`) | C1a `N=25` N1 / N2 power (`0.05`) | C1b synth-2300 `N=10` / `N=25` power (`0.05`) |
|---|---|---|---|---|
| `0.25` | 0.798 / 0.547 | 0.644 / 0.450 | 0.975 / 0.928 | 0.644 / 0.953 |
| `0.35` | 0.926 / 0.774 | 0.830 / 0.688 | 0.998 / 0.993 | 0.828 / 0.998 |
| **`0.48`** | **0.986** / 0.936 | **0.952** / 0.897 | **1.000** / **1.000** | **0.972** / **1.000** |
| `0.70` | 1.000 / 0.999 | 1.000 / 0.996 | 1.000 / 1.000 | 0.998 / 1.000 |

At the exact held-out corpus size (571 texts subsampled from `dev`, `N = 10`, `p_true = 0.48`), C1a power is **0.986** at `alpha = 0.05` (**0.938** at `alpha = 0.01`).

### C2 (Calibration) & C3 (Rare-load confounding control: uncoupled sign exclusively in `r = 0` texts)
False-positive rates at nominal `alpha = 0.05`:

| Control | `N = 10` | `N = 25` | `N = 50` |
|---|---|---|---|
| **C2** matched `(L, r)` uncoupled: `N1` all / `N2` num (dev) | 0.022 / 0.018 | 0.030 / 0.024 | — |
| **C1b** matched `(L, r)` uncoupled: `N1` (synth 2,300) | 0.019 | 0.015 | — |
| **C3 (dev numerals, `r = 0` only):** global binomial | **0.102** | **0.135** | **0.191** |
| **C3 (dev numerals, `r = 0` only):** length-only `N0` | **0.082** | **0.111** | **0.183** |
| **C3 (dev numerals, `r = 0` only):** rare-matched `N2` | **0.027** | **0.022** | **0.025** |
| **C3 (synth 2,300, `r = 0` only):** global / `N0` vs rare-matched `N1` | 0.021 / 0.021 vs 0.021 | 0.081 / 0.081 vs **0.021** | 0.100 / 0.100 vs **0.041** |

Naive global and length-only numeral nulls are genuinely miscalibrated when a trigger sign sits in `r = 0` texts (up to 19.1% false positives at `alpha = 0.05`), while rare-and-length matching stays strictly calibrated (`<= 0.041`; conservative below `0.05` due to discrete counts).

---

## Secondary nulls and sensitivity checks

| Check | Result | Null mean | Excess | `p` |
|---|---|---|---|---|
| **N0 (length-only)** M77 HO all / num | 7/10 | 0.0196 / 0.0905 | +0.680 / +0.610 | `9.0e-11` / `3.7e-6` |
| **N0 (length-only)** ICIT all / num | 13/33 | 0.0270 / 0.0394 | +0.367 / +0.355 | `1.3e-12` / `2.2e-11` |
| **N1_devref** M77 HO vs dev all `(L, r)` | 7/10 | 0.0319 | +0.668 | `1.9e-9` |
| **N3 (position + `L` + `r`)** M77 HO num / ICIT num | 7/10 / 13/33 | 0.1146 / 0.0576 | +0.585 / +0.336 | `1.1e-6` / `9.3e-13` |
| **N4 (within-stratum token perm, 10k)** M77 HO / M77 all / ICIT | 7/10 / 12/25 / 13/33 | 0.0257 / 0.0293 / 0.0282 | +0.674 / +0.451 / +0.366 | `1.0e-4` / `1.0e-4` / `1.0e-4` |
| **M77 dev** (`N1` all / `N2` num) | 5/15 (0.333) | 0.0285 / 0.0476 | +0.305 / +0.286 | `3.7e-5` / `1.6e-4` |
| **M77 all** (`N1` all / `N2` num) | 12/25 (0.480) | 0.0279 / 0.0545 | +0.452 / +0.426 | `4.1e-13` / `3.9e-11` |
| **Rare threshold `< 5`** (T1–T4 worst) | 7/10; 13/33 | max 0.1171 (T2) | min +0.351 | max `2.1e-5` |
| **Rare threshold `< 20`** (T1–T4 worst) | 7/10; 13/33 | max 0.0484 (T4) | min +0.346 | max `1.4e-11` |
| **Run-scoped `r_run`** (T1–T4 worst) | 7/10; 13/33 | max 0.0893 (T2) | min +0.352 | max `2.2e-7` |
| **`r_excl_trigger`** (T1–T4 worst) | 7/10; 13/33 | max 0.0892 (T2) | min +0.351 | max `1.9e-7` |
| **Seals only:** M77 HO (`N1` / `N2`) | 5/7 (0.714) | 0.0182 / 0.0927 | +0.696 / +0.622 | `2.0e-8` / `3.3e-5` |
| **Seals only:** M77 all (`N1` / `N2`) | 9/20 (0.450) | 0.0268 / 0.0508 | +0.423 / +0.399 | `5.7e-10` / `2.7e-8` |
| **Seals only:** ICIT (`N1` / `N2`) | 9/25 (0.360) | 0.0306 / 0.0421 | +0.329 / +0.318 | `2.0e-8` / `2.5e-8` |
| **Edit-1 family dedup:** M77 (`N1`) / ICIT (`N1` / `N2`) | 9/20 / 9/20 | 0.0271 / 0.0272 / 0.0402 | +0.423 / +0.423 / +0.410 | `5.9e-10` / `5.4e-10` / `1.5e-10` |
| **Leave-one-site-out** M77 all (`N1` worst: drop Harappa) | 7/20 (0.350) | 0.0270 | +0.323 | `4.3e-7` |
| **Leave-one-site-out** ICIT (`N1` worst: drop Harappa) | 8/25 (0.320) | 0.0296 | +0.290 | `2.9e-7` |
| **Post-1977 ICIT sites absent from M77** (`N1`) | **1/4** (0.250, CI 0.006–0.806) | 0.0353 | +0.215 | `0.135` |

---

## Caveats and falsifier
1. **ICIT is mostly a second transcription, not new objects.** On ICIT sites absent from M77, only 4 non-final `W016` tokens exist (`1/4` followed by `W220`, at Nausharo, `p = 0.135`). True out-of-sample replication on newly excavated objects remains open under frozen prediction P4 (`docs/PREDICTION_REGISTRY.md`).
2. **Sparse zero-count strata in secondary sub-pools.** In four secondary/sensitivity sub-tests where reference pools are small (`N2_m77_ho_horef`, `N3_m77_ho_all`, `thresh_lt20 T2`, `m77_fam_N2`), several matched strata have empirical follower rate `0.0`, causing the exact Poisson-binomial tail to underflow to `0.0` (while `p_mc` hits `1/(B+1)`). Primary `T1`–`T4` do not suffer from this (`0` collapsed strata in `T1`–`T3`, `2` in `T4`; exact and MC null means match to 4 decimal places).
3. **Small `N` on held-out.** Held-out M77 has `N = 10` non-final `M109` occurrences (exact 95% CI on rate: `0.348–0.933`). The point estimate on held-out (`0.70`) is higher than on `dev` (`0.333`, 5/15) and ICIT (`0.394`, 13/33), consistent with sampling variance at `N = 10`.
4. **No semantic or language inference.** Passing this null rules out a rare-sign/length artefact; it does not distinguish a Dravidian asterism (*aṟu-mīn*) from a title, clan name, or measure in any language.
5. **What would falsify the claim:** New inscriptions excavated or published independently of M77/ICIT with at least 10 non-final two-tier six tokens where fewer than 20% are followed by plain fish (`p >= 0.05` against `(L, r)`-matched non-final tokens), or photographic re-inspection showing that `M109`/`W016` was systematically misread before fish signs.

## Hypotheses tested

| Hypothesis | Verdict |
|---|---|
| `M109 -> M59` / `W016 -> W220` is an artefact of text length and rare-sign load | **refuted** (survives all 4 primary `(L, r)`-matched tests, Holm `p = 4.6e-12` to `2.9e-7`; retains 99.4–100.3% of `N0` excess; within-stratum perm `p = 1e-4`) |
| Naive global/length-only numeral nulls are miscalibrated for `r = 0`-concentrated signs | **supported** (C3 false-positive rate 10.2–19.1% global, 8.2–18.3% length-only vs 2.2–2.7% under rare-matched `N2`) |
| The `(L, r)`-matched test has high power to detect a real fixed pair at `N = 10` | **supported** (C1a power 98.6% `N1`, 95.2% `N2` at `p_true = 0.48`; C1b 2,300-text synthetic corpus 97.2%) |
| The finding replicates on post-1977 sites absent from M77 alone | **inconclusive** (`1/4` = 0.25 vs 0.035 null, `p = 0.135`; severely underpowered at `n = 4`) |

## Next experiments
- Score frozen forward prediction P4 (`M109 -> M59 >= 0.30`) as newly published inscriptions are added to `experiments/new_finds/new_texts.csv` (starter task S9).
- Apply the same `(L, r)`-matched numeral null (`N2`) to other candidate fixed pairs (such as `M102 -> M59`, three + fish, and top fixed pairs in `experiments/core_semantics/`), where `C3` shows naive numeral nulls over-flag `r = 0`-concentrated triggers.
