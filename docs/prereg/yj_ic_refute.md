# Power-gated IC refute test of Yajnadevam's Sanskrit key (sealed 2026-11-23, before any score of his key)

Agent `paper`. Main line (a), the claim bench. This is Fable's top study after `lb_shape_ladder` (RESEARCH_STATE, "Main-line plan").

## Why
`lb_shape_ladder` set the standard. IC, scored against shuffles that keep text shape, recognises a real key at Indus length with no word division, provided every sign is keyed (Linear B, 20/20). It never certifies a key.

Yajnadevam's key is the only published key we hold sign by sign at full coverage (99.9% of readable tokens). Atlas 1.1 now calls it "unsupported" because the old CPW score was blind. This test asks a narrower question: does his key beat its own shuffled values on the Indus corpus?
- **A failure** counts against the key, at the power the planted control shows.
- **A pass** means nothing, because he fitted the key to this corpus, and fitted keys pass easily. The pass-meaning control below measures how easily.

## Data (all on hand)
- **Key.** His current public table, `yajnadevam/lipi` commit fc8813a (2026-08-19), `src/assets/data/xlits.csv`. It is fetched to `sources/yajnadevam_lipi_fc8813a/` and kept local, as the repo has no license.
  - Our older copy (`sources/field-cady…/xlits.csv`) differs in 32 of 716 signs, mostly vowel length. It is scored as a secondary key, reported, and does not decide the verdict.
  - Empty values resolve through `canonical`, as in `yj_common.load_key`.
- **Corpus.** Distinct ICIT texts (`corpus.load.icit_texts`, `distinct`) in reading order.
  - A segment ends at a line break, a `#` break, or a sign with no readable value.
  - Vowel-only values add no consonants.
  - The whole corpus is used: no split is unseen by the claimant, and no model of ours is fitted here (precedent `a1_key_null`).
  - Measured before sealing: 3,249 texts, 712 signs, 11,752 key consonants, 3.40 consonants per segment, 47% of consonants in segments of 5 or more.
- **Lexicon.** Monier-Williams headwords plus the consonantal endings, built as in `experiments/language/a1_key_null.py`, at most 7 consonants. Two matchers:
  - **generous:** his latitude classes from `a1_key_null` (s:{s S z h H}, n:{n N R Y m M}, …); primary;
  - **strict:** each key letter is its plain consonant only.
- **Planted Sanskrit.** `experiments/language/ext/eqstats/rv_names_epithets.txt` (Rigveda), IAST mapped to SLP1, then to key letters through the matcher's classes.

## Statistic
- **IC** is the share of key consonants inside lexicon words of at least LMIN consonants, under the segmentation that maximises that share.
- **LMIN** follows the frozen rule from `lb_shape_ladder`: the smallest L with lexicon density at or below 25% of the 16^L key-letter strings. Measured before sealing (lexicon only):

  | matcher | L=3 | L=4 | L=5 | LMIN |
  |---|---|---|---|---|
  | generous | 0.73 | 0.34 | 0.09 | **5** |
  | strict | 0.80 | 0.36 | 0.08 | **5** |

## Null
**N1:** the key's own consonant values permuted within frequency bins of 10, inside each consonant-count class (shape fixed). 1,000 draws. A key "beats shuffles" if its IC exceeds the N1 99th percentile.

## Power gate (run before his key is scored), per matcher
- **Planted corpora (20).** Each one:
  - draws a planted key: his values shuffled across signs within consonant-count class;
  - rewrites every Indus text slot by slot. A slot whose sign carries c consonants gets a sign whose planted value equals the next c consonants of the Rigveda stream, picked by Indus frequency. Each text starts at a random point in the stream. If no sign matches after 50 stream advances, the slot takes a random sign of the same class; the miss rate is reported.
- **Gate.** The planted key beats its N1 in at least 16 of 20 corpora, AND the same pipeline on a unigram-shuffled Rigveda stream passes in at most 1 of 20, AND partial planted keys rise strictly. Partial keys keep 0, 25, 50 or 75% of values right (the rest shuffled within class); each level is the mean of 10 draws per corpus, and the full planted key comes last.
- **Pass-meaning control.** 3 keys are hill-climbed (3,000 within-class swaps, generous matcher) on unigram-shuffled Indus texts. Each is scored against its own N1 on that corpus. This measures how often a key fitted to meaningless text "beats shuffles".

## Kill test
- Planted corpus 0, generous matcher.
- If the planted key does not beat its N1 99th percentile: **STOP**. Verdict: "Monier-Williams fit cannot refute at Indus shape". His row becomes "untestable by fit".

## Verdict rules (frozen; primary key = upstream fc8813a)
- **Untestable with this lexicon:** the generous gate fails.
- **Refuted at stated power:** both gates pass, and his key does **not** beat shuffles under either matcher. The planted pass rate is the stated power.
- **Not refuted; no support:** his key beats shuffles under either matcher. Given the pass-meaning control, this is not evidence for the key.
- **Inconclusive:** the strict gate fails and the generous test does not beat shuffles.

## Limits stated in advance
- His insertions and deletions in readings (about 0.19 per reading) are not modelled.
- The Rigveda is older than much of Monier-Williams. That period mismatch, if anything, favours planted detection less than his own lexicon choice favours him.
- "About 1.3 free choices per sign" is modelled only through the consonant classes.
- Signs are opaque. Vowels are ignored.

## Cost
About 5 ms per scoring, a few minutes in all on 4 workers. It runs under the Indus compute lock with `nice -n 20` and the memory guard.
