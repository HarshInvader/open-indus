# Self-labelling objects: do signs depict the object they are written on?

Pre-registered in `docs/prereg/self_label.md`. The silhouettes, the frozen candidate signs and the test code were hashed into `docs/prereg/HASHES.txt` before any sign-by-object count was computed. Code: `shapes.py`, `s1_freeze.py` (blind shape step), `s2_test.py` (the single confirmatory run, log `s2.log`), `s3_redteam_bangle.py` (exploratory), `s4_report.py`. Numbers: `results.json`, `results_raw.json`, `redteam_bangle.json`. Ledger: rows `sl_*` in `docs/test_ledger.csv`.

## Findings first

1. **Null on the decisive bar.** The bar was at least 2 signs enriched on the object they resemble, surviving FDR and replicating at a second site. Only **1** of 78 frozen (object, sign) pairs passed every criterion. Per the pre-registration, that makes it a single lead, not a reading.
2. **Signs that look like an object are not more common on that object.** The question was whether the frozen look-alike signs rank higher than random signs on their object's own vocabulary list. On every route and every set the answer is no:
   - chamfer (primary): dev 0.41, held-out 0.44, ICIT 0.51, against 0.50 for random signs (p = 0.93, 0.76, 0.45);
   - Hu: 0.46-0.50;
   - referent catalogue: 0.31-0.39, i.e. **below** chance (dev p=0.999 for enrichment).
3. **The jar sign is rarer on jars.** M342, which blind raters call a jar, appears in 70 ICIT pottery-graffito texts against 124 expected under the within-site null. It is also low in M77 dev (23 vs 32) and held-out (9 vs 11). The other vessel-looking signs behave the same way: M336 5 vs 18, M343 6 vs 16. The likeliest reason is that pottery marks are short and lack the seal formula that the jar sign closes. Either way, the jar sign is not a "this is a jar" label.
4. **The one lead: an oval sign on bangles.** M373 is a lens-shaped oval. In ICIT it is Wells W790, which the Mahadevan-Wells bridge lumps with M261 (diamond) and M374 (small oval). It is on **6 of 41** distinct bangle texts against 0.45 expected (p=1e-4, BH q=0.008, top 1% of signs on bangles). It passes all four pre-registered criteria:
   - second site: Harappa, 2 of 6 texts vs 0.07 expected, p=0.001;
   - register: 99th percentile;
   - held-out direction: holds vacuously, because M77 has no bangles.
   - Exploratory red-team:
     - Against texts of the same length and site it still stands: 6 vs 0.24 expected, p<1e-4.
     - It is a whole one-sign text on 3 of 14 one-sign bangle texts, against 1 of 165 seals, 0 of 165 pottery texts and 0 of 138 tablets.
   - Why it is weak:
     - It rests on 7 objects, mostly Mohenjo-daro stoneware bangles; the Harappa replication is 2 texts, one of them broken.
     - Only the catalogue route found it. The chamfer route matched the bangle's oblique ring to other signs and put M373 first for the spearhead instead.
     - A pointed oval could just as well be an eye, a bead or a grain.
     - A stoneware-bangle workshop mark explains it as well as a "bangle" word does.
5. **A copper-tablet sign, not a self-label.** M169 is enriched on copper tablets in all three sets: dev 12 vs 3.2 (q=0.006), held-out 4 vs 0.8 (p=0.006), ICIT 21 vs 12 (p=0.005). But the Hu route that picked it matched a branched stick to a rectangle, a visibly poor match that was flagged before testing. M169 is also a known copper-legend sign. Copper tablets come from one site, so the pair could never pass the second-site rule, and that was stated in advance. This is the object-register effect (README #6), not depiction.

**What this means:** inscribed objects do not carry a picture-sign of themselves. Where an object class has a distinctive sign, as copper tablets have M169, the sign does not look like the object. The one look-alike that is enriched (the oval on bangles) is too thin to read as "bangle". This fits the earlier results: signs are not tied to the animal picture on seals (logograms), and what a sign depicts does not predict its role (iconography).

## Contact sheet

`results_sheet.png`: each object silhouette, then its frozen top-3 signs by chamfer, catalogue and Hu route, labelled with ICIT observed/expected counts on that object (* = confirmed). `contact_sheet.png` shows every silhouette, including the alternates (seal profile, prism-tablet end, rod lying, knife, spearhead, oblique ring), with its top-3 by chamfer and Hu. `contact_sheet_v1_hu_bug.png` is the pre-fix version.

![results sheet](results_sheet.png)

## Method

- **Object classes** (M77 object_type, ICIT type). Distinct (sequence, class, site) texts, M77 / ICIT:
  - seal 1,725 / 2,158
  - sealing 414 / 195
  - miniature tablet 177 / 886
  - copper tablet 65 / 98
  - pottery graffito 115 / 384
  - ivory/bone rod 26 / 37
  - bronze implement 17 / 18
  - stamped pottery (pointed goblets): ICIT only, 50
  - bangle (mostly stoneware): ICIT only, 41
- **Untestable classes:**
  - weights: there are no inscribed weights in either corpus;
  - beads: 2 items;
  - copper tablets cannot replicate across sites, since they come from Mohenjo-daro only.
- **Silhouettes** were drawn in code from each object's physical shape, before any distribution was computed:
  - square seal face, and seal profile with a pierced boss;
  - sealing lump carrying a square impression;
  - tablet bar and triangular-prism end;
  - 2:1 copper tablet;
  - globular jar with neck;
  - pointed goblet;
  - rod, upright and lying;
  - flat axe, knife blade and spearhead;
  - ring, face-on and oblique.
  - No museum photographs were fetched. Outlines defined in code were the option the brief allowed, and they avoid segmenting untrusted images.
- **Shape routes** over a pool of 196 signs with at least 5 distinct M77 texts:
  1. chamfer distance on thinned, size-normalised drawings (primary; keeps orientation and aspect);
  2. keyword match in the blind referent catalogue (top-120 signs);
  3. Hu moments of the filled region.
  - Top-3 per object per route were frozen, giving 78 pairs.
  - Disclosure: v1 computed Hu on 1-pixel outlines, which is degenerate. It was fixed after viewing the contact sheet and before any distribution. The fixed route is still poor and was flagged so in the pre-registration.
- **Test.** Count the class texts containing the sign. Null: object labels permuted among texts within site, 10,000 times (the object-vocabulary null). Register control: the sign's percentile among all pool signs by null z on that class.
- **Sets:** M77 dev, M77 held-out v2, ICIT. ICIT signs were mapped to Mahadevan numbers through the bridge.
- **Confirmation (all four required):**
  - C1: ICIT BH q<0.05 over 78 pairs;
  - C2: p<0.05 at a second ICIT site;
  - C3: register percentile ≥0.90;
  - C4: same direction on held-out v2.

## Hypotheses

| Hypothesis | Result | Verdict |
|---|---|---|
| ≥2 signs depict and label their object (decisive) | 1 pair passes (bangle × M373) | **refuted at this data size** (single lead) |
| Shape-nearest signs (chamfer) enriched beyond register | pct 0.41 / 0.44 / 0.51 vs 0.50; p ≥ 0.45 | refuted |
| Catalogue look-alikes enriched beyond register | pct 0.31-0.39 (depleted) | refuted (reversed) |
| Hu look-alikes enriched | pct 0.46-0.50 | refuted |
| Jar sign M342 labels jars | ICIT 70 vs 124 expected; dev 23 vs 32 | refuted (depleted) |
| Oval M373/W790 = "bangle" | 6/41 vs 0.45; Harappa 2/6; length-matched p<1e-4 | inconclusive lead |
| Axe/blade signs on copper implements | 0-1 hits per sign, expected ≤1.4 | untestable in practice (18 texts) |
| Rod-like stroke on rods | M86 3 vs 2.3 | refuted / low power |
| Weight-like sign on weights | no inscribed weights | untestable |

**Power caveat:** rods (37), implements (18), bangles (41) and stamped goblets (50) are small. A sign on about 15% of a class's texts with a base rate near 1% is detectable, as the bangle case shows. Weaker self-labels on those classes are not excluded.

## Next experiments

1. **Bangle oval, cheap check.** Look at the W790 bangle photos (CISI M-1630, 1631, 1644, 1645; H-1010, H-2578) to see which Mahadevan sign it is (M261 diamond, M373 oval or M374 small oval), and whether it is incised in the same place on each bangle. Then score it as a frozen prediction for new stoneware bangles (Fuls 2023 catalogue, HARP reports). Hash the prediction now: "the next stoneware bangle with an inscription has an oval/lens sign with probability ≥0.15, against ~0.01 for other short texts."
2. Human raters for the silhouette match, so the chamfer route is not the only depiction judge.
3. Close the route otherwise. Object-register signs exist (README #6), but they are not drawings of the object.
