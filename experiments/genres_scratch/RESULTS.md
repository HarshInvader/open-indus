# Genres from scratch: unsupervised text types checked against objects (board #34, N2)

2026-11-18. Pre-registration `docs/prereg/genres_from_scratch.md` (hash in `docs/prereg/HASHES.txt` before any fit), amendment A1 appended and hashed after the four pre-registered models had run. Unit: distinct texts. M77 split = `splits_v2` (dev 1,698 / held-out 571). ICIT: own near-copy family split 75/25 (seed 34; train 2,624). Ledger rows: `ledger_rows.csv` (`gsx_*`).

## Verdict

**UNDETERMINED, leaning negative for strong genres.** No unsupervised model finds Indus text types from the signs alone, but no model could have found types as weak as the real object-type signal at Indus size. So "no genres" cannot be claimed.

What the data do allow:

1. **Indus has no split into text types as different as Mesopotamian seal legends vs tags vs brick inscriptions.** The one model that passed the known-answer test (a mixture of small HMMs) recovers those cuneiform genres from the texts alone (K* = 5, ARI 0.65 with the true genre, p = 0.0005). On Indus (M77) and on ICIT it chooses one genre. It also never invents genres in synthetic one-model corpora (0/5).
2. **Anything weaker is invisible to these methods here.** Measured on one scale (held-out bits per text that a calibrated supervised classifier gains from the label):
   - the method recovered the cuneiform genres at 1.15 bits;
   - it missed the Latin label/inscription split (0.35 bits) and the ICIT object kinds (0.44 bits);
   - the real Indus object-type signal is 0.15 bits (seal shape in ICIT also 0.15; site 0.01).
   - Planted genres (20% + 10% of texts, up to half their tokens swapped) reach at most 0.06 bits, and no valid model found them (HMM 0/15, formula model 0/15).
   So finding 06 ("kinds of object have their own vocabulary") is real but small: it shifts sign choice by a few hundredths of a bit per sign, not into separate text types.
3. **Exploratory, not a gate: forced into 4 types, the genres weakly track the object.**
   - M77, HMM: object type 0.04 bits per text, p = 0.0005. This survives holding site and length fixed (p = 0.001), but the overlap is tiny (ARI 0.015).
   - ICIT: forced genres track object kind (p = 0.0005) and, weakly, seal shape (p = 0.002 to 0.04).
4. **Round seals (exploratory, forced K = 4): home and foreign round seals fall into the same types, away from the standard formula.**
   - Under the HMM, 18 of 36 round texts sit in a short (mean 2.7 signs), numeral-opening type, against 24% of square seals. Only 3 of 36 sit in the long "W820/W861/W817 opener + W740 jar" type, against 34% of square seals. p = 0.0002 against random sets of square seals; the formula model agrees (p = 0.0006).
   - Home (19) and foreign (17) round seals split almost identically (HMM: 9/9 in the short-numeral type, 5/6 in the next).
   - This supports #22, #23 and #25: the off-order pattern is a round-seal format, not a foreign-name effect. But these forced types are neither chosen by the data nor stable, so it is a lead, not a finding.

No genre was found, so none of the planned descriptions applies: numerical/administrative, names/titles, fixed label. For orientation only, the four forced M77 HMM types are:
- an "M267/M391 opener … M342" long formula, 98% seals or sealings;
- a short "fish + M342/M176" type;
- an "M86/M336 opener … M211" type;
- a short type ending in M176 or the M162 count frame, which has the most tablets.

## Pre-registered gates (Indus)

| model | M77 K* | S1 genres exist | S2 track objects | S4 stable | ICIT K* | notes |
|---|---|---|---|---|---|---|
| BG bigram mixture | 1 | fail | n/a | n/a | 1 | fails known answer (cun K* 1, lat K* 1) |
| LCA formula latent classes | 1 | fail | n/a | n/a | 2 (held-out CI −0.04 to 0.17) | fails known answer on cun; false positives on synthetic one-model corpora (5/5) |
| HMM mixture (4 states each) | 1 | fail | n/a | n/a | 1 | **only model passing known answer** (cun K* 5, ARI 0.65, G 0.76 bits, p 0.0005); 0/5 false positives |
| LDA topics, signs + pairs | 1 | fail | n/a | n/a | 1 | held-out bound picks K = 1 on every corpus, including both known answers; cannot choose K |
| BG2 tilted bigram (A1, post hoc) | 10 | "pass", void | obj p 0.39, site p 0.78 | ARI 0.03 | 10 | splits every corpus, incl. 5/5 synthetic one-model corpora → S1 meaningless |

- **S3 power: fail.** At the plant nearest the real object-type signal (f = 0.5, 0.06 bits), detection was:
  - HMM 0/5, formula model 0/5;
  - BG2 2/5, against a 1/5 false-positive rate at f = 0.
- **Verdict rule.** S1 fails for every valid model and S3 fails, so the result is "undetermined", per the pre-registration.
- **Holm.** The 12 primary label tests are all p = 1 (K* = 1) except BG2, which is void, so nothing survives.

## Numbers

**Known answer (held-out).**
- Cuneiform: 1,612 train / 537 test units. Ur III seals, OB seals, tags; bricks short, only 106 available.
  - HMM: K* 5; held-out log-lik +2.81 nats per text over K = 1 (CI 1.90 to 3.24); G 0.76 bits; ARI 0.65; stability ARI 0.29 (unstable).
  - BG2 (β 80): K* 8, ARI 0.40.
  - BG, LCA, LDA: K* 1.
- Latin: labels vs other short inscriptions.
  - LCA: K* 5; held-out +1.27 nats (CI 1.06 to 1.48); G 0.21 bits, p 0.0005; but ARI 0.055 (below the 0.20 bar) and stability 0.27.
  - All others: K* 1 (BG2 ARI 0.01).
  - **Known-answer test: passed on cuneiform (HMM), failed on Latin.**

**Supervised scale.** Logistic regression, signs + pairs + first/last/length, held-out bits per text over base rate: cun genre 1.15; lat genre 0.35; ICIT register 0.44; ICIT seal shape 0.15; M77 object 0.15; M77 site 0.01; plants f 0.15 / 0.30 / 0.50: −0.01 / 0.00 / 0.06.

**Planted power (corrected run, 5 reps per cell).**
- f = 0.5: HMM 0/5, LCA 0/5, BG2 2/5.
- f = 0.3: 0, 0, 2/5.
- f = 0.15: 0, 0, 1/5.
- f = 0: 0, 0, 1/5.

**Synthetic one-bigram corpora** (genre count chosen, held-out gain above K = 1):
- HMM: K* 1 in 5/5.
- LCA: K* 2 to 4, positive held-out CI in 5/5.
- BG2: K* 5 to 6 in 5/5.

**Round seals.** ICIT SEAL:C + SEAL:CY, distinct, n = 36 (17 foreign); forced K = 4, likelihood-ratio statistic against 5,000 square-seal draws of the same size: HMM p 0.0002, LCA p 0.0006, BG p 0.83.

## Deviations and limits

- **Amendment A1 is post hoc** (BG2, LDA dropped from power runs, synthetic negative control). Written after the pre-registered results were seen; it only ever weakens claims.
- **Planted-label bug.** The first power run is discarded and kept as `out/plant_v1_buggy_labels.jsonl`. The near-copy rule chains 571 dev texts into one family, which took 44% of dev labels as class 1 and none as class 2. It was fixed with a quota fill and rerun. Neither run gave HMM or LCA any detection.
- **The same giant family affects other checks.**
  - It makes the 5-fold cross-validation folds inside dev unbalanced, and the stability bootstrap noisy. K choice by 5-fold CV and the 1-SE rule was done on that family structure.
  - LDA K selection uses the variational bound, as pre-registered; it is known to favour small K.
- **HMM CV used 2 restarts** (pre-registration said 3). The M77 HMM shows a held-out "gain" with K* = 1 (CI 0.08 to 0.41). That is a better K = 1 optimum from 3 restarts against 1, not a genre effect.
- **The planted genres are a vocabulary shift only** (frequency-neighbour substitution). Genres that differ in length or formula, like the cuneiform ones, are easier to find. Power was not tested for formula-type plants.
- **The forced K = 4 analyses** (object association, round seals, marker signs) were not gated by the pre-registration and are exploratory. They are about 10 tests, uncorrected.
- **Not done:**
  - proto-cuneiform or Proto-Elamite as a known answer (no genre labels in the repo copies);
  - period as a label (mostly missing in ICIT);
  - a genre test on longer multi-line texts only.

## Next experiments

1. **Find out what the method can detect.** Run formula-type and length-type plants, and the cuneiform corpus thinned to Indus-like separability (mix fractions so the supervised gain falls to 0.15 to 0.4 bits). Pre-register the threshold first. If no unsupervised method can find a 0.15-bit split at 2,300 texts, close the route in NEGATIVE_ATLAS with that number.
2. **Get a labelled Proto-Elamite corpus** (genre tags from Dahl's CDLI work) as the true known answer for the Dahl/Kelley method at matching size.
3. **Round seals:** test the "short numeral-opening type" lead directly and pre-registered. Predict that new round seals (CISI 3.4, Gulf finds) lack the standard long opener formula and start with a numeral more often than square seals of the same length.
