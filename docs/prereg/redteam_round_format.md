# Pre-registration: red team of #22's format-control result (board task #23, agent H9)

Written before any of the new statistics below were computed. Already known (from #22, H8): the 9 ICIT home SEAL:C/CY texts score +1.84 KN bits/sign over home square+rectangular seals (p=1e-4); foreign round seals beat them by only +0.37 (p=0.48); grammar scorer on its 12 home round units: +0.41 (p=0.18).

## Claim under attack
"True home circular/cylinder seals are as off-order as Gulf round seals, so the foreign-order signal may be a round-seal format effect."

## Attack 1: are the home circular/cylinder objects really home Indus seals? (documentary)
From local open sources only (CISI vols 1-2 introduction and captions, Mackay 1938 FEM, Marshall 1931, Vats 1940 registers in experiments/old_registers), classify each home SEAL:C/CY object: (a) not a seal (CISI reclassification), (b) Indus-type (perforated boss like square seals), (c) Gulf/Dilmun-type features (boss decoration, no boss, short-horned bull "Gaur" without manger), (d) unknown. Also report whether ICIT field symbol 'Gaur' (the Gulf-type bull) is over-represented on home circular vs home square seals (Fisher exact, descriptive).

## Attack 2: larger home sample
Search ICIT (all types incl. untyped SEAL), the old registers (Mackay/Vats/Marshall seal types, "round") and CISI for further home round/cylinder inscribed seals not in the 9. Add any found with a legible sequence of >=2 signs.

## Attack 3: corrected set
Corrected home set = H8's 9 minus objects that CISI classifies as not seals, plus any added in Attack 2. Re-run the KN comparison (same code as experiments/round_label_audit/fmt_control.py; q4_gulf KN, 10-fold CV, length-matched draws).

## Attack 4: inventory vs order decomposition (the main new test)
For every text with >=2 signs, using 10-fold CV KN models for home texts (model trained on all native texts for foreign texts):
- ORDER component d = bits(real order) - mean bits over 200 random within-text permutations (all permutations if fewer distinct). Sign inventory cancels; d<0 means the real order is more Indus-like than shuffles of the same signs.
- INVENTORY component u = mean bits over the permutations (the same signs in random order).
Group means of d and u for home circular (corrected), foreign round, home square+rect seals; each group vs length-matched home-seal draws (10,000), and foreign round minus home circular by label permutation (20,000, two-sided).

Decision rule (alpha 0.05 each; 4 primary tests: d and u for home circular vs home seals, d and u for foreign round minus home circular; Holm over the 4):
- The format effect "survives" as an ORDER effect if home circular d is higher than home seals (Holm p<0.05).
- If home circular is anomalous only in u (inventory) but not d, the #22 KN result is a sign-inventory effect, not an order effect, and it does not undercut #1/#11's order flags (which are permutation/grammar based).
- Foreign round is "beyond format" on order if foreign minus home circular d > 0 with Holm p<0.05. With n~8 home, report power: the chance of p<0.05 if the true difference equals the foreign-vs-home-seal d difference (simulated by drawing home-circular-sized samples from home seals shifted by that amount).

## Attack 5: why KN and grammar disagree (descriptive)
List the units in each scorer's home-round set; score both sets with KN; report how much of the gap is set membership (e.g. single-sign or common texts in the grammar set) versus scorer.

## Not done
No Indus sound or meaning claims. No change to other agents' folders.
