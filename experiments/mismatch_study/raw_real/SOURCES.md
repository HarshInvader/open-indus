# Stage 5 real-script sources (mismatch_study)

Compiled 2026-11-19 for prereg `docs/prereg/mismatch_study.md` §3 and §6 (stage 5).
Every HTTP request used User-Agent `open-research-site/1.0`. Each source sits in its
own directory and nothing downloaded was executed. Counts came from helper scripts kept
outside `raw_real/` (`/tmp/mmsrc/`, run with `python3 -I`). Total downloaded: about 41 MB.
No Turkish, Azerbaijani, Czech, Slovak, Dutch or German corpus was downloaded (see the
note on German under Cypriot).

---

## 1. Linear B / Greek

### Data already in the repo (not re-downloaded)

| file | sha256 | size | notes |
|---|---|---|---|
| `sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl` | `0526b40ce087ced556e27f618b47396a6e7e7e8961b2826d6a50c24dc77907de` | 1,161,030 B, 6,300 items | DAMOS (Oslo). Items by heading: KN 4,228, PY 1,004, TH 438, MY 107, TI 72, KH 53, MI 6, no heading 368. Hyphenated syllabic word tokens: about 12,200 (5,015 types; rough regex count). Anchor words present: `a-mi-ni-so` ×11, `ko-no-so` ×8, `tu-ri-so` ×8, `pa-i-to` ×44, `ku-do-ni-ja` ×10. |
| `experiments/cognate_decipher/ext/greek/homer_001.xml` | `cd74db353d411844774d7a6b5d870084967e6f7b082a30ea5be86f9e164bd71b` | 2,043,739 B | Homeric Greek (TEI/EpiDoc) |
| `experiments/cognate_decipher/ext/greek/homer_002.xml` | `7b13c553363bed18c86c5db3e350b9482b0ec5cab1ecf9f4d6de8438d6d96f6a` | 1,557,943 B | Homeric Greek |

Note for the retrodiction: in mid-1952 Ventris had the Knossos tablets (Scripta Minoa II,
1952) and Bennett's 1951 Pylos edition. He did not have TH, MY (mostly 1952 onwards) or the
1953 Pylos finds. To be historically faithful, restrict the cipher corpus to KN plus PY.

### Downloaded (anchor documentation)

| path | URL | license | sha256 | size |
|---|---|---|---|---|
| `cam_classics_linearb_process/process.pdf` | https://www.classics.cam.ac.uk/system/files/documents/process.pdf | Freely accessible teaching page from the Cambridge Faculty of Classics (Mycenaean Epigraphy Room). No explicit license; kept for citation only. | `32c33fa242de9738e2d85f2bd7dcca6863a46d715b5bfa3652a23d4b38acc552` | 518,882 B |
| `palaima1993_ventris_blueprint/1993-TGP-MichaelVentrisBlueprint.pdf` | https://sites.utexas.edu/scripts/wp-content/uploads/sites/3428/2020/05/1993-TGP-MichaelVentrisBlueprint.pdf | Freely accessible author PDF on the UT Austin PASP site. No explicit license; kept for citation only. | `5e3d9aa6dfe60a7b99ab1423f74800518852045f107ba72012bcee408de0215f` | 6,014,085 B |

### Historical anchors (only what the opened sources state)

Sources: **[CAM]** "The Decipherment Process", Cambridge Faculty of Classics, 5-page PDF
(2013), and **[PAL]** T. G. Palaima, "Michael Ventris's Blueprint" (1993), printed pp. 21–26.

Structural anchors, available before any sign value:
- The script is a CV syllabary with about 87 phonetic signs, separated from ideograms. Bennett's sign list made frequency statistics valid. [CAM p.1–2]
- Kober's triplets: word groups that differ only in their final signs. They show inflection and give same-consonant / same-vowel relations, which Ventris turned into a row × column grid. [CAM p.2; PAL PDF p.3, "Kober's triplets"]
- The grid itself: in Work Note 17 (Feb 1952), signs in one column share a vowel and signs in one row share a consonant. [CAM p.3]

Sign values Ventris fixed or guessed, in order:

| step | value(s) | basis | source |
|---|---|---|---|
| 1 | **a** | very frequent word-initially, so probably a pure vowel | [CAM p.3] |
| 2 | **ni** | resemblance to the Cypriot syllabary sign | [CAM p.3] |
| 3 | **mi, so** | `a-mi-ni-so` = Amnisos, the harbour of Knossos, filled in from a and ni | [CAM p.4] |
| 4 | **no, ko** | `?-?-so`: the 2nd sign is in ni's row and so's column, giving no. The 1st sign is in the o column, so the word is `?o-no-so` = Knossos and the sign is ko | [CAM p.4] |
| 5 | **tu, ri** | `tu-ri-so` = Tylissos on tablet "Knossos 59". Palaima: that tablet gave "one descriptive term and one known Cretan place name, i.e., a total of six sign values (we, ka, ta, tu, ri, so)" | [PAL printed p.26, PDF p.7] |

These place-name anchors give **a, ni, mi, so, no, ko, tu, ri** (8 signs). Counting Palaima's
`we, ka, ta` from the descriptive word on Knossos 59 gives 11. Through the grid, each value
also fixes a consonant row or vowel column: for example, `ni` + `no` fix the n-row and
`so` + `no` + `ko` fix the o-column. Stage 5 should take the anchors as these 8 (or 11)
sign identities plus the grid's row/column partition, as far as Kober/Ventris had it.
Caveat from [PAL p.21 caption]: in his mid-June 1952 grid Ventris still merged the t-/d-
series and lacked the labiovelars. The historical grid therefore does not match the final
values one for one.

I did not open Ventris's Work Notes, Chadwick's *Decipherment of Linear B* or
Ventris & Chadwick 1953 (JHS 73): none has an open copy I could confirm as legal. Values
Ventris carried over from Cypriot beyond `ni` are not documented here.

**Verdict: yes.** The sign corpus (DAMOS), the model-language text (Homer) and the
place-name anchors are all in hand. The one remaining decision is how to encode the
partial grid as a prior.

---

## 2. Ugaritic / Hebrew

### Already in repo
- `experiments/cognate_decipher/ext/neurodecipher/uga-heb.no_spe.cog`: sha256 `b4ef9c91a245cb1ff1583c56a3c243fb3db8078da12fb9b895982dffebe4fa7e`, 43,952 lines (Luo et al. 2019 cognate list).

### Downloaded

**(a) Copenhagen Ugaritic Corpus (CUC), Text-Fabric v0.3.0** → `cuc_ugaritic_tf030/`
- URL: `https://raw.githubusercontent.com/DT-UCPH/cuc/1cf507c668bc6d860a39d432569e7e7f3e81ccb9/tf/0.3.0/<feature>.tf`. Repo https://github.com/DT-UCPH/cuc, pinned at commit `1cf507c6…`. README.md and LICENSE.md were saved from the same commit.
- License: **CC BY-NC 4.0** (stated in LICENSE.md, README and every .tf header). Older Zenodo releases (10.5281/zenodo.10695308) carry CC BY 4.0. Non-commercial research use is fine; attribute the CACCHT project.
- 37 files, 4.8 MB. Per-file hashes are in the appendix.
- Contents: 342 KTU tablets, 8,692 lines, 30,843 word nodes, 165,665 sign slots. The `g_cons` feature (consonantal word reading) has 30,171 non-empty word tokens and 5,786 types. Top tokens: w 1849, l 1446, b 979, bn 408, **bʿl 391**, il 352, **mlk 270**.
- Alphabet: 27 consonants plus 3 aleph signs (a, i, u) = 30 letters, which matches the 30-sign Ugaritic abjad. Ugaritic transliteration is one letter per cuneiform sign, so `g_cons` letters serve directly as the sign-level corpus. `usign` gives the Unicode cuneiform.
- Caveats: v0.3.0 also contains Hurrian, mixed Ugaritic/Hurrian and alphabet-exercise texts. Filter on the tablet-level language metadata (`tablet_info`) and drop `x` (illegible) tokens. Word division follows the scribal divider, which matches the historical condition.

**(b) Open Scriptures Hebrew Bible (Westminster Leningrad Codex 4.x)** → `oshb_morphhb_wlc/`
- URL: `https://raw.githubusercontent.com/openscriptures/morphhb/db6c5c9b46b8f39346f10915ddb1a70dcd429901/wlc/<Book>.xml` (39 books; VerseMap.xml excluded). LICENSE.md and README.md saved from the same commit.
- License: WLC text is **public domain**; OSHB lemma/morphology is **CC BY 4.0** ("credit the Open Scriptures Hebrew Bible Project").
- 39 OSIS XML files, 27 MB. Per-file sha256 in the appendix.
- Count (each `<w>`, consonants U+05D0–05EA only, morpheme slashes removed): **306,785 word tokens, 39,956 consonantal types, 27 letter forms** (22 letters plus 5 finals, which need folding).
- Caveat: Daniel and Ezra contain Biblical Aramaic portions. Drop them, or tag them via the `<w>` `lang` / morph prefix, for a pure Hebrew model.

**(c) Anchor documentation** → `day2002_ugaritic_decipherment/day_dies_diem_docet.pdf`
- Peggy L. Day, "Dies diem docet: The decipherment of Ugaritic", *Studi Epigrafici e Linguistici* 19 (2002) 37–57.
- The original URL http://sel.cchs.csic.es/sites/default/files/06day_2a4aeb99.pdf was unreachable (connection timeout/refused). I fetched the Internet Archive capture instead: https://web.archive.org/web/20241203001720id_/http://www.sel.cchs.csic.es/sites/default/files/06day_2a4aeb99.pdf
- License: freely posted by the journal; no explicit license. Kept for citation only.
- sha256 `2cd378bb4c8266fb5224534011a44aa15a33a61e2cd751f7925109dbf0a836d3`, 1,814,820 B, 21 pp.

### Historical anchors (Day 2002; printed page numbers)

Structural anchors, published before Bauer started:
- **Word dividers.** Virolleaud, 20 Sept 1929: a sign repertoire of about 26 signs, so the script is alphabetic, not syllabic, and it uses word dividers (p. 41). Bauer could plan his attack in advance "as the inscriptions' employment of word dividers was part of the published record" (p. 43 n. 37).
- **Short words, so vowels are probably not written.** Virolleaud inferred this from the brevity of the divided words (p. 42).
- **Six-sign proper name on four axeheads.** It recurs at the start of tablet 18, preceded there by a single sign. Virolleaud proposed that this single sign is "to" (Akkadian *ana*), marking a letter's addressee. On the fifth axehead the name is preceded by a 4-sign word, which he proposed means "axe" (p. 42).

Bauer's method (p. 43 n. 37) is effectively the attack under test. He assumed West Semitic, found the signs that occur as prefixes, suffixes and single-sign words, compared them with West Semitic prefix/suffix/one-letter words and their frequencies, and got 2 candidate values for each of 4 signs. He then took the tablet-18 single sign as **l** and searched for common West Semitic words, divine names and a 4-consonant word for "axe".

| anchor | value(s) | source |
|---|---|---|
| single-sign word "to" before the name on tablet 18 | **l** | Bauer (p. 43 n. 37); Dhorme reached the same as "Phoenician lamed" (p. 45) |
| 4-sign word on the 5th axehead, read as "axe" | **g r z n** (Bauer, May 1930; Heb. *garzen*). Later revised to **ḥ r ṣ n** (Oct 1930, p. 49 n. 78). Only **r, n** survive, and Bordreuil argues the word is a personal name, not "axe" (p. 49 n. 78) | pp. 44, 49 |
| word at the head of each line of tablet 14 | **bʿl** (Baal) | Dhorme (p. 45) |
| royal word | **mlk** | Dhorme (p. 45) |
| opening of tablet 18 | **l rb khnm** "to the chief of priests", reached after taking Bauer's **n** | Dhorme (p. 45) |

Scores reported by Day for comparison with a retrodiction: Bauer, about 20 values claimed in May 1930 (p. 43). Bauer's monograph alphabet, Sept 1930: 14 of 25 correct (p. 46). Dhorme, 15 Aug 1930: 29 signs, 18 correct (p. 45). Bauer, 5 Oct 1930: 22 of 26 correct plus 3 nearly correct (p. 50).

The minimal anchor set a stage-5 run can claim is therefore: word divider + "alphabetic, consonantal" + West-Semitic model + **l** (from the "to" hypothesis). The richer set adds **b, ʿ, m, k, r, n** via bʿl / mlk / the axe word. The `grzn` anchor was partly wrong (g, z), which makes it a natural noisy-anchor condition.

Missing:
- The historical cipher corpus was only the 1929 Ras Shamra tablets (Virolleaud's editio princeps, *Syria* 10, 1929). These still need mapping to KTU numbers so the CUC can be restricted to them; I did not do this. The full CUC is far larger than what the decipherers had.
- No running-text Ugaritic corpus under a permissive (non-NC) license was found.

**Verdict: yes.** The cipher corpus (CUC, NC license), the model corpus (WLC) and the anchors are all in hand. For historical fidelity the 1929 tablet subset still needs to be identified.

---

## 3. Cypriot syllabary / Greek

### Corpus search result

An openly licensed digital corpus **does exist**: the BBAW/TELOTA digital edition of
*Inscriptiones Graecae* XV 1 (Karnava & Perna with Egetmeyer, 2020;
https://telota.bbaw.de/ig/). Each record's TEI header states CC BY 4.0, with a link back
to the record page required. It has syllabic transliterations such as `ị-te-ọ-…`.
- Coverage is IG XV 1 nos. 1–410 only: Amathus, Kourion and Marion. That is about 592 entries, of which 170 are interpreted as Greek (counts from the derived snapshot https://github.com/hawkinsnick/Cypriot-syllabic-Greek, v1.0.0, created Oct 2026, data CC BY 4.0 / project material CC BY-NC). **The Idalion bronze tablet and the Idalion bilingual are not included.** The full Cypriot corpus (Olivier/Perna, about 1,400 inscriptions; Masson's ICS) is not open.
- **Not downloaded.** Every IG XV record embeds a **German translation** (`<div type="translation" xml:lang="DE">`). German is a sealed held-out family. While checking the license I viewed one sample record (IG XV 1, 1) through the GitHub API, which exposed one German sentence of about 20 words. Nothing was saved. Fetching this corpus needs a decision from the study owner. One option is a fetch that strips the `translation` div before writing to disk; another is to wait until the Germanic family is unsealed after stage 3.
- Even complete, the corpus is small. 170 Greek entries are mostly short dedications and epitaphs, probably a few thousand syllable tokens (not counted). That sits at or below the 2.5k-token floor of the stage 2 grid.

### Downloaded (anchor documentation)

| path | URL | license | sha256 | size |
|---|---|---|---|---|
| `tsba_vol1_1872_smith_cypriote/transactionssoc07nashgoog_djvu.txt` | https://archive.org/download/transactionssoc07nashgoog/transactionssoc07nashgoog_djvu.txt | Public domain (1872; archive.org flags it NOT_IN_COPYRIGHT). OCR text only; the 25 MB PDF was not fetched. | `8acca05360ca3977f24a7438b9ba8b65b1ed3815ff076027c4c27d8f6f063412` | 869,621 B |

### Historical anchors

Source: George Smith, "On the Reading of the Cypriote Inscriptions", *Transactions of the
Society of Biblical Archaeology* 1 (1872) 129–144 (OCR lines ~8000–8330). Lang's companion
paper on the find is at pp. 116–128, and Birch on the Dali bronze tablet at pp. 153–172.

- **The Idalion bilingual** (Phoenician–Cypriot, found by R. H. Lang at Dali). The Phoenician side was already read: a dedication "in the fourth year of Melekyaton king of Kitium and Idalium". The Cypriot first line is divided by dots into 5 words (p. 132).
  - Words 1 and 5 differ in one sign, so they are two case forms of **king**.
  - Word 2, the longest (7 signs), is **Melekyaton**. Its last sign is a case ending, and "the other six characters then agree letter for letter with the Phoenician word, and give the values of six Cypriote signs" (p. 132).
  - Words 3 and 4 share their final two signs (genitive), so they are **Kitium** and **Idalium**. The Cypriot order differs from the Phoenician (p. 132).
  - Idalium: an initial conjunction sign, then 3 stem signs **e-da-li**, then a 2-sign case ending. The sign for *l* is shared with Melekyaton (p. 133).
  - The *k* sign in Melekyaton differs from the one in Kitium, so they are **ka** vs **ki**. This is the evidence for a syllabary of "between 50 and 60" signs (p. 133).
  - The "king" forms differ in their penultimate sign. Smith compared words for king in neighbouring languages and concluded the word is **basileus**, i.e. Greek (p. 133).
  - Result: "the phonetic values of eighteen of the Cypriote characters", "with more or less certainty" (p. 133).
- **Coin legends** (de Luynes 1852; Lang), read with these values: **E-u-a-go-ra** (Evagoras), *basileus*, *Stasioikos*, *Teukros … Paphos*, and the name of Idalium on a sphinx coin (pp. 134–135).
- Smith's sign-by-sign table is not legible in the OCR (it is in the plates). The exact list of 18 values is therefore **not recoverable from this text**; only the words above are. Several of Smith's vowel values were later corrected by Brandis, Birch and Deecke, none of which I opened.

The anchor set a retrodiction can claim is: syllabary of 50–60 signs, word dividers, and
the proper names Melekyaton / Kitium / Idalium plus the word *basileus*, all aligned through
a bilingual. That gives about 15–18 signs, some with wrong vowels. The model language is
Greek, which can reuse the Homer files (Arcado-Cypriot dialect mismatch).

**Verdict: partial / currently no.** An open CC BY corpus exists, but (i) it embeds German
translations, so it is blocked under the seal until the owner decides; (ii) it lacks Idalion,
the very texts that carried the anchors; and (iii) it is likely below the stage-2 minimum size.
The anchors themselves are documented from the primary 1872 source.

---

## Appendix: per-file sha256

```
db710308d6c9bb19484160657814d8c8db42d6fcb8b37c8f626db01b00e3f36f  19287  cuc_ugaritic_tf030/LICENSE.md
db853327879b4db5bb423c5708ede3a401a639c2e8f54733866ce0e4766df790  2685  cuc_ugaritic_tf030/README.md
81801ab0eff64b775d3139efbee5bca3309f9523ea94ca0b8f2510eeb4b9f6f6  126835  cuc_ugaritic_tf030/after.tf
a3148767b0fff240579cbdb6d82f842084ad19072d1c2f75b458613c8d83e9f8  171532  cuc_ugaritic_tf030/alt.tf
57047c2a69c502cb2da65f9c6553375eb7b6b735d8b8bc77629763250c75aaaf  8051  cuc_ugaritic_tf030/boundary_kind.tf
46173b72290ece618f3770f89afc31e5d3f19d3cb6601253660dc9b4694001ee  8155  cuc_ugaritic_tf030/boundary_next.tf
eb58c80f45f1ca69709f4fbd7151bc0313e3cf2627f9eedba34d44f77ac63ecd  8232  cuc_ugaritic_tf030/boundary_prev.tf
64960e4dd2892314399dced3b846efc1309fc394136135381be05ccc8db1018f  21450  cuc_ugaritic_tf030/boundary_source.tf
1bed72bcf9c719f0b67c491f23a6f3e0edec8413f1fd9c746311b6fd31b89ac7  370  cuc_ugaritic_tf030/catalogue_alias.tf
93d9d6216281bd96a604aca66b953303d98d9ccc2139e61ddd49c9471a52eab6  429  cuc_ugaritic_tf030/catalogue_alias_source.tf
3320519e365b8e64c5f8aa0dc06f60001578bc21f1bedcad1fda1a75d3bf9b45  388  cuc_ugaritic_tf030/catalogue_target.tf
9d220810b7ff3efdae865357791ce0d49f5636c3225e2fa35f3721f7a18e8701  539711  cuc_ugaritic_tf030/cert.tf
6614b441c00de4a370bf10d407fd7c7508fb91ab06c3bbab8cefd16a75dc06c8  1343  cuc_ugaritic_tf030/column.tf
47e814aaed70f54d016d156546b17dc2e2f45d2db657e963488370f784ea4c87  171468  cuc_ugaritic_tf030/cont.tf
9ca75a26aacb975f721f702899129a861bd62eb0c5c77b7becadf47281e7a37f  647609  cuc_ugaritic_tf030/emen.tf
aa6fbb31f3ee2c6292651216e3ace80adc419d63c706d56c68b68cd6686edf31  2357  cuc_ugaritic_tf030/erratum.tf
646ee9e3e3622f2f879759b9e72088aa1957458bdcb0c0ec068ce7bc493bbf22  409  cuc_ugaritic_tf030/fragment.tf
81643e7e77a3436f0465a3740d6a4cceb37bdb77386ba866f973f35b3da4ca73  138338  cuc_ugaritic_tf030/g_cons.tf
96404d6a47e777af07d5957b341fd935a4e100046f562714f6ee1d47c73bb19a  23142  cuc_ugaritic_tf030/line.tf
a64258ed8310854de0a3002aeb5404b26faff21d7a4a557dc67f7e75b6218df7  23257  cuc_ugaritic_tf030/line_label.tf
a9b68888f6b3e96e7d24c65d4f2039510701a4b9096080dfaa0f46b87fc6aa50  31063  cuc_ugaritic_tf030/numbering.tf
9359efd5b7ca3a091b33e1409d1f288edbfe05192cb3f93aa50a1a5beba43610  516450  cuc_ugaritic_tf030/oslots.tf
381ef493eaac7e121df70ce7865988c47589b058bebd9ade55f8568fee52e7cc  423  cuc_ugaritic_tf030/otext.tf
ba7f7686fe57b969153322907739d42ddacb4e955bb093e5e84fad3a750d796a  425  cuc_ugaritic_tf030/otype.tf
e49476d43a9ead281ba679dcdf3788b045788a269f13c6a89960596cedfc6dfa  357275  cuc_ugaritic_tf030/sign.tf
f80ffe9444ca96a853c1d085eec5bd4fdf15f23bc7c0f485d8844dca0e9d6dde  370  cuc_ugaritic_tf030/sign_index.tf
5c6934e4e455fc85dcb098c865a2f48908c7ba347bb14fcd6bb1d26b37005fca  44278  cuc_ugaritic_tf030/surface.tf
2a288619c378f48801617b6acf4960133977592d2a66573ee5472296d40c618d  43828  cuc_ugaritic_tf030/surface_cert.tf
3dbd0ab332a007186e2347d5a096c654fc491bf4708cb1629a9ecbe70aca8ff3  12676  cuc_ugaritic_tf030/synthetic.tf
cbe3e93e0a43af034d007667ac9cd6bc1b325cd31358877807ebfb2e0768d4c4  3453  cuc_ugaritic_tf030/tablet.tf
dcb2bc3b5c866d715f4f967e0caae359df38ee2cace2e871455e6d3b8d8a7f66  859  cuc_ugaritic_tf030/tablet_info.tf
e79d9ebeac3e7be39249ed215064f652c765453930629f167ca905c638423ec5  46502  cuc_ugaritic_tf030/trailer.tf
36604d3c796afcba616c9aa743b15859112933b9575ed16e283711d7620236ca  44735  cuc_ugaritic_tf030/trailer_emen.tf
5a46dac5d347a4aa63d18eaf8bd664c950f7d2ef6af8cf4679deea95842364fa  1046326  cuc_ugaritic_tf030/type.tf
43e5f999593321377a4b65a14c86e635e9edc1ea395351b76a8defb8a2dd5f09  172788  cuc_ugaritic_tf030/uafter.tf
a22d34ceffc5818bc5c8a1caf4968a6c887f38e3b36a34614a07da1da4b8302f  573932  cuc_ugaritic_tf030/usign.tf
892cf4972a4d95eab61924e1ebe0a262b976a66244f6b1e1a75bb95a517e8f74  92453  cuc_ugaritic_tf030/utrailer.tf
8b59992b6607c6ca0fc423813be8cc244f011c1da32bc8485c0c0f581a897ed4  1014881  oshb_morphhb_wlc/1Chr.xml
832ba10f605dce34c4888ee0a795d91edc2b293391d6ae9c36c36c6350761a3e  1189874  oshb_morphhb_wlc/1Kgs.xml
960432732c22286b82d80b6b25af8d10dc5f2e82a4e5e48b2e3a1b1eea17f3cb  1206608  oshb_morphhb_wlc/1Sam.xml
507294e8ca0fcf31ec25fe62fa24a7f2581f53116519bf08cfe96ff85e9c99fb  1222694  oshb_morphhb_wlc/2Chr.xml
056db5393beaef0a1159d9bcaac7dfd865df9bab2eb240ea90e9fa3f0c0e7449  1115537  oshb_morphhb_wlc/2Kgs.xml
e7793e141ed94eadbd2dfb23936abbb4062e81a7dcd41114a6e36644f50b8333  1013552  oshb_morphhb_wlc/2Sam.xml
6ad94c6a18076762f1a458720c62156d354e5111ee25719b7792b70792d0084d  201588  oshb_morphhb_wlc/Amos.xml
bc69d0fa9708dacb11ea6d587509250bf1bcc1b4343eac2d6e97f8b41518fc0d  569236  oshb_morphhb_wlc/Dan.xml
04f8087442a1e67a631cd70f2ac4e42fe0a780ae132edb165a3a29f3f290358f  1315399  oshb_morphhb_wlc/Deut.xml
2dfc858d19048f6479eca33b9fe781c2d7e9059e9ae3ab0b37b802d3afec02bb  285122  oshb_morphhb_wlc/Eccl.xml
f9b5b8adaf504dcac409bb6a27c9328967f47eeb4e920070cd53ef5301299019  292184  oshb_morphhb_wlc/Esth.xml
04868367cdacb6ccdc61488e923e20f918172042e6437842a0621f63ac5b847f  1524391  oshb_morphhb_wlc/Exod.xml
90bf8adfa66b2f6695c702263fe668755c99c6afc386202c12de4f704f5d4e46  1724378  oshb_morphhb_wlc/Ezek.xml
fb28ff697d0ee17eba5b4db47fb7261ee1870cea0d5701bfc77c9e28d4138129  369918  oshb_morphhb_wlc/Ezra.xml
0526e5c9a5fb4d907847645f954ed3d1268fa69decbd872056cedd2668d86449  1859928  oshb_morphhb_wlc/Gen.xml
2592b212d816775adc8dac46bd0c46263982c308a186dde64dfb8239c57bd2d1  79467  oshb_morphhb_wlc/Hab.xml
26ebbae4fe491cf89ce70e1264cbcbf66a562b497cb214b677e67a9a43ad545c  71754  oshb_morphhb_wlc/Hag.xml
f38ae44a3a97d142768bd5f4d40e77b69265184f9a5aec9e6af1b9b226e8daae  236712  oshb_morphhb_wlc/Hos.xml
0807678de609bdef284bed5400b94ddab570d101b593c7f59ae1939015572fa2  1548674  oshb_morphhb_wlc/Isa.xml
1a7ad7bc26a2cae1d3964230e8eb73043bc1f32505cb86cd69a25261dc39f493  1977728  oshb_morphhb_wlc/Jer.xml
7db3311184122f37a8fd52f3c7c0c4a6d2da7b77ee82f4fdb26bcba9171d297f  813715  oshb_morphhb_wlc/Job.xml
c0fefc6881afe949b023968106cdccc05a690734b8bb6e9aa48914d77e5369af  105277  oshb_morphhb_wlc/Joel.xml
1e1afcc3aaba1399d5c884ee106894c6bfca87c8c81fa57783ab75a923eee17d  80534  oshb_morphhb_wlc/Jonah.xml
a066200ab2269c0a86a2e9ba119a3d0fce8c5f7ecc44bb53ec134b83dffc6006  919916  oshb_morphhb_wlc/Josh.xml
3b3a909f04041dbd52dc6b7293a96ce75d94db8a90fdeda878943db7b8fac57f  904347  oshb_morphhb_wlc/Judg.xml
9bf4a2890c25372e4c1dc750d550bfb4eacfbfcb63c53123b0628159370d1878  1476  oshb_morphhb_wlc/LICENSE.md
be68fc6a913313367280c2596e28733ee8cf877c12a65227237733b40d0248c4  167766  oshb_morphhb_wlc/Lam.xml
e21e70265c9ef500182f8ccb4f4e1186e5a79e1169d24cef23cc479baf07b191  1085066  oshb_morphhb_wlc/Lev.xml
1583e6a701406dce7b8c2bf85e3522ec31383756de130685fc7c2eb6df8964b2  95722  oshb_morphhb_wlc/Mal.xml
267e111adc1b941e32444816af07aa136ecde02cb315cd42597f78b393e67a01  145482  oshb_morphhb_wlc/Mic.xml
5993b28bdbee3c922e3e93002d343a655493e8bd45e3472f3b62d77beadcb62c  69823  oshb_morphhb_wlc/Nah.xml
be082e95c206469122455b9849d4dd08da50c817732d8198c1beece90402801a  512876  oshb_morphhb_wlc/Neh.xml
02e4febfcc027d10b3e35e4f091eae67a40d26f37b6254faac6b4af053fe4896  1496830  oshb_morphhb_wlc/Num.xml
1e893e552a7ed7e2e6d4048637ff5da8a2853a9e4432f4095cede80b959d850c  44626  oshb_morphhb_wlc/Obad.xml
964f99c00239b53b854c4686c99490c8d1ac7664784a30afdfc23781a3abb161  678669  oshb_morphhb_wlc/Prov.xml
f8ca52eb40aff5bbcc69f5d9a4e6a668d93a5756d616e233986fa6602abec334  1925090  oshb_morphhb_wlc/Ps.xml
4a9e90f33e13d1330c9fcdbadf30f443611a250b77e9efb8651360610af0fa17  5170  oshb_morphhb_wlc/README.md
fb6a2660383c7176941cb87b2be182ef634b66d49d057635869f4d9cb1f0a11e  136188  oshb_morphhb_wlc/Ruth.xml
5cd6ae36d32c059aaf794af5a5eaed914ac643486db3e412eb0b969760db82ca  138554  oshb_morphhb_wlc/Song.xml
2e287c8d0e0abd3bf601eb8ef9b4ee6ca3ae12cf36c0ed1612a7dcca54a2e777  300202  oshb_morphhb_wlc/Zech.xml
eb5bd2a745fba1ffeed31dfafd834ce7c290929c992390be1a2b9451d22dea2e  87313  oshb_morphhb_wlc/Zeph.xml
```

## Decision on Cypriot (agent `paper`, 2026-11-19, before any run)
Cypriot is deferred until after stage 3, when the held-out boundary is hashed and the Germanic family is unsealed. Two reasons. The open IG XV corpus is probably below the 2,500-token floor. It also lacks the Idalion inscriptions that carried the historical anchors, so it cannot be a faithful retrodiction anyway. As amendment 1 (B4) allows, kill criterion 4 rests on Linear B and Ugaritic. Disclosure: one German translation sentence (about 20 words) was seen while checking the license. Nothing was saved, and no German text is used before stage 3.

Ugaritic stage-5 corpus: restrict to the tablets found in 1929 (the decipherers' material). The mapping to CUC catalogue numbers must be fixed in the stage-5 code header before it runs.
