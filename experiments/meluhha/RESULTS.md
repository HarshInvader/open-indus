# Meluhha in cuneiform: an outside anchor for the Indus script?

Code: `name_shape.py`, `goods.py` (run from the repo root with `.venv/bin/python`). Data: `catalogue.csv` (49 rows: persons, titles, places, goods) and `foreign_objects.csv` (23 Indus-type objects found in the West). Logs: `*.log`. Numbers: `results.json`. This builds on paragorth `ANCHORS.md` §2–21 (the CDLI dump of 214 tablets, Gadd 1932, Laursen 2010). Those sections are cited here, not redone.

## Conclusion first

1. **There is no anchor yet.** The cuneiform record has exactly two securely Meluhhan, non-Mesopotamian personal names: **na-na-sa₃ (also spelled Na-na-za)** and **sa₆-ma-ar**. Both belong to one household of royal bezoar-goat shepherds at Irisagrig, recorded on 4 tablets from Šu-Suen 6 to 9 (three of these tablets are new to the project). Three weaker foreign names exist: *sak-ku-ši* on the Indus-type seal BM 120573, *za-ši-ri* on a Linear Elamite Gulf seal, and *da-la-me*. Every other named Meluhhan carries a Sumerian or Akkadian name: Ur-Lamma, Ur-Igalim, Lu-sunzida, Lu-marza, Ili-ahi, Ali-ahi, Dadi, and men simply called "Meluhha".
2. **Name shape cannot pick between Meluhhan and Sumerian/Akkadian, and it says nothing about language.**
   - Indus name cores are 55% single signs, against 2% of Ur III names. Syllabic spelling of names shaped like either group is ruled out. This agrees with the typology finding that Indus cores are written with word signs.
   - Indus cores do double signs more than chance: 5.1% start with a doubled sign against 2.2% in a frequency-preserving null (p < 0.0005). But 71% of the doubled signs are four signs (M245 alone accounts for 49%), and the home pattern is "doubled sign + closer" (M59 M59 M342, M153 M153 M342). That is logographic doubling, not syllable reduplication like *na-na-sa*.
   - On initial doubling, Indus (5.1%) sits closer to Ur III names (2.6%) than to the Meluhhan point estimate (1 of 5). The Meluhhan rate, however, cannot be estimated: its 95% interval runs from 0.02 to 0.63.
3. **Goods give candidates but no support.** No commodity candidate (the tree-unit W390, the tree W405, the fish W220, the cup W700) is enriched on the 30 Indus-inscribed objects found in the West. The jar W740 is *depleted* there (5 against 11.4 expected, p = 0.007), which fits the foreign texts lacking the home title formula (context Q4).
4. **No Indus seal can be tied to a person named in cuneiform.**
   - The best case is co-occurrence only: Ur in the Sargonic period, where Gadd no. 15 (U.8685, an Indus round seal from a grave) and Lu-marza "son of Meluhha" (CUSAS 26 259, Ur, Old Akkadian) fall in the same place and period. Lu-marza has a Sumerian name, and nothing links him to that seal. I put the chance they are the same man below about 5%.
   - Tell Asmar is the only site where Indus imports and tablets come from the same houses (Akkadian houses, tablets naming Šu-Durul). No Meluhhan is named there.

## 1. Catalogue (`catalogue.csv`)

- **Persons: 23 rows.**
  - 11 are explicitly Meluhhan and named.
  - 2 are Magan rulers: Manium (Naram-Sin) and **Nadubeli, ensi₂ of Magan** (CTMMA 1 17 = P108701, Amar-Suen 4; new).
  - 2 are Dilmun rulers: Rimum and Yagli-El.
  - The rest are interpreters, envoys and seal owners.
- **Titles:** EME.BAL me-luh-ha "interpreter" (Šu-ilišu seal). For the "Meluhha ship" (ma₂ me-luh-ha, Old Akkadian Adab), a soldier, an officer (nu-banda₃) and workers. ra-gaba me-luh-ha "courier" (Lagash II).
- **Places:** the Meluhha village é-duru₅ me-luh-ha of Gu'abba, with its granary, from Šulgi 32 to Šu-Suen 9, and the Meluhha orchard of Ninmar.
- **Goods:**
  - ab-ba wood: the commonest Meluhha good in administrative texts, used for chairs and footstools at Umma, Ur, Girsu and Isin. Also new: Nisaba 33 960, a carpenter travelling for it.
  - mes wood, esi, gold dust, uruda me-luh-ha "copper", carnelian gug gi-rin.
  - Ivory zu₂ am-si, and the dar-bird of Meluhha (as figurines in the Ur workshop texts of Ibbi-Suen 15).
  - The "speckled dog" ur gun₃-a (from Marhaši), Meluhha goats and sheep, a "Meluhha stone".
  - From ETCSL: Enki and the World Order lines 124–129 and 221–232, Enki and Ninhursaĝa 49C–E, Curse of Agade 48–49.
- **New beyond the 2022 CDLI dump:**
  - P516138 (CUSAS 40/2 1354) and P516366 (CUSAS 40/2 1582).
  - UCTIS 099 (BDTNS 205179). It spells the name Na-na-za, which shows the third sign is a sibilant that varies (sa₃/za).
  - P361994 and P108701.
  - BDTNS dates Nisaba 15 0371 to Šu-Suen 8, not year 6.
- **Gaps:**
  - I did not read Laursen & Steinkeller 2017 App. 1 or Parpola, Parpola & Brunswig 1977 directly; harappa.com blocked access.
  - The CDLI search returned HTTP 500 errors.

## 2. Test 1: name shape (`name_shape.py`)

References: the 5 Meluhhan/Gulf names (2 secure); 3,155 distinct Ur III seal-legend names with determinatives dropped; 2,522 Indus name cores from the functional-reading slots (distinct texts).

| statistic | Meluhhan (n=5) | Ur III (n=3,155) | Indus cores |
|---|---|---|---|
| mean written signs | 3.0 (all exactly 3) | 3.29 | 1.70 |
| mean syllables (approx.) | 2.8 | 3.37 | — |
| one-sign names | 0 | 0.020 | **0.553** |
| initial doubling (length ≥ 2) | 0.20 (95% CI 0.02–0.63) | 0.026 | 0.051 (null 0.022, p < 0.0005) |

- **Are the Meluhhan names Ur III-shaped?**
  - All 5 have exactly 3 signs. Under Ur III lengths that has p = 0.012, but only p = 0.17 for the 2 secure names.
  - One of 5 starts with a doubled sign: p = 0.12 under Ur III (0.05 for the 2 secure names). Ur III has many such names itself (a-a-, ba-ba, da-da, na-na…).
  - A sibilant-plus-*a* sign appears in 4 of 5 names (sa, sa₆, sak, za), with p = 0.0009. I noticed this after looking, so it is **not counted**.
  - Verdict: the names are short and CV-shaped, but nothing distinguishes them from Mesopotamian names at n = 2–5.
- **Do Indus cores fit Meluhhan shapes better?** Per-core log-likelihood of Indus core lengths:
  - Meluhhan syllable counts −2.28, Meluhhan signs −2.56; Ur III signs −2.84, Ur III syllables −2.90.
  - The Meluhhan "advantage" comes entirely from Dirichlet smoothing of a 5-name sample (bootstrap range −2.54 to −2.12). The real result is that **neither** fits, because 55% of Indus cores are single signs.
  - Doubling fits Ur III's rate better (binomial log-likelihood −14 vs −106 for 0.20), but the Meluhhan rate is unknown.
- **West Asian texts:**
  - M77 West Asian finds have an adjacent repeat in 4 of 16 texts, against 0.058 at home. paragorth §8 found p = 0.023 for this, and it did not replicate in Wells.
  - Only one is *na-na-sa*-shaped (AAB): **M77 9905 M59-M59-M167**, unprovenanced. P(at least 1 AAB in 16) = 0.25 under the home rate, and its home parallels are M59 M59 M342/M12. Not diagnostic.

## 3. Test 2: goods (`goods.py`)

Thirty ICIT texts from 18 western sites, compared with home texts of the same length (20,000 draws):

| sign | observed | expected | p (enriched) |
|---|---|---|---|
| W390 tree-unit | 3 | 2.05 | 0.34 |
| W405 tree | 2 | 0.67 | 0.15 |
| W220 fish | 6 | 3.09 | 0.07 |
| W700 cup | 1 | 0.81 | 0.56 |
| W740 jar | 5 | 11.39 | depleted, p = 0.007 |

Commodity matches, all **speculative**, none supported by a context test:
- W390 ↔ ab-ba/mes timber (the Umma tag reads "of 4 tree-units"; paragorth S345–346).
- W220 ↔ Dilmun "fish-eyes" (pearls, Old Babylonian Ur).
- The bird signs ↔ the dar-bird.
- The elephant emblem ↔ ivory am-si. Emblems are not text (context Q1).

paragorth already found Lothal sealing backs null for packaging against text, apart from one elephant seal on wooden boxes.

## 4. Test 3: Indus objects in the West (`foreign_objects.csv`)

- **Dated finds:**
  - Gadd 15 (Sargonic grave, Ur).
  - BM 120573 (cuneiform *sak-ku-ši*, pre-Sargonic/Akkadian by palaeography; no context).
  - ICIT 3898 (Ur, "Dynasty III", W415-W803-W001-W328-W004-W002; date source unknown).
  - U.16220 (cylinder from the fill of the Šulgi mausoleum).
  - The Kish seals ("Akkadian").
  - The Tell Asmar Akkadian houses.
  - Nippur (Kassite heirloom).
  - The Susa seals ("late 3rd millennium"; the same site has Old Akkadian MDP 14 Meluhha boat rations).
- **Named Meluhhans by place and period:**
  - Girsu, Ur III: Ur-Lamma and Ur-Igalim. The two Girsu Indus seals are undated.
  - Ur, Old Akkadian: Lu-marza. This is the only overlap with a dated seal.
  - Irisagrig, Ur III: Nanasa and Samar. No Indus seal is known from there (the site was looted, not excavated).
  - Adab, Old Akkadian: crews of the Meluhha ship. No Indus seal is known from there.
- **Kish 240-643** recurs at Harappa (861-2-240-643-740) and Mohenjo-daro (240-643-740). It is the one Indus name-core found in Mesopotamia that is also attested at home, but no Kish text names a Meluhhan.
- **Strength:** no match. Ur–Lu-marza is a weak co-occurrence (P(same person) ≲ 0.05).

## 5. The 3 best anchor routes and how to verify each

1. **Ur-Lamma dumu me-luh-ha's sealed receipts (Gu'abba, Šulgi 34 to Amar-Suen 6).** Nin-mar accounts (OTR 242, UDT 64, PPAC 5 0612) cite "kišib Ur-Lamma dumu me-luh-ha", so documents sealed by a named Meluhhan existed. I checked OTR 242 on CDLI: it has no impression transliterated.
   - Verify: find the actual sealed receipts of the Gu'abba granary archive (BM, Istanbul, Louvre; BDTNS search for the seal legend "ur-{d}lamma dumu me-luh-ha"), photograph the impressions, and check for Indus, Gulf or stamp-seal imagery or signs.
   - Success = a cuneiform name on the same object as Indus signs.
   - Odds: low, but this is the one place where a named Meluhhan's seal impression must physically exist.
2. **The Irisagrig household (Nanasa, Samar).**
   - (a) Collate the seal impression on CUSAS 40/2 1582 (P516366; CDLI calls it illegible) and on the other three tablets. The one on CUSAS 40/2 1354 is a scribe's seal ("dub-sar dumu …"), so it does not count.
   - (b) Pre-register for new finds: if Meluhhans spelled names by sound, Gulf/round seals will show AAB cores (X-X-Y, Y ≠ the jar) above the home rate of 1.8%. This is falsifiable on CISI 3.4 and Bahrain/Failaka finds.
   - Success = an AAB core on a round seal from a Gulf or Ur III context. That would still be only a shape match unless (a) succeeds.
3. **BM 120573 (*sak-ku-ši*) and the Sargonic houses at Ur and Tell Asmar.**
   - Re-collate BM 120573 (RTI imaging) to fix the reading (*sak-ku-ši* or *ka-lu-ši*).
   - Search Sargonic Ur (CUSAS 26, UET 2 supplements) and the Tell Asmar Akkadian-house tablets (MAD 1) for that name and for any "lu₂/dumu me-luh-ha".
   - Success = the owner of an Indus-type seal named in a dated archive. That gives the phonology of one Meluhhan name tied to a known seal, but still no Indus sign value.

## Hypotheses tested

| hypothesis | result | verdict |
|---|---|---|
| Meluhhan names differ in shape from Ur III names | p = 0.17 (secure, length); p = 0.05–0.12 (doubling) | inconclusive (n = 2–5) |
| Indus cores are syllabic spellings of Meluhhan-shaped names | 55% one-sign cores vs 0% | refuted |
| Indus doubling = Meluhhan-style reduplication | excess is real but concentrated in 4 signs, home pattern XX+closer | not supported |
| Commodity signs are enriched abroad | 0 of 4 enriched; jar depleted | refuted at this n |
| An Indus seal abroad can be tied to a named Meluhhan | best: Ur Sargonic co-occurrence | no anchor (weak) |

Tests run: 9 formal (name shape 4, goods 5). The only result below 0.01 is jar depletion (expected from context Q4). The one smaller p-value (the sibilant pattern) is post hoc and not counted.

## Next experiments
- Do the verification steps in §5. All three need collation or images, not computation.
- Get Laursen & Steinkeller 2017 App. 1 and Vermaak 2008 in full for any names missed.
- Freeze the AAB-on-round-seals prediction in `docs/prereg/` before CISI 3.4.
