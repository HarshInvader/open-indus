"""Planted gate for crib attack v2 (task #26).  Pre-registered in docs/prereg/crib_attack_v2_planted.md.
No Indus outcomes are used: only the real TEXT LENGTHS of the foreign / home-round sets.
Run (from repo root):  board/run.sh .venv/bin/python -I experiments/crib_attack_v2/run_grid.py [--time]
Appends one JSON record per search to experiments/crib_attack_v2/out/grid.jsonl (resumable)."""
import sys, json, time, csv
from pathlib import Path
import numpy as np
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from names2 import capped_list, cv_variants, write_cv  # noqa
from method import make_corpus, shuffle_texts, NameIndex, Attack  # noqa

ATT_LISTS = {"elamite30": ("elamite", 30), "gulf": ("gulf", 200), "elamite": ("elamite", 200),
             "akkadian": ("akkadian", 200), "sumerian": ("sumerian", 200)}
WRONG = "amorite"
NS = [9, 11, 20, 41, 49]
ANCHORS = [0, 3, 6]
REPS = {"planted": 20, "wronglang": 10, "shuffle": 40}
MISREAD, P_NAME = 0.2, 0.75
SAFE9 = ["UR-01", "UNPROV-02", "SUSA-02", "BAHRAIN-01", "BAHRAIN-06", "BAHRAIN-07", "GIRSU-02",
         "SALUT-01", "UNPROV-03"]
EXTRA11 = ["SUSA-01", "LURISTAN-01"]
HOME_ROUND_LENGTHS = [4, 2, 2, 5, 8, 7, 5, 4]  # ICIT 114.1 2419.2 2911.1 2912.1 2977.1 3668.1 4247.1 5468.1


def iters_for(n):
    return 1500 + 60 * n


def real_lengths():
    r = {x["id"]: x for x in csv.DictReader(open(ROOT / "experiments/foreign_corpus/foreign_corpus.csv"))}
    leg = [int(x["n_legible"]) for x in r.values() if x["n_legible"] and int(x["n_legible"]) >= 2]
    L9 = [int(r[i]["n_legible"]) for i in SAFE9]
    L11 = L9 + [int(r[i]["n_legible"]) for i in EXTRA11]
    return {9: L9, 11: L11, 41: leg, 49: leg + HOME_ROUND_LENGTHS, 20: leg}


_C = {}


def setup():
    if _C:
        return _C
    lists = {}
    allu = []
    for tag, (nm, cap) in ATT_LISTS.items():
        lists[tag] = capped_list(nm, cap=cap)
        allu += lists[tag][0]
    wu, wsp = capped_list(WRONG)
    allu += wu
    vals = sorted({x for u in allu for v in cv_variants(u, max_free=8) for x in v})
    vid = {v: i for i, v in enumerate(vals)}
    _C.update(lists=lists, wrong=wu, values=vals, vid=vid, lengths=real_lengths(),
              ni={t: NameIndex(sp, vid) for t, (u, sp) in lists.items()})
    return _C


def job(args):
    tag, n, a, kind, rep = args
    C = setup()
    rng = np.random.default_rng([26, NS.index(n), ANCHORS.index(a), list(REPS).index(kind), rep,
                                 list(ATT_LISTS).index(tag)])
    L = C["lengths"][n]
    if n == 20:
        L = [int(x) for x in rng.choice(L, size=20, replace=False)]
    units = C["wrong"] if kind == "wronglang" else C["lists"][tag][0]
    c = make_corpus(L, units, C["values"], rng, write_cv, p_name=P_NAME, misread=MISREAD)
    tk = c["true_key"]
    toks = np.concatenate([np.asarray(t) for t in c["texts"]])
    cnt = np.bincount(toks, minlength=c["nsigns"])
    syl = np.flatnonzero((tk >= 0) & (cnt > 0))
    anchors = {int(s): int(tk[s]) for s in syl[np.argsort(-cnt[syl], kind="stable")][:a]}
    texts = shuffle_texts(c["texts"], rng) if kind == "shuffle" else c["texts"]
    ni = C["ni"][tag]
    att = Attack(texts, ni, c["nsigns"], len(C["values"]), rng, anchors=anchors)
    t0 = time.time()
    E, key = att.run(iters_for(n), restarts=3)
    E_true = att.score(tk) if kind != "shuffle" else None
    used = att.reading(key)
    corr = [s for s in used if key[s] == tk[s]]
    syl_na = [int(s) for s in syl if int(s) not in anchors]
    return dict(list=tag, n=n, a=a, kind=kind, rep=rep, E=int(E), E_true=E_true,
                n_matchable=len(att.matchable), n_name_texts=int(sum(c["name_text"])),
                n_used=len(used), n_correct=len(corr), n_syl=len(syl_na), secs=round(time.time() - t0, 2))


# Amendment 1 (docs/prereg/crib_attack_v2_planted_amend1.md): compute cut before any outcome was read.
GRID_LISTS = ["elamite30", "gulf", "elamite", "akkadian"]   # sumerian dropped
GRID_NS = [9, 20, 41, 49]                                     # n = 11 dropped
A6_NS = [49]                                                  # a = 6 only at n = 49


def all_jobs():
    return [(t, n, a, k, r) for a in ANCHORS for n in GRID_NS for t in GRID_LISTS for k, R in REPS.items()
            for r in range(R) if a < 6 or n in A6_NS]


if __name__ == "__main__":
    out = HERE / "out"; out.mkdir(exist_ok=True)
    if "--time" in sys.argv:  # timing probe: a few searches, not part of the grid
        for j in [("sumerian", 49, 0, "shuffle", 0), ("sumerian", 49, 0, "planted", 0), ("gulf", 9, 3, "planted", 0),
                  ("akkadian", 41, 6, "shuffle", 0)]:
            r = job(j); print(json.dumps(r), flush=True)
        sys.exit()
    jl = out / "grid.jsonl"
    done = set()
    if jl.exists():
        for line in open(jl):
            r = json.loads(line); done.add((r["list"], r["n"], r["a"], r["kind"], r["rep"]))
    jobs = [j for j in all_jobs() if j not in done]
    print("jobs left", len(jobs), flush=True)
    with Pool(2) as p, open(jl, "a") as fh:  # laptop limit: 2 workers
        for i, res in enumerate(p.imap_unordered(job, jobs, chunksize=4)):
            fh.write(json.dumps(res) + "\n"); fh.flush()
            if i % 500 == 0:
                print(i, flush=True)
    print("done", flush=True)
