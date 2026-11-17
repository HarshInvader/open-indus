# T5 Site signal in non-repeated seal texts (Fable plan 5, test 5)

Pre-registered: `docs/prereg/site_signal.md`, hashed with `lib.py` and `s1_confirm.py` in `docs/prereg/HASHES.txt` (tag `site_signal`) before the final run. Only data sizes and a run with shuffled labels had been seen before that. Ledger rows `ss_p1`..`ss_p5` are in `docs/test_ledger.csv`.

## Findings first

1. **The signs on a unique seal do not tell you which city it came from. Mohenjo-daro and Harappa seals look like draws from one pool.**
   - The sample is 621 seals whose text never repeats and has no near-copy anywhere in ICIT.
   - A classifier trained on sign and sign-pair features predicts site no better than chance: AUC 0.49, against a permutation null of 0.50 (95th percentile 0.56); p = 0.61 (P1).
   - Exploratory power check, run after the frozen test: the same pipeline catches a planted local stock of 20 signs, swapped into 20% of Harappa tokens, 92% of the time. Swapped into 10% of tokens, it catches it 22% of the time.
   - So a site difference of that size is excluded for the whole text. A subtler one is not.
2. **The pre-registered open-slot test (P2) is null too, but too weak to refute anything.**
   - Medial signs, carving variants merged, period-stratified: AUC 0.51 vs null 0.50, p = 0.44.
   - Planted power is only 0.12 at q = 0.2 (0.39 at q = 0.3). Only 60 dated Harappa seals with 3 or more signs exist.
   - Training on one period band and testing on the other (P3) is null: mean AUC 0.47, p = 0.72.
   - The four-site classifier (P4: Mohenjo-daro, Harappa, Dholavira, Lothal) is at chance: balanced accuracy 0.24 vs 0.25, p = 0.82.
   - All Holm p = 1.0. **Formal verdict under the frozen rule: INCONCLUSIVE.** The refute branch needed P2 power of at least 0.8 and got 0.12.
3. **The only hints of a local signal sit in the frame slots and in carving variants, not in the open slot.** All of these are exploratory and uncorrected, from about 24 secondary tests.
   - **Closer, raw Wells signs:** AUC 0.58, p = 0.018. Merging carving variants (A1) removes it (0.52, p = 0.26).
     - It comes from Harappa preferring closers W405 (6.5% vs 1.6%) and W154 (4.7% vs 1.2%).
     - W154 is a Wells variant of the M12/M15 person sign; W405 is in the ambiguous W390/W405 cup group.
   - **Leaf sign variants:** Harappa uses variant W806 in 11 of 13 cases, against 21 of 40 at Mohenjo-daro (p = 0.053).
     - This is the same "Harappa W806 W154" local item that the toponyms test found.
     - So that local item is most likely a carving habit, not sign choice.
   - **Frame (opener + closer), period-stratified, A1:** AUC 0.62, p = 0.022. The opener alone gives 0.59, p = 0.056. This is weak, uncorrected and not pre-registered.
   - **Medial slot, every variant, every allograph level:** AUC 0.46-0.48, at or below the null.
   - **Drivers:** no single medial sign differs by site after BH (0 at q < 0.10). The biggest leave-one-out AUC drop is 0.02 (W390 at Mohenjo-daro, 26 vs 1).
4. **Time inside one city is a bigger signal than the difference between cities.**
   - Within Mohenjo-daro, earlier vs late seals are told apart above chance: AUC 0.61, p = 0.02, all features.
   - Mohenjo-daro vs Harappa, on the same kind of features, is at chance.
   - Within Harappa, time is not detectable (0.56, p = 0.27; few seals).
5. **Beta diversity (P5, low power): each site pair differs slightly more than sampling from one pool predicts.**
   - Rarefied Bray-Curtis is 0.50-0.56, against 0.51 for the pooled null; mean excess +0.028.
   - The exception is Dholavira-Lothal, the closest pair at 258 km, which sits below the null.
   - Mantel r against distance is 0.90 for Bray-Curtis (p = 0.042, the smallest possible value with 24 permutations) and 0.52 for Jaccard (p = 0.17). Both rest on 4 sites and 6 pairs.
   - With 6 sites (at least 20 seals each, 15 pairs) the correlation vanishes: r = 0.02, p = 0.48.
   - No distance decay can be claimed.

**Reading.** Unique seal texts draw on one pan-Indus vocabulary with no detectable city-specific stock in the open slot. A whole-text city signal of moderate size (a 20% local stock) would have been seen and was not. The scraps of locality that do show sit at the closer and in carving variants (W154, W806), which are scribal or workshop habits rather than local names. This matches the earlier results that repeats are placeless (identifiers), place names don't travel (toponyms), and seal size follows the variant (redteam_rank). It counts against readings of the open slot as local personal names, but formally the open-slot test is underpowered. Further support for the open-slot claim would need more dated seals from Harappa or other sites, not more analysis.

## Data

- Sample: ICIT seals, complete, unbroken (1,606).
- Exclusions:
  - exact text found on any other ICIT object (any type);
  - a direct near-copy of any other distinct ICIT text under `corpus/build.py _close` (<= 1 edit with both >= 4 signs, or a >= 3-sign text contained in another).
- Strict set: 802 seals (Mohenjo-daro 489, Harappa 132, Dholavira 33, Lothal 30, Chanhu-daro 25, Kalibangan 24).
- Allograph levels:
  - A0: raw Wells.
  - A1: Wells splits of one Mahadevan sign merged (e.g. W704/705/706 = M336), plus shaunmortal M5 image + distribution allograph pairs; 20 groups, 45 signs.
  - A2: A1 plus the fish family and tall-1/tall-2.
- Period bands:
  - late = MD Late, HARP 3C, Vats Strata I-III;
  - earlier = MD Early/Intermediate, HARP 3A-B, Vats Strata IV-VII.
- Classifier: Bernoulli naive Bayes on presence features, stratified group 5-fold x 3, AUC.
- Null: site labels permuted (within band where stated), with the full CV re-run, 1,000 times for P1-P4.

## Pre-registered tests

| id | test | result | null mean / q95 | p (Holm) | verdict |
|---|---|---|---|---|---|
| P1 | MD vs Harappa, all features, A0, n = 611 | AUC 0.490 | 0.500 / 0.560 | 0.61 (1.0) | null; exploratory power 0.92 at q = 0.2 |
| P2 | MD vs Harappa, medial, A1, within-band null, n = 270 (60 H) | AUC 0.509 | 0.502 / 0.584 | 0.44 (1.0) | null; power 0.08 / 0.12 / 0.39 at q = 0.1 / 0.2 / 0.3 |
| P3 | train one band, test the other, medial A1 | 0.536 (earlier to late), 0.412 (late to earlier); mean 0.474 | 0.500 / 0.580 | 0.72 (1.0) | null |
| P4 | 4 sites >= 30, all features A1 | balanced accuracy 0.241 (chance 0.25) | 0.250 / 0.267 | 0.82 (1.0) | null |
| P5 | Bray-Curtis / Jaccard vs distance, 4 sites | Mantel r 0.90 / 0.52 | 24 permutations | 0.042 / 0.17 | low power; not replicated with 6 sites (r 0.02) |

Decision: P2 fails, P1 fails, and P2 power is 0.12 < 0.8, so the result is **INCONCLUSIVE** (not REFUTE).

## Secondary (MD vs Harappa, >= 3 signs, n = 532, 500 permutations; uncorrected)

| slot | A0 AUC (p) | A1 AUC (p) | A2 AUC (p) | A1 period-stratified |
|---|---|---|---|---|
| opener | 0.472 (0.69) | 0.458 (0.77) | 0.454 (0.83) | 0.589 (0.056) |
| closer | **0.577 (0.018)** | 0.519 (0.26) | 0.555 (0.07) | 0.486 (0.52) |
| frame | 0.562 (0.07) | 0.548 (0.09) | 0.579 (0.020) | **0.616 (0.022)** |
| medial | 0.480 (0.65) | 0.466 (0.77) | 0.460 (0.83) | (P2) 0.509 (0.44) |
| all | 0.507 (0.43) | 0.495 (0.54) | 0.490 (0.60) | 0.505 (0.52) |

Other checks:
- Logistic regression for P2: AUC 0.527, p = 0.32.
- Robustness, one seal per family: P1 0.51 (p 0.40), P2 0.51 (p 0.42).
- Robustness, families kept and grouped: P1 0.536 (p 0.068), P2 0.522 (p 0.31).
- M77 (Mahadevan list, same objects): all 0.488 (p 0.58), medial 0.467 (p 0.79).
- Six sites with >= 20 seals: balanced accuracy 0.168 vs 0.167, p = 0.42.

## Caveats

- **Harappa is small.** It has 132 strict seals, 60 dated with >= 3 signs. The open-slot test cannot exclude a modest local stock.
- **Strict exclusion removes 526 non-repeated seals that have a near-copy anywhere,** including texts that contain a common 3-sign formula. The kept-families variant gives the same answer (P1 p = 0.068, the closest to a signal in any variant).
- **The period alignment across sites is coarse.** MD bands and Harappa Vats strata were dug and recorded differently.
- **The planted power model** (a 20-sign stock, uniform replacement) is one choice. Signals spread thinly over many rare signs would be harder to see. Naive Bayes on presence features is a simple detector; logistic regression agrees.
- **ICIT and M77 cover the same objects,** so the M77 check is a second transcription, not a second sample.
- **The P1 power figure is exploratory.** It was computed after the frozen run with the frozen P1 null threshold.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Unique seal texts carry site composition (MD vs Harappa, whole text) | not supported; moderate effect (q = 0.2) excluded at power 0.92 (exploratory) |
| The site signal lives in the open (medial) slot after allograph merging and period stratification | inconclusive (null, power 0.12) |
| Site signal is place, not time (transfers across period bands) | not supported (no signal to transfer) |
| Multi-site composition differs (4 or 6 sites) | not supported |
| Dissimilarity grows with distance | not supported (4-site r 0.90 at the minimum possible p; 6-site r 0.02) |
| Residual locality = carving variants / frame habits (W154, W806 at Harappa) | lead, exploratory |

## Next experiments

- Freeze W806-vs-W803 and W154 preference at Harappa as a new-finds prediction. Check them on the CISI photographs to see whether they are a cutting style.
- Re-run P2 when HARP or new-site seals add dated Harappa texts. About 3x the current Harappa count would be needed for power 0.8 at q = 0.2 (rough estimate, not computed).
- A frame-slot site test (opener + closer, period-stratified), pre-registered on fresh data. It is the only slot with a hint.

## Files

- `lib.py` (data, allograph maps, CV);
- `s0_describe.py` / `.log` (sizes);
- `s1_confirm.py`, `s1_final.log`, `s1_final.json` (pre-registered run), `s1_dryrun.json`;
- `s2_explore.py`, `s2_explore.log`, `s2_explore.json` (exploratory power, closers, beta-diversity pairs);
- `results.json` (key numbers).
