# raj_check stage 4a: Tamil on equal terms (prereg T6)

2026-11-27. Written and hashed before any stage-4a run. Known: T0–T5 (Tamil +223; Japanese +134.5; Sumerian +103.5; Egyptian +77.6; Finnish +63.7; Sanskrit −13.3).

## Why
Tamil had two inputs no other language in our panel had:
1. **Spelling.** The contest's sound matcher (`nphon.py`) has cheap near-matches for Tamil letters (ṉ≈n 0.2, ḷ≈l 0.35, ṟ≈r 0.35, long≈short vowels 0.3, ṭ≈t 0.6 and so on). Japanese, Finnish, Sumerian and Egyptian were written in plain ASCII, as the plans fixed, so they get only the generic near-matches.
2. **Kinds of names.** Raj's Tamil list (`names_model_clean.jsonl`) is names of every kind from the Sangam poems and Tamil-Brahmi: 532 people, 240 places, 98 deities, 87 groups, 37 lineages, 33 hills, 29 celestial, 14 rivers and others. The other lists are personal names or surnames only.

## Runs (Raj's `contest.py` unchanged; seeds 0–9; real and null; Raj's headline Tamil inputs otherwise unchanged)
- **T6a, Tamil in ASCII (headline of this stage).** Every Tamil string in names, name parts, picture words and config (number words, drop and keep lists) is converted mechanically to plain ASCII: Unicode NFD, combining marks removed (ṉ→n, ḻ→l, ā→a, ṭ→t, ṟ→r and so on). Nothing else changes. If two parts merge into one spelling, the first label in file order is kept (counted and reported).
- **T6b, Tamil people only (descriptive).** Only names of type "person" (532), original spelling. Size-limited; reported, no verdict.
- **T6c, Tamil people only, in ASCII (descriptive).** Both changes.

## Reading T6a (fixed now)
D_A = mean over seeds of (real − null), against Tamil T0 D = 223.0.
- **Spelling explains most of Tamil's lead over Japanese:** D_A ≤ 134.5 (Japanese's score).
- **Spelling explains little:** D_A ≥ 178.4 (80% of T0).
- **Spelling explains part:** otherwise.
Also reported: seeds above control, picture options per sign, signs read, for all three runs.
