# Context and meaning: which signs go with non-textual context?

Area: archaeology/semantics. Code: `experiments/context/*.py` (run from the repo root with `.venv/bin/python`). Logs: `*.log`. Machine-readable results: `results.json`. Builds on `sources/shaunmortal_indus/STATE.md` (F1-F40) and paragorth (`sources/paragorth_Indus-/STRATEGIES.md`). Where they already answered a question I replicated it cheaply and cite them.

## Conclusion first

1. **The object, not the emblem, sets the vocabulary.** Object type (seal, sealing, tablet, copper tablet, pottery, rod, bangle, implement) can be predicted from the text alone: one-vs-rest CV AUC 0.71-0.91 in M77 and 0.66-0.89 in ICIT, against within-site nulls of about 0.5-0.6. Specific register markers replicate from M77 to ICIT through the M-W bridge (10 of 17 replication tests pass Bonferroni). The seal animal, by contrast, is only weakly predictable from the text: balanced accuracy 0.19 vs 0.12 null; unicorn vs other AUC 0.52, which is null; cross-site AUC 0.505. Emblem classes share no more signs than chance.
2. **Copper tablets bind a picture to a whole legend, not to its signs.** Tablets with identical text share the picture 62% of the time, against 6% when pictures are permuted (p<0.001). Merge variant copies of one legend (edit distance <=1 or containment) and ask whether *different* legends that share signs share the picture: nearest neighbour 0.03 vs 0.06 null (p=0.81); sharing a bigram, 0.11 vs 0.05 (p=0.08). This replicates paragorth S-DARK-67. The legend names or labels the picture as a unit, and no single sign means "elephant" or "hare". A new small observation: on two-faced copper tablets, a single large pictographic sign (M362/M363/M346/M184) stands where the picture would be, next to the same legend that elsewhere sits beside the picture. These are candidate emblem-logograms.
3. **Texts found in the Gulf and West Asia on round seals do not follow Indus sign order.** Under a Kneser-Ney bigram model trained on native texts, they cost +2.17 bits/sign more than length-matched native texts (95% CI +1.63 to +2.70, p<1e-4, n=18). That is +2.09 bits over *home* round seals, so the seal format does not explain it. The bigram model gains nothing over a unigram model on these texts (-0.25 bits, vs +1.37 for native texts), which is the signature of shuffled order (-0.37 in a planted control). Square seals found abroad are *not* anomalous (+0.44, CI includes 0). This supports Parpola's "Indus signs used for a different language or system", but it cannot tell a foreign language from ad hoc or pseudo-script use: the 17 texts share no ordered bigram among themselves.
4. **Negative results, each well supported.** (a) Stroke numerals do not follow the binary weight series (1,2,4,8...). Values 4 and 8 are flat or troughs; the spikes are short 3/7/12 and tall 2/3. Ratios between two numerals in one text are powers of two no more often than chance. (b) No sign innovation or obsolescence survives correction across Harappa, Mohenjo-daro, Dholavira and Kalibangan phases. The pre-urban Harappa inscriptions (Period 1-2) are 1-3-sign pot marks built from the later inventory. (c) Sealings do not travel more than seal texts do (13 cross-site matches vs 10.0 expected, p=0.17). Only 2 of 66 sealing texts match a seal found at the same site.

## Semantic anchors table

Strength: **strong** = survives correction and replicates across corpora or held-out data; **moderate** = survives correction in one corpus with consistent direction in the other; **weak** = suggestive or descriptive, small n.

| Sign / sequence (M = Mahadevan, W = Wells) | Proposed meaning category | Evidence (distinct texts) | Strength |
|---|---|---|---|
| Whole copper-tablet legends, e.g. M65-M336-M89-M407-M169-M183-M169 = hare; M204-M245-M358-M342 = ox-antelope; M389-M407-M124-M169-M373-M287-M342 = horned bovine personage | Label or name *of the depicted figure*, bound at the level of the whole legend | Identical-text tablet pairs share the picture 0.62 vs 0.06 null (272 pairs, p<0.001). Sign sharing *between* legend families does not predict the picture (NN 0.03 vs 0.06, p=0.81) | **strong** (legend level); **null** (sign level) |
| M362, M363 (horned "shield"), M346, M184: copper-only one-sign faces | Pictographic emblem standing in for the picture (logogram for the figure) | 13 two-faced tablets carry a one-sign face and no picture. M362/M363 sit beside the horned-personage legend, which is on 5/5 picture tablets with that figure. M346 sits beside a goat-antelope legend (3/3). M184 sits beside a rhino legend (1/1). But M363 also pairs with a goat-antelope legend | **weak** (6 distinct pairings, descriptive) |
| W845/M407 and final W407/M169; M18/W095; M97-M25/W001-W142; M252-M97 | Copper-tablet register formula (the "copper closer") | M77 copper: M407 9 obs vs 0.8 exp, BH q=4e-6. ICIT copper: W407 18 vs 2.5 (q=4e-9), W845 7 vs 0.9. 6 copper features replicate M77 to ICIT (Bonferroni) | **strong** (register); meaning unknown |
| W002 / M99 (two short strokes) | Element of personal-seal legends (name/title grammar), absent from labels and dockets | Enriched on seals (M77 480 vs 438, q=1e-6; ICIT 584 vs 542, q=3e-4) and ICIT sealings (50 vs 33). Depleted on copper (M77 2 vs 12.7; ICIT 4 vs 22, q=3e-5) and on tablets (M77 3 vs 14.2; ICIT 55 vs 92, q=3e-6) | **strong** |
| M342-M176 / W740-W400 (jar + post-jar suffix) | Ending of the tablet and rod formula (administrative token), not of seal names | Rods: M77 9 vs 0.5 (q=8e-8), ICIT 7 vs 0.7 (q=0.001). ICIT tablets 99 vs 59 (q=5e-18). Seals 0.18-0.23x expected in both corpora | **strong** (register) |
| M328 / W700 (cup) | Unit or measure word of the tablet/pottery docket (extends STATE F15) | Depleted on seals (M77 13 vs 27, q=0.001; ICIT 16 vs 38.5, q=1e-5). Enriched on Harappa moulded tablets ("sealings" in M77: 24 vs 12) and ICIT tablets (58 vs 42) | **moderate** |
| Tall strokes W031/W033/W034 + W480 (M134) on pottery | Pottery-mark numerals (capacity/quantity marks?) (extends F33) | ICIT pottery: W031 31 vs 15.6, W033 37 vs 20, W034 15 vs 6.6, W480 15 vs 5.3 (all q<0.05). Not tested as survivors in M77 (pottery n=109) | **moderate** |
| Jar M342 / W740 in a text | Title/office formula shared across cities (not a unique personal name) | Texts with the jar are found at 2 or more sites more often than length-matched texts without it: M77 55 vs 31 (q=5e-5); ICIT 48 vs 27 (q=0.001). Replicated | **moderate** |
| Short legends under the goat-antelope emblem | The goat-antelope seal carries a different (short) legend type | ICIT mean length 2.31 vs about 4.5 (n=13, BH q=0.024); M77 3.60 (n=10, p=0.06, same direction) | **weak** |
| Gulf / West Asian round-seal texts | Indus signs used in a non-Indus sign order (different language or system) | +2.17 bits/sign (CI 1.63-2.70); bigram gain -0.25 vs +1.37 native; M77 West Asian finds +1.96 (CI 1.23-2.63) | **strong** as an anomaly; interpretation open |
| Animal emblem vs text (any sign) | No lexical marking of the emblem (clan/office not written) | See Q1: unicorn vs other AUC 0.52 (null); cross-site 0.505; same-emblem Jaccard at null for all 16 class tests | **strong negative** |

## Findings in detail

### Q1. Does the whole text predict the seal animal? (`q1_animal.py`)
Unit: distinct seal texts; texts seen under more than one animal were dropped (18 in M77, 16 in ICIT). Classes with at least 10 texts. M77 n=1,149 (unicorn 945, short-horned bull 78, zebu 45, elephant 34, rhino 15, tiger 12, goat-antelope 10, buffalo 10). ICIT n=1,409. Model: L2 logistic regression on sign presence, initial sign, bigrams, length, numeral classes, jar-final and multiline. 5-fold CV. Null: labels permuted within site, 200x.

| Test | Observed | Null mean (95%) | p |
|---|---|---|---|
| M77 all features, balanced accuracy | 0.192 | 0.123 (0.159) | 0.005 |
| M77 macro AUC | 0.615 | 0.493 | 0.005 |
| M77 length + classes only | 0.219 | 0.124 (0.181) | 0.005 |
| M77 unicorn vs other AUC | 0.516 | 0.502 (0.550) | 0.39 |
| M77 **held-out** (fit dev 874, test 275), balanced accuracy | 0.240 | 0.124 | 0.035 |
| ICIT all features, balanced accuracy | 0.177 | 0.134 (0.176) | 0.045 |
| ICIT unicorn vs other AUC | 0.523 | 0.500 | 0.18 |
| ICIT **cross-site** (MD+Harappa to 250 texts from other sites), unicorn AUC | 0.505 | 0.499 | 0.44 |

- A weak multiclass signal exists among the minority animals and survives held-out testing. It comes mostly from length and coarse classes, not from specific signs. Per-class CV recall is 8-30%.
- Length by animal (within-site permutation, BH over 8 classes): goat-antelope is short in ICIT (2.31, q=0.024) and in M77 (3.60, p=0.06). Zebu is shorter in ICIT (3.96, p=0.046, q=0.18). Non-unicorn seals as a group are not consistently longer or shorter. Unicorn seals run +0.18 (M77) and +0.26 (ICIT) signs longer than the rest, both n.s.
- Same-emblem sharing: mean pairwise Jaccard within each class is at null in all 16 tests. The best case is rhino in ICIT, 1.45x, p=0.054, q=0.43. **Texts under one emblem do not share elements.** This extends F14 (single sign x animal) to whole texts.
- Caveat: the classifier has no planted-signal power calibration. I did not establish what effect size it could detect.

### Q2. Object-type registers (`q2_registers.py`) and copper tablets (`q2b_copper.py`)
Unit: distinct texts within each object type. Null: type labels permuted within site x length bin. Computed exactly as a sum of per-stratum hypergeometrics. BH over 3,500 tests (M77, unigrams + bigrams x 7 types), 2,844 (M77, sides 0/1 only, which removes the F15 side-2 docket), and 4,888 (ICIT). Survivors at q<0.05: 25, 22 and 33.
- Classifier (one-vs-rest CV AUC, within-site null): M77 seal 0.79, sealing 0.71, tablet 0.82, copper 0.91, pottery 0.77, rod 0.82, implement 0.82. ICIT: seal 0.80, sealing (TAG) 0.68, tablet 0.78, copper 0.89, pottery 0.81, bangle 0.83, implement 0.79, rod 0.66. All p<=0.01 with 100 permutations; null 95th percentiles 0.56-0.64.
- Replication: each M77 positive survivor was mapped to Wells signs and re-tested on ICIT, one-sided, Bonferroni over 17 tests. Replicated: copper M169/W407, M407/W845, M18/W095, M97-M25, M252-M97; rod M342-M176 and M176; tablet M176/W400; seal M99/W002 and M391/W820. Failed: the M77 "sealing" survivors. **Mapping caveat:** M77 "sealing" at Harappa and Mohenjo-daro is mostly moulded tablets (ICIT TAB:B). The M77 sealing M176 signal duly reappears as ICIT *tablet* W400 (193 vs 124, q=3e-23).
- Copper tablets: picture per tablet from the IM77 line file. 91 tablets with one complete text and one picture: 30 texts, 22 pictures.
  - Tablet level: 0.62 vs 0.06 (p=0.0002).
  - Die level with variant copies merged (20 legend families): nearest-neighbour picture prediction 0.030 vs 0.064 (p=0.81). Bigram-sharing pairs 0.111 vs 0.046 (p=0.078).
  - Sensitivity: with no family merging the test looks strongly positive (0.485 vs 0.065). That apparent signal is entirely variant copies of the same legend, for example M336-M89-M296-M342 vs ...-M98. This is the trap paragorth S-DARK-67.4 flagged.
  - Bigram M97-M25 / M25-M245 spans rhino, two-headed animal, unicorn and fs950, so even the most shared copper unit crosses pictures.

### Q3. Sealings (`q3_sealings.py`)
ICIT TAG* = true clay sealings, giving 66 complete distinct site-level texts.
- Only 2/66 match a seal at the same site. 13/66 recur at another site, against 10.0 expected from seal texts of the same length (exact stratified, p=0.17). Sealings are not a special travelling vocabulary.
- Cross-site sealing texts: Lothal W817-W002-W048-W740 = a Mohenjo-daro seal (the "wooden boxes" seal, paragorth S226). Dholavira W817-W002 is at 4 other cities. W171-W035 is at Dholavira/MD/Harappa. W003-W390 is at 4 cities.
- Which elements make a text multi-site (all objects, length-stratified, BH over 426 / 408 features): only the jar survives, in both corpora (ICIT 48 vs 27.4, q=0.0013; M77 55 vs 31.0, q=5e-5). Top non-surviving candidates: arrow W520 (14 vs 5.3, q=0.14) and "3 + tree" W003-W390 (4 vs 0.5). These match paragorth's pan-Indus "3-comb/33+W520" terms.
- Lothal sealing-back packaging (Frenez & Tosi 2005) vs text was done by paragorth (S226, S-DARK-13.4). It is null after deduplication except the single elephant-seal text on 10/10 wooden boxes. Not redone.

### Q4. Gulf / West Asian finds (`q4_gulf.py`, `q4b_gulf_internal.py`)
Interpolated Kneser-Ney bigram; native texts scored by 10-fold CV; distinct texts. Foreign set: 33 ICIT texts from 21 sites (30 Gulf/Mesopotamia/Iran, 3 Central Asia). Native: 3,177.

| Group | n | bits/sign | matched native | diff [95% CI] | p |
|---|---|---|---|---|---|
| All foreign | 33 | 6.52 | 5.17 | +1.35 [+0.86, +1.85] | 1e-4 |
| Foreign, round/cylinder | 18 | 7.24 | 5.07 | **+2.17 [+1.63, +2.70]** | 1e-4 |
| Foreign round, pseudo-script removed | 15 | 7.46 | 5.02 | +2.44 [+1.85, +2.98] | 1e-4 |
| Foreign round vs HOME round seals | 18 | 7.24 | 5.15 | +2.09 [+1.53, +2.60] | 1e-4 |
| Foreign, square seals | 8 | 5.74 | 5.30 | +0.44 [-0.54, +1.54] | 0.19 |
| Foreign, other objects (pots, tags) | 7 | 5.58 | 5.30 | +0.28 [-0.51, +1.03] | 0.31 |
| Unknown provenance | 28 | 5.56 | 5.00 | +0.56 [+0.02, +1.15] | 0.018 |
| Home round vs home square seals | 344 | 5.18 | 5.01 | +0.17 [+0.02, +0.33] | 0.011 |
| Dholavira (regional reference) | 142 | 5.68 | 5.16 | +0.52 [+0.27, +0.77] | 1e-4 |
| **M77 West Asian finds** (replication) | 17 | 6.67 | 4.71 | +1.96 [+1.23, +2.63] | 1e-4 |

- Planted controls at n=33 (detection rate): real held-out 0.06 (the false-positive rate); within-text shuffled order 0.99; frequency-matched sign substitution 1.00; 30% substitution ("dialect") 0.76.
- Decomposition (unigram bits; bigram gain over unigram):
  - foreign round: 6.99; **-0.25**
  - home round: 6.55; +1.37
  - home square: 6.36; +1.35
  - planted shuffled order: 6.25; -0.37
- So the foreign round texts use somewhat rarer signs, and their order carries no Indus bigram information at all. OOV rate is only 5%: they use Indus signs.
- Internal structure: 0 ordered bigrams are shared by 2 or more of the 17 distinct foreign round texts (within-text-shuffle null 1.11). Home round subsets of the same size show +1.8 over their nulls (90% range -0.25 to 4.2), so power is low.
- Interpretation: strong evidence that Gulf round-seal legends are not Indus-grammar texts. That fits Parpola's different-language hypothesis and paragorth S20/S46/S98 (person sign + "1" blocks), but pseudo-script or ad hoc use of signs fits equally well. Square seals found abroad (Kish, Gonur, Altyn Depe, Shortughai, Nippur) are ordinary Indus texts.

### Q5. Chronology (`q5_chronology.py`)
Dated distinct texts (ICIT): MD 750 (Early/Intermediate/Late; period level only, because the sub-phase numbering direction is uncertain), Harappa 443 (Periods 1-2, 3A/B, 3B/C, 3C, 4/5), Dholavira 126 (stages 1-6), Kalibangan 97.
- 55 feature x site Spearman trends (null: phase permuted within object type): none survives BH. Best: Harappa text length rises over time, rho +0.13, p=0.008, q=0.15. MD multiline falls, p=0.005, q=0.15.
- Whole-text early-vs-late classifier: MD AUC 0.569 vs 0.515 (p=0.02); Kalibangan 0.650 vs 0.455 (p=0.03, n=97); Harappa and Dholavira null. A weak, non-replicating signal.
- Innovation/obsolescence: 102 signs on relative time within site x object type, 5000 perms. Best W690 (earlier, p=0.002, q=0.20; same direction at Harappa and MD). Nothing survives BH. This extends F9/F17 from two sites to four, with whole-text models.
- Harappa Period 1-2 (pre-urban): 22 distinct texts, 21 of them pottery marks of 1-3 signs (numerals, W700, W698). 75% of tokens recur in dated Period 3 texts and 97% elsewhere at Harappa. The early marks are a subset of the later system, and the long seal texts appear only in Period 3.

### Q6. Metrology (`q6_metrology.py`)
Distinct texts per object type. Local excess E(v) = log count(v) minus the mean of the log counts of its neighbours; bootstrap CIs.
- M77 short strokes:
  - counts: 1:157, 3:129, 4:61, 5:36, 6:34, 7:67, 8:7, 12:52
  - 4: E=-0.11 [-0.44, +0.19]
  - 8: E=-0.84 [-1.87, +0.06]
  - 7: E=+1.43 [+1.03, +2.03]
- M77 tall strokes:
  - counts: 1:134, 2:255, 3:186, 4:11, 5:20
  - 2: E=+0.48 [+0.31, +0.65], consistent with binary
  - 3: E=+1.24, a larger spike
  - 4: E=-1.68 [-2.41, -1.15], a trough
- ICIT replicates both patterns: short 8 E=-1.00 [-1.99, -0.17]; tall 4 E=-0.91.
- Pottery shows the same pattern.
- Pairs of numerals in one text (M77 n=140; ICIT n=209): ratio a power of two in 0.19 / 0.25 of pairs, vs 0.22 / 0.23 at random.
- **The weight series is not reflected in stroke counts.** This agrees with paragorth S4/S207 and STATE F5. Short-3's E is inflated because short-2 is excluded as a connective, so read 3 against 4 only.

## Hypotheses tested

| Hypothesis | Verdict |
|---|---|
| Whole text predicts the seal animal | **Weak support** for a minority-class signal (held-out p=0.035). **Refuted** for unicorn vs other and cross-site |
| Texts under the same emblem share elements (clan/office emblem) | **Refuted** (16/16 null) |
| Non-unicorn seals have different-length texts | **Inconclusive**, apart from goat-antelope short (weak) |
| Object types have distinct registers | **Supported** (strong; replicated M77 to ICIT) |
| Copper text predicts copper picture | **Supported** at the legend level; **refuted** at the sign level once variants are merged |
| Copper-only one-sign faces stand for the picture | **Inconclusive**, suggestive (n=6 pairings) |
| Sealing texts travel more than seal texts | **Refuted** (p=0.17) |
| Some elements mark pan-Indus (multi-site) texts | **Supported** for the jar (replicated); others inconclusive |
| Gulf texts are anomalous under a native n-gram model | **Supported** for round seals (strong, replicated in M77); **refuted** for square seals abroad |
| Gulf texts form their own consistent grammar | **Inconclusive** (no shared bigrams; low power) |
| Sign innovation / obsolescence across phases | **Refuted** at current power (0/102 after BH) |
| Stroke numerals follow binary weight ratios | **Refuted** |

Tests run: Q1 about 40 (classifier perms, 16 length, 16 sharing); Q2 11,232 enrichment + 17 replication + 15 classifiers; Q2b 4; Q3 835; Q4 15 comparisons + planted controls; Q5 161; Q6 CI-based. Corrections are as stated per block.

## Caveats and what would falsify
- The copper picture labels come from IM77 fs80 (paragorth showed the Wells symbol field is unreliable on copper). The legend-family definition changes the die-level verdict, and I report both versions.
- The Gulf result rests on 18 texts, and some readings are uncertain (gulf_seals.csv "probable/uncertain"). It is falsified if better transcriptions of the same seals bring their bigram gain toward +1.3 bits, or if a larger set of home round seals shows the same negative bigram gain.
- Register findings mix function with site and production (Harappa moulded tablets). Site x length strata control the first two but cannot separate "object function" from "workshop".
- No classifier calibration against planted signal (Q1). A null emblem effect smaller than the detectable size remains possible.

## Next experiments
1. Planted-signal calibration for Q1: inject one sign into k% of a minority class and find the detectable k.
2. Copper one-sign faces: compare the M362/M363/M346/M184 drawings with the copper pictures (CISI vol. 2 pp. 255-264) to test the logogram reading by shape.
3. Gulf: score the 28 unknown-provenance texts and the Gulf seals in `gulf_seals.csv` individually. Check whether the "person + 1" texts (paragorth S99) carry the anomaly or whether it is spread evenly.
4. Registers: separate moulded from incised Harappa tablets and test whether the W400/W700 formula is a production (mould) or function effect, using HARP find-groups.
5. Dholavira's +0.52 bits regional anomaly: which signs or bigrams drive it? It is a natural test of regional variation in a city absent from M77.
