# Red team of #22: is the home round-seal "format effect" real? (board #23, H9)

**Verdict: #22 survives, and the result is sharper.** Round seals found inside the Indus area really do break Indus sign order, about as much as the round seals found in the Gulf and Mesopotamia. The effect is in the **order** of the signs. It is not in which signs are used. Three things fail to break it:
- removing the Harappa object that is not a seal,
- comparing only against home seals that have no near-copies,
- re-scoring with the Wells grammar.

So the "foreign order" signal behind #1, #11 and #4 can't be credited to foreign names over a round-seal (Gulf-type) genre. The archaeology doesn't separate the two either. Three of the 8 home round seals carry the Gulf-type short-horned bull (3/8 against 4% of home seals, p=0.004). At least one of those three has an Indus-type perforated boss. They are best read as Gulf-type seals made or used in the Indus area, so home and foreign round seals are one class.

Pre-registration: `docs/prereg/redteam_round_format.md` (sha256 in HASHES.txt, written before any new number was computed). Code: `run.py`, `grammar_check.py`. Outputs: `results.json`, `grammar_check.json`, `run.log`, `grammar_check.log`. Ledger rows: `ledger_rows.csv`.

## Attack 1: are the home circular/cylinder objects really home seals, or Gulf imports?
I used local open sources only: the CISI 1-2 introductions, Mackay 1938 FEM, Marshall 1931, and Vats 1940 in `experiments/old_registers/raw`.
- **H-368/H-369 (ICIT 1387.1, 1388.1, 1388.2) are not seals.** CISI 1 (intro, fn. 75) classes these two tiny Harappa cylinders as incised tablets. #22's n=9 included 1388.1, so it is dropped here. The corrected set has n=8.
- **Indus round seals are Indus-made in form.** CISI 1 and 2: "the round seals of the Indus Civilization have a perforated boss of the same type as the square seals and differ in this respect from the round 'Dilmun' seal". CISI also says other seal forms are rare and "in most cases inspired by foreign models, if the seal itself is not a foreign import".
  - Mackay's register lists M-415 (ICIT 2911.1, short-horned bull) as "round seal with perforated boss". It is the only round seal from his 1927-31 Mohenjo-daro work, found in upper levels (ICIT: Intermediate).
  - M-500 (2977.1) is "round, thin, no boss, inscribed on both sides", with a stylised tree. That is not Gulf iconography.
- **Iconography.** ICIT field symbol "Gaur" (the short-horned bull of Gulf-type seals) appears on:
  - 3/8 home round seals: M-415, M-416 and Dholavira 4247.1,
  - 77/1,835 home square and rectangular seals (4.2%), Fisher p=0.004,
  - 13/18 foreign round seals.

  The other five home round objects are Chanhu-daro C-32 (bull), two with a tree or plant, one with no device, and the Rakhigarhi cylinder.
- **Reading.** The home round seals are a mixed group. About three are Gulf-type in iconography but Indus-type in boss. The rest are other rare formats. None is shown to be an import, and none is shown not to be one: no photographs of the bosses were checked.

## Attack 2: a larger home sample
None exists in our sources. ICIT has 15 home SEAL:C/CY objects, and only 8 distinct texts with at least 2 legible signs once the Harappa tablets are removed.
- Mackay: one round seal.
- Marshall: the "cylinder seals" are thin ivory rods, which are not seals and are not in this class.
- Vats: the two "tiny cylindrical seals" are the CISI-reclassified tablets.
- M77 has no shape field.
- n=8 is the ceiling until CISI vol. 3 or the Dholavira, Rakhigarhi and Lothal reports are read.

## Attack 3: the corrected set (KN, same code as #22)
| group | n | KN bits/sign | vs length-matched home seals | p |
|---|---|---|---|---|
| #22 set (9) | 9 | 6.93 | +1.91 | 1e-4 |
| corrected home round (8) | 8 | 7.15 | **+2.12** | 1e-4 |
| foreign round | 16 | 7.39 | +2.41 | 1e-4 |

Dropping the tablet makes the home effect a little *larger*.

## Attack 4: order or inventory? (pre-registered primary test)
For each text:
- **d** = KN bits of the real order minus the mean over up to 200 within-text permutations. The sign inventory cancels out.
- **u** = the shuffle mean.

Home texts are scored by 10-fold CV; foreign texts by the all-native model. Texts made of one repeated sign have no order and are excluded (Karzakan W740 W740).

| test | diff | raw p | Holm p (of 4) |
|---|---|---|---|
| home round **order** d vs home seals | **+1.96** (−0.12 vs −2.08) | 1e-4 | **4e-4** |
| home round **inventory** u vs home seals | +0.16 | 0.30 | 0.90 |
| foreign round minus home round, order d | +0.11 | 0.68 | 1.0 |
| foreign round minus home round, inventory u | +0.13 | 0.79 | 1.0 |

- Home seals' real order beats shuffles of their own signs by 2.1 bits/sign. On average a shuffle scores worse than the real text in 92% of cases (mean percentile q 0.08).
- Home round seals and foreign round seals both sit at a shuffle percentile of about 0.5. Their real order is no more Indus-like than a random ordering of the same signs.
- Inventory is ordinary for home round seals (+0.16). It is mildly raised abroad (+0.36, p=0.037, secondary).
- **Power.** If home round seals were ordinary seals, the foreign-minus-home-round order test would detect the foreign anomaly with power 0.99 (400 simulations). The null result is therefore informative: the two round groups do not differ.
- **Post-hoc robustness** (not pre-registered): many home seals have near-copies in the CV training folds, which flatters their real order. Against the 1,164 home seals with no near-copy (bigram-set Jaccard <0.5 to every other native text):
  - home round order: +1.63 (p=3e-4),
  - foreign round order: +1.65 (p=1e-4).

  The effect is not a uniqueness artefact.

## Attack 5: why KN and the Wells grammar disagreed
#22's grammar figure (+0.41, p=0.18) used 12 units. Four of them should not be there:
- the Harappa tablet H-369,
- Daimabad `W740` (1 sign),
- `W140 #` (1 sign),
- `W003 # # W003`.

These short, common texts pull the mean down. KN on the same 12 units also drops, to +0.91 (p=0.03). On the corrected 8 units:
- grammar: **+0.96 (p=0.025)**,
- glib KN: +1.66 (p=6e-4).

The rest of the gap is the scorer. The class bigram shrinks every anomaly: Gulf round is +1.77 under the grammar against +2.17 under KN. Under the grammar, home round sits at about half the Gulf-round excess. I did not test that ratio formally.

## Hypotheses
| hypothesis | verdict |
|---|---|
| #22's home-round anomaly is an artefact of including non-seals | refuted (effect grows without H-369) |
| It is a rare-sign (inventory) effect, not an order effect | refuted (order +1.96, inventory +0.16 n.s.) |
| It is an artefact of near-duplicate home texts | refuted (post hoc, +1.63) |
| KN and grammar truly disagree | refuted: set membership explains most of it; grammar on the corrected set p=0.025 |
| Foreign round seals break order more than home round seals | not supported (+0.11, p=0.68, power 0.99) |
| Home round seals are Gulf imports | inconclusive: Gulf-type iconography over-represented (3/8, p=0.004) but CISI/Mackay boss evidence says Indus-made |

## What this means for #4 (crib attack)
The 9-11 flagged foreign texts are off-order because they are round, Gulf-type seals, and home round seals are off-order in the same way. A crib attack that treats off-order as evidence of foreign names has no control group left. Run #4 with a **home round-seal control**: run the same crib on the 8 home round texts. A name list that "fits" them equally well is fitting the genre. Gulf-type seals may write names in all places, including the Indus sites; that is still open.

## Not checked
- Photos of the bosses of M-416, Dholavira 4247.1 and the Rakhigarhi cylinder.
- Find contexts beyond Mackay's level for M-415.
- CISI vol. 3 (Dholavira and others), which we do not hold.
- n=8 is small. The order test is strong (p=1e-4), but per-object claims are descriptive.
