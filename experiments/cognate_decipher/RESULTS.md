# Word-level cognate decipherment (Snyder 2010 / NeuroDecipher style): does it rescue the related-language case?

Computational decipherment specialist, 2026-11-14. Code: `wm.py` (model), `common.py`, `data.py`, `c1_linearb.py`, `c2_planted.py`, `c3_minimal.py`, `c4_bootstrap.py`, `summarize.py` (run from this folder: `cd experiments/cognate_decipher && ../../.venv/bin/python c1_linearb.py`). Logs and raw numbers: `out/*.log`, `out/*.json`; tables: `out/tables.md`; key numbers: `results.json`.
External data fetched: `ext/neurodecipher/` (Luo et al. 2019 Linear B-Greek cognate list, 919 pairs), `ext/greek/` (Perseus Iliad + Odyssey).

## Conclusion first

1. **The word-level matcher works when its lexicon contains the words.** On real Linear B with the Greek cognate list (the NeuroDecipher setting), blind search reads **80-91% of sign tokens** correctly from 230-919 words (871-3,451 tokens). Greek beats every wrong-language lexicon, a shuffled lexicon and a shuffled corpus by a wide margin (score 2.85 vs ≤1.44 nats/token).
2. **With a realistic lexicon it does not read signs, at any size we tested.**
   - Linear B against the 10,000 commonest Homeric word types (only 15.6% of Linear B words have a cognate form in it): **1-14%** recovery from 1,727 to 13,000 tokens.
   - Planted Sanskrit names read with Pali/Prakrit: **5% / 21% / 24%** at 2.5k / 10k / 40k tokens.
   - Planted Tamil names read with Malayalam: **6% / 19-39% / 30%** at 2.5k / 10k / 40k tokens.
   - That is the same 10-26% band as the syllable-bigram key search in `experiments/decipherability`. The word-level model does not change that conclusion.
3. **What does change: the word-level objective usually prefers the truth. The search cannot reach it.**
   - The bigram search had wrong keys outscoring the true key in 88-100% of K2 runs.
   - Here, EM started from the true key reaches a *higher* score than the best blind restart in 21 of 25 realistic-lexicon runs (7 Linear B/Homer, 9 natural true-language, 9 related-language). All 4 exceptions are Sanskrit with Pali, where a wrong key wins.
   - At its own optimum, the true-key basin reads only **0.48-0.56** of signs (Linear B/Homer), **0.51-0.61** (Sanskrit/Pali) and **0.75-0.83** (Tamil/Malayalam).
   - So even a perfect search with a related lexicon caps out around half to three quarters.
4. **Language identification works only when the lexicon contains enough exact forms.** The statistic is the paired bootstrap of the matching score, 2,000 resamples:
   - **Works:** Greek (Homer) beats Latin, Sanskrit, Finnish, Sumerian and Tamil lexicons on Linear B words, raw-score CIs all > 0 (e.g. +0.065 [+0.038, +0.091] nats/token vs Sumerian). Malayalam beats Latin, Finnish, Sumerian and Sanskrit on planted Tamil, and is first in all 4 Tamil cells.
   - **Fails:** Pali/Prakrit comes **last of 5** on planted Sanskrit in every cell: 2.5k, 10k, 10k with 20% logograms, 40k, and undivided texts. All wrong lexicons beat it, e.g. Latin by 0.183 [0.164, 0.201] nats/token. Pali covers only 6-7% of the planted word tokens exactly; Malayalam covers 17-19% of Tamil.
   - Malayalam also "reads" planted Sanskrit better than Pali does (36% of signs at 40k), through its Sanskrit loanwords. A loan stratum makes a wrong language fit.
5. **Indus was not run (task step 3), as the gate required.** The controls fail on the realistic case. Indus is also harder on every axis that mattered:
   - no word dividers;
   - candidate words of 1.4-2.4 signs (`structure` DP segments 1.44 tokens on average; `functional_reading` noun/name runs 2.4), against 3.75 for Linear B;
   - unknown logogram share;
   - the best available Proto-Dravidian list has 380 reconstructed roots (Wiktionary), while the matcher needs about 30-50% of the corpus's word *types* present in the lexicon (finding 3).
   - On the controls, a ranking from an Indus run could not be read as evidence for any language.
6. **Minimal conditions for word-level matching to identify a language at 10k tokens** (planted, word-divided, no logograms):
   - **Coverage.** The lexicon contains ≥ 50% of the corpus's word types with ≤ 10% irregular edits (Sanskrit 0.75-0.99, Tamil 0.93-1.00), or ≥ 30% exactly (Sanskrit 0.52, Tamil 0.90).
   - **Regular sound change is harmless.** A consistent shift of 30% of values costs nothing (0.96-1.00). Irregular change is what hurts (Sanskrit 0.99 → 0.92 → 0.76 at 10 / 20 / 30% edits).
   - **Word length.** Words average ≥ 3.5 signs.
   - **Size.** More text helps only once coverage is there. With exactly 20% coverage, 10k → 40k tokens raises recovery from 0.54 to 0.89 (Sanskrit) and 0.47 to 0.61 (Tamil). With natural Pali coverage (6-7%) it goes from 0.21 to only 0.24.
   - **For identification:** exact-form token coverage ≥ ~15-20% by the true lexicon and below that by every rival (Malayalam/Tamil yes; Pali/Sanskrit no).
   - **Mapping to Indus.** A dated, attested lexicon of the Harappan language itself (not a reconstructed proto-language, not a sister language 1,000+ years later) would be needed, plus word division. No candidate lexicon for Indus meets this.

## Method

**Model (`wm.py`).**
- **Candidate words.** Inscription words are distinct sign sequences.
- **Lexicon.** Entries are value sequences in the shared 101-value CV/C/V alphabet (`experiments/decipherability/langdata.py`).
- **Pair score.** A Viterbi edit alignment gives a log-likelihood ratio against a sign-unigram null:
  - substitution log P(s|b) − log P(s);
  - an unwritten lexicon value has learned probability Pdel(b) (prior 0.35 for bare consonants, as in Linear B spelling);
  - an inserted sign costs log 0.01.
- **Cognate kernel.** Counts are smoothed over phonetically close values: same consonant / other vowel 0.15, same vowel and same place of articulation 0.15. This makes P(s|b) tolerant of regular sound change.
- **Objective.** Exact maximum-weight **one-to-one** matching between words and lexicon entries over the top-8 candidates per word (scipy `min_weight_full_bipartite_matching`, with a dummy "unmatched" column for each word).
- **Learning.** Hard EM alternates matching with re-estimating P(s|b) and Pdel from the Viterbi alignments of matched pairs.
- **Restarts.** 16-24 per run. Half start from frequency-rank keys and half from uniform random keys; every other restart gets a deterministic-annealing soft-EM warm-up (T 8 → 1, Gumbel noise). The best final matching score is the blind answer.
- **Oracle.** The same EM is also started from the true key, which tells search failure apart from objective failure.
- **Accuracy.** The token-weighted share of syllabic signs whose argmax aligned value equals the truth. "Cons" credits the right consonant only.
- Logograms are allowed implicitly: a one-sign word can match a whole lexicon entry with deletions. They are scored as wrong when accuracy is computed.

**Controls.**
- **c1, real Linear B (DAMOS + Luo et al. cognates).** L1: 919 cognate words vs their Greek forms (1,414 entries). L2: the same words vs Homer's 10k commonest types. L3: all 3,560 distinct complete DAMOS words vs Homer 10k.
  - Rivals: equal-size random type samples from Latin (Caesar), Sanskrit (MW + sa.wiki), Finnish, Sumerian and Tamil, plus Greek with values shuffled across entries and Greek against a sign-shuffled corpus.
- **c2, planted.** Rigveda name/epithet chunks (Sanskrit, real) and Tamil synthetic name templates are written in a random CV syllabary, with the commonest words as logograms (0 or 0.2 of tokens). Corpora have 2.5k / 10k / 40k tokens. Units are true words ("gold") or whole undivided texts ("text").
  - Lexicons have 5,000 entries:
    - **K1inj_p:** a true-language lexicon holding a fraction p of the corpus's word types;
    - **K1:** natural true-language types;
    - **K2:** the related language;
    - **W/R:** wrong languages;
    - **K2shuf:** K2 with values shuffled across entries.
  - Every lexicon is also run on a sign-shuffled corpus ("gain" = real − shuffled score per token).
- **c3, minimal conditions.** The fraction of word types present (p), the irregular per-value edit rate (e) and the regular systematic shift (30% of values) are varied. Linear B: Homer 10k with 25/50/75% of the true cognate forms injected.
- **c4, paired bootstrap** of per-word matching scores: true or related lexicon vs each rival, 2,000 resamples.

Test count: 7 Linear B conditions × 8 lexicons, 9 planted cells × 9-10 lexicons (+ shuffles), 21 minimal-condition runs, 3 bootstrap panels (15 comparisons). No held-out Indus data was touched.

## Findings

### F1. Real Linear B (`c1_linearb.py`, `out/c1_linearb.json`)

| condition | words / tokens | lexicon | blind acc (cons) | oracle-start acc | cognate pairs right | Greek score/tok | best wrong | Greek, values shuffled | corpus shuffled |
|---|---|---|---|---|---|---|---|---|---|
| L1 | 230 / 871 | 1,414 cognate forms | **0.80** (0.81) | 0.84 | 0.77 | 2.58 | 1.82 Finnish | 1.75 | 1.73 |
| L1 | 460 / 1,731 | same | **0.91** (0.91) | 0.92 | 0.93 | 2.86 | 1.64 Latin | 1.54 | 1.52 |
| L1 | 919 / 3,451 | same | **0.87** (0.87) | 0.87 | 0.94 | 2.85 | 1.44 Sumerian | 1.33 | 1.30 |
| L2 | 460 / 1,727 | Homer 10k | 0.02 (0.23) | 0.56 | 0.01 | 2.02 | 1.97 Sumerian | 1.91 | 1.85 |
| L2 | 919 / 3,451 | Homer 10k | 0.14 (0.32) | 0.56 | 0.01 | 1.93 | 1.89 Sumerian | 1.80 | 1.69 |
| L3 | 1,780 / 6,565 | Homer 10k | 0.01 (0.18) | 0.48 | 0 | 1.87 | 1.83 Sumerian | 1.74 | 1.65 |
| L3 | 3,560 / 13,000 | Homer 10k | 0.03 (0.29) | 0.54 | 0 | 1.78 | 1.76 Sumerian | 1.65 | 1.57 |
| L2 + 25 / 50 / 75% cognates injected (c3) | 919 / 3,451 | Homer 10k + 216 / 438 / 616 | 0.00 / 0.00 / 0.07 | 0.75 / 0.85 / 0.85 | | | | | |

- L1 reproduces the published NeuroDecipher result: Luo et al. report 84% cognate accuracy, we get 77-94%, and this matcher also recovers the sign values.
- The L1 result is what "the lexicon is the answer key" looks like. Each Linear B word's cognate is in a 1,414-entry list.
- In L2/L3 the oracle-start score beats the blind score in every run. This is a search failure: blind restarts lock onto short spurious matches against 10k forms.
  - Even with 75% of the true cognates injected into Homer 10k, blind recovery stays ≤ 0.07, while the oracle basin reads 0.85.
  - Identification still works in L2 (F4), but reading does not.

### F2. Planted Sanskrit / Tamil at Indus size (`c2_planted.py`, `out/c2_main.json`, `out/c2_rest.json`, `out/c2_tam40.json`)

Blind sign accuracy (token-weighted), gold word division unless noted:

| lexicon | san 2.5k | san 10k | san 10k logo .2 | san 10k undivided | san 40k | tam 2.5k | tam 10k | tam 10k logo .2 | tam 40k |
|---|---|---|---|---|---|---|---|---|---|
| K1inj 1.0 (all words present) | 0.99 | 1.00 | 1.00 | - | - | 1.00 | 1.00 | 1.00 | - |
| K1inj 0.5 | 0.82 | 0.99 | 0.91 | - | - | 0.62 | 0.96 | 0.98 | - |
| K1inj 0.2 | 0.25 | 0.54 | 0.22 | 0.57 | **0.89** | 0.23 | 0.47 | 0.52 | 0.61 |
| K1 natural (coverage san 5-9%, tam 32-44%) | 0.36 | 0.25 | 0.48 | 0.50 | 0.52 | 0.35 | 0.47 | 0.28 | 0.41 |
| **K2 related** (Pali 6-7%, Malayalam 11-20% coverage) | **0.05** | **0.21** | **0.20** | **0.17** | **0.24** | **0.06** | **0.39** | **0.19** | **0.30** |
| K2 oracle-start acc | 0.60 | 0.60 | 0.54 | 0.51 | 0.61 | 0.83 | 0.78 | 0.79 | 0.75 |
| best wrong-language acc | 0.06 | 0.23 (Malay.) | 0.18 | 0.19 | 0.37 (Malay.) | 0.10 | 0.11 | 0.11 | 0.10 |
| K2 values shuffled | 0.00 | 0.12 | 0.00 | - | - | 0.00 | 0.00 | 0.07 | - |

- **K2 is flat** from 2.5k to 40k in the 0.2-0.4 band, as in the bigram study.
- **The search-vs-objective split.** With K2, a wrong key beats the oracle basin for Sanskrit (4 of 5 cells) but not for Tamil (0 of 4).
- Undivided texts (Indus-like) do not hurt here when the lexicon is good. K1 accuracy is actually higher (0.50 vs 0.25, one replicate), because whole short texts align to single long entries. With K2 it is equally bad (0.17).

### F3. Minimal conditions (`c3_minimal.py`, `out/c3_minimal.json`), 10k tokens, word-divided, no logograms

| fraction of word types in lexicon | irregular edits per value | 30% values regularly shifted | Sanskrit acc | Tamil acc |
|---|---|---|---|---|
| 1.0 | 0 | yes | 0.998 | 1.000 |
| 1.0 | 0.1 | no | 0.993 | 0.999 |
| 1.0 | 0.2 | no | 0.920 | 0.981 |
| 1.0 | 0.3 | no | 0.758 | 0.976 |
| 1.0 | 0.2 | yes | 0.962 | 0.974 |
| 0.5 | 0.1 | yes | 0.755 | 0.928 |
| 0.5 | 0.2 | no | 0.267 | 0.824 |
| 0.3 | 0 | no | 0.517 | 0.895 |
| 0.3 | 0.1 | no | 0.270 | 0.814 |

- The oracle basin is ≥ 0.97 in every row. Failures are search failures, so better optimisers could push these thresholds down somewhat.
- They cannot help the natural K2 case, where the oracle basin itself is only 0.5-0.8.
- Tamil is easier than Sanskrit because its synthetic names reuse a smaller, Zipfian name pool: 1,240 word types vs 1,786 at 10k.

### F4. Language identification with paired bootstrap CIs (`c4_bootstrap.py`, `out/c4_bootstrap.json`)

The statistic is the reference lexicon's matching score minus the rival's, in nats per token, with a 95% bootstrap CI over words. "Gain-adjusted" also subtracts each lexicon's score on a sign-shuffled corpus, a point estimate with the shuffle treated as fixed.

| corpus | reference | vs Latin | vs Sanskrit | vs Finnish | vs Sumerian | vs Tamil / other Indian | vs true-language K1 |
|---|---|---|---|---|---|---|---|
| Linear B 919 words (3,451 tok) | Greek Homer 10k | +0.163 [0.137, 0.189]; adj +0.026 | +0.120 [0.093, 0.145] | +0.079 [0.052, 0.105] | +0.065 [0.038, 0.091] | Tamil +0.076 [0.050, 0.102] | - |
| planted Sanskrit 10k | Pali/Prakrit (K2) | **−0.183** [−0.201, −0.164] | - | −0.166 [−0.184, −0.147] | −0.110 [−0.127, −0.093] | Malayalam −0.181 [−0.200, −0.163] | −0.142 |
| planted Tamil 10k | Malayalam (K2) | +0.035 [0.023, 0.046] | +0.134 [0.118, 0.148] | +0.038 [0.027, 0.049] | +0.070 [0.058, 0.082] | - | +0.008 [−0.004, 0.019] |

- Greek is identified on Linear B, and Malayalam on planted Tamil.
- **Pali is "identified" as the worst fit for Sanskrit.** That is a strong, significant wrong answer: a decipherer using this method with a Middle Indo-Aryan lexicon would reject Indo-Aryan.
- With only 5 rival languages, the ranking alone gives p ≥ 0.2. The CIs cover sampling of words, not the choice of lexicons (lexicon size, genre and loan strata), and that choice is what drove the Sanskrit failure.

## Hypotheses

| hypothesis | verdict |
|---|---|
| H1 Word-level matching with a one-to-one constraint recovers sign values when the lexicon contains the words (Linear B + cognate list; planted, ≥ 50% coverage) | **supported** (0.80-1.00) |
| H2 It recovers sign values at Indus size with a realistic related or later-stage lexicon (Homer for Linear B; Pali for Sanskrit; Malayalam for Tamil) | **refuted** (0.01-0.39 blind, flat 2.5k-40k) |
| H3 It removes the "wrong keys outscore the true key" pathology of character-LM search | **mostly supported**: the true basin wins in 21/25 realistic-lexicon runs, but its accuracy is only 0.5-0.85 and blind search does not reach it |
| H4 The true or related language outranks wrong languages and shuffles | **inconclusive / lexicon-dependent**: yes for Greek (Linear B) and Malayalam (Tamil), significantly **no** for Pali (Sanskrit, ranked last) |
| H5 Controls justify running Indus vs Proto-Dravidian / Old Tamil / Vedic / Proto-Munda / Elamite / Sumerian | **refuted**: not run |
| H6 More inscriptions help | only once ≥ 20% exact coverage exists (0.54 → 0.89 Sanskrit); not with natural related lexicons (0.21 → 0.24) |

## Caveats and how this could mislead

- **Optimistic for the decipherer.** Planted corpora have known word division (except the "text" cell), no polyphony and no scribal error. Linear B words average 3.75 signs, against Indus's 1.4-2.4-sign units.
- **Possibly pessimistic.**
  - The blind search (hard EM + soft annealing, 16-24 restarts) leaves the oracle basin unreached in most realistic runs. A stronger search (NeuroDecipher's neural edit model with flow regularisation, or anchoring via proper names) might narrow the gap between blind accuracy and the 0.5-0.85 oracle basin, but not exceed it.
  - Our lexicons are ASCII-folded and merge length, aspiration and retroflexion, as in the bigram study.
- **Single replicates per cell** (time limit). Differences under about 0.1 in accuracy are within replicate noise; the bigram study saw ±0.1-0.2. The robust patterns are the K2 band (0.05-0.39 across 9 cells), the coverage thresholds and the Pali-last result (5 of 5 cells).
- Tamil names are synthetic templates; Malayalam and Tamil wiki lexicons may share modern vocabulary. The Tamil success is likely an upper bound for a sister-language lexicon.
- Wrong-language lexicons are frequency-ranked types from wiki/prose. Their short, frequent forms fit short name words well. That is the mechanism behind the Pali failure, and it would equally affect an Indus run.

## What would falsify the main claim

A blind word-level search reading > 50% of sign values on a planted name corpus of ≤ 10k tokens with a natural related-language lexicon (exact coverage < 10%). Or the related language ranking first with bootstrap CIs > 0 in ≥ 4 of 5 planted language pairs.

## Next experiments

1. **Search, not model.** Since the true basin usually wins, run a stronger optimiser on the realistic Linear B/Homer and Tamil/Malayalam cases: population-based EM, NeuroDecipher's neural edit model, or proper-name anchors. Measure how much of the 0.5-0.85 oracle basin it reaches. If it reaches it, the Linear B/Homer case (no injected cognates) becomes the benchmark any Indus claim must pass first.
2. **Indus-shaped words in the planted controls.** Cap word length at 1-3 signs and use the `functional_reading` noun/title slots as units, to check whether identification survives at Indus word lengths. We expect it not to: with 1-2-sign words, every lexicon has a short-form match.
3. If anyone proposes a Harappan-era lexicon (for example Meluhhan words in cuneiform, queue item 5), it is the only kind of lexicon these controls say could work. Test it as a held-out *matching* prediction, not as a key search.
4. A machine-readable DEDR (DSAL hosts it as HTML: https://dsal.uchicago.edu/dictionaries/burrow/; Starostin's Tower of Babel `dravet` database is reachable) would give about 5,000 Proto-Dravidian entries instead of 380. It is still a reconstructed proto-language, which F2/F3 say is not enough on its own.
