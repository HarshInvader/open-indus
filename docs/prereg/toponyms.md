# Pre-registration: toponym / city-seal test (Fable 5.2 plan item F7)

Registered 2026-11-15 in `experiments/toponyms/`, after exploratory work on discovery data only (`explore.py`, `explore_*.log`) and a code dry run in which both halves came from discovery data (`confirm.py dryrun`, `confirm_dryrun.log`). BEFORE `confirm.py final` touches ICIT half B or M77 held-out v2. Scripts `common.py`, `confirm.py` are hashed with this file in `docs/prereg/HASHES.txt` (tag `toponyms`).

Run: `.venv/bin/python experiments/toponyms/confirm.py final`.

## Question and prediction

Jemdet Nasr "city seals" name cities; their signs cluster at the home city and appear elsewhere on sealed, travelling objects. If some Indus signs or sequences name places or groups: (a) the sequence is enriched at one site beyond its size and object mix, and the enrichment REPLICATES on independent texts; (b) its occurrences away from home fall on mobile media (clay sealings/tags; broadly also tablets and trade pottery) more than other texts at those same sites; (c) reverse: some sequences are on seals at only one site but on sealings at others.

## Units and data

- Unit = distinct (site, medium, sign sequence). Medium: ICIT SEAL* = seal, TAG* = sealing, TAB:B/TAB:I = tablet, TAB:C = copper, POT* = pottery, rest = other. M77: object_type mapped the same way (M77 "sealing" at Harappa is mostly moulded tablets; declared caveat).
- Near-copy families (same rule as `corpus/build.py` v2, with containment for >= 4-sign texts): identical string, <= 1 edit with both >= 4 signs, or a >= 4-sign text inside another.
- Enrichment uses one record per (site, family) (a seal and its impressions, or a mould series, count once per site). Travel and reverse tests use one record per (site, medium, family).
- Features: sign unigrams (>= 5 site-family units), bigrams and trigrams (>= 4), from break-free runs. Unknown provenance, "Other sites", "West Asian finds" never serve as homes.

## Split (confirmatory = independent text families)

- **M77:** discovery = `dev_heldout(version=2)` dev; confirmation = held-out v2.
- **ICIT:** families (rule above) shuffled with seed 20261114 and alternated into half A (discovery, 1,899 units) and half B (confirmation, 2,018 units). Justification: holding out whole sites would leave no home site to replicate on (most small sites have < 20 texts), and a random family split keeps near-copies (moulded tablets, a seal and its sealings) on one side. ICIT and M77 overlap heavily in objects; they are two transcriptions, not two samples, so a joint pass counts as one replication, not two.

## Candidate rule (frozen; applied to discovery half only)

Site enrichment with a site-size-aware null: site labels permuted among site-family units within medium strata (preserves every site x medium total), 2,000 permutations. Candidate = (feature, home) with obs >= 3, obs/exp >= 2, one-sided p < 0.05. Redundant n-grams with identical occurrence sets at the same home are dropped.

## Confirmatory tests (on the confirmation half; alpha = 0.05/8 = 0.00625 Bonferroni over T1, T2a, T2b, T4 x 2 corpora)

| id | hypothesis | statistic | null | support if |
|---|---|---|---|---|
| T1 | candidates are enriched at their discovery home on new texts | pooled sum over candidates of (O_home - E_home), E within medium | site labels permuted within medium, 2,000x | p <= alpha |
| T2a | candidates' off-home occurrences are on clay sealings (primary mobile) | S1 = pooled (observed - expected) mobile off-home units, expected from each unit's own site mobile rate | medium labels permuted among units within site, 5,000x | p <= alpha AND S2 > 0 |
| T2b | same, broad mobile (sealing + tablet + pottery) | S1 as above | same | p <= alpha AND S2 > 0 |
| T4 | reverse: features found on seals at one site only (>= 2 seal units) and on sealings only at other sites occur more than chance | count of such features (>= 3 units) | site labels permuted within medium, 2,000x | p <= alpha |

S2 (register control) = Mantel-Haenszel-weighted difference between the off-home and the home mobile excess rate for each candidate; a sequence that sits on sealings everywhere (an object-type register effect, README #6) raises S1 but not S2.

Secondary (reported, not counted): T3 frequency-matched null (each candidate replaced by a random non-candidate feature within +-50% of its frequency, same home); T2 with MD/Harappa homes dropped; S2 p-values; T1 and T2 power by planting (T1: move off-home occurrences to home until home ratio 1.5/2/3; T2: off-home mobile odds x 2/3/5), 30 replicates x 200 permutations each.

**Dholavira signboard (T5, exploratory only).** The 8 distinct signs of ICIT 144.1 (W820 W611 W388 W850 W645 W031 W821 W798) were fixed a priori, but the dry run already computed their Dholavira enrichment on full ICIT (pooled O = 38 vs E = 39.1, p = 0.61). It is therefore reported as exploratory, not confirmatory.

## Interpretation (fixed now)

- Toponym/ethnonym reading **supported** in a corpus only if T1 AND T2a (or T2b) pass. T1 alone = local vocabulary (workshop, dialect, scribal habit), not evidence of travel. T2 alone is uninterpretable (candidates did not replicate).
- **Refuted at stated power** if T1 and T2a fail and planted power for T2a at odds ratio 3 is >= 0.5: then a sizable toponym-travel effect would likely have been seen.
- Otherwise inconclusive.

## Frozen predictions (rule fixed now)

After the final run, every candidate that individually replicates on the confirmation half (O_home >= 2 and O/E >= 2 in C, same corpus) is frozen in a new hashed file `docs/prereg/2026-11-15_toponym_predictions.md` with two predictions for new finds: P-home (a new text with the feature comes from its home site at > 2x that site's share of new texts) and P-travel (if found off home, it is on a sealing/tag or tablet more often than other new texts from that site). If no candidate replicates, the file freezes the null predictions: no feature reaches >= 3 occurrences with O/E >= 2 at one site in new finds beyond chance, and off-home occurrences of discovery candidates are not over-represented on sealings.

## Known risks

- Few sealings outside Lothal, Dholavira and Kalibangan (MD and Harappa sealing rates ~1%), so T2a depends on small sites.
- Signs that are numerals (W031/W032) or register markers can become candidates; the rule does not exclude them (no tuning after the dry run).
- ICIT and M77 overlap; a joint result counts once.
