# Recchia & Louwerse 2016 rerun: results

Prereg: `docs/prereg/recchia_rerun.md`, hashed with `rr.py` in `docs/prereg/HASHES.txt` (tag `recchia_rerun`, 2026-11-21T18:01:17Z) before anything was scored. Only the set sizes (`sizes.log`) had been looked at. One run, seed 20261130, no code change after hashing. Raw numbers: `results.json`, `run.log`. Ledger: `ledger_rows.csv`.

## Verdict

**Their geography result does not reappear in our rerun. By the frozen rule the verdict is "underpowered", not "refuted". There is no conflict with Mohenjo-daro = Harappa seal uniformity.**

- **Seals (M77, 1,823 texts).** The site map is no closer to real geography than chance.
  - The real assignment ranks 45th of the 120 ways of assigning the five coordinates to the five sites (p_exact 0.375).
  - It is below the median of the site-label shuffle (R_proc 0.688 vs null median 0.703; p_label 0.61).
  - No sensitivity variant reaches p_exact ≤ 0.05 (range 0.21-0.41). That covers 20, 50 or all LSA dimensions, unit-length document vectors, a space fitted on the seals only, complete texts only, ICIT, and de-duplication.
- **Sealings (M77, 716 texts).** The five sites' sealing vectors differ more than shuffled labels (p_label 0.025; 0.0002 after de-duplication). But the differences do not line up with geography (p_exact 0.54; 0.15 after de-duplication).
  - This matches our earlier finding that sealings differ between sites. The difference is not a map.
- **Why the verdict is "underpowered" and not "fails".** The method itself is weak with five points.
  - A planted geographic gradient of local signs replacing 15% of tokens is detected in 30% of runs for seals and 0% for sealings. The bar was 80%.
  - Seals reach 80% only at 20% of tokens. Sealings stay at 1%, because Chanhu-daro has three sealings.
  - So a real but modest geographic signal could have been missed. A strong one (20% of tokens or more, for seals) is ruled out.
- **Drivers.** Neither object type survives the null, so the frozen driver rules (sealings, outer sites, size, near copies) do not apply. Descriptively:
  - Leaving out Lothal is the only case where the four remaining sites take the best of 24 assignments, for both seals and sealings (p_exact 0.042, the smallest possible). The label null does not back this up for seals (p_label 0.39).
  - Size-matched draws (56 seals per site) sit exactly on their null (median R_proc 0.619 vs 0.609; p_matched 0.48).
  - Near-copy removal changes nothing for seals. For sealings it makes the "sites differ" signal stronger, but still not geographic.
- **Mohenjo-daro vs Harappa seals in their LSA space.** Their cosine distance at matched n (356) has a median of 0.0621. Two disjoint halves of Mohenjo-daro give a median of 0.0492 and a 95th percentile of 0.0624.
  - By the frozen rule this is "no conflict", but only just: the margin is 0.0003, and 48% of the between draws exceed the within 95th percentile.
  - After de-duplication the margin is clearer (0.0620 vs 0.0671; 24% of draws above).
  - Sealings, by contrast, are far apart (0.361 vs a within 95th percentile of 0.128): a clear "differs", as before.

In plain words: when we rebuild their pipeline as closely as the abstract allows, Indus seal texts do not place the five sites on a map. The pipeline is also too blunt to have found a modest geographic signal. So their result is neither confirmed nor ruled out. Either way it does not rest on Mohenjo-daro and Harappa seals, which sit at or just inside their within-city floor here too.

## Limits

- **We did not read their full text.** The publisher PDF returned HTTP 403 with a bot challenge to our generic client. We did not try to get round it. We worked from the abstract (ERIC EJ1120525) and the method summary in our brief.
- **Settings are our own.** Weighting, dimensions, MDS type and fit statistic were frozen by us. Their settings may differ, and their reported fit may come from a choice we did not try: other terms (such as sign n-grams), non-metric MDS, or another fit measure. Several dimension and weighting variants all agree here.
- **Corpus size.** Our M77 seal set is 1,823 texts against their 1,936. Sealings are 716 against 723.
- **Chanhu-daro has 3 sealings (M77) and 1 in ICIT.** Any five-site sealing map rests on three texts for one of its five points.
- **The gate's gradient is shallow.** A 300 km kernel mostly gives each site its own stock, and only Mohenjo-daro and Chanhu-daro (about 130 km apart) share strongly. A steeper or wider gradient might be easier to detect. We did not change the gate after seeing the data.

## Safe wording for the paper

> Recchia & Louwerse (2016) report that LSA site vectors of Indus inscriptions recover the relative positions of five sites. In our reimplementation from their published description (LSA with log-entropy weighting, summed site vectors, cosine distances, classical MDS, Procrustes fit to site coordinates; M77, seals and sealings separately), the seal configuration was no closer to geography than chance: the real site-to-coordinate assignment ranked 45th of 120 (p = 0.38), and the fit was below a site-label permutation null (p = 0.61). This held across dimensionality, weighting, editor (ICIT) and near-duplicate removal. Sealing vectors differed between sites beyond the label null (p = 0.025) but not in a geographic arrangement (p = 0.54). With five points the test is weak: a planted geographic gradient affecting 15% of seal tokens was detected in 30% of simulations, so we do not claim that their result is false. It does not, however, depend on Mohenjo-daro versus Harappa seals, whose distance in the same LSA space lies at the edge of the within-Mohenjo-daro range (median 0.062 against a 95th percentile of 0.062; 0.062 against 0.067 after near-duplicate removal). We could not consult their full text, and their exact settings may differ.

Do not write:
- "Recchia & Louwerse's result does not replicate" without the power caveat. The frozen verdict is "underpowered".
- "inscription statistics carry no geographic information". Sealings do differ between sites. They are just not arranged like the map.
- "Mohenjo-daro and Harappa seals are identical in LSA space". They sit at the edge of the within-site range, not inside it.

## Tables

### Primary fits (M77, LSA k = 100, corpus-wide space)

| set | n per site (MD, HA, CD, LO, KB) | R_proc | r_mds | r_cos | rank / 120 | p_exact | label null median / q95 | p_label |
|---|---|---|---|---|---|---|---|---|
| seals | 1259, 356, 58, 94, 56 | 0.688 | 0.041 | 0.089 | 45 | 0.375 | 0.703 / 0.773 | 0.613 |
| seals, de-duplicated | 1066, 339, 56, 92, 54 | 0.679 | 0.022 | 0.074 | 46 | 0.383 | 0.700 / 0.770 | 0.652 |
| sealings | 154, 431, 3, 99, 29 | 0.610 | −0.258 | −0.103 | 65 | 0.542 | 0.482 / 0.589 | 0.025 |
| sealings, de-duplicated | 93, 201, 3, 59, 21 | 0.778 | 0.216 | 0.041 | 18 | 0.150 | 0.502 / 0.610 | 0.0002 |

R_proc = Procrustes (bidimensional regression) correlation of the 2-D MDS with site coordinates. r_mds = MDS distances vs great-circle km. r_cos = cosine distances vs great-circle km (10 pairs).

### Planted geographic gradient (share detected, 100 runs each; bar 80% at q = 0.15)

| q (share of tokens) | 0.05 | 0.10 | 0.15 | 0.20 | gate |
|---|---|---|---|---|---|
| seals | 0.00 | 0.06 | **0.30** | 0.80 | fail |
| sealings | 0.00 | 0.00 | **0.00** | 0.01 | fail |

### Bootstrap over texts (1,000 resamples)

| set | median R_proc | 95% interval | share with p_exact ≤ 0.05 |
|---|---|---|---|
| seals | 0.686 | 0.577-0.772 | 0.000 |
| seals, de-dup | 0.678 | 0.560-0.765 | 0.003 |
| sealings | 0.574 | 0.397-0.736 | 0.000 |
| sealings, de-dup | 0.665 | 0.406-0.825 | 0.022 |

### Leave one site out (24 assignments; label null 2,000)

| dropped | seals R_proc | rank / 24 | p_label | sealings R_proc | rank / 24 | p_label |
|---|---|---|---|---|---|---|
| Mohenjo-daro | 0.757 | 10 | 0.573 | 0.632 | 19 | 0.524 |
| Harappa | 0.862 | 9 | 0.476 | 0.737 | 12 | 0.013 |
| Chanhu-daro | 0.646 | 16 | 0.887 | 0.728 | 10 | 0.350 |
| Lothal | 0.766 | **1** | 0.387 | 0.759 | **1** | 0.120 |
| Kalibangan | 0.758 | 12 | 0.118 | 0.816 | 10 | 0.000 |

### Size-matched draws (1,000; sites with ≥ 20 texts)

| set | sites | n per site | median R_proc | matched null median / q95 | p_matched | share p_exact ≤ 0.05 |
|---|---|---|---|---|---|---|
| seals | 5 | 56 | 0.619 | 0.609 / 0.866 | 0.48 | 0.011 |
| seals, de-dup | 5 | 54 | 0.606 | 0.611 / 0.870 | 0.52 | 0.004 |
| sealings | 4 (no CD) | 29 | 0.739 | 0.722 / 0.945 | 0.46 | 0.000 |
| sealings, de-dup | 4 (no CD) | 21 | 0.760 | 0.731 / 0.945 | 0.45 | 0.055 |

### Mohenjo-daro vs Harappa, cosine distance of summed LSA vectors (1,000 draws)

| set | n | between median | within (larger site) median / q95 | share between > q95 | conflict (frozen rule) |
|---|---|---|---|---|---|
| seals | 356 | 0.0621 | 0.0492 / 0.0624 | 0.48 | no (margin 0.0003) |
| seals, de-dup | 339 | 0.0620 | 0.0523 / 0.0671 | 0.24 | no |
| sealings | 154 | 0.361 | 0.085 / 0.128 | 1.00 | yes |
| sealings, de-dup | 93 | 0.258 | 0.184 / 0.237 | 0.80 | yes |

### Site cosine distances, M77 seals (primary)

| | Harappa | Chanhu-daro | Lothal | Kalibangan |
|---|---|---|---|---|
| Mohenjo-daro | 0.046 | 0.169 | 0.119 | 0.222 |
| Harappa | | 0.226 | 0.156 | 0.251 |
| Chanhu-daro | | | 0.264 | 0.318 |
| Lothal | | | | 0.359 |

The distances grow as sites get smaller (Mohenjo-daro-Harappa is the closest pair, Lothal-Kalibangan the farthest), whatever their geography. This is what summing vectors over unequal site sizes produces: big sites converge on the corpus mean. Chanhu-daro, 130 km from Mohenjo-daro, is farther from it than Lothal is (600 km).

### Sensitivity (reported, not verdict-bearing)

| variant | seals R_proc / p_exact / p_label | sealings R_proc / p_exact / p_label |
|---|---|---|
| k = 20 | 0.688 / 0.333 / 0.441 | 0.669 / 0.342 / 0.004 |
| k = 50 | 0.670 / 0.408 / 0.654 | 0.616 / 0.508 / 0.026 |
| k = full (414) | 0.684 / 0.392 / 0.680 | 0.552 / 0.650 / 0.128 |
| unit-length docs | 0.704 / 0.367 / 0.483 | 0.783 / 0.167 / 0.0002 |
| complete texts only | 0.682 / 0.375 / 0.666 | 0.630 / 0.425 / 0.091 |
| space fitted on the set only | 0.670 / 0.408 / 0.733 | 0.540 / 0.700 / 0.182 |
| ICIT | 0.776 / 0.208 / 0.201 | 0.681 / 0.500 / 0.367 (4 sites) |
| ICIT, de-dup | 0.768 / 0.233 / 0.268 | 0.672 / 0.500 / 0.439 (4 sites) |

## Deviations

- None in the analysis: one run of the hashed code, no threshold or setting changed.
- The full text could not be read (above), so faithfulness to their settings is limited to the abstract and brief.
- Compute: `board/run.sh` plus `open-citizen-science/.local/compute.lock.indus`, nice 20 with background priority, 2 BLAS threads. Memory was 27% free at start.

## Files

- `rr.py`: code (`sizes`, `run`).
- `sizes.log`, `run.log`, `results.json`, `ledger_rows.csv`, this file.
