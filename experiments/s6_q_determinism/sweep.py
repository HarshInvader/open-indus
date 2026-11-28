"""S6 seed sweep: run experiments/ledger/v2_reruns.py + build_ledger.py under many seeds, in scratch copies.

Run from the repo root (needs data/ and sources/ from `python3 datasets/fetch.py corpus`):

    .venv/bin/python -I experiments/s6_q_determinism/sweep.py RUN [--jobs 4]

Each run: v2_reruns.py, then build_ledger.py, then the lr_* p-values are written into a copy of the
COMMITTED docs/test_ledger.csv (see patch_committed_ledger), then merge_rows.py appends pending experiment
rows and recomputes every q column. That q is the one README would cite. The q from build_ledger.py's own
(smaller) rebuilt ledger is kept as `ledger_build_only`.

RUN is one of
    A   unmodified v2_reruns.py (as of commit 1c1da07), PYTHONHASHSEED = 0..19
    B   current v2_reruns.py, master seed fixed, PYTHONHASHSEED = 0, 1, 2   (determinism check)
    C   current v2_reruns.py, INDUS_SEED = 1..20, each with PYTHONHASHSEED = its seed + 100

Each run gets its own scratch directory: experiments/ledger and docs/ are copied (they are written),
everything else is symlinked, so nothing in the repository is overwritten. Scripts run with `-s -P`, not
`-I`: `-I` implies `-E`, under which Python ignores PYTHONHASHSEED. Results go to
experiments/s6_q_determinism/runs/<RUN>/<tag>/ (v2_reruns.json, the ledger rows we need, a log).
"""
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PY = ROOT / ".venv" / "bin" / "python"
BASE_COMMIT = "1c1da07"   # upstream HEAD this task started from
KEEP = ["lr_gulf", "rt_gulf"]  # rows whose q we report; all lr_* p-values are kept too


def scratch(script_src: bytes) -> Path:
    w = Path(tempfile.mkdtemp(prefix="s6_", dir=os.environ.get("S6_SCRATCH")))
    for p in ROOT.iterdir():
        if p.name in (".git", "experiments", "docs"):
            continue
        (w / p.name).symlink_to(p)
    shutil.copytree(ROOT / "docs", w / "docs", symlinks=True)
    (w / "experiments").mkdir()
    for p in (ROOT / "experiments").iterdir():
        if p.name == "ledger":
            shutil.copytree(p, w / "experiments" / "ledger")
        else:
            (w / "experiments" / p.name).symlink_to(p)
    (w / "experiments" / "ledger" / "v2_reruns.py").write_bytes(script_src)
    return w


def ledger_rows(w):
    rows = {r["id"]: r for r in csv.DictReader(open(w / "docs" / "test_ledger.csv"))}
    return {k: {c: rows[k][c] for c in ("p_value", "q_global", "q_area", "q_hier", "q_all")}
            for k in rows if k in KEEP or k.startswith("lr_")}


def patch_committed_ledger(w):
    """build_ledger.py rebuilds the ledger from its own rows only; ~500 committed rows have no script behind
    them, so a rebuilt ledger is smaller than the real one and its q-values are too low. Instead, take the
    COMMITTED docs/test_ledger.csv and replace only the p_value (and note) of the rows this run recomputed
    (every lr_* row). merge_rows.py then adds pending experiment rows and recomputes every q column."""
    new = {r["id"]: r for r in csv.DictReader(open(w / "docs" / "test_ledger.csv")) if r["id"].startswith("lr_")}
    rows = list(csv.DictReader(open(ROOT / "docs" / "test_ledger.csv")))
    cols = list(rows[0].keys())
    for r in rows:
        if r["id"] in new:
            r["p_value"] = new[r["id"]]["p_value"]; r["note"] = new[r["id"]]["note"]
    with open(w / "docs" / "test_ledger.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader(); wr.writerows(rows)


def one(run, tag, script_src, env_extra):
    out = HERE / "runs" / run / tag
    if (out / "summary.json").exists():
        return json.load(open(out / "summary.json"))
    out.mkdir(parents=True, exist_ok=True)
    w = scratch(script_src)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", **env_extra)
    t0 = time.time()
    snaps = {}
    with open(out / "log.txt", "w") as log:
        for s in ("experiments/ledger/v2_reruns.py", "experiments/ledger/build_ledger.py",
                  "experiments/ledger/merge_rows.py"):
            # Not -I: isolated mode implies -E, which IGNORES PYTHONHASHSEED (the hash seed is then random
            # on every run). -s -P keeps the other two parts of isolation (no user site, no script dir first).
            r = subprocess.run([str(PY), "-s", "-P", s], cwd=w, env=env, stdout=log, stderr=subprocess.STDOUT)
            if r.returncode:
                raise RuntimeError(f"{run}/{tag}: {s} failed, see {out / 'log.txt'}")
            if s == "experiments/ledger/build_ledger.py":
                snaps["build_ledger"] = ledger_rows(w)
                patch_committed_ledger(w)
            elif s == "experiments/ledger/merge_rows.py":
                snaps["merge_rows"] = ledger_rows(w)
    shutil.copy(w / "experiments" / "ledger" / "v2_reruns.json", out / "v2_reruns.json")
    keep = snaps["merge_rows"]
    v2 = json.load(open(out / "v2_reruns.json"))
    summ = dict(run=run, tag=tag, env=env_extra, seconds=round(time.time() - t0),
                v2_reruns_sha256=hashlib.sha256((out / "v2_reruns.json").read_bytes()).hexdigest(),
                F=v2["F_gulf_round"], ledger=keep, ledger_build_only=snaps["build_ledger"])
    json.dump(summ, open(out / "summary.json", "w"), indent=1)
    shutil.rmtree(w)
    print(f"{run}/{tag}: {summ['seconds']} s, lr_gulf p={keep['lr_gulf']['p_value']} "
          f"q_all={keep['lr_gulf']['q_all']}", flush=True)
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", choices=["A", "B", "C"])
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    if a.run == "A":
        src = subprocess.run(["git", "show", f"{BASE_COMMIT}:experiments/ledger/v2_reruns.py"], cwd=ROOT,
                             capture_output=True, check=True).stdout
        plan = [(f"hash{h:02d}", dict(PYTHONHASHSEED=str(h))) for h in range(20)]
    else:
        src = (ROOT / "experiments" / "ledger" / "v2_reruns.py").read_bytes()
        if a.run == "B":
            plan = [(f"hash{h:02d}", dict(PYTHONHASHSEED=str(h))) for h in range(3)]
        else:
            plan = [(f"seed{s:02d}", dict(INDUS_SEED=str(s), PYTHONHASHSEED=str(s + 100))) for s in range(1, 21)]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda tp: one(a.run, tp[0], src, tp[1]), plan))
    json.dump(res, open(HERE / "runs" / f"{a.run}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
