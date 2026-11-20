# Carver hands × text: gate results (2026-11-20, before any sealed test)

**Source.** G. M. Jamison 2017, PhD thesis, University of Wisconsin-Madison, https://search.library.wisc.edu/digital/AC3N6TSMX73CAE8O. I opened it and read the method myself.
- The 11 grouping attributes are iconographic. Jamison writes, "I chose to omit inscribed characters from the stylistic analysis" (ch. 7).
- Inscription carving style (curvature, depth) is used for periods, not for groups.
- The thesis is © the author, all rights reserved. It stays in `raw/` (gitignored), and only derived counts are published.

## Gate 1: join (pass)
`parse.py` parsed Appendix 7.1 (481 seals) and Appendix 9.1 (265 rows; 180 seals in 56 groups, matching the thesis).

| Count | Seals |
|---|---|
| Linked to ICIT by CISI number (site agrees for all; Balakot vs "Bala-kot" is spelling) | 450 of 514 |
| Grouped seals linked | **156** of 180 |
| Seals in hands with ≥ 2 linked members (44 hands) | 147 |

- **Unlinked grouped seals:** 24. They use non-CISI numbering (Bagasra, Dholavira, Farmana, the KLB and CD series) and are left unlinked rather than guessed.
- **Gate:** at least about 120 linked. Passed.

## Gate 2: power (fail)
- **Design.** Hands are first reassigned at random within site × size-tercile strata. This keeps the real hand sizes and destroys any real link. A hand-specific sign is then planted in a share of each hand's seals.
- **Test.** A within-hand vs stratified-permutation test excluding near-copy pairs (≤ 1 edit or contained). Holm over two statistics: sign-set Jaccard, and rarity-weighted (IDF) shared signs. 300 permutations, 30 replicates per row.

| Planted share | Rejection rate |
|---|---|
| 0 (size) | 0.03 |
| 20% | **0.17** |
| 35% | 0.70 |
| 50% | 0.97 |

- **The 20% rule fails** (power ≥ 0.8 required). The smallest detectable effect is about 40% of a hand's seals sharing one hand-specific sign.
- **Why.** 44 hands give only 289 within-hand pairs once near-copies are excluded.

## Disclosure
- **What happened.** A first power estimate planted into the *real* hands and gave about 0.95, with within-hand rarity-weighted ratios of 1.36-1.47 at 20% planting. That number mixes the planted signal with any real one, so it hints that real hands may share rare signs above the stratified null.
- **Status.** This look was not planned. It is reported here and must be treated as exploratory. No test of real hands without planting was run.

## Status
Dead at the power gate under the coordinator's kill rule. Any further run needs a new decision, and a sealed prereg that names this disclosure.

## Direction 2 (allographs by hand): dropped at the feasibility gate (2026-11-20)
- **Prior art.** A fresh Fable read found no work that uses hand identity to decide allograph vs sign:
  - Daggumati & Revesz 2021, https://www.nature.com/articles/s41599-021-00713-0, uses positions only;
  - Corazza et al. 2022 (https://aclanthology.org/2022.lt4hala-1.12.pdf, Cypro-Greek) and Born et al. 2023 (https://aclanthology.org/2023.cawl-1.11/, proto-Elamite) use shape plus context;
  - Wells, Fuls, Parpola 1994 and Mahadevan 1977's rules are unverified (not opened).
- **Feasibility.**
  - The grouped seals carry 877 tokens of 212 Wells types.
  - Wells-split pairs with ≥ 10 tokens each: **1** (W817/W861 → M267) under `sources/shaunmortal_indus/data/bridge_WM.json`, and 0 under `experiments/consensus_corpus/corrected_concordance.csv`.
  - Only 2 hands contain both variants (6 tokens).
  - Only 24 types reach 10 tokens at all.
  - The kill rule needs ≥ 15 pairs, so the study is dead.
- **Reopen with** a much larger hand-attributed seal set.
