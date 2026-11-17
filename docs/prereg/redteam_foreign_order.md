# Pre-registration: red team of task #1 "10/39 foreign texts break Indus order" (board task #11, agent H2)

Written before any of the tests below is run. Code: experiments/redteam_foreign/attack.py. It copies the
model and reference set-up of experiments/foreign_corpus/score.py, with the same grammar, the same training
set and the same 5-fold CV native reference. It does not edit or import H1's folder.

Base flag (H1): grammar p < 0.05 against native square seals of the same (min(len,6), full) key.

T1 Direction. Score the reversed sequence for SUSA-02, BAHRAIN-01 and FAILAKA-01.
  Calibration: the flag rate of reversed native CV seals (how much reversal alone breaks a native text).
T2 Alternative readings. Each is bridged to Wells via bridge_WM first candidate; unbridged signs become #.
  UR-02 with the M77 ending (M171-M387-M97-M341-M107); UR-05 as M77 (M175-M12-M182); SUSA-02 as the M77
  published sequence (M173-M10-M97-M121-M185-M97-M297-M57) in both directions.
T3 Reference. (i) The native pool is every CV-scored native text in any register, keyed the same way.
  (ii) The square-seal pool is kept, but 0.18 bits/sign is subtracted from each foreign score (H1's format cost).
T4 Bridge. Native M77 held-out seals are bridged to Wells exactly as M77-only foreign texts are, then scored
  with the full model (they are out of sample: icit_devlike excludes near-copies of M77 held-out). Report
  their flag rate. If it exceeds 5%, re-test the M77-only flagged texts (UNPROV-07) against that rate.
T5 Provenance. Drop region "unknown-WA" rows; recount flags and the binomial p (rate 0.05).
T6 Misreading control (new). Take native CV seals with >= 3 signs. Replace one random sign position with a
  sign drawn by native frequency, score with the fold model that excluded the text, and get the flag rate f1.
  Under H0 (reading errors only), "probable/uncertain/corpus only" texts are flagged at rate f1 and
  "confirmed" texts at 0.05. Compare the observed flag count to this Poisson-binomial (exact, by convolution).
T7 Order versus inventory (new). For each scored foreign text with >= 3 signs, take up to 2,000 random
  permutations of its sign list (completeness kept) and compute q = the fraction of permutations scoring
  strictly better (lower bits/sign) than the observed order. Do the same for native CV seals with >= 3 signs.
  Order-break claim: flagged foreign texts have higher q than natives (one-sided Mann-Whitney). If flagged
  texts have q no higher than natives, the flags reflect rare or unusual signs, not their order.

Survivor rule (decided now). A text survives if it is flagged (p < 0.05) under every direction and reading
tested in T1/T2, with the original pool. The headline number is survivors out of scored texts. It is tested
(a) against binomial 0.05 and (b) against the T6 misreading null. Survivors that are also order-driven
(T7 q > the native 90th percentile) are listed separately.
Verdict: "holds" if (a) and (b) both give p < 0.01 after T1/T2; "weakened" if only (a) does; "broken" if neither.
Tests run: 7 families; no other analyses are reported as confirmatory.
