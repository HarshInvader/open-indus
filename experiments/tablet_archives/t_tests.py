"""Pre-registered tests T1-T4 for docs/prereg/tablet_archives.md.

Run from repo root: .venv/bin/python -I experiments/tablet_archives/t_tests.py
Reads tablets.csv (build_tablets.py). Writes results.json and t_tests.log (via tee).
Power (planted answers) is computed and printed BEFORE the real statistics.
"""
import csv, json, os, collections, math
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261114)
NPERM = 10000
NPLANT, NPERM_PLANT = 200, 1000

rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'tablets.csv'))) if r['tier'] in ('2', '3', '4')]
for r in rows:
    r['tier'] = int(r['tier'])


def half(m):
    return 'F' if m == 'F' else ('E' if m in ('E', 'ET') else '')


# ---------- units ----------
groups = collections.OrderedDict()
for r in rows:
    groups.setdefault(r['copy_group'], []).append(r)
G = []  # copy-group units
for k, mem in groups.items():
    f = mem[0]
    G.append(dict(key=k, type=f['type'], tier=f['tier'], mult=len(mem), complete=f['obv_complete'] == '1',
                  stratum=f"{f['type']}|{f['period_key']}", half=half(f['mound']),
                  signs=sorted(set(x for x in f['obverse'].replace('/', ' ').split() if x != '#'))))
GC = [g for g in G if g['complete']]

# T1 units: distinct (copy group, deposit)
seen, U1 = set(), []
for r in rows:
    if not r['deposit']:
        continue
    k = (r['copy_group'], r['deposit'])
    if k in seen:
        continue
    seen.add(k)
    U1.append(dict(dep=r['deposit'], trench=f"{r['mound']}|{r['trench']}", tier=r['tier'],
                   stratum=f"{r['type']}|{r['period_key']}"))


def codes(xs):
    u = {v: i for i, v in enumerate(sorted(set(xs)))}
    return np.array([u[x] for x in xs])


def perm_matrix(strata, R):
    """R within-stratum permutations as index arrays: tiers_perm = tiers[P[r]] keeps each tier in its stratum."""
    s = codes(strata).astype(float)
    base = np.argsort(s, kind='stable')
    keys = s[None, :] + rng.random((R, len(s))) * 0.5
    order = np.argsort(keys, axis=1)  # within-stratum random order, strata grouped like base
    P = np.empty_like(order)
    P[:, base] = order
    return P


def onehot(t):
    return (t[:, None] == np.array([2, 3, 4])[None, :]).astype(float)


# ---------- statistics ----------
def g_table(O):
    E = O.sum(-1, keepdims=True) * O.sum(-2, keepdims=True) / O.sum((-1, -2), keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(O > 0, O * np.log(O / E), 0.0)
    return 2 * t.sum((-1, -2))


def t1_stat(dep, T):  # T: (R, n) tiers
    nd = dep.max() + 1
    idx = dep[None, :] * 3 + (T - 2)
    O = np.stack([np.bincount(row, minlength=nd * 3) for row in idx]).reshape(len(T), nd, 3).astype(float)
    return g_table(O)


def t2_stat(mult_rank, T):
    tr = T.astype(float)
    # Spearman with ties = Pearson of ranks; ranks of tiers are a fixed multiset, recompute per row
    from scipy.stats import rankdata
    tr = rankdata(tr, axis=1)
    a = tr - tr.mean(1, keepdims=True); b = mult_rank - mult_rank.mean()
    return (a * b).sum(1) / np.sqrt((a ** 2).sum(1) * (b ** 2).sum())


def t3_stat(X, T):
    Y = np.stack([onehot(t) for t in T])  # R,n,3
    O1 = np.einsum('ns,rnk->rsk', X, Y)
    O0 = Y.sum(1)[:, None, :] - O1
    O = np.stack([O1, O0], axis=2)  # r,s,2,3
    return g_table(O).sum(1)


def perm_p(stat_fn, tiers, strata, R, alt='greater'):
    obs = stat_fn(tiers[None, :])[0]
    P = perm_matrix(strata, R)
    null = np.concatenate([stat_fn(tiers[P[i:i + 500]]) for i in range(0, R, 500)])
    if alt == 'greater':
        p = (np.sum(null >= obs - 1e-12) + 1) / (R + 1)
    else:
        p = (np.sum(null <= obs + 1e-12) + 1) / (R + 1)
    return float(obs), float(p), null


# ---------- data arrays ----------
dep_count = collections.Counter(u['dep'] for u in U1)
U1k = [u for u in U1 if dep_count[u['dep']] >= 3]
dep1 = codes([u['dep'] for u in U1k]); tier1 = np.array([u['tier'] for u in U1k]); str1 = [u['stratum'] for u in U1k]

GB = [g for g in GC if g['type'] == 'TAB:B']
from scipy.stats import rankdata


def t2_arrays(gs):
    return (np.array([g['tier'] for g in gs]), rankdata([g['mult'] for g in gs]), [g['stratum'] for g in gs])


sign_n = collections.Counter(s for g in GC for s in g['signs'])
feat = [s for s, n in sign_n.items() if n >= 5]
X3 = np.array([[s in g['signs'] for s in feat] for g in GC], float)
tier3 = np.array([g['tier'] for g in GC]); str3 = [g['stratum'] for g in GC]

out = dict(n_tablets=len(rows), n_groups=len(G), n_groups_complete=len(GC), n_T1_units=len(U1k),
           n_T1_deposits=int(dep1.max() + 1), n_TABB_groups=len(GB), n_T3_features=len(feat))
print(json.dumps(out))
marg = np.bincount(tier3 - 2, minlength=3) / len(tier3)

# ---------- POWER (planted answers) ----------
print('\n== Planted-answer power (printed before real statistics) ==')


def power(make_planted, stat_fn, strata, alt):
    hits = 0
    for _ in range(NPLANT):
        t = make_planted()
        _, p, _ = perm_p(stat_fn, t, strata, NPERM_PLANT, alt)
        hits += p < 0.01
    return hits / NPLANT


def plant_t1():
    t = tier1.copy()
    for d in np.unique(dep1):
        pr = rng.dirichlet(3 * marg)
        m = dep1 == d
        t[m] = rng.choice([2, 3, 4], size=m.sum(), p=pr)
    return t


tB, mB, sB = t2_arrays(GB)


def plant_t2():
    t = rng.choice([2, 3, 4], size=len(tB), p=np.bincount(tB - 2, minlength=3) / len(tB))
    multi = mB > mB.min()
    t[multi] = rng.choice([2, 3, 4], size=multi.sum(), p=[0.6, 0.3, 0.1])
    return t


top15 = [feat.index(s) for s, _ in sorted(((s, sign_n[s]) for s in feat), key=lambda x: -x[1])[:15]]


def plant_t3():
    t = tier3.copy()
    pref = rng.choice([2, 3, 4], size=len(top15))
    for i in range(len(t)):
        for j, f in enumerate(top15):
            if X3[i, f]:
                t[i] = pref[j] if rng.random() < 0.7 else rng.choice([2, 3, 4], p=marg)
                break
    return t


pw = dict(
    T1=power(plant_t1, lambda T: t1_stat(dep1, T), str1, 'greater'),
    T2=power(plant_t2, lambda T: t2_stat(mB, T), sB, 'less'),
    T3=power(plant_t3, lambda T: t3_stat(X3, T), str3, 'greater'))
print('power at p<0.01:', pw)
out['power'] = pw

# ---------- REAL TESTS ----------
print('\n== Confirmatory tests ==')
res = {}
o, p, _ = perm_p(lambda T: t1_stat(dep1, T), tier1, str1, NPERM)
res['T1'] = dict(G=o, p=p, units=len(U1k), deposits=int(dep1.max() + 1))
print(f"T1 tier x deposit: G={o:.1f} p={p:.4f} (units {len(U1k)}, deposits {dep1.max()+1})")

o, p, _ = perm_p(lambda T: t2_stat(mB, T), tB, sB, NPERM, alt='less')
res['T2'] = dict(rho=o, p=p, groups=len(GB))
print(f"T2 TAB:B tier vs multiplicity: rho={o:+.3f} p(one-sided neg)={p:.4f} (groups {len(GB)})")

o, p, _ = perm_p(lambda T: t3_stat(X3, T), tier3, str3, NPERM)
res['T3'] = dict(S=o, p=p, groups=len(GC), features=len(feat))
print(f"T3 obverse sign x tier: S={o:.1f} p={p:.4f} (groups {len(GC)}, signs {len(feat)})")

# T4a: T2 per half, all types pooled
res['T4a'] = {}
for h in ('F', 'E'):
    gs = [g for g in GC if g['half'] == h]
    t, m, s = t2_arrays(gs)
    o, p, _ = perm_p(lambda T, m=m: t2_stat(m, T), t, s, NPERM, alt='less')
    res['T4a'][h] = dict(rho=o, p=p, groups=len(gs))
    print(f"T4a half {h}: rho={o:+.3f} p={p:.4f} (groups {len(gs)})")
res['T4a']['pass'] = all(res['T4a'][h]['p'] < 0.05 for h in ('F', 'E'))
res['T4a']['p'] = max(res['T4a'][h]['p'] for h in ('F', 'E'))

# T4b: transfer of sign mean tier F vs E
gF = [g for g in GC if g['half'] == 'F']; gE = [g for g in GC if g['half'] == 'E']
nF = collections.Counter(s for g in gF for s in g['signs']); nE = collections.Counter(s for g in gE for s in g['signs'])
f4 = [s for s in feat if nF[s] >= 3 and nE[s] >= 3]
both = gF + gE
X4 = np.array([[s in g['signs'] for s in f4] for g in both], float)
isF = np.array([g['half'] == 'F' for g in both])
t4 = np.array([g['tier'] for g in both]); s4 = [g['half'] + '|' + g['stratum'] for g in both]


def t4b_stat(T):
    out_ = []
    for t in T:
        mF = (X4[isF] * t[isF, None]).sum(0) / X4[isF].sum(0)
        mE = (X4[~isF] * t[~isF, None]).sum(0) / X4[~isF].sum(0)
        out_.append(spearmanr(mF, mE).correlation if len(f4) > 2 else 0.0)
    return np.nan_to_num(np.array(out_))


o, p, _ = perm_p(t4b_stat, t4, s4, NPERM)
res['T4b'] = dict(rho=o, p=p, signs=len(f4), signs_list=f4, nperm=NPERM)
print(f"T4b sign mean-tier transfer F->E/ET: rho={o:+.3f} p={p:.4f} (signs {len(f4)}: {f4})")

# Holm
names = ['T1', 'T2', 'T3', 'T4a', 'T4b']
ps = [res[n]['p'] for n in names]
order = np.argsort(ps); adj = [0] * 5; run = 0
for rank, i in enumerate(order):
    run = max(run, min(1, ps[i] * (5 - rank))); adj[i] = run
for n, a in zip(names, adj):
    res[n]['p_holm'] = a
print('Holm:', {n: round(a, 4) for n, a in zip(names, adj)})
supported = (res['T2']['p_holm'] < 0.05 and res['T3']['p_holm'] < 0.05 and res['T4a']['pass'] and res['T4b']['p'] < 0.05)
res['verdict'] = 'SUPPORTED' if supported else 'CLOSED'
print('VERDICT:', res['verdict'])
out['confirmatory'] = res

# ---------- SECONDARY / DESCRIPTIVE ----------
print('\n== Secondary (not counted) ==')
sec = {}
# trench-level T1
tc = collections.Counter(u['trench'] for u in U1)
U1t = [u for u in U1 if tc[u['trench']] >= 3 and u['trench'] != '|']
dt = codes([u['trench'] for u in U1t]); tt = np.array([u['tier'] for u in U1t]); st = [u['stratum'] for u in U1t]
o, p, _ = perm_p(lambda T: t1_stat(dt, T), tt, st, NPERM)
sec['T1_trench'] = dict(G=o, p=p, units=len(U1t), trenches=int(dt.max() + 1))
print(f"T1 trench level: G={o:.1f} p={p:.4f} units {len(U1t)} trenches {dt.max()+1}")
# unstratified T1 (shows how much is period drift)
o, p, _ = perm_p(lambda T: t1_stat(dep1, T), tier1, ['x'] * len(tier1), NPERM)
sec['T1_unstratified'] = dict(G=o, p=p)
print(f"T1 unstratified (period drift allowed): G={o:.1f} p={p:.4f}")
O = np.zeros((dep1.max() + 1, 3))
for d, t in zip(dep1, tier1): O[d, t - 2] += 1
chi = ((O - O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / O.sum()) ** 2 / (O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / O.sum())).sum()
sec['T1_cramers_v'] = float(math.sqrt(chi / (O.sum() * 2)))
# per-deposit table for the largest deposits
dn = sorted(set(u['dep'] for u in U1k))
sec['deposit_tier_table'] = {d: list(map(int, O[i])) for i, d in enumerate(dn)}
for i, d in enumerate(dn):
    if O[i].sum() >= 6: print(f"   {d:45s} tiers2/3/4 = {list(map(int, O[i]))}")
# T2 variants
for lab, gs in (('TAB:I', [g for g in GC if g['type'] == 'TAB:I']), ('both', GC)):
    t, m, s = t2_arrays(gs)
    o, p, _ = perm_p(lambda T, m=m: t2_stat(m, T), t, s, NPERM, alt='less')
    sec[f'T2_{lab}'] = dict(rho=o, p_neg=p, groups=len(gs))
    print(f"T2 {lab}: rho={o:+.3f} p(neg)={p:.4f} groups {len(gs)}")
for lab, gs in (('TAB:B', GB), ('TAB:I', [g for g in GC if g['type'] == 'TAB:I'])):
    d = {}
    for t in (2, 3, 4):
        ms = [g['mult'] for g in gs if g['tier'] == t]
        d[t] = dict(groups=len(ms), objects=int(sum(ms)), mean_mult=float(np.mean(ms)) if ms else 0,
                    multi_share=float(np.mean([x > 1 for x in ms])) if ms else 0)
    sec[f'mult_by_tier_{lab}'] = d
    print(f"multiplicity by tier {lab}: " + '; '.join(f"t{t}: {v['groups']} groups/{v['objects']} obj, mean {v['mean_mult']:.2f}, multi {v['multi_share']:.2f}" for t, v in d.items()))
# naive Bayes LOO
def nb_loo(X, t):
    ok = 0
    for i in range(len(t)):
        m = np.ones(len(t), bool); m[i] = False
        sc = []
        for k in (2, 3, 4):
            Xk = X[m & (t == k)]
            pk = (Xk.sum(0) + 1) / (len(Xk) + 2)
            sc.append(np.log((m & (t == k)).sum() / m.sum()) + (X[i] * np.log(pk) + (1 - X[i]) * np.log(1 - pk)).sum())
        ok += [2, 3, 4][int(np.argmax(sc))] == t[i]
    return ok / len(t)
acc = nb_loo(X3, tier3)
Pm = perm_matrix(str3, 200)
nb_null = [nb_loo(X3, tier3[Pm[i]]) for i in range(200)]
sec['nb_loo'] = dict(acc=acc, null_mean=float(np.mean(nb_null)), p=float((np.sum(np.array(nb_null) >= acc) + 1) / 201),
                     majority=float(np.max(np.bincount(tier3 - 2)) / len(tier3)))
print(f"naive Bayes LOO acc {acc:.3f} vs null {np.mean(nb_null):.3f} (p={sec['nb_loo']['p']:.3f}); majority {sec['nb_loo']['majority']:.3f}")
# recurring obverses with one tier
ob = collections.defaultdict(list)
for r in rows:
    if r['obv_complete'] == '1': ob[(r['type'], r['obverse'])].append(r['tier'])
rec = {k: v for k, v in ob.items() if len(v) >= 2}
obs_single = sum(len(set(v)) == 1 for v in rec.values())
allt = np.array([t for v in rec.values() for t in v]); sizes = [len(v) for v in rec.values()]
null_single = []
for _ in range(5000):
    sh = rng.permutation(allt); i = 0; c = 0
    for s in sizes:
        c += len(set(sh[i:i + s])) == 1; i += s
    null_single.append(c)
sec['recurring_obverse_single_tier'] = dict(obs=obs_single, n=len(rec), null_mean=float(np.mean(null_single)),
                                            p=float((np.sum(np.array(null_single) >= obs_single) + 1) / 5001),
                                            note='objects as units; mould copies make single-tier trivially likely; descriptive only (cf. administration P11)')
print(f"recurring obverses single-tier: {obs_single}/{len(rec)} vs null {np.mean(null_single):.1f} (objects as units, descriptive)")
# multi-tier obverses list
sec['multi_tier_obverses'] = {f"{k[0]} {k[1]}": dict(collections.Counter(v)) for k, v in rec.items() if len(set(v)) > 1}
# tier x half, tier x period
sec['tier_by_half'] = {h: dict(collections.Counter(r['tier'] for r in rows if half(r['mound']) == h)) for h in ('F', 'E', '')}
sec['tier_by_period'] = {p: dict(collections.Counter(r['tier'] for r in rows if r['period_key'] == p)) for p in sorted(set(r['period_key'] for r in rows))}
print('tier by half', sec['tier_by_half'])
out['secondary'] = sec

with open(os.path.join(HERE, 'results.json'), 'w') as fh:
    json.dump(out, fh, indent=1, default=lambda x: x.item() if hasattr(x, 'item') else str(x))
print('wrote results.json')
