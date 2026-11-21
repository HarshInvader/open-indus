# Pre-registration: Recchia & Louwerse 2016 rerun

Written 2026-11-21, before any geography fit, null, bootstrap or planted run was scored. Only the analysis-set sizes (`experiments/recchia_rerun/sizes.log`) were looked at. Code: `experiments/recchia_rerun/rr.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `recchia_rerun`).

## Target

Recchia, G. L. & Louwerse, M. M. 2016. Archaeology through computational linguistics: inscription statistics predict excavation sites of Indus Valley artifacts. *Cognitive Science* 40(8): 2065-2080. doi:10.1111/cogs.12311.

- Full text: not read. The publisher PDF link returned HTTP 403 with a bot challenge to our generic client; we did not try to get round it. We work from the abstract (ERIC EJ1120525) and from the method summary in the brief: LSA document vectors, summed into five site vectors (Mohenjo-daro, Harappa, Chanhu-daro, Lothal, Kalibangan), site cosines, MDS, compared with real coordinates; seals (n = 1,936) and sealings (n = 723) separately.
- Everything below that the abstract does not fix (weighting, dimensions, MDS type, fit statistic) is our choice, frozen here. A mismatch with their exact settings is a limit of this rerun, stated in the results.

## Data

- **Primary:** M77 (Mahadevan 1977 concordance), every object side of the five sites, complete and incomplete, `|` and `#` removed from the terms. Sizes: seals 1,823 (theirs 1,936), sealings 716 (theirs 723). Chanhu-daro has 3 sealings.
- **Variants:** M77 complete only; ICIT (seal = any `SEAL*` type except `SEAL:R`; sealing = `SEAL:R`); near-copy removal with `experiments/fish_tick_closer_v2/dedup.py::greedy`, per site and object type (never `corpus/build.py::_close`). Sites with fewer than 2 texts in a set are dropped (ICIT sealings: Chanhu-daro, 1 text).
- Coordinates (lat, lon): Mohenjo-daro 27.3243, 68.1357; Harappa 30.6280, 72.8640; Chanhu-daro 26.1740, 68.3240; Lothal 22.5215, 72.2491; Kalibangan 29.4730, 74.1300. Equirectangular km for Procrustes; great-circle km for distance correlations.

## Method (frozen)

- **LSA space:** terms = signs; log-entropy weighting (local log(1 + tf), global 1 + Σ p log p / log N); SVD of the weighted matrix of all texts of that corpus (every object type and site); k = 100 (capped at rank). Document vector = weighted term vector · V_k.
- **Site vector:** sum of the site's document vectors in the analysed set.
- **Configuration:** cosine distance between site vectors → classical (Torgerson) 2-D MDS.
- **Primary statistic:** R_proc, the Procrustes / bidimensional-regression correlation between the MDS points and the site coordinates, with rotation, reflection and scaling (0 to 1). Also reported: r_mds (MDS interpoint distance vs great-circle distance) and r_cos (cosine distance vs great-circle distance, no MDS), Pearson over the 10 pairs.
- Seed 20261130.

## Tests

1. **Exact assignment test:** R_proc for all 120 assignments of the five coordinates to the five sites; p_exact = share ≥ observed (minimum 1/120). Four sites: 24 assignments.
2. **Site-label permutation null:** shuffle site labels within the analysed set (one object type), keeping site sizes; 5,000 permutations; p_label = (1 + #null ≥ obs) / 5,001.
3. **Bootstrap over texts:** resample texts with replacement within each site, 1,000 times; 95% interval of R_proc and share of resamples with p_exact ≤ 0.05.
4. **Leave one site out:** the four-site fit for each dropped site, with its own 24-assignment test and a 2,000-permutation label null.
5. **Near-copy removal:** rerun 1-2 on the de-duplicated set.
6. **Size-matched:** 1,000 draws of n texts per site without replacement, n = the smallest site with at least 20 texts (sites under 20 are left out: Chanhu-daro sealings). Matched null: the same draws with labels shuffled among the drawn texts. p_matched = share of null draws ≥ the median real R_proc.
7. **Mohenjo-daro vs Harappa in the same space:** cosine distance between the summed vectors of the smaller site and a size-matched draw of the larger, against two disjoint random sets of the larger site at the same n (1,000 draws each).
8. **Sensitivity (reported, not verdict-bearing):** k = 20, 50, full rank; unit-length document vectors before summing; LSA space fitted on the analysed set only; M77 complete only; ICIT; ICIT de-duplicated.

## Planted-answer gate

- Background: the real primary analysed set with site labels shuffled (sizes kept), so no real site signal is left.
- Plant: five new 10-sign stocks, one per site. Each token of a site-s text is replaced with probability q by a sign from the stock of site t, with t drawn with weight exp(−d_st / 300 km). Nearby sites therefore share local signs: a geographic gradient.
- The space is refitted with the planted texts. Detected = p_exact ≤ 0.05 and p_label ≤ 0.05 (1,000 permutations). 100 replicates at q = 0.05, 0.10, 0.15, 0.20.
- **Gate passes at ≥ 80% detection at q = 0.15**, per object type. If the gate fails for an object type, a non-significant result there is "underpowered", not a negative.

## Verdict rules (frozen)

- **Replicates (per object type):** primary p_exact ≤ 0.05.
- **Survives the null (per object type):** primary p_exact ≤ 0.05 and p_label ≤ 0.05.
- **Fails:** not surviving with the gate passed. **Underpowered:** not surviving with the gate failed.
- **Overall:** their geography result survives if seals or sealings survive.
- **Drivers**, for each object type that survives:
  - *sealings-driven:* sealings survive and seals do not;
  - *site-driven:* a site whose removal makes the four-site p_label > 0.05; if any such site is Chanhu-daro, Lothal or Kalibangan, the result is "driven by outer sites";
  - *size-dependent:* p_matched > 0.05;
  - *copy-dependent:* the de-duplicated set has p_label > 0.05.
- **Conflict with Mohenjo-daro = Harappa seal uniformity:** only if, for M77 seals, the median Mohenjo-daro vs Harappa distance is above the 95th percentile of the within-site distances (test 7). Otherwise "no conflict": a geography fit that is not carried by the Mohenjo-daro vs Harappa seal pair does not contradict our result.
- No threshold, k, statistic or data choice may change after scoring. Any fix goes in a dated deviation with a re-hash.

## Compute

`board/run.sh` (repo lock), plus the Indus lock in `open-citizen-science/.local/`; nice 20; at most 2 BLAS threads; one job; nothing detached.
