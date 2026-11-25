# Certify size curve: how many sign tokens does the restoration route need before a true key's fit to the lexicon shows?

Status: **v4, sealed** 2026-11-25 (tag `certify_size_curve`). v2 followed a fresh review of v1 ("FIX, then seal"). v3 writes in the coordinator's decisions of 2026-11-25 and adds the data; see "Decisions" and the review log. No study code existed at sealing. Nothing has been scored. Drafted after `lift_score` failed K1 and closed the restoration route "for this corpus size". Main line (a), the claim bench. Kind ii/iii (a read script used as a known-answer control). Label-free counts were run before this draft with scratch scripts outside the repo; every one is disclosed under "What was seen before this draft".

## Question
- Set by the coordinator: **how many sign tokens would the restoration route need before a true key's fit to the lexicon shows?**
- "Shows" means the sealed `lift_score` gate, unchanged: the true key's held-out restoration gain G is at least 0.02 nats per masked sign, and the controls with no language in them stay under their bars.
- The study walks one read script (Old Assyrian cuneiform) up a ladder of nested corpus sizes, from one sealed draw (2,300 chunks) to 16 of them, with one record-only draw at 32.
- Brief 9 (§3, study 4) framed this question for fit-refute. The coordinator now asks it for the restoration route. Nothing here tests fit-refute.
- **No Indus key is scored. No Indus text is restored, masked or read with any key. No outcome supports or counts against any Indus key, and none licenses a run of one.**

## Why
- `lift_score` (sealed v3): the word-and-fragment score passed its planted test (K0: G 0.16-0.28) and failed at the true key's own dose (K1: 11 of 20). On real Linear B the true key's dose D was −0.02 to +0.03 and λ* was 0 in 20 of 20 draws.
- Its reading closed "certify by held-out restoration on existing texts" for that corpus size and sent the open part here: "what happens at larger corpus sizes".
- There is a stated mechanism by which size could help: the word weights p(w) are learned from the development half. One sealed draw gives about 3,600 development consonants to weight 2,800 or more words. Sixteen draws give about 58,000.
- There is a stated mechanism by which size could mislead: with learned weights, any dense word set becomes a consonant n-gram model of the text, and any grouping of signs into classes can smooth a sparse sign trigram. Both would produce a gain that is not the lexicon's. The controls at every size exist for this.
- **G is this study's gate. Hit@1 is the 2027-clause measure and is reported on every cell. A G pass alone does not meet the 2027 clause** (coordinator decision of 2026-11-25, carried over from `lift_score`).

## Prior art
Opened 2026-11-25 with a plain HTTP client sending User-Agent "open-research-site/1.0". Full open-access text unless noted. Nothing behind a paywall or a bot block was opened.

**Size and decipherment (established).**
- **Ravi and Knight 2008,** "Attacking decipherment problems optimally with low-order n-gram models", EMNLP. https://aclanthology.org/D08-1085.pdf
  - Exact (integer-programming) solution of one-to-one letter substitution, with error plotted against cipher length from 2 to 1,024 letters. A 3-gram model "works well on ciphers of length 64 or more".
  - Tests Shannon's unicity distance U = H(K) / (A − B): the formula gives 173, 74 and 50 letters for 1-, 2- and 3-gram models; the authors call these "a bit too rosy" against their measured equivocation curves.
- **Shannon 1949,** "Communication theory of secrecy systems", doi:10.1002/j.1538-7305.1949.tb00928.x **(unverified:** the DOI resolved to a publisher page that returned no content; the formula above is taken from Ravi and Knight 2008). The general statement was also read at https://en.wikipedia.org/wiki/Unicity_distance.
- **Nuhn, Schamper and Ney 2013,** "Beam search for solving substitution ciphers", ACL. https://aclanthology.org/P13-1154.pdf — symbol error against cipher length (2 to 256 letters) for one-to-one ciphers; a 6-gram model reaches 4.1% error at 32 letters. The same beam search also solves the homophonic Zodiac-408 cipher, where several cipher symbols stand for one letter.
- **Ravi and Knight 2011,** "Deciphering foreign language", ACL. https://aclanthology.org/P11-1002.pdf — word-substitution decipherment reported at 9k and at 100k cipher tokens, and translation quality against training size (their Figure 4): more text helps every system.
- **Berg-Kirkpatrick and Klein 2013,** EMNLP. https://aclanthology.org/D13-1087.pdf — no size curve. Kept for its warning (a wrong key can outscore the gold key), as in `lift_score`.

**Lost-language decipherment (no size curve found).**
- **Snyder, Barzilay and Knight 2010.** https://aclanthology.org/P10-1107.pdf — one corpus size (7,386 Ugaritic word types). A keyword search of the full text found no result by corpus size.
- **Luo, Cao and Barzilay 2019.** https://arxiv.org/pdf/1906.06718 — calls decipherment "an ultimate low-resource challenge"; no size ablation found.
- **Luo, Hartmann, Santus, Cao and Barzilay 2021,** arXiv 2010.11054. https://arxiv.org/pdf/2010.11054 — three corpora of fixed size (Gothic 40,518 tokens, Ugaritic 7,353, Iberian 3,466 chunks). It varies word division and the share of known cognates, not the amount of text.

**Restoration (established at large size; no power analysis found).**
- **Fetaya, Lifshitz, Aaron and Gordin 2020,** PNAS, doi:10.1073/pnas.2003794117. The publisher page refused the client (HTTP 403) and was not retried; the open copy at https://pmc.ncbi.nlm.nih.gov/articles/PMC7502733/ was read. 1,400 Late Babylonian texts, LSTM against n-gram baselines, scored by MRR and Hit@k on 520 test sentences. One training size.
- **Lazar, Saret, Yehudai, Horowitz, Wasserman and Stanovsky 2021,** EMNLP. https://aclanthology.org/2021.emnlp-main.384.pdf — about 10,000 Oracc texts, 2.3 million signs; 89% Hit@5. Zero-shot multilingual pretraining beat a model trained on Akkadian alone, which the authors tie to the small corpus. No curve by corpus size.
- **Assael et al. 2022** (Ithaca), Nature, doi:10.1038/s41586-022-04448-z, read at https://www.nature.com/articles/s41586-022-04448-z — 78,608 Greek inscriptions; 62% restoration accuracy alone. A keyword search of the article found no training-size ablation.

**Verdict.**
- **Established, and not tested here:** a full decipherment search needs a minimum cipher length, which falls as the language model gets stronger (Shannon; Ravi and Knight 2008; Nuhn 2013); more cipher text improves decipherment (Ravi and Knight 2011); restoration models reach high accuracy on corpora of millions of signs.
- **Not established (no source found):** a size curve for a held-out restoration gain that a stated key plus an outside lexicon adds over a sign n-gram; any such curve on undivided text where about nine signs share a consonant value; a power analysis for it; controls for gain that grows with size without any language.
- The cipher-length results do not carry over directly, and not because of homophony: Nuhn 2013 solves a homophonic cipher too. They measure how much text a search needs to recover a key, given a language model of the right language. Here the key is given, the test is whether it can be told from keys with no language behind them, and the lexicon is an outside one.
- The search was short. "Not found" is weak evidence that this is new.

## What was seen before this draft
- **Sealed results:** `lift_certify`, `lift_score` (K0 to K3, including the real-text D and G on Linear B), `ur3_legend_refute`, `lb_shape_ladder`, `lb_formula_dial`, `lb_wrong_lexicon`.
- **Label-free counts, 2026-11-25, scratch scripts outside the repo,** run with the project interpreter and `-I`. They produced only: token and line counts, the reading-to-sign mapping, the modal value of each sign from the editors' readings, lexicon skeleton counts and densities, chunk counts, top-50 bigram shares, distinct-chunk shares, and clean-position counts.
- **Downloads (CC0 Oracc open data):** the Oracc Global Sign List (`ogsl.zip`), the State Archives of Assyria online glossaries (`saao.zip`), and one further project's glossaries (`akklove.zip`, density only). Since v3 the sign list is in the repo and the lexicon is in the repo as a small derived file; `saao.zip` itself stays outside. Hashes are in "Data".
- **Also downloaded or probed, and not used:** the Oracc project list (`projects.json`), read to find glossaries; `riao.zip` (Royal Inscriptions of Assyria online), whose file list was read and which holds no glossary file, so nothing in it was opened; and header-only requests for the sizes of 15 other Oracc project archives, none downloaded. The prior-art papers were downloaded as PDF or HTML.
- **Three further label-free counts for v2:** the uncertain-period catalogue rows, the texts with no language line, and the number of Old Assyrian word-skeleton types (see "Ceiling lexicon").
- **Label-free recount for v3, 2026-11-25.** The coordinator excluded the uncertain-period rows, so every pool count, the mapping tables, the shape table and the ceiling-lexicon count were run again on the pool without them, with the same scratch scripts and one changed line (the period filter). The uncertain rows were also counted alone. The lexicon build script in the repo was run once on `saao.zip`; it reads no text. Nothing was scored. The scratch copies of the prior-art papers, `akklove.zip`, `riao.zip` and `projects.json` were then deleted.
- **Not seen:** any gain G, any dose D, any λ*, any IC, any trigram hit rate, or any lexicon match, on any cuneiform text, real or planted. No lexicon was ever matched against text. No planted text was built. Nothing was run on Indus text.
- The scratch scripts are not the study code. The sealed code must recompute every "Measured" table here before any gain (abort A2).

## Count gate
**Need:**
1. One script, one dialect, syllabic, with at least 8 sealed draws of text. A sealed draw is 2,300 chunks of M77 seal lengths.
2. A true sign-to-value key.
3. A lexicon that does not come from the test text and passes the density rule (LMIN = the smallest L with skeletons / alphabet^L ≤ 25%).
4. At least four nested sizes, each with at least 1,000 clean held-out positions per draw (`lift_score`'s count gate).

**Have:**

| need | found | verdict |
|---|---|---|
| text | Old Assyrian tablets in the held CDLI dump, uncertain-period rows excluded: 4,435 texts with transliteration, 445,733 keyed sign tokens under the frozen drop rule, 53.6 sealed draws. Letters alone: 1,009 texts, 120,265 tokens, 14.2 draws. | passes |
| key | Reading-level key: on disk (the editors' readings). Sign-level key: needs a sign list. With the Oracc sign list every syllabic reading but 11 tokens maps to a sign name; the modal value of each sign covers 98.1% of tokens. | passes **only with the sign list added** |
| lexicon | On disk: one Akkadian glossary of 223 entries (Rimanum), too thin, and one third-party word list with no stated source (not usable). With the Neo-Assyrian glossary added: 3,632 skeletons, density 0.110 at 4 consonants, LMIN 4. | **fails on disk; passes only with the glossary added** |
| sizes | 1, 2, 4, 8 and 16 draws graded (median clean positions 1,614 to 7,536); 32 record-only. | passes |

- **Gate verdict: passes.** It was conditional on two CC0 sources being added. The coordinator approved both on 2026-11-25 (decisions 1 and 2), and they are now in the repo: the sign list as downloaded, the lexicon as a derived file.
- The v2 gate counted a pool that included the uncertain-period rows (4,522 texts, 446,876 tokens). The numbers here are the recount without them. No verdict changed.
- Brief 9 gave "about 205,000 tokens" for Old Assyrian letters. That figure counted broken lines and logograms. Under the frozen drop rule the letters hold 120,265 keyed syllabic tokens.

### The unit
- `lift_score` describes its corpus as "about 13,100 sign tokens in M77-length chunks". Its sealed draws hold a median of 8,049 sign tokens (`kill.json`, check A2): 2,300 chunks at a mean of 3.5 signs.
- **Coordinator decision, 2026-11-25: the `lift_score` unit is worded "2,300 chunks, about 8,000 tokens".** This prereg uses that wording. It edits no other file.
- Sizes are stated in **draw units u (1 u = 2,300 chunks, the sealed draw)** and in tokens. 1 u is about 8,000 tokens here too. M77's own 13,398 tokens sit between 1 u and 2 u.

## Data
- **Text.** The CDLI dump under `experiments/short_labels/raw/cdli` (transliterations and catalogue), as loaded by `ur3_legend_refute/run.py`.
- **Pool T (primary; coordinator decision 3):** catalogue period exactly "Old Assyrian (ca. 1950-1850 BC)", object type "tablet" or "tablet & envelope", genre exactly "Letter", "Legal", "Administrative" or empty.
  - **The period match is exact (coordinator decision 7).** The 159 catalogue rows that pass the other filters with the period "Old Assyrian (ca. 1950-1850 BC) ?" are **not in pool T.** They enter nothing graded: not the key, not a block, not the ceiling lexicon, not pool L. They form set Q, used once in the record-only sensitivity check under "Kill tests".
  - **Language rule:** lines after a `#atf: lang` line that does not name `akk` are dropped. **A text with no `#atf: lang` line at all is kept.** There are 2 such texts in the pool (38 lines, 218 keyed tokens).
  - This is one script, one dialect and almost one site (Kanesh, 93% of the period's catalogue rows). It is **not one genre.** Blocks are cut from one random tablet order, so the genre mix is the same in expectation at every size.
- **Pool L (record-only; coordinator decision 3):** the tablets of pool T with genre "Letter". It is one genre but holds only 14.2 u.
- **Set Q (record-only):** the uncertain-period rows above. 87 have a transliteration, 36 keep at least one line, 35 hold a run of 2 or more signs; 189 lines kept, 1,143 keyed tokens, about 315 chunks (0.14 u).
- **Drop rule (frozen, as `ur3_legend_refute`):** a line is dropped if any sign carries `#`, `[ ]`, `x` or `...`. `?`, `!`, `*` and `< >` marks are stripped and the sign kept.
- **Sign list (coordinator decision 1):** Oracc Global Sign List, CC0, https://oracc.museum.upenn.edu/json/ogsl.zip. In the repo at `experiments/certify_size_curve/raw/ogsl/ogsl.zip` (248,486 bytes), SHA-256 `46d8a29c11c351baa922c912c4472d6fb7ec7f79e76d4d473f29d58d4caf860f`. The study reads the member `ogsl/ogsl-sl.json`.
- **Lexicon (coordinator decision 2):** State Archives of Assyria online, CC0, https://oracc.museum.upenn.edu/json/saao.zip, member `saao/gloss-akk-x-neoass.json`.
  - The archive is 66 MB and is not in the repo. Its SHA-256 is `29bcf61b55ef291a97180f836ca620e13a1bcab802dad7ff64e2baf2e9d7a17f`.
  - **The study code loads only the derived file** `experiments/certify_size_curve/raw/saao/neoass_skeletons.tsv` (43,122 bytes, 3,632 skeletons), SHA-256 `3ab28cf9dae963f5930298e13e75ddde3790ea41ad5119f4c7faa76f14aa8823`.
  - It is built by `experiments/certify_size_curve/build_lexicon.py`, which checks the archive's hash, applies the rule in "Lexicon" and reads no text. The rebuild command and licences are in `experiments/certify_size_curve/raw/README.md`. Its columns are the skeleton, its consonant count, and the number of normalised forms and of headwords behind it. The study uses the first column only; the counts set no weight.
- M77 enters only as the list of text lengths used for chunking (`lb_certify` `m77_lengths`), as sealed.
- Linear B, its key and the Homeric lexicon enter only for abort A1.

## Readings, signs and the true key (frozen)
- **A sign token is one sign name.** Each syllabic reading in the transliteration is mapped to its Oracc sign name (CDLI ASCII is rewritten first: `sz` to š, `s,` to ṣ, `t,` to ṭ, index digits to subscripts). The text a decipherer would face is the sequence of sign names.
- **Determinatives** are signs with the empty value. Word-divider wedges (`/`) are removed and are not breaks: the text is undivided.
- **Breaks:** numerals, logograms (everything between `_ _`), upper-case sign names, compounds without a stated value, and any reading with no sign-list entry. Each unbroken run of 2 or more signs inside a line is a text. Its id is its tablet's id.
- **Alphabet: 11 letters.** Old Assyrian spelling does not separate voiced, voiceless and emphatic stops, so they are merged: P (b p), T (d t ṭ), K (g k q), S (s ṣ z), Š, M, N, L, R, H, W. The glides y and j and the glottal stop are dropped, as j and w were for Linear B.
- **The true key gives each sign one value:** the consonants, merged, of the reading it most often has in pool T. Ties go to the shorter value, then alphabetical order.
  - It is an oracle built from the editors' readings over the whole pool, held-out halves included. It uses no lexicon and no score.
  - 1.9% of tokens have a different value from their sign's modal one. They are scored with the modal value anyway.

### Measured: mapping

| pool | texts with text | lines kept | lines dropped | keyed sign tokens | logogram tokens | numeral tokens | sign types | reading types | signs for 90% of tokens |
|---|---|---|---|---|---|---|---|---|---|
| **T** | 4,435 | 73,135 | 27,234 | 445,733 | 63,111 | 23,015 | 207 | 459 | 55 |
| L | 1,009 | 18,307 | 7,532 | 120,265 | 14,900 | 5,411 | 175 | 370 | 54 |
| Q (uncertain period; sensitivity only) | 87 | 189 | 1,120 | 1,143 | 158 | 38 | 90 | 149 | 51 |
| Old Babylonian letters (not used; v1 count) | 2,265 | 26,677 | 23,230 | 185,576 | 17,715 | 2,647 | 271 | 570 | 66 |

| pool | key purity, 11 letters | key purity, unmerged | signs by consonant count 0 / 1 / 2 / 3+ | token share 0 / 1 / 2 / 3+ | runs of ≥ 2 | tokens in them | tablets |
|---|---|---|---|---|---|---|---|
| **T** | 0.981 | 0.892 | 13 / 114 / 71 / 9 | 0.193 / 0.722 / 0.082 / 0.003 | 77,412 | 442,702 | 3,951 |
| L | 0.983 | 0.893 | 10 / 101 / 57 / 7 | 0.185 / 0.738 / 0.074 / 0.003 | 19,400 | 119,458 | 926 |

- Syllabic readings with no sign-list entry: 11 tokens in T, 1 in L, none in Q.
- Tables for T, L and Q are the v3 recount (uncertain-period rows out of T and L).
- Old Babylonian letters were counted as the fallback pool. They are not used: more sign types, lower key purity (0.958), and 47% of lines lost to damage.

## Lexicon (frozen)
- **Skeleton of a word = the consonants of a normalised form** in the glossary (every `norms` entry of every headword), with the text's merging, long vowels shortened, y, j and the glottal stop dropped, and **a doubled consonant written once**, because Old Assyrian spelling rarely writes doubling. This is the analogue of passing Homer through Linear B spelling rules.
- Entries whose part of speech is a name class (PN, DN, GN, RN and the like) or a numeral are left out. A claimant would not hold a names list.
- **Word list W:** skeletons of LMIN to LMIN + 3 consonants, as `lift_score` (4 to 7).
- The study loads the skeletons from the derived file named in "Data" and checks its hash (abort A7).
- **The primary lexicon is not built from the test text or from any Old Assyrian text.** The one exception in the study is the record-only ceiling lexicon, defined under "Kill tests".

### Measured: density (11 letters)

| lexicon | entries | skeletons | density at 3 | at 4 | at 5 | rule LMIN | W (4 to 7) | role |
|---|---|---|---|---|---|---|---|---|
| Homer (sealed bench) | n/a | 10,491 | n/a | 0.177 | 0.014 | 4 | 9,636 | reference |
| **Neo-Assyrian (SAAo), normalised forms** | 4,166 | 3,632 | 0.524 | **0.110** | 0.006 | **4** | **2,815** (1,612 / 896 / 259 / 48) | **primary** |
| Standard Babylonian (SAAo) | 2,171 | 1,768 | 0.407 | 0.051 | 0.002 | 4 | 1,121 | not run |
| Neo-Babylonian (SAAo) | 1,981 | 1,911 | 0.398 | 0.054 | 0.002 | 4 | 1,267 | not run |
| four SAAo dialects pooled | n/a | 4,786 | 0.577 | 0.141 | 0.008 | 4 | 3,888 | not run |
| Old Babylonian literary (akklove) | 756 | 720 | 0.211 | 0.017 | 0.001 | 3 | 626 (3 to 6) | not run |
| Rimanum Old Babylonian (on disk) | 223 | not counted | | | | | | too thin |

- The primary lexicon is the same dialect line as the text (Assyrian), about 1,100 years later, and largely letters. Homer stands about 500 years after the Linear B tablets.
- **Known mismatch:** Old Assyrian nouns end in -m (mimation); Neo-Assyrian ones do not. 7.9% of the primary skeletons end in M, against 32.9% in the Old Babylonian glossary. The word model can absorb a stray M as a single-consonant unit. No rule adds one.

## Text shape and the size ladder (frozen)
- Every run in pool T is cut into chunks with lengths drawn from M77 seals (`lb_certify` `chunk`).
- **One tablet order:** tablet ids sorted as strings, then shuffled once with the study seed. Chunks follow their tablet.
- **Block b of size s** (s in u) is the next s × 2,300 chunks in that order, starting where block b − 1 of that size ended. Blocks of one size share no tablet except at one cut edge. Block j of size 2s contains blocks 2j and 2j + 1 of size s, so the ladder is nested.
- **Split, nested by hash (v2):** a tablet is held out if CRC32 of the ASCII string `ho:` + its id is odd, and is development text otherwise. No seed.
  - A tablet therefore has the same role in every block of every size that contains it. The development half of a block contains the development halves of the blocks nested in it, and no position is held out at one size and trained on at another.
  - The halves are close to equal, not exactly equal.
  - The development half trains everything. The held-out half is scored. The split is by tablet, which is stricter than `lift_score`'s split by line.
- **Chains.** A chain is one top-size block with the blocks nested in it that start at the same tablet: 16 u block j, 8 u block 2j, 4 u block 4j, 2 u block 8j, 1 u block 16j. There are three chains.
- **Sizes and draws:**

| size | chunks | tokens (median) | disjoint blocks in T | real draws used | pass bar | role |
|---|---|---|---|---|---|---|
| 1 u | 2,300 | 7,998 | 53 | 20 | ≥ 16 of 20 | graded |
| 2 u | 4,600 | 16,020 | 26 | 20 | ≥ 16 of 20 | graded |
| 4 u | 9,200 | 32,056 | 13 | 13 | ≥ 11 of 13 | graded |
| 8 u | 18,400 | 64,006 | 6 | 6 | ≥ 5 of 6 | graded |
| 16 u | 36,800 | 127,760 | 3 | 3 | 3 of 3, each with the one-sided bound | graded; the top of the ladder |
| 32 u | 73,600 | 255,332 | 1 | 1 | none | **record-only (v2)** |

- Bars are 80% of draws, rounded up, as `lift_score` F2 already words it.
- **The 32 u cell is one draw and grades nothing.** It has no K1, enters no reading and no bound, and is reported in one line.

### Clustered standard error and the one-sided bound
- **Clustered SE.** For a mean x̄ of per-position values x_i over n positions that sit in C held-out tablets: SE_cl = sqrt( C / (C − 1) × Σ over tablets c of (Σ over i in c of (x_i − x̄))² ) / n. Positions in one tablet are not treated as independent. A planted chunk takes the tablet id of the real chunk whose place it fills.
- **Gain and control bars at 16 u** (fewer than 5 disjoint draws): a draw meets a gain bar only if G − 1.645 × SE_cl ≥ 0.02. A control is under its bar only if its G + 1.645 × SE_cl ≤ 0.005. At 1 to 8 u the sealed point rule is used and the same bounds are reported.
- **Bar C, at every graded size.** For permuted lexicon j, Δ_j is the mean over the draw's clean positions of [log p_S(true sign) under the true lexicon − log p_S(true sign) under permuted lexicon j]. This equals G(true lexicon) − G(permuted j) on the same positions. Its one-sided bound is L_j = Δ_j − 1.645 × SE_cl(Δ_j).
  - **1 to 8 u:** a draw passes bar C if Δ_j > 0 for all five j (the sealed rule: the true-lexicon G is above the largest permuted G). L_j is reported for every draw and grades nothing.
  - **16 u:** a draw passes bar C only if L_j ≥ 0 for all five j, that is, each paired difference is at least 1.645 clustered standard errors above zero. All five must hold; no correction for five tests is made, which errs on the strict side.
  - K0b's planted cells (10 plants at each size) use the sealed rule at both sizes and report L_j.

### Fixed position sets (record-only; v2)
- The clean share falls as the corpus grows, so G at different sizes is taken over different positions. To give a curve on the same positions, each chain reports two fixed sets, taken from its 1 u block:
  - **Set F1:** every held-out position in a chunk of ≥ 4 signs of the chain's 1 u block that is clean against that block's own development half.
  - **Set Ftop:** the positions of F1 that are also clean against the development half of the chain's top-size block (16 u; 8 u after F7). Development halves are nested, so these positions are clean at every size.
- At each size on the chain, the true key's mean gain over F1 and over Ftop is reported, with the trigram, the word model and λ* fitted at that size. The same positions are scored at every size; only the training text grows.
- F1 at larger sizes includes positions that are no longer clean. That is stated beside it. Ftop is expected to be thin (about 400 positions a chain).
- These numbers grade nothing and enter no reading. They are listed beside the graded curve.

### Measured: shape (pool T; median of three tablet orders, range of clean positions in brackets)

| size | tablets | held-out positions in chunks ≥ 4 | clean held-out positions | clean share | clean positions, one development fold | sign types | top-50 bigram share | distinct chunks |
|---|---|---|---|---|---|---|---|---|
| 1 u | 73 | 2,330 | 1,614 (1,485-1,874) | 0.68 | 426 | 131 | 0.248 | 0.80 |
| 2 u | 148 | 4,768 | 2,725 (2,222-2,729) | 0.54 | 653 | 142 | 0.238 | 0.74 |
| 4 u | 307 | 9,916 | 4,221 (3,692-4,380) | 0.42 | 906 | 156 | 0.237 | 0.66 |
| 8 u | 596 | 19,232 | 5,668 (5,182-6,028) | 0.30 | 1,061 | 167 | 0.238 | 0.59 |
| 16 u | 1,200 | 38,458 | 7,536 (6,829-7,979) | 0.20 | 1,464 | 175 | 0.237 | 0.51 |
| 32 u | 2,388 | 73,959 | 8,675 (8,379-8,680) | 0.12 | 2,083 | 190 | 0.234 | 0.44 |

- **This is the v3 recount, on pool T without the uncertain-period rows.** Removing 87 texts changes the three random tablet orders, so every cell moved. The 1 u median moved from 1,366 to 1,614 (18%) on order noise alone. A median of three orders is a rough number, and abort A2's tolerance on these counts is set to 25% for that reason (v2: 15%).
- **These counts were made with a seeded half-and-half split, not the hashed split of v2.** The hashed split was not counted. This is the second reason for A2's tolerance.
- Mean chunk length 3.47 signs; 3.08 consonants per chunk (Linear B R1: 2.51); 41% of chunks have 4 or more signs.
- **The clean rule bites harder as the corpus grows:** the clean share falls from 0.68 at 1 u to 0.20 at 16 u and 0.12 at 32 u. This is a property of the frozen rule and would hold for any corpus. The graded G is not corrected for it; the fixed sets above are the check.
- The 1 u clean count (1,614; range 1,485-1,874) is near Linear B's sealed 1,376.
- Top-50 bigram share 0.234-0.248 sits between Linear B (0.207-0.223) and M77 (0.298).

## Frozen scoring (from `lift_score`, unchanged)
Taken word for word from `docs/prereg/lift_score.md`, "Frozen scoring", with only the script-specific items below changed.
- **Unchanged:** masking (one sign at a time, every position of every clean held-out chunk of ≥ 4 signs; clean by `corpus.build._close`); candidates (every sign type in the draw); the baseline trigram B; the word model (window likelihood with whole words, single consonants and prefix, suffix and infix fragments; 15 EM rounds from uniform p and ρ = 0.5; α = 0.01); LLR; S(c) = B(c) + λ × cov(c); the gain **G** (mean log-probability gain of the true sign, nats per clean position); the λ grid 0, 0.25, 0.5, 1, 2, 4; five development folds; the 0.01-nat margin for λ* > 0; the dose statistic **D**; the Markov filler (`lb_certify` `markov`, order 1 on signs); the dilution by bisection to within 0.005 of the target D in at most 12 steps.
- **Changed, because the script changed:**
  - alphabet: 11 letters in place of 10;
  - word list W: the primary lexicon's skeletons of 4 to 7 consonants (2,815);
  - folds: CRC32 of the tablet id mod 5 (the split unit here is the tablet);
  - N1 shuffled keys: the sealed `lb_shape_ladder` shuffle (values permuted within frequency bins of 10 inside each consonant-count class), **5 keys per draw** in place of 20 (coordinator decision 6). **The shuffled-key control bar is computed on those 5 keys and on nothing else:** a draw is under the bar if the median of its 5 shuffled-key gains, that is the third largest, is at most 0.005 nats. No sixth key is drawn, none is dropped, and no key from another draw is pooled in. At 16 u the one-sided bound is applied to that median key's G. The maximum of the 5 is reported and grades nothing;
  - plant spelling: a consonant is written with a one-consonant sign of exactly that value, drawn by sign frequency in the block; zero-consonant signs follow at the block's rate.
- **Changed, because the size changes (v2): the plant's vocabulary grows with the text.**
  - For plant k, W is put in one seeded random order. The plant at size s uses the first **min(500 × s, |W|)** words of that order, with weights 1 / rank: 500 words at 1 u, 1,000 at 2 u, 2,000 at 4 u, and all 2,815 from 8 u up.
  - The larger language contains the smaller one, with the same ranks. At 1 u the plant is `lift_score`'s 500-word plant.
  - **Chosen over keeping 500 words at every size.** A fixed 500 words at 16 u would repeat each word about 16 times as often as at 1 u, so the planted curve would measure a small closed vocabulary learned by heart. Nothing in the generator, the dilution or F2 depends on the count of 500, so nothing breaks.
  - Consequence, stated: along the planted curve the vocabulary changes as well as the size. The planted curve is "a language whose vocabulary grows with its corpus", not "one 500-word language".
- **Reported on every cell and key, grading nothing: Hit@1 and Hit@1 lift (the 2027-clause measure),** Hit@5, mean reciprocal rank, SE of G (per position and clustered), λ*, ρ, D, the trigram's own Hit@1, and the number of clean positions.
- **Permuted-lexicon D (record-only; v2).** At each size, D of the true key under each of the five letter-permuted lexicons is reported on the real development half of every draw, beside D under the true lexicon. `lift_score` found D was not specific to the lexicon on plants (a random lexicon gave 0.07-0.10). This shows whether the same holds on real text and whether it changes with size. It sets no dose and grades nothing. It is computed with the K2 cells, after all K1 targets are on disk.

## Kill tests, in this order (strongest first)
All plants are synthetic and their answers are known by construction. K0 sees no real-text gain and no real-text D.

### K0, the planted known answer
**K0a. The 1 u result of `lift_score`, reproduced on the new script.**
- Full dose (w = 1), 5 plants at 1 u. Every K0 plant k is built on block (k − 1) mod the number of blocks of its size; "draw" in the seeds is k. True key **G ≥ 0.10 in 5 of 5**; the same key on the unigram scramble **G ≤ 0.005 in 5 of 5**; five shuffled keys, **median G ≤ 0.005 in 5 of 5**. This is `lift_score` K0 with its bars.
- Low dose (**w = 0.25**), 20 plants at 1 u, true key only. **Known answer: a miss, fewer than 16 of 20 at G ≥ 0.02.** This is the failing cell. In the `lift_score` pilot a quarter dose gave G of 0.027, 0 and 0.
- Full dose misses: stop. The score does not carry to this script, and nothing is learned about size.

**K0b. A pass must appear at a planted larger size.**
- The same low dose, 10 plants each at 4 u and 16 u, built on real blocks' shapes (block k mod the number of blocks), with the vocabulary of that size (2,000 and 2,815 words).
- **Gain bar: at 16 u, true key G ≥ 0.02 in ≥ 8 of 10.**
- **Control bars at 4 u and at 16 u, each in ≥ 8 of 10:** unigram scramble G ≤ 0.005; median G of five shuffled keys ≤ 0.005; bar C against five letter-permuted lexicons (sealed rule).
- **K0c, no language at all.** Five pure-filler texts (w = 0) at 16 u. True key **G ≤ 0.005 in 5 of 5.** The filler is an order-1 sign chain, which the trigram contains, so any gain here comes from class smoothing and not from a language.
- K0b and K0c use point rules, not the one-sided bound: plants are not short of draws.

**Why this K0.**
- It is the cheapest test that can kill the study's premise before any real-text number exists. The premise is that more text turns an invisible dose into a visible one without also lighting up the controls.
- If the gain bar fails, a real-text null at 16 u would mean nothing: even a planted language stays hidden. If a control bar fails, a real-text pass at that size would mean nothing: keys or lexicons with no language pass too.
- It is a harder test than `lift_score` K0, which every reader now knows passes. The expected weak point is the controls at 16 u, not the gain.
- K0 does not use the real dose. K1 does that, and needs the first real-text number.

### K1, power at the true key's own dose, per graded size
- As `lift_score` K1, at 1, 2, 4, 8 and 16 u. The target for a plant is D of the true key on the real development half of its block. It sets a dose and grades nothing. All targets are written to disk before any K1 gain is computed.
- Plants: 20 at 1 u and 2 u; 10 at 4 u, 8 u and 16 u. None at 32 u.
- **Bar: G ≥ 0.02 in ≥ 80% of plants** (16 of 20; 8 of 10).
- A size that meets the bar is **powered**. A size that misses is **unpowered**. Its real cells still run once.

### K2 and K3, real text, per size
- **K2 controls** (as `lift_score` K2): true key on the unigram scramble, G ≤ 0.005; five shuffled keys, median of the five G ≤ 0.005. Each at the size's pass bar, with the one-sided bound at 16 u.
- **Bar C:** as defined under "Clustered standard error and the one-sided bound", at the size's pass bar.
- **K3:** true key, **G ≥ 0.02**, at the size's pass bar, with the one-sided bound at 16 u.
- All graded sizes run, smallest first, whatever the smaller sizes gave. A curve is the product. The 32 u cell runs last, record-only.

### Ceiling lexicon (record-only; v2)
- **Kept by coordinator decision 2** as the bound on the "lexicon too distant" risk.
- **Purpose.** A null with the Neo-Assyrian lexicon cannot tell "too little text" from "too distant a lexicon". This arm asks what the same score gives with the closest lexicon that could exist: Old Assyrian words themselves. No claimant could hold it. It is an upper bound.
- **How it is built, for one block:**
  - Source: every kept line (frozen drop rule) of every pool T tablet that is **not in the block**, neither in its development half nor in its held-out half.
  - A word is one space-separated group of hyphen-joined readings on a line. It is used only if every part is a syllabic reading with a sign-list entry.
  - **Excluded:** any word that holds a logogram, a numeral, a determinative, an upper-case sign name or a compound; any word broken by the drop rule; words are never joined across a line end.
  - Its skeleton is the true key's values of its signs, in order. So it follows the text's conventions exactly, modal values included.
  - Skeletons of 4 to 7 consonants are ranked by the number of distinct source tablets they occur in, then by token count, then alphabetically.
  - **Size match:** at each length the top-ranked skeletons are kept, up to the primary lexicon's count at that length (1,612 / 896 / 259 / 48). If fewer exist, all are kept and the shortfall is reported. The ceiling list therefore has the primary list's density at every length, or less.
- **Names are not removed.** They cannot be told apart without a names list, and they are part of what makes this a ceiling.
- **What runs:** the true key's G (the K3 cell) and bar C against the same five letter permutations applied to the ceiling list, at **1, 4 and 16 u**, on the same draws as K3.
- **It grades nothing and changes no reading.** Its numbers are printed beside the main curve under the frozen sentence in "Readings".
- Count seen before sealing (label-free, whole pool T without the uncertain-period rows, no block left out): 146,597 such word tokens; 1,985 / 1,824 / 733 / 195 skeleton types at 4 / 5 / 6 / 7 consonants; density 0.136 at 4. The size match can be met at every length on the whole pool; outside a 16 u block length 4 may fall short.

### Uncertain-period sensitivity check (record-only; v3, coordinator decision 7)
- **Purpose.** Uncertain dating must not be able to decide the verdict. Set Q is out of every graded cell. This check shows what putting it back would have done.
- **Set Q** is fixed in "Data": the catalogue rows with period exactly "Old Assyrian (ca. 1950-1850 BC) ?" that pass pool T's object and genre filters, under the same drop and language rules. All of Q is used, every time.
- **Where.** At 1 u (20 draws), where Q is about 14% of a block, and at the top graded size that ran (16 u, 3 draws; 8 u, 6 draws, after F7), where it is about 1%.
- **How, for one draw:**
  - Q's runs are chunked once for the whole study with their own seed. All of Q's chunks are added to the block.
  - A Q tablet is held out or development text by the same hash of its id as any tablet, and takes its fold from the same hash.
  - Signs take their values from the true key, which is built on pool T alone and is not rebuilt. A Q sign with no value in that key is a break.
  - The trigram, the word model and λ* are fitted again on the enlarged development half. The clean rule is applied again to the enlarged halves.
  - One cell is scored: the true key with the primary lexicon, on the enlarged held-out half.
- **Reported:** per draw, G with Q and G without (the K3 cell); per size, the two medians, their difference, the count of draws at or above 0.02 with Q, and whether the K3 bar's verdict at that size would differ.
- **It grades nothing.** No control, plant, K1 or K4 is run with Q. No label, reading or bound uses it. If the K3 verdict would differ with Q, that is stated and the graded verdict stands.

### K4, keys fitted to noise (only at the first size that shows)
- **Coordinator decision 5:** K4 runs once, at s\*, the smallest size labelled "shows", and only under reading B. It is not run at any other size, whether or not that size shows.
- As `lift_score` "Certify reading": 9 N2 keys and 3 N3 keys per draw, bars A and B at that size's pass bar.
- Without K4, "shows" is not "certifies".

## Calibration fallbacks (written before any calibration)
Calibration here means: the low dose of K0, the λ grid, the K1 dilution, the plant, and the top of the ladder. **These rules are the only changes allowed. Each is applied at most once and logged. Any other change after the first gain of any study cell is seen makes the study INVALID:** to the word model, α, the EM start or round count, the grid, the 0.01 λ margin, the statistic, any bar, the clustered SE or the one-sided bound, the masking, the clean rule, the trigram, the plants or their vocabulary rule, the filler, the dose statistic or its tolerance, the alphabet or its merging, the key, the lexicon or its skeleton rule, the ceiling lexicon's build, LMIN, the pool, the tablet order, the hashed split, the blocks, the chains, the fixed position sets, the sizes, which sizes are graded, the number of draws, the number of shuffled keys, set Q or its use, the permuted lexicons, the seeds, or anything else this document fixes. An invalid study is labelled so and is not rerun under this name.

**Every test is one-sided in the predicted direction:** gains are tested for being at or above their bar, controls for being at or below theirs, and bar C for the true lexicon being above the permuted ones. No two-sided test is used.

- **F1, grid edge** (as `lift_score`). If λ* = 4 for the true key in 3 or more of the 5 full-dose K0a plants, the values 8 and 16 are added for every key in every cell. K0a is not regraded.
- **F2, dose out of range or unbuilt** (as `lift_score`, per size). A target below the plant's D at w = 0 (minus 0.005) is a K1 miss logged "no dose above filler". A target above the plant's D at w = 1 uses w = 1 and is flagged. A plant not landed in 12 steps is unbuilt; a size needs 90% of its plants built, and its bar is 80% of the built ones. A size with fewer than 90% built is unpowered.
- **F3, plant too easy for the trigram** (as `lift_score`). If the trigram's Hit@1 on a full-dose K0a plant exceeds 60%, the vocabulary rule becomes min(2,000 × s, |W|) once, before any K0 gain is computed, and stays so.
- **F4, thin size.** A draw with fewer than 900 clean positions is kept and flagged. A size whose median falls below 900 is dropped from the ladder.
- **F5, the low dose does not fail at 1 u (coordinator decision 4: 0.25, with 0.125 as the one fallback).** If the w = 0.25 plants pass (≥ 16 of 20) at 1 u, the low dose becomes 0.125, once, with fresh seeds, before any K0b plant is built. If that also passes, stop and redraft: no failing cell exists to rescue.
- **F6, cost, projected from the first 16 u plant (v2).** K0b builds its 16 u plant 1 first and times its 12 key cells. The whole study is then projected from that timing and the cell counts in "Cells".
  - Above 60 processor-hours: the 32 u record-only cell and pool L are dropped.
  - Still above 90 processor-hours without them: stop and redraft before any further gain is computed.
  - The projection uses time only. The gains of that first plant are not read for it, and the plant stays in K0b as plant 1.
- **F7, ladder cut after a 16 u control miss (v2).** If the K0b gain bar passes, every K0b control passes at 4 u, and a K0b control at 16 u or K0c misses, the ladder is cut to 1, 2, 4 and 8 u.
  - No 16 u or 32 u real cell runs, and no K1 at 16 u. The ceiling arm runs at 1 and 4 u only. The sensitivity check runs at 1 u and 8 u. The top size for chains, Ftop and N is 8 u (64,006 tokens).
  - 8 u has no planted control test of its own. It counts as usable only if its real-text K2 bars hold, which the per-size labels already require.
  - Nothing else changes.
- **Not permitted, as examples:** raising the low dose after a K0b miss; another filler; a second or backup score; a relative statistic in place of G; another lexicon, a pooled lexicon, or a mimation rule; grading the ceiling arm, the 32 u cell, a fixed-set gain or the sensitivity check; moving a Q tablet into pool T; more or fewer than 5 shuffled keys; another alphabet; reading-level tokens in place of signs; pool L or Old Babylonian letters in place of pool T; overlapping draws to raise a count; dropping a size after seeing its gain; moving a bar; grading Hit@1 in place of G; rerunning K0.

## Readings (frozen; worded for the bench)
- T(s) is the median token count at size s. **N is the top graded size that ran:** 127,760 tokens (16 u), or 64,006 (8 u) after F7. A size dropped by F4 is left out of everything below.
- Readings are taken in two steps. Step 1 has six outcomes; exactly one applies, the first in the list whose condition holds. Step 2 is reached only from outcomes 5 and 6.

### Step 1: K0
1. **K0a full dose misses** (its gain bar or either control): "The word-and-fragment score does not pass its planted test on Old Assyrian. Nothing is learned about size." Nothing else runs.
2. **K0a low dose passes at 0.25 and again at 0.125 (F5):** "No failing cell to rescue at 1 u: this script's shape is easier than Linear B's. Redraft." Nothing else runs.
3. **K0b gain bar misses, whatever the controls did:** "Even a planted language at the K0b low dose (0.25, or 0.125 if F5 applied) stays hidden at 128,000 tokens. More text does not rescue this score. The restoration route stays closed up to that size for this score; a real-text null would add nothing." **This reading wins when the gain bar and a control both miss.** The control miss is added as one sentence: "A control with no language also passed its bar at (size)." Real K3 cells at 1 u and 16 u run once, record-only. Nothing else runs.
4. **K0b gain bar passes and a K0b control misses at 4 u** (whatever happened at 16 u): "The gain is not specific beyond one draw. The size question cannot be asked with this score." Nothing else runs.
5. **K0b gain bar passes, every 4 u control passes, and a 16 u control or K0c misses:** "At 128,000 tokens the score gains for keys, lexicons or texts with no language. The usable range of this score ends below that size." F7 applies. Go to step 2 with the ladder 1, 2, 4, 8 u.
6. **Every K0 bar passes.** Go to step 2 with the ladder 1, 2, 4, 8, 16 u.

### Step 2a: one label per graded size
Each size gets exactly one label, from K1, K3 and the controls (K2 and bar C taken together):

| K1 | K3 | K2 and bar C | label |
|---|---|---|---|
| passes | passes | both pass | **shows** |
| passes | passes | either misses | **not specific** |
| passes | misses | any | **does not show** |
| misses | passes | any | **seen without planted power** |
| misses | misses | any | **unpowered** |

- **Powered** means K1 passed at that size. The first three labels are the powered ones.
- **"A larger size that is unpowered"** means a size above s* whose K1 missed, whatever its real cells gave (labels "unpowered" and "seen without planted power"). It neither confirms nor breaks a threshold. Only a powered larger size can break one.
- "Seen without planted power" is logged "plant harsher than real text at this size". It never counts as showing.

### Step 2b: the curve reading
Exactly one applies, the first in the list whose condition holds.

- **A. No size is powered.** "Unpowered at every size. At the lexicon fit the true Old Assyrian key actually reaches with a Neo-Assyrian lexicon, a planted language does not raise restoration by 0.02 nats per sign with up to N tokens. The route needs more than N tokens or a closer lexicon; this study cannot say which." The D values per size are reported. Sizes "seen without planted power" are listed. No bound statement is made.
- **B. Some size shows, and no powered size above the smallest showing size s\* has the label "does not show" or "not specific".** "On Old Assyrian with a Neo-Assyrian lexicon, the true key's fit to the lexicon shows from about T(s\*) sign tokens in M77-length chunks."
  - Then one of: "The size below did not show." / "The size below was unpowered." / "It shows at the smallest size run."
  - Then, if any: "Sizes (list) above it were unpowered and neither confirm nor break this."
  - Then the K4 result at s\*: "Keys fitted to noise by these two fitters do / do not show it too."
- **C. Some size shows, and a powered size above s\* does not.** "Not stable: the gain appears at T(s\*) and is gone, or not specific, at T(s′). No threshold is stated." K4 does not run.
- **D. No size shows, and some powered size is "not specific".** "From T(s) a gain exists but it is not specific to the key or the lexicon. No size up to N shows the true key's fit." No bound statement is made.
- **E. No size shows, and every powered size "does not show".** "No size up to N tokens shows the true key's fit, though a planted language at the same dose is visible from T(s_plant)", where s_plant is the smallest powered size. Then exactly one of the two bound statements below.

- **Added to every step 2 reading, always:** "This is one script, one lexicon and an oracle key. It is an order of magnitude for other scripts, not a threshold. M77 holds 13,398 tokens."
- **Added to every step 2 reading, deciding nothing:**
  - "With a lexicon of Old Assyrian words from other tablets, which no claimant could hold, the true key's G was (values) at 1, 4 and 16 u, and bar C held in (counts)."
  - "On fixed positions the gain was (values per size) on F1 and (values) on Ftop."
  - "The one 32 u draw gave G (value)."
  - "With the 36 tablets of uncertain period added, the true key's median G was (value) against (value) at 1 u, and (value) against (value) at (top size). The K3 verdict at those sizes would / would not have differed."
- **Coverage.** Step 1 is an ordered list with a catch-all (6). The step 2a table covers all eight combinations of its three columns. Step 2b splits on "is any size powered" (A), then "does any size show" (B and C against D and E), then one yes-or-no each. So every outcome has one reading and no outcome has two.

### Bound and extrapolation rule (fixed now; used only in reading E)
- m(s) is the median over real draws of the true key's G at graded size s.
- **Flat case:** m(s) = 0 at every graded size (λ* = 0 in most draws everywhere). Statement: "the need is above N tokens by an unknown factor". **No extrapolation is made.** A row of zeros has no slope.
- **Rising case:** m(s) > 0 at three or more graded sizes, and the least-squares slope of m on log2 T(s) over those sizes is positive. The line is extended to 0.02. If it crosses at or below 4 × N, the crossing is reported as "extrapolated, not shown: about X tokens". If it crosses above 4 × N: "above 4 × N; not extrapolated further".
- Any other pattern: the flat-case statement.
- The 32 u draw is not used in the fit.
- As a check on the rule, the line through the low-dose plant medians at 1 u (K0a) and 4 u (K0b) is extended to 16 u, and its miss against the measured 16 u median is reported. This grades nothing.
- No extrapolation is ever worded as a result, and none is carried to Indus as a number of tokens needed.

## Indus rule
- **No Indus step is run in this study.** M77 supplies text lengths only.
- No Indus key (claimed, fitted or shuffled) is scored on any text. No M77 sign is masked or restored. The study code must not load `splits_v2` or any key file from the claim bench.
- No outcome licenses a run on Indus. That would need its own prereg and the coordinator's OK.

## Cells

| cell | text | keys and lexicons | sizes | draws | role |
|---|---|---|---|---|---|
| A1 | Linear B plant, `lift_score` K0 draw 1 | true | 1 u | 1 | abort check |
| K0a full | plant, w = 1, and its unigram scramble | true; 5 N1; 5 permuted lexicons (record-only) | 1 u | 5 | graded |
| K0a low | plant, w = 0.25 | true | 1 u | 20 | graded |
| K0b | plant, w = 0.25, and its scramble | true; 5 N1; 5 permuted lexicons | 4 u, 16 u | 10 each | graded |
| K0c | filler only, w = 0 | true | 16 u | 5 | graded |
| K1 | real development half (D only); plant at matched D | true | 1 to 16 u | 20, 20, 10, 10, 10 | graded |
| K2 | real, and its unigram scramble | true; 5 N1; 5 permuted lexicons (G and D) | 1 to 16 u | 20, 20, 13, 6, 3 | graded |
| K3 | real | true | 1 to 16 u | 20, 20, 13, 6, 3 | graded |
| K4 | real | 9 N2, 3 N3 | smallest size that shows | that size's draws | graded |
| 32 u | real, and its unigram scramble | true; 5 N1; 5 permuted lexicons | 32 u | 1 | record-only |
| ceiling | real | true with the ceiling lexicon; its 5 permuted copies | 1 u, 4 u, 16 u | 20, 13, 3 | record-only |
| fixed sets | real, sets F1 and Ftop | true | every size on each chain | 3 chains | record-only |
| pool L | real, letters only | true; K2 controls | 1 u, 2 u, 4 u | 14, 7, 3 | record-only |
| sensitivity | real, with all of set Q added | true | 1 u, top graded size | 20, 3 | record-only |

## Aborts
- **A1.** The study code, pointed at Linear B and Homer, does not reproduce the sealed `lift_score` K0 draw-1 gain to 1e-9: stop.
- **A2.** The sealed code recomputes the "Measured" tables before any gain. Stop and redraft if: a pool T count differs (4,435 texts; 73,135 lines; 445,733 tokens; 207 sign types); set Q differs (36 texts with a kept line; 1,143 tokens); key purity differs from 0.981 by more than 0.005; the primary lexicon's density at 4 differs from 0.110 by more than 0.01, or its rule LMIN is not 4; the number of blocks at any size differs; or a median clean count differs from its table value by more than 25% (the scratch count used three tablet orders and a seeded split, not the sealed order and the hashed split; see the note under the shape table).
- **A3.** F2, F4, F5 and F6 stop conditions.
- **A4.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- **A5.** Any step would read an Indus key or restore an Indus sign: stop.
- **A6.** The window model does not sum to 1 (to 1e-9) over all strings of 1 to 4 consonants on 11 letters for the fitted K0a draw-1 model: stop.
- **A7.** `ogsl.zip` or `neoass_skeletons.tsv` in the repo does not match its SHA-256 in "Data": stop. The study code opens no other lexicon file and never opens `saao.zip`.
- **A8.** A ceiling lexicon would include a word from a tablet of its own block: stop.
- **A9.** A tablet of set Q appears in pool T, pool L, the true key's source, a ceiling lexicon or any cell other than the sensitivity check: stop.
- No rerun, no tuning, no fix tags after any gain is seen.

## Seeds
- Study base **20270201** (not `lift_score`'s 20270101, not `lift_certify`'s 20261201, not the pilot's 990000).
- Tablet order: base. Chunk lengths: base + 1. Chunk lengths for set Q: base + 2.
- **The split uses no seed:** CRC32 of `ho:` + tablet id, odd means held out. Development folds: CRC32 of the tablet id, mod 5. Nothing else is hashed.
- Plants, for size s and plant k: spelling base + 200,000 + 1,000 s + k; filler base + 300,000 + 1,000 s + k; dilution uniforms base + 400,000 + 1,000 s + k. The F5 rebuild adds 50,000 to each.
- Plant vocabulary order for plant k: base + 100,000 + k, the same at every size, so the vocabularies are nested.
- Unigram scrambles: base + 500,000 + 1,000 s + draw. N1 keys: base + 600,000 + 1,000 s + 10 × draw + j, j = 1..5. N3 starts and swaps: base + 700,000 + 1,000 s + 10 × draw + restart.
- Lexicon letter permutations: base + 800,000 + j, j = 1..5; five for the whole study, each a permutation of the 11 letters with no letter fixed. The same five are applied to the primary and to the ceiling lexicon.
- A1 uses the sealed `lift_score` seeds unchanged.

## Limits stated in advance
- **The expected result is a null.** On Linear B the true key's D was about zero. If the same holds here, K1 reports "no dose above filler" at every size and the answer is reading A, with no bound.
- **A null would not separate size from lexicon.** The lexicon is 1,100 years younger than the text, lacks mimation and merchant vocabulary, and holds no names, while Old Assyrian letters are full of names. The ceiling arm describes the other end of that range. It is record-only and cannot settle it.
- **The ceiling lexicon is generous in three ways:** same dialect, archive and century; built with the editors' word division; and spelled through the same key. Tablets outside a block can still share senders, names and formulae with it.
- **The draws at the top are few.** Three disjoint draws at 16 u. The tablet-clustered bound replaces the 16-of-20 logic there. Three of three is a weak count even so.
- **Size and clean share move together.** At 16 u only 20% of held-out positions are clean. The positions that survive are the ones least like the development text, so the graded sample gets harder as the corpus grows. The fixed sets describe this; they do not grade.
- **The planted curve changes vocabulary as well as size** (500 words at 1 u, 2,815 from 8 u). That is closer to a real corpus and is not a pure size dial.
- **The hashed split gives unequal halves** and is the same for every size, so a chain's results are not independent across sizes. Results at one size are independent across blocks only.
- **The key is an oracle** with one value per sign, taken from the editors' readings on the same pool. A decipherer's key would be worse. A pass is an upper bound.
- **The merge to 11 letters** raises key purity from 0.89 to 0.98 and lowers the information in every skeleton.
- **Old Assyrian is close to a syllabary** (55 signs give 90% of tokens). That makes it a fair stand-in for a syllabic script and a poor one for a script with many logograms. Logograms and numerals are cut out here; 16% of all tokens are lost that way.
- **The pool mixes genres** (letters, legal, administrative, untyped). The mix is constant across sizes in expectation; it is not controlled within a block.
- **The sensitivity check is small.** Set Q holds 1,143 tokens. At 16 u it can hardly move G; at 1 u it is one fixed addition to twenty blocks, so its twenty differences are not independent.
- **Five shuffled keys make a coarse control.** The median of five is the third largest; two keys with a gain can hide under it. The maximum is reported for that reason.
- **Plants are kinder in lexicon match and harsher in sign choice** than real text, as in `lift_score`. The low dose of 0.25 is a round number, not a matched one.
- **One script, one lexicon, one score.** The score was chosen on a Linear B pilot. Nothing here tunes it.
- **Not a threshold for Indus.** Token counts transfer as an order of magnitude at best.

## Cost
- At most 4 workers. Every stage runs detached with a pid file, under the Indus compute lock and `board/run.sh`.
- One key on one draw cost about 10 to 13 seconds for `lift_score` at 1 u. Scaled by clean positions, candidates and text size, the estimate here is about 20 seconds at 1 u, 60 at 4 u, 110 at 8 u, 220 at 16 u and 330 at 32 u. These are estimates and could be off by a factor of two. F6 replaces them with a measured 16 u timing.
- **Stage 1, K0:** about 10 processor-hours (16 u plants dominate), about 2.5 hours on 4 workers.
- **Stage 2, K1:** about 5 processor-hours (v1: 7; no K1 at 32 u).
- **Stage 3, K2 and K3 with the 32 u record cell:** about 12 processor-hours.
- **Ceiling arm (new in v2):** about 3 processor-hours (six lexicon cells a draw at 1, 4 and 16 u). **Fixed sets:** about half an hour. Permuted-lexicon D comes from cells that already run.
- K4 and pool L: about 2. **Sensitivity check (new in v3):** about 0.3 (20 cells at 1 u, 3 at 16 u).
- **Total: about 33 processor-hours** (v1: 31; plus about 3.8 for the new arms, minus about 2.4 for K1 at 32 u), **about 8 to 9 hours of wall time on 4 workers,** in three detached stages. F6 caps it.
- Outputs: small JSON files with per-draw summaries. No per-position arrays are saved; clustered SEs are computed in memory. Results are written to the repo's results folder, not to a temporary directory.

## Decisions
**Made by the coordinator, 2026-11-25. No question is open.**

1. **Sign list.** The Oracc Global Sign List (CC0) is added to the repo with its hash and source URL. Signs are the tokens.
2. **Lexicon.** The SAAo Neo-Assyrian glossary (CC0) is the lexicon. The Old Assyrian ceiling lexicon is kept, record-only, as the bound on the "lexicon too distant" risk.
3. **Pool.** The primary pool is all Old Assyrian tablets (pool T). Letters only (pool L) is record-only.
4. **Low dose.** K0's low dose is 0.25, with 0.125 as the one fallback, stated in advance (F5).
5. **K4.** It runs only at the first size where the fit shows.
6. **Shuffled keys.** 5 per draw. The control bar is the median of those 5 (stated under "Frozen scoring").
7. **Uncertain period.** The 159 "Old Assyrian ?" catalogue rows are excluded from the primary pool. They are run once as the record-only sensitivity check defined under "Kill tests", so that uncertain dating cannot decide the verdict. The count gate was recounted without them.
8. **Unit.** The `lift_score` unit is worded "2,300 chunks, about 8,000 tokens".

Settled earlier by the review of v1: the 32 u cell (record-only); the cut to 8 u after a 16 u control miss (F7); the plant vocabulary (grows with size).

**Made by the drafter in v3 and not asked for; the coordinator may strike it before sealing:** abort A2's tolerance on clean-position counts is 25% in place of 15%, because the recount moved the 1 u median by 18% on tablet-order noise alone.

## Before sealing
- The coordinator seals. A pre-seal check of v3, if wanted.
- `experiments/*/raw/` is ignored by the repo's ignore file. The sign list, the derived lexicon and the raw README are on disk but will not be tracked until an exception is added. The ignore file now excepts this folder; the files are tracked with the study.
- Code written and hashed after sealing, before any gain.

## Review log
- 2026-11-25: DRAFT v1 written. Not reviewed. Not sealed. No study code exists. Label-free counts only; no gain, D, λ* or lexicon match was computed on any text.
- 2026-11-25: Fresh review of v1 returned "FIX, then seal", 11 items.
- 2026-11-25: **DRAFT v2.** Not sealed. No study code exists. Nothing was scored for this revision; three label-free counts were added (uncertain-period rows, texts with no language line, Old Assyrian word-skeleton types) and are disclosed. Changes:
  1. Plant vocabulary is min(500 × s, |W|) words at size s, nested; chosen over a fixed 500, with the consequence stated.
  2. Ceiling lexicon arm added, record-only, at 1, 4 and 16 u: build rule, exclusions and size match fixed; abort A8.
  3. Permuted-lexicon D on real development text reported at each size, record-only.
  4. The 32 u cell is record-only, with no K1; the ladder is graded to 16 u and N is 127,354.
  5. Bar C at 16 u needs each paired difference to be at least 1.645 tablet-clustered standard errors above zero; the bound is defined and reported at every graded size. The 16 u gain and control bounds also use the clustered SE.
  6. Splits are nested by a hash of the tablet id. Fixed position sets F1 and Ftop are reported on each chain, record-only.
  7. F7 added (cut to 8 u after a 16 u control miss). F6 now projects cost from the first 16 u plant and has a stop at 90 processor-hours.
  8. Readings rewritten as an ordered step 1, a per-size label table and five curve readings: the K0b gain miss wins over a control miss; "a larger size that is unpowered" is defined; coverage is stated.
  9. Prior art: the unicity sentence reworded; Nuhn 2013 also solves the homophonic Zodiac-408.
  10. Disclosed: the prefix period filter and the decision to keep the 159 uncertain-period rows; 2 texts with no language line kept; the `riao.zip` and `projects.json` downloads and the header probes.
  11. Cost, decisions and this log updated.
- 2026-11-25: Coordinator decisions received (eight, listed under "Decisions").
- 2026-11-25: **DRAFT v3.** Not sealed. No study code exists. Nothing was scored. Changes:
  1. Decisions written in as coordinator-made; the open questions removed.
  2. Pool T's period match is exact. The uncertain-period rows form set Q, which is out of every graded cell and is run once as a record-only sensitivity check (1 u and the top graded size); abort A9.
  3. Count gate, mapping tables, shape table, ceiling count, A2 counts and N recounted label-free on the pool without those rows (4,435 texts, 445,733 tokens, 53.6 u). No gate verdict changed. A2's clean-count tolerance set to 25% (drafter's change, flagged under "Decisions").
  4. The shuffled-key control bar is stated as the median of exactly 5 keys per draw.
  5. K4 only at the first size that shows. Unit worded "about 8,000 tokens".
  6. Data: `ogsl.zip` added; `build_lexicon.py` added and run once on `saao.zip`; the derived `neoass_skeletons.tsv` and a raw README added. The study code loads only the derived file; A7 checks its hash.
  7. Scratch copies of the papers and of the unused archives deleted.
- 2026-11-25: pre-seal check of v3: four blocking fixes applied (K4 tied to reading B, K0 block/seed index, INVALID clause made total, ignore-file note) and one wording fix (K0b dose in reading 3). A2's 25% clean-count tolerance kept and disclosed (drafter's pre-seal change; the scratch counts used three tablet orders and a seeded split). The `saao.zip` hash was re-verified. Sealed as v4.
