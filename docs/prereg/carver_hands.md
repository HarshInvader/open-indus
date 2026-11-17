# Pre-registration: carver hands vs text slots (experiments/carver_hands)

Written 2026-11-15, AFTER the motif features, validation and clustering were computed (`c2_features.py`, which reads no sign identities; it only drops texts with a line break so text rarely enters the motif crop) and BEFORE any partition was compared with any text slot. Frozen with `clusters.csv`, `work/features.npz`, `validation.json`, `c2_features.py`, `c3_test.py` in `docs/prereg/HASHES.txt` (tag `carver_hands`). Fable 5.2 plan 2, item 4.

## Question
Within one workshop or carver, which slot of the seal text varies and which stays fixed? If seals with similar carving share the frame (opener, title, closer) more than chance but not the core, the frame belongs to the workshop/institution and the core to the individual. The reverse would make the frame name the individual.

## What is known before the test (contamination and feasibility)
- Image facts (from `validation.json`): 499 unicorn seals (single-line texts, measured), one photo each (impression preferred). Sampling is about 8 px per mm of the real seal (CISI prints at 2:1, scanned at 100 ppi).
- V1 identity: an impression retrieves its own seal photo among 418 at median rank 3 (chance 209), so features are object-specific. That is layout identity, not proof of a hand.
- V2: ICIT unicorn style letter is predicted at balanced accuracy 0.33 (null 0.23, p=0.005), but site+size+photo alone give 0.38, so the letter is largely a size/site proxy.
- V3: CISI's within-size-group order (Rissman collar -> hatched neck -> hatched face, but also breakage) is predicted at rho 0.28 (null 95% 0.09, p=0.002).
- Clustering: silhouette 0.04-0.05 for every K in 3..10 (best K=10 at the edge of the range), bootstrap ARI 0.19. **There are no discrete clusters**: the "hands" are a partition of a continuum. Clusters are near-independent of site (NMI 0.04) and size group (0.04).
- Prior work (paragorth `STRATEGIES.md` S-DARK-14.1/14.3, 46.1-46.5): physical clusters and the ICIT style letter do not predict shared vocabulary, closer or identical middles (all null after Holm); allograph choice (incl. W705/W706) is a city habit and largely set by the neighbouring sign. I have seen those summaries, not slot-level results.
- redteam_rank: the M336 seal-size effect came entirely from carriers of W706.

## Partitions / similarity (frozen)
- **P1 kNN (primary image test)**: for each of the 499 seals, its 5 nearest neighbours by cosine in the residualised style space `R` of `work/features.npz` (row order = `clusters.csv`); "near pairs" = the union of those (unordered) pairs.
- **P2 clusters**: `clusters.csv` column `cluster` (K=10); same-cluster pairs.
- **P3 ICIT style letter**: all ICIT `SEAL:S` unicorn seals with a style letter, complete single-line text, measured size (n=814); same-letter pairs.
- **P4 text proxy (allograph hand marker)**: ICIT unicorn `SEAL:S` texts carrying exactly one of W705/W706 (complete, no line break filter: all lines joined; '#'-free); same-variant pairs. W705/W706 tokens are deleted before slots are computed.

## Slots (frozen rule, `c3_test.slots`)
Each Wells sign is mapped to Mahadevan via `bridge_WM.json` and given the top-probability role in `experiments/functional_reading/lexicon.csv` (if several M signs, the one with most dev texts). Unmapped signs = core.
- opener = leading run of OPENER/CONNECTIVE signs; closer = trailing run of CLOSER / POST-CLOSER CLITIC / BRACKETED-FISH CLOSER signs; title = TITLE ELEMENT signs (anywhere else); numeral = NUMERAL(short/tall), UNIT/MEASURE signs; core = all remaining signs, in order.
- Slot value = the tuple of signs in it. Frame = opener + title + closer.

## Statistic
For a slot s and a pair set (P1 near pairs, or same-group pairs for P2-P4): rate_within = share of pairs with identical non-empty value among pairs where both are non-empty; rate_between = same over all other pairs. Excess E_s = log((rate_within+eps)/(rate_between+eps)), eps = 1e-3. Frame excess E_F pools the three frame slots (identical counts and both-non-empty counts summed over slots before the ratio). Core excess E_C as above. **Primary statistic Δ = E_F − E_C.**
Null: texts shuffled among seals within site x CISI size group (I..VI by ICIT width) strata, partition held fixed, 2,000 permutations. Two-sided p for Δ; one-sided (greater) p for E_F and E_C.
Power: planted control — within each P2 cluster (and P1: each seal's neighbour set via cluster labels), each seal's closer is replaced by its cluster's modal closer with probability q = 0.1, 0.2, 0.3; 100 plants each; detection = Δ p < 0.0125.

## Decision rule
Four primary tests (Δ for P1-P4), Bonferroni alpha 0.0125.
- "Frame = workshop": Δ > 0 with p < 0.0125 AND E_F one-sided p < 0.0125 in P1 or P2 (image), same sign in P3.
- "Frame = individual / core = workshop": Δ < 0, p < 0.0125, E_C p < 0.0125.
- Otherwise: no slot meaning from carving (report power).
P4 is interpreted with the caveat that allograph choice is neighbour-conditioned (S-DARK-46.5); it cannot by itself name a hand.
Per-slot excesses (opener, title, closer, numeral, core) are exploratory.

## Amendment A1 (2026-11-15, written AFTER c3 ran; the frozen hash above covers the text before this section)
The frozen power control was broken by design: it planted each group's MODAL closer, which is the jar W740 in every group, so it added no group-specific signal and returned power 0 at every q. `c4_power_amend.py` re-runs power with a group-specific (non-jar) closer planted at q = 0.05/0.1/0.2, testing E_F one-sided, and gives an upper 95% bound on the frame within/between ratio. This is exploratory and does not change the pre-registered verdict. A second design weakness, noted not fixed: core values (whole core tuples) are almost never identical (0.2% of pairs), so E_C and hence Δ are very noisy (null sd 0.1-0.7); Δ has little power whatever the partition.
