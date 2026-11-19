# Pre-registration: red team of bench_restoration (IIT Hyderabad masked-sign release, Zenodo 24164070)

Written 2026-11-19, before any score in this red team was computed. Code: `experiments/redteam_bench_restoration/rt.py`
(hashed with this file in `docs/prereg/HASHES.txt`). The original bench code (`experiments/bench_restoration/*.py`)
was NOT read or imported; only its RESULTS.md and prereg were read. Leakage detection, the trigram and the Hit@k
evaluation are written from scratch. Before hashing, the code was only run in `--smoke` mode (truth signs replaced by
a random relabelling), which exercises every path without producing a real outcome.

## Claim under test (experiments/bench_restoration/RESULTS.md)
C1 rebuild: scoring the deposited probabilities against our M77 reproduces their Hit@1 within 0.5 points.
C2 leakage: 107/296 test texts (36%) have a near copy in the training pool.
C3 tie: on clean texts their transformer (28.5% Hit@1) does not beat a plain trigram (29.8%).
C4 inflation: leaked texts score far higher than clean texts (blend 57.8 vs 30.5).

## Data
- Deposit: `experiments/bench_restoration/raw/dep/zenodo_deposit/data` (fold_assignments.csv,
  masked_positions_exhaustive.csv, predictions/test_probabilities.npz). Read-only.
- Text id `N` = M77 text_no N side 0; `N.k` = text_no N side k. Sequence = our M77 `seq` with `|` dropped.
- Train pool = deposit `train` + `val` (1,282 texts; what their final models were fitted on). Test = the 296 texts in
  masked_positions_exhaustive.csv.

## Near-copy rule (my own definition)
Two texts A, B (sign lists, |A| <= |B|) are near copies under rule R(k, contain) if
  (a) A == B, or
  (b) sign-level Levenshtein(A, B) <= k and min(|A|, |B|) >= 4  (edits on 2-3 sign texts are too cheap to mean a copy), or
  (c) contain = True and A is a contiguous substring of B and |A| >= 3.
PRIMARY rule: R(1, contain=True) on the M77 sign list.
Sensitivity (descriptive): k in {0, 1, 2} x contain in {True, False}; and R(1, True) after mapping signs through the
sign-list variants `parpola`, `lump_fish`, `lump_all`, `img_lo` (experiments/signlist_robustness/variants.json).
A test text is LEAKED if any train-pool text is a near copy of it.

## Models scored
- Their KN-3, transformer, blend: argmax / ranks from test_probabilities.npz (column j = sign j+1; ties broken by
  higher probability then lower sign id, i.e. stable sort).
- My trigram (PRIMARY baseline): interpolated Kneser-Ney trigram, discount D = 0.75 at every order, base distribution
  uniform over the 417 signs mixed in by the unigram back-off weight, BOS/EOS padded, fitted on the train pool. Each
  candidate c at position i is scored by the log-probability of the whole text with c in place (only the up-to-3
  trigrams that touch position i change, so only those are summed).
- My Witten-Bell trigram (secondary, robustness to smoothing choice), same scoring.
- Unigram frequency (floor).
Metrics: Hit@1, Hit@5, MRR over masked positions.

## Tests and kill criteria
K1 (C1): any of their three models' Hit@1 over all 1,403 positions differs from their README (39.56 / 37.49 / 40.84)
   by more than 0.5 points -> C1 WEAKENED.
K2 (C2): leaked share of the 296 test texts under the PRIMARY rule outside [30%, 42%] -> C2 WEAKENED.
K3 (C3): on CLEAN positions (PRIMARY rule), transformer Hit@1 minus my KN trigram Hit@1 > +3.0 points -> C3 WEAKENED.
   Also reported: paired bootstrap over clean texts (10,000 resamples, seed 20261119), 95% CI and one-sided p, for
   transformer - KN trigram and blend - KN trigram.
K4 (C4): blend Hit@1 on leaked minus clean <= 5 points -> C4 WEAKENED.

## Split question
S1: does fold = int(sha256("ebuds:" + object_id)[:8], 16) % 5 reproduce every row of fold_assignments.csv
    (object-level hash = random by object, not by text family)?
S2: are near-copy families split across folds? Count test texts whose near copies (PRIMARY rule) sit in other objects.
S3: is 36% leakage typical of a random object-level split? Draw 200 alternative object-hash splits (salts
    "rt:0".."rt:199", fold 0 = test, all other objects = train pool, test texts of >= 2 signs), report the leaked-share
    distribution (median, 2.5-97.5%). A text-family split gives 0 by construction.

## Verdict rule
- SURVIVES: none of K1-K4 trips.
- WEAKENED: one or more of K1-K4 trips, but not the REFUTED condition.
- REFUTED: K2 trips with leaked share < 15% AND the transformer beats my KN trigram on clean by > 3 points with the
  bootstrap 95% CI excluding 0 (both main pillars fail).
Sensitivity results do not change the verdict, but if the transformer beats my KN trigram on clean by > 3 points with
CI excluding 0 under any k/contain variant, RESULTS.md must say the "tie" depends on the leak definition.

## Compute
One process via board/run.sh, numpy only, < 1 GB RAM. Tests run: 4 kill criteria + 2 bootstrap CIs + descriptive grid.
