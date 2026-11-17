# Carver hands: does one workshop's style go with a fixed part of the text?

Code: `c1_locate.py` (find and label photos), `c2_features.py` (motif features, validation, frozen clustering), `c3_test.py` (pre-registered slot test), `c4_power_amend.py` (amendment A1, power). Run from the repo root with `.venv/bin/python -I`. Pre-registration: `docs/prereg/carver_hands.md` (hashes in `docs/prereg/HASHES.txt`, tag `carver_hands`). Numbers: `results.json`, `validation.json`, `c3.json`, `c4.json`, logs `c3.log`, `c4.log`. Fable 5.2 plan 2, item 4.

## Conclusion first

1. **No slot follows carving style.** Seals that look alike in the animal motif do not share the opener, title, closer, numeral or core more often than seals that look different. This holds for every grouping tested: 4 of 4 pre-registered tests are null (Bonferroni alpha 0.0125). So the carving gives no independent slot meaning: it neither ties the frame to a workshop nor the core to one.
   - The null has some power. The frame-sharing rate within a style group is at most about 1.01-1.11 times the rate between groups (upper 95% bound). A group-specific closer planted on 20% of a group's seals is detected 92-100% of the time; one on 10% is detected 0-26% of the time.
   - This agrees with paragorth S-DARK-14.3 / 46.x (style letter and physical clusters do not predict shared text; allograph choice is a city habit set by the neighbouring sign). Their test used whole-text overlap; this one tests each slot.
2. **Feasibility: CISI vol. 1-2 photos are too coarse to find carvers' hands.** They sample about **8 px per mm of the real seal** (prints at 2:1, scanned at 100 ppi; 10th-90th percentile 7.6-8.6). That is enough to see pose, collar folds, neck hatching on large seals and the type of standard. It is not enough for tool-level traits (hatching pitch, drill-hole shape, hoof and eye cutting). Motif features are object-specific: an impression finds its own seal photo at median rank 3 of 418. But they form **no discrete clusters** (silhouette 0.04-0.05 for every K from 3 to 10; bootstrap ARI 0.19). The "hands" tested are therefore slices of a continuum, not workshops.
3. **Human-action lead.** Tool-level hand attribution needs about **30 px/mm or more of the object** (e.g. 0.1 mm cuts at 3 px), about 4x the current linear resolution. Ways to get it:
   - re-scan the CISI 2:1 photographic prints at 1200 dpi (about 47 px/mm);
   - macro or RTI photographs of the seals (Harappa.com/HARP, the National Museum Karachi, ASI);
   - Konasukawa & Koiso's or Rissman's unicorn style codings.

   Ground truth for checking any clustering: seal-sealing matches, and HARP's workshop/debris attributions. Sample: on this design about 500 seals detect only strong effects (20% of a group sharing a group-specific closer), so plan for 1,000+ unicorns from vol. 3 as well (not on disk).

## Data and method

- **Photos.** Every page image of CISI vol. 1-2 was extracted (917 pages) and run through tesseract OCR (3x upscale, `work/ocr/`). Photo boxes were detected as non-white blobs and labelled from the caption below them ("M-207 a").
  - Of 1,159 ICIT unicorn square seals with a CISI number, 456 impressions and 461 seal photos were found; 361 objects have both. The rest are mostly in vol. 3, or are OCR misses.
  - Analysis set: 499 seals, one photo each (impression preferred), single-line texts only (so text rarely enters the motif crop), with measured size. Mohenjo-daro 339, Harappa 117, Lothal 17, Kalibangan 16.
- **Features (motif only).**
  - Crop: lower 58% of the photo, CLAHE, resized to 128x72.
  - HOG with unsigned gradients, 9 bins, 8 px cells, implemented in numpy because cv2 5 has no HOG.
  - Gabor energy: 4 orientations x 2 scales on a 4x3 grid.
  - A head/neck high-frequency "hatching" index.
  - All features are flip-symmetrised, so facing direction doesn't matter. No pretrained CNN was available offline (no torch for Python 3.15).
- **Clustering.** Features were residualised on site, log size, photo brightness/contrast/width and seal-vs-impression. Then PCA to 20 dimensions and KMeans with K picked by silhouette over 3..10, which gave K=10 (cluster sizes 11-81). The clusters were then frozen and hashed before any text was linked.

### Validation (no text used)

| Check | Result | Reading |
|---|---|---|
| V1 identity: impression -> its own seal photo (mirrored) among 418 | median rank 3 (chance 209.5); top-1 115/328, top-10 222/328 (chance 7.8) | features are object-specific (layout identity, not proof of a hand) |
| V2 predict ICIT unicorn style letter (W/J/S/I/L) | balanced accuracy 0.33 vs null 0.23 (95% 0.28), p=0.005; but site+size+photo alone give 0.38 | the letter is mostly a site/size proxy; weak validation |
| V3 predict CISI's within-size-group order (Rissman collar -> hatched neck -> hatched face) | CV Spearman 0.28 vs null 95% 0.09, p=0.002 | features carry some style, but the CISI order also puts broken seals last |
| Proxy check | site + size + photo explain 15% of feature variance; clusters vs site NMI 0.04, vs size group 0.04 | clusters are not site/size proxies |
| Cluster structure | silhouette 0.04-0.05 at all K; bootstrap ARI 0.19 | no discrete hands |

Not done: a sealing-of-same-seal positive control. CISI vol. 1-2 have few matched seal/sealing pairs for unicorns, so V1 is the closest substitute.

### Pre-registered slot test (`c3.log`)

**Slots** come from `functional_reading/lexicon.csv` roles via the W->M bridge:
- opener = leading OPENER/CONNECTIVE run;
- closer = trailing CLOSER/clitic run;
- title = TITLE ELEMENT signs;
- numeral = numeral and unit signs;
- core = the rest.

**Statistic.** For each slot: the share of pairs with an identical, non-empty value, within a group vs between groups. E = log ratio of the two shares. E_F pools opener, title and closer. Δ = E_F − E_C.

**Null.** Texts were shuffled among seals within site x CISI size-group strata, 2,000 times.

| Partition | n | frame identical within / between | E_F (p) | E_C (p) | Δ (two-sided p) |
|---|---|---|---|---|---|
| P1 image 5-nearest-neighbour pairs | 499 (1,562 pairs) | 0.290 / 0.283 | +0.03 (0.32) | +0.36 (0.20) | −0.34 (0.37) |
| P2 image clusters K=10 | 499 | 0.283 / 0.283 | +0.00 (0.54) | −0.00 (0.47) | +0.00 (0.88) |
| P3 ICIT style letter | 814 | 0.264 / 0.270 | −0.02 (0.96) | +0.03 (0.10) | −0.05 (0.07) |
| P4 W705 vs W706 carriers (text proxy) | 80 (W705 53, W706 27) | 0.333 / 0.307 | +0.08 (0.23) | +0.25 (0.52) | −0.17 (0.99) |

- No per-slot excess reaches p<0.05 in any partition. The lowest p is the P3 core at 0.10.
- In P4, W705 carriers and W706 carriers do not differ in their other slots. The W706 size effect (redteam_rank) is therefore not part of a text package that a hand marker would reveal. Allograph choice depends on the neighbouring sign (S-DARK-46.5), so P4 could not name a hand anyway.

### Amendment A1 (after c3; exploratory)

The frozen power control planted each group's modal closer. That is the jar W740 in every group, so it added no group signal and returned power 0 everywhere, which says nothing. `c4_power_amend.py` plants a group-specific non-jar closer instead:

| Partition | q=0.05 | q=0.10 | q=0.20 |
|---|---|---|---|
| P2 clusters | 0.00 | 0.26 | 1.00 |
| P3 letters | 0.00 | 0.00 | 0.92 |

Upper 95% bound on the frame within/between ratio: P1 1.11, P2 1.05, P3 1.01.

Δ itself is weak by design: whole-core identity is rare (0.2% of pairs), so E_C is noisy (null sd 0.10-0.67).

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| CISI vol. 1-2 photos allow carver-hand attribution | refuted at 8 px/mm (no cluster structure); needs ~30+ px/mm |
| Seals of one carving style share frame slots (frame = workshop) | refuted for strong effects (frame ratio <= 1.01-1.11); weak effects not excluded |
| Seals of one carving style share the core (frame = individual) | not supported (E_C p 0.10-0.52) |
| W705/W706 variant marks a hand with its own text package | not supported (n=80, low power) |

## Caveats

- The image "hands" are style neighbourhoods, not demonstrated workshops. A real hand signal could be hidden below the photo resolution.
- Slots come from a role lexicon that was itself only weakly validated (README #9, q=0.085).
- The style letter (P3) is a human coding of unknown definition. Prior work calls it a carving style, but it tracks size and site.
- One measurer (1930s) for Mohenjo-daro/Harappa seal sizes, as in rank_ladder.

## Next experiments

1. Get high-resolution imagery (the 1200 dpi CISI print scans or museum macro/RTI) for about 300 unicorn seals, with a known-positive set of seal-sealing pairs. Re-run c2-c3 unchanged with the same frozen statistic.
2. If the resolution can't be had: use expert style codings (Rissman/Konasukawa) as the partition, with the same c3 test.
3. Use a slot measure with more power for the core (shared sign rather than identical tuple). Pre-register it fresh.
