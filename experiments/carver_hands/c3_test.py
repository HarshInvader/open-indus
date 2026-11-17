"""C3: pre-registered test (docs/prereg/carver_hands.md): do seals of one carving style share frame
slots (opener/title/closer) or core slots more than chance?
Run: .venv/bin/python -I experiments/carver_hands/c3_test.py   -> c3.json, c3.log (stdout)
"""
import os, sys, csv, json, hashlib, collections as C
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(D))
RNG = np.random.default_rng(20261115)
NPERM = 2000
EPS = 1e-3
SLOTS = ['opener', 'title', 'closer', 'numeral', 'core']
FRAME = ['opener', 'title', 'closer']

# ---------- roles ----------
BR = json.load(open(os.path.join(REPO, 'sources/shaunmortal_indus/data/bridge_WM.json')))
LEX = {}
for r in csv.DictReader(open(os.path.join(REPO, 'experiments/functional_reading/lexicon.csv'))):
    if r['kind'] != 'sign' or not r['roles'].strip():
        continue
    rs = [x.strip().rsplit(' ', 1) for x in r['roles'].split(';') if x.strip()]
    role = max(rs, key=lambda t: float(t[1]))[0]
    LEX[r['item']] = (role, int(r['dev_texts'] or 0))


def role(w):
    b = BR.get(str(int(w[1:])))
    if not b:
        return 'NOUN'
    c = [LEX[f'M{m}'] for m in b['M'] if f'M{m}' in LEX]
    return max(c, key=lambda t: t[1])[0] if c else 'NOUN'


OPEN = {'OPENER', 'CONNECTIVE'}
CLOSE = {'CLOSER', 'POST-CLOSER CLITIC', 'BRACKETED-FISH CLOSER'}
NUM = {'NUMERAL(short)', 'NUMERAL(tall)', 'UNIT/MEASURE'}


def slots(signs):
    rl = [role(s) for s in signs]
    i = 0
    while i < len(signs) and rl[i] in OPEN:
        i += 1
    j = len(signs)
    while j > i and rl[j - 1] in CLOSE:
        j -= 1
    out = dict(opener=tuple(signs[:i]), closer=tuple(signs[j:]), title=(), numeral=(), core=())
    t, n, c = [], [], []
    for s, r in zip(signs[i:j], rl[i:j]):
        (t if r == 'TITLE ELEMENT' else n if r in NUM else c).append(s)
    out.update(title=tuple(t), numeral=tuple(n), core=tuple(c))
    return out


def size_group(w):
    w = float(w or 0)
    for g, lo in [('I', 43.5), ('II', 35), ('III', 29), ('IV', 23), ('V', 17.5)]:
        if w >= lo: return g
    return 'VI' if w > 0 else 'NA'


# ---------- engine ----------
def codes(texts):
    S = [slots(t) for t in texts]
    V = {}
    for s in SLOTS:
        vocab = {}
        V[s] = np.array([-1 if not x[s] else vocab.setdefault(x[s], len(vocab)) for x in S])
    return V, S


def stat(V, perm, I, J, within):
    """returns dict slot -> (ident_within, both_within, ident_between, both_between)"""
    out = {}
    for s in SLOTS:
        v = V[s][perm]
        a, b = v[I], v[J]
        both = (a >= 0) & (b >= 0)
        ide = both & (a == b)
        out[s] = (ide[within].sum(), both[within].sum(), ide[~within].sum(), both[~within].sum())
    return out


def excess(c, slots_):
    iw = sum(c[s][0] for s in slots_); bw = sum(c[s][1] for s in slots_)
    ib = sum(c[s][2] for s in slots_); bb = sum(c[s][3] for s in slots_)
    rw = iw / bw if bw else 0.0; rb = ib / bb if bb else 0.0
    return float(np.log((rw + EPS) / (rb + EPS))), rw, rb


def summarize(c):
    E = {s: excess(c, [s]) for s in SLOTS}
    EF = excess(c, FRAME); EC = E['core']
    return dict(delta=EF[0] - EC[0], E_F=EF[0], E_C=EC[0], rates={k: (v[1], v[2]) for k, v in E.items()},
                rate_frame=(EF[1], EF[2]), E={k: v[0] for k, v in E.items()})


def strat_perm(strata):
    p = np.arange(len(strata))
    for s in set(strata):
        ii = np.where(strata == s)[0]
        p[ii] = ii[RNG.permutation(len(ii))]
    return p


def run(name, texts, strata, within_fn, n, nperm=NPERM, V=None):
    if V is None:
        V, _ = codes(texts)
    I, J = np.triu_indices(n, 1)
    within = within_fn(I, J)
    obs = summarize(stat(V, np.arange(n), I, J, within))
    nd, nf, nc, nsl = [], [], [], {s: [] for s in SLOTS}
    for _ in range(nperm):
        sm = summarize(stat(V, strat_perm(strata), I, J, within))
        nd.append(sm['delta']); nf.append(sm['E_F']); nc.append(sm['E_C'])
        for s in SLOTS: nsl[s].append(sm['E'][s])
    nd, nf, nc = map(np.array, (nd, nf, nc))
    res = dict(n=int(n), pairs_within=int(within.sum()), obs=obs,
               p_delta_two=float(min(1, 2 * min((nd >= obs['delta']).mean(), (nd <= obs['delta']).mean())) + 1 / nperm),
               p_EF=float((nf >= obs['E_F']).mean() + 1 / nperm), p_EC=float((nc >= obs['E_C']).mean() + 1 / nperm),
               null_delta_mean=float(nd.mean()), null_delta_sd=float(nd.std()),
               p_slot={s: float((np.array(nsl[s]) >= obs['E'][s]).mean() + 1 / nperm) for s in SLOTS})
    print(f"\n== {name}: n={n} within-pairs={res['pairs_within']}")
    for s in SLOTS:
        rw, rb = obs['rates'][s]
        print(f"  {s:8s} identical within {rw:.3f} between {rb:.3f}  E={obs['E'][s]:+.2f}  p={res['p_slot'][s]:.3f}")
    print(f"  frame within {obs['rate_frame'][0]:.3f} between {obs['rate_frame'][1]:.3f}")
    print(f"  E_F={obs['E_F']:+.3f} (p {res['p_EF']:.4f})  E_C={obs['E_C']:+.3f} (p {res['p_EC']:.4f})  "
          f"DELTA={obs['delta']:+.3f} (two-sided p {res['p_delta_two']:.4f}; null {nd.mean():+.3f}+-{nd.std():.3f})")
    return res


def power(name, texts, strata, within_fn, groups, n, qs=(0.1, 0.2, 0.3), reps=100):
    """planted: each seal's closer replaced by its group's modal closer with prob q."""
    V0, S = codes(texts)
    out = {}
    for q in qs:
        hits = 0
        for r in range(reps):
            V = {k: v.copy() for k, v in V0.items()}
            for g in set(groups):
                ii = np.where(groups == g)[0]
                cl = [V['closer'][i] for i in ii if V['closer'][i] >= 0]
                if not cl: continue
                mode = C.Counter(cl).most_common(1)[0][0]
                pick = ii[RNG.random(len(ii)) < q]
                V['closer'][pick] = mode
            res = run_quiet(V, strata, within_fn, n)
            hits += res < 0.0125
        out[str(q)] = hits / reps
    print(f"  power {name}: {out}")
    return out


def run_quiet(V, strata, within_fn, n, nperm=200):
    I, J = np.triu_indices(n, 1); within = within_fn(I, J)
    obs = summarize(stat(V, np.arange(n), I, J, within))['delta']
    nd = np.array([summarize(stat(V, strat_perm(strata), I, J, within))['delta'] for _ in range(nperm)])
    return min(1, 2 * min((nd >= obs).mean(), (nd <= obs).mean())) + 1 / nperm


def main():
    icit = {r['id']: r for r in (json.loads(l) for l in open(os.path.join(REPO, 'data/icit_texts.jsonl')))}
    OUT = {}
    # ---- P1 / P2 image ----
    CL = list(csv.DictReader(open(os.path.join(D, 'clusters.csv'))))
    F = np.load(os.path.join(D, 'work', 'features.npz'))
    R = F['R']; assert len(R) == len(CL)
    texts = [[s for s in icit[c['icit_id']]['seq'] if s not in ('|', '#')] for c in CL]
    strata = np.array([f"{c['site']}|{c['size_group']}" for c in CL])
    lab = np.array([int(c['cluster']) for c in CL])
    n = len(CL)
    Rn = R / np.linalg.norm(R, axis=1, keepdims=True)
    S = Rn @ Rn.T; np.fill_diagonal(S, -9)
    nn = np.argsort(-S, axis=1)[:, :5]
    near = np.zeros((n, n), bool)
    for i in range(n):
        near[i, nn[i]] = True
    near = near | near.T
    OUT['P1_knn'] = run('P1 image kNN(5) near pairs', texts, strata, lambda I, J: near[I, J], n)
    OUT['P2_clusters'] = run('P2 image clusters K=10', texts, strata, lambda I, J: lab[I] == lab[J], n)
    OUT['P2_clusters']['power'] = power('P2', texts, strata, lambda I, J: lab[I] == lab[J], lab, n)
    # P1 power with groups = clusters (closer planted by cluster; near pairs are mostly within cluster?)
    OUT['P1_knn']['near_pairs_same_cluster'] = float(np.mean([lab[i] == lab[j] for i, j in zip(*np.where(np.triu(near, 1)))]))
    OUT['P1_knn']['power'] = power('P1', texts, strata, lambda I, J: near[I, J], lab, n)
    # ---- P3 style letter ----
    U = [r for r in icit.values() if r['type'] == 'SEAL:S' and r['symbol'].startswith('Bull1:') and r['complete']
         and '|' not in r['seq'] and '#' not in r['seq'] and float(r['width_mm'] or 0) > 0]
    t3 = [r['seq'] for r in U]
    s3 = np.array([f"{r['site']}|{size_group(r['width_mm'])}" for r in U])
    l3 = np.array([r['symbol'].split(':')[1] for r in U])
    OUT['P3_letter'] = run('P3 ICIT unicorn style letter', t3, s3, lambda I, J: l3[I] == l3[J], len(U))
    OUT['P3_letter']['power'] = power('P3', t3, s3, lambda I, J: l3[I] == l3[J], l3, len(U))
    # ---- P4 W705 vs W706 ----
    U4 = [r for r in icit.values() if r['type'] == 'SEAL:S' and r['symbol'].startswith('Bull1')
          and ('W705' in r['seq']) != ('W706' in r['seq']) and '#' not in r['seq']]
    t4 = [[s for s in r['seq'] if s not in ('|', 'W705', 'W706')] for r in U4]
    s4 = np.array([f"{r['site']}|{size_group(r['width_mm'])}" for r in U4])
    l4 = np.array(['706' if 'W706' in r['seq'] else '705' for r in U4])
    OUT['P4_w705_w706'] = run('P4 W705 vs W706 carriers', t4, s4, lambda I, J: l4[I] == l4[J], len(U4))
    OUT['P4_w705_w706']['variant_counts'] = dict(C.Counter(l4.tolist()))
    # bonferroni verdict
    OUT['bonferroni_alpha'] = 0.0125
    json.dump(OUT, open(os.path.join(D, 'c3.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
