"""Forward predictions F1-F5 (board #44). Prereg: docs/prereg/forward_predictions.md

    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/forward_predictions/fp.py --mode dryrun
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/forward_predictions/fp.py --mode forward

dryrun : train on every non-Kalibangan text (ICIT for F1-F4, M77 for F5), score Kalibangan.
forward: train on all current M77 texts, score scorable rows of experiments/new_finds/new_texts.csv.
Single process, no pool.
"""
import sys, json, csv, re, math, argparse
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import binom, poisson

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts, runs  # noqa

HELD = {"ICIT": "Kalibangan", "M77": "Kalibangan"}
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Failaka", "Karzakan", "Qala'at al-Bahrain", "Luristan", "Hajar",
           "Salut", "Ra's al-Junayz", "Tello", "Girsu", "Tepe Yahya", "Saar", "Janabiyah", "Tell Umma", "Dilmun",
           "Kalba", "Gonur", "Gonur Depe", "Altyn Depe", "Shortughai", "West Asian finds"}
SC = list(csv.DictReader(open(ROOT / "experiments/grammar/sign_classes.csv")))
CLOSE = {"M": {r["sign"] for r in SC if r["final_class"] == "closer"},
         "W": {w for r in SC if r["final_class"] == "closer" for w in re.split(r"[;\s]+", r["wells_signs"]) if w.startswith("W")}}
JAR = {"M": "M342", "W": "W740"}
CUP = {"M": "M328", "W": "W700"}
TALL = {"M": {"M86": 1, "M87": 2, "M88": 3, "M89": 3, "M92": 3, "M93": 3, "M94": 3, "M95": 4, "M96": 5},
        "W": {f"W03{i}": i for i in range(1, 8)}}
FISH = {"M67", "M70", "M72"}
LAM = (0.5, 0.3, 0.15, 0.05)
rng = np.random.default_rng(44)
L2 = math.log2


def unit(seq, code, **kw):
    raw = [s for s in seq if s != "|"]
    sg = [s for s in raw if s.startswith(code)]
    return dict(seq=sg, raw=[s if s.startswith(code) or s == "#" else s for s in raw], L=len(sg),
                last_ok=bool(raw) and raw[-1] != "#", runs=[[s for s in r if s.startswith(code)] for r in runs(raw)], **kw)


def dedupe(us):
    seen, out = set(), []
    for u in us:
        k = (u["site"], u["kind"], " ".join(u["seq"]))
        if u["L"] == 0 or k in seen: continue
        seen.add(k); out.append(u)
    return out


# ---------------------------------------------------------------- data
def icit_units():
    out = []
    for t in icit_texts():
        tp = t["type"]
        kind = ("round" if tp in ("SEAL:C", "SEAL:CY") else "seal" if tp.startswith("SEAL") else
                "pot_g" if tp == "POT:T:g" else "pot_other" if tp.startswith("POT") else
                "tablet" if tp.startswith("TAB") else "other")
        out.append(unit(t["seq"], "W", site=t["site"], kind=kind, id=t["id"]))
    return dedupe(out)


def m77_units():
    out = []
    for t in m77_texts():
        ot = t["object_type"]
        kind = "seal" if ot == "seal" else "pot_g" if ot == "pottery graffito" else "tablet" if "tablet" in ot else "other"
        out.append(unit(t["seq"], "M", site=t["site"], kind=kind, id=t["text_no"]))
    return dedupe(out)


def new_units():
    out = []
    for r in csv.DictReader(open(ROOT / "experiments/new_finds/new_texts.csv")):
        if r["scored"].strip().lower() != "yes" or r["status"].strip().lower() != "new": continue
        seq = [s.rstrip("?") for s in r["seq_M"].split()]
        seq = [s if re.fullmatch(r"M\d+", s) else "#" for s in seq]
        ot = r["object_type"].lower()
        if "seal" in ot and "sealing" not in ot and any(w in ot for w in ("round", "circular", "button", "cylinder")):
            kind = "round"
        elif "seal" in ot and "sealing" not in ot: kind = "seal"
        elif "graffit" in ot and "painted" not in ot and "stamp" not in ot: kind = "pot_g"
        elif "tablet" in ot: kind = "tablet"
        else: kind = "other"
        out.append(unit(seq, "M", site=r["site"], kind=kind, id=r["obj_id"], vessel=r.get("vessel_form", "")))
    return dedupe(out)


def home(u):
    return u["site"] not in FOREIGN and u["site"] not in ("Unknown", "Other sites")


# ---------------------------------------------------------------- models
class Tri:
    def __init__(self, seqs):
        self.c3, self.c2, self.c1 = Counter(), Counter(), Counter()
        self.h2, self.h1 = Counter(), Counter()
        self.V = set()
        for s in seqs:
            x = ["<s>", "<s>"] + s + ["</s>"]
            self.V |= set(s)
            for i in range(2, len(x)):
                self.c3[(x[i - 2], x[i - 1], x[i])] += 1; self.h2[(x[i - 2], x[i - 1])] += 1
                self.c2[(x[i - 1], x[i])] += 1; self.h1[x[i - 1]] += 1
                self.c1[x[i]] += 1
        self.N = sum(self.c1.values()); self.nv = len(self.V) + 2

    def _upd(self, s, d):
        x = ["<s>", "<s>"] + s + ["</s>"]
        for i in range(2, len(x)):
            self.c3[(x[i - 2], x[i - 1], x[i])] += d; self.h2[(x[i - 2], x[i - 1])] += d
            self.c2[(x[i - 1], x[i])] += d; self.h1[x[i - 1]] += d; self.c1[x[i]] += d
        self.N += d * (len(s) + 1)

    def bits_loo(self, s):
        self._upd(s, -1)
        try: return self.bits(s)
        finally: self._upd(s, 1)

    def p(self, a, b, c):
        p3 = self.c3[(a, b, c)] / self.h2[(a, b)] if self.h2[(a, b)] else 0
        p2 = self.c2[(b, c)] / self.h1[b] if self.h1[b] else 0
        return LAM[0] * p3 + LAM[1] * p2 + LAM[2] * self.c1[c] / self.N + LAM[3] / self.nv

    def bits(self, s):
        s = [w if w in self.V else "<unk>" for w in s]
        x = ["<s>", "<s>"] + s + ["</s>"]
        return [-L2(self.p(x[i - 2], x[i - 1], x[i])) for i in range(2, len(x))]


def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def lsc(p, y):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return L2(p) if y else L2(1 - p)


# ---------------------------------------------------------------- F1
def f1(train, test, code):
    C = CLOSE[code]
    sq = [u for u in train if u["kind"] == "seal" and home(u) and u["L"] >= 2 and u["last_ok"]]
    p0 = sum(u["seq"][-1] in C for u in sq) / len(sq)
    seals = [u for u in train if u["kind"] in ("seal", "round") and u["L"] >= 2 and u["last_ok"]]
    g = sum(u["seq"][-1] in C for u in seals) / len(seals)
    ctx2, ctx1 = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for u in seals:
        y = u["seq"][-1] in C
        k2 = tuple(u["seq"][-3:-1]); k1 = u["seq"][-2]
        ctx2[k2][0] += y; ctx2[k2][1] += 1; ctx1[k1][0] += y; ctx1[k1][1] += 1

    def base(u):
        k2, k1 = tuple(u["seq"][-3:-1]), u["seq"][-2]
        for d in (ctx2.get(k2), ctx1.get(k1)):
            if d and d[1] >= 3: return (d[0] + 1) / (d[1] + 2)
        return g
    el = [u for u in test if u["kind"] == "round" and u["L"] >= 2 and u["last_ok"]]
    n = len(el); k = sum(u["seq"][-1] in C for u in el)
    R = dict(n=n, k=k, p0_square=round(p0, 4), min_n=8, evaluable=n >= 8)
    if n:
        share = k / n
        R.update(share=round(share, 4), wilson=[round(x, 3) for x in wilson(k, n)], p_binom=float(binom.cdf(k, n, p0)),
                 gain_bits_per_unit=round(np.mean([lsc(0.20, u["seq"][-1] in C) - lsc(base(u), u["seq"][-1] in C) for u in el]), 4))
        R["verdict"] = ("pass" if share <= 0.25 and R["p_binom"] < 0.05 else "fail" if share >= 0.40 else "neither") if n >= 8 else "not evaluable"
    else:
        R["verdict"] = "not evaluable"
    return R


# ---------------------------------------------------------------- F2
def f2(train, test, code):
    sq_tr = [u for u in train if u["kind"] == "seal" and home(u)]
    rd = [u for u in test if u["kind"] == "round"]
    sq_te = [u for u in test if u["kind"] == "seal" and home(u)]
    R = dict(n_round=len(rd), n_square=len(sq_te), min_n=8, evaluable=len(rd) >= 8)
    if not rd:
        R["verdict"] = "not evaluable"; return R
    M = Tri([r for u in sq_tr for r in u["runs"] if r])

    def bps(us):
        b = [x for u in us for r in u["runs"] if r for x in M.bits(r)]
        return np.mean(b) if b else float("nan")
    if len(sq_te) >= 8:
        ref = sq_te
        ex = bps(rd) - bps(ref)
        lab = rd + ref; per = [np.mean([x for r in u["runs"] if r for x in M.bits(r)]) for u in lab]
        nr = len(rd); obs = np.mean(per[:nr]) - np.mean(per[nr:]); cnt = 0
        for _ in range(2000):
            pi = rng.permutation(len(per)); a = np.array(per)[pi]
            cnt += (a[:nr].mean() - a[nr:].mean()) >= obs
        pperm = (cnt + 1) / 2001
    else:  # leave-one-out reference on training home squares
        b = [x for u in sq_tr for r in u["runs"] if r for x in M.bits_loo(r)]
        ex = bps(rd) - np.mean(b); pperm = float("nan")
    R.update(excess_bits_per_sign=round(float(ex), 4), p_perm=float(pperm), gain_vs_mid=round(float(ex) - 0.25, 4))
    R["verdict"] = ("pass" if ex >= 0.5 and pperm < 0.05 else "fail" if ex < 0 else "neither") if len(rd) >= 8 else "not evaluable"
    return R


# ---------------------------------------------------------------- F3
def f3(train, test, code):
    J = JAR[code]
    seal_tok = [s for u in train if u["kind"] in ("seal", "round") for s in u["seq"]]
    all_tok = [s for u in train for s in u["seq"]]
    fs, fa = seal_tok.count(J) / len(seal_tok), all_tok.count(J) / len(all_tok)
    el = [u for u in test if u["kind"] == "pot_g"]
    E = sum(1 - (1 - fs) ** u["L"] for u in el); obs = sum(J in u["seq"] for u in el)
    R = dict(n_texts=len(el), observed=obs, expected=round(E, 3), f_seal=round(fs, 5), f_all=round(fa, 5), min_E=8, evaluable=E >= 8)
    if el:
        rr = obs / E if E else float("nan")
        pp = float(poisson.cdf(obs, E))
        g = np.mean([lsc(0.6 * (1 - (1 - fs) ** u["L"]), J in u["seq"]) - lsc(1 - (1 - fa) ** u["L"], J in u["seq"]) for u in el])
        R.update(RR=round(rr, 4), p_poisson=pp, gain_bits_per_unit=round(float(g), 4))
        R["verdict"] = ("pass" if rr <= 0.70 and pp < 0.05 else "fail" if rr >= 1.0 else "neither") if E >= 8 else "not evaluable"
    else:
        R["verdict"] = "not evaluable"
    return R


# ---------------------------------------------------------------- F4
def f4(train, test, code):
    cup, T = CUP[code], TALL[code]
    vals = sorted(set(T.values()) | set(range(1, 8)))

    def pairs(us):
        cu, ot = [], []
        for u in us:
            for r in u["runs"]:
                for i in range(len(r) - 1):
                    if r[i] in T:
                        (cu if r[i + 1] == cup else ot).append(T[r[i]])
        return cu, ot
    cu_tr, ot_tr = pairs(train)
    lead = {v: (cu_tr.count(v) + 0.5) / (len(cu_tr) + 0.5 * len(vals)) for v in vals}
    base = {v: (ot_tr.count(v) + 0.5) / (len(ot_tr) + 0.5 * len(vals)) for v in vals}
    cu_te, _ = pairs(test)
    n = len(cu_te)
    R = dict(n=n, train_cup_N=dict(Counter(cu_tr)), test_cup_N=dict(Counter(cu_te)), min_n=10, evaluable=n >= 10)
    if n:
        k = sum(v in (2, 3, 4) for v in cu_te); hi = sum(v >= 5 for v in cu_te) / n
        lo = wilson(k, n)[0]
        R.update(share_234=round(k / n, 4), wilson_lower=round(lo, 3), share_ge5=round(hi, 4),
                 gain_bits_per_unit=round(float(np.mean([L2(lead[v]) - L2(base[v]) for v in cu_te])), 4))
        R["verdict"] = ("pass" if k / n >= 0.9 and lo >= 0.8 and hi <= 0.05 else "fail" if k / n < 0.8 or hi > 0.05 else "neither") if n >= 10 else "not evaluable"
    else:
        R["verdict"] = "not evaluable"
    return R


# ---------------------------------------------------------------- F5
class ClassTri:
    def __init__(self, seqs, cls):
        self.cls = cls
        self.T = Tri([[cls.get(s, s) for s in q] for q in seqs])
        self.em = Counter(s for q in seqs for s in q)
        self.mem = defaultdict(set)
        for s in self.em: self.mem[cls.get(s, s)].add(s)

    def ll(self, q):  # nats, list per token (signs seen in training + EOS)
        q = [s for s in q if s in self.em]
        c = [self.cls.get(s, s) for s in q]
        x = ["<s>", "<s>"] + c + ["</s>"]
        out = []
        for i in range(2, len(x)):
            lp = math.log(self.T.p(x[i - 2], x[i - 1], x[i]))
            if i - 2 < len(q):
                s = q[i - 2]; m = self.mem[x[i]]
                lp += math.log((self.em[s] + 0.5) / (sum(self.em[t] for t in m) + 0.5 * len(m)))
            out.append(lp)
        return out


def f5(train, test):
    tr = [r for u in train for r in u["runs"] if r]
    merged = ClassTri(tr, {s: "FISH" for s in FISH}); plain = ClassTri(tr, {})
    per = []
    for u in test:
        a = [x for r in u["runs"] if r for x in merged.ll(r)]; b = [x for r in u["runs"] if r for x in plain.ll(r)]
        if a: per.append((sum(a) - sum(b), len(a)))
    nfish = sum(s in FISH for u in test for s in u["seq"])
    R = dict(n_texts=len(per), n_tokens=int(sum(n for _, n in per)), n_fish_tokens=nfish, min_fish=30, evaluable=nfish >= 30)
    if per:
        d = np.array([x for x, _ in per]); w = np.array([n for _, n in per])
        g = d.sum() / w.sum(); bs = []
        for _ in range(2000):
            i = rng.integers(0, len(d), len(d)); bs.append(d[i].sum() / w[i].sum())
        lo, hi = np.percentile(bs, [2.5, 97.5])
        R.update(gain_nats_per_token=round(float(g), 5), ci=[round(float(lo), 5), round(float(hi), 5)],
                 gain_bits_total=round(float(d.sum() / math.log(2)), 3))
        R["verdict"] = ("pass" if g > 0 and lo > 0 else "fail" if hi < 0 else "neither") if nfish >= 30 else "not evaluable"
    else:
        R["verdict"] = "not evaluable"
    return R


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["dryrun", "forward"], required=True)
    a = ap.parse_args()
    R = {"mode": a.mode}
    if a.mode == "dryrun":
        I, M = icit_units(), m77_units()
        itr, ite = [u for u in I if u["site"] != HELD["ICIT"]], [u for u in I if u["site"] == HELD["ICIT"]]
        mtr, mte = [u for u in M if u["site"] != HELD["M77"]], [u for u in M if u["site"] == HELD["M77"]]
        R["n"] = dict(icit_train=len(itr), icit_test=len(ite), m77_train=len(mtr), m77_test=len(mte),
                      test_kinds_icit=dict(Counter(u["kind"] for u in ite)), test_kinds_m77=dict(Counter(u["kind"] for u in mte)))
        R["F1"], R["F2"], R["F3"], R["F4"] = f1(itr, ite, "W"), f2(itr, ite, "W"), f3(itr, ite, "W"), f4(itr, ite, "W")
        R["F5"] = f5(mtr, mte)
        R["F3_M77_secondary"] = f3(mtr, mte, "M")
    else:
        M = m77_units(); N = new_units()
        R["n"] = dict(m77_train=len(M), new=len(N), kinds=dict(Counter(u["kind"] for u in N)))
        R["F1"], R["F2"], R["F3"], R["F4"], R["F5"] = f1(M, N, "M"), f2(M, N, "M"), f3(M, N, "M"), f4(M, N, "M"), f5(M, N)
    ev = {k: v for k, v in R.items() if k in ("F1", "F2", "F3", "F4", "F5") and v.get("evaluable")}
    tot = 0.0
    for k, v in ev.items():
        tot += v.get("gain_bits_per_unit", v.get("gain_vs_mid", v.get("gain_nats_per_token", 0) / math.log(2)))
    R["evaluable"] = sorted(ev); R["summed_gain"] = round(tot, 4)
    R["kill"] = "uninformative (none evaluable)" if not ev else ("KILLED: no gain over baseline" if tot <= 0 else "survives: gain over baseline")
    json.dump(R, open(OUT / f"results_{a.mode}.json", "w"), indent=1, default=float)
    print(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
