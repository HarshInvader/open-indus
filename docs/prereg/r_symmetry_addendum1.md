# r_symmetry addendum 1: code choices (sealed with the code, before power mode)

**Native statistics reproduce their published values.**

| test | published | reproduced |
|---|---|---|
| T3 S | 101.0 | 100.9955 |
| round excess | -0.10 | -0.0955 |
| jar pooled ratio | 0.74 | 0.739 |
| Q1 ρ | -0.17 | -0.168 |
| Q2 ρ | +0.08 | +0.076 |
| Q3 χ² | 28.2 | 28.21 |
| T1 | p 0.83 | p 0.8348 |
| emblem AUC | 0.516 | 0.5156 |

**Choices the sealed text did not fix**
1. **Units stay native.** Copy groups, mould-copy identities and distinct texts are built on native labels, and a list only relabels the signs inside them. As a result, Q1-Q3, T1 and the jar are INVARIANT or NT under every list, so cup-vessel-fee can be at most UNCHECKED.
2. **The M77 baseline list is not a family.** It is reported per cell.
3. **Emblem under the three image cuts is NT**, by the sealed numeral-set rule: those cuts put short and tall numerals in one label.
4. **Other-edition sizes after the sealed filters:**
   - licence-pairing: 234 Harappa objects (tiers 2-4), not 242;
   - jar: 115 M77 pottery texts after de-duplication, not 126.
5. **Jar power** uses the exact null mean, so no observed count is read before `test` mode.
6. **Rows with several tests.** A family's kill condition counts as met only if every testable test in it meets it. This is conservative against HOLDS.

**Code:** `experiments/r_symmetry/` — `maps.py`, `run.py`, `summarise.py`, `copied_t_tests.py`, `copied_round.py`, `copied_strokedjar.py`.
