"""Do tablets carry counted numerals more than seals? (prereg docs/prereg/numerals_by_object.md)
Run: .venv/bin/python -I experiments/numerals_by_object/run.py kill   # Latin known answer at Indus sizes
     .venv/bin/python -I experiments/numerals_by_object/run.py full   # planted Indus gate, then the real statistic
"""
import glob, json, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/count_index_rehearsal")); sys.path.insert(0, str(ROOT / "corpus"))
import cir          # noqa: E402  (index: rarefied distinct values in 4 tokens, heads >= 8 tokens; Latin pair rule)
import load as L    # noqa: E402

SEED = 20261129
NPERM_DRAW, NPERM_REAL = 300, 2000
KILL_DRAWS, PLANT_DRAWS = 200, 40
DELTAS = (0.25, 0.5, 1.0, 1.5)
SITES = ("Harappa", "Mohenjodaro")
TABLET = {"Harappa": "miniature tablet", "Mohenjodaro": "copper tablet"}


# ------------------------------------------------------------------ shared statistic
def index_table(pairs):
    vals = defaultdict(list)
    for p in pairs:
        vals[p["head"]].append(p["value"])
    return {h: cir.rarefied_distinct(v) for h, v in vals.items() if len(v) >= cir.NMIN}


class Stat:
    """tokens: list of (index, stratum, text_id); lab: {text_id: 1 tablet / 0 seal}. D = token-weighted mean over strata of
    (mean index on tablet tokens - mean index on seal tokens), strata weighted by tablet tokens."""
    def __init__(self, tokens):
        self.x = np.array([t[0] for t in tokens], float); self.s = np.array([t[1] for t in tokens]); self.t = np.array([t[2] for t in tokens])
        self.texts = {k: list(dict.fromkeys(self.t[self.s == k])) for k in sorted(set(self.s))}

    def D(self, lab):
        y = np.array([lab[t] for t in self.t]); per = {}; w = {}
        for k in self.texts:
            m = self.s == k; a = self.x[m & (y == 1)]; b = self.x[m & (y == 0)]
            if len(a) and len(b):
                per[k] = float(a.mean() - b.mean()); w[k] = len(a)
        if not per:
            return 0.0, per
        return sum(per[k] * w[k] for k in per) / sum(w.values()), per

    def perm(self, lab, rng):
        out = dict(lab)
        for k, ts in self.texts.items():
            v = [lab[t] for t in ts]; out.update(zip(ts, rng.permutation(v)))
        return out

    def test(self, lab, rng, n):
        obs, per = self.D(lab)
        null = np.array([self.D(self.perm(lab, rng))[0] for _ in range(n)])
        p = float((1 + (null >= obs).sum()) / (n + 1))
        return dict(D=obs, per_stratum=per, p=p, null_mean=float(null.mean()), null_p99=float(np.quantile(null, .99)),
                    passed=bool(p <= 0.01 and len(per) == 2 and all(v > 0 for v in per.values())))


# ------------------------------------------------------------------ Indus
def indus_pairs():
    """Distinct M77 texts at Harappa (seals, miniature tablets) and Mohenjo-daro (seals, copper tablets); numeral directly
    before a non-numeral head inside a break-free run (count_index_rehearsal rule; M99, M101 not numerals)."""
    short, tall = cir.indus_tables(); isnum = lambda s: s in short or s in tall
    out = []
    for ti, x in enumerate(L.distinct(L.m77_texts())):
        if x["site"] not in SITES or x["object_type"] not in ("seal", TABLET[x["site"]]):
            continue
        for r in L.runs(x["seq"]):
            for i, s in enumerate(r):
                if isnum(s) and i + 1 < len(r) and not isnum(r[i + 1]):
                    sy = "short" if s in short else "tall"
                    out.append(dict(head=(sy, r[i + 1]), value=(short if sy == "short" else tall)[s], text=ti, site=x["site"],
                                    tab=int(x["object_type"] != "seal")))
    return out


def indus_setup():
    pairs = indus_pairs(); idx = index_table(pairs)
    tok = [(idx[p["head"]], p["site"], p["text"]) for p in pairs if p["head"] in idx]
    lab = {p["text"]: p["tab"] for p in pairs}
    return pairs, idx, tok, lab


def plant(tok, lab, delta, rng):
    """Label swap within site (texts never edited): swap tablet/seal labels between a tablet text with a low mean index and a
    seal text with a higher mean index (similar token count) until the tablet mean index is natural + delta. None if infeasible."""
    lab = dict(lab); st = Stat(tok)
    mean_t = defaultdict(list); ntok = Counter()
    for x, s, t in tok:
        mean_t[t].append(x); ntok[t] += 1
    mt = {t: float(np.mean(v)) for t, v in mean_t.items()}
    for k in SITES:
        def tmean():
            a = [x for x, s, t in tok if s == k and lab[t] == 1]
            return float(np.mean(a)) if a else None
        start = tmean()
        if start is None:
            return None
        goal = start + delta; tries = 0
        while tmean() < goal and tries < 400:
            tries += 1
            tabs = [t for t in st.texts[k] if lab[t] == 1]; seals = [t for t in st.texts[k] if lab[t] == 0]
            a = tabs[rng.integers(len(tabs))]; cand = [t for t in seals if mt[t] > mt[a] and abs(ntok[t] - ntok[a]) <= 1]
            if not cand:
                continue
            b = cand[rng.integers(len(cand))]; lab[a], lab[b] = 0, 1
        if tmean() < goal:
            return None
    return lab


G = {}


def init_full():
    G["pairs"], G["idx"], G["tok"], G["lab"] = indus_setup()


def plant_draw(args):
    delta, d = args
    rng = np.random.default_rng(SEED + int(delta * 100) * 1000 + d)
    lab = plant(G["tok"], G["lab"], delta, rng)
    if lab is None:
        return dict(delta=delta, d=d, feasible=False, passed=False)
    r = Stat(G["tok"]).test(lab, rng, NPERM_DRAW); r.update(delta=delta, d=d, feasible=True)
    return r


# ------------------------------------------------------------------ Latin known answer
def latin_pairs():
    ty = {}
    for f in sorted(glob.glob(str(ROOT / "experiments/short_labels/raw/edh/p*.json"))):
        for it in json.load(open(f))["items"]:
            ty[it["id"]] = (it.get("type_of_inscription") or "").rstrip("?")
    pairs = cir.edh_pairs(cir.greedy_fast(cir.edh_texts()))
    A = [p for p in pairs if ty.get(p["text"]) == "epitaph"]
    B = [p for p in pairs if ty.get(p["text"]) in ("honorific inscription", "building/dedicatory inscription", "military diploma")]
    return A, B


def take(P, n, rng):
    byt = defaultdict(list)
    for p in P:
        byt[p["text"]].append(p)
    ks = list(byt); rng.shuffle(ks); out = []
    for k in ks:
        out += byt[k]
        if len(out) >= n:
            break
    return out


def kill_draw(d):
    rng = np.random.default_rng(SEED + d); pairs = []; lab = {}
    for k in SITES:
        nt, ns = G["sizes"][k]
        a = take(G["A"], nt, rng); b = take(G["B"], ns, rng)
        for p, l in [(p, 1) for p in a] + [(p, 0) for p in b]:
            key = f"{k}|{p['text']}"; pairs.append(dict(head=p["head"], value=p["value"], text=key, site=k)); lab[key] = l
    idx = index_table(pairs)
    tok = [(idx[p["head"]], p["site"], p["text"]) for p in pairs if p["head"] in idx]
    r = Stat(tok).test(lab, rng, NPERM_DRAW); r["d"] = d
    return r


def init_kill():
    G["A"], G["B"] = latin_pairs()
    pairs = indus_pairs()
    G["sizes"] = {k: (sum(1 for p in pairs if p["site"] == k and p["tab"] == 1), sum(1 for p in pairs if p["site"] == k and p["tab"] == 0)) for k in SITES}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    if mode == "kill":
        init_kill(); print("Indus token counts (tablet, seal) per site:", G["sizes"], flush=True)
        with Pool(4, initializer=init_kill) as P:
            res = P.map(kill_draw, range(KILL_DRAWS), chunksize=4)
        power = float(np.mean([r["passed"] for r in res]))
        out = dict(power=power, passed=bool(power >= 0.8), sizes=G["sizes"], mean_D=float(np.mean([r["D"] for r in res])), draws=res)
        print(json.dumps({k: v for k, v in out.items() if k != "draws"}, indent=1))
        json.dump(out, open(HERE / "kill.json", "w"), indent=1, default=str)
    elif mode == "full":
        kj = json.load(open(HERE / "kill.json")); assert kj["passed"], "kill test stopped the study"
        with Pool(4, initializer=init_full) as P:
            pl = P.map(plant_draw, [(dl, d) for dl in DELTAS for d in range(PLANT_DRAWS)], chunksize=2)
        gate = {}
        for dl in DELTAS:
            f = [r for r in pl if r["delta"] == dl and r["feasible"]]
            gate[dl] = dict(feasible=len(f), power=float(np.mean([r["passed"] for r in f])) if f else None)
        ok = [dl for dl in DELTAS if gate[dl]["power"] is not None and gate[dl]["feasible"] >= 20 and gate[dl]["power"] >= 0.8]
        cstar = min(ok) if ok else None
        out = dict(gate=gate, c_star=cstar, latin_mean_D=kj["mean_D"])
        print(json.dumps(out, indent=1), flush=True)
        if cstar is None or cstar > 1.0:
            out["verdict"] = "untestable (planted gate c* > 1.0 index units)"
        else:
            init_full(); rng = np.random.default_rng(SEED + 1)
            real = Stat(G["tok"]).test(G["lab"], rng, NPERM_REAL)
            heads = Counter((p["site"], p["tab"], p["head"][1]) for p in G["pairs"] if p["head"] in G["idx"])
            out.update(real=real, n_tokens={f"{k}:{t}": sum(v for (s, tt, _), v in heads.items() if s == k and tt == t) for k in SITES for t in (0, 1)},
                       verdict="tablets carry more counted numerals than seals" if real["passed"]
                       else f"powered negative: no tablet-seal gap of {cstar} index units or more")
        out["plants"] = pl
        print(json.dumps({k: v for k, v in out.items() if k != "plants"}, indent=1, default=str))
        json.dump(out, open(HERE / "full.json", "w"), indent=1, default=str)
