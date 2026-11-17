# Pre-registration: validated positional grammar of the Indus seal text (experiments/grammar)

Written 2026-11-14, after dev-only development and a dev-only dry run of the validation code, and BEFORE any
held-out M77 text, any Gulf seal, any ICIT-only-site text or any Ur III test family was scored by this
pipeline. This file, `glib.py`, `step1_classes_seeds.py`, `validate.py`, `classes_m77.json`, `classes_wells.json`,
`sign_classes.csv`, `grammar.json` and `step2.json` are hashed in `docs/prereg/HASHES.txt` (tag `grammar`).
Fable plan 6, part B.

## The model being tested (frozen)

- **Grammar.** Hard class bigram over signs ("class HMM, one class per sign"):
  P(text) = P(c1|BOS) P(s1|c1) prod P(c_i|c_{i-1}) P(s_i|c_i) P(EOS|c_L).
  Signs seen once in training are emitted as `<UNK>`; every model below uses the same vocabulary and UNK rule.
- **Classes.** Induced on M77 dev (`dev_heldout(version=2)`, 1,698 distinct texts) by the exchange
  algorithm, initialised from earlier experiments' role seeds (functional_reading lexicon, structure sign table)
  plus random restarts, best training likelihood kept. K = 16 chosen by dev BIC (grid 8-50); add-alpha
  transition smoothing alpha = 3 chosen by 5-fold family CV on dev. Classes are named by fixed positional rules
  (`glib.name_classes`). Final validated sign labels (`sign_classes.csv`) need bootstrap stability >= 0.7
  (200 family bootstraps) and agreement with the Wells-list run where the sign is bridged; functional classes are
  kept only if they occur under both lists, token-weighted stability >= 0.7 and bridged agreement >= 0.5 and
  above a permutation 95th percentile. Kept: opener, medial, connective, closer. Dropped: numeral (stability 0.47,
  agreement 0.35), post-closer (stability 0.67).
- **Wells grammar.** The same pipeline on 3,049 ICIT texts at Indus sites with no near-copy of an M77
  held-out text: K = 20 (BIC), alpha = 3 (CV).
- **Development disclosure.** The class-keep rule was changed once on dev, from unweighted to token-weighted
  member stability, after a 10-bootstrap trial in which the unweighted rule dropped every class except
  connective and closer. No held-out data had been seen.

Dev numbers that set expectations (no held-out data): 5-fold family CV within dev, bits per event
(signs + end of text): grammar K=16 5.24, KN bigram 4.93, position-only 5.89, unigram 6.01. BIC on dev
favours the grammar (67,277 vs 74,438), AIC favours the bigram (63,570 vs 55,025). Dry run (dev split 50/50 by
family): grammar - bigram +0.46 bits [0.35, 0.58]; restoration top-5 grammar 0.50 vs bigram 0.62 vs
position 0.34; transfer MD -> Harappa grammar - bigram +0.21, small sites +0.12 (in-domain +0.27); Ur III at
Indus size: grammar - bigram +0.08 [-0.11, +0.25]. **I expect a1, b2 and c-big to fail, and primary (e) to fail
on SERV.**

## Validations (all run once by `validate.py final`)

Unit: distinct texts; perplexity on complete texts only (no `#`, beginning and end preserved, line breaks
dropped). CIs: 2,000 bootstrap resamples of held-out text families (restoration: of texts).

**(a) Held-out perplexity.** Train on all dev; test on complete held-out v2 texts. Models: grammar (frozen
assignment, refitted on dev), interpolated Kneser-Ney bigram, position-only (sign | position from start, capped
at 4, + stop probability), unigram, grammar re-induced on within-text-shuffled dev, grammar scored on shuffled
held-out texts (20 shuffles), 7-state functional grammar, register-aware grammar.
- a1 (primary): grammar beats the bigram: 95% CI of (grammar - bigram) bits/event entirely below 0, AND fewer
  parameters (grammar: class-transition cells + emissions; bigram: observed bigram types + continuation
  distribution). AIC and BIC on the dev fit are reported, not tested.
- a2: grammar beats position-only and the shuffled-trained grammar (both CIs below 0).
- a3 (secondary): register-aware grammar (beta = gamma = 50, chosen on dev) beats the pooled grammar (CI below 0).

**(b) Masked restoration.** Every position of every complete held-out text with 2+ signs; candidates = the
dev vocabulary without `<UNK>`; a hidden `<UNK>` sign counts as a miss for identity.
- b1: grammar top-5 identity accuracy above position-only (text-bootstrap CI of difference above 0).
- b2: grammar top-5 not worse than the bigram by more than 0.03 (lower CI bound of difference > -0.03).
- b3: functional-label top-1 accuracy >= 0.60 and above position-only (CI above 0).
  Also reported: MRR, fine-class top-1/top-5, top-1 on validated classes, unigram baseline.

**(c) Transfer.** Grammar re-induced on the training set with K = 16, alpha = 3 and seeds; bigram,
position-only, unigram on the same training set.
- c1: train all M77 Mohenjo-daro distinct texts (dev + held-out); test Harappa, and small sites (Lothal,
  Kalibangan, Chanhu-daro, other sites), excluding texts identical to a training text.
- c2: train all M77 distinct texts; test ICIT texts from Indus sites absent from M77 (sites other than
  Mohenjo-daro, Harappa, Lothal, Kalibangan, Chanhu-daro; foreign and unknown excluded), mapped to M77 through the
  bridge (unbridged = `<UNK>`); all, fully bridged only, seals only.
- Tests, on every target set with >= 10 complete texts: c-big (primary) grammar beats bigram (CI below 0);
  c-pos grammar beats position-only (CI below 0); c-gap the grammar's deficit to the bigram is smaller on the
  target than in 5-fold in-domain CV (point estimate, every target).

**(d) Negative control: Gulf round seals.** Wells grammar trained on the 3,049 dev-like ICIT texts; Gulf round
or cylinder seals (ICIT, foreign West-Asian/Central-Asian sites, types SEAL:R/C/CY, all 18, breaks allowed) scored
per text in bits/event; compared with native ICIT square seals scored by 5-fold family CV, matched on number of
signs (capped at 6) and completeness, 10,000 matched draws.
- d (primary): Gulf mean bits higher, one-sided matched-draw p < 0.01.
- Secondary: foreign square seals (expected not significantly worse, as in context Q4); home round seals vs
  native square (format control, dry run: +0.18, p = 0.01 on dev-like data, so format alone adds a little);
  KN bigram as reference.

**(e) Positive control: Ur III seal legends** (CDLI, word level, slots tagged by the genre_alignment rule tagger,
imported read-only). Distinct legends; 25% of owner names (first word) held out as test families; primary
training set = an Indus-size random sample (1,698 legends) of the training families; the same pipeline
(K by BIC over 8-30, alpha by CV, exchange with random restarts, the same positional naming rules; no seeds,
none exist for Ur III).
- e1: token-level NMI between induced class and gold slot on the test legends exceeds all 20 values from the
  same pipeline trained on within-legend-shuffled training legends.
- e2: the relators are isolated: >= 70% of test KIN tokens (dumu ...) and >= 70% of SERV tokens (arad2 ...) fall
  in classes whose majority gold slot is KIN or SERV respectively.
- e2-KIN (secondary, added after the dry run): KIN isolation alone >= 0.70. Disclosure: the dry run (Ur III
  training families only, split again 75/25) gave e1 NMI 0.536 vs shuffled-train max 0.439 (pass), KIN 0.99,
  SERV 0.51 (fail; SERV words split between a final 'your servant' class and a medial class shared with titles).
  The primary e2 is left unchanged, so I expect primary (e) to fail on SERV.
- (e) passes if e1 and e2 pass. Reported, not tested: purity, slot x functional label table, grammar vs
  bigram perplexity on Ur III (calibrates a1: if a real name-and-title genre also gives a class grammar that
  loses to a bigram, failing a1 says nothing against grammaticality).

## Decision and interpretation

- The grammar counts as **validated as a description** if a2, b1, b3, c-pos, d and e pass. It counts as a
  **better predictor than the bigram** only if a1 (and c-big) pass.
- 14 decisions in total (a1, a2, a3, b1, b2, b3, c-big, c-pos, c-gap, d, e1, e2, e2-KIN, e). Decisions use 95% CIs
  or the stated p; no correction across them; all are reported, including failures.
- Falsification: the positional description is falsified if the grammar does not beat position-only or the
  shuffled-trained grammar on held-out text (a2), or does not separate Gulf round seals (d).
