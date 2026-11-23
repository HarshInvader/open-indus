# sigil_heldout: results (prereg `docs/prereg/sigil_heldout.md`, sealed 2026-11-23 22:57:46Z)

**Verdict: kill test FAILED, so the test is untestable. The Indus held-out set was not read.**

The statistics reject everything, including SIGIL's own output: 98 of 100 planted SIGIL corpora were rejected, against a bar of at most 5. Rejecting Ur III and Linear B therefore says nothing.

| corpus (Indus-shaped draws) | draws | rejected | mean ε (unparsed share) | gate |
|---|---|---|---|---|
| Ur III seal legends | 50 | 50 | 0.95 | ≥ 40 ✓ |
| Linear B | 50 | 50 | 0.85 | ≥ 40 ✓ |
| SIGIL, stock | 50 | 49 | 0.40 | planted total ≤ 5 ✗ (98) |
| SIGIL, jittered | 50 | 49 | 0.45 | |
| slot | 20 | 20 | 0.60 | ≤ 2 ✗ |
| heraldry (not gating) | 10 | 10 | 0.64 | |
| khipu (not gating) | 10 | 10 | 0.99 | |

- **Why.** The fit cannot recover SIGIL's roles from its own output at Indus size. About 40-45% of texts go unparsed and fall to the unigram backoff. The synthetic corpora are therefore less structured than any real or planted corpus, and all four statistics (skip-gram MI, bigram gain, multi-sign segments, polyvalence) catch this in nearly every draw.
- The limit is the fitter at this size, as the prereg anticipated. It is not a finding about Indus.
- **Scorecard.** FUN-sigil: "untestable at Indus size: a fitted SIGIL grammar cannot be told apart from its own failure to fit (planted false alarms 98/100)". This needs a blind re-rating (rule from scorecard addendum 1); it is queued with the next batch.
- **Reopen with.** A fitter that recovers SIGIL's roles from SIGIL output at 1,680 texts (ε near 0). For example, the author's own generator with published parameters, or a role-labelled emblem corpus. No tuning was done after the gate, as the prereg requires.

Files: `run.py`, `hmm_init.py` (tried, not used), `kill.json`, `kill_draws.json`, `kill.out`.
