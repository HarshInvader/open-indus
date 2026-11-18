# Forward predictions for the surviving leads (board #44)

## Verdict

- **Seven forward predictions are now hash-frozen** for material we do not have yet: CISI vol 3, the HARP sherd spreadsheet and new excavations. They cover every lead that survived on 2026-11-18. `fp.py --mode forward` scores them mechanically from `experiments/new_finds/new_texts.csv`.
- **The dry run on the held-out site, Kalibangan, KILLS the set under the board #44 rule.** Only one prediction could be scored there, F3 (the jar sign is rarer on pottery than its seal rate predicts), and it failed. Kalibangan graffiti carry the jar sign on 12 texts against 10.7 expected (RR 1.12, p = 0.72). The forecast was worse than the frequency baseline by 0.056 bits per text.
- **F3 is wrong everywhere, not only at Kalibangan.** An exploratory leave-one-site-out check gives RR 0.92 at Harappa, 1.17 at Mohenjo-daro and 1.12 at Kalibangan. Once text length is allowed for, the jar sign is not rarer on pottery. self_label's "jar rarer on jars" (70 vs 124) was mostly pottery texts being short. F3 stays frozen but is retired.
- **The other leads could not be tested on one site.** Kalibangan has 1 round seal, 1 cup-sign token and 9 plain-fish tokens, all below the minimum n. The direction matched the prediction for F1 (0 of 1 round seals ends in a closer) and F5 (fish merge +0.007 nats/token, CI −0.015 to +0.035). These are not evidence.
- **One frozen bar was wrong and has been amended.** I set the F4 bar from object-level counts by mistake. On distinct texts the current corpus fails it: {2,3,4} share 0.85, N ≥ 5 share 0.05. Amendment A1 was hashed after the dry run and before any forward scoring. It replaces F4 with "N = 5 absent (≤ 2%) and the forecast beats the frequency baseline".
- **What triggers scoring:** any one of
  - CISI vol 3 in hand;
  - the HARP spreadsheet arriving (Kenoyer, about 2027-01-05);
  - 20 or more new scorable texts in new_texts.csv;
  - 8 or more new round seals.

  Today the forward run is uninformative: 2 scorable new texts, none of them evaluable.

## Files

- Prereg: `docs/prereg/forward_predictions.md`. The sha256 hashes were appended to HASHES.txt at 10:39:18Z, before any scoring. Amendment A1 was hashed at 10:41:04Z.
- Scorer: `fp.py` (hashed) and `fp_a1.py` (hashed, for F4-A1).
- Dry run: `results_dryrun.json`, `dryrun.log`. Forward run: `results_forward.json`, `forward.log`.
- Exploratory: `x_f3_sites.py`, `x_f3_sites.json`.
- Everything ran through `board/run.sh`, one process, a few seconds each.

## The frozen predictions

All units are distinct texts. Each prediction is compared with a baseline: a trigram, an end-of-text trigram, or a unigram frequency model. Gain is the lead's log2 score minus the baseline's.

| id | prediction | pass | fail | min n | status |
|---|---|---|---|---|---|
| F1 | round seals end in a closer ≤ 25% of the time | ≤ 0.25 and binomial p < .05 vs square rate (≈0.53-0.55) | ≥ 0.40 | 8 | live |
| F2 | round seals break square-seal order: trigram excess ≥ +0.5 bits/sign | ≥ 0.5 and permutation p < .05 | < 0 | 8 round | live |
| F3 | jar M342 on post-firing graffiti ≤ 0.70 × seal-rate expectation (length-aware) | RR ≤ 0.70, Poisson p < .05 | RR ≥ 1.0 | E ≥ 8 | **retired** (failed dry run; RR ≈ 1 at all sites) |
| F3b | jar sign not concentrated on storage jars (HARP vessel forms) | RR < 1.5 | RR ≥ 2, Fisher p < .05 | 5 jar texts | live (needs forms) |
| F4 → F4-A1 | cup M328 preceded by tall strokes: N = 5 absent | N=5 share ≤ 0.02 and gain > 0 | N=5 share > 0.05 or gain < 0 | 10 | live (amended) |
| F4b | cup sign on offering-scene moulded tablets, OR ≥ 3 | OR ≥ 3, Fisher p < .05 | OR < 1.5 with ≥ 10 scene types | 5 scene types | live (needs CISI 3 photos) |
| F5 | plain fish M67 = M70 = M72 are one sign: merged class trigram beats plain | gain > 0 and CI lower > 0 | CI upper < 0 | 30 fish tokens | live |

Already frozen elsewhere and not duplicated here: ticked fish final (P3), M109+M59 (P4), M373 on bangles (BO-H1-4), and painted vessels with jar < 5% (A4b).

Not frozen because they did not survive:
- M342 on broken seals (R37, corrected p 0.06);
- numeral-opening round seals (#39);
- the whole L_strict shape list. It fails the ICIT replication, and only the fish merge carries its gain.

## Dry run (Kalibangan held out; training = all other sites)

I chose Kalibangan from object counts only, before reading any of its texts. It is the only non-core site present in both editions that has a large graffito set and a seal set.

| id | n at Kalibangan | result | gain vs baseline | verdict |
|---|---|---|---|---|
| F1 | 1 round seal | 0/1 closer-final (square p0 0.55) | +0.16 bits/text | not evaluable |
| F2 | 1 round, 55 square | excess −2.6 bits/sign (one text) | — | not evaluable |
| F3 | 64 graffiti | 12 observed vs 10.7 expected, RR 1.12, p 0.72 | **−0.056 bits/text** | **fail** |
| F4 / F4-A1 | 1 cup token (N=2) | — | −1.12 bits | not evaluable |
| F5 | 98 texts, 455 tokens, 9 fish | +0.0073 nats/token (CI −0.015, +0.035) | same | not evaluable |
| F3 (M77 edition, secondary) | 19 graffiti | 9 vs 4.0, RR 2.26 | −0.29 | not evaluable (E < 8) |

**Kill rule:** summed gain over the evaluable predictions is −0.056, which is ≤ 0, so the set is killed. Only F3 was evaluable, so the kill rests entirely on F3.

The scoring machinery works, end to end, on both editions.

## Caveats and what was not checked

- **The dry run is not a clean confirmation.** Every lead was found on corpora that include Kalibangan, as the prereg says. It does show that F3 fails even on data it was partly fitted to.
- **One site cannot test F1, F2, F4 or F5.** Round seals, cup tablets and plain fish are concentrated at Mohenjo-daro, Harappa and the Gulf. A dry run that could test them would need Mohenjo-daro or Harappa held out, which removes half the training data. I did not run that, because the task allowed one site.
- **The summed gain mixes units** (bits per text, per token, per sign). Only its sign is used.
- **F2 compares against one batch.** Its reference is the square seals in the same batch, or a leave-one-out training mean if a batch has fewer than 8. It does not use #39's site × length matching, so it is cruder than the red-teamed statistic.
- **Forward material arrives in M numbers.** F1 and F2 were developed in Wells codes on ICIT. In forward mode they are trained on M77 home seals, where the square closer rate is p0 = 0.53.
- **F4b and F3b need data we do not hold.** F4b needs blind scene coding of CISI 3 photos; F3b needs vessel forms. The scorer cannot run either yet; score them by hand under the stated bars.

## Next

- Score on the triggers above, once per trigger, and report every prediction, including fails.
- Pending lead decision: the lead could hold out Mohenjo-daro as a second dry run to give F1, F2, F4 and F5 real n. That needs a new prereg; this one allows one site.
- Retire "jar sign rarer on pottery" from any site or README text that still implies it beyond length (self_label finding 3). That is for the lead, since I do not edit README or the site.
