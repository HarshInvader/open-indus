# Blindness note

The workshop coding was built without seeing which signs any coded unit's objects carry.

## What I looked at

- Excavation-report OCR only, for the coding: Mackay 1938 vol. I, Marshall 1931 vol. II, Vats 1940, Mackay 1943 (all under `experiments/magnitude/raw/`).
- `experiments/assemblage/build_coding.py`, `craft_units.csv` (craft labels per unit, no signs), `RESULTS.md`, and the first 122 lines of `test.py` (the unit-key functions). I copied the unit-key logic and did not run `test.py`.
- The header line of `experiments/assemblage/assemblages.csv` and `linked_objects.csv` (column names only, printed with `head -1`). I did not read any row of `linked_objects.csv`.
- `sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json`, loaded in Python. I printed only the value counts of `site`, `area-section`, `block-house` and `room-grid`. `build_units.py` reads `seq` only to test that it is non-empty (`any(x > 0 ...)`), so counts match the assemblage linkage. It counts objects by record and never reads, prints or stores a sign value.

## What I did not look at

- No sign sequence for any unit, coded or not. No fish (or any other) sign frequency per unit or per site.
- `experiments/meaning_claims/` files (RESULTS.md, CATALOGUE.csv, counts.json) were not opened.
- `experiments/assemblage/linked_objects.csv` rows, `results.json`, `run.log`, `explore_size.*`.
- ICIT and M77 sign files, `corpus/` loaders.
- No statistic was computed that involves signs. `power.py` uses only an assumed 30% fish base rate and hypothetical 1.5x and 2x enrichments.

## Leaks to declare

- From the task brief I knew that 10 of 28 Chanhu-daro workshop objects carry fish. For that reason Chanhu-daro units are flagged `role=seen` and are left out of every count marked "new".
- The assemblage RESULTS.md names a few non-fish sign IDs (M197, M1, M343, M48) in weight and storage contexts. These are unrelated to this coding.
- Report passages I read now and then describe an inscribed object (for example Mackay's stoneware bangles "with pictographic characters", Vats's "unicorn seal with 3 pictograms"). No such passage was used to code a unit, and none of the qualifying evidence is an inscribed object.
- Coding decisions came before I saw the inscribed-object count of any unit. Counts were printed only after the evidence list was fixed. Two changes came after the first count printout, and neither used signs:
  1. Mackay's object list was found to start at OCR line 11503, not 11859. This changed only the listed-find proxy.
  2. The partly made shell bracelet (Bl. 1, court I) was moved from `DKG. (S)|1|-` to `DKG. (S)|1|I`, because Mackay's own list puts Court I and the Central Corridor under Block 1, House I (OCR lines 11508-11568). Under rule (b) this raised `DKG. (S)|1|I` from low to medium.

  The second change is a judgement made after counts were visible (the unit holds 26 inscribed objects), so a red team should check it.
