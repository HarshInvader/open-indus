# Research sweep, 2024-2026: methods and data the project has not used (board task #9, H5)

## Conclusion

1. **No new bilingual and no new readable text beside Indus signs** turned up anywhere in 2024-2026. The anchor situation is unchanged.
2. **There is one new inscribed object found abroad:** a round Gulf-type seal with Indus signs and a humped bull from Umm al-Quwain, UAE, reported around April 2026. It is known only from a news aggregator. The primary report, the reading and the findspot are all still missing.
3. **Four items are worth acting on:**
   - a masked-sign restoration dataset from IIT Hyderabad (open, Nov 2026);
   - an open Indus glyph image set alongside proto-cuneiform and proto-Elamite glyphs (ivc2tyc, MIT, PCI-recommended);
   - a 2026 Zenodo preprint making one sharp sequence claim we can test in minutes;
   - the Linear Elamite corpus (already local) used as a *real-script* known-answer test for the M1 crib attack.
4. **Everything else is one of three things:** already in the atlas or literature map, a fringe reading, or data available only "on request". We may not contact anyone, so request-only data is out of reach.

Method:
- 17 web searches covering arXiv, ACL, Zenodo, Academia, journals and excavation news, plus direct reads of record pages and repositories.
- Repo coverage was checked by grepping `docs/` and every `experiments/*/RESULTS.md`.
- Blocked: harappa.com (403); Zenodo file downloads and the API intermittently (403 or rate limit; record pages worked through WebFetch); Academia.edu (403).

## Items

| # | Item | Date | What it claims or adds | Already covered? | Action |
|---|---|---|---|---|---|
| 1 | Round Gulf-type softstone seal, Indus signs + humped bull, Umm al-Quwain, UAE ([aggregator](https://ittihaas.com/api/apps/685bf8c05cf93a74890518d0/functions/newsSharePage?newsId=69db8bcd9150f8827bc41491&slug=bronze-age-seal-found-in-uae-confirms-direct-maritime-trade-with-indus-valley)) | about Apr 2026 | A new foreign-found Indus-sign text, dated c. 2300 BCE. Site (Tell Abraq?), excavator and sign reading not given. | "Umm al" appears once in the repo; this object is not in the M1 foreign corpus. | **Task added (M1).** |
| 2 | Indus masked-sign restoration: code, splits, predictions, Kanichira, Singam, Katyal, Somala (IIT Hyderabad), [Zenodo 24164070](https://zenodo.org/records/24164070), CC BY 4.0 + MIT, 6 MB | 12 Nov 2026 | A neural sign-restoration model with public splits. Corpus and model not described on the page. | No | **Task added (M5).** Bench it against our n-gram baseline on family-level splits (splits_v2). Check whether near-copy families leak across their splits. |
| 3 | Dominik, *Constructional Grammar and Semantic Constraints in the Indus Script*, [Zenodo 23307028](https://zenodo.org/records/23307028) | 12 Oct 2026 | Held-out NLL gain of only 0.014 nats (CI 0.010-0.018) on 6,778 tokens; the author says the contexts were chosen in advance, so not independent. Sharp claim: W090 never follows W520 (0/136) but follows W740 69/994 (7%). Corpus inputs are withheld. | No | **Task added (M5).** Test the W520/W740 → W090 contrast on ICIT and M77 with a family-level null. |
| 4 | Ivc2tyc: Indus vs Tibetan-Yi Corridor scripts by hybrid vision embeddings ([arXiv 2503.21074](https://arxiv.org/abs/2503.21074); [Zenodo 20755243](https://zenodo.org/records/20755243); GitHub oohalakkadi/ivc2tyc, MIT; PCI Archaeology recommended) | 2025-26 | Claims Tibetan-Yi scripts (Naxi Dongba, Yi, Ba-Shu) look more like Indus than proto-cuneiform or proto-Elamite do. Repository ships glyph image sets for Indus, proto-cuneiform, proto-Elamite and five Tibetan-Yi scripts. | Shape look-alikes are closed as a phonetic route (atlas 8.1-8.3). This dataset is new. | **Task added (M6/M5).** Red-team the claim with a shape-complexity-matched null. The images are a reusable asset (license per dataset to be checked). |
| 5 | Linear Elamite edition: Desset et al. 2026, *Linear Elamite Texts from Susa* (OrientLab SM 10); 2026 press wave | 2026 | Full edition of the Susa texts. The decipherment rests on royal names, the same kind of anchor M1 needs. | Yes: `experiments/elamite_bridge` (HLED corpus local, 45 docs). | **Task added (M1).** Use Linear Elamite as a real-script known-answer test of the M1 crib attack: can the method recover the name-anchored values from LE texts at n = 20-45, given only a name list? |
| 6 | Zhang & Sheng, *Can Statistics Tell Whether an Undeciphered Text Is Language? Calibrated Tests on the Voynich Manuscript*, [arXiv 2610.34499](https://arxiv.org/abs/2610.34499) | Oct-Nov 2026 | Method: write both hypotheses (meaningless copying vs enciphered language) as generative programs, fit each with the same search budget, and judge them on held-out statistics. Adds a decipherment-free language signal ("the same word pairs keep sharing a line") calibrated on 28 texts in 16 languages, plus planted messages. No code link. | The principle matches atlas 3.x and SIGIL. The line-co-occurrence signal does not apply: Indus texts average 4.6 signs on one line. | **No task.** Noted as the best statement of the "equal search budget, held-out statistic" standard. Cite it in the method section of any language-vs-code reopen. |
| 7 | Raghavendra, SIGIL, arXiv 2608.02999; Tiwari 2026 NLP4DH | 2026 | Read in full for task #6; see `experiments/bench2026/RESULTS.md`. | Yes | None |
| 8 | Nair, arXiv 2604.17828 (synthetic-baseline scorecard) | Apr 2026 | Indus sits between heraldic and administrative baselines. | Yes (literature map) | None |
| 9 | Dixit et al. 2025, *Deep Learning in Archiving Indus Script and Motif Information*, JCAA 8(1):156-169, doi:10.5334/jcaa.175; GitHub DM-BiCLab | May 2025 | YOLOv3 sign detection, MobileNet sign classification and motif identification on seal photos. The repository holds only sample data; full data is "from authors upon request". | No | **No task.** Request-only data, and contacting anyone is barred. Only the sample folders are public. |
| 10 | Kotada Bhadli "caravanserai", Shirvalkar, Prasad & Rawat 2025, doi:10.1016/j.anthro.2025.103409 | Sep 2025 | Three enclosures; finds reportedly include steatite seals and weights (secondary source only). Possible inscribed objects with a trade context. | Kotada Bhadli is in `firing_stage` (pottery marks), not as a seal context. | **No task yet.** Paywalled journal. Add only if an open copy lists inscribed finds. |
| 11 | Rajan & Sivanantham 2025, 15,184 Tamil Nadu graffiti marks from 140 sites | Jan 2025 | Shape parallels for about 90% of marks. | Yes: `experiments/tn_brahmi_graffiti`, board #7/#13 | None |
| 12 | Monroe, Kelley, Born & Sarkar 2025, *Recent progress in deciphering Proto-Elamite*, NEA 88(4):316-323; Born et al. multimodal sign-composition model (via [arXiv 2506.19208](https://arxiv.org/abs/2506.19208) review); Cambridge Element *Proto-Elamite* (2026) | 2025-26 | Methods for internal sign composition in an unread script. No values. | Proto-Elamite is partly used (`protocuneiform`, codelib). | **No task.** Nothing validated on a known answer. |
| 13 | Mukhopadhyay 2025: SSRN 5079207 (fish signs = gems, *maṇi*); centenary-volume chapter (in press) | 2025 | More of the administrative/logographic reading, plus a Dravidian gem-word. | Her 2019-2023 claims are in the atlas (5.1) and literature map. | **No task.** Predictions are not stated in testable form. If wanted, the "fish = gem" claim could be checked against find context (bead and lapidary loci). |
| 14 | Venkatesh & Farghaly 2023 (J. Emerging Investigators; ICCCNT): Markov models for missing signs and for anomalous West Asian texts | 2023 | Earlier version of what paragorth ANCHORS §1 and task #1 already do. | Effectively yes | None |
| 15 | AI-EPIGRAPHY interactive tool (ACM, late 2025) | 2025 | Z-tests, collocations, n-grams. | Method covered | None |
| 16 | Kriger & Hunt 2026 (3 papers); Adelman 2026 | 2026 | Benched in task #6. | Yes | None |
| 17 | Gulf/Iran: Laursen 2010, Frenez et al. on Salūt (Oman), Vidale & Frenez on the Konar Sandal cylinder | before 2024 | No 2024-26 finds located. | Partly (Laursen, Konar in repo) | Feeds task #1 only. |
| 18 | ASI conference *Decipherment of Indus Script: Current Status and Way Forward*, 20-22 Aug 2025 ([ASI PDF](https://asi.nic.in/admin/whatsnew/download/771)) | Aug 2025 | Programme only; no proceedings found. | No | None until proceedings appear. |

## Searches that found nothing new for 2024-2026
- New inscribed seals at Rakhigarhi, Binjor, Lakhan-jo-daro, Dholavira, Khirsara, Gonur, Shahdad, Jiroft or Mahtoutabad.
- New Meluhha cuneiform texts.
- New Indus-sign seals at Failaka, Saar, Qala'at al-Bahrain or Salūt.
- Any decipherment method validated on a known script at Indus text length. The closest is the SIGIL and Voynich-calibration standard, which is negative in spirit.

## Not checked
- Puratattva, Ancient Asia, South Asian Studies and Heritage (Kerala) tables of contents. These are not indexed well by the search tool, and the journal sites were not crawled.
- Pakistani excavation news in Urdu or Sindhi.
- Indian Archaeology – A Review volumes after 2019.
- Any of these could hold inscribed finds with context. A human with library access is the better route (`docs/HUMAN_LEADS.md`).
