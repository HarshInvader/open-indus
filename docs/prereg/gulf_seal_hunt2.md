# New inscribed round and foreign seals from open literature: a count gate, then the frozen forward predictions (sealed 2026-11-23, before the search)

Agent `paper`. This is study 1 of the Fable list dated 2026-11-23; see RESEARCH_STATE, "Next unblocked studies".

## Question
Are there at least 8 inscribed seal texts, not yet in our corpus, that are either round Gulf-type seals or Indus-type seals found outside the Indus region? If so, we can score the frozen forward predictions F1 (round seals rarely end in a closer) and F2 (round seals break square-seal order) from `docs/prereg/forward_predictions.md` on independent objects for the first time.

## Eligible
- An object with Indus signs that is not in `experiments/foreign_corpus/foreign_corpus.csv` (55 objects), ICIT or M77.
- It is published in an open source: free PDF, open-access article, or a museum or excavation page. No login walls.
- It is one of:
  - a round, Dilmun or Gulf-type seal, or a sealing from one, from any findspot;
  - an Indus-type seal found outside the Indus region;
  - a round seal from the Indus region whose shape a printed register states.
- Its sign text is published as a drawing with signs individually visible, or as a transliteration in Mahadevan (M) or Wells (W) numbers.
  - A plate photo alone does not count. Plate readers failed at 52% (`plate_corpus`).

## Reading rule
- A transliteration in M or W numbers is used as published.
- A drawing is read by two blind readers (fresh agents). Each reader sees the drawing and the sign list only, never this file or any prediction. Each sign gets an M number and a confidence.
- Only signs both readers agree on are kept. A text with any disputed position is not scored for F2. It is scored for F1 only if its last sign is agreed.

## Kill test (count gate, run first)
- **8 or more eligible new texts:** score F1 and F2 exactly as frozen in `forward_predictions.md` (training = all current M77 texts; thresholds unchanged).
- **3 to 7:** record the list and the count. Run descriptive F1/F2 numbers, labelled underpowered, with no verdict.
- **Under 3:** stop. Record what was searched and what was found.

## Shape rider (no new texts)
- M-1369 (ICIT 3668.1) appears in CISI vol. 2 (`pak_0473`). If the local page states or clearly shows its shape, record it.
- The README #4 count of round seals confirmed by a printed register would then move from 3/8 to 4/8.
- No test is re-run for this.

## Not allowed after the search
- Changing the eligibility, the reading rule, the gate or the F1/F2 thresholds.
- Counting objects that fail eligibility.
