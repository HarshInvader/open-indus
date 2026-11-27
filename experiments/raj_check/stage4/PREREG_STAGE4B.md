# raj_check stage 4b: the other Dravidian languages, and a fresh Old Tamil list (prereg T7)

2026-11-27. Written and hashed before any stage-4b agent ran or any stage-4b score was seen. Known: T0–T6. In particular stage 4a: Tamil's score comes from its place, hill, river, god and group names (people only: +2.9; size-matched mixed subsets: median +178).

## Why
If the contest detects Dravidian, Old Tamil's sister languages should also fit the seals well. And if the paper's Tamil list is not special, a fresh Old Tamil list built by a new agent the same way should score like it. Stage 4a showed that the kind of name matters, so every list here is built the way the paper built its rival list (REP-1, Vedic Sanskrit): proper names of every kind, compiled by an agent who knows nothing of this project, from the language's earliest texts.

## Languages
| Run | Names from |
|---|---|
| Old Tamil, fresh list | Sangam poems and Tamil-Brahmi inscriptions |
| Old Kannada | Kannada inscriptions to about 1200 CE (Halmidi onward) and early literature (Kavirājamārga, Pampa, Ranna) |
| Old Telugu | Telugu inscriptions to about 1200 CE (Kalamalla onward) and early literature (Nannaya, Tikkana) |
| Old Malayalam | Malayalam and Kerala Tamil inscriptions to about 1400 CE (Vazhappally, Syrian Christian and Jewish copper plates and others) and early literature (Rāmacaritam, Uṇṇunīli Sandēśam) |

## Building the inputs (one fresh agent each step, prompts saved in `agents/`)
1. **Compiler**: Raj's REP-1 Sanskrit name-compiler prompt with only the language and sources changed. About 1,400 proper names of every kind (people, groups, lineages, deities, places, rivers, hills), each split into members in dictionary form with glosses, type and source. Web use allowed; no invented names.
2. **Translator** (blind: sees only the 171 English entries): Raj's REP-1 Tamil translator prompt with only the language changed. Native words of the old language; no Sanskrit or Prakrit loans. ISO 15919 / Tamil Lexicon style transliteration with diacritics, as Raj's Tamil.
3. **Labeler**: the stage-2 labeler prompt (Raj's categories), plus one category, `sanskrit_loan` (a word borrowed from Sanskrit or Prakrit), as in Raj's Tamil file. Loans are dropped by the contest's loan rule; a name with no native member left is dropped. Stability from Raj's `category_stability.json`.
4. **Checker**: a fresh agent checks 50 random names and 50 random picture words per language (seed 20261127) against standard dictionaries (DEDR, Tamil Lexicon, Kittel, Brown/Gwynn, Gundert) and epigraphic sources. More than 10% wrong in either sample sends that list to a fresh agent once; if still above 10%, the language is reported as void.
5. Names taken in the compiler's order until 1,125 kept, or all if fewer (reported).
6. Number words: Tamil as REP-1 (oru, iru, mū, nāl, ai, aṟu, ēḻu, pattu); Kannada ondu, eraḍu, mūru, nālku, aydu, āru, ēḷu, panneraḍu; Telugu okaṭi, reṇḍu, mūḍu, nālugu, aidu, āru, ēḍu, panneṇḍu; Malayalam oṉṉu, raṇṭu, mūṉṉu, nālu, añcu, āṟu, ēḻu, pantraṇṭu. weights "once", punmax 0.5.

## Test (Raj's `contest.py` unchanged; seeds 0–9; real and null)
Reported for each: D ± sd, seeds above control, seeds ahead of Raj's Tamil (T0), picture options per sign, signs read, names used, mix of name types.

Readings fixed now:
- **Fresh Old Tamil.** "Raj's list is not special" if D ≥ 178.4 (80% of T0). "Raj's list is special" if D ≤ 111.5 (half of T0). Otherwise "partly".
- **Sister languages.** "The contest favours Dravidian" if at least two of the three sisters reach D ≥ 111.5 with at least 8 of 10 seeds above control. "The contest does not favour Dravidian" if none of the three reaches D ≥ 111.5. Otherwise "mixed".
- Both readings are reported together with stage 3: a Dravidian sister that scores below Sumerian (+103.5) is reported as such.

## Limits stated now
- These lists are from later texts than the Sangam corpus (Kannada from about 450 CE, Telugu about 575 CE, Malayalam about 830 CE) and carry many Sanskrit loans, which are dropped.
- One compiler and one translator per language; agent errors are possible; the checker limits but does not remove them.
