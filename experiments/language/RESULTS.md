# Language hypotheses: results (historical-linguistics tester, 2026-11-14)

## Conclusion first

1. **Yajnadevam's Sanskrit key gives no evidence for Sanskrit.** His readings depend on about 1.3 free choices per sign. His key makes dictionary words only slightly better than the same values shuffled across signs (z = 1.0, p = 0.15 with his own phonetic latitude; z = 1.45, p = 0.04 without it). Keys fitted the same way to random sign sequences make far longer Sanskrit words (about 4.4 consonants per word against his 3.0). In a planted-Sanskrit control, the true key scored below keys fitted to noise. So this way of scoring cannot pick out a correct key.
2. **Parpola's numeral + fish asterisms: one of the three predictions holds, one fails clearly, one is unclear.** "6 + fish" (aṟu-mīn, Pleiades) is a real fixed compound: 12 of 28 six-stroke tokens are followed by fish, against a base rate of 13% (p = 1e-4), and the held-out texts agree (4 of 7). "7 + fish" (ēḻu-mīn, Ursa Major) is *avoided*: 1 of 60 tokens, p(depletion) = 0.0025. "3 + fish" is raised in dev but does not replicate on held-out. The marked fish signs share the plain fish's slots and take numerals far less often (2.9% vs 13%, replicated). That fits "compound names built on mīn", but it fits any fish-class word family just as well. None of this tells us the language.
3. **Corpus statistics cannot pick the language.** In simulations, a classifier separates seven planted languages well: 94–96% within one simulator design and 81% when trained on four designs and tested on a fifth (chance 14%). It still fails on real text. Real Latin, written in the same simulated script, is classed as Munda (8 of 10 random-forest runs, never as Indo-Aryan). The Indus label flips between Indo-Aryan and Munda depending on simulator choices we cannot know. **Key result: typological fingerprinting has no external validity here, so the statistics cannot identify the language.**
4. **The firmest constraints come from outside the script, and they rule things out rather than in.** Meluhhan was not Sumerian or Akkadian (the Šu-ilišu interpreter seal). Vedic Sanskrit as the Mature Harappan language is ruled out by chronology and ancient DNA (no steppe ancestry in Harappan-cline individuals). Proto-Munda is strained by when Austroasiatic reached South Asia. Dravidian, a lost isolate (including a Burushaski-like one), or several languages at once all remain open.

All counts below use distinct texts (`distinct()`), break-free runs. Number of formal tests run: A1 4 (permutation), A2 22 (P1: 2 fish sets x 3 splits; P2: 10 signs; P3: 2; P4: 1; P5: 3), B3 power runs 6 + 5 binary LOSO + 3 real controls. Bonferroni over the 26 A1+A2 tests gives alpha 0.002. The 6+fish result (p = 1e-4) and the 7+fish depletion (p = 0.0025, borderline) are the only A2 results near that line, and the 6+fish result replicates on held-out data.

---

## Part A1: Yajnadevam's Sanskrit key (xlits.csv + `sanskrit` column)

Prior work, read as data: `Equationist/indusscript-decipherment-stats` reports a+ā = 95% of vowels in his readings, against 60–68% in Vedic and epigraphic Sanskrit (seal legends 66%). `jplew/icv-test` is an empty repository (no branches; checked 2026-11-14). paragorth `RESULTS.md` found his key at z = 0.02 (full string) and z = 2.05 (skeleton) against fake lexicons, without modelling his phonetic latitude. Our version models that latitude explicitly, uses frequency-stratified permutations, and adds fitted-key and planted-answer nulls.

Reading order check: the ICIT `text` field reversed gives his readings (`+410-017+` → hara, `+031-705-167+` → vanAH). That reversed order is also our corpus reading order.

### A1a. Free choices per reading (`a1_free_choices.py`, `out/a1_free_choices.json`)
1,648 own readings (not `ref:`) with every sign keyed; mean 4.73 signs each.

| choice | per reading | note |
|---|---|---|
| vowels supplied | 4.10 | 95.3% are a/ā (real Sanskrit 60–68%) |
| word breaks | 0.96 | anywhere, also inside one sign's value |
| consonant swapped from key value | 0.88 | s→h 354, s→ś 200, n→m 183, n→ṇ 156, d→dh 85, b→bh 78, n→ñ 74, t→th 50, s→ṣ 46 |
| consonant inserted / dropped | 0.11 / 0.08 | |
| anusvara / visarga added | 0.12 | |

Only 32.5% of readings use the key consonants unchanged. Counting each vowel as at least one binary choice, a reading needs at least 1.32 choices per sign. 98.8% of his word types are Monier-Williams stems or stem + ending (`a1_reading_words.py`). He is a careful Sanskritist, but with this much freedom, making real words is easy.

### A1b. Key vs null keys (`a1_key_null.py`, `out/a1_key_null*.json`)
- Corpus: 2,962 distinct keyed ICIT runs (≥2 signs).
- Lexicon: 194,083 MW headwords (Cologne `hwnorm1/sanhw1`, entries tagged MW), plus the consonantal endings -m, -s/-ḥ, -sy, -t, -n.
- Matcher: vowels free; each key consonant may be any member of the class he actually uses (s:{s ś ṣ h ḥ}, n:{n ṅ ṇ ñ m ṃ}, d:{d dh ḍ ḍh}, t:{t th ṭ ṭh}, b/k/c/j/p ± aspiration). "Strict" mode drops these classes.
- Score: CPW = consonants per word in the fewest-word segmentation of each text into lexicon words. Every consonant alone is some word, so every text can be segmented; CPW measures how long the words can get.

| key | generous CPW | strict CPW |
|---|---|---|
| Yajnadevam | **3.022** | **3.017** |
| N1: same values permuted within frequency bins (200) | 2.929 ± 0.094 → z = 1.00, p = 0.15 | 2.906 ± 0.077 → z = 1.45, p = 0.040 |
| N2: key fitted by value swaps, real corpus (4 runs) | 4.39–4.50 | 3.87–3.97 |
| N2: key fitted to a random unigram corpus (same sign frequencies and lengths) | 4.38–4.53 | 3.89–4.00 |
| N2: key fitted to a bigram-Markov corpus | 4.36–4.45 | 3.87–3.97 |
| Planted control: true key on planted Sanskrit (RV names/epithets) | 3.16–3.17 | 3.00–3.03 |
| Planted control: key fitted to planted Sanskrit | 3.90–3.96 | 3.65–3.69 |

How to read the table:
- His key beats its own permutations by at most 1.5 SD.
- His key scores 3.02 on the real corpus and 2.94–2.99 on random corpora. That 0.05 edge is what fitting to this corpus would give.
- Fitting to pure noise gives far "better" Sanskrit, and fitting does no better on the real corpus than on noise.
- The planted-answer control fails: the TRUE key on true Sanskrit (3.16) scores below keys fitted to noise (4.4). Lexical-match rate under free vowels and broad consonant classes therefore cannot certify a key; Yajnadevam's argument rests on exactly this kind of rate.

Caveats: we used MW stems, not his full inflection engine. Adding inflection would raise every key's score, not his alone. We could not hold out texts, because he fitted to the whole corpus.

Falsifier: a key that is fixed BEFORE it sees new texts (new excavations, or the held-out sites) and reads them with fewer than about 0.3 free choices per sign, at a rate above keys fitted to noise.

## Part A2: Parpola and Mahadevan's Dravidian readings (`a2_parpola.py`; predictions frozen first in `a2_predictions.json`)

Sign sets: short numerals (M97/98 = 1, M102 = 3, M104/105 = 4, M106/107 = 5, M108/109 = 6, M110–112 = 7, M114 = 8, M115–117 = 9, M121 = 12). M103 is excluded (bound to M403, shaunmortal F7), and so is M99/100 (connective, F7). Plain fish = M59. Marked fish = M60, M65–M75.

| claim | prediction (frozen) | observed (all / held-out) | verdict |
|---|---|---|---|
| P1a 6 + fish = aṟu-mīn (Pleiades) | P(fish \| 6) above other numerals | 12/28 = 43% vs pooled 13%, p = 1e-4; held-out 4/7, p = 0.002. All are **M109** (two-tier 3-over-3) + M59; one-row six M108 never takes a fish (0/3) | **supported** as a fixed compound (meaning untested) |
| P1b 7 + fish = ēḻu-mīn (Ursa Major) | P(fish \| 7) raised | 1/60 = 1.7%, **depleted** (binomial p = 0.0025); held-out 0/13. The 7-sign M112 goes with M194/M197 (copper tablets, F7) and M342 | **refuted** |
| P1c 3 + fish = mum-mīn | raised | plain fish 16/93 = 17% vs 8.6%, p = 0.005 (dev 14/71); held-out 2/22, n.s. | inconclusive |
| P1 joint statistic (6,7 vs non-asterism values) | positive | fish family +0.04, perm p = 0.18; plain fish +0.11, p = 0.002 (carried by 6 alone) | mixed |
| P2 marked fish = compounds sharing fish's slot | neighbour similarity to M59 above frequency-matched signs | M67, M70, M72 at the 100th percentile, M60 97th, M65 88th (all texts); held-out: M60 100th, others 51st–79th | supported (also expected if they are allographs, shaunmortal M3) |
| P3 different marks = different words, not allographs | plain + marked co-occur at least at chance | same-text 66 vs 69.7 expected (no avoidance); adjacent 48 vs 31.1, p = 0.002 (dev); held-out 6 vs 6.2 | weakly supported (adjacency does not replicate) |
| P4 marked fish = names of single heavenly bodies (our derivation) | numerals precede marked fish less often | 2.9% (20/681) vs 13% (39/301), Fisher p < 1e-4; held-out 1.9% vs 12.1%, p = 0.003 | supported, but not specific to Dravidian |
| P5 Mahadevan: jar M342 = masculine suffix -an | (a) final, (b) left-diverse, (c) alternates in a paradigm | (a) 72.6% final vs 22.6% by chance; (b) 35.7 distinct left neighbours per 60 tokens vs 23.6 for frequent signs (94th percentile; dev and held-out 100th); (c) alternates in only 49 of 688 stems, mostly with M12/M15 | (a, b) supported; (c) weak. Any closing word (title, genitive, "seal of") predicts the same, so this does not distinguish Dravidian |

So the asterism programme predicts one compound that exists (6+fish), one that does not (7+fish), and one that does not replicate. A fixed "6 + fish" term is just as compatible with a non-astronomical title or clan name in any language. Mahadevan's jar behaves like a closer, which every hypothesis expects.

## Part B3: Typological fingerprinting with power analysis (`b3_sim.py`, `b3_classify.py`, `b3_robust.py`, `b3_realcontrols.py`)

**Simulated corpora.** 2,300 distinct legends each, with the length distribution resampled to Indus. Each legend is a name plus optional title, kin phrase and case ending. Classes:
- **DRA**: PDr reconstructions (Wiktionary 381) + Malayalam/Kannada lexicons; strictly suffixing (-an/-ar/-i, gen. -a/-in, dat. -kku), modifier-head, makan "son".
- **IA**: RV names and epithets (Equationist list) + 8k MW headwords; -sya/-ḥ, name prefixes su-/pra-/vi-…, vṛddhi patronymics, putra, śrī.
- **MUN**: Santali lexicon + Proto-Austroasiatic; prefixes ka-/ki-/ma-, infix -n-, -ren/-ak', hopon.
- **BUR**: Burushaski Wiktionary lemmas, Latin plus a crude transliteration from Urdu script; possessor prefixes i-/mu-/a-/gu- on kin terms, -e/-mo.
- **ELA**: Elamite lexicon; class suffixes with agreement, šak "son", head-first.
- **SUM**: real CDLI Ur III seal legends (6,381) with names resampled.
- **NONLING**: a slot grammar of emblems.

**Script.** Simulated logo-syllabic writing: 80–450 logograms for the commonest morphemes, the rest in CV syllabograms, with random coda spelling, length marking and homophony. Nuisance rates are redrawn for every corpus.

**Features.** 19 statistics that can also be computed on Indus: suffix-vs-prefix alternation asymmetry (1- and 2-sign), first- and last-sign entropy, position of the top-1 and top-10 signs, top-5 initial and final share, left/right branching entropy, conditional entropy, adjacent and within-text repeats, Zipf slope, bigram type ratio. Inventory-size and length statistics were dropped from the classifier because the script and genre drive them.

**Power.**

| test | accuracy (chance 0.143) |
|---|---|
| within spec A, 5-fold CV, RF / LR | 0.941 / 0.957 |
| leave-one-spec-out (A base; B other title order, endings, no vṛddhi; C genre opener for all; D scribes omit affixes; E equal name-ending rates), RF | A 0.975, B 0.829, **C 0.621**, D 0.779, E 0.854 (LR: 0.975, 0.857, 0.586, 0.786, 0.893) |
| binary DRA vs IA, LOSO | 1.00, 1.00, **0.66**, 0.93, 0.79 |
| binary language vs NONLING, A→B | 0.989 |

Under mis-specification, IA and MUN soak up errors: 26 DRA, 36 ELA and 18 BUR corpora were called IA when their spec was held out, and 38 BUR corpora were called MUN.

**External-validity controls (real text, known language).** These decide the question.

| corpus | expected | RF says | LR says |
|---|---|---|---|
| Latin EDH inscriptions ≤5 words, in the simulated script (10 script draws) | IA (IE, suffixing) | **MUN 8, NONLING 2, IA 0** (P(IA) = 0.15) | MUN 5, IA 4, ELA 1 |
| Linear B lines (real Mycenaean Greek syllabary) | IA | **MUN** (0.52) | IA (0.99) |
| Ur III real legends | SUM | SUM 10/10 | SUM 10/10 (not independent: SUM was simulated from these) |

**Indus (reported only to show the instability).**
- Inside the simulated space: kNN distance at the 84th percentile of simulated corpora (spec A); the most unusual feature is the very final top sign (jar), z = +1.4.
- Pooled A–E model: M77 IA 0.44 / NONLING 0.18 / ELA 0.14 / MUN 0.09 / DRA 0.08 (RF). LR gives IA 0.49 / NONLING 0.31 / BUR 0.17; ICIT LR gives IA 0.98.
- Spec E alone: M77 RF **MUN 0.43 vs IA 0.39**.
- Text bootstrap on spec A (30 resamples of Indus texts): IA in 30/30 (P = 0.43, 90% interval 0.36–0.54). In the first run of spec A, which differed only in its random stream, the same bootstrap gave NONLING in 30/30. So even the bootstrap answer depends on which random set of simulated corpora the model saw.

Why Indus lands on IA/MUN: Indus has frequent signs at both ends of the text, a common initial set plus the jar finally (first-minus-last entropy 0.20, top-10 mean position 0.45). Our DRA and ELA generators put the frequent elements only at the end. Whether a seal genre has fixed openers is a scribal or genre convention, not a fact about the language, and the real-Latin control shows the classifier mistakes such conventions for language type.

Verdict: power exists only inside the simulator. (Numbers are from the final regenerated run; an earlier run with a different random stream gave the same picture: LOSO 0.80, Latin → MUN 10/10.) On real languages it fails at exactly the distinction (IA vs MUN, suffixing vs prefixing) that the Indus label depends on, so **no posterior over languages is supported**. The one robust-looking pattern is that strictly-suffixing-with-written-endings designs (DRA, ELA) score low on Indus in every spec (P(DRA) ≤ 0.18, P(ELA) ≤ 0.29 across all models and specs). We do not count even this, because a Dravidian language written logographically with genre openers was within the spec space (C/D) and still lost. That says "Indus is not written like our DRA generator", not "Indus is not Dravidian".

## Part B4: Constraints from outside the script

| source | what it shows | constrains |
|---|---|---|
| Šu-ilišu cylinder seal, "interpreter of Meluhha" (EME.BAL me-luh-ha), Akkad period, Louvre AO 22310 | Meluhhan needed an interpreter | Not Akkadian or Sumerian (strong) |
| 214 CDLI tablets naming Meluhha (paragorth `cdli-meluhha-attestations.json`): 86 from the 3rd millennium (Old Akkadian 17, Lagash II 10, Ur III 57) | goods (carnelian gug gi-rin, ab-ba and mes wood, ivory, gold, copper, the dar bird), ships, the Meluhha village é-duru5 me-luh-ha (Guabba, Vermaak 2008) | trade only; the goods are named with Sumerian words |
| Named Meluhhans | almost all Sumerian or Akkadian names (Ur-Lamma dumu me-luh-ha, ~15 tablets; Lu-sunzida; Ur-Igalim; Lu-marza). The only foreign-looking names are na-na-sa₃ /nanasa/ and sa₆-ma-ar /samar/ (Nisaba 15 0371, Irisagrig, Šu-Suen 6; paragorth ANCHORS.md), plus possibly sak-ku-ši on Indus-type seal BM 120573 | too few and too short; CV-shaped and reduplicated names fit Dravidian, Munda and isolates alike: **no constraint on family** |
| Proposed loanwords (Sum. ilu / Akk. ellu "sesame oil" ~ Dr. eḷ/eḷḷu vs Witzel's Para-Munda *jar-tila*; Meluhha < Dr. *mel-akam (Southworth) or other) | each has competing etymologies | none secure (weak) |
| Rigvedic substrate (Kuiper 1991: ~380 non-IA words; Witzel 1999) | earliest RV (Punjab) loans look prefixing ("Para-Munda", ka-/ki-); Dravidian loans appear in the middle and late RV and further south and east; Masica's "Language X" in agricultural vocabulary | Punjab c. 1500 BCE had a non-Dravidian substrate; says little about Sindh/Gujarat 2500 BCE (moderate) |
| PDr agricultural vocabulary (Southworth 2005; Fuller 2007) | reconstructible PDr crop terms match the South Deccan Neolithic (millets, pulses), not the Harappan wheat-barley package | against PDr = the language of the whole Harappan core (moderate; Dravidian could have been one language among several) |
| Brahui (N. Dravidian, Balochistan) | relic or later migrant (Elfenbein 1987: no Old Iranian loans → arrived ~1000 CE) | weak either way |
| aDNA: Shinde et al. 2019 (Rakhigarhi I6113), Narasimhan et al. 2019 | Harappan-cline people = Iranian-related (split from Zagros before farming) + AASI, **no steppe ancestry**; steppe ancestry enters South Asia 2000–1500 BCE; the Harappan cline is the main source of later ASI (South Indian) ancestry | Vedic Sanskrit as the Mature Harappan language is very unlikely (strong). Fits a Dravidian origin in the Harappan cline (compatible, not proof). Weakens Elamo-Dravidian as a farmer migration from the Zagros |
| Austroasiatic chronology (Sidwell & Rau 2015; aDNA admixture dates ~2000–4000 years ago) | Munda reached eastern India late | Proto-Munda in the Indus by 2600 BCE strained; a western "Para-Munda" remains hypothetical (moderate) |
| Elamo-Dravidian (McAlpin 1974/1981) | lexical comparisons not accepted (Krishnamurti 2003; Blažek) | unsupported as a family; Elamite as the Indus language has no specific support |

## Hypotheses table

| hypothesis | test | prediction | observed | verdict | confidence |
|---|---|---|---|---|---|
| Yajnadevam key reads Sanskrit | permuted-key null, his latitude | key ≫ permutations | z = 1.0 (p = 0.15); strict z = 1.45 (p = 0.04) | refuted as evidence | high |
| Yajnadevam key is non-trivially fitted | fitted-to-noise null | noise-fitted keys ≪ his | noise-fitted CPW 4.4 vs his 3.0; true planted key 3.2 | refuted (method cannot discriminate) | high |
| Readings are constrained by the key | free-choice audit | few choices | 1.32 choices/sign; 95% a-vowels; 67.5% of readings alter key consonants | refuted | high |
| 6 fish = aṟu-mīn | numeral x fish enrichment | 6+fish ≫ base | 43% vs 13%, p = 1e-4, held-out 4/7 | supported (as a compound; meaning untested) | medium |
| 7 fish = ēḻu-mīn | same | 7+fish ≫ base | 1/60, depleted p = 0.0025 | refuted | medium-high |
| 3 fish = mum-mīn | same | enriched | dev yes, held-out no | inconclusive | low |
| marked fish = compounds of mīn | slot similarity; numeral rate | same slot; fewer numerals | yes (97–100th percentile; 2.9% vs 13%) | supported, not diagnostic of language | medium |
| jar = Dravidian -an | final position, left diversity, paradigm | final, diverse, alternating | final 73%, diversity 94–100th percentile, alternation weak | consistent; not diagnostic | low |
| Proto-Dravidian | typology classifier + external constraints | DRA-like statistics; fits outside facts | classifier P(DRA) ≤ 0.18 but the classifier fails real controls; aDNA compatible; agri-vocabulary partly against | inconclusive | — |
| Vedic / Old Indo-Aryan | classifier + chronology + aDNA | IA statistics; IA presence by 2600 BCE | classifier argmax IA in most specs, but Latin → MUN shows no validity; no steppe ancestry in the Harappan cline | refuted on external grounds; classifier result void | high (external) |
| Munda / Para-Munda | classifier + chronology | MUN statistics; AA presence by 2600 BCE | MUN ties IA under spec E; AA arrival dated late; RV Punjab substrate prefixing | inconclusive (chronology against Proto-Munda proper) | low |
| Burushaski-type isolate | classifier | BUR statistics | P(BUR) 0.01–0.42 | inconclusive | — |
| Elamite / Elamo-Dravidian | classifier + literature | ELA statistics | P(ELA) ≤ 0.29; family link unsupported | inconclusive, unsupported | low |
| Sumerian-type | classifier + interpreter seal | SUM statistics | P(SUM) ≤ 0.08; interpreter needed | refuted for Sumerian itself | high |
| non-linguistic | classifier (language vs NONLING binary 0.99 within sim) | NONLING statistics | P(NONLING) 0.01–0.39 depending on model; one crude NONLING design only | inconclusive | low |
| Corpus typology can identify the language | LOSO power + real-language controls | high power that transfers to real languages | 81% LOSO, but Latin → MUN, never IA | **refuted: statistics cannot pick the language** | high |

## Files
- `yj_common.py`, `a1_free_choices.py`, `a1_key_null.py` (`--strict`), `a1_reading_words.py`: Part A1
- `a2_predictions.json` (frozen first), `a2_parpola.py`: Part A2
- `fetch_vocab.py` (Wiktionary lemma lists → `ext/wikt/`), `b3_sim.py` (`--alt`, `--opener`, `--underspell`, `--sym`), `b3_classify.py`, `b3_transfer.py`, `b3_robust.py`, `b3_realcontrols.py`: Part B3
- `out/*.json`: all numbers; `results.json`: key results
- External data (untrusted, data only): `ext/skt/sanhw1.txt` → `ext/skt/mw_headwords.txt` (Cologne), `ext/eqstats/` (Equationist RV lists), `ext/wikt/`. Lexicons, Ur III legends, Latin EDH and Linear B are read from `sources/paragorth_Indus-/data` (data only).

## Next experiments
1. Run a real-language external-validity battery before any typology claim: add real Tamil-Brahmi, Prakrit and Old Tamil inscription corpora, plus Sanskrit seal legends (the DHARMA corpus used by Equationist), each written in the simulated script. If no real corpus is classified correctly, stop using typology classifiers.
2. Pre-register 6+fish (M109 + M59) as a fixed term on the forthcoming new texts (CISI 3.4, Rakhigarhi). Prediction: ≥30% of new two-tier-6 tokens are followed by M59, and 7-stroke signs are not.
3. Test any phonetic key only on texts released after the key is frozen, scored against keys fitted to noise (the A1 design).
4. Compare the 214 Meluhha attestations with the Indus "abroad" formulae (paragorth ANCHORS 415-803) if a sealed tablet naming a Meluhhan ever appears.
