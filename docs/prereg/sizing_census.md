# Sizing census: n and smallest detectable effect for every open route

Agent `paper`. Main lines (a) and (b). Fable's ranked study 1 of 2026-11-24 (after `tablet_pic_text`); coordinator-approved.
**Status: sealed 2026-11-24, after a fresh review (10 fixes applied). No code existed at sealing; nothing had been run.**

## Why
- Three sealed studies in a row stopped on size: `anchor_ceiling` v2, `scott_ic_refute`, `tablet_pic_text`. Each cost a full prereg, a review and a kill run.
- **The calculator could have foreseen at most two of the three.** The Scott stop came from the lexicon and the null's width, not from counts.
- So: one cheap calculator, checked against sealed outcomes, then a table of every open route. After that, no prereg is drafted before its row passes a count gate.
- It also absorbs the pending "recovery vs documents-per-word" curve (the minimum-count rule for the scorecard's U rows).

## Disclosure: what has been seen
- **Every kill-test outcome below is known to the drafter.** The kill test is a calibration check, not a blind test.
- **Hand checks made while drafting** (normal approximation, guessed prevalences): tablet bovine, unicorn, C6 and C9.
  - They suggest the calculator runs optimistic, by up to about +0.25 on mid-power cells. The α / m rule was chosen with the unicorn case in view.
  - The tolerance below (0.20) was set knowing this. A failure of A1 or A3 on a hard cell is a likely outcome.
- **Not seen and not to be seen here:** any feature × label table on real data. The census reads marginals only.

## Prior art
- In-repo, opened: `harp_pack/power.py` and `power.log`, `animal_tie_power` Leg A, the `tablet_pic_text` sizing run, the `anchor_ceiling` v2 gate.
- Standard methods relied on, none opened for this draft: two-proportion normal approximation, Cohen 1988 **(unverified)**; minimum detectable effect, Bloom 1995 **(unverified)**; Bonferroni; Gaussian copula for rank correlation **(unverified)**; Monte Carlo power for small cells (no source claimed).

## The calculator (`experiments/sizing_census/calc.py`, one entry: `power(family, shape, effect, alpha)`)
- **Inputs are shape only:** n, class and stratum sizes, feature prevalences (marginals), m, alpha, the planted effect's definition. Never a result.
- **Family A1, binary tie, two classes** (sign × class, label-swap plant).
  - **n counts rows** (text types × class), not objects and not near-copy families. Families are CV groups in the real pipelines. They are not modelled (gap G1).
  - For a tie sign g with c_g rows of n: p0 = c_g / n. Target count in class A = ceil(n_A · (p0 + δ)). The draw is **feasible** if that count ≤ min(n_A, c_g).
  - Realised δ follows from the ceiling. p_B is what remains of c_g in the n_B other rows.
  - Test: one-sided two-proportion z at α / m; exact Fisher on 2,000 simulated tables when an expected cell is under 5.
  - **Power is conditional on feasible draws,** averaged over tie signs drawn uniformly from the case's candidate list. The feasible share is reported. A rung under 0.75 feasible is not counted.
  - **m** = the number of tests the real statistic corrects over, or the size of the plant's candidate list when the statistic is a classifier. A pre-named feature has m = 1.
- **Family A2, rate tests** (2,000 simulated samples).
  - A2a, one sample against a fixed rate p0: exact binomial, plus the route's share bar if it has one.
  - A2b, two samples in strata, the reference sample finite: both are drawn (reference at its stratum rates, target at R × them); test = exact stratified hypergeometric, upper tail, plus the ratio bar.
- **Family A3, rank correlation** (2,000 draws × 999 permutations).
  - Gaussian copula at latent ρ; the value margin is the route's own, ties kept.
  - Rows are first collapsed to (lot, text) units at the shape's duplicate share. Ranks are taken within strata. p = values permuted within stratum, two-sided.
  - A draw with fewer than the route's minimum of positive values (C9: 8) is a fail.
- **Family B, profile recovery vs documents per word** (2,000 simulated word sets).
  - Three anchor blocks, named S (site), K (object class), P (picture). These are `anchor_ceiling`'s rung "A3" variables; that name is not used here.
  - Each document has one value per block, drawn from the block's base rates, and holds w words. A document with ≥ 1 planted word takes the picture value of one of its planted words (uniform) with probability s; else it keeps its own.
  - Profiles as in v2: α = 2 smoothing toward dev base rates, log ratio, unit-normalised blocks. Words go to the nearest true-field dev centroid by cosine.
  - Scoring as in v2: k = 6; a field with under 3 held-out words in a draw is unscored there; recovered = ≥ 4 of 5 draws.
- **Family C, dictionary fit of a key:** not computed (see the exclusion). **No family:** omnibus G tests over lots, genre models, image detectors. Raw n only.
- **MDE** = smallest effect with power ≥ 0.8, by bisection (δ to 0.005, ρ to 0.01, R to 0.01). **n needed** = smallest scale k (all counts × k) with power ≥ 0.8, up to 64×.
- **Pre-declared gaps** (each lowers real power, so the calculator should be an upper bound):
  - G1: no CV, no near-copy families, no classifier; A1 knows the feature;
  - G2: A1's null is the formula's, not a within-site permutation; site and length strata enter only through class sizes (F14: strata of site × min(length, 7) are not modelled);
  - G3: C6's removal of rows already in ICIT, and its broken-text generator, enter only as the stratum mix;
  - G4: C9's lot structure enters only as a duplicate share; form × period strata are taken as equal-sized.

## Kill test, run first (seed 20261125)
- `cases.json` holds each case's shape; `sealed.json` the sealed numbers. `calc.py` never reads `sealed.json`; `compare.py` reads both.

### Excluded: `scott_ic_refute`. The bar changes.
- Its stop came from lexicon saturation under her sound swaps (random keys fit 0.43-0.70) and a shuffle null made twice as wide by formulae (0.061 against 0.035). A shape-only version would be the experiment again.
- **Change to the coordinator's bar, stated plainly:** "4 of 5 outcomes" becomes **adoption per family**, each on its own cases (below). Scott counts for nothing.
- Family C routes enter the census with raw counts and the standing verdict "untestable by fit at stated power".

### Cells and sealed values
| case | family | shape fed in | cells: sealed value |
|---|---|---|---|
| 1 `anchor_ceiling` v2 | B | see the next list | dev gate (every field ≥ 0.8): met, 0.95-1.00. Held-out adjusted Rand 0.56; person 0.65 (bar 0.8 each: not met) |
| 3 `tablet_pic_text` bovine | A1 | 61 rows, n_A = 21, 13 candidate signs (≥ 5 rows), m = 13, α = 0.025 | δ 0.095: 0.03. δ 0.143: 0.03. **Grey, not gating:** δ 0.238: 0.40 (20 of 40 feasible, not counted, standard error about 0.11) |
| 4a `animal_tie_power` unicorn | A1 | 1,149 rows; class A = the 204 non-unicorn rows, n_B = 945; α = 0.05 / m | δ 0.05: 0.20. δ 0.10: 0.73. δ 0.20: 1.00. δ 0.40: 1.00 |
| 4b F14 shorthorn bull | A1 | n_A = 78 of 1,149; m = 30 (the sealed test count); α = 0.05 / 30; signs in ≥ 15 texts | δ 0.05: 0.18. 0.10: 0.60. 0.20: 0.95. 0.40: 1.00. 0.80: 1.00 |
| 4c F14 elephant | A1 | n_A = 34; else as 4b | δ 0.05: 0.10. 0.10: 0.30. 0.20: 0.68. 0.40: 1.00. 0.80: 1.00 |
| 5a `harp_pack` C6 | A2b | seal counts and rates per stratum (length 1-5 / 6+ × broken / complete), from `power.py`; R = 1.5; bar R̂ ≥ 1.25; α = 0.00385 | n 725: 1.00. 546: 1.00. 393: 0.99. 366: 0.99. 184: 0.84 |
| 5b `harp_pack` C9 | A3 | value margin, duplicate share and strata count from `power.py`; latent ρ = 0.5; ≥ 8 positive values; α = 0.00385 | n 290: 1.00. 220: 0.99. 146: 0.89. 120: 0.82. 72: 0.39 |

- **Case 4a's m** = the size of the plant's candidate list: M77 signs in ≥ 5 of the 1,149 texts (`run.py`, `cands`). The sealed output does not store the integer (58 distinct signs were drawn). It is counted from the texts alone and written into `cases.json` before `calc.py` is hashed.
- **Case 1's shape, all from `anchor_ceiling`:**
  - 5 draws of 1,680 dev + 565 held-out documents; dev words have ≥ 5 dev documents, held-out words ≥ 2 (observed 2-5);
  - field sizes place 25, admin 14, land 8, occupation 8, person 5; of these 16 / 10 / 5 / 3 / 3 are in the 44-word held-out pool;
  - s = 1.0 (about 85% of a planted word's dev documents then carry its value, as sealed);
  - documents per word (dev and held-out), words per document, and base rates of S, K and P: tabulated from draw 0 by `shapes.py`, which opens no truth label and builds no word × anchor table.
- Effects fed in are the plants' nominal definitions. Realised values from the sealed logs (C9's ρ 0.42) are not used.

### What "reproduce" means (frozen)
- **R1, verdict.** On every counted cell with sealed power ≤ 0.5 or ≥ 0.9, the prediction is on the same side of 0.8. For case 1: dev gate met and held-out gate not met.
- **R2, hard cells.** Over the case's counted cells with sealed power between 0.05 and 0.95, the **maximum** absolute error is ≤ 0.20. For case 1: adjusted Rand within 0.56 ± 0.20 and person within 0.65 ± 0.20.
- A case is reproduced if R1 and R2 both hold. The grey tablet cell is reported and gates nothing.
- **Adoption per family.** A family is adopted only if every one of its cases is reproduced. One family's miss does not discard another.
  - A1: cases 3, 4a, 4b, 4c. A2 (both modes): 5a. A3: 5b. B: 1.
- **Reported, never gating:** predicted MDE and minimum n against the sealed c\* (0.20, 0.20, 0.40) and minimum n (184, 146); any cell predicted more than 0.10 **below** sealed, which contradicts "upper bound".
- No tolerance, formula or shape changes after the hashes.

## The census (seed 20261126)
- **The list below is the list.** Family and effect are assigned here, at sealing. The run adds, drops and re-labels nothing. It only recounts n and reports differences.
- **Effect rule.** A1 routes use Linear B strength, δ 0.23. Another effect is used only where a sealed prereg names it; the prereg is cited in the row.
- **Reading rule.** Counts only: rows, class sizes, single-variable prevalences. No cross-table of feature by label is built.
- Rows of a family that was not adopted, and rows marked "none", report raw n only.

| # | route (source) | family | n in hand → n if the lead arrives | effect |
|---|---|---|---|---|
| 1 | seal text × animal (atlas 5.7) | A1 | 1,149 rows; minorities 78 / 45 / 34 / 15 / 12 / 10 / 10 | δ 0.23 |
| 2 | tablet picture × text (5.7; Fuls code list; CISI 3) | A1 | 61 rows → 136 → about 2× | δ 0.23 |
| 3 | copper emblem out of sample (ranked study 6) | A1 | under 30 rows, 7 signs | δ 0.23 |
| 4 | per-sign profiles: sign × object, sign × site (3.6) | B | 2-5 held-out documents per sign | curve d\* |
| 5 | jar sign on pottery (7.8; harp C6) | A2b | 65 texts → ≥ 184 new units | R 1.5 (`m342_offsite.md`, `harp_pack.md`) |
| 6 | firing stage (10b.3; harp C1, C2) | A2b | 36 staged vessels → ≥ 146 pre-firing units | rates 0.04 vs 0.16; 0.15 vs 0.05 (`harp_pack.md`) |
| 7 | numerals vs size (6.8; harp C9-C12) | A3 | rods 13, implements 3, bangles 0 → 146 rims | ρ 0.5 (`magnitude.md`, `harp_pack.md`) |
| 8 | bangle oval (10b.2; BO-H1) | A2a | 0 new texts → HARP list | 0.15 against 0.0106, bar 0.08 (`bangle_oval.md`) |
| 9 | titles on door sealings (5.8) | A1 | 3 door sealings of 55 | δ 0.23 |
| 10 | M328 on offering scenes (10b.1) | A1 | 1 offering type → 3-6 with photos | OR 3 (`scene_text.md`, pass bar) |
| 11 | ticked fish by area (10b.15; TF1; harp C13) | A2a | 6 ticked fish of 417 Harappa seal texts | rate tripled in one area of ≥ 20 seals (`harp_pack.md`) |
| 12 | city sign stock (10b.5) | A1 | as in atlas → 3× dated seals | δ 0.23 |
| 13 | line breaks (10b.10) | none | 74 two-line texts; sealed gate n ≥ 150 | raw n |
| 14 | tablets quote seals (5.10); M99 relator (4.11) | none | as in atlas | raw n |
| 15 | Gulf round texts (1.10; F1/F2) | none | 12-28 texts; 0 new of 8 needed | raw n |
| 16 | new-find predictions P1-P15, L1-L7, PK (registry A) | none | 12 new objects, 2 scorable; each minimum n as sealed | raw n |
| 17 | lots and archives (5.1, 5.3, 10b.4, 10b.14; harp C7) | none | → 184 tablet units in lots ≥ 3 | raw n |
| 18 | copper calendar (5.6); carver hands, craft (10b.17) | none | as in atlas | raw n |
| 19 | Meluhha tablet photos (9.2) | none | 0 photos → 2 tablets | raw n |
| 20 | edition sweep for stamped tablets (ranked item 2) | none | 1 firm positive; 10 needed | raw n |
| 21 | phonetic keys by fit (1.1) | C | 10,005 tokens; key coverage | not sized |

- **Output** (`census.csv`, `RESULTS.md`), one row per route and data state: `route`, `source`, `family`, `n`, `class_sizes`, `m`, `alpha`, `effect` and its source, `power_at_effect`, `MDE_0.8`, `feasible_share`, `power_LB_names` (δ 0.07 and 0.11), `n_needed` (count and multiple of n in hand), `gate`, `what_adds_rows`.
- **Linear B strength** is `animal_tie_power`'s calibration: a full line's tie ≈ +23 points (excess AUC 0.13); formula words removed ≈ +7 to +11. It is defined for binary ties only.

### Gate rule (adopted per family)
- **A prereg needs predicted power ≥ 0.8 on data in hand, at δ 0.23 by default, or at a named effect only where a sealed prereg names one.**
- The check is a census row, or a fresh `calc.py` call with the route's shape, quoted in the new prereg's first section.
- **Passing is necessary, not sufficient.** Each prereg still runs its own planted kill test. STOP by count stands until rows are added.
- A route in a family that was not adopted, or in none, states its own count gate in two lines before any design work.

## U-row minimum-count rule (seed 20261127; planted data only)
- **Code.** `curve.py` uses `core2.profiles` and `core2.assign` unchanged. The plant and the thinning are new code. `truth/labels_*.json` are never opened.
- **Documents.** Draw 0, dev and held-out together (2,245 documents).
- **Per d in 2, 3, 5, 8, 12, 20:**
  - E_d = words with ≥ d + 5 documents (text counts only). Only these can be tested at d. If |E_d| < 30 the rung is "not reachable at this corpus size", and that is the reported result. |E_d| is listed for every d.
  - **Planted truth:** every word of E_d gets a random field, in the proportions 25 : 14 : 8 : 8 : 5. Pictures are planted by the v2 rule at s = 1.0 and 0.6. Real labels play no part.
  - **Thinning:** a random 30% of E_d are test words. Each keeps d of its documents, chosen at random. The union of kept documents is the test side.
  - Test-side documents are removed from every centroid. So a document shared by two words is on one side only, and counts for each test word that kept it.
  - A test word's profile uses its d kept documents only. Centroids use non-test words with ≥ 5 documents left.
  - 20 plants. A plant counts at d only with ≥ 3 test words in each of ≥ 3 fields.
- **d\*** = smallest reachable d where, at s = 1.0, the median adjusted Rand is ≥ 0.8 and every scored field is recovered in ≥ 0.8 of plants. If none: d\* is "> the largest reachable d".
  - One exclusive picture value per field is easier than any real tie, so d\* is a lower bound.
- Family B's predicted curve is printed beside it. It decides nothing.
- **The rule, per U row** (27 rows of `experiments/scorecard_v1/final.json`, assigned now):
  - own A1 row at δ 0.23, counts from the row's cited RESULTS: MUK25-fish-gem, MUK22-gold-ratti, MUK23-kanmer-occupation, MUK23-wild-ass, MUK19-crop-on-jars, PAR-sign193-weight, PAR-man-steelyard, LAU10-twins-prefix, MAH09-jar-bearer, MAH09-arrow-bearer, PAR75-chanhu-toponym;
  - census route: WEL15-jar-40L (5); KEN06-jar-strokes, MUK23-triple-cup-goblet (7); HV-bangle-workshop (8); FT05-access-control (9); LAU10-other-language (15); CAL-noise-keys, KEY-yajnadevam (21);
  - no count rule: FUN-sigil, MUK23-no-names-no-toponyms, MAH-bearer-kaviti, PAR-vel-substitution, PAR-murukan-partners, KEN20-premature-marks, FSW04-emblems, OWN-7.
  - Any row whose test needs a per-sign profile also needs ≥ d\* documents per sign, for ≥ 3 signs per class.
- The scorecard page gains two columns for U rows: count in hand, count needed. **No tier changes here.**

## Frozen readings
- **A family is adopted:** its census rows carry MDE and n needed, and the gate rule binds routes of that family. It goes into RESEARCH_STATE's standing rules.
- **A family is not adopted:** its calculator is not trusted. Its rows report raw n only, with any minimum n already sealed elsewhere. No gate for that family.
- **Family B not adopted:** the curve leg is still run and reported as a description. No U-row profile rule is adopted.
- **No family adopted:** the census is a table of raw n. No gate rule.
- Either way, no route is opened or closed by this study, and no atlas verdict or scorecard tier changes.

## Limits stated in advance
- A1 rests on four cases from two studies; A2, A3 and B on one case each.
- The kill test is not blind, and the tolerance was set with rough numbers in view.
- An oracle test can pass routes that a real pipeline cannot power. The gate only removes hopeless routes.
- Linear B strength is one script's tie between a line and its logogram. It is an upper bound for an emblem.
- Plants tie one feature to one class. Spread ties need more rows than the table says.

## Sealing order, cost and procedure
1. Fresh review of this file. Then hash this file alone in `docs/prereg/HASHES.txt` (tag `sizing_census`).
2. Write `calc.py`, `compare.py`, `curve.py`, `shapes.py`. `calc.py` may be tried on made-up shapes only.
3. Hash the four scripts. **`calc.py` is not run on any case shape before its own hash is recorded.**
4. Run `shapes.py` to write `cases.json`; write `sealed.json` by hand from the sealed files; hash both.
5. Kill test → commit `kill.json` → census → curve leg → RESULTS.
- **Cost:** under 1 hour on 4 workers, `nice -n 20`.
- **Lock:** `mkdir /Users/harsha/Desktop/Personal/open-citizen-science/.local/compute.lock.indus` before any run; removed after. `board/run.sh` is not relied on for this.
- **Memory:** `memory_pressure | tail -1` must show ≥ 20% free before each step; otherwise wait.
- Changes after sealing go in `sizing_census_add1.md`, hashed before the affected step.
