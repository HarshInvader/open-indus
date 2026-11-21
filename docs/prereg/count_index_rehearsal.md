# Prereg: count-likeness index, known-answer rehearsal (plan 10, Route 1, step 1)

Written 2026-11-21, before any index value was computed on any corpus. Code: `experiments/count_index_rehearsal/cir.py` (hashed with this file). Plan: `experiments/fable52_plan10.md`, Route 1 and ordered step 1.

Before freezing I ran one dry extraction. It printed only head token counts, class labels and the pooled Indus numeral value marginals, which plan 10 had already printed. It printed no index value. Two rules changed after that dry run and before freezing, both from head names and sizes alone. (1) A stoplist for Latin unit epithets, because the first run caught "et", "hic" and "annorum" as epithets. (2) A secondary strict size cut of 349 tokens, because real Indus dev after de-duplication has 20 eligible heads and 349 tokens, about half the plan's 700.

## Question

Numbers vary when they count goods and stay frozen in names and titles. Does a count-likeness index per head sign tell counted heads from frozen ones when a known-answer corpus is cut to Indus size? If it does not, Route 1 step 2 (the index on real Indus heads) is underpowered and is not run.

## 1. The index (frozen)

- **Token:** one numeral directly next to a head sign (extraction rules per corpus are in section 3).
- **Index of a head:** the expected number of distinct numeral values in a random sub-sample of 4 of its tokens, drawn without replacement (rarefaction): `I = sum over values v of [1 - C(n - n_v, 4) / C(n, 4)]`. It runs from 1 (always the same value) to 4. Because it is rarefied, common heads do not look more varied just because they are common. This is plan 10's index.
- **Minimum:** 8 tokens per head.
- **Head-level call:** a head is "called counted" if I >= 2.0. In 4 tokens, a counted head is expected to show at least 2 values.
- The modal share and entropy are not used. One index only.

## 2. Cutting to Indus size (frozen)

Each corpus is cut in 1,000 draws (seed 20261121). In each draw:
1. Shuffle the eligible heads (labelled, at least 8 tokens in the de-duplicated corpus).
2. Take heads in that order. Each head gets n = min(available, uniform integer 8..30) tokens, sampled without replacement.
3. Stop once the draw holds at least 700 tokens (primary cut) or 349 tokens (secondary strict cut, reported but not a bar). This gives roughly 36 heads per draw on the primary cut and 20 on the strict cut.
4. A draw with fewer than 3 heads of either class counts as a failed test (p = 1).

**De-duplication:** distinct texts, then the non-chaining greedy from `experiments/fish_tick_closer_v2/dedup.py`. For large corpora `cir.py::greedy_fast` uses a bigram index. Its output must be identical to `dedup.greedy`. `cir.py dedupcheck` confirmed this on Indus dev, 3,000 EDH texts and 2,000 proto-cuneiform tablets (all identical). Text units: one tablet (proto-cuneiform and proto-Elamite), one inscription (Latin), one Indus text.

## 3. Corpora and known answers

**a. Proto-cuneiform** (`experiments/protocuneiform/pc_lines.json`, administrative Uruk IV-III).
- **Extraction:** per line, each maximal group of numeral tokens. The head is the first non-numeral sign directly after the group, or else the sign directly before it. The value is the numeral group as written, for example "1(N14) 7(N01)". The head key is the base sign name, with `~x` and `@x` variants stripped.
- **Labels from `pc_classes.py`:** counted = the commodity classes (GRAIN_FOOD, LIQUID_DAIRY, VESSEL, TEXTILE, LIVESTOCK, OTHER_GOODS). Not counted = OFFICE_PERSON and PLACE_INST. UNKNOWN is excluded.
- The dry run found 103 eligible heads (52 commodity, 51 person, office or place).

**b. Proto-Elamite** (`pe_lines.json`). Same extraction. The repo holds **no reliable class labels** for proto-Elamite signs: `meaning_classes` calls it unread, and no PE class file exists. So PE gets a **descriptive check only**: the index distribution under the same cut and the share of heads called counted. No bar applies, because in PE every number is a count and there is nothing frozen to separate.

**c. Latin** (EDH, `experiments/short_labels/raw/edh`, Latin-language items, `transcription` field with the parenthesis characters of expansions removed and line marks `/` dropped). A token or neighbour containing any of `[ ] ? { } < > +` is skipped, because restored or uncertain numerals are editorial guesses. The rules are applied in this order to each numeral:
- **Frozen, title:** a token `<Roman>vir...` (IIvir, IIIIIIvir, VIvir, Xvir, XVvir...). Head = "vir", value = the numeral. This is one head with several frozen numbers, kept that way on purpose because Indus heads can be like that too.
- **Counted:** a standalone Roman numeral whose previous word, or failing that next word, is a form of annus, mensis, dies, hora, stipendium, pes, passus, sestertius, denarius, libra or modius. Exact form lists are in `cir.py::COUNT_FORMS`. Head = the lemma.
- **Frozen, unit name:** a standalone Roman numeral whose previous word is a form of legio, cohors or ala, and whose next word is at least 4 letters, alphabetic, not a count form and not in `EPI_STOP`. Head = unit type + first 5 letters of that epithet, for example `leg:frete` or `coh:hispa`.
- The previous-word count rule is checked before the unit rule, and the unit rule before the next-word count rule.
- The dry run found 76 eligible heads (11 counted, 65 frozen).
- **Secondary, reported only:** Latin without the "vir" head.

**d. Planted Indus gate** (M77 `dev_heldout(version=2)` dev, greedy de-duplicated).
- Numeral tokens follow the redteam_pnl rule: a stroke numeral directly before a non-numeral sign inside a break-free run. Values come from `stroke_signs.json` (short without M99/M101, plus tall). Heads are keyed by (stroke system, sign).
- 20 heads have at least 8 tokens.
- **Indus data supply only three things:** the head sizes, the stroke system of each head, and the pooled dev value distribution per system. **No real head's values are read and no index is computed for any real Indus head.** That is step 2 and needs its own prereg.
- In each draw (same cut rule, so all 20 heads and about 349 tokens), round(0.3 x heads) heads are planted as counted and the rest as frozen. The 0.3 share follows plan 10's prior.
  - **Counted head:** every value is an independent draw from the pooled values of its stroke system.
  - **Frozen head:** one value v* drawn from that pool. Each token is v* with probability 0.70, else a pool draw. This is plan 10's "30% of a fixed number replaced by count draws".
- **Secondary, reported only:** frozen share 0.90, which is about the observed tall 2 + fish rate.

## 4. Statistics (frozen)

- **Separation:** in each draw, the AUC = P(index of a counted head > index of a frozen head), with ties counted as 0.5. Report the mean over draws, the median and the 5th percentile.
- **Power:** the share of draws in which a one-sided permutation test (class labels permuted across the heads of that draw, 999 permutations, statistic = AUC via midrank sum) gives p <= 0.05.
- **False alarm:** the same test after one random permutation of the labels in each draw. This is the share of p <= 0.05.
- **Head-level calls (proto-cuneiform requirement):** for each head, the share of draws in which it is called counted (I >= 2.0). Its majority call is "counted" if that share is at least 0.5.
  - Sensitivity = share of commodity heads whose majority call is counted.
  - Specificity = share of other heads whose majority call is not counted.
  - Balanced accuracy = their mean.

## 5. Go / kill bars (frozen; all must hold for GO)

| bar | requirement |
|---|---|
| B1 | Proto-cuneiform power >= 0.80 (commodity vs person, office, place) at the 700-token cut |
| B2 | Proto-cuneiform head-level balanced accuracy >= 0.80 (commodity heads called counted, the rest not) |
| B3 | Latin power >= 0.80 at the 700-token cut |
| B4 | Latin separation (mean AUC) >= 0.90 |
| B5 | Planted Indus gate power >= 0.80 (frozen share 0.70) |
| B6 | False alarm <= 0.06 for proto-cuneiform, Latin and the planted gate (0.05 plus Monte Carlo error at 1,000 draws) |

- **NO-GO** if any bar fails. Plan 10's kill condition then applies: "Rehearsal power under 0.8 at Indus size: the route is underpowered. Record it and stop."
- The thresholds will not be changed after scoring.
- The strict 349-token cut, Latin without "vir", frozen share 0.90, and PE are reported but do not decide GO. If GO passes at 700 but fails at 349, the RESULTS must say that step 2 on dev alone is below the size the rehearsal validated.

## 6. Tests run

- Five scored runs (two planted, three labelled).
- Two strict-cut runs.
- One descriptive PE run.
- One verdict.

No multiple-comparison correction applies to the verdict, because it is a conjunction of fixed bars.

## 7. What a GO does and does not license

A GO licenses only writing the step 2 prereg (P1-P4 on real Indus heads). It is not evidence about any Indus sign.
