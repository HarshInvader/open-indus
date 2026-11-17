# Pre-registration: reg_harappa (out-of-sample replication at Harappa of the Mohenjo-daro findspot tests F1 and F3)

Registered 2026-11-14 in `experiments/reg_harappa/`, BEFORE any sign, opener, closer or class was tabulated by findspot. Hash of this file goes into `docs/prereg/HASHES.txt` (tag `reg_harappa`), together with `experiments/reg_harappa/prose.py`, `data.py`, `findspots.csv` and `test.py` (tag `reg_harappa_data`).

What had been looked at when this was written: the Vats 1940 tabulation fields (mound/area, find no., depth below surface); the narrative chapters I-VI of Vats vol. I, parsed for citations of seal plates (Pls. LXXXV-CI) with their square / find no. / depth; per-unit object counts and the number of same-unit / different-unit pairs per stratum; the marginal (not by findspot) number of families carrying each F3 class. Prior results known: reg_findspot (F1 null at MD; F3 only ticked fish clusters by DK-G block), redteam_fish_block (ticked fish WEAKENED; Harappa untestable at M77 locus), reg_chrono (M162 frame deeper at Harappa), administration (titles do not cluster by M77 locus).

## Findspot resolution available (step 1, descriptive)

- The Vats tabulation itself gives only Mound/Area (F, AB, D, G, H, J), find no. and depth below the local surface. It has no trench/square/locus column.
- Square-level findspots come from the narrative chapters, where Vats lists finds as '... Pl. XCVI, 429. Size ... No. 10359; Square I 8/10; Depth 15 ft. 6 in. b.s.' (`prose.py`). A citation is used only if corroborated against the register row of that serial (find no. agrees after OCR normalisation, one-character edit allowed; a readable conflicting find no. rejects; if a find no. is missing, the depth must agree within 1 ft). See `data.py` docstring.
- Grid: square 'I 9/24' = big square I9 (Vats's lettered-numbered grid square) and sub-square 24 (of 25 numbered sub-squares in the big square).
- Coverage: 552 register objects carry an M77 text (seal 260, miniature tablet 170, sealing 121, rod 1); 295 of them have an accepted square (F 225, AB 43, D 19, J 5, H 3), in 47 big squares and 184 sub-squares. Register depth agrees with the M77 level within 1 ft for 485/522; with the narrative list depth for 262/284.

## Unit of analysis: text families

- Harappa tablets repeat one text many times. Objects with an identical full text (all sides, `seq_all`) in the same big square are one family; the family keeps its lowest serial (its depth, sub-square, type). This gives 287 families from 295 objects with squares.
- All tests use families. Sensitivity (reported, not confirmatory): seals only.

## Sign elements and classes (M77 numbering; identical to reg_findspot)

- opener = first sign of side 0 (missing if '#'); closer = last sign of side 0; core = set of side-0 signs excluding first and last (>= 3 signs); whole = set of all signs on all sides.
- F3 classes (any side): TICKED_FISH = M60/M66/M68/M71/M73; M267; M293; M391; NUMERAL = M86-M121 except M90, M92, M93; plus three classes added for Harappa: M342 (jar), M99, M162 (count frame; reg_chrono definition: contains M162).
- Marginal counts among the 287 families: TICKED_FISH 3, M293 6, M162 19, M391 15, M267 30, M99 49, M342 134, NUMERAL 185. Ticked fish is too rare at Harappa for any test with power; it is run and reported but its verdict is fixed in advance as UNTESTABLE unless planted power >= 0.5.

## F1: shared elements within a locus (confirmatory family of 8, Holm) — replication of the MD null

- Level A (big square, analogue of MD house): stratum = mound x band5 (band5 = floor(depth below surface / 5 ft)); unit = big square. 283 families, 46 units, 12 strata, 885 same / 6,000 different pairs.
- Level B (sub-square, analogue of MD room): stratum = big square x band5; unit = sub-square. 239 families, 138 same / 773 different pairs.
- Strata with one unit dropped; families without depth dropped. Pairs with identical side-0 sequences excluded.
- Statistic T = mean similarity of same-unit pairs minus mean of different-unit pairs (opener equal, closer equal, core Jaccard, whole Jaccard), pooled over strata. Null: permute unit labels within stratum, 10,000 permutations; two-sided p = min(1, 2 min tail), tails (1+#)/(1+n). Holm over 8.
- Power: planted locus signature exactly as reg_findspot (signature sign per unit drawn from the Harappa slot distribution; each family takes it with probability q in {0.25, 0.5}; 200 plants x 1,000 permutations; hit = p <= 0.05/8).
- Verdicts: signature SUPPORTED if any upper-tail Holm p < 0.05; distinctness SUPPORTED if any lower-tail Holm p < 0.05; otherwise "no sharing", with strength q EXCLUDED where power >= 0.8, else INCONCLUSIVE. The MD null REPLICATES at a level if no element there is Holm-significant and at least one element has power >= 0.8 at q = 0.5.

## F3: sign class x locus clustering (confirmatory family of 16, BH)

- Level A (big square): units = big squares with >= 8 families; smaller squares pooled per mound ('other_F', 'other_AB', ...). G statistic of class x unit. Null: permute unit labels within mound x band5 (families without depth form their own band), 10,000 permutations, one-sided upper p.
- Level B (sub-square within big square): units = sub-squares with >= 3 families; null permutes sub-square labels within big square x band5.
- 16 tests = 8 classes x 2 levels; BH q < 0.05 = concentrated.
- Power per class and level: plant a 3x enrichment in one random unit with >= 20 families (A) / >= 6 (B), as reg_findspot; and an "MD-sized cluster": add 4 class bearers in one random unit with >= 15 families (A) / >= 5 (B) (block 12 had 4 of 19 ticked fish). 200 plants x 1,000 permutations, hit = p <= 0.05/16.
- A class/level with power < 0.5 for BOTH plants is INCONCLUSIVE whatever its p; a non-significant result with power >= 0.8 for a plant EXCLUDES that size of cluster.
- Replication logic: MD found ticked fish clustered and the other four MD classes null. Ticked fish at Harappa: expected UNTESTABLE (3 families). The other four MD classes replicate their null if q >= 0.05 with power stated. M342, M99, M162 are new tests.

## Exploratory (labelled as such)

- Seals-only rerun of F1 and F3; mound-level F3 on all 552 objects (units = mounds, null within band5); leave-one-unit-out for any significant result.

## Caveats fixed in advance

- Vats depths are below the local surface, which varies across a mound; band5 within mound only partly controls time.
- Squares exist only for objects Vats mentioned in the narrative (53% of linked objects); these are not a random sample (more from Mound F granary/working-floor areas). Findspots are loss/discard places.
- 24 confirmatory tests (8 + 16), families corrected separately.
