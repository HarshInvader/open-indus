# Do gaps between signs mark word boundaries in scripts without dividers? (layout_word_division)

**SEALED v2, 2026-11-25** (tag `layout_word_division`), after one fresh review. Written 2026-11-25. Coordinator plan 12, top pick. No gap has been measured, no box has been joined to a word boundary, and no AUC has been computed. The drafter has seen one Yale tablet photo (layout check only) and the size statistics of the Dencker boxes (median box height and width), nothing else about gap sizes.

**v2 changes (fresh review, same day).** These apply the reviewer's must-fix items 1-8 and the nice-to-haves, and make the body follow the ruled decisions D1-D5 (end of file):
- the Dencker boxes are partial, so the gold gaps for G2 are redefined;
- the S1 counts are redone with damaged lines excluded, and the S1 sample is now drawn from all SAA tablets with a CDLI photo;
- the G1 join rule is replaced;
- §5.4 (planted run through the real pipeline), G2b (an S2 agreement check) and §6.4(d) (a sign-class control) are new;
- the reading precedence is fixed;
- the licence text is corrected;
- the statistic is written out exactly;
- S2 is clustered by provenience and year;
- crops are rotated 180° for raters;
- an Indus-resolution re-score is added.

## Question

Indus texts have no word dividers. Word division is one of the things no past decipherment did without (`experiments/decipher_reference_class/RESULTS.md`). Can the physical layout of an inscription stand in for a divider? This study asks:
- the gaps between neighbouring signs, and
- sign size and spacing in general.

**Kill test first, on read scripts only.** In two read scripts written without word dividers, does the gap between adjacent signs predict known word boundaries at AUC ≥ 0.65, after end-of-line cramping is controlled? The Indus stage is only sketched (§9), and it needs its own prereg if K0 passes.

## 1. Prior art: has this been done?

Sources were opened with a generic user agent (`open-research-site/1.0`). "(unverified)" means the source was not opened.

**Short answer: not found.** No open source measures inter-sign gaps on photos of a script without dividers and scores them against known word boundaries. The nearest work splits into four groups:

| Area | What is established | Source | Bearing |
|---|---|---|---|
| Scriptio continua in Greek and Latin | The oldest Greek and Latin inscriptions use word dividers (interpuncts). Classical Greek and late Latin write continuously. Word spacing in Europe comes in during the 7th-8th c. | Wikipedia "Scriptio continua" (opened); Saenger 1997, *Space Between Words* (unverified) | Established history of the convention. It gives no measured gap statistics. |
| Stoichedon Greek | Letters sit on a grid, the same number per line, with **no spaces between words**. | Wikipedia "Stoichedon" (opened) | **A stoichedon text cannot test this question**, because the layout removes gap variation by design. Excluded. |
| Dividers in neighbouring scripts | The Ugaritic alphabet uses a vertical divider stroke, which is rare in Assyrian cuneiform. Old Persian uses a sloping-wedge divider. | Wikipedia "Word divider" (opened) | Old Persian and Linear B can serve only as positive controls with the divider masked (§6.3). |
| Ashokan Brahmi | Hultzsch 1925 notes "a vacant space" at scattered points, often **inside** words (for example "between tha and ya", where the rock may be flawed). There is no remark on systematic word spacing. | Hultzsch, *Inscriptions of Asoka* (CII 1, new ed. 1925), archive.org `InscriptionsOfAsoka.NewEditionByE.Hultzsch`, OCR text searched (opened) | It suggests gaps in Brahmi follow the stone more than the words. Salomon 1998 on occasional word grouping in Ashokan texts was not opened (unverified). |
| Computational word segmentation by gaps | Gap-metric and scale-space word segmentation is standard for handwriting **with** word spaces. | Manmatha & Rothfeder 2005, IEEE TPAMI, doi:10.1109/TPAMI.2005.150 (Crossref record opened); ICDAR segmentation contests (unverified) | It assumes spaces exist. None of this work asks whether gaps carry boundaries in undivided scripts. |
| Cuneiform sign detection | Dencker, Klinkisch, Maul & Ommer 2020, PLOS ONE 15(12), doi:10.1371/journal.pone.0243039 (opened), with the dataset on GitHub `compvis/cuneiform-sign-detection-dataset` (opened). Cuneiform is written "without regular spacing between words", and signs are "often inscribed without space between neighboring signs". The release gives **8,109 expert sign boxes on 81 Neo-Assyrian tablets.** | (opened) | **The boxes exist, but no one has scored their gaps against words.** This is the main data asset (§2). |
| Cuneiform word segmentation from text | Dictionary-free segmenters reach F1 > 0.97 on transliterated Akkadian and Sumerian. | Zhou & Anderson 2026, EMNLP (repo library, verified) | Text only. The layout cue is untested. |
| Cypro-Minoan | A model predicts word dividers from the images of neighbouring signs. | Corazza et al. 2022, PLOS ONE, doi:10.1371/journal.pone.0269544 (repo library, verified) | Uses divider glyphs, not gaps. |

**Indus claims about spacing.**
- **Mahadevan 1977, Parpola 1994 and Fuls 2024** use spacing and cramping to set the **direction** of writing (about 87% right to left, per Fuls). They do not use it for word units (`experiments/literature/RESULTS.md`, citing [Fuls 2024, IJAS 14(1)](https://ijas.usb.ac.ir/article_8463.html)). Mahadevan's harappa.com page returned 403, so it is unverified. No open source was found in which Mahadevan, Parpola, Wells or Fuls claims that gap or sign size marks word units. Wells 2011 and 2015 were not opened (unverified).
- **Zenil & Uthamacumaran 2026** (arXiv 2610.08861, repo library) predict Indus **row breaks** from the sign sequence at AUC 0.81 on 47 inscriptions. That uses the text, not measured coordinates.

**This repo already holds:**
- `structure` §4: unsupervised segments are short (1.4 signs on average). A bigram beats the segment lexicon.
- `line_breaks`: **untestable.** It had 74 usable multi-line texts. Line 1 is not full, and about half of the `|` breaks are separate sign fields rather than wraps. That is layout evidence that some unit structure is shown spatially.
- `plate_corpus` v1 and v2: blind agent readers segmented and counted Indus signs poorly (52.5% exact counts). Their images were bad (3.4 true px/mm), and CISI is about 5.3-8 px/mm. **Agent sign segmentation is the known weak point**, and it drives the measurement design in §4.
- `decipher_reference_class`: word division is part of the rule that every read script satisfied.

**What is skipped as established:** that Greek, Latin and Brahmi were written continuously; that cramping gives direction on Indus seals; that dividers exist in Old Persian, Ugaritic and Linear B.

## 2. Candidate scripts and the count gate

### Minimum, written before counting
The minimum below was written at 2026-11-25 16:37 UTC, before any count. The scratch file has sha256 `b758d9ca547d80cf3842fd25da4b061d0562d04a84e560a007eabbb2f3ae51fe`.

It applies per script, counting only objects that have an open photo usable locally, a word-segmented transliteration that aligns line by line, and at least one line of 3 or more signs.
- **M1.** At least 30 inscribed objects (the bootstrap clusters).
- **M2.** At least 1,500 within-line gaps, leaving out the last gap of each line.
- **M3.** At least 300 word-boundary gaps and at least 300 non-boundary gaps among those.
- **M4.** A median sign height of at least 25 px at the resolution used.

**Why these numbers.** At 300/300 the AUC standard error is about 0.023. With a design effect of about 2 from object clustering it is about 0.033. A true AUC of 0.65 then gives a lower 95% bound above 0.58.

### Counts (label-free: signs, words and lines from transliterations and box files; no gap size read)

| Script | Photos | Transliteration with word division | Objects | Lines ≥ 3 signs | Gaps (excl. last per line) | Word-boundary gaps | M1-M4 |
|---|---|---|---|---|---|---|---|
| **Neo-Assyrian Akkadian cuneiform** (SAA letters, reports and other genres) | CDLI tablet photos (local use only). The Dencker 2020 segment files list 2,198 tablets with a CDLI image. Boxes exist for only 81 of them: 8,254 boxes (8,109 sign + background), median box height 55 px and width 74 px. | ORACC SAAo corpus JSON, **CC0**. Each word is a lemma node with its signs. **Lines with any ORACC break, damage, uncertainty, collation or correction mark, or an x sign, are excluded**, as in S2. | **2,164** Dencker-imaged tablets matched to ORACC; **832** have 6 or more clean lines of 3+ signs | 13,231 clean (of 39,493) | 72,725 | 29,239 (non-boundary 43,486) | **Pass.** The v1 count (56 boxed tablets, 7,913 gaps) is withdrawn: it counted damaged lines and assumed whole-tablet Dencker coverage. On those 56 tablets, clean lines give only 287 lines and 1,474 gaps, which **fails M2**. So the S1 sample is drawn from the 832 (§4.5), and the Dencker boxes serve only G2 and the record-only measure (D5). |
| **Ur III Sumerian cuneiform** (administrative tablets) | Yale Babylonian Collection, **CC0** IIIF (Peabody API). 1,388 images are already on disk under `experiments/stamp_detector/raw/img/` (gitignored), about 11 px/mm on the obverse, so a sign is about 40-50 px tall. | CDLI ATF (dump on disk). Spaces separate words; `-` and `.` join signs; determinatives count as signs. Only lines with no damage marks are counted. | 6,538 with ATF and a Yale photo record; **256 with the photo already on disk** | 63,284 (on disk: 2,787) | 215,550 (on disk: 9,138) | 122,289 (on disk: 5,199; non-boundary 3,939) | **Pass** |
| Ashokan Brahmi (Prakrit) | Hultzsch 1925 estampage plates, archive.org, **public-domain mark**, 300/600 dpi, 55 plates | Hultzsch's line-numbered, word-divided text | **About 26 Brahmi inscriptions** (Shahbazgarhi and Mansehra are Kharoshthi and excluded) | not counted | not counted | not counted | **Fails M1** (26 < 30). Reserve only, and only if the Sanchi and Bharhut donative labels are added under a new count. |
| Linear B, Old Persian | Not counted | — | — | — | — | — | Divider scripts, so **positive controls only, with the divider masked** (§6.3). Not part of the kill test. |
| Maya | — | — | — | — | — | — | **Excluded.** Glyph blocks sit on a grid, and blocks are not words. |
| Early Greek and Latin | — | — | — | — | — | — | **Excluded.** Early texts use interpuncts. Classical Attic texts are mostly stoichedon. Open photos with aligned texts are scattered. |

**Gaps free of the sign-class confound** (§6.4(d)). These are gaps where neither neighbour is a numeral, a determinative or, in S1, an ORACC logogram:
- **S1:** 40,407 such gaps, 11,332 of them boundaries, over the 2,164 tablets;
- **S2:** 5,460 gaps, 2,573 of them boundaries, on the 256 tablets on disk.

**Dencker coverage** (must-fix 1):
- The reviewer counts **47% of transliterated signs boxed on a median face**. The drafter's recount, over the 109 faces that have both files, is 66%. The two counts treat empty and background rows differently. Either way, coverage is partial.
- **Line annotations exist for 36 tablets.** 24 of them have boxes and a Dencker transliteration on the same face, and 11 match ORACC.
- On the first 10 of those 24 in calibration hash order, there are at most **704** candidate consecutive gold pairs. This is an upper bound from label presence; position is not yet checked.

The v2 scratch count scripts (`count_na2.py` for S1, `count_ur3_v2.py` for S2) will be committed as `experiments/layout_word_division/count_*.py` at sealing and hashed with this file.

### Chosen kill-test pair, and its weakness
- **S1: Neo-Assyrian.** The expert boxes exist on a subset, so measurement error can be checked against them.
- **S2: Ur III Sumerian.** It is a different language, 1,300 years earlier, with different sign forms and genre. The photos are CC0 and the counts are large.
- **Weakness.** **Both are cuneiform.** They are two writing traditions of one script family, not two unrelated scripts. A shared cuneiform habit (wedges crowding each other) could pass or fail both together. **Ruled D1:** the pair is accepted, and every reading says "shown within cuneiform only". Ashokan Brahmi is the next script if an open source reaches 30 objects (it fails M1 now).

## 3. Data, licences, storage

| Item | Licence | Use |
|---|---|---|
| ORACC SAAo JSON (`saao-saa01…16.zip`) | CC0 (stated in each file) | Word segmentation for S1. May be committed as derived counts. |
| Dencker 2020 box, line and transliteration CSVs | **The Dencker repo has no licence, so all rights are reserved by default. Only the article is CC BY 4.0.** | Local use only. **Dencker boxes, and per-gap values derived from them, are never committed. Only aggregates are** (ICCs, recall, the record-only AUC). The CSVs are not re-hosted. |
| CDLI photos of the S1 tablets | CDLI terms, not an open licence | **Local only, never published.** Fetched at 1 request per second. |
| Yale Peabody IIIF images | CC0 | Local. Crops need not be published; none will be. |
| CDLI ATF dump (already on disk) | CDLI terms | Word segmentation for S2. Local. |
| CISI vols. 1-2 PDFs (`experiments/iconography/raw/cisi/`, gitignored) | Not open | Indus sketch only (§9), local only. |
| Museum APIs (Met, Cleveland and others) | CC0 records only | Not needed for K0. They are possible sources of Indus seal photos for §9. |

- **Storage.** Downloads go to a new empty directory outside the repo first. The repo copy lives under `experiments/layout_word_division/raw/`, which `experiments/*/raw/` keeps out of git.
- **What is committed.**
  - Agent box coordinates, per-gap values from agent boxes, hashes and scores. No Dencker-derived per-gap value is committed.
  - **No image or crop is ever committed or published.**

## 4. Measurement design

### 4.1 What is measured
- **Sign box.** A tight axis-aligned rectangle around all strokes or wedges of one sign, in the rotated frame of its line.
- **Line frame.** A straight line fitted through the box centres. Coordinates are rotated so the line runs horizontally, in writing direction (left to right for both S1 and S2).
- **Raw gap** `g_i`: the left edge of box i+1 minus the right edge of box i. It may be negative where signs overlap; Dencker notes that cuneiform signs often touch.
- **Normalised gap** `G_i = g_i / H_line`, where `H_line` is the median box height in that line. Height is used, not width, because sign width varies with sign identity much more than height does.
- **Sign-width control.** The widths of the two neighbours, `W_i / H_line` and `W_{i+1} / H_line`, enter the residual model (§4.3). This handles the case where wide signs simply sit further apart.
- **Secondary layout cues**, reported and not decisive:
  - vertical offset between neighbouring box centres, `/ H_line`;
  - size ratio `log(area_{i+1} / area_i)`.

### 4.2 Who measures, and blinding
- **Primary measurer: blind agent boxes.**
  - **Agents (ruled D2).** Two fresh agents, Opus = A and Fable = B, each blind to the transliteration and to the other, each run once. Sonnet replaces a model only under R3.
  - **Bundle.** A rater gets a new empty working directory holding one crop per inscribed surface, the protocol sheet (§10), and nothing else: no transliteration, no sign list, no catalogue number, no repo or web access.
  - **Rotation, the default.** Every crop is shown **rotated 180°**. This keeps every gap but makes signs hard to read, so a rater cannot fall back on reading. `align.py` maps the boxes back to the original frame and reverses the box order. This also applies to the calibration and synthetic crops, so G2, G2b and §5.3-5.4 measure the rotated task.
    - If rotation breaks the box task, G2 fails, and F2 applies as written.
    - There is no switch back to upright crops.
  - **Labels.** Crops are renamed by sha256 of `layout_word_division:crop:<rater>:<id>` and the key is hashed before raters start. This is the blind-mapper protocol of `foreign_transcribe3` §4.
  - **Output.** A JSON list of lines; each line is a list of boxes `[x0, y0, x1, y1]` in pixel coordinates of the given crop, in visual order.
- **Reference rater for S1: the Dencker expert boxes.** These were drawn by Assyriology students **who could see the transliteration**, so they are not blind. They also cover only part of each face. Per ruled D5 they are used:
  1. as the gold standard for the G2 validity check (§4.4);
  2. for a **record-only S1 AUC** on the boxed tablets. It is never decisive.
- **Classical CV, a cross-check on S1 only.** Inside each line strip (from the Dencker line annotations), compute a column profile of wedge edge energy (Sobel magnitude, summed over the strip height). The **CV gap** is the width of the profile valley below the strip's 20th percentile, between the centres of boxes i and i+1. It uses the box **centres**, not their edges, so annotator edge bias cannot enter it. Reported, not decisive.
- **Why no CV as primary.** Cuneiform wedges on worn clay do not separate into connected components. `plate_corpus` showed agents mis-segment Indus signs. Gate G2 below tests whether agents box cuneiform well enough.

### 4.3 Lines and end-of-line cramping
- **Exclusions.** The last gap of every line is excluded from the primary test, because cramping and line-end spreading concentrate there. Lines with fewer than 3 boxes are excluded.
- **Residual gap** `R_i`. The model is fitted **without boundary labels**, on all scored gaps of that script and rater: `G_i` on a natural cubic spline of relative position in the line `p_i = i / (n_line − 1)`, plus the two neighbour widths, plus the line's fill ratio (summed box width / line length). `R_i` is the residual.
  - **Spline.** Boundary knots at 0 and 1, interior knots at 0.25, 0.50 and 0.75 (4 df).
  - **Fit.** Huber M-estimation with tuning constant **k = 1.345**, scale by the normalised MAD (re-estimated by IRLS to convergence, tolerance 1e-8, at most 100 iterations).
  - **No refit under resampling.** The model is fitted once per script and rater and is not refitted in bootstraps or shuffles.
- **Within-line comparison.** The primary AUC compares only gaps **in the same line** (§6.1). Line-level scale, hand, tablet and photo effects therefore cancel.

### 4.4 Joining gaps to word boundaries (after measurement is frozen)
- **G1, alignment.** Agent boxes carry no sign identity, so the join is by count and order only.
  - **The rule.** A line is joined only if both raters' box counts equal its sign count and A's and B's boxes pair one-to-one in order at IoU ≥ 0.5. Lines are matched by rank after removing $-, ruling and seal lines; a face whose line counts differ is dropped. `align.py` runs after the outputs are hashed, with no manual edits.
  - **Ranks.** They count every transliterated line, including the damaged lines that are later excluded from scoring.
  - **The drop rate is reported. If more than 40% of clean lines are dropped in a script, that script fails G1** (fallback F1).
- **G2, measurement validity, on S1 only and before any boundary is joined.**
  - **Calibration set.** 10 S1 tablets, the first 10 by sha256 of `layout_word_division:cal:<id>`, among Dencker tablets **with line annotations**. These tablets are excluded from the S1 draw.
  - **Gold gaps.** Gold gaps only between boxes that are consecutive signs in the Dencker line, ordered along the line annotation and matched to the transliteration by MZL label. Tablets without line annotations are skipped. If the calibration set gives fewer than 200 gold pairs, add tablets in hash order; if still fewer than 200, G2 fails.
  - **Pairing.** Agent boxes are paired to the gold boxes by IoU ≥ 0.3 (Hungarian). Recall is computed over gold boxes only, because unboxed signs have no gold.
  - **Pass** if, for each agent:
    - box recall is ≥ 0.85;
    - on gold pairs whose two boxes are both matched, the agent gaps have ICC(2,1) ≥ 0.70 against the gold gaps;
    - the agent-agent gap ICC is ≥ 0.70.
  - **Exclusion.** This set is **excluded** from the S1 AUC.
  - **Feasibility, stated now.** Agent edge errors of ±5-10 px are about the size of a typical gap (about 0.1 × 55 px). **G2 at ICC ≥ 0.70 may be out of reach.** If so, the study ends INCONCLUSIVE after F2. **The bar is not lowered.**
- **G2b, S2 agreement.** Agent-agent gap ICC ≥ 0.70 on 10 S2 tablets: the first 10 of the S2 draw, both faces.
  - It uses no labels, so these tablets stay in the S2 AUC.
  - G2b failing is treated like G2 failing: the F2 re-run is applied to S2 once, and INCONCLUSIVE follows if it fails again.
- **G3, resolution (M4).** The median box height at the image size used is ≥ 25 px. S1 passes at 55 px. For S2 it is checked on the first 10 sampled tablets.

### 4.5 Sample
- **S1.**
  - **Draw.** 60 tablets, the first 60 by sha256 of `layout_word_division:S1:<id>` among the 832 SAA tablets that have a CDLI image listed by Dencker and at least 6 clean lines of 3 or more signs. Calibration tablets are skipped, and the next in hash order is taken.
  - **Measured faces.** Obverse and reverse.
  - **Expected yield** (label-free count, done before calibration exclusions): 897 clean lines, 4,859 gaps, 1,886 boundaries.
  - **Clusters.** The bootstrap cluster is the tablet.
- **S2.**
  - **Draw.** 60 tablets from the 256 Ur III photos on disk, the first 60 by sha256 of `layout_word_division:S2:<P-number>` among tablets with at least 6 undamaged lines of 3 or more signs.
  - **Measured faces.** Obverse and reverse, cropped from the six-view sheet by a fixed rule in `make_crops.py`.
  - **Expected yield.** About 650 lines and 2,100 gaps, with about 1,200 boundaries. This is checked against M2 and M3 before measurement (a label-free count).
  - **Clusters.** The bootstrap cluster is **provenience × regnal year**, from the Yale record or the CDLI catalogue. A tablet missing either field is its own cluster. If there are fewer than 20 clusters, the tablet is the cluster, and this is reported.

## 5. Planted known answers (run before any real gap is joined to a label)

1. **Synthetic layouts.**
   - **Rendering.** `synth.py` renders 400 lines of cuneiform-like glyphs (random wedge clusters drawn at the size and aspect statistics of the Dencker boxes), grouped into "words" of 1-4 signs.
   - **Gap model.** Base gap ~ N(0.10, 0.08) × H, truncated at −0.15. Line-end compression shrinks the last 30% of gaps by up to 50%. Word-boundary gaps get an extra `δ × H`, with δ ∈ {0, 0.03, 0.06, 0.10, 0.20}.
   - **Noise.** Gaussian pixel noise and a shading gradient.
2. **Scorer check (truth boxes).** With true boxes:
   - δ = 0 must give a primary AUC in [0.47, 0.53], and the within-line shuffle null must reject at p < 0.01 in no more than 5% of 200 replicates;
   - δ = 0.20 must give AUC ≥ 0.80.

   This checks the cramping control: line-end compression with δ = 0 must not create a false signal.
3. **Measurer check (agent boxes).** Each agent boxes 40 of the synthetic lines (δ = 0.10 and δ = 0, 20 each, mixed blind). The recovered AUC at δ = 0.10 is reported with the truth-box AUC. The **attenuation ratio** `(AUC_agent − 0.5) / (AUC_truth − 0.5)` is reported and used in §8 to read a FAIL.
4. **Planted test through the real pipeline.**
   - **The test.** On the S1 calibration tablets, run agent-A boxes through `align.py` and `score.py` using pseudo-boundaries from each line's own word-length sequence, shuffled. At δ = 0 the AUC must fall in [0.45, 0.55]. Boxes past each pseudo-boundary are then shifted by 0.10·H, and the result is reported.
   - **Word lengths.** They come from ORACC. Only calibration tablets with ORACC text are used. If fewer than 5 such tablets exist, the remaining ORACC-matched line-annotated tablets (11 in all) are added in hash order, for §5.4 only.
   - **Failure.** If the δ = 0 condition fails, it is treated as F3.

## 6. K0 statistic, bar and null

### 6.1 Primary statistic, per script
- **Within-line AUC.** Over every pair (b, n) of a word-boundary gap and a non-boundary gap **in the same line**, both not the last gap, it is the share of pairs with `R_b > R_n`, with ties counting ½. Pairs are pooled over lines.
  - **Exactly:** `AUC = Σ_l Σ_{b∈B_l} Σ_{n∈N_l} [1(R_b > R_n) + ½·1(R_b = R_n)] / Σ_l |B_l|·|N_l|`, where `B_l` and `N_l` are the boundary and non-boundary gaps of line l, last gap excluded.
  - Lines with no boundary or no non-boundary gap add nothing.
- **Uncertainty.** A 95% **percentile** bootstrap.
  - **Resampling.** 2,000 resamples of clusters with replacement (S1: tablet; S2: provenience × year, §4.5), with each cluster's lines and pairs carried whole.
  - **No refit.** `R_i` stays as fitted on the full data.
  - **Seed.** 20261125.
- **Rater.** The primary value is agent A's boxes. Agent B is reported, and the mean of A and B is a sensitivity check.

### 6.2 Null
- **Shuffle.** Boundary labels are shuffled **within line** (positions kept; each line's number of boundaries kept), 1,000 times.
- **p-value.** One-sided: (1 + #null ≥ observed) / 1,001.

### 6.3 Optional positive control (descriptive, not part of PASS)
- **Source.** Old Persian (Behistun or Persepolis, open Wikimedia photos), divider wedges boxed as signs and then removed.
- **What it measures.** The gap left where the divider stood is compared with the other gaps.
- **Status.** This is a pipeline sanity check only. Masking a divider leaves a large gap by construction, so it cannot count toward PASS. It runs only if a count of at least 20 lines is reached.

### 6.4 K0 rule

**PASS** only if, in **both** S1 and S2 (primary rater):
- (a) within-line AUC ≥ 0.65;
- (b) lower 95% bootstrap bound ≥ 0.58;
- (c) shuffle-null p < 0.01;
- (d) the same AUC on gaps where neither neighbour is a numeral, determinative or (S1) ORACC logogram has a lower 95% bound ≥ 0.55;
- and G1, G2, G2b and G3 have passed, and the checks of §5.2 and §5.4 have passed.

**Notes on (d).**
- S2 has no logogram flag, so (d) removes numerals and determinatives only.
- **The breaks inside Ur III numerals, as in `1(u) 2(disz)`, are editorial.** The ATF splits one number into words, so those boundaries say nothing about the scribe. (d) removes them.
- The (d) residuals come from the same fitted model as the primary; there is no refit.

**FAIL** if, in either script, the upper 95% bound is < 0.65 with the measurement gates (G1, G2, G2b, G3) passed.

**INCONCLUSIVE** otherwise, which includes any failed measurement gate.

Per-position and per-sign-pair breakdowns, the secondary cues (§4.1) and the Dencker and CV versions for S1 are **description only**.

### 6.5 Hit@1
**Hit@1 is not relevant here and is not reported.** Nothing is ranked against candidate readings. The output is a separability score for a binary label (boundary or not), so AUC is the right measure.

## 7. Fallbacks, fixed now (any other change after calibration starts makes the study INVALID)

- **F1. G1 fails in a script** (> 40% of lines dropped). That script is not scored. K0 is INCONCLUSIVE. There is no substitute script under this prereg.
- **F2. G2 fails.**
  - The agents are re-run **once** with crops upsampled 2x (bicubic) and the protocol sheet's optional "one box per sign, include touching wedges" paragraph switched on. Both are written in §10 now.
  - If G2 still fails, K0 is INCONCLUSIVE ("no blind measurer of cuneiform layout at this precision"). The S1 Dencker AUC is reported as description only (record-only, D5). The ICC bar of 0.70 is not lowered.
- **F3. The synthetic δ = 0 check fails** (false-reject rate > 5%). The position spline is replaced by position-decile fixed effects plus "last 3 gaps" indicators, and §5.2 is re-run. If it still fails, the design is INVALID and stops.
- **F4. G3 fails for S2.** The next IIIF size up (full resolution) is fetched for the same 60 tablets. Nothing else changes.
- **R1-R3 from `foreign_transcribe3`:**
  - R1: a bad-format output is re-run once with the same model, and a second failure counts as a G2 failure;
  - R2: a bad crop is fixed before raters start;
  - R3: if a model is unavailable, Sonnet replaces it.
- **No second K0.** No other script, rater, statistic or bar is tried after the labels are joined.

## 8. Frozen readings

| Outcome | Reading | Consequence |
|---|---|---|
| PASS in both | "In two cuneiform traditions without dividers, inter-sign gaps carry word-boundary information (AUC a, b), **shown within cuneiform only**." A pass does not show that the cue carries across script families (D1). | The Indus stage (§9) may be pre-registered, after the §9 resolution gate. It does **not** say Indus gaps mark words. |
| PASS in one, FAIL in the other (**this row takes precedence over "FAIL (either script)"**) | "Gap as a boundary cue is tradition-specific, shown within cuneiform only." | No Indus stage. Atlas entry. |
| FAIL (both scripts, or one FAIL with the other INCONCLUSIVE) | "Gap size is not a usable word-boundary cue in undivided cuneiform at agent-box precision (shown within cuneiform only)." The attenuation ratio (§5.3) is quoted. If it is < 0.5, the reading adds "measurement noise may hide a weak cue". | Indus layout segmentation via gaps is **closed** until an expert measurer exists. Atlas entry; reopen only with expert boxes. |
| INCONCLUSIVE | Reported with the failed gate or interval, shown within cuneiform only. | No Indus stage. |

- Every outcome gets a ledger row.
- **Nothing here bears on any reading of an Indus sign.**

## 9. Indus stage (sketch only; needs its own prereg)

- **Images.**
  - CISI vols. 1-2 photos on disk (about 5.3-8 px/mm per `plate_corpus` v2, so an Indus sign is roughly 20-40 px tall and a gap of 0.5 mm is about 3-4 px).
  - CISI 3.3 pages in `experiments/source_sweep/raw/cisi33/`.
  - CC0 museum photos (Met and Cleveland APIs).
- **Measurer.** The same blind protocol, only if G2-style validity holds on Indus (to be shown by two-rater agreement, since there are no gold boxes).
- **Known answers.** None exist for Indus words. The test would score gaps against **independently proposed boundaries**, each frozen beforehand:
  - the frame grammar's opener and closer slots;
  - the fixed pairs (M267-M99, M336-M89-M211) as non-boundaries;
  - the numeral + sign formulas.

  Those segmentations predict where gaps should be large.
- **Direction.** The cramping side must be modelled first, since direction is itself read from spacing.
- **Resolution gate, record-only.** Before any Indus stage, K0 is re-scored on S1 and S2 crops downsampled to Indus resolution (median sign height 20-40 px; 30 px is used) by area averaging. This uses the same raters protocol, fresh agents and the same scorer.
  - The result does not change the K0 verdict.
  - It gates the Indus sketch: if (a)-(c) of §6.4 fail at Indus resolution, the Indus stage is not pre-registered.
- **Do not run** unless K0 PASSES.

## 10. Protocol sheet for the box raters (hashed with this file; the only text a rater sees)

> You will see images C1…Cn. Each shows one inscribed face of a clay tablet (or, in a calibration set, a drawing of glyph-like marks). Some images may be upside down; box them exactly as shown and do not rotate them.
> 1. Find each line of writing, top to bottom.
> 2. In each line, draw one tight box around every sign, in order from left to right. A sign is a cluster of strokes or wedges that belongs together. Do not split one sign into two boxes or merge two signs into one box. If you are unsure, make your best single choice.
> 3. Give each box as `[x0, y0, x1, y1]` in pixel coordinates of the image as given (origin top-left).
> 4. Skip broken or illegible areas. Do not box a region you cannot see.
>
> *(F2 paragraph, used only in the F2 re-run:)* Use exactly one box per sign. Include wedges that touch a neighbouring sign in the box of the sign they belong to. Boxes may overlap.
>
> Work alone. Do not use the web or any file other than those given. Return only JSON:
> `{"rater": "<A|B>", "crops": {"C1": {"lines": [[[x0,y0,x1,y1], ...], ...], "note": "<optional>"}, ...}}`

## 11. Folding in `foreign_transcribe3`

That draft's premise mostly failed at drafting:
- UR-07 already has a print;
- UR-09 is probably a duplicate of UR-05;
- BAHRAIN-02 keeps one or two signs;
- the drawings are 3.4 px/mm.

**Reused here:**
- the blind-rater protocol: anonymised crops, hash-ordered labels, and a key hashed before raters start;
- two raters from different model families, with outputs hashed before scoring;
- fallbacks R1-R3;
- crop hashing in `make_crops.py`.

**Not reused:**
- the Gulf-seal drawings, which are far too coarse for gap measurement (signs 8-15 px);
- its K0 and main step;
- its M-number DP alignment, which G1 no longer needs because agent boxes carry no sign identity.

**Ruled D4:** `foreign_transcribe3` is superseded. Its draft is kept, marked "superseded by layout_word_division before sealing".

## 12. Code and CPU

**Files** (`experiments/layout_word_division/`), all hashed into `docs/prereg/HASHES.txt` (tag `layout_word_division_code`) before the first run:
- `count_na2.py`, `count_ur3_v2.py`;
- `make_crops.py`, `synth.py`;
- `align.py`, `score.py`.

**Steps and CPU:**

| Step | CPU | How it runs |
|---|---|---|
| ORACC, Dencker and ATF counts | seconds | inline |
| Fetch CDLI photos (about 70: 60 S1 + 10 calibration, plus §5.4 extras) and Yale IIIF full-size (60) at 1 req/s | about 3-5 min wall time, network-bound | **detached** (nohup + perl setsid), coordinator launches |
| `synth.py`, 400 lines plus 200 null replicates | about 1-2 min, 1 core | inline or detached |
| Agent boxing: about 130 tablets plus 40 synthetic lines, 2 raters; the §9 downsampled re-score is a second round, only if K0 passes | agent time, not CPU | coordinator launches the rater agents |
| `score.py`: residual model, AUC, 2,000 bootstraps, 1,000 shuffles, 2 scripts | under 1 min, 1 core | inline |

- **Logging.** Long jobs write `HEARTBEAT <utc> stage=<name> done=<k>/<n>` to `experiments/layout_word_division/run.log`. The log is checked by hand, with no watcher task.
- **Python.** Every interpreter call uses `python -I`, with `nice -n 10`.
- **No compute lock is needed.**

## 13. Risks

1. **Biggest risk: no blind measurer good enough** (G2 fails, so INCONCLUSIVE).
   - Cuneiform gaps are small: often under 0.1 of sign height, and often negative.
   - Agent boxes with ±5-10 px error on 55 px signs are about the size of a typical gap, and could swamp a real cue. The drafter agrees with the reviewer that G2 at ICC ≥ 0.70 may be out of reach; that outcome is INCONCLUSIVE, and the bar stays.
   - `plate_corpus` showed agents mis-segment Indus signs. The 180° rotation may make segmenting harder still.
   - If G2 fails, the study ends without a verdict, and only the non-blind, partial Dencker S1 AUC is reported (record-only).
2. **Strict G1.** G1 needs both raters to match the sign count exactly and to agree in order. This may drop more than 40% of lines, which also ends INCONCLUSIVE.
3. **Both scripts are cuneiform** (D1). A PASS is shown within cuneiform only.
4. **Sign identity confound.** Some signs are wide at one end, and boundary signs (determinatives, numerals, word-final syllables) are not random. A pass may partly reflect shape rather than intended spacing.
   - §6.4(d) controls numerals, determinatives and S1 logograms. The per-sign-pair breakdown is reported.
   - For an Indus use, any cue helps, but the claim is worded as "gaps predict boundaries", not "scribes spaced words".
5. **Logograms and determinatives in Sumerian blur what a "word" is.** ATF spacing is the editors' segmentation, and the numeral splits are editorial. It is the label used, as stated.
6. **Expected result.** The drafter's guess is AUC 0.55-0.65 in S1, with S2 lower (dense administrative lines), and a PASS chance of about 20-30%.

## 14. Decisions put to the project lead (v1; all ruled, see the next section)

- **D1. The pair.** Accept two cuneiform traditions (NA Akkadian and Ur III Sumerian) as the "two scripts"? The alternative is to count Sanchi and Bharhut Brahmi donative labels to bring Brahmi over M1, which needs a new count and plates of uncertain resolution.
- **D2. Rater models.** Opus 5.5 = A and Fable = B, with Sonnet as backup?
- **D3. The bar.** The rule is point AUC ≥ 0.65 **and** lower bound ≥ 0.58. Is the second condition wanted, or point ≥ 0.65 with p < 0.01 only?
- **D4. `foreign_transcribe3`.** Mark it superseded, or keep BAHRAIN-02 as a separate small study?
- **D5. S1 primary.** Should the Dencker expert boxes (not blind) be the primary for S1 if G2 passes only narrowly, or stay secondary as drafted?

## Decisions, ruled 2026-11-25 (project lead, before review)
- **D1.** Neo-Assyrian and Ur III Sumerian are accepted as the two scripts. Because both are cuneiform, every reading must say "shown within cuneiform only". A pass does not show the cue carries across script families. Ashokan Brahmi is noted as the next script if an open source reaches 30 objects.
- **D2.** The two raters are fresh Opus and Fable agents, each blind to the transliteration and to the other.
- **D3.** The lower-bound condition stays in the bar.
- **D4.** `foreign_transcribe3` is superseded. Its draft is kept, marked "superseded by layout_word_division before sealing". Its blind-rater protocol is reused; its drawings are not.
- **D5.** The blind agent measure is primary. The Neo-Assyrian expert boxes serve as the validity check and as a record-only second measure.
