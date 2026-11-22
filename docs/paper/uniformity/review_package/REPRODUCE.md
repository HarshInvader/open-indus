# How to reproduce the paper

All commands run from the archive root. Paths are relative to it.

## 1. Environment

The results were produced with CPython 3.15.0 on macOS (arm64). `environment/requirements.lock.txt` is the exact `pip freeze` of that environment.

```sh
python3.15 -m venv .venv
.venv/bin/pip install -r environment/requirements.lock.txt
```

Every script is run as `.venv/bin/python -I ...` (isolated mode: no user site-packages, and the current directory is not put on the import path).

`board/run.sh` is the compute gate used for every scoring run: it takes a repository lock and runs the command at the lowest priority (`taskpolicy -b nice -n 20`). `taskpolicy` is macOS only. On Linux, replace that line with `nice -n 20 "$@"`; the results do not depend on it.

## 2. Rebuild the figures (no third-party data needed)

The four figures are drawn only from `results.json` files in this archive.

```sh
for f in docs/paper/uniformity/figures/make_fig1_between_within.py \
         docs/paper/uniformity/figures/make_fig3_power.py \
         docs/paper/uniformity/figures/make_fig4_sites.py; do
  nice .venv/bin/python -I "$f"
done
cd docs/paper/uniformity/latex/figures && shasum -a 256 -c SHA256SUMS
```

`make_fig1_between_within.py` writes Figures 1 and 2 (`fig1_between_within`, `fig2_gap`). Each figure is written as PDF and PNG. The scripts overwrite the shipped files, so the checksum file is the record of the published bytes.

Both formats rebuild byte for byte on the locked environment: the PDF carries no creation date and matplotlib uses its bundled DejaVu fonts. A different matplotlib, FreeType or Pillow version can change the bytes but not the plotted values. Each script also refuses to save a figure with any text under 8 pt or wider than the text block.

## 3. Third-party corpora

Fetch the corpora listed in `SOURCES.md` into the paths given there. Then build the shared Indus corpus:

```sh
.venv/bin/python -I corpus/build.py          # -> data/m77_lines.jsonl, data/m77_texts.jsonl, data/icit_texts.jsonl
```

## 4. Build the reference pools

```sh
board/run.sh .venv/bin/python -I experiments/uniformity_benchmark/build.py    # Ur III, proto-cuneiform, Latin pools
board/run.sh .venv/bin/python -I experiments/uniformity_paper/step1/build.py  # Linear B, Ur III with POS, Latin
.venv/bin/python -I experiments/uniformity_paper/step2/build2.py              # Ur III reigns and collections, CDLI seals, Old Babylonian, Latin metadata
```

Each writes into the `data/` folder next to it. These folders hold third-party text and are not in the archive.

## 5. Run order

Each step was pre-registered and hashed into `docs/prereg/HASHES.txt` before it was scored. Steps run in this order, because later steps import earlier ones and some read earlier results. Every `run` is resumable: it appends to `draws*.jsonl` and skips conditions already done. `report` only reads the draws and writes `results.json` (and `table.md` where there is one).

| # | Step (prereg tag) | Commands | Seed | Wall time on the original run |
|---|---|---|---|---|
| 1 | `uniformity_benchmark` | `run.py sizes`, `run.py calib`, `run.py run`, `run.py report`, `report.py`, `achieved_mix.py` | 20261121 | about 15 min |
| 2 | `redteam_uniformity` | `rt.py sizes`, `rt.py run`, `rt.py report`; `rt_extra.py`; `leak_words.py` | 20261122 | about 15 min |
| 3 | `uniformity_paper_step1` | `s1.py sizes`, `s1.py run`, `s1.py report`; `s1_extra.py` | 20261123 | about 5 min |
| 4 | `redteam_uniformity_step1` | `rt1.py sizes`, `rt1.py run`, `rt1.py report` | 20261124 | about 10 min |
| 5 | `uniformity_paper_step2` | `s2.py sizes`, `s2.py run`, `s2.py report` | 20261125 | about 40 min |
| 6 | `redteam_uniformity_step2` | `rt2.py sizes`, `rt2.py audit`, `rt2.py run`, `rt2.py report` | 20261127 (audit sample 20261126) | about 35 min |
| 7 | `chanhudaro_followup` | `cd.py sizes`, `cd.py run main`, `cd.py run loso`, `cd.py run drivers`, `cd.py report` | 20261128 | about 10 min |
| 8 | `recchia_rerun` | `rr.py sizes`, `rr.py run` | 20261130 | about 30 min |
| 9 | `uniformity_paper_revision` | `rev.py sizes`, then `rev.py run` with each of `boot`, `names`, `diffuse`, `roles`, `latin`, `alt`, `m93`, `unicorn`, then `rev.py report` | 20261201 | about 2 h 50 min in all (roles 20 min, alt 18 min; the rest is mostly boot, names and diffuse) |
| 10 | `uniformity_paper_contrast` | `revision/contrast.py`; also `revision/overlap.py` (descriptive count) | none (arithmetic on saved draws) | seconds |
| 11 | `uniformity_referee_checks` | `rc.py sizes`, then `chunk.sh` (or `rc.py run`) with each of `hpoint`, `hboot`, `joint`, `indep20`, `rt`, `rtboot`, then `rc.py report` | 20261122 | about 3 h 10 min (hpoint 2 min, hboot 28 min, joint 59 min, indep20 80 min, rt 1 min, rtboot 17 min) |

Folders: steps 1, 2, 4, 6, 7, 8 and 11 are `experiments/<tag>/`; steps 3, 5, 9 and 10 are `experiments/uniformity_paper/{step1,step2,revision}/`. Scoring commands were run through `board/run.sh .venv/bin/python -I <script> ...`; `sizes` and `report` commands do no scoring and were run directly. The exact command lines are in each script's docstring.

**Seeds.** Each step has one master seed (`SEED` near the top of its script). Each draw's generator is seeded from the master seed, the draw index and a CRC-32 of the condition name (`np.random.default_rng([SEED, k, crc32(name)])`), and the classifier's cross-validation folds from `SEED + k`. The frozen classifier in `experiments/site_signal/lib.py` defaults to seed 20261114. So a single condition can be rerun alone and gives the same draws, in any order.

**Compute.** One laptop core: every scoring job ran as a single process at the lowest priority, on an Apple-silicon laptop that was doing other work at the same time, so a dedicated core should be faster. Times above are measured from the run logs (first to last write of `run.log`, or its start and end lines). The whole sequence took about 9 hours of wall time, of which steps 9 and 11 took 6. No step uses a GPU, and only the fetch scripts use the network.

**Checks against the archive.** Each rerun step rewrites its own `draws*.jsonl` and `results.json`. Compare them with the shipped copies, for example with `diff` or by loading both JSON files. Per-draw AUCs should agree exactly on the locked environment; a different NumPy or scikit-learn can change the last digits.

## 6. Where each number in the paper comes from

Every number in the paper is copied from a `RESULTS.md`, `results.json`, `contrast.json` or `table.md` in these folders. The figure captions and table captions name the file each panel or row comes from. The ledger rows for each step (`ledger_rows.csv`) give the claim, statistic, p-value and family used for multiple-testing correction.
