# Pre-registration: uniformity paper, revision analyses (review 1)

Written 2026-11-21, before any draw in this file was scored. Code: `experiments/uniformity_paper/revision/rev.py`
(draws) and `report.py` (verdicts). Both are hashed with this file in `docs/prereg/HASHES.txt`, tag
`uniformity_paper_revision`.

## What has been seen before this file

- Pool sizes only (`revision/sizes.log`): counts per side for every condition below. No AUC has been computed on any
  revision pool.
- The step-2, Chanhu-daro follow-up and red-team results that the paper already reports.
- The M93 concordance facts: in M77 the sign occurs only at Chanhu-daro (10 seals, 1 sealing); it usually stands
  as its own final line after M342; the M77 numeral inventory lists it as a three-stroke form like M94; the
  consensus-corpus links align it to ICIT W032, and ICIT reads the same final line as W031 W032. These facts
  shaped the merge variants in R6. They are reported as facts, not tested.
- A 40-legend audit sample of the Ur III role tagger (`revision/data/roles_sample.txt`, gitignored), used to fix
  tagger rules. No scores.

## Fixed pipeline (unchanged from step 2)

Cleaning `ub.clean` (strings found at both sides dropped, then non-chaining de-dup with
`experiments/fish_tick_closer_v2/dedup.py`). Length-matched draws `ub.draw_n`. Scorer `ub.score`: Bernoulli NB,
grouped 5-fold CV x3, plus one permuted-label AUC. Margin 0.05. Planted gate: `rt.plant` new100 at q = 0.15 with
labels permuted; a draw counts if AUC >= max(0.65, null q95 of the between condition); the gate passes at >= 80%.
Indus power: `s2.plant_side`, 20-sign stock at q = 0.15 on side b; a draw counts if AUC minus the within median
>= 0.05; power passes at >= 80%. Family rule: "above floor" when every gated structural split has Δ >= 0.05;
"not above floor" when a gated split has Δ < 0.05; "underpowered" when no split is gated. Seed 20261201.
Gates are never loosened after data.

## R1. Bootstrap over texts

Conditions: MD vs Harappa in m77_seal, icit_seal, icit_sealtype (n per side 200, 172, 227, as in step 2); unicorn
seals (R7 pools, n 145); Ur III Umma vs Girsu against U_reign, U_coll, G_reign, G_coll (ORACC; n 227, 171, 199,
157) and CDLI U_reign, G_reign (227, 197); Latin Britannia vs Germania against ge_rlp_vs_bwhe and
br_north_vs_south (128, 73); Chanhu-daro pairs m77_seal and icit_sealtype with Harappa and Mohenjo-daro (44, 42,
40, 38).

Per replicate (200 per condition): resample texts with replacement within each side label of the between pool
and, independently, of the within pool, keeping each side's size; copies keep their group, so grouped CV keeps
them in one fold. Then 5 between draws and 5 within draws at the step-2 n. Replicate statistics from medians:
Δfloor = b − w, Δnull = b − permuted-label AUC, Δcons = b − max(w, null).

Choice stated in advance: resampling B and W separately, and drawing inside resampled pools that hold duplicate
texts, makes the interval wider than a paired design would. This is the conservative direction.

Rules. 95% CI = 2.5 and 97.5 percentiles. TOST at ±0.05 (alpha 0.05 each side): equivalent when the 5th
percentile > −0.05 and the 95th < 0.05. If not met, the supportable margin is m* = max(|q5|, |q95|). References
are "above margin" when q5 of Δfloor >= 0.05. Chanhu-daro pairs are judged on Δcons (as in the follow-up).

## R2. Planted names, finer grid

For each MD–Harappa family, 60 replicates. Each replicate: bootstrap B and W as in R1; 3 within draws; for each
rate r in {0, .10, .20, .25, .30, .35, .40, .45, .50} and each stock form (`sign`: an invented stock of 100 one-sign
names per site, Zipf weights; `spelt`: 100 invented two-sign names per site spelt with common signs; `ur3emp`:
real Ur III personal-name frequencies, Umma for side a and Girsu for side b, each name spelt as a fixed pair of
common signs shared by both sites), 3 between draws with
`rt2.plant_names_real` applied at rate r. Replicate Δ_r = median planted between AUC − median within AUC.

Rules. Detection at r = share of replicates with Δ_r >= 0.05. r80 = first crossing of 80% on the grid, linear
interpolation; 95% CI by resampling replicates (1000x). Exclusion: a rate is excluded when >= 95% of replicates
give Δ_r above the observed step-2 Δ (0.005, 0.014, 0.042). The new name bound is the smallest excluded rate per
form and family, with its CI. If 80% is never reached by 0.50, the form is reported as "underpowered up to 0.50".

Diffuse effects (no stock): `variants` (half of the sign types at Harappa get a local variant; each token of
those types switches with probability v) and `shift` (each Harappa token is replaced with probability v by a
draw from shared common-sign frequencies reweighted by exp(N(0,1)) per sign). v in {.1, .2, .3, .5}, 50 draws
each. Power = share of draws with AUC − step-2 within median >= 0.05. The mean altered-token share is reported.

## R3. Ur III name roles

Tagger (fixed in code): names are PN, RN, X, u, ?. Father = a name right after dumu. Patron = any RN, or a name
right after arad₂ / geme₂; in a dedicated legend (arad₂-zu, in-na-ba and the forms listed in `DED`), first-line
names are patron only if a later unassigned name exists. Owner = the first remaining name; other = any further
name. "+gov" marks a name followed by ensi₂. Variants: noPN (step-2 rule), noOwner, noFather, noPatron,
noOwnFath, noPrivate (owner, father, other, unless +gov), noOffice (patron or +gov), noAllNames.

Each variant: Umma vs Girsu against all four ORACC floors and both CDLI floors, n matched per split to the smaller
of the two pools, plus a gate. Family rule as above, with min and max gated Δ.

Between-archive: ORACC and CDLI carry no archive field. The stand-in is a same-collection test: Umma texts in the
British Museum vs Girsu texts in the British Museum (variants whole, noPN, noPrivate), against the four ORACC
floors. This removes the museum confound, not the archive one; it will be called that.

Expected underpowered or thin: CDLI G_reign and ORACC U_coll / G_coll in the name-poor variants (n 45–80).

## R4. Latin by object class

Classes, fixed in code: MIL (any unit word), STAMP (step-2 stamped flag), GRAF (graffito cue in the EDH
commentary), REST (GRAF + unflagged). Between Britannia vs Germania against ge_rlp_vs_bwhe and
br_north_vs_south, whole legends, names kept, gate as above. Expected: MIL (n 9, 6) underpowered; STAMP (n 9, 1)
untestable between provinces, because Britannia has 9 stamped legends. These will be reported as such, not as
"no difference".

## R5. Second classifier

(a) L2 logistic regression: the frozen `lib.oof_scores(model="lr")` (C = 0.5, balanced) in place of NB, same CV
and permuted-label AUC. (b) Jensen–Shannon divergence between the two sides' pooled sign and within-line pair
counts, with a 200-shuffle permutation p per draw. 50 draws each, step-2 n.

Indus (three families): LR verdict "underpowered" if power < 0.80; "differs" if Δ >= 0.05 and p_floor <= 0.10;
"same" if Δ < 0.05 and p_floor > 0.10; otherwise "inconclusive". JSD: PS = P(JSD between > JSD within) over all
draw pairs; "between > floor" if PS >= 0.80; JSD power = share of planted draws with JSD above the within q95;
"underpowered" below 0.80. References: LR by the family rule; JSD "between > floor" when PS >= 0.80 in every
split. Agreement = same verdict class as NB in step 2.

## R6. M93

Listing: every M93 in M77 with object id, the linked ICIT id, CISI number and ICIT sequence; twins M94, M89, M86,
M87 by site; share of ICIT seal texts whose last segment is W031 W032, by site. Object ids go to
`docs/HUMAN_LEADS.md` for photo checks.

Merge test, m77_seal, Chanhu-daro vs Harappa and vs Mohenjo-daro, 50 draws, n = the smallest natural n across
variants and the within pool (43, 41): base; M93 → M94; M93 → M89 (the common three-stroke sign); M93 → M86 M87
(the ICIT reading); M93 dropped. Rule: a variant "removes" the gap if Δcons < 0.05 in both pairs; "partly" if Δcons
falls by at least half of base in both; otherwise "does not remove".

## R7. Unicorn seals only

ICIT symbol code starting "Bull1". MD vs Harappa (n 145 matched to the within pool), within = MD random halves.
Power from `s2.plant_side` at q .10, .15, .20. Verdict by the step-2 part-2 rule with p_floor <= 0.10 (one test
per family). Δnull reported.

## Compute and deviations known now

One process at a time through `board/run.sh`, background priority, single worker. The shared lock
`open-citizen-science/.local/compute.lock.mind` dates from 2026-11-21T07:44Z and no process for it is running; it
is treated as stale and left in place.
