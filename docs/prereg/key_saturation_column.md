# Key saturation column: what share of consonants do random keys read under a claimant's own rules?

Status: **DROPPED pre-seal, 2026-11-25 (coordinator decision).** Never sealed, no code, nothing scored. A second fresh review of v2 found that the K0 fail is fixed by arithmetic from already-sealed numbers (the ordered share is capped near 62% against an 80% bar), and that fallback 1 would stop the run (80 and 61 length-6 segments, under the floor of 100). The raw read shares are to be recorded with a shape caveat instead. The text below is kept as the v2 draft.

## Question
- For each held Indus key that meets the coverage standard: **under the rules as we encode them, what share of consonants do random keys read as dictionary words?**
- Two numbers answer two different questions, and v2 keeps them apart.
  - **R, the raw share,** is the share on the claimant's own texts. It is already in hand for both keys. It moves with text shape.
  - **S, the chance-match rate,** is a property of the lexicon and the rules. It is almost free of the corpus by construction. It is not the share on the claimant's texts.
- **K0 asks whether S says anything about refute power.** It tests, on cells already sealed, whether S orders the pass counts of true keys.
- A "random key" is the claimant's own values moved to other signs. The claimant's unshuffled key is never scored.
- **No outcome supports or counts against any Indus key. None licenses a rerun of one. No label is attached to any key.**

## What the repo already established (not tested again)
| fact | source |
|---|---|
| The Homeric skeleton lexicon is saturated at 1-3 consonants and thins at 4 (0.177) | `lb_certify`, `lb_shape_ladder` |
| LMIN rule: the smallest word length with lexicon density at or below 25% | `lb_shape_ladder` (frozen) |
| Scott v3, M77 distinct: R = 0.703 at LMIN 4 (first alternative only 0.644; swaps off 0.623) and 0.428 at LMIN 5 (0.363; 0.334). Density 0.122 and 0.024 | `scott_ic_refute` K2 |
| Yajnadevam fc8813a, ICIT distinct, LMIN 5: shuffled-key mean IC 0.236 (generous), 0.203 (strict) | `yj_ic_refute` |
| True Linear B key: shuffled-key mean 0.150 (R1), 0.373 (R2), 0.067 (R3); refute 20/20 at each | `lb_shape_ladder` |
| Same key at 1.18 and about 1.8 values per sign: 0.198 and 0.315; refute 17/20 and 2/20 | `lb_formula_dial` |
| Same key at LMIN 5: 0.014; refute 8/20 | `lb_wrong_lexicon` |
| Ur III legends, true reading, LMIN 3: 0.509; refute 0/20. Administrative text, same rules: 20/20 | `ur3_legend_refute` |

- **R is shape-dependent.** Rules fixed, R goes from 0.150 to 0.373 between R1 and R2.
- **Refute power does not simply follow saturation.** LMIN 5 gives 0.014 with 8/20; R2 gives 0.373 with 20/20. K0 below tests this properly, with the bar fixed in advance. On the numbers in hand it is **expected to fail**.

## Prior art
**Opened 2026-11-25** (User-Agent `open-research-site/1.0`; two hosts answered 403 and one a bot check, none retried).
- **Shannon 1949**, "Communication Theory of Secrecy Systems", https://pages.cs.wisc.edu/~rist/642-spring-2014/shannon-secrecy.pdf. The random-cipher model: the expected number of wrong keys that still give acceptable text. A solution on material "of the same order or shorter than the unicity distance" is "highly suspicious".
- **Farmer, Sproat and Witzel 2004**, EJVS 11(2): 19-57, doi 10.11588/ejvs.2004.2.620, opened at the author's copy https://safarmer.com/fsw2.pdf. "By inventing enough rules as you go" one can read any signs in any language. Made in words; no rate is measured.
- **Yajnadevam**, "A cryptanalytic decipherment of the Indus script", https://rarebooksocietyofindia.org/book_archive/A_cryptanalytic_decipherment_of_the_Indu.pdf. The case rests on reading past the unicity distance. A text search found no measured rate at which other keys read the corpus.
- **Pāṇini Protocol**, https://ugrashravas.github.io/paniniprotocol/ (a web page, not reviewed). The same kind of rules applied to unrelated text. No random-key rate.
- **`farhan3011/indus-epigraphy-ai`**, https://raw.githubusercontent.com/farhan3011/indus-epigraphy-ai/main/README.md. Shuffles a claim's own values under a frequency-matched null, with an exploratory dictionary match rate and Linear B, Ugaritic and Linear A controls. It reports percentiles and p-values.
- **Ringe 1992**, doi 10.2307/1006563, http://languagelog.ldc.upenn.edu/myl/Ringe1992.pdf. Chance matches in word-list comparison.
- **Rosenfelder**, https://www.zompist.com/chance.htm. Expected chance matches depend "almost entirely" on how loose the match rules are.

**Not opened (unverified).** Hellman 1977 on spurious keys; von zur Gathen 2021, IACR ePrint 2021/1620 (403); doi 10.3390/cryptography10040060 (403); Sproat 2010 and Rao et al. 2010; Bowern and Lindemann 2021, doi 10.1146/annurev-linguistics-011619-030613; Possehl 1996; Duhoux 2000.

## What was seen before this draft
- Every figure above, and every pass count in the K0 cell list below. **All 33 pass counts are known.** Only S for those cells is not.
- **The reviewer's planted simulation** (synthetic lexicon and texts; no Indus, no Linear B, no real key): S 0.304 against 0.300 across shapes while R moved 2.7 times; a pipeline that ignored the signs also passed v1's K0d; density 0.177 to 0.35 moved S from 0.30 to 0.48.
- **Count gate (label-free).** Coverage and consonant-length counts only; no lexicon, no IC, no key scored.

| key | corpus | token coverage | values per keyed sign | consonants per segment | gate |
|---|---|---|---|---|---|
| Yajnadevam fc8813a (714 readable signs) | ICIT distinct, 13,190 tokens | 100.0% | 1.00 | 3.33 | **yes** |
| Scott v3 (345 keyed, 72 blank) | M77 distinct, 10,005 tokens | 94.4% | 1.18 (1 → 289, 2 → 51, 3 → 5) | 6.20 | **yes** |
| Pierson K185 / K161 | M77 distinct | 74.1% / 67.4% | — | — | no |
| Field-Cady 100-sign table | ICIT | about 82% (`key_hunt`) | — | — | no |

- Segments per consonant length (4, 5, 6, 7): Linear B R1 per draw 112-120, 47-68, 19-24, 6-9; Yajnadevam on ICIT 520, 419, 238, 136. Scott (M77 development texts, counted for v1): 206, 210, 222, 170.
- Scott: 24 keyed signs have alternatives that differ in consonant count.

## Data (all already held)
- **Read scripts:** the sealed builds, keys, lexicons and matchers of `lb_shape_ladder` (and its addendum 1), `lb_formula_dial`, `lb_wrong_lexicon` and `ur3_legend_refute`, imported unchanged.
- **Yajnadevam key:** `sources/yajnadevam_lipi_fc8813a/xlits.csv` (local). **Corpus: the whole distinct ICIT corpus**, as in `yj_ic_refute`.
- **Scott key:** *MahaSamVani: The Lexicon of the Indus Script* v3, doi 10.5281/zenodo.21522783, CC BY-NC-ND. Read from `.local/scott_lis/` at run time only, through the sealed `values.py` and the sealed 7-row overrides file. **No value of this key is written to any file; outputs hold aggregates only.** **Corpus: the whole distinct M77 corpus**, as in `scott_ic_refute`.
- **Lexicons for the Indus cells:** Monier-Williams headwords plus the consonantal endings, at most 7 consonants. A word with a consonant outside the alphabet is dropped whole. This fixes the lexicon bug recorded in the `yj_ic_refute` red team, so those densities are reported afresh.
- **The matchers are our encoding** of each claimant's stated latitude, not the claimant's own procedure.

## The statistics (frozen)
- **Scoring** is the sealed IC: the most consonants coverable by lexicon words of LMIN to 7 consonants, per segment, maximised over the segmentation and over each token's alternative. Ties take the reading with fewer consonants.
- **Random key.** The value sets shuffled across keyed signs inside each consonant-count class (count of the first alternative). Whole alternative sets move together. Blank signs stay blank. 200 keys per cell.
- **Length of a segment, n.** The consonant count with every sign on its **first** alternative.
- **Length curve c(n).** Over all random keys and all segments of length n: consonants covered ÷ **consonants of the chosen readings**. So when alternatives differ in consonant count, the denominator is the chosen reading's count, as in the sealed IC; only the bin uses the first alternative.
- **S.** The plain mean of c(4), c(5), c(6), c(7). **The reference lengths are 4 to 7 in every cell, whatever its LMIN.** In the Ur III cells (LMIN 3) words of 3 consonants count towards coverage; c(3) is reported and is not part of S.
- **R.** The random keys' mean IC over the whole text. Reported beside S.
- **LMIN** is set per lexicon and matcher by the frozen 25% rule. The other of LMIN 4 and 5 is reported as record-only.

## Checks, in this order (no Indus key is loaded before step 3 is done)

### 1. Pipeline
- **P1.** The true Linear B key on R1 gives 20 of 20, scrambled 0, every per-draw value equal to the sealed R1 to 1e-9.
- **P2. Known answers.** An empty lexicon gives S = 0 exactly. A lexicon of every string of 4 to 7 letters gives S = 1 exactly. A random lexicon of density 0.20 at length 4 only, on uniform random letters: c(4) = 0.200 ± 0.010 and c(5) = 0.288 ± 0.015.
- **P3. Planted repeated-sign text.** Lexicon: only the strings of 4 identical letters. Key: every sign has one consonant, and no two signs share a letter.
  - Text A, segments of one sign written 4 times: c(4) = 1 exactly, for every random key.
  - Text B, segments of 4 different signs: c(4) = 0 exactly.
  - A pipeline that ignores which signs are in the text fails both.
- **P4. Identity check** (v1's K0d, demoted). Linear B R2 against R1, same rules: |ΔS| ≤ 0.02, and R on R2 at least 1.5 times R on R1. S should agree here by construction; the check only catches code errors. The Ur III pair is not used: it also changes the sign inventory.
- **P5.** Scott's R on the whole distinct corpus, with the sealed K2 seeds, equals the sealed 0.7030797712 (LMIN 4) to 1e-9. This runs with the Indus cells, after step 3.
- Any failure: "pipeline error". Nothing is read.

### 2. Anchors (descriptive; no bar)
S, c(n) and R for the true Linear B key's rules at 1.0, 1.18 and 2.0 nominal values per sign on R1, and at LMIN 5.

### 3. K0: does S order refute power across the sealed cells?
- **Cells, fixed now (33).** Every sealed cell in which a true key or true reading was scored against a lexicon in the text's own language, with an interpretable control. Pass counts are taken from the sealed JSON, out of 20, with unbuilt draws as non-passes.

| study | cells (passes of 20) |
|---|---|
| `lb_shape_ladder` + addendum 1 | R0 13, R1 20, R2 20, R3 20, R95 20, R90 17 |
| `lb_formula_dial` | F0×1.18 17, F0×2.0 2, F1×1.0 16, F1×1.18 12, F1×2.0 2, F2×1.0 10, F2×1.18 6, F2×2.0 1 |
| `lb_wrong_lexicon` | G×F0×L4 17, Od×F0×L4 20, H×F0×L5 8, H×F1×L5 6, B1×F0×L4 19, B1×F1×L4 17, B2×F0×L4 18, B2×F1×L4 15, B1×F0×L5 8, B1×F1×L5 8, B2×F0×L5 7, B2×F1×L5 5, B3×F0×L5 9, B3×F1×L5 5 |
| `ur3_legend_refute` | K3 administrative 20, L1 0, L2 0, L3 12, L5 13 |

  - Left out, by rule: duplicates of R1 and F1×1.0; the wrong-language lexicons (Fi, Hu, Id, Es); Ur III L4 (control not interpretable); `null_width`, which sealed null widths and no true-key pass counts.
- **S per cell** is computed on that cell's own sealed held-out draws, pooled, with its own lexicon, matcher, value sets and LMIN.
- **Test (one-sided; prediction: higher S, fewer passes).** Take every pair of cells whose pass counts differ by 4 or more. A pair is **ordered** if the cell with fewer passes has S higher by more than 0.02. Ties and reversals are not ordered.
- **Bar: at least 80% of those pairs are ordered.**
- Reported beside it, deciding nothing: the same share with R in place of S, and Spearman's rank correlation of each with the pass count.
- **Disclosure.** The pass counts are known and S is partly guessable from the shuffled-key means in hand. Cells that share rules but differ in passes (R1 against F2×1.0; Ur III administrative against L1) cannot be ordered by S, and the LMIN 5 cells pair low saturation with few passes. So a fail is the expected outcome.

### 4. Indus cells (run whether K0 passes or fails, after steps 1 to 3)
| cell | corpus | rules as encoded | LMIN by the rule |
|---|---|---|---|
| Y-gen | ICIT distinct | Yajnadevam fc8813a, generous matcher | computed |
| Y-str | ICIT distinct | same key, strict matcher | computed |
| S-full | M77 distinct | Scott v3, full stated rules as parsed | computed (4 at the sealed density 0.122) |
| S-first, S-noswap, S-noq | M77 distinct | first alternative only; sound swaps off; the 15 "?" entries blanked | as S-full; record-only |

- **Yajnadevam is reported as a range** from the strict to the generous matcher. Neither is "his".
- Scott's sealed bench ended on LMIN 5 through its K2 fallback; that value is reported as record-only beside the rule's LMIN.

## Calibration fallbacks (written before any calibration)
Only these are allowed. **Any other change after a number is seen makes the study INVALID**, and it is reported as invalid.

1. **Thin lengths.** A reference length with fewer than 100 segments in any cell (pooled over its draws) is dropped from S for **every** cell and key. Lengths 4, 5 and 6 must remain; otherwise STOP, "not enough long segments".
2. **Unbuilt draws.** Draws the sealed studies could not build are not rebuilt. S uses the built draws; the pass count stays out of 20.
3. **The 2.0 rung** is used as built (1.78 actual).
4. **Monte Carlo error.** If the standard error of any cell's S exceeds 0.005 at 200 keys, the number of keys is doubled once, to 400, for every cell.
5. **No label.** There is no cut, band or threshold on S or R, and none may be added after any number is seen.

Not allowed, among other things: another reference set or weighting, moving the 80%, 4-pass or 0.02 figures, adding or dropping a K0 cell, a second ordering statistic as the test, or a rerun.

## Readings (frozen; descriptive, worded for the bench)
- **Any pipeline check fails:** "pipeline error". Nothing else is read.
- **K0 fails:** "No corpus-independent column. S is reported only as a lexicon-and-rules chance rate."
- **K0 passes:** "Across 33 sealed cells on two read scripts, a higher chance-match rate went with fewer refute passes in at least 80% of pairs."
- **In both cases the Indus cells are reported as numbers only:** S, c(4) to c(7), R, density, alphabet size and values per sign, beside the same figures for the Linear B anchors. No key is placed in a class.
- **What the numbers can say.** S: how often runs of 4 to 7 consonants made by keys with no information contain dictionary words, under this lexicon and these rules as encoded. R: the same share on that key's own texts.
- **What they cannot say.**
  - Whether a key is right or wrong. A true key and a wrong key under the same rules get the same S and R.
  - Whether a key can be tested by fit. That question was answered by the sealed benches, and their verdicts stand unchanged.
  - Anything about evidence from outside fit.
  - How two keys compare on their texts: R differs with segment length, and the two keys use different corpora and lexicon encodings.
- S and R are **lower bounds** on the freedom in use: unmodelled rules (insertions and deletions in readings, sign-order rules, rare rule breaks) can only raise them.
- No number changes a scorecard tier.

## Scorecard
- This study does not edit the scorecard.
- **Coordinator follow-up, outside this study:** the raw figures already sealed (Scott 0.703 and 0.428; Yajnadevam 0.236 and 0.203) are to be copied to the scorecard now, marked "shape-dependent". That needs no run.
- Whether S is added later is decided after K0, through a sealed scorecard addendum.

## Aborts
- **A1.** P1 does not reproduce to 1e-9: stop.
- **A2.** Any count differs: Scott 345 keyed, 72 blank, alternatives 289 / 51 / 5, coverage 94.4%, overrides file 7 rows with the sealed sha256; Yajnadevam 714 readable signs, 3,249 texts, 11,752 consonants; any sealed pass count in the K0 table against its JSON; the sealed Ur III counts. Stop and redraft.
- **A3.** A K0 cell cannot be rebuilt from its sealed code: stop. No cell is dropped.
- **A4.** The Indus compute lock is not held through `board/run.sh`, or free memory is below the 20% guard: do not start.
- **A5.** Any output would hold a sign-level value, a shuffled key or a reading: stop.
- No rerun, no tuning, no fix tags after any S is seen.

## Seeds
- Base seed 20261210 (unused elsewhere). Known-script builds use their sealed seeds, unchanged.
- Random keys: cell index j (K0 table order from 0, then the anchors, then the Indus cells), draw k: base + 100,000 j + 1000 k; 200 keys in sequence from one generator. Indus cells use k = 0.
- Scott's R for P5 uses the sealed K2 seeds of `scott_ic_refute`.
- P2 and P3: base + 9,000,000; 5,000 segments per length.
- If fallback 4 fires, keys 201 to 400 continue the same generators.

## Limits stated in advance
- K0 is a test on known pass counts, so it is closer to a fixed-rule reanalysis than a blind test.
- The 33 cells are not independent: 28 share one script and most share one lexicon. No significance is claimed for the 80% share.
- The 80%, 4-pass and 0.02 figures are judgements.
- The lexicon build (headwords plus five endings, at most 7 consonants) and both matchers are ours.
- Shuffles keep the claimant's value set, so the letter mix is the claimant's own. About 7.5% of tokens keep their value by chance under Scott's shuffles.
- The same rules on unrelated text (the Pāṇini Protocol kind of control) is not run.

## Cost
- Single process, `nice -n 20`, under the lock and `board/run.sh`, only when the lock is free. About 33 cells × 20 draws × 200 keys, plus 6 Indus cells. Estimated under an hour, most of it the Ur III load. Outputs: `kill.json`, `full.json`, small.

## Decisions
Written in (coordinator, 2026-11-25):
1. Whole distinct corpora for both keys.
2. Our matcher is our encoding: generous and strict are reported as a range, with LMIN by the frozen 25% rule.
3. The raw figures go to the scorecard now, marked shape-dependent, as a coordinator follow-up.
4. No labels and no power wording.
5. v2 is to be sealed and not run.

Open:
1. **The K0 bar** (80% of pairs, 4 passes apart, 0.02 in S) and the 33-cell list need the reviewer's OK.
2. **`null_width` is left out of K0** because it sealed no true-key pass counts. Say if a width-based cell should be added.
3. **Is K0 worth running at all?** Its fail is expected. If it is never run, the sealed draft still records the definitions of R and S.

## Before sealing
- A fresh review of v2, then the prereg hash. Code and its hash only if a run is approved.

## Review log
- **v1 (2026-11-25):** first draft.
- **v2 (2026-11-25): fresh review, REDESIGN.** Findings: (1) v1's K0d was not a kill, since c(n) under the class shuffle is fixed by the value set and the lexicon; (2) S is a chance-match rate, a different quantity from R; (3) the labels were tunable and already contradicted by sealed results. Changes: labels and power wording removed; K0d demoted to an identity check on one Linear B pair; a planted repeated-sign check added; new K0 on 33 sealed cells with the bar fixed; fallback 5 replaced by "no label"; the denominator for unequal alternatives and the Ur III reference lengths defined; whole distinct corpora; matchers reported as a range with LMIN by the 25% rule; the novelty line dropped; the scorecard follow-up noted. No count or score was run for v2.
