"""Leg 2: does the tall-stroke count N before the cup (M328 / W700) track a physical quantity?

Run from repo root: .venv/bin/python experiments/m328_measure/l2_quantity.py
Pre-registration: docs/prereg/m328_measure.md (Q1-Q4 + secondaries). Writes l2_results.json.
"""
import json, os, sys, math, random, collections
import numpy as np
from scipy.stats import spearmanr, kruskal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, 'experiments', 'functional_reading'))
from corpus.load import icit_texts, m77_lines, m77_texts  # noqa
import fr  # noqa

W_TALL = {'W031': 1, 'W032': 2, 'W033': 3, 'W034': 4, 'W035': 5, 'W036': 6, 'W037': 7}
ALPHA = 0.0125
NPERM = 10000
rng = np.random.default_rng(20261115)


def f(x):
    try: return float(x)
    except Exception: return 0.0


def n_before(seq, cup, tall):
    vals = [tall[seq[i - 1]] for i, x in enumerate(seq) if x == cup and i > 0 and seq[i - 1] in tall]
    return vals


# ---------------- ICIT objects ----------------
def icit_units():
    objs = collections.defaultdict(list)
    for t in icit_texts():
        objs[t['id'].split('.')[0]].append(t)
    out = []
    for oid, recs in objs.items():
        recs.sort(key=lambda r: r['id'])
        vals = set()
        for r in recs: vals |= set(n_before(r['seq'], 'W700', W_TALL))
        if not vals: continue
        if len(vals) > 1: continue  # conflicting N dropped
        ws = [f(r['width_mm']) for r in recs]; hs = [f(r['height_mm']) for r in recs]
        w, h = max(ws), max(hs)
        typ = recs[0]['type']
        strat = 'TAB:B' if typ == 'TAB:B' else 'TAB:I' if typ == 'TAB:I' else 'other'
        out.append(dict(oid=oid, N=vals.pop(), sides=tuple(' '.join(r['seq']) for r in recs),
                        w=w, h=h, strat=strat, site=recs[0]['site'],
                        lot=(recs[0]['period'], recs[0]['phase'])))
    return out


def identities(objs):
    g = collections.defaultdict(list)
    for o in objs: g[(o['sides'], o['strat'])].append(o)
    ids = []
    for (sides, strat), os_ in g.items():
        L = [max(o['w'], o['h']) for o in os_ if max(o['w'], o['h']) > 0]
        A = [o['w'] * o['h'] for o in os_ if o['w'] > 0 and o['h'] > 0]
        ids.append(dict(sides=sides, strat=strat, N=os_[0]['N'], copies=len(os_),
                        length=float(np.median(L)) if L else 0.0, area=float(np.median(A)) if A else 0.0,
                        site=os_[0]['site']))
    return ids


def strat_perm_spearman(x, y, strata, nperm=NPERM, alt='greater', rng=rng):
    x = np.asarray(x, float); y = np.asarray(y, float)
    obs = spearmanr(x, y).correlation
    idx = collections.defaultdict(list)
    for i, s in enumerate(strata): idx[s].append(i)
    idx = [np.array(v) for v in idx.values()]
    ry = np.argsort(np.argsort(y)).astype(float)
    cnt = 0
    for _ in range(nperm):
        xp = x.copy()
        for v in idx: xp[v] = x[rng.permutation(v)]
        r = spearmanr(xp, ry).correlation
        if alt == 'greater': cnt += r >= obs - 1e-12
        else: cnt += abs(r) >= abs(obs) - 1e-12
    return float(obs), (cnt + 1) / (nperm + 1)


def chi2_stat(N, lots):
    tab = collections.Counter(zip(lots, N))
    L = sorted(set(lots)); V = sorted(set(N))
    M = np.array([[tab[(l, v)] for v in V] for l in L], float)
    E = M.sum(1, keepdims=True) * M.sum(0, keepdims=True) / M.sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        return float(np.nansum((M - E) ** 2 / np.where(E > 0, E, np.nan))), M.shape


def perm_chi2(N, lots, strata, nperm=NPERM, rng=rng):
    obs, shape = chi2_stat(N, lots)
    N = np.asarray(N)
    idx = collections.defaultdict(list)
    for i, s in enumerate(strata): idx[s].append(i)
    idx = [np.array(v) for v in idx.values()]
    cnt = 0
    for _ in range(nperm):
        Np = N.copy()
        for v in idx: Np[v] = N[rng.permutation(v)]
        cnt += chi2_stat(list(Np), lots)[0] >= obs - 1e-9
    return obs, (cnt + 1) / (nperm + 1), shape


# ---------------- M77 objects (find-spot lots) ----------------
def m77_units(heldout_only=False):
    held = set(json.load(open(os.path.join(REPO, 'data', 'splits_v2.json')))['heldout'])
    side_texts = collections.defaultdict(list)
    for t in m77_texts(): side_texts[t['text_no']].append(' '.join(t['seq']))
    objs = collections.defaultdict(list)
    for l in m77_lines():
        if l['site'] == 'Harappa': objs[l['text_no']].append(l)
    units = set()
    for tn, ls in objs.items():
        vals = set()
        for l in ls:
            for seg in l['segments']: vals |= set(n_before(seg, 'M328', fr.TALL))
        if len(vals) != 1: continue
        if heldout_only and not any(s in held for s in side_texts[tn]): continue
        loc = ls[0]['locus']
        if loc in ('', '-', None): continue
        full = ' | '.join(' '.join(l['signs']) for l in sorted(ls, key=lambda l: (l['side'], l['line'])))
        units.add((loc, full, vals.pop(), ls[0]['object_type']))
    units = list(units)
    c = collections.Counter(u[0] for u in units)
    units = [u for u in units if c[u[0]] >= 5]
    return units


# ---------------- Q4 ----------------
def ztp_fit(N):
    N = np.asarray(N, float); m = N.mean()
    lo, hi = 1e-6, 50
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid / (1 - math.exp(-mid)) < m: lo = mid
        else: hi = mid
    lam = (lo + hi) / 2
    ll = float(np.sum(N * math.log(lam) - lam - [math.lgamma(k + 1) for k in N] - math.log(1 - math.exp(-lam))))
    return lam, ll


def ztp_pmf(k, lam):
    return math.exp(k * math.log(lam) - lam - math.lgamma(k + 1)) / (1 - math.exp(-lam))


def q4(N):
    lam, llp = ztp_fit(N)
    c = collections.Counter(N); n = len(N)
    llc = sum(v * math.log(v / n) for v in c.values())
    aic_p = 2 * 1 - 2 * llp; aic_c = 2 * (len(c) - 1) - 2 * llc
    verdict = 'count-like' if aic_p <= aic_c else ('name-like' if aic_c < aic_p - 2 else 'undecided')
    obs_round = sum(c[k] for k in (2, 4)) / n
    exp_round = ztp_pmf(2, lam) + ztp_pmf(4, lam)
    expected = {k: round(n * ztp_pmf(k, lam), 2) for k in range(1, 8)}
    return dict(n=n, counts=dict(sorted(c.items())), ztp_lambda=lam, ztp_expected=expected,
                aic_poisson=aic_p, aic_categorical=aic_c, verdict=verdict,
                share_round_2_4=obs_round, ztp_expected_round=exp_round)


# ---------------- power ----------------
def power_spearman(N, strata, rho=0.3, sims=300, nperm=400, alt='greater'):
    N = np.asarray(N, float); hits = 0
    r = 2 * math.sin(math.pi * rho / 6)  # Pearson for target Spearman under normality
    zN = (np.argsort(np.argsort(N + rng.random(len(N)) * 1e-6)) + 0.5) / len(N)
    from scipy.stats import norm
    zN = norm.ppf(zN)
    lr = np.random.default_rng(7)
    for _ in range(sims):
        y = r * zN + math.sqrt(1 - r * r) * lr.standard_normal(len(N))
        _, p = strat_perm_spearman(N, y, strata, nperm=nperm, alt=alt, rng=lr)
        hits += p <= ALPHA
    return hits / sims


def power_lot(units, plant=0.3, sims=200, nperm=400):
    lr = np.random.default_rng(11); hits = 0
    lots = [u[0] for u in units]; strata = [u[3] for u in units]; N0 = [u[2] for u in units]
    vals = sorted(set(N0))
    for _ in range(sims):
        pref = {l: lr.choice(vals) for l in set(lots)}
        N = [pref[l] if lr.random() < plant else n for l, n in zip(lots, N0)]
        _, p, _ = perm_chi2(N, lots, strata, nperm=nperm, rng=lr)
        hits += p <= ALPHA
    return hits / sims


def families(ids):
    parent = list(range(len(ids)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    first = {}
    for i, u in enumerate(ids):
        for s in u['sides']:
            if s in first: parent[find(i)] = find(first[s])
            else: first[s] = i
    fam = collections.defaultdict(list)
    for i in range(len(ids)): fam[find(i)].append(i)
    return list(fam.values())


def main():
    res = {}
    objs = icit_units()
    ids = identities(objs)
    res['n_objects'] = len(objs); res['n_identities'] = len(ids)
    res['strata'] = dict(collections.Counter(u['strat'] for u in ids))
    print('objects', len(objs), 'identities', len(ids), res['strata'])

    # Q1
    U = [u for u in ids if u['length'] > 0]
    rho, p = strat_perm_spearman([u['N'] for u in U], [u['length'] for u in U], [u['strat'] for u in U])
    UA = [u for u in ids if u['area'] > 0]
    rhoA, pA = strat_perm_spearman([u['N'] for u in UA], [u['area'] for u in UA], [u['strat'] for u in UA], nperm=5000)
    byN = collections.defaultdict(list)
    for u in U: byN[u['N']].append(u['length'])
    groups = [v for k, v in sorted(byN.items()) if len(v) >= 3]
    kw = kruskal(*groups) if len(groups) >= 2 else None
    means = {k: (len(v), round(float(np.median(v)), 1)) for k, v in sorted(byN.items())}
    # within-stratum descriptive
    within = {}
    for s in ('TAB:B', 'TAB:I'):
        V = [u for u in U if u['strat'] == s]
        if len(V) >= 8: within[s] = (len(V), float(spearmanr([u['N'] for u in V], [u['length'] for u in V]).correlation))
    res['Q1'] = dict(n=len(U), rho=rho, p=p, pass_=p <= ALPHA, median_length_by_N=means,
                     area=dict(n=len(UA), rho=rhoA, p=pA), kruskal_p=(float(kw.pvalue) if kw else None),
                     within_stratum_rho=within)
    print('Q1', res['Q1'])

    # Q2
    rho2, p2 = strat_perm_spearman([u['N'] for u in ids], [u['copies'] for u in ids], [u['strat'] for u in ids], alt='two')
    cop = collections.defaultdict(list)
    for u in ids: cop[u['N']].append(u['copies'])
    res['Q2'] = dict(n=len(ids), rho=rho2, p=p2, pass_=p2 <= ALPHA,
                     mean_copies_by_N={k: (len(v), round(float(np.mean(v)), 2)) for k, v in sorted(cop.items())})
    print('Q2', res['Q2'])

    # replication halves
    fams = families(ids)
    order = list(range(len(fams))); random.Random(20261115).shuffle(order)
    halves = [[], []]
    for j, fi in enumerate(order): halves[j % 2] += [ids[i] for i in fams[fi]]
    rep = {}
    for h, H in enumerate(halves):
        V = [u for u in H if u['length'] > 0]
        rep[f'half{h}'] = dict(n_len=len(V),
                               rho_len=float(spearmanr([u['N'] for u in V], [u['length'] for u in V]).correlation),
                               n=len(H), rho_copies=float(spearmanr([u['N'] for u in H], [u['copies'] for u in H]).correlation))
    res['replication_halves'] = dict(n_families=len(fams), **rep)
    print('halves', rep)

    # Q3
    units = m77_units()
    chi, p3, shape = perm_chi2([u[2] for u in units], [u[0] for u in units], [u[3] for u in units])
    tab = collections.defaultdict(collections.Counter)
    for u in units: tab[u[0]][u[2]] += 1
    hu = m77_units(heldout_only=True)
    if len(set(u[0] for u in hu)) >= 2:
        chih, p3h, shapeh = perm_chi2([u[2] for u in hu], [u[0] for u in hu], [u[3] for u in hu], nperm=5000)
    else:
        chih, p3h, shapeh = None, None, None
    res['Q3'] = dict(n_units=len(units), table_shape=shape, chi2=chi, p=p3, pass_=p3 <= ALPHA,
                     table={k: dict(v) for k, v in sorted(tab.items())},
                     heldout=dict(n_units=len(hu), chi2=chih, p=p3h, shape=shapeh))
    print('Q3', {k: v for k, v in res['Q3'].items() if k != 'table'})

    # secondary: ICIT lot = period/phase (Harappa)
    lotu = set()
    for o in objs:
        if o['site'] == 'Harappa' and o['lot'] != ('-', '-'):
            lotu.add(('/'.join(o['lot']), o['sides'], o['N'], o['strat']))
    lotu = list(lotu); c = collections.Counter(u[0] for u in lotu); lotu = [u for u in lotu if c[u[0]] >= 5]
    chi_l, p_l, sh_l = perm_chi2([u[2] for u in lotu], [u[0] for u in lotu], [u[3] for u in lotu], nperm=5000)
    res['Q3_secondary_icit_phase'] = dict(n_units=len(lotu), shape=sh_l, chi2=chi_l, p=p_l)
    print('Q3 icit phase', res['Q3_secondary_icit_phase'])

    # Q4
    res['Q4_identities'] = q4([u['N'] for u in ids])
    sideN = {}
    for o in objs:
        for s in o['sides']:
            v = n_before(s.split(), 'W700', W_TALL)
            if v: sideN[s] = v[0]
    res['Q4_secondary_distinct_cup_side_texts'] = q4(list(sideN.values()))
    print('Q4', res['Q4_identities']); print('Q4 sides', res['Q4_secondary_distinct_cup_side_texts'])

    # entropy of N by head sign (ICIT distinct side texts), exploratory
    heads = collections.defaultdict(dict)
    for t in icit_texts():
        s = t['seq']
        for i in range(1, len(s)):
            if s[i - 1] in W_TALL and s[i] not in W_TALL and s[i] not in ('#', '|'):
                heads[s[i]][' '.join(s)] = W_TALL[s[i - 1]]
    ent = {}
    for h, d in heads.items():
        if len(d) >= 10:
            c = collections.Counter(d.values()); n = sum(c.values())
            ent[h] = (n, round(-sum(v / n * math.log2(v / n) for v in c.values()), 3), dict(sorted(c.items())))
    res['entropy_by_head'] = dict(sorted(ent.items(), key=lambda kv: -kv[1][1]))

    # power
    res['power'] = dict(
        Q1_rho0_3=power_spearman([u['N'] for u in U], [u['strat'] for u in U]),
        Q2_rho0_3=power_spearman([u['N'] for u in ids], [u['strat'] for u in ids], alt='two'),
        Q3_plant30pct=power_lot(units))
    print('power', res['power'])
    json.dump(res, open(os.path.join(HERE, 'l2_results.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
