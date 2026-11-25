# Lexicon ceiling: on real Old Assyrian text, does the true key gain anything when the lexicon comes from the same archive?

Status: **v2, sealed 2026-11-25** (tag `lexicon_ceiling`). v2 applies a fresh review of v1 and the project lead's rulings (see "Decisions, ruled" and the review log). No study code existed and nothing had been scored at sealing. Study 4 of `docs/fable_brief11.md`. Main line (a), the claim bench. Kind ii/iii (a read script used as a known-answer control). Label-free counts were run before this draft with scratch scripts outside the repo; every one is disclosed under "What was seen before this draft".

## Coordinator's ruling
- **This is a new study with its own prereg.** It does not reopen the frozen stop of `certify_size_curve`.
- That study's result and its reading 3 stay exactly as they are. No file of that study is edited, rerun or regraded. Its modes `k1`, `real`, `extras` and `k4` are never called.
- This study adds no new score. It runs the sealed `lift_score` score, unchanged, with a different word list. So the one-attempt rule of `lift_score` is not touched.
- No Indus key is scored and no Indus text is read.

## Question
- **On real Old Assyrian text, does the true key gain anything when the lexicon is built from the same archive, size-matched?**
- The same question in other words: is the restoration closure about lexicon distance, or about the score?
- "Gain" means the sealed gate: held-out restoration gain G of at least 0.02 nats per masked sign.

## Why
- `certify_size_curve` stopped at K0. Its results file says it cannot tell lexicon distance from corpus size, because the ceiling arm never ran.
- On real text the true key with the Neo-Assyrian lexicon had λ* = 0 in 21 of 23 record-only draws. G was at most 0 everywhere.
- A referee will ask whether the score works on real text at all. If it does not, the planted results say little about real text.
- **G is this study's gate. Hit@1 is the 2027-clause measure and is reported on every cell. A G pass alone does not meet the 2027 clause.**
- **Adds to the 2027 bar: nothing.** Indus has no matched lexicon under either reading. The study fixes the wording of one negative.

## Prior art
Opened 2026-11-25 with `curl -A "open-research-site/1.0"`. Full open-access text unless noted. Nothing behind a paywall or a bot block was opened.

**Lexicon-based decipherment of real text (established).**
- **Snyder, Barzilay and Knight 2010,** ACL. https://aclanthology.org/P10-1107.pdf
  - Ugaritic against a Hebrew lexicon with known Hebrew morphology. 29 of 30 letters mapped correctly. 60.4% of the Ugaritic word forms that have a Hebrew cognate are translated correctly.
  - Hebrew cognates exist for 2,155 word forms, about a third of the Ugaritic vocabulary. The rest include "many personal and geographic names".
  - The score is cognate accuracy against a gold list. No held-out restoration and no test of a stated key against keys with no language.
- **Berg-Kirkpatrick and Klein 2011,** EMNLP. https://aclanthology.org/D11-1029.pdf
  - Matches two lexicons by edit distance under a learned alphabet map. On Ugaritic: 90.4% lexicon accuracy and 28 of 33 character mappings.
  - Both lexicons hold only words that have a cognate (2,214 pairs). The authors say this is an easier task than Snyder's.
- **Luo, Cao and Barzilay 2019,** ACL. https://arxiv.org/pdf/1906.06718
  - Ugaritic: 93.5% with cognates only, 65.9% with unpaired words on both sides. Linear B: 84.7% on 919 cognate pairs, 67.3% when the Greek side is 455 proper nouns.
  - The drop from the clean to the noisy setting is the nearest published number to "how much does a matched word list matter".
- **Luo, Hartmann, Santus, Cao and Barzilay 2021,** arXiv 2010.11054. https://arxiv.org/pdf/2010.11054
  - Undivided text. Gothic (40,518 tokens): P@10 is noticeably higher with Proto-Germanic as the known language than with Old Norse or Old English. The authors conclude that "choosing a close known language is vital for decipherment".
  - So a gain that falls with lexicon distance is established for cognate search. It ranks languages. It does not test a stated key.
- **Berg-Kirkpatrick and Klein 2013,** EMNLP. https://aclanthology.org/D13-1087.pdf — kept for its warning: a wrong key can reach a higher likelihood than the gold key.

**Held-out restoration with in-domain training (established at large size).**
- **Assael, Sommerschield and Prag 2019** (Pythia), EMNLP. https://aclanthology.org/D19-1668.pdf — Greek inscriptions restored by a model trained on the same corpus: 30.1% character error against 57.3% for human experts. A model with the 100,000 most frequent words of the corpus as input did best.
- **Lazar and others 2021,** EMNLP. https://aclanthology.org/2021.emnlp-main.384.pdf — about 10,000 Oracc tablets, 2.3 million signs; 89% Hit@5.
- **Fetaya and others 2020,** PNAS, read at https://pmc.ncbi.nlm.nih.gov/articles/PMC7502733/ — the article notes that "many texts survive in duplicate copies" and that experts restore from them. That is the leak this study has to shut out.
- A keyword search of these three found no rule that removes duplicate copies between training and test texts (weak evidence; the search was short).
- Assael and others 2022 (Ithaca), Nature **(unverified:** not reopened today; see the sealed `certify_size_curve` prereg).

**Verdict.**
- **Established, and not tested here:** a lexicon of a close language supports decipherment of real text; the result gets worse as the lexicon gets more distant or noisier; restoration models trained on the same corpus restore well at large size.
- **Not found:** a held-out restoration gain from a stated key plus a same-archive word list, over a sign n-gram, at 8,000 tokens; the same with the held-out texts' own tablets and near-copies shut out; controls with letter-permuted word lists.
- The search was short. "Not found" is weak evidence that this is new.

## What was seen before this draft
- **Sealed results:** `lift_certify`, `lift_score`, `certify_size_curve` (its `RESULTS.md`, `kill.out` and `kill.json`).
  - From `kill.json`, real text with the **Neo-Assyrian** lexicon at 1 u: G, λ*, D and the trigram's Hit@1 for all 20 draws (G = 0 in 18, −0.021 and −0.008 in two; D from −0.067 to +0.012; trigram Hit@1 11.4 to 18.9%).
  - From `kill.json`, the K0a full-dose plants: the five letter-permuted lexicons' G on each plant. This bears on the control rule below and is quoted there.
  - Per-cell wall times, used for "Cost".
- **Label-free counts, 2026-11-25,** two scratch scripts outside the repo. Single process, `nice -n 20`, the project interpreter with `-I`, about 10 seconds each. No compute lock was taken.
  - They load the sealed `certify_size_curve/run.py` by path and call only its label-free parts: the corpus build with the ceiling word counts, and the ceiling list builder.
  - They produced only: pool counts; ceiling word and skeleton counts; per-draw list sizes, shortfalls, source-tablet counts and the tablet count of the last-ranked word; counts of identical lines shared between tablets; counts of two catalogue fields.
- **Reviewer's label-free shingle check (seen for v2).** The reviewer compared source tablets with held-out tablets by shingles of 6 signs that run across line breaks. No lexicon was matched and nothing was scored.
  - Copies that exclusion 2 misses, at a shingle overlap of 0.5 or more: 8 outside tablets over the 20 draws. They contribute 0 list words of which they are the only source.
  - At an overlap of 0.3 or more: 128 tablets, contributing 1 such word.
- **Not seen:** any G, D, λ*, Hit@1 or word-model fit with a ceiling lexicon, on any text, real or planted. No ceiling lexicon was matched against any text. The overlap of the ceiling list with the Neo-Assyrian list was not counted. No planted text was built. Nothing was run on Indus text.
- The scratch scripts are not the study code. The study code must recompute the "Measured" numbers below before any gain (abort A2).

## Count gate
**Need:**
1. The 20 sealed 1 u draws of pool T, each with its tablet ids.
2. For each draw, a same-archive word list that uses no tablet of the draw and matches the primary list's size at every length: 1,612 / 896 / 259 / 48 skeletons at 4 / 5 / 6 / 7 consonants.
3. At least 900 clean held-out positions per draw (sealed F4).

**Have (measured today with the sealed code):**

| item | found |
|---|---|
| Pool T | 4,435 texts, 73,135 lines, 445,733 tokens, 207 sign types, 3,951 tablets with a chunk. Equal to the sealed A2 figures. |
| Tablets with at least one usable word of 4 to 7 consonants | 3,821 |
| Such word tokens, whole pool | 40,322 |
| Skeleton types at 4 / 5 / 6 / 7, whole pool | 1,967 / 1,793 / 720 / 191 |
| Tablets in a 1 u draw | 58 to 86 (median 75.5) |
| Source tablets left for a 1 u draw, after both exclusions below | 3,730 to 3,761 |
| Source word tokens left for a 1 u draw | 39,305 to 39,540 |
| Types available outside a 1 u draw, smallest over 20 draws | 1,946 / 1,765 / 704 / 185 |
| **Draws with a shortfall at any length** | **0 of 20** (also 0 of 13 at 4 u and 0 of 3 at 16 u) |
| List size per draw | 2,815, as the primary list |
| Density at 4 consonants | 0.110, as the primary list |
| Clean held-out positions per draw (sealed `kill.json`) | median 1,594.5; one draw, number 16, has 895 |

- **Gate verdict: passes.** The size match of 1,612 / 896 / 259 / 48 is met in every draw.
- **Two things the gate shows that the sealed prereg did not state:**
  - The sealed prereg gave 1,985 / 1,824 / 733 / 195 types from an earlier scratch count. The sealed code is stricter (it drops any word group that touches a logogram span) and gives 1,967 / 1,793 / 720 / 191. The sealed code is what this study uses.
  - **The list is not a list of common words.** At 4 consonants it keeps 1,612 of about 1,950 types, so the last-ranked word occurs on one source tablet. The same holds at 5 and 6 consonants; at 7 the last-ranked word occurs on two. A single stray copy of a held-out tablet could therefore put that tablet's own rare words in the list. This is why the build below has a second exclusion.

## Data, key, text shape and scoring
**All as sealed in `docs/prereg/certify_size_curve.md`.** Listed here by name; that document's text governs.
- Pool T, the drop rule, the language rule, the sign list and its hash.
- Signs, breaks, the 11-letter alphabet and the true key (the modal value of each sign over pool T).
- Chunks of M77 seal lengths, the one tablet order, 1 u blocks, the hashed split by tablet, the five hashed folds.
- Masking, candidates, the trigram, the word model, the λ grid 0, 0.25, 0.5, 1, 2, 4, the 0.01-nat margin, G, D, the clean rule, the clustered standard error.
- The five letter permutations (sealed seeds), the five shuffled keys per draw, the unigram scramble, the Markov filler.
- **Draws: the sealed 1 u draws 1 to 20** (blocks 0 to 19 of the one tablet order). They are the draws of the sealed record-only K3 cell.
- The primary Neo-Assyrian list enters only as the size target (four counts) and in abort A1.

## The ceiling lexicon and the leakage control (frozen)
**Leakage is the central risk.** A word list from the same archive could hold the held-out texts' own words. The build shuts that out in two steps, and four checks verify it.

### Build, for one draw
1. **Text id.** A text's id is its tablet's CDLI id (the P number). Every chunk carries it. A "tablet & envelope" object has one id, so both parts fall in the same block and on the same side of the split.
2. **Exclusion 1, by text id.** The source is every kept line of every pool T tablet whose id is **not in the draw's block**. Both halves of the block are out: the held-out half and the development half.
3. **Exclusion 2, near-copies (new in this study).** A tablet outside the block is also dropped from the source if it shares **3 or more identical kept lines of 5 or more signs** with any one tablet of the block.
   - A line is compared as its transliteration text after the marks `< > ! ? *` are removed and runs of spaces are made one space. Its sign count is its count of syllabic readings and determinatives.
   - Measured: this drops 2 to 19 tablets a draw (median 8) and changes 0 to 12 of the 2,815 list words. In the whole pool 2,436 such lines occur on two or more tablets.
   - Reason: letters and contracts exist in copies under other ids. Exclusion by id alone would let a copy through.
4. **Words, skeletons, ranking and size match: the sealed rule, unchanged.** A word is one space-separated group of hyphen-joined readings, used only if every part is a syllabic reading with a sign-list entry and a key value. Words with a logogram, numeral, determinative, upper-case sign name or compound are out, and so are words on dropped lines. Its skeleton is the true key's values of its signs. Skeletons of 4 to 7 consonants are ranked by distinct source tablets, then token count, then alphabetically. The top 1,612 / 896 / 259 / 48 are kept.
5. Names are not removed (sealed).
6. The same five sealed letter permutations are applied to the draw's list to make its five permuted copies.

### Verification (all before any gain; any miss stops the study, abort A8)
- **V1, provenance.** For every kept skeleton the code holds the ids of the source tablets it came from. The union of those ids must share no id with the block and none with the near-copy set.
- **V2, a second build by deletion.** The list is built a second way: the block's tablets and the near-copy tablets are removed from the text file's rows before any word is read, and the list is built from what is left with no exclusion step. The two lists must be identical (same SHA-256 of the sorted list).
- **V3, canaries, on draw 1.** The canary has 4 consonants and occurs nowhere in the pool. It is added with a high count, in turn, to: (a) a held-out tablet of the block: absent. (b) A development tablet of the block: absent. (c) A synthetic copy of a held-out tablet, under a new id, sharing 3 long lines with it: absent. (d) The same copy sharing 2 lines: present. (e) One ordinary source tablet, same count: present. Cases (d) and (e) show the check can fail and that a one-tablet word does reach the list. The canary lists are thrown away and score nothing.
- **V4, the ledger.** `ledger.json` is written before any gain. Per draw: the count of block tablets, held-out tablets, near-copy tablets and source tablets; the list's SHA-256; the shortfall by length; the number of list words that occur on one source tablet only, by length.
- **A9, as sealed:** no set Q tablet enters the source.

### The leak dial (record-only)
- For each of the 20 draws, the true key is scored once more with a list built with **no exclusion at all** (the whole pool, the draw's held-out tablets included).
- It is a deliberate leak. It shows how large a leak would look on this score. It is never called a result and enters no reading.
- It runs after the graded cells.

### What the control does not remove
- Tablets outside a draw share senders, names, formulae and the archive's spelling habits with it. That is what "same archive" means, and it is why this is a ceiling.
- Copies that share fewer than 3 long lines with a block tablet.
- Joins catalogued under another id. 170 pool tablets have a join note in the catalogue; the notes were counted, not read.
- The true key is an oracle built over the whole pool (sealed). It carries sign values, not words. The permuted copies are scored with the same key.

## Kill tests, in this order
K0b runs first. It uses planted text only, so a K0a result can be read. K0a is the test that decides. **K0b tests the code path, not power:** the sealed quarter-dose plant already misses at 1 u (8 of 20), so a full-dose pass says only that the ceiling path can find a language that is there.

### K0b, the planted known answer
- **Five full-dose plants at 1 u,** on blocks 0 to 4. The sealed generator, with one change: the vocabulary is the first 500 words of a seeded order of **that block's ceiling list** (weights 1 / rank).
- Scored with that block's ceiling list.
- **Bars, as sealed K0a full dose:** true key **G ≥ 0.10 in 5 of 5**; true key on the unigram scramble **G ≤ 0.005 in 5 of 5**; five shuffled keys, **median G ≤ 0.005 in 5 of 5**.
- The five permuted copies are scored on each plant. They set the control rule (FC below) and grade nothing else.
- A miss on any bar: stop. No real-text cell runs.
- **Why it is useful.** The ceiling path is new code that the sealed run never executed. A K0a miss means nothing unless that path is shown to find a language that is there.

### K0a, real text (the test)
- The 20 sealed 1 u draws. For each: the true key with the draw's ceiling list; the true key with each of its five permuted copies; and the five sealed shuffled keys with the ceiling list.
- **T** = the number of draws where the true key's G ≥ 0.02 (sealed point rule).
- **P** = the number of draws that are a "permuted hit" under the control rule in force.
- **S** = the number of draws whose median shuffled-key G (the third largest of five) is ≥ 0.02. **The shuffled-key cell is graded and always runs.**
- **C** = the number of draws where the sealed bar C holds (true list above all five copies on the same positions).
- **Pass: T ≥ 16, P ≤ 1 and S ≤ 1.** S ≥ 2 gives reading 2.
- **Under P2, a pass also needs bar C in ≥ 16 of 20; otherwise reading 2.**
- **Control rule P1 (brief 11 as written, the strict reading):** a draw is a permuted hit if **any** of its five permuted copies has G ≥ 0.02.
- **Control rule P2 (the one fallback, FC):** a draw is a permuted hit if the **median** of its five permuted copies' G (the third largest) is ≥ 0.02. This is the form of the sealed shuffled-key bar.
- Both P counts and C are reported whichever rule is in force.
- Draw 16 has 895 clean positions. It is kept and flagged (sealed F4).

### Record-only cells
They grade nothing and enter no reading except as the printed sentences under "Readings". Run in this order, after K0a and its shuffled keys.
1. **Scramble, 1 u, 20 draws:** the true key on the unigram scramble, with the ceiling list.
2. **Leak dial,** as above.
3. **Filler, 1 u, 5 texts:** the sealed order-1 filler built on blocks 0 to 4, each with its block's ceiling list, true key.
4. **Counts (label-free; no score):**
   - the share of each draw's ceiling list that is also in the Neo-Assyrian list, by length;
   - the share of the draw's held-out word tokens of 4 to 7 consonants (sealed word rule) whose skeleton is in the draw's ceiling list, and the same share for the Neo-Assyrian list. It lets a fail be attributed: a low share points at the list, a high share at the score.

## Calibration fallbacks (written before any calibration)
Calibration here means: the λ grid, the K0b plant, the control rule, and the run's length. **These rules are the only changes allowed. Each is applied at most once and logged. Any other change after the first gain of any study cell is seen makes the study INVALID:** to the score, the grid, the margin, any bar, the draws, the key, the split, the clean rule, the ceiling build, either exclusion, the near-copy thresholds, the size match, the permutations, the control rules, the bars on P, S and C, the plants, the seeds, the bands of T, or anything else this document fixes. An invalid study is labelled so and is not rerun under this name.

- **F1, grid edge (sealed rule).** If λ* = 4 for the true key in 3 or more of the 5 K0b plants, the values 8 and 16 are added for every key in every cell. K0b is not regraded.
- **F3, plant too easy for the trigram (sealed rule).** If the trigram's Hit@1 on a K0b plant exceeds 60%, the plant vocabulary becomes 2,000 words, once, before any K0b gain is computed.
- **F4, thin draw (sealed rule).** A draw with fewer than 900 clean positions is kept and flagged. Draw 16 is known to be one.
- **FC, the control rule, set on the plants before any real-text gain.**
  - Count the K0b plants that are a permuted hit under P1.
  - 0 or 1 of 5: P1 is in force.
  - 2 or more of 5: P1 fires on a language that is in the text by construction, so it cannot be the control. **P2 is in force.**
  - If P2 also flags 2 or more of 5 plants: stop. No control is usable (reading 0c).
  - **Disclosed expectation.** On the sealed K0a plants (Neo-Assyrian list) the largest permuted G was 0.018, 0.023, 0.050, 0.024 and 0.034: P1 would have flagged 4 of 5 and P2 none. The drafter expects FC to choose P2.
- **FS, shortfall.** The gate found none. If the study code finds a shortfall in any draw, that is a count mismatch: stop (A2).
- **FT, time only.** Record-only cells are started in the order listed. No record-only cell is started after 4.5 h. Running jobs finish. K0b, K0a and the shuffled-key cell always run to the end. The rule reads the clock and no gain.
- **Not permitted, as examples:** another lexicon or a pooled one; removing names; a list of another size; another near-copy threshold after a gain is seen; grading the leak dial or Hit@1; a run at 4 u or 16 u; a third control rule; moving 16, 4 or 0.02; adding draws; rerunning K0b or K0a.

## Readings (frozen)
Exactly one of 0a, 0b, 0c, 1, 2, 3, 4 applies, the first in the list whose condition holds.

- **0a. An abort or a verification check stops the run.** No reading. The stop is reported.
- **0b. K0b misses a bar.** "The pipeline did not find a language planted from the ceiling list (bar named). Nothing is learned about real text."
- **0c. FC finds no usable control.** "Letter-permuted copies gain on planted text under both rules. The real-text question cannot be asked with this control."
- **1. Pass: T ≥ 16, P ≤ 1 and S ≤ 1; and, if P2 is in force, C ≥ 16** (brief 11, frozen): **"The score works on real text with a matched lexicon, so the limit for Indus is that no matched lexicon can exist."**
- **2. Not specific: T ≥ 16 and reading 1 does not hold** (P ≥ 2, or S ≥ 2, or P2 in force with C ≤ 15). "A same-archive word list raises restoration on real text in T of 20 draws, but the controls do not hold: letter-permuted copies gained in P of 20, shuffled keys in S of 20, and the true list beat all five copies in C of 20. The gain is not shown to be the lexicon's or the key's. The score is not shown to work on real text."
- **3. Fail: T ≤ 4** (brief 11, frozen): **"This score has no power on real text even with the best lexicon, so restoration is untested, not closed."**
- **4. Partial: T from 5 to 15.** "With the best lexicon the score gains on real text in T of 20 draws, under the 16 needed. It has some power on real text and too little to certify. Lexicon distance explains part of the real-text null and the score explains the rest; this study cannot size the two." If P ≥ 2 or S ≥ 2: "Permuted copies gained in P of 20 and shuffled keys in S of 20, so even this part is not shown to be the lexicon's."

**Added to every reading from 1 to 4, deciding nothing:**
- "G is the gate. Hit@1 lift was (range, median). A G pass alone does not meet the 2027 clause."
- "The rule in force was (P1 / P2). Under the other rule P was (value). Bar C held in C of 20. S was (value)."
- "The true key on the scramble reached 0.02 in (count) of 20 draws." Or: "The scramble cell did not run (FT)."
- "With the draw's own tablets left in the source (a deliberate leak), median G was (value) against (value)."
- "The dose D with the ceiling list was (range); with the Neo-Assyrian list it was −0.067 to +0.012; on the sealed quarter-dose plants −0.078 to −0.021; on the full-dose plants 0.20 to 0.26."
- "On the order-1 filler the ceiling list gave G (values)."
- "The ceiling list held (share) of the held-out word tokens of 4 to 7 consonants; the Neo-Assyrian list held (share)."
- "This is one script, one archive and an oracle key. The list was built with the editors' word division and holds names. It is an upper bound that no claimant could hold."
- "The result and reading of `certify_size_curve` are unchanged."
- "No Indus key is scored. No outcome supports or counts against any Indus key, and none licenses a run of one."

**Coverage.** T is a whole number from 0 to 20. Readings 1 and 2 split T ≥ 16 on the controls (P, S and, under P2, C); reading 2 is everything in T ≥ 16 that is not reading 1. Reading 3 takes T ≤ 4 and reading 4 the rest. So every outcome of K0a has one reading.

**Atlas wording (decision 5).** After a fail the atlas carries brief 11's reading: "this score has no power on real text even with the best lexicon, so restoration is untested, not closed". The `certify_size_curve` and `lift_score` entries get a pointer line. Their sealed readings are not edited under any outcome.

## Indus rule
- No Indus step is run. M77 supplies text lengths only, as sealed.
- No Indus key is scored on any text. No M77 sign is masked or restored. The code must not load `splits_v2` or any key file from the claim bench.
- No outcome licenses a run on Indus.

## Code reuse
- New file `experiments/lexicon_ceiling/run.py`, one mode (`kill`). It loads the sealed `experiments/certify_size_curve/run.py` by path and first checks that file's SHA-256 against its sealed code tag in `docs/prereg/HASHES.txt`. The sealed file is not edited.
- **Used unchanged, by calling the loaded module:** the corpus build and true key; the block, split and fold functions; the clean index; the trigram; the word model, EM and LLR; the evaluation of one key on one text (λ*, G, D, Hit@1, clustered SE); the letter permutations; the sealed ceiling word rule; the memory guard and lock check; the seal check.
- **Copied, not called.** The sealed plant generator, scramble, filler and shuffled-key functions hard-code base 20270201 and the primary list, and the sealed `job_cells` calls the sealed builder without exclusion 2. **These functions are copied with base and list as parameters; no name of the loaded module is assigned.** The ceiling builder, the text builder and the job function are copied the same way. A1 runs through the copies. **With an empty near-copy set, the new builder must equal sealed `ceiling_lex(1, b)` on all 20 draws (A8).**

**Changes, each with its reason:**

| # | change | reason |
|---|---|---|
| 1 | A new entry mode. The sealed modes are never called. | The sealed `extras` mode refuses without a `real.json`, and running it would be the frozen stop. |
| 2 | Exclusion 2 (near-copies) in the ceiling source. | Leakage through copies under another id. |
| 3 | Checks V1 to V4 and the ledger, before any gain. The sealed A8 line cannot fail by construction. | The leak control has to be verified by a check that can fail. |
| 4 | The plant's vocabulary comes from the block's ceiling list, not the primary list. | K0b must test the ceiling path. |
| 5 | Grading: T, P, S and C, the rules P1 and P2 and FC, in place of the sealed per-size bars. Bar C is computed as sealed. | The K0 of brief 11, with the review's control fixes. |
| 6 | A1 reproduces two sealed Old Assyrian numbers in place of the Linear B number. | What must be shown here is that the loaded code gives the sealed numbers on this script. |
| 7 | The leak dial, the ceiling filler cell, the list-overlap count and the held-out coverage count. | Record-only context for the reading. |
| 8 | The file-open allow-list adds this study's outputs. It still refuses `splits_v2`, claim-bench key files and `saao.zip`. | Outputs need a home; the Indus rule stays enforced. |
| 9 | Seeds for the new plants (below). | New random draws must not reuse sealed streams. |
| 10 | The FT clock rule. | The sealed run lost about 2 h to other jobs. |
| 11 | Parameterised copies of the generator, scramble, filler, shuffled-key, builder and job functions. | The sealed ones fix the base, the list and the builder. A1 and A8 check the copies against sealed numbers. |

- Outputs: `ledger.json`, `kill.json`, `kill.out` in `experiments/lexicon_ceiling/`. Per-draw and per-key aggregates only. No key value and no per-position array is written.

## Cells

| cell | text | keys and lexicons | size | draws | key cells | role |
|---|---|---|---|---|---|---|
| A1 | sealed plant 1; sealed real draw 4, both through the copied functions | true, primary list | 1 u | 2 | 2 | abort check |
| K0b | plant from the ceiling list, and its scramble | true; 5 permuted copies; 5 shuffled keys | 1 u | 5 | 60 | graded; sets FC |
| **K0a** | real | true with the ceiling list; its 5 permuted copies; 5 shuffled keys | 1 u | 20 | 220 | **graded** |
| scramble | scramble of real | true with the ceiling list | 1 u | 20 | 20 | record-only |
| leak dial | real | true with the no-exclusion list | 1 u | 20 | 20 | record-only |
| filler | order-1 filler on blocks 0 to 4 | true with the ceiling list | 1 u | 5 | 5 | record-only |

## Aborts
- **A1.** The loaded code does not reproduce, to 1e-9, the sealed K0a plant-1 gain (0.3731052945333844) and the sealed real-text gain of draw 4 with the primary list (`kill.json`): stop.
- **A2.** The code recomputes the count gate before any gain. Stop and redraft if: a pool T count differs from the sealed A2 figures; the whole-pool type counts differ from 1,967 / 1,793 / 720 / 191; the count of tablets with a usable word differs from 3,821; any draw has a shortfall; a list is not 2,815 words; or the near-copy counts of the 20 draws differ from 9, 8, 4, 14, 3, 19, 15, 5, 9, 3, 5, 8, 10, 9, 9, 10, 6, 7, 2, 7.
- **A3.** FC stop (reading 0c).
- **A4.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- **A5.** Any step would read an Indus key or restore an Indus sign: stop.
- **A6.** The window model does not sum to 1 (to 1e-9) for the fitted K0b plant-1 model: stop.
- **A7.** The sign list or the sealed code file does not match its SHA-256: stop. `saao.zip` is never opened.
- **A8.** V1, V2 or V3 fails for any draw, or the new builder with an empty near-copy set differs from sealed `ceiling_lex(1, b)` on any of the 20 draws: stop.
- **A9.** A set Q tablet is in pool T or in a ceiling source: stop.
- No rerun, no tuning, no fix tags after any gain is seen.

## Seeds
- Study base **20270301**, used only for what is new: the K0b plants (vocabulary order base + 100,000 + k; spelling base + 200,000 + 1,000 + k; scramble base + 500,000 + 1,000 + k; shuffled keys base + 600,000 + 1,000 + 10 k + j) and the filler texts (base + 300,000 + 1,000 + k).
- **Everything on real text keeps the sealed base 20270201:** the tablet order, the chunk lengths, the scrambles and the shuffled keys of the real draws, and the five letter permutations.
- The split and the folds use no seed (sealed hashes).

## Limits stated in advance
- **A pass may be archive knowledge, not word knowledge.** The trigram learns from about 4,000 development tokens. The ceiling list is drawn from about 440,000 tokens of the same archive. A gain could be "more text in the same language", carried in through the list. The permuted copies test letter identity, not this. The filler cell describes it. A trigram trained on the whole archive would test it directly; that would be a new baseline and is not run.
- **The permuted control is known to be loose on plants.** See FC. Under P2, two of five copies can gain and the draw is not flagged. That is why a pass under P2 also needs bar C in 16 of 20.
- **The 20 draws share one source.** Their held-out texts are disjoint, but each draw's list is built from nearly the same 3,750 tablets. The draws are not independent in the lexicon.
- **The list is nearly the whole vocabulary at 4 consonants** and includes words seen on one tablet. It is as generous as a list can be.
- **Generous in three more ways (sealed):** the editors' word division; spelling through the same oracle key; names kept.
- **Near-copies are found by identical lines only.** A copy with small spelling differences in every line passes exclusion 2. The reviewer's shingle check puts the cost at 0 to 1 list words (see "What was seen").
- **One script, one archive, one score, one size graded.** 1 u is about 8,000 tokens.
- **A fail is not a proof.** It says this score, on this text shape (chunks of 3.5 signs), gains nothing from this list.
- **The bands of T (16 and 4) are round numbers:** 80% of draws, as sealed, and its mirror.
- **Expected result (brief 11):** pass 30%.

## Cost
- Heavy. At most 4 workers, `nice -n 20`, detached with a pid file, under the Indus compute lock through `board/run.sh`. One run.
- **Measured in the sealed run, per key cell, when not starved:** about 20 s at 1 u. Cell builds add about 15 s per text at 1 u.
- **Estimate:**

| stage | key cells | processor-hours |
|---|---|---|
| checks, ledger, A1 | 2 | 0.1 |
| K0b | 60 | 0.4 |
| K0a, true key and permuted copies | 120 | 0.9 |
| K0a, shuffled keys (graded) | 100 | 0.7 |
| scramble, leak dial, filler, counts | 45 | 0.3 |
| **total** | **327** | **about 2.4** |

- **327 key cells, about 2.4 processor-hours. Wall time on 4 workers: about 1 h** when the machine is free. The estimate could be off by a factor of two.
- The sealed run was slowed about tenfold for 2 h by other projects' jobs. At that rate throughout, the graded cells (2.0 processor-hours) take about 5 h. FT keeps the run under 6 h by not starting record-only cells late.
- Results go to the study's folder in the repo, not to a temporary directory.

## Decisions needed before sealing
- None open. The five questions of v1 are answered under "Decisions, ruled" at the end, and the body follows them.

## Before sealing
- A pre-seal check of v2, if wanted.
- Code written and hashed after sealing, before any gain.

## Review log
- 2026-11-25: DRAFT v1 written. Not reviewed. Not sealed. No study code exists. Label-free counts only: no G, D, λ* or lexicon match was computed with a ceiling lexicon on any text.
- 2026-11-25: Project lead's rulings received (five, under "Decisions, ruled"). Fresh review of v1 returned five must-fix items.
- 2026-11-25: **DRAFT v2.** Not sealed. No study code exists. Nothing was scored. Changes:
  1. The 4 u / 16 u arm is struck everywhere (decision 4). FT has one cut, at 4.5 h. Cost is 327 key cells, about 2.4 processor-hours.
  2. V3 uses a 4-consonant canary, a synthetic near-copy at 3 and at 2 shared lines, and one ordinary source tablet.
  3. The shuffled-key cell is graded and always runs. A pass needs S ≤ 1.
  4. Under P2 a pass also needs bar C in 16 of 20.
  5. Code reuse: the generator, scramble, filler, shuffled-key, builder and job functions are parameterised copies; A1 runs through them; A8 checks the builder against the sealed one.
  6. The reviewer's shingle check is disclosed under "What was seen".
  7. Added: a record-only held-out coverage count; the statement that K0b tests the code path, not power; the filler blocks (0 to 4).
  8. Atlas wording follows decision 5. The open-questions list is replaced by a pointer to the rulings.

## Decisions, ruled 2026-11-25 (project lead, before review)
1. **Control rule:** strict as drafted. The switch to median-of-five is allowed only by the pre-stated rule set on the K0b plants. Nothing else may change it.
2. **Partial band:** 5 to 15 of 20 gets its own reading. "No power" applies only at 4 or fewer.
3. **Near-copy thresholds:** as drafted (3 or more identical lines of 5 or more signs).
4. **The record-only 4 u / 16 u arm is struck.** It adds compute and decides nothing.
5. **Atlas wording after a fail:** brief 11's reading, "this score has no power on real text even with the best lexicon, so restoration is untested, not closed". The `certify_size_curve` and `lift_score` entries get a pointer line. Their sealed readings are not edited.
