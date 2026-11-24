# Ur III seal legends: does a true reading pass the refute bench on a formulaic, name-heavy seal corpus? (SEALED; no code existed and no IC had been computed at sealing)

Status: **SEALED v3**, 2026-11-24 (v2 plus the pre-seal check's six edits E1-E6). Drafted by Fable (brief 9, study 3). One fresh review (FIX) applied; see the review log. A narrow pre-seal check of v2 returned SEAL-WITH-EDITS; its edits are applied. Main line (a), the claim bench. Kind iii (a read script used as a known-answer control).

## Question
- On Ur III seal legends cut to Indus shape and size, does the attested cuneiform reading beat shape-keeping shuffles of itself against a Sumerian lexicon, under the sealed IC refute bench?
- **No Indus key is scored. No outcome supports or counts against any Indus key, and none licenses a rerun of one.**
- **The key is an oracle** (the editors' reading). So a fail is strong and a pass is an upper bound.

## Why
- The refute standard has been shown on one script and one genre: Linear B palace records (`lb_shape_ladder` R1, 20 of 20).
- `lb_formula_dial` put the true Linear B key at the bar (16 of 20) once the text was tilted to Indus formula excess. That tilt was synthetic.
- Seal legends are the closest read analogue to Indus seals: short, formulaic, mostly names and titles. No sealed study scores a true key on one.

## What was seen before this draft
- **Sealed results:** `lb_certify`, `lb_shape_ladder` (+ addendum 1), `lb_formula_dial`, `lb_wrong_lexicon`, `yj_ic_refute`, `scott_ic_refute`.
- **Label-free counts, run 2026-11-24 with scratch scripts outside the repo** (tokens, readings, lexicon skeletons, segment lengths and bigram shares only). v2 reran them under the frozen drop rule and the numeral cut. They fill the tables below.
- **Label-free numbers read from sealed output:** `lb_formula_dial` `kill.json` (M77 and Linear B excess).
- **Not seen:** any IC of any key on any cuneiform text; any planted test; any null width.
- The scratch scripts are not the study code. The sealed code must recompute every table here before any IC (abort A2).

## Prior art
- **Repo.** `short_labels` extracted the legends as a short-label register. `language` used them to simulate a Sumerian-type corpus. Neither scores a reading against a lexicon.
- **Opened 2026-11-24:**
  - CDLI seals project note, 2013 (ancientworldonline.blogspot.com/2013/10/seals-and-sealing-in-cdli-files.html). Legends "as a rule named the seal owner, his profession or educational standing, his patronymic" and his affiliation; duplicates were merged into composite entries; royal introductions run to fixed lines.
  - Dahl, "Where have all the Ur III seals gone?", doi:10.33182/aijls.v3i2.2851 (abstract page only). About surviving physical seals, not legend structure. The three-line owner / dub-sar / dumu type and the arad-zu type were seen in a search summary of this paper only (unverified).
  - CDLN 2011:4 (cdli.earth/articles/cdln/2011-4). The Ur III transliterations were normalised to one conventional reading per sign use. So the "true key" here is an editor's unified reading.
  - SumTablets, arXiv 2602.22200 (abstract only). A transliteration baseline that samples among a glyph's possible readings. The figure of about 22 readings per glyph, weighted by frequency, comes from a search summary (unverified).
- **Not found:** an IC or dictionary-fit test of a stated key against shuffles on cuneiform, or on any seal corpus. The search was short; "not found" is weak evidence that this is new.

## Data (all already held)
- **CDLI dump** in `experiments/short_labels/raw/cdli` (ATF and catalogue). Period "Ur III" only.
- **Drop rule (frozen):** A legend or line is dropped if any sign carries `#`, `[ ]`, `x` or `...`. One broken line drops its whole legend. `?`, `!`, `*` and `< >` marks are stripped and the sign kept. Seal objects give no administrative lines.
- **Legends:** `@seal` sections of Ur III texts plus whole texts of seal objects. One copy per distinct sign sequence, the first in dump order.
- **Administrative lines (kill-test text):** lines of Ur III texts with genre "Administrative", outside `@seal` sections. Only texts whose id has CRC32 mod 20 equal to 0 are used (a fixed 5% of texts; see Seeds). The sample holds 39,192 lines from 3,475 texts.
- **Lexicons:** Oracc ePSD2 project glossaries, Sumerian (`gloss-sux.json`): Old Babylonian administrative (under `experiments/onomasticon/raw`) and Old Akkadian administrative (in the zip under `experiments/meaning_classes/raw/oracc`). No Ur III glossary is held, so no lexicon is built from the test text.
- Indus text lengths: M77 seals and sealings, as `lb_certify`.

## Readings (frozen)
- **A sign token is one transliterated reading**, as CDLI gives it. Words split at `-`, `.`, `+`.
- **The true key** gives each reading its consonants in order. `sz` is š, `s,` is ṣ, `t,` is ṭ. Index digits and a final `x` are removed. Vowels are a e i u.
- **Alphabet: 14 letters,** b d g h k l m n p r s š t z. CDLI ASCII does not mark ĝ, so g stands for both.
- **Determinatives** `{x}` are signs with the empty value. They are not breaks.
- A determinative is its own sign type with the empty value and enters N1's zero-consonant class.
- **Unkeyed, and a break:** numerals, upper-case sign names, `|compounds|` without a stated value, and any reading with a letter outside the alphabet (q, w, ṣ, ṭ).
- **One value per reading.** The editor has already chosen among each sign's readings. This is easier than what a decipherer faces. See Limits.

### Measured: mapping
| text | units | sign tokens | reading | determinative | numeral | unread | reading types |
|---|---|---|---|---|---|---|---|
| legends | 4,819 distinct | 52,907 | 88.3% | 9.3% | 0.0% | 2.4% | 670 |
| administrative lines (all) | 767,047 lines | 4,175,889 | 76.1% | 5.1% | 17.6% | 1.2% | n/a |
| administrative lines (5% sample) | 39,192 lines, 3,475 texts | 212,556 | n/a | n/a | n/a | n/a | n/a |

- Recomputed in v2 under the frozen drop rule. It drops 10,198 legend sections and 204,699 administrative lines.
- "Unread" here includes readings with a letter outside the alphabet (0.2% of legend tokens, 20 types). v1 counted them as readings.
- Legends: 97.6% of tokens are keyed, above the 90% coverage rule (`lb_shape_ladder` addendum 1).
- Administrative lines: numerals are 17.6% of tokens. **A line is cut at each numeral, and each numeral-free run is a text.** Of the remaining tokens 98.6% are keyed.
- The sample gives 39,690 numeral-free runs of 2 or more tokens (166,856 tokens, 3,472 texts).
- Earlier counts: the plan had 6,381 legends and 59,134 tokens (older extractor, which split compounds and kept determinatives as readings). v1 had 5,134 and 56,926 (it kept signs marked `#` or `[ ]`). The sealed code's count is the one that stands.

## Lexicon construction (frozen)
- **Skeleton of a word = the consonants of an attested spelling**, sign by sign, with the same rules as the text. No doubling is collapsed, because the text stream collapses none. This is the analogue of passing Homer through Linear B spelling rules.
- A spelling with an upper-case sign or a letter outside the alphabet is dropped. 1 to 7 consonants are kept. Citation forms (L4) collapse doubled letters and include the Rimanum glossary held beside the OB one (1 skeleton).
- **Density** = skeletons of length L over 14^L. **Rule LMIN** = the smallest L with density ≤ 25% (frozen in `lb_shape_ladder`).

### Measured: density (14 letters)
| lexicon | skeletons | 2 | 3 | 4 | 5 | rule LMIN | role |
|---|---|---|---|---|---|---|---|
| Homer (sealed bench, 9 letters) | 10,491 | n/a | n/a | 0.177 | 0.014 | 4 | reference |
| **OB administrative, spelled forms** | 1,838 | 0.735 | **0.180** | **0.014** | 0.001 | **3** | **primary** |
| Old Akkadian administrative, spelled forms | 1,940 | 0.821 | 0.243 | 0.016 | 0.001 | 3 | report only |
| OB + Old Akkadian citation forms | 928 | 0.699 | 0.126 | 0.008 | 0.000 | 3 | report only |
| all spelled forms pooled | 3,044 | 0.847 | 0.300 | 0.026 | 0.001 | 4 | not run |
| Old Akkadian names glossary, spelled | 4,327 | 0.918 | 0.339 | 0.036 | 0.002 | 4 | not run |

- The primary lexicon's density at LMIN and at LMIN + 1 (0.180, 0.014) matches Homer's (0.177, 0.014) without thinning.
- **Rule LMIN is 3 for every run lexicon.** L3 and L4 run at 3 whatever K1 recomputes; L5 alone runs at 4. Sumerian words are short, so the matched cut sits one consonant lower than in Greek.
- No names glossary enters any lexicon. A claimant would not hold one.

## Text shape (frozen; the sealed R1 set-up)
- Each legend is cut into chunks with lengths drawn from M77 seals, as `lb_certify` `chunk`. 2,300 chunks per draw. Texts are split half and half by CDLI text id (see Seeds); the held-out half is scored. 20 draws.
- Administrative texts are built the same way from numeral-free runs.
- **Excess** is the sealed `lb_formula_dial` measure, with its function copied unchanged: top-50 pair share minus its mean over 20 unigram shuffles, pairs kept inside a chunk. It is measured on the held-out half of the 2,300 chunks.

### Measured: shape
- Share and segment columns: 13,100 tokens, 3 draws each. Excess: held-out half, 20 draws, range and median.
- "Whole" rows take whole texts to the same token budget before the split.

| text | top-50 bigram share | excess over unigram shuffle | consonants per segment | consonants in segments ≥ 3 | ≥ 4 |
|---|---|---|---|---|---|
| legends, whole | 0.379-0.394 | 0.234-0.281 (0.252) | 12.1-12.3 | 98.7-98.8% | 98.2% |
| **legends, M77 chunks** | **0.381-0.396** | **0.225-0.272 (0.255)** | 5.1 | **93.0-93.4%** | 85.0-85.2% |
| administrative, whole runs | 0.212-0.218 | 0.138-0.187 (0.162) | 5.2 | 95.1-95.8% | 86.0-87.4% |
| **administrative, M77 chunks** | **0.219-0.225** | **0.149-0.172 (0.165)** | 3.9 | **88.5-89.4%** | 71.2-72.1% |
| reference: M77 distinct seals and sealings | 0.274 | 0.158 (sealed e_M 0.159) | n/a | n/a | n/a |
| reference: Linear B R1 (F0) | n/a | 0.127 (sealed median) | 2.51 | 18.6% at ≥ 5 | n/a |
| reference: `yj_ic_refute` corpus | 0.238 | n/a | n/a | 47.4% at ≥ 5 | n/a |

- Held-out size (median of 20 draws): 4,520 tokens for legend chunks and 3,552 for administrative chunks.
- M77's excess was recomputed with the sealed function at both sizes (0.158 each). The sealed value is 0.159 at 4,014 tokens. The pre-seal review of `lb_formula_dial` gave 0.155 for M77 and 0.129 for Linear B.
- The LMIN cut removes little here: over 88% of consonants sit in segments the scorer can read. The `lb_wrong_lexicon` Arm B failure (18.6%) does not apply.
- By excess, legends are about 1.6 × M77 (median 0.255 against 0.158) and administrative chunks are at M77's level (median 0.165). Raw shares are not compared across scripts.
- So the kill-test text is not an easy one. It sits at Indus excess, which is the F1 rung that passed only at the bar (16 of 20) in `lb_formula_dial`.

## Statistic, null and bars (as sealed)
- **Token IC:** share of held-out key consonants inside a lexicon word of at least LMIN consonants.
- **N1:** values permuted across readings within frequency bins of 10, inside each consonant-count class. 1,000 draws.
- **Refute pass (per draw):** true IC above the N1 99th percentile. **A cell passes at ≥ 16 of 20, fails clearly at ≤ 12,** and is "at the edge" at 13-15.
- **Scrambled-text control (every cell):** unigram shuffle of the same chunks; at most 1 of 20.
- Width, signal and margin are reported as in `lb_formula_dial`.

## Checks, run first and in this order (strongest kill first)
1. **K0, pipeline unchanged.** The study code, pointed at Linear B and Homer, reproduces `lb_shape_ladder` R1 per draw to 1e-9 (20 of 20, control 0).
2. **K1, tables.** The sealed code recomputes the three "Measured" tables. No IC yet.
3. **K2, null calibration on administrative text.** In each of the 20 draws one N1 draw is treated as the claimed key and tested against a fresh N1. Pooled wrong-key pass rate ≤ 1 of 20.
4. **K3, planted known answer.** On administrative text the true reading passes ≥ 16 of 20, with the scrambled control ≤ 1 of 20 and partial keys (0 / 25 / 50 / 75 / 100% right, 40 draws each, built as `lb_shape_ladder` control ii) with the five pooled means strictly rising. Fewer than 16, or means not rising, is a K3 fail; at 13-15 the reading is "power not shown at the bar". This text sits at Indus formula excess, where the true Linear B key passed only at the bar.
5. Only then the legend cells.

## Cells
| cell | text | lexicon | role |
|---|---|---|---|
| **L1** | legends, M77 chunks | OB administrative, spelled | **primary** |
| L2 | legends, whole | OB administrative, spelled | report only |
| L3 | legends, M77 chunks | Old Akkadian administrative, spelled | report only |
| L4 | legends, M77 chunks | citation forms | report only |
| L5 | legends, M77 chunks | primary, LMIN 4 | report only |

## Readings (frozen; worded for the bench)
- **The oracle key sets the weight of each outcome:** a fail is strong, and a pass is an upper bound.
- **K3 fails:** "the bench has no power on cuneiform at Indus formula excess and this size; cause not separated (pipeline or formulae)." The legend cells are not run.
- **L1 passes:** "the refute standard survives real formulae and names, at reading level." This does not show the language is identified (Spanish passed in `lb_wrong_lexicon`). This is an upper bound from an editor-resolved reading, a same-convention lexicon and segments twice Linear B's. It does not show why `yj_ic_refute` or `scott_ic_refute` lost power.
- **L1 fails clearly with K3 passed:** "on a formulaic, name-heavy seal corpus a true reading does not beat its shuffles." Fit-refute has no stated power on seal legends at 1.6 × Indus excess. It does not decide Indus-level corpora. Cause not separated (excess, names missing from the lexicon, lexicon period).
- **L1 at the edge:** "not decided."
- Report-only cells describe; they decide nothing.

## Aborts
- **A1.** K0 does not reproduce: stop.
- **A2.** The tables are the v2 ones above, recomputed under the frozen drop rule and the numeral cut. Any recomputed density differs from its table by more than 0.01, the primary's rule LMIN is not 3, legend coverage is below 90%, a count differs (4,819; 52,907; 39,192; 3,475), or a chunk excess median moves more than 0.01 from 0.255 or 0.165: stop and redraft. Share and segment columns are descriptive and gate nothing.
- **A3.** K2 above 1 of 20, or any scrambled control above 1 of 20 in K3: stop.
- **A4.** Fewer than 20 draws can be built for a cell: unbuilt draws count as non-passes.
- **A5.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- No rerun, no tuning, no fix tags after any IC is seen.

## Seeds
- Base seed 20261126. K0 uses the sealed `lb_shape_ladder` seeds unchanged.
- **Draw k (1-20)** uses base + 1000k for chunking, the pick of 2,300 chunks and the split, as `lb_shape_ladder` `build`.
- **Split id:** the CDLI text id (P number, written `P` plus six digits).
  - A legend takes the id of the first text in dump order that carries its sign sequence. A numeral-free run takes its tablet's id.
  - The ids in a draw are sorted ascending as strings, then shuffled by Python `random.Random(base + 1000k)`. The first half (rounded down) is the development half; the rest is held out. Nothing is hashed for the split.
- **5% sample:** CRC32 of the id's ASCII bytes, mod 20, equal to 0. No seed.
- **N1:** base + 1000k + 7. All cells of a draw share the L1 N1 seed.
- **Scrambled control:** the unigram shuffle uses base + 600,000 + k; its N1 uses base + 610,000 + k.
- **Partial keys (K3):** draw k and level j (0, 1, 2, 3 for 0 / 25 / 50 / 75% right) use base + 700,000 + 1000k + j, one generator for that level's 40 keys. The 100% level is the true key.
- **K2:** the claimed key uses base + 500,000 + k; the fresh N1 uses base + 510,000 + k.
- **Excess:** the shuffle baseline of draw k uses 20261129 + k, as `lb_formula_dial`.

## Limits stated in advance
- **Reading level, not sign level.** The key has one value per reading, and the editor resolved each sign's many readings. A decipherer's key must do that itself. A sign-level arm needs a sign list (OGSL), which is not held. A pass here is an upper bound on what a sign-level key would do.
- **The readings are normalised** by the CDLI editors, partly with knowledge of the lexicon.
- **The lexicon is close to the text:** same language, same administrative world, 100 to 300 years apart. Homer is further from Linear B.
- **Names are not outside the lexicon.** Sumerian names are built from common words (ur, lugal, and divine names). So "name-heavy" is weaker than it sounds, and Akkadian names sit in the same legends.
- **The kill-test text also holds names** and comes from the same tablets as many legends. Lines that name seal owners are not removed.
- ĝ and g are merged. One script, one statistic. Held-out sizes are about 4,500 tokens (legends) and 3,550 (administrative).
- A pass is consistent with the language, and does not identify it.

## Cost
- About 1,000 N1 scores per draw per cell; 5 cells plus the kill tests. Under an hour with 4 small workers. Outputs are small JSON files.

## Decisions
1. **Reading-level key:** accepted, as an upper bound. No sign-level arm (OGSL) is added.
2. **Alphabet:** 14 letters kept, since LMIN is 3 either way.
3. **Primary lexicon:** OB is primary, because Old Akkadian's 0.243 sits within A2's 0.01 tolerance of the rule edge (0.25).
4. **Owner-name lines** are not removed from the kill-test text, and this is disclosed (Limits).
5. **Sample:** the 5% CRC sample is kept, at 39,192 lines from 3,475 texts.

## Before sealing
- A second fresh review. Code written and hashed after sealing, before any IC.

## Review log
**v2 (first fresh review, FIX, 9 items).** Recounts are label-free: no IC, no planted test.
1. Drop rule frozen; mapping table recomputed (legends 5,134 to 4,819; tokens 56,926 to 52,907).
2. Shape table: administrative rows recomputed under the numeral cut; excess column added with the `lb_formula_dial` function; last bullet replaced; "less formulaic" removed.
3. K2 bar is ≤ 1 of 20 (A3 follows).
4. K3-fails reading reworded: cause not separated.
5. L1-passes reading: upper-bound sentence added.
6. L1-fails reading: scope limited to seal legends at their own excess.
7. Determinative: own sign type, empty value, N1 zero-consonant class.
8. Limits: held-out sizes replace "about 4,000".
9. Seeds: split id, sample hash, scrambled-control and partial-key seeds stated.

Also applied: "Open questions" became "Decisions" (5 items); the oracle-key line; A2 points at the v2 tables.

Where this draft's recount differs from the review's figures, the recount stands:
- Legends, sample lines and sample texts match the review exactly (4,819; 52,907; 39,192; 3,475).
- Excess over 20 draws: legends 0.225-0.272 (review 0.253-0.261); administrative 0.149-0.172 (review 0.161-0.177).
- M77 is 0.158 and Linear B 0.127 from the sealed function and output (review 0.155 and 0.129, the pre-seal figures). So the ratio is written as 1.6 ×, not 1.65 ×.
- Administrative held-out size is about 3,550 (review 3,650).
- Administrative chunk rows: share 0.219-0.225, ≥ 3 at 88.5-89.4%, ≥ 4 at 71.2-72.1% (review 0.217-0.222, 88.7-89.2%, 70.5-71.5%).
- Pre-seal check of v2: SEAL-WITH-EDITS, six edits (drop-rule detail, LMIN wording, citation-form rule, K3 partial keys and edge reading, A2 counts and excess tolerance, L1-fails cause clause). Applied; sealed as v3.
