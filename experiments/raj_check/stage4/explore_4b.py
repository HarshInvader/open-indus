"""Stage 4b, EXPLORATORY (not preregistered), run after the fresh Tamil result was seen.
Why does a fresh Old Tamil list score ~0 when the paper's scores +223? Two differences: the names and the picture words.
  X1 fresh names + the paper's Tamil picture words
  X2 the paper's names + the fresh picture words
  X3 fresh names resampled to the paper's mix of name types (47% people): all non-person names + random persons, 5 subsets
Raj's contest.py unchanged, seeds 0-9, real and null, nice 20, 4 processes. Outputs out/T7x_<tag>."""
import json, os, random, subprocess, sys, itertools, statistics as st
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); I = os.path.join(H, 'inputs'); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out')
base = json.load(open(os.path.join(I, 'cfg_tamil4b.json'), encoding='utf-8'))
cfgs = {}
c = dict(base, lang='tamil4b_x1', words='../../work/REP1/inputs/words_tamil_new.json'); cfgs['tamil4b_x1'] = c
c = dict(base, lang='tamil4b_x2', names='../../work/REP1/inputs_surviving/names_model_clean.jsonl', parts='../../work/REP1/inputs_surviving/morphemes.jsonl'); cfgs['tamil4b_x2'] = c
names = [json.loads(l) for l in open(os.path.join(I, 'names_tamil4b.jsonl'), encoding='utf-8')]
non = [r for r in names if r['type'] != 'person']; per = [r for r in names if r['type'] == 'person']
k = round(len(non) * 532 / (1125 - 532))
for i in range(1, 6):
    sub = non + random.Random(f'x3-{i}').sample(per, k)
    fn = f'names_tamil4b_x3_{i}.jsonl'
    with open(os.path.join(I, fn), 'w', encoding='utf-8') as f:
        for r in sub: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    cfgs[f'tamil4b_x3_{i}'] = dict(base, lang=f'tamil4b_x3_{i}', names=fn)
for t, c in cfgs.items(): json.dump(c, open(os.path.join(I, f'cfg_{t}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('X3 subset size', len(non) + k, 'non-person', len(non), 'persons', k)
jobs = [(t, s, m) for t in cfgs for s, m in itertools.product(range(10), ('real', 'null'))]
def run(j):
    t, s, m = j
    r = subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(I, f'cfg_{t}.json'), str(s), m, f'{O}/T7x_{t}'],
                       cwd=W, env=dict(os.environ, RAJ_SURV=os.path.join(W, 'code_surviving')), capture_output=True, text=True)
    if r.returncode: print('FAIL', j, r.stderr[-600:], flush=True)
    return r.returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
print('failed', sum(1 for x in rc if x))
out = {}
for t in cfgs:
    d, o, rd = [], [], []
    for s in range(10):
        R = json.load(open(f'{O}/T7x_{t}/{t}_real_{s}.json')); N = json.load(open(f'{O}/T7x_{t}/{t}_null_{s}.json'))
        d.append(R['heldout'] - N['heldout']); o.append(R['pic_mean_opts']); rd.append(R['read'] if isinstance(R['read'], (int, float)) else len(R['read']))
    out[t] = {'D': round(st.mean(d), 1), 'sd': round(st.stdev(d), 1), 'above': sum(x > 0 for x in d), 'opts': round(st.mean(o), 2), 'read': round(st.mean(rd), 1), 'seeds': [round(x) for x in d]}
    print(t, out[t])
json.dump(out, open(f'{O}/T7x_summary.json', 'w'), indent=1)
