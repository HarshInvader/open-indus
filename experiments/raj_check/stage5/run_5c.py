"""Stage 5c V3 (PREREG_STAGE5C.md): python3 -I stage5/run_5c.py
From the V2 pool, local search for 1,125 names maximising mean D on seal half A (seeds 0-4), start = V2, 1,500 single swaps, seed 3.
Writes inputs/names_jsym_v3.jsonl, parts_jsym_v3.jsonl (= V2 parts), search_log_v3.json. Then run: python3 -I stage5/run_5b.py jsym_v3"""
import json, os, sys, runpy, random, shutil, tempfile, statistics as st
sys.argv = ['x', 'none']
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_5.py'))
H, I, J2, JCFG, jl, wjl = g['H'], g['I'], g['J2'], g['JCFG'], g['jl'], g['wjl']
sys.path.insert(0, os.path.join(H, '..', 'work', 'REP1', 'code_surviving')); import nphon
A = os.path.join(H, 'agents')
pool = jl(os.path.join(A, 'names_jsym.jsonl')) + jl(os.path.join(A, 'names_jsym3.jsonl'))
seen = set(); pool = [r for r in pool if not (r['name'] in seen or seen.add(r['name']))]
pool = [r for r in pool if any(p.get('origin') == 'native' and nphon.norm(p['m']) for p in r['parts'])]
rows = [{'name': r['name'], 'type': r.get('type'), 'morphemes': [p['m'] for p in r['parts']], 'weight': 1} for r in pool]
idx = {r['name']: i for i, r in enumerate(rows)}; N = len(rows)
cur = {idx[r['name']] for r in jl(os.path.join(I, 'names_jsym_v2.jsonl'))}
shutil.copy(os.path.join(I, 'parts_jsym_v2.jsonl'), os.path.join(I, 'parts_jsym_v3.jsonl'))
base = dict(JCFG, parts=os.path.join(I, 'parts_jsym_v3.jsonl'))
tmp = tempfile.mkdtemp(prefix='t9c_'); rnd = random.Random(3)
def obj(sel):
    p = os.path.join(tmp, 'names.jsonl'); wjl(p, [rows[i] for i in sorted(sel)])
    return st.mean(g['D'](g['cfg'](base, J2, p, os.path.join(I, 'corpus_A.csv'), 'jv3', tmp), 'jv3', range(5), tmp))
best = obj(cur); log = [(0, best)]; print('pool', N, 'start', round(best, 1), flush=True)
for it in range(1, 1501):
    a = rnd.choice(sorted(cur)); b = rnd.choice(sorted(set(range(N)) - cur))
    cand = (cur - {a}) | {b}; v = obj(cand)
    if v > best: cur, best = cand, v; log.append((it, best))
    if it % 50 == 0: print(it, round(best, 1), flush=True)
wjl(os.path.join(I, 'names_jsym_v3.jsonl'), [rows[i] for i in sorted(cur)])
json.dump({'pool': N, 'start': log[0][1], 'final': best, 'accepted': log}, open(os.path.join(H, 'search_log_v3.json'), 'w'), indent=0)
print('final', round(best, 1), 'accepted', len(log) - 1); g['EX'].shutdown()
