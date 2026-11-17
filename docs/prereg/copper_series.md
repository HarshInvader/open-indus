# Pre-registration: are Mohenjo-daro copper tablets a calendrical series, tallies, or amulets?

Registered 2026-11-15, area `experiments/copper_series/`. Written AFTER building the type table (`build_types.py`, `types.csv`; I have seen the type list and the object count per type) and BEFORE computing any statistic below (no Gini, richness estimate, graph statistic, numeral test or seal correlation has been computed). Script `tests.py` will be hashed with this file in `docs/prereg/HASHES.txt` (tag `copper_series`) before it is run.

## Data and units

- Tablets: `experiments/logograms/copper_tablets.csv` (M77 IM77 line file, 135 objects; ICIT TAB:C, 190 objects), re-verified: all 135 M77 legends match `data/m77_texts.jsonl` (object_type 'copper tablet'); all 190 ICIT ids found (189 Mohenjo-daro, 1 Kalibangan).
- **Type** = legend family under a strict rule (`build_types.py`): complete legends join if both have >= 4 signs and edit distance <= 1, or a >= 4-sign legend is contained in another, and their M77 (fs80) pictures do not conflict. Fragments join only an unambiguous type. One manual merge (MD 3302/3335/3364 = M-513..515, same faces read differently by M77 and ICIT). Result: **37 strict types** (36 lumped: types that share a non-formula bigram and the modal picture are merged). 23 of 325 tablet records are unassigned fragments and are excluded from counts.
- **Count per type** = n_est = max(M77 objects, ICIT objects). The two corpora overlap in objects but share no ids, so max is a conservative union. Sensitivities: n_sum (upper bound), M77 only, ICIT only, lumped types.
- **Formula signs** (copper register closers, context Q2): M342, M169, M407. "Content signs" = all other signs.
- **Numerals**: signs with role NUMERAL(short/tall) in `experiments/functional_reading/lexicon.csv`, with its stroke values.
- Unit is the type (a legend = one distinct text), so the "distinct texts" rule holds: each type counts once in every structure test; objects are used only for frequency tests, where object counts are the point (mass production).

## Hypotheses and pre-registered predictions

### H1 calendrical / ritual series (closed cycle issued in rotation)
Candidate cycle sizes K in {6, 7, 12, 13, 27, 28}.
- **H1a closure.** Good-Turing sample coverage C = 1 - f1/N >= 0.90 AND the Chao1 95% CI for the number of types contains at least one K. (f1 = singleton types, N = typed objects.)
- **H1b evenness.** The Gini coefficient of observed type counts lies inside the central 95% of Gini values simulated from N draws uniform over K types (observed types only, K in the set, best K reported) for at least one K. Refuted for evenness if outside for all K. Secondary: likelihood comparison of uniform-K vs a Zipf law p_i ∝ i^-s over 100 possible types with s fitted by maximum likelihood on the rank-frequency vector (reported, not counted).
- **H1c ring.** Graph: nodes = types with n_est >= 2; edge if two legends share >= 1 content sign. H1 predicts (i) a Hamiltonian cycle exists AND (ii) degree coefficient of variation is LOWER than under the null (one-sided p < 0.05). Null: content-sign tokens of all type legends permuted across types (preserving legend lengths, sign frequencies and formula signs in place), 2,000 permutations. Also reported: modularity of the observed graph vs null (a cluster structure is the alternative to a ring).
- **H1d numerals as position.** Among types carrying a stroke numeral, values are all distinct across types (no two types share the same numeral value) AND the set of values is contiguous from 1 (a run 1..m with m >= 4). Null for distinctness: numeral tokens permuted across types, 10,000 permutations; H1 needs distinct-value count in the top 5%.
- H1 **supported** only if H1a, H1b and H1c all pass. **Refuted** if H1b fails at every K and H1c(ii) fails (with planted ring power >= 0.5). Otherwise inconclusive.

### H2 tokens / tallies of a commodity or entitlement
- **H2a numeral contrast.** Pairs of types at edit distance 1 (substitution) whose differing sign is a numeral or the unit M190 are more frequent than expected from the share of numeral tokens among content-sign tokens (binomial, one-sided p < 0.05).
- **H2b skew.** Type counts are skewed: Gini above the uniform-K 97.5th percentile for every K (this is the complement of H1b).
- **H2c value-frequency.** Among types with a numeral, Spearman rho between numeral value and n_est is non-zero (two-sided p < 0.05). Direction not predicted (cheap units common, or large lots common).
- H2 **supported** if H2a and H2b pass. **Refuted** if H2a fails with >= 3 numeral-bearing minimal pairs possible (power note) and numerals are on fewer than 25% of types.

### H3 amulets naming deities / protective formulas
- **H3a fixed pairing.** Within types with >= 2 pictured objects (M77 fs80 only), the modal picture covers >= 80% of pictured objects (pooled), above the null where pictures are permuted across pictured M77 tablets (one-sided p < 0.05, 10,000 permutations).
- **H3b popularity.** Across coarse picture classes, Spearman rho between number of copper objects (M77 fs80) and number of M77 seals with that class is > 0, one-sided p < 0.05.
- **H3c picture-text.** Types with the same coarse picture share more content signs (mean Jaccard) than types with different pictures, permutation of picture labels across types, one-sided p < 0.05.
- H3 **supported** if H3a and H3b pass. H3a alone (fixed pairing without popularity tracking) = "type emblem", not specifically amulet.

## Tests counted
H1a, H1b, H1c(ii), H1d, H2a, H2b, H2c, H3a, H3b, H3c = 10 tests. Bonferroni alpha 0.005 reported alongside raw p; verdict rules above use the stated thresholds and Bonferroni is applied to any test called "supported".

## Power (computed and reported)
- H1b/H2b: probability that the evenness test rejects uniform-K when counts come from a Zipf(s=1) law over 40 types, and that it accepts uniform-K when counts really are uniform-K, at the observed N.
- H1c: planted ring. Replace one content sign in each node's legend by a ring token shared with its successor (cycle over all nodes) and rerun; power = share of 200 plants with HC present AND degree-CV p < 0.05.
- H1a: coverage and Chao1 behaviour at observed N under uniform-K draws.

## Structural comparison (descriptive, not counted)
Number of types, number of minimal pairs, and shared-element structure compared with: Babylonian month names (12 + intercalary), the 27/28 nakshatra list (3 pairs differ only by "former/latter": Phalguni, Ashadha, Bhadrapada), the Chinese 12-animal cycle, 7-day week, 6 Indian seasons.

## Frozen prediction for new finds
Newly published Mohenjo-daro copper tablets (CISI vol. 3+, excavation reports) will belong to an already known strict type with probability within +-0.15 of the Good-Turing coverage C computed here. A closed calendrical series predicts >= 0.90.

## Known risks
- Mould/batch clustering: copies of one type may be cast and buried together, inflating unevenness even under rotation. Unevenness therefore weakens H1 but does not alone exclude a series of which batches survive unevenly; stated in results.
- n_est = max undercounts the union; sensitivity analyses bracket it.
- ICIT picture field is coarse; all picture tests use M77 fs80.
- Small n: 37 types, ~20 with >= 2 objects.

## Amendment before running (2026-11-15, still no statistic computed)
1. The type table already shows 37 strict types, more than the largest candidate K (28). A one-type-per-position cycle is therefore impossible on the strict table as it stands. H1a/H1b are run as written, and in addition (counted as the same tests, reported side by side) on the **core types** (n_est >= 2), the set a series analysis would use if singletons were damaged or variant copies. H1 passes H1a/H1b if either the full or the core table passes (the more lenient reading, which favours H1).
2. H1d statistic corrected: permuting numeral tokens leaves the number of distinct values unchanged, so the statistic is the number of **type pairs sharing a numeral value** (collisions). H1 needs collisions in the bottom 5% of the permutation null (and contiguity 1..m, m >= 4).
3. H1c uses the most frequent complete spelling of each type (column `legend` of types.csv).
