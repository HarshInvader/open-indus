# Unread-sealer shortlist: K0a passed, K0b failed (reading 3). After the sealed cuts, one new tablet is left for a person to look at.

- **Prereg:** `docs/prereg/unread_sealer_shortlist.md`, sealed 2026-11-25 as v2 (tag `unread_sealer_shortlist`), after one fresh review.
- **Code:** `run.py`, written without being run and hashed before the run (tag `unread_sealer_shortlist_code`). The hash was re-checked before running.
- **Run:** once, through `board/run.sh`, single process, 27 s. The Indus compute lock was not needed and was not taken.
- **Outputs:** `kill.json`, `shortlist.csv`, `run.out`.
- **Scope:** a search aid on catalogue metadata. No Indus text was read, no key was scored, no image was downloaded, and nobody was contacted.

## Result
- **Recount:** reproduced exactly. Pool W has 1,909 rows (Ur III 1,441, Early Old Babylonian 100, Old Babylonian 368). Brief 10's pools are 669 / 62 / 32.
- **K0a, the bar: passed.** YBC 5447 (P306518) scores 6 of 9, with a worst-case rank of 6 (bar 95).
  - Points: site 2, period 1, seal note 2, trade word 1 (`kaskal`). It has no Gulf word and no named sealer.
  - The features were written by someone who knew this control. A noise ranking would pass 5% of the time. So this pass shows only that the score does not bury the one known case.
- **K0b, the Ur III check: failed.** P453801, with the Gulf-word feature zeroed, scores 4, with a worst-case rank of 321 (bar 95). With the feature on it ranks 6, but that rank is record-only, because the word is how the tablet was found.
- **P516366:** not ranked, because it has no text on disk.
- **F2, dead features:** period and seal note each score more than half the pool. They stay in the score, as sealed.
- **F1, ties at the cut:** the score-4 tie block holds 273 rows and would run to rank 321, past the 150-row cap. It is left out, so 48 rows remain.
- **Reading 3:** "K0a passes and K0b fails. The list holds only Early Old Babylonian and Old Babylonian rows from the top 95. Ur III rows are dropped."

## The list
After F1 and reading 3, 2 rows are left:

| P-number | Publication | Site | Period | Score | Worst-case rank | Photo flag | Line art |
|---|---|---|---|---|---|---|---|
| P306518 | AS 16, 199-209 (YBC 5447) | Ur? | Early Old Babylonian | 6 | 6 | yes | no |
| P415075 | UET 5, 0184 | Ur | Old Babylonian | 5 | 48 | no | yes |

- The first row is the control itself.
- **So the study yields one new lead: P415075 (UET 5 184).** It has a line drawing and no photo flag.
  - Its `kiszib` line reads "lu2 inim-ma-bi-mesz", "the witnesses". So it names no single sealer and could not be anchor grade A.
  - The person who looks should check the drawing's edges for a round or oval impression. Then, if the owner wants, an image request can go to the holder.
- The lead goes into `docs/HUMAN_LEADS.md` for the owner. No agent contacts anyone.

## What this can and cannot say
- **It can say:**
  - With metadata alone, the one known Gulf-stamped tablet ranks near the top of 1,909 unread sealed tablets. The features were written knowing it, though.
  - The Ur III arm does not survive its own check.
  - The score is too coarse to make a long list: 273 rows tie at 4 points.
- **It cannot say:**
  - that any listed tablet carries a foreign impression;
  - anything about recall, which rests on 1 of 1;
  - anything about any Indus reading.
- **Bearing on the 2027 bar:** none. Even a hit would be one pair, and `anchor_crossread` needs more than 15. This lead also names no sealer.

## Disclosures
- **Implementer choices:** 18 places are marked `# PREREG-AMBIGUITY:` in `run.py`. The one that decides the recount is that brief 10's `kiszib` test is a substring test on cleaned numbered body lines. The recount reproduced under it.
- **Counts that differ from the review:**
  - The 2-point site tier holds 124 rows. The reviewer counted 125 under the exact site rule; the gap was not chased.
  - `seal_id` is filled for 1,743 rows because "Sx" counts as filled. The reviewer counted 276 rows with an identified S-number.
  - Neither difference moves any control's points.
- No rerun, no tuning, no fix tags.
