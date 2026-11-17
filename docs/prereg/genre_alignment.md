# Pre-registration: genre alignment ("structural bilingual") of Indus seal slots

Agent: genre_alignment. Written 2026-11-15 after building the cuneiform corpora and running the controls (`experiments/genre_alignment/ga_controls.py` -> `controls.json`), and BEFORE computing any Indus fingerprint or alignment. The only Indus facts used so far: number of distinct seal texts per split (dev 1,240, held-out 391) and the role labels already published in `experiments/functional_reading/RESULTS.md`.

## Data
- Reference cultures (word level, CDLI open dump downloaded by short_labels; reused read-only): distinct seal legends with no broken word. Ur III 5,252; Old Babylonian (incl. early OB) 2,763; Old Akkadian + Old Assyrian 254 (control only). Slots annotated by rule (`ga_slots.py`): SEAL_OF (kišib), OWNER, TITLE, KIN (dumu/dumu-munus/dam), FATHER, SERV (arad/geme2, incl. arad2-zu), LORD (deity or king), EPITHET, CONJ. Hand audit of 70 random legends: about 5% of Ur III and 13% of OB legends have at least one mis-slotted word.
- Indus: distinct M77 seal texts, no `#`, from `functional_reading/readings.csv` (v2 split column). Slots per sign from the parse. Primary = COARSE level: OPEN (O), CONN (C), CORE (S, T, U, F, N), TITLE (I and non-closer signs inside a TITLE-BLOCK), CLOSER (J and B), POST (P).

## Method (frozen in `ga_core.py`, `ga_indus.py`)
- Slot run = maximal stretch of same-slot tokens; 15 label-free features per slot (occupancy, mean position, first/last share, filler length, type-token ratio / entropy at 100 runs, top filler share, Zipf slope, retention on short texts, recursion, unit sharing with other slots, alone share, max/min co-occurrence lift). Slots need >= 30 runs and >= 2% occupancy.
- z-scoring with mean/sd frozen from cuneiform slots only (controls.json). Distance = Euclidean / sqrt(15).
- Reference fingerprint = mean over 20 subsamples cut to the Indus split size. Hungarian matching of Indus slots onto reference slots.
- Global test: column-permutation null (each feature permuted among Indus slots, 2,000 draws) on the mean matched distance.
- Pair stability: 100 bootstraps (Indus texts resampled, fresh reference subsample).
- Acceptance threshold tau = 0.803 (largest distance at which C1 matches are >= 80% correct).

## Controls already run (known before this registration)
- C1 gold-to-gold at Indus size (40 reps): Ur III -> OB 53% of slots matched to their same-meaning slot, OB -> Ur III 53%, Ur III -> OAkk+OA 85%; random 11%. Per-slot reliability: OWNER 1.00, FATHER 1.00, KIN 0.97, SERV 0.89, TITLE 0.33, EPITHET 0.33, LORD 0.00 (LORD is initial in Ur III presentation seals but final in OB "arad DN" seals).
- C2 planted blind control (Ur III relabelled, slots induced blindly by positional clustering, aligned to gold OB): 28-35% of induced classes get the right meaning vs 11% random (k = 4, 6, 8).
- Consequence: only OWNER, FATHER, KIN, SERV are meaning-bearing targets; a match to TITLE, EPITHET or LORD cannot carry meaning even if it is close.

## Predictions (coarse Indus slots)
| id | prediction | reference |
|---|---|---|
| P1 (primary) | CLOSER -> SERV ("servant of", final closed relator) | Ur III and OB |
| P2 | CORE -> OWNER (open name slot) | Ur III and OB |
| P3 | TITLE -> TITLE | Ur III and OB (meaning not transferable, reliability 0.33) |
| P4 | CONN -> KIN (closed relator) | Ur III and OB |
| P5 | OPEN -> SEAL_OF (initial possessive "seal of") | OB only |
Alternatives for the closer named in advance: KIN (genitive-like relator "son of"), TITLE, LORD (deity/king).

## Decision rule (per prediction and reference)
- **Supported** if all hold: (a) global column-permutation p < 0.05 on dev; (b) the predicted pair is chosen in >= 70% of dev bootstraps; (c) its dev distance < tau; (d) the pair is chosen in >= 50% of held-out bootstraps; (e) the reference slot has C1 reliability >= 0.75.
- **Suggestive** if (a), (b), (d) hold but (c) or (e) fails.
- Otherwise **not supported**.
- The closer is assigned a meaning only if P1 (or a named alternative with a reliable slot) is supported in BOTH Ur III and OB.
- Tests: 9 prediction x reference pairs plus 4 global tests (2 refs x dev/held-out) = 13. Report Bonferroni at 0.05/13 for the global p-values.

## Exploratory (labelled as such)
Fine Indus slots (NUM, FISH, NOUN, BFISH separate); blind-induced Indus classes (same inducer as C2) aligned to the references.

## What would falsify a supported mapping
The mapping fails to replicate on held-out; or it does not survive the fine-level split; or it depends on one feature (to be checked by leave-one-feature-out).
