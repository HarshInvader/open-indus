# Prereg: uniformity paper, step 1 (Linear B reference, name-free references, within-city floor)

Written 2026-11-21, before any condition below was scored. Code: `experiments/uniformity_paper/step1/build.py` (pools) and `s1.py` (conditions, draws, report), hashed with this file in `docs/prereg/HASHES.txt` (tag `uniformity_paper_step1`). Seen before writing: pool sizes per condition (`sizes.json`, `sizes.log`), token-tag counts, and the published numbers of `uniformity_benchmark` and `redteam_uniformity`. No AUC of any new condition has been computed.

## Claim being strengthened

Mohenjo-daro vs Harappa seal texts cannot be told apart by sign use (ICIT, 227 per side: median AUC 0.549, draws 0.504-0.589; 0.52-0.55 under five sign lists), while Ur III seals from different cities separate at 0.71-0.87 with city names, gods and repeated owners removed, and Latin Britannia vs Germania labels at 0.68.

## Method (fixed)

Every condition runs through the benchmark's own `clean()` (drop strings found at both sides, then the non-chaining greedy de-dup from `fish_tick_closer_v2/dedup.py`), `draw_n()` (Indus length mix, balanced sides) and `score()` (frozen site_signal NB pipeline, one permuted-label AUC per draw), called the way `redteam_uniformity/rt.py` calls them. 30 draws per condition, seed 20261123. Size per side = the smaller side after cleaning, capped at 227; where one text per group is drawn (Linear B: one line per tablet), the cap is the number of tablets. Statistic: median AUC over draws; null = permuted-label AUCs.

**Indus comparator.** 0.549 (rt, ICIT 227 per side). "At Indus level" means a median ≤ 0.589 (the top of the Indus draw range). Indus at 100 per side was 0.520 (rt), for comparisons at smaller sizes.

**Planted-answer power gate.** For each primary condition, the same pool and size with labels permuted and an rt.plant `new100` local stock at q = 0.15. Detection = draw AUC ≥ max(0.65, null q95 of the unplanted condition). If detection < 80% of draws, that condition's verdict is **underpowered**, whatever its median.

### A. Linear B, Knossos vs Pylos (DAMOS, CC BY-NC-SA 4.0; already on disk, gitignored)

Unit = one tablet line, at most one line per tablet per draw. Lines with brackets, erasures, "?" or lost numerals are dropped; under-dots are removed (reading kept). Tokens: syllabic words as written, ideograms and measure signs as written, every numeral → `NUM`. Names: NeuroDecipher (Luo et al. 2019) `linear_b-greek.names.cog` (proper names) + Wiktionary Mycenaean proper nouns = 471 forms; common words = NeuroDecipher cognates not in the names file = 460 forms. A word with enclitic -qe / allative -de / -pi is looked up without it.

| id | condition | size |
|---|---|---|
| **A1** | whole (all tokens) | 227 |
| A2 | whole, frame removed (benchmark rule: commonest 38.3% of tokens) | 227 |
| A3 | syllabic words only | 227 |
| A4 | ideograms and measure signs only | 75 |
| A5 | whole, tagged names removed | 227 |
| A6 | syllabic words, tagged names removed | 227 |
| **A7** | strict name-free: listed common words + ideograms + `NUM` only | 115 |
| **A8** | whole, series-balanced (same number of tablets per Bennett series letter at both sites) | 116 |
| A9 | whole, words split into syllabic signs (unit = sign, as Indus) | 227 |
| A10 | strict name-free + series-balanced | 75 |

Proto-Elamite: not run. In `experiments/protocuneiform/raw/cdli_atf` only 22 transliterated tablets have a secure non-Susa findspot (Anšan), under the bar of 40; Proto-Elamite entries on one tablet are not independent texts.

### B. Name-free references, and how much naming Indus could hold

- **Ur III** (ORACC part of speech, same pool as the benchmark, checked word for word): drop every word whose POS is a proper noun (PN, RN, DN, SN, GN, FN, WN, TN, MN, AN, any `*N` except N), unlemmatised (X, u), or carries a name determinative ({d}, {ki}, {iri}, {uru}, {kur}, {m}, {f}, {disz}, {1}). Keep titles, offices, common nouns, verbs, numbers.
  - B1 name-free; **B2 name-free + one legend per owner** (rt rule, applied before names are removed); B3 = B2 + frame removed. For Umma vs Girsu (ug: 197 / 76 / 56 per side) and Puzriš-Dagan vs Nippur (pn: 105 / 40 / 25).
- **Latin** (EDH labels, Britannia vs Germania, re-tokenised from the edited transcription to diplomatic-style abbreviations; 1,585 of 1,596 labels match the benchmark tokens exactly). Proper noun = capitalised in the transcription and never written lower-case anywhere in EDH; Roman numerals kept.
  - B4 transcription tokens, nothing removed (calibration of the re-tokenising); **B5 name-free**; B6 name-free + rt military/numeral labels dropped; B7 name-free + frame removed.
- **Linear B**: A5-A7, A10 above.
- **Reverse power test (BW).** Indus ICIT pool, 227 per side, labels permuted inside each draw, then a share r ∈ {0.1, 0.2, 0.3, 0.5, 0.75, 1.0} of texts gets a local name from its site's own 100-name stock (Zipf weights). Two name forms: `sign` (one new site-specific symbol replacing one sign) and `spelt` (a pair of existing common Indus signs, so both sites spell from one shared sign list, replacing two adjacent signs). Report the smallest r with ≥ 80% detection (detection = AUC ≥ max(0.65, null q95 of C7)) and the largest r whose 2.5-97.5% draw range still contains the observed Indus median (C7).

### C. Within-city floor (M77 seals, complete, no break marks; one object side = one text)

Area from the M77 locus code, checked against excavation field numbers in `experiments/old_registers` (loci 31-34 are DK: 483 + 120 + 8 + 5 field numbers, 0 others; loci 16, 17, 18, 20, 22 are HR / VS).

| id | condition | size |
|---|---|---|
| **C1** | Mohenjo-daro DK (loci 31-34) vs HR + VS (16, 17, 18, 20, 22) | 169 |
| **C2** | Mohenjo-daro DK only, deep vs shallow: level ≤ median (−11 ft) vs above; level 0 (unknown) excluded | 204 |
| **C3** | Harappa mound F (loci 40-45) vs AB (46-49) | 48 |
| C4 / C8 / C5 | M77 Mohenjo-daro vs Harappa (between cities), same editor, at the sizes of C1 / C2 / C3 | 169 / 204 / 48 |
| C6 | ICIT Mohenjo-daro DK vs HR + VS (area from the CISI field number) | 90 |
| C7 | ICIT Mohenjo-daro vs Harappa at 227 (rerun of the rt comparator with this seed) | 227 |

Gates: A1, A7, A8, B2 (ug, pn), B5, C1, C2, C3, C7.

## Predictions

| id | prediction |
|---|---|
| P-A1 | A1 Knossos vs Pylos whole ≥ 0.65 |
| P-A2 | A8 series-balanced ≥ 0.65 |
| P-A3 | A7 strict name-free ≥ 0.65 |
| P-B1 | B2 Ur III Umma vs Girsu, name-free + owner de-dup ≥ 0.65 |
| P-B2 | B5 Latin name-free ≥ 0.60 |
| P-B3 | BW `sign` names reach 80% detection at r ≤ 0.3; `spelt` names at r ≤ 0.5 |
| P-C1 | C1 between 0.45 and 0.60 |
| P-C2 | C2 between 0.45 and 0.60 |
| P-C3 | C3 below its own null q95 |

## Verdict rules (fixed now)

**A (Linear B).** Gate fails for A1 or A8 → **underpowered**. Else: **supports the claim** if A1 ≥ 0.65 and A8 ≥ 0.65. **Badly weakens the claim** if A1 ≤ 0.589 or A8 ≤ 0.589; this is stated plainly: a genre-matched administrative script from two palaces is then as uniform as Indus. Otherwise **weak reference** (claim weakened).

**B (names).** A name-free reference *separates* if its median ≥ 0.60, is above its own null q95 and its gate passes; it is *at Indus level* if its median ≤ 0.589 and its gate passes; it is *underpowered* if its gate fails. The three name-free references are B2 Ur III Umma vs Girsu, B5 Latin, A7 Linear B.
- **Objection answered**: ≥ 2 of 3 separate.
- **Objection stands**: ≥ 2 of 3 are at Indus level. Then the paper must say Indus is consistent with name-free writing and the claim narrows to "no city-bound name stock".
- **Partly answered**: otherwise (including underpowered cases).
- The reverse power test sets the wording on how much local naming Indus seals could carry; it has no kill.

**C (floor).** Δ = between-city − within-city at matched size and editor (C4 − C1, C8 − C2, C5 − C3). Primary: C4 − C1.
- **City signal above the floor** if Δ ≥ 0.05.
- **No city signal above the floor** if |Δ| < 0.05: 0.55 is a same-city number.
- **Areas differ more than cities** if Δ ≤ −0.05.
- Gate fails for C1 → **floor underpowered**.

Tests: about 60 conditions, descriptive medians with gates; no p-value decisions, so no multiple-test correction. Any condition added after scoring is labelled exploratory. Deviations go in `experiments/uniformity_paper/step1/RESULTS.md`.

## Known weaknesses (stated before scoring)

- Linear B lines are drawn from palace archives with different series mixes (Knossos mostly D sheep tablets; Pylos A, E, C, J). A8 / A10 balance series letters, which matches subject class only roughly.
- The Linear B name lists cover only names with a known Greek reading; most personal names are untagged (`unk`). A5 / A6 therefore remove only part of the names; A7 / A10 (whitelist) remove all of them and many common words too.
- The Latin proper-noun rule depends on editors' capitals; imperial titles (AVG) count as names, and a few gods' names that also occur lower-case (e.g. MARTI) count as common.
- `clean()` drops any string found at both sides. After names are removed, many short generic legends ("dub-sar dumu") occur at both cities and are dropped; this is the benchmark rule and applies to Indus in the same way.
- C1 mixes area with excavator (Mackay DK vs Marshall HR / VS) and partly with date.
