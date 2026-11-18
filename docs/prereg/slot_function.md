# Pre-registration: slot_function (two tests from the 2026 survey, ideas 1 and 2)

Written 2026-11-18 (UTC) by agent `paper`, before any outcome is computed. Only sample sizes have been counted. Source ideas: `experiments/survey_2026/SURVEY.md` ranks 1 and 2 (Born et al. 2022 header method, https://aclanthology.org/2022.emnlp-main.620.pdf; Rao 2018, https://arxiv.org/pdf/1812.00049).

Common data rules: distinct texts only; line breaks removed; reading order as stored; a text is usable if `complete` is true, it has no `#`, and it has at least 3 signs. M77 split = `dev_heldout(version=2)`. ICIT signs are Wells signs; the M-W bridge is `sources/shaunmortal_indus/data/bridge_WM.json`. Code: `experiments/slot_function/sf.py`, hashed with this file.

## Test A: which slot carries the object-type signal?

Hypothesis (Born et al.: a header or closing slot marks the document type; Rao 2018: a terminal slot marks function). README #6 shows the whole text predicts object type. A asks where.

- Classes: SEAL vs LABEL. ICIT: SEAL = type starting `SEAL`; LABEL = `TAB:B`, `TAB:I`, `TAB:C`, `TAG`, `ROD`, `BNGL`, `POT...`. M77: seal vs {miniature tablet, copper tablet, pottery graffito, ivory/bone rod, bronze implement}. Sealings are excluded in both (M77 "sealing" mixes impressions and moulded tablets).
- Features: the sign in one slot (INIT = first sign, TERM = last sign, MID = bag of the other signs), one-hot, signs seen fewer than 2 times in training -> UNK, plus text-length bins (3, 4, 5, 6+). A LEN-only model is the baseline. Model: logistic regression (C = 1). Score: AUC for LABEL.
- **Primary data: ICIT**, 5-fold CV stratified by class (seed 0). **Second check: M77**, fit on dev, score on held-out.
- **A1 (prediction):** AUC_TERM − AUC_INIT ≥ 0.03, and the 95% bootstrap CI of the difference (2,000 resamples of test texts, pooled CV predictions) excludes 0.
- **A2:** AUC_TERM is above the 95th percentile of a within-text-shuffle null (sign order permuted inside every text, train and test, refit; 200 runs for ICIT, 500 for M77). This asks whether the last slot carries more than a random sign of the same text.
- **Planted check (gate, ICIT, run first):** on a within-text-shuffled ICIT copy, replace the last sign of 15% of LABEL texts with a new sign PLANT. A1's rule must fire in ≥ 80 of 100 plants. With the plant in the first slot instead, A1's rule must fire in ≤ 5 of 100. On unplanted shuffled copies, A1 must fire in ≤ 10 of 100. If the gate fails, A is UNTESTABLE.
- Verdict: SUPPORTED if A1 and A2 hold on ICIT and A1's difference has the same sign on M77 held-out; WEAKENED if they hold on ICIT only; REFUTED if AUC_TERM − AUC_INIT ≤ 0 on ICIT. Also reported: AUC_MID and AUC_LEN.

## Test B: human-figure signs as counted kinds of people (Rao 2018)

- H = M1-M46 (every human-figure drawing in Mahadevan's list; checked by eye on the sign drawings, not blind). Sub-class HT = M18-M46 (a figure holding or beside an object). NUM = stroke numerals M86-M122, excluding M99 (connective) and M100 (ambiguous).
- **B1 (prediction, primary data = M77 held-out, all usable runs of ≥ 2 signs):** r_H = share of H tokens, not run-initial, whose preceding sign is in NUM. Control: 1,000 random sets of non-H, non-NUM signs, each H sign matched to a control sign in the same dev-frequency decile and the same tercile of text-final share (dev). Prediction: r_H / mean(r_ctrl) ≥ 2 and r_H ≥ the 95th percentile of r_ctrl. Dev is reported too, as exploratory.
- **B2 (prediction, primary data = ICIT, H mapped through the bridge):** H tokens make up a larger share of tokens on tablets (TAB:B, TAB:I) than on seals (SEAL*). Mantel-Haenszel odds ratio, stratified by site, ≥ 1.5, with p < 0.05 by permuting object type among texts within site (2,000 runs). M77 is reported as descriptive.
- **Planted check (B1, run first):** on a within-text-shuffled held-out copy, pick one random matched control set as pseudo-H. Before 30% of its non-initial tokens, replace the preceding sign with a random NUM sign. B1's rule (against the other control sets) must fire in ≥ 80 of 100 plants. If not, B1 is UNTESTABLE.
- Verdict per sub-test: SUPPORTED (prediction met), WEAKENED (direction right, threshold missed), REFUTED (wrong direction or ratio ≤ 1). HT is reported as a secondary breakdown.

## Multiple tests

Four confirmatory tests (A1, A2, B1, B2). Holm correction over the four p-values is reported next to raw values.

## Compute

Seconds to minutes; background priority under the shared compute lock.
