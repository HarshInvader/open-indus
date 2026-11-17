# Red team of local_repeats: the travelling numeral formula (R1) and "texts grow, never shrink" (R2)

Pre-registered in `docs/prereg/redteam_local_repeats.md`, hashed in `docs/prereg/HASHES.txt` (2026-11-15T04:07:50Z) before any check ran. Ledger rows `rt_lr_r1a`, `rt_lr_r1d`, `rt_lr_r2a`, `rt_lr_r2b` (confirmatory family of 4, Holm) and `rt_lr_x1`, `rt_lr_x2` (diagnostic). `experiments/local_repeats/`, `experiments/redteam_identifiers/` and `experiments/identifiers/` were imported read-only.

## Verdicts

| claim | verdict | key numbers |
|---|---|---|
| R1 "the formula M267/M391 + M99 + 3/4/6 strokes + M161 is ~40% of the excess; null 0.15" | **weakened** | The frame is far beyond chance under every null: 14 objects vs 0.06-1.14 expected under trigram, slot and bigram nulls (all p=0.002). But (1) it is **not new**: it is in `sources/shaunmortal_indus/STATE.md` line 336, and it is the M162 count frame that pair_numeral_long and redteam_pnl already reported; (2) the closer is **M162 (13 of 16) or M169 (3)** in Mahadevan, never M161; "M161" comes from Wells W390, which lumps five signs; (3) "~40% of the excess" and "the other 20 objects still exceed chance" depend on the null. Under a trigram the rest is fully explained (20 vs 18.6 expected, p=0.42). |
| R1d M77 held-out | **untestable by design** (fails under the literal rule) | All formula texts were put in dev by the v2 family split. Held-out has 0 frame seals, so it cannot test the formula. |
| R2a "texts grow" | **survives, but much smaller than claimed** | Against commonness-matched singletons: 6 vs 0.99 [0-3] expected (p=1e-4). Mantel-Haenszel OR 21 (p=2e-4). A generative trigram null already gives repeated texts a longer variant 13x as often as singletons, so most of the 6/15 vs 8/1,017 gap (p=9e-9) is built into the comparison. The excess beyond that: 6 vs 1.8 expected (p=0.005; bigram null 3.1, p=0.07). |
| R2a "never shrink" | **weakly informative** | Matched controls give 0 of 15 a probability of 0.018. Generative nulls give it 0.03 (bigram) or 0.12 (trigram). |
| R2b "not local" | **survives as "not shown local"; no power** | No weighting gives p<0.05. With the formula removed, the other 10 families lean local: the family-weighted same-site share is 0.67 vs 0.45 (p=0.087) and the between/within ratio is 0.62 [0.09-1.38]. |

Holm across the family (R1a 0.002, R2a 0.005, R2b 0.087; R1d excluded as untestable): 0.006, 0.011, 0.087.

## R1: the numeral formula

**R1a, choice of null (500 simulations of the 4-5 sign seal texts, lengths kept).**

| null | all repeated 4-5 objects (obs 34) | formula objects (obs 14) | other (obs 20) |
|---|---|---|---|
| N2 bigram (reproduces local_repeats) | 7.6 [0-16] p=0.002 | 0.13, p=0.002 | 7.5, p=0.006 |
| TRI-A trigram, λ 0.6/0.3/0.1, self-inclusive | 18.5 [8-31] p=0.006 | 0.68 [0-4] p=0.002 | 17.8, p=0.37 |
| **TRI-L** trigram, 4-5 seal texts left out | 18.7 [8-31] p=0.012 | **0.06**, p=0.002 | **18.6, p=0.42** |
| SLOT-A positional slot bigram | 9.0 p=0.002 | 0.31, p=0.002 | 8.7, p=0.016 |
| **SLOT-L** slot, left out | 14.4 p=0.002 | **0.08**, p=0.002 | **14.4, p=0.18** |
| TRI-A λ 0.8 (sensitivity) | 49.5 p=0.96 | 1.14, p=0.002 | 48.4, p=1.0 |
| TRI-A λ 0.4 (sensitivity) | 5.0 p=0.002 | 0.14, p=0.002 | 4.9, p=0.002 |

- Under the pre-registered rule the formula **survives** the choice of null: p<0.025 under both fair nulls, with expected counts below 1.5.
- The residual claim **fails**: p is 0.42 and 0.18 under the fair nulls.
- **Diagnostic, added after seeing the λ dependence (`r1_calib.py`, 200 sims).** I tuned the trigram weight on the band the red team already accepts as pure collisions (repeated 1-3 sign objects, observed 145).
  - λ=0.7 matches that band as well as N2 does: TRI-L 152.5 and TRI-A 140.5, against N2 150.4.
  - At λ=0.7 the model predicts **32.5 [20-49] repeated 4-5 sign objects (TRI-L)**, against 34 observed (p=0.45).
  - Two models that both fit the short band therefore disagree four-fold on the 4-5 band (8 vs 32). Whether there is any 4-5 sign "excess" at all depends on the null.
  - The formula is the part that holds under every model.
- **Fit (5-fold CV log-likelihood of held-out 4-5 sign seal texts).** Best is the trigram at λ 0.3: −20.61 nats per text, against −21.44 for the bigram. That model, though, under-predicts the short band (97 vs 145). No tested model fits both bands.
- So "~40% of the excess" should read: **the formula is the only part of the 4-5 sign repeats that is robust to the null. Under a calibrated trigram it is essentially all of the excess.**
- **Where the frame lives.** 12 distinct texts in the corpus contain it, 9 of them as the whole text.
  - After opener + W002 + numeral, W390 follows 12 times. The other followers are W220 (6), W585 (3) and smaller counts.

**R1b, novelty: not new.**
- `sources/shaunmortal_indus/STATE.md:336` already lists repeated square-seal texts "opener + stroke + tree (M267-M99-M102-M161 x5, M267-M99-M104-M161 x5, M391-M99-M102-M161 x4)".
- In Mahadevan's own transcription (M77), the 16 frame seals end in **M162** (13) or **M169** (3). M161 never appears there.
- pair_numeral_long already named short-numeral + M162 (values 3-8) and + M169 (1-9) as "count-like heads".
- redteam_pnl found 5 M77 minimal pairs for M162 that differ only in the numeral, and failed the confirmatory counted-item test (p=0.079).
- The texts have been in print since Mahadevan 1977 and Parpola's CISI. The published discussion of an "M391/M267 M99 numeral M162" formula (Mahadevan, Parpola, Wells) is a human lookup: those sources are not machine-readable here.
- local_repeats has independently re-found, in ICIT, the M162/M169 count frame. Its new content is narrower: the frame spreads across sites, and the carriers are mostly square unicorn seals.

**R1c, are the 14 objects independent?**
- 4 objects are flagged:
  - 3 Dholavira seals without a CISI number, two of them rectangular (SEAL:R) with no emblem;
  - M-1729, which is faience.
- None of the 14 has the same text on another carrier at its own site.
- There are no exact same-site, same-emblem, same-size duplicates. Close cases: M-1697 and M-712 (31.8 vs 31.8x33 mm). M-32 is also 31.8 mm, Late, DK-G(S), the same as M-1697, and W817 and W861 are one sign according to the shaunmortal allograph merge.
- Dropping all 4 flagged objects leaves 10 formula objects against 0 expected under every null (p=0.002). Under the rule (at least 3 flagged) R1 is weakened on this axis, but the formula survives.
- **Not** a misclassified Harappa incised-tablet batch: that is the H-352/H-354 family, which is not a formula family.
- In M77 the frame sits on 16 seals: 14 at Mohenjo-daro, 1 at Harappa, 1 at Chanhu-daro. It also appears on 2 sealings and 1 moulded tablet.
- Spread over sites rests on ICIT additions: Dholavira 3 and Nausharo 1, both absent from M77.

**R1d, M77 held-out.**
- Every M77 frame text is in dev (16 dev seal objects, 4 repeated families). Held-out has 0, because `splits_v2` groups text families.
- The test is therefore impossible by construction, and the rule's "fails" is not evidence against the formula.
- Held-out repeated 4-5 sign objects: 5, against 1.3-2.0 expected from dev-trained nulls (p=0.02-0.07).
- Independent new-site evidence: Dholavira (3 frame seals) and Nausharo (1), descriptive only.

## R2a: texts grow, never shrink

- **Reproduction:** 6/15 vs 8/1,017 longer, and 0/15 vs 37/1,017 shorter (p=8.6e-9).
- **Unit (text, site):** 6/24 vs 8/1,017 (p=2e-7).
- **Commonness.** Repeated texts are much more common (mean bigram log-probability per sign −2.07, against −2.88 for singletons).
  - Matched controls (same length, same site, 10 nearest in commonness) give 4.2% of units a longer variant.
  - Family-level null: 0.99 [0-3] against 6 observed (p=1e-4).
  - MH OR across length × site × commonness strata: 21.4 (p=2e-4). Expected hits within strata: 1.1.
- **Generative null** (300 whole-corpus simulations, all classes, site and length kept):

  | null | repeated families with a longer variant | singletons with one | ratio | P(≥6/15) |
  |---|---|---|---|---|
  | N2 bigram | 0.208 | 0.0053 | 40x | 0.072 |
  | TRI-A trigram | 0.118 | 0.0089 | 13x | 0.005 |

  The comparison is asymmetric by construction: a text common enough to repeat is also common enough to sit inside a longer one. Most of the headline p=9e-9 is this artefact. The defensible excess is about 2-3x over generative expectation.
- **Never shrink.**
  - Matched controls have a shorter variant in 23.6% of families, so P(0/15)=0.018.
  - Generative nulls give repeated families a shorter variant 13-21% of the time, so P(0/15)=0.03-0.12.
  - The 4+ filter does not hide shorter versions: the search covers 3-sign texts on any carrier.
  - Against the singleton rate (3.6%), 0/15 is expected (P=0.57). The original "shorter control" was therefore no evidence. Against the right control it is weak evidence.

## R2b: not local (10,000 permutations)

| variant | families | pair-weighted same-site share (null) p | family-weighted (null) p |
|---|---|---|---|
| all | 15 | 0.43 (0.45) 0.62 | 0.61 (0.45) 0.10 |
| non-formula | 10 | 0.57 (0.45) 0.29 | 0.67 (0.45) **0.087** |
| formula only | 5 | 0.29 (0.45) 0.88 | 0.50 (0.45) 0.44 |
| drop flagged families | 11 | 0.47 0.52 | 0.61 0.16 |
| 4-5 band | 14 | 0.41 0.69 | 0.58 0.15 |
| 4-5 non-formula | 9 | 0.54 0.37 | 0.63 0.14 |

- Between/within ratio per possible pair: all families 1.10 [0.38-2.16]; non-formula 0.62 [0.09-1.38].
- **Reading.** The "not local" result came from pair weighting. Formula families contribute 14 of 28 pairs, and those pairs are mostly cross-site.
- Once the formula is removed, the remaining repeats lean local, but 10 families cannot decide it. The red-team "local like Ur III" reading is not restored, and "not local" is not established either.

## What changes
- Rewrite local_repeats finding 2 as: "the opener + M99 + short numeral + M162/M169 frame (Mahadevan; Wells W390) recurs on 14 ICIT seals at 5 sites, far beyond any grammar null. It was already known (shaunmortal; the pair_numeral_long M162 count frame). Whether any other 4-5 sign repeat exceeds chance depends on the null."
- Rewrite finding 4 as: "repeated texts have a one-sign-longer text at the same site 2-3x more often than a generative grammar predicts (6/15 vs 1.8-3.1 expected). The singleton comparison mostly measures commonness."
- Rewrite finding 1 as: "locality is undetermined; non-formula repeats lean local (p=0.09)."

## Caveats
- I knew the shaunmortal record existed before registration (stated in the prereg).
- `r1_calib.py` is post hoc.
- All nulls are fitted to the same corpus. The leave-out versions (TRI-L, SLOT-L) only remove 4-5 sign seal texts.
- n is 15 families throughout.

## Files
`rlib.py` (trigram, slot models), `r1.py` → `r1.json`, `r1.log`; `r1_calib.py` → `r1_calib.json`, `r1_calib.log`; `r2.py` → `r2.json`, `r2.log`; `results.json`.
