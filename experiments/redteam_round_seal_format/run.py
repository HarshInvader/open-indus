"""Red team of #39 round-seal format (board #41). Prereg: docs/prereg/redteam_round_seal_format.md
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/redteam_round_seal_format/run.py
Own code; reuses only the shared KN class (context/q4_gulf.py) and glib.PositionModel / glib.NUM.
"""
import sys, json, csv, itertools, time, math, re
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT / "experiments/grammar"), str(ROOT)]
import q4_gulf as Q  # noqa
import glib  # noqa
from corpus.load import icit_texts  # noqa

T0 = time.time()
log = lambda *a: print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)
rng = np.random.default_rng(41)
NDRAW = 10000
ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
NUM = set(glib.NUM["ICIT"])
SC = list(csv.DictReader(open(ROOT / "experiments/grammar/sign_classes.csv")))


def wset(lab, buggy=False):
    out = set()
    for r in SC:
        if r["final_class"] != lab: continue
        toks = r["wells_signs"].split() if buggy else re.split(r"[;\s]+", r["wells_signs"])
        out |= {w for w in toks if w.startswith("W")}
    return out


OPEN_B, CLOSE_B = wset("opener", True), wset("closer", True)
OPEN, CLOSE = wset("opener"), wset("closer")
GW = json.load(open(ROOT / "experiments/grammar/classes_wells.json"))
WLAB = {w: v["label"] for w, v in GW["signs"].items()}
CLOSE_GR = {w for w, l in WLAB.items() if l == "closer"}
R = dict(open_buggy=sorted(OPEN_B), open=sorted(OPEN), close_buggy=sorted(CLOSE_B), close=sorted(CLOSE), close_gr_n=len(CLOSE_GR))
log(R)

FC = pd.read_csv(ROOT / "experiments/foreign_corpus/foreign_corpus.csv")
FCI = {str(r["icit_id"]): r for _, r in FC.iterrows() if pd.notna(r["icit_id"])}
REG_CONFIRMED = {"2911.1", "2912.1", "2977.1"}
ALT = {"148.1": "REV", "3863.1": "REV", "3882.1": "REV",
       "3887.1": "W235 W090 W090 W615 W615", "3898.1": "W415 W803 W001 W717 W005",
       "5222.1": "W255 W013 W745 W892 W740"}


def mk(raw_seq, **kw):
    raw = [s for s in raw_seq if s != "|"]
    sg = [s for s in raw if s.startswith("W")]
    return dict(seq=sg, L=len(sg), first_ok=bool(raw) and raw[0] != "#", last_ok=bool(raw) and raw[-1] != "#", raw=raw, **kw)


# ---------------- units (replicating #39, plus the dedup-dropped round texts) ----------------
seen, units, dropped = set(), [], []
for t in icit_texts():
    site, tp = t["site"], t["type"]
    if not tp.startswith("SEAL") or t["id"] in NOT_SEALS: continue
    grp = "abroad" if site in glib.FOREIGN else "unprov" if site == "Unknown" else "home"
    u = mk(t["seq"], id=t["id"], site=site, grp=grp, type=tp, round=tp in ROUND,
           complete=bool(t["complete"]) and "#" not in t["seq"], w=t.get("width_mm"), h=t.get("height_mm"))
    if u["L"] == 0: continue
    k = (grp, " ".join(u["seq"]))
    if k in seen:
        if u["round"]: dropped.append(u)
        continue
    seen.add(k); units.append(u)
rkeys = {" ".join(u["seq"]) for u in units if u["round"]}
rnd = [u for u in units if u["round"]]
sq = [u for u in units if not u["round"] and u["grp"] == "home" and " ".join(u["seq"]) not in rkeys]
fsq = [u for u in units if not u["round"] and u["grp"] == "abroad"]
R["n"] = dict(round=len(rnd), square=len(sq), square_abroad=len(fsq), dedup_dropped_round=[u["id"] for u in dropped])
log(R["n"])

# alternative readings
def alt_unit(u):
    a = ALT.get(u["id"])
    if a is None: return dict(u)
    v = dict(u)
    raw = list(reversed(u["raw"])) if a == "REV" else a.split()
    v.update(mk(raw, **{k: u[k] for k in ("id", "site", "grp", "type", "round", "complete", "w", "h")}))
    v["alt"] = True
    return v
rnd_alt = [alt_unit(u) for u in rnd]


def shape_info(u):
    fc = FCI.get(u["id"])
    return dict(id=u["id"], site=u["site"], grp=u["grp"], icit_type=u["type"], dims=f"{u['w']}x{u['h']}",
                fc_shape=None if fc is None else fc["shape"], fc_conf=None if fc is None else fc["reading_confidence"],
                register_confirmed=u["id"] in REG_CONFIRMED, seq=" ".join(u["seq"]))
R["shape_table"] = [shape_info(u) for u in rnd + dropped]


def is_cyl(u):
    fc = FCI.get(u["id"])
    return u["type"] == "SEAL:CY" or (fc is not None and "cylinder" in str(fc["shape"]))


def is_gulf_or_reg(u):
    fc = FCI.get(u["id"])
    if u["grp"] == "home": return u["id"] in REG_CONFIRMED
    return fc is not None and ("round Gulf" in str(fc["shape"]) or "Dilmun" in str(fc["shape"]))


def confirmed_or_home(u):
    if u["grp"] == "home": return True
    fc = FCI.get(u["id"])
    return fc is not None and fc["reading_confidence"] == "confirmed"


# ---------------- A: closer tests ----------------
def strata(pool, keyf):
    d = defaultdict(list)
    for i, u in enumerate(pool): d[keyf(u)].append(i)
    return d


def share_test(sel, pool, featf, condf, direction=-1, ndraw=NDRAW, two_sided=False):
    sel = [u for u in sel if condf(u)]; pool = [u for u in pool if condf(u)]
    if not sel: return dict(n=0)
    vals = np.array([float(featf(u)) for u in pool])
    by_sl = strata(pool, lambda u: (u["site"], min(u["L"], 7))); by_l = strata(pool, lambda u: min(u["L"], 7))
    idx = []
    for u in sel:
        c = by_sl.get((u["site"], min(u["L"], 7)), []) if u["grp"] == "home" else []
        if len(c) < 5:
            L = min(u["L"], 7)
            while len(by_l.get(L, [])) < 5 and L > 1: L -= 1
            c = by_l[L]
        idx.append(np.array(c))
    draws = np.stack([vals[c[rng.integers(len(c), size=ndraw)]] for c in idx]).mean(0)
    obs = float(np.mean([featf(u) for u in sel]))
    lo = (1 + (draws <= obs).sum()) / (ndraw + 1); hi = (1 + (draws >= obs).sum()) / (ndraw + 1)
    p = min(1.0, 2 * min(lo, hi)) if two_sided else (lo if direction < 0 else hi)
    return dict(n=len(sel), k=int(sum(featf(u) for u in sel)), obs=obs, null=float(draws.mean()), p=float(p))


lastok = lambda u: u["last_ok"]
endsin = lambda S: (lambda u: u["last_ok"] and bool(u["seq"]) and u["seq"][-1] in S)
# A4 data-driven closers from complete home squares
fin, tot = Counter(), Counter()
for u in sq:
    if not u["complete"] or u["L"] < 2: continue
    for i, s in enumerate(u["seq"]):
        tot[s] += 1
        if i == u["L"] - 1: fin[s] += 1
CLOSE_DD = {s for s in tot if tot[s] >= 10 and fin[s] / tot[s] >= 0.6}
R["close_datadriven"] = sorted(CLOSE_DD)
A = {}
A["A0_buggy_sets"] = share_test(rnd, sq, endsin(CLOSE_B), lastok)
A["A1_corrected"] = share_test(rnd, sq, endsin(CLOSE), lastok)
A["A2_W740_only"] = share_test(rnd, sq, endsin({"W740"}), lastok)
A["A3_wells_class_closer"] = share_test(rnd, sq, endsin(CLOSE_GR), lastok)
A["A4_datadriven_closer"] = share_test(rnd, sq, endsin(CLOSE_DD), lastok)
A["A5_complete_only"] = share_test(rnd, sq, endsin(CLOSE), lambda u: u["last_ok"] and u["complete"])
A["A6_keep_dedup_dropped"] = share_test(rnd + dropped, sq, endsin(CLOSE), lastok)
A["A7_no_cylinders"] = share_test([u for u in rnd if not is_cyl(u)], sq, endsin(CLOSE), lastok)
A["A7b_gulf_type_plus_register_round"] = share_test([u for u in rnd if is_gulf_or_reg(u)], sq, endsin(CLOSE), lastok)
A["A8_confirmed_readings_only"] = share_test([u for u in rnd if confirmed_or_home(u)], sq, endsin(CLOSE), lastok)
A["A9_alternative_readings"] = share_test(rnd_alt, sq, endsin(CLOSE), lastok)
A["A9b_alt_readings_W740_only"] = share_test(rnd_alt, sq, endsin({"W740"}), lastok)
A1set = [u for u in rnd if u["last_ok"]]
loo = []
for i, u in enumerate(A1set):
    r = share_test(A1set[:i] + A1set[i + 1:], sq, endsin(CLOSE), lastok, ndraw=4000)
    loo.append(dict(drop=u["id"], p=r["p"], obs=r["obs"]))
A["A10_LOO"] = dict(max_p=max(x["p"] for x in loo), worst=max(loo, key=lambda x: x["p"]), all=loo)
A["A11_closer_first_two_sided"] = share_test(rnd, sq, lambda u: u["first_ok"] and bool(u["seq"]) and u["seq"][0] in CLOSE,
                                              lambda u: u["first_ok"], two_sided=True)
A["A11b_closer_first_alt_readings"] = share_test(rnd_alt, sq, lambda u: u["first_ok"] and bool(u["seq"]) and u["seq"][0] in CLOSE,
                                                  lambda u: u["first_ok"], two_sided=True)
A["closer_last_round_ids"] = [u["id"] for u in rnd if endsin(CLOSE)(u)]
R["A"] = A
a1 = A["A1_corrected"]["p"] < 0.0125
sens = [A[k]["p"] < 0.05 and A[k]["obs"] < A[k]["null"] for k in
        ("A2_W740_only", "A3_wells_class_closer", "A4_datadriven_closer", "A5_complete_only", "A6_keep_dedup_dropped",
         "A7_no_cylinders", "A7b_gulf_type_plus_register_round", "A8_confirmed_readings_only", "A9_alternative_readings")]
R["verdict_C1"] = ("BROKEN" if (not a1 or sum(not s for s in sens) > len(sens) / 2) else
                   "SURVIVES" if (all(sens) and A["A10_LOO"]["max_p"] < 0.05) else "WEAKENED")
log("A", json.dumps({k: v for k, v in A.items() if k not in ("A10_LOO",)}, default=str))
log("A10 max p", A["A10_LOO"]["max_p"], A["A10_LOO"]["worst"], "C1:", R["verdict_C1"])

# ---------------- B: order models ----------------
home_all, seen2 = [], set()
for t in icit_texts():
    s = [x for x in Q.clean(t["seq"]) if x.startswith("W")]
    if not s or t["site"] in glib.FOREIGN or t["site"] == "Unknown": continue
    k = " ".join(s)
    if k in seen2: continue
    seen2.add(k); home_all.append(s)
hidx = {" ".join(s): i for i, s in enumerate(home_all)}
N = len(home_all); perm_i = rng.permutation(N); fold = np.zeros(N, int)
for f in range(10): fold[perm_i[f::10]] = f
GCLS = dict(zip(GW["words"], GW["cls"])); K = GW["K"]


class GR:
    def __init__(self, texts, a=0.5):
        c = Counter(s for t in texts for s in t)
        self.V = {s for s, n in c.items() if n >= 2 and s in GCLS}
        tr = np.full((K + 1, K + 1), a); em = defaultdict(Counter)
        for t in texts:
            cs = [self.cl(s) for s in t]
            for s, cc in zip(t, cs): em[cc][self.m(s)] += 1
            seq = [K] + cs + [K]
            for x, y in zip(seq, seq[1:]): tr[x, y] += 1
        self.T = tr / tr.sum(1, keepdims=True)
        self.em = {}
        for cc in range(K):
            n = sum(em[cc].values()); vc = sum(1 for w in self.V if GCLS[w] == cc) + 1
            self.em[cc] = (em[cc], n, vc)

    def m(self, s): return s if s in self.V else "<UNK>"
    def cl(self, s): return GCLS[s] if s in self.V else GCLS["<UNK>"]

    def bits(self, t):
        cs = [self.cl(s) for s in t]; lp = 0.0
        for s, cc in zip(t, cs):
            e, n, vc = self.em[cc]; lp += math.log2((e[self.m(s)] + 0.5) / (n + 0.5 * vc))
        seq = [K] + cs + [K]
        for x, y in zip(seq, seq[1:]): lp += math.log2(self.T[x, y])
        return -lp / (len(t) + 1)


class POS:
    def __init__(self, texts):
        self.m = glib.PositionModel(cap=4).fit([dict(runs=[(tuple(t), True, True)]) for t in texts])

    def bits(self, t):
        lp, n = self.m.run_logp(tuple(t), True, True)
        return -lp / n


MODELS = {}
for name, cls in (("KN", Q.KN), ("GR", GR), ("POS", POS)):
    MODELS[name] = ([cls([home_all[i] for i in range(N) if fold[i] != f]) for f in range(10)], cls(home_all))
log("models fitted", N)
FULLV = MODELS["KN"][1].V


def perms(seq, k=200):
    if len(seq) <= 5:
        ps = set(itertools.permutations(seq)); ps.discard(tuple(seq)); ps = [list(p) for p in ps]
        return ps if len(ps) <= k else [ps[i] for i in rng.choice(len(ps), k, replace=False)]
    out = []
    for _ in range(k):
        p = list(rng.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def score(u):
    s = u["seq"]; ps = perms(s) if len(s) >= 2 else []
    k = " ".join(s)
    for name, (folds, full) in MODELS.items():
        M = folds[fold[hidx[k]]] if (u["grp"] == "home" and k in hidx) else full
        u["d_" + name] = (M.bits(s) - float(np.mean([M.bits(p) for p in ps]))) if ps else np.nan


for grp in (rnd, rnd_alt, dropped, sq, fsq):
    for u in grp:
        if grp is rnd_alt and not u.get("alt"): continue
        score(u)
for u in rnd_alt:
    if not u.get("alt"):
        o = next(v for v in rnd if v["id"] == u["id"])
        for m in MODELS: u["d_" + m] = o["d_" + m]
log("scored")

# format features
for u in units + rnd_alt + dropped:
    s = u["seq"]
    u["num1"] = u["first_ok"] and bool(s) and s[0] in NUM
    u["op1"] = u["first_ok"] and bool(s) and s[0] in OPEN
    u["clL"] = u["last_ok"] and bool(s) and s[-1] in CLOSE
    u["op1b"] = u["first_ok"] and bool(s) and s[0] in OPEN_B
    u["clLb"] = u["last_ok"] and bool(s) and s[-1] in CLOSE_B
    u["w9091"] = any(x in ("W090", "W091") for x in s)
    u["numany"] = any(x in NUM for x in s)
    u["clfree"] = not any(x in CLOSE for x in s)
    u["fcl"] = WLAB.get(s[0], "unk") if (s and u["first_ok"]) else "broken"
    u["lcl"] = WLAB.get(s[-1], "unk") if (s and u["last_ok"]) else "broken"
    u["rare"] = min(sum(x not in FULLV for x in s), 2)
    u["roundlike"] = (not u["op1"], u["clfree"], u["w9091"] or u["numany"])

DEFS = {
    "F0b_39_buggy_sets": lambda u: (u["num1"], u["op1b"], u["clLb"]),
    "F0_39_key_corrected": lambda u: (u["num1"], u["op1"], u["clL"]),
    "F1_W090_W091_present": lambda u: (u["w9091"],),
    "F2_numeral_anywhere": lambda u: (u["numany"],),
    "F3_closer_free": lambda u: (u["clfree"],),
    "F4_first_last_class": lambda u: (u["fcl"], u["lcl"]),
    "F5_F0_plus_rare_load": lambda u: (u["num1"], u["op1"], u["clL"], u["rare"]),
    "F6_roundlike_composite": lambda u: u["roundlike"],
}


def levels(u, fdef):
    f = fdef(u) if fdef else ()
    L = min(u["L"], 9)
    return [(L,) + tuple(f[:j]) for j in range(len(f), -1, -1)]


class Matcher:
    def __init__(self, model, fdef):
        self.pool = [u for u in sq if not np.isnan(u["d_" + model])]
        self.vals = np.array([u["d_" + model] for u in self.pool])
        self.fdef = fdef
        self.tab = defaultdict(list)
        for i, u in enumerate(self.pool):
            for k in levels(u, fdef): self.tab[k].append(i)

    def stratum(self, u):
        for j, k in enumerate(levels(u, self.fdef)):
            if len(self.tab.get(k, [])) >= 5: return np.array(self.tab[k]), j
        L = min(u["L"], 9)
        while len(self.tab.get((L,), [])) < 5 and L > 2: L -= 1
        return np.array(self.tab[(L,)]), 99


def excess(sel, model, fdef, ndraw=NDRAW, vals=None):
    sel = [u for u in sel if not np.isnan(u["d_" + model])]
    M = Matcher(model, fdef); st = [M.stratum(u) for u in sel]
    v = np.array([u["d_" + model] for u in sel]) if vals is None else vals
    nm = np.array([M.vals[c].mean() for c, _ in st])
    draws = np.stack([M.vals[c[rng.integers(len(c), size=ndraw)]] for c, _ in st]).mean(0) if ndraw else None
    out = dict(n=len(sel), mean_d=float(v.mean()), excess=float(v.mean() - nm.mean()),
               fallback=int(sum(j > 0 for _, j in st)) if fdef else 0)
    if ndraw: out["p"] = float((1 + (draws >= v.mean()).sum()) / (ndraw + 1))
    return out, v, nm, st, M


def frac(sel, model, fdef, boot=2000, ndraw=NDRAW):
    eF, v, nmF, stF, MF = excess(sel, model, fdef, ndraw)
    eL, _, nmL, _, _ = excess(sel, model, None, ndraw)
    fr = 1 - eF["excess"] / eL["excess"] if eL["excess"] > 0 else None
    bs = []
    for _ in range(boot):
        b = rng.integers(len(v), size=len(v)); el = (v[b] - nmL[b]).mean()
        if el > 0: bs.append(1 - (v[b] - nmF[b]).mean() / el)
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None
    return dict(E_L=eL["excess"], p_L=eL.get("p"), E_F=eF["excess"], p_F=eF.get("p"), frac=fr, ci=ci,
                fallback=eF["fallback"], n=eF["n"]), (v, nmF, nmL, stF, MF)


B, cache = {}, {}
for model in MODELS:
    for dn, fd in DEFS.items():
        B[f"{model}|{dn}"], cache[(model, dn)] = frac(rnd, model, fd)
        log(model, dn, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in B[f"{model}|{dn}"].items()})
R["B"] = B

# planted: pseudo-round sets with round set's stratum composition (expected-value form, no draws)
PL = {}
for model in MODELS:
    for dn, fd in DEFS.items():
        v, nmF, nmL, stF, MF = cache[(model, dn)]
        ML = Matcher(model, None)
        eLs, frs = [], []
        for rep in range(200):
            picks = [MF.pool[c[rng.integers(len(c))]] for c, _ in stF]
            pv = np.array([u["d_" + model] for u in picks])
            pnL = np.array([ML.vals[ML.stratum(u)[0]].mean() for u in picks])
            pnF = np.array([MF.vals[MF.stratum(u)[0]].mean() for u in picks])
            el = (pv - pnL).mean(); eLs.append(el)
            if abs(el) > 1e-9: frs.append(1 - (pv - pnF).mean() / el)
        PL[f"{model}|{dn}"] = dict(format_only_E_L=float(np.mean(eLs)), E_L_ci=[float(np.percentile(eLs, 2.5)), float(np.percentile(eLs, 97.5))],
                                   frac_explained_median=float(np.median(frs)) if frs else None)
R["B_planted"] = PL
log("planted", json.dumps(PL)[:2000])

# LOO, subsets, alt readings (KN, F0 corrected)
F0 = DEFS["F0_39_key_corrected"]
scorable = [u for u in rnd if not np.isnan(u["d_KN"])]
loo = []
for i, u in enumerate(scorable):
    r, _ = frac(scorable[:i] + scorable[i + 1:], "KN", F0, boot=0, ndraw=0)
    loo.append(dict(drop=u["id"], frac=r["frac"], E_F=r["E_F"]))
fr_ = [x["frac"] for x in loo]
R["B_LOO_KN_F0"] = dict(min=min(fr_), max=max(fr_), at_max=max(loo, key=lambda x: x["frac"]), all=loo)
R["B_subsets_KN_F0"] = {name: frac(sel, "KN", F0, boot=1000)[0] for name, sel in (
    ("confirmed_readings_only", [u for u in rnd if confirmed_or_home(u)]),
    ("alternative_readings", rnd_alt),
    ("no_cylinders", [u for u in rnd if not is_cyl(u)]),
    ("gulf_type_plus_register_round", [u for u in rnd if is_gulf_or_reg(u)]),
    ("plus_dedup_dropped", rnd + dropped))}
for model in ("GR", "POS"):
    R["B_subsets_KN_F0"][f"alternative_readings_{model}"] = frac(rnd_alt, model, F0, boot=1000)[0]
log("LOO", R["B_LOO_KN_F0"]["min"], R["B_LOO_KN_F0"]["max"], R["B_LOO_KN_F0"]["at_max"])
log("subsets", json.dumps(R["B_subsets_KN_F0"]))

cells = {k: v for k, v in B.items() if "F0b" not in k}
bad = [k for k, v in cells.items() if not (v["frac"] is not None and v["frac"] < 0.5 and v["p_F"] < 0.05)]
broken_defs = [dn for dn in DEFS if dn != "F0b_39_buggy_sets" and
               sum(1 for m in MODELS if (B[f"{m}|{dn}"]["frac"] or 0) >= 0.5 and B[f"{m}|{dn}"]["p_F"] >= 0.05) >= 2]
R["verdict_C2"] = dict(verdict="SURVIVES" if not bad else ("BROKEN" if broken_defs else "WEAKENED"),
                       failing_cells=bad, broken_defs=broken_defs)
log("C2", R["verdict_C2"])

# ---------------- C: find-spot power ----------------
fs = [u for u in fsq if not np.isnan(u["d_KN"])]
ML = Matcher("KN", None); stf = [ML.stratum(u)[0] for u in fs]
O2 = excess(fs, "KN", None)[0]
pw = {}
for shift in (0.5, 1.0):
    hits = 0
    for rep in range(1000):
        picks = np.array([ML.vals[c[rng.integers(len(c))]] for c in stf]) + shift
        draws = np.stack([ML.vals[c[rng.integers(len(c), size=2000)]] for c in stf]).mean(0)
        hits += (1 + (draws >= picks.mean()).sum()) / 2001 < 0.05
    pw[f"+{shift}"] = hits / 1000
R["C_findspot"] = dict(O2_replication=O2, n=len(fs), power=pw)
log("C", R["C_findspot"])

R["round_texts"] = [dict(id=u["id"], grp=u["grp"], seq=" ".join(u["seq"]), clL=u["clL"],
                         **{m: (None if np.isnan(u["d_" + m]) else round(float(u["d_" + m]), 3)) for m in MODELS}) for u in rnd]
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("done")
