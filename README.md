# Indus script: a reproducible decipherment attempt

**Status (2026-11-14): partial structural and functional decipherment; no phonetic reading, and the language is not identified.** We also show, with planted-answer experiments, *why* no phonetic reading can currently be defended, and what evidence would change that.

**Claim ladder** (what "partial decipherment" can defensibly mean here, following how Proto-Elamite was partly read):

- **L0 structure:** done.
- **L1 function** of sign classes: largely done.
- **L2 semantic field**, anchored by a non-textual covariate on held-out data: open.
- **L3 denotation**, tying one sign to one referent by depiction, arithmetic or physical measure: open.
- **L4 phonetic value:** unreachable without a bilingual. The leads that need museum imaging are in `docs/HUMAN_LEADS.md`.

The target is 3-5 L2/L3 anchors plus a full numeral grammar. Two more outputs support it:

- a record of every closed route and its power (`docs/RESEARCH_STATE.md`);
- a hash-sealed prediction registry for future finds (`docs/prereg/`).

## What we can defend

Ranked by strength after an independent red-team reimplementation, a re-test on a held-out split with zero near-copy leakage (`experiments/revalidation/`), and a project-wide multiple-testing audit over about 14,100 tests (`experiments/ledger/`, `docs/test_ledger.csv`). q = Benjamini-Hochberg across all tests unless noted.

| # | Finding | Key numbers | Where |
|---|---|---|---|
| 1 | **Sign order is grammatical, not positional.** Real order beats every permutation of its own signs far above chance, and still does with the jar, M176, M267, M391 and M99 deleted. | clean held-out: 40% of 321 runs vs 5.7% chance; q~8e-72 | structure, redteam |
| 2 | **The script is logo-syllabic.** About 400 signs (about 565 with unseen ones; 95% CI 508-658). At matched size the frequency profile sits with Proto-Elamite and Sumerian, far from Linear B or an alphabet. | 120 signs cover 90% of tokens (Linear B 63, Latin 14). Descriptive comparison, not a hypothesis test | structure |
| 3 | **Corner ticks on a fish sign move it to the closing slot** (M60/66/68/71/73 vs M59/65/67/70/72): a modifier inside a sign with a grammatical effect. | ICIT native: final in 40 of 73 vs 26% expected, p=1e-7; clean held-out 11/19 final vs 7% for plain fish, p=0.004 (q=0.03 hierarchical; q=0.54 across all tests) | novel_methods, redteam |
| 4 | **Gulf round seals break Indus sign order**; square Indus seals found abroad do not. Fits Indus signs used for another language (Parpola), but pseudo-writing is not excluded. | +2.17 bits/sign (95% CI 1.63-2.70); permutation percentile 0.53 vs 0.87-1.00 at every Indus site; q=0.005 over confirmatory tests, 0.02-0.09 across all (varies with unfixed hash seed; see docs/REPRO_REPORT.md) | context, redteam |
| 5 | **Two-tier six + fish (M109 M59) is a fixed expression.** Parpola's "7 + fish = Ursa Major" has essentially no support (1 text). | 12 of 25; Wells 13 of 33 incl. Nausharo; clean held-out 7 of 10 vs 3% base; q~6e-8 | language, redteam |
| 6 | **Each object type has its own vocabulary** (seal, tablet, copper tablet, rod, pottery). | clean held-out AUC: copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67 (all above permutation 95th pct 0.55-0.61) | context, redteam |
| 7 | **Left-to-right texts are real reversals.** | 31 of 34 copy-free lines, q=6e-6. (The jar-closes-both-directions count of 33 vs 3 included copies; copy-free it is 5 vs 0, p=0.03, which does not survive correction.) | structure, redteam |
| 8 | *(exploratory)* **Copper tablets come in about 18-64 fixed text + picture types**; a one-sign face can stand in for the picture, consistently within a legend. Blind matching shows the sign does not depict the picture: it is a type emblem. | same legend -> same sign face 8/8, p=1e-4 (all-data test, not held out); blind match 5/24 vs 3.3 chance | context, logograms, iconography |
| 9 | **Functional reading of every text** (see also docs/GRAMMAR.md, where only 4 classes - opener, connective, medial, closer - are stable under both sign lists): 11 roles (opener, connective, two numeral classes, unit, fish-class noun, ticked-fish closer, noun, title, closer, post-closer clitic). Parses 76% of unseen texts vs 44% for shuffles (v2), and 77% at sites absent from M77 incl. Dholavira. This shows positional classes exist; whether these specific 11 roles are right is weakly supported (p=0.013, q=0.085). | `experiments/functional_reading/readings.csv`, `lexicon.csv` | functional_reading |
| 10 | **Name cores are one or two word-signs, not syllabic spellings.** ('Name core' = the non-frame part of a seal text; cycle 7-10 tests did not show these are personal names: novelty sits in two slots, not one name slot.) 34% of cores are a single sign, and 80% of signs in longer cores also stand alone as whole names (syllabic name systems: at most 14% / 11%). Recurring sign pairs keep one fixed order (91% of tokens; held-out 115/138 follow dev order, p=3e-16): lexicalised pairs, with no general head-direction rule. A Sumerian-type head-initial profile is ruled out. | typology prereg 4/5 passed (formal verdict inconclusive); core_semantics prereg 8/9 passed | typology, core_semantics |
| 11 | **The fish family (M59, M65, M67, M70, M72, M75) is a lexical class.** It substitutes as a set, forms more compounds than frequency predicts, compounds with itself, and keeps a stable partner set (M53, M387, M343, M171, M389). Parpola's "fish = deity name" is not supported: it failed held-out, and fish pairing with fish argues against it. | held-out p=0.0002-0.0004 | core_semantics |

**Correction to #4 (2026-11-17, team board tasks #22 and #23).** The control behind "square Indus seals found abroad do not" / "not a format effect" used a group labelled "home round seals" that was 97% rectangular (a label error in `glib.icit_register`). With the label fixed, the 8 true round and cylinder seals found in the Indus region break Indus sign order as much as the Gulf ones (order component +1.96 bits/sign above home seals, Holm p=4e-4; foreign vs home round seals +0.11, p=0.68, power 0.99). 3 of the 8 carry the Gulf-type short-horned bull (4% of home seals). So the off-order texts belong to **round Gulf-type seals as a type, wherever found**, not to seals found abroad as such. The Gulf numbers in #4 are unchanged; the reading "another language" is still possible but now has no home control. n=8. A second red team (#25) passed with a null matched on rare-sign load: order excess +1.64 bits/sign (Holm p=3e-4; rare signs explain about 14% of the earlier +1.92), stable under leave-one-out, and foreign vs home round +0.11 (p=0.66). Two limits: the order is weak, not absent (6 of 8 texts still beat most shuffles of their own signs; mean shuffle percentile 0.38 vs 0.10 for ordinary seals), and only 3 of the 8 are confirmed round in a printed excavation register, the other 5 only by ICIT's type code. See `experiments/round_label_audit/`, `experiments/redteam_round_format/`, `experiments/redteam_round_order/`.

**Sign-list robustness** (`experiments/signlist_robustness/`): all nine headline tests keep their direction under 12 alternative sign lists (Wells/ICIT, merged and split variants, image-clustered lists). #1, #6, #9, #10a and #11 pass under every list. #3, #5, #7 and #10b miss their pre-registered bar under at least one coarse list, with effect sizes unchanged (lost power or partly a product of Mahadevan's fine splits).

**Positional grammar of the seal text** (`docs/GRAMMAR.md`, `experiments/grammar/`, pre-registered): a 16-class model (stable classes: opener 10 signs, connective M99/M123, medial 85, closer 7) beats position-only and shuffled baselines on held-out families (5.79 vs 6.38 bits/sign) but **loses to a plain sign bigram** (5.49), so it is a compact description (BIC favours it), not a better predictor. Gulf round seals score 1.80 bits/sign worse than matched Indus seals (p=0.0001), consistent with #4. Ur III positive control only partly recovered, so the grammar is not formally validated. `restore.py` proposes fillers for broken texts (true sign in top 5: 35%; the bigram gets 48%).

**What seal texts are** (cycle 7-10, all pre-registered; positive results red-teamed): open-ended and nearly all unique (new-text rate 93-97% per site), with no large city-specific sign stock (MD vs Harappa AUC 0.49; a planted 20% local stock is caught 92% in an exploratory power check; the pre-registered open-slot test was underpowered, so its formal verdict is inconclusive). Novelty sits in two slots (opener, medial), not one, so they do not look like a name + title formula. Short cross-site repeats are chance collisions; the main repeated longer text is the known M162 count frame. Seals found in the same house (Mohenjo-daro, Mackay 1938 register) or the same square (Harappa, Vats 1940) share no more signs than seals from elsewhere; a signature carried by half a household's seals would have been caught (power 0.90-1.0) in both cities (reg_findspot, reg_harappa).

## What is refuted or unsupported

- **No published phonetic key beats chance.** Yajnadevam's Sanskrit key: dictionary score z=1.0 against its own values shuffled (p=0.15). It needs at least 1.3 free choices per sign, and keys fitted the same way to random sign strings score as high. Earlier tests of the Pierson, Fairservis and S.R. Rao keys found the same (literature).
- **The scoring used by such claims cannot recognise a true key:** on a planted Sanskrit corpus the true key scores below keys fitted to noise (language).
- **No Kober/Ventris consonant-vowel grid exists in the data.** The method recovers a regular syllabic grid in planted languages (ARI 0.86) but finds nothing in Indus (z -0.04). It is weak even on real Linear B, so this rules out only a regular, well-attested syllabic language (phonetic_grid).
- **Statistics cannot pick the language.** A typology classifier scores 95% inside its simulator but calls real Latin "Munda". The Indus label flips with the random seed (language).
- **Animal emblems are not written in the seal text** (context). **No pictorial sign is tied to its matching picture on seals** (17 pre-registered tests, logograms). **Stroke numerals do not follow the Indus weight series**; short strokes peak at 7 and 12 (context).
- **No sound information leaks through spelling.** No phonetic complements, homophone sets, ligature decompositions or silent determinatives were found; ligature candidates (M343-5, M348, M190, M103+M403) are firmly refuted (internal_phonetics).
- **No Maya-style alternation of a sign with a 2-3 sign spelling** (substitution, pre-registered): dev at chance, 0 of 11 candidate equations replicate on held-out; heavy alternation (about 20%+ of word tokens) is unlikely, light alternation is not excluded. Real Ur III seal legends cut to Indus size show no phonetic swaps either, so this genre hides phonetics.
- **No travelling place names** (toponyms, pre-registered): sequences concentrated at one site are not over-represented on sealings, the clay that moved between cities, elsewhere (power 0.83-0.93). Local habits exist (e.g. a Chanhu-daro end mark, M93) but stay at home.
- **No relational readings.** Line 2 of a seal is not another seal's text, and no sign means "son of". Titles don't cluster by locus; Mahadevan's citadel (M267) vs lower town (M293) split is refuted. Side-2 counts are not ranks or dates, and no commodity sign appears on Lothal sealing backs. 0 of 14 pre-registered tests positive (administration).
- **Gulf seals do not spell foreign names by sound;** they are richer in person and number signs (typology). **No cuneiform anchor exists in print:** only two secure Meluhhan names (na-na-sa, sa-ma-ar), and no Indus seal abroad can be tied to a named person (meluhha).
- **What a sign depicts does not predict its grammatical role** (36 tests; iconography).
- **Dholavira has no regional pairing style** once training size is equalised (redteam). **No change in sign use over time** was detected (context), apart from an exploratory early-vs-late separation of Mohenjo-daro seals (AUC 0.61, p=0.02; site_signal, not pre-registered); with decimal excavation depths from the 1930s registers, no detectable change in slot classes or markers, at most a weak drift in Harappa seals (p=0.029, 0.057 corrected; reg_chrono).

## Why there is no phonetic reading yet: the decipherability result

`experiments/decipherability/` (phase diagram: `phase_diagram.png`). Five real languages were written in a simulated logo-syllabic script and attacked with a full key search:

- With a **perfect** model of the true language, ~2,500 tokens suffice (Indus has 10,005).
- With only a **related** language or phonotactics, recovery is 10-26%. It stays **flat from 2,500 to 230,000 tokens**, and a mostly wrong key outscores the true key in 88-100% of runs. More seals of the same kind will not help.
- Every language, wrong ones included, beats a shuffled corpus by z>7, so "beats a shuffle" proves nothing about the language.
- On the real Indus corpus no candidate stands out (Tamil z 0.45-0.76, Malayalam 0.3-1.05, Sanskrit ~0, Sumerian 0.3-0.5). A correctly planted language gives only z 0.3-2.8 at this size, so this null is expected even if the right language were among the candidates.
- A **word-level** cognate model (NeuroDecipher-style, `experiments/cognate_decipher/`) reproduces the Linear B result with a curated Greek cognate list (80-91% of signs read), but with a realistic related-language lexicon it reads 1-39%, flat with more text, and can confidently pick the wrong language (Pali ranks planted Sanskrit last of five). It needs a lexicon covering half the corpus's words plus word division; no Indus candidate has that, so Indus was not run.
- **What would help, in order:** a lexicon close to the true language (recovery 0.2 -> 0.8); longer continuous texts; 10-20 anchor values from a bilingual proper name (0.17 -> 0.47-0.68).

## Language: constraints from outside the script

- **Not Sumerian or Akkadian:** the Šu-ilišu seal names an "interpreter of Meluhha".
- **Vedic Indo-Aryan unlikely for the Mature Harappan period:** Harappan-related aDNA shows no steppe ancestry, which arrives 2000-1500 BCE.
- **Proto-Munda strained:** Austroasiatic appears to arrive too late.
- **Dravidian remains open but unproven.** The fixed "six + fish" compound is compatible with Parpola's Dravidian *aṟu-mīn* (Pleiades), but also with any language that names the six-star Pleiades (e.g. Vedic *Kṛttikā*). "Seven + fish" is not attested, against his Ursa Major reading.

## Repository

- `corpus/build.py`, `corpus/load.py`: builds the corpus from `sources/` and exposes shared loaders and the held-out splits.
- `data/`
  - `m77_lines.jsonl`, `m77_texts.jsonl`: Mahadevan 1977, 3,573 lines, 13,372 tokens, 417 signs; matches his published totals exactly.
  - `icit_texts.jsonl`: Wells/Fuls ICIT, 5,679 inscriptions, reading order.
  - `splits_v2.json`: held-out split by text family, zero near-copy leakage. `splits.json` (v1) leaked: 45% of held-out texts had a near-copy in dev.
  - `sign_images/`: Mahadevan's drawing of every sign.
- `docs/AGENT_BRIEF.md`: rules of evidence every experiment follows.
- `experiments/<area>/`: code, `RESULTS.md` and `results.json` for each area (64 areas; full list and verdicts in `docs/NEGATIVE_ATLAS.md` and `docs/test_ledger.csv`).
- `docs/GRAMMAR.md`, `docs/PREDICTION_REGISTRY.md`, `docs/NEGATIVE_ATLAS.md`, `docs/HUMAN_LEADS.md`, `docs/outreach/` (draft data requests, unsent), `RELEASE_NOTES_v1.1.md`, `docs/REPRO_REPORT.md`.
- `experiments/old_registers/registers.csv`: per-seal depth, size and findspot from the public-domain Marshall 1931, Mackay 1938/1943 and Vats 1940 registers.

Rebuild everything with `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `scripts/reproduce.sh` (fixes the hash seed and keeps the frozen `splits_v2.json`; `corpus/build.py --force-split` rebuilds it). The `sources/` repos are cloned by hand (list in `corpus/build.py`).

## Known weaknesses

- Wave-1/2 held-out tests used split v1, which leaked near-copies; the top claims were re-run on v2 (`experiments/revalidation/`).
- About 14,100 tests sit behind the headline claims (`docs/test_ledger.csv`, 842 rows as of cycle 10; the test total was not re-derived after cycle 3). A project-wide Benjamini-Hochberg correction now exists (`experiments/ledger/`), but only claims that replicated on an independent transcription or on clean held-out data are ranked above.
- ICIT is mostly a second transcription of the same objects, not new data. About 90% of it comes from sites M77 covers.
- Iconic judgements of sign drawings (e.g. M184 = rhinoceros, M346 = goat-antelope) were not blind and use drawings, not photographs.

## Data sources and credit

- Mahadevan 1977 via indusscript.in (export in [paragorth/Indus-](https://github.com/paragorth/Indus-)).
- ICIT (Wells and Fuls) via yajnadevam/lipi ([field-cady export](https://github.com/field-cady/indus_valley_script_corpus)).
- Mahadevan-Wells sign bridge and prior findings: [shaunmortal/indus](https://github.com/shaunmortal/indus).
- Null-model toolkit: [joyboseroy/indus_decipher](https://github.com/joyboseroy/indus_decipher).

Licences of derived corpus data follow their sources.
