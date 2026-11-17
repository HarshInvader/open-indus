# Pre-registration: is the Indus closer an ownership/title marker rather than "servant of"?

Agent: closer_ownership. Written 2026-11-15, after development on KNOWN references (Ur III, Old Babylonian; already used by genre_alignment) and Indus dev only (`co_dev_explore.py`, `co_dev_slots.py`, `co_dev_check.py`, log `co_dev_check.log`), and BEFORE computing any feature on the fresh references, Indus held-out (v2) or ICIT. Facts known about the fresh data at registration time: legend counts per period and their most frequent words (from `co_extract.py`), and the counts of held-out (418) and ICIT new-site (171) seal texts. Code frozen: `co_lib.py`, `co_core.py` (hashes in `docs/prereg/HASHES.txt`).

## Lead under test
genre_alignment (exploratory): the closer (jar M342 and the other closers) behaves like a title or "seal of" (kišib) ownership marker, not like "servant of" (arad), because it survives on 1-2 slot legends (53%) where Mesopotamian relators never occur.

## Data
- **Fresh references** (never aligned to Indus): CDLI open dump, word level, distinct legends, no broken word, slots tagged by rule (`co_lib.tag_legend`, class lists and title list derived from KNOWN cultures only). Pool F = Old Akkadian 145, Old Assyrian/Kültepe 109, Middle Babylonian 132, ED IIIb 22, Lagash II 10, Neo-Assyrian 10, MA 2, NB 1 = 431 legends. Strict-fresh subset (not even in genre_alignment's C1 control) = MB + ED IIIb + Lagash II + NA + MA + NB = 177. Mari seals are in the OB group (already used) and are not available as a separate fresh set; no open Egyptian scarab sequence corpus with slot structure exists in the downloads.
- **Indus fresh**: (i) M77 held-out v2 distinct seal texts, break-free, line breaks dropped: 418; (ii) ICIT seals (SEAL*) from sites absent from M77, distinct, break-free, W signs: 171.
- KNOWN references (Ur III 5,180, OB 2,760) are reported for comparison only.

## Method (frozen)
- **Matched-coarse segmentation, same rule on both sides.** Closed function classes are kept as slot labels, all open content is merged into one CONTENT label. Reference: SEAL_OF, SERV, KIN, CONJ kept; TITLE kept only when it is the target class; OWNER/NAME/FATHER/LORD -> CONTENT. Indus: OPEN {M267, M391, M293, M150}, CONN {M99, M123}, POST {M176, M1}, CLOSER kept; the rest -> CONTENT. ICIT signs mapped by the first M reading in the bridge.
- **Closer**: primary = closer set {M342, M211, M12, M14, M15, M254, M169, bracketed fish M60/66/68/71/73}; secondary = jar M342 alone.
- **Decision features** (position-free, label-free): short = P(slot present | legend has <=2 slot runs); nameonly = P(legend is exactly CONTENT + slot | slot present); longdiff = P(present | >=4 runs) - P(present | <=2 runs); occ = P(present); edge_s = share of slot runs at either legend edge (mirror-invariant). Reported only: share last/first, distinct fillers per 20 runs (definition-dependent for a closed sign list), recursion, alone.
- **Scaling**: sd per feature frozen from KNOWN class fingerprints: [0.227, 0.328, 0.524, 0.249, 0.364] (floor 0.05). Distance = Euclidean on scaled features / sqrt(5).
- **Classification**: nearest reference class among SEAL_OF, TITLE, SERV, KIN (classes with >= 10 legends). 200 bootstraps (Indus texts and reference legends resampled).

## Development facts already known (disclosed)
- Indus dev closer set: short 0.60, nameonly 0.37, longdiff +0.35, occ 0.72, edge_s 0.79. Jar alone: 0.34, 0.34, +0.55, 0.47, 0.77.
- Dev classification: vs Ur III -> SERV (closer set and jar); vs OB -> SEAL_OF (set) / SERV (jar).
- **Planted control on KNOWN refs already FAILS**: at held-out size, OB kišib -> Ur III SERV in 40/40 reps (Ur III has no kišib slot); Ur III arad -> OB TITLE 30/40, SEAL_OF 9/40, SERV 1/40. Blind version: OB kiszib/kiszib3 -> Ur III SERV 20/20, OB arad/arad2 -> Ur III TITLE 20/20, Ur III arad2-zu -> OB TITLE 20/20. Reason: under coarse segmentation Ur III "king ... PN title arad2-zu" is CONTENT + SERV, a final closed word beside one content block, i.e. the same profile as the Indus closer. "Servant of" is not one distributional type across Mesopotamian periods. **I therefore expect the gate below to fail and the verdict to be "untestable"**; the test is run anyway on fresh data.

## Gate (planted control on fresh data; must pass for any verdict)
- G1 (gold slots): at Indus held-out size (418 legends, 40 reps), classify A's SEAL_OF and SERV slots against B's classes for A->B in {OB->F, F->OB}. Binary success = SEAL_OF -> {SEAL_OF, TITLE}; SERV -> SERV. Pass if mean binary accuracy over the 4 cells >= 0.75 and no cell < 0.5.
- G2 (blind, relabelled): A's words relabelled; each of A's 12 most frequent word types is its own closed label, the rest CONTENT; every kišib-form and arad-form among them is classified against B's gold classes (A->B in {OB->F, F->OB}, 20 reps). Pass if binary accuracy >= 0.75 pooled over kišib and arad forms and >= 0.5 for each of the two.

## Predictions (lead = "closer is title/ownership, not servant")
| id | prediction | threshold |
|---|---|---|
| P1 | closer appears on short (<=2 run) legends | short >= 0.40, held-out and ICIT |
| P2 | closer stands alone beside one content block | nameonly >= 0.20, held-out and ICIT |
| P3 | ownership-specific: closer not commoner on long legends | longdiff <= 0, held-out and ICIT (dev +0.35: expected to fail) |
| P4 | fingerprint is nearer own/title than servant in fresh pool F | min(d SEAL_OF, d TITLE) < d SERV in >= 80% of bootstraps, held-out and ICIT |
| P5 | in fresh references "servant of" does not stand alone with a name | F: SERV short <= 0.10 and SERV nameonly <= 0.05 (needed for P1/P2 to discriminate) |

## Decision rule
- Gate fails -> **untestable** (the features cannot tell kišib from arad across cultures), whatever P1-P5 give.
- Gate passes: **supported** if P1, P2, P4, P5 hold on both Indus sets; "ownership rather than title" additionally needs P3. **Refuted** if SERV is the nearest class in >= 80% of bootstraps on both sets, or short < 0.20 on both. Otherwise **inconclusive**.
- Secondary (jar alone) and strict-fresh subset are reported, not used for the verdict.
- Tests: G1, G2, P1x2, P2x2, P3x2, P4x2, P5 = 11.

## What would falsify the lead
A passing gate together with SERV nearest on both held-out and ICIT, or the closer absent from short legends on fresh Indus data.

## Task A (red team, not a prereg of a new claim)
Reimplementation of CONN -> dumu without the functional-reading grammar: grammar-free token profiles of M99 vs reference word classes, a pseudo-connective null (any single frequent medial sign defined as its own slot), and slots from positional/distributional clustering. Verdict wording fixed in advance: survives (M99/its induced slot still nearest KIN, specific vs pseudo-slots p < 0.05, holds dev and held-out), weakened (nearest KIN only under some definitions or not specific), fails (not nearest KIN under grammar-free slots).
