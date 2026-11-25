# split_witness count gate

2026-11-25. Rules: `MINIMUM.txt` (sha256 `ff807dc40887736d240ac67a6724e5375684445832d7b9447bca6ffca7e161a5`, recorded 2026-11-25T19:35:57Z in `MINIMUM.sha256`), written before this count. Script: `count_gate.py`, output in `count_gate.json`. No cohesion value or percentile was computed at any real split.

## Verdict: the gate fails on both conditions. Stop (MINIMUM F1).

| condition | needed | found |
|---|---|---|
| eligible units after the family rule | ≥ 200 | **25** (22 wraps, 3 face splits) |
| Null 2 minimum achievable p on those units | ≤ 0.01 | **1.0** (every unit has exactly one capacity placement) |

Either condition alone closes the study. The capacity null fails at any n: with a median capacity, the split position is fixed, so no p below 1 is possible.

## Counts

**Wraps confirmed by both editions (W).** 118 ICIT records have a `|`, and 26 survive:
- 38 have damage or are incomplete.
- 18 have a line of one sign.
- 6 do not have exactly 2 lines.
- 15 have no M77 link.
- 15 fail on the M77 side: 9 line counts differ, 3 are not 2 lines, 2 are mixed direction, 1 is incomplete.

The family rule leaves 22, all square seals: 6 linked by register, 16 by signs. One has the lines in reverse order between the two editions.

**Face splits (F).** 902 multi-face objects give 2,178 ordered face pairs. The rules leave 25 events:
- 738 pairs drop because a face has a `|` or a `#`.
- 54 drop because the joined text has fewer than 3 signs.
- 1,361 drop because the joined text does not occur whole on another object.

The 25 events cover only **3 distinct junctions in 3 families**, because moulded tablets repeat one text. Allowing damage marks away from the junction gives 26 events, 4 junctions and 4 families. The brief's "60 cases, 29 junctions" does not reproduce under these rules.

**Sites.** Mohenjo-daro 17, Harappa 4, Chanhu-daro 2, Kalibangan 1, Lothal 1. Text lengths run from 4 to 13 signs.
