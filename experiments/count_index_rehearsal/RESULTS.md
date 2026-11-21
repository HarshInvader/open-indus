# Count-likeness index rehearsal (plan 10, Route 1, step 1)

2026-11-21. Prereg: `docs/prereg/count_index_rehearsal.md`, hashed with `cir.py`, `dedup.py` and `pc_classes.py` in `docs/prereg/HASHES.txt` at 01:38:55Z, before any index was scored. Code: `cir.py`. Output: `results.json`, `score.log`, `extract.json`, `dedupcheck.json`.

## Verdict: NO-GO

- **The rehearsal fails on proto-cuneiform.** Two of six frozen bars fail, and both are proto-cuneiform bars.
- **Plan 10's kill condition applies.** Route 1 step 2 (the index on real Indus heads) should not run under this prereg.
- **Latin passes easily.** The index separates counts from numbered titles and unit names at AUC 0.99, with power 0.995.
- **The planted Indus gate passes.** Power is 0.986.
- **Why proto-cuneiform fails:** its person, office and place heads are not frozen. They take many different numbers, just as goods do. The known answer the plan asked for ("person, office and place signs must not be called counted") does not hold in this corpus. Plan 10 says it too: "Every number there is a count." So the index did not fail to find frozen numbers in proto-cuneiform. There were none to find. The failure still stands, because the bars were frozen before scoring.
- **No index was computed for any real Indus head.**

## Bars (frozen; all needed for GO)

| bar | requirement | result | pass |
|---|---|---|---|
| B1 | proto-cuneiform power >= 0.80 | 0.276 | no |
| B2 | proto-cuneiform head-level balanced accuracy >= 0.80 | 0.50 (sensitivity 1.00, specificity 0.00) | no |
| B3 | Latin power >= 0.80 | 0.995 | yes |
| B4 | Latin separation (mean AUC) >= 0.90 | 0.988 (5th percentile 0.971) | yes |
| B5 | planted Indus gate power >= 0.80 | 0.986 | yes |
| B6 | false alarm <= 0.06 (proto-cuneiform, Latin, gate) | 0.049, 0.052, 0.046 | yes |

## Numbers per script

**Index.** The expected number of distinct numeral values in 4 tokens of a head, by rarefaction (1 to 4). A head needs at least 8 tokens. A head is called counted if the index is 2.0 or more. Each corpus was cut 1,000 times to about 700 tokens, with 8 to 30 tokens per head. Power is a per-draw permutation test of AUC at p <= 0.05. Texts were de-duplicated with the non-chaining greedy method. The fast version of that greedy method gave output identical to `dedup.greedy` on all three checks.

**Proto-cuneiform** (4,600 tablets, 103 heads: 52 commodity, 51 person, office or place; about 41 heads and 709 tokens per draw).
- Mean AUC 0.61 (5th percentile 0.48). Power 0.28. At the strict 349-token cut, power is 0.17.
- All 51 person, office and place heads were called counted in at least 99% of draws.
- 51 of 52 commodity heads were also called counted. KU3 was called counted in 67% of draws.
- **Exploratory, after scoring:** EN takes 134 distinct numeral notations in 604 tokens, with a modal share of 0.35. SAL takes 82 in 382 (0.23) and SANGA 44 in 147 (0.30). Barley SZE takes 317 in 666 (0.06). So commodities do vary more, which is why the AUC sits above 0.5. But both groups sit far above the counted line.

**Latin** (EDH, 76,584 inscriptions after de-dup; 76 heads: 11 count words, 65 frozen, namely "vir" titles plus legion, cohort and ala names; about 44 heads and 709 tokens per draw).
- Mean AUC 0.988, power 0.995, false alarm 0.052. 5 draws were skipped because they had fewer than 3 counted heads, and they count as failures.
- Without "vir": AUC 0.988, power 0.996.
- **Head-level calls are weaker than the ranking.** All 11 count words are called counted. But 28 of 65 frozen heads are called counted too, giving balanced accuracy 0.78.
  - These are mostly numbered cohort series such as `coh:praet`, `coh:urban` and `coh:vigil`. Each is a name, but the series runs I to X or more.
  - Legion epithets with one fixed number, such as Ulpia, Primigenia and Fulminata, are called frozen.
  - So the index ranks well, but the fixed 2.0 line does not mark the counted/frozen boundary by itself.
- At the strict 349-token cut, power is 0.66. 342 of 1,000 draws had fewer than 3 counted heads, because Latin has only 11.

**Proto-Elamite (descriptive only).** The repo has no reliable class labels for PE signs, so no bar applied.
- 124 heads with 8 or more tokens. Index quartiles 2.77, 3.38 and 3.68.
- 95% of drawn heads are called counted.
- This fits "every number is a count", and it means the index does not find frozen numbers where there are none.

**Planted Indus gate.**
- Real dev after greedy de-dup gives 20 heads with 8 or more tokens. A draw holds 261 tokens on average, because each head is capped at a random 8-30 tokens.
- Each draw plants 30% of the heads as counted (values drawn from the real pooled dev numerals of their stroke system). The rest are frozen: one value on 70% of tokens, pool draws on the other 30%.
- Power 0.986, mean AUC 0.938, false alarm 0.046.
- With the frozen share at 0.90 (about the tall 2 + fish rate): power 1.00, AUC 0.995.
- Head-level calls at 70% frozen share: 96% of counted heads are called counted, but only 64% of frozen heads are called frozen.
- Indus data supplied only head sizes, stroke systems and the pooled value marginals. No real head's values were read.

## What this means for Route 1

- **The index itself works on a clean contrast.** Numbered names against counts at Indus size, in Latin and in the planted gate.
- **It cannot pass the rehearsal as frozen.** The proto-cuneiform contrast it was asked to pass is not a counted-against-frozen contrast. In proto-cuneiform, people and institutions are counted or receive counted goods.
- Changing the labels or thresholds now would be loosening after seeing data. So the step stops here.
- **A future rehearsal needs a second script with real frozen numerals.** It would need its own prereg. Candidates: Linear B personal names with numerals; Greek or Egyptian titles such as "the Thirty"; Mesoamerican calendar names. In that rehearsal, proto-cuneiform should serve only as an all-counts check, the role PE plays here.

## Limits

- **The proto-cuneiform head rule is mechanical.** It takes the first sign after the numeral group, so in entries like "2(N01) , EN ..." the head may be the recipient rather than the counted thing. A better head rule would not create frozen numerals, though. EN with "1(N01)" is still only 35% of EN tokens.
- **Latin labels come from a fixed lexical rule.** Numbered units (legion, cohort, ala) are names, but one epithet can carry several numbers (Augusta takes II, III and VIII), so some "frozen" heads vary. The "vir" head mixes IIvir, IIIIvir, VIvir, Xvir and XVvir on purpose.
- **Indus at dev size is smaller than the plan's 700 tokens.** It is 20 heads and about 261-349 tokens. At 349 tokens even Latin drops to power 0.66, because draws run short of counted heads. Any step 2 on dev alone would be below the size this rehearsal validated.
- **The planted gate is only partly realistic.** Its "count" draws come from the real pooled Indus numerals, which frozen formulas dominate, so planted counted heads are less varied than real counts. That makes the gate harder, not easier. The gate passes because the frozen planted heads are frozen by construction.
- **Tests run:** 5 scored runs, 2 strict-cut runs, 1 PE descriptive run and 1 verdict, plus 1 exploratory diagnostic (the PC value spreads above), which is not part of the verdict.

## Hypotheses

| hypothesis | verdict |
|---|---|
| The index separates counted from non-commodity heads in proto-cuneiform at Indus size | refuted (power 0.28, AUC 0.61) |
| The index separates counts from numbered titles and units in Latin at Indus size | supported (power 0.995, AUC 0.988) |
| The index detects planted counted vs frozen heads at real Indus dev sizes | supported (power 0.986) |
| Route 1 rehearsal GO | no (NO-GO by B1, B2) |

## Next experiments

1. Write a new prereg for a rehearsal on a script with known frozen numerals (Linear B or later cuneiform titles, Greek "the Thirty"). Use proto-cuneiform and PE only as all-counts checks. This is a new test, not a re-score of this one.
2. If that passes, size step 2 to dev + held-out + ICIT new sites pooled. On dev alone the counted class will be too small, as the Latin strict cut shows.
