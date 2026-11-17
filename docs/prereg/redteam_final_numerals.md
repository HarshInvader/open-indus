# Pre-registration: red team of #15 (final numerals on foreign texts), board task #21, agent H7

Written 2026-11-17 before any of the tests below were computed. Already seen (from #15 and its RESULTS): foreign
numeral-final ids and their sequences; home square-seal numeral-final rate 4.6%; ICIT type counts (SEAL:C = circular,
32 objects, about 10 at home sites; SEAL:R = rectangular, width/height median 2.2). Home final rates for the circular
and rectangular pools have NOT been computed.

Claim under attack: foreign Indus texts end in a numeral (W001-W059) more often than home seals
(#15: all-foreign 9/40 vs 2.08, p = 0.00025; secondary set 6/20 vs 0.72, p = 5e-5).

## Data
- Foreign texts: `experiments/foreign_corpus/foreign_corpus.csv`, same selection and cleaning as #15 test.py
  (`#`, `|`, `?` dropped; final legible sign used). Sets: ALL (n_legible >= 2, as #15 descriptive), SEC (#15 secondary,
  readings_check use = yes or sensitivity). ROUND = rows whose `shape` starts with "round".
- Home pools (ICIT, site not in glib.FOREIGN and not Unknown, distinct sign sequences, length >= 2):
  SQ = #15 pool (SEAL:S + SEAL); CIRC = SEAL:C; RECT = SEAL:R.

## Attacks
A. Genre / shape. (A1) ROUND foreign texts vs CIRC home: one-sided Fisher exact on numeral-final counts.
   (A2) ROUND vs RECT, length-matched null as #15 (pool L±1 if < 30 texts at L). (A3) report CIRC and RECT final
   rates. Power for A1: probability Fisher p < 0.05 if CIRC's true rate is 4.6% and ROUND's is 29%, at the real n.
B. Reading artefact. Recompute numeral-final using the M77 reading (`seq_m77`; if its last legible position is `?`
   use the last legible sign) mapped to Wells through the inverted bridge (`bridge_WM.json`, M -> W numeral if the M
   appears in any W001-W059 entry). Texts with no M77 reading keep their ICIT reading. Rerun #15's null (SQ pool)
   on ALL and SEC. Also report per-text agreement ICIT vs M77 on "numeral-final".
C. Non-count role. Define COUNT = numeral excluding W001 (1 short stroke), W002 (short-2, the M99 connective) and
   W031 (1 tall stroke). Rerun the SQ-pool length-matched test on ALL and SEC with COUNT-final as the outcome, the
   home pool recoded the same way. Report each final sign's home final share.

Planted control for the null machinery: insert numeral endings into a random 30% of ALL texts (replacing the last
sign by W004) 1000 times; report how often the SQ-pool test gives p < 0.05 (must be >= 0.8 for B and C to count).

## Decision rule (alpha 0.05 / 3 attacks = 0.0167)
- "reading artefact" if B on ALL gives p > 0.0167.
- "non-count role" if C on ALL gives p > 0.0167.
- "genre effect" if A1 Fisher p > 0.05 AND CIRC rate >= 15%; "genre untested" if CIRC has < 8 texts or A1 power < 0.5.
- The #15 effect "survives" an attack if it is not explained by it. Verdict: positive (survives all), mixed, or negative.
