# Pre-registration: round_seal_format (board #39)

Written 2026-11-18 before any statistic below was computed. Agent: research-agent. Folder: experiments/round_seal_format/.

## Question
Do round seals (Indus-found and abroad) share their own short text format (numeral-opening, no standard opener), and does that format account for the off-order pattern of Gulf round seals (README #4, board #22/#23/#25) better than the idea that they spell foreign names?

Lead (exploratory, #34 genres_scratch): forced HMM K=4, 18/36 ICIT round texts in a short numeral-opening type vs 24% of square seals; 3/36 carry the long standard opener vs 34%.

## Data and fixed definitions
- Corpus: ICIT (`corpus.load.icit_texts`), Wells numbering. Distinct texts: first-seen per (findspot group, sign sequence) after removing `|`; `#` kept for edge checks.
- Round = type SEAL:C or SEAL:CY, minus ICIT 1387.1/1388.1/1388.2 (CISI: incised tablets, #23).
- Findspot groups: home = Indus site (not in glib.FOREIGN, not Unknown); abroad = site in glib.FOREIGN; unprovenanced = Unknown (foreign_corpus.csv records all Unknown round seals as probable West Asian finds). Primary "abroad" pools abroad + unprovenanced; sensitivity drops unprovenanced.
- Square reference = home non-round seals (SEAL:S, SEAL:R, SEAL, SEAL:L), distinct, excluding any sequence also on a round seal.
- Numeral = first sign in glib.NUM["ICIT"] (graphic stroke numerals from numeral_grammar inventory).
- Standard opener = first sign in the Wells signs of the grammar's `final_class == opener` rows in experiments/grammar/sign_classes.csv.
- Closer = last sign in the Wells signs of `final_class == closer` rows.
- Edge legibility: F1/F2 need an unbroken first sign (raw seq does not start with `#`); F4 needs an unbroken last sign; F3 uses complete texts only (complete flag and no `#`). Length = number of legible signs.

## Discovery set (NOT independent)
All ICIT round texts are the 36 texts #34 used. Tests on them can refute the lead (if the model-free pattern is absent the HMM result was a model artefact) but cannot confirm it.

## Primary format tests (discovery set, one-sided, Holm over F1-F4)
Matched null: for each round text draw a reference square text from the same stratum; 10,000 draws; p = (1+#draws >= obs)/(10001) in the predicted direction.
- Strata: home round -> same site x length (length capped at 7); if <5 candidates, length only over all home sites (count fallbacks). Abroad round -> length only over home squares (no site control possible; foreign squares too few — reported descriptively).
- F1 numeral-first share: round > matched squares.
- F2 standard-opener share: round < matched squares.
- F3 length: complete round texts shorter than same-site (home) / all (abroad) complete squares; matched-site permutation of mean length (draw from same site without length matching).
- F4 closer-last share: round < length-matched squares.
Pass for "round-seal format exists (descriptive)": F1 and F2 both Holm p < 0.05. Also reported separately for home round and abroad round (descriptive, uncorrected).

## Held-out set (defined before looking)
Round seals not in the #34 set: rows of experiments/foreign_corpus/foreign_corpus.csv whose shape contains "round" or "cylinder", with >= 2 legible signs and no ICIT round record (so not in #34), sequence from `seq_wells` ('?' = illegible). Rows with shape "seal" (unknown shape) are excluded. ICIT round texts at sites outside M77 are all in #34 already, and M77 has no shape field, so dev_heldout(version=2) adds no new round object (its West Asian texts are other readings of the same objects). Expected n = 2 (UR-07, UR-10). Test: F1 and F2 counts vs the length-matched square rates, exact binomial / Poisson-binomial. Power: probability of p < 0.05 for F1 at held-out n given the discovery round numeral-first share vs the matched square share (simulation, 10,000). If power < 0.8 the held-out test cannot confirm, and the verdict is capped at "lead not refuted, not confirmed".

## Off-order tests
Order excess d per text = KN bits(real) - mean KN bits(permutations), as #25 (10-fold CV KN for home texts trained on home texts; full home model for abroad texts; up to 200 distinct permutations; texts with >= 2 signs and a distinct permutation). Positive d = more off-order.
- O1 format-matched null: round texts (home + abroad) vs home square seals matched on length (cap 9) x numeral-first x opener-first x closer-last (fallback order: drop closer-last, then opener-first, then shorten length; min pool 5). Also the length-only null (N0). Fraction explained = 1 - excess_fmt / excess_len, bootstrap CI over round texts (2,000).
- O1b E_fmt: home square seals that share the round format (numeral-first and no standard opener) — their mean d vs length-matched home squares. If ~0 (CI includes 0 and upper bound < half the round excess), the format itself does not produce off-order in Indus texts.
- O2 findspot without shape: abroad non-round seals (glib.FOREIGN sites, SEAL* not round) mean d vs length-matched home squares.
- O3 abroad round minus home round, mean d (permutation of labels, two-sided).
Holm over O1 (format-matched), O2 (one-sided, excess > 0), O3 (two-sided).

Interpretation (fixed):
- "Format explains the off-order": O1 format-matched p >= 0.05 AND fraction explained >= 0.5 AND planted power (below) >= 0.8.
- "Format does not explain it": O1 format-matched p < 0.05 AND format-matched excess >= 50% of length-only excess.
- Otherwise inconclusive.
- "Find-spot effect irrespective of shape": O2 p < 0.05. Reported with its planted power; if power < 0.8 and p >= 0.05, "not detected, underpowered".
- Foreign-name hypothesis predicts: off-order specific to abroad finds (O3 > 0, O2 > 0) and not removed by format matching. Round-format hypothesis predicts: O3 ~ 0, O2 ~ 0, and O1 removed by format matching. Mixed outcomes are reported as mixed.

## Planted / known-answer checks
- P1 power: draw sets of home square seals format-matched to the round set (same size), shuffle each text within itself; fraction flagged by O1 (p < 0.05): needs >= 0.8. 500 reps, 2,000 null draws each.
- P2 size: same draws unshuffled; false-positive rate should be <= 0.10.
- P3 O2 power: n_O2 length-matched home seals within-text shuffled, fraction flagged by O2 test. 500 reps.
- P4 known answer for "explained by format": pseudo-round sets drawn from home square seals with the round set's format composition, unshuffled, scored with the length-only null: the excess they show is what format alone produces (same as O1b, resampled).

## Near-copy check
Near-copy clusters among round texts (sign-bigram Jaccard >= 0.5, single linkage). F1 and O1 rerun keeping one text per cluster (the first). #34 noted single-linkage chaining over the whole corpus; here linkage is only among <= 36 round texts and the chain sizes are reported.

## Reported but not tested
#34's "home" round group included unprovenanced Gulf-type seals; the split of the 36 by findspot group is reported.

Tests: F1-F4 (4), held-out F1/F2 (2), O1-O3 (3), O1b (1) = 10 confirmatory-style tests, plus planted checks.
