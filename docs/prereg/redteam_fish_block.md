# Pre-registration: redteam_fish_block (red team of reg_findspot F3 ticked-fish block clustering)

Registered 2026-11-15 in `experiments/redteam_fish_block/` BEFORE any of the tests below were run. Hash in `docs/prereg/HASHES.txt` (tag `redteam_fish_block`).

Claim attacked: "Ticked fish (M60, M66, M68, M71, M73) cluster by block at Mohenjo-daro (Mackay 1938 DK-G): G=36.2, p=0.0007, BH q=0.007 (family of 10); house 12/V holds 4 of 21 ticked-fish seals; blocks 1 and 7 hold 1 of 151; plain fish do not cluster."

Already seen when writing this: reg_findspot RESULTS/test.py/explore.json; the list of the 21 ticked-fish seals with findspot, depth, text, CISI number and register dimensions; depths of blocks 3, 9, 13, 19 seals; the 7 `block_junk_stripped` rows. No test below has been run.

Data: `experiments/reg_findspot/findspots.csv` (read only), M77 via `corpus.load`, `experiments/old_registers/registers.csv`, ICIT via `corpus.load.icit_texts()`, bridge `sources/shaunmortal_indus/data/bridge_WM.json` (data only). Primary statistic and units exactly as reg_findspot F3 level A (blocks with >= 8 text seals, other numbered blocks pooled as 'other', streets one unit; G; null permutes unit labels within band5; 10,000 permutations; one-sided upper p) unless stated.

## A1 Depth / period confound
- a. Description: ticked-fish (TF) rate vs depth (logistic slope, permutation p, two-sided) in FEM; also in all M77 Mohenjo-daro seals with a level. Depth range (median, IQR) per block; Kruskal-Wallis of depth across level-A units.
- b. Finer depth strata for the permutation null: band 3 ft, 2 ft, 1 ft, and depth deciles.
- c. Within-stratum statistic: G summed over 5-ft bands (block heterogeneity computed inside each band), null within band.
- d. Depth-covariate parametric null: logistic TF ~ natural cubic spline of depth (3 df) fitted on all level-A seals; simulate TF 10,000 times from fitted probabilities; p = share of simulated G >= observed G.
- Confound verdict: depth explains the clustering if any of b-d gives p > 0.05.

## A2 Batch / one carver / text family
- a. Describe the 4 house-12/V texts: pairwise edit distance, shared n-grams, register size, depth.
- b. Family collapse: within a level-A unit, TF seals are one family if (i) identical or edit distance <= 1, or (ii) [strict] they share the bigram (sign before TF, TF sign). Keep one seal per family (the shallowest), drop the rest, re-run the primary test. Families counted.
- Batch verdict: clustering reduces to batches if collapsed (strict) p > 0.05.

## A3 Statistic, null, multiplicity, small counts, OCR
- a. Multiplicity: BH and Holm of the TF block p over (i) all 21 reg_findspot confirmatory tests, (ii) 21 + the 140 exploratory single-sign scan p-values + 2 E1 tests (163 total).
- b. Alternative statistics/unit definitions: Pearson chi-square, max standardized residual, min block size 5 / 15 / 20, streets excluded, 'other' excluded, no depth stratification. Report all p (no selection).
- c. Leave-one-house-out (each house holding a TF seal) and leave-one-block-out (each level-A unit) on the primary test; report max p.
- d. OCR: the 3 TF seals whose block came from junk-stripping (serials 234, 307, 417): (i) drop them, (ii) reassign 'i 3' -> 13 and 'I 9' -> 19.
- Verdict: fragile if max LOHO/LOBO p > 0.05 or more than one variant in b/d gives p > 0.05; multiplicity fails if (ii) q > 0.05.

## A4 Allograph / catalogue coding
- a. Conditional on fish: among seals with any fish sign (TF or plain M59, M65, M67, M70, M72), test block clustering of 'ticked' (primary test on this subset).
- b. Independent coder: for FEM seals linked to ICIT, compare M77 tick coding with Wells coding (ticked-fish W signs via the bridge: W signs mapped to M60/M66/M68/M71/M73 vs plain fish). Report agreement; re-run primary test on the ICIT-linked subset using the ICIT coding (low power expected).
- c. Contiguity: are TF seals clustered in FEM serial / M77 text number / CISI number more than chance (mean gap to nearest TF neighbour vs 10,000 random sets of 21 seals)? Association of serial position with block is reported.
- Verdict: coding artefact supported if (a) p > 0.05 while the unconditional test holds AND (b) agreement < 80%, or if TF seals are contiguous in catalogue order (p < 0.05) beyond what depth sorting gives.

## A5 Replication (low power acknowledged)
- a. Mohenjo-daro outside FEM (M77 MD seals not in 2000-series; units = M77 locus with >= 8 seals, others pooled; null within M77-level 5-ft band).
- b. Harappa M77 seals (units = M77 locus 40-59; same rule).
- c. Chanhu-daro CE squares: descriptive only.
- Power: for a and b, plant the FEM effect size (TF rate x6 in one unit with >= 15 seals) and report share of 200 plants at p <= 0.05.
- Replicates if a or b p < 0.05 (Holm over 2).

## Overall verdict rule
- SURVIVES: no attack verdict triggered and multiplicity (ii) q < 0.05.
- WEAKENED: the signal holds under depth control (A1) and family collapse (A2) at p < 0.05, but at least one of: LOO/variant fragility, multiplicity (ii) q > 0.05, failed replication with power >= 0.5.
- FAILS: A1 or A2 verdict triggered, or a coding artefact (A4) supported.

All tests here are red-team checks; ledger rows `rtfb_*`, mode 'redteam'.
