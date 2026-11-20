# Indus-size search check: result (2026-11-20)

This applies the sealed decision rule in `indus_size_search_check.md`, as cut to the 3 Latin no-anchor cells by `indus_size_search_check_change1.md`.

| Cell | Restarts | Selected accuracy | Best blind objective | Truth-climbed objective (accuracy) | Label |
|---|---|---|---|---|---|
| Latin rep 0 | 1,000 | 0.526 | -10,765.6 | -10,756.7 (0.686) | solved |
| Latin rep 1 | 1,000 | 0.450 | -10,902.9 | -10,868.1 (0.703) | search-limited |
| Latin rep 2 | 375 (stop rule) | 0.458 | -10,901.8 | -10,914.2 (0.730) | objective-limited |

- **Decision.** One cell of each label is the "otherwise" branch. The sealed wording applies: "At Indus size the result is mixed. Search depth matters, and so does closeness."
- **Where the wording now appears.** README, atlas 1.8, `experiments/decipherability/RESULTS.md`, `docs/RESEARCH_STATE.md` and the approach-page chart note.
- **Raw output.** `experiments/mismatch_study/out/step1.jsonl` and `step1_summary.json`.
