# lb_shape_ladder addendum 1: refute at 95% and 90% coverage (sealed before running)

- **Why.** The Scott (Dunn) MahaSamVani key covers about 95% of M77 tokens. Refute fails at 74% (R0: 13 of 20) and passes at 100% (R1: 20 of 20), so the standard has to be measured in between before that key is benched.
- **Rungs.** R95 and R90 use Indus chunks, as R0 and R1 do. The same 20 subsamples, lexicon, IC statistic, N1 null, 1,000 permutations and seeds scheme are reused, with `run.py` unchanged.
- **Refute only.** There is no N2: certify fails on undivided text at every rung.
- **Bar.** As sealed: refute in at least 16 of 20 subsamples, and the shuffled-text control in at most 1 of 20.
- **Use.** A claimed key is benched under refute only if its token coverage is at or above the lowest passing rung. Signs it leaves blank stay unkeyed, as at R0.
- **Code.** `experiments/lb_shape_ladder/coverage.py`.
