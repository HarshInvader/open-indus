# Fish tick as a closer, v2: the better de-duplication does not rescue the test

Prereg: `docs/prereg/fish_tick_closer_v2.md`. Hashes of the prereg, `dedup.py`, `run_v2.py` and the unchanged v1
`ftc.py` and `run.py` were appended to `docs/prereg/HASHES.txt` at 2026-11-20T22:23:32Z, before any run.
All runs went through `board/run.sh`. Raw outputs: `out_counts.json`, `out_gate.json`. Summary: `results.json`.

## Conclusion

**Verdict by the frozen rule: underpowered. The test stopped at the gate.**

- The new de-duplication works. It keeps 1,507 of 1,698 dev texts; v1 kept 971. Its largest cluster is 7 texts; v1's was 571.
- The gate still fails on dev. Planted merges were found 0% of the time for P1 and 25% for P2. The bar is 80%.
- So the stop rule applied. No real test and no red team were run under v2.
- The degenerate collapse was not the main cause of v1's failure. The real limit is that "plain fish + closer" is rare.
- P1's dev rule cannot pass at this size by design. Two bases (M65/66, M70/71) get only 2 planted tokens. A base needs 3 to be tested. The rule needs 4 of 5 bases.
- v1's verdict (underpowered) stands. The question stays open until there are more texts (CISI 3, HARP).

## Texts kept

| set | distinct texts | v1 collapse kept | v1 largest family | v2 kept | v2 drops (same signs / near) | v2 largest cluster |
|---|---|---|---|---|---|---|
| DEV | 1,698 | 971 | 571 | 1,507 | 7 / 184 | 7 |
| HELD | 571 | 505 | 9 | 550 | 1 / 20 | 3 |
| NEW (post-1977 ICIT) | 326 | 326 | 2 | 301 | 23 / 2 | 5 |

- v1 counts here come from the same union-find as `ftc.collapse`. It reports 972 dev families; v1's analysis used 971 after `prep` dropped one all-break text.
- v2 cuts NEW more than v1 did (301 vs 326). That is step 2 of the unit: ICIT texts that differ only in `|` or `#` now count once.

## Known-answer gate (run first)

200 plantings per set; 30% of "plain fish + closer" pairs merged into one new sign. Detection = the set's frozen bar passes.

| set | planted tokens per base (mean) | P1 detection | P2 detection | P1 false alarm | P2 false alarm |
|---|---|---|---|---|---|
| DEV | 13, 2, 5, 2, 6 | **0.00** | **0.25** | 0.00 | 0.00 |
| HELD | 5, 1, 2, 2, 2 | 0.795 | 0.00 | 0.045 | 0.00 |
| NEW | 2, 1, 0, 0, 0 | 0.00 | 0.00 | 0.00 | 0.00 |

- Gate needs 0.80. DEV fails for both P1 and P2, so the prereg stop rule applies.
- v2 roughly doubled the planted tokens on dev (v1: 2, 2, 4, 2, 3). The M59/60 base now gets 13. The others stay at 2 to 6.
- P2 rose from 0.00 to 0.25 on dev. It needs 0.80.
- HELD P1 reached 0.795, just under the bar. It is a secondary set, and the stop rule is set on DEV.
- No rule was miscalibrated (all false alarms at or below 0.045).

## Real tests and red team

Not run. Stop rule: the DEV gate failed for both predictions. No P1, P2 or red-team number exists under v2.

## Multiple testing

The prereg counts 20 effective tests: v1's 10 plus v2's 10. v2 added none, because nothing past the gate was run.
v1's Holm-adjusted p-values (smallest 0.26) are unchanged.

## Hypotheses

| hypothesis | verdict |
|---|---|
| v1 near-copy collapse caused the gate failure | **Mostly refuted.** It cost texts (971 vs 1,507), but the gate still fails without it |
| P1: ticked-fish contexts match plain fish + closer | underpowered (dev gate 0.00) |
| P2: ticked-final texts carry no other closer | underpowered (dev gate 0.25) |
| Overall: the tick is a closer inside the sign | underpowered (v1 and v2) |

## Deviations

1. The prereg header says "Written 2026-11-21 (UTC)". The hash time is 2026-11-20T22:23:32Z. The prereg was written minutes before the hash.
2. Counts on NEW: v1 reported 326 texts after collapse. The v1 union-find here also gives 326 families, from 330 distinct records (4 empty or break-only). This has no effect on any test.

## Limits

- The gate plants 30% of real "plain fish + closer" pairs, as in v1. Pairs are rare, so this gate is harsh. A gate sized to the real ticked-fish counts was not preregistered, so it was not run.
- The P1 dev rule (4 of 5 bases at p < 0.01) needs at least 3 tokens in 4 bases. Two bases cannot reach that. A pooled dev rule would have more power. Switching to it now would loosen a bar after seeing data, so it was not done. A future test on new texts could preregister it.
- Both editions read the same small ticks from the same photographs. Shared reading errors are not checked.

## Next experiments

- Add a v3 only with new texts (CISI 3, HARP sheet). Preregister a pooled dev P1 rule and a gate sized to the real ticked-fish counts. Do this before looking.
- Other agents should use the v2 unit (`experiments/fish_tick_closer_v2/dedup.py::greedy`) or leader clustering (`experiments/genre_floor/floor.py`) to reduce texts to one per family. Do not use the chaining union-find for that.
