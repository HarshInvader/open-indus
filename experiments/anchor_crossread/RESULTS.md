# Anchor cross-read: true name pairs separate from false ones with no language model, but only with direction known, at 15 pairs, and not once 20% of signs are unread.

- **Prereg:** `docs/prereg/anchor_crossread.md`, sealed 2026-11-25 as v4 (tag `anchor_crossread`).
- **Code:** `run.py`, hashed before any run (tag `anchor_crossread_code`). The hash was re-checked before each mode.
- **Runs:** `kill`, `ladder` and `cells`, each once and in that order, detached with a pid file, under the Indus compute lock and `board/run.sh`, 4 workers.
- **Outputs:** `kill.json`, `ladder.json`, `cells.json`, plus their `.out` logs.
- **Scope:** a rehearsal on Ur III sealed tablets. No Indus key is scored, no Indus text is read, and no outcome supports or counts against any Indus reading. Arm C uses M77 sign statistics only. Because both sides of each pair are cuneiform, the Ur III result is an upper bound on power.
- **Clause (b) of the 2027 bar:** still unruled. No cell, bar or reading depended on it.

## Kill test
- **Recount (A1):** reproduced 1,316 true pairs (POS), 224 mismatched pairs (NEG) and 128 variant pairs (VAR). F2 projected 4.8 processor-hours, so no fallback was applied.
- **Kp, planted sets:** 20 of 20 passed (bar ≥ 19).
- **Kc, re-pairing null:** 0 of 20 passed (bar ≤ 1).
- **K0 at 15 pairs:**

  | arm | freedom | K0a, mismatched sets passing | K0b, true sets passing | K0 |
  |---|---|---|---|---|
  | B2 | any start, either direction | 0 | **13** | fail (edge, reading 9) |
  | B1 | any start, forward only | 1 | **20** | **pass** |
  | A | name span given | 0 | 20 | pass (record) |

  - The sealed fallback F1 moved the claim from B2 to B1.
  - Kk did not run, because K0a did not fail.

## Ladder, cell P: true sets passing out of 20 at each number of pairs m
Mismatched sets passed 0 of 20 at every rung below 15 in every arm.

| m | B2 | B1 | A |
|---|---|---|---|
| 15 | 13 | **20** | 20 |
| 12 | 14 | 14 | 20 |
| 10 | 12 | 13 | 20 |
| 9 | 4 | 12 | 17 |
| 8 | 3 | 9 | 19 |
| 7 | 2 | 5 | 12 |
| 6 | 1 | 1 | 8 |
| 5 or fewer | 0 | 0 | 0 |

- **Claimed m:** B1 15 (the claiming arm), A 8, B2 none.
- **Value bar:** not met.

## Cells, claiming arm B1: true sets passing out of 20
| cell | what changes | m 15 | 12 | 10 | 9 | 8 | claimed m |
|---|---|---|---|---|---|---|---|
| R1 (binding) | 20% of legend signs unread, the reading-gate floor | 10 | 10 | 3 | 4 | 5 | **none** |
| C1 (binding) | Indus sign statistics, values drawn by frequency | 20 | 20 | 18 | 17 | 15 | 9 |
| R2 | 25% of name units written as word signs | 9 | 8 | 11 | 4 | 3 | none |
| R3 | editor-resolved readings (upper bound) | 18 | 18 | 14 | 7 | 5 | 12 |
| C2 | Indus statistics, values drawn evenly | 20 | 20 | 19 | 19 | 13 | 9 |

## Frozen readings
- **Reading 5:** "B2 has no claim and B1 claims. The legend's reading direction must be known from outside the set."
- **Reading 4:** "The test works on clean Ur III legends only. At the reading gate's floor, or at Indus sign statistics, 15 pairs are not enough. Section 4 stays. The minimum event is restated as more than 15 pairs."
  - The cell that triggers it is R1. With 20% of signs unread, true sets pass only 10 of 20 even at 15 pairs.
  - C1 (Indus sign statistics) claims m = 9.
- **Notes the code adds:**
  - Reading 9: B2's 13 of 20 at the top rung is at the edge and is read as a fail.
  - Reading 7a: the claim of m = 15 rests on one rung, since B1 has 14 of 20 at 12.
  - Reading 8: a passing set shows that the pairing is real. It does not certify single values; the rule may count the set, never a value.
- **Record only (rung 20):**
  - B2 passes 19 of 20 and B1 20 of 20.
  - In passing sets the median number of correctly recovered values is 2 to 4.5.

## What this can and cannot say
- **It can say:** with no language model, a set of 15 known names on 15 legends can be told apart from false pairings on clean Ur III legends. This works only if the legends' reading direction is known. False pairings almost never pass.
- **But:** at the reading gate's floor, with 20% of signs unread, even 15 pairs do not pass. So the minimum anchoring event for Indus is more than 15 name–legend pairs. That is well beyond the two pairs at most known today.
- **Recovered values:** a passing set certifies the pairing, not the values. In passing sets at 15 pairs, the median number of correctly recovered values is 1 to 2.5 across cells (2 in cell P). The 10-values part of the 2027 bar is not reachable by this route at these sizes.
- **It cannot say:**
  - what power the test has across two different scripts. Here both sides are cuneiform, so this is an upper bound;
  - anything about any Indus reading.

## Disclosures
- **Kill test order:** the sealed fallback F1 (from B2 to B1) was applied as written. All three arms ran the full ladder for the record, as the prereg says.
- **Reading 4a:** R1 had 2 mismatched sets passing at m = 12, above the bar of 1. The code checks 4a only at rung 15, where R1 had 0, so 4a was not added. This is marked `# PREREG-AMBIGUITY:` in `run.py`. Under a reading that checks every rung, 4a would add the sentence "Unread signs raise the false-pass rate"; reading 4 stands either way.
- **Implementer choices:** marked `# PREREG-AMBIGUITY:` in `run.py`: tie-keeping in the search, F2's projection, CDLI loading as in the drafter's count script, and big-endian seed bytes.
- No rerun, no tuning, no fix tags.
