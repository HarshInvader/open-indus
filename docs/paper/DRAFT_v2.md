# Measuring the Indus corpus before testing it: edition disagreement, near-copy leakage and detection limits

Second draft, for Digital Scholarship in the Humanities or the Journal of Quantitative Linguistics. Not submitted. Replaces the broader audit draft (`AUDIT_DRAFT.md`) with the three results that are new. Each number carries a comment naming the file it comes from, and `scripts/audit_paper_numbers.py docs/paper/DRAFT_v2.md` checks them. Author names are left out of the repository copy.

## Abstract

Statistical and machine-learning work on the Indus script rests on a corpus of 2,270 distinct short texts. <!-- src: data/splits_v2.json --> Three properties of this corpus decide what such work can show, and none has been measured before. First, the editions disagree. We matched 469 objects across the two standard transcriptions through the 1930s excavation registers, not through their signs, and found that the editions read 12.9% of signs differently (95% CI 11.1-14.9%; 14.0% when our mapping fixes are fitted and measured on separate halves). <!-- src: experiments/consensus_corpus/RESULTS.md; experiments/redteam_consensus/RESULTS.md --> Second, random splits leak. Moulded tablets and fixed formulae put near-copies of a text on different objects, so a random split by object leaves a near-copy of 36% of test texts in training (median of 200 splits, 95% range 31-41%). <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> Retraining a public sign-restoration model without those near-copies lowers its accuracy by 6-7 points, and on a split by text family its transformer no longer beats a trigram. <!-- src: experiments/bench_restoration/RESULTS.md --> Third, many questions are below the corpus's detection limit. With planted answers we show that a genre difference must exceed 0.57 bits per text to be found, that a relational reading of a joining sign needs about four times more texts, and that a widely used sign-order test passes on four of seven non-linguistic codes. <!-- src: docs/NEGATIVE_ATLAS.md; experiments/audit_followups/RESULTS.md --> We release a split by text family, a concordance between the two sign lists and the code to rebuild both.

## 1. Introduction

The Indus script was used in the Indus Valley in the third millennium BCE. No bilingual text is known and the language is unidentified. Since the 1960s the script has been studied statistically, from the concordances of Mahadevan and of Parpola's group to entropy arguments about whether it writes language (Rao et al. 2009; Sproat 2014) and n-gram models of its sign sequences (Yadav et al. 2010). Neural models are now being trained on it, as on other ancient corpora (Assael et al. 2022; Sommerschield et al. 2023).

All of this work treats the transcribed corpus as fixed and its texts as independent. Neither is true, and the size of each problem has not been measured. This paper measures three things that any quantitative claim about the script depends on:

1. **How far the two standard editions agree** (Section 3). If they disagree often, every result carries a reading error that is rarely reported.
2. **How much random splits leak** (Section 4). If test texts have near-copies in training, held-out scores measure memory. Leakage of this kind is a known cause of irreproducible results in machine-learning science (Kapoor and Narayanan 2023) and in NLP benchmarks (Lewis et al. 2021; Søgaard et al. 2021). It has not been measured for the Indus corpus.
3. **What the corpus can detect at all** (Section 5). A null result is uninformative without the power of the test (Button et al. 2013). We plant known answers in texts of Indus size and record what the tests recover.

We make no claim about what the signs mean, about their sounds or about a language. The results concern the corpus as a measuring instrument. We made two of the errors we describe ourselves, and say where.

## 2. Data

**Editions.** We use two transcriptions. Mahadevan's 1977 concordance (M77) has 3,573 lines, 13,372 sign tokens and 417 signs, and our digital copy matches his published totals. <!-- src: README.md --> The Interactive Corpus of Indus Texts of Wells and Fuls (ICIT) has 5,679 inscriptions in reading order. <!-- src: README.md --> About 90% of ICIT comes from sites M77 already covers, so ICIT is mostly a second reading of the same objects, not new data. <!-- src: README.md -->

**Distinct texts.** Moulded tablets repeat one text many times. We count distinct sign sequences: M77 has 2,270, which fall into 1,477 near-copy families (Section 4.1). <!-- src: data/splits_v2.json -->

**Pre-registration.** Every confirmatory test in this paper was written up before it was run, naming the statistic, the null, the pass bar and the minimum sample. The write-up and the scripts were hashed into a public file before any outcome was computed. Each claim was then attacked by a separate analyst who wrote their own code without reading the original. Sections 3.3 and 4.3 report those attacks.

## 3. How far the editions agree

### 3.1 Matching objects without using their signs

Comparing two editions needs pairs of readings known to be the same object. Matching texts by their signs would favour pairs that already agree. We instead linked 469 objects through the excavation registers of Mohenjo-daro, Harappa and Chanhu-daro (Mackay 1938; Vats 1940; Mackay 1943), by serial and field number: 342 seals, 81 tablets and 46 sealings. <!-- src: experiments/consensus_corpus/RESULTS.md -->

Comparing readings also needs a mapping between the two sign lists. We built it from the 395 matched objects whose two readings have the same length, where the sign at each position can be compared with no mapping at all. <!-- src: experiments/consensus_corpus/RESULTS.md --> Our first mapping had errors. The five plain fish signs were cross-wired, one sign was unmapped, and Mahadevan's habit of writing some signs twice where Wells has a single "double" sign had been counted as a substitution plus a missing sign. <!-- src: experiments/consensus_corpus/RESULTS.md --> These errors had inflated the disagreement rate to 19.4%. <!-- src: experiments/consensus_corpus/RESULTS.md --> We report this because other sign-list concordances are likely to have similar errors, and because they change the result by a third.

### 3.2 Result

After correction, the editions disagree on 12.9% of compared signs (95% CI 11.1-14.9%). <!-- src: experiments/consensus_corpus/RESULTS.md --> Table 1 splits this by kind. <!-- src: experiments/consensus_corpus/RESULTS.md -->

**Table 1.** Disagreement between M77 and ICIT on 469 register-matched objects, per compared sign (text bootstrap). <!-- src: experiments/consensus_corpus/RESULTS.md -->

| kind | rate (95% CI) |
|---|---|
| different sign | 7.3% (6.1-8.6) |
| sign present in one edition only | 5.0% (3.8-6.3) |
| adjacent signs in swapped order | 0.6% (0.3-1.0) |
| all kinds | 12.9% (11.1-14.9) |
| texts with any difference | 34.5% (30.3-38.8) |
| texts read in opposite directions | 2.1% (0.9-3.4) | <!-- src: experiments/consensus_corpus/RESULTS.md -->

So about one text in three is read differently somewhere by the two editors. <!-- src: experiments/consensus_corpus/RESULTS.md --> Three patterns stand out. Signs that only M77 has lean toward the start of the text: per position, 6.4% of initial signs against 3.4% of final and 2.8% of medial ones. <!-- src: experiments/consensus_corpus/RESULTS.md --> Disagreement is uneven by site and object type: Harappa objects 17.5% against Mohenjo-daro 10.8%, and sealings 24% against tablets 18% and seals 11%. <!-- src: experiments/redteam_consensus/RESULTS.md --> And 9 of the 12 order swaps involve one sign, M328, all on Harappa objects. <!-- src: experiments/consensus_corpus/RESULTS.md --> Apart from this, there is no dominant error: the 20 most frequent disagreeing pairs cover only 24% of disagreements. <!-- src: experiments/consensus_corpus/RESULTS.md -->

### 3.3 Checks

**Fitting.** The mapping fixes were derived from the same objects they are measured on. A separate analyst re-derived the fixes on half the objects and measured on the other half, over 200 random halvings. The out-of-sample rate is 14.0% (range 12.2-16.0%). <!-- src: experiments/redteam_consensus/RESULTS.md --> So fitting lowers the figure by about one point, and "about 13%, 14% out-of-sample" is the honest statement. <!-- src: experiments/redteam_consensus/RESULTS.md -->

**The fish pairing.** Of all 120 ways of pairing the five plain fish signs between the two lists, the corrected pairing gives the lowest disagreement (12.6%), the next best gives 14.2% and the old pairing ranks 28th. <!-- src: experiments/redteam_consensus/RESULTS.md --> The pairing is decided by large counts: for example 37 of 38 and 22 of 23 same-position matches. <!-- src: experiments/redteam_consensus/RESULTS.md -->

**Alignment method.** Across alignment costs and methods the rate ranges from 10.5% to 13.2%. <!-- src: experiments/redteam_consensus/RESULTS.md --> What matters more is the cut that rejects register links whose readings are too far apart to be the same object. Random pairs fall under the cut 11.6% of the time, so it is needed; keeping every register link gives 28%, which is mostly linking errors. <!-- src: experiments/redteam_consensus/RESULTS.md -->

**Beyond the register sample.** On 2,741 further M77 texts linked to ICIT by their signs, the rate is 11.0%. <!-- src: experiments/consensus_corpus/RESULTS.md --> This is a floor, because linking by signs keeps pairs that agree: among register pairs, those that sign-linking would have admitted disagree on 8.6% of signs and those it would have missed on 67%. <!-- src: experiments/redteam_consensus/RESULTS.md -->

### 3.4 What it means for analyses

The matched sample is the best-documented part of the corpus, so disagreement elsewhere is unlikely to be lower. Errors that both editors share cannot be seen this way, because ICIT drew on M77 and on the same photographs. <!-- src: README.md -->

A rate of 13% matters most for findings that rest on rare signs or exact sequences. We re-ran nine published structural findings on the signs both editions agree on, on the ICIT readings, and under noise that copies the measured pattern of disagreement (which signs are confused with which, where deletions fall, how often texts are reversed). <!-- src: experiments/consensus_corpus/RESULTS.md --> All nine pass at the measured rate. The thinnest, that recurring sign pairs keep one order, passes in only 3 of 5 runs when the noise is aimed at rare signs. <!-- src: experiments/redteam_consensus/RESULTS.md --> A finding about reading direction cannot be checked at all: only 8 left-to-right lines carry the same label and the same signs in both editions. <!-- src: experiments/consensus_corpus/RESULTS.md --> We recommend that quantitative work on the script report results on both editions, or under measured noise, and state which edition it uses.

## 4. How much random splits leak

### 4.1 Near-copy families

Many Indus texts recur on several objects with small differences: a moulded tablet series, or a seal formula with one sign changed. We join two distinct texts into one family if they are within one sign edit of each other, or if one contains the other (for texts of three signs or more). <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> The 2,270 distinct M77 texts form 1,477 families. <!-- src: data/splits_v2.json -->

### 4.2 Leakage under random splits

We drew 200 random splits of M77 by object, as is standard, and counted the test texts with a near-copy in training. The median is 36.0%, with a 95% range of 31.3-41.5%. <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> The figure depends on the copy rule, and should always be quoted with it (Table 2). <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> Exact copies alone are a small share. Copies within one edit, or contained, are about a third.

**Table 2.** Share of test texts with a copy in training, for one random object split, by copy rule. <!-- src: experiments/redteam_bench_restoration/RESULTS.md -->

| copy rule | share of test texts |
|---|---|
| exact copy only | 6.8% |
| exact or contained | 30.1% |
| within one edit | 18.9% |
| within one edit, or contained (primary) | 36.1% |
| within two edits | 38.2% |
| within two edits, or contained | 50.0% | <!-- src: experiments/redteam_bench_restoration/RESULTS.md -->

A coarser sign list raises the share: lumping the fish signs takes the primary rule to 43.2%, and lumping all look-alike signs to 49.7%. <!-- src: experiments/redteam_bench_restoration/RESULTS.md -->

We made this error ourselves. Our first held-out set was drawn from distinct sequences at random, and 251 of its 554 texts (45%) were within one edit of a development text. <!-- src: experiments/redteam/RESULTS.md --> On that split, the real order of signs beat every reordering in 63% of held-out texts; without the leaked texts, 42%, with chance at 3%. <!-- src: experiments/redteam/RESULTS.md --> On a split by family the figure is 40.2% against 5.7% by chance. <!-- src: experiments/revalidation/RESULTS.md --> The finding survived; its size did not.

### 4.3 Effect on a trained model

Leakage matters only if models exploit it. To measure this, we retrained a public masked-sign restoration model (a Kneser-Ney trigram, a transformer and their blend), using its authors' code unchanged on our M77 readings of their texts. <!-- src: experiments/bench_restoration/RESULTS.md --> We do not name the release here, because the paper describing it is under review. [Before submission: send the authors these results and cite their paper if it is out.] Its split was random by object, as is standard, and its authors removed exact repeats. <!-- src: experiments/bench_restoration/RESULTS.md -->

We kept the test set fixed and removed 177 texts from training in two ways: once the 177 that are near-copies of a test text, and once 177 unrelated texts as a size control. We also built a split that keeps each family on one side. <!-- src: experiments/bench_restoration/RESULTS.md --> The design was pre-registered with a pass bar of a 5-point drop for all three models. <!-- src: experiments/bench_restoration/RESULTS.md -->

**Table 3.** Top-1 accuracy (%) of masked-sign restoration, every position of every test text. <!-- src: experiments/bench_restoration/RESULTS.md -->

| training set | trigram | transformer | blend |
|---|---|---|---|
| size control (177 unrelated texts removed) | 41.71 | 39.00 | 43.42 |
| near-copies removed (177 texts) | 35.44 | 33.10 | 36.16 |
| split by family | 35.45 | 35.66 | 36.41 | <!-- src: experiments/bench_restoration/RESULTS.md -->

Removing near-copies lowers accuracy by 6.3, 5.9 and 7.3 points. <!-- src: experiments/bench_restoration/RESULTS.md --> Over 100 further random size controls, the trigram gap is never below 5.7 points. <!-- src: experiments/bench_restoration/RESULTS.md --> So about a sixth of the reported accuracy comes from near-copies. Without them the transformer is 2.3 points below the trigram, and on the family split it ties (+0.2). <!-- src: experiments/bench_restoration/RESULTS.md --> The authors' own table already had the trigram ahead of the transformer, which our result supports. <!-- src: experiments/bench_restoration/RESULTS.md -->

An independent reimplementation, written without reading our scoring code, confirms the tie under all ten copy rules we tried. <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> Two cautions apply. The trigram's smoothing alone moves clean accuracy by about 2 points, the size of every neural-against-n-gram difference here. <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> And our readings differ from the authors' on some texts, so absolute numbers are ours; the comparisons between rows all use the same readings. <!-- src: experiments/bench_restoration/RESULTS.md -->

### 4.4 Recommendation

Split the Indus corpus by family, not by object, and report the copy rule. We release our split (571 held-out texts in 505 families, none within one edit of a development text) as text numbers with a fixed hash. <!-- src: experiments/revalidation/RESULTS.md --> Family splitting catches near-copies, not shared formulae, so it is a floor on what a clean evaluation needs.

## 5. What the corpus can detect

A null result on a corpus this small says little unless the test could have succeeded. For each question below we planted a known answer, in Indus texts or in a real corpus thinned to Indus size, and recorded how often the test found it.

**Text genres.** Unsupervised mixture models find one genre in the Indus texts. Planting genres in 2,269 real texts shows that 80% power needs a genre that differs by 0.57 bits per text, in vocabulary, formula and length together. <!-- src: docs/NEGATIVE_ATLAS.md --> Object type, which a supervised classifier does separate on held-out texts, carries only 0.15 bits. <!-- src: docs/NEGATIVE_ATLAS.md --> So "one genre" is expected even where registers exist. A split as strong as Mesopotamian seal legends against tags, at 1.15 bits, would have been found. <!-- src: docs/NEGATIVE_ATLAS.md -->

**A joining sign as a relation word.** One frequent sign often stands between two sign groups. If it meant something like "son of", the groups on either side should also occur as independent texts more often than chance. Before using Indus data, we ran this test on real Ur III and Old Babylonian seal legends thinned to Indus size. It recovered "son of" in 3 of 100 and 0 of 100 samples, against a bar of 80. <!-- src: docs/NEGATIVE_ATLAS.md --> On the full 5,180 Ur III legends it ranks "son of" first. <!-- src: docs/NEGATIVE_ATLAS.md --> The test was therefore not run on Indus; it needs about four times more texts. <!-- src: docs/NEGATIVE_ATLAS.md -->

**A sign enriched on pottery.** A test of whether the jar-shaped sign marks vessels has 47% power on the 65 pottery texts from Harappa, Lothal and Kalibangan where both editions agree; about 250 are needed. <!-- src: experiments/m342_offsite/RESULTS.md -->

**Language or code.** Whether the script writes language is the most argued statistical question about it (Farmer et al. 2004; Rao et al. 2009; Sproat 2014). We tested two approaches against known answers. First, a sign-order test: how often a text's real order beats every reordering of its own signs. Indus scores 0.402. Run unchanged on 7 non-linguistic codes and 6 writing systems, each sampled to Indus size and split by family, it gave weather reports 0.98, named chess openings 0.63, emoji sequences 0.60 and heraldic blazons 0.49, against Linear B 0.34 and short Latin inscriptions 0.10. <!-- src: experiments/audit_followups/RESULTS.md --> Four of the seven codes passed the bar of 0.30. <!-- src: experiments/audit_followups/RESULTS.md --> The test detects fixed formats, not language, which extends Sproat's (2014) argument about entropy measures to order. Second, a classifier trained on known languages and codes reaches a balanced accuracy of 0.61 when each code is held out in turn, and 0.69 on genre-matched short labels, against a pre-registered gate of 0.80. <!-- src: docs/NEGATIVE_ATLAS.md --> Neither approach can answer the question at this size.

**Summary.** Table 4 lists these limits with what would change them. <!-- src: docs/NEGATIVE_ATLAS.md -->

**Table 4.** Detection limits at the present corpus size. <!-- src: docs/NEGATIVE_ATLAS.md -->

| question | what the test needs | what the corpus has |
|---|---|---|
| distinct genres | a difference of 0.57 bits per text | object type differs by 0.15 |
| joining sign as relation word | about 4 times more texts | 2,270 distinct texts |
| jar sign on pottery | about 250 pottery texts | 65 |
| language against code | a test that separates known cases | none passed its gate | <!-- src: docs/NEGATIVE_ATLAS.md; experiments/m342_offsite/RESULTS.md; data/splits_v2.json -->

Some of these limits will move with new data. The third volume of the Corpus of Indus Seals and Inscriptions, not yet in any digital corpus we could use, and excavation databases of marked sherds could bring the pottery question within reach. We have hashed forward predictions for such data so that the test is fresh when it arrives.

## 6. Limitations

**Shared errors.** Disagreement between the editions is a lower bound on reading error, because errors both share are invisible.

**One sign list.** All tests run in Mahadevan's sign numbering. We re-ran the main structural tests under 12 alternative sign lists elsewhere, but the leakage figures here use M77 and change with lumping (Table 2). <!-- src: README.md -->

**Readings in the restoration test.** We used our readings of the release's texts, not the authors'. Under their readings, some texts we count as copies are not copies, which is why we report the retraining (Table 3) rather than our first scoring of their deposited predictions. <!-- src: experiments/bench_restoration/RESULTS.md -->

**Simulators.** The planted-answer controls write real languages in invented scripts. They may differ from the Indus texts in how often names occur, which affects the size of the limits in Section 5.

**Agents.** Most analyses and all red-team attacks were run by AI agents under written rules, with a human lead who set the questions and checked the results. Pre-registration and hashing limit what an agent could tune after seeing data. The red teams share a model family with the original analysts, so their independence is partial, and none of this replaces review by epigraphers.

## 7. Data and code

Code, pre-registrations with their hashes, results files and a ledger of every test run are in the project repository. The split by family is released as text numbers with its hash. The corrected sign-list concordance is released with the evidence for each entry. The corpus files are not redistributed, because neither source states terms that allow it; a script rebuilds them from the public sources.

## References

<!-- audit: skip -->

Assael, Y., Sommerschield, T., Shillingford, B., et al. (2022). Restoring and attributing ancient texts using deep neural networks. *Nature* 603, 280-283.

Button, K. S., Ioannidis, J. P. A., Mokrysz, C., et al. (2013). Power failure: why small sample size undermines the reliability of neuroscience. *Nature Reviews Neuroscience* 14, 365-376.

Farmer, S., Sproat, R. and Witzel, M. (2004). The collapse of the Indus-script thesis. *Electronic Journal of Vedic Studies* 11(2).

Kapoor, S. and Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 4(9), 100804.

Lewis, P., Stenetorp, P. and Riedel, S. (2021). Question and answer test-train overlap in open-domain question answering datasets. *Proceedings of EACL*.

Mackay, E. J. H. (1938). *Further Excavations at Mohenjo-daro*. Government of India.

Mackay, E. J. H. (1943). *Chanhu-daro Excavations 1935-36*. American Oriental Society.

Mahadevan, I. (1977). *The Indus Script: Texts, Concordance and Tables*. Archaeological Survey of India.

Parpola, A. (1994). *Deciphering the Indus Script*. Cambridge University Press.

Rao, R. P. N., Yadav, N., Vahia, M. N., Joglekar, H., Adhikari, R. and Mahadevan, I. (2009). Entropic evidence for linguistic structure in the Indus script. *Science* 324, 1165.

Søgaard, A., Ebert, S., Bastings, J. and Filippova, K. (2021). We need to talk about random splits. *Proceedings of EACL*.

Sommerschield, T., Assael, Y., Pavlopoulos, J., et al. (2023). Machine learning for ancient languages: a survey. *Computational Linguistics* 49(3).

Sproat, R. (2014). A statistical comparison of written language and nonlinguistic symbol systems. *Language* 90(2), 457-481.

Vats, M. S. (1940). *Excavations at Harappā*. Government of India.

Wells, B. K. (2015). *The Archaeology and Epigraphy of Indus Writing*. Archaeopress.

Wells, B. K. and Fuls, A. *Interactive Corpus of Indus Texts* (ICIT), online database.

Yadav, N., Joglekar, H., Rao, R. P. N., Vahia, M. N., Adhikari, R. and Mahadevan, I. (2010). Statistical analysis of the Indus script using n-grams. *PLoS ONE* 5(3), e9506.

[To verify every entry against the published record before submission. Add the restoration release once its paper is out, Parpola et al. CISI volumes 1-3, and the Kalibangan and Lothal reports if cited.]

<!-- audit: end-skip -->

## Numbers audit

Generated by `scripts/audit_paper_numbers.py`. Numbers checked: 180. Mismatches: 0. Missing source files: 0.

The check is mechanical: a number passes if it appears in the file its sentence cites. It does not prove the number means the same thing there; that was checked by reading.

Single-digit numbers pass on presence alone, which is weak evidence: 23 of the 180 checks. These were also read against their sources by hand.

No mismatches.
