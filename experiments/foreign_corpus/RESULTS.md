# Foreign corpus: every Indus-inscribed object found outside the Indus region (board task #1, H1)

## Correction (task #12, same day)

Gadd 1932 showed two duplicate rows (ICIT 3887 = M77 9902; M77 9845 = Laursen no.20) and one wrong merge (M77 9842 is Gadd 12, a pictorial device, now excluded). Re-run with the same pre-registered rule: **54 objects, 9/38 scorable break Indus order (1.9 expected, binomial p = 8.5e-5)**. The CSVs in this folder are the corrected ones; the numbers below are the original run. See experiments/foreign_readings/RESULTS.md.

## Verdict

We now have one list of **55 objects** with Indus signs from outside the Indus region: 18 from Mesopotamia, 6 from Iran, 11 from the Gulf, 7 from Oman, 3 from Central Asia and 10 unprovenanced but probably West Asian. It is in `foreign_corpus.csv`. **4 of the 55 are new to us**, but none of those 4 has a sign sequence we can use yet. **41 objects have 2 or more legible signs.**

Scored one by one against our validated Wells grammar, **10 of the 39 scorable texts break Indus sign order** (p < 0.05 against native seals of the same length). Chance would give about 1.95 (binomial p = 1.6e-5). Another 11 are borderline (p 0.05-0.20). Round Gulf seals and cylinders account for most of the breaks (7/22). Square seals have 2/7, and pottery and other objects 1/10. Every text from Oman pottery, Gonur, Altyn Depe, Shortughai and Hajar reads as ordinary Indus.

So the crib attack (#4) has **at most about 10 texts that are both well read and out of order**. Several of those have disputed readings.

## What was built

- `build.py` writes `foreign_corpus.csv`, one row per object. Columns:
  - id, findspot, region, shape, animal, date
  - the sequence in Wells and M77 numbers, in reading order. The other list is filled through `bridge_WM.json`; `?` means no bridge.
  - Mahadevan's published sequence, the ICIT id and the Laursen 2010 Fig. 11 number
  - n_legible, reading confidence
  - whether the reading was checked against a drawing or photo
  - new_to_us, sources, notes
- Inputs:
  - ICIT foreign sites (data/icit_texts.jsonl)
  - M77 "West Asian finds" 9801-9905. Findspots come from Mahadevan 1977 Appendix V, taken from the OCR in `experiments/old_registers/raw/mahadevan_item`.
  - Laursen 2010 Fig. 11 as transcribed in `sources/paragorth_Indus-/data/gulf_seals.csv`
  - `experiments/meluhha/foreign_objects.csv`
  - an open-literature search
- I matched records across the three corpora by hand. These identities were not in any file before:
  - 9801 = Susa cylinder ICIT 3882
  - 9811 = Umma tag 3884
  - 9821 and 9822 = Kish 1970 and 1971
  - 9832 = Gadd 2 (3897)
  - 9833 = Gadd 5 (5225)
  - 9846 = Gadd 16 (3898)
  - 9851 = Telloh tiger 3885
  - 9852 = Girsu 5222
  - 9901 = Gadd 17 (3889)
  - 9903 = the Rosen seal (Langdon 1932; Laursen no. 25, which paragorth lists as "missing")
- **New to us (4):**
  - Jalalabad cylinder, Fars, NMI 2698 (Vidale & Frenez 2021, JARCS; PDF in `raw/`). It has 3-5 signs with "man" and "twins" signs, and the reading is uncertain.
  - Knox 1994 cylinder, probably from Sistan
  - A round seal with a humped bull from Umm al-Quwain, UAE. It is reported only by a news aggregator (c. April 2026), no sequence is published, and it is unverified.
  - A Babylon round seal (a British Museum image record). It may be one of the Gadd items.
- **Known but not transcribed:** Gadd 15 (Laursen no. 20), Laursen no. 17, Qala'at al-Bahrain fragment no. 6, Tell Asmar As.31-221, and Umma TJ17 (partial: ...-803-740).

## Order flag (pre-registered: docs/prereg/foreign_corpus.md, hash in HASHES.txt, tag foreign_corpus)

- Model: the Wells class-bigram grammar from experiments/grammar, trained as in validate.py part (d).
- Reference: 1,353 cross-validated scores of native square seals, matched by length and completeness.

| id | shape | n | bits/sign | p (grammar) | p (KN bigram) |
|---|---|---|---|---|---|
| BAHRAIN-01 (Qala'at) | round | 5 | 8.38 | 0.005 | 0.005 |
| BAHRAIN-07 (Janabiyah) | round | 7 | 8.50 | 0.005 | 0.008 |
| SUSA-02 (Sb 2425) | cylinder | 8 | 8.36 | 0.011 | 0.008 |
| UNPROV-02 (Gadd 18) | round | 3 | 11.55 | 0.013 | 0.013 |
| UR-01 (Gadd 2) | round | 5 | 7.75 | 0.019 | 0.033 |
| BAHRAIN-06 (Saar) | round | 6 | 7.89 | 0.024 | 0.024 |
| GIRSU-02 (Telloh tiger) | square | 4 | 8.95 | 0.034 | 0.017 |
| UNPROV-07 (M77 9902) | seal | 5 | 7.46 | 0.038 | 0.028 |
| SALUT-01 | square, local stone | 5 | 7.34 | 0.043 | 0.024 |
| UNPROV-03 (Buchanan 1088) | round | 5 | 8.80 | 0.043 | 0.043 |

- Borderline: UR-02, UR-05, KISH-01, SUSA-01, LURISTAN-01, FAILAKA-01, FAILAKA-02, BAHRAIN-04, UNPROV-01, UNPROV-08.
- The KN-bigram check flags 13 at p < 0.05, so the result does not depend on the choice of model.
- Full table: `order_flags.csv`.

| hypothesis | verdict |
|---|---|
| Foreign texts break Indus order more often than chance (10/39 vs 5%) | supported (binomial p = 1.6e-5); fits the earlier pooled Gulf result (+1.80 bits) |
| Square seals found abroad read as ordinary Indus | mostly supported (5/7 Indus-like); the Telloh tiger and Salut are exceptions |

## Caveats and what was not checked

- **I did not look at any drawing or photo myself.** The "verified" column only repeats paragorth's check of Laursen's drawings, which covers 20 objects. Everything else is a corpus reading.
- **Reading direction is disputed** for three flagged or borderline texts:
  - SUSA-02: M77 reads it left to right; ICIT has the opposite order.
  - BAHRAIN-01 and FAILAKA-01: in Laursen's drawings the order is reversed relative to the corpus.
  - A reversed reading could explain their flags. I did not test the reversed order, because that was not pre-registered.
- **The readings disagree in places:** the end of UR-02, and every sign of UR-05 except the first.
- **M77-only texts depend on the bridge.** Texts known only from M77 (UR-07, UNPROV-07, -08, -10) were scored through the bridge, and signs with no bridge entry were scored as unknown.
- **Unprovenanced objects are a soft category.** "unknown-WA" rows (10) are placed in West Asia on the strength of a catalogue's grouping, not a findspot.
- **Sources not obtained:**
  - Parpola 1994b (the Qala'at al-Bahrain catalogue), Laursen & Steinkeller 2017, Kjaerum's catalogues and Frenez on Bat
  - harappa.com copies were not fetched (the site blocks bots); the Semantic Scholar copy returned 403.
- **Multiple comparisons:** this is one flag per text at 5%. Expect about 2 false flags among the 10.

## Next

- #4 should use the 10 flagged texts and treat the 11 borderline ones as a sensitivity set.
- Before #4 runs, someone should check the flagged readings against Laursen's drawings, Gadd 1932 and Amiet 1972 (added as a task).
- Get Parpola 1994b for the Bahrain readings.
