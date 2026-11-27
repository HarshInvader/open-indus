"""Stage 4a summary per PREREG_STAGE4A.md."""
import json, os, statistics as st
O = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')
def D(d, L): return [json.load(open(f'{O}/{d}/{L}_real_{s}.json'))['heldout'] - json.load(open(f'{O}/{d}/{L}_null_{s}.json'))['heldout'] for s in range(10)]
def M(d, L, k): return st.mean(json.load(open(f'{O}/{d}/{L}_real_{s}.json'))[k] for s in range(10))
T = D('T0', 'tamil'); res = {}
for d, L in [('T0', 'tamil'), ('T6_6a', 'tamil6a'), ('T6_6b', 'tamil6b'), ('T6_6c', 'tamil6c')]:
    x = D(d, L); m = st.mean(x)
    res[L] = dict(D=round(m, 1), sd=round(st.stdev(x), 1), above=sum(v > 0 for v in x), ahead=sum(a > t for a, t in zip(x, T)),
                  opts=round(M(d, L, 'pic_mean_opts'), 2), read=round(M(d, L, 'read'), 1), names=json.load(open(f'{O}/{d}/{L}_real_0.json'))['names'], seeds=[round(v) for v in x])
    print(L, res[L])
m = res['tamil6a']['D']
res['verdict_6a'] = "Spelling explains most of Tamil's lead over Japanese" if m <= 134.5 else 'Spelling explains little' if m >= 178.4 else 'Spelling explains part'
print(res['verdict_6a']); json.dump(res, open(f'{O}/T6_summary.json', 'w'), indent=1)
