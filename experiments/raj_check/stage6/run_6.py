"""Stage 6 (T10): Raj's contest.py, unchanged, on the Brahui list. nice 20, 4 processes.
  python3 -I stage6/run_6.py [meaningfirst]   -> out/T10_brahui6{,m}/, out/T10_summary.json (after build_6.py final and a commit of the inputs)"""
import os, subprocess, sys, itertools, json, statistics as st
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
SURV = os.path.join(W, 'code_surviving'); tag = 'brahui6' + ('m' if len(sys.argv) > 1 else ''); out = f'{O}/T10_{tag}'
def run(j):
    seed, mode = j
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(H, 'inputs', f'cfg_{tag}.json'), str(seed), mode, out],
                       cwd=W, env=dict(os.environ, RAJ_SURV=SURV), capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-800:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, itertools.product(range(10), ('real', 'null'))))
if any(rc): sys.exit('failed')
R = [json.load(open(f'{out}/{tag}_real_{s}.json')) for s in range(10)]
x = [R[s]['heldout'] - json.load(open(f'{out}/{tag}_null_{s}.json'))['heldout'] for s in range(10)]
rd = lambda r: len(r) if not isinstance(r, (int, float)) else r
res = {'names': R[0]['names'], 'D': round(st.mean(x), 1), 'sd': round(st.stdev(x), 1), 'above': sum(v > 0 for v in x), 'opts': round(st.mean(r['pic_mean_opts'] for r in R), 2),
       'read': round(st.mean(rd(r['read']) for r in R), 1), 'seeds': [round(v, 1) for v in x]}
res['reading'] = ('void' if res['read'] < 5 else 'Brahui fits the seals like the paper\'s Tamil' if res['D'] >= 111.5 and res['above'] >= 8 else 'Brahui does not')
p = os.path.join(O, 'T10_summary.json'); allr = json.load(open(p)) if os.path.exists(p) else {}; allr[tag] = res
json.dump(allr, open(p, 'w'), indent=1); print(tag, res)
