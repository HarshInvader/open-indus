# Chanhu-daro follow-up: results

Prereg: `docs/prereg/chanhudaro_followup.md`, hashed with `cd.py` at 2026-11-21T17:43:05Z (tag `chanhudaro_followup`). Code re-hashed at 17:51:49Z after deviation 1 (tag `chanhudaro_followup_deviation1`). 4,180 scored draws; no failures left after deviation 1.

## Verdict

**NO ROBUST DIFFERENCE, by the frozen rule.**

Chanhu-daro seals sit +0.13 to +0.17 above both the within-site floor and the shuffled-label null, in all four pairs (Harappa and Mohenjo-daro, M77 and ICIT). A planted local stock is found 96 to 98% of the time. But each pair's chance p is only 0.02 to 0.06, and after correction every q is 0.06. So 0 of 4 pairs clear the "distinct" bar (q ≤ 0.05).

The baseline is a consistent near-miss, not a null. The four pairs share the same 40-odd Chanhu-daro seals, so they are not four independent replications.

**What drives the gap that is there:**

- **Not period.**
  - Only 1 of 50 M77 Chanhu-daro seals lies at the Jhukar levels (Mackay 1943 register, Mound II ≥ +13.7 ft).
  - Dropping it changes nothing (Δ_cons +0.151 to +0.139 vs Harappa, +0.134 to +0.126 vs Mohenjo-daro).
  - A finer within-Chanhu-daro deep-vs-shallow floor is underpowered: 17 seals per side, gate 26% / 16%.
- **Not repeated seals or near copies.**
  - Strict de-dup removes 4 to 6 Chanhu-daro seals.
  - The gap grows, to +0.16 to +0.21.
- **Not one findspot.** Dropping the 6 seals from Square 9/D leaves the gap at +0.13 to +0.18.
- **Not iconography or format.**
  - Unicorn seals only: +0.138 vs Harappa (base +0.173), +0.099 vs Mohenjo-daro (base +0.138).
  - Gates 88% / 80%.
- **Partly a few signs, chiefly M93.**
  - M93 is on 20% of Chanhu-daro M77 seals and is the last sign on 16% of them. It is on 0 of 251 Harappa seals and 0 of 1,026 Mohenjo-daro seals.
  - Removing M93 is the largest leave-one-sign-out drop in both pairs: −0.040 vs Harappa, −0.126 vs Mohenjo-daro.
  - Removing the drivers together roughly halves the gap:
    - vs Mohenjo-daro (M93 + M123): +0.134 to +0.057, which meets the "accounts for" rule;
    - vs Harappa (M93 + M293): +0.151 to +0.078, which misses the half-drop rule by 0.002.
  - So "a few signs" is rated "partly".

In plain terms, the evidence leans toward place, carried in part by a local end sign. M93 is a Chanhu-daro end mark: it ends texts and is absent from the two big cities' seals. It does not lean toward period, copies or one workshop. But the place signal is not strong enough to call Chanhu-daro distinct after correction.

## Safe paper wording

> Chanhu-daro seals separate from Harappa and Mohenjo-daro seals by a consistent margin (+0.13 to +0.17 AUC above both the within-site floor and a shuffled-label null, in two editions; power 96 to 98%). The margin does not reach significance after correction (q = 0.06 in each pair), so we do not claim a Chanhu-daro place signal. The margin does not come from Jhukar-period seals (one seal), near-duplicate seals (de-duplication enlarges it), a single findspot, or unicorn-type format. About half of it comes from a few signs, mainly M93: it ends one Chanhu-daro seal text in six and does not occur on Harappa or Mohenjo-daro seals in the M77 corpus. Without these signs the margin falls to +0.06 to +0.08.

Do not write "Chanhu-daro differs" or "Chanhu-daro is a separate scribal tradition". Do not write that period was excluded: we excluded only the Jhukar-level seals, and the within-site depth floor was underpowered.

## Deviations

1. **Leave-one-sign-out failures.** Seven conditions had no valid draw: M342, M87 and M93 vs Harappa; M342, M343, M67, M87 and M93 vs Mohenjo-daro.
   - Cause: deleting the sign made 1 to 3 Chanhu-daro texts identical, `clean()` merged them, and the side fell below the fixed n.
   - Fix: they were rescored at their own natural n (40 to 43) against an unmanipulated baseline drawn at the same n (`L2_` / `LB2_`), with the same driver threshold (0.03) and draws (30). The code was re-hashed before this scoring (tag `chanhudaro_followup_deviation1`).
   - Effect: the new driver set adds M93 to both pairs. The combined-removal test was rerun as `BD2_`.
   - The original stage-2 run (`BD_`, drivers from the first pass only: M293 vs Harappa, M123 vs Mohenjo-daro) is kept in results.json. It gave Δ_cons +0.135 / +0.102, so it does not account.
2. **Shared compute lock.** The shared compute lock (`open-citizen-science/.local/compute.lock.indus`) was gone by the time Part 2 ran, so there was no conflict. The repo lock was taken by `board/run.sh` for every stage. This is noted only for completeness.
3. **LOSO noise.** The 30-draw LOSO medians have a standard error of about 0.02, so the 0.03 driver threshold is noisy for every sign except M93 vs Mohenjo-daro (−0.126). M293 and M123 sit just over the threshold (0.037 / 0.031). The threshold was not changed.

## Tables

### T0 baseline (200 between + 200 within draws per pair)

| pair | n/side | between | within floor | null | Δ_cons | p_floor | p_chance | q_chance | power | distinct |
|---|---|---|---|---|---|---|---|---|---|---|
| M77 Harappa–Chanhu-daro | 44 | 0.646 | 0.451 | 0.495 | +0.151 | 0.005 | 0.050 | 0.06 | 96% | no |
| M77 Mohenjo-daro–Chanhu-daro | 42 | 0.641 | 0.497 | 0.507 | +0.134 | 0.055 | 0.050 | 0.06 | 96% | no |
| ICIT Harappa–Chanhu-daro | 40 | 0.676 | 0.503 | 0.488 | +0.173 | 0.005 | 0.020 | 0.06 | 98% | no |
| ICIT Mohenjo-daro–Chanhu-daro | 38 | 0.638 | 0.500 | 0.497 | +0.138 | 0.085 | 0.060 | 0.06 | 96% | no |

### Explanation tests (50 draws; Δ_cons against the same pair's floor and null)

| test | pair | n/side | between | Δ_cons | base Δ_cons | accounts |
|---|---|---|---|---|---|---|
| T1 drop Jhukar-level (1 seal) | M77 HA | 43 | 0.637 | +0.139 | +0.151 | no |
| | M77 MD | 41 | 0.622 | +0.126 | +0.134 | no |
| T2 strict near-copy de-dup | M77 HA | 39 | 0.705 | +0.212 | +0.151 | no |
| | M77 MD | 36 | 0.661 | +0.164 | +0.134 | no |
| | ICIT HA | 36 | 0.694 | +0.192 | +0.173 | no |
| | ICIT MD | 32 | 0.714 | +0.212 | +0.138 | no |
| T5 drop Square 9/D (6 seals) | M77 HA | 39 | 0.647 | +0.137 | +0.151 | no |
| | M77 MD | 37 | 0.628 | +0.131 | +0.134 | no |
| T3b drop drivers (M93 + M293) | M77 HA | 43 | 0.586 | +0.078 | +0.151 | no (drop 0.073 vs 0.0755 needed) |
| T3b drop drivers (M93 + M123) | M77 MD | 41 | 0.559 | +0.057 | +0.134 | **yes** |
| T4 unicorn only | ICIT HA | 31 | 0.630 | +0.138 | +0.173 | no (power 88%) |
| | ICIT MD | 30 | 0.593 | +0.099 | +0.138 | no (power 80%) |

T5 for ICIT has no findspot data, so its pools are unchanged: +0.176 / +0.129.

The T4b reference (Mohenjo-daro unicorn vs no-symbol seals, n = 40) is 0.649 (null 0.501). A format split inside one city is about as large as the Chanhu-daro gap. So the unicorn-only control matters, and it leaves most of the gap in place.

### T1b within-Chanhu-daro depth floor (Mackay register depth, Mound II, median split, n = 17)

| | between | Chanhu-daro deep vs shallow | difference | power | verdict |
|---|---|---|---|---|---|
| Harappa–Chanhu-daro | 0.627 | 0.658 | −0.031 | 26% | underpowered |
| Mohenjo-daro–Chanhu-daro | 0.603 | 0.658 | −0.055 | 16% | underpowered |

At n = 17, deep vs shallow Chanhu-daro seals separate at least as well as Chanhu-daro vs the big cities. The test has no power, so this neither shows nor excludes a stratigraphic effect.

### T3 leave-one-sign-out (30 draws; drop = baseline median − median without the sign)

| sign | drop vs Harappa | drop vs Mohenjo-daro |
|---|---|---|
| M93 | **+0.040** | **+0.126** |
| M293 | **+0.037** | +0.011 |
| M123 | +0.021 | **+0.031** |
| M12 | +0.028 | +0.001 |
| M65 | +0.028 | (< 5 tokens) |
| M162 | +0.015 | +0.002 |
| M342 | −0.025 | +0.014 |
| M343 | −0.001 | +0.010 |
| M267 | +0.010 | −0.011 |
| M67 | +0.005 | −0.002 |
| M99 | −0.011 | +0.004 |
| M87 | −0.019 | −0.041 |

### Classifier-free sign profile (raw complete M77 seals; share of texts)

| sign | Chanhu-daro (50) has / first / last | Harappa (251) has / first / last | Mohenjo-daro (1,026) has / first / last |
|---|---|---|---|
| M93 | 0.20 / 0.00 / 0.16 | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 |
| M293 | 0.12 / 0.08 / 0.00 | 0.04 / 0.02 / 0.01 | 0.06 / 0.04 / 0.00 |
| M123 | 0.14 / 0.00 / 0.00 | 0.06 / 0.00 / 0.00 | 0.10 / 0.00 / 0.00 |

## Files

- `cd.py`: code. Modes: `sizes`, `run main|loso|loso2|drivers|drivers2`, `report`.
- `sizes.log`, `run.log`: logs.
- `draws.jsonl`: per-draw AUCs and null AUCs only, with no texts.
- `results.json`: full report.
- `ledger_rows.csv`: ledger rows.
