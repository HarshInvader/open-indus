"""search_scaling: does more search lift blind recovery under a related-language model?

Prereg: docs/prereg/search_scaling.md. Reuses rt.py (redteam_decipherability) unchanged for data,
models, scoring and the annealed Gibbs search. Run:
    .venv/bin/python -I experiments/search_scaling/ss.py time
    .venv/bin/python -I experiments/search_scaling/ss.py full
"""
import json, random, sys, time, zlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "redteam_decipherability"))
import rt  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def setup(pair, ntok, q, model, rep):
    """Identical corpus and model construction to rt.one_run."""
    cfg = rt.PAIRS[pair]
    rng = random.Random(zlib.crc32(f"{pair}|{ntok}|{q}|{rep}".encode()))
    paras = rt.paragraphs(cfg["src"])
    half_a = [p for i, p in enumerate(paras) if i % 2 == 0]
    half_b = [p for i, p in enumerate(paras) if i % 2 == 1]
    wl = np.mean([len(rt.word_values(w, set())) for p_ in half_a for w in p_])
    p_one = float(min(1.0, max(0.0, 2.0 - 4.5 / wl)))
    seqs, true_val, n = rt.make_corpus(half_a, ntok, q, rng, p_one)
    L = rt.train_lm(half_b, q) if model == "K0" else rt.train_lm(paragraphs_rel(cfg), q)
    N, cnt, truth, S = rt.collapse(seqs, true_val)
    return N, cnt, truth, S, L


def paragraphs_rel(cfg):
    return rt.paragraphs(cfg["rel"])


def restarts(pair, ntok, rep, R, sweeps, model="K2"):
    N, cnt, truth, S, L = setup(pair, ntok, 0.0, model, rep)
    s_true = rt.score(truth.copy(), N, cnt, L, S)
    srng = random.Random(zlib.crc32(f"ss|{pair}|{ntok}|{rep}|{sweeps}".encode()))
    res = []
    for r in range(R):
        k, sc = rt.search(N, cnt, L, S, srng, sweeps=sweeps)
        res.append((float(sc), rt.accuracy(k, truth, cnt, S)))
    return dict(pair=pair, ntok=ntok, rep=rep, R=R, sweeps=sweeps, model=model, true_score=float(s_true), runs=res)


def best_of(runs, n, g, B=500):
    """Bootstrap: accuracy of the top-scoring key among n restarts drawn with replacement."""
    runs = np.array(runs)
    out = []
    for _ in range(B):
        idx = g.integers(len(runs), size=n)
        out.append(runs[idx][np.argmax(runs[idx, 0]), 1])
    return float(np.mean(out))


def analyse():
    g = np.random.default_rng(0)
    rows = [json.loads(l) for l in open(OUT / "runs.jsonl")]
    out = {}
    for arm, sw, ns in (("R", 300, (1, 4, 10, 50, 200)), ("S", 3000, (1, 4, 20))):
        rs = [r for r in rows if r["sweeps"] == sw]
        curve = {n: float(np.mean([best_of(r["runs"], n, g) for r in rs])) for n in ns}
        per = {f'{r["pair"]}{r["rep"]}': dict(best_of_max=best_of(r["runs"], max(ns), g), max_acc=max(a for _, a in r["runs"]),
                                             share_above_true=float(np.mean([s > r["true_score"] for s, _ in r["runs"]])),
                                             wrong_above_true=any(s > r["true_score"] and a < 0.5 for s, a in r["runs"]),
                                             corr=float(np.corrcoef([s for s, _ in r["runs"]], [a for _, a in r["runs"]])[0, 1]))
               for r in rs}
        top = curve[max(ns)]
        verdict = "H1 search artefact" if top >= 0.50 else ("H0 not search" if top <= 0.25 else "partial")
        out[arm] = dict(curve=curve, per_replicate=per, verdict=verdict)
    print(json.dumps(out, indent=1)); (OUT / "verdicts.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "time":
        for sw in (300, 1500):
            t = time.time(); r = restarts("lat", 2500, 0, 1, sw); print("sweeps", sw, "secs", round(time.time() - t, 1), r["runs"])
        sys.exit()
    if mode == "analyse":
        analyse(); sys.exit()
    gf = OUT / "gate.json"
    if not gf.exists():
        g = {p: max(restarts(p, 2500, 0, 4, 300, "K0")["runs"])[1] for p in ("lat", "fin")}
        g["pass"] = all(v >= 0.90 for v in g.values())
        gf.write_text(json.dumps(g)); print("gate", g, flush=True)
    if not json.loads(gf.read_text())["pass"]:
        print("gate failed: uninformative"); sys.exit()
    f = OUT / "runs.jsonl"
    have = set()
    if f.exists():
        for line in f.read_text().splitlines():
            d = json.loads(line); have.add((d["pair"], d["ntok"], d["rep"], d["sweeps"]))
    plan = [(p, 2500, rep, 200, 300) for p in ("lat", "fin") for rep in range(3)]
    plan += [(p, 2500, rep, 20, 3000) for p in ("lat", "fin") for rep in range(3)]
    for p, n, rep, R, sw in plan:
        if (p, n, rep, sw) in have:
            continue
        d = restarts(p, n, rep, R, sw)
        with open(f, "a") as fh:
            fh.write(json.dumps(d) + "\n")
        accs = [a for _, a in d["runs"]]
        print(p, n, rep, R, sw, "max acc", round(max(accs), 3), "best-score acc", round(max(d["runs"])[1], 3), flush=True)
