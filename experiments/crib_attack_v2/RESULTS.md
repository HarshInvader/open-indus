# Crib attack v2: planted gate at the real sample size (board task #26, H10)

## Verdict: conditional go. The redesigned attack works only with about 40 or more texts and a list of about 30 names. It cannot work on the 9-11 safe foreign texts.

The redesign uses an exact-match score E, short name lists and optional anchors. I tested it on planted data with the real text lengths, and it beats keys fitted to shuffled texts in 6 of 36 cells. All 6 passing cells have n ≥ 41:
- **The 27-spelling Elamite list (elamite30, capped at 30) passes at n = 41 with no anchors.** Power is 1.00, wrong-language false positives 0.00, and median precision 0.80, with 47% of sign values recovered. It also passes at n = 41 and 49 with 3 anchors.
- **Lists of 66-200 spellings need n = 49 plus 3-6 anchors.** The Gulf list (66 spellings) passes at n = 49 with 3 or 6 anchors, and the Elamite core list (81) at n = 49 with 6 anchors. The Akkadian list (198) passes nowhere: its best precision is 0.46.
- **At n = 9 nothing passes.** In every list and anchor setting, power is 0.00-0.30 and the true key's E is below the noise 95th percentile in ≥ 95% of runs. At n = 20 power reaches 0.70 at most and no cell passes.
- **Smallest passing sizes.** With anchors a = 0: n = 41 with 27 spellings. With a = 3: n = 41 with 27 spellings, or n = 49 with 66. With a = 6: n = 49 with 81 (not run below n = 49). The true key alone first beats the noise 95th percentile at the same points (unicity), so the bottleneck is the data, not the search.

**For #17 (Linear Elamite): go, under the registered rule.** A cell passes at n = 41 with a ≤ 3. Use n = 45 as the decisive size with a crib list of at most about 30 spellings. Planted data predicts failure at n = 20 and 30, so run those only as a check that the method behaves.

**For #4 (real Indus):** with the 9-11 safe texts the method has no power (≤ 0.30), so a run there would be uninformative. It is only informative on about 41-49 texts, which means using the unconfirmed readings. It would also need a list of about 30 spellings that actually contains the owners' names.

Pre-registration: `docs/prereg/crib_attack_v2_planted.md` (tag `crib_attack_v2_planted`). Amendment 1, `..._amend1.md`, made compute cuts before any E value was read.

## Method (frozen)
- **Simulated script.** A CV syllabary, using #3's spelling rule (copied into `names2.py`), plus 12 frame signs and 40 logograms. 75% of texts carry one planted name, and each name sign is misread with probability 0.2. Text lengths are the real legible lengths:
  - n = 9: the readings_check 'yes' set;
  - n = 20: a random 20 of the 41;
  - n = 41: every foreign text with ≥ 2 legible signs;
  - n = 49: the 41 plus the 8 home round seals.

  No Indus sign sequence was used.
- **Name lists.** Each list is capped at ≤ 200 CV spellings, with names taken in file order:
  - elamite30: 27 spellings, 17 names (cap 30);
  - gulf: 66 spellings, 28 names;
  - elamite: 81 spellings, 50 names;
  - akkadian: 198 spellings, 80 names.

  Planted names are drawn from the attacker's own list, so the list contains every true name. This is the most favourable case. The wrong-language corpora are planted from the Amorite list (200 spellings).
- **Score E** is the number of texts containing an exact full spelling of 3 or more signs. The search is annealing on E with "make this window read as this name" moves, 3 restarts, and 1500 + 60n iterations.
- **Anchors** are the a most frequent syllabic signs, fixed to their true values. This is optimistic.
- **Runs per cell:** 20 planted, 10 wrong-language and 40 token-shuffled. The gate is power ≥ 0.8, FPR ≤ 0.2 and median precision ≥ 0.5.
- **Search adequacy.** On shuffles at n = 41, a = 0, 4x iterations raised the median E from 10 to 10 (gulf) and from 6 to 7 (elamite30). Both rises are under the registered limit of 2, so the null is not under-searched. The registered Sumerian half had no baseline after amendment 1, so elamite30 was substituted. That substitution was decided after the grid had been read.

## Full table
| list | n | a | null med | null q95 | planted E med | true E med | power | FPR | unicity (true>q95 share) | prec med | rec med | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| elamite30 | 9 | 0 | 5 | 6.0 | 6.0 | 3.0 | 0.30 | 0.0 | no (0.05) | 0.36 | 0.30 | - |
| elamite30 | 9 | 3 | 4 | 5.0 | 5.0 | 3.0 | 0.30 | 0.0 | no (0.05) | 0.25 | 0.26 | - |
| elamite30 | 20 | 0 | 5 | 6.0 | 7.0 | 5.0 | 0.70 | 0.0 | no (0.15) | 0.48 | 0.33 | - |
| elamite30 | 20 | 3 | 4 | 5.0 | 6.0 | 4.0 | 0.65 | 0.0 | no (0.25) | 0.50 | 0.37 | - |
| elamite30 | 41 | 0 | 6 | 7.0 | 12.0 | 10.5 | 1.00 | 0.0 | yes (0.85) | 0.80 | 0.47 | PASS |
| elamite30 | 41 | 3 | 5 | 6.0 | 12.0 | 10.5 | 1.00 | 0.0 | yes (1.00) | 0.86 | 0.49 | PASS |
| elamite30 | 49 | 0 | 7 | 7.0 | 14.0 | 12.5 | 1.00 | 0.3 | yes (1.00) | 0.74 | 0.49 | - |
| elamite30 | 49 | 3 | 5 | 6.0 | 14.0 | 12.0 | 1.00 | 0.1 | yes (1.00) | 0.85 | 0.46 | PASS |
| elamite30 | 49 | 6 | 3 | 4.0 | 14.5 | 12.5 | 1.00 | 0.3 | yes (1.00) | 0.85 | 0.45 | - |
| gulf | 9 | 0 | 8 | 9.0 | 8.5 | 3.0 | 0.00 | 0.0 | no (0.00) | 0.05 | 0.05 | - |
| gulf | 9 | 3 | 7 | 8.0 | 8.0 | 3.0 | 0.30 | 0.0 | no (0.00) | 0.18 | 0.26 | - |
| gulf | 20 | 0 | 9 | 10.0 | 10.0 | 5.0 | 0.15 | 0.0 | no (0.00) | 0.16 | 0.17 | - |
| gulf | 20 | 3 | 8 | 9.0 | 10.0 | 4.0 | 0.55 | 0.0 | no (0.00) | 0.18 | 0.17 | - |
| gulf | 41 | 0 | 10 | 11.0 | 12.0 | 10.0 | 0.85 | 0.4 | no (0.05) | 0.38 | 0.29 | - |
| gulf | 41 | 3 | 9 | 10.0 | 12.0 | 9.0 | 0.95 | 0.0 | no (0.20) | 0.38 | 0.32 | - |
| gulf | 49 | 0 | 10 | 11.0 | 13.0 | 9.0 | 0.90 | 0.6 | no (0.25) | 0.08 | 0.05 | - |
| gulf | 49 | 3 | 9 | 10.0 | 14.0 | 11.0 | 1.00 | 0.1 | yes (0.55) | 0.51 | 0.37 | PASS |
| gulf | 49 | 6 | 7 | 9.0 | 14.5 | 11.5 | 0.95 | 0.0 | yes (0.75) | 0.58 | 0.37 | PASS |
| elamite | 9 | 0 | 8 | 9.0 | 9.0 | 3.5 | 0.00 | 0.0 | no (0.00) | 0.00 | 0.00 | - |
| elamite | 9 | 3 | 7 | 8.0 | 8.0 | 3.5 | 0.20 | 0.0 | no (0.00) | 0.20 | 0.26 | - |
| elamite | 20 | 0 | 10 | 11.0 | 10.0 | 4.5 | 0.15 | 0.2 | no (0.00) | 0.04 | 0.05 | - |
| elamite | 20 | 3 | 9 | 10.0 | 11.0 | 5.0 | 0.65 | 0.0 | no (0.00) | 0.17 | 0.20 | - |
| elamite | 41 | 0 | 12 | 13.0 | 15.0 | 12.0 | 0.90 | 0.1 | no (0.10) | 0.28 | 0.22 | - |
| elamite | 41 | 3 | 10 | 12.0 | 16.0 | 12.0 | 1.00 | 0.1 | no (0.45) | 0.43 | 0.41 | - |
| elamite | 49 | 0 | 12 | 13.0 | 17.0 | 12.5 | 0.90 | 0.6 | no (0.45) | 0.29 | 0.24 | - |
| elamite | 49 | 3 | 11 | 13.0 | 17.5 | 13.0 | 1.00 | 0.0 | no (0.30) | 0.43 | 0.34 | - |
| elamite | 49 | 6 | 9 | 11.0 | 18.0 | 15.0 | 1.00 | 0.1 | yes (0.80) | 0.52 | 0.39 | PASS |
| akkadian | 9 | 0 | 8 | 9.0 | 9.0 | 3.0 | 0.00 | 0.0 | no (0.00) | 0.02 | 0.02 | - |
| akkadian | 9 | 3 | 8 | 9.0 | 9.0 | 3.0 | 0.00 | 0.0 | no (0.00) | 0.13 | 0.20 | - |
| akkadian | 20 | 0 | 10 | 11.0 | 11.0 | 5.5 | 0.40 | 0.3 | no (0.00) | 0.04 | 0.05 | - |
| akkadian | 20 | 3 | 9 | 11.0 | 11.0 | 6.5 | 0.40 | 0.0 | no (0.00) | 0.26 | 0.31 | - |
| akkadian | 41 | 0 | 12 | 13.0 | 14.0 | 11.0 | 0.60 | 0.5 | no (0.15) | 0.12 | 0.11 | - |
| akkadian | 41 | 3 | 12 | 13.0 | 15.0 | 11.0 | 0.90 | 0.0 | no (0.10) | 0.30 | 0.24 | - |
| akkadian | 49 | 0 | 12 | 14.0 | 14.0 | 12.5 | 0.40 | 0.5 | no (0.15) | 0.15 | 0.13 | - |
| akkadian | 49 | 3 | 12 | 14.0 | 17.0 | 12.0 | 1.00 | 0.0 | no (0.15) | 0.40 | 0.32 | - |
| akkadian | 49 | 6 | 11 | 12.0 | 17.0 | 12.5 | 1.00 | 0.0 | yes (0.50) | 0.46 | 0.37 | - |

rows 2520 cells 36 passing cells 6

## What failed or was not checked
- **Coverage below 1.** Every planted name is on the attacker's list. If the real owners' names are missing from the list, power falls further. This is untested, and is the main reason the go is conditional.
- **Anchor realism.** Anchors are true values of the most frequent signs. Real outside anchors would be fewer and might be wrong.
- **Script models.** Only a CV syllabary was tested. Not tested: logograms or rebus spellings of names, homophonous signs, consonant-only matching, and a cuneiform-style CVC script. Indus has about 400 signs, while the simulation has about 120. Its sparser sign reuse would loosen the constraints, so noise would fit more easily.
- **Cuts made for compute** (amendment 1): the Sumerian list, n = 11 (close to n = 9) and 6 anchors below n = 49 were dropped, and wrong-language runs were cut from 20 to 10. Grid cost was about 3 CPU-hours.
- **Estimate precision.** With 20 planted runs, each power figure has a 95% CI of about ±0.2. With 10 wrong-language runs, an FPR of 0.0 is compatible with a true rate of up to about 0.3. Some cells just miss on FPR: elamite30 at n = 49, a = 0 has FPR 0.3.
- Real Indus outcomes were not touched.

## Hypotheses
| hypothesis | verdict |
|---|---|
| Short list + E recovers a planted key at n = 9-11 | refuted (power ≤ 0.30, unicity never) |
| Same at n = 20 | refuted (power ≤ 0.70, no cell passes) |
| Same at n = 41-49 with ≤ 30 spellings | supported (power 1.00, FPR 0-0.1, precision 0.74-0.86) |
| Same at n = 41-49 with ~200 spellings | refuted without 6 anchors; not passing even with 6 (Akkadian, precision 0.46) |

## Update after #17 (Linear Elamite known-answer test, negative)
The go for #17 did not survive a real script. On Linear Elamite the frozen method recovers nothing: 0/24 cells pass (see experiments/crib_le_known_answer/RESULTS.md). The planted assumption that 75% of texts carry a listed name was far from reality: 2-15 of 224 real words do. The test also exposed a flaw in the CV spelling rule: cuneiform CV-VC echo vowels become an extra vowel sign (*na-ak* becomes na-a-k). So this planted pass is necessary but not sufficient, and #4 should not be run.
