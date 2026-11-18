# Harappa.com collection results

Collection audit: 2026-11-17 America/New_York (last network requests 2026-11-18 UTC). This is a source collection, not an interpretation or a comparison with M328. No corpus or other experiment files were intentionally changed; no commit was made.

## Status and counts

| Need | Status | Collected | Remaining limitation |
| --- | --- | --- | --- |
| 1. Kneeling/vessel tablet photographs | **Partial** | All **5 requested CISI faces** cropped at native resolution; **1 caption-identified related H95-2487 photograph**; **21 face measurements** total, including related/excluded leads | No resolution upgrade for the five target faces. H95-2487 is not a confirmed offering-vessel target; the proposed H-1975 cross-reference remains provisional. |
| 2. Stoneware bangles | **Partial** | **5 illustrated inscription instances** with individual crops; **7 existing Harappa ICIT records** audited | **0 confirmed additional texts**, **0 individual inner diameters**; target >=19 not reached. Anonymous illustration instances may duplicate one another or ICIT objects. |
| 3. Marked/graffiti sherds | **Partial** | Phase counts covering **1,218 sherds**; firing stages for **247 Period 1–2 sherds**; **8 captioned vessel-form examples** | No per-sherd register or complete pre/post-firing × vessel-form data for all 1,218. |
| 4. Recent inscribed-object photographs | **Partial** | **16 photographic object/illustration rows**: **5** with post-2018 source-year evidence/intervals and **11** undated candidates | **0 independently established exact website-post years**. Counts are records, not guaranteed distinct objects or new discoveries. |

The machine-readable collection is [SOURCES.csv](SOURCES.csv). Paths in its `local_file` column are relative to this folder. Each row includes the exact working asset URL; contextual page URLs are in the notes or `recent_objects.csv`. [asset_manifest.csv](asset_manifest.csv) hashes the local evidence and derivatives. [document.py](document.py) regenerates tables/crops without making network requests.

## 1. Requested faces and native pixels

Bounding boxes use original raster pixels, x0/y0 inclusive and x1/y1 exclusive. Widths are approximate tablet-face extents (typically +/-5 px; irregular larger faces +/-10), not physical dimensions or measurements of the depicted vessel. Crops have no resampling or enhancement. Page-render dimensions are never used as evidence of photograph resolution.

| Face | Native source page image | Approximate px across face | Native crop |
| --- | --- | --- | --- |
| M-478 B | 796 × 1,165 | **311** | [M-478_B.png](evidence/crops/M-478_B.png) |
| M-479 B | 796 × 1,165 | **304** | [M-479_B.png](evidence/crops/M-479_B.png) |
| M-480 B | 796 × 1,165 | **318** | [M-480_B.png](evidence/crops/M-480_B.png) |
| H-177 B | 830 × 1,149 | **201** | [H-177_B.png](evidence/crops/H-177_B.png) |
| H-180 B | 830 × 1,149 | **371** | [H-180_B.png](evidence/crops/H-180_B.png) |
| H95-2487/4466-01, related lead | 935 × 410 | **875** | [H95-2487.png](evidence/crops/H95-2487.png) |

The first three are CISI 1 printed p.115 / PDF p.151; the two Harappa faces are printed p.209 / PDF p.245. Existing source reused: <https://rarebooksocietyofindia.org/book_archive/CorpusVol1.pdf> (HTTP 200 in the request log).

A newly checked government mirror, <https://ignca.gov.in/Asi_data/76884.pdf>, returned **200**, but gives **the same native target image bytes and dimensions**. It has 862 pages, repeating the same 431-page scan: target images on PDF pp.151/245 repeat on pp.582/676. It provides no resolution improvement. This alternative was fetched to check the unresolved resolution need; it is not another independent photographic source.

**Correction to the 2,184 × 662 lead:** In Kenoyer's *Master of Animals* paper, printed p.50 / PDF p.16, **Figure 11** is the 935 × 410 photograph captioned “Horned deity and ‘temple,’ Harappa (H95-2487/4466-01).” Its PDF image xref is 107. **Figure 12**, xref 114, is the 2,184 × 662 composite of drawings of other objects: Mehrgarh MR-17, Mohenjo-daro M-312, and a Banawali scene. It is **not** the H95-2487 photo. Both the native photograph and the excluded drawings are preserved under `evidence/crops/`; the full page is [master_p16.png](evidence/crops/master_p16.png).

Working paper: <https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Master%20of%20Animals.pdf>. A line drawing of H95-2487 also occurs as Figure 9.10 in the already saved 1997 paper (PDF p.18); that table explicitly pairs the accession with lot 4466-01. It supplies no CISI H-1975 number. Therefore the user-supplied local cross-reference is retained as provisional, not silently promoted to a verified identity.

[image_measurements.json](evidence/image_measurements.json) and SOURCES provide the remaining related slide measurements. Examples include the 279-px seated-scene face in `harappa-molded-tablets.jpg`, and captioned narrative tablets H95-2486 and H2001-5075. These are leads, **not confirmations of the requested offering scene**. A vertically displayed tablet has its stored horizontal extent reported; the long axis is also noted where relevant.

ICIT's literal `symbol == Scene` subset at H-1101+ / M-2000+ contains **10 side records for 7 CISI ids**: H-1144, H-1774, H-1968, H-1975, H-1976, H-2007, M-2033. Exact metadata saved in [icit_scene_candidates.json](evidence/icit_scene_candidates.json). No additional photo-to-CISI-id join was independently established. This filter is a metadata candidate list, not an exhaustive visual classification of all tablet iconography.

## 2. Bangles: source audit and missing data

[bangles.csv](bangles.csv) has **12 rows**: seven known ICIT baseline records plus five source-illustration instances. It must **not** be counted as 12 distinct bangles or 12 newly recovered texts. Unknown values are blank, and unknown image-to-ICIT matches are `unsure`.

The supplied `stoneware_bangles.pdf` is **Massimo Vidale's** *Stoneware Industry of the Indus Civilization: An Evolutionary Dead-End in the History of Ceramic Technology*, rather than a Kenoyer catalogue of 19 inscriptions. It supplies two usable individual inscription references:

- PDF p.6, Fig.3: Mohenjo-daro fragment, caption reports **5 signs**, photograph negative **14756/27**; [crop](evidence/crops/Vidale-fig3-14756_27.png).
- PDF p.7, Fig.4: Mohenjo-daro fragment, caption reports **2 signs**, photograph negative **14575/12**; [crop](evidence/crops/Vidale-fig4-14575_12.png).

These captions do not provide sign-number transcriptions or inner diameters. The crops retain the original scale/caption where present; no diameter was inferred from a fragment or from a reproduced scale.

Kenoyer's *Painted Indus Script on Ceramics and Steatite* (Ancient Pakistan XXXII, **2021**, printed/PDF p.7, Fig.4) adds **three illustration references**: two Mohenjo-daro photographs and one Harappa drawing. Their identifiers are local figure labels, not original museum identifiers. Figures 4.1 and 4.2 explicitly say “not to scale”; Fig.4.3 is a drawing with a scale, not a photograph. These three may overlap the Vidale images or previously catalogued objects; none is declared new to ICIT. Sign readings have not been invented from the images.

Working sources:

- <https://www.harappa.com/sites/default/files/pdf/stoneware_bangles.pdf>
- <http://ojs.uop.edu.pk/ancientpakistan/article/download/580/528> — actual saved PDF `raw/580-Article Text-993-1-10-20220407.pdf`; successful **HTTP 200**. The corresponding HTTPS attempts timed out; this public HTTP link worked without authentication.
- <https://www.harappa.com/content/painted-indus-script-ceramics-and-steatite-new-insights-indus-script-calligraphy-and> — captioned composite `raw/painted-script.jpg` is higher resolution than the PDF's small Figure 4 raster.
- <https://www.harappa.com/slide/stoneware-bangle> — quotes Kenoyer, *Ancient Cities*, pp.145–146, describing **5.5–6 cm interior diameter (55–60 mm)** for the class. That is **not** an individual measurement and has not been copied into per-bangle diameter cells.

ICIT audit: `corpus/load.py:icit_texts()` reads `data/icit_texts.jsonl`. A literal case-insensitive search for `bangle` in the type returns zero because the actual code is **BNGL**. For site Harappa, BNGL yields **7 records**: H-2578, H-2574, H-2576, H-2575, ICIT 820.1 with no CISI number, H-1009, H-1010. Only two explicitly list material Stoneware; the others are clay or unspecified. Their exact supplied transcriptions are preserved as the **existing baseline**, without re-reading signs. Snapshot: [icit_harappa_bangles.json](evidence/icit_harappa_bangles.json).

**What blocks the target:** the checked public files do not expose 19 object-level text/diameter pairs or reliable identities for the five illustration instances. The Dales ceramics chapter (printed pp.67–68 / PDF pp.9–10) discusses stoneware technology and chemical characterization, not such a catalogue. The bibliography points to Franke-Vogt, “Inscribed Bangles: An Inquiry into Their Relevance” (1989), pp.237–246, and related workshop studies; a freely accessible primary catalogue with the required fields was not located. The two Smithsonian repository URLs already attempted returned **403**; these are retained as access failures, with no bypass. Neither failure establishes that the requested 19 records exist at those endpoints.

## 3. Sherds: what the 1,218 total actually supplies

The exact 1,218 tally is in **Kenoyer 2020**, *The Origin and Development of the Indus Script*, printed p.227 (sampling explanation) and p.230 / PDF p.14, **Tables 3–4**. It refers to pottery studied during **1986–2003**. It is not a 1,218-row table in the Kenoyer–Meadow 2010 introduction.

- [sherd_phase_counts.csv](sherd_phase_counts.csv): Period 1 Ravi **23**; 1/2 **7**; Period 2 Kot Diji **224**; 2/3 **19**; Period 3 Harappa **941**; Period 4/5 Late Harappa **4**; total **1,218**. Percentages are transcribed as printed.
- [sherd_firing_counts.csv](sherd_firing_counts.csv): Ravi **7 pre / 16 post**; Kot Diji **49 pre / 175 post**. Thus **247** early-phase sherds have a published stage split (**56 pre / 191 post**). Do not extend these proportions to all phases.
- [marked_sherds.csv](marked_sherds.csv): **8** Harappa vessels in Kenoyer 2021 p.6, Fig.3.1–8, with captioned object ids, forms, and stage/location. Seven are post-firing only; H95-2662/6640-501 explicitly has **both** post-firing graffiti and pre-firing potter's marks. Forms include black-slipped jars, a large red-slipped black-band jar, and a plain globular jar. This is an illustrative sample; it has not been joined to individual members of the 1,218 tally.

Evidence: [Tables 3–4 page](evidence/crops/sherd_tables3_4_p230.png), [eight-vessel figure](evidence/crops/painted2021_fig3_sherds.png).

Working URLs:

- <https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script.pdf>
- <https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf>
- <https://www.harappa.com/sites/default/files/pdf/Harappa1986-90_05_Dales-Ceramics.pdf>

The 2010 text distinguishes pre-firing marks from post-manufacture graffiti (PDF pp.6–8; footnote 7) and describes pre-firing stamped **pointed-base goblets**, including H-1081/H-1082 (PDF p.10 / printed li). The Dales ceramics chapter reviews production and forms but supplies neither the later 1,218 tally nor a comprehensive stage-by-form register. **The missing register/cross-tab is a publication/data gap in the checked sources, not an HTTP failure.**

## 4. Inscribed objects on recent pages

[recent_objects.csv](recent_objects.csv) records **site, object, year or interval, basis for the year, URL, local photograph and dimensions**. Five rows have post-2018 source-year evidence, but **no exact website post date**:

- **Ganweriwala clay tablet**: page describes and illustrates Masih's contribution to *Walking with the Unicorn* (**2018**). Recorded interval **2018–2026**, not a claimed 2018 post date. <https://www.harappa.com/blog/glimpses-ganweriwala>; `raw/ganweriwala-3.jpg`, 800 × 903.
- **Umma Indus sealing**, now Ashmolean: page cites *Save Mohenjo Daro!* (**2022**). Interval **2022–2026**. <https://www.harappa.com/blog/indus-seal-impression-umma-mesopotamia>; `raw/umma-seal-impression.jpg`, 1,000 × 826. Umma is reported provenance, not a newly excavated Indus-site find.
- **Two Mohenjo-daro stoneware bangle photographs** and **one Mohenjo-daro gold pendant photograph**: Kenoyer paper published **2021**, as explicitly identified by the Harappa page. Interval **2021–2026**; corresponding figure crops in `evidence/crops/`. <https://www.harappa.com/content/painted-indus-script-ceramics-and-steatite-new-insights-indus-script-calligraphy-and>. The Harappa bangle in Fig.4.3 is excluded here because it is drawing-only.

The **11 undated candidates** have legible photographic inscriptions but unverified since-2018 dating: four Mohenjo-daro seals from “Four Seals Up Close,” one Chanhu-daro seal photographed at MFA Boston, one featured Mohenjo-daro seal in the interregional-connections article, and five caption-identified Bagasra seals (BSR 7368, 8288, 7197, 6719, 6952). Museum/CISI identity is not inferred where the page omits it. These rows are explicitly marked candidate-only.

Working contextual URLs for those candidates:

- <https://www.harappa.com/blog/four-seals-close>
- <https://www.harappa.com/blog/toponym-chanhu-daro>
- <https://www.harappa.com/content/mohenjo-daro-and-interregional-connections-indus-civilization-evidence-inscribed-seals>
- <https://www.harappa.com/content/inscribed-unicorn-seals-bagasra-gujarat-comparative-analysis-morphology-carving-styles-and>

The saved HTML exposes no post-date/time metadata for these pages. Current copyright years, `Last-Modified` headers, discovery years, source-paper years and apparent chronological blog ordering were **not substituted for exact post dates**. *Happy New Year 2022* was checked because it supplies an explicit year, but its seal image is a modern **graphic**, not a photograph; excluded. Archive CDX dating had already timed out. This is a documented sample, not a complete census of every object posted since 2018.

## Image rights and access evidence

Working policy page: <https://www.harappa.com/indus-image-rights>; saved [indus-image-rights.html](evidence/indus-image-rights.html), **HTTP 200**. The site says it represents commercial rights to its images; prices vary by commercial/non-profit client and use; **“Non-commercial scholarly works are usually free”**; inquiries should be made through its contact page. This is **not** a blanket Creative Commons/public-domain grant or an unconditional permission to redistribute the saved photographs. PDF publisher/author and photographed-object owner rights can also apply. CISI 1 PDF p.6 specifically credits copyright 1987 to Academia Scientiarum Fennica for the volume and original-object owners for photographs; page preserved as `evidence/crops/cisi_front_p6.png`.

[requests.jsonl](evidence/requests.jsonl) records **90 requests: 81 HTTP 200, 4 HTTP 404, 2 HTTP 403, and 3 timeout/error records** at final collection. All successful original downloads were reused. New direct collection requests used the unchanged `collect.py`, serially paced at one request per 2.2 seconds; no login, paywall, authentication or bot challenge was bypassed. The earlier claim that a browser User-Agent got Harappa 403 is not independently evidenced in this log: the recorded 403s are **Smithsonian** responses.

| Failure | Exact endpoint | Effect / resolution |
| --- | --- | --- |
| 403 | `https://repository.si.edu/items/a9c30a34-8dd1-470d-998a-1c44f50208e1` | Repository item inaccessible; no bypass. |
| 403 | `https://repository.si.edu/bitstreams/64271be1-5d78-4196-8a87-f1ea1669c777/download` | Repository download inaccessible; no bypass. |
| Timeout | `https://ojs.uop.edu.pk/ancientpakistan/article/view/580/528` | Public HTTP view succeeded. |
| Timeout | `https://ojs.uop.edu.pk/ancientpakistan/article/download/580/528` | Public HTTP download succeeded; Kenoyer 2021 paper available. |
| Timeout | `https://web.archive.org/cdx/search/cdx?url=harappa.com/slide/*&output=json&filter=statuscode:200&filter=mimetype:text/html&collapse=urlkey&limit=5` | No archive dating result. |
| 404 | `https://www.harappa.com/terms-of-use` | Image-rights page successfully retrieved instead. |
| 404 | `https://www.harappa.com/slide/molded-tablet-1` | Guessed lead absent; related `molded-tablet` / `molded-tablet-0` pages exist. |
| 404 | `https://www.harappa.com/slide/horned-deity` | Guessed lead absent; paper Fig.11 supplies captioned H95-2487 photo. |
| 404 | `https://www.harappa.com/content/master-animals-and-master-fish-and-tiger` | Guessed content page absent; direct Master of Animals PDF succeeded. |

## Validation

Checked source files, exact successful URLs, decoded image dimensions, native embedded PDF image sizes, crop boundaries, corpus baseline rows, CSV consistency, hashes, and the sherd arithmetic. The five requested target crops, H95-2487 caption/page, bangle crops, sherd tables, and recent-photo contact sheet were visually inspected. Collection code makes no sign readings, diameter estimates or M328 comparison. The report distinguishes unknown data from access failures and does not claim the open targets have been fulfilled.
