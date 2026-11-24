# Sizing census: a shape-only power calculator, checked against known outcomes

Prereg `docs/prereg/sizing_census.md`. The prereg was sealed first (tag `sizing_census`), then the code (tag `sizing_census_code`), before any mode ran on a case shape. Run from the repo root:
- `nice -n 20 .venv/bin/python -I experiments/sizing_census/calc.py kill | census | curve`
- then `adopt.py`

Outputs: `kill.json`, `census.csv` and `census.json`, `curve.json`, `u_rows.csv`, `adoption.json`, and the `*.out` logs.

## Kill test: which calculator families reproduce their sealed results
| family | case | result | why |
|---|---|---|---|
| A1 binary tie | tablet bovine (3) | reproduced | 0.03 / 0.14 vs 0.03 / 0.03 |
| A1 | unicorn vs other (4a) | **missed** | 0.73 vs 0.20 at δ 0.05; 0.96 vs 0.73 at δ 0.10 (errors 0.53, 0.23) |
| A1 | F14 shorthorn bull (4b) | reproduced | max error 0.20 (0.80 vs 0.60) |
| A1 | F14 elephant (4c) | reproduced | max error 0.17 |
| A2 rate ratio | harp C6 (5a) | reproduced | 0.81-0.98 vs 0.84-1.00 |
| A3 rank correlation | harp C9 (5b) | **missed** | 0.57 vs 0.82 at n 120; 0.13 vs 0.39 at n 72 |
| B profile recovery | anchor_ceiling v2 (1) | **missed** | dev gate predicted not met (field minimum 0.49 vs sealed ≥ 0.95); held-out adjusted Rand 0.34 vs 0.56 |

**Adopted: A2 only.** A1, A3 and B are not trusted, so their census rows give raw n only.

The misses point in both directions:
- A1 is too optimistic on unicorn. The sealed test there is a whole-text classifier AUC, while the calculator models a single-sign test at α/m.
- A3 and B are too pessimistic.

So the calculator is not a reliable upper bound, as the prereg feared.

## Census (`census.csv`; gate binds only A2 rows)
- **A2 routes, all of which depend on HARP data:**
  - Jar sign on pottery: in hand 65 texts, power 0.53, STOP. With ≥ 184 HARP units, 0.82, passes.
  - Firing stage C1: 35 in hand, 0.44, STOP. 146 with HARP, 0.96, passes.
  - Firing stage C2: 0.44, STOP. With HARP, 0.84, passes.
  - Bangle oval: 0 new texts, STOP (needs 19).
  - Ticked fish by area: 20 seals, 0.05, STOP (needs about 400).
- **A1, A3, B routes:** raw n only (see `census.csv`). The calculator's figures there are not gating. For example, tablet picture × text has 61 rows → 136 with the ICIT code list → about 272. Numerals vs size has rods 13, implements 3, HARP rims 146.
- **Consequence:** no route with data in hand passes an adopted gate. Every A2 pass needs the HARP sheet, expected around 2027-01-05.

## U-row curve (family B, not adopted, so description only)
- Planted fields at d = 2, 3, 5 and 8 documents per word: median adjusted Rand 0.15-0.55. The bar (0.8, every field ≥ 0.8) is not reached at any d.
- d = 12 has no countable plants, and d = 20 is not reachable at this corpus size.
- **No U-row minimum-count rule is adopted.** The descriptive reading is that per-word anchor profiles do not reach field recovery at any document count this corpus offers. This agrees with atlas §3.6.

## Disclosures
- All five known outcomes were known before the design, so the kill test is a calibration check, not a blind one. Hand calculations were made while drafting (prereg disclosure).
- **`adopt.py` was written after the run,** because `calc.py` has no adoption step. It encodes only the prereg's sealed cell values and the R1/R2 rules. "Counted cells" are taken to be the sealed run's counted cells, not `calc.py`'s own feasibility flag: `calc.py` marked every unicorn cell infeasible, which would otherwise have exempted case 4a.
- Implementer choices, as reported:
  - A1 uses closed-form z power when all expected cells are ≥ 5, otherwise simulated Fisher;
  - in family B, draw-0 counts are held fixed across the simulated draws;
  - routes 3 and 12 are upper bounds, since their marginals are not in the repo;
  - 11 U rows needing their own A1 shape are left empty.
- `scott_ic_refute` was excluded at design time: its stop came from lexicon saturation and null width, not from counts.
