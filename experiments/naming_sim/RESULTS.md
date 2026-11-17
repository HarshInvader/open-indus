# Naming-system simulation: which real naming system produces the Indus name-core statistics?

2026-11-15. Fable 5.2 plan item 11. Pre-registration: `docs/prereg/naming_sim.md` (hash-frozen before Indus was scored). Unit: distinct name (core) types. Held-out = `dev_heldout(version=2)`.

## Findings first

1. **None of the real naming systems tested produces the Indus name-core statistics.** Indus sits outside the range of all 11 real name lists, on dev and on held-out (pre-registered P1 and P2: both "outlier").
   - Indus's distance to its nearest real system is 1.57 on dev and 2.59 on held-out. Between real systems, the largest nearest-neighbour distance is 1.21 (median 0.87).
   - Against the larger lists (n ≥ 423), Indus is 7.6-8.9 away from every one of them, Germanic, Sanskrit, Chinese, Greek and Ur III alike.
2. **What makes Indus different, in plain words.** Real name systems build compound names from two partly separate stocks of elements: first elements and second elements. Their compound elements rarely occur as whole names on their own. Indus cores do neither.

   | statistic (dev, n = 800) | Indus | real lists (range) |
   |---|---|---|
   | sign tokens in longer cores that also stand alone (standalone) | 0.91 | 0.00-0.13 |
   | two-slot polarisation excess (pol_ex; 0 = one stock, 1 = two stocks) | 0.14 | 0.29-1.0 |
   | elements used in both positions (both_pos) | 0.71 | 0.00-0.60 |
   | unordered pairs attested in both orders (both_orders) | 0.063 | 0.000-0.043 |
   | one-element share (len1) | 0.26 | 0.00-0.67 |
   | head-direction index (hfi; 0.5 = none) | 0.45 | 0.10-0.75 |

   - Fixed order is not a sign of a naming system. Indus pairs are *less* fixed (6% of pairs reversed) than real compound names (0-4%). So the "91% fixed order" reported earlier is ordinary for compounds, not distinctive.
   - The standalone gap is partly caused by Indus's small sign inventory. Fitted generators run with the Indus inventory raise standalone close to the Indus value (Old High German z = 0.0). Even then they miss polarisation by about 10 SD and both-position use by 6-9 SD (secondary analysis S1). **The robust difference is that Indus has one shared stock of signs with no slot preference, while every real naming system has slot-preferring elements.**
3. **The fish family self-compounds more than any real animal-element class** (S2 passes). cls_self is 0.39 on dev and 0.53 on held-out, against at most 0.09 in real lists (Old High German). Germanic wolf/raven/bear themes, Sanskrit siṃha/nāga/aśva and Chinese 龙/虎/凤 do not combine with each other more than chance. This is not a like-for-like comparison: the fish class was picked for its cohesion.
4. **Numeral formulas are foreign to personal naming.** 41% of distinct dev texts carry a numeral+sign formula. In every non-calendrical name list, names containing a numeral are at most 2% (Sanskrit 1.2%, Chinese 1.6%, Plains 2%, Old English 0%). Only a calendrical system like the Mixtec reaches this rate, and there the numbers vary freely (1-13 with any day sign), which is the opposite of the fixed Indus formulas (tall2+M59) found in pair_numeral_long.
5. **Germanic vs Sanskrit vs Chinese is undecidable with these statistics, and this was declared before scoring.**
   - In calibration on real lists, 0 of 7 lists had a family member as nearest neighbour (about 1 expected by chance). The statistics track name structure (Greek, Sanskrit and Germanic dithematic names form a loose cluster, d = 0.60-1.1), not tradition or language.
   - So even a close match could not have pointed to a language family.
   - For the record, Indus is equally far from Old English (7.6), Sanskrit (8.5), Chinese given names (8.4) and Greek (8.7). Smaller lists look closer (Old Norse 2.4, Egyptian 1.6) only because the matched sample is small.
6. **The simulation route works within its own model but fails on real data.**
   - Fitted generators are perfectly identifiable from each other (LDA 0.998 at Indus size).
   - But 9 of 12 real lists, and Indus, are rejected by their own fitted generator.
   - When a real list is scored against the other systems' generators, it lands on a relative in only 1 of 6 cases.
   - Generator-based rankings are therefore reported only as descriptive (S1). The verdict rests on the model-free comparison.

**Bottom line for the programme:** the Indus "name core" does not behave like the personal-name stock of any tested tradition, including Germanic dithematic and Sanskrit/Dravidian-style compounds. Two readings fit the evidence:
- (a) the cores are not personal names: they could be epithets, titles, offices, commodities or clan emblems built from one lexical stock;
- (b) they are names written logographically in a way that hides slot structure, for example by a determinative/word-sign system that drops elements.

This experiment cannot separate (a) from (b). It does weaken every proposal that reads seal cores as dithematic personal names, whether Indo-Aryan, Dravidian or Germanic-like.

## Data (raw/, untrusted, read with `python -I`)

| list | source | types | segmentation |
|---|---|---|---|
| old_english, old_high_german, old_norse | Wiktionary given-name categories (`raw/wiktionary/`) | 1043 / 488 / 159 | etymology templates (`{{af}}`, `{{surf}}`, ...); unsegmented names split into attested themes, else one element |
| greek | Wiktionary Ancient Greek male names | 962 | same; includes some suffixes (-ιος) |
| sanskrit | Monier-Williams "N. of a man/king/..." (core_semantics/data/mw) | 7431 | key2 compound members |
| egyptian | Wiktionary Egyptian names | 171 | templates (theophoric) |
| ur3 | CDLI Ur III seal-legend names (codelib) | 3318 | hyphen elements, {d}DN whole (mixes logograms and syllables) |
| chinese_given / chinese_full | Chinese-Names-Corpus (typology/data) | 30653 / 60000 | characters |
| plains | Wikipedia categories (Lakota, Oglala, Cheyenne, Kiowa, ...) (`raw/wikipedia/`) | 101 | English translation words, stop words dropped |
| sangam | Wikipedia "List of Sangam poets" table | 540 | words (place, father, epithet, name + honorific) |
| mixtec | RULE-BASED (no open list): number 1-13 + day sign + 0-2 personal elements | 3000 | synthetic; generator fit degenerate, so excluded from the statistical ranking |

Not obtained: Elamite, Linear B (beyond the typology DAMOS set), heraldic blazons, gotra+name lists. Tamil (Wiktionary) was dropped: Unicode normalisation broke Tamil vowel signs and 86% of entries were unsegmented.

## Method

- **Statistics** (`stats.py`): defined on distinct types.
  - len1;
  - standalone (typology standalone_tok);
  - both_orders (type version of core_semantics "both orders");
  - hfi (core_semantics HFI_prod);
  - pol_ex and both_pos (pair_numeral_long polarisation vs orientation null);
  - cls_self (class self-compounding vs a token shuffle);
  - plus len3p and tpt as descriptive.
  - Indus cores use the frozen typology/core_semantics definition.
- **Generator** (`gen.py`), 11 parameters:
  - length mix;
  - Zipf inventory;
  - per-element slot propensity (Beta concentration = polarisation);
  - head rule (frequency to slot);
  - share of one-element names from the compounding stock, and the size of a separate monothematic stock;
  - lexicalised order;
  - lexical class with self-affinity.
  - Slot-aware drawing: first slot ∝ freq·π, last ∝ freq·(1−π).
  - Fitted by simulated minimum distance (`fit.py`): random search, then Nelder-Mead with common random numbers, then a grid polish.
  - Two earlier versions were discarded: v1 drew elements without regard to slot and could not produce two-stock polarisation (`fit_v1_slotblind.log`); v2 had no monothematic stock size (`fit_v2.log`).
- **Identifiability** (`identify.py`): each system's structure at the Indus frequency profile, 150 simulations at n = 800 and n = 423; LDA and ABC k-NN.
- **Validation** (`validate.py`, `selfcheck.py`, `realcmp.py calib`): leave-one-tradition-out, self-recognition, and nearest neighbours among real lists.
- **Primary scoring** (`realcmp.py indus`, pre-registered): model-free distance between Indus and each real list at matched n. This is the RMS of z-differences over 6 statistics, scaled by the across-system SD.
- **Secondary** (`score.py`): generator GOF and ABC.

## Pre-registered tests

| id | test | result | verdict |
|---|---|---|---|
| P1 | Indus dev inside real range (d_NN ≤ 1.21) | d_NN 1.57 (Egyptian, n = 171) | **outlier** |
| P2 | same, held-out | d_NN 2.59 (Plains, n = 101) | **outlier (replicates)** |
| P3 | separated by standalone+, pol_ex−, both_pos+ (\|z\| ≥ 2) | dev vs Egyptian: +2.3, −2.3, +0.9; held-out vs Plains: +4.2, −3.4, +2.8 | **not met on dev** (met on held-out) |
| P4 | Germanic vs Sanskrit vs Chinese | 7.6 / 8.5 / 8.4 (dev) | **undecidable** (declared in advance) |
| P5 | stable nearest system under leave-one-statistic-out | dev Egyptian 6/6; held-out Plains 5/6 | **unstable** (different systems) |
| S1 | any generator accepts Indus | 0/12, p = 0.007 (floor) on both splits | descriptive |
| S2 | fish cls_self above every real animal class | 0.39 / 0.53 vs 0.09 | **pass** |

**Registered verdict:** P1 and P2 are both "outlier", so **no tested naming system produces the Indus core statistics.**

Prereg slips, corrected here (neither changes an outcome):
- leave-one-tradition-out was 1 of 6 lists with relatives, not 1 of 7;
- the real cls_self maximum is 0.094 (Old High German), not −0.095.

## Caveats

- **Segmentation quality varies.**
  - Wiktionary templates cover only part of the Old Norse and Old High German names; theme splitting fills some of the gap.
  - Ur III "elements" include syllables.
  - Greek includes suffixes.
  - These choices push real lists towards *more* one-element names and fewer standalone themes, and cannot explain a gap of 0.91 vs ≤ 0.13.
- **The small lists** (Plains 101, Old Norse 159, Egyptian 171) are the "nearest" only because Indus statistics shrink at small n. With so few types their own statistics are noisy.
- **Inventory confound.** standalone depends on inventory size relative to n. The generator analysis at the Indus inventory shows that most of the standalone gap is an inventory effect. The polarisation and both-position gaps are not.
- **Scope.** Personal-name lists only. No epithet, title, toponym, clan-emblem or commodity-label corpora were tested. These are exactly the alternatives the result now points to.
- **The fish/animal comparison in S2 is not like-for-like.**
- **Mixtec** is rule-based, not an attested list.

## Next experiments

1. Test the non-name alternatives with the same statistics:
   - Ur III and Old Akkadian **titles/professions** (lu2-X, ugula-X);
   - Proto-Elamite and Linear B **commodity headings**;
   - Mesopotamian **toponyms**;
   - European **heraldic charges**;
   - Egyptian **epithet** strings.
   A one-stock, unpolarised, standalone-rich vocabulary is predicted for epithet/commodity systems.
2. Get real Elamite and Gu'abba "Meluhha village" names (CDLI prosopography) for a structure-only comparison.
3. Replace the parametric generator with a nonparametric resampler of each real list's element graph (preserving real both-order rates), so that self-recognition passes before any ranking.

## Files

- Code: `fetch.py`, `names.py`, `stats.py`, `gen.py`, `fit.py`, `identify.py`, `validate.py`, `selfcheck.py`, `realcmp.py`, `score.py`, `raw_stats.py`, `numerals.py`.
- Outputs: `results.json`, `realcmp_indus.json`, `realcmp_calib.json`, `score.json`, `identify.json`, `validate.json`, `selfcheck.json`, `raw_stats.json`, `numerals.json`, `fits/*.json`, `*.log`.
- Ledger rows: `ns_*` in `docs/test_ledger.csv`.
