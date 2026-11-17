# Open-access per-object data harvest (no tests run)

## Findings first
1. **No stalled test becomes runnable.** Open sources reachable without a login give 1 object-level firing stage (a non-script mark), 0 new inscribed bangles and 0 new texts with a readable sign sequence. firing_stage, bangle_oval, new_finds `score.py` / `score_leads.py` and magnitude all stay blocked. None of them was run.
2. **The best new source is the ASI e-publication server.** `asi.nic.in/admin/publications/ePublicationReportsDetails/download/<id>` serves full PDFs, and ids 1-61 respond. Id 10 is **MASI 110, Excavations at Kalibangan: The Harappans, Part II** (Lal et al. 2020, 876 pp). Its catalogue entries give the registration number, trench, level, form and dimensions for 34 inscribed or graffito objects. 12 of the 34 match ICIT exactly by excavation number. That proves the excavation number links report entries to ICIT rows reliably.
3. **There are 22 candidate new Kalibangan objects, but their texts are unread.** Kalibangan Part I, which would hold the seals, sealings and the main pottery-graffiti chapter, is **not** hosted. I tried four URL patterns and all returned 404.
   - The 22 objects have no ICIT excavation-number match: 7 inscribed chaklas (ring-base dishes), 7 terracotta gamesmen, 2 copper tools with stroke marks, 1 cake, 3 figurines with graffiti, and 1 burial jar.
   - Sibling gamesmen in the same series are in ICIT as K-459 to K-475, so many of the 22 are probably already in ICIT under other numbers.
   - The photographs are JPEG, rotated and about 8-10 px/mm. No sign sequence is legible enough to transcribe, so every row is marked `needs human`.
4. **Gandi Umar Khan (Gomal plain) has a Mature Harappan unicorn seal.** The site is absent from ICIT. The seal's upper edge, which carries the text, is broken off, so there is no readable text.
5. **Rehman Dheri (Ancient Pakistan 10) has 314 marked sherds** with trench, layer and level per sign type. 190 are stratified, and most sit just above the base of storage jars. These are Early Harappan marks with no firing stage given, and the sign forms are only in a chart. That makes the data useful for potters_marks (precursor signs), not for firing_stage. It is not parsed into rows.

## Rows obtained per target
| Target | Need | Obtained | Notes |
|---|---|---|---|
| (1) pottery with firing stage + form | ~200+ | 9 rows in `pottery_marks.csv`; firing stage known for **1** (Kalibangan Burial-1 urn, "prefiring graffiti mark", cross lines in a rectangle, not a script sign) | 7 chaklas with form + diameter (12-36 cm) + period; stage not stated |
| (2) inscribed bangles not in ICIT | >=19 | **0** (`bangles.csv`: 1 row, K-445 terracotta kangan, already ICIT; gives inner/outer diameter 6.20/7.85 cm) | Dholavira 2015 report (already in new_finds/raw) lists ~95 stoneware bangles with diameters, all uninscribed except one graffito fragment (Fig. 8.10, unnumbered) |
| (3) new post-2018 texts, readable | any | **0 readable**; 22 candidate objects + 1 seal without text (`new_texts_extra.csv`, `scored=no`) | All sign readings: needs human |
| (4) dims/mass/findspot/period | ~40 per class | 34 Kalibangan objects with trench/reg/level (`context.csv`); dims for 12 (chaklas, kangan, axe, chisel); no masses | Copper K-121/K-122 dims duplicate ICIT |

Transcription confidence: context fields are copied from catalogue text (high). Two registration numbers may contain typos: "43278" is out of range for the series, and 21623(b) carries a suffix. No sign was read from any figure.

## Which tests become runnable
- **firing_stage**: no. There is 1 object-level stage (a non-script mark), against the 40-60 post-firing held-out texts needed. Still needs the HARP sherd DB or Kalibangan Part I / MASI 98.
- **bangle_oval**: no. There are 0 eligible new bangles.
- **new_finds score.py / score_leads.py**: no. There are 0 scorable texts. If a person reads the 7 chaklas and 7 gamesmen from MASI 110 Figs 14.1-14.6 and 21.63-21.64, and checks them against CISI 3.1 K-numbers, there might be up to ~10 single-sign or short Kalibangan texts. These would come from a site already in M77/ICIT, so they would not be an out-of-sample site.
- **magnitude**: no. That needs ~40 objects in one class. Chakla diameters (n=7, texts unread) are the only new size series.

## Sources reached / blocked
| Source | Status | Yield |
|---|---|---|
| Ancient Pakistan OJS (`http://ojs.uop.edu.pk`; https times out) | reached; robots allows; 35 issues, 333 articles indexed (`work/ap_index.json`); 12 PDFs downloaded | Kenoyer 2021 painted script (already used by firing_stage); Rehman Dheri marks; Gandi Umar Khan seal. No HARP reports here |
| ASI e-publications (`asi.nic.in/.../download/<id>`) | reached; ids 1-61 PDFs (HEAD-probed, 6 downloaded) | MASI 110 Kalibangan pt II (id 10). Ids 15-19 = IAR 2009-14 (already in new_finds). Ids 23-61 look like older IAR volumes (by size), not checked. No IAR after 2013-14 found |
| Mohenjo-daro research journal (Sindhi Adabi Board OJS) | reached | Kenoyer, "Origin, context and function of the Indus script": narrative counts only (e.g. 13 post-firing + 4 pre-firing Ravi-phase sherds), no per-sherd table |
| Heritage: J. Multidisc. Stud. Archaeol. (Kerala) | blocked: 403 (http) / 503 (https) to scripted fetch; not bypassed | none |
| Pakistan Heritage (Hazara U.) | DNS/URL error | none |
| Zenodo API | 400 to query syntax used; web search found only an unvetted "decipherment" record | none |
| GitHub / OSF | GitHub search reached: repos only re-package M77/ICIT/CISI; OSF endpoint 404 | none |
| harappa.com (Kenoyer 2020, Kenoyer & Meadow 2010 PDFs) | not attempted (403 to fetchers, per brief) | the per-sherd HARP tables are there |
| Fuls 2022 corpus / 2023 catalogue | ResearchGate/Academia/Scribd only (login) | none |
| Man and Environment, Puratattva, J. Asian Civilizations | no open per-object PDFs found | none |

## For a person (add to HUMAN_LEADS)
- Read the chakla and gamesman signs in MASI 110 pt II Figs 14.1-14.6 (pp. 840-851) and 21.63-21.64 (pp. 1221-1223), at full PDF resolution or from the printed volume. Map the registration numbers to CISI 3.1 K-numbers.
- MASI 110 **Part I** (Lal et al. 2015, ch. "The inscribed material" by B.B. Lal) is not on the ASI server. It probably holds per-sherd graffiti with pre/post-firing for ~90 Kalibangan graffiti. Ask ASI Publications, or check whether a later upload id exists (the HEAD scan stopped at id 110).
- Kenoyer 2020 / Kenoyer & Meadow 2010 on harappa.com (normal browser) remain the single best unlock for firing_stage.

## Files
- `build_tables.py` builds `pottery_marks.csv`, `bangles.csv`, `new_texts_extra.csv` (new_finds columns) and `context.csv`.
- `tools/fetch.py`: polite cached fetcher, 3 s delay, logs to `fetch_log.jsonl`. `tools/ap_index.py` and `tools/ap_get.py` index and fetch Ancient Pakistan. `tools/kbg_items.py` extracts the MASI 110 entries.
- `raw/<source>/`: untrusted downloads, never executed. `work/`: extracted text and figure renders.
