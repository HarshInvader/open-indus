# Meaning classes from genre-matched seal and label corpora (board task #14, H1; reopen of #8)

## Verdict

**Negative, and this time the method has enough power, so the negative counts.** Genre-matched training does not rescue cross-script transfer of word meaning classes (NAME / CONTENT / FUNC). Nothing was applied to Indus.

- **The method works when the held-out text comes from a system it was trained on.** In the pre-registered power check, training on the other two scripts plus half of script S and testing on the other half of S passes the #8 bars in **all 3 scripts**:
  - Ur III seals: macro-F1 0.52 against a null 95th percentile of 0.50
  - Egyptian verbless phrases: 0.46 against 0.42
  - Latin labels: 0.42 against 0.36
  - Within-script ceilings are 0.82, 0.61 and 0.65.
- **On an unseen script it fails in all 3 scripts:**
  - Ur III seals: 0.41 against null 95th percentile 0.55 (p = 0.30)
  - Egyptian: 0.22, below the frequency-only baseline of 0.26 (p = 0.89)
  - Latin labels: 0.35. That just beats the null 95th percentile (0.34, p = 0.035), but it misses the bar of baseline + 0.10 (0.37).

So the class signal is real inside each seal or label system, but how it shows in position and partner statistics is specific to each system, even within one genre. That repeats #8's result, now with power shown and the genre objection removed.

Pre-registration: `docs/prereg/meaning_classes_seal.md` (hash in HASHES.txt, tag meaning_classes_seal), written before any corpus or score was computed. Features, model and scoring were imported unchanged from `experiments/meaning_classes/mc_gate.py`.

## Data (all public)

| script | source | units (2-17 tokens, distinct) | scored types per draw (classes) |
|---|---|---|---|
| cun_seal: Ur III seal legends | ORACC epsd2/admin/ur3 lemmatised JSON, CC0 (562 MB, `raw/ur3.zip`). Lines labelled "seal N"; POS from ORACC | 6,467 | about 420: NAME 327, CONTENT 95 (FUNC: 9 tokens in total, because ORACC tags "son" and "servant" as nouns) |
| egy_nom: Earlier Egyptian verbless sentences | TLA v18 (local), UPOS | 2,640 | about 630: CONTENT 399, NAME 159, FUNC 74 |
| lat_label: Latin stamps, labels, instrumentum | EDH (local), #8's capitalisation heuristic | 1,833 | about 405: NAME 266, CONTENT 126, FUNC 13 |

## Numbers (mean over 5 draws; null = 200 label permutations on draw 0)

| step | held-out | full | baseline | null 95th pct | p | pass |
|---|---|---|---|---|---|---|
| power (same system, other half) | cun_seal | 0.521 | 0.340 | 0.500 | 0.040 | yes |
| power | egy_nom | 0.463 | 0.244 | 0.416 | 0.015 | yes |
| power | lat_label | 0.417 | 0.276 | 0.362 | 0.010 | yes |
| gate (unseen script) | cun_seal | 0.411 | 0.363 | 0.549 | 0.30 | no |
| gate | egy_nom | 0.216 | 0.257 | 0.421 | 0.89 | no |
| gate | lat_label | 0.348 | 0.270 | 0.343 | 0.035 | no (misses base + 0.10) |

Exact values are in `results.json`; the run log is `gate.log`.

| hypothesis | verdict |
|---|---|
| The method can recover a known class signal at Indus size (power check) | supported (3/3) |
| Genre-matched training transfers meaning classes to an unseen script | refuted (0/3) |
| Indus sign classes | not estimated |

## Caveats

- **Only 3 scripts.** The board asked for 4-5. Linear B was dropped because the only local word-class source defines names by their position on the line, which would leak the features into the labels. The pre-registration said so in advance.
- **Some classes are missing or thin.** Cuneiform seals have no FUNC class, and the Latin labels come from a heuristic.
- **The power check uses halves, not independent draws.** The Egyptian and Latin corpora are too small for two disjoint draws of 2,300 units, so the power check used half-corpus test sets (1,320 and 916 units).
- **Class mix differs by script.** NAME is 77% of scored cuneiform-seal types against 25% of Egyptian. Since features are rank-normalised within each script, part of the transfer failure may be this shift in class mix. I did not correct for it: trying a different model after seeing the result would be tuning against the gate.

## What would change this

M4 by this route is closed unless one of two things appears:
- a class signal whose surface form is shared across systems, which this result argues against;
- or a training script that is a close relative of the Indus system. No such script is known.

I would not reopen this with more scripts of the same kind. The failure is in transfer, not in power.
