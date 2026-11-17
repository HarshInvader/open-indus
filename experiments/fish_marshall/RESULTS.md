# fish_marshall: do ticked-fish seals cluster by block outside Mackay's register?

**Verdict (pre-registered rule): INCONCLUSIVE.** The Marshall 1931 seals show no block clustering of ticked fish: family-level p = 0.88. But this sample cannot answer the question. Only 6 of the 15 ticked-fish seals have a block-level findspot, and power to detect a block-sized cluster is 0.00 under the pre-registered null. So this neither replicates nor refutes the Mackay (FEM) result, redteam family p = 0.0056.

## Findings

1. **Primary test, null.** Ticked fish (M60/M66/M68/M71/M73) were tested against block, permuting within area x 5-ft depth band and collapsing text families:
   - G = 10.4 against a null mean of 12.4, p = 0.878 (10,000 permutations).
   - The sample is 165 seals in 12 units, 6 of them ticked fish, each in a different unit.
   - No text families merged, so the non-collapsed p is the same (0.890).
2. **Power is zero; this is the deciding fact.**
   - Adding 4 ticked fish to one block of 15 or more seals reached p < 0.05 in 0 of 200 plants. Raising one block's rate sixfold also gave 0/200.
   - The cause: inside an area, a 5-ft depth band mostly covers only one or two blocks (14 strata, 25% of seals sit in strata with a single unit). The within-stratum permutation can barely move seals between blocks, so the null already looks like the data.
   - Relaxing strata to area only (not pre-registered) still gives p = 0.73, with power 0.08.
3. **Plain-fish control is null, as it should be:** p = 0.82 (46 families in 159 seals).
4. **Leave-one-block-out:** p ranges from 0.73 to 1.00 over the 6 units holding a ticked fish. No block drives anything.
5. **Secondary tests (exploratory):**
   - By field-number group (all 469 seals, 15 ticked fish): p = 0.071. A numeric-only grouping variant gave p = 0.025, but that is a forking path.
   - By area: p = 0.093. The ticked-fish share is highest in VS (5/69) and lowest in DK (2/148).
   - These are weak hints, not a replication.
6. **Fisher combination** with the FEM p gives 0.031. It is driven entirely by FEM and adds no evidence.

## Register re-read (task 2)

- The MIC vol. II seal tabulation (pp. 402-405) was transcribed in full: serials 1-557 plus 526b, 528b and 557b, 560 rows. Each row has its level and site/field number.
- Every row was cross-checked against independent readings:
  - Apple Vision OCR of the site column on three different scans (archive.org A, DLI B, OLMh C).
  - The old djvu parse.
  - ICIT idno links (prefix + field + serial).
- Results:
  - **Depth vs M77 level: 450/450 within 1 ft (100%; target 90%)**, 77% exact. The old djvu parse managed 76%.
  - ICIT depth agrees within 0.2 ft for 227/228 rows.
  - 512 rows are confirmed by at least one other reading.
- The prereg rule dropped 9 rows that were unconfirmed and conflicted with the djvu reading: serials 264, 265, 267-271, 344 and 477.
- Result: 544 reliable rows, of which 469 are reliable M77 seals: HR 164, DK 148, VS 69, other 59, SD 17, L 12.
- Caveat: M77 levels probably come from this same register. The 100% match shows the transcription is faithful, not that the depths are independently true.

**The block, house and room findspots are not in the tabulation.** It has only plate, size, level, type, material and site/serial. Findspots came from the ICIT field records, linked by register identifiers only (prereg amendment A1, hashed before any findspot was read): 164 reliable seals have a block. The MIC prose gave findspots for 86 field numbers, but only 2 of them are block-located seals in this register.

## Deviations from the pre-registration

- A manual transcription is the primary reading of the tabulation. Vision OCR is used only as a confirming reading, because Vision on whole pages read the columns vertically and was unusable.
- Amendment A1 made the ICIT findspot fields source (a), because the tabulation has no block column. It was hashed at 05:45Z, after the original prereg (05:31Z) and before any findspot analysis.
- The decision rule picked U_block as primary: 165 seals, 6 ticked fish, 7 units with 8 or more seals.
- The area-only-strata run (row `fm_x_areaonly`) was not pre-registered. It is reported only to explain the low power.

## What would settle it

The real limit is 15 ticked-fish seals with block findspots for only 6. The next step is more located seals. Two sources could add them:
- Mackay's DK-G register (already used) or the remaining Marshall house lists, read from vol. I chapters by house.
- Pooling FEM and Marshall into one model with area-specific strata.

Either needs a new prereg.

## Files

- `test.py` runs the test and writes `results.json`, `test.log` and `analysis_table.csv`.
- `register.py` builds `register.csv` and `register_summary.json`.
- `manual_B.txt` is the transcription. `vision_read.py` writes `vision_reads.csv`. `prose.py` writes `prose_findspots.csv`.
- Pre-registration: `docs/prereg/fish_marshall.md` (+ A1). Hashes are in `docs/prereg/HASHES.txt`. Ledger rows are `fm_*` in `docs/test_ledger.csv`.
