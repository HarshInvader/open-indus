# Pre-registration: reg_findspot (house/room co-location of Mohenjo-daro seals, Mackay 1938)

Registered 2026-11-14 in `experiments/reg_findspot/`, BEFORE any sign was compared across findspots. Hash goes into `docs/prereg/HASHES.txt` (tag `reg_findspot`), together with `experiments/reg_findspot/data.py` and `findspots.csv` (tag `reg_findspot_data`).

What had been looked at when this was written: the findspot strings, depths and parse flags of the 695 FEM register rows; counts of seals per block/house/room; the number of same-unit and different-unit pairs per stratum (house level, 5-ft bands: 390 seals, 36 strata, 552 same-house / 2,096 different-house pairs; room level: 452 seals, 85 strata, 68 / 481 pairs). No sign, opener, closer or text was tabulated by findspot. Previous project results that bear on this were known: administration (titles do not cluster by M77 locus), local_repeats and its red team (repeats of 4+ signs not shown local; one cross-site M162 count formula), identifiers (texts open-ended and unique).

## Data

- `experiments/reg_findspot/findspots.csv`, built by `data.py` from `experiments/old_registers/registers.csv` (Mackay 1938 FEM rows only) joined by M77 text number to `corpus.load.m77_lines()`. 639 FEM seals carry an M77 text (636 seals, 3 ivory/bone rods; rods kept, they are inscribed objects in the same register).
- Units: house = block number + house numeral (405 seals, 84 houses). Room = block + house (or '-') + room number (472 seals). Streets/between-block lanes (153), block-only (9), surface (3) and unreadable blocks (25) are not houses; streets are a single 'street' category in F3.
- Depth = -|register depth| (ft below datum; Mackay's table is depth-sorted, a leading '+' is an OCR minus). Spilled depths in the room column are recovered; outliers (> 3 ft from the running median of 9 serial neighbours) are replaced by the M77 level if consistent, else dropped; missing depths take the M77 level. Depth agrees with M77 level within 1 ft for 631/636.
- Depth band: band5 = floor(depth_below_datum / 5 ft) (primary); band3 (3 ft) as sensitivity only.
- OCR ambiguity reported: 43 house numerals repaired (e.g. rv->IV, HI->III, 11->II), 25 blocks unreadable (dropped from house/room/block analyses), 4 houses unreadable.

## Sign elements (per seal; M77 numbering)

- side-0 sequence `seq_side0` (first side, lines joined); all sides for 'whole'.
- opener = first sign of side 0 (missing if '#'); closer = last sign of side 0 (missing if '#'); core = set of side-0 signs excluding first and last (needs >= 3 signs); whole = set of all signs on all sides.
- Classes for F3: M267; M293; M391; NUMERAL = any of M86-M121 except M90, M92, M93 (stroke signs); TICKED FISH = any of M60, M66, M68, M71, M73.

## F1: shared elements within house / room (confirmatory family of 8, Holm)

- Pairs: all pairs of seals in the same stratum. House level: stratum = block x band5; unit = house_key. Room level: stratum = block x band5; unit = room_key. Strata with one unit only are dropped. Pairs with identical side-0 sequences are excluded (they belong to F2); sensitivity: included.
- Similarity per element: opener equal (0/1), closer equal (0/1), core Jaccard, whole Jaccard. Pairs where either seal lacks the element are skipped for that element.
- Statistic T = mean similarity over same-unit pairs minus mean over different-unit pairs (pooled across strata).
- Null: permute unit labels among seals within each stratum (unit sizes kept), 10,000 permutations. Two-sided p = min(1, 2 x min(p_upper, p_lower)), each tail (1 + #)/(1 + n).
- 8 tests = 4 elements x 2 levels; Holm at 0.05.
- Power: planted household signature. For each unit, a signature sign is drawn from the MD slot distribution (opener: first signs; closer: last signs; core/whole: medial signs) and, for each seal of the unit, with probability q in {0.25, 0.5} the opener/closer is replaced by it, or one core sign is replaced by it (texts >= 3 signs). Power = share of 200 plants with two-sided p <= 0.05/8 (Bonferroni, conservative), 1,000 permutations each.
- Interpretation: household/office signature SUPPORTED if any element has upper-tail Holm p < 0.05 at house or room level. Personal-ID distinctness (texts of one house deliberately different) SUPPORTED if any element has lower-tail Holm p < 0.05. Otherwise: no sharing beyond block and depth; a signature of strength q is EXCLUDED for an element/level only where planted power at that q >= 0.8, else that cell is INCONCLUSIVE.

## F2: repeated and near-repeated texts (confirmatory family of 3, Holm)

- Repeat pairs among the 639 seals: identical side-0 sequences of >= 3 signs with no '#', or one-sign-longer variants (the shorter, >= 3 signs, is the longer with exactly one sign removed).
- Statistics: (a) number of repeat pairs in the same block; (b) number in the same house; (c) among repeat pairs with both depths, mean |delta depth|.
- Null: permute findspots (block, house, room, depth together) among the 639 seals, 10,000 times. (a),(b) one-sided upper p; (c) two-sided p.
- Interpretation: office/holder co-location supported if (a) or (b) Holm p < 0.05. Successive holders vs contemporary duplicates is DESCRIPTIVE: among repeat pairs in the same block, median |delta depth| > 2 ft reads as successive, <= 1 ft as contemporary; with < 5 such pairs we report it as unresolved.
- Expected: few pairs (< 15); power will be reported as the null distribution of (a),(b) and the smallest count that would reach p < 0.05.

## F3: sign classes concentrated in blocks / houses (confirmatory family of 10, BH)

- Feature per seal: contains M267, M293, M391, NUMERAL, TICKED FISH (any side).
- Level A (block): units = numbered blocks with >= 8 text-bearing seals, other numbered blocks pooled as 'other', streets as 'street'. Statistic G (likelihood-ratio) of feature x unit. Null: permute unit labels within band5 (seals without depth form their own band), 10,000 permutations; one-sided upper p.
- Level B (house within block): units = houses with >= 3 seals; G over houses; null permutes house labels within block x band5.
- 10 tests = 5 features x 2 levels; BH q < 0.05 = concentrated.
- Power: for the M267 feature, plant a 3x enrichment in one randomly chosen block with >= 20 seals (level A) / house with >= 6 seals (level B) by switching the feature on in extra seals there; power = share of 200 plants with p <= 0.005 (= 0.05/10).
- HR vs DK: the Mackay register is DK-G area only, so the HR/DK split cannot be tested at room resolution here; this is reported, not tested (administration already refuted the coarse area version).

## Counterevidence / falsification

- F1 positive result would be weakened if driven by one house (report leave-one-house-out range) or by identical/near-identical texts.
- Findspots of seals record where they were lost/discarded, not where the holder lived; street and fill finds dilute any household signal. A null result therefore bounds, but does not exclude, household signatures.

## Multiplicity

21 confirmatory tests (8 + 3 + 10), families corrected separately as stated. Everything else is exploratory and labelled so.
