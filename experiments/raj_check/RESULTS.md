# Checking Raj (2026), "Indus Script Read as Early Dravidian, with AI Assistance" (v0.7)

2026-11-27. Plans: `PREREG.md` (sha256 0d9b3da9…96ba, commit 544309a) and `stage2/PREREG_STAGE2.md` (sha256 83609964…6ec0, commit 4895276), both hashed before the runs they cover. Source: Zenodo 10.5281/zenodo.24383779 (CC BY 4.0), every file copied to `sources/raj_zenodo_24383779_v0.7/` with md5 equal to Zenodo's. Corpus: the ICIT copy in yajnadevam/lipi @ fc8813a, sha256 equal to the one in Raj's README.

We ran Raj's own code on Raj's own data. Where we changed anything, the change is a hook saved as a diff (`code/contest_ctl.diff`).

## Summary

- **Their code is honest and reproduces exactly.** All 40 headline runs match their stored outputs to 0.01: Tamil +223 ± 103 (10 of 10 seeds above control), Sanskrit −13 ± 45.
- **The pictures do not drive the language result.** With Tamil's picture words moved onto the wrong signs at random, Tamil scores the same: median +224 over 50 permutations, p = 0.51. All 50 permuted runs score above zero.
- **The score does track real order in the seals.** On fake seals (shuffled order, or meaningless strings with the same sign frequencies) it falls to zero or below. So the contest measures how well Tamil name structure fits the repeated sign sequences. It does not measure whether the signs depict Tamil words.
- **Most Tamil readings are sound-alikes, not picture words.** In their own headline runs, 161 of 274 Tamil readings (59%) are name parts chosen for sounding like a picture word, not the picture word itself. For Sanskrit it is 52 of 178 (29%).
- **The object marks rest on copies.** The 21 copper-tablet faces with the "copper" sign carry 3 distinct texts. Counted once each, p = 0.19. The armlet sign is on 4 distinct bangle texts, p = 0.017, which fails the paper's own multiple-test line (1.1e-5). Assigning their readings to signs at random gives as many object-naming hits as the real key, p = 0.10.
- **A language with no link to the Indus gets 60% of Tamil's score.** Japanese family names, which like Tamil names are built from drawable things, score +134.5 against Tamil's +223, and beat Tamil in 4 of 10 splits. Sanskrit, which the paper rules out, scores −13. By our preregistered bar (8 of 10 seeds above control) Japanese narrowly fails (7 of 10), so the contest passes this control. But the margin is naming style, not language.

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
