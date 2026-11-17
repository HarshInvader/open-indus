# Red team of experiments/identifiers: the formula layer, core novelty, and the repulsion null

Pre-registered: `docs/prereg/redteam_identifiers.md` (hashed in `docs/prereg/HASHES.txt` before any check was run). Ledger rows `rt_id_c1b`, `rt_id_c1c`, `rt_id_c2`, `rt_id_c3` (family of 4) and `rt_id_x45` (exploratory). `experiments/identifiers/` was not edited; its `id_lib.py` and `s4.py` were imported read-only.

## Verdicts

| claim | verdict | key numbers |
|---|---|---|
| C1 "repeated seal texts are a short formula layer shared across cities at random" | **fails** | Short repeats are no more common than chance collisions under the script's own sign-pair grammar: 145 objects on repeated 1-3 sign texts vs 151 expected [129-174]. At equal length, Indus repeats are as local as Ur III ones: 0.51 vs 0.53. |
| C2 "seal cores are more novel than real personal names" | **fails as stated; a narrower version survives** | Build Ur III cores the same way as Indus cores and they are *more* novel: 0.96-0.995 vs 0.91-0.92. Against single Ur III names of the same length, Indus cores are more novel (2-4 signs: 0.75-0.99 vs 0.39-0.59). That gap is not caused by inventory size. |
| C3 "no identifier repulsion" | **fails (uninformative)** | Power is 0.03-0.07 against repulsion among small sets of true contemporaries. Ur III personal seals, a real identifier system, do not repel: within one archive and reign they *cluster* (z -9 to -15). |

**Honest restatement:** short seal texts collide, about as often as a bigram model of the script predicts, and they collide wherever seals are found. That is the whole "formula layer". The only repeats beyond chance are 4-5 sign texts (34 objects vs 8 expected). These stay local, just as Ur III repeats do. Nothing in S3/S4 separates Indus seals from a personal-identifier system once text length is matched.

## C1: chance collisions and length matching

**C1a, duplicate records.** 4 of 181 repeated objects (2%) could be double entries:
- 3 pairs at the same site where one object has no CISI number (Banawali, Dholavira ×2);
- 1 pair with the same site, emblem and size (H-352/H-354).

No CISI number appears twice among the seals. Dropping the 4 objects changes little: 173 objects on repeated texts, multi-site share 0.70. **Not inflated.**

**C1b, generative null (primary).** The test simulates 500 corpora that keep every seal's site and text length:
- **N2 (primary):** a global bigram model with exact length conditioning, fitted on distinct complete ICIT texts of all object classes.
- **N3:** a per-site bigram model, mixed 50/50 with the global one.
- **N1:** a positional unigram model (first, middle and last sign drawn separately).
- **N2x (robustness):** the bigram model refitted with every 1-3 sign seal text removed, so short seals cannot train their own collisions.

| statistic | observed | N1 positional | N2 bigram | N3 site bigram | N2x refit |
|---|---|---|---|---|---|
| objects on repeated 1-3 sign texts | 145 | 68 [52-85] | **151 [129-174]**, p≥ 0.71 | 147 [125-170] | 168 [145-190] |
| repeated 2-sign objects | 102 | 49 | 105 [88-123] | 103 | 115 |
| repeated 4-5 sign objects | 34 | 0 | 8 [2-16], p 0.002 | 8 | 11 |
| share of repeated texts at more than one site | 0.66 | 0.76 | 0.74 [0.64-0.85] | 0.67 [0.56-0.78] | 0.74 |

- The prereg rule gives **artefact**: the observed count is below N2's 97.5th percentile. Single-sign frequencies (N1) are not enough to produce the collisions; the bigram habits of the script are.
- Repeats are slightly *more* local than a global model predicts (0.66 vs 0.74). They match a model with site-specific grammar (0.67). "Shared across cities at random" is just what a shared grammar produces when short texts are drawn from it.

**C1c, length-matched locality.** This uses a leave-one-out version of identifiers' ratio R: hits at the reference site divided by the reference site's own leave-one-out match rate for texts of the same length, over all site pairs with at least 40 Indus seals or 100 Ur III seals.

| set | R_LOO (95% CI) |
|---|---|
| Indus, all lengths, unstratified | 0.45 (0.39-0.53) |
| Indus, identifiers' site pairs (MD and Harappa as reference) | 0.89 (0.73-1.07), which reproduces 0.89 |
| Indus, length-stratified | 0.52 (0.45-0.60) |
| Indus, ≤7 signs | **0.51 (0.43-0.59)** |
| Indus, 1-3 signs | 0.82 (0.68-0.96) |
| Indus, ≥4 signs | **0.18 (0.10-0.25)** |
| Ur III legends, all (median 10 written signs) | 0.18 (0.16-0.21) |
| Ur III legends ≤7 written signs (n = 754) | **0.53 (0.35-0.76)** |
| Ur III name lines (median 3 signs) | 0.52 (0.51-0.53) |

- The "0.89 vs 0.18" contrast compares mostly 2-4 sign Indus texts with 10-sign Ur III legends.
- At equal length the two systems match: 0.51 vs 0.53, and Indus 4+ sign texts are exactly as local as Ur III legends (0.18 vs 0.18).
- R also moves from 0.45 to 0.89 depending on which site pairs are used.
- Side note: identifiers' Chao-bootstrap CIs do not always contain their own point estimate (Ur III name R 0.51, CI 0.44-0.48), so that CI method is biased.

## C2: core novelty (new-text rate at m = 100 objects)
- **C2a, same recipe.** Indus frame signs make up 38.3% of seal tokens. Removing the 6 most frequent Ur III words, which also cover 38.3% of tokens (dumu, dub-sar, lugal, arad2-zu, kal-ga, uri5ki-ma), leaves an Ur III "core" with new rate **0.96-0.995** across 7 archives. The Indus core is 0.91-0.92.
  - Identifiers compared a multi-element Indus core with one Ur III name line, which is not like for like.
  - The prereg rule gives **fails**: the gap reverses.
- **C2b, length strata (written signs).**

  | core length | Indus pooled | Indus MD | Ur III name pooled | Ur III Umma |
  |---|---|---|---|---|
  | 2 | 0.75 | 0.77 | 0.43 | 0.39 |
  | 3 | 0.97 | 0.97 | 0.59 | 0.49 |
  | 4 | 0.99 | 0.99 | 0.57 | 0.41 |

  At equal length, Indus core strings are far more novel than single Ur III names.
- **C2c, inventory size.** Indus cores use 509 sign types (7.1 bits per sign); Ur III names use 443 (6.6 bits).
  - Quantile-mapping Ur III signs onto the Indus mass profile leaves name novelty unchanged to 3 decimals.
  - Unlike core_genre, this gap is **not** an inventory artefact.
- **Reading:** Indus cores behave like free combinations (name plus something), not like single entries from a stock of names. A whole Ur III legend minus its formula words behaves the same way, and is even more novel. So C2 cannot say "more novel than personal names" without saying which unit of the name is compared.

## C3: what the S4 null can detect
- **C3a, minimum detectable effect.** On nearest-neighbour edit distance (NN-NED) it is 2.5 null SD = 0.0094, or 1.5% relative.
  - Only 17% of units have a within-bin neighbour closer than NED 0.5.
  - The largest shift any NED<0.5 repulsion could cause is 0.028.
  - Two bins (MD Intermediate 247 units, MD Late 219) carry 61% of the weight.
- **C3b, repulsion among contemporaries.** Repulsion was planted only within random sets of h units inside each bin (strength 1.0; 30 reps × 200 permutations).
  - Power: **0.07 at h = 5, 0.03 at h = 10**.
  - The same code applied to the whole bin gives 0.90, matching identifiers' 0.83.
  - The test sees only repulsion that spans whole centuries-long bins.
- **C3c, real identifier positive control.** The same statistic and null A were run on Ur III personal seal legends, binned by archive + reign or archive + year.

  | data and bins | groups | NN-NED shift vs null | z |
  |---|---|---|---|
  | legends, by reign | 33 | -3.4% | -9.1 |
  | legends, by year | 199 | -4.7% | -15.2 |
  | name lines, by reign | 33 | -5.1% | -9.0 |
  | name lines, by year | 187 | -5.0% | -12.6 |

  - Real personal seals **cluster**: contemporaries share offices, patronyms and titles. They never repel.
  - "No repulsion" is therefore no evidence against identifiers.
  - Side note: Indus (-0.7%, z -1.1) is *less* clustered than Ur III, and a shift of Ur III's size would have been detectable (MDE 1.5%). Scripts, lengths and bins differ, so this is not a claim.

## Caveats
- The bigram nulls are fitted on the corpus they test. Each distinct text counts once, and N2x removes short seals entirely; it predicts *more* collisions (168), not fewer.
- Ur III sign counts come from transliteration: determinatives count as signs, and `-`/`.` split signs. CDLI seal ids are partly assigned by legend (identifiers' caveat), which makes Ur III look more unique.
- Ur III ≤7-sign legends: n = 754 across 7 archives, so the CI is wide (0.35-0.76).
- The C3c bins are capped at 250 legends. Ur III dating comes from the sealed tablet, which is the date of use.

## Next
- Treat the 4-5 sign repeats (the only excess over chance, and local) as the real duplicate set. Check whether they are the same die, the same owner, or the same workshop (emblem, size, CISI photos).
- Any new identifier test should use a comparator matched for text length and unit, and a positive control from a known identifier system. S3/S4 as built cannot separate identifiers from labels.

## Files
- Code: `c1.py` (C1a-c), `c2.py`, `c3.py` (`a`, `b5`, `b10`, `b1000`, `c`).
- Logs and data: `c1.log`, `c1.json`, `c2.log`, `c2.json`, `c3_*.log`, `c3_*.json`, `repeated_dump.txt`, `results.json`.
