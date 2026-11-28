# S3: the ticked-fish finding, re-implemented from its description alone

Contributor: m0x1n (starter task S3). Pre-registration: `docs/prereg/s3_ticked_fish_reimpl.md`, sha256 `1587d767…`, committed before the code was written. I wrote `run.py` from README #3, the rules of evidence and the corpus docstrings. I had not opened the original team's code or results.

## Conclusion

**The finding reproduces.** On complete single-line held-out texts, corner-ticked fish (M60, M66, M68, M71, M73) end the text **9 times out of 16, against 4.15 expected from text length (p = 0.007)**. Plain fish (M59, M65, M67, M70, M72) end it in 2% of cases. That is the reported "9 of 16 vs 2%, p = 0.006", reached independently. Every pre-registered test passes after Holm correction. The effect is as strong on dev texts and in the separate ICIT corpus. It also shows, on few tokens, at sites that are not in M77 at all.

Two of the three reported numbers I matched exactly or almost exactly. For the third (ICIT "40 of 73") I got the same rate but not the same count. The differences are explained below.

## Results (pre-registered)

Clean text: `complete`, one line, no break. Final: last sign in reading order. Split v2, distinct texts. Plain-fish share is the comparison group; the length-matched expectation is the sum of 1/L over ticked tokens.

| Test | Data | Ticked final | Plain final | Null | p (raw) | p (Holm, 4) | Verdict |
|---|---|---|---|---|---|---|---|
| T1 Fisher, ticked vs plain | held-out, 412 clean texts | 10 / 17 (0.59) | 3 / 142 (0.02) | | 2.3e-9 | 9.1e-9 | supported |
| T2 length-matched (one-sign texts excluded) | held-out | **9 / 16 (0.56)** | | 4.15 expected (0.26) | **0.0072** | 0.0072 | supported |
| T3 within-text shuffle (100,000) | held-out, 124 texts with a fish | difference 0.567 | | null mean 0.092 | 3.0e-5 | 6.0e-5 | supported |
| T5 length-matched, ICIT native | 2,075 clean texts | 35 / 59 (0.59) | 21 / 716 (0.03) | 15.0 expected (0.25) | 1.4e-8 | 4.3e-8 | supported |
| T4 (descriptive) dev | 1,246 clean texts | 23 / 33 (0.70); 22 / 32 excluding one-sign texts | 11 / 538 (0.02) | 8.6 expected | 5.2e-7 | | consistent |
| T5b (descriptive) ICIT sites not in M77 | 176 clean texts | 5 / 7 (0.71) | 6 / 40 (0.15) | 1.9 expected | 0.014 | | consistent, few tokens |

T5b comes from 6 sites: Bala-kot, Banawali, Bhirrana, Gola Dhoro, Nausharo and Rupar. Per sign on held-out (final/tokens): M60 2/3, M66 1/5, M68 3/5, M71 4/4, M73 0/0. The effect is not carried by one sign, although M66 is weak.

**Planted control.** Fish tokens in the clean held-out texts were relabelled into a fake "ticked" class of 17 tokens, 2,000 times:
- Uniform relabelling (no real effect): T1 passed 3.0% of the time, T3 2.0% (200 replicates), at α = 0.05. The tests do not over-fire.
- Final-weighted relabelling (expected 50% final): T1 passed 99%, T3 95.5%. At this sample size the tests detect an effect of the size claimed.

Both meet the pre-registered bars (≤ 10% and ≥ 50%).

## My numbers next to the reported ones

I read the original results only after `run.py` had run. The comparison is in `posthoc.py` / `posthoc.json`. It is **post hoc**: definition variants tried only to explain differences, not new tests.

| Reported | Mine | Explained? |
|---|---|---|
| (a) complete single-line held-out: 9 of 16 vs 2%, p = 0.006 (`audit_followups` C, 415 texts) | 9 of 16 vs 2%, p = 0.0072 (412 texts) | **Yes, matches.** The 16 tokens exclude one one-sign text. My T1 counts it, giving 10 of 17. The small difference in p fits a different null: theirs is "frequency-matched" (null mean 0.17), mine is exact length-matched (null mean 0.26). The 3 extra texts in their 415 are unexplained. |
| (b) "clean held-out" 11 of 19 vs 7%, p = 0.004 | 11 of 19 vs 8.4%, p = 0.0018 | **Mostly.** The original row is "M77 type, original, 571 texts", meaning all held-out texts, not only complete ones. Counting the end of every break-free run as final, I get 11 of 19, the same count. Plain fish give 16 of 191 (8.4%) against their 7%. With the 12-sign plain list in `ledger/v2_reruns.py` it is 17 of 198 (8.6%). **The plain-fish share is not explained.** README calls this set "clean held-out", but it includes texts with breaks and line ends. That is the very confound the complete single-line rerun removed, so the README wording is misleading. |
| (c) ICIT native 40 of 73 vs 26% expected, p = 1e-7 | 35 of 59 (0.59) vs 25% expected, p = 1.4e-8 | **Partly.** The original team maps M73 to W234; `bridge_WM.json` has no W number for M73. Adding W234 gives 37 of 63 on clean texts and 46 of 80 over all break-free segments. The expected rate (0.26) and the final share (0.55 to 0.59) match. **The exact count 40 of 73 was not reproduced.** It probably uses a different unit (segments vs texts, or object-level vs distinct). |
| "New sites only: 5/10, p = 0.07" (redteam) | 5 of 7, p = 0.014 (5 of 8 with W234, p = 0.025) | Not explained. A different site list or definition of "new site" is likely. |

## Caveats

- **Small sample.** 16 or 17 held-out tokens, and 13 of the original 16 are from Mohenjo-daro (README). The effect is large, but its size is uncertain: the 95% Clopper-Pearson interval for 9/16 is 0.30 to 0.80.
- **"Final" is not "closing slot".** I tested last sign of the text. Whether a ticked fish closes a phrase inside longer texts was not tested.
- **The sign list is one editor's.** Under ICIT readings the effect holds (T5), but both corpora share photographs.
- **Python 3.13.18**, packages at the pinned versions (the pin says 3.15). Deterministic: re-running gives identical `results.json`.
- Ledger: `ledger_rows.csv` adds the four Holm-family tests (T1, T2, T3, T5) as mode `red-team`, family `s3:tick`, size 4. They are an independent replication of existing rows, so the lead may prefer to mark them that way rather than count them as new tests.

## Files

- `run.py`: pre-registered tests T1 to T5b and the planted control, giving `results.json`. About 3 seconds.
- `posthoc.py`: definition variants, written after reading the original results, giving `posthoc.json`.
- `ledger_rows.csv`: four rows in the ledger's column format.

```bash
.venv/bin/python -I experiments/s3_ticked_fish_reimpl/run.py
.venv/bin/python -I experiments/s3_ticked_fish_reimpl/posthoc.py
```
