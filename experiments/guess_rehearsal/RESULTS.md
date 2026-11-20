# Educated-guess rehearsal on proto-cuneiform: does it work when the answers are known?

Owner's request, 2026-11-20. Pre-registration: `docs/prereg/guess_rehearsal.md`. Its sha256, together with those of `build.py`, `score.py` and the sealed key, was appended to `docs/prereg/HASHES.txt` before any guess was made. Numbers: `results.json`. Guesses: `guesses/{A,B,C}.json`.

## Verdict: educated guessing of sign meanings fails its pre-registered bar on a script whose answers are known. By the frozen rule, no Indus meaning key is produced from it.

- **Best condition, picture plus context:** 9 of 33 signs the guesser did not recognise from memory got the right meaning class. That is 27%, against 12.5% by chance (binomial p = 0.017).
- **The bar:** at least 40% with p < 0.01. Every condition missed it.
- **Even the 27% is generous.** All three guessers worked out that the script was proto-cuneiform from Uruk. They knew the culture and the kind of document, a head start we would not have for the Indus script.
- **Memory was not reliable either.** In condition C, 2 of the 7 signs flagged as "recognised" were wrong:
  - the oil sign was taken for "head";
  - the cow sign was taken for "arrow".

## Numbers (40 signs, 8 meaning classes, chance 12.5%)

| Condition | All signs | Not recognised (primary) | Binomial p (primary) | Permutation p (all) | Recognised |
|---|---|---|---|---|---|
| A: picture only | 13/40 (33%) | 7/33 (21%) | 0.11 | 0.001 | 7 |
| B: context only | 9/40 (23%) | 9/40 (23%) | 0.055 | 0.087 | 0 |
| C: picture + context | 14/40 (35%) | 9/33 (27%) | 0.017 | 0.0003 | 7 |

- **Confident guesses:** almost every guess at confidence 0.6 or above was a sign the guesser recognised (A 3/3 right, C 4/4 right). Among signs worked out rather than remembered, confidence stayed at 0.15-0.55. The guessers did not fool themselves, but they also had nothing solid to go on.
- **Glosses:** the pre-registered judge pass on glosses was not run. Class accuracy already decides the verdict. Glosses are listed in `results.json` for anyone who wants to judge them.

## One thing that does work (exploratory, not pre-registered)

Collapse the 8 classes to two: counted goods versus people, offices and places. Then **context alone** gets 31 of 40 right (78%). That beats the majority baseline of 70% (permutation p = 0.0003).
- Pictures do not help with this split: A gets 67% and C 70%.
- So distribution reliably shows *what kind of slot* a sign fills (counted item or not), but not *what* it means.
- That is the same level the Indus project already reaches with its functional reading (README #9).

## What this means for the Indus script

- An AI looking at sign pictures and contexts with general historical knowledge does not recover meanings reliably, even on a more pictographic, number-rich script whose culture it has identified.
- Indus signs are less pictographic and the culture is less known. Expect worse there.
- So a history-informed meaning key for Indus signs would be mostly invention. Its "hits" could not be told from luck.
- Coarse role (counted item, or person, office or place) is recoverable from distribution. The project already has that.

## Limits

- Only one rehearsal script, with 40 signs and coarse classes. The confidence intervals are wide: 27% has a 95% interval of roughly 13-46%.
- Each condition had one run of one model.
- Recognition was self-reported.
- The 8-class truth is coarse, and some guesses fell in a neighbouring class (vessel vs liquid). A lenient scorer would give a few more points. It would not reach 40%.
- Proto-Elamite, a less-known script, was not run. The result here already fails, and a harder script would be expected to fail harder.

## Files

- `build.py`: makes the blind packets and the sealed key.
- `score.py`: scorer.
- `guesses/`: the three guess files.
- `sealed/key.json`: the answer key, unsealed after scoring.
- `packets/`: the blind packets with CDLI drawings. Not committed; rebuild with `build.py`.
