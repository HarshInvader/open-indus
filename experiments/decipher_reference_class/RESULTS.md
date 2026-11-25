# Decipherment reference class: no listed script, read or unread, has Indus's profile. The rule check is INCONCLUSIVE because coders did not agree on ANCHOR.

- **Prereg:** `docs/prereg/decipher_reference_class.md`, sealed 2026-11-25 as v2 (tag `decipher_reference_class`), after one fresh review.
- **Code:**
  - `build_packets.py` was run to fetch the pinned accounts.
  - `score.py` was hashed before any code existed and run twice, as the prereg says: `agree` after coders 1 and 2, and `final` after coder 3. The hash was checked before each run.
- **Coders:** coder 1 was Fable and coder 2 was Opus. Each was a fresh agent that saw only its packet. Coder 3, a fresh Fable agent, coded only the 22 cells where the first two differed.
- **Inputs:** 47 rows. The texts are kept outside the repo (CC BY-SA and Mnamon); their sha256 and revision ids are in `packets.sha256`.
- **Outputs:**
  - the coder tables, each with its quotations: `codes_coder1.csv`, `codes_coder2.csv`, `codes_coder3.csv`;
  - `third_coder_cells.csv`;
  - `table_majority.csv`;
  - `scores.json`;
  - `RESULTS_TABLE.csv`.

## Agreement (sealed bar: kappa ≥ 0.8)
| feature | kappa, full levels | kappa, collapsed | raw agreement | status |
|---|---|---|---|---|
| LANG_PRIOR | 0.81 | 0.81 | 0.87 | pass |
| LANG_HIND (30 rows) | 0.89 | 0.89 | 0.97 | pass |
| ANCHOR | 0.72 (weighted) | 0.69 | 0.85 | **fail** |
| VALUES | 0.93 | 0.93 | 0.96 | pass |
| WORDDIV | 0.91 | 0.89 | 0.94 | pass |
| CORPUS | 0.85 | 0.85 | 0.94 | pass |

- ANCHOR is a rule feature, so the sealed fallback applies: readout 1 is computed from coder 1's table, coder 2's table and the majority table. A verdict stands only if all three agree.

## Readout 1: does the rule fit at least 24 of the 26 deciphered rows?
The rule: a script was read only with outside names or values, or with a known language plus word division.

| table | fit with NS counted for | fit with NS counted against | verdict |
|---|---|---|---|
| coder 1 | 26 | 22 | INCONCLUSIVE |
| coder 2 | 26 | 24 | PASS |
| majority | 26 | 24 | PASS |

- **Verdict: INCONCLUSIVE.** The frozen reading: "The sentence is marked 'not checked: the accounts do not settle it' wherever it stands. The rows that decide it are listed."
- **The deciding rows** are Old Turkic and Safaitic in every table; coder 1 adds Tangut and Ugaritic. Each has `NS` on a rule feature.
- **No table has a deciphered row that clearly misses the rule.** Every gap is a feature the accounts do not state.

## Readout 1b: the stricter sentence in `RESEARCH_STATE.md`
- The sentence: every past decipherment rested on names fixed from outside.
- Because readout 1 is INCONCLUSIVE, the prereg makes this a count only.
- The fit is 17 to 23 of 26.
- **Three deciphered rows miss under both NS settings:** Hittite cuneiform, Meroitic and Northeastern Iberian.
- So the strong form of the sentence does not hold for this table, and the project should not repeat it as written. This is a count, not a verdict; see "Changes" below.

## Readout 1c: does the rule separate read scripts from unread ones?
- Of 14 undeciphered scripts, 10 also fit the rule. Fisher's exact test against the deciphered rows gives p = 0.16, two-sided.
- The frozen reading: "The rule does not separate. Having these features is common among unread scripts too, so the rule is at most a necessary condition."

## Readout 2: has Indus's profile ever been read?
- **Indus's core profile in the majority table is all zeros:** no language known, no outside anchor, no borrowed values, no word division.
  - The coders gave Indus's WORDDIV as `NS`, so the project's stated value 0 is used, as the prereg requires. This is flagged.
- **No deciphered row has this profile, and no undeciphered row has it either** (0 of 26 and 0 of 14). Adding the corpus band changes nothing.
- **Possible matches**, where the row's stated features equal Indus's and the rest are `NS`:
  - deciphered: Old Turkic and Safaitic;
  - undeciphered: Ba–Shu, Cypro-Minoan and Isthmian.
- The frozen reading: "No listed script, read or unread, has Indus's profile. The outside view has no reference class for Indus and the project says so."

## Sensitivity (record only)
These pass in the majority table:
- D1 plus D2: 28 to 30 of 30, bar 27;
- either contested row counted as deciphered;
- LANG_HIND in place of LANG_PRIOR;
- VALUES = 2 only.

By language family there is no bar: 17 to 19 of 19 groups fit, against a reference figure of 18.

Leave-one-out: with NS counted against, a single flipped row can move the count from 24 to 23, so the majority-table pass sits on the bar.

## What this can and cannot say
- **It can say:**
  - Among 40 coded scripts, nothing read or unread shares Indus's profile. Indus is outside the reference class of every past decipherment in this table.
  - The weak rule fits the read scripts where the accounts are clear. It also fits most unread scripts, so it is at most necessary, never sufficient.
  - The strong sentence "every past decipherment rested on names fixed from outside" has three counterexamples in this table.
- **It cannot say:**
  - anything about Indus's chances beyond the absence of a precedent;
  - that coder agreement reflects the codebook rather than shared training memory. Both coders are language models, so kappa is an upper bound on reliability.
- **Bearing on the 2027 bar:** none to the odds. It replaces a prior stated by feel with one a reader can check.

## Changes this asks for
- Wherever the project states "every past decipherment rested on names fixed from outside", it should be reworded. Per readout 1, the weak form is "not checked: the accounts do not settle it". Per readout 1b, the strong form has three counterexamples here (Hittite, Meroitic, Northeastern Iberian). Changing that wording is the coordinator's decision; nothing was edited.

## Disclosures
- **Batches:** each packet (1.6 MB) was too long for one agent. Each coder's shuffled packet was cut into 4 consecutive batches with the order kept, and each batch was coded by a fresh agent of the same model. The codebook and row texts were unchanged. The prereg does not mention batching.
- **Reading:** one coder-1 batch read some late rows through shell filters rather than line by line. Coder 3 skipped table-cell and bibliography lines. The later briefs asked for full reading.
- **"At T":** coders read it differently. Coder 1, batch 3, coded `NS` where an anchor's date relative to T was not stated, while coder 3 read it loosely. This is the likely source of the ANCHOR disagreement.
- **Quotations:** a few are infobox or list lines rather than sentences, flagged in the coders' notes. All passed the mechanical check except the 2 logged in `scores.json`.
- **D2 years:** the four T values the lead wrote are from memory and marked unverified in the prereg.
- **Scorer choices:** 16 are marked `PREREG-AMBIGUITY`, and all are listed in `scores.json`.
- No rerun, no codebook change, no fix tags.
- The account texts are CC BY-SA 4.0 (Wikipedia) and Mnamon; the quotations in the coder tables come from them.
