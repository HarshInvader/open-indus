"""Stage 3 summary and verdict per PREREG_STAGE3.md."""
import json, os, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(H, '..', 'out')
def load(d, L): return [json.load(open(f'{O}/{d}/{L}_real_{s}.json'))['heldout'] - json.load(open(f'{O}/{d}/{L}_null_{s}.json'))['heldout'] for s in range(10)]
def meta(d, L, k): return st.mean(json.load(open(f'{O}/{d}/{L}_real_{s}.json'))[k] for s in range(10))
T = load('T0', 'tamil'); res = {}
langs = [('T0', 'tamil'), ('T0', 'sanskrit'), ('T4_japanese', 'japanese'), ('T5_sumerian', 'sumerian'), ('T5_egyptian', 'egyptian'), ('T5_finnish', 'finnish')]
for d, L in langs:
    D = load(d, L); m = st.mean(D); above = sum(x > 0 for x in D); ahead = sum(a > t for a, t in zip(D, T))
    v = 'fits like Tamil' if m >= 111.5 and above >= 8 else 'partial fit' if (m >= 111.5) or (m > 0 and above >= 8) else 'no fit'
    res[L] = {'D': round(m, 1), 'sd': round(st.stdev(D), 1), 'above': above, 'ahead_of_tamil': ahead, 'per_seed': [round(x, 1) for x in D],
              'pic_opts': round(meta(d, L, 'pic_mean_opts'), 2), 'signs_read': round(meta(d, L, 'read'), 1), 'verdict': v if L != 'tamil' else ''}
    print(f"{L:9} D {m:+7.1f} ± {st.stdev(D):5.1f}  above {above}/10  ahead of Tamil {ahead}/10  opts {res[L]['pic_opts']}  read {res[L]['signs_read']}  {res[L]['verdict']}")
new = ['sumerian', 'egyptian', 'finnish']
if any(res[L]['verdict'] == 'fits like Tamil' for L in new): pv = 'The contest does not single out Tamil'
elif all(res[L]['ahead_of_tamil'] <= 3 for L in new + ['japanese']): pv = 'The contest picks out Tamil within this panel'
else: pv = 'Mixed'
print('PANEL:', pv); res['panel_verdict'] = pv
json.dump(res, open(f'{O}/T5_summary.json', 'w'), indent=1)
