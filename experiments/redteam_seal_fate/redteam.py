"""Red team of seal_fate H2 (board #37). Pre-registered: docs/prereg/redteam_seal_fate.md.
Run: board/run.sh .venv/bin/python -I experiments/redteam_seal_fate/redteam.py
Single process, < 200 MB. Writes results.json and run.log here.
"""
import csv, json, os, sys
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SEED = 37037
NNULL = 10000
NCAL = 500
NPLANT = 500
if "quick" in sys.argv:
    NNULL, NCAL, NPLANT = 500, 50, 50
LOG = open(os.path.join(HERE, "run.log" if NNULL == 10000 else "run_quick.log"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); LOG.write(s + "\n"); LOG.flush()


OPENER = {"M267", "M391", "M293", "M150", "M286", "M412", "M146", "M395", "M305"}
CLOSER = {"M342", "M211", "M15", "M254", "M12", "M14", "M388"}
FISH = {f"M{i}" for i in range(59, 76)}
NUMERAL = {f"M{i}" for i in range(86, 122)} - {"M90", "M92", "M93"}
CLASSES = [("OPENER", OPENER), ("CLOSER", CLOSER), ("FISH", FISH), ("NUMERAL", NUMERAL)]

# ---------------- M77 raw lines with break marks, reading order
LINES = defaultdict(list)
OTYPE = {}
for r in csv.DictReader(open(os.path.join(REPO, "sources/paragorth_Indus-/data/im77/im77_corpus_lines.csv"))):
    toks = r["signs_reading_order"].split()
    if not toks:
        continue
    LINES[int(r["text_no"])].append((int(r["side"]), int(r["line"]), toks))
    OTYPE[int(r["text_no"])] = r["object_type"]
RAW = {}
for tn, ls in LINES.items():
    seq = []
    for _, _, t in sorted(ls, key=lambda x: (x[0], x[1])):
        seq += t
    RAW[tn] = seq


def pattern(raw):
    signs = [i for i, t in enumerate(raw) if t != "0"]
    if not signs:
        return "EMPTY"
    if "0" not in raw:
        return "NONE"
    st = any(t == "0" for t in raw[:signs[0]])
    en = any(t == "0" for t in raw[signs[-1] + 1:])
    if st and en:
        return "BOTH"
    if st:
        return "START"
    if en:
        return "END"
    return "INTERIOR"


def signs_of(tn):
    return ["M" + t for t in RAW.get(tn, []) if t != "0"]


# ---------------- groups (labels from seal_fate fate.csv + old_registers links)
fate = {}
for r in csv.DictReader(open(os.path.join(REPO, "experiments/seal_fate/fate.csv"))):
    fate.setdefault((r["source"], r["serial"]), r)
reg = {}
for r in csv.DictReader(open(os.path.join(REPO, "experiments/old_registers/registers.csv"))):
    if r["source"] in ("Vats1940_EH", "Mackay1938_FEM") and r["m77_text_no"]:
        reg.setdefault((r["source"], r["object_no"]), r)

objs = []
for k, f in fate.items():
    rg = reg.get(k)
    if rg is None:
        continue
    tn = int(float(rg["m77_text_no"]))
    seq = signs_of(tn)
    if not seq:
        continue
    objs.append(dict(source=k[0], serial=k[1], tn=tn, seq=seq, L=len(seq), pat=pattern(RAW[tn]),
                     otype=OTYPE.get(tn, ""), typ="seal" if OTYPE.get(tn) == "seal" else "other",
                     block=rg.get("block", ""), f=f))


def dedup(g):
    seen, out = set(), []
    for o in g:
        k = " ".join(o["seq"])
        if k not in seen:
            seen.add(k); out.append(o)
    return out


FEM, EH = "Mackay1938_FEM", "Vats1940_EH"
Q = dedup([o for o in objs if o["source"] == FEM and o["f"]["BROKEN_PROXY"] == "1"])
POOL = dedup([o for o in objs if o["source"] == FEM and o["f"]["BROKEN_PROXY"] == "0"])
HB = dedup([o for o in objs if o["source"] == EH and o["f"]["BROKEN"] == "1"])
INTACT = [o for o in POOL if o["pat"] == "NONE"]
log(f"'?' group {len(Q)} distinct; pool {len(POOL)} (intact {len(INTACT)}); Harappa broken {len(HB)}")
R = {"n": dict(q=len(Q), pool=len(POOL), intact=len(INTACT), harappa_broken=len(HB))}

PATS = ["NONE", "START", "END", "BOTH", "INTERIOR"]


def pat_counts(g):
    c = Counter(o["pat"] for o in g)
    return {p: c.get(p, 0) for p in PATS}


all_m77_seal = [dict(pat=pattern(RAW[tn])) for tn in RAW if OTYPE.get(tn) == "seal"]
pc = {"q": pat_counts(Q), "pool": pat_counts(POOL), "harappa_broken": pat_counts(HB), "m77_all_seals": pat_counts(all_m77_seal)}
for k, v in pc.items():
    log(f"break patterns {k}: {v}")
R["patterns"] = pc
tbl = np.array([[pc["q"][p] for p in PATS], [pc["pool"][p] for p in PATS]])
tbl = tbl[:, tbl.sum(0) > 0]
chi = stats.chi2_contingency(tbl)
q_broken = sum(pc["q"][p] for p in PATS[1:]); p_broken = sum(pc["pool"][p] for p in PATS[1:])
fe = stats.fisher_exact([[q_broken, len(Q) - q_broken], [p_broken, len(POOL) - p_broken]])
log(f"'?' vs pool break-mark share: {q_broken}/{len(Q)} vs {p_broken}/{len(POOL)} Fisher OR={fe[0]:.2f} p={fe[1]:.3g}; chi2 patterns p={chi[1]:.3g}")
R["break_mark_q_vs_pool"] = dict(q=[q_broken, len(Q)], pool=[p_broken, len(POOL)], fisher_or=fe[0], fisher_p=fe[1], chi2_p=chi[1])

# ---------------- fragment sampler
by_typ = defaultdict(list)
for o in INTACT:
    by_typ[o["typ"]].append(o)


def cands(typ, cond):
    c = [o for o in by_typ[typ] if cond(o["L"])]
    return c if c else [o for o in INTACT if cond(o["L"])]


CACHE = {}


def cand_for(typ, mode, L):
    key = (typ, mode, L)
    if key in CACHE:
        return CACHE[key]
    if mode == "NONE":
        c = []
        for d in (0, 1, 2, 3, 5, 10):
            c = cands(typ, lambda x: abs(x - L) <= d)
            if len(c) >= 5:
                break
    elif mode == "BOTH":
        c = cands(typ, lambda x: x >= L + 2) or cands(typ, lambda x: x > L)
    else:
        c = cands(typ, lambda x: x > L) or cands(typ, lambda x: x >= L)
    CACHE[key] = c
    return c


def draw(o, mode, rng):
    L = o["L"]
    c = cand_for(o["typ"], mode, L)
    t = c[rng.integers(len(c))]["seq"]
    n = len(t)
    if mode == "NONE":
        return t
    if mode == "INTERIOR" and L == 1:
        mode = "START" if rng.random() < 0.5 else "END"
    if mode == "START":
        return t[n - L:]
    if mode == "END":
        return t[:L]
    if mode == "BOTH":
        if n >= L + 2:
            st = rng.integers(1, n - L)
        else:
            st = rng.integers(n - L + 1)
        return t[st:st + L]
    if mode == "INTERIOR":
        a = int(rng.integers(1, L))
        return t[:a] + t[n - (L - a):]
    if mode == "RANDOM":  # seal_fate's null: random window of a pool text (any pattern) length >= L
        st = rng.integers(n - L + 1)
        return t[st:st + L]
    raise ValueError(mode)


def counts(seq, sets):
    return [sum(s in S for s in seq) for S in sets] + [len(seq)]


SETS = [S for _, S in CLASSES] + [{"M342"}, CLOSER - {"M342"}]
NAMES = [n for n, _ in CLASSES] + ["M342", "CLOSER_noM342"]


def run_null(group, modefn, rng, n):
    out = np.zeros((n, len(SETS) + 1))
    for i in range(n):
        for o in group:
            out[i] += counts(draw(o, modefn(o, rng), rng), SETS)
    return out


def rate_mode(rates):
    ps = np.array([rates.get(p, 0) for p in PATS], float)
    ps = ps / ps.sum()
    return lambda o, rng: PATS[rng.choice(5, p=ps)]


def obs_counts(group):
    return np.sum([counts(o["seq"], SETS) for o in group], 0).astype(float)


def test(name, group, null, obs=None):
    obs = obs_counts(group) if obs is None else obs
    sh = null[:, :-1] / null[:, -1:]
    so = obs[:-1] / obs[-1]
    mu, sd = sh.mean(0), sh.std(0)
    res = {}
    for j, nm in enumerate(NAMES):
        z = (so[j] - mu[j]) / sd[j] if sd[j] > 0 else 0.0
        p = (1 + int((np.abs(sh[:, j] - mu[j]) >= abs(so[j] - mu[j]) - 1e-12).sum())) / (1 + len(sh))
        res[nm] = dict(obs=round(float(so[j]), 4), null=round(float(mu[j]), 4), ratio=round(float(so[j] / mu[j]), 2) if mu[j] else None,
                       z=round(float(z), 2), p=round(p, 5))
    zs = np.array([res[n]["z"] for n in NAMES[:4]])
    zn = (sh[:, :4] - mu[:4]) / np.where(sd[:4] > 0, sd[:4], 1)
    T = float((zs ** 2).sum()); Tn = (zn ** 2).sum(1)
    res["omnibus"] = dict(T=round(T, 2), p=round((1 + int((Tn >= T - 1e-12).sum())) / (1 + len(Tn)), 5))
    log(f"{name}: n={len(group)} tokens={int(obs[-1])} CLOSER {res['CLOSER']} M342 {res['M342']} nonM342 {res['CLOSER_noM342']} omni {res['omnibus']}")
    return res


rng = np.random.default_rng(SEED)
obsQ = obs_counts(Q)
R["obs"] = dict(tokens=int(obsQ[-1]), closer_tokens=int(obsQ[1]), m342_tokens=int(obsQ[4]))

hb_rates = pc["harappa_broken"]
hb_rates_trunc = {p: v for p, v in hb_rates.items() if p != "NONE"}
m77_rates_trunc = {p: v for p, v in pc["m77_all_seals"].items() if p != "NONE"}
R["rates"] = dict(N_B=hb_rates, N_B2=hb_rates_trunc, N_B3=m77_rates_trunc)

NULLS = {
    "N0_random_window_reproduction": lambda o, r: "RANDOM",
    "N_B_harappa_broken_rates": rate_mode(hb_rates),
    "N_B2_harappa_truncated_rates": rate_mode(hb_rates_trunc),
    "N_B3_all_m77_seal_break_rates": rate_mode(m77_rates_trunc),
    "N_A_own_m77_pattern": lambda o, r: o["pat"],
    "N_L_whole_text_same_length": lambda o, r: "NONE",
}
# N0 must draw from the full pool like seal_fate (not only intact texts)
res, nulls = {}, {}
for nm, fn in NULLS.items():
    if nm.startswith("N0"):
        saved = dict(by_typ), list(INTACT)
        by_typ.clear(); [by_typ[o["typ"]].append(o) for o in POOL]; INTACT[:] = POOL; CACHE.clear()
        nl = run_null(Q, fn, rng, NNULL)
        by_typ.clear(); by_typ.update(saved[0]); INTACT[:] = saved[1]; CACHE.clear()
    else:
        nl = run_null(Q, fn, rng, NNULL)
    nulls[nm] = nl
    res[nm] = test(nm, Q, nl)
R["tests"] = res

# seals only under N_B
Qs = [o for o in Q if o["typ"] == "seal"]
nl = run_null(Qs, rate_mode(hb_rates), rng, NNULL)
R["tests"]["N_B_seals_only"] = test("N_B_seals_only", Qs, nl)
R["n"]["q_seals"] = len(Qs)
R["q_object_types"] = dict(Counter(o["otype"] for o in Q))

# Holm over the pre-registered secondary closer tests
sec = {"N_B2": res["N_B2_harappa_truncated_rates"]["CLOSER"]["p"], "N_B3": res["N_B3_all_m77_seal_break_rates"]["CLOSER"]["p"],
       "N_A": res["N_A_own_m77_pattern"]["CLOSER"]["p"], "N_L": res["N_L_whole_text_same_length"]["CLOSER"]["p"],
       "N_B_M342": res["N_B_harappa_broken_rates"]["M342"]["p"], "N_B_nonM342": res["N_B_harappa_broken_rates"]["CLOSER_noM342"]["p"],
       "N_B_seals_only": R["tests"]["N_B_seals_only"]["CLOSER"]["p"], "N_B_omnibus": res["N_B_harappa_broken_rates"]["omnibus"]["p"]}
order = sorted(sec, key=sec.get)
holm, run_max = {}, 0
for i, k in enumerate(order):
    run_max = max(run_max, min(1, sec[k] * (len(order) - i)))
    holm[k] = round(run_max, 4)
R["secondary_holm"] = holm
log("secondary Holm:", holm)

# ---------------- calibration + power under N_B
nB = nulls["N_B_harappa_broken_rates"]
shB = nB[:, 1] / nB[:, -1]
muB = shB.mean()


def p_closer(c, tot):
    s = c / tot
    return (1 + int((np.abs(shB - muB) >= abs(s - muB) - 1e-12).sum())) / (1 + len(shB))


crng = np.random.default_rng(SEED + 1)
cal = run_null(Q, rate_mode(hb_rates), crng, NCAL)
fpr = float(np.mean([p_closer(cal[i, 1], cal[i, -1]) < 0.05 for i in range(NCAL)]))
power = {}
for r in (1.5, 1.7, 2.0):
    hits = 0
    for i in range(NCAL if NCAL < NPLANT else NPLANT):
        row = cal[i % NCAL]
        k = int(round((r - 1) * muB * row[-1]))
        c = min(row[1] + k, row[-1])
        hits += p_closer(c, row[-1]) < 0.05
    power[str(r)] = hits / min(NCAL, NPLANT)
R["calibration_fpr_N_B"] = fpr
R["power_N_B"] = power
log(f"N_B calibration FPR={fpr:.3f} power={power}")

# ---------------- other cheap checks
Lq = [o["L"] for o in Q]; Lp = [o["L"] for o in POOL]
mw = stats.mannwhitneyu(Lq, Lp)
R["length"] = dict(q_mean=float(np.mean(Lq)), pool_mean=float(np.mean(Lp)), mw_p=float(mw.pvalue),
                   q_hist=dict(Counter(Lq)), q_short_le3=sum(l <= 3 for l in Lq))
log(f"length: '?' mean {np.mean(Lq):.2f} vs pool {np.mean(Lp):.2f}, MW p={mw.pvalue:.3g}; '?' hist {sorted(Counter(Lq).items())}")


def closer_share(g):
    c = obs_counts(g)
    return round(float(c[1] / c[-1]), 3), int(c[1]), int(c[-1])


# closer share by own break pattern, '?' vs pool (descriptive)
bp = {}
for p in PATS:
    bp[p] = dict(q=closer_share([o for o in Q if o["pat"] == p]) if any(o["pat"] == p for o in Q) else None,
                 pool=closer_share([o for o in POOL if o["pat"] == p]) if any(o["pat"] == p for o in POOL) else None)
R["closer_by_pattern"] = bp
log("closer share by pattern ('?' vs pool):", bp)
# ends-with-closer per object, '?' vs pool, among NONE texts
for lab, g in (("q", Q), ("pool", POOL)):
    e = sum(o["seq"][-1] in CLOSER for o in g)
    log(f"{lab}: last sign is a closer in {e}/{len(g)} texts")
    R.setdefault("last_is_closer", {})[lab] = [e, len(g)]

blk = Counter(o["block"].strip(" .:'") for o in Q)
blkp = Counter(o["block"].strip(" .:'") for o in POOL)
top = blk.most_common(3)
R["blocks_q"] = dict(blk)
fb = []
for b, n in top:
    t = [[n, len(Q) - n], [blkp.get(b, 0), len(POOL) - blkp.get(b, 0)]]
    fb.append(dict(block=b, q=n, pool=blkp.get(b, 0), p=float(stats.fisher_exact(t)[1])))
R["block_check"] = fb
log("top '?' blocks vs pool:", fb)

# per-object listing for the page check (serial, M77 text, pattern, L, n closers)
with open(os.path.join(HERE, "q_objects.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["fem_serial", "m77_text_no", "object_type", "L", "m77_break_pattern", "n_closer", "last_sign"])
    for o in sorted(Q, key=lambda x: int(x["serial"])):
        w.writerow([o["serial"], o["tn"], o["otype"], o["L"], o["pat"], sum(s in CLOSER for s in o["seq"]), o["seq"][-1]])

json.dump(R, open(os.path.join(HERE, "results.json" if NNULL == 10000 else "results_quick.json"), "w"), indent=1, default=str)
log("done")
