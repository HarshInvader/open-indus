# Pre-registration: fish_marshall (independent replication of the ticked-fish block clustering on Marshall 1931 seals)

Registered 2026-11-15 in `experiments/fish_marshall/` BEFORE any findspot of any Marshall seal was read and before any test was run. Hash in `docs/prereg/HASHES.txt` (tag `fish_marshall`).

Claim under replication: "Ticked fish (M60, M66, M68, M71, M73) cluster by block at Mohenjo-daro" (reg_findspot F3, Mackay 1938 DK-G: G=36.2, p=0.0007; redteam_fish_block WEAKENED, not replicated at M77-locus resolution, p=0.31, power 0.44 for a block-sized cluster).

Already seen when writing this: the redteam/reg_findspot results; the header and first ~13 rows of MIC vol. II p. 402 (columns: Plate No. | Size | Level below surface | Type | Material | Site and Serial No., e.g. "HR 4161"). The tabulation carries NO section/block/house; those can only come from prose in MIC vols I-II that cites a field number with its findspot. I have not read any such prose sentence for a seal, nor linked any seal's area/field no. to its text.

## Data
- Seals: Marshall 1931 MIC vol. II pp. 402-405 tabulation, serial s -> M77 text_no 1000+s (Mahadevan App. V). Signs from M77 (`corpus.load.m77_lines`, object_type seal, all sides). Only Mohenjo-daro seals not in Mackay 1938 (text_no 1001-1999).
- Re-reading (step 2): Apple Vision OCR (`experiments/old_registers/tools/vocr`) on page images of pp. 402-405 from up to three independent archive.org scans of vol. II, several passes (whole page, each half-table, row strips; upscaled/binarised), plus the existing djvu word layer. Per row: serial, area code, field no., level (ft, in.).
- Findspot (block/house/room): sentences in MIC vols. I and II (OCR text of archive.org scans) that cite a field number ("HR 5548", "VS 2671", "DK 1234") together with Section/Block/House/Room/Chamber. A field number is assigned the findspot of the sentence in which it occurs (nearest preceding locative phrase within that sentence). Field numbers with two conflicting findspots are dropped.

## Row reliability rule (fixed now)
A tabulation row is RELIABLE if all hold:
1. its serial is read and fits the running sequence (repair only by one-digit edit that continues the sequence);
2. area code + field no. agree in >= 2 independent readings (passes/scans), or are read once and no reading conflicts;
3. depth: if M77 has a level for text 1000+s, the re-read level agrees within 1 ft (|diff| <= 1.0). If M77 has no level, the row passes on 1-2 alone.
Unreliable rows are dropped from all tests. Accuracy reported = share of rows with both readings whose re-read level is within 1 ft of M77 (target >= 90%), before dropping.
Area labels used: HR, VS, DK, plus any other area code with >= 8 reliable seals (e.g. C, E, L, SD); rarer codes pooled as 'other'.

## Statistic (same as reg_findspot F3 / redteam primary)
G statistic of TF presence across units (2 x k), null = permute unit labels within strata, 10,000 permutations, one-sided upper p = (1 + #null >= obs)/(1 + N). Strata = area x 5-ft depth band (depth = M77 level, else re-read level; missing depth = own band). Units with < 8 text seals are pooled into 'other-<area>'.
Text-family level: within a unit, TF seals with edit distance <= 1 or sharing the bigram (sign before TF, TF sign) form one family; keep one per family (the shallowest), drop the rest (redteam A2b strict rule). The analogous rule applies to plain fish in the control.

## Units and the primary test (one primary test; decision rule fixed now)
- U_block: area + section + block from prose (HR: section + block; DK: section + block; VS and others: block if given else house).
- U_fn (proxy): within each area, seals sorted by field number and cut into consecutive groups of 25 seals (last group merged into previous if < 13). Field numbers were issued in order of finding, so neighbours in field number were found close in place and time.
- PRIMARY = U_block IF >= 120 reliable seals with a block-level findspot, >= 6 of them TF, in >= 4 units with >= 8 seals. Otherwise PRIMARY = U_fn, and U_block is reported as exploratory/descriptive.
- SUCCESS (replication): primary test p < 0.05 at text-family level. The non-collapsed p is reported as secondary.

## Secondary (reported, not part of success)
- S1 plain-fish control (M59, M65, M67, M70, M72), same primary units, family level. Expectation if TF clustering is specific: p > 0.05.
- S2 leave-one-block(unit)-out on the primary test: drop each unit holding >= 1 TF seal; report all p and max p.
- S3 the non-primary unit definition (U_block or U_fn), same statistic.
- S4 area level only (HR vs VS vs DK vs other, within depth band) - descriptive.
- S5 exploratory: Fisher combination of this primary p with redteam family-collapsed p (0.0056) - labelled exploratory, not a replication.

## Power (reported before interpreting p)
On the primary units, plants of (a) a block-sized cluster: +4 TF seals added to one random unit with >= 15 seals (redteam a5 definition), and (b) TF rate x6 in one unit with >= 15 seals; 200 plants each, 2,000-permutation nulls; power = share with p <= 0.05 (family level). If power (a) < 0.5, a null result counts only weakly against the claim; the verdict says so.

## Verdict rule
- REPLICATED: primary family-level p < 0.05.
- NOT REPLICATED (informative): p >= 0.05 and power (a) >= 0.5.
- INCONCLUSIVE: p >= 0.05 and power (a) < 0.5, or the register could not be read to the reliability rule for >= 100 seals.
Ledger rows `fm_*` in `docs/test_ledger.csv`, mode 'confirmatory' for the primary, 'exploratory' otherwise.

## Amendment A1 (2026-11-15, after transcribing the register, BEFORE any seal's findspot was linked to its text or TF status)
Found while checking data sources: the raw ICIT file `sources/field-cady_indus_valley_script_corpus/inscriptions.csv` (data only) carries CISI "basic data" findspot fields for Mohenjo-daro objects: `area-section`, `block-house`, `room-grid`, `excavation-idno`, `depth`. For Marshall seals `excavation-idno` = field no. + MIC serial run together (e.g. `C841043` = C 841, serial 43; `D90289/359` = D 90, serials 289/359). This is the register-derived block/house findspot the prose route was meant to approximate. Changes:
1. Findspot source priority: (a) ICIT row whose `excavation-idno` starts with the re-read area code + field no. AND contains the MIC serial (link by register identifiers only, never by sign sequence); (b) MIC vols. I-II prose as pre-registered. If (a) and (b) both give a block and disagree, the seal is dropped from U_block.
2. U_block unit = normalised `area-section` (e.g. HR-A, HR-B, VS-A, DK-C, 'DK-' kept as DK) + block parsed from `block-house` (leading block number; 'Trench X' -> trench unit; any 'Street'/'Lane' -> street-<area>; 'Betw.'/unparsable -> no block). Houses (roman numeral after the block number) are kept for description only.
3. Area label for strata = first letters of ICIT `area-section` (HR, VS, DK, SD, L) when the seal links; otherwise the register prefix (HR, VS, DK, SD, L as written; other prefixes mapped to the area that the majority of their ICIT-linked seals have; unmapped -> 'other').
4. ICIT `excavation-idno` and `depth` count as extra independent readings for the reliability rule (criterion 2) and as a depth cross-check; M77 level remains the depth reference for accuracy and strata.
Everything else (statistic, family collapse, primary-unit decision rule, success criterion, power, controls) is unchanged.
