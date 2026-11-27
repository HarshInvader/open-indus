# Checking Raj (2026), "Indus Script Read as Early Dravidian, with AI Assistance" (v0.7)

2026-11-27. Preprint: [doi:10.5281/zenodo.24579269](https://doi.org/10.5281/zenodo.24579269). Plans: `PREREG.md` (sha256 0d9b3da9…96ba, commit 544309a) and `stage2/PREREG_STAGE2.md` (sha256 83609964…6ec0, commit 4895276), both hashed before the runs they cover. Source: Zenodo 10.5281/zenodo.24383779 (CC BY 4.0), every file copied to `sources/raj_zenodo_24383779_v0.7/` with md5 equal to Zenodo's. Corpus: the ICIT copy in yajnadevam/lipi @ fc8813a, sha256 equal to the one in Raj's README.

We ran Raj's own code on Raj's own data. Where we changed anything, the change is a hook saved as a diff (`code/contest_ctl.diff`).

## Summary

- **Their code is honest and reproduces exactly.** All 40 headline runs match their stored outputs to 0.01: Tamil +223 ± 103 (10 of 10 seeds above control), Sanskrit −13 ± 45.
- **The pictures do not drive the language result.** With Tamil's picture words moved onto the wrong signs at random, Tamil scores the same: median +224 over 50 permutations, p = 0.51. All 50 permuted runs score above zero.
- **The score does track real order in the seals.** On fake seals (shuffled order, or meaningless strings with the same sign frequencies) it falls to zero or below. So the contest measures how well Tamil name structure fits the repeated sign sequences. It does not measure whether the signs depict Tamil words.
- **Most Tamil readings are sound-alikes, not picture words.** In their own headline runs, 161 of 274 Tamil readings (59%) are name parts chosen for sounding like a picture word, not the picture word itself. For Sanskrit it is 52 of 178 (29%).
- **The object marks rest on copies.** The 21 copper-tablet faces with the "copper" sign carry 3 distinct texts. Counted once each, p = 0.19. The armlet sign is on 4 distinct bangle texts, p = 0.017, which fails the paper's own multiple-test line (1.1e-5). Assigning their readings to signs at random gives as many object-naming hits as the real key, p = 0.10.
- **A language with no link to the Indus gets 60% of Tamil's score.** Japanese family names, which like Tamil names are built from drawable things, score +134.5 against Tamil's +223, and beat Tamil in 4 of 10 splits. Sanskrit, which the paper rules out, scores −13. By our preregistered bar (8 of 10 seeds above control) Japanese narrowly fails (7 of 10), so the contest passes this control. But the margin is naming style, not language.
- **Three more languages (stage 3): none reaches half of Tamil's score, but all but Sanskrit beat their scrambled control.** Sumerian +103.5 (9 of 10 seeds above control), Egyptian +77.6 (7 of 10), Finnish +63.7 (10 of 10). Tamil is top in all six; beating chance is not special to Tamil.
- **Tamil's score comes from its place, hill, river, god and group names (stage 4a).** Written in plain ASCII it still scores +206, so spelling is not the cause. But with people's names only it scores +3 (4 of 10 seeds), while size-matched random subsets of the full list score a median of +178. Tamil personal names (532) fit worse than Sumerian and Egyptian personal names (1,125 each); Japanese and Finnish surnames are themselves mostly place and landscape words.

## T0. Reproduction
`out/T0/`. Every held-out value equals `outputs/headline/*` in their archive. Tamil D = +223.0 (sd 103.0), 10 of 10 above control. Sanskrit D = −13.3 (sd 44.7), 4 of 10.

## T1. Picture-permutation control
`out/T1/perm1…50/`. Before each run, the 69 picture-word lists were shuffled among the non-number signs, with each list kept whole. Statistic: mean over their seeds 0–9 of (real − scrambled names).

| | Tamil, true signs (T0) | Tamil, picture words on random signs (50 permutations) |
|---|---|---|
| D | +223.0 | median +223.7, mean +251.7, range +95.8 to +531.4 |
| Signs read, mean | 27.4 | 28.5 |

p = 0.51 (25 of 50 permutations reach +223). By the plan, this goes **against** the claim that the pictures are part of the reason Tamil fits. The share of the score due to the correct sign–picture match is −0.3%.

Why: a sign's candidates include every Tamil name part within a small sound distance of any of its picture words (same first letter, length within 3, sound cost ≤ 0.5). The solver then picks whichever candidates make recurring sign pairs look like recurring name pairs. Tamil's list gives the solver this freedom wherever the words land.

## T2. Fake-seal controls
`out/T2_order/`, `out/T2_iid/`, 20 fake corpora each.

| Seals | D (mean over 20 corpora) | Highest | Corpora with D > 0 |
|---|---|---|---|
| Real (T0) | +223.0 | | |
| Sign order shuffled inside each seal | −18.5 | +12.4 | 1 of 20 |
| Meaningless seals, same sign frequencies | −28.5 | −8.9 | 0 of 20 |

By the plan, this result **supports** the paper on one point: the score depends on the real order of signs, which no fake corpus reaches (p = 1/21 ≈ 0.048, the smallest value 20 fakes allow). Combined with T1, the score shows that Tamil names have recurring two-part patterns that can be mapped onto the recurring sign pairs of the seals. It does not show that the signs stand for those words.

## Readings: picture words or sound-alikes (descriptive)
`code/reading_origin.py`, over T0's chosen readings. Tamil: 113 literal picture words and 161 sound-alikes (41% literal). Sanskrit: 126 and 52 (71% literal). Tamil's advantage comes largely from sound-alike freedom. The paper says so itself (§15): "Our controls measure how often chance fits; they cannot remove the extra freedom."

## T3. Object marks
`out/T3_object_marks.json`. Their scan, recomputed with their rule: 296 signs × 15 object types; 101 pairs pass Bonferroni (1.1e-5). 133 read signs are in the scan, 60 of them in a passing pair.

- **Object-naming hits** (keyword rule fixed in the plan): 2 observed (840 armlet on bangles; 061 copper on copper tablets; 705 and 706 do not pass on their own). With their readings shuffled among the read signs (100,000 times): mean 0.58, 99th percentile 3, P(≥ 2) = 0.10. Not above chance by the plan's line.
- **Copies.**

| Case | Rows (as in the paper) | Distinct texts on the object | Fisher p, each distinct text once |
|---|---|---|---|
| 840 armlet, bangles | 10 of 50, p 1.5e-7 | 4 | 0.017 |
| 061 copper, copper tablets | 21 of 230, p 6.4e-11 | 3 | 0.19 |
| 705 smith, copper tablets | 20 of 230 | 4 | 0.62 |
| 706 smith, copper tablets | 14 of 230 | 3 | 0.32 |

Copper tablets were made in sets with identical inscriptions, so each set counts many times in the paper's test. Counted once per text, no case passes their multiple-test line.

## Stage 2. A wrong language whose names are built from drawable things
`stage2/`, `out/T4_japanese/`, `out/T4_japanese_perm/`. Japanese family names (shuheilocale dataset @ 793b250, MIT). The top 1,125 that keep a native part (ranks 1–1185) were run through Raj's `contest.py`, unchanged. Inputs were built by three agents using Raj's own translator and labeler prompts, with only the language changed (diffs in `stage2/PREREG_STAGE2.sha256` and the `*_ORIGINAL.txt` copies). The translator saw only the 171 English entries and filled 127 (Tamil 150, Sanskrit 125). Sino-Japanese parts were dropped as loans, as Tamil drops Sanskrit loans.

| | Old Tamil (T0) | Japanese surnames | Vedic Sanskrit (T0) |
|---|---|---|---|
| Real names minus scrambled, mean ± sd | +223 ± 103 | **+134.5 ± 195** | −13 ± 45 |
| Seeds above its own control | 10 of 10 | **7 of 10** | 4 of 10 |
| Seeds ahead of Tamil | | **4 of 10** | 0 of 10 |
| Picture options per sign | 2.52 | 2.38 | 1.1 |
| Signs read, mean | 27.4 | 27.9 | 18 |

Seed by seed, Japanese: −5, +129, +112, +359, +260, +4, −106, +429, −131, +294. Tamil: +104, +238, +158, +255, +192, +244, +185, +176, +487, +191.

**By the preregistered rule, the contest passes this control, narrowly.** Japanese clears the half-of-Tamil bar (134.5 ≥ 111.5) but is above its control in 7 of 10 seeds, one short of the 8 required. We report it as a pass for Raj.

What it does show: a language with no proposed link to the Indus gets 60% of Tamil's score and beats Tamil in 4 of 10 splits, once it has a naming style like Tamil's. Sanskrit's and Akkadian's failures in the paper are mostly about naming style (single-word names, gods and verbs), not about language. Tamil's real edge over Japanese is consistency (sd 103 against 195; 10 of 10 against 7 of 10).

Descriptive: with Japanese picture words moved onto random signs (20 permutations), D has median +114.9 (range −35 to +206), and 6 of 20 reach +134.5. As with Tamil, the sign–picture match adds little.

## Comparison with Yajnadevam (descriptive)
- **Same corpus file**: both use the ICIT copy in Yajnadevam's lipi repository. Raj's README notes it "has not yet been checked against the ICIT itself".
- **Same kind of evidence**: a key fitted to the corpus is judged by how well texts then read in the target language (Sanskrit dictionary fit for Yajnadevam; Tamil name fit for Raj). No value was fixed before the data used to test it, and neither has been tested on newly found material.
- **Same freedom problem**: our earlier tests (NEGATIVE_ATLAS 1.1; `experiments/language/RESULTS.md` A1) found that Yajnadevam's key reads random sign strings nearly as well as real texts. Here, Raj's contest scores Tamil the same with the pictures on the wrong signs.
- **Differences, to Raj's credit**: a held-out design, a scrambled control, preregistered plans, a published wrong-word rate for each confidence group, rival languages run (Sanskrit, Akkadian, Munda), and an explicit limitations section. Raj's key is logographic (a word per sign), Yajnadevam's syllabic.
- **They contradict each other**: each method crowns its own language on the same corpus. That alone shows fit-based methods do not settle the language.

## What would settle it
Values fixed before testing, then: (1) new or unpublished inscriptions read blind; (2) a blind test with Dravidianists rating readings of real texts mixed with fake ones; (3) the full pipeline run end to end on a deciphered logographic corpus and on a planted wrong language.

## Stage 3. A panel of other languages (T5)
`stage3/`, `out/T5_*`, `out/T5_summary.json`. Plan `stage3/PREREG_STAGE3.md` (sha256 in `PREREG_STAGE3.sha256`), committed before any agent ran (commits 8035ca0, 5552677). Inputs committed before any contest run (0f60d69). Names: Sumerian, the 1,600 most-attested Ur III personal names (Oracc ePSD2); Egyptian, 1,600 personal names drawn at random (seed 20261127) from the TLA lemma list of 2018; Finnish, the 1,600 commonest surnames (DVV). Nine fresh agents (translator, segmenter, labeler per language); Raj's `contest.py` unchanged.

| Language | Real names minus scrambled, mean ± sd | Seeds above control | Seeds ahead of Tamil | Picture options per sign | Signs read | Verdict (plan's rule) |
|---|---|---|---|---|---|---|
| Tamil | +223.0 ± 103 | 10 of 10 |  | 2.52 | 27.4 |  |
| Japanese | +134.5 ± 195 | 7 of 10 | 4 of 10 | 2.38 | 27.9 | partial fit |
| Sumerian | +103.5 ± 70 | 9 of 10 | 1 of 10 | 1.12 | 15.6 | partial fit |
| Egyptian | +77.6 ± 148 | 7 of 10 | 3 of 10 | 1.62 | 15.9 | no fit |
| Finnish | +63.7 ± 28 | 10 of 10 | 0 of 10 | 0.78 | 12.7 | partial fit |
| Sanskrit | -13.3 ± 45 | 4 of 10 | 0 of 10 | 1.06 | 17.8 | no fit |

Seed by seed:
- Sumerian: +54, +134, +134, +43, +89, +173, -12, +232, +112, +75
- Egyptian: +174, -33, -200, +192, +96, +77, -41, +302, +6, +202
- Finnish: +73, +119, +56, +55, +36, +44, +83, +94, +46, +30

**Panel verdict by the plan: mixed.** No new language fits like Tamil: none reaches half of Tamil's score (111.5). Sumerian comes closest (+103.5, above its control in 9 of 10 seeds). The verdict is "mixed", not "picks out Tamil", because Japanese beats Tamil in 4 of 10 seeds (the plan allowed at most 3).

What it shows:
- **For the paper:** Tamil has the highest and steadiest score of all six languages tried. No other language reaches half of it.
- **Against reading much into it:** every language with a real naming system except Sanskrit scores above its scrambled control: Sumerian in 9 of 10 seeds, Finnish in 10 of 10, Egyptian and Japanese in 7 of 10. Beating the scrambled control is what real names do on these seals, whatever the language. The size of the lead follows the number of picture options per sign more than the language (Tamil 2.52, Japanese 2.38, every other language 1.6 or fewer), and T1 shows that Tamil's lead does not depend on its pictures being on the right signs.
- A fairer contest would hold picture options per sign equal across languages. Not done here.

Limits: one translator per language, no expert check of the Sumerian and Egyptian lists; agents' notes are in `stage3/agents/`.

## Stage 4a. Tamil on equal terms (T6)
`stage4/`, `out/T6_*`. Plan `stage4/PREREG_STAGE4A.md` (sha256 in `PREREG_STAGE4A.sha256`), committed with the mechanically built inputs before any run (4306ce0).

| Run | Names | Real minus scrambled, mean ± sd | Seeds above control | Picture options per sign | Signs read |
|---|---|---|---|---|---|
| Tamil, as the paper (T0) | 1,125, every kind | +223.0 ± 103 | 10 of 10 | 2.52 | 27.4 |
| T6a Tamil in plain ASCII | 1,125, every kind | +205.8 ± 98 | 10 of 10 | 3.9 | 40.5 |
| T6b Tamil, people only | 532 | +2.9 ± 246 | 4 of 10 | 1.07 | 13.9 |
| T6c Tamil, people only, ASCII | 532 | +28.3 ± 148 | 6 of 10 | 1.86 | 21.4 |

**T6a, by the plan: spelling explains little.** Written in plain ASCII like the other languages, Tamil still scores +205.8 (the plan's line for "little" was 178.4). Stripping the marks merges letters, so Tamil gets more picture options per sign, not fewer. Our guess that the sound matcher favoured Tamil's letters was wrong.

**T6b and T6c (descriptive): Tamil's personal names alone do not fit the seals.** Raj's Tamil list is 532 people, 240 places, 98 deities, 87 groups, 37 lineages, 33 hills, 29 celestial names, 14 rivers and others. With people only, Tamil scores +2.9 (4 of 10 seeds above control).

**Exploratory, not preregistered: kind of name or list size?** Ten random subsets of 532 names from the full list (all kinds, about half people), original spelling: median +177.7, range +98.5 to +230.9, 8 or more seeds above control in 8 of 10 subsets (`stage4/size_check_4a.py`, `out/T6_size_summary.json`). None comes near +2.9. So the collapse is about the kind of name, not the size: **Tamil's score comes from its place, hill, river, god and group names.** Tamil personal names score below the Sumerian (+103.5) and Egyptian (+77.6) personal names, though those lists are twice as long. Japanese and Finnish surnames (+134.5, +63.7) are mostly place and landscape words, so they belong with Tamil's place names, not its personal names.

What it means for the paper: the paper reads the seals as names of people with titles and clans. The part of its name list that fits the seals is the place, landscape and group vocabulary, which is the most drawable. That is the naming-style effect again, inside Tamil.

## Stage 4b. Tamil's sister languages and a fresh Old Tamil list (T7)
`stage4/`, `out/T7_*`. Plan `stage4/PREREG_STAGE4B.md` (sha256 in `PREREG_STAGE4B.sha256`), committed before any 4b agent ran. Departures from the plan, all logged before any 4b run: `stage4/DEVIATIONS_4B.md` (main one: Sanskrit loans labelled by origin for every language; a sensitivity run labels them by meaning). Each language's inputs were committed before its contest ran. Raj's `contest.py` unchanged.

Checker (50 random names, 50 random picture words per language; more than 10% wrong fails):

| List | Names compiled | Names wrong | Words wrong | Checker looked up |
|---|---|---|---|---|
| Old Tamil, fresh | 1,276 | 2 of 50 | 3 of 50 | 19 of 100 items |
| Old Malayalam | 631 | 1 of 50 | 1 of 50 | about 57 of 100 |
| Old Telugu | 1,338 | 0 of 50 | 4 of 50 | 51 of 100 (names almost all from memory) |
<!--KANNADA_CHECK-->

Results (main run: loans labelled by origin and dropped):

| Run | Names used | Real minus scrambled, mean ± sd | Seeds above control | Seeds ahead of Raj's Tamil | Picture options per sign | Signs read | Sensitivity run (loans by meaning) |
|---|---|---|---|---|---|---|---|
| Raj's Old Tamil (T0) | 1,125 | +223.0 ± 103 | 10 of 10 |  | 2.52 | 27.4 |  |
| Old Tamil, fresh list | 1,125 | +4.2 ± 185 | 4 of 10 | 1 of 10 | 2.65 | 30.2 | +0.6 (6 of 10) |
| Old Malayalam | 510 | −92.1 ± 85 | 0 of 10 | 0 of 10 | 0.94 | 10.0 | −25.9 (3 of 10) |
| Old Telugu | 182 | +31.7 ± 184 | 4 of 10 | 1 of 10 | 0.20 | 1.6 | +11.1 (6 of 10) |
<!--KANNADA_ROW-->

Seed by seed (main run):
- Fresh Tamil: −143, +154, −46, +227, +326, +80, −104, −250, −138, −62
- Malayalam: −214, −5, −182, −18, −126, −31, −33, −41, −221, −52
- Telugu: −88, −77, −24, +58, +64, −17, −99, +531, −41, +9
<!--KANNADA_SEEDS-->

**Fresh Old Tamil, by the plan: "Raj's list is special"** (D ≤ 111.5). A second Old Tamil list from the same kinds of sources, checked against the Tamil Lexicon and DEDR, scores +4. The solver reads more signs with it than with Raj's list (30.2 against 27.4), so the list does not fail for want of picture options.

**Exploratory, not preregistered (run after the fresh-Tamil result was seen; `stage4/explore_4b.py`, `out/T7x_summary.json`):**

| Run | Real minus scrambled | Seeds above control | Picture options | Signs read |
|---|---|---|---|---|
| X1 fresh names + Raj's picture words | −72.5 ± 176 | 3 of 10 | 2.83 | 30.5 |
| X2 Raj's names + fresh picture words | +276.4 ± 87 | 10 of 10 | 2.49 | 27.9 |
| X3 fresh names resampled to Raj's mix (47% people; 683 names), 5 subsets | −50, +70, −1, +71, +155 | 5–8 of 10 | 1.6–2.0 | 18–25 |

The difference is in the names, not the picture words: Raj's names score high with either set of picture words, and the fresh names score near zero or below with either. Matching the mix of name types recovers part of the gap, unstably. **The +223 is a property of one particular list of 1,125 names**, built by a model in the paper's step 0 (`names_model_clean.jsonl`), not of Old Tamil names in general. The fresh list leans on Sangam poets' names from the colophons (68% people), so it is not a copy of Raj's in kind; but Raj's list is not a copy of Old Tamil either, and nothing in the paper fixes which list is the right one.

**Sister languages, by the plan:** <!--DRAVVERDICT_RESULTS-->

Limits: one compiler, translator and labeler per language. The Telugu list is mostly Sanskrit epic names, which leaves almost nothing once loans are dropped (182 names, about 2 signs read), so the Telugu run says little about Telugu. The Malayalam list is short (631 compiled, 510 used).
