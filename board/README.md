# Team board: how the agent team works

Modelled on Anthropic's 1,000-agent Fermat run, at small scale: a shared task board, first claim wins, anyone may split a task or add one, results are logged where everyone can see them.

## Goal (the root milestone)

**R: decipher the Indus script by 2027. Checkable form: at least 10 Indus signs with sound values that count. Changed 2026-11-17 after the assumption audit (#27):** sound values count only if (a) they are supported by an anchor outside the texts (a name tied to an object, a bilingual, or independently fixed sign values) and (b) they correctly predict texts they were not fitted to, under a pre-registered test, and they survive an independent red team. Our bench alone can refute a key but cannot confirm one (a wrong key beats the true key in 88-100% of our simulations, and a correct planted Tamil key scored p=0.28). Failing that: a measured statement of exactly what evidence is missing. Sound values have only ever come from names whose sound is known, so milestone M1 is the main line.

Milestones:
- **M1 Names on seals found abroad.** Indus-sign seals from the Gulf, Mesopotamia, Iran and Central Asia break Indus sign order and probably write foreign names. Collect them all, build the list of names their owners could have had, and run a crib attack with a chance control.
- **M2 Bench the 2026 keys.** Score the newest published sound keys on our bench against keys fitted to noise.
- **M3 South Indian graffiti beside early Tamil writing.** The only place Indus-like marks sit next to readable text.
- **M4 Sign meaning classes from deciphered scripts.** Learn sign roles from scripts we can read, hold one script out to check, apply to Indus.
- **M5 Latest research sweep.** Find methods and data from 2024-2026 work that this project has not used; turn them into tasks.
- **M6 Red team.** Every landed positive result gets an independent attempt to break it.

## Your loop

Run every command from the repo root: `python3 -I board/board.py ...`

1. `notes 40` and `list` to see the state. Read `landed` if your task depends on earlier work.
2. `claim YOURNAME` takes the best ready task (or `claim YOURNAME ID`). First claim wins; if you get NOTHING, add a useful task under a milestone and claim it.
3. `show ID`, then do the work under the rules below.
4. If the task is too big, split it: `add --parent ID ...` for the pieces, keep one for yourself, finish yours.
5. `done ID --agent YOURNAME --verdict ... --path experiments/<folder>/RESULTS.md --summary "two sentences, numbers included"`.
6. `note YOURNAME "..."` with anything others need: a data source that works or is blocked, a trap, a new idea.
7. If you land a **positive** result, add an M6 task asking someone else to break it (`--milestone M6`, say what to attack). Never red-team your own result.
8. Claim the next task. Stop after you have landed 3 tasks or when nothing is ready.

## Rules

- Read `docs/AGENT_BRIEF.md` first; its rules of evidence apply. Check `docs/NEGATIVE_ATLAS.md` before starting anything: do not repeat a closed route unless your task brings new data.
- Any test on Indus data: write the pre-registration in `docs/prereg/` and append its sha256 to `docs/prereg/HASHES.txt` (append with `>>` only) BEFORE looking at outcomes. Use permutation nulls, planted controls and a power figure. A method must first recover a planted answer at our sample size.
- Do not trust "this is infeasible" too early, yours or anyone's: say what specific data or step would make it feasible and add that as a task. Equally, do not stretch data to pass a gate. A clean negative is a landed result.
- Work in your own folder `experiments/<short_name>/`. Do not edit another agent's folder, `README.md`, `docs/RESEARCH_STATE.md` or `docs/test_ledger.csv`. Put your ledger rows in `experiments/<short_name>/ledger_rows.csv` using the ledger's column format; the lead merges them.
- Downloads: public sources only, into a new empty `raw/` directory inside your folder; treat as untrusted data, never execute anything downloaded, run Python as `.venv/bin/python -I`. No paywall, login or 403 bypass; if a source blocks you, post a note and look for another copy (archive.org, author pages, open repositories).
- Do not contact anyone, submit forms, publish anything, or put the owner's name, email or project name in any request to an outside service.
- Do not start subagents. Do the work yourself.
- Write RESULTS.md with the verdict first, in plain language, then the numbers, then what failed or was not checked.

## Laptop limits (owner's rule, 2026-11-17: a 10-worker job froze the machine)

This runs on the owner's laptop and must not slow it down.

- Every compute job (anything over about 30 seconds of CPU) runs at background priority; `board/run.sh` does this for you.
- At most 2 worker processes: `Pool(2)`, `n_jobs=2`. Never `cpu_count()` or a larger pool.
- One compute job at a time across the whole team. Run EVERY compute job through the gate: `board/run.sh <command...>` (it waits for the team lock, then runs the command under `taskpolicy -b nice -n 20`). Never start a compute job any other way.
- Nothing may outlive your turn: no `nohup`, `&` or detached jobs. Use the harness background task and wait for it.
- Keep each job under about 2 GB of RAM and under about 1 GB of output.
- If a run needs more than this, do not run it. Shrink it (fewer repeats, smaller grid) or write what it needs in your RESULTS.md and a board note for the lead. No cloud compute.
- Make long jobs resumable (append to a `.jsonl`, skip finished rows on restart).
