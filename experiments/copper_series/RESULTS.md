# Copper tablets: calendar series, tallies or amulets?

Area: copper_series. Pre-registration: `docs/prereg/copper_series.md` (hash-frozen with `tests.py`, `build_types.py`, `types.csv` in `docs/prereg/HASHES.txt`, tag `copper_series`). Code, run from the repo root in order: `build_types.py` -> `tests.py` -> `explore_batches.py` (exploratory). Logs `*.log`, numbers `results.json`, tables `types.csv` (one row per type) and `tablets_typed.csv` (one row per tablet record), figure `accumulation.png`. Ledger rows `cs_h1a`..`cs_h3c` in `docs/test_ledger.csv`.

## Findings first

1. **The copper tablets are not a calendar series in any form we can detect.** None of the four pre-registered H1 tests passes.
   - There are too many types: 37 distinct legends (22 seen on 2+ tablets), more than any candidate cycle (6, 7, 12, 13, 27, 28). The richness estimate is Chao1 65 (95% CI 45-140), which excludes every candidate.
   - The types are far from equally common. One type (rhino-less ox-antelope legend M204-M245-M358-M342) is 30 of 178 tablets (17%); 15 types are known from one tablet. Gini 0.55, against at most 0.27 for any rotation of K <= 28 types (p < 2.5e-4 at every K, in every sensitivity version).
   - Texts are not linked in a ring. Types that share signs form **clusters** (modularity 0.38 vs 0.28 null, p=0.012), not a cycle: no Hamiltonian cycle exists, and degree spread is exactly at the null (p=0.52).
   - Numerals do not mark positions: the same value recurs across types more than chance (58 type pairs share a value vs 54 expected, p=0.77). Tall 3 (M89, inside the M336-M89 pair) alone sits on 6 types.
   - Formal verdict is **inconclusive, leaning against**, not "refuted". Two reasons: the ring test has low power (a planted ring is detected 38% of the time), and the evenness test cannot rule out a series whose copies survive in batches (see 4).
2. **Tallies (H2): inconclusive, with no positive sign.** Frequencies are skewed (H2b passes, it is the mirror of H1b), but nothing ties the skew to numbers.
   - Numerals are on 19 of 37 types, but no two types differ only by a numeral. Only 3 minimal pairs exist at all (M348 / M358 / M53 + M342), and none involves a numeral: 0 of 3, p=1.
   - Numeral value does not predict how common a type is: rho 0.26, p=0.28, n=19.
3. **Amulets (H3): half supported, and the half that fails is informative.**
   - Each type keeps its picture: 93% of pictured tablets show their type's usual picture, against 34% under permutation (p < 1e-4). This repeats the context/logograms result and is not independent of it.
   - Copper pictures do **not** follow seal popularity. The rank correlation is negative (rho -0.23, p=0.81 one-sided). The unicorn is 78% of seals but 3% of copper pictures. The hare, the horned archer and the endless knot are common on copper (10, 6, 4 tablets) and never appear on M77 seals.
   - Types with the same picture do not share more signs (p=0.12).
   - So the copper set is its own repertoire with fixed text-picture pairs, a "type emblem" system. It is not a cheap copy of the seal emblems.
4. **Exploratory caveat on evenness.** Suppose a 27- or 28-type series was issued in rotation, but tablets survive in cast batches averaging about 4 copies. That reproduces the 22 core types and their Gini (simulated median S=22, Gini 0.41; observed 22 and 0.42). Unevenness alone therefore does not kill a series. What stands against H1 is the combination: 15 more singleton types beyond the core, clustered rather than ring-like text links, and numerals that repeat.

## Type table (`types.csv`)

- **Sources.** The tablet list is `experiments/logograms/copper_tablet_types.csv` / `copper_tablets.csv`, re-verified here. All 135 M77 legends match `data/m77_texts.jsonl` (object_type "copper tablet"). All 190 ICIT TAB:C ids are present (189 Mohenjo-daro, 1 Kalibangan).
- **Type rule.** This is stricter than the logograms "family", which had merged 2-sign legends at edit distance 1. Two complete legends are one type only if:
  - both have 4+ signs and differ by at most one edit, or one 4+ sign legend sits inside the other;
  - and their M77 pictures do not conflict.
  This keeps M204-M245-M342 (rhino / M184 face) apart from M204-M245-M358-M342 (ox-antelope).
- **Fragments.** A fragment joins a type only if exactly one type fits it. 23 of 325 records stay unassigned.
- **Manual merge.** One merge was made by hand: MD 3302/3335/3364 = M-513..515. These are the same faces, transcribed as 336-89-87 // 72-194-169 in M77 and 72-194-169 // 106-336 in ICIT.
- **Counts.** n_est = max(M77, ICIT) objects per type. The two corpora overlap but share no ids, so this is a conservative union.

| type | n (M77/ICIT/est) | picture | legend | sign face / second text |
|---|---|---|---|---|
| T01 | 20/30/30 | ox-antelope | M204 M245 M358 M342 | |
| T02 | 12/16/16 | horned archer | M389 M407 M124 M169 M373 M287 M342 | horned-U (M362/363/364) x8 |
| T03 | 11/14/14 | hare | M65 M336 M89 M407 M169 M183 M169 | M355 x2 |
| T04 | 9/12/12 | elephant | M336 M89 M296 M342 | |
| T05 | 11/11/11 | goat-antelope, arching horns | M389 M72 M326 M342 | M346 x4 |
| T06 | 8/10/10 | goat-antelope, twirled horns | M70 M112 M194 M18 M211 M87 M169 | horned-U x9 |
| T07 | 5/9/9 | two-headed | M295 M87 M97 M252 M97 M25 M245 M245 | |
| T08 | 6/8/8 | ox-antelope / tiger / horned tiger | M53 M67 M407 M124 M169 | |
| T09 | 5/7/7 | goat-antelope, twirled horns | M102 M190 M48 M8 M342 M373 | |
| T10 | 7/4/7 | unicorn (+ two-headed, double-axe) | M345 M341 M18 M252 M97 M25 M245 M245 | |
| T11 | 4/6/6 | rhinoceros | M65 M72 M62 M342 | |
| T12-T22 | 2-5 each | buffalo, two-headed, endless knot, rhino (M184 face), bull, ... | see `types.csv` | M184, M51 faces; second texts |
| T23-T37 | 1 each | | 15 singletons, mostly 2-5 signs | M405, M96, M364, M346 faces |

## Tests (pre-registered, 10 counted; Bonferroni alpha 0.005)

| id | hypothesis | result | p | verdict |
|---|---|---|---|---|
| H1a | closed set of size K | S=37, coverage 0.92, Chao1 65 (45-140); core 22 types, coverage 1.0, CI degenerate at 22 | n/a | fail (passes only in the M77-only sensitivity: Chao1 32, CI 28-52) |
| H1b | rotation-even frequencies | Gini 0.55 (core 0.42) vs uniform-K 97.5% ceiling 0.15-0.27 | <2.5e-4 at every K | fail |
| H1c | text ring | no Hamiltonian cycle; degree CV 0.50 vs null 0.50 | 0.52 | fail (power 0.38) |
| H1d | numerals = position | 58 value collisions vs 54 null; values {1,2,3,4,7} | 0.77 | fail |
| H2a | types differ by numerals | 0/3 minimal pairs | 1.0 | fail (power near zero: 3 pairs) |
| H2b | skewed frequencies | Gini 0.55, Zipf exponent 1.16 | <2.5e-4 | pass |
| H2c | value vs frequency | rho 0.26, n=19 | 0.28 | fail |
| H3a | fixed picture per type | 0.93 vs 0.34 null (87 pictured M77 tablets) | <1e-4 | pass (not independent of context Q2b) |
| H3b | copper tracks seal popularity | rho -0.23 over 16 picture classes | 0.81 | fail |
| H3c | same picture, shared signs | Jaccard difference 0.034 | 0.12 | fail |

**Verdicts (pre-registered rules).**

| Hypothesis | Verdict | Why |
|---|---|---|
| H1 calendrical / ritual series | inconclusive, leaning against | fails H1a-d; not formally refuted because ring power is 0.38 |
| H2 tallies | inconclusive | skew yes, numeral contrast no; the minimal-pair test is nearly powerless |
| H3 amulets | type emblem only (H3a) | fixed pairing yes; popularity tracking clearly no |

**Sensitivity.** The H1b/H2b result is the same whichever count or grouping is used:
- n_sum (upper-bound counts): Gini 0.58;
- M77 only: 0.47;
- ICIT only: 0.55;
- lumped types: 0.55;
- M77 picture classes instead of legends: 15 classes, Gini 0.42 vs ceiling 0.33.

**Power.**
- Evenness: the test rejects uniformity for a Zipf(1) law over 40 types in 100% of simulations. It has full power against a skewed law, but not against batch survival (finding 4).
- Ring: power is 0.38. A planted ring raises degree regularity only modestly, because the shared formula segments already link many types. A ring hidden under that formula noise could be missed.
- H2a: 3 minimal pairs give no power.

## Structural comparison with known series (descriptive)

- **Size.** The candidate cycles have 6, 7, 12, 13 or 27/28 members. The copper set has 37 legend types (22 repeated) and 15 picture classes. Only the nakshatras come close, and only if all 15 singletons are discarded.
- **Pairs.** The nakshatra list has 3 "former/latter" pairs (Phalguni, Ashadha, Bhadrapada): frequent members that share a name and differ by one modifier. Copper has exactly 3 minimal pairs. All three are among rare two-sign "X + jar" singletons (M348 / M358 / M53 + M342), not among the frequent types.
- **Shared elements.** Month and nakshatra names share few elements, and they share them in pairs. Copper legends share recurrent formula blocks in clusters: M336-M89, M97-M25-M245-M245, M407-M124-M169, M112-M194, M389-M72. That is a modular graph, not a chain.
- **Emblems.** In the Chinese 12-animal cycle, each position has exactly one animal. On copper:
  - One legend carries three different pictures (T08: tiger, horned tiger, ox-antelope).
  - One sign face (horned-U) serves two legends.
  - Pictures include non-animals (endless knot, double-axe).
  A calendar position would not swap its emblem.

## Caveats

- n_est is a lower bound on the objects (the corpus overlap is unresolved). Sensitivities bracket it, and no verdict changes.
- The type rule decides the type count. The looser logograms rule gives 64 families, and lumping gives 36. Both make "too many types for a cycle" stronger or leave it unchanged.
- All tablets are from Mohenjo-daro, with no usable stratigraphy here. A series used for a short period, with most types lost, cannot be excluded by frequency data alone.
- H3a overlaps earlier tests (context Q2b, logograms T3), so it is not new evidence.
- The analysis uses M77 fs80 pictures only. The ICIT symbol field is too coarse on copper.

## What would change the verdict

- **New finds.** Newly published copper tablets (CISI vol. 3+) should fall into known types at about the coverage rate, 0.92 (frozen prediction: within +-0.15). A closed series predicts at least 0.90 and no new types. A run of new types would push further against H1; all-known types would fit both.
- **Find-spot data.** If excavation lots show that each type comes in batches from one context, and the batch-corrected type count is at most 28, H1 would need re-testing on lots rather than objects.

## Next experiments

1. Re-count by find-spot or batch (Mackay/Marshall loci, if digitised): count types per lot instead of objects. This is the only way to separate batch survival from issue frequency.
2. Test the two-tier structure directly: the copper "register" formula (M407-M124-M169, M97-M25-M245-M245, M336-M89) against the variable part of each legend. If the variable part is a name and the formula is a fixed title, the types are named entities (deities or emblems), not positions.
3. Compare with Harappa moulded tablets (also mass-produced types). Do they show the same skew and clustering? A shared production logic would argue against a copper-specific calendar.
