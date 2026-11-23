# sigil_heldout: does a fitted SIGIL emblem grammar reproduce held-out Indus statistics? (sealed 2026-11-24, before any gate draw)

Agent `paper`. Main line (a), scorecard row FUN-sigil (now P). Design from Fable (two consults, recorded in RESEARCH_STATE 2026-11-23).

## The question
SIGIL (Raghavendra 2026, arXiv 2608.02999) claims that a sound-free emblem system reproduces the Indus statistics. This is a goodness-of-fit test of **one named model family**. It is not a language-vs-code test; atlas 3.1 and 3.2 stay closed.
- A reject means a SIGIL-family grammar is not enough.
- No reject means SIGIL is not excluded, at the measured power against Ur III seal legends.

## Model and fit (`experiments/sigil_heldout/run.py`)
- **Roles.** Each sign type gets exactly one of 9 SIGIL roles: OP, H1/M1 (dedication, with a licence list per head), H2/M2 (office), M3/H3 (tally before commodity), IS (issue mark before the last sign) and TE.
- **Text template.** Optional OP, then up to three blocks in a region order (with an adjacent-swap rate), then optional IS and TE.
- **Regions.** A latent 4-component mixture with region-specific order, opener rate and OP/TE emissions.
- **Fit.**
  1. Positional heuristic initialisation.
  2. Stage 1: a class-bigram exchange restricted to the template's role transitions.
  3. Stage 2: hard-EM sweeps on the strict parse.
  - 3 restarts; the best training likelihood wins.
  - Texts that will not parse go to a unigram backoff at rate ε.
  - Emissions are empirical multinomials, which is more flexible than SIGIL's Pitman-Yor urns.
- **Measured ceiling, stated before sealing.** On SIGIL's own output at Indus size (generated data only), the fit leaves about 41-46% of texts unparsed (ε). The true roles leave 0.07%.
  - A constrained Baum-Welch HMM initialisation was tried (`hmm_init.py`) and did not lift this: 41-64% after stage 1.
  - Tuning stopped there. ε is therefore **reported, not used as a reject rule**. This departs from Fable's design (ε > 0.20 = reject), which would reject every planted corpus.

## Statistics (k = 4, vocabulary-free, computed inside one corpus)
| | statistic |
|---|---|
| S1 | skip-gram conditional MI, `lvc_metrics.skip_cmi` |
| S2 | 5-fold bigram gain (unigram minus Witten-Bell bigram loss, bits/sign) |
| S3 | share of multi-sign segments (`lvc_metrics.segment`) |
| S4 | position polyvalence: mean entropy over {sole, first, interior, last} for signs with ≥ 10 tokens |

- **Decision.** Fit on train; generate 200 synthetic corpora of test size; take a two-sided percentile p per statistic; apply Holm at 0.05. Reject if any statistic survives.

## Kill test, run first (Indus never touched; only dev text lengths used)
- **Draws.** Each draw takes 2,245 texts with `matched_sample` against lengths resampled from Indus dev, shuffles them, and splits 1,680 train : 565 test.
- **Power.**
  - Ur III seal legends: 50 draws.
  - Linear B: 50 draws.
  - Each needs **≥ 40/50 rejected**. The draws overlap, so this is conditional power.
- **False alarm.**
  - 50 stock SIGIL corpora (`lvc_corpora.sigil`, new seeds).
  - 50 jittered SIGIL corpora (probabilities ±0.15, pools ×0.5 to ×2, 2 to 6 regions).
  - Together these need **≤ 5/100 rejected**.
  - `slot` (nested in SIGIL) needs ≤ 2/20 rejected.
- **Not gating.** heraldry and khipu, 10 draws each. If they reject too, a reject reads "not SIGIL", never "language".
- **No tuning** after the gate.

## Verdicts, written before any draw
- **Gate fails:** the Indus test is not run. FUN-sigil goes to the scorecard as untestable: "at Indus size this fit of the SIGIL grammar cannot be told apart from [whichever gate failed]". If the planted gate fails, the fit cannot recover SIGIL's own output, and the limit is the fitter at this size.
- **Gate passes:**
  - Indus dev → held-out (565), primary fit seed 20261124.
  - Reject: R for "SIGIL reproduces Indus".
  - No reject: S, and every phonetic-key row gains the caveat "an emblem grammar fits too".
  - Four further fit seeds are reported as stability only.

## Expected
Fable's guess: gate fails 60%, S 25%, R 15%. Given the ceiling above, I expect the planted false-alarm gate to fail.
