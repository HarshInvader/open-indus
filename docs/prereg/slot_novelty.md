# Pre-registration: slot_novelty (Fable plan 5, tests T2 and T3)

Registered 2026-11-15 in `experiments/slot_novelty/`, after dev-only exploration and controls (`dev_explore.py`, `power_t2.py`; logs `dev_t2.log`, `dev_t3.log`, `dev_power_t2.log`) and BEFORE any statistic on M77 held-out (`dev_heldout(version=2)`) or ICIT new-site seals. Code hashes (`sn_lib.py`, `confirm.py`) and this file are in `docs/prereg/HASHES.txt` (tag slot_novelty).

## Disclosure: what was already seen
- All T2 and T3 statistics on M77 **dev** seals (all sites, MD, Harappa); Ur III seal legends (positive control, word and sign level, merged to the Indus inventory); shuffled-sign negative control; planted-template power at held-out sizes.
- Held-out and ICIT: only the NUMBER of texts per site and length stratum (all sites 276: L3 62, L4 40, L5 65, L6+ 109; MD 221; Harappa 29; ICIT new sites 129).
- Lesson carried from core_genre: no grammar-defined slots or cores. Slots are positions only. Productivity is compared at equal N (one token per text per slot) so the medial slot is not favoured by having more tokens; rarity is inventory-relative.

## Data
Distinct M77 seal texts (`object_type == 'seal'`), `complete` and no `#`, line breaks dropped, length >= 3 signs. Held-out = v2 (text families). Secondary independent data: ICIT seals from sites absent from M77 (Wells numbers, no bridging needed: all statistics are within-corpus).

## T2: where the novelty lives (Baayen productivity)
- Slots: opener = first sign; closer = last sign; medial = one interior sign drawn at random per text (averaged over draws). Strata by length 3, 4, 5, 6+.
- P = n1/N per slot within a stratum (n1 = signs used exactly once in that slot in that stratum; N = texts in the stratum, equal for all three slots). PRIMARY statistic: pooled over strata, P_slot = sum n1 / sum N; share = slot n1 / all slots' n1. CIs: 1,000 subsamples of 80% of texts without replacement (bootstrap duplicates would destroy hapaxes).
- Rare vs common: common = most frequent signs covering 80% of seal tokens (M77: all M77 seals; ICIT: all ICIT new-site seals). Novel content of a slot is split into (a) new combinations of common signs vs (b) containing a rare sign.
- Labels (pooled): **single** = top-slot share >= 0.50 AND P_top/P_second >= 1.5 AND CI lower bound of that ratio > 1.0; **even** = P_max/P_min < 1.5; otherwise **mixed**.
- Calibration (dev): shuffled-within-text negative control labels 'even' 50/50 at n=276; Indus dev labels 'mixed' 100/100 at n=276 (P opener 0.22, medial 0.21, closer 0.11). Ur III legends (word level and merged to the Indus inventory) label 'mixed' with medial as the closed slot (two name slots, owner and father). Labelled Ur III slots: names carry the novelty (content novel 0.58-0.63 vs kin 0.00, servant 0.01, title 0.37).

Hypotheses (held-out all sites = PRIMARY; MD held-out and ICIT new sites = replication):
- **H2a (plan prediction).** Pooled label = single -> SUPPORTED (one slot carries most novelty); even -> REFUTED; mixed -> NOT SUPPORTED (novelty in two slots). Dev expectation: mixed.
- **H2b (dev-derived).** The closer is the closed slot: lowest P is the closer, min(P_opener, P_medial)/P_closer >= 1.5, CI lower bound > 1.0. Dev pass rate at held-out size 1.00 (all), 0.95 at n=129.
- **H2c (dev-derived).** Opener and medial are equally productive at sign level: the top two slots are opener and medial and their ratio < 1.5.
- **H2d (dev-derived, decomposition).** Among 2-sign windows (texts >= 4 signs), novel interior windows are more often made only of common signs than novel start or end windows (dev 0.55 vs 0.42 / 0.35): the middle innovates by recombination, the edges by rare signs.
Each H is a threshold decision on PRIMARY; replication sets reported, no extra correction (4 decisions).

## T3: frame dependency
- Statistic: I(O;C) in bits, O = opener class, C = closer class; classes = the K=8 most frequent openers / closers in the analysed set, rest = OTHER (sensitivity K = 4, 16). Classes fixed from the observed data and reused for nulls.
- PRIMARY null: positional suffix-swap MCMC (for each length L, position k, and sign at k, permute the suffixes after k among texts sharing that sign there). It preserves exactly the length distribution and every positional unigram and bigram count per length, i.e. the whole adjacent chain; so excess MI = opener-closer information not carried through the medial chain (conditional on medial content). 2,000 null samples after burn-in 5 sweeps, thin 2. One-sided p (excess).
- SECONDARY null: fitted MLE bigram chain with START/END (non-positional), sampled exactly at each real length; 1,000 samples.
- Within one site, seals only: MD held-out (n=221) and Harappa held-out (n=29). Holm over the two. Exploratory: ICIT new sites pooled (mixes sites).
- Calibration (dev): size on chain-generated data 0.05 (40 reps). Planted template (top-2 openers force top-2 closers with probability f) at n=220: power 0.20 at f=0.25, 0.82 at f=0.5 (40 reps; recomputed with 100 reps in `confirm.py`, dev data only). Harappa at n=30: power ~0 -> its held-out test is uninformative by design. Ur III legends (word level, n=600): NO excess (p=0.20): in a real formulaic genre the register-specific middle vocabulary carries the frame dependency, so this null absorbs it. Dev results: MD excess small, n.s. (K=8 p=0.13); Harappa dev BELOW the swap null (p=1.0, z about -2.8).
- Decisions: **SUPPORTED** = MD held-out Holm p < 0.05 (excess) and Harappa excess > 0. **REFUTED (no excess beyond the chain, for templates of planted strength f >= 0.5)** = MD p >= 0.05 with power >= 0.8 at f=0.5. Otherwise INCONCLUSIVE. A below-null result is reported two-sided as exploratory.
- Caveat fixed in advance: a null result does NOT show the texts are chains rather than templates, because a template whose registers use their own medial vocabulary is invisible to this test (Ur III control).

## Ledger
Rows `sn_*` in `docs/test_ledger.csv`: 4 T2 decisions, 2 T3 primary tests (family slot_novelty).
