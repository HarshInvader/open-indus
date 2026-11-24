# Count gate: stamp-sealed tablets with open editions (edition full-text sweep)

Run 2026-11-24. One agent, about 1.5 hours. Rows are in `positives.csv`. Requests used the User-Agent `open-research-site/1.0`; CDLI pages were fetched 61 s apart. No email was sent. Nothing outside this folder was edited.

## Verdict

**18 tablets count under the frozen rules, so the gate (10 or more) passes by the letter. Only 1 of the 18 is a Gulf-type stamp.**

- 1 Gulf-type: YBC 5447 (Gungunum 10).
- 17 Old Assyrian tablets and envelopes from Kültepe and Alişar with Anatolian stamp seals.
- 0 Indus-type. 0 from ED III, Old Akkadian or Ur III. 0 from Babylonia other than YBC 5447.

The pass rests on the rule "any stamp seal, ideally Gulf or Indus". If the gate is meant for the Babylonia and Gulf horizon, the count is 1 and the gate fails. The coordinator should decide which reading applies before any design.

## What this means for the sweep

- A recall test on the 17 Old Assyrian rows would measure one thing: whether a search finds the word "stamp" in CDLI's Old Assyrian transliteration notes. All 17 were found exactly that way.
- The one Gulf positive fails that test already. CDLI gives the YBC 5447 seal as "(not given)". Its stamp is stated only in the print edition (AS 16, open PDF).
- So a sweep of CDLI text can reach Anatolian stamps on Old Assyrian envelopes, which are well known and not the target. A sweep for Gulf stamps would have to read open edition PDFs, and there is one known positive to test it on.

## Correction to `sealing_hunt`

`experiments/sealing_hunt/RESULTS.md` says the stamp scan of 135,198 CDLI texts found only brick stamps. Its own `stamp_scan.csv` lists Old Assyrian rows with notes such as "(2 stamp seal impressions)" (for example P293711, P361463, P272900). The statement holds for Babylonian tablets, not for the whole dump. That file was not edited.

## How the count was made

1. Read atlas 9.2, `RESEARCH_STATE.md`, `sealing_hunt`, `gulf_seal_hunt2` and the stamp-detector prior art.
2. Scanned the local CDLI dump for stamp, Stempel, cachet, Dilmun and Gulf, in window periods:
   - every catalogue field (353,283 rows);
   - every ATF note line (135,198 texts).
   - Brick stamps and physical seals were dropped.
3. Opened the live CDLI page of each candidate and confirmed the stamp note, the period and the transliteration (21 pages, all HTTP 200).
4. Downloaded AS 16 from ISAC and read Hallo and Buchanan on YBC 5447 (pp. 199-209).
5. Ran 9 web searches for Gulf or Dilmun impressions on tablets from Ur, Larsa, Tell Sifr, Susa, Failaka, Bahrain, Mari and Sippar. They returned YBC 5447 and one Susa tablet, nothing else.
6. Searched the local Yale catalogue harvest (about 18,000 Ur III and Old Babylonian records) for "stamp": one queried Late Old Babylonian note.

## Rules as applied

- **Stamp evidence.** The source must say "stamp seal" outright. "(stempel)" alone and notes ending in "?" do not count.
- **Date.** For the Old Assyrian rows the basis is CDLI's period field, "Old Assyrian (ca. 1950-1850 BC)". No single tablet was dated by eponym here.
- **Edition.** A CDLI transliteration with inline seal notes counts as an open edition, as the brief allows. Two of the 17 are marked unpublished on CDLI but carry a full transliteration.
- **One object.** A tablet and its envelope share one P-number and count once.

## Near misses (do not count)

- **Louvre Sb 11221, Susa.** Gulf-type impression on a receipt naming Milhi-El son of Tem-Enzag (Lambert, RA 70, 1976, 71-72). Unverified: no source could be opened, and no open edition was found. It would be the second Gulf positive.
- **Susa tablet from the Kutir-Nahhunte I archive** with a Dilmun-style impression, known from an Encyclopaedia Iranica snippet only. It may be the same object as Sb 11221; not resolved.
- **CBS 391 (P257839),** Old Babylonian. CDLI states "2 stamp seal impressions on lower end of Rev." No transliteration exists.
- **YBC 6795 (P307811),** Late Old Babylonian. Yale's note reads "anepigraphic stamp seal(?)". The reading is queried and the date sits at or after 1700 BC.
- **TCL 4 94 (P357429) and AKT 1 60 (P360519),** Old Assyrian, with ambiguous notes.
- **BM 28714 (P208506),** Ur III bulla with four stamp impressions and no text.
- **UM 29-16-639, N 6906, N 6976, CBS 14278,** Nippur, undated, no editions.

## Blocked or closed sources (not bypassed)

- harappa.com PDFs (Laursen 2010, Laursen 2016): 403.
- academia.edu (Laursen, Dilmun sealing paper): 403.
- iranicaonline.org: 403.
- collections.louvre.fr: 429, tried three times.
- Laursen & Steinkeller 2017: not open access (OpenAlex lists no open copy).
- Lambert, RA 70: no open copy found.
- Yale's collection record page needs JavaScript; the IIIF manifest and the local harvest were used instead.
- Not searched for lack of time: BDTNS, ORACC, Kjærum's and Eidem's Failaka and Bahrain volumes (print only, per `gulf_seal_hunt2`).

## Limits

- The 17 Old Assyrian rows are a floor. Kültepe has many more stamp-sealed envelopes in print; only those with a CDLI note were counted.
- The Gulf count of 1 matches every earlier pass in this repo. Nine more searches did not change it.
