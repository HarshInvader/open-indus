# Pre-registration: fish_tick_closer_v2 (second attempt, new de-duplication unit)

Written 2026-11-21 (UTC), before any v2 statistic, text count or gate figure was computed. Frozen with
`experiments/fish_tick_closer_v2/dedup.py` and `run_v2.py`, and the v1 files they import
(`experiments/fish_tick_closer/ftc.py`, `run.py`, unchanged). sha256 of all five appended to
`docs/prereg/HASHES.txt` with a UTC timestamp before the first run.

## Why a v2, and what has been seen

This is a second attempt after a diagnosed artefact. v1 (`docs/prereg/fish_tick_closer.md`) ended
"underpowered": the known-answer gate detected 0% (dev), 17% (held) and 0% (new sites) of planted merges.
`experiments/parpola_rules34/RESULTS.md` then showed that v1's near-copy collapse is degenerate. It runs
union-find over `corpus/build.py::_close`, where a text of 3+ signs is linked to every longer text that
contains it. Chaining puts 571 of 1,698 dev texts in one family, and only one text per family was kept.
That rule is right for keeping families on one side of a split. As a unit of analysis it removes recurring
formulas and most of the data. It probably caused the gate failure.

**Seen before writing this:** all v1 numbers on DEV, HELD and NEW (gate, P1, P2, red team, and the
no-collapse sensitivity run, which gave P1 M65/66 p = 0.0008 and P2 dev p = 0.0003 on all distinct dev texts).
The parpola_rules34 post hoc greedy de-dup numbers for rules 3 and 4 (not fish-tick statistics). No fish-tick
statistic has been computed under the v2 unit. v1's verdict stands as recorded and is not replaced by v2.

## The new unit (frozen in `dedup.py`)

Within each set separately:
1. Exact distinct texts (`corpus/load.py::distinct`).
2. Texts with the same sign string once `|` and `#` are removed count as one (the first in the order below kept).
3. Greedy pass, longest first (ties: lexicographically first sequence string). A text is DROPPED only if it
   has 4 or more signs AND it is within one edit (one substitution, insertion or deletion) of, or a contiguous
   part of, a text ALREADY KEPT. There is no chaining: a dropped text never causes another text to be dropped.
   Texts of 1-3 signs are never dropped by this step.

Reference: `experiments/parpola_rules34/posthoc.py::greedy`. Difference: posthoc used `_close`, which also
drops 3-sign texts contained in a kept text; v2 requires 4+ signs for every drop, as the task specifies.

Reported descriptively (stage `counts`, not a test): texts kept per set under v1 collapse and v2, and the
largest family (v1: union-find family; v2: kept text plus everything dropped onto it).

## Sets, signs, tests: identical to v1

- DEV / HELD: `dev_heldout(version=2)`. NEW: distinct ICIT texts from the 14 post-1977 sites listed in v1.
- Fish pairs, Wells pairs, closer set C, post-closer set: as v1 (constants in `ftc.py`).
- Texts are flattened over `|` with `ftc.prep`, as v1.
- **P1** (left contexts; Delta_b = JSdist(A,D) - JSdist(A,B); 9,999 label permutations; testable if all
  groups >= 3). DEV bar: Delta_b > 0 with p < 0.01 in >= 4 of 5 bases. HELD and NEW bar: pooled Delta_sum,
  base-stratified permutation, one-sided p < 0.05.
- **P2** (ticked-final single-line complete texts carry no other closer; length-matched keep-one-closer
  Bernoulli null, 100,000 draws, bins 2..7+, merge bins below 5 reference texts). Bars: DEV p < 0.01,
  HELD p < 0.05, NEW p < 0.05.
- **Known-answer gate**: 200 seeded plantings per set, 30% of "plain fish + closer" pairs merged into a new
  sign X_b; P1 with 999 permutations, P2 with 10,000 draws; detection = the set's bar passes; gate passes at
  detection >= 0.80; false-alarm control (random plain-fish tokens) > 0.10 marks a rule miscalibrated and its
  real result invalid. Seeds as v1 (gate 5200+i, real 7700+i, red team 9100+i).
- Code: v1's `gate`, `real`, `redteam`, `p1`, `p2`, `plant` are imported unchanged. Only the unit differs.

## Order and stop rule

1. `counts`. 2. `gate` on DEV, HELD, NEW.
3. **Stop rule:** if the DEV gate fails (< 0.80) for BOTH P1 and P2, the verdict is "underpowered", and no real
   test or red team is run. Otherwise run `real` (DEV, HELD, NEW) and then `redteam`.

## Confirmation sets

v1's held-out set has already been seen, and so have v1's NEW numbers, though under the old unit. Neither is
clean. NEW (ICIT post-1977 sites; a different edition and different sites from the M77 dev data) is the
**primary confirmation set**: v1 saw only its collapsed version, and the dev/held split never touched it.
v2 DEV and HELD are **secondary**.

## Verdict rule (frozen), per prediction, then overall = the weaker

- **Supported**: gate passes on DEV and NEW; DEV bar passes; NEW bar passes.
- **Refuted**: gate passes on DEV and NEW; DEV and NEW both fail.
- **Not replicated**: DEV passes; NEW fails with a passing NEW gate.
- **Mixed / inconclusive**: DEV fails with a passing DEV gate, NEW passes.
- **Dev-only**: NEW gate fails; then DEV pass = "dev-only, unconfirmed"; DEV fail with passing DEV gate =
  "refuted on dev, primary set underpowered".
- **Underpowered**: DEV gate fails for that prediction.
- Order: supported > dev-only > mixed > not replicated > refuted on dev > refuted; underpowered is reported
  as such.
- HELD (secondary): reported. A HELD failure with a passing HELD gate is stated as a caveat next to the verdict.
- Fragile flag (as v1): if on DEV the pooled P1 result loses significance (p >= 0.05) under the length-matched
  null (R1) or the within-text shuffle (R2), "fragile" is written next to the P1 verdict. For P2 the same
  applies with R1' (post-closer texts out of the pool) and R2' (within-text shuffle).

## Kill condition

The hypothesis "tick = closer inside the sign" is killed at our data size if, with passing gates, either:
- P1: DEV has fewer than 4 of 5 bases passing AND the NEW pooled p >= 0.05; or
- P2: DEV p >= 0.01 AND NEW p >= 0.05.
A killed hypothesis goes to `docs/NEGATIVE_ATLAS.md` (via the lead) and is not re-tested on these corpora
without new texts (CISI 3, HARP).

## Multiple testing

v1 ran 10 confirmatory tests. v2 runs another 10 (5 P1 DEV bases, P1 pooled HELD and NEW, P2 DEV, HELD, NEW).
The correction counts **20 effective tests** (v1 included, since v2 is a second look at the same question).
Holm-adjusted p over the 20 (v1's 10 recorded p-values plus v2's 10) are reported. The bars above stay as frozen;
if a "supported" verdict's NEW p does not survive Holm over 20 at 0.05, it is written "supported, not
Holm-robust over 20 tests". Gate, counts and red-team checks are robustness checks, not used to rescue a rule.

## What would falsify

A passing gate with a DEV and NEW failure of either prediction (the kill condition). A ticked-fish context that
matches "plain fish, no closer" as well as or better than "plain fish then closer" in most bases.

## Compute

All stages through `board/run.sh .venv/bin/python -I ...`, single process, background priority.
