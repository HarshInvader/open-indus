"""Run T0 (their contest.py, unchanged) and T1/T2 (contest_ctl.py) for raj_check. nice 20, 4 processes."""
import os, subprocess, sys, itertools
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
SURV = os.path.join(W, 'code_surviving')
jobs = []
for lang in ('tamil', 'sanskrit'):
    for seed, mode in itertools.product(range(10), ('real', 'null')):
        jobs.append((['code/contest.py', f'inputs/cfg_headline_{lang}.json'], seed, mode, f'{O}/T0', {}))
for p in range(1, 51):
    for seed, mode in itertools.product(range(10), ('real', 'null')):
        jobs.append((['../../code/contest_ctl.py', 'inputs/cfg_headline_tamil.json'], seed, mode, f'{O}/T1/perm{p}', {'CTL_PERM': str(p)}))
for kind in ('order', 'iid'):
    for f in range(1, 21):
        for seed, mode in itertools.product(range(10), ('real', 'null')):
            jobs.append((['../../code/contest_ctl.py', 'inputs/cfg_headline_tamil.json'], seed, mode, f'{O}/T2_{kind}/fake{f}', {'CTL_FAKE': f'{kind}:{f}'}))
def run(j):
    (script, cfg), seed, mode, out, env = j
    if os.path.exists(f"{out}/tamil_{mode}_{seed}.json") and 'T0' not in out: return 0
    e = dict(os.environ, RAJ_SURV=SURV, **env)
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', script, cfg, str(seed), mode, out], cwd=W, env=e, capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-500:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
print('jobs', len(jobs), 'failed', sum(1 for x in rc if x))
