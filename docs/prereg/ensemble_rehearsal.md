# Pre-registration: ensemble-guesser rehearsal on proto-cuneiform (Route 3, fable52_plan10)

Written 2026-11-21 (UTC) before any guess was made. The lead has not read the new key.

## Question
One blind guesser got 27% class accuracy on non-recognised proto-cuneiform signs (chance 12.5%), and its confidence did not separate right from wrong (`experiments/guess_rehearsal`). Do signs on which many independent guessers agree reach high precision? If so, agreement marks which guesses to trust.

## Data
- Truth: the 8 function classes in `experiments/protocuneiform/pc_classes.py` (written 2026-11-15, unchanged).
- Targets (`experiments/ensemble_rehearsal/build.py`, a copy of `guess_rehearsal/build.py`): simple signs with a known class, a CDLI drawing and >= 15 line occurrences (floor lowered from 30), one variant per base, up to 10 most frequent per class, EXCLUDING the 40 signs of `guess_rehearsal/sealed/key.json` and every sign sharing a base with them. Seed 20261121052. Result: 40 targets, LIVESTOCK 10, OFFICE_PERSON 10, PLACE_INST 10, OTHER_GOODS 7, VESSEL 2, GRAIN_FOOD 1 (LIQUID_DAIRY and TEXTILE are exhausted by the first study). The majority-class rate is therefore 25%, not 12.5%; the permutation null below keeps each guesser's class mix and so accounts for this.
- Condition C only (drawing + up to 12 whole-tablet contexts, all signs anonymous, numerals `#n` with unit hidden), the best condition before. The general text and class definitions are exactly those of guess_rehearsal.
- Key sealed in `experiments/ensemble_rehearsal/sealed/key.json`.
- Proto-Elamite: skipped. The repo has PE drawings and lines (`experiments/protocuneiform/pe_*`) but no meaning labels, and no labels can be built here from a published sign list by a rule fixed in advance without new sources; most accepted PE meanings also come from proto-cuneiform look-alikes, which would leak. Route 3's "both scripts" condition is therefore tested on one script only.

## Guessers
- N = 10, `G01`..`G10`, each a fresh subagent that reads only its own packet copy `packets/Gxx/` (task.json + images). Target order shuffled per guesser (`orders.json`). Prompt: `experiments/ensemble_rehearsal/guesser_prompt.md` (no web, no other files).
- Model mix: opus G01, G05, G09; sonnet G02, G06, G10; haiku G03, G07; fable G04, G08. Run in pairs, foreground.
- Output `guesses/Gxx.json`: class, gloss, confidence, recognised, recognised_as, reasoning (same as guess_rehearsal).
- A guesser whose file is missing or unparseable after one re-run is dropped; N becomes the number of valid files and agreement shares use that N. A missing or invalid class for one sign counts as a non-vote (still in the denominator).

## Scoring (`experiments/ensemble_rehearsal/score.py`)
- Recognition: a sign is "recognised" if ANY guesser flags it. Recognised signs are excluded from the primary score (reported descriptively).
- Agreement: modal class among the N guessers; share = modal count / N. Ties for the modal class: no modal class, the sign never enters an agreement subset.
- Primary: high-agreement subset S = non-recognised signs with share >= 0.70. Coverage = |S| / non-recognised signs. Precision = correct modal classes in S / |S|, with a Clopper-Pearson 95% CI.
- Bars (from plan 10, point estimates):
  - GO: coverage >= 10% AND precision >= 60%.
  - KILL: precision < 50% OR coverage < 10% (including S empty).
  - Otherwise (precision 50-60%, coverage >= 10%): inconclusive.
- Secondary: precision and coverage at share >= 0.5 and >= 0.6; the full agreement-accuracy curve (0.3 to 1.0); plurality-vote accuracy on all non-recognised signs; permutation null that shuffles each guesser's guessed classes across the non-recognised signs independently (10,000 draws), p for the number of correct signs in the subset at 0.5/0.6/0.7, and the null's mean subset size and precision; single-guesser accuracy for each guesser on the same non-recognised signs (and on its own non-flagged signs), mean and range; majority-class baseline.

## Expectations (stated before running)
Single guessers 20-35% on non-recognised signs. Same-family models will agree often for shared reasons, so the 70% subset will be larger than under the null; I expect precision there of 35-60%, i.e. most likely KILL or inconclusive, and a GO would surprise me.

## Limits
- One script, 40 signs; coverage of 10% of perhaps 30 non-recognised signs is 3 signs, so any precision will have a very wide CI. The bars are point estimates as in plan 10; the CI is reported beside them.
- Guessers are all Claude models; their errors are correlated, so agreement is not independent evidence. Model mix gives only partial independence.
- Recognition is self-reported; a sign recognised by no guesser may still be half-remembered.
- Even a GO gives only a calibrated prior for picture-led guesses; it verifies nothing on Indus.

## Deviation 1 (2026-11-21, before any guess was opened or scored)
The first two guessers (G01 opus, G02 sonnet) read only lines 1-179 of the 778-line task.json in one Read call (the Read tool truncates large files), so they saw contexts for 7 of 40 targets and guessed the rest from drawings alone; this is not condition C. Their files were moved unopened to `guesses_partial_read/` and are not scored. `guesser_prompt.md` now tells guessers to read task.json in chunks and report how many contexts they read; G01 and G02 are re-run with fresh agents of the same models. A guesser reporting contexts read for fewer than 40 ids is re-run once; if still short, it is scored and its shortfall reported. Nothing else changes.
