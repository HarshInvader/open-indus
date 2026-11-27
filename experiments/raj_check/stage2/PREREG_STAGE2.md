# raj_check stage 2: a wrong language with a picture-rich naming style (prereg T4)

2026-11-27. Written and hashed before any agent was run or any Japanese contest score was seen. Stage 1 results were known when this was written (T1: picture permutation p = 0.51; T2: fake seals ≤ 0; T3: object marks p = 0.10, collapses on distinct texts).

## Why
Raj's contest beats Sanskrit (1.1 picture options per sign) and Akkadian (0.5). Raj notes that the Akkadian control "does not test Akkadian on equal terms of naming style". Tamil has 2.5. A fair control is a language with no proposed Indus link whose names are built from drawable things.

## Language and data
Japanese family names. Source: shuheilocale/japanese-personal-name-dataset @ 793b250 (MIT), `last_name_org.csv`, sha256 df881e4a…70b3ed, 1,999 surnames ranked by population. Modern names. Raj's Munda and village contests also used modern names.

## Building the inputs (mirrors REP-1; the prompts are Raj's own, with only the language changed; diffs saved)
1. Translator (blind: sees only the 171 English entries): `japanese_translator_prompt.txt`, from `tamil_translator_prompt.txt`. Native words (wago) attested in early Japanese literature; no Sino-Japanese loans.
2. Segmenter: `japanese_segmenter_prompt.txt` (new, since Raj's Tamil splits came from a dictionary splitter). Ranks 1–1600, parts in standalone form, origin native or sino, gloss.
3. Labeler (sees only parts and glosses): `japanese_labeler_prompt.txt`, from Raj's labeler prompt. Stability is set from category with Raj's `category_stability.json`.
4. Loans. As Tamil drops Sanskrit loans, Sino-Japanese parts get category `sino_loan` and are dropped by the contest's own loan rule (stability 1). A name with no native part left is dropped. We take names in rank order until 1,125 remain (Tamil's count). If fewer than 1,125 remain in ranks 1–1600, we use all that remain and report it.
5. Number words (config): 1 hito, 2 futa, 3 mi, 4 yo, 5 itsu, 6 mu, 7 nana, 12 to. weights "once", punmax 0.5, as in Tamil's headline config.
6. No list is edited after a contest run. If an agent output is malformed, it is fixed mechanically (format only) or the agent is rerun, and this is reported.

## Test
Raj's `contest.py` unchanged, seeds 0–9, real and null. D_J = mean over seeds of (real − null). Tamil D_T = 223.0 (T0).
Decision rule: the same bar Raj used to rule out Sanskrit ("mean below half of Tamil's"), applied the other way.
- **The contest does not single out Tamil** (against Raj's language claim): D_J ≥ D_T / 2 = 111.5 and Japanese above its control in at least 8 of 10 seeds.
- **The contest passes this control** (for Raj): D_J < 111.5, or Japanese above its control in fewer than 8 of 10 seeds.
- Reported either way: D_J ± sd, seeds above control, Japanese against Tamil seed by seed, options per sign, signs read.
Descriptive extra: Japanese picture-permutation (20 permutations), as T1.
