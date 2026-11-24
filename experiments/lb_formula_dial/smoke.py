"""Smoke tests for run.py that compute no IC on a real or planted key.
  .venv/bin/python -I experiments/lb_formula_dial/smoke.py toy        # lattice scorer vs enumeration, invented data
  .venv/bin/python -I experiments/lb_formula_dial/smoke.py time       # one 2.0-rung job timed on an invented key and corpus
  .venv/bin/python -I experiments/lb_formula_dial/smoke.py labelfree  # targets, G0, tilt/D1 builds, loose keys (no IC)
  .venv/bin/python -I experiments/lb_formula_dial/smoke.py plumb      # cell_job and readings on invented data
"""
import importlib.util, json, random, sys, time
from itertools import product
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dial", HERE / "run.py")
D = importlib.util.module_from_spec(_spec); sys.modules["dial"] = D; _spec.loader.exec_module(D)
L = D.L
CONS = "dkmnpqrstz"


def toy_lex(rng, n=1500, A="kmn"):
    lex = set()
    for _ in range(n):
        lex.add(tuple(rng.choice(A) for _ in range(rng.randint(1, 7))))
    return lex, {t[:i] for t in lex for i in range(1, len(t) + 1)}


def brute(tokens, lex):
    best = -1
    for ch in product(*tokens):
        c = [x for a in ch for x in a]
        best = max(best, L.ic_seg(c, lex))
    return best


def toy():
    rng = random.Random(1)
    lex, pre = toy_lex(rng)
    n_ok = n_hit = 0
    for trial in range(3000):
        toks = []
        for _ in range(rng.randint(1, 8)):
            m = rng.choice([1, 1, 1, 2, 3])
            na = rng.choice([1, 1, 2, 3])
            toks.append(tuple(tuple(rng.choice("kmnp") for _ in range(m)) for _ in range(na)))
        a = D.lattice(toks, lex, pre)[0]; b = brute(toks, lex)
        assert a == b, (trial, toks, a, b)
        if all(len(t) == 1 for t in toks):
            assert a == L.ic_seg([x for t in toks for x in t[0]], lex)
        n_ok += 1; n_hit += a > 0
    # LatticeIC with one value per sign equals the sealed IC class on an invented corpus and key
    signs = [f"X{i}" for i in range(60)]
    key = {s: [rng.choice("kmnp") for _ in range(rng.choice([0, 1, 1, 1, 2]))] for s in signs}
    texts = [[[rng.choice(signs) for _ in range(rng.randint(2, 12))]] for _ in range(300)]
    D.LEX = lex
    a = L.IC(texts, lex).full(key); b = D.LatticeIC(texts, lex, pre).full({s: (tuple(v),) for s, v in key.items()})
    assert abs(a - b) < 1e-15, (a, b)
    print(dict(lattice_vs_enumeration_ok=n_ok, nonzero=n_hit, single_value_equals_sealed_IC=True))


def time_job():
    """Invented key and corpus (no Linear B text, no true key); the real Homeric lexicon gives realistic density.
    Mimics one cell job: 1 + 1000 scorings on held-out and on scrambled text."""
    D.init(); rng = random.Random(7); nrng = np.random.default_rng(7)
    lens = L.base.m77_lengths()
    signs = [f"X{i}" for i in range(166)]
    key1 = {s: [rng.choice("kmnprst") for _ in range(rng.choice([0] * 10 + [1] * 85 + [2] * 5))] for s in signs}
    tok = 0; ho = []
    while tok < 4000:
        n = int(lens[nrng.integers(len(lens))]); ho.append([[rng.choice(signs) for _ in range(n)]]); tok += n
    by = {}
    for s in signs:
        by.setdefault(len(key1[s]), []).append(s)
    key2 = {}
    for s in signs:
        dn = [d for d in by[len(key1[s])] if d != s and key1[d] != key1[s]]
        key2[s] = (tuple(key1[s]), tuple(key1[rng.choice(dn)])) if dn else (tuple(key1[s]),)
    freq = {s: 1 + rng.randint(0, 50) for s in signs}
    cl = L.classes(signs, key1)
    t0 = time.time(); H = L.IC(ho, D.LEX)
    for _ in range(50):
        H.full(L.permute_in_class_bins(key1, cl, freq, rng))
    t1 = (time.time() - t0) / 50
    t0 = time.time()
    for txt in (ho, L.unigram(ho, rng)):
        H2 = D.LatticeIC(txt, D.LEX, D.PRE)
        for _ in range(1001):
            H2.full(L.permute_in_class_bins(key2, cl, freq, rng))
    job2 = time.time() - t0
    print(json.dumps(dict(tokens=tok, chunks=len(ho), sealed_IC_one_scoring_s=round(t1, 4),
                          lattice_2p0_job_s=round(job2, 1), lattice_2p0_per_scoring_s=round(job2 / 2002, 4))))


def labelfree():
    summ, draws, corp, lkeys = D.labelfree()
    print(json.dumps({k: v for k, v in summ.items() if k not in ("rungs", "loose")}, indent=1, default=str))
    for rung in ("F0", "F1", "F2", "D1"):
        rr = summ["rungs"][rung]
        ok = [r for r in rr if r.get("ok", True)]
        print(rung, dict(n=len(rr), ok=len(ok), excess=[round(r["excess"], 4) for r in ok],
                         tau=[round(r["tau"], 3) for r in ok if "tau" in r],
                         tokens=[r["tokens"] for r in ok][:5], growth=[round(r["token_growth"], 2) for r in ok if "token_growth" in r],
                         fails=[(r["k"], r["why"]) for r in rr if not r.get("ok", True)],
                         pool_tokens=[r["pool_tokens"] for r in rr if "pool_tokens" in r][:3]))
    for lr in ("1.18", "2.0"):
        ii = summ["loose"][lr]
        print(lr, dict(ok=sum(i["ok"] for i in ii), share=[round(i["loose_token_share_ho"], 3) for i in ii],
                       vps=round(float(np.mean([i["values_per_sign"] for i in ii])), 3),
                       no_donor=[i["n_no_donor"] for i in ii][:5]))


def plumb():
    """cell_job, summarise and readings end to end in-process, on an invented corpus, key and lexicon
    (true_value patched to the invented key; nothing of Linear B is scored)."""
    rng = random.Random(3)
    lex, pre = toy_lex(rng)
    signs = [f"X{i}" for i in range(80)]
    inv = {s: [rng.choice("kmnp") for _ in range(rng.choice([0, 1, 1, 1, 2]))] for s in signs}
    D.B.true_value = lambda s: list(inv[s]); D.LEX, D.PRE = lex, pre
    dev = [[[rng.choice(signs) for _ in range(rng.randint(2, 9))]] for _ in range(200)]
    ho = [[[rng.choice(signs) for _ in range(rng.randint(2, 9))]] for _ in range(200)]
    d1 = ho + ho[:20]
    freq = D.Counter(s for t in dev + ho for w in t for s in w)
    lk, info = D.loose_key(1, "2.0", dev, ho)
    D.NPERM = 50
    rows = {}
    for name, h, lr, key in (("F0", ho, "1.0", None), ("D1", d1, "1.0", None), ("F0", ho, "2.0", lk), ("D1", d1, "2.0", lk)):
        rows[(name, lr)] = D.cell_job((1, name, lr, h, freq, key))
    assert rows[("F0", "1.0")]["n1_keys_sha256"] == rows[("D1", "1.0")]["n1_keys_sha256"]
    assert rows[("F0", "2.0")]["n1_keys_sha256"] == rows[("D1", "2.0")]["n1_keys_sha256"]
    cells = {"F0 x 1.0": D.summarise([rows[("F0", "1.0")]]), "F1 x 1.0": D.summarise([rows[("F0", "1.0")]]),
             "F0 x 1.18": D.summarise([rows[("F0", "2.0")]]), "F1 x 1.18": D.summarise([rows[("F0", "2.0")]])}
    R = D.readings(cells, dict(G0_applied=False, gate=dict(F2=dict(reachable=False))), False)
    print(dict(plumbing_ok=True, loose_info={k: info[k] for k in ("n_loose", "n_no_donor", "values_per_sign")},
               reading_keys=sorted(R)))


if __name__ == "__main__":
    {"toy": toy, "time": time_job, "labelfree": labelfree, "plumb": plumb}[sys.argv[1]]()
