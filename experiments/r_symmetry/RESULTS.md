# r_symmetry: do our refutations survive other sign lists and the other edition?

Prereg `docs/prereg/r_symmetry.md` (sealed 2026-11-24T09:20Z after a fresh Fable review). Code addendum 1 was sealed before power mode. `power.json` was committed before any variant statistic was computed.

## Verdicts
| R row | verdict | what decided it |
|---|---|---|
| MC-MUK23-licence-pairing (T3) | **HOLDS** | kill condition met in all 6 testable families (p 0.62-0.82), including M77 Harappa (S 56.7, p 0.79, power 0.92) |
| MC-KM-tablets-tokens (T1, T3) | **HOLDS** | T3 as above; T1 on M77 with locus as deposit: G 15.9, p 0.84 (power 1.00) |
| MC-MUK23-emblem-organisation | **HOLDS** | AUC 0.514-0.531, p 0.15-0.34 in all 5 testable families, including ICIT square seals (AUC 0.523, p 0.18) |
| MC-LAU10-other-language | **HOLDS** | round excess -0.15 to +0.06, all p ≥ 0.21, in all 7 testable families |
| MC-MUK19-stroked-jar-MET | **UNCHECKED** | every list either leaves the inputs unchanged or merges the stroked jars with the plain jar; M77 pottery (115 texts) has power 0.65 < 0.8 |
| MC-MUK23-cup-vessel-fee | **UNCHECKED** by the sealed code (only 1 testable family); see the note | other edition: Q2 ρ -0.02, p 0.78 (kill met); **Q3 meets the claim's survive bar: ICIT period/phase lots χ² 64.6, p 0.0048** |
| FUN-kriger-hunt, KEY-pierson | out of scope | no K1/K3 plant; the key is defined per Mahadevan sign |

Full table: `table.md`. Data: `shape.json`, `power.json`, `test.json`.

## Note on cup-vessel-fee
- **Both of the sealed rules apply:**
  - fewer than 2 testable families, which gives UNCHECKED (the code checks this first);
  - "survive bar met in any testable family", which gives ARTEFACT.
- **The cell was not new.** Q3's other-edition stand-in is the period/phase test that `m328_measure` had already reported as a secondary (p = 0.005). It was read then as drift of the stroke count over time or batch. The claim's own prediction is clustering by find-spot, which stays refuted (p 0.42, held-out 0.19).
- **The other edition tests a different thing.** The edition swap replaced "find-spot" with "phase", so this cell is not a clean test of the claim's own prediction.
- **Consequence.** UNCHECKED and ARTEFACT both send the row to blind re-rating (scorecard addendum 5). The raters see this note.

## What it means
- **Four of the six refutations are not artefacts of Mahadevan's sign list or of the edition.** They hold under every list that changes their inputs and on the other transcription.
- **The other two cannot be checked this way.**
  - The stroked-jar refutation stands on ICIT alone.
  - The cup-fee refutation stands on its native tests. The one alternative cell available shows the period drift already known.
