# Leakage of random object splits on M77 alone

Prereg: `docs/prereg/split_leakage.md` (hashed in `docs/prereg/HASHES.txt` before the run). Script: `leak.py`. Data: `results.json`. Run through `board/run.sh`, 2026-11-19.

Descriptive measurement on our own M77 corpus, replacing the figure measured on a third-party release's text set. Object = M77 text number. 200 random splits by object, about 20% of objects in test. Share of test texts (2+ signs) with a copy in training: median and 95% range.

| copy rule | A: all texts (3,424 texts, 2,906 objects) | B: exact repeats removed first (2,263 texts, 2,158 objects) |
|---|---|---|
| exact copy | 39.1% (35.0-43.0) | 0 by construction |
| within 1 edit | 47.1% (42.6-50.6) | 13.5% (10.0-15.8) |
| exact or contained | 59.4% (55.8-62.9) | 32.2% (27.9-36.8) |
| **within 1 edit, or contained (primary)** | **62.3% (58.9-65.9)** | **37.3% (33.3-41.6)** |
| within 2 edits | 61.5% (57.7-64.6) | 36.0% (32.1-39.4) |
| within 2 edits, or contained | 70.4% (67.3-73.8) | 50.6% (46.9-55.2) |

- Even after exact repeats are removed, a random object split leaves a near-copy of about 37% of test texts in training (primary rule). This agrees with the earlier deposit-based figure (36.0%, range 31-41%), inside the range the prereg expected.
- Without de-duplication, 62% of test texts have a near-copy and 39% an exact copy.
- The share depends on the copy rule: 13% to 51% after de-duplication. Quote it with the rule.
