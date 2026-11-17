# Plate-corpus gate, v2: real detail in the plate scans

Date: 2026-11-17. This follows `RESULTS.md` (gate 1). Machine-readable results: `results_v2.json`. Ledger rows: `pc2_true`, `pc2_upload`, `pc2_readers`, plus dated correction notes on `pc_res` and `pc_vs_cisi`.

## Verdict

**FAIL at step 1. No public greyscale scan of any of the four volumes has 12 px/mm of real seal detail, so all four volumes are dropped and no second gate was run.**

- **The plate crops in gate 1 were enlarged low-resolution images.** Their true detail is a median **3.6 px/mm**, not the reported 18.5.
- **Plates are worse than CISI, not better.** On the paired seals the plates have 3.4 true px/mm; CISI has at least 5.3, and probably about 8.
- **"The readers are the bottleneck" is withdrawn.** The readers were given images worse than CISI, so gate 1 says nothing about how they read adequate images.
- No pre-registration was written, no seals were drawn and no reader agents were started. The task made all three conditional on at least one volume passing.

True px/mm per volume:

| Volume | Upload used in gate 1 | Nominal px/mm | Enlargement found | True px/mm | Best greyscale upload of the volume |
|---|---|---|---|---|---|
| Mackay 1938 FEM vol. II | `in.gov.ignca.9954` | 19.9 | 6x (block period 6) | **3.3** | 3.3 (`…_191_N` is the same file) |
| Vats 1940 EH vol. II | `dli.ministry.25730` | 15.4 | 4x (block period 4) | **3.9** | 3.9 (every other upload is 1-bit) |
| Mackay 1943 CE | `dli.ministry.25495` | 22.1 | 4x (block period 4) | **5.5** | at most 10.1 (`nufj-…`, 256 ppi colour) |
| Marshall 1931 MIC vol. III | `in.gov.ignca.48270` | 10.6 | 3-4x | **3.1** | at most 5.4 (`xSFp_…`, 1973 reprint) |
| All 20 seals | | 18.5 | | **3.6** (range 2.3-7.0) | |

The bar was 12 px/mm, and no volume clears it.

## What was wrong the first time

1. **The source files are enlargements.** The crop script was not at fault:
   - `p2_crop.py` decoded the full JP2 and cropped at native pixels, with no resize.
   - The uploads themselves were made from small images blown up 3-6x by pixel replication and then saved at "600 ppi".
   - The block grid is strong and exact. Mean gradient at one offset modulo the period, against the median offset:
     - FEM: ratio 8-15 at period 6, on all 8 crops.
     - EH: 3.7-9 at period 4.
     - CE: 5.7-6.5 at period 4.
     - A clean CISI crop scores 1.3-2.2.
   - A 6x block round trip removes 12-18% of the detail energy on 6 of the 8 FEM crops (27% on FEM 289, 37% on FEM 83). On a sharp image it removes about 66%, and on these same crops a 5x round trip removes 49-56%.
   - So the "20 px/mm" FEM crops hold about 3.3 px/mm of information, which is what the reviewer saw.
2. **The pre-registered px/mm was a geometric measure.** It was box pixels divided by seal millimetres. The gate-1 prereg did list "nominal can exceed effective resolution" as a risk, but only as a note that did not affect the gate. That note was the gate's undoing.
3. **The "readers are the bottleneck" argument does not hold.**
   - It rested on the FEM crops being "sharp" and on readers doing no better on CISI than on plates.
   - Both premises fail. The FEM crops are 3.3 px/mm. The CISI crops are the sharper set.
   - So equal scores on the two sets are no evidence about the readers.
   - Reader A's "pixelated" remark was accurate.
4. **One CISI pairing was wrong.** For FEM 288, the plate shows a 5-sign bar seal (36.8 x 15.2 mm, M77 has 5 signs). The CISI crop (`v1-078-077.jpg`, M-126) shows a square unicorn seal with a longer text. The gate-1 paired comparison therefore has at most 6 valid pairs.
5. **Halftone was not the main EH/CE problem.** Gate 1 blamed halftone screens. The bigger loss is the 4x enlargement.

## How real detail was measured

Script: `v2_effres.py`. Each image was tested in three ways:

- **Block grid.** Mean absolute gradient at each offset modulo k, for k = 2-40. A peak-to-median ratio of 2.5 or more marks pixel replication with period P.
- **Round trip.** Shrink the image by f, enlarge it back, and take the RMS difference over the RMS of the detail finer than 16 px. Two variants are run and the smaller loss is kept:
  - smooth: area shrink, bicubic enlarge;
  - grid-aligned: block mean, nearest enlarge, best phase.

  The factor is the largest f whose round trip keeps all but 17% of the detail. Where a block grid exists, the divisor of its period that shows a loss dip is used.
- **Tone.** The fraction of mid-grey pixels, to catch 1-bit scans.

**Calibration on known enlargements** of a sharp CISI crop:

| Input | Factor given |
|---|---|
| Sharp crop, unchanged | 2 (the test's floor) |
| 3x nearest | 3 |
| 3x bicubic | 4 |
| 6x nearest | 6 |
| 6x bicubic | 6 |

**How to read the numbers.** For block-replicated uploads the factor is exact, read straight from the grid period. For clean images it is only an upper bound on enlargement, because a sharp image already scores 1.5-2. So CISI's "true" figure (median 5.3) is a lower bound; its nominal figure is 7.9.

Gate 1 also suggested the power spectrum as a measure. It was not needed: the block grid gives the factor directly.

## Every upload checked

Audit scripts: `v2_audit.py` takes the two largest JP2s per upload, and `v2_audit_plates.py` checks seal-plate pages located by eye on thumbnails. Results are in `work/v2_scan_audit.csv` and `work/v2_scan_audit_plates.csv`.

| Volume | Upload | Stated ppi | Tone | Enlargement | Real paper ppi |
|---|---|---|---|---|---|
| FEM | `in.gov.ignca.9954` | 600 | grey | 6x | ~100 |
| FEM | `furtherexcavations…vol2…_191_N` | 600 | grey | 6x (same file) | ~100 |
| FEM | `in.ernet.dli.2015.57013` | 600 | **1-bit** | none found | see below |
| FEM | `in.ernet.dli.2015.440862`, `dli.jZY9…0009130`, `dli.ernet.426189` | 300-567 | 1-bit | | |
| EH | `dli.ministry.25730` | 600 | grey | 4x | ~150 |
| EH | `…vats vol2 alt_435_p`, `…alt1_617_R`, `in.ernet.dli.2015.106332`, `.210462`, `.358921`, `.358923`, `.426170`, `.537391` | 300-600 | **all 1-bit** | | |
| CE | `dli.ministry.25495` | 600 | grey | 4x | ~150 |
| CE | `in.gov.ignca.27263` | 600 | grey | 6x | ~100 |
| CE | `nufj-chanhu-daro…` | 256 | colour | none found (factor 1-1.5) | ~170-270 |
| CE | `chanhudaro…_184_y`, `in.ernet.dli.2015.105167` | 300 | 1-bit | | |
| CE | `BK001064…` | 72 | 1-bit | | |
| MIC | `in.gov.ignca.48270` | 300 | grey | 3-4x | 75-100 |
| MIC | `…vol3…_292_u` | 150 | grey | 2x | ~75 |
| MIC | `xSFp_…` (1973 reprint) | 256 | grey | none found | about 150 on this page |
| MIC | `dli.ministry.25759` | 150 | grey | | |
| MIC | `in.ernet.dli.2015.96024`, `.441817` | 600 | 1-bit (and vol. I per gate 1) | | |

Notes on the table:

- **EH alternative uploads.** The two `alt` uploads returned HTTP 503 for the JP2 zip and 500 for IIIF. They were measured from the full-size BookReader JPEG. Both are 1-bit: only 3% of pixels are mid-grey.
- **The CE and MIC greyscale upper bounds** come from page width relative to the gate-1 upload of the same plate page:
  - CE `nufj`: 2051 against 4507 px gives about 10.1 px/mm nominal.
  - MIC `xSFp`: 1362 against 2677 px gives about 5.4.
  
  Both stay under 12 even before any enlargement is taken off.

### The 1-bit DLI uploads

The 1-bit DLI scans are the one place where finer spatial detail survives.

- **`in.ernet.dli.2015.57013` comes from the same master scan as IGNCA 9954.** The page geometry is identical on p189 and p201 (template match r = 0.64-0.84 on the 8 FEM seals).
- **It was thresholded before the downsampling.** On FEM 273 it has 158 specks of 4 px or less. A thresholded 6x enlargement of the IGNCA file has 2.
- So IGNCA holds a full-resolution greyscale master. Only damaged derivatives are public.
- **The gate-1 prereg allows greyscale or colour scans only.** I kept that rule. It is part of the design, and the task said not to change the design without a written reason. A reason to keep it is visible in `crops_v2/contact_fem_compare.png`:
  - The 1-bit crops turn the relief shading into solid black.
  - FEM 461, 273 and 289 stay fairly legible. FEM 83, 407 and 420 are mostly blobs.
  - CISI shows the same seals more clearly than either plate version.

## Crop pipeline fix (`v2_crop.py`)

- **Two px/mm figures per crop.** Every crop reports nominal px/mm and true px/mm (nominal divided by the measured factor), plus its tone fraction.
- **Scan choice uses true px/mm**, not stated ppi or page size.
- **`tile()` splits a crop into tiles of at most 1000 px**, at native pixels, so that an image viewer cannot shrink it. Gate 1 did not do this. It did not matter there, because the crops held so little detail.
- **Re-measurement of the 20 gate-1 crops** is in `crops_v2/v1_remeasure.csv`.
- **FEM side-by-side sheet: `crops_v2/contact_fem_compare.png`.** It shows IGNCA greyscale, DLI 1-bit and CISI for the 8 FEM seals. I viewed it at full size. The IGNCA crops are soft 6-px blocks, and CISI is the clearest.
- **Steps 3-4 were not done**: no new draw, no 20 new crops, no new contact sheet. They depended on a volume passing step 1.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| Gate-1 plate crops carry >= 12 px/mm of real detail | **refuted** (true median 3.6) |
| Some greyscale/colour archive.org upload of FEM, EH, CE or MIC reaches 12 px/mm | **refuted** for all four |
| Plates are sharper than CISI | **refuted** (3.4 against at least 5.3 on the pairs) |
| Blind agent readers are the bottleneck (gate 1) | **withdrawn**: not tested on adequate images |

## What would change this

- **The IGNCA greyscale masters.** The DLI 1-bit derivatives show that full-resolution masters exist for at least FEM vol. II. At 600 ppi they would give about 20 true px/mm. Getting them means asking IGNCA (or the DLI mirror) for the original TIFF or JP2 files. This is an outreach item, not a download.
- **Physical rescans, or library collotype copies scanned at 600+ ppi in greyscale.** The carver-hands lead in `experiments/carver_hands/RESULTS.md` still stands.
- **A fair test of the readers** needs images that are at least CISI quality. CISI vol. 1-2 crops (about 8 px/mm nominal, clean) exist for many seals. A reader-reliability gate on CISI alone, with fresh seals and the segmentation guide gate 1 proposed, would separate reader error from image quality without waiting for new scans. It needs its own pre-registration.
- **Optional, not recommended as the main route:** a separate pre-registered gate on the 1-bit DLI FEM/CE uploads. They cover 636 + 48 texts, but any reading gain would have to beat CISI on the same seals.

## Files

- **Scripts:**
  - `v2_effres.py`: measure
  - `v2_audit.py`, `v2_audit_plates.py`: upload audit
  - `v2_thumbs.py`: locate plates
  - `v2_crop.py`: re-measure the 20 crops and build the FEM sheet
  - `v2_summary.py`: writes `results_v2.json`
- **Data:**
  - `work/v2_scan_audit*.csv`
  - `work/v2_audit_pages/`
  - `work/v2_contact_*.png`
  - `crops_v2/`
- **Downloads** are in `raw/v2/<item>/`. They are untrusted image data, only decoded and never executed.
