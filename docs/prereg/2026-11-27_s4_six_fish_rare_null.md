# Pre-registration: rare-sign- and length-matched null for 'six then fish' (Starter task S4)

Written before any rare-sign-matched statistic, sensitivity test, or planted control below is computed on M77 held-out or ICIT.

**Known beforehand** (already published in `README.md`, `experiments/revalidation/RESULTS.md`, and `experiments/redteam/RESULTS.md`):
- M77 v2 held-out: two-tier six `M109` is followed by plain fish `M59` in 7 of 10 non-final occurrences against a dev unigram base rate of 3.1% (`p = 2.8e-9`).
- All distinct M77 texts: `M109 -> M59` in 12 of 25 non-final occurrences (`0.48` vs `0.06` other-numeral base, `p = 9e-9`).
- Native ICIT distinct texts: `W016 -> W220` in 13 of 33 non-final occurrences (`p = 4e-9`).
- Exploratory inspection prior to sealing was restricted strictly to M77 v2 `dev` (1,699 distinct texts; 15 non-final `M109` occurrences, 5 followed by `M59`) to verify `(L, r)` stratum counts and check whether `P(next = M59)` depends on rare-sign load. On `dev`, `P(next = M59)` drops sharply with rare-sign load `r` (number of tokens with `count_dev < 10`): across all non-final tokens from `0.0405` (`r = 0`) to `0.0159` (`r = 2`), and across other short numerals from `0.1134` (`r = 0`) to `0.0000` (`r >= 2`).

## Claim under test
README #5: Two-tier six (`M109` in M77; `W016` in native ICIT) immediately followed by plain fish (`M59` in M77; `W220` in native ICIT) is a fixed pair.

**Confound tested:** Earlier tests compared `P(next = M59 | M109)` against the corpus-wide unigram rate of `M59` or the pooled short-numeral follower rate without controlling for how many rare signs each text carries (`r`) or the length of the text (`L`). Because `M59` is a common sign (`count_dev = 234`), texts with low rare-sign load carry higher baseline rates of `M59` following any sign—and especially following numerals. Conversely, texts with high rare-sign load carry lower baseline rates of `M59`. Starter task S4 asks whether the six-then-fish result survives a null matched on both rare-sign load and text length, paralleling the red team of the round-seal finding (`experiments/redteam_round_order/`).

## Data, counting unit, and sign sets
- **Counting unit:** Distinct texts (`distinct()` from `corpus/load.py` for M77; first-seen distinct `tuple(seq)` for ICIT, matching `experiments/redteam/r2_sixfish.py`). Never objects with mould duplicates.
- **Runs:** Contiguous break-free runs (`runs(seq)`, splitting at `|` and `#`). Only non-final tokens within runs of length `>= 2` are eligible trigger occurrences.
- **M77 splits:** Frozen `dev_heldout(version=2)` (1,699 dev distinct texts, 571 held-out distinct texts; zero edit-distance-1 family leakage).
  - Target pair: `M109 -> M59`.
  - Short-numeral set `NUM_M` (identical to `r2_sixfish.py`): `{M97, M98, M102, M104, M105, M106, M107, M108, M109, M110, M111, M112, M114, M115, M116, M117, M121}`. Other short numerals: `NUM_M \ {M109}`.
- **ICIT native corpus** (independent second transcription + post-1977 sites): all distinct ICIT texts.
  - Target pair: `W016 -> W220`.
  - Short-numeral set `NUM_W` (identical to `r2_sixfish.py`): `{W001..W020, W025, W026, W027, W028} \ {W002, W012}`. Other short numerals: `NUM_W \ {W016}`.

## Rare-sign load `r`, text length `L`, and stratum collapsing
For any distinct text `t`, let `toks(t)` be all sign tokens across its break-free runs (excluding `|` and `#`):
- **Text length:** `L(t) = len(toks(t))`, capped at `L_bin = min(L(t), 9)` (matching `redteam_round_order`).
- **Rare-sign load:** `r(t)` = number of tokens `s` in `toks(t)` with reference count `< 10`, capped at `r_bin = min(r(t), 3)` (matching `redteam_round_order`):
  - For M77 `dev` and M77 `heldout`: reference count is strictly `count_dev(s)` across the 1,699 M77 v2 `dev` distinct texts (zero leakage from held-out into the rareness definition).
  - For ICIT native: reference count for text `t` is the leave-one-text-out count across all other distinct ICIT texts, `count_icit_total(s) - count_in_t(s) < 10` (deterministic, zero self-leakage, no fold-seed dependence).
- **Stratum collapsing** (exact rule from `redteam_round_order`): for a target stratum `(L_bin, r_bin)`, if the reference pool has `< 5` eligible non-final tokens, decrement `r_bin` down to `0`; if still `< 5`, decrement `L_bin` down to `1` and search `r_bin` down to `0` at each length. The number of collapsed occurrences is logged for every test.

## Statistic and Primary tests (4 tests, Holm-Bonferroni corrected)
For `N` non-final occurrences of the target trigger (`M109` or `W016`), the statistic is `k_obs` = number of occurrences immediately followed by the target fish (`M59` or `W220`), equivalently `rate_obs = k_obs / N`.

Under a stratified reference pool `pools[key]`, each target occurrence `i = 1..N` is mapped to its stratum `k_i = key(L_i, r_i)` with stratum fish-follower rate `p_i`.
- **Exact p-value (`p_exact`):** One-sided Poisson-binomial tail `P(sum_{i=1}^N Bernoulli(p_i) >= k_obs)` computed by exact dynamic programming (exact distribution of independent with-replacement stratum draws, avoiding any Monte Carlo p-value floor).
- **Monte Carlo cross-check (`p_mc`, `B = 100,000` draws):** Draws `B = 100,000` matched samples of size `N` from the strata (without replacement within a stratum whenever the stratum holds at least as many reference tokens as needed in that stratum), reporting `(1 + sum(k_null >= k_obs)) / (B + 1)`, null mean rate, and rate excess `rate_obs - null_mean`.
- Primary Holm-Bonferroni adjustment uses `p_exact` across the 4 primary tests:
  - **T1 (M77 held-out v2, N1_all):** `M109 -> M59` on M77 v2 held-out vs all non-final non-`M109` tokens in M77 v2 held-out matched on `(L, r)`.
  - **T2 (M77 held-out v2, N2_num):** `M109 -> M59` on M77 v2 held-out vs non-final other short-numeral (`NUM_M \ {M109}`) tokens in M77 v2 `dev` matched on `(L, r)` (using `dev` as reference pool so numeral `(L, r)` strata are well-populated without tuning on held-out).
  - **T3 (ICIT native, N1_all):** `W016 -> W220` on all distinct ICIT texts vs all non-final non-`W016` tokens in distinct ICIT texts matched on `(L, r)`.
  - **T4 (ICIT native, N2_num):** `W016 -> W220` on all distinct ICIT texts vs non-final other short-numeral (`NUM_W \ {W016}`) tokens in distinct ICIT texts matched on `(L, r)`.

## Secondary and sensitivity checks (reported, not in the primary Holm family)
1. **Length-only null `N0` (`L_bin` only)** for T1–T4: quantifies how much rare-sign matching shifts the null rate and excess (`diff_N1 / diff_N0`).
2. **Alternative reference pools for M77 held-out:** `N1_devref` (held-out `M109` vs M77 `dev` all non-final `(L, r)` pool) and `N2_horef` (held-out `M109` vs held-out other-numeral `(L, r)` pool).
3. **Position + length + rare-load null `N3` (`(L_bin, r_bin, is_run_initial)`)** for T1–T4: controls for whether the trigger stands run-initial (`i == 0`) vs medial (`i > 0`).
4. **Within-stratum token permutation null `N4` (`B = 10,000` draws):** permutes all sign tokens within each `(L_bin, r_bin)` stratum across texts (preserving exact text lengths, run boundaries, stratum rare-sign loads, and exact stratum counts of trigger and fish) on M77 held-out, M77 all, and ICIT native.
5. **M77 `dev` and M77 `all`** under `N0`, `N1`, `N2` (descriptive context).
6. **Rare-definition sensitivity** on T1–T4:
   - rareness thresholds `< 5` and `< 20` (in addition to `< 10`);
   - `r_run` (rare tokens inside the break-free run rather than full text);
   - `r_excl_trigger` (rare tokens in the text excluding the trigger token itself).
7. **Object-type, near-duplicate family, and site sensitivity:**
   - **Seals only** (M77 `object_type == "seal"` on held-out and all-M77; ICIT `type.startswith("SEAL")`) under `N1` and `N2`;
   - **Edit-distance-1 family deduplication** (single-linkage Levenshtein `<= 1` over distinct sequences, one representative per family) on M77 all and ICIT;
   - **Leave-one-site-out** on M77 all and ICIT, plus **ICIT sites absent from M77**;
   - **Exact Clopper-Pearson 95% CI** on `rate_obs`.

## Planted controls (1,000 replicates each; zero held-out tuning)
All controls use fixed deterministic RNG seeds (`np.random.default_rng`) and no unsorted set iteration (verified byte-identical across `PYTHONHASHSEED` values). Stratum profiles for `C1a` and `C2` are drawn from M77 `dev`'s empirical `M109` `(L, r)` distribution (`n = 15`) so no held-out information enters control design.
- **C1a (Real-corpus-embedded planted fixed pair, `N = 10` held-out size and `N = 25` full-corpus size):**
  On M77 `dev` (and on random 571-text subsamples of `dev` matching held-out size), draw `N` texts from `M109`'s dev `(L, r)` strata, pick one non-final slot per text, plant synthetic trigger `A*`, and set its follower to `M59` with coupling probability `p_true` in `{0.25, 0.35, 0.48, 0.70}` (otherwise keeping the natural follower). Score each replicate with `N1` and `N2` (`p_exact`). Report power at `alpha = 0.05` and `alpha = 0.01`.
- **C1b (Pure synthetic corpus of 2,300 distinct texts, mean ~4.5 signs):**
  Generate a synthetic corpus of 2,300 distinct texts matching M77's length distribution and Zipfian sign frequencies, with two latent regimes (common-sign formulaic texts with `r = 0` and higher `B*` rate, vs rare-heavy texts with `r >= 1` and lower `B*` rate, matching the Indus `r`-gradient seen on dev). Plant `(A*, B*)` at `N = 10` and `N = 25` with `p_true` in `{0.25, 0.35, 0.48, 0.70}` and report power under `N1`.
- **C2 (Calibration control — uncoupled sign in matched `(L, r)` strata):**
  Same as `C1a` and `C1b` with `p_true = 0` (natural follower untouched). Report false-positive rate at `alpha = 0.05` under `N0`, `N1`, and `N2`.
- **C3 (Rare-load confounding control — uncoupled sign concentrated in `r = 0` texts):**
  Plant an uncoupled sign `A*` (`p_true = 0`) exclusively in `r = 0` texts (and in `r = 0` other-numeral slots for `N2`) at `N = 10`, `25`, and `50`, on both M77 `dev` and the two-regime 2,300-text synthetic corpus. Compare false-positive rates at `alpha = 0.05` under (i) naive corpus-wide binomial null, (ii) length-only null `N0`, and (iii) rare-and-length-matched null `N1` / `N2`.

## Pass / fail decision rule
- **SURVIVES:**
  1. All 4 primary tests (`T1`–`T4`) have Holm-adjusted `p_exact < 0.01`, AND
  2. Planted control `C1a` power at `N = 10`, `p_true = 0.48` is `>= 0.80` under both `N1` and `N2`, AND
  3. Calibration control `C2` false-positive rate at `alpha = 0.05` is `<= 0.10` under both `N1` and `N2`, AND
  4. Rate excess under `N1` and `N2` retains at least half of the length-only `N0` excess (`diff_N1 >= 0.5 * diff_N0` and `diff_N2 >= 0.5 * diff_N0`) across T1–T4, AND
  5. Effect remains significant (`p_exact < 0.01`) on seals-only (M77 all seals and ICIT seals) and across rare-threshold sensitivities (`< 5`, `< 20`, `r_run`, `r_excl_trigger`).
- **FALLS:**
  Any primary test (`T1`–`T4`) has unadjusted `p_exact >= 0.05` while `C1a` power at `N = 10`, `p_true = 0.48` is `>= 0.80`.
- **INCONCLUSIVE:**
  `C1a` power at `N = 10`, `p_true = 0.48` is `< 0.50`, or `C2` calibration fails (`FP > 0.10`).
- **WEAKENS:**
  Anything between `SURVIVES` and `FALLS` (for example, `0.01 <= p_holm < 0.05`, or rare-sign matching removes more than half of the excess, or seals-only / threshold sensitivities fail).

## Reporting commitment
Regardless of outcome (`SURVIVES`, `WEAKENS`, `FALLS`, or `INCONCLUSIVE`), all primary, secondary, sensitivity, and planted-control results will be reported in `experiments/six_fish_rare_null/RESULTS.md`, `experiments/six_fish_rare_null/results.json`, and `docs/test_ledger.csv`, with no post-hoc changes to this frozen pre-registration or to the frozen test script.

## Scope limits
No language, sound-value, or semantic claim (such as Parpola's *aṟu-mīn* "Pleiades") is tested here. This experiment tests only whether the observed adjacency of two-tier six (`M109` / `W016`) and plain fish (`M59` / `W220`) survives a rare-sign- and length-matched null.
