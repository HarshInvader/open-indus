# Pre-registration: red team of #23's round-seal ORDER anomaly (board task #25, agent H11)

Written before any statistic below is computed. Known beforehand (published in #23, experiments/redteam_round_format/results.json): per-text KN d, u, q for the 8 home round texts and 16 foreign round texts; home round order d excess +1.96 bits/sign vs length-matched home seals (p=1e-4); foreign minus home round d +0.11 (p=0.68). Also seen before writing this (metadata only, no scores): 4 of the 8 home round texts contain a break or are marked incomplete in ICIT (2419.2 starts '# #', 3668.1 ends '#', 4247.1 starts '#', 5468.1 has '#' mid-text), and q4_gulf.clean() joins signs across breaks; 2977.1 has ICIT direction 'BUS' and its M77 reading (2604) has a different sign order.

## Claim under attack
"Home round seals (n=8) break Indus sign ORDER as much as foreign round seals: real order no more Indus-like than shuffles of the same signs (order component about +2 bits/sign over ordinary home seals)."

Main suspicion: rare signs. A sign seen <2 times in training becomes <UNK>, and rare signs get backed-off probabilities, so ANY text heavy in rare signs has d near 0 whatever its order. #23's null matches length only.

## Data and scorers
Groups exactly as #23 (ICIT, q4_gulf.clean, first-seen dedup by (group, sequence), foreign sequences removed from native; home round = SEAL:C/CY at Indus sites minus ICIT 1387.1/1388.1/1388.2 with a distinct permutation: the 8 texts 114.1, 2419.2, 2911.1, 2912.1, 2977.1, 3668.1, 4247.1, 5468.1; home seals = other SEAL:* types with a distinct permutation; foreign round as #23, n=16).
Per text: real bits/sign, and the same set of up to 200 within-text permutations for every scorer (all distinct permutations if fewer). d = real minus mean over permutations; q = share of permutations scoring <= real.
- KN: q4_gulf.KN, 10-fold CV for native texts, all-native model for foreign.
- GR: Wells class-bigram grammar (glib.ClassBigram, K and alpha from experiments/grammar/classes_wells.json, init SEED_W), 5-fold CV; restarts cut to 2 for compute.
- POS: positional model (glib.PositionModel, cap 4: P(sign | position from start), P(stop | length)), same 5 folds. Order enters only through position, i.e. initial/medial/final placement.
Each text is one complete run (BOS and EOS), as in #23.

Rare load r = number of sign tokens in the text whose count in the scoring fold's training texts (KN folds; full native for foreign texts) is < 10.

## Primary tests (home round n=8 vs home seals, statistic mean d, one-sided, 10,000 draws)
Null N1: for each round text draw a home seal from the same stratum (min(L,9), min(r,3)); a stratum with <5 home seals is collapsed to r-1 (repeat), then L-1.
- T1 KN-N1, T2 GR-N1, T3 POS-N1. Holm over 3.
Secondary (reported, not in the decision): N0 = length-only (#23's null) for each scorer; N2 = N1 restricted to home seals with no near-copy (#23's Jaccard rule); N3 = strata (L, r, broken) where broken = text has '#' or ICIT complete=False; q statistic in place of d; foreign round vs home seals under N1; foreign minus home round on N1-standardised d (d minus its N1 stratum mean), label permutation 20,000, two-sided.

## Planted controls (each scorer; 1,000 replicates, each tested against 2,000 null draws)
- C1 power: 8 home seals drawn from the 8 round texts' N1 strata, each replaced by a random within-text permutation different from the original, scored by its own fold model; flag = N1 p<0.05. Power = flag rate.
- C2 rare-sign false positives: 8 UNSHUFFLED home seals drawn from the same N1 strata (same length and rare load); flag rate under N0 and under N1. Plus C2b: 8 unshuffled home seals of the round lengths from the top quartile of rare load (r/L) within length; flag rate under N0 and N1.

## Sensitivity
- Leave-one-out over the 8 for T1-T3 (N1).
- Complete-only: the 4 home round texts without '#' and with complete=True vs complete home seals (N1 strata within complete seals).
- 2977.1 read in reversed order.
- Documentary: for each of the 8, what our local sources say on shape (ICIT type/dims, CISI register rows, Mackay/Marshall registers, CISI intro), and reading agreement M77 vs ICIT.

## Decision rule
- SURVIVES: T1 Holm p<0.05, and T2 or T3 Holm p<0.05, and C1 KN power >= 0.8, and C2 KN N1 flag rate <= 0.10, and KN-N1 leave-one-out max p < 0.05, and complete-only excess > 0.
- FALLS: T1 p>=0.05 while C1 KN power >= 0.8 (the test could see off-order texts at this rare load, and the round seals look like ordinary seals of the same rare load).
- INCONCLUSIVE: C1 KN power < 0.5.
- WEAKENS: anything else (e.g. T1 holds but GR and POS both fail, LOO max p >= 0.05, complete-only reverses, or N1 excess < half the N0 excess).
Number of tests: 3 primary (Holm); everything else descriptive.

## Not done
No Indus sound or meaning claims. No edits outside experiments/redteam_round_order/. Compute via board/run.sh, Pool <= 2 (single process planned), about one CPU-hour cap; permutation counts are cut first if needed, and the cut is reported.
