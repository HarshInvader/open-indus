# reg_size: does T4's omission order hold on seals T4 never saw?

Pre-registration: `docs/prereg/reg_size.md`, hash-frozen with `rs_lib.py` and `rs_test.py` (`docs/prereg/HASHES.txt`, tag `reg_size`) before any class share was related to area on the new objects. Before freezing, only coverage, measurement agreement and power (`coverage.py`) and a shuffled-area smoke test were run. No amendments. Ledger rows `rs_*` in `docs/test_ledger.csv`. Log: `rs_test.log`. Numbers: `results.json` (with `coverage.json` folded in). Run from the repo root: `.venv/bin/python experiments/reg_size/rs_test.py`.

## Findings first

1. **By the frozen rule, T4's order replicates on 138 new texts. But the replication comes from the closer end; the connective result does not replicate.**
   - The new set is 139 square seals from Mackay 1938 (Mohenjo-daro, 85 texts) and Vats 1940 (Harappa, 53 texts). Their texts are not among T4's 952.
   - Positive control: +1.14 signs per doubling of area (p = 0.0001). T4 had +1.05.
   - All three predicted signs come out right, and the rank agreement with T4's 8 slopes is rho = 0.79 (permutation p = 0.011).
   - Per class (share change per doubling of area, new vs T4):

     | class | new | p | T4 | prediction |
     |---|---|---|---|---|
     | non-jar closers | -0.027 | 0.006 (Holm 0.019) | -0.021 | kept: yes |
     | post-closers | -0.013 | 0.040 (Holm 0.080) | -0.009 | kept: yes |
     | jar | -0.023 | 0.039 | -0.009 | not predicted |
     | connective | +0.002 | 0.41 | +0.013 | dropped first: sign right, size not |
     | title | +0.014 | 0.10 | +0.007 | not predicted |

   - The connective was T4's headline "dropped first" class. Here it is flat. Its sign flips when Marshall's seals are added or when seals without an animal are removed. So the connective result stays unreplicated.
   - What does replicate: on smaller seals, closers (jar, non-jar closers, post-closers) take a larger share of the text, while titles and openers thin out.
2. **This is a replication on new objects by the same measurers, not by independent ones.**
   - For objects that appear in both sources, ICIT's dimensions are the register's own figures converted from inches. For Mackay, 93% of sides agree within 0.3 mm (median difference 0.03 mm, log-area reliability 0.95). For Vats, 94% agree within 0.3 mm.
   - So the redteam_rank worry ("one 1930s measurement set") still applies. The step forward is that the texts and seals are new. The measurer is not.
3. **On the strictest subset the replication vanishes, but that subset has almost no power.** Dropping every new text within one sign edit of a T4 text leaves 59 texts, where rho = 0.02 (verdict "partial"). With MDEs of 0.03-0.06 per doubling this subset cannot tell the cases apart. It does mean that part of the agreement may come from near-relatives of T4 texts.
4. **Combined data (T4 + new, 1,090 texts) give a stable order (secondary, not independent).**
   - Order, dropped first to kept: connective > title > opener > ticked fish > numeral > post-closer > jar > other closers.
   - Holm over 8 classes: connective +0.011 (Holm 0.011), other closers -0.022 (Holm 0.002), post-closers -0.010 (Holm 0.003).
   - Bootstrap: mean rho with the point order is 0.91, and all three key signs are kept in 100% of 1,000 resamples. Connective rank 1 (95% interval 1-3); other closers rank 8 (6-8). This meets the pre-registered "stable" rule.
   - T4 supplies 952 of the 1,090 texts, so the connective's place here is mostly T4's.

**Bottom line.** Seals T4 never saw confirm that small seal texts keep their closers and lose title/opener material. The "connective dropped first" part does not hold on the new texts. Both T4 and this test use the same 1930s measurers. The test had power 0.45 before the outcome, so passing it means something, and the connective failure is weak evidence against that part.

## Data

| step | n |
|---|---|
| register rows, FEM + EH | 1,344 |
| not square (tablets, bar seals) / no dims / implausible size | 387 / 278 / 9 |
| object is a T4 object (ICIT id) | 142 |
| text equals a T4 analysed text (bridge-canonical) | 199 |
| incomplete text / no M77 link / other type or material | 74 / 53 / 63 |
| **kept: objects / distinct texts** | **139 / 138** (MD 85, Harappa 53) |
| strict subset (no text within 1 edit of T4) | 59 |
| Marshall MIC / Mackay CE extra (sensitivity) | 15 / 12 |

- Texts come from M77 through Mahadevan's serial rule. T4's Wells classes are translated to Mahadevan numbers through the bridge.
- For 221 objects that have both an M77 and an ICIT text, the two give identical counts in all 8 classes for 81% of objects (92-100% per class).
- Sensitivity s7 uses the ICIT text, with T4's classes, wherever an object links to exactly one ICIT text. It gives the same result: rho 0.79, replicated.
- Strata are site only, because the registers give no period. This matches T4's sensitivity s4.
- Using register depth terciles as a time proxy (s5) gives rho 0.90, replicated, and the connective comes back to +0.010.

## Pre-registered tests

| id | prediction | result | verdict |
|---|---|---|---|
| P1 | length rises with area | +1.14 signs/doubling, p = 0.0001 | pass |
| R1 | connective +, other closer -, post-closer - | +0.002 / -0.027 / -0.013 | pass on signs; connective about 0 |
| R2 | rho with T4 slopes >= 0.5 | 0.79 (p = 0.011) | pass |
| verdict | P1 + R1 + R2 | | **replicated** (new objects, same measurers) |
| combined | stable order (mean rho >= 0.8, signs kept >= 90%) | 0.91; 100% | stable (secondary, T4-dominated) |

Power before the outcome: subsamples of 138 T4 texts compared with the rest of T4 pass both rules 45% of the time (signs alone 71%, rho alone 54%). 80% MDE per class on the new set: 0.011 (ticked fish) to 0.038 (numeral) per doubling, and 0.024 for the connective. T4's connective slope (+0.013) is below the new set's MDE, so a flat connective is weak evidence against it.

## Sensitivities (not decisive)

| set | n | P1 | conn | other closer | post-closer | rho | verdict |
|---|---|---|---|---|---|---|---|
| primary | 138 | +1.14 | +0.002 | -0.027 | -0.013 | 0.79 | replicated |
| s1 strict (no 1-edit relatives) | 59 | +1.00 | +0.004 | -0.008 | -0.001 | 0.02 | partial |
| s2 + Marshall | 153 | +0.99 | -0.002 | -0.019 | -0.011 | 0.67 | partial |
| s3 + Marshall + CE | 165 | +0.95 | -0.004 | -0.020 | -0.010 | 0.74 | partial |
| s4 animal seals only | 130 | +1.10 | -0.001 | -0.032 | -0.016 | 0.71 | partial |
| s5 site x depth strata | 114 | +1.27 | +0.010 | -0.033 | -0.009 | 0.90 | replicated |
| s6 single-line | 130 | +1.13 | +0.001 | -0.019 | -0.016 | 0.62 | replicated |
| s7 ICIT text where linked | 138 | +1.14 | +0.002 | -0.027 | -0.013 | 0.79 | replicated |

- s2-s4 are "partial" only because the connective sign flips. s1 is "partial" because its rho fails. The two closer classes keep their signs in every set. rho is 0.62-0.90 everywhere except the 59-text strict subset.
- Marshall's measurements are poor (log-area reliability 0.69 against ICIT), which is why they were kept to sensitivity only.

## Caveats

- **Same measurers.** Mackay and Vats measured both T4's catalogue-site seals and these new ones. A measurer or workshop habit shared across both sets is not excluded.
- **Translation.** New texts are M77 readings put through bridge-translated classes. 19% of objects differ from the ICIT reading in at least one class count, which adds noise. The s7 check, which uses ICIT where possible, gives the same result.
- **No steatite filter for Harappa.** Vats records colour, not material.
- **Unit choices.** Strata are site, not site|period. Pooling by distinct M77 text means a text shared by two new seals counts once.
- **Near-relatives.** The strict subset suggests part of the agreement may come from near-copies of T4 texts. It is too small to decide this.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Small seals keep closers (non-jar, post-closer) while titles/openers thin out, on new objects | supported (new objects; same measurers) |
| Small seals drop the connective first | not replicated (new +0.002, p 0.41; sign unstable) |
| Combined T4 + new give a stable omission order | supported (secondary; T4-dominated) |
| The order is measurer-independent | untested (no independent measurements exist in reach) |

## Next

1. A measurer-independent test needs new face measurements, e.g. from CISI scale-bar photos at 30 px/mm or better, or the HARP database for Harappa.
2. Freeze "closers take a larger share on small seals" and "connective flat" as forward predictions for Dholavira, Lothal and other new-site seals with metric dimensions.

## Files

- `rs_lib.py`: new-set builder, class translation, T4 exclusion (frozen)
- `rs_test.py`: frozen test → `results.json`, `rs_test.log`
- `coverage.py` → `coverage.json`: pre-outcome counts, measurement and text agreement, power
