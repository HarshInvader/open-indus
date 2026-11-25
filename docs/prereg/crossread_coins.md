# Cross-read on coins: does the sealed cross-read test hold across two scripts and two languages? (sealed v2; no code existed and no test statistic had been computed on any real pair at sealing)

Status: **v2, sealed 2026-11-25** (tag `crossread_coins`). Drafted from `docs/fable_brief11.md`, study 3. First study of plan 11 by the coordinator's order. The checked legend table is not built. A fresh review of v1 returned 6 must-fix items and 4 smaller ones; all are applied (log at the end).

## Question
- Indo-Greek coins carry a king's name in Greek on one side and in Kharosthi on the other. Greek gives the sounds. The Kharosthi aksharas are treated as opaque symbols.
- Does the test sealed in `docs/prereg/anchor_crossread.md` tell sets of 15 true pairs from sets of 15 re-paired ones on these coins?
- This is a rehearsal on a script that was in fact read this way. **No Indus key is scored, no Indus text is read, no Indus file is opened, and no outcome supports or counts against any Indus reading.**

## Why
- `anchor_crossread` found a working rule: 15 pairs, direction known from outside, clean legends. Both sides of every pair were cuneiform, so one name unit was one legend sign. The result file calls its power an upper bound for that reason.
- A real anchor find would pair a name in one script and language with a legend in another. Units would not line up one to one. Vowels and endings would change.
- The coins are the one open case where that happened and the answer is known. The legends are formulaic (title, epithet, name), like seal legends.
- The outcome decides whether the "more than 15 pairs" in section 4 of `docs/prereg/anchor_objects.md` is a real number or only an upper bound on power.

## What was seen before this draft
- **Repo results:** `anchor_crossread` (sealed, done), brief 11.
- **The legend pairs themselves.** The drafter read the Greek and Kharosthi legends in the source export while checking that the source was usable. The standard readings of these names are also common knowledge. So the name-unit rule below was written with the pairs in view. It is not a blind rule. It is frozen here, before any statistic.
- **Label-free counts**, made with single-process scratch scripts outside the repo, each under 10 seconds, at lowest priority, `python -I`. They count rows, legends, akshara types, name units and repeated sounds. The Greek side and the Indic side were counted separately. The tables are under "Count gate".
- **Timing on synthetic random-symbol sets only**, with the sealed statistic loaded from the sealed `run.py`. No real pair.
- **Not seen:** the statistic T, any p-value, any pass count, or any alignment found by the search, on any real coin pair or any re-pairing of one.

## Prior art
Opened 2026-11-25 with curl and the User-Agent `open-research-site/1.0`. Nothing paywalled was bypassed.

### How the script was read
- **Masson found the first matches.** Prinsep writes that Masson "first pointed out" the signs that stood for the names of Menander, Apollodotus and Hermaeus and for the words for king and saviour. That is three names and two titles. Prinsep, *Essays on Indian Antiquities* (ed. Thomas, 1858), vol. 1, art. IX, pp. 178 to 184, a reprint of his 1835 paper. https://archive.org/details/essaysonindiana06pringoog
- **Prinsep 1835: twelve names, six titles, and a wrong language.** He "extended the series of words thus authenticated, to the names of twelve kings, and to six titles or epithets". He then assigned letters one by one from the names. He took the language for a kind of Pehlvi, read the final akshara of every word as *o*, and read the word for king as a form of *malaka*. He printed his twelve name readings and added that "many of these are highly unsatisfactory, especially the last three". Same source.
- **Prinsep 1838: about sixteen names, and the right language.** He saw that the final akshara could be *sa*, the Prakrit genitive, and "at once found an easy solution of all the names and the epithets". His revised list has 16 Greek names with a Kharosthi transcript (the drafter's count from an OCR text). He lists three more coin types apart, where "the names are either quite different on either side", such as Vonones in Greek with Spalahores in Kharosthi. He still could not read the Gondophares group. *Essays*, vol. 2, art. XXI, from p. 125. https://archive.org/details/in.ernet.dli.2015.281393
- **His stated rule is the statistic tested here.** "The only incontestible authority for the determination of a vowel or consonant is its constant employment as the equivalent of the same Greek letter in the proper names of the Bactrian kings." Same source, p. 127.
- **Three people worked in parallel.** Prinsep (1835), Grotefend (1836) and Lassen (1838) "all used the bilingual coins of the Indo-Greek Kingdom". https://en.wikipedia.org/wiki/Kharosthi
- **Brahmi.** Lassen fixed several letters in 1836 from the Greek and Brahmi coin of Agathocles. Prinsep then used a coin of Pantaleon and finished the script. https://en.wikipedia.org/wiki/Brahmi_script . Only two names carry Brahmi, so Brahmi cannot fill a set of 15 and stays out of this study.

### Modern computational work
- **Transliteration as decipherment.** Ravi and Knight 2009 learn phoneme mapping tables for name transliteration from monolingual data alone. Both languages are known and the data are large. https://aclanthology.org/N09-1005/ (first page read)
- **Transliteration mining.** Sajjad, Fraser and Schmid 2012 pick transliteration pairs out of parallel text with a mixture of a transliteration model and a model that assumes no link between the two words. Their second model is the same idea as the re-pairing null. They train on whole corpora. https://aclanthology.org/P12-1049/ (first page read)
- **Names across scripts in comparable text.** Sproat, Tao and Zhai 2006, Chinese and English. https://aclanthology.org/P06-1010/ (first page read)
- **Reviews.** Braović et al. 2024 review computational work on the Aegean scripts and list 15 challenges. https://aclanthology.org/2024.cl-2.7/ (abstract read)
- **Coin legends by machine** are an image problem so far. Kavelar, Zambanini and Kampel test on 180 cropped legend words. https://arxiv.org/abs/1304.7184 (abstract read)
- **Two web searches found no computational study of Kharosthi or Brahmi coin legends** and no computer replay of this decipherment. The searches were short, so "not found" is weak evidence.
- From the repo, not reopened: the prior art list in `docs/prereg/anchor_crossread.md` (Snyder 2010, Luo 2019 and 2021, Kessler 2007, Tamburini 2025).

### Not opened (unverified)
Salomon 1998, *Indian Epigraphy*, pp. 209 to 215. Grotefend 1836. Lassen 1838. Masson's memoirs in the Journal of the Asiatic Society of Bengal. Bopearachchi 1991. Mitchiner 1975. Knight and Graehl 1998, https://aclanthology.org/J98-4003/ (landing page only). The single coin entries of the Gandhari.org catalogue.

**What is established.** Kharosthi was read from name pairs, by matching each Greek letter to the sign that stands in its place in several names. With 12 names and the wrong language the first reading was poor. With about 16 names and the right language it worked. **What nobody in the opened sources gives** is a false-pass rate or a pass rate for such a set under a stated test, with the signs taken as opaque. That is this study.

## Data sources and licences
| source | what it holds | licence | role |
|---|---|---|---|
| Coins of the Bactrian and Indo-Greek Rulers (BIGR), type export, https://numismatics.org/bigr/ | 2,109 type rows with the Greek legend and the Kharosthi legend in Unicode | Open Database License 1.0 for coin type data, as the site states | transcriber A, Indo-Greek names |
| Wikipedia ruler pages, raw wikitext | name forms in Greek and in Kharosthi Unicode; full legends in some captions, mostly as Latin transliteration | CC BY-SA 4.0 | transcriber A, names BIGR lacks |
| Gardner 1886, *The Coins of the Greek and Scythic Kings of Bactria and India in the British Museum*, https://archive.org/details/coinsofgreekscyt00gard | Greek legends, Kharosthi legends in Latin transliteration, plates. The OCR text of the Greek is unusable, so B works from the page scans | public domain (author died 1937); the archive record states no rights field | transcriber B |
| Prinsep's *Essays*, 1858 | history only | public domain | prior art |

Looked at and not used:
- **Gandhari.org** lists 337 coin legends in transliteration. The pages opened state no licence, so nothing was taken from it.
- **Whitehead 1914**, the Lahore catalogue. Public domain in the United States. The author died in the 1960s, so it is still in copyright where the term is life plus 70 years. Not used.
- **Coinindia, Bopearachchi 1991, Mitchiner.** Not open.
- **Nomisma and OCRE** cover Roman coinage. BIGR is the instance of the same software for these kings.

The BIGR export was fetched once: `query.csv`, 2,047,926 bytes, SHA-256 `847add2aebcc64ac2907cca31d58c0e13968f00db003c92e13e036e9e26ad8bc`. The study will keep its own copy in a new empty `experiments/crossread_coins/raw/bigr/`, with the attribution the licence asks for. **Rows from BIGR (ODbL) and rows from Wikipedia (CC BY-SA) are kept in separate files**, each with its own licence note, and are joined only in memory. Every other download sits in its own new empty directory under the scratch area, outside the repo.

## Count gate (label-free; the checked table is not built)
### BIGR export
| quantity | count |
|---|---|
| type rows | 2,109 |
| rows with a Greek legend on one side and a Kharosthi legend on the other | 1,464 |
| rows with a Greek legend and a Brahmi legend | 3 (Agathocles 2, Pantaleon 1) |
| authority strings with at least one such row | 37 of 49 |
| distinct Kharosthi legends | 45 |
| Greek words that are not a title or epithet | 29 spellings, **28 distinct names** (Zoilus has two spellings) |

The 28 are 26 kings and two queens (Agathocleia, Calliope).

### Wikipedia pages
Of 60 fetched ruler pages, 27 belong to rulers outside BIGR. 18 of those hold a Greek-script form and an Indic Unicode form. After removing a repeat (Azes), pages whose Greek legend names another ruler, and one with no name in the Greek, **11 to 14 further names** are candidates: Abdagases, Arta, Azes, Azilises, Gondophares, Kharahostes, Kujula Kadphises, Maues, Pacores, Spalahores, Vima Kadphises, Zeionises, and perhaps Rajuvula and Nahapana. For most of them only the name is in Unicode. The full legend must come from a caption or from Gardner.

### Shape of the legends (BIGR, Indic side only)
- Aksharas per legend: median 15, range 10 to 24. Words: median 3. The Ur III legends had a median of 9 signs.
- 66 akshara types in 45 legends.
- Five aksharas stand in 98% or more of the legends. They are the title and the case ending. The penalty term of the statistic was built for signs like these.

### Shape of the names (BIGR, Greek side only, under the unit rule below)
| | exact units | consonant-only units |
|---|---|---|
| units per name, median | 4 | 4 |
| sound types over 29 spellings | 59 | 23 |
| sound types in 2 or more names | 24 | 18 |
| sounds in 2 or more names of a random 15, median | 10 | 11 |
| chance that a random 15 has 8 or more such sounds | 0.90 | 1.00 |

The sealed Ur III count gave a median of 8 repeated sounds at 15 names. So the Greek side has enough repeats. Whether the same sound lands on the same akshara is what K0 measures.

### Gate
**Brief 11's gate: at least 30 distinct names, each with both legends in a table that two blind transcribers agree on.**
- Today: 28 names with full legends in one open source, and 39 to 42 candidates in all.
- BIGR alone is two short on this count, and the protocol will cut it further. **The reviewer puts BIGR's yield near 21** (the reviewer's count, not rechecked by the drafter):
  - The two queens stand only in legends with two names or with another person on the Indic side. They give no pair (lists RM and RM2).
  - Gardner lacks Thraso, Peucolaus and Polyxenus, so B cannot confirm them.
  - BIGR spells two names ΔΗΜΗΤΡΙΟΡΟΥ and ΑΡΤΕΜΙΔΟΡΟΥ. **Misspellings are copied as given by both transcribers. Nothing is corrected.** If B's Greek differs from A's, the Greek-name bar drops the pair.
- So about 9 of the 11 to 14 Indo-Scythian, Indo-Parthian or Kushan candidates must pass the table protocol.
- **Open, not passed.** The table decides. Brief 11's 85% for the gate looks too high.

## The table: two blind transcribers
### Who
- **Transcriber A** works from BIGR and, for names BIGR lacks, from Wikipedia. For BIGR rows A is a script: it takes the legend pair that stands on the most types for each name.
- **Transcriber B** works from the page scans of Gardner 1886. The OCR text is not used: its Greek is unusable. B may be a person or a fresh agent.
- **Blind means this.** B gets only a protocol sheet hashed at sealing and copies the source uncorrected. A never uses Gardner. The sheet is the section "Protocol sheet for transcriber B" below, so it is hashed with this file. B does not see the rest of this file, A's table, BIGR, the Wikipedia pages or any output. The comparer is a script.
- **Nobody is blind to the sounds.** Every source was made by people who read Kharosthi. Blindness to sound is enforced at the code boundary, under "Symbols and sounds".

### What each records, per name
- The Greek legend, word by word, and which word is the name.
- The Indic legend, akshara by akshara, in reading order, and which word is the name.
- Whether both sides name the same person.

### Agreement bars
- **Same person.** A pair enters POS only if both transcribers say the two sides name the same person. Types where the sides name different people (joint issues, mules, Prinsep's "names quite different on either side") go to a list RM of real mismatches. They are counted and kept out of every set.
- **Greek name.** The letters must agree after folding the forms of sigma and omega. If not, the pair is dropped. Spellings are copied as given and never corrected.
- **Agreement is on keys.** A is Unicode and B is 1886 Latin, so the two are compared through a key.
  - **Unicode key:** from character names. KA + VOWEL SIGN I gives `ki`. No vowel sign gives `a`. ANUSVARA gives `m`.
  - **Latin key:** lower case, NFD, marks dropped.
  - Both drop retroflex.
  - The comparer is a script hashed before B's table exists.
  - Run symbols are A's aksharas. The keys are used for the comparison only and never reach the run.
- **Akshara rule, carried over from section 1 of `anchor_objects.md`.** An akshara counts as read only if A and B give the same key. The two sequences are aligned by edit distance, and an unmatched akshara is unread. A legend passes with 80% or more of its aksharas read.
- **An unread akshara stays in the legend as a symbol used nowhere else.** That is the treatment the sealed cell R1 gave an unread sign.
- **Gate:** 30 or more names pass. The share of aksharas agreed over the whole table is reported. Under 90% it is flagged to the coordinator.
- **One pair per distinct name.** Rulers who share a name (Strato I and II, Menander I and II) give one pair, from the legend on the most types.
- The table and the lists RM and RM2 are hashed into `docs/prereg/HASHES.txt`. No T is computed while the table is built.

## Protocol sheet for transcriber B
This section is the whole of what B receives. It is hashed with this file at sealing.

> **Task.** Copy coin legends from one printed catalogue into a table.
>
> **Source.** Percy Gardner, *The Coins of the Greek and Scythic Kings of Bactria and India in the British Museum*, 1886, page scans at https://archive.org/details/coinsofgreekscyt00gard . Use the page images. Do not use the OCR text. Use no other book, website, database or memory of these coins.
>
> **Which entries.** Go through the catalogue ruler by ruler. Take every coin entry that prints a legend in Greek letters and a second legend that the catalogue gives in Latin letters in brackets.
>
> **One row per distinct pair of legends under each ruler heading.** Record:
> 1. the ruler heading as printed, and the page number;
> 2. the Greek legend, letter by letter, as printed, with a space where the catalogue has a word break or line break;
> 3. the second legend in Latin letters, as printed, with every dot, accent and hyphen;
> 4. the number of coin entries under that heading that carry this pair;
> 5. whether the catalogue's own heading or note says the two sides name different people: yes, no, or not stated.
>
> **Copy, do not correct.** Do not fix a spelling, fill a gap, expand an abbreviation or bring two entries into line. If a letter cannot be read on the scan, write `?` in its place. If the catalogue marks letters as missing or restored, copy its marks.
>
> **Do not** translate, say which word is a name, or compare your rows with any other table.
>
> **Return** one CSV file with those five columns and nothing else.

Which word is the name is not B's call. It follows from the title list on the Greek side and from the truth marks on the Indic side.

## Symbols and sounds (frozen)
### The central risk, stated plainly
The method must see the Indic side as opaque symbols. Three leaks are possible. Each gets a rule.

1. **The label names the sound.** A Unicode Kharosthi letter and a Latin transliteration both are the reading. **Rule:** each distinct akshara becomes an integer through a seeded random relabelling. The run receives integers only. The map is written to a file the run never opens, and an audit hook on file opens enforces that, as A5 did in the sealed run. The sealed search already treats symbols as opaque: it renumbers them on entry and never looks inside one.
2. **The cutting into units carries knowledge.** **Word spaces leak:** the BIGR Kharosthi legends hold 3,298 spaces and 188 no-break spaces (the reviewer's count), and a space says where the name word starts. **Delete all Z\* and P\* characters before cutting. NS and TS take the name span from truth marks.** **Rule for Unicode:** an akshara is one base character, plus any combining marks (general category Mn or Mc), plus any character joined to it by the virama U+10A3F. No table of sound values is used. A conjunct such as the one written for *stra* is one symbol. **Rule for a Latin-only source:** an akshara is a run of consonants, one vowel, and an optional anusvara. Consonants are cut with a fixed digraph list (kh, gh, ch, jh, th, dh, ph, bh, and the same with a dot or accent on the first letter, plus sh). A consonant run before a vowel is one conjunct. The Latin string is then relabelled like any other akshara and never reaches the run. Unicode wins where both exist.
3. **The name side is fitted to the Indic side.** **Rule:** the name units come from the Greek spelling alone, by the rule below. The script that builds them never opens the Indic column. The two sides are joined by row number only. The units file is hashed before any T.

**What no rule removes.** Each symbol is a reading that an editor has resolved. One akshara type is one sound, variant shapes are merged, worn signs are restored, and the cutting is certain. A script nobody can read gives shapes. So the Indic side here is the state of the sealed cell R3 (editor-resolved readings), which was the easier state on Ur III. **Power in this study is an upper bound for that reason. The false-pass rate is not affected**, because every re-pairing uses the same symbols. Cells U and S dial part of the way back.

### Legend symbol
The whole akshara, base and vowel mark together, is one symbol. A transcriber who cannot read a script records whole shapes. Splitting off the vowel mark assumes the abugida analysis, which is part of the decipherment. A record-only cell (BASE) drops the vowel marks.

### Name sound: the unit rule (Greek only)
1. Upper case. Fold lunate sigma and small omega. Drop anything in brackets. Brackets are ( ) and [ ].
2. The name is the word that is not in the title list: ΒΑΣΙΛΕΩΣ, ΒΑΣΙΛΕΩΝ, ΒΑΣΙΛΙΣΣΗΣ, ΜΕΓΑΛΟΥ, ΣΩΤΗΡΟΣ, ΔΙΚΑΙΟΥ, ΝΙΚΗΦΟΡΟΥ, ΑΝΙΚΗΤΟΥ, ΕΠΙΦΑΝΟΥΣ, ΝΙΚΑΤΟΡΟΣ, ΕΥΕΡΓΕΤΟΥ, ΦΙΛΟΠΑΤΟΡΟΣ, ΘΕΟΤΡΟΠΟΥ, ΚΑΙ, ΦΙΛ. **Later title words:** any word in the legends of 2+ names, from the Greek column alone, hashed before code. A legend with zero or 2+ non-title words gives no pair (list RM2).
3. Strip one case ending, the first that fits of ΟΥΣ, ΟΥ, ΟΣ, ΑΣ, ΗΣ, ΩΣ, if two letters or more remain.
4. Cut into syllables. A nucleus is one vowel letter, or one of the diphthongs ΑΙ, ΕΙ, ΟΙ, ΥΙ, ΑΥ, ΕΥ, ΗΥ, ΟΥ. The onset of a nucleus is the longest consonant run before it that is a legal onset: one consonant, or one of ΒΛ ΒΡ ΓΛ ΓΡ ΓΝ ΔΡ ΘΛ ΘΡ ΘΝ ΚΛ ΚΡ ΚΝ ΚΤ ΠΛ ΠΡ ΠΝ ΠΤ ΤΡ ΤΛ ΤΜ ΦΛ ΦΡ ΦΘ ΧΛ ΧΡ ΧΘ ΧΝ ΣΚ ΣΠ ΣΤ ΣΦ ΣΧ ΣΘ ΣΜ ΜΝ, or one of ΣΤΡ ΣΠΡ ΣΚΡ ΣΠΛ ΣΚΛ ΣΦΡ ΣΧΡ ΣΤΛ. A run at the start of the word is all onset. Consonants left before an onset are a coda and are dropped.
5. A consonant run left at the end of the stem is a unit of its own, with its onset by the same rule and no vowel.
6. **Exact unit:** the onset letters and the nucleus letters. So ΜΕΝΑΝΔΡΟΥ gives ΜΕ, ΝΑ, ΔΡ.
7. **Consonant-only unit (the fallback):** the onset letters alone. Every unit with no onset is the one sound V.

Dropped codas and the vowel-less final unit are not the school rule; they match akshara spelling. The rule was not tuned on any statistic. It was written with the pairs in view, as said above.

### Truth, used for scoring only
After the table is frozen and before any run, the two transcribers mark for each name unit the akshara it stands for, or none. The marks are hashed. They are used only in the record-only value readout and to build cells TS, NS and arm A.

## The test (frozen; the sealed method)
The run loads `experiments/anchor_crossread/run.py` after checking its hash against `docs/prereg/HASHES.txt` (tag `anchor_crossread_code`). It uses that file's placement family, statistic, search and leave-one-out readout as they stand. Nothing in them is rewritten.

- **Placement family.** The units of a name go on legend positions in order, contiguous or with one legend symbol skipped. No name unit is skipped.
- **Arm B1 is primary:** any start, forward only. It is the arm that claimed in the sealed study, with the condition that direction is known from outside. The legend is given in its own reading order.
- **Statistic T, penalty weight 0.25, six restarts, 20 sweeps:** unchanged.
- **Null:** re-pair the 15 legends among the 15 names, 999 times. A set passes if (1 + b) / 1000 ≤ 0.01. An observed T of 0 never passes. Early stop at b = 10.

### Sets
- N is the number of names in the checked table, N ≥ 30.
- Set s, for s from 0 to 19: shuffle the N names with the seed purpose `set/<s>`. The first 15 are the set's names.
- **True set:** those 15 names with their own legends.
- **Re-paired set:** those 15 names with the legends of the next 15 names in the same shuffle. No true pair can occur in the observed pairing or in any re-pairing of it. This is the design of the sealed check Kc.
- **The 20 sets overlap.** Two sets share 7.5 names on average at N = 30 and 5.6 at N = 40. They are 20 draws from one historical set of names, not 20 archives. The count out of 20 estimates the pass rate over subsets of this one set.
- The disjoint sets from one shuffle (2 at N below 45, else 3) are reported on their own beside the 20.

### Bars
- **Power bar:** true sets pass in at least 16 of 20. 13 to 15 is "at the edge" and counts as a fail. No rerun.
- **Mismatch bar:** re-paired sets pass in at most 1 of 20.
- **The mismatch half is exchangeable by construction.** It checks the null and the code. It is not evidence about real mismatched coins. A calibrated test breaks the bar at most 10% of the time (expected passes 0.2, two needed), with or without independence.
- **The real false-pass control here is cell NS**, where the name is taken out of the legend.

## Checks, in this order (strongest kill first)
1. **A1, recount.** The code rebuilds the count tables above from the hashed export and the checked table. No T.
2. **Kp0, the method is unchanged.** The sealed planted check Kp is run again with the sealed seeds. It must reproduce the per-set T and b in `experiments/anchor_crossread/kill.json` exactly (20 of 20 passed there).
3. **Kq, planted known answer at coin shape, arm B1, 20 sets of 15.** The names are the real Greek names with their units. The legends are synthetic. Each sound type in the set gets one random symbol. A legend is 5 symbols common to every legend, then 4 symbols for one of 6 epithets, then the coded name, then one ending symbol common to every legend. **At least 19 of 20 must pass.** Fewer means these names do not repeat enough sounds for the test even with a perfect one-to-one spelling, and nothing after it could be read as a statement about transport.
4. **K0, the kill test, at 15 pairs, arm B1, exact units.** Both halves must hold.
   - **K0a:** 20 re-paired sets. At most 1 passes.
   - **K0b:** 20 true sets. At least 16 pass.
5. **Only if K0b fails: F1 below, once.**
6. **NS, U and D**, then the reported and record-only cells.

K0 comes before every cell because it is the sealed rule on clean legends with nothing made harder. If true coin pairs cannot be told from re-paired ones there, no cell is read.

## Calibration fallbacks (written before any calibration)
Only these are allowed. **Any other change after a number from a real pair has been seen makes the study INVALID.** That includes a change to the unit rule, the title list, the akshara rule, the table, 0.25, the placement family, 0.01, the restart count, the arm or the bars. No calibration on real pairs is planned.

- **F1, consonant-only, applied once.** If K0b fails with exact units, the name units are replaced by the consonant-only units of step 7. The legend symbols do not change. Kq, K0a and K0b are run again on the same sets. Greek vowels and endings change on the way into Prakrit, and consonants mostly do not. If K0 passes under F1, every cell runs with consonant-only units and reading 4 governs.
- **F1 is the only step between a failed K0 and reading 5**, "the rule does not transport across scripts as built". There is no move to another arm, another symbol unit or another weight.
- **F2, cost.** Before any real pair, time T on 50 synthetic sets of the Kq generator. If the projection for all cells exceeds 6 CPU-hours, every cell uses 199 re-pairings and a set passes at b ≤ 1. As sealed.
- **F3, unbuilt sets.** A set that cannot be drawn counts as a non-pass among true sets and as a pass among re-paired sets. As sealed.
- **F4, the gate.** If fewer than 30 names pass the table protocol, the study does not run. No smaller K0 replaces it.
- **F5, Kq.** If Kq fails with exact units, K0 with exact units is not run and F1 is applied at once. If Kq fails with consonant-only units too, reading 2 ends the study. If K0 then passes under F1, reading 4b governs. If Kq passed with exact units, K0b failed, and Kq then fails with consonant-only units, reading 5 governs.

## Cells (arm B1, 15 pairs, 20 sets)
| cell | what changes | halves | role |
|---|---|---|---|
| P | nothing; clean legends | true and re-paired | K0 |
| NS | the name span, taken from the truth marks, is cut out of each Indic legend; titles and epithets stay | true only | **control: at most 1 of 20 may pass** |
| U | each akshara unread with probability 0.20 and replaced by a symbol used nowhere else | true and re-paired | binding on the wording |
| D | each legend reversed with probability 0.05, one draw per legend: a guessed direction that is wrong 1 time in 20. With 15 legends, 46% of sets have no legend reversed (0.95^15), so about 9 of the 20 sets are cell P again | true and re-paired | binding on the wording |
| TS | everything outside the name span, taken from the truth marks, is cut out, so the legend is the name alone | true and re-paired | reported; an upper bound |
| UD | U and D together | true and re-paired | record only |
| S | each akshara token moved to a second symbol for its type with probability 0.25, standing for variant shapes a reader would not merge | true only | record only |
| BASE | vowel marks dropped from the symbols | true only | record only |
| arms B2 and A | P in the other two sealed arms; arm A takes the span from the truth marks | true and re-paired | record only |
| rungs 10, 12, 20 | P at other sizes; 20 is true sets only | | record only |
| Kd | the Kq plant with each name unit dropped from the legend with probability p and one extra symbol put inside the name with probability p, for p = 0.1, 0.2, 0.3 | planted | record only; a dial for unit mismatch |

The same bars apply to both halves of U and D.

## Readings (frozen)
The first of readings 1 to 5 whose condition holds governs (4b is the form reading 4 takes after F5). Readings 6 to 9 are added where they apply.

1. **Kp0 fails:** fix before any real pair. Kp0 uses no real pair, so the fix and a new code hash come before any T on one. **K0a fails:** "null not calibrated on coins"; study ends, no rerun.
2. **Kq fails with exact and with consonant-only units.** "These names repeat too few sounds for a 15-pair test even when the spelling is planted one to one. The study says nothing about transport." Section 4 stays as it is.
3. **K0 passes with exact units.** "The sealed cross-read rule transports across two scripts and two languages as built: 15 pairs, direction known. The 'more than 15 pairs' of the minimum event is not only an upper bound made by using one script." Then, by cell:
   - **3a. U and D both meet both bars.** "It holds with 20% of the aksharas unread and with a guessed direction that is wrong 1 time in 20."
   - **3b. U misses.** "It holds on clean legends only. With 20% unread it fails, as it did on Ur III. The minimum event stays at more than 15 pairs."
   - **3c. D misses.** "A direction guess that is wrong 1 time in 20 breaks it. The direction must be certain."
   - If U or D misses on the mismatch bar and not on power, the note says so in those words.
4. **K0 fails with exact units and passes under F1.** "The rule transports only when sounds are matched on consonants. Section 4 must say that a foreign name is matched on its consonants." Readings 3a to 3c then apply to the cells under consonant-only units.
   - **4b. Kq failed exact, K0 passes under F1:** "shown on consonants; exact untested."
5. **K0 fails with exact units and under F1.** **"The rule does not transport across scripts as built."** Section 4 of `anchor_objects.md` must say so, and the 15-pair figure is then an upper bound that holds only when name and legend share a script. The note reports arm A, cell TS and the Kd dial beside it, so a reader can see whether the loss is in finding the name or in the units. None of them changes the reading.
   - **Kq fails consonant-only after K0b failed:** reading 5.
6. **NS control.** If more than 1 of 20 true sets pass with the name cut out, a pass does not show that the name is spelled in the legend. Any passing reading is then worded "the names are tied to these legends".
7. **Edge.** 13 to 15 of 20 is reported as "at the edge" and read as a fail. It triggers F1 like any other fail.
8. **Values, record only.** The median number of confirmed values and of confirmed and right values per set, for P and U. No bar. The sealed study found that a passing set certifies the pairing and not the values. Nothing here can overturn that.
9. **Record-only cells and rungs** are reported with their pass counts and decide nothing.

In every reading, power is an upper bound, because the Indic symbols are editor-resolved readings and the unit rule was written with the pairs in view. In every reading the 20 sets are draws from one set of names.

## Changes from `anchor_crossread`, each with its reason
| # | sealed study | here | reason |
|---|---|---|---|
| 1 | Ur III sealed tablets, two cities | one table of coin name pairs | the question |
| 2 | name sounds are the readings of the name's own cuneiform signs | name sounds come from the Greek spelling by the unit rule | the two sides are in different scripts; this is the thing tested |
| 3 | legend symbols are sign names from a public sign list | legend symbols are whole aksharas, relabelled as integers | no sign list plays that part; the relabelling blocks the sound label |
| 4 | pools POS, NEG and VAR from a matcher, with a cleaning rule | POS from the two-transcriber table; RM listed and kept out | there is no line that says whose seal it is; the table does that work |
| 5 | K0 in arm B2, then F1 to B1, then to A | K0 in arm B1 only; B2 and A record only | the sealed result fixed the claiming arm; the rule being transported is B1's |
| 6 | K0a on real mismatched tablets, restricted re-pairings, Kk, F4 | K0a on re-paired sets built like the sealed Kc | too few real mismatched types for sets of 15 |
| 7 | none | cell NS as the false-pass control | K0a is exchangeable by construction, so a real control is needed |
| 8 | sets disjoint within a city | 20 overlapping sets from N names | 30 to 42 names give 2 disjoint sets of 15 |
| 9 | ladder 3 to 15 and a claimed m | 15 only for K0; 10, 12 and 20 record only | the brief asks whether the rule at 15 transports |
| 10 | cells R1, R2, R3, C1, C2, X | U (the R1 mechanism, unchanged), D, TS, NS and record-only cells | brief 11's cells; the Indus-statistics arm is done and is not about transport |
| 11 | fallback F1 moves between arms | fallback F1 moves to consonant-only units, once | brief 11's fallback; vowels and endings are what change between the languages |
| 12 | value bar of 90% | value readout is record only | the sealed result already says a set certifies the pairing, not the values |
| 13 | Kp, Kc | Kp0 (Kp rerun, must match the sealed file), Kq and Kd planted at coin shape | to show the method is unchanged, and that the names can carry the test |
| 14 | seeds under `anchor_crossread/v3` | seeds under `crossread_coins/v1` | fresh streams; Kp0 alone uses the sealed seeds |
| 15 | arm C reads sign sequences from the M77 file | no Indus file is opened | not needed |

**Unchanged:** the placement family, the statistic and its 0.25, the search, 999 re-pairings, the pass level 0.01, the bars of 16 and 1 in 20, the edge rule, F2 and F3.

## Aborts
- **A1.** A recount differs from the tables above. The row and name counts must match exactly, shares within 0.01. Stop and redraft.
- **A2.** The hash of the BIGR export, of the checked table, of the units file or of the sealed `run.py` does not match. Stop.
- **A3.** Kp0 does not reproduce the sealed numbers. Stop.
- **A4.** The run was not started through `board/run.sh`. It runs at `nice -n 20` with at most 4 workers and `python -I`.
- **A5.** The run opens the akshara label map, any Indus file, or any key file. Or the script that builds the name units opens the Indic column. Stop.
- No rerun, no tuning and no fix tag after any T on a real pair is seen.

## Seeds
Every random stream is seeded from the first 8 bytes of SHA-256 of `crossread_coins/v1/<cell>/<arm>/<half>/<m>/<set>/<purpose>`, read as a big-endian integer as in the sealed code. Purposes are `set/<s>`, `perm/<index>`, `init/<index>/<restart>`, `noise`, `code` and `relabel`. No global random state.

## Limits stated in advance
- **Editor-resolved symbols.** Stated under "Symbols and sounds". Power is an upper bound. The false-pass half transfers.
- **The unit rule is not blind.** It was written by someone who had read the pairs and knows the readings.
- **One historical set.** All sets are subsets of 30 to 42 names from one region and three centuries. Many kings share name elements.
- **One language pair.** Greek into Gandhari Prakrit, an alphabet into an abugida. Both are Indo-European and both write vowels. A name crossing into a script that writes whole words would lose more.
- **A known answer chosen because it worked.** This is the case where cross-reading succeeded. A pass says the rule can transport. It does not say how often it would.
- **The legend start is given.** Many coin legends run in a circle. The editors chose where each one starts.
- **Two source families.** Most of the Indo-Greek legends come from one typology. The later names come from page captions and an 1886 catalogue.
- **Real mismatches are too few to test.** The RM list is expected to hold under 10 types.
- **The penalty weight was fitted on a generator of Ur III shape.** Coin legends are longer, and their titles are more uniform. The weight is not refitted.
- **Cell D is a weak dial.** 46% of its sets reverse nothing. A pass in D says little more than a pass in P.
- The search is a hill climb. A weak search costs power and cannot raise the false-pass rate.

## Cost
- **Measured on synthetic sets at coin shape** (15 symbols per legend, 3 to 5 units per name): 6.4 ms per value of T at 15 pairs in arm B1, 11.9 ms in B2. So a set that runs all 999 re-pairings takes about 6 to 12 seconds.
- **Count of sets:** about 500 with every cell, arm and rung, and about 1,000 if F1 is applied.
- **Estimate: 1 to 2.5 CPU-hours** with no early stopping, under 40 minutes of wall time at 4 workers. Re-paired sets stop early and cost about a hundredth of that. F2 holds the 6-hour limit.
- No Indus data, no cloud, no GPU.
- About 1.5 days of work. Most of it is the table and transcriber B's pass through Gardner.

## Odds (from brief 11, not revised)
Gate passes 85%. K0 passes as sealed 35%. With F1 60%. Informative 80%.

## Decisions and open questions
1. **The table's second source.** Gardner 1886 for transcriber B. Agreed? The alternative is coin photographs on Wikimedia Commons, which are slower and closer to the reading gate.
2. **Whole akshara as the symbol**, with BASE record only. Agreed?
3. **F1 changes the name side only.** The other reading of "consonants only" also drops the vowel marks from the symbols. That is cell BASE under F1, record only. Agreed?
4. **K0 in arm B1 only**, with no move between arms. Agreed?
5. **"Titles stripped" is read as cell TS**, the legend cut to the name word, reported as an upper bound. NS is added as the control. If the coordinator meant another cell, it must be said before sealing.
6. **The 20 overlapping sets** with the sealed bars. Agreed? The other choice is to report the 2 or 3 disjoint sets alone, which cannot carry a bar of 16 in 20.
7. **Gate at 30 with no fallback.** BIGR alone gives 28. If the later names fail the protocol the study does not run. Agreed?
8. **The compute lock.** The run touches no Indus data and is small. This draft still starts it through `board/run.sh`. The coordinator may waive that.
9. **Gandhari.org** would be the best single source for the later names. Using it needs a licence statement or permission. Nobody has been contacted.
10. **Where the result goes.** Under readings 3 to 5 a sentence is proposed for section 4 of `anchor_objects.md`. That file is a sealed prereg, so the sentence would be an addendum, not an edit. The coordinator decides.

## Before sealing
- A check that the v2 fixes are applied.
- Decisions 1 to 10 are ruled (below).

## After sealing, in this order (decision 11)
- Hash the comparer script. Then build the table and the lists RM and RM2 under the sealed protocol. Hash them. Count N.
- Build the later title words from the Greek column alone. Hash them.
- Write and hash the code. The code checks the gate before any T.

## Decisions, ruled 2026-11-25 (project lead, before review)
1. Gardner 1886 is transcriber B's source.
2. The symbol is the whole akshara, with BASE as record only.
3. F1 changes the name side only. BASE under F1 is record only.
4. K0 runs in arm B1 only, with no move between arms. Coin legends have a known reading direction.
5. "Titles stripped" means cell TS, with NS as the control, as drafted.
6. The 20 overlapping sets carry the sealed bars. The disjoint sets are reported as record only.
7. The gate is 30, with no fallback.
8. The run goes through `board/run.sh` and takes the Indus compute lock: at most 4 workers, `nice -n 20`.
9. Gandhari.org is not used.
10. Any sentence for `anchor_objects.md` section 4 is an addendum, decided by the coordinator after the result.
11. **Order changed from "Before sealing":** this prereg, including the transcriber protocol, is sealed first. The table and the list RM are then built by two fresh blind transcribers under the sealed protocol, and hashed. Code is written and hashed after that, and the gate is checked by the code before any T.

## Review log
**v2 (fresh review of v1; 6 must-fix items, applied as worded).**
1. Z\* and P\* characters are deleted before cutting. NS and TS take the name span from the truth marks.
2. Agreement is on keys, with a comparer script hashed before B's table exists. Run symbols are A's aksharas.
3. B gets only the protocol sheet, now a section of this file. A never uses Gardner.
4. Later title words come from the Greek column by rule. List RM2 added. Brackets defined. Both "before sealing" clauses on the table are gone, and "Before sealing" follows decision 11.
5. Reading 1 split: Kp0 is fixed before any real pair; a K0a fail ends the study. Reading 4b added. Kq failing consonant-only after K0b failed is reading 5. F5 says the same.
6. The "school rule" claim is replaced.

Smaller items: the gate note (about 21 from BIGR; misspellings copied as given), B works from page scans, ODbL and CC BY-SA rows in separate files, and cell D's 46%.

The reviewer's counts (3,298 spaces, 188 no-break spaces, about 21 names, Gardner's missing kings) were not rechecked by the drafter. No T was computed on any real pair. The ruled decisions are unchanged.
