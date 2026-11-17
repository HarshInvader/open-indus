# redteam_size: is the "small seals keep their closers" omission order just "texts have one closer"?

Pre-registration: `docs/prereg/redteam_size.md`, hash-frozen with `rt_size.py` (`docs/prereg/HASHES.txt`, tag `redteam_size`) before the real run. Before freezing, one smoke run with area shuffled was used to check the pipeline. It showed only 13 new texts link to an ICIT steatite object, so the material check (A3d) became "Mackay FEM only". That change is written into the frozen document. Ledger rows `rts_*`. Log `rt_size.log`, numbers `results.json`. Post hoc check: `explore_dups.py` / `.log`. Run: `.venv/bin/python experiments/redteam_size/rt_size.py`.

Claim attacked: "On small seals, closers keep their share while other classes are dropped. The omission order is stable and replicates (rho 0.79)."

## Verdicts

| attack | verdict | key numbers |
|---|---|---|
| A1 mechanical artefact | **fails** | Non-jar closer slope equals the obligatory-closer null exactly (T4 -0.0212 vs -0.0212, p = 0.998; new set p = 0.43). Residual order T4 vs new: rho 0.52, exact p = 0.098. Mechanics alone give a replication rho with median 0.52; P(rho >= 0.79) = 0.13 |
| A2 independence | **weakened** | Exact 8! p for rho 0.786 = 0.014. Family-disjoint rho 0.93 (n = 68, p = 0.001). Family cluster bootstrap median 0.63 [0.10, 0.93], P(rho >= 0.5) = 0.75. **41 of 138 "new" texts are T4 seals counted twice** |
| A3 confounds | **survives** | rho 0.81 / 0.83 / 0.81 / 0.69 under seal-type strata / unicorn only / site-only strata / FEM only. Closer slopes are negative in every variant |

**What the claim reduces to.** Most texts carry about one closer, and the number of closers barely grows with length. In T4 the closer count rises only +0.046 per doubling of area (p = 0.10), against the +0.157 that uniform deletion predicts. The remaining signs thin out roughly at random. The closer classes' "kept" share slopes, and most of the 0.79 rank agreement, follow from that alone. The data support one statement: "closers are obligatory, about one per text." They do not support a graded omission order.

## A1 Mechanical artefact

Method: each dataset keeps its real areas, strata and lengths. A text's signs are simulated by taking a long text (6+ signs) from the same site and cutting it down to the observed length, 1,000 times. The share slope is measured with T4's own estimator.
- N1: signs deleted uniformly.
- N2: all closers (jar, non-jar, post) kept, the rest deleted uniformly.
- N2b: only non-jar closers and post-closers kept.

Earlier tests used a null that permutes area. That null removes the length-area link itself, so any class whose count does not fall with length looks "kept" under it.

| class | T4 obs | N1 | N2 | p vs N2 | new obs | N1 | N2 | p vs N2 |
|---|---|---|---|---|---|---|---|---|
| connective | +0.013 | -0.001 | +0.006 | 0.13 | +0.002 | -0.003 | +0.003 | 0.92 |
| title | +0.007 | +0.001 | +0.005 | 0.80 | +0.014 | +0.004 | +0.007 | 0.54 |
| opener | +0.003 | -0.002 | +0.003 | 0.92 | +0.010 | +0.001 | +0.005 | 0.65 |
| numeral | -0.004 | +0.001 | +0.008 | 0.024 | +0.008 | +0.003 | +0.008 | 0.99 |
| jar | -0.009 | -0.002 | -0.035 | 0.001 | -0.023 | -0.007 | -0.033 | 0.47 |
| other closer | -0.021 | -0.001 | **-0.021** | 0.998 | -0.027 | +0.004 | -0.014 | 0.43 |
| post-closer | -0.009 | -0.001 | -0.005 | 0.40 | -0.013 | -0.002 | -0.006 | 0.42 |

(Share change per doubling of area. N1 p for other closer: T4 0.001, new 0.008.)

- **Closers are not deleted at random.** Against N1 the non-jar closer departs in both sets. Its presence also stays flat as the face shrinks (T4 -0.014 per doubling vs N1 +0.052, p = 0.001). That is a real fact.
- **Beyond being obligatory, there is nothing left.** Against N2 neither non-jar closers nor post-closers depart in either set. That fails the K criterion.
- **The jar is less protected than the other closers.** In T4 its observed slope (-0.009) lies between N1 and N2 (+0.026 above N2, p = 0.001). It behaves like a frequent but optional closer.
- **Order (O criterion).** After N2 is subtracted, the residuals of T4 and the new set correlate at rho 0.52 (exact p = 0.098), so O fails. The pre-registered rule gives **fails**.
  - Secondary: with N2b, residual rho = 0.71 (p = 0.029). The leftover agreement comes from the jar's intermediate place. It is not a graded order of connective > title > opener.
  - Mechanics alone, with T4's observed slopes and N2 draws on the new set, give a replication rho with median 0.52 and 95% interval [-0.19, 0.90].
- **T4's connective "dropped first" (+0.013).** Against N1 it is p = 0.027 (Holm 0.16). Against N2 it is p = 0.13. Under N2 it is not significant in either set.
- Templates of any length (sensitivity) give the same picture (N2_any: other closer p = 0.81 / 0.36).

## A2 Independence of the replication

- **Only 8 points.** The exact one-sided permutation p over all 40,320 orderings is 0.014 for rho = 0.786. This matches reg_size's 0.011.
- **Same objects counted twice.**
  - 41 of the 138 new texts sit at the same site as a T4 text, with area within 3% and a text within one edit or contained.
  - Shifting the new areas by ±0.1-0.3 in log area gives 0-3 such matches, so these are not chance.
  - All 41 lack an ICIT link in the register. Their M77 reading differs from the ICIT reading by one bridge-unmatched token, which let them slip past both of reg_size's exclusions (object id and exact canonical text).
  - Example: M267 M99 M67 M205 M245 M342 = T4's W817 W002 W240 W495 W615 W740.
  - So about 30% of the "new seals" are T4 seals read twice. Without them, rho = 0.95 (n = 97, p = 0.0006). They are a flaw in the independence claim but do not drive the rho.
- **Near-copy families.** These use `corpus.build._close` on canonical tokens: 671 families over T4 + new, and 70 of 138 new texts share a family with T4.
  - The family-disjoint new set (68 texts) gives rho 0.93 (p = 0.001). This differs from reg_size's strict s1 (rho 0.02), which used a looser one-edit rule that also links short texts.
  - Cluster bootstrap over families: median rho 0.63, 95% interval [0.10, 0.93], P(rho >= 0.5) = 0.75. That is below the 0.8 bar, so the verdict is **weakened**.
- **Same measurers (Mackay, Vats).** Not testable here, as reg_size already said.

## A3 Confounds

| variant | T4 other / post closer | new other / post closer | rho(T4, new) |
|---|---|---|---|
| + seal type in strata (unicorn / other animal / none) | -0.024 / -0.010 | -0.029 / -0.012 | 0.81 (p 0.011) |
| unicorn seals only (720 / 95) | -0.027 / -0.010 | -0.034 / -0.008 | 0.83 (p 0.008) |
| site-only strata (no period) | -0.022 / -0.009 | -0.027 / -0.013 | 0.81 |
| material: new set Mackay FEM only (85) | (T4 steatite) | -0.032 / -0.004 | 0.69 (p 0.035) |

- Seal type, period and material do not create the slopes, so A3 **survives**.
- In every variant the closer residuals against N2 stay null (|z| ≤ 1.7). The confound checks keep the slopes but do not rescue A1.
- Descriptive: text-only seals are rare (T4 27, new 5). Their texts are shorter, and in T4 they carry a closer less often (0.48 vs 0.82).

## Consequences for the project

1. Restate the T4 / reg_size finding as: **"Seal texts carry about one closer regardless of length (closers are not shed as the face shrinks); the other classes thin about uniformly; the jar is in between."** Drop the "omission order (connective > title > opener > ...)" and the reading of rho 0.79 as replicating an order. Most of that rho is expected from the obligatory-closer mechanism (median 0.52, upper 95% 0.90).
2. reg_size's new set includes 41 T4 objects. Any further use of that set must exclude them by site + area + close text, not by ICIT id or exact text alone.
3. Any future "share vs size" test needs a mechanical null that preserves length and protects obligatory slots. An area-permutation null is not a test of uniform thinning.

## Files

- `rt_size.py`: frozen test → `results.json`, `rt_size.log`
- `explore_dups.py` → `explore_dups.log`: post hoc chance rate and examples of the double-counted objects
