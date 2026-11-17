# Logogram anchors: can any sign be given a meaning from pictures alone?

Area: logograms. Code: `experiments/logograms/l1..l5_*.py` (run from the repo root with `.venv/bin/python`, in order l1, l2, l3, l4, l5). Logs: `l*.log`. Numbers: `results.json`. Catalogues: `copper_tablet_types.csv` (legend x other face, with tablet counts per source) and `copper_tablets.csv` (one row per tablet per source). Builds on `experiments/context` (Q2b) and paragorth S-DARK-67.

## Conclusion first

1. **No sign meets the bar for a word-level decipherment.** Every candidate equation "sign S = picture P" rests on **one** independent legend type. Most rest on one or two physical objects, which are listed in both corpora. One coincidence is not a decipherment, so none of the meanings below is better than *low* confidence.
2. **What is solid is a structural fact, not a set of meanings.** On Mohenjo-daro copper tablets, the face that normally carries a picture can instead carry one large sign.
   - The two never share a tablet: 0 of 36 sign-face tablets also have a picture, against 227 picture tablets.
   - Each legend takes **one** sign face, consistently: 8 of 8 legends with two or more sign-face tablets always show the same sign family (null mean 0.9, p=1e-4; M77 alone 4/4, p=3e-4; ICIT alone 7/7, p=1e-4).
   - On five legends the same legend appears with a picture on other tablets. That makes these five the substitution cases.
3. **The substituting signs do not behave like names of the pictured animal.**
   - The horned-U sign (M362/M363/M364 = W777/W780/W781/W782) replaces two different pictures: the horned archer personage (fs520) and the goat-antelope with twirled horns (fs139). That breaks "one sign = one picture".
   - The obvious class reading, "horned head", explains its partners no better than chance: 3/3 head-sign partners are horned, against a base rate of 0.79, p=0.49.
   - M355 (W753) is a horned U with a wheel inside, yet it replaces the **hare**.
   - Most signs do not mean the pictured animal; at best they mark a class or emblem.
4. **On seals and tablets, pictorial signs do not echo the picture.** Ten pre-registered sign/picture pairs were tested in M77 and ICIT (17 tests, site x object-type stratified): fish, pipal leaf, human figure, horned-U, horned man, bow-man, bird, quadruped, svastika, branch. All are null (all p>=0.26, all q=1).
   - Pipal-leaf signs occur in 0 of 40 (M77) and 0 of 45 (ICIT) texts on tree/pipal objects.
   - An exploratory scan of 835 sign x picture-group tests finds nothing after correction. The best hit is M242 on scene seals: 4 vs 0.24 expected, q=0.21. M242 is a detached second-line sign, which is common on large seals.
5. **Variant copies give no picture/sign minimal pairs outside copper.**
   - We searched for a text T with picture P and T plus one sign without a picture. This gives 114 pairs in ICIT and 109 in M77.
   - (S, P) combinations that recur across two or more text types are at chance: ICIT 9 vs 10.4 expected, p=0.85; M77 10 vs 11.1, p=0.83.

## Candidate sign meanings

| Sign (M / W) | Drawing | Proposed meaning | Independent supporting cases | p vs chance | Counterexamples | Confidence |
|---|---|---|---|---|---|---|
| **M184 / W341** | quadruped: grid body, 4 legs, one upright spike at the front | "rhinoceros" (stands for the picture of legend M204-M245-M342) | **1 legend**; 4 sign-face tablets (MD 3334, 3398 = CISI M-516, M-517) vs 2 rhino-picture tablets (MD 1707, ICIT 2522, probably one object) | n/a for a single case (the substitution system: p=1e-4, T3) | (a) M77 reads M184 inside 245-184-252 beside an ox-antelope; Wells reads a different two-horned animal sign there (W343). (b) 3 seal uses with no rhino: 2 with no picture, 1 bull (West Asian). (c) The minimal pair M204-M245-**M358**-M342 = ox-antelope (19 tablets), so the legend differs by one sign | low |
| **M346 / W749** | frontal head, comb top, horns sweeping back and curling | "goat-antelope with horns arching back" (fs135) | **1 legend** (M389-M72-M326-M342); 4 tablets (MD 3313, 3343 = M-597, M-1550) vs 3 M77 picture tablets of this exact legend (7 incl. the M48 variant) | n/a | W749 also faces two legends beginning M70-M51 (M-1548, M-1549, ICIT 2465). Neither has a picture version; the related legend 51-130-149-342 carries buffalo/bull. Copper-only, so it cannot be checked elsewhere | low |
| **M362/M363/M364** (W777/W780/W781/W782) | U-shaped face with two horns (branched, arrow or curled) and an inner "fish-like" mark | **not** a specific animal. If anything, "horned (divine?) being", an emblem shared by two legends | 2 legends: horned archer personage (8 sign-face tablets vs 15 picture tablets) and goat-antelope with twirled horns (9 sign-face tablets, two spelling variants, vs 6 picture tablets) | "horned" class: binomial p=0.49 | One sign, two different pictures. The horn sub-types (branched vs curled) do not track the pictures, and Mahadevan and Wells disagree on them for the same objects. M364 occurs on 2 unicorn seals | low (meaning); **high** that it fills the picture slot |
| **M355 / W753** | horned U with a wheel inside | "hare"? (the slot partner of the hare legend) | 1 legend; 2 ICIT tablets (M-593, M-1547) vs 22 hare-picture tablets | n/a | Hornless animal, horned sign. 2 Harappa/MD unicorn seals, one with M355 as the whole text | very low |
| **M183 / W321** | quadruped frame with legs | "animal" (class sign) inside the hare legend | 1 legend (fixed spelling on 25 tablets) | n/a | 1 seal use (unicorn) | very low |
| M48 ~ M326 | zigzag-bird / pipal leaf | interchangeable in one legend (both copies carry the fs135 goat-antelope) | 1 legend (7 tablets) | n/a | Free variation or synonymy; says nothing about meaning | descriptive |
| Pictorial signs on seals (fish, pipal, man, bird, bow-man, horned man, svastika, branch, horned-U, quadruped) | | depict the object's picture | 0 | all p>=0.26, q=1 (17 tests) | Pipal 0/40 and 0/45 | **refuted** |

## Findings in detail

### L1. Copper tablet catalogue (`l1_copper_catalogue.py`)
- Sources:
  - IM77 line file: 135 text numbers. Line 9 marks a side that has a picture and no text, so its fs80 code is the picture.
  - ICIT TAB:C: 230 objects, including CISI vol. 2-3 tablets absent from M77. Its picture is only the coarse `symbol` field.
- ICIT legends were mapped to Mahadevan numbers (bridge plus copper parallels listed in `common.W2M_EXTRA`) only to group copies of a legend. Evidence is counted by legend and legend family, so objects listed in both corpora are not double-counted.
- Tablet kinds:

| Source | Picture | One-sign face | Second text | One face only |
|---|---|---|---|---|
| M77 | 96 | 13 | 7 | 18 |
| ICIT | 131 | 23 | 11 | 24 |

- **No tablet has both a picture and a one-sign face.**
- 64 legend families. The full table (legend x other face, with M77 text numbers and CISI ids) is in `copper_tablet_types.csv`.
- New relative to context/Q2b: ICIT adds the hare legend's sign face (M355/W753). It also adds 4 more horned-U faces on the goat-antelope legend (M-1555 to M-1558) and 2 more on the archer legend (M-1563, M-2054). It identifies the Wells codes of the M77 sign faces (M184=W341, M346=W749, M405=W841, M51=W957).

### L2. Substitution tests (`l2_substitution.py`)
- **T2. Five legends occur both with a picture and with a one-sign face:**
  - 204-245-342: rhino / M184
  - 389-407-124-169-373-287-342: archer / horned-U
  - 59|70-112-194-18-211-87-169: twirl-horned goat-antelope / horned-U
  - 389-72-326-342: arching-horn goat-antelope / M346
  - 65-336-89-407-169-183-169: hare / M355
- Three more sign faces sit on legends that never carry a picture: M51, M405, and M96 (five strokes). So the slot is not reserved for pictorial signs.
- **T3 consistency:** 8 of 8 legends with two or more sign-face tablets always take the same sign family. The permutation null mean is 0.88 (p=1e-4).
  - Caveat: copies of one legend were probably made as a batch, so this shows the sign face was part of the tablet *type*, like the picture. It does not show that the sign means the picture.
- **T4:** Legends with a sign face are no more often pictured than other legends: 5/8 vs 15/21, Fisher p=0.82. The sign faces are not drawn preferentially from picture legends.
- **T5/T6 one sign, one picture?**
  - M184, M346 and M355 each have only one pictured partner.
  - Horned-U has two pictured partners with different pictures.
  - Horned partners: 3/3, against a base rate of 0.79 over 19 pictured families (p=0.49). M355 + hare is a counterexample to "horned head".
- **T7 copper minimal pairs** (exact legends at edit distance 1):
  - 204-245-342 (rhino) vs 204-245-**358**-342 (ox-antelope, 19 tablets): the only pair whose picture differs.
  - The other three pairs keep the picture: M48/M326, M59/M70, and a final M98.
  - Three legends carry more than one picture:
    - 53-67-407-124-169: tiger, horned tiger, ox-antelope
    - 345-341-18-252-97-25-245-245: unicorn, two-headed animal (+ double-axe in ICIT)
    - 336-89-296-342-98: elephant, horned tiger
  - So even legend to picture is not one-to-one.

### L3. Iconic agreement on seals (`l3_iconic_seals.py`)
- Unit: distinct (text, picture), only objects with a picture, copper excluded (M77 1,538; ICIT 2,124). The null permutes picture labels within site x object type. Results are in the table above and `l3.log`.
- Both the horned-personage seals (fs470/480 "proto-Shiva", 520/530) and the scene seals were examined. Their texts share no sign with each other or with the copper archer legend. Example: 2420 (three-faced personage) reads M1 | M3-M216-M229-M344-M59-M342.

### L4. Variant copies (`l4_variant_copies.py`)
- The picture-to-sign minimal pairs recur no more than under picture permutation (p=0.85 ICIT, 0.83 M77).
- The extra sign is mostly at the start of the text: 65/114 and 55/109, the typical "added opener" pattern. These signs are not picture substitutes.
- Exact repeats (3+ signs) whose copies carry different pictures: 16 of 1,246 texts (ICIT) and 12 of 1,177 (M77).

### L5. Other contexts of the candidates (`l5_other_contexts.py`)
- Outside copper the candidates are rare: 8 M77 and 4 ICIT occurrences, all on seals, mostly unicorn seals.
- They are text-initial more often than chance: M77 4/7 vs 1.23 expected (p=0.02); ICIT 3/4 vs 1.10 (p=0.05; overlapping objects).
- Initial position is the opener class (structure agent), not the noun-like medial core. This weakly fits an emblem or title sign better than a common noun. n is tiny.

## Hypotheses tested

| Hypothesis | Verdict |
|---|---|
| A one-sign face can replace the picture on copper tablets | **Supported** (exclusive slot; 5 legends with both forms; legend-specific sign, p=1e-4) |
| Each substituting sign names its picture (one sign = one picture) | **Refuted** for horned-U (2 pictures); **inconclusive** for M184, M346, M355 (one case each) |
| Horned-U = "horned head/being" | **Inconclusive** (p=0.49; hare counterexample if M355 is a variant) |
| Pictorial signs in seal texts echo the seal picture (10 pairs, 2 corpora) | **Refuted** (all q=1) |
| Picture/sign minimal pairs among duplicated non-copper texts | **Refuted** (at chance) |
| A single sign inside copper legends determines the picture | **Inconclusive**: one minimal pair (M358: rhino vs ox-antelope); three legends carry several pictures |

Tests run: L2 7 blocks (permutation/Fisher/binomial); L3 17 pre-registered + 835 exploratory (BH within each); L4 2 permutation tests; L5 2. No held-out split was needed for L2, because the copper corpus was not tuned on. L3 was pre-registered. ICIT acts as the second transcription, but it overlaps M77 for most Mohenjo-daro copper objects.

## Caveats and what would falsify
- Iconic judgements (M184 looks like a one-horned quadruped; M346 has horns sweeping back) are mine. They are not blind, and they were made from sign drawings only, not photographs of the pictures. Wells and Mahadevan disagree on the horn details of the same horned-U faces.
- Object overlap between M77 and ICIT could not be resolved fully (no shared ids). Counts by legend are safe; tablet counts per source are not additive.
- The ICIT `symbol` field is coarse on copper ("Othr" covers the whole ox-antelope legend). The M77 fs80 codes were used for every picture-class claim.
- The M184 = rhinoceros reading would be **supported** by a second, different legend whose rhino picture is replaced by M184, or by M184 in a text beside a rhino picture. It would be **falsified** by M184 standing in for a non-rhino picture. The same logic applies to M346 (goat-antelope with arching horns).

## Next experiments
1. **Blind iconicity rating.** Show independent raters the 5 substitution signs and photographs of the copper pictures (CISI vol. 2 pp. 255-264, vol. 3), shuffled, and score the matches against chance. This is the only way to turn the M184/M346 readings into evidence.
2. Check the CISI photographs of MD 3378 (245-184-252, ox-antelope): Mahadevan reads M184 and Wells W343. If it is the two-horned W343, then M184 = one-horned (rhino) and W343 = two-horned (ox-antelope). That would be a second, independent iconic case.
3. Look for additional copper and moulded-tablet publications (post-CISI vol. 3) carrying the five substitution legends. Each new sign face is a test of the slot-specific prediction: the same sign family on the same legend.
4. Horned-U: test whether the archer and the twirl-horned goat-antelope legends share anything else (find spot, size, tablet shape). That would show whether the horned-U marks a cult or emblem class rather than an animal.
