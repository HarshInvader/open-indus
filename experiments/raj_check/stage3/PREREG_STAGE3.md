# raj_check stage 3: a panel of other languages (prereg T5)

2026-11-27. Written and hashed before any stage-3 agent was run or any stage-3 contest score was seen. Known when this was written: stage 1 (T1 picture permutation p = 0.51; T2 fake seals ≤ 0; T3 object marks), stage 2 (Japanese surnames D = +134.5, 7 of 10 seeds above control), and the paper's own Akkadian (REP-3: −2) and Munda village-name (M8: +7) results.

## Why
Stage 2 showed one unrelated language with a picture-rich naming style gets 60% of Tamil's score. One language is one data point. This stage runs the paper's contest, unchanged, on three more languages, chosen before any run:

| Language | Why it is in the panel | Names | Source and licence |
|---|---|---|---|
| Sumerian | Mesopotamia, the Indus cities' trading partner; proposed in the past as the Indus language (Waddell 1925); an isolate whose names are often built from nouns | Ur III personal names, ranked by attestations | Oracc ePSD2 `epsd2/admin/ur3` `gloss-qpn.json` (CC BY-SA 3.0) |
| Egyptian | The other great early writing system of the time; rebus writing, names built from words | Personal names of the TLA lemma list (2,944) | TLA lemma list, January 2018, `aaew_wlist.json`, via pcomans/hapi PR 364 `reconciled.jsonl` (CC BY-SA 4.0) |
| Finnish | A placebo with no possible Indus link whose surnames, like Japanese ones, are built from landscape and nature words (*Mäkinen* "hill", *Virtanen* "stream") | Surnames of living citizens, ranked by holders | DVV Population Information System, `sukunimitilasto-2026-08-04-dvv.xlsx` (CC BY 4.0) |

Not in the panel, with reasons: Akkadian and Munda (run by the paper itself), Elamite and Burushaski (no open name list of the needed size found today), Sanskrit (stage 1).

Source files were extracted by `extract_sources.py` (no model involved) into `agents/names_in_*.jsonl`; sha256 of each source in `agents/sources.sha256.json`. Sumerian and Finnish: the top 1,600 by attestations or holders. Egyptian: all 2,944, shuffled once with seed 20261127 and taken in that order (the TLA list has no frequencies). Finnish double-barrelled surnames were left out at extraction.

## Building the inputs (as stage 2, per language)
1. **Translator** (blind: sees only the 171 English entries), Raj's translator prompt with only the language changed. Sumerian: words attested in Ur III or Old Babylonian Sumerian, no Akkadian loans. Egyptian: Middle Egyptian words, no foreign loans. Finnish: native Finnish words, no Swedish or other loans.
2. **Segmenter**: splits each name into its parts, each in standalone dictionary form, with origin (native, or loan from another language) and a short English gloss. Sumerian: Akkadian, Amorite and other non-Sumerian parts are loans. Egyptian: divine names are kept as native parts (they are Egyptian words, as Tamil keeps its god names); foreign parts are loans. Finnish: Swedish and other non-Finnish parts and the surname endings -nen, -la/-lä, -o and similar are marked as suffixes, as in step 3.
3. **Labeler** (sees only parts and glosses), Raj's labeler prompt and categories, unchanged. Stability set from category with Raj's `category_stability.json`.
4. **Loans** are dropped by the contest's own loan rule (category `loan`, stability 1). A name with no native part left is dropped. Names are taken in rank order until 1,125 remain, or all that remain if fewer, which is reported.
5. **Spelling.** So that the contest's sound-matching code (which knows Indo-Aryan and Tamil letters) treats every language alike, all agents write words in plain lowercase ASCII romanization, as Japanese was written in stage 2: Sumerian ŋ → g, š → sh, ḫ → h; Egyptian in the conventional Egyptological pronunciation with e inserted (nfr → nefer, ḥtp → hotep, ꜥnḫ → ankh); Finnish ä → a, ö → o, y kept.
6. **Number words** (config): Sumerian 1 dish, 2 min, 3 esh, 4 limmu, 5 ia, 6 ash, 7 imin, 12 u-min; Egyptian 1 wa, 2 senwy, 3 khemet, 4 fedu, 5 diu, 6 sisu, 7 sefekh, 12 medjsenwy; Finnish 1 yksi, 2 kaksi, 3 kolme, 4 nelja, 5 viisi, 6 kuusi, 7 seitseman, 12 kaksitoista. weights "once", punmax 0.5.
7. No list is edited after a contest run. Malformed agent output is fixed mechanically (format only) or the agent is rerun, and this is reported.

## Test
Raj's `contest.py` unchanged, seeds 0–9, real and null, for each language. D_L = mean over seeds of (real − null). Tamil D_T = 223.0 (T0).

Per language, the same rule as stage 2:
- **Fits like Tamil** (against the paper's language claim): D_L ≥ 111.5 and above its own control in at least 8 of 10 seeds.
- **Partial fit**: D_L ≥ 111.5 but fewer than 8 of 10 seeds, or D_L > 0 and at least 8 of 10 seeds.
- **No fit**: otherwise.

Panel verdict (fixed now):
- **The contest does not single out Tamil** if at least one of the three languages fits like Tamil.
- **The contest picks out Tamil within this panel** if none fits like Tamil and none, Japanese included, beats Tamil in more than 3 of 10 seeds.
- **Mixed** otherwise.

Reported for every language either way: D ± sd, seeds above control, seeds ahead of Tamil, picture options per sign, signs read, names used, and the share of name parts in the drawable categories (animal, plant, body_part, artefact, landscape, celestial).

## Agents
Nine fresh agents with no project context: per language one translator, one segmenter, one labeler. Prompts saved next to their outputs in `agents/`.

## Limits stated now
- One translator per language; no expert checker in this stage. Agent errors in Sumerian and Egyptian glosses are likely and are not corrected by hand.
- The Egyptian list is lemmas, not attestation-weighted, and spans all periods in the TLA.
- The Ur III list is from administrative texts and mixes Sumerian and Akkadian names; only Sumerian parts are kept.
- Finnish surnames are modern, as the Japanese and the paper's Munda village names are.
