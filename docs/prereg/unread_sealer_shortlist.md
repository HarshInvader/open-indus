# Unread-sealer shortlist: which sealed tablets with no legend read are worth a person's look? (sealed v2; no control was ranked before sealing)

Status: **v2, sealed 2026-11-25** (tag `unread_sealer_shortlist`) after one fresh review. Decisions ruled below. Drafted by Fable from `docs/fable_brief10.md`, study 5. Nothing here is a result.

## Verdict of the draft, first
- The shortlist has not been made before. Atlas 9.2 closed the detector routes and the stamp-note text route. It did not rank the unread sealed tablets for people.
- Brief 10's counts reproduce: 669 Ur III, 62 Old Babylonian, 32 Old Assyrian.
- **Brief 10's kill test cannot run as written.** None of the three known cases sits in the pool it counted. The draft widens the pool so that two of them do.
- The kill test rests on **one** true positive (YBC 5447). A pass is weak evidence. A fail is a clean stop.
- The review step has no passing control. A blind eye review already missed YBC 5447 on its photo.
- Even a perfect hit is one name pair. `anchor_crossread` puts the minimum at more than 15 pairs. So this study can produce a lead for a museum request and nothing more.
- Whether that is worth half a day is the coordinator's call (Decision 1).

## Question
Among sealed cuneiform tablets from 2100 to 1600 BC whose seal legend nobody has transliterated, which few should a person open on CDLI first to look for a Gulf-type or Indus-type stamp impression?

**This is a search aid, not a test.** No Indus text is read, no key is scored, and no outcome supports or counts against any Indus reading.

## Why
- Brief 10 puts the 2027 bar near 0.1% and names one event that would move it: sealed tablets with named sealers and Indus-sign legends.
- `sealing_hunt` showed that CDLI's transliterations hide such seals. YBC 5447 carries a Gulf stamp, and CDLI gives its seal as "(not given)".
- So an unread seal section is the only catalogue trace a foreign impression could leave. Most unread sections are worn cylinder rollings. The question is whether metadata can put the few likely ones first.

## What exists already (step 0)
- **`experiments/sealing_hunt`:** 12 sealed Meluhha tablets. 10 have ordinary cylinder legends and 2 are unread (P516366, P453801). No photo of either is online. It read tablets that name Meluhha. It did not rank the unread sealed tablets as a whole.
- **Atlas 9.2, image route, closed:**
  - `stamp_detector`: recall 0.44 against a bar of 0.80, and 0 of 5 controls.
  - `stamp_zeroshot`: 0 of 5 controls.
  - `stamp_eye_review`: a blind vision reviewer marked YBC 5447 "no".
- **Atlas 9.2, text route, closed:** `stamp_positives` found 18 stamp-noted tablets. 17 are Old Assyrian envelopes with Anatolian stamps. 1 is Gulf-type (YBC 5447).
- **`gulf_seal_hunt2`:** no new inscribed Gulf-type object in the open literature, 2010 to 2026.
- **`stamp_eye_review` pool:** 707 Yale tablets from Ur or Larsa, or naming Dilmun, Magan or Meluhha. It was never reviewed, because its kill test failed. It overlaps this study in aim. It is Yale only and was picked by site, with no ranking.
- **`docs/prereg/anchor_objects.md`:** sections 2 and 4 already fix what an anchor is and how it is read. This draft uses them unchanged.
- **`anchor_crossread`, done 2026-11-25:** the minimum anchoring event is more than 15 name and legend pairs with reading direction known. A passing set certifies the pairing, not single values.
- **Not found anywhere in the repo:** a ranked list of unread sealed tablets, or a count of them outside brief 10.

## What was seen before this draft
- The repo files above, and brief 10.
- **Label-free counts** from the CDLI dump in `experiments/short_labels/raw/cdli/`. Three scratch scripts outside the repo, single process, lowest priority, each about 6 seconds. They count pool sizes, sites, periods, note types, photo flags and how many pool rows contain each context word.
- **The three known cases, row by row.** I read their CDLI text, site, period, seal note, photo flag and genre. This cannot be avoided: they are the only cases, and their features are the prior art. It means the features below were written by someone who knew the controls. See "What K0 can and cannot show".
- **Not seen:** the score or rank of any tablet, control or not. No score has been computed.

## Prior art
Opened 2026-11-25 with curl and the User-Agent `open-research-site/1.0`. Nothing paywalled was bypassed.

- **The one Gulf impression on a dated tablet.** Hallo and Buchanan 1965, in *Studies in Honor of Benno Landsberger* (AS 16), pp. 199-209, on YBC 5447. PDF opened and read: https://isac-assets.s3.amazonaws.com/isac-publications/as16.pdf
  - Buchanan found the impressions while cataloguing Yale's seals. The tablet's editors had not noted them.
  - The best impressions are "on one side and one end", with traces of two more on the other long side.
  - They sit off centre and oblique to the edge. He calls this "puzzling, since cylinder seals were customarily rolled parallel to the edge of a tablet".
  - He read the style at first as a provincial cylinder of about 1900 BC. The match was a stamp seal from Failaka.
  - So the one known case was found by a seal specialist, on the edges, and was at first taken for a cylinder.
- **CDLI's record of the same tablet.** Early Old Babylonian, "Ur (mod. Tell Muqayyar)", Administrative, dated Gungunum 10, "seal 1 (not given)", linked to a dummy record for unidentified seals. https://cdli.earth/artifacts/306518
- **Gulf-type seals.** Laursen 2010, doi:10.1111/j.1600-0471.2010.00329.x. Abstract read through the Crossref record (https://api.crossref.org/works/10.1111/j.1600-0471.2010.00329.x); the paper is paywalled and was not read.
  - The type dates "to the end of the third millennium BC".
  - Seals with Indus characters differ in shape from those without.
  - From about 2050 BC the type "became practically synonymous with the merchant communities in Dilmun".
- **Stamp and cylinder sealing in Arabia.** Potts 2010, doi:10.1111/j.1600-0471.2009.00319.x. Abstract only, through Crossref.
- **The Meluhha village near Girsu.** Parpola, Parpola and Brunswig 1977, doi:10.2307/3631775. Crossref record opened; text not read. The summary used here is from https://en.wikipedia.org/wiki/Meluhha : the references are mostly Old Akkadian and Ur III, and the village is tentatively placed at Gu'abba.
- **Gulf seals as trade evidence.** "Persian Gulf" circular stamped seals are known from Dilmun, Lothal, Failaka and Mesopotamia. https://en.wikipedia.org/wiki/Dilmun . Indus seals with script were found at Ur, Babylon and Kish. https://en.wikipedia.org/wiki/Indus%E2%80%93Mesopotamia_relations
- **Laursen 2018,** "Seals and Sealing Technology in the Dilmun Culture", doi:10.1017/9781108160186.015. Found through OpenAlex (https://api.openalex.org/works?search=Dilmun+seal+impression+cuneiform+tablet). Title only; no open copy.
- **Not opened (unverified):**
  - Laursen and Steinkeller 2017, *Babylonia, the Gulf Region, and the Indus*. OpenAlex lists it with no DOI and no open copy.
  - Lambert 1976, RA 70, 71-72, on Louvre Sb 11221, a Susa receipt with a Gulf-type impression. Cited from `experiments/stamp_positives/COUNT.md`. A Crossref search did not find it. It would be the second Gulf positive. It is not in the CDLI dump as a flagged row.
  - Gadd 1932, "Seals of ancient Indian style found at Ur". A Crossref search did not find it.
  - Vermaak 2008, "Guabba, the Meluhhan village in Mesopotamia". OpenAlex lists it with no DOI and no open copy.
  - Buchanan 1981, no. 1090. A copy is in `experiments/sealing_hunt/raw/`. I did not reopen it.
  - Owen, CUSAS 40 and Nisaba 15, the editions of the two Irisagrig tablets.
- **What nobody has published, as far as this search went:** a count of Gulf or Indus impressions on tablets beyond YBC 5447 and the Susa receipt, or any ranked search of unread seal sections. The search was short, so "not found" is weak.

## The known cases, and where they sit on disk

| Case | What it is | In the CDLI text dump | Seal note | Sealer line (`kiszib`) | In brief 10's pool |
|---|---|---|---|---|---|
| YBC 5447 (P306518) | **True positive.** Gulf stamp, Gungunum 10 | yes | "(not given)" | no | **no** |
| Nisaba 15 0371 (P453801) | Unread. Meluhhan household, Irisagrig | yes | "illegible" | no | **no** |
| CUSAS 40 1582 (P516366) | Unread. Same household | **no** (catalogue row only) | none on disk | none on disk | **no** |

- Brief 10 calls P516366 and P453801 "the two known unread Meluhha impressions" and asks that they rank in the top 5%.
- **They are not known positives.** Nobody has seen either impression. `sealing_hunt` put the chance that either is unusual below 5%.
- **Neither is in the pool brief 10 counted.** That pool needs a `kiszib` line. P453801 has none. P516366 has no text on disk at all.
- YBC 5447, the one true positive, has no `kiszib` line either.
- So the kill test in brief 10 cannot run on brief 10's pool. It can run on a wider pool for two of the three cases. P516366 cannot be ranked by any text feature.

## Count gate (label-free, run for this draft)
Gate, written before counting: the pool must hold at least 500 rows and at least one true positive that is on disk. Result: 1,909 rows and 1 true positive (1,911 in v1; see the review corrections below). The gate passes at its minimum for positives.

**Brief 10's counts, re-run.** A text is in if it has a `@seal` section, no numbered legend line, and a body line containing `kiszib`.

| Period | With a seal section | No legend read | No legend and a `kiszib` line | Brief 10 |
|---|---|---|---|---|
| Ur III | 24,804 | 1,442 | **669** | 669 |
| Early Old Babylonian and Old Babylonian | 3,269 | 469 | **62** | 62 |
| Old Assyrian | 152 | 47 | **32** | 32 |

- Ur III sites of the 669: Umma 372, Girsu 221, Puzriš-Dagan 38, uncertain 18, Irisagrig 8, Nippur 3, Ur 3, Garšana 2. Same as brief 10.
- Old Babylonian sites of the 62: Larsa 18, Dūr-Abī-ēšuḫ 11, no site 11, Nippur 8, Ur 6, Sippar 3. Brief 10 gave Larsa 17 and Ur 5, because its site table kept Early Old Babylonian apart. The totals agree.
- Old Assyrian: all 32 are Kanesh.

**The pool this draft ranks (pool W).** Ur III, Early Old Babylonian and Old Babylonian texts with a seal section and no legend line. The `kiszib` line is not required.

- **1,909 rows** under the exact rules below: Ur III 1,441, Old Babylonian 368, Early Old Babylonian 100. v1 counted 1,911, because P135986 and P423440 keep their legends under `@surface a` inside `@seal`. The other counts in this section were taken on the 1,911 rows and are kept as v1 counted them.
- 731 have a `kiszib` line. 712 have a photo flag. 742 have a line-art flag.
- Seal note: illegible 1,208; legend broken 375; uninscribed or "no linguistic content" 175; not given 110; other 43.
- Sites: Umma 622, Girsu 319, Puzriš-Dagan 185, Sippar 160, Nippur 132, uncertain 96, Irisagrig 61 (two spellings), Kisurra 57, Garšana 40, Dūr-Abī-ēšuḫ 34, Ur 32, no site 31, Uruk 30, Larsa 29, Susa 2, Ešnunna 1 (v1 searched "Eshnunna" and found 0).
- Genre: Administrative 1,583, Legal 278, Letter 44.

**Context words are almost absent from the pool.** Rows of the 1,911 whose body contains each word:

| Word group | Rows |
|---|---|
| me-luh-ha, dilmun, tilmun, ni-tuk{ki}, ma2-gan | **1** |
| The Meluhhan names (na-na-sa3, na-na-za, sa6-ma-ar) | 1 |
| dam-gar3 (merchant) | 36 |
| nam-tab-ba, tab-ba (partnership) | 21 |
| kaskal (journey) | 17 |
| zabar (bronze) | 8 |
| gug (carnelian) | 5 |
| ga-esz8, urudu, za-gin3 | 0 (the sign is `uruda`, 50 rows; see the review corrections) |

- The single Gulf-word row is the tablet that the word search in `sealing_hunt` found. So the Gulf-word feature can do nothing in this pool except put that one row on top.

**A larger unread pool sits outside the text dump (arm C, not ranked here).** 6,575 catalogue rows in the same periods have the seal field "Sx" (sealed, seal not identified) and no transliteration on disk. 1,275 have a photo flag. Sites: no site 2,758, Girsu 870, Larsa 292, Ur 153, Irisagrig 112, Susa 17. P516366 is one of them. Brief 10 did not count this group. It has no text, so only site, period and photo flag could rank it.

## Rules made exact at review (fresh review, 2026-11-25)
These replace any looser wording above or below.
- **Seal section.** It runs from an `@seal` line to the next `@` line that is not `@surface` or `@column`.
- **Legend line.** A line in a seal section that matches `^\d+[a-z']*\.`. A text with any legend line is out of the pool.
- **Period.** By the catalogue period's prefix: "Ur III", "Early Old Babylonian", "Old Babylonian". A trailing "?" counts as the period (4 rows).
- **Duplicate P-number blocks** in the text dump: the last block wins.
- **Seal note.** The `$` and `#` lines inside seal sections, lowercased. For each note, the first rule that matches wins:
  - 0 if it contains "broken", "abraded" or "seal of";
  - 2 if it contains "not given", "not copied" or "to do";
  - 1 otherwise.
  - A tablet with several notes takes its highest note score. A tablet with no note scores 1. This replaces "or no note at all" in the table.
- **Body words.** Only numbered lines outside seal sections. Delete the characters `[ ] # ? ! < >` first. A word matches only as a whole run of hyphen-joined signs, never as a substring of a sign. The sign list for copper is `uruda`. `gug` matches only the sign `gug`, not `gug4`.
- **Disclosure:** the control's body has `kaskal`, so it takes the trade point. Under the exact site rule the 2-point site tier holds 125 rows.
- **Unscored column:** the catalogue `seal_id` (276 pool rows carry an identified S-number).
- **Empty list.** If F1 or reading 3 leaves no rows, the result says "empty list" and nothing else is written.

## Ranking features, fixed now
The score is a sum of whole points. Every weight comes from the prior art above. No weight changes after K0.

| Feature | Points | Rule | Reason |
|---|---|---|---|
| Site | 2 | Ur, Larsa, Irisagrig, Irisaĝrig, Susa, Ešnunna | Gulf seals and the Gulf trade at Ur; YBC 5447 is dated by a Larsa king; the Meluhhan household at Irisagrig; the Susa receipt; Indus-type finds in the Diyala |
| | 1 | Girsu | The Meluhha village at Gu'abba |
| | 0 | every other site, "uncertain", no site | |
| Period | 1 | Ur III or Early Old Babylonian | Gulf-type seals date to about 2100-2000 BC and Dilmun-type to about 2000-1800 |
| | 0 | Old Babylonian | Mostly later than the type |
| Seal note | 2 | "not given", "not copied", "to do", or no note at all | Nobody described the impression |
| | 1 | illegible, indistinct, uninscribed, no legend, no linguistic or written content, and any note not listed here | An editor looked and read no cuneiform |
| | 0 | "legend broken", "broken", "broken seal", "legend abraded", or "seal of" a named person | An editor saw a cuneiform legend |
| Gulf word | 2 | body has me-luh-ha, dilmun, tilmun, ni-tuk{ki}, ma2-gan, or a Meluhhan name | Direct link |
| Trade word | 1 | body has dam-gar3, kaskal, nam-tab-ba, tab-ba, ga-esz8, uruda, zabar, gug or za-gin3 (one point at most) | Merchant ventures and Gulf goods |
| Named sealer | 1 | a numbered body line has the sign `kiszib` or `kiszib3`, not as part of `e2-kiszib3-ba` | Needed for anchor grade A |

- Maximum 9 points.
- **Site text:** the catalogue's provenience cut at the first "(", with "?" removed and spaces trimmed, then matched exactly. A queried site counts as the site. P306518's site is queried ("Ur ... ?"), so this rule helps the control. Disclosed at review.
- **Photo and line-art flags are not scored.** They are columns in the output. Scoring them would make K0 measure photo coverage. YBC 5447 has a photo and P453801 has none.
- **Genre is not scored.** I had thought of a point for Legal, then saw that CDLI files YBC 5447 as Administrative. Dropping it neither helps nor hurts that control. Disclosed.
- **Old Assyrian is left out of the ranking.** Its 47 unread rows are all Kanesh, where Anatolian stamps are common and known. They are not the target. (Decision 3.)
- **Ties.** A tablet's rank is the number of pool rows that score the same or higher. This is the worst case for a control.

## Kill test K0, run first
Top 5% of 1,909 is **95 rows** (rounded down).

- **K0a, the bar.** YBC 5447 (P306518) must have worst-case rank 95 or better in pool W.
- **K0b, the Ur III check.** P453801 must have worst-case rank 95 or better **with the Gulf-word feature set to zero in every row**. With that feature on, it ranks at or near the top by construction, because the word is how the tablet was found. That rank is reported for the record and decides nothing.
- **P516366** has no text on disk. It is not ranked. The result file says so.
- **Recount check.** The script must reproduce 1,909, 669, 62 and 32 exactly before any score is computed.

### Readings, fixed now
1. **K0a fails.** Stop. No list is written. Atlas 9.2 gets one line: metadata does not put the one known Gulf-stamped tablet in the top 5% of unread sealed tablets.
2. **K0a passes and K0b passes.** The list is the top 95 rows of pool W.
3. **K0a passes and K0b fails.** The list holds only Early Old Babylonian and Old Babylonian rows from the top 95. Ur III rows are dropped, because the one Ur III check did not pass. The two Irisagrig tablets stay where they already are, in `docs/HUMAN_LEADS.md`.
4. **The recount differs by even one row.** Stop and redraft. This is an integrity stop.

### Fallbacks, stated before any score exists
- **F1, ties at the cut.** If the tie block that contains rank 95 runs past it, the whole block is listed, up to 150 rows in all. If that would pass 150, the block is left out and the list is shorter. No tie-breaking feature is added.
- **F2, a dead feature.** A feature that scores more than half the pool, or no row, is reported as dead. It stays in the score. Nothing is re-weighted.
- **F3, K0b is expected to fail.** The 2-point site tier alone holds 124 rows (6.5%), more than the 95 slots, and P453801 has no trade word and no `kiszib` line. I have not computed its rank. If it fails, reading 3 applies as written. Narrowing the site tier to Irisagrig to rescue it would be tuning to the control and is not allowed.
- **Any other change after K0 makes the run invalid.**

### What K0 can and cannot show
- **There is one true positive.** P453801 is an unread candidate, and K0b tests only whether its site and period carry it.
- **A noise ranking passes K0a 5% of the time.** So a pass is evidence at about 20 to 1 at most, and less in practice, because I wrote the features after reading the control.
- **A pass cannot give a recall.** With 1 of 1 found, the 95% lower bound on recall is 5%.
- **A pass cannot show the list holds any foreign impression.** It shows the score does not bury the one known case.
- **A fail is informative.** If features written with the control in view still miss it, the ranking is noise and the study stops.
- **Blinding is not possible.** The control's site, date and note are the prior art. A fresh agent given the prior art would learn the same facts.
- **A second true positive would change this.** Louvre Sb 11221 is the candidate. It is not on disk.

## Output
Only if K0a passes.

- **File:** `experiments/unread_sealer_shortlist/shortlist.csv`, plus `RESULTS.md` and the script.
- **Columns:** P-number, CDLI page link, publication, site, period, the six feature scores, total, worst-case rank, photo flag, line-art flag, the name on the `kiszib` line if any.
- **No image is downloaded, stored or published.** The list holds links to public CDLI pages. P-numbers, scores and links can be republished (`docs/prereg/stamp_detector_priorart.md`, section 2).
- **Two blocks:** rows with a photo flag, which a person can open now, and rows without, which would need an image request. Agents send no request. Nobody is contacted in this study.
- **Review sheet, for a person.** For each row: are the edges shown; is an impression visible; is it a rolled band parallel to the edge, or a round, oval or square face, repeated, off centre or oblique; yes, no, unsure, or edges not shown.

## Limits of the review step
- **It has no passing control.** CDLI's photo of YBC 5447 does not show the stamped edges. On Yale's photo a blind reviewer read the impression as a rolled band (`stamp_eye_review`).
- So "the reviewer found nothing" is not a null result. It may be written only as "N rows looked at, E with edges shown, 0 marked yes".
- The photo flags carry 2016 dates. Some rows without a flag have a photo now.
- The reviewer should know seal iconography. Buchanan needed the Failaka seal beside him to see what the impressions were.

## Odds, and what a hit must look like
- **About 1%** that the list leads to one confirmed Gulf-type or Indus-type impression. This is a guess. The base rate is 1 known case among about 28,000 sealed texts of these periods in the dump.
- **About 0.1%** that it is anchor grade A. That needs Indus signs in the impression and a named sealer. Only 731 of the 1,911 rows name one.
- **Lead.** A non-rolled impression on a row of the list. It is entered in `docs/HUMAN_LEADS.md` as an image request for the owner to decide on.
- **Anchor.** As fixed in `docs/prereg/anchor_objects.md`, section 2:
  - grade A is a tablet that says "seal of PN" and carries an impression whose legend is in Indus signs;
  - the reading gate in section 1 applies: two readers, at least 80% of signs agreed, hashed before any comparison.
- **Even a grade A hit is one pair.** `anchor_crossread` found that more than 15 pairs with direction known are needed, and that a passing set certifies the pairing and not the values. One hit is filed as "anchor recorded, not yet testable". No sign value is claimed and no scorecard number moves.
- A Gulf-type impression with no Indus signs, like YBC 5447's banquet scene, is grade C. It adds a second positive for future kill tests and nothing else.

## Compute
- One script, single process, `nice -n 20`, Python with `-I`, under one minute. It reads the two CDLI files only.
- It does not take the Indus compute lock and reads no Indus data.
- No download. No network.

## Biggest risks
1. **The review cannot see the target.** Edges are often missing from photos, and the one control was missed by eye. The list may be unusable however well it ranks.
2. **K0 is one case, read in advance.** A pass means little.
3. **The Ur III arm is likely to drop out** (F3), leaving a list of about 95 or fewer Old Babylonian rows.
4. **The larger unread pool is not covered.** 6,575 sealed rows have no text on disk.
5. **No route to the bar.** The best outcome is one pair against a need for more than 15.

## Decisions, ruled 2026-11-25 (the coordinator asked that this study stay cheap and short)
1. **Run.** It costs under a minute of CPU and turns "look for foreign seals" into a list of P-numbers. Nothing is added beyond this draft.
2. **K0b is a bar,** as in reading 3. A failed K0b drops the Ur III rows.
3. **Old Assyrian is left out.**
4. **Arm C is left out.** No text is on disk, so it could only be ranked by site and period.
5. **Review: nobody yet.** The list goes to `docs/HUMAN_LEADS.md` for the owner to decide on. No agent contacts anyone.
6. **The `stamp_eye_review` pool stays closed,** as in atlas 9.2.

## Pre-seal checklist
- A fresh review of this draft.
- Decisions 1 to 6 ruled (done, see above).
- Hash this file into `docs/prereg/HASHES.txt`, then write the script, then hash the script, then run K0.

## Review notes not taken
- The reviewer asked that "more than 15 pairs" read "at least 15". Not taken: `anchor_crossread` reading 4 restates the minimum as more than 15 pairs, because cell R1 failed at 15.
