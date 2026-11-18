# Pre-registration: jar sign M342 on pottery vs seals off Mohenjo-daro (board #45)

Written 2026-11-18 by research45 before any M342 contrast was computed on these pools. Script: `experiments/m342_offsite/m342.py` (hashed with this file).

## What has already been seen (disclosure)
- Prior work: self_label found M342 RARER on pottery in ICIT (all sites, 70 vs 124 expected); firing_stage found it on 1/25 painted vs 70/384 graffiti. redteam_seal_fate left M342 ~1.5x on Mohenjo-daro "?"-dimension seals (corrected p 0.06). The prior expectation is therefore NO enrichment.
- While exploring the data I printed raw distinct-text counts from base M77 per site x object type, which included M342-containing counts (H/L/K pottery graffiti 14/49 texts, seals 176/405). No length/break stratification, no null, no consensus corpus, no ICIT. I also printed pool sizes and the control sign choice (M99; 125 vs M342 211 texts in the primary pool). This is disclosed; the frozen thresholds below are not changed by it.

## Hypothesis
H1: if M342 marks vessels/storage, texts written on pottery carry it more often than seal texts of the same length and completeness.

## Data
- Primary pool: consensus corpus `experiments/consensus_corpus/out/corpora/cons_sign_ext.json` (signs the two editions disagree on are masked '#'), sites Harappa, Lothal, Kalibangan (Mohenjo-daro excluded), object_type 'pottery graffito' vs 'seal', distinct texts within class. Pool: 65 pottery, 432 seal texts.
- Secondaries (reported, not used for the verdict): S1 base M77 same pools; S2 ICIT H/L/K POT:* vs SEAL* with W740 (= M342, bridge); S3 sealings vs seals (exploratory: sealings may be jar stoppers); S4 Harappa seals restricted to those linked in experiments/old_registers/registers.csv (Vats 1940 seal tabulation; the registers contain no pottery, so they can only confirm the seal side); per-site primary.

## Statistic and null
R = O/E. O = pottery texts containing M342; E = sum over strata of n_pottery x seal M342 rate in that stratum. Strata = readable signs (1..5, 6+) x broken (any '#' or incomplete). Null: object labels permuted within strata (4,000 perms), one-sided p for enrichment.

## Known-answer plant (run FIRST, before the real contrast)
Labels permuted within strata (true effect destroyed), then M342 written over the last readable sign of randomly chosen pottery texts until expected R = 1.5. 400 reps x 1,000 perms. Detection = p < 0.05 and R >= 1.25. Frequency-matched control = non-jar sign with text count closest to M342 (M342-M347 excluded): M99. Its false-positive rate in planted data must be <= 0.10, and the unplanted size <= 0.07.
- Gate: if power < 0.8 at 1.5x, the route is UNTESTABLE at these sites; report the number of pottery texts needed (pottery resampled to 100/150/200/300/400) and do NOT read the real R as evidence either way. The real R is then reported descriptively only.

## Decision rule (primary only; one confirmatory test, alpha 0.05)
- SUPPORTED: R >= 1.25 and p < 0.05.
- KILL (close M342-as-vessel-marker): R < 1.25 (including wrong direction, R < 1). If R < 1 with p_low < 0.05, say "depleted on pottery".
- Anything else: inconclusive.
Falsifier of a positive: S2 (ICIT, different edition and many post-1977 graffiti) R < 1.

## Amendment A1 (2026-11-18, before any outcome was read)
The first plant run crashed in the ICIT secondary plant: it planted and chose the control using the M-number jar (M342) on W-numbered ICIT texts. Fix: the jar sign is a parameter (W740 for ICIT; control excludes only the jar there). The primary plant had completed in that run but its output was never written or read; it is rerun unchanged with the same seed. Primary pool, statistic, thresholds unchanged. Control-sign selection for M-space unchanged (it now also excludes '|'/'#', which were never candidates in practice since only M-prefixed signs were counted before).
