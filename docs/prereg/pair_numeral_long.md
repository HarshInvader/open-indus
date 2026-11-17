# Pre-registration: pair_numeral_long (Fable 5.2 plan items F1, F2, F6)

Registered 2026-11-14 in `experiments/pair_numeral_long/`, after dev work (`*_dev.json`) and a code dry-run in which "held-out" was the last quarter of dev (`PNL_DRYRUN=1`), BEFORE any `dev_heldout(version=2)` held-out text was analysed by these scripts. Unit: distinct texts. Train = dev, test = held-out. Script hashes are in `docs/prereg/HASHES.txt` (lines tagged pair_numeral_long).

Run: `.venv/bin/python experiments/pair_numeral_long/{f1_pairs,f2_numerals,f6_long}.py heldout`.

Bonferroni within each experiment: F1 alpha = 0.05/3 = 0.0167, F2 alpha = 0.05/4 = 0.0125, F6 alpha = 0.05/5 = 0.01.

## F1. Bipartite (two inventories) or compound (one inventory)?

Pairs = adjacent signs inside name cores (core_semantics/typology frozen definition), one count per distinct text. Graph metrics are on distinct pair types; self-pairs dropped. POL = sum|out-in| / sum(out+in) over signs of degree >= 3; POL excess = (POL - orientation-null mean)/(1 - null mean), where the null randomises the orientation of each pair type. Max-cut excess = same against undirected degree-preserving edge swaps.

Dev facts (orientation): all dev pair types POL excess +0.055 (p = 0.015), both-position share 0.87, max-cut excess -0.034; 2-sign cores only +0.145. References at matched n = 140 (5th pct / mean / 95th pct): Chinese clan+given 0.71/0.85/1.00; Ur III names 0.61/0.74/0.86; Sanskrit names 0.36/0.60/0.75; Chinese 2-char given names -0.03/0.23/0.44; simulated one-inventory compounding -0.11/-0.04/0.04; 25% emblem x name mixture 0.01/0.13/0.27. Order-rule accuracy (predict order of unseen pairs from each sign's first-position share): Chinese clan 0.94, Sanskrit 0.95, Ur III 0.83, Chinese given 0.71, compounding sim 0.50; dev 75/25 rehearsal 0.63.

| id | hypothesis (H_C = one inventory, compounding) | prediction on held-out | pass |
|---|---|---|---|
| F1-T1 | no two-inventory split (primary) | POL excess on held-out 2-sign-core types < 0.30 AND bootstrap 95% CI upper bound < 0.50 | both |
| F1-T2 | no undirected two-inventory (blazon-type alternation) | max-cut excess on all held-out pair types < 0.10 and swap-null p > alpha | both |
| F1-T3 | sign position does not determine pair order the way two inventories do | order-rule accuracy dev -> held-out on pair types unseen in dev: Wilson 95% upper bound < 0.83 | yes |

Interpretation: T1+T2+T3 pass -> single inventory with per-pair (lexicalised) order = compounding; emblem x individual and modifier x head with fixed classes are not supported. T1 estimate >= 0.36 and T3 accuracy >= 0.83 -> two-inventory system. Anything else inconclusive. The order-rule accuracy vs 0.5 is reported (one-sided binomial) as descriptive.

## F2. Counts or number-names?

Value = stroke count of the numeral sign directly before a head sign (fr.SHORT / fr.TALL; short-2 connective M99/M101 excluded). Heads with >= 8 dev occurrences classified on dev: lexeme-like (one value >= 60% and max-share permutation q < 0.05 vs pooled numerals), formula-preferring (q < 0.05, share < 0.6), calendar-like (>= 4 values, value 1 attested, cap >= 6, uniform-to-cap beats decay by BIC, uniform GOF p > 0.05), count-like (>= 3 values, no value >= 60%, not significant).

Dev classes. Lexeme-like: short M194 (7), M197 (7), M287 (3), M403 (3), M190 (3), M15 (3), M25 (1); tall M59 (2), M211 (3), M342 (2), M60 (2), M284 (2). Formula-preferring: short M59 (3), M342 (7 and 12). Count-like: short M162, M169; tall M249, M328. Calendar-like heads: none.

| id | hypothesis | prediction on held-out | pass |
|---|---|---|---|
| F2-N1 | numeral + lexeme-like head is a frozen number-name | pooled over dev lexeme-like heads, held-out share at the dev spike value >= 0.6 and above pooled-numeral expectation, permutation p < alpha | both |
| F2-N2 | count-like heads are counted (values vary) | held-out share at the dev modal value < 0.6 AND lower than the N1 share (Fisher one-sided p < alpha) | both |
| F2-N3 | no calendar-style naming | pooled dev+held-out: zero heads (n >= 8) classified calendar-like, and no cap in {7, 12, 13, 20} shared by >= 2 count/calendar-like heads | both |
| F2-N4 | jar M342 after short strokes takes 7 or 12 | held-out share of {7, 12} >= 0.6, binomial vs pooled short base, p < alpha | both |

Power caveat registered in advance: held-out has about a third of dev's numerals; N2 rests on few occurrences, and values 13 and 20 cannot be written with one stroke sign (max short = 12), so a 13- or 20-cap is only detectable through numeral clusters, which this test does not sum.

## F6. Long texts: label list or one clause?

Long = >= 10 signs, or multi-line with >= 8. Frozen functional grammar (fr.load_model(), fit on dev). Nulls: concat = each line refilled with whole random held-out short texts (1-6 signs, single line) to the same line lengths (simulated label lists); shuffle = signs permuted within the text. 1,000 null draws. Statistics in `f6_long.py` docstring.

Dev (n = 47, grammar in-sample): accept 0.53 vs concat 0.11; cuts per 10 signs 0.64 vs 1.50; resets 0.22 vs 1.16; reversed bigrams 0.033 vs 0.043; novel bigrams 0.29 vs 0.245 (real higher, p = 0.015); short texts accept 0.855.

| id | hypothesis | prediction on held-out long texts | pass |
|---|---|---|---|
| F6-L1 | long texts are not lists of short labels | acceptance > concat null, p(null >= real) < alpha | yes |
| F6-L2 | few label boundaries inside lines | resets per 10 signs < concat null, p(null <= real) < alpha | yes |
| F6-L3 | long texts carry residue beyond the short template | bootstrap 95% upper bound of long acceptance < acceptance of held-out short texts | yes |
| F6-L4 | new ordering among known signs (syntax) | reversed-order bigram share > concat null, p < alpha (dev predicts FAIL) | yes |
| F6-L5 | new combinations among known signs | novel bigram share > concat null, p < alpha (dev weak, p = 0.015) | yes |

Interpretation: L1+L2 pass -> long texts are one extended seal template, not concatenated labels; L3 pass -> part of them goes beyond the template; L4 fail -> no evidence of new syntax (order reversals). ICIT long texts at sites absent from M77 (OOV = unknown noun) are reported descriptively (n ~ 6, no power).
