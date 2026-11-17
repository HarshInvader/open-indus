# Phonetic grid (automated Kober triplets + Ventris grid)

## Conclusion first

1. **The method has real power only in easy cases.** On a regular synthetic CV language with fused case endings, it recovers the hidden consonant rows well (ARI 0.86 at 2,300 texts) and still works at 300 texts and with 50% logograms. It breaks once 75% or more of texts belong to no inflectional paradigm. On **real Linear B** it is weak at every size we could test: ARI 0.13 ± 0.06 for 2,300 word forms, and 0.09 for tablet lines with no word dividers. Its alternation edges are only 1.4× (words) to 3× (lines) more likely than chance to join same-consonant signs. **Vowel columns are not recovered from paradigms.** What survives is the bigram between the bridge sign and the ending, and that also survives a shuffle.
2. **Indus shows more end and start alternation than a frequency-matched shuffle, but none of the structure that inflection produces.** The extra alternation replicates on held-out texts and in the ICIT transcription. But the Indus alternation graph is no more clustered than its shuffle (modularity z = −0.04 at the end, +0.1 at the start). The suffixing controls give z = +7 to +15. Real Linear B gives only +2.1 as word lists and +0.6 as lines, so the test cannot rule out a Linear-B-like system written as noisily as Linear B lines.
3. **No grid is stable.** Harappa vs Mohenjo-daro partitions: ARI 0.06 (null 0.03, p = 0.35). Strong dev alternation edges come back in held-out texts 2.8% of the time, against 3.7% under the null. Every control replicates at the same size, including the one with no morphology.
4. **Suffixing vs prefixing: inconclusive.** Alternation at the start is at least as strong as at the end. It comes from openers (M267, M391, M293-M123) swapping in front of the same continuation, which is substitution of whole words, not morphology. The only suffix-like behaviour is optional elements after the closer (M176, M1). Munda nominal case is also suffixing, so even that does not separate the candidate languages. **Evidence strength: weak.**
5. **Connectives.**
   - **M99** never alternates and is never dropped (0 of 115 held-out uses vs a 5.5% peer rate). It is the fixed closing member of the opener units M267-M99 and M391-M99, not an ending that varies with its stem.
   - **M267** is a word that starts the text.
   - **M176** is an optional element after the closer, the most suffix- or clitic-like sign (droppable in 15% of dev uses and 23% of held-out uses vs 5.5% for peers).
   - **M59** (fish) is an ordinary open-class sign.

This confirms and extends the corrected F23 in `sources/shaunmortal_indus/STATE.md` (end alternation 1.09× chance, "Kober's grid method cannot get traction") and paragorth S1 ("no inflection grid"). What is new here is the planted-answer power analysis, which shows *why* a negative result is only moderately informative.

---

## 1. Controls (the method's power)

### Method (`grid_lib.py`; settings frozen on controls only)
- **Kober pair:** two distinct texts that share a stem of at least 2 signs, then diverge at a "bridge" sign, with at most 1 sign after it.
- **Consonant graph:** an edge joins two bridge signs, weighted by how many stems they alternate on. Rows come from spectral clustering (with K set to the true number, for scoring the controls only) or from Louvain clustering, which needs no K.
- **Vowel columns:** clustering of each bridge sign's profile of following tail signs, with a cannot-link penalty for signs in the same row.
- **Settings:** chosen from 24 combinations (stem length 2 or 3 × tail 0, 1 or 2 × 4 weighting schemes) by mean ARI × coverage over four controls. The best was stem ≥ 2, tail ≤ 1, count weighting (`out/controls.json` → `stage1`).

### Control corpora (`corpora.py`)
Every sign is replaced by a random ID; the true consonant and vowel of each syllabogram are kept hidden for scoring.
- **Linear B words:** real, from DAMOS (via `sources/paragorth_Indus-/.../damos_items.jsonl`). 3,676 distinct complete word forms; mean 3.7 signs.
- **Linear B lines:** distinct tablet lines with word dividers removed, ideograms kept as logograms (16% of tokens) and numerals dropped. 1,200 lines, 5.8 signs.
- **Synthetic:** a CV language. Consonant-final name stems take vowel-initial case endings, as in Ventris's ko-no-SO / ko-no-SI-jo. Names are drawn with Zipf frequencies, and texts look like [title] name+case [title].
- **Dravidian-like:** real Malayalam lemmas with Malayalam case suffixes and sandhi, written in akshara (virama for final consonants).
- **Synthetic, prefixing:** vowel-initial stems with consonant prefixes.
- **Synthetic, no morphology:** names and titles only, no case endings.

The Japanese and Tamil name lists in the brief were not built; the Dravidian-like corpus stands in for them.

### Main table (2,300 texts unless noted; mean of 5 seeds)

| Control | ARI rows (true K) | ARI rows (Louvain) | ARI vowels | Coverage | Edge precision / chance | Same method on shuffled copy (ARI rows) |
|---|---|---|---|---|---|---|
| Synthetic suffixing | **0.86 ± 0.07** | 0.47 | 0.54 | 0.92 | 0.35 / 0.07 | −0.01 |
| Dravidian-like | 0.38 ± 0.07 | 0.23 | 0.08 | 0.60 | 0.40 / 0.03 | 0.01 |
| **Linear B words (real)** | **0.13 ± 0.06** | 0.13 | 0.04 | 0.99 | 0.087 / 0.063 | 0.01 |
| **Linear B lines (real, 1,200)** | **0.09 ± 0.01** | 0.07 | 0.03 | 0.76 | 0.20 / 0.07 | −0.02 |
| Synthetic prefixing (run on the start) | ≈0 (rows vs vowels 0.11) | – | – | 0.96 | – | – |
| Synthetic, no morphology | −0.01 | 0.00 | 0.00 | 0.87 | 0.067 / 0.068 | 0.00 |

- The strongest real Linear B edges are true Ventris pairs: jo~ja (64 stems), ta~te, to~ta, we~wo, ra~ro, na~no, ko~ka. Edges seen on ≥ 5 stems are 15.5% same-consonant, vs 6.6% by chance (22% with tail = 0). Short stems shared by unrelated words supply the noise.
- On a block-shuffled copy, vowel ARI stays at 0.24 for the synthetic corpus. The vowel step therefore reflects bridge→ending co-occurrence, not paradigm alternation, and we did not apply it to Indus.

### Where the method stops working (`out/controls.json` stage3, `out/sweep_noise.json`, `out/sweep_nocomplement.json`)
- **Corpus size (synthetic, regular):** ARI rows 0.58–0.74 already at 300 texts (coverage 0.2–0.5), and 0.72–0.97 at 2,300–4,600 (Zipf ≤ 1.0). Size is not the limit for a regular language.
- **Logograms:** when a logogram stem keeps its spelled ending (phonetic complement), there is no breakdown up to 50% logogram tokens (ARI 0.47–0.94 for N ≥ 600). When whole words are logograms, Linear B breaks:
  - at 500 words with 30% logograms: ARI −0.03, edge precision below chance (0.04 vs 0.06);
  - at 2,300 words with 50% logograms: ARI 0.07.
- **Share of texts in no paradigm (the real limit), at Indus dev size of 1,317 texts:**

| Non-paradigm texts | 0% | 25% | 50% | 75% | 90% |
|---|---|---|---|---|---|
| ARI rows, no logograms | 0.76 | 0.60 | 0.26 | 0.03 | 0.00 |
| ARI rows, 30% logograms | 0.59 | 0.46 | 0.10 | 0.00 | 0.00 |
| End modularity z vs shuffle (30% logograms) | 7.4 | 8.2 | 4.0 | **−0.03** | −1.9 |

  With 75% non-paradigm texts, the extra alternation is still there (z 4.4) but modularity is gone (z ≈ 0). That is exactly the Indus profile.
- **Corpus size (real Linear B words):** ARI 0.08 at 500 words, 0.11 at 1,000, 0.17 at 2,300 and 0.17 at 3,676 (0.29 with the full 3,676 and one seed). It never reaches the synthetic level.

**Bottom line:** at Indus size, a grid becomes detectable only if about half or more of the texts are inflected members of shared paradigms in a fairly regular CV spelling. Real Linear B sits at the edge of detectability.

---

## 2. Indus result (dev = 1,317 complete distinct M77 texts, mean 4.74 signs)

Inputs: distinct texts, no `#` breaks, line breaks joined. Held-out: 437 texts. ICIT: 2,184 complete distinct texts, with W signs mapped to M numbers through `bridge_WM.json`.

### 2a. Alternation vs nulls (200 permutations; bigram null 100)
The **block** null permutes the bridge+tail block among texts of the same length: it keeps the endings and breaks the link between stem and ending.

| Corpus / end of text | Alternating stems: obs vs block null | Triplets: obs vs null | Modularity vs block null | Alternating stems vs bigram null |
|---|---|---|---|---|
| dev, end | 79 vs 62.2 (1.27×, z 5.1) | 26 vs 16.9 (z 5.9) | 0.391 vs 0.393 (**z −0.04**) | 79 vs 84.1 (z −0.7) |
| dev, start | 133 vs 102.8 (1.29×, z 6.6) | 52 vs 37.9 (z 5.2) | 0.390 vs 0.387 (z 0.1) | 133 vs 93.5 (z 5.6) |
| held-out, end | 19 vs 12.6 (z 4.7) | 4 vs 2.1 | 0.45 vs 0.39 (z 0.8) | z −0.8 |
| held-out, start | 34 vs 21.1 (z 7.0) | 8 vs 5.0 | z 0.5 | z 2.8 |
| ICIT, end | 125 vs 100.6 (z 4.9) | 41 vs 33.1 | z −0.5 | z −1.3 |
| ICIT, start | 202 vs 172.4 (z 5.0) | 84 vs 59.5 | z 3.1 | z 5.9 |

The same statistics on controls at Indus size (1,317 texts; Linear B lines 1,200):

| Control | End alternation z | End modularity z | Start alternation z | Start modularity z |
|---|---|---|---|---|
| Synthetic suffixing, no logograms | 13.9 | 15.5 | 0.4 | 0.7 |
| Synthetic suffixing, 30% logograms | 11.8 | 6.9 | 1.0 | 8.3 |
| Dravidian-like | 14.7 | 9.0 | 3.4 | 2.7 |
| Synthetic prefixing | 3.1 | 13.9 | 11.7 | 12.1 |
| Linear B words | 7.2 | 2.1 | 6.2 | −0.6 |
| Linear B lines | 7.0 | 0.6 | 4.7 | 0.4 |
| No morphology (preposed titles) | −1.2 | −0.3 | 3.0 | 3.3 |
| **Indus dev** | **5.1** | **−0.04** | **6.6** | **0.1** |

- **Other nulls (reported for transparency).** Against the final-sign-only shuffle (the F23 null), dev end alternation is *below* chance (79 vs 87.5). Modularity is above that null (z 4.35) but equal to the block null. The clustering therefore comes from which signs may follow which inside the ending block, not from stem–ending pairing.
- **Multiple comparisons.** 48 alternation tests; Bonferroni α = 0.001, using normal-approximation p values because the permutation floor is 0.005. Survivors:
  - extra alternation vs the block null, in all four corpora and both directions;
  - start alternation vs the bigram null (dev, dev with incomplete texts, ICIT);
  - dev end modularity vs the final-sign null;
  - ICIT start modularity.
  - No end-modularity test against the block null survives in any corpus.
- **Where the alternation comes from.**
  - The largest Kober "families" are opener formulae followed by an open slot. M267-M99 is followed by 20 different signs (M102, M104, M59, M65, M86, …), M391-M99 by 11, and M293-M123-M343 by 7. Kober triplets have 2–4 alternants.
  - The Louvain "rows" mirror these formulae. One community holds what follows M267-M99, another what follows M391-M99 and M293-M123-M343. A third is a closer block (M342, M211, M347, M169, M162, M15, …) and a fourth a post-closer block (M176, M12, M1, M328, M130, M375).
  - These groups reflect position in the text (slots), not shared sounds.

### 2b. Grid stability
| Test | Indus | Null | Controls at the same size |
|---|---|---|---|
| Bootstrap ARI to the full partition | 0.55 (95% CI 0.31–0.80) | 0.45 ± 0.02 (block-shuffled) | Linear B 0.24, synthetic 0.58, no-morph 0.41: **not diagnostic** |
| Harappa (458) vs Mohenjo-daro (1,081), ARI | 0.058 (17 shared signs) | 0.033, p = 0.35 | – |
| Same, strong-edge replication | 12.5% | 10.8% (z 0.4) | – |
| Dev → held-out, ARI | 0.138 (19 shared signs) | 0.033, p = 0.16 | – |
| Dev → held-out, strong-edge replication | **1 of 36 (2.8%)** | 3.7% | – |
| Random halves of dev (×5) | ARI 0.125; edges 0.31 vs 0.20 (z 0.2; about 4 strong edges per half) | – | Linear B halves 0.53 vs 0.20 (z 3.4); Dravidian 0.65 vs 0.14; no-morph 0.50 vs 0.22 |
| Dev → ICIT | ARI 0.27, edges 0.75 vs 0.46 (z 3.1) | – | Not independent: largely the same objects transcribed again. It shows the alternations are robust to transcription, not to new texts. |

### 2c. Which signs behave like grammatical suffixes?
Ranking by final-position share × end-alternation degree:

| Sign | Final share | End alternation degree |
|---|---|---|
| M342 | 0.69 | 32 |
| M211 | 0.82 | 13 |
| M176 | 0.79 | 10 |
| M12 | 0.89 | 4 |
| M169 | 0.62 | 5 |
| M15 | 0.71 | 3 |
| M162 | 0.40 | 5 |
| M1 | 0.75 | 1 |

This is the known closed closer set plus the post-closer signs (F23; paragorth S17/S24). They alternate with each other as a small set at the end of the text, which is the only Linear-B-like feature. But they do not split into phonetic rows, and the alternation edges do not replicate.

A calibration corpus has known suffix signs (case markers, one sign each, nominative = no sign) and known word signs (`corpora.synthetic_agglut`). There, true suffix signs show:
- final position 68% of the time;
- droppable 25% of the time (the no-ending form exists);
- 34 substitution partners;
- more variety before them than after (2.4 bits more on the left; 5.4 vs 2.4 bits);
- they never occur in both orders with the same neighbour.

**Only M176, and more weakly M1 and M12, fit this profile** (2d).

### 2d. Connectives (dev; peers = signs of similar frequency in the same dominant slot)

| Sign | Position (initial / middle / final) | Droppable: dev (peers) | Droppable: held-out vs all M77 (peer mean 5.5%, 95th pct 20.9%) | Substitution partners (peers) | Variety before / after (bits) | Main left neighbours |
|---|---|---|---|---|---|---|
| **M99** | 0.00 / 0.99 / 0.01 | 0.3% (4.0%) | **0 / 115** (binomial p ≈ 0.002) | 1 (7.6) | 3.8 / **5.6** (peers 3.6 / 2.9) | M267 139, M391 60 of 336 (59%; held-out 58%) |
| **M267** | 0.78 / 0.20 / 0.03 | 0.6% (3.9%) | 0 / 71 | 5 (6.9) | 1.9 / 1.2 | text start 135; followed by M99 in 80% |
| **M176** | 0.00 / 0.21 / 0.79 | **14.7% (2.8%, z +4.6)** | **9 / 39 = 23%** | 5 (6.1) | 4.2 / 1.4 | M342 51, M15 9, M211 6 (52 types) |
| **M59** | 0.11 / 0.88 / 0.02 | 3.8% (3.4%) | 2 / 45 | 19 (6.0, z +2.4) | 3.9 / 5.1 | M87 43, M171 30 |
| M1 (for comparison) | 0.05 / 0.20 / 0.75 | 16.7% (2.1%) | 1 / 17 | 0 | 1.3 / 1.5 | M342 48 of 60 |

- **M99 does not behave like an inflection of the preceding unit in the Kober sense.** It has no paradigm partners, is never dropped and has zero end alternation. It is tied to a few preceding signs (59% are the openers M267/M391) and opens onto an open class (86 different followers). That makes it the invariant final part of a fixed opener unit ("M267-M99", "M391-M99"). If it is grammatical, it is a single invariant marker welded to its host. It is not a separate free word either: it never stands alone and is never optional. Replicated on held-out and ICIT (still 97% middle; 58% after M267/M391; held-out drop rate 0%).
- **M267** is a word at the start of the text: 78% initial, so nothing precedes it to inflect. It alternates only with other openers (the start alternation).
- **M176 behaves most like a bound postposed element** (suffix or clitic) of the preceding unit. It is final, follows many different signs, is followed by few, is optional, and alternates with a small set (M12, M1, closers). Optionality replicates on held-out (23%, above the peers' 95th percentile). Caveat: paragorth S24/S29 found M176 five times more common on sealings, tablets and rods than on seals, so it may mark the kind of document rather than grammar.
- **M59** (fish) is the most freely substituting sign: 37 end alternation partners and 19 substitution partners. It is not droppable more often than peers. That is an open-class item, not a connective.

---

## Hypotheses tested

| # | Hypothesis | Verdict | Key number |
|---|---|---|---|
| C1 | The method recovers a planted consonant grid | Supported for regular synthetic; **weak for real Linear B** | ARI 0.86 vs 0.13 / 0.09 |
| C2 | It recovers vowel columns from paradigms | Refuted (the signal survives shuffling) | Shuffled synthetic vowel ARI 0.24 |
| I1 | Indus has more final alternation than a frequency-matched shuffle | Supported vs block null, replicated; **explained by a bigram model** | 1.27×, z 5.1; bigram z −0.7 |
| I2 | The alternation is structured like inflection (rows) | Not detected; refuted vs regular suffixing, inconclusive vs Linear-B-level noise | Modularity z −0.04 (controls +2 to +15) |
| I3 | A stable consonant × vowel grid exists | Refuted | Harappa vs Mohenjo-daro ARI 0.06 (p 0.35); held-out edges 2.8% vs 3.7% |
| I4 | The morphology is suffixing rather than prefixing | Inconclusive (start ≥ end; neither side morphological) | End z 5.1, start z 6.6, modularity ≈ 0 on both |
| I5 | M99 is an alternating inflection of the preceding unit | Refuted: invariant, bound to the opener | Dropped 0 of 115 held-out; 1 partner |
| I6 | M267 is an inflection | Refuted: an initial unit | 78% initial |
| I7 | M176 is a bound optional postposed element | Supported, weak to moderate | Droppable 15% / 23% vs 5.5% |
| I8 | M59 is a connective or inflection | Refuted | Peer-level drop rate; most substitutable sign |

About 60 formal tests in total: 48 alternation tests, 8 split statistics and held-out drop rates. Peer z scores are descriptive.

## Caveats and what would falsify this
- **Low ceiling on real data.** The method is weak on real Linear B, so "no grid in Indus" rules out only a regular, densely attested CV-fusional system. A Linear-B-like syllabary with endings in fewer than about half the texts, or a logo-syllabic system whose endings are mostly not written, would pass undetected.
- **Corpus framing.** Indus texts are mostly seal legends, short formulaic name and title strings (F27/F28). Recurring stems are formulae more than lexemes, which is the wrong material for Kober triplets.
- **Sign list.** Mahadevan's sign list matters: allograph splits such as M102/M103 or M161/M162 create false rows. The ICIT check helps only partly.
- **Falsifiers.**
  - End modularity above the block null (z > 3) in an independent new corpus (post-1977 sites).
  - Dev Kober edges replicating in new texts significantly above the null.
  - A Harappa/Mohenjo-daro row partition with ARI > 0.3.
  - Any of these would overturn the negative.

## Next experiments
1. Restrict Kober pairs to the middle of the text, between opener and closer formulae (the "individual" part, F29), so formula slots do not dominate the families.
2. Reduce noise in the real Linear B control the way Kober did, using tablet-series context (same series, same position), to see how far context restores power. If context is what made Linear B crackable, find the Indus analogue: same find-spot or same seal series.
3. Rerun with an allograph-merged sign list (STATE.md M2 merges) and on Wells v3.
4. Test M176 as a document-type marker vs a grammatical suffix, controlling for object type.

## Files
- `grid_lib.py`: the method and nulls.
- `corpora.py`: the planted-answer corpora.
- `controls.py`: parameter selection, main control table and power sweeps → `out/controls.json`.
- `sweep_noise.py`, `sweep_nocomplement.py`: breakdown sweeps → `out/sweep_noise.json`, `out/sweep_nocomplement.json`.
- `indus.py`: the Indus analysis → `out/indus.json`.
- `results.json`: the key numbers.
- Run order: `controls.py`, `sweep_*.py`, `indus.py`, all from the repo root with `.venv/bin/python`.
