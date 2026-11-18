# Pre-registration: genre detection floor at Indus size (board #43, Fable plan 7 G2)

Written 2026-11-18, before any detection run. Only a pilot was run first (`experiments/genre_floor/pilot.py`, `pilot.json`): near-copy family sizes, the supervised-gain value of each plant strength (1 rep), and the run time of one detection on one MIX s=1.0 corpus (its outcome was not printed or saved).

## Question
What is the weakest genre signal, in held-out supervised bits per text, that the two genres_scratch models (HMM mixture, 4 states per component; formula latent-class model LCA) detect with power >= 0.8 in a corpus of ~2,270 distinct texts? Compare with the real Indus object-type signal, 0.15 bits/text (genres_scratch final.py, same scale).

## Fix carried in from #34
The splits_v2 near-copy rule chains texts transitively (one family of 571 M77 texts, 445 in the cuneiform mix). Here families are built by leader clustering with the same `_close` rule, no chaining: texts visited longest first, each joins the first leader it is close to, else becomes a leader. Pilot: largest family 571 -> 8 (M77, 1,912 families), 445 -> 4 (cuneiform). These families drive the 75/25 split, the CV folds, the bootstrap and label assignment.

## Corpora (per rep, fresh randomness)
Two classes, minority share 30%, assigned by family (whole families get one label). 75/25 family split (seed = rep).
- **Indus-based plants** on all 2,269 distinct M77 texts (dev + held-out pooled; these are synthetic labels, no Indus claim is tested). The minority class gets an edit of strength s:
  - VOC: each token replaced with prob s by a class substitute (cyclic shift within blocks of 5 frequency-adjacent signs, as #34).
  - FORM: with prob s the first sign is replaced by one of 3 class openers, and independently with prob s the last sign by one of 3 class closers (drawn from frequency ranks 20-80).
  - LEN: two attempts, each with prob s, to delete one random sign (texts >= 2 signs).
  - MIX: VOC + FORM + LEN at the same s.
- **CUN (thinned cuneiform, dilution)**: 2,270 texts; class A = Ur III seal legends; class B = with prob s an OB seal / tag / brick text, else another Ur III seal legend.
- Nulls: Indus s = 0 (MIX kind, labels only) and CUN s = 0.

Grid: VOC, FORM s in {0.25, 0.5, 0.75, 1.0}; LEN {0.5, 1.0}; MIX {0.15, 0.25, 0.5, 0.75, 1.0}; CUN {0.2, 0.4, 0.6, 0.8, 1.0}; nulls. 10 reps per cell. 22 cells, 220 corpora.

## Scale
Supervised gain per corpus: calibrated logistic regression (signs + pairs + first/last/length), held-out bits/text over base rate, exactly genres_scratch `final.py lr_gain`. A cell's signal = mean over its reps.

## Detection rule (per model, per corpus)
K chosen from {1,2,3,4} by 3-fold family CV with the 1-SE rule (restarts: HMM 1, LCA 2, as #34 power runs). Detected iff K* >= 2 AND the held-out log-likelihood gain of K* over K = 1 has a family-bootstrap 95% CI above 0 (300 boots) AND the held-out genre assignment predicts the planted label, label-shuffle permutation p < 0.05 (500 perms). Power of a cell = detections / 10.

## Floor
For each model x plant kind: the lowest-strength cell with power >= 0.8 such that every stronger cell of that kind also has power >= 0.8; its floor = that cell's mean supervised gain. If no cell qualifies, floor > the kind's largest tested gain. Secondary: logistic fit of detection on gain within the kind, gain at 0.8.
**Headline floor** = minimum over the Indus-based kinds (VOC, FORM, LEN, MIX) and models whose null false-positive rate is <= 2/10. CUN is reported separately (it dilutes a strong latent split rather than making a weak one).

## Verdict rule
- Floor > 0.15 bits/text (or no kind reaches power 0.8): the methods cannot see a genre as weak as Indus object type at Indus size. Genres-from-scratch closes as a route; Indus K* = 1 says only that no genre >= floor of these kinds exists. Propose NEGATIVE_ATLAS text.
- Floor <= 0.15: Indus K* = 1 (#34) becomes evidence that no genre of that kind at >= floor exists; route stays open as a negative-at-power result; a 0.15-bit object-type genre should have been found, which then needs explaining.
- A model with null false positives > 2/10 is void for the floor.

## Caveats stated in advance
Plants on real Indus texts with a single class edit are cleaner than real genres; synthetic plants match no model exactly. The floor is per kind; a genre of a different kind could have a different floor. Not a test of any Indus claim; no Indus held-out data is touched beyond the texts used as plant carriers.
