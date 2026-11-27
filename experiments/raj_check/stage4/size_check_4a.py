"""Stage 4a, exploratory (not preregistered): is the people-only collapse about kind of name or list size?
10 random subsets of 532 names from Raj's full Tamil list (all kinds), original spelling, seeds 0-9 each."""
import json, os, random, subprocess, sys, itertools, statistics as st
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, '..', 'work', 'REP1'); O = os.path.join(H, '..', 'out'); I = os.path.join(H, 'inputs')
names = [l for l in open(os.path.join(W, 'inputs_surviving', 'names_model_clean.jsonl'), encoding='utf-8')]
cfg0 = json.load(open(os.path.join(I, 'cfg_6b.json'), encoding='utf-8'))
for k in range(1, 11):
    sub = random.Random(20261127 + k).sample(names, 532)
    open(os.path.join(I, f'names_sz{k}.jsonl'), 'w', encoding='utf-8').writelines(sub)
    json.dump(dict(cfg0, lang=f'tamilsz{k}', names=f'names_sz{k}.jsonl'), open(os.path.join(I, f'cfg_sz{k}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
jobs = [(k, s, m) for k in range(1, 11) for s, m in itertools.product(range(10), ('real', 'null'))]
def run(j):
    k, s, m = j
    return subprocess.run(['nice', '-n', '20', sys.executable, '-I', 'code/contest.py', os.path.join(I, f'cfg_sz{k}.json'), str(s), m, f'{O}/T6_size/sz{k}'],
                          cwd=W, env=dict(os.environ, RAJ_SURV=os.path.join(W, 'code_surviving')), capture_output=True).returncode
with ThreadPoolExecutor(4) as ex: rc = list(ex.map(run, jobs))
out = []
for k in range(1, 11):
    x = [json.load(open(f'{O}/T6_size/sz{k}/tamilsz{k}_real_{s}.json'))['heldout'] - json.load(open(f'{O}/T6_size/sz{k}/tamilsz{k}_null_{s}.json'))['heldout'] for s in range(10)]
    kinds = {}
    for l in open(os.path.join(I, f'names_sz{k}.jsonl'), encoding='utf-8'): t = json.loads(l)['type']; kinds[t] = kinds.get(t, 0) + 1
    out.append({'subset': k, 'D': round(st.mean(x), 1), 'above': sum(v > 0 for v in x), 'people': kinds.get('person', 0)})
    print(out[-1])
Ds = [o['D'] for o in out]
print('failed', sum(1 for r in rc if r), '| median D over subsets', round(st.median(Ds), 1), 'range', min(Ds), max(Ds), '| subsets with D <= people-only (2.9):', sum(d <= 2.9 for d in Ds))
json.dump(out, open(f'{O}/T6_size_summary.json', 'w'), indent=1)
