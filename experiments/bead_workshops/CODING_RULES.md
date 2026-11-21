# Coding rules: bead, lapidary, shell, faience and jeweller workshop units

Written 2026-11-21, before any unit was coded. Purpose: a sign-blind list of findspot units that show ornament-production evidence, for a later test of meaning-claims rule 1 (Mukhopadhyay 2025: fish signs mean gems or beads). This file sets the rules only. No test is run here.

## Sources (all already in the repo, read-only)

| site | source | file |
|---|---|---|
| Mohenjo-daro, DK-G area | Mackay 1938, *Further Excavations at Mohenjo-daro*, vol. I (text) | `experiments/magnitude/raw/mackay1938_v1/ocr.txt` |
| Mohenjo-daro, HR, VS, DK A-E | Marshall 1931, *Mohenjo-daro and the Indus Civilization*, vol. II | `experiments/magnitude/raw/marshall1931_v2/*_djvu.txt` |
| Harappa | Vats 1940, *Excavations at Harappa* | `experiments/magnitude/raw/vats1940_v1/ocr.txt` |
| Chanhu-daro | Mackay 1943 | `experiments/magnitude/raw/mackay1943/ocr.txt` |
| Lothal | Frenez & Tosi 2005 sealing contexts | `sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json` |

Marshall 1931 vol. I (the HR, VS and DK area chapters) and Rao's Lothal reports are not in the repo. Units that only those volumes describe cannot be coded.

## What counts as a unit

The smallest findspot that the inscribed-object corpus (`merged-corpus-reading-order.json`, fields `area-section`, `block-house`, `room-grid`) can also resolve:

- Mohenjo-daro: area + block + house, keyed exactly as `experiments/assemblage/test.py::md_unit` does (`DKG. (S)|1|I`, `HRB|2|VIII`, `DKC|16|-`). A room is recorded in the evidence but the unit is the house, because the corpus has no room for most objects. If the report gives no house, the house is `-`.
- Harappa: Vats grid square without the sub-square (`J12`).
- Chanhu-daro: square (`9/D`).
- Lothal: none possible (see RESULTS.md).

Streets, lanes and trenches without a house are recorded only if the report gives no better unit. They are flagged `joinable=no` when the corpus cannot resolve them.

## Production indicators (what qualifies)

A unit is coded only from report text, for these crafts:

| craft code | qualifying evidence |
|---|---|
| BEAD | unfinished, unbored or partly bored beads; bead blanks or roughouts; stone bead drills; carnelian/agate chips, flakes or nodules described as waste or raw stock; a bead-making kiln or "bead factory" |
| LAPIDARY | unfinished stone ornaments other than beads (pendants, spacers, inlay) of agate, jasper, carnelian, steatite, lapis; a jeweller's or lapidary's tool explicitly identified by the author |
| SHELL | shell cores, columella, cut-shell waste, partly made bangles, ladles or inlay |
| FAIENCE | kilns or furnaces the author ties to glazing or faience; frit or glaze-paste slabs; unfired or wasted faience |
| JEWELLER | a hoard of precious-metal ornaments that the author describes as containing scrap, lump or cut metal or waste, or attributes to a goldsmith, jeweller or dealer |
| JEWEL_HOARD | a hoard of finished jewellery with no working material (recorded, but not a workshop) |

Not qualifying: finished beads or ornaments alone; flint cores and blades (household use per Marshall); weights (coded already as WEIGHT in `experiments/assemblage`); pottery kilns; copper smelting alone; unfinished seals (coded as SEALCUT in `experiments/assemblage`; recorded here only as a co-occurring note).

## Confidence

- **high**: the author calls the unit a workshop, shop, factory or bead-making area for one of the crafts above, AND at least two kinds of production debris or tools are listed there.
- **medium**: either (a) a JEWELLER hoard with working material, or (b) two or more independent qualifying finds of the target crafts in the same house-level unit, or (c) a kiln the author ties specifically to glazing.
- **low**: a single unfinished bead or ornament, a single tool, a speculative kiln use (author lists glazing as one of several possibilities), or any JEWEL_HOARD. Also any unit with no house subdivision (a whole block or a whole street), whatever the evidence, unless the author names a workshop there.

The later test should use high + medium as the primary set and add low as a sensitivity check. This choice is fixed now, before counts are seen.

## Inscribed-object counts and find density

For each coded unit, and for every other unit at the same site, the build script records:

- `n_inscribed`: corpus records mapped to the unit whose sign sequence is non-empty, counted by object ID (cisi). The sequence is tested only for length > 0; its signs are never read. Split into `n_seal` and `n_nonseal` by the corpus `type` field.
- `n_inscribed_block`: the same count over the whole block (Mohenjo-daro only), because many corpus records carry a block but no house.
- `n_listed_finds`: a find-density proxy from the same report: Mackay 1938 object-list entries for that block and house (DK-G); Marshall vol. II findspot citations of that house; Vats 1940 item citations of that square. This is a count of published finds, not of all finds.

## Blindness

The coder does not open any file that holds sign sequences joined to findspots (`experiments/assemblage/linked_objects.csv`, `seq` contents of any corpus, any meaning-claims count file) and does not run any statistic involving signs. See BLINDNESS.md.

## Chanhu-daro

Chanhu-daro units are coded for completeness but flagged `role=seen`: their fish counts (10 of 28 workshop objects) were seen before this coding, so they cannot confirm the rule.
