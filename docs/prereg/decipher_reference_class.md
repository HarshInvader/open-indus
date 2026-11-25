# Decipherment reference class: which features were present when a script was read, and has Indus's profile ever been read? (sealed v2; no row had been coded at sealing)

Status: **v2, sealed 2026-11-25** (tag `decipher_reference_class`). Drafted by Fable from `docs/fable_brief11.md`, section 4, study 6. No coder has run. No feature has been coded for any script. A fresh review of v1 returned 8 must-fix items and 4 smaller ones; all are applied (list at the end).

## Question
- Across deciphered and undeciphered scripts, which of five features were in hand when a script was read?
- Does a fixed rule fit at least 90% of the deciphered scripts?
- Does any undeciphered script share Indus's feature profile, and has that profile ever been read?

**No Indus text is read, no key is scored, and no outcome supports or counts against any Indus reading.** The study is a table built from published accounts.

## Why
- `docs/RESEARCH_STATE.md` rests its verdict on one sentence: "Every past decipherment rested on names fixed from outside the texts plus a known language." Nobody in the project has checked it against a list.
- The same verdict says "Only a digraphic find changes the odds". That is a claim about a reference class, and the class has never been written down.
- Brief 11 gives this study 20% odds of changing a belief. Its value is that a reader can check the prior instead of trusting it.

## What was seen before this draft
- **The two list pages**, read in full as wikitext: the Wikipedia decipherment timeline and the list of undeciphered writing systems.
- **For each listed script, the page's revision number and byte size only.** These came from the Wikipedia API. No script page was opened or read for this draft.
- **For 25 Mnamon pages, the HTTP status and byte size only.** The Mnamon index was read to get the list of scripts it covers.
- **One count from the repo:** `data/icit_texts.jsonl` has 5,679 texts and 20,066 sign tokens, median text length 3.
- **The prior-art sources** listed below.
- **Not seen:** any coded feature, any rule fit, any profile match.

**The drafter is not blind.** Fable knows the standard decipherment stories from training and expects the rule to fit most rows. For that reason the drafter codes nothing, the rule is taken from brief 11 as written, and the list comes from a stated rule on two public pages.

## Prior art
Opened 2026-11-25 with curl and the User-Agent `open-research-site/1.0`. Nothing paywalled was bypassed. Scratch copies sit outside the repo.

**Opened and read**
- **Gelb and Whiting's four cases**, as reported at https://en.wikipedia.org/w/index.php?title=Decipherment&oldid=1387594754 .
  - Type I is unknown writing with a known language: Phoenician, Ugaritic, Cypriot, Linear B.
  - Type II is known writing with an unknown language: Linear A. It is "extremely difficult to achieve on the basis of internal information only".
  - Type III is unknown writing with an unknown language. Without outside information "decipherment is typically considered impossible".
- **The same page on method.** "Many successful decipherments have proceeded from the discovery of external information", usually a multilingual text. Its list of obstacles names an unknown language, unsegmented words, an unknown reading direction and a small corpus.
- **The same page's timeline:** 29 rows, 1674 to 2022. It quotes Daniels (1988) that Palmyrene in 1754 was the first dead language recovered through its script.
- **Farmer, Sproat and Witzel 2004**, http://www.safarmer.com/fsw2.pdf , pages 1 to 40 as text.
  - The longest Indus text on one surface has 17 signs. The mean over Mahadevan's 2,905 objects is 4.6.
  - It names Daniels and Bright 1996, Pope 1999 and Robinson 2002 as the "standard reviews of deciphered or undeciphered scripts".
  - It lists what would change its view. One item is a bilingual with "a minimum of 30 or so Indus symbols" beside a deciphered script.
- **Luo, Hartmann, Barzilay and Cao 2021**, https://aclanthology.org/2021.tacl-1.5.pdf , introduction read.
  - Earlier machine decipherments of Ugaritic and Linear B assumed a known language family and given word boundaries.
  - It says these assumptions "are not applicable to many undeciphered scripts". Iberian is its example: under-segmented, with no agreed close language.
- **Luo, Cao and Barzilay 2019**, https://aclanthology.org/P19-1303/ , landing page. Ugaritic and Linear B, each against a known related language.
- **Snyder, Barzilay and Knight 2010**, https://aclanthology.org/P10-1107.pdf . Already summarised in `docs/prereg/anchor_crossread.md`.
- **Tamburini 2025**, doi:10.3389/frai.2025.1581129 , introduction read. It gives three obstacles: too few inscriptions, no known descendant language, and doubt that the signs are writing. It says every current computational attempt compares the lost wordlist with a known language.
- **Knight and Sproat 2009**, https://aclanthology.org/N09-4008.pdf , tutorial abstract. The tutorial surveys undeciphered scripts and "the prospects of deciphering them given currently available data". The slides were not opened.
- **Sproat, rongorongo approximate matches**, https://rws.xoba.com/ror/ . It finds parallel passages across tablets by string matching. It assigns no values.
- **Mnamon, Scuola Normale Superiore**, index at https://mnamon.sns.it/index.php?page=IndiceAlfabetico&lang=en . 58 scripts, each with its own page.
- **From the repo, not reopened:** the prior-art lists in brief 11 section 3, `docs/prereg/anchor_crossread.md` and `docs/RESEARCH_STATE.md` (Desset et al. 2022, Ferrara et al. 2024, Corazza et al. 2022, among others).

**Not opened**
- Pope 1999, *The Story of Decipherment* (unverified). archive.org holds it for lending only.
- Robinson 2002, *Lost Languages* (unverified). archive.org holds it for lending only. A search also returned an unauthorised copy, which was not opened.
- Daniels and Bright 1996, *The World's Writing Systems* (unverified). No open copy found.
- Daniels 1988, JAOS 108, https://www.jstor.org/stable/603863 (unverified). Landing page only. Known through the quotation above.
- Robinson 2015, Nature 526, https://www.nature.com/articles/526499a (unverified). Preview only.
- Sproat 2014, Language 90, 457 to 481 (unverified). The address tried returned a web page, not the paper.
- Coe 1992, *Breaking the Maya Code* (unverified, from memory). It is said to list five conditions: a large corpus, a known language, a bilingual, a known cultural context and pictorial references.
- Bonmann et al. 2023 on the Kushan script, doi:10.1111/1467-968X.12269 (unverified). HTTP 403.
- A recent survey of machine learning for ancient languages (Sommerschield et al. 2023) (unverified). Not located at the two addresses tried.

**What is established.** The qualitative claim is textbook. Outside information started most decipherments. An unknown script in an unknown language with no outside information is held to be undecipherable. Machine methods need a known related language and word boundaries. Indus texts are very short. This study does not retest any of these.

**What nobody in the opened sources gives.** A coded table of scripts by feature, made by coders who did not know the rule, with agreement reported, a rule stated before coding, and a count of how many unread scripts share one script's profile. The three books may hold such a table. They were not opened, so "not found" is weak.

## The frozen script list
The list is fixed here, before any coding. It comes from two pages at fixed revisions.
- Timeline: https://en.wikipedia.org/w/index.php?title=Decipherment&oldid=1387594754
- Undeciphered list: https://en.wikipedia.org/w/index.php?title=Undeciphered_writing_systems&oldid=1386509873

Status (deciphered or not) is taken from these pages. It is never judged by the project.

**Account.** Each script's primary account is its Wikipedia page at the revision given. The account is the linked page after redirects; a decipherment page is added only where the timeline links one. The address is `https://en.wikipedia.org/w/index.php?title=<page>&oldid=<revision>`. Where Mnamon has a page, it is a second fixed account at `https://mnamon.sns.it/index.php?page=Scrittura&id=<n>&lang=en`. All 25 Mnamon pages returned HTTP 200 today. Their text is not versioned, so the run saves a copy with a SHA-256 before coding.

### Rule for the deciphered set D1
Every script on the timeline, with these exclusions.
1. The page itself marks the row as disputed as a decipherment. This drops staveless runes and cipher runes.
2. The script has no page of its own. This drops the "enlarged opening script" of Ravenna.
3. The script also stands on the undeciphered list. This moves Proto-Sinaitic to the contested set.

"Brahmi, Kharosthi" is one timeline row and two scripts. Each is a row here.

| # | Script (timeline year) | Page | Revision | Mnamon id |
|---|---|---|---|---|
| 1 | Palmyrene (1754) | Palmyrene_alphabet | 1376618079 | |
| 2 | Phoenician (1758) | Phoenician_alphabet | 1387525641 | 23 |
| 3 | Pahlavi (1791) | Pahlavi_scripts | 1385710803 | |
| 4 | Demotic (1816) | Demotic_Egyptian_script | 1387003548 | 6 |
| 5 | Lycian (1821) | Lycian_alphabet | 1336944040 | 55 |
| 6 | Egyptian hieroglyphs (1822) | Egyptian_hieroglyphs | 1387646159 | 32 |
| 7 | Old Persian cuneiform (1823) | Old_Persian_cuneiform | 1383878573 | |
| 8 | Brahmi (1837) | Brahmi_script | 1385416860 | |
| 9 | Kharosthi (1837) | Kharosthi | 1379847884 | |
| 10 | Nabataean (1840) | Nabataean_script | 1376893068 | |
| 11 | Libyco-Berber (1843) | Libyco-Berber_alphabet | 1382352877 | 47 |
| 12 | Mesopotamian cuneiform (1857) | Cuneiform | 1387668614 | 39 |
| 13 | Cypriot syllabary (1871) | Cypriot_syllabary | 1383916676 | 4 |
| 14 | Old Turkic (1893) | Old_Turkic | 1383724847 | |
| 15 | Oracle bone script (1899) | Oracle_bone_script | 1387651602 | |
| 16 | Safaitic (1901) | Safaitic | 1385643189 | 66 |
| 17 | Meroitic (1909) | Meroitic_script | 1373940996 | 69 |
| 18 | Hittite cuneiform (1915) | Hittite_cuneiform | 1341776131 | 16 |
| 19 | Northeastern Iberian (1922) | Northeastern_Iberian_script | 1359640333 | 13 |
| 20 | Ugaritic (1930) | Ugaritic_alphabet | 1382309044 | 30 |
| 21 | Tangut (1930s) | Tangut_script | 1369050224 | |
| 22 | Linear B (1952) | Linear_B | 1381263317 | 20 |
| 23 | Maya (1950s) | Maya_script | 1387537194 | |
| 24 | Carian (1980s) | Carian_language | 1371669903 | 56 |
| 25 | Caucasian Albanian (2001) | Caucasian_Albanian_script | 1375555724 | |
| 26 | Linear Elamite (2022) | Linear_Elamite | 1379887485 | 67 |

The timeline links a decipherment page in two rows. Egyptian hieroglyphs also gets `Decipherment_of_ancient_Egyptian_scripts` at 1383048866. Old Persian also gets `Decipherment_of_cuneiform` at 1377477828. The timeline links `Demotic_Egyptian_script` (24,871 bytes) for row 4, `Cuneiform` for row 12, `Old_Turkic` for row 14 and `Carian_language` for row 24, so those are the accounts. v1 had other pages for rows 4, 6, 12, 14 and 24.

### Rule for the undeciphered set U
Every entry on the undeciphered list outside its "Proto-writing" and "Non-writing systems" sections that meets all of these.
1. It links to a page of its own about a script or an inscribed corpus.
2. The list does not mark its status as writing, or its authenticity, as disputed or uncertain.
3. It is not a manuscript or cipher of the medieval or modern period, and not a script invented after 1800.
4. It is a graphic script. This drops quipu.
5. It is more than a single inscription.
6. Its page has at least 4,000 bytes of wikitext. This drops Pushkarasari (2,122 bytes).
7. The list does not say that a recent proposal gives phonetic values for a substantial part of its sign list. This moves the Kushan script to the contested set. The two Khitan scripts ("partially understood") and Southwest Paleohispanic ("sign values largely known" for the group) stay in U, since the list still files them as undeciphered. Their partial values are a matter for F3.

The Phaistos Disc fails item 5. It is added by name, because the decipherment page lists it among the undeciphered and it is the standard single-object case.

**Olmec hieroglyphs are dropped (v2).** The review read the page: it calls the text a "singleton" and its status as writing unsettled. So it fails items 2 and 5, and no second exception is made.

**Espanca is not added.** The decipherment page lists it among the undeciphered. It is one inscribed stone, so it fails item 5, and it is not on the undeciphered list under its own name. It is held to belong to the Southwest Paleohispanic script, which is row U11 (the drafter's understanding; the Espanca page, 4,321 bytes, was not read). Adding it would count that script twice.

| # | Script | Page | Revision | Mnamon id |
|---|---|---|---|---|
| U1 | Proto-Elamite | Proto-Elamite_script | 1377337083 | 9 |
| U2 | Linear A | Linear_A | 1383661467 | 19 |
| U3 | Cretan hieroglyphs | Cretan_hieroglyphs | 1386486383 | 35 |
| U4 | Cypro-Minoan | Cypro-Minoan_script | 1361395878 | 34 |
| U5 | Byblos syllabary | Byblos_syllabary | 1382993728 | 3 |
| U6 | Rongorongo | Rongorongo | 1386878024 | |
| U7 | Isthmian | Isthmian_script | 1364788667 | |
| U8 | Zapotec | Zapotec_script | 1364302696 | |
| U9 | Khitan large script | Khitan_large_script | 1384399817 | |
| U10 | Khitan small script | Khitan_small_script | 1375659721 | |
| U11 | Southwest Paleohispanic | Southwest_Paleohispanic_script | 1253389624 | |
| U12 | Ba–Shu | Ba–Shu_scripts | 1374117805 | |
| U13 | Shankhalipi | Shankhalipi | 1380173053 | |
| U14 | Phaistos Disc | Phaistos_Disc | 1373685216 | 22 |

Rongorongo also gets `Decipherment_of_rongorongo` at 1377140952, which the decipherment page links beside it.

### Target row
| Script | Page | Revision |
|---|---|---|
| Indus | Indus_script | 1383975240 |

Indus is coded by the same coders, in the same shuffled order, with no mark that it is the target. It is not counted in U.

### Contested set C (coded; never in a bar)
| Script | Page | Revision | Mnamon id | Why |
|---|---|---|---|---|
| Proto-Sinaitic | Proto-Sinaitic_script | 1387678777 | 25 | on both lists |
| Kushan script | Kushan_script | 1375969649 | | partial decipherment reported in 2023 |

### Added set D2 (coded; sensitivity only)
These are deciphered scripts the timeline omits. The drafter chose them from memory, which is a selection risk. They can neither rescue nor sink the bar.

| Script | Page | Revision | Mnamon id |
|---|---|---|---|
| Anatolian hieroglyphs | Anatolian_hieroglyphs | 1384294051 | 46 |
| Ancient South Arabian | Ancient_South_Arabian_script | 1386224373 | 27 |
| Lydian | Lydian_alphabet | 1364001919 | 18 |
| Sidetic | Sidetic_language | 1387353954 | |

**T for D2, written by the lead before sealing.** Each year is that of the publication usually named as the decipherment. They are from memory and marked (unverified); D2 is sensitivity only.
- Anatolian hieroglyphs: 1973, the revised readings of Hawkins, Morpurgo Davies and Neumann (unverified).
- Ancient South Arabian: 1841, Gesenius and Rödiger (unverified).
- Lydian: 1916, Littmann, from the Sardis Lydian–Aramaic bilingual (unverified).
- Sidetic: 2002, Pérez Orozco (unverified).

### Count gate
| Set | Rows | Gate |
|---|---|---|
| D1, deciphered | 26 | at least 25 |
| U, undeciphered, without Indus | 14 | at least 10 |
| all coded rows (D1, D2, C, U, Indus) | 47 | |

**Gate: passes.** D1 has a margin of one row. No row may be added or dropped after sealing. If a saved account cannot be fetched at its revision on the day of the run, the study stops and is re-registered.

## Codebook (frozen)
**Reference time T.** The packet gives T per row: the timeline year for D1/D2, the account date otherwise. LANG_HIND is coded for D1/D2 only and is `NA` elsewhere. The four D2 scripts are not on the timeline, so the lead writes a year for each into the packet before any coder starts.

**General rules for a coder**
- Code from the fixed accounts only. Do not use what you know from elsewhere.
- Every code needs one quoted sentence from an account that supports it.
- If the accounts do not say, code `NS` (not stated). Do not guess.
- A 0 may cite a sentence stating the absence; failing that, code `NS`.
- If the two accounts conflict, code from the Wikipedia account and note the conflict.

### F1. LANG: was the language known at T?
- **LANG_PRIOR = 1.** At T the account reports scholars held a language identification on stated outside grounds (place, history, later tradition, a living descendant). Code alike whether or not later confirmed. The identification must name a language or a family. "Family" means a group below phylum level, close enough to supply words and grammar: Semitic or Iranian counts, Afroasiatic or Indo-European does not.
- **LANG_PRIOR = 0.** The account states that the language was unknown at T, or that several candidates stood with none leading.
- **LANG_HIND (D1 and D2 rows only; `NA` elsewhere) = 1.** The language turned out to be a known language or a close relative of one. Else 0.

### F2. ANCHOR: names or a parallel text from outside
- **2.** At T at least one object or text carried the script beside a version, or a name, in a readable script. A bilingual, a digraphic coin or seal, and a glossary all count.
- **1.** No such object. But at T the account reports scholars held expected names in stated texts (rulers, places, gods known from outside sources) on stated outside grounds. Code alike whether or not later confirmed.
- **0.** Neither.

### F3. VALUES: borrowed or inherited sign values
- **2.** Most of the sign list is shared with a script that was readable at T, and its values carry over. The script is a known script or a close variant of one.
- **1.** At T the account reports scholars held sign resemblances to a readable script, with values taken from it, on stated outside grounds. Code alike whether or not later confirmed.
- **0.** The account states that no such resemblance was held at T.

### F4. WORDDIV: is word division marked?
- **2.** Most texts mark words by a divider sign, a space, or a regular visual unit that the account says matches a word (a glyph block, or one sign per word).
- **1.** Division is marked in some texts only, or irregularly.
- **0.** Not marked.

### F5. CORPUS: size band at T, in sign tokens
- **A** under 1,000. **B** 1,000 to 9,999. **C** 10,000 to 99,999. **D** 100,000 or more.
- If the account gives only a count of inscriptions and a typical length, multiply them and say so. If it gives neither, code `NS`.
- Use the account's corpus figure whatever its date. A count of distinct signs is never a corpus size.

### Indus profile, stated now
The project's own coding of Indus is LANG_PRIOR 0, ANCHOR 0, VALUES 0, WORDDIV 0, CORPUS C (20,066 tokens in ICIT). The coders' agreed Indus row is the one used. Any difference from this line is reported.

## Coding protocol
- **Two coders**, each a fresh agent with no repo access and no memory of this project. They are not run under this draft.
- **Each coder receives only:** the codebook above, and for each row the script name and the saved text of its fixed accounts.
- **Each coder is not told:** the rule, the bar, the project's sentence, which set a row belongs to, that Indus is the target, or what the other coder wrote.
- **Row order** is shuffled per coder with seeds 20261125 and 20261126.
- **What the packet does reveal.** T and the `NA` on LANG_HIND show a coder which rows the lists count as read. The v2 codebook asks the same question of every row, so this no longer changes a definition.
- **Output per row:** the six codes (LANG_PRIOR, LANG_HIND, ANCHOR, VALUES, WORDDIV, CORPUS) and one quotation for each.
- **Mechanical check before scoring:** each quotation must be found in the saved account text. A code whose quotation is missing is set to `NS`.
- **Third coder.** After agreement is computed, a third fresh agent codes only the cells where the two differ, from the same packet, without seeing either code. The majority code stands. A three-way split is `NS`.
- **No codebook change after the first coder starts.** A changed codebook is a new version of this document with new coders. The old codes are kept and reported.

**A limit to state plainly.** Both coders are language models that have read these histories in training. Their agreement may come from shared memory and not from the codebook, so kappa here is an upper bound on reliability. The quotation rule narrows this. It does not remove it.

## Agreement bar and fallback (frozen)
Kappa is computed between the two coders over all 47 rows, before the third coder. `NS` is a category of its own. LANG_HIND kappa uses the 30 D1/D2 rows. In collapsed form `NS` is a third category. If both coders are constant, kappa is undefined and step 3 applies. Step 3 also needs at least one row both coders put in the smaller class. Readout 1 uses the majority table.

For each feature, in order:
1. **Full levels.** Cohen's kappa at least 0.8. For the ordered features (ANCHOR, VALUES, WORDDIV, CORPUS) kappa is linear-weighted, with `NS` scored as a full disagreement with any level. If met, the feature passes.
2. **Collapsed form.** If step 1 fails, the feature is collapsed to the form the rule uses: ANCHOR at least 1, VALUES at least 1, WORDDIV equal to 2, and CORPUS under 10,000 against 10,000 or more. Unweighted kappa at least 0.8 passes the feature in collapsed form only.
3. **Rare class.** If step 2 fails, and either coder put fewer than 5 rows in the smaller class, kappa is unstable. Raw agreement of at least 0.90 on the collapsed form passes the feature, flagged.
4. **Otherwise the feature fails.**

What a failure does:
- **CORPUS fails.** Readout 2 uses the four-feature profile only. Nothing else changes.
- **LANG_HIND fails.** Readout 1b is not reported as a verdict.
- **LANG_PRIOR, ANCHOR, VALUES or WORDDIV fails.** Readout 1 is then also computed from coder 1's table and from coder 2's table. A verdict stands only if all three agree. Otherwise the result is INCONCLUSIVE.

Any other change after codes are seen makes the run INVALID.

## Readout 1: the fixed rule
**Rule, from brief 11:** "read only with outside names or values, or with a known language plus word division".

**In codes:** a row FITS if ANCHOR is at least 1, or VALUES is at least 1, or (LANG_PRIOR = 1 and WORDDIV = 2).

**`NS` cells.** The fit is computed twice, once with every `NS` set to the value that helps the row fit and once with the value that hurts. A verdict needs both.

**Bar.** At least 90% of the 26 rows of D1, which is **24 or more**.

| Outcome | Frozen reading |
|---|---|
| **PASS.** 24 or more fit under both `NS` settings | The rule holds for the listed decipherments. The project may say: "every listed decipherment but k had outside names or values, or a known language with word division". The misses are named. See readout 1b for the project's own sentence. |
| **MISS.** 23 or fewer fit under both `NS` settings | The sentence "Every past decipherment rested on names fixed from outside the texts plus a known language" is withdrawn from `docs/RESEARCH_STATE.md`, the briefs' standing text and the site. It is replaced by the measured count and the list of misses. "Only a digraphic find changes the odds" is flagged as unsupported until each miss is read in a primary source. |
| **INCONCLUSIVE.** The two `NS` settings fall on opposite sides of 24, or the three tables disagree | The sentence is marked "not checked: the accounts do not settle it" wherever it stands. The rows that decide it are listed. |

### Readout 1b: the project's sentence as written
The rule is weaker than the sentence. The sentence needs both parts: ANCHOR at least 1 **and** LANG_HIND = 1.

| Outcome, given readout 1 passed | Frozen reading |
|---|---|
| 24 or more of D1 fit the sentence | The sentence stands as written. |
| 23 or fewer | The sentence is replaced by the rule's wording. |

The same two `NS` settings apply. If readout 1 is MISS or INCONCLUSIVE, 1b is a count only.

### Readout 1c: does the rule separate read from unread?
The share of the 14 U rows that fit the rule, with `NS` set against fitting.

| Share of U that fits | Frozen reading |
|---|---|
| 3 or fewer of 14 | The rule separates read from unread scripts in this list. |
| 4 to 7 | The rule separates weakly. |
| 8 or more | The rule does not separate. Having these features is common among unread scripts too, so the rule is at most a necessary condition. |

A Fisher exact p for D1 against U is recorded. It decides nothing, since the rows are not a random sample.

## Readout 2: Indus's profile
**Core profile:** the four rule features in collapsed form, as the coders agreed them for Indus. The project expects (0, 0, 0, 0).

Two counts, on the majority table:
- **k_U:** U rows with the same core profile as Indus.
- **k_D:** D1 rows with the same core profile as Indus.

A row with `NS` on a core feature counts as a "possible match" and is listed apart. It is in neither count. If Indus has `NS` on a core feature, the project's stated value is used and flagged.

| k_D | k_U | Frozen reading |
|---|---|---|
| 0 | 1 or more | Indus's profile is not seen among the 26 listed decipherments. k_U unread scripts share it, and they are named. With 0 of 26, the upper 95% limit on the share of listed decipherments that came from this profile is 10.9% (exact binomial, one-sided). |
| 0 | 0 | No listed script, read or unread, has Indus's profile. The outside view has no reference class for Indus and the project says so. |
| 1 or more | any | Indus's profile has been read k_D times. Those scripts are named. Each is then read in a primary source to learn how, as a new study. "Only a digraphic find changes the odds" is withdrawn until that is done. |

If the coders' Indus row differs from (0, 0, 0, 0), the same table is read with the coders' profile, and the difference is the first line of the result.

**With the corpus band.** If CORPUS passed its agreement bar, the same two counts are given for the five-feature profile. This is a record, with no reading attached.

**What readout 2 cannot say.** It gives no probability that Indus will be read. The lists are not a sample: deciphered scripts are recorded because they were read, and the undeciphered list leaves out scripts nobody wrote a page about.

## Sensitivity (all record-only)
- Readout 1 on D1 plus D2 (30 rows, bar 27).
- Readout 1 with each contested row counted as deciphered, then as undeciphered.
- Readout 1 with the stricter clause VALUES = 2.
- Readout 1 with LANG_HIND in place of LANG_PRIOR.
- Readout 1 by family, since related scripts are not independent. The families are fixed now: Egyptian (rows 4, 6), cuneiform (7, 12, 18), Aramaic-derived and its neighbours (1, 2, 3, 10), Indic (8, 9). That gives 19 groups. A group fits if every row in it fits.
- Leave-one-out: the count if any single row changes its fit.

## What a pass would not show
- It would not show that the rule is a cause. The features were chosen by people who already knew the stories.
- It would not show that the accounts are right. Wikipedia and Mnamon are summaries, not primary sources.
- It would not show reliability across independent coders, for the reason given under "A limit to state plainly".
- It bears on no Indus reading and on no language.

## Outputs
- `experiments/decipher_reference_class/accounts/`: the saved account text for each row, with SHA-256 values.
- `experiments/decipher_reference_class/codes_coder1.csv`, `codes_coder2.csv`, `codes_coder3.csv`, `table_majority.csv`.
- `experiments/decipher_reference_class/RESULTS.md`: the agreement table, the three readouts, the sensitivity table, every miss by name.
- The result goes into `docs/RESEARCH_STATE.md`, and into the atlas if readout 1 misses or k_D is above 0.

## Cost
No CPU beyond fetching about 75 pages and counting a 47-row table. Three agent runs. Half a day.

## Open decisions before sealing
1. **Which form of the sentence is on trial.** The bar is on brief 11's rule, which is weaker than the sentence in `docs/RESEARCH_STATE.md`. Readout 1b tests the sentence itself. The lead may prefer the sentence as the primary bar.
2. **Hindsight in "known language".** The sentence most naturally means LANG_HIND (Linear B turned out to be Greek). Only LANG_PRIOR can be coded for Indus. The draft puts LANG_PRIOR in the rule and LANG_HIND in the sentence.
3. **Wikipedia as the fixed account.** It is open and versioned, but thin for some rows (Ba–Shu 5 kB, Shankhalipi 7 kB, Lycian 7 kB, Northeastern Iberian 7 kB). Thin accounts give `NS`, and `NS` on a few rows makes readout 1 INCONCLUSIVE with only one row of margin. The alternative is a second open source for each thin row, found and fixed before sealing.
4. **A codebook pilot.** Run the two-coder protocol on four scripts outside the list (for example Jurchen, Elamite cuneiform, Sogdian, Etruscan) before sealing, and fix wording then. After sealing no change is allowed.
5. **Coder independence.** Use two different models, or add a human spot check of 10 rows, to answer the shared-memory limit.
6. **A sixth feature for text length.** Indus is in corpus band C by tokens, but its median text is 3 signs. Farmer, Sproat and Witzel treat brevity as the main point. A band for typical text length would catch it. Brief 11 asked for five features, so it is left out here.
7. **D2 and the Phaistos Disc** are the drafter's additions. The lead may drop them.

## Decisions, ruled 2026-11-25 (project lead, before review)
1. The primary bar is brief 11's rule, as drafted. Readout 1b, on the `RESEARCH_STATE.md` sentence, has its own frozen readings.
2. LANG_PRIOR goes in the rule and LANG_HIND in the sentence, as drafted.
3. No second source. Wikipedia at fixed revisions, plus Mnamon where present. An INCONCLUSIVE reading is accepted as a possible outcome.
4. No pilot.
5. The coders are two different models (one Fable and one Opus agent), each fresh and blind to the other.
6. No sixth feature. Text brevity is noted as a limit.
7. D2 and the Phaistos Disc stay.

## Review fixes applied in v2
Must-fix:
1. **Hindsight.** ANCHOR 1, VALUES 1 and LANG_PRIOR 1 now use one test for all rows: what scholars held at T on stated outside grounds, coded alike whether or not later confirmed. The 0 levels of LANG_PRIOR and VALUES lost their "proved wrong" and "proved misleading" clauses to match.
2. **T and status.** The packet gives T. LANG_HIND is `NA` outside D1/D2. D2 has no timeline year, so the lead supplies one. The protocol now says that T reveals which rows are read.
3. **Absence codes.** A 0 needs a sentence stating the absence, else `NS`. An `NS` on Indus falls back to the project's stated value, flagged.
4. **Kappa.** LANG_HIND on 30 rows, `NS` as a third collapsed category, the constant-coder case, the shared-row condition for step 3, and the majority table for readout 1.
5. **Readout 1b.** Same `NS` settings; a count only after MISS or INCONCLUSIVE.
6. **Demotic.** Row 4 is `Demotic_Egyptian_script` at 1387003548.
7. **Page choice.** The account is the linked page. Applying it also changed rows 6, 12, 14 and 24.
8. **CORPUS.** The account's figure whatever its date; never a count of distinct signs.

Smaller:
- Olmec dropped. U is 14 rows and the table 47. Readout 1c keeps its cut points, now out of 14.
- Espanca left out, with the reason stated.
- "Family" bounded below phylum level.
- The upper limit for 0 of 26 is 10.9%.
