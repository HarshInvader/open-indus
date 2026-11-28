# S4: "six then fish" against a rare-sign-matched null

Contributor: m0x1n (starter task S4). Pre-registration: `docs/prereg/s4_sixfish_rare_null.md`, sha256 `f1880341…`, committed before any null was computed.

## Conclusion

**Survives.** Two-tier six (M109) is followed by plain fish (M59) in 7 of 10 held-out cases. In comparable runs without M109 (same run length, same rare-sign load, same slot position), M59 sits in that slot only 2.8% of the time. The matched null expects 0.28 of 10; p < 1e-5. The new null barely moves the base rate: 2.8%, against the 3.0% global rate used before. Neither the slot's position nor the rare-sign load of the texts explains the pair.

The pair also beats a within-run shuffle of the same signs (7 vs 1.6 expected, p = 2e-5). It holds on dev texts (5 of 15 vs 2.1%) and in ICIT (W016 → W220, 13 of 33 vs 2.8%).

## Results (pre-registered)

Units: break-free runs of distinct M77 texts, split v2. Rare load: tokens of signs seen fewer than 10 times in dev. Strata: (min(L, 9), min(rare load, 3)), with the fallback rule from the prereg. 100,000 replicates.

| Test | Data | M109 → M59 | Null expectation | Null rate | p (raw) | p (Holm, 2) | Verdict |
|---|---|---|---|---|---|---|---|
| **T1 matched slot null** | held-out | **7 of 10** | 0.28 | **2.8%** | < 1e-5 | 2e-5 | **supported** |
| T2 within-run shuffle | held-out, 11 runs with M109 | 7 | 1.61 | | 2e-5 | 2e-5 | supported |
| T3 matched slot null | dev | 5 of 15 | 0.32 | 2.1% | < 1e-5 | | consistent |
| T4 matched slot null | ICIT native (W016 → W220) | 13 of 33 | 0.91 | 2.8% | < 1e-5 | | consistent |

p < 1e-5 is the floor at 100,000 replicates. No slot needed the "any long-enough run" fallback; every one was matched within a (length, rare-load) stratum.

**Planted control (pre-registered).** 20 carrier signs with 12 to 20 held-out slots. In each, the next sign was replaced by M59 at a random 60% of slots:
- Power 1.00: all 20 carriers were flagged at p < 0.05.
- Without planting, 0 of 20 were flagged. 19 carriers never precede M59 at all; M104 does so in 1 of 14 cases and gives p = 0.39.

The test catches a fixed pair of the claimed size at this sample size, and it does not invent one.

## Post hoc (not pre-registered): how strong must a pair be?

The pre-registered plant (60%, 12 to 20 slots) is easy to detect. `posthoc.py` cuts each carrier to exactly 10 slots, the same as M109, and plants weaker pairs:

| Planted rate | Power of T1 | Median p |
|---|---|---|
| 10% | 0.30 | 0.24 |
| 20% | 0.45 | 0.054 |
| 30% | 0.80 | 0.001 |
| 60% | 1.00 | 5e-5 |

At n = 10, the test reliably sees a pair once it occurs about 30% of the time or more. M109 → M59 runs at 70%.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| M109 → M59 is explained by slot position, run length and rare-sign load | **refuted** (T1) |
| M109 → M59 is explained by M59 being common in runs that contain M109 | **refuted** (T2) |
| "Two-tier six + fish is a fixed expression" (README #5), against the stricter null | **survives** |

## Caveats

- **Small n.** 10 held-out slots in 11 runs. The 95% interval for 7/10 is 0.35 to 0.93. Across the whole of M77 the pair occurs in 12 texts from 10 near-copy families at 3 sites (`experiments/redteam/`). The matched null controls slot context; it does not add independent texts.
- **The null uses one sign list.** It is matched within M77. Under `lump_all` the pair weakens to 7 of 32 because numerals and fish are merged (`signlist_robustness`); that issue is separate from this one.
- **ICIT shares objects with M77**, so T4 is a second reading of mostly the same seals, not new data.
- **Meaning.** This supports a fixed pair, nothing about what it means.
- Python 3.13.18, pinned packages. Deterministic; about 1 second to run.

## Files

- `run.py`: pre-registered tests and planted control, giving `results.json`.
- `posthoc.py`: power at n = 10, giving `posthoc.json` (not pre-registered).
- `ledger_rows.csv`: T1 and T2.

```bash
.venv/bin/python -I experiments/s4_sixfish_rare_null/run.py
.venv/bin/python -I experiments/s4_sixfish_rare_null/posthoc.py
```
