# Prereg: uniformity benchmark (Fable 5.2 plan 11, candidate 1)

Written 2026-11-21, before any reference AUC was computed. Code: `experiments/uniformity_benchmark/build.py` and `run.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `uniformity_benchmark`).

## What was seen before writing this

- Text counts per site and length mixes of each reference pool (printed by `run.py sizes`).
- The frame words each pool would lose (listed below).
- No classifier was run on any reference corpus. No planted-stock curve was run.
- The Indus numbers are old and known: site AUC 0.49 (`site_signal` P1), early vs late Mohenjo-daro AUC 0.61.

## Question

Indus seal texts do not reveal their city (Mohenjo-daro vs Harappa, AUC 0.49). Is that strange? We run the same classifier, unchanged, on scripts we can read, cut to Indus size, and see where 0.49 sits.

## Pipeline (frozen, reused unchanged)

- `experiments/site_signal/lib.py` is imported as is.
- Features: `design(texts, {}, "all", min_df=2)`. That is word or sign unigrams plus bigrams inside a line.
- Classifier: `oof_scores(model="nb", k=5, reps=3)`. Bernoulli naive Bayes, stratified group 5-fold, 3 repeats.
- Score: `auc`. Rows with no features are dropped, as in `s1_confirm.binary_test`.
- Null: for each draw, the site labels are permuted once and the CV re-run with `reps=1`, as in `binary_test`. The 200 permuted AUCs per pair and variant form the null.

## Sample design (matches the Indus test)

- Size: 621 texts per draw. 311 from site A, 310 from site B.
- Length mix: the length mix of the 621-seal Indus P1 sample, in bins 1..8 and 9+ (2.1%, 12.2%, 19.6%, 13.4%, 20.0%, 14.3%, 8.9%, 4.7%, 4.8%). A bin that runs short is filled from the nearest bin, ties to the longer bin.
- Draws: 200 per pair and variant, without replacement inside a draw.
- De-duplication: `experiments/fish_tick_closer_v2/dedup.py::greedy` (non-chaining) on the pooled pair. Strings found at both sites are dropped first, because their label is ambiguous.
- Secondary design: the Indus site ratio, 483 vs 128 (n = 611), whole texts only. Reported, not used in any decision.

## Pairs, data and labels

All data are already in the repo. Units: a word for cuneiform and Latin, a sign for proto-cuneiform. Line breaks are kept as runs.

1. **Ur III seals, Umma vs Girsu (name-bearing).**
   - Data: ORACC `epsd2/admin/ur3` in `experiments/meaning_classes_seal/raw/ur3.zip`.
   - A text is one seal legend: the lines labelled "seal N" on one tablet. Word = ORACC form. Legends with any broken word (x, ...) are dropped.
   - Site = the ORACC catalogue provenience of the tablet.
   - After cleaning: Umma 1,023, Girsu 707 distinct legends.
2. **Ur III seals, Puzriš-Dagan vs Nippur (name-bearing).** Replaces Old Babylonian (see dropped pairs). Same data and rules. It shares no city with pair 1. After cleaning: Puzriš-Dagan 329, Nippur 483. Puzriš-Dagan is close to 311, so its side of each draw changes little between draws.
3. **Latin labels, Britannia vs Germania (name-bearing, the empire-wide control).**
   - Data: EDH in `experiments/short_labels/raw/edh`. Genre = labels, exactly as `short_labels` built `lat_label`: owner/artist, label or identification inscriptions, or instrumentum, tile, tessera, signaculum, lamp, amphora, vessel. Damaged texts dropped. Word = letters of the diplomatic text; lines split on "/".
   - EDH has no province field. Site comes from the modern country. United Kingdom = Britannia. Germany = Germania; this is mostly Germania Superior and Inferior plus part of Raetia, so it is a region, not one province.
   - After cleaning: Britannia 475, Germania 1,078.
4. **Proto-cuneiform, Uruk IV vs Uruk III (time pair).**
   - Data: `experiments/protocuneiform/pc_lines.json`. A text is one line (case). Numeral `k(Nxx)` becomes `Nxx`. Lines with X or broken signs are dropped.
   - Only tablets with provenience Uruk in `cdli_cat.csv`, so site does not mix with time.
   - At most one line per tablet in a draw; the tablet is the CV group.
   - After cleaning: Uruk IV 2,329 lines from 1,091 tablets; Uruk III 4,479 lines from 1,376 tablets.

## Frame-words-removed variant

Each pair is run twice: whole texts, and with the frame removed. The frame is the most common words of the cleaned pair pool, taken in order until at least 38.3% of tokens are gone (the `redteam_identifiers` rule). Texts left empty are dropped; the rest are de-duplicated again and length-matched to the same Indus mix.

| pair | frame words | share | first words |
|---|---|---|---|
| Umma vs Girsu | 11 | 0.385 | dumu, dub-sar, lugal, arad₂-zu, ensi₂, uri₅ki-ma, kal-ga, dšara₂, arad₂, nu-banda₃ |
| Puzriš-Dagan vs Nippur | 6 | 0.399 | dumu, lugal, dub-sar, arad₂-zu, uri₅ki-ma, kal-ga |
| Britannia vs Germania | 58 | 0.384 | L, P, C, M, V, F, S, I, T, A |
| Uruk IV vs Uruk III | 18 | 0.389 | N01, N14, EN~a, N34, N57, AN, NUN~a, BA, PAP~a, GAL~a |

Note: the Umma frame includes the god Šara and "ensi₂" (governor). That removes some city signal by rule. That is what the variant is for.

## Dropped before running

- **Old Babylonian seals** (`seals_ob.jsonl` joined to `cdli_cat.csv`). Sippar has about 1,100 legends but the next site, Larsa, has 220. No second site reaches 310. Dropped.
- **Linear B, Knossos vs Pylos.** The repo copies (`short_labels/data/linb_*.jsonl`) keep no site prefix. Dropped.
- **Latin Britannia vs Dacia.** Romania (minus Dobruja) gives 313 distinct labels whole and 232 with the frame removed. Too few for 310 per draw. Dropped.
- **Proto-Elamite.** 95% of tablets are from Susa. Dropped, as the plan says.

## Predictions (copied from plan 11)

- **P1.** Ur III Umma vs Girsu reaches AUC 0.80 or more whole and 0.65 or more with the frame removed.
- **P2.** Uruk IV vs Uruk III reaches 0.70 or more.
- **P3.** Latin provinces sit lower, between 0.50 and 0.65.
- **P4.** Indus stays where it is, 0.49 for site and 0.61 for early vs late Mohenjo-daro. **Nothing new is scored on Indus.** The planted-stock curve below uses Indus texts with permuted site labels only.
- Added here, not in the plan: Puzriš-Dagan vs Nippur is expected to behave like Umma vs Girsu (0.65 or more with the frame removed). It enters the kill rule as a name-bearing pair.

"Reaches X" means the median AUC over the 200 balanced draws is X or more. P2 and P3 are judged on whole texts; the frame-removed value is also reported.

## Kill conditions (copied from plan 11)

- **K1.** Fewer than 2 name-bearing pairs reach 0.65 with the frame removed. Then the pipeline cannot see real local name stocks at this size, and the README line "no large city-specific sign stock" must be reworded as **uncalibrated**. Name-bearing pairs: Umma vs Girsu, Puzriš-Dagan vs Nippur, Britannia vs Germania.
- **K2.** Latin also reaches 0.65 (frame removed). Then every real corpus shows site signal and the Indus null is stranger still. A result, not a kill; it changes the wording.
- **K3.** Latin stays at chance (median below its own null 95th percentile, whole and frame removed). Then "no site signal" does not rule out names. The claim narrows to "no city-bound vocabulary".

## Extra number per pair: planted-stock share

On the Indus P1 sample with site labels permuted, a 20-sign stock replaces a share q of Harappa tokens (the `site_signal` s2 recipe), q in {0, 0.05, ..., 0.8}, 50 repeats each. This gives mean AUC as a function of q. Each reference median AUC is read back to a q by linear interpolation. Then Indus and the references sit on one scale: the share of tokens that would have to come from a local stock. This uses the unbalanced Indus design, so it is an approximate scale.

## Report

Per pair and variant: median AUC, 2.5-97.5% range over draws, null mean and 95th percentile, p = (1 + null draws at or above the median) / 201, share of draws at or above 0.65, number of draws that needed bin filling, the planted-stock q. Then the rank of Indus 0.49 among the reference medians.

Tests: 4 pairs × 2 variants = 8 primary AUCs; 4 secondary (Indus ratio). The predictions and kill rules are threshold rules, not p-value tests, so no multiple-test correction is applied to them; p-values are reported raw.

## Not changed after seeing data

Thresholds, pairs, frame rule, sample size and length mix are fixed here. If a draw cannot be filled, it is recorded as failed, not redrawn with new rules.
