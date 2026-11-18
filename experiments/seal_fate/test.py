"""Confirmatory tests H1-H4 + power, calibration and exploratory scan for docs/prereg/seal_fate.md.
Run (through the gate): board/run.sh .venv/bin/python -I experiments/seal_fate/test.py
Writes results.json and test.log in this folder. Single process.
"""
import csv, json, os, sys
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SEED = 20261118
NNULL = 5000
NPLANT = 200
NPERM_PLANT = 1000
RS = (1.5, 2.0, 3.0)
QUICK = "quick" in sys.argv
if QUICK:
    NNULL, NPLANT, NPERM_PLANT = 300, 10, 100
LOG = open(os.path.join(HERE, "test_quick.log" if QUICK else "test.log"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); LOG.write(s + "\n"); LOG.flush()


OPENER = {"M267", "M391", "M293", "M150", "M286", "M412", "M146", "M395", "M305"}
CLOSER = {"M342", "M211", "M15", "M254", "M12", "M14", "M388"}
FISH = {f"M{i}" for i in range(59, 76)}
NUMERAL = {f"M{i}" for i in range(86, 122)} - {"M90", "M92", "M93"}
CLASSES = {"OPENER": OPENER, "CLOSER": CLOSER, "FISH": FISH, "NUMERAL": NUMERAL}
CN = list(CLASSES)

# ------------------------------------------------------------------ data
M77 = defaultdict(list)
OT = {}
for l in open(os.path.join(REPO, "data/m77_lines.jsonl")):
    x = json.loads(l)
    M77[x["text_no"]].append((x["side"], x["line"], x["signs"]))
    OT[x["text_no"]] = x["object_type"]
TEXT = {k: [s for _, _, sg in sorted(v, key=lambda t: (t[0], t[1])) for s in sg if s not in ("#", "|")] for k, v in M77.items()}

fate = {}
for r in csv.DictReader(open(os.path.join(HERE, "fate.csv"))):
    fate.setdefault((r["source"], r["serial"]), r)
reg = {}
for r in csv.DictReader(open(os.path.join(REPO, "experiments/old_registers/registers.csv"))):
    if r["source"] in ("Vats1940_EH", "Mackay1938_FEM") and r["m77_text_no"]:
        reg.setdefault((r["source"], r["object_no"]), r)


def depth_band(r):
    try:
        return str(int(abs(float(r["depth_ft"])) // 5))
    except Exception:
        return "na"


objs = []
for k, f in fate.items():
    rg = reg.get(k)
    if rg is None:
        continue
    tn = int(float(rg["m77_text_no"]))
    seq = TEXT.get(tn, [])
    if not seq:
        continue
    objs.append(dict(source=k[0], serial=k[1], tn=tn, seq=seq, L=len(seq),
                     typ="seal" if OT.get(tn) == "seal" else "other", band=depth_band(rg), f=f))
log("linked objects with text:", Counter(o["source"] for o in objs))


def dedup(group):
    seen, out = set(), []
    for o in group:
        k = " ".join(o["seq"])
        if k not in seen:
            seen.add(k); out.append(o)
    return out


def ccounts(seq):
    return np.array([sum(s in CLASSES[c] for s in seq) for c in CN] + [len(seq)], dtype=float)


ALLTOK = Counter(s for o in objs for s in o["seq"])
CLASS_SIGNS = {c: (list(CLASSES[c] & set(ALLTOK)), np.array([ALLTOK[s] for s in CLASSES[c] & set(ALLTOK)], float)) for c in CN}

# ------------------------------------------------------------------ truncation-null tests (H1, H2)


def trunc_null(fate_grp, pool, rng, n):
    """n pseudo fate groups: each member replaced by a random window (same length) of a pool text of same type."""
    by_t = defaultdict(list)
    for o in pool:
        by_t[o["typ"]].append(o)
    cand = []
    skipped = 0
    for b in fate_grp:
        c = [o for o in by_t[b["typ"]] if o["L"] >= b["L"]] or [o for o in pool if o["L"] >= b["L"]]
        if not c:
            skipped += 1
            continue
        cand.append((b["L"], c))
    tot = np.zeros((n, len(CN) + 1))
    pres = defaultdict(lambda: np.zeros(n))
    for i in range(n):
        for L, c in cand:
            o = c[rng.integers(len(c))]
            st = rng.integers(o["L"] - L + 1)
            w = o["seq"][st:st + L]
            tot[i] += ccounts(w)
            for s in set(w):
                pres[s][i] += 1
    return tot, pres, skipped, len(cand)


def omni(counts_obs, null_tot):
    """counts_obs: (5,) class counts + total tokens; null_tot: (n,5). Returns T_obs, T_null, z dict."""
    sh_n = null_tot[:, :4] / null_tot[:, 4:5]
    mu, sd = sh_n.mean(0), sh_n.std(0)
    ok = sd > 0
    sh_o = counts_obs[:4] / counts_obs[4]
    z = np.where(ok, (sh_o - mu) / np.where(ok, sd, 1), 0.0)
    zn = np.where(ok, (sh_n - mu) / np.where(ok, sd, 1), 0.0)
    return float((z ** 2).sum()), (zn ** 2).sum(1), {c: (round(float(z[j]), 3), round(float(sh_o[j]), 4), round(float(mu[j]), 4)) for j, c in enumerate(CN)}, ok


def pval(obs, null):
    return (1 + int((null >= obs - 1e-12).sum())) / (1 + len(null))


def plant_counts(counts, c_idx, k, rng):
    """replace k non-class tokens by class c tokens (counts-level)."""
    x = counts.copy()
    N = int(x[4])
    others = [int(x[j]) for j in range(4) if j != c_idx]
    none = N - int(x[:4].sum())
    pools = others + [none]
    k = min(k, sum(pools))
    if k <= 0:
        return x
    take = rng.multivariate_hypergeometric(pools, k)
    oi = [j for j in range(4) if j != c_idx]
    for j, t in zip(oi, take[:3]):
        x[j] -= t
    x[c_idx] += k
    return x


def trunc_test(name, site, flag):
    grp = [o for o in objs if o["source"] == site and o["f"].get(flag) == "1"]
    pool = [o for o in objs if o["source"] == site and o["f"].get(flag) == "0"]
    grp, pool = dedup(grp), dedup(pool)
    rng = np.random.default_rng(SEED + sum(map(ord, name)))
    null, pres, skipped, used = trunc_null(grp, pool, rng, NNULL)
    obs = sum(ccounts(o["seq"]) for o in grp if any(p["L"] >= o["L"] for p in pool))
    T, Tn, z, ok = omni(obs, null)
    p = pval(T, Tn)
    log(f"{name}: n_fate={len(grp)} (used {used}, skipped {skipped}) n_pool={len(pool)} tokens={int(obs[4])} T={T:.2f} p={p:.4f} z={z}")
    # calibration: pseudo-observed groups drawn from a second independent null
    cal, _, _, _ = trunc_null(grp, pool, np.random.default_rng(SEED + 7), 200)
    fpr = float(np.mean([pval(omni(cal[i], null)[0], Tn) < 0.05 for i in range(200)]))
    # power: plant into pseudo-observed groups
    mu_counts = null.mean(0)
    power = {}
    base, _, _, _ = trunc_null(grp, pool, np.random.default_rng(SEED + 11), NPLANT)
    prng = np.random.default_rng(SEED + 13)
    for j, c in enumerate(CN):
        for r in RS:
            k = int(round((r - 1) * mu_counts[j]))
            hits = 0
            for i in range(NPLANT):
                x = plant_counts(base[i], j, k, prng)
                hits += pval(omni(x, null)[0], Tn) < 0.05
            power[f"{c}@{r}"] = hits / NPLANT
    log(f"  calibration FPR={fpr:.3f}  power={power}")
    # exploratory per-sign presence scan
    scan = []
    nobj = Counter(s for o in grp + pool for s in set(o["seq"]))
    for s, n in nobj.items():
        if n < 8:
            continue
        ob = sum(s in set(o["seq"]) for o in grp if any(p["L"] >= o["L"] for p in pool))
        nl = pres[s] if s in pres else np.zeros(NNULL)
        m = nl.mean()
        pp = (1 + int((np.abs(nl - m) >= abs(ob - m) - 1e-12).sum())) / (1 + NNULL)
        scan.append(dict(sign=s, obs=int(ob), null_mean=round(float(m), 2), p=pp, dir="+" if ob > m else "-"))
    return dict(test=name, site=site, flag=flag, n_fate=len(grp), n_used=used, n_pool=len(pool), tokens=int(obs[4]),
                T=round(T, 3), p=p, z=z, classes_testable=[c for c, k in zip(CN, ok) if k], calib_fpr=fpr, power=power), scan


# ------------------------------------------------------------------ permutation tests (H3, H4)


def perm_mats(lab, strata, n, rng):
    out = np.empty((n, len(lab)), dtype=bool)
    groups = [np.where(strata == s)[0] for s in np.unique(strata)]
    for r in range(n):
        x = lab.copy()
        for g in groups:
            x[g] = lab[g][rng.permutation(len(g))]
        out[r] = x
    return out


def open_tests():
    site = "Mackay1938_FEM"
    o_ = dedup([o for o in objs if o["source"] == site and o["f"]["OPEN"] == "1"])
    r_ = dedup([o for o in objs if o["source"] == site and o["f"]["ROOM"] == "1"])
    data = o_ + r_
    lab = np.array([1] * len(o_) + [0] * len(r_), dtype=bool)
    strata = np.array([o["typ"] + "|" + o["band"] for o in data])
    C = np.array([ccounts(o["seq"]) for o in data])
    L = np.array([o["L"] for o in data], float)
    rng = np.random.default_rng(SEED + 3)
    P = perm_mats(lab, strata, NNULL, rng)

    def share_stats(Pm, Cm):
        cnt = Pm.astype(float) @ Cm
        return cnt[:, :4] / cnt[:, 4:5]

    shn = share_stats(P, C)
    mu, sd = shn.mean(0), shn.std(0)
    ok = sd > 0
    sho = (lab.astype(float) @ C)[:4] / (lab.astype(float) @ C)[4]
    zo = np.where(ok, (sho - mu) / np.where(ok, sd, 1), 0)
    zn = np.where(ok, (shn - mu) / np.where(ok, sd, 1), 0)
    T, Tn = float((zo ** 2).sum()), (zn ** 2).sum(1)
    p3 = pval(T, Tn)
    z = {c: (round(float(zo[j]), 3), round(float(sho[j]), 4), round(float(mu[j]), 4)) for j, c in enumerate(CN)}
    log(f"H3 OPEN vs ROOM classes: n_open={len(o_)} n_room={len(r_)} T={T:.2f} p={p3:.4f} z={z}")

    def mdiff(Pm):
        Pf = Pm.astype(float)
        return (Pf @ L) / Pf.sum(1) - ((1 - Pf) @ L) / (1 - Pf).sum(1)

    d_obs = float(mdiff(lab[None, :])[0])
    dn = mdiff(P)
    p4 = (1 + int((np.abs(dn - dn.mean()) >= abs(d_obs - dn.mean()) - 1e-12).sum())) / (1 + NNULL)
    log(f"H4 OPEN vs ROOM length: mean L open={L[lab].mean():.3f} room={L[~lab].mean():.3f} diff={d_obs:.3f} p={p4:.4f}")

    # power: pseudo labels (a permutation), plant into pseudo-OPEN group, null = NPERM_PLANT reused perms
    prng = np.random.default_rng(SEED + 17)
    Pp = P[:NPERM_PLANT]
    shp = share_stats(Pp, C)
    pw3, pw4 = {}, {}
    base_labels = perm_mats(lab, strata, NPLANT, np.random.default_rng(SEED + 19))
    for j, c in enumerate(CN):
        for r in RS:
            hits = 0
            for i in range(NPLANT):
                bl = base_labels[i]
                Cx = C.copy()
                tot = Cx[bl].sum(0)
                k = int(round((r - 1) * mu[j] * tot[4]))
                # spread the k replacements over pseudo-OPEN objects in proportion to their non-class tokens
                idx = np.where(bl)[0]
                room = Cx[idx, 4] - Cx[idx, j]
                if room.sum() <= 0 or k <= 0:
                    continue
                add = prng.multivariate_hypergeometric(room.astype(int), min(k, int(room.sum())))
                for ii, a in zip(idx, add):
                    if a:
                        Cx[ii] = plant_counts(Cx[ii], j, int(a), prng)
                cnt_o = Cx[bl].sum(0); sh_o = cnt_o[:4] / cnt_o[4]
                cn = Pp.astype(float) @ Cx; sh_n = cn[:, :4] / cn[:, 4:5]
                m_, s_ = sh_n.mean(0), sh_n.std(0); okk = s_ > 0
                Tz = float((np.where(okk, (sh_o - m_) / np.where(okk, s_, 1), 0) ** 2).sum())
                Tnn = (np.where(okk, (sh_n - m_) / np.where(okk, s_, 1), 0) ** 2).sum(1)
                hits += pval(Tz, Tnn) < 0.05
            pw3[f"{c}@{r}"] = hits / NPLANT
    for dl in (0.25, 0.5, 1.0):
        hits = 0
        for i in range(NPLANT):
            bl = base_labels[i]
            Lx = L + np.where(bl, dl, 0.0)
            Pf = Pp.astype(float)
            dnn = (Pf @ Lx) / Pf.sum(1) - ((1 - Pf) @ Lx) / (1 - Pf).sum(1)
            do = Lx[bl].mean() - Lx[~bl].mean()
            pp = (1 + int((np.abs(dnn - dnn.mean()) >= abs(do - dnn.mean()) - 1e-12).sum())) / (1 + NPERM_PLANT)
            hits += pp < 0.05
        pw4[f"+{dl} signs"] = hits / NPLANT
    log(f"  H3 power={pw3}\n  H4 power={pw4}")
    # exploratory scan
    scan = []
    pres_all = Counter(s for o in data for s in set(o["seq"]))
    for s, n in pres_all.items():
        if n < 8:
            continue
        v = np.array([s in set(o["seq"]) for o in data], float)
        ob = float(lab.astype(float) @ v)
        nl = P.astype(float) @ v
        m = nl.mean()
        pp = (1 + int((np.abs(nl - m) >= abs(ob - m) - 1e-12).sum())) / (1 + NNULL)
        scan.append(dict(sign=s, obs=int(ob), null_mean=round(float(m), 2), p=pp, dir="+" if ob > m else "-"))
    h3 = dict(test="H3", n_open=len(o_), n_room=len(r_), T=round(T, 3), p=p3, z=z, classes_testable=[c for c, k in zip(CN, ok) if k], power=pw3)
    h4 = dict(test="H4", mean_L_open=round(float(L[lab].mean()), 3), mean_L_room=round(float(L[~lab].mean()), 3), diff=round(d_obs, 3), p=p4, power=pw4)
    return h3, h4, scan


def bh(ps):
    n = len(ps)
    order = np.argsort(ps)
    q = np.empty(n)
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        prev = min(prev, ps[i] * n / rank)
        q[i] = prev
    return q


def holm(ps):
    n = len(ps)
    order = np.argsort(ps)
    adj = np.empty(n)
    run = 0
    for rank, i in enumerate(order):
        run = max(run, min(1, (n - rank) * ps[i]))
        adj[i] = run
    return adj


if __name__ == "__main__":
    h1, s1 = trunc_test("H1 Harappa BROKEN", "Vats1940_EH", "BROKEN")
    h2, s2 = trunc_test("H2 MD BROKEN_PROXY", "Mackay1938_FEM", "BROKEN_PROXY")
    h3, h4, s3 = open_tests()
    ps = np.array([h1["p"], h2["p"], h3["p"], h4["p"]])
    ha = holm(ps)
    for h, a in zip((h1, h2, h3, h4), ha):
        h["p_holm"] = round(float(a), 4)
    log("Holm-adjusted:", [round(float(a), 4) for a in ha])
    # replication of per-class directions H1 vs H2
    rep = {c: dict(h1_z=h1["z"][c][0], h2_z=h2["z"][c][0],
                   replicated=bool(abs(h1["z"][c][0]) >= 1.96 and abs(h2["z"][c][0]) >= 1.96 and np.sign(h1["z"][c][0]) == np.sign(h2["z"][c][0])))
           for c in CN}
    log("class replication:", rep)
    # exploratory scans
    ex = {}
    for nm, sc, other in (("E1_broken_harappa", s1, {d["sign"]: d for d in s2}), ("E1_broken_md", s2, {d["sign"]: d for d in s1}), ("E1_open_md", s3, None)):
        if not sc:
            ex[nm] = []
            continue
        q = bh(np.array([d["p"] for d in sc]))
        for d, qq in zip(sc, q):
            d["q"] = round(float(qq), 4)
            if other is not None and d["sign"] in other:
                d["other_site_p"], d["other_site_dir"] = other[d["sign"]]["p"], other[d["sign"]]["dir"]
        sc.sort(key=lambda d: d["p"])
        ex[nm] = sc
        log(nm, "signs scanned:", len(sc), "q<0.10:", [d for d in sc if d["q"] < 0.10], "top5:", sc[:5])
    # descriptive counts for untestable fates
    desc = {}
    for site in ("Vats1940_EH", "Mackay1938_FEM"):
        sub = [f for (s, _), f in fate.items() if s == site]
        desc[site] = {k: sum(f[k] == "1" for f in sub) for k in ("BROKEN", "BROKEN_PROXY", "CUT", "BURNT", "WORN", "REUSED", "UNFINISHED", "OPEN", "DRAIN_WELL_GATE", "ROOM", "BURIAL", "HOARD", "SURFACE")}
    json.dump(dict(H1=h1, H2=h2, H3=h3, H4=h4, class_replication=rep, exploratory=ex, fate_counts=desc,
                   kappa=json.load(open(os.path.join(HERE, "kappa.json")))), open(os.path.join(HERE, "results_quick.json" if QUICK else "results.json"), "w"), indent=1, default=str)
    log("done")
