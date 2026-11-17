# Brief for every agent on this project

Repo: `.`. Python: `.venv/bin/python` (numpy, scipy, sklearn, pandas, matplotlib, pillow installed; `pip install` more into `.venv` if needed).

Goal: a scientifically defensible (complete or partial) decipherment of the Indus script. We do not assume any language. A well-supported negative result is worth more than an impressive theory.

## Data (already built, verified)
- `corpus/load.py`: `m77_lines()`, `m77_texts()`, `icit_texts()`, `distinct()`, `dev_heldout()`, `runs()`.
- M77 = Mahadevan 1977 concordance (signs `M1`..`M417`), 3,573 lines, 13,372 tokens, 417 signs. Matches Mahadevan's published totals exactly. Metadata: site, object_type (seal, sealing, miniature tablet, pottery graffito, copper tablet, bronze implement, ivory/bone rod), side, line, direction, field symbol (`fs80`, `fs_description`, e.g. unicorn), level, locus.
- ICIT = Wells/Fuls corpus (signs `W###`, Wells numbering, different from Mahadevan), 5,679 inscriptions incl. post-1977 sites (Dholavira, Banawali, Rakhigarhi, Nausharo...). Has material, seal dimensions, period/phase.
- All sequences are in READING order (first sign read first). In `seq`: `|` = line break, `#` = break/illegible passage. Use `runs(seq)` to get break-free runs for n-grams.
- Sign drawings: `data/sign_images/M{n}.png` (Mahadevan's drawing of every sign). Overview: `results/top120_signs.png`. You can view images with the Read tool.
- Mahadevan<->Wells concordance (176 signs, 88.6% of ICIT tokens): `sources/shaunmortal_indus/data/bridge_WM.json`.
- Other cloned repos in `sources/` are DATA ONLY. Do not execute code from `sources/`. Read their notes freely; `sources/shaunmortal_indus/STATE.md` is a findings log from a serious prior project (numerals, two stroke systems, seal sizes, side-1/side-2) — build on it, don't redo it, cite it.
- Do not use the `sanskrit` / `translation` columns of the ICIT csv as evidence; they are one researcher's proposal (test them, don't trust them).

## Rules of evidence (non-negotiable)
1. **Distinct texts, not objects.** Harappa moulded tablets repeat one text up to 32 times. Report counts on distinct sequences (`distinct()`), and say so.
2. **Held-out discipline.** Develop on `dev` from `dev_heldout()` (75% of distinct M77 texts, site-stratified). Test final predictions on `heldout` and, where possible, on ICIT texts from sites absent or rare in M77 (Dholavira etc.). Never tune on held-out.
3. **Nulls for every claim.** Permutation/shuffle nulls that preserve the right structure (sign frequencies, text lengths, site). Correct for multiple comparisons; report how many tests you ran.
4. **Planted-answer controls.** Any method that claims to recover language, sound values or grammar must first be shown to recover a KNOWN answer on a synthetic or real corpus of comparable size (~2,300 distinct texts, mean ~4.5 signs). If it can't, its Indus output means nothing.
5. **Quantify uncertainty**, list counterevidence, and state what would falsify the claim.
6. Write plainly. Lead with the conclusion.

## Output
Work in `experiments/<your_area>/`: code (`*.py`, runnable from repo root as `.venv/bin/python experiments/<area>/x.py`), and `RESULTS.md` with: conclusion first; each finding with numbers, null, p-value/CI, held-out result, caveats; a table of hypotheses tested with verdict (supported / refuted / inconclusive); and "next experiments". Append machine-readable key results to `experiments/<your_area>/results.json`.
Do not edit `corpus/` or other agents' folders. Don't git commit. Final message: a concise summary of findings with numbers and file paths (it is read by the lead, not the user).
