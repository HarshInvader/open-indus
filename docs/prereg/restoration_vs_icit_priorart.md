# Prior-art check: restoration scored against an independent reading (ICIT)

Date: 2026-11-19. Read-only. "Opened" means I read the page or PDF text. Anything else is marked (unverified).

## 1. Verdict: partly holds

- **For Indus, it holds on everything I could open.** Yadav 2010 (Sec. 5) deletes a random sign from intact texts. Venkatesh & Farghaly 2023 tune on single signs removed from complete ICIT texts (abstract only). The IIT Hyderabad deposit scores masked positions on texts with no lost or doubtful sign. Its Table S11 lists candidates for 360 damaged texts with no second reading to score them against. The only check is an intact parallel in the corpus, for 111 of 360: a different text, not an independent reading of the same object.
- **Gap in my search:** Venkatesh & Farghaly also predicted signs in about 100 real damaged texts. The abstract does not say how those were checked, and I did not read the full text.
- **As a general claim about restoration models, it fails.** Linear B work scored a model on 29 real damaged gaps against experts' estimates. Ithaca and Pythia each scored one real decree against a published edition.
- **Not found:** the IIT paper itself. The Zenodo record links none, so I could not read how the paper treats S11.
- **No paper compares experts' restorations of the same real damage with each other.** Lazar reports kappa 0.79, but on the plausibility of model suggestions.

## 2. What would be new

The first scoring, at n≈360 and for any script, of a model's restorations of real damage against an independent transcription of the same objects, split by clean texts versus near-copies. Comparing with experts is not new (Linear B, n=29, one edition). The independent second reading and the leakage split are.

## 3. Papers

| Paper | URL opened | Evaluation and notes |
|---|---|---|
| IIT Hyderabad deposit, Kanichira et al. 2026 | https://zenodo.org/records/24164070 | Masked positions on intact texts. S11: 360 damaged texts, unscored. S11 read from our local zip copy |
| Yadav et al. 2010 | https://arxiv.org/pdf/0901.3017 | Random deletion from intact texts (Table 5). Doubtful M77 reads restored (Table 6), no second reading |
| Venkatesh & Farghaly 2023 | https://emerginginvestigators.org/articles/22-256 | Single signs removed from complete ICIT texts, about 63%. About 100 real damaged texts predicted. Abstract only |
| Rao et al. 2009 | https://www.pnas.org/doi/10.1073/pnas.0906237106 | (unverified) 403. A search snippet says it used an artificially damaged set |
| Pythia, Assael 2019 | https://aclanthology.org/D19-1668.pdf | Hidden characters in intact text. Two doctoral students scored 57.3% CER. One real decree vs the Rhodes and Osborne edition. Students not compared with each other |
| Ithaca, Assael 2022 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8907065/ | Hidden 1-10 characters. Two historians. One real decree (IG II² 116) vs edition, 74 vs 45 mistakes. No inter-annotator agreement |
| Aeneas, Assael 2025 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12408360/ | Artificial masking. 23 epigraphers on 60 inscriptions, scored against the masked original, never against each other. About 60% of the text read |
| Fetaya 2020, Akkadian | https://arxiv.org/html/2003.01912v1 | Masked words in intact sentences. No expert baseline. One real tablet shown, no model comparison |
| Lazar 2021, Akkadian | https://aclanthology.org/2021.emnlp-main.384.pdf | Masked gold spans. Two Assyriologists (also authors) rated 5 options, kappa 0.79 |
| Papavassileiou & Kosmopoulos 2024, Linear B | https://aclanthology.org/2024.ml4al-1.13.pdf | Synthetic gaps, plus 29 real gaps vs experts' estimates from one edition. Top-5 matched 9, top-10 matched 15. Closest analogue |

Also opened, no restoration test on real damage: Raghavendra 2026 (https://arxiv.org/abs/2608.02999, abstract only, synthetic corpus) and Zhang et al. 2026 (https://arxiv.org/pdf/2608.28170, synthetic damage).

Not found: an Indus "sign2vec", restoration models by Fuls, Wells or Ansumali Mukhopadhyay, or Maya and Linear A restoration benchmarks.

## 4. Practical blockers

- **Table S11 is usable.** The README in the local zip says data (including S11) is CC BY 4.0 and code is MIT. The Zenodo page lists both without saying which applies to what. The CSV has 360 rows keyed by M77 text number, each with one lost sign. Mahadevan 1977 is covered by neither licence.
- **ICIT access is by permission.** The site, https://www.indus.epigraphica.de, returned 401 and I did not try to get past it. A Nature HSSC article (s41599-023-02320-7) hit a login redirect, so the terms are (unverified) beyond a search snippet: permission from Wells and Fuls. A repo note (sources/shaunmortal_indus/research/paper_v0.5.md) records that a circulating ICIT snapshot was shared without the compilers' permission. Do not use third-party dumps.
- **Independence is unchecked.** I did not find how ICIT marks damaged signs. If Wells and Fuls worked from the same photographs as Mahadevan, their reading is less independent than the study needs. Mapping M77 numbers to Wells's sign list also needs a concordance.

## Decision (2026-11-20): dropped before sealing

A fresh Fable novelty and feasibility read rejected the study.

- **Novelty.** Partly novel for Indus only. Venkatesh & Farghaly 2023 (https://doi.org/10.59720/22-256, read in full) predicts signs for about 100 damaged ICIT texts but never scores them.
- **Feasibility.** It fails. Of the 360 Table S11 texts, 43 link to an ICIT object through `experiments/old_registers/registers.csv`. Of those 43, ICIT:
  - marks the same sign as lost in 23;
  - is one sign shorter, so it sees no gap, in 11;
  - gives a full reading of a different length in 5;
  - gives a full reading of the same length, so the text can be scored, in 4.
- **Extrapolated size.** About 30-40 of 360 could be scored even with a full concordance. That gives a confidence interval of about ±15 points.
- **Licence.** Our ICIT copy has no stated terms, so publishing a score for each object would republish ICIT readings.
- **Kept as a possible half-day descriptive note** (not run): how often the second edition confirms vs reads a lost sign. Hand-check the 4 scoreable and 11 "no gap" links against CISI first, and stop if fewer than 3 of the 4 hold.
