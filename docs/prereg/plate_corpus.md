# Pre-registration: plate-corpus gate (can 1930s-40s excavation plates give a better seal photo corpus?)

Registered 2026-11-17, BEFORE any seal crop is made or viewed and BEFORE any plate page is fetched. Work dir `experiments/plate_corpus/`. SHA-256 of this file and of `p1_sample.py` go in `docs/prereg/HASHES.txt` (tag `plate_corpus`). This is a gate check on 20 seals, not the corpus build.

## Question

Do the photo plates of Mackay 1938 (FEM vol. II), Vats 1940 (EH vol. II), Mackay 1943 (CE) and Marshall 1931 (MIC vol. III), as scanned on archive.org, give seal images that are (a) sharper than the CISI vol. 1-2 scans (about 8 px/mm of real seal) and (b) readable by blind agent readers well enough to support line-layout work (and, on a stricter line, carver-hand work)?

## What the analyst knows (declared)

- The analyst is not blind and can see M77 texts, the register rows and their dimensions, and will see the crops for crop quality control (correct object, whole object inside the crop). The analyst does not read signs and does not code anything that is scored.
- Before registration the analyst saw archive.org metadata only (item list, stated ppi, JP2-zip sizes, page counts, one IIIF info.json giving 4382 x 6798 px for page 200 of in.gov.ignca.9954). No plate page or seal crop has been viewed.

## Sample (`p1_sample.py`, seed 20261117)

- Eligible rows of `experiments/old_registers/registers.csv`: M77 link, both dimensions (`l_in`, `w_in`), a plate/serial reference, M77 object type = seal, exactly one M77 text record for the text number (one inscribed side, so no side confusion), and no `#` (broken passage) in the M77 text.
- MIC rows (known noisy) additionally need `check_depth_vs_m77 == agree` and, where present, `seq_sim_m77_icit >= 0.5`.
- Stratified quotas (single-line + multi-line): FEM 6 + 2, EH 5 + 1, CE 2 + 2, MIC 2 + 0 = 20 seals, 5 of them multi-line. If a stratum has fewer multi-line texts than its quota, the shortfall is filled with single-line texts.
- Replacement rule: a sampled seal is replaced (next draw from the same stratum with the same RNG stream continued, logged) ONLY if its plate cannot be located in any scan of the volume or its plate photo is absent (not photographed). Unreadable-but-present photos are NOT replaced; they are read and scored as they are.

## Scan choice per volume (objective, before reading)

For each volume, every archive.org upload found by title search is a candidate. The scan used is the one with the highest median measured px/mm over the sampled seals of that volume, among scans that are greyscale or colour (not 1-bit bitonal). Ties or failures fall back to the next. The choice uses only pixel geometry and bit depth, never reading results. All candidates and their stated ppi are listed in RESULTS.md.

## Measurement

- **px/mm** = sqrt(photo box width x height in px) / sqrt(l_in x w_in x 25.4^2). The box is the tight bounding box of the seal face (not the boss/back). If a plate shows both the seal and its impression, the face used is the one with the clearer inscription by box contrast (measured, not read); which one (seal = mirror of reading orientation, or impression) is recorded.
- Median and 10th-90th percentile over the 20 seals.
- CISI baseline: the CISI vol. 1-2 photo of the same object where `experiments/carver_hands/work/boxes.csv` or `experiments/scene_text` boxes locate it, measured the same way.

## Readers (blind)

- Two independent sub-agent readers: A = Opus, B = Sonnet. No other subagents.
- They see ONLY image crops (random IDs, no plate number, no field number, no site, no M77 or ICIT text) and the sign chart `data/sign_images/` (Mahadevan drawings). They are told the photo may show a seal (mirror image of the reading orientation) or an impression, and that signs may appear mirror-reversed relative to the chart.
- Each crop set is a separate batch: plate crops (P-set) and CISI crops (C-set), with independent random IDs and shuffled order. Order is counterbalanced: A reads P then C, B reads C then P. Carry-over memory between the two sets of the same seal is possible and is declared as a limitation.
- Per crop each reader records: number of lines; signs per line; the visual order it reports in (left-to-right as seen); best sign ID per position (Mahadevan M-number) with confidence 0-2; whether the image looks like a seal or an impression; "unreadable" flag.

## Scoring against the known text

- **Sign-count agreement** (primary): reader's total sign count equals the M77 total, exactly. Rate over the 40 seal x reader readings. Within +-1 also reported.
- **Line count vs M77**: reader's line count equals M77's.
- **Two-reader layout agreement** (primary): per seal, A and B give the same number of lines AND the same signs-per-line vector (this fixes line-break position). Rate over the 20 seals.
- **Per-position sign match** (secondary): reader sequence is compared to M77 in the expected visual order (impression with R-L reading -> visual R-L, i.e. reversed; seal face -> visual order equals reading order of the M77 sequence for R-L texts; L-R texts the converse), lines concatenated. Matches from an optimal (Levenshtein) alignment; accuracy = matches / M77 length. The better of the two orders is reported as a secondary, lenient figure.
- An "unreadable" flag scores as a miss on every measure.

## Gate (fixed)

- **PASS for layout work**: median px/mm >= 12 AND sign-count agreement >= 90% AND two-reader layout agreement >= 85%.
- **PASS for carver-hand work**: the layout PASS AND median px/mm >= 30.
- **Plates beat CISI**: on seals with both crops, median plate px/mm >= 1.5 x the CISI median AND plate sign-count agreement >= CISI sign-count agreement.
- Secondary line, reported but not gating: per-position sign match >= 80% (would support sign-level reading from plates).
- Each volume is also reported separately (n is small, 2-8 per volume; per-volume figures are descriptive only).

Why these numbers: CISI gives about 8 px/mm and failed line-break and scene work; 12 px/mm is 1.5x CISI, the smallest gain worth a corpus build. 90% count agreement allows 4 errors in 40 readings; below that, a line-layout study would carry more reader noise than the effects tested in `line_breaks`. 30 px/mm comes from `carver_hands` (0.1 mm cuts at 3 px).

## Coverage and cost

- Coverage = register rows with an M77 link whose plate volume's chosen scan passes, counted from registers.csv and the plate lists, with the distinct M77 text count.
- Cost = measured reader wall time and tokens per seal from the gate run, scaled to the coverage.

## What would make the result wrong

- Plates may be photographs of plaster casts or drawings at an unknown scale: scale is measured per seal from recorded dimensions, so a wrong dimension (OCR error) inflates or deflates px/mm. Outliers > 3x the volume median are checked against ICIT dimensions and logged.
- Nominal px/mm can exceed effective resolution (halftone screen, collotype grain, JPEG2000 compression). An effective-resolution note (visible screen or blur) is reported but does not change the gate.
- n = 20; a 90% rate on 40 readings has a 95% CI of roughly 76-97%. This is a gate, not a final estimate.

## Amendment A0 (2026-11-17, before any image was fetched; logged)

The first run of `p1_sample.py` crashed before drawing anything from CE (`int()` on the CE object number "CE pl. LI, 8"). The sort key was changed to a zero-padded string; quotas, seed and eligibility are unchanged. One pronoun was neutralised in this file. Both files were re-hashed under tag `plate_corpus_A0`.
