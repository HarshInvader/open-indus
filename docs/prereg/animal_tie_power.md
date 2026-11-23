# How strong a sign-animal tie could the Indus tests have seen? (sealed 2026-11-23, before any power number)

Agent `paper`. Main line (b), non-textual anchors. This is Fable's spec after `yj_ic_refute`, recorded in RESEARCH_STATE.

## Why
Atlas 5.7 says the "animal is not named in the text": unicorn vs other AUC 0.516. F14 found no single sign × animal pair passing Bonferroni. Neither result was sized: no planted tie was run, so we don't know what size of tie they exclude.

The red teams of `lb_certify` and `yj_ic_refute` taught three things:
- power must be measured on the real corpus, with its formulae;
- power must be stated at the real null's width;
- ladders must be token-weighted.

So we plant on the real Indus seals. Linear B supplies a real-script effect size to place on that ladder, as an upper bound, since a logogram is what the line counts.

## Indus tests calibrated (code reused unchanged)
- **T1:** `experiments/context/q1_animal.py`, giving `build`, `featurize` and `cv_score`. Features are signs, initial signs, bigrams, length and stroke classes; the model is L2 logistic regression with 5-fold CV.
  - Unicorn vs other AUC for the pooled target.
  - 8-class balanced accuracy for single-animal targets.
  - Null: labels permuted within site. Pass at p < 0.05.
- **T2:** the F14 statistic (`sources/shaunmortal_indus/analysis/icon1.py`): sign × animal counts, with strata of site × min(length, 7) (strata of at least 5 texts kept).
  - Signs in at least 15 texts; a test counts only with at least 5 observed.
  - Animals: the non-unicorn classes with at least 20 texts (shorthorn bull, zebu, elephant).
  - The exact stratified hypergeometric p replaces F14's Monte Carlo (`common.strat_hyper_matrix`, the same null). Bonferroni over the real data's test count.
  - **Deviation from F14:** run on the M77 unit, so both tests share one corpus. F14 itself ran on ICIT.
- **Unit:** M77 distinct seal texts with an animal (texts under more than one animal dropped), classes with at least 10 texts. Measured before sealing: 1,149 texts (unicorn 945, shorthorn bull 78, zebu 45, elephant 34, rhino 15, tiger 12, goat-antelope 10, buffalo 10).

## Leg A (primary): label-swap plants on the real Indus seals
- **Texts are never edited.** For each draw:
  - pick a tie sign g uniformly from signs in at least 5 texts;
  - inside each site, swap animal labels between class-A texts lacking g and non-A texts having g, until a share (natural rate of g in A + δ) of class A carries g, capped at 100%.
  - Formulae, sign frequencies and site × class counts stay exact.
  - If the target cannot be reached, another g is tried (up to 50). If none works, the draw is infeasible and is reported, not counted.
- **Targets:** non-unicorn pooled (T1 binary), shorthorn bull (T1 multi, T2), elephant (T1 multi, T2), tiger (T1 multi only, since it has fewer than 20 texts).
- **Ladder:** δ = 0.05, 0.10, 0.20, 0.40 and 0.80 of class A's texts (token-weighted by construction); 40 draws per rung.
- **Null:** the null is identical across plants, because the texts and the site × class counts are fixed. It is computed once: 1,000 within-site permutations for each T1 statistic, which is the real null's width.
- **Power** at a rung is the share of feasible draws passing the test's own bar. **c\*** is the smallest δ with power of at least 0.8, for T1 and T2 separately.

## Leg B: Linear B at Indus shape
- **Data:** `sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl` (DAMOS), parsed with Fable's rules:
  - a word is lowercase syllables joined by "-";
  - a logogram is 2 or more capitals, with optional `:`/`+`/`;` suffixes;
  - a line counts if it has at least 1 word and at least 1 logogram;
  - label = the line's first logogram;
  - site = KN, PY or other.
- **Unit and subsamples:** one random qualifying line per tablet. The classes are the 8 most common tablet-modal logograms: OVIS, GRA, VIR, MUL, OLE, TELA, LANA, SA (measured before sealing). Each subsample keeps every OVIS tablet (about 390) and cuts the seven others to 78/45/34/15/12/10/10, matching Indus minority sizes.
  - Indus's unicorn share is 82%; here OVIS is about 66%. This gap is stated, not fixed.
  - Lines are then deduplicated and conflicts dropped, as in `q1.build`. Subsample 0 has 459 distinct texts.
  - Logograms, units and numerals are never features.
- **Two opaque codings:** words as signs, and syllabograms as signs (word division removed).
- **Tests:**
  - T1 binary (OVIS vs other AUC) and T1 multi (8-class balanced accuracy); null of 100 within-site permutations per subsample; pass at p < 0.05.
  - T2 on the minorities with at least 20 texts.
  - 20 subsamples.
- **Formula ladder (T1 binary):** delete the most frequent words covering 0, 10, 20, 35 and 50% of word tokens before coding.
- **Control:** labels permuted within site, then tested as real. This must pass in at most 2 of 20 per coding, or Leg B is void.
- **Mapping:** the conservative coding is the one with the lower mean AUC at rung 0. Each of its rungs' mean AUC is placed on Leg A's pooled ladder (mean planted AUC per δ, linear interpolation, with the null mean at δ = 0) to give an Indus-equivalent δ.

## Kill test
- Linear B, words coding, subsample 0, T1 binary AUC against 200 within-site permutations. It must exceed the null's 99th percentile.
- If it fails, STOP. Verdict: "q1's classifier cannot see a ledger's own commodity tie at Indus shape". Atlas 5.7 becomes "untestable".

## What each outcome means (frozen)
- **T1 c\* ≤ 0.20 for a target:** atlas 5.7 and F14 become "excluded at stated power: no sign tie covering c\* or more of class A's texts beyond its natural rate".
- **c\* > 0.40, or none, for a target:** that animal is "untestable at its size". The README line "no sign tied to picture" is narrowed to the targets with a c\*.
- **Linear B full passes and names-only (50% rung) fails:** the Indus null rules out "the text is about the animal" only. It says nothing on "the animal is an emblem and the text is a name".
- **T2 c\*** is stated separately for each of the three F14 animals.
- Neither leg can show a positive anchor. This study sizes a negative and gives the scorecard's tripod rows a floor.

## Limits stated in advance
- A plant ties one sign to one class. Ties spread over several signs, or over bigrams, are not planted.
- In Linear B the logogram is part of the record, which is closer to a label than an Indus field animal is. Leg B is therefore an upper bound.
- The real Indus statistics are recomputed and reported. They were already published (Q1), so they are not new tests.

## Cost
About 0.2-0.4 s per Leg A draw, and 0.05-0.35 s per classifier fit. In all, about 15-30 minutes on 4 workers under the Indus compute lock, with `nice -n 20` and the memory guard.
