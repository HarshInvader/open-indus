# Pre-registration: Genres from scratch (board #34, agent N2)

Written 2026-11-18 before any model in `experiments/genres_scratch/` was fitted and before any genre-object association was computed. Hash appended to `docs/prereg/HASHES.txt`.

## Question

Do Indus texts fall into text types ("genres") that can be found from the sign sequences alone, the way Dahl and Kelley found Proto-Elamite text types, and do those types line up with the objects the texts are written on?

## Data

- **Main corpus (M77).** Distinct object-side texts, `dev_heldout(version=2)`: dev 1,699 texts, held-out 571 (family split, `data/splits_v2.json`). Line breaks dropped; `#` splits a text into runs; a run's start/end probabilities are used only where the text edge is intact (`glib.make_runs`). Signs seen fewer than 2 times in the training set map to UNK.
- **Shape corpus (ICIT).** Distinct ICIT texts (Wells signs), home and foreign, split 75/25 by near-copy family (`glib.families`, seed 34). Needed because only ICIT records seal shape (SEAL:S square, SEAL:R rectangular, SEAL:C circular, SEAL:CY cylinder).
- **Labels used only after fitting:** M77 object type collapsed to {seal, sealing, miniature tablet, copper tablet, pottery graffito, other}; M77 site {Mohenjodaro, Harappa, Lothal, Kalibangan, Chanhudaro, other}; ICIT register {square seal, rect seal, round/cyl seal, incised tablet, bas-relief tablet, copper tablet, pottery, tag/sealing, other}; ICIT seal shape (seals only, {S, R, C+CY}); ICIT site group.
- **Models never see** object type, site, shape, period, field symbol or direction.

## Models (four families)

1. **BG**: mixture of K bigram models (BOS/EOS, add-beta smoothing towards a component unigram, itself smoothed to the global unigram). EM, 3 restarts, best training likelihood kept.
2. **HMM**: mixture of K small ergodic HMMs (4 states each), EM (forward-backward), 3 restarts.
3. **LDA**: topic model over sign unigrams and adjacent sign pairs (sklearn `LatentDirichletAllocation`, batch); a text's genre = its largest topic.
4. **LCA**: latent class model over formula features (first sign, second sign, second-to-last sign, last sign, length bin 1/2/3/4/5/6/7+); features at a broken edge are missing and skipped.

Genre of a text = most probable component.

## Choosing K

K in 1..10. Primary: mean log-likelihood per text over 5-fold near-copy-family cross-validation inside dev; K* = smallest K within one standard error of the best mean (1-SE rule). For LDA, the same with sklearn's held-out variational bound (perplexity). Confirmation: log-likelihood of the splits_v2 held-out set for K* vs K = 1 (no labels involved). The held-out set is not used to pick K.

## Tests (on held-out texts only, labels never used before this step)

- **Association statistic G**: genres are assigned to dev and held-out texts by the dev-fitted model. P(label | genre) is estimated on dev (add-0.5), and G = mean held-out log2-loss of the base rate minus that of P(label | genre), in bits per text. Null: permute held-out labels (2,000 draws). One-sided p.
- **Primary tests (Holm over 12):** 4 models × {M77 object type, M77 site, ICIT seal shape}. For ICIT seal shape the same procedure runs on the ICIT corpus with its own K*.
- **Secondary (not part of the verdict gate):** (a) object type with labels permuted within site × length-bin strata (does genre predict object type beyond site and length?); (b) ICIT register and site; (c) NMI with the same nulls.

## Planted-genre controls (power)

On the real M77 texts (dev + held-out kept as split), assign fake labels by family: 70% / 20% / 10%. In the two minority classes, each token is replaced with probability f by a class-specific substitute (a fixed random pairing of signs of neighbouring frequency rank), so length, position and sign-frequency profile are kept. f in {0.15, 0.30, 0.50}, 8 replicates each, run through the same pipeline (K by the same CV rule, with a 3-fold CV and K in 1..6 to fit the laptop budget). Power = share of replicates with p < 0.05 for the fake label. To place the real signal on this scale, a supervised naive-Bayes classifier's held-out gain (bits per text) is computed for real object type and for each plant strength.

## Stability

20 refits on family bootstrap resamples of dev at K*; genres assigned on all dev texts; median pairwise ARI.

## Known-answer test

The same pipeline on two labelled comparison corpora with genres known, using units of 1-17 tokens, whole units, about 2,270 distinct units, near-copy family split 75/25:
- **Cuneiform (one sign system):** Ur III seal legends 50%, Old Babylonian seal legends 25%, tags 15%, brick inscriptions 10% (`experiments/short_labels/data`, cun_*).
- **Latin (one word system):** stamps/labels 30%, other short inscriptions 70% (lat_label, lat_short).

The pipeline passes on a corpus if, for at least one model, K* ≥ 2, G for the known genre is above the permutation null at p < 0.05, and ARI(genre, known genre) ≥ 0.20 on held-out.

## Decision rules

- **S1 genres exist**: K* ≥ 2 and the splits_v2 held-out log-likelihood of K* beats K = 1 (family bootstrap 95% CI of the difference above 0).
- **S2 genres track objects**: Holm-corrected p < 0.05 for object type, site or seal shape.
- **S3 power**: planted power ≥ 0.8 at the plant strength nearest the real supervised object-type signal. If below, a negative reads "undetermined", not "no genres".
- **S4 stable**: median bootstrap ARI ≥ 0.5 (0.3-0.5 "unstable", < 0.3 "not reproducible").
- **Verdict "genres found and tied to objects"** needs S1, S2 and S4 for the same model, and the known-answer test passed on at least one corpus. S1+S4 without S2: "text types exist but do not track objects". S2 without S4: "an association exists but the types are not reproducible". Failing S1 for all four models: "no genre structure beyond one model" (qualified by S3).
- **Length caveat**: if the object-type association disappears in secondary test (a), it is reported as a length/site effect.

## Description (only if the verdict needs it; descriptive, no p-values claimed)

Per genre: top marker signs by smoothed log-odds vs other genres (dev); top first and last signs; mean length; numeral share (functional_reading NUMERAL signs for M77; W001-W059 minus W001/W002/W031 for ICIT); type-token ratio; share of distinct texts repeated on 2+ objects. Operational tags: "numerical/administrative" if numeral share ≥ 1.5× corpus rate and repeated-text share is not elevated; "fixed label" if distinct-text diversity is low (≥ 30% of objects repeat a text) and mean length ≤ 3; "names/titles" if type-token ratio of non-frame signs is in the top half and mostly seals. Round seals: ICIT SEAL:C + SEAL:CY texts (home and foreign); test whether their genre distribution differs from square seals' (likelihood-ratio statistic, permutation null drawing the same number of seal texts, 5,000 draws), reported for each model. Pre-registered expectation from #23/#25: round texts have weak order, so they may fall in a "loose" genre.

## Compute

All runs through `board/run.sh`, at most 2 workers, under 2 GB. If the planted grid is too slow, replicates are cut to 5 per cell and the cut is reported.

## Amendment A1 (2026-11-18, after the four pre-registered models had run on all corpora)

Seen before writing this: on M77 and ICIT, BG, LCA, HMM and LDA all chose K* = 1 (LCA K* = 2 on ICIT without a held-out gain). Known-answer: only HMM passed (cuneiform K* = 5, ARI 0.65); BG and LCA chose 1 genre on cuneiform; LDA's held-out bound chose K = 1 on every corpus, so LDA cannot choose K and is dropped from the power runs.

1. **BG2 (post hoc model).** Mixture of bigrams whose components are tilts of one shared bigram (`gs.BG2`). beta was chosen on the known-answer corpora only (grid 5/20/80; 80 best on cuneiform: K* = 8, ARI 0.40; Latin ARI 0.01 at every beta, i.e. BG2 fails Latin). Frozen at beta = 80, lam = 2, K in 1..10. It is run on M77 and ICIT with the same tests and is reported as post hoc.
2. **Power runs** use HMM, LCA and BG2 (not LDA), 5 replicates per cell, f in {0, 0.15, 0.30, 0.50}; f = 0 gives the false-positive rate for the label test.
3. **Negative control for S1 (new).** BG2 chose the largest K offered on both known-answer corpora, so it may split any corpus. Five synthetic corpora are drawn from a single bigram model (BG, K = 1) fitted to all M77 texts, with the M77 dev/held-out sizes; the share of these where a model's K* ≥ 2 with a positive held-out CI is reported. A model whose S1 fires on these corpora cannot support "genres exist".
4. Verdict rules are unchanged; BG2 can only add to them if it passes the negative control.
