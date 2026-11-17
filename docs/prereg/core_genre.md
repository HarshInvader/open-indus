# Pre-registration: core_genre Part B (which real genre do Indus core statistics resemble?)

Registered 2026-11-15 in `experiments/core_genre/`, after the reference-only calibration (`partB.py calib`) and BEFORE `partB.py score` (the first time Indus is compared with any non-name genre). Script hashes in `docs/prereg/HASHES.txt` (tag core_genre).

## Disclosure: what was already seen
- Indus core statistics (dev and held-out) from naming_sim, and Part A of this experiment (`partA.json`, `partA_dist.json`, `partA_calib.json`): Indus grammar cores, Indus whole texts / numeral-free texts / edge-stripped segments / top-10-stripped segments, and Indus vs NAME lists under raw, truncated, merged, slot-merged, edge and sym variants. So the Indus side of all three variants below is known, and Indus vs the 11 name lists is known (V3 sym: dev nearest Plains 0.92, held-out Sangam 0.58).
- The calibration among reference systems (`partB_calib.json`). The Indus core-sign frequency profile is used as the merge target (V2, V3) in calibration.
- NOT seen: any distance between Indus and a non-name genre or a code.

## Systems (`genres.py`, frozen)
13 non-name writing genres (Ur III legends word/sign, Ur III title skeletons, OB legends signs, Egyptian verbless phrases and title strings (lemmas), Rietstap blazons, Linear B entry lines, Proto-Elamite entries, proto-cuneiform entries, cuneiform tags, Latin stamps/labels, Linear A labels), 5 codes (khipu, chess, chords, emoji, METAR), 11 naming_sim name lists. Numeral tokens removed; units of 1-8 elements; distinct units. Systems with < 100 units at a matched size are skipped.

## Variants
- V1 raw: Indus grammar cores vs whole units at their own inventory.
- V2 merge: Indus grammar cores vs whole units merged at random onto the 286-class Indus core-sign frequency profile (homography model).
- V3 sym: Indus grammar-free edge segments vs each system's edge segments (same rule), merged as in V2.

Statistic set, distance and scales: naming_sim (6 PRIMARY statistics; RMS z; naming_sim realcmp_scales). Matched n = min(n_sys, n_indus, cap); cap 800 dev, 423 held-out. 30 subsamples per side; 200 bootstrap resamples of the replicate means.

## Calibration facts (reference systems only)
- Group of nearest neighbour (genre / code / name) matches the system's own group for 19/29 (raw), 21/29 (merge), 21/29 (sym); label-permutation chance about 10/29; p = 0.003, 0.0002, 0.0002. The statistics carry genre-group information, but 8-10 systems per variant still have a nearest neighbour from another group.
- Reference NN distance: median 0.79 / 0.92 / 0.83, max 3.69 / 3.04 / 2.85 (raw / merge / sym). The maxima are set by chess openings and Linear A labels (small).

## Decision rules
- R1 (outlier): per variant and split, Indus d_NN vs reference NN distribution: <= median typical, <= max peripheral, > max outlier.
- R2 (category): share of bootstrap resamples in which the best NON-NAME writing genre is nearer to Indus than the best NAME list. "Genres nearer than names" if >= 0.95 on BOTH dev and held-out in at least 2 of 3 variants. "Names nearer" if <= 0.05 on both splits in at least 2 of 3 variants. Otherwise undecided.
- R3 (named genre): a single system is "the Indus-like genre" only if it is nearest, or its bootstrap CI overlaps the nearest one's, on both splits in at least 2 of 3 variants, AND is the leave-one-statistic-out nearest in >= 4 of 6 runs on dev in V1. Otherwise: "no single genre".
- R4 (codes): same as R2 with codes vs names, descriptive only (codes are not candidates for a script).

Multiple testing: R1-R3 are threshold decisions (no p-values); the ledger records them as decisions. Sensitivity (not deciding): pooled scales (SD over all reference systems in the variant).

## Run
```
.venv/bin/python -I experiments/core_genre/partB.py score
```
