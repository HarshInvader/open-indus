# Literature note: regional variation vs uniformity in Indus inscriptions

Claim under review: Indus seal texts from Mohenjo-daro and Harappa show no place signal beyond a within-city floor, while readable seal legends that carry names (Ur III, Latin instrumentum) do. Chanhu-daro may differ.

Our numbers, for reference:
- Between-city AUC on seals is 0.51-0.55, the same as the within-Mohenjo-daro floor (Δ −0.033 to +0.042).
- A 15% local sign stock would be detected in 93-100% of runs. Planted names on up to 20-30% of seals would still be compatible with what we observe.
- Ur III legends separate their cities by Δ +0.16 to +0.31 above the floor. Latin instrumentum separates its provinces by Δ +0.12 to +0.14.
- Linear B Knossos vs Pylos drops from 0.90 to 0.524 once hands are held out.
- Chanhu-daro is the most separable site (0.61-0.68) but does not beat its permutation null (q 0.18-0.35).
- Sealings differ between the two cities (+0.10 to +0.12). The tablet difference (0.774) is an object-subtype effect.

Relation key: **confirms** = says what we find; **extends** = we test what they asserted or add a calibration they lacked; **conflicts** = reports a site signal or regional difference that we must answer.

Page numbers are those printed in the source (or the PDF page where none is printed). "Seen via" means we read the claim only as cited by another author.

---

## 1. Statements of uniformity

### Parpola 1994
Parpola, A. 1994. *Deciphering the Indus Script*. Cambridge: Cambridge University Press.
- Open access: none (book).
- Claim: Indus sign sequences are uniform across the whole civilisation, which argues against widely different languages. A harappa.com summary of Parpola gives: "The uniformity of the sign sequences in Indus inscriptions coming from all parts of the large area occupied by the Indus civilisation precludes the possibility that widely different languages were used". Parpola contrasts this with the unusual sign combinations on West Asian seals.
- Status: **the quote is unverified**. We saw it only in a search snippet of harappa.com/script/parpola15.html, which blocked our client, and we could not check the book page. Kenoyer & Meadow 2010 and Jamison 2017 both cite Parpola 1994 as the standard statement of uniformity (below).
- Relation: **confirms and extends.** He made a qualitative claim for Mohenjo-daro and Harappa; we add a calibrated test with a within-city floor and power analysis. His West Asian exception matches Rao et al. 2009.

### Yadav, Salgaonkar & Vahia 2017
Yadav, N., Salgaonkar, A. & Vahia, M. N. 2017. "Clustering Indus Texts using K-means." *International Journal of Computer Applications* 162(1): 16-21. DOI 10.5120/ijca2017913207.
- Open access: https://www.ijcaonline.org/archives/volume162/number1/yadav-2017-ijca-913207.pdf
- Claims:
  - Abstract: the clusters "are only weakly associated to any archaeological site or medium of writing".
  - p. 19: "No signification [sic] correlation between the clusters and the archaeological sites or medium of writing is observed. Only cluster C8 has a large fraction of texts on sealings ... from the site of Harappa."
  - pp. 20-21: the "absence of any significant correlation with the archaeological sites ... suggests a high level of uniformity of writing over the entire stretch of the Indus civilization", i.e. a "high level of standardization".
  - Sites: Mohenjo-daro, Harappa, Lothal, Kalibangan, Chanhu-daro, other Harappan, West Asian.
- Relation: **confirms, and we extend it.** This is the closest prior computational result. It is unsupervised, with no floor, no power analysis and no positive control. Its one exception (Harappa sealings) is the same object-type effect we find (+0.10 to +0.12 on sealings). Must cite.

### Yadav 2013 (not accessed)
Yadav, N. 2013. "Sensitivity of Indus Script to Site and Type of Object." *Scripta* 5: 67-103. Cited as reference [17] in Yadav et al. 2017.
- This is directly on our question and must be read before submission. **Not accessed**; we saw only the citation.

### Nair 2026
Nair 2026. "How Non-Linguistic Is the Indus Sign System? A Synthetic-Baseline Scorecard." arXiv 2604.17828.
- Open access: https://arxiv.org/abs/2604.17828
- Claims:
  - p. 9, Table 7 gives per-site counts (e.g. Chanhu-daro 44 texts, 86 signs).
  - "positional structure (Cramér's V) is remarkably similar (0.160 vs. 0.153), suggesting the same positional grammar was in use across sites".
- Relation: **confirms** for positional grammar. That is one summary statistic, not a classifier and not floor-calibrated.

### Fuls 2024
Fuls, A. 2024. "Comparison of Linear Elamite and Indus Writing Systems." *Iranian Journal of Archaeological Studies* 14(1). DOI 10.22111/IJAS.2024.48980.1305.
- Open access: ijas.usb.ac.ir (journal site).
- Claims:
  - p. 4: "The script and the inscribed material, however, show several differences between the two major sites ...: Harappa mostly used tablets and Mohenjo-daro seals."
  - p. 13: "Throughout this time Indus signs did not show significant graphical changes in shape or function".
  - Corpus shares: Mohenjo-daro 38%, Harappa 41%, Gujarat/Kutch about 9%.
- Relation: **confirms our design choice.** The two cities differ mainly in which objects they inscribed. That is why we compare seals with seals, and why tablets come out as an object-subtype effect. Must cite.

Fuls's site-specific sign-frequency work in ICIT and in *Catalog of Indus Signs* (2023) was **not accessed** (see section 8).

---

## 2. Statements of regional variation (script)

### Wells 2015
Wells, B. K. 2015. *The Archaeology and Epigraphy of Indus Writing*. Oxford: Archaeopress (appendices by A. Fuls).
- Open access: only the publisher's sample PDF (front matter) was read.
- Claims:
  - p. viii: "Bigger issues of regional variations or multiple languages ... need further work ... There are marked regional differences in sign uses and artifact inventories. Future research should focus on defining these regional differences in text structure."
  - p. ix: researchers should take care "not to mix the corpus into a monolithic unit, as it is demonstrably affected by spatial and temporal variation (Wells 2011)".
- Relation: **conflicts in wording, compatible in substance.** "Sign uses and artifact inventories" is mostly what we attribute to object type (tablets, sealings) and to the outer regions. For seals from Mohenjo-daro and Harappa, we found no regional difference in text structure above the floor, which answers the research question Wells set. Must cite. Wells 2011 (*Epigraphic Approaches to Indus Writing*, Oxbow) was **not accessed**; nor were the Dholavira notes.

### Kenoyer & Meadow 2010
Kenoyer, J. M. & Meadow, R. H. 2010. "Inscribed Objects from Harappa Excavations 1986-2007." In A. Parpola, B. M. Pande & P. Koskikallio (eds), *Corpus of Indus Seals and Inscriptions* 3.1, pp. xliv-lviii. Helsinki: Suomalainen Tiedeakatemia.
- Open access: https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf (local copy in the repo; the site blocks automated fetches).
- Claims:
  - p. xlviii: in the Harappa phase "a relatively standardized form of the core Indus script became more common".
  - p. li: "a well-defined carving style across the northern part" of the Indus region, perhaps from a "single workshop or perhaps seal carvers who were trained originally in one workshop and then developed their own ateliers at other sites".
  - p. lvi: what is needed is "rigorous analysis at the site, regional, and cross-regional levels ... When such studies have been carried out, assumptions about the uniformity of the signing system (Parpola 1994) probably will need to be revised."
- Relation: **conflicts as a prediction, and we test it directly.** They predicted that site-level analysis would overturn uniformity. For sign sequences on seals at Mohenjo-daro and Harappa, our site-level test with a floor does not. Their chronology (standardisation increasing through the Harappa phase) fits our observation that time inside Mohenjo-daro separates as strongly as city does (site_signal: 0.61). Must cite.

### Kenoyer 2020
Kenoyer, J. M. 2020. "Origin and Development of the Indus Script." In K. Lashari (ed.), *Studies on Indus Script*, pp. 217-236 (end page unverified; see section 9). Karachi: National Fund for Mohenjodaro.
- Open access: harappa.com PDF (local copy in the repo).
- Claims:
  - p. 218: "Kutch and Gujarat also played an important role in terms of specific regional styles of graphic symbols, but more research needs to be done".
  - p. 219: the script was used "to write names and commodities in many regional dialects and even different languages".
  - In the Late Harappan period there is "no regional pattern of writing use".
- Relation: **partly conflicts.** If the seals wrote names in several regional dialects, a place signal would be expected. Our planted-name test bounds this: names on more than 20-30% of Mohenjo-daro and Harappa seals would have been detected. Regional styles in Gujarat and Kutch are outside our two-city test.

### Rao et al. 2009 (West Asian seals)
Rao, R. P. N., Yadav, N., Vahia, M. N., Joglekar, H., Adhikari, R. & Mahadevan, I. 2009. "A Markov model of the Indus script." *PNAS* 106(33): 13685-13690. Technical report version: UW-CSE TR 08-11-02 (2008).
- Open access: the technical report (UW CSE).
- Claims:
  - TR p. 11: the median likelihood of West Asian texts under the Indus-valley model is 6.22e-13, "about 100,000 times less" than held-out Indus-valley texts at 6.85e-8.
  - The script "may have been used to represent a different language or subject matter by Indus traders ... in West Asia". This cites Parpola on unusual sign combinations.
- Relation: **confirms the method can see a place effect.** A sequence model does detect a place effect when one exists (the West Asian texts). This is the Indus-internal positive control to set beside our Ur III and Latin ones. It also shows that the uniformity claim covers the Indus heartland, not the whole diaspora. Must cite.

### Mahadevan 1977; Mahadevan & Bhaskar 2018
Mahadevan, I. 1977. *The Indus Script: Texts, Concordance and Tables*. New Delhi: Archaeological Survey of India. (Already in the repo library.)
- Claim relevant here: the concordance tables tabulate signs by site and object, the basis of later site analyses. We did not re-read them for an explicit statement on regional variation.

Mahadevan, I. & Bhaskar, M. V. 2018. "Toponyms, Directions and Tribal Names in the Indus Script." In D. Frenez et al. (eds), *Walking with the Unicorn*, pp. 359-376. Oxford: Archaeopress.
- Known only from the volume's table of contents. **Not accessed.**
- Relation, from the title: **potential conflict.** Toponyms on seals would predict a place signal. Our planted-name power analysis is the relevant test. Must read before submission.

### Oakes 2019 (abstract only)
Oakes, M. P. 2019. "Statistical Analysis of the Tables in Mahadevan's Concordance of the Indus Valley Script." *Journal of Quantitative Linguistics* 26(1): 22-47. DOI 10.1080/09296174.2017.1406294.
- Open access: green open-access copy at https://hdl.handle.net/2436/620846. The repository reset our connection, so we did not read it.
- Claim (abstract): significant associations of signs "with position, object, field symbol or direction of writing". Site is one of the concordance tables, but the abstract does not name it among the significant associations.
- Relation: **unclear.** Must read the full text to see whether a site association was found.

### Recchia & Louwerse 2016 (abstract only)
Recchia, G. & Louwerse, M. M. 2016. "Archaeology through Computational Linguistics: Inscription Statistics Predict Excavation Sites of Indus Valley Artifacts." *Cognitive Science* 40(8): 2065-2080. DOI 10.1111/cogs.12311.
- Open access: none found; the publisher page served a bot challenge, so the full text was not read.
- Claims (abstract):
  - Methods like latent semantic analysis "can accurately predict the relative locations of archeological sites on the basis of artifacts of known provenance".
  - "inscription statistics reflect historical interactions among locations".
  - Five sites (Mohenjo-daro, Harappa, Chanhu-daro, Lothal, Kalibangan) and four unprovenanced sealings.
- Relation: **the main conflict.** It reports a site signal in inscription statistics. Possible reconciliations to check against the full text:
  1. Their unit pools all object types per site, so tablet/seal/sealing mix (Fuls 2024) can carry the signal.
  2. No within-site floor.
  3. Duplicate texts (e.g. Harappa tablet series) may inflate similarity.
  4. Their outlying sites (Chanhu-daro, Lothal, Kalibangan) are where we too see the most separation.

  Must cite, and should be discussed explicitly.

---

## 3. Seal style and iconography (not sign sequences)

### Ameri 2013 (seen via Petrie et al. 2018)
Ameri, M. 2013. "Regional Diversity in the Harappan World: The Evidence of the Seals." In S. A. Abraham, P. Gullapalli, T. P. Raczek & U. Z. Rizvi (eds), *Connections and Complexity: New Approaches to the Archaeology of South Asia*, pp. 355-374. Walnut Creek: Left Coast Press.
- Open access: none found. **Not accessed directly.**
- Claims, as cited by Petrie et al. 2018: 467:
  - Ameri 2013: 362: the unicorn is the majority motif at Harappa, Mohenjo-daro and Lothal.
  - Ameri 2013: 367: only 17% of seals at Banawali bear the unicorn.
- Relation: **compatible.** Her regional diversity is in iconography and style, mostly at outer sites. Our test is on sign sequences at the two big cities. This should be stated in the paper so the claims do not appear to clash. Ameri's other relevant chapter, "Sincerest Form of Flattery?" (*Walking with the Unicorn*, 2018, p. 19 onward), was **not accessed**.

### Jamison 2017
Jamison, G. M. 2017. *The Organization of Indus Unicorn Seal Production: A Multi-faceted Investigation of Technology, Skill, and Style*. PhD thesis, University of Wisconsin-Madison.
- Open access: thesis PDF (local copy in the repo).
- Claims:
  - p. ii: "Traditionally thought to be highly uniform, this study has uncovered evidence of patterned variation in unicorn carving styles".
  - p. 1: "Traditionally, inscribed Indus seals have been described as highly standardized and uniform ... (Marshall 1931; Parpola 1994)".
  - About p. 12: the results refute "the notion that Indus seals were highly uniform and standardized".
  - Style groups cross sites (including a Mohenjo-daro–Chanhu-daro group), pointing to "decentralized" production.
- Relation: **compatible, and it sharpens our framing.** Carving style varies by workshop, but the workshops span cities. That fits a text signal that follows workshop or period rather than city. It also offers one explanation for Chanhu-daro. Must cite.

### Jamison & Uesugi (venue unverified)
Jamison, G. M. & Uesugi, A. "Mohenjo-daro and Interregional Connections ..." (Academia.edu 86751036). Read through a harappa.com summary only.
- Claims:
  - 350 unicorn seals sorted into 14 stylistic groups, all of which include Mohenjo-daro.
  - Group #8 links Mohenjo-daro, Harappa and Dholavira (p. 27).
  - The harappa.com reviewer notes that the groups "do not seem to suggest any similarities in the signs carved".
- Relation: **confirms** that style groups do not map onto texts. The venue and year are **unverified**.

### Petrie, Parikh, Green & Bates 2018
Petrie, C. A., Parikh, D., Green, A. S. & Bates, J. 2018. "Looking beneath the Veneer: Thoughts about Environmental and Cultural Diversity in the Indus Civilization." In D. Frenez, G. M. Jamison, R. W. Law, M. Vidale & R. H. Meadow (eds), *Walking with the Unicorn*, pp. 453-474. Oxford: Archaeopress.
- Open access: https://api.repository.cam.ac.uk/server/api/core/bitstreams/fee9f30d-c311-4e0c-ba10-ab9c693cb8c1/content
- Claims:
  - p. 453: "There is clear evidence for degrees of uniformity ... also evidence that there was considerable cultural diversity". It uses the "veneer" of uniformity concept from Meadow & Kenoyer 1997: 139.
  - p. 465: "Indus stamp seals and the clay sealings ... are typically used as examples of social and cultural uniformity, but they also exemplify patterns of variation."
  - p. 467: "Seals and sealings provide one of the most abundant sources of Indus imagery and writing, which also exhibits considerable variation". This cites Ameri 2013, and Konasukawa 2014 on animals facing right in the eastern region.
  - p. 468: "the degree of material uniformity has been overstated (Petrie 2013)".
- Relation: **partial conflict, in general terms.** Their variation is iconographic and regional. Our result adds that, for the texts at the two big cities, the "veneer" holds under a calibrated test. Must cite as the current statement of the diversity view.

### Kenoyer, Possehl, Meadow on standardisation
- Kenoyer & Meadow 2010 (above) is the verified source.
- Possehl 1996 (*Indus Age: The Writing System*) and Possehl 2002 (*The Indus Civilization*) were **not accessed**. We have no verified Possehl quotes on standardisation.
- Meadow & Kenoyer 1997 is verified only through Petrie et al. 2018: 453.

---

## 4. Chanhu-daro

### Mackay 1943
Mackay, E. J. H. 1943. *Chanhu-daro Excavations 1935-36*. American Oriental Series 20. New Haven: American Oriental Society.
- Open access: Internet Archive, in.ernet.dli.2015.105167 (OCR copy in the repo).
- Claims:
  - pp. 140-141: Jhukar-period seals are "radically different they are both in shape and in the designs they bear from those of the Harappa Culture".
  - p. 143: "There are no characters or pictographs on any of the amulets of this period [Jhukar]".
  - p. 145: whether seals "were made only for local use or to be traded over an extended area it is impossible as yet to say". Unfinished seals show that seals were made on site.
  - p. 146: copper tablets, "so plentiful at Mohenjo-daro and so rare at Harappa, have also not yet appeared at Chanhu-daro: they may have been a purely local product of the former city". The unicorn is on 44 of 55 seals with animals.
  - pp. 148-149: "The diversity of the characters ... implies that they do not refer to the animal ... it is generally thought that they are personal names, perhaps with titles appended." Also "One new sign at least occurs on the seals from Chanhu-daro" (Pl. LI, 30).
  - Most seals come from Mound II, between −5.7 and +15.4 ft.
- Relation:
  - **Supports our Chanhu-daro caveat** in three ways: seals were made locally, there is at least one sign new to the site, and the inscribed seals all come from the Harappan levels. Because Jhukar seals carry no signs, the Jhukar period cannot explain the Chanhu-daro text difference.
  - Mackay does not mention the M93 end mark. The finding that M93 is a Chanhu-daro habit (repo: toponyms experiment) appears to be **new**.
  - His copper-tablet remark is an early statement of an object-type difference that is local to one city.

### Didier 2017 and in press
Didier, A. 2017. Renewed excavations at Chanhu-daro. *Pakistan Archaeology* 30: 69-121.
Didier, A., in press. Chanhu-daro chronology. *Sindh Antiquities*. HAL preprint halshs-04365840.
- Open access: HAL (halshs-04365840).
- Claims:
  - Chanhu-daro was occupied in the Mature Harappan period, 2600/2500-1900 BCE.
  - Mackay's Harappa I-IV levels are re-phased, and the Harappa II craft quarters show bead and seal making.
- Relation: **supports a workshop or period explanation** for Chanhu-daro's separability. It is a possibility, not something we tested.

---

## 5. Comparison corpora (within-site and scribal-hand confounds)

### Linear B: Bennett 1966
Bennett, E. L., Jr. 1966. "Some Local Differences in the Linear B Script." *Hesperia* 35(4): 295-309.
- Open access: https://www.ascsa.edu.gr/uploads/media/hesperia/147560.pdf
- Claims:
  - p. 295: "Differences could be pointed out in the shapes of signs, as well as in the disparate frequencies of use of the less common syllabic signs", yet "the Linear B script is remarkably uniform".
  - p. 296: "this handwriting is not uniform", attributed to individual scribes and apprenticeship.
- Relation: **confirms our Linear B red-team result.** Local differences run through scribes. Once hands are held out, Knossos vs Pylos falls from 0.90 to 0.524. Must cite.

### Linear B: Srivatsan et al. 2021
Srivatsan, N., Vega, J., Skelton, C. & Berg-Kirkpatrick, T. 2021. "Neural Representation Learning for Scribal Hands of Linear B." ICDAR 2021 Workshops. arXiv 2108.04199.
- Open access: https://arxiv.org/abs/2108.04199
- Claims: 74 hands (48 Knossos, 26 Pylos). Findplace is predicted from hand embeddings (8 findplaces, 63 hands). Hand and findplace are entangled.
- Relation: **confirms** that a place classifier on Linear B partly learns hands. This justifies holding hands out in our comparison.

Palaima 1988 (*The Scribes of Pylos*) and Olivier 1967 (*Les scribes de Cnossos*) are the standard scribal-hand references. **Not accessed.**

### Ur III and Latin
- We found **no prior computational study** that classifies the place of origin of Ur III seal legends or Latin instrumentum inscriptions against a within-site floor. We state this as a gap, not as a finding.
- Latin regional variation has computational work behind it (the Budapest *Computerized Historical Linguistic Database of Latin Inscriptions*, LLDB). A workshop abstract by Adamik describes the Danubian provinces as a "complex mosaic" rather than a distinct dialect area. We saw the abstract only, so it is weak support. Full citation is **unverified** (section 9).

### Related work already in the repo library
- Gokhale, P. & Ameri, M. 2026. "Modelling the possible archaeological past(s): Agent-based modelling of Harappan seal use and survival." *CAA Proceedings* 51(1). DOI 10.64888/caaproceedings.v51i1.1025. It gives the seal-to-sealing ratio (about 2,200 : 250) and notes that DK-G South holds more than 15% of all seals. This matters for our within-Mohenjo-daro floor by area. Cite for context.
- Raghavendra 2026. "On the Non-Specificity of Statistical Measures Used in Script Decipherment (SIGIL)." arXiv 2608.02999. Corpus statistics cannot settle what kind of system Indus is. Cite as a caution that our null result does not establish what the seals encode.

---

## 6. Methods references (why a floor is needed)

- Kapoor, S. & Narayanan, A. 2023. "Leakage and the reproducibility crisis in machine-learning-based science." *Patterns* 4(9): 100804. DOI 10.1016/j.patter.2023.100804. Open access. Grounds the argument that classifier accuracy needs a leakage-aware baseline.
- Zech, J. R. et al. 2018. "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study." *PLoS Medicine* 15(11): e1002683. DOI 10.1371/journal.pmed.1002683. Open access. A classifier learned the hospital site rather than the disease. This is the same confound a place classifier on inscriptions faces: it can learn excavation area, period, object type or scribe instead of place.

---

## 7. What is new in our paper

Uniformity of Indus sign sequences is an old claim (Parpola 1994). A clustering study found no site association (Yadav et al. 2017), and one positional statistic is similar across sites (Nair 2026). Regional variation in seal iconography, carving style and object inventories is also well established (Ameri 2013; Jamison 2017; Petrie et al. 2018; Wells 2015; Fuls 2024). At least one study reports that inscription statistics predict site relations (Recchia & Louwerse 2016). Kenoyer & Meadow (2010: lvi) predicted that site-level analysis would force a revision of the uniformity assumption. We do not claim to be first to say Indus texts look uniform. What is new is how we test it:

1. We compare sign sequences on one object type (seals) between Mohenjo-daro and Harappa against a within-city floor, built from area splits and random halves of Mohenjo-daro. Nothing we found in the prior work calibrates a site test this way.
2. We report power: a 15% local sign stock would have been detected, and names on more than about 20-30% of seals would have shown.
3. We apply the same pipeline to readable seal legends that carry names. Ur III and Latin instrumentum do separate their places above their floors, and their name-free text does not, so the method can see a place effect when names carry one.
4. We show, with Linear B, how scribal hands inflate a naive place classifier.
5. We separate object-type effects (sealings, tablets) from place.

The result is narrow. It concerns seals at the two big cities. It says nothing about the Gujarat or Kutch sites or about iconography, and it leaves Chanhu-daro open: the site is the most separable but is not significant against its own null. We also add one finding not reported before: the M93 end mark is a Chanhu-daro habit.

---

## 8. Prior results to cite, and conflicts

### Must cite
1. Parpola 1994 (the uniformity claim; page to verify).
2. Yadav, Salgaonkar & Vahia 2017 (no site association; Harappa-sealing cluster C8).
3. Yadav 2013, *Scripta* 5 (site and object sensitivity; must read).
4. Rao et al. 2009 PNAS (West Asian texts differ; an Indus-internal positive control).
5. Recchia & Louwerse 2016 (site prediction from inscriptions; main conflict).
6. Kenoyer & Meadow 2010 (prediction that uniformity will be revised; Harappa chronology and workshops).
7. Wells 2015 (regional differences in sign use; call for text-structure study).
8. Fuls 2024 (Harappa tablets vs Mohenjo-daro seals; no graphic change over time).
9. Ameri 2013 (regional diversity in seals; iconography).
10. Jamison 2017 (carving-style groups that cross sites).
11. Petrie et al. 2018 (veneer of uniformity; variation in seals).
12. Mackay 1943 (Chanhu-daro: local seal making, new sign, uninscribed Jhukar seals, Mohenjo-daro copper tablets).
13. Bennett 1966 and Srivatsan et al. 2021 (Linear B: local differences follow scribes).
14. Mahadevan 1977 (corpus and tables) and Mahadevan & Bhaskar 2018 (toponyms; must read).
15. Nair 2026 (similar positional structure across sites).
16. Kapoor & Narayanan 2023 and Zech et al. 2018 (methods: leakage and site confounds).

### Conflicts to address in the paper
- **Recchia & Louwerse 2016**: site relations predicted from inscription statistics. This is the direct conflict. Check their unit of analysis, object-type mix, duplicates and baseline.
- **Kenoyer & Meadow 2010: lvi**: they expected the uniformity assumption to be revised. For seal texts at Mohenjo-daro and Harappa, our test does not revise it.
- **Wells 2015: viii**: "marked regional differences in sign uses". Most likely object type and outer regions. Say so with our sealing and tablet results.
- **Kenoyer 2020: 219**: names in "many regional dialects". This is bounded by our planted-name power analysis.
- **Mahadevan & Bhaskar 2018**: if seals carry toponyms, a place signal is expected. This is bounded by the same analysis, and the chapter should be read first.
- **Ameri 2013, Jamison 2017, Petrie et al. 2018**: variation in iconography and style. Not in conflict with a text result, but readers will see it as one unless the paper separates text from image.
- **Oakes 2019**: unknown whether a site association was reported. Read the full text.

---

## 9. Sources not accessed

These were blocked, paywalled or not found as open-access copies. No access controls were bypassed.
- Ameri 2013, *Connections and Complexity*, pp. 355-374. Seen only through page citations in Petrie et al. 2018.
- Ameri 2018, "Sincerest Form of Flattery?", *Walking with the Unicorn*.
- Yadav 2013, *Scripta* 5: 67-103.
- Mahadevan & Bhaskar 2018, *Walking with the Unicorn*, pp. 359-376.
- Recchia & Louwerse 2016, full text (abstract only).
- Oakes 2019, full text (abstract only; the repository did not respond).
- Fuls 2023, *Catalog of Indus Signs*, section on sign frequencies by region; Fuls's site-specific ICIT analyses and his writing on mathematical epigraphy.
- Wells 2011, *Epigraphic Approaches to Indus Writing*; Wells's Dholavira and regional notes; the full text of Wells 2015 beyond the sample.
- Frenez 2018, "Private Person or Public Persona?", *Walking with the Unicorn*.
- Konasukawa & Koiso 2018, "Size of Indus Seals", *Walking with the Unicorn*.
- Uesugi, on diversity, complexity and standardisation (exact title not confirmed).
- Possehl 1996 and 2002.
- Parpola 1994, specific pages; Parpola's harappa.com lecture pages (blocked).
- Palaima 1988 and Olivier 1967 (Linear B scribes).
- Excavation registers for Mackay-era Chanhu-daro beyond the 1943 report.

## 10. Unverified

- The Parpola uniformity quote: wording from a search snippet only; source page and book page unknown.
- Jamison & Uesugi, "Mohenjo-daro and Interregional Connections ...": venue and year.
- A search-engine summary saying Oakes 2019 found a site association. The abstract does not say so; treat it as unverified.
- Kenoyer 2020, end page of the chapter (236 or 270).
- Adamik on Danubian Latin as a "complex mosaic": seen in a workshop abstract only; full citation not confirmed.
- Meadow & Kenoyer 1997: 139 ("veneer"): seen only as cited by Petrie et al. 2018.
- Konasukawa 2014 (eastern seals face right): seen only as cited by Petrie et al. 2018.
