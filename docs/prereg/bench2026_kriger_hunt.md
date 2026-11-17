# Pre-registration: Kriger & Hunt 2026 "registration code" predictions (board task #6, agent H5)

Written 2026-11-17 before any outcome below was computed. Script: `experiments/bench2026/kh_tests.py` (hashed with this file).

## Source claims (Zenodo 19103880 abstract; Zenodo 20040472 abstract; full PDFs blocked by Zenodo 403)
On 179 Mohenjo-daro unicorn seals (their corpus: mayig/indus-valley-script-corpus):
- C1 98.3% of inscriptions unique vs a permutation null of 91.2% (p < 0.001), read as "unique account numbers".
- C2 positional entropy differs by position (Friedman p = 0.005): constrained edges, diverse middle = "structured code, not language".
- C3 stroke numerals (15.4% of tokens) concentrate in the penultimate position; "2" is 66.9% of numerals.
- C4 near-duplicate pairs (differ by one sign) differ only in middle positions, never at edges (binomial p = 0.008).
- C5 (paper 3) duplicate seals are replacement issuances to the same holder.

## Populations
- U (primary): M77 objects with site Mohenjodaro, object_type seal, field symbol description containing "Unicorn", text complete, no `#`, line breaks removed. Object level for K1; distinct texts for K2-K4.
- S (replication): all other M77 seals (not in U) meeting the same cleaning.
- UR (linguistic comparator): Ur III seal legends (`experiments/identifiers/data/ur3_occ.jsonl`), one per seal_id, words flattened in reading order; distinct legends.
Sign numerals: `experiments/numeral_grammar/common.py` M_NUM (M99 is flagged there as the connective "2").

## Tests (all one-sided as stated; 2,000 null draws each; alpha 0.05, Holm over the 4 primary tests on U)
- K1 uniqueness. Statistic: share of objects whose text no other object in the population carries. Nulls: N1 tokens of the population redealt at random into the real text lengths; N2 positional redeal (signs permuted among texts of the same length, within each position). Code prediction: real share >= null 95th percentile. Expected under prior project work (joyboseroy, 10b.4): real share BELOW null (formulas repeat). Verdict: "C1 replicated" if real > N1 95th pct; "C1 reversed" if real < N1 5th pct.
- K2 positional entropy. Texts of length 5 (as in their 5-position Friedman). Statistic: mean entropy of positions 2-4 minus mean of positions 1 and 5. Null: within-text shuffle. Expected: positive and significant (already known: openers/closers). Specificity check: same statistic on UR legends of length 5 words... UR legends are short in words; use UR legends with >= 3 words, positions first/middle/last. If UR shows the same sign of effect (significant), C2 is declared non-specific (does not separate code from a known linguistic name genre).
- K3 numerals. (a) share of numeral tokens (M_NUM, all classes) at the penultimate position vs within-text shuffle null; (b) share of value-2 among numeral tokens with and without M99. Verdict on "2 dominates": if value-2 share excluding M99 < 0.30, C3's "digit 2" is declared a connective/formula artefact, not a count distribution.
- K4 near-duplicate locus. Pairs of distinct texts of equal length L >= 3 at Hamming distance 1. Statistic: share of such pairs whose differing position is first or last. Null N2 (positional redeal, keeps every per-position distribution). Code prediction (C4 beyond positional entropy): real edge share < N2 5th pct. If real edge share sits inside the N2 interval, C4 is explained by positional entropy alone and does not support a serial-code reading. Same on UR (comparator) and on S.
- Planted control for K4 (run before the real U statistic is read; reported regardless): synthetic corpus = one N2 draw of U plus k extra texts, each a copy of a random text with one middle position re-drawn (serial-number variants), k = 10 and 25. Power = share of 200 planted corpora where the statistic falls below the N2 5th percentile. If power < 0.5 at k = 25, K4 is declared low-power.
- C5 is not re-tested: 10b.4 (repeats cross-site at random, R 0.89 vs Ur III 0.18) and 10b.9 already bear on it; cite.

## What would falsify the registration-code reading here
K1 reversed (real less unique than N1) and K4 inside N2 interval together mean the two signature results are what any positionally structured corpus with formulas gives.
