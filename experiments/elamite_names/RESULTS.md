# Elamite / eastern personal-name crib list for #4 (board #24, H8)

**Verdict: data.** `short_Elamite_core.csv` has **50 names** of people the Ur III scribes label as men *of* an Elamite or eastern place. Each was found in a line of the form "PN lu₂ Šušin / Šimaški / Marhaši / Anšan / Urua / Kimaš / Sabum / Hurti / Adamšah / Huhnuri". The names date to about 2100–2000 BCE, the same time as the Gulf round seals, so they are a better crib than later Elamite. The file is in H2's onomasticon format, with a dot-syllabified `syllables` column. Mean length is 3.46 syllables.

One feature matters for #4. **These names repeat a syllable far more than chance: 24% of names, against a shuffled null of 10% (95% range 2–18%).** Examples are ba.na.na, bu.ka.ka, da.da.a, zi.li.li, pa.na.na and du.ga.ga. Sumerian, Akkadian and Amorite names repeat a syllable *less* than chance (#2). Of the 9 foreign texts flagged in #1 or #22, some show sign repetition (typology q2: G2/G3 excess). So an Elamite-type crib predicts repetition where a Mesopotamian one does not. That contrast can be tested.

## Method
- Source: ORACC epsd2/admin/ur3 corpusjson (CC0), 80,181 texts, read in place from `experiments/meaning_classes_seal/raw/ur3.zip`. Nothing new was downloaded.
- Rule, fixed in `build.py` before the names were inspected: a PN on the same line as lu₂, where the lu₂ is followed by an eastern SN/GN. That gives 83 PNs. Places: Šušin 23 lines, Šimaški 13, Marhaši 11, Urua 8, Kimaš 8, Sabum 6, Anšan 5, Hurti 4, Adamšah 3, Huhnuri 2, Giša 1.
- Then `finalize.py` flags 33 of them as Mesopotamian-shaped: either already in names.csv as Sumerian or Akkadian, or containing dingir/puzur/ur/Suen/Utu/Iškur/lu/igi and similar elements. These are envoys or Akkadian-named officials of eastern towns. 50 remain in the core list.

## Caveats
- The list is **small**, which H3 wanted. It is small because ORACC lemmatises only part of the Ur III messenger texts and the rule is strict. Phrasings like "PN lu₂ kin-gi₄-a Anšan-ta" with a verb in between, and names on unlemmatised tablets, are missed.
- The shape filter is a hand-made rule. A few Akkadian-looking names are still in the core list: La-qip, Zariq, Šarum-ili, Išar-…, Ikbusum, and Sumerian Nannakugzu. Names like Banana, Dada and Babduša could be Mesopotamian too. Use `names_all.csv` (with `meso_shape`) to tighten or loosen the list.
- "Of Marhaši" (eastern Iran / Baluchistan region) is not "Elamite" in language. The column says "Elamite/eastern (by origin)". Marhaši is the region nearest to Meluhha in the cuneiform record, so it is a useful crib in any case.
- Libanašgubi (20 attestations, son of the Marhaši king) dominates the counts. Weight by distinct names, not by attestations.

## Files
`build.py`, `finalize.py`, `names_all.csv` (83 rows with places and flags), `short_Elamite_top150.csv` (63, Sum/Akk duplicates removed only), **`short_Elamite_core.csv` (50, use this)**, `stats.json`, `stats_core.json`.
