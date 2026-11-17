# R7: are any signs tied to a craft or facility?

Pre-registered in `docs/prereg/assemblage.md` (hash tag `assemblage`) before any text was joined to a craft context. The craft coding (`craft_units.csv`, `build_coding.py`) was hash-frozen (tag `assemblage_coding`) before `test.py` ran. Ledger rows `as_*` in `docs/test_ledger.csv`.

Run, from the repo root:
- `.venv/bin/python -I experiments/assemblage/build_coding.py <vats ocr> <mackay1938 ocr> <marshall vol II ocr> <lothal json>` (full command in the script docstring)
- `.venv/bin/python -I experiments/assemblage/test.py` (log `run.log`)
- `.venv/bin/python -I experiments/assemblage/explore_size.py` (exploratory, log `explore_size.log`)

## Findings first

1. **No sign is tied to a craft or facility at two sites. The test had almost no power, so the result is "inconclusive", not "refuted".**
   - Primary test (sealings and other non-seal objects): 0 of K = 49 sign × context × site-pair tests replicate. The bar was p ≤ 0.032 at both sites with observed/expected ≥ 2 at both.
   - Global count: G = 0 against a null mean of 0.01 (p = 1.0).
   - Planted power is effectively zero. A sign of median frequency that is 3 times as likely in the craft units at two sites is caught 0% of the time; at 5 times, at most 4.5%.
   - Only three contexts reach two sites at all: COPPER and WEIGHT (Harappa and Mohenjo-daro) and STORAGE (Harappa and Lothal).
2. **Adding seals changes nothing.** This was the secondary test. 0 of K = 193 tests replicate, G = 0 (null mean 0.07), and power at 3 times is at most 3.5%.
   - Nearest miss: M197 (W575) in units with weights. Harappa 10 texts vs 5.1 expected (p = 0.0027); Mohenjo-daro 3 vs 0.4 (p = 0.0019). It misses the rule only on observed/expected at Harappa (1.95 against the bar of 2).
   - It is not a real lead. At Harappa, weights are recorded in the find-rich squares, so every common sign looks "enriched" there (the jar M342: 192 vs 118). The frozen null permutes unit labels and does not correct for how many finds a unit has.
   - In the exploratory share-based check (below), M197 does not reach p ≤ 0.05 at both sites.
3. **One exploratory "storage" signal comes from a single seal.** The exploratory check compares a sign's share of records inside craft units with its share outside.
   - It flags M1 (W090) in storage contexts: the Harappa Great Granary area has 4 of 56 records vs 4 of 327 elsewhere (p = 0.019); the Lothal warehouse has 12 of 56 vs 0 of 10 outside (p = 0.005).
   - But 11 of the 12 Lothal hits are impressions of one seal text, W705 W500 W741 W001 W055 W220 W740 W090, on warehouse sealings (Frenez & Tosi 2005 contexts). M343 (W741) flags for the same reason.
   - With one seal per text, the Lothal side is n = 1. The design also had a flaw: each Lothal sealing was its own unit, so repeated impressions of one seal were not merged.
   - M48 (W176) in units with weights (Harappa 25/484 vs 2/113; Mohenjo-daro 4/38 vs 29/874) depends on seals and was not pre-registered.
   - Across 169 sign × context pairs testable at two sites in this check, 2 pass p ≤ 0.05 at both sites (0.42 expected by chance), and 1 of 49 in the non-seal set (0.12 expected). This is not evidence.
4. **The real limit is the data. Very few inscribed objects outside seals have a findspot at the level of a room or house, and the reports record craft evidence selectively.**
   - Units linked to texts: Harappa 60 Vats grid squares (41 with non-seal texts, 383 distinct non-seal text records); Mohenjo-daro 200 houses (74 with non-seal texts, 144 records); Lothal 55 sealings; Chanhu-daro 19 squares (5 non-seal, 9 records).
   - Craft-coded units that also have any text: 104 (Lothal 48, Harappa 36, Mohenjo-daro 11, Chanhu-daro 9).
   - Mohenjo-daro has only 2 copper units, 2 weight units, 1 kiln unit and 1 shell unit with non-seal texts.
   - The Chanhu-daro bead factory (squares 8/C, 9/C, 9/D, 9/F) holds 5 non-seal texts in total.
   - Harappa HARP trenches (Mound E/ET craft areas, about 700 tablets) have no grid square in ICIT, and no open source gives craft evidence per trench, so they could not be used.

## What was built

- `craft_units.csv`: 301 rows of craft indicators per findspot unit, each with a report citation.
  - Harappa: 50 Vats squares. The rows were parsed from Vats 1940's item lists ("…No. X; Square I 13/7"), plus hand-coded rows:
    - the furnaces in Trench IV, Mound F (squares H14, I13, I14, J13; OCR lines 83071-83280);
    - the shell and seal workshop group No. 10460 in J 12/23 (lines 8134-8170);
    - squares in the Great Granary Area.
  - Mohenjo-daro: 16 houses.
    - Mackay 1938's object lists by block and house: ingots in 12A/I, weights, an unfinished shell ladle.
    - Mackay 1938's prose: kilns in Block 1 (the "Palace", room 33) and in 2/III and 9/II; copper ore pit in 1/I, room 51.
    - Marshall 1931 vol. II findspots.
  - Chanhu-daro: Mackay 1943 pp. 52-53 (OCR lines 3818-3878): bead-making, unfinished weights, unfinished seals and shell working by square, and the bead factory with furnace (215, 286, 287, square 9/D).
  - Lothal: Frenez & Tosi 2005 sealing contexts (W/W1/W2 = warehouse, O = outside).
- `assemblages.csv`: 369 units. Each row gives the crafts, the number of inscribed seals and of non-seal objects, the object types and the craft sources. This is the reusable deliverable.
- `linked_objects.csv`: 1,774 inscribed objects with their unit, crafts and Wells sign sequence.

## Pre-registered tests

| id | hypothesis | n | result | verdict |
|---|---|---|---|---|
| as_r1 | sign enriched in same craft context at 2 sites, non-seal | K = 49; 602 records | 0 replicated; power OR3 0.00 | inconclusive |
| as_g1 | global replication count, non-seal | 49 pairs | G = 0 vs 0.01, p = 1.0 | inconclusive |
| as_r2 | same, all objects | K = 193; 1,634 records | 0 replicated; nearest M197 WEIGHT; power OR3 ≤ 0.035 | inconclusive |
| as_g2 | global count, all objects | 193 pairs | G = 0 vs 0.07, p = 1.0 | inconclusive |
| as_x1 | (exploratory) share-based storage signal M1 | 1 pair | p 0.019 / 0.005, but Lothal side is 1 seal | dead lead |

## Caveats

- **Craft evidence is recorded selectively.** Vats lists illustrated or noteworthy objects; Mackay 1938's lists cover only illustrated objects. "No indicator" means "not recorded", not "no craft". Weights are so widely recorded at Harappa (23 of 41 non-seal squares) that WEIGHT tracks how much was dug, not trade.
- **Parsing is from OCR.** The Vats square regex takes the 350 characters before each square as the item description, so a few rows sit on the neighbouring item (spot-checked: the I13 row at OCR line 6556, the N10 row at line 12022). Mohenjo-daro street units and the HR/VS houses in Marshall vol. I were not coded, because vol. I (the architecture chapters) is not among the scans.
- **Unit mapping.** Harappa squares come from the CISI `room-grid` field (e.g. `-I13/7` gives I13) and Mohenjo-daro houses from `block-house` (e.g. `7IV`). Block 1/I is taken to be Mackay's "Palace"; this was not verified against the plan.
- **The frozen null does not correct for unit size.** A unit with many finds gets both more craft indicators and more texts. The exploratory share statistic corrects this, but it was not registered.
- **Repeated impressions.** One sealing per unit at Lothal let repeated impressions of one seal count many times. Merge by text before any rerun.

## What a person must look up (to make R7 testable)

1. **HARP trench craft areas at Harappa** (largest gain: about 700 inscribed tablets in Mound E/ET with trench and period but no craft coding). Sources:
   - Meadow & Kenoyer annual reports, 1986-2010;
   - Kenoyer 2005 on steatite and faience working in Mound E;
   - Miller 1999 (PhD thesis), kiln and pyrotechnic features by trench;
   - Kenoyer & Meadow 2010, CISI 3.1 pp. 423-441, lot list per H-number.

   For trenches 11, 10W/11, 54, 55, 7/8, 39N, 42 and 43, record whether shell, steatite or faience, agate bead, stoneware bangle or copper production debris was found, and in which lot or period. harappa.com is behind Cloudflare, so this needs a normal browser.
2. **Mohenjo-daro craft areas.** Two kinds of source give these:
   - Marshall 1931 vol. I (HR, VS, DK and L area chapters) and Mackay 1938 vol. II plate lists, both giving room-level findspots of unfinished beads, shell waste, crucibles and weights;
   - the Mohenjo-daro surface survey workshop maps (Pracchia, Tosi & Vidale 1985; Vidale 1989), to be matched against DK-G and HR blocks.
3. **Lothal.** Rao 1979/1985 locus tables for the bead factory (lower town) and the coppersmith's workshop, with the Lothal tags and pottery inscriptions found there. ICIT `area-section` gives only SRG numbers.
4. **Dholavira.** Bisht 2015 findspots of the inscribed tags (Middle and Lower Town grid) and the bead and shell workshop areas. ICIT gives grid strings, but no craft areas are published openly.
5. **Chanhu-daro.** Mackay 1943 catalogue findspots for the 54 seals and 15 other inscribed objects. Only 13 have a square in ICIT.

If items 1 and 3 were done, a non-seal test could cover Harappa (tablets) × Lothal (tags) × Chanhu-daro for BEAD and SHELL, the craft contexts that actually occur at several sites. Power would still need at least about 10 craft units with texts per site.

## Next experiments
- Rerun `test.py` with the size-conditioned share statistic as the registered null, with Lothal sealings merged by text, once item 1 is coded (new prereg).
- Freeze as a new-finds prediction (null): no sign appears at more than 2× its site share in craft-context finds at two sites.
