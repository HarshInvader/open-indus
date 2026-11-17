# Genre alignment: matching Indus seal slots to Mesopotamian seal-legend slots

Code: `ga_extract.py` (CDLI seal legends at word level), `ga_slots.py` (slot annotation, Indus slots), `ga_core.py` (fingerprints, Hungarian alignment, nulls), `ga_controls.py` (controls), `ga_indus.py` (pre-registered run), `ga_explore.py` (exploratory). Run from the repo root as `.venv/bin/python -I experiments/genre_alignment/<script>.py`, in that order. Outputs: `controls.json`, `indus_alignment.json`, `explore.json`, `results.json`, logs `*.log`. Pre-registration: `docs/prereg/genre_alignment.md`, hash-frozen in `docs/prereg/HASHES.txt` before any Indus fingerprint was computed. Ledger: rows `ga_*` in `docs/test_ledger.csv`.
Unit: distinct texts (one per distinct legend or sign sequence).

## Conclusion first

1. **The Indus closer (jar M342 and other closers) does not line up with "servant of".** The primary prediction (P1, closer = arad "servant of") failed against both references. Ur III puts the closer nearest FATHER (59% of bootstraps; "servant of" 22%). Old Babylonian (OB) puts it on the deity/king slot LORD (99%), which the controls show carries no transferable meaning. Every closer distance is above the pre-registered threshold. **No meaning can be assigned to the closer by this method.**
2. **One mapping is supported: the connective (M99 after M267/M391, M123 after M293/M150) is distributed like the kinship relator dumu "son of".** This holds for both references, on dev and held-out: chosen in 95-100% of bootstraps, distance 0.50-0.73 against a threshold of 0.80, and it survives dropping any one of the 15 features. **Read it modestly:** what matches is the profile of "a closed, one-sign linking word, always in mid-legend and never on short seals". It does not show that M99 means "son of". Any relator word (e.g. "of", "and") would give the same fingerprint, and part of the connective's profile comes from how the functional grammar defines it.
3. **Suggestive only:** Indus core = OB owner name, title = OB title, opener = OB kišib "seal of". All three are stable in bootstraps but fail either the distance threshold or the control-based reliability requirement. None replicates against Ur III.
4. **Exploratory finding (not pre-registered) that cuts against "servant of" and against any relator reading of the closer.** In Mesopotamian seals, relators (dumu, arad) never appear on legends of one or two slots: 0% in both Ur III and OB. The Indus closer appears on 53% of 1-2-slot Indus seals ("name + jar"). On short legends it behaves like a slot that can stand beside the bare name: the Ur III title (72%) or OB kišib "seal of" (66%). With position features removed, its nearest neighbours are Ur III TITLE (dev 0.97, held-out 0.76) and OB SEAL_OF/LORD (1.02-1.10). Hypothesis, with low confidence: **the closer is a title or possessive/ownership marker, not "servant of".**
5. **The method works between known cultures, but only for some slots.** At Indus size, Ur III to OB matches 53% of slots correctly (random 11%). Ur III to the small Old Akkadian + Old Assyrian pool matches 85%. Only OWNER, FATHER, KIN and SERV transfer reliably (0.89-1.00). TITLE, EPITHET (0.33) and LORD (0.00) do not: the "servant of DN" block sits at the end in OB but the king's name opens Ur III presentation seals. With blind-induced slots (planted control C2) only 28-35% of classes get the right meaning. So the real bottleneck is the quality of the Indus slots, not the alignment.

## Data

| corpus | distinct legends | source | slots |
|---|---|---|---|
| Ur III seals | 5,252 | CDLI open dump (`experiments/short_labels/raw/cdli`, reused read-only), `@seal` sections + seal objects, no broken word | OWNER, TITLE, KIN, FATHER, SERV, LORD, EPITHET, (CONJ, SEAL_OF rare) |
| Old Babylonian seals | 2,763 | same | + SEAL_OF (kišib, 21% of legends), CONJ |
| Old Akkadian + Old Assyrian | 145 + 109 | same | control only |
| Indus seals | 1,629 (dev 1,240 / held-out 391, v2) | `functional_reading/readings.csv` | coarse: OPEN, CONN, CORE (numerals, fish, nouns), TITLE, CLOSER (jar + bracketed fish), POST |

- **Annotation.** Rule-based, word level. Relators come from closed lists (kišib, dumu/dumu-munus/dam, arad/arad2/geme2 incl. arad2-zu). Titles come from a seeded list extended from the data: words that are never initial and not name-like. Owner is the first word, father follows dumu, lord follows arad. A hand audit of 70 random legends found about 5% of Ur III and 13% of OB legends with at least one mis-slotted word. Typical errors: OB co-owner deity after u3, and multi-word names split into TITLE.
- **Not done:** Egyptian Middle Kingdom scarabs, Linear B sealings, Linear Elamite and BMAC seals. The open data at hand (TLA sentences, 80 Linear B labels, 258 Linear A labels) has no seal corpus with slot structure big enough to fingerprint (at least 30 runs per slot at Indus size). This is listed under next experiments.

## Method

- **Fingerprint.** A slot run is a maximal stretch of same-slot tokens. Each slot gets 15 label-free features, which never look at sign identity, only at equality between tokens:
  - how often it occurs, mean position, share first, share last;
  - filler length, type-token ratio and entropy at 100 runs, top-filler share, Zipf slope;
  - retention on short (1-2 slot) legends, recursion, shared units with other slots, standalone share;
  - maximum and minimum co-occurrence lift.
- **Standardisation.** z-scores with means and SDs frozen from cuneiform slots only.
- **Alignment.** References are averaged over 20 subsamples cut to the Indus split size, then Hungarian matching.
- **Tests.**
  - Global: a column-permutation null (each feature permuted among Indus slots, 2,000 draws).
  - Stability: 100 bootstraps.
  - Acceptance threshold tau = 0.803: the distance below which 80% of control matches are correct.
- **Decision rule (pre-registered).** A mapping is *supported* if all five hold: global p<0.05, dev bootstrap ≥0.70, distance < tau, held-out bootstrap ≥0.50, and reference slot reliability ≥0.75. It is *suggestive* if the distance or reliability test fails.

## Findings with numbers

### Global alignment (Indus slots vs feature-permuted slots)
| | Ur III | OB |
|---|---|---|
| dev mean distance (null) | 1.119 (1.236), p = 0.0085 | 1.027 (1.220), p = 0.0005 |
| held-out | 1.199 (1.302), p = 0.0115 | 1.099 (1.280), p = 0.0005 |

The structure is non-random against OB on both splits; OB survives Bonferroni (0.05/13 = 0.0038), Ur III does not. These p-values only show that Indus slots differ from one another in seal-like ways. They do not show that any particular pairing is right.

### Pre-registered predictions
| id | prediction | Ur III result | OB result | verdict |
|---|---|---|---|---|
| P1 | CLOSER = servant-of | → FATHER (boot 0.59, SERV 0.22), d 1.15; held-out → TITLE 0.56 | → LORD (0.99), d 1.07 | **not supported** (both) |
| P2 | CORE = owner name | → TITLE (0.78), d 2.32 | → OWNER (1.00 / 1.00), d 1.84 | Ur III no; OB suggestive |
| P3 | TITLE = title | → LORD (0.65) | → TITLE (0.99 / 0.91), d 0.79 | Ur III no; OB suggestive (title not transferable) |
| P4 | CONN = kinship relator | → KIN (1.00 / 1.00), d 0.50 / 0.73 | → KIN (1.00 / 0.95), d 0.64 / 0.66 | **supported** (both) |
| P5 | OPEN = "seal of" | (no slot) | → SEAL_OF (1.00 / 0.98), d 1.04 | suggestive |

With the "leave unmatched" option at cost tau, only CONN→KIN is accepted in both references and both splits (plus OB TITLE→TITLE). The Indus core is far from every reference slot (d 1.8-2.8). It is longer (mean 2.2 signs per run vs about 1.0), recursive (23% of texts have two core runs vs about 1%), and its units rarely appear elsewhere (16% vs 34-57%). These differences fit the typology result that name cores are compounds of word signs, unlike syllabically spelt Sumerian/Akkadian names.

### Controls
- **C1 gold to gold at Indus size, 40 reps.** Ur III→OB 0.53, OB→Ur III 0.53, Ur III→OAkk+OA 0.85, random 0.11. The column-permutation p is <0.001. Correct pairs have median distance 1.02, wrong pairs 1.51.
- **C2 planted blind control** (Ur III words relabelled, slots induced by positional clustering, aligned to gold OB). Classes get the correct meaning 0.28 / 0.31 / 0.35 of the time at k = 4 / 6 / 8 (random 0.11; class purity 0.44-0.57). The method only transfers meaning when the slots themselves are good.
- **Exploratory blind Indus classes** (same inducer, no grammar labels) align to Ur III no better than chance (p = 0.15) and to OB only weakly (p = 0.037). Any positive result therefore leans on the functional-reading slot labels.

### Exploratory robustness
- **Leave-one-feature-out survival.** CONN→KIN 15/15 in every condition. OB pairs 0.93-1.00. Ur III pairs other than CONN 0.33-0.93.
- **Short legends.** 38% of Indus seal texts have only 1-2 slot runs (Ur III 7%, OB 30%). On those, the Indus closer is present 53% of the time and the connective 0%. In Ur III/OB, dumu and arad are 0%, the Ur III title 72%, OB kišib 66%.
- **Fine Indus slots (dev).** The connective still matches KIN in both references. Numerals map to TITLE in both: by distribution, number-names behave like a shared title/epithet slot. Fish maps to LORD/FATHER, unstable.

## Hypotheses tested
| hypothesis | verdict | key number |
|---|---|---|
| Indus closer = "servant of" (arad) | **refuted as stated** | 0.22 (Ur III) and 0.01 (OB) of bootstraps; d > tau |
| Closer = genitive-like relator (dumu-type) | not supported | closer survives on short seals (53% vs 0%) |
| Closer = title / ownership marker | inconclusive (exploratory lead) | nearest without position: Ur III TITLE 0.76-0.97; OB SEAL_OF 1.02 |
| Connective = closed relator word, dumu-like | **supported** (as a distributional class) | boot 0.95-1.00, d 0.50-0.73 < 0.80, both references, held-out |
| Indus core = owner-name slot | suggestive (OB only) | boot 1.00, but d 1.84-2.08 |
| Opener = kišib "seal of" | suggestive (OB only) | boot 0.98-1.00, d 1.04-1.16; opener rare on short seals (10% vs 66%) |
| Method transfers slot meaning between known cultures | supported for relators and names only | C1 53-85% vs 11% |

Tests: 13 pre-registered (4 global, 9 pairs), plus controls and about 10 exploratory comparisons.

## Caveats
- The Indus slots are the output of another team's grammar. CONN is defined as "the sign right after an opener", so part of its dumu-like profile (never first, never on short seals) is built in. The clean result is that the grammar's connective has the fingerprint of a relator word; whether M99 is a word at all is not decided here.
- The references are one family (Mesopotamian, Sumerian/Akkadian). A match means "distributed like the Mesopotamian slot", not a universal meaning.
- The annotation is rule-based, with roughly 5-13% of legends partly mis-slotted, and OB LORD/EPITHET boundaries are noisy.
- The connective → KIN match would be produced by any closed one-sign medial relator. The method cannot tell "son of" from "of" or "and".

## Next experiments
1. Add non-Mesopotamian seal genres with slot structure: Egyptian Middle Kingdom scarab name seals (title + name; Martin 1971, Ben-Tor), Linear B sealings (Wa- series), Linear Elamite / Gulf seals, Proto-Elamite seal legends. This would test whether "relator = medial closed word" and "closer survives on short legends" hold across genres.
2. Improve the Indus slots without the grammar. Blind induction is the bottleneck: C2 reaches only 0.28-0.35.
3. Test the closer = title/ownership lead directly. If the jar marks ownership, it should be rarer on seals whose legend is a bare title block, and commoner on tablets that name an owner. Pre-register this before looking.
