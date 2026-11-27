"""Summarise T0-T2 for raj_check -> out/stage1_summary.json"""
import json, os, glob, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(H, '..', 'out')
STORED = os.path.join(H, '..', '..', '..', 'sources', 'raj_zenodo_24383779_v0.7', 'x_tests_archive', 'REP-1_tamil_vs_sanskrit', 'outputs', 'headline')
def J(p): return json.load(open(p))
def D(d, lang='tamil'):
    xs = [J(f'{d}/{lang}_real_{s}.json')['heldout'] - J(f'{d}/{lang}_null_{s}.json')['heldout'] for s in range(10)]
    return st.mean(xs), xs
res = {}
# T0
mism = []
for lang in ('tamil', 'sanskrit'):
    for s in range(10):
        for m in ('real', 'null'):
            a = J(f'{O}/T0/{lang}_{m}_{s}.json')['heldout']; b = J(f'{STORED}/{lang}_{m}_{s}.json')['heldout']
            if abs(a - b) > 0.01: mism.append((lang, m, s, a, b))
dt, xt = D(f'{O}/T0'); ds, xsk = D(f'{O}/T0', 'sanskrit')
res['T0'] = dict(mismatches=mism, tamil_D=round(dt, 1), tamil_sd=round(st.stdev(xt), 1), tamil_above=sum(x > 0 for x in xt),
                 sanskrit_D=round(ds, 1), sanskrit_sd=round(st.stdev(xsk), 1), sanskrit_above=sum(x > 0 for x in xsk))
def summ(ds_):
    ds_ = sorted(ds_); n = len(ds_)
    return dict(n=n, mean=round(st.mean(ds_), 1), median=round(st.median(ds_), 1), p95=round(ds_[int(0.95 * n) - 1] if n >= 20 else ds_[-1], 1),
                max=round(ds_[-1], 1), min=round(ds_[0], 1), n_above_0=sum(x > 0 for x in ds_),
                n_ge_obs=sum(x >= dt for x in ds_), p=round((1 + sum(x >= dt for x in ds_)) / (n + 1), 4),
                share_of_obs_above_median=round((dt - st.median(ds_)) / dt, 3))
res['T1_picture_permutation'] = summ([D(d)[0] for d in sorted(glob.glob(f'{O}/T1/perm*'))])
res['T1_reads'] = round(st.mean(J(f)['read'] for f in glob.glob(f'{O}/T1/perm*/tamil_real_*.json')), 1)
for k in ('order', 'iid'):
    res[f'T2_{k}'] = summ([D(d)[0] for d in sorted(glob.glob(f'{O}/T2_{k}/fake*'))])
    res[f'T2_{k}_reads'] = round(st.mean(J(f)['read'] for f in glob.glob(f'{O}/T2_{k}/fake*/tamil_real_*.json')), 1)
res['T0_reads_tamil'] = round(st.mean(J(f'{O}/T0/tamil_real_{s}.json')['read'] for s in range(10)), 1)
json.dump(res, open(f'{O}/stage1_summary.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
