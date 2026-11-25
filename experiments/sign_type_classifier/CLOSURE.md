# Per-sign type classifier: closed at the count gate (plan 12, family 3)

- **Ruling:** closed by the coordinator on 2026-11-25 (D1 = a). The draft prereg stays unpublished, and nothing was sealed.
- **Run:** no feature, classifier or accuracy was ever computed.
- **What was planned:** learn from distribution alone whether a sign is a syllabogram or a logogram. Train on read scripts with known types. Test on a held-out script family. The gate was balanced accuracy of at least 0.75, set against each family's majority-class baseline.

## Count gate
- **The minimum:** written and timestamped before any count, at 2026-11-25T18:23Z. It is in `MINIMUM.txt`. It requires at least 3 eligible families, and the held-out unit is the family.
- **The count:** done with the tokeniser the study would have used (`tokenise.py`, `count_gate.py`). Lines with any damage mark are dropped whole. A numeral group is one token per place. The output is in `count_gate.json`.
- **Indus (M77):** 10,005 tokens and 417 sign types.
- **Eligible: 2 families.**
  - Neo-Assyrian letters (Oracc, CC0): 97,869 tokens, with 142 syllabogram and 69 logogram types per draw of 10,000 tokens.
  - Japanese Wikipedia, as the Sinographic family: majority share 0.831, and 1,387 types per draw.
- **Not eligible:**
  - Linear B: 17,413 clean tokens, against a minimum of 20,000;
  - Linear A: too small, and the licence is unclear;
  - Brahmic: only one sign type;
  - Old Akkadian administrative texts: their lines are Sumerian.
- **Verdict: FAIL, 2 families against 3.** Admitting Linear B would change a rule after counting, so that option was rejected.

## Findings that stand
1. **Labelled families are too few.** Open data gives at most 2 or 3 labelled script families at Indus shape. A test of transfer across families is therefore not possible. This is the second study to stop at this wall, after the disguised-script tournament (atlas 10b.20).
2. **Prior art does not settle the question.** No published classifier of sign type is trained on read scripts and tested on an unseen one. The nearest precedent is our own `meaning_classes`: word classes were learned within each script in 3 of 3, but transferred to an unseen script in 0 of 3.
3. **Determinatives stay untestable at Indus shape** (atlas 1.6). Even cuneiform has only about 9 determinative types per draw of Indus size.
