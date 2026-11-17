# Pre-registration: numerals at the end of foreign-found Indus texts (board #15, agent H6)

Written 2026-11-17, before computing the statistic on the sets below. The only result already known is
#10's descriptive count over the full foreign corpus (9/43 numeral tokens text-final vs 69/1253 at home).

## Hypothesis
H1: texts on Indus-script objects found outside the Indus region end in a numeral sign more often than
length-matched home seals. H0: same rate.

## Data
- Numeral = Wells signs W001-W059 (as in #10).
- Sequences: `seq_wells` in `experiments/foreign_corpus/foreign_corpus.csv`, reading order, with `#`, `|`, `?` dropped,
  length >= 2. For UNPROV-02 use the M77 reading, as #12 asks (final sign numeral if it is an M77 stroke sign M1-M? per the
  bridge; if no bridge, the Wells sequence and say so).
- PRIMARY set: objects with `use_in_crib_attack` starting with "yes" in `experiments/foreign_readings/readings_check.csv`.
  SUSA-02 and BAHRAIN-01 are run in both directions; the reported primary p is the LARGER of the two.
- SECONDARY set: PRIMARY + "sensitivity only" rows.
- DESCRIPTIVE: all foreign_corpus rows with length >= 2 (replicates #10), not confirmatory.
- Home pool: distinct ICIT seal texts from non-foreign, known sites (`icit_units(exclude_sites=FOREIGN|{"Unknown"}, types={"seal"})`), length >= 2.

## Test
- Statistic T = number of texts whose last sign is a numeral (a text-level count, so one long numeral text cannot dominate).
- Null: for each foreign text of length L, draw one home seal of length L (pool L±1 if fewer than 30 at L);
  20,000 draws; p = P(T_null >= T_obs).
- Alpha 0.05 for PRIMARY; SECONDARY reported, not corrected (2 tests: Holm over PRIMARY and SECONDARY given too).
- Concentration: leave-one-out p (max over dropping each text); rate in the 9 order-breaking survivors of #11 vs the rest.
- Power: plant a final-numeral rate r in a synthetic foreign set of the same size and lengths (r = 0.2, 0.3, 0.5) and
  report the share of 2,000 plants with p < 0.05.
- Supported only if PRIMARY p < 0.05 AND leave-one-out max p < 0.10. Otherwise inconclusive (if power < 0.8 at r = 0.3)
  or refuted.
