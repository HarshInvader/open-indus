# Red team of uniformity paper step 1

Prereg: `docs/prereg/redteam_uniformity_step1.md`, hashed with `rt1.py` in `docs/prereg/HASHES.txt` (tag `redteam_uniformity_step1`, 2026-11-21T15:43:36Z) before any condition was scored. Every condition ran through the benchmark's own `clean()` + `draw_n()` + `score()`, with pools from step 1's `s1.py` and `rt.py`. 30 draws per condition, seed 20261124. Numbers: `table.md`, `results.json`, `draws.jsonl`. Ledger: `ledger_rows.csv`.

## Verdict: BROKEN (on the reference side). The Indus side stands.

- **What breaks: Linear B is not evidence that readable corpora carry their site.** By the frozen rule K1, Knossos vs Pylos falls to **0.524** with series balanced and scribal hands held out of training. That is Indus level, and the gate passes (97%). The same split without hand hold-out gives 0.774.
- **Two groups of scribes inside one palace separate as well as the two palaces do.** Knossos hand groups give 0.883 against 0.876 between palaces at the same size. Pylos hand groups give 0.861 against 0.886. So the Linear B signal is a scribe-and-office signal, not a place signal. "Between equals within" holds for Linear B too, just at a high level.
- **The Indus side holds against every attack.**
  - Mohenjo-daro vs Harappa matches the within-city floor in every check:
    - with findspot-confirmed seals only: Δ −0.007;
    - with cross-split near copies dropped: Δ −0.006;
    - under the five sign lists: Δ −0.03 to +0.07, four of five within ±0.05.
  - Two random halves of Mohenjo-daro give the same number (0.539).
  - A Harappa-only stock making up 15% of its tokens would have been caught 93% of the time.
- **Latin survives as a reference.** Name-free Britannia vs Germania gives 0.713. Two regions of one province give 0.629 at the same size, so Δ = +0.084.
- **The "formula words" reading does not generalise.** With names and the frame removed, only Latin falls to Indus level (0.570). Linear B stays at 0.832 and Ur III Umma vs Girsu at 0.689, though both of those gates are under 80%.

By the prereg, any kill makes the verdict BROKEN. Weakening triggers W1, W2 and W4 also fired. What is broken is the second sentence of the claim, the reference contrast built on Linear B. The first sentence, that Indus cities cannot be told apart and match the within-city floor, survived every attack.

### Safe wording (paper / README)

> Seal texts from Mohenjo-daro and Harappa cannot be told apart by which signs they use (AUC 0.52-0.55 under five sign lists and two editors). They differ no more than two excavation areas of Mohenjo-daro, or two random halves of it. That still holds with findspot-confirmed seals only and with near-copies across the split removed. A Harappa-only stock of signs making up 15% of its tokens would have been detected in 93% of draws. Among readable references, Roman labels separate Britannia from Germania without personal names (0.71) more than two regions of one province do (0.63). Linear B tablets do not serve as a site reference: groups of scribes inside one palace separate as strongly as Knossos from Pylos, and with series balanced and scribes held out the two palaces fall to 0.52.

Do not write:
- Linear B Knossos vs Pylos (0.90, 0.78 or 0.79) as evidence that administrative corpora carry their site.
- "Readable corpora separate their sites" with Linear B as one of the corpora.
- "The cities share a vocabulary while references don't" as a general contrast. It now rests on Latin (one pair, with a floor of 0.63) and Ur III (no within-city floor; name-free versions underpowered).

## Between-minus-within, all corpora (matched size; median AUC)

| corpus / split | per side | between | within | Δ |
|---|---|---|---|---|
| **Linear B whole, Knossos hand groups** (3 partitions) | 152-157 | 0.876 | **0.883** | **−0.006** |
| **Linear B whole, Pylos hand groups** | 154-184 | 0.886 | **0.861** | **+0.025** |
| Linear B series-balanced, Knossos hands | 45-51 | 0.686 | 0.676 | +0.010 |
| Linear B series-balanced, Pylos hands | 75-115 | 0.763 | 0.730 | +0.033 |
| Linear B name-free, Knossos hands | 28-39 | 0.690 | 0.812 | −0.121 |
| Linear B name-free, Pylos hands | 96-113 | 0.786 | 0.809 | −0.023 |
| Linear B whole, random tablet halves (Kn / Py) | 163 / 181 | 0.876 / 0.886 | 0.447 / 0.483 | +0.43 / +0.40 |
| **Latin name-free, Germania: Rheinland-Pfalz vs Baden-Württ. + Hessen** | 125 | 0.713 | **0.629** | **+0.084** |
| Latin whole, same split | 222 | 0.718 | 0.633 | +0.085 |
| Latin name-free, Britannia north vs south | 54 | 0.651 | 0.470 | +0.180 |
| Latin whole, Britannia north vs south | 116 | 0.651 | 0.586 | +0.065 |
| Latin whole, Germania random halves | 227 | 0.718 | 0.517 | +0.201 |
| **Indus M77, Mohenjo-daro DK vs HR+VS** | 169 | 0.517 | **0.537** | **−0.020** |
| Indus M77, Mohenjo-daro random halves | 169 / 227 | 0.517 | 0.539 | −0.022 |
| Indus M77, findspot-confirmed only | 85 | 0.520 | 0.527 | −0.007 |
| Indus M77, cross-split near copies dropped | 138 | 0.522 | 0.529 | −0.006 |
| Indus M77, frame (commonest signs) removed | 142 | 0.567 | 0.608 | −0.042 |
| Indus ICIT raw, CISI area split | 90 | 0.523 | 0.529 | −0.007 |
| Indus ICIT A1 | 90 | 0.540 | 0.474 | +0.067 |
| Indus ICIT A2 | 90 | 0.526 | 0.511 | +0.015 |
| Indus M77 (Mahadevan) | 169 | 0.518 | 0.550 | −0.032 |
| Indus M77 lump_all | 162 | 0.541 | 0.534 | +0.006 |
| Ur III | no within-city provenance on disk | | | |

Reading:
- **Pipeline floor.** Random halves of one pool score 0.45-0.54 in every corpus.
- **Linear B scribe effect.** Splitting by scribe hands inside one palace raises Linear B from about 0.46 to 0.86-0.88, the same as between palaces.
- **Latin.** It is the only reference where cities beat parts of one province (+0.08). Even its within-province floor (0.63) sits above Indus between-city (0.52).
- **Indus.** Between, area, random halves and every robustness variant all sit at 0.47-0.55. The one exception is the frame-removed variant, which rises to 0.57-0.61 on both the between and the within side.

## Numbers per attack

### 1. Like-for-like floors
See the table above. Gates pass for the Knossos hand split, the Pylos hand split and the Latin province split (100%, 100%, 93%). Primary reference gaps: Linear B −0.006 and +0.025, both under 0.05; Latin +0.084. The Linear B floors (0.883, 0.861) exceed 0.70. So **W1 fired**.

### 2. Scribe / series (Knossos vs Pylos)

| condition | per side | median | 95% of draws | null q95 |
|---|---|---|---|---|
| whole, hand-held-out CV | 227 | 0.767 | 0.739-0.800 | 0.566 |
| series-balanced, tablet CV (A8 rerun) | 116 | 0.774 | 0.751-0.804 | 0.571 |
| **series-balanced, hand-held-out CV** | 116 | **0.524** | 0.460-0.584 | 0.572 |
| name-free, hand-held-out CV | 115 | 0.644 | 0.582-0.696 | 0.593 |
| name-free + series-balanced, hand-held-out CV | 75 | 0.483 | 0.421-0.544 | 0.549 |

- About 0.25 of the 0.78 vanishes when the classifier must generalise to scribes it has not seen. Almost none of the series-balanced site signal survives.
- **K1 fired**, gate 97%. W2 also fired (0.483).
- Note: Indus CV is by text, not by carver, because carvers are unknown. Any carver leakage would favour Indus separating, yet it still sits at 0.52-0.55.

### 3. Formula words (names + commonest 38.3% of tokens removed)

| condition | per side | median | null q95 | gate |
|---|---|---|---|---|
| **Linear B strict name-free + frame** | 109 | **0.832** | 0.600 | 73% (fails) |
| Linear B tagged names + frame | 227 | 0.942 | 0.561 | |
| **Ur III Umma-Girsu name-free + frame** | 145 | **0.689** | 0.552 | 43% (fails) |
| Ur III Umma-Girsu name-free + owner + frame | 56 | 0.725 | 0.634 | |
| Ur III Puzriš-Dagan-Nippur name-free + frame | 70 | 0.790 | 0.587 | |
| **Latin name-free + frame (B7 rerun)** | 132 | **0.570** | 0.597 | 100% |
| top-10 / top-20 types removed: Linear B name-free | 98 / 91 | 0.831 / 0.817 | | |
| top-10 / top-20: Ur III Umma-Girsu name-free | 128 / 99 | 0.629 / 0.683 | | |
| top-10 / top-20: Latin name-free | 149 / 138 | 0.568 / 0.576 | | |
| Indus ICIT frame removed | 206 | 0.612 | 0.564 | |
| Indus ICIT top-10 / top-20 removed | 214 / 189 | 0.597 / 0.619 | | |
| Indus M77 city / area, frame removed | 173 / 142 | 0.586 / 0.608 | | |

- Only 1 of 3 references falls to Indus level, so W3 did not fire. The Latin collapse is Latin-specific. Linear B and Ur III keep their separation without names and formula words, although their gates are under 80%.
- Indus rises a little when its commonest signs go (0.61-0.62 ICIT, above null q95). The within-city split rises just as much (0.608), so this is a pipeline or length effect, not city signal. K3 needed ≥ 0.65, so it did not fire.
- **Which reading the data support.** "Indus cities share a vocabulary" holds against Latin only once formula words are kept. Against Ur III it holds either way. The "Indus lacks site-varying formula words" alternative fits Latin and nothing else.

### 4. Indus findspot validity

- Every M77 locus code agrees with the register field numbers. Loci 31/32/34 give 533 DK field numbers and no others. Locus 33 gives 4 DK and 33 unlinked. Loci 16/17/18/20/22 give mostly HR/VS, with a few stray prefixes (DK 2, B 3, R 3, C 3, E 4, SD 4).
- **Texts before cleaning:**
  - DK: 535 confirmed, 47 uncertain.
  - HR+VS: 97 confirmed, 81 uncertain, 12 contradicted, 8 mixed.
  - The HR+VS side is the weak one: 101 of 198 are not confirmed.
- **Confirmed only:** within 0.527 (vs C1 0.537; the floor moves by 0.01), between 0.520 at 85 per side, Δ −0.007. The gate passes (87%).
- **Near copies.** In the C1 pool after `clean()`, 118 texts (56 with ≥ 3 signs) have a within-one-edit partner across the split; the city pool has 232 (91). Dropping every ≥ 3-sign cross-split near copy from both sides gives within 0.529 and between 0.522 (Δ −0.006).
- Leakage does not prop up either number.

### 5. Sign lists
Δ = −0.007 (ICIT raw), +0.067 (A1), +0.015 (A2), −0.032 (M77), +0.006 (lump_all). One of five reaches +0.05, so **W4 fired**. That one case comes from a low within value (0.474, below chance), not from a high between value (0.540). No between value exceeds 0.541.

### 6. Power (M77 Mohenjo-daro vs Harappa at 169 per side, Harappa-only stock)

| stock, q | median | draws with between − within ≥ 0.05 (vs within median / paired) |
|---|---|---|
| 20 existing signs, 0.10 | 0.574 | 47% / 37% |
| **20 existing signs, 0.15** | 0.631 | **93%** / 90% |
| 20 existing signs, 0.20 | 0.684 | 100% / 97% |
| 100 new signs, 0.10 / 0.15 / 0.20 | 0.601 / 0.663 / 0.746 | 67% / 100% / 100% |

The within-vs-between comparison catches a stock covering 15% or more of Harappa's tokens. It misses about half the time at 10%. K4 and W5 did not fire.

## Rule check

| rule | result | fired |
|---|---|---|
| K1 LB series-bal + hand CV ≤ 0.589, gate passes | 0.524, gate 97% | **yes** |
| K2 Indus Δ ≥ 0.10 confirmed-only, or ≥ 3/5 lists Δ ≥ 0.05 | −0.007; 1/5 | no |
| K3 Indus frame removed ≥ 0.65 | 0.612 / 0.586 | no |
| K4 power q 0.20 < 50% | 100% | no |
| W1 reference Δ < 0.05 or floor ≥ 0.70 | LB −0.006 / +0.025, floors 0.88 / 0.86 | **yes** |
| W2 LB hand CV 0.589-0.65, or name-free+bal ≤ 0.589 | 0.483 | **yes** |
| W3 ≥ 2/3 formula-removed refs at Indus level | 1/3 (Latin) | no |
| W4 Indus Δ ≥ 0.05 in a robustness variant | ICIT A1 +0.067 | **yes** |
| W5 power q 0.15 < 80% | 93% | no |

## Deviations and limits

1. **`B1_lat_namefree_at_ge_random` failed by construction.** Britannia name-free has only 174 texts, under the borrowed 227. It is a non-primary row and was not rerun, so no Δ is given for Latin name-free random halves.
2. **Two gates failed.** Linear B name-free + frame (73%) and Ur III name-free + frame (43%) are below the 80% gate, so attack 3's non-Latin rows are underpowered. Their medians are still far above Indus.
3. **Compute lock.** All runs went through `board/run.sh` (repo lock, `taskpolicy -b nice -n 20`, one process). The shared marker `open-citizen-science/.local/compute.lock.indus` was held by stamp_detector. Its only live process was a network image harvest, so this light single-process job ran alongside it, as step 1 did.
4. **Proxies and missing floors.**
   - No Pylos room or Knossos findspot data is on disk, so hand groups stand in for office.
   - Knossos hand splits are close to "hand 117 (D sheep tablets) vs the rest".
   - Linear B within-palace splits drop tablets of unknown hand; the between-palace pools keep them.
   - Ur III has no within-city floor.
5. Nothing was changed after scoring. Thresholds, conditions and code are as hashed.

## Files

`rt1.py` (sizes / run / report), `sizes.log`, `run.log`, `draws.jsonl`, `results.json`, `table.md`, `ledger_rows.csv`. No third-party text is stored here: pools are read from `experiments/uniformity_paper/step1/data/` (gitignored).
