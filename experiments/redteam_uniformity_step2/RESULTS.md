# Red team of uniformity paper step 2

Prereg: `docs/prereg/redteam_uniformity_step2.md`, hashed with `rt2.py` in `docs/prereg/HASHES.txt` (tag `redteam_uniformity_step2`, 2026-11-21T17:03:52Z) before any condition was scored or any audit token was judged. Every scored condition ran through the benchmark's own `clean()` + `draw_n()` + `score()`. There were 50 draws per condition (seed 20261127): 10,500 draws, none failed. A4 re-reads the step-2 draws and adds no new ones. Numbers are in `table.md` and `results.json`, per-draw values in `draws.jsonl`, and the ledger in `ledger_rows.csv`. The hand-judged audit is in `data/audit.csv`, which is gitignored because it holds third-party text; its counts are below.

## Verdicts

| claim | verdict | why, in one line |
|---|---|---|
| (a) name-bearing legends carry place; name-free do not | **BROKEN** on the name-free half; the name-bearing half stands | Under strict stripping, Umma vs Girsu name-free clears the Umma reign floor by +0.052 (gate exactly 80%), so frozen rule A1-iii fires. |
| (b) Mohenjo-daro = Harappa seals at the floor | **STANDS WEAKENED** | No pool differs under any reference. ICIT seals + sealings sits +0.054 above its shuffled-label null (q 0.29). |
| (c) Chanhu-daro above the floor, not above the null | **STANDS** | Δ_cons is +0.117 / +0.183 for the two "differs" pairs, and q_chance is ≥ 0.235 for every Chanhu-daro pair. |
| (d) sealings differ | **STANDS WEAKENED** | Both editors still differ after strict de-dup (+0.091, +0.167) and under the null. The cross-object test is underpowered in both. |
| (d) tablet gap is a copper artefact | **BROKEN** | Moulded vs moulded tablets alone differ: +0.150, p 0.020, power 96%. |
| Emerging reading: "Indus seals behave like name-free legends" | **BROKEN** (rule: (a) broken) | The Indus half holds: Ur-III-like name loads are excluded in all three pools. But "name-free legends show no place" is not established, so it cannot be used as the anchor. |

### (a) In plain words

- **Name-bearing legends really do carry place, and the place sits in personal names.** [Superseded 2026-11-21: see correction note at end.]
  - With toponyms, god names and every theophoric personal name removed (`noTGtheo`), Umma vs Girsu still clears all four within-city floors: min Δ +0.102 (ORACC) and +0.093 (CDLI), gates 100%.
  - With personal names removed but toponyms and gods kept (`noPN`), it does not clear the Girsu reign floor: Δ +0.027 (ORACC, gate 86%) and +0.028 (CDLI, gate 92%).
  - So the place signal is not a city-name or city-god leak (`umma{ki}`, Šara, Ningirsu). It lives in the people named on the seals.
  - Latin is the same story: without unit words and numerals (`noUNIT`), Britannia vs Germania still clears both floors (+0.084, +0.163; gates 98% and 100%).
- **The name-free half does not survive as a firm "no".**
  - Step 2's "not above floor" rested on one gated split: Umma reigns, Δ +0.009.
  - Strict stripping removes every form ever tagged as a name, every determinative, and the word after dumu / arad₂ etc. That moves the same split to **+0.052** (p_floor 0.078; gate 80%, exactly at the bar).
  - By the frozen rule, the family is then "above floor", and claim (a) is BROKEN.
  - This is a knife-edge result, not a strong place signal. The ungated Girsu reign split stays below its floor under every tagging (−0.061 to −0.094), and CDLI strict is underpowered.
  - The honest reading: without personal names, Ur III legends separate the two cities by about as much as they separate two reigns of one city, give or take 0.05. Neither "carries place" nor "does not" is established.
- **Why the reign floors are high.** The Šulgi and Amar-Suen royal seals call the king `nita kal-ga`: 368 Umma legends, and 5 later ones. The Šu-Suen and Ibbi-Suen seals write `lugal kal-ga`, and royal-dedication seals are twice as common late. Name-free legends therefore carry a dated formula. The reign floor is a real date signal, not noise.
- **The tagger is clean for Ur III, poor for Latin.**
  - ORACC: 0 of 50 kept tokens were names, and 0 of 50 removed tokens were non-names.
  - CDLI: 2 of 50 kept tokens were names leaked through POS look-up (owner and father slots), and 1 of 50 removed was a title (`nu-banda₃-gu₄`).
  - Latin: 42% of kept tokens were names or unclear (praenomen initials L, C and Q, and cognomina such as Maximus, Moderatus and Laetus). 22% of removed tokens were non-names or unclear (legion epithets AVG, ITAL, SEV, M(inervia), and C(ivium) R(omanorum)).
  - Latin "name-free" is not name-free. It was underpowered in step 2 anyway.
- **Size is not the explanation.** Whole Ur III legends drawn at the name-free size (68 per side) still clear the Umma reign floor by +0.164 (gate 90%).
- **Loose stripping** keeps unknown and determinative forms. It stays "not above floor" (Girsu reigns −0.084, gate 92%), so it does not trigger the weakening rule.

### (b) Mohenjo-daro vs Harappa

| pool | Δ floor | Δ null | Δ cons | verdict floor / null / cons |
|---|---|---|---|---|
| M77 seals | +0.005 | +0.043 | +0.005 | same / same / same |
| ICIT seals | +0.014 | +0.014 | +0.014 | same / same / same |
| ICIT seals + sealings | +0.042 | **+0.054** | +0.042 | same / underpowered / same |

Nothing "differs". ICIT seals + sealings sits just over the 0.05 margin against its shuffled-label null (q_chance 0.29), which is why the verdict is weakened. Power is 98-100% against every reference.

### (c) Chanhu-daro

- The floor bias is real for small sites, not for Chanhu-daro against the big cities:
  - Harappa vs Chanhu-daro: Δ_cons +0.117 (M77) and +0.183 (ICIT seals + sealings).
  - Mohenjo-daro vs Chanhu-daro: +0.111 to +0.153.
- No Chanhu-daro pair is above its shuffled-label null after BH correction (q_chance 0.235-0.392). The p-value floor of 0.02 with 50 draws limits this; the Part 2 follow-up uses more draws.
- **Floor-bias flips (A4).** Every "differs" between two small sites flips to "underpowered" once the null is the reference:
  - Lothal-Chanhu-daro, Lothal-Kalibangan and Chanhu-daro-Kalibangan in M77;
  - Dholavira-Chanhu-daro, Lothal-Chanhu-daro and Chanhu-daro-Kalibangan in ICIT.
  - Their within floors were 0.32-0.47, while the nulls sit at 0.47-0.53. This confirms step 2's footnote: those rows are pipeline bias.

### (d) Sealings and tablets

- **Duplication is real but already handled.**
  - M77 Harappa has 367 complete sealings, but only 162 distinct strings. One seal text is impressed 49 times, another 36. Mohenjo-daro: 126 raw, 75 distinct (largest cluster 9). ICIT sealings are almost all distinct (134 → 133, 68 → 64).
  - `clean()` already collapses these. A stricter de-dup (`dedup.greedy` with MIN_DROP = 2, plus one text per sign multiset) keeps the difference:
    - ICIT: Δ +0.091, q 0.020, power 80%, "differs".
    - M77: Δ +0.167, q 0.020, power 100%, "differs". Its floor is low (0.394), but it is still +0.072 above its own null.
- **Object/format test: underpowered, and leaning towards format.**
  - Gates on the 62-per-side cross pools are 2-4%, so this test cannot decide.
  - Descriptively:
    - M77: each city's sealings are as far from its own seals as from the other city's (+0.016, +0.002).
    - ICIT: inconsistent. Harappa sealings are closer to Harappa seals (+0.120), but Mohenjo-daro sealings are closer to Harappa seals than to their own (−0.116).
  - Neither pattern looks like a place signature.
- **Harappa mound floor** (F vs AB): AB has 8 sealings, power 46%. Not usable.
- **Tablets.**
  - Moulded vs moulded (TAB:B): Mohenjo-daro vs Harappa 0.641 against a 0.490 floor, Δ +0.150, power 96%. The non-copper set gives +0.148.
  - So the tablet gap is not only copper vs moulded. Caveat: Mohenjo-daro has 42 moulded tablets, and Harappa's moulded tablets are a late, Harappa-specific series. A period or type difference inside "moulded" is not excluded.

### Indus analog (A3): how many names could Indus carry?

With real labels, the largest share of Mohenjo-daro / Harappa seals that could carry a site-specific name and still give the observed gap:

| pool | one new sign per name | two shared signs per name | real Ur III name frequencies, spelt in shared signs |
|---|---|---|---|
| M77 seals | 10% | 10% | 30% |
| ICIT seals | 10% | 20% | 30% |
| ICIT seals + sealings | 10% | 10% | 30% |

- Ur III legends carry a personal name on 99.8% of seals (1.86 per legend, 36% of tokens).
- A name load like that is excluded in every pool and form: 95-100% of draws exceed the observed gap from r = 0.2 (Zipf stocks) or r = 0.5 (real Ur III names).
- Step 1 (labels permuted, absolute AUC) said 20-30%. Measured against the floor, the bound is tighter for invented name stocks (10-20%) and the same for realistic, overlapping names (30%).

## Safe paper wording

> Seal texts from Mohenjo-daro and Harappa differ no more than two random halves of one city, against both the within-city floor and a shuffled-label null (between minus floor +0.005 to +0.042; minus null +0.014 to +0.054; 98-100% power for a 15% local sign stock). Planted tests exclude site-specific personal names on more than about 30% of seals when names are drawn from real Ur III frequencies, and on more than 10-20% for invented name stocks; Ur III seals carry a name on 99.8% of legends. In readable seal corpora the site signal sits in personal names: Ur III Umma vs Girsu legends with toponyms, divine names and theophoric names removed still exceed every within-city floor (+0.09 to +0.27), while legends without personal names do not exceed the Girsu reign floor. Without personal names, Ur III legends separate two cities about as well as two reigns of one city (differences −0.09 to +0.05 depending on floor and name tagging), because the royal formula changes between reigns.

Do not write:
- "Indus seals behave like name-free seal legends", or "name-free legends carry no place". The name-free result is a tie within ±0.05, not a clean negative.
- "the tablet gap is a copper artefact". Moulded tablets alone differ (+0.150).
- "sealings show a place difference". They differ, but the object/format test could not tell place from sealing type.
- Latin "name-free" numbers as name-free. 42% of the tokens kept are names or unclear.

## Tables

### A1/A2: Umma vs Girsu (and Britannia vs Germania) against structural floors

Minimum gated Δ per family (full rows in `table.md`):

| corpus | whole (step 2) | name-free (step 2) | loose | strict | noTG | noTGtheo | noPN / noUNIT |
|---|---|---|---|---|---|---|---|
| Ur III ORACC | +0.158 | +0.009 | −0.084 (not above) | **+0.052 (above, 1 gated split)** | +0.137 | +0.102 | +0.027 (not above) |
| Ur III CDLI | +0.165 | underpowered | −0.028 (not above) | underpowered | +0.126 | +0.093 | +0.028 (not above) |
| Latin | +0.123 | underpowered | underpowered | underpowered | | | noUNIT +0.084 (above); noPN underpowered |

Size control (whole legends at the name-free size): Umma reigns Δ +0.164 (gate 90%); Girsu reigns +0.213 (gate 76%).

### Audit (50 kept + 50 removed tokens per corpus, step-2 rule)

| corpus | kept tokens that are names or unclear | removed tokens that are not names or unclear | tagging |
|---|---|---|---|
| Ur III ORACC | 0% | 0% | sound |
| Ur III CDLI | 4% | 2% | sound |
| Latin owner/maker marks | 42% (22% names, 20% unclear) | 22% | weak |

### A4, A3, A5

See `table.md`: all 34 step-2 Part 2 pairs under three references, the planted-name curves and the sealing / tablet blocks.

## Deviations

1. The audit sample file was first written into the experiment folder, then moved to `data/audit.csv` (gitignored) because it holds third-party text. Nothing else changed.
2. Compute lock: all runs went through `board/run.sh` (repo lock, `taskpolicy -b nice -n 20`, one process). The shared marker `open-citizen-science/.local/compute.lock.indus` was held by stamp_detector (`embed.py`, near-idle network job). This single-process job ran alongside it, as step 1, its red team and step 2 did. Stated in the prereg.
3. No threshold, condition or code was changed after scoring.

## Limits

- 50 draws per condition put the p-value floor at 0.020, which caps how small BH q-values can get in families of 10-15 pairs.
- The Ur III strict verdict rests on one split whose gate is exactly 80%.
- Old Babylonian was not re-attacked (underpowered in step 2).

## Correction (2026-11-21, review 2)

- "The place sits in personal names" (finding heading and the safe-wording block) is superseded by the role-by-role analysis in `experiments/uniformity_paper/revision/RESULTS.md` (R3): removing owner names, patronyms or patron names one at a time leaves Umma vs Girsu above every gated within-city floor, so the signal is spread across name roles, not located in one. Removing all personal names leaves a positive gap on the Girsu reign floor that falls short of the 0.05 margin; it does not go below the floor. The safe-wording paragraph above is kept as written for the record and should not be quoted. (Found by `docs/paper/uniformity/REVIEW_2.md`.)
