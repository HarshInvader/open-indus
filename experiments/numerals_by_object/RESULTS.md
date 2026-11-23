# Do Indus tablets carry counted numerals more than seals do? (prereg `numerals_by_object`, hashed 2026-11-23T20:41:22Z)

**Verdict: powered negative. Tablets do not use more count-like numerals than seals from the same city.**
- The planted gate catches a tablet-seal gap of 1.0 index units with power 1.0 (c\* = 1.0). A real-script gap measured the same way, Latin epitaph ages vs honorific and military unit numbers at Indus sizes, is 0.93.
- **The real gap runs the other way:** D = −0.38 (Harappa −0.43, Mohenjo-daro −0.32), with one-sided p = 1.0 against the "tablets count more" null.
- **Beside the old result:** `count_index_rehearsal` (2026-11-21) was NO-GO on its proto-cuneiform bars. This study swaps that gate for a Latin object-type known answer (stated in the prereg as a changed gate), and the question is now an object contrast, not head-level calls.

## Kill test (Latin at Indus sizes; `kill.json`)
| | value |
|---|---|
| power (200 draws, p ≤ 0.01 and D > 0 at both "sites") | **1.0** |
| mean Latin D (epitaphs minus honorific/building/military) | 0.93 index units |

The Latin contrast is extreme, so this gate shows only that the pipeline sees a real counted-vs-frozen split at Indus token counts. The planted gate sizes the test.

## Planted gate (label swaps within site, texts never edited; `full.json`)
| Δ (index units added to the tablet mean) | 0.25 | 0.5 | 1.0 | 1.5 |
|---|---|---|---|---|
| feasible draws | 40 | 40 | 40 | 0 |
| power | 0.00 | 0.20 | **1.00** | — |

- c\* = 1.0, close to the Latin gap (0.93). A Latin-sized gap is at the edge of what the test sees. A gap of half that size (0.5) would be missed 80% of the time.

## Real Indus statistic (2,000 within-site permutations)
- Tokens on heads with 8 or more tokens: Harappa 22 tablet and 81 seal; Mohenjo-daro 18 tablet and 294 seal.
- D = −0.378. Null mean −0.005, 99th percentile 0.251. p (tablets higher) = 1.0. **Not passed.**

## Exploratory, after the verdict (not sealed)
- **The opposite tail is strong:** p (tablets lower) = 0.0005 over 2,000 permutations.
- **Dropping any one of the top three tablet heads per site leaves D between −0.33 and −0.41.** Both sites stay negative.
- **Tablet numeral heads are mostly fixed:**
  - Harappa: 3 + M403 (4), 7 + M197 (2);
  - Mohenjo-daro copper: 3 + M190 (4), 7 + M194 (3), 1 + M25 (5).
  - Copper tablets come in fixed text types (README #8), so their numbers repeat by design.
- **Reading:** on tablets, numerals behave like parts of fixed names or types more than like counts of goods. This fits "tablets are tokens with their own fixed vocabulary" (atlas 5.10, README #6 and #8). It is not a test of that reading.
- **Possible forward prediction (not sealed here):** numeral heads on newly published tablets (CISI vol. 3, new excavations) will be the same fixed pairs. It would need its own prereg before any new tablet is seen.

## What changes
- **Atlas:** a new entry, "tablets as counting records (numeral form)", refuted at stated power for a gap of 1.0 index units or more, with the observed gap in the other direction.
- **Scorecard (for v2; v1 stays as rated):**
  - Kenoyer & Meadow "tablets as transaction tokens or ration records" is already R. It gains a sized null in the numeral form: tablet numerals are not count-like.
  - MUK19 "stroked jar = metrological unit" is untouched: jars are not in this test.
- **Limits:** about 40 usable tablet tokens; a few heads dominate; the index pools objects; sealings and pots are not tested.
