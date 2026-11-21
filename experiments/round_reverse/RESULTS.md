# Round-seal reversal (Fable 5.2 plan 11, candidate 6)

Prereg: `docs/prereg/round_reverse.md`, hashed with `run.py` in `docs/prereg/HASHES.txt` (tag `round_reverse`, 2026-11-21T07:59:45Z) before any reversed text was scored. Ledger: `ledger_rows.csv`.

## Conclusion first

**No dent. Reading round-seal texts backwards does not make them look like Indus order. Finding #4 is not a reading-direction error.**

- Primary (Kneser-Ney bigram, format-matched, 31 texts): order excess +1.30 bits/sign forward, +1.35 reversed. Ratio 1.04 (95% CI 0.80-1.29). The reversed excess is still significant (p = 1e-4).
- The other two models agree: class grammar ratio 1.08, positional model 1.57 to 2.14 (wide CIs).
- Only 15 of 31 texts score better reversed, which is a coin flip.

## Why: round texts have no Indus order in either direction

- Ordinary square seals score about 2.1 bits/sign better than shuffles of their own signs under KN. Round texts score about the same as their shuffles, forwards (mean d -0.04) and backwards (+0.06).
- Reversing a square seal costs it 3.3 bits/sign (KN). Reversal moves the round texts by only 0.1.
- So the round texts are not home texts written in the wrong direction. A text read the wrong way would score well once turned round. These score like random orders both ways.

## Controls

| control | result | pass? |
|---|---|---|
| C1 direction sensitivity: 400 square seals reversed | KN +3.28, GR +2.88, POS +1.27 bits/sign worse | yes, the models see direction |
| C2 planted direction error: length-matched square seals written backwards, 100 repeats | planted excess +3.13; after reversal +0.03; ratio below 0.5 in 100% of repeats | yes (bar 80%) |

The test could see a direction error of this kind. It found none.

## Numbers (excess over matched square seals, bits/sign; 10,000 matched draws)

| model | matching | forward | reversed | ratio (CI) | texts lower reversed |
|---|---|---|---|---|---|
| KN | length | +2.07 | +2.17 | 1.05 (0.89-1.22) | 15/31 |
| **KN** | **F0 format** | **+1.30** | **+1.35** | **1.04 (0.80-1.29)** | 15/31 |
| GR | length | +1.66 | +1.79 | 1.08 (0.86-1.38) | 12/31 |
| GR | F0 | +0.97 | +1.05 | 1.08 (0.72-1.58) | 12/31 |
| POS | length | +0.46 | +0.72 | 1.57 (0.72-3.57) | 14/31 |
| POS | F0 | +0.22 (p 0.07) | +0.47 | 2.14 (0.56-14.2) | 14/31 |

- The forward numbers reproduce board #41 (+2.10 and +1.35 there; small differences come from permutation draws).
- Secondary set, the 28 texts with a readable last sign (25 scorable; descriptive only, `subset28.json`): mean d KN -0.02 forward, +0.02 reversed; 13 of 25 lower when reversed. Same picture. Disclosure: the hashed `run.py` did not compute the matched excess for this subset, so it is reported from the per-text table by `subset28.py`, added after the run.

## Hypothesis table

| hypothesis | verdict |
|---|---|
| The round-seal off-order (#4) is mainly a reading-direction error | **refuted** (ratio 1.04, controls pass) |

## Caveats

- The same 31-35 round texts used by #22-#41. Not new data.
- Reversal is sign by sign over the whole text. A text with lines read in different directions (boustrophedon) is not tested.
- Some texts are short (2 signs). Their reversal is their only permutation, so d flips sign exactly; they add noise, not bias.
- What remains open is what #41 left open: a separate naming practice or language, or a genre whose order rules we cannot see.

## Files

`run.py` (hashed), `run.log`, `results.json` (main, per-text table, controls, verdict), `subset28.py` + `subset28.json` (descriptive add-on), `ledger_rows.csv`.
