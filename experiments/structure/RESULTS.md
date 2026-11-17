# Structure of the Indus texts: direction, inventory, positional classes, segmentation, grammar

Structural analyst, 2026-11-14. Code: `experiments/structure/*.py` (run from the repo root with `.venv/bin/python`, in this order: q1, q2_inventory, q2_allographs, q3_positional, q3b, q4_segment, q4b, q4c, q5_grammar, q6_icit, build_sign_table). Numbers: `results.json`. Per-sign table: `sign_table.csv`.
Unit: distinct texts (`distinct()`) unless stated. Models were developed on `dev`. `heldout` was used only for the final test of each model. ICIT was used as an independent transcription, with Dholavira-only texts as an out-of-sample site.

## Conclusion first

1. **Direction.** The transcribers' reading order agrees with the sign grammar, and the L-to-R exception texts are real. Read in their labelled direction, these texts behave like R-to-L texts, not like mirror images of them. M342 (the jar) is final in L-to-R texts too: 33 last vs 3 first in M77, 36 vs 2 in ICIT. Our data cannot fix the *absolute* direction. That still rests on physical evidence.
2. **Inventory.** About 400 distinct signs are observed in the Mahadevan list (417 published, about 6 to 16 probable allograph merges). The estimated true inventory, including unseen signs, is about **550 (Chao2 565, 95% CI 508-658)**.
   - At a matched 10,005 tokens, Indus shows 417 types and needs 120 signs to cover 90% of tokens.
   - Linear B shows 212 types and needs 63. Latin letters show 24 and need 14.
   - Proto-Elamite (473 types, 139 signs) and Sumerian seal legends (496 readings, 152 signs) look like Indus.
   - The curve is incompatible with an alphabet or a pure syllabary. It falls within the logo-syllabic/logographic range.
3. **Positional classes.** Only **three** positional classes are reproducible: openers, medial core and closers. K=3 has bootstrap ARI 0.67; at K>=5 the ARI is 0.40-0.53.
   - 82 of 124 signs (n>=10 texts) have a positional preference beyond a within-text shuffle (BH q<0.05).
   - The classes hold on held-out texts: 87.5% nearest-centroid agreement vs 47% chance.
   - They also hold on ICIT (92% of bridged signs get the same class) and at Dholavira.
   - Numeral (stroke) signs do **not** form a stable distributional class.
4. **Segmentation.** Segments found without supervision are short: 1.4 signs on average, mostly fixed pairs such as M267-M99, M347-M342, M336-M89(-M211).
   - Two methods agree beyond chance: Dirichlet-process (DP) vs PMI boundary F1 0.49 vs null 0.35, z=25.
   - The segment lexicon predicts held-out texts better than a sign unigram and better than a lexicon learned from shuffled texts. It predicts **worse than a sign bigram** (6.19 vs 5.83 bits/sign).
   - Planted controls show this ranking also happens in a real language with real words (Ur III seal legends). So it is *not* evidence against words.
   - Segment inventories of Mohenjo-daro and Harappa seals are as similar as random halves of one corpus.
5. **Grammar.** Order is far stricter than a bag of words.
   - 67% of texts fit `opener* core closer*` vs 25% after shuffling within texts.
   - The real order of a held-out text beats all its permutations in 63% of cases (5.5% expected), and stays at a mean percentile of 0.94.
   - 97% of sign multisets that recur on 3 or more objects always appear in one order.
   - Repeats longer than 5 signs (up to 10) exist only as re-attestations of the same text, not as reused phrases.
   - All of this replicates on ICIT and on Dholavira-only texts. Dholavira's specific pairings are, however, less predictable from Mohenjo-daro and Harappa (see 6).
6. **ICIT / Dholavira.** Every structural result replicates on the independent Wells transcription. One difference: an M77 bigram gains only 0.71 bits/sign on long Dholavira-only texts vs 1.19 on M77 held-out. The order skeleton is shared, but there may be regional differences in pairings (n=89 runs).

## 1. Writing direction (`q1_direction.py`)

| Test (distinct line sequences, length >=2) | M77 | ICIT |
|---|---|---|
| R-L lines: jar last / first | 678 / 6 of 2,077 (32.6% / 0.3%) | 713 / 7 of 2,143 |
| **L-R lines: jar last / first** | **33 / 3 of 150** (binomial p=1e-7) | **36 / 2 of 134** (p=3e-9) |
| Spearman rho of sign final-rate, L-R vs R-L (as labelled) | **+0.66** (53 signs) | +0.52 (39) |
| same, L-R final vs R-L *initial* (mirror hypothesis) | **-0.52** | -0.17 |
| Bigram direction classifier (trained on 75% of R-L): held-out R-L accuracy | 93% (483/520) | 95% |
| ... applied to L-R lines: read as labelled is more probable | **89% (134/150), p=1e-24** | 90% (120/134), p=2e-22 |
| ... jar-free (all lines with the jar removed, train and test) R-L / L-R | 90% / **84% (86/102), p=5e-13** | 89% / 84% (68/81) |
| Dholavira R-L, classifier trained on other ICIT sites (jar-free) | 86% (76/88) (85%, 52/61) | |

- **Asymmetry.** The first position is diverse: 291 sign types, H=6.69 bits. The last position is concentrated: 196 types, H=4.94 bits, with the top five closers M342, M176, M211, M169, M1.
- **L-R texts by object type (M77).** Jar last/first: seals 15/1 of 64, sealings 6/1 of 30, miniature tablets 8/1 of 42, pottery 3/0 of 8. The lower jar-final share in L-R texts (22% vs 33%) partly reflects this object mix.
- **Multi-line texts.** Line order cannot be recovered from the grammar: the given order beats the swapped order in 61 of 112 texts (p=0.20). The jar ends the first line more often than the last (26 vs 14), and 40 of 112 last lines are a single sign. Second lines look like add-ons, not continuations.
- **Caveats.**
  - The transcribers may have used the jar itself as a direction cue. The jar-free test addresses this partly: 84% of L-R texts are still correctly oriented.
  - The test shows that the labels agree with the grammar. Which end is the "beginning" is a convention our data cannot decide. It rests on physical evidence (stroke overlaps, cramping).
- **What would falsify this:** L-R texts whose oriented grammar matched the mirror (rho > 0 with R-L initial-rates), or a jar-free classifier at chance.

## 2. Sign inventory (`q2_inventory.py`, `q2_allographs.py`)

### 2a. Size and unseen signs

| Corpus (distinct texts) | texts | tokens | types | hapax | Good-Turing coverage | Chao1 | **Chao2 (95% CI)** | ACE | signs for 90% |
|---|---|---|---|---|---|---|---|---|---|
| M77 all | 2,270 | 10,005 | 417 | 119 | 0.988 | 557 | **565 (508-658)** | 544 | 120 |
| M77 with the 16 shaunmortal v3 merges | | | 401 | | | 541 | 549 (492-642) | | 104 |
| M77 Mohenjo-daro | 1,342 | 6,215 | 353 | 107 | 0.983 | 491 | 488 (433-581) | 467 | 115 |
| M77 Harappa | 621 | 2,424 | 255 | 81 | 0.967 | 320 | 323 (293-375) | 348 | 105 |
| ICIT all (Wells list) | 3,504 | 13,190 | 712 | 232 | 0.982 | 947 | 947 (879-1,043) | 971 | 182 |
| ICIT Dholavira | 175 | 559 | 156 | 73 | 0.869 | 253 | 246 (203-327) | 255 | 101 |

**Rarefaction** (types seen at matched token counts, mean of 30 random text orders):

| | 500 tokens | 2,000 tokens |
|---|---|---|
| Mohenjo-daro | 140 | 243 |
| Harappa | 137 | 239 |
| Lothal | 130 | |
| ICIT Mohenjo-daro | 161 | 324 |
| ICIT Harappa | 157 | 314 |
| ICIT Dholavira | 148 | |

Sites do not differ in sign richness once sample size is controlled. The Chao2 difference between Mohenjo-daro and Harappa is a sample-size effect. The Wells list yields about 1.6x more types than Mahadevan's at the same sample size. That is a difference in how finely variants are split, not more signs.

### 2b. Comparison with known scripts at matched sample size

Comparison corpora are data files in `sources/paragorth_Indus-/data/codelib`, sub-sampled by text.

| Script | types @2k | types @10k | Chao2 @10k | signs for 90% | top-10 share | hapax share @10k |
|---|---|---|---|---|---|---|
| Latin letters (alphabet) | 23 | 24 | 24 | 14 | 0.78 | 0.01 |
| Linear B (syllabary + logograms, admin) | 142 | 212 | 262 | 63 | 0.30 | 0.21 |
| Linear A (Unicode signs; 8,967 tokens in total) | 184 | 257 @5k | 436 @5k | 71 | 0.48 | 0.36 |
| **Indus M77** | **249** | **417** | **565** | **120** | 0.33 | 0.29 |
| Proto-Elamite (CDLI, variants collapsed) | 276 | 473 | 671 | 139 | 0.49 | 0.31 |
| Sumerian Ur III seal legends (sign *readings*) | 291 | 496 | 668 | 152 | 0.42 | 0.28 |

**What the curve implies.**
- An alphabet is saturated after a few hundred tokens.
- A syllabary with logograms (Linear B) reaches about 210 types and 63 signs for 90% coverage.
- Indus shows twice that and is still growing at 10k tokens: about 75 new types per 5k tokens, against about 32 for Linear B.
- Its profile sits next to Proto-Elamite and the genre-matched Sumerian seal legends (names + titles).
- This supports a **logographic or logo-syllabic** system with a few hundred core signs, as most authors have argued, now shown at matched sample size.

**Caveats.**
- Sumerian readings over-count signs, because one sign can have several readings.
- Mahadevan's list contains ligatures and composite signs, which inflate the count. Even so, the frequent core (120 signs for 90% of tokens) is twice Linear B's.
- Corpus genre matters: Indus texts are short seal legends.

### 2c. Probable allographs (image similarity × context indistinguishability; dev only)

**Screening.** 137 signs have at least 8 dev tokens. Pairs in the top 2% of drawing similarity (cosine of blurred, normalised drawings >= 0.79) gave 187 pairs. Each pair got a permutation test of whether its left/right contexts differ (300 permutations), plus a mutual nearest-neighbour rank in context space. Each candidate's drawings were then checked by eye.

- **Probable allographs (accepted after visual check):**
  - M14→M12 (person; contexts p=0.98)
  - M386→M387 and M389→M387 (leaf outline; p=0.88, 0.40)
  - M226→M216 (crossed chevron)
  - M344→M343 and M345→M343 (handled jar with 1/2/3 inner strokes; p=0.09, 0.05). Inner strokes may still carry meaning (shaunmortal F16).
- **Possible only:** M286~M267.
- **Rejected on drawing:** M391~M286, M177~M397 (an artefact of the blurred images).
- **Variant families: contexts nearly identical (mutual top-5, cosine >= 0.49) but statistically distinguishable at high frequency:**
  - fish M59/M65/M67/M70/M72
  - openers M267/M391/M284
  - M387/M389
  - M216/M222

  These are either allographs used with scribal or site preferences, or distinct signs of one class. The data cannot decide.
- **Look-alike but distinct (150 pairs, contexts differ at p<0.01):** includes M342 vs M343/M344/M345/M348 (jar closer vs handled jar), M149 vs M150, M99 vs M100, M403 vs M406/M407, M124 vs M125. **We disagree with shaunmortal M3 on M97~M98:** the one-stroke variants differ in context here (p<0.01).
- **Held-out validation, and why it is weak.** Merging the 9 candidates lowers held-out bigram bits/sign from 5.000 to 4.947. Random frequency-matched merges give 4.980 ± 0.009 (z=-3.6, p=0.005). However, merging *context-matched pairs that do not look alike* gives 4.937 ± 0.018 (p=0.67). **Held-out perplexity rewards any merge of similarly behaving signs, so it cannot validate allography.** This weakens shaunmortal M4's "validated by prediction". Allography needs palaeographic evidence: the same object, scribe or seal, or graded drawings.

**How many signs are truly distinct?** About 411 after the accepted merges, and about 400 if the variant families collapse (shaunmortal v3: 401). With unseen signs, the true inventory is about 550 (CI about 490-660). The unseen signs are mostly rare forms, many probably ligatures or variants.

## 3. Positional classes (`q3_positional.py`, `q3b_context_classes.py`)

**Method.**
- Clean distinct texts only (no break mark, flagged complete): 1,758 texts in M77.
- Signs on at least 10 distinct texts: 124.
- Profiles over initial / medial / final / standalone positions.
- Null: within-text shuffle (300 shuffles). BH correction over 124 tests.
- **82 of 124** signs are positionally non-random (q<0.05). ICIT: 85 of 133.

**Choosing K.** Bootstrap stability (adjusted Rand index, ARI) by number of classes K:

| K | 2 | 3 | 4 | 5 | 6 | 8 |
|---|---|---|---|---|---|---|
| M77 ARI | 0.63 | **0.67** | 0.52 | 0.53 | 0.47 | 0.41 |
| ICIT ARI | 0.67 | **0.67** | 0.57 | 0.40 | 0.46 | 0.42 |

This replicates shaunmortal M1b (K=3) on our split.

**Classes (centroid: initial / medial / final share):**

| Class | signs | tokens | centroid | top members (M77) | ICIT top members |
|---|---|---|---|---|---|
| **Opener** | 37 | 1,496 | 0.47 / 0.44 / 0.08 | M267, M391, M86, M293, M389, M17, M216, M197, M150, M28 | W861, W820, W031, W817, W003, W920 |
| **Medial core** | 70 | 4,271 | 0.15 / 0.79 / 0.06 | M99, M59, M87, M67, M162, M336, M123, M65, M343, M89 | W002, W032, W220, W240, W060, W033, W741 |
| **Closer** | 17 | 1,719 | 0.07 / 0.22 / 0.69 | M342, M176, M211, M169, M1, M15, M12, M254, M328, M60 | W740, W400, W390, W520, W090, W151, W700 |

- **Held-out.** Classes learned on dev were re-measured on held-out texts. Pooled class profiles: openers 53% initial, core 77% medial, closers 71% final. Per sign, nearest-centroid agreement is **87.5%** (80 signs) vs 47% chance. Dev vs full-data class agreement: 91%.
- **Cross-transcription.** Of 105 bridged signs, 97 (92%) have the same class in M77 and ICIT. Spearman rho of bridged profiles: initial 0.93, medial 0.92, final 0.80.
- **Dholavira.** Under ICIT classes, Dholavira profiles are: closers 72% final, openers 44% initial, core 74% medial (n=61/141/61 tokens).
- **Numeral-like.** Stroke signs, identified by drawing, are spread over core (M99, M87, M89, M102, M97, M98, M104, M112, M121) and opener (M86, M106, M109, M103). With context features (PPMI neighbour profiles), no stable class emerges (ARI 0.19-0.34 for K>=3). A short-stroke group (M102, M104, M106, M109, M112, M121, M124, M25...) appears only at unstable K (best hypergeometric p=0.002 at K=10, 9 values of K tried, ARI 0.24). Shaunmortal's finer classes ("title", "number-name") are not reproducible from distribution alone.

## 4. Segmentation (`q4_segment.py`, `q4b_site_seals.py`, `q4c_planted_control.py`)

**Methods.**
- **A.** Goldwater-style DP unigram word model: Gibbs sampling with annealing, alpha=20, 3 chains. Boundary F1 between chains: 0.92.
- **B.** PMI<0 boundaries.
- **C.** Branching-entropy rise.

**Planted control first** (corpora with known words, sub-sampled to Indus size, about 10k tokens):

| Corpus | true boundary rate | DP F1 (null) | PMI F1 (null) | BE F1 (null) | held-out bits: unigram / bigram / DP lexicon / TRUE lexicon |
|---|---|---|---|---|---|
| Linear B (syllabograms) | 0.21 | **0.43** (0.31) | 0.35 (0.21) | 0.15 (0.24), fails | 5.73 / 5.34 / **5.10** / 5.53 |
| Ur III seal legends | 0.35 | **0.63** (0.41) | 0.54 (0.28) | 0.39 (0.34) | 6.76 / **4.55** / 5.12 / 5.21 |

- DP and PMI recover real word boundaries well above chance, though only moderately. DP over-segments (boundary rate 0.62 against a true 0.21 in Linear B).
- **Branching entropy fails at this corpus size, so it is not used as evidence.**
- In the genre-matched Ur III legends, a sign bigram beats even the true word lexicon on held-out text. A segmentation losing to a bigram is therefore not evidence against words. This qualifies shaunmortal F21.

**Indus (M77 dev → held-out):**

| | M77 dev → held-out | ICIT non-Dholavira → Dholavira-only |
|---|---|---|
| boundary rate DP / PMI | 0.60 / 0.22 | |
| mean DP segment length | 1.44 signs | 1.37 |
| **DP-PMI boundary F1** | **0.49 vs null 0.35 ± 0.006 (z=25)** | 0.66 vs 0.52 (z=38) |
| BE-DP / BE-PMI | z=5.9 / 1.4 | z=1.0 / 1.3 |
| top-50 multi-sign segments, Jaccard DP vs PMI | 0.52 | |
| held-out bits/sign: sign unigram | 6.84 | 7.06 |
| DP lexicon trained on **shuffled** dev | 6.94 | 7.08 |
| **DP lexicon (real)** | **6.19** | **6.97** |
| sign bigram (Kneser-Ney) | **5.83** | **6.80** |
| DP lexicon on shuffled held-out | 7.50 | 7.60 |

- **Top segments (DP, dev counts):** M267-M99 (148), M391-M99 (62), M347-M342 (55), M87-M59 (44), M342-M1 (41), M336-M89 (37), M48-M342 (37), M336-M89-M211 (33), M150-M123 (32), M245-M245 (29), M342-M176 (28), M293-M123-M343 (23), M249-M162-M342 / M249-M169-M342 (19 each), M51-M130-M149-M342 (20 on the full corpus).
- **Site stability.** Top-50 multi-sign segments, Mohenjo-daro vs Harappa, against a null that re-splits the pooled texts at the same sizes:
  - All objects: Jaccard 0.30 vs 0.46 ± 0.03 (z=-4.9).
  - **Seals only: 0.32 vs 0.31 ± 0.05 (z=+0.2).**
  - ICIT seals: 0.25 vs 0.34 ± 0.05 (z=-1.9).
  - ICIT square seals: 0.28 vs 0.33 ± 0.03 (z=-1.4).

  The all-objects difference comes from Harappa's tablets: for example, the M112-M194/M197 and M103-M403 formulae are in the Harappa-only list. Seal segment inventories are stable between the two cities; ICIT shows at most a weak difference.
- **Verdict.** There are recurring units beyond chance, and two methods agree on them. They are mostly 2-3-sign fixed pairs and formulae. They add predictive power over single signs but not over adjacency. The planted control shows that this pattern does not decide between "words" and "no words".

## 5. Text grammar (`q5_grammar.py`)

**Template** (O=opener, K=core run, C=closer, J=jar M342; clean distinct texts, n=1,758):

| Template | share |
|---|---|
| KJ | 11.4% |
| OKJ | 10.4% |
| K | 8.9% |
| KC | 8.8% |
| OKC | 6.7% |
| OK | 4.8% |
| KJC (jar followed by M1/M176-type closer) | 3.4% |
| KOKJ | 2.6% |
| OKOKJ | 2.2% |

By family: `-K C` 37%, `O K C` 32%, `-K -` 18%, `O K -` 13%.

**Typical seal text:** `[opener: M267/M391 (+M99)] [core: 1-4 signs, fish/strokes/M336-M89 ...] [closer: M342 jar, optionally + M1/M176; or M211/M169/M176 directly]`.

**Order tests:**

| Test | M77 | ICIT | Null |
|---|---|---|---|
| texts fitting `O* K C*` | **66.8%** | 66.7% | 24.8 ± 0.7% / 28.3% (within-text shuffle) |
| class precedence P(O before C), P(core before C), P(O before core) | 0.91, 0.92, 0.74 | 0.91, 0.91, 0.71 | 0.5 |
| sign pairs (co-occurring in >=10 texts): mean order consistency | 0.75 (346 pairs; 59% at >=90% one order) | 0.72 (333) | 0.20 ± 0.01 |
| **held-out permutation test:** real order vs all permutations under a dev bigram | mean percentile **0.94**; best in **63%** (415 texts) | Dholavira-only, ICIT model: 0.87; best in 46% (61) | 0.5; 5.5% (5.7%) |
| same, M77 model on bridged Dholavira-only texts | 0.89; best in 54% (54 texts) | | 8.2% |
| multisets on >=3 objects (length 2-5): mean distinct orders | **1.03** (139 multisets; 97% single order) | | 3.08 (random order per object) |

**Longest repeated substrings** (in >=2 distinct texts), vs a corpus generated by the empirical bigram with identical run lengths (5 replicates):

| length | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| observed M77 | 266 | 81 | 30 | 16 | 8 | 4 | 1 |
| bigram null | 172 ± 7 | 17 ± 4 | 0.6 | 0 | 0 | 0 | 0 |
| ICIT | 259 | 68 | 25 | 12 | 7 | 4 | 1 |

- The longest repeat is **10 signs**: M150-M123-M51-M130-M149-M342-M150-M123-M387-M342, in two texts.
- Grouped by the texts that share them, repeats of length >=6 form **15 families**. **Only 7 are not near-duplicates** of a whole text (edit distance >2), and even those are mostly "the same text plus an extra line".
- So long repeats are re-attestations of one text: the same name or title on two objects, or with an added line. They are not reused long phrases.
- At length 4-5, repeats exceed the bigram null (81 vs 17 at length 5). The texts contain more 3-5-sign formulae than adjacency alone generates.
- **Caveat.** This partly conflicts with shaunmortal F30 (block coverage = bigram), which measured coverage rather than counts of long repeats. Near-duplicate texts that `distinct()` keeps also inflate the counts.

**Verdict.** Ordering is much stricter than a bag of words, on every test, on held-out texts, in both transcriptions and at Dholavira. The grammar defensible at class level is `O? core C?`. Beyond that, the structure is fixed formulae.

## 6. ICIT and Dholavira (`q6_icit.py`; the ICIT sections of q1-q3)

- **Distinct texts.** 3,504 ICIT texts. Dholavira: 175, all of them Dholavira-only (no exact sequence is attested at another ICIT site).
- **Replications.** Direction, inventory curve, K=3 classes, DP-PMI agreement, template shares (67% conformity) and permutation tests all replicate on ICIT (tables above).
- **Cross-transcription prediction.** The M77-dev bigram was scored on ICIT texts mapped to M codes through the bridge (only runs whose every sign is bridged):
  - Non-Dholavira ICIT: 5.46 bits/sign vs unigram 6.52 vs 7.76 for shuffled.
  - Dholavira-only: 6.15 vs 6.37 vs 7.58.
- **Length-matched bigram gain** (bits/sign) over unigram:

  | | length 2 | length 3 | length 4+ |
  |---|---|---|---|
  | M77 held-out | 0.22 | 0.67 | 1.19 |
  | ICIT non-Dholavira | 0.27 | 0.84 | 1.43 |
  | Dholavira-only | -0.15 | 0.02 | 0.71 |

- **What this means.** Dholavira keeps the order skeleton: permutation percentile 0.89, and classes behave the same. But its specific sign pairings are less predictable from Mohenjo-daro and Harappa. This is consistent with a regional lexicon of names and titles.
- **Caveats.** The sample is small (89 Dholavira-only runs of length 2+). Bridge coverage selects frequent signs (132 of 195 runs survive). Choosing texts "unattested elsewhere" biases towards rarer combinations. A fair control would score site-unique texts from another site with that site held out of training. Not done yet.
- **Dholavira-only templates:** K 17, KC 11, KJ 8, OKJ 7, KO 4, OK 4.

## Hypotheses tested

| # | Hypothesis | Verdict | Key number |
|---|---|---|---|
| H1 | L-R labels are real (texts read as labelled follow the R-L grammar) | **Supported** | 89% oriented correctly (84% without the jar), p=1e-24; rho +0.66 vs mirror -0.52 |
| H2 | Jar M342 is terminal in L-R texts | **Supported** | 33 last vs 3 first (M77), 36 vs 2 (ICIT) |
| H3 | Line order of multi-line texts is recoverable from the grammar | Refuted / inconclusive | 61 vs 51, p=0.20 |
| H4 | Inventory fits an alphabet (20-40) or a syllabary (50-100) | **Refuted** | 417 types, Chao2 565, 120 signs for 90% |
| H5 | Inventory is like logo-syllabic systems at matched sample size | **Supported** (with genre caveats) | Proto-Elamite 473, Sumerian seal legends 496, Linear B 212 at 10k tokens |
| H6 | Sites differ in sign richness | Refuted | rarefied 243 vs 239 types at 2k tokens |
| H7 | Context-matched look-alikes are allographs (M12/14, M386/387/389, M216/226, M343/344/345) | Supported as probable | permutation p 0.05-0.98, visual check |
| H8 | Held-out perplexity validates allograph merges | **Refuted as a test** | context-matched non-look-alike merges do as well (p=0.67) |
| H9 | Signs have positional preferences | **Supported** | 82/124 at q<0.05 |
| H10 | More than 3 stable positional classes | Refuted | ARI 0.67 at K=3, <=0.53 at K>=4 |
| H11 | Numerals form a distributional class | Refuted (inconclusive for short strokes) | ARI <=0.34 |
| H12 | Two segmentation methods agree beyond chance | Supported (DP-PMI); BE fails the planted control | F1 0.49 vs 0.35, z=25 |
| H13 | Segment lexicon beats nulls on held-out | Supported vs unigram and shuffled; **refuted vs bigram** | 6.19 vs 6.84 / 6.94 / 5.83 bits |
| H14 | Segment inventories are stable between Mohenjo-daro and Harappa | Supported for seals; differ for all objects (tablets) | z=+0.2 (seals) vs z=-4.9 (all) |
| H15 | Order is stricter than a bag of words | **Supported** | held-out best-of-permutations 63% vs 5.5%; 97% of multisets have one order |
| H16 | Long phrases (>=6 signs) are reused across different texts | Refuted | 15 families, mostly re-attestations of the same text |
| H17 | Dholavira follows the same grammar | Supported for order and classes; its pairings are less predictable | percentile 0.89; gain 0.71 vs 1.19 bits |

**Multiplicity.** About 35 headline tests (listed above), each reported with its own null. Screening tests corrected by BH: 257 per-sign positional tests (M77 + ICIT) and 187 allograph pair permutations. Every headline p-value given as <=1e-5 survives Bonferroni over 35 tests. These do not: the K=10 stroke cluster (p=0.002 among 9 K and unstable), ICIT seal site stability (z=-1.9), and H3.

## Next experiments
1. **Absolute direction from physical data.** Code stroke-overlap and cramping from CISI photographs for a sample of seals. This is the only way to settle which end is the beginning without assuming it.
2. **Dholavira control.** For each site, hold out its site-unique texts, train on the rest, and compare bigram gain with Dholavira's. This tests whether Dholavira's lower predictability is regional or a selection effect.
3. **Allographs from palaeography.** Graded drawings across CISI photos for the variant families (fish, M267/M391, M387/M389). Test whether variant choice tracks site, period or object (scribal hands) rather than context.
4. **Phrase-level segmentation with a bigram-word model** (Goldwater bigram DP). Run it on the planted Ur III control first, then on Indus, to see whether formula units add anything beyond adjacency.
5. **Near-duplicate clustering.** Collapse texts at edit distance <=1 before counting repeats and multiplicities. This gives a cleaner test of 3-5-sign formulae beyond bigram (section 5).
6. **Bridge extension.** Map the remaining 11% of ICIT tokens so Dholavira texts can be scored without selection by bridge coverage.
