# Pre-registration: what kind of quantity do Indus short-stroke numerals count? (Fable 5.2 plan 2, item E3)

Registered 2026-11-15 in `experiments/numeral_class/`, BEFORE any reference distribution was built or compared with the Indus counts. What was known before writing: the published Indus short-stroke counts (context Q6: M77 1:157, 3:129, 4:61, 5:36, 6:34, 7:67, 8:7, 12:52; peaks 7 and 12), pair_numeral_long F2 (most numeral+sign pairs are fixed formulas), naming_sim (numerals in <=2% of real personal names). What was looked at in the reference sources: file formats only (CDLI ATF notation for numbers, `u4 N-kam`, `mu N-kam`; DAMOS item format; GRETIL Rigveda transliteration; EDH and name lists already on disk). No reference value distribution was tabulated. SHA-256 of this file goes into `docs/prereg/HASHES.txt` (tag `numeral_class`) before `fit.py` runs.

## Question

Which reference class of quantity best reproduces the distribution of Indus short-stroke numeral values?

## Indus data (frozen)

- Values: short-stroke signs from `sources/shaunmortal_indus/data/stroke_signs.json` (`short`), M77. Value 2 (M99/M100/M101) is EXCLUDED (M99 is the connective, M100 is ambiguous). M113 and M123 excluded (unclear). Support S_M77 = {1,3,4,5,6,7,8,9,10,12} (no sign for 11). ICIT replication: W001=1, W003/W013=3, W004/W014=4, W005/W015=5, W006/W016=6, W007/W017=7, W018=8, W019=9, W055=12 (support S_ICIT = {1,3,...,9,12}).
- Unit (primary): every short-numeral token in distinct texts, where distinct = distinct sign sequence within object type (as context Q6). Sites/types from metadata.
- Strata: pooled M77; per site with >= 15 tokens (Mohenjodaro, Harappa, Lothal, Kalibangan, Chanhudaro as available); per object type: SEALS = `seal`; TABLETS = `miniature tablet` + Harappa `sealing` (moulded tablets). ICIT pooled, SEAL, TAB.
- Sensitivity (reported, not decisive): (s1) one token per text (first short numeral); (s2) distinct (numeral sign, following sign) types; (s3) drop tokens inside the known fixed formulas short7+M194/M197, short3+M190/M403/M15, short1+M25.

## Reference classes (frozen list; data rules fixed before tabulation)

Every reference distribution is conditioned on the Indus support (values outside the support are dropped and the rest renormalised). Open-ended classes are fitted in two variants with equal prior weight: EXACT (value v = v) and CEILING (12 means "12 or more": all reference values >= 12 are pooled into 12; values outside the support still dropped).

| class | sub-corpora (each a real sample of the class unless marked model) | variants |
|---|---|---|
| A commodity counts on administrative records | A1 Ur III administrative texts with <= 8 text lines (CDLI); A2 Old Akkadian administrative (CDLI); A3 Proto-Elamite (CDLI, N01/N14 groups); A4 proto-cuneiform Uruk IV/III (CDLI, N01/N14 groups); A5 Linear B (DAMOS, integer after an ideogram or measure sign); A6 CDLI objects typed tag/bulla/docket/label, any period | exact, ceiling |
| B month numbers | uniform over 1-12 (model; a 13th intercalary month changes nothing on S) | one |
| C day-of-month dates | CDLI `u4 N-kam` (all periods) | exact, ceiling |
| D regnal / year numbers | CDLI `mu N-kam` in Middle Babylonian and later periods (Ur III `mu N-kam us2` excluded) | exact, ceiling |
| E numbers inside personal names | E1 Sanskrit names (Monier-Williams persons, numeral first member); E2 Chinese given names (numeral characters); E3 Latin numeral names in EDH (Primus...Decimus, Quintus, Sextus, Septimius/Septimus, Octavius, Nonius, Decimus) | exact |
| F ages | Latin epitaph ages at death, EDH `vixit annis/annos N` | exact, ceiling |
| G ritual/sacred numbers | Rigveda cardinal numerals 1-12 incl. compound first members (GRETIL Aufrecht, frozen regex list in `refs.py`). Sangam: attempted only if a lemmatised corpus is found (Tamil number words are homographs of common words) | exact |
| H generic counts | H1 Benford-type p(v) ~ log(1+1/v); H2 Zipf p(v) ~ v^-a, a uniform on [0,3] integrated; H3 geometric p(v) ~ q^v, q uniform on (0,1) integrated (also stands in for rank/grade ladders and lineage-generation numbers, for which no open data exist) | exact, ceiling for H2/H3 |
| I unit numbering (exploratory extra) | Roman legion numbers in EDH (`LEG N`) | exact |

Age grades / ranks / generation numbers: no open real data located; represented only by the H3 decaying-ladder model. Stated in advance.

## Likelihood

For a real sub-corpus with counts r_v on S, the predictive is Dirichlet-multinomial with alpha_v = r_v + 0.5 (reference sampling uncertainty included). For models, closed form or integration over the parameter prior (grid, 2,001 points). Class marginal likelihood = equal-weight average over its sub-corpora x variants (this penalises classes with many options). BF(X:Y) = class marginal likelihood ratio. Multinomial coefficient cancels.

## Decision rule (frozen)

A class WINS if all hold:
1. Pooled M77: its BF over every other class > 10.
2. Per site: at every site with >= 40 tokens it is top with BF > 10 over the runner-up; at sites with 15-39 tokens no other class beats it by BF > 10.
3. Per object type: same as 2 for SEALS and TABLETS (thresholds by token count as in 2).
4. ICIT pooled: top with BF > 10.

ADEQUACY (posterior predictive check) for the winner, pooled M77: simulate 10,000 Indus-sized samples from the winner's predictive (best variant/sub-corpus by marginal likelihood); statistic G = 2 sum o log(o/e). Adequate if p(G_sim >= G_obs) >= 0.05. Also reported: simulated vs observed share of 7 and of 12.

Outcomes:
- WIN + ADEQUATE: the class narrows what the numerals count (report which).
- WIN + INADEQUATE: relative winner only; no listed class reproduces the distribution -> line closed for these classes (a narrowing only in the sense of the ranking, stated as such).
- NO WIN: line closed.

Number of decisive tests: 1 decision (with 4 conditions + adequacy). Ledger rows tagged `nc_*` in `docs/test_ledger.csv`, mode confirmatory for the decision, exploratory for sensitivities.

## What would change the verdict

A class that fits pooled and per stratum and passes the PPC. Peaks at 7 and 12 are the features most classes are expected to miss; a class with a ceiling at 12 (counts, days) can create a 12 peak but not a 7 peak.
