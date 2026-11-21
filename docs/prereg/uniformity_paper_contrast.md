# Pre-registration: Ur III minus Indus gap contrast (review 2, item R10)

Written 2026-11-21, before the contrast below was computed. Code: `experiments/uniformity_paper/revision/contrast.py`.
Both files are hashed in `docs/prereg/HASHES.txt`, tag `uniformity_paper_contrast`.

## What has been seen before this file

- Every marginal bootstrap percentile in `experiments/uniformity_paper/revision/results.json` (`boot`), as reported in
  the paper: Indus Δfloor 97.5th percentiles +0.106, +0.106, +0.123; Ur III Δfloor 2.5th percentiles +0.107 to
  +0.220. So it is known that the marginal intervals touch or overlap. The paired difference has not been computed.
- No new classifier runs. This is arithmetic on `draws_boot.jsonl` (200 replicates per condition, already written).

## Why pairing is valid

`rev.py run_boot` seeds each replicate with `rng_for("boot", cond, rep)`, so each condition is resampled from its
own pool with its own random stream. The Ur III and Indus replicates are independent draws, and the bootstrap
distribution of the difference is the distribution of (Ur III replicate − Indus replicate). Pairing replicate i with
replicate i is one valid sample of 200 differences; all 200 × 200 combinations use the same two marginals and give a
smoother estimate. Both are reported; the index-paired one is primary.

## Statistic

Per replicate, as in `report.py r1`: Δfloor = median(b) − median(w). Contrast D = Δfloor(Ur III) − Δfloor(Indus).

- Primary: Ur III = `REF_ur3_U_reign` (ORACC, Umma reigns: the step-2 primary Ur III floor and the lowest Ur III
  median). Indus = each of `MDHA_m77_seal`, `MDHA_icit_seal`, `MDHA_icit_sealtype`. Three contrasts.
- Secondary: every one of the six structural Ur III floors (`REF_ur3_*`, `REF_cdli_*`) against each of the three
  Indus pools (18 contrasts), and the two unicorn pools (`UNI_*`) against `REF_ur3_U_reign`.

## Rules (fixed now)

- 95% CI = 2.5th and 97.5th percentiles of D.
- "Ur III above Indus": 2.5th percentile of D > 0.
- "Ur III above Indus by the margin": 5th percentile of D ≥ 0.05 (same one-sided rule as R1 references).
- Otherwise "contrast not established" for that pair.
- No correction across the 3 primary contrasts; all are reported. The headline sentence in the paper uses the primary
  three only, and reports the smallest 2.5th percentile among them.
