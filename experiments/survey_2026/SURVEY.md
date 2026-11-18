# Survey 2026: floated ideas we have not yet tested

Survey agent, 2026-11-18. Files: `SURVEY.md` (this file), `survey.json` (ranked ideas), `raw/` (downloaded open-access PDFs and extracted text, untrusted, never executed).

Scope. Before searching I read what the project already covers: `experiments/literature/RESULTS.md`, `experiments/research_sweep/`, `site/news.json` (25 items), `docs/NEGATIVE_ATLAS.md` (all headings plus sections 4, 5, 6 and 10b in full), the README "What we can defend" table and `docs/HUMAN_LEADS.md`. Below, "atlas x.y" means a section of `docs/NEGATIVE_ATLAS.md`.

## Conclusion first: the five most promising testable ideas

The project has already closed most of the obvious routes. Only a few of the ideas floated in 2018-2026 are both new to the project and runnable on M77 or ICIT. They are below, ranked by (chance of a clear answer) × (what it would add) ÷ cost. All five can be run with data already on disk. None is a phonetic route.

1. **Which slot carries the object's function: a "header vs terminal" test.** This combines Born et al.'s proto-Elamite header method (EMNLP 2022) with Rao's four-part reading of patterned texts (2018): the prefix names an institution and the terminal names the function of the sealing or tablet. We already know the whole text predicts the object type (README #6). Nobody has asked which slot carries that signal. If the terminal slot carries it, that is an L1/L2 step: a slot class tied to a non-textual covariate on held-out data. Data in hand.
2. **Human-figure signs as counted labour units (Rao 2018).** Rao reads the "porter" and other "man + attribute" signs as categories of labour that get counted, as on proto-Elamite ration tablets. That predicts the human-figure block (Mahadevan's first signs, roughly M1-M47, list to be frozen after a drawing check) is preceded by numerals more often than matched signs, and is commoner on miniature tablets and tokens than on seals. Atlas 6.6 tested numeral-to-item spikes in general, not this class. Data in hand.
3. **Face specialisation on multi-face objects, borrowed from Cretan Hieroglyphic.** Civitillo, Ferrara and Meissner (eds., CUP 2024) distinguish the uses of signet seals from prismatic seals, and repeated "formulae" make up almost half of the seal material. The Indus version: on objects with several inscribed faces, one face carries a repeated formula and the others carry unique text, more often than independent faces would, and the effect grows with the number of faces. This partly overlaps shaunmortal F15 (tablet side 2) and atlas 5.1 P1, but the dose-response across face counts and object types is new. Data in hand (M77 `side`, ICIT multi-text objects).
4. **Fish signs as precious-commodity marks at lapidary sites (Mukhopadhyay 2023, 2025).** She argues that fish-sign inscriptions concentrate where gem and bead work happened, and her 2023 paper names Chanhu-daro and Lothal as bead and warehouse sites. That predicts a higher fish-family share at those two sites than at Mohenjo-daro, Harappa and Kalibangan, within object type. Atlas 10b.17 (craft assemblage, within site, power 0-4.5%) and 10b.5 (no large city-specific stock) argue for a small effect at best, so power is the main risk. Data in hand.
5. **Characteristic magnitude per counted sign, replicated out of sample (Born et al. 2025 on proto-Elamite).** Born et al. found that container-like signs carry consistently larger or smaller counts. The Indus version: per counted sign, the rank order of mean numeral value learned on M77 dev replicates on held-out texts and on ICIT post-1977 sites. This overlaps shaunmortal F2/F5 (complementary tall/short value sets) and atlas 6.5/6.6, so it is the weakest of the five on novelty, but it is cheap and would give an ordinal "size" scale for counted signs. Data in hand.

Not promoted to the top five:
- **Mahadevan & Bhaskar 2018 direction and topography signs.** The paper could not be opened, so its sign numbers are unknown.
- **Frenez 2026 "branding" and Green 2021 "collective governance".** Their text predictions are already closed by atlas 10b.14, 10b.5 and 5.7.
- **Rongorongo cross-readings and Tamburini's 2025 optimiser.** These are closed by atlas 1.4, 1.7, 1.8 and 1.9.

---

## Table of new sources

Read level:
- **Full** means I read the whole text or all of its methods and results.
- **Partial** means I read the abstract plus the sections named.
- **Abstract** means I read the abstract only.
- **Unverified** means I saw it only through search-engine snippets: the page returned 403 or a login redirect, so I did not open it. Unverified entries are listed so that a person can check them, not as evidence.

| # | Citation | URL opened | Read | One-line claim | Relevance |
|---|---|---|---|---|---|
| 1 | Born, Monroe, Kelley & Sarkar, "Sequence models for document structure identification in an undeciphered script", EMNLP 2022 | https://aclanthology.org/2022.emnlp-main.620.pdf | Full | Proto-Elamite "header" signs are confirmed without supervision: an HMM state found only at text start matches expert labels at precision 0.93 and recall 0.67, and a regression on Transformer attention to pre-numeral signs gets 92% (77% majority baseline). Signs in the first and second positions predict distinct information. | Method for idea 1. It gives a slot-localised known-answer design, and data at github.com/sfu-natlang/pe-headers (not opened). |
| 2 | Born, Monroe, Kelley & Sarkar, "Disambiguating numeral sequences to decipher ancient accounting corpora", CAWL 2023; arXiv 2502.00090 v2 (2025, corrects Englund 1996 values) | https://arxiv.org/abs/2502.00090 ; https://arxiv.org/pdf/2502.00090 | Full (methods, results) | Bootstrapped classifiers and checks of totals assign proto-Elamite numerals to number systems. Counts vary by content: M288 entries are always exactly 4× an adjacent M376 entry and 2× an adjacent M367~i entry (44 entries), and M288 and M263 have the largest and smallest capacity magnitudes. | Idea 5. The fixed-ratio idea also bears on atlas 5.1 P11. |
| 3 | Born, Monroe, Kelley & Sarkar, "Learning the character inventories of undeciphered scripts using unsupervised deep clustering", CAWL 2023 | https://aclanthology.org/2023.cawl-1.11.pdf | Partial (abstract, intro) | Image plus context clustering beats Sign2Vec on Cypro-Greek with about 2% of the parameters, and replicates expert proto-Elamite groupings. | Sign-list question. Already largely covered by `signlist_robustness` and atlas 7.7. A possible future positive control. |
| 4 | Rao, "The Indus script and economics: a role for Indus seals and tablets in rationing and administration of labor", in *Walking with the Unicorn* (Archaeopress 2018), 518-525; arXiv 1812.00049 | https://arxiv.org/pdf/1812.00049 | Full | The 1997 Harappa miniature tablets (numeral + sign on each side) were ration tokens. Human-figure signs ("porter", "man + wheels", "man + harrow", "man + tongs") are labour categories. Seals generated ration or wage tokens. A patterned text reads Prefix = institution, Medial = quantity, Core = commodity, Terminal = function of the sealing or tablet. | Ideas 1 and 2. Not previously cited anywhere in the repo. |
| 5 | Mukhopadhyay, "Semantic scope of Indus inscriptions comprising taxation, trade and craft licensing, commodity control and access control", *Humanities and Social Sciences Communications* 10:972 (2023), doi:10.1057/s41599-023-02320-7 | https://www.nature.com/articles/s41599-023-02320-7.pdf | Partial (sections on toponyms, weights, craft areas, Lothal sealings) | Seals cluster near lapidary, metal and shell workshops and near weights (e.g. Chanhu-daro bead factory, room 215: 14 weights, scale pans and seal C-22, after Mackay 1943). The paper argues against toponyms. Lothal sealing texts recur on Lothal seals (L-208/L-6, L-210/L-37). | Idea 4. The seal-with-weights co-location could be tested if the Mohenjo-daro registers list weights (data_ready false). |
| 6 | Mukhopadhyay, "Indus script's gemstone and precious shiny commodity related fish-signs, and Indus gemstone-word *maṇi*", SSRN 5079207 (2025, in press in the Chennai centenary proceedings) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5079207 (HTTP 403, not read) | Unverified | According to search snippets, fish-sign inscriptions occur in large numbers at lapidary workshops and jewellers' shops, so fish signs relate to gems and shiny goods. | Idea 4. The site list must come from the 2023 paper (#5), which I did open. |
| 7 | Civitillo, Ferrara & Meissner (eds.), *Cretan Hieroglyphic* (CUP 2024), introduction and ch. 1 (Ferrara) | https://www.cambridge.org/core/services/aop-cambridge-core/content/view/F6BAF70365CE3741F43487E1BAC43664/9781009490108int_1-12.pdf/introduction.pdf ; https://cris.unibo.it/retrieve/4d46baae-d5a6-4071-96b6-07acb6b83f2b/Cretan%20Hieroglyphic_CUP_ch1.pdf | Partial (intro; ch. 1 sections 1.1-1.4) | Repeated sign groups ("formulae") make up almost half of the material on seals but are rare on clay. Evans read them as "canting badges" tied to official roles. The volume says signet seals and prismatic seals had different uses (Valério and Civitillo chapters). | Idea 3. The claim that prisms carry formulae and 1-2-face seals carry names comes only from an Academia summary of Civitillo's seminar paper (unverified). |
| 8 | Tamburini, "On automatic decipherment of lost ancient scripts relying on combinatorial optimisation and coupled simulated annealing", *Frontiers in AI* (2025), doi:10.3389/frai.2025.1581129 | https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1581129/full | Partial (first 100k characters: methods and results) | Cognate matching on known pairs: Linear B/Greek 89.4%, Cypriot/Greek 86.3%, Luvian/Hittite 47.5%. There is no shuffled or planted null, and it is not applied to any undeciphered script. | Closed for Indus by atlas 1.8 and 1.9 (needs a known related language). Its known-pair benchmarks could be reused as positive controls. |
| 9 | Mair, "Decipherment of the Indus script: new angles and approaches", Language Log, Mar 2025 | https://languagelog.ldc.upenn.edu/nll/?p=68508 | Full | A survey post: Parpola rebus, Knorozov phonetic components, McAlpin Elamo-Dravidian, AI. Comments discuss checking methods for false positives. | Context only. No new testable claim. |
| 10 | Salgarella & Castellan, SigLA database paper | https://sigla.phis.me/paper.pdf | Partial | In Linear A, a sign's function is often inferable from position: logograms end an entry, after word-like sequences and before numerals. | Already the logic of `functional_reading`. No new test. |
| 11 | Gondwana, "Learning Indus script via Proto-Dravidian Gondi, clan-totem correlation and socio-cultural context", *Educational Development in Various Fields* (Kosmos, Nov 2026), doi:10.37722/EDIVF.2026201 | https://kosmospublishers.org/wp-content/uploads/2026/11/Learning-Indus-Script-via-Proto-Dravidian-Gondi-Clan-Totem-Correlation-and-Socio-Cultural-Context.pdf | Partial (abstract, intro, chief-title section) | Gondi readings of seals (e.g. M-260a as a phratry chief's title). Society organised in 12 phratries and 750 clans. Claims more than 90% consistent decipherment. No null. | Fringe phonetic key, closed in kind by atlas 1.1. The clan-in-text claim is closed by atlas 5.7/7.1. Noted only because "12 phratries" will be cited against the value-12 spike in atlas 6.3. It is not a test. |
| 12 | Frenez, "Branding authority: further considerations on the oligopolistic nature of the Indus seal-based administrative system", SSRN 6103846 (2026) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6103846 (HTTP 403, not read) | Unverified | According to search snippets, strict standardisation of seals plus a very uneven spread of motifs indicate institutional branding by a few authorised roles. | Floated-ideas section. Text-level predictions are closed (atlas 10b.14, 10b.5, 5.7). |
| 13 | Jamison et al.(?), "Unicorns and seals: new multivariate approaches to exploring patterned stylistic variation in the Indus Civilization" (2023), ScienceDirect S2352226723000582 | https://www.sciencedirect.com/science/article/abs/pii/S2352226723000582 (HTTP 403, not read) | Unverified | According to search snippets, 827 unicorn seals from 24 sites show fine-scale patterned variation in design attributes and inscriptions that tracks time and place. | Would reopen atlas 10b.17 (carver hands) if the attribute coding were public. It is not. |
| 14 | Green, "Killing the priest-king: addressing egalitarianism in the Indus Civilization", *J. Archaeol. Research* 29 (2021), doi:10.1007/s10814-020-09147-9 | Springer login redirect, not followed | Unverified | According to search snippets, seals and weights were standardised public goods used among corporate groups, with no ruling class. | Floated ideas. Closed at text level by atlas 10b.14. |
| 15 | Mahadevan & Bhaskar, "Toponyms, directions and tribal names in the Indus script", in *Walking with the Unicorn* (2018) | harappa.com (HTTP 403, not read) | Unverified | According to search snippets, ideograms for hills/plains, high/low and west/east, and paired sign sets A-F, denote topographic features. | Floated ideas. Needs the sign table before it can be tested. |
| 16 | Valério, "The rongorongo 'lunar calendar' of Rapa Nui and the type of script", in Ferrara, Montecchi & Valério (eds.), *Writing from Invention to Decipherment* (OUP 2024) | Not opened (OUP) | Unverified | According to search snippets, parallel passages and glyph alternations in identical contexts (Davletshin's "cross-readings") are used to argue for script type. | Closed for Indus by atlas 1.4, 1.7 and 7.7. |
| 17 | Kharakwal et al., Kanmer clay "passes" with one unicorn impression each and different incised reverses | Not opened; known through Rao 2018 (#4), which describes them | Unverified (secondary) | Rao says all three carry "1 + man-with-harrow". Parpola, as quoted in a search snippet, says the reverses differ. | Feeds idea 2. ICIT has 10 Kanmer texts, so these could serve as held-out cases if they are in ICIT. |
| 18 | "Automated identification of allographs among the Indus Valley script signs" (Springer chapter, 2025), doi:10.1007/978-3-032-06744-9_19 | Springer login redirect, not followed | Unverified | According to search snippets, VGG16 + PCA + k-means put the 417 M77 signs into 50 clusters. | Closed in kind by atlas 7.7 and `signlist_robustness`. |

Searches that found nothing new for 2023-2026 (beyond the items above and the ones in `research_sweep`):
- New Fuls, Parpola, Yadav/Vahia or Kenoyer journal articles on the script.
- Linear Elamite numerals or seal readings. There is only the Hatamti database abstract (ORBi 2268/333157, not opened).
- Computational proto-cuneiform name finding.
- Automatic sign-function classification for Linear A or Cretan Hieroglyphic. LogogramNLP (ACL 2024) classifies find-place, which `site_signal` already covers.

Blocked:
- SSRN, ScienceDirect and harappa.com returned 403.
- Springer redirects to a login. Nature pages redirect to a cookie check, but the open-access PDF downloaded directly.
- Academia.edu was not tried, because it was known to be blocked.

---

## Floated ideas, one by one

Every idea below states:
- the prediction, written so it can be hash-sealed before any Indus number is computed;
- the null;
- a planted check that shows the method can find the effect;
- the held-out data;
- the main power concern;
- any atlas overlap.

"v2 held-out" means `dev_heldout(version=2)`. "Post-1977 ICIT" means ICIT objects at sites or excavations absent from M77 (for example HARP Harappa 1986-2007, Dholavira, Kanmer, Farmana, Rakhigarhi, Bhirrana). Nothing in this section was run. I computed only metadata counts (object types, sides, sites), not any outcome statistic.

### Idea 1 (rank 1). Header vs terminal: which slot carries the object's function

- **Who floated it.** Born, Monroe, Kelley & Sarkar 2022 (source #1): text-initial "header" signs in proto-Elamite "qualify all transactions" and are detectable without supervision, and positions 1 and 2 carry distinct information. Rao 2018 (source #4): Indus patterned texts read Prefix (institution) – Medial (quantity) – Core (commodity) – Terminal (function of sealing/tablet).
- **Hypothesis as stated.** Rao: the terminal sign encodes what the object is for, and the prefix encodes who issued it.
- **Variation we can test.** Make the known object-type signal (README #6, whole-text AUC 0.67-0.87 on clean held-out) slot-resolved. Train one-vs-rest object-type classifiers on dev using one slot's sign only: initial (in reading order), terminal, or one random medial sign. Compare their held-out AUCs. Do the same for site (Mohenjo-daro vs Harappa, seals and sealings only) as Rao's institution prediction.
- **Prediction (for sealing).**
  - P1a: on v2 held-out M77 texts of length ≥ 3, macro-AUC over object types (seal, sealing, miniature tablet, copper tablet, pottery graffito) is at least 0.03 higher for the terminal-sign-only model than for the initial-sign-only model, and the terminal model's AUC is ≥ 0.62.
  - P1b (Rao's prefix = institution): the initial-sign-only model separates Mohenjo-daro from Harappa seals at AUC ≥ 0.58, higher than the terminal-only model.
- **What we expect.** P1b will probably fail, given atlas 10b.5 (whole-text site AUC 0.49).
- **Null.** Within each text, permute which sign is called "initial" and "terminal" (keeping the sign multiset and length), refit, 1,000×. A second null permutes object labels within site.
- **Planted check.** In a copy of dev:
  - In 15% of miniature tablets, swap the terminal sign for an artificial marker. The method must place the gain in the terminal slot in ≥ 80% of 100 plants, and in the initial slot in ≤ 5%.
  - Repeat with the marker planted in the initial slot. The method must localise it the other way.
- **Held-out data.** v2 held-out, then ICIT post-1977 objects. Use native Wells signs, with slots defined by the ICIT direction field.
- **Power concern.** Object type and site are confounded: miniature tablets are mostly Harappa, copper tablets all Mohenjo-daro. Stratify by site, or restrict P1a to Harappa and Mohenjo-daro separately. Single-sign features are sparse, so pool signs seen fewer than 5 times into an "other" bucket fixed on dev. Before sealing, read `experiments/context/RESULTS.md` (register markers): if the 10 replicating markers are already known to sit in the final slot, P1a is partly descriptive and the threshold should be raised.
- **Atlas overlap.**
  - Not closed. README #6 is the whole-text version (positive).
  - Atlas 4.10 (genres from signs alone) is about unsupervised genres, not slot-resolved supervised signal.
  - Atlas 5.7 and 7.1 close the animal emblem, not object type.
  - P1b overlaps atlas 10b.5.

### Idea 2 (rank 2). Human-figure signs as counted labour categories

- **Who floated it.** Rao 2018 (source #4). It is partly anticipated by Mahadevan's burden-carrier M12 as the title *poṟai* (literature map, unverified page), which reads the same sign as a title instead.
- **Hypothesis as stated.** "Porter", "man + wheels", "man + harrow", "man + tongs" and "man + bow" are kinds of labour, counted as in proto-Elamite ration texts. The Kanmer "passes" carry 1 + man-with-harrow.
- **Variation we can test.** Treat Mahadevan's human-figure block as a class. A montage of `data/sign_images/M1`-`M60` shows human figures up to about M47; freeze the exact list after a two-person drawing check. Ask whether the class behaves like counted items rather than like titles.
- **Prediction (for sealing).** On v2 held-out M77 plus post-1977 ICIT (through the M-W bridge):
  - (a) the proportion of human-figure tokens immediately preceded, in reading order, by a stroke numeral is at least 2× the rate for non-numeral signs matched on frequency decile and mean relative position;
  - (b) human-figure tokens make up a larger share of signs on miniature tablets and tags than on seals, with a Mantel-Haenszel OR ≥ 1.5 stratified by site.
- **The competing title reading.** It predicts the opposite of (a): the class sits after names and before closers, with no numerals.
- **Null.**
  - For (a): 1,000 random sign sets of the same size, matched on frequency decile and position.
  - For (b): object-type labels permuted within site.
- **Planted check.** Pick a random 40-sign set and insert a short-stroke numeral before 10% of its tokens in a dev copy. The test must detect an OR of 2 in ≥ 80% of 100 plants.
- **Held-out data.** v2 held-out, plus post-1977 ICIT. The 10 Kanmer texts are a small out-of-sample check of the stated "1 + man-with-harrow" pattern.
- **Power concern.**
  - Count human-figure tokens in dev before sealing (a count, not an outcome).
  - If fewer than about 150 tokens are in held-out, (a) can only catch about 2× effects.
  - Copies of the 1997 Harappa miniature tablets inflate (b), so count each tablet text family once.
- **Atlas overlap.** Not closed for this class. Related:
  - atlas 6.6 (counted items after numerals, refuted in general, 13/25);
  - atlas 4.8 (tool-sign cluster as occupation titles, refuted);
  - atlas 7.2 (picture signs as logograms of the seal picture, a different question).
  - shaunmortal F2 (counted-item sets differ by stroke class) should be checked so the matched null does not reuse its signs.

### Idea 3 (rank 3). Face specialisation on multi-face objects (Cretan Hieroglyphic parallel)

- **Who floated it.**
  - Civitillo, Ferrara & Meissner 2024 (source #7). Formulae make up almost half of the seal material, and signets and prisms had different uses.
  - Evans, as reported there. Formulae are "canting badges" tied to official roles.
- **Hypothesis as stated.** On Cretan multi-face prisms, formulae occupy faces next to non-formulaic sign groups, which may be names. The detailed "prisms = formulae, 1-2-face = names" split is unverified (source #7 note).
- **Variation we can test.** On Indus objects with several inscribed faces (M77 `side` 1-6, about 1,300 texts; ICIT 902 objects with more than one text), call a face formulaic if its text, as a family, appears on at least two other unrelated object families.
- **Prediction (for sealing).**
  - P3a: among objects with ≥ 2 inscribed faces, the share with exactly one formulaic face exceeds the expectation under independent faces by ≥ 25% (relative), p < 0.01.
  - P3b: the per-face formula rate is higher on objects with ≥ 3 faces than on objects with 2 faces, within object type.
- **Null.** Permute face texts among objects of the same type, site and face count, 1,000×.
- **Planted check.** Build a synthetic corpus with the real face counts and per-face formula rates, assigned independently. Plant "one formula face per object" in 30% of objects. Detection must be ≥ 80%. On unplanted synthetic data the false-positive rate must be ≤ 5%.
- **Held-out data.** ICIT post-1977 HARP tablets and Dholavira objects not in M77. Formula status is defined using dev families only.
- **Power concern.**
  - Multi-face objects are mostly Harappa miniature tablets, so the result may just restate shaunmortal F15 (side 1 identity, side 2 tall-stroke formula).
  - Report seals and non-tablet objects separately. M77 has only 46 texts on sides 3-6, so P3b on seals is underpowered.
- **Atlas overlap.** Partly closed:
  - atlas 5.1 P1 (line 2 or side 2 of seals attested elsewhere: 2/28, refuted);
  - atlas 5.1 P11 (side-2 value not fixed per identity);
  - atlas 10b.9 (repeated 4+ sign texts).
  The new part is the across-type dose-response and the one-formula-face pairing statistic. Run it only if F15 is not already the whole story on tablets.

### Idea 4 (rank 4). Fish signs mark precious commodities at lapidary sites

- **Who floated it.** Mukhopadhyay 2023 (source #5, opened) and 2025 (source #6, unverified).
- **Hypothesis as stated.** Seals cluster near lapidary, metal and shell workshops (e.g. Chanhu-daro bead factory). Fish signs signify gems and shiny commodities, from Proto-Dravidian *mīn* 'shine'.
- **Variation we can test.** A site-level, object-type-stratified enrichment of the fish family. Sites are fixed in advance from her 2023 text: Chanhu-daro (bead factory, Mackay 1943) and Lothal (warehouse and bead finds, Rao 1979). The comparison sites are Mohenjo-daro, Harappa and Kalibangan.
- **Prediction (for sealing).** On ICIT, seals and sealings only, the fish-family token share is higher at Chanhu-daro + Lothal than at Mohenjo-daro + Harappa + Kalibangan, with a Mantel-Haenszel OR ≥ 1.5 across object types and one-sided p < 0.05.
  - The fish family is frozen as M59, M65, M67, M70, M72, M75 and their ticked forms M60, M66, M68, M71, M73.
  - The same contrast for a frequency-matched non-fish family (control) must not show OR ≥ 1.5.
- **Null.** Permute site labels within object type, 10,000×. Use text families, not copies.
- **Planted check.** Inflate fish tokens at the two sites by 1.5× (replacing random non-frame signs) in a copy. Detection must reach ≥ 80% before the real test counts as informative.
- **Held-out data.** M77 v2 held-out for the M77 rows. Post-1977 Gujarat sites (Kanmer, Shikarpur, Gola Dhoro/Bagasra, a shell and bead site) serve as a tiny replication, so report it descriptively only.
- **Power concern.**
  - Chanhu-daro has 74 ICIT texts and Lothal 208. The minimum detectable OR is probably about 1.6-2, so compute it on the planted runs before sealing.
  - Lothal sealings are many impressions of few seals, so deduplicate by seal identity (Frenez & Tosi 2005 list, already in the repo through paragorth).
- **Atlas overlap.** Not closed, but discouraged:
  - atlas 10b.17 (craft assemblage within sites: 0/49, power 0-4.5%);
  - atlas 10b.5 (no large city-specific stock);
  - atlas 4.7 (fish = deity: untestable with that statistic).
  A null here would close Mukhopadhyay's fish = gem only at site level.
- **A stronger version, not runnable now.** Her seals-with-weights co-location could be tested if the Mackay 1938 register in `experiments/old_registers` lists weights by room (unchecked; data_ready false).

### Idea 5 (rank 5). Characteristic magnitude per counted sign, out of sample

- **Who floated it.** Born, Monroe, Kelley & Sarkar 2025 (source #2). In proto-Elamite, entries ending in some container signs (M288) carry the largest capacity counts, others (M263) the smallest, and adjacent entries can stand in exact ratios (M288 = 4 × M376 across 44 entries). The Indus counterpart is Mukhopadhyay's commodity-specific denominations (literature map P12).
- **Variation we can test.** For counted signs (the sign right after a stroke numeral in reading order) with ≥ 8 numeral tokens in dev, compute mean numeral value (short strokes counted as units; tall strokes kept as a separate class, as shaunmortal F2 requires). Freeze the dev rank order.
- **Prediction (for sealing).** The Spearman correlation between the dev rank order and the held-out rank order (v2 held-out plus post-1977 ICIT, signs with ≥ 4 held-out numeral tokens) is ≥ 0.5, p < 0.05.
- **Secondary prediction.** On multi-face objects where two faces each carry numeral + sign, the ratio of the two values is constant within a text family more often than under permutation. Atlas 5.1 P11 already makes this unlikely.
- **Null.** Permute numeral values among counted-sign tokens within object type and stroke class (tall vs short), 10,000×.
- **Planted check.** Assign 10 random signs a true mean value from 2 to 8 and resample their numerals with Poisson noise at real token counts. The method must recover rho ≥ 0.5 in ≥ 80% of runs.
- **Held-out data.** v2 held-out, then ICIT post-1977.
- **Power concern.** Few counted signs reach 8 dev tokens, and value sets are lumpy (peaks at 3, 7 and 12, atlas 6.3), so rank correlation may rest on fewer than 10 signs.
- **Atlas overlap.** Partly closed:
  - atlas 6.6 (no spike of numerals on counted items);
  - atlas 6.5 (M328 fixed-value model);
  - atlas 5.1 P11 (side-2 value not fixed);
  - shaunmortal F2/F5.
  What is new is the out-of-sample replication of an ordinal magnitude scale.

### Other floated ideas, with why they were not ranked

| Idea | Who (source) | Hypothesis | Testable variation | Atlas overlap / status |
|---|---|---|---|---|
| Seals as generators of ration tokens; seal texts repeat on tablets and tags | Rao 2018 (#4) | A seal's text (or its last two signs) is reproduced on token-like objects | Share of seal texts whose final bigram appears on a miniature tablet at the same site, vs a bigram null | Mostly closed: atlas 5.3, 10b.9, 10b.4 and identifiers S3 (short cross-object repeats are chance collisions under a bigram null). The 1997 Harappa case is one family. |
| Seal texts as "patterned" vs "complex" texts | Rao 2018 after Wells 2015 and Bonta (#4) | Two genres: economic patterned texts and other complex texts | Unsupervised split | Closed at this corpus size: atlas 4.10 (methods blind below about 0.5 bits/text). |
| Branding or oligopoly; the seal marks a role, not a person | Frenez 2026 (#12, unverified); Frenez 2018 "Private person or public persona" (Zenodo 5513987, not opened); Green 2021 (#14, unverified) | Few "firms" with low personalisation | (a) texts under one emblem share a firm element; (b) few discrete seal-size classes per emblem | (a) closed by atlas 5.7 (same-emblem Jaccard at null), 10b.14 and 10b.5. (b) is not about the script, and atlas 5.2 found no size link to the title ladder. Not ranked. |
| Unicorn style attributes co-vary with inscriptions | Jamison et al. 2023 (#13, unverified) | Carving style and inscription vary together by time and place | Style cluster × text frame | Needs their attribute coding (not public). Atlas 10b.17 found no frame sharing among carving-alike seals at about 8 px/mm. |
| Topographic and direction ideograms; paired sign sets | Mahadevan & Bhaskar 2018 (#15, unverified) | Sign pairs mean hills/plains, high/low, west/east | Paired signs in complementary distribution in one slot; "west" sign enriched at western sites | Data_ready false: sign numbers unknown until the paper is read. The toponym version is closed (atlas 5.4). A direction-by-site test is not closed. |
| Clan totems in text; Gondi readings | Gondwana 2026 (#11); Kenoyer 1998 and Fairservis (via search snippets) | Animal = clan, and text names the clan | Text predicts the animal | Closed: atlas 5.7 and 7.1 (unicorn vs other AUC 0.52). The phonetic key is closed in kind by atlas 1.1. |
| Image-plus-context clustering of the sign inventory | Born et al. 2023 (#3); Corazza et al. 2022 (already in the literature map); Springer 2025 chapter (#18, unverified) | Data-driven allograph merges | Run the Born architecture on `data/sign_images` + M77 context, with the Cypro-Greek known answer as a gate | Largely covered: `signlist_robustness`, atlas 7.7. Worth doing only as a source of a new sign list for the headline re-runs. |
| Cross-readings (glyph alternation in identical contexts) reveal phonetic or allographic links | Davletshin; Valério 2024 (#16, unverified) | Substitution in parallel passages | Already done | Closed: atlas 1.4, 1.7, 7.7; README #11 (fish substitution). |
| Combinatorial-optimisation cognate matching | Tamburini 2025 (#8) | Sign-to-sign and word-to-word matching to a known related language | Needs a candidate language and word division | Closed: atlas 1.8, 1.9. |
| Function from position (logogram before numeral) | SigLA (#10) | Position gives function | Already `functional_reading` | Covered (README #9). |
| Seals co-located with weights mark tax or revenue roles | Mukhopadhyay 2023 (#5) | Seals found with weights carry different texts | Seals in rooms with weights vs without (Mohenjo-daro DK registers) | Data_ready false until someone checks whether the register in `experiments/old_registers` lists weights by room. Not covered by atlas 10b.14, which compares seals with each other, not with weights. |

---

## What to do next

1. Before sealing ideas 1-3, check three overlaps that I could not settle from the result files alone:
   - the slot position of the register markers in `experiments/context`;
   - shaunmortal F15's exact definition, for idea 3;
   - which counted signs F2 already used, for ideas 2 and 5.
2. Write each prediction above into `docs/prereg/` with its planted check, and hash it before computing any Indus number.
3. Human leads (for `docs/HUMAN_LEADS.md`, not edited by me):
   - an open copy of Mahadevan & Bhaskar 2018 (Table 1 and Table 10 sign sets);
   - Mukhopadhyay 2025 (SSRN 5079207) for her list of fish-sign find contexts;
   - the Jamison et al. 2023 attribute coding;
   - the Kanmer pass reverses (Kharakwal et al., Puratattva 39, 2009, or the 2012 report).
