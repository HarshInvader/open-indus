"""Parallel driver for mismatch_study stage 1 (laptop, several processes at background priority).

Calls only the sealed functions of mm.py (sha256 04ef0c0f...; checked at start). It reproduces mm.py's
stage loops cell by cell, with the same seeds and record fields, but runs cells in a process pool and
writes every finished record from the main process (checkpoint = the jsonl files; rerun resumes).

Two things differ from running mm.py's stages serially, both allowed by the prereg:
  * A3 (1,000 restarts) and A3+ (10,000 restarts, prereg section 5, now approved by the owner) are split
    into chunks of 125 restarts. Chunk c of a cell uses run_attack(..., seed = base_seed * 1000 + c).
    The cell's answer is the chunk answer with the highest objective; max_acc is the max over chunks.
    (Serial mm.py would draw all restarts from one stream; the design - n restarts, score-selected - is
    the same.)
  * Phase order: planted checks and attack gate first; the kill test starts only after PC1-PC3 have been
    judged by mm.analyse(). If a planted check fails, the kill test is not run (prereg section 4).

  * A3+ cells are reported under the same kill rule as A3 (valid if A0 passes its gate) in
    out/verdicts_a3plus.json; mm.analyse() itself does not know A3+. They run last, after the sealed
    A0-A3 cells.
  * The run stops submitting new cells after --minutes (default 100) so each harness job (2 h cap) ends
    cleanly; rerunning resumes.

Run from repo root, holding the shared compute lock:
  OMP_NUM_THREADS=1 taskpolicy -b nice -n 20 .venv/bin/python -I experiments/mismatch_study/par.py WORKERS MINUTES
"""
import hashlib, json, os, sys, time, zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEALED = "04ef0c0f77baec628537f06b353f439aadfedd5c43bb030bfd70e240aab96a13"
got = hashlib.sha256((HERE / "mm.py").read_bytes()).hexdigest()
assert got == SEALED, f"mm.py hash {got} != sealed {SEALED}"
sys.path.insert(0, str(HERE))
import mm  # noqa: E402
import numpy as np  # noqa: E402

CHUNK = 125


def t_pc1(pair, kind):
    cp, ms, P2, sc = mm.build(pair, 2500, kind, 0, model="K0")
    r = mm.run_attack("A0", cp, ms, P2, seed=1)
    return "pc1", dict(pair=pair, kind=kind, ntok=2500, S=cp.S, tokens=cp.tokens(), **r)


def t_pc2(lam, rep):
    cp, Q, dH = mm.synth_cell(lam, rep)
    r = mm.run_attack("A0", cp, None, Q, seed=2 + rep)
    return "pc2", dict(lam=lam, rep=rep, dH=dH, S=cp.S, tokens=cp.tokens(), **r)


def t_pc3(pair):
    cp, ms, P2, sc = mm.build(pair, 10000, "syll", 0, model="K0", shuffle=True)
    r = mm.run_attack("A0", cp, ms, P2, seed=3)
    return "pc3", dict(pair=pair, ntok=10000, freq_baseline=mm.freq_rank_baseline(cp, ms), **r)


def t_gate(pair, att):
    cp, ms, P2, sc = mm.build(pair, 10000, "syll", 0, model="K0")
    r = mm.run_attack(att, cp, ms, P2, seed=4)
    return "gate", dict(pair=pair, att=att, **r)


def t_kill(p, n, a, r):
    cp, ms, P2, sc = mm.build(p, n, "syll", r, model="K2")
    res = mm.run_attack(a, cp, ms, P2, seed=zlib.crc32(f"{p}{n}{a}{r}".encode()))
    res["true_obj_A0"] = mm.score2(cp.truth.copy(), cp, np.log(P2))
    return "kill", dict(pair=p, ntok=n, att=a, rep=r, S=cp.S, tokens=cp.tokens(), **res)


def t_chunk(p, n, a, r, c):
    cp, ms, P2, sc = mm.build(p, n, "syll", r, model="K2")
    base = zlib.crc32(f"{p}{n}{a}{r}".encode())
    res = mm.run_attack("A3", cp, ms, P2, seed=base * 1000 + c, R=CHUNK)
    return "chunks", dict(pair=p, ntok=n, att=a, rep=r, chunk=c, acc=res["acc"], obj=res["obj"],
                          max_acc=res["max_acc"], S=cp.S, tokens=cp.tokens(),
                          true_obj_A0=mm.score2(cp.truth.copy(), cp, np.log(P2)))


def done(name, keys):
    f = mm.OUT / f"{name}.jsonl"
    if not f.exists():
        return set()
    return {tuple(json.loads(l)[k] for k in keys) for l in f.read_text().splitlines() if l.strip()}


def write(name, rec):
    with open(mm.OUT / f"{name}.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(name, json.dumps({k: v for k, v in rec.items() if k != "restart_accs"}), flush=True)


def run(pool, tasks, workers, stop_at):
    """Keep at most `workers` cells in flight; submit nothing new after stop_at. Returns True if all ran."""
    tasks, live = list(tasks), set()
    while tasks or live:
        while tasks and len(live) < workers and time.time() < stop_at:
            fn, args = tasks.pop(0)
            live.add(pool.submit(fn, *args))
        if not live:
            return False
        f = next(as_completed(live))
        live.discard(f)
        write(*f.result())
    return True


def ok(x):
    return x in (True, "True")  # verdicts.json stores numpy bools as strings


def combine_chunks():
    """Fold chunk records into one kill.jsonl row per A3/A3+ cell, once all its chunks are in."""
    f = mm.OUT / "chunks.jsonl"
    if not f.exists():
        return
    rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    have = done("kill", ("pair", "ntok", "att", "rep"))
    cells = {}
    for x in rows:
        cells.setdefault((x["pair"], x["ntok"], x["att"], x["rep"]), []).append(x)
    for k, xs in cells.items():
        need = (1000 if k[2] == "A3" else 10000) // CHUNK
        if k in have or len({x["chunk"] for x in xs}) < need:
            continue
        best = max(xs, key=lambda x: x["obj"])
        write("kill", dict(pair=k[0], ntok=k[1], att=k[2], rep=k[3], S=best["S"], tokens=best["tokens"],
                           acc=best["acc"], obj=best["obj"], max_acc=max(x["max_acc"] for x in xs),
                           n_restarts=need * CHUNK, restart_accs=None, true_obj_A0=best["true_obj_A0"],
                           chunked=CHUNK))


def a3plus_verdict():
    v = json.loads((mm.OUT / "verdicts.json").read_text())
    rows = [r for r in mm.load("kill") if r["att"] == "A3+"]
    means = {f'{r["pair"]}|{r["ntok"]}|A3+': r["acc"] for r in rows}
    valid = "A0" in v["kill_test"]["valid_attacks"]
    out = dict(valid=valid, cell_means=means, cells=len(rows),
               kill=bool(valid and any(m > 0.5 for m in means.values())))
    (mm.OUT / "verdicts_a3plus.json").write_text(json.dumps(out, indent=1))
    print("A3+", json.dumps(out), flush=True)


def main(workers, minutes):
    stop_at = time.time() + 60 * minutes
    P = list(mm.PAIRS)
    with ProcessPoolExecutor(workers) as pool:
        # phase 1: planted checks + attack gate
        t = [(t_pc1, (p, k)) for p in P for k in ("alpha", "syll", "logo") if (p, k) not in done("pc1", ("pair", "kind"))]
        t += [(t_pc2, (l, r)) for r in (0, 1) for l in (1.0, 0.8, 0.6, 0.4, 0.2, 0.0) if (l, r) not in done("pc2", ("lam", "rep"))]
        t += [(t_pc3, (p,)) for p in P if (p,) not in done("pc3", ("pair",))]
        t += [(t_gate, (p, a)) for p in P for a in ("A0", "A1", "A2") if (p, a) not in done("gate", ("pair", "att"))]
        if not run(pool, t, workers, stop_at):
            print("TIME UP in phase 1; rerun to resume", flush=True); return
        mm.stage_pc2()  # all cells done -> only the planted-surface fit runs
        mm.analyse()
        v = json.loads((mm.OUT / "verdicts.json").read_text())
        if not all(ok(v[k]["pass_"]) for k in ("PC1", "PC2", "PC3")):
            print("PLANTED CHECK FAILED: kill test not run (prereg section 4)", flush=True)
            return
        # phase 2: sealed kill test (A0-A3), then A3+
        kd = done("kill", ("pair", "ntok", "att", "rep"))
        cd = done("chunks", ("pair", "ntok", "att", "rep", "chunk"))
        t = [(t_kill, (p, n, a, r)) for n in (30000, 10000, 2500) for a in ("A1", "A2", "A0") for p in P
             for r in range(3) if (p, n, a, r) not in kd]
        t += [(t_chunk, (p, n, "A3", 0, c)) for p in P for n in (30000, 10000) for c in range(1000 // CHUNK)
              if (p, n, "A3", 0, c) not in cd]
        t += [(t_chunk, (p, n, "A3+", 0, c)) for c in range(10000 // CHUNK) for p in P for n in (30000, 10000)
              if (p, n, "A3+", 0, c) not in cd]
        finished = run(pool, t, workers, stop_at)
    combine_chunks()
    mm.analyse()
    a3plus_verdict()
    print("ALL DONE" if finished else "TIME UP; rerun to resume", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4, float(sys.argv[2]) if len(sys.argv) > 2 else 100)
