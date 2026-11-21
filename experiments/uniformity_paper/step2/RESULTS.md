# Uniformity paper, step 2: seal-type references with their own floors; all-site Indus map

Prereg: `docs/prereg/uniformity_paper_step2.md`, hashed with `s2.py` and `build2.py` in `docs/prereg/HASHES.txt` (tag `uniformity_paper_step2`, 2026-11-21T16:12:08Z) before any condition was scored. Every condition ran through the benchmark's own `clean()` + `draw_n()` + `score()`. There are 50 draws per condition, seed 20261125, and 15,250 draws in all, none failed. Numbers are in `table.md` and `results.json`; per-draw values are in `draws.jsonl`. Ledger: `ledger_rows.csv`.

## Verdicts

**Part 1: whole seal legends SUPPORT the reference contrast. Name-free legends REFUTE it, by the frozen rule.**

- **Whole legends.** Ur III and Latin both separate their sites more than any within-site split, and every gate passes. Old Babylonian points the same way but its gates are just short (78% and 56%), so it counts as underpowered.
  - Ur III impressions: Umma vs Girsu is 0.86-0.88. Two reigns inside one city give 0.62-0.72, and two museum collections give 0.55-0.62, so Δ = +0.16 to +0.31.
  - Ur III seals counted once per physical seal (CDLI) replicate this: Δ = +0.17 and +0.22 against the reign floors.
  - Latin instrumentum owner/maker marks: Britannia vs Germania is 0.66-0.71. Two regions of one province give 0.52-0.58, so Δ = +0.12 and +0.14.
- **Name-free legends.** Ur III Umma vs Girsu (0.599) is no higher than early vs late reigns inside Umma (0.590): Δ +0.009, with the gate passing (82%). Inside Girsu, the reign split (0.698) beats the between-city value (0.604), though that gate is 62%. The CDLI replication says the same: Umma reigns Δ +0.033, Girsu reigns −0.075.
  - Without personal names, Ur III seal legends carry date as strongly as place. That is the Linear B outcome again, in a seal corpus.
  - Latin name-free (42 and 29 per side) and Old Babylonian name-free (11 and 8 per side) are underpowered, as stated in advance.
  - The kill rule K-Ur3 (a gated Δ ≤ 0) did not fire: the gated Δ is +0.009, and the negative one is not gated.

**Part 2: the pre-registered question answers YES, but the answer is fragile.**

- The paper's kill rule fired: some gated Indus pairs differ.
- Mohenjo-daro vs Harappa seals stay "same" in every editor and pool: Δ +0.005 (M77), +0.014 (ICIT seals) and +0.042 (ICIT seals + sealings), with power 98-100% at q = 0.15.
- Chanhu-daro is the exception.
  - It is the most separable site in all six pairs with the two big cities: AUC 0.61-0.68.
  - Harappa vs Chanhu-daro meets the frozen "differs" rule in two editors: M77 0.631 (Δ +0.164, q_floor 0.098) and ICIT seals + sealings 0.680 (Δ +0.187, q_floor 0.074).
  - Mohenjo-daro vs Chanhu-daro is 0.61-0.65 but misses the q bar (q_floor 0.16-0.24).
- **Why it is fragile.**
  - None of the Chanhu-daro AUCs beats its own label-permuted null after correction: q_chance 0.18-0.35. Three of the six pairs with a big city sit above their null q95, with raw p_chance 0.039-0.059: M77 Mohenjo-daro, and ICIT seals + sealings with Mohenjo-daro and with Harappa. The other three do not.
  - The "differs" verdicts rest on the random-halves floor of the larger site, which falls a little below 0.5 (0.47-0.49).
  - Pairs between two small sites (Lothal, Chanhu-daro, Kalibangan) have floors of 0.32-0.40. That is the pipeline's known low bias on small pools with shared strings removed. Their "differs" verdicts (between 0.57-0.61) should not be read as place signal.
- **Other object types.** Mohenjo-daro and Harappa differ in sealings (0.613 ICIT, 0.608 M77; Δ +0.10 and +0.12; q_floor 0.02) and in tablets (0.774, Δ +0.32). But Mohenjo-daro's "tablets" are mostly copper tablets (197 of 299), while Harappa's are moulded or incised tablets. The tablet row is a subtype contrast, not a place contrast.
- **Lothal, Kalibangan and Dholavira** never differ from Mohenjo-daro or Harappa. Most of those pairs are underpowered (power 16-84% at q = 0.15). Mohenjo-daro vs Dholavira (ICIT seals + sealings) is gated "same" (Δ +0.047).

### What this does to the paper's claim

The claim "no measurable spatial or group structure at any scale" is now too strong. Safe wording:

> Seal texts from Mohenjo-daro and Harappa differ no more than two random halves of one city, under both editors (between minus within +0.005 to +0.042, with 98-100% power to detect a local sign stock covering 15% of tokens). Lothal, Kalibangan and Dholavira show no difference either, but most of those comparisons are underpowered. Chanhu-daro, a small craft town, is the most distinct site in every comparison (AUC 0.61-0.68). It clears the within-city floor against Harappa, but it does not clear its own permutation null. Among readable seal-type corpora, whole legends carry their site well above their within-city floors (Ur III +0.16 to +0.31, Latin instrumentum +0.12 to +0.14). Once personal names are removed, Ur III legends separate two reigns of one city as strongly as two cities.

Do not write:
- "no spatial structure at any scale", or "uniform across all sites".
- "readable seal corpora separate their sites even without names". Name-free Ur III fails against its reign floor, and name-free Latin and Old Babylonian are underpowered.
- the tablet AUC (0.77) as a Mohenjo-daro vs Harappa place difference.

## Part 1 table: between minus within (median AUC, matched size, 50 draws)

Gate = planted new100 stock at q = 0.15, labels permuted, detected when AUC ≥ max(0.65, null q95); it passes at ≥ 80%. Bold rows are the structural floors that enter the verdict. p (floor) has a minimum of 0.020.

| corpus | variant | within split | n/side | between | within | Δ | p (floor) | gate |
|---|---|---|---|---|---|---|---|---|
| **Ur III impressions (ORACC)** | whole | **Umma reigns** | 227 | 0.876 | 0.718 | **+0.158** | 0.020 | 100% |
| | whole | **Umma BM vs Yale** | 171 | 0.865 | 0.623 | **+0.243** | 0.020 | 100% |
| | whole | Umma random halves | 227 | 0.875 | 0.470 | +0.404 | 0.020 | 100% |
| | whole | **Girsu reigns** | 199 | 0.867 | 0.619 | **+0.248** | 0.020 | 100% |
| | whole | **Girsu BM vs Istanbul L** | 157 | 0.856 | 0.549 | **+0.307** | 0.020 | 100% |
| | whole | Girsu random halves | 227 | 0.876 | 0.520 | +0.355 | 0.020 | 100% |
| | name-free | **Umma reigns** | 68 | 0.599 | 0.590 | **+0.009** | 0.431 | 82% |
| | name-free | Umma BM vs Yale | 41 | 0.598 | 0.531 | +0.067 | 0.098 | 44% |
| | name-free | Umma random halves | 88 | 0.642 | 0.394 | +0.247 | 0.020 | 88% |
| | name-free | Girsu reigns | 58 | 0.604 | 0.698 | −0.094 | 1.000 | 62% |
| | name-free | Girsu BM vs L | 52 | 0.582 | 0.569 | +0.013 | 0.333 | 74% |
| | name-free | Girsu random halves | 88 | 0.630 | 0.518 | +0.112 | 0.020 | 82% |
| | name-free + owner | 6 splits | 19-40 | 0.67-0.76 | 0.49-0.57 | +0.10 to +0.24 | | 18-40% |
| **Ur III seals, one per seal (CDLI)** | whole | Umma reigns | 227 | 0.865 | 0.700 | +0.165 | 0.020 | 100% |
| | whole | Girsu reigns | 197 | 0.853 | 0.631 | +0.222 | 0.020 | 100% |
| | whole | Umma / Girsu random halves | 227 | 0.858 / 0.856 | 0.476 / 0.488 | +0.381 / +0.368 | 0.020 | 100% |
| | name-free | Umma reigns | 72 | 0.651 | 0.618 | +0.033 | 0.078 | 76% |
| | name-free | Girsu reigns | 48 | 0.622 | 0.696 | −0.075 | 1.000 | 64% |
| | name-free | Umma / Girsu random halves | 104 / 97 | 0.681 / 0.669 | 0.477 / 0.512 | +0.205 / +0.158 | 0.020 | 84% / 82% |
| | name-free + owner | 4 splits | 28-50 | 0.57-0.63 | 0.45-0.56 | +0.02 to +0.17 | | 14-32% |
| **Latin instrumentum owner/maker marks (EDH)** | whole | **Germania RLP vs BW + Hessen** | 128 | 0.705 | 0.582 | **+0.123** | 0.020 | 100% |
| | whole | **Britannia north vs south** | 73 | 0.659 | 0.517 | **+0.143** | 0.020 | 100% |
| | whole | Germania / Britannia random halves | 214 / 111 | 0.705 / 0.698 | 0.424 / 0.427 | +0.281 / +0.270 | 0.020 | 100% / 96% |
| | name-free | Germania RLP vs BW + He | 42 | 0.700 | 0.602 | +0.099 | 0.020 | 54% |
| | name-free | Britannia north vs south | 29 | 0.711 | 0.511 | +0.200 | 0.020 | 36% |
| | name-free | Germania / Britannia random halves | 75 / 50 | 0.749 / 0.726 | 0.498 / 0.482 | +0.251 / +0.244 | 0.020 | 72% / 78% |
| **Old Babylonian impressions (ORACC), Nippur vs Isin** | whole | Nippur random halves | 65 | 0.812 | 0.431 | +0.381 | 0.020 | 78% |
| | whole | Isin random halves | 31 | 0.789 | 0.512 | +0.277 | 0.020 | 56% |
| | name-free | Nippur / Isin random halves | 11 / 8 | 0.554 / 0.470 | 0.210 / 0.367 | +0.34 / +0.10 | | 6% / 10% |

Latin stamped marks, within Germania only (Britannia has 13 stamped labels, too few for a between):
- RLP vs BW + He: 0.562 whole (63 per side), 0.454 name-free (19 per side).
- Random halves: 0.464 whole (109), 0.543 name-free (40).

These floors are at or below the instrumentum floors above.

**Family verdicts.**

| tier | Ur III | Latin | Old Babylonian | Part 1 |
|---|---|---|---|---|
| whole | above floor (min Δ +0.158) | above floor (min Δ +0.123) | underpowered | **SUPPORTED** |
| name-free | **not above floor** (Δ +0.009, gate 82%) | underpowered | underpowered | **REFUTED** |

Reading:
- **Reign floors are not small.** Whole Ur III legends separate two reigns of one city at 0.62-0.72; random halves give 0.47-0.52.
- **The between-city value stays far above the reign floors with names in.** Names of owners, fathers and local gods are where Ur III place signal lives.
- **What remains without names.** The titles, offices and royal epithets left after name removal change with reign as much as with city.
- **CDLI replicates ORACC.** Counting each physical seal once gives the same pattern (whole Δ +0.17 / +0.22; name-free +0.03 / −0.08). So repeated impressions of one seal do not drive the Ur III result.

## Part 2 table: all-site Indus map

Columns:
- Δ = between − within. The within floor is random halves of the larger site at the same n.
- Power = share of draws with a planted 20-sign stock in the smaller site (at q of its tokens) where AUC − within median ≥ 0.05. The gate is power ≥ 80% at q = 0.15.
- q values are Benjamini-Hochberg within each family; p has a minimum of 0.020.

| family | a (larger) | b | n/side | between | within | Δ | q floor | q chance | power 10/15/20% | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| M77 seals | Mohenjo-daro | Harappa | 200 | 0.540 | 0.535 | +0.005 | 0.458 | 0.245 | 54/98/100 | **same** |
| | Mohenjo-daro | Lothal | 60 | 0.469 | 0.487 | −0.018 | 0.627 | 0.549 | 54/70/94 | underpowered |
| | Mohenjo-daro | Chanhu-daro | 42 | 0.627 | 0.516 | +0.111 | 0.163 | 0.245 | 82/94/100 | underpowered |
| | Mohenjo-daro | Kalibangan | 38 | 0.583 | 0.481 | +0.102 | 0.270 | 0.245 | 74/76/98 | underpowered |
| | Harappa | Lothal | 67 | 0.538 | 0.471 | +0.068 | 0.196 | 0.327 | 76/90/100 | underpowered |
| | Harappa | Chanhu-daro | 44 | 0.631 | 0.466 | +0.164 | 0.098 | 0.245 | 98/98/100 | **differs** |
| | Harappa | Kalibangan | 44 | 0.569 | 0.445 | +0.125 | 0.157 | 0.245 | 86/96/98 | underpowered |
| | Lothal | Chanhu-daro | 34 | 0.571 | 0.330 | +0.241 | 0.065 | 0.245 | 100/100/100 | differs* |
| | Lothal | Kalibangan | 34 | 0.602 | 0.324 | +0.278 | 0.065 | 0.245 | 100/100/100 | differs* |
| | Chanhu-daro | Kalibangan | 22 | 0.605 | 0.397 | +0.207 | 0.065 | 0.245 | 88/90/86 | differs* |
| ICIT seals | Mohenjo-daro | Harappa | 172 | 0.525 | 0.510 | +0.014 | 0.447 | 0.447 | 64/100/100 | **same** |
| | Mohenjo-daro | Dholavira | 41 | 0.502 | 0.512 | −0.010 | 0.588 | 0.510 | 32/58/80 | underpowered |
| | Mohenjo-daro | Chanhu-daro | 37 | 0.612 | 0.476 | +0.136 | 0.235 | 0.235 | 94/96/92 | underpowered |
| | Harappa | Dholavira | 47 | 0.575 | 0.527 | +0.049 | 0.353 | 0.265 | 54/58/82 | underpowered |
| | Harappa | Chanhu-daro | 39 | 0.624 | 0.546 | +0.078 | 0.353 | 0.235 | 80/82/80 | underpowered |
| | Dholavira | Chanhu-daro | 20 | 0.659 | 0.447 | +0.212 | 0.118 | 0.265 | 76/78/88 | underpowered |
| ICIT seals + sealings | Mohenjo-daro | Harappa | 227 | 0.552 | 0.509 | +0.042 | 0.196 | 0.294 | 96/100/100 | **same** |
| | Mohenjo-daro | Dholavira | 58 | 0.534 | 0.487 | +0.047 | 0.404 | 0.441 | 84/90/96 | same |
| | Mohenjo-daro | Lothal | 49 | 0.519 | 0.490 | +0.029 | 0.441 | 0.561 | 44/76/90 | underpowered |
| | Mohenjo-daro | Chanhu-daro | 38 | 0.652 | 0.499 | +0.153 | 0.176 | 0.294 | 94/98/96 | underpowered |
| | Mohenjo-daro | Kalibangan | 37 | 0.487 | 0.478 | +0.009 | 0.520 | 0.613 | 44/70/80 | underpowered |
| | Harappa | Dholavira | 62 | 0.592 | 0.483 | +0.109 | 0.210 | 0.392 | 92/92/98 | underpowered |
| | Harappa | Lothal | 55 | 0.539 | 0.527 | +0.012 | 0.441 | 0.420 | 44/70/76 | underpowered |
| | Harappa | Chanhu-daro | 40 | 0.680 | 0.493 | +0.187 | 0.074 | 0.294 | 98/100/96 | **differs** |
| | Harappa | Kalibangan | 40 | 0.482 | 0.521 | −0.039 | 0.706 | 0.630 | 16/48/48 | underpowered |
| | Dholavira | Lothal | 30 | 0.494 | 0.469 | +0.025 | 0.441 | 0.630 | 32/54/54 | underpowered |
| | Dholavira | Chanhu-daro | 30 | 0.617 | 0.463 | +0.153 | 0.074 | 0.392 | 86/88/88 | differs* |
| | Dholavira | Kalibangan | 30 | 0.445 | 0.462 | −0.017 | 0.706 | 0.686 | 40/34/48 | underpowered |
| | Lothal | Chanhu-daro | 27 | 0.611 | 0.510 | +0.101 | 0.074 | 0.368 | 72/70/78 | differs (gate fails) |
| | Lothal | Kalibangan | 27 | 0.541 | 0.507 | +0.034 | 0.425 | 0.458 | 38/28/46 | underpowered |
| | Chanhu-daro | Kalibangan | 19 | 0.598 | 0.433 | +0.164 | 0.074 | 0.559 | 86/86/92 | differs* |
| ICIT sealings | Mohenjo-daro | Harappa | 62 | 0.613 | 0.508 | +0.104 | 0.020 | 0.039 | 84/92/94 | differs |
| M77 sealings | Harappa | Mohenjo-daro | 51 | 0.608 | 0.488 | +0.120 | 0.020 | 0.098 | 88/94/94 | differs |
| ICIT tablets | Harappa | Mohenjo-daro | 102 | 0.774 | 0.456 | +0.318 | 0.020 | 0.020 | 100/100/100 | differs** |

\* The floor is random halves of a small site (19-37 per side) and sits at 0.32-0.47. Every between value in these rows (0.57-0.62) is below its own permuted-label null q95 (0.61-0.69). Read these rows as pipeline floor bias, not place signal.
\** Subtype confound: Mohenjo-daro 197 copper (TAB:C) + 94 moulded + 8 incised; Harappa 669 moulded + 563 incised.

**Pre-registered question (frozen rule):** **YES.** Harappa vs Chanhu-daro "differs" in two editors while Mohenjo-daro vs Harappa is "same" in the same families. **Robustness reading:**
- Chanhu-daro is the only site that is consistently distinct: 0.61-0.68 in all six pairs with Mohenjo-daro or Harappa, across two editors.
- Lothal is not distinct: 0.47-0.54 with the big cities.
- No Chanhu-daro between value beats its own permuted-label null after correction (q_chance 0.18-0.35).
- So "Chanhu-daro differs" is a signal above the within-city floor, not a signal above chance. It needs the confirmation test listed below.

## Deviations

1. Pool counts were taken before the prereg was written (counts only, as in step 1). The prereg states the expected underpowered conditions in advance.
2. Two changes were made to `s2.py` before hashing and before any scoring:
   - a two-tier (whole / name-free) family verdict;
   - removal of M77 miniature tablets (Mohenjo-daro has none).
3. Nothing was changed after scoring. Thresholds, conditions and code are as hashed.
4. Compute lock:
   - All runs went through `board/run.sh` (repo lock, `taskpolicy -b nice -n 20`, one process), Part 1 then Part 2.
   - The shared marker `open-citizen-science/.local/compute.lock.indus` was held by stamp_detector. Its only live process was a network image harvest, so this single-process job ran alongside it, as step 1 and its red team did.

## Could not do, and why

- **No sub-provenience (findspot within the site) for Ur III.** The ORACC and CDLI catalogues have no excavation context for Umma or Girsu legends: 16 of 13,517 Umma texts have an excavation number, and most Umma tablets come from the antiquities market. Reign and museum collection stand in for archive. The Istanbul "L" collection is the closest thing to an excavated Girsu group.
- **Strictly stamped Latin marks** cannot be identified in Britannia. EDH Britannia rarely has commentary (13 stamped of 271), so stamped-only exists only as a within-Germania floor.
- **Old Babylonian name-free** has only 8-11 legends per side, and OB has no archive metadata (random halves only).
- **No new download was needed.** ORACC Old Babylonian and the CDLI seal catalogue + ATF were already on disk. `fetch2.py` documents the public URLs with the generic User-Agent. Other options were rejected:
  - Old Akkadian ORACC has 34 seal-bearing texts.
  - CDLI OB seals have Kutalla 99 vs Ešnunna 49, but those differ in period (OB vs Early OB).
  - Aegean CMS has no readable text.
- **Indus within floors** use random halves of the larger site. Excavation areas exist only for Mohenjo-daro (step 1, red team).

## Next test (not run; would need its own prereg)

The open question is whether Chanhu-daro is distinct by place, period or object mix. Chanhu-daro has 45 ICIT seal-type texts, all without a period band. A test would:
- compare Chanhu-daro against Mohenjo-daro's late levels only;
- use more permutation draws, so the p-value floor sits below 0.02;
- check whether the distinct signs are a few repeated seals carved by one hand.

## Files

- `build2.py`: pools. `data/*.jsonl` are gitignored (third-party text). `sizes2.json` holds the counts.
- `fetch2.py`: source URLs (not run).
- `s2.py`: `sizes`, `run 1`, `run 2`, `report`.
- `sizes.log`, `run.log`, `draws.jsonl`, `results.json`, `table.md`, `ledger_rows.csv`.
