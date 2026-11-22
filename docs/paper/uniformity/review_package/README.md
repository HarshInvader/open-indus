# Review archive: Mohenjo-daro and Harappa seal texts

This archive lets a reviewer check every number and figure in the submitted paper. It is anonymised for review.

- `REPRODUCE.md`: run order, seeds, compute needs, and how to rebuild the figures byte for byte.
- `SOURCES.md`: every third-party corpus, with its source URL, licence, access date and the script that rebuilds the local copy. The corpora themselves are not included.
- `environment/`: the Python version and a `pip freeze` lock file of the environment that produced the results. `ANONYMISED_FILES.txt` lists the few files edited for anonymity.
- `experiments/`: code, per-draw records (`draws*.jsonl`), summaries (`results.json`, `RESULTS.md`) and ledger rows (`ledger_rows.csv`) for each pre-registered run.
- `docs/prereg/`: the pre-registrations for these runs and `HASHES.txt`, the SHA-256 of each pre-registration and its code at the time it was frozen.
- `docs/paper/uniformity/figures/`: the figure scripts. The published figures and their checksums are in `docs/paper/uniformity/latex/figures/`.

Paths in code, notes and the paper are relative to the archive root, which stands in for the repository root.

Rebuilding the four figures needs nothing but this archive and the Python packages in the lock file. Rerunning the analyses needs the third-party corpora, fetched as `SOURCES.md` describes.
