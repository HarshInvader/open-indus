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

## Addendum 1 (sealed 2026-11-23, still before any table has arrived)
Two later sealed studies showed that the CPW score above is blind at Indus shape:
- `lb_certify`: the true Linear B key could not be told from shuffled keys.
- `lb_shape_ladder`: fit can refute a full-coverage key but never certify one.

The scoring method was frozen only against changes made after the table arrives. No table has arrived, so we replace it now:
- **Primary score.** IC with a shape-keeping N1, exactly as in `experiments/yj_ic_refute/run.py` (prereg `yj_ic_refute`):
  - Monier-Williams lexicon, generous matcher primary and strict as a second arm;
  - LMIN fixed by the frozen density rule;
  - 1,000 N1 draws within consonant-count class and frequency bins.
- **Power gate at his coverage.** His unread signs stay as breaks. The planted-Rigveda gate is run with his value inventory, on his signs, with his unread signs masked the same way.
  - The gate needs at least 16 of 20 planted passes, at most 1 of 20 on a shuffled stream, and strictly rising partial keys.
  - If the gate fails, the verdict is "below the fit standard: untestable by fit". At 74% coverage the true Linear B key failed (13/20), so a partial table will likely end here.
- **Reading the result (replaces the frozen reading above).**
  - **Gate passes and his key does not beat shuffles under either matcher:** "refuted at stated power". It is reported to him first, with code.
  - **His key beats shuffles:** "not refuted; no support". Fit can never support a key (`lb_shape_ladder`), so this is not a lead.
- **Secondary.** The old CPW/N2 method runs as sealed above, as a descriptive result only.
- **Unchanged.** The gate on what gets scored (at least 15 M-numbers with sound values; no meaning-only tables) and the rule that nothing may change once a table arrives.
