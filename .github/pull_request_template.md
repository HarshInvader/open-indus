<!-- Thanks for helping toward the goal: decipher the Indus script by 2027.
     Every pull request that reports a result needs the two items marked "required".
     Fixes to code, docs or the site that report no result can skip them. -->

## What this changes

<!-- One or two sentences, conclusion first. Link the issue or starter task, e.g. "Closes #12 (S3)". -->

## Pre-registration (required for a result)

- Pre-registration file: `docs/prereg/...`
- SHA-256: `...`
- Line in `docs/prereg/HASHES.txt` committed in commit: `...` <!-- this commit must come before the commit with your results -->
- [ ] The pre-registration was hashed before any held-out result was seen.
- [ ] Nothing was tuned on held-out texts.

## Planted control (required for a result)

<!-- Show that your method finds a known answer in a corpus of the same size: about 2,300 distinct texts, 4.5 signs each.
     Say what was planted, how often the method found it, and where the code is. -->

- What was planted:
- How often it was recovered:
- Code:

If your method makes no claim about sounds, a language or a grammar, write "not applicable" and say why.

## Result

- Verdict: supported / refuted / inconclusive
- Key numbers: effect, null, p-value or interval, and how many tests you ran
- Held-out result:
- What would prove this wrong:

## Checklist

- [ ] Work is in a new `experiments/<area>/` folder, with `RESULTS.md` (conclusion first) and `results.json`.
- [ ] One row per test added to `docs/test_ledger.csv`.
- [ ] Counts are on distinct texts, not objects.
- [ ] Code runs from the repository root with `.venv/bin/python -I`.
- [ ] No corpus files, catalogue scans or page images are added (see `LICENSING.md`).
- [ ] No files in `corpus/` or in another contributor's folder are changed.
