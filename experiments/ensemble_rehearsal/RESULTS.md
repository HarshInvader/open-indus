# Ensemble-guesser rehearsal (plan 10, Route 3): results

## Verdict: KILL

When guessers agree, they are not right more often. Four of the 26 non-recognised signs reached 70% agreement, and only one of those four had the right class. That gives a precision of 25%. The kill bar is precision under 50%. Coverage passed (15%), but precision failed.

Taken together, the ten guessers do no better than always naming the most common class. Agreement tells us which signs the models find easy to agree on. It does not tell us which guesses are right. By the frozen rule, Route 3 cannot give a way to sort Indus picture guesses into ones to trust and ones to drop.

## Numbers

All figures come from the frozen `score.py` (`results.json`), run on 10 valid guess files over 40 proto-cuneiform signs with 8 classes.

**Recognition.** At least one guesser flagged 14 of the 40 signs as recognised. Those 14 are left out of the primary score, leaving 26 non-recognised signs.

**Primary test (agreement of 70% or more):**
- 4 signs reached it, so coverage is 4/26 = 15.4% (bar: at least 10%, passed).
- 1 of the 4 was right, so precision is 25%, with a 95% CI of 0.6% to 80.6% (Clopper-Pearson). The GO bar is 60% and the kill bar is 50%, so this is a KILL.
- The four signs: T11 was right (OFFICE_PERSON). T05 got GRAIN_FOOD and T10 got LIVESTOCK, but both are OTHER_GOODS. T39 got PLACE_INST but is OFFICE_PERSON.
- One-sided binomial test against 12.5%: p = 0.41.

**Agreement-accuracy curve (non-recognised signs):**

| agreement | signs | right | coverage | precision | 95% CI |
|---|---|---|---|---|---|
| 0.3 | 25 | 7 | 96% | 28% | 12-49% |
| 0.4 | 23 | 7 | 88% | 30% | 13-53% |
| 0.5 | 19 | 6 | 73% | 32% | 13-57% |
| 0.6 | 11 | 4 | 42% | 36% | 11-69% |
| 0.7 | 4 | 1 | 15% | 25% | 1-81% |
| 0.8 | 1 | 1 | 4% | 100% | 2.5-100% |
| 0.9, 1.0 | 0 | - | 0% | - | - |

Precision stays between 25% and 36% at every agreement level up to 0.7. The curve does not climb. The single sign at 0.8 is one data point.

**Permutation null** (10,000 draws, each guesser's classes shuffled across the 26 signs on their own):
- At 0.7: 1 sign right against a null mean subset of 0.04 signs, p = 0.009.
- At 0.6: 4 right against a null mean subset of 0.36, p = 0.0001.
- At 0.5: 6 right against a null mean subset of 2.25, p = 0.0001.
- When the null subset is not empty, its precision averages 21-23%.

The real guessers agree far more often than shuffled ones, so the right count beats the null. Most of that comes from the bigger subsets, not from higher precision: observed precision (25-36%) sits only a little above the null's 21-23% and at the majority-class rate of 27%. The null shows that the guessers are correlated. It does not show that they are accurate.

**Baselines on the same 26 signs:**
- Plurality vote across all 26: 7/26 = 26.9%.
- Always naming the most common class: 26.9%.
- One guesser on its own: mean 24.2%, range 7.7% to 38.5%.
  - opus: G01 23%, G05 31%, G09 27%
  - sonnet: G02 27%, G06 8%, G10 27%
  - haiku: G03 19%, G07 12%
  - fable: G04 31%, G08 38%

The previous single-guesser study got 27% under the same condition C.

**Recognition calls** (descriptive, not scored):
- There were 26 calls on 14 signs; 17 of them had the right class.
- Most calls came from the fable guessers: G08 flagged 11 signs and G04 flagged 9. G05 flagged 3, G01 flagged 2, and the rest flagged none.
- Several sign names were exactly right: MASZ2, AMA, UDUNITA, NIN, GU4 and U8. KUR was named correctly, but the guessers gave it the wrong class.
- The worst miss was T32 (NAGAR, a person or office). Four guessers confidently called it the fish sign KU6. That is the same confident, shared error that makes agreement untrustworthy.

## Deviations and run notes

- **Deviation 1** (in the prereg before any guess was opened) applied. The first G01 and G02 files, made when the guessers read only part of task.json, stay unopened and unscored in `guesses_partial_read/`. Fresh G01 and G02 agents were run.
  - All 10 guessers reported reading contexts for 40 of 40 ids, so no Deviation 1 re-runs were needed.
  - G07 reported its last line as 777 and the others as 778. The file has 777 lines, so all ten read it to the end.
- **Run order.** The prereg says guessers run in pairs. They were run one at a time to avoid rate limits. Each guesser was still a fresh agent with only its own packet, so this does not affect the scoring.
- No API errors and no retries. All 10 files were valid JSON with 40 ids and valid classes. N = 10, so nobody was dropped.
- The hashes of the prereg, `build.py`, `score.py`, `guesser_prompt.md` and `sealed/key.json` matched `docs/prereg/HASHES.txt` before scoring. Scoring ran through `board/run.sh`.

## Limits

- **Small sample.** One script, 40 signs and 26 scored. The primary subset has 4 signs, so its CI runs from 1% to 81%. Still, the curve is flat at 25-36% everywhere it has more than 4 signs, which points the same way as the verdict.
- **Correlated guessers.** All guessers are Claude models, and their errors are correlated, as T32 shows. Mixing models did not make them independent.
- **Recognition removes the easy signs.** The fable models recognised many signs, so a third of the targets were taken out before scoring. Those were probably the signs that are easiest to guess from the picture. The non-recognised set is the hard part of the data.
- **Recognition is self-reported.** A sign nobody flagged may still be half-remembered.
- **Proto-Elamite was not tested** (see the prereg), so Route 3's "both scripts" condition was tested on one script only.
- **Nothing here touches Indus data.** The result only says that agreement among these models does not mark which picture-led guesses are right.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Guesses with 70% or more agreement reach at least 60% precision with at least 10% coverage | refuted (KILL: 25%, 1/4) |
| Precision rises with agreement | not supported (flat at 25-36% from 0.3 to 0.7) |
| Guessers agree more than chance | supported (null p ≤ 0.009) |
| The ensemble beats the majority-class rate | not supported (26.9% vs 26.9%) |

## Files

- `guesses/G01.json` .. `G10.json`
- `results.json`
- `ledger_rows.csv`
- prereg: `docs/prereg/ensemble_rehearsal.md`
