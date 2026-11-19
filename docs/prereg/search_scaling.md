# Pre-registration: search_scaling (is weak blind recovery under a related language a search artefact?)

Written 2026-11-18 (UTC) by agent `paper`, before any run. Follows `experiments/redteam_decipherability` (C3 weakened: a climb from the true key ends 66-83% right, while blind search with 4 restarts reaches 4-13%). Literature motivation: Berg-Kirkpatrick & Klein 2013 (https://aclanthology.org/D13-1087/): on Zodiac 408 one restart gave 18% and 100 restarts 90%. Code: `experiments/search_scaling/ss.py`, which reuses `rt.py` unchanged (data, models, score, annealed Gibbs search).

## Design

- Related-language model (K2), q = 0, 2,500 tokens, both pairs (Latin text / Italian model; Finnish text / Estonian model), replicates 0-2 (the same corpora as the red team).
- Arm R (more restarts): 200 independent restarts of the red team's search (300 sweeps each).
- Arm S (slower annealing): 20 restarts with 3,000 sweeps each.
- Read-out: best-of-n curve. The accuracy of the highest-scoring key among n restarts (n = 1, 4, 10, 50, 200), bootstrapped from the 200 runs. Also the highest accuracy any restart reached, and the share of restarts scoring above the true key.

## Predictions and rules (fixed now)

Reference value per replicate: the red-team climb accuracy at 2.5k (Latin 0.77, Finnish 0.69 on average).

- **H1 (search artefact):** best-of-200 accuracy reaches at least 0.50 averaged over the 6 replicates. Then more search largely fixes blind recovery.
- **H0 (not a search artefact):** best-of-200 accuracy is at most 0.25 averaged. Then more search does not help, and anchors are needed.
- Between 0.25 and 0.50: partial.
- Arm S is judged on the same thresholds using best-of-20.
- Also reported:
  - whether any restart scores above the true key while being below 0.5 accurate (C3 again, at scale);
  - the correlation of score and accuracy across restarts.

## Planted check

The same code under the true-language model (K0) must reach at least 0.90 with best-of-4 at 2.5k (the red team found 0.998). It is run for replicate 0 of each pair before the main arms. If it fails, the result is uninformative.

## Limits

2.5k tokens only (cost). This tests the search, not Indus. Compute: one worker, background priority, under the shared compute lock.
