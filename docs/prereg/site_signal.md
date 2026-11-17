# Pre-registration: site signal in non-repeated seal texts (Fable plan 5, T5; ecology beta diversity)

Registered 2026-11-15 in `experiments/site_signal/`. Before this file was written, only data sizes were computed (`s0_describe.py`, `s0_describe.log`) and the pipeline was run once in `dryrun` mode, where site labels are shuffled before anything is computed (`s1_confirm.py dryrun`). No real site-prediction outcome has been seen. Hashed with `lib.py` and `s1_confirm.py` in `docs/prereg/HASHES.txt` (tag `site_signal`) before `s1_confirm.py final`.

Run: `.venv/bin/python experiments/site_signal/s1_confirm.py final` (defaults: 1,000 permutations for P1-P4, 500 for secondary, 100 power replicates).

## Question

Repeated seal texts are placeless (identifiers S3: cross-site ratio 0.89; redteam_identifiers). Does the unique bulk of seal texts carry local composition, as local name stocks would? Or is it one homogeneous pan-Indus pool?

## Data and exclusions

- ICIT, object type SEAL* only, flagged complete, no `#` break. 1,606 seals.
- Drop any seal whose exact sign string occurs on more than one ICIT object of any type (seal, sealing, tablet, pot ...).
- Drop any seal that is a near-copy of another distinct ICIT text under the `corpus/build.py` `_close` rule (splits_v2): <= 1 edit with both >= 4 signs, or a >= 3-sign text contained in another. The universe includes all object types and the >= 3-sign runs of broken texts.
- Result (strict set): 802 seals (Mohenjo-daro 489, Harappa 132, Dholavira 33, Lothal 30, Chanhu-daro 25, Kalibangan 24, others fewer). Every remaining seal is its own text family, so grouped CV is per text. In the `all` robustness variant, families are kept and used as CV groups.
- Signs: Wells numbers, in reading order. Line breaks are ignored for position; bigrams are taken only within a line.

## Allograph levels (fixed now)

- **A0:** raw Wells signs.
- **A1 (carving variants merged):** (a) Wells signs that each map to exactly one Mahadevan sign, with several mapping to the same one, are merged (Mahadevan lumps what Wells splits; e.g. W704/W705/W706 = M336). (b) shaunmortal M5 image + distribution allograph candidates are merged: W741/742/745, W803/806, W151/156, W384/388, W904/923, W615/630, W705/706. The fish family (W220/231/233/235/240) and tall-1/tall-2 (W031/W032) are excluded at A1, because they are lexical-class or numeral pairs, not carving variants. The W405/W407 font artefact is excluded. A1 has 20 groups covering 45 signs.
- **A2:** A1 plus the fish family and W031/W032 (most aggressive).

## Period bands (aligned coarsely, fixed now)

- **late:** Mohenjo-daro period "Late"; Harappa HARP 3C; Harappa Vats Strata I-III (I = top = latest).
- **earlier:** Mohenjo-daro "Early" and "Intermediate"; HARP 3A, 3B; Vats Strata IV-VII.
- HARP 3B/C (mixed) and undated seals have no band.
- Strict set, Mohenjo-daro and Harappa: MD earlier 146, late 115; Harappa earlier 31, late 45. The alignment between the sites is approximate. That is why P3 (transfer across bands) is included.

## Method

- Classifier: Bernoulli naive Bayes (alpha 1, flat prior) on binary presence features, min document frequency 2.
- Score: out-of-fold probabilities from stratified group 5-fold CV, repeated 3 times. Groups are text families.
- Binary metric: ROC AUC (MD = 1).
- Permutation null: site labels shuffled (within period band where stated) and the full CV re-run. One-sided p = (1 + #null >= obs) / (R + 1).
- Slots, positional:
  - opener = first sign;
  - closer = last sign;
  - frame = opener + closer;
  - medial = signs 2..n-1 plus bigrams wholly inside them (texts of >= 3 signs);
  - all = unigrams + within-line bigrams.

## Confirmatory tests (Holm over P1-P4, alpha 0.05)

| id | test | data | features | null |
|---|---|---|---|---|
| P1 | MD vs Harappa | strict, all lengths (621) | all, A0 | site permuted |
| P2 | MD vs Harappa, **open slot, period-stratified** | strict, dated, >= 3 signs | medial, A1 | site permuted within band |
| P3 | **place vs time:** train on one band, test on the other (both directions, mean AUC) | as P2 | medial, A1 | site permuted within band |
| P4 | multi-site (sites with >= 30 strict seals: MD, Harappa, Dholavira, Lothal) | strict | all, A1 | site permuted; metric balanced accuracy |

P5 (beta diversity vs distance) is reported, not counted, and labelled low power. Sites with >= 30 strict seals (4 sites, 6 pairs, 24 Mantel permutations) are rarefied to 30 seals, 200 draws, on A1 sign counts per seal set. Metrics are Bray-Curtis and Jaccard. Mantel r against great-circle distance, by exhaustive permutation. A pooled-labels null (same sizes drawn from one pool) gives the dissimilarity expected from sampling alone. Secondary: sites with >= 20 seals (6 sites, 15 pairs).

**Power (fixed now):** null world = P2 data with site permuted within band. Harappa-labelled medial tokens are replaced, with probability q, by a draw from a random 20-sign stock of common medial signs (>= 5 medial uses). 100 replicates each at q = 0.1, 0.2, 0.3. Power = share of replicates with AUC above the 95th percentile of the real P2 null.

## Decision rule (fixed now)

- **SUPPORT** (site signal in the open slot): P2 passes Holm. If P3 also passes (p < 0.05), the signal is attributed to place rather than time. If P3 fails, place vs time is reported as unresolved.
- **REFUTE** (one homogeneous pan-Indus pool, at stated power): P1 and P2 both fail, and planted power for P2 at q = 0.2 is >= 0.8.
- **SITE SIGNAL OUTSIDE THE OPEN SLOT:** P1 passes, P2 fails. The signal is in frame slots, carving variants or period.
- Otherwise **INCONCLUSIVE.**

## Secondary and exploratory (reported, not counted)

- Slot x allograph table: opener / closer / frame / medial / all x A0 / A1 / A2. This is MD vs Harappa, strict, >= 3 signs, unstratified, 500 permutations. Also period-stratified versions at A1.
- Logistic regression (L2, C 0.5, balanced) as a classifier sensitivity for P2.
- **Time yardstick:** within each site, earlier vs late band, A1, medial and all features.
- **Drivers:** medial unigrams (>= 8 uses), Fisher MD vs Harappa with BH, and leave-one-sign-out AUC drop (sign and every bigram containing it removed). Each driver is flagged for A1 allograph-group membership.
- **Variant split:** for each A1 group, whether MD and Harappa prefer different variants (Fisher on the main variant).
- **Robustness:** `rep` (one seal per family) and `all` (families kept, grouped CV) variants of P1/P2. Medial A1 on undated texts too.
- **M77 replication:** Mahadevan list, strict exclusion on M77. The objects are the same as ICIT, so this replicates the transcription, not the sample.
- P4 with sites >= 20 (6 sites).

## Known risks

- Harappa dated strict seals are few (76; fewer with >= 3 signs), so P2 and P3 power is the binding limit. The power run quantifies it.
- Period bands are a coarse cross-site alignment. P3 tests the generalisation directly.
- Strict near-copy exclusion removes 526 non-repeated seals that have a near-copy anywhere. Formula-bearing texts are thus under-represented. The `all` variant checks this.
- MD and Harappa seal measurements and transcriptions come largely from 1920s-30s excavation reports; reporting habits could differ by site (e.g. how variants were drawn). The A1/A2 merges address the known variant pairs only.
- Under the null, CV AUC with naive Bayes sits slightly below 0.5 (seen in the dry run). The permutation null carries the same bias, so p-values are unaffected; AUC is always read against the null mean.
