# Red team of #15: final numerals on foreign Indus texts (board task #21, agent H7)

## Verdict: mixed. The excess is real in the readings but belongs to round seals, not to foreign texts as such, and it shrinks to borderline once the 1-stroke and 2-stroke "connective" signs are set aside.

- **Not a reading artefact.** Using Mahadevan's (M77) readings instead of ICIT's makes the effect stronger: 11 of 40 foreign texts end in a numeral, against 2.09 expected (p < 5e-5). The two readings disagree on only 2 of 39 texts, and both disagreements add numeral endings (SALUT-01, SHORT-01).
- **It sits on round seals.** 7 of 23 round foreign seals end in a numeral, against 0.98 expected from square home seals (p = 5e-5). The 17 foreign texts that are not round show nothing: 2 vs 1.1 expected (p = 0.30). Round foreign seals still beat home rectangular seals (7 vs 1.75, p = 0.0012).
- **Home round seals look the same, but there are too few to test.** Only 8 distinct circular seals come from Indus sites in ICIT. 2 of them end in a numeral (25%; one is the 12-stroke W055 block), about the same as the round foreign seals (30%) and five times the square home rate (4.6%). Fisher p = 0.58, but power is only 0.14, so under the pre-registered rule the genre test is **untested**. The data point toward a round-seal genre slot. They do not prove it.
- **Partly a non-count effect.** Of the 9 numeral endings abroad, 5 are signs that may not be counts: W002 (the short-2 sign M99, which works as a connective at home) 3 times, W001 (one short stroke) once and W031 (one tall stroke) once. Counting only real counts (2+ strokes, not W002), the all-foreign result drops to 4 vs 1.06 (p = 0.019), just above the Bonferroni alpha of 0.0167. So under the pre-registered rule the all-foreign claim falls to the non-count attack. The 20-text secondary set still holds (4 vs 0.44, p = 0.00055).

For the crib attack (#4), the practical advice from #15 stands, and is sharper now. On round Gulf-type seals the last slot often holds a stroke group, and that habit may come from Indus round seals generally. Keep final stroke signs out of the name window. Do not read the final slot as a foreign name ending.

## Numbers (pre-registered: `docs/prereg/redteam_final_numerals.md`, sha256 2570ebbc..., logged before running)

| attack | set | obs | expected | p | rule outcome |
|---|---|---|---|---|---|
| reproduction of #15 | ALL 40, SQ pool | 9 | 2.08 | 0.00025 | matches #15 |
| reproduction of #15 | SEC 20, SQ pool | 6 | 0.73 | 5e-5 | matches #15 |
| A1 genre: round foreign vs home circular | 7/23 vs 2/8 | | | Fisher 0.58, power 0.14 | untested (power < 0.5) |
| A2 round foreign vs home rectangular, length-matched | 23 | 7 | 1.75 | 0.0012 | |
| A round foreign vs home square | 23 | 7 | 0.98 | 5e-5 | |
| A non-round foreign vs home square | 17 | 2 | 1.10 | 0.30 | effect absent |
| B M77 readings | ALL 40 | 11 | 2.09 | < 5e-5 | survives |
| B M77 readings | SEC 20 | 7 | 0.72 | < 5e-5 | survives |
| C count-only (no W001/W002/W031) | ALL 40 | 4 | 1.06 | 0.019 | explained (p > 0.0167) |
| C count-only | SEC 20 | 4 | 0.44 | 0.00055 | survives |

Home final-numeral rates (distinct ICIT texts, length >= 2): square/unspecified 4.6% (n = 1,507), rectangular 6.6% (n = 350), circular 25% (n = 8). For counts only: 2.3%, 4.0%, 25%.

Final numeral signs abroad and how often each ends a text at home (square seals): W002 x3 (home 3.3% of its tokens are final), W033 = 3 tall strokes x2 (6.5%), W001 x1 (7.0%), W004 = 4 short strokes x1 (6.5%), W031 x1 (11.4%), W055 = 12-stroke block x1 (4.8%).

Planted control: with 30% of foreign texts forced to end in W004, the length-matched test reached p < 0.05 in 100% of 1,000 runs, so attacks B and C had power.

## What was not done or failed
- Task item (2), checking the endings of UR-02, UR-05, BAHRAIN-04, BAHRAIN-07 and UNPROV-08 against drawings: no usable drawings are open (see #12: Gadd's plates are coarse halftones). I could only compare two independent readings (ICIT vs M77). They agree on every one of these endings being a stroke sign, except that UR-02's published M77 ending is M107 (5 strokes) where ICIT has W002. A 9- vs 12-stroke reading of BAHRAIN-07 does not change the outcome.
- Home circular seals: only 8. A real genre test needs more round Indus seals, for example from Lothal, Dholavira and Gola Dhoro reports not in ICIT. The data step: list every circular Indus-site seal with a legible text.
- glib's `icit_register` labels SEAL:R as "round_seal", but SEAL:R objects are rectangular (width/height median 2.2). Anyone using glib's "round_seal" register is mixing rectangular and circular seals.
- Only one test design per attack; 3 attacks in total, Bonferroni 0.0167.

## Files
`test.py`, `results.json`, `ledger_rows.csv`.
