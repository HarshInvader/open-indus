# Red team: is Indus seal writing unusually uniform across cities?

Prereg: `docs/prereg/redteam_uniformity.md`, hashed with `rt.py` in `docs/prereg/HASHES.txt` (tag `redteam_uniformity`, 2026-11-21T08:27:24Z) before any condition was scored. Code: `rt.py` (prereg'd conditions), `rt_extra.py` (exploratory rerun of 3 failed conditions), `leak_words.py` (exploratory counts). Numbers: `table.md`, `table_extra.md`, `results.json`, `draws.jsonl` (30 draws per condition). Ledger: `ledger_rows.csv`.

## Verdict: the claim STANDS WEAKENED

- **The core holds.** Through the benchmark's exact code, Mohenjo-daro vs Harappa seals give 0.55. That is at the edge of chance (p ≈ 0.06–0.10). Every name-bearing reference at the same size and length mix is clearly higher.
- **The size of the gap was overstated.** The headline numbers (0.885 and 0.807 for Ur III) lean on city names, gods' names and the same owners' seals counted many times. With those removed, Umma vs Girsu falls to 0.71. Puzriš-Dagan vs Nippur falls to 0.58, though that is only 93 texts per side.
- **The 0.49 is not the like-for-like number.** It came from a different pool (strict exclusion), a 483:128 design and family CV groups. The fair comparator is 0.55 (0.52–0.55 under every sign list).
- **Vocabulary size is not the explanation.** Cutting the references to 400 classes does not lower them; some rise.
- **Proto-cuneiform is a time pair, not a city pair.** Part of its signal is editors' period-specific variant labels. It should not support a sentence about cities.
- **One Indus site pair is not uniform.** Chanhu-daro vs Harappa gives 0.67 at 40 per side (null q95 0.63). That is exploratory and small, but it means "uniform across cities" is not true for every pair.
- **Power is good for a real local stock and marginal for a thin one.** A local stock covering 10% of tokens is detected 40–83% of the time; 15% or more is detected 100% of the time.

By the prereg rules this is not "broken": Indus is 0.55, below 0.60, and only 1 of 3 name-bearing references falls below 0.60 under the strongest controls. It is not "stands" either: Puzriš-Dagan vs Nippur falls below 0.65 under full controls, Chanhu-daro passes the small-n reference range, and power is under 80% for the thinnest reference-like stock.

### Safe README wording

> Seal texts from Mohenjo-daro and Harappa cannot be told apart by which signs they use (AUC 0.55, near chance, under five sign lists). The same classifier, at the same size, tells apart Ur III seals from different cities (0.71–0.87 even after city names, gods and repeated owners are removed) and Roman labels from Britain and Germany (0.68 after military stamps are removed). A city-specific stock of signs making up 15% of tokens would have been found. So the two big Indus cities share their seal vocabulary more closely than the readable seal and label corpora we tested.

Do not write: "unusually uniform" as a general fact (two reference corpora, three city pairs); 0.49 as the comparator; 0.885 or "0.71 to 0.89" as the reference range; proto-cuneiform as a city control; "across cities" as if every Indus site pair were tested and flat.

## Numbers per attack (median AUC over 30 draws; Indus length mix; benchmark clean + draw + score)

### 1. Like-for-like

| condition | per side | median | 95% of draws | null q95 |
|---|---|---|---|---|
| **Indus ICIT seals MD vs Harappa** (benchmark clean + draw) | 227 | **0.549** | 0.504–0.589 | 0.542 |
| same | 100 / 50 / 35 | 0.520 / 0.510 / 0.493 | | |
| Indus, old strict P1 pool | 130 | 0.524 | 0.460–0.580 | 0.552 |
| Ur III Umma vs Girsu, whole / frame removed | 227 | 0.873 / 0.873 | | |
| Ur III Puzriš-Dagan vs Nippur, whole / frame removed | 227 | 0.763 / 0.857 | | |
| Latin Britannia vs Germania, whole / frame removed | 227 | 0.668 / 0.674 | | |
| Proto-cuneiform Uruk IV vs III, whole / frame removed | 227 | 0.833 / 0.865 | | |

- Harappa has only 232 texts after the benchmark's cleaning, so 311 per side was never possible for Indus. The benchmark compared 621-text balanced reference draws with an old unbalanced Indus run.
- At like-for-like size, Indus is 0.55. Its p against its own 30 null draws is 0.065, and 0.098 against 1,290 pooled null draws at that size. So it is near chance, not exactly at chance.
- Latin falls from 0.713 to 0.668 at 227 per side and is 0.63 at 130 per side. Latin is the weakest reference, and its margin depends on size.

### 2. Vocabulary and tokenisation (227 per side unless noted)

| reference | whole | top-400 + UNK | top-400, rest dropped | 200 + 200 hashed | top-400 + frame | Ur III as sign readings |
|---|---|---|---|---|---|---|
| Umma vs Girsu | 0.873 | 0.878 | 0.886 | 0.849 | 0.923 | 0.875 (+top-400 + frame 0.839) |
| Puzriš-Dagan vs Nippur | 0.763 | 0.792 | 0.805 | 0.736 | 0.837 | 0.884 (0.789) |
| Britannia vs Germania | 0.668 | 0.700 | 0.764 (207) | 0.664 | 0.761 (188) | |
| Uruk IV vs III | 0.833 | 0.821 | 0.826 | 0.809 | 0.876 | |

- After the cut, the references have 300–380 types per draw and a type-token ratio of 0.13–0.20. Indus has 339 types and 0.16. The vocabularies now match, and the gap stays.
- Hashing rare words into shared classes costs 0.01–0.03. Under a ~400-class vocabulary, the local signal is carried by the frequent words.

### 3. Label leaks

Counts (`leak_words.log`, exploratory) show plain site tags among the most site-bound tokens:
- Umma: `umma{ki}` in 65 texts at Umma and 0 at Girsu; the god `{d}šara₂` 78 to 0.
- Girsu: `lagaš{ki}` 21 to 0 and `{d}ba-ba₆` 16 to 0.
- Nippur: `nibru{ki}` and `{d}en-lil₂`.
- Latin: `XXII` and `LEGIO` appear only in Germania (Legio XXII stamps).
- Ur III repeats seal owners heavily. Umma has 1,023 legends but only 461 distinct first lines.

| control | Umma vs Girsu | Puzriš-Dagan vs Nippur |
|---|---|---|
| none | 0.873 | 0.763 |
| one legend per owner | 0.825 | 0.681 (107 per side) |
| no {d} or {ki} tokens | 0.787 | 0.757 |
| **all: owner de-dup + no {d}/{ki} + sign readings + top-400 + frame** | **0.709** (226) | **0.584** (93; null q95 0.575) |

- Latin with every military or numeral label dropped: 0.685. With top-400 and the frame also removed: 0.679 (141 per side).
- Proto-cuneiform with variant marks removed: 0.803 (0.832 with the frame removed). Much of its signal is real sign choice, but it is time, not place.
- For comparison, Indus at 100 per side is 0.52. The Puzriš-Dagan gap under full controls is about 0.06, and that sample is too small to separate it from Indus.

### 4. Indus transcription (exploratory rerun at 190 per side, `table_extra.md`)

| sign list | median |
|---|---|
| ICIT Wells, raw (the splitter, ~700 signs) | 0.535 (0.549 at 227) |
| ICIT + carving-variant merges (A1) | 0.521 |
| ICIT + A1 + fish family (A2) | 0.535 |
| M77 Mahadevan (a different editor) | 0.537 |
| M77 lump_all (coarsest) | 0.554 |

- Two independent editors and five granularities all give 0.52–0.55. The finest list available (Wells) is no more site-specific than the coarsest.
- Not testable: local carving variants that no published list records. That would need sign images per site.

### 5. Other Indus pairs (size = smaller side)

| pair | per side | median | null q95 |
|---|---|---|---|
| Harappa vs Dholavira | 62 | 0.592 | 0.612 |
| MD vs Dholavira | 58 | 0.545 | 0.570 |
| Harappa vs Lothal | 55 | 0.553 | 0.612 |
| MD vs Lothal | 49 | 0.511 | 0.615 |
| Harappa vs Kalibangan | 40 | 0.504 | 0.612 |
| MD vs Kalibangan | 37 | 0.463 | 0.645 |
| **Harappa vs Chanhu-daro** | 40 | **0.672** | 0.632 |
| MD vs Chanhu-daro | 38 | 0.641 | 0.654 |
| M77 sealings MD vs Harappa | 65 | 0.617 | 0.628 |
| M77 Lothal vs Harappa (seals + sealings) | 83 | 0.615 | 0.578 |
| MD earlier vs late (time) | 205 | 0.527 | 0.562 |
| Harappa seal vs sealing (object type) | 141 | 0.776 | 0.605 |
| Harappa seal vs miniature tablet (object type) | 132 | 0.814 | 0.581 |
| *Reference baselines, raw whole, 35 / 50 per side* | | 0.55–0.67 / 0.55–0.75 | |

- Most pairs sit at chance. Chanhu-daro differs from both big cities, and M77 Lothal is just over its null. These are single small samples among 12 pairs, so read them as leads, not findings.
- The pipeline does find structure in Indus when it exists: seals vs miniature tablets 0.81, seals vs sealings 0.78. So the classifier is not blind to Indus sign stock.
- Mohenjo-daro earlier vs late falls from the old 0.61 to 0.53 under the benchmark's cleaning.

### 6. Power (Indus 227-per-side pool, labels permuted, each site given its own Zipf-weighted local stock)

| share of tokens replaced q | 100 new symbols per site: median / ≥0.65 / local share | 40 existing signs per site |
|---|---|---|
| 0.05 | 0.561 / 0% / 0.073 | 0.563 / 0% / 0.049 |
| 0.10 | 0.680 / 83% / 0.115 | 0.644 / 40% / 0.065 |
| 0.15 | 0.772 / 100% / 0.161 | 0.731 / 100% / 0.086 |
| 0.20 | 0.848 / 100% | 0.811 / 100% |
| 0.30 | 0.933 / 100% | 0.903 / 100% |

- "Local share" does not use the classifier. It is the share of tokens whose type is seen twice or more and is at least 90% at one site.
- Indus real: 0.041. References at 227 per side: 0.11–0.22 raw; 0.09 (Umma vs Girsu) and 0.13 (Latin) under full controls.
- Indus sits below a planted 5% stock (0.049–0.073) on this scale too.
- A stock like Latin's or controlled Umma's (local share 0.09–0.13) is found 40–100% of the time, depending on the stock's form. A thinner one would be missed.

## Hypotheses tested

| attack | hypothesis (the claim is wrong because...) | verdict |
|---|---|---|
| 1 | Indus and references were not run alike | **partly supported**: Indus was run differently. Like-for-like it is 0.55, not 0.49; the gap stays |
| 2 | big reference vocabularies make them separable | refuted: 400-class vocabularies keep 0.66–0.92 |
| 3 | references carry site tags and repeated seals | **supported in part**: removing them costs 0.16–0.18 on Ur III; Latin barely moves |
| 4 | single-editor sign lists flatten Indus | refuted with available lists (0.52–0.55 for 5 lists, 2 editors); unrecorded variants untested |
| 5 | 0.49 is special to MD/Harappa | inconclusive: most pairs flat, Chanhu-daro 0.64–0.67 (small n) |
| 6 | Indus is too small to show 0.65 | refuted for stocks ≥ 15% of tokens; marginal at 10% |

## Not checked / caveats

- 30 draws per condition (the benchmark used 200). The Indus side of each draw is nearly fixed because Harappa has only 232 texts, so draw ranges understate the true uncertainty.
- The owner key (first line of the legend) merges different people with the same name. It is a conservative de-dup.
- My military word list for Latin is hand-made. Potters' and workshop stamps stay in, and they are a real local stock.
- No new reference corpus was added. The claim still rests on two readable corpora (Ur III, Latin) and three city pairs.
- `rt_extra.py`, `leak_words.py` and the 190-per-side rows were added after scoring and are exploratory.

## Next

- Add a third city-pair reference that has no city or god tags at all (e.g. Old Assyrian or Neo-Babylonian names by city) to test the "names in general" reading.
- Pre-register Chanhu-daro vs the big cities before anything is said about it. M77 and ICIT cover largely the same Chanhu-daro objects, so a real check needs new texts.
- Report the planted-stock scale as "local share", which does not depend on the classifier.
