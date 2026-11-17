# reg_findspot: do seals found in one house or room share signs?

Pre-registered in `docs/prereg/reg_findspot.md`, hashed (tags `reg_findspot`, `reg_findspot_data`) before any sign was compared across findspots. Ledger rows `rf_f1_*`, `rf_f2_*`, `rf_f3_*` (21 confirmatory) and `rf_e2_scan` (exploratory) in `docs/test_ledger.csv`.

Run from the repo root:
- `.venv/bin/python experiments/reg_findspot/data.py` builds `findspots.csv` and `data_summary.json`
- `.venv/bin/python experiments/reg_findspot/test.py` runs the confirmatory tests (`test.log`, `test.json`)
- `.venv/bin/python experiments/reg_findspot/explore.py` runs the exploratory follow-ups (`explore.log`, `explore.json`)

## Findings first

1. **Seals from one house or one room share no more signs than seals from other houses in the same block and depth band (F1: 0 of 8 tests, Holm).** That holds for openers, closers, the medial core and the whole text.
   - House level: 345 seals, 74 houses, 552 same-house and 2,095 different-house pairs. The same opener appears in 4.0% of same-house pairs and 3.0% of other pairs (p=0.46). For the closer it is 12.3% against 13.0% (p=0.61).
   - Room level: 417 seals, 87 same-room pairs. The same opener appears in 5.7% of same-room pairs and 3.1% of other pairs (p=0.37). None of the room tests reaches p<0.3 after correction.
   - The test had the power to catch a real signature. Suppose each seal in a house carries one shared house sign with probability 0.5. The test would catch that 98.5-100% of the time at the house level, for every element, and 90-100% of the time at the room level for opener, closer and core. So a household or office signature of that strength is **excluded**. A weaker one (probability 0.25) is excluded only for openers at the house level (power 0.96).
   - There is also no sign of deliberate distinctness, where texts in one house would avoid each other's signs. Every statistic sits inside its null 95% band.
2. **Copies of a text are not kept together and are not contemporary (F2).** Among the 639 seals there are 48 repeat pairs: 17 identical texts and 31 where one text is one sign longer.
   - Same block: 3 pairs against 2.1 expected (p=0.35). Same house: 1 against 0.36 (p=0.30). Significance would have needed at least 6 same-block pairs or at least 2 same-house pairs.
   - Depth: the two seals in a copy pair lie on average 5.7 ft apart. Random pairs lie 5.9 ft apart (p=0.81). Copies are spread through time like unrelated seals. They are not duplicates made at one moment.
   - Whether these are successive holders or contemporary duplicates cannot be decided: only 3 same-block pairs have depths. They are 2.7, 5.4 and 11.6 ft apart, all above the 2-ft "successive" line, but the rule needs at least 5 pairs.
   - The single same-house pair is M204-M245-M342, in house 7/III, adjacent rooms 51 and 52, found 11.6 ft apart in depth. That fits one long-lived household or office, but it is n=1.
3. **One sign class is concentrated by block: the ticked fish (F3).** This was pre-registered as one of 5 classes.
   - Block level: G=36.2 against a null of 16.6, p=0.0007, BH q=0.007. The null keeps depth fixed.
   - 21 seals carry a ticked fish (M60, M66, M68, M71 or M73). Block 12 has 4 of its 19 seals, all in house 12/V (0.65 expected). Blocks 6, 3 and 18 have 2 each. Blocks 1 and 7, the two largest, have 1 of 151 between them (5.2 expected). Streets have 5 of 153, which is what chance predicts.
   - House level: p=0.018, q=0.087, so not significant after correction.
   - Exploratory checks. The block result survives removing house 12/V (p=0.018). The plain fish bases M59, M65, M67, M70 and M72 do not cluster (block p=0.31, house p=0.87).
   - **No other class clusters:**

     | Class | Block level | House level |
     |---|---|---|
     | M267 | p=0.62 | p=0.44 |
     | M293 | p=0.46 | p=0.09 |
     | M391 | p=0.63 | p=0.45 |
     | Numerals | p=0.23 | p=0.12 |

     This repeats, at house resolution, the earlier result that titles do not cluster by M77 locus.
   - Power is limited. A 3x enrichment of M267 in one block would be caught 71% of the time. At house level the power is 0, so the house-level nulls say nothing.
   - Exploratory scan of 70 single signs (each on ≥10 seals): 4 reach p≤0.05 at block level (3.5 expected by chance) and 0 at house level. None reaches q<0.05. The ticked-fish result rests on the class, which comes from an earlier project finding. No single sign drives it.
4. **HR vs DK could not be tested at room level.** Mackay's 1938 register covers only the DK-G area. Marshall's register (HR, VS) gives areas only and its OCR is poor. The coarse area version was already refuted by `administration`.

**What this means.** Seals lost in one house do not carry a household or office sign of any substantial strength. Copies of one text turn up in different houses and at different depths. This fits the project's running picture: texts are built from a city-wide shared vocabulary, and are not house- or office-bound titles. The ticked fish is the one exception. It is a closing-slot modifier (README #3), and it is uneven across DK-G blocks. It could reflect a neighbourhood or workshop habit, or a time effect finer than the 5-ft bands. It rests on 21 seals and is a lead, not a claim.

## Data handling (`data.py` → `findspots.csv`)

- 695 FEM rows. 639 carry an M77 text: 636 seals and 3 ivory/bone rods.
- Findspot types:

  | Type | Seals |
  |---|---|
  | Block / house / room | 405 |
  | Room without a house number | 69 |
  | Street or between-block lane | 153 |
  | Block only | 9 |
  | Surface | 3 |
  | Block unreadable | 25 |

- OCR repairs and ambiguity:
  - 43 house numerals were repaired: rv→IV, HI/Ill/111/UI→III, 11/U→II, vm/VUI/Vlll→VIII, 1→I. They are flagged in `parse_flags`.
  - The repair 11→II could in principle be XI. This affects 4 seals.
  - 4 house numerals were unreadable ('n', 'm', '_', 'DK Area'). They are dropped from house analyses.
  - Rows with an unreadable block, such as 'III / 14', may be ditto marks for the row above. They are not inferred and are dropped from house, room and block analyses.
- Depth:
  - Mackay's table is sorted by depth. A '+' in front of a depth is a misread minus, because the absolute depth increases steadily with the serial number. We therefore use -|depth|.
  - 80 depths had spilled into the room column (e.g. '22 -11-6'). They were recovered.
  - 8 outliers were found. 5 were replaced by the M77 level and 3 dropped.
  - 42 missing depths were taken from the M77 level.
  - The final depth agrees with the M77 level within 1 ft for 631 of 636 seals.
- Several seals in one room are kept as separate objects. F1 excludes pairs with identical texts, which is F2's question. Including them changes nothing (house p=0.36-0.62).
- Sensitivity with 3-ft depth bands: house opener p=0.11, room opener p=0.17; everything else p>0.2.

## Tests (confirmatory)

| Test | Observed | Null | p (raw) | Corrected | Verdict |
|---|---|---|---|---|---|
| F1 house opener | 0.040 vs 0.030 | T 95% band −0.013..0.022 | 0.46 | Holm 1 | no sharing (q=0.5 power 1.0) |
| F1 house closer | 0.123 vs 0.130 | −0.028..0.039 | 0.61 | 1 | no sharing (1.0) |
| F1 house core | 0.039 vs 0.030 (Jaccard) | −0.005..0.015 | 0.44 | 1 | no sharing (1.0) |
| F1 house whole | 0.058 vs 0.051 | −0.007..0.011 | 0.29 | 1 | no sharing (0.985) |
| F1 room opener | 0.057 vs 0.031 | −0.032..0.050 | 0.37 | 1 | no sharing (1.0) |
| F1 room closer | 0.138 vs 0.130 | −0.075..0.056 | 0.68 | 1 | no sharing (0.945) |
| F1 room core | 0.046 vs 0.032 | −0.014..0.033 | 0.49 | 1 | no sharing (0.90) |
| F1 room whole | 0.051 vs 0.053 | −0.014..0.022 | 0.60 | 1 | inconclusive (power 0.03) |
| F2 same block | 3 / 48 pairs | 2.1 | 0.35 | Holm 0.69 | refuted at n available |
| F2 same house | 1 / 48 | 0.36 | 0.30 | 0.69 | refuted at n available |
| F2 depth difference | 5.7 ft | 5.9 ft | 0.81 | 0.81 | not contemporaneous |
| F3 ticked fish, block | G 36.2 | 16.6 | 0.0007 | BH 0.007 | **supported** |
| F3 ticked fish, house | 54.1 | 46.9 | 0.018 | 0.087 | not significant |
| F3 M293, house | 55.8 | 49.2 | 0.09 | 0.30 | null |
| F3 numerals, house / block | | | 0.12 / 0.23 | 0.31 / 0.46 | null |
| F3 M267, M391 (both levels), M293 block | | | 0.44-0.63 | 0.58-0.63 | null (house power 0) |

21 confirmatory tests and 141 exploratory ones were run: the 70-sign scan at two levels plus E1 and E3.

## Caveats and counterevidence

- A findspot records where a seal was lost or thrown away, not where its holder lived. Fill, streets and re-deposition all blur any household signal, so the F1 exclusion holds for findspots as recorded.
- Only DK-G is covered, and only seals. Sealings and tablets with house findspots are not in this register.
- Some house keys may be split by OCR variants, or merged when blocks were misread. A false split would weaken F1, but power was checked on the same keys.
- The ticked-fish result is one significant class out of 10. A blind replication would need house-level findspots from another area (Marshall's HR or VS houses, Vats's Harappa squares). Depth bands 5 ft wide may also leave a residual time effect.

## Next experiments

- Replicate the ticked-fish block clustering with Marshall 1931 HR/VS house findspots. This needs a better OCR of the MIC register, or a reading of the CISI basic-data "findspot" field.
- Parse Mackay's "List of objects" room lists, so that seals can be set against the other objects found in the same room.
- Re-test F2 when Marshall's register is readable: HR adds about 300 seals, so there would be more copy pairs inside one block.
