# Anchor cross-read: can a handful of digraphic name pairs be checked with no language model? (DRAFT; not sealed; no code exists and no test statistic has been computed on any real pair)

Status: **v4, sealed** 2026-11-25 (tag `anchor_crossread`). Drafted by Fable from `docs/fable_brief10.md`, study 1. A fresh review of v1 returned FIX, 12 items, and a pre-seal check of v2 returned FIX, 6 items; all are applied (lists at the end). K0 was moved to m = 15 before sealing, on planted power only (lead's design decision). Clause (b) is unruled; every reading holds under either ruling. No study code existed at sealing.

## Question
- A set of m objects each pairs a known name with a legend in an unknown script. Can a test that uses no language model tell sets where the name is spelled in the legend from sets where it is not?
- How many pairs does it need, at Ur III legend shape and at Indus sign statistics?
- The rehearsal runs on Ur III sealed tablets, where the answer is known. **No Indus key is scored, no Indus text is read, and no outcome supports or counts against any Indus reading.**

## Why
- `docs/prereg/anchor_objects.md` section 4 waits for `m_star` under a wrong-language model. `name_anchors` showed that number does not exist (power 0.27 to 0.40 up to 10 pairs). So today an anchor-grade find would be filed as "recorded, not yet testable" for ever.
- Brief 9 counted that 10 anchored values cover about 2 runs of 4 or more signs in M77. Clause (b) of the 2027 bar can then only be met by a prediction that is not a fit. Predicting a held-out name's spelling from the other names fits no language model. Whether it counts as clause (b) is Decision 1, which is open.
- Brief 10 measured that two random M77 seal texts share a sign 39.5% of the time. A naive "shared sound, shared sign" check passes by chance, so the test needs a measured false-pass rate before the day it is needed.

## What was seen before this draft
- **Repo results:** `name_anchors`, `sealing_hunt`, `ur3_legend_refute` (sealed, done), atlas 1.8 to 1.10 and 9.1 to 9.3, brief 10.
- **Label-free counts, made for this draft** with single-process scratch scripts outside the repo, each under 10 seconds, at lowest priority. They read the CDLI catalogue and transliterations, the public OGSL sign list, and M77 sign identifiers. The tables under "Count gate" hold all of them. They count pairs, lengths, sign sharing and repeated sounds.
- **Timing on synthetic random sets only** (random symbols, no Ur III pair, no Indus sign). One value of the statistic at m = 10 with full freedom takes about 16 ms.
- **Pre-seal planted calibration (v2), on synthetic sets only.** The statistic ran on planted random-symbol sets to fix the penalty weight, with the grid and rule written first. The table is under "Penalty weight". The review ran the same generator with another seed, and its counts stand beside it.
- **The review's label-free count of sign sharing in the mismatch pool** (an overlap count, not T). It is under "Shape of the pools".
- **The list of mismatch-pool names** (v2), read to write the cleaning rule. No statistic was computed on them.
- **Not seen:** the statistic T, any p-value, any pass count, or any alignment found by the search, on any real Ur III pair, real mismatch or M77 text.

## Prior art
Opened 2026-11-25 with curl and the User-Agent `open-research-site/1.0`. Nothing paywalled was bypassed.

- **Names started the hand decipherments.**
  - Ventris guessed that sign groups found only in the Cretan tablets were Cretan place names, and built values from them. https://en.wikipedia.org/wiki/Michael_Ventris
  - The Linear B page credits Kober's triplets for the grid he used. https://en.wikipedia.org/wiki/Linear_B
  - George Smith read the Cypriot syllabary from the Idalion Phoenician and Cypriot bilingual. https://en.wikipedia.org/wiki/Cypriot_syllabary and https://en.wikipedia.org/wiki/Idalion_bilingual
  - Brief 10 section 3 opened the Egyptian, Old Persian, Anatolian hieroglyphic, Carian and Linear Elamite cases. Young scored 6 of 13 values right from one or two names.
- **Computational decipherment aligns names and cognates, but with a known related language and hundreds of pairs.**
  - Snyder, Barzilay and Knight 2010 map 29 of 30 Ugaritic letters and 60% of cognates, given a Hebrew lexicon. https://aclanthology.org/P10-1107.pdf
  - Luo, Cao and Barzilay 2019 add a Linear B run on 455 Greek proper nouns, built to mimic the place-name route. https://aclanthology.org/P19-1303.pdf
  - Luo et al. 2021 score Iberian against personal names known from the Latin Ascoli bronze and report 75% top-10 accuracy. https://aclanthology.org/2021.tacl-1.5.pdf
  - Berg-Kirkpatrick and Klein 2011 (https://aclanthology.org/D11-1029.pdf) and Knight and Yamada 1999 (https://aclanthology.org/W99-0906.pdf) were downloaded and their abstracts read. Both work on the same known-language setting.
  - Tamburini 2025, doi:10.3389/frai.2025.1581129, abstract read. It allows one-to-many and many-to-one sign mappings. It states no chance baseline for a small set of name pairs.
- **The null used here is standard in historical linguistics.** Kessler 2007 tests whether words are more alike "when paired up by semantics than when paired up at random". https://aclanthology.org/W07-1302.pdf. A 2024 review dates the permutation test to Oswalt 1970. https://aclanthology.org/2024.naacl-long.141.pdf
- **Not opened (unverified):** Oswalt 1970; Kessler 2001, *The Significance of Word Lists*; Ringe 1992; Chadwick, *The Decipherment of Linear B*; Desset et al. 2022, doi:10.1515/za-2022-0003, where the publisher again returned an empty HTTP 202.
- **Leave-one-out validation of anchors.** One web search found no work that holds out one bilingual name and predicts its spelling from the rest as a formal test. The search was short, so "not found" is weak evidence.

**What is established.** First values have always come from names, and a decipherer checks them by reading a new name with them. Machines can align names when they have a related language and a large list. Re-pairing is an accepted null for chance resemblance. **What nobody in the opened sources gives** is a false-pass rate for cross-reading 3 to 10 name pairs when the name's place in the legend is unknown. That is this study.

## Count gate (label-free; brief 10's numbers rechecked)
Source: the CDLI dump under `experiments/short_labels/raw/cdli/`.

### Brief 10's numbers under its own rule
| quantity | brief 10 | recount | note |
|---|---|---|---|
| Ur III texts with a transliterated legend | 23,369 | 23,362 | 9 legend-bearing P-numbers occur twice in the dump; each now counts once |
| ... that also have a `kiszib3 X` line | 14,894 | 14,891 | same cause |
| ... X is the first word of a legend | 10,044 | 10,041 (67.4%) | same cause |
| mismatched tablets | 4,850 | 4,850 | confirmed as a count; see the next table for what they are |
| distinct matched names; on 2 or more tablets | 712; 401 | 712; 401 | confirmed |
| distinct intact (name, legend) pairs | 1,623 | 1,623 | confirmed |
| usable owner names; sign types; collision | 505; 283; 0.020 | 505; 283; 0.020 | confirmed |
| name length, median | 3 signs | 3 signs | confirmed |
| legend length, median (quartiles) | 12 (10, 12, 14) | **9 (8, 9, 11)** | 93% of legend lines end in a space, and the brief's split counted one extra sign per line |
| owner name as a share of the legend | 30% | **33%** | follows from the length |
| P(3+ checks) at m = 5, 6, 8, 10 | 0.56, 0.74, 0.96, 1.00 | **0.14, 0.29, 0.69, 0.91** | the brief counted check instances and counted the determinative as a name unit; the recount counts distinct repeated sounds |
| P(10+ values fixed) at m = 4 | 0.92 | 0.79 (0.98 at m = 5) | determinatives no longer count as values |

### The 4,850 mismatches are not 4,850 negatives
Under the brief's first-word matcher the mismatched tablets split as follows (the scratch tokeniser gives 4,852).

| class | tablets |
|---|---|
| the sealer's name stands in the legend, but not as its first word | 1,288 |
| every legend on the tablet is damaged | 1,455 |
| name damaged or outside 2 to 6 signs | 174 |
| clean | 1,935 |

Of the clean ones, the commonest "names" are titles: `ensi2-ka` 551 tablets, `nam-sza3-tam` 318. Many of the rest are the same name in another editor's reading, such as `lu2-saga` beside `lu2 sa6 ga`. Real negatives are far fewer than the brief said, and they need a stated rule.

### Frozen pools (sign level)
A tablet enters only if it has exactly one `kiszib3 X` token and exactly one legend. Legend and name carry no `[ ] # < > ?`, no `...` and no `x` sign. Every reading maps to an OGSL sign. The name has 2 to 6 signs, at most one determinative and at least 2 sound units.

**Cleaning rule (v2; applied to every tablet before it is sorted into a pool).** X is dropped if any of these holds.
- It is one of `asz-a`, `dub-sar`, `sanga`, `szabra`, `ugula`, `sukkal-mah`, `nig2-dab5`, `didli-a`, `bala-a`, `im-sar-a`, `ugu2-a`, `esz-am3`, `dab-ba`.
- It starts with `ensi2`, `nam-sza3-` or `sza13-dub-ba`.
- It ends in `-e-ne`, `-ta` or `-sze3`.
- **Case form.** Its last reading is `ra`, `bi` or `ka`, and X without that reading is itself the `kiszib3` name of another candidate tablet.

The listed terms came from reading the names in the v1 mismatch pool. The rule is blind to the pool a tablet would join, so it also costs true pairs: POS fell by 16.

- **POS:** the name's sign sequence stands in the legend as a contiguous run, anywhere.
- **VAR (variant spelling, kept out of both pools):** not POS, and either 2 or more name signs stand in order inside some legend window of k + 1 signs, or the name's sounds joined as one string stand inside the legend's sounds joined as one string. A reading written `valuex(SIGN)` loses its `x` as well as its index. That sends `lugal-uszurx(|LAL2.TUG2|)` with the legend `lugal uszur3` to VAR. In v1 it sat in NEG and was a true pair.
- **NEG:** everything else. The sealer's name is not in the legend by any rule above.

| | tablets | distinct pairs | distinct names | Umma / Girsu names | v1 pairs; names |
|---|---|---|---|---|---|
| POS | 6,303 | 1,316 | 483 | 227 / 212 | 1,332; 493 |
| NEG | 617 before the sound rule | 224 | 154 | 63 / 57 | 256; 179 |
| VAR | 213 before the sound rule | 128 | | | 153 |

The NEG names stand on 56 distinct legends at Umma and 53 at Girsu. Dropped on the way: 5,113 tablets with a damaged legend, 1,289 titles and terms, 570 damaged names, 471 with several names or seals, 161 by name length, 70 case forms, 57 with an unmapped reading, 25 with two determinatives, 7 numerals.

### Shape of the pools
| | POS | NEG |
|---|---|---|
| name signs, median | 3 | 3 |
| legend signs, median (quartiles) | 9 (8, 9, 11) | 10 (9, 10, 12) |
| legend lines, median | 3 | 3 |
| names with one determinative | 39% | 17% |

- **The name opens the legend in 91.0% of POS pairs** (1,198 of 1,316). The brief's 1,623 pairs had it first in every case, by construction of its matcher. A span-free arm on that pool would have been a fixed-position test without saying so.
- **Legends share far more than Indus texts do.** Two POS legends share a sign 93.4% of the time and 2 or more signs 69.3%. Outside the name span they still share one 88.1% of the time. `TUR` (dumu) is in 89% of legends, `AN`, `DUB` and `SAR` in 56%. A name shares a sign with a random other legend 42.2% of the time.
- **Mismatched tablets are not unrelated pairs (the review's count, redone on the cleaned pool).** A NEG name shares at least one sign with its own legend more often than with another legend it could be re-paired with: Umma 51% against 32%, Girsu 39% against 30%. The review found 50% against 33% and 38% against 29% on the v1 pool. A sealer often used the seal of a relative or a superior, and families share name elements. 31 Umma and 35 Girsu NEG names share no sign with their own legend.
- **Re-pairing inside NEG.** 92% (Umma) and 94% (Girsu) of cross pairs meet the NEG rule. A random re-pairing of 10 meets it throughout 47% and 54% of the time.
- **Name signs and sounds.** One pair per distinct name gives 205 sign types and 201 sounds. 47 sounds are written by more than one sign, and 45 signs write more than one sound.
- **Placements** per pair under the frozen family below: median 38, largest 282.

### How many values, and how many with their own check
Sets of m distinct POS names, 4,000 draws. A sound is one reading with its index digits dropped. Determinatives are silent.

| m | values fixed, median | P(10+ fixed) | sounds in 2+ names, median | P(3+ such) | P(10+ such) |
|---|---|---|---|---|---|
| 3 | 8 | 0.21 | 0 | 0.01 | 0.00 |
| 4 | 11 | 0.79 | 1 | 0.04 | 0.00 |
| 5 | 13 | 0.98 | 1 | 0.14 | 0.00 |
| 6 | 15 | 1.00 | 2 | 0.29 | 0.00 |
| 8 | 20 | 1.00 | 3 | 0.69 | 0.00 |
| 10 | 23 | 1.00 | 4 | 0.91 | 0.00 |
| 15 | 32 | 1.00 | 8 | 1.00 | 0.21 |
| 20 | 39 | 1.00 | 11 | 1.00 | 0.81 |
| 25 | 46 | 1.00 | 15 | 1.00 | 0.99 |

**This corrects brief 10's "six to eight pairs".** Six to eight pairs fix 10 values and give about 2 or 3 of them a held-out check. Ten pairs give 4. Ten values that each have their own held-out check need about 20 pairs. Which of the two the bar means is Decision 1.

### Indus side (M77 sign identifiers only)
1,575 distinct seal texts of 2 or more signs, 7,685 tokens, 370 types, median length 5. 852 texts have 5 or more signs. Two random texts share a sign 39.5% of the time and 2 or more 9.7%. The commonest sign is in 47% of texts. All as brief 10.

**Gate: passes.** POS is ample. NEG is thin: 63 Umma and 57 Girsu names on 56 and 53 distinct legends. That gives 3 disjoint sets of 15 per city, or 5 of 10, so 20 NEG sets at those rungs must overlap. "Sets" says how.

## Data (all public or already held)
- CDLI dump, as above.
- Oracc Global Sign List, CC0, https://oracc.museum.upenn.edu/json/ogsl.zip, 248,486 bytes, SHA-256 `46d8a29c11c351baa922c912c4472d6fb7ec7f79e76d4d473f29d58d4caf860f`. The study keeps its own copy in a new empty `experiments/anchor_crossread/raw/ogsl/`. It does not read the copy under `experiments/certify_size_curve/`.
- `data/m77_texts.jsonl`, sign identifiers only, for arm C.

## Symbols and sounds (frozen)
- **Legend symbol.** Each reading is replaced by its OGSL sign name. A compound sign is one symbol. A determinative is its sign. When a reading belongs to several signs, the one with the fewest components wins, then the shortest name, then alphabetical order. The test sees symbols as opaque labels.
- **Name sound.** Each reading of the name on the `kiszib3` line, lower case, index digits dropped, and the `x` of a `valuex(SIGN)` reading dropped. Determinatives are dropped, since the sealer's name reaches us as sounds. So `sa` and `sa6` are one sound with two signs, and `lamma` and `kal` are two sounds with one sign.
- **Truth, used for scoring only.** A unit is placed correctly when it lands on the legend position of its own sign in the POS run.

## The test (frozen)
### Alignment family
A placement puts the k sound units of a name on legend positions in order. The positions are contiguous, or contiguous with one legend sign skipped between two units. No name unit is skipped.
- **Arm B2 (primary, full freedom).** Any start. The direction is free for each pair independently, so one set may mix forward and reversed placements. The calibration script does the same.
- **Arm B1.** Any start, forward only.
- **Arm A.** The span is given, forward. Each legend has a span start: the start of its own true run for a POS legend, position 0 for a NEG legend. A name of k units paired with a legend, in the observed pairing or in a re-pairing, gets the window of k + 1 signs from that legend's span start, cut at the legend's end. Only the choice of the skipped sign is free. The window is k + 1 and not k because a k-sign true run would leave no skip, and the observed pairing would then have less freedom than its re-pairings.
- **No placement.** In every arm, a name with no placement in the legend it is paired with earns no credit and takes part in no a(s, y).

### Statistic T
For a joint choice of one placement per pair:
- a(s, y) is the number of objects whose name has sound s with a unit of s placed on symbol y.
- x(s, y) is the number of objects whose name lacks s and whose legend holds y anywhere.
- credit(s) is the largest value over y of a(s, y) − 1 − 0.25 · x(s, y), or 0 if that is negative or a(s, y) < 2.
- G is the sum of credit(s) over sounds.

**T is the largest G the search finds.** The search starts from a random placement for every pair. It sweeps the pairs in order, moves a pair to the placement with the highest G, and moves only on a strict gain. It stops when a sweep changes nothing, or after 20 sweeps. Six restarts, and T is the best of the six. The x term stops signs that sit in most legends, such as dumu, from earning credit.

### Penalty weight (fixed in v2 by planted calibration, before sealing)
- **Stated before the run:** grid 0, 0.25, 0.5, 1.0. Synthetic planted sets only, m = 10, arm B2, 20 sets per weight, 199 re-pairings, pass at b ≤ 1. The weight with the most passing planted sets wins, and a tie goes to the smaller weight.
- **Generator:** the review's. Random symbols at Ur III shape: 400 names over 203 sounds, 46 sounds with a second sign, 46 signs with a second sound, the owner name first, a `DUB SAR` pair in 56% of legends, and a `TUR` sign followed by another name in 89%.

| weight | this draft, seed 20261125 | the review, seed 7 |
|---|---|---|
| 0 | 3 of 20 | 5 of 20 |
| **0.25** | **13 of 20** | **17 of 20** |
| 0.5 | 9 of 20 | 11 of 20 |
| 1.0 | 5 of 20 | 9 of 20 |

- **Chosen: 0.25.** Both runs rank it first.
- Recorded at 0.25, deciding nothing: planted mismatch sets 0 of 20; planted kin sets, where the legend owner takes the sealer's first unit half the time, 0 of 20; the easy plant Kp below, 20 of 20.
- **The gap between 13 and 17 is seed noise (pre-seal check).** Both runs used 199 re-pairings. Pooled with the check's own sets, planted power at m = 10 and weight 0.25 is about 0.80: 29 of 40 at 199 re-pairings and 32 of 40 at 999. A test with power 0.80 meets a 16 of 20 bar only about 60% of the time.
- **Larger planted sets.** m = 15 passed 12 of 12 and m = 12 passed 6 of 8.
- **Pre-seal design decision (study lead; based on planted power only, no real pair).** K0 moves from m = 10 to m = 15, the strongest kill that is powered. m = 10 and m = 12 stay as rungs of cell P.
- **Power statement.** Calibrated at 199 re-pairings; sealed at 999. Planted power at m = 15 is about 1.0 (12/12). At m = 10 it is about 0.8, so a fail at 10 alone means 10 pairs is at the edge, not that the route is closed.
- This is a calibration on planted sets, made before sealing and disclosed as such. No real pair was scored.

### Null and pass rule (one-sided)
- Re-pair the m legends among the m names at random, 999 times, and recompute T with the same search each time.
- b is the number of re-pairings with T at or above the observed T. Ties count against the set.
- **A set passes if (1 + b) / 1000 ≤ 0.01.** The test is one-sided, in the predicted direction: the real pairing scores higher. An observed T of 0 never passes.
- The run may stop a set's re-pairings once b reaches 10. That does not change the verdict.
- **NEG sets use restricted re-pairings.** Every re-paired pair must itself meet the NEG rule. This removes the bias from having picked NEG pairs for low overlap. Rejection sampling, at most 10,000 tries per re-pairing.

### Sets
- One pair per distinct name, the first in dump order.
- A set is m pairs from one city, with distinct names and distinct legends. Each rung has 20 sets: 10 from Umma and 10 from Girsu, for POS and for NEG alike. One city per set matches the event the test is for, an archive from one house.
- **POS sets are disjoint** within a city (227 and 212 names).
- **NEG sets.** A city's distinct legends allow q disjoint sets of m, the whole part of legends over m. If q is 10 or more, the 10 sets are disjoint (m ≤ 5). Otherwise they come from successive partitions of q disjoint sets until there are 10, and the last partition is cut short. Sets overlap across partitions and never within one.
  - **m = 15:** q = 3 in both cities (56 and 53 legends). Each city gives three partitions of 3 plus one set from a fourth. That is 20 sets, of which 6 are mutually disjoint. A legend sits in about 2.7 of its city's 10 sets. The overlap is real and disclosed; it is not so heavy that sets repeat.
  - **m = 12:** q = 4, two partitions of 4 plus 2 sets. **m = 10:** q = 5, two partitions of 5.
- **Draw procedure (it replaces a per-set seed, which cannot give disjoint sets).** For a cell, arm, pool, rung, city and partition index, shuffle the city's pairs with the seed purpose `partition/<index>`. Walk the shuffled list and keep a pair only if its legend has not been kept yet. Cut the kept list into consecutive blocks of m. The first q blocks are that partition's sets. POS sets use one partition per city and its first 10 blocks.
- Sets are drawn fresh for each rung, arm and cell.

### Bars
- **Mismatch bar:** NEG sets pass in at most 1 of 20.
- **Power bar:** POS sets pass in at least 16 of 20. 13 to 15 is "at the edge" and counts as a fail. No rerun.
- **Chance of breaking the mismatch bar with a calibrated test.** With 20 independent sets it is 1.7%. The NEG sets at m ≥ 6 are not independent, and the bound that needs no independence is 10%: the expected number of passes is 0.2, and 2 or more are needed. The truth lies between. The same bound holds at m = 15, where NEG supplies only 6 disjoint sets.
- **Why 20 overlapping sets and not the disjoint ones alone.** The bar of 1 in 20 is the one this study was given. Six disjoint sets at m = 15 with a bar of 1 would let a false-pass rate near 17% through, and a bar of 0 in 6 would say little. The cost of overlap is a higher chance of a false K0a fail, and that error blocks a claim. It never makes one. The first partition of both cities (6 disjoint sets at m = 15, 10 at m = 10) is reported on its own beside the 20.
- A test with true power 0.90 meets the power bar 96% of the time, 0.80 meets it 63%, 0.70 meets it 24%, 0.60 meets it 5%.
- **Claimed m for an arm:** the smallest m such that every rung from m to 15 meets both bars. The rungs are 3 to 10, 12 and 15. A lone passing rung below a failing one claims nothing.

### Leave-one-out readout (reported for every POS and NEG set; it gates values, not sets)
For each object i, run the search on the other m − 1 pairs. Take each sound with credit above 0 and its best symbol as a value. Predict name i with those values. The prediction is confirmed for a unit if some placement of name i in its legend, within the arm's family, puts every predicted unit on its predicted symbol. A value is **confirmed** if at least one held-out name confirms it, and **confirmed and right** if the placements behind it are correct.
- **Value bar:** pooled over the 20 POS sets at the claimed m, at least 90% of confirmed values are right.

## Checks, in this order (strongest kill first)
1. **A1, recount.** The code rebuilds the pools and the tables above without computing T.
2. **Kp, planted known answer.** 20 synthetic sets, m = 15, arm B2, 999 re-pairings. Each set has 15 names of 3 sounds drawn evenly from 12 sounds, one sign per sound. Each legend is the name at a random place among 6 filler symbols used nowhere else. One direction per set, drawn at random. **At least 19 of 20 must pass.** Fewer means the search or the null is broken, and nothing after it could be read as closing the route. The scratch runs before sealing gave 20 of 20 at m = 10 and 20 of 20 at m = 15, with 199 re-pairings.
3. **Kc, code check.** 20 sets, m = 15, arm B2. The names of 15 POS pairs are paired with the legends of 15 other POS pairs from the same city, none of them in the set. Every re-pairing permutes those same 15 outside legends. At most 1 of 20 may pass. No true pair can occur in the observed pairing or in any re-pairing, so the pairings are exchangeable and more than 1 means a bug. (v1 re-paired a set's own legends, which leaves about one true pair in every re-pairing.)
4. **K0, the kill test, at m = 15.** K0 is rung 15 of cell P in arm B2. It uses that rung's sets and is not run twice. Both halves must hold.
   - **K0a:** 20 sets of 15 real mismatched tablets (NEG), built as "Sets" says, full alignment freedom. At most 1 of 20 passes.
   - **K0b:** 20 disjoint sets of 15 true pairs (POS). At least 16 of 20 pass.
5. **Kk, only if K0a fails.** K0a again at m = 15 on NEG0, the NEG pairs whose name shares no sign with its own legend (31 Umma on 30 legends, 35 Girsu on 32). Re-pairings must meet the NEG rule and share no sign either. About 1 to 2% of random re-pairings of 15 do, so the 10,000-try cap is rarely reached. 20 sets, 10 per city. At m = 15, q is 2, so each city gives five partitions of 2. Under F4 at rung 10, q is 3, so each city gives three partitions of 3 plus one set. At most 1 of 20 passes, with the same 10% bound.
6. Only then the rest, as "Cells" lists.

K0 sits at m = 15 because that is the largest rung where planted power is near 1.0 and NEG still supplies sets. If full freedom cannot separate true from false there, no smaller set will be trusted. A miss at m = 10 or 12 with a pass at 15 is a statement about how many pairs are needed, and reading 3 reports it through the claimed m.

## Calibration fallbacks (written before any calibration)
Only these are allowed. **Any other change after a number from a real pair has been seen makes the study INVALID**, including a change to 0.25, the alignment family, the pools, the cleaning rule, 0.01, the restart count or the bars.

- **F1, brief 10's arm-B fallback.** If arm B2 fails K0, run the same K0 for arm B1. If B1 fails, run it for arm A. A pass moves the claim to that arm, and the rule then demands what the arm was given.
  - B1: the reading direction of the legend must be known from outside the set.
  - A: an independent reason must locate the name span, such as a fixed legend position. The reason has to be stated before the set is scored.
- **F2, cost.** Before any real pair, time T on 50 synthetic sets of the calibration generator at each m and arm, and take the mean t(m, arm). The projection is the sum over every cell, arm, pool and rung of 20 sets × 1,000 values of T × t(m, arm). Early stopping and the leave-one-out searches are left out of the sum. If it exceeds 6 CPU-hours, every cell uses 199 re-pairings and a set passes at b ≤ 1.
- **F3, unbuilt sets.** A set that cannot be drawn, or a NEG re-pairing that hits the 10,000 cap, counts as a non-pass for POS and as a pass for NEG. So an unbuilt set can only hurt the claim.
- **F4, kin ties.** If K0a fails and Kk passes, the arm may still claim, with NEG0 in place of NEG in the mismatch bar at every rung and cell. Reading 2a then governs the wording.

## Cells
| cell | what changes | arms | m | role |
|---|---|---|---|---|
| P | primary, as frozen above | B2, then B1 and A | 15 first, then 12, 10 and down to 3 | K0 and the claim |
| R1 | each legend sign unread with probability 0.20 and replaced by a symbol used nowhere else, the floor of the reading gate in `anchor_objects.md` section 1 | the claiming arm | 3 to 10, 12, 15 | binding on the rule |
| R2 | each name unit replaced with probability 0.25 by a sound used nowhere else, standing for a unit written as a word sign | the claiming arm | 3 to 10, 12, 15 | reported |
| R3 | legend symbols are readings, not signs, so the editor has resolved every sign | the claiming arm | 3 to 10, 12, 15 | reported, an upper bound |
| C1 | arm C, Indus sign statistics, values drawn by sign frequency | the claiming arm | 3 to 10, 12, 15 | binding on the rule |
| C2 | arm C, values drawn evenly from signs with 5 or more tokens | the claiming arm | 3 to 10, 12, 15 | reported |
| X | P at m = 12 and 15, POS and NEG | B2 | 12, 15 | **binding in P, run whatever K0 says** |
| X20 | P and C1 at m = 20, POS only, since NEG holds 2 disjoint sets of 20 per city | B2 and the claiming arm | 20 | record only, for Decision 1 |

All three arms run the full ladder in P whatever K0 says, for the record. Only the claiming arm can claim.

### Arm C (M77 sign statistics only, label-free)
- Each set takes m POS names as sound sequences and m distinct M77 seal texts. A name of k units gets a host text of at least k + 2 signs.
- A code gives each sound in the set one M77 sign type, with no type used twice. C1 draws types in proportion to their M77 token counts. C2 draws evenly from the 175 types with 5 or more tokens.
- The coded name overwrites a random contiguous run of k signs in its host text. The rest of the text stays as it is. All names in a set run the same way.
- **Mismatch sets** pair m names with m untouched texts under the same host-length rule, k + 2 signs or more for the name each text is first paired with. Under a re-pairing a name may meet a text too short to hold it. It then has no placement and earns no credit, as in every arm.
- **The mismatch half passes by construction.** Names and untouched texts are independent, so every pairing is exchangeable. It is a code check like Kc and is not evidence about Indus texts. Arm C's information is in its power half.
- The same test, null and bars apply. The code is random and seeded. **No sign receives a value that anyone claims, no key is scored, and no M77 text is read.** The output is pass counts only.

## Readings (frozen)
Precedence: reading 1 comes first. Reading 2 is per arm: it settles whether that arm may claim and with which mismatch pool, and it never ends the reading of the study. After it, the first of readings 3 to 7 whose condition holds governs. Readings 8 to 10 are added where they apply.

1. **Kp or Kc fails.** A bug. Stop. Nothing else is computed. Fix, state the fix, reseal the code. Neither closes anything.
2. **K0a fails in an arm (per arm).** That arm runs Kk.
   - **2a. Kk passes.** "Mismatched Ur III tablets are not unrelated pairs. The sealer's name shares signs with the legend of the seal he used (Umma 51% against 32%), and the test picks that up." This is a real tie, not a false pass, and it does not close the route. Under F4 the arm goes on with NEG0. Any claim is then worded "the names are tied to these legends", and only the value bar can add "and spelled in them".
   - **2b. Kk fails.** "With no shared sign at all, real mismatches still pass under this arm's freedom." The arm cannot claim. F1 moves to the next arm.
   - **K0a alone never closes the route.** Closure is reading 7, and it needs every arm to end without a claim.
3. **K0 passes and P, R1 and C1 all have a claimed m.** "A span-free cross-read test separates true from false pairs. The rule's m is the largest of the three." If the coordinator rules yes on Decision 1, this becomes a proposal for section 4. If no, it is filed as a rehearsed consistency check.
4. **K0 passes but R1 or C1 has no claimed m up to 15.** "The test works on clean Ur III legends only. At the reading gate's floor, or at Indus sign statistics, 15 pairs are not enough." Section 4 stays. The minimum event is restated as more than 15 pairs.
   - **4a. R1 misses on the mismatch bar while P meets it.** "Unread signs raise the false-pass rate." R1 has no claimed m, and reading 4 applies with that sentence.
   - **4b. C1 misses on the mismatch bar.** Its mismatch half passes by construction, so this is a bug in arm C. Arm C is void until the code is fixed and resealed. P and R1 stand.
5. **B2 has no claim and B1 claims.** As 3 or 4, with the direction condition written into the rule.
6. **Arm B fails at every m ≤ 15, and so at every m ≤ 10** (B2 and B1 both without a claim) **and arm A claims.** "Cross-reading needs an independent reason to locate the name span." Brief 10's fallback rule is the result. The note must say that the name opens 91.0% of Ur III legends, so position is nearly free there and may not be on an Indus object.
7. **No arm claims.** The wording depends on why.
   - **7a. A miss at m = 10 or 12 while rung 15 passes is not this reading.** The arm then claims m = 15 under readings 3 to 6, and the note says "10 pairs is at the edge", never "closed".
   - **7b. Every arm misses at m = 15.** "The route is closed at 15 pairs or fewer on this statistic. Section 4 of `anchor_objects.md` stays as it is." The note says for each arm whether it fell on the mismatch bar (2b) or on power. One atlas entry under section 9. Reopen with a set of more than 15 pairs or a new statistic under a new prereg.
8. **Value bar missed** in an arm that claims. "A passing set shows the pairing is real. It does not certify single values." The rule may then count the set, never a value.
9. **Edge.** 13 to 15 of 20 at the top rung is reported as "at the edge" and read as a fail.
10. **Rungs 10, 12, 15 and 20.** Report the median number of confirmed and right values at each. No bar. Rungs 10 and 12 of cell P are always reported by name, pass counts included.

In every reading the Ur III result is an upper bound on power, for the reason in "Limits". No reading depends on Decision 1. The ruling changes only where a result is filed.

## Aborts
- **A1.** A recount differs from a table above. The pool counts (1,316; 224; 128; 483; 154) must match exactly, shares within 0.01. Stop and redraft.
- **A2.** The OGSL hash does not match. Stop.
- **A3.** Kp below 19 of 20, or Kc above 1 of 20. Stop.
- **A4.** The run was not started through `board/run.sh`, which waits for the Indus compute lock. Do not start it any other way, and do not run it beside the job that holds the lock.
- **A5.** The code opens any Indus key file, any file under `experiments/certify_size_curve/`, or any M77 field other than the sign sequence and object type. Stop.
- No rerun, no tuning and no fix tag after any T on a real pair is seen.

## Seeds
Every random stream is seeded from the first 8 bytes of SHA-256 of the string `anchor_crossread/v3/<cell>/<arm>/<pool>/<m>/<city>/<set>/<purpose>`. Purposes are `partition/<index>` (set left empty; it replaces the per-set `draw`), `perm/<index>`, `init/<index>/<restart>`, `noise`, `code` and `host`. No global random state.

## Limits stated in advance
- **Same script on both sides.** The name's sounds come from the same cuneiform spelling that stands in the legend. One name unit is one legend sign, apart from a silent determinative. A foreign name in an Indus legend could be cut into different units or written as a word. Power here is an upper bound. The false-pass control transfers, the power does not.
- NEG is small, so NEG sets at m ≥ 6 overlap across partitions and are not independent draws. At m = 15 only 6 of the 20 are mutually disjoint. Kk's pool is smaller still, with 4 disjoint sets of 15.
- **Arm C has no homophony.** Each sound gets one sign and each sign one sound. Ur III names have 47 sounds with a second sign and 45 signs with a second sound. Arm C's power is an upper bound on that count too.
- The penalty weight was fitted on one synthetic generator, at 199 re-pairings and m = 10. K0's rung was then chosen from planted power on the same generator.
- The cleaning rule's term list was written after reading the v1 mismatch names.
- The VAR rule cannot catch every case of one name in two readings. Any that remain in NEG push K0a toward failing.
- Arm C plants by overwriting part of a real sign sequence. Nobody knows how a name sits in an Indus text.
- The search is a hill climb. A weak search costs power. It cannot raise the false-pass rate, because every re-pairing gets the same search.
- A claimed m of 15 rests on one rung.

## Cost
- About 16 ms per value of T at m = 10 on synthetic sets, so about 16 s for a set that runs all 999 re-pairings.
- About 4 CPU-hours for all cells with rungs 12 and 15 added, one worker, at background priority. The m = 15 time per value is not yet measured. F2 pins the projection and its 6-hour rule.
- **The run queues behind the Indus compute lock.** `certify_size_curve` holds it, and its 4 workers fill the machine's cap. This study starts through `board/run.sh` only after that run releases the lock. No cloud.
- About 1.5 days of work with the reviews.

## Decisions and open questions
1. **Coordinator ruling, open and not assumed either way: does leave-one-anchor-out prediction count as clause (b) of the 2027 bar?** The study runs the same either way. No cell, bar, seed or reading depends on the ruling.
   - **If yes,** readings 3 to 6 end in a proposed rewrite of `anchor_objects.md` section 4, and the claimed m defines scorecard tier A.
   - **If no,** the same run is filed as a rehearsal of an anchor consistency check. Section 4 stays, and nothing here opens a path to the bar.
   - **A second part needs an answer with it.** Does the bar want 10 values from a set that passes, or 10 values each confirmed by a held-out name? The first needs about 5 to 10 pairs. The second needs about 20, by the count above. Rungs 15 and 20 measure the second.
2. Sign-level symbols through OGSL, with a second copy of the public zip in this study's folder. Agreed?
3. The NEG and VAR rules, the cleaning rule, restricted re-pairings for NEG sets, and Kk with F4. Agreed?
4. **Closed (v2).** The penalty weight is 0.25, fixed by the planted calibration above.
5. A pass level of 0.01 with 999 re-pairings, so that a calibrated test meets the mismatch bar 98% of the time. At 0.05 it would break it 26% of the time.
6. One city per set, Umma and Girsu only.
7. No rung dials a mismatch in how the two scripts cut a name into units. Add one before sealing, or leave it as the stated limit?
8. Brief 10's numbers are corrected here, not in the brief. Should the brief get a correction line?
9. **Closed (v2).** The run queues behind the Indus compute lock.
10. Twenty overlapping NEG sets with the 10% bound, and not 10 disjoint sets. Agreed?

**Settled at sealing (2026-11-25).** The coordinator instructed: review, fix, then seal. Under that instruction the lead accepted decisions 2, 3, 5, 6 and 10 as drafted. Decision 7 is left as a stated limit (no unit-cutting rung). Decision 8: a correction line is added to brief 10, which is outside the repo. Decision 1 (clause (b)) stays open; no part of the run depends on it.

## Before sealing
- Done: the decisions above were settled at sealing; only decision 1 stays open.
- Code written and hashed after sealing, before any T on a real pair.

## Review log
**v2 (first fresh review, FIX, 12 items).** Recounts are label-free. The statistic ran on synthetic planted sets only.
1. Kc re-pairs with the legends of 10 POS pairs outside the set.
2. Kp added before Kc and K0, bar 19 of 20.
3. Cleaning rule written; `valuex(SIGN)` readings lose their `x`. POS 1,332 to 1,316 pairs and 493 to 483 names. NEG 256 to 224 pairs and 179 to 154 names. VAR 153 to 128. All tables recomputed.
4. K0a keeps 20 sets, built as two partitions of 5 disjoint sets per city. The 1.7% figure now stands beside the 10% bound for overlapping sets.
5. K0a alone no longer closes the route. Kk, F4 and reading 2a added; kin-tie count disclosed.
6. Penalty weight fixed at 0.25 by planted calibration, grid and rule stated first. Decision 4 closed.
7. Arm A's window defined for re-pairings, k + 1 signs from the legend's span start.
8. Arm C: mismatch half named as a code check; host-length rule; no credit without a placement; "no homophony" in Limits.
9. Readings: precedence stated; 4a and 4b added; K0 named as rung 10 of cell P; F2's formula pinned.
10. Cost and A4: the run queues behind the Indus compute lock. Decision 9 closed.
11. Clause (b) left open; every reading now reads correctly under either ruling.
12. This log.

Where this draft differs from the review's figures: the planted calibration gave 3, 13, 9 and 5 of 20 under seed 20261125 against the review's 5, 17, 11 and 9 under seed 7. Both are in the table. Distinct NEG legends are 56 and 53 after cleaning (review 68 and 54 before it).

**v3 (pre-seal check of v2, FIX, 6 items).** No new count on real pairs. The statistic ran on synthetic planted sets only.
1. **Pre-seal design decision by the study lead, based on planted power only:** K0 moves to m = 15. K0a and K0b restated. NEG at m = 15 is 20 sets from three partitions of 3 plus one set per city, 6 of them disjoint, bar at most 1 of 20, bound 10%. Power statement replaced. Reading 7 split so that a miss at m = 10 is never "closed".
2. Row X is binding in P, arm B2, at m = 12 and 15, whatever K0 says. The claimed m runs to 15. m = 20 is a separate record-only row.
3. Arm B2's direction is free for each pair independently.
4. Kk's partitions stated, and the partition draw procedure replaces the per-set `draw` seed.
5. Reading 2 marked per arm. The clause (b) sentence under "Why" made neutral.
6. This log.

Two things go beyond the check's wording, for the coordinator to confirm. Kk follows K0 to m = 15, where it has five partitions of 2 per city; "three partitions of 3 plus one set" is its shape at rung 10 under F4. Kp and Kc also moved to m = 15. Kp at m = 15 gave 20 of 20 in scratch.
- 2026-11-25: the lead accepted the drafter's two extensions (Kk, Kp and Kc at m = 15; m = 20 record-only, POS-only). Sealed as v4. Nothing was scored on real pairs before sealing.
