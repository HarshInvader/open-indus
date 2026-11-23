# Do round seal texts look like phonetically spelled names? Atlas 1.10 reopened on the shape-defined set (sealed 2026-11-23, before any number)

Agent `paper`. Study 2 of the Fable list, 2026-11-23.

## Claim under attack
Gulf-type round seals spell names syllabically (Parpola-style "foreign names"; atlas 1.10). This is the only route in our hands that could lead to sound values.

Atlas 1.10 tested it on 12 Gulf residues: G1 p = 0.81, G4 p = 0.94, low power. Its reopen condition was "more seals". Defining the set by shape (round, wherever found) gives the 35 round texts of `experiments/round_seal_format` (10 home, 18 abroad, 7 unprovenanced).

## Data
- **Round set:** the 35 texts in `experiments/round_seal_format/results.json` `round_texts`, legible Wells signs only.
- **Residue:** remove person (W090-W175) and numeral (W001-W059) signs, exactly as in `experiments/typology/q2_gulf.py`. Empty residues are dropped.
- **Home pool:** distinct ICIT SEAL:S texts (square seals) from sites outside q2_gulf's FOREIGN_ALL and not "Unknown", with residues computed the same way.

## Statistics
- **G1:** sign types per token over the set. A phonetic subset predicts this is lower.
- **G2:** share of residues with any repeated sign. Phonetic names predict this is higher.
- **Null:** 10,000 draws of length-matched home residues (lengths capped at 5, as in q2_gulf). One-sided p.
- **Holm correction** over G1 and G2.
- **Claim supported:** G1 Holm p < 0.05, or G2 Holm p < 0.05 with observed G2 of at least 0.15.

## Kill test first: planted power
- **Plant:** take Ur III syllabically spelled seal-legend names (`typology/corpora.ur3_names`, the `syllabic_ur` filter in q2_gulf, length 2-5). For each plant:
  - map every syllable to a distinct random sign from the home residue inventory;
  - replace each round residue of length 2-5 with a random planted name of the same length;
  - leave length-1 residues unchanged.
- 200 plants, 1,000 null draws each, same decision rule.
- **Power** = share of plants where the claim is supported.
- **Power under 0.8:** STOP. The verdict is "untestable at n = 35"; the real set is not scored.
- **Power 0.8 or more:** score the real set once.

## Reading
- **Supported:** a lead only. These are the same objects that showed the order excess, so this can refute but not confirm. It goes to red team.
- **Not supported at power 0.8 or more:** the syllabic-name reading of round seals is refuted for this residue definition. Update atlas 1.10.

## Seeds and code
- Seed 20261123.
- Code: `experiments/round_name_shape/run.py`, hashed before it runs.
