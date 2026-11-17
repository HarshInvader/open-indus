# Pre-registration: assumption audit sensitivity checks (board #27, H12)

Written 2026-11-17 before any perturbed condition was scored. Code: `experiments/assumption_audit/sens.py` (hashed with this file).

## Question

Which headline structural findings depend on three assumptions the project takes for granted:

- **A-dir** we know each text's reading direction and line order;
- **A-tx** the transcription (Mahadevan 1977) is accurate token by token;
- **A-ind** held-out texts are independent of dev texts (no workshop series or near-copies doing the work).

The sign-list assumption is NOT re-run here: `experiments/signlist_robustness/` already ran the same nine tests under 12 alternative lists (Wells/ICIT, Parpola lumps, targeted lumps, random allograph splits, three image-cluster lists). This audit cites it.

## Tests

The nine tests T1-T9 of `experiments/signlist_robustness/harness.py`, unchanged, type unit, M77 sign list, split v2, with their frozen pass bars ("survives"):
T1 order beats permutations (#1), T2 ticked fish final (#3), T3 M109+M59 (#5), T4 object-type registers (#6), T5 L-R reversals (#7), T6 cores are 1-2 word signs (#10a), T7 fixed pair order (#10b), T8 fish lexical class (#11), T9 functional parse vs shuffle (#9).
Finding #2 (logo-syllabic, descriptive), #4 (Gulf/round seals, separate code base) and #8 (copper types) are not run; the register treats them.

## Conditions (dev and held-out both damaged; held-out membership fixed from the undamaged text)

| condition | what | seeds |
|---|---|---|
| base | none (must reproduce harness M77/type) | - |
| rev10 / rev25 / rev50 | whole object read backwards for 10/25/50% of objects (lines for T5 reversed for the same objects) | 1,2,3 |
| lineshuf | line order shuffled within each multi-line object (T5 unaffected by construction) | 1,2,3 |
| noiseR2 / 5 / 10 | that % of sign tokens replaced by a random sign drawn by corpus frequency | 1,2,3 |
| noiseV2 / 5 / 10 | that % replaced by a look-alike sign (same `img_mid` drawing cluster of signlist_robustness), random if none | 1,2,3 |
| dedup | texts of >=3 signs: held-out kept only if more than 1 edit (3 signs) / 2 edits (>=4 signs) from every dev text, and one per held-out family; dev collapsed to one per family by the same rule | - |
| nodoubt | drop every object that has a sign Mahadevan marked doubtful | - |

29 runs. Lines for T5 under noise get independent noise draws at the same rate.

## Verdict rules (per test, per condition family; frozen)

- **holds**: passes its frozen harness bar in at least 2 of 3 seeds (single-run conditions: passes).
- **weakens**: fails the bar in at least 2 of 3 seeds but keeps its direction in at least 2 of 3. Direction means: T1 share > chance; T2 ticked share > plain share and > null mean; T3 k/n > base; T4 mean AUC > 0.60; T5 share > 0.5; T6 len-1 share > 0.14 and standalone > 0.11 (the syllabic references); T7 share > 0.5; T8 at least 1 of 3 sub-tests p < 0.05; T9 coverage > shuffle.
- **fails**: direction lost in at least 2 of 3 seeds.
- **NT**: not testable (e.g. no tokens).

Effect sizes are reported for every run: T1 share/chance; T2 ticked minus null share; T3 k/n over base; T4 mean AUC; T5 share; T6 len-1 and standalone shares; T7 share; T8 n_pass; T9 coverage minus shuffle.

## Predictions (stated so they can be wrong)

- P1 Direction: T2, T5, T7 (position- or order-specific) weaken or fail at rev50; T4, T6 hold at rev50; T1 holds at rev25.
- P2 Noise: every test holds at 2% random noise; at 10% random noise at least T2 and T3 (few-token tests) weaken. Look-alike noise hurts T2/T3/T8 more than random noise at the same rate (it moves fish into fish).
- P3 Dedup: all tests keep direction; T3 and T5 may miss bars from lost n.
- P4 nodoubt: all hold.

## Interpretation fixed in advance

A test that holds at rev50 does not need us to know the reading direction. A test that holds at 5% look-alike noise tolerates a misreading rate well above Mahadevan's own doubtful rate (374 of 13,372 tokens = 2.8%). Failure under dedup means the finding leaned on near-copies and should be reworded. None of this tests whether the signs are language; that is in the register only.

## Multiplicity

These are robustness runs (ledger mode `robustness`), 29 runs x 9 tests = 261 rows of pass/fail, not new discoveries; no claim is added on their strength. The ledger file gets one row per test x condition family (9 x 10 = 90 rows).
