# Do later-published tablets carry the same fixed numeral pairs? (sealed 2026-11-23, before any ICIT numeral was read)

Agent `paper`. Main line (b). This is Fable's pick after `numerals_by_object` (recorded in RESEARCH_STATE). It turns that study's exploratory finding into an out-of-sample test.

## Claim under test
- `numerals_by_object` found that numerals on M77 tablets come in fixed pairs: 3 + M403 and 7 + M197 (Harappa tablets); 3 + M190, 7 + M194 and 1 + M25 (Mohenjo-daro copper).
- Prediction: tablets published or catalogued outside M77 keep these exact pairs, **more than seals keep their own modal pairs**.
- Without the seal comparison, "fixed pairs" might simply be how the script uses numbers everywhere.

## Data
- ICIT (`data/icit_texts.jsonl`), Harappa and Mohenjo-daro.
- Distinct legends are bridged to M77 signs (`glib.bridge_unit`, first listed M per W).
- **Out of sample:** a legend counts only if neither it nor a near copy (`corpus.build._close`, length ±1) appears among any M77 text.
- This is out of sample for the numeral pairs, **not unseen data**: ICIT has been used in other studies here.
- Shape, measured before sealing (no numeral read): ICIT-only tablets 396 (Harappa) and 43 (Mohenjo-daro); seals 135 and 417; copper 52.
- **Copper is secondary only.** The copper tablets in ICIT and M77 are largely the same Mohenjo-daro objects. Bridging differences may hide copies, so they are reported, not tested.

## Statistic and null
- **Tablet rate:** of ICIT-only tablet numeral tokens whose head is in {M403, M197, M190, M194, M25}, the share whose value equals the sealed value.
- **Seal rate:** the same for ICIT-only seal tokens. The seal pairs are frozen from M77 before ICIT was read: the 5 seal heads with most numeral tokens on M77 seals (Harappa and Mohenjo-daro) and their modal values: M59 → 2, M342 → 2, M162 → 3, M211 → 3, M169 → 4.
- Pair rule: a numeral directly before a non-numeral head, as in `numerals_by_object`.
- **Null:** tablet and seal legends (each carrying its 0/1 hits) are pooled and relabelled, keeping the two group sizes; 10,000 permutations. One-sided p for tablet rate minus seal rate.
- **Pass:** p ≤ 0.01 and a positive difference.
- **Untestable:** fewer than 10 ICIT-only tablet tokens on the five heads.

## Outcomes (frozen)
- **Pass:** "tablet numerals are fixed pairs, out of sample, beyond the script's general habit". This strengthens atlas 6.10's reading (tablets are tokens with fixed vocabulary) and becomes an S candidate for our own findings after a red team (mould copies, type duplication).
- **Fail:** fixed pairs on tablets are not shown to be more fixed than seal numerals out of sample. The exploratory note in `numerals_by_object` stays exploratory.

## Limits
- Few tokens are expected; the copper pairs are mostly unavailable outside M77.
- Mould-made Harappa tablets (TAB:B) come in copies. Distinct legends collapse exact copies only.
