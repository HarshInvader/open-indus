# Pre-registration: scene element x sign on narrative tablets and seals (Fable 5.2 plan 3, R3)

Registered 2026-11-15, BEFORE any scene code exists and BEFORE any scene code is joined with any text. Work dir `experiments/scene_text/`. SHA-256 of this file and of `s1_locate.py`, `s2_catalogue.py`, `s3_join.py` (once written, before it is run) go in `docs/prereg/HASHES.txt` (tag `scene_text`). `scene_codes.csv` is hashed (tag `scene_text_codes`) before `s3_join.py` runs.

## What the analyst saw before registering (declared)

- The analyst is NOT blind: while building the catalogue he printed the ICIT texts of the 71 objects whose ICIT symbol is Scene/Anth/T-A-T/T-M-T/Htgr, and knew from the literature/m328_measure that M-478/479/480 (Parpola: kneeling worshipper offering a pot to a tree, text with 4 + cup) and H-177 (text ends W033 W700) exist, and that H-180 shows a kneeling figure and a pot (text without W700). He also viewed CISI page 209 (vol 1) and one contact sheet of 12 random crops for crop QA.
- Therefore the analyst does NOT code scenes. Coding is done by independent sub-agent raters that see only anonymised face crops (random ids X####, no CISI number, no site, no label, no mention of the Indus or of writing systems' sign lists), under the fixed scheme below.
- Text base rates (no scene information): W700 (= M328, bridge) occurs on ~50% of distinct-text Harappa TAB:B objects, ~5% of Mohenjo-daro TAB:B, ~1% of MD TAB:C, <1% of seals.

## Consequence of the base rate for the lead's ">= 3x" criterion

At Harappa the base rate of W700 among moulded tablet types is about 0.5, so a rate ratio of 3 is arithmetically impossible there (maximum ~2). The effect-size criterion is therefore the Mantel-Haenszel odds ratio across strata (>= 3). The pooled rate ratio observed/expected is reported alongside.

## Catalogue and crops (done before registration, scripts frozen)

- `s1_locate.py`: tesseract OCR of every page of CISI vol 1 and vol 2 (pdfimages, ~100 ppi); printed labels ("H-180 B") parsed and assigned to the photo box directly above.
- `s2_catalogue.py`: candidate objects = (a) ICIT tablets with any non-plain picture code, seals/sealings/tags with a narrative-type code; (b) every object on a CISI TABLETS/SEALS page whose printed header names a narrative class (anthropomorph, tree, cult object, animal group, gharial, joined animals, snake). 551 candidates, 408 with a located face, 1,120 face crops in 94 contact sheets. Objects in CISI vol 3 (HARP finds H-1101+, M-2000+) have no photos here and are NOT coded (they include ICIT 'Scene' objects; reported as a coverage loss).

## Coding scheme (fixed; given verbatim to raters in `rater_instructions.md`)

Per crop: `content` in {script_only, blank_or_unreadable, single_animal, geometric, scene} and binary elements:
`human` (any human or human-like figure), `kneeling` (a kneeling, squatting-forward or bowing figure facing a tree, figure or object), `vessel_offered` (a pot/bowl/cup held, extended or placed before a figure or tree as part of the picture), `tree` (tree or branch as a picture element), `figure_in_tree` (figure standing inside a tree/arch of branches), `horned_figure` (human-like figure with horns or horned headdress), `seated_figure` (figure seated cross-legged / on a dais, 'yogi'), `procession_standard` (several figures in a row and/or a carried pole/standard/banner), `combat` (human grappling or fighting animals, e.g. holding two tigers), `animal_attack` (human spearing/attacking an animal, e.g. buffalo), `tiger`, `buffalo`, `gharial` (crocodile/long-snouted reptile), `fish`, `boat`, `snake`, `bird`, `cult_object` (stand/manger/standard-like object in front of an animal), `multiple_animals`, plus `confidence` 0-2. Raters are told to ignore rows of small schematic signs (writing) and to code a vessel only if it is part of the picture (held, offered, placed before a figure/tree), never an isolated U-shape inside a row of signs.

Two independent raters per crop (different model families: Opus, Sonnet), sheets in different order. Inter-rater agreement (Cohen kappa per element) is reported.

**Consensus (primary):** an element is present on a crop if both raters mark it. **Lenient (secondary):** either rater. Object-level code = OR over its crops. Scene object = any crop with content=scene by consensus (lenient for secondary).

**Offering scene (primary hypothesis predictor):** `vessel_offered` OR `kneeling` (consensus).

## Units

- Object = ICIT record-id prefix (all sides). Text of object = all its sides.
- **Moulded type** = connected component of objects with the same site and ICIT type whose break-free texts are identical or differ by edit distance <= 1 (on the concatenated side texts, '#' removed) or one is contained in the other (>= 3 signs). Copies count once. A type's scene code = OR over its coded copies.
- Objects whose ICIT symbol is a plain single-animal/None code are NOT candidates and count as offering = 0 / element = 0 without coding. Candidate objects that could not be coded (no photo located, vol 3) are EXCLUDED from both groups (their type is dropped unless another copy was coded).

## Primary hypothesis H1 (single confirmatory test)

M328 (W700) is enriched on moulded tablets (ICIT TAB:B) whose picture shows an offering/vessel scene, against other TAB:B types of the same site.
- Population: TAB:B types, strata = site (period is '-' for almost all vol 1-2 objects, so period cannot be a stratum; phase is reported where known).
- **Discovery objects excluded:** types containing M-478, M-479, M-480 (Parpola's generating example) are removed from the primary test. The inclusive version is reported as secondary H1b.
- Statistic: number of offering types carrying W700 on any side. Null: offering labels permuted among types within stratum, 100,000 permutations; one-sided p.
- **PASS** if p < 0.05 AND Mantel-Haenszel OR >= 3. **FAIL** if p >= 0.05. If p < 0.05 but OR < 3: "enriched, below the effect bar".
- Power: computed after scene coding but before the join, by planting W700 on offering types at OR = 3 and OR = 5 given the observed number of offering types per stratum (1,000 simulations). If power at OR = 3 < 0.5, a FAIL is reported as "inconclusive (underpowered)".
- Shape leg (vessel looks like M328): no new attempt; m328_measure showed ~100 ppi photos cannot settle shape. Reported as not tested.

## Exploratory (BH-FDR, reported as leads only)

For every element with >= 3 positive types (consensus) and every Wells sign occurring in >= 3 types of the population, enrichment of the sign on element-positive types vs element-negative types. Population for exploratory tests: all coded or plain-coded types of every object type (tablets, seals, sealings), strata = site x ICIT type. Statistic: count of element types with the sign; null: element labels permuted within stratum (20,000x); one-sided p; BH over all element x sign tests. Report for each element the top 3 signs by p with observed/expected. Same with lenient codes as a sensitivity check.

## What would count

- H1 PASS (plus a later shape confirmation on hi-res photos) would make "M328 = offering vessel" an L3 candidate. H1 FAIL at adequate power argues that the cup sign is not glossed by vessel scenes. An exploratory hit is a lead only, to be frozen as a prediction for CISI vol 3 objects.

## Amendment A1 (2026-11-15, after hashing codes, before any join output was seen)

The first run of `s3_join.py` was stopped after 10 minutes with no output printed (Python permutation loops too slow). `strat_perm` now draws the within-stratum permutation null as a sum of hypergeometric variables, which is the exact same distribution. No other change. Both hashes are in HASHES.txt.

## Amendment A2 (2026-11-15, AFTER the A1 join output was seen; logged honestly)

Bug: the pre-registered moulded-type rule (single linkage on edit distance <= 1 or containment) chained unrelated short texts: one Mohenjo-daro seal "type" held 426 objects, one Harappa TAB:B "type" 189. The exploratory top hits were driven by these mega-types. Fix: a type = identical break-free text (all sides) within site x ICIT type; an incomplete object joins a complete type only if its text is contained in exactly one complete type's text. The A1 output is kept (`join_results_A1_chained.json`, `s3_A1_chained.log`). The primary H1 outcome was the same under A1 (1 offering type, no cup, power 0), so the fix cannot have been chosen to favour H1. Exploratory results are reported from A2 and the A1 numbers are mentioned.
