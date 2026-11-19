# What 2,300 Indus texts can and cannot show: a leakage-free benchmark, power floors and sealed predictions <!-- src: docs/AGENT_BRIEF.md -->

Draft for Digital Scholarship in the Humanities, Journal of Quantitative Linguistics or PLOS ONE. Not submitted. Every number carries a comment naming the file it comes from; `scripts/audit_paper_numbers.py` checks them, and its report is at the bottom.

## Abstract

The Indus script survives in short texts, and many decipherments have been proposed without an outside test. We report what this corpus can support under strict controls. In 469 objects matched through excavation registers, the two standard editions disagree on 12.9% of signs. <!-- src: experiments/consensus_corpus/RESULTS.md --> A held-out split built on text identity alone leaked: 45% of held-out texts had a near-copy in training. <!-- src: experiments/redteam/RESULTS.md --> We rebuilt it by text family and re-ran every headline test on it. Sign order is fixed, but four of seven non-linguistic codes pass the same order test, so order does not show language. <!-- src: experiments/audit_followups/RESULTS.md --> No published sign-to-sound key beats keys fitted to noise with the same freedom. A published neural restoration benchmark loses about 10 points of accuracy once near-copies are removed. <!-- src: experiments/bench_restoration/RESULTS.md --> We measure detection floors: genres weaker than 0.57 bits per text, a relational reading of the connective sign and a vessel reading of the jar sign are untestable at this size. <!-- src: docs/NEGATIVE_ATLAS.md --> Several structural findings survive correction over about 14,100 tests. <!-- src: README.md --> We freeze forward predictions by hash, to be scored on new publications. We claim no decipherment and no language.

## 1. Introduction

The Indus script was used in the Indus Valley around the third millennium BCE. No bilingual is known, and the language is not identified. Proposals that assign sound values to the signs keep appearing. Each tends to report a high match rate against a chosen lexicon, and few report what a key fitted to random strings would score on the same measure.

The statistical literature has its own weak points. Texts are short, many repeat, and some objects carry the same text dozens of times. A random split by object puts near-copies on both sides, so a model can score well by memory. Two printed editions exist, and they read many signs differently. Most published tests do not report their power, so a null result cannot be told apart from a test that could never have succeeded.

This paper is an audit of what the corpus can and cannot support. It makes five contributions:

1. a measured disagreement rate between the two editions, and the headline tests re-run at that rate;
2. a held-out split with no near-copy leakage, and a demonstration of how much the old split inflated results;
3. benches of published phonetic keys and of a published restoration model against fair baselines;
4. power floors for questions the corpus cannot answer at its present size;
5. hash-frozen forward predictions, to be scored on texts not yet published.

We do not offer a decipherment, give any sign a sound value or favour any language family. Where a finding is reported, it is a statement about how signs are ordered and used. It holds whether or not the signs write language.

## 2. Data

**Editions.** We use two transcriptions. The first is Mahadevan's 1977 concordance (M77): 3,573 lines, 13,372 tokens and 417 signs, matching his published totals. <!-- src: README.md --> The second is the Interactive Corpus of Indus Texts of Wells and Fuls (ICIT), 5,679 inscriptions in reading order. <!-- src: README.md --> About 90% of ICIT comes from sites M77 already covers, so it is mostly a second reading of the same objects, not new data. <!-- src: README.md -->

**Distinct texts.** Moulded tablets repeat one text many times. All counts are on distinct sequences: 2,270 distinct M77 texts in 1,477 near-copy families. <!-- src: data/splits_v2.json -->

**How far the editions agree.** We matched 469 objects through the 1930s excavation registers of Mohenjo-daro, Harappa and Chanhu-daro, by serial and field number rather than by their signs. <!-- src: experiments/consensus_corpus/RESULTS.md --> On these, the editions disagree on 12.9% of compared signs (95% CI 11.1-14.9%). <!-- src: experiments/consensus_corpus/RESULTS.md --> An earlier figure of 19.4% included errors in our own mapping between the two sign lists. The largest was a cross-wired pairing of the plain fish signs. <!-- src: experiments/consensus_corpus/RESULTS.md --> An independent red team re-derived the mapping fixes on half the objects and measured on the other half. It got 14.0% over 200 splits (range 12.2-16.0%), so fitting lowers the figure by only 0.6 points. <!-- src: experiments/redteam_consensus/RESULTS.md --> Of all 120 ways to pair the five plain fish signs, the corrected pairing fits best. <!-- src: experiments/redteam_consensus/RESULTS.md -->

Disagreement is uneven. Harappa objects disagree more than Mohenjo-daro objects (17.5% against 10.8%), and sealings more than tablets or seals (24%, 18%, 11%). <!-- src: experiments/redteam_consensus/RESULTS.md --> The matched sample is the best-documented part of the corpus, so disagreement elsewhere is unlikely to be lower. Errors shared by both editors cannot be seen this way, because ICIT drew on the same photographs and on M77.

## 3. Methods

### 3.1 Rules of evidence

Every experiment follows the same written rules. Counts are on distinct texts. Development uses a fixed 75% of texts, and final tests run once on the held-out rest. <!-- src: docs/AGENT_BRIEF.md --> Every claim has a permutation or shuffle null that keeps the relevant structure, such as sign frequencies, text lengths and site. Any method that claims to recover language, sound values or grammar must first recover a known answer from a synthetic or real corpus of similar size, about 2,300 texts of mean length about 4.5 signs. <!-- src: docs/AGENT_BRIEF.md -->

### 3.2 A held-out split by text family

Version 1 of the split held out distinct sequences at random. A red-team audit found that 251 of 554 held-out texts (45%) were within one edit of a training text. <!-- src: experiments/redteam/RESULTS.md --> Version 2 assigns whole families to one side. A family joins texts within one edit of each other, or where one text contains the other. The held-out set has 571 texts in 505 families. <!-- src: data/splits_v2.json; experiments/revalidation/RESULTS.md --> No held-out text is within one edit of a development text. <!-- src: experiments/revalidation/RESULTS.md --> The split file is frozen and its hash recorded in the file itself.

### 3.3 Pre-registration

Each confirmatory test was written up before it was run. The write-up names the statistic, the null, the pass bar and the minimum sample. Its SHA-256 hash, and the hashes of the scripts, go into `docs/prereg/HASHES.txt` before any outcome is computed. As of the last full check, 55 pre-registration files had a hash line; 5 had changed since hashing, and four of these log an amendment. <!-- src: docs/PREDICTION_REGISTRY.md --> We report these deviations rather than hide them.

### 3.4 A ledger of every test, with false discovery rate control

Every test reported in any results file gets one row in `docs/test_ledger.csv`, with its p-value, unit, split, mode and family. The ledger now has 1,272 rows. <!-- src: rows:docs/test_ledger.csv --> Families that reported "ran N tests" without listing them are padded with unlisted members at p = 1. We apply Benjamini-Hochberg correction four ways: across all listed tests, within each area, hierarchically, and across all tests the project ran, about 14,108 after padding. <!-- src: experiments/ledger/RESULTS.md --> A finding is ranked as defensible only if it also replicated on clean held-out data or on the other edition.

### 3.5 Red teams

Positive results go to a separate agent who did not run the original. The red team writes its own pre-registration and its own code and tries to break the claim. Several findings were weakened or reversed this way, and the atlas lists 36 such reversals and weakenings. <!-- src: docs/NEGATIVE_ATLAS.md -->

### 3.6 Robustness to the sign list and to reading errors

The headline tests were re-run under 12 alternative sign lists, including the Wells list and lists built by clustering sign images. <!-- src: README.md --> They were also re-run on the signs both editions agree on, on Wells and Fuls's own readings, and under noise that copies the measured disagreement pattern. <!-- src: experiments/consensus_corpus/RESULTS.md -->

## 4. Results

### 4.1 The old split inflated results

Leakage changes magnitudes. On the version 1 split, 63% of held-out runs had their real sign order beat every permutation of their own signs. Without leaked copies the figure was 42%, with chance at 3%. <!-- src: experiments/redteam/RESULTS.md --> On the version 2 split the true order is strictly best in 40.2% of 321 runs, against 5.7% by chance. <!-- src: experiments/revalidation/RESULTS.md --> The effect survives; its old size did not. Every held-out number in this paper is on version 2.

### 4.2 Sign order is fixed, and that does not show language

The order test asks how often a text's real order beats every reordering of its own signs, under a bigram model trained on development texts. Indus scores 0.402. <!-- src: experiments/audit_followups/RESULTS.md --> We ran the same test, unchanged, on 7 non-linguistic codes and 6 writing corpora, each sampled to Indus size and split by family. <!-- src: experiments/audit_followups/RESULTS.md --> Weather reports scored 0.98, named chess openings 0.63, emoji sequences 0.60 and heraldic blazons 0.49. Ur III seal legends scored 0.47, Linear B entry lines 0.34 and short Latin inscriptions 0.10. <!-- src: experiments/audit_followups/RESULTS.md --> Four of the seven codes reached the pre-registered bar of 0.30, where two would have been enough to declare that the test cannot separate language from code. <!-- src: experiments/audit_followups/RESULTS.md -->

High scores go with formulaic, fixed-slot text, whether it is language or not. Free word order scores low. So the Indus result shows a fixed format. It is no evidence for language over code.

### 4.3 Published phonetic keys fail fair baselines

A bench is only useful if it can tell a correct key from a fitted one. The atlas bench separates a real decipherment by a wide margin, Linear B at z 11.5. <!-- src: docs/NEGATIVE_ATLAS.md --> The fair comparison for any key is a key fitted to noise with the same freedom.

**Yajnadevam's Sanskrit key.** It needs about 1.3 free choices per sign. Its dictionary score beats the same values shuffled across signs only weakly, z = 1.0 and p = 0.15 under its own phonetic latitude. Keys fitted the same way to random sign strings make longer Sanskrit words, about 4.4 consonants per word against the key's 3.0. <!-- src: experiments/language/RESULTS.md --> In a planted control, the true key on true Sanskrit scored 3.16, below the keys fitted to noise. <!-- src: experiments/language/RESULTS.md --> This way of scoring cannot pick out a correct key.

**Pierson's Proto-Dravidian key.** On held-out texts the key does not beat its own readings shuffled among signs of similar frequency on any of three scores, p = 0.16, 0.11 and 0.75. <!-- src: experiments/bench_pierson/RESULTS.md --> Keys fitted with the same freedom to shuffled sign strings score far higher, a Tamil-bigram hit rate of 0.97 against the key's 0.59. <!-- src: experiments/bench_pierson/RESULTS.md --> The author's coverage of 92.8% is a property of sign frequencies: our measure of it, 74.1% on the real corpus, is identical on a token-shuffled corpus. <!-- src: experiments/bench_pierson/RESULTS.md -->

**A registration-code reading.** Kriger and Hunt report that unicorn seal texts are more unique than chance. On 646 Mohenjo-daro unicorn seals we find the reverse: 88.2% unique, below every draw of a random redeal (99.2%) and of a positional redeal (97.5%). <!-- src: experiments/bench2026/RESULTS.md -->

**The limit of these benches.** In a planted Tamil corpus, the bench could not certify even the true key, p = 0.28 on the first score. <!-- src: experiments/bench_pierson/RESULTS.md --> So the benches can reject a key's evidence as non-diagnostic, but a pass would not confirm a key. Text-internal scores alone cannot certify sound values at this corpus size.

### 4.4 Restoration accuracy on a published release is inflated by near-copies

*Red team passed; retraining pending.* An independent reimplementation from scratch, pre-registered before it ran, reproduced the leakage count exactly, at 107 of 296 texts, and tripped none of its kill criteria. Leakage depends on the copy rule: 7% for exact copies, 36% for one edit or containment, and 50% for two edits. Across 200 other random object splits the median is 36.0% (95% range 31-41%), so any random object split of this corpus leaks about this much. On clean texts the transformer is at or below the trigram under all 10 copy definitions (−1.8 points, 95% CI −4.5 to +0.8), and +0.5 against a differently smoothed trigram, so it ties. <!-- src: experiments/redteam_bench_restoration/RESULTS.md --> A retraining check on leakage-fixed splits is pre-registered (`docs/prereg/bench_restoration_retrain.md`). The numbers below come from scoring the release's deposited predictions.

We benched the masked-sign restoration release from IIT Hyderabad. Of their 296 test texts, 107 (36%) have a near-copy among the 1,282 training texts. Their folds were hashed by object, not by text family. <!-- src: experiments/bench_restoration/RESULTS.md --> On leaked texts their blended model gets 57.8% top-1 accuracy, and on clean texts 30.5%. <!-- src: experiments/bench_restoration/RESULTS.md --> On clean texts the transformer is no better than a plain trigram: 28.5% against 29.8%, a difference of −1.4 points (95% CI −4.0 to +1.3, p = 0.86). <!-- src: experiments/bench_restoration/RESULTS.md --> A neural gain above about 3 points would have been detected. <!-- src: experiments/bench_restoration/RESULTS.md --> The authors' own table already had their trigram ahead of the transformer, 39.6 against 37.5, and the deposit is honest and well built. <!-- src: experiments/bench_restoration/RESULTS.md --> The bench scored subsets of fixed predictions. Clean texts may also be harder for reasons other than leakage, which the retraining check is designed to separate.

### 4.5 Findings that survive, and their caveats

The findings below survived an independent reimplementation, a re-test on the version 2 split and correction across the ledger. Each is worded as a fact about sign use. If the signs are not language, none of them falls; the words change, so that "grammar" becomes "fixed ordering". <!-- src: docs/ASSUMPTIONS.md -->

**Fixed order beyond position.** Shown in Sections 4.1 and 4.2. On clean held-out texts, 40% of 321 runs beat every permutation against 5.7% chance, q about 8e-72. <!-- src: README.md --> It holds with half the texts read backwards, at 2.6 times chance, and with 10% of signs misread, at about 5 times. <!-- src: README.md --> It shows sequential structure, which a grammar or a fixed formula would give equally.

**Ticked fish take the closing slot.** Fish signs with corner ticks end the text far more often than plain fish signs. On complete single-line held-out texts, 9 of 16 ticked fish are final against 2% of plain fish, p = 0.006. <!-- src: experiments/audit_followups/RESULTS.md --> The effect size is the same under every sign list, but the p-value misses 0.05 when the fish are lumped. Across all tests the clean held-out result has q = 0.54. <!-- src: README.md --> The sample is small: 13 of the 16 held-out tokens are from Mohenjo-daro. <!-- src: README.md --> "Closing" assumes the reading direction is known text by text.

**Round Gulf-type seals break Indus sign order.** Gulf seals carry +2.17 bits per sign of order excess (95% CI 1.63-2.70). <!-- src: README.md --> After a label error was fixed, 8 round seals from the Indus region break order about as much: foreign against home round seals differ by +0.11 bits, p = 0.68. <!-- src: README.md --> So the effect belongs to the round seal type, wherever found. It fits another language, a round-seal genre in the Indus language or pseudo-writing, and the data cannot separate these. With n = 8, it is the smallest sample among the findings. <!-- src: README.md -->

**Six plus fish is a fixed expression.** The two-tier six sign M109 is followed by the fish M59 in 7 of 10 clean held-out cases against a base rate of 3.1%, p = 2.8e-9. <!-- src: experiments/revalidation/RESULTS.md --> It misses its bar under a coarse sign list that lumps signs. <!-- src: docs/ASSUMPTIONS.md -->

**Object types have their own vocabularies.** A classifier trained on development texts separates object types on held-out texts: AUC 0.87 for copper tablets, 0.76 for tablets, 0.73 for pottery, 0.72 for seals and 0.67 for sealings. All are above the 95th percentile of label permutations, 0.55-0.61. <!-- src: experiments/revalidation/RESULTS.md -->

**Text cores are one or two signs.** 34% of cores are a single sign, and 80% of signs in longer cores also stand alone as whole cores, against at most 14% and 11% in syllabic name systems. <!-- src: README.md --> Recurring sign pairs keep one order in 91% of tokens; on held-out texts, 115 of 138 follow the development order, p = 3e-16. <!-- src: README.md --> This is the finding most sensitive to transcription. Under noise that copies the measured disagreement and targets rare signs, the fixed-pair part passes in only 3 of 5 runs. <!-- src: experiments/redteam_consensus/RESULTS.md -->

**The fish signs substitute for each other as a class.** Held-out p = 0.0002-0.0004. <!-- src: README.md --> This is a distributional class. It does not support reading the fish as a deity name, which failed on held-out texts.

**Weaker findings.** Left-to-right texts behave as reversals in 31 of 34 copy-free lines, q = 6e-6. <!-- src: README.md --> But this needs the direction label to be right for nearly every line: with 10% of objects flipped at random the share falls to 0.69-0.72 and misses its bar. <!-- src: README.md --> Neither edition can confirm the other: only 8 lines carry the same label and signs in both. <!-- src: experiments/consensus_corpus/RESULTS.md --> A functional parse covers 76% of unseen texts against 44% for shuffles, which shows that positional classes exist. Whether its 11 specific roles are right is weakly supported, p = 0.013, q = 0.085. <!-- src: README.md -->

**At the measured disagreement rate.** All nine headline tests pass on the signs both editions agree on, on Wells and Fuls's readings and under structured noise. <!-- src: experiments/consensus_corpus/RESULTS.md --> The ticked-fish result passes the primary consensus corpus only at p = 0.039 against a bar of 0.05. <!-- src: experiments/consensus_corpus/RESULTS.md -->

**A descriptive comparison, not a test.** If the signs write language, the inventory fits a logo-syllabic or mostly logographic script: 120 signs cover 90% of tokens, against 63 in Linear B and 14 in Latin. <!-- src: README.md --> No sign-level phonetic structure was found to support the syllabic part.

## 5. Negative results and power floors

A null result means little without the power of the test. For each question below we measured, with planted answers, what the corpus could have detected.

**Text genres from the signs alone.** Unsupervised mixture models find one genre in the Indus texts. Planting genres in 2,269 real texts shows the floor: 80% power needs a genre that differs by 0.57 bits per text, in vocabulary, formula and length together. <!-- src: docs/NEGATIVE_ATLAS.md --> Real Indus object type carries 0.15 bits. <!-- src: docs/NEGATIVE_ATLAS.md --> So "no genres found" is expected even if object-type registers exist, as Section 4.5 shows they do. A split as strong as Mesopotamian seal legends against tags, 1.15 bits, would have been found. <!-- src: docs/NEGATIVE_ATLAS.md -->

**The connective sign M99 as a relator.** We asked whether, in "X M99 Y", X and Y each occur as independent texts more often than chance, as names joined by "son of" do. Before touching Indus, we ran the test on real Ur III and Old Babylonian seal legends thinned to Indus size. It recovered "son of" in 3 of 100 and 0 of 100 samples, against a bar of 80. <!-- src: docs/NEGATIVE_ATLAS.md --> On the full 5,180 Ur III legends the same test ranks "son of" first. <!-- src: docs/NEGATIVE_ATLAS.md --> The test was not run on Indus. It needs about four times more texts.

**The jar sign M342 as a vessel marker.** In the consensus corpus, 65 pottery texts from Harappa, Lothal and Kalibangan give 47% power to detect a 1.5-fold enrichment; about 250 are needed. <!-- src: experiments/m342_offsite/RESULTS.md --> The larger ICIT pool for the same sites, with 265 pottery texts and power 0.92, points the other way, at 0.80 times the expected rate. <!-- src: experiments/m342_offsite/RESULTS.md --> The pre-registered test is untestable. The secondary evidence leans against a vessel reading.

**Language against code.** A classifier trained on known languages and codes reaches a balanced accuracy of 0.61 when each code is held out in turn, and calls 3 of 6 codes language. <!-- src: docs/NEGATIVE_ATLAS.md --> It gives Indus a probability of being language of 0.49 on development texts and 0.51 on held-out texts. <!-- src: docs/NEGATIVE_ATLAS.md --> On genre-matched short labels it reaches 0.69 against a pre-registered gate of 0.80. <!-- src: docs/NEGATIVE_ATLAS.md --> Neither battery passes its own gate, so the question is untestable at this size. Entropy-style statistics fail their controls too. Together with Section 4.2, this means no statistic we know of can tell whether these texts write language.

**Other closed routes.** The atlas records 80 entries, each with its question, method, key number, power, verdict and what would reopen it. <!-- src: docs/NEGATIVE_ATLAS.md --> Many fall into two groups: routes refuted at stated power, such as a consonant-vowel grid or phonetic complements, and routes untestable without more texts or an outside anchor.

## 6. Sealed forward predictions

Retrospective tests on a corpus that has been studied for decades can always be suspected of tuning. The cleanest test is a prediction frozen before new data arrive.

The registry lists 38 forward predictions for new finds. <!-- src: docs/PREDICTION_REGISTRY.md --> They include that ticked fish stand last, that M109 is followed by M59, that the 849 majority-order sign pairs keep their order, and that the frozen functional parse covers new texts at a rate whose interval contains 0.77. <!-- src: docs/PREDICTION_REGISTRY.md --> Each has a pass bar, a fail bar and a minimum sample below which it is reported as not evaluable rather than failed. Scoring is mechanical: new texts go in one table, and a frozen script scores them.

A later set, frozen on 2026-11-18, covers the leads that survived to that date. <!-- src: docs/PREDICTION_REGISTRY.md --> Round seals should end in a closer sign at most 25% of the time and should break square-seal order by at least +0.5 bits per sign. <!-- src: experiments/forward_predictions/RESULTS.md --> The plain fish M67, M70 and M72 should behave as one sign. <!-- src: docs/PREDICTION_REGISTRY.md --> A dry run on the held-out site Kalibangan could score only one prediction, about the jar sign on pottery, and it failed (RR 1.12, p = 0.72). That prediction is retired and stays on record. <!-- src: experiments/forward_predictions/RESULTS.md -->

Scoring is triggered by any of: the third volume of the Corpus of Indus Seals and Inscriptions in hand; the sherd and object spreadsheet of the Harappa Archaeological Research Project; 20 or more new scorable texts; or 8 or more new round seals. <!-- src: experiments/forward_predictions/RESULTS.md --> Today only 2 new texts are scorable, and every prediction is below its minimum sample. <!-- src: experiments/forward_predictions/RESULTS.md -->

## 7. Limitations

**The corpus is small and its readings uncertain.** About 13% of signs differ between editions on the best-documented objects, and errors both editors share are invisible. <!-- src: README.md --> ICIT is not independent data. No sign list has been built from photographs by an independent team, and the iconic judgements of sign drawings were not blind.

**Held-out reuse.** The same held-out set has served dozens of experiments since the first cycle. Later tests were designed knowing earlier held-out results, so late-cycle held-out p-values may be optimistic. <!-- src: docs/ASSUMPTIONS.md --> Family splitting catches near-copies, not shared formulae such as the M162 count frame.

**The ledger is probably incomplete.** The total of about 14,100 tests was not re-derived after an early cycle, and board-era tests were merged late. <!-- src: README.md --> This matters for marginal findings, such as ticked fish and round seals, not for those with orders of magnitude to spare.

**Reading direction.** Several findings, and the names of the slots, assume the direction is known for nearly every text. Ten percent of objects read backwards pushes two findings below their bars. <!-- src: docs/ASSUMPTIONS.md -->

**Simulators.** Our planted-answer controls write real languages in an invented script. They may be unrealistic in how often names occur and how words are spelled, which affects the size of the negative results, not the structural findings.

**Agents.** Most experiments and red teams were run by AI agents under written rules, with a human lead. Pre-registration and hashing limit what an agent could tune after seeing data, but they do not replace review by epigraphers. The red teams share a model family with the original analysts, so their independence is partial.

**What we do not claim.** We claim no decipherment, no sound value for any sign and no language or language family. The positive findings are about the order and distribution of signs. They do not depend on the signs writing language, and they do not show that they do.

## 8. Data and code availability

Code, results files, the test ledger, the pre-registrations with their hashes and the prediction registry are in the project repository (https://github.com/HarshInvader/open-indus). The corpus files are not redistributed, because neither source states terms that allow it; `corpus/build.py` rebuilds them from the public sources. The frozen held-out split is included as text numbers. `scripts/reproduce.sh` reruns the analyses with a fixed hash seed. Proposed licences are MIT for code and CC BY 4.0 for writing and result data; these are not yet final.

## References

<!-- audit: skip -->

Farmer, S., Sproat, R. and Witzel, M. (2004). The collapse of the Indus-script thesis. *Electronic Journal of Vedic Studies* 11(2).

Mahadevan, I. (1977). *The Indus Script: Texts, Concordance and Tables*. Archaeological Survey of India.

Parpola, A. (1994). *Deciphering the Indus Script*. Cambridge University Press.

Wells, B. K. and Fuls, A. *Interactive Corpus of Indus Texts* (ICIT), online database.

[Further references to be completed: the restoration release, Pierson 2026, Kriger and Hunt 2026, Yajnadevam, SIGIL (arXiv 2608.02999), the Mackay 1938 and Vats 1940 registers.]

<!-- audit: end-skip -->

## Numbers audit

Generated by `scripts/audit_paper_numbers.py`. Numbers checked: 203. Mismatches: 0. Missing source files: 0.

The check is mechanical: a number passes if it appears in the file its sentence cites. It does not prove the number means the same thing there; that was checked by reading.

Single-digit numbers pass on presence alone, which is weak evidence: 21 of the 203 checks. These were also read against their sources by hand.

No mismatches.
