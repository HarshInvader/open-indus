# Pre-registration: sign meaning classes from read scripts, held-out-script gate (board task #8, H5)

Written 2026-11-17 after building the tagged corpora (`experiments/meaning_classes/build_corpora.py`, class counts only) and before any feature, model or score was computed. Script: `experiments/meaning_classes/mc_gate.py` (hashed with this file).

## Question
Can a word or sign's distributional behaviour in short texts predict its meaning class (NAME / CONTENT / FUNC) well enough to transfer to a script it was not trained on? Only if it does, apply the model to Indus signs.

## Corpora (3 scripts, 3 languages, 3 genres)
- cun: ORACC epsd2/admin/oakk, line units, ORACC POS. NAME = PN, DN, GN and other *N tags; CONTENT = N, V, AJ, AV; FUNC = CNJ, PRP etc. (only 124 tokens, so FUNC is effectively absent in cun); NUM = n/NU.
- egy: TLA Earlier Egyptian, sentence units, UPOS (PROPN = NAME; NOUN, VERB, ADJ, ADV = CONTENT; ADP, PRON, DET, PART, CONJ, AUX = FUNC).
- lat: EDH inscriptions, line units, editor capitalisation = NAME, closed list = FUNC, Roman numerals = NUM.
- Linear B was not used: there is no POS-tagged lexicon locally (DAMOS has no bulk export), and proto-Elamite is unread.

## Size matching
For each script, units with 2-17 tokens, no break token. Draw 2,300 units without replacement (seed 0). Types are scored only when they occur ≥ 3 times in the draw. This gives an Indus-like scale: Indus dev has about 1,700 distinct texts with mean about 4.5 signs.

## Features (per type, computed inside its own corpus draw; every feature is a within-corpus rank percentile)
log frequency; share of tokens unit-initial; share unit-final; mean relative position; left and right partner diversity (distinct partners / occurrences); share preceded by NUM; share followed by NUM; distinct units / occurrences; share of partners that are singletons in the draw; mean length of the units containing the type.

## Model and metric
- Model: multinomial logistic regression (sklearn, C = 1, class_weight balanced) on the 11 features. Baseline: the same model on the log-frequency feature alone.
- Classes predicted: NAME, CONTENT, FUNC. NUM types are excluded as targets, because Indus numerals are known.
- Metric: macro-F1 on the held-out script, over the classes present in it with ≥ 10 scored types.
- Leave-one-script-out (LOSO): train on two scripts, test on the third.
- Null: labels permuted within each training script, 200 draws; null distribution of held-out macro-F1.
- Repeat the whole procedure over 5 corpus draws (seeds 0-4) and report the mean.

## Gate (pre-set bar)
**PASS** only if, in all 3 held-out scripts (mean over 5 draws), both hold:
1. full macro-F1 ≥ baseline macro-F1 + 0.10;
2. full macro-F1 > the 95th percentile of the permuted-label null (seed 0).

Otherwise **FAIL**, and nothing is applied to Indus. For reference, atlas 2.1 failed at a similar gate for language family (0.62).

## Indus application (only on PASS)
- Train on all three scripts. Predict classes for M77 non-numeral signs with ≥ 3 occurrences, using M77 dev distinct texts (version 2 split).
- Stability: repeat on held-out texts. Report Spearman agreement of P(NAME) between dev and held-out, and per-sign classes only where both splits agree with P ≥ 0.6.
- Caveat stated in advance: this assumes an Indus sign behaves like a word. If signs are syllables, the classes have no meaning.
