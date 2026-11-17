# Release notes, v1.0 (2026-11-15)

**In one line:** we can describe how Indus texts are built and what roles their sign classes play. We cannot say what any sign means or how it sounds, and no one can until new kinds of evidence turn up. This release freezes the corpus, the code, the tests and the predictions, so anyone can check the work or score new finds against it.

The "levels" below follow the claim ladder in `README.md`. It is modelled on how Proto-Elamite was partly read.

## What is established

### L0, structure: done

- **Sign order is grammar, not chance.** On unseen texts, the real order beats every reshuffle of its own signs in 40% of 321 cases. Chance is 5.7%.
- **It is a word-and-syllable script (logo-syllabic).** It has about 400 signs, with an estimated 565 in use. Its frequency profile sits with Proto-Elamite and Sumerian, not with Linear B or an alphabet.
- **Texts written left to right are genuine reversals**, not errors: 31 of 34 such lines.

### L1, function: largely done

- **Each kind of object has its own vocabulary.** Seals, tablets, copper tablets and pottery can be told apart from their text alone, on unseen texts (AUC 0.67 to 0.87).
- **Small ticks on a fish sign move it to the closing slot.** This is a mark inside a sign that has a grammatical effect.
- **"Two-tier six + fish" is a fixed expression.** "Seven + fish" is essentially absent.
- **The fish signs form one word class.** They swap for each other and combine with each other.
- **Name cores are one or two word-signs, not spelled-out syllables.** Common sign pairs keep a fixed order.
- **An 11-role functional grammar** parses 76% of unseen texts, against 44% for shuffled texts. That shows positional classes exist. Whether these exact 11 roles are right is only weakly supported.
- **Gulf round seals break Indus sign order.** This fits Indus signs being used for another language, though pseudo-writing is not ruled out.
- Full table with numbers: `README.md`, "What we can defend".

### L2, semantic field: open

No sign class has yet been tied to a field of meaning by evidence from outside the text, such as object, findspot or measure, on held-out data. Every attempt so far is either refuted or untestable (below).

### L3, denotation: open

No sign is tied to a specific referent by its picture, by arithmetic or by physical measure. Some examples that failed:
- Picture signs do not match the animal on their seal (17 pre-registered tests).
- Stroke counts do not track object size or the Indus weight series.
- The "M328 = measure" reading is dead.

### L4, sound: out of reach without a bilingual

Our planted-language experiments show that statistics cannot recover sound values, or identify the language, from a corpus like this one. That holds even with a related language and far more text. Language constraints from outside the script still apply. It was not Sumerian or Akkadian. Vedic Indo-Aryan is unlikely for this period, and Proto-Munda is strained. Dravidian remains open but is unproven.

## What is refuted

Each entry in `docs/NEGATIVE_ATLAS.md` gives the test, its power, and what would reopen it. The headline refutations:

- **Every published sign-to-sound key tested scores at chance.** That covers Yajnadevam's Sanskrit key (z = 1.0, p = 0.15), Pierson, Fairservis and S.R. Rao. The scoring these claims rely on cannot even recognise a true key.
- **No hidden syllable grid** of the kind Ventris used for Linear B.
- **No spelling clues to sound:** no phonetic complements, homophone sets, ligature breakdowns, silent classifiers or rebus alternations.
- **No relational readings.** There is no "son of" sign and no person network across seals. Titles do not cluster by part of the city.
- **No travelling place names**, and no foreign names spelled by sound on Gulf seals.
- **Numerals are not a base-10 or base-12 system with units.** The 12-stroke sign is a ceiling, not a unit.
- **What a sign depicts does not predict its grammatical role.** Signs that look like an object are not used on that object.
- **26 earlier positive results were reversed or weakened by our own red team.** Atlas section 11 lists them.

## What is untestable now, and what would unlock it

Each row is a route the current data cannot decide. These are not refutations.

| Question | What would unlock it |
|---|---|
| Does any candidate language fit? Is it a language or a non-linguistic code? Which language family? | A bilingual text, or about 10-20 sign values from a bilingual proper name. Failing that, longer continuous texts than seals provide. |
| Word-level (cognate) decipherment | Word division, plus a lexicon of the right language covering about half the words |
| Do numbers track object size, mass or capacity? | Per-object measurements for about 40 inscribed objects of one class (museum masses, a bangle table, the Harappa sherd database) |
| Do title signs mark what a sealing closed? | 40-80 inscribed door sealings with recorded findspots |
| Is a sign tied to a craft or workshop? | Craft coding for the about 700 Harappa tablets that lack it (HARP trench records, CISI 3.1 lot list) |
| Carver "hands" and seal-to-sealing links | Rescans at 30 px/mm or more (1200 dpi or RTI), and CISI vol. 3 |
| Does sign M328 depict the vessel held in offering scenes? | High-resolution images of tablets M-478/479/480 B, H-177 B and H-180 B, with human raters |
| A cuneiform anchor for a Meluhhan seal | Imaging of Ur-Lamma's sealed receipts, CUSAS 40/2 1582, Nisaba 15 0371 and BM 120573 |
| Do the forward predictions hold? | New inscriptions published after 2018: Fuls 2022-23 corpus, CISI 3.2/3.3, IAR 2012+, Binjor and Rakhigarhi reports |

Who to ask, and for which object, is in `docs/HUMAN_LEADS.md`.

## Predictions for future finds

`docs/PREDICTION_REGISTRY.md` indexes every hash-frozen prediction, with pass and fail bars and a scoring script. An excavator adds rows to `experiments/new_finds/new_texts.csv` and runs `experiments/new_finds/score.py` and `score_leads.py`. Hashes are in `docs/prereg/HASHES.txt`.

## Reproducibility

- `scripts/reproduce.sh` rebuilds the corpus and checks the prereg hashes. It then re-runs the headline scripts in a scratch copy and compares every output with the committed one.
- Results of that check are in `docs/REPRO_REPORT.md`:
  - 36 scripts reproduced exactly, 13 within resampling noise, and 2 differ. 25 heavy, network or rater-based scripts were skipped.
  - The README's Gulf q-value across all tests (0.086) ranges from 0.020 to 0.086 depending on Python's hash seed.
  - `data/splits_v2.json` is frozen, not regenerable. Its sha256 is `7a2bd876a6b4025b105a4568ecd2cbba8089962863a68bad571b8b473f5d78ca`.
- 13 prereg hash lines no longer match their files. Most of these are amendments appended after hashing. One, `signlist_robustness.md`, changed with no amendment logged.
- Environment: Python 3.15.0, with packages pinned in `requirements.txt`.
- How to cite: `CITATION.cff`.

## Known limits

- ICIT is mostly a second transcription of the same objects as M77, not new data.
- Wave-1/2 results used a leaky held-out split (v1). The top claims were re-run on the leak-free v2 split.
- Iconic judgements of sign drawings were not blind and used drawings, not photographs.
- `README.md` lists the remaining limits under "Known weaknesses".
