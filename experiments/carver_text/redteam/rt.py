"""Independent red-team reimplementation of the carver_text test, written from the prereg text only."""
import json, math, sys, collections
import numpy as np

import os; ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')) + '/'

def lev(a, b):
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def contained(a, b):
    if len(a) > len(b): a, b = b, a
    n = len(a)
    return any(b[i:i + n] == a for i in range(len(b) - n + 1))

def load(multi='concat'):
    d = json.load(open(ROOT + 'experiments/carver_text/out/seals.json'))
    pool = []
    for r in d:
        if not r['icit']: continue
        rows = r['icit']
        if multi == 'concat':
            seq = [s for x in rows for s in x['seq']]
        elif multi == 'first':
            seq = list(rows[0]['seq'])
        if not seq: continue
        def area(x):
            try: return float(x['width_mm']) * float(x['height_mm'])
            except Exception: return None
        ar = next((area(x) for x in rows if area(x)), None)
        pool.append(dict(id=r['id'], jsite=r['site'], site=rows[0]['site'], group=r['group'], seq=seq,
                         area=ar, rows=rows, attrs=r['attrs']))
    return pool

def strata(pool, key='site'):
    by = collections.defaultdict(list)
    for i, p in enumerate(pool):
        if p['area'] is not None: by[p[key]].append(i)
    st = [None] * len(pool)
    for s, idx in by.items():
        a = np.array([pool[i]['area'] for i in idx])
        q1, q2 = np.quantile(a, [1 / 3, 2 / 3])
        for i in idx:
            v = pool[i]['area']
            st[i] = (s, 0 if v <= q1 else (1 if v <= q2 else 2))
    for i, p in enumerate(pool):
        if st[i] is None: st[i] = (p[key], 'unk')
    return st

def matrices(pool, nc_rule=True):
    N = len(pool)
    sets = [set(p['seq']) for p in pool]
    df = collections.Counter(s for S in sets for s in S)
    w = {s: math.log(N / c) for s, c in df.items()}
    S = np.zeros((N, N)); M = np.ones((N, N)); np.fill_diagonal(M, 0)
    for i in range(N):
        for j in range(i + 1, N):
            S[i, j] = S[j, i] = sum(w[s] for s in sets[i] & sets[j])
            if nc_rule:
                a, b = pool[i]['seq'], pool[j]['seq']
                if lev(a, b) <= 1 or contained(a, b):
                    M[i, j] = M[j, i] = 0
    return S, M, w, df

def hands(pool, minsize=2):
    c = collections.Counter(p['group'] for p in pool if p['group'] is not None)
    names = sorted(g for g, n in c.items() if n >= minsize)
    gi = {g: k for k, g in enumerate(names)}
    lab = np.array([gi.get(p['group'], -1) for p in pool])
    return lab, names

def stat(lab, W, M, K):
    H = np.zeros((len(lab), K)); m = lab >= 0
    H[np.nonzero(m)[0], lab[m]] = 1
    num = (H * (W @ H)).sum() / 2; den = (H * (M @ H)).sum() / 2
    return num / den, den

def perm_test(lab, W, M, K, st, nperm, seed):
    rng = np.random.default_rng(seed)
    groups = collections.defaultdict(list)
    for i, s in enumerate(st): groups[s].append(i)
    groups = [np.array(v) for v in groups.values() if len(v) > 1]
    obs, npairs = stat(lab, W, M, K)
    null = np.empty(nperm)
    for b in range(nperm):
        L = lab.copy()
        for g in groups: L[g] = lab[rng.permutation(g)]
        null[b] = stat(L, W, M, K)[0]
    ge = int((null >= obs - 1e-12).sum())
    return dict(obs=obs, pairs=int(npairs), null_mean=float(null.mean()), ge=ge, p=(ge + 1) / (nperm + 1), nperm=nperm), null

if __name__ == '__main__':
    nperm = int(sys.argv[1]); seed = int(sys.argv[2])
    pool = load(); st = strata(pool); S, M, w, df = matrices(pool); lab, names = hands(pool)
    r, _ = perm_test(lab, S * M, M, len(names), st, nperm, seed)
    r.update(pool=len(pool), hands=len(names), grouped=int((lab >= 0).sum()), strata=len(set(st)), seed=seed)
    print(json.dumps(r))
