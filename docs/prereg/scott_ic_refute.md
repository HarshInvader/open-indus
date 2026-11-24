# Refute-only IC bench of the Scott (Dunn) key (sealed before any code runs; no score of her key exists)

Agent `paper`. Main line (a), the claim bench. Fable's top study after `anchor_ceiling` (RESEARCH_STATE, 2026-11-24 ranking). Drafted by Fable, then revised after a fresh Fable review (10 fixes applied).

## Licensing before sealing
- `/.local/` was added to `.gitignore`, so `key.csv` cannot be committed by accident.
- `experiments/key_hunt/candidates.md` (commit fa6d5e6) quoted a few sign values. They are redacted in the working tree. Whether to rewrite history is left to the owner.

## Scope
- **Refute-only.** The best possible outcome is "refuted at about X% power". No outcome supports the key.
- **Why a pass means nothing.** Keys fitted to meaningless text beat their shuffles (`yj_ic_refute`: 3 of 3; `lb_shape_ladder`: certify at 0 rungs).
- **Question.** Does her key's IC on the M77 corpus exceed the 99th percentile of its own shape-keeping shuffles?
- **Fixes carried from the `yj_ic_refute` red team:** strict lexicon that drops words, a formula-keeping plant with power read at the real null's width, and a token-weighted partial ladder.

## Data
- **Key.** Scott (Dunn), MahaSamVani LIS v3, doi 10.5281/zenodo.21522783. 417 rows in Mahadevan order: 332 ok, 15 uncertain, 70 blank.
  - Read from `.local/scott_lis/key.csv` only. CC BY-NC-ND: never committed.
- **Corpus.** Distinct M77 texts (`corpus.load.m77_texts`, `distinct`) in reading order.
  - Measured without the key: 2,270 texts, 10,005 sign tokens, 417 sign types (all texts: 3,445 and 13,372).
  - A segment ends at a line break, a `#` break, or an unkeyed sign.
  - The whole corpus is used; nothing of ours is fitted.
- **Lexicon.** Monier-Williams headwords (`ext/skt/mw_headwords.txt`, 194,083 lines) plus the 5 consonantal endings of `yj_ic_refute`. At most 7 consonants.
- **Planted Sanskrit.** `ext/eqstats/rv_names_epithets.txt` (Rigveda), as in `yj_ic_refute`.

## Values to consonant skeletons (frozen)
Vowels are not scored. Each keyed sign gets a set of 1 or more alternative skeletons.
- **Clean-up.** Remove "(...)". Cut all text after an en dash or a semicolon.
- **Alternatives.** "/", "," and " or " separate alternatives. Each is kept. There is no cap; the code aborts if a sign has more than 4 (a parse error to fix in `overrides.csv` before any run).
- **Brackets.** "[...]" and its content are removed: by her convention that part is understood, not sounded. A bracket holding single-letter alternatives gives one alternative per letter.
- **Gaps.** An alternative containing "…" is dropped. A sign with no alternative left is blank.
- **Affixes.** Hyphens are removed and the parts joined. No position rule is enforced.
- **Whole-word and multi-word values.** The full unbracketed consonant string, words joined.
- **"?" entries (15).** The "?" is removed and the value is used (primary). Secondary: all 15 treated as blank.
- **Blanks (70).** Unkeyed. They break segments.
- **Vowel-only values.** Keyed, with 0 consonants.
- **Free-text entries.** Entries holding English notes the rules cannot parse are resolved by hand in `.local/scott_lis/overrides.csv`.
  - The file is written before any code runs. Its sha256 and exact row count are sealed with this prereg (in `HASHES.txt` and the addendum line below).
  - An override may only select text printed in that entry.
  - Any entry the parser flags that is not in the file aborts the run.
  - Secondary: overridden entries treated as blank.

## Sound classes (applied to key, lexicon and planted stream alike)
- **Parsing.** Digraphs first: kh gh ch jh th dh ph bh sh.
- **Her swaps:** b/v one class; r/l one class; d/t one class.
  - s/ts: a lexicon word containing T+S yields both its T+S and its S forms. Key and stream are untouched.
  - au/o/u has no effect, because vowels are not scored.
  - The swaps are applied literally. They are not extended to aspirates (th and dh stay apart).
- **Forced by her spelling (no diacritics on most values):**
  - dental and retroflex stops merge;
  - s, ś, ṣ and "sh" merge;
  - n, ṇ, ñ, ṅ merge;
  - c and ch merge;
  - h and visarga merge;
  - vocalic ṛ counts as r in key and lexicon.
- **Classes (at most 20):** k, kh, g, gh, C, j, jh, T, th, dh, N, p, ph, B, bh, m, y, R, S, h.
- **Anusvara** in a lexicon word yields both the m and the N variant. This is the only one-to-many step.
- **Key alphabet A.** The classes that occur in her key, counted by the code.
- **Strict semantics.** A lexicon or stream word with a consonant outside A is dropped whole. No consonant is ever deleted from a word.

## Statistic and null
- **IC.** The share of key consonants inside lexicon words of at least LMIN consonants.
  - Covered consonants are maximised exactly over the segmentation and over each token's alternative.
  - Ties take the reading with fewer consonants. IC = total covered / total consonants of the chosen readings.
- **LMIN = 4**, subject to the saturation check (K2), which runs before any power is seen. The density bound is |A|^LMIN.
- **N1.** Her value sets permuted across signs within frequency bins of 10, inside each consonant-count class (count of the first alternative). Whole alternative sets move together. 1,000 draws.
- **Width.** W = N1 99th percentile minus N1 mean. W_real is the width from her key's shuffles on the real corpus. It is computed without scoring her unshuffled key.

## Step 0. Coverage (precondition, computed by the code)
- Token coverage = share of the 10,005 tokens whose sign is keyed. The all-texts figure is also reported.
- Expected about 95% (`key_hunt/candidates.md`); not yet computed.
- **Below 90%: verdict "below standard". The run stops.** (Standard: `lb_shape_ladder` addendum 1, R90 at 17 of 20.)

## Formula-keeping plant
- **Planted key.** Her own value sets, shuffled across signs within consonant-count class. So every planted value obeys her rules, slashes included, and each distinct sign has one fixed planted value.
- **Formula chunks.** Each real segment is parsed left to right into the longest n-gram (n = 4, 3, 2) that occurs at least 5 times in the corpus; other slots are single.
- **Rewriting.**
  - Slots are filled as in `yj_ic_refute`:
  - c is the consonant count of the real sign's first alternative.
  - An alternative matches if it equals the next len(alt) stream consonants. The longest matching alternative wins, and the stream advances by its length.
  - Among matching signs, the pick is by Indus frequency.
  - Blank (unkeyed) signs stay blank.
  - The first occurrence of a chunk type is filled from the running stream and stored. Every later occurrence reuses the stored signs, and the stream resumes after that chunk's stretch.
  - So repeated formulae stay repeated.
- **Reported:** miss rate, share of stream skipped, and top-50 bigram share against the real corpus's.
- **Formula fidelity (frozen).** If the planted top-50 bigram share is below 0.8 × the real share, X is labelled "upper bound, plant not formula-faithful".
- **Limit.** Joins before a reused chunk break the Sanskrit. That lowers power; it cannot raise it.

## Kill tests, in order (her key is not scored until all pass)
- **Order: K2 runs first,** so that LMIN is fixed before any power is seen. Then K1, K3 and K4.
- **K1. Power at the real null width (strongest test).**
  - Planted corpora 0-4. A planted key passes if IC minus its N1 mean exceeds max(W_planted, W_real).
  - Fewer than 3 of 5: **STOP**, "untestable at stated power".
- **K2. Lexicon saturation.**
  - Density of length-4 skeletons must be at or below 25% of A^4 (the frozen `lb_shape_ladder` rule).
  - 200 random keys (her value sets shuffled within consonant-count class) on the real corpus must have mean IC at or below 0.50.
  - Reported beside it: the same mean with first alternatives only, and with the swap classes off.
  - If either bound fails, LMIN moves to 5 once and K2 is rerun (before K1). If it fails again: **STOP**, "untestable at stated power".
- **K3. Full power.** 40 planted corpora. At least 32 of 40 must pass at max(W_planted, W_real). Power 0.8.
- **K4. False alarms.** The same pipeline on a unigram-shuffled stream must pass in at most 2 of 40.

## Partial ladder (sanity check, not a gate)
- Signs are kept right at random until they hold 0, 25, 50 or 75% of **tokens**; the rest are shuffled within class. 10 draws per level per corpus; the full planted key comes last.
- Reported: mean IC per level, the token share right by chance at level 0, and the share of corpora with a strict rise.
- It is not a gate. In `yj_ic_refute` a strict rise held in only 27-62% of resamples, so it is too noisy to decide.

## Verdicts (frozen)
- **Below standard:** coverage under 90%. The key can be neither supported nor refuted by fit.
- **Untestable at stated power:** K1, K2, K3 or K4 fails. Her key is not scored. The measured power is reported.
- **R, "fails to beat its shuffles":** all gates pass and her key's IC does not exceed its N1 99th percentile.
  - Wording: "a fully right key of this shape on Rigveda text passes X%". X is the K3 pass rate, with its 95% Wilson interval.
  - The K3-style power of a key right on 75% of tokens is reported beside it.
  - A partly right key is not refuted by this.
- **Not refuted; no support:** all gates pass and her key exceeds its N1 99th percentile. This is not evidence for the key.
- **Secondaries** (reported, never decide): "?" entries blanked; first alternative only.

## Scorecard and licensing
- **Row.** New row `KEY-scott` (phonetic key) in `experiments/scorecard_v1/rows.csv`, beside `KEY-yajnadevam`.
- **Route.** The row is added and rated only through a sealed scorecard addendum (next: `scorecard_addendum6.md`), with fresh blind raters under the v1 rubric. NEGATIVE_ATLAS 1.1 gains one line.
- **Changes to this design** after sealing go in `scott_ic_refute_add1.md`, hashed in `HASHES.txt` before the affected step runs.
- **No key values in any committed file.**
  - Code reads `key.csv` and `overrides.csv` from `.local/` at run time.
  - Output JSON holds aggregates only: coverage, A, densities, IC, null statistics, counts. No sign-level values, no planted keys, no readings.
  - RESULTS.md cites the key by DOI and gives no examples of values.

## Limits stated in advance
- Her nesting and stacking order rules are not modelled; M77 order is used.
- Her "extremely rare" rule breaks are not modelled.
- A sign may take a different alternative at each token. That favours her key and its shuffles equally.
- The Rigveda is older than much of Monier-Williams.
- M-number alignment was spot-checked, not proven sign by sign.

## Cost
- Minutes on 4 workers. It runs under the Indus compute lock with `nice -n 20` and the memory guard.
- Code: `experiments/scott_ic_refute/run.py`, hashed before any run.

## Sealed inputs
- `.local/scott_lis/overrides.csv`: exactly 7 rows, sha256 `3223b902581f5120f3eb04671ac6022c9d9867001af1558043b089af07ff5e8a`. It was written before any code ran. The parser (`values.py`) flags no other entry.
- **Parse aggregates** (no values): 345 signs keyed, 72 blank. Alternatives per keyed sign: 1 → 289, 2 → 51, 3 → 5.
- **Smoke-test disclosure (before the code seal).** Planted corpus, unused seed 999, 20 shuffles: shuffled-key IC mean 0.795, planted-key IC 0.804, width 0.023, miss 0.07, skipped 0.78, bigram share 0.198 against 0.295 real. Her key was not scored. K2 and its LMIN fallback are frozen, so this changes nothing.
