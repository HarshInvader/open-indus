# Sealing generative model: count gate (plan 12, family 4)

- **Verdict: FAIL.** 4 corpora are eligible in 3 families, against the 8 corpora and 4 families that `MINIMUM.txt` requires. The family closes at the gate. No model, simulator or posterior was built.
- **Minimum:** `MINIMUM.txt`, written before any count at 2026-11-25T18:42:44Z. Its sha256 is `22d8b01ad7e1616a2a3e3a06cef4740ab1138e8bbcd3f72210c6736e390d6c55`. It is not in HASHES.txt.
- **Count script:** `count_gate.py`, run as `python3 -I experiments/sealing_generative/count_gate.py <dir of PNM listing pages>`. It writes `count_gate.json`.
- **Downloads:** all went to a new directory outside the repo. Every URL below was opened in this session unless it is marked (unverified).

## Size floor
- Indus (M77): 2,577 seal and sealing objects carry text, with 1,973 distinct sign sequences.
- **FLOOR = ceil(1,973 / 2) = 987 distinct legends per corpus.**

## Table

| # | Candidate corpus | Legends (distinct, legible) | Readings | Licence | Family | Eligible? Why |
|---|---|---|---|---|---|---|
| 1 | Ur III seal legends (CDLI impressions on tablets; ORACC epsd2/admin/ur3) | CDLI 5,771 from 25,061 `@seal` blocks; seal objects add 5,898; ORACC lemmatised units 6,553 (all local) | yes, lemmatised with POS | ORACC: the docs page footer says CC BY-SA 3.0 (the repo recorded CC0 earlier); CDLI text may be re-used under academic practice ([oracc opendata](https://oracc.museum.upenn.edu/doc/opendata/), [CDLI terms](https://cdli.earth/terms-of-use)) | cuneiform | **YES** |
| 2 | Old Babylonian seal legends (CDLI) | 3,329 on tablets; 550 on seal objects (local) | yes (transliteration) | as row 1 | cuneiform | **YES** |
| 3 | Early Old Babylonian seal legends (CDLI) | 568 on tablets; 377 on seal objects (overlap not removed) | yes | as row 1 | cuneiform | no: each count is below 987, and the family cap is already used by rows 1 and 2 |
| 4 | Old Assyrian, Old Akkadian and Middle Babylonian seals (CDLI) | 127 + 164; 58 + 189; 5 + 192 | yes | as row 1 | cuneiform | no: below 987, and the family is capped |
| 5 | Neo-Assyrian seals (CDLI, SAAo) | 9 on tablets; 13 on seal objects. CDLI lists 869 Neo-Assyrian seal objects, but only 38 have ATF | yes where given | as row 1 | cuneiform | no: 22, far below 987. The main catalogues (e.g. Herbordt 1992) are print only (unverified) |
| 6 | Mesopotamian cylinder-seal catalogues (CDLI seal objects, all periods) | 15,524 seal objects; legible legends are counted in rows 1-5 | yes | as row 1 | cuneiform | counted in rows 1-5. Most catalogue seals have no legend (iconography only, so they fail E3) |
| 7 | Achaemenid, PFS (Persepolis Fortification) | about 50 inscribed seals with Elamite legends ("nearly fifty", [CDLN 2023:2](https://cdli.earth/articles/cdln/2023-2), CC BY 4.0). An NYU abstract gives about 200 inscribed out of 4,000+ seals (page did not render: unverified) | yes, published one by one | the article is CC BY; the corpus is print or OCHRE | cuneiform (Elamite majority) | no: about 50-200, below 987 |
| 8 | Linear B sealings (Pylos, Knossos, Thebes, Mycenae nodules) | 181 W-series documents in the local DAMOS copy (TH Wu 59, KN Wb 35, KN Ws 21, PY Wr 20, PY Wa 19, ...) | yes | CC BY-NC-SA 4.0 ([DAMOS](https://damos.hf.uio.no/about/)) | Aegean | no: 181, below 987. Also, the writing is a commodity note on the nodule, not a seal legend (the seals are uninscribed glyptic), so E2 is doubtful |
| 9 | Cretan hieroglyphic seals (CHIC) | 150 seal and sealing documents (as of 1989, [Wikipedia](https://en.wikipedia.org/wiki/Cretan_hieroglyphs)) | **not read** | print (CHIC 1996) | Aegean | no: fails E1, because it is undeciphered |
| 10 | Hittite and Luwian royal and official seals | BONUS_SCRIBA `Names_in_seals.csv`: 1,383 rows, 1,077 distinct seals (Nişantepe 669, StMe VI 204, SBo II 100, ...), 1,003 with a name, title or transliteration, **715 distinct legends**. The full Nişantepe archive is about 3,400 bullae (Herbordt 2006, from a summary: unverified), print only | yes (name, title, transliteration) | CC BY-SA 3.0 ([repo](https://github.com/DigitalPasts/BONUS_SCRIBA)) | Anatolian hieroglyphic | no: 715, below 987. The full archive fails E6 (print only) |
| 11 | Ugaritic seals | a small inscribed share of the Ras Shamra cylinders (Amiet 1992 catalogue numbers run past 472, mostly uninscribed; [Ougarit site](https://archeologie.culture.gouv.fr/ougarit/fr/les-sceaux-cylindres)). Exact inscribed count not taken | partly | print | cuneiform | no: well below 987, and the family is capped |
| 12 | Egyptian scarabs and seal impressions (PNM, Middle Kingdom to early New Kingdom) | **3,507 objects** of type "Scarab, seal, scaraboid, intaglio": 3,003 with a name, 388 royal. At least **2,187 distinct legends** (distinct owners plus royal legends, a lower bound) | yes: name, title and owner per object | CC BY 4.0 ([PNM](https://pnm.uni-mainz.de/inscriptions), Zenodo dataset doi:10.5281/zenodo.1411391 (unverified: Zenodo returned 403 to our script)) | Egyptian | **YES** |
| 13 | Sasanian seals and bullae | the Met catalogue has 224 seals in all, not all inscribed ([Brunner 1978, archive.org](https://archive.org/stream/SasanianStampSealsinTheMetropolitanMuseumofArt/SasanianStampSealsinTheMetropolitanMuseumofArt_djvu.txt)). Gyselen's corpora are print (unverified) | yes | open PDF of one catalogue | Middle Iranian | no: below 987, and no machine-readable corpus |
| 14 | Chinese seals (古璽, 封泥) | no open machine-readable corpus found. The mebag.com 封泥 index returned 403 (unverified) | yes, in print | none found | Sinographic | no: fails E5 and E6 (unverified) |
| 15 | Dilmun and Gulf seals | 55 inscribed Gulf or foreign Indus-type objects (repo `experiments/foreign_corpus/foreign_corpus.csv`); most Dilmun seals are uninscribed | **not read** (Indus signs) | repo | Indus | no: fails E1, and M2 bars Indus |
| 16 | Byzantine lead seals (Dumbarton Oaks catalogue), not on the brief's list | **15,931 seal pages** in the DO sitemap. Each gives a Greek legend, an edition, a translation, and the name and offices in its title (e.g. "John protospatharios, judge of the Hippodrome and skribas") | yes | no open licence; free online use for scholarly purposes ([DO seals](https://www.doaks.org/resources/seals/byzantine-seals), [rights](https://www.doaks.org/research/library-archives/rights-and-reproductions)). Robots allow item pages at a 20 s crawl delay | Greek alphabetic | **YES** (size from the stated total, per E4; distinct-legend count not taken) |
| 17 | West Semitic seals and bullae (Southern Levant), not on the brief's list | `seals.acheros.com` is a placeholder (1 object, template pages). Avigad & Sass (WSS, about 1,200 seals) is print (unverified) | yes | none usable | West Semitic | no: fails E6 |
| 18 | Medieval Latin seals (sigilla.org), not on the brief's list | site returned HTTP 520 (unverified) | — | — | Latin alphabetic | no: not verified |

## Tally against MINIMUM.txt
- **Eligible:** 4 corpora (rows 1, 2, 12 and 16).
- **After the per-family cap of 2:** 4. These span **3 families**: cuneiform (2), Egyptian (1) and Greek alphabetic (1).
- **M1 requires** at least 8 corpora and at least 4 families. **FAIL.**
- **Even generous readings do not reach 8:**
  - Admitting Hittite (715) adds a fourth family and gives 5.
  - Splitting PNM or DO by period would break the "one tradition" rule after counting (M3).

## Closest near-misses
1. **Hittite and Luwian seals (BONUS_SCRIBA), at 715 of 987 distinct legends.** It is open (CC BY-SA), labelled with name and title, and would be a fourth family. The full Nişantepe archive (about 3,400 bullae) would clear the floor easily, but it is print only (Herbordt 2005; the royal-seal volume, 2011).
2. **Early Old Babylonian seal legends (CDLI), at 568 + 377.** This is moot, because cuneiform already fills its 2 slots.

## Bearing
- This is the third plan-12 family to stop at the same wall, after 10b.20 and 10b.21.
- Open, read and labelled data exist for cuneiform, plus single large corpora in Egyptian and Byzantine Greek. Nothing else at Indus scale is open and machine-readable.
- **Reopen with** at least 4 more open corpora, from at least 1 new family, at 987 or more distinct legends each. Candidates:
  - a digitised Nişantepe;
  - an open West Semitic corpus (WSS);
  - an open Sasanian or Chinese seal corpus;
  - a medieval Latin seal database.
