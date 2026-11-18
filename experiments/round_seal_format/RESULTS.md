# Round-seal format (board #39)

**Verdict 1: the lead fails as stated.** Round seals do not open with a numeral more often than square seals: 3 of 28 (11%) against 13% for square seals of the same length and site (p = 0.72). They are not clearly shorter either: 4.5 against 4.9 signs (p = 0.27). The pre-registered rule needed more numeral openers *and* fewer standard openers. The numeral half fails, so "round seals share a short numeral-opening format" is **not supported**.

**Verdict 2: what round seals do share is the absence of the standard formula.** Only 14% end in a closer sign such as the jar (W740), against 45% of matched square seals (Holm p = 0.003). Only 1 of 28 starts with a standard opener, against 13% (p = 0.096, n.s.). Home and abroad round seals look the same on every one of these measures.

**Verdict 3: that format does not explain why Gulf round seals break Indus sign order.**
- Matching square seals on length, numeral start, opener start and closer end removes only **24% of the order excess** (95% CI 18 to 30%). The remaining +1.58 bits/sign still has p = 1e-4.
- Home square seals that share the round-seal opening pattern are only slightly off-order (+0.25 bits/sign, against +2.07 for round seals).

**Verdict 4: the off-order goes with the round shape, not with where a seal was found.**
- Seven square seals found abroad (at Kish, Girsu, Salut, Gonur, Altyn Depe and Shortughai) read in normal Indus order: +0.23 bits/sign, p = 0.32. The test had power 1.0 against shuffled order.
- Round seals found abroad differ from round seals found in the Indus area by only +0.17 bits/sign (p = 0.49).

**For the Gulf-seal findings:** neither explanation wins as posed.
- "Foreign names because the seals were found abroad" gets no support, because place adds nothing once shape is known.
- "A round-seal text format" in the sense of #34 (numeral first, no formula) accounts for only about a quarter of the effect.

What is left is the README #4 correction from #22, #23 and #25, now sharper. Round, Gulf-type seals carry texts with their own sign order wherever they turn up. That order is not produced by dropping the opener or closer, or by starting with a number. Two readings remain open, and these data cannot tell them apart:
- a distinct naming practice or language used by Gulf-type seal owners, at home and abroad;
- a separate genre whose order rules we cannot see.

**Held-out test:** it cannot confirm anything. Only 2 round seals exist outside the #34 set (UR-07 and UR-10, M77 readings only). Neither starts with a numeral or an opener, and power is 0.01. About 100 new round seals would be needed for 0.8 power on the numeral test, at the effect #34 implied.

Pre-registration: `docs/prereg/round_seal_format.md` (sha256 c21ab038…, logged in HASHES.txt before any number was computed). Code: `run.py` (single run, about 35 s via board/run.sh), `posthoc_hmm_type.py` (post hoc). Outputs: `results.json`, `run.log`, `posthoc_hmm_type.json`. Ledger: `ledger_rows.csv`.

## Data
- ICIT. Round means SEAL:C or SEAL:CY. ICIT 1387.1 and 1388.1-2 are dropped, because CISI classes them as tablets (#23).
- Texts are distinct per find-spot group. That gives 35 round texts: 10 home, 18 abroad and 7 unprovenanced. The unprovenanced ones are all probable West Asian finds, per `foreign_corpus.csv`.
- The comparison pool is 1,952 home square and rectangular seals, plus 8 non-round seals found abroad.
- Sign sets were fixed in advance:
  - numerals: `glib.NUM["ICIT"]`, the stroke numerals;
  - standard opener: the Wells signs of the grammar's stable opener class (W820, W861/W817, W920, W692, W880, W201);
  - closer: the grammar's closer class (W740, W151, W154/156, W161, W520, W526/527, W804).

**These are the same texts #34 used.** #34 used every ICIT round seal, so the format tests below are a model-free re-check on the discovery set. They can refute the lead, but they cannot confirm it.

## Format tests (round vs square seals matched on length and site; one-sided; Holm over 4)
| test | round | matched square | p | Holm |
|---|---|---|---|---|
| F1 starts with a numeral (predicted higher) | 3/28 = 0.11 | 0.13 | 0.72 | 0.72 |
| F2 starts with a standard opener (predicted lower) | 1/28 = 0.04 | 0.13 | 0.096 | 0.29 |
| F3 length, complete texts (predicted shorter) | 4.53 (n=17) | 4.88 | 0.27 | 0.55 |
| F4 ends in a closer (predicted lower) | 4/28 = 0.14 | 0.45 | 0.0007 | **0.003** |

- By find-spot, uncorrected:
  - home round: numeral first 0.13, opener 0.13, closer 0.13 (F4 p = 0.049);
  - abroad round: numeral first 0.06, opener 0.00 (p = 0.047 with unprovenanced included), closer 0.13 (p = 0.004).
- Two home round seals had too few same-site squares and fell back to length-only matching.
- No near-copy pairs exist among the 35 round texts (sign-bigram Jaccard ≥ 0.5), so #34's chaining problem does not arise here. The deduplicated rerun is identical.

**Why #34 saw a "numeral-opening type" (post hoc).** #34's HMM type 2 holds 18 of the 36 round texts. It is the short catch-all type: mean length 2.7, and only 24% of its texts start with a numeral. The round seals land there because they lack the W820/W861/W817 … W740 formula (HMM type 0), not because they start with numbers. The "numeral-opening" label overstated a 24% rate.

## Off-order tests (KN order excess d = real bits minus mean bits over permutations, as in #25)
| test | n | excess (bits/sign) | p | Holm |
|---|---|---|---|---|
| O1 round vs length-matched home seals | 31 | +2.07 | 1e-4 | n/a (reference) |
| **O1 round vs format-matched home seals** (length × numeral-first × opener-first × closer-last) | 31 | **+1.58** | 1e-4 | 3e-4 |
| fraction of O1 excess explained by format | | 0.24 (CI 0.18-0.30) | | |
| O1 by group, format-matched: home / abroad / unprovenanced | 8 / 16 / 7 | +1.36 / +1.65 / +1.66 | 3e-4 / 1e-4 / 2e-4 | |
| O1b home squares with round-style opening (numeral first, no opener) | 208 | +0.25 (mean d CI −1.93 to −1.64 vs round −0.03) | 0.004 | |
| O2 non-round seals found abroad, length-matched | 7 | +0.23 | 0.32 | 0.64 |
| O2 same, format-matched | 7 | +0.02 | 0.48 | |
| O3 abroad (+unprovenanced) round minus home round, two-sided | 23 vs 8 | +0.17 | 0.49 | 0.64 |

**Planted checks**, 500 reps each:
- P1: format-matched square sets of the same size, shuffled within each text. O1 flags them 100% of the time.
- P2: the same sets unshuffled. Flagged 3.8% (bar ≤ 10%).
- P3: seven length-matched home seals, shuffled. O2 flags them 100%.
- P4: pseudo-round sets drawn from home seals with the round set's format mix, scored against the length-only null. They show +0.51 bits/sign (CI 0.15 to 0.88). That is what format alone produces, a quarter of the observed +2.07.

The pre-registered verdict rule gives "format does not explain the off-order": O1 format-matched p < 0.05, with 76% of the excess remaining. Find-spot effect: not detected, at power 1.0 against full shuffling.

## Hypotheses
| hypothesis | verdict |
|---|---|
| Round seals open with numerals more than square seals | refuted on discovery set (11% vs 13%) |
| Round seals avoid the standard opener | inconclusive (4% vs 13%, Holm 0.29) |
| Round seals avoid closers | supported on discovery set (14% vs 45%, Holm 0.003); not independently replicated |
| Round seals are shorter | not supported (4.5 vs 4.9, p 0.27) |
| Round-seal format explains the Gulf off-order | refuted (explains 24%, CI 18-30%) |
| Off-order is a find-spot (abroad) effect irrespective of shape | not supported (square abroad +0.23, p 0.32; round abroad − home +0.17, p 0.49) |
| Held-out round seals confirm the format | untestable (n = 2, power 0.01) |

Tests run: 10 pre-registered (F1-F4, held-out F1/F2, O1-O3, O1b) plus 4 planted checks, 1 post-hoc description.

## Limits
- **No independent test.** Every round seal in our corpora was already in #34. The closer finding needs CISI 3.4 or new Gulf seals before it counts.
- **Small groups.** There are 8 scorable home round seals and 7 square seals found abroad. The O2 power figure is against full shuffling. A smaller find-spot effect, say +0.5 bits/sign, would be missed.
- **Some shapes rest on one code.** Five of the 8 home round seals are "round" on ICIT's type code alone (#25).
- **Readings and matching are uncertain.** Several Gulf readings are disputed (`foreign_corpus.csv`). Abroad texts are scored by the full home model and home texts by the 10-fold model, as in #25.
- **What "format" covers.** Here format means the opening sign, the closing sign and the length. A format defined by other slots, such as a "W090/W091 + numeral" pattern, was not tested. W090 or W091 starts 6 of the 18 abroad round texts (post hoc, not tested).

## Next experiments
1. **Fresh check of the W090/W091 pattern.** It is common at the start of Gulf round texts. Pre-register whether those signs start or appear in round texts more often than in square ones. Then test whether the off-order comes from where those signs sit. That needs new round seals (CISI 3.4).
2. **Red team (M6 task added).** Can the closer deficit and the 24% figure be broken with another order model (the Wells grammar, a positional model) and another format definition?
3. **A closer-free control.** Do Indus square seals without a closer show any order excess at matched length? O1b suggests only a little.
