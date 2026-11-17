# Pre-registration: predictions for newly published Indus inscriptions (new finds, ~2010-2026)

Author: new-data specialist agent. Written 2026-11-14 BEFORE any new inscription was searched for, viewed or transcribed. Frozen by sha256 in `docs/prereg/HASHES.txt`.

## Test set (defined in advance)

- Inscriptions published after the ICIT / M77 coverage (roughly 2010-2026): Rakhigarhi, Farmana, Kanmer, Dholavira post-2015, Sanauli, Khirasara, Bhirrana, Karanpura, Ganweriwala, Gola Dhoro/Bagasra, Juni Kuran, Shikarpur, Lothal re-excavation, Harappa HARP after 2007, Gulf/Oman/Iran finds after 2010, and any other legible new Indus inscription. Keezhadi / South Indian graffiti are NOT Indus and are excluded.
- Each candidate must be checked against ICIT (`data/icit_texts.jsonl`) and M77 by site, CISI number and sign sequence. Anything already in either corpus is excluded (logged, not scored).
- Unit: distinct texts (identical sequences count once). Objects whose text cannot be read with at least medium confidence for >=50% of signs are logged but excluded from scoring.
- Transcription is into Mahadevan numbers (M###) by visual comparison with `data/sign_images/`; per-sign confidence high/medium/low; reading direction marked. Primary analysis = all scored texts; sensitivity analysis = only signs/texts at high+medium confidence. A sign that matches no M77 sign is coded `NEW`.
- Foreign (Gulf/Iran/Central Asia) round seals are analysed separately and excluded from P1-P12 (they are known to break Indus order; README #4).

## Known bias, declared

The transcriber (this agent) knows these predictions. Visual transcription of worn signs can drift toward expected readings (e.g. reading an unclear final sign as the jar). Mitigations: (1) where the publication gives its own sign list or transcription, record it and prefer it; (2) record confidence per sign and rerun every test on high-confidence signs only; (3) transcribe each object sign by sign before scoring anything; scoring code runs only after `new_texts.csv` is complete.

## Baselines (computed on old data only; `experiments/new_finds/baselines.py`, `baselines.json`, `ref_tables.json`)

M77 distinct native texts: 2,253; complete unbroken texts with >=2 signs: 1,684. Leave-one-site-out (LOSO) rates for Lothal / Kalibangan / Chanhu-daro give the expected range for a site not in the reference data.

## Predictions

"CI" = Wilson 95% interval on the new-text proportion. A prediction PASSES when its stated criterion holds; INCONCLUSIVE when n is below the stated minimum; otherwise FAILS. No thresholds may be changed after this file is hashed.

| id | prediction | old-data basis | criterion (pass) | min n |
|---|---|---|---|---|
| P1 | Among complete, unbroken seal texts of >=2 signs, the share ending in jar M342 (or M342 M176) is similar to old seals | M77 seals 0.38 | point estimate in [0.20, 0.60] AND CI contains 0.38 | 8 texts |
| P1c | Jar M342 tokens (unbroken lines) are line-final or followed only by M176 | 0.80 (n=960) | share >= 0.65 | 5 tokens |
| P2 | Adjacent sign pairs that have a majority order in M77 (>=2 occurrences, majority >=2/3; 849 pairs in `ref_tables.json`) keep that order in new texts | in-sample 0.96; core_semantics held-out 0.83 | share >= 0.75 AND one-sided binomial vs 0.5 p < 0.05 | 8 pair tokens |
| P3 | Ticked/bracketed fish (M60, M66, M68, M71, M73) are line-final | 0.68 (n=60); plain fish 0.08 | ticked final share >= 0.50 AND exceeds plain-fish final share | 3 ticked tokens |
| P4 | Six-stroke M109 is followed by plain fish M59 | 0.48 (n=25 non-final M109) | share >= 0.30; any M109 + fish other than M59 counted as a miss | 2 tokens |
| P5 | The frozen functional-reading template (`experiments/functional_reading/fr.py`, `load_model()`, unchanged) parses new texts at the old rate | held-out 0.76, ICIT new sites 0.77, shuffled 0.33-0.37 | CI contains 0.77 AND point estimate exceeds the within-text shuffle mean (20 shuffles) | 10 texts of >=2 signs |
| P6 | First signs of complete texts are already attested as text-initial in M77 | LOSO 0.91-1.00 | share >= 0.85 | 8 texts |
| P7 | Last signs of complete texts are already attested as text-final in M77 | LOSO 0.83-0.96 | share >= 0.85 | 8 texts |
| P8 | Sign tokens are existing M77 signs (not `NEW`) | LOSO 0.95-0.99 | share >= 0.93 | 30 tokens |
| P9 | Openers M267 / M391, when present in a complete text, stand first | 0.74 (n=405) | share >= 0.60 | 4 tokens |
| P10 | M176 is line-final | 0.83 (n=197) | share >= 0.70 | 3 tokens |
| P11 | Mean length of complete texts (all object types) | M77 mean 4.85, median 5 | mean in [3.0, 6.5] | 8 texts |
| P12 | Reading direction is right-to-left (where determinable) | ICIT 0.955 R/L (n=2,963) | share R-to-L >= 0.85 | 8 texts |
| P13 | Fish partners: among fish / non-fish adjacent pairs, the non-fish partner is in {M53, M387, M343, M171, M389} | core_semantics 24% vs 13% base | share >= 0.20 | 8 pairs |
| P14 | (exploratory) Fish stands first in fish / non-fish adjacent pairs | M77 0.54 (n=1,289) | reported only | - |
| P15 | (exploratory) Any new foreign round seals fail the template more often than native new texts | functional_reading: 0.53 vs 0.22 | reported only | - |

## Overall verdict rule

Count passes among P1-P13 that reach their minimum n. "Old structure transfers to new finds" is supported if >= 75% of evaluable predictions pass, and contradicted if <= 50% pass. In between = mixed. Report the count with and without low-confidence signs, and the number of texts, objects and low-confidence transcriptions.

## What would falsify

P2 below 0.6 with n >= 20, P5 below 0.55 with n >= 20, or P8 below 0.85 would mean the old corpus does not represent the new material (regional or period difference, or our structure is overfit to Mohenjo-daro/Harappa).
