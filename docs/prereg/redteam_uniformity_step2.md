# Pre-registration: red team of uniformity paper step 2

Date: 2026-11-21. Written after pool counts were taken (`experiments/redteam_uniformity_step2/sizes.log`, counts only) and before any condition was scored or any audit token was judged. Code: `experiments/redteam_uniformity_step2/rt2.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `redteam_uniformity_step2`).

## What is under attack

Step 2 (`experiments/uniformity_paper/step2/RESULTS.md`) claims:

- (a) Name-bearing seal legends (Ur III ORACC impressions, Ur III CDLI one-per-seal, Latin owner/maker marks) separate their sites above their own within-site floors (gaps +0.12 to +0.31). Name-free legends do not: Ur III Umma vs Girsu name-free 0.599 vs within-Umma reigns 0.590.
- (b) Mohenjo-daro vs Harappa seals equal their within-site floor in every pool (gaps +0.005 to +0.042, power 98-100% at a 15% planted stock).
- (c) Chanhu-daro differs from Harappa above the floor (+0.16 / +0.19) but not above its own shuffled-label null (q 0.18-0.35).
- (d) Mohenjo-daro vs Harappa sealings differ (+0.10 / +0.12, q 0.02); the tablet gap is an object-type (copper) artefact.
- Emerging paper reading: "Indus Mohenjo-daro / Harappa seals behave like name-free seal legends: no place signal beyond the within-site floor, whereas name-bearing legends carry place."

## Method (fixed)

- Every scored condition goes through the benchmark's own `clean()` (drop strings found at both sides, then `fish_tick_closer_v2/dedup.py` greedy de-dup), `draw_n()` (Indus length mix) and `score()` (frozen NB pipeline plus one permuted-label AUC per draw). No new classifier. `corpus/build.py::_close` is not used.
- 50 draws per condition, seed 20261127, at most 227 texts per side. Pools come from step-2 `s2.py` and step-1 `s1.py` unchanged.
- Matched size: a between condition and its within floor are drawn at the same n per side (the smaller natural size).
- Δ = median between − median within; margin 0.05. p_floor = (1 + within draws ≥ median between) / 51; p_chance = (1 + permuted-label AUCs ≥ median between) / 51.
- Power gate (Part 1 style): same pool and size, labels permuted, `rt.plant` new100 stock at q = 0.15, detected when AUC ≥ max(0.65, null q95); passes at ≥ 80%, else "underpowered". Indus/sealing style: `s2.plant_side` 20-sign stock at q = 0.15 in side b with real labels, detected when AUC − within median ≥ 0.05; passes at ≥ 80%.
- Family rule (step 2): a family is "above floor" if every gated structural split has Δ ≥ 0.05; "not above floor" if at least one gated structural split has Δ < 0.05; "underpowered" if none is gated. Structural splits: Ur III ORACC U_reign, U_coll, G_reign, G_coll; CDLI U_reign, G_reign; Latin ge_rlp_vs_bwhe, br_north_vs_south.

## A1. Name tagging validity

**Audit.** `rt2.py audit` draws, with seed 20261126, 50 kept and 50 removed token occurrences (uniform over occurrences in Umma + Girsu legends, or Latin owner/maker marks) under the step-2 name-free rule, for each of: Ur III ORACC, Ur III CDLI, Latin. Each is hand-judged as `name` (personal, divine, royal or place name, or a name fragment), `not_name`, or `unclear`, with a reason, in `audit.csv`.

- Leak rate = share of kept tokens judged name or unclear (unclear counted against the tagger).
- Over-strip rate = share of removed tokens judged not_name or unclear.
- Tagging is "weak" for a corpus if leak ≥ 10% or over-strip ≥ 20%.

**Stricter and looser stripping, scored.**

- Ur III (ORACC and CDLI):
  - loose: remove only tokens whose ORACC part of speech is a proper noun (*N except N). Unknown / unlemmatised forms and forms with a name determinative are kept.
  - strict: the step-2 rule, plus any form tagged proper or unknown anywhere in the ORACC Ur III or Old Babylonian seal corpora, plus any form with any determinative `{...}`, plus the word after a kinship or service word (dumu, dam, šeš, dumu-munus, arad₂, geme₂).
- Latin: loose = remove editor-capitalised (proper) tokens of ≥ 3 letters only; strict = remove proper tokens, unit words and numerals (`rt.MIL` regex, LEGIO, COHORS ..., every numeral token) and every token of ≤ 2 letters.
- Each variant: Umma vs Girsu (or Britannia vs Germania) against each structural floor, with its own gate.
- Size control: whole Ur III legends at the name-free matched size (68 and 58 per side, U_reign and G_reign), to check that the name-free collapse is not just a smaller-n effect.

## A2. Which part of the names carries place

Ur III (ORACC and CDLI), against the same structural floors:

- `noTG`: remove toponyms and divine names (any proper part of speech other than PN and RN; any form with {ki}, {iri}, {uru}, {kur}; any {d} form not tagged PN or RN). Personal names, including theophoric ones, are kept.
- `noTGtheo`: `noTG` plus every personal name containing {d} (theophoric names, which carry city gods such as Šara or Ningirsu).
- `noPN`: remove personal names (PN) and unknown forms only. Toponyms, gods and royal names are kept.

Latin:

- `noUNIT`: remove unit words and numerals only (legion and cohort words, `rt.MIL` tokens, numerals). Names kept.
- `noPN`: remove proper tokens that are not unit tokens. Unit words and numerals kept.

Reading: place lives in personal names if `noTGtheo` stays above floor; it is a city-name / city-god leak if `noTGtheo` falls to not above floor while `noPN` stays above floor.

## A3. Indus analog: how many names could Indus carry?

- Pools: step-2 Mohenjo-daro vs Harappa seals in `m77_seal` (200 per side), `icit_seal` (172) and `icit_sealtype` (227), at the step-2 n, with REAL labels.
- A share r of texts at each site gets one site-specific name (`plant_names_real`, which is `s1.plant_names` without the label permutation):
  - `sign`: one new symbol per name, 100-name Zipf stock per site (step-1 form).
  - `spelt`: a pair of common Indus signs per name, 100-name Zipf stock per site (step-1 form).
  - `ur3emp`: the real Ur III personal-name frequencies (POS PN) of Umma (for the larger site) and Girsu, each name spelt as a fixed pair of common signs, shared names identical at both sites. This uses the real overlap of names between two Ur III cities.
- r ∈ {0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0}. The Ur III reference share is the share of raw Umma + Girsu legends with ≥ 1 personal name: 0.998 (counted before this prereg); its nearest grid point is 1.0.
- For each pool and form: a share r is **excluded** if ≥ 95% of planted draws have AUC − step-2 within median > the observed step-2 Δ. Max consistent share = largest tested r below the first excluded r.
- "Ur-III-like name load excluded" for a pool and form if the first excluded r ≤ 1.0 (the grid point for 0.998).
- Comparison with step 1 (permuted labels, absolute AUC detection: 80% detection at r = 0.5; 0.55 compatible with names on up to 20-30% of seals) is reported, not tested.

## A4. Floor bias

No new draws. For every between condition of step 2 (`experiments/uniformity_paper/step2/draws.jsonl`):

- Δ_floor (step 2), Δ_null = between median − median of that condition's permuted-label AUCs (same pool, same n), Δ_cons = between − max(within median, null median).
- Part 2 pair verdicts are recomputed three ways with the step-2 rule: floor (Δ_floor, q_floor, power vs within median), null (Δ_null, q_chance, power vs null median), cons (Δ_cons, max(q_floor, q_chance), power vs the larger reference). q = Benjamini-Hochberg within each step-2 family. Any pair whose three verdicts disagree is listed as a flip.
- Part 1 family verdicts are recomputed with Δ_null and Δ_cons in place of Δ (gate unchanged).
- Known limit: with 50 draws the smallest p is 0.020, so a single p of 0.02 in a family of 15 gives q = 0.30. This is reported, not fixed.

## A5. Sealings and tablets

- Duplication profile: raw, distinct, cleaned and strict-cleaned counts and the largest identical-string cluster per site (descriptive).
- Strict de-dup: `clean()`, then `dedup.greedy` again with `MIN_DROP = 2`, then one text per sign multiset (multisets at both sides dropped). Between, random-halves floor of the larger site, side-b power at q = 0.15; step-2 pair rule with BH over the two editors.
- Cross-object test (per editor, all four at the same n = 62): X1 Harappa sealings vs Mohenjo-daro seals, X2 Harappa sealings vs Harappa seals, X3 Mohenjo-daro sealings vs Harappa seals, X4 Mohenjo-daro sealings vs Mohenjo-daro seals. Gate (`rt.plant` new100, q 0.15) on X1 and X3.
  - place-consistent: X1 − X2 ≥ 0.05 and X3 − X4 ≥ 0.05 (each city's sealings are closer to its own seals);
  - object/format: both < 0.05; mixed otherwise; underpowered if either gate < 80%.
  - Note: `clean()` drops sealings whose string matches a same-city seal in X2 / X4, which pushes X2 and X4 up and makes "place-consistent" harder to reach. Stated in advance.
- Harappa mound floor for M77 sealings (mound F vs AB). Counts show AB = 8, so this is expected to be underpowered and will be reported as such.
- Tablets, subtype-matched (ICIT): moulded only (TAB:B), and non-copper (TAB:B + TAB:I), Harappa vs Mohenjo-daro, floor = Harappa random halves, side-b power at q 0.15, step-2 pair rule with p_floor ≤ 0.10.

## Verdict rules per claim

**(a) name-bearing carries place, name-free does not.**
- BROKEN if any of:
  - A4: the whole-tier Ur III or Latin family is not above floor under Δ_cons;
  - A2: Ur III ORACC `noTGtheo` is "not above floor" while `noPN` is "above floor" (place = city names / city gods, not personal names);
  - A1: Ur III ORACC strict name-free is "above floor" (the name-free failure was caused by leaked names).
- STANDS WEAKENED if not broken and any of:
  - audit tagging "weak" for an Ur III corpus;
  - Ur III loose name-free is "above floor";
  - Ur III strict name-free is underpowered;
  - Latin `noUNIT` is not above floor (Latin place sits in unit words / numerals);
  - the whole-at-name-free-size control is not above floor (the name-free failure could be a small-n effect).
- STANDS otherwise.

**(b) Mohenjo-daro vs Harappa seals are at the floor.**
- BROKEN if any of the three pools is "differs" under the null or cons reference.
- STANDS WEAKENED if any pool has Δ_null ≥ 0.05 or Δ_cons ≥ 0.05 without reaching "differs", or its power against the null or cons reference is < 80%.
- STANDS otherwise.

**(c) Chanhu-daro above floor, not above null.**
- BROKEN if any Chanhu-daro pair with Mohenjo-daro or Harappa is "differs" under the null reference (it is then above chance), or if no Chanhu-daro pair with a big city has Δ_cons ≥ 0.05 (the "above floor" part was floor bias).
- STANDS WEAKENED if a step-2 "differs" Chanhu-daro pair has Δ_cons < 0.05.
- STANDS otherwise.

**(d) sealings differ; tablet gap is a subtype artefact.**
- Sealing part BROKEN if strict de-dup gives Δ < 0.05 in both editors, or the cross-object verdict is "object/format" in both editors, or neither editor's sealing pair is "differs" under the null reference. WEAKENED if one of these holds in one editor only, or the cross-object test is mixed or underpowered.
- Tablet part BROKEN if subtype-matched moulded tablets "differ" (gated): the tablet gap is then not only a copper artefact. STANDS if "same"; underpowered otherwise.

**Emerging reading** ("Indus seals behave like name-free legends").
- SUPPORTED if (a) is not BROKEN, (b) is not BROKEN, and `ur3emp` excludes the Ur-III-like name load in all three Indus pools.
- WEAKENED if (a) or (b) is WEAKENED, or the exclusion holds in only some pools.
- BROKEN if (a) or (b) is BROKEN, or the exclusion holds in no pool.

## Compute and logging

- `board/run.sh` (repo lock, `taskpolicy -b nice -n 20`, one process, one worker). Nothing detached.
- The shared marker `open-citizen-science/.local/compute.lock.indus` is held by stamp_detector (`embed.py`, a network image job using ~0% CPU). As in step 1, its red team and step 2, this single-process job runs alongside it; logged as a deviation.
- Thresholds are not changed after scoring. Deviations go in RESULTS.md.
- Part 2 of this task (Chanhu-daro follow-up) has its own prereg, written after this part is written up.
