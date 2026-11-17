# Red team: attacks on the project's positive claims

Red team, 2026-11-14. Every number below comes from my own code in `experiments/redteam/` (`r1`..`r8*.py`, run from this folder or the repo root with `.venv/bin/python`). The scripts read `data/*.jsonl` directly and reuse no other team's scripts. Logs are in `*.log`, numbers in `results.json`, and glyph renders in `img/`. Wells codes come from rendering the lipi font (`sources/paragorth_Indus-/tools/indus_font.ttf`, codepoint 0xE000+W; the font in field-cady is a 404 stub) and checking each against Mahadevan's drawings.

## Conclusion first

- No claim is fully broken by a data artefact. Two survive almost untouched: ticked fish move to the closer slot, and Gulf round seals break Indus order. Several headline numbers are inflated by variant copies.
- Dholavira's "regional pairings" do not survive the missing control. That claim is broken.
- Three sub-claims should be dropped:
  - "7+fish is avoided"
  - "M99 is seal-specific"
  - "jar+M176 is a rod register"
- **Project-wide artefact 1: held-out texts are variant copies of dev texts.** 251 of 554 held-out M77 texts (45%) are within edit distance 1 of a dev text. Every "held-out replication" in the project is partly a re-test on copies.
- **Project-wide artefact 2: L-R lines are copies of R-L texts.** 116 of 150 M77 L-R lines (77%) are exact or edit-distance-1 copies of an R-L line.
- **Project-wide artefact 3: ICIT is not a second sample.** About 90% of ICIT inscriptions come from the five sites M77 already covers (MD, Harappa, Lothal, Kalibangan, Chanhu-daro). Most of them are the same objects re-transcribed. "Replicates on ICIT" means "survives a different sign list and transcriber", not "replicates on new data".

| # | Claim (team) | Verdict | Key red-team numbers |
|---|---|---|---|
| 1 | Bracketed fish move to text end (novel_methods) | **Survives (strengthened)** | Native Wells: 40/73 final vs 0.26 by chance (p=1e-7). 5/5 base→ticked pairs shift individually. Jar in 14% of their texts vs 48% matched. New sites only: 5/10 (p=0.07) |
| 2 | Two-tier six + fish is a fixed pair; 7+fish refuted (language) | **6+fish survives; "7 avoided" weakened** | M109+M59 12/25 (10 families, 3 sites); W016+W220 13/33 (11 families, 4 sites). Sevens on seals 1/50, p=0.07, like 1, 5 and 12 |
| 3 | Object-type registers; M99 seal-specific; jar+M176 tablet/rod (context) | **Registers survive; M99-seal and rod markers weakened** | Grouped-CV AUC 0.62-0.89. M99 on seals at family level 1.04-1.08x (p 0.07-0.23). Rod jar+M176 = 4-6 legends, all at Mohenjo-daro |
| 4 | Gulf round seals anomalous (context) | **Survives** | Permutation percentile 0.53 vs 0.87-1.00 for every peripheral site with the site held out. Robust to 5 smoothing variants. Not a direction error |
| 5 | Strict order; 63% beat all permutations (structure) | **Survives, magnitude inflated** | Without leaked copies: 42% (chance 3%). Removing jar/M176/M267/M391/M99: 42% (chance 9%). Texts with none of them: 33% (chance 8%) |
| 6 | Copper tablets: same text, same picture (context) | **Survives at legend level; interpretation over-read** | 18 legends, not 272 pairs; 82% of pairs come from 3 legends. Modal picture share 0.90 vs 0.39 (p=2e-4) |
| 7 | Dholavira pairings less predictable (structure) | **Broken (as regional)** | Site-held-out, equal training size, 4+ signs: Dholavira 0.84 bits, Kalibangan 0.83, Chanhu-daro 0.78, Lothal 1.08, MD 1.20, Harappa 1.22 |
| 8 | Reading direction: L-R labels real (structure) | **Survives on a much smaller base** | Clean (non-copy) lines: M77 31/34; with the top 20 positional signs removed 25/33 (p=0.002). ICIT 15/22 (p=0.07) |

## 1. Bracketed fish → text-final (`r1_fish.py`, `r1b_fish_newsites.py`)

**What the code does.** `novel_methods/exp3_sign_morphology.py` T6 pools 5 derived signs. It compares their final share with one frequency-matched random sign per derived sign. The fish subset was split off *after* a dev screen of 5 families × 5 statistics, where the whole enclosure family showed a final shift (p=0.039). The held-out confirmation is p=0.032, or 0.10 after their own Bonferroni. This is a classic forking path, so a native, out-of-transcription test was needed.

**What the "brackets" are.** The renders show they are four corner ticks, not an enclosure (`img/m_fish.png`, `img/wells_fish.png`). Wells keeps each ticked fish as its own sign:

| Mahadevan | Wells | Base sign |
|---|---|---|
| M60 | W226 | W220 / M59 |
| M71 | W232 | W231 |
| M73 | W234 | W233 |
| M66 | W236 | W235 |
| M68 | W241 | W240 |

W237 is a ticked hatched fish with 0 tokens in usable texts. Parenthesis-enclosed fish (W221-W225) are a different family. The team's non-fish "enclosure" null, together with this, means the effect is specific to **ticks on fish**. It is not a general enclosure modifier.

**Native ICIT** (2,395 distinct break-free texts of 2+ signs, no bridge):
- **Pooled.** Ticked fish are final 40/73 = 0.55. A within-text shuffle expects 0.26 (binomial p=1.1e-7). Bases are final 45/843 = 0.05.
- **Frequency-matched null** (their design, my code): 0.19 ± 0.13, p=0.018. This null is weak because 5 random signs vary a lot. The shuffle and Fisher tests are sharper.
- **Per pair** (they only pooled). Each ticked form is more often final than its base:

  | Pair | Ticked final | Base final | Fisher p |
  |---|---|---|---|
  | W220→W226 | 18/31 | 19/265 | 5e-11 |
  | W231→W232 | 3/8 | 3/66 | 0.015 |
  | W233→W234 | 3/5 | 8/141 | 0.003 |
  | W235→W236 | 7/18 | 5/158 | 2e-5 |
  | W240→W241 | 9/11 | 10/213 | 1e-9 |

- **The "tall-2 + W226" formula is not the driver.** Without W226: 22/42 = 0.52, p=1.2e-4.
- **Collapsing near-duplicate families** (edit distance ≤1): 60 families, mean final 0.57.
- **Seals only:** 34/56 = 0.61.
- **Closer-slot competition.** Texts containing a ticked fish carry the jar W740 in 13.7% of cases, against 48.1% in length-matched texts (p=5e-4). Only 2 of 49 texts ending in a ticked fish (or ticked fish + W400) contain the jar. So the ticked fish fills the closer slot, as the team predicted.
- **M77 recount:** 32/56 = 0.57 (bases 0.06). The per-pair direction is the same.

**Limits.**
- ICIT mostly re-transcribes the same Mohenjo-daro and Harappa seals. Sites absent from M77 give only 10 tokens: 5 final, p=0.07, from 7 sites.
- This rules out a Mahadevan sign-list artefact and a single-formula artefact. It is not yet a replication on new objects.
- What remains untested is CISI photo verification that the ticks are not field or edge marks.

**Verdict: survives.** It is the best "sign-internal" finding in the project.

## 2. Two-tier six + fish; 7+fish (`r2_sixfish.py`)

**6+fish.**
- **M77:** M109 is followed by M59 in 12 of 25 numeral-run tokens (0.48), against a base of 0.06 (p=9e-9). The 12 texts form 10 near-duplicate families at 3 sites (MD 6, Harappa 5, Chanhu-daro 1). Seals only: 9/20.
- **Native ICIT:** W016 (3-over-3) is followed by W220 in 13 of 33 (p=4e-9). That is 11 families at 4 sites, including Nausharo, which is absent from M77.
- **Verdict: survives** as a fixed pair. Nothing shows it means "six" or "Pleiades".

**One-row six never takes fish.**
- This rests on n=3 (M108). In ICIT, W006 takes fish 1/4.
- **Verdict: drop the statement.**

**7+fish.**
- **All objects:** 1/60 in M77. Depletion p=0.017 against my base rate of 0.096. The team's base was 13% and their p 0.0025; the base depends on which numerals are pooled.
- **Seals only:** 1/50, p=0.07. ICIT seals: 1/45, p=0.07.
- **Other numerals on seals take fish just as rarely:**
  - M97 (1 short stroke) 1/66
  - M98 0/55
  - M106 (5) 0/17
  - M121 (12) 0/34
  - M104 (4) 3/34
- Six (9/20) and three (12/75) are the exceptions. Seven is the norm.
- **Verdict:** "7+fish is not enriched" survives, so Parpola's P1b fails. "7+fish is avoided" is **weakened**: it is an object-type and base-rate effect, not a specific avoidance.

## 3. Object-type registers (`r3_registers.py`, `r3b_register_cv.py`)

**What the code does.** `context/q2_registers.py` deduplicates on (type, exact sequence including `|` and `#`). Broken or line-split copies of one legend therefore count as separate texts.
- Copper: 65 units collapse to 38 near-duplicate families.
- M77 tablets: 177 → 61.
- ICIT tablets: 854 → 260.

I recomputed observed and expected counts within site × length strata, at unit and at family level. I used a Poisson tail, which is more conservative than their exact hypergeometric.

| Marker | Units obs/exp | Families obs/exp | Families p | Sites (families) |
|---|---|---|---|---|
| M99 on seals (M77) | 480 / 436 | 392 / 364 (1.08x) | 0.07 | 6 sites |
| W002 on seals (ICIT) | 584 / 537 | 449 / 434 (1.04x) | **0.23** | 21 |
| M99 on copper (M77) | 2 / 12.8 | 2 / 9.3 | 0.005 (depleted) | MD |
| W002 on ICIT tablets | 55 / 92 | 39 / 52 | 0.04 (depleted) | 5 |
| M342-M176 on rods (M77) | 9 / 0.5 | **6** / 0.34 | 1e-6 | **MD only** |
| W740-W400 on rods (ICIT) | 7 / 0.9 | **4** / 0.5 | 0.001 | **MD only** |
| W740-W400 on ICIT tablets | 100 / 59 | 27 / 10.4 | 1e-5 | Harappa 21 of 27 |
| W407 on copper (ICIT) | 18 / 2.7 | 14 / 1.5 | 1e-9 | MD only (as all copper) |

**M99 is mostly a property of the openers.**
- About half of all M99 tokens directly follow an opener (M77: 234 of 455).
- Copper legends almost never have an opener: 1 of 38 families.
- On ICIT tablets, M99 appears in 49% of texts that have an opener, against 53% on seals. Its tablet depletion comes from tablets lacking openers.
- **Verdict:** "M99 is a personal-seal element" is **weakened**. What survives is "the opener+M99 formula is rare on copper and tablets". Seal *enrichment* is at null once copies are merged.

**Rods.** The jar+M176 rod register rests on 4-6 legends from one site. **Weak.**

**Tablet jar+W400.**
- It survives, but it is a Harappa-tablet formula.
- Site, workshop and object function cannot be separated. The team says this too.

**Classifier.** Whole-text AUC with families never split across CV folds drops only slightly:

| Type | Plain CV | Grouped CV |
|---|---|---|
| M77 copper | 0.91 | 0.89 |
| ICIT copper | 0.89 | 0.81 |
| M77 tablet | 0.84 | 0.82 |
| ICIT sealing | 0.68 | 0.62 |

So **"object types have different registers" survives**.

## 4. Gulf round seals (`r4_gulf.py`)

**What the code does.** `context/q4_gulf.py`:
- removes `#` and **joins the pieces of broken texts**, creating bigrams that were never written;
- scores native texts by plain 10-fold CV, so a native text's variant copies sit in its training fold, while foreign texts never get that advantage;
- maps hapaxes to UNK.

**My version.**
- Break-free texts only. That leaves **12** foreign round/cylinder texts of 2+ signs, not 18.
- Every native comparison group is scored by a model trained with **its whole site held out**, which is the foreign texts' situation.
- Five smoothing variants: KN d=0.5/0.75/0.9; rare signs (<3) collapsed to UNK; add-k interpolation.
- A smoothing-free order test: each text's percentile of the real order among all its permutations.

| Group (site-held-out, KN 0.75) | n | perm. percentile | bigram gain | reversed − real bits |
|---|---|---|---|---|
| **Foreign round** | 12 | **0.53** | **−0.49** | **−0.03** |
| Foreign square/other | 9 | 0.94 | +1.04 | +2.34 |
| Dholavira | 70 | 0.87 | +0.89 | +2.50 |
| Kalibangan | 39 | 0.90 | +0.98 | +2.46 |
| Chanhu-daro | 44 | 0.93 | +0.98 | +2.58 |
| Lothal | 56 | 0.92 | +1.22 | +2.89 |
| Nausharo | 15 | 0.97 | +1.39 | +3.13 |
| Banawali | 10 | 1.00 | +1.17 | +3.08 |
| Home round, MD (MD held out) | 149 | 0.93 | +1.09 | +2.50 |
| Home round, Harappa (held out) | 70 | 0.92 | +1.25 | +2.81 |

- **Matched-n resampling.** I drew 12 seals from one peripheral site at a time, with lengths matched to the foreign set. The 5th percentile of the permutation percentile is ≥0.75 at every site; foreign round seals sit at 0.53. Bigram gain stays negative for foreign round seals under every smoothing (−0.02 to −0.74), and every native group stays ≥ +0.56.
- **Not a direction error.** Reading the foreign texts backwards does not help (−0.03 bits); native texts pay +2.3 to +3.1 bits when reversed.
- **Not rare-sign smoothing, not a small-site effect, not format.** Home round seals behave normally.

**Verdict: survives**, on 12 texts from 7 sites. Required corrections:
- Restate n (12 clean texts).
- Recompute the context CI without splicing across breaks.
- The M77 "West Asian" replication is the same objects.
- Untested alternative: Gulf-type seals are late (about 2000 BCE), and no team compared them with *late* home seals. ICIT Harappa 3C/4-5 has too few seals to do it here.

The interpretation (foreign language vs pseudo-script) stays open.

## 5. Order and grammar (`r5_grammar.py`, `r5b_multisets.py`)

Own KN bigram, same split file. The baseline reproduces the claim at a slightly lower level: 56.5% of held-out texts have the real order best of all permutations (chance 11.5% counting length-2 texts). The team's 63% vs 5.5% likely uses a different chance computation.

| Condition | n | best order | chance | mean percentile |
|---|---|---|---|---|
| All held-out | 520 | 0.565 | 0.115 | 0.91 |
| **Held-out without an edit-1 neighbour in dev** | 303 | **0.416** | 0.034 | 0.93 |
| Same, jar/M176/M267/M391/M99 deleted (train+test) | 300 | 0.417 | 0.086 | 0.87 |
| Same, 11 most positional signs deleted | 295 | 0.420 | 0.111 | 0.87 |
| Texts containing none of the 5 fixed signs | 87 | 0.333 | 0.084 | 0.84 |
| Interior only (first and last sign dropped, length 4+) | 268 | 0.500 | 0.148 | 0.86 |
| **Position-only model** (no adjacency), no-leak texts | 303 | 0.046 | 0.034 | 0.82 |

**Readings.**
- **The order is not produced by 2-3 fixed positional signs.** Deleting them leaves the best-order share unchanged. The interior of texts is also ordered.
- **Leakage inflates the magnitude.** 45% of held-out texts have a dev copy.
- **Position alone explains most of the percentile, but not the best-order share.** Pure positional preference gives a mean percentile of 0.82 and almost no best-order texts. Adjacency carries the rest.
- **The `O* K C*` template test (67% vs 25%) is circular.** The classes are defined by positional profiles, and the within-text shuffle destroys exactly those profiles. It shows positional preference, not grammar. Do not cite it as independent evidence.
- **"97% of multisets on 3+ objects have one order" counts objects, i.e. copies.** The 140 multisets average 6.7 objects each. Restated on distinct texts, the fact is stronger and clean: among 1,505 distinct texts of 2-5 signs, only 8 multisets ever occur in two orders.

**Verdict: survives.** Quote 42% (chance 3%) on non-copy texts.

## 6. Copper tablets (`r6_copper.py`)

The 272 identical-text pairs come from **18 legends**. Tablets per legend:
- 19
- 9
- 6
- 5
- 4 (two legends)
- 3 (eight legends)
- 2 (four legends)

The three largest legends supply 82% of the pairs.

**Legend-level test.** Measure: the mean share of a legend's tablets that carry its modal picture, with pictures permuted among tablets as the null.
- Result: 0.90 vs 0.39 (p=2e-4). All copies share one fs80 picture in 13 of 18 legends.
- The pair-level 0.62 *understates* the binding. The largest legend (M204-M245-M358-M342) is split 12/7 between fs147 and fs145, which look like two codes for one picture type.

**Verdict: survives as "copper tablets come in about 18 fixed text+picture types"** (Mohenjo-daro only).
- "The legend names the picture" is one reading. "Each tablet type is a fixed design struck in batches" predicts the same data.
- Do not present it as evidence for labels or semantics.

## 7. Dholavira (`r7_dholavira.py`)

This is the control the structure team listed but did not run.
- Native ICIT. For each site, the model is trained on all other sites, subsampled to 1,800 texts (5 replicates).
- Test texts: that site's texts unattested at any other site.
- Statistic: bigram gain over unigram, in bits/sign.

| Site (site-unique texts) | 4+ signs, all objects | 4+ signs, seals | n (4+) |
|---|---|---|---|
| Dholavira | **0.84** | 0.97 | 48 |
| Kalibangan | 0.83 | 0.89 | 28 |
| Chanhu-daro | 0.78 | 0.81 | 31 |
| Lothal | 1.08 | 1.09 | 43 |
| Mohenjo-daro | 1.20 | 1.23 | 803 |
| Harappa | 1.22 | 1.41 | 399 |

Dholavira is indistinguishable from Kalibangan and Chanhu-daro. The team's 0.71 vs 1.19 compared site-unique texts from an unseen site with random held-out texts from the training sites, which have copies in training.

**Verdict: broken** as a Dholavira-specific regional claim.
- What remains: every non-core site is somewhat less predictable than MD/Harappa. The training pool is dominated by those two cities, so this is as much "MD and Harappa share formulae" as regional variation.

## 8. Reading direction (`r8_direction.py`)

The labelled direction agrees with the grammar on the full set:
- M77: 135/150.
- With the 40 most positional signs deleted: 63/74 (85%).

**Copies dominate the set.** 60 of the 150 M77 L-R lines are exact copies of an R-L line, and 56 more are at edit distance 1. In ICIT the figure is 126 of 149. Most are probably sealings and tablets whose texts also occur on seals.

**Copy-free lines:**

| Lines | All signs | Top 20 positional signs + jar removed |
|---|---|---|
| M77 | 31/34 (p=4e-7) | 25/33 (p=0.002) |
| ICIT | 18/23 (p=0.005) | 15/22 (p=0.07) |

**Verdict: survives, but quote it on about 34 independent lines**, not 150 with p=1e-24.
- The copies are themselves evidence: a mirrored copy, read as labelled, has the same order as the R-L text. But a transcriber could have set the direction by matching the copy to a known seal, so they cannot count as independent tests.
- ICIT agreement is not independent of M77.
- No test in the project bears on *absolute* direction. The team says so correctly.

## Planted-answer controls: which mislead

| Control | Problem | Effect on the claim |
|---|---|---|
| novel_methods exp3b: relabel 8% of a sign's tokens as a "planted allograph" (45/45 detected) | **Too easy.** The planted variant has identical contexts by construction. Real allographs differ by site, scribe and period, and so pick up context differences. | "M343-M345 are not allographs of the jar" over-relies on this power figure. The positional opposition (jar final, M343-345 medial/initial) is the real evidence |
| context Q4: shuffled order (0.99) and full frequency substitution (1.00) | **Too easy.** Neither plants the realistic confounds: grammatical texts in a rare genre, reversed direction, late-period texts | My site-held-out, reversal and smoothing tests fill the first two; the late-period confound is open |
| novel_methods exp2: synthetic slot code (disjoint Zipf vocabularies, no dependencies) and English-name "legends" | **Strawman comparators.** "Indus is not a slot code" means "not this slot code" | Treat exp2 as descriptive |
| phonetic_grid: synthetic suffixing language (ARI 0.86) | Too easy, but the team also ran real Linear B (0.13) and said the Indus negative is only moderately informative | Honest; no change |
| language B3: real Latin and Linear B under the classifier | **Good design.** It is what exposed the classifier | The model for all other teams |
| language A1: planted Sanskrit key | Good: the true key scores below noise-fitted keys | Kills the scoring method, correctly |
| structure q4c: Linear B and Ur III segmentation | Good, real corpora at matched size | No change |
| context Q1 (animal), structure q1 (direction), context q2b (copper), structure q6 (Dholavira) | **No planted control or selection control at all** | Q1's null cannot be sized. Direction needed a leakage control (§8). Dholavira needed the site control (§7) |
| Every team using `dev_heldout()` | The split is by distinct sequence, not by near-duplicate family, so 45% of held-out texts have a dev copy | All held-out numbers are optimistic. Re-split by family (edit distance ≤1, plus containment) |

## Garden of forking paths

Approximate counts from each RESULTS.md and the code (scripts / reported tests):

| Team | Scripts | Tests (approximate) |
|---|---|---|
| structure | 12 | about 35 headline + 444 corrected screening tests |
| novel_methods | 7 | about 100: 4 methods run of 16 listed; exp3 alone is 25 dev statistics + 6 confirmation tests |
| context | 9 | about 12,300: 11,232 enrichment tests, 835 multi-site, 161 chronology, about 70 others |
| language | 11 | 26 formal + about 15 simulation and classifier configurations, 2 random-stream reruns |
| phonetic_grid | 6 | 24 setting combinations + 3 sweeps |

- In total, about 13,000 tests behind about 60 headline claims. Corrections are made within teams, never across the project.
- **Claims that came out of a screen and have only one nominal confirmation:**
  - enclosed fish (now confirmed natively, §1)
  - 3+fish (failed held-out)
  - roof modifier (p=0.024/0.05)
  - goat-antelope short legends (q=0.024, n=13)
  - Kalibangan early/late classifier (p=0.03)
- **Re-runs that changed the answer:** language B3 swapped NONLING ↔ IA between random streams. The team reported this honestly.

## What the project can defend publicly (ranked)

1. **Order is strongly constrained beyond position.** On held-out texts with no dev copy, the real order beats all permutations in 42% of cases (chance 3%). This is unchanged when the jar, M176, M267, M391 and M99 are deleted. Among 1,505 distinct short texts, only 8 sign multisets occur in two orders.
2. **Ticked fish (M60/66/68/71/73 = W226/236/241/232/234) take the closer slot.**
   - 55-61% final vs 5% for their bases, with 5/5 pairs shifting in the Wells list.
   - They avoid the jar (14% vs 48%).
   - Caveat: same objects in both sign lists; 5/10 at new sites.
3. **Gulf round-seal legends do not follow Indus order.** Permutation percentile 0.53 vs ≥0.87 at every Indus site, robust to smoothing, held-out site and reversal. n=12; interpretation open.
4. **Two-tier six + plain fish is a fixed pair.** 40-48% vs 5-6%; 10-11 families at 3-4 sites. Meaning untested.
5. **Object types have distinct registers.** Grouped-CV AUC 0.62-0.89. The copper legend formula (W407/W845; 14 families) and the Harappa tablet ending W740-W400 (27 families) are site-bound.
6. **L-R labelled texts are genuine reversals**, with the grammar unchanged. Only about 34 copy-free lines; p=0.002 after deleting positional cues.
7. **Copper tablets come in about 18 fixed text+picture types** (0.90 vs 0.39). This says nothing about semantics.

**Do not defend:**
- Dholavira regional pairings
- 7+fish "avoided"
- one-row six never takes fish (n=3)
- M99 as a seal-specific element
- jar+M176 as a rod register (4-6 legends, one site)
- "the legend names the picture"
- the 67%-vs-25% template test
- the 63% / p=1e-24 / "97% of multisets" magnitudes as stated

## Next experiments
1. Re-split dev/held-out by near-duplicate family and rerun every team's held-out test.
2. Verify the ticked-fish ticks on CISI photographs, and pre-register the closer-slot prediction for new finds (CISI 3.x, Rakhigarhi, HARP).
3. Gulf: compare with *late* home seals once phase data allow, and recompute context's CI on break-free texts.
4. Fit a cross-project multiple-comparison ledger (one file listing every test run), so that a public claim states its true family size.
