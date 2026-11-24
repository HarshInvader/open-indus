# Sealing hunt: is there a non-cuneiform seal impression on any Meluhha tablet?

Code: `extract.py`, `parse_bdtns.py`, `stamp_scan.py`. Run them from the repo root with `.venv/bin/python -I`. Data: `meluhha_texts.csv` (CDLI), `bdtns_meluhha.csv`, `stamp_scan.csv`, `candidates.csv`. Raw downloads are in `raw/<source>/` and are untrusted. Thumbnails of the images I inspected are in `view/`.

## Findings first

1. **Null result. I found no non-cuneiform seal impression on any tablet that names Meluhha or a Meluhhan.**
   - 12 Meluhha tablets are sealed: 9 in the CDLI dump, plus 3 from Irisagrig that only BDTNS has.
   - 10 of them have a readable legend, and every one is an ordinary Ur III cylinder-seal legend of the form "Name, scribe, son of X". These belong to Mesopotamian scribes and officials, not Meluhhans.
   - No seal legend in CDLI or BDTNS contains "me-luh-ha". (BDTNS's seal-legend search for "me-luh" returns 47 texts, all false matches such as Ur-sila-luh.)
2. **Two Meluhhan-household tablets have seals nobody has read.** Both are from Irisagrig and record oil rations for Nanasa and Samar, "men of Meluhha":
   - CUSAS 40/2 1582 (P516366): CDLI calls the impression illegible.
   - Nisaba 15 0371 (P453801): the seal is recorded, but its legend is not given.
   - Neither tablet has a photo online. They are the only Meluhha tablets where an unusual seal is still possible. I put the prior below 5%: the household carried a seal-using office, and most Irisagrig impressions are scribal cylinders.
3. **The receipts sealed by Ur-Lamma "son of Meluhha" have not been identified.**
   - Three Nin-mar accounts cite them, all from Šulgi 40: OTR 242, UDT 64 and PPAC 5 0612. "kišib Ur-Lamma dumu me-luh-ha" covers about 84 gur of grain.
   - I checked all 173 CDLI texts with "kišib₃ Ur-Lamma". The Girsu/Gu'abba Ur-Lamma seals name other fathers: Ur-Baba, Nammah, Ur-Ninmar ("dumu Ninmar-ka"), Nabasa, Lu-Suen, Kasa, Lu-dingira, and others. None names Meluhha.
   - Either his receipts are lost or unpublished, or his seal named a father with a Sumerian name. If the latter, he cannot be told apart from the other Ur-Lammas.
4. **The CDLI transliterations cannot detect this kind of seal at all. This weakens the null.**
   - The positive control is **YBC 5447 (P306518)**: a merchant contract dated to Gungunum 10 (1923 BC), probably from Ur, and the one well-known Gulf (Dilmun) stamp-seal impression on a dated cuneiform tablet (Hallo & Buchanan 1965; Buchanan 1981, no. 1090).
   - Its CDLI transliteration says only `@seal 1 $ (not given)`.
   - Its CDLI photo shows the obverse, the reverse and one edge. The stamp impressions are on the left and right edges (Buchanan), which are not photographed.
   - A scan of all 135,198 CDLI texts found no stamp-seal note on any 3rd- or early 2nd-millennium tablet; the only stamp hits are brick stamps. So a stamp or Indus impression on a Meluhha tablet would be invisible in the transliterations. It would also be easy to miss in standard CDLI photos, which often skip the edges.
   - **Correction 2026-11-24:** "only brick stamps" holds for Babylonian tablets only. The full CDLI dump also has 17 Old Assyrian stamp-sealed envelopes (Kültepe, Alişar; for example P293711, P361463, P272900, which are listed in this folder's `stamp_scan.csv`). YBC 5447 carries a Gulf stamp that CDLI does not record. See `experiments/stamp_positives/COUNT.md`.
   - What the null actually rules out is narrow: none of the 10 legible seals is foreign, and none of the 7 images I examined shows a non-cylinder impression.
5. **What I looked at.**
   - Photos: P235705 and P492732 (rolled cylinder legends clearly visible), P135969 (no impression visible, although BDTNS marks it sealed), P306518 (control; edges not shown), and P283682 (UET 5 272, Old Babylonian Ur, "illegible" seal; a cylinder rolling is visible).
   - Line art: P116633 and P137152 (cylinder legends).
   - No photo online: P374962, P114609, P206053, P140868, P453801, P516366, P516138. The British Museum website blocks scripted access (403).

## Method

- **CDLI.** The live search returns HTTP 500, so I used the local bulk dump (`experiments/short_labels/raw/cdli`: ATF plus catalogue, 135,198 texts).
  - Regex for me-luh-ha variants, plus the known names (na-na-sa₃/za, sa₆-ma-ar, sak-ku-ši).
  - 229 hits, 145 of them from the 3rd or early 2nd millennium.
  - Seal status taken from the `@seal` blocks and from `$`/`#` seal notes.
- **BDTNS.** It has moved to `bdtns.cesga.es`; the old host has a bad certificate.
  - A line search for "me-luh" (substring, 823 lines) gave 72 real Meluhha lines.
  - Seal flags come from the BDTNS "Seal" column.
  - BDTNS adds UCTIS 099 (unsealed), CUSAS 40/2 1354 and 1582, and Nisaba 33 960, which are missing from the dump.
- **Images.** I downloaded `cdli.earth/dl/photo/P*.jpg` wherever one exists. Only 5 of the 13 relevant texts have photos.
- **Stamp scan.** Searched all ATF comments for stamp, round, square, button, Dilmun, Gulf, Indus, uninscribed, illegible and anepigraphic.
  - Result: 320 texts. The stamp hits are all brick stamps.
  - The "uninscribed/illegible" hits are mostly Old Babylonian (Larsa, Ur, Kisurra), where figurative cylinders without legends are common.
- **Ur-Lamma.** Read all CDLI texts with "kišib₃ Ur-Lamma" and compared their legends and patronymics.

## Hypotheses tested

| hypothesis | result | verdict |
|---|---|---|
| A sealed Meluhha tablet carries a non-cuneiform (stamp/Indus/Gulf) impression | 0 of 10 legible seals; 0 of 7 images | not found (weak: screening sensitivity is low, see finding 4) |
| A seal legend names a Meluhhan | 0 legends contain me-luh-ha (CDLI + BDTNS) | refuted for published legends |
| Ur-Lamma dumu Meluhha's sealed receipts survive in CDLI | 0 of 173 kišib Ur-Lamma texts | not found |
| CDLI ATF flags Gulf stamp impressions | YBC 5447 recorded only as "(not given)" | refuted: ATF is blind to them |

No statistics. This is a search, not a test.

## Next steps: human actions (curator emails)

1. **Iraq Museum, Baghdad (and D.I. Owen, editor of CUSAS 40).** Ask for photos of all six faces of CUSAS 40/2 1582 (P516366), plus RTI or raking-light shots of the seal impression. Also ask for CUSAS 40/2 1354 and UCTIS 099 (IM 226931). The CUSAS 40 tablets came from the Museum of the Bible repatriation. CDLI's collection page for the Iraq Museum and the CUSAS series editors (Cornell) are the routes in.
2. **Nisaba 15 editors (Università di Messina, the Nisaba series).** Ask for their photos of Nisaba 15 0371 (P453801), especially the sealed surface, and who holds the tablet now.
3. **Yale Babylonian Collection (babylonian-collection.yale.edu, contact page).** Ask for edge photos or RTI of YBC 5447, the Gulf-stamp control. This is the only known Gulf impression on a dated tablet. It tells us what such an impression looks like on a tablet and whether any sign-like marks are present.
4. **British Museum, Department of the Middle East (britishmuseum.org/collection; Middle East department enquiries).**
   - RTI or high-resolution images of the seal BM 120573, to settle the reading sak-ku-ši vs ka-lu-ši.
   - Ask whether the unpublished BM Girsu tablets (the 1890s-1910s Tello purchases, BM 12xxx-30xxx) include Gu'abba receipts dated Šulgi 34 to Amar-Suen 6 that are sealed "Ur-Lamma" with an uninscribed or foreign seal.
   - Photos of BM 94466 (Nisaba 18 41) for completeness.
5. **Optional.** Hearst Museum, Berkeley: confirm whether HMA 9-02648 (P135969) is sealed. BDTNS says yes; the photo shows nothing.

## Citations

- Hallo, W.W. & Buchanan, B. 1965. A "Persian Gulf" seal on an Old Babylonian mercantile agreement. AS 16: 199–209. Buchanan, B. 1981. *Early Near Eastern Seals in the Yale Babylonian Collection*, p. 382 no. 1090 (YBC 5447). Read here from `raw/buchanan1981`.
- Laursen, S.T. 2010. The westward transmission of Indus Valley sealing technology. AAE 21: 96–134. Not read (harappa.com returns 403). Potts, D.T. 2010. Cylinder seals and their use in the Arabian Peninsula. AAE 21.
- CDLI bulk data (cdli.earth); BDTNS (bdtns.cesga.es). P-numbers are in `candidates.csv`.
- Earlier work: `experiments/meluhha/RESULTS.md` §5.
