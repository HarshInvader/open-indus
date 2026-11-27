# raj_check stage 5b: names chosen for their picture words (prereg T9b)

2026-11-27. Written and hashed before any 5b run or agent. Known: T0–T8, and the stage-5 search in progress (half-A training objective only, not its held-out test).

## Question
A list-builder who knows the signs' pictures might favour names whose parts are words for those pictures (the rebus words). Two questions: (1) is the paper's Tamil list richer in such names than our rebuilt Tamil lists? (2) if a Japanese list is built the same way, from names containing the Japanese picture words, how does it score? Openly labelled as deliberate picking; not evidence for Japanese; no claim about how the paper's list was made.

## 1. Diagnostic (descriptive)
For each list, with its own picture words and the contest's own rule (a name part is a picture candidate if it is in the list's part vocabulary used by the contest, i.e. length ≥ 2 and in ≥ 2 names, and equals a picture word or matches one with same first letter, length within 3, pun cost ≤ 0.5): share of names with at least one picture-candidate part. Lists: paper's Tamil, Tamil 4b, Tamil faithful (T8b), Japanese T4, and T8's C6 (paper-only names) and C7 (4b-only names). Expected if the idea is right: paper's Tamil and C6 higher than the rebuilt lists and C7.

## 2. Japanese, picked by rule (J_sym1)
From the 1,125 T4 Japanese names, keep every name with at least one picture-candidate part (rule above, computed on the 1,125). No contest score is used to pick.

## 3. Japanese, built from the symbols (J_sym2)
A fresh agent compiles about 1,300 attested Japanese names (family names, place names, mountains, rivers, shrines and gods; no invented names) each containing at least one native Japanese word from the T4 picture-word list, segmented in the T4 format. A fresh labeler (the T4 labeler prompt) labels parts not already labelled in T4. Sino-Japanese parts dropped as in T4; first 1,125 names kept.

## Runs and readings
Raj's `contest.py` unchanged, T4 picture words, seeds 0–9, full corpus; also on the stage-5 seal half B for comparison with stage 5. For each of J_sym1 and J_sym2 (full corpus):
- **"Picking by picture words lifts a wrong language to the paper's Tamil level"** if D ≥ 223.0;
- **"most of the way"** if 111.5 ≤ D < 223.0 with at least 8 of 10 seeds above control;
- **"does not"** otherwise.

## Limits
One agent, one labeler; the agent knows its names must contain picture words, which is the point. Full-corpus runs use all seals (the picking rule does not look at seals or scores, so no held-out split is needed for it).
