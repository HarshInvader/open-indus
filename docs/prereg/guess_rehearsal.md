# Pre-registration: educated-guess rehearsal on proto-cuneiform (known answers hidden)

Written 2026-11-20 before any guess was made. Owner's request: before guessing meanings of Indus signs from history, pictures and context, rehearse the same method on a script whose meanings are known, find how much evidence it needs, then freeze it.

## Question
Can an AI agent, reasoning from a sign's picture and/or its contexts, assign the right meaning class to proto-cuneiform signs it is not told the names of? Which evidence condition is cheapest for a given accuracy?

## Data
- Truth: function classes in `experiments/protocuneiform/pc_classes.py` (written 2026-11-15 from PC scholarship, before this study), 8 classes.
- Targets: `build.py` takes, per class, up to 6 most frequent simple (non-compound, non-numeral) signs with >= 30 line occurrences and a CDLI drawing, one variant per base sign. 40 targets: PLACE_INST 6, OTHER_GOODS 6, OFFICE_PERSON 6, LIVESTOCK 6, VESSEL 6, LIQUID_DAIRY 5, TEXTILE 3, GRAIN_FOOD 2.
- Key sealed in `experiments/guess_rehearsal/sealed/key.json` (sha256 in HASHES.txt). The lead does not read it before scoring.

## Conditions (each run by a fresh agent that sees only its packet)
- A: picture only (CDLI drawing of each target, file named by anonymous id).
- B: context only (up to 12 whole tablets per target; all signs anonymous; numerals shown as `#n`, unit type hidden).
- C: picture + context.
All get the same one-paragraph setting (an early Bronze Age urban society, short texts on small clay objects, many with numbers) and the 8 class definitions. Guessers must flag any sign they recognise from memory (and name it); those are scored separately.

## Outputs
`guesses/{A,B,C}.json`: per id: class (one of 8), gloss, confidence 0-1, recognised (bool), recognised_as, reasoning.

## Scoring (`score.py`)
- Primary: class accuracy on signs NOT flagged as recognised, per condition. One-sided binomial vs 1/8.
- Secondary: accuracy on all signs; permutation p (guessed classes shuffled across signs, 20,000); accuracy at confidence >= 0.6.
- Gloss: a separate judge agent, blind to condition, marks each gloss right / partly / wrong against the sign's conventional meaning. Descriptive.

## Decision rules
- The method is "worth applying to Indus" only if the best condition reaches >= 40% class accuracy on non-recognised signs with binomial p < 0.01, AND at least 10 signs are non-recognised in that condition. Otherwise: report that educated guessing is not shown to work, and do not produce an Indus key from it.
- Cheapest adequate condition = the cheapest (A < B < C) within 5 points of the best.
- If most signs are flagged as recognised (> 30 of 40), the rehearsal is contaminated: verdict "uninformative", move to a less-known script.

## Expectations (stated before running)
A 30-45%, B 20-35%, C 40-55% on non-recognised signs. Heavy recognition in A and C is likely (PC drawings are well known).

## Limits
- One rehearsal script; proto-cuneiform is more pictographic and more numerical than Indus, so success here is an upper bound for Indus.
- Same underlying model guesses in all conditions; independence is only per-run context.
- Truth classes are a coarse 8-way scheme; a sign can fit two classes (e.g. vessel vs liquid).
