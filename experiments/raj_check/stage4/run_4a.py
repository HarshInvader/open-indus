"""Stage 4a (T6): Raj's contest.py, unchanged, on Tamil on equal terms. nice 20, 4 processes."""
import os, subprocess, sys, itertools
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
SURV = os.path.join(W, 'code_surviving')
jobs = [(L, s, m) for L in ('6a', '6b', '6c') for s, m in itertools.product(range(10), ('real', 'null'))]
def run(j):
    L, seed, mode = j
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(H, 'inputs', f'cfg_{L}.json'), str(seed), mode, f'{O}/T6_{L}'],
                       cwd=W, env=dict(os.environ, RAJ_SURV=SURV), capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-800:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
print('jobs', len(jobs), 'failed', sum(1 for x in rc if x))
