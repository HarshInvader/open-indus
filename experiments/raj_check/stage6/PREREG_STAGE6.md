# raj_check stage 6: Brahui (prereg T10)

2026-11-27. Written and hashed before any stage-6 agent or run. Known: T0–T9b and T9c V1. Suggested by a reader.

## Why Brahui
Brahui is the North Dravidian language spoken in Balochistan, the Dravidian language closest to the Indus cities today. It has no early texts (its first writing is 18th century), and its vocabulary is mostly borrowed (Balochi, Persian, Arabic, Sindhi, Pashto); native Dravidian words are a minority. So this is a weak test, and it may well be void like Old Telugu and Old Kannada. We run it because it is the geographically closest Dravidian language and readers asked.

## Inputs (built by fresh agents in Antigravity, Gemini, with no project context; prompts saved in `agents/`)
1. **Names.** About 1,400 Brahui proper names of every kind (people, tribes, clans and sections, places, rivers, hills, saints and shrines) from Bray, The Brahui Language (1909, 1934), the Baluchistan District Gazetteers (1906–07) and Census of India 1901/1911 Baluchistan tribal tables, and Elfenbein's Brahui work. Same output format as stage 4 (name, type, morphemes, gloss, source); the paper's compiler prompt with language and sources changed, nothing added.
2. **Picture words.** The 171 English picture words, translated blind to at most 2 native (Dravidian-origin) Brahui words each, by the stage-4 translator prompt with the language changed; empty if none.
3. **Part labels.** The stage-4 v2 labeler prompt, with the loan category `loan`: a word borrowed from any non-Dravidian language (Balochi, Persian, Arabic, Sindhi, Pashto, Indo-Aryan), judged by origin. A second labeler labels by meaning only (loans get their meaning category) for the sensitivity run.
4. **Checker.** A fresh Claude agent checks 50 random names and 50 random picture words (seed `20261127-brahui`) against Bray, the DEDR and the gazetteers; more than 10% wrong sends the list back once.
Number words: asiṭ, irāṭ, musiṭ (native 1–3); chār, panch, shash, haft, dwāzdah (4, 5, 6, 7, 12, loans as Brahui uses them).

## Runs and readings
Raj's `contest.py` unchanged, seeds 0–9, real and null. Main run: loans dropped. Sensitivity run: meaning labels, loans kept.
- **Void** if the solver reads fewer than 5 signs (the paper's own adequacy line).
- Otherwise: "Brahui fits the seals like the paper's Tamil" if D ≥ 111.5 with at least 8 of 10 seeds above control; "Brahui does not" if D < 111.5.
