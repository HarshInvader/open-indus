# meaning_calibration v2: the same calibration with a resolution gate (sealed before the v2 kill test)

Agent `paper`. Main line (a). Follows v1 (`meaning_calibration.md`), whose kill test FAILED on 2026-11-24 (planted power 0.455; `experiments/meaning_calibration/RESULTS.md`).
- The v1 failure stays in the ledger and in the test count.
- v2 follows Fable's advice of 2026-11-24. The change is to the test's domain, not its statistic.

## Disclosure
- In v1, every planted head whose null had at least 99 pseudo-partner sets survived (71 of 71). The v2 kill test is therefore expected to pass and is **confirmatory only**.
- The informative part is the claims stage (false-refutation bound and AUC). It is unchanged from v1.

## Unchanged from v1
- Corpus, tokeniser (`load.py`) and draw sizes (1,680 + 565).
- Form F statistic and null (`fcore.f_test`, the `p34.rule4` path).
- Eligibility: at least 10 dev and at least 3 held-out next-tokens.
- Thresholds: share ≥ 0.4, dev p ≤ 0.01, held-out p ≤ 0.05.
- Majority over 5 draws.
- Claim writing (A: 30 claims; decoys; B on opaque IDs; chance baseline).
- Main measures, bars and verdicts.

## Changes
1. **Seeds:** 20261125 + k, for k = 0..4.
2. **Resolution gate.** A claim is testable in a draw only if:
   - its dev null has at least 99 pseudo-sets; and
   - its held-out null has at least 19.
   - Otherwise it scores **U-resolution**, which counts as U and is never R. The U-resolution share is reported.
3. **Plants mirror the real rows.** Each planted claim has a main partner plus 1 or 2 secondaries (chosen at random), all drawn from tokens with dev count ≥ 3.
   - ceil(0.4·n) of the head's next-positions are set to a partner: half to the main partner (rounded up), the rest spread at random over the secondaries. This is done in dev and held-out alike.
   - One-partner plants are run as before and reported separately. They do not count toward the bar.
4. **Coverage bar.** In every draw, at least 50% of planted pair-claims must pass the resolution gate. Otherwise v2 fails.
5. **Kill bars.**
   - Power ≥ 0.8 over testable pair plants (pooled).
   - False alarm ≤ 0.05: the share of random heads with random partner sets of size 1-3, on within-text shuffled draws, that survive with the gate applied.
   - The power by bin of dev next-tokens is used for the R rule, as in v1.
6. **Stop rule.** If coverage, power or false alarm fails, the calibration stops for good. There is no v3.

## Code (sealed with this file)
- `experiments/meaning_calibration/fcore2.py`: the gate, pair planting and `verdict2`. It imports `fcore` unchanged.
- `experiments/meaning_calibration/kill2.py`: the kill test.
- Writing claims and `run.py` follow only if v2 passes, sealed by addendum before any claim is scored.
