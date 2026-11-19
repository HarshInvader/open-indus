# Novelty check: "decipherability" under a related-language model

Survey agent, 2026-11-19. Every URL below was downloaded and its text read (methods and results at least). PDFs were fetched with a generic User-Agent. Nothing was taken from snippets unless marked **NOT READ**.

## The claim being checked

1. Deciphering a logo-syllabic script with only a related language's model (e.g. an Italian model for Latin text) is not identifiable. Sign-value recovery stays at 4-26% and is flat from 2.5k to 230k tokens.
2. Wrong keys outscore the true key under the objective. The effect is strong at small sizes and weakens by about 30k tokens.
3. More search (200 restarts) does not help.
4. A model of the true language needs only about 2.5k tokens.
5. Anchors (10-20 known values) and a closer lexicon raise recovery.
6. Planned: a fitted "decipherability law" of the form recovery = f(size, LM mismatch, anchors, text length, logogram share). It would be validated on held-out pairs and on Linear B and Ugaritic, then used to place Indus, Linear A and Rongorongo.

## Conclusion first (verdict)

- **The qualitative core is already known.** Previous work showed that a less related known language degrades decipherment, that partial known values help, that a mismatched model makes EM drift away from the truth, and that the gold key need not maximise the objective. A reviewer will cite Luo et al. 2021, Knight et al. 2006, Snyder et al. 2010 (and the thesis chapter), Berg-Kirkpatrick & Klein 2013 and Dou & Knight 2013. "Related-language decipherment degrades" is **not a contribution**. Nor is "anchors help".
- **What is plausibly new:**
  - (a) A controlled size sweep showing that under model mismatch, sign-value recovery reaches a **plateau that does not move with corpus size**, while a matched model succeeds at small sizes. Framed this way it is an empirical "infinite unicity distance under mismatch".
  - (b) Direct measurement that the **true key scores below wrong keys** under the mismatched objective, and how that gap changes with size. This separates model error from search error.
  - (c) An **anchor dose-response curve**.
  - (d) Any of this specifically for **logo-syllabic** inventories. All the prior controlled work is alphabetic, abjad, syllabic Linear B or word-level MT.
  - (e) A multi-factor fitted law validated on held-out pairs. **Nobody has published one.**
- **Biggest risks:**
  - (i) Dou & Knight 2013 already show a mismatch plateau: their "Adjacent" system's curve "plateaus quickly" at 4.2% at 10M tokens. That is word-level MT, but it is the same phenomenon.
  - (ii) Shannon 1949 already notes that equivocation need not go to zero, and that the analysis *assumes the a priori probabilities are known*. Mismatch is the obvious extension, so a theory reviewer will call (a) "expected".
  - (iii) The "law" has only two real deciphered calibration points (Linear B, Ugaritic), and both are alphabetic or syllabic. The mismatch term for Indus, Linear A and Rongorongo is unknown by definition, so a "prediction" for them is a conditional curve, not a placement. Present it as "recovery as a function of an assumed mismatch", or reviewers will call it circular.
  - (iv) Knight & Yamada 1999 got only 22% syllable accuracy on logographic Chinese *with the true language's sound model*. That clashes with claim 4. You need to explain why your logo-syllabic simulation is so much easier with a true-language model (inventory size, logogram share, token definition).

## Paper-by-paper

### 1. Snyder, Barzilay & Knight 2010, "A Statistical Model for Lost Language Decipherment" (ACL)
URL opened: https://aclanthology.org/P10-1107.pdf (full)

**Overlap:**
- Ugaritic is deciphered with a non-parallel *related* language (Hebrew).
- An HMM substitution baseline with a Hebrew character-trigram LM, the closest analogue to our setup, "recovers correct mappings for 22 out of 30 Ugaritic characters (73.3%)". The full model with morphology and a sparsity prior reaches "96.67%".
- Cognate translation reaches 60.42% of types and 66.71% of tokens, against 28.82% and 46.00% for the baseline. Without the sparsity priors the model drops to 46.08% of types.
- Morphology, sparsity and lexical structure all raise accuracy, which is the "lexicon closeness" direction.

**Not shown:**
- No corpus-size sweep and no variation in relatedness.
- The true-vs-wrong-key score comparison is not reported.
- The script is alphabetic (an abjad), not logo-syllabic.
- Note the contrast: a related-language LM gives **73%** alphabet recovery here, far above our 4-26%. A reviewer will ask whether our low numbers come from the logo-syllabic inventory and not from mismatch as such.

### 1b. Snyder, thesis chapter "Lost Language Decipherment" (MIT RBG)
URL opened: https://groups.csail.mit.edu/rbg/code/decipherment/decipherment-chapter.pdf (sections 1.9.4-1.9.6 read)

**Overlap:**
- Ablations: "Know Cogs" (cognate set known exactly) raises word-type accuracy to 71%, against 63% for the full model. Without morphology the model scores 21% (Combo 2).
- Related versus *unrelated* known language: with Hebrew, candidate mappings exist for "67% of all Ugaritic words (4,797 / 7,386)". With English, only "7% (551 / 7,386)".
- Cross-character entropy is 0.48 for Hebrew and 1.58 for English.
- So "unrelated language → failure, and this is detectable" is shown.

**Not shown:**
- No graded relatedness and no size curve.
- Recovery under English is not measured as a function of data.
- No anchors.

### 2. Luo, Cao & Barzilay 2019, "Neural Decipherment via Minimum-Cost Flow: from Ugaritic to Linear B" (ACL)
URL opened: https://aclanthology.org/P19-1303.pdf (full)

**Overlap:**
- Cognate identification: Ugaritic 93.5 (noiseless) and 65.9 (noisy). Linear B 84.7, and 67.3 on "Linear B/names", a subset that simulates deciphering from place names with roughly 50% unpaired words.
- Ablations: removing the monotonic or residual component gives 0.0, and removing flow gives 8.6. Without structural priors, decipherment collapses.

**Not shown:**
- Known-language proximity is not varied.
- The data are lexicons (Linear B has 919 tokens), with no running-text size sweep.
- The Linear B task is cognate *matching* given a Greek lexicon that largely contains the answers. This is much easier than sign-value recovery from running text under an LM. It is not a test of mismatch.

### 3. Luo, Hartmann, Santus, Barzilay, Cao 2021, "Deciphering Undersegmented Ancient Scripts Using Phonetic Prior" (TACL)
URL opened: https://aclanthology.org/2021.tacl-1.5.pdf (full)

**This is the closest prior work on mismatch × anchors.**

**Overlap:**
- Gothic is deciphered against three known languages of decreasing closeness. Base A@10 at 0% whitespace: Proto-Germanic 0.820, Old Norse 0.213, Old English 0.046. Averages: 0.771, 0.338 and 0.148.
- Their words: "language proximity directly impacts the complexity of the decipherment tasks … choosing a close known language is vital".
- **Anchors:** the "partial" model knows the values of 7 characters (k, l, m, n, p, s, t). For Gothic–ON this lifts A@10 from 0.213 to 0.397 (full knowledge gives 0.597). For OE it goes 0.046 → 0.204 → 0.497.
- The IPA prior adds 12.8% on the hardest setting.
- They propose an unsupervised closeness measure, which ranks the right family for Gothic and Ugaritic. For Iberian, no language stands out, so Basque is not supported.
- Iberian personal names: base 60% P@10, full 75%.

**Not shown:**
- No corpus-size sweep.
- No true-vs-wrong-key objective comparison.
- No anchor *dose-response* (one anchor set of 7).
- No logogram share and no fitted law.
- The task is cognate span matching, not full sign-value recovery.

### 4. Nuhn & Ney 2013, "Decipherment Complexity in 1:1 Substitution Ciphers" (ACL)
URL opened: https://aclanthology.org/P13-1060.pdf (full)

**Overlap:**
- The search problem is characterised: optimal decipherment under a bigram LM is NP-hard (equivalent to QAP), while the unigram case is solvable as a linear sum assignment.

**Not shown:**
- This is *computational* complexity, not statistical identifiability.
- No LM mismatch, no data size, no experiments.
- It supports our framing only in that it is about search hardness, the thing we argue is *not* the bottleneck.

### 5. Shannon 1949, "Communication Theory of Secrecy Systems"
URL opened: https://pages.cs.wisc.edu/~rist/642-spring-2014/shannon-secrecy.pdf (read the summary, unicity and a priori sections)

**Overlap:**
- Unicity distance ≈ H(K)/D, "about 30 letters" for English simple substitution.
- He notes that for some "languages" equivocation "does not approach zero … no matter how much material is intercepted".
- He states the key assumption we violate: "a priori probabilities of various keys and messages are assumed known by the enemy cryptographer—how can one determine operationally if his estimates are correct". He gives "Martian invaders" as the case where the priors are "devoid of significance".

**Not shown:**
- No treatment of a cryptanalyst using a *wrong but related* message model.
- Our mismatch plateau is the natural extension, which is novel as a measurement but predictable in theory.

### 6. Ravi & Knight 2008, "Attacking Decipherment Problems Optimally with Low-Order N-gram Models" (EMNLP)
URL opened: https://aclanthology.org/D08-1085.pdf (full)

**Overlap:**
- Exact (ILP) decipherment error is measured against cipher length (2-256 letters) for 1-, 2- and 3-gram English models. "Deciphering with 3-grams works well on ciphers of length 64 or more."
- With a 2-gram model at 414 letters: EM gives 10% error, their method 0.5%.
- Empirical key and message equivocation curves.
- Shannon unicity U = H(K)/(A−B) is computed as 173, 74 and 50 for the 1-, 2- and 3-gram models. They call these "a bit too rosy".
- This is the template for "recovery vs size, search error removed".

**Not shown:**
- The plaintext model always matches (English–English). No mismatch.
- Note that B in their unicity formula is the decipherer's model entropy. Under mismatch, the relevant quantity is the cross-entropy gap between the true key and the best wrong key. That is an opening for a formal contribution.

### 7. Knight, Nair, Rathod & Yamada 2006, "Unsupervised Analysis for Decipherment Problems" (COLING/ACL)
URL opened: https://aclanthology.org/P06-2065.pdf (full)

**Overlap (strong):**
- **Fig. 9:** a Spanish ciphertext (Don Quixote) deciphered against 80 source-language models. Final edit distance: Spanish 434, **Galician 741**, Portuguese 1487, Kurdish 4041, English 4116.
- This is a direct related-language mismatch result. It degrades sharply even for very close languages, and the correct language still wins on P(c).
- They describe the model-error mechanism: "EM initially locks onto the correct theory, but task performance degrades as it tries to make the ciphertext decoding fit the expected bigram frequencies. Better source models do not suffer much." They also note "incompatibilities between the n-gram frequencies used to train P(p) and the n-gram frequencies found in the correct decipherment".
- Restarts: 40+ restarts fix a small word-matching task.

**Not shown:**
- No size sweep under mismatch.
- No true-key-vs-wrong-key score test.
- No anchors curve.
- Alphabetic scripts only.

### 8. Knight & Yamada 1999, "A Computational Approach to Deciphering Unknown Scripts" (ACL workshop)
URL opened: https://aclanthology.org/W99-0906.pdf (full)

**Overlap:**
- They pose our questions explicitly: "What quantity of written text is needed", alphabetic vs syllabic vs logographic, and "robust against language change … (ancient forms of a language)".
- Spanish phonetic decipherment with the true language model: 100 sentences give 97.5%, 50 give 96.2%, 20 give 82.2%, 5 give 48.5%.
- Kana: 200 sentences give 99%.
- **Chinese (logographic): 22% syllable accuracy**, against a 3.2% baseline, with the true language's model.
- They suggest that sound-triple models "may provide robustness against language evolution", but never test it.

**Not shown:**
- The language-change question is raised but no mismatch experiment is run.
- Their logographic result (22% with a *matched* model) cuts against our claim that "a true-language model needs only ~2,500 tokens". We must explain the difference.

### 9. Berg-Kirkpatrick & Klein 2011, "Simple Effective Decipherment via Combinatorial Optimization" (EMNLP)
URL opened: https://aclanthology.org/D11-1029.pdf (methods, results)

**Overlap:**
- Lexicon matching. ROMANCE (Spanish/Portuguese/Italian cognates) reaches 90.1% accuracy.
- Ugaritic–Hebrew lexicons restricted to cognates give 90.4%, with 28 of 33 alphabet entries correct (Snyder reported 60.4% and 29/33).
- They note that restricting to cognates "made the task easier".

**Not shown:**
- No mismatch gradient, no size curve, no anchors.

### 10. Berg-Kirkpatrick & Klein 2013, "Decipherment with a Million Random Restarts" (EMNLP)
URL opened: https://aclanthology.org/D13-1087.pdf (full)

**Overlap (search vs model error):**
- Zodiac 408: 1 restart gives 18% accuracy, 100 restarts give 90%, and gains saturate at about 100.
- **The gold key is not the optimum.** Gold-initialised EM scores −1467.4, but the best of 1M restarts scores −1466.5, and accuracy drops from 92% to 89%. So with a *matched* LM, a slightly wrong key already outscores the truth. Their reading: "small improvements to high likelihoods … may not be" correlated with accuracy.
- Synth-340: 100 → 100K restarts gains about 9%. Across 100 synthetic ciphers with 10K restarts, mean accuracy is 75% and the minimum 36%.

**Not shown:**
- No mismatch and no size sweep.
- Our claim "restarts don't help because wrong keys outscore the truth" is the *model-error* half of their diagnosis, scaled up by mismatch. This is new as a measurement but not as a concept.

### 11. Ravi & Knight 2011, "Deciphering Foreign Language" (ACL)
URL opened: https://aclanthology.org/P11-1002.pdf (full)

**Overlap:**
- Word-substitution decipherment: 87.8-88.6% on temporal expressions. On Transtac, Bayesian decipherment gives 60.1% at 9k tokens and 80.0% at 100k (2-gram), and 82.5% with a 3-gram LM.
- MT decipherment Spanish→English, using English monolingual data only (a cross-language model): edit distance 28.7 and BLEU 48.7 on Time, against MOSES at 4.7 and 88.0. OPUS gives BLEU 15-19.
- "Scores do not improve much when going beyond 10,000 train[ing]" sentences, which is a size plateau in cross-language decipherment.

**Not shown:**
- No controlled mismatch, and not a script or sign-value recovery task.

### 12. Dou & Knight 2012, "Large Scale Decipherment for Out-of-Domain Machine Translation" (EMNLP-CoNLL)
URL opened: https://aclanthology.org/D12-1025.pdf (methods, results)

**Overlap:**
- Same-language word cipher with the LM trained on a *different chronological half* of Gigaword, a mild domain mismatch. Accuracy reaches 92.2%, and "both token and type accuracy increase as more and more data becomes available".
- Transtac improves from 82.5% to 88.1%.

**Not shown:**
- With a mild mismatch, accuracy still grows with data. That contrasts with our plateau and helps place where the regime changes.

### 13. Dou & Knight 2013, "Dependency-Based Decipherment for Resource-Limited Machine Translation" (EMNLP)
URL opened: https://aclanthology.org/D13-1173.pdf (methods, results)

**Overlap (closest to the "flat with size" claim):**
- Spanish deciphered into English (different languages) by word decipherment.
- "The learning curve of Adjacent plateaus quickly", at **4.2%** accuracy at 10M tokens.
- Dependency bigrams lift this to 24.6% (10M) and 27.0% (100M), and to 41% on the top 5k types.
- So under language mismatch, a bigram objective plateaus at a few percent regardless of size, and richer structure raises the ceiling.

**Not shown:**
- Not a cipher or script: word-to-word translation, with no true 1:1 key.
- No anchors.
- No explicit true-key-vs-wrong-key comparison.
- Still, a reviewer could cite it against the "flat with size" novelty.

### 14. Kambhatla, Mansouri Bigvand & Sarkar 2018, "Decipherment of Substitution Ciphers with Neural Language Models" (EMNLP)
URL opened: https://aclanthology.org/D18-1102.pdf (methods, results)

**Overlap:**
- Beam search plus neural LM, with symbol error against cipher length (16-256).

**Not shown:**
- The plaintext language is always matched (English). Little overlap.

### 15. Kambhatla, Born & Sarkar 2023, "Decipherment as Regression: Solving Historical Substitution Ciphers by Learning Symbol Recurrence Relations" (Findings of EACL)
URL opened: https://aclanthology.org/2023.findings-eacl.160.pdf (sections 5-7 read)

**Overlap (mismatch + anchors):**
- Their English-trained model was applied zero-shot to the **Latin** Borg cipher: "SER of 45.14%".
- "A mere 3 manual interventions … are sufficient to solve the entire cipher with SER 3.89%."
- A multilingual model (13 languages, no language ID) gets 4.10% against 5.47% for the earlier system.
- So "wrong-language model + a few anchors → solved" is demonstrated anecdotally on one alphabetic cipher.

**Not shown:**
- No systematic dose-response, size curve or identifiability analysis.
- Alphabetic only.

### 16. Aldarrab & May 2021, "Can Sequence-to-Sequence Models Crack Substitution Ciphers?" (ACL)
URL opened: https://aclanthology.org/2021.acl-long.561.pdf (methods, results)

**Overlap:**
- Multilingual decipherment without language ID across 14 languages. Increasing the number of training languages "negatively affects performance".
- The Borg cipher is cracked using a Latin model.

**Not shown:**
- No held-out related-language test and no size × mismatch analysis.

### 17. Pourdamghani & Knight 2017, "Deciphering Related Languages" (EMNLP)
URL opened: https://aclanthology.org/D17-1266.pdf (methods, results)

**Overlap:**
- Character-cipher conversion between six related-language pairs with no parallel data. BLEU4 (IL→RL, best): bos→srb 39.9, mkd→bul 11.9, mal→ind 10.4, dan→swe 6.9, afr→dut 4.3, bel→pol 1.9.
- Success varies widely with the pair, even among close languages.

**Not shown:**
- The task is translation or conversion, not script decipherment.
- No size curve and no anchors.

### 18. Hauer & Kondrak 2016, "Decoding Anagrammed Texts Written in an Unknown Language and Script" (TACL)
URL opened: https://aclanthology.org/Q16-1006.pdf (sections 3-4 read)

**Overlap:**
- Identifying the plaintext language of ciphers across 380 languages: trial decipherment reaches 97.1% (test).
- Of the 11 errors, 7 "involve closely related languages, such as Serbian and Bosnian". Related languages are confusable under the objective.

**Not shown:**
- No measurement of recovery when only the related language is available.

### 19. Raghavendra 2026, "On the Non-Specificity of Statistical Measures Used in Script Decipherment" (arXiv 2608.02999)
URL opened: https://arxiv.org/pdf/2608.02999 (abstract, sections 1-3 and 6.3 read)

**Overlap (Indus-specific, recent):**
- A synthetic non-linguistic emblem system (SIGIL) reproduces Indus-like statistics.
- A decipherment stress test gets in-sample dictionary coverage of 83.0% (English), 88.13% (Sanskrit) and 67.73% (Tamil). Grouped held-out coverage is 74.23%, 61.01% and 44.05%. Random keys give 6.50-9.48%.
- "Six bootstrap script keys agree on just 9.30% of sign values even though each parses more than 93.5% of the corpus."
- The objective is satisfied by mutually incompatible keys, which is our "not identifiable" message in a different setting.

**Not shown:**
- The corpus encodes *no* language, so this is not a related-language mismatch.
- No size curve and no anchors.
- **A reviewer of an Indus-facing paper will certainly cite this.** It already makes the "high objective ≠ identified key" argument for Indus.

### 20. Nair 2026, "How Non-Linguistic Is the Indus Sign System? A Synthetic-Baseline Scorecard" (arXiv 2604.17828)
URL opened: https://arxiv.org/pdf/2604.17828 (abstract and intro)

**Overlap:**
- None on decipherability. It uses synthetic baselines for the linguistic-or-not question (1,916 texts, 584 signs, 11,110 tokens).

**Not shown:**
- No decipherment experiments.

### 21. Yadav, Joglekar, Rao, Vahia, Mahadevan & Adhikari 2009, "Statistical analysis of the Indus script using n-grams" (arXiv 0901.3017)
URL opened: https://arxiv.org/pdf/0901.3017 (abstract and intro)

**Overlap:**
- None on decipherment under candidate languages. The abstract says the script "cannot conclusively establish that it encodes natural language".

### 22. Tamburini 2023, "Decipherment of Lost Ancient Scripts as Combinatorial Optimisation using Coupled Simulated Annealing" (CAWL)
URL opened: https://aclanthology.org/2023.cawl-1.10.pdf (skimmed methods and results)

**Overlap:**
- Known-pair cognate matching (Ugaritic, Linear B), with no closeness gradient.

### 23. Braović, Krstinić et al. 2024, "A Systematic Review of Computational Approaches to Deciphering Bronze Age Aegean and Cypriot Scripts" (Computational Linguistics 50(2))
URL opened: https://aclanthology.org/2024.cl-2.7.pdf (sections 2, 4 and 8 skimmed)

**Overlap:**
- Restates Gelb & Whiting: Type III (unknown script and language) "might even be undecipherable". An unknown language "can make the script almost undecipherable".
- No quantitative decipherability analysis is reported. A useful citation to show the gap exists.

### 24. Lin 2024, "Revisiting the Unicity Distance through a Channel Transmission Perspective" (arXiv 2410.14816)
URL opened: https://arxiv.org/pdf/2410.14816 (full; short)

**Overlap:**
- Re-derives U = H(K)/D. Assumes matched language statistics. No mismatch.

### Searched for but not read
- **Sproat 2014**, "A statistical comparison of written language and nonlinguistic symbol systems" (*Language* 90(2)). The Project MUSE PDF returned **HTTP 403**, so it was **NOT READ**. As far as I know, and as the abstracts say, it tests whether corpora are linguistic, not decipherability. Low overlap, but someone should check it.
- **Rao et al. 2009** (Science and PNAS): not opened. Yadav et al. 2009 stands in for this line of work.
- **2023-2026 searches** for "decipherability", "identifiability of decipherment", "lost language decipherment limits" and "cognate decipherment related language" found **no paper** that sweeps size × mismatch × anchors, or that fits a decipherability law. The only recent Indus-relevant items are #19 and #20. The LLM "rare script" benchmarks (e.g. arXiv 2501.17785) are puzzle-style and were not opened.

## What is known vs new, claim by claim

| Our claim | Status | Prior work a reviewer will cite |
|---|---|---|
| A related-language model degrades decipherment | **Known** | Luo et al. 2021 Table 2 (Gothic: PG 0.820 → ON 0.213 → OE 0.046); Knight et al. 2006 Fig. 9 (Galician 741 vs Spanish 434 edit distance); Snyder thesis (English 7% vs Hebrew 67% mappable) |
| Recovery is flat from 2.5k to 230k tokens under mismatch | **Partly new.** The plateau phenomenon is in Dou & Knight 2013 (Adjacent "plateaus quickly", 4.2% at 10M) and is hinted at by Ravi & Knight 2011. No one has shown it for script or sign-value decipherment with a matched-model control. | Dou & Knight 2013; Shannon 1949 (equivocation need not reach 0) |
| Wrong keys outscore the true key (model error, not search error) | **Concept known, measurement new.** BK 2013 show gold < best local optimum even with a matched LM (−1467.4 vs −1466.5). Knight et al. 2006 describe EM drifting away from the truth under worse source models. | BK 2013; Knight et al. 2006 |
| More restarts don't help | Follows from the above, so it is not novel by itself. It is only interesting paired with the gold-score test. | BK 2013 (restarts help when the error is search error) |
| A matched model needs only ~2.5k tokens | Consistent with Ravi & Knight 2008 and Knight & Yamada 1999 for alphabets and kana. **In tension** with Knight & Yamada's 22% on logographic Chinese. | Knight & Yamada 1999 |
| Anchors raise recovery | **Known qualitatively.** A dose-response curve is new. | Luo et al. 2021 (7 known chars: 0.213 → 0.397); Kambhatla et al. 2023 (3 interventions: 45.14% → 3.89% SER) |
| Lexicon closeness raises recovery | **Known** | Snyder thesis (Know Cogs 71%); Luo 2019 Linear B/names; BK 2011 |
| Fitted multi-factor "decipherability law", validated on held-out pairs | **New** (nothing found) | None. The risk is validity: only 2 real calibration cases, and the mismatch for Indus, Linear A and Rongorongo is unknown |

## Closest prior work, ranked (what a reviewer will throw at us)
1. **Luo et al. 2021 (TACL).** Closeness gradient plus partial known values plus a closeness measure, on real ancient languages.
2. **Knight et al. 2006.** Related-language decipherment (Galician/Portuguese for Spanish) and the model-error mechanism of EM under poor source models.
3. **Dou & Knight 2013.** A cross-language decipherment plateau at about 4% regardless of data. Bigger structure raises the ceiling.
4. **Berg-Kirkpatrick & Klein 2013.** The model-vs-search error split. The gold key is not the optimum.
5. **Raghavendra 2026.** For an Indus audience: a high objective with unstable keys (9.30% agreement) means nothing is identified.
6. **Ravi & Knight 2008 + Shannon 1949.** Accuracy vs length and unicity distance. Our result is the mismatched-model extension.

## Recommendations to make it publishable
- Frame the contribution as **identifiability under model mismatch**: an empirical unicity curve that never reaches zero equivocation. Back it with a formal statement, such as "the true key is the argmax only if the cross-entropy gap between true-key and best-wrong-key decodings, under the mismatched LM, is positive". Then show the measured gap against size. That goes beyond Ravi & Knight 2008 and BK 2013.
- Include an **alphabetic control** (e.g. reproduce Knight 2006's Spanish/Galician/Portuguese or Luo's Gothic/PG/ON/OE) on the same pipeline. This shows that logo-syllabic is what makes the plateau so low. Snyder's 73% alphabet recovery with a related LM implies the script type matters.
- Explain the Knight & Yamada 22% logographic result against our ~2.5k-token success with a matched model.
- Report the law as **conditional curves** ("if mismatch ≥ X, recovery ≤ Y at any size"), not as point placements for Indus, Linear A or Rongorongo.
