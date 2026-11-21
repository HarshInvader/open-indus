# Pre-registration: Chanhu-daro follow-up

Date: 2026-11-21. Written after the Part 1 red team (`experiments/redteam_uniformity_step2/RESULTS.md`) was finished. Pool counts were taken first (`experiments/chanhudaro_followup/sizes.log`, counts only). No condition had been scored. Code: `experiments/chanhudaro_followup/cd.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `chanhudaro_followup`).

## Question

Step 2 found Chanhu-daro seals above the Harappa within-site floor (+0.16 / +0.19) but not above their own shuffled-label null (q 0.18 to 0.35). The red team kept that result: Δ_cons +0.117 / +0.183, q_chance ≥ 0.235. Is any Chanhu-daro difference better explained by one of these?

- place;
- period (Jhukar-level seals);
- a few repeated seals or near copies;
- one findspot (a workshop or hoard);
- a few signs (such as M93, often called a Chanhu-daro end mark);
- iconography or format.

## Method (fixed)

- Every condition uses the benchmark's own `clean()` (strings at both sides dropped, then `fish_tick_closer_v2/dedup.py` greedy) and `draw_n()` (Indus length mix). Scoring uses `score()`: the frozen NB pipeline plus one permuted-label AUC per draw. No new classifier. `corpus/build.py::_close` is not used.
- Pools are step-2 `s2.indus_raw`: M77 complete seals, and ICIT complete seal-type objects (SEAL*).
- Four baseline pairs: Harappa–Chanhu-daro and Mohenjo-daro–Chanhu-daro, in m77_seal and in icit_sealtype.
- Floor: the bigger site's random halves (`s2.indus_within`), drawn at the same n per side as the between condition.
- Seed 20261128.
- Δ_cons = median between − max(median within floor, median permuted-label AUC). This is the red-team "conservative" reference. Margin 0.05.
- p_chance = (1 + permuted AUCs ≥ median between) / (1 + draws). BH correction runs over the 4 baseline pairs.
- Power gate: `s2.plant_side`, a 20-sign stock at q = 0.15 in the Chanhu-daro texts with real labels. Detected when AUC − max(within median, null median) ≥ 0.05. Passes at ≥ 80%, otherwise "underpowered". 50 draws.

## T0. Is Chanhu-daro distinct? (baseline)

200 between draws and 200 within draws per pair, at a matched n (m77 44 / 42, ICIT 40 / 38). A pair is "distinct" if all three hold:

- Δ_cons ≥ 0.05;
- q_chance ≤ 0.05;
- the gate passes.

The baseline verdict depends on how many of the 4 pairs are distinct:

| distinct pairs | verdict |
|---|---|
| ≥ 3 | **distinct** |
| ≤ 1 | **not distinct** |
| 2 | **equivocal** |

## Explanation tests

Each test changes only the Chanhu-daro side of the pair. Each is scored with 50 draws at n matched to the bigger site's floor, and compared with the same pair's T0 Δ_cons.

The "accounts for" rule for a pair: after the change, Δ_cons < 0.05, or Δ_cons falls by at least half of the T0 Δ_cons. A test **accounts** if it accounts in both m77 pairs. It is **partly** if it accounts in one, and **does not account** if it accounts in neither. T1, T3b and T5 use the M77 pairs only, because the Mackay metadata link to M77 text numbers.

- **T1 period.** Drop Chanhu-daro seals whose Mackay 1943 register depth (experiments/old_registers/registers.csv, source Mackay1943_CE, linked by m77_text_no) is ≥ +13.7 ft on Mound II. That is the lowest Jhukar floor Mackay reports. The counts show only 1 such seal among the 50 M77 seals; 35 have a register depth. T1 therefore cannot account for much, and it is reported as written.
- **T1b within-Chanhu-daro depth floor.** Chanhu-daro register-dated Mound II seals are split at the median depth, deep vs shallow (17 per side). The big site vs Chanhu-daro is drawn at the same n = 17, with a gate. If the gate fails in either pair, the result is "underpowered". Otherwise it "accounts" when between − depth floor < 0.05 in both pairs.
- **T2 repeats.** Strict near-copy de-dup (`rt2.strict_clean`):
  - `clean()`;
  - then `dedup.greedy` with MIN_DROP = 2;
  - then one text per sign multiset.
- **T5 one findspot.** Drop the Chanhu-daro seals from the most common register square (9/D, 6 seals).
- **T3 a few signs.**
  - Stage 1, leave-one-sign-out: for every sign with ≥ 5 tokens on the Chanhu-daro side of the cleaned m77 pair (12 signs vs Harappa, 11 vs Mohenjo-daro), delete that sign everywhere in both sites and score 30 draws. Compare with a 30-draw unmanipulated baseline at the same n. A sign is a **driver** if its median AUC drops by ≥ 0.03.
  - Stage 2 (T3b), run only if drivers exist: delete all drivers for that pair together and apply the "accounts for" rule.
  - Classifier-free report for the drivers and for M93: share of texts containing the sign, as first sign and as last sign, at Chanhu-daro, Harappa and Mohenjo-daro (raw complete M77 seals).
- **T4 iconography / format.** ICIT unicorn-only ("Bull1" field symbol) at both sites, with the bigger site's unicorn-only random-halves floor. Gated, using the ICIT T0 Δ_cons for the "accounts for" rule. If either gate fails, the result is "underpowered".
- **T4b.** Report only: Mohenjo-daro unicorn vs Mohenjo-daro no-symbol seals at n = 40, as a reference for the size of a format effect.

## Final category (rule)

1. T0 "not distinct": **NO ROBUST DIFFERENCE**. The tests are still reported, but no explanation is needed.
2. Otherwise, if any test accounts: **EXPLAINED BY** those tests (place not needed).
3. Otherwise, if any test is underpowered: **PLACE NOT EXCLUDED**, with the underpowered alternatives listed.
4. Otherwise: **PLACE**. Chanhu-daro is distinct, and no tested alternative accounts for it.

When T0 is equivocal, the prefix "EQUIVOCAL BASELINE" is added.

## Compute and data

- `board/run.sh`, background priority, one process, one heavy job at a time. Order: `run main`, then `run loso`, then `run drivers`.
- Third-party texts stay in the gitignored corpus. Outputs hold counts and AUCs only.
- Thresholds are not changed after data are seen. Deviations are logged in RESULTS.md.
