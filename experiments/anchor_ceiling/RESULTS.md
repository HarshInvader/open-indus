# anchor_ceiling v1: kill test (prereg `docs/prereg/anchor_ceiling.md`, sealed 2026-11-24T12:05Z)

## Verdict: the kill test FAILED, so v1 stops as sealed
- The sealed reading: "the method cannot see a perfect tie at Indus size". No real run.
- The truth was frozen first. Two blind labellers agreed at κ 0.881 and kept 69 words. Scored fields: place 25, admin 14, land 8, occupation 8, goods 5, person 5.

| planted strength | median adjusted Rand | power (mean share of fields recovered) |
|---|---|---|
| 1.0 | -0.0004 | 0.00 |
| 0.6 | 0.0002 | 0.008 |
| 0.3 | 0.010 | 0.00 |

- **The null corpus was stopped unread.** It permuted one anchor at a time against the real truth, so its output would have exposed the real site and class association before any later version. It wrote nothing, and the verdict does not need it.

## Why (exploratory, after the verdict; planted data only)
- **The plant held.** About 85% of a planted word's dev documents carry its value.
- **The method failed.**
  - Average-link cosine clustering chained: 62 of 80 words fell in one cluster.
  - The site and class dimensions diluted the picture signal.
  - k-means reached a dev adjusted Rand of 0.71 with picture dimensions only.
- **The bar was unreachable.** Goods and person (5 words) were scoreable in ≥ 4 draws in only 10 and 9 of 20 plants (Fable's review).
- **The smoothing hurt.** Add-0.5 gives rare words positive log-ratios on rare values (Fable's review, from code).
- **So this is a method failure.** It says nothing about whether anchors carry field information.

## Next
- `docs/prereg/anchor_ceiling_v2.md`, sealed. It is the last version, with the disclosures above.

---

# v2 (prereg `anchor_ceiling_v2.md`, sealed; the last version)

## Method selection (`select.json`, hashed before the kill test)
- The statistic is the held-out adjusted Rand at strength 1.0 (10 plants, seed 20261201).
- k-means scored 0.199 and Ward 0.137, so k-means was chosen.

## Kill test: the supervised gate FAILED, so the study stops as sealed (`kill2.json`)
| check (strength 1.0, 20 plants) | value | bar |
|---|---|---|
| dev, leave-one-word-out, field recovery | admin 1.00, land 1.00, occupation 0.95, person 0.95, place 1.00 | ≥ 0.8 each: met |
| held-out, true-field centroids, median adjusted Rand | **0.56** | ≥ 0.8: not met |
| held-out, true-field centroids, field recovery | admin 1.00, land 0.95, occupation 0.90, **person 0.65**, place 1.00 | ≥ 0.8 each: not met |

- **Sealed reading:** "profiles too thin at this size".
- The blind test and the null corpus were not run.
- No anchor claim is made.

## What it means
- **Dev profiles separate the planted fields well.** These are words with ≥ 5 dev documents.
- **Held-out profiles are too thin to place words reliably,** even with true-field centroids and a perfect, exclusive planted picture. Held-out words have 2-5 documents each.
- **The blind method was further still from the bar** (held-out adjusted Rand about 0.2 at selection).
- **So anchor-based recovery of meaning fields cannot be calibrated at Indus size on Linear B.**
  - The real association was never looked at.
  - As sealed, main line (b) falls back to function (L1). The outcome is recorded in `docs/NEGATIVE_ATLAS.md` §3.6.
- **Caveat.** The supervised held-out test is close to the bar on four of five fields. One soft field (person, 3 pool words) and the adjusted Rand bar decide the failure.
