"""Do Indus tablets and pots quote same-site seal texts? (prereg docs/prereg/tablet_quoting.md)
Run: .venv/bin/python -I experiments/tablet_quoting/run.py shape   # counts only
     .venv/bin/python -I experiments/tablet_quoting/run.py kill    # Ur III rehearsal at Indus size (200 draws)
     .venv/bin/python -I experiments/tablet_quoting/run.py full    # planted Indus gate, then the real test
"""
import json, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
SEED = 20261128
SITES = ("Harappa", "Mohenjo-daro")
NFORM = 50
N1_REAL, N2_REAL, N1_DRAW, N2_DRAW = 2000, 1000, 300, 300
KILL_DRAWS, PLANT_DRAWS = 200, 40
DELTAS = (0.02, 0.05, 0.10, 0.20)


def grp(t):
    if t.startswith("SEAL"):
        return "seal"
    if t in ("TAB:B", "TAB:I", "TAB:C"):
        return t
    if t.startswith("POT"):
        return "pot"
    return None


# ------------------------------------------------------------------ data
def indus():
    """Distinct complete texts: seals[site] (>= 3 signs) and targets[site] = [(seq, group)] (>= 3 signs)."""
    seals = {s: set() for s in SITES}; targ = {s: {} for s in SITES}
    for l in open(ROOT / "data/icit_texts.jsonl"):
        r = json.loads(l)
        if r["site"] not in SITES or not r.get("complete"):
            continue
        g = grp(r["type"]); seq = tuple(x for x in r["seq"] if x.startswith("W"))
        if g is None or len(seq) < 3:
            continue
        if g == "seal":
            seals[r["site"]].add(seq)
        else:
            targ[r["site"]].setdefault(seq, g)
    return {s: sorted(v) for s, v in seals.items()}, {s: sorted(v.items()) for s, v in targ.items()}


def tri(seq):
    return {tuple(seq[i:i + 3]) for i in range(len(seq) - 2)}


def formulae(texts, n=NFORM):
    c = Counter(t for s in texts for t in tri(s))
    return {t for t, _ in c.most_common(n)}


# ------------------------------------------------------------------ statistic and nulls
class Test:
    def __init__(self, seals, targ, form):
        """seals: {site: [seq]}, targ: {site: [seq]}."""
        self.form = form
        self.seal_list = [(s, tri(q) - form, len(q)) for s in SITES for q in seals[s]]
        self.targ = {s: [tri(q) - form for q in targ[s]] for s in SITES}

    def T(self, labels):
        pool = {s: set() for s in SITES}
        for (_, tr, _), lab in zip(self.seal_list, labels):
            pool[lab] |= tr
        hit = {s: sum(1 for t in self.targ[s] if t & pool[s]) for s in SITES}
        n = {s: len(self.targ[s]) for s in SITES}
        return sum(hit.values()) / sum(n.values()), {s: hit[s] / n[s] if n[s] else 0.0 for s in SITES}

    def real_labels(self):
        return [s for s, _, _ in self.seal_list]

    def perm(self, rng):
        lab = np.array(self.real_labels(), dtype=object)
        L = np.array([min(l, 7) for _, _, l in self.seal_list])
        out = lab.copy()
        for b in np.unique(L):
            idx = np.where(L == b)[0]; out[idx] = lab[rng.permutation(idx)]
        return list(out)


def bigram_regen(targ, rng):
    """Regenerate every target text (same site, same length) from a bigram model fitted on all targets."""
    nxt = defaultdict(list); starts = []
    for s in SITES:
        for q in targ[s]:
            starts.append(q[0])
            for a, b in zip(q, q[1:]):
                nxt[a].append(b)
    out = {}
    for s in SITES:
        out[s] = []
        for q in targ[s]:
            x = [starts[rng.integers(len(starts))]]
            while len(x) < len(q):
                c = nxt.get(x[-1])
                x.append(c[rng.integers(len(c))] if c else starts[rng.integers(len(starts))])
            out[s].append(tuple(x))
    return out


def evaluate(seals, targ, rng, n1, n2, form=None):
    if form is None:
        form = formulae([q for s in SITES for q in seals[s]] + [q for s in SITES for q in targ[s]])
    t = Test(seals, targ, form); obs, per = t.T(t.real_labels())
    nl = [t.T(t.perm(rng)) for _ in range(n1)]
    null1 = np.array([x[0] for x in nl]); per_null = {s: float(np.mean([x[1][s] for x in nl])) for s in SITES}
    b = []
    for _ in range(n2):
        tb = Test(seals, bigram_regen(targ, rng), form); b.append(tb.T(tb.real_labels())[0])
    b = np.array(b)
    p1 = float((1 + (null1 >= obs).sum()) / (n1 + 1))
    excess = {s: per[s] - per_null[s] for s in SITES}
    passed = bool(p1 <= 0.01 and all(v > 0 for v in excess.values()) and obs > np.quantile(b, .99))
    return dict(T=obs, per_site=per, p_site_perm=p1, null1_mean=float(null1.mean()), per_site_excess=excess,
                bigram_mean=float(b.mean()), bigram_p99=float(np.quantile(b, .99)), passed=passed)


# ------------------------------------------------------------------ Ur III rehearsal
def ur3():
    by = defaultdict(list)
    for l in open(HERE / "data/ur3_sealed.jsonl"):
        r = json.loads(l)
        if r["prov"] in ("Umma", "Girsu"):
            by[r["prov"]].append(r)
    return by


U = {}


def init_kill():
    s, t = indus(); U["ur3"] = ur3()
    U["seal_len"] = {k: [len(q) for q in v] for k, v in s.items()}
    U["targ_len"] = {k: [len(q) for q, _ in v] for k, v in t.items()}


def kill_draw(d):
    rng = np.random.default_rng(SEED + d); rr = random.Random(SEED + d)
    m = {"Mohenjo-daro": "Umma", "Harappa": "Girsu"}          # larger seal site <-> larger Ur III archive
    seals, targ = {}, {}
    for s in SITES:
        tabs = U["ur3"][m[s]]
        legs = list({tuple(l) for r in tabs for l in r["legends"] if len(l) >= 3})
        rr.shuffle(legs); legs = legs[:len(U["seal_len"][s])]
        seals[s] = []
        for q, L in zip(legs, rr.sample(U["seal_len"][s], len(legs))):
            L = min(L, len(q)); i = rr.randrange(len(q) - L + 1); seals[s].append(q[i:i + L])
        bodies = rr.sample(tabs, len(U["targ_len"][s])); targ[s] = []
        for r, L in zip(bodies, U["targ_len"][s]):
            q = [x for line in r["body"] for x in line]
            if len(q) < 3:
                continue
            L = min(L, len(q)); i = rr.randrange(len(q) - L + 1); targ[s].append(tuple(q[i:i + L]))
    res = evaluate(seals, targ, rng, N1_DRAW, N2_DRAW)
    res["d"] = d
    return res


# ------------------------------------------------------------------ planted Indus gate and real test
I = {}


def init_full():
    s, t = indus(); I["seals"] = s; I["targ"] = {k: [q for q, _ in v] for k, v in t.items()}; I["groups"] = t
    I["form"] = formulae([q for k in SITES for q in s[k]] + [q for k in SITES for q in I["targ"][k]])


def plant_draw(args):
    delta, d = args
    rng = np.random.default_rng(SEED + 5000 + int(delta * 1000) * 100 + d); rr = random.Random(SEED + 77 + int(delta * 1000) * 100 + d)
    targ = {}
    for s in SITES:
        src = [sorted(tri(q) - I["form"]) for q in I["seals"][s]]; src = [x for x in src if x]
        tl = list(I["targ"][s]); k = int(round(delta * len(tl)))
        for j in rr.sample(range(len(tl)), k):
            run = rr.choice(rr.choice(src)); q = list(tl[j]); i = rr.randrange(len(q) - 2)
            q[i:i + 3] = run; tl[j] = tuple(q)
        targ[s] = tl
    res = evaluate(I["seals"], targ, rng, N1_DRAW, N2_DRAW, form=I["form"])
    res.update(delta=delta, d=d)
    return res


def by_group():
    """Descriptive: T per target group with the site-permutation null (formulae as in the real test)."""
    rng = np.random.default_rng(SEED + 999); out = {}
    for g in ("TAB:B", "TAB:I", "TAB:C", "pot"):
        targ = {s: [q for q, gg in I["groups"][s] if gg == g] for s in SITES}
        if sum(len(v) for v in targ.values()) < 10:
            continue
        t = Test(I["seals"], targ, I["form"]); obs, per = t.T(t.real_labels())
        null = np.array([t.T(t.perm(rng))[0] for _ in range(N1_REAL)])
        out[g] = dict(n={s: len(targ[s]) for s in SITES}, T=obs, null_mean=float(null.mean()),
                      p=float((1 + (null >= obs).sum()) / (N1_REAL + 1)))
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    if mode == "shape":
        s, t = indus(); u = ur3()
        print(dict(seals={k: len(v) for k, v in s.items()}, targets={k: dict(Counter(g for _, g in v)) for k, v in t.items()},
                   ur3={k: len(v) for k, v in u.items()}))
    elif mode == "kill":
        with Pool(4, initializer=init_kill) as P:
            res = P.map(kill_draw, range(KILL_DRAWS), chunksize=2)
        power = float(np.mean([r["passed"] for r in res]))
        out = dict(power=power, passed=bool(power >= 0.8), mean_T=float(np.mean([r["T"] for r in res])),
                   mean_null1=float(np.mean([r["null1_mean"] for r in res])), mean_bigram=float(np.mean([r["bigram_mean"] for r in res])),
                   share_p1=float(np.mean([r["p_site_perm"] <= 0.01 for r in res])),
                   share_bigram=float(np.mean([r["T"] > r["bigram_p99"] for r in res])), draws=res)
        print(json.dumps({k: v for k, v in out.items() if k != "draws"}, indent=1))
        json.dump(out, open(HERE / "kill.json", "w"), indent=1)
    elif mode == "full":
        assert json.load(open(HERE / "kill.json"))["passed"], "kill test stopped the study"
        with Pool(4, initializer=init_full) as P:
            pl = P.map(plant_draw, [(dl, d) for dl in DELTAS for d in range(PLANT_DRAWS)], chunksize=2)
        gate = {dl: float(np.mean([r["passed"] for r in pl if r["delta"] == dl])) for dl in DELTAS}
        ok = [dl for dl in DELTAS if gate[dl] >= 0.8]; cstar = min(ok) if ok else None
        out = dict(gate=gate, c_star=cstar)
        print(json.dumps(out, indent=1), flush=True)
        if cstar is None or cstar > 0.10:
            out["verdict"] = "untestable (planted gate c* > 0.10)"
        else:
            init_full(); rng = np.random.default_rng(SEED + 1)
            real = evaluate(I["seals"], I["targ"], rng, N1_REAL, N2_REAL, form=I["form"])
            out.update(real=real, by_group=by_group(),
                       verdict="quoting found" if real["passed"] else f"powered negative: no quoting above {cstar:.2f} of tablet/pot texts")
        out["plants"] = pl
        print(json.dumps({k: v for k, v in out.items() if k != "plants"}, indent=1))
        json.dump(out, open(HERE / "full.json", "w"), indent=1)
