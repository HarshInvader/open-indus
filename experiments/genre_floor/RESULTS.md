# Genre detection floor at Indus size (board #43, Fable plan 7 G2)

2026-11-18. Pre-registration `docs/prereg/genre_floor.md`; its sha256 and those of `floor.py` and `run.py` were appended to `docs/prereg/HASHES.txt` (09:31Z) before any detection run. 220 planted corpora, 10 reps per cell. Raw data: `out/floor.jsonl`. Summary: `summary.json` / `results.json`. Ledger: `ledger_rows.csv` (`gfl_*`).

## Verdict

- **The floor is 0.57 bits/text, nearly 4x the real Indus object-type signal (0.15).** That is the weakest genre either method finds with power >= 0.8 at ~2,270 texts. The formula model (LCA) reaches it only when the genre differs in vocabulary, opener/closer and length all at once (MIX, s = 1). Logistic fit: 0.54.
- **The HMM mixture never reaches power 0.8 on any genre made inside Indus texts** (vocabulary up to 0.50 bits, formula up to 0.50, length up to 0.14, all three together up to 0.57). Its best was 1/10.
- **Neither model gives false alarms.** Detections on null corpora (labels without a planted genre) were 0/10 for both models, for both Indus and cuneiform nulls.
- **So, by the pre-registered rule, genres-from-scratch closes as a route.** At Indus size these methods cannot see a genre as weak as object type. #34's K* = 1 on Indus means only that Indus has no strong latent split of the kind that separates Mesopotamian seals from tags. It says nothing about genres at 0.15 bits.
- **One near miss.** A genre that differs **only in length** was found by the formula model 7/10 times at 0.144 bits (logistic 0.8-power point 0.17). That kind is the one exception where the floor sits close to 0.15. Since the formula model chose K = 1 on M77 (#34), a pure length-type genre of about 0.17 bits or more is unlikely in Indus. It was not run as a confirmatory Indus test.

## Fix for the near-copy chaining problem

#34 linked texts transitively (`splits_v2` rule), which chained 571 M77 texts into one family; that family skewed folds and planted labels. Here families come from **leader clustering** under the same `_close` rule: texts are visited longest first, and each joins the first leader it is close to, otherwise it becomes a leader. Nothing chains.

| corpus | old largest family | new largest family | families (new) |
|---|---|---|---|
| M77 (2,269 distinct) | 571 | 8 | 1,912 |
| cuneiform mix (2,270) | 445 | 4 | 2,084 |

Trade-off: two texts that are both close to a text but not to each other's leader can land in different families, so a little near-copy leakage across folds is possible. That leakage helps detection, so it would only push the floor down, not up.

## Design (as pre-registered)

- **Carriers.** All 2,269 distinct M77 texts, with synthetic labels: 30% minority class, assigned by whole family. Own 75/25 family split.
- **Plants on the minority class, strength s.**
  - VOC: tokens swapped to frequency neighbours with prob s.
  - FORM: first sign replaced by one of 3 class openers with prob s; last sign by one of 3 class closers with prob s.
  - LEN: two deletions, each with prob s.
  - MIX: all three edits together.
- **CUN (dilution of real cuneiform).** Class A = Ur III seal legends. Class B = with prob s an OB seal, tag or brick text, otherwise another Ur III legend.
- **Scale.** The supervised logistic-regression held-out bits/text from genres_scratch `final.py`, the same scale as the 0.15 for Indus object type.
- **Detection rule.** Three conditions, all required:
  - K* >= 2, chosen from 1..4 by 3-fold family CV with the 1-SE rule;
  - held-out gain over K = 1 with a bootstrap CI above 0;
  - held-out genres predict the label (label-shuffle p < 0.05, 500 permutations).

## Numbers (power out of 10 reps; gain = mean supervised bits/text)

| plant | s | gain | HMM power | LCA power | LCA K>=2 |
|---|---|---|---|---|---|
| null (Indus) | 0 | -0.004 | 0.0 | 0.0 | 0.0 |
| VOC | 0.25 / 0.5 / 0.75 / 1.0 | 0.04 / 0.21 / 0.35 / 0.50 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 |
| FORM | 0.25 / 0.5 / 0.75 / 1.0 | 0.11 / 0.26 / 0.42 / 0.50 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0.1 | up to 0.5 |
| LEN | 0.5 / 1.0 | 0.03 / 0.14 | 0 / 0 | 0 / **0.7** | 1.0 at s=1 |
| MIX | 0.15 / 0.25 / 0.5 / 0.75 / 1.0 | 0.06 / 0.15 / 0.35 / 0.49 / 0.57 | 0 / 0 / 0 / 0 / 0.1 | 0 / 0 / 0 / 0.5 / **1.0** | 0.7, 1.0 |
| CUN null | 0 | -0.005 | 0.0 (K>=2 in 10/10, no label link) | 0.0 | 0 |
| CUN | 0.2 / 0.4 / 0.6 / 0.8 / 1.0 | 0.02 / 0.11 / 0.22 / 0.38 / 0.66 | **0.8** / 1 / 1 / 1 / 1 | 0 / 0 / 0 / 0 / 0 | up to 0.2 |

Floors by the pre-registered rule:
- **HMM:** above 0.50 (VOC), above 0.50 (FORM), above 0.14 (LEN), above 0.57 (MIX). Logistic fit for MIX: 0.82.
- **LCA:** above 0.50 (VOC), above 0.50 (FORM, logistic 0.60), above 0.14 (LEN, logistic 0.17), **0.57 (MIX)**.
- **Headline (lowest over the Indus kinds):** 0.57 bits/text.

## How to read the CUN line

The HMM picks up diluted cuneiform labels at only 0.02 bits. That is not a weak genre being found. Ur III seals and tags are a strong latent split (#34: 1.15 bits), and the label merely tracks it. The model finds the strong split, and the diluted label rides along with it. Indus shows no such strong split (#34: K* = 1 for every valid model), so this route offers nothing for Indus. It is reported separately, as pre-registered.

The HMM also chose K >= 2 on pure Ur III seal legends in 10/10 reps without linking to the null labels. So Ur III seal legends contain latent structure of their own; Indus at the same size does not.

## Caveats

- **The plants are single, clean class edits on real Indus texts.** Real genres could mix edits in other ways, and a different kind of genre could have a different floor. Four kinds were tested; the floor is per kind.
- **Strength is capped by the design.** VOC, FORM and LEN top out at about 0.5, 0.5 and 0.14 bits, so for HMM the floor is only bounded from below.
- **LEN at 0.144 gave 7/10.** With 10 reps, a true power of 0.8 is not excluded there. Treat the length floor as about 0.15-0.2.
- **Settings.** K was capped at 4 with 3-fold CV and 1 HMM restart (as #34's power runs). More restarts might lower the HMM floor somewhat. Not checked, for compute.
- **No Indus claim was tested.** Indus texts served only as carriers for the planted genres.

## Proposed NEGATIVE_ATLAS text (for the lead)

### 4.x Text genres found from the signs alone (genres-from-scratch)
- **Question.** Do Indus texts fall into text types (genres) that an unsupervised model can find from the signs alone?
- **Method.** HMM mixture and formula latent-class model (#34). Detection floor measured with planted genres on 2,269 real M77 texts (#43), with near-copy families rebuilt without chaining.
- **Result.** On Indus, K* = 1 for every valid model (#34). The floor for power 0.8 at Indus size is 0.57 bits/text: the formula model on a genre that differs in vocabulary, formula and length together. The HMM is never reliable on genres made inside Indus texts up to about 0.5 bits. Null false alarms: 0/10. Real Indus object type carries 0.15 bits.
- **Not excluded.** Genres weaker than about 0.5 bits/text, including object-type registers (0.15). Pure length types are excluded only above about 0.17 bits.
- **Excluded.** A strong split like Mesopotamian seal legends vs tags (1.15 bits; the HMM finds it, and finds even a diluted version at 0.02 bits of label signal).
- **Verdict.** Closed at stated power (methods blind below about 0.5 bits/text at 2,300 texts).
- **Folder.** `experiments/genres_scratch`, `experiments/genre_floor`.
- **Prereg.** `genres_from_scratch.md`, `genre_floor.md`.
- **Reopen with.** A corpus several times larger, or a labelled known-answer genre corpus of Indus-like weakness, or a model shown to beat 0.15 bits on these plants.

## Next experiments

- None on this route at the current corpus size.
- Object-type differences are better studied supervised: label known, held-out test, as finding 06 already does.
