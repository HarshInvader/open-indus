# Pre-registration: uniformity paper, referee checks from review 2 (Harappa floor; joint resampling)

Written 2026-11-21 (UTC), before any draw below was scored. Code: `experiments/uniformity_referee_checks/rc.py`.
This file and `rc.py` are hashed in `docs/prereg/HASHES.txt` (tag `uniformity_referee_checks`), and the hash lines are
committed and pushed before the first scoring run. The commit hash and its UTC time, and the UTC time of the first
scored draw, are recorded in `experiments/uniformity_referee_checks/RESULTS.md`. (Review 2's R12: the revision hashes
were made public only after most revision runs. This check is meant not to repeat that.)

Source of the two checks: `docs/paper/uniformity/REVIEW_2.md` C1.3 (Harappa has no within-city floor of its own) and
C3.4 (the Mohenjo-daro texts in the between pool and in the Mohenjo-daro floor are resampled independently although
they are the same texts). Queued as U3 and U4 in `docs/RESEARCH_STATE.md`.

## What has been seen before this file

- Every number in the paper and in `experiments/uniformity_paper/revision/RESULTS.md` (R1: MD–Harappa Δfloor medians
  +0.010 to +0.034, 95% CIs −0.089 to +0.123, m* 0.101–0.107; unicorn m* 0.134–0.143).
- Descriptive counts only, no scoring: Harappa texts by ICIT period/phase field; Harappa M77 seals by Vats-register
  mound (`experiments/reg_harappa/findspots.csv`); pool sizes from `rc.py sizes`:
  - Harappa M77 seals after `clean()`, labelled by mound: mound F 114, other mounds (AB, D, G, H, J) 59.
    F against AB only: 115 / 44. ICIT seal records linked to a register mound: 14 of 197 (seals), 18 of 262
    (seals + sealings), so ICIT has no usable locus split. HARP period labels (3B, 3C) cover 18–27 ICIT texts.
  - Harappa random halves after `clean()`: M77 seals 119 / 119; ICIT seals 102 / 92; ICIT seals + sealings 135 / 122.
  - Shared MD texts: of the MD ids in the between pool and in the MD random-halves floor, 817 / 735 / 851 are in both
    (M77 seals / ICIT seals / ICIT seals + sealings), with 13–25 in only one of them.
- No AUC for any Harappa split, any matched-size MD–Harappa draw below n 145, or any joint replicate has been computed.

## Frozen pipeline

Unchanged from step 2 and the revision: pools from `s2.indus_raw` / `s2.indus_between` / `s2.indus_within`;
`ub.clean()` (drop strings found on both sides; non-chaining greedy de-dup, `fish_tick_closer_v2/dedup.py`);
`ub.draw_n()` with the step-2 length mix and n per side; `ub.score()` (Bernoulli NB, pooled out-of-fold AUC, grouped
CV, plus one shuffled-label AUC). Δ per replicate = median(between draws) − median(floor draws), as `revision/report.py r1`.
m* = max(|q5|, |q95|) of the bootstrap Δ (the paper's "one-sided 95% upper limit"). Seed 20261122. Margin 0.05.

## (a) Harappa within-city floor

**Split (fixed now).**
- Primary: M77 seals, Harappa mound F against the other mounds (AB, D, G, H, J), labels from the Vats register
  (`findspots.csv`; a text whose register rows give both F and another mound, or a blank mound, is left out).
  Minimum n per side: 40. With 59 on the smaller side, the matched n is 59, and the primary row runs at n = 59.
  (Had it been under 40, the primary would have been Harappa random halves.)
- Secondary (ICIT has no locus field): Harappa random halves (`s2.half(id)`) in all three families: M77 seals (n 119),
  ICIT seals (n 92), ICIT seals + sealings (n 122).
- n per row = min(smaller between side, smaller floor side, 227). The MD–Harappa between pool is drawn at that same n
  and length mix, so between and floor are size-matched. For context only, the MD random-halves floor is also drawn at
  that n.

**Point estimate and power (50 draws each, no bootstrap).** Between, Harappa floor, MD floor at the same n, and a power
gate: the step-2 local stock (20 common signs, `s2.plant_side`) on the Harappa side at q = 0.15; power = share of
planted draws with AUC − median Harappa floor ≥ 0.05; gate 80%.

**Bootstrap (same as the existing floors).** 200 replicates; each resamples texts with replacement within each side
of the between pool and, independently, of the Harappa floor pool; 5 between + 5 floor draws per replicate
(mode `indep`). Also reported, secondary: mode `joint`, where Harappa texts are resampled once per replicate and
shared by the between pool and the floor.

**Rules (fixed now; not to be loosened).**
- Primary verdict, on the M77 mound row, `indep` bootstrap:
  - UNDERPOWERED if the power gate < 80%. The paper then says the Harappa floor is underpowered at n 59.
  - WITHIN the Harappa floor if the 2.5th percentile of Δ_H ≤ 0 (interval includes zero).
  - BEYOND the Harappa floor if the 2.5th percentile of Δ_H > 0. The paper then says the MD–Harappa gap exceeds
    Harappa's own floor, and the headline "no detectable place signal beyond a within-city floor" is qualified to
    "beyond Mohenjo-daro's floors but not Harappa's".
- Secondary rows (Harappa random halves): same WITHIN / BEYOND rule per row. Any BEYOND row is reported in the paper
  as a weakening, whatever the primary verdict.
- m* and q95 are reported for every row; TOST at ±0.05 as in R1.
- "Harappa floor lower than the MD floor at the same n" is descriptive only (point medians).

## (b) Joint resampling of the shared Mohenjo-daro texts

**Pools.** The three headline pools (M77 seals n 200, ICIT seals n 172, ICIT seals + sealings n 227) against the MD
random-halves floor, and the two unicorn pools (n 145), at the R1 sizes.

**Resampling.** Mode `joint`: per replicate, MD ids (union of the between pool's MD side and the floor pool) are
resampled once with replacement; that one resample gives the MD side of the between pool and both floor halves (each
text keeps its fixed half label and its group). Harappa is resampled on its own. 200 replicates, 20 between + 20 floor
draws per replicate (R1 used 5 + 5). Mode `indep20` (secondary): the R1 independent resample at 20 + 20 draws, to
separate the effect of jointness from the effect of more draws.

**Rules (fixed now; not to be loosened).**
- "Every interval includes zero" SURVIVES if the `joint` 2.5th percentile of Δ is ≤ 0 in all three headline pools.
  It FAILS if any headline pool has a 2.5th percentile > 0; the paper then reports that pool as beyond the floor.
- Upper limit: max m* over the three headline `joint` pools. "About 0.11 holds" if 0.095 ≤ max m* ≤ 0.115;
  "tighter" if < 0.095; "wider" if > 0.115. In every case the paper reports the joint number as the upper limit
  (replacing 0.101–0.107), with the range over the three pools.
- TOST at ±0.05 per pool as in R1; if a pool passes, the paper may say equivalence at ±0.05 holds for that pool only.
- Unicorn pools: same rules, reported separately; they do not enter the headline verdict.
- Secondary arithmetic, no new runs: the R10 contrast recomputed with the joint Indus replicates paired by replicate
  index with the R1 `REF_ur3_U_reign` replicates (independent streams); same rules as `uniformity_paper_contrast.md`.

## Red team (exploratory, specified now, run after the confirmatory jobs)

Results are reported whatever they show; they do not change the verdicts above, but any red-team row that reverses a
verdict is stated in the paper's limitations.
1. Seed: the primary (a) row (point + 100 bootstrap replicates) and the (b) joint M77 seals and ICIT seals + sealings
   pools (100 replicates) rerun with a shifted seed.
2. Split choice: mound F against mound AB only (n 44), point + 100 replicates.
3. Near-copies: on the primary (a) row, drop both members of every cross-side near-copy pair (`dedup.near`,
   ≥ 4 signs, within one edit or contained) in the between pool and in the Harappa floor, using
   `experiments/fish_tick_closer_v2/dedup.py` only; point + 100 replicates.

## Compute

`board/run.sh` (taskpolicy -b, nice 20) under `open-citizen-science/.local/compute.lock.indus`, one process, one
worker, `.venv/bin/python -I`, `timeout -s INT 85m` per chunk; jobs resume from their `draws_*.jsonl` by
(condition, replicate). Job order: hpoint, hboot, joint, indep20, rt, rtboot.

## Deviations

Any change to `rc.py` after hashing (bug fix) is logged in RESULTS.md with the diff, a new hash line
(tag `uniformity_referee_checks_fix<k>`), and a statement of which draws, if any, were rerun.
