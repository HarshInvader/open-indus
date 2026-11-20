"""Small Step 1: heavy search at Indus size (prereg docs/prereg/indus_size_search_check.md).

Uses the sealed mm.py (hash checked) for corpus, model, objective and conditionals. Adds only anchors:
anchored signs are fixed to their true values in init, skipped in sweeps and excluded from swaps.
Accuracy is token-weighted over NON-anchor signs. The cell's key is the restart with the best objective.

Cells: lat x anchors {0,5,10} x rep {0,1,2}; fin x anchors {10} x rep {0,1,2}. 2.5k tokens, syllabary, K2
(related-language model). Restarts in chunks of 125, up to 1,000, 100 sweeps each (as A3).
Stop rule per cell, checked after each chunk: stop when the best blind objective >= the truth-climbed
objective while the selected key's accuracy is < 0.5 (objective-limited).

Run from repo root, holding compute.lock.indus:
  OMP_NUM_THREADS=1 taskpolicy -b nice -n 20 .venv/bin/python -I experiments/mismatch_study/step1.py WORKERS MINUTES
"""
import hashlib, json, random, sys, time, zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEALED = "1e7181f0381e4c855fde086492cb613eaa397077185eb65280cfb8b0c97f1f2d"
assert hashlib.sha256((HERE / "mm.py").read_bytes()).hexdigest() == SEALED, "mm.py hash mismatch"
sys.path.insert(0, str(HERE))
import mm  # noqa: E402
import numpy as np  # noqa: E402

NTOK, KIND, CHUNK, MAXR, SWEEPS = 2500, "syll", 125, 1000, 100
CELLS_SEALED = [("lat", k, r) for k in (0, 5, 10) for r in range(3)] + [("fin", 10, r) for r in range(3)]
CELLS = [("lat", 0, r) for r in range(3)]  # change 1 (docs/prereg/indus_size_search_check_change1.md)
OUTF = mm.OUT / "step1.jsonl"


def setup(pair, k, rep):
    cp, ms, P2, sc = mm.build(pair, NTOK, KIND, rep, model="K2")
    rng = random.Random(zlib.crc32(f"anch|{pair}|{rep}".encode()))
    pool = sorted(s for s in range(cp.S) if cp.cnt[s] >= 5)
    ten = rng.sample(pool, 10)
    fixed = np.zeros(cp.S + 2, dtype=bool); fixed[ten[:k]] = True
    return cp, np.log(P2), fixed


def acc_free(cp, key, fixed):
    m = ~fixed[:cp.S]; c = cp.cnt[:cp.S] * m
    return float((c * (key[:cp.S] == cp.truth[:cp.S])).sum() / c.sum())


def search(cp, L, fixed, g, init=None, sweeps=SWEEPS, t0=3.0, greedy_only=False):
    """mm.gibbs + mm.polish with anchored signs held at their true values."""
    S, sc = cp.S, cp.sc
    key = np.zeros(S + 2, dtype=int); key[S] = sc.LOGO; key[S + 1] = sc.BND
    key[:S] = g.integers(0, sc.nv - 2, S) if init is None else init[:S]
    key[:S][fixed[:S]] = cp.truth[:S][fixed[:S]]
    free = [s for s in range(S) if not fixed[s] and cp.cnt[s] > 0]
    temps = [0.0] * 10 if greedy_only else list(np.linspace(t0, 1.0, sweeps - 10)) + [0.0] * 10
    for T in temps:
        cv = np.bincount(key[:S], weights=cp.cnt[:S], minlength=sc.nv).astype(float)
        for s in g.permutation(free):
            v = mm.cond2(s, key, cp, L, cv)
            new = int(np.argmax(v)) if T == 0 else int(g.choice(len(v), p=(lambda p: p / p.sum())(np.exp((v - v.max()) / T))))
            cv[key[s]] -= cp.cnt[s]; key[s] = new; cv[new] += cp.cnt[s]
    if greedy_only:
        return key, mm.score2(key, cp, L)
    return polish(cp, L, fixed, g, key)


def climb(pair, k, rep):
    cp, L, fixed = setup(pair, k, rep)
    g = np.random.default_rng(zlib.crc32(f"climb|{pair}|{k}|{rep}".encode()))
    key, _ = search(cp, L, fixed, g, init=cp.truth.copy(), greedy_only=True)
    key, sc = polish(cp, L, fixed, g, key)  # same moves the blind search gets
    return dict(kind="climb", pair=pair, k=k, rep=rep, obj=float(sc), acc=acc_free(cp, key, fixed),
                true_obj=float(mm.score2(cp.truth.copy(), cp, L)), S=cp.S, tokens=cp.tokens())


def polish(cp, L, fixed, g, key):
    """mm.polish restricted to free (non-anchor) signs."""
    S = cp.S; free = [s for s in range(S) if not fixed[s] and cp.cnt[s] > 0]
    best = mm.score2(key, cp, L)
    while True:
        improved = False
        for i, a in enumerate(free):
            for b in free[i + 1:]:
                if key[a] == key[b]:
                    continue
                key[a], key[b] = key[b], key[a]
                s_ = mm.score2(key, cp, L)
                if s_ > best + 1e-9:
                    best, improved = s_, True
                else:
                    key[a], key[b] = key[b], key[a]
        k2, s2 = search(cp, L, fixed, g, init=key.copy(), greedy_only=True)
        if s2 > best + 1e-9:
            key, best, improved = k2, s2, True
        if not improved:
            return key, best


def chunk(pair, k, rep, c):
    cp, L, fixed = setup(pair, k, rep)
    g = np.random.default_rng(zlib.crc32(f"s1|{pair}|{k}|{rep}".encode()) * 1000 + c)
    best = None
    for _ in range(CHUNK):
        key, sc = search(cp, L, fixed, g)
        a = acc_free(cp, key, fixed)
        if best is None or sc > best[0]:
            best = (float(sc), a)
    return dict(kind="chunk", pair=pair, k=k, rep=rep, chunk=c, obj=best[0], acc=best[1])


def load():
    return [json.loads(l) for l in OUTF.read_text().splitlines() if l.strip()] if OUTF.exists() else []


def cell_state(rows, cell):
    p, k, r = cell
    cl = [x for x in rows if x["kind"] == "climb" and (x["pair"], x["k"], x["rep"]) == cell]
    ch = sorted([x for x in rows if x["kind"] == "chunk" and (x["pair"], x["k"], x["rep"]) == cell], key=lambda x: x["chunk"])
    if not cl:
        return dict(climb=None, chunks=ch, stop=False, done=False)
    b = max(ch, key=lambda x: x["obj"]) if ch else None
    stop = bool(b and b["obj"] >= cl[0]["obj"] and b["acc"] < 0.5)
    return dict(climb=cl[0], chunks=ch, best=b, stop=stop, done=stop or len(ch) >= MAXR // CHUNK)


def summarise(rows):
    out = {}
    for cell in CELLS:
        st = cell_state(rows, cell)
        if not st["climb"] or not st["chunks"]:
            continue
        b, cl = st["best"], st["climb"]
        if b["acc"] >= 0.5:
            label = "solved"
        elif b["obj"] >= cl["obj"]:
            label = "objective-limited"
        else:
            label = "search-limited" if st["done"] else "running"
        out["|".join(map(str, cell))] = dict(acc=round(b["acc"], 3), best_obj=round(b["obj"], 1), climb_obj=round(cl["obj"], 1),
                                            climb_acc=round(cl["acc"], 3), restarts=len(st["chunks"]) * CHUNK, label=label)
    return out


def main(workers, minutes):
    stop_at = time.time() + 60 * minutes
    with ProcessPoolExecutor(workers) as pool:
        live = {}
        while True:
            rows = load()
            inflight = set(live.values())
            todo = []
            for cell in CELLS:
                st = cell_state(rows, cell)
                if st["climb"] is None:
                    if ("climb", cell) not in inflight:
                        todo.append((climb, cell, ("climb", cell)))
                    continue
                if st["done"]:
                    continue
                # one chunk in flight per cell, so the stop rule is checked between chunks
                if any(t[0] == "chunk" and t[1] == cell for t in inflight):
                    continue
                todo.append((chunk, cell + (len(st["chunks"]),), ("chunk", cell)))
            while todo and len(live) < workers and time.time() < stop_at:
                fn, args, tag = todo.pop(0)
                live[pool.submit(fn, *args)] = tag
            if not live:
                break
            f = next(as_completed(live))
            live.pop(f)
            rec = f.result()
            with open(OUTF, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(json.dumps(rec), flush=True)
    s = summarise(load())
    (mm.OUT / "step1_summary.json").write_text(json.dumps(s, indent=1))
    print("SUMMARY", json.dumps(s), flush=True)
    alld = all(cell_state(load(), c)["done"] for c in CELLS)
    print("ALL DONE" if alld else "TIME UP; rerun to resume", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4, float(sys.argv[2]) if len(sys.argv) > 2 else 100)
