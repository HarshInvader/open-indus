# Shape ladder: at what text shape does dictionary fit start to recognise Linear B's true key? (sealed 2026-11-23, before any number)

Agent `paper`. Main line (a), the claim bench. This is Fable's top study after `lb_certify` (RESEARCH_STATE, "Main-line plan", study 1 result).

## Why
`lb_certify` stopped at its kill test. The CPW fit score could not tell Linear B's true key from shuffled keys at Indus chunk lengths. Fable's review found two reasons:
- **The lexicon is saturated.** The Homeric skeleton lexicon contains almost every string of 1-3 consonants, so short runs always "read".
- **The segments are short.** Scored segments averaged 2.47 consonants. Noise-fitted keys also won by changing segment shape.

The scorecard therefore needs to know at what text shape fit starts to work, judged with a statistic that ignores saturated short words and nulls that hold shape fixed. The answer becomes a public standard: "dictionary fit counts as evidence only at shape X or above". If no rung passes, the standard is "never, with this lexicon".

## Data (all already held; unchanged from `lb_certify`)
- **Linear B, lexicon, sign readings and key rules:** as in `docs/prereg/lb_certify.md`.
  - Syllabic words only.
  - Homer skeleton lexicon, at most 7 consonants.
  - j and w are removed from every key value.
  - q matches p, t or k.
- **Code:** imports the hashed `experiments/lb_certify/run.py` for data, lexicon and true values.

## Rungs
Each subsample k first draws 2,300 Indus-length chunks, as in `lb_certify`, and records their total token count T. Every rung of subsample k uses about T tokens. Dev and held-out are split 50/50 by source line.

| rung | text unit | word division | coverage of true key |
|---|---|---|---|
| R0 | Indus-length chunks (as `lb_certify`) | no | 74% (unkeyed signs are breaks) |
| R1 | the same chunks | no | 100% |
| R2 | whole lines, taken in random order until T tokens | no | 100% |
| R3 | the same lines | yes (each word is a segment) | 100% |

## Statistic
- **IC** is the share of all held-out key consonants that lie inside a lexicon word of at least LMIN consonants. Each segment is segmented to maximise coverage, and consonants may stay uncovered.
- **LMIN = 4.** This is the smallest length at which the q-free lexicon holds 25% or less of the 9^L possible strings. Measured before sealing (lexicon only): L=1 100%, L=2 98.8%, L=3 67.5%, L=4 17.7%, L=5 1.4%.

## Nulls (shape-preserving)
Keys keep the same signs. Values move only between signs with the same consonant count, so every key gives identical segment and consonant-run lengths.
- **N1:** true values permuted within frequency bins of 10, inside each consonant-count class. 1,000 draws.
- **N2:** keys hill-climbed to maximise IC on dev-shaped corpora: real dev, a unigram shuffle of dev and a bigram-Markov dev, keeping word and text lengths. Each corpus gets 3 restarts of 3,000 swaps, swapping only within a consonant-count class. Each start is the true values shuffled within class. The 9 fitted keys are then scored on held-out.

## Decision rules (20 subsamples per rung, k = 1-20)
- **Refute** holds at a rung if the true key's held-out IC exceeds the N1 99th percentile in at least 16 of 20 subsamples.
- **Certify** holds at a rung if the true key's held-out IC exceeds the maximum of the 9 pooled N2 keys in at least 16 of 20 subsamples.
- **The published standard** is the lowest rung passing refute and the lowest rung passing certify, each stated as the true key's mean consonants per scored segment at that rung.

## Planted controls (the study is void if one fails)
1. **R3 must pass refute.** If it does not, the verdict is "the Homeric lexicon (or IC) is inadequate even at word-divided shape", and no shape standard is issued.
2. **Partial keys.** At the lowest rung passing refute, partial keys must rise strictly: 0, 25, 50 and 75% of signs right (the rest shuffled within class), mean of 40 draws per level, then the true key.
3. **Shuffled text.** On unigram-shuffled held-out text, the true key must pass refute against its own N1 in at most 1 of 20 subsamples, at every rung that passes refute. Otherwise the pass reflects letter statistics, not reading.

## Kill test (run first)
- R3 on subsample k = 0, all quantities computed.
- **If R3 fails refute (true IC at or below the N1 99th percentile): STOP.** Verdict: "lexicon/statistic inadequate; no shape standard". The full ladder is not run.
- Otherwise run the full ladder (80 jobs, 4 workers).

## What each outcome means for the scorecard
- **Refute passes only at R3:** dictionary fit can count against a key only on word-divided text. Indus has no word division, so fit can never refute an Indus key. Atlas 1.1 stays "unsupported".
- **Refute passes at R2 or R1:** fit can count against a key on undivided text of that length, with full coverage. Atlas 1.1 rows whose keys meet that shape could become "refuted" again in a follow-up sealed test.
- **Refute passes at R0:** the `lb_certify` failure was due to CPW, not shape. That needs a follow-up rerun of the benched keys with IC.
- **Certify fails everywhere:** fit can never certify a key on its own. The scorecard's top tiers then need non-fit evidence (the tripod tier, forward predictions).

## Limits stated in advance
- **Lexicon.** It is Homeric, not Mycenaean. An R3 failure cannot separate "shape" from "lexicon".
- **Key coverage.** R1-R3 use 100% coverage. Indus claimants key nearly every sign, so this matches them, but their values are 1 consonant per sign far more often.
- **Scope.** One script, one lexicon, one statistic family.

## Cost
Timed before sealing on a shuffled key (no score printed): one held-out scoring takes about 0.004 s, and 300 fit swaps about 0.45 s. One job is about 1 minute, so the full ladder is about 20-30 minutes on 4 workers. It runs under the Indus compute lock with `nice -n 20` and the memory guard.
