# Closer and connective: red team of the "son of" match, and a pre-registered test of "closer = ownership/title"

Agent closer_ownership, 2026-11-15. Pre-registration: `docs/prereg/closer_ownership.md`, hash-frozen together with `co_lib.py` and `co_core.py` (`docs/prereg/HASHES.txt`) before any fresh reference, held-out or ICIT feature was computed. Ledger rows: `co_*` in `docs/test_ledger.csv`. Unit: distinct texts and distinct legends.

## Findings first

1. **The connective's "son of" match does not survive without the grammar (Task A: fails, by the wording set in advance).**
   - It replicates when the grammar's own slots are used: M99/M123 lands on dumu in 100% of bootstraps.
   - It disappears when slots come from distributional clustering of the signs instead. M99 never forms a slot of its own; it falls into a group of 17-43 signs (fish signs, numerals, M336, M343). That group's nearest Mesopotamian slot is never dumu (0 of 48 runs) and its distance to dumu is at least 1.14, well over the 0.80 bar.
   - With no slots at all (the sign's own profile compared with word classes), M99 looks most like a title or "servant of" word, never dumu (0 of 6).
   - What is left is a raw fact about position: M99 is frequent, sits mid-text, is almost never first (4%) or last (1%), and almost never appears on texts of 1-2 signs (1%, against 12% of all texts). Any linking word fits that. It is not evidence for "son of".
2. **The closer-as-ownership test cannot be decided (Task B: untestable). The planted control fails, and the lead's main argument breaks down on fresh data.**
   - **Control.** Take one Mesopotamian culture, hide its words and line it up against another. The procedure should then sort "seal of" (kišib) from "servant of" (arad). It does not: 25% correct with real slot labels (gate 0.75) and 50% in the blind version. Even "seal of" behaves differently from one period to the next. In Old Babylonian it opens short legends ("seal of PN"). In Old Assyrian it opens long ones ("seal of PN son of PN2").
   - **Wrong premise.** The lead rested on "relators never stand next to a bare name". That is false once both sides are cut into slots the same coarse way. "Servant of" stands beside a single content block in 35% of Old Akkadian and 32% of Ur III legends where it occurs, because the king's name, the owner and the title all merge into one block. The fresh-reference value is 0.20, against the 0.05 limit (P5 fails).
   - **What held.** On fresh Indus data the closer does appear on short legends (held-out 47%, ICIT 49%) and beside a single content block (44% / 47%), so P1 and P2 pass.
   - **What went against the lead.** The closer is *more* common on long legends (+0.47 held-out, +0.37 ICIT), whereas Old Babylonian "seal of" is −0.60 (P3 fails). Its overall profile is no nearer ownership or title than servant: own/title wins only 61% and 52% of bootstraps, against the required 80% (P4 fails).
3. **Net effect on the project.** genre_alignment's one positive (CONN = dumu) shrinks to "M99 has the position profile of a linking word". Its post-hoc lead (closer = title/ownership) is neither supported nor refuted, and this method cannot test it. With these features, slot fingerprints do not carry the meaning "seal of" vs "servant of" across Mesopotamian periods, so they cannot carry it to Indus.

## Data
| set | distinct texts | notes |
|---|---|---|
| Fresh references (never aligned to Indus) | 431 legends | Old Akkadian 145, Old Assyrian (Kanesh) 109, Middle Babylonian 132, ED IIIb 22, Lagash II 10, Neo-Assyrian 10, MA 2, NB 1. CDLI open dump, word level, no broken word (`co_extract.py`). OAkk and OA had been used only as a gold-to-gold control target in genre_alignment. Strict-fresh subset (MB, ED IIIb, Lagash II, NA, MA, NB) is 177 legends. |
| Known references | Ur III 5,180; OB 2,760 | used by genre_alignment; development and comparison only |
| Indus dev / held-out v2 | 1,194 / 418 seal texts | M77, break-free, line breaks dropped |
| ICIT new sites | 171 seal texts | SEAL* from sites absent from M77 (Dholavira, Nausharo, Banawali...), W signs |

Not available: separate Mari seals (inside the OB group), Neo-Sumerian outside Ur III beyond 10 Lagash II legends, and Egyptian scarabs (no open sequence corpus with slot structure in the downloads). The fresh pool is small: 40 kišib, 92 arad and 138 title tokens.

Slot tagging: my own word-class rules (`co_lib.py`). kišib forms, arad/geme2 forms (excluding personal names like arad-{d}nanna), dumu/dam (and MB/NA *a* "son"), a title list (seed list plus words that are frequent, never first and right after the first word in Ur III/OB), and deities/king. The genre_alignment code was not read until my code and results existed. I then checked only its feature list: 5 of its 15 features (filler length, type-token ratio, top-filler share, entropy, Zipf slope) describe the fillers.

## Task A: red team of CONN → dumu

| Indus slot definition | depends on grammar? | CONN/M99 → KIN? | key numbers |
|---|---|---|---|
| R0 functional-reading parse roles (replication) | yes | **yes** | Hungarian matching and bootstraps 1.00 (Ur III, OB, dev and held-out); d 0.59 / 0.35 |
| R1 sign lists (M99, M123 as one class; rest CORE) | lexicon only | yes on dev; weaker on held-out | held-out boot Ur III 0.91, OB 0.68 (SERV 0.32); M99 alone 1.00 / 0.94 |
| R2 distributional clustering (dev; k = 5, 6, 8, 10 × 3 seeds) | **no** | **no** | M99 never isolated; cluster has 10.9-18.2 distinct fillers per 20 runs (dumu 1.3-1.9); nearest slot LORD/TITLE in 48/48; Hungarian KIN 7/48 (29/48 with filler features dropped); dKIN ≥ 1.14 > 0.80 |
| No slots: token profile of M99 vs word classes | **no** | **no** | nearest TITLE (Ur III), TITLE/SERV (OB), SERV (fresh): KIN 0/6. Nearest words: dub-sar, arad2, lugal |

**Circularity.** Defining CONN as {M99, M123} fixes 5 of genre_alignment's 15 features: a slot with two fillers is "closed" by construction. The grammar also forces first, last, short-legend and stand-alone shares to exactly 0. In raw data these are small but not zero: initial 4.2%, final 0.8%, on ≤2-sign texts 0.8% (dev), and 3-5% on held-out and ICIT. So "mid-legend, never on short seals" is real, while "closed class" is built in. Dropping the filler features keeps CONN → KIN under R0 and R1, so the replication does not rest only on the built-in part. The match does rest on M99 being given a slot of its own.

**Pseudo-connective null.** Each of 36 frequent CORE signs was made its own one-sign slot. Against Ur III, Hungarian matching gives KIN to 97% of these pseudo-slots, because one-to-one matching pushes any one-sign slot onto dumu. That makes Ur III's "100% KIN" uninformative on its own. Against OB, only 6% go to KIN. M99's distance to KIN is smaller than 35 of the 36 pseudo-slots in both references (p = 0.027). That is the most that survives: among signs forced into a slot, M99 has the most dumu-like position profile.

**Verdict A: fails as an independent result, by the rule set in advance** ("fails if not nearest KIN under grammar-free slots"). Caveat: blind slot induction is weak (genre_alignment C2 gets 28-35% right on Ur III), so this failure does not show that M99 is *not* a relator. It only shows that the dumu match cannot be claimed apart from the grammar. Defensible restatement: *M99 is a frequent mid-text sign with the position profile of a linking word; which linking word it is cannot be told.*

## Task B: pre-registered test of "closer = ownership/title, not servant"

Method (frozen): **matched-coarse segmentation, same rule on both sides.** Closed function classes are kept as slots and all open material is merged into one CONTENT block. Five position-free features: share present on ≤2-run legends; share standing beside one content block only; long-minus-short presence; occupancy; edge share. Nearest reference class among SEAL_OF, TITLE, SERV and KIN, with 200 bootstraps.

### Gate (planted control): FAILS
| control | result | bar |
|---|---|---|
| G1 gold slots, OB → fresh | kišib → SERV 40/40; arad → KIN 40/40 | |
| G1 gold slots, fresh → OB | kišib → TITLE 40/40 (counted correct); arad → TITLE 40/40 | |
| G1 mean / min binary accuracy | **0.25 / 0.00** | 0.75 / 0.5 |
| G2 blind relabelled (top-12 words as own slots) | kišib forms 1.00 (n = 42), arad forms 0.25 (n = 81), pooled **0.50** | 0.75 |
| (development, disclosed in the prereg) Ur III ↔ OB | OB kišib → Ur III SERV 40/40; Ur III arad → OB TITLE 30/40 | |

Why it fails: no reference class keeps one profile across periods. Under matched-coarse slots:

| class | OB | Old Assyrian | Middle Babylonian | Old Akkadian | Ur III |
|---|---|---|---|---|---|
| kišib: short / next to content only / long−short | 0.62 / 0.95 / −0.60 | 0.00 / 0.00 / +0.77 | 0.05 / 0.13 / +0.29 | (none) | (none) |
| arad: short / next to content only / long−short | 0.02 / 0.02 / +0.94 | (n < 10) | 0.00 / 0.00 / +0.61 | 0.20 / 0.35 / +0.69 | 0.44 / 0.32 / +0.51 |

### Predictions
| id | prediction | held-out | ICIT | result |
|---|---|---|---|---|
| P1 | short ≥ 0.40 | 0.472 (90% CI 0.42-0.52) | 0.490 (0.41-0.56) | pass |
| P2 | stands beside one content block ≥ 0.20 | 0.438 (0.38-0.49) | 0.474 (0.39-0.54) | pass |
| P3 | long − short ≤ 0 (ownership-specific) | +0.47 | +0.37 | **fail** |
| P4 | own/title nearer than SERV in ≥ 80% of bootstraps | 0.61 | 0.525 | **fail** |
| P5 | fresh SERV short ≤ 0.10 and beside-content ≤ 0.05 | 0.097 / 0.196 | | **fail** |

Nearest class (point estimate) for the closer set: fresh pool TITLE (d 1.16 vs SERV 1.19); strict-fresh SEAL_OF (1.28 vs 1.54); OB SEAL_OF; Ur III SERV (0.73). Jar alone: fresh SERV (0.71 vs TITLE 0.73), Ur III SERV (0.53). All distances except Ur III are above 0.8. The answer depends on which reference you pick.

**Verdict B: untestable (gate failed).** Read descriptively, the fresh data cut slightly *against* "ownership marker": the jar becomes more frequent as legends get longer, the opposite of OB kišib. Title and servant-of profiles cannot be told apart.

## Hypotheses tested
| hypothesis | verdict | key number |
|---|---|---|
| CONN = dumu slot, independent of the grammar | **fails** (red team) | grammar-free nearest KIN 0/48 and 0/6; dKIN ≥ 1.14 |
| CONN is the most relator-like one-sign slot | weak support | below 35/36 pseudo-slots, p = 0.027 |
| "Closed class" profile of CONN is built into its definition | **confirmed** | 5/15 features fixed by the definition |
| Slot fingerprints transfer kišib vs arad across cultures | **refuted** | G1 0.25, G2 0.50 |
| Closer = ownership/title, not servant | **untestable** | gate fails; P1, P2 pass; P3, P4, P5 fail |
| Relators never stand beside a bare name (genre_alignment premise) | **refuted** under matched segmentation | Ur III arad 0.32, OAkk 0.35, fresh 0.20 |

Tests: Task B 11 pre-registered (2 gates, 9 predictions). Task A has 5 red-team comparisons plus 36 pseudo-slots and 12 clusterings. The only p-value is the pseudo-slot null (0.027), which does not survive a Bonferroni correction over 16 rows.

## Caveats
- The fresh references are small and mixed: MB legends are long prayers, OA legends are almost all "PN dumu PN2". Rule-based tagging is noisy (title and name boundaries especially).
- The Indus sign lists (opener, connective, closer) come from earlier positional work. The clustering run avoids them but is a weak inducer.
- Word (reference) vs sign (Indus) units differ: Indus names are 1-2 signs, Sumerian names one word. This is why the primary Task B analysis uses slot runs, not tokens.

## Files
`co_extract.py` (CDLI word-level legends → `data/legends_all.jsonl`), `co_lib.py` and `co_core.py` (frozen), `co_dev_*.py` and `co_dev_check.log` (development on known refs and dev), `co_taskB.py` → `taskB.json`, `co_taskB.log` (pre-registered run), `co_taskA.py` → `taskA.json`, `co_taskA.log`, `results.json`. Run from this folder: `../../.venv/bin/python -I co_taskA.py`; for the others use `-c "import sys; sys.path.insert(0,'.'); exec(open('co_taskB.py').read())"` (with `-I` the script folder is not on the path).

## Next experiments
1. Drop slot-fingerprint alignment as a route to word meaning. Its own control fails within Mesopotamia.
2. If the closer question is pursued, use object context rather than distribution: closer rates on seals vs sealings vs tablets of the same text (an ownership mark should travel with sealings). Pre-register it.
3. M99: test whether it ever links two independently attested names (X M99 Y, where X and Y both occur as whole seal texts). That is a relational test that position profiles cannot replace.
