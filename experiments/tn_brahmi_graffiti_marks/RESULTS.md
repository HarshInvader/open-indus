# Identifying the graffiti marks beside Tamil-Brahmi (board #13, M3, agent H6)

## Verdict: blocked by resolution. 2 of 21 marks identified, n stays far below 30

From the published plate photographs, the marks on the 21 sherds can be named with any confidence on only **2**, and only at grade B. Kodumanal-TNSDA_075 carries a triangle with an extra stroke (base sign 40 family). Alagankulam_044 carries a drawn figure, a field symbol rather than a base sign. Five more are guesses (grade C: 14.0?, 11.0?, 12.0?, 18.0?, 1.0?), and 14 cannot be read at the printed resolution.

No open Sri Lankan sherd list was reachable, so n cannot be raised. The pre-registered test (`docs/prereg/tn_brahmi_graffiti.md`) stays unrun. The route is closed until high-resolution photos of the 21 sherds, or the excavators' own drawings of the marks, become available.

## What was done
- **Crops.** `../tn_brahmi_graffiti/crop_sherds.py` locates each catalogue label in Vol. II App. III with `pdftotext -bbox` and crops the photo above it at 200 dpi. Contact sheets: `contact_sheet_1.png`, `contact_sheet_2.png`.
- **Reference.** The base sign list is Vol. I Fig. 5.1 (pdf p. 345). It shows signs 1-45, although the text says 42.
- **Identification.** One pass by H6 (not an epigrapher), recorded in `mark_ids.csv`. A second independent pass was not possible inside one agent, so no agreement figure can be given.

| Grade | Count | Meaning |
|---|---|---|
| B | 2 | shape clear, sign family clear |
| C | 5 | a mark is visible, the sign number is a guess |
| illegible | 14 | the mark is not resolved in the printed photo |

## Side finding: the list and the plates disagree
On 2 of 21 sherds, the reading in Appendix I does not match the caption on the plate photo.
- Keeladi_ASI_035: list `[a] ##`, plate `[ṇa ṉ ta]`.
- Arikamedu_027: list `ṇakkaṉ####`, plate "undeciphered".

So the `#` flag that #7 counted is itself not fully reliable, and the 20-sherd count from #7 carries about a 10% error.

## Sri Lanka
- Falk 2014, "Owners' graffiti on pottery from Tissamaharama" (ZAAK 6: 45-94) is on academia.edu only, which needs a login. I did not use it, and there is no other open copy. From its abstract, the paper is mainly about Brahmi owners' legends; it may not catalogue symbols beside the text.
- I did not search Anuradhapura (Coningham) further.

## Hypotheses
| Hypothesis | Verdict |
|---|---|
| The 20 marks can be identified from the published photos | Refuted: 2 of 21 at grade B |
| n ≥ 30 can be reached from open sources | Not reached: TN gives 20; Sri Lanka is behind a login |

## What would make it feasible
High-resolution photos (≥600 dpi) or line drawings of the 21 sherds from the TN State Dept of Archaeology (the Keeladi, Kodumanal and Alagankulam reports may carry drawings), or the open Falk 2014 catalogue. Then two independent identification passes, then the hashed test.
