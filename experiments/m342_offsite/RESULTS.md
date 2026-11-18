# M342 (jar sign) off Mohenjo-daro: vessel marker or not? (board #45)

## Verdict

- **UNTESTABLE on the pre-registered test.** At Harappa, Lothal and Kalibangan the consensus corpus has only 65 distinct pottery texts. With that many, a real 1.5x enrichment of the jar sign on pottery is detected only 47% of the time (needed: 80%).
- **About 250 distinct pottery texts are needed** at these sites for 80% power (resampling: 0.58 at 100, 0.69 at 150, 0.75 at 200, 0.96 at 300). That is roughly 4 times what the consensus corpus holds.
- **Descriptively, the two editions disagree, and the bigger pool points the wrong way.**
  - Consensus corpus (the pre-registered pool): 1.43x, 19 vs 13.3 expected, p = 0.057. Not evidence, because the test is underpowered.
  - ICIT for the same three sites, with 265 pottery texts: 0.80x, 41 vs 51.4 expected (p = 0.91 for enrichment; p = 0.089 for depletion). This pool does have power (0.92 at 1.5x), but it was a secondary pool, so it does not decide the verdict.
- **The route is not formally closed.** The kill rule applies only to the primary test, and that test could not run. The weight of evidence still leans against "M342 marks vessels":
  - ICIT here: 0.80x on pottery.
  - self_label (ICIT, all sites): 70 jar texts on pottery against 124 expected.
  - firing_stage: on 1 of 25 painted pots.
- **No positive result, so no M6 red-team task.**

## Design (docs/prereg/m342_offsite.md; hashes in docs/prereg/HASHES.txt, tag m342_offsite board#45, plus amendment A1)

- **Statistic.** R = observed / expected count of pottery texts that contain M342. The expectation comes from seal texts in the same stratum. Strata are readable signs (1-5, 6+) crossed with broken or complete.
- **Null.** Object labels are permuted within strata, 4,000 times. The p-value is one-sided.
- **Data.**
  - Primary: `experiments/consensus_corpus/out/corpora/cons_sign_ext.json`. Sites are Harappa, Lothal and Kalibangan; Mohenjo-daro is excluded. Pottery graffiti (65 texts) are compared with seals (432), counting distinct texts within each class.
  - Lothal contributes no pottery texts. Harappa has 51 and Kalibangan 15.
- **Amendment A1.** A bug fix logged before any outcome was read. The ICIT plant had used the M-number jar sign on W-numbered texts. The primary plant was rerun unchanged with the same seed.
- **Disclosure, also in the prereg.** Before pre-registering I had printed raw M77 counts by site and object type: pottery 14 of 49 texts, seals 176 of 405.

## Known-answer plant (run first)

Labels were permuted within strata, then M342 was written over the last sign of pottery texts until the expected R reached 1.5. A detection required p < 0.05 and R >= 1.25.

| pool | pottery / seal texts | power at 1.5x | power at 2x | size (no plant) | control-sign false positives |
|---|---|---|---|---|---|
| consensus H/L/K (primary) | 65 / 432 | **0.465** | 0.98 | 0.045 | M99: 0.045 (median R 0.97) |
| ICIT H/L/K (secondary) | 265 / 554 | 0.92 | - | 0.06 | W002: 0.075 (median R 1.01) |

The method is sound: it recovers 1.5x when there are enough texts and 2x even at n = 65, it keeps its nominal size, and the frequency-matched control sign stays flat. The one thing missing is pottery texts.

## Real data (descriptive only, because the gate failed)

| pool | R | O / E | p (enrich) | p (deplete) |
|---|---|---|---|---|
| primary consensus H/L/K | 1.43 | 19 / 13.3 | 0.057 | 0.94 |
| control sign M99, same pool | 0.68 | 4 / 5.9 | 0.82 | 0.20 |
| S1 base M77, H/L/K (49 pottery) | 1.20 | 14 / 11.7 | 0.25 | 0.75 |
| S2 ICIT, H/L/K (265 pottery) | **0.80** | 41 / 51.4 | 0.91 | 0.089 |
| S3 sealings vs seals (consensus) | 1.10 | 108 / 98.3 | 0.16 | 0.84 |
| S4 Harappa seals limited to register-linked ones (Vats 1940) | 1.31 | 19 / 14.6 | 0.13 | 0.87 |
| Harappa only | 1.36 | 12 / 8.8 | 0.14 | 0.86 |
| Kalibangan only | 1.32 | 7 / 5.3 | 0.34 | 0.78 |

## Caveats and what was not checked

- **The consensus pool has 65 pottery texts, but base M77 has 49 distinct ones.** Masking disagreed signs as '#' splits some copies into separate "distinct" texts, which slightly inflates n in the consensus pool.
- **The old registers hold no pottery.** Vats 1940 tabulates seals only. They can confirm the seal side (S4) but add nothing to the pottery side.
- **M77 and ICIT conflict, and the cause is unknown.** M77 and the consensus corpus lean toward enrichment (1.2-1.4x); ICIT, which adds many post-1977 Harappa graffiti, leans the other way (0.8x). The difference could be the newer graffiti, how ICIT types pottery, or chance. It was not resolved here.
- Vessel form and firing stage are not recorded for these texts, so "storage jar versus other vessel" could not be asked.

## What would make it testable

- **About 250 distinct inscribed pottery texts off Mohenjo-daro, read in M77 space** (i.e. under Mahadevan's sign numbering). The ICIT pool already has 265, but its outcome has now been seen (0.80x), so it cannot serve as a fresh confirmatory test.
- **A clean test needs new data.** The best candidate is the Kenoyer and Meadow HARP sherd database (1,218 marked sherds, with form and firing stage), which is already listed in HUMAN_LEADS. Pre-register a vessel-form contrast before reading it.

## Proposed NEGATIVE_ATLAS text (for the lead; the route is NOT formally closed)

> **M342 (jar) as a vessel/storage marker off Mohenjo-daro (#45, m342_offsite).** Untestable on the consensus corpus: 65 pottery texts at Harappa, Lothal and Kalibangan give 47% power for 1.5x; about 250 are needed. Descriptively, the consensus corpus shows 1.43x (p = 0.057, underpowered) and ICIT for the same sites shows 0.80x (265 pottery texts, power 0.92, wrong direction). With self_label (70 vs 124 expected on pottery) and firing_stage (1 of 25 painted), the evidence leans against M342 marking vessels. Reopen only with new marked-sherd data (HARP sherd DB) under a fresh pre-registration.

## Hypotheses

| hypothesis | verdict |
|---|---|
| M342 enriched >= 1.5x on pottery vs seals at H/L/K (consensus) | inconclusive: untestable (power 0.465) |
| Same in ICIT (secondary) | not supported (0.80x, wrong direction) |
| M342 enriched on sealings vs seals (exploratory) | not supported (1.10x, p 0.16) |

Files: `m342.py`, `plant.json`, `real.json`, `plant.log`, `real.log`. Every run went through `board/run.sh`.
