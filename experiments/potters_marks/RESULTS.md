# Potter's marks and the frame signs (Fable 5.2 plan 2, item 7)

## Findings first
1. **M342 (the "jar" closer) and M347 were already in use before the Mature phase, as graffiti scratched on pots.** Kenoyer (2020) shows M342 on sherds from Harappa Period 1 (Ravi, fig. 6a) and Period 2 (Kot Diji phase, fig. 6b), and the pair M342-M347 in Period 2. ICIT lists pre-Mature Harappa pottery with M342 (992.1, and 959.1 as M287-M342). Dales and Franke-Vogt report M342 as the most important sign at Balakot I. This contradicts paragorth loop 57 (S-DARK-57, "0 frame signs among 985 early marks") for these two signs. That coding read the forked-U as W706.
2. **The openers M267 and M391 have no early attestation under any definition, and the closer M211 has only one loose match.** So the frame did not arrive ready-made from pot marks. At most, one closer and one title sign had precursors.
3. **Test (a), frame vs core precursors, is INCONCLUSIVE.** Under the strict definition, 5 of 52 frame signs have an early precursor (9.6%) against 8 of 103 core signs (7.8%). Odds ratio 1.26, stratified permutation p = 0.39. The test had only 33% power to detect a doubling.
4. **Test (b), vessel restriction, is not supported, and the test is too weak to refute it.** Of 32 Sarai Khola marks with a published vessel type, 19 are on jars and 13 on bowls. No shape family is confined to one class (chi-square 5.73, permutation p = 0.23). The power to catch a family of 6 marks all on jars was 22%. Quivron (1980) states for Mehrgarh (about 850 marks) that the same marks appear "indifféremment" on goblets, cups and jars, and that "le choix des motifs n'est visiblement pas déterminé par l'usage".
5. **No named frame sign has an early occurrence with a published vessel type.** Harappa, Balakot and ICIT give no vessel type per mark. Kenoyer says that, in the Mature phase, graffiti are mostly on large storage jars. That is a general statement, not a per-sign count. **Test (c) is therefore untestable**, because no Mature corpus records vessel form per inscription.

Bottom line: M342/M347 do have pottery-graffiti ancestors, and these are post-firing, which suggests owners or users rather than potters. We cannot say whether those ancestors were tied to one vessel type. The open literature only shows that marks in general were not tied to a vessel type at Mehrgarh or Sarai Khola.

## Hypothesis table
| Test | Pre-registered rule | Result | Power | Verdict |
|---|---|---|---|---|
| (a) P1 strict | SUPPORTED if strat-perm p<0.05 and P2 frame>core | frame 5/52 vs core 8/103, OR 1.26, Fisher p 0.455, perm p 0.391, logit beta 0.24 (p 0.70) | 0.33 at 2x, 0.78 at 3x | INCONCLUSIVE |
| (a) P2 others' IDs | (condition) | frame 5/52 vs core 5/103, OR 2.09, Fisher p 0.211, perm p 0.138 | 0.23 / 0.54 | frame > core, n.s. |
| (a) P3 loose | sensitivity | frame 11/52 vs core 15/103, OR 1.57, perm p 0.173 | 0.62 / 0.96 | n.s. |
| (b) Sarai Khola jar vs bowl | SUPPORTED if perm p<0.05 and a family >=80% one class with q<0.05 | chi2 5.73, perm p 0.230; families: strokes 7/4, cross-T 1/3, V 1/3, W-N 4/1, chevron-arrow 4/1; min q 0.78 | planted all-jar family of 4/6/10: 0.11/0.22/0.45 | not supported (underpowered) |
| (c) Mature vessel association | untestable unless vessel form recorded | 0 of 636 ICIT pottery rows record vessel form | n/a | UNTESTABLE |

Bonferroni alpha for the area is 0.017. Nothing comes near it.

Hits under P1. Frame: M139, M177, M294, M342, M347. Core: M59, M134, M137, M214, M245, M287, M303, M328.
Hits under P2. Frame: M99, M169, M177, M342, M347. Core: M59, M134, M162, M287, M328.
Numerals (strokes) have precursors under every definition, as expected. They are not tested.

## Named frame signs (credited early marks, P1 / P2 / P3)
| Sign | Role | P1 | P2 | P3 | Note |
|---|---|---|---|---|---|
| M342 | closer | 7 | 8 | 11 | Harappa P1-2, Balakot I, Kalibangan lower levels (doubtful date) |
| M328 | noun (0.62) / unit | 7 | 6 | 54 | U-shape; common simple form, so it may be a coincidental match |
| M211 | closer | 0 | 0 | 1 | |
| M162 | noun | 0 | 1 | 14 | |
| M169 | closer | 0 | 1 | 2 | |
| M267 / M391 | opener | 0 | 0 | 0 | absent |
| M99 | connective | 0 | 1 | 82 | stroke pairs; ambiguous with numerals |

Early marks with a published vessel type, by M77 match (Sarai Khola and Kot Diji, any confidence):
- Chevron M134: 4 jars, 1 bowl.
- M86|M97: 3 jars.
- M87|M99: 2 jars, 3 bowls.
- M365|M328: 1 bowl and 1 lid.

None of these is a confident frame-sign match.

Mature descriptive counts (ICIT, distinct texts):
| Sign | Pre-firing pots (15 texts) | Graffiti (328) | Stamped pots (50) | Seals (2068) |
|---|---|---|---|---|
| M342 | 1 | 58 | 8 | 856 |

Openers M267/M391 appear 2 and 2 times on 15 pre-firing pot texts, and 14 and 7 times on graffiti. Full table in `tests.json`.

## Data
`marks.csv` holds 233 rows and 931 marks. The columns are shape, site, phase, approximate date, firing, published vessel type and class, part of the vessel, M77 match, confidence, match basis and citation. It is built by `build_marks.py`.

| Source | What it gives |
|---|---|
| Kenoyer, J.M. 2020, "Indus writing and graffiti" (Harappa; via Wayback copy of harappa.com) | Tables 3-4: Period 1 has 7 pre-firing and 16 post-firing marked sherds; Period 2 has 49 and 175; 1,218 marked sherds overall. Figs 6a/6b: M342. No vessel type per mark. |
| Kenoyer, Mohenjo-daro journal article (Ravi and Kot Diji marks, figs 3-4) | Ravi: 13 post-firing sherds (6 rims) and 4 pre-firing. Kot Diji: 95 sherds. Multi-sign pre-firing marks were inscribed in moulds for large bowls and jars. |
| Halim, M.A. 1972, Excavations at Sarai Khola, Pakistan Archaeology 8, Table 11 | The only catalogue with vessel type per mark (jar types VII, IX/IXA/IXB/IXE; bowl types X, XI/XIA; one lid XIIIA). |
| Khan, F.A. 1965, Excavations at Kot Diji, Pakistan Archaeology 2 | Marked rimless jar. |
| Quivron, G. 1980, "Les marques incisées sur les poteries de Mehrgarh", Paléorient 6 | About 850 marks, 147 forms, 50 categories. 80% are on the outer base. Not vessel-specific. Read as potters' or workshop marks. |
| Dales, G.F. 1974 (Balakot); Franke-Vogt, U. 2001 (cited by Kenoyer) | M342 is the key sign at Balakot I. |
| Lal, B.B. 1979 (Kalibangan) | 3 sherds with M342 from lower levels, possibly Mature. |
| ICIT (Wells), pre-Mature pottery rows, mapped through `sources/shaunmortal_indus/data/bridge_WM.json` | 992.1, 959.1, 950.1 (Harappa Periods 1-2). |

## Caveats
- **Contamination.** I coded all the matches myself, knowing the hypothesis and the roles of about 35 signs. P2 removes my judgement, and its direction agrees with P1.
- **Simple shapes.** Early marks are mostly simple: strokes, crosses, V, U, chevron. Matching them to Mahadevan signs inflates the credit for simple signs, whatever their role. The ink-tertile stratification only partly controls for this.
- **Firing.** M342's early cases are post-firing graffiti. They show the sign existed on pots, not that potters made it.
- **Unit of count.** Test (a) counts signs. Test (b) counts sherd occurrences, and several Sarai Khola occurrences may come from one pot or one deposit, so its p is if anything optimistic.
- **Deviation (Amendment A1).** After hashing, the descriptive vessel-by-match listing crashed on empty `n_marks` values. I patched it to read an empty value as 1 mark and re-hashed it (tag `potters_marks_A1`). Tests (a) and (b) are seeded, and the rerun reproduced them exactly.

## What would settle it (human access needed)
- Kenoyer and Meadow's HARP sherd database. Kenoyer's Table 3 (1,218 marked sherds) was built from records that include vessel form. This is the best single source and would make (b) testable for M342.
- Durrani, Ali and Erdosy 1995, Ancient Pakistan 10 (Rehman Dheri, more than 300 marked sherds).
- Franke-Vogt 2001 (Balakot marks).
- Lal et al. 2003, Kalibangan, MASI 98.
- Khatri and Acharya (Kunal).
- Quivron 1997 (Nausharo).
- Shinde et al. 2011 (Farmana).
- Rao (Bhirrana, Puratattva).
- Dani 1970-71, Ancient Pakistan 5 (Gumla).
- CISI vol. 3, for Mature pottery with object descriptions.

## Files
`build_marks.py`, `marks.csv`, `tests.py`, `tests.json`, `tests.log`, `results.json`. Raw downloads are in `raw/` (untrusted). Crops and contact sheets are in `work/`. The pre-registration is `docs/prereg/potters_marks.md`. Ledger rows are pm_a1, pm_a2, pm_a3, pm_b and pm_c.
