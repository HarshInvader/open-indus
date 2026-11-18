# Indus data, in one place

Every dataset this project uses about the Indus (Harappan) civilisation and its script, listed in one catalogue: what it is, where it comes from, its terms, and how to get it.

Some sources can't be copied here: their owners have not given terms that allow it (see `../LICENSING.md`). For those, this folder gives the exact source and a script that rebuilds them on your machine. Everything the project made itself is included.

## What is here

| Path | What |
|---|---|
| `catalog.csv` | All 94 sources: 33 included here, 53 public and fetchable, 8 reference-only (in copyright or no terms stated). Columns: `id, title, kind, tier, origin, terms, local, fetch, included_here`. |
| `open/` | 33 tables made by this project (CC BY 4.0). `open/MANIFEST.csv` says where each came from. |
| `splits/` | The frozen held-out split that every result uses, as M77 text numbers (`text_no.side`), with its sha256. |
| `fetch.py` | Rebuilds the rest locally (see below). |
| `build.py` | Regenerates `catalog.csv` and `open/` from the experiments. |

## Get everything

```bash
python3 datasets/fetch.py list             # the catalogue, by tier
python3 datasets/fetch.py corpus           # both sign corpora at the exact commits we used, then data/ and the frozen splits
python3 datasets/fetch.py reports          # OCR text of all 39 archive.org copies of the 1931-1943 excavation reports
python3 datasets/fetch.py reports --pdf    # the same, plus one PDF scan per item (several GB)
```

`corpus` builds `data/` with `corpus/build.py`: 3,573 lines of text from Mahadevan 1977 and 5,679 inscriptions from ICIT, with site, object type and direction. It then restores the frozen split and checks its hash, so your numbers match ours. Downloads go to `sources/`, `data/` and `datasets/local/`, which git ignores.

## The included tables

| File | Rows | What |
|---|---|---|
| `registers_1931_1940.csv` | 1811 | Object registers of the 1931-1943 excavation reports (Marshall, Mackay, Vats), OCR transcribed and repaired: object no., findspot, depth, size, material, M77 link. |
| `register_mackay1938_seals.csv` | 695 | Mackay 1938 (Further Excavations at Mohenjo-daro) seal register: size, material, block/house/room, level. |
| `register_vats1940_seals.csv` | 677 | Vats 1940 (Excavations at Harappa) seal register: size, mound, depth, find no. |
| `register_marshall1931_seals.csv` | 522 | Marshall 1931 (Mohenjo-daro and the Indus Civilization) seal register. |
| `register_mackay1943_chanhudaro_seals.csv` | 91 | Mackay 1943 (Chanhu-daro Excavations) seal list. |
| `findspots_mohenjodaro.csv` | 695 | Mohenjo-daro seals: parsed block/house/room and depth, linked to M77 text numbers. |
| `findspots_harappa.csv` | 639 | Harappa seals (Vats 1940): mound, square, depth, linked to M77/ICIT/CISI. |
| `findspots_marshall_prose.csv` | 86 | Findspots stated in the prose of Marshall 1931. |
| `craft_units.csv` | 301 | Craft-activity evidence per excavation unit (Harappa, Mohenjo-daro, Lothal, Dholavira) with sources. |
| `assemblages.csv` | 369 | Per excavation unit: crafts present and counts of inscribed objects. |
| `assemblage_linked_objects.csv` | 1774 | Inscribed objects linked to excavation units. |
| `seal_sizes_carver_clusters.csv` | 499 | Seal widths (mm) and photo-based carver clusters, by CISI/ICIT id. |
| `harappa_tablets.csv` | 1083 | Harappa miniature tablets: type, material, mound, trench, HARP period, mould copy groups. |
| `copper_tablet_types.csv` | 37 | Mohenjo-daro copper tablet types (text + picture), counts in M77 and ICIT. |
| `copper_tablets.csv` | 325 | Each copper tablet with its type, picture and sign face. |
| `vessel_marks.csv` | 650 | Inscribed and marked vessels: pre- or post-firing, vessel form and size, sources incl. Kenoyer 2021. |
| `potters_marks.csv` | 233 | Potter's marks from early and Mature Harappan sites (Rehman Dheri, Balakot, Kalibangan, Nausharo, Farmana, Gumla, Harappa) with firing stage and vessel type. |
| `sealings.csv` | 238 | Clay sealings (Lothal and others): number of impressions, back type (door, jar, bundle), context. |
| `inscribed_object_measurements.csv` | 26 | Masses and lengths of inscribed tools and objects from excavation reports. |
| `indus_objects_abroad.csv` | 34 | Indus-related inscribed objects found outside South Asia (Gulf, Mesopotamia, Iran), with context and publication. |
| `foreign_seal_texts.csv` | 54 | Texts of Indus-sign seals found abroad, with findspot, shape, animal and date. |
| `meluhha_cuneiform_mentions.csv` | 46 | Meluhha (the Indus region) in cuneiform texts: persons, goods, places, with text ids. |
| `meluhha_foreign_objects.csv` | 23 | Indus objects abroad matched to cuneiform evidence from the same site and period. |
| `meluhha_tablet_seal_candidates.csv` | 15 | Sealed cuneiform tablets naming Meluhha that need re-imaging (CDLI P-numbers). |
| `new_finds_post2010.csv` | 28 | Inscribed objects published after 2010 that are not in the corpora, with our readings. |
| `new_finds_open_journals.csv` | 22 | More new inscribed objects from open-access journals. |
| `open_journals_context.csv` | 34 | Excavation context for inscribed objects in open-access reports. |
| `open_journals_pottery_marks.csv` | 9 | Pottery marks from open-access reports. |
| `tamil_nadu_sherds_graffiti_and_brahmi.csv` | 21 | Tamil Nadu sherds carrying both a graffiti mark and a Tamil-Brahmi text (Rajan & Sivanantham 2026). |
| `sign_statistics_m77.csv` | 417 | Per sign (Mahadevan numbers): frequency and share of initial, medial, final and standalone positions. |
| `sign_positional_classes.csv` | 369 | Per sign: positional class (opener, connective, medial, closer...) with confidence. |
| `sign_decompositions.csv` | 145 | Compound signs split into base sign + modifier. |
| `numeral_signs.csv` | 80 | Numeral signs in M77 and ICIT: value and layout. |

**Sign texts.** Tables longer than 60 rows have no column of whole sign texts. They keep the catalogue numbers instead (M77 `text_no`, ICIT id, CISI number), so you can join them to `data/` after `fetch.py corpus`. The short tables (objects found abroad, new finds) keep their texts as quotations. `open/MANIFEST.csv` lists every removed column.

## Reference-only

These need a library or the holder's permission:
- CISI photographs, vols. 1-3. In copyright.
- harappa.com / HARP images. Permission needed.
- Mahadevan's sign drawings. No terms stated.
- Dholavira museum photographs.
- Jalalabad, Laursen 2010 and the BDTNS pages.

If you hold rights to any of these and can open them, please get in touch.

## Missing, and wanted

The most useful data that is not public anywhere:
- the HARP excavation database (lots, strata, masses);
- the Kenoyer & Meadow marked-sherd database;
- CISI vol. 3;
- high-resolution images of the Harappa offering-scene tablets;
- re-imaging of sealed cuneiform tablets that mention Meluhha.

`../docs/HUMAN_LEADS.md` has the full list.
