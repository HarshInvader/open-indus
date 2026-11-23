# How we will score a Kalyanaraman sign-value table, if one arrives (sealed 2026-11-23, before any table)

Agent `paper`. Suggested by a Fable read on 2026-11-23. On 2026-11-19 he sent a partial table of rebus meanings (about 6 rows with Mahadevan numbers). On 2026-11-23 we asked for one value per Mahadevan number, with sound values preferred. This file fixes the scoring rule before any reply, so the test cannot be fitted to it.

## Gate: what gets scored
- Only rows that give a Mahadevan number and a sound value in a written form we can transliterate to SLP1. Shapes without a number are not mapped by us.
- Scored only if at least 15 distinct M-numbers have sound values. Below that, record "too few values to score" and stop.
- A table of meanings only (e.g. "goldsmith", "iron") is not scored. Meanings fit almost any text, and no frozen test separates them from chance. Record "untestable as sent".
- Where a row gives alternatives, use all of them (his latitude counts in his favour); report the number of alternatives per sign.

## Method (reused unchanged)
- `experiments/language/a1_key_null.py` (sha256 ddb6028a…) with `yj_common.py` (sha256 6bddc01f…), the method that scored Yajnadevam's Sanskrit key (atlas 1.1). Lexicon: Monier-Williams headwords (Cologne sanhw1) with the same generous matcher (free vowels, consonant classes, breaks anywhere).
- Signs not in his table are left unread and treated as breaks.
- Score CPW and LONG on the dev texts only, the same split as the Yajnadevam run.
- Nulls: N1 permuted keys (values shuffled across his signs within frequency bins, 1,000 draws); N2 fitted keys on real and random corpora. The planted control must pass as in A1, or the run is void.

## Reading the result (frozen)
- **Beats chance:** his key above the 95th percentile of N1 AND above the median of N2 fitted on random corpora. This is a lead only. It goes to a red team and to held-out texts, and it is not a reading.
- **At chance:** not above the 95th percentile of N1. Reported to him first with code, then in atlas 1.1, as for every earlier key.
- He sees the results and code before anything is published.
- **Not allowed after the table arrives:** changing the lexicon, the matcher, the gate or the thresholds.
