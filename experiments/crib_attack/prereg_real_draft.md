# DRAFT pre-registration: crib attack on the real foreign corpus (board task #4). NOT HASHED.

Hash this only after (a) task #1's corpus and #2's per-site name shortlists exist and (b) the planted re-check below passes at the real n.

1. **Data.** Distinct texts of Indus-sign objects found outside South Asia (task #1), with person and number signs marked (typology W90-175, W1-59) but not removed. Name lists: per find-site shortlists from #2, syllabified, each ≤ 200 spellings; the full Ur III list is used only as a contrast.
2. **Planted re-check (gate).** Run `experiments/crib_attack/run_planted.py` with the real n, the real text lengths and the real shortlist sizes, and the scorer switched to E (exact full-name matches of 3 or more signs, search optimising E). Proceed only if power ≥ 0.8, wrong-language FPR ≤ 0.2 and median precision ≥ 0.5.
3. **Statistic.** E_best on the real texts against: (a) 200 sign-shuffled versions of the same texts (primary, one-sided p); (b) the same attack with a wrong-language list of equal size (Linear B names); (c) 200 random samples of home Indus texts matched for length and n.
4. **Decision.** Supported only if p(a) < 0.05 AND E_best beats the 95th percentile of (b) and (c). Every recovered sign value is then frozen as a prediction for new foreign finds before anything else is read.
