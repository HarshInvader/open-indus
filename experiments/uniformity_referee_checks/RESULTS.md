# Uniformity paper: referee checks from review 2 (Harappa floor; joint resampling), results

Prereg `docs/prereg/uniformity_referee_checks.md`, hashed with `rc.py` in `docs/prereg/HASHES.txt` (tag
`uniformity_referee_checks`, 2026-11-21T22:54:55Z). **Committed and pushed as `400f20b` at 2026-11-21T22:55:08Z
(push done by 22:55:12Z). The first scored draw began at 22:55:39Z** (chunk `hpoint`; timeline under Files). No draw was scored
before the commit; the only earlier work was the descriptive counts the prereg lists. `rc.py` is unchanged since
hashing. Every number below comes from `results.json` (`rc.py report`).

## Verdicts in plain English

1. **(a) Harappa floor, primary (M77 seals, mound F against the other mounds, n 59 per side): UNDERPOWERED.**
   Power to detect a 20-sign stock on 15% of Harappa tokens is 38% (gate 80%). The gap is Δ_H −0.019, with a
   bootstrap 95% CI of −0.185 to +0.143. The interval includes zero, but at n 59 this floor cannot decide anything.
2. **(a) Harappa random halves, secondary: no row is beyond Harappa's own floor.** All three intervals include zero.
   M77 seals (n 119): Δ_H +0.031, CI −0.097 to +0.160, power 96%. ICIT seals + sealings (n 122): +0.014, CI −0.109
   to +0.163, power 94%. ICIT seals (n 92): −0.037, CI −0.177 to +0.124, underpowered (26%; its Harappa floor is high,
   0.585). **Weakening:** against Harappa's own floor the one-sided upper limit is 0.14 in the two powered rows, not
   0.11. These rows run at half the size of the headline pools, so part of the widening is size.
3. **(b) Joint resampling: "every interval includes zero" survives.** M77 seals +0.018 (CI −0.062, +0.091);
   ICIT seals −0.003 (−0.080, +0.088); ICIT seals + sealings +0.039 (−0.031, +0.111). **Upper limit m* 0.089 /
   0.077 / 0.102; max 0.102, so "about 0.11 holds"** by the pre-registered rule (0.095–0.115). The paper reports
   0.08–0.10 as the joint range. No pool passes TOST at ±0.05.
4. **Jointness changes little; more draws do most of the narrowing.** The independent resample at the same 20 + 20
   draws gives m* 0.089 / 0.084 / 0.089 and the same zero-inclusion. Review 2 expected the joint resample to narrow
   the interval through the b–w correlation; with 13–25 of about 850 MD texts outside the overlap, that correlation
   barely moves the interval.
5. **Unicorn seals (joint): no difference beyond the floor;** +0.050 (CI −0.037, +0.137) and +0.048 (−0.080,
   +0.128); m* 0.123 / 0.121 (R1: 0.143 / 0.134).
6. **Ur III minus Indus contrast with joint Indus replicates (secondary):** median +0.15 / +0.18 / +0.13; every
   2.5th percentile above zero (lowest +0.037), and every 5th percentile at or above 0.05 (lowest +0.053). In R10,
   M77 seals missed the margin by 0.001; with joint replicates all three pools meet it.

## Deviation (no code change)

The secondary `joint` mode of (a) is not usable. In that mode the union of Harappa ids (between ∪ floor) is resampled
once, and the floor takes only the picked ids that carry a floor label. The floor therefore keeps fewer texts than its
original size, and one side often falls below the matched n, so `draw_n` returns nothing. Usable replicates: mound 108
of 200; M77 halves 11; ICIT seals 87; ICIT seals + sealings 104 (red team 53–64 of 100). The surviving replicates
are a selected subset. They are listed in the tables for completeness but are not interpreted. The primary (a) mode
(`indep`) and all of (b) have their full replicates. In (b) the MD floor is large (about 420 per side against n ≤ 227),
so the same shrinkage never empties a draw. The bug was found after the runs. It was not fixed and rerun, because
the row is secondary and the prereg's verdicts do not use it.

## Red team (exploratory, as pre-registered)

| Attempt | Row | n | Δ_H or Δ | 95% CI | m* | Power | Changes a verdict? |
|---|---|---|---|---|---|---|---|
| Seed shift (+1) | (a) mound, point + 100 reps | 59 | −0.001 (point −0.026) | −0.168, +0.136 | 0.160 | 56% | no (still underpowered; includes zero) |
| Split choice: F vs AB only | (a) | 44 | −0.051 (point −0.024) | −0.215, +0.106 | 0.202 | 40% | no |
| Near-copy removal (`dedup.near`, both members) | (a) mound | 59 | −0.028 (point −0.040) | −0.172, +0.140 | 0.146 | 40% | no; see note |
| Seed shift (+1) | (b) joint M77 seals, 100 reps | 200 | +0.024 | −0.060, +0.109 | 0.105 | | no; m* moves 0.089 → 0.105 |
| Seed shift (+1) | (b) joint ICIT seals + sealings | 227 | +0.034 | −0.041, +0.109 | 0.101 | | no |

Notes. (i) Near-copy removal dropped **zero** texts from both the between pool (842 / 200) and the mound floor
(114 / 59): `clean()` already runs the same non-chaining greedy de-dup over each pooled pair, so no cross-side
near-copy survives it. That row differs from the primary only by its random stream, so it is a third seed, not a
de-dup test. (ii) Power on the mound split is 38–56% across seeds: the "underpowered" verdict is stable, and so is
"interval includes zero". (iii) Seed moves the joint upper limit by up to 0.016 (M77: 0.089 vs 0.105). So the
upper limit is best stated as 0.08–0.11 across seeds, which is still "about 0.1". The paper gives the primary-seed
range 0.08–0.10 and notes the seed spread.

## Tables

### (a) Harappa floor, point estimates (50 draws each; Δ = median between − median floor)

| Row | n | floor sides | between | Harappa floor | MD floor same n | Δ_H | Δ_MD same n | power q 0.15 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| M77 seals, mound F vs others (primary) | 59 | 114 / 59 | 0.492 | 0.539 | 0.511 | −0.047 | −0.019 | 0.38 | underpowered |
| M77 seals, HA halves | 119 | 119 / 119 | 0.486 | 0.473 | 0.523 | +0.013 | −0.037 | 0.96 | not beyond |
| ICIT seals, HA halves | 92 | 102 / 92 | 0.516 | 0.585 | 0.510 | −0.069 | +0.006 | 0.26 | underpowered |
| ICIT seals + sealings, HA halves | 122 | 135 / 122 | 0.542 | 0.516 | 0.505 | +0.027 | +0.038 | 0.94 | not beyond |

### (a) Harappa floor, bootstrap (200 replicates, 5 + 5 draws, `indep` = as R1)

| Row | n | median Δ_H | 95% CI | q5 / q95 | m* | TOST | interval includes 0 |
|---|---|---|---|---|---|---|---|
| M77 mound (primary) | 59 | −0.019 | −0.185, +0.143 | −0.165 / +0.117 | 0.165 | no | yes |
| M77 HA halves | 119 | +0.031 | −0.097, +0.160 | −0.073 / +0.140 | 0.140 | no | yes |
| ICIT seals HA halves | 92 | −0.037 | −0.177, +0.124 | −0.168 / +0.102 | 0.168 | no | yes |
| ICIT seals + sealings HA halves | 122 | +0.014 | −0.109, +0.163 | −0.086 / +0.140 | 0.140 | no | yes |
| (joint, not interpreted) mound / M77 / ICIT / ICIT+ | | −0.035 / +0.052 / −0.041 / +0.020 | | | | | 108 / 11 / 87 / 104 reps |

### (b) MD–Harappa against the MD random-halves floor (200 replicates, 20 + 20 draws)

| Pool | n | joint median | joint 95% CI | joint q5 / q95 | joint m* | indep20 median | indep20 95% CI | indep20 m* | R1 (5 + 5) m* |
|---|---|---|---|---|---|---|---|---|---|
| M77 seals | 200 | +0.018 | −0.062, +0.091 | −0.048 / +0.089 | 0.089 | +0.018 | −0.062, +0.101 | 0.089 | 0.101 |
| ICIT seals | 172 | −0.003 | −0.080, +0.088 | −0.072 / +0.077 | 0.077 | +0.006 | −0.090, +0.092 | 0.084 | 0.102 |
| ICIT seals + sealings | 227 | +0.039 | −0.031, +0.111 | −0.024 / +0.102 | 0.102 | +0.037 | −0.035, +0.098 | 0.089 | 0.107 |
| Unicorn, ICIT seals | 145 | +0.050 | −0.037, +0.137 | −0.026 / +0.123 | 0.123 | +0.041 | −0.051, +0.140 | 0.128 | 0.143 |
| Unicorn, seals + sealings | 145 | +0.048 | −0.080, +0.128 | −0.047 / +0.121 | 0.121 | +0.039 | −0.051, +0.156 | 0.132 | 0.134 |

### (b) secondary: Ur III (ORACC Umma reigns, R1 replicates) minus Indus (joint), paired by replicate

| Indus pool | median D | 95% CI | 5th pct | above 0 | above margin |
|---|---|---|---|---|---|
| M77 seals | +0.152 | +0.063, +0.246 | +0.072 | yes | yes |
| ICIT seals | +0.176 | +0.072, +0.286 | +0.089 | yes | yes |
| ICIT seals + sealings | +0.133 | +0.037, +0.238 | +0.053 | yes | yes |

## Sentences safe for the paper

- "Resampling the shared Mohenjo-daro texts jointly, with 20 draws per replicate, leaves every interval including
  zero (M77 −0.062 to +0.091; ICIT seals −0.080 to +0.088; with sealings −0.031 to +0.111); the one-sided 95% upper
  limit is 0.08–0.10 AUC (0.10–0.11 under a second seed). An independent resample at the same draw count gives
  nearly the same limits, so the gain over R1 comes from more draws, not from the shared texts."
- "Against Harappa's own floor, the gap is not beyond it in any split, but the floor is weaker: the mound split
  (F against the other mounds, n 59) is underpowered (power 38–56%), and random halves of Harappa (n 92–122) give
  upper limits of 0.14 where powered."

Not safe: "the Harappa floor confirms the tie" (it is underpowered on the mound split); "joint resampling narrows the
interval" (more draws do); "the upper limit is 0.08".

## Files

Chunk timeline (from the local `run.log`, which `.gitignore` keeps out of the repo, as for earlier runs):
hpoint 22:55:39Z–22:57:24Z; hboot 22:57:32Z–23:25:31Z; joint 23:25:42Z–00:24:12Z; indep20 00:24:23Z–01:44:01Z;
rt 01:44:14Z–01:45:06Z; rtboot 01:45:06Z–02:02:26Z (2026-11-21/22 UTC). All exit 0.

`rc.py` (analysis), `chunk.sh` (lock + timeout wrapper), `draws_hpoint.jsonl`, `draws_hboot.jsonl`,
`draws_joint.jsonl`, `draws_indep20.jsonl`, `draws_rt.jsonl`, `draws_rtboot.jsonl`, `results.json`, `ledger_rows.csv`.
Compute: one process at a time, `board/run.sh` (taskpolicy -b, nice 20) under `compute.lock.indus`, `timeout 85m` per
chunk; six chunks, 22:55Z–02:02Z, none hit the timeout. The `compute.lock.mind` of another project was left alone.
