# Red team of bench_restoration (IIT Hyderabad masked-sign release, Zenodo 24164070)

## Verdict: SURVIVES. None of the four pre-registered kill criteria trips. Two limits belong in any published version: the 36% depends on the near-copy rule, and the transformer rebuild sits right at the 0.5-point bar.

An independent reimplementation reproduces every headline number. Near-copy detection, two trigrams, Hit@k and the bootstrap were all written from scratch; the original `bench.py` was not read or imported.

- **Rebuild (C1) holds, only just for the transformer.** Their deposited probabilities scored against our M77 give KN-3 39.91, transformer 36.99 and blend 40.77 Hit@1, against their reported 39.56, 37.49 and 40.84. The gaps are +0.35, **−0.498** and −0.07 points. The transformer passes the 0.5-point bar by 0.002, about 7 of 1,403 positions where our M77 reading probably differs from theirs.
- **Leakage (C2) holds: 107 of 296 test texts (36.1%)**, the same count as the original. That is one edit (texts of 4+ signs), an exact copy, or a contained copy of 3+ signs, matched against the 1,282 training-pool texts. 20 are exact copies. The bar was 30-42%.
- **The tie (C3) holds.** On the 189 clean texts (875 positions), the transformer scores 28.5% Hit@1 and my Kneser-Ney trigram 30.3%: a difference of −1.8 points (95% CI −4.5 to +0.8, one-sided p = 0.92). The kill bar was +3. The blend minus my trigram is +0.2 (CI −1.5 to +1.9). Against a Witten-Bell trigram (28.0%) the transformer is +0.5 (CI −2.8 to +3.5). So "ties a trigram" is the right wording, and "loses to a trigram" would not be.
- **Inflation (C4) holds.** The blend scores 57.8% on leaked texts and 30.5% on clean ones, a gap of 27.3 points (the kill bar was ≤ 5). This is not a length effect: leaked texts average 4.9 signs and clean texts 4.6.
- **Their split is random by object, and the leakage is typical of such a split.** Their documented rule, `sha256("ebuds:"+object_id) % 5` (validation `sha256("ebuds-val:"+…) % 10 == 0`), reproduces 1,585/1,585 fold and split labels. Over 200 alternative object-hash splits, the leaked share has a median of 36.0% (95% range 31.3-41.5%), and theirs falls at the 51st percentile. So 36% is not bad luck: any random object-level split of M77 leaks this much, because moulded-tablet and formula copies sit on different objects. A split by text family gives 0 by construction.

## Sensitivity (descriptive, pre-registered)

| near-copy rule | leaked texts | share | clean Hit@1 tf / blend / their KN-3 / my KN-3 | tf − my KN-3 (95% CI) | blend leaked − clean |
|---|---|---|---|---|---|
| exact only | 20 | 6.8% | 37.1 / 41.0 / 40.2 / 40.5 | −3.4 (−5.6, −1.1) | −5.4 |
| exact + contained | 89 | 30.1% | 31.3 / 33.5 / 32.6 / 33.0 | −1.7 (−4.3, +0.9) | +22.7 |
| ≤1 edit, no containment | 56 | 18.9% | 33.1 / 36.7 / 35.8 / 36.1 | −3.0 (−5.3, −0.5) | +24.3 |
| **≤1 edit + contained (primary)** | **107** | **36.1%** | **28.5 / 30.5 / 29.7 / 30.3** | **−1.8 (−4.5, +0.8)** | **+27.3** |
| ≤2 edits, no containment | 113 | 38.2% | 29.0 / 32.3 / 31.5 / 31.6 | −2.6 (−5.4, +0.1) | +23.0 |
| ≤2 edits + contained | 148 | 50.0% | 25.0 / 26.5 / 25.4 / 25.9 | −0.9 (−3.9, +2.2) | +27.6 |
| primary, Parpola list | 107 | 36.1% | same as primary | −1.8 (−4.5, +0.8) | +27.3 |
| primary, fish lumped | 128 | 43.2% | 26.8 / 29.5 / 29.1 / 29.5 | −2.6 (−5.5, +0.3) | +24.6 |
| primary, all lumps | 147 | 49.7% | 25.2 / 27.7 / 27.5 / 28.0 | −2.8 (−5.9, +0.3) | +25.4 |
| primary, image-merged 240 | 136 | 45.9% | 27.6 / 29.9 / 29.5 / 30.5 | −2.9 (−6.0, +0.1) | +22.6 |

- **The leakage share depends on the rule.** It ranges from 7% (exact copies only) to 50% (two edits, or a coarser sign list). The number 36% belongs to the one-edit-or-contained rule and should always be quoted with it. Every rule that admits near copies, not just exact ones, puts 30-50% of test texts in "leaked".
- **The tie does not depend on the rule.** Under all 10 definitions the transformer is at or below my trigram (−0.9 to −3.4 points). The pre-registered flag (transformer > +3 with CI above 0 under any variant) never fires. Under two definitions the trigram is significantly *better*.
- **Exact copies alone do not inflate scores** (−5.4). These 20 texts average 2.95 signs, which leaves almost no context. The inflation comes from one-edit and contained copies of longer texts.

## All models, all positions and clean positions (primary rule)

| model | all Hit@1 | clean Hit@1 | clean Hit@5 | clean MRR | leaked Hit@1 |
|---|---|---|---|---|---|
| their KN-3 | 39.9 | 29.7 | 50.6 | 0.397 | 56.8 |
| their transformer | 37.0 | 28.5 | 48.2 | 0.379 | 51.1 |
| their blend | 40.8 | 30.5 | 51.9 | 0.409 | 57.8 |
| my KN trigram (D=0.75, whole-text score) | 42.2 | 30.3 | 52.5 | 0.408 | 61.9 |
| my Witten-Bell trigram | 40.4 | 28.0 | 49.6 | 0.384 | 61.0 |
| unigram | 10.5 | 8.2 | 20.6 | 0.157 | 14.2 |

The original bench reported 29.8 for its trigram on clean texts. My KN trigram gives 30.3, and my Witten-Bell trigram 28.0. The smoothing choice moves clean Hit@1 by about 2 points, which is the size of every neural-vs-n-gram difference here.

## Hypotheses

| claim | kill criterion | result | verdict |
|---|---|---|---|
| C1 rebuild within 0.5 pts | any model off by > 0.5 | max 0.498 (transformer) | survives, marginal |
| C2 36% (107/296) leaked | share outside 30-42% | 36.1% (107/296) | survives (rule-dependent: 7-50%) |
| C3 transformer ties trigram on clean | tf − trigram > +3 | −1.8 (CI −4.5, +0.8) | survives, robust to all 10 rules |
| C4 leaked texts inflate scores | blend gap ≤ 5 | +27.3 | survives |
| split random by object | descriptive | rule reproduces 1,585/1,585; 36% = median of random object splits | confirmed |

Tests run: 4 kill criteria, 4 primary bootstrap CIs, 10 sensitivity bootstraps (descriptive). The planted control in `--smoke` (a synthetic corpus with 87 planted copies) recovered 87/87 under the primary rule.

## Wording for publication
- Say "36% (107/296) of test texts have a near copy (≤1 sign edit or contained) in training". Do not say "36% are copies": exact copies are 7%.
- Say "the transformer does not beat a trigram on clean texts (−1.8 points, CI −4.5 to +0.8)". The ±2-point spread across trigram smoothings means it ties; it does not lose.
- Say "a random split by object leaks this much on any draw (31-41%)". That frames the issue as a split design choice, not a mistake specific to this release.
- The rebuild is faithful, but the transformer margin is 0.498 points. Say "within 0.5 points", not "within 0.4".

## Caveats
- The truth comes from our M77 transcription. About 7 positions likely differ from the authors' readings, and this cannot be checked without their corpus.
- Their models were not retrained on a family-clean split. Clean-subset scoring is leakage-free only because clean test texts have no near copy in training. Clean texts are not a random sample (under the primary rule they are slightly shorter), so their absolute accuracy is not a random-split accuracy.
- The tie means "no detectable gain above about 3 points" (CI half-width ~2.7). A smaller neural advantage cannot be excluded.

## Next
Nothing new is needed for publication. If the retrain in `experiments/bench_restoration/retrain.py` (another agent, running) reports, check that its family-clean numbers fall inside the CI above.

Files: `rt.py` (sha256 in `docs/prereg/HASHES.txt`), `results.json`, `results_smoke.json`, `ledger_rows.csv`. Prereg: `docs/prereg/redteam_bench_restoration.md`.
