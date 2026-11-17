# Contributing to Open Indus

**The goal: decipher the Indus script by 2027.** Deciphered means sound values for at least 10 signs that beat chance on our public test bench and survive an independent red team. We are not there. No sign has a proven sound or meaning yet, and our honest odds of getting there by 2027 are under 1 in 10. Every careful contribution moves those odds, including one that breaks a result of ours.

You do not need to agree with any theory of the script to help. You need to follow the same rules of evidence as everyone else.

## Pick a way in

| You are | The most useful thing you can do | Start here |
|---|---|---|
| A programmer or statistician | Re-implement a finding from its description without reading our code, or give an old test a fairer null | Starter tasks S3, S4, S5, S6 |
| An epigraphist, archaeologist or Assyriologist | Check readings and object records against published photographs; build short lists of names attested at Gulf sites | Starter tasks S1, S2 |
| A museum, archive or collection holder | Share photographs, shapes or findspots of seals, especially round seals and seals found outside the Indus region | [Offer data](https://github.com/OWNER/REPO/issues/new?template=offer-data.yml) |
| Someone with a proposed reading | Submit your sound key to the bench; it is scored the same way as every other key | [Submit a reading](https://github.com/OWNER/REPO/issues/new?template=submit-reading.yml) |
| Anyone careful | Spot-check links between texts and the 1930s excavation registers | Starter task S7 |

Starter tasks are in [site/starter_tasks.json](site/starter_tasks.json), with what each needs and when it counts as done. The agent team's own tasks are on the board described in [board/README.md](board/README.md).

## Claim a task

1. Open an issue titled with the task id, for example "S3: re-implement the ticked-fish finding".
2. A maintainer marks it taken. The first claim wins. If a claim goes quiet for three weeks it is released.
3. Write and hash your pre-registration before you look at outcomes (below).
4. Open a pull request. The template asks for the hash and your planted control.

## The rules of evidence

These are the rules every agent and every person on the project follows. The full version is [docs/AGENT_BRIEF.md](docs/AGENT_BRIEF.md).

1. **Count texts, not objects.** Some tablets repeat one text up to 32 times. Report counts on distinct texts (`distinct()` in `corpus/load.py`).
2. **Build on one part, test on the other.** Develop on the working split from `dev_heldout()`. Test once on the held-out split. Never tune on held-out texts.
3. **Every claim needs a null.** Compare against shuffles that keep sign frequencies, text lengths and sites. Say how many tests you ran; the project-wide count is in [docs/test_ledger.csv](docs/test_ledger.csv).
4. **Find a planted answer first.** A method that claims to recover sounds, a language or a grammar must first recover a known answer from a corpus of the same size: about 2,300 distinct texts, 4.5 signs each on average.
5. **Seal it before you look.** See below.
6. **Say what would prove you wrong.** Give the uncertainty, the counter-evidence and the result that would falsify the claim. Lead with the conclusion, in plain words.

## Seal a pre-registration

1. Write `docs/prereg/YYYY-MM-DD_<area>.md`. Include:
   - the hypothesis;
   - the exact test and the data split;
   - the null;
   - the pass mark;
   - the planted control;
   - what you will report if it fails.
2. Hash it, and any script or table it fixes, before running anything on held-out texts:
   ```
   shasum -a 256 docs/prereg/YYYY-MM-DD_<area>.md
   ```
3. Add the line to `docs/prereg/HASHES.txt` in the same format as the lines already there:
   ```
   <sha256>  <path>  <UTC time>
   ```
   Commit it on its own, before the commit with your results. The commit time is the public record that it came first.
4. Do not edit a sealed file. If the plan has to change, write a new file, hash it, and say in your results why it changed.

## Lay out your work

Put your work in a new folder, `experiments/<your_area>/`. Do not edit `corpus/` or another contributor's folder; open an issue instead. Your folder needs three things:

- Code that runs from the repository root: `.venv/bin/python -I experiments/<your_area>/x.py`.
- `RESULTS.md`, conclusion first. Give each finding with:
  - its numbers and null;
  - its p-value or interval;
  - its held-out result and caveats.

  End with a table of the hypotheses tested and the verdict on each (supported, refuted or inconclusive).
- `results.json` with the key numbers, in a form a script can read.

Add one row per test to `docs/test_ledger.csv`.

## Attack a result

A broken result is a contribution, and it is credited like any other. To red-team a finding:

1. Pick one finding and say what you will attack: a confound, a leak between splits, or a weak null.
2. Open a [test proposal](https://github.com/OWNER/REPO/issues/new?template=propose-test.yml) with your pass and fail marks.
3. Hash it, run it, and report it whichever way it goes.

## Report an error

Use the [error form](https://github.com/OWNER/REPO/issues/new?template=report-error.yml) for a misread sign, a wrong findspot, a wrong number on the site, or a broken link. Point to the published photograph, drawing or page if you can.

## Data and pictures

- **Corpus files.** Do not add corpus files, scans or page images from published catalogues to a pull request. They are not ours to redistribute; see [LICENSING.md](LICENSING.md).
- **Photographs.** Only crops from the 1931–1940 excavation reports are used.
- **Data you offer.** We agree its terms of use with you before anything is published.

## Credit

Every merged contribution is credited in the results file it changes and in the release notes. If your work feeds a paper, you will be asked whether you want to be listed as an author.

## Conduct

Argue with results, never with people. The [code of conduct](CODE_OF_CONDUCT.md) applies to every issue, pull request and discussion.
