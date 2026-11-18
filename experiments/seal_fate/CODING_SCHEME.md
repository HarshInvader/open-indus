# Fate coding scheme (written 2026-11-18, before any coding)

Unit: one register object (Vats 1940 EH serial at Harappa; Mackay 1938 FEM serial at Mohenjo-daro).
Input: `remarks.csv` only (built by `extract.py`). It holds the excavator's words about the object and its findspot, with every count of pictograms masked as `[k]`. The coder never opens M77, ICIT or any sign list. `code.py` imports nothing from `corpus/` or `data/`.

Each code is 1 (stated), 0 (codable and not stated), or blank (cannot be coded from this source). Text the coder may use: the entry text, the findspot / level / dims fields, and the section header (mound, area, stratum).

| Code | 1 when the remark says | Notes |
|---|---|---|
| BROKEN | broken, fragment, fragmentary, bit of, piece of, part (missing / broken off / lost), chipped, damaged, split, cracked, "only [k] ... surviving / left / remaining", "extant", "trace of" | FEM: a `?` in the dims cell (a side could not be measured) is coded BROKEN_PROXY = 1 instead, never BROKEN. |
| CUT | cut / sawn / ground down / deliberately broken, of the object itself (not "cut" as in "well cut" or "seal-cutter") | Expected near 0. |
| BURNT | burnt, burned, scorched, calcined, blackened by fire, of the object | "burnt steatite", "burnt clay", "burnt brick" are materials or architecture, not fate: 0. |
| WORN | worn, rubbed, defaced, effaced, blurred, indistinct, faint, weathered, corroded | |
| REUSED | re-used, re-cut, recut, re-engraved, inscription removed, converted | |
| UNFINISHED | unfinished, in (the) process of manufacture, blank, uncut | |
| OPEN | findspot is a street, lane, alley, "between blocks", open courtyard outside a house, drain, well, gateway, city wall | FEM findspot field; Vats entry text. |
| DRAIN_WELL_GATE | drain, well, gateway, gate, city / fortification wall | subset flag of OPEN |
| ROOM | findspot names a house and a room (FEM), or the entry says "room" / "chamber" / "house" | |
| BURIAL | section header is a cemetery (Area H prehistoric cemetery, R37, Cemetery H) or remark says grave, burial, skeleton, interment | |
| HOARD | found with / together with other objects named in the same group, "group of antiquities", "hoard", "in a jar", "from the same mould were also found" | |
| SURFACE | level "surface", or depth below surface <= 1 ft 0 in (Vats "b.s."), or FEM level_raw contains "Surface" | Blank if no level. |

Rules for doubtful cases:
- A word that describes the motif (e.g. "the animal is broken off") counts as BROKEN: it means the object is broken.
- "Slightly broken", "partly broken" = BROKEN.
- Sealings and tablets are coded the same way as seals; object type is kept as a stratum, not a code.
- If an entry describes several objects (a group), each seal plate number in it gets the group's HOARD code; condition words are attached to the plate number they sit next to (the run-together split in `extract.py`).

Inter-coder consistency: after the pre-registration is hashed and before outcomes are computed, the author re-codes a 20% random sample by hand (seed 7, items in a shuffled order, codes taken in the reverse of the table order), without looking at `code.py` output. Agreement = Cohen's kappa per code against `code.py`. Codes with kappa < 0.6 are reported but their tests are marked unreliable.
