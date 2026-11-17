# Old excavation registers: seal tabulations from Marshall 1931, Mackay 1938, Vats 1940 and Mackay 1943

## Result

- We now have 1,811 register rows covering 1,524 distinct M77 texts:
  - Mohenjo-daro: 924 of 1,540
  - Harappa: 552 of 985
  - Chanhu-daro: 48 of 66
- Through CISI the rows also link to 590 ICIT records.
- The links are real. For the 490 rows where both an M77 and an ICIT text exist, sign sequences matched through the Wells-Mahadevan bridge have a mean similarity of 0.65, with 364 of 490 at 0.5 or more. Random pairs score 0.07 (21 of 1,984).
- New fields gained beyond M77 and ICIT:
  - Depth with decimal precision for 904 objects. M77 stores whole feet only. A further 31 objects have no depth in M77 at all.
  - Dimensions for 912 objects where ICIT has none or the object is not in ICIT.
  - Block/house/room findspots for 640 Mohenjo-daro seals (Mackay) and square/locus findspots for 47 Chanhu-daro seals. M77 has only a coarse area code.
  - Excavation field numbers for about 1,570 objects. Neither corpus file has these.
- Use with care:
  - The Mackay FEM, Vats EH and Chanhu-daro tables are good.
  - The Marshall MIC table is noisy. Its depths disagree with M77 in 84 of 268 checks.

## Sources (archive.org, public domain; downloads in raw/<item>/)

| Source | archive.org item | Section used | OCR | Parsed rows |
|---|---|---|---|---|
| Mackay 1938, *Further Excavations at Mohenjo-daro* (FEM) vol. I | in.ernet.dli.2015.70071 | Tabulation of seals, pp. 369-391 (leaves 391-413) | good | 695 (692 of 704 serials) |
| Vats 1940, *Excavations at Harappa* (EH) vol. I | in.ernet.dli.2015.537391 | Tabulation of seals, pp. 337-356 (leaves 363-384) | good | 649 after de-duplication (643 serials) |
| Mackay 1943, *Chanhu-daro Excavations* (CE) | in.ernet.dli.2015.105167 | Catalogue of pls. XLIX-LIII | good | 91 |
| Marshall 1931, *Mohenjo-daro and the Indus Civilization* (MIC) vol. II | in.ernet.dli.2015.107493 | Tabulation of seals, pp. 402-405 (leaves 55-58) | poor | 376 kept (rows with a site/field no.) out of 522 |
| CISI vols. 1-2 (Joshi & Parpola 1987; Shah & Parpola 1991), "Basic data" tables | TheIndusScript.TextConcordanceAndTablesIravathanMahadevan (India and Pakistan djvu) | Basic data for illustrated objects | fair | 2,282 rows; 1,875 with a KP number, 884 with a field no. |

- Marshall vol. I and III and Vats vol. II were also fetched. They contain prose and plates only, with no seal register.
- Several other DLI scans in raw/ have Devanagari-garbage OCR and were not used.
- No openly licensed per-object Indus dataset turned up beyond the CISI scans already in the project. HARP remains unreachable.

## How the rows were read

The work was done from the djvu word boxes (`*_djvu.xml`), not from the flat text. The steps were:

1. Deskew each page.
2. Anchor rows on the serial column.
3. Assign each word to the nearest anchor (`tablib.py`).
4. Read the fields:
   - FEM: by header column position.
   - EH: by content regex, because the column positions drift between pages.
   - CE: by regex on the catalogue entries.
5. Repair misread serials with a one-digit edit that continues the sequence. The original value is kept in `ocr_repaired`.

CISI was parsed the same way (`parse_cisi.py`). Apple Vision OCR (`tools/vocr`) was tried as a second reader but drops serials and short tokens, so the djvu text layer was kept.

## Links and their checks (`link.py` → `registers.csv`, `link_summary.json`)

M77 links use Mahadevan's App. V rule:

- text_no = 1000 + MIC serial
- text_no = 2000 + FEM serial
- text_no = 4000 + EH serial
- Chanhu-daro: 6000 + 100·k + plate number, with k = 1 for pl. LI, 2 for LII and 3 for LIII. The sequence test supports this: LI with k=1 gives 0.60 against 0.14 for k=2, and LII with k=2 gives 0.86 against 0.09 for k=1. LIII is unconfirmed because there was no CISI match. Plates XLIX-L (seal-amulets, sealings) have no M77 number.

ICIT links go from the register field number to the CISI "Basic data" field number, then from the CISI number to ICIT `cisi`.

| Source | Rows | M77 link | ICIT link | Depth vs M77 level (±1 ft) | CISI KP no. vs serial rule | Sequence similarity ≥ 0.5 |
|---|---|---|---|---|---|---|
| FEM | 695 | 639 | 272 | 506 agree / 9 disagree | 220 / 45 | 218 / 263 |
| EH | 649 | 558 | 132 | 486 / 38 | 105 / 26 | 80 / 123 |
| CE | 91 | 48 | 7 | 43 / 3 | n/a | 6 / 7 |
| MIC | 376 | 334 | 101 | 184 / **84** | 64 / 42 | 60 / 97 |

Caveats:

- The depth agreement for FEM is partly built in: Mackay sorted his table by depth, and M77 copied its levels from the same source.
- The independent checks are the KP numbers and the sign sequences.
- KP disagreements mostly come from field-number collisions in the CISI parse, where one field number occurs at several sites or sub-areas. They do not show that the serial rule is wrong.
- **Treat MIC rows as unreliable** unless `check_depth_vs_m77` agrees and the sequence similarity is 0.5 or more.

## New fields per source (linked objects only)

| Source | Depth absent in M77 | Decimal depth (M77 integer only) | Dims absent in ICIT | Fine findspot | Field no. |
|---|---|---|---|---|---|
| FEM | 11 | 462 | 363 | 640 (block/house/room) | 627 |
| EH | 11 | 313 | 342 | none (mound only: F 439, AB 79, D 45) | 558 |
| CE | 0 | 43 | 33 | 47 (sq./loc.) | 48 |
| MIC | 9 | 86 | 174 | none (area only) | 338 |

Quality notes:

- Dimensions are in inches, with the decimal point restored by rule.
- FEM dimensions agree with ICIT within 1.5 mm in 243 of 363 cases where both exist.
- FEM house and room strings are OCR text. Linked FEM seals spread over 282 house keys, 97 of which have two or more seals (445 seals). There are 63 rooms with two or more seals (151 seals). Expect some false splits from OCR variants.
- EH depths are below the local surface. FEM depths are below datum. CE depths are ± relative to datum. Do not pool them without a per-site offset.
- Type letters were captured: FEM types B, F, C and D; EH types a, h, c, n. The OCR of these letters is noisy.

## Previously failed tests that could now be re-run (not run here)

- **magnitude**:
  - Real dimensions for about 900 more seals: FEM, EH and CE length/width, plus thickness for FEM and CE.
  - Masses are still missing; the registers give no weights for seals.
  - This is enough to re-run any size-based version on Mohenjo-daro and Harappa.
- **assemblage**:
  - Block/house/room for 640 Mohenjo-daro seals and square/locus for Chanhu-daro.
  - Grouping by house is now possible: 97 houses hold two or more seals.
  - The registers here are seal-only. Co-found non-seal objects would need Mackay's room lists ("List of Objects..."), which are in the same OCR but were not parsed.
- **sealing_function**:
  - Only partly re-runnable.
  - Type letters separate seals from sealings and tablets in FEM and EH, and CE pl. L lists sealings.
  - These are a few dozen objects, and the OCR of the type letters is noisy.
  - Check the type codes against the report keys before use.
- **half_life chronology**:
  - Re-runnable within each site. FEM has decimal depth below datum together with block/house; EH has depth below surface within each mound.
  - This replaces M77's integer and missing levels.
  - Use FEM rather than EH: Vats depths are below the surface, which varies across the mound.
- **local_repeats office test**:
  - Re-runnable for Mohenjo-daro at house and room level: 445 seals in houses with two or more seals, 151 in rooms with two or more seals.
  - Normalise the house/room strings first (OCR variants).

## Files

- `registers.csv`: one row per register entry, with these fields:
  - source, object_no, site, findspot, block/house/room, depth_ft and its reference
  - dims (in), material, type/description, plate_ref, field_no
  - m77_text_no, cisi, icit_ids, ICIT dims/material
  - the three checks, linked, and the new_* flags
- `fem_seals.csv`, `eh_seals.csv`, `ce_seals.csv`, `mic_seals.csv`, `cisi_basic.csv`: per-source parses.
- `link_summary.json`: all counts above.
- Scripts: `fetch.py`, `find_pages.py`, `cache_words.py`, `djvu_rows.py`, `tablib.py`, `parse_fem.py`, `parse_eh.py`, `parse_mic.py`, `parse_ce.py`, `parse_cisi.py`, `link.py`.
  - Run with `.venv/bin/python -I`.
  - Downloaded files were only read, never executed.

## Not done

- Mackay's room-by-room object lists (assemblage context), plus the metal, bead and weight tabulations in FEM vol. I.
- A better Marshall MIC parse (re-OCR of the page images in raw/report_pages).
- House/room string normalisation.
