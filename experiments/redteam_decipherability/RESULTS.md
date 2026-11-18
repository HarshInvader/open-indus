# Red team of the decipherability result (board #46): results

Prereg `docs/prereg/redteam_decipherability.md` (sha256 cb9a4422..., hashed 2026-11-18T20:47:50Z). Code `rt.py` (9b50a1fd..., hashed 21:09:29Z), written by an agent that did not write `experiments/decipherability` and did not read its code. Verdicts: `summarise.py` applies the sealed rules to `out/runs.jsonl` (78 runs) and writes `out/verdicts.json`.

**Date error in the prereg.** The text says "Written 2026-11-19". It was written on 2026-11-18. The hash line timestamp (20:47:50Z) is the true time.

## Verdicts

| Claim | Sealed rule | Result | Verdict |
|---|---|---|---|
| Gate | K0, 10k, q=0 ≥ 0.70 | 0.9997 | passes |
| C1 a true-language model recovers values at about 10k tokens | ≥ 0.70 (q=0), ≥ 0.60 (q=0.2) | 0.9997 / 0.990 | **SURVIVES** |
| C2 a related-language model gives low, flat recovery | every cell ≤ 0.35; rise ≤ 0.15 | cells 0.071-0.116; rise −0.017 | **SURVIVES** |
| C3 under a related model, wrong keys outscore the true key | ≥ 80% of runs | 72% (26/36): 100% at 2.5k, 67% at 10k, 50% at 30k | **WEAKENED** |
| C4 even a wrong language beats a shuffle hugely | z > 5 every replicate | z 16.3-90.9 (6/6) | **SURVIVES** |

For C3 we read "direction holds" as "more than half of runs". The prereg does not define it more exactly.

## What is new: the related-language objective points roughly the right way

The original result said the objective under a related-language model prefers wrong keys. That would mean more compute cannot help. The red team finds something more useful.

| Pair | Tokens | Blind accuracy | Climb from true key: accuracy | Climb ends above true key | Best blind key above true key |
|---|---|---|---|---|---|
| Latin / Italian model | 2.5k | 0.119 | 0.770 | 6/6 | 6/6 |
| | 10k | 0.131 | 0.792 | 6/6 | 2/6 |
| | 30k | 0.122 | 0.825 | 6/6 | **0/6** |
| Finnish / Estonian model | 2.5k | 0.085 | 0.686 | 6/6 | 6/6 |
| | 10k | 0.088 | 0.695 | 6/6 | 6/6 |
| | 30k | 0.042 | 0.662 | 6/6 | 6/6 |

- In all 36 related-model runs, a greedy climb starting from the true key ends at a key that scores higher and is still 66-83% right. The objective's high ground near the truth is mostly correct keys.
- For Latin with an Italian model, at 30k tokens the true key outscores every wrong key that blind search found. At this size the failure is in the search, not in the objective.
- For Finnish with an Estonian model, wrong keys still win at 30k. The closer the related language, the sooner the objective turns.
- Blind search stays at 4-13% in every cell. Random restarts never reach the mostly-right region.

**Implication.** With a related language, a search that is put near the right answer would likely end 66-83% right. Anchors are a way to do that: a few sign values fixed from names or bilingual evidence. This explains the original anchor result (0.17 -> 0.47-0.68) and suggests that it is about getting the search into the right basin, not only about adding information. It also gives a concrete next test: how many anchors does it take for a blind search under a related model to reach the climb's 66-83%? That must be pre-registered before it is run.

## Limits

- Two Latin-script language pairs only; sizes up to 30k tokens (Indus has about 10k). Bigram models only.
- The decipherer is told which signs are logograms, which favours the decipherer.
- C4 used three shuffles per replicate, so the z values are rough. All are far above 5.

## Files

- `rt.py`: the reimplementation.
- `summarise.py`: applies the sealed rules.
- `out/runs.jsonl`: one line per run.
- `out/verdicts.json`: the verdicts.
- `ledger_rows.csv`: ledger rows.
