"""Stage 5b runs: python3 -I stage5/run_5b.py jsym1|jsym2  (full corpus and seal half B, seeds 0-9)."""
import json, os, sys, runpy, statistics as st
sys.argv, tag = ['x', 'none'], sys.argv[1]
g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_5.py'))
H, I, O, J2, JCFG, SRC = g['H'], g['I'], g['O'], g['J2'], g['JCFG'], g['SRC']
names = os.path.join(I, f'names_{tag}.jsonl'); parts = JCFG['parts']
base = dict(JCFG)
if os.path.exists(os.path.join(I, f'parts_{tag}.jsonl')): base['parts'] = os.path.abspath(os.path.join(I, f'parts_{tag}.jsonl'))
res = {}
for c, corpus in (('full', SRC), ('B', os.path.join(I, 'corpus_B.csv'))):
    lab = f'{tag}_{c}'; d = os.path.join(O, 'T9b', lab); os.makedirs(d, exist_ok=True)
    x = g['D'](g['cfg'](base, J2, names, corpus, lab, I), lab, range(10), d)
    r0 = [json.load(open(f'{d}/{lab}_real_{s}.json')) for s in range(10)]
    res[lab] = {'names': r0[0]['names'], 'D': round(st.mean(x), 1), 'median': round(st.median(x), 1), 'sd': round(st.stdev(x), 1), 'above': sum(v > 0 for v in x),
                'opts': round(st.mean(r['pic_mean_opts'] for r in r0), 2), 'read': round(st.mean(r['read'] if isinstance(r['read'], (int, float)) else len(r['read']) for r in r0), 1), 'seeds': [round(v, 1) for v in x]}
    print(lab, res[lab], flush=True)
D = res[f'{tag}_full']['D']; res['reading'] = ('lifts to Tamil level' if D >= 223.0 else 'most of the way' if D >= 111.5 and res[f'{tag}_full']['above'] >= 8 else 'does not')
if tag.startswith('jsym_v'):  # PREREG_STAGE5C readings
    rd = lambda x, t: 'above Tamil' if x['D'] >= t and x['above'] >= 8 else 'level' if abs(x['D'] - t) <= 20 else 'below'
    res['reading'] = {'B': rd(res[f'{tag}_B'], 103.8), 'full': rd(res[f'{tag}_full'], 223.0)}
p = os.path.join(O, 'T9b_summary.json'); allr = json.load(open(p)) if os.path.exists(p) else {}; allr[tag] = res
json.dump(allr, open(p, 'w'), indent=1); print(tag, res['reading']); g['EX'].shutdown()
