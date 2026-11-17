> **Correction, 2026-11-17 (see `RESULTS_v2.md`).**
>
> - **The px/mm figures below are nominal, not real.** Every plate upload used here is a low-resolution image enlarged 3-6x before upload. The true median detail is **3.6 px/mm**, not 18.5:
>   - FEM: 3.3 (6x)
>   - EH: 3.9 (4x)
>   - CE: 5.5 (4x)
>   - MIC: 3.1 (3-4x)
> - **The resolution bar therefore fails.** The plates are less detailed than CISI, not 2.5x more.
> - **"The readers are the bottleneck" is withdrawn.** The readers were given degraded images, so their reliability on adequate images is untested.
> - **One CISI pair was wrong.** The CISI crop paired with FEM 288 shows a different seal.
> - No greyscale archive.org upload of any of the four volumes reaches 12 px/mm. The text below is kept as it was written.

# Plate-corpus gate: can 1930s-40s excavation plates give a usable seal photo corpus?

Pre-registration: `docs/prereg/plate_corpus.md` (tags `plate_corpus` and `plate_corpus_A0` in `docs/prereg/HASHES.txt`). This was a gate check on 20 seals, not the corpus build. Ledger rows `pc_*` in `docs/test_ledger.csv`.

## Verdict

**FAIL.** The scans are sharp enough, but blind agent readers cannot read the seals reliably from them.

- **Resolution passes.** Median 18.5 px/mm of real seal, against about 8 px/mm in CISI. That is 2.5x CISI on the same seals and clears the 12 px/mm bar.
- **Reading fails.**
  - Blind sign counts matched the known text in 21 of 40 readings (52.5%, 95% CI 38-67%). The bar was 90%.
  - The two readers agreed on line count and line breaks for 7 of 20 seals (35%). The bar was 85%.
- **Carver-hand line fails.** The 18.5 px/mm median is below 30 px/mm.
- **Plates against CISI.** By the letter of the pre-registered rule, the plates "beat" CISI: 2.46x the px/mm, and count agreement 10/14 against 10/14 on the 7 seals with both crops. But the count rate is a tie, so the plates showed **no reading gain** over CISI. The comparison is also confounded (see "What failed").

The main bottleneck is the readers, not the scans:

- On the sharpest volume (Mackay FEM, about 20 px/mm, clean collotype impressions) the readers still got only 9 of 16 counts right.
- On the 7 paired seals they did exactly as well on the 8 px/mm CISI crops as on the 19 px/mm plates.
- Sign identification is poor everywhere: 23% per-position match on plates and 36% on the CISI crops. The secondary bar was 80%.

So more pixels alone will not unlock layout work with agent readers. Two volumes (Vats EH, Mackay CE) also have a real scan problem: they are coarse halftone prints, and all 4 "unreadable" flags fell on them.

## Numbers

| Measure | Plates (20 seals) | Bar | Result |
|---|---|---|---|
| Median px/mm (p10-p90) | 18.5 (12.3-22.1) | >= 12 | pass |
| Sign count exact vs M77 | 21/40 = 52.5% (CI 0.38-0.67) | >= 90% | **fail** |
| Sign count within +-1 | 31/40 = 77.5% | (reported) | |
| Line count vs M77 | 33/40 = 82.5% | (reported) | |
| Two-reader layout agreement (lines + signs per line) | 7/20 = 35% | >= 85% | **fail** |
| Per-position sign match (expected order / better order) | 22.8% / 23.7% | >= 80% (secondary) | fail |
| Unreadable flags | 4/40 (all EH/CE) | | |
| Median px/mm for carver hands | 18.5 | >= 30 | **fail** |

Paired comparison on the 7 seals with a CISI crop (6 FEM, 1 MIC):

| | Plate | CISI |
|---|---|---|
| Median px/mm | 19.5 | 7.9 |
| Count exact | 10/14 | 10/14 |
| Two-reader layout agreement | 3/7 | 5/7 |
| Per-position sign match | 39.5% | 35.5% |

By volume (descriptive only, n = 2-8):

| Volume (scan used) | Seals | Median px/mm | Count exact | Layout agree | Unreadable | Sign match |
|---|---|---|---|---|---|---|
| Mackay 1938 FEM vol. II (`in.gov.ignca.9954`) | 8 | 19.9 | 9/16 | 2/8 | 0 | 27% |
| Vats 1940 EH plates (`dli.ministry.25730`) | 6 | 15.4 | 7/12 | 3/6 | 1 | 21% |
| Mackay 1943 CE (`dli.ministry.25495`) | 4 | 22.1 | 1/8 | 0/4 | 3 | 12% |
| Marshall 1931 MIC vol. III (`in.gov.ignca.48270`) | 2 | 10.6 | 4/4 | 2/2 | 0 | 50% |

Per reader on plates:
- A (Opus): 9/20 counts right, 26% sign match, 1 unreadable, about 6.4 min for the batch.
- B (Sonnet): 12/20 counts right, 19% sign match, 3 unreadable, about 1.5 min for the batch.

## What failed, and why (plain)

1. **Agent readers do not segment and count signs the way Mahadevan did.**
   - Errors are often +-1 (77.5% of readings are within one sign).
   - The usual causes:
     - numeral strokes split or merged;
     - a sign next to the animal's horn read as a sign, or missed;
     - FEM 420, a scene seal, read as one line where M77 has 6 + 1.
   - This happens on crisp FEM crops too, so it is not a resolution limit.
   - Reader A described clean FEM crops as "pixelated". The image-viewing path the readers use may downsample large crops, but that is not verified.
2. **Halftone plates are poor.**
   - Vats EH and Mackay CE were printed as coarse halftones.
   - The nominal px/mm (15-22) overstates the effective resolution: the screen dots and blur are visible in `crops/contact_plate_crops.png`.
   - CE got 1 of 8 counts right, and 3 of its 8 readings were flagged unreadable.
3. **MIC scans are low resolution.** The only greyscale MIC vol. III scan (`in.gov.ignca.48270`, about 300 ppi) gives 10.6 px/mm, below the 12 px/mm bar. Both MIC seals were read correctly for count, but n = 2.
4. **The CISI comparison is weak.**
   - Only 7 of the 20 seals have a located CISI photo (all CISI vol. 1; the EH/CE seals were not found in the carver_hands box table).
   - Both readers noticed that some P and C crops showed the same seal. Reader B copied readings across those pairs. This carry-over was declared as a risk in the prereg, and it pushes the paired figures toward a tie.

## Method (short)

- **Sample.** `p1_sample.py`, seed 20261117, stratified: FEM 8, EH 6, CE 4, MIC 2, of which 5 have multi-line texts. Rows were drawn from 902 eligible register rows (M77-linked seals with dimensions, one inscribed side, no broken passage). No replacements were needed.
- **Scan choice.**
  - Metadata for every archive.org upload found by title search was probed with `p0_probe.py` (JP2-zip member list and sizes).
  - Seal plates were located with low-resolution page thumbnails through the BookReader page API (`pcfetch.py`).
  - Only the 13 needed plate pages were downloaded as original JP2s, about 16 MB in all (`raw/<item>/pages/`). The remaining raw/ space is thumbnails.
- **Candidates rejected per volume.**
  - FEM vol. II:
    - `in.ernet.dli.2015.57013` is thresholded to black and white.
    - `furtherexcavations…_191_N` is the same 4807x6798 scan as `in.gov.ignca.9954`. Its small 9 MB PDF is only a downsample; the JP2s are full quality, so the feared problem with that item does not apply to its JP2s.
    - The Tamil Virtual Academy item (`…TVA_BOK_0009130`, 567 ppi) is the text volume only.
  - EH:
    - `excavationsatharappa…vol2alt_435_p` is bitonal.
    - `in.ernet.dli.2015.210462` is text only.
    - `dli.ministry.25730` is the greyscale plates volume (4020x5815 px per page).
  - CE: `dli.ministry.25495`, 4507x6046 px per page.
  - MIC vol. III:
    - `in.gov.ignca.48270` is used (about 2650x3450 px).
    - `…292_u` is 150 ppi.
    - The 1973 reprint `xSFp_…` is a re-reproduction.
    - The two 600 ppi DLI items probed are vol. I text.
- **Every plate photographs impressions.** The FEM legends say "Impressions of seals". In EH, CE and MIC the animals face right, as on impressions.
- **Crops.**
  - The analyst placed one seed point per seal by eye next to the printed number (`p2_crop.py`, `SEEDS`).
  - The box was then found automatically: Otsu threshold, close/fill/open, then a trim of thin edge rows so that a merged handwritten number is cut off.
  - Crop QA (whole object, right object) led to 5 manual boxes: EH 3, EH 138, EH 16, CE LI-16 and CE LII-27. Each is logged in `crops.csv` (`box_method`).
  - px/mm = sqrt(box area) / sqrt(l x w in mm), as pre-registered.
  - FEM 83 is a likely dimension error. The register gives 2.0 x 1.09 in, but the photo is square in both FEM and CISI: plate 13.8 and CISI 5.4 px/mm, against about 20 and about 8 for the other FEM seals. It was kept as registered. It is not a >3x outlier.
- **Readers (blind).**
  - Two subagents, A = Opus and B = Sonnet.
  - They saw only `/tmp` packets: random IDs, crops and the 417-sign Mahadevan chart (`p3_reader_packets.py`; instructions copied to `readers/INSTRUCTIONS.md`).
  - Order was counterbalanced: A read plates then CISI; B read CISI then plates, the plates in reverse order.
  - Outputs are in `readers/`.
- **Scoring** (`p4_score.py` -> `scores.csv`, `results.json`).
  - Count exact vs M77.
  - Two-reader identical lines and signs-per-line vector.
  - Per-position match from an optimal edit alignment against the expected visual order (an impression of an R-L text, read left to right as seen, is the reversed M77 line).
  - An "unreadable" flag scores as a miss.

## Coverage if a later build were attempted

- Register rows with an M77 link, by volume:
  - FEM: 639 rows (636 distinct texts), 588 with dimensions
  - EH: 558 (552), 407 with dimensions
  - CE: 48 (48), 39 with dimensions
  - MIC: 334 (288), 144 with dimensions
- The three volumes that clear 12 px/mm (FEM, EH, CE) cover **1,236 distinct M77 texts**. All four together cover 1,524.
- The FEM plates number each seal by its register serial, so locating the seals is mechanical. The numbers are handwritten, though, so OCR will be weak and a seed or label step per plate is needed (about 50 seals per FEM plate).

## Cost (rough, from this run)

- **Reading.** About 4,900 subagent tokens and 10-30 s per seal per reader. Two readers on about 1,034 seals with dimensions comes to about 10M tokens and roughly 10-15 agent-hours.
- **Locating and QA.** About 45 plate pages, roughly 5 agent-hours at this run's pace.
- **Not recommended at current reader reliability.** Under this gate a full build would mostly produce counts that are wrong about half the time.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| The plate scans give >= 12 px/mm of real seal | supported (18.5 median; MIC alone fails at 10.6) |
| The plate scans give >= 30 px/mm (carver hands) | refuted for all four volumes |
| Blind agent readers count signs on plate crops with >= 90% agreement with M77 | refuted (52.5%, CI 38-67%) |
| Two blind readers agree on layout >= 85% | refuted (35%) |
| Plates improve agent reading over CISI | not shown (count 10/14 vs 10/14 on 7 paired seals; carry-over confound) |

## Next experiments

1. **Fix the reader before the scans.** Give readers a short calibration set of M77-segmented examples on other seals (not the test seals), plus explicit segmentation rules (numerals, compound signs, signs near the horn). Re-run this exact gate on a fresh 20-seal draw with a new seed. Measure reader-vs-reader agreement first, since it needs no ground truth.
2. **Check the image path.** Verify whether the readers' viewer downsamples crops. If it does, give tiled sign-row crops at native resolution.
3. If reading clears the gate, build only the FEM volume first (clean collotype, about 20 px/mm, 636 texts). Treat EH and CE as low-grade unless better scans of the Vats/Mackay plates turn up (for example, institutional collotype scans).
4. Carver hands still needs 30+ px/mm. None of these public scans reaches it. The human-action lead in `experiments/carver_hands/RESULTS.md` (1200 dpi rescans or museum macro photos) stands.

## Files

- Scripts:
  - `p0_probe.py`: probe the JP2 zips
  - `p0_dims.py`: scandata probe; it found no per-page sizes
  - `pcfetch.py`: single-page fetch and thumbnails
  - `p1_sample.py`: hashed
  - `p2_crop.py`
  - `p3_reader_packets.py`
  - `p4_score.py`
- Data:
  - `sample.csv`
  - `crops.csv`
  - `crops/plate_*.png` (20) and `crops/cisi_*.png` (7)
  - `crops/contact_plate_crops.png`
  - `readers/`
  - `scores.csv`
  - `results.json`
  - `work/reader_key.csv`
- Downloads are in `raw/<item>/` (untrusted image data, decoded only, never executed).
