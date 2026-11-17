# Stratigraphic half-life: do name signs turn over faster than frame signs? (Fable plan 2, item 9)

Pre-registered in `docs/prereg/half_life.md`. The prereg, `hl_lib.py` and `h1_main.py` were hash-frozen before the first run (`docs/prereg/HASHES.txt`, tag `half_life`). Ledger rows `hl_p1`..`hl_p4` are in `docs/test_ledger.csv`.

Run from `experiments/half_life/` with `../../.venv/bin/python`:
- `h0_describe.py`: data sizes (before the prereg)
- `h1_main.py`: P1-P4, persistence, sensitivity checks, planted power (pre-registered)
- `h2_followup.py`, `h3_finetype.py`, `h4_shared_texts.py`: exploratory follow-ups run after the frozen run

Outputs: `results.json` (all results, with follow-ups merged in), `drift_signs.csv` (every sign x dataset), and logs `h*.log`.

## Findings first

1. **No difference between name signs and frame signs over time, in either direction.** The model predicted that name-core signs turn over and frame signs persist. The data show neither that nor the reverse.
   - Sign level (P1): frequency-matched core-minus-frame drift S = -0.034 (95% CI -0.095 to +0.025), one-sided p = 0.75. The sign is opposite to the prediction, but not significantly (two-sided p = 0.51).
   - Name strings (P2), the direct test of "persons vs offices": S = -0.077 (CI -0.161 to +0.007), p = 0.93. Again the opposite sign, n.s. (two-sided p = 0.14).
   - Holm-adjusted p = 1.0 for both. **Verdict: inconclusive.**
   - One sensitivity check leans toward the damaging direction: with the M77 Mohenjo-daro depth tertiles in place of ICIT periods, frame strings drift *more* than core strings (two-sided p = 0.037). This is one of six checks, not corrected, and should not be read as a reversal.
2. **What the null rules out, and what it doesn't (power).** In the planted-turnover simulation, P1 detects (power 1.0) a world where half or more of the core signs lose at least half of their out-of-period uses. That world gives S = +0.23 or more, which lies far outside the observed CI. Weak turnover would go undetected:
   - 30% of cores, 30% moved: power 0.18, S = +0.03 (inside the CI);
   - 50% of cores, 20% moved: power 0.05.

   So **strong, person-like turnover of core word signs across strata is excluded; mild turnover is not.** This fits the typology result that core signs are reusable word signs, not names. The ICIT period scale is also too coarse to resolve "a generation": periods last centuries, and Harappa 3B/C is a mixed deposit category.
3. **Survival curves show the same.** Rarefied to equal sample size per period, the share of signs in period t that recur in t+1 is what sampling predicts, for every class at every site. Deficits for CORE run -0.001 to +0.028 and for FRAME -0.053 to +0.060. The core-minus-frame difference ranges from -0.055 to +0.059 by site, and every CI includes 0. As raw counts, frame strings look more persistent (seen in more than one period: 0.33-0.55 vs 0.07-0.39 for core strings). That gap is entirely frequency, and it vanishes under matching.
4. **A relative chronology of sign use exists at Harappa (P3, pre-registered, positive).** Per-sign early/late shifts (within object type) agree between the two independent Harappa excavations: HARP periods 3B, 3B/C, 3C against Vats 1920s depth tertiles within locus. Spearman rho = 0.48 over 53 shared signs, p = 0.002; pooled over 3 pairs r = 0.30, p = 0.001.
   - Exploratory robustness: the result survives fine object types as strata (incised vs moulded tablets, seal shapes): rho 0.43, p = 0.002. It survives removing the 54 texts found in both excavations: rho 0.45, p = 0.004. Leave-one-sign-out minimum rho is 0.45. It holds within frame signs (rho 0.70, n = 16) and within core signs (0.45, n = 30).
   - **It does not transfer cleanly to Mohenjo-daro:** HAR~MD rho 0.15 (p = 0.16); Vats~MD 0.25 (p = 0.034); seals only, Vats~MD -0.02.
   - Signs that run late in both Harappa excavations: M127, M387, M197, M341, M72, M173, opener M293. Early in both: closer M12, M375, opener M205, M1, title element M347.
   - This reverses the earlier "no change in sign use over time" (context Q5). That test asked whether single signs pass BH, which none do. This test pools the weak per-sign shifts and asks whether two independent excavations agree, which they do.
5. **No datable innovation (P4).** None of 302 sign x dataset tests reaches q < 0.05 (best: Lothal connective M99, p = 0.0024, q = 0.46; MD tall-2 M87 later, p = 0.004, q = 0.46). Power is the limit: a sign seen *only* in one period needs about 4-14 occurrences (depending on dataset) to pass BH, and almost every sign rare enough to be period-restricted falls below that. The chronology lives in many small frequency shifts, not in signs appearing or vanishing.
6. **Context for m328_measure.** The sign M328 itself does not drift (HARP p = 0.48), and neither do tall 2/3 (M87, M89) at Harappa. The period shift that m328_measure found is in *which stroke value* goes with the cup, not in the signs.

## Data and what is usable

Unit: a distinct text in a period (mould copies count once per period).

| dataset | source | ordering | units | caveat |
|---|---|---|---|---|
| HAR | ICIT, HARP | 3B < 3B/C < 3C | 485 | 92% tablets in 3B and 3B/C; 3C adds pots and seals |
| HAR_VATS | M77 Harappa (Vats) | depth tertile within locus (8 loci) | 520 | independent of HARP; depth ≠ phase |
| MD | ICIT | Early < Intermediate < Late | 758 | Early only 45; sub-phases not used (numbering direction uncertain) |
| MD_M77 | M77 depth tertiles | within locus | 1,097 | same objects as MD; sensitivity check only |
| DHO | ICIT | stage 4 < 5 < 6 | 112 | thin |
| KAL | ICIT | II early+middle < late | 101 | 3-4 signs per class with n ≥ 5: no power |
| LOT | ICIT | Rao phase II < III < IV | 83 | phase II has 9 units |

Not usable: Harappa Period 1-2 (22 pot marks, already covered by context Q5), Dholavira stages 1-3 (3 texts), and every other site (fewer than 10 dated texts). ICIT signs were mapped through the Mahadevan-Wells bridge; 12-19% of ICIT tokens are unbridged and get no role. Roles are the top-weight role in `functional_reading/lexicon.csv`: CORE = noun or fish-class noun; FRAME = opener, connective, closer, title element, post-closer clitic, bracketed-fish closer; numerals are kept apart. Note that M328 is labelled NOUN there.

## Method (summary; full spec in the prereg)

- **Drift D** per sign: G statistic of the sign's period distribution against the within-object-type expectation, minus its permutation-null mean, divided by n. It has mean 0 at every frequency under no time structure.
- **P1/P2 null:** CORE/FRAME labels shuffled among signs (or strings) within dataset x frequency quintile, 10,000 times.
- **Persistence:** rarefied recurrence from t to t+1 minus the type-stratified permutation null, with a bootstrap over units.
- **P3:** Spearman correlation of per-sign shifts between datasets, against a null with periods permuted within object type.
- **P4:** exact permutation per sign, then BH across all 302 tests.
- **Planted power:** occurrence swaps that concentrate a chosen core sign in a home period while preserving frequencies.

## Hypotheses tested

| id | hypothesis | result | verdict |
|---|---|---|---|
| P1 | core signs drift more than frequency-matched frame signs | S -0.034, p 0.75 (reverse n.s.) | inconclusive (strong turnover excluded, power 1.0; weak not, power ≤ 0.18) |
| P2 | core strings (persons) drift more than frame strings (offices) | S -0.077, p 0.93 (reverse two-sided p 0.14) | inconclusive |
| P3 | per-sign time shifts replicate across independent strata | HAR~Vats rho 0.48, p 0.002; pooled p 0.001 | **supported at Harappa**; weak to absent across sites |
| P4 | period-restricted signs beyond sampling | 0/302 at q < 0.05 | not detected (low power for rare signs) |
| sens | seals only / MD_M77 / HAR 3B vs 3C / n ≥ 10 | S -0.063 / -0.018 / -0.049 / +0.000, all n.s. | same as P1 |

## Honest limits

- Each period lasts centuries, so this cannot see turnover within a generation. It can only see whether a sign or string is tied to one period. The name-core prediction was therefore tested in its strong form only.
- In the class contrast, only Harappa (both excavations) and Mohenjo-daro carry weight. DHO, KAL and LOT have 3-10 signs per class.
- HARP is mostly tablets and Mohenjo-daro mostly seals. Object type is controlled within each dataset, but the two sites sample different registers. That may be why the Harappa chronology does not carry over to Mohenjo-daro.
- Vats depth tertiles within locus are a rough proxy for phase. That they still agree with HARP phases is part of why P3 is convincing.

## Next experiments

1. Red-team P3: reimplement it independently, try a different Vats ordering (absolute depth by mound, AB vs F), and test whether the shared early/late sign sets predict the phase of held-out Harappa texts.
2. Use the P3 shift vector as a relative date for undated Harappa texts and objects, and check it against the HARP 3C seal shapes (square vs round seals, R vs S).
3. Name-string turnover at generation scale needs finer stratigraphy: HARP lot/feature numbers (Kenoyer and Meadow reports) or Mohenjo-daro sub-phases with a known direction.
