"""Stage 4b (T7): Raj's contest.py, unchanged, on one Dravidian list. nice 20, 4 processes.
  python3 -I stage4/run_4b.py <lang> [meaningfirst|paperwords]   (paperwords: tamilf with the paper's picture words, T8b second run; after build_4b.py final <lang> and a commit of the inputs)"""
import os, subprocess, sys, itertools
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
SURV = os.path.join(W, 'code_surviving'); L = sys.argv[1]; tag = f'{L}4b' + ({'meaningfirst': 'm', 'paperwords': 'p'}[sys.argv[2]] if len(sys.argv) > 2 else '')
jobs = list(itertools.product(range(10), ('real', 'null')))
def run(j):
    seed, mode = j
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(H, 'inputs', f'cfg_{tag}.json'), str(seed), mode, f'{O}/T7_{tag}'],
                       cwd=W, env=dict(os.environ, RAJ_SURV=SURV), capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-800:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
print(tag, 'jobs', len(jobs), 'failed', sum(1 for x in rc if x))
