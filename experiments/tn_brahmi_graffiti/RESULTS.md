# Graffiti marks beside Tamil-Brahmi: count and power gate (board #7, M3, agent H6)

## Verdict: gate not passed, test not run (untestable at present)

The most complete open record has 20 secure sherds carrying both a Tamil-Brahmi text and a graffiti mark (21 with one doubtful). That is below the 30 the gate requires. The mark on none of them is identified as a specific graffiti sign, so the usable n for "does mark X go with word Y" is **0**. The test was not run.

Even with 20 identified marks, the pre-registered test would find only very strong links. Power is 0.25 at odds ratio 3 and 0.57 at OR 10 for the commonest mark, and 0.08 / 0.42 for a mid-frequency mark. About 60 identified sherds would give 0.94-0.97 power at OR 10.

There is one descriptive pattern; it is not a test result. Where the catalogue places the mark, it sits at the END of the word or text in 16 of 18 cases (start: 2). In 8 of 20 secure cases the word before it ends in the name ending -ṉ/-ṇ. This matches the authors' own statement that graffiti are "noticed in the final position of the Tamiḻi inscriptions". Every case is Early Historic (c. 600-100 BCE), 1,000+ years after the Indus script, and says nothing yet about Indus signs.

## Data
- **Source found (open, official):** Rajan & Sivanantham 2026, *Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi*, TN State Dept of Archaeology, Vol. I and Vol. II, free PDFs on tamildigitallibrary.in (items 062969, 062968). The PDFs are saved in `raw/`; they are untrusted data and were only text-extracted (`pdftotext`) and rendered (`pdftoppm`).
  - Vol. I: 15,184 graffiti sherds and 1,570 Tamiḻi sherds from 140+ sites.
  - Vol. II, Appendix I: per-sherd list of the 1,570 Tamiḻi sherds (site, trench, depth, ware, reading). Appendix III: photographs.
  - This supersedes Mahadevan 2003 for Tamil Nadu pottery: the authors say it covers every excavated Tamiḻi sherd, including unpublished ASI Keeladi material.
- **2025 study** (*Indus Signs and Graffiti Marks of Tamil Nadu*, 145 pp.) is also free on tamildigitallibrary.in; not needed here.
- **Graffiti API** `api.tamilknowledgecampus.in/graffiti/sites`, `/sites/<site>`, `/sign/<n>` returns site × sign counts only (9,349 occurrences, 53 sites); `raw/sites.json`. It has no sherd-level records and no Brahmi link. `tngraffiti.in` sits behind a Cloudflare challenge, so I did not use it.
- **How "both" was counted:** the authors' own flags in the Appendix I reading column, `#` (a mark next to the letters; checked on the photo of Kodumanal-TU-PU_399, App. Plate 34), `Graffiti`, and the Tamil `குறியீடு` ("symbol"). Rows: `both_sherds.csv`.

| Site | Sherds with text + mark |
|---|---|
| Kodumanal | 5 |
| Keeladi | 5 |
| Alagankulam | 5 |
| Arikamedu | 2 (+1 doubtful) |
| Korkai | 2 |
| Marungur | 1 |
| **Total** | **20 secure, 21 with the doubtful one** (1.3% of 1,570) |

One more Alagankulam sherd (`_004`) reads only "Graffiti?" with no text, so it is excluded. Thulukkarpatti, Sivagalai and Porunthal have Tamiḻi sherds but no flagged mark.

**Mark identity:** the catalogue writes `#` and never gives the graffiti sign number. The concordance (Vol. II ch. 6) indexes graffiti by catalogue number (`KLD-G-…`), and that numbering is separate from the Tamiḻi catalogue. No mark is linked.

## Power (planted control; `power.py`, `power.json`)
Planted answer: one mark goes with -ṉ words at a fixed odds ratio. The test is a Holm-corrected one-sided Fisher test over 8 mark types with Zipf frequencies, using an -ṉ share of 0.40 (taken from the 20 sherds), 1,000 simulations. Type-I rate with no plant at n = 20: 0.007.

| Planted mark | OR | n=20 | n=30 | n=60 | n=120 |
|---|---|---|---|---|---|
| commonest | 3 | 0.25 | 0.38 | 0.70 | 0.96 |
| commonest | 10 | 0.57 | 0.75 | 0.97 | 1.00 |
| commonest | ~∞ | 0.82 | 0.98 | 1.00 | 1.00 |
| rank 3 | 3 | 0.08 | 0.17 | 0.37 | 0.74 |
| rank 3 | 10 | 0.42 | 0.65 | 0.94 | 1.00 |

## Hypotheses
| Hypothesis | Verdict |
|---|---|
| ≥30 sherds with both text and mark exist in open sources | Refuted for Tamil Nadu (20 secure); Sri Lanka not yet counted |
| Specific marks go with specific words or name endings | Untestable (0 marks identified; power ≤0.57 even at n = 20) |
| Marks sit at the end of the written word | Descriptive only: 16/18 placed, no null |

## Not checked, and what would make it feasible
1. **Unflagged marks.** I did not inspect all ~100 photo plates. The authors may have flagged marks inconsistently, so 20 is a lower bound for sherds the catalogue explicitly marks.
2. **Mark identification.** Each of the 20 marks needs to be cropped from the App. III photos and assigned a Rajan-Sivanantham base sign (1-42). This is a visual transcription job; doing it double-blind would be best.
3. **Sri Lanka.** Tissamaharama (Falk 2014, "Owner's graffiti on pottery from Tissamaharama", ZAAK 6) and Anuradhapura (Coningham et al.) Brahmi sherds with symbols. These could lift n past 30. I did not fetch them.
4. Non-sherd objects (the Anaikottai seal, Karur rings) carry both and are excluded by the task's definition.

## Next experiments
- Do the photo audit of App. III plates and identify each mark (new task added).
- Add Sri Lankan sherds, then re-run the gate. If n ≥ 30, run the pre-registered test (`docs/prereg/tn_brahmi_graffiti.md`, sha256 4573d33c…).
