# Is the fish tick a closer drawn inside the sign? (plan 9, story 3)

Prereg: `docs/prereg/fish_tick_closer.md`. Hashes of the prereg, `ftc.py` and `run.py` were appended to
`docs/prereg/HASHES.txt` at 2026-11-20T21:29:55Z, before any run on real data. All runs went through
`board/run.sh` (one process, background priority). Raw outputs: `out_*.json`. Summary: `results.json`.

## Conclusion

**Verdict by the frozen rule: underpowered.** The test cannot answer the question with the texts we have.

- The known-answer gate failed on every set. A planted merged sign was detected 0% of the time on dev (needed 80%).
- The reason is size. After near-copies are collapsed, "plain fish then closer" occurs only 5 to 13 times per base
  on dev. Planting 30% of those gives 2 to 4 tokens per base. No test can find a match with 2 to 4 tokens.
- So the real results below are not evidence against the hypothesis. They are also not evidence for it.
- For the record, the point estimates lean the wrong way. On dev, ticked-fish contexts were closer to
  "plain fish, no closer" in 3 of 5 bases. The pooled difference was negative on dev and held-out.
- Prediction 2 looked suggestive on dev (20 of 21, p = 0.026, short of 0.01). The red team removed it.
  Its signal came from post-closer texts in the null pool. Dropping them gave p = 0.39.

README #3 (ticked fish move to the closing slot) is untouched. This test asked a narrower question: is the tick
the closer itself? We cannot tell.

## Known-answer gate (run first)

200 plantings per set. In each, 30% of "plain fish + closer" pairs became one new merged sign.
Detection means the frozen rule for that set passed.

| set | texts (families) | planted tokens per base (mean) | P1 detection | P2 detection | P1 false alarm | P2 false alarm |
|---|---|---|---|---|---|---|
| DEV | 971 | 2, 2, 4, 2, 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| HELD (v2) | 505 | 3, 1, 2, 2, 2 | 0.17 | 0.00 | 0.03 | 0.00 |
| NEW (post-1977 ICIT) | 326 | 2, 1, 0, 0, 0 | 0.00 | 0.00 | 0.00 | 0.00 |

Gate needs 0.80. It fails everywhere. No rule was miscalibrated (all false alarms at or below 0.10).

## Prediction 1: contexts before the ticked fish

Delta = JS distance(ticked, plain-no-closer) minus JS distance(ticked, plain+closer). Positive supports the
hypothesis. p is one-sided, from 9,999 label permutations. Counts are tokens: ticked / plain+closer / plain-no-closer.

| base | DEV n | DEV Delta | DEV p | HELD n | HELD Delta | HELD p |
|---|---|---|---|---|---|---|
| M59/60 | 21 / 6 / 76 | -0.28 | 0.97 | 6 / 11 / 44 | -0.30 | 1.00 |
| M65/66 | 7 / 5 / 45 | +0.06 | 0.08 | 5 / 2 / 31 | untestable | |
| M67/68 | 3 / 13 / 43 | +0.01 | 0.45 | 5 / 5 / 22 | -0.11 | 0.85 |
| M70/71 | 3 / 7 / 18 | -0.15 | 0.93 | 3 / 5 / 7 | 0.00 | 1.00 |
| M72/73 | 4 / 10 / 39 | -0.07 | 0.62 | 0 / 6 / 20 | untestable | |

- DEV: 0 of 5 bases pass (rule needs 4 at p < 0.01). Pooled Delta -0.42, p = 0.70.
- HELD: pooled Delta -0.41 over 3 testable bases, p = 0.99.
- NEW: 2 testable bases (W220/226: +0.18, p = 0.06; W235/236: -0.20, p = 1.0). Pooled -0.02, p = 0.35.

## Prediction 2: texts ending in a ticked fish carry no other closer

Single-line complete texts. Null: length-matched texts whose final sign is not a closer or a fish.

| set | ticked-final texts | with no other closer | expected under null | p | closer-final texts with no 2nd closer |
|---|---|---|---|---|---|
| DEV | 21 | 20 (95%) | 16.2 (77%) | 0.026 | 96% |
| HELD | 8 | 6 (75%) | 5.8 (72%) | 0.61 | 96% |
| NEW | 4 | 4 (100%) | 3.4 (85%) | 0.50 | 98% |

DEV needs p < 0.01; it misses. HELD and NEW need p < 0.05; they miss.

## Multiple testing

10 confirmatory tests (5 P1 dev bases, 2 P1 replications, 3 P2). Holm-adjusted: smallest is P2 dev, 0.26.
All others 0.74 to 1. Ledger rows: `ledger_rows.csv`.

## Red team

All alternative nulls agree: nothing is significant anywhere.

| check | DEV p | HELD p | NEW p |
|---|---|---|---|
| P1 R1 length-matched (labels permuted within length bins) | 0.80 | 0.98 | 0.08 |
| P1 R2 within-text shuffle (fish and closers fixed, other signs shuffled) | 1.00 | 1.00 | 0.57 |
| P1 R3 drop text-initial contexts | 0.71 | 1.00 | 0.09 |
| P2 R1' length-matched, post-closer-final texts removed from the pool | 0.39 | 0.83 | 0.62 |
| P2 R2' within-text shuffle | 0.52 | 0.81 | 0.72 |
| P2 R3' plain-fish-final texts as the pool | 1.00 (pool 8) | untestable (pool 3) | 1.00 (pool 5) |

- P1 was never significant, so the "fragile" flag does not apply.
- P2's dev hint does not survive. With post-closer-final texts out of the pool, the null rate rises from 77% to 91%.
  Plain-fish-final texts lack closers just as often (8 of 8) as ticked-fish-final texts.
  So "no other closer" is what any final non-closer sign shows. It does not single out the tick.

## Sensitivity: no near-copy collapse (not used for the verdict)

On all 1,698 distinct dev texts, P1 passes 1 of 5 bases (M65/66, p = 0.0008). Pooled p = 0.36. P2 dev gives
p = 0.0003. Both shrink or vanish once near-copies are collapsed. They come from repeated formulas, the thing the
collapse exists to remove. HELD and NEW are unchanged in substance.

## Hypotheses

| hypothesis | verdict |
|---|---|
| P1: ticked-fish contexts match plain fish + closer | underpowered (gate 0.00 on dev); point estimates lean against |
| P2: ticked-final texts lack other closers beyond a keep-one-closer null | underpowered (gate 0.00); dev hint gone under red team |
| Overall: tick = closer inside the sign | underpowered |

## Limits

- The gate plants 30% of "plain fish + closer" pairs, as the plan fixed. Pairs are rare, so the gate is harsh.
  A gate sized to the real ticked counts (3 to 21 per base) would have more power. It was not preregistered, so not run.
- Family collapse keeps one text per near-copy family. That roughly halves dev (1,698 to 971 texts).
  It is the rule the task asked for. It costs most of the power.
- One left-neighbour sign is the only context used. Longer contexts were not tried.
- W234 = M73 comes from the earlier red team, not from the bridge file.
- Both editions read the same small ticks from the same photographs. Shared reading errors are not checked.

## What would make this testable

More ticked-fish and fish-plus-closer tokens: CISI volume 3, the HARP sheet, or a pooled analysis over all ICIT
sites with a single near-copy rule across M77 and ICIT. Until then this question stays open.

> v2 (2026-11-20): re-run with a non-chaining de-duplication; still underpowered. See `experiments/fish_tick_closer_v2/RESULTS.md`.
