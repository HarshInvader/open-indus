# Onomasticon for the M1 crib attack (board task #2)

## Verdict

**Done, with one gap that matters.** The name stock of the period is now in one file (7,776 rows; 7,066 broken into syllables), and the short lists the crib attack needs are ready. But the names of people *from* the Gulf and Meluhha are still very few: 21 people are explicitly tied to Meluhha, Magan or Dilmun, and only 2 of them (na-na-sa, sa-mar) have names that are clearly neither Sumerian nor Akkadian. Most "Gulf-linked" rows are Mesopotamian officials named in texts that mention the Gulf, not Gulf people. A crib attack can therefore test "Mesopotamian-type names", but it cannot test "Dilmunite names". The second option has no list to test against.

Names in Sumerian, Akkadian and Amorite all repeat a syllable *less* often than chance. If a foreign Indus text has a repeated sign, that counts weakly against reading it as one of these names. It does not count against a logogram or a name with a title attached.

## Files

| file | what |
|---|---|
| `names.csv` | name, written (cuneiform spelling), syllables (dot-separated), n_syll, language, lang_basis, source, source_text_id, date, role, gulf_link |
| `short_gulf_core.csv` | **use this first**: 21 Meluhha/Magan/Dilmun persons + 6 Gulf deities + Agarum, syllabified |
| `short_Sumerian_top150.csv`, `short_Akkadian_top150.csv`, `short_Amorite_top150.csv` | the most attested distinct names per language (Amorite has only 95) |
| `deities_formulas.csv` | Inzak, Enzag, Ninsikila, Meskilak, Enki, Panipa, Agarum, and 3 legend formulas, each with its verification status |
| `stats.json` | per language and per source: length distribution, syllable frequencies (top 40), CV shapes, repeat rates with a permutation null |
| `gulf_manual.csv` | hand-entered literature rows (source for the above) |
| `build_names.py`, `short_lists.py` | rebuild: `.venv/bin/python -I experiments/onomasticon/build_names.py && .venv/bin/python -I experiments/onomasticon/short_lists.py` |

Sources: ORACC `epsd2/names` (1,222 personal names, ED IIIb to OB), `epsd2/admin/oldbab` (4,208 OB names), `rimanum` (533 OB names, an archive with many foreign people), all CC0, in `raw/`. The CDLI dump already in the repo: 1,330 distinct Ur III seal-owner names, plus 473 name/text pairs from Ur III, Old Akkadian and OB texts that mention Dilmun, Magan or Meluhha. Also `experiments/meluhha/catalogue.csv` and literature.

## Numbers (distinct syllable strings)

| group | n | mean syllables | lengths 2 / 3 / 4 / 5+ | any repeated syllable | permutation null | initial doubling |
|---|---|---|---|---|---|---|
| Sumerian | 1,299 | 3.87 | 96 / 387 / 494 / 321 | 0.096 | 0.139 | 0.021 |
| Akkadian | 1,922 | 3.75 | 123 / 773 / 624 / 402 | 0.085 | 0.101 | 0.015 |
| Amorite | 95 | 3.47 | 11 / 41 / 32 / 11 | 0.042 | 0.123 | 0.011 |
| unknown (no marker) | 2,192 | 3.63 | 256 / 768 / 784 / 339 | 0.126 | 0.078 | 0.021 |
| Gulf-linked (all languages) | 275 | 3.45 | 41 / 111 / 88 / 34 | 0.120 | 0.084 | 0.033 |
| Meluhhan? (na-na-sa, sa-mar) | 2 | 2.5 | | 1 of 2 | | 1 of 2 |

- **Permutation null:** syllable tokens shuffled across names within the group, with name lengths kept, 50 shuffles. Labelled names avoid repeats; the "unknown" pool runs above its null. That pool holds most hypocoristics (ba-ba, a-a, nu-nu), which the language heuristic leaves unlabelled. A short repeated name is therefore more likely a nickname-type name than a full Sumerian or Akkadian name.
- **Syllable inventory:** Sumerian 288 types, Akkadian 408, Amorite 107, Gulf-linked 169.
- **Syllable shapes, Akkadian:** CV 3,522; CVC 1,965; V 1,090; VC 627. Sumerian is close: CV 2,496; CVC 1,356; VC 687; V 480.
- **Top syllables:**
  - Sumerian: lu, ur, gal, nin, e, a, en, ga, mu, na.
  - Akkadian: a, i, li, šu, tum, il, na, ma, num, ya.
  - Amorite: ya, mu, su, a, il, el, da, gan, yah, di.
  - Full lists are in `stats.json`.
- **Typical name length** is 3-4 syllables in every language. An Indus foreign text of 3-6 signs fits a syllabic name only if it has almost no logograms or titles.

## How syllables were made

Cuneiform spellings are split into sign values with determinatives dropped. A V-final sign merges with a following VC sign of the same vowel (sa-ar → sar), and ia → ya. In names tagged Akkadian or Amorite, dingir → il; the logograms UTU, AMAR.UTU, EN.ZU and a few others map to Šamaš, Marduk, Suen and so on. Syllables never cross a sign boundary otherwise: lugal-ezem → lu.gal.e.zem. Names containing a broken sign (x) or an unmapped logogram get no syllables (710 rows).

## What failed or was not checked

- **Language labels are a regex heuristic, not a source tag.**
  - I hand-read 45 random labelled names and judged about 43 plausible. The judge is me, so treat this as a rough figure.
  - 39% of rows stay "unknown".
  - Known errors: the Sumerian name dingir-ra was tagged Akkadian and syllabified il.ra; lowercase divine names like iškur are not turned into Adad.
  - Elamite has no baseline at all. The Susa Old Elamite names were not collected, and that is the main missing language list.
- **CDLI co-text names are noisy.** Only names that follow ki / giri3 / kiszib3 / dumu / igi, or come before szu ba-ti, are taken, and only if the name is also known elsewhere. Most are Mesopotamian scribes, officials and shippers, not Gulf people.
- **Not available in our dump:** the Old Babylonian Ur Dilmun-trade texts (UET 5, Ea-nasir and others) and the Durand stone. Ea-nasir, Nanni, Lu-Enlilla, Inzak, Meskilak, Agarum and the formulas are entered from the literature. Their spellings are not checked against photos.
- **Panipa and "Yagli-El servant of Panipa"** come only from the task brief (Laursen et al. 2026), and that paper was not read. They are marked UNVERIFIED.
- **BDTNS was not queried** (the CDLI dump plus the meluhha catalogue already include its Meluhha hits). The 560 MB ORACC Ur III admin corpus was not downloaded; Ur III comes from seal legends only.
- **No Indus data was touched,** so no pre-registration was needed.

## Next

1. Add an Elamite name list (Susa, Old Elamite and sukkalmah texts) as the third foreign baseline for the crib attack.
2. When task #1 lands, add any cuneiform legends on Gulf seals to `gulf_manual.csv` (each one is a new name).
