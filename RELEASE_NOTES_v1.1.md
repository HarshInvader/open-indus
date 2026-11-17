# Release notes, v1.1 (2026-11-15)

**In one line:** four more cycles of tests did not move any claim up the ladder. We now know more about what Indus seal texts are, but no sign has a meaning or a sound value, and the tests we can still run on the texts in hand have run out. Progress now depends on new data held by excavators and museums (ranked list at the end).

v1.1 adds cycles 7-10 (2026-11-14 to 11-15) to v1.0. Every test in it was pre-registered and hash-frozen before its outcome was computed, and every positive result was attacked by an independent red team. Where the red team disagreed, its verdict is the one reported here.

## What changed since v1.0

### New data: the 1930s excavation registers

The excavators of Mohenjo-daro, Harappa and Chanhu-daro printed seal-by-seal tables in their reports. Four of these reports are public domain on archive.org: Marshall 1931, Mackay 1938, Vats 1940 and Mackay 1943. We read their tables and linked each row to its text (`experiments/old_registers/`).

- 1,524 texts now have register data: Mohenjo-daro 924, Harappa 552, Chanhu-daro 48.
- New fields: depth to a tenth of a foot for 904 objects, dimensions for 912, the house and room where 640 Mohenjo-daro seals were found, and field numbers for about 1,570.
- The links were checked against the sign sequences: 364 of 490 linked pairs match well, against 21 of 1,984 random pairs.
- Marshall 1931 was later transcribed by hand; its depths match Mahadevan's levels in 450 of 450 checks.

A search of open-access journals and the Archaeological Survey of India's online reports found almost nothing usable: no new inscribed bangles, no new readable texts, and one firing stage on a mark that is not a script sign (`experiments/open_journals/`).

### A positional grammar, described but not validated

`docs/GRAMMAR.md` describes where signs sit in a seal text: an optional opener (10 signs, mainly M267, M391), an optional connective (M99, M123), a middle drawn from a large vocabulary (85 signs in the stable class), and a closer (7 signs, mainly the jar M342). `restore.py` suggests fillers for broken texts.

- On unseen texts the grammar beats position-only and shuffled baselines (5.79 vs 6.38 bits per sign).
- A plain two-sign model predicts better (5.49). The grammar is a compact description, not the best predictor.
- Gulf round seals fit it far worse than Indus seals (1.80 bits per sign, p = 0.0001), as expected if they were not written in the same system.
- On Ur III seal legends, used as a control with known structure, the same method finds "son of" but splits "servant of". So by its own pre-registered rule the grammar is not validated.

### What seal texts are

- **Almost every seal text is unique, and the supply never runs out.** At each site 93-97% of newly found seals carry a text never seen before.
- **The few repeats are mostly chance.** Short texts repeat about as often as the script's own sign-pair habits predict, wherever seals are found. The one repeated longer text beyond chance is a frame already known since Mahadevan 1977 (opener + M99 + a numeral + M162/M169).
- **No city has its own sign stock.** Mohenjo-daro and Harappa seals cannot be told apart from their signs (AUC 0.49). A stock large enough to cover 20% of a city's signs would have been caught 92% of the time. Smaller local differences are not excluded.
- **There are two open positions, not one.** New material appears at the start and in the middle of a text; the closer is the least open. That does not look like a single name plus a fixed title.
- **Every text has about one closer, whatever its length.** Short texts are cut-down versions of longer ones that keep the closer (51% of short texts sit inside a longer one, against 35.5% by chance).
- **Seals and sealings carry the same closers**, and the excavated seals are almost never the dies that made the excavated sealings (at most about 6%).

None of this says what the texts mean. It narrows what kind of thing they are: unique combinations drawn from one shared vocabulary across the civilisation.

### No household or office signature, in two cities

If seals carried a family or office mark, seals lost in the same house should share signs. They do not.

- **Mohenjo-daro** (Mackay 1938; 345 seals in 74 houses): seals from one house share an opener 4.0% of the time, against 3.0% for seals from other houses (p = 0.46). 0 of 8 tests significant.
- **Harappa** (Vats 1940; 287 text families in 46 grid squares): 1.7% against 1.4% (p = 0.56). 0 of 8.
- A mark carried by half the seals of a house would have been caught 90-100% of the time in both cities. Weaker marks are not excluded.
- Copies of the same text are not kept together either: they turn up in different houses and at different depths.

### One lead: ticked fish cluster in one part of Mohenjo-daro

The ticked fish (fish signs with corner ticks, which move to the closing slot; README #3) are unevenly spread across the building blocks of Mackay's excavation area (p = 0.0007). Block 12 holds 4 of the 21, all in one house; the two largest blocks hold 1 of 151 between them.

- The red team found it is not caused by depth, one carver, catalogue order or sign coding.
- It does not survive correction over every findspot test run (q = 0.11), and it does not show in the rest of Mohenjo-daro (p = 0.31).
- Marshall's 1931 seals could not test it: only 6 ticked-fish seals have a block, each in a different one (power 0).

Status: a frozen prediction (TF1 in `docs/PREDICTION_REGISTRY.md`), not a claim.

### Results reversed or withdrawn

Ten results from these cycles shrank or failed under the red team (`docs/NEGATIVE_ATLAS.md`, section 11, items 27-36). The main ones:

- **"A layer of short formulas shared across cities."** These were chance collisions of short texts.
- **"Small seals drop signs in a fixed order."** The pattern follows from one rule alone: keep the closer, drop the rest at random. 41 of the 138 "new" seals in the replication were old seals counted twice.
- **"Repeated longer texts are one owner's re-cut seals."** Withdrawn; their locality is undetermined.
- **"A new travelling numeral formula."** Real, but already known (the M162 count frame).
- **"Texts grow, never shrink."** Survives at a much smaller size (6 against 1.8 expected).
- **"Ticked fish cluster by block."** Weakened to a lead (above).

### Routes closed or found untestable

Seventeen new atlas entries (`docs/NEGATIVE_ATLAS.md`, section 10b). Most are untestable for lack of object-level data, not refuted:

| Route | Verdict | What blocks it |
|---|---|---|
| Cup sign M328 glossed by offering scenes | Untestable | Photos at about 100 ppi show no vessels |
| Oval sign as a bangle sign | Untestable | 0 bangles outside the data that suggested it |
| Pre- vs post-firing pottery marks | Underpowered (power 0.06) | Firing stage recorded for 36 of 650 vessels |
| Line breaks as phrase boundaries | Untestable | 74 two-line texts; many breaks are editorial |
| Signs on their own line as a class | Not supported | They are closers given their own line |
| Left-to-right texts as a class | Untestable | No record of how editors fixed direction |
| Depth chronology | Inconclusive | Broad strong change excluded; weak Harappa drift only |
| Seal texts as personal identifiers | Undecidable | Statistics cannot separate identifiers from labels once length is matched |

## Claim ladder

| Level | v1.0 | v1.1 |
|---|---|---|
| L0 structure | done | done; positional grammar written up (`docs/GRAMMAR.md`), not validated as a predictor |
| L1 function | largely done | largely done; adds "about one closer per text" and "short texts are abridgements" |
| L2 semantic field | open | open. Every attempt to tie a sign class to findspot, object, firing stage or scene was null, untestable or weakened. Ticked fish × block is the only lead |
| L3 denotation | open | open. The M328 offering-scene test could not be run |
| L4 sound | out of reach without a bilingual | unchanged |

The README's ranked findings (#1-#11) are unchanged.

## What would unlock progress, ranked

This order is the human-access priority set in cycle 7 (`docs/RESEARCH_STATE.md`, queue 0e) and kept since. Contacts and object lists are in `docs/HUMAN_LEADS.md`; email drafts (not sent) are in `docs/outreach/`.

1. **HARP context database (Kenoyer and Meadow, Harappa).** Lot, stratum, dimensions and masses for inscribed objects, plus the marked-sherd database (1,218 sherds with firing stage and vessel form). Unblocks the firing-stage test on its own, the bangle test (HARP bangle list), true contemporaneity for identifier tests, chronology at lot level, craft assemblage, and a ticked-fish replication at Harappa.
2. **Curator photos of the sealed Meluhha tablets.** CUSAS 40/2 1582 (Iraq Museum), Nisaba 15 0371 (Messina), Ur-Lamma's sealed receipts at Gu'abba, YBC 5447 as a reference case. The only route to a cuneiform anchor.
3. **CISI vol. 3** (the HARP-era Harappa objects). Roughly doubles the Harappa scene tablets, adds about 1,000 unicorn seals, and gives the lot list (pp. 423-441) for tablet-archive and chronology tests. The Fuls 2022-23 corpus and 2023 sign catalogue would serve the bangle, line-break and new-finds tests.
4. **High-resolution images of the scene tablets** M-478/479/480 B, H-177 B, H-180 B (≥ 600 dpi or RTI). Needed before the M328 offering-vessel test can run.
5. **Museum masses and per-object measurements** for about 40 objects of one class (tools, bangles, vessels). Unblocks the magnitude test; independent seal measurements would also re-test "one closer per text" outside the 1930s measurers.
6. **RTI of BM 120573 and Louvre Sb 9382.** A possible Meluhhan seal legend and a mixed Indus/Linear Elamite text.

Also listed in HUMAN_LEADS: Kalibangan excavation report Part I (pottery graffiti with firing stage; not online), clean findspots for Mohenjo-daro HR/VS seals (ticked-fish replication), and two-line seal texts recoded from photographs (line-break test).

## Registry and reproducibility

- **Predictions for future finds:** 38, up from 31. New: the bangle-oval rules (BO-H1 to H4), W621 on scene seals (W1), painted-pottery signs (FS1) and ticked fish by block (TF1). See `docs/PREDICTION_REGISTRY.md`, A4.
- **Preregistrations:** 55 files, all in `docs/prereg/HASHES.txt`. 50 match a hash line; 5 changed after hashing, 4 of them with a logged amendment (`signlist_robustness.md` has none).
- **Test ledger:** 842 rows across 64 areas, up from 654.
- **Reproducibility:** `docs/REPRO_REPORT.md` covers v1.0. The cycle 7-10 scripts were not part of that re-run.
- How to cite: `CITATION.cff` (version 1.1).
