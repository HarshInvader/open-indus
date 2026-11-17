# A positional grammar of the Indus seal text

This describes where signs sit in an Indus text. It gives no sound values and no meanings. The model, code and
tests are in `experiments/grammar/` and the test plan is in `docs/prereg/grammar.md`. Results are in
`experiments/grammar/RESULTS.md`.

## The short version

A typical seal text (read in reading order) has up to four parts:

    [opener] [connective]  medial ... medial  [closer] [post-closer]

- **Opener**: a small set of signs that start texts. M267 and M391 make up 86% of the main opener class.
- **Connective**: M99 and M123, almost always right after an opener (an opener is followed by a connective 62%
  of the time) and never at the end.
- **Medial**: the bulk of the vocabulary. Most text-specific sign choice happens here.
- **Closer**: M342 (the "jar" sign) and a few others end texts. A closer is followed by end of text 71% of the
  time.
- **Post-closer**: M176, M1 and a few others can follow a closer as the very last sign. This class was not stable
  enough under resampling to keep as a validated class.

Every part is optional. 59% of texts start straight with a medial sign, and many texts have no closer.

## Validated sign classes (M77 numbering)

A sign gets a validated label only if it keeps that label in at least 70% of 200 family bootstraps of the dev
corpus, and, where the sign has a Wells counterpart, the Wells-list grammar gives it the same label. A class is
kept only if it appears under both sign lists, is stable and agrees across lists more than a permutation null.
Numeral and post-closer failed that test and were dropped. Signs that fail are "unclassified", which means
"not reliably placed", not "no position".

| validated class | signs | share of dev tokens | signs (dev tokens, bootstrap stability) |
|---|---|---|---|
| opener | 10 | 0.073 | M267 (254, 0.99), M391 (142, 0.99), M293 (99, 0.75), M150 (35, 0.97), M286 (10, 0.93), M412 (4, 0.98), M146 (3, 0.75), M395 (3, 0.97), M305 (2, 0.98), M64 (2, 0.70) |
| medial | 85 | 0.348 | M59 (234, 0.98), M67 (173, 1.00), M336 (155, 0.90), M65 (129, 0.96), M343 (124, 0.82), M72 (123, 0.98), M249 (108, 0.82), M245 (105, 0.94), M53 (91, 0.99), M387 (80, 0.96), M48 (72, 0.97), M51 (72, 0.70) ... |
| connective | 2 | 0.076 | M99 (445, 1.00), M123 (132, 0.91) |
| closer | 7 | 0.141 | M342 (776, 1.00), M211 (142, 1.00), M15 (58, 1.00), M254 (47, 0.80), M12 (42, 0.88), M14 (7, 0.95), M388 (4, 0.76) |
| unclassified | 265 | 0.363 | M87 (191, 0.75), M176 (153, 0.70), M162 (140, 0.61), M89 (134, 0.55), M169 (111, 0.56), M86 (92, 0.53), M171 (85, 0.47), M1 (80, 0.70), M102 (77, 0.62), M17 (55, 0.41) ... |

The full list, with confidence and the Wells label for every sign, is `experiments/grammar/sign_classes.csv`.

## The 16 fine classes the model actually uses

The generative model works with 16 classes (K chosen by BIC on dev). Each sign belongs to exactly one. The
functional label is assigned by fixed positional rules. Two classes come out as "numeral" (most of their members
are stroke numerals), but they mix numerals with other signs and were not stable, so numeral is not a validated
class.

| fine class | label | share of dev tokens | P(start) | P(end) | initial / medial / final | main signs (P within class) |
|---|---|---|---|---|---|---|
| c2 | opener | 0.060 | 0.23 | 0.04 | 0.77 / 0.19 / 0.04 | M267 0.55, M391 0.31, M150 0.08, M286 0.02, M330 0.01, M412 0.01, M146 0.01 |
| c9 | opener | 0.035 | 0.08 | 0.05 | 0.46 / 0.50 / 0.04 | M293 0.38, M180 0.13, M409 0.06, M261 0.05, M400 0.03, M19 0.03, M214 0.03 |
| c5 | medial | 0.104 | 0.12 | 0.01 | 0.25 / 0.75 / 0.00 | M67 0.22, M65 0.16, M72 0.16, M53 0.12, M387 0.10, M389 0.09, M70 0.07 |
| c13 | medial | 0.072 | 0.12 | 0.18 | 0.32 / 0.50 / 0.18 | rare signs 0.19, M402 0.10, M328 0.08, M375 0.07, M252 0.06, M28 0.06, M307 0.05 |
| c10 | medial | 0.065 | 0.07 | 0.03 | 0.23 / 0.74 / 0.03 | M48 0.15, M51 0.15, M216 0.10, M244 0.09, M341 0.08, M294 0.08, M155 0.07 |
| c15 | medial | 0.062 | 0.10 | 0.04 | 0.34 / 0.62 / 0.04 | M249 0.23, M17 0.12, M204 0.09, M175 0.08, M124 0.08, M104 0.07, M25 0.05 |
| c3 | medial | 0.057 | 0.02 | 0.27 | 0.07 / 0.60 / 0.32 | M162 0.32, M169 0.26, M245 0.24, M230 0.08, M81 0.03, M206 0.01, M110 0.01 |
| c14 | medial | 0.054 | 0.08 | 0.05 | 0.31 / 0.65 / 0.05 | M343 0.30, M86 0.22, M98 0.12, M345 0.07, M344 0.06, M178 0.04, M100 0.04 |
| c0 | medial | 0.053 | 0.04 | 0.10 | 0.15 / 0.73 / 0.12 | M59 0.57, M197 0.11, M287 0.09, M284 0.06, M60 0.05, M326 0.04, M190 0.03 |
| c12 | medial | 0.041 | 0.01 | 0.02 | 0.04 / 0.95 / 0.01 | M8 0.23, M347 0.22, M194 0.11, M296 0.07, M135 0.06, M222 0.06, M348 0.05 |
| c6 | medial | 0.031 | 0.03 | 0.03 | 0.18 / 0.79 / 0.03 | M336 0.66, M130 0.15, M182 0.10, M103 0.06, M138 0.01, M22 0.01, M55 0.01 |
| c1 | connective | 0.083 | 0.00 | 0.02 | 0.00 / 0.98 / 0.02 | M99 0.71, M123 0.21, M97 0.08, M195 0.00 |
| c4 | numeral | 0.066 | 0.07 | 0.05 | 0.24 / 0.70 / 0.06 | M87 0.38, M171 0.17, M102 0.15, M112 0.10, M373 0.06, M233 0.03, M125 0.02 |
| c11 | numeral | 0.035 | 0.02 | 0.08 | 0.09 / 0.81 / 0.10 | M89 0.50, M403 0.18, M149 0.18, M209 0.05, M321 0.02, M189 0.01, M297 0.01 |
| c8 | closer | 0.143 | 0.00 | 0.68 | 0.00 / 0.26 / 0.74 | M342 0.71, M211 0.13, M15 0.05, M254 0.04, M12 0.04, M66 0.01, M14 0.01 |
| c7 | post-closer | 0.040 | 0.01 | 0.67 | 0.03 / 0.14 / 0.83 | M176 0.50, M1 0.26, M242 0.07, M139 0.04, M224 0.03, M93 0.03, M374 0.02 |

The medial classes are fairly coherent groups: c5 is the "fish" signs with their modifiers (M67, M65, M72, M53,
M387, M389, M70), and c3 (M162, M169, M245) leans towards the end of a text without being a closer.

## How the parts follow each other

Transition probabilities between functional labels on dev (row = this sign's label, column = next).

| from \ to | opener | medial | connective | numeral | closer | post-closer | end |
|---|---|---|---|---|---|---|---|
| start of text | 0.31 | 0.59 | 0.00 | 0.09 | 0.00 | 0.01 | - |
| opener | 0.05 | 0.20 | **0.62** | 0.04 | 0.03 | 0.02 | 0.04 |
| connective | 0.01 | **0.80** | 0.00 | 0.15 | 0.01 | 0.01 | 0.01 |
| medial | 0.05 | 0.48 | 0.04 | 0.11 | 0.23 | 0.02 | 0.08 |
| numeral | 0.02 | 0.64 | 0.01 | 0.08 | 0.19 | 0.00 | 0.06 |
| closer | 0.01 | 0.08 | 0.01 | 0.01 | 0.01 | 0.18 | **0.71** |
| post-closer | 0.01 | 0.05 | 0.00 | 0.01 | 0.05 | 0.09 | **0.78** |

## Example parses (dev seals, reading order)

    M391/opener  M99/connective  M62/medial  M342/closer
    M293/opener  M123/connective  M343/medial  M65/medial  M294/medial  M342/closer
    M267/opener  M99/connective  M70/medial  M222/medial  M254/closer
    M391/opener  M123/connective  M98/medial  M249/medial  M162/medial  M342/closer
    M65/medial  M67/medial  M233/numeral  M342/closer
    M59/medial  M53/medial  M342/closer
    M17/medial  M345/medial  M25/medial  M245/medial  M245/medial

(Labels here are the fine-class labels the model uses.)

## Length and object type

- **Face size.** On 931 ICIT square seals with recorded dimensions, text length rises with face area: about
  1.2 more signs per doubling of area (95% CI for the log-slope 0.23-0.32). Length = 1 + Poisson-like count with
  log mean linear in log2(area). Bigger seals carry longer texts.
- **Object type.** Mean length on M77 dev: seals 5.1, sealings 4.3, copper tablets 4.8, miniature tablets 3.3,
  pottery 2.4. Letting each object type have its own transitions and emissions (shrunk towards the pooled model)
  improves dev cross-validated prediction a little: tablets 0.21 bits per sign, copper 0.15, sealings and seals
  0.04, pottery slightly worse (-0.04). Copper and pottery texts mostly start with a medial sign rather than an
  opener.

## How good is it

Held-out results (441 complete M77 texts, pre-registered; full detail in `experiments/grammar/RESULTS.md`):

| model | bits per sign | parameters |
|---|---|---|
| sign bigram (Kneser-Ney) | 5.49 | 2,734 |
| **this grammar (16 classes)** | **5.79** | 522 |
| 7-state functional grammar | 6.03 | 315 |
| grammar trained on shuffled texts | 6.25 | 522 |
| unigram | 6.29 | 266 |
| position only | 6.38 | 1,329 |

- The grammar captures real positional structure. It beats position-only and shuffled baselines on held-out
  text, at Harappa, at the small sites and at ICIT-only sites.
- Gulf round seals score 1.8 bits per sign worse than native Indus seals of the same length.
- A plain sign bigram still predicts the next sign better. The grammar is a compact description of the text,
  not the best predictor of it.

## Restoring a broken text

    .venv/bin/python experiments/grammar/restore.py "M267 ? ? M342"
    .venv/bin/python experiments/grammar/restore.py "# M59 ? M342"        # broken at the start
    .venv/bin/python experiments/grammar/restore.py "W817 W002 ? W740" --list wells
    .venv/bin/python experiments/grammar/restore.py "M267 ? M342" --register sealing --top 8 --json

`?` is one missing sign; `#` at an edge means the text is broken there. For `M267 ? ? M342` the first gap is a
connective with probability 0.78 (M99 p=0.56, M123 p=0.17) and the second is a medial sign (fish signs lead).
The tool proposes signs that fit the position. On held-out texts the true sign is in the top 5 for 35% of
gaps, and the top slot label is right for 66%. The slot label is the more reliable output. For the best
identity guess, a bigram does better (48% top 5).
