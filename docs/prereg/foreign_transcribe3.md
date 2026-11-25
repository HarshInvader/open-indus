# Three foreign objects with open drawings: can two blind mappers agree on their signs? (foreign_transcribe3)

**Status: SUPERSEDED before sealing (2026-11-25)** by `docs/prereg/layout_word_division.md`. The prior-art check found that all three objects are already in the 54-row foreign corpus: UR-07 has a published reading, UR-09 is probably UR-05, and only BAHRAIN-02 might be new, from a 3.4 px/mm drawing. The blind-rater protocol is reused there. Nothing was run.

**DRAFT v1, unsealed.** Written 2026-11-25. No mapper has been started and no score has been computed. Brief 11, study 7. Agent `paper`.

The drafter has seen the whole of Fig. 4 (below), including the five K0 drawings and the three target drawings, but has not mapped any sign in them. The mappers will not see this file.

## Question

Can two blind mappers agree on the signs of UR-07, UR-09 and BAHRAIN-02 from the open drawings found by `gulf_seal_hunt2`?

## 1. Prior art: which of the three already have a published reading

All checks used open sources fetched with a generic user agent. "(unverified)" means the source exists, but no open copy was opened.

| Object | Concordance | Published sign reading | Status |
|---|---|---|---|
| UR-07 | Laursen no. 20 = Gadd 1932 no. 15 = U.8685 (Penn) | **Yes.** Mahadevan 1977, M77 text 9845: `M175-M1-#-M59-M51-\|-M374` (6 positions, 1 damaged, 2 lines). It is in `data/m77_texts.jsonl` and in our row. Legrain, Museum Journal 1929 pl. xli, has a photo (unverified: Penn's site returns 403). Parpola 1994b and CISI 3.1 probably include it (unverified). | **Not a new transcription.** At most an image check of the M77 reading. |
| UR-09 | Laursen no. 17. The paragorth concordance (`sources/paragorth_Indus-/data/gulf_seals.csv`) gives Gadd 1932 pl. I no. 3 = BM 122946 = U.17342. | **Probably yes.** Our row UR-05 is ICIT 3899.1, a round Ur seal read `W350-W090-W004-#-#`. Its note already says "Gadd 1932 no.3 (U.17342)?". Gadd's text says no. 3 is under half preserved and has a "man" sign with a branch-like appendage, which fits W350 in first place. M77 9833 (`M1-#-M157-M97`) is Gadd 3 or Gadd 5 (the OCR is ambiguous). | **Probably a duplicate of UR-05, not a new text.** The identity is not proven. See §6. |
| BAHRAIN-02 | Laursen no. 6 = Kjaerum 1994 fig. 1726 (Qala'at al-Bahrain) | **None in any corpus we hold** (ICIT, M77, paragorth). Laursen 2010 notes that only the "twins" sign is legible. Parpola 1994b, the catalogue in the same Qala'at volume, may give a reading (unverified: no open copy). CISI 3.1 too (unverified). | The only possibly new transcription. Its drawing keeps very little script. |

**Correction to the brief.** All three objects are already rows among the 54 in `experiments/foreign_corpus/foreign_corpus.csv`. UR-09 and BAHRAIN-02 are rows with 0 legible signs. So the row count does not go from 54 to 57. This study can change three things only:
- texts with at least 1 legible sign, now 45;
- texts with at least 2 legible signs, now 41 (the order tests need 2);
- the row count, which can only go down: to 53 if UR-09 is merged into UR-05.

The most it can add is 2 texts with at least 2 signs: UR-09, if it is not a duplicate, and BAHRAIN-02. UR-07 already has 5 legible signs.

## 2. Images and licences

| Item | Source | Licence | Use |
|---|---|---|---|
| Fig. 4 of Vidale, Desset & Frenez 2021, "The Jalalabad seal, a reappraisal", JARCS 12(4), p. 10 (journal p. 292). It redraws the Gulf-seal compilation "from Laursen 2020", with Laursen's numbers. | https://jarcs.ut.ac.ir/article_81265_f85f962ddf0a7a91b4da2c938352e375.pdf (landing page https://jarcs.ut.ac.ir/article_81265.html) | The journal page says the article is under CC BY 4.0. **The figure is reproduced from Laursen 2020**, a Government of Sindh conference volume with no open copy. Laursen 2010 (Wiley) holds the earlier version of the drawings. Whether CC BY covers this third-party figure is unclear. | **Agent viewing only. Never published,** neither the figure nor any crop. |
| M77 sign drawings, `data/sign_images/M{n}.png` (417 signs) | Mahadevan 1977 (ASI), already in the repo | Not an open licence; the path is gitignored | Mapper reference only |

- PDF sha256 `4df149e756b64b2696f1a14865939791747eb8b4e65b5cc8f8e68a86df480d9e`. It is byte-identical to `experiments/foreign_corpus/raw/jalalabad_2021.pdf`, which is gitignored.
- The figure was extracted with `pdfimages -f 10 -l 10 -png`, which gives the embedded image at native pixels: 892 x 849, sha256 `9e724f71317eabc9514beffcb3f7bddb81b9ce20499e4835c48672b0a43f649b`.
- **Resolution.** The 5 cm scale bar is 169 px, so the figure is **3.4 px/mm**. Each seal is about 85 px across, and a sign is about 8-15 px. That is the same true detail as the plate scans that failed in `plate_corpus` (3.6 px/mm), but here it is black-on-white line art, not a halftone photo.
- The numbering checks against our concordance:
  - no. 24 shows two "men" and a fish, which is Gadd 18;
  - no. 56 shows twins, a motif and twins, which is BAHRAIN-05;
  - no. 28 is the Linear Elamite seal, as paragorth lists it.
- **Storage.** Downloads and crops go in a new empty directory outside the repo. Their only copy in the repo tree is under `experiments/foreign_transcribe3/raw/`, which `experiments/*/raw/` keeps out of git. Only text (mapper JSON, hashes, scores) is committed.
- **No other open drawing was found.** Penn and British Museum object pages return 403 to scripts. Wikimedia Commons has no photo of any of the three. archive.org has CISI vols. 1-2 only. These were not used.

## 3. Crops (frozen)

`make_crops.py` will be committed next to the scorer and hashed with it. It does the following:
1. Cuts each drawing from the extracted figure by the box below (x0, y0, x1, y1, inclusive) plus a 3 px pad.
2. Whitens the printed catalogue number. That is any 8-connected component of pixels < 250 that does not touch the crop's largest dark component and lies wholly in the right quarter and bottom quarter of the crop.
3. Saves the crop at native size and at 4x nearest-neighbour. Nearest-neighbour adds no detail.

| Object | Role | Box | Crop sha256 (native) |
|---|---|---|---|
| UNPROV-01 | K0 | 263,150,346,233 | `fadbbbfc358241ca7be5b2d8bf31d6970cee3c87df74c96dd409ba8d878b348b` |
| UR-02 | K0 | 259,502,339,580 | `92a526b95fd02c6cbc520db7ecabb03e493c455eb5302e4bdd5fc1d0347ae27d` |
| GIRSU-01 | K0 | 258,272,339,353 | `1055ef6b3c61b6f6a62645c7987a383847c57559523ed877c7ced2be9afe1cfd` |
| UR-01 | K0 | 257,385,343,463 | `35c10b07a55e200ff955786c3ed258559c0f0b948953e298ef18b996e070e539` |
| UNPROV-08 | K0 | 487,278,566,361 | `a704267786c1553f522c8f9dbaf820d6319edea32e0fa408e1470c4282bf3d1e` |
| UNPROV-02 | K0 reserve | 608,284,719,397 | `93bd8ff3c55c63161612e04f7af73948c8153b3bd550d262f369227d15577baf` |
| UR-07 | target | 483,152,564,232 | `960be28c94e4ecabaee02c08eda8b7373450e95ef9f6df2c87eb13da2e216c22` |
| UR-09 | target | 479,390,567,433 | `ea772abecab1fc2f8148cd448c6c94f55cff43c2ecfdc4262b78214d43789b89` |
| BAHRAIN-02 | target | 623,725,709,817 | `da7437981eccf5fdfa8dcd7e8c2318228d6b178e215ea6f102195613329b0262` |

The drafter checked by eye that no crop shows a catalogue number or another seal's drawing.

## 4. K0, the kill test (run first, same session as the main step)

### The five objects: frozen selection rule
1. **Pool.** Rows of `foreign_corpus.csv` that meet all of these:
   - (a) the Laursen number is drawn in Fig. 4;
   - (b) the row has an M77 text number and `m77_seq_as_published` has no `#` or `?`, so the print is complete and native in the sign list the mappers use, with no bridge;
   - (c) the row is not one of the three targets;
   - (d) the note does not start with PICTORIAL.

   Rule (b) is about whether the print can be scored, not about how hard the drawing looks.
2. **Order.** Sort the pool by sha256 of the string `foreign_transcribe3:K0:<id>` in ascending order. Take the first five. The sixth is the reserve.
3. **Result.** The pool is 6. The five, in hash order:

   | Object | Laursen no. | M77 text | Print, M77 reading order | Positions |
   |---|---|---|---|---|
   | UNPROV-01 | 23 | 9901 | M178-M53-M97-M342-M342 | 5 |
   | UR-02 | 21 | 9846 | M171-M387-M97-M341-M107 | 5 |
   | GIRSU-01 | 22 | 9852 | M51-M103-M345-M307-M342 | 5 |
   | UR-01 | 16 | 9832 | M254-M74-M297-M184-M3 | 5 |
   | UNPROV-08 | 25 | 9903 | M18-M102-M59-M98-M294-M134-M89 | 7 |

   The reserve is UNPROV-02 (9902). The five prints have 27 positions in all.
4. **Comparable quality.** All five come from the same figure, draftsman, scale and pixel density as the targets.
5. **Known print disputes are kept, not cleaned.** These make K0 harder, not easier:
   - Gadd counts four signs on UR-02;
   - paragorth notes one more sign in the GIRSU-01 drawing than in ICIT;
   - Laursen says "about 6" signs for UNPROV-08.

### Mappers
- Two fresh agents, each run once. The drafter proposes these models:
  - **Mapper A: Opus 5.5.**
  - **Mapper B: Fable.** A different model family should make the two mappers' errors less correlated.
  - **Backup for either: Sonnet,** used only under fallback R3.
- **What a mapper gets.** A new empty working directory outside the repo containing:
  - the protocol sheet (§9) and nothing else from this file;
  - the 8 crops (5 K0 and 3 targets) at native size and 4x, renamed `C1`…`C8`;
  - `data/sign_images/M*.png`.
- **Labels.** Each mapper gets its own label order: sort by sha256 of `foreign_transcribe3:crop:<A|B>:<id>`. The key file from label to object is written by the drafter and hashed before the mappers start. Neither mapper knows which crops are K0.
- **What a mapper does not get.** No repo access and no web access. It never sees:
  - this file or the CSVs;
  - M77 or ICIT data;
  - the article text or catalogue numbers;
  - the other mapper's output.
- **Hashing before scoring.** Each output file is hashed into `docs/prereg/HASHES.txt` (tags `foreign_transcribe3_mapA` and `foreign_transcribe3_mapB`) before the scorer reads it. This is the reading gate of `anchor_objects.md` §1: two readers, readings hashed before any comparison.

### Alignment and score (exact)
- **Tokens.** A mapper gives, per crop, a list of lines. Each line is a list of tokens in visual order, left to right:
  - an M number such as `M97`;
  - `?` for a sign that is seen but matches no M number;
  - `#` for a position that is damaged or unreadable.

  The scorer joins the lines in the order given. `|` in prints is dropped.
- **Match.** Two tokens match only if both are the same M number. `?` and `#` never match.
- **Alignment of X and Y.**
  - A global DP that maximises the number of matches, with match = 1, mismatch = 0 and gap = 0.
  - Ties go to the diagonal step first, then to a gap in Y, then to a gap in X.
  - `m(X,Y)` is the number of matched columns.
  - `n(X,Y) = max(len X, len Y)`, counting `?` and `#` tokens. Missing or extra signs therefore count against agreement.
- **Mapper against print (direction).** The mapper's joined list is aligned to the print as given and also reversed. The higher `m` is kept, with ties going to reversed (impressions read right to left). Each mapper's direction is chosen separately and recorded.
- **Mapper against mapper.** No reversal, because both lists are in visual order.
- **Mirror images.** The sheet tells mappers that a drawing may show the seal face, so a sign may appear left-right mirrored, and that they map it to the same M number. The scorer does nothing about mirroring.
- **K0 rates.** For each of the three pairs, A–B, A–Print and B–Print, the scorer sums over the five objects: `R = Σm / Σn`.

### K0 rule
- **PASS** if all three pooled rates are ≥ 0.80. For the two print pairs, Σn ≥ 27, so each mapper must match at least 22 of the 27 print signs.
- **FAIL** otherwise. **Nothing is transcribed.**
  - The target outputs, already hashed, are not scored and not looked at by anyone.
  - The three rows stay as they are.
- Per-object rates are reported for both outcomes, as description only.

### Fallbacks, fixed now (any other change after the mappers start makes the study INVALID)
- **R1. Bad format.** An output that does not parse, or that omits a crop: the same model is re-run once as a fresh agent with the same bundle. A second failure is a K0 FAIL.
- **R2. Bad crop.** If a crop shows a catalogue number or part of another drawing, it is fixed before any mapper starts. For a K0 object the fix is the reserve UNPROV-02. For a target the box is re-cut by the same rule with a larger box. This check is made only before the mappers start.
- **R3. Model unavailable.** If a proposed model cannot be run on the day, Sonnet takes its place. Nothing else changes.
- **No second K0.** If K0 fails, no other set, model, resolution, crop or scoring rule is tried. A better image source, such as CISI 3.1, a museum photo or Laursen 2010, needs a new prereg.

## 5. Main step (only if K0 passes)

- **Per target object.** Align A and B as above.
  - **Merged reading:** one token per alignment column. A column gives the agreed M number if it is a match and `#` otherwise. The merged reading keeps the visual order and is written in visual order.
  - **Object rate** = m / n.
- **Reading gate** (`anchor_objects.md` §1):
  - **An object with rate ≥ 0.80 passes.** Its agreed signs enter the foreign corpus as specified in §6. Disagreed positions stay `#` (unread).
  - **An object with rate < 0.80** is recorded as "unreadable at this resolution". Nothing from it enters.
  - An object where both mappers give no M number at all has rate 0 and fails.
- **Reading direction is not decided here.** It stays as the corpus has it, or "not checked".

## 6. Frozen readings for every outcome

| Outcome | What is written to the corpus | What it means |
|---|---|---|
| K0 FAIL | Nothing. Rows unchanged. RESULTS says "agent mappers cannot read these drawings at 3.4 px/mm to the 80% bar". | Blind agent mapping of the Laursen drawings is not usable. Any further transcription needs a better image or a human reader. |
| K0 PASS, target fails the gate | That row is unchanged and noted "unreadable at this resolution (foreign_transcribe3)". | |
| K0 PASS, **UR-07** passes | The M77 reading stays the row's sequence. The new column `drawing_check` gets "two blind mappers, Laursen 2020 drawing: agreed k signs; agreement with M77 9845 = m/n" (same scorer, both directions). If m/n ≥ 0.80, `verified_against_image` becomes "checked vs Laursen 2020 drawing (2 blind mappers)". Otherwise the reading is marked "disputed: drawing vs M77". | An image check of an existing print, not a new text. |
| K0 PASS, **UR-09** passes | The merged reading is compared with ICIT 3899 (UR-05) through `bridge_WM.json`. A UR-05 sign matches if the mapped M number is in that W sign's bridge list. The best direction is used, with `#` never matching. **If at least 2 of UR-05's 3 legible signs align in order, UR-09 is recorded as a probable duplicate of UR-05** and the rows are merged under UR-05, giving 54 rows → 53 (the order flags are not re-run). If not, UR-09 gets the merged reading, `seq_origin` = "foreign_transcribe3", and `n_legible` = the agreed count. | A duplicate is the more likely result, given the concordance. |
| K0 PASS, **BAHRAIN-02** passes | The merged reading, `seq_origin` = "foreign_transcribe3", and `n_legible` = the agreed count. It enters the order tests only if n_legible ≥ 2. | The only possibly new text. |

- **For every outcome:**
  - **It adds nothing to the 2027 bar.**
  - No order test, crib test or forward prediction F1/F2 is re-run by this study. F1 and F2 need 8 new texts.
  - The foreign corpus row count stays at 54 or falls to 53.
  - Texts with ≥ 2 legible signs go from 41 to at most 43.
- Readings enter as M numbers. `seq_wells` is filled only through the existing bridge, and an unbridged sign is written `?`, as in `build.py`.

## 7. Scoring code (written later, hashed before it runs)

- **Files.** `experiments/foreign_transcribe3/score.py`, with `make_crops.py` and `prints.json`. `prints.json` holds the five K0 prints and the UR-07 and UR-05 prints, copied from the CSV by the script, which records the CSV's sha256.
- **Hash first.** All three files are hashed into HASHES.txt (tag `foreign_transcribe3_code`) before the first run.
- **Run.** Detached, with `nohup` and `perl -e 'use POSIX; setsid(); exec @ARGV'` around `nice -n 10 python -I score.py`. The log is written to `experiments/foreign_transcribe3/run.log`. It is checked by hand; no watcher task.
- **What `score.py` computes, in order:**
  1. **Heartbeat.** `HEARTBEAT <utc> stage=<name> done=<k>/<n>` at the start of each stage and after each object.
  2. **Checks.** It verifies:
     - the sha256 of every crop against §3;
     - the label key's hash, and the hash of both mapper outputs, against HASHES.txt.

     Any mismatch is a hard stop.
  3. **Parsing.** It parses both outputs and applies R1 (the bad-format rule).
  4. **K0.** For each K0 object it computes `m` and `n` for A–B, A–P and B–P, plus the chosen direction. Then the pooled rates and the PASS/FAIL verdict.
  5. **Main step.** It runs only on PASS. For each target: the A–B alignment, the merged reading, the object rate and the gate verdict.
  6. **Comparisons.** They also run only on PASS, and only for targets that passed the gate:
     - UR-07 merged against M77 9845;
     - UR-09 merged against ICIT 3899 through the bridge, and against M77 9833, for description only.
  7. **Output.** It writes `results.json` and `ledger_rows.csv`. It does not edit `foreign_corpus.csv`. A separate commit applies §6 by hand from `results.json`.
- **CPU.** Seconds, on a single core.

## 8. Risks

1. **The biggest risk: K0 fails because agent mappers cannot read 8-15 px signs to exact M numbers.**
   - In `plate_corpus`, blind agent readers matched 23-36% of sign positions on photos of similar true detail.
   - Line drawings are easier than halftones, but M77 splits many signs into close variants (for example M97/M98, M1/M2 and the stroke groups). Exact-number scoring punishes every such split.
   - The drafter's estimate is 25-40% for PASS, below the brief's 60%.
2. **The print and the drawing may disagree** (see the disputes in §4). This lowers the A–Print and B–Print rates even when the mappers read the drawing well. It is kept on purpose: the bar is agreement with the print.
3. **Memorised readings.** A model might recall a famous seal's published reading. The anonymised crops and the missing catalogue numbers make this unlikely. A–B agreement on the targets is not checked against any print except UR-07's.
4. **The two print-direction tries** give the print pairs a small upward bias. The same rule applies to K0 and to every later comparison.
5. **Expected yield is small even on a PASS:**
   - UR-07 is already read;
   - UR-09 is probably UR-05;
   - BAHRAIN-02 keeps perhaps one or two signs.

## 9. Protocol sheet for the mappers (hashed with this file; the only text a mapper sees)

> You will see 8 small black-and-white line drawings of ancient stamp seals, files C1…C8 (native size and `_x4` enlarged), and a sign list: one image per sign, named M1…M417.
>
> For each drawing:
> 1. Find every written sign. Ignore the animal, the scene and the outline; they are not writing.
> 2. List the signs line by line, top line first, and within a line **from left to right as drawn**.
> 3. For each sign, give the one M number whose image is the same sign. The drawing may be a mirror image, so a sign may face the other way from the list; give the same M number anyway. Strokes that form one sign in the list are one sign.
> 4. If you see a sign but no M number fits, write `?`. If a position is broken or too unclear to identify, write `#`. Do not guess between two numbers; pick one or write `?`.
> 5. Give a confidence (high, medium or low) for each token.
>
> Work alone. Do not search the web or any files other than those given. Return only this JSON:
> `{"mapper": "<A|B>", "crops": {"C1": {"lines": [[["M97","high"], ["#","low"]], [...]], "note": "<optional, one line>"}, ...}}`

## 10. Decisions needed before sealing

1. **Mapper models.** Opus 5.5 for A, Fable for B, Sonnet as backup?
2. **Exact M numbers, or M77 variant groups.** The default is exact numbers, as in `anchor_objects.md` §1. Group-level matching would raise the K0 odds but loosen the gate.
3. **Should UR-07 and UR-09 stay in the study,** given their prior prints (UR-07 is not a new transcription; UR-09 is probably a duplicate)? The alternative is to run BAHRAIN-02 alone, though K0 costs the same either way.
4. **Is a K0 pool of 6 acceptable?** It has 27 print positions, which gives a 95% interval of about ±15 points on each rate.
