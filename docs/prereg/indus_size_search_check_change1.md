# Change 1 to the Indus-size search check: cut to the 3 Latin no-anchor cells

Logged 2026-11-20 (UTC) by agent `paper`, on the coordinator's decision.

## Why
- At background priority, the 4 workers got about 30% of an efficiency core each while other projects ran.
- After about an hour, 4 of up to 96 chunks were done, so the full 12-cell check would have taken about 20 hours.
- The decision rule (wording only) depends only on the 3 Latin/Italian cells with 0 anchors.

## What changes
- `step1.py`: `CELLS` becomes the 3 cells ("lat", 0, rep) for rep = 0, 1, 2. The sealed list is kept as `CELLS_SEALED`.
- Nothing else changes: thresholds, seeds, stop rule, labels and decision rule all stay.
- The anchor arms (Latin with 5 and 10 anchors) and Finnish with 10 anchors are not run. They were descriptive only.

## Data seen before the change
Run 1 (stopped) had written:
- 12 truth-climbed keys;
- 4 chunks of 125 restarts:
  - Latin, no anchors: rep 0 at 0.29, rep 1 at 0.45, rep 2 at 0.28;
  - Latin, 5 anchors: rep 0 at 0.38.

In all 4 chunks the best blind objective was below the truth-climbed one. These chunks are kept and count toward their cells; the resumable driver reuses them.

The change cannot favour any outcome. It removes descriptive arms only. The 3 deciding cells keep their sealed seeds and restart budget.
