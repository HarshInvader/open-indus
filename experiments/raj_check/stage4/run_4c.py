"""Stage 4c (T8) C1-C7, as PREREG_STAGE4C.md. Builds config-only inputs, runs Raj's contest.py unchanged, writes out/T8_summary.json."""
import json, os, subprocess, sys, itertools, statistics as st
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); I = os.path.join(H, 'inputs'); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
sys.path.insert(0, os.path.join(W, 'code_surviving')); import nphon
SURV = os.path.join(W, 'inputs_surviving')
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
def wl(p, rows):
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
PN = jl(os.path.join(SURV, 'names_model_clean.jsonl')); FN = jl(os.path.join(I, 'names_tamil4b.jsonl'))
PP = jl(os.path.join(SURV, 'morphemes.jsonl')); FP = jl(os.path.join(I, 'parts_tamil4b.jsonl'))
pset = {r['name'] for r in PN}; fset = {r['name'] for r in FN}; shared = pset & fset
print('shared', len(shared), 'paper-only', len(pset - shared), 'fresh-only', len(fset - shared))
plab = {nphon.norm(x['m']): x for x in PP}
merged = [dict(x, category=plab[nphon.norm(x['m'])]['category'], stability=plab[nphon.norm(x['m'])].get('stability', x['stability'])) if nphon.norm(x['m']) in plab else x for x in FP]
wl(os.path.join(I, 'parts_tamil4c_c3.jsonl'), merged)
P_N, P_P = '../../work/REP1/inputs_surviving/names_model_clean.jsonl', '../../work/REP1/inputs_surviving/morphemes.jsonl'
F_P = 'parts_tamil4b.jsonl'
for tag, rows in (('c1', [r for r in PN if r['name'] in shared]), ('c2', [r for r in FN if r['name'] in shared]),
                  ('c6', [r for r in PN if r['name'] not in shared]), ('c7', [r for r in FN if r['name'] not in shared])):
    wl(os.path.join(I, f'names_tamil4c_{tag}.jsonl'), rows)
base = json.load(open(os.path.join(I, 'cfg_tamil4b.json'), encoding='utf-8'))
base['words'] = '../../work/REP1/inputs/words_tamil_new.json'
END = ['tiru', 'aiyaṉ', 'ār', 'ar', 'aṉ', 'āṉ', 'aḷ']
C = {'c1': dict(names='names_tamil4c_c1.jsonl', parts=P_P), 'c2': dict(names='names_tamil4c_c2.jsonl', parts=F_P),
     'c3': dict(names='names_tamil4c_c2.jsonl', parts='parts_tamil4c_c3.jsonl'), 'c4': dict(names='names_tamil4b.jsonl', parts=F_P, drop_parts=END),
     'c5': dict(names=P_N, parts=P_P, drop_parts=END), 'c6': dict(names='names_tamil4c_c6.jsonl', parts=P_P), 'c7': dict(names='names_tamil4c_c7.jsonl', parts=F_P)}
for t, c in C.items(): json.dump(dict(base, lang=f'tamil4c_{t}', **c), open(os.path.join(I, f'cfg_tamil4c_{t}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if len(sys.argv) > 1 and sys.argv[1] == 'build': sys.exit()
jobs = [(t, s, m) for t in C for s, m in itertools.product(range(10), ('real', 'null'))]
def run(j):
    t, s, m = j
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(I, f'cfg_tamil4c_{t}.json'), str(s), m, f'{O}/T8_{t}'],
                       cwd=W, env=dict(os.environ, RAJ_SURV=os.path.join(W, 'code_surviving')), capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-600:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
print('failed', sum(1 for x in rc if x))
out = {}
for t in C:
    d, o, rd, nm = [], [], [], None
    for s in range(10):
        R = json.load(open(f'{O}/T8_{t}/tamil4c_{t}_real_{s}.json')); N = json.load(open(f'{O}/T8_{t}/tamil4c_{t}_null_{s}.json'))
        d.append(R['heldout'] - N['heldout']); o.append(R['pic_mean_opts']); rd.append(R['read']); nm = R['names']
    out[t] = {'D': round(st.mean(d), 1), 'sd': round(st.stdev(d), 1), 'above': sum(x > 0 for x in d), 'opts': round(st.mean(o), 2), 'read': round(st.mean(rd), 1), 'names': nm, 'seeds': [round(x) for x in d]}
    print(t, out[t])
def rd(a, b, hi, lo): x = out[a]['D'] - out[b]['D']; return round(x, 1), (hi if x >= 100 else lo if abs(x) < 50 else 'unclear')
c4 = out['c4']['D']
out['readings'] = {'segmentation C1-C2': rd('c1', 'c2', 'how names are cut matters', 'does not matter'),
                   'endings C4': 'the endings explain the low score' if c4 >= 178.4 else 'they do not' if c4 <= 111.5 else 'partly',
                   'selection C6-C7': rd('c6', 'c7', 'which names are chosen matters', 'does not matter')}
print(out['readings'])
json.dump(out, open(f'{O}/T8_summary.json', 'w'), ensure_ascii=False, indent=1)
