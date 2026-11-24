# anchor_ceiling: how much semantic-field structure can non-textual anchors recover at Indus size? (sealed before the ground truth and kill test)

Agent `paper`. Main line (b). Fable's study 3; design drafted by Fable on 2026-11-24, then revised after a fresh Fable review (9 fixes applied).
- **Stand-in:** Linear B (DAMOS, `experiments/meaning_calibration/load.py`).
- **Draws:** 5 draws of 1,680 dev + 565 held-out documents, on the same random stream as `fcore.draw` (seed `fcore.SEED0` = 20261124).

## Anchors (rungs, cumulative)
| rung | anchor | Indus counterpart | comparison |
|---|---|---|---|
| A1 | site (KN/PY/TH/MY/…) | Indus site | weaker: 67% of a draw is Knossos |
| A2 | + object class (tablet/sealing/vase) | seal/tablet/pottery/copper | much weaker: 96% tablets, about 62 sealings and 10 vases per draw |
| **A3** (primary) | + picture: the first ideogram on the document (measure signs S, T, V, Z, M, N, P, Q, numerals and adjuncts are never ideograms), collapsed to OVIS, GRA, VIR, MUL, OLE, TELA, LANA, SA, other or none | animal on seals | stronger, because the ideogram is the thing counted. **A3 is an upper bound.** |
| A4 (reported only) | + scribal hand (heading bracket, known for about 87%) | find-spot or carver | — |

- **Never an anchor:** the series prefix, which is a modern content label.
- **Indus has anchors Linear B lacks:** locus and richer object classes.

## Leak rule
- The text is the hyphenated syllabic words only.
- Ideograms, ligatures, measures, numerals and one-sign adjuncts are dropped from the text, and so is quoted `ZE`.
- Half-bracket marks ⌞ ⌟ are stripped before words are matched.

## Units (measured before sealing)
- **Eligible words:** in ≥ 5 dev documents. After half brackets are stripped (`core.word_of`), that gives 79-84 per draw, 92 in the union and 69 in all five. The draft's 77-82 / 90 / 68 came before the stripping.
- **Scored on held-out:** eligible words with ≥ 2 held-out documents, 46-56 per draw.
- **Disclosure:** the designer saw draw 0's eligible word list and ideogram totals, but no word × anchor count.

## Ground truth (frozen and hashed before any word × anchor count)
- **Labellers.** Two fresh agents, each with no repo access beyond the word list. Each gets the 92 union words, alphabetically, with no counts.
- **Fields.** Each labels each word by lexicon and etymology (Documents, DMic), not by the commodity its tablets usually record, into one of:
  - place or ethnic name;
  - personal name;
  - person class or occupation;
  - livestock;
  - textile or wool;
  - land tenure or grain;
  - made goods (vessel, chariot, arms);
  - administrative or transaction word;
  - religious;
  - unknown.
- **Kept words:** both labellers agree, and neither says unknown. Cohen's κ must be ≥ 0.6; otherwise the study stops.
- **Small fields:** a field with fewer than 4 kept words merges into "other", which is not scored.
- **Fewer than 3 held-out words:** in a given draw, a field is scored only if it has at least 3 held-out words.
- **Stop rule:** the study stops if fewer than 4 fields are scored.
- **Order:** the truth is frozen and hashed **before the kill test**, because labelling needs no counts.
- **Scoring is lexical,** not by document topic. A place name that clusters with sheep counts as a miss. Scoring by topic would be nearly circular with the picture anchor.

## Blind method
- **Profiles.** On dev, each word gets a profile: for each anchor value, the share of its documents carrying it, as a log-ratio to the base rate (add-0.5 smoothing).
- **Clusters.** All eligible words are clustered, with average-link clustering on cosine distance (scipy). k = scored fields + 1, a mild oracle stated here.
- **Scoring words.** The adjusted Rand index is computed on kept (labelled, scored) words only.
- **Ties.** Hungarian-matching and centroid ties break alphabetically.
- **Held-out.** Each word's held-out profile goes to the nearest dev centroid.

## Measures
- **Primary:** adjusted Rand index of the held-out assignments against the ground truth at A3, median over 5 draws.
- **Null:** 1,000 permutations of field labels within word-frequency bins.
- **A field is recovered** if its best-matched cluster (Hungarian matching) has F1 ≥ 0.5 and beats the null's 95th percentile in ≥ 4 of 5 draws.
- **Ceiling:** the share of scored fields recovered, plus the share of eligible word tokens they hold, for each rung.
- **Secondary:** same-field against different-field pair AUC on dev.
- **Supervised control (method-failure check):** leave-one-word-out nearest field centroid on dev, with the same null and the same recovered rule.

## Kill test, run first
- **Plant.** The texts are never edited.
  - Eligible words are given random fields at the real field sizes.
  - Document pictures are relabelled so that each field's documents carry that field's own anchor value, at strength 1.0, 0.6 and 0.3.
  - 20 plants per draw.
  - **Bar:** at strength 1.0, adjusted Rand ≥ 0.8, with every field recovered in ≥ 80% of plants. The smallest strength with power ≥ 0.8 is reported.
  - Plants use the real field sizes and the real k, from the frozen truth.
  - **Plant rule.**
    - A document takes the planted value of one of its eligible words, chosen uniformly.
    - With probability equal to the strength, it carries that value; otherwise it keeps its own picture.
    - Dev and held-out are both planted.
    - Documents with no eligible word keep their picture.
- **Null corpus.** Run for each rung, shuffling only that rung's added anchor across documents, 200 times. "Any field recovered" must happen in ≤ 5% of them.
- **If either fails, the study stops:** "the method cannot see a perfect tie at Indus size". There is no real run.

## What each outcome means (frozen)
- **Bands are stated as counts:** recovered fields out of scored fields.
- **High (A3 recovers ≥ 50% of fields):**
  - Next main-line (b) study: the same profile clustering on Indus signs (M77/ICIT: site, object, animal).
  - It is read as an upper bound, since Indus's real sign-animal tie is about +2 points (`animal_tie_power`).
  - A high result licenses the Indus run only. It supports no Indus claim.
- **Middle (20-50%):**
  - Only the recovered field kinds are pursued in Indus.
  - The rest are marked "not reachable by anchors".
- **"A3 no better than A2"** means: no more fields recovered, and a median adjusted Rand difference ≤ 0.
- **Low (< 20%, or A3 no better than A2):**
  - Anchors cannot deliver L2 at Indus size, even with a commodity picture.
  - Main line (b) falls back to function (L1), and the scorecard's field rows become "untestable by anchors" through a sealed addendum.
  - This reads "anchors cannot" only if the supervised control also fails. Otherwise it reads "blind clustering fails".
  - Either way, the claim is capped at "no tie at or above the kill test's smallest powered strength".
- **A2 alone ≥ 20%** (and A2's own null passed): site and object carry field information without pictures, the case closest to Indus.

## Limits
- One script, accounting genre; the draws resample one corpus.
- Topic contamination: a word's profile reflects its document's topic.
- Any two draws share 87-88% of documents, so "≥ 4 of 5 draws" is a stability check, not replication.
- Livestock and textile glosses partly derive from ideogram context in the scholarship. The labellers are told to use lexicon and etymology.

## Code plan (`experiments/anchor_ceiling/`)
- **`core.py`:**
  - `draw_docs(k)`, which reproduces `fcore.draw` exactly (checked) but returns document dicts;
  - `profiles`, `cluster`, `score`.
- **`words.py`** writes `truth/words.txt` and checks `draw_docs` against `fcore.draw` (passed for all 5 draws).
- **Word and ideogram rules:** as in the `core.py` docstring.
- **`truth/`:** `words.txt`, `labels_A.json`, `labels_B.json`.
- **Scripts:**
  - `kill.py` writes `kill.json`.
  - `run.py` writes `result.json`. It refuses to run unless `kill.json` passed and the truth files are hashed.
