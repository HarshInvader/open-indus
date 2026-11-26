"""Red team: which implementation choices move p? Exploratory. Args: nperm seed"""
import sys, json, collections
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import rt

def strata_v(pool, tie, small):
    by = collections.defaultdict(list)
    for i, p in enumerate(pool): by[p['site']].append(i)
    st = [None] * len(pool)
    for s, idx in by.items():
        known = [i for i in idx if pool[i]['area']]
        cuts = np.quantile([pool[i]['area'] for i in known], [1/3, 2/3]) if len(known) >= (3 if small else 1) else None
        for i in idx:
            a = pool[i]['area']
            st[i] = (s, 'u' if not a else (0 if cuts is None else int(np.searchsorted(cuts, a, side=tie))))
    return st

nperm, seed = int(sys.argv[1]), int(sys.argv[2])
out = {}
for multi in ('first', 'concat'):
    pool = rt.load(multi); S, M, w, df = rt.matrices(pool); lab, names = rt.hands(pool)
    for tie in ('right', 'left'):
        st = strata_v(pool, tie, True)
        r, _ = rt.perm_test(lab, S * M, M, len(names), st, nperm, seed)
        sizes = collections.Counter(st)
        r['strata'] = len(sizes)
        out[f'{multi}|tie_{tie}'] = r
        print(multi, tie, json.dumps(r), flush=True)
